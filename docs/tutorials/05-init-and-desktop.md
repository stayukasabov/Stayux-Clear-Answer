# 5. Set up a repo, and use STE on Desktop

## Add STE rules to a repo

`/ste-init` writes a short STE section into the project's CLAUDE.md, so every
session in that repo writes to the standard.

1. Open Claude Code in the repo.
2. Run:
   ```
   /ste-init
   ```
3. Claude adds or updates a "Simplified Technical English (STE)" section in
   `CLAUDE.md`, then shows you what it added.
4. Commit the change so your team shares it.

## Use STE on Claude Desktop

The plugin commands are for Claude Code. On Claude Desktop and through the API,
STE ships as an uploaded skill. This suits technical writers, designers, and
project managers, who usually work in Desktop.

1. Build the upload bundle from the repo root:
   ```bash
   bash build-desktop-skill.sh
   ```
   This writes `dist/stayux-ste.zip`.
2. Upload `dist/stayux-ste.zip` as a custom skill. See
   [`desktop/README.md`](../../desktop/README.md) for the upload flow.
3. In a chat, ask Claude to reply in STE, for example "reply in STE" or "rewrite
   this in Simplified Technical English".

See [`desktop/README.md`](../../desktop/README.md) for the full Desktop and API
notes.
