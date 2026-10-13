# 1. Install

Clear Answer installs as a Claude Code plugin. The repository is also its own
plugin marketplace.

## Claude Code

1. Open Claude Code.
2. Add the marketplace and install the plugin:
   ```
   /plugin marketplace add stayukasabov/Stayux-Clear-Answer
   /plugin install clear-answer@stayux-clear
   ```
3. Start a new session. Type `/clear-answer:` and look for `explain`, `on`,
   `off`, `mode`, `check`, `rewrite`, and `init`.

The linter needs Python 3.9 or later:

```bash
python3 --version
```

## Update

```
/plugin update clear-answer
```

Then start a new session. A session that is open keeps the old command text.

## Use a local copy

To try a local copy of the repository, add the folder as the marketplace:

```
/plugin marketplace add /path/to/Stayux-Clear-Answer
/plugin install clear-answer@stayux-clear
```

## Claude Desktop and claude.ai

See [tutorial 6](06-desktop.md).

Next: [2. Explain a topic](02-explain.md).
