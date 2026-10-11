#!/usr/bin/env python3
"""Find a second copy of the Clear Answer skill synced from claude.ai.

A user who adds the plugin and also has the skill from the Anthropic Directory
(or an uploaded Desktop build) gets two copies in Claude Code. claude.ai syncs
skills to ~/.claude/skills/synced/<account>/<skill>/SKILL.md.

Usage:
    python3 ste_dupcheck.py [--skills-dir DIR]

Prints a message if a copy is found, and nothing otherwise. Always exits 0.
"""
import argparse
import os
import re
import sys

DEFAULT_SYNCED_DIR = os.path.join(os.path.expanduser("~"), ".claude", "skills", "synced")

# Current skill names and the names from before the rebrand.
SKILL_NAMES = {"stayux-clear-answer", "clear-write", "stayux-ste", "ste-write"}

NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.MULTILINE)


def _skill_name(path):
    try:
        with open(path) as f:
            head = f.read(2000)
    except OSError:
        return None
    if not head.startswith("---"):
        return None
    m = NAME_RE.search(head.split("---", 2)[1])
    return m.group(1) if m else None


def find_duplicates(skills_dir=DEFAULT_SYNCED_DIR):
    """Return the SKILL.md paths of synced Clear Answer copies, sorted."""
    found = []
    if not os.path.isdir(skills_dir):
        return found
    for account in sorted(os.listdir(skills_dir)):
        account_dir = os.path.join(skills_dir, account)
        if account.startswith(".") or not os.path.isdir(account_dir):
            continue
        for skill in sorted(os.listdir(account_dir)):
            path = os.path.join(account_dir, skill, "SKILL.md")
            if not skill.startswith(".") and _skill_name(path) in SKILL_NAMES:
                found.append(path)
    return found


def message(paths):
    if not paths:
        return ""
    lines = ["Clear Answer is installed twice. This session uses the plugin copy.",
             "Another copy is synced from claude.ai:"]
    lines += [f"  {p}" for p in paths]
    lines += ["The two copies can have different versions and rules. Keep one:",
              "- To keep the plugin, remove the Clear Answer skill in claude.ai, "
              "in your skills settings.",
              "- To keep the synced skill, run /plugin uninstall clear-answer."]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Find a duplicate Clear Answer skill")
    ap.add_argument("--skills-dir", default=DEFAULT_SYNCED_DIR)
    args = ap.parse_args(argv)
    text = message(find_duplicates(args.skills_dir))
    if text:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
