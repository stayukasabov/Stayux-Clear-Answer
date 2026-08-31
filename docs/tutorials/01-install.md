# 1. Install the plugin

Stayux Clear Answer installs as a Claude Code plugin. The repo is also its own
plugin marketplace.

## Steps

1. Open Claude Code.
2. Add the marketplace:
   ```
   /plugin marketplace add stayukasabov/Stayux-Clear-Answer
   ```
3. Install the plugin:
   ```
   /plugin install clear-answer@stayux
   ```
4. Confirm the commands are available. Type `/clear-answer:` and look for `on`,
   `off`, `mode`, `check`, `rewrite`, and `init`.

## Local install (for development)

To test a local checkout instead of the GitHub copy, point the marketplace at the
folder:

```
/plugin marketplace add /path/to/Stayux-Clear-Answer
/plugin install clear-answer@stayux
```

## Update later

When a new version ships, refresh the plugin:

```
/plugin update clear-answer
```

Restart Claude Code to apply the update. From a terminal you can also run
`claude plugin update clear-answer`.

## Check your Python

The checker runs with the code execution tool and needs Python 3.9 or later. From
a terminal:

```bash
python3 --version
```

You are ready. Go to [02-dialogue-mode](02-dialogue-mode.md).
