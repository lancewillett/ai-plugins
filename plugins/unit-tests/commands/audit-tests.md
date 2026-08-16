---
description: "Audit a test suite for quality—find tests to delete, rewrite, or add. Produces a structured report."
argument-hint: "[path or file]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Edit", "Write", "Agent"]
---

# Audit tests

Run a test quality audit using the unit-tests agent. Reviews existing tests and makes them better—not bigger.

**Target:** "$ARGUMENTS" (defaults to current directory if empty)

## Workflow

### 1. Determine scope

- If a path argument is provided, audit that specific file or directory
- If no argument, audit the current working directory
- Find all test files using standard patterns:
  - `**/*.test.*`, `**/*.spec.*`, `**/__tests__/**` (JavaScript)
  - `**/tests/**/*Test.php`, `**/*Test.php` (PHP)

### 2. Launch audit

Use the Agent tool with `subagent_type: "unit-tests"` to launch the audit with a prompt like:

```
Audit the test suite at {target path}. Follow your full workflow:
1. Discover all test files
2. Run the existing suite for a baseline
3. Audit each test file against the decision framework and smell catalog
4. Produce the structured audit report

Target: {path}
```

If the user wants changes applied (not just a report), add:

```
After producing the audit report, apply the recommended changes:
- Delete tests that should be deleted (with explanations)
- Rewrite tests that have fixable smells
- Add tests only where genuine gaps exist
- Run the suite again to verify all changes pass
```

### 3. Present results

Show the structured audit report to the user. Highlight:
- **Critical findings**—tests that are actively hiding bugs (mock-testing-mocks, constructor drift, dodgers)
- **Quick wins**—tests to delete that add no value (framework testers, coverage chasers)
- **Gaps**—missing tests for high-risk code paths

### 4. Offer next steps

After the report, ask if the user wants to:
1. Apply recommended changes (delete/rewrite/add)
2. Focus on a specific file or smell type

## Usage examples

**Audit everything:**
```
/unit-tests:audit-tests
```

**Audit a specific directory:**
```
/unit-tests:audit-tests src/components/__tests__
```

**Audit a specific file:**
```
/unit-tests:audit-tests tests/unit/UserServiceTest.php
```

## What the agent does NOT do

- Blindly add tests to increase coverage numbers
- Test framework behavior (React rendering, WordPress hooks)
- Change expected values to make failing tests pass
- Add tests for trivial code (getters, setters, constructors)
