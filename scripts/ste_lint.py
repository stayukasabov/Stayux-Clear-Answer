#!/usr/bin/env python3
"""STE linter: deterministic ASD-STE100 checks (v1, dictionary deferred).

Usage:
    echo "text" | python3 ste_lint.py [--profile chat|full] [--pretty | --brief]

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
from ste_dictionary import (  # noqa: E402
    WORD_SUBSTITUTIONS, PHRASE_SUBSTITUTIONS, WORDINESS_PHRASES, REMOVED_TERMS,
    CONTRACTIONS, FILLER_OPENERS, FILLER_CLOSERS, APPROVED_POS,
)
import ste_pos  # noqa: E402

# Optional local cache built from the user's own official copy (never shipped).
# See ste_import.py. Read from disk, so it costs no model-context tokens.
DEFAULT_CACHE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, "cache", "official.json")


def load_cache(path=DEFAULT_CACHE_PATH):
    """Return the parsed official cache, or None if it is absent/unreadable."""
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


_DEFAULT_CACHE = load_cache()

# Optional per-project word list. A plain, hand-authored file that adds company
# terms and swaps on top of the seed and the official cache. See parse_custom_dict.
DEFAULT_CUSTOM_PATH = os.path.join(os.getcwd(), ".ste-dict.txt")


def parse_custom_dict(text):
    """Parse a `.ste-dict.txt` word list into approved words and substitutions.

    - `term = replacement` -> a substitution (word, or phrase if multiword).
      A word may name its part of speech: `file (v) = remove`.
    - a bare `word` (optional leading `+`) -> an approved word, never flagged.
      `word (pos)` approves only that part of speech.
    - `#` starts a comment (whole-line or inline); blank lines are ignored.
    Keys are lowercased.
    """
    approved = set()
    words = {}
    phrases = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if "=" in line:
            term, _, repl = line.partition("=")
            term, repl = term.strip().lower(), repl.strip()
            if not term or not repl:
                continue
            word, _ = ste_pos.split_key(term)
            (phrases if " " in word else words)[term] = repl
        else:
            approved.add(line.lstrip("+").strip().lower())
    return {"approved": sorted(approved),
            "word_substitutions": words, "phrase_substitutions": phrases}


def load_custom_dict(path=DEFAULT_CUSTOM_PATH):
    """Return the parsed custom dictionary, or None if it is absent/unreadable."""
    try:
        with open(path) as f:
            return parse_custom_dict(f.read())
    except OSError:
        return None


_DEFAULT_CUSTOM = load_custom_dict()


# Part-of-speech key for an entry from a version 1 cache, which has no part of
# speech: it applies to every use except a noun or a noun modifier.
LEGACY_POS = "legacy"
POS_NAMES = {"n": "a noun", "v": "a verb", "adj": "an adjective", "adv": "an adverb",
             "prep": "a preposition", "pron": "a pronoun", "conj": "a conjunction",
             "art": "an article", "abbr": "an abbreviation", "TN": "a technical noun",
             "IV": "a technical verb"}


def _add_entries(words, subs, legacy=False, overrides=False):
    """Add entries. With overrides, a word's entries from an earlier layer give
    way: a new entry replaces an earlier one for every use."""
    for key, repl in subs.items():
        word, pos = ste_pos.split_key(key.lower())
        pos = LEGACY_POS if legacy else pos
        entries = words.setdefault(word, {})
        if repl.lower() == word:
            # "test (v)" -> "TEST (n)": the word is approved only in another
            # part of speech. Keep earlier advice; else say it is not approved.
            if pos not in entries and None not in entries:
                entries[pos] = ""
            continue
        if overrides:
            entries.pop(None, None)
        entries[pos] = repl


def _approvals(layer):
    """Yield (word, pos) approvals. pos None approves every use."""
    approved = layer.get("approved", ())
    if isinstance(approved, dict):  # version 2 cache: {word: [pos, ...]}
        for word, tags in approved.items():
            for pos in tags or [None]:
                yield word, pos
    else:
        for key in approved:
            yield ste_pos.split_key(key.lower())


def _effective_maps(cache, custom=None):
    """Merge the seed with the official cache and the custom list, in that order
    of precedence (custom wins).

    Returns (words, phrases, approved_pos). words maps a word to
    {pos: replacement}, where pos None means every use. An approval removes the
    entry for its part of speech, or every entry if it names none.
    """
    words = {}
    _add_entries(words, WORD_SUBSTITUTIONS)
    phrases = dict(PHRASE_SUBSTITUTIONS)
    approved_pos = {w: set(p) for w, p in APPROVED_POS.items()}
    for layer in (cache, custom):
        if not layer:
            continue
        legacy = layer is cache and "version" not in layer
        _add_entries(words, layer.get("word_substitutions", {}), legacy, overrides=True)
        phrases.update(layer.get("phrase_substitutions", {}))
        for word, pos in _approvals(layer):
            entries = words.get(word, {})
            if pos is None:
                words.pop(word, None)
            else:
                entries.pop(pos, None)
                approved_pos.setdefault(word, set()).add(pos)
                if not entries:
                    words.pop(word, None)
    return words, phrases, approved_pos


def _advice(word, pos, repl):
    # An imported entry can list several alternatives, joined with "|".
    options = " or ".join(f"'{r}'" for r in repl.split("|") if r and r != word) if repl else ""
    if pos is None or pos == LEGACY_POS:
        return f"use {options} instead of '{word}'" if options else f"'{word}' is not approved"
    name = POS_NAMES.get(pos, pos)
    return f"'{word}' as {name}: use {options}" if options else f"'{word}' as {name} is not approved"


def _word_advice(word, tag, entries, approved_pos):
    """Return the unapproved-word detail for one use of a word, or None."""
    if tag is not None:
        if tag in entries:
            return _advice(word, tag, entries[tag])
        if None in entries:
            return _advice(word, None, entries[None])
        if LEGACY_POS in entries and tag not in ("n", "adj"):
            return _advice(word, LEGACY_POS, entries[LEGACY_POS])
        return None
    # Unknown part of speech: warn as before, unless the word is approved for
    # another part of speech.
    if None in entries:
        return _advice(word, None, entries[None])
    if approved_pos.get(word):
        return None
    if LEGACY_POS in entries:
        return _advice(word, LEGACY_POS, entries[LEGACY_POS])
    pos = next((p for p in ("v", "adj", "adv", "n") if p in entries), next(iter(entries)))
    return _advice(word, pos, entries[pos])

PROFILES = {
    # STE distinguishes procedures (<=20 words) from descriptions (<=25).
    # "chat" is a pragmatic conversational subset; "full" is document-strict.
    # format_rules: chat-only style warnings (see _check_format).
    "chat": {"max_sentence_words": 25, "max_paragraph_sentences": 6, "format_rules": True},
    "full": {"max_sentence_words": 20, "max_paragraph_sentences": 6, "format_rules": False},
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


# Common technical imperative verbs. Used only to detect two instructions
# joined by "and"/"then" in one sentence (the one-instruction rule).
ACTION_VERBS = {
    "open", "close", "remove", "install", "set", "turn", "push", "pull",
    "connect", "disconnect", "check", "do", "make", "start", "stop", "apply",
    "tighten", "loosen", "examine", "replace", "put", "get", "hold", "release",
    "press", "lift", "lower", "attach", "detach", "clean", "measure", "adjust",
    "align", "fill", "drain", "add", "keep", "move", "read", "record", "send",
    "wait", "test", "use", "give", "cut", "seal", "go", "find", "select",
}

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")
# A sentence ends at ., !, or ? followed by white space or the end of the text,
# so "example.com", ".com", and "1.1.1.1" stay inside their sentence.
SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
TABLE_RE = re.compile(r"^\s*\|")
TABLE_SEP_RE = re.compile(r"^[\s|:\-]+$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def _closes(line, fence):
    """True if the line closes the fence: the same mark, at least as long."""
    mark = line.strip()
    return bool(mark) and set(mark) == {fence[0]} and len(mark) >= len(fence)
BOLD_RE = re.compile(r"\*\*[^*\n]+\*\*|__[^_\n]+__")
HEADER_RE = re.compile(r"^#{1,6}\s", re.MULTILINE)
BULLET_RE = re.compile(r"^\s*[-*+]\s+")

# Chat format limits. Sources: behaviours-kit/Research/2026-10-10-chat-format-rule-sources.md
MAX_BOLD_SPANS = 2          # GOV.UK and Google: use bold sparingly. The limit of 2 is our own number.
MIN_WORDS_FOR_HEADER = 150  # Microsoft Style Guide: use headings judiciously. 150 is our own number.
MAX_BULLETS = 7             # Microsoft Style Guide: 2 to 7 items. Google: no 1-item lists.
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
# An HTML tag in markdown, such as <a href="..." target="_blank">. Only the text
# between tags is prose; the tag and its attributes are not.
HTML_TAG_RE = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>\n]*)?/?>")
QUOTE_RE = re.compile(r"^\s*(?:>\s?)+")


def _unclosed_fence(text):
    """Return the line number of a code fence that never closes, or None."""
    fence, start = None, None
    for n, line in enumerate(text.split("\n"), 1):
        if fence:
            if _closes(line, fence):
                fence = None
        else:
            m = FENCE_RE.match(line)
            if m:
                fence, start = m.group(1), n
    return start if fence else None


def _strip_code(text):
    """Remove code so the prose rules do not apply to it.

    A fenced block becomes empty lines, so line numbers do not move. An inline
    code span becomes the word "code", so the sentence keeps its shape.
    """
    out, fence = [], None
    for line in text.split("\n"):
        m = FENCE_RE.match(line)
        if fence:
            if _closes(line, fence):
                fence = None
            out.append("")
        elif m:
            fence = m.group(1)
            out.append("")
        else:
            # A quote marker is not text: "> - item" is a list item, and ">"
            # alone is a blank line that ends a paragraph.
            line = QUOTE_RE.sub("", line)
            out.append(HTML_TAG_RE.sub(" ", INLINE_CODE_RE.sub("code", line)))
    return "\n".join(out)


def _iter_segments(text):
    """Yield (kind, chunk, line_no) for prose runs and individual list items.

    line_no is the 1-based line where the segment starts. Blank lines split
    blocks. List items are separated so a bullet/numbered list is not mistaken
    for one over-long paragraph. Each table cell is yielded as a list item, and
    separator rows are skipped. Consecutive other lines join into a prose
    chunk that keeps the first line's number.
    """
    lines = text.split("\n")
    i, n = 0, len(lines)
    while i < n:
        if not lines[i].strip():
            i += 1
            continue
        prose, prose_line = [], None
        while i < n and lines[i].strip():
            m = LIST_RE.match(lines[i])
            if TABLE_RE.match(lines[i]):
                # Each table cell is its own item, like a list item.
                if prose:
                    yield ("prose", " ".join(prose), prose_line)
                    prose, prose_line = [], None
                if not TABLE_SEP_RE.match(lines[i]):
                    for cell in lines[i].strip().strip("|").split("|"):
                        if cell.strip():
                            yield ("list", cell.strip(), i + 1)
            elif m:
                if prose:
                    yield ("prose", " ".join(prose), prose_line)
                    prose, prose_line = [], None
                yield ("list", m.group(1), i + 1)
            else:
                if prose_line is None:
                    prose_line = i + 1
                prose.append(lines[i].strip())
            i += 1
        if prose:
            yield ("prose", " ".join(prose), prose_line)


def _split_sentences(chunk):
    return [s.strip() for s in SENTENCE_END_RE.split(chunk) if s.strip()]


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


def _make(rule, severity, detail, text, line=None):
    return {"rule": rule, "severity": severity, "detail": detail,
            "text": text, "line": line}


def _check_sentence(sentence, cfg, violations, line,
                    word_subs=None, phrase_subs=PHRASE_SUBSTITUTIONS, approved_pos=None):
    if word_subs is None:
        word_subs, _, approved_pos = _effective_maps(None)
    approved_pos = approved_pos or {}
    words = _words(sentence)
    # Tag each clause on its own: a comma, semicolon, or colon ends a noun
    # phrase, and an instruction can start after it ("If ..., check the value").
    tags = [t for clause in re.split(r"[,;:]", sentence) for t in ste_pos.tag(_words(clause))]
    if len(words) > cfg["max_sentence_words"]:
        violations.append(_make(
            "sentence-length", "error",
            f"{len(words)} words (max {cfg['max_sentence_words']})", sentence[:60], line))

    lower = [w.lower() for w in words]
    for i, w in enumerate(lower):
        if w in BE_VERBS:
            j = _next_content(lower, i)
            if j is not None:
                nxt = lower[j]
                if nxt.endswith("ing") and len(nxt) > 4:
                    violations.append(_make(
                        "progressive-tense", "error",
                        f"'{w} {nxt}' is a compound tense", sentence[:60], line))
                elif _is_participle(nxt):
                    violations.append(_make(
                        "passive-voice", "warning",
                        f"'{w} {nxt}' is passive voice", sentence[:60], line))
        if w in HAVE_VERBS:
            j = _next_content(lower, i)
            if j is not None and _is_participle(lower[j]):
                violations.append(_make(
                    "perfect-tense", "error",
                    f"'{w} {lower[j]}' is a perfect tense", sentence[:60], line))
        if i + 1 < len(lower) and (w, lower[i + 1]) in PHRASAL_VERBS:
            violations.append(_make(
                "phrasal-verb", "warning",
                f"'{w} {lower[i + 1]}' is a phrasal verb", sentence[:60], line))
        if w in word_subs:
            advice = _word_advice(w, tags[i], word_subs[w], approved_pos)
            if advice:
                violations.append(_make("unapproved-word", "warning", advice,
                                        sentence[:60], line))
        if w in CONTRACTIONS:
            violations.append(_make(
                "contraction", "error",
                f"use '{CONTRACTIONS[w]}' instead of '{w}'", sentence[:60], line))

    # One instruction per sentence: flag an imperative sentence that joins a
    # second action verb with "and" or "then" (for example "Open X and close Y").
    if lower and lower[0] in ACTION_VERBS:
        for i, w in enumerate(lower):
            if w in ("and", "then"):
                j = i + 1
                while j < len(lower) and lower[j] in ("the", "a", "an", "then"):
                    j += 1
                if j < len(lower) and lower[j] in ACTION_VERBS:
                    violations.append(_make(
                        "one-instruction", "warning",
                        "one instruction per sentence: split the joined steps",
                        sentence[:60], line))
                    break

    low = sentence.lower()
    for phrase, sub in phrase_subs.items():
        if re.search(r"\b" + re.escape(phrase) + r"\b", low):
            violations.append(_make(
                "unapproved-word", "warning",
                f"use '{sub}' instead of '{phrase}'", sentence[:60], line))
    for phrase, sub in WORDINESS_PHRASES.items():
        if re.search(r"\b" + re.escape(phrase) + r"\b", low):
            advice = (f"remove '{phrase}'; it adds no meaning" if not sub
                      else f"'{phrase}' is wordy: use '{sub}'")
            violations.append(_make("wordiness", "warning", advice, sentence[:60], line))
    for term in REMOVED_TERMS:
        if re.search(r"\b" + re.escape(term) + r"\b", low):
            violations.append(_make(
                "removed-word", "warning",
                f"'{term}' was removed from the ASD-STE100 word list", sentence[:60], line))


def _line_of(text, pos):
    return text[:pos].count("\n") + 1


def _starts_with_phrase(sentence, phrases):
    low = sentence.lower().lstrip()
    return next((p for p in phrases
                 if re.match(re.escape(p) + r"\b", low)), None)


def _check_format(text, violations):
    """Chat-only format warnings for a whole reply. Text is already code-free."""
    bold = list(BOLD_RE.finditer(text))
    if len(bold) > MAX_BOLD_SPANS:
        violations.append(_make(
            "bold-overuse", "warning",
            f"{len(bold)} bold spans (max {MAX_BOLD_SPANS}); use bold sparingly",
            bold[0].group(0)[:60], _line_of(text, bold[0].start())))

    header = HEADER_RE.search(text)
    word_count = len(WORD_RE.findall(text))
    # A text that starts with a level-1 title is a document, not a chat reply.
    is_document = text.lstrip().startswith("# ")
    if header and word_count < MIN_WORDS_FOR_HEADER and not is_document:
        violations.append(_make(
            "header-in-short-reply", "warning",
            f"header in a reply of {word_count} words (min {MIN_WORDS_FOR_HEADER})",
            text[header.start():header.start() + 60].split("\n")[0],
            _line_of(text, header.start())))

    # A bullet list is a run of bullet lines. Blank lines do not end it.
    lists, current = [], []
    for i, line in enumerate(text.split("\n"), 1):
        if BULLET_RE.match(line):
            current.append(i)
        elif line.strip() and current:
            lists.append(current)
            current = []
    if current:
        lists.append(current)
    for items in lists:
        if len(items) == 1 or len(items) > MAX_BULLETS:
            violations.append(_make(
                "bullet-overuse", "warning",
                f"bullet list of {len(items)} items (use 2 to {MAX_BULLETS})",
                "", items[0]))

    segments = list(_iter_segments(text))
    if not segments:
        return
    first = _split_sentences(segments[0][1])
    if first:
        phrase = _starts_with_phrase(first[0], FILLER_OPENERS)
        if phrase:
            violations.append(_make(
                "filler-opener", "warning",
                f"remove '{phrase}'; start with the answer", first[0][:60], segments[0][2]))
    last = _split_sentences(segments[-1][1])
    if last:
        low = last[-1].lower()
        phrase = next((p for p in FILLER_CLOSERS
                       if re.search(r"\b" + re.escape(p) + r"\b", low)), None)
        if phrase:
            violations.append(_make(
                "filler-closer", "warning",
                f"remove '{phrase}'; end with the last fact", last[-1][:60], segments[-1][2]))


def lint(text, profile="chat", cache=None, custom=None):
    cfg = PROFILES.get(profile, PROFILES["chat"])
    if cache is None:
        cache = _DEFAULT_CACHE
    if custom is None:
        custom = _DEFAULT_CUSTOM
    word_subs, phrase_subs, approved_pos = _effective_maps(cache, custom)
    violations = []

    # Normalize curly apostrophes so contractions match regardless of source.
    text = text.replace("’", "'")
    open_line = _unclosed_fence(text)
    if open_line:
        # The rest of the text would be skipped as code, unchecked.
        violations.append(_make(
            "unclosed-code-fence", "error",
            "this code fence never closes, so the text after it is not checked",
            text.split("\n")[open_line - 1].strip()[:60], open_line))
    text = _strip_code(text)

    body = []
    if ";" in text:
        semi_line = text[:text.index(";")].count("\n") + 1
        body.append(_make("semicolon", "error",
                          "semicolons are not allowed; use separate sentences",
                          ";", semi_line))

    for kind, chunk, line in _iter_segments(text):
        sentences = _split_sentences(chunk)
        # paragraph-length applies to prose only; list items are separate.
        if kind == "prose" and len(sentences) > cfg["max_paragraph_sentences"]:
            body.append(_make(
                "paragraph-length", "error",
                f"{len(sentences)} sentences (max {cfg['max_paragraph_sentences']})",
                chunk[:60], line))
        for sentence in sentences:
            _check_sentence(sentence, cfg, body, line, word_subs, phrase_subs, approved_pos)

    if cfg["format_rules"]:
        _check_format(text, body)
    violations += body

    passed = not any(v["severity"] == "error" for v in violations)
    return {"passed": passed, "profile": profile, "violations": violations}


def main(argv=None):
    ap = argparse.ArgumentParser(description="STE deterministic linter")
    ap.add_argument("--profile", choices=sorted(PROFILES), default="chat")
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--brief", action="store_true",
                    help="print PASS, or FAIL and one line for each error (no warnings)")
    ap.add_argument("--text", help="lint this string instead of stdin")
    args = ap.parse_args(argv)

    text = args.text if args.text is not None else sys.stdin.read()
    result = lint(text, profile=args.profile)
    if args.brief:
        # The short form for the gate: only what Claude must fix, few tokens.
        print("PASS" if result["passed"] else "FAIL")
        for v in result["violations"]:
            if v["severity"] == "error":
                print(f"{v['line']} {v['rule']} {v['detail']} | {v['text']}")
    else:
        print(json.dumps(result, indent=2 if args.pretty else None))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
