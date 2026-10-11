"""Tests for scripts/explain_build.py: fill the blanks, build HTML or Markdown.

Run: python3 -m unittest discover -s tests
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))

import explain_build  # noqa: E402

SEQUENCE = """# A comment line
title: How DNS works
answer: DNS turns a name, such as `example.com`, into an IP address. Your computer asks a resolver.
diagram: sequence
actor B: Browser
actor R: Resolver
actor N: Name server
B -> R: Ask for the address
R -> N: Ask the name server
N --> R: Send the address
R --> B: Send the address
caption: The resolver finds the address for the browser.
part: Resolver | Finds the address for your computer.
part: Name server | Keeps the records for a domain.
step: The browser asks the resolver for the address.
step: The resolver asks the name server.
section: Example | You type `www.example.com` in the browser.
limits: The resolver keeps a copy for a set time.
"""

FLOW = """title: How a build works
answer: A build turns source code into a program.
diagram: flow
node: Write the code
node: Compile it
node: Run the tests
caption: Each stage starts when the stage before it ends.
part: Compiler | Turns the code into a program.
step: Write the code.
limits: A build does not show that the program is correct.
"""


def wheres(result, rule=None):
    return [p["where"] for p in result["problems"] if rule is None or p["rule"] == rule]


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.doc = explain_build.parse(SEQUENCE)

    def test_blanks(self):
        self.assertEqual(self.doc["title"], "How DNS works")
        self.assertEqual(self.doc["diagram"], "sequence")
        self.assertEqual(self.doc["caption"], "The resolver finds the address for the browser.")
        self.assertEqual(self.doc["limits"], "The resolver keeps a copy for a set time.")

    def test_actors_and_messages(self):
        self.assertEqual(self.doc["actors"], [("B", "Browser"), ("R", "Resolver"), ("N", "Name server")])
        self.assertEqual(self.doc["messages"][0], ("B", "R", "request", "Ask for the address"))
        self.assertEqual(self.doc["messages"][2], ("N", "R", "reply", "Send the address"))

    def test_lists(self):
        self.assertEqual(self.doc["parts"][0], ("Resolver", "Finds the address for your computer."))
        self.assertEqual(len(self.doc["steps"]), 2)
        self.assertEqual(self.doc["sections"], [("Example", "You type `www.example.com` in the browser.")])

    def test_flow_nodes(self):
        doc = explain_build.parse(FLOW)
        self.assertEqual(doc["nodes"], ["Write the code", "Compile it", "Run the tests"])


class StructureTests(unittest.TestCase):
    def problems(self, text):
        return explain_build.check(explain_build.parse(text))["problems"]

    def structure(self, text):
        return [p["where"] for p in self.problems(text) if p["rule"] == "structure"]

    def test_valid_files_have_no_structure_problems(self):
        self.assertEqual(self.structure(SEQUENCE), [])
        self.assertEqual(self.structure(FLOW), [])

    def test_missing_title(self):
        self.assertIn("title", self.structure(SEQUENCE.replace("title: How DNS works\n", "")))

    def test_answer_too_long(self):
        long = "answer: Open it. Close it. Stop it. Start it.\n"
        text = re.sub(r"answer: .*\n", long, SEQUENCE)
        self.assertIn("answer", self.structure(text))

    def test_unknown_actor(self):
        self.assertIn("message 1", self.structure(SEQUENCE.replace("B -> R:", "X -> R:")))

    def test_message_to_self(self):
        self.assertIn("message 1", self.structure(SEQUENCE.replace("B -> R:", "B -> B:")))

    def test_too_many_actors(self):
        extra = "".join(f"actor X{i}: Box {i}\n" for i in range(3))
        self.assertIn("diagram", self.structure(SEQUENCE.replace("actor N: Name server\n",
                                                                "actor N: Name server\n" + extra)))

    def test_long_actor_label(self):
        self.assertIn("actor B", self.structure(SEQUENCE.replace("actor B: Browser", "actor B: The web browser app")))

    def test_unknown_section_name(self):
        self.assertIn("section 1", self.structure(SEQUENCE.replace("section: Example", "section: Background")))

    def test_unknown_line(self):
        self.assertIn("line 3", self.structure("title: X\nanswer: Open it.\nfoo bar\n"))

    def test_unknown_diagram_kind(self):
        self.assertIn("diagram", self.structure(SEQUENCE.replace("diagram: sequence", "diagram: pie")))


class LintTests(unittest.TestCase):
    def check(self, text):
        return explain_build.check(explain_build.parse(text))

    def test_clean_file_passes(self):
        r = self.check(SEQUENCE)
        self.assertTrue(r["passed"], r["problems"])

    def test_problem_names_the_blank(self):
        r = self.check(SEQUENCE.replace("step: The resolver asks the name server.",
                                        "step: The resolver is asking the name server."))
        self.assertIn("step 2", wheres(r, "progressive-tense"))
        self.assertFalse(r["passed"])

    def test_message_label_is_linted_as_a_label(self):
        r = self.check(SEQUENCE.replace("Ask for the address", "Ask for the address of the site in the end now"))
        self.assertIn("message 1", wheres(r, "label-length"))

    def test_caption_and_part_are_linted(self):
        r = self.check(SEQUENCE.replace("Keeps the records", "Has kept the records"))
        self.assertIn("part 2", wheres(r, "perfect-tense"))

    def test_code_in_backticks_is_not_linted(self):
        r = self.check(SEQUENCE.replace("`www.example.com`", "`is running`"))
        self.assertNotIn("progressive-tense", [p["rule"] for p in r["problems"]])


class MarkdownTests(unittest.TestCase):
    def setUp(self):
        self.md = explain_build.render_md(explain_build.parse(SEQUENCE))

    def test_sections_in_order(self):
        order = [self.md.index(s) for s in ("# How DNS works", "```mermaid", "## The parts",
                                            "## The steps", "## Example", "## Limits", "Stayux Clear Answer")]
        self.assertEqual(order, sorted(order))

    def test_mermaid_sequence(self):
        self.assertIn('%%{init: {"theme": "neutral"}}%%\nsequenceDiagram\n    autonumber', self.md)
        self.assertIn("    participant B as Browser", self.md)
        self.assertIn("    B->>R: Ask for the address", self.md)
        self.assertIn("    N-->>R: Send the address", self.md)

    def test_parts_table(self):
        self.assertIn("| Part | What it does |", self.md)
        self.assertIn("| Resolver | Finds the address for your computer. |", self.md)

    def test_steps_numbered(self):
        self.assertIn("1. The browser asks the resolver for the address.", self.md)

    def test_mermaid_flow(self):
        md = explain_build.render_md(explain_build.parse(FLOW))
        self.assertIn("flowchart LR", md)
        self.assertIn('N1["Write the code"] --> N2["Compile it"]', md)


class HtmlTests(unittest.TestCase):
    def setUp(self):
        self.page = explain_build.render_html(explain_build.parse(SEQUENCE))

    def test_framed_page_with_sections(self):
        self.assertIn("<title>How DNS works</title>", self.page)
        for s in ("<h1>How DNS works</h1>", '<p class="ca-answer">', "<h2>The parts</h2>",
                  "<dt>Resolver</dt>", "<h2>The steps</h2>", "<h2>Example</h2>", "<h2>Limits</h2>"):
            self.assertIn(s, self.page)
        self.assertIn('class="ca-footer"', self.page)

    def test_backticks_become_code(self):
        self.assertIn("<code>example.com</code>", self.page)

    def test_text_is_escaped(self):
        page = explain_build.render_html(explain_build.parse(SEQUENCE.replace("Keeps the records", "Keeps <b> records")))
        self.assertIn("Keeps &lt;b&gt; records", page)

    def test_lanes_geometry(self):
        arrows = re.findall(r'<path class="edge( reply)?" d="M (\d+) (\d+) H (\d+)"/>', self.page)
        self.assertEqual(len(arrows), 4)
        ys = [int(a[2]) for a in arrows]
        self.assertEqual(ys, [98, 138, 178, 218])  # one horizontal arrow per step
        self.assertEqual([bool(a[0]) for a in arrows], [False, False, True, True])
        self.assertEqual(len(re.findall(r'class="lifeline"', self.page)), 3)

    def test_step_labels_sit_above_their_arrows(self):
        labels = re.findall(r'<text class="step" x="\d+" y="(\d+)">', self.page)
        self.assertEqual([int(y) for y in labels], [90, 130, 170, 210])

    def test_flow_row(self):
        page = explain_build.render_html(explain_build.parse(FLOW))
        self.assertEqual(len(re.findall(r'<g class="node">', page)), 3)
        self.assertEqual(len(re.findall(r'<path class="edge" d="M \d+ 68 H \d+"/>', page)), 2)

    def test_page_passes_the_page_linter(self):
        import ste_lint
        r = ste_lint.lint(self.page, fmt="html", cache={}, custom={})
        self.assertTrue(r["passed"], r["violations"])


class CliTests(unittest.TestCase):
    def build(self, text, to):
        d = tempfile.mkdtemp()
        src = os.path.join(d, "how-dns-works.clear.txt")
        with open(src, "w") as f:
            f.write(text)
        p = subprocess.run([sys.executable, os.path.join(SKILL_ROOT, "scripts", "explain_build.py"),
                            src, "--to", to], capture_output=True, text=True)
        return p, d

    def test_builds_html(self):
        p, d = self.build(SEQUENCE, "html")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        out = json.loads(p.stdout)
        self.assertTrue(out["passed"])
        self.assertEqual(out["file"], os.path.join(d, "how-dns-works.html"))
        self.assertTrue(os.path.exists(out["file"]))
        self.assertTrue(os.path.exists(os.path.join(d, "how-dns-works.clear.txt")))

    def test_builds_markdown(self):
        p, d = self.build(SEQUENCE, "md")
        self.assertEqual(p.returncode, 0)
        self.assertTrue(os.path.exists(os.path.join(d, "how-dns-works.md")))

    def test_error_writes_no_file(self):
        p, d = self.build(SEQUENCE.replace("Keeps the records", "Has kept the records"), "html")
        self.assertEqual(p.returncode, 1)
        out = json.loads(p.stdout)
        self.assertFalse(out["passed"])
        self.assertIsNone(out["file"])
        self.assertFalse(os.path.exists(os.path.join(d, "how-dns-works.html")))


if __name__ == "__main__":
    unittest.main()
