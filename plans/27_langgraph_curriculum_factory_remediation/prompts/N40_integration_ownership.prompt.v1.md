# GOAL

Prove every retained deterministic/model node is reachable through the one
production-compiled LangGraph and give every body, registration seam, call site,
shared output, and integration test one deterministic owner.

This node prevents recurrence of PM-11 through PM-14 and PM-18.

# TEST

1. Derive the normative topology from approved v2, not from current hardcoded
   test expectations or private builder functions.
2. Produce a machine-readable ownership matrix covering every D-node, M01–M08,
   registration function, production call site, interface, shared output, and
   integration test. Reject gaps and ambiguous concurrent ownership.
3. Compile through the exact production entry point used by the CLI and prove
   reachability of the complete unit path, D16–D23 repair/acceptance cycle,
   D24–D32 workbook/release path, and every legal terminal.
4. Prove forbidden bypass edges, unreachable registered nodes, undeclared
   registered nodes, missing joins, and stale topology expectations fail.
5. Execute one deterministic/fake-transport graph walk through unit acceptance
   and one through workbook completion. This is integration proof, not live
   product proof.
6. Ensure migration nodes own their interface and direct retirement/
   compatibility tests atomically.
7. Add an ownership-closure check that the scheduler can run before each future
   node attempt.
8. Run topology, unit graph, repair/acceptance, workbook, and CLI integration
   tests against the production compile point.
9. Emit the ownership matrix, compiled topology evidence, exact test commands,
   and schema-valid result.

The integration owner may edit only the six graph/repair/workbook modules, four
integration tests, and one ownership contract declared in the manifest. It must
not take directory-level ownership of provider, preflight, evidence, controller,
or unrelated runtime tests. Remove every retired-provider reference from its
owned active topology test and keep the zero-occurrence test scan green.

# LOOP

When topology and tests disagree, resolve against approved v2. Do not change the
spec or weaken a normative edge merely to preserve a stale test. Repair body
registration, call site, and affected integration expectation as one sequenced
change, then rerun the entire production-reachability slice.
