---
name: clear-write
description: >
  Clear Answer: write, rewrite, and check text in plain English with short
  sentences (Simplified Technical English, ASD-STE100). Load this when the user asks for a
  clear answer, plain English, short replies, to write or rewrite in STE, to
  check STE compliance, apply ASD-STE100, or simplify technical documentation.
  Commands: /clear-answer:on, /clear-answer:off, /clear-answer:mode,
  /clear-answer:check, /clear-answer:rewrite, /clear-answer:init,
  /clear-answer:explain.
---

# Simplified Technical English (STE)

Simplified Technical English (ASD-STE100) is a controlled-English standard for
technical text that is clear, direct, and unambiguous. Use it to write or rewrite
text so any reader, including a non-native reader, parses it the same way.

The plugin bundles a zero-dependency Python linter that is the objective
pass/fail gate. The rules and the substitution dictionary live on disk, so they
cost no model-context tokens.

## Commands

- `/clear-answer:on`, `/clear-answer:off`: turn Clear Answer dialogue mode on or
  off. While on, every reply is written in plain English with short sentences
  and gated by the linter.
- `/clear-answer:mode off|prose|strict`: set the mode and strictness.
- `/clear-answer:check`: check a file or text and report the violations.
- `/clear-answer:rewrite`: rewrite text with a before and after.
- `/clear-answer:init`: add the rules to the project's CLAUDE.md.
- `/clear-answer:explain [--format text|diagram|html]`: explain a topic as text,
  a Mermaid diagram, or a self-contained HTML page.

## When the user asks for STE without a command

Apply STE to the relevant text, then lint it before you present it:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ste_lint.py" --profile full --pretty <<'EOF'
<your text>
EOF
```

Rewrite until `passed` is true. For a rewrite task, show a before and after. For
a compliance check, report the violations. For a dialogue request, keep the
sentences short and gate every reply.

## How to write a Clear Answer

Clear Answer is a translation into plain English, not a summary. A translation
keeps all the content. Only the sentences change.

1. **Full draft first.** Write the answer that you would give without Clear
   Answer. Do not shorten it.
2. **Lint the draft, then fix only the flagged sentences.** Split a long
   sentence into two or more sentences, or rephrase it. Keep every sentence
   that passed. Do not merge or drop content.
3. **Check the content.** Compare the final text with the draft. Every fact,
   step, check, and warning must still be there.

A Clear Answer is often the same length as a normal answer, or longer.

Example:

- Normal: "Before you revoke the old key, disable it and wait a day, so that
  you can re-enable it if something breaks."
- Clear Answer: "Disable the old key. Wait 24 hours. If errors occur, enable
  the old key again. If no errors occur, delete the old key."

The Clear Answer has more sentences and the same facts.

## The rules you write by

- One instruction per sentence. Keep sentences within the profile limit (chat 25
  words, full 20).
- Use the active voice. Write instructions as commands ("Open the valve").
- Use simple tenses only: present, past, future, imperative, infinitive.
- Do NOT use perfect tenses ("have done"), progressive ("is running"), passive
  voice in instructions, or semicolons.
- Do NOT use contractions. Write "do not", not "don't".
- Do NOT stack more than three nouns in a row.
- Prefer single verbs over phrasal verbs ("remove" not "take off").
- Keep paragraphs to six sentences or fewer, one topic each.
- Cut hedging and filler. Say the thing.
- Put the answer in the first sentence. Do not open with filler ("Great
  question") or close with filler ("I hope this helps").
- In chat, use bold rarely, use headers only in long replies, and keep bullet
  lists to 2 to 7 items. If the user asks for a table, a list, or headers,
  ignore the format warnings for that reply.
- Avoid em dashes and "Label: text" openers. Use a period instead. This is a
  style choice, not an STE rule, and the linter does not check it.

See `${CLAUDE_PLUGIN_ROOT}/references/writing-rules.md` for the condensed rule set
and `${CLAUDE_PLUGIN_ROOT}/scripts/ste_lint.py` for exactly what the gate
enforces.

## Scope

The linter enforces the deterministic rules plus a curated substitution
dictionary (`scripts/ste_dictionary.py`), verified in part against ASD-STE100
Issue 9. This is a seed set, not the full ~900-word official dictionary. Do not
claim full dictionary conformance yet. A user can extend it with a
`.ste-dict.txt` in the project (word list) or an imported official cache; the
linter merges both automatically.
