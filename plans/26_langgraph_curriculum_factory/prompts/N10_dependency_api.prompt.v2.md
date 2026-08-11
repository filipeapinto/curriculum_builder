# GOAL

Implement `N10_DEPENDENCY_API` after N00 passes. Add the exact Plan 26 direct
dependency inputs and complete hash lock, prove the selected LangGraph 1.2.9 and
SQLite-checkpointer 3.1.0 APIs in isolated Python 3.13, and make lock drift a
repository CI-owned failure rather than a manual convention.

Use LangGraph directly without LangChain chat wrappers. Transitive
`langchain-core` does not authorize LangChain application/model abstractions.
Pin the specified runtime/test stack. Add one deterministic lock-regeneration
check and wire it into the repository's actual CI entry so regeneration that
differs from the committed lock fails CI with the diff.

# TEST

1. Direct pins and complete hash lock reproduce in a clean environment.
2. API tests prove `StateGraph`, reducers, `START`, `END`, conditional edges,
   `Send`, compile/invoke/state/history, and `SqliteSaver` pending-write behavior.
3. SQLite saver works synchronously with the selected Python/package versions.
4. Import audit rejects LangChain wrappers, provider SDKs, and model HTTP clients.
5. Lock regeneration is byte-identical on pass and a controlled pin/hash change
   fails the same CI command with a nonempty drift report.
6. The committed CI configuration invokes that exact lock-drift command; deleting
   the CI step or the test fails a static ownership test.

Write `results/N10_DEPENDENCY_API.result.v1.md` with package hashes, API/lock/CI
commands and exits, clean-environment evidence, and any prerequisite blocker.

# LOOP

Fix only dependency inputs, lock generation, API tests, or the Plan 26 CI lock-
drift step. Never change versions silently or accept an unverified lock. If a
pinned API fails, record the incompatibility and block rather than falling back.

