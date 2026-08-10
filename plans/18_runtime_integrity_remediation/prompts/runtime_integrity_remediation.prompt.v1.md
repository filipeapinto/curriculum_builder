# GOAL

Implement `plans/runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md`
in full, exactly as scoped there. That plan fixes the seven defects recorded
in `issues/001-renderer-emits-raw-json.md` through
`issues/007-run-level-state-is-incomplete.md`, reproduced against the shipped
`outputs/arduino_kit_run_v2/` run and the runtime that produced it
(`runtime/session_bridge.py`, `runtime/checks.py`), in the order its Exact
work sections lay out: §1 field-aware renderer, §2 role/map-kind-driven
visual pipeline, §3 fail-closed acceptance against the real check inventory,
§4 L04's meter evidence and safety teaching, §5 real Predict-Observe-Explain
evidence, §6 source-claim entailment, §7 run-level lifecycle state, §8 the
bounded policy/curriculum check-inventory reconciliation, §9 regeneration and
re-acceptance of L01-L04.

The plan's boundary — respect it exactly, do not expand it:

- Fixes only the four already-generated units (L01-L04) under the existing
  linear `prepare()`/`finalize()` architecture. Does **not** build out
  `policy/controller.v1.yaml`'s full state machine (that is `RT-1`, tracked
  separately). Does not generate L05-L35. Does not touch
  `tests/gates/registry.py` or `tests/gates/gate_families.v1.yaml` (§8's
  explicit boundary — `tests/gates/fr_p5_unit.py` is a fixture-gate script,
  not part of that catalogue-pairing mechanism, and §3 already requires
  editing its imports; that edit is in scope).
- Does not edit `policy/deferred.v1.yaml`.
- §8 keeps `deferred: RT-5` on all six of `LAB-SCHEMA-VALID`,
  `PDF-PAGE-COUNT`, `PDF-PAGE-NONBLANK`, `PDF-ASSET-RESOLVES`,
  `PDF-TEXT-LEGIBLE`, `PDF-VISUAL-REVIEW` — do not remove it and do not
  invent a `verified_by` pointer to a call site; no registered gate executes
  these six ids' production call sites and §8 forbids adding one, so the fix
  is `note`-field prose (documenting the real call site) plus `deferred: RT-5`
  staying in place, not a `verified_by` value.
- `curricula/arduino_kit/checks.v1.yaml`'s `DOMAIN-VERIFIER` and
  `VISUAL-ROLES-COMPLETE` entries are `stage: deterministic`, advertised in
  the deterministic row (not `static`'s); `DOMAIN-VERIFIER` carries
  `verified_by: FR-P5-VERIFIER-REQUIRED`; `VISUAL-ROLES-COMPLETE` carries
  `deferred: RT-5`. Follow §3 exactly as worded — its wording was itself
  independently QA'd across ten rounds specifically to be schema-legal
  against `schemas/checks.schema.v1.json` and gate-clean against
  `FR-P2-GATEITEMS`/`FR-P4-ALL-VALIDATE`; do not "improve" the wording.

**External prerequisite (photography).** §2's "External prerequisite" note
and §9 step 0 require a fail-fast, human-verified check: whether
`official_kit_photo.jpg` can be cropped to a region containing L02's
breadboard, L03's wire detail, and L04's multimeter. This plan does **not**
authorize acquiring new photographs. If a subject is not locatable, record
that unit's photographic role as `BLOCKED (needs verified photograph)` and
let that unit reach `ACCEPTED_PENDING_REVIEW`/`BLOCKED` rather than
`ACCEPTED` for that role — this is not a failure of the implementation, it is
the correct, honest outcome. Only if **no** subject at all is croppable from
`official_kit_photo.jpg` (not just L04's meter) does this become a full stop:
halt, do not proceed into §9's regeneration, and report per the "Stop
conditions and result" section of the plan and the LOOP section below —
do not attempt to acquire a photograph, run a live LLM content-authoring
session, or build any part of `controller.v1.yaml` to work around it.

# TEST

Use the ordered tests in
`plans/runtime_integrity_remediation/qa/execution_test.plan.v1.md`. Run
`RIR-T00` through `RIR-T13`, strictly in order — later tests assume earlier
ones' evidence exists (e.g. `RIR-T09`/`RIR-T12` diff against `RIR-T00`'s
baseline, `RIR-T10` depends on `RIR-T01`'s recorded outcome):

1. `RIR-T00`: capture the pre-implementation baseline (git state, file
   hashes under `outputs/arduino_kit_run_v2/L01-L04`, current test/gate
   results) — read-only, run before any change.
2. `RIR-T01`: record, by direct inspection, whether `official_kit_photo.jpg`
   is croppable to L02/L03/L04's subjects — the one test that proves the
   photography prerequisite's real state.
3. `RIR-T02`: the §1 renderer — no raw JSON/key syntax reaches the learner,
   `RendererError` on an unrenderable required field.
4. `RIR-T03`: the §2 visual pipeline — role/`map_kind`-driven asset
   selection, the three-item `same_wire` L03 case, `BLOCKED` on an
   unresolved role.
5. `RIR-T04`: §3's fail-closed acceptance — all `test_acceptance_gate.py`
   fixtures, plus schema/stage/advertising validity of the two new
   curriculum check ids.
6. `RIR-T05`: §4's L04 correction — the direct current-mode safety
   statement, the two removed universal claims, the red-X visual.
7. `RIR-T06`: §5's POE semantics — shared-event linkage per unit, the
   "look at the answer map" rejection.
8. `RIR-T07`: §6's source-claim entailment — the four regression fixtures,
   L03's two miscitations resolved.
9. `RIR-T08`: §7's run-level lifecycle — `run_state.json` honesty,
   `assemble()`'s coverage gate, `assert_resumable`'s rejections.
10. `RIR-T09`: §8's policy/curriculum check-inventory reconciliation —
    0 schema errors, 0 mapping violations, `FR-P2-GATEITEMS`/
    `FR-P4-ALL-VALIDATE` both `PASS`, `RT-7`'s note corrected not deleted,
    `registry.py`/`gate_families.v1.yaml` untouched.
11. `RIR-T10`: §9's regeneration and re-acceptance of L01-L04 — asset
    hashes actually changed, every check explicit, every `terminal_state`
    matching `RIR-T01`'s real recorded outcome.
12. `RIR-T11`: full replay of the plan's own "Verification sequence"
    (all five steps) against the implemented state.
13. `RIR-T12`: regression — no path outside L01-L04/run-level state
    changed, no schema-validation break for units this plan doesn't
    regenerate, `policy/deferred.v1.yaml` untouched.
14. `RIR-T13`: the result file and log entry both exist and are complete.

# LOOP

On any test failure: fix only the in-scope artifact the failure points at
(the specific `runtime/`, `curricula/`, `policy/`, or `schemas/` file the
corresponding plan section names) — do not redesign a section that passed
its own test to chase a failure elsewhere. Re-run the failed test and every
test downstream of it (per the TEST section's order), and continue until
every applicable test passes. Do not mark a test `PASS` on a partial or
inferred result; if a test genuinely cannot run yet (a dependency from an
earlier phase is still missing), record it `NOT_RUN`, not `PASS`, exactly as
`RIR-T04`'s own subject (`unit_checks.json`'s `NOT_RUN_BLOCKED`) requires of
the runtime under test.

**Stop conditions** (from the plan — halt and report rather than working
around):

- A schema change in `lab.schema.v4.json` or
  `curricula/arduino_kit/domain.schema.v1.json` breaks validation for a unit
  outside L01-L04 that this plan does not regenerate.
- `official_kit_photo.jpg` cannot be cropped to **any** subject at all (not
  just L04's meter) — `RIR-T01` finding this is the trigger; stop before
  §9/`RIR-T10`.
- Never acquire new photographs, run a live LLM content-authoring session, or
  build any part of `controller.v1.yaml`'s state machine to route around a
  blocker.

On completion — every applicable test `PASS` (or `NOT_RUN` only where a Stop
condition genuinely halted the sequence, honestly reported as such, never
silently) — write
`plans/runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md`
recording: the `RIR-T00` verification-sequence baseline; every
changed/created/deleted path per phase (§1-§9); the `RIR-T01`
photography-blocker disposition for L02/L03/L04; full test results (pass/
fail/not-run counts for every suite named in "Verification sequence"); and
any remaining failures with their exact cause. Append the execution outcome
as a new entry to `plans/runtime_integrity_remediation/plans.log.md` —
append-only, never edit or remove a prior entry. Completion may only be
claimed once every applicable test in the TEST section has actually passed,
not once the code "should" pass it.
