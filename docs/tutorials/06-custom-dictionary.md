# 6. Add your own words with a project dictionary

The standard lets a company add its own approved technical terms. You do the
same here with a plain **`.ste-dict.txt`** file in your project. The linter reads
it automatically, no code edit and no dependency.

## The file format

One rule per line:

```
# comments start with a hash; blank lines are ignored
bolt = fastener      # flag "bolt", suggest "fastener"
as per = by          # a multiword left side is a phrase swap
widget               # a bare word is approved: never flag it
+gizmo               # a leading + is allowed and means the same
```

- `term = replacement` adds a substitution. A single word goes to the word list;
  a multiword term goes to the phrase list.
- A bare word marks it **approved**, so the linter stops flagging it. Use this for
  house-style words you want to keep.
- Custom entries win over the built-in seed and any imported official cache.

## Worked example

Put this in `.ste-dict.txt` at your project root:

```
# Acme terms
bolt = fastener      # our part name
assist               # house style keeps "assist"
```

Check this sentence:

```
Assist the operator to install the bolt.
```

Without the file, the seed flags `assist`:

```
1: warning: unapproved-word, use 'help' instead of 'assist'
```

With the file, `assist` is left alone and `bolt` is flagged with your swap:

```
1: warning: unapproved-word, use 'fastener' instead of 'bolt'
```

## Run it without Claude

The checker picks up `.ste-dict.txt` from the working directory. From a folder
that has one:

```bash
echo "Assist the operator to install the bolt." | python3 scripts/ste_lint.py --profile full --pretty
```

## Where this sits

Three layers stack, most specific last: the built-in seed, an imported official
cache (see [the dictionary section of the README](../../README.md#the-dictionary)),
and your `.ste-dict.txt`. Your file has the final say.
