# 5. Dictionaries

The linter checks words against three layers. Each layer overrides the layer
before it:

1. The built-in word list. It is small, and it ships with the plugin.
2. Your own copy of the official ASD-STE100 dictionary, if you import it.
3. Your project words, in a `.ste-dict.txt` file.

Each entry can name a part of speech, as the standard does. So "file (v)" warns
on "file the edge" but not on "open the file".

## Your project words

Put a `.ste-dict.txt` file in the root of your project. The linter reads it
automatically.

```
# Acme terms. A hash starts a comment.
bolt = fastener      # warn on "bolt", and suggest "fastener"
as per = by          # a phrase on the left is a phrase swap
assist               # a word alone is approved: never warn on it
file (v) = remove    # warn on "file" only as a verb
file (n)             # approve "file" only as a noun
```

Use `n`, `v`, `adj`, or `adv` for the part of speech.

Example with the sentence "Assist the operator to install the bolt.":

- Without the file: `warning: unapproved-word, use 'help' instead of 'assist'`
- With the file: `warning: unapproved-word, use 'fastener' instead of 'bolt'`

## Your official dictionary

The official ASD-STE100 dictionary is copyrighted, so the plugin does not ship
it. If you have your own copy as a PDF, import it once:

```bash
python3 scripts/ste_import.py path/to/your-ste100.pdf
```

This writes `cache/official.json` on your computer. Git ignores it, so it is
never shared. The import needs `pdftotext` (from Poppler) for a PDF. You can
also give it a text file.

The import keeps each entry's part of speech and every approved alternative.
For example, "check" as a verb gets this advice:
`use 'make sure' or 'measure' or 'examine'`. The import reads only the
dictionary entries, not the change log or the summary tables of the PDF.

Import your copy again after an update of the plugin. An older cache still
works, but it can give less precise advice.

## What the linter cannot know

The dictionary also gives each approved word one meaning. For example,
"follow" means "come after", not "obey". The linter checks the word and its part
of speech, but not its meaning.

Next: [6. Claude Desktop and the API](06-desktop.md).
