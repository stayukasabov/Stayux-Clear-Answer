# 9. Build and update

For the maintainers of Clear Answer: run the tests, build the Desktop skill, and
release a version.

## Run the tests

```bash
python3 -m unittest discover -s tests
```

Run them two times: with your official cache (`cache/official.json`), and once
with the `cache` folder moved away. Users who clone the repository have no
cache, so the tests must pass both ways.

## Build the Desktop skill

```bash
bash build-desktop-skill.sh
```

This writes `dist/stayux-clear-answer.zip`, with these files at its root:

```
SKILL.md
ste_lint.py
ste_dictionary.py
ste_pos.py
writing-rules.md
```

Upload the zip as a custom skill to test it (see [tutorial 6](06-desktop.md)).

## Import your official dictionary again

After a change to the importer, import your copy again:

```bash
python3 scripts/ste_import.py path/to/your-ste100.pdf
```

## Release a version

1. Change the version in `.claude-plugin/plugin.json`,
   `.claude-plugin/marketplace.json`, and `pyproject.toml`.
2. Run the tests and build the zip.
3. Commit, and push to GitHub. Users of the GitHub marketplace get the update
   with `/plugin update clear-answer`.
4. Attach `dist/stayux-clear-answer.zip` to a GitHub release.
5. To update the listing in the Anthropic Directory, submit the new version at
   [platform.claude.com/plugins/submissions](https://platform.claude.com/plugins/submissions).
   The listing changes after review.

## Measure the effect

`scripts/bench.py` runs tasks with Clear Answer off and on through `claude -p`.
Each run uses your Claude plan. See the [benchmark pilot](../benchmark.md) for
the method and the first results.
