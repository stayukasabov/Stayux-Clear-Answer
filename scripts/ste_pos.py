#!/usr/bin/env python3
"""Rule-based part-of-speech tagger for the STE linter. No dependencies.

ASD-STE100 approves each word for one part of speech: TEST (n) is approved,
test (v) is not. This tagger decides the part of speech of an open-class word
only when the context makes it clear. Otherwise it returns None, and the
linter falls back to its part-of-speech-free behaviour.

Tags: "n" (noun), "v" (verb), "adj" (adjective, also a noun used as a
modifier), "adv" (adverb), or None (unknown).
"""
import re

DETERMINERS = {
    "the", "a", "an", "this", "that", "these", "those", "each", "every", "all",
    "any", "some", "no", "another", "other", "which", "whose", "my", "your",
    "our", "their", "its", "his", "her",
}
PREPOSITIONS = {
    "of", "in", "on", "at", "by", "with", "from", "for", "into", "onto", "about",
    "between", "through", "during", "before", "after", "under", "over",
    "without", "against", "along", "across", "behind", "near", "than", "via",
    "per", "inside", "outside", "below", "above", "around", "until",
}
MODALS = {
    "must", "can", "could", "will", "would", "shall", "should", "may", "might",
    "do", "does", "did", "cannot",
}
SUBJECT_PRONOUNS = {"i", "you", "we", "they", "he", "she"}
OBJECT_STARTERS = DETERMINERS | {"it", "them"}
OTHER_CLOSED = {
    "and", "or", "but", "if", "when", "then", "so", "not", "to", "it", "them",
    "me", "us", "him", "is", "are", "was", "were", "be", "been", "being", "am",
    "has", "have", "had", "there", "here", "also", "only", "as", "because",
    "while", "where", "how", "what", "who", "why",
}
CLOSED = DETERMINERS | PREPOSITIONS | MODALS | SUBJECT_PRONOUNS | OTHER_CLOSED
# Adverbs that may sit between a modal and its verb ("do not test").
SKIPPABLE = {"not", "also", "always", "never", "only", "then", "first"}

POS_TAGS = r"n|v|adj|adv|pron|prep|conj|art|abbr|TN|IV"
KEY_RE = re.compile(rf"^(.*?)\s*\(({POS_TAGS})\)\s*$")


def split_key(key):
    """Split a dictionary key such as "file (v)" into ("file", "v")."""
    m = KEY_RE.match(key)
    return (m.group(1).strip(), m.group(2)) if m else (key.strip(), None)


def _is_open(word):
    return word not in CLOSED and not word.endswith("'s")


def _starts_noun_phrase(word):
    return word in DETERMINERS or word in PREPOSITIONS or word.endswith("'s")


def _previous(words, i):
    """The nearest earlier word that is not a skippable adverb."""
    j = i - 1
    while j >= 0 and words[j] in SKIPPABLE:
        j -= 1
    return words[j] if j >= 0 else None


def tag(tokens):
    """Return one tag (or None) for each token of a sentence."""
    words = [t.lower() for t in tokens]
    tags = [None] * len(words)
    in_noun_phrase = False
    for i, w in enumerate(words):
        if not _is_open(w):
            in_noun_phrase = _starts_noun_phrase(w)
            continue
        nxt = words[i + 1] if i + 1 < len(words) else None
        prev = _previous(words, i)
        if len(w) > 3 and w.endswith("ly"):
            tags[i] = "adv"
            in_noun_phrase = False
        elif prev in MODALS or prev == "to" or prev in SUBJECT_PRONOUNS:
            tags[i] = "v"
            in_noun_phrase = False
        elif (i == 0 or (i == 1 and tags[0] == "adv")) and nxt in OBJECT_STARTERS:
            tags[i] = "v"  # imperative: "Test the software."
            in_noun_phrase = False
        elif in_noun_phrase:
            if nxt is not None and _is_open(nxt) and not nxt.endswith("ly"):
                tags[i] = "adj"
            else:
                tags[i] = "n"
                in_noun_phrase = False
    return tags
