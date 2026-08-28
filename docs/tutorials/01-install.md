# 1. Install the plugin

Stayux-STE-linter installs as a Claude Code plugin. The repo is also its own
plugin marketplace.

## Steps

1. Open Claude Code.
2. Add the marketplace:
   ```
   /plugin marketplace add stayukasabov/Stayux-STE-linter
   ```
3. Install the plugin:
   ```
   /plugin install stayux-ste@stayux
   ```
4. Confirm the commands are available. Type `/ste-` and look for `ste-on`,
   `ste-off`, `ste-mode`, `ste-check`, `ste-rewrite`, and `ste-init`.

## Local install (for development)

To test a local checkout instead of the GitHub copy, point the marketplace at the
folder:

```
/plugin marketplace add /path/to/Stayux-STE-linter
/plugin install stayux-ste@stayux
```

## Update later

When a new version ships, refresh the plugin:

```
/plugin update stayux-ste
```

Restart Claude Code to apply the update. From a terminal you can also run
`claude plugin update stayux-ste`.

## Check your Python

The checker runs with the code execution tool and needs Python 3.9 or later. From
a terminal:

```bash
python3 --version
```

You are ready. Go to [02-dialogue-mode](02-dialogue-mode.md).
