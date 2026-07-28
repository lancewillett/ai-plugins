# Failure classification taxonomy

Use a label with a domain, mechanism, and scope when evidence permits. Add `Intermittent` only when comparable runs show the same signature both passing and failing. Omit it for a one-off failure. Prefer the exact observed signature over a broad category.

| Domain | Mechanisms to use when supported |
| --- | --- |
| Test design | Brittle selector; outdated assertion; fixed wait; unstable fixture; excess E2E scope |
| Product behavior | Race; unobservable async state; auth/session loss; session/shared-state collision; cache inconsistency; route/404; data readiness |
| Test environment | Database/service startup; container/VM; missing config; tunnel/site URL mismatch; browser/runtime mismatch; resource exhaustion |
| Network/dependencies | DNS/connectivity; request timeout; third-party unavailable; auth-provider failure; outage |
| CI orchestration | Merge-queue-only; parallel-worker collision; scheduler/queue; PR-only alert noise; artifact/setup |
| Platform/runtime | CPU/memory; OS/library version; animation/GPU timing; clock/time-zone |
| Build/deploy/config | Dependency resolution; artifact; deploy/restart; config drift |
| Security/policy | Vulnerability/advisory gate; scanner finding; permission/policy rejection; secret-scanning match; integrity/signature failure |
| Unknown | Use only when the available evidence cannot support a domain or mechanism |

Use Security/policy only when a security or policy mechanism causes the failure. A security test can expose a product, environment, dependency, CI, runtime, or configuration failure; classify that actual cause instead.

## Classification examples

| Observed evidence | Label | Next evidence or action |
| --- | --- | --- |
| Comparable runs use the same revision, configuration, and runner image; MySQL reaches health in some and exits before health in others. The security suite never starts in failed runs. | Intermittent test environment—database startup failure: MySQL container did not become healthy | Preserve container startup logs and exit code. |
| The same login test fails only when another worker uses the account. | Product behavior—session/shared-state collision: parallel workers reuse one account | Give each worker an isolated account or session. |
| A visible-text locator fails after copy changes while the control still exists. | Test design—brittle selector failure: visible-text lookup no longer matches the control | Select a stable role, label, or test identifier. |
| A request redirects to login during a previously authenticated flow. | Product behavior—auth/session loss: authenticated request redirects to login | Capture cookies, redirect chain, and session expiry details. |
| A browser reaches a local hostname that does not resolve through the test tunnel. | Test environment—tunnel/site URL mismatch: browser cannot reach the configured site URL | Compare browser-visible URL and tunnel configuration. |
| Comparable runs send the same request to the same dependency; some complete and others exceed the timeout without a response. | Intermittent network/dependencies—request timeout: API did not respond within 30 seconds | Capture request timing, dependency status, and correlation ID. |
| A test waits a fixed 500 ms before asserting background work completed. | Test design—fixed-wait failure: assertion races background work | Wait for an observable completion signal. |
| Publishing succeeds but the asserted URL returns 404 before routing completes. | Product behavior—route/404 failure: published route is unavailable | Trace publish and route readiness events. |
| The assertion runs before the fixture record appears in the queried service. | Product behavior—data readiness failure: fixture is not visible when asserted | Record fixture creation and read-after-write timing. |
| A screenshot comparison changes during a transition on one runtime. | Platform/runtime—animation/GPU timing failure: screenshot captured during transition | Disable motion or wait for a stable visual state. |
| Failures cluster when several child builds share a constrained runner. | CI orchestration—parallel-worker collision: workers contend for runner capacity | Compare worker assignment and resource metrics. |
| A dependency scan blocks a build because a package matches a published advisory. | Security/policy—vulnerability/advisory gate: dependency matches a published advisory | Verify the advisory and update or replace the dependency. |
| A page load times out with no trace, request log, or resource data. | Unclassified failure: page load exceeded 30 seconds; needs browser trace and request timing | Collect the requested diagnostics before inferring a cause. |
| Comparable runs show the same page-load signature passing and failing, but provide no trace, request log, or resource data. | Unclassified intermittent failure: page load exceeded 30 seconds; needs browser trace and request timing | Collect the requested diagnostics before inferring a cause. |

## Evidence boundaries

- A retry that passes establishes only that the signature is intermittent in the observed sample.
- A one-off failure is not intermittent. Do not infer recurrence from its mechanism or wording.
- A recurring signature does not establish a common mechanism across different scopes or environments.
- A label should include the narrowest scope known: test, suite, worker, environment, branch, release, or dependency.
- If a mechanism is plausible but unproven, preserve it as a low-confidence hypothesis in the expanded report; do not put it in the label.
