# Runtime Integrity Remediation Plan v1 — Focused QA (Round 4)

## Verdict

**CHANGES REQUIRED — 2 Critical, 0 High.** Round 3's remediation (factoring
asset generation into `visual_maps.regenerate_assets()` and calling it from
§9 before `finalize(..., reentry_reason=...)`) does fix the exact defect
Round 3 found: the corrected map/evidence-card/identification bytes now do
get written to `output/assets` before `finalize()` copies them into
`document/assets`. But the factoring introduces two new, independently
mechanically-confirmed breaks in the same §9 regeneration path it was meant
to complete. First, `visual_maps.regenerate_assets()` changes the on-disk
asset bytes without any plan step updating the corresponding
`visuals[].provenance.file_hash` values already hand-patched into
`workers/lab.json` — so `finalize()`'s unconditional, uncaught
`check_receipts()` call raises `CheckFailure: receipt-hash-mismatch` and
crashes §9's re-invocation for every unit whose assets actually changed
(confirmed by reproducing the exact call sequence against the real,
already-`ACCEPTED` `outputs/arduino_kit_run_v2/L04`). Second, §5's
instruction to switch L02's `domain.build_map` to `$defs.breadboard_build_map`
is schema-incompatible with §2's evidence-card generator, which the plan
itself says continues to read `domain.build_map.evidence_card.child_records`
for L02 "after §5's L02/L03 domain changes" (line 198) — `breadboard_build_map`
has no `evidence_card` property and forbids additional properties, so a
breadboard-kind `build_map` carrying an `evidence_card` field fails
`domain.schema.v1.json` validation outright (confirmed by validating a
constructed instance with `jsonschema`). Neither break was present, or even
possible to detect, before Round 3's fix existed, since before that fix §9
never actually ran the new asset-generation code at all.

## Findings

### 1. Critical — `regenerate_assets()` changes asset bytes but nothing updates the `lab.json` receipt hashes those bytes are checked against, so §9's reentrant `finalize()` call crashes for every regenerated unit

**Evidence.** `finalize()` calls `check_receipts({"visuals": {"receipts": [item["provenance"] for item in lab["visuals"]]}}, output)` unconditionally and without a `try`/`except` (`runtime/session_bridge.py:256`). `check_receipts()` (`runtime/checks.py:46-62`) recomputes the actual SHA-256 of each asset file on disk and raises `CheckFailure(f"receipt-hash-mismatch: {relative}")` — a plain `RuntimeError` subclass, uncaught anywhere in `finalize()` — if it does not equal the `file_hash` recorded in that visual's `provenance` inside `workers/lab.json`. Today, those two values match exactly for every shipped unit (verified directly: `L04/assets/path_map.svg` sha256 `b4579fa0...` equals `L04/workers/lab.json`'s `visuals[1].provenance.file_hash`), because in `prepare()`'s original flow the model author writes `lab.json`'s visual provenance *after* the assets already exist, reading `assets/manifest.json` as an authorized input.

§9's sequence inverts this without re-synchronizing the hashes: bullet 2 (plan lines 542-548) hand-patches `workers/domain.json`/`workers/lab.json` "with the specific field corrections named in §4, §5, and §6 (map_kind, evidence_card, observe/predict fields, the two miscited claims, the L04 model-agnostic rewrite)" — this list never mentions recomputing or rewriting `visuals[].provenance.file_hash`. Bullet 3 (lines 549-553) then calls `regenerate_assets()`, which overwrites `output/assets` in place, changing the bytes (and therefore the SHA-256) of `path_map.svg`/`evidence_card.svg`/etc. Bullet 4 (lines 554-560) then re-invokes `finalize(engine, output, reentry_reason=...)`, whose `check_receipts()` call now compares the newly-changed asset bytes against the never-updated, stale hash recorded in the hand-patched `lab.json`.

I reproduced this mechanically against the real repository: implemented the plan's described `reentry_reason` behavior (open a new logger `ACT`, use its id for `logger.complete()`), appended a byte to `outputs/arduino_kit_run_v2/L04/assets/path_map.svg` to simulate `regenerate_assets()` changing the map (leaving `workers/lab.json` untouched, exactly as §9's bullet 2 leaves it), and called the patched `finalize()` against the real, already-`ACCEPTED` `L04` output root. Result: `CheckFailure: receipt-hash-mismatch: assets/path_map.svg`, raised unhandled. The order of §9's bullets doesn't matter — patching `lab.json` before or after asset regeneration makes no difference, since neither step is instructed to write the new hash anywhere.

**Impact.** §9 is the plan's only actual delivery step — the one that produces the "regenerated" L01-L04 the rest of the plan's acceptance criteria describe. As written, it crashes on an unhandled exception for L02, L03, and L04 (every unit whose map/evidence-card assets the plan says must actually change) before reaching the check-recording, `acceptance.json`, or `run_state` steps. This is the same failure class Round 3 found (§9 unable to actually ship the visual fix for these units) reappearing at a different point in the same call sequence, one step later than where Round 3's fix intervened.

**Minimal required remediation.** Add an explicit step, either inside `regenerate_assets()` itself or as a required part of §9's worker-JSON-patch bullet, that recomputes each regenerated asset's SHA-256 and writes it back into the corresponding `visuals[].provenance.file_hash` (and `crop_transform_history`, where the crop changed) entry in `workers/lab.json` before `finalize()` is invoked — e.g., sequence §9 as regenerate-assets-first, then patch `lab.json`'s other named fields *and* its visuals' provenance hashes together in one step, then call `finalize(..., reentry_reason=...)`.

### 2. Critical — §5's L02 switch to `breadboard_build_map` is schema-incompatible with §2's evidence-card generator, which the plan itself says still reads `domain.build_map.evidence_card` for L02 after that switch

**Evidence.** `curricula/arduino_kit/domain.schema.v1.json`'s `build_map` property is a strict `oneOf` between `$defs/breadboard_build_map` and `$defs/unpowered_path_map`, each with `additionalProperties: false`. `unpowered_path_map` (the map kind L02 currently uses, `map_kind` enum `["power_path", "connectivity"]`) is the *only* one of the two `$defs` with an `evidence_card` property. `$defs.breadboard_build_map` (`domain.schema.v1.json:679-698`, the exact lines the plan cites) requires exactly `map_kind, orientation, labelled_features, wire_endpoints, placement_steps, schematic_included, safety_inset` and has no `evidence_card` field at all.

§5's L02 bullet (plan lines 347-352) instructs switching `domain.build_map.map_kind` "to `breadboard` (`$defs.breadboard_build_map`, `domain.schema.v1.json:679-698`)". §2's evidence-card bullet (lines 196-200) instructs the card generator to read "each unit's own `domain.build_map.evidence_card.child_records` (and, **after §5's L02/L03 domain changes**, the corrected fields)" — explicitly asserting that `domain.build_map.evidence_card` still exists on L02 post-switch. These two instructions cannot both be satisfied: a `build_map` object with `map_kind: "breadboard"` that also carries an `evidence_card` key fails `oneOf` against both branches (rejected by `breadboard_build_map` as an extra property, rejected by `unpowered_path_map` on `map_kind` mismatch). I confirmed this by constructing exactly such an object (real `L02/workers/domain.json` with `build_map` replaced by a schema-conformant `breadboard_build_map` payload plus the `evidence_card` field the plan says must remain) and validating it against the real `domain.schema.v1.json` with `jsonschema.Draft202012Validator`: `is not valid under any of the given schemas`.

No `domain.schema.v1.json` change is proposed anywhere in the plan to add an `evidence_card` property to `breadboard_build_map` (or to relocate evidence-card data to a schema location both map kinds share) — the plan's only schema-change discussion, in "Stop conditions" (lines 642-646), names `lab.schema.v4.json`'s `derived[]` and `sourced_claims[]` additions and is silent on `domain.schema.v1.json`.

**Impact.** L02 is §5's lead example for the breadboard fix — the unit issue 005 names first, and the one the plan's own architectural narrative treats as proof the breadboard map kind is now real. As literally specified, patching L02's `domain.json` to satisfy both §5 (switch to `breadboard`) and §2 (keep `evidence_card` under `build_map`) produces a domain object that fails `DOMAIN-SCHEMA-VALID`-equivalent validation (`jsonschema...validate(domain)`, `session_bridge.py:238`, unconditional and uncaught) — `finalize()` crashes before rendering, checks, or acceptance for L02 during §9. This is independent of Finding 1: even if Finding 1 is fixed, L02 specifically still cannot pass schema validation as instructed.

**Minimal required remediation.** Either (a) amend `curricula/arduino_kit/domain.schema.v1.json`'s `breadboard_build_map` `$defs` entry to add an `evidence_card` property matching `unpowered_path_map`'s shape (`prompt` + `child_records`), and add this schema edit to the plan's schema-change/stop-conditions bookkeeping alongside the `lab.schema.v4.json` edits, or (b) relocate evidence-card data to a schema location both `build_map` kinds already share (or a new top-level `domain` property outside `build_map`) and update §2's card-generator instruction accordingly. Either fix must also update §5's L02 bullet so it no longer implies the pre-switch `evidence_card` field simply survives unchanged inside a `breadboard_build_map`.

## Observations (non-blocking)

- §7's root-logging bullet promises `unit_started`/`unit_completed`/`run_closed` records, but only `record_unit_transition` (a completion-time hook, "called from `finalize()` after each unit's own `acceptance.json` is written") has a described call site. No step in the plan describes where `unit_started` would be emitted (`prepare()` is never touched by §7). This doesn't block the plan's core issue-007 deliverables (`run_state.json`'s honest `PARTIAL`/`INTERRUPTED` reporting and `close_run`'s durable `terminal_reason` already satisfy the "event/reason that stopped execution" criterion on their own), but an implementer following the plan literally would have no instruction for where to add the `unit_started` emission it promises.
- The plan's closing "Acceptance criteria" section paraphrases rather than exhaustively restates each issue's own acceptance-criteria list (e.g., issue 002's "an integration fixture ... is rejected" and issue 006's "visual receipts additionally prove the named subject/feature is visible" aren't repeated verbatim in the summary bullets). In every case checked, the underlying commitment is still present in the corresponding "Exact work" section, so this is a summary-completeness nuance rather than a missing deliverable.
