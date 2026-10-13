---
name: explain
description: Explain a topic in plain English, in a fixed structure. The linter checks the explanation before you see it.
---

# Explain a topic

The argument is the topic. Explain it in one reply, in plain English with short
sentences.

## Structure

Use these parts, in this order:

1. The answer, in 3 sentences or fewer.
2. "The parts": a bulleted list, one item for each part of the topic and what
   it does. Write each item as one full sentence, such as "The resolver finds
   the address for your computer." Do not use bold labels or "Label: text".
3. "The steps": a numbered list, in order.
4. "Limits": one short paragraph.

Use the headings "The parts", "The steps", and "Limits". Leave out a part only
when the topic has no parts or no steps.

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
