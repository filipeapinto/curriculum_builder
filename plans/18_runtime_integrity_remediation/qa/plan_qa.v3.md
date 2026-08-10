# Runtime Integrity Remediation Plan v1 — Focused QA (Round 3)

## Verdict

**CHANGES REQUIRED — 1 Critical, 0 High.** All three round-2 findings were
independently re-verified by patching a scratch copy of the actual repository
(`/tmp/rirqa3/repo`) with the literal behavior the revised plan text
describes and running it against the real, already-`ACCEPTED`
`outputs/arduino_kit_run_v2/L04`: the `reentry_reason` re-entry design works
mechanically (no `LogError`, no `FileExistsError`, a clean second
`ACCEPTED` with a coherent, monotonic execution log), Phase 8's inventory of
which `policy/checks.v1.yaml` ids carry `deferred: RT-5` now matches the
file exactly, and the `tests/gates/fr_p5_unit.py` carve-out is now explicit
and consistent with §3 and Verification-sequence step 2. Round 3 instead
found a new, mechanically-confirmed defect in the interaction between §2 and
§9: every one of §2's new visual-generation call sites (asset resolver, map
renderer, evidence-card generator) replaces code that lives inside
`prepare()`, and `prepare()` cannot be re-invoked against an already-existing
output root (confirmed: raises `RuntimeFailure("PRECONDITION-OUTPUT-ROOT-EXISTS")`).
§9 regenerates L01-L04 by calling only `finalize()`, which — confirmed by
reading its full body and by the successful scratch re-entry run — never
touches `output/assets` at all; it only copies whatever is already there.
As literally written, §9 cannot produce the "re-rendered visuals (§2)" it
promises: L01-L04 would ship with the exact same defective map SVGs,
generic evidence cards, and wrong-subject photo that issue 003 documents,
while the plan's own fail-closed blocking check (existence/hash-based, not
semantic) would let them through and the acceptance criteria would falsely
assert the visual pipeline was fixed for the shipped units.

## Findings

### 1. Critical — §9's `finalize()`-only re-invocation cannot execute any of §2's new visual-generation code, so L01-L04 ship with the same broken visuals issue 003 describes

**Evidence.** §2's three visual-generation rewrites all cite call sites that
live inside `prepare()`, not `finalize()`:
- "Asset-selection rewrite ... Replace the `sorted(curriculum.glob("*.jpg"))[0]` copy at `session_bridge.py:108-110`" — lines 108-110 are inside `prepare()` (the `photo_candidates = sorted(curriculum.glob("*.jpg"))` / `_copy(photo_candidates[0], output / "assets/official_reference.jpg")` block).
- "Map renderer rewrite ... Replace `_svg()`'s generic ... (`session_bridge.py:49-63,146-150`)" — 49-63 is the `_svg()` helper itself and 146-150 (`_svg(assets / "path_map.svg", ...)`) is its call site inside `prepare()`.
- "Evidence-card rewrite ... Replace the three hardcoded generic lines (`session_bridge.py:150`)" — line 150 (`_svg(assets / "evidence_card.svg", ...)`) is also inside `prepare()`.

Confirmed directly against `runtime/session_bridge.py`: `finalize()`'s only
interaction with `output/assets` is `document.mkdir()` +
`shutil.copytree(output / "assets", document / "assets")` — it never
generates, resolves, or overwrites any asset. Confirmed mechanically in a
scratch copy (`/tmp/rirqa3/repo`) two ways: (a) calling
`session_bridge.prepare(engine, curriculum, "L04", output)` a second time
against the existing `outputs/arduino_kit_run_v2/L04` raises
`RuntimeFailure: /.../L04` (the `PRECONDITION-OUTPUT-ROOT-EXISTS` guard,
`output.exists()` at the top of `prepare()`), so `prepare()` genuinely
cannot be re-run for these units; (b) implementing the plan's described
`reentry_reason` fix and calling only `finalize(engine, output,
reentry_reason=...)` on that same L04 directory succeeds end-to-end
(`SUCCESS ACCEPTED`) while never touching `output/assets/path_map.svg`,
`evidence_card.svg`, or `official_reference.jpg` — it only re-copies them
byte-for-byte into a freshly recreated `document/assets`.

Within §2 itself, only two bullets explicitly name `finalize()`:
"Placement" (repositioning already-resolved visuals in the assembled
markdown) and "Blocking on missing roles" (failing the unit if a
`visual_roles` entry has no *resolved* asset — an existence/receipt check,
not a semantic-correctness check, and not a generation step). Nothing in §2
or §9 states that the asset-selection resolver, `visual_maps.py`'s
`map_kind` dispatcher, or the evidence-card generator move to (or are also
invoked from) `finalize()`. §9 nonetheless states as fact: "Re-invoke
`session_bridge.finalize(engine, output, reentry_reason=...)` ... producing
re-rendered markdown (§1), re-rendered visuals (§2), the full fail-closed
check set (§3) ..." — this is not true of the mechanism as specified.

**Impact.** Issue 003 (P0: "Visuals do not teach or verify the claimed
facts; L04 has no multimeter image") and the visual-dependent portions of
issue 005 (L02's breadboard cutaway, L03's connected-endpoint map) are the
plan's second-highest-priority defects. As written, §9 — the only step that
actually ships any fix into the four units this plan touches — cannot
regenerate a single asset file for them: the wrong-subject whole-kit photo,
the generic "NOT CONNECTED" chain maps, and the three-generic-line evidence
cards named in issue 003 would still be the exact bytes shipped after this
plan runs, re-packaged into a "fixed" PDF with corrected prose and a
fail-closed check set that cannot detect the problem (its role-resolution
check is existence-based, and the stale assets do exist and do have
matching hashes, since they are simply being re-copied unchanged). The
`unit_checks.json`/`acceptance.json` for the regenerated units, and the
plan's own Verification-sequence step 3 ("each `unit_checks.json` lists
every required check id with PASS/FAIL/NOT_RUN_BLOCKED") and Acceptance
criteria bullet for issue 003 ("Asset selection is role- and `map_kind`-
driven; every manifest visual role resolves to a shipped, receipted
asset... visuals are placed beside the text they support") would misreport
issue 003 as fixed for L01-L04 when it is not — a false-discharge claim,
and this is the plan's actual deliverable, not a hypothetical future run.
Round 2 logged the underlying `prepare()`/`finalize()` timing question as a
non-blocking observation, reasoning it was "moot" for §9 because
`domain.json` already exists for L01-L04 by the time §9 runs; that
reasoning addressed only whether the *data* `domain.build_map.map_kind`
would be available, not whether the *code* that reads it is ever invoked in
§9's actual call path. It is not: `prepare()` is where that code is cited
to live, and `prepare()` cannot run again.

**Minimal required remediation.** Add an explicit instruction — either in
§2 or in §9 — that the new asset-selection resolver, `visual_maps.py`
dispatcher, and evidence-card generator are factored into functions callable
independently of `prepare()`'s control flow, and that §9's regeneration
step calls them directly (writing into `output/assets` before invoking
`finalize()`), or that this logic is moved into `finalize()` itself
(consistent with "Blocking on missing roles" already living there). Update
§9's "Re-invoke `finalize()` ... producing re-rendered visuals (§2)" claim
to match whichever mechanism is chosen, and note the regeneration order
(assets before markdown assembly) explicitly, since `finalize()`'s
`document.mkdir()`/`copytree` step depends on `output/assets` already
holding the corrected files by the time it runs.

## Observations (non-blocking)

- §3's "derived\[\] array" instruction ("add a minimal `derived[]` array to
  the schema/lab content model") is ambiguous about whether the property
  belongs at the lab document's top level or nested under `content`.
  `runtime/checks.py::check_derivation(unit)` reads `unit.get("derived", [])`
  and `unit["domain"]` from the same object, both of which are top-level
  keys on the shipped `lab.json` today (`schemas/lab.schema.v4.json`'s
  top-level `properties` are `identity`, `pedagogy`, `sequence`, `content`,
  `safety`, `visuals`, `domain`, with `additionalProperties: false`), so a
  literal-minded implementer following the phrase "content model" could
  reasonably nest it under `content` and mismatch the existing function's
  contract. §6's parallel instruction ("Extend `schemas/lab.schema.v4.json`
  with a `content.sourced_claims[]` array") is unambiguous by contrast,
  which makes the `derived[]` phrasing's imprecision more noticeable. This
  is resolvable by reading `check_derivation`'s existing signature and does
  not on its own block the plan's goal.
- The plan's "Verification sequence" (steps 1-5) has no step that would
  independently have caught Finding 1: step 3 inspects markdown/PDF text and
  `unit_checks.json`/`acceptance.json` fields, and step 5 diffs only the L04
  safety-statement text; nothing in the sequence re-inspects that L02/L03/L04's
  shipped map SVGs or evidence cards actually changed from their pre-plan
  bytes. `tests/runtime/test_visual_maps.py` (§2) tests the new render
  functions in isolation and would pass regardless of whether `finalize()`
  or `prepare()` ever calls them against the real output roots, so the test
  suite passing would not surface Finding 1 either.
