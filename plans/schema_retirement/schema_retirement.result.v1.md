# Schema retirement — result

**Prompt executed:** `plans/schema_retirement/prompt/schema_retirement.prompt.v1.md`
**Result written:** 2026-08-02
**Outcome:** complete. `./tests/run_gates.sh 4` reports 30 PASS / 0 FAIL, `run_gates.sh 5`
reports 38 PASS / 0 FAIL, `python3 tests/check_meta_prompt.py` reports EXECUTABLE (6/6),
`git status --porcelain` is empty. `schemas/*.json` holds exactly one version of each
contract; `schemas/deprecated/` holds the four superseded ones plus `.gitkeep`;
`FR-P1-SCHEMA-RETENTION` reports `4 files, 4 retired` with zero live references.

---

## The finding, confirmed before any edit

The retention justification named in `RT-6` — "both v1 contracts stay in `schemas/` for
as long as any accepted record cites them" — was empty. Confirmed directly:

- no unit has ever been generated (`RT-7`);
- no logger or execution log exists (`RT-5`);
- no `curricula/*/units/` directory or output root exists anywhere in the repo;
- `meta_prompt/curriculum.prompt.v1.md` itself stated, of the other two, "zero units were
  ever accepted under either."

Nothing accepted under any of the four superseded schemas ever existed. All four moved.

## What moved

`schemas/lab.schema.v3.json`, `curriculum.schema.v4.json`, `execution_log.schema.v1.json`
and `routing_decision.schema.v1.json` → `schemas/deprecated/`, via `git mv` (commit
`270c3fe`), preserving history — `FR-P0-HISTORY`'s `git log --follow` reaches the baseline
commit for all four.

## What was deleted, from which gate, and why

- **`tests/gates/fr_p2_selector.py`** — `DECISION_V1`, `LOG_V1` and `v1_mutation()`, and
  the leg of `FR-P2-CONTRACT-VERSIONED` that read them ("both v1 files remain in
  `schemas/`, byte-unchanged from `HEAD~`"). That leg *was* the retention claim; once the
  finding held, it asserted something that had become false by design, not by defect.
  `bound_violations()` (`FR-P2-BOUND`) lost its "retained-contracts table states RT-6 and
  restricts to accepted work" leg for the same reason — the table it read no longer
  exists. What survives in both: `FR-P2-CONTRACT-VERSIONED` now asserts v2's own required
  shape directly (no longer diffed against v1), and `FR-P2-BOUND` still asserts a v1
  basename is never an authorized input.
- **`tests/gates/fr_p1_retention.py`** — `RETAINED_CONTRACTS` and the "still cited" block
  in `check_schema_gate`, plus the now-unused `citations_of()` helper. Same reasoning:
  "a contract stays outside `deprecated/` for as long as anything cites it" had nothing
  left to protect. The core retention gate (`retention_gate_violations` — a schema may
  enter `deprecated/` only when its basename has zero live hits) is untouched.
- **`tests/gates/fr_p3_calibration.py`** — `FROZEN_CONTRACTS_EXEMPT`, a name-based
  exemption keeping the two v1 schemas out of the "no hard-coded calibration literal"
  scan (their frozen `$id` carries a vendor-namespace string that would otherwise trip
  it). Deliberately *not* removed in the same commit as the other two exemptions —
  removing it before the `git mv` would have failed `FR-P3-NO-LITERALS` immediately, since
  the files were still live schemas at that point. It was replaced, in the same commit as
  the move, with the same `common.under_deprecated` path exclusion used everywhere else:
  a retired schema is not a live contract for this gate to police, regardless of name.
- **Two fixtures**, whole files: `contract_v1_edited_in_place.reject.json` (tested that a
  v1 contract mutated in place is caught — the mutation-must-never-happen claim is gone
  with the leg it proved) and `act_v1_shaped.accept.json` (tested that a v1-shaped record
  still validates against v1 — the "v1 stays usable" claim is gone the same way). Neither
  defect is re-expressible once v1 is fully retired rather than retained.
- **`policy/deferred.v1.yaml` `RT-6`** — rewritten, not deleted. It now records discharge
  by obsolescence ("no record was ever accepted under either superseded v1 contract...
  retirement never actually needed a v2-emitting logger") rather than the original,
  never-true blocking condition. `RT-5` and `RT-7` are untouched.

## The `deprecated/` scan-exclusion decision (step 5)

Recommended by the prompt and taken as written: `common.under_deprecated()` (new, in
`tests/gates/common.py`) excludes any path with a `deprecated` component from every
gate's basename/citation scan — not only `schemas/deprecated/`, since
`meta_prompt/deprecated/*.md` cite the old basenames verbatim and nothing reads that
folder. It replaced two different ad hoc mechanisms that had converged on the same gap:
`fr_p1_retention.py`'s scan previously excluded only `schemas/deprecated/` itself, and
`fr_p2_selector.py`'s `live_v1_references` had been (coincidentally, and only until the
retained-contracts table was deleted) excluding `meta_prompt/deprecated/` by matching
identical leftover text against that table.

Proof the narrowing doesn't blind the gate, as required: `deprecated_narrowing_still_bites()`
in `fr_p1_retention.py`, a synthesized fixture (scratch tree outside the repo, matching
the existing `FR-P1-GITKEEP` pattern) that builds a live citation and a `deprecated/`
citation of the same basename and asserts the scan drops only the buried one.

## Unanticipated work

The prompt's worklist didn't anticipate two knock-on breaks, both fixed in the commits
where they surfaced rather than deferred:

- Removing the prompt's retained-contracts table broke `FR-P2-CONTRACT-VERSIONED` and
  `FR-P2-BOUND` immediately (not just at the later `git mv`), since both read that table
  directly. Fixed in the same commit as the table's removal (`50cac32`) rather than left
  red until the later "remove exemptions" step, per the "30 PASS, 0 FAIL at every commit"
  constraint.
- `FR-P0-TREE` (a phase-0 structural gate, unrelated to schema retention) parses
  `folder_refactoring.plan.v6.md`'s §4/§5 as a literal, ongoing existence check for the 26
  files that plan's 13 move rules placed — including these four, at their `schemas/`
  destination. `check_tree` now accepts a `schemas/` destination as satisfied when the
  same basename is found under `schemas/deprecated/` instead: that plan's own §6 already
  names `schemas/deprecated/` as where a retired schema goes, so a later, separately
  authorized plan moving the file again is not v6's own move having failed to stick. The
  rule/file counts (13, 26) are untouched — they describe what v6 itself moved, not what
  happened after. §4's annotations for the four entries changed from `RETAINED` to
  `RETIRED`; `routing_decision.schema.v1.json`'s `←` source marker was kept intact,
  since rule 1's file-count resolution depends on it.

Two `claim_class` values changed as a direct, truthful consequence of mechanism changes,
not as a relaxation: `FR-P2-CONTRACT-VERSIONED` (`tree+text+schema+mapping+execution` →
`tree+text+schema+parse` — the removed leg was the gate's only source of `mapping` and
`execution`) and `FR-P1-SCHEMA-RETENTION` (`tree+text+mapping` → `tree` while 0 files were
retired, then → `tree+text` once the move made the basename search actually run). Both
are reflected in `registry.py` and `folder_refactoring.plan.v6.md`'s per-gate tables, which
`FR-P0-REGISTRY` cross-checks in both directions.

## Left undone

Nothing. All nine steps in the prompt's order of work completed; every constraint held at
every commit (six total: `80ac92a`, `50cac32`, `9420008`, `9510c7b`, `433c10e`,
`270c3fe`).
