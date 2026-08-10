# Runtime Integrity Remediation Plan v1 — Focused QA (Round 8)

## Verdict

**CHANGES REQUIRED — 1 Critical, 1 High.** Both round-7 remediations are present
and each does what it claims for the thing it was aimed at. Fix 1 was reproduced
mechanically: adding `DOMAIN-VERIFIER` and `VISUAL-ROLES-COMPLETE` to a scratch
copy of `curricula/arduino_kit/checks.v1.yaml` *together with* the new
"Release-table advertising" bullet's `advertises` entries keeps `FR-P2-GATEITEMS`
at PASS (baseline `PASS (… 42 staged check ids)` → modified `PASS (… 44 staged
check ids)`), where round 7 reproduced a FAIL. Fix 2's corrected factual claim
matches the shipped data exactly: `outputs/arduino_kit_run_v2/L03/workers/lab.json`
has `build_map.traced_path == ["wire endpoint a", "wire endpoint b", "expansion
board row"]`, `lab["domain"]` is equal to `workers/domain.json`, and L04's is the
four-item `["com socket", "v omega ma socket", "ten a socket", "mode dial"]`; the
revised `same_wire` render rule (connect items 0/1, enumerate the rest) covers
L03's real shape, its per-item template is specified in the `enumeration` bullet
directly below it, and §5's L03 POE rewrite and §9's `relationship: "same_wire"`
patch instruction remain consistent with it. No new finding is raised against
fix 2.

What survives is the *other half* of fix 1. Round 7's finding was that adding
these two ids as the plan words them breaks a currently-passing gate; the round-8
bullet fixed the release-surface half only. Written as §3 still literally
instructs — `verified_by` pointing at the executing call site — the two entries
are invalid against `schemas/checks.schema.v1.json` and flip a second,
currently-passing gate (`FR-P4-ALL-VALIDATE`) from PASS to FAIL, reproduced in a
scratch copy. Separately, the round-8 bullet's new decision to file both as
`stage: static` mis-states when they run, in a plan whose own goal is an inventory
that says truthfully what executes.

## Findings

### 1. Critical — the two new inventory entries are schema-invalid as §3 words them, flipping `FR-P4-ALL-VALIDATE` from PASS to FAIL

**Evidence.** §3 instructs adding `DOMAIN-VERIFIER` "with a `verified_by`/`method`
pointer to the already-executing `verify_domain.py` subprocess call
(`session_bridge.py:244-254`)", and §8 uses the same construction for six engine
ids ("remove `deferred: RT-5` and add a `verified_by`-style pointer to their
existing (pre-this-plan) call sites", "…to the new
`tests/runtime/test_acceptance_gate.py` and the new production call sites in
`session_bridge.py`/`checks.py`"). `schemas/checks.schema.v1.json` — the contract
both inventories validate against, named in the header of
`curricula/arduino_kit/checks.v1.yaml` — constrains `verified_by` to
`"pattern": "^FR-[A-Z0-9-]+$"` ("A gate in this suite that executes the id") and
requires each entry to satisfy `oneOf: [required verified_by, required deferred]`.
A file path is not a legal value, and dropping `deferred` without a legal
`verified_by` fails the `oneOf`.

Reproduced mechanically in a scratch copy of the repo. Baseline
`bash tests/run_gates.sh 5`: `FR-P4-ALL-VALIDATE PASS (12 manifest→schema pairs
resolved from the manifests themselves)`. After adding the two entries exactly as
§3 describes them (both `stage: static`, alongside `CUR-VISUAL-ROLES`, with the
round-8 `advertises` additions):

```
FR-P2-GATEITEMS   PASS (… 44 staged check ids)
FR-P4-ALL-VALIDATE FAIL (12 manifest→schema pairs …) — curricula/arduino_kit/checks.v1.yaml:
  ValidationError:'runtime/session_bridge.py:244-254' does not match '^FR-[A-Z0-9-]+$'
```

Direct `jsonschema` validation of the modified inventory reports exactly two
errors, one per new entry. The same construction applied to `policy/checks.v1.yaml`
for §8's six ids (`LAB-SCHEMA-VALID`, `PDF-PAGE-COUNT`, `PDF-PAGE-NONBLANK`,
`PDF-ASSET-RESOLVES`, `PDF-TEXT-LEGIBLE`, `PDF-VISUAL-REVIEW`) produces six errors
of the same kind. `FR-P4-CHECK-MAPPING`'s `mapping_violations()`
(`tests/gates/fr_p4_policy_schemas.py:130-168`), called directly against the
modified inventory, independently reports
`advertised-without-owner:DOMAIN-VERIFIER — runtime/session_bridge.py:244-254 is
not a gate in the registry` and the same for `VISUAL-ROLES-COMPLETE`; that gate is
BLOCKED in this repo today only because `FR-P2-DEFERRED` fails for unrelated
`.claude/` workspace files, so it would surface as soon as that clears.

Note the trap the plan is in: `verified_by` must name an id in
`tests/gates/registry.py::GATES`, and no registered gate executes either new
check, while §8 explicitly forbids touching `registry.py`/`gate_families.v1.yaml`
to add one. So neither the plan's stated wording nor "add a gate" is available as
written — the entries must take a `deferred: RT-N` mapping or point at an existing
gate that genuinely executes them.

**Impact.** An implementer following §3 literally ships a
`curricula/arduino_kit/checks.v1.yaml` that fails its own contract, regressing
`FR-P4-ALL-VALIDATE` from PASS to FAIL — the same class of regression round 7
raised, on the same edit, one gate over. §8's identically-worded instruction
extends it to `policy/checks.v1.yaml`. The plan's Verification sequence step 2
("the existing fixture-gate suite … still passes") would not hold, and the
check-inventory honesty this plan exists to restore (issue 002, Architectural end
state item 6) would instead be recorded in a form the inventory schema rejects.

**Minimal required remediation.** State in §3 (and §8) the legal form these
entries take. Either give each id `verified_by: FR-<existing registry gate id>`
where a registered gate genuinely executes it, or give it `deferred: RT-N` naming
a real id in `policy/deferred.v1.yaml` with the runtime call site recorded in the
entry's `asserts`/`note` prose rather than in `verified_by`. A schema-legal,
gate-clean variant was verified in a scratch copy: `DOMAIN-VERIFIER` with
`verified_by: FR-P5-VERIFIER-REQUIRED` and `VISUAL-ROLES-COMPLETE` with
`deferred: RT-5`, both `stage: deterministic` and advertised in the deterministic
row, yields 0 schema errors, 0 `mapping_violations`, and
`FR-P2-GATEITEMS PASS` + `FR-P4-ALL-VALIDATE PASS`.

### 2. High — filing both new ids as `stage: static` mis-states when they run

**Evidence.** The round-8 bullet decides the stage for the first time: "In the same
edit that adds the two check entries (both `stage: static`, alongside
`CUR-VISUAL-ROLES`), add `DOMAIN-VERIFIER` and `VISUAL-ROLES-COMPLETE` to the
`static` stage's `advertises` list." Both ids' subjects are *generated units*:
`DOMAIN-VERIFIER` asserts the copied verifier exits zero against a unit's
`workers/domain.json` at `finalize()` time (`session_bridge.py:244-254`), and
`VISUAL-ROLES-COMPLETE` asserts a generated unit's new
`unresolved_visual_roles[]` array is empty. Enumerating both inventories, every
`static` id today owns a policy or curriculum *source* file —
`policy/calibration.v1.yaml`, `meta_prompt/curriculum.prompt.v1.md`,
`policy/controller.v1.yaml`, `arduino_kit_curriculum.v5.yaml`,
`kit_calibration.v1.yaml`, `l01_unpowered_power_path.json` — and no `static` id has
a generated unit as its subject. Every generated-unit check in
`policy/checks.v1.yaml` is `deterministic` or `golden` (`LAB-SCHEMA-VALID`:
golden; `LAB-POE-ORDER`, `LAB-BLOOM-DEPTH`, `TEXT-READABILITY-BAND`: deterministic;
the `pdf:` family: golden). `fr_p2_selector.py:840-845` states the rule the stage
field carries: "An id is covered only by a pattern advertised at *its own* stage:
an id advertised under the wrong gate item is claimed by a stage that does not run
it."

**Impact.** The two ids this plan adds to fix issue 002's inventory drift would
themselves enter the inventory claiming a release stage that does not run them —
a new misrepresentation in a production catalogue, introduced by the edit whose
purpose is truthfulness (Architectural end state item 6). `FR-P2-GATEITEMS` cannot
catch it: it only checks that a staged id is advertised at whatever stage it
declares, so a wrong-but-self-consistent stage passes. The field is declarative in
this repo today (no code outside `fr_p2_selector.py` reads `stage`), which is why
this is High and not Critical — nothing breaks mechanically, but the record is
wrong and nothing will report it.

**Minimal required remediation.** Change the round-8 bullet to file both entries
as `stage: deterministic` (matching every other generated-unit check) and to add
the two literals to the **deterministic** row's `advertises` list rather than the
`static` row — the two decisions are coupled, since `FR-P2-GATEITEMS` requires the
pattern and the id to sit at the same stage. Verified in a scratch copy: with both
entries at `stage: deterministic` and advertised in the deterministic row,
`FR-P2-GATEITEMS` reports `PASS (… 44 staged check ids)`.

## Observations (non-blocking)

- The round-8 log entry states the release-table edit was added "to Stop
  conditions bookkeeping alongside the four schema edits". It was not: "Stop
  conditions and result" (plan lines 789-806) still lists only the schema edits,
  and the string `release` appears nowhere outside §3. The §3 bullet does carry
  the instruction inline, so an implementer reading the plan is not misled — but
  the two texts disagree. (Relatedly, §3 says "the four schema edits already
  tracked there" while Stop conditions tracks five: `derived[]`,
  `sourced_claims[]`, `unresolved_visual_roles[]`, `evidence_card`,
  `relationship`.)
- The revised `same_wire` rule is positional ("connects exactly the first two
  items and enumerates the rest") but the new `relationship` property added to
  `$defs.unpowered_path_map` records nothing about that convention. Correct for
  every unit this plan ships (L03's real `traced_path` puts the pair first), but a
  future author could set `relationship: "same_wire"` on a path whose pair is not
  items 0/1 and get a silently false connectivity claim. A sentence in the
  property's `description` stating the convention would close it.
- Verification sequence step 2 still names `bash tests/gates/run_gates.sh`; the
  real runner is `tests/run_gates.sh` and it requires a phase argument
  (`./tests/run_gates.sh <phase>`). Worth noting that the repo's phase-2 baseline
  is not all-green today (`FR-P1-GITKEEP` and `FR-P2-DEFERRED` fail on `.claude/`
  workspace files unrelated to this plan, blocking three more), so step 2 needs a
  per-gate baseline delta, not "the suite passes".
- Round 7's non-blocking observation is still open: §3's "`run_state` wiring"
  bullet passes `output_root` to `record_unit_transition` from inside
  `finalize()`, whose `output` parameter is the *unit* directory
  (`outputs/<run>/L0N`); the one-clause `output.parent` derivation is still
  unstated.
