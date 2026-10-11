#!/usr/bin/env python3
"""Add the fixed Stayux Clear Answer frame to an explain file, in place.

Claude writes only the body content. This script adds the rest, so every page
looks the same and Claude does not spend tokens on CSS or the footer.

Usage:
    python3 explain_page.py how-dns-works.html   # wrap the body in the page frame
    python3 explain_page.py how-dns-works.md     # add the footer

Running it twice gives the same file. A page that already has the frame is
wrapped again from its body, so it picks up template changes.
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
START, END = "<!-- ca:body:start -->", "<!-- ca:body:end -->"
FOOTER_MARK = "Stayux Clear Answer"
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


def _template(name):
    # templates/ sits next to scripts/ in the repo, and next to this file in
    # the flat Desktop bundle.
    for folder in (os.path.join(HERE, os.pardir, "templates"), HERE):
        path = os.path.join(folder, name)
        if os.path.exists(path):
            with open(path) as f:
                return f.read()
    raise FileNotFoundError(name)


def extract_body(page):
    """Return the body between the frame markers, or None if there is no frame."""
    if START not in page or END not in page:
        return None
    return page[page.index(START) + len(START):page.index(END)].strip("\n")


def _title(body):
    m = H1_RE.search(body)
    if not m:
        return "Clear Answer"
    text = " ".join(html.unescape(TAG_RE.sub("", m.group(1))).split())
    return html.escape(text, quote=False) or "Clear Answer"


def wrap_html(text):
    body = extract_body(text)
    body = (text if body is None else body).strip("\n")
    page = _template("explain-page.html")
    return page.replace("{{title}}", _title(body)).replace("{{body}}", body)


def add_md_footer(text):
    if FOOTER_MARK in text:
        return text
    return text.rstrip("\n") + "\n" + _template("explain-footer.md")


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: explain_page.py FILE.html|FILE.md", file=sys.stderr)
        return 2
    path = args[0]
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".html", ".md"):
        print(f"explain_page.py: expected a .html or .md file, got {path}", file=sys.stderr)
        return 2
    with open(path) as f:
        text = f.read()
    out = wrap_html(text) if ext == ".html" else add_md_footer(text)
    with open(path, "w") as f:
        f.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
