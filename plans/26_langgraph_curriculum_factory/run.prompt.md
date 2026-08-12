# GOAL

Execute `implementation.graph.v3.yaml` with Claude Sonnet through the deterministic
controller at `prompt_graph_controller.py`. This prompt runs the implementation
prompt graph; it does not replace the production LangGraph curriculum factory.

Preserve the interrupted v2 results as audit evidence. Adopt a v2 `PASSED` node
only after its v3 focused verification succeeds. Never adopt the blocked N30 result.

# TEST

From the repository root:

1. Validate graph schema and invariants:
   `python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py validate`
2. Confirm completed receipts remain admitted and identify the current frontier:
   `python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py status`
3. Hash-anchor historical receipts and logs once before the first resumed run:
   `python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py audit-anchor`
4. Prove the nested Sonnet permission/interpreter path:
   `python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py preflight`
5. Preview every scheduler generation before launching it:
   `python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py run --dry-run`
6. Execute one generation:
   `python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py run`

The controller must admit a node only when its Claude command succeeds, its
focused/join/full verification commands return zero, every changed file is inside
the declared write set, its compact receipt validates, and all output hashes match.

# LOOP

Repeat status, dry-run, and run one generation at a time until N90. The controller
launches disjoint ready nodes concurrently in isolated copies of the current dirty
baseline, merges only declared writes, caches verified nodes, and invalidates stale
receipts when inputs or outputs change.

Every attempt is retained under `.plan26-run/plan26/attempts`; never discard a failed
workspace. Inspect branches with:
`python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py attempts`.
Continue failed or interrupted work on a new immutable child branch with:
`python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py run --node NODE_ID --resume-attempt ATTEMPT_ID`.
The controller rejects continuation if predecessor receipt hashes changed.

Alter prompts only through `create-patch`, previewing the affected nodes with
`--dry-run`. Patches take effect at the next attempt, never inside a running
Claude call. Revoke a patch by adding a `revoke-patch` record; never edit history.

Lifecycle events append to `results/v3/audit/events.v1.jsonl`. Generate a
read-only postmortem summary at any time with:
`python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py postmortem`.

Do not load historical result Markdown into Claude by default. Do not rerun the
complete suite at ordinary nodes. N50 runs the complete unchanged suite; N90 audits
that immutable receipt. Return only `ACTIVATED`, `IMPLEMENTED_NOT_ACTIVATED`, or
`BLOCKED` after N90 evidence validates.
