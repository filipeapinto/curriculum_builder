# Run 27 — LangGraph Curriculum Factory remediation

Status: `SCAFFOLDED_BLOCKED_BY_SPEC_APPROVAL`

Run 27 converts the corrective actions in the Run 26 post-mortem into an
execution package. It does not treat the defective Plan 26 v1 specification or
its `IMPLEMENTED_NOT_ACTIVATED` verdict as implementation authority.

## Entry gate

Implementation may begin only after all of these artifacts exist and agree on
the same SHA-256 digest:

1. `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md`
2. `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec_correction.result.v1.md`
3. witnessed, hash-chain-valid `QA_PASSED` evidence produced by the repository's
   Claude-Codex QA gate
4. `plans/27_langgraph_curriculum_factory_remediation/contracts/spec_approval.v1.yaml`,
   conforming to
   `plans/27_langgraph_curriculum_factory_remediation/schemas/spec_approval.schema.v1.json`
   and recording explicit user approval
   of that exact v2 digest

The approval record is deliberately absent from this scaffold. The request to
prepare Run 27 authorizes the scaffold, not approval of a corrected specification
that does not yet exist.

## Canonical files

- `remediation.plan.v1.md` — authority, scope, graph, ownership, and terminals
- `implementation.graph.v1.yaml` — machine-readable phase graph
- `run.prompt.md` — execution instructions
- `qa_criteria.v1.md` — rejection and final acceptance criteria
- `prompts/` — one GOAL/TEST/LOOP prompt per graph node
- `schemas/node_result.schema.v1.json` — machine-readable node outcome protocol
- `schemas/spec_approval.schema.v1.json` — user-approval binding
- `tools/validate_plan.py` — read-only structural validation

## Validate the scaffold

From the repository root:

```sh
python3 plans/27_langgraph_curriculum_factory_remediation/tools/validate_plan.py
```

Validation proves the graph schema, DAG, prompt/result paths, non-empty
machine-runnable verification, edge/dependency agreement, entry node,
node-specific terminal-result semantics, scoped forbidden-production scan, and
exclusive cross-node write ownership. It does not satisfy the specification or
user-approval gate.

## Execute after approval

Give `run.prompt.md` to the implementation orchestrator from the repository
root. The orchestrator must start at `N00_SPEC_APPROVAL_GATE`, emit a
schema-valid JSON result for each node, and advance only through admitted
receipts. A missing or mismatched gate artifact returns
`BLOCKED_SPEC_NOT_APPROVED` without modifying runtime code.

Run 26 files under `plans/26_langgraph_curriculum_factory/` remain immutable
historical evidence except for the separately authorized v2 specification,
specification-correction result, and QA-gate-owned evidence created by the
pre-Run-27 correction workflow.
