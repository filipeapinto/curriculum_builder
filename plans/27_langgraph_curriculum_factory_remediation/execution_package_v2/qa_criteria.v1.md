# Run 27 execution package v2 — QA criteria v1

This package is the corrected recovery of the v1 attempt that reached
`BLOCKED` at `N20_PROVIDER_TRANSPORT`
(`plans/27_langgraph_curriculum_factory_remediation/results/N20_PROVIDER_TRANSPORT.result.v1.json`,
findings N20-F01, N20-F02, N20-F03, N20-F04, N20-F06) and of the first,
failed execution-package correction
(`plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml`,
preserved immutable together with its QA session and `PKG-QA-001` finding).
Every criterion in
`plans/27_langgraph_curriculum_factory_remediation/qa_criteria.v1.md`
(the v1 package's own criteria, unmodified and still authoritative for the
substance of what a correct Run 27 implementation must prove) applies to this
package unchanged. This document adds only the criteria specific to the two
structural corrections this package makes.

## Immediate rejection (in addition to the v1 list)

- A node-scoped forbidden-reference verification command that omits an
  explicit `--graph` binding to this package's own
  `implementation.graph.v1.yaml` (the exact defect independent QA found in
  the first correction attempt, `PKG-QA-001`).
- Any command in this package's graph that loads
  `plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml`
  (the parent v1 package's own graph) instead of this package's graph.
- `runtime/langgraph_factory/egress.py` or
  `tests/runtime/test_plan26_egress.py` owned by any node other than
  `N20_PROVIDER_TRANSPORT`, or `N30_PREFLIGHT_EGRESS` not declaring
  `egress.py` as a read-only input.
- Any edit to `implementation.graph.v1.yaml` (the parent v1 package's graph),
  `implementation.graph.v2.yaml` (the failed correction), their QA sessions,
  or any v1 N00–N20 result or evidence file.
- A node-scoped scan reporting a violation the corresponding whole-tree scope
  would not have reported, or omitting one the whole-tree scope would have
  reported for a file inside the node's own write set.

## Required proof (in addition to the v1 list)

1. This package's own graph validates and reports `version: 2`.
2. `source_spec` binds to the QA-passed specification v4 artifact
   (`plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md`,
   sha256 `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`),
   not v1 or v2.
3. Every node's result/evidence write path lives under this package's own
   `execution_package_v2/results/` root, never the parent v1 package's
   `results/` root or the failed correction's `results/v2/` root.
4. `N20_PROVIDER_TRANSPORT`'s node-scoped scan includes its newly owned
   egress implementation and test; `N30_PREFLIGHT_EGRESS`'s node-scoped scan
   excludes them.
5. `N60_ADVERSARIAL_REGRESSION` alone runs the scanner in complete-tree mode;
   every other scanning node runs it in node-scoped mode bound explicitly to
   this package's graph.
6. No package-v2 write path overlaps another node's write path.
7. No file under `runtime/`, `policy/`, `schemas/routes.schema.v1.json`, or
   `schemas/model_registry.schema.v1.json` was created or changed while
   authoring this package.
