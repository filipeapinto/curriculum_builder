# Execute the folder-refactoring plan v4

## Goal

Implement `folder_refactoring.plan.v4.md` through phases 0–4. Finish only when every
active cumulative gate passes, every review approves, results are recorded, and the
worktree is clean. Preserve unrelated changes. Never weaken a requirement and never
report an unexecuted check as passing.

## Agents

- **Coordinator:** assigns work, enforces phase order, and owns commits.
- **Implementer:** makes the current phase's changes.
- **Validator:** independently runs the harness and verifies its result record.
- **Reviewer:** independently checks the diff against the plan.

Only the coordinator changes Git history. Keep implementation, validation, and review
separate.

## Loop

Read `AGENTS.md` and the complete v4 plan. For each phase `N`:

1. The implementer completes phase `N`. In phase 0, follow §9's seven steps in order —
   in particular, stage `schema/`→`schemas/` and confirm **four `R100` lines** from
   `git diff --cached --name-status -M100%` *before* applying any §10 content edit.
2. The reviewer returns `APPROVE` or actionable findings.
3. Fix findings and repeat review until approved.
4. The coordinator creates the phase's **candidate commit**. Gates run against a commit,
   never a dirty tree: `FR-P0-HISTORY` reads `HEAD` and `FR-P0-CLEAN` requires an empty
   `git status`.
5. The validator runs `./tests/run_gates.sh N` and inspects the new JSON result.
6. Validation passes only when `FR-P0-HARNESS` passed first, all gates with
   `activation_phase <= N` pass, later gates are recorded as skipped, every rejection
   fixture fails for its declared reason, results are written, and the worktree is
   clean.
7. On failure, the implementer fixes the cause, the reviewer rechecks the diff, the
   coordinator **amends** the unshared candidate commit, and validation repeats from 5.
8. Advance only after review returns `APPROVE` and validation returns `PASS`.

After phase 4, run `./tests/run_gates.sh 4` and review the complete result. Repeat the
same correction loop until both agents approve.

## Standing constraints

- **`FR-P0-HARNESS` gates everything.** If it fails, report `BLOCKED` and report no other
  gate's outcome from that run — they are unreliable.
- **Claim discipline (harness rule 6).** Every gate carries a claim class and may not
  claim more than its class supports. No gate claims `execution` of a controller or
  routing runtime: none exists. Never write, in a report or a document, that the selector
  is enforced or that the check suite is fully executed. Phase 2 makes rules *stated,
  owned and mapped*; §12 owns the rest.
- **`MAPPED, NOT EXECUTED` is a count, never a pass.** Report the number from
  `FR-P4-CHECK-MAPPING` explicitly in the final result.
- **Never let a production scan read a fixture (harness rule 7).** If a detector flags a
  file under `tests/fixtures/` or `tests/selftest/`, the detector's scan roots are wrong;
  fix the detector, never the fixture.
- **Never resolve a gate failure by editing the gate.** Fix the repository, or return
  `BLOCKED` naming the gate id and the plan's stated failure meaning for it.
- **Scope.** Layout, placement, references, and the harness. Not curriculum content.
  Anything in §12 is a separate decision — surface it, do not act on it.

Return `APPROVED` only when the plan's final approval conditions hold. Otherwise
return `BLOCKED` with the exact external blocker or required human decision.
