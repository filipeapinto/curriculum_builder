# P4 — Implement manifest orchestration and durable resume

## GOAL

- `prompt_id`: `plan24.P4.manifest_resume.v1`
- `role`: `run_lifecycle_implementer`
- `objective`: Execute live `--lab-id`, live `--all`, interruption, and
  cold-process resume in compiled manifest order with truthful lifecycle state.
- `non_goals`: Do not infer order/status from directory enumeration; overwrite
  accepted work; require a coding-agent invocation between units; claim workbook
  completion after the last unit.
- `authorized_inputs`: P0–P3 factory implementation and receipts, compiled run
  graph, frozen lifecycle/resume contracts, bounded unrelated fixture.
- `output_contract`: Production CLI paths, durable checkpoint/continuation
  behavior, run lifecycle records, fault tests, three-unit live fixture run,
  cold-resume evidence, and P4 receipt.
- `completion_condition`: Both modes execute the production graph and resume is
  atomic, manifest-derived, hash-safe, idempotent, and proven across processes.

## TEST

1. `--lab-id` accepts only a known legal requested unit and returns
   `UNIT_ACCEPTED` without a full-run claim.
2. `--all` derives exact order/count from the frozen manifest and advances only
   after unit acceptance.
3. Interruption commits a complete checkpoint and emits one exact resume
   command; no later node activates before commit.
4. Cold resume consumes continuation once, preserves accepted hashes, and
   starts at the first incomplete valid graph position.
5. Changed manifest/prompt/policy/graph digest, out-of-order request, accepted
   overwrite, duplicate consume, corrupt checkpoint, or false status is refused.
6. The live three-unit unrelated fixture completes unit production without
   manual control between units.

## LOOP

Lifecycle failures repair only controller/checkpoint/resume owners and rerun the
full crash matrix. Never delete accepted evidence to make resume tests pass.
An external interruption returns `INTERRUPTED`; invalid state or lost atomicity
is `SYSTEM_FAILURE`. Advance only when the three-unit and cold-resume proofs
bind the current graph and code.
