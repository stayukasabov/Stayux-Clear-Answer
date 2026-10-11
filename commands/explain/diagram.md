---
description: Explain a topic as a Markdown file with a Mermaid diagram. Claude fills the blanks, and a script builds the file.
---

# Explain a topic as a diagram file

The argument is the topic. The result is a Markdown file with a Mermaid
diagram, in fixed sections, with the Stayux Clear Answer footer.

Clear Answer is a translation, not a summary. Give the content that the topic
needs. Only the sentences change.

## Workflow

1. Plan the content silently. Then write the content file
   `<topic-slug>.clear.txt` once, in the working directory, for example
   `how-dns-works.clear.txt`. Fill only the blanks below. Write in plain
   English from the start. Do not write HTML, Markdown, Mermaid, or SVG.
2. Build the file:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/explain_build.py" "<topic-slug>.clear.txt" --to md
   ```
3. If `passed` is false, read `problems`. Each problem names its blank in
   `where`, such as "step 3". Change only those blanks. Build again.
4. Fix a warning only when a one-word change fixes it.
5. Reply with exactly one sentence and the path in `file`:
   "The diagram is ready: /absolute/path/how-dns-works.md". Do not show the content file,
   the build output, or the linter output.

<!-- content-format:start -->
## The content file

Write one blank on each line. A line that starts with `#` is a comment.

```text
title: How DNS works
answer: DNS turns a name, such as `example.com`, into an IP address. Your computer asks a resolver for it.
diagram: sequence
actor B: Browser
actor R: Resolver
actor N: Name server
B -> R: Ask for the address
R -> N: Ask the name server
N --> R: Send the address
R --> B: Send the address
caption: The resolver finds the address for the browser.
part: Resolver | Finds the address for your computer.
part: Name server | Keeps the records for a domain.
step: The browser asks the resolver for the address.
step: The resolver asks the name server and sends the address back.
section: Example | You type `www.example.com` in the browser.
limits: The resolver keeps a copy for a set time.
```

The blanks:

- `title`: "How X works", or "What X is" for a thing.
- `answer`: the answer, in 3 sentences or fewer.
- `diagram`: `sequence` for actors that send messages, or `flow` for a
  straight chain of stages.
- `actor ID: Label`: for `sequence`, 2 to 5 actors. Use a short ID and a
  label of 3 words or fewer.
- `A -> B: label`: a request. `A --> B: label` is a reply. For `sequence`, 1 to
  12 messages, in order. A label is a verb and an object, 6 words or fewer.
- `node: Label`: for `flow`, 2 to 5 stages, in order, 3 words or fewer each.
- `caption`: one sentence about the diagram.
- `part: Name | what it does`: one line for each part.
- `step: text`: one line for each step, in order.
- `section: Name | text`: at most 2. The name is "Example", "Common mistakes",
  or "Safety".
- `limits`: one short paragraph.

Put code, names of files, and addresses in backticks: `example.com`.
<!-- content-format:end -->
