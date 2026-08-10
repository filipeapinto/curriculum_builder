# Runtime Integrity Remediation Plan v1 — Focused QA (Round 6)

## Verdict

**CHANGES REQUIRED — 3 Critical, 0 High.** Five rounds of scrutiny on §9's mechanics
(re-entry, asset regeneration, receipt hashes, schema compatibility, map dispatch,
domain.json sync, blocking behavior) were sound, and those fixes hold up under
mechanical re-verification against the actual repo. But a broader sweep of the rest of
the plan finds three new, independently fatal gaps, all mechanically confirmed against
the repository: (1) the required-check-set the plan builds "from `policy/checks.v1.yaml`"
in §3 names an id, `DOMAIN-SCHEMA-VALID`, that exists in neither `policy/checks.v1.yaml`
nor `curricula/arduino_kit/checks.v1.yaml` — the very inventory §8 exists to reconcile —
directly contradicting the plan's own "not hardcoded" architecture claim and the
`checks_version`-auditability acceptance criterion; (2) §7 asserts
`record_unit_transition` is "called from finalize()," but §3 — the section that owns
every edit to `finalize()` — never adds that call, and §9 instead invokes it as a
separate manual step, so the claimed permanent wiring for issue 007's fix does not
actually exist in the reusable code path, only in the one-off regeneration script, and
no test in the Verification sequence would catch this; (3) the "Blocking on missing
roles" mechanism (§2) asserts that an unresolved `visual_roles` entry causes `finalize()`
to write a `BLOCKED` `acceptance.json`, but no schema field or data path is specified
for carrying "this role could not be resolved" from asset-resolution time (before
`finalize()`, in `regenerate_assets()`) into `finalize()`'s own check-recording logic —
and `lab.schema.v4.json`'s `visual` definition structurally cannot represent an
unresolved role at all (it requires `provenance`, which an unresolved role has none of)
— so the specific L04 `BLOCKED` deliverable the plan's own Verification sequence demands
has no described causal mechanism to produce it.

## Findings

### 1. Critical — Required check set cites a check id that exists in no check inventory

**Evidence.** §3 states: "Build the required check set for a unit from
`policy/checks.v1.yaml` at `finalize()` start (new helper
`runtime/checks.py::required_checks_for(unit)`), covering `lab_document`, `unit`, and
`pdf` families: `LAB-SCHEMA-VALID`, `DOMAIN-SCHEMA-VALID` (already run), ..." I grepped
both check inventories that exist in this repo — `policy/checks.v1.yaml` (the engine's)
and `curricula/arduino_kit/checks.v1.yaml` (the curriculum's, per the engine file's own
header comment describing the two-file split) — for `DOMAIN-SCHEMA-VALID` and
`DOMAIN-VERIFIER`. Neither id appears in either file, under any family. §8, the section
whose entire purpose is "Reconcile the policy check inventory with what now executes,"
also never adds these ids to either catalogue — it only touches `PDF-PAGE-COUNT`,
`PDF-PAGE-NONBLANK`, `LAB-SCHEMA-VALID`'s stale `deferred: RT-5` flags and the three new
`PDF-*` ids. `DOMAIN-SCHEMA-VALID`/`DOMAIN-VERIFIER` are today only two hardcoded keys
in `session_bridge.py:258-261`'s dict — exactly the hardcoding the plan's own
"Architectural end state" item 2 says the required check set must not be ("The required
check set is built from `policy/checks.v1.yaml`, not hardcoded in `session_bridge.py`").

**Impact.** An implementer following §3 literally cannot build `DOMAIN-SCHEMA-VALID`
from `policy/checks.v1.yaml` — the id is not there. They either drop it (silently
regressing a real, currently-executed, safety-relevant check — that the domain object
validates against its curriculum's own domain schema — out of the recorded
`unit_checks.json`, which is itself an issue-002 regression) or hardcode it as an
exception, directly contradicting the stated architecture. Either path also breaks the
issue-002 acceptance criterion "Acceptance output identifies the policy/check-set
version used, so omissions are auditable" — `checks_version` names a catalogue version
that does not actually govern this id, so its presence or absence can never be audited
against that version. This is the exact `DRIFT-NO-MISREPORTING` failure mode issue 002
exists to correct, reintroduced by the plan meant to fix it.

**Minimal required remediation.** Either add `DOMAIN-SCHEMA-VALID` (and, if it is to keep
being recorded, `DOMAIN-VERIFIER`) as real entries to `curricula/arduino_kit/checks.v1.yaml`
(its subject — validating a curriculum's domain object against that curriculum's own
domain schema — matches the file's stated scope) with `verified_by` pointers to their
actual call sites, or fold `DOMAIN-SCHEMA-VALID`'s assertion into the already-catalogued
`LAB-SCHEMA-VALID` (whose own `asserts` text already covers "its domain block validates
against the schema its own curriculum names in manifest domain.schema") and drop the
separate id from the required set and from `unit_checks.json`.

### 2. Critical — `record_unit_transition` is claimed to be wired into `finalize()` but no edit adds it there

**Evidence.** §7 states: "`record_unit_transition(output_root, unit_id, terminal_state)`
— called from `finalize()` after each unit's own `acceptance.json` is written; updates
`outputs/<run>/run_state.json`..." — an explicit claim that this call lives inside
`finalize()`'s own implementation. §3 is the section that owns every other edit to
`finalize()` in this plan (required-check-set computation, the cross-family-bypass
terminal-state change, the `reentry_reason` re-entry parameter) and is explicit about
that ownership elsewhere ("it is listed here because §3 is the section that already
modifies `finalize()`'s check-recording path, and one coherent set of edits to
`finalize()` is easier to review than the same function touched from two sections" —
said of the `reentry_reason` edit). §3 never mentions `run_state` or
`record_unit_transition` anywhere. Instead, §9's regeneration sequence lists it as a
separate, manually-invoked step performed by the operator after calling `finalize()`:
"Call `run_state.record_unit_transition` for each, then `run_state.close_run`..." I
grepped the whole plan for every occurrence of `record_unit_transition`/`close_run`/
`run_state.` — the only two places it is invoked are §7's own description (as an API)
and §9's manual step; no edit to `finalize()`'s body is ever specified to include it.

**Impact.** As literally specified, `record_unit_transition` only ever fires because §9's
script calls it by hand for the four L01-L04 regenerations. `finalize()` itself — the
function this plan explicitly keeps as the ongoing production code path — never
actually updates `run_state.json`. Any future invocation of `finalize()` outside this
one-off script (e.g. a later session preparing and finalizing L05) would silently leave
`run_state.json` stale, exactly reproducing issue 007 for every unit this plan does not
itself hand-drive through §9. This directly contradicts "Architectural end state" item 5
("The run root carries one authoritative lifecycle record... never inferred from
directory contents") as a standing property of the system, not just a one-time fact
about this run. No test in "Verification sequence" would catch the gap, because §9's
manual call produces a correct-looking `run_state.json` regardless of whether the wiring
inside `finalize()` exists.

**Minimal required remediation.** Add an explicit bullet to §3's edit list for
`finalize()` adding the `run_state.record_unit_transition(...)` call immediately after
`acceptance.json` is written (mirroring where §7 says it belongs), and change §9's
corresponding bullet to state that this happens automatically as a consequence of
calling `finalize()`, retaining only the explicit `run_state.close_run(...)` call as a
manual §9 step.

### 3. Critical — no mechanism or schema field carries "role unresolved" from asset resolution to `finalize()`'s `BLOCKED` decision

**Evidence.** §2's "Blocking on missing roles" bullet requires: "If any `visual_roles`
entry from the curriculum manifest has no resolved, receipted asset, `finalize()` still
reaches its `acceptance.json` write... it becomes... `BLOCKED`... This matters
concretely for L04: §2's own 'External prerequisite' note already establishes as fact...
that the `photorealistic meter` role cannot resolve — §9's Verification sequence
requires an actual `acceptance.json` recording `BLOCKED` for that unit." But
`regenerate_assets(unit, curriculum, output)` — the only function in the plan that has
access to the curriculum manifest and therefore to `visual_roles`, and that runs before
`finalize()` — is only specified to return the `unit` dict with existing visuals'
`provenance.file_hash`/`crop_transform_history` corrected ("`regenerate_assets(...)`
takes and **returns** the `unit` dict with each regenerated visual's
`provenance.file_hash`... recomputed and updated in place"). Nothing is specified for
recording that a role could *not* be resolved. I checked `schemas/lab.schema.v4.json`'s
`$defs.visual` definition directly: it requires `role`, `source_kind`,
`supports_section`, and `provenance` (itself requiring `file_hash`/`embedded_as`/etc.) —
an unresolved role, by definition, has no such bytes to hash, so it cannot be
represented as a valid `visual` entry under the current schema, and the plan's schema
stop-conditions list (only `derived[]`, `sourced_claims[]`, `evidence_card`, and
`relationship`) never adds a field to represent one. `finalize()`'s own signature, per
§3, only gains `reentry_reason` — no parameter or read path is added for "which roles
resolved." §3's required-check-set list (`LAB-SCHEMA-VALID`, `DOMAIN-SCHEMA-VALID`,
`TEXT-READABILITY-BAND`, `TEXT-BLOOM-VERBS`, `DOC-DERIVED-FROM-SOURCE`,
`RECEIPT-HASH-RESOLVES`, `PDF-ASSET-RESOLVES`, `PDF-TEXT-LEGIBLE`, `PDF-VISUAL-REVIEW`)
contains no check that compares the manifest's declared `visual_roles` count/names
against `lab["visuals"]`'s actual entries — every one of those checks, as §3 defines
them, only inspects entries that already exist, never the completeness of the required
set. `PDF-ASSET-RESOLVES` is separately claimed (§2, External prerequisite bullet) to
be the check id that records `BLOCKED (needs verified photograph)` for the unresolved
role, but §3's own definition of `PDF-ASSET-RESOLVES` ("extracts each embedded image
from the shipped PDF and confirms its bytes match the `visuals[].provenance.file_hash`
receipt...") has no defined behavior for a role that was never added to `visuals[]` at
all — it is defined purely as a match-existing-entries check.

**Impact.** As specified, nothing in the pipeline ever tells `finalize()` that L04's
`photorealistic meter` role failed to resolve. `finalize()` will simply see whatever
`lab["visuals"]` contains (fewer entries than the manifest calls for) and run its
required checks against those entries only — every one of which can pass trivially,
producing `terminal_state: "ACCEPTED"` or `"ACCEPTED_PENDING_REVIEW"`, not `"BLOCKED"`.
This means the plan's own explicitly required deliverable — "§9's Verification sequence
requires an actual `acceptance.json` recording `BLOCKED` for that unit" — cannot be
produced by the mechanism the plan describes, and the L04 photography gap this plan
itself establishes as fact would ship silently unflagged, which is precisely what issue
003's "every manifest visual role either resolves to a shipped asset or blocks the unit"
acceptance criterion exists to prevent.

**Minimal required remediation.** Specify a concrete signal: e.g., have
`regenerate_assets()` also return (and its caller persist into `workers/lab.json`) an
explicit `unresolved_visual_roles: [{role, reason}]` list (a small, additive schema
change alongside this plan's other three), and add a check to §3's required set (or a
dedicated new id) that fails/blocks whenever that list is non-empty, with `finalize()`
reading it to set `terminal_state: "BLOCKED"` before it would otherwise compute
`"ACCEPTED"`/`"ACCEPTED_PENDING_REVIEW"`.

## Observations (non-blocking)

- §7's `assert_resumable` is specified to refuse overwriting a unit directory whose
  `acceptance.json` already records `ACCEPTED` or `ACCEPTED_PENDING_REVIEW`, but does not
  mention the new `BLOCKED` terminal state — a resume could silently overwrite a
  previously-`BLOCKED` unit's artifacts. Issue 007's own acceptance criterion only names
  "accepted artifacts," so this is arguably in-scope-as-written rather than a defect, but
  it is worth tightening once Finding 3 is resolved and `BLOCKED` becomes a real,
  reachable state.
