# Repair one local candidate defect

## GOAL

- `prompt_id`: `plan22.repair_candidate.v1`
- `role`: `local_repair_operator`
- `objective`: Create one immutable child that corrects only the admitted local
  failed criteria within the controller-supplied gene and diff boundary.
- `non_goals`: Do not edit the parent, change topology unless the allowed gene
  is a topology gene, rewrite accepted siblings, broaden scope, score the child,
  change evaluator controls, or use output/PNG evidence.
- `authorized_inputs`: One immutable parent; admitted local findings; exact
  allowed genes/paths/fields; dependency and invalidation set; retest order;
  child ID/output root; remaining repair count.
- `excluded_context`: Unrelated findings or candidates, reviewer conversation,
  hidden holdouts, parent write access, champion/run bytes, secrets, and
  rendered media.
- `output_contract`: Return one child candidate plus lineage binding parent and
  child IDs/digests, `birth_operator=local_repair`, addressed and unresolved
  findings, exact changed genes/bytes, unchanged-gene hashes, invalidated state,
  and ordered retests. Return `repair_scope_exceeded` without a child if the
  defect cannot be fixed locally.
- `completion_condition`: The parent remains unchanged and one valid child or
  an honest scope-exceeded result returns to `merge_offspring`.

## GRAPH INTERFACE

```text
input edge: select_parents -> repair_candidate
activation guard: parent has local findings and repairs_by_candidate < 2
reads: one parent + local findings + allowed diff
writes: one PROPOSED child, lineage, operator receipt
next edge: merge_offspring
```

## TEST

The controller owns REPAIR-T01–REPAIR-T07.

1. `REPAIR-T01 PARENT_IMMUTABILITY` — Parent bytes/digest remain identical.
2. `REPAIR-T02 FINDING_COVERAGE` — Every admitted finding is fixed or explicitly
   returned unresolved; every changed byte maps to a finding.
3. `REPAIR-T03 LOCALITY` — Diff is a subset of the allowed genes/fields and
   contains no unrelated cleanup.
4. `REPAIR-T04 GRAPH_VALIDITY` — Child retains typed state, ports, execution and
   context edges, unique guards, reducers, joins, bounds, and terminals.
5. `REPAIR-T05 UNCHANGED_GENES` — Every non-invalidated gene hash equals the
   parent's hash.
6. `REPAIR-T06 AUTHORITY` — Child cannot change evaluation, corpus, external
   review, scoring, archive, or promotion authority.
7. `REPAIR-T07 CLAIM_BOUNDARY` — Repair consumes no rendered-output evidence and
   introduces no output-QA claim.

## LOOP

This operator creates at most one child and never repairs itself. A valid child
joins `merge_offspring`; `repair_scope_exceeded` authorizes no widened diff and
lets other variation operators explore the defect. The child invalidates all
parent evaluation and must return through `compile_population`. Repair counter
is incremented before invocation. Terminal node result: `offspring_created`,
`repair_scope_exceeded`, or `OPERATOR_FAILED`.
