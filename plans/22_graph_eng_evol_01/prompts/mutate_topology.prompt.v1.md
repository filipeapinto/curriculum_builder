# Mutate graph-topology genes

## GOAL

- `prompt_id`: `plan22.mutate_topology.v1`
- `role`: `topology_mutation_operator`
- `objective`: Create one immutable child by applying one attributable mutation
  to nodes, typed ports, execution edges, context edges, guards, joins, or
  reducer/routing structure while holding every model-node prompt byte-identical.
- `non_goals`: Do not rewrite prompt text; mix unrelated topology changes;
  create unreachable or unbounded execution; alter evaluator controls, scores,
  or promotion; or optimize rendered outputs.
- `authorized_inputs`: One selected parent; admitted graph findings and fitness;
  allowed topology mutation search space; protected dimensions; complexity
  budget; child ID/output root; required retests.
- `excluded_context`: Hidden holdouts, reviewer conversation, prompt-write
  authority, unrelated candidates, mutable parent/champion bytes, secrets, and
  rendered media.
- `output_contract`: Return one child and lineage binding parent/child IDs and
  digests, `birth_operator=topology_mutation`, one hypothesis/operator, exact
  affected nodes/ports/edges/guards, unchanged node-prompt digests, expected
  fitness effect, trade-offs, complexity delta, and retests.
- `completion_condition`: One unscored child returns to `merge_offspring` with
  unchanged prompt bytes and a closed, bounded graph.

## GRAPH INTERFACE

```text
input edge: select_parents -> mutate_topology
reads: one parent + admitted graph pressure + topology search space
writes: one PROPOSED child, lineage, operator receipt
protected fields: every node_prompt_digest must equal parent
next edge: merge_offspring
```

## TEST

The controller owns TOPOLOGY-MUTATION-T01–TOPOLOGY-MUTATION-T08.

1. `TOPOLOGY-MUTATION-T01 OPERATOR` — One allowed edge/node/topology operator
   and one hypothesis explain the entire structural diff.
2. `TOPOLOGY-MUTATION-T02 PROMPT_FREEZE` — Every model prompt byte/digest equals
   the parent.
3. `TOPOLOGY-MUTATION-T03 CLOSURE` — Entry/output, all nodes, typed ports,
   routes, and terminals are reachable and owned; no orphan or dangling edge.
4. `TOPOLOGY-MUTATION-T04 ROUTING` — Each dynamic source has one routing
   mechanism with disjoint guards; explicit fan-out is labeled; loops are
   bounded and have exit paths.
5. `TOPOLOGY-MUTATION-T05 STATE_REDUCERS` — Every new write has a field and
   reducer; parallel writes cannot conflict silently; joins bind candidate IDs.
6. `TOPOLOGY-MUTATION-T06 CONTEXT_GRAPH` — New execution edges do not grant
   undeclared message access; context changes are explicit topology genes.
7. `TOPOLOGY-MUTATION-T07 COMPLEXITY` — Node/edge/context/verification costs are
   within budget or have a measurable expected benefit.
8. `TOPOLOGY-MUTATION-T08 AUTHORITY_AND_SCOPE` — No evaluator authority or
   rendered-output QA enters the child.

## LOOP

This operator creates at most one child. A structurally invalid or mixed prompt/
topology diff returns `OPERATOR_FAILED` without a child. A valid child joins
`merge_offspring`, then recompiles and receives all evaluation from scratch.
The operator never scores or repairs its child.
