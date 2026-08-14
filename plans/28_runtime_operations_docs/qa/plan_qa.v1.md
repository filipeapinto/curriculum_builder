# Runtime Operations Documentation Plan v1 — Focused QA

## Verdict

**APPROVED — 0 Critical, 0 High.** Round 1 found 1 High finding, remediated
in place (see below); round 2 independently re-verified the revised plan
against the live repository and found nothing further.

### Round 2 (final)

Re-verified, against the live repository, that: `execution_package_v2/`
contains `implementation.graph.v5.yaml`, `.v6.yaml`, `.v7.yaml` directly in
the directory (plus `deprecated/` holding v1–v6), so the plan's "highest
`implementation.graph.v*.yaml` not under `deprecated/`" instruction
unambiguously selects v7 today; `implementation.graph.v7.yaml`'s own
`result_pattern` field resolves exactly to the path the plan expects; N90's
node config, `node_result.schema.v1.json`'s `terminal_recommendation` enum,
and `run27_controller.py`'s terminal handling all match the plan's citations
verbatim; and today's absence of `results/v7/N90_...json` means step 0
correctly stops right now, since Plan 27 has not concluded. Scope stays
confined to `docs/` and `readme.md`; all `runtime/`/`policy/`/schema
references in the plan are read-only sourcing citations, not writes.

Non-blocking observation: `implementation.graph.v5.yaml` and `.v6.yaml`
currently exist both directly in `execution_package_v2/` and duplicated under
`deprecated/` (byte-identical copies, not moves) — the plan's framing text
"v1–v6 moved to deprecated/" is technically imprecise for v5/v6 today. This
doesn't affect step 0's mechanism (the glob still ignores `deprecated/` and
correctly picks v7) and is below the High threshold; not a gating finding.

## Findings

### 1. High — step-0 gate has no defense against a superseded graph version

**Evidence.** `execution_package_v2/` already contains graph versions v1
through v7, with v1–v6 moved to `deprecated/`; each version exists because a
real, evidenced defect was found in its predecessor (v6→v7's own header
documents v6's `results/` path-collision defect). Each correction moved
`result_pattern` to a new version-specific directory. There is no
`CURRENT`/latest pointer file; `run27_controller.py` is invoked with an
explicit `--graph <path>` argument, and nothing marks an older version's
results as stale once a newer graph version exists — old results simply sit
unreferenced at their old path.

**Impact.** Plan 28's step 0 hardcodes `results/v7/N90_....json`. If Plan 27
reaches `PASSED`/`ACTIVATED` under v7, and a defect is later found (following
this package's own repeated pattern) requiring a v8 correction, the v7 N90
result file remains on disk unchanged and still reads `PASSED`/`ACTIVATED`.
Plan 28's implementer, run at that point, would pass the literal step-0 check
against the stale v7 file and proceed to write documentation describing a
system state Plan 27 itself has since superseded. The plan's only staleness
guard ("re-read the N90 result before the final write") only re-checks the
*same* v7 path — it does not check whether v7 is still the current graph
version.

**Minimal required remediation.** Add a step-0 sub-check: before trusting the
v7 result, confirm no `implementation.graph.v8.yaml` (or higher-numbered)
file exists under `execution_package_v2/`. If one does, stop and re-derive
the correct `results/vN/` path from that newer graph's own `result_pattern`
field instead of trusting the v7 result.
