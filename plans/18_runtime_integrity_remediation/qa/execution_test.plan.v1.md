# Runtime Integrity Remediation — Execution Test Plan v1

## Purpose and boundary

Tests `plans/runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md`
without implementing it: this document specifies the ordered checks a future
implementation pass must satisfy, but authoring it performs no change under
`runtime/`, `curricula/`, `policy/`, `schemas/`, or `outputs/`. Every test's
evidence must come from actually running a command (`pytest`, the real gate
scripts under `tests/`, `jsonschema` validation, byte-level hashing/diffing)
against the repository after implementation — never from re-reading the
plan's prose as if it were the result.

Tests must never delete or overwrite pre-existing shipped units outside
L01-L04, never write to `policy/deferred.v1.yaml`, `tests/gates/registry.py`,
or `tests/gates/gate_families.v1.yaml` (§8's explicit boundary), and any
reproduction done before the real implementation exists (e.g. to establish a
baseline, or to re-check a plan-stage fix in isolation) must run against a
scratch copy under `/tmp`, never against the working tree. Once the real
implementation lands, tests run directly against the repository, but must not
touch any unit's on-disk state beyond what §9 itself specifies (L01-L04 only).

## Availability stages

This plan's one external prerequisite (§2 "External prerequisite
(photography)") is **not** a whole-plan blocker: the plan explicitly states
every fix other than L02/L03/L04's specific photographic-identification role
proceeds regardless of whether `official_kit_photo.jpg` can be cropped to
those subjects. Consequently:

- `RIR-T00` and `RIR-T01` can run immediately, before any implementation
  exists — they are read-only baseline capture and a manual photography
  check respectively.
- `RIR-T02`-`RIR-T09`, `RIR-T11`, `RIR-T12`, `RIR-T13` can run once the
  corresponding implementation phase lands, independent of `RIR-T01`'s
  outcome.
- `RIR-T10` (§9 regeneration) is the one test whose **expected values**
  depend on `RIR-T01`'s recorded outcome, not on `RIR-T01`'s outcome
  determining whether `RIR-T10` runs at all: if `RIR-T01` records a subject
  as `BLOCKED (needs verified photograph)`, `RIR-T10` must find that unit's
  `acceptance.json` reporting `ACCEPTED_PENDING_REVIEW`/`BLOCKED` for that
  role — reporting `ACCEPTED` instead would itself be a `RIR-T10` failure,
  and reporting `BLOCKED`/`ACCEPTED_PENDING_REVIEW` when `RIR-T01` found the
  subject locatable would equally be a failure. `RIR-T01` is the one test
  that proves the prerequisite's real state; nothing downstream may assume
  an outcome for it that wasn't actually recorded.
- Per the plan's own Stop conditions: if `RIR-T01` finds `official_kit_photo.jpg`
  cannot be cropped to **any** subject at all (not just L04's meter), halt
  the whole test sequence at that point and report per "Final audit and pass
  rule" rather than continuing into phase-specific tests that assume at
  least partial photographic coverage exists.

## Ordered tests

### RIR-T00 — Baseline capture (read-only)

Before any implementation change, capture and record in the result file:

- `git rev-parse HEAD` and `git status --porcelain` (starting tree state).
- SHA-256 of every file under `outputs/arduino_kit_run_v2/L01/` through
  `L04/` (`assets/*.svg`, `assets/*.jpg`, `workers/lab.json`,
  `workers/domain.json`, `acceptance.json`, `unit_checks.json`,
  `document/*`) — the "before" state `RIR-T10`'s asset-hash-diff check
  compares against.
- `python3 -m pytest tests/runtime/ -v` output today (the suite already
  contains `test_checks.py`, `test_controller.py`, `test_run_curriculum.py`,
  and others pre-dating this plan) — pass/fail counts the plan's
  Verification-sequence step 1 must not regress below.
- `bash tests/run_gates.sh 2` and `bash tests/run_gates.sh 5` output today,
  specifically the `FR-P2-GATEITEMS` and `FR-P4-ALL-VALIDATE` lines —
  baseline for `RIR-T09`'s post-§8 comparison (independently reproduced at
  round 10 of this plan's QA: `FR-P2-GATEITEMS PASS`, 42 staged ids
  pre-catalogue-edit; `FR-P4-ALL-VALIDATE PASS`).

**Pass:** every capture command completes and its output is written into the
result file's evidence section; no file under `outputs/`, `policy/`,
`curricula/`, or `schemas/` is modified by running this test.

### RIR-T01 — External prerequisite: photography locatability (§2, §9 step 0)

By direct visual inspection of `official_kit_photo.jpg` (not inference),
determine for each of L02 (breadboard), L03 (wire detail), L04 (multimeter)
whether a croppable region containing that unit's named subject exists.
Record one of `locatable-and-croppable` or
`BLOCKED (needs verified photograph)` per unit-role in the result file.

**Pass:** an explicit, recorded outcome exists for all three unit-roles —
silence or inference is a failure regardless of what the true answer turns
out to be. If **all three** report `BLOCKED`, that is still a pass for this
test (a real, honestly recorded data point); it is not this test's job to
require a favorable outcome. If the inspection instead finds no subject at
all is croppable from `official_kit_photo.jpg` (a materially larger finding
than issues 003/004 describe), stop per the plan's Stop conditions and skip
directly to "Final audit and pass rule" rather than continuing to `RIR-T02`.

### RIR-T02 — Renderer (§1, issue 001)

Run `python3 -m pytest tests/runtime/test_lesson_render.py -v`. Separately,
render a fixture unit through the assembled `_markdown()` path and grep the
output for `{`, `":`, and the literal schema field names
(`recorded_before_observing`, `what_you_saw`, `safe_first_check`, ...) —
expect zero matches. Construct one fixture with a required field the
renderer has no template branch for and confirm `RendererError` is raised,
not a silent drop.

**Pass:** all `test_lesson_render.py` cases pass; zero raw-JSON/key-syntax
matches in the fixture's rendered markdown; the unrenderable-required-field
fixture raises `RendererError`.

### RIR-T03 — Visual pipeline (§2, issue 003)

Run `python3 -m pytest tests/runtime/test_visual_maps.py -v`, covering:
`power_path`, `connectivity`+`same_wire` (including the three-item
`traced_path` fixture matching L03's real shape — items 0/1 render as the
connected dashed pair, item 2 as its own unconnected labeled point),
`connectivity`+`enumeration`, `breadboard`, unrecognized-`map_kind`-fails,
evidence-card-reflects-fixture's-own-`child_records`, and
unresolvable-`visual_roles`-writes-`BLOCKED`-`acceptance.json`.

**Pass:** every case in `test_visual_maps.py` passes, including the
three-item `same_wire` case and the `BLOCKED`-not-raised case.

### RIR-T04 — Fail-closed acceptance (§3, issue 002)

Run `python3 -m pytest tests/runtime/test_acceptance_gate.py -v`, covering
fixtures (a) raw-JSON body rejected, (b) irrelevant image rejected by
`PDF-ASSET-RESOLVES`, (c) clipped/undersized text rejected by
`PDF-TEXT-LEGIBLE`, (d) a unit missing one required check's implementation
recorded `NOT_RUN_BLOCKED`, (e) cross-family bypass present forces
non-`ACCEPTED`, (f) `finalize()` called twice with `reentry_reason` set on
the second call succeeds, and twice **without** it on the second call still
raises. Separately, validate `curricula/arduino_kit/checks.v1.yaml` against
`schemas/checks.schema.v1.json` with `jsonschema` and confirm
`DOMAIN-VERIFIER`/`VISUAL-ROLES-COMPLETE` are present, `stage: deterministic`,
and advertised in the deterministic row.

**Pass:** every `test_acceptance_gate.py` case passes; 0 `jsonschema` errors
on `curricula/arduino_kit/checks.v1.yaml`.

### RIR-T05 — L04 correction (§4, issue 004)

Diff rendered L04 child- and adult-facing content against
`curricula/arduino_kit/arduino_kit_curriculum.v5.yaml:227` and confirm the
direct current-mode-across-supply statement appears verbatim in meaning in
both the child-facing render and the adult-verification section. Grep the
rewritten `l04_multimeter_evidence.v1.json` and generated
`L04/workers/domain.json`/`lab.json` for the two removed claims (the
shared-fuse-under-200mA claim, the universal 10A-above-200mA threshold) —
expect zero matches unless replaced by an explicit
`derivation.premises`-marked conservative statement. Confirm the
deterministic current-mode red-X visual's `supports_section` resolves and
its underlying domain data is present.

**Pass:** the direct safety statement is present in both audiences; neither
removed universal claim remains unqualified; the red-X visual resolves; a
recorded `PDF-VISUAL-REVIEW` verdict for L04 covers both checks.

### RIR-T06 — POE semantics (§5, issue 005)

Run `python3 -m pytest tests/runtime/test_poe_semantics.py -v`. For each of
L02/L03/L04, confirm `observe.what_to_observe`/`evidence_fields`/
`explain.what_you_saw` and the visuals' `role`/`supports_section` all name
the same event as the corrected domain data (L02: breadboard clip groups;
L03: the wire pair plus the separately-located expansion row; L04: the
jack-and-dial diagram). Confirm the rejecting fixture (only the assembly map
referenced, no `evidence_fields`) is actually rejected.

**Pass:** all `test_poe_semantics.py` cases pass, including the "look at the
answer map" rejection.

### RIR-T07 — Source-claim entailment (§6, issue 006)

Run the new fixtures under `tests/fixtures/`:
`unit_claim_wrong_device.reject.json`,
`unit_claim_unsupported_number.reject.json`,
`unit_claim_out_of_scope_source.reject.json`,
`unit_claim_valid_exact_model.accept.json` through
`checks.check_claim_entailment`. Confirm L03's `absolute_max: 1 A`
jumper-wire rating and "expansion board is in the kit" claim are each either
re-cited to a source that actually supports them or explicitly marked
`derivation.premises`/scope-corrected (grep `L03/workers/lab.json` and
`domain.json` directly, not the plan's prose).

**Pass:** all four fixtures resolve to their expected accept/reject outcome;
neither L03 miscitation remains unresolved in the shipped worker JSON.

### RIR-T08 — Run-level lifecycle (§7, issue 007)

Run `python3 -m pytest tests/runtime/test_run_state.py -v`, covering: a
fixture reproducing the real `arduino_kit_run_v2` shape (35-unit manifest, 4
completed) asserts `run_state.json` reports `run_status` other than
`COMPLETE`/`ACCEPTED` and `remaining_unit_ids` has 31 entries; `assemble()`
refuses `COMPLETE` with incomplete coverage; `assert_resumable` rejects a
hash mismatch and rejects overwriting an already-`ACCEPTED`
(or `ACCEPTED_PENDING_REVIEW`) unit.

**Pass:** all `test_run_state.py` cases pass.

### RIR-T09 — Policy/curriculum check-inventory reconciliation (§8)

Validate both `policy/checks.v1.yaml` and `curricula/arduino_kit/checks.v1.yaml`
against `schemas/checks.schema.v1.json` with `jsonschema` — 0 errors. Run
`tests/gates/fr_p4_policy_schemas.mapping_violations()` against the merged
inventory — 0 problems, with `LAB-SCHEMA-VALID`/`PDF-PAGE-COUNT`/
`PDF-PAGE-NONBLANK`/`PDF-ASSET-RESOLVES`/`PDF-TEXT-LEGIBLE`/`PDF-VISUAL-REVIEW`
all still `deferred: RT-5` (MAPPED, not removed) and each carrying a `note`
naming its real call site. Run `bash tests/run_gates.sh 2` and
`bash tests/run_gates.sh 5` and confirm `FR-P2-GATEITEMS PASS` and
`FR-P4-ALL-VALIDATE PASS` (comparing against `RIR-T00`'s baseline — the
staged-id count should grow by exactly the ids this plan adds, nothing should
newly fail). Read `TEXT-READABILITY-BAND`'s `note` in
`policy/checks.v1.yaml` and confirm it states the check now executes against
real rendered content while `RT-7`'s own path-specific criterion remains
unmet — not deleted, not claiming `RT-7` discharged. Confirm via
`git diff --stat tests/gates/registry.py tests/gates/gate_families.v1.yaml`
that neither file changed, and confirm `tests/gates/fr_p5_unit.py`'s
`syllables`/`grade_level`/`readability_violations`/`check_readability`/
`bloom_flags`/`check_bloom_verbs` are now imported from
`runtime/readability.py` rather than defined locally, with its own fixture
gate still passing unchanged.

**Pass:** 0 schema errors on both files; 0 mapping violations; `FR-P2-GATEITEMS`
and `FR-P4-ALL-VALIDATE` both `PASS`; the `RT-7` note is corrected, not
deleted; `registry.py`/`gate_families.v1.yaml` are byte-identical to
`RIR-T00`'s baseline; `fr_p5_unit.py`'s own fixture gate still passes after
the import change.

### RIR-T10 — Regenerate and re-accept L01-L04 (§9)

After `RIR-T01`'s outcome is known: patch and regenerate L01-L04 per §9, then
for each of L02-L04 diff `assets/path_map.svg`/`evidence_card.svg`'s SHA-256
against `RIR-T00`'s baseline bytes and confirm they **changed** (a match
means `regenerate_assets()` did not actually run). Confirm each
`unit_checks.json` lists every required check id with an explicit
`PASS`/`FAIL`/`NOT_RUN_BLOCKED` (no hardcoded four-key dict). Confirm each
`acceptance.json`'s `terminal_state`: `ACCEPTED` only where every required
check truly passed and `RIR-T01` recorded that unit's photographic role as
locatable; `ACCEPTED_PENDING_REVIEW`/`BLOCKED` (naming the role) wherever
`RIR-T01` recorded `BLOCKED` for that unit's role, or a cross-family bypass
applied. Confirm `run_state.record_unit_transition` fired for each (no
separate manual call needed per §3's wiring). Rasterize each regenerated PDF
and visually confirm it reads as prose with subject-appropriate visuals and
states the L04 safety rule directly.

**Pass:** asset hashes changed for L02-L04; every `unit_checks.json` entry is
explicit; every `terminal_state` matches what `RIR-T01` actually found for
that unit's photographic role, not an assumed-favorable outcome; rasterized
PDFs pass direct visual inspection.

### RIR-T11 — Full verification-sequence replay

Run the plan's own "Verification sequence" end to end against the
implemented state: (1) `python3 -m pytest tests/runtime/ -v` — all tests
pass; (2) `bash tests/run_gates.sh 2` and `bash tests/run_gates.sh 5` (the
plan's own text names `tests/gates/run_gates.sh`, which does not exist as
written — the real runner is `tests/run_gates.sh <phase>`; run the real
command) — the existing fixture-gate suite still passes after §3's
`readability`/`bloom` extraction; (3) the L01-L04 inspection from
`RIR-T10`; (4) `run_state.json` inspection from `RIR-T08`; (5) the L04 diff
from `RIR-T05`.

**Pass:** all five Verification-sequence steps pass as the plan defines
"pass" for each.

### RIR-T12 — Regression: scope boundary held

Confirm no unit outside L01-L04 is touched: `git diff --stat
outputs/arduino_kit_run_v2/` lists only `L01/`-`L04/` and
`run_state.json`/`workbook/` paths. Confirm the two schema edits
(`lab.schema.v4.json`'s `derived[]`/`sourced_claims[]`/
`unresolved_visual_roles[]`, `domain.schema.v1.json`'s `evidence_card`/
`relationship`) do not break validation for any unit this plan does not
regenerate — if any such unit exists under a path this repository already
validates, revalidate it against the amended schemas and confirm no new
failure. Confirm `policy/deferred.v1.yaml` is byte-identical to `RIR-T00`'s
baseline (§8 explicitly does not edit it).

**Pass:** no path outside L01-L04/run-level state changed; no
schema-validation regression for any unit this plan doesn't regenerate;
`policy/deferred.v1.yaml` unchanged.

### RIR-T13 — Result file and log completeness

Confirm `plans/runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md`
exists and records: the `RIR-T00` baseline, every changed/created/deleted
path per phase (§1-§9), the `RIR-T01` photography-blocker disposition for
L02/L03/L04, full test results (pass/fail counts for every suite named in
"Verification sequence"), and any remaining failures with their exact cause.
Confirm the execution outcome was appended to
`plans/runtime_integrity_remediation/plans.log.md` as a new entry (not a
rewrite of an existing one).

**Pass:** the result file exists with all required content; the log entry
exists and is a genuine append.

## Final audit and pass rule

The package is passing only when `RIR-T00` through `RIR-T13` all report
`PASS`, with `RIR-T10`'s `terminal_state` expectations matching exactly what
`RIR-T01` recorded — never an assumed-favorable outcome. If `RIR-T01` finds
no subject at all croppable from `official_kit_photo.jpg`, the sequence
halts there per the plan's Stop conditions, and the result file must report
this honestly as a halted, partial run — not as a pass with the remaining
tests silently skipped or presumed. Any test that cannot run because a prior
phase's implementation is missing must be recorded as `NOT_RUN`, distinct
from `PASS` and from `FAIL`, exactly as `RIR-T04`'s own subject
(`NOT_RUN_BLOCKED`) requires of the runtime it tests — this test plan holds
itself to the same standard it holds the implementation to.
