# Runtime Integrity Remediation Plan v1 — Focused QA (Round 7)

## Verdict

**CHANGES REQUIRED — 2 Critical, 0 High.** All three round-6 remediations (the
`DOMAIN-VERIFIER`-not-`DOMAIN-SCHEMA-VALID` rewording, the `run_state` wiring into
`finalize()`, and the `unresolved_visual_roles[]`/`VISUAL-ROLES-COMPLETE`
unresolved-role signal) are genuinely present in the plan text and internally sound
as *described*. But two new, independently fatal defects survive this pass, both
mechanically confirmed against the live repository: (1) the two new curriculum
check ids the plan itself introduces this round — `DOMAIN-VERIFIER` and
`VISUAL-ROLES-COMPLETE`, added to `curricula/arduino_kit/checks.v1.yaml` "matching
that file's existing pattern" — are staged ids with no matching entry in that same
file's own `release.advertises` patterns, which breaks `FR-P2-GATEITEMS`, a real,
currently-passing gate in the registered gate suite the plan's own Verification
sequence step 2 runs; I reproduced this by adding both ids to a scratch copy of the
file and re-running the actual gate, which flipped from PASS to
`check-id-unadvertised:DOMAIN-VERIFIER` / `check-id-unadvertised:VISUAL-ROLES-
COMPLETE` FAIL. (2) The `connectivity` discriminator §2 introduces to stop a
wire-pair template from falsely showing unrelated points as connected — the exact
mechanism round 5 added specifically for this failure mode — misdescribes L03's
actual data: the plan asserts "L03's `traced_path` is a two-item wire pair," but
the real `outputs/arduino_kit_run_v2/L03/workers/lab.json` (and `domain.json`,
byte-identical) `build_map.traced_path` has **three** entries — `["wire endpoint
a", "wire endpoint b", "expansion board row"]` — and the third is not part of the
wire pair. Setting `relationship: "same_wire"` on this object, as §9 literally
instructs, gives the renderer no way to represent "two of these three are the same
wire, the third is a separately-locatable but unconnected place" — it either falsely
renders "expansion board row" as joined to the wire by the same-wire template, or
silently drops it even though L03's own evidence card and steps require the child to
locate it. Either outcome reproduces, for L03, the class of false-connectivity or
missing-role defect this plan and its round-5 fix exist to eliminate.

## Findings

### 1. Critical — the plan's own new curriculum check ids break a currently-passing gate (`FR-P2-GATEITEMS`)

**Evidence.** §3's required-check-set bullet (the round-6 fix) instructs: "add a
real `DOMAIN-VERIFIER` entry to `curricula/arduino_kit/checks.v1.yaml` (matching
that file's existing pattern, e.g. alongside `CUR-VISUAL-ROLES`)... and include it
in the required set from there." The "Unresolved-role signal" bullet (also round 6)
instructs: "Add a real `VISUAL-ROLES-COMPLETE` entry to
`curricula/arduino_kit/checks.v1.yaml` (alongside `CUR-VISUAL-ROLES`...)." Every
existing entry in that file — including `CUR-VISUAL-ROLES` itself — carries a
`stage` field (`static` or `deterministic`), and "matching that file's existing
pattern" is the plan's own instruction for how to write these two new entries.
`curricula/arduino_kit/checks.v1.yaml`'s own header states the rule
`FR-P2-GATEITEMS` (`tests/gates/fr_p2_selector.py::check_gate_items`, a registered
gate in `tests/gates/registry.py`, `activation_phase: 2`, run by
`tests/run_gates.sh`) enforces: "every staged id in this file is matched by a
pattern at its own stage" in that file's own `release.advertises` list. That list
today is exactly `{static: [CAL-*, CUR-*, L01-*], deterministic: [L01-*, LAB-*]}` —
neither pattern matches `DOMAIN-VERIFIER` or `VISUAL-ROLES-COMPLETE`. I confirmed
this mechanically: baseline `bash tests/run_gates.sh 2` reports `FR-P2-GATEITEMS
PASS`; in a scratch copy, appending the two new staged entries exactly as the plan
describes them and re-running the same command flips the result to `FR-P2-GATEITEMS
FAIL (... check-id-unadvertised:DOMAIN-VERIFIER in
curricula/arduino_kit/checks.v1.yaml; check-id-unadvertised:VISUAL-ROLES-COMPLETE
in curricula/arduino_kit/checks.v1.yaml)`. The plan never mentions `release`,
`advertises`, `gate_item`, or `GATEITEMS` anywhere in its text (grepped, zero
hits), so nothing directs an implementer to update the release table alongside
adding the two ids. The plan's exclusion clause — "It does not touch `tests/gates/`
FR-P* meta-governance... that suite checks planning artifacts, not runtime
behavior" — does not cover this: `FR-P2-GATEITEMS` validates
`curricula/arduino_kit/checks.v1.yaml`, a real production catalogue this plan
itself edits twice this round, not a plan document.

**Impact.** As literally specified, adding these two ids the way the plan
describes regresses a real, currently-passing gate to FAIL. The plan's own
Verification sequence step 2 ("`bash tests/gates/run_gates.sh`... the existing
fixture-gate suite... still passes") would not pass. An implementer following the
plan literally either ships a broken gate suite, or has to independently discover
and fix a release-table gap the plan never names — silently reintroducing exactly
the kind of unadvertised-check drift `FR-P2-GATEITEMS` exists to catch, on the two
ids this very plan introduces to fix issue 002's check-inventory drift.

**Minimal required remediation.** Add one line to §3 (or §8, which already touches
this file's stale `deferred: RT-5` flags): update
`curricula/arduino_kit/checks.v1.yaml`'s `release` list so its `static` (or
whichever stage is chosen) row's `advertises` includes patterns matching
`DOMAIN-VERIFIER` and `VISUAL-ROLES-COMPLETE` (e.g. add `DOMAIN-VERIFIER` and
`VISUAL-ROLES-COMPLETE` literals, or a shared prefix pattern if one is introduced
for both).

### 2. Critical — the `connectivity` discriminator does not cover L03's actual three-item `traced_path`, undermining its own purpose for L03

**Evidence.** §2's "`connectivity` discriminator" bullet states as fact: "L03's
`traced_path` is a two-item wire pair, but L04's shipped `traced_path`... is a
four-item enumeration." I read `outputs/arduino_kit_run_v2/L03/workers/lab.json`
(and its byte-identical `domain.json`) directly: `domain.build_map.traced_path` is
`["wire endpoint a", "wire endpoint b", "expansion board row"]` — three items, not
two, and the third is explicitly a different kind of thing (the manifest's L03
`visual_roles` and this unit's own `evidence_card.child_records` — "expansion row
found" — and `steps` — "Find one row on the expansion board the plan would use." —
all treat it as a separate, non-wire location the learner must also locate). The
plan's own Map-renderer-rewrite bullet, describing the fix this discriminator
enables, says: "`connectivity` + `relationship: 'same_wire'` (L03): render
`wire_endpoint_a`/`wire_endpoint_b` as **connected** (same wire, dashed 'same wire'
label)" — language that only accounts for two items, and §9 instructs "its L03
patch sets `relationship: 'same_wire'`" for the whole `build_map` object (the
schema property is per-object, not per-item). §5's L03 POE bullet repeats the same
two-item assumption: "identifying that both labeled ends in the diagram belong to
the physical wire." No part of the plan's `same_wire`/`enumeration` two-value enum,
or any other instruction, specifies what the renderer does with a third `traced_path`
item that is neither a same-wire endpoint nor part of a pure enumeration of
unconnected controls (L04's case).

**Impact.** Implemented literally, the renderer for `connectivity` +
`relationship: "same_wire"` either (a) treats all of `traced_path` uniformly and
renders "expansion board row" as joined to the wire by the same dashed "same wire"
line as the two real endpoints — a false connectivity claim exactly of the kind
issue 003 names and round 5's discriminator exists to prevent, now reproduced for
L03 by the very mechanism meant to close it — or (b) only renders the first two
items and silently drops "expansion board row" from the map even though this
unit's own evidence card and steps require the learner to locate it there,
producing the "visual role required by the manifest is missing" defect issue 003
also names. Either way, L03's visual pipeline fix — one of this plan's four named,
concretely-required deliverables alongside L01/L02/L04 — is not actually achieved
by the mechanism as specified.

**Minimal required remediation.** Correct the factual claim ("two-item" → describe
the real three-item shape), and extend the discriminator (or `same_wire`'s render
behavior) to state explicitly how a `traced_path` item that is neither of the two
same-wire endpoints is rendered — e.g., render it as its own labeled,
unconnected point (matching L04's `enumeration` per-item template) alongside the
dashed same-wire pair, rather than assuming exactly two items whenever
`relationship: "same_wire"` is set.

## Observations (non-blocking)

- §3's "`run_state` wiring" bullet does not spell out how `finalize()` derives the
  *run* root (`outputs/<run>/`) from its own `output` parameter, which — per the
  actual directory layout and CLI usage (`--output-root`) — is always the
  *unit*-level directory (e.g. `outputs/arduino_kit_run_v2/L01`), one level below
  the run root `record_unit_transition` needs to write into. The derivation is a
  one-line `output.parent`, but the plan never states it; worth a one-clause
  addition once Finding 1 is resolved.
