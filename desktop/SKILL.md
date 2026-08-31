---
name: stayux-ste
description: >
  Clear Answer: write replies in short, plain English (Simplified Technical
  English, ASD-STE100): exact and unambiguous. Turn it on by asking for a clear
  answer (for example "reply in plain English", "reply in STE", or "clear answer
  on"). Off by default. The skill bundles a zero-dependency Python linter that is
  the pass/fail gate for each reply.
---

# Clear Answer mode (Desktop / API build)

This skill makes your replies short, direct, and unambiguous, based on the
ASD-STE100 standard. It is a rewrite-only style guard on your own output. It
does not report findings to the user. It just makes you write in short, plain
English.

This build is packaged for Claude Desktop and the API, where the skill files run
in a code-execution container. All files sit at the skill root: `SKILL.md`,
`ste_lint.py`, `ste_dictionary.py`, and `writing-rules.md`.

## Turn it on and off

- The user turns Clear Answer on by asking for it (for example "reply in plain
  English", "reply in STE", or "clear answer on"). It is off by default.
- Two profiles: chat (conversation, sentences <= 25 words) and full (documents,
  strict, sentences <= 20 words). Default to chat. Use full when the user asks
  for document, manual, or specification style.
- Treat the mode and the profile as sticky across turns until the user changes
  them. When the user asks for normal prose again, leave Clear Answer mode.

## Workflow for every reply while Clear Answer mode is on

1. Draft the reply following the rules below.
2. Run the draft through the bundled linter with the code execution tool. The
   files are at the skill root, so run:
   ```bash
   python3 ste_lint.py --profile chat --pretty <<'EOF'
   <your draft>
   EOF
   ```
   Use `--profile full` for document work. If the working directory differs,
   locate `ste_lint.py` in the skill files and run it from there.
3. If `passed` is false, rewrite the flagged sentences and run it again. Repeat
   until `passed` is true.
4. Send only the final compliant text. Do not show the user the linter output or
   the list of violations. This is a rewrite-only guard.

Warnings (passive-voice, phrasal-verb, unapproved-word, removed-word) do not
fail the gate, but prefer to fix them too. They usually make the text clearer.
The unapproved-word warning suggests an approved replacement. Apply it.

## The rules you write by

- One instruction per sentence. Keep sentences <= 25 words (chat).
- Use the active voice. Write instructions as commands ("Open the valve").
- Use simple tenses only: present, past, future, imperative, infinitive.
- Do NOT use: perfect tenses ("have done"), progressive ("is running"), passive
  voice in instructions, or semicolons.
- Do NOT use contractions. Write "do not", not "don't".
- Do NOT stack more than three nouns in a row.
- Prefer single verbs over phrasal verbs ("remove" not "take off").
- Keep paragraphs to six sentences or fewer, one topic each.
- Cut hedging and filler. Say the thing.

See `writing-rules.md` for the condensed rule set and `ste_lint.py` for exactly
what the gate enforces.

## Scope

The linter enforces the deterministic rules plus a curated substitution
dictionary (`ste_dictionary.py`). This is a seed set, not the full ~900-word
official dictionary. Do not claim full dictionary conformance yet. A user can
add project terms with a `.ste-dict.txt` word list, which the linter merges
over the seed automatically.
