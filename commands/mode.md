---
name: mode
description: Set Clear Answer mode to off, prose, or strict. Prose uses the chat profile. Strict uses the full document profile.
---

# Set Clear Answer mode

Read the argument after the command:

- `off`: leave Clear Answer mode. Return to normal prose. Same as
  `/clear-answer:off`.
- `prose`: enter Clear Answer mode with the chat profile (sentences of 25 words
  or fewer), for conversation. Same as `/clear-answer:on`.
- `strict`: enter Clear Answer mode with the full profile (sentences of 20
  words or fewer), for manuals, procedures, and specifications.

If no argument is given, report the current mode and the three options.

While the mode is on, treat it as sticky until the user changes it, and do this
for every reply:

<!-- gate:start -->
## Write it right the first time

- Keep each sentence to 25 words or fewer (20 in strict mode). Split long
  sentences.
- Do not use semicolons. Write two sentences.
- Do not use contractions. Write "do not", not "don't".
- Use simple tenses. Do not write "is running" or "has done".
- Keep each paragraph to 6 sentences or fewer.
- Use the active voice. Write one instruction in each sentence.
- Put the answer first. Do not open or close with filler.

Clear Answer is a translation, not a summary. Give the same content that you
would give without it. Keep every fact, step, check, and warning. Only the
sentences change.

## The check

1. Write the full text, with the rules above.
2. Check it. Use `--profile full` in strict mode:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ste_lint.py" --profile chat --brief <<'EOF'
   <your text>
   EOF
   ```
3. `PASS`: send the text as your reply. Do not show the check.
4. `FAIL`: each line names an error and its sentence. Fix only those sentences.
   Split or rephrase them, and do not delete a fact. Check again with
   only the changed sentences. After a `paragraph-length` error, check the
   whole paragraph again. Repeat until `PASS`.
<!-- gate:end -->
