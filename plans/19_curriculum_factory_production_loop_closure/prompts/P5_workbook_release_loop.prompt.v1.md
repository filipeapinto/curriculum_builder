# GOAL

Implement phase **P5 — Workbook release loop** of
`plans/19_curriculum_factory_production_loop_closure/curriculum_factory_production_loop_closure.plan.v1.yaml`
(status `approved`, red-team `final_gate: approved`). Read that file first: `overall_goal`,
`scope_lock`, `operating_rules` and `red_team_protocol.severity` bind this phase, and the
`P5` block is authoritative over any paraphrase below.

P5 `depends_on: [P4]`. Do not start until P4 has executed and left a run that reached
manifest-order unit acceptance. Consume P4 **by contract**: the immutable
execution-contract digest, the frozen manifest unit order, the run lifecycle record at
`OUTPUT_ROOT/run_state.json` (`schemas/run_lifecycle.schema.v1.json`), and the rule that
only an exactly-`ACCEPTED` unit may enter workbook coverage. Consume P0 by contract for
the frozen workbook state table. If P0 froze no workbook states, or P4 left no digest,
**stop** — that is an upstream defect, not a licence to invent states.

Build: the workbook state handlers, the assembly manifest, the page inventory, exactly
four isolated workbook review records, revision receipts, the terminal workbook
acceptance record, and **one** code path permitted to write `run_status: COMPLETE`.

## Hard constraints

Operating rules, applied literally to this phase:

1. Preserve the precedence and ownership rules already declared in
   `meta_prompt/curriculum.prompt.v1.md` and `policy/controller.v1.yaml`.
2. Treat simulated evidence, live-capability evidence, generated-unit evidence, and
   workbook-release evidence as distinct categories.
3. **Never infer success from file presence; validate declared outputs, hashes, checks,
   transitions, and terminal decisions.**
4. A worker may write only its declared schema-bound artifact and may never decide
   transitions or acceptance.
5. A blocked curriculum fact, a retryable tool failure, and a factory defect remain
   separate terminal classifications.
6. Preserve accepted units on resume and refuse overwrite unless a new output version is
   explicitly requested.
7. Execute phases in dependency order; atomically update policy, schema, checks, and
   deferred claims when their enforcement becomes true.
8. Stop when a phase definition of success cannot be proven.

In scope, and nothing beyond it: assemble only exact accepted-manifest coverage, render
every page, execute the declared workbook reviews, target workbook-only revisions, audit
release, and implement the P0-frozen workbook states under the same code-owned
transition, checkpoint and audit rules already used for unit states.

Out of scope, and treated as failure if attempted: reopening accepted unit content
through a workbook-layout failure, and sampling pages instead of inspecting all pages.

Workbook-owned artifacts are exactly: table of contents, pagination, cross-unit
navigation, front matter, and workbook layout. Everything under `OUTPUT_ROOT/<unit_id>/`
is immutable to this phase.

## Current implementation surface

These files exist and are the real starting point (several are untracked; preserve
unrelated user work and do not stage, stash, reset or clean the worktree):

- `runtime/workbook.py` — `assemble()`, `WorkbookError`. Today the only writer of
  `COMPLETE`, and today insufficient. It derives coverage from
  `run_state["completed_unit_ids"]`, concatenates unit PDFs with `pdfunite`, calls
  `runtime.checks.rasterize_and_check_nonblank`, then writes state. It has no digest
  binding, no page inventory, no per-page inspection, no reviews, no revision loop, no
  terminal log audit, and it writes run state without schema validation.
- `runtime/run_state.py` — `read`, `validate`, `_recompute`, `_write`,
  `record_unit_transition`, `close_run`, `assert_resumable`, `RunStateError`. Note
  `_COMPLETED_STATES` currently admits `ACCEPTED_PENDING_REVIEW`. Coverage for the
  workbook must be derived from each unit's own `acceptance.json`
  `terminal_state == "ACCEPTED"` exactly. If `completed_unit_ids` and the exact-`ACCEPTED`
  set diverge, fail loudly; never silently prefer either.
- `runtime/checks.py` — `pdf_page_count`, `rasterize_and_check_nonblank`, `CheckFailure`,
  `required_checks_for`.
- `runtime/pdf_inspect.py` — `text_legible`, `clipped_lines`, `assets_resolve`,
  `embedded_image_hashes`, `visual_review_template`, `visual_review_problems`,
  `VISUAL_REVIEW_CRITERIA`.
- `runtime/lesson_render.py` (`render_unit`), `runtime/visual_maps.py`,
  `runtime/readability.py` — reuse for workbook-owned pages; do not fork them.
- `runtime/logger.py` — `ExecutionLogger.start/complete/fail/audit`;
  `runtime/checkpoint.py` — `Checkpoints`; `runtime/controller.py` —
  `CurriculumRuntime`; `runtime/session_bridge.py` — `finalize`.
- Policy: `policy/controller.v1.yaml` (`owned_by_code`, `never_uses_a_model_for`,
  `checkpointing`, `review_aggregation`, `full_run.completion_rule`),
  `policy/checks.v1.yaml` (`PDF-VISUAL-REVIEW` asserts all four PDF reviewers pass
  against the rasterized pages), `policy/routing/task_taxonomy.v2.yaml`
  (`workbook_assembly`, `curriculum_final_review` and their `evidence_required` lists),
  `policy/routes.v1.yaml`, `policy/limits.v1.yaml`.
- Tests: `tests/runtime/test_run_state.py`, `tests/runtime/unit_fixture.py`,
  `tests/runtime/test_acceptance_gate.py`, `tests/gates/` and `tests/run_gates.sh`.

## Declared outputs

Under `OUTPUT_ROOT/workbook/`: `assembly_manifest.json`, `workbook.pdf`,
`page_renders/`, `page_inventory.json`, `reviews/<role>.review.json` (exactly four),
`revisions/<n>.revision_receipt.json`, `workbook_acceptance.json`. Every one of these is
schema-bound; add the schemas under `schemas/` and register them the same way existing
runtime schemas are registered. Every one binds the execution-contract digest.

# TEST

Every test below is a real, runnable, deterministic check committed under
`tests/runtime/` (and `tests/gates/` where a phase gate is the right home). Run them in
this order. Do not waive, weaken, reorder or replace one.

1. **P5-T01 — Dependency and toolchain preflight.** Assert P4's run state exists and
   validates; assert one execution-contract digest is recorded and non-empty; assert the
   handler registry has exactly one production handler per P0-frozen workbook state and
   no handler for a state P0 did not freeze. Assert `pdfunite`, `pdfinfo`, `pdftoppm`,
   `pdftotext`, `pdfimages` and Pillow all resolve. A missing dependency is a stop, not a
   skip.
2. **P5-T02 — Assembly refuses non-exact coverage.** For each of: a manifest unit with no
   `acceptance.json`; one recording `ACCEPTED_PENDING_REVIEW`; one recording `BLOCKED`;
   one recording `SYSTEM_FAILURE`; one recording an unknown state — assembly raises,
   writes no `workbook.pdf`, and leaves `run_status` unchanged and not `COMPLETE`.
3. **P5-T03 — Exactly once, in manifest order.** With every manifest unit exactly
   `ACCEPTED`, `assembly_manifest.json` lists every accepted unit exactly once, in frozen
   manifest order. Fixtures with a duplicated unit, a reordered unit, or a unit absent
   from the frozen manifest are all rejected.
4. **P5-T04 — Digest binding.** Every covered unit record and every workbook record
   (assembly manifest, page inventory, each review, each revision receipt, the acceptance
   record) carries the identical execution-contract digest. Mutating the digest in any
   single record fails assembly or acceptance, naming the record.
5. **P5-T05 — Every page rendered and inspected, never sampled.** `page_inventory.json`
   has exactly `pdf_page_count(workbook.pdf)` entries, one per page number with no gap.
   Every page rasterizes non-blank and is inspected (`text_legible`, `clipped_lines`, and
   `assets_resolve` for declared visuals). Injecting one blank page, one clipped line, or
   one unresolvable asset fails. An inventory missing one page's entry fails. Instrument
   the inspection path and assert the per-page inspection is invoked exactly
   `pdf_page_count(workbook.pdf)` times, once per page number, on a fixture large enough
   that any sampling stride would show — and assert the inspection entry point exposes no
   stride, limit, sample or first-N parameter.
6. **P5-T06 — Page hashes resolve to the assembled PDF.** The inventory records the
   `workbook.pdf` SHA-256 and each page raster's SHA-256. Recomputing rasters from the
   recorded PDF reproduces the inventory exactly. Replacing `workbook.pdf` after
   inventory, or editing one page hash, fails.
7. **P5-T07 — Deterministic assembly.** Assembling twice from byte-identical accepted
   inputs yields an identical `workbook.pdf` SHA-256 and identical page hashes. If the
   toolchain injects nondeterminism (creation date, document ID), normalize it inside the
   assembly path and prove the normalization; if it cannot be made deterministic, **stop**
   per the stop condition.
8. **P5-T08 — Exactly four schema-valid reviews.** The four review roles come from the
   P0/P3-frozen role set, not from whatever files exist. Three reviews, five reviews, a
   missing role, a duplicated role, or a record failing its schema each block acceptance.
9. **P5-T09 — Review isolation and identity.** Identity is the tuple (recorded role,
   invocation, routing decision, executed model). Reject: two records sharing that tuple;
   two reviews sharing a session; a review whose authorized inputs include a sibling
   reviewer's verdict path (rejected before invocation, not after); a review whose
   executed model differs from its routing decision's decided model; an absent, extra or
   malformed record.
10. **P5-T10 — Reviews never decide.** Aggregation is deterministic Python
    (`policy/controller.v1.yaml` `review_aggregation`). A review cannot write run state,
    the acceptance record, or `COMPLETE`. A review body containing prose instructing
    acceptance changes no outcome.
11. **P5-T11 — Workbook-only revision.** A failed workbook check revises only
    workbook-owned artifacts. Hash every file under every `OUTPUT_ROOT/<unit_id>/` before
    and after a revision cycle and assert byte-identity. An attempted write to a unit path
    is a hard refusal recorded as a factory defect, not a warning.
12. **P5-T12 — A layout failure never reopens a unit.** Instrument the unit state handler
    registry and the filesystem write path: across a full workbook revision cycle, assert
    the invocation count of every unit state handler is zero and the count of writes to
    any path under `OUTPUT_ROOT/<unit_id>/` is zero.
13. **P5-T13 — Independent re-audit after revision.** After a revision, the affected
    checks, the page inventory, and the reviews in the affected scope re-run from scratch.
    A pre-revision pass cannot satisfy post-revision acceptance; each revision receipt
    names the failed check, the artifacts it was allowed to touch, and the re-audit result.
14. **P5-T14 — Convergence.** The same workbook check failing repeatedly terminates per
    `policy/limits.v1.yaml` with an honest non-`COMPLETE` status and a stated
    `terminal_reason`, instead of looping.
15. **P5-T15 — One writer of COMPLETE.** A test scans `runtime/` and asserts exactly one
    assignment site for `run_status` `COMPLETE`, inside workbook acceptance.
    `run_state.close_run` still refuses `COMPLETE`. Any other attempt raises.
16. **P5-T16 — COMPLETE is conjunctive.** `COMPLETE` requires all of: exact `ACCEPTED`
    coverage; four accepted workbook reviews; a valid final PDF; a clean terminal log
    audit. Removing any single one yields no `COMPLETE` and an honest status with
    `terminal_reason`. The written state validates against
    `schemas/run_lifecycle.schema.v1.json` via `run_state.validate` before it is written.
17. **P5-T17 — Clean terminal log audit.** `ExecutionLogger.audit()` over the run reports
    monotonic ids, zero unclosed starts, zero unknown closes, zero duplicate closes, and
    no missing workbook checkpoint or transition id. An injected unclosed start or
    duplicate close blocks `COMPLETE`.
18. **P5-T18 — Negative-control completeness.** One named, committed fixture exists and is
    rejected for each of: a non-`ACCEPTED` unit; a bad page; a duplicate review identity;
    sibling-verdict access; a shared session; an invalid review record. A test asserts the
    set of negative fixtures is complete against that list.
19. **P5-T19 — Full fixture run.** P4's bounded multi-unit fixture, driven through `--all`
    with live routed workers and no manual intervention, produces a workbook. Then force a
    workbook-layout failure and prove targeted revision to acceptance with every unit
    artifact hash unchanged.
20. **P5-T20 — Independent recomputation.** A separate auditor recomputes coverage from
    unit `acceptance.json` terminal states, page hashes from the shipped PDF, the check
    results from the artifacts, and log start/close pairs — without reading
    `run_state.json`, the acceptance record, or any controller conclusion — and reproduces
    the same terminal decision. Any divergence fails.
21. **P5-T21 — Regression.** The full runtime suite and the applicable phase gates
    (`tests/run_gates.sh`) show no new or worsened result against the P0 baseline.

# LOOP

Run P5-T01 through P5-T21 in order. On the first failure: record the test id, the exact
command, the exit code, the artifact hashes involved, and a narrow root cause. Then revise
**only** the workbook-owned artifact or the runtime code that owns the failed behaviour —
never a unit artifact, never an accepted unit's acceptance record, never a check
threshold, never a test. Re-run in this order: the failed test, then P5-T04 (digest
binding), P5-T05 and P5-T06 (page inventory), P5-T11 (unit immutability), then every later
test whose evidence the revision could have changed, then P5-T21. Repeat until all
twenty-one pass.

Never respond to a failure by widening coverage to a non-`ACCEPTED` unit, by sampling
pages, by relaxing the four-review requirement, by reusing a prior review verdict, by
regenerating a unit, or by writing `COMPLETE` from anywhere but workbook acceptance.

**Stop, without claiming success, if:** the PDF toolchain cannot deterministically
assemble and rasterize the shipped artifact (P5-T07); workbook revision can mutate an
accepted unit (P5-T11, P5-T12); `COMPLETE` can be written outside workbook acceptance
(P5-T15); P4's digest or frozen manifest order is absent or inconsistent (P5-T01); or a
definition-of-success item cannot be proven. A stop is reported as a stop, with the
failing test id and the evidence — never as a partial success.

Before claiming P5 done, write
`plans/19_curriculum_factory_production_loop_closure/results/P5.result.v1.md` containing: the
execution-contract digest; the assembly manifest (unit ids in manifest order with their
`ACCEPTED` terminal states and artifact hashes); the full page-hash inventory (every page,
never an excerpt) with the `workbook.pdf` SHA-256; the four review records summarised by
role, invocation, routing decision, executed model and verdict; every revision receipt
with its named failed check, permitted artifacts, and re-audit result; the terminal log
audit output; the independent recomputation audit from P5-T20 with its inputs and its
reproduced decision; the P5-T01 through P5-T21 table of ids, commands and exit codes; the
before/after unit-artifact hash comparison proving immutability; any remaining failure;
and the final verdict. Claim completion only when all twenty-one tests have passed, the
fixture run in P5-T19 actually ran, and P5-T20's independent recomputation reproduced the
terminal decision.
