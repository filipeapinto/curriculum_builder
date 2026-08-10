# Runtime Integrity Remediation Plan v1 — Focused QA (Round 2)

## Verdict

**CHANGES REQUIRED — 1 Critical, 2 High.** Round 1's two findings (the
`runtime/controller.py` mischaracterization in "Status and objective," and the
`RT-7`-note-deletion risk in Phase 8) were independently re-checked against the
current repository and both revisions hold up. This round instead found a
mechanically-reproduced defect in §9's core delivery mechanism — literally
re-invoking `session_bridge.finalize()` against an already-finalized unit
directory crashes immediately, before any of the plan's fixes could take
effect — plus two further problems in the Phase 8 policy-reconciliation text
that round 1 did not surface: an inaccurate inventory of which check ids
carry `deferred: RT-5` (which causes Phase 8 to leave other
already-executing, already-misrepresented checks untouched), and boundary
language ("Do not touch `tests/gates/`") that, read literally, forbids the
exact edit to `tests/gates/fr_p5_unit.py` that §3 explicitly requires and
that Verification-sequence step 2 depends on having happened.

## Findings

### 1. Critical — §9's "re-invoke `finalize()`" step crashes on the actual code, before any fix takes effect

**Evidence.** §9 says: "Patch `L02/workers/domain.json`+`lab.json`, ... in
place ... Re-invoke `session_bridge.finalize()` for L01-L04 against the
corrected worker JSON, producing re-rendered markdown (§1), re-rendered
visuals (§2), the full fail-closed check set (§3), and updated
`acceptance.json`/`unit_checks.json`." This targets the same output
directories that already exist and are already `ACCEPTED`
(`outputs/arduino_kit_run_v2/L01`-`L04`).

`finalize()` (`runtime/session_bridge.py:223-296`) is not idempotent against
an already-finalized output root:
- It reads `pending["model_start_id"]` from the (untouched) `worker_request.json`
  and calls `logger.complete(start_id, ...)` (line 242). That exact `ACT` id
  was already closed by the *first* `finalize()` run — `ExecutionLogger.complete()`
  → `_require_open()` (`runtime/logger.py:104-111`) raises `LogError` for a
  start that is already closed.
- Independently, `document = output / "document"; document.mkdir()` (line 266)
  and the following `shutil.copytree(output / "assets", document / "assets")`
  (line 267) both assume `output/document` does not yet exist; it already does,
  fully populated, from the original run.

This was reproduced mechanically, not just reasoned about: copying the full
repo to a scratch tree (`/tmp/rirqa2/repo`) and calling
`runtime.session_bridge.finalize(engine, Path('outputs/arduino_kit_run_v2/L04'))`
directly raises:

```
FAILED as expected: LogError operation refused: start is already closed: ACT-013
```

— i.e. the very first side-effecting call in `finalize()` after schema
validation fails outright. No workaround, reset step, or idempotency
requirement is mentioned anywhere in the plan (not in §9, not in §1-§8, not
in "Stop conditions"). `finalize()` itself is not touched by any exact-work
bullet.

**Impact.** As literally written, §9 — the step that actually ships every
other fix in the plan (renderer, visuals, fail-closed acceptance, L04
correction, POE evidence, claim entailment) into the shipped L01-L04
artifacts — cannot execute. This blocks the plan's entire deliverable:
Verification-sequence steps 3-5 (regenerated documents/PDFs, corrected
`unit_checks.json`/`acceptance.json`, `run_state.json`, the L04 diff check)
and every "issue N acceptance criteria" bullet that depends on regenerated
output are all unreachable until this is fixed, regardless of how correct
§1-§8's individual designs are.

**Minimal required remediation.** Add an explicit step to §9 (or a small
`finalize()` change under §3, since §3 already modifies `finalize()`'s check
set) that makes re-entry safe for an already-finalized unit: e.g. reset the
per-unit `document/` directory and the relevant execution-log/model-start
state before re-invoking (or have `finalize()` detect and tolerate a prior
completed run — start a fresh logger `ACT` for re-finalization rather than
reusing the original `model_start_id`, and use `document.mkdir(exist_ok=True)`
/ a directory-clearing step before `copytree`). Whichever approach is chosen,
state it explicitly — the plan currently assumes `finalize()` is safely
re-entrant and it is not.

### 2. High — Phase 8's premise that only three ids carry `deferred: RT-5` is false, so it leaves other already-executing checks misrepresented

**Evidence.** Phase 8 states: "`policy/checks.v1.yaml` only carries
`deferred: RT-5` on the three PDF-family ids (`PDF-ASSET-RESOLVES`,
`PDF-TEXT-LEGIBLE`, `PDF-VISUAL-REVIEW`, lines 159-177). For exactly these
three, once §3 wires them into production execution, remove `deferred: RT-5`
and add a `verified_by`-style pointer..."

Reading the actual file (`grep -n "^- id: PDF\|deferred: RT-5"
policy/checks.v1.yaml`) shows the `pdf:` family has **five** ids, and all
five carry `deferred: RT-5`: `PDF-PAGE-COUNT` (lines 146-151),
`PDF-PAGE-NONBLANK` (152-158), and the three the plan names (159-177). Both
`PDF-PAGE-COUNT` ("rendered page count equals the count recorded at
assembly") and `PDF-PAGE-NONBLANK` ("no page is uniform within 1% of a
single colour") are *already executed today* — `session_bridge.py`'s
`finalize()` already calls `pdf_page_count(pdf)` and
`rasterize_and_check_nonblank(pdf, ...)` (imported from `runtime/checks.py`,
lines 25, 278, 287) — yet the policy file still marks both `deferred: RT-5`.

Worse, in the `lab_document:` family, `LAB-SCHEMA-VALID` (line 65-72) also
carries `deferred: RT-5`, even though it is executed today
(`jsonschema...validate(lab)` in `finalize()`, line 239) and is recorded as
`"LAB-SCHEMA-VALID": "PASS"` in every shipped `unit_checks.json` right now
(`session_bridge.py:258`). This is a live instance of exactly the failure
mode `DRIFT-NO-MISREPORTING` names ("no check was reported as present
without executing" — inverted here: a check is executing and reported PASS
while the catalogue still calls it unexecuted).

**Impact.** Because Phase 8's fix is scoped to "exactly these three" based on
a false count, it does not touch `PDF-PAGE-COUNT`, `PDF-PAGE-NONBLANK`, or
`LAB-SCHEMA-VALID`. After this plan ships, `policy/checks.v1.yaml` will still
misrepresent three checks that are demonstrably executing (one of them
already proven by a real, shipped `PASS` record predating this plan) as
deferred/unexecuted. This directly contradicts "Architectural end state"
item 6's promise that entries this plan touches "are updated to say so
truthfully," and undercuts the stated purpose of Phase 8 itself
("Reconcile the policy check inventory with what now executes").

**Minimal required remediation.** Correct Phase 8's premise: identify that
`PDF-PAGE-COUNT`, `PDF-PAGE-NONBLANK`, and `LAB-SCHEMA-VALID` also carry a
stale `deferred: RT-5` despite already executing, and either fold their
`deferred: RT-5` removal into Phase 8's scope (with `verified_by` pointers to
the existing call sites), or explicitly state why they are left as-is (if,
e.g., the plan wants to bound Phase 8 strictly to ids §3/§6 newly wire in —
in which case the "only... three" factual claim about the file's current
state still needs correcting even if the action stays scoped to three ids).

### 3. High — Phase 8's "Do not touch `tests/gates/`" contradicts §3's explicit instruction to edit `tests/gates/fr_p5_unit.py`

**Evidence.** §3 ("Make acceptance fail-closed") instructs: "Extract these
functions into `runtime/readability.py` (new, shared module); have
`tests/gates/fr_p5_unit.py` import from it (no behavior change to the
existing fixture gate) and have `runtime/checks.py` import the same
functions..." — an explicit, required edit to a file physically inside
`tests/gates/`. Confirmed the functions genuinely live there today
(`syllables`, `grade_level`, `readability_violations`, `check_readability`,
`bloom_flags`, `check_bloom_verbs` are defined directly in
`tests/gates/fr_p5_unit.py`, matching the plan's own line citation).

Phase 8 then states: "Do not touch `tests/gates/`, `tests/gates/registry.py`,
or `tests/gates/gate_families.v1.yaml` — that suite validates planning
documents against their own catalogues and is orthogonal to these seven
production issues." Read literally, the first item in that list — bare
`tests/gates/` — forbids touching anything under the directory at all,
including `fr_p5_unit.py`. (The redundant separate listing of
`tests/gates/registry.py` and `tests/gates/gate_families.v1.yaml` suggests
the author meant "the `tests/gates/` meta-governance suite" collectively, as
"Status and objective" phrases it — but that is not what the sentence
literally says, and it is not what a plain reading of a comma-separated
"do not touch X, Y, or Z" list conveys.)

**Impact.** If Phase 8's boundary is followed literally, the `fr_p5_unit.py`
import-extraction §3 requires cannot be made, which in turn makes
Verification-sequence step 2 impossible to satisfy as written: "`bash
tests/gates/run_gates.sh` ... the existing fixture-gate suite (`fr_p5_unit.py`
and friends) still passes after §3's extraction of `readability`/`bloom`
functions into `runtime/readability.py`" presupposes the extraction (and
therefore the edit to `fr_p5_unit.py`) already happened. The plan
contradicts itself about whether this one file may be touched.

**Minimal required remediation.** In Phase 8, narrow the "do not touch"
language to what "Status and objective" already scopes it to: `tests/gates/registry.py`
and `tests/gates/gate_families.v1.yaml` (the meta-governance catalogue
files), and drop the bare `tests/gates/` directory-wide phrasing, or add an
explicit carve-out for the `fr_p5_unit.py` import-line edit §3 already
specifies.

## Observations (non-blocking)

- §2's "Map renderer rewrite" cites the current `_svg()` call sites
  (`session_bridge.py:49-63,146-150`), which live inside `prepare()` — a
  point in the pipeline that runs *before* the model authors
  `workers/domain.json`, so `domain.build_map.map_kind` does not exist yet
  for a freshly-authored unit (the curriculum manifest carries `visual_roles`
  but never `build_map`/`map_kind`; only the model's own `domain.json`
  output does, confirmed by inspecting `arduino_kit_curriculum.v5.yaml` and
  the L02/L03/L04 seed files). The bullet doesn't say the map-rendering call
  needs to move to `finalize()` (where `domain.json` is already available and
  where the plan's other §2 bullets — "Placement," "Blocking on missing
  roles" — already explicitly operate). For §9's one-off regeneration of
  L01-L04 this is moot (their `domain.json` already exists), but as stated
  this leaves the durable, general-purpose "map-kind-driven rendering"
  architecture the plan's "Architectural end state" item 3 promises
  under-specified for any future freshly-authored unit.
- Verified empirically (scratch schema edit + validation against all four
  shipped `workers/lab.json` files) that adding `content.sourced_claims[]` as
  an optional property is schema-consistent with `content`'s existing
  `additionalProperties: false` pattern and does not break L01-L04
  validation — this part of §6 holds up as stated.
- Verified that a plausible `breadboard` build_map populated per §5's L02
  description (labelled_features covering all five enum values,
  `wire_endpoints`, `placement_steps`, `schematic_included: true`,
  `safety_inset`) validates cleanly against
  `domain.schema.v1.json`'s `$defs.breadboard_build_map`; the plan's prose is
  less explicit than the schema's required-field list but nothing in it is
  actually inconsistent with that schema.
- The plan's "Acceptance criteria" summary section omits a few sub-bullets
  present in the underlying issues (e.g. issue 006's "visual receipts prove
  the subject is visible in the shipped crop" is addressed in Exact work §6
  as a narrower "presence check," but the Acceptance-criteria summary for
  issue 006 doesn't restate it; issue 003's "usable evidence-card checkboxes
  and adult signoff" is present in Exact work §2 but not restated in the
  issue-003 summary bullet). In each case the underlying work item is still
  present in "Exact work," so nothing appears to be actually dropped from
  scope — only from the summary section's restatement.
