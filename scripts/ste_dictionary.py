"""STE substitution dictionary — non-approved term -> approved replacement.

This is a *curated seed set* of well-known Simplified Technical English swaps,
NOT the full copyrighted ~900-word ASD-STE100 dictionary. The linter reads this
file from disk, so it costs no model-context tokens. Extend it freely: add
entries here and the gate picks them up. To approximate the full standard,
paste the official approved words / substitutions into these maps.

Keys are lowercase. WORD_SUBSTITUTIONS are matched per token; PHRASE_
SUBSTITUTIONS are matched as whole-word phrases inside a sentence.
"""

WORD_SUBSTITUTIONS = {
    "commence": "start",
    "initiate": "start",
    "utilize": "use",
    "utilise": "use",
    "terminate": "stop",
    "assist": "help",
    "attempt": "try",
    "obtain": "get",
    "require": "need",
    "sufficient": "enough",
    "additional": "more",
    "approximately": "about",
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
}

PHRASE_SUBSTITUTIONS = {
    "in order to": "to",
    "due to the fact that": "because",
    "in the event that": "if",
    "prior to": "before",
    "subsequent to": "after",
    "a number of": "some",
    "with regard to": "about",
    "in the process of": "during",
}
