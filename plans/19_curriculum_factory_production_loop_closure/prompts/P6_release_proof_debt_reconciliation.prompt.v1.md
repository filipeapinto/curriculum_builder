# GOAL

Execute phase **P6 — End-to-end release proof and debt reconciliation** of
`plans/19_curriculum_factory_production_loop_closure/curriculum_factory_production_loop_closure.plan.v1.yaml`.

**Resolve paths first.** The `plans/` tree has been renumbered with ordinal prefixes.
`PLAN_DIR` = `plans/19_curriculum_factory_production_loop_closure/` (holding the plan YAML,
schema, phase prompts, and reviews) — confirm this is still the single live plan directory
before doing anything else, and use it for every plan-relative path below. The same applies
to `plans/03_folder_refactoring/`, referenced below as `FOLDER_REFACTORING_PLAN` =
`plans/03_folder_refactoring/folder_refactoring.plan.v6.md`.

Read the plan file first in full: `overall_goal`, `scope_lock`, `operating_rules`, and
`red_team_protocol.severity` bind this phase, and the P6 block is authoritative over
anything below that contradicts it. P6 `depends_on: [P5]`; do not start until
`PLAN_DIR/results/P0.result.v1.md` through `P5.result.v1.md` all exist and record
success. P6 is the final phase: it adds no
capability. It proves the loop that P0–P5 built, and then updates only the obligations
that the proof makes literally true.

Prove three things by running them, from fresh output roots: one clean live single-unit
production run, one bounded unrelated full-manifest fixture driven to COMPLETE through
`--all`, and one Arduino-kit production attempt. Then reconcile deferred obligations
**RT-1, RT-2, RT-3, RT-4, RT-5, RT-7, RT-10**, the check mappings, and the status
documents — each one only when its own recorded criterion is discharged.

The RT- registry is `policy/deferred.v1.yaml` (schema `schemas/deferred.schema.v1.json`).
Bind every ID by reading its `obligation`, `acceptance_criterion`, `blocked_by`,
`promotes_gate`, and `promoted_id` fields verbatim from that file at execution time. Do
not paraphrase a criterion, do not infer one from an ID's name, and do not act on any
summary of these obligations — including this prompt's. Three structural facts about that
file constrain every edit to it:

- `policy/deferred.v1.yaml` is mirrored exactly by section 12 of
  `FOLDER_REFACTORING_PLAN` (the RT- catalogue rows near line 1357). Gate **FR-P2-DEFERRED** proves the two agree in both directions and that
  every RT- citation anywhere in the repository resolves. Any edit to one must be
  mirrored in the other in the same change.
- FR-P2-DEFERRED reads comments as citations. The number 9 must stay free: defining
  `RT-9` would make `tests/fixtures/deferred_reference_dangling.reject.yaml` accepted and
  break the gate for the exact reason that fixture exists.
- **RT-6** is already discharged and **RT-8** is not in this phase. Do not touch either.

Hard constraints, in force for the whole phase:

- Preserve the precedence and ownership rules in `meta_prompt/curriculum.prompt.v1.md`
  and `policy/controller.v1.yaml`.
- Keep simulated evidence, live-capability evidence, generated-unit evidence, and
  workbook-release evidence as four distinct categories; never let one stand for another.
- Never infer success from file presence. Validate declared outputs, hashes, checks,
  transitions, and terminal decisions.
- A worker may write only its declared schema-bound artifact and may never decide
  transitions or acceptance.
- A blocked curriculum fact, a retryable tool failure, and a factory defect remain three
  separate terminal classifications.
- Preserve accepted units on resume; refuse overwrite unless a new output version is
  explicitly requested.
- Update policy, schema, checks, and deferred claims atomically, and only when their
  enforcement actually becomes true.
- **Never claim more coverage, genericity, review, child-readiness, or completion than
  the recorded evidence supports.** This outranks any pressure to close the plan.
- Stop when a definition of success cannot be proven.

Scope discipline, from P6 `out_of_scope`: do **not** declare the Arduino workbook complete
while required automated reviews or genuine external safety-critical evidence remain
unresolved, and do **not** add a production curriculum merely to satisfy genericity — the
unrelated fixture exists only to prove engine neutrality.

Existing user work is protected. `outputs/arduino_kit_run_v2/` was produced by manual
session-bridge shepherding; it is prior work, not P6 evidence. Do not use it as release
proof, and do not delete, move, or edit it. The authoritative output-root contract is
enforced by `runtime/io.py::require_internal_output` (the root must resolve beneath
`ENGINE/outputs/`) and stated at `meta_prompt/curriculum.prompt.v1.md:12`; per-unit layout
is `<output_root>/<UNIT_ID>/` per `runtime/run_state.py`. `outputs/` is gitignored, so
release evidence is carried by recorded paths, hashes, and receipts, not by committed
artifacts — say so plainly rather than implying committed proof.

# TEST

Run P6-T01 through P6-T17 in order. Every test is pass/fail against a recorded command,
exit code, and artifact hash. Do not skip ahead, waive, reorder, or weaken a test.

1. **P6-T01 — Preconditions and frozen baseline.** Confirm P0–P5 result files exist and
   record success. Freeze the P0 implementation matrix, canonical digest algorithm, and
   inventory by hash. Before any P6 mutation, capture the baseline: `python3 -m pytest
   tests/runtime/`, `bash tests/run_gates.sh 5`, `python3 tests/gates/fr_p4_policy_schemas.py
   --check validate`, `python3 tests/gates/fr_p0_structure.py --check schema`, and
   `python3 tests/check_meta_prompt.py`. Record per-gate ids and results. Fails if any
   baseline artifact is unreadable or if the P0 matrix cannot be resolved to a hash.

2. **P6-T02 — Clean live single-unit run.** From a *fresh, empty* output root beneath
   `outputs/`, run the production CLI's `--lab-id` path (`runtime/run_curriculum.py`, or
   the P3/P4-designated production entry point, using the flag names P4 actually
   implemented) against a curriculum whose prerequisites are satisfied. Passes only if the
   unit reaches an honest terminal state through factory-owned requests and workers. Fails
   if the run falls through to simulation, refuses unconditionally, or requires a manual
   invocation between states.

3. **P6-T03 — No manual shepherding in the run root.** Hash-inventory the P6-T02 run root
   at completion. Every file must trace to a factory-issued worker request, route decision,
   or code-owned record, with no file created or edited by hand and no prewritten worker
   artifact staged in advance. Fails on any unattributable file, any post-hoc edit
   timestamp inside the run root, or any artifact whose hash is not bound by a receipt.

4. **P6-T04 — Unrelated full-manifest fixture reaches COMPLETE.** Use the bounded
   non-electronics fixture curriculum defined by P0/P4 (today `curricula/` holds only
   `arduino_kit`; the fixture must live wherever the P0-frozen contract places test
   curricula, **not** be promoted into a production curriculum to inflate a count). From a
   fresh output root, run `--all`. Passes only if every manifest unit is processed in
   manifest order with no manual invocation between units and `run_status` reaches
   COMPLETE through the single code path authorized by P5 to write it.

5. **P6-T05 — Every fixture unit used live workers.** For each unit in P6-T04, show a
   routing decision, executed-model identity equal to the decided model, captured worker
   result, and append-only execution record. Fails if any unit was produced in simulation
   or test mode, or if executed model identity is absent or unobserved.

6. **P6-T06 — Independent recomputation of the fixture terminal decision.** Recompute
   coverage, page hashes, check verdicts, log pairs, and the **execution-contract digest**
   from immutable inputs and receipts alone. The recomputed terminal decision must equal
   the recorded one. Fails on any digest mismatch, any unit bound to a different digest,
   or any decision reproducible only by trusting a controller conclusion.

7. **P6-T07 — Interrupt and resume.** Interrupt the fixture run mid-sequence (via the
   P3/P4 interrupt mechanism), then resume. Accepted units must be preserved with valid
   hashes, the run must restart at the first missing or invalid checkpoint, and no accepted
   artifact may be overwritten or manually repaired. Fails if resume loses a checkpoint,
   rewrites accepted work, or continues past an unresolved hash mismatch.

8. **P6-T08 — Workbook assembly and terminal audit.** For the fixture, prove exact
   accepted-unit coverage in manifest order, every shipped page rasterized and inspected
   and resolving to the assembled PDF hash, exactly four schema-valid isolated reviews, and
   a clean terminal log audit. Fails if coverage is inferred from directory enumeration or
   if COMPLETE is written outside workbook acceptance.

9. **P6-T09 — Arduino-kit production attempt.** From a fresh output root (never
   `outputs/arduino_kit_run_v2/`), run `--all` against `curricula/arduino_kit`. Passes if
   real manifest selection and production routing are proven **and** the run either
   advances autonomously or stops at the first genuine external prerequisite with a
   correctly classified, resumable, truthful receipt — BLOCKED only for a named
   unavailable safety-critical fact, never for a tool or factory defect. Fails if a factory
   defect is dressed as BLOCKED, if a real prerequisite is dressed as SYSTEM_FAILURE, or if
   the run is reported as complete. Supplying the prerequisite and continuing is permitted;
   declaring the Arduino workbook complete while required automated reviews or genuine
   external safety-critical evidence remain unresolved is not.

10. **P6-T10 — Negative controls still bite.** Re-run the P1–P5 negative controls against
    the P6 runs' real records: execution-contract digest mismatch refused; simulated output
    rejected as unit evidence; accepted-unit overwrite refused; unmet prerequisite,
    out-of-order and duplicate unit, pending review, and false completion all refused;
    routing bypass and unrecorded call refused at runtime. Fails if any control passes
    only against a static fixture when the plan requires runtime refusal.

11. **P6-T11 — Full suite and gates, compared to baseline.** Re-run every command from
    P6-T01. Compare gate-by-gate against the P6-T01 baseline by gate id. Accept no new or
    worsened result. Fails on any regression, any newly skipped gate, or any test made to
    pass by weakening an assertion.

12. **P6-T12 — P0 matrix reconciliation.** Compare the produced records against the frozen
    P0 implementation matrix and account for **every** controller state, route, check, and
    deferred obligation: exercised-and-proven, deliberately not exercised with a reason, or
    unmet with a named residual. Fails if any matrix row is unaccounted for.

13. **P6-T13 — RT-7 stale-path repair.** RT-7's criterion names `curricula/<name>/units/`;
    no writer, schema, or runtime module produces that path. Repair it against the
    authoritative output-root contract named in GOAL, recording the **exact
    before text and exact after text** of the criterion in the result file. Then apply the
    repaired criterion literally to every site that repeats the stale path — at minimum
    `policy/deferred.v1.yaml`, `policy/checks.v1.yaml`, `tests/gates/fr_p5_unit.py`
    (including `unit_files()` and the module docstring), `runtime/readability.py`, and the
    RT-7 row in `FOLDER_REFACTORING_PLAN`. Repair means
    correcting a path that was always wrong; it does not mean relaxing what the criterion
    demands. Fails if the repair lowers the evidentiary bar, if the mirror disagrees, or if
    FR-P2-DEFERRED, FR-P5-READABILITY, FR-P5-BLOOM-VERBS, FR-P5-DERIVATION, or
    FR-P5-RECEIPT-HASH do not pass afterwards with their scanned-unit counts stated
    honestly.

14. **P6-T14 — Obligation disposition, criterion by criterion.** For each of RT-1, RT-2,
    RT-3, RT-4, RT-5, RT-7, RT-10, quote the criterion verbatim, cite the specific P6
    evidence (run id, artifact path, hash, test id), and record exactly one of
    **DISCHARGED** or **UNCHANGED BLOCKER** with the residual named. Discharge only on the
    literal, unweakened criterion. Where a `promoted_id` exists (RT-3 →
    FR-P2-BYPASS-ENFORCED, RT-4 → FR-P2-UNRECORDED-FATAL), renaming the gate in
    `tests/gates/registry.py` and every citation is part of discharging it, and is
    forbidden otherwise. RT-5 must be resolved per-ID: every id FR-P4-CHECK-MAPPING reports
    as MAPPED, NOT EXECUTED, plus every A-series id in `policy/failures.v1.yaml`. RT-10
    requires both legs — an unrelated curriculum running to completion with no edit to
    `meta_prompt/curriculum.prompt.v1.md`, **and** FR-P5-ENGINE-GENERIC passing with more
    than one curriculum present; if the second leg would only be met by promoting the
    neutrality fixture into a production curriculum, that is out of scope, so record RT-10
    as an unchanged blocker with the residual stated rather than satisfying it by
    relocation. Fails if any ID is closed without literal discharge, if a criterion is
    edited to fit the evidence, or if the mirror or FR-P2-DEFERRED breaks.

15. **P6-T15 — No document overclaims.** Sweep every document that asserts coverage,
    genericity, review status, child-readiness, or completion, and align each to recorded
    evidence: `readme.md`, `docs/how_it_works.md`, `policy/deferred.v1.yaml`,
    `policy/checks.v1.yaml`, the `tests/gates/fr_p5_unit.py` docstring, `issues/README.md`
    and the issue files it indexes, the RT- rows in
    `FOLDER_REFACTORING_PLAN`, and any curriculum status or
    teaching-readiness document under `curricula/arduino_kit/`. Both directions are
    failures: a document that still says nothing has ever been generated when P6 generated
    it, and a document that claims release, review, or child-readiness that P6 did not
    prove. Fails on any residual overclaim or on a corrected claim without a cited
    artifact.

16. **P6-T16 — Operator documentation is executable.** Produce operator documentation
    containing the **exact** production, resume, inspect, and failure-recovery commands.
    Every command must have been run verbatim during P6 with its output recorded. Fails if
    any documented command is untested, uses a flag the CLI does not accept, or references
    a path outside the authoritative output-root contract.

17. **P6-T17 — Independent audit.** An independent auditor — a separate session that
    receives immutable inputs, receipts, hashes, and schemas, and does **not** receive
    controller conclusions, terminal records' verdict fields, or this phase's own
    narrative — recomputes the terminal decision for all three runs (P6-T02, P6-T04/T07/T08,
    P6-T09). Every recomputed decision must match. The auditor also confirms zero
    unresolved Critical or High findings under the plan's `red_team_protocol.severity`
    definitions. Fails on any divergence, or on any Critical or High finding left open.

# LOOP

Execute the tests in order. On a failure: record the test id, exact command, exit code,
evidence hashes, and a narrow root cause. Fix the root cause in the smallest in-scope
artifact — never by adjusting the test, relaxing a criterion, or reclassifying a failure.
Then rerun the failed test, plus every earlier test whose evidence the fix could have
invalidated, plus every later test. Any change touching `policy/deferred.v1.yaml`,
`tests/gates/registry.py`, or the folder-refactoring mirror requires an immediate rerun of
FR-P2-DEFERRED and FR-P4-CHECK-MAPPING before continuing. Any change to runtime or policy
requires rerunning P6-T11 before any completion claim.

P6 is the last phase, so a failure here means the **plan** is not finished — it never
means the scope should grow. If a P6 failure has its root cause in P1–P5 work, the correct
response is a narrow repair in the owning phase's artifact plus a rerun of that phase's
gate and all of P6; it is not new capability, not a new curriculum, and not a relaxed
gate.

Stop — without claiming success, leaving the repository in a consistent state, and writing
the result file with the blocker named — if any release proof would rely on simulated
output, prewritten worker artifacts, or manual mutation inside the run root, or if closing
a deferred obligation would require weakening its original acceptance criterion. Also stop
rather than: deleting or editing `outputs/arduino_kit_run_v2/` or any other pre-existing
user work; defining `RT-9`; declaring the Arduino workbook complete while required
automated reviews or genuine external safety-critical evidence remain unresolved; or
promoting the neutrality fixture into a production curriculum to make a genericity count
pass.

Before claiming done, write `PLAN_DIR/results/P6.result.v1.md` containing: the
P6-T01 baseline and the final gate-by-gate comparison; full traces for all three runs
(command line, output root, run id, execution-contract digest, per-unit states and hashes,
terminal decision, and for the Arduino run the exact classification and named prerequisite);
the P6-T12 matrix reconciliation; RT-7's exact before/after criterion text; the RT-
obligation disposition table for RT-1, RT-2, RT-3, RT-4, RT-5, RT-7, RT-10 with verbatim
criteria, cited evidence, and DISCHARGED or UNCHANGED BLOCKER per ID; the document
reconciliation list; the operator command list with recorded outputs; the independent audit
result including the auditor's inputs and what was withheld from it; and any remaining
failure or residual. Note explicitly that run roots under `outputs/` are gitignored and
that the evidence is carried by recorded hashes and receipts.

This result file, together with the six prior phase result files
(`results/P0.result.v1.md` … `results/P5.result.v1.md`), constitutes the completion
evidence for the whole plan, all seven resolved under the same `PLAN_DIR`. Claim the plan
complete only when P6-T01 through P6-T17 have
all passed, the independent audit reproduced every terminal decision, and zero Critical or
High findings remain open. If some obligations remain unchanged blockers, that is a
truthful outcome and must be reported as such — it is not a reason to close them.
