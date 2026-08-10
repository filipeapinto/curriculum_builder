# Runtime Integrity Remediation Plan v1 — Focused QA (Round 5)

## Verdict

**CHANGES REQUIRED — 1 Critical, 2 High.** The round-4 remediations verified
correctly: the `finalize(reentry_reason=...)` re-entry path, the
`regenerate_assets()` hash-synchronization contract, and the L02
`breadboard_build_map.evidence_card` schema amendment were mechanically
re-checked (including constructing an actual schema-valid L02 domain instance
against the amended schema) and all hold up. However, tracing §9's full
patch → regenerate_assets → finalize sequence end to end for L02, L03, and L04
specifically surfaces one new Critical defect in §2's map-renderer dispatch
(it has no correct rendering behaviour for L04's actual `connectivity`
build_map shape, and the closest literal reading would render two multimeter
sockets as electrically joined) and two new High defects: §9's patch step
silently leaves `L03/workers/domain.json` carrying the exact miscitation issue
006 requires fixing, and §3's "blocking on missing visual roles" mechanism is
not specified precisely enough to guarantee the `acceptance.json` write that
§9's own Verification sequence requires for L04's (plan-acknowledged,
near-certain) photography gap.

## Findings

### 1. Critical — `connectivity` map_kind has no defined (or safe) rendering behaviour for L04

**Evidence.** §2's "Map renderer rewrite" dispatches `runtime/visual_maps.py`
on `domain.build_map.map_kind` and enumerates exactly three recognized
values plus a catch-all: `power_path` (L01), `connectivity` — described only
as "connectivity used as a wire/endpoint relationship (L03): render
`wire_endpoint_a`/`wire_endpoint_b` as connected (same wire, dashed 'same
wire' label)" — and `breadboard` (L02, post-switch). "Any other/unrecognized
`map_kind` fails the unit."

L04's actual shipped `domain.build_map` (verified directly:
`outputs/arduino_kit_run_v2/L04/workers/lab.json`) is also `map_kind:
"connectivity"`, but its `traced_path` is `["com socket", "v omega ma
socket", "ten a socket", "mode dial"]` — four enumerated items to identify,
not two endpoints of one wire. §9 explicitly regenerates L04's map (Step 2
calls `regenerate_assets` for L02/L03/L04; Verification step 3 requires
diffing L04's `assets/path_map.svg` and confirming it changed). Nothing in
the domain schema (`$defs.unpowered_path_map`, which has only `map_kind` +
`traced_path` + `evidence_card` + `power_on_release`) distinguishes "this
`connectivity` block is a wire pair" from "this `connectivity` block is an
identification list" — the plan's own dispatch rule is keyed only on
`map_kind`, and both L03 and L04 carry the identical value.

This is not a hypothetical: §2's own test list requires a
`connectivity-as-path` test case distinct from `connectivity-as-wire-pair`,
proving the plan itself intends `connectivity` to carry more than one
behaviour — but never states the discriminator, and none of L01-L04 is
actually an instance of `connectivity-as-path` (L01 is `power_path`).

**Impact.** An implementer following the dispatch table literally has two
outcomes, both bad: (a) apply the only specified `connectivity` behaviour
(wire-pair, "connected, same wire") to L04, which would render the meter's
COM socket and V/Ω/mA socket as electrically joined by the same wire — a
false, safety-adjacent claim that directly contradicts issue 004 (the entire
point of which is correct, non-misleading meter-socket guidance) and the
plan's own acceptance criterion that "connectivity, wire-pair, and path
relationships render with distinct, truthful semantics" (issue 003); or (b)
treat L04 as unhandled and raise, which contradicts §9's requirement to
regenerate and diff L04's map asset. Either way this is a self-inflicted new
defect of the exact class (false diagram semantics) this section exists to
eliminate, in one of the three units this round was asked to verify.

**Minimal required remediation.** Add an explicit third `connectivity`
sub-case (or a schema-level discriminator, e.g. a `relationship: "sequence" |
"same_wire" | "enumeration"` field on `unpowered_path_map`) that correctly
covers L04's shape, and change the test list / dispatch prose so `L04` maps
to an identification-style rendering (each item labelled and shown as a
distinct, unconnected point to find) rather than either the power-path or
wire-pair template.

### 2. High — §9's patch step omits `L03/workers/domain.json`, leaving the issue-006 jumper-wire miscitation uncorrected in a shipped artifact

**Evidence.** §9 Step 1: "Patch `L02/workers/domain.json`+`lab.json`,
`L03/workers/lab.json`, `L04/workers/domain.json`+`lab.json` in place" — L03
is listed with `lab.json` only. But the specific defect §6 requires fixing at
`L03/workers/lab.json:302-305` (verified directly) is
`lab["domain"]["electrical"]["ratings_and_limits"][0]`, i.e. data that lives
inside the `domain` object — and today `lab["domain"]` is byte-identical to
the standalone `L03/workers/domain.json` (verified directly:
`lab["domain"] == json.load(open("domain.json"))` is `True`). §3 simultaneously
removes the one check that used to compare these two (`lab["domain"] !=
domain` at `session_bridge.py:240-241`) and replaces it with
`check_derivation(unit)`, which — per `runtime/checks.py`'s actual
implementation — only ever resolves pointers against `unit["domain"]`
(i.e. `lab.json`'s copy) and never reads or compares the standalone
`domain.json` file at all. The new `check_claim_entailment` (§6) has the same
scope: it inspects `unit["domain"]`, never `domain.json`.

**Impact.** If §9 is followed literally, `L03/workers/domain.json` — a
retained, inspectable output artifact, and the exact file passed to the
external `verify_domain.py` subprocess — keeps the uncited "1 A" claim
attributed to a source that only supports "around 2 A," the precise
miscitation issue 006 names as something this plan must fix. No check in the
post-§3 pipeline would ever notice the divergence between `domain.json` and
`lab["domain"]`, because the only check that used to compare them is being
deleted. The plan's own acceptance criterion ("L03's 1 A jumper rating ...
claims are corrected") would be false for this artifact even though the
rendered PDF and `lab.json` are fixed.

**Minimal required remediation.** Add `L03/workers/domain.json` to §9 Step
1's patch target list alongside `lab.json` for this specific field, or note
explicitly in §9 that any `lab["domain"]` field correction touching data also
present in the standalone `domain.json` must be applied to both files
identically.

### 3. High — "blocking on missing visual roles" isn't specified as a graceful write, contradicting §9's requirement that L04 (a guaranteed case) produce a `BLOCKED` `acceptance.json`

**Evidence.** §2's "Blocking on missing roles" bullet: "`finalize()` fails
the unit (does not proceed to `ACCEPTED`) if any `visual_roles` entry ... has
no resolved, receipted asset." §9's Verification sequence step 3 requires,
for the regenerated units: "`acceptance.json`'s `terminal_state` is
`ACCEPTED` only where every required check truly passed, and
`ACCEPTED_PENDING_REVIEW`/`BLOCKED` where §9's photography gap ... applies."
§2's own "External prerequisite" text already establishes, as fact rather
than possibility, that L04's `photorealistic meter` role "cannot resolve from
existing assets" — this is not a maybe, it is asserted to be certain before
§9 even runs.

`finalize()`'s current code structure only ever writes `acceptance.json` once,
near the very end of the function (`session_bridge.py:291`), after every
prior check; every existing failure path (`MODEL-OUTPUT-MISSING`,
`RESUME-HASH-MISMATCH`, `DOMAIN-VERIFIER-FAILED`, `check_receipts`'s
`CheckFailure`) raises and aborts the function with **no** `acceptance.json`
written at all. The plan's "fails the unit" phrasing for missing visual roles
uses the same vocabulary as these hard-abort paths, and — unlike the
cross-family-bypass case two paragraphs earlier, which explicitly names the
graceful mechanism ("`terminal_state` cannot be `"ACCEPTED"`... it becomes a
distinct non-accepted value") — never states that the missing-role case must
still reach the `atomic_json(... "acceptance.json" ...)` write with a
`BLOCKED` state rather than raising.

**Impact.** If implemented as a raised exception (consistent with every other
"fails" path already in `finalize()`), L04's regeneration in §9 would crash
before writing `acceptance.json` at all — since the photography gap for
L04's meter photo is not a maybe, it is a certainty per the plan's own text.
That directly contradicts §9's Verification step 3, which requires
`acceptance.json` to exist and show `BLOCKED` for exactly this unit/role.

**Minimal required remediation.** State explicitly, alongside the
`ACCEPTED_PENDING_REVIEW` mechanism in §3, that an unresolved required visual
role also produces a graceful non-`ACCEPTED` `terminal_state` (e.g.
`BLOCKED`) written to `acceptance.json` — not a raised exception — so §9's
Verification requirement is actually reachable for L04.

## Observations (non-blocking)

- §2 assigns an explicit `supports_section` only to L04's new red-X visual
  ("`troubleshooting` (or `adult_verification`)"). L02's new "rail-break
  warning" and L03's new "loose-wire hazard" roles are never given a
  `supports_section`, which the new placement mechanism (§2, "Placement")
  needs to decide where each visual is inlined. A reasonable implementer can
  infer `troubleshooting` by analogy to L04, but the plan doesn't say so.
