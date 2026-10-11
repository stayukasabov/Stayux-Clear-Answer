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


def mermaid(body):
    return "Open the valve.\n\n```mermaid\n" + body + "\n```\n"


class MermaidLabelTests(unittest.TestCase):
    def labels(self, body):
        return [l for l, _ in ste_lint.mermaid_labels(body.split("\n"), 1)]

    def test_flowchart_node_labels(self):
        self.assertEqual(self.labels("graph TD\nA[Open the valve] --> B{Is the pressure high?}"),
                         ["Open the valve", "Is the pressure high?"])

    def test_node_shapes_and_quotes(self):
        body = 'flowchart LR\nA(Start) --> B(("Stop the pump")) --> C[[Check the seal]] --> D[(Store)]'
        self.assertEqual(self.labels(body), ["Start", "Stop the pump", "Check the seal", "Store"])

    def test_edge_labels(self):
        body = "graph TD\nA -->|yes| B\nA -- no --> C"
        self.assertEqual(sorted(self.labels(body)), ["no", "yes"])

    def test_br_tag_becomes_space(self):
        self.assertEqual(self.labels("graph TD\nA[Open<br>the valve]"), ["Open the valve"])

    def test_sequence_messages(self):
        body = "sequenceDiagram\nAlice->>Bob: Send the token\nNote over Bob: Check the token"
        self.assertEqual(self.labels(body), ["Send the token", "Check the token"])

    def test_unknown_diagram_type_has_no_labels(self):
        self.assertEqual(self.labels('pie\n"Dogs" : 10'), [])

    def test_label_line_numbers(self):
        found = ste_lint.mermaid_labels(["graph TD", "A[Open the valve]", "B[Close it]"], 10)
        self.assertEqual(found, [("Open the valve", 11), ("Close it", 12)])


class MermaidLintTests(unittest.TestCase):
    def test_eight_word_label_passes(self):
        r = ste_lint.lint(mermaid("graph TD\nA[one two three four five six seven eight]"))
        self.assertNotIn("label-length", rules(r))

    def test_nine_word_label_fails(self):
        r = ste_lint.lint(mermaid("graph TD\nA[one two three four five six seven eight nine]"))
        self.assertIn("label-length", errors(r))

    def test_label_word_rules_apply(self):
        r = ste_lint.lint(mermaid("graph TD\nA[The pump is running] --> B[Don't stop]"))
        self.assertIn("progressive-tense", errors(r))
        self.assertIn("contraction", errors(r))

    def test_label_violation_line(self):
        r = ste_lint.lint(mermaid("graph TD\nA[Open it]\nB[The pump is running]"))
        line = next(v["line"] for v in r["violations"] if v["rule"] == "progressive-tense")
        self.assertEqual(line, 6)

    def test_mermaid_semicolons_pass(self):
        r = ste_lint.lint(mermaid("graph TD;\nA[Open the valve] --> B[Close the door];"))
        self.assertTrue(r["passed"])

    def test_other_code_fences_still_skipped(self):
        r = ste_lint.lint("Open the valve.\n\n```python\nx = 'is running'\n```\n")
        self.assertNotIn("progressive-tense", rules(r))


def page(body, head=""):
    return f"<!doctype html>\n<html>\n<head>{head}</head>\n<body>\n{body}\n</body>\n</html>"


class HtmlTextTests(unittest.TestCase):
    def lint(self, html):
        return ste_lint.lint(html, fmt="html")

    def test_clean_page_passes(self):
        r = self.lint(page("<h1>Valves</h1>\n<p>Open the valve. Close the door.</p>"))
        self.assertTrue(r["passed"])
        self.assertEqual(r["violations"], [])

    def test_visible_text_is_checked(self):
        r = self.lint(page("<p>The pump is running.</p>"))
        self.assertIn("progressive-tense", errors(r))

    def test_hidden_elements_are_skipped(self):
        html = page("<script>var a = 'is running'; b();</script>\n"
                    "<style>p { color: red; }</style>\n"
                    "<pre>x = 1; y = 2</pre><p>Use <code>a; b</code> now.</p>",
                    head="<title>The pump is running</title>")
        r = self.lint(html)
        self.assertTrue(r["passed"], r["violations"])

    def test_paragraphs_are_separate(self):
        six = " ".join(["Open the valve."] * 6)
        r = self.lint(page(f"<p>{six}</p>\n<p>{six}</p>"))
        self.assertNotIn("paragraph-length", rules(r))

    def test_long_paragraph_flagged(self):
        seven = " ".join(["Open the valve."] * 7)
        r = self.lint(page(f"<p>{seven}</p>"))
        self.assertIn("paragraph-length", errors(r))

    def test_list_items_are_not_a_paragraph(self):
        items = "".join("<li>Open the valve.</li>" for _ in range(8))
        r = self.lint(page(f"<ul>{items}</ul>"))
        self.assertNotIn("paragraph-length", rules(r))

    def test_table_cells_are_separate(self):
        rows = "".join("<tr><td>Valve</td><td>Open</td><td>Pump</td></tr>" for _ in range(10))
        r = self.lint(page(f"<table>{rows}</table>"))
        self.assertNotIn("sentence-length", rules(r))

    def test_inline_tags_keep_the_sentence(self):
        r = self.lint(page("<p>The pump <b>is</b> <em>running</em>.</p>"))
        self.assertIn("progressive-tense", errors(r))

    def test_line_number_is_the_source_line(self):
        r = self.lint(page("<p>Open the valve.</p>\n<p>The pump is running.</p>"))
        line = next(v["line"] for v in r["violations"] if v["rule"] == "progressive-tense")
        self.assertEqual(line, 6)

    def test_chat_format_rules_off_for_html(self):
        r = self.lint(page("<h1>Steps</h1>\n<p>Great question! Open the valve.</p>"))
        self.assertNotIn("header-in-short-reply", rules(r))
        self.assertNotIn("filler-opener", rules(r))

    def test_svg_text_is_a_label(self):
        svg = "<svg><text>one two three four five six seven eight nine</text></svg>"
        r = self.lint(page(svg))
        self.assertIn("label-length", errors(r))

    def test_svg_short_label_passes(self):
        r = self.lint(page("<svg><text>Open <tspan>the valve</tspan></text></svg>"))
        self.assertTrue(r["passed"], r["violations"])


class ExternalRequestTests(unittest.TestCase):
    def lint(self, html):
        return ste_lint.lint(html, fmt="html")

    def test_external_script_flagged(self):
        r = self.lint(page("<p>Open it.</p>", head='<script src="https://cdn.example.com/a.js"></script>'))
        self.assertIn("external-request", errors(r))

    def test_external_stylesheet_flagged(self):
        r = self.lint(page("<p>Open it.</p>", head='<link rel="stylesheet" href="//fonts.example.com/a.css">'))
        self.assertIn("external-request", errors(r))

    def test_external_image_flagged(self):
        r = self.lint(page('<p>Open it.</p><img src="http://example.com/a.png" alt="">'))
        self.assertIn("external-request", errors(r))

    def test_css_import_flagged(self):
        r = self.lint(page("<p>Open it.</p>", head="<style>@import url('https://x.example.com/a.css');</style>"))
        self.assertIn("external-request", errors(r))

    def test_link_to_another_page_is_fine(self):
        r = self.lint(page('<p>Open <a href="https://example.com">the guide</a>.</p>'))
        self.assertNotIn("external-request", rules(r))

    def test_data_uri_is_fine(self):
        r = self.lint(page('<p>Open it.</p><img src="data:image/png;base64,AAAA" alt="">'))
        self.assertNotIn("external-request", rules(r))

    def test_markdown_has_no_external_request_rule(self):
        r = ste_lint.lint('Open <img src="https://x.example.com/a.png">.')
        self.assertNotIn("external-request", rules(r))


class HtmlCliTests(unittest.TestCase):
    def test_cli_format_html(self):
        p = subprocess.run(
            [sys.executable, os.path.join(SKILL_ROOT, "scripts", "ste_lint.py"), "--format", "html"],
            input=page("<p>The pump is running.</p>"), capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        self.assertIn("progressive-tense", p.stdout)


class ExplainPageFixtureTests(unittest.TestCase):
    # The page format that /clear-answer:explain --format html asks for.
    def test_sample_page_passes(self):
        with open(os.path.join(SKILL_ROOT, "tests", "fixtures", "explain-page.html")) as f:
            r = ste_lint.lint(f.read(), fmt="html")
        self.assertTrue(r["passed"], [v for v in r["violations"] if v["severity"] == "error"])
        self.assertNotIn("external-request", rules(r))


if __name__ == "__main__":
    unittest.main()
