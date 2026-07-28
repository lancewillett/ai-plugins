---
name: classify-test-failures
description: Replace vague “flaky” or “flakiness” language with the narrowest evidence-supported classification of a test, build, deployment, performance, security, or CI failure. Use when triaging an intermittent, recurring, or apparently nondeterministic failure; responding to a test alert; reviewing a failure report; or someone calls a test “flaky.”
---

# Classify test failures

Read [the taxonomy](references/taxonomy.md) before classifying. Classify the failure, not the test or the people involved.

## Workflow

1. Capture observed facts first: the exact failing signature, failed step or assertion, relevant logs, execution context, and run history. Keep facts separate from inferences.
2. Describe recurrence separately from cause. Use `intermittent` only when the same signature has both passed and failed in comparable runs. Omit it for a one-off failure, even when the mechanism is commonly intermittent or the source calls it flaky or nondeterministic. It is a modifier, never a root cause.
3. Choose the narrowest supported domain, mechanism, and scope from the taxonomy. State all three in the label or expanded report. Name a mechanism only when evidence supports it.
4. State confidence from the evidence:
   - **High:** direct error, trace, or reproduction identifies the mechanism.
   - **Medium:** several consistent signals identify the likely mechanism.
   - **Low:** the signature or context suggests a domain, but a distinguishing diagnostic is missing.
5. Treat retries as measurement, not proof. A passing retry can establish recurrence; it cannot prove the failure was harmless or identify its cause.
6. If evidence cannot support a mechanism, write: `Unclassified [intermittent ]failure: <exact signature>; needs <specific diagnostic>`. Include `intermittent` only with comparable pass/fail evidence. Do not invent a cause.

## Label and output

Default to one plain-English line:

`[Intermittent ]<domain>—<specific mechanism failure>: <exact signature or affected scope>`

Examples: `Test environment—database startup failure: MySQL container did not become healthy` and `Test design—brittle selector failure: visible-text lookup no longer matches the control`.

For an expanded report, use this order:

```markdown
Label: <one-line label>
Observed: <facts only>
Evidence: <log, trace, run history, or reproduction>
Confidence: <high|medium|low>
Impact/scope: <test, suite, environment, branch, or release scope>
Owner/route: <responsible component or team route; do not guess a person>
Next evidence/action: <one diagnostic or corrective action>
```

Use the failure signature verbatim where practical. Do not write `flaky`, `flakiness`, `random`, or `harmless` as a substitute for evidence. If a source uses that language, quote it only as source wording and replace it in the conclusion.

## Match evidence to action

- Inspect the failed child build, logs, setup output, trace, and artifacts before choosing a label.
- Compare passed and failed runs only when their test, revision, configuration, and execution context are known.
- Route the issue to the component implied by evidence, such as test code, product behavior, CI setup, or an external dependency.
- Request one discriminating diagnostic when uncertain: startup logs, browser trace, request timing, worker assignment, runtime version, resource metrics, or configuration diff.
- Recommend a corrective action only after the label is supported. A retry may be useful for measurement, but never close or downgrade the failure by itself.
