# Execute the folder-refactoring plan

## Goal

Implement `folder_refactoring.plan.v1.md` in phase order. Finish only when every phase
gate and the final regression run pass. Preserve unrelated changes. Never weaken a
requirement or report an unexecuted check as passing.

## Agents

- **Coordinator:** assigns work, enforces phase order, and commits approved phases.
- **Implementer:** makes the current phase's changes.
- **Validator:** independently runs its gates and relevant regression checks.
- **Reviewer:** independently compares the diff with the plan.

Only the coordinator commits. Validation and review must be independent of
implementation.

## Loop

Read `AGENTS.md` and the complete plan. For each phase:

1. The implementer completes the phase.
2. The validator runs the phase gate and regressions.
3. The reviewer checks the diff against the plan.
4. The implementer fixes every failure or finding.
5. Repeat steps 2–4 until validation returns `PASS` and review returns `APPROVE`.
6. The coordinator commits the phase, verifies a clean worktree, and advances.

After the last phase, validate and review the complete result. Repeat the same loop
until both agents approve.

Return `APPROVED` only when all gates pass, all reviews approve, and the worktree is
clean. Otherwise return `BLOCKED` with the exact external blocker or required human
decision.
