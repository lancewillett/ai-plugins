# Unit tests

Use the `unit-tests` skill to audit an existing test suite for value, speed, and meaningful regression coverage.

## Audit without changing files

In Claude Code, run the plugin command with no argument to audit the current repository:

```text
/unit-tests:audit-tests
```

Pass a path to narrow the audit:

```text
/unit-tests:audit-tests tests/unit/UserServiceTest.php
/unit-tests:audit-tests src/components/__tests__
```

The command reports findings without editing files by default. It reads each test with its production code, runs the suite for a baseline, and returns a structured report.

## Apply improvements

Run the audit first. After reviewing its findings, ask Claude to apply the relevant recommendations:

```text
Apply the recommended improvements in tests/unit.
```

When authorized, the skill removes low-value tests with reasons, rewrites brittle checks, and adds tests only for genuine regression gaps. It runs the relevant suite before and after changes.

## Use with Codex

Invoke the bundled skill directly:

```text
Use $unit-tests to audit all tests in this repository.
```

## Guardrails

- Never changes an expected value merely to make a failure pass
- Tests behavior instead of implementation details
- Treats live network or service dependencies as integration coverage
- Flags zero-test runs, skipped checks, and assertion-free tests
- Records runtime and pass, fail, and skip counts
