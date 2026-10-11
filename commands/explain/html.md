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

Use only shell commands. Do not use the Write tool, the Edit tool, or `sed`.
The dialogue then shows no file content and no diffs.

1. Plan the content silently. Then build the file with one command. Put the
   blanks (see below) in the command. The script saves them to
   `<topic-slug>.clear.txt` in the working directory and builds the file:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/explain_build.py" "<topic-slug>.clear.txt" --to html --stdin <<'EOF'
   title: How a CDN works
   ...
   EOF
   ```
   Write in plain English from the start.
2. If `passed` is true, the work is done.
3. If `passed` is false, read `errors`. Each error names its blank in `where`,
   such as "step 3". Fix only those errors, and change nothing else. Replace
   each blank with `--set`, all in one command:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/explain_build.py" "<topic-slug>.clear.txt" --to html --set "step 3=New text." --set "actor M=Main server"
   ```
   For a message, give the whole line: `--set "message 2=C -> M: Ask if no copy"`.
   For a part or a section, give `Name | text`. Do not send all the blanks again.
4. Reply with exactly one sentence and the path in `file`:
   "The page is ready: /absolute/path/how-a-cdn-works.html". Do not show the
   blanks, the build output, or the linter output.

<!-- content-format:start -->
## The content file

Write one blank on each line. A line that starts with `#` is a comment.

```text
title: How a CDN works
answer: A content delivery network (CDN) keeps copies of your files on servers near your users. A user gets a file from a near server, not from your main server. The page loads faster, and your main server gets less traffic.
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
- The diagram is always actors that send messages, in order. For a process,
  make each stage an actor that hands the work to the next one.
- `actor ID: Label`: 2 to 5 actors. Use a short ID and a
  label of 3 words or fewer.
- `A -> B: label`: a request. `A --> B: label` is a reply. 1 to 12 messages,
  in order. A label is a verb and an object, 6 words or fewer.
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
