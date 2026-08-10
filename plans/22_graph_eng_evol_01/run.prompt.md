# Plan 22 evolutionary prompt-graph run

## GOAL

- `prompt_id`: `plan22.run_evolution_graph.v1`
- `role`: `graph_coordinator`
- `objective`: Execute the population-based computational graph in this prompt
  until it promotes an evidence-backed prompt graph or reaches an honest
  terminal.
- `non_goals`: Do not author candidate content, score candidates, choose an
  edge from prose, change evaluator controls, reveal holdouts to authoring
  nodes, inspect rendered media, or convert a failed run into success.
- `authorized_inputs`:
  - `evolutionary_approach/evolution_graph_approach.v4.md`
  - `previous_plan.obs.v1.md`
  - the eight exact prompts listed under `MODEL NODES`
  - controller-owned graph state and admitted node results
  - frozen development/regression inputs and evaluator-owned review inputs
- `excluded_context`: Full worker conversations, undeclared files, sibling
  messages not authorized by the context graph, secrets, mutable prior
  candidates, protected holdouts outside external review, and all PNG/image/
  visual/PDF/rendered-output content.
- `output_contract`: Emit only typed node activations and one terminal record.
  Each activation binds run, generation, candidate/parent IDs and digests,
  node, incoming edge, authorized state projection, prompt digest, output
  fields, and remaining counters. The terminal record binds the champion before
  and after, selected candidate if any, complete fitness/evaluation evidence,
  external-review results, and exact terminal state.
- `completion_condition`: Reach exactly one of `PROMOTED`,
  `CONVERGENCE_EXHAUSTED`, `EVALUATOR_UNAVAILABLE`,
  `REVIEW_AUTHORITY_UNPROVEN`, `SYSTEM_FAILURE`, or `INTERRUPTED`.

## GRAPH STATE

The controller owns one state object. Model nodes receive only the projection
authorized under `CONTEXT GRAPH`.

```text
run_id: stable string
status: ACTIVE | terminal
generation: integer, initially 0, maximum 6
population_size: integer, fixed at run start, minimum 4
variation_quotas:
  prompt_mutation: minimum 1 per later generation
  topology_mutation: minimum 1 per later generation
  recombination: minimum 1 when a compatible parent pair exists
  local_repair: zero or more when local findings exist
  total planned children: population_size
candidates:
  candidate_id -> {
    digest, parent_ids[], birth_operator, generation,
    prompt_graph, node_prompt_digests, topology_digest,
    complexity
  }
generation_population: generation -> candidate_id[]
candidate_status:
  candidate_id -> PROPOSED | COMPILED | EVALUATED | COMPILE_FAILED | ARCHIVED
compile_results: candidate_id -> compiled graph identity or compile failure
generation_compiled: generation -> candidate_id[]
archive:
  candidate_id -> immutable candidate identity + fitness + disposition
frontier: candidate_id[]
champion_before: candidate identity or null
development_results: candidate_id -> case_id -> result
regression_results: candidate_id -> case_id -> result
internal_reviews: candidate_id -> complete structured verdict
fitness: candidate_id -> ten-dimensional vector
selected_parents: variation_batch_id -> candidate_id[]
variation_plan:
  generation -> variation_batch_id -> invocation_id ->
    operator + parent_ids + assigned_child_id
variation_results: invocation_id -> child identity or typed no-child result
selection_pressure: finding_id -> admitted finding/evidence
review_attempts:
  review_attempt_id -> frozen candidate/control/corpus identity
active_review_attempt: review_attempt_id or null
challenge_results: review_attempt_id -> raw captured result
final_results: review_attempt_id -> raw captured result
counters:
  node_invocations, evaluator_retries,
  repairs_by_candidate, offspring_by_operator
```

Candidate status is exactly `PROPOSED -> COMPILED -> EVALUATED -> ARCHIVED` or
`PROPOSED -> COMPILE_FAILED -> ARCHIVED`.
Archive disposition is separately one of `REJECTED`, `FRONTIER`,
`REVIEW_TARGET`, or `PROMOTED`. Candidate bytes never change after `PROPOSED`;
every repair, mutation, or recombination creates a new ID and digest.

### Reducers

- `candidates`: set union by candidate ID. Same ID with different digest is
  `SYSTEM_FAILURE`; no overwrite exists.
- `generation_population`: write once per generation. Every ID must resolve to
  one immutable candidate born no later than that generation; duplicates fail.
- `population_size` and `variation_quotas`: frozen at run start. No author or
  evaluator output can shrink them; prompt and topology mutation quotas are
  always at least one after generation 0.
- `candidate_status`: controller-only monotonic transition through the exact
  lifecycle. Skip, rollback, and conflicting transition fail.
- `compile_results`: keyed union by candidate ID. Each generation candidate has
  exactly one immutable compiled identity or one deterministic compile failure.
- `generation_compiled`: write once per generation with the IDs whose compile
  results passed; it is always a subset of `generation_population[generation]`.
- `development_results`, `regression_results`, and `internal_reviews`: keyed
  union by candidate and case/test ID. Conflicting duplicate results fail.
- `archive`: append-only keyed union. An archived disposition cannot be erased
  or relabeled.
- `frontier`: deterministic replacement from `update_archive`; IDs must all
  exist in the archive and have complete fitness.
- `selected_parents`: write once per variation batch; every ID must be an
  archived candidate selected by the declared selection rule.
- `variation_plan`: append-only by generation and variation-batch ID. Before
  each fan-out it fixes operator quotas, parents, invocation IDs, and assigned
  child IDs; a shortfall may create a new batch but cannot rewrite an old one.
- `variation_results`: write once per planned invocation. `merge_offspring`
  activates only after every planned invocation has one bound result.
- `selection_pressure`: append-only union by stable finding ID. Conflicting
  evidence for one ID fails; findings are never silently removed.
- `counters`: monotonic controller increment before activation; model output
  cannot set or decrement counters.
- `review_attempts`, `challenge_results`, and `final_results`: append-only by
  review-attempt ID. Each result is write-once after raw capture and must bind
  the same attempt, candidate, and controls; no cross-attempt reuse.
- `active_review_attempt`: controller-only pointer to one frozen attempt; it may
  change only when `freeze_for_review` creates a new attempt.
- `champion_before`: immutable for the run. Only `promote_prompt_graph` may
  write the external champion pointer after compare-and-swap.

## MODEL NODES

| Node | Prompt | Function |
| --- | --- | --- |
| `seed_population` | `prompts/seed_population.prompt.v1.md` | Create a diverse initial population of immutable prompt graphs. |
| `review_candidate` | `prompts/review_candidate.prompt.v1.md` | Independently evaluate one compiled candidate; findings only. |
| `repair_candidate` | `prompts/repair_candidate.prompt.v1.md` | Create one locally repaired child from one failed parent. |
| `mutate_prompts` | `prompts/mutate_prompts.prompt.v1.md` | Mutate selected node-prompt genes while holding topology fixed. |
| `mutate_topology` | `prompts/mutate_topology.prompt.v1.md` | Mutate selected edges/guards/topology while holding prompt text fixed. |
| `recombine_candidates` | `prompts/recombine_candidates.prompt.v1.md` | Create one child from compatible subgraphs of two parents. |
| `challenge_review` | `prompts/challenge_review.prompt.v1.md` | Fresh Codex adversarial review of the frozen review target. |
| `final_review` | `prompts/final_review.prompt.v1.md` | Independent fresh Codex final review of the same target. |

## DETERMINISTIC NODES

These are graph operations, not model prompts.

| Node | State transition |
| --- | --- |
| `compile_population` | Emit one immutable compile result for every PROPOSED candidate; malformed graphs receive deterministic failed results rather than disappearing. |
| `dispatch_candidate_checks` | Map each COMPILED candidate to `test_candidate` and `review_candidate` in parallel. |
| `test_candidate` | Run the complete public development and regression denominator for one candidate. |
| `join_candidate_checks` | Wait for both result branches for the same candidate; never join across candidate IDs. |
| `join_population` | Wait until every candidate in the generation has one complete joined result. |
| `score_population` | Compute all ten fitness dimensions, protected-dimension failures, and normalized complexity. |
| `update_archive` | Append every evaluated candidate and disposition; compute the Pareto frontier. |
| `decide_generation` | Choose review, another generation, or exhaustion from frozen rules. |
| `select_parents` | Select parents from the frontier/archive using fitness, diversity, and failure coverage; never from caller preference. |
| `merge_offspring` | Wait for every planned variation result, union offspring, deduplicate digests, reject missing lineage, and create an exact-size next population. |
| `freeze_for_review` | Freeze one frontier candidate, reviewer controls, public results, and one evaluator-owned holdout attempt. |
| `capture_challenge` | Capture/hash challenge output before author exposure, validate bindings and structure, and admit pass/findings. |
| `capture_final` | Capture/hash final output before author exposure, validate bindings and structure, and admit pass/findings. |
| `compare_with_champion` | Verify mandatory gates and strict constrained-Pareto eligibility against the current champion. |
| `promote_prompt_graph` | Atomically compare-and-swap the champion pointer; append promotion lineage; never edit candidate bytes or active runs. |

## EXECUTION GRAPH

```text
START
  -> seed_population
  -> compile_population
       | at least one compiled candidate
       v
     dispatch_candidate_checks
       -- map for every compiled candidate --------------------+
       -> test_candidate -----------------------------------+  |
       -> review_candidate ---------------------------------+  |
       -> join_candidate_checks(candidate_id) <-------------+  |
       ---------------------------------------------------------+
       | no candidate compiled -> join_population with compile failures
  -> join_population(generation)
  -> score_population
  -> update_archive
  -> decide_generation
       | review_target_ready
       v
     freeze_for_review
       -> challenge_review -> capture_challenge
            | findings -> select_parents
            | pass
            v
          final_review -> capture_final
            | findings -> select_parents
            | pass
            v
          compare_with_champion
            | eligible -> promote_prompt_graph -> PROMOTED
            | ineligible + budget -> select_parents
       | no_review_target + budget
       v
     select_parents
       -> fan-out variation ------------------------------------+
          repair_candidate        (only local failed criteria)  |
          mutate_prompts          (node genes only)              |
          mutate_topology         (edge/topology genes only)     |
          recombine_candidates    (compatible parent subgraphs)  |
       -> merge_offspring <--------------------------------------+
            | shortfall + operator budget -> select_parents
       -> increment generation
       -> compile_population
       | no budget -> CONVERGENCE_EXHAUSTED
```

### Edge guards

| Source | Guard | Destination |
| --- | --- | --- |
| `START` | run inputs frozen and counters initialized | `seed_population` |
| `seed_population` | population count and unique digests equal requested size | `compile_population` |
| `compile_population` | at least one compiled candidate | `dispatch_candidate_checks` |
| `compile_population` | no candidate compiled and every compile result is complete | `join_population` |
| `dispatch_candidate_checks` | compiled candidate ID | `test_candidate` |
| `dispatch_candidate_checks` | same compiled candidate ID | `review_candidate` |
| `test_candidate` | complete denominator | matching `join_candidate_checks` |
| `review_candidate` | complete verdict | matching `join_candidate_checks` |
| `join_candidate_checks` | both matching results present | `join_population` |
| `join_population` | every generation candidate has joined checks or a compile failure | `score_population` |
| `score_population` | every candidate has complete fitness or deterministic failure vector | `update_archive` |
| `update_archive` | all generation candidates archived and frontier computed | `decide_generation` |
| `decide_generation` | eligible frontier candidate exists | `freeze_for_review` |
| `decide_generation` | no eligible target and generation remains | `select_parents` |
| `freeze_for_review` | target, controls, corpora, and authority frozen | `challenge_review` |
| `challenge_review` | raw result returned | `capture_challenge` |
| `capture_challenge` | pass and zero unresolved Critical/High | `final_review` |
| `capture_challenge` | findings and generation remains | `select_parents` |
| `final_review` | raw result returned | `capture_final` |
| `capture_final` | pass and zero unresolved Critical/High | `compare_with_champion` |
| `capture_final` | findings and generation remains | `select_parents` |
| `compare_with_champion` | all promotion conjuncts pass | `promote_prompt_graph` |
| `compare_with_champion` | ineligible and generation remains | `select_parents` |
| `promote_prompt_graph` | atomic compare-and-swap and promotion record pass | `PROMOTED` |
| `select_parents` | parent has admitted local finding and repair quota remains | `repair_candidate` |
| `select_parents` | prompt-mutation parent/operator quota assigned | `mutate_prompts` |
| `select_parents` | topology-mutation parent/operator quota assigned | `mutate_topology` |
| `select_parents` | compatible pair/recombination quota assigned | `recombine_candidates` |
| `repair_candidate` | planned invocation returns child or no-child result | `merge_offspring` |
| `mutate_prompts` | planned invocation returns child or failure result | `merge_offspring` |
| `mutate_topology` | planned invocation returns child or failure result | `merge_offspring` |
| `recombine_candidates` | planned invocation returns child, incompatible, or failure result | `merge_offspring` |
| `merge_offspring` | unique next population equals fixed size and generation remains | `compile_population` |
| `merge_offspring` | valid-child shortfall and operator-attempt budget remains | `select_parents` |
| `decide_generation` | generation budget exhausted | `CONVERGENCE_EXHAUSTED` |
| `merge_offspring` | legal offspring cannot fill population and operator-attempt budget exhausted | `CONVERGENCE_EXHAUSTED` |
| `capture_challenge` | findings and generation exhausted | `CONVERGENCE_EXHAUSTED` |
| `capture_final` | findings and generation exhausted | `CONVERGENCE_EXHAUSTED` |
| `compare_with_champion` | ineligible and generation exhausted | `CONVERGENCE_EXHAUSTED` |
| `challenge_review` | evaluator unavailable | `EVALUATOR_UNAVAILABLE` |
| `final_review` | evaluator unavailable | `EVALUATOR_UNAVAILABLE` |
| `freeze_for_review` | separate authority unproven | `REVIEW_AUTHORITY_UNPROVEN` |
| `capture_challenge` | separate authority or binding unproven | `REVIEW_AUTHORITY_UNPROVEN` |
| `capture_final` | separate authority or binding unproven | `REVIEW_AUTHORITY_UNPROVEN` |

Every node additionally has global fail-closed edges: state, contract, or
integrity failure routes to `SYSTEM_FAILURE`; external interruption routes to
`INTERRUPTED`. These global edges never produce another active node.

No source mixes unconditional and conditional routing. Each dynamic source has
one controller-owned routing function returning exactly one declared guard
value, except explicit fan-out/map nodes.

## CONTEXT GRAPH

Execution edges do not imply message access.

| Node | Receives | Must not receive |
| --- | --- | --- |
| `seed_population` | approach, observations, development cases, champion structure | evaluations, holdouts, review results |
| `review_candidate` | one compiled candidate, internal rubric, requested test IDs | author history, sibling candidates, prior verdicts, holdouts |
| `repair_candidate` | one parent, local findings, allowed gene diff, retest order | unrelated findings, siblings, holdouts, reviewer conversation |
| `mutate_prompts` | selected parent, admitted evidence, node-gene mutation rules | topology changes, hidden holdouts, sibling conversations |
| `mutate_topology` | selected parent, admitted evidence, edge search space | prompt-text changes, hidden holdouts, sibling conversations |
| `recombine_candidates` | exactly two parents, compatibility map, admitted fitness | other candidates, holdouts, reviewer conversation |
| `challenge_review` | frozen review target and evaluator-owned review inputs | author history, sibling candidates, prior external threads |
| `final_review` | same frozen target/inputs in a fresh thread | challenge result/thread, author history, sibling candidates |
| coordinator | state projections and admitted receipts | semantic source content not needed for routing |

Unauthorized context is dropped before invocation and recorded as a failed
noninterference test if its presence could alter the node result.

## TEST

The controller owns RUN-T01–RUN-T12. Each test records state version, node,
edge, candidate IDs/digests, exact evidence, and pass/fail. Prose cannot waive a
failure.

1. `RUN-T01 INVENTORY` — Exactly the eight model prompts exist and each has one
   complete GOAL/TEST/LOOP contract.
2. `RUN-T02 GRAPH_CLOSURE` — Every node and terminal is reachable; every
   nonterminal has an outgoing edge; every edge names one source, guard, and
   destination; no orphan or ambiguous route exists.
3. `RUN-T03 STATE_AND_REDUCERS` — Every node reads/writes declared fields only;
   reducers reject conflicting IDs, lifecycle skip/rollback, result overwrite,
   counter rollback, and cross-candidate or cross-review-attempt joins.
4. `RUN-T04 EXECUTION_CONTEXT_SEPARATION` — Adding an execution predecessor
   does not grant message access; unauthorized sibling/history injection cannot
   change a node's permitted result.
5. `RUN-T05 POPULATION` — Initial and later generations contain the fixed
   population size or an explicitly failed shortfall; candidates have unique
   immutable identities and complete lineage.
6. `RUN-T06 MAP_JOIN` — Both per-candidate branches execute against the same
   digest; candidate join waits for both; population join waits for every
   candidate exactly once through either joined checks or one compile failure;
   offspring merge waits for every planned variation invocation exactly once.
7. `RUN-T07 NODE_AND_EDGE_SEARCH` — Every later generation applies at least one
   node-prompt mutation and one topology-edge mutation; recombination runs when
   compatible parents exist; topology is not permanently hand-fixed.
8. `RUN-T08 ARCHIVE_AND_SELECTION` — Archive is append-only; frontier and
   parents derive from complete measured fitness, diversity, and protected
   constraints rather than author preference.
9. `RUN-T09 EXTERNAL_INDEPENDENCE` — Review target/inputs are frozen; challenge
   and final use fresh separate threads; raw results are captured before author
   exposure; missing authority fails closed.
10. `RUN-T10 INVALIDATION` — Every offspring candidate recompiles and reruns
    all public/internal evaluation; no parent score, review, or receipt is
    inherited as the child's result.
11. `RUN-T11 TERMINATION` — Generation, repair, evaluation-retry, and total-node
    counters bite; exhaustion preserves the champion.
12. `RUN-T12 CLAIM_BOUNDARY` — Fitness and routing are invariant to absent or
    changed PNG/rendered-output data and make no output-QA claim.

## LOOP

The graph loops only through `select_parents -> variation -> merge_offspring ->
compile_population`. Local repair is one variation operator, never in-place
editing. External findings join the admitted selection pressure for the next
generation; they do not reopen or repair the reviewed candidate. Each offspring
invalidates compilation, public tests, internal review, fitness, frontier
status, review target, and external results for itself.

Increment generation before `compile_population`. Stop when the next generation
would exceed six, the node-invocation bound is reached, no legal offspring can
be produced, evaluator execution is unavailable, review authority is unproven,
state integrity fails, or interruption occurs. Only `promote_prompt_graph` can
return `PROMOTED`; every other terminal preserves `champion_before`.
