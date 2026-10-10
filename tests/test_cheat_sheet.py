"""Known errors in the STE cheat sheet shared with Karpathy's post.

Each test checks that the linter follows ASD-STE100 Issue 9, not the cheat
sheet. Source: https://max.nardit.com/articles/karpathy-understanding-llm-outputs

Run: python3 -m unittest discover -s tests
"""
import os
import sys
import unittest

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))

import ste_lint  # noqa: E402


def rules(result):
    return [v["rule"] for v in result["violations"]]


def lint(text):
    # No official cache or custom list, so only the shipped seed is tested.
    return ste_lint.lint(text, cache={}, custom={})


class ApproximatelyTests(unittest.TestCase):
    # Cheat sheet: "approximately" is not approved. Issue 9: APPROXIMATELY (adv) is approved.
    def test_approximately_not_flagged(self):
        r = lint("Drain approximately 2 liters of fuel.")
        self.assertNotIn("unapproved-word", rules(r))


class TestAsVerbTests(unittest.TestCase):
    # Cheat sheet: TEST (v) is approved. Issue 9: TEST is a noun only.
    def test_imperative_test_flagged(self):
        r = lint("Test the software.")
        self.assertIn("unapproved-word", rules(r))

    def test_adverb_then_test_flagged(self):
        r = lint("Functionally test the software.")
        self.assertIn("unapproved-word", rules(r))

    def test_detail_suggests_noun_form(self):
        r = lint("Test the software.")
        detail = next(v["detail"] for v in r["violations"] if v["rule"] == "unapproved-word")
        self.assertIn("do a test of", detail)

    def test_noun_not_flagged(self):
        r = lint("Do a functional test of the software.")
        self.assertNotIn("unapproved-word", rules(r))

    def test_noun_as_subject_not_flagged(self):
        r = lint("Test results show the valve is open.")
        self.assertNotIn("unapproved-word", rules(r))


class InOrderToTests(unittest.TestCase):
    # Cheat sheet: "in order to" is a dictionary row. Issue 9: no such entry.
    def test_in_order_to_is_wordiness(self):
        r = lint("Open the valve in order to drain the tank.")
        self.assertIn("wordiness", rules(r))

    def test_in_order_to_is_not_an_ste_dictionary_finding(self):
        r = lint("Open the valve in order to drain the tank.")
        self.assertNotIn("unapproved-word", rules(r))


if __name__ == "__main__":
    unittest.main()
