---
name: plan-graph-create
description: Compile an approved implementation or research plan into a dependency-aware graph of goal, prompt-test, implementation, and verification nodes; route each node to an appropriate model and effort; validate prompts before executing the graph. Use when Codex must implement a plan through an auditable, bounded prompt graph. Do not use to approve plans or bypass their gates.
---

# Plan Graph Create

Turn an approved plan into a reviewable execution graph, test the graph's prompts, then execute and verify the plan. The plan remains authoritative: the graph may operationalize it but must not weaken, invent, or silently repair its scope, allocations, budgets, gates, authority boundaries, stopping rules, or acceptance criteria.

## Required input and start gate

1. Read the complete plan and every artifact it declares normative before creating nodes.
2. Confirm the exact plan version is explicitly approved and separately authorized for implementation. If either state is absent, create no execution graph and report the failed gate.
3. Inventory protected user changes and plan-declared read-only artifacts.
4. Extract requirements, dependencies, outputs, tests, allocations, budgets, retries, stops, human decisions, and permitted parallelism into stable IDs.
5. Read [references/graph-contract.md](references/graph-contract.md) before emitting or executing a graph.

## Compile the graph

Create the prompt files first, followed by `plan-graph.json`. Use the plan's artifact directory when specified; otherwise use `<plan-directory>/graph/<plan-stem>/`.

Every executable objective becomes a `goal` node. Each goal must have:

- one or more `prompt_test` predecessors that test its prompt without performing the implementation;
- an `implement` node that may run only after those prompt tests pass;
- one or more `result_test` successors tied to plan acceptance criteria;
- a bounded `repair` edge from a failed test when the plan permits retry;
- an explicit terminal route for success, failure, blocked state, or required human decision.

Keep deterministic discovery, hashing, syntax checks, schema validation, and fixture execution as `tool` nodes rather than model prompts. Represent human authority as `human_gate` nodes; never infer a pass.

Each model node references one standalone prompt file containing the node ID, objective, exact inputs, allowed tools and writes, protected paths, required output contract, acceptance oracle, budget, retry limit, provenance fields, and stop conditions. Do not embed large prompts inside graph JSON.

## Route models and effort

Use the plan's explicit executor, model, family-diversity constraint, and effort exactly. Record substitutions as deviations and stop for approval when the plan requires it.

Only if allocation is genuinely absent, choose the least costly capable route:

- deterministic tool: measurable transformations and checks;
- `gpt-5.6-luna`, medium: bounded, reversible normalization;
- `gpt-5.6-terra`, high: evidence mapping, classification, and ordinary implementation;
- `gpt-5.6-sol`, xhigh: architecture, cross-artifact integration, high-consequence synthesis, and difficult repair;
- a different available model family, xhigh: independent challenge when independence matters.

Record why each fallback is adequate. Never route approval, acceptance, scope expansion, or implementation authority to a model.

## Test prompts before implementation

For each model prompt, run its `prompt_test` using fixtures, dry-run inputs, or an isolated temporary workspace. A prompt passes only when its output is contract-shaped, grounded in declared inputs, scoped to permitted writes, testable by the named oracle, and compliant with its stop conditions. A reviewer must not receive the intended answer or hidden defense.

On failure, record the failure class and revise the prompt materially. Respect the plan's retry ceiling; if absent, allow one revision. A failed final attempt blocks its goal. Do not use implementation output as evidence that an untested prompt passed.

Run `scripts/validate_graph.py <plan-graph.json>` after compilation and after every structural edit. Validation success is necessary, not sufficient.

## Execute and test the plan

1. Freeze prompt and graph digests and initialize the plan-required execution log and budget ledger.
2. Execute ready nodes in dependency order, using parallelism only where the graph and plan allow it.
3. Before each node, recheck gates, remaining budget, protected inputs, and predecessor results.
4. Record actual model/tool version, effort, inputs, outputs, timing, usage, result, retry, and deviation—not merely planned values.
5. Run `result_test` nodes immediately after their implementation node. Use deterministic acceptance oracles whenever possible.
6. Follow bounded repair edges only for diagnosed, repairable failures. Never create an unplanned retry loop.
7. After all goals pass, run plan-wide integration tests, independent challenge when required, accepted corrections, and final verification in the plan's order.
8. Stop on any hard budget, unresolved high-severity challenge, failed mandatory check, protected-file mutation, missing authority, or material plan change.

## Deliverables

Deliver the prompt directory, `plan-graph.json`, validation receipt, prompt-test records, execution log, budget ledger, node outputs, test receipts, deviations, and final traceability from every plan requirement and acceptance criterion to graph nodes and results. Report execution, verification, and human-acceptance states separately. Do not equate completed nodes with plan acceptance.
