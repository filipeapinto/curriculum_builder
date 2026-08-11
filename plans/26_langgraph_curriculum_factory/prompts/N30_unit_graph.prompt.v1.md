# GOAL

Implement `N30_UNIT_GRAPH` after N20/N21/N22/N23. Integrate and execute the
compiled graph from bootstrap through D16 unit evidence reduction, including
source and visual dynamic fan-outs, actual rendering, every-page inspection,
and M05 independent review.

Exercise D00/D00R/D01–D16, D90–D92, D96/D98 and M01–M05 through LangGraph
edges—not direct Python orchestration. Exact denominators are created before
dispatch. Deterministic and model visual subsets use sequential map/reduce
supersteps around D12 and handle empty subsets.

This node does not claim product success; clean D16 evidence is a handoff to N31.

# TEST

1. Fresh bootstrap executes D01 once; resume uses D00R/D04 and validated state import.
2. `one` mode computes complete prerequisite closure in manifest order.
3. Source discovery/retrieval/interpretation join rejects missing/extra/duplicate/stale/cross-unit members.
4. Domain/content heads advance only after code-owned admission.
5. Visual denominator permutations produce identical admitted heads; empty subsets work.
6. Actual PDF/assets and positive contiguous page inventory are required.
7. D15 packet contains exact PDF and every page once; M05 result matches it.
8. D16 rejects any absent/failed/stale/`NOT_RUN` denominator member.
9. Interrupt/hard crash at every node/map/barrier boundary resumes without repeated valid calls.
10. No capability, intermediate artifact, review, or D16 pass emits success.

Write `results/N30_UNIT_GRAPH.result.v1.md` with LangGraph trace, fan-out
denominators, artifact tree, crash matrix, commands, and hashes.

# LOOP

Patch one node registration, guard, projection, barrier, adapter, or fixture;
then rerun bootstrap, exact-join, denominator, and crash invariants. Stop if the
unit path bypasses LangGraph, admits a partial join, or repeats committed work.

