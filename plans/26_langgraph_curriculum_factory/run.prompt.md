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
2. Adopt verified completed work through the N20 integration join (which is
   topologically after N22/N23):
   `python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py adopt-v2 --through N20_GRAPH_COMPILER`
3. Confirm N30 is the next frontier:
   `python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py status`
4. Preview every scheduler generation before launching it:
   `python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py run --dry-run`
5. Execute one generation:
   `python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py run`

The controller must admit a node only when its Claude command succeeds, its
focused/join/full verification commands return zero, every changed file is inside
the declared write set, its compact receipt validates, and all output hashes match.

# LOOP

Repeat status, dry-run, and run one generation at a time until N90. The controller
launches disjoint ready nodes concurrently in isolated copies of the current dirty
baseline, merges only declared writes, caches verified nodes, and invalidates stale
receipts when inputs or outputs change.

Do not load historical result Markdown into Claude by default. Do not rerun the
complete suite at ordinary nodes. N50 runs the complete unchanged suite; N90 audits
that immutable receipt. Return only `ACTIVATED`, `IMPLEMENTED_NOT_ACTIVATED`, or
`BLOCKED` after N90 evidence validates.
