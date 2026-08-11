# GOAL

Compile and execute the implementation prompt graph at
`plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml` to
implement `spec/langgraph_curriculum_factory.spec.v1.md` exactly.

This is the prompt-graph runner. It does not implement phase work itself and it
does not replace the specified production LangGraph runtime. Read the complete
source spec, graph manifest/schema, QA criteria, and all node prompts before
activating the entry node.

Validate schema plus graph invariants: unique/known nodes, prompt/result paths,
one entry, reachable final audit/terminals, dependencies matching edges, valid
`all_of` joins, acyclic forward dependencies, total rework ownership, and
disjoint write sets for concurrently ready nodes.

# TEST

For each scheduler generation:

1. Recompute node status from result records and declared artifact hashes; file
   presence alone never means pass.
2. A node is `READY` only when every `depends_on` predecessor has an admissible
   passing result and every incoming guard/join is satisfied.
3. Select all ready nodes with disjoint `writes` for concurrent execution;
   serialize conflicts in stable node-ID order.
4. Execute each selected node's prompt verbatim, including its TEST and LOOP.
5. Validate the result record, commands, exit codes, tests, outputs, hashes, and
   write-set containment before admitting `PASSED` or `NOT_AVAILABLE` where allowed.
6. Append a scheduler receipt with graph digest, generation, ready/selected sets,
   predecessor/result hashes, edge decisions, invalidations, and next frontier.
7. On final-audit finding, use exactly one declared `rework_edges` owner,
   invalidate that node and all descendants, and resume normal scheduling.

After N90, independently validate its evidence and return exactly its verdict:
`ACTIVATED`, `IMPLEMENTED_NOT_ACTIVATED`, or `BLOCKED`.

# LOOP

Traverse the manifest, not filename order. Begin at `N00_BASELINE_FREEZE`; after
it passes, execute the N10/N11/N12/N13 fan-out concurrently where safe; honor
every later `all_of` join and declared dependency.

Never invent an edge, skip a predecessor, execute an unready node, weaken a
test, mutate unrelated dirty work, or fall back to a sequential implementation
controller. A node's own LOOP runs before its failure is propagated. A final-
audit finding may traverse the same rework key/root-cause pair twice; the third
occurrence reaches `BLOCKED`.

Stop at `BLOCKED` when graph validation fails, no legal frontier exists, a node
exhausts its loop, required authority is absent, or implementation would violate
the source spec. Missing external prerequisites for N60 yield
`IMPLEMENTED_NOT_ACTIVATED` only when all implementation/adversarial nodes pass.
