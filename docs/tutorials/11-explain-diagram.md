# 11. Explain a topic with a diagram

`/clear-answer:explain --format diagram` writes a markdown file with a short
explanation, one Mermaid diagram, and the Stayux Clear Answer footer. The linter
checks the text and every label in the diagram. The dialogue shows only a link
to the file.

## Run it

1. Open Claude Code with the plugin installed.
2. Run:
   ```
   /clear-answer:explain --format diagram How does HTTPS keep a connection private?
   ```

## What you get

Claude replies with one sentence and the path of the file:

```
The diagram is ready: /Users/you/project/how-https-keeps-a-connection-private.md
```

The file has a title, the explanation, the diagram, and the footer. This is the
real text from Claude Sonnet, saved in
[`examples/explain-https-diagram.md`](examples/explain-https-diagram.md),
without the title and the footer:

````markdown
HTTPS keeps a connection private with encryption. The browser and the server first agree on a secret key. Then they use that key to lock all data.

```mermaid
sequenceDiagram
    participant B as Browser
    participant S as Server
    B->>S: Send hello and supported ciphers
    S->>B: Send certificate and public key
    B->>B: Check certificate with trusted authority
    B->>S: Send key share
    S->>B: Send key share
    Note over B,S: The two sides make the same secret key
    B->>S: Send encrypted data
    S->>B: Send encrypted data
```

The certificate proves who the server is. The secret key never crosses the network. An attacker who reads the traffic sees only scrambled data.
````

GitHub, many editors, and Claude Desktop show the diagram as a picture. The
Mermaid CLI (`mmdc`) gave this image:

![The HTTPS sequence diagram](examples/explain-https-diagram.png)

## What the gate checks

- The text gets all the usual rules.
- Each node label, edge label, and sequence message gets the word rules: simple
  tenses, no contractions, and approved words.
- A label of more than 8 words is an error (`label-length`).
- The linter reads `flowchart`, `graph`, and `sequenceDiagram` diagrams. In
  other diagram types, it does not read the labels.

Check the file yourself:

```bash
python3 scripts/ste_lint.py --profile chat --pretty < docs/tutorials/examples/explain-https-diagram.md
```

The result is `"passed": true`. The footer links are HTML, and the linter
skips HTML tags in markdown.

## The footer

Each file ends with this footer, centered:

```
Stayux Clear Answer
Stayux.com | LinkedIn | X.com
```

The links open in a new tab. Some markdown viewers, such as GitHub, remove the
`target` attribute and the styles, so there the links open in the same tab.

## What the gate does not check

The gate checks words, not drawings. It does not check that the arrows are in
the correct order or that the diagram is correct. Read the diagram before you
share it.

## Render the diagram to an image (optional)

```bash
npx -p @mermaid-js/mermaid-cli mmdc -i diagram.mmd -o diagram.png -b white
```

This downloads the Mermaid CLI and a browser the first time.
