# Tutorials

Step-by-step guides for Stayux Clear Answer. Each one is short and has a worked
example you can run.

## Before you start

- Claude Code with the plugin installed. See [01-install](01-install.md).
- Python 3.9 or later on your PATH. The checker uses the standard library only.

## The tutorials

1. [Install the plugin](01-install.md)
2. [Get clear answers in the dialogue](02-dialogue-mode.md)
3. [Check a document](03-check-a-document.md)
4. [Rewrite a document](04-rewrite-a-document.md)
5. [Set up a repo, and use Clear Answer on Desktop](05-init-and-desktop.md)
6. [Add your own words with a project dictionary](06-custom-dictionary.md)

## Example file

[`examples/sample-procedure.md`](examples/sample-procedure.md) is a short, unclear
draft. Tutorials 3 and 4 use it.

## The commands, at a glance

Each command has a legacy `/ste-*` alias that does the same thing.

- `/clear-on`, `/clear-off`: turn Clear Answer dialogue mode on or off.
- `/clear-mode off|prose|strict`: set the strictness.
- `/clear-check`: check a file or text and report the violations.
- `/clear-rewrite`: rewrite text into plain English with a before and after.
- `/clear-init`: add the rules to the project's CLAUDE.md.
