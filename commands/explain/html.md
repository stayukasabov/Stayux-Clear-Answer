---
description: Explain a topic as a self-contained HTML page with a diagram. Claude fills the blanks, and a script builds the page.
---

# Explain a topic as an HTML page

The argument is the topic. The result is one HTML page that works with no
network. It contains fixed sections, an SVG diagram, light and dark mode, and the
Stayux Clear Answer footer.

Clear Answer is a translation, not a summary. Give the content that the topic
needs. Only the sentences change.

## Workflow

1. Plan the content silently. Then write the content file
   `<topic-slug>.clear.txt` once, in the working directory, for example
   `how-a-cdn-works.clear.txt`. Fill only the blanks below. Write in plain
   English from the start. Do not write HTML, Markdown, Mermaid, or SVG.
2. Build the file:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/explain_build.py" "<topic-slug>.clear.txt" --to html
   ```
3. If `passed` is true, the work is done. Do not build again for a warning.
4. If `passed` is false, read `problems`. Each problem names its blank in
   `where`, such as "step 3". Change only the lines of those blanks, with the
   Edit tool. Do not use `sed`, and do not write the whole file again. In the
   same edit, you can also fix a warning with a one-word change. Then build
   again.
5. Reply with exactly one sentence and the path in `file`:
   "The page is ready: /absolute/path/how-a-cdn-works.html". Do not show the content file,
   the build output, or the linter output.

<!-- content-format:start -->
## The content file

Write one blank on each line. A line that starts with `#` is a comment.

```text
title: How a CDN works
answer: A content delivery network (CDN) keeps copies of your files on servers near your users. A user gets a file from a near server, not from your main server. The page loads faster, and your main server gets less traffic.
diagram: sequence
actor U: User
actor C: CDN server
actor M: Main server
U -> C: Ask for a file
C -> M: Ask if no copy
M --> C: Send the file
C --> U: Send the file
caption: The CDN server asks the main server only when it has no copy.
part: CDN server | A server near the user that keeps copies of your files.
part: Main server | Your own server. It has the original files.
step: The user asks for a file, such as an image.
step: The request goes to the nearest CDN server.
step: If that server has a copy, it sends the copy to the user.
step: If it has no copy, it gets the file from the main server. It keeps a copy for the next request.
limits: A CDN helps most with files that do not change often. For data that changes for each user, the CDN must ask the main server each time.
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

The example is about a different topic. Do not copy its actors, messages, or
steps. Use the real parts and steps of your topic.
<!-- content-format:end -->
