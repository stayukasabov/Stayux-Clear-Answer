# 8. Other agents

> **Untested.** These steps are not tested on these agents. They depend on the
> agent running a shell command. If it cannot run the linter, the instructions
> tell the agent to say that the check is off.

Other coding agents can use the same rules and the same linter. They read an
instructions file instead of a plugin.

## Steps

1. Get the linter:
   ```bash
   git clone https://github.com/stayukasabov/Stayux-Clear-Answer ~/.clear-answer
   ```
2. Copy the instructions file to the place that your agent reads:

   | Agent | Copy `~/.clear-answer/prompts/AGENTS.md` to |
   |---|---|
   | Codex CLI | `AGENTS.md` in the project, or `~/.codex/AGENTS.md` for all projects |
   | Cursor | `AGENTS.md` in the project |
   | Gemini CLI | `GEMINI.md` in the project, or `~/.gemini/GEMINI.md` for all projects |
   | VS Code with GitHub Copilot | `.github/copilot-instructions.md` in the project |

   If the file is already there, add the Clear Answer text to the end of it.
3. Ask a question. The agent must run `ste_lint.py` before it replies. If it
   asks for permission to run the command, allow it.

## Tools that cannot run commands

For a chat tool or an API call with no shell, use
[`prompts/system-prompt.md`](../../prompts/system-prompt.md) as the system
prompt. It has the same rules, but there is no linter check.

Next: [9. Build and update](09-build-and-update.md).
