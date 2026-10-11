#!/usr/bin/env python3
"""Build an explain page or Markdown file from a content file of filled blanks.

Claude writes only the blanks (see commands/explain/html.md). This script
checks the structure, lints each blank on its own, and builds the output:
the HTML page or the Markdown file, with the diagram drawn from the same data.
The template, the plugin title, and the footer are never linted.

Usage:
    python3 explain_build.py how-dns-works.clear.txt --to html|md

Prints JSON: {"passed", "file", "problems": [{"where", "rule", "severity",
"detail", "text"}]}. Writes the output file only when there is no error, and
exits 1 on an error.
"""
import argparse
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import explain_page  # noqa: E402
import ste_lint      # noqa: E402

SECTION_NAMES = ("Example", "Common mistakes", "Safety")
SINGLE = ("title", "answer", "diagram", "caption", "limits")
MAX_ACTORS, MAX_MESSAGES, MAX_NODES, MAX_SECTIONS = 5, 12, 5, 2
MAX_BOX_WORDS = 3
MESSAGE_RE = re.compile(r"^(\w+)\s*(-->|->)\s*(\w+)\s*:\s*(.+)$")
ACTOR_RE = re.compile(r"^actor\s+(\w+)\s*:\s*(.+)$")
BLANK_RE = re.compile(r"^(title|answer|diagram|caption|limits|part|step|section|node)\s*:\s*(.*)$")
CODE_RE = re.compile(r"`([^`]+)`")
WIDTH = 760


def parse(text):
    doc = {"actors": [], "messages": [], "nodes": [], "parts": [], "steps": [],
           "sections": [], "unknown": [], "twice": []}
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = ACTOR_RE.match(line)
        if m:
            doc["actors"].append((m.group(1), m.group(2).strip()))
            continue
        m = MESSAGE_RE.match(line)
        if m:
            kind = "reply" if m.group(2) == "-->" else "request"
            doc["messages"].append((m.group(1), m.group(3), kind, m.group(4).strip()))
            continue
        m = BLANK_RE.match(line)
        if not m:
            doc["unknown"].append(n)
            continue
        key, value = m.group(1), m.group(2).strip()
        if key in SINGLE:
            if key in doc:
                doc["twice"].append(key)
            doc[key] = value
        elif key == "node":
            doc["nodes"].append(value)
        elif key == "step":
            doc["steps"].append(value)
        else:  # part, section: "name | text"
            name, _, body = value.partition("|")
            doc[key + "s"].append((name.strip(), body.strip()))
    return doc


def _problem(where, rule, detail, text="", severity="error"):
    return {"where": where, "rule": rule, "severity": severity, "detail": detail, "text": text[:60]}


def _structure(doc):
    out = []
    for n in doc["unknown"]:
        out.append(_problem(f"line {n}", "structure", "not a known blank"))
    for key in doc["twice"]:
        out.append(_problem(key, "structure", f"'{key}' appears more than once"))
    for key in SINGLE:
        if not doc.get(key):
            out.append(_problem(key, "structure", f"'{key}' is missing"))
    if doc.get("answer") and len(ste_lint._split_sentences(doc["answer"])) > 3:
        out.append(_problem("answer", "structure", "use 3 sentences or fewer", doc["answer"]))
    if doc.get("caption") and len(ste_lint._split_sentences(doc["caption"])) > 1:
        out.append(_problem("caption", "structure", "use one sentence", doc["caption"]))
    if not doc["parts"]:
        out.append(_problem("part", "structure", "add at least one part"))
    if not doc["steps"]:
        out.append(_problem("step", "structure", "add at least one step"))
    for i, (name, _) in enumerate(doc["sections"], 1):
        if name not in SECTION_NAMES:
            out.append(_problem(f"section {i}", "structure",
                                f"use one of: {', '.join(SECTION_NAMES)}", name))
    if len(doc["sections"]) > MAX_SECTIONS:
        out.append(_problem("section", "structure", f"use at most {MAX_SECTIONS} sections"))

    kind = doc.get("diagram")
    if kind == "sequence":
        ids = [a for a, _ in doc["actors"]]
        if not 2 <= len(ids) <= MAX_ACTORS:
            out.append(_problem("diagram", "structure", f"use 2 to {MAX_ACTORS} actors"))
        if not 1 <= len(doc["messages"]) <= MAX_MESSAGES:
            out.append(_problem("diagram", "structure", f"use 1 to {MAX_MESSAGES} messages"))
        for a, label in doc["actors"]:
            if len(ste_lint.WORD_RE.findall(label)) > MAX_BOX_WORDS:
                out.append(_problem(f"actor {a}", "structure",
                                    f"use {MAX_BOX_WORDS} words or fewer", label))
        for i, (src, dst, _, label) in enumerate(doc["messages"], 1):
            if src not in ids or dst not in ids:
                out.append(_problem(f"message {i}", "structure", "uses an actor that is not defined", label))
            elif src == dst:
                out.append(_problem(f"message {i}", "structure", "a message must go to another actor", label))
    elif kind == "flow":
        if not 2 <= len(doc["nodes"]) <= MAX_NODES:
            out.append(_problem("diagram", "structure", f"use 2 to {MAX_NODES} nodes"))
        for i, label in enumerate(doc["nodes"], 1):
            if len(ste_lint.WORD_RE.findall(label)) > MAX_BOX_WORDS:
                out.append(_problem(f"node {i}", "structure",
                                    f"use {MAX_BOX_WORDS} words or fewer", label))
    elif kind:
        out.append(_problem("diagram", "structure", "use 'sequence' or 'flow'", kind))
    return out


def _blanks(doc):
    """Yield (where, text, is_label) for every blank that Claude wrote."""
    for key in ("title", "answer", "caption", "limits"):
        if doc.get(key):
            yield key, doc[key], False
    for a, label in doc["actors"]:
        yield f"actor {a}", label, True
    for i, (_, _, _, label) in enumerate(doc["messages"], 1):
        yield f"message {i}", label, True
    for i, label in enumerate(doc["nodes"], 1):
        yield f"node {i}", label, True
    for i, (name, body) in enumerate(doc["parts"], 1):
        yield f"part {i}", name, True
        yield f"part {i}", body, False
    for i, text in enumerate(doc["steps"], 1):
        yield f"step {i}", text, False
    for i, (_, body) in enumerate(doc["sections"], 1):
        yield f"section {i}", body, False


def check(doc, cache=None, custom=None):
    problems = _structure(doc)
    for where, text, is_label in _blanks(doc):
        result = (ste_lint.lint_label(text, cache=cache, custom=custom) if is_label
                  else ste_lint.lint(text, profile="chat", cache=cache, custom=custom))
        for v in result["violations"]:
            problems.append(_problem(where, v["rule"], v["detail"], v["text"], v["severity"]))
    passed = not any(p["severity"] == "error" for p in problems)
    return {"passed": passed, "problems": problems}


# --- Markdown -------------------------------------------------------------

def _mermaid(doc):
    lines = ['%%{init: {"theme": "neutral"}}%%']
    if doc["diagram"] == "sequence":
        lines += ["sequenceDiagram", "    autonumber"]
        lines += [f"    participant {a} as {label}" for a, label in doc["actors"]]
        for src, dst, kind, label in doc["messages"]:
            arrow = "-->>" if kind == "reply" else "->>"
            lines.append(f"    {src}{arrow}{dst}: {label.replace(';', ',')}")
    else:
        nodes = [f'N{i}["{label.replace(chr(34), chr(39))}"]' for i, label in enumerate(doc["nodes"], 1)]
        lines += ["flowchart LR", "    " + " --> ".join(nodes)]
    return "\n".join(lines)


def render_md(doc):
    out = [f"# {doc['title']}", "", doc["answer"], "", "```mermaid", _mermaid(doc), "```", "",
           doc["caption"], "", "## The parts", "", "| Part | What it does |", "|---|---|"]
    out += [f"| {name} | {body} |" for name, body in doc["parts"]]
    out += ["", "## The steps", ""]
    out += [f"{i}. {text}" for i, text in enumerate(doc["steps"], 1)]
    for name, body in doc["sections"]:
        out += ["", f"## {name}", "", body]
    out += ["", "## Limits", "", doc["limits"], ""]
    return explain_page.add_md_footer("\n".join(out))


# --- HTML -----------------------------------------------------------------

def _inline(text):
    """Escape text for HTML and turn `code` into <code>."""
    return CODE_RE.sub(lambda m: f"<code>{m.group(1)}</code>", html.escape(text, quote=False))


def _box(cx, top, width, height, label):
    return (f'<g class="node"><rect x="{cx - width // 2}" y="{top}" width="{width}" '
            f'height="{height}" rx="4"/><text x="{cx}" y="{top + height // 2}">{_inline(label)}</text></g>')


def _lanes(doc):
    ids = [a for a, _ in doc["actors"]]
    n, m = len(ids), len(doc["messages"])
    left = (WIDTH - (150 * n - 10)) // 2 + 70
    cx = {a: left + 150 * i for i, a in enumerate(ids)}
    height = 58 + 40 * m + 30
    parts = [_box(cx[a], 10, 140, 48, label) for a, label in doc["actors"]]
    parts += [f'<path class="lifeline" d="M {cx[a]} 58 V {height - 10}"/>' for a in ids]
    for k, (src, dst, kind, label) in enumerate(doc["messages"], 1):
        y, a, b = 58 + 40 * k, cx[src], cx[dst]
        end = b - 4 if b > a else b + 4
        cls = "edge reply" if kind == "reply" else "edge"
        parts.append(f'<path class="{cls}" d="M {a} {y} H {end}"/>')
        parts.append(f'<text class="step" x="{(a + b) // 2}" y="{y - 8}">{k}. {_inline(label)}</text>')
    return height, parts


def _row(doc):
    n = len(doc["nodes"])
    left = (WIDTH - (180 * n - 30)) // 2 + 75
    xs = [left + 180 * i for i in range(n)]
    parts = [_box(x, 40, 150, 56, label) for x, label in zip(xs, doc["nodes"])]
    parts += [f'<path class="edge" d="M {a + 77} 68 H {b - 77}"/>' for a, b in zip(xs, xs[1:])]
    return 136, parts


def render_html(doc):
    height, shapes = _lanes(doc) if doc["diagram"] == "sequence" else _row(doc)
    svg = (f'<svg viewBox="0 0 {WIDTH} {height}" role="img" aria-label="{html.escape(doc["caption"])}">\n    '
           + "\n    ".join(shapes) + "\n  </svg>")
    body = [f"<h1>{_inline(doc['title'])}</h1>",
            f'<p class="ca-answer">{_inline(doc["answer"])}</p>',
            f'<figure class="ca-diagram">\n  {svg}\n  <figcaption>{_inline(doc["caption"])}</figcaption>\n</figure>',
            "<h2>The parts</h2>", "<dl>"]
    body += [f"  <dt>{_inline(name)}</dt><dd>{_inline(text)}</dd>" for name, text in doc["parts"]]
    body += ["</dl>", "<h2>The steps</h2>", "<ol>"]
    body += [f"  <li>{_inline(text)}</li>" for text in doc["steps"]]
    body.append("</ol>")
    for name, text in doc["sections"]:
        body += [f"<h2>{_inline(name)}</h2>", f"<p>{_inline(text)}</p>"]
    body += ["<h2>Limits</h2>", f"<p>{_inline(doc['limits'])}</p>"]
    return explain_page.wrap_html("\n".join(body))


def output_path(src, to):
    base = src[:-len(".clear.txt")] if src.endswith(".clear.txt") else os.path.splitext(src)[0]
    return f"{base}.{to}"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build an explain file from filled blanks")
    ap.add_argument("content", help="the content file, such as how-dns-works.clear.txt")
    ap.add_argument("--to", choices=("html", "md"), required=True)
    args = ap.parse_args(argv)

    with open(args.content) as f:
        doc = parse(f.read())
    result = check(doc)
    out = None
    if result["passed"]:
        out = os.path.abspath(output_path(args.content, args.to))
        with open(out, "w") as f:
            f.write(render_html(doc) if args.to == "html" else render_md(doc))
    print(json.dumps({"passed": result["passed"], "file": out,
                      "problems": result["problems"]}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
