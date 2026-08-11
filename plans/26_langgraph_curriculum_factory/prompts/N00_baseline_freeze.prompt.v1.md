# GOAL

Implement graph node `N00_BASELINE_FREEZE`. Read the complete Plan 26 spec,
implementation graph, QA criteria, current Plan 25 runtime, tests, and dirty
worktree. Create the implementation contract and traceability matrix before any
production edits.

Map every Plan 26 section, state field, reducer, D00–D98 node, M01–M08 job,
edge/guard, fan-out denominator, repair rule, terminal, CLI behavior, migration
rule, and adversarial test to one implementation-graph owner. Freeze shared
names, paths, schemas, result contract, graph/package digest algorithm, and the
baseline commit/test/dirty-path record. Preserve unrelated changes.

# TEST

1. Every normative Plan 26 requirement has exactly one owning node.
2. D00–D98 and exactly M01–M08 have complete dispositions.
3. Every shared artifact has one writer; graph-parallel write sets are disjoint.
4. The result-record schema requires status, inputs, outputs, hashes, commands,
   exit codes, tests, findings, and invalidated descendants.
5. Baseline tests and dirty paths are recorded without modification.
6. No framework substitution or weakened product requirement is introduced.

Write contracts under `plans/26_langgraph_curriculum_factory/contracts/` and
`results/N00_BASELINE_FREEZE.result.v1.md` with commands and hashes.

# LOOP

Fix only contracts, traceability, schemas, or baseline evidence. Rerun all six
tests after change. Stop if ownership is ambiguous, the spec is contradictory
without an explicit resolution, or user work would be overwritten. Two repeated
same-cause failures mark the node `BLOCKED`.

