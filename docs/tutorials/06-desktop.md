# 6. Claude Desktop and the API

On Claude Desktop, claude.ai, and the API, Clear Answer is one uploaded skill.
There are no slash commands. You turn it on and off with words.

## Install

1. Download `stayux-clear-answer.zip` from the
   [latest release](https://github.com/stayukasabov/Stayux-Clear-Answer/releases/latest).
2. Open **Settings > Capabilities**. Turn on code execution, because the skill
   runs the linter.
3. In **Skills**, upload the zip and turn the skill on.

Custom skills need a Pro, Max, Team, or Enterprise plan.

## Use

- Turn it on: say "clear answer on", "reply in plain English", or "reply in
  STE".
- For manuals and procedures, ask for the "full" profile (sentences of 20
  words or fewer).
- Turn it off: say "clear answer off" or "reply in normal prose".

## Two copies

claude.ai also copies your uploaded skills into Claude Code. If you also have
the plugin in Claude Code, you have two copies. `/clear-answer:on` tells you
when this happens, and how to remove one copy.

## The API

Upload the same zip with the Skills API, and turn on the code execution tool.
See the [Skills guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide).

To build the zip yourself, see [tutorial 9](09-build-and-update.md).

Next: [7. Team rules and automatic checks](07-team-and-checks.md).
