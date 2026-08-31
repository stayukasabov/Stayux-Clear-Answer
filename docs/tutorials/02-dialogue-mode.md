# 2. Get clear answers in the dialogue

Use Clear Answer mode to make Claude reply in short, clear, controlled English.
Claude drafts each reply, checks it with the linter, and rewrites until it passes.

## Steps

1. Turn the mode on:
   ```
   /clear-on
   ```
2. Ask a normal question, for example: "How do I restart the service after a
   config change?"
3. Claude replies with short sentences, active voice, and one instruction each.
4. For strict, document-style output (sentences of 20 words or fewer), use:
   ```
   /clear-mode strict
   ```
5. Turn the mode off to return to normal prose:
   ```
   /clear-off
   ```

## Before and after

The same answer, mode off then on.

Off (normal prose):

> Intermittent 502s just after a deploy usually mean traffic reaches new
> instances before they are ready to serve it, so I would start with the
> readiness probes and whether they reflect real readiness, and also check that
> the load balancer drains old connections during the rollout.

On (Clear Answer):

> Check three things.
> 1. Readiness probes. Confirm they pass only when the app can serve requests.
> 2. Connection draining. Make sure the load balancer removes old pods first.
> 3. Deploy timing. Read the logs from the first 30 seconds after each rollout.

## Notes

- The mode is sticky. It stays on across turns until you run `/clear-off` or
  `/clear-mode off`.
- `prose` uses the chat profile (25 words). `strict` uses the full profile (20
  words).
- Clear Answer mode is a rewrite-only guard. Claude does not show you the linter
  output, only the final compliant reply.
