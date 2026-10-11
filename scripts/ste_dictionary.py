"""STE substitution dictionary: non-approved term -> approved replacement.

This is a *curated seed set* of well-known Simplified Technical English swaps,
NOT the full copyrighted ~900-word ASD-STE100 dictionary. The linter reads this
file from disk, so it costs no model-context tokens. Extend it freely: add
entries here and the gate picks them up. To approximate the full standard,
paste the official approved words / substitutions into these maps.

Keys are lowercase. WORD_SUBSTITUTIONS are matched per token; PHRASE_
SUBSTITUTIONS and REMOVED_TERMS are matched as whole-word phrases inside a
sentence.

Provenance tags mark where each swap comes from, so the seed is auditable and
legally defensible:
- [Issue 9]       Verified against the ASD-STE100 Issue 9 dictionary using your
                  own bring-your-own copy. The standard's actual replacement.
- [Google style]  From the Google Developer Documentation Style Guide word list
                  (https://developers.google.com/style/word-list), CC BY 4.0.
                  Reusable with attribution.
- [plain-English] Uncontroversial formal/wordy -> plain swaps. Not from any
                  copyrighted source; general style advice.
All swaps are advisory warnings only; they never fail the gate.
"""

WORD_SUBSTITUTIONS = {
    # --- [Issue 9] verified against your BYO official copy ---
    # A key may name its part of speech, "word (pos)". Then the entry applies
    # only to that use of the word (see ste_pos.py). A key without one applies
    # to every use.
    "require (v)": "necessary",      # require (v) -> NECESSARY (adj)
    "substance (n)": "material",     # substance (n) -> MATERIAL (n)
    "acceptable (adj)": "permitted", # acceptable (adj) -> PERMITTED (adj)
    "alternate (adj)": "alternative",  # alternate (adj) -> ALTERNATIVE (adj)
    "avoid (v)": "prevent",          # avoid (v) -> PREVENT (v)
    "ensure (v)": "make sure",       # ensure (v) -> MAKE SURE (v)
    "main (adj)": "primary",         # main (adj) -> PRIMARY (adj)
    "complete (adj)": "completed",   # complete (adj) -> COMPLETED (adj) [verb COMPLETE is approved]
    "activity (n)": "task",          # activity (n) -> TASK (n) / PROCEDURE (n)
    "action (n)": "task",            # action (n) -> STEP (n) / TASK (n)
    "abandon (v)": "go",             # abandon (v) -> GO (v) / STOP (v)
    "assistance (n)": "help",        # assistance (n) -> AID (n) / HELP (v)
    "blank (v)": "seal",             # blank (v) -> SEAL (v)
    "test (v)": "do a test of",      # test (v) -> TEST (n): "Do a test of the software"
    # NOTE: "subsequently" is an APPROVED word in Issue 9. Do not add it here.

    # --- [Google style] Google Developer Documentation Style Guide (CC BY 4.0) ---
    "utilize": "use",
    "utilise": "use",

    # --- [plain-English] uncontroversial formal/wordy -> plain swaps ---
    "commence": "start",
    "initiate": "start",
    "terminate": "stop",
    "assist": "help",
    "attempt": "try",
    "obtain": "get",
    "additional": "more",
    "indicate": "show",
    "demonstrate": "show",
    "purchase": "buy",
    "retain": "keep",
    "numerous": "many",
    "possess": "have",
    "accomplish": "do",
    "endeavor": "try",
    "endeavour": "try",
    "facilitate": "help",
    "regarding": "about",
    "ascertain": "check",
    "commencement": "start",
    "consequently": "so",
    "accordingly": "so",
    "aforementioned": "this",
    "apparent": "clear",
    "cease": "stop",
    "comprehend": "understand",
    "comprise": "include",
    "deem": "think",
    "designate": "name",
    "discontinue": "stop",
    "eliminate": "remove",
    "excessive": "too much",
    "expedite": "speed up",
    "fabricate": "make",
    "finalize": "finish",
    "finalise": "finish",
    "illustrate": "show",
    "locate": "find",
    "modify": "change",
    "notify": "tell",
    "objective": "goal",
    "optimal": "best",
    "provide": "give",
    "rectify": "correct",
    "relocate": "move",
    "undertake": "do",
    "verify": "check",
    "whilst": "while",
    # NOTE: the following are APPROVED words in Issue 9 -> do NOT flag them:
    # approximately, sufficient, equivalent, previous, transmit.
    # And do NOT suggest these banned words as replacements: need, expect, ask, now.
}

# Wordy multiword phrases -> a shorter form. [plain-English], except
# "prior to", which also appears in the Google Developer Documentation Style
# Guide word list (CC BY 4.0).
PHRASE_SUBSTITUTIONS = {
    "due to the fact that": "because",
    "in the event that": "if",
    "prior to": "before",
    "subsequent to": "after",
    "a number of": "some",
    "with regard to": "about",
    "in the process of": "during",
    "as a result of": "because of",
    "at this point in time": "at this time",
    "at the present time": "at this time",
    "for the purpose of": "to",
    "in accordance with": "by",
    "in close proximity to": "near",
    "in conjunction with": "with",
    "in spite of the fact that": "although",
    "on a regular basis": "regularly",
    "the majority of": "most",
}

# Wordiness / "zombie" filler: phrases that add no meaning and should be cut,
# not swapped for a shorter word (that is what PHRASE_SUBSTITUTIONS does). The
# value is the advice: an empty string means "delete it", a non-empty string is
# the shorter form to keep. Seeded from the FOSS prose linters write-good and
# proselint (both openly licensed); this is original curation, not ASD data.
# Advisory warnings only; they never fail the gate.
WORDINESS_PHRASES = {
    "it is important to note that": "",
    "it is worth noting that": "",
    "it should be noted that": "",
    "it is interesting to note that": "",
    "needless to say": "",
    "for all intents and purposes": "",
    "for what it is worth": "",
    "at the end of the day": "",
    "when all is said and done": "",
    "in a very real sense": "",
    "as a matter of fact": "",
    "in the final analysis": "",
    "the fact that": "that",
    "in my opinion": "",
    "please note that": "",
    # [Google style] Not an ASD-STE100 entry. Issue 9 has no "in order to", so
    # it is wordiness advice, not a dictionary finding.
    "in order to": "to",
}

# Terms removed from the ASD-STE100 word list in Issue 9. No approved
# replacement is given, so these are flagged as advisory warnings only.
REMOVED_TERMS = (
    "at least",
    "bear down",
    "blank off",
    "blank out",
    "brightness",
)

# STE does not allow contractions. Keys are lowercase, with a straight
# apostrophe; the linter normalizes curly apostrophes before it matches.
# Possessive forms (for example "valve's") are not contractions and are absent.
CONTRACTIONS = {
    "aren't": "are not",
    "can't": "cannot",
    "couldn't": "could not",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hasn't": "has not",
    "haven't": "have not",
    "he's": "he is",
    "here's": "here is",
    "i'm": "I am",
    "i've": "I have",
    "isn't": "is not",
    "it'll": "it will",
    "it's": "it is",
    "let's": "let us",
    "mustn't": "must not",
    "she's": "she is",
    "shouldn't": "should not",
    "that's": "that is",
    "there's": "there is",
    "they'll": "they will",
    "they're": "they are",
    "wasn't": "was not",
    "we'll": "we will",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what's": "what is",
    "who's": "who is",
    "won't": "will not",
    "wouldn't": "would not",
    "you'll": "you will",
    "you're": "you are",
    "you've": "you have",
}

# Parts of speech that Issue 9 approves for words that also have an entry
# above. When the tagger cannot decide the part of speech of such a word, the
# linter stays silent. [Issue 9]
APPROVED_POS = {
    "test": ["n"],
    "complete": ["v"],
}

# Chat filler at the start or the end of a reply. [plain-English] original
# curation, based on the Microsoft Style Guide "Top 10 tips" ("Get to the point
# fast", "Prune every excess word"). Used by the chat profile only. Advisory
# warnings only; they never fail the gate.
# Openers match only at the start of the first sentence.
FILLER_OPENERS = (
    "great question",
    "good question",
    "sure",
    "certainly",
    "absolutely",
    "of course",
    "happy to help",
    "i'd be happy to",
    "you asked about",
    "to answer your question",
)

# Closers match anywhere in the last sentence.
FILLER_CLOSERS = (
    "i hope this helps",
    "hope this helps",
    "let me know if",
    "feel free to",
    "happy to help",
    "don't hesitate to",
    "hope that helps",
    "any other questions",
    "good luck",
    "happy coding",
)
