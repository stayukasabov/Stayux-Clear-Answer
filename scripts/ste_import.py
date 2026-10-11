#!/usr/bin/env python3
"""Import a *local* ASD-STE100 copy into a git-ignored cache.

The official dictionary is copyrighted (all rights reserved) and is never
committed or downloaded. A user who has their own copy runs this once:

    python3 ste_import.py my-ste.pdf        # writes cache/official.json
    python3 ste_import.py my-ste.txt        # already-extracted text

`ste_lint.py` loads cache/official.json if it is present. The cache stays on
the user's machine; `.gitignore` covers `cache/` and `*.official.*`.

Parsing targets `pdftotext -layout` output. In that layout each dictionary
entry starts a line with its headword and part of speech:
    WORD (pos)   -> an APPROVED word
    word (pos)   -> a NOT-approved word, usually followed on the same line by
                    its UPPERCASE approved alternative(s).
"""
import argparse
import json
import os
import re
import subprocess
import sys

POS = r"(?:n|v|adj|adv|pron|prep|conj|art|abbr|TN|IV)"
_HEAD = re.compile(rf"^\s*([A-Za-z][A-Za-z\-]*)\s+\(({POS})\)")
# An approved alternative is 1-3 UPPERCASE words joined by single spaces (so
# "MAKE SURE" stays whole) that sit immediately before a part-of-speech tag.
# The single-space join stops it from bridging the wide column gaps that
# pdftotext -layout leaves between the alternative and the example text.
_ALT = re.compile(rf"([A-Z][A-Z\-]*(?:\s[A-Z][A-Z\-]*){{0,2}})\s*\({POS}\)")
# Words that continue an alternative after its tag, joined by single spaces:
# "ONE (TN) MORE", "TWO (TN) … NOT". The STE example column usually starts
# after a wider gap. pdftotext can join the two with one space ("ONE (TN) OF
# THE TWO IF THERE IS ..."), so take at most 3 words.
_ALT_TAIL = re.compile(r"(?: (?:…|[A-Z][A-Z\-]*)){1,3}")


# Lines that follow an entry, where more approved alternatives can start.
_LOOKAHEAD = 25


def _entry_rank(after):
    """Rank the text after an alternative. 2: a dictionary entry, with an
    UPPERCASE STE example. 1: nothing after it, as in a summary table. 0: not
    an entry, as in a change-log line ("removed from ...") or a comma list."""
    rest = after.strip()
    if not rest:
        return 1
    return 2 if rest[0].isupper() or rest[0] in "(…0123456789" else 0


_SEGMENT = re.compile(r"(?:^|(?<=\s\s))\S")


def _example_column(lines, start, alt_column):
    """The column where the STE example text starts, from the first line after
    an entry that has text right of the alternatives column, or None."""
    for line in lines[start + 1:start + 1 + _LOOKAHEAD]:
        if line[:alt_column].strip():
            return None  # the next headword: the entry has one line only
        for m in _SEGMENT.finditer(line):
            if m.start() > alt_column + 2:
                return m.start()
    return None


def _alternative(text, alt, limit=None):
    """The alternative of a match, with any words that continue it. limit is
    the index in text where the example column starts."""
    words = alt.group(1)
    tail = _ALT_TAIL.match(text, alt.end())
    if tail:
        for token in re.finditer(r" (…|[A-Z][A-Z\-]*)", tail.group(0)):
            if limit is not None and alt.end() + token.end() > limit:
                break
            words += token.group(0)
    return words.lower()


def _more_alternatives(lines, start, column, limit=None):
    """Approved alternatives that start in the same column on the lines after
    an entry, up to the next headword."""
    found = []
    for line in lines[start + 1:start + 1 + _LOOKAHEAD]:
        if line[:column].strip():
            if _HEAD.match(line):
                break  # the next headword, at the left margin
            continue
        text = line[column:]
        alt = _ALT.match(text)
        if alt:
            name = _alternative(text, alt, None if limit is None else limit - column)
            tail = alt.end() + len(name) - len(alt.group(1))
            if _entry_rank(text[tail:]):
                found.append(name)
    return found


def parse_official(text):
    """Parse pdftotext -layout output into a version 2 cache.

    Each entry keeps its part of speech: approved words map to their approved
    parts of speech, and substitution keys have the form "word (pos)". When an
    entry has several approved alternatives, the value joins them with "|".
    A dictionary entry with an STE example wins over a summary-table line.
    Change-log lines are not entries.
    """
    approved = {}
    word_subs = {}
    ranks = {}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = _HEAD.match(line)
        if not m:
            continue
        head, pos = m.group(1), m.group(2)
        if head.isupper():
            tags = approved.setdefault(head.lower(), [])
            if pos not in tags:
                tags.append(pos)
            continue
        if not head.islower():
            continue
        rest = line[m.end():]
        alt = _ALT.search(rest)
        if not alt or rest[:alt.start()].strip():
            continue
        alt_column = m.end() + alt.start()
        limit = _example_column(lines, i, alt_column)
        name = _alternative(rest, alt, None if limit is None else limit - m.end())
        rank = _entry_rank(rest[alt.end() + len(name) - len(alt.group(1)):])
        key = f"{head} ({pos})"
        if rank == 0 or rank <= ranks.get(key, 0):
            continue
        alts = [name]
        alts += _more_alternatives(lines, i, alt_column, limit)
        word_subs[key] = "|".join(dict.fromkeys(alts))
        ranks[key] = rank
    return {
        "version": 2,
        "approved": {w: approved[w] for w in sorted(approved)},
        "word_substitutions": word_subs,
        "phrase_substitutions": {},
    }


def write_cache(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def _read_source(src):
    """Return text from a .txt directly, or a .pdf via pdftotext."""
    if src.lower().endswith(".pdf"):
        try:
            out = subprocess.run(
                ["pdftotext", "-layout", src, "-"],
                check=True, capture_output=True, text=True)
        except FileNotFoundError:
            raise SystemExit("pdftotext not found; install poppler or pass a .txt")
        return out.stdout
    with open(src) as f:
        return f.read()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Import a local STE dictionary")
    ap.add_argument("source", help="path to your local .pdf or extracted .txt")
    ap.add_argument("--out", default=os.path.join("cache", "official.json"),
                    help="cache path (default cache/official.json)")
    args = ap.parse_args(argv)

    data = parse_official(_read_source(args.source))
    write_cache(args.out, data)
    n = len(data["word_substitutions"])
    a = len(data["approved"])
    print(f"wrote {args.out}: {a} approved words, {n} substitutions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
