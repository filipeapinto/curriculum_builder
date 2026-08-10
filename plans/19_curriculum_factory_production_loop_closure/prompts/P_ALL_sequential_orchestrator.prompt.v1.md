# GOAL

Execute phases **P0 through P6** of
`plans/19_curriculum_factory_production_loop_closure/curriculum_factory_production_loop_closure.plan.v1.yaml`
(schema: the sibling `.schema.v1.json`) end to end, unattended, in one continuous run, by
executing each sibling phase prompt in this directory verbatim and in order:

1. `P0_baseline_contract_freeze.prompt.v1.md`
2. `P1_live_capability_routing_closure.prompt.v1.md`
3. `P2_schema_bound_worker_execution.prompt.v1.md`
4. `P3_production_unit_state_machine.prompt.v1.md`
5. `P4_full_manifest_orchestration.prompt.v1.md`
6. `P5_workbook_release_loop.prompt.v1.md`
7. `P6_release_proof_debt_reconciliation.prompt.v1.md`

This prompt adds no phase content of its own and overrides none of the seven files' `GOAL`,
`TEST`, `LOOP`, stop conditions, or "before phase may be claimed done" checklists. It only
sequences them. The plan's own `operating_rules` already require dependency order and require
stopping when a phase's definition of success cannot be proven; this prompt is that rule made
executable as a single unattended run instead of seven separately-launched ones.

**Read before starting:** the plan YAML in full, and all seven phase prompt files in full.
Do not begin P0 until you have read every file below once.

## Non-negotiable properties of this run

- **No skipping ahead.** Never begin phase `Pn+1` until phase `Pn`'s own
  `results/Pn.result.v1.md` has been written and its "before phase may be claimed done"
  checklist is fully satisfied with real evidence, exactly as `Pn`'s own prompt defines it.
- **No silent substitution.** Never mark a phase done because artifacts exist; each phase
  prompt already forbids inferring success from file presence, and that rule is not relaxed
  here.
- **No autonomy grant beyond what each phase already declares.** If a phase's own prompt
  requires a real external call (for example P1's live-capability probes, or a live model
  call in P2/P4/P5), make that call exactly as that phase's prompt specifies. Do not add,
  widen, mock, or skip such calls to keep the chain unattended.
- **No cross-phase file edits out of turn.** While executing phase `Pn`, touch only the paths
  `Pn`'s own prompt authorizes. Do not pre-edit files reserved for a later phase to make that
  later phase pass faster.

# LOOP

For `n` in `0, 1, 2, 3, 4, 5, 6`:

1. Open `P{n}_*.prompt.v1.md` and treat its `GOAL`, `TEST`, and `LOOP` sections as the
   complete, authoritative instructions for this step — follow them exactly, including their
   own internal retry loop on test failure.
2. Run that phase's `TEST` list to completion per its own `LOOP` section: on failure, narrow
   to the single responsible artifact, fix only that artifact, and rerun in the order that
   phase's `LOOP` section specifies. Do not advance to step 3 while any of that phase's own
   required tests are failing.
3. Confirm that phase's own stop conditions do not apply. If they do, **stop the entire
   chain immediately** — do not attempt `Pn+1`, do not partially satisfy it, do not report
   phases beyond `Pn` as attempted. Write whatever partial evidence exists for `Pn` and mark
   it blocked, truthfully, per that phase's own instructions for a stop.
4. Confirm that phase's "before phase may be claimed done" checklist is satisfied with real
   evidence and that its `results/Pn.result.v1.md` has been written per its own instructions.
5. Only then move to `P{n+1}`.

**Global stop conditions** (in addition to each phase's own):

- Any phase's stop condition fires.
- A phase's own tests cannot be made to pass after the fixes its own `LOOP` section permits
  (i.e., the phase's own loop has genuinely exhausted itself, not merely been attempted once).
- Evidence required by a later phase's own "read the prior result" step
  (`P3` reads `P0`'s result; `P6` reads `P0`'s through `P5`'s) is missing or contradicts what
  is being claimed now.

A stop at phase `Pn` is a valid, truthful end state for this run. It is not a failure of this
orchestrator prompt to report "blocked at `Pn`" with `Pn`'s own recorded evidence — it is the
correct outcome when `Pn`'s definition of success cannot be proven, exactly as the plan's
`operating_rules` require.

**When all seven phases complete:** the run is done when `P6`'s own "before phase may be
claimed done" criteria are met — i.e., `results/P0.result.v1.md` through
`results/P6.result.v1.md` all exist, `P6` has compared every one of them against the P0
implementation matrix, and `P6`'s own verdict has been recorded. Do not write any additional
summary file beyond what `P0`–`P6` each already require; this prompt produces no artifact of
its own besides those seven.
