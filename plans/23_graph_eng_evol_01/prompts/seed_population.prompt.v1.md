# Seed the prompt-graph population

## GOAL

- `prompt_id`: `plan23.seed_population.v1`
- `role`: `population_initializer`
- `objective`: Create the requested number of diverse, immutable prompt-graph
  candidates for generation 0.
- `non_goals`: Do not evaluate, rank, repair, select, or promote candidates; do
  not copy one candidate under multiple IDs; do not create evaluator controls;
  do not use PNG or rendered-output evidence.
- `authorized_inputs`: Governing Plan 23 v1 approach; previous-plan observations;
  visible development cases; champion structure or null; controller-assigned
  run ID, population size, candidate IDs, output roots, and response contract.
- `excluded_context`: Regression answers beyond disclosed public cases,
  protected holdouts, fitness or review results, prior reviewer conversations,
  mutable candidate aliases, secrets, and rendered media.
- `output_contract`: Return exactly `population_size` candidate records. Each
  record binds candidate ID, generation 0, `birth_operator=seed`, parent IDs,
  graph entry/output, typed nodes and ports, directed execution edges, separate
  context edges, state fields/reducers, node-prompt genes, topology genes,
  counters, terminals, prompt paths/digests, topology digest, full candidate
  digest, diversity rationale, expected strengths, and trade-offs.
- `completion_condition`: A complete unscored population is returned once to
  `compile_population` with no duplicate candidate or graph digest.

## GRAPH INTERFACE

```text
input edge: START -> seed_population
reads: approach, observations, development cases, champion structure,
       population_size, assigned candidate IDs/output roots
writes: candidates[candidate_id], generation_population[0],
        candidate_status[candidate_id]=PROPOSED
next edge on exact count + unique digests: compile_population
failure edge: SYSTEM_FAILURE or one fresh seed retry owned by controller
```

Candidates must differ causally, not cosmetically. Across the population,
explore at least two materially different execution topologies and at least two
different prompt-contract strategies while preserving the governing QA scope.

## TEST

The controller owns SEED-T01–SEED-T07 after return.

1. `SEED-T01 CARDINALITY` — Candidate count equals the fixed population size;
   every assigned ID appears exactly once.
2. `SEED-T02 IMMUTABLE_IDENTITY` — Each ID binds one unique candidate digest,
   topology digest, prompt inventory, and generation-zero lineage.
3. `SEED-T03 GRAPH_CLOSURE` — Every graph has an entry, output/terminal, typed
   node inputs/outputs, execution edges, context edges, reducers, and reachable
   failure behavior.
4. `SEED-T04 PROMPT_CONTRACTS` — Every model node prompt has complete explicit
   GOAL/TEST/LOOP and a typed response.
5. `SEED-T05 DIVERSITY` — Pairwise comparison proves material prompt-gene and
   topology diversity; whitespace, renaming, and reordered prose do not count.
6. `SEED-T06 AUTHORITY_BOUNDARY` — No candidate controls QA-gate criteria,
   severity, threshold, transport, iteration limit, regression denominator,
   QA result, verification, or promotion.
7. `SEED-T07 CLAIM_BOUNDARY` — No candidate scores or claims PNG, visual, PDF,
   rendered-page, curriculum, or downstream-output quality.

## LOOP

This node is one-shot per seed attempt and cannot repair its population. Return
all candidates together. Missing count, duplicate digest, malformed graph, or
insufficient diversity fails the attempt before compilation. The controller may
start one fresh seed attempt with the same inputs and new candidate IDs; it may
not accept a partial population. A valid population advances to
`compile_population`. Terminal result: `population_seeded` or `SYSTEM_FAILURE`.
