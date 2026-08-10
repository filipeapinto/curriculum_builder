# GOAL

Implement phase **P3 — Production unit state machine** of
`plans/19_curriculum_factory_production_loop_closure/curriculum_factory_production_loop_closure.plan.v1.yaml`
(status `approved`, final_gate `approved`). Read that file first: `overall_goal`, `scope_lock`,
`operating_rules`, and `red_team_protocol.severity` bind this phase in full, and the phase block
`id: P3` is the authority for scope. Nothing here overrides it; where this prompt and the plan
disagree, the plan wins and you stop to say so.

P3 `depends_on: [P2]`. P0, P1 and P2 execute before you. Consume their outputs **by contract, never
by reimplementation**:

- **P0** froze the unit and workbook state list, the canonical terminal vocabulary (with detailed
  failure IDs kept separate), the neutral domain-declared role contract, the derived unit-identifier
  contract, the per-state code owner and expected artifact table, and the canonical digest algorithm.
- **P1** owns capability preflight, the frozen effective route manifest, the run's
  execution-contract digest, and decided-versus-executed model enforcement.
- **P2** owns the single worker invocation interface, sealed request construction, staged-filesystem
  containment, atomic output admission, failure normalization, and the worker-artifact schema registry.

Read `plans/19_curriculum_factory_production_loop_closure/results/P0.result.v1.md`,
`.../P1.result.v1.md` and `.../P2.result.v1.md` to discover the actual frozen names, paths and
interfaces. **If any of those three records is absent, or does not name the frozen state list,
terminal vocabulary, identifier contract, role contract, digest algorithm, or worker adapter entry
point, stop and report P3 unstartable — do not invent the freeze and do not re-freeze it here.**

Goal: implement every declared unit state as executable code and connect worker stages to
deterministic validation and targeted revision.

## Hard constraints (from `operating_rules`, applied literally)

1. Preserve the precedence and ownership rules already declared in
   `meta_prompt/curriculum.prompt.v1.md` and `policy/controller.v1.yaml`.
2. Treat simulated evidence, live-capability evidence, generated-unit evidence, and workbook-release
   evidence as distinct categories.
3. Never infer success from file presence; validate declared outputs, hashes, checks, transitions,
   and terminal decisions.
4. A worker may write only its declared schema-bound artifact and may never decide transitions or
   acceptance.
5. **A blocked curriculum fact, a retryable tool failure, and a factory defect remain separate
   terminal classifications.** A named safety-critical fact that stays unavailable after recorded
   official-manufacturer and primary-source searches is the only legal `BLOCKED`. A transient tool,
   source or image failure is a bounded retry class under `policy/limits.v1.yaml → retry`. Any schema,
   render, layout, model, image-generation or engine defect is a factory defect and resolves to the
   P0-frozen system-failure terminal, never to `BLOCKED` (`policy/controller.v1.yaml →
   blocked_eligibility.never_a_block`).
6. Preserve accepted units on resume and refuse overwrite unless a new output version is explicitly
   requested.
7. Execute phases in dependency order; atomically update policy, schema, checks, and deferred claims
   when their enforcement becomes true.
8. Stop when a phase definition of success cannot be proven.

## What exists today (the real starting state)

- `runtime/controller.py` — `CurriculumRuntime.simulate()` is the state simulation: it walks
  `self.states` (loaded from `policy/controller.v1.yaml`, 25 states `VALIDATE` … `FINAL_ACCEPTANCE`),
  writes `simulated/states/NNN_STATE.json` per state, and has one linear `legal_transition()`. There
  are no per-state handlers. `static_preflight()`, `validated_manifest()`, `run_verifier_fixtures()`
  and `_logger_gate()` are real and reusable.
- `runtime/session_bridge.py` — the manual bridge this phase must migrate or reduce. `prepare()`
  freezes inputs, fetches sources, calls `visual_maps.regenerate_assets()`, writes
  `worker_request.json`, then **deliberately returns `INTERRUPTED` so a human/in-session model writes
  `workers/domain.json` and `workers/lab.json` by hand**; `finalize()` then scores checks and decides
  a terminal state. It hardcodes `MODEL_ID = "gpt-5.6-sol"`, `CROSS_FAMILY_BYPASS`, a `--lab-id L01`
  default, Arduino-only companion filenames (`kit_calibration.v1.yaml`, `circuit_library.v1.yaml`) and
  electronics constraint prose.
- `runtime/checks.py` — `required_checks_for()` builds the required set from `policy/checks.v1.yaml`
  plus `curricula/<name>/checks.v1.yaml`; `ENGINE_REQUIRED`, `CURRICULUM_REQUIRED` and `NON_BLOCKING`
  are engine constants; `_claimful_strings()` hardcodes electrical vocabulary
  (`domain.electrical.ratings_and_limits`, `mA`/`V`/`ohm` unit words).
- `runtime/visual_maps.py` — `_ROLE_CLASSES`, `classify_role()`, `render_breadboard()`,
  `regenerate_assets()`; `runtime/lesson_render.py:366` branches on `kind == "breadboard"`.
- `runtime/checkpoint.py` (`Checkpoints.write()`, `valid_prefix()`), `runtime/run_state.py`
  (`record_unit_transition()`, `assert_resumable()`, `close_run()`), `runtime/logger.py`,
  `runtime/io.py` (`require_internal_output` — run roots must resolve beneath the engine's
  `outputs/`), `runtime/run_curriculum.py` (CLI; today production raises
  `LIVE-GENERATION-NOT-PREFLIGHTED`).
- `policy/limits.v1.yaml` — `per_lab.max_revisions=3`, `convergence.repeat_failure_threshold=2`,
  `retry.malformed_structured_output=1`, `retry.transient_worker_source_or_image_failure=1`.
- `tests/gates/fr_p4_policy_schemas.py:171` `check_mapping()` registered as `FR-P4-CHECK-MAPPING`.

Two live contradictions you must resolve **using the P0 freeze, not your own judgement**:
`session_bridge.finalize()` currently sets `terminal_state = "BLOCKED"` for *any* blocking check
failure — including schema, render and PDF defects — which violates `blocked_eligibility`; and
`ACCEPTED_PENDING_REVIEW` is written by `finalize()`/`run_state.py` while
`policy/controller.v1.yaml → terminal_states` lists only `ACCEPTED`, `BLOCKED`, `SYSTEM_FAILURE`.
Apply the P0-frozen canonical vocabulary; if P0 did not reconcile these, stop.

## Build

- A **state-handler registry** with exactly one production handler per P0-frozen unit state, and no
  production state outside the controller contract. Registry totality is enforced at import time.
- **Simulation is retained as a separate test mode.** `--test-simulated-all` and `--test-golden-l01`
  keep working, keep writing simulated-evidence-labelled records, and are unreachable from the
  production path.
- **Code-owned services**: transition, review aggregation, targeted revision, checkpoint, resume, and
  terminal decision. Review aggregation reads schema-valid review records only; a model never
  aggregates, never chooses the next state, and no transition or acceptance may depend on
  unstructured model prose.
- **Integration** of session preparation, research, domain and lab production, visuals, rendering,
  reviews, acceptance, checkpoints and resume through the P2 worker adapter for every model-produced
  artifact.
- **Targeted revision only**: revise exactly the artifacts named by the failed checks, under
  `per_lab.max_revisions` and `convergence.repeat_failure_threshold`.
- **P0-frozen neutral domain-declared roles and derived unit IDs**: the engine binds roles and
  identifiers the curriculum declares. Arduino vocabulary lives under `curricula/arduino_kit/`, not in
  engine layers. Prerequisite validation is semantic (a prerequisite resolves to an accepted unit that
  actually supplies the named idea), not id-existence.
- **Session-bridge disposition**: migrate `runtime/session_bridge.py` into the controller path, or
  reduce it to a tested internal adapter with no production CLI entry point and no manual
  prepare/finalize handoff. Record which, and why.
- **A validated check-to-owned-artifact mapping** giving every blocking check exactly one bounded
  revision route or one non-revision terminal class.

## Out of scope (stop rather than do)

Rewriting accepted prerequisites; regenerating an entire unit for one local defect; letting a model
aggregate reviews; redesigning curriculum schema, pedagogy, visual style or the Arduino sequence;
hand-authoring worker artifacts; weakening any safety, evidence, visual, review or acceptance gate to
make a run pass; P4's `--all`/manifest orchestration and P5's workbook loop. Do not mutate existing
run roots (e.g. `outputs/arduino_kit_run_v2`) or any pre-existing dirty user work; use fresh output
roots beneath `outputs/`.

# TEST

Run `P3-T01` through `P3-T24` in order. Each is a committed, deterministic, re-runnable test (pytest
under `tests/runtime/`, or a registered gate) with a recorded command and exit code. No test may be
waived, reordered, weakened, or replaced by inspection.

1. **P3-T01 — Registry totality.** The production handler registry has exactly one handler per
   P0-frozen unit state: no state without a handler, no handler without a frozen state, no duplicate.
   Deleting or duplicating one entry fails the test.
2. **P3-T02 — No production state outside the contract.** Every state name appearing in a production
   checkpoint, execution-log transition record, or terminal record is a member of the frozen state
   list; an injected out-of-contract state name is rejected at write time, not at audit time.
3. **P3-T03 — Every frozen state is reachable in production.** Union of states traversed across the
   production tests (including P3-T24) equals the frozen state list; any never-entered state fails
   with its name.
4. **P3-T04 — Simulation retained and isolated.** `--test-simulated-all` and `--test-golden-l01` still
   pass and still label their output simulated evidence; a test asserts no production code path can
   reach `CurriculumRuntime.simulate()` (or its successor) and that simulated records can never be
   counted as generated-unit evidence.
5. **P3-T05 — No electronics vocabulary in engine layers.** A scan of engine modules (`runtime/`,
   `policy/` engine files, `schemas/`, excluding `curricula/`) finds no curriculum-specific domain
   token (`breadboard`, `resistor`, `multimeter`, `polarity`, `arduino`, `electrical`, `circuit`, and
   the `_ROLE_CLASSES`/`render_breadboard`/`lesson_render.py:366` branches as they stand today).
   Renderers and role classes resolve from curriculum-declared data. Every allowed exception is an
   explicit, justified allowlist entry in the test itself.
6. **P3-T06 — Unrelated curriculum binds its own roles and IDs.** A minimal non-electronics fixture
   curriculum declares its own domain roles and its own unit identifiers, valid under the P0-frozen
   identifier contract and not the Arduino sequence, and executes the production state path with
   **zero edits to engine code** — proven by a byte-identical hash of every engine module before and
   after the fixture run.
7. **P3-T07 — Semantic prerequisite validation.** A unit whose declared prerequisite names an idea no
   accepted prior unit supplies is rejected with the unmet idea named; a prerequisite that merely
   points at an existing unit id does not satisfy the check.
8. **P3-T08 — Clean unit reaches acceptance.** A unit with zero blocking failures traverses the full
   state path and records the P0-frozen accepted terminal, with every intermediate record present.
9. **P3-T09 — Targeted revision revises only named artifacts.** Inject one local defect (one failed
   check naming one artifact). Assert: only that artifact's bytes change, every other artifact's
   SHA-256 is identical before and after, the revision worker's authorized-output list contains
   exactly the named artifact, and the unit is not regenerated.
10. **P3-T10 — Transient retry is bounded and classified.** A transient tool/source/image failure
    retries exactly `policy/limits.v1.yaml → retry` times, then resolves to the retry-exhausted
    classification — never to `BLOCKED`.
11. **P3-T11 — Repeated identical failure terminates per policy.** The same failed-check set recurring
    up to `convergence.repeat_failure_threshold` / `per_lab.max_revisions` terminates the unit with the
    binding limit, its value and the observed figure recorded, and the last valid checkpoint preserved.
12. **P3-T12 — Legal block.** A named safety-critical fact unavailable after recorded
    official-manufacturer and primary-source searches yields `BLOCKED` with the fact, the searches and
    their receipts named in the record.
13. **P3-T13 — Factory defect is never a block.** Schema-invalid worker output, a render/PDF toolchain
    failure, and an image-generation failure each yield the P0-frozen system-failure terminal, never
    `BLOCKED` — including through whatever survives of `session_bridge.finalize()`.
14. **P3-T14 — Interrupt.** An interrupt at an arbitrary state leaves a valid last checkpoint, a
    truthful interrupted record, and no partial artifact admitted.
15. **P3-T15 — Resume.** Resume from P3-T14 revalidates prior checkpoint hashes, restarts at the first
    missing or invalid checkpoint, rebuilds nothing already valid, and completes without any manual
    file repair.
16. **P3-T16 — Resume never overwrites accepted work.** Resume against a unit already recorded accepted
    is refused unless a new output version is explicitly requested; an unresolved hash mismatch halts
    the resume instead of continuing.
17. **P3-T17 — Negative: illegal transition.** A transition not permitted by the frozen contract is
    rejected before any artifact or checkpoint is written.
18. **P3-T18 — Negative: skipped state.** Advancing past a state whose handler never completed is
    rejected and names the skipped state.
19. **P3-T19 — Negative: duplicated completion.** Recording completion twice for one state, or
    replaying a completed handler, neither duplicates log entries nor mutates the accepted artifact.
20. **P3-T20 — Negative: stale hash.** A checkpoint whose recorded input/output hash no longer matches
    disk halts the run; it is never repaired silently or treated as valid prefix.
21. **P3-T21 — Negative: broad rewrite.** A revision attempt that writes any artifact not named by the
    failed check, or that regenerates the unit for one local defect, is rejected and the accepted
    artifacts are unchanged.
22. **P3-T22 — Negative: false block.** A `BLOCKED` record without a named unavailable safety-critical
    fact plus its recorded searches is rejected; a model-prose-only justification is rejected; and a
    transition or acceptance decision derived from unstructured model prose is rejected.
23. **P3-T23 — Check-to-owned-artifact mapping.** Reading `policy/checks.v1.yaml` and
    `curricula/<name>/checks.v1.yaml` as one inventory (as `runtime/checks.py:required_checks_for` and
    `FR-P4-CHECK-MAPPING` already do), the test **fails** if any blocking check lacks exactly one
    authorized correction route or exactly one non-revision terminal class — zero routes, two routes,
    or a route naming an artifact no handler owns all fail, each naming the offending check id.
24. **P3-T24 — Live full-state-path unit run.** One real unit is produced end to end into a **fresh**
    output root beneath `outputs/`, through the P2 worker adapter and P1-proven routes, traversing the
    complete state path. Assert: every intermediate record exists (per-state checkpoints, routing
    decisions, worker requests/receipts, review records, check results, terminal record); every file
    under the run's worker artifact directory is attributable to a logged adapter invocation with a
    routing decision and matching output hash; **no hand-authored worker file exists**; the
    execution-contract digest is bound in every record; and the terminal state is a P0-frozen terminal
    that the recorded checks actually justify. A simulated, prewritten, or manually edited artifact
    cannot satisfy P3-T24.

Finally re-run the full runtime suite (`python3 -m pytest tests/runtime -q`) and the applicable phase
gates (`tests/gates/runner.py`, including `FR-P4-CHECK-MAPPING`); accept no new or worsened result
against the P0-recorded baseline.

# LOOP

Execute P3-T01 → P3-T24 in order. On any failure, record the test id, exact command, exit code,
evidence hashes and a narrow root cause; fix **only** the in-scope artifact the failure names; then
rerun P3-T01, P3-T02 and P3-T23 immediately (registry, contract and mapping invariants), then the
failed test, then every later test whose evidence could have changed. Repairing a failure by widening
scope — regenerating a whole unit, rewriting an accepted prerequisite, editing engine code to satisfy
the fixture curriculum, or hand-writing a worker artifact — is itself a failure of P3-T06, P3-T21 or
P3-T24 and must be reverted.

Convergence: the same failed test with the same root cause recurring twice without narrowing ends the
attempt. Record the binding limit, its value and the observed figure, preserve the last valid
checkpoint, and report the phase blocked. Never respond to a failure by relaxing a check, deleting a
negative control, marking a blocking check non-blocking, reclassifying a factory defect as `BLOCKED`,
substituting simulated for generated-unit evidence, or mutating a pre-existing run root or user work.

**Stop immediately, without claiming success, if:** a controller transition or acceptance decision
would depend on unstructured model prose; resume could overwrite accepted work or continue past an
unresolved hash mismatch; a P0/P1/P2 handoff record is missing or does not name the artifact you need;
the P0 freeze does not reconcile the canonical terminal vocabulary or the `BLOCKED`-versus-system-
failure boundary; or a definition-of-success bullet cannot be proven with a deterministic test.

Before claiming done, write
`plans/19_curriculum_factory_production_loop_closure/results/P3.result.v1.md` containing: the complete
state-handler registry (each frozen state → handler → owned artifact → owning module); the
session-bridge disposition (migrated or reduced, with the resulting entry points); the check-to-owned-
artifact mapping with each blocking check's single correction route or terminal class; the full
P3-T24 live run trace (run root, per-state checkpoint ids and hashes, routing decisions, executed
models, worker artifact hashes, check results, terminal record, execution-contract digest); the
per-test result table for P3-T01…P3-T24 with commands, exit codes and evidence hashes; the
negative-control outcomes for P3-T17…P3-T22 stating what each rejected and how; the gate and suite
comparison against the P0 baseline; and any remaining failure or blocked item stated plainly. Append —
never rewrite — the outcome to the plan's execution log.

Claim P3 complete only when every P3-T01…P3-T24 test passes, including the live full-state-path run,
every P3 definition-of-success bullet is discharged by a named passing test, and no Critical or High
red-team finding is unresolved.
