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

    def test_substitution_uses_first_approved_alternative(self):
        subs = self.parsed["word_substitutions"]
        self.assertEqual(subs.get("zorp"), "start")
        self.assertEqual(subs.get("acceptable"), "permitted")
        self.assertEqual(subs.get("enough"), "sufficient")

    def test_no_substitution_when_no_alternative(self):
        # "quux" has no UPPERCASE alternative on its line.
        self.assertNotIn("quux", self.parsed["word_substitutions"])

    def test_multiword_alternative_is_kept_whole(self):
        # "MAKE SURE" must not be truncated to "sure".
        self.assertEqual(self.parsed["word_substitutions"].get("guarantee"),
                         "make sure")

    def test_two_letter_alternative_is_captured(self):
        # Short approved verbs like GO/DO must still be captured.
        self.assertEqual(self.parsed["word_substitutions"].get("achieve"), "do")


class CacheRoundTripTests(unittest.TestCase):
    def test_write_and_load_cache(self):
        parsed = ste_import.parse_official(FAKE_DICT)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "official.json")
            ste_import.write_cache(path, parsed)
            loaded = ste_lint.load_cache(path)
            self.assertEqual(loaded["word_substitutions"]["zorp"], "start")

    def test_load_missing_cache_returns_none(self):
        self.assertIsNone(ste_lint.load_cache("/no/such/file.json"))


class LintWithCacheTests(unittest.TestCase):
    def test_cache_adds_new_substitution(self):
        cache = {"approved": [], "word_substitutions": {"widget": "gadget"},
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
        r = ste_lint.lint("We utilize the tool.")
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
            self.assertEqual(data["word_substitutions"]["acceptable"], "permitted")


if __name__ == "__main__":
    unittest.main()
