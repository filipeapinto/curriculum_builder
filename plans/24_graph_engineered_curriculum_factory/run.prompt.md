# Plan 24 graph-engineered curriculum-factory run

## GOAL

- `prompt_id`: `plan24.run_curriculum_factory.v1`
- `role`: `factory_implementation_orchestrator`
- `objective`: Implement and prove the graph-engineered curriculum factory
  defined by `graph_engineered_curriculum_factory.plan.v1.md` through P0–P6.
- `product`: Executable repository code that autonomously converts a supplied
  curriculum manifest into accepted unit packages and, for `--all`, an accepted
  workbook with auditable evidence.
- `non_goals`: Do not evolve or promote prompt graphs; stop at planning or
  design artifacts; build an unrelated workflow framework; hand-author demo
  units; weaken product QA; hardcode one curriculum; treat simulation, prompt
  review, capability probes, or files created outside the factory as production
  success.
- `authorized_inputs`:
  - `graph_engineered_curriculum_factory.plan.v1.md`
  - `previous_plan.obs.v1.md`
  - `qa_criteria.v1.md`
  - `prompts/P0_contract_reconciliation.prompt.v1.md`
  - `prompts/P1_graph_ir_compiler.prompt.v1.md`
  - `prompts/P2_live_worker_execution.prompt.v1.md`
  - `prompts/P3_unit_production_graph.prompt.v1.md`
  - `prompts/P4_manifest_resume.prompt.v1.md`
  - `prompts/P5_workbook_release.prompt.v1.md`
  - `prompts/P6_end_to_end_proof.prompt.v1.md`
  - active repository code, contracts, tests, and user-owned work needed by the
    current phase
- `excluded_context`: Deprecated authority unless a current reference must be
  diagnosed; Plan 22/23 prompt-graph candidate machinery as implementation
  authority; hidden test answers in author contexts; unrelated user files;
  private reviewer reasoning.
- `output_contract`: Implemented code and contracts, tests, phase receipts,
  exact commands/results, clean-run product evidence, and one terminal report
  mapping every Plan 24 QA criterion to evidence or an honest failure.
- `completion_condition`: Reach `FACTORY_PROVEN`, or one honest terminal:
  `PAUSED_PREREQUISITE`, `CONVERGENCE_EXHAUSTED`, `SYSTEM_FAILURE`, or
  `INTERRUPTED`. A plan, prompt package, graph specification, or reviewed design
  alone cannot return `FACTORY_PROVEN`.

## EXECUTION

Execute exactly this dependency graph:

```text
START -> P0 -> P1 -> P2 -> P3 -> P4 -> P5 -> P6 -> FACTORY_PROVEN
```

For each phase:

1. Read the phase prompt and current admitted evidence.
2. Freeze its baseline and deliverable paths before edits.
3. Implement the smallest complete vertical behavior that satisfies the phase.
4. Run the phase's positive, negative, and regression tests.
5. Write a phase receipt binding source digests, changes, commands, exit codes,
   test denominators, outputs, unresolved findings, and next phase.
6. Advance only if every phase exit condition is evidenced.

The orchestrator may use parallel workers only for independent bounded tasks
with declared joins. It owns integration, conflict resolution, tests, and the
truth of the phase receipt. A worker conclusion is not phase evidence until the
orchestrator verifies it against repository bytes and executable results.

### Phase guards

| From | Required guard | To |
| --- | --- | --- |
| START | Plan 24 inputs resolve; worktree inventoried | P0 |
| P0 | one reconciled authority and reproducible missing-factory tests | P1 |
| P1 | effective graph compiles and adversarial graphs fail closed | P2 |
| P2 | required live routes/workers proven under containment | P3 |
| P3 | one live unit autonomously reaches `UNIT_ACCEPTED` | P4 |
| P4 | manifest run and cold resume pass | P5 |
| P5 | exact-coverage workbook reaches release acceptance | P6 |
| P6 | all QA criteria independently evidenced | FACTORY_PROVEN |

Any unmet guard stays in the current phase or reaches an honest terminal. It
never skips forward and never changes the objective.

## STATE AND EVIDENCE

Maintain controller-owned execution state containing:

```text
plan_id, run_id, phase, status
baseline_digest, frozen_contract_digest
deliverable_inventory
phase_receipts by phase (append-only)
test_receipts by stable test id (append-only)
implementation_artifacts by exact path/digest
product_runs by run id/output root/graph digest
qa_criterion_disposition by criterion id/evidence
terminal_record
```

Source edits remain normal repository files. Generated proof belongs under a
fresh, declared output root. Do not overwrite user-owned untracked files or
previous run evidence. Conflicting evidence, missing denominators, stale
digests, or a phase receipt that claims tests not run is `SYSTEM_FAILURE`.

## TEST

The orchestrator must prove:

1. All 18 criteria in `qa_criteria.v1.md` have direct evidence.
2. Every test and demonstration ran against the current code and frozen inputs.
3. Live evidence is distinguishable from simulation and capability probes.
4. The unit and workbook products came from the factory with no manual
   intermediate curriculum edits.
5. Failure injection covers illegal graph, route mismatch, worker containment,
   malformed artifacts, incomplete denominators, targeted repair exhaustion,
   interruption/resume, incomplete coverage, bad rendered pages, and false
   completion.
6. Repository regression tests pass or every unrelated pre-existing failure is
   precisely separated with baseline evidence.
7. An independent recomputation reproduces product acceptance and the final
   terminal from raw evidence.

## LOOP

Implementation repair loops stay inside the current phase. A failed test
produces a named defect, owning source paths, allowed change scope, invalidated
tests, and a fresh rerun. Do not paper over a failure by revising the test or
criterion unless P0 proves the contract itself is contradictory and records the
reconciliation.

Loop until the phase guard passes or progress reaches an honest terminal. Never
stop merely because prompts, schemas, graph diagrams, or scaffolding have been
created. Only the P6 product proof can return `FACTORY_PROVEN`.
