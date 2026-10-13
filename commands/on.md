---
name: on
description: Turn on Clear Answer mode. Every following reply is written in plain English with short sentences and checked by the linter until you run /clear-answer:off.
---

# Turn on Clear Answer mode

Enter Clear Answer mode with the prose (chat) profile. From now until the user
runs `/clear-answer:off` or `/clear-answer:mode off`, write every reply in plain
English with short sentences (Simplified Technical English, ASD-STE100). Treat
the mode as sticky across turns.

When the mode turns on, check once for a second copy of the skill:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ste_dupcheck.py"
```
If it prints a message, show the message to the user. If it prints nothing,
say nothing about it.

For every reply while the mode is on:

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

Use `/clear-answer:mode strict` for manuals and procedures (sentences of 20
words or fewer).
