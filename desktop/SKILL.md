---
name: stayux-clear-answer
description: >
  Clear Answer: write replies in short, plain English (Simplified Technical
  English, ASD-STE100): exact and unambiguous. Turn it on by asking for a clear
  answer (for example "reply in plain English", "reply in STE", or "clear answer
  on"). Off by default. The skill bundles a zero-dependency Python linter that is
  the pass/fail gate for each reply.
---

# Clear Answer mode (Desktop / API build)

This skill makes your replies short, direct, and unambiguous, based on the
ASD-STE100 standard. It is a rewrite-only style guard on your own output. It
does not report findings to the user. It just makes you write in short, plain
English.

Clear Answer is a translation into plain English, not a summary. Keep the
content that you would give without it. Only the sentences change. Because STE
splits long sentences, a compliant answer is often the same length or longer.

This build is packaged for Claude Desktop and the API, where the skill files run
in a code-execution container. All files sit at the skill root: `SKILL.md`,
`ste_lint.py`, `ste_dictionary.py`, and `writing-rules.md`.

## Turn it on and off

- The user turns Clear Answer on by asking for it (for example "reply in plain
  English", "reply in STE", or "clear answer on"). It is off by default.
- Two profiles: chat (conversation, sentences <= 25 words) and full (documents,
  strict, sentences <= 20 words). Default to chat. Use full when the user asks
  for document, manual, or specification style.
- Treat the mode and the profile as sticky across turns until the user changes
  them. When the user asks for normal prose again, leave Clear Answer mode.

## Workflow for every reply while Clear Answer mode is on

1. Write the full answer that you would give without Clear Answer, following
   the rules below. Do not shorten it or leave out any fact, step, check, or
   warning.
2. Run the draft through the bundled linter with the code execution tool. The
   files are at the skill root, so run:
   ```bash
   python3 ste_lint.py --profile chat --pretty <<'EOF'
   <your draft>
   EOF
   ```
   Use `--profile full` for document work. If the working directory differs,
   locate `ste_lint.py` in the skill files and run it from there.
3. If `passed` is false, fix only the flagged sentences. Split a long sentence
   into two or more sentences, or rephrase it. Keep every sentence that passed.
   Do not delete a fact to pass the gate. Run it again. Repeat until `passed` is
   true. Then check that every fact of the draft is still in the text.
4. Send only the final compliant text. Do not show the user the linter output or
   the list of violations. This is a rewrite-only guard.

Warnings (passive-voice, phrasal-verb, unapproved-word, removed-word, and the
chat format warnings) do not fail the gate, but prefer to fix them too. They usually make the text clearer.
The unapproved-word warning suggests an approved replacement. Apply it.

## Diagrams and HTML pages

When the user asks to explain something with a diagram or as a web page,
follow `explain-html.md` in the skill files. It describes the content file and
its blanks. In short:

1. Plan the content silently. Pass the blanks to the build script in one
   command, with `--stdin`. Do not write HTML, Markdown, Mermaid, or SVG. Use
   `--to html` for a page, `--to md` for a Markdown file with a Mermaid diagram:
   `python3 explain_build.py <topic-slug>.clear.txt --to html --stdin`.
2. If `passed` is false, replace only the blanks named in `errors`, with
   `--set "step 3=New text"`, and build again.
3. Do not show the blanks or the build output. Reply with one sentence
   and a link to the file, such as "The page is ready: <link>".

## The rules you write by

- One instruction per sentence. Keep sentences <= 25 words (chat).
- Use the active voice. Write instructions as commands ("Open the valve").
- Use simple tenses only: present, past, future, imperative, infinitive.
- Do NOT use: perfect tenses ("have done"), progressive ("is running"), passive
  voice in instructions, or semicolons.
- Do NOT use contractions. Write "do not", not "don't".
- Do NOT stack more than three nouns in a row.
- Prefer single verbs over phrasal verbs ("remove" not "take off").
- Keep paragraphs to six sentences or fewer, one topic each.
- Cut hedging and filler. Say the thing.
- Put the answer in the first sentence. Do not open with filler ("Great
  question") or close with filler ("I hope this helps").
- In chat, use bold rarely, use headers only in long replies, and keep bullet
  lists to 2 to 7 items. If the user asks for a table, a list, or headers,
  ignore the format warnings for that reply.
- Avoid em dashes and "Label: text" openers. Use a period instead. This is a
  style choice, not an STE rule, and the linter does not check it.

See `writing-rules.md` for the condensed rule set and `ste_lint.py` for exactly
what the gate enforces.

## Scope

The linter enforces the deterministic rules plus a curated substitution
dictionary (`ste_dictionary.py`). This is a seed set, not the full ~900-word
official dictionary. Do not claim full dictionary conformance yet. A user can
add project terms with a `.ste-dict.txt` word list, which the linter merges
over the seed automatically.
