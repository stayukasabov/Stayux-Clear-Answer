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
cp "$ROOT/scripts/ste_pos.py"         "$OUT/ste_pos.py"
cp "$ROOT/references/writing-rules.md" "$OUT/writing-rules.md"
cp "$ROOT/commands/explain.md"        "$OUT/explain.md"
cp "$ROOT/scripts/explain_page.py"    "$OUT/explain_page.py"
cp "$ROOT/templates/explain-page.html" "$OUT/explain-page.html"
cp "$ROOT/templates/explain-footer.md" "$OUT/explain-footer.md"

( cd "$ROOT/dist" && rm -f stayux-clear-answer.zip && zip -r -q stayux-clear-answer.zip stayux-clear-answer )

echo "Built:"
echo "  $OUT"
echo "  $ROOT/dist/stayux-clear-answer.zip"
