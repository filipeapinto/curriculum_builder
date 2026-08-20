# Plan graph contract

`plan-graph.json` is a UTF-8 JSON object with these required top-level members:

```json
{
  "schema_version": "1.0",
  "graph_id": "PG-...",
  "plan": {"path": "...", "version": "...", "digest": "sha256:...", "approval": "APPROVED", "implementation_authority": "GRANTED"},
  "budgets": {},
  "protected_paths": [],
  "nodes": [],
  "edges": [],
  "traceability": []
}
```

## Nodes

Every node has `id`, `kind`, `title`, `depends_on`, `executor`, `inputs`, `outputs`, `acceptance`, `budget`, `retry`, and `terminal_routes`.

Allowed `kind` values are `goal`, `prompt_test`, `implement`, `result_test`, `repair`, `tool`, `human_gate`, `challenge`, and `verify`. Model executors also require `model`, `effort`, `routing_basis`, and `prompt_path`. Tool executors require a reproducible `command_or_check`. Human gates require `authority`, `decision`, and `evidence_required`.

`retry` contains `max_attempts` and `repair_node`; no cycle is valid unless it contains a `repair` node and a finite `max_attempts`. `terminal_routes` explicitly names outcomes for `pass`, `fail`, and `blocked`.

## Edges and traceability

Each edge has `from`, `to`, and `condition`. Allowed conditions are `pass`, `fail`, `blocked`, `approved`, and `always`. Node IDs must exist. Dependency links and edges must agree.

Each traceability record contains one `requirement_id`, its `source_locator`, and nonempty `node_ids` and `test_node_ids`. Every plan requirement and acceptance criterion must occur exactly once; one record may map to several nodes.

## Required invariants

- IDs are unique and paths are relative to the graph file or repository root, stated consistently.
- Every `implement` node is preceded by a passing `prompt_test` for the same goal.
- Every executable goal has a downstream `result_test`.
- Prompts exist before execution and their digests are frozen in the execution log.
- Model and effort match the plan or have an approved deviation ID.
- Human gates cannot be auto-completed.
- All loops are bounded; budget and retry limits cannot exceed the plan.
- Failed or blocked mandatory nodes cannot lead to overall success.
- Challenge and verification remain distinct from implementation when the plan requires independence.
- Actual results and provenance belong in the execution log, not as rewrites of the prospective graph.
