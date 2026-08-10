# P0 — Reconcile the executable factory contract

## GOAL

- `prompt_id`: `plan24.P0.contract_reconciliation.v1`
- `role`: `baseline_and_contract_owner`
- `objective`: Establish a reproducible baseline and one non-contradictory
  executable authority for the curriculum factory.
- `non_goals`: Do not implement later phases; choose whichever prose file was
  read last; delete or overwrite dirty work; preserve stale claims merely to
  avoid reconciliation.
- `authorized_inputs`: Active runtime, meta-prompt, policy, schemas, curricula,
  tests, docs, Plans 19/21/23 as historical evidence, git status, and Plan 24.
- `output_contract`: Baseline inventory/digests, contradiction disposition,
  frozen node/check/artifact/terminal ownership matrix, current behavior
  receipts, and failing factory-acceptance tests.
- `completion_condition`: Every planned behavior has one authority and the
  absent live factory behavior fails reproducibly for the intended reason.

## TEST

1. Current full test and CLI baseline is captured with commands and exit codes.
2. User-owned modified/untracked paths are inventoried and preserved.
3. Live refusal, simulation coverage, lifecycle, review-count, terminal, and
   workbook claims are compared across code and active contracts.
4. Each accepted contradiction resolution updates all active owners atomically
   or records a blocking dependency.
5. Stable failing tests cover live unit, full manifest, targeted repair, cold
   resume, exact coverage, and workbook release.
6. The matrix maps each graph node, state write, artifact type, blocking check,
   repair route, and terminal to exactly one owner.

## LOOP

Repair only baseline or authority defects exposed here and rerun affected
contract tests. Stop as `SYSTEM_FAILURE` if two active authorities cannot be
reconciled without a user product decision. Otherwise emit the P0 receipt and
advance to P1; do not claim factory progress from baseline documents alone.
