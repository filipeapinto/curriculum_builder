# GOAL

Execute `implementation.graph.v1.yaml` as the Run 27 remediation of the defects
in `plans/26_langgraph_curriculum_factory/post_morten/postmortem.v2.md`.

Start at `N00_SPEC_APPROVAL_GATE`. Do not modify runtime, tests, policy, or
historical Plan 26 evidence unless N00 proves a corrected v2 specification,
witnessed independent `QA_PASSED`, and explicit user approval all bind the same
bytes. The absence of those artifacts is the expected truthful terminal
`BLOCKED_SPEC_NOT_APPROVED`.

After admission, implement only what the corrected specification authorizes.
Preserve reusable LangGraph mechanics and repair the provider, harness,
preflight, topology, evidence, and audit defects without weakening product QA.

# TEST

Before execution:

1. Run
   `python3 plans/27_langgraph_curriculum_factory_remediation/tools/validate_plan.py`.
2. Inventory the worktree and preserve unrelated or pre-existing changes.
3. Execute the current node's prompt and all listed verification commands.
4. Validate its JSON result against `schemas/node_result.schema.v1.json`.
5. Admit a receipt only when every command exits zero, every output is inside
   the declared write set, and all recorded hashes match current bytes.

N60 must run the complete unchanged deterministic/integration/adversarial suite.
N70 and N80 must use the actual production CLI and graph; simulations, fake
transports, probes, or hand-authored intermediate curriculum files are not live
proof. N90 independently recomputes the terminal from raw evidence.

# LOOP

For each node in graph order:

1. Freeze its input and predecessor receipt digests.
2. Execute the node prompt's smallest complete change.
3. Run its positive, negative, and regression tests.
4. On failure, name the finding, owner, allowed write scope, invalidation set,
   and falsifiable repair target.
5. Create a new attempt; never overwrite attempt evidence or an admitted result.
6. If an ancestor changes, invalidate and rerun every descendant before final
   audit.
7. Advance only from a schema-valid `PASSED` or explicitly permitted
   `NOT_AVAILABLE` result. `NOT_AVAILABLE` is permitted only for N70/N80 and
   prevents `ACTIVATED`.

The scheduler consumes only JSON outcomes. Do not infer status from prose or
Markdown. Stop after N90 returns exactly one terminal defined by the plan.
