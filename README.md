<p align="center">
  <img src="Stayux-Clear-Answer.png" alt="Stayux Clear Answer — make Claude reply in short, plain English, in the dialogue and on your documents" width="820">
</p>

# Stayux Clear Answer

Clear Answer makes Claude write in plain English with short sentences. A Python
linter checks every answer before you see it, so the rules hold every time. It is
compatible with Simplified Technical English (ASD-STE100).

> **Unofficial.** Not affiliated with or endorsed by ASD. See [NOTICE](NOTICE).
> "Simplified Technical English" and "ASD-STE100" are trademarks of ASD
> (EUTM 017966390). This tool does not include or download ASD's copyrighted
> dictionary.

## Quick start

In Claude Code:

```
/plugin marketplace add stayukasabov/Stayux-Clear-Answer
/plugin install clear-answer@stayux-clear
```

Then explain a topic, or turn the mode on for the whole conversation:

```
/clear-answer:explain How does a CDN work?
/clear-answer:on
```

On Claude Desktop or claude.ai, see [Install](#install).

## Commands

| Command | What it does |
|---|---|
| `/clear-answer:explain <topic>` | Explains a topic in a fixed structure: the answer, the parts, the steps, and the limits. |
| `/clear-answer:on`, `/clear-answer:off` | Every reply in plain English, checked by the linter, until you turn it off. |
| `/clear-answer:mode prose\|strict` | `prose` allows sentences of 25 words. `strict` allows 20, for manuals and procedures. |
| `/clear-answer:check <file>` | Reports the problems in a document. It does not change the file. |
| `/clear-answer:rewrite <file>` | Rewrites a document and shows the before and after. |
| `/clear-answer:init` | Adds the Clear Answer rules to the project's `CLAUDE.md`, for the whole team. |

## Example

`/clear-answer:explain How does a CDN work?` gave this (first part of a real run
with Claude Sonnet):

> A CDN is a network of servers placed in many places around the world. It keeps
> copies of your content close to your users. This makes pages load faster and
> lowers the load on your main server.
>
> **The parts**
>
> - The origin server holds the original content of the site.
> - The edge servers are the CDN computers that sit near users and store copies of the content.
> - The DNS or routing system sends each user to a nearby edge server.

Every explanation has the same structure, so readers know where to look. The
full output is in [tutorial 2](docs/tutorials/02-explain.md).

## How it saves effort

**For the model.** The rules and the dictionary run in Python, outside Claude's
context. Claude sends its draft to the linter and reads back a short result.

| Item | Tokens | In Claude's context? |
|---|---:|---|
| Rules, dictionary, word tagger, and rule reference | about 9,700 | **no** |
| Skill text, when it loads | about 1,000 | yes, once |
| Lint result | 50 to 270 | yes, per check |
| Draft sent to the linter | about the length of the answer | yes, per check |

The token counts are estimates (characters divided by 4). Your imported official
dictionary also stays outside the context.

The check is not free. Claude writes the draft for the linter and then the final
text. In a real run, the checked answer used about 50% more output tokens than
the same answer without the check (1,640 against 1,082). For long procedures, the checked answer is
shorter, so the total can stay level or fall. See [the benchmark](docs/benchmark.md).

**For the people who read it.** In that run, the checked answer had 262 words
instead of 443, in numbered steps. Clear Answer helps with work in these ways:

- Readers find the answer faster and act on one step at a time.
- Non-native readers and translation tools read short, simple sentences more
  easily. That is the purpose of the STE standard.
- `/clear-answer:init` gives the whole team the same rules in every session.
- A commit hook or a CI step runs the same linter on your documents, so unclear
  text does not get in. See [tutorial 7](docs/tutorials/07-team-and-checks.md).

**Why a check is better than a prompt.** A prompt asks the model to remember the
rules. The linter checks every answer. Published STE cheat sheets have errors,
and a model that follows them repeats the errors. For example, one cheat sheet
says that TEST is an approved verb, but ASD-STE100 Issue 9 approves TEST as a
noun only. The linter has the correct rule, and a test for it
(`tests/test_cheat_sheet.py`).

## What it checks

| Errors (the answer must be fixed) | Warnings (advice) |
|---|---|
| Sentences over 25 words (20 in strict mode) | Passive voice and phrasal verbs |
| Paragraphs over 6 sentences | Two instructions in one sentence |
| Semicolons and contractions | Words that STE does not approve, by part of speech, with the approved options |
| Progressive tense ("is running") and perfect tense ("has done") | Wordy phrases ("in order to") |
| A code block that does not close | Chat style: too much bold, a header in a short reply, filler openers and closers |

Code, inline code, and HTML tags are not checked. Tables and lists are checked
item by item. The chat style warnings are not STE rules. Each one comes from a
public style guide (GOV.UK, Google, Microsoft).

Prose mode is close to the "80% STE" that Andrej Karpathy describes. Strict mode
follows the document rules of the standard.

## Install

**Claude Code:** see [Quick start](#quick-start). Update later with
`/plugin update clear-answer`, then start a new session.

**Claude Desktop and claude.ai:** download `stayux-clear-answer.zip` from the
[latest release](https://github.com/stayukasabov/Stayux-Clear-Answer/releases/latest).
Upload it in **Settings > Capabilities > Skills**, and turn on code execution.
Then say "clear answer on" in a chat. See [tutorial 6](docs/tutorials/06-desktop.md).

**Other agents:** Codex, Cursor, Gemini CLI, and Copilot can use the same rules
and linter. See [tutorial 8](docs/tutorials/08-other-agents.md).

The linter needs Python 3.9 or later. It has no other dependencies.

## Dictionaries

The plugin ships a small word list of its own. It does not include the official
ASD-STE100 dictionary, which is copyrighted. You can add two more layers:

- Your own words, in a `.ste-dict.txt` file in your project.
- Your own copy of the official dictionary, imported into a private local cache.

See [tutorial 5](docs/tutorials/05-dictionaries.md).

## Documentation

- [Tutorials](docs/tutorials/README.md): install, explain, dialogue mode, check
  and rewrite, dictionaries, Desktop, team checks, other agents, and build and
  update.
- [Rule reference](references/writing-rules.md)
- [The skill](skills/clear-write/SKILL.md)
- [Benchmark pilot](docs/benchmark.md)

## License

[MIT](LICENSE). See [NOTICE](NOTICE) for trademark and copyright terms.
