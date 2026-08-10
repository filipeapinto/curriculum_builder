# Runtime Integrity Remediation — Implementation Plan v1

## Status and objective

Planning only; no implementation is authorized by this document's creation.

This plan fixes the seven defects recorded in `issues/001-renderer-emits-raw-json.md`
through `issues/007-run-level-state-is-incomplete.md`, all reproduced against the
shipped `outputs/arduino_kit_run_v2/` run and the runtime that produced it
(`runtime/session_bridge.py`, `runtime/checks.py`). It follows the fix order
`issues/README.md` recommends: renderer (001) and visuals (003) first, then make
acceptance fail-closed (002), then correct L04 (004), then evidence (005) and
receipts (006), then run-level state (007).

The plan's boundary: it fixes the four already-generated units (L01-L04) under the
existing linear `prepare()`/`finalize()` architecture in `session_bridge.py`. It does
**not** build out the full aspirational state machine in `policy/controller.v1.yaml`
(`VALIDATE`, `PLAN_REVIEW_*`, `QA_*`, ...) — that is `RT-1`, tracked separately in
`policy/deferred.v1.yaml`. `runtime/controller.py`'s `CurriculumRuntime.simulate()`
walks every `policy/controller.v1.yaml` state, and `session_bridge.py`'s `prepare()`
already imports and calls several of its methods (`resolve_curriculum`,
`resolve_companions`, `validated_manifest`, `run_verifier_fixtures`, `_logger_gate`),
but `simulate()` only writes placeholder state files labelled
`"coverage": "simulated-controller-only"` — no path produces the real per-state
artifacts `RT-1` requires, and this plan does not build that. It does not generate L05
through L35. It does not touch `tests/gates/` FR-P* meta-governance (the suite that
validates *plan documents*, via `tests/gates/registry.py` and
`tests/gates/gate_families.v1.yaml`) — that suite checks planning artifacts, not
runtime behavior, and none of the seven issues name it.

## Architectural end state

1. `_markdown()` (and any successor) never serializes structured teaching content
   with `json.dumps`; every rendered block goes through a field-aware template a
   test enumerates by schema field, and an unknown/unmapped required field raises
   rather than silently dropping.
2. Acceptance is fail-closed: a required check that is absent, skipped, deferred,
   bypassed, or unable to inspect its real subject is recorded as non-`PASS` and
   blocks `ACCEPTED`. The required check set is built from `policy/checks.v1.yaml`,
   not hardcoded in `session_bridge.py`.
3. Visual asset selection is driven by each unit's declared `visual_roles` and the
   domain's `map_kind`, never filesystem sort order. A role that cannot resolve to a
   verified asset blocks the unit; it never falls back to an unrelated asset.
4. Every externally-supported claim carries a locator a deterministic check resolves
   against cached source bytes. Derived/conservative numbers carry their premises and
   are never attributed to a source that states a different number.
5. The run root carries one authoritative lifecycle record. Run-level
   `ACCEPTED`/`COMPLETE` requires full manifest coverage, workbook assembly, and PDF
   review — never inferred from directory contents.
6. `policy/checks.v1.yaml` entries this plan wires into production execution
   (§Phase 8) are updated to say so truthfully. `policy/deferred.v1.yaml`'s `RT-5`
   (which also covers logging, selector, and reviewer-panel obligations this plan
   does not touch) and `RT-7` (whose acceptance criterion names the
   `curricula/<name>/units/` path, not `outputs/<run>/L0N/`, and deciding where
   generated units canonically live is a structural question this plan does not
   own) are left untouched. This plan makes no claim about their discharge.

## Exact work

### 1. Add a field-aware lesson renderer (issue 001)

- Create `runtime/lesson_render.py` with one pure function per `lab.schema.v4.json`
  block, each returning a list of markdown lines, replacing every
  `json.dumps(...)` call in `_markdown()` (`runtime/session_bridge.py:211-214`):
  - `render_engage(engage)` — hook paragraph, then the eliciting question as a
    posed question, not a JSON key.
  - `render_explore(explore, vocabulary)` — prediction as a question with the
    `options` as a lettered choice list and a **visible "written down before
    observing" mark** for `recorded_before_observing`; `steps` as a numbered
    action list (`steps[].number`/`steps[].action`); an evidence-recording block
    keyed on `observe.record_method` (`evidence_table` → markdown table with one
    row per `evidence_fields` entry; `drawing_prompt` → a labeled blank-space
    prompt; `tick_or_circle` → checkboxes; `adult_read_measurement` → a
    reading-slot line marked adult-recorded); `not_yet_outcome` rendered as a
    named safe outcome, not a failure state.
  - `render_explain(explain)` — `what_you_saw` and `why_it_happened` as separate
    labeled paragraphs (never merged, per the schema's observation/mechanism
    distinction) plus the `self_explanation_prompt` as a prompt for the child to
    answer, not a stored value.
  - `render_elaborate(elaborate)` — `near_transfer`/`far_transfer` as two labeled
    bullet lists.
  - `render_evaluate(evaluate)` — `success_criteria_checklist` as literal
    checkboxes; `hinge_question.question` posed to the child (never leaking
    `reveals`, which is teacher-facing).
  - `render_identification(identification)` — child/technical name pair,
    `distinguishing_features` prose, `orientation_cue` if present, and `parts` as
    a labeled list.
  - `render_troubleshooting(troubleshooting)` — a three-column table
    (`what_you_notice` | `likely_reason` | `safe_first_check`), calm tone per
    `unit_prose.v1.md`.
  - `render_adult_verification(safety)` — a visibly separate section (distinct
    heading, e.g. `## Adult verification (adult only)`) rendering
    `hazard_mode`, `adult_verification.variant/marking/verified_configuration/
    limits/endpoint_check` as a checklist and `signoff_required` as an explicit
    signoff line — never interleaved with child-facing content.
- Add the currently-dropped blocks `_markdown()` never renders at all: a
  "Before we start" block from `pedagogy.prior_knowledge.retrieval_prompt`
  (recall, not re-read, placed before Engage per `unit_prose.v1.md`'s required
  arc); a misconception-confrontation block from `pedagogy.misconceptions[]`
  (`misconception`/`confronted_by`, placed where `unit_prose.v1.md` puts mechanism
  confrontation — beside Explain); vocabulary definitions from
  `pedagogy.vocabulary[]`, each inserted beside its first use, keyed by
  `introduced_in` (e.g. a term with `introduced_in: explore` is defined inline
  inside `render_explore`'s output, not in a glossary at the end); scaffolding
  roles from `pedagogy.scaffolding` (`adult_does`/`child_does` as a "who does
  what" block near the core activity, `fading_note` noted where relevant).
- `_markdown()` becomes an assembler that calls these functions in the
  `unit_prose.v1.md` arc order and raises `RendererError` (new, in
  `lesson_render.py`) if a required schema field it does not have a template
  branch for is present and non-empty — "fail on unknown/unrendered required
  fields" from the issue's acceptance criteria, not a silent drop.
- Add `tests/runtime/test_lesson_render.py` (new — no `test_session_bridge.py`
  exists today): one test per render function per field shape (all four
  `record_method` values, empty vs. populated `options`, `worked_example`
  present/absent, `next_lab_link` present/absent), plus a test asserting the
  assembled markdown for a fixture unit contains no `{`, no `":` key-value
  syntax, and none of the literal schema field names
  (`recorded_before_observing`, `what_you_saw`, `safe_first_check`, ...), plus a
  test that an unrenderable required field raises `RendererError`.

### 2. Build a role- and map-kind-driven visual pipeline (issue 003)

- **Factoring for reuse (call-site correction).** The three rewrites below all
  replace code that lives inside `prepare()`
  (`session_bridge.py:108-110,146-150`), and `prepare()` refuses to run a
  second time against an existing output root (`PRECONDITION-OUTPUT-ROOT-
  EXISTS`). §9 regenerates L01-L04 by editing their worker JSON and
  re-invoking only `finalize()` — which never touches `output/assets` at all,
  it only copies whatever is already there into `document/assets`. So the
  asset-selection resolver, the `visual_maps.py` `map_kind` dispatcher, and
  the evidence-card generator must be written as one function, e.g.
  `visual_maps.regenerate_assets(unit, curriculum, output)`, callable
  independently of `prepare()`'s control flow — writing/overwriting files
  directly under `output/assets` — and called from **two** places: from
  `prepare()` for a freshly-authored unit (replacing
  `session_bridge.py:108-110,146-150` in place), and directly by §9, once per
  regenerated unit, **before** §9's `finalize(..., reentry_reason=...)` call
  (so `finalize()`'s `document.mkdir()`/`copytree` step, which runs after,
  picks up the corrected assets rather than the stale ones). Without this,
  §9's `finalize()`-only re-invocation would re-copy the original,
  unmodified `path_map.svg`/`evidence_card.svg`/`official_reference.jpg`
  bytes into the "regenerated" units, silently leaving issue 003 unfixed for
  the units this plan ships.
- **Receipt hashes stay synchronized.** `regenerate_assets()` changes asset
  bytes on disk, which changes their SHA-256; `finalize()`'s unconditional,
  uncaught `check_receipts()` call (`session_bridge.py:256`) recomputes that
  hash and compares it to whatever is recorded in `visuals[].provenance.
  file_hash` inside `workers/lab.json` — a mismatch raises `CheckFailure` and
  crashes `finalize()` before anything else runs. So
  `regenerate_assets(unit, curriculum, output)` takes and **returns** the
  `unit` dict with each regenerated visual's `provenance.file_hash` (and
  `crop_transform_history`, where the crop changed) recomputed and updated in
  place to match the new on-disk bytes — it is the single place both the
  bytes and their recorded hash change together, so they cannot drift apart.
  Any caller (`prepare()` or §9) must persist the returned `unit` back to
  `workers/lab.json` before the next step that reads it.
- **Asset-selection rewrite.** Replace the `sorted(curriculum.glob("*.jpg"))[0]`
  copy at `session_bridge.py:108-110` with a resolver keyed on each unit's
  `visual_roles` (`arduino_kit_curriculum.v5.yaml:108-112,152-156,193-197,235-239`)
  and the domain's own subject name. For a `subject_identification`/
  `photorealistic *` role: the resolver looks for a verified asset whose
  provenance already names the exact subject (crop of `official_kit_photo.jpg`
  where the subject is visibly present and croppable, or an existing cached
  source photograph scoped to that exact subject). If none exists, the role
  resolves to `BLOCKED`, not to `official_kit_photo.jpg` wholesale — this is the
  plan's one external prerequisite; see the note below.
- **External prerequisite (photography).** `curricula/arduino_kit/` contains
  exactly one photograph (`official_kit_photo.jpg`, a whole-kit inventory shot).
  It does not visibly contain a multimeter (confirmed by issue 004 and the
  `L04.md` mismatch), so L04's `photorealistic meter` role cannot resolve from
  existing assets. Whether it contains a crop-worthy breadboard (L02) or wire
  detail (L03) is unverified today. This plan does **not** acquire new
  photographs — that needs a human with the physical kit. Step 0 of §9
  (regeneration) runs a fail-fast check: for each of L02/L03/L04, attempt to
  locate a croppable region of `official_kit_photo.jpg` containing the named
  subject (manual visual check, recorded in the plan's result file); any subject
  not locatable is recorded as `PDF-ASSET-RESOLVES: BLOCKED (needs verified
  photograph)` for that role, and that unit's photographic-identification role
  stays open rather than being faked — the unit does not reach the L04
  meter-identification acceptance criterion in `issues/004` until a human
  supplies the photograph. This does not block the rest of this plan: every
  other fix (renderer, other visual roles, acceptance gating, POE, receipts, run
  state) proceeds regardless.
- **`connectivity` discriminator (schema prerequisite).** `map_kind:
  "connectivity"` alone is not enough to dispatch correctly: L03's shipped
  `traced_path` (`outputs/arduino_kit_run_v2/L03/workers/lab.json`, and its
  byte-identical `domain.json`) is `["wire endpoint a", "wire endpoint b",
  "expansion board row"]` — three items, not a plain wire pair. The first two
  are the same-wire endpoints; the third, "expansion board row," is a
  separate, non-wire location the learner's own evidence card
  (`child_records`) and steps require them to locate, and is not connected to
  the wire. L04's shipped `traced_path` (`["com socket", "v omega ma
  socket", "ten a socket", "mode dial"]`) is a four-item enumeration of
  distinct sockets/controls, not a chain of connected points at all —
  rendering either shape with a plain wire-pair template would falsely show
  either "expansion board row" or the meter sockets as electrically joined,
  directly undermining issues 003 and 004. Add a `relationship` property to
  `$defs.unpowered_path_map` in
  `curricula/arduino_kit/domain.schema.v1.json`, enum `["same_wire",
  "enumeration"]`, required whenever `map_kind: "connectivity"`. This is a
  third schema edit alongside §5's `evidence_card` addition to
  `breadboard_build_map` and §3/§6's `lab.schema.v4.json` additions — record
  it in "Stop conditions" the same way. §9's L03 patch sets
  `relationship: "same_wire"`; its L04 patch sets `relationship:
  "enumeration"`.
- **Map renderer rewrite.** Replace `_svg()`'s generic "stack every row, label
  every edge NOT CONNECTED" (`session_bridge.py:49-63,146-150`) with
  `runtime/visual_maps.py` (new), dispatching on `(domain.build_map.map_kind,
  domain.build_map.relationship)`:
  - `power_path` (L01): render the traced path as a directed sequence with
    truthful edge labels (`carries current` / `not yet connected`) matching
    `domain.electrical` data — never a blanket "NOT CONNECTED".
  - `connectivity` + `relationship: "same_wire"` (L03): render only
    `traced_path[0]`/`traced_path[1]` as **connected** (same wire, dashed
    "same wire" label), not disconnected — this is the specific defect issue
    003 names for L03. Any further `traced_path` items (L03 has one more,
    "expansion board row") render as their own labeled, unconnected point
    (the same per-item template `enumeration` uses below), never joined to
    the same-wire pair by the dashed label — `same_wire` connects exactly the
    first two items and enumerates the rest, it does not assume `traced_path`
    has exactly two items.
  - `connectivity` + `relationship: "enumeration"` (L04): render each
    `traced_path` item as its own labeled point/target to find, with no
    connecting line implying continuity between them — an identification-style
    rendering, matching the `deterministic jack-and-dial map` visual role
    the manifest requires for L04, never the wire-pair template.
  - `breadboard` (`$defs.breadboard_build_map`,
    `curricula/arduino_kit/domain.schema.v1.json:679-698`, currently unused by
    any shipped unit): switch L02's domain build_map to this map kind (see §5)
    and render five-hole clip groups, the center trench, and rail breaks as a
    real cutaway-style diagram from `wire_endpoints`/`schematic_included`/
    `safety_inset`, not a vertical chain.
  - Any other/unrecognized `map_kind` fails the unit rather than falling back
    to the generic chain, per the issue's acceptance criterion.
  - Also render, from the same domain data, the additional deterministic-render
    roles the manifest requires and issue 003 lists as missing: L02's rail-break
    warning, L03's loose-wire hazard, L04's probe-placement diagram and
    current-mode red-X (§5 supplies the L04 red-X's underlying data). These are
    `deterministic_render`, not `imagegen` — they render from the same
    structured domain fields the map itself uses, so prose, map, and warning
    diagram cannot disagree (`unit_prose.v1.md:55`).
- **Evidence-card rewrite.** Replace the three hardcoded generic lines
  (`session_bridge.py:150`) with a card generator reading each unit's own
  `domain.build_map.evidence_card.child_records` (and, after §5's L02/L03
  domain changes, the corrected fields) as real tick-boxes, plus an adult-signoff
  line wherever `safety.adult_verification.signoff_required` is true.
- **Placement.** Change the PDF assembly step in `finalize()` so each visual is
  placed in the markdown immediately after the section named by its own
  `supports_section`, rather than isolated on a separate asset page (removes the
  "oversized inventory image on its own page" defect).
- **Blocking on missing roles.** If any `visual_roles` entry from the
  curriculum manifest has no resolved, receipted asset, `finalize()` still
  reaches its `acceptance.json` write — the same graceful mechanism as the
  cross-family-bypass case in §3 (`terminal_state` cannot be `"ACCEPTED"`; it
  becomes a distinct non-accepted value, e.g. `"BLOCKED"`, with the unresolved
  role named in the record) — it does **not** raise and abort before writing
  `acceptance.json`, unlike `finalize()`'s existing hard-abort paths
  (`MODEL-OUTPUT-MISSING`, `RESUME-HASH-MISMATCH`,
  `DOMAIN-VERIFIER-FAILED`, a `check_receipts` `CheckFailure`). This matters
  concretely for L04: §2's own "External prerequisite" note already
  establishes as fact, not possibility, that the `photorealistic meter` role
  cannot resolve — §9's Verification sequence requires an actual
  `acceptance.json` recording `BLOCKED` for that unit, which is only
  reachable if this path writes rather than raises.
- Add `tests/runtime/test_visual_maps.py` (new): one test per
  `(map_kind, relationship)` pair (`power_path`, `connectivity`+`same_wire`,
  `connectivity`+`enumeration`, `breadboard`, unrecognized-kind-fails); a
  `connectivity`+`same_wire` test specifically using a three-item
  `traced_path` fixture (matching L03's real shape) asserting only items 0/1
  render as the connected dashed pair and item 2 renders as its own
  unconnected labeled point, not dropped and not joined to the pair; a test
  that the evidence card reflects a fixture's own `child_records` (not the
  three generic lines); and a test that a unit with an unresolvable
  `visual_roles` entry writes a `BLOCKED` `acceptance.json` naming the role,
  rather than raising or substituting an unrelated asset.

### 3. Make acceptance fail-closed against the real check inventory (issue 002)

- Build the required check set for a unit from `policy/checks.v1.yaml` (the
  engine-owned ids) plus `curricula/arduino_kit/checks.v1.yaml` (the
  curriculum-owned ids, per `policy/checks.v1.yaml`'s own header describing
  this two-file split) at `finalize()` start (new helper
  `runtime/checks.py::required_checks_for(unit)`): from the engine catalogue,
  `LAB-SCHEMA-VALID` (whose own `asserts` text already covers the domain
  block's validity against its curriculum's domain schema, so no separate
  `DOMAIN-SCHEMA-VALID` id is needed — that id exists in neither catalogue
  today, and inventing one here would be exactly the uncatalogued-check
  problem this phase exists to avoid), `TEXT-READABILITY-BAND`,
  `TEXT-BLOOM-VERBS`, `DOC-DERIVED-FROM-SOURCE`, `RECEIPT-HASH-RESOLVES`,
  `PDF-ASSET-RESOLVES`, `PDF-TEXT-LEGIBLE`, `PDF-VISUAL-REVIEW`; from the
  curriculum catalogue, add a real `DOMAIN-VERIFIER` entry to
  `curricula/arduino_kit/checks.v1.yaml` (matching that file's existing
  pattern, e.g. alongside `CUR-VISUAL-ROLES`), `stage: deterministic` (its
  subject is a generated unit's `workers/domain.json`, verified at
  `finalize()` time, matching every other generated-unit check in either
  inventory), with `verified_by: FR-P5-VERIFIER-REQUIRED` — the registered
  gate in `tests/gates/registry.py` that already covers this obligation —
  documenting the already-executing `verify_domain.py` subprocess call
  (`session_bridge.py:244-254`) in the entry's `asserts`/`note` prose, not in
  `verified_by` itself (`schemas/checks.schema.v1.json` constrains
  `verified_by` to the pattern `^FR-[A-Z0-9-]+$`, a gate id, not a file-path
  pointer). Include it in the required set from there. Record both
  catalogues' `checks_version` in `unit_checks.json` for auditability
  (issue's last acceptance criterion).
- **Release-table advertising (gate prerequisite).** `DOMAIN-VERIFIER` and
  `VISUAL-ROLES-COMPLETE` (below) are new staged ids in
  `curricula/arduino_kit/checks.v1.yaml`, and that file's own `FR-P2-GATEITEMS`
  rule requires every staged id to be matched by a pattern in its stage's
  `release.advertises` list (`curricula/arduino_kit/checks.v1.yaml:29-40`,
  currently `{static: [CAL-*, CUR-*, L01-*], deterministic: [L01-*, LAB-*]}`).
  Neither new id matches an existing pattern. In the same edit that adds the
  two check entries (both `stage: deterministic`, alongside `LAB-*`), add
  `DOMAIN-VERIFIER` and `VISUAL-ROLES-COMPLETE` to the **deterministic**
  stage's `advertises` list — not `static`'s, since neither entry's subject is
  a static/source artifact — otherwise `FR-P2-GATEITEMS`, a real gate the
  Verification sequence runs, flips from PASS to
  `check-id-unadvertised:DOMAIN-VERIFIER`/`check-id-unadvertised:VISUAL-ROLES-
  COMPLETE` FAIL. Add this release-table edit to "Stop conditions" bookkeeping
  alongside the schema edits already tracked there, since it is a second
  production catalogue this plan edits beyond those schemas.
- Record one explicit `PASS`/`FAIL`/`NOT_RUN_BLOCKED` (with `reason`) entry per
  required check in `unit_checks.json` — replace the hardcoded four-key dict at
  `session_bridge.py:258-261` with this computed set. A check with no
  implementation for its subject records `NOT_RUN_BLOCKED`, never `PASS`.
- **Readability and Bloom-verb checks.** `tests/gates/fr_p5_unit.py:112-296`
  already implements `syllables`/`grade_level`/`readability_violations`/
  `check_readability` and `bloom_flags`/`check_bloom_verbs`, but only against
  hand-written fixtures — it is never imported by production code. Extract
  these functions into `runtime/readability.py` (new, shared module); have
  `tests/gates/fr_p5_unit.py` import from it (no behavior change to the existing
  fixture gate) and have `runtime/checks.py` import the same functions and run
  them against the actual rendered child-facing text §1 produces (excluding the
  adult-verification section). `TEXT-BLOOM-VERBS` records flags but never blocks
  (per policy note); `TEXT-READABILITY-BAND` blocks.
- **Derivation check.** Replace the whole-document byte-equality check at
  `session_bridge.py:240-241` (`lab["domain"] != domain`) with a real call to
  the existing, currently-unwired `checks.check_derivation(unit)`
  (`runtime/checks.py:32-43`), which validates each rendered fact's
  `domain_pointer` resolves and matches — this is what `DOC-DERIVED-FROM-SOURCE`
  actually asserts per `policy/checks.v1.yaml:126-128`. Requires each renderer
  function from §1 to record which `domain_pointer` a rendered fact came from,
  wherever `lab.schema.v4.json` doesn't already carry one — add a minimal
  `derived[]` array to the schema/lab content model if none exists for a given
  fact-bearing field (scope this to the fields §1 and §5 touch, not a
  schema-wide rewrite).
- **PDF checks.** Add `runtime/pdf_inspect.py` (new): `PDF-TEXT-LEGIBLE` uses
  `pdffonts`/`pdftotext -layout` (same toolchain family as the existing
  `pdftoppm`/`pdfinfo` calls in `checks.py:70-103`) to assert body text is at
  or above 9pt effective at 200dpi and no text box reports as clipped;
  `PDF-ASSET-RESOLVES` extracts each embedded image from the shipped PDF and
  confirms its bytes match the `visuals[].provenance.file_hash` receipt for the
  asset `supports_section` places at that point in the document — a receipt
  that doesn't resolve against the actual shipped PDF is a failed gate, not a
  warning (`policy/checks.v1.yaml:165`). `PDF-VISUAL-REVIEW` is recorded as a
  required structured reviewer verdict (checklist: relevance, semantic
  truthfulness, legibility, correct placement, one line item per shipped page)
  that must be explicitly filled and attached to `acceptance.json` before
  `ACCEPTED` — this plan implements the recording mechanism and the block-if-
  absent rule, not full automated computer vision; §5's L04 work supplies the
  first real reviewer pass. This is a narrower claim than full automation and is
  stated as such, not overclaimed.
- **Cross-family judge bypass.** Change `finalize()` so that when
  `routing_divergence` records a cross-family judge bypass
  (`session_bridge.py:289`), `terminal_state` cannot be `"ACCEPTED"` — it becomes
  a distinct non-accepted value (e.g. `"ACCEPTED_PENDING_REVIEW"`) that a
  downstream human step must resolve. The disclosure string alone no longer
  co-exists with `"ACCEPTED"`.
- **Safe re-entry.** `finalize()` is not idempotent against an already-finalized
  output root today: it calls `logger.complete(pending["model_start_id"], ...)`
  (`session_bridge.py:242`) against the `model_start_id` recorded in the
  original run's `worker_request.json`, and that `ACT` is already closed on a
  second call (`ExecutionLogger.complete()` → `_require_open()`,
  `runtime/logger.py:104-111`, raises `LogError`); separately,
  `document.mkdir()` (line 266) and `shutil.copytree(output / "assets",
  document / "assets")` (line 267) both assume `output/document` does not yet
  exist. Add a `finalize(engine, output, *, reentry_reason: str | None = None)`
  parameter: when set (used by §9's regeneration of already-finalized L01-L04),
  `finalize()` opens a **new** logger `ACT` for this re-finalization pass (via
  the existing `logger.start(...)` path) and uses that new start id for the
  `logger.complete(...)` call instead of the stale `model_start_id` — it never
  re-touches the original run's already-closed `ACT`; and it clears and
  recreates `output/document` (`shutil.rmtree(document, ignore_errors=True)`
  then `document.mkdir()`) before the `copytree`, instead of assuming a clean
  directory. Without `reentry_reason`, behavior for a fresh unit is unchanged.
  §9 depends on this; it is listed here because §3 is the section that already
  modifies `finalize()`'s check-recording path, and one coherent set of edits
  to `finalize()` is easier to review than the same function touched from two
  sections.
- **Unresolved-role signal.** §2's "Blocking on missing roles" requires
  `finalize()` to write a `BLOCKED` `acceptance.json` when a manifest
  `visual_roles` entry has no resolved asset (concretely required for L04's
  `photorealistic meter` role), but nothing carries "this role failed to
  resolve" from asset-resolution time into `finalize()` — `lab.schema.v4.json`'s
  `visual` definition requires `provenance`, so an unresolved role cannot be
  represented as a `visuals[]` entry at all. Add a top-level, optional
  `unresolved_visual_roles: [{role, reason}]` array to `lab.schema.v4.json`
  (a fifth schema edit, alongside `derived[]`/`sourced_claims[]`/
  `evidence_card`/`relationship` — add it to "Stop conditions" the same way).
  `regenerate_assets()` (§2) returns this list (empty when every role
  resolved) alongside the `unit` dict; the caller persists it into
  `workers/lab.json`. Add a real `VISUAL-ROLES-COMPLETE` entry to
  `curricula/arduino_kit/checks.v1.yaml` (alongside `CUR-VISUAL-ROLES`,
  whose subject is the manifest declaring roles, not a generated unit
  covering them), `stage: deterministic` (its subject is a generated unit's
  `unresolved_visual_roles[]`, checked at `finalize()` time, matching every
  other generated-unit check in either inventory) asserting
  `unresolved_visual_roles` is empty, with `deferred: RT-5` — no registered
  gate in `tests/gates/registry.py` executes this obligation yet, and
  `schemas/checks.schema.v1.json` requires each entry to satisfy
  `oneOf: [verified_by, deferred]`, so an honest `deferred: RT-5` (the same
  id already covering this check family's other not-yet-gated obligations)
  is the legal form until one is added. Include it in
  `required_checks_for(unit)`'s curriculum-catalogue set, and have
  `finalize()` set `terminal_state: "BLOCKED"` whenever it fails — checked
  before the cross-family-bypass/`ACCEPTED_PENDING_REVIEW` logic, so a
  `BLOCKED` unit is never also reported `ACCEPTED_PENDING_REVIEW`.
- **`run_state` wiring.** Add the `run_state.record_unit_transition(output_root,
  unit_id, terminal_state)` call (§7) directly inside `finalize()`,
  immediately after `acceptance.json` is written — as a standing part of the
  reusable production path, not only invoked by §9's one-off regeneration
  script. §9's own step calling it separately is removed; only
  `run_state.close_run(...)` remains a manual §9 step, since deciding a run
  is closed is inherently a human/session judgment `finalize()` cannot make
  for itself.
- Add `tests/runtime/test_acceptance_gate.py` (new): fixtures with (a) raw-JSON
  body → rejected by §1's renderer test surfaced through this gate, (b) an
  irrelevant image swapped in → rejected by `PDF-ASSET-RESOLVES`, (c)
  deliberately clipped/undersized text → rejected by `PDF-TEXT-LEGIBLE`, (d) a
  unit missing one required check's implementation → recorded
  `NOT_RUN_BLOCKED` and non-`ACCEPTED`, (e) cross-family bypass present →
  non-`ACCEPTED` terminal state, (f) calling `finalize()` twice against the
  same output root with `reentry_reason` set on the second call succeeds
  without a `LogError` and without an existing-directory crash, and calling it
  twice **without** `reentry_reason` on the second call still raises — proving
  re-entry is opt-in, not a silent behavior change for the normal path.

### 4. Correct L04's meter evidence and safety teaching (issue 004)

- Rewrite `curricula/arduino_kit/l04_multimeter_evidence.v1.json` (and the
  corresponding generated `L04/workers/domain.json`/`lab.json`) to the
  model-agnostic path issue 004 explicitly allows: `curricula/arduino_kit/
  roster.md:3,10` and the curriculum manifest (`arduino_kit_curriculum.v5.yaml:
  209`) already only ever call it "a basic digital multimeter" — no exact
  model is named anywhere in this curriculum's own source documents, so
  inventing a verified single-model citation is not achievable without new
  physical verification (the same photography blocker as §2). Take the
  explicitly-allowed alternative: drop the SparkFun-VC830L-sourced universal
  claims — the "shares one small fuse across voltage, resistance, and currents
  under 200 mA" claim (`L04.md:89`, unsupported per the cited source per issue
  004's evidence) and the "10A socket used only above 200 mA" universal
  threshold (`L04.md:63,138`, sourced from an inconsistent, meter-specific
  tutorial) — and replace them with generic, source-honest statements: a shared
  physical jack can carry more than one measurement path without those paths
  sharing one fuse (cite generically, per §6's claim-entailment rule, or mark
  explicitly derived/conservative with premises if a numeric limit is kept),
  and current-range/socket selection is framed as "read your meter's own
  labels and manual," never a universal 200 mA rule.
- Add the direct safety statement to rendered content (currently only in
  `curricula/arduino_kit/arduino_kit_curriculum.v5.yaml:227`'s hidden domain
  object, never reaching the learner per issue's evidence): both child-facing
  (`sequence.explain.why_it_happened` or a dedicated safety callout §1 renders)
  and adult-facing (`safety.adult_verification.limits`/`endpoint_check`) content
  states plainly: "Current mode is never placed directly across a supply."
  Replace the vague self-explanation-only framing at `L04.md:90` with this
  direct statement plus the self-explanation prompt as a supplement, not a
  substitute.
- Wire §2's deterministic current-mode red-X visual with `supports_section:
  troubleshooting` (or `adult_verification`) sourced from this same domain data,
  so the prohibited connection is shown, not just stated.
- Record a completed `PDF-VISUAL-REVIEW` verdict (§3) for L04 specifically
  covering: the current-mode-across-supply statement is present and correctly
  worded, and no jack/threshold claim exceeds what §6's claim-entailment check
  will allow.
- L04's existing `outputs/arduino_kit_run_v2/L04/acceptance.json` (`terminal_
  state: "ACCEPTED"`) is superseded by §9's regeneration, not hand-patched.

### 5. Give Predict-Observe-Explain activities a real observation (issue 005)

- **L02 — schema prerequisite.** `$defs.breadboard_build_map`
  (`domain.schema.v1.json:679-698`) has no `evidence_card` property and, like
  `$defs.unpowered_path_map`, forbids additional properties — only
  `unpowered_path_map` (L02's current map kind) carries `evidence_card`
  today. Before switching L02's `map_kind`, amend
  `curricula/arduino_kit/domain.schema.v1.json`'s `breadboard_build_map`
  entry to add an `evidence_card` property with the same shape
  `unpowered_path_map` already declares (`prompt` string + `child_records`
  array), so §2's evidence-card generator can keep reading
  `domain.build_map.evidence_card.child_records` for L02 after the switch
  without producing a domain object that fails `oneOf` against both `build_map`
  branches. This is a second, narrow schema edit alongside §3's `derived[]`
  and §6's `sourced_claims[]` additions to `lab.schema.v4.json` — record it in
  "Stop conditions" the same way.
- **L02.** Switch `domain.build_map.map_kind` from the generic
  `unpowered_path_map`/`connectivity` shape it currently uses
  (`L02/workers/lab.json`'s `domain.build_map`) to `breadboard`
  (`$defs.breadboard_build_map`, `domain.schema.v1.json:679-698`, amended per
  the prerequisite above), populated
  with the standard five-hole clip group / center trench / rail-break facts
  that define a half-plus breadboard (generic, citable electronics-construction
  knowledge, not device-specific). `observe.what_to_observe` becomes "which
  holes the cutaway diagram (§2) shows sharing one metal clip," with
  `evidence_fields` recording the specific holes/groups the learner ticks
  against that diagram — the diagram itself is the observation's evidence
  source, consistent with `unit_prose.v1.md`'s "the map is rendered from the
  domain's own data" and with the "fully disconnected and unpowered" constraint
  (a verified cutaway visual counts as evidence per issue 005's own expected
  behavior).
- **L03.** After §2's map fix renders `traced_path[0]`/`traced_path[1]`
  ("wire endpoint a"/"wire endpoint b") as connected (same wire) rather than
  "NOT CONNECTED," set `observe.what_to_observe` to identifying (a) that both
  labeled ends in the diagram belong to the physical wire the learner is
  holding, and (b) locating the separately-rendered third point, "expansion
  board row," which the map shows as its own unconnected labeled point, not
  part of the wire; `evidence_fields` records which two named locations the
  wire connects and which row the learner located — this removes the current
  contradiction (prose says "a wire joins two endpoints," the map said the
  opposite) without dropping the expansion-row observation the evidence card
  already requires.
- **L04.** `observe.what_to_observe` becomes reading §2/§4's deterministic
  jack-and-dial diagram and pointing to the correct socket + dial position for
  a named, unpowered planning task; `evidence_fields` records which socket/mode
  the learner identified. No live measurement, consistent with the existing
  `worker_request.json` constraint (`session_bridge.py:184`) and issue 005's
  "safe, exact socket/mode planning task" requirement.
- For every unit, verify `predict.options` each map to a stated observable
  result, `observe.what_to_observe`/`steps`/`expected_observation`/
  `evidence_fields`/`explain.what_you_saw` and the visuals'
  `role`/`supports_section` all refer to the same named event, and evidence
  cards (§2) record the unit-specific prediction/outcome instead of the three
  generic identification lines (already fixed structurally by §2, verified
  again here against the corrected L02/L03/L04 domain data).
- Add `tests/runtime/test_poe_semantics.py` (new): a semantic integration test
  per unit asserting the shared-event linkage above, and a rejecting fixture
  where the only referenced visual is the assembly map itself with no
  `evidence_fields` populated ("look at the answer map" — the exact failure
  mode issue 005 names).

### 6. Validate that cited sources support generated claims (issue 006)

- Extend `schemas/lab.schema.v4.json` with a `content.sourced_claims[]` array
  (each entry: `claim`, `source_locator` {`path`, `section_or_line`},
  `subject_scope` {`exact_model` or `model_independent` + `justification`},
  `evidence_scope`, optional `derivation` {`premises[]`}). Optional at the
  schema level (`minItems: 0`) — coverage is enforced semantically, not by
  schema cardinality, because "does this string contain a claim" isn't a shape
  constraint.
- Add `runtime/checks.py::check_claim_entailment(unit, source_root)` (new): for
  every numeric or safety-critical string in `safety.adult_verification.limits`/
  `endpoint_check` and in `domain` electrical ratings, requires a matching
  `sourced_claims` entry; resolves each entry's `source_locator` inside the
  cached source page under `sources/`; confirms the located text actually
  supports the bounded claim (substring/keyword presence plus explicit
  device-name match when `subject_scope` names an exact model); fails
  device-specific claims whose cited source is generic or names a different
  model unless `subject_scope.model_independent` is set with a non-empty
  `justification`; requires `derivation.premises` for any conservative/derived
  number and forbids attributing it directly to a source stating a different
  figure.
- Fix the two concrete miscitations issue 006 names: L03's `absolute_max: 1 A`
  jumper-wire rating (`L03/workers/lab.json:302-305`), currently cited against
  a source that only supports "a good-quality breadboard is generally limited
  to around 2 A" (`source_01.html:1885`) — either re-cite a source that
  actually supports a 1 A jumper-wire rating, or mark it `derivation.premises`
  explicit and conservative rather than attributing 1 A to the 2 A source; and
  L03's "breadboard expansion board is in the kit" claim
  (`lab.json:207-208`), currently over-scoped from a generic breadboard guide —
  correct the scope or the claim.
- Add visual receipts' `crop_transform_history` requirement: a
  `subject_identification`/`photorealistic *` visual's receipt must record an
  annotation/crop step naming the subject region — a deterministic presence
  check, not pixel-content classification; state this scope limit explicitly
  in the check's docstring and in `policy/checks.v1.yaml`'s note for
  `RECEIPT-HASH-RESOLVES` if amended.
- Wire `check_claim_entailment` into §3's required check set as part of
  `DOC-DERIVED-FROM-SOURCE`'s "safety-critical and numeric claims require
  explicit technical entailment review" requirement.
- Add regression fixtures under `tests/fixtures/`: `unit_claim_wrong_device.
  reject.json`, `unit_claim_unsupported_number.reject.json`,
  `unit_claim_out_of_scope_source.reject.json`,
  `unit_claim_valid_exact_model.accept.json`.

### 7. Record an honest run-level lifecycle state (issue 007)

- Add `schemas/run_lifecycle.schema.v1.json` (new): `run_status` enum
  (`IN_PROGRESS`, `PARTIAL`, `INTERRUPTED`, `BLOCKED`, `COMPLETE`),
  `manifest_unit_count`, `manifest_unit_ids`, `completed_unit_ids`,
  `blocked_unit_ids`, `failed_unit_ids`, `remaining_unit_ids`, `current_unit`,
  `next_unit`, `terminal_reason` (required whenever `run_status != IN_PROGRESS`
  and not `COMPLETE`), `resumable_checkpoint` (last completed unit id + its
  recorded hashes), `workbook_assembled` (bool), timestamps.
- Add `runtime/run_state.py` (new):
  - `record_unit_transition(output_root, unit_id, terminal_state)` — called
    from `finalize()` after each unit's own `acceptance.json` is written;
    updates `outputs/<run>/run_state.json` by recomputing
    `completed_unit_ids`/`remaining_unit_ids` against the manifest (available
    from `results/gate_1_static_preflight.json`'s `unit_ids`), and sets
    `run_status = IN_PROGRESS` while `remaining_unit_ids` is non-empty.
  - `close_run(output_root, reason)` — an explicit action a human/session
    invokes to set `run_status` to `PARTIAL`/`INTERRUPTED`/`BLOCKED` with a
    required `terminal_reason` string, turning an implicit stop into a durable,
    stated decision. Never inferred from directory contents.
  - `assert_resumable(output_root, curriculum_hash, prompt_hash, requested_unit)`
    — before starting a new unit, verifies `manifest_sha256`/`prompt_sha256`
    (already computed the same way as `meta_execution_state.json`) match the
    recorded run state, verifies `requested_unit == next_unit`, and refuses to
    overwrite a unit directory whose `acceptance.json` already records
    `ACCEPTED` (or the new `ACCEPTED_PENDING_REVIEW`), raising rather than
    silently proceeding.
- Add `runtime/workbook.py` (new): `assemble(output_root)` concatenates every
  completed unit's PDF/markdown into `outputs/<run>/workbook/workbook.pdf` plus
  a coverage receipt (`{expected: manifest_unit_count, included:
  len(completed_unit_ids)}`). `run_status` may become `COMPLETE` **only**
  through this function's success path, and only when
  `completed_unit_ids == manifest_unit_ids`, the workbook PDF rasterizes
  nonblank (`checks.rasterize_and_check_nonblank`), and coverage matches
  exactly — never by any other code path.
- Extend root logging: add explicit `unit_started`/`unit_completed`/
  `run_closed` records (distinct from the existing logger concurrency probe
  records already in `execution_log.jsonl`) so "the event/reason that stopped
  execution" (issue's acceptance criterion) has a durable record separate from
  the probe.
- Add `tests/runtime/test_run_state.py` (new): a fixture reproducing the actual
  `arduino_kit_run_v2` shape (35-unit manifest, 4 completed) asserting
  `run_state.json` reports `run_status` other than `COMPLETE`/`ACCEPTED` and
  `remaining_unit_ids` has 31 entries; a test that `assemble()` refuses to mark
  `COMPLETE` with incomplete coverage; a test that `assert_resumable` rejects a
  hash mismatch and rejects overwriting an already-accepted unit.

### 8. Reconcile the policy check inventory with what now executes (bounded)

- `policy/checks.v1.yaml`'s `pdf:` family has **five** ids, and all five carry
  `deferred: RT-5`: `PDF-PAGE-COUNT` (146-151), `PDF-PAGE-NONBLANK` (152-158),
  and the three §3 newly wires in — `PDF-ASSET-RESOLVES`, `PDF-TEXT-LEGIBLE`,
  `PDF-VISUAL-REVIEW` (159-177). `PDF-PAGE-COUNT`/`PDF-PAGE-NONBLANK` are
  already executed today, before this plan changes anything —
  `session_bridge.py:278,287` already call `pdf_page_count`/
  `rasterize_and_check_nonblank` — so the manifest already misrepresents them
  as unexecuted. Separately, in the `lab_document:` family,
  `LAB-SCHEMA-VALID` (65-72) also carries `deferred: RT-5` despite already
  executing (`jsonschema...validate(lab)`, `session_bridge.py:239`) and
  already being recorded `"PASS"` in every shipped `unit_checks.json`. Fold all
  five stale entries into this phase's scope, not just the three §3 newly
  wires in, but **keep `deferred: RT-5` on all six** (`PDF-PAGE-COUNT`,
  `PDF-PAGE-NONBLANK`, `LAB-SCHEMA-VALID`, and the three §3 newly wires in) —
  `schemas/checks.schema.v1.json` constrains `verified_by` to
  `^FR-[A-Z0-9-]+$`, a registered gate id in `tests/gates/registry.py::GATES`,
  and no registered gate executes any of these six ids' production call
  sites, while §8 forbids adding one; a file-path/call-site string is not a
  legal `verified_by` value, so removing `deferred` without one fails the
  schema's `oneOf` requirement, the same defect round 8/9 QA found and fixed
  in §3's `DOMAIN-VERIFIER`/`VISUAL-ROLES-COMPLETE` entries. Instead, apply
  the pattern this section already uses correctly for `TEXT-READABILITY-BAND`'s
  `RT-7` note (below): add (for `PDF-PAGE-COUNT`, `PDF-PAGE-NONBLANK`,
  `LAB-SCHEMA-VALID`) or correct (for the three §3 newly wires in, whose
  `note` fields do not yet exist) each entry's `note` field in place to state
  the check already executes at its real, named call site
  (`session_bridge.py:239` for `LAB-SCHEMA-VALID`, `:278` for
  `PDF-PAGE-COUNT`, `:287` for `PDF-PAGE-NONBLANK`, and the new
  `tests/runtime/test_acceptance_gate.py` / `session_bridge.py`/`checks.py`
  production call sites for `PDF-ASSET-RESOLVES`/`PDF-TEXT-LEGIBLE`/
  `PDF-VISUAL-REVIEW`) rather than leaving or implying it unexecuted — this
  corrects the manifest's *prose* without touching `deferred`, since "is
  `RT-5`'s deferred obligation still outstanding" and "does this repo have a
  gate that verifies the manifest entry is honest" are different questions,
  and only the second one is what `verified_by` answers.
- The four unit-family ids (`TEXT-READABILITY-BAND`, `TEXT-BLOOM-VERBS`,
  `DOC-DERIVED-FROM-SOURCE`, `RECEIPT-HASH-RESOLVES`) already carry
  `verified_by` pointers to existing gates (`FR-P5-READABILITY`,
  `FR-P5-BLOOM-VERBS`, `FR-P5-DERIVATION`, `FR-P5-RECEIPT-HASH`) and no
  `deferred: RT-5` field — leave those pointers as-is. `TEXT-READABILITY-BAND`
  alone carries a `note` ending "...zero generated units exist to score today
  ... RT-7 is the coverage that is missing." Do **not** delete this note: its
  subject is `RT-7` (a unit under `curricula/<name>/units/`), which this plan
  still does not produce (§9 writes to `outputs/<run>/L0N/`). Instead, correct
  it in place to state that the check now executes against real rendered
  content under `outputs/<run>/L0N/`, while `curricula/arduino_kit/units/`
  remains empty and `RT-7`'s own path-specific criterion is still unmet.
  Deleting the note instead would misrepresent `RT-7` as discharged, which is
  exactly the `DRIFT-NO-MISREPORTING` failure mode
  (`policy/checks.v1.yaml:295-300`) and would contradict this plan's own
  "Architectural end state" item 6.
- Do not edit `policy/deferred.v1.yaml`. `RT-5` also covers `LOG-*`, `SEL-*`,
  `DRIFT-*`, and `REV-JUDGE-SINGLE-CROSS-FAMILY`, none of which this plan
  implements; `RT-7`'s acceptance criterion names a `curricula/<name>/units/`
  path this plan's output does not use. Leaving both as-is and stating this
  explicitly (already done in "Architectural end state" item 6) avoids a false
  discharge claim.
- Do not touch `tests/gates/registry.py` or `tests/gates/gate_families.v1.yaml`
  — that meta-governance catalogue pairing validates planning documents
  against their own catalogues and is orthogonal to these seven production
  issues. This does **not** extend to `tests/gates/fr_p5_unit.py`: §3 already
  requires editing its imports (to pull `syllables`/`grade_level`/
  `readability_violations`/`check_readability`/`bloom_flags`/
  `check_bloom_verbs` from the new `runtime/readability.py` instead of
  defining them locally), and "Verification sequence" step 2 depends on that
  edit having happened. `fr_p5_unit.py` is a fixture-gate script, not part of
  the `registry.py`/`gate_families.v1.yaml` catalogue-pairing mechanism this
  bullet actually means to exclude.

### 9. Regenerate and re-accept L01-L04

- Step 0 (fail-fast): run §2's photography-locatability check for L02/L03/L04's
  photographic identification roles; record the result (locatable-and-cropped,
  or `BLOCKED (needs verified photograph)`) before proceeding — this determines
  whether those specific units can reach full `ACCEPTED` or stop at
  `ACCEPTED_PENDING_REVIEW`/`BLOCKED` for that one role, per §3's fail-closed
  rule. This is not a plan-wide blocker (see §2's note).
- Patch `L02/workers/domain.json`+`lab.json`, `L03/workers/domain.json`+
  `lab.json`, `L04/workers/domain.json`+`lab.json` in place with the specific
  field corrections named in §4, §5, and §6 (map_kind, relationship,
  evidence_card, observe/predict fields, the two miscited claims, the L04
  model-agnostic rewrite). `L03/workers/domain.json` is included because
  `lab["domain"]` is byte-identical to it today, and §6's jumper-rating fix
  (`lab.json:302-305`) lives inside that shared `domain.electrical.
  ratings_and_limits` data — §3 removes the one check that used to compare
  the two files (the whole-document equality at `session_bridge.py:240-241`),
  so any `lab["domain"]` field correction touching data also present in the
  standalone `domain.json` must be applied to both files identically, or the
  divergence goes uncaught. This edits existing worker output directly; it
  does not re-run a fresh LLM "bounded unit author" session — regenerating
  net-new pedagogical content beyond fixing the named defects is out of
  scope.
- Call `visual_maps.regenerate_assets(unit, curriculum, output)` (§2's
  factored-out function) for each of L02/L03/L04 (and L01 if its map data
  changed) **before** the next step — this overwrites `output/assets` with
  the corrected map/evidence-card/identification assets in place, since
  `finalize()` itself never generates or resolves assets. Per §2's "Receipt
  hashes stay synchronized" bullet, this call returns the `unit` dict with
  each regenerated visual's `provenance.file_hash` already updated to match
  the new bytes — write this returned `unit` back to `workers/lab.json`
  (replacing the version the previous bullet patched) before the next step,
  so the receipt hashes `finalize()` checks are never stale.
- Re-invoke `session_bridge.finalize(engine, output, reentry_reason=...)` (§3's
  safe-re-entry addition — a bare re-invocation crashes on the already-closed
  logger `ACT` and the already-populated `document/` directory, so this
  parameter is required here, not optional) for L01-L04 against the corrected
  worker JSON, producing re-rendered markdown (§1), the full fail-closed check
  set (§3), and updated `acceptance.json`/`unit_checks.json`, over the assets
  the previous step already corrected on disk. Per §3's "`run_state` wiring"
  bullet, `run_state.record_unit_transition` fires automatically inside this
  call — no separate step is needed for it here.
- Call `run_state.close_run` with `terminal_reason` describing the actual
  scope (four of thirty-five units attempted; L05-L35 not generated) —
  replacing the current silent absence of any run-level record.
- Rasterize each regenerated PDF and visually confirm (by direct inspection, not
  inference) it reads as prose, contains the correct subject-appropriate
  visuals, and states the L04 safety rule directly.

## Verification sequence

1. `python3 -m pytest tests/runtime/ -v` — all new (`test_lesson_render.py`,
   `test_visual_maps.py`, `test_acceptance_gate.py`, `test_poe_semantics.py`,
   `test_run_state.py`) and existing (`test_checks.py`, ...) tests pass.
2. `bash tests/gates/run_gates.sh` (or the runner's documented invocation) — the
   existing fixture-gate suite (`fr_p5_unit.py` and friends) still passes after
   §3's extraction of `readability`/`bloom` functions into
   `runtime/readability.py`, proving the refactor didn't change fixture-gate
   behavior.
3. Regenerate L01-L04 per §9 and inspect: each `document/L0N.md` and its
   rasterized PDF pages contain no serialized object syntax; each
   `unit_checks.json` lists every required check id with `PASS`/`FAIL`/
   `NOT_RUN_BLOCKED`, none hardcoded; each `acceptance.json`'s
   `terminal_state` is `ACCEPTED` only where every required check truly passed,
   and `ACCEPTED_PENDING_REVIEW`/`BLOCKED` where §9's photography gap or a
   cross-family bypass applies. For L02-L04 specifically, diff each
   regenerated `assets/path_map.svg`/`evidence_card.svg`'s SHA-256 against the
   original `outputs/arduino_kit_run_v2/L0N/assets/` bytes and confirm they
   changed — a pass here that reused the original bytes unchanged would mean
   §2's `regenerate_assets` call in §9 did not actually run.
4. Inspect `outputs/arduino_kit_run_v2/run_state.json` (new): `run_status` is
   `PARTIAL` or `INTERRUPTED` (never `COMPLETE`/absent), `remaining_unit_ids`
   has 31 entries, `terminal_reason` is a real, stated sentence.
5. Manually diff L04's rendered child- and adult-facing text against
   `curricula/arduino_kit/arduino_kit_curriculum.v5.yaml:227` to confirm the
   direct current-mode-across-supply statement is present verbatim in meaning.

## Acceptance criteria

- No learner-facing section in any regenerated L01-L04 document contains
  serialized object syntax or literal schema field names; every
  `unit_prose.v1.md`-required block (retrieval, vocabulary, misconception
  confrontation, scaffolding, evidence recording, adult verification) is
  present and renderer tests cover every supported field shape and reject
  unknown/unrendered required fields (issue 001).
- `unit_checks.json` records one explicit result for every check in the
  required set built from `policy/checks.v1.yaml`, including
  `TEXT-READABILITY-BAND` (executed against real rendered text),
  `TEXT-BLOOM-VERBS` (flags, non-blocking), `DOC-DERIVED-FROM-SOURCE`
  (pointer-based, not whole-document equality), `PDF-ASSET-RESOLVES`,
  `PDF-TEXT-LEGIBLE`, `PDF-VISUAL-REVIEW`; a cross-family judge bypass cannot
  coexist with `terminal_state: "ACCEPTED"`; `checks_version` is recorded
  (issue 002).
- Asset selection is role- and `map_kind`-driven; every manifest visual role
  resolves to a shipped, receipted asset or blocks the unit; connectivity,
  wire-pair, and path relationships render with distinct, truthful semantics;
  evidence cards are populated from each unit's own `child_records`; visuals
  are placed beside the text they support (issue 003).
- L04 states no meter-model-specific threshold/jack claim it cannot support
  from a verified source, or explicitly frames itself as model-agnostic; the
  current-mode-across-supply prohibition is stated directly to both child and
  adult, not only in hidden domain data, and is backed by a deterministic red-X
  visual; a recorded reviewer verdict covers this before acceptance (issue
  004).
- For L02-L04, `observe`/`steps`/`expected_observation`/`evidence_fields`/
  `explain.what_you_saw`/visuals all refer to the same named observation, no
  "what you saw" asserts a result the shipped steps/visuals never exposed, and
  a semantic test rejects a POE block whose only evidence is "look at the
  answer map" (issue 005).
- L03's `1 A` jumper rating and "expansion board in kit" claims are corrected
  (re-cited or explicitly marked derived-with-premises); a deterministic check
  resolves every safety-critical/numeric claim's `source_locator` against
  cached source bytes and rejects wrong-device, unsupported-number, and
  out-of-scope-source-reuse fixtures (issue 006).
- `outputs/arduino_kit_run_v2/run_state.json` exists, schema-validates, and
  honestly reports `PARTIAL`/`INTERRUPTED` with 31 remaining units and a stated
  `terminal_reason`; `COMPLETE` is unreachable without full manifest coverage,
  workbook assembly, and PDF review; resume checks reject a hash mismatch and
  refuse to overwrite an accepted unit (issue 007).

## Stop conditions and result

Stop on: a schema change in `lab.schema.v4.json` (§3's `derived[]` addition,
§6's `sourced_claims[]` addition, §3's `unresolved_visual_roles[]` addition)
or in `curricula/arduino_kit/domain.schema.v1.json` (§5's `evidence_card`
addition to `breadboard_build_map`, §2's `relationship` addition to
`unpowered_path_map`) that an existing accepted unit outside L01-L04
depends on in an incompatible way — this plan only touches L01-L04, but
if a shared schema edit would break validation for a unit this plan does not
regenerate, halt and report rather than loosening the schema to paper over it.
Also tracked here: §3's `release.advertises` edit to
`curricula/arduino_kit/checks.v1.yaml` (adding `DOMAIN-VERIFIER` and
`VISUAL-ROLES-COMPLETE` to the deterministic stage's pattern list), a second
production catalogue this plan edits beyond the five schema edits above.
Stop on discovering that `official_kit_photo.jpg` cannot be cropped to any
subject at all (not just L04's meter) — that would mean every unit's
`subject_identification` role is blocked, which is a materially larger finding
than issues 003/004 describe and should be reported before proceeding further
into §9. Do not attempt to acquire new photographs, run a live LLM
content-authoring session, or build any part of the `controller.v1.yaml` state
machine to work around a blocker — those are explicitly out of scope per
"Architectural end state."

Write `plans/runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md`
recording: the verification-sequence baseline captured before changes, every
changed/created/deleted path per phase (§1-§9), the photography-blocker
disposition for L02/L03/L04 (§9 step 0's outcome), full test results (pass/fail
counts for each suite in "Verification sequence"), and any remaining failures
with their exact cause. Append the execution outcome to
`plans/runtime_integrity_remediation/plans.log.md`.
