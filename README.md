# STAYUX-STE-LINTER

A fast, deterministic linter for **Simplified Technical English (STE)** — the
terse, unambiguous controlled-English style based on the ASD-STE100 standard.

It ships as three things in one:
1. A **Python linter** — a zero-dependency pass/fail gate for STE rules.
2. A **Claude Code skill** — makes an AI assistant write replies in STE.
3. (Roadmap) a **CLI + pre-commit hook** for documents and repos.

> **Unofficial.** Not affiliated with or endorsed by ASD. See [NOTICE](NOTICE).
> "Simplified Technical English" and "ASD-STE100" are trademarks of ASD
> (EUTM 017966390). This tool does not include or download ASD's copyrighted
> dictionary.

## Why

Most STE helpers are LLM-only: they load rules into context and rely on the
model's judgment. This project puts the deterministic rules in **Python**, so
checks are exact, testable, offline, and cost no model-context tokens. The AI
layer only handles the judgment rules on top.

## What it checks (v1)

Deterministic rules (errors fail the gate):
- Sentence length (chat ≤ 25 words, full ≤ 20)
- Paragraph length (≤ 6 sentences; lists parsed separately)
- Semicolons (banned)
- Progressive tense (`is running`) and perfect tense (`has done`)

Advisory (warnings):
- Passive voice, phrasal verbs
- Unapproved words → suggested plain-English swap (curated seed map)

## Use

```bash
# lint text on stdin; exit 1 if any error-severity violation
echo "Commence the repair prior to the test." | python3 scripts/ste_lint.py --pretty

# lint files, globs, or directories (.md / .txt); human output with line numbers
python3 scripts/ste_lint.py --format text docs/ "notes/*.md"
#   docs/intro.md:12: error: sentence-length — 27 words (max 25)

# stricter document profile
python3 scripts/ste_lint.py --profile full --text "Your sentence here."
```

Installed as a console command (`pip install .`):

```bash
ste --format text README.md        # exit 1 if any file has an error violation
```

Run the tests:

```bash
python3 -m unittest discover -s tests
```

## As a Claude Code skill

Copy or symlink this folder into `~/.claude/skills/ste/`, then toggle it with
`/ste on` and `/ste off`. See [SKILL.md](SKILL.md).

## The dictionary

v1 bundles a small, hand-authored **substitution map**
(`scripts/ste_dictionary.py`) — common non-STE words mapped to plain
replacements. It is **not** the official 900-word list, which is copyrighted.

Extend it two ways:
- Add your own entries (including company technical terms).
- (Roadmap) point the tool at **your own** official ASD-STE100 copy; it parses
  that local file into a git-ignored cache. The official data is never shipped
  or committed.

## Roadmap

- [ ] Standalone `ste` CLI (files, globs, config)
- [ ] pre-commit hook
- [ ] Custom / project dictionary loading
- [ ] Local official-dictionary parsing (bring your own copy)
- [ ] Noun-cluster rule (needs part-of-speech tagging)

## License

[MIT](LICENSE). See [NOTICE](NOTICE) for trademark and copyright terms.
