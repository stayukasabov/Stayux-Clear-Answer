---
name: on
description: Turn on Clear Answer mode. Every following reply is written in plain English with short sentences and gated by the linter until you run /clear-answer:off.
---

# Turn on Clear Answer mode

Enter Clear Answer mode with the chat profile. From now until the user runs
`/clear-answer:off` (or `/clear-answer:mode off`), write every reply in plain English
with short sentences (Simplified Technical English, ASD-STE100). This is a
rewrite-only guard on your own output. Do not report findings to the user.
Clear Answer is a translation, not a summary. Give the same content that you
would give without it. Only the sentences change.

Treat the mode as sticky across turns until the user changes it.

## For every reply while Clear Answer mode is on

1. Write the full answer that you would give without Clear Answer. Do not
   shorten it or leave out any fact, step, check, or warning. Use the rules in
   `${CLAUDE_PLUGIN_ROOT}/skills/clear-write/SKILL.md` and
   `${CLAUDE_PLUGIN_ROOT}/references/writing-rules.md`.
2. Lint the draft. It is the objective gate:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ste_lint.py" --profile chat --pretty <<'EOF'
   <your draft>
   EOF
   ```
3. If `passed` is false, fix only the flagged sentences. Split a long sentence
   into two or more sentences, or rephrase it. Keep every sentence that passed.
   Do not delete a fact to pass the gate. Lint again. Repeat until `passed` is
   true.
4. Compare the final text with your first draft. Every fact, step, check, and
   warning of the draft must be in the final text.
5. Send only the final compliant text. Do not show the linter output.

Format warnings (bold-overuse, header-in-short-reply, bullet-overuse,
filler-opener, filler-closer) do not fail the gate. If the user asked for a
table, a list, or headers, ignore them for that reply.

Use `/clear-answer:mode strict` for document-strict checking (sentences of 20
words or fewer).
