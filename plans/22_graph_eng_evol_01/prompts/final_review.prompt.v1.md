# Final-review the selected prompt graph

## GOAL

- `prompt_id`: `plan22.final_review.v1`
- `role`: `external_reviewer`
- `objective`: Independently make the decisive prompt-only judgment for the
  exact frozen candidate that passed challenge review, in a new Codex thread
  using the same target, rubric, thresholds, and denominators.
- `non_goals`: Do not read/inherit the challenge result or thread; author,
  repair, mutate, recombine, score, or promote; inspect sibling candidates or
  rendered outputs; reinterpret severity; resume or transfer another thread.
- `authorized_inputs`: The same frozen review target and exact prompts;
  state/execution/context graph; lineage and measured public results; frozen
  rubric, severity, thresholds, response contract, regression and single-use
  holdout inputs/results, complexity/fitness evidence, provider facts, and
  clean target bindings.
- `excluded_context`: Challenge result/conversation, Claude history, population
  content beyond bound comparison evidence, mutable files, caller overrides,
  secrets, and PNG/image/visual/PDF/rendered-media content.
- `output_contract`: Return one raw structured result binding target/control/
  corpus digests and distinct job/thread/turn IDs; every required test/case;
  exact evidence and frozen severity; all findings; unresolved Critical/High
  count; prompt-only scope statement; and `pass|reject`.
- `completion_condition`: One raw result returns to `capture_final`; pass is
  legal only when every test passes and unresolved Critical/High equals zero.

## GRAPH INTERFACE

```text
input edge: capture_challenge(pass) -> final_review
reads: same frozen review projection; excludes challenge result/thread
writes: raw final result only
pass edge after capture: capture_final -> compare_with_champion
finding edge after capture: capture_final -> select_parents
thread rule: fresh and distinct from challenge review
```

## TEST

This fresh Codex reviewer owns FINAL-T01–FINAL-T12 and rechecks from bound
candidate bytes rather than inheriting challenge conclusions.

1. `FINAL-T01 TARGET_AND_THREAD` — Every target/control/corpus binding is exact;
   thread/job/turn identities are distinct from challenge review.
2. `FINAL-T02 STATE_EXECUTION_CONTEXT` — State/reducers, typed nodes, execution
   edges, context edges, routing, joins, loops, bounds, and terminals compose.
3. `FINAL-T03 PROMPT_CONTRACTS` — Every model prompt's GOAL/TEST/LOOP and typed
   response agree with node reads/writes and routing authority.
4. `FINAL-T04 POPULATION_AND_ARCHIVE` — Population, immutable lineage,
   per-candidate evaluation, archive, and frontier are complete and nonmutable.
5. `FINAL-T05 NODE_AND_EDGE_SEARCH` — Both prompt and topology search spaces
   genuinely vary and are independently attributable/tested.
6. `FINAL-T06 REPAIR_AND_CROSSOVER` — Repair locality, parent compatibility,
   child invalidation, and from-scratch reevaluation are enforced.
7. `FINAL-T07 REGRESSION_HOLDOUT` — Exact denominators reconcile to complete
   executed results with no omission, duplicate, waiver, or stale reuse.
8. `FINAL-T08 FITNESS_PARETO` — Ten dimensions, protected non-regression,
   diversity, measured improvement, minimality, and complexity determine
   frontier/selection without author override.
9. `FINAL-T09 AUTHORITY` — Author, reviewer, and controller write domains are
   separate; raw capture precedes exposure; only promotion changes champion.
10. `FINAL-T10 TERMINATION` — All attempt/generation/node bounds bite and every
    failure/interrupt preserves the champion.
11. `FINAL-T11 CLAIM_BOUNDARY` — Candidate and decision state prompt assurance
    only and explicitly withhold PNG/visual/PDF/curriculum/output approval.
12. `FINAL-T12 ADVERSARIAL_RECHECK` — Attempt concrete substitutions and bypasses
    across every protected boundary; report all findings.

Any unresolved Critical/High or incomplete evidence produces `reject`.

## LOOP

This decisive review is one-shot. Return the raw result once; do not repair,
revise, resume, or read challenge context. `capture_final` binds it before
author exposure. Captured pass routes to deterministic champion comparison;
this node never promotes. Captured findings freeze the candidate and route
evidence into the next generation through `select_parents` if budget remains.
A new candidate must repeat all compilation, evaluation, and both fresh reviews.
