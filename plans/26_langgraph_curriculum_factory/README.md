# Plan 26 implementation prompt graph

This folder contains the implementation graph for
`spec/langgraph_curriculum_factory.spec.v1.md`.

The graph is a prompt-execution graph, not a replacement for the specified
LangGraph production runtime. Its nodes implement the specification in bounded,
dependency-aware units. Independent nodes may run concurrently; joins require
all declared predecessors; failures return to the owning node through explicit
rework edges.

Files:

- `implementation.graph.v2.yaml` — active node, edge, join, ownership, and terminal manifest.
- `deprecated/implementation.graph.v1.yaml` — superseded graph retained for audit.
- `prompts/*.prompt.v1.md` — one implementation prompt per graph node.
- `run.prompt.md` — validates and runs the prompt graph.
- `qa_criteria.v2.md` — active graph-wide implementation and product-proof criteria.
- `results/<node_id>.result.v1.md` — generated completion evidence.

The implementation uses the exact LangGraph and SQLite-checkpointer contract in
the specification. It must not use LangChain chat-model wrappers, provider SDKs,
or direct model HTTP APIs. Model work remains through `codex exec` and `gemini`.

Run `run.prompt.md` to execute the graph.

Version 2 closes the v1 sequencing gaps by requiring real N22/N23 callables
before N20 compilation and assigning D98 solely to N22 before N31/N32 execute.
It also assigns CI lock-drift enforcement to N10/N50 and runtime egress policing
to N13/N50. Superseded affected prompts are retained under `prompts/deprecated/`.
