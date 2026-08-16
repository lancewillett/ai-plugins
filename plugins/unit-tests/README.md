# Unit tests

Audit an existing test suite and make it better—not bigger.

The auditor finds low-value checks, brittle assertions, duplicated coverage, slow feedback loops, and genuine regression gaps. It reads the production code alongside its tests, records a baseline, and verifies any requested changes.

## Install

### Claude Code

```text
/plugin install unit-tests@ai-plugins
```

Run the command against the current repository or a specific path:

```text
/unit-tests:audit-tests
/unit-tests:audit-tests tests/unit
```

### Codex

```text
codex plugin install unit-tests@ai-plugins
```

Ask Codex to audit or improve a test suite. The `unit-tests` skill activates for focused test-quality work.

## What it checks

- Whether each test protects a named regression scenario
- Behavior assertions versus implementation coupling
- Duplicate, tautological, assertion-free, and over-mocked tests
- Expensive tests that belong at a cheaper boundary
- Live external dependencies inside unit suites
- Missing coverage for high-risk paths
- Runtime, independence, and silent-pass risks

The auditor never changes an expected value merely to make a failure pass. It flags uncertain behavior for human review.

## License

GPL-2.0-only. See [LICENSE](./LICENSE).
