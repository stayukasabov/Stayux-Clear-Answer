# Stayux-STE-linter

A fast, deterministic linter for **Simplified Technical English (STE)**, the
terse, unambiguous controlled-English style based on the ASD-STE100 standard.

It ships as two things in one:
1. A **Claude Code skill** that makes an AI assistant write its replies in STE.
2. A **zero-dependency Python linter**: the pass/fail gate the skill writes
   against, plus a curated substitution dictionary.

> **Unofficial.** Not affiliated with or endorsed by ASD. See [NOTICE](NOTICE).
> "Simplified Technical English" and "ASD-STE100" are trademarks of ASD
> (EUTM 017966390). This tool does not include or download ASD's copyrighted
> dictionary.

## Why

Most STE helpers are LLM-only: they load the rule set (and often a dictionary
reference) into the model's context and reason over it every turn. This project
moves the deterministic rules **and the substitution dictionary into Python**.
The model never holds them in context. It calls the linter as a subprocess and
reads back a small pass/fail result. So the rules and the dictionary cost **no
model-context tokens**, and the dictionary can grow toward the full standard
without adding any context cost. The AI layer only handles the judgment rules on
top.

To be precise about what *does* cost tokens: turning the skill on loads
`SKILL.md` once, and each draft-check adds a small lint round-trip. Those are
fixed and small. The part that scales, the rules and the ~900-word-scale
dictionary, stays out of context.

### Token economy (measured)

Counts use the `o200k_base` BPE tokenizer as a proxy for Claude's, which is not
public, so treat them as approximate, not exact.

| Item | Tokens | In model context? |
|---|---:|---|
| `SKILL.md`, loaded on `/ste on` | ~745 | yes (once, sticky) |
| Lint round-trip, clean pass | ~50 | yes (per check) |
| Lint round-trip, many violations | ~270 | yes (per failing check) |
| Rule engine + dictionary + rules reference | ~3,455 | **no** (read by Python) |

The last row is the point: that material never enters the context window. An
LLM-only skill would load and reason over the equivalent every turn.

## What it checks

Deterministic rules (errors fail the gate):
- Sentence length (chat ≤ 25 words, full ≤ 20)
- Paragraph length (≤ 6 sentences; lists parsed separately)
- Semicolons (banned)
- Progressive tense (`is running`) and perfect tense (`has done`)

Advisory (warnings that never fail the gate):
- Passive voice, phrasal verbs
- Unapproved words, with a suggested plain-English swap (curated seed map)
- Words removed from the ASD-STE100 word list (Issue 9)

## As a Claude Code skill

This is the primary use. Copy or symlink this folder into
`~/.claude/skills/ste/`, then toggle it with `/ste on` and `/ste off`. While the
mode is on, the assistant drafts each reply, runs it through the linter as an
objective gate, and rewrites until it passes. See [SKILL.md](SKILL.md).

## The linter directly

The gate reads text on stdin (or `--text`) and prints a JSON result, exiting 1
if any error-severity violation is found:

```bash
echo "Commence the repair prior to the test." | python3 scripts/ste_lint.py --pretty
python3 scripts/ste_lint.py --profile full --text "Your sentence here."
```

Run the tests:

```bash
python3 -m unittest discover -s tests
```

## The dictionary

The linter bundles a small, hand-authored **substitution map**
(`scripts/ste_dictionary.py`). It maps common non-STE words and phrases to plain
replacements, and lists terms removed from the standard. Entries marked
"Issue 9" were checked against the ASD-STE100 Issue 9 dictionary; the rest are
uncontroversial plain-English swaps.

It is **not** the official ~900-word list, which is copyrighted. Extend it two
ways:
- Add your own entries (including company technical terms).
- Point the tool at **your own** official ASD-STE100 copy and paste the approved
  words / substitutions into the maps. The official data is never shipped or
  committed.

## Roadmap

- [ ] Custom / project dictionary loading (merge a user file over the seed)
- [ ] Local official-dictionary parsing (bring your own copy)
- [ ] Noun-cluster rule (needs part-of-speech tagging)

## License

[MIT](LICENSE). See [NOTICE](NOTICE) for trademark and copyright terms.
