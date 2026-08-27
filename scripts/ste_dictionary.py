"""STE substitution dictionary — non-approved term -> approved replacement.

This is a *curated seed set* of well-known Simplified Technical English swaps,
NOT the full copyrighted ~900-word ASD-STE100 dictionary. The linter reads this
file from disk, so it costs no model-context tokens. Extend it freely: add
entries here and the gate picks them up. To approximate the full standard,
paste the official approved words / substitutions into these maps.

Keys are lowercase. WORD_SUBSTITUTIONS are matched per token; PHRASE_
SUBSTITUTIONS and REMOVED_TERMS are matched as whole-word phrases inside a
sentence. Entries marked "Issue 9" were checked against the ASD-STE100 Issue 9
dictionary; all others are common, uncontroversial plain-English swaps.
"""

WORD_SUBSTITUTIONS = {
    # --- Original seed set ---
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

    # --- Verified against ASD-STE100 Issue 9 ---
    "substance": "material",     # substance (n) -> MATERIAL (n)
    "acceptable": "permitted",   # acceptable (adj) -> PERMITTED (adj)
    "alternate": "alternative",  # alternate (adj) -> ALTERNATIVE (adj)
    "avoid": "prevent",          # avoid (v) -> PREVENT (v)
    "ensure": "make sure",       # ensure (v) -> MAKE SURE (v)
    "main": "primary",           # main (adj) -> PRIMARY (adj)
    "complete": "completed",     # complete (adj) -> COMPLETED (adj) [verb COMPLETE is approved]
    "activity": "task",          # activity (n) -> TASK (n) / PROCEDURE (n)
    "action": "task",            # action (n) -> STEP (n) / TASK (n)
    "abandon": "go",             # abandon (v) -> GO (v) / STOP (v)
    "assistance": "help",        # assistance (n) -> AID (n) / HELP (v)
    "blank": "seal",             # blank (v) -> SEAL (v)
    # NOTE: "subsequently" is an APPROVED word in Issue 9 — do not add it here.
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

# Terms removed from the ASD-STE100 word list in Issue 9. No approved
# replacement is given, so these are flagged as advisory warnings only.
REMOVED_TERMS = (
    "at least",
    "bear down",
    "blank off",
    "blank out",
    "brightness",
)
