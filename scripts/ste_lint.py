#!/usr/bin/env python3
"""STE linter — deterministic ASD-STE100 checks (v1, dictionary deferred).

Usage:
    echo "text" | python3 ste_lint.py [--profile chat|full] [--pretty]

Reads text on stdin, prints a JSON result, exits 1 if any *error* violation.
`passed` is true when there are no error-severity violations (warnings allowed).

The linter is a *gate*, not a rewriter: it verifies STE compliance so the
draft can be revised until it passes. See SKILL.md for the workflow.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ste_dictionary import WORD_SUBSTITUTIONS, PHRASE_SUBSTITUTIONS  # noqa: E402

PROFILES = {
    # STE distinguishes procedures (<=20 words) from descriptions (<=25).
    # "chat" is a pragmatic conversational subset; "full" is document-strict.
    "chat": {"max_sentence_words": 25, "max_paragraph_sentences": 6},
    "full": {"max_sentence_words": 20, "max_paragraph_sentences": 6},
}

BE_VERBS = {"am", "is", "are", "was", "were", "be", "been", "being"}
HAVE_VERBS = {"have", "has", "had"}

# Irregular past participles that do not end in -ed.
IRREGULAR_PARTICIPLES = {
    "gone", "done", "seen", "taken", "given", "written", "broken", "put",
    "set", "cut", "shut", "read", "built", "held", "kept", "left", "found",
    "told", "sent", "spent", "lost", "met", "paid", "said", "laid", "made",
    "shown", "known", "grown", "drawn", "worn", "torn", "chosen", "frozen",
    "driven", "risen", "fallen", "begun", "run", "been", "come", "become",
}

# Adverbs allowed to sit between an auxiliary and its participle/-ing form.
INTERVENING = {"not", "never", "always", "already", "just", "still", "also", "now"}

# Common phrasal verbs (verb + particle) that STE replaces with single verbs.
PHRASAL_VERBS = {
    ("turn", "off"), ("turn", "on"), ("put", "on"), ("take", "off"),
    ("set", "up"), ("shut", "down"), ("back", "up"), ("carry", "out"),
    ("look", "up"), ("fill", "in"), ("pick", "up"), ("hook", "up"),
    ("plug", "in"), ("switch", "off"), ("switch", "on"), ("break", "down"),
    ("check", "out"), ("find", "out"), ("go", "through"), ("hold", "on"),
}

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]*", re.DOTALL)
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")


def _split_blocks(text):
    return [b for b in re.split(r"\n\s*\n", text) if b.strip()]


def _segment_block(block):
    """Yield (kind, text) tuples: prose runs and individual list items.

    List items are separated so a bullet/numbered list is not mistaken for one
    over-long paragraph. Consecutive non-list lines join into one prose chunk.
    """
    prose = []
    for line in block.splitlines():
        m = LIST_RE.match(line)
        if m:
            if prose:
                yield ("prose", " ".join(prose))
                prose = []
            yield ("list", m.group(1))
        elif line.strip():
            prose.append(line.strip())
    if prose:
        yield ("prose", " ".join(prose))


def _split_sentences(chunk):
    return [s.strip() for s in SENTENCE_RE.findall(chunk) if s.strip()]


def _words(sentence):
    return WORD_RE.findall(sentence)


def _is_participle(word):
    w = word.lower()
    return w in IRREGULAR_PARTICIPLES or (len(w) > 3 and w.endswith("ed"))


def _next_content(tokens, i):
    """Index of the next token after i, skipping allowed intervening adverbs."""
    j = i + 1
    while j < len(tokens) and tokens[j].lower() in INTERVENING:
        j += 1
    return j if j < len(tokens) else None


def _make(rule, severity, detail, text):
    return {"rule": rule, "severity": severity, "detail": detail, "text": text}


def _check_sentence(sentence, cfg, violations):
    words = _words(sentence)
    if len(words) > cfg["max_sentence_words"]:
        violations.append(_make(
            "sentence-length", "error",
            f"{len(words)} words (max {cfg['max_sentence_words']})", sentence[:60]))

    lower = [w.lower() for w in words]
    for i, w in enumerate(lower):
        if w in BE_VERBS:
            j = _next_content(lower, i)
            if j is not None:
                nxt = lower[j]
                if nxt.endswith("ing") and len(nxt) > 4:
                    violations.append(_make(
                        "progressive-tense", "error",
                        f"'{w} {nxt}' is a compound tense", sentence[:60]))
                elif _is_participle(nxt):
                    violations.append(_make(
                        "passive-voice", "warning",
                        f"'{w} {nxt}' is passive voice", sentence[:60]))
        if w in HAVE_VERBS:
            j = _next_content(lower, i)
            if j is not None and _is_participle(lower[j]):
                violations.append(_make(
                    "perfect-tense", "error",
                    f"'{w} {lower[j]}' is a perfect tense", sentence[:60]))
        if i + 1 < len(lower) and (w, lower[i + 1]) in PHRASAL_VERBS:
            violations.append(_make(
                "phrasal-verb", "warning",
                f"'{w} {lower[i + 1]}' is a phrasal verb", sentence[:60]))
        if w in WORD_SUBSTITUTIONS:
            violations.append(_make(
                "unapproved-word", "warning",
                f"use '{WORD_SUBSTITUTIONS[w]}' instead of '{w}'", sentence[:60]))

    low = sentence.lower()
    for phrase, sub in PHRASE_SUBSTITUTIONS.items():
        if re.search(r"\b" + re.escape(phrase) + r"\b", low):
            violations.append(_make(
                "unapproved-word", "warning",
                f"use '{sub}' instead of '{phrase}'", sentence[:60]))


def lint(text, profile="chat"):
    cfg = PROFILES.get(profile, PROFILES["chat"])
    violations = []

    if ";" in text:
        violations.append(_make("semicolon", "error",
                                 "semicolons are not allowed; use separate sentences", ";"))

    for block in _split_blocks(text):
        for kind, chunk in _segment_block(block):
            sentences = _split_sentences(chunk)
            # paragraph-length applies to prose only; list items are separate.
            if kind == "prose" and len(sentences) > cfg["max_paragraph_sentences"]:
                violations.append(_make(
                    "paragraph-length", "error",
                    f"{len(sentences)} sentences (max {cfg['max_paragraph_sentences']})",
                    chunk[:60]))
            for sentence in sentences:
                _check_sentence(sentence, cfg, violations)

    passed = not any(v["severity"] == "error" for v in violations)
    return {"passed": passed, "profile": profile, "violations": violations}


def main(argv=None):
    ap = argparse.ArgumentParser(description="STE deterministic linter")
    ap.add_argument("--profile", choices=sorted(PROFILES), default="chat")
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--text", help="lint this string instead of stdin")
    args = ap.parse_args(argv)

    text = args.text if args.text is not None else sys.stdin.read()
    result = lint(text, profile=args.profile)
    print(json.dumps(result, indent=2 if args.pretty else None))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
