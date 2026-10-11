---
name: mode
description: Set Clear Answer mode to off, prose, or strict. Prose uses the chat profile. Strict uses the full document profile.
---

# Set Clear Answer mode

Read the argument after the command:

- `off`: leave Clear Answer mode. Return to normal prose. Same as
  `/clear-answer:off`.
- `prose`: enter Clear Answer mode with the chat profile (sentences of 25 words or
  fewer). Lenient, for conversation and READMEs. Same as `/clear-answer:on`.
- `strict`: enter Clear Answer mode with the full profile (sentences of 20 words or
  fewer). For manuals, procedures, and specifications.

When on, follow this workflow for every reply. Treat the mode as sticky until the
user changes it.

Clear Answer is a translation, not a summary. Give the same content that you would give without it. Only the sentences
change. In strict mode, a procedure keeps every step, check, and warning. Each
one becomes its own sentence.

1. Write the full answer that you would give without Clear Answer. Do not
   shorten it or leave out any fact, step, check, or warning. Use the rules in
   `${CLAUDE_PLUGIN_ROOT}/skills/clear-write/SKILL.md`.
2. Lint the draft with the matching profile: `chat` for prose, `full` for strict.
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ste_lint.py" --profile full --pretty <<'EOF'
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

If no argument is given, report the current mode and the three options.
