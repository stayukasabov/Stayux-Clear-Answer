# Stayux-STE-linter

A fast, deterministic linter for **Simplified Technical English (STE)** — the
terse, unambiguous controlled-English style based on the ASD-STE100 standard.

It ships as two things in one:
1. A **Claude Code skill** — makes an AI assistant write its replies in STE.
2. A **zero-dependency Python linter** — the pass/fail gate the skill writes
   against, plus a curated substitution dictionary.

> **Unofficial.** Not affiliated with or endorsed by ASD. See [NOTICE](NOTICE).
> "Simplified Technical English" and "ASD-STE100" are trademarks of ASD
> (EUTM 017966390). This tool does not include or download ASD's copyrighted
> dictionary.

## Why

Most STE helpers are LLM-only: they load the rules into context and rely on the
model's judgment every turn. This project puts the deterministic rules in
**Python**, so the checks are exact, testable, offline, and cost **no
model-context tokens** — the model calls the linter instead of reasoning about
rules. That token economy is the whole point: the AI layer only handles the
judgment rules on top.

## What it checks

Deterministic rules (errors fail the gate):
- Sentence length (chat ≤ 25 words, full ≤ 20)
- Paragraph length (≤ 6 sentences; lists parsed separately)
- Semicolons (banned)
- Progressive tense (`is running`) and perfect tense (`has done`)

Advisory (warnings — never fail the gate):
- Passive voice, phrasal verbs
- Unapproved words → suggested plain-English swap (curated seed map)
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
(`scripts/ste_dictionary.py`) — common non-STE words and phrases mapped to plain
replacements, plus a list of terms removed from the standard. Entries marked
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
