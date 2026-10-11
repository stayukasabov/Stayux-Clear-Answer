# 11. Explain a topic with a diagram

`/clear-answer:explain --format diagram` writes a markdown file with a short
answer, one Mermaid diagram, and fixed sections. The linter checks the text and
every label in the diagram. The dialogue shows only a link to the file.

## Run it

1. Open Claude Code with the plugin installed.
2. Run:
   ```
   /clear-answer:explain --format diagram How does DNS work?
   ```
3. Claude replies with one sentence and the path of the file:
   ```
   The diagram is ready: /Users/you/project/how-dns-works.md
   ```

## What Claude does

Claude writes the file once. It does not write a draft first.

1. It writes the file in plain English, with the fixed structure.
2. `scripts/explain_page.py` adds the footer.
3. The linter checks the file on disk.
4. If the linter finds an error, Claude changes only the flagged lines.

In a real run with Claude Sonnet, this took one write and one lint, and the file
passed on the first lint.

## What you get

The real file is
[`examples/explain-dns-diagram.md`](examples/explain-dns-diagram.md). Each file
has the same sections, in the same order:

1. The title, "How X works".
2. The answer, in 3 sentences or fewer.
3. The diagram and a one-sentence caption.
4. "The parts", as a table.
5. "The steps", as a numbered list.
6. "Limits".

The Mermaid CLI (`mmdc`) gave this image of the diagram:

![The DNS sequence diagram](examples/explain-dns-diagram.png)

The diagram rules keep the style the same from run to run. The theme is
`neutral`, and the diagram uses `sequenceDiagram` with `autonumber`. Each label
is a verb and an object, such as "Send the IP address".

## Where the diagram shows

The diagram shows as a picture only in a viewer that supports Mermaid, such as
Obsidian or GitHub. MacDown shows the Mermaid code instead.

## What the gate checks

```bash
python3 scripts/ste_lint.py --profile chat --pretty < docs/tutorials/examples/explain-dns-diagram.md
```

- The text gets all the usual rules.
- Each node label, edge label, and message gets the word rules.
- A label of more than 8 words is an error (`label-length`).
- The footer is HTML, and the linter skips HTML tags in markdown.

The gate checks words, not drawings. Read the diagram before you share it.

## The footer

Each file ends with this footer, centered:

```
Stayux Clear Answer
Stayux.com | LinkedIn | X.com
```

The links open in a new tab. Some markdown viewers, such as GitHub, remove the
`target` attribute and the styles, so there the links open in the same tab.
