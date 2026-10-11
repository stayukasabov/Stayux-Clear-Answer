"""Tests for scripts/explain_page.py, the fixed frame for explain files.

Run: python3 -m unittest discover -s tests
"""
import os
import subprocess
import sys
import tempfile
import unittest

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))

import explain_page  # noqa: E402
import ste_lint      # noqa: E402

BODY = """<h1>How a valve works</h1>
<p class="ca-answer">A valve controls the flow of a liquid. Open the valve to start the flow.</p>
<h2>The steps</h2>
<ol><li>Open the valve.</li><li>Close the valve.</li></ol>
"""
LINKS = ("https://stayux.com", "https://www.linkedin.com/in/stayu-kasabov-stayux/",
         "https://x.com/StayuKasabov")


class WrapHtmlTests(unittest.TestCase):
    def setUp(self):
        self.page = explain_page.wrap_html(BODY)

    def test_is_a_full_page(self):
        self.assertTrue(self.page.lstrip().lower().startswith("<!doctype html>"))
        self.assertIn("</html>", self.page)

    def test_title_comes_from_h1(self):
        self.assertIn("<title>How a valve works</title>", self.page)

    def test_body_is_inside(self):
        self.assertIn("<li>Open the valve.</li>", self.page)

    def test_frame_has_css_marker_and_footer(self):
        self.assertIn("<style>", self.page)
        self.assertIn('id="ca-arrow"', self.page)
        self.assertIn("prefers-color-scheme: dark", self.page)
        footer = self.page[self.page.index('<footer class="ca-footer">'):]
        for url in LINKS:
            self.assertIn(f'href="{url}" target="_blank" rel="noopener noreferrer"', footer)
        self.assertIn(">Stayux.com</a>", footer)

    def test_footer_style(self):
        for rule in ("font: 14px system-ui", "text-align: center",
                     "text-decoration: underline", ".ca-footer a:hover"):
            self.assertIn(rule, self.page)

    def test_wrapping_twice_gives_the_same_page(self):
        self.assertEqual(explain_page.wrap_html(self.page), self.page)

    def test_extract_body(self):
        self.assertEqual(explain_page.extract_body(self.page).strip(), BODY.strip())
        self.assertIsNone(explain_page.extract_body(BODY))

    def test_page_passes_the_linter(self):
        r = ste_lint.lint(self.page, fmt="html", cache={}, custom={})
        self.assertTrue(r["passed"], r["violations"])
        self.assertNotIn("external-request", [v["rule"] for v in r["violations"]])

    def test_title_is_escaped(self):
        page = explain_page.wrap_html("<h1>A &amp; B</h1><p>Open it.</p>")
        self.assertIn("<title>A &amp; B</title>", page)

    def test_missing_h1_uses_a_default_title(self):
        page = explain_page.wrap_html("<p>Open it.</p>")
        self.assertIn("<title>Clear Answer</title>", page)


class MarkdownFooterTests(unittest.TestCase):
    def test_footer_added_once(self):
        text = explain_page.add_md_footer("# How a valve works\n\nOpen the valve.\n")
        self.assertEqual(explain_page.add_md_footer(text), text)
        self.assertIn(">Stayux.com</a>", text)
        for url in LINKS:
            self.assertIn(f'href="{url}" target="_blank" rel="noopener noreferrer"', text)

    def test_markdown_with_footer_passes(self):
        text = explain_page.add_md_footer("# How a valve works\n\nOpen the valve.\n")
        self.assertTrue(ste_lint.lint(text, cache={}, custom={})["passed"])


class CliTests(unittest.TestCase):
    def run_script(self, path):
        return subprocess.run(
            [sys.executable, os.path.join(SKILL_ROOT, "scripts", "explain_page.py"), path],
            capture_output=True, text=True)

    def test_html_file_is_wrapped_in_place(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "how-a-valve-works.html")
            with open(path, "w") as f:
                f.write(BODY)
            p = self.run_script(path)
            self.assertEqual(p.returncode, 0, p.stderr)
            with open(path) as f:
                self.assertIn("<!doctype html>", f.read())

    def test_md_file_gets_the_footer(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "how-a-valve-works.md")
            with open(path, "w") as f:
                f.write("# How a valve works\n\nOpen the valve.\n")
            self.assertEqual(self.run_script(path).returncode, 0)
            with open(path) as f:
                self.assertIn("Stayux Clear Answer", f.read())

    def test_other_file_type_is_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "notes.txt")
            open(path, "w").close()
            self.assertNotEqual(self.run_script(path).returncode, 0)


class FixtureTests(unittest.TestCase):
    def test_fixture_page_is_the_wrapped_body(self):
        with open(os.path.join(SKILL_ROOT, "tests", "fixtures", "explain-body.html")) as f:
            body = f.read()
        with open(os.path.join(SKILL_ROOT, "tests", "fixtures", "explain-page.html")) as f:
            self.assertEqual(f.read(), explain_page.wrap_html(body))


if __name__ == "__main__":
    unittest.main()
