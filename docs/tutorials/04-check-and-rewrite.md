# 4. Check and rewrite a document

`/clear-answer:check` reports the problems in a document and changes nothing.
`/clear-answer:rewrite` rewrites the document and shows the before and after.

## The sample

[`examples/sample-procedure.md`](examples/sample-procedure.md) is a short draft
that is not clear:

> The technician should utilize the diagnostic tool in order to ascertain whether
> the primary hydraulic pump is functioning correctly, and it is recommended that
> the system is checked prior to each flight.
>
> Don't remove the pump before the system is depressurized.
>
> Open the access panel and remove the four bolts.

## Check it

```
/clear-answer:check docs/tutorials/examples/sample-procedure.md
```

The linter finds these problems with the strict profile:

```
3: error: sentence-length, 32 words (max 20)
3: warning: unapproved-word, use 'use' instead of 'utilize'
3: warning: unapproved-word, use 'make sure' instead of 'ascertain'
3: error: progressive-tense, 'is functioning' is a compound tense
3: warning: passive-voice, 'is recommended' is passive voice
3: warning: passive-voice, 'is checked' is passive voice
3: warning: unapproved-word, use 'before' instead of 'prior to'
3: warning: wordiness, 'in order to' is wordy: use 'to'
5: error: contraction, use 'do not' instead of 'don't'
5: warning: passive-voice, 'is depressurized' is passive voice
7: warning: one-instruction, one instruction per sentence: split the joined steps
```

An error must be fixed. A warning is advice.

## Rewrite it

```
/clear-answer:rewrite docs/tutorials/examples/sample-procedure.md
```

A real run with Claude Sonnet gave this result, which passes the strict profile:

> Use the diagnostic tool to find if the primary hydraulic pump operates
> correctly. Examine the system before each flight.
>
> Do not remove the pump until you release the pressure in the system.
>
> Open the access panel. Remove the four bolts.

What changed:

- The 32-word sentence is now two short sentences.
- "utilize" is now "use", and "in order to ascertain" is now "to find".
- "is functioning" is now "operates", and "prior to" is now "before".
- "it is recommended that the system is checked" is now the command "Examine the
  system".
- "Don't" is now "Do not".
- "Open ... and remove ..." is now two commands.

## Run the linter yourself

The linter is a plain Python script. From the repository folder:

```bash
python3 scripts/ste_lint.py --profile full --pretty < docs/tutorials/examples/sample-procedure.md
```

It prints the result as JSON. It exits with 1 when it finds an error, so you
can use it in scripts (see [tutorial 7](07-team-and-checks.md)).

Next: [5. Dictionaries](05-dictionaries.md).
