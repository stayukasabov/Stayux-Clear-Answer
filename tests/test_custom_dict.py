"""TDD spec for the custom / project dictionary (.ste-dict.txt).

Run: python3 -m unittest discover -s tests
"""
import os
import sys
import tempfile
import unittest

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))

import ste_lint  # noqa: E402


def details(result, rule="unapproved-word"):
    return [v["detail"] for v in result["violations"] if v["rule"] == rule]


SAMPLE = """\
# project dictionary
bolt = fastener
in order to = to
widget                 # approved technical term
+gizmo
Utilize = apply        # keys are case-insensitive
"""


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.d = ste_lint.parse_custom_dict(SAMPLE)

    def test_single_word_substitution(self):
        self.assertEqual(self.d["word_substitutions"]["bolt"], "fastener")

    def test_multiword_is_a_phrase_substitution(self):
        self.assertEqual(self.d["phrase_substitutions"]["in order to"], "to")
        self.assertNotIn("in order to", self.d["word_substitutions"])

    def test_bare_word_is_approved(self):
        self.assertIn("widget", self.d["approved"])

    def test_leading_plus_is_approved(self):
        self.assertIn("gizmo", self.d["approved"])
        self.assertNotIn("+gizmo", self.d["approved"])

    def test_keys_are_lowercased(self):
        self.assertEqual(self.d["word_substitutions"]["utilize"], "apply")

    def test_comments_and_blanks_ignored(self):
        # No stray key from the comment line or blank lines.
        self.assertNotIn("#", "".join(self.d["word_substitutions"]))
        self.assertNotIn("project", self.d["word_substitutions"])


class LoadTests(unittest.TestCase):
    def test_load_reads_file(self):
        with tempfile.TemporaryDirectory() as dd:
            p = os.path.join(dd, ".ste-dict.txt")
            with open(p, "w") as f:
                f.write(SAMPLE)
            loaded = ste_lint.load_custom_dict(p)
            self.assertEqual(loaded["word_substitutions"]["bolt"], "fastener")

    def test_missing_file_returns_none(self):
        self.assertIsNone(ste_lint.load_custom_dict("/no/such/.ste-dict.txt"))


class LintTests(unittest.TestCase):
    def test_custom_adds_substitution(self):
        d = ste_lint.parse_custom_dict("bolt = fastener\n")
        r = ste_lint.lint("Install the bolt.", custom=d)
        self.assertIn("use 'fastener' instead of 'bolt'", details(r))

    def test_custom_approved_suppresses_seed_false_positive(self):
        d = ste_lint.parse_custom_dict("utilize\n")
        r = ste_lint.lint("We utilize the tool.", custom=d)
        self.assertNotIn("use 'use' instead of 'utilize'", details(r))

    def test_custom_wins_over_official_cache(self):
        cache = {"approved": [], "word_substitutions": {"bolt": "pin"},
                 "phrase_substitutions": {}}
        d = ste_lint.parse_custom_dict("bolt = fastener\n")
        r = ste_lint.lint("Install the bolt.", cache=cache, custom=d)
        self.assertIn("use 'fastener' instead of 'bolt'", details(r))
        self.assertNotIn("use 'pin' instead of 'bolt'", details(r))

    def test_custom_phrase_substitution(self):
        d = ste_lint.parse_custom_dict("as per = by\n")
        r = ste_lint.lint("Torque the bolt as per the manual.", custom=d)
        self.assertIn("use 'by' instead of 'as per'", details(r))

    def test_no_custom_behaves_as_seed(self):
        r = ste_lint.lint("We utilize the tool.")
        self.assertIn("use 'use' instead of 'utilize'", details(r))


if __name__ == "__main__":
    unittest.main()
