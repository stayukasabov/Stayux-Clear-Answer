A 502 right after a deploy usually means the proxy cannot get to a healthy backend. Look at these items in sequence.

1. **Readiness.** Make sure the load balancer sends traffic only after the new instance is prepared. A missing or weak readiness probe is the most frequent cause.
2. **Startup time.** Compare the app start time with the probe interval. If the probe passes before the app can serve, requests fail.
3. **Shutdown.** Make sure the previous instance stops cleanly. It must complete open requests before it exits. Add a graceful shutdown with a SIGTERM handler.
4. **Connection draining.** Make sure the load balancer stops new traffic to the previous instance before it kills it. Set a drain time that is longer than your longest call.
5. **Keep-alive timeouts.** The backend idle timeout must be longer than the proxy idle timeout. If not, the proxy reuses a closed connection and gets a 502.
6. **Crashes.** Read the logs from the new instance. A crash on boot, a bad config, or a database migration that did not work will give 502 errors.
7. **Resources.** Examine memory and CPU limits at start. A killed process (OOM) gives 502.
8. **Proxy logs.** Read the error record of the proxy or load balancer. It states the cause, such as connection refused, connection reset, or upstream timeout.

Use this quick test. If the errors stop after a few seconds, the cause is probably readiness or draining. If the errors continue until you start the service again, the cause is probably a crash or a bad config.
