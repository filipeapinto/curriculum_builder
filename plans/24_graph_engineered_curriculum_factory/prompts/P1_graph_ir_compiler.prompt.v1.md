# P1 — Build the effective factory graph compiler

## GOAL

- `prompt_id`: `plan24.P1.graph_ir_compiler.v1`
- `role`: `graph_compiler_implementer`
- `objective`: Implement a typed IR and deterministic compiler that expands one
  supplied curriculum manifest into one closed immutable production graph.
- `non_goals`: Do not create a prompt-evolution system; execute model calls;
  hardcode Arduino units; permit runtime authority to live only in prose.
- `authorized_inputs`: P0 frozen authority, active curriculum/engine contracts,
  Plan 24 graph model, existing runtime and tests.
- `output_contract`: IR schema/types, compiler, effective graph artifact and
  digest, static validator, positive fixtures, adversarial fixtures, tests, and
  P1 receipt.
- `completion_condition`: Arduino and unrelated manifests compile into closed
  graphs; every required invalid graph is rejected before execution.

## TEST

1. Manifest units, order, dependencies, domain contracts, checks, and outputs
   expand without subject-specific engine constants.
2. Every node read/write, port, edge, guard, join, context projection, loop,
   counter, artifact, and terminal validates.
3. Single-writer, output-collision, reachability, guard-exclusivity,
   correlation, check-denominator, and terminal-closure tests pass.
4. Mutation tests reject dangling nodes, type mismatch, undeclared context,
   cross-unit joins, duplicate writers, unbounded repairs, missing failures, and
   implicit success terminals.
5. Recompiling identical frozen inputs yields byte-identical canonical IR and
   digest; meaningful manifest change changes the digest.

## LOOP

Compiler failures identify the violated invariant and exact source. Repair only
the compiler, schema, or reconciled authority that owns it, then rerun all
compiler and mutation tests. Do not soften an invariant to admit a bad graph.
Advance only with a complete P1 receipt.
