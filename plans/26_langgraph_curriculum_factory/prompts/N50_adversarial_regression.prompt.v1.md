# GOAL

Implement `N50_ADVERSARIAL_REGRESSION` after N40. Encode and run the complete
Plan 26 section 17 test matrix, QA rejection criteria, API/dependency audits,
full runtime suite, gates, rendering/product integrations, and migration checks.

Fake-transport tests prove orchestration only and must use unmistakable
non-product roots/terminals. Inject SIGINT and hard process death around every
node, fan-out member, model process, admission, checkpoint, acceptance, and
terminal boundary. Preserve P0 baseline failures separately.

# TEST

1. Every section 17.2 adversarial row has a named executable test and passes.
2. Reducer/topology/transport/persistence/unit/repair/workbook/CLI suites pass.
3. Crash denominator is independently enumerated and completely covered.
4. Completion-order permutations do not change state, hashes, or acceptance.
5. Forbidden import/dependency and second-production-path scans pass.
6. Full `tests/runtime` and applicable gate suites have no new/worsened failure.
7. Fake outputs cannot be copied or promoted into a product root.
8. Test reports contain commands, exits, environment/package hashes, and evidence.

Write `results/N50_ADVERSARIAL_REGRESSION.result.v1.md` with the row-to-test
matrix, complete results, baseline comparison, commands, and hashes.

# LOOP

Route each failure to its exact implementation-graph owner using the manifest's
rework map; do not patch a non-owner here except test enumeration/fixtures owned
by N50. Invalidate and rerun affected descendants. Never weaken, delete, or
waive a negative control. Two same-cause rework returns block the graph.

