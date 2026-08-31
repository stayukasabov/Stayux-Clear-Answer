# 3. Check a document

`/clear-answer:check` runs the linter on a file or pasted text and reports the problems. It
does not rewrite. Use it to audit documentation.

## Steps

1. Use the sample file at
   [`examples/sample-procedure.md`](examples/sample-procedure.md), or point at
   your own `.md` or `.txt`.
2. Run the check:
   ```
   /clear-answer:check docs/tutorials/examples/sample-procedure.md
   ```
3. Read the report. Each line is `line: severity: rule, detail`. Errors fail the
   gate; warnings are advisory.

## What you get

The sample produces this, on the strict profile:

```
3: error: sentence-length, 32 words (max 20)
3: warning: unapproved-word, use 'use' instead of 'utilize'
3: warning: unapproved-word, use 'check' instead of 'ascertain'
3: error: progressive-tense, 'is functioning' is a compound tense
3: warning: passive-voice, 'is recommended' is passive voice
3: warning: passive-voice, 'is checked' is passive voice
3: warning: unapproved-word, use 'to' instead of 'in order to'
3: warning: unapproved-word, use 'before' instead of 'prior to'
5: error: contraction, use 'do not' instead of 'don't'
5: warning: passive-voice, 'is depressurized' is passive voice
7: warning: one-instruction, one instruction per sentence: split the joined steps
```

## Read it

- Line 3 is one 32-word sentence with a compound tense. Split it and use simple
  verbs.
- Line 5 has a contraction. Write "do not".
- Line 7 joins two steps with "and". Make two sentences.

## Run it without Claude

The checker is a plain script. From the repo root:

```bash
python3 scripts/ste_lint.py --profile full --pretty < docs/tutorials/examples/sample-procedure.md
```

It prints JSON and exits 1 when any error is present. Next, fix these problems in
[04-rewrite-a-document](04-rewrite-a-document.md).
