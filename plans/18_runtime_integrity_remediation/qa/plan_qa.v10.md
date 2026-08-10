# Runtime Integrity Remediation Plan v1 — Focused QA (Round 10)

## Verdict

**CLEAN — 0 Critical, 0 High.** §8's rewrite is present exactly as
`plan_author`'s round-10 log entry describes it, and it resolves round 9's
sole open finding without reintroducing it or any adjacent defect.

§8's first bullet now instructs keeping `deferred: RT-5` on all six ids
(`LAB-SCHEMA-VALID`, `PDF-PAGE-COUNT`, `PDF-PAGE-NONBLANK`,
`PDF-ASSET-RESOLVES`, `PDF-TEXT-LEGIBLE`, `PDF-VISUAL-REVIEW`) — the removal
instruction round 9 flagged as schema-illegal is gone — and instead requires
adding/correcting each entry's `note` field to document its real,
already-executing call site (`session_bridge.py:239/278/287` for the three
pre-existing ids; the new `tests/runtime/test_acceptance_gate.py` /
`session_bridge.py`/`checks.py` sites for the three §3 wires in), the same
pattern §8's own next bullet already applies correctly to
`TEXT-READABILITY-BAND`'s `RT-7` note.

I independently reproduced the combined effect in one fresh scratch copy of
the real repo (`/tmp/qa10_repo`, `cp -r`, deleted after use), applying **both**
round 9's already-verified §3 fix (adding `DOMAIN-VERIFIER`
`verified_by: FR-P5-VERIFIER-REQUIRED` and `VISUAL-ROLES-COMPLETE`
`deferred: RT-5`, both `stage: deterministic`, to
`curricula/arduino_kit/checks.v1.yaml` plus its deterministic
`release.advertises` entries) and round 10's §8 fix (note-only edits to the
six `policy/checks.v1.yaml` ids, `deferred: RT-5` left untouched on all six)
in the same scratch state, from scratch, not by trusting either round's
numbers:

- `jsonschema` (`schemas/checks.schema.v1.json`): 0 errors on
  `policy/checks.v1.yaml` and 0 errors on
  `curricula/arduino_kit/checks.v1.yaml`.
- `tests/gates/fr_p4_policy_schemas.mapping_violations()`, called directly
  against the combined engine+curriculum inventory with the real
  `tests/gates/registry.py::GATES` and `policy/deferred.v1.yaml`: **0**
  problems. `DOMAIN-VERIFIER` reports VERIFIED HERE; all six §8 ids plus
  `VISUAL-ROLES-COMPLETE` report MAPPED via `RT-5`.
- `bash tests/run_gates.sh 2` → `FR-P2-GATEITEMS PASS (6 gate items in the
  engine's release table plus 2 declared by curricula, 44 staged check ids)`.
- `bash tests/run_gates.sh 5` → `FR-P4-ALL-VALIDATE PASS (12 manifest→schema
  pairs resolved from the manifests themselves)`.

Both gates PASS together, in the same scratch state, with all seven affected
ids (the two §3 curriculum ids plus the six §8 engine ids) present — matching
`plan_author`'s round-10 claim independently. (`FR-P2-DEFERRED` still fails in
this scratch copy on unrelated `.claude/` workspace content, a pre-existing,
already-documented baseline condition per round 8/9's carried-forward
observations, not caused by or related to this edit; it blocks
`FR-P4-CHECK-MAPPING`/`FR-P4-AGREEMENT` by dependency, which is why
`mapping_violations()` was also called directly rather than only through the
gate runner.)

`TEXT-READABILITY-BAND`'s `RT-7` note bullet, immediately below the rewritten
six-id bullet, is byte-for-byte the same text quoted in round 8's and round
9's reports: "correct it in place to state that the check now executes
against real rendered content under `outputs/<run>/L0N/`, while
`curricula/arduino_kit/units/` remains empty and `RT-7`'s own path-specific
criterion is still unmet." The new six-id prose does not mention `RT-7`
anywhere except as a comparison ("the pattern this section already uses
correctly for `TEXT-READABILITY-BAND`'s `RT-7` note (below)") — it neither
overwrites nor contradicts RT-7's description. Confirmed by direct read of
`policy/checks.v1.yaml:94-106` (the real, unmodified `TEXT-READABILITY-BAND`
entry): its `note` field still reads "zero generated units exist to score
today; the executed assertion is the fixture pair, and RT-7 is the coverage
that is missing" — matching what the plan says to correct it *to*, not yet
applied (expected, since the plan is not yet implemented).

No ripple effects found elsewhere in the plan. "Architectural end state" item
6 ("`policy/checks.v1.yaml` entries this plan wires into production execution
(§Phase 8) are updated to say so truthfully") is satisfied by the note-only
fix without amendment — nothing in that item requires `verified_by`
specifically, only a truthful update, and a corrected `note` alongside an
honest `deferred: RT-5` is truthful. "Verification sequence" and "Stop
conditions and result" make no claim specific to §8's six ids (grepped both
sections for the six ids' names and for `verified_by`: no hits outside §3's
own, unrevised text) — §8's fix touches no schema, no release table, and no
check id, so it needed no new Stop-conditions bookkeeping entry, and none was
added or is missing. §3's required-check-set bullet (lines 279–304, not
touched this round) already lists `PDF-ASSET-RESOLVES`/`PDF-TEXT-LEGIBLE`/
`PDF-VISUAL-REVIEW` as production-executing per `finalize()`'s wiring, which
is the factual premise §8's note text now documents — the two sections agree.

## Findings

None. 0 Critical, 0 High.

## Observations (non-blocking)

- §8's rewritten bullet says to "add (for `PDF-PAGE-COUNT`, `PDF-PAGE-NONBLANK`,
  `LAB-SCHEMA-VALID`) or correct (for the three §3 newly wires in, whose
  `note` fields do not yet exist)" — but `PDF-ASSET-RESOLVES` (one of the
  "three §3 newly wires in") already has a `note` field today
  (`policy/checks.v1.yaml`: `note: corrects B4 — a receipt that does not
  resolve is a failed gate, not a warning`), confirmed by direct read.
  "Whose `note` fields do not yet exist" is factually wrong for this one id
  (right for `PDF-TEXT-LEGIBLE`/`PDF-VISUAL-REVIEW`, which have none). This
  does not change what an implementer would write — the bullet separately
  names the exact call site to add per id regardless of the add/correct
  verb — and does not affect schema validity or gate results (verified above:
  0 errors, both gates PASS with the note applied as an edit-in-place to
  `PDF-ASSET-RESOLVES`'s existing note, exactly as "correct" implies). Purely
  cosmetic; not raised as a finding.
- Round 8's and round 9's other carried-forward non-blocking observations
  remain open and untouched by round 10's scope (not required by round 10's
  authorization, and not newly affected by it): the schema-edit ordinal
  labels at lines ~201/~397/~490 still don't form one consistent counting
  scheme with "Stop conditions"'s own five-item list; "Verification sequence"
  step 2 still names `bash tests/gates/run_gates.sh` instead of the real
  `tests/run_gates.sh <phase>` and doesn't state the repo's not-all-green
  phase-2 baseline (`FR-P1-GITKEEP`/`FR-P2-DEFERRED` fail today on
  `.claude/`-related content unrelated to this plan); round 7's observation
  that `run_state.record_unit_transition`'s `output.parent` derivation inside
  `finalize()` is still unstated also remains open.

## Round-by-round Critical+High count

R1=2, R2=3, R3=1, R4=2, R5=3, R6=3, R7=2, R8=2, R9=1, R10=0.
