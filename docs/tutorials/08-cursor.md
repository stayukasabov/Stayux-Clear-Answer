# 8. Clear Answer in Cursor

> **Untested.** This path is not tested on Cursor. The instructions are
> standard for Cursor, but the gate depends on the agent running a shell
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

Cursor reads an `AGENTS.md` file in the project root.

```bash
cp ~/.clear-answer/prompts/AGENTS.md ./AGENTS.md
```

If the project already has an `AGENTS.md`, add the Clear Answer text to the end
of it. You can also add the same text as a project rule in `.cursor/rules/`.
Use the agent mode, because it can run terminal commands.

## 3. Check it

Ask a question, for example "What does a CDN do?". The agent must run
`ste_lint.py` before it replies. If it asks for permission to run the command,
allow it. If it says that the gate is off, check that `python3` is on the path.
