# P5 — Implement workbook assembly and release

## GOAL

- `prompt_id`: `plan24.P5.workbook_release.v1`
- `role`: `workbook_graph_implementer`
- `objective`: Assemble exact accepted-manifest coverage into a rendered,
  reviewed, auditable workbook and make release audit the only path to
  `COMPLETE`.
- `non_goals`: Do not accept partial/duplicate/out-of-order coverage; treat PDF
  concatenation as release; sample pages; reopen unit content for workbook
  layout defects; let another code path write `COMPLETE`.
- `authorized_inputs`: P0–P4 implementation/evidence, accepted immutable unit
  packages, compiled workbook graph, workbook contracts/checks/review policy.
- `output_contract`: Assembly manifest, workbook nodes and repairs, full page
  inventory, checks/reviews, terminal audit, negative tests, released fixture
  workbook, and P5 receipt.
- `completion_condition`: The bounded fixture produces a release-audited
  workbook and all false-completion cases are rejected.

## TEST

1. Assembly input equals the ordered manifest and contains each accepted unit
   exactly once with current hashes.
2. Missing PDF, changed accepted unit, partial, duplicate, or out-of-order
   coverage prevents assembly/release.
3. Every workbook page rasterizes and enters the deterministic and declared
   visual/review denominators.
4. Independent reviews have valid isolated identities and code reduces their
   typed results.
5. TOC, navigation, pagination, front matter, and layout failures revise only
   workbook-owned artifacts and rerun invalidated release checks.
6. Only a passing final audit writes `COMPLETE`; mutation tests prove no other
   function/path can do so.

## LOOP

Workbook repair creates a new workbook version while accepted unit hashes stay
fixed. Loop through assembly, page QA, review, and audit within the compiled
bound. Repeated failures terminate `CONVERGENCE_EXHAUSTED`; tool/integrity
failures terminate `SYSTEM_FAILURE`. Advance only with an actual accepted
workbook.
