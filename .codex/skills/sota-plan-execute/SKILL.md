---
name: sota-plan-execute
description: Execute an approved, self-contained, versioned state-of-the-art research plan produced by sota-plan-create. Use when Codex must run the plan's searches, evidence appraisal, synthesis, challenge, verification, and delivery while enforcing the allocations, budgets, gates, provenance requirements, and acceptance rules embedded in that plan.
---

# SOTA Plan Execute

Execute the latest explicitly approved plan as a controlled research run. Treat the plan as the governing contract and preserve evidence sufficient to audit every conclusion.

## Required references

1. Read the complete approved plan, `references/sota-family-contract.md`, and `references/execution-contract.md` before substantive work.
2. Treat the approved plan as the sole project execution contract.
3. Read cited supporting artifacts only to inspect evidence, never to discover missing execution instructions.

If the plan or a required dependency is missing, unapproved, contradictory, or not executable within its controls, stop and report the exact gate that failed.

## Start gate

1. Resolve the latest plan version without modifying any version.
2. Confirm that its status records explicit human approval.
3. Run family preflight first. Confirm the plan contains every universal family field and only strengthens the family contract, then confirm its plan-specific objective, scope, method, allocations, outputs, budgets, measurements, stops, and acceptance criteria.
4. Map each activity to the deterministic tools, model allocation, or human authority embedded in the plan.
5. Initialize the required execution log, source register, budget ledger, stable identifiers, and artifact locations.
6. Resolve every non-human team assignment to its installed role skill. Stop if a named skill is unavailable.
7. Do not start evidence collection until all mandatory gates pass.

## Execute

1. Follow dependency order and permitted parallelism from the plan. Invoke `$sota-method-lead`, `$sota-evidence-review`, `$sota-synthesize`, `$sota-independent-challenge`, and `$sota-verify` only for roles assigned by the plan.
2. Prefer deterministic tools for discovery, hashing, validation, deduplication, and schema checks.
3. Record searches, candidates, exclusions, appraisals, extractions, claims, retries, failures, and deviations as they occur.
4. Keep facts, attributed claims, inferences, competing explanations, and unknowns distinct.
5. Reuse completed evidence products by stable identifier and digest.
6. Measure consumption using the mechanisms named in the plan. Apply warning thresholds, convergence rules, retry limits, hard stops, and external-spend controls exactly as approved.
7. Run independent challenge without giving it final acceptance authority. Record every challenge and disposition.
8. Produce the compact run package at `research/<sota-slug>/runs/<run-id>/` with `report.html`, canonical `execution-log.json`, and optional justified `evidence/`.
9. Submit the verified package to the human owner for acceptance. Do not self-approve it.

## Plan-change boundary

Do not silently repair or expand the approved plan during execution. If execution reveals a material change to scope, method, budget, eligibility, authority, required outputs, or acceptance criteria:

1. Preserve completed evidence and record the blocking condition.
2. Stop affected work.
3. Return the plan to `$sota-plan-create` for `vN+1`.
4. Resume only after the new version receives explicit approval.

Minor implementation choices that remain within the approved contract may be recorded in the execution log without creating a new plan version.

## Completion report

Report the executed plan version, terminal status, outputs, verification results, budget usage, deviations, unresolved limitations, and human-acceptance state. Mark partial or blocked work accurately; artifact production alone is not research success.
