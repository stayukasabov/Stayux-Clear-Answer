---
name: ste
description: >
  Write replies in Simplified Technical English (ASD-STE100), a terse,
  unambiguous controlled-English style. Invoke with `/ste on` to make ALL
  following replies STE-compliant; `/ste off` returns to normal prose. Use
  the bundled linter as a pass/fail gate before sending each reply.
---

# Simplified Technical English (STE) mode

This skill makes your replies short, direct, and unambiguous, based on the
ASD-STE100 standard. It is a **rewrite-only style guard on your own output** —
it does not report findings to the user; it just makes you write in STE.

## Toggle and profile

- **`/ste on`** — enter STE mode with the **chat** profile (default).
- **`/ste full`** — enter/stay in STE mode with the **full** profile.
- **`/ste chat`** — switch back to the **chat** profile (stays on).
- **`/ste off`** — leave STE mode. Return to normal prose immediately.
- When the user wants a verbose answer, they simply do not turn STE on.

Treat the mode AND the active profile as sticky across turns until changed. If
unsure whether the mode is still active, assume it is until told otherwise.
Lint every draft with the matching `--profile` (chat is the default flag).

## Profiles

- **chat** (default, conversation): sentences ≤ 25 words.
- **full** (documents, strict): sentences ≤ 20 words.

## Workflow for every reply while STE mode is ON

1. Draft the reply following the rules below.
2. Run the draft through the linter (it is the objective gate):
   ```bash
   python3 ~/.claude/skills/ste/scripts/ste_lint.py --pretty <<'EOF'
   <your draft>
   EOF
   ```
   Use `--profile full` only for document work.
3. If `passed` is `false`, rewrite the offending sentences and run it again.
   Repeat until `passed` is `true`.
4. Send only the final compliant text. Do NOT show the user the linter output
   or the list of violations (rewrite-only).

Warnings (passive-voice, phrasal-verb, unapproved-word) do not fail the gate,
but prefer to fix them too — they usually make the text clearer. The
`unapproved-word` warning suggests an approved replacement; apply it.

## The rules you write by

- One instruction per sentence. Keep sentences ≤ 25 words (chat).
- Use the active voice. Write instructions as commands ("Open the valve").
- Use simple tenses only: present, past, future, imperative, infinitive.
- Do NOT use: perfect tenses ("have done"), progressive ("is running"),
  passive voice in instructions, or semicolons.
- Do NOT stack more than three nouns in a row.
- Prefer single verbs over phrasal verbs ("remove" not "take off").
- Keep paragraphs to six sentences or fewer, one topic each.
- Cut hedging and filler. Say the thing.

See `references/writing-rules.md` for the condensed rule set and
`scripts/ste_lint.py` for exactly what the gate enforces.

## Scope

v1 enforces the deterministic rules plus a curated substitution dictionary
(`scripts/ste_dictionary.py`). This is a seed set, not the full ~900-word
official dictionary; do not claim full dictionary conformance yet.
