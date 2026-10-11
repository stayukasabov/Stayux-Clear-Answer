"""Tests for the duplicate skill check (PRD F9).

Run: python3 -m unittest discover -s tests
"""
import os
import subprocess
import sys
import tempfile
import unittest

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))

import ste_dupcheck  # noqa: E402


def make_skill(root, account, folder, name):
    path = os.path.join(root, account, folder)
    os.makedirs(path)
    with open(os.path.join(path, "SKILL.md"), "w") as f:
        f.write(f"---\nname: {name}\ndescription: x\n---\n\nBody.\n")
    return os.path.join(path, "SKILL.md")


class FindDuplicatesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_finds_synced_clear_answer(self):
        path = make_skill(self.root, "acct-1", "stayux-clear-answer", "stayux-clear-answer")
        self.assertEqual(ste_dupcheck.find_duplicates(self.root), [path])

    def test_finds_old_name(self):
        path = make_skill(self.root, "acct-1", "stayux-ste", "stayux-ste")
        self.assertEqual(ste_dupcheck.find_duplicates(self.root), [path])

    def test_ignores_other_skills(self):
        make_skill(self.root, "acct-1", "docx", "docx")
        self.assertEqual(ste_dupcheck.find_duplicates(self.root), [])

    def test_matches_name_field_not_folder(self):
        path = make_skill(self.root, "acct-1", "renamed-folder", "clear-write")
        self.assertEqual(ste_dupcheck.find_duplicates(self.root), [path])

    def test_ignores_hidden_folders(self):
        make_skill(self.root, ".staging", "stayux-clear-answer", "stayux-clear-answer")
        self.assertEqual(ste_dupcheck.find_duplicates(self.root), [])

    def test_missing_folder_gives_no_duplicates(self):
        self.assertEqual(ste_dupcheck.find_duplicates(os.path.join(self.root, "nope")), [])


class MessageTests(unittest.TestCase):
    def test_no_duplicates_prints_nothing(self):
        self.assertEqual(ste_dupcheck.message([]), "")

    def test_message_names_the_copy_and_the_fix(self):
        msg = ste_dupcheck.message(["/x/synced/a/stayux-clear-answer/SKILL.md"])
        self.assertIn("/x/synced/a/stayux-clear-answer/SKILL.md", msg)
        self.assertIn("plugin", msg)
        self.assertIn("claude.ai", msg)


class CliTests(unittest.TestCase):
    def test_cli_reports_duplicate_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as root:
            make_skill(root, "acct-1", "stayux-clear-answer", "stayux-clear-answer")
            p = subprocess.run(
                [sys.executable, os.path.join(SKILL_ROOT, "scripts", "ste_dupcheck.py"),
                 "--skills-dir", root], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("stayux-clear-answer", p.stdout)

    def test_cli_silent_when_clean(self):
        with tempfile.TemporaryDirectory() as root:
            p = subprocess.run(
                [sys.executable, os.path.join(SKILL_ROOT, "scripts", "ste_dupcheck.py"),
                 "--skills-dir", root], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdout, "")


if __name__ == "__main__":
    unittest.main()
