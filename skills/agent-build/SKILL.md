---
name: agent-build
description: "Build a change with a coding agent and hand over a PR that is actually ready: five-steps first, a proven launch with a sized watcher, a multi-lens review of the final diff, proof on the real path, a Definition of Done, every review comment answered, and CI fully green. A gate-check script verifies the gates before handoff. Use when asked to /agent-build or to have an agent build a change end to end."
argument-hint: "<the change to build>"
---

# Agent build

Hand the human a PR they can review once and merge, not a draft they have to chase.

## Gates: none optional, none replaced by a cheaper step

Run them in order for every PR this skill produces, including PRs a sub-agent or a follow-up agent run builds. Follow them yourself; don't recite them in chat.

1. **Five-steps first.** Run `/five-steps` (from this marketplace) on the change before any coding starts. Thinking it through without the skill doesn't count. If the cuts remove the feature, stop. Mention a cut in chat only when it changes what gets built.
2. **A watcher on every background agent run,** follow-ups included.
3. **A multi-lens review of the final diff.** Use a review battery that routes the diff to several lenses (correctness, security, tests, simplification), with at least one reviewer from a second model family. A single reviewer subagent is not a substitute. Rerun it after a rewrite.
4. **The repo's own pre-push checks,** run locally on the committed state before each push.
5. **Proof on the real path.** Exercise the change the way production will, and confirm the proof ran your branch's code, not the default branch. A CI job on an unwatched branch can silently build the default branch.
6. **A Definition of Done in the PR body,** as a checklist under a `Definition of done` heading. Include the after-merge check that proves it works.
7. **Every review comment answered.** Read every human and AI review comment, fix or reply to each one.
8. **CI 100% green.** Every check finished and passed, none pending, none failed. A passing summary with a check still queued does not count.

## End check

Before handing over, run the bundled script from this skill's directory:

```bash
python3 scripts/gate-check.py <PR URL> --worktree <worktree> --lint "<repo pre-push command>" --attest 1,2,3,5
```

- Attest only the gates you actually ran. Write `2=na` when no background run happened.
- The script checks gates 4, 6, 7 and 8 itself. It runs the lint command on the clean, committed PR head, checks for a Definition of Done with an after-merge item, counts unanswered review comments, and checks CI and mergeability. Pass `--ai-marker '<text>'` to also flag AI review summaries that contain that marker and lack a "No blocking issues" line.
- On any FAIL, fix it and rerun. Its output is for you, not the human.
- When everything passes, it opens the PR in your browser (`--no-open` to skip). Tell the human in one line that the PR is ready, with its link.

## Choosing the agent

Default to a second model family for coding (for example Codex when you're in Claude Code). It finds things a second copy of you will not. Ask it to work in a git worktree, and clean the worktree up after the PR merges.

Use same-family subagents instead for mechanical or tightly specified work. They also fit when you need the result back right away, or expect to iterate with the agent. Say which you picked and why in one line.

## Launching and watching

Prove the run actually started before you say it's running. Check the job is registered and names the worktree you meant; a returned launch ID is not proof. Launch the watcher in the same breath as the job, never after. The gap between "launched" and "watching" is where runs get lost.

Size the watcher to the work, then add half again: a real build runs 15–45 minutes, so watch for an hour, not ten minutes. Poll every 15 seconds or so; more often buys nothing. Have it exit when the job leaves the running state and dump commits, working tree, and diffstat when it does. Re-launch it before it expires, not after. Test the watcher's own parsing: a broken check reports a false stop, which is worse than no watcher.

Judge progress by real commits and changed files in the worktree, not by a status line. If it stalls, produces nothing, or the job disappears, say so and restart it. Never let the human be the one who asks how it's going.

## Scope

Avoid bloat, drift, hand-waving, and anything that doesn't carry its weight. Only build what survives the five steps.

Skip the browser handoff for a PR you will merge yourself; link it in chat instead.

The change: $ARGUMENTS
