# Tutorials

Step-by-step guides for Stayux-STE-linter. Each one is short and has a worked
example you can run.

## Before you start

- Claude Code with the plugin installed. See [01-install](01-install.md).
- Python 3.9 or later on your PATH. The checker uses the standard library only.

## The tutorials

1. [Install the plugin](01-install.md)
2. [Write in STE in the dialogue](02-dialogue-mode.md)
3. [Check a document](03-check-a-document.md)
4. [Rewrite a document](04-rewrite-a-document.md)
5. [Set up a repo, and use STE on Desktop](05-init-and-desktop.md)

## Example file

[`examples/sample-procedure.md`](examples/sample-procedure.md) is a short, non-STE
draft. Tutorials 3 and 4 use it.

## The commands, at a glance

- `/ste-on`, `/ste-off`: turn STE dialogue mode on or off.
- `/ste-mode off|prose|strict`: set the strictness.
- `/ste-check`: check a file or text and report the violations.
- `/ste-rewrite`: rewrite text into STE with a before and after.
- `/ste-init`: add STE rules to the project's CLAUDE.md.
