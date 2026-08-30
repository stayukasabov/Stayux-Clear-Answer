"""TDD spec for the STE linter (stdlib unittest, no external deps).

Run: python3 -m unittest discover -s tests
"""
import json
import os
import subprocess
import sys
import unittest

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))

import ste_lint  # noqa: E402


def rules(result):
    return [v["rule"] for v in result["violations"]]


def errors(result):
    return [v["rule"] for v in result["violations"] if v["severity"] == "error"]


class ContractTests(unittest.TestCase):
    def test_result_shape(self):
        r = ste_lint.lint("Open the valve.")
        self.assertIn("passed", r)
        self.assertIn("profile", r)
        self.assertIn("violations", r)
        self.assertIsInstance(r["violations"], list)

    def test_clean_text_passes(self):
        r = ste_lint.lint("Open the valve. Close the door.")
        self.assertTrue(r["passed"])
        self.assertEqual(r["violations"], [])

    def test_passed_is_false_only_on_errors(self):
        # a warning-only text still passes
        r = ste_lint.lint("The bolt was removed by the technician.")
        self.assertIn("passive-voice", rules(r))
        self.assertTrue(r["passed"])  # passive is a warning, not an error


class SentenceLengthTests(unittest.TestCase):
    def test_chat_allows_25_words(self):
        s = " ".join(["word"] * 25) + "."
        r = ste_lint.lint(s, profile="chat")
        self.assertNotIn("sentence-length", rules(r))

    def test_chat_flags_26_words(self):
        s = " ".join(["word"] * 26) + "."
        r = ste_lint.lint(s, profile="chat")
        self.assertIn("sentence-length", errors(r))

    def test_full_profile_is_stricter(self):
        s = " ".join(["word"] * 22) + "."
        self.assertNotIn("sentence-length", rules(ste_lint.lint(s, profile="chat")))
        self.assertIn("sentence-length", errors(ste_lint.lint(s, profile="full")))


class ParagraphLengthTests(unittest.TestCase):
    def test_six_sentences_ok(self):
        r = ste_lint.lint(" ".join(["Do it."] * 6))
        self.assertNotIn("paragraph-length", rules(r))

    def test_seven_sentences_flagged(self):
        r = ste_lint.lint(" ".join(["Do it."] * 7))
        self.assertIn("paragraph-length", errors(r))

    def test_blank_line_splits_paragraphs(self):
        block = " ".join(["Do it."] * 5)
        r = ste_lint.lint(block + "\n\n" + block)
        self.assertNotIn("paragraph-length", rules(r))


class SemicolonTests(unittest.TestCase):
    def test_semicolon_flagged(self):
        r = ste_lint.lint("Do this; do that.")
        self.assertIn("semicolon", errors(r))


class VerbFormTests(unittest.TestCase):
    def test_progressive_flagged(self):
        r = ste_lint.lint("The pump is running.")
        self.assertIn("progressive-tense", errors(r))

    def test_perfect_flagged(self):
        r = ste_lint.lint("You have removed the bolt.")
        self.assertIn("perfect-tense", errors(r))

    def test_simple_present_ok(self):
        r = ste_lint.lint("The pump runs.")
        self.assertFalse(
            {"progressive-tense", "perfect-tense", "passive-voice"} & set(rules(r))
        )


class PassiveVoiceTests(unittest.TestCase):
    def test_passive_flagged(self):
        r = ste_lint.lint("The valve was closed by the operator.")
        self.assertIn("passive-voice", rules(r))

    def test_active_not_flagged(self):
        r = ste_lint.lint("The operator closed the valve.")
        self.assertNotIn("passive-voice", rules(r))


class PhrasalVerbTests(unittest.TestCase):
    def test_phrasal_verb_flagged(self):
        r = ste_lint.lint("Turn off the switch.")
        self.assertIn("phrasal-verb", rules(r))


class ListHandlingTests(unittest.TestCase):
    def test_bullet_list_not_paragraph_length(self):
        text = "\n".join(f"- item number {i}." for i in range(8))
        self.assertNotIn("paragraph-length", rules(ste_lint.lint(text)))

    def test_numbered_list_not_paragraph_length(self):
        text = "\n".join(f"{i}. item number {i}." for i in range(1, 9))
        self.assertNotIn("paragraph-length", rules(ste_lint.lint(text)))

    def test_heading_plus_list_ok(self):
        text = "Data for it:\n" + "\n".join(f"- point {i}." for i in range(7))
        self.assertNotIn("paragraph-length", rules(ste_lint.lint(text)))

    def test_prose_paragraph_still_flagged(self):
        r = ste_lint.lint(" ".join(["Do it."] * 7))
        self.assertIn("paragraph-length", errors(r))

    def test_long_list_item_still_flagged(self):
        r = ste_lint.lint("- " + " ".join(["word"] * 26) + ".")
        self.assertIn("sentence-length", errors(r))


class NounClusterTests(unittest.TestCase):
    # Correct noun-cluster detection needs POS tagging (noun vs verb/adjective).
    # It is deferred to v2 with the dictionary. v1 must NOT emit it, since the
    # content-word heuristic produced false positives on normal prose.
    def test_noun_cluster_deferred_normal_prose(self):
        r = ste_lint.lint("Digital design roles grow fast this year.")
        self.assertNotIn("noun-cluster", rules(r))

    def test_noun_cluster_deferred_real_cluster(self):
        r = ste_lint.lint("Replace the main landing gear door actuator.")
        self.assertNotIn("noun-cluster", rules(r))


class DictionaryTests(unittest.TestCase):
    def _detail(self, result, rule):
        return next(v["detail"] for v in result["violations"] if v["rule"] == rule)

    def test_unapproved_single_word_flagged(self):
        r = ste_lint.lint("Commence the test.")
        self.assertIn("unapproved-word", rules(r))
        self.assertIn("start", self._detail(r, "unapproved-word"))

    def test_approved_word_not_flagged(self):
        r = ste_lint.lint("Start the test.")
        self.assertNotIn("unapproved-word", rules(r))

    def test_unapproved_phrase_flagged(self):
        r = ste_lint.lint("Push the button in order to start.")
        self.assertIn("unapproved-word", rules(r))
        self.assertIn("to", self._detail(r, "unapproved-word"))

    def test_unapproved_is_warning_not_error(self):
        r = ste_lint.lint("Commence the test.")
        self.assertTrue(r["passed"])  # word choice is advisory, not a gate error

    def test_issue9_swap_main_to_primary(self):
        r = ste_lint.lint("Open the main valve.")
        self.assertIn("unapproved-word", rules(r))
        self.assertIn("primary", self._detail(r, "unapproved-word"))

    def test_issue9_subsequently_is_approved(self):
        r = ste_lint.lint("Subsequently, close the valve.")
        self.assertNotIn("unapproved-word", rules(r))


class RemovedTermTests(unittest.TestCase):
    def _details(self, result):
        return [v["detail"] for v in result["violations"] if v["rule"] == "removed-word"]

    def test_removed_single_word_flagged(self):
        r = ste_lint.lint("Increase the brightness.")
        self.assertIn("removed-word", rules(r))
        self.assertTrue(any("brightness" in d for d in self._details(r)))

    def test_removed_phrase_flagged(self):
        r = ste_lint.lint("Wait at least two hours.")
        self.assertIn("removed-word", rules(r))

    def test_removed_term_is_warning_not_error(self):
        r = ste_lint.lint("Increase the brightness.")
        self.assertNotIn("removed-word", errors(r))
        self.assertTrue(r["passed"])


class ContractionTests(unittest.TestCase):
    def _detail(self, result, rule):
        return next(v["detail"] for v in result["violations"] if v["rule"] == rule)

    def test_contraction_flagged_as_error(self):
        r = ste_lint.lint("Don't open the valve.")
        self.assertIn("contraction", errors(r))
        self.assertFalse(r["passed"])

    def test_contraction_suggests_expansion(self):
        r = ste_lint.lint("Don't open the valve.")
        self.assertIn("do not", self._detail(r, "contraction"))

    def test_curly_apostrophe_contraction_flagged(self):
        r = ste_lint.lint("Don’t open the valve.")
        self.assertIn("contraction", rules(r))

    def test_possessive_not_flagged_as_contraction(self):
        r = ste_lint.lint("Set the valve's cover.")
        self.assertNotIn("contraction", rules(r))


class OneInstructionTests(unittest.TestCase):
    def test_and_joined_imperatives_flagged(self):
        r = ste_lint.lint("Open the valve and close the door.")
        self.assertIn("one-instruction", rules(r))

    def test_then_joined_imperatives_flagged(self):
        r = ste_lint.lint("Open the valve then close it.")
        self.assertIn("one-instruction", rules(r))

    def test_and_between_nouns_not_flagged(self):
        r = ste_lint.lint("Remove the valve and the pump.")
        self.assertNotIn("one-instruction", rules(r))

    def test_non_imperative_and_not_flagged(self):
        r = ste_lint.lint("The valve and the pump are clean.")
        self.assertNotIn("one-instruction", rules(r))

    def test_one_instruction_is_warning(self):
        r = ste_lint.lint("Open the valve and close the door.")
        self.assertNotIn("one-instruction", errors(r))


class WordinessTests(unittest.TestCase):
    def _detail(self, result, rule):
        return next(v["detail"] for v in result["violations"] if v["rule"] == rule)

    def test_filler_phrase_flagged(self):
        r = ste_lint.lint("It is important to note that the valve is open.")
        self.assertIn("wordiness", rules(r))

    def test_wordiness_is_warning_not_error(self):
        r = ste_lint.lint("It is important to note that the valve is open.")
        self.assertNotIn("wordiness", errors(r))
        self.assertTrue(r["passed"])

    def test_wordiness_detail_names_the_phrase(self):
        r = ste_lint.lint("It is important to note that the valve is open.")
        self.assertIn("it is important to note that", self._detail(r, "wordiness").lower())

    def test_the_fact_that_flagged(self):
        r = ste_lint.lint("The fact that it failed is clear.")
        self.assertIn("wordiness", rules(r))

    def test_clean_sentence_has_no_wordiness(self):
        r = ste_lint.lint("Open the valve.")
        self.assertNotIn("wordiness", rules(r))


class CliTests(unittest.TestCase):
    def _run(self, text, *args):
        return subprocess.run(
            [sys.executable, os.path.join(SKILL_ROOT, "scripts", "ste_lint.py"), *args],
            input=text, capture_output=True, text=True,
        )

    def test_cli_clean_exit_zero(self):
        p = self._run("Open the valve.")
        self.assertEqual(p.returncode, 0)
        self.assertTrue(json.loads(p.stdout)["passed"])

    def test_cli_violation_exit_one(self):
        p = self._run("Do this; do that.")
        self.assertEqual(p.returncode, 1)
        self.assertFalse(json.loads(p.stdout)["passed"])


class LineNumberTests(unittest.TestCase):
    def _line(self, result, rule):
        return next(v["line"] for v in result["violations"] if v["rule"] == rule)

    def test_violation_reports_line(self):
        r = ste_lint.lint("Open the valve.\n\nThe pump is running.")
        self.assertEqual(self._line(r, "progressive-tense"), 3)

    def test_semicolon_reports_line(self):
        r = ste_lint.lint("Open it.\n\nDo this; do that.")
        self.assertEqual(self._line(r, "semicolon"), 3)


if __name__ == "__main__":
    unittest.main()
