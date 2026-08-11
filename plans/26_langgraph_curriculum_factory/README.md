# Plan 26 implementation prompt graph

This folder contains the implementation graph for
`spec/langgraph_curriculum_factory.spec.v1.md`.

The graph is a prompt-execution graph, not a replacement for the specified
LangGraph production runtime. Its nodes implement the specification in bounded,
dependency-aware units. Independent nodes may run concurrently; joins require
all declared predecessors; failures return to the owning node through explicit
rework edges.

Files:

- `implementation.graph.v1.yaml` — node, edge, join, ownership, and terminal manifest.
- `prompts/*.prompt.v1.md` — one implementation prompt per graph node.
- `run.prompt.md` — validates and runs the prompt graph.
- `qa_criteria.v1.md` — graph-wide implementation and product-proof criteria.
- `results/<node_id>.result.v1.md` — generated completion evidence.

The implementation uses the exact LangGraph and SQLite-checkpointer contract in
the specification. It must not use LangChain chat-model wrappers, provider SDKs,
or direct model HTTP APIs. Model work remains through `codex exec` and `gemini`.

Run `run.prompt.md` to execute the graph.

