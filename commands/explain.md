---
name: explain
description: Explain a topic in plain English as text, a Mermaid diagram, or a self-contained HTML page. Every visible word passes the linter.
---

# Explain a topic

Read the arguments: an optional `--format text|diagram|html`, then the topic.
The default format is `text`. Use the chat profile, or the full profile if the
user asks for a manual or a procedure.

Clear Answer is a translation, not a summary. Give the same content that you
would give without it. Only the sentences change.

## text

Follow the workflow of `/clear-answer:on` for one reply.

## diagram

1. Write a short explanation and one Mermaid diagram in a ```mermaid block.
   Use a `flowchart` or a `sequenceDiagram`.
2. Keep each node, edge, and message label to 8 words or fewer. Write labels in
   plain English, with simple tenses.
3. Lint the full reply, with the diagram. The linter reads the labels:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ste_lint.py" --profile chat --pretty <<'EOF'
   <your reply>
   EOF
   ```
4. If `passed` is false, fix the flagged sentences and labels. Lint again until
   `passed` is true. Do not delete a fact to pass the gate.
5. Send the final reply. Do not show the linter output.

## html

1. Write one self-contained HTML file, `<topic-slug>.html`, in the working
   directory. The page has:
   - a title and a short introduction,
   - a diagram as inline SVG (boxes, arrows, and `<text>` labels of 8 words or
     fewer),
   - step-by-step sections, as lists where the order matters.
2. The page must work with no network. Put all CSS in a `<style>` element. Do
   not load scripts, fonts, styles, or images from a URL. Mermaid.js needs a
   network request, so draw the diagram as SVG. If `mmdc` is installed, you
   can render a Mermaid diagram to SVG with it and put the SVG in the page.
3. Lint the visible text of the page:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ste_lint.py" --format html --profile chat --pretty < "<topic-slug>.html"
   ```
4. If `passed` is false, edit the flagged text in the file. Lint again until
   `passed` is true. Do not delete a fact to pass the gate.
5. Reply with one sentence that gives the path of the file. Do not show the
   linter output.
