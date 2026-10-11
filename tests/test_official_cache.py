"""TDD spec for the local official-dictionary cache (bring your own).

Run: python3 -m unittest discover -s tests

No copyrighted data here: FAKE_DICT is a small invented dictionary written in
the ASD-STE100 pdftotext -layout column format, only to exercise the parser.
"""
import json
import os
import sys
import tempfile
import unittest

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))

import ste_lint      # noqa: E402
import ste_import    # noqa: E402


def rules(result):
    return [v["rule"] for v in result["violations"]]


def details(result, rule):
    return [v["detail"] for v in result["violations"] if v["rule"] == rule]


# Invented entries, real layout: "WORD (pos)" = approved, "word (pos)" = not.
FAKE_DICT = """\
 Non-STE                                       STE
 ABOUT (prep)          Concerned with               FOR DATA ABOUT THE
 START (v),            To begin                     START THE PUMP
 SUFFICIENT (adj)      Not less than                THE FORCE IS SUFFICIENT
 zorp (v)              START (v)                    ZORP THE PUMP        Start the pump
 acceptable (adj)      PERMITTED (adj)              A VALUE IS ACCEPTABLE
 enough (adj)          SUFFICIENT (adj)             ENOUGH FORCE         Sufficient force
 guarantee (v)         MAKE SURE (v)                GUARANTEE THE FIT    Make sure of the fit
 achieve (v)           DO (v)                       ACHIEVE THE RESULT   Do the result
 quux (n)              Removed from the word list.
 TEST (n)              A procedure to find        DO A TEST OF THE PUMP
 test (v)              TEST (n)                   TEST THE PUMP        Do a test of the pump
"""


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.parsed = ste_import.parse_official(FAKE_DICT)

    def test_returns_expected_keys(self):
        self.assertIn("approved", self.parsed)
        self.assertIn("word_substitutions", self.parsed)

    def test_uppercase_headwords_are_approved(self):
        approved = set(self.parsed["approved"])
        self.assertIn("about", approved)
        self.assertIn("start", approved)
        self.assertIn("sufficient", approved)

    def test_lowercase_headwords_are_not_approved(self):
        approved = set(self.parsed["approved"])
        self.assertNotIn("zorp", approved)
        self.assertNotIn("acceptable", approved)

    def test_cache_is_version_2(self):
        self.assertEqual(self.parsed["version"], 2)

    def test_approved_words_keep_their_part_of_speech(self):
        approved = self.parsed["approved"]
        self.assertEqual(approved["about"], ["prep"])
        self.assertEqual(approved["start"], ["v"])
        self.assertEqual(approved["test"], ["n"])

    def test_substitution_keys_keep_their_part_of_speech(self):
        subs = self.parsed["word_substitutions"]
        self.assertEqual(subs.get("zorp (v)"), "start")
        self.assertEqual(subs.get("acceptable (adj)"), "permitted")
        self.assertEqual(subs.get("enough (adj)"), "sufficient")
        self.assertEqual(subs.get("test (v)"), "test")

    def test_no_substitution_when_no_alternative(self):
        # "quux" has no UPPERCASE alternative on its line.
        self.assertNotIn("quux (n)", self.parsed["word_substitutions"])

    def test_multiword_alternative_is_kept_whole(self):
        # "MAKE SURE" must not be truncated to "sure".
        self.assertEqual(self.parsed["word_substitutions"].get("guarantee (v)"),
                         "make sure")

    def test_two_letter_alternative_is_captured(self):
        # Short approved verbs like GO/DO must still be captured.
        self.assertEqual(self.parsed["word_substitutions"].get("achieve (v)"), "do")


class CacheRoundTripTests(unittest.TestCase):
    def test_write_and_load_cache(self):
        parsed = ste_import.parse_official(FAKE_DICT)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "official.json")
            ste_import.write_cache(path, parsed)
            loaded = ste_lint.load_cache(path)
            self.assertEqual(loaded["word_substitutions"]["zorp (v)"], "start")

    def test_imported_cache_checks_part_of_speech(self):
        parsed = ste_import.parse_official(FAKE_DICT)
        noun = ste_lint.lint("Do a test of the pump.", cache=parsed, custom={})
        verb = ste_lint.lint("Test the pump.", cache=parsed, custom={})
        self.assertNotIn("unapproved-word", rules(noun))
        self.assertIn("unapproved-word", rules(verb))

    def test_load_missing_cache_returns_none(self):
        self.assertIsNone(ste_lint.load_cache("/no/such/file.json"))


class LintWithCacheTests(unittest.TestCase):
    def test_cache_adds_new_substitution(self):
        cache = {"version": 2, "approved": {}, "word_substitutions": {"widget": "gadget"},
                 "phrase_substitutions": {}}
        r = ste_lint.lint("Install the widget.", cache=cache)
        self.assertIn("unapproved-word", rules(r))
        self.assertIn("use 'gadget' instead of 'widget'", details(r, "unapproved-word"))

    def test_cache_approved_suppresses_seed_false_positive(self):
        # "utilize" is in the seed. If the official cache marks it approved,
        # the linter must NOT flag it.
        cache = {"approved": ["utilize"], "word_substitutions": {},
                 "phrase_substitutions": {}}
        r = ste_lint.lint("We utilize the tool.", cache=cache)
        self.assertNotIn("use 'use' instead of 'utilize'",
                         details(r, "unapproved-word"))

    def test_cache_overrides_seed_replacement(self):
        cache = {"approved": [], "word_substitutions": {"utilize": "apply"},
                 "phrase_substitutions": {}}
        r = ste_lint.lint("We utilize the tool.", cache=cache)
        self.assertIn("use 'apply' instead of 'utilize'",
                      details(r, "unapproved-word"))

    def test_no_cache_behaves_as_seed(self):
        r = ste_lint.lint("We utilize the tool.", cache={}, custom={})
        self.assertIn("use 'use' instead of 'utilize'",
                      details(r, "unapproved-word"))


class ImporterCliTests(unittest.TestCase):
    def test_main_writes_json_cache_from_text(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "dict.txt")
            out = os.path.join(d, "official.json")
            with open(src, "w") as f:
                f.write(FAKE_DICT)
            rc = ste_import.main([src, "--out", out])
            self.assertEqual(rc, 0)
            with open(out) as f:
                data = json.load(f)
            self.assertEqual(data["word_substitutions"]["acceptable (adj)"], "permitted")


# Invented words in the real layouts of three parts of the PDF: the change log
# (before the dictionary), a summary table, and dictionary entries with
# several approved alternatives on continuation lines.
LAYOUT_DICT = """\
blorp (adj)         GLIMMER (v) removed from the approved alternatives.
quib (adj)          STE and non-STE examples revised.
 frab (v)                          SNAP (v), HOLD (v)
blorp (adj)         ONE (TN) MORE             INSTALL ONE MORE      Install a blorp washer
quib (adj)          AGREE (v)                 MAKE SURE THAT THE    Make sure that the
                                              VALUES AGREE.         values are quib.
frab (v)            ATTACH (v)                ATTACH THE PANEL      Frab the panel
glarb (adj)         ONE (TN) OF THE TWO IF THERE IS WATER      If there is water
zorg (adv)          ROUGHLY (adv) PUT A BOX
                                  UNDER THE TANK.
 plonk (v)                                     PLONK (n)
glub (adj)          TWO (TN) … NOT            THE TWO UNITS MUST    Glub unit must
plonk (v)           MAKE SURE (v)             MAKE SURE THAT IT     Plonk that it is safe
                    EXAMINE (v)               EXAMINE THE PART      Plonk the part
zink (n)            DIFFERENT (adj)           IF THE TWO            If there is a zink
                                              VALUES ARE            between the two
                                              DIFFERENT, STOP.      values, stop.
                    AGREE (v)                 IF THE TWO            If there is a zink
                                              VALUES DO NOT         between the two
                                              AGREE, STOP.          values, stop.
"""


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.subs = ste_import.parse_official(LAYOUT_DICT)["word_substitutions"]

    def test_change_log_line_is_not_an_entry(self):
        self.assertNotEqual(self.subs.get("blorp (adj)"), "glimmer")

    def test_summary_table_line_is_not_an_entry(self):
        self.assertEqual(self.subs.get("frab (v)"), "attach")

    def test_dictionary_entry_wins(self):
        self.assertEqual(self.subs.get("quib (adj)"), "agree")

    def test_entry_with_example_beats_table_line(self):
        self.assertEqual(self.subs.get("plonk (v)"), "make sure|examine")

    def test_ellipsis_alternative_is_an_entry(self):
        self.assertEqual(self.subs.get("glub (adj)"), "two … not")

    def test_continuation_is_at_most_three_words(self):
        # pdftotext can join the alternative and the example with one space.
        self.assertEqual(self.subs.get("glarb (adj)"), "one of the two")

    def test_alternative_stops_at_the_example_column(self):
        # The next line shows where the example column starts.
        self.assertEqual(self.subs.get("zorg (adv)"), "roughly")

    def test_alternative_continues_after_its_tag(self):
        self.assertEqual(self.subs.get("blorp (adj)"), "one more")

    def test_all_alternatives_are_kept(self):
        self.assertEqual(self.subs.get("zink (n)"), "different|agree")

    def test_linter_names_every_alternative(self):
        cache = {"version": 2, "approved": {}, "word_substitutions": self.subs,
                 "phrase_substitutions": {}}
        r = ste_lint.lint("Find the zink.", cache=cache, custom={})
        self.assertIn("'zink' as a noun: use 'different' or 'agree'", details(r, "unapproved-word"))


if __name__ == "__main__":
    unittest.main()
