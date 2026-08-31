# 4. Rewrite a document

`/clear-answer:rewrite` turns text into short, plain English and shows a before and
after. Use it to fix a draft, not just to find problems.

## Steps

1. Point at the sample file, or paste your own text:
   ```
   /clear-answer:rewrite docs/tutorials/examples/sample-procedure.md
   ```
2. Claude rewrites the text, checks the result with the linter, and shows both
   versions.
3. Review the after. Keep any term you must not change.

## Worked example

Before:

> The technician should utilize the diagnostic tool in order to ascertain whether
> the primary hydraulic pump is functioning correctly, and it is recommended that
> the system is checked prior to each flight.
>
> Don't remove the pump before the system is depressurized.
>
> Open the access panel and remove the four bolts.

After (Clear Answer, strict profile):

> Use the diagnostic tool to check the primary hydraulic pump. Do this check
> before each flight.
>
> Depressurize the system. Remove the pump.
>
> Open the access panel. Remove the four bolts.

## Why the after passes

- Long sentences are split. Each one is 20 words or fewer.
- "utilize" becomes "use". "in order to" becomes "to". "prior to" becomes
  "before".
- The compound tense "is functioning" becomes the simple verb "check".
- The contraction "don't" becomes "do not", and the passive is removed:
  "Depressurize the system."
- The joined step "Open ... and remove ..." becomes two sentences.

Confirm it yourself:

```bash
python3 scripts/ste_lint.py --profile full --text "Use the diagnostic tool to check the primary hydraulic pump. Do this check before each flight. Depressurize the system. Remove the pump. Open the access panel. Remove the four bolts."
```

The result is `"passed": true`.
