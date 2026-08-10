# GOAL

Implement phase **P4 — Full-manifest orchestration** of
`plans/19_curriculum_factory_production_loop_closure/curriculum_factory_production_loop_closure.plan.v1.yaml`
(status `approved`, phase review and whole-plan review closed with zero unresolved Critical
or High findings). Read that plan's `overall_goal`, `scope_lock`, `operating_rules` and
`red_team_protocol.severity` before your first edit; they bind this phase in full.

Make `--lab-id` and `--all` execute the P3 production state machine over
**manifest-derived unit order** with truthful run lifecycle management.

P4 `depends_on: [P3]`. P3 delivers, and you consume by contract rather than re-implement:
a registry with exactly one production handler for every state in
`policy/controller.v1.yaml:states`; code-owned transition, review-aggregation, targeted
revision, checkpoint, resume and terminal-decision services; neutral domain-declared roles
and **derived** unit IDs (no electronics vocabulary in engine layers); and a per-unit
terminal decision written as that unit's own validated acceptance receipt. If P3 has not
executed, or its handler registry / terminal-receipt contract is absent or differs from
this description, stop and report the mismatch — do not build a private substitute.

## What to build

1. **Production `--lab-id`, `--all`, `--resume`, and explicit run close** in the real CLI at
   `runtime/run_curriculum.py`, which today reaches
   `RuntimeFailure("LIVE-GENERATION-NOT-PREFLIGHTED", ...)` for both routes and only ever
   calls `CurriculumRuntime.simulate()` (`runtime/controller.py`). Simulation stays reachable
   as a separate test mode (`--test-simulated-all`, `--test-golden-l01`); production must not
   fall through to it. `policy/controller.v1.yaml:cli.required_flags` is the minimum surface
   and may not shrink. Add an explicit run-close flag; do not make a stop inferable.
2. **One authoritative lifecycle schema and record.** `schemas/run_lifecycle.schema.v1.json`
   and `runtime/run_state.py` (`outputs/<run>/run_state.json`) are that schema and that
   record — extend them, do not add a second. They must represent acceptance, pending
   review, block, interruption and system failure, each derived from **validated receipts
   and frozen manifest order**. Three defects in the current files are in scope and must be
   corrected:
   - `run_state._COMPLETED_STATES` counts `ACCEPTED_PENDING_REVIEW` as completed, so
     `runtime/workbook.assemble()` would treat a pending-review unit as coverage and write
     `run_status: COMPLETE`. Only exact `ACCEPTED` may advance or enter coverage.
   - `run_status` has no `SYSTEM_FAILURE` member and `run_state.close_run()` accepts only
     `{PARTIAL, INTERRUPTED, BLOCKED}`, so a factory or tool failure cannot be recorded
     honestly at run level.
   - `manifest_unit_ids` is pinned to `"pattern": "^L[0-9]{2,3}$"`, which contradicts P3's
     derived, curriculum-neutral unit IDs. Replace it with the P0-frozen unit-ID rule
     resolved from the manifest contract; do not hardcode a curriculum's identifier shape.
3. **One immutable execution-contract digest** binds run initialization, every advance,
   pause, resume and close. `run_state` currently compares `manifest_sha256` and
   `prompt_sha256` separately in `assert_resumable()`; bind and compare the single P1
   execution-contract digest instead of, or in addition to, those, and refuse any operation
   whose recomputed digest differs from the one the run was initialized with.
4. **Sequential acceptance and next-unit derivation** per
   `policy/controller.v1.yaml:full_run.advance_rule` ("advance to the next lab only after
   the current lab is ACCEPTED") and `completion_rule`. Order comes from the frozen manifest
   (`runtime/controller.CurriculumRuntime.validated_manifest()` →
   `results/gate_1_static_preflight.json:unit_ids`), never from `os.listdir` of the run root.
   `run_state._scan_units()` may key on manifest order but must consume a **schema-validated**
   acceptance receipt, not the mere presence of `acceptance.json`.
5. **Per-unit budgets and convergence state that reset without weakening run-level limits.**
   Use `policy/limits.v1.yaml` as-is: `per_lab.max_model_calls`, `per_lab.max_revisions`,
   `per_lab.max_images`, `per_lab.max_storage_mb` reset at each unit boundary;
   `per_run.max_storage_mb`, `per_run.max_concurrency` and every `convergence.*` counter
   accumulate across the run. Honour `behaviour_on_limit`: stop **before** exceeding, keep
   the last valid checkpoint, name the binding limit with its value and the observed figure,
   and never report a limit stop as an accepted unit or a passed gate.
6. **Explicit blocked and interrupted outcomes.** A blocked unit stops the sequential run and
   names its external prerequisite. `policy/controller.v1.yaml:blocked_eligibility` is
   authoritative: `BLOCKED` is legal only for a named safety-critical fact still unavailable
   after recorded official-manufacturer and primary-source searches; tool, model, image,
   schema, writing, rendering and layout failures are `SYSTEM_FAILURE`.

## Hard constraints

The plan's `operating_rules` apply literally to every line you write:

- Preserve the precedence and ownership rules already declared in
  `meta_prompt/curriculum.prompt.v1.md` and `policy/controller.v1.yaml`.
- Treat simulated evidence, live-capability evidence, generated-unit evidence, and
  workbook-release evidence as distinct categories.
- Never infer success from file presence; validate declared outputs, hashes, checks,
  transitions, and terminal decisions.
- A worker may write only its declared schema-bound artifact and may never decide
  transitions or acceptance.
- A blocked curriculum fact, a retryable tool failure, and a factory defect remain separate
  terminal classifications.
- **Preserve accepted units on resume and refuse overwrite unless a new output version is
  explicitly requested.** An accepted unit's artifacts and hashes are immutable within a run
  root; overwrite requires an explicit new output version, never a silent rerun. This is also
  `policy/controller.v1.yaml:resume.refuses`.
- Execute phases in dependency order; atomically update policy, schema, checks, and deferred
  claims when their enforcement becomes true.
- Stop when a phase definition of success cannot be proven.

Out of scope for P4, and each an automatic failure of this phase: hardcoding Arduino
identifiers anywhere in engine layers; silently skipping a blocked unit to keep `--all`
moving; claiming workbook completion from unit directories. Workbook assembly, page
inspection and the four workbook reviews are **P5** — P4 may compute and record coverage and
must keep `runtime/workbook.assemble()` as the only writer of `COMPLETE`, but must not
implement the release loop.

Do not weaken safety, evidence, visual, review or acceptance gates to make a run pass. Do not
stage, stash, reset, restore or clean the pre-existing dirty worktree, and do not delete or
overwrite any existing `outputs/` run root.

# TEST

Every test below is a checkable artifact: a named test function under `tests/runtime/`, a
recorded CLI invocation with its exit code and resulting `run_state.json`, or both. Run them
strictly in the order given. `P4-T01` through `P4-T17` may drive the orchestrator with
synthetic unit receipts injected as *inputs*; such receipts are never evidence of unit
production and may not be used to satisfy `P4-T18` or `P4-T19`. `P4-T18` and `P4-T19` require
live routed workers.

`tests/runtime/test_run_state.py` currently encodes the pre-P4 semantics — it asserts that
four `ACCEPTED_PENDING_REVIEW` units count as `completed_unit_ids`. Update those assertions
to the exact-`ACCEPTED` rule; do not delete the tests to make them stop failing.

1. **P4-T01 — one authoritative lifecycle contract.** `schemas/run_lifecycle.schema.v1.json`
   validates records expressing acceptance, pending review, block, interruption and system
   failure, each requiring the bound execution-contract digest and a stated
   `terminal_reason` for any stopped status. Assert no second lifecycle schema or second
   writer of `run_state.json` exists in the tree. Negative fixtures: a stopped status with no
   reason; a record with no digest; a record whose `run_status` is not in the enum.
2. **P4-T02 — order comes from the frozen manifest.** With a run root containing unit
   directories that are extra, missing, out of order and alphabetically misleading, assert
   `manifest_unit_ids` and next-unit derivation match the manifest exactly and ignore the
   directory listing. Assert a unit directory with an unvalidated or schema-invalid
   `acceptance.json` counts as **not** completed.
3. **P4-T03 — `--lab-id` processes only the requested unit.** A `--lab-id` invocation whose
   prerequisites are all `ACCEPTED` executes that unit and no other; assert exactly one unit
   root gains new artifacts and `current_unit` names it.
4. **P4-T04 — `--all` processes manifest order without a manual invocation between units.**
   One CLI call advances across consecutive units; assert per-unit transitions were recorded
   in manifest order from a single process invocation with no operator step in between.
5. **P4-T05 — next-unit derivation and accepted-unit survival across resume.** Interrupt a
   run mid-unit, then `--resume`: assert every previously `ACCEPTED` unit's artifact hashes
   are byte-identical before and after, the run restarts at the first missing or invalid
   checkpoint, and `next_unit` is the correct manifest successor.
6. **P4-T06 — explicit run close and durable checkpoint.** Closing a partial run records the
   stated status and reason and a `resumable_checkpoint` that a later `--resume` actually
   consumes. Assert an unfinished run can never be closed as `COMPLETE` through the close
   path, and that killing the process at any recorded step leaves a usable checkpoint.
7. **P4-T07 — per-unit budgets reset, run-level limits do not.** Assert `per_lab.*` counters
   reset at each unit boundary while `per_run.*` and `convergence.*` accumulate; assert a run
   stops **before** exceeding a limit, names the binding limit with its value and the observed
   figure, preserves the checkpoint, and does not report an accepted unit.
8. **P4-T08 — only exact `ACCEPTED` advances or enters coverage.** Parameterise over
   `ACCEPTED`, `ACCEPTED_PENDING_REVIEW`, `BLOCKED`, `SYSTEM_FAILURE`, unattempted and
   schema-invalid receipts: only `ACCEPTED` appears in `completed_unit_ids`, permits advance,
   and is eligible for workbook coverage. Assert `runtime/workbook.assemble()` refuses a run
   whose coverage includes any non-`ACCEPTED` unit and that `run_status` stays non-`COMPLETE`.
9. **P4-T09 — a blocked unit stops the sequential run, loudly.** A unit whose receipt records
   `BLOCKED` for a named unavailable safety-critical fact halts `--all` at that unit; assert
   the run record names the external prerequisite, no later unit was attempted, and the unit
   was not skipped. Assert the run remains resumable once the prerequisite is supplied.
10. **P4-T10 — tool and factory failures become `SYSTEM_FAILURE`.** Inject a tool-invocation
    failure and a factory defect (invalid internal state, malformed artifact, renderer
    error). Assert both classify as `SYSTEM_FAILURE`, neither classifies as `BLOCKED`, and
    each `blocked_eligibility.never_a_block` category is covered.
11. **P4-T11 — negative control: unmet prerequisite.** `--lab-id` for a unit whose predecessor
    is unattempted, pending review, blocked or failed is refused with the unmet prerequisite
    named; assert zero artifacts were written and the run record is unchanged.
12. **P4-T12 — negative control: pending review.** A pending-review unit neither advances
    `--all` nor enters coverage nor permits `COMPLETE`; assert the run reports it as
    outstanding rather than done.
13. **P4-T13 — negative control: out-of-order and duplicate unit.** Requesting a later unit
    while an earlier one is unattempted is refused naming the correct next unit; re-requesting
    an already-`ACCEPTED` unit is refused; assert neither produces a duplicate transition
    record or a second acceptance for the same unit.
14. **P4-T14 — negative control: changed inputs.** Mutate a manifest, prompt or policy input
    contributing to the execution-contract digest, then `--resume`: the run is refused with
    the recorded and recomputed digests both reported; assert no artifact was written and no
    unit advanced.
15. **P4-T15 — negative control: accepted-unit overwrite.** Any rerun targeting an `ACCEPTED`
    unit in the same run root is refused and the unit's hashes are unchanged; assert overwrite
    succeeds only when a new output version is explicitly requested, and that doing so leaves
    the original run root byte-identical.
16. **P4-T16 — negative control: system failure does not corrupt the run.** After an injected
    `SYSTEM_FAILURE` mid-`--all`, assert previously accepted units are intact, the
    resumable checkpoint survives, no later unit was attempted, and the run is neither
    `COMPLETE` nor silently `IN_PROGRESS` without a stated reason.
17. **P4-T17 — negative control: false completion.** Construct a run root whose directories
    *look* finished (every unit directory present, PDFs present) but whose receipts are
    missing, pending, blocked or invalid. Assert `COMPLETE` is unreachable, the refusal names
    the first non-accepted unit, and no code path outside `runtime/workbook.assemble()` can
    write `COMPLETE`.
18. **P4-T18 — bounded three-unit live fixture.** Use the genericity fixture curriculum P3
    proved the engine neutral against; if P3 left none, author the minimal three-unit
    non-electronics fixture the plan's `scope_lock` permits — nothing larger, and not a
    production curriculum. With **live routed workers for every unit** (no hand-authored
    worker artifacts, no simulation), exercise in one sequence: `--all` advancement across all
    three units; an interrupt during the third; `--resume` to completion; and coverage
    computation. Assert live routing evidence (routing decision, executed model identity)
    exists for every unit, accepted hashes survive the interrupt, the digest is identical
    across the whole lifecycle, and coverage equals exactly the accepted set in manifest
    order. Record the full trace. This test cannot be satisfied by fixtures or fakes.
19. **P4-T19 — real Arduino-kit `--all` attempt.** Run `--all` against
    `curricula/arduino_kit` (35 units, `L01`–`L35`, from
    `curricula/arduino_kit/arduino_kit_curriculum.v5.yaml`) into a **fresh** output root;
    never into an existing one. Assert unit selection came from the frozen manifest, that the
    run either advances autonomously or stops at the first *genuine* external prerequisite
    with that prerequisite named and a resumable checkpoint written, and that engine layers
    contain no Arduino-specific identifier making this work. A stop is a legitimate outcome
    here; a stop misclassified as a factory defect, or a factory defect reported as a
    curriculum block, is a failure.

# LOOP

Run `P4-T01` through `P4-T19` in order. Do not skip ahead, reorder, waive, weaken or replace
a test, and do not begin `P4-T18` until `P4-T01`–`P4-T17` pass.

On a failure, record the test id, the exact command, the exit code, the resulting
`run_state.json`, the relevant artifact hashes and a narrow root cause. Revise **only** the
in-scope artifact the root cause names — never the test's expectation, never an accepted
unit's artifacts, never a gate threshold. Then rerun the failed test, then rerun every
earlier test whose evidence the revision could have changed (any change to
`schemas/run_lifecycle.schema.v1.json` or `runtime/run_state.py` requires rerunning from
`P4-T01`; any change to `runtime/run_curriculum.py` or the orchestration path requires
rerunning from `P4-T02`). After the last revision, run the full sequence once more clean, plus
`tests/run_gates.sh` and the whole `tests/runtime/` suite, and accept no new or worsened
result against the pre-change baseline.

**Stop without claiming success** if unit order or completion is inferred from filesystem
enumeration rather than the frozen manifest and this cannot be corrected in scope; if a
partial run can lose its resumable checkpoint or be reported as complete; if P3's handler
registry or terminal-receipt contract is absent or incompatible; if proving a definition-of-
success bullet would require weakening a gate, hardcoding a curriculum identifier, skipping a
blocked unit, or hand-authoring worker output; or if live routes are unavailable for `P4-T18`.
Report the stop with its evidence rather than a partial success. Never respond to a failure by
deleting a run root, editing frozen receipts, relaxing the lifecycle schema, reclassifying a
factory defect as `BLOCKED`, or substituting simulated output for live worker output.

Before claiming P4 done, write
`plans/19_curriculum_factory_production_loop_closure/results/P4.result.v1.md` containing: the
pre-change baseline; every changed path with its diff summary; each test id with its command,
exit code and pass/fail; the complete `P4-T18` three-unit fixture run trace (per-unit routing
evidence and executed model, transitions, interrupt point, resume restart point, hashes before
and after resume, final coverage and lifecycle record); the result of each negative control
`P4-T11`–`P4-T17` stating what was refused and how; the `P4-T19` Arduino `--all` outcome with
the output root, the units attempted, and either the advance record or the exact external
prerequisite it stopped on; the per-unit and run-level limit figures observed; any remaining
failure; and the final verdict. Claim completion only when `P4-T01` through `P4-T19` have all
passed, including the live fixture and the real Arduino attempt, and every one of the phase's
four definition-of-success bullets is backed by a named test in that file.
