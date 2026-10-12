---
name: explain
description: Explain a topic in plain English, in a fixed structure. The linter checks the explanation before you see it.
---

# Explain a topic

The argument is the topic. Explain it in one reply, in plain English with short
sentences.

Clear Answer is a translation, not a summary. Give the content that the topic
needs. Only the sentences change.

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

## Workflow

1. Write the full explanation, with the structure above. Do not shorten it.
2. Lint the draft. It is the gate:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ste_lint.py" --profile chat --pretty <<'EOF'
   <your draft>
   EOF
   ```
3. If `passed` is false, fix only the flagged sentences. Split a long sentence
   into two or more sentences, or rephrase it. Do not delete a fact to pass the
   gate. Lint again. Repeat until `passed` is true.
4. Send only the final explanation. Do not show the linter output.
