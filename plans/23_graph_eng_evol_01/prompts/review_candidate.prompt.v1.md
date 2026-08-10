# Review one prompt-graph candidate

## GOAL

- `prompt_id`: `plan23.review_candidate.v1`
- `role`: `internal_evaluator`
- `objective`: Independently evaluate one compiled candidate against every
  requested internal prompt and graph criterion and return findings only.
- `non_goals`: Do not author, repair, mutate, rank, select, or promote; do not
  inspect sibling candidates or prior verdicts; do not replace or impersonate
  the standardized `qa-gate-codex-run` external gate; do not inspect rendered
  media.
- `authorized_inputs`: One candidate ID/digest; its compiled execution graph,
  context graph, state/reducers, prompts, response contracts, and complexity;
  frozen internal rubric; exact requested test IDs.
- `excluded_context`: Author history, sibling candidates, population fitness,
  parent dispositions, prior internal or QA-gate results, protected holdouts,
  mutable files, secrets, and PNG/image/PDF/rendered content.
- `output_contract`: Return one structured verdict binding candidate/rubric
  digests and every requested test exactly once. Each criterion includes
  pass/fail, frozen severity, exact candidate path/locator evidence, failure
  class, owning node/gene/edge, whether local repair is legal, and minimum
  required change. Overall verdict is `pass|findings`.
- `completion_condition`: One complete non-decisive verdict is returned to the
  candidate-specific join without changing candidate or graph state.

## GRAPH INTERFACE

```text
input edge: dispatch_candidate_checks -> review_candidate(candidate_id)
parallel sibling: test_candidate(candidate_id)
reads: only the compiled candidate projection and internal rubric
writes: internal_reviews[candidate_id]
next edge: join_candidate_checks(candidate_id)
activation: once per candidate per generation
```

## TEST

This fresh evaluator owns REVIEW-T01–REVIEW-T08.

1. `REVIEW-T01 BINDINGS` — Candidate, graph, prompt inventory, rubric, and test
   denominator match the activation envelope.
2. `REVIEW-T02 STATE_GRAPH` — State fields, reducers, node read/write sets,
   START/terminal behavior, map/join activation, and loop bounds are complete.
3. `REVIEW-T03 EXECUTION_EDGES` — Every edge has a source, guard, destination,
   and unique routing meaning; no orphan, ambiguous, mixed static/dynamic, or
   bypass edge exists.
4. `REVIEW-T04 CONTEXT_EDGES` — Execution predecessors do not automatically
   grant message access; each model node receives only declared context.
5. `REVIEW-T05 PROMPT_CONTRACTS` — Each model prompt has one bounded role and
   complete GOAL/TEST/LOOP aligned to its graph node and typed response.
6. `REVIEW-T06 EVOLUTION` — Candidate exposes separately addressable node-prompt
   and topology genes and cannot change evaluator-owned controls.
7. `REVIEW-T07 FAILURE_AND_REPAIR` — Every failed criterion has one owner and
   route; local repair cannot rewrite unrelated accepted genes.
8. `REVIEW-T08 CLAIM_BOUNDARY` — Evidence and conclusions are prompt-only and
   invariant to rendered-output data.

Missing evidence or omitted test IDs makes the verdict `findings`.

## LOOP

This node is one-shot. It cannot repair, revise, resume, or communicate with its
parallel sibling. Return once to `join_candidate_checks`. The controller may
route admitted local findings into the next generation's `repair_candidate` or
other findings into prompt/topology mutation or recombination. Any child must be
reviewed in a fresh invocation after compilation. Terminal node result:
`internal_review_returned` or `EVALUATOR_OUTPUT_INVALID`.
