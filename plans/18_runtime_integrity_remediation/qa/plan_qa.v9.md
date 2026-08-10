# Runtime Integrity Remediation Plan v1 — Focused QA (Round 9)

## Verdict

**CHANGES REQUIRED — 1 Critical, 0 High.** Both round-8 fixes are present and
each does what it claims. Reproduced together, in one scratch copy: adding
`DOMAIN-VERIFIER` (`verified_by: FR-P5-VERIFIER-REQUIRED`, `stage:
deterministic`) and `VISUAL-ROLES-COMPLETE` (`deferred: RT-5`, `stage:
deterministic`) to `curricula/arduino_kit/checks.v1.yaml`, with both ids
advertised under the deterministic row instead of static's, yields 0
`jsonschema` errors against `schemas/checks.schema.v1.json`, 0
`mapping_violations()` problems (`DOMAIN-VERIFIER` VERIFIED HERE,
`VISUAL-ROLES-COMPLETE` MAPPED via `RT-5`), `bash tests/run_gates.sh 2`
reports `FR-P2-GATEITEMS PASS (… 44 staged check ids)`, and
`bash tests/run_gates.sh 5` reports `FR-P4-ALL-VALIDATE PASS (12
manifest→schema pairs …)` — both gates clean together, matching
`plan_author`'s round-8→round-9 revision entry exactly. The two non-blocking
observations round 8 raised are also fixed correctly and without
contradiction: "Stop conditions and result" now names the
`release.advertises` edit for real, and the stale "four schema edits" count
is corrected to five (`derived[]`, `sourced_claims[]`,
`unresolved_visual_roles[]`, `evidence_card`, `relationship`), consistent
with Stop conditions' own enumeration.

What survives is §8. Round 8's Finding 1 evidence explicitly noted "the same
construction applied to `policy/checks.v1.yaml` for §8's six ids … produces
six errors of the same kind," and round 8's own Minimal Required Remediation
said to state the legal form "in §3 (and §8)." Round 9's revision fixed only
§3 and explicitly left §8 untouched. §8 still instructs, for
`LAB-SCHEMA-VALID`, `PDF-PAGE-COUNT`, `PDF-PAGE-NONBLANK`,
`PDF-ASSET-RESOLVES`, `PDF-TEXT-LEGIBLE`, and `PDF-VISUAL-REVIEW`: "remove
`deferred: RT-5` … adding a `verified_by`-style pointer to their existing
(pre-this-plan) call sites." I independently reproduced this literally in a
scratch copy of `policy/checks.v1.yaml` and it is the identical illegal
construction: 6 `jsonschema` errors, 6 `advertised-without-owner`
`mapping_violations()` problems, and `FR-P4-ALL-VALIDATE` flips from PASS to
FAIL. This is a live Critical defect in the plan as currently worded, not a
settled round 1-8 finding being re-litigated — it is the still-open half of
round 8's own Finding 1.

## Findings

### 1. Critical — §8's unrevised `verified_by`-as-call-site-pointer instruction is the same schema-illegal construction round 8 flagged for §3, still unfixed, and still flips `FR-P4-ALL-VALIDATE` from PASS to FAIL

**Evidence.** §8 reads: "remove `deferred: RT-5` from `PDF-PAGE-COUNT`,
`PDF-PAGE-NONBLANK`, and `LAB-SCHEMA-VALID` as well, adding a
`verified_by`-style pointer to their existing (pre-this-plan) call sites …
For the three §3 newly wires in, remove `deferred: RT-5` and add a
`verified_by`-style pointer to the new `tests/runtime/test_acceptance_gate.py`
and the new production call sites in `session_bridge.py`/`checks.py`." This
text is unchanged from round 8 (diffed against `plan_qa.v8.md`'s quotation of
it) — round 9's revision touched only §3's `DOMAIN-VERIFIER`/
`VISUAL-ROLES-COMPLETE` bullets, per its own log entry ("Did not touch §8's
six engine-id entries").

`policy/checks.v1.yaml` (§8's target) validates against the same
`schemas/checks.schema.v1.json` as `curricula/arduino_kit/checks.v1.yaml`
(both files' own `schema:` field names it; confirmed by direct read).
`verified_by` is constrained to `pattern: "^FR-[A-Z0-9-]+$"` and each entry
must satisfy `oneOf: [required verified_by, required deferred]` — a call-site
string (a file path, optionally with a line range, or a bare test-file path)
matches neither.

Reproduced mechanically in a scratch copy (`/tmp/qa9_repo`, a fresh `cp -r`
of the real repo). Baseline: `jsonschema` reports 0 errors on
`policy/checks.v1.yaml`; `bash tests/run_gates.sh 5` reports
`FR-P4-ALL-VALIDATE PASS (12 manifest→schema pairs resolved from the
manifests themselves)`. After editing the six named entries exactly as §8
instructs — removing `deferred: RT-5` and setting, e.g.,
`verified_by: session_bridge.py:239` (`LAB-SCHEMA-VALID`),
`verified_by: session_bridge.py:278` (`PDF-PAGE-COUNT`),
`verified_by: session_bridge.py:287` (`PDF-PAGE-NONBLANK`), and
`verified_by: tests/runtime/test_acceptance_gate.py` for the three §3-wired
ids:

```
$ python3 -c "jsonschema validate against schemas/checks.schema.v1.json"
errors: 6
'session_bridge.py:239' does not match '^FR-[A-Z0-9-]+$'
'session_bridge.py:278' does not match '^FR-[A-Z0-9-]+$'
'session_bridge.py:287' does not match '^FR-[A-Z0-9-]+$'
'tests/runtime/test_acceptance_gate.py' does not match '^FR-[A-Z0-9-]+$'
'tests/runtime/test_acceptance_gate.py' does not match '^FR-[A-Z0-9-]+$'
'tests/runtime/test_acceptance_gate.py' does not match '^FR-[A-Z0-9-]+$'

$ bash tests/run_gates.sh 5 | grep FR-P4-ALL-VALIDATE
FR-P4-ALL-VALIDATE FAIL (12 manifest→schema pairs …) — policy/checks.v1.yaml:
  ValidationError:'session_bridge.py:239' does not match '^FR-[A-Z0-9-]+$'
```

Calling `tests/gates/fr_p4_policy_schemas.mapping_violations()` directly
against the modified inventory (with the curricula file's real, current
`deferred: RT-5` entries left alone) independently reports 6 problems, one
per edited id, e.g. `advertised-without-owner:LAB-SCHEMA-VALID —
session_bridge.py:239 is not a gate in the registry`, and the same for the
other five — the identical failure mode round 8 reported for §3's two ids,
at six times the count.

The same trap round 8 identified for §3 applies unchanged: no gate in
`tests/gates/registry.py::GATES` executes `LAB-SCHEMA-VALID` or any
`PDF-*` id's actual production call site (confirmed — grepped `registry.py`'s
38 registered gate ids; none targets these six), and §8 itself forbids touching
`registry.py`/`gate_families.v1.yaml` to add one. §8's own "Architectural end
state" item 6 states its acceptance bar directly: "`policy/checks.v1.yaml`
entries this plan wires into production execution (§Phase 8) are updated to
say so truthfully" — an inventory that fails its own schema is not a
truthful update, it is a broken one.

**Impact.** An implementer following §8 literally ships a
`policy/checks.v1.yaml` that fails its own contract, regressing
`FR-P4-ALL-VALIDATE` from PASS to FAIL — precisely the class of regression
round 7 and round 8 raised for the sibling curriculum file, one file over,
at six ids instead of two. `FR-P4-CHECK-MAPPING`'s
`advertised-without-owner` result (currently masked only because
`FR-P2-DEFERRED` fails today on unrelated `.claude/` workspace files, per
round 8's observation) would surface as soon as that unrelated gate clears.
Architectural end state item 6, the acceptance bar §8 exists to satisfy, is
directly violated: the entries are not "updated to say so truthfully," they
are updated to a form the schema rejects.

**Minimal required remediation.** Apply the same fix round 9 already applied
to §3, to §8: for each of the six ids, either give it
`verified_by: FR-<existing registry gate id>` where a registered gate
genuinely executes it, or keep/restate `deferred: RT-5` (or another real
`RT-N` id in `policy/deferred.v1.yaml`) and document the existing call site
(`session_bridge.py:239`, `:278`, `:287`, or the new
`test_acceptance_gate.py`/`checks.py` sites) in the entry's `asserts`/`note`
prose instead of in `verified_by`. Since no registered gate executes any of
these six ids' actual production call sites today (confirmed by grep), and
§8 forbids adding one, the schema-legal path for all six — matching §3's own
resolution for `VISUAL-ROLES-COMPLETE` — is `deferred: RT-5` with the call
site named in prose, i.e., closer to *not* removing `deferred: RT-5` at all
for these six, just correcting/adding the prose that documents they already
execute (which is what §8's second bullet, for `TEXT-READABILITY-BAND`'s
`RT-7` note, already does correctly for a different id in the same section —
§8 is internally inconsistent, applying two different resolutions to two
classes of already-executing-but-deferred ids without acknowledging it).
Verified in a scratch copy: reverting the six edits (restoring
`deferred: RT-5`, unchanged) returns `jsonschema` to 0 errors and
`FR-P4-ALL-VALIDATE` to PASS — confirming the fix direction, not just the
break.

## Observations (non-blocking)

- The schema-edit ordinal labels scattered through the plan text at their
  point of introduction don't form a consistent sequence with each other or
  with "Stop conditions"'s own listed order (`derived[]`, `sourced_claims[]`,
  `unresolved_visual_roles[]`, `evidence_card`, `relationship`): §2's
  `relationship` bullet (line 201) calls itself "a third schema edit," §5's
  `evidence_card` bullet (line 490) calls itself "a second, narrow schema
  edit," and §3's `unresolved_visual_roles[]` bullet (round-9-corrected) calls
  itself "a fifth schema edit" — none of "third," "second," and "fifth"
  reflects the same counting scheme, and by document reading order
  `relationship` (line 201) actually appears before all of `derived[]`,
  `evidence_card`, and `sourced_claims[]`. Nothing reads these ordinal words
  mechanically (unlike "Stop conditions," which lists all five items by name
  and is itself complete and correct), so this is cosmetic, not a new
  finding — but pre-existing since at least round 6/7 and never previously
  flagged; round 9 did not touch these lines.
- §8's two remediation styles for its own six ids are inconsistent with each
  other even setting the schema-legality problem aside: the `TEXT-*`
  `RT-7` note correction ("correct it in place to state that the check now
  executes … while `RT-7`'s own path-specific criterion is still unmet") is
  exactly the honest deferred-with-documented-execution pattern Finding 1's
  remediation recommends for the six ids above, but §8 does not apply that
  same pattern to the six — it applies the schema-illegal
  remove-`deferred`-add-file-path pattern instead. Fixing Finding 1 by
  applying the `TEXT-READABILITY-BAND`-style note pattern to the six ids
  would resolve both inconsistencies in the same edit.
- Round 8's carried-forward non-blocking observations remain open and
  unaddressed (not required by round 9's authorized scope, and not newly
  broken by it): Verification sequence step 2 still names
  `bash tests/gates/run_gates.sh` instead of the real
  `tests/run_gates.sh <phase>`, and doesn't account for the repo's
  not-all-green phase-2 baseline (`FR-P1-GITKEEP`/`FR-P2-DEFERRED` fail today
  on `.claude/`-related content unrelated to this plan); round 7's
  observation that `run_state.record_unit_transition`'s `output.parent`
  derivation inside `finalize()` is still unstated also remains open.

## Round-by-round Critical+High count

R1=2, R2=3, R3=1, R4=2, R5=3, R6=3, R7=2, R8=2, R9=1.
