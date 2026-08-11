# GOAL

Implement `N10_DEPENDENCY_API` after N00 passes. Add exact Plan 26 dependency
inputs and hash lock, then prove the selected official LangGraph 1.2.9 and
SQLite-checkpointer 3.1.0 APIs in an isolated Python 3.13 environment.

Use LangGraph directly without LangChain chat wrappers. The transitive
`langchain-core` package required by LangGraph is not permission to import
LangChain application/model abstractions. Pin the existing runtime/test stack
as specified. Do not alter production behavior in this node.

# TEST

1. Direct pins and complete hash lock reproduce from a clean environment.
2. API-contract tests prove `StateGraph`, typed reducers, `START`, `END`,
   conditional edges, `Send`, compile/invoke/state/history, and `SqliteSaver`
   checkpoint tuple/pending-write behavior used by the spec.
3. SQLite saver works synchronously with the selected Python/package versions.
4. Import audit rejects LangChain wrappers, provider SDKs, and model HTTP clients.
5. Lock regeneration is byte-identical.

Write `results/N10_DEPENDENCY_API.result.v1.md` with wheel/package hashes, API
test commands/exits, and any prerequisite blocker.

# LOOP

Fix only dependency manifests, lock generation, or API-contract tests. Never
select a different version silently. If the pinned APIs fail, record the exact
incompatibility and block rather than falling back. Two same-cause failures stop.
