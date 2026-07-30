# Execute the folder-refactoring plan v2

## Goal

Implement `folder_refactoring.plan.v2.md` through phases 0–4. Finish only when every
active cumulative gate passes, every review approves, results are recorded, and the
worktree is clean. Preserve unrelated changes. Never weaken a requirement or report
an unexecuted check as passing.

## Agents

- **Coordinator:** assigns work, enforces phase order, and owns commits.
- **Implementer:** makes the current phase's changes.
- **Validator:** independently runs the harness and verifies its result record.
- **Reviewer:** independently checks the diff against the plan.

Only the coordinator changes Git history. Keep implementation, validation, and review
separate.

## Loop

Read `AGENTS.md` and the complete v2 plan. For each phase `N`:

1. The implementer completes phase `N`.
2. The reviewer returns `APPROVE` or actionable findings.
3. Fix findings and repeat review until approved.
4. The coordinator creates the phase's candidate commit.
5. The validator runs `./tests/run_gates.sh N` and inspects the new JSON result.
6. Validation passes only when all gates with `activation_phase <= N` pass, later
   gates are recorded as skipped, every rejection fixture fails for its declared
   reason, results are written, and the worktree is clean.
7. On failure, the implementer fixes the cause, the reviewer rechecks the diff, the
   coordinator amends the unshared phase commit, and validation repeats.
8. Advance only after review returns `APPROVE` and validation returns `PASS`.

After phase 4, run `./tests/run_gates.sh 4` and review the complete result. Repeat the
same correction loop until both agents approve.

Return `APPROVED` only when the plan's final approval conditions hold. Otherwise
return `BLOCKED` with the exact external blocker or required human decision.
