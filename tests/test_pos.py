"""Tests for the rule-based part-of-speech tagger (scripts/ste_pos.py).

Run: python3 -m unittest discover -s tests
"""
import os
import sys
import unittest

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))

import ste_pos  # noqa: E402


def tag_of(sentence, word):
    words = sentence.rstrip(".").split()
    tags = ste_pos.tag(words)
    return tags[[w.lower() for w in words].index(word)]


class NounTests(unittest.TestCase):
    def test_after_article(self):
        self.assertEqual(tag_of("Open the file.", "file"), "n")

    def test_after_possessive(self):
        self.assertEqual(tag_of("Save your file.", "file"), "n")

    def test_after_preposition_and_article(self):
        self.assertEqual(tag_of("Remove the dust from a branch.", "branch"), "n")

    def test_after_preposition(self):
        self.assertEqual(tag_of("Send it by request.", "request"), "n")

    def test_after_adjective_in_noun_phrase(self):
        self.assertEqual(tag_of("Open the new file.", "file"), "n")


class AdjectiveTests(unittest.TestCase):
    def test_before_noun_after_article(self):
        self.assertEqual(tag_of("Open the main valve.", "main"), "adj")

    def test_noun_modifier_counts_as_adjective(self):
        self.assertEqual(tag_of("Open the file menu.", "file"), "adj")


class VerbTests(unittest.TestCase):
    def test_after_to(self):
        self.assertEqual(tag_of("Use a tool to file the edge.", "file"), "v")

    def test_after_modal(self):
        self.assertEqual(tag_of("You must test the pump.", "test"), "v")

    def test_after_do_not(self):
        self.assertEqual(tag_of("Do not test the pump.", "test"), "v")

    def test_after_subject_pronoun(self):
        self.assertEqual(tag_of("Then you test the pump.", "test"), "v")

    def test_imperative_start(self):
        self.assertEqual(tag_of("Test the software.", "test"), "v")

    def test_imperative_after_ly_adverb(self):
        self.assertEqual(tag_of("Functionally test the software.", "test"), "v")


class OtherTests(unittest.TestCase):
    def test_ly_adverb(self):
        self.assertEqual(tag_of("Open the valve slowly.", "slowly"), "adv")

    def test_noun_subject_at_start_is_unknown(self):
        self.assertIsNone(tag_of("Test results show a leak.", "test"))

    def test_unclear_context_is_unknown(self):
        self.assertIsNone(tag_of("Files open slowly.", "files"))

    def test_same_length_as_input(self):
        words = ["Open", "the", "file"]
        self.assertEqual(len(ste_pos.tag(words)), 3)

    def test_empty(self):
        self.assertEqual(ste_pos.tag([]), [])


class KeyTests(unittest.TestCase):
    def test_split_key_with_pos(self):
        self.assertEqual(ste_pos.split_key("file (v)"), ("file", "v"))

    def test_split_key_without_pos(self):
        self.assertEqual(ste_pos.split_key("utilize"), ("utilize", None))

    def test_split_key_multiword(self):
        self.assertEqual(ste_pos.split_key("make sure (v)"), ("make sure", "v"))


if __name__ == "__main__":
    unittest.main()
