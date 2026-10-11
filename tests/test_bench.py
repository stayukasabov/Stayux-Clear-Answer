"""Tests for the benchmark tasks and the pure functions in scripts/bench.py.

No test calls `claude`. Run: python3 -m unittest discover -s tests
"""
import json
import os
import sys
import unittest

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_PATH = os.path.join(SKILL_ROOT, "bench", "tasks.json")
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))

import bench  # noqa: E402

CHAT = {"id": "c1", "type": "chat", "prompt": "What is a CDN?"}
WRITE = {"id": "d1", "type": "write", "prompt": "Write a procedure."}
REWRITE = {"id": "d6", "type": "rewrite", "prompt": "Rewrite this.", "source": "Old text."}


class TasksFileTests(unittest.TestCase):
    def setUp(self):
        with open(TASKS_PATH) as f:
            self.tasks = json.load(f)

    def test_ten_chat_and_ten_document_tasks(self):
        types = [t["type"] for t in self.tasks]
        self.assertEqual(types.count("chat"), 10)
        self.assertEqual(types.count("write") + types.count("rewrite"), 10)

    def test_ids_are_unique(self):
        ids = [t["id"] for t in self.tasks]
        self.assertEqual(len(ids), len(set(ids)))

    def test_each_rewrite_task_has_a_source(self):
        for t in self.tasks:
            if t["type"] == "rewrite":
                self.assertTrue(t.get("source", "").strip(), t["id"])

    def test_each_task_has_a_prompt(self):
        for t in self.tasks:
            self.assertTrue(t["prompt"].strip(), t["id"])


class PromptTests(unittest.TestCase):
    def test_rewrite_prompt_includes_source(self):
        self.assertEqual(bench.task_text(REWRITE), "Rewrite this.\n\nOld text.")

    def test_chat_prompt_is_the_question(self):
        self.assertEqual(bench.task_text(CHAT), "What is a CDN?")

    def test_profile_by_task_type(self):
        self.assertEqual(bench.profile_for(CHAT), "chat")
        self.assertEqual(bench.profile_for(WRITE), "full")
        self.assertEqual(bench.profile_for(REWRITE), "full")


class BuildCmdTests(unittest.TestCase):
    def _arg(self, cmd, flag):
        return cmd[cmd.index(flag) + 1]

    def test_off_has_no_plugin_and_no_tools(self):
        cmd = bench.build_cmd("haiku", "off", CHAT, "/repo")
        self.assertEqual(cmd[:3], ["claude", "-p", "What is a CDN?"])
        self.assertNotIn("--plugin-dir", cmd)
        self.assertEqual(self._arg(cmd, "--tools"), "")
        self.assertEqual(self._arg(cmd, "--model"), "haiku")

    def test_off_is_isolated_from_user_settings(self):
        cmd = bench.build_cmd("haiku", "off", CHAT, "/repo")
        self.assertEqual(self._arg(cmd, "--setting-sources"), "")
        self.assertIn("--no-session-persistence", cmd)
        self.assertEqual(self._arg(cmd, "--output-format"), "json")

    def test_setup_chat_turns_mode_on_with_plugin(self):
        cmd = bench.setup_cmd("sonnet", CHAT, "/repo")
        self.assertEqual(cmd[2], "/clear-answer:on")
        self.assertEqual(self._arg(cmd, "--plugin-dir"), "/repo")
        self.assertEqual(self._arg(cmd, "--setting-sources"), "")
        self.assertNotIn("--no-session-persistence", cmd)

    def test_setup_document_uses_strict_mode(self):
        cmd = bench.setup_cmd("opus", WRITE, "/repo")
        self.assertEqual(cmd[2], "/clear-answer:mode strict")

    def test_on_resumes_the_setup_session(self):
        cmd = bench.build_cmd("sonnet", "on", CHAT, "/repo", resume="abc-123")
        self.assertEqual(cmd[2], "What is a CDN?")
        self.assertEqual(self._arg(cmd, "--resume"), "abc-123")
        self.assertEqual(self._arg(cmd, "--plugin-dir"), "/repo")
        self.assertEqual(self._arg(cmd, "--tools"), "Bash,Read")
        self.assertEqual(self._arg(cmd, "--allowedTools"), "Bash(python3:*)")
        self.assertNotIn("--no-session-persistence", cmd)

    def test_on_can_read_the_plugin_files(self):
        for cmd in (bench.setup_cmd("haiku", CHAT, "/repo"),
                    bench.build_cmd("haiku", "on", CHAT, "/repo", resume="x")):
            self.assertEqual(self._arg(cmd, "--add-dir"), "/repo")


class MetricsTests(unittest.TestCase):
    def test_clean_text(self):
        m = bench.metrics("Open the valve. Close the door.", "chat")
        self.assertEqual(m["words"], 6)
        self.assertEqual(m["errors_per_100"], 0)
        self.assertEqual(m["format_defects"], 0)

    def test_rates_are_per_100_words(self):
        m = bench.metrics("Do this; do that.", "chat")  # 4 words, 1 error
        self.assertEqual(m["errors_per_100"], 25.0)

    def test_format_defects_counted(self):
        m = bench.metrics("Great question! Open the valve. I hope this helps.", "chat")
        self.assertEqual(m["format_defects"], 2)

    def test_empty_text_has_zero_rates(self):
        m = bench.metrics("", "chat")
        self.assertEqual(m["words"], 0)
        self.assertEqual(m["errors_per_100"], 0)


class JudgeTests(unittest.TestCase):
    def test_judge_is_never_the_writer(self):
        for writer in ("haiku", "sonnet", "opus"):
            self.assertNotEqual(bench.judge_model(writer), writer)

    def test_order_is_stable(self):
        a = bench.on_first("c1", "haiku")
        self.assertEqual(a, bench.on_first("c1", "haiku"))

    def test_order_varies_across_tasks(self):
        orders = {bench.on_first(f"c{i}", "haiku") for i in range(1, 11)}
        self.assertEqual(orders, {True, False})

    J = '{"a": {"score": 4, "lost": ["the port number"]}, "b": {"score": 5, "lost": []}}'

    def test_parse_plain_json(self):
        r = bench.parse_judge(self.J)
        self.assertEqual(r["a"], {"score": 4, "lost": ["the port number"]})
        self.assertEqual(r["b"]["score"], 5)

    def test_parse_fenced_json(self):
        r = bench.parse_judge("```json\n" + self.J + "\n```")
        self.assertEqual(r["a"]["score"], 4)

    def test_parse_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            bench.parse_judge('{"a": {"score": 7, "lost": []}, "b": {"score": 5, "lost": []}}')

    def test_parse_rejects_missing_text(self):
        with self.assertRaises(ValueError):
            bench.parse_judge('{"a": {"score": 4, "lost": []}}')

    def test_parse_rejects_non_json(self):
        with self.assertRaises(ValueError):
            bench.parse_judge("The score is 4.")

    def test_judge_prompt_hides_conditions(self):
        p = bench.judge_prompt(CHAT, "first text", "second text")
        self.assertIn("Text A:\nfirst text", p)
        self.assertIn("Text B:\nsecond text", p)
        for word in ("gate", "STE", "linter", "Clear Answer", "on", "off"):
            self.assertNotRegex(p, r"\b" + word + r"\b")

    def test_judge_prompt_includes_rewrite_source(self):
        p = bench.judge_prompt(REWRITE, "x", "y")
        self.assertIn("Old text.", p)


class StorageTests(unittest.TestCase):
    def test_result_path(self):
        self.assertEqual(bench.result_path("/r", "haiku", "c1", "on"),
                         os.path.join("/r", "raw", "haiku", "c1", "on.json"))

    def test_error_result_is_a_stop(self):
        self.assertTrue(bench.is_stop({"is_error": True, "result": "limit"}))
        self.assertFalse(bench.is_stop({"is_error": False, "result": "ok"}))


if __name__ == "__main__":
    unittest.main()
