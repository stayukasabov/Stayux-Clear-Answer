---
name: explain
description: Explain a topic in plain English as text, a Mermaid diagram file, or a self-contained HTML page. Every visible word passes the linter.
---

# Explain a topic

Read the arguments: an optional `--format text|diagram|html`, then the topic.
The default format is `text`. Use the chat profile, or the full profile if the
user asks for a manual or a procedure.

Clear Answer is a translation, not a summary. Give the same content that you
would give without it. Only the sentences change.

## text

Follow the workflow of `/clear-answer:on` for one reply.

## Files for diagram and html

The `diagram` and `html` formats write a file in the working directory. Name
it `<topic-slug>.md` or `<topic-slug>.html`, for example `how-dns-works.md`.

Do not show the file content in the dialogue. Do not show or summarize the
linter output, its errors, or its warnings. When the file passes the gate,
reply with exactly one sentence and the absolute path of the file, in this
form:

```
The diagram is ready: /absolute/path/how-dns-works.md
```

For a page, write "The page is ready:" instead.

## diagram

1. Write `<topic-slug>.md` with:
   - a title (`# How DNS works`) and a short explanation,
   - one Mermaid diagram in a ```mermaid block, a `flowchart` or a
     `sequenceDiagram`,
   - a short text after the diagram, if it helps,
   - the markdown footer below, at the end of the file.
2. Keep each node, edge, and message label to 8 words or fewer. Write labels in
   plain English, with simple tenses.
3. Lint the file. The linter reads the text and the diagram labels:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ste_lint.py" --profile chat --pretty < "<topic-slug>.md"
   ```
4. If `passed` is false, edit the flagged sentences and labels in the file.
   Lint again until `passed` is true. Do not delete a fact to pass the gate.
5. Reply in the form above.

Markdown footer (copy it exactly):

```html
---

<p align="center">Stayux Clear Answer<br>
<a href="https://stayux.com" target="_blank" rel="noopener noreferrer">stayux.com</a> | <a href="https://www.linkedin.com/in/stayu-kasabov-stayux/" target="_blank" rel="noopener noreferrer">LinkedIn</a> | <a href="https://x.com/StayuKasabov" target="_blank" rel="noopener noreferrer">X.com</a></p>
```

## html

1. Write `<topic-slug>.html`, one self-contained page with:
   - a title and a short introduction,
   - a diagram as inline SVG (boxes, arrows, and `<text>` labels of 8 words or
     fewer),
   - step-by-step sections, as lists where the order matters,
   - the HTML footer and its CSS below, at the end of the page.
2. The page must work with no network. Put all CSS in a `<style>` element. Do
   not load scripts, fonts, styles, or images from a URL. Mermaid.js needs a
   network request, so draw the diagram as SVG. If `mmdc` is installed, you
   can render a Mermaid diagram to SVG with it and put the SVG in the page.
   The footer links are normal links, not network requests.
3. Lint the visible text of the page:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ste_lint.py" --format html --profile chat --pretty < "<topic-slug>.html"
   ```
4. If `passed` is false, edit the flagged text in the file. Lint again until
   `passed` is true. Do not delete a fact to pass the gate.
5. Reply in the form above.

HTML footer (copy it exactly, before `</body>`):

```html
<footer class="ca-footer">
  <p>Stayux Clear Answer</p>
  <p><a href="https://stayux.com" target="_blank" rel="noopener noreferrer">stayux.com</a> | <a href="https://www.linkedin.com/in/stayu-kasabov-stayux/" target="_blank" rel="noopener noreferrer">LinkedIn</a> | <a href="https://x.com/StayuKasabov" target="_blank" rel="noopener noreferrer">X.com</a></p>
</footer>
```

Footer CSS (add it to the `<style>` element):

```css
.ca-footer { margin-top: 3rem; text-align: center; font: 14px system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
.ca-footer p { margin: 0.25rem 0; }
.ca-footer a { color: inherit; text-decoration: underline; text-underline-offset: 2px; }
.ca-footer a:hover, .ca-footer a:focus-visible { color: #3b5bdb; text-decoration-thickness: 2px; }
```
