# 12. Explain a topic as an HTML page

`/clear-answer:explain --format html` writes one HTML page that works with no
network. The page has a short answer, a diagram, and fixed sections. The linter
checks every word that a reader sees. The dialogue shows only a link to the
file.

## Run it

1. Open Claude Code with the plugin installed, in the folder for the page.
2. Run:
   ```
   /clear-answer:explain --format html How does DNS work?
   ```
3. Claude replies with one sentence and the path:
   ```
   The page is ready: /Users/you/project/how-dns-works.html
   ```

## What Claude does

Claude writes only the body of the page, once. It does not write the CSS or the
footer.

1. It writes the body: the title, the answer, the diagram, and the sections.
2. `scripts/explain_page.py` adds the fixed frame: the page head, the CSS for
   light and dark mode, and the footer.
3. The linter checks the visible text of the page.
4. If the linter finds an error, Claude changes only the flagged lines.

In a real run with Claude Sonnet, this took one write and one lint, and the page
passed on the first lint.

## What you get

The real page is
[`examples/explain-dns-page.html`](examples/explain-dns-page.html). This is the
page in a browser with the network blocked:

![The DNS page in a browser](examples/explain-dns-page.png)

Each page has the same sections as the diagram files, in the same order. They
are the title, the answer, the diagram, "The parts", "The steps", and "Limits".

## The diagram

The diagram is inline SVG. It uses only the classes of the frame, so the colors
and the fonts are the same on every page. Claude picks one of two layouts:

- **Row**: a chain of 2 or 3 boxes, where each box talks only to its
  neighbors.
- **Lanes**: boxes in a row at the top, with a dotted line down from each box.
  Each step is a horizontal arrow with its label above it, so arrows do not
  cross. The DNS page uses this layout.

## What the gate checks

```bash
python3 scripts/ste_lint.py --format html --profile chat --pretty < docs/tutorials/examples/explain-dns-page.html
```

- Only visible text is checked. The linter skips the head, scripts, styles, and
  code.
- Each paragraph, list item, and table cell is checked on its own.
- Text in the SVG diagram is checked as labels, with a limit of 8 words.
- A page that loads a script, style, font, or image from the network fails
  with `external-request`. A link to another page is fine.

The gate checks words, not drawings. Open the page and look at the diagram
before you share it.

## The footer

The page ends with the Stayux Clear Answer footer. It is centered, in a 14 px
system font. The links are underlined, change color on hover, and open in a new
tab. The footer links are normal links, so they do not count as network
requests.
