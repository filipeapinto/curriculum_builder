# Plan 26 implementation prompt graph

This folder contains the implementation graph for
`spec/langgraph_curriculum_factory.spec.v1.md`.

The graph is a prompt-execution graph, not a replacement for the specified
LangGraph production runtime. Its nodes implement the specification in bounded,
dependency-aware units. Independent nodes may run concurrently; joins require
all declared predecessors; failures return to the owning node through explicit
rework edges.

Files:

- `implementation.graph.v3.yaml` — active node, edge, join, ownership, test-lane, and execution manifest.
- `deprecated/implementation.graph.v1.yaml` and `deprecated/implementation.graph.v2.yaml` — superseded graphs retained for audit.
- `prompts/*.prompt.vN.md` — one active implementation prompt per graph node; superseded versions are under `prompts/deprecated/`.
- `run.prompt.md` — validates and runs the prompt graph through Claude Sonnet.
- `prompt_graph_controller.py` — deterministic scheduler, cache, isolated-workspace launcher, verifier, and compact-receipt writer.
- `qa_criteria.v3.md` — active graph-wide implementation and product-proof criteria.
- `results/<node_id>.result.v1.md` — generated completion evidence.
- `results/v3/*.receipt.v1.json` — compact authoritative scheduler receipts; raw Markdown remains audit-only.

The implementation uses the exact LangGraph and SQLite-checkpointer contract in
the specification. It must not use LangChain chat-model wrappers, provider SDKs,
or direct model HTTP APIs. Model work remains through `codex exec` and `gemini`.

Run the commands in `run.prompt.md` to execute the graph. The controller uses
Claude Sonnet for implementation work and Python only for mechanical scheduling,
hashing, isolation, verification, and caching. The production system remains the
specified LangGraph runtime.

Version 2 closes the v1 sequencing gaps by requiring real N22/N23 callables
before N20 compilation and assigning D98 solely to N22 before N31/N32 execute.
It also assigns CI lock-drift enforcement to N10/N50 and runtime egress policing
to N13/N50. Superseded affected prompts are retained under `prompts/deprecated/`.

Version 3 preserves that topology while replacing LLM-administered scheduling
with deterministic execution. It adopts v2 passes only after focused verification,
isolates concurrent writers, caches by content, runs integration tests at joins,
and reserves the unchanged complete suite for N50 plus final receipt audit at N90.
