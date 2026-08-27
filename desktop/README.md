# Stayux-STE-linter for Claude Desktop and the API

The same STE writing guard as the Claude Code skill, packaged so it runs in
Claude Desktop and through the API. It suits the whole technical-documentation
process, not only engineers: technical writers, designers, and project managers
who want compact, clear output from Claude.

## What it does

It makes Claude write in Simplified Technical English (STE), a controlled-English
standard for short, exact, unambiguous text. Claude drafts a reply, checks it
against a bundled Python linter (the pass/fail gate), and rewrites until it
passes. See the [main README](../README.md) for the token economy and the rule
set.

## How it differs from the Claude Code version

- **Activation.** Claude Code uses the plugin commands (`/ste-on`, `/ste-off`, `/ste-check`, `/ste-rewrite`, `/ste-init`, `/ste-mode`).
  Here you turn it on by asking: "reply in STE", "use Simplified Technical
  English", or "STE on". It is off until you ask.
- **Packaging.** Claude Code loads the skill from a local folder. Desktop and the
  API load an uploaded skill that runs in a code-execution container, so the
  files are bundled flat and the linter runs inside that sandbox.
- **No install on the machine.** The linter is zero-dependency stdlib Python, so
  the sandbox runs it with no setup.

## Use it (end users)

1. Add the skill to your workspace (see "Build and upload" below, or use a
   prepared `stayux-ste.zip`).
2. In a chat, ask Claude to reply in STE. Ask for the "full" profile when you
   want strict document style (sentences of 20 words or fewer).
3. Continue as normal. Claude keeps replies in STE until you ask for normal
   prose again.

## Build and upload (maintainers)

From the repository root, assemble the flat upload bundle:

```bash
bash build-desktop-skill.sh
# writes dist/stayux-ste/ and dist/stayux-ste.zip
```

The bundle is flat, as the container expects:

```
stayux-ste/
├── SKILL.md
├── ste_lint.py
├── ste_dictionary.py
└── writing-rules.md
```

Upload `dist/stayux-ste.zip` as a custom skill (via the API `/v1/skills` endpoint or
your workspace skill settings), then attach it to the model as documented in the
[Skills guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide).
Skills require the code execution tool.

## Before and after

The same question, answered with the skill off (normal prose) and on.

**You:** The API returns 502 sometimes right after a deploy. What should I check?

**STE off (default):**

> Intermittent 502s just after a deploy usually mean traffic reaches new
> instances before they are ready to serve it, so the first thing I would look
> at is your readiness checks and whether they genuinely reflect when the app
> can handle requests. Beyond that, it is worth confirming that the load balancer
> drains connections from the old instances gracefully during the rollout.

**STE on:**

> Check three things.
> 1. Readiness probes. Confirm they pass only when the app can serve requests.
> 2. Connection draining. Make sure the load balancer removes old pods before it stops them.
> 3. Deploy timing. Look at the logs from the first 30 seconds after each rollout.

Same information. The STE reply is shorter, scannable, and faster to act on.

## License

[MIT](../LICENSE). See [NOTICE](../NOTICE) for trademark and copyright terms.
"Simplified Technical English" and "ASD-STE100" are trademarks of ASD. This tool
does not include or download ASD's copyrighted dictionary.
