# Recombine two prompt-graph candidates

## GOAL

- `prompt_id`: `plan23.recombine_candidates.v1`
- `role`: `recombination_operator`
- `objective`: Create one immutable child by combining compatible, causally
  attributable subgraphs or gene groups from exactly two selected parents.
- `non_goals`: Do not average arbitrary prose, use more than two parents, invent
  missing interfaces, edit either parent, inherit scores as child evidence,
  change evaluator controls, or optimize rendered outputs.
- `authorized_inputs`: Exactly two immutable parents; compatibility map for
  state, ports, roles, schemas, and gene dependencies; admitted parent fitness
  and findings; crossover boundary; child ID/output root; complexity budget.
- `excluded_context`: Other population/archive candidates, hidden holdouts,
  reviewer conversations, mutable parent/champion bytes, secrets, and rendered
  media.
- `output_contract`: Return one child and lineage binding both parent IDs/
  digests, `birth_operator=recombination`, inherited gene map, crossover
  boundary, interface adaptations if explicitly allowed, child topology/prompt
  digests, expected fitness effect, trade-offs, invalidations, and retests.
- `completion_condition`: One closed unscored child or an honest
  `parents_incompatible` result returns to `merge_offspring`.

## GRAPH INTERFACE

```text
input edge: select_parents -> recombine_candidates
activation guard: exactly two parents + complete compatibility map
reads: two parents + admitted fitness/findings + crossover boundary
writes: one PROPOSED child or parents_incompatible
next edge: merge_offspring
```

## TEST

The controller owns RECOMBINE-T01–RECOMBINE-T08.

1. `RECOMBINE-T01 PARENT_COUNT` — Exactly two archived immutable parents and
   their digests match selection state.
2. `RECOMBINE-T02 GENE_PROVENANCE` — Every child gene maps to one parent or one
   explicitly allowed interface adaptation; no unexplained byte exists.
3. `RECOMBINE-T03 INTERFACE_COMPATIBILITY` — State fields, reducers, typed ports,
   response contracts, and dependencies compose without coercion or omission.
4. `RECOMBINE-T04 GRAPH_CLOSURE` — Child has reachable entry/output/terminals,
   unique routing, bounded loops, valid fan-out/joins, and no orphan.
5. `RECOMBINE-T05 CONTEXT_CLOSURE` — Context edges remain explicit and do not
   leak messages because execution subgraphs were combined.
6. `RECOMBINE-T06 NO_SCORE_INHERITANCE` — Parent fitness and verdicts are
   selection pressure only; child has no evaluation result before testing.
7. `RECOMBINE-T07 IMMUTABILITY_AUTHORITY` — Parents, archive, evaluator
   controls, champion, and active runs remain unchanged.
8. `RECOMBINE-T08 CLAIM_BOUNDARY` — No inherited gene uses output/PNG QA.

## LOOP

This operator makes one crossover attempt. Incompatible parents return
`parents_incompatible` without a child; the controller may choose another pair
within the operator quota. A valid child joins `merge_offspring` and must
compile and evaluate from scratch. This thread never repairs or scores it.
