502s right after a deploy almost always mean the proxy or load balancer is sending traffic to an instance that isn't ready, or is killing one that's still serving. In rough order of likelihood:

**1. Readiness: traffic hits the new instance before it can serve**
- Does the health check actually verify the app is ready (DB connected, caches warmed), or just that the process is up?
- Is the readiness probe or LB health check passing before the instance is registered? Look at `initialDelaySeconds`, healthy-threshold counts, and registration delay.
- Slow startup (migrations, JIT warmup, big imports) combined with an optimistic health check is the classic cause.

**2. Graceful shutdown: old instances die with in-flight requests**
- Does the app handle SIGTERM by stopping accepting new connections, finishing in-flight ones, then exiting?
- Is the termination grace period longer than your longest request?
- Is deregistration from the LB happening *before* the process stops? On Kubernetes, add a `preStop` sleep (5-15s) because endpoint removal propagates asynchronously.

**3. Keep-alive timeout mismatch**
- If the upstream (nginx/ALB/ELB) keep-alive idle timeout is longer than the app's, the app closes a connection the proxy thinks is still open, giving a 502. The app's keep-alive timeout should be *greater* than the LB's (e.g., Node's `keepAliveTimeout` > ALB's 60s).
- This tends to show up as sporadic 502s, and deploys make it more visible because connections are being churned.

**4. Stale upstream targets**
- nginx resolves upstream DNS once at startup and caches it; after a deploy the IPs change and it hits dead ones. Check for `resolver` and variable-based `proxy_pass`.
- Same for any service mesh or sidecar that's slow to pick up new endpoints.

**5. Rollout strategy**
- Is `maxUnavailable` too high, or are you replacing all instances at once? Use `maxUnavailable: 0` / `maxSurge: 1` or similar so capacity never drops.
- Check that the new version isn't crash-looping briefly (OOM, missing env var/secret) and then recovering.

**How to tell which one it is**
- Check the proxy/LB error log at the 502 timestamps. Messages like `upstream prematurely closed connection`, `connection refused`, or `connection reset by peer` point to different causes: refused → not ready yet, reset/premature close → shutdown or keep-alive.
- Correlate the 502 timestamps with instance start and stop events. 502s clustered at start suggest readiness, and at stop suggest graceful shutdown. Scattered ones suggest keep-alive.
- On AWS, compare `HTTPCode_ELB_502_Count` vs `HTTPCode_Target_5XX_Count`. ELB-generated 502s mean the target broke the connection.

If you tell me your stack (k8s, ECS, nginx in front, ALB, etc.) I can narrow this down, and I can look at your deploy config if it's in this directory.
