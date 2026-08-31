#!/usr/bin/env bash
# Build the Claude Desktop / API upload bundle for the STE skill.
#
# The linter stays single-source in scripts/. This script only assembles a
# flat, self-contained skill directory (SKILL.md plus helper files at the root,
# the layout the code-execution container expects) and zips it for upload.
#
# Usage:
#   bash build-desktop-skill.sh
# Output:
#   dist/stayux-clear-answer/       the unpacked bundle
#   dist/stayux-clear-answer.zip    the archive to upload as a custom skill

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$ROOT/dist/stayux-clear-answer"

rm -rf "$OUT"
mkdir -p "$OUT"

cp "$ROOT/desktop/SKILL.md"            "$OUT/SKILL.md"
cp "$ROOT/scripts/ste_lint.py"        "$OUT/ste_lint.py"
cp "$ROOT/scripts/ste_dictionary.py"  "$OUT/ste_dictionary.py"
cp "$ROOT/references/writing-rules.md" "$OUT/writing-rules.md"

( cd "$ROOT/dist" && rm -f stayux-clear-answer.zip && zip -r -q stayux-clear-answer.zip stayux-clear-answer )

echo "Built:"
echo "  $OUT"
echo "  $ROOT/dist/stayux-clear-answer.zip"
