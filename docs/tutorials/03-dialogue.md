# 3. Clear answers in the dialogue

`/clear-answer:on` makes every reply plain English, checked by the linter, until
you turn it off.

## Steps

1. Turn the mode on:
   ```
   /clear-answer:on
   ```
2. Ask your questions as usual.
3. For manuals and procedures, use the strict profile (sentences of 20 words or
   fewer):
   ```
   /clear-answer:mode strict
   ```
4. Turn the mode off:
   ```
   /clear-answer:off
   ```

The mode stays on across turns. Claude does not show you the linter output,
only the final reply.

## Before and after

Real replies from Claude Sonnet to the same question: "The API returns 502
sometimes right after a deploy. What should I check?"

**Off:** 443 words, in sections with bold labels and long sentences. The full
reply is in [`examples/dialogue-502-off.md`](examples/dialogue-502-off.md).

**On:** 262 words. The first part:

> A 502 right after a deploy usually means the proxy cannot get to a healthy
> backend. Look at these items in sequence.
>
> 1. **Readiness.** Make sure the load balancer sends traffic only after the new
>    instance is prepared. A missing or weak readiness probe is the most
>    frequent cause.
> 2. **Startup time.** Compare the app start time with the probe interval. If the
>    probe passes before the app can serve, requests fail.

The full reply is in [`examples/dialogue-502-on.md`](examples/dialogue-502-on.md).

## The cost

The checked reply used 1,640 output tokens, against 1,082 without the check.
Claude writes a draft for the linter and then the final text. You pay that in
tokens, and the reader gets a shorter text with one step on each line.

## Clear Answer is a translation, not a summary

The mode changes the sentences, not the content. If a reply seems to leave out
facts that you need, ask for them. The skill tells Claude to keep every fact,
step, and warning.

Next: [4. Check and rewrite a document](04-check-and-rewrite.md).
