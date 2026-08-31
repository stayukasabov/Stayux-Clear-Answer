# 5. Set up a repo, and use Clear Answer on Desktop

## Add the Clear Answer rules to a repo

`/clear-answer:init` writes a short rules section into the project's CLAUDE.md, so every
session in that repo writes to the standard.

1. Open Claude Code in the repo.
2. Run:
   ```
   /clear-answer:init
   ```
3. Claude adds or updates a "Clear Answer (plain-English rules)" section in
   `CLAUDE.md`, then shows you what it added.
4. Commit the change so your team shares it.

## Use Clear Answer on Claude Desktop

The plugin commands are for Claude Code. On Claude Desktop and through the API,
Clear Answer ships as an uploaded skill. This suits technical writers, designers,
and project managers, who usually work in Desktop.

1. Build the upload bundle from the repo root:
   ```bash
   bash build-desktop-skill.sh
   ```
   This writes `dist/stayux-clear-answer.zip`.
2. Upload `dist/stayux-clear-answer.zip` as a custom skill. See
   [`desktop/README.md`](../../desktop/README.md) for the upload flow.
3. In a chat, ask Claude for a clear answer, for example "reply in plain English"
   or "rewrite this in Simplified Technical English".
4. Turn it off with words when you are done, for example "clear answer off" or
   "reply in normal prose". Desktop has no slash commands, so you turn the mode
   on and off by asking.

See [`desktop/README.md`](../../desktop/README.md) for the full Desktop and API
notes.
