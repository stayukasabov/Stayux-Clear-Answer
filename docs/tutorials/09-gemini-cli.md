# 9. Clear Answer in Gemini CLI

> **Untested.** This path is not tested on Gemini CLI. The instructions are
> standard for Gemini CLI, but the gate depends on the agent running a shell
> command. If the agent cannot run it, the instructions tell it to say that the
> gate is off.

## 1. Get the linter

Clone the repository to a fixed place. The instructions file calls the linter
from there.

```bash
git clone https://github.com/stayukasabov/Stayux-Clear-Answer ~/.clear-answer
python3 ~/.clear-answer/scripts/ste_lint.py --text "Open the valve."
```

The second command must print `"passed": true`. The linter needs only Python 3.

## 2. Add the instructions

Gemini CLI reads `GEMINI.md` files. Use one of these:

- For one project: copy the file to the project root as `GEMINI.md`.
  ```bash
  cp ~/.clear-answer/prompts/AGENTS.md ./GEMINI.md
  ```
- For all projects: copy it to `~/.gemini/GEMINI.md`.

If the file already exists, add the Clear Answer text to the end of it.

## 3. Check it

Ask a question, for example "What does a CDN do?". The agent must run
`ste_lint.py` before it replies. If it asks for permission to run the command,
allow it. If it says that the gate is off, check that `python3` is on the path.
