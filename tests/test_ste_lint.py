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
        r = ste_lint.lint("Push the button in the event that it stops.")
        self.assertIn("unapproved-word", rules(r))
        self.assertIn("if", self._detail(r, "unapproved-word"))

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


class CodeExemptionTests(unittest.TestCase):
    def test_semicolon_in_backtick_fence_passes(self):
        r = ste_lint.lint("Open the valve.\n\n```\nx = 1; y = 2\n```\n")
        self.assertNotIn("semicolon", rules(r))
        self.assertTrue(r["passed"])

    def test_semicolon_in_tilde_fence_passes(self):
        r = ste_lint.lint("Open the valve.\n\n~~~python\nx = 1; y = 2\n~~~\n")
        self.assertNotIn("semicolon", rules(r))

    def test_semicolon_in_inline_code_passes(self):
        r = ste_lint.lint("Type `a; b` in the box.")
        self.assertNotIn("semicolon", rules(r))

    def test_semicolon_after_fence_keeps_line_number(self):
        r = ste_lint.lint("Open the valve.\n\n```\nx = 1\ny = 2\n```\n\nDo this; do that.")
        semis = [v for v in r["violations"] if v["rule"] == "semicolon"]
        self.assertEqual(len(semis), 1)
        self.assertEqual(semis[0]["line"], 8)

    def test_unapproved_word_in_fence_not_flagged(self):
        r = ste_lint.lint("Open the valve.\n\n```\nverify the build\n```\n")
        self.assertNotIn("unapproved-word", rules(r))

    def test_unapproved_word_in_inline_code_not_flagged(self):
        r = ste_lint.lint("Type `make verify` now.")
        self.assertNotIn("unapproved-word", rules(r))


class TableTests(unittest.TestCase):
    TABLE = "| Name | Value |\n|---|:---:|\n| Valve | Open |\n| Pump | Off |"

    def test_short_cells_pass(self):
        rows = "\n".join("| Valve | Open | Pump |" for _ in range(10))
        r = ste_lint.lint("| Name | Value | Part |\n|---|---|---|\n" + rows)
        self.assertNotIn("sentence-length", rules(r))
        self.assertNotIn("paragraph-length", rules(r))

    def test_long_cell_flagged(self):
        cell = " ".join(["word"] * 26)
        r = ste_lint.lint("| Name | Note |\n|---|---|\n| Valve | " + cell + " |", profile="chat")
        self.assertIn("sentence-length", errors(r))

    def test_separator_row_not_flagged(self):
        r = ste_lint.lint("|---|:---:|---:|")
        self.assertEqual(r["violations"], [])

    def test_table_not_counted_in_paragraph_above(self):
        prose = " ".join(["Open the valve."] * 6)
        rows = "\n".join("| Close the door. | Stop the pump. |" for _ in range(2))
        r = ste_lint.lint(prose + "\n" + rows)
        self.assertNotIn("paragraph-length", rules(r))

    def test_cell_violation_reports_row_line(self):
        r = ste_lint.lint(self.TABLE + "\n| Pump | is running |")
        line = next(v["line"] for v in r["violations"] if v["rule"] == "progressive-tense")
        self.assertEqual(line, 5)


class FormatRuleTests(unittest.TestCase):
    SHORT = "Open the valve. Close the door."
    LONG = " ".join(["Open the valve."] * 55)  # 165 words

    def test_two_bold_spans_pass(self):
        r = ste_lint.lint("Open the **valve** and the **door**.")
        self.assertNotIn("bold-overuse", rules(r))

    def test_three_bold_spans_flagged(self):
        r = ste_lint.lint("Open the **valve**, the **door**, and the **lid**.")
        self.assertIn("bold-overuse", rules(r))

    def test_header_in_short_reply_flagged(self):
        r = ste_lint.lint("## Steps\n\n" + self.SHORT)
        self.assertIn("header-in-short-reply", rules(r))

    def test_header_in_long_reply_passes(self):
        r = ste_lint.lint("## Steps\n\n" + self.LONG)
        self.assertNotIn("header-in-short-reply", rules(r))

    def test_one_bullet_flagged(self):
        r = ste_lint.lint(self.SHORT + "\n\n- Open the valve.")
        self.assertIn("bullet-overuse", rules(r))

    def test_three_bullets_pass(self):
        r = ste_lint.lint("- Open the valve.\n- Close the door.\n- Stop the pump.")
        self.assertNotIn("bullet-overuse", rules(r))

    def test_eight_bullets_flagged(self):
        r = ste_lint.lint("\n".join("- Open the valve." for _ in range(8)))
        self.assertIn("bullet-overuse", rules(r))

    def test_eight_numbered_items_pass(self):
        r = ste_lint.lint("\n".join(f"{i}. Open the valve." for i in range(1, 9)))
        self.assertNotIn("bullet-overuse", rules(r))

    def test_two_lists_of_four_pass(self):
        four = "\n".join("- Open the valve." for _ in range(4))
        r = ste_lint.lint(four + "\n\nClose the door.\n\n" + four)
        self.assertNotIn("bullet-overuse", rules(r))

    def test_filler_opener_flagged(self):
        r = ste_lint.lint("Great question! Open the valve.")
        self.assertIn("filler-opener", rules(r))

    def test_restating_opener_flagged(self):
        r = ste_lint.lint("To answer your question, open the valve.")
        self.assertIn("filler-opener", rules(r))

    def test_sure_inside_sentence_not_opener(self):
        r = ste_lint.lint("Make sure that the valve is open.")
        self.assertNotIn("filler-opener", rules(r))

    def test_direct_opener_passes(self):
        r = ste_lint.lint("Open the valve.")
        self.assertNotIn("filler-opener", rules(r))

    def test_filler_closer_flagged(self):
        r = ste_lint.lint("Open the valve. I hope this helps.")
        self.assertIn("filler-closer", rules(r))

    def test_closer_phrase_not_in_last_sentence_passes(self):
        r = ste_lint.lint("Let me know if the valve leaks. Close the door.")
        self.assertNotIn("filler-closer", rules(r))

    def test_format_rules_off_in_full(self):
        text = "Great question! **A** **B** **C**.\n\n## Note\n\n- One item.\n\nI hope this helps."
        r = ste_lint.lint(text, profile="full")
        for rule in ("bold-overuse", "header-in-short-reply", "bullet-overuse",
                     "filler-opener", "filler-closer"):
            self.assertNotIn(rule, rules(r))

    def test_format_rules_are_warnings(self):
        text = "Great question! **A** **B** **C**.\n\n## Note\n\n- One item.\n\nI hope this helps."
        r = ste_lint.lint(text, profile="chat")
        self.assertIn("filler-opener", rules(r))
        self.assertTrue(r["passed"])

    def test_bold_in_code_not_counted(self):
        r = ste_lint.lint("Open the valve.\n\n```\n**a** **b** **c**\n```\n")
        self.assertNotIn("bold-overuse", rules(r))


class LongFenceTests(unittest.TestCase):
    QUOTED = ("Open the valve.\n\n````markdown\nA reply.\n\n```mermaid\ngraph TD\n"
              "A[The pump is running]\n```\n\nThe pump is running; it is hot.\n````\n")

    def test_four_backtick_fence_hides_inner_fences(self):
        r = ste_lint.lint(self.QUOTED)
        self.assertTrue(r["passed"], r["violations"])

    def test_text_after_long_fence_is_checked(self):
        r = ste_lint.lint(self.QUOTED + "\nThe pump is running.\n")
        self.assertIn("progressive-tense", errors(r))

    def test_shorter_fence_does_not_close_longer_one(self):
        r = ste_lint.lint("Open it.\n\n````\n```\nx; y\n````\n")
        self.assertNotIn("semicolon", rules(r))


class PartOfSpeechTests(unittest.TestCase):
    CACHE = {"version": 2,
             "approved": {"test": ["n"]},
             "word_substitutions": {"file (v)": "remove", "branch (v)": "divide",
                                    "request (v)": "tell", "main (adj)": "primary"},
             "phrase_substitutions": {}}

    def lint(self, text, cache=None, custom=None):
        return ste_lint.lint(text, cache=self.CACHE if cache is None else cache,
                             custom=custom or {})

    def unapproved(self, r):
        return [v["detail"] for v in r["violations"] if v["rule"] == "unapproved-word"]

    def test_noun_use_is_not_flagged(self):
        self.assertEqual(self.unapproved(self.lint("Open the file. Merge the branch.")), [])

    def test_verb_use_is_flagged_with_pos(self):
        details = self.unapproved(self.lint("Use a tool to file the edge."))
        self.assertEqual(details, ["'file' as a verb: use 'remove'"])

    def test_imperative_verb_is_flagged(self):
        self.assertTrue(self.unapproved(self.lint("Request the parts.")))

    def test_adjective_entry_flags_adjective_use(self):
        self.assertTrue(self.unapproved(self.lint("Open the main valve.")))

    def test_noun_modifier_without_adjective_entry_passes(self):
        self.assertEqual(self.unapproved(self.lint("Open the file menu.")), [])

    def test_unknown_tag_still_warns_and_names_the_pos(self):
        details = self.unapproved(self.lint("Files open slowly, file them."))
        self.assertIn("'file' as a verb: use 'remove'", details)

    def test_unknown_tag_with_approved_pos_is_silent(self):
        self.assertEqual(self.unapproved(self.lint("Test results show a leak.")), [])

    def test_seed_entries_without_pos_apply_to_all_uses(self):
        self.assertTrue(self.unapproved(self.lint("Utilize the tool.", cache={})))

    def test_version_1_cache_skips_noun_use(self):
        v1 = {"approved": [], "word_substitutions": {"file": "remove"}, "phrase_substitutions": {}}
        self.assertEqual(self.unapproved(self.lint("Open the file.", cache=v1)), [])
        self.assertTrue(self.unapproved(self.lint("Use a tool to file the edge.", cache=v1)))

    def test_custom_entry_with_pos(self):
        custom = ste_lint.parse_custom_dict("deploy (v) = install\n")
        self.assertTrue(self.unapproved(self.lint("You must deploy the app.", custom=custom)))
        self.assertEqual(self.unapproved(self.lint("Open the deploy log.", custom=custom)), [])

    def test_custom_approval_with_pos(self):
        custom = ste_lint.parse_custom_dict("file (v)\n")
        self.assertEqual(self.unapproved(self.lint("Use a tool to file the edge.", custom=custom)), [])

    def test_custom_approval_without_pos_approves_all(self):
        custom = ste_lint.parse_custom_dict("+file\n")
        self.assertEqual(self.unapproved(self.lint("Use a tool to file the edge.", custom=custom)), [])


class PartOfSpeechWordingTests(unittest.TestCase):
    def test_adjective_takes_an(self):
        r = ste_lint.lint("Open the main valve.", cache={}, custom={})
        details = [v["detail"] for v in r["violations"] if v["rule"] == "unapproved-word"]
        self.assertIn("'main' as an adjective: use 'primary'", details)


class SelfReplacementTests(unittest.TestCase):
    # The official entry "test (v)" points to "TEST (n)", so the cache maps the
    # word to itself. That is not useful advice.
    CACHE = {"version": 2, "approved": {"test": ["n"]},
             "word_substitutions": {"test (v)": "test", "zorp (v)": "zorp"},
             "phrase_substitutions": {}}

    def details(self, text):
        r = ste_lint.lint(text, cache=self.CACHE, custom={})
        return [v["detail"] for v in r["violations"] if v["rule"] == "unapproved-word"]

    def test_seed_advice_is_kept(self):
        self.assertEqual(self.details("Test the software."),
                         ["'test' as a verb: use 'do a test of'"])

    def test_self_replacement_without_seed_names_the_problem(self):
        self.assertEqual(self.details("Zorp the pump."),
                         ["'zorp' as a verb is not approved"])


class MarkdownHtmlTagTests(unittest.TestCase):
    FOOTER = ('<p align="center">Stayux Clear Answer<br>\n'
              '<a href="https://stayux.com" target="_blank" rel="noopener noreferrer">Stayux.com</a> | '
              '<a href="https://x.com/StayuKasabov" target="_blank" rel="noopener noreferrer">X.com</a></p>')

    def test_tag_attributes_are_not_words(self):
        r = ste_lint.lint("Open the valve.\n\n" + self.FOOTER, cache={}, custom={})
        self.assertEqual(r["violations"], [])

    def test_text_inside_tags_is_checked(self):
        r = ste_lint.lint('<p align="center">The pump is running.</p>', cache={}, custom={})
        self.assertIn("progressive-tense", errors(r))


class PosNameTests(unittest.TestCase):
    def test_preposition_is_named_in_full(self):
        cache = {"version": 2, "approved": {}, "word_substitutions": {"past (prep)": "after"},
                 "phrase_substitutions": {}}
        r = ste_lint.lint("Go past it.", cache=cache, custom={})
        details = [v["detail"] for v in r["violations"] if v["rule"] == "unapproved-word"]
        self.assertEqual(details, ["'past' as a preposition: use 'after'"])


class DocumentHeaderTests(unittest.TestCase):
    def test_document_with_title_may_have_headers(self):
        r = ste_lint.lint("# How a valve works\n\nOpen the valve.\n\n## The steps\n\n1. Open it.\n2. Close it.\n",
                          cache={}, custom={})
        self.assertNotIn("header-in-short-reply", rules(r))

    def test_short_reply_with_header_still_warns(self):
        r = ste_lint.lint("Open the valve.\n\n## Steps\n\nClose the door.", cache={}, custom={})
        self.assertIn("header-in-short-reply", rules(r))


class SentenceSplitTests(unittest.TestCase):
    def test_domain_does_not_end_a_sentence(self):
        self.assertEqual(ste_lint._split_sentences("Open example.com in the browser. Close it."),
                         ["Open example.com in the browser.", "Close it."])

    def test_leading_dot_word_does_not_end_a_sentence(self):
        self.assertEqual(len(ste_lint._split_sentences("The .com server points to the name server.")), 1)

    def test_numbers_with_dots(self):
        self.assertEqual(len(ste_lint._split_sentences("Use 1.1.1.1 or version 2.0 now.")), 1)

    def test_question_and_exclamation(self):
        self.assertEqual(len(ste_lint._split_sentences("Is it open? Close it! Then stop.")), 3)

    def test_no_final_punctuation(self):
        self.assertEqual(ste_lint._split_sentences("Open the valve"), ["Open the valve"])

    def test_paragraph_with_domains_is_not_too_long(self):
        text = ("You type a name that ends in .com. The root server points to the .com server. "
                "The .com server points to the name server. That name server gives the address.")
        self.assertNotIn("paragraph-length", rules(ste_lint.lint(text, cache={}, custom={})))


class UnclosedFenceTests(unittest.TestCase):
    def test_unclosed_fence_is_an_error(self):
        r = ste_lint.lint("Open the valve.\n\n```\nThe pump is running.\n", cache={}, custom={})
        self.assertIn("unclosed-code-fence", errors(r))
        line = next(v["line"] for v in r["violations"] if v["rule"] == "unclosed-code-fence")
        self.assertEqual(line, 3)

    def test_closed_fence_is_fine(self):
        r = ste_lint.lint("Open the valve.\n\n```\nx\n```\n", cache={}, custom={})
        self.assertNotIn("unclosed-code-fence", rules(r))

    def test_inline_triple_backticks_in_a_bullet(self):
        r = ste_lint.lint("- Write one\n  ```mermaid block. The pump is running.\n", cache={}, custom={})
        self.assertIn("unclosed-code-fence", errors(r))


class ClauseTaggingTests(unittest.TestCase):
    CACHE = {"version": 2, "approved": {}, "phrase_substitutions": {},
             "word_substitutions": {"zink (n)": "difference", "frob (v)": "examine"}}

    def details(self, text):
        r = ste_lint.lint(text, cache=self.CACHE, custom={})
        return [v["detail"] for v in r["violations"] if v["rule"] == "unapproved-word"]

    def test_comma_ends_the_noun_phrase(self):
        self.assertIn("'zink' as a noun: use 'difference'", self.details("If there is a zink, frob the value."))

    def test_clause_start_is_an_imperative(self):
        self.assertIn("'frob' as a verb: use 'examine'", self.details("If there is a zink, frob the value."))


class MermaidBlockTests(unittest.TestCase):
    def test_mermaid_block_is_skipped_like_code(self):
        r = ste_lint.lint("Open the valve.\n\n```mermaid\ngraph TD\nA[The pump is running]\n```\n",
                          cache={}, custom={})
        self.assertTrue(r["passed"], r["violations"])


class CommandGateTests(unittest.TestCase):
    # A command that says "lint" must contain the linter command itself.
    # Claude does not follow a pointer to another command file.
    def test_gated_commands_contain_the_linter_command(self):
        for name in ("on", "mode", "explain", "rewrite", "check"):
            with open(os.path.join(SKILL_ROOT, "commands", f"{name}.md")) as f:
                self.assertIn('${CLAUDE_PLUGIN_ROOT}/scripts/ste_lint.py', f.read(), name)


if __name__ == "__main__":
    unittest.main()
