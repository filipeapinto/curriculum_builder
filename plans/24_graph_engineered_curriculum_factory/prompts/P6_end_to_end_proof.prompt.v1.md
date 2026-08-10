# P6 — Prove and hand off the curriculum factory

## GOAL

- `prompt_id`: `plan24.P6.end_to_end_proof.v1`
- `role`: `factory_release_auditor`
- `objective`: Prove from clean roots and raw evidence that the repository now
  operates as the Plan 24 curriculum factory.
- `non_goals`: Do not implement a new product; repair evidence by hand; count
  simulation/canaries as production; trust controller conclusions without
  recomputation; close deferred claims not literally proven.
- `authorized_inputs`: Current repository, P0–P5 receipts, clean production
  runs, Plan 24 criteria, raw immutable evidence, operator documentation.
- `output_contract`: Regression results, clean live unit proof, unrelated
  full-manifest/workbook proof, cold-resume proof, Arduino attempt, fault
  matrix, independent recomputation, criterion disposition, truthful docs, and
  terminal release report.
- `completion_condition`: Every QA criterion has current passing evidence and
  the terminal is `FACTORY_PROVEN`, or the first honest unmet criterion is
  reported with preserved work and next action.

## TEST

1. Run all repository, graph compiler, containment, unit, lifecycle, workbook,
   mutation, and fault-injection suites against current bytes.
2. Reproduce one live unit from a clean output root with no intermediate manual
   edit and verify `UNIT_ACCEPTED` from raw records.
3. Reproduce the unrelated bounded `--all` run and accepted workbook from a
   clean root; verify `COMPLETE` from raw records.
4. Kill and cold-resume a run, proving accepted hashes and exactly-once
   continuation.
5. Start the Arduino run through the same manifest compiler and runtime; accept
   progress or only a proven external-prerequisite pause.
6. Independently recompute graph digest, route coverage, source/artifact hashes,
   check/review/page denominators, transitions, unit acceptance, coverage, and
   release terminal without controller verdict fields.
7. Map every criterion in `qa_criteria.v1.md` to exact file/command evidence;
   zero unresolved blocker is required.

## LOOP

A P6 failure returns to the owning implementation phase, invalidates all
downstream proof that depends on changed bytes, and reruns from a clean output
root. Evidence is never edited to pass. If a genuine external prerequisite is
missing, preserve the run and emit the exact resume path. Return
`FACTORY_PROVEN` only for the complete evidence-backed product.
