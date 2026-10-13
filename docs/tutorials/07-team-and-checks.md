# 7. Team rules and automatic checks

Clear Answer can make a whole team write the same way. Put the rules in the
project, and check every document before it gets into the repository.

## Share the rules

```
/clear-answer:init
```

Claude adds a "Clear Answer" section to the project's `CLAUDE.md`. Commit it.
Then every Claude Code session in the project writes to the same rules.

## Get the linter

The commit hook and the CI step call the linter from a fixed folder:

```bash
git clone https://github.com/stayukasabov/Stayux-Clear-Answer ~/.clear-answer
```

## Check each commit

This Git hook stops a commit when a Markdown file in it has an error. Save it as
`.git/hooks/pre-commit`, then run `chmod +x .git/hooks/pre-commit`:

```sh
#!/bin/sh
# Clear Answer: check the Markdown files in this commit.
LINT="$HOME/.clear-answer/scripts/ste_lint.py"
status=0
git diff --cached --name-only --diff-filter=ACM -- '*.md' | while IFS= read -r file; do
  if ! python3 "$LINT" --profile full < "$file" > /dev/null; then
    echo "Clear Answer: $file has errors. See: python3 $LINT --profile full --pretty < \"$file\""
    exit 1
  fi
done || status=1
exit $status
```

The hook was tested: it lets clear files through, including names with spaces,
and it stops a file with errors. Warnings do not stop a commit.

## Check in CI

Add this step to a CI job, for example in GitHub Actions. It fails the job when
a document has an error:

```yaml
- name: Clear Answer
  run: |
    git clone --depth 1 https://github.com/stayukasabov/Stayux-Clear-Answer /tmp/clear-answer
    failed=0
    for f in docs/*.md; do
      python3 /tmp/clear-answer/scripts/ste_lint.py --profile full < "$f" > /dev/null || { echo "::error file=$f::Clear Answer errors in $f"; failed=1; }
    done
    exit $failed
```

Change `docs/*.md` to the files of your project. The loop was tested in bash.
The full workflow was not run in GitHub Actions.

## Use your own words

Put your project words in a `.ste-dict.txt` file at the root of the repository
(see [tutorial 5](05-dictionaries.md)). The hook and the CI step read it when
they run from that folder.

Next: [8. Other agents](08-other-agents.md).
