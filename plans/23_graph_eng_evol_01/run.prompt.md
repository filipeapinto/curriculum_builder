# Plan 23 evolutionary prompt-graph run

## GOAL

- `prompt_id`: `plan23.run_evolution_graph.v1`
- `role`: `graph_coordinator`
- `objective`: Execute the bounded population graph until one immutable prompt
  graph earns a verified standardized QA-gate pass and promotion, or the graph
  reaches an honest terminal.
- `non_goals`: Do not author candidate content, score from prose, edit an
  existing candidate, write under a QA-gate-owned `QA/` directory, construct or
  soften the external reviewer prompt, reinterpret a gate verdict, inspect
  rendered media, or turn an unavailable/failed gate into success.
- `authorized_inputs`:
  - `evolutionary_approach/evolution_graph_approach.v1.md`
  - `previous_plan.obs.v1.md`
  - `qa_criteria.v1.md`
  - the six exact model prompts listed under `MODEL NODES`
  - `.claude/skills/qa-gate-codex-run/SKILL.md`
  - `.claude/skills/qa-gate-codex-run/scripts/qa_gate.py`
  - controller-owned graph state and admitted node results
  - frozen public development/regression inputs
- `excluded_context`: Undeclared files, full worker conversations, sibling
  messages not authorized by the context graph, hidden holdout answers,
  secrets, mutable prior candidates, raw private reviewer reasoning, and all
  PNG/image/visual/PDF/rendered-output content.
- `output_contract`: Emit typed node activations and one terminal record. Every
  activation binds run, generation, candidate/parent IDs and digests, node,
  incoming edge, authorized state projection, prompt digest when applicable,
  result fields, and remaining counters. The terminal binds champion before
  and after, selected candidate if any, complete evaluation evidence, exact QA
  state, QA verification evidence, and terminal reason.
- `completion_condition`: Reach exactly one of `PROMOTED`,
  `CONVERGENCE_EXHAUSTED`, `QA_GATE_FAILED`, `QA_ERROR`,
  `QA_INTEGRITY_BREACH`, `SYSTEM_FAILURE`, or `INTERRUPTED`.

## FROZEN QA STANDARD

Before `START`, hash and freeze:

```text
skill_root: .claude/skills/qa-gate-codex-run
gate_script: .claude/skills/qa-gate-codex-run/scripts/qa_gate.py
criteria_file: plans/23_graph_eng_evol_01/qa_criteria.v1.md
criteria_digest: sha256(criteria file)
approach_ground: plans/23_graph_eng_evol_01/evolutionary_approach/evolution_graph_approach.v1.md
run_ground: plans/23_graph_eng_evol_01/run.prompt.md
focus: graph correctness, prompt-graph agreement, evolutionary integrity,
       authority separation, regression evidence, and promotion safety
threshold: blocker
max_iterations: 5
transport: app-server
allow_execution: false
```

The values above are immutable for the run. A candidate, author node, caller
message, or gate finding cannot alter them.

## GRAPH STATE

```text
run_id: stable string
status: ACTIVE | terminal
generation: integer, initially 0, maximum 6
population_size: integer, fixed at run start, minimum 4

variation_quotas:
  prompt_mutation: minimum 1 per generation after generation 0
  topology_mutation: minimum 1 per generation after generation 0
  recombination: minimum 1 when a compatible parent pair exists
  local_repair: zero or more when admitted local findings exist
  total planned children: population_size

candidates:
  candidate_id -> {
    digest, parent_ids[], birth_operator, generation,
    prompt_graph, node_prompt_digests, topology_digest, complexity
  }
generation_population: generation -> candidate_id[]
candidate_status:
  candidate_id -> PROPOSED | COMPILED | EVALUATED | COMPILE_FAILED | ARCHIVED
compile_results: candidate_id -> immutable compile result
generation_compiled: generation -> candidate_id[]
development_results: candidate_id -> case_id -> result
regression_results: candidate_id -> case_id -> result
internal_reviews: candidate_id -> structured verdict
fitness: candidate_id -> ten-dimensional vector
archive: candidate_id -> immutable identity + fitness + disposition
frontier: candidate_id[]

selected_parents: variation_batch_id -> candidate_id[]
variation_plan:
  generation -> variation_batch_id -> invocation_id ->
    operator + parent_ids + assigned_child_id
variation_results: invocation_id -> child identity or typed no-child result
selection_pressure: finding_id -> admitted evidence

qa_standard:
  skill_digest, script_digest, criteria_digest, approach_digest, run_digest,
  focus, threshold, max_iterations, transport, allow_execution
qa_attempts:
  qa_attempt_id -> {
    workspace, qa_dir,
    status: STARTING | ROUND_OPEN | QA_PASSED | QA_FAILED | QA_ERROR |
            VERIFIED_PASS | VERIFIED_FAILURE | INTEGRITY_BREACH | CLOSED,
    session_id, thread_id, rounds_completed, current_artifact_version,
    current_candidate_id, current_candidate_digest, chain, terminal_reason
  }
active_qa_attempt: qa_attempt_id or null
qa_submissions:
  qa_attempt_id + version ->
    candidate_id + candidate_digest + artifact_path + artifact_digest
qa_findings: qa_attempt_id + round -> threshold finding records
qa_verification: qa_attempt_id -> immutable verify output
qa_postmortem: qa_attempt_id -> immutable postmortem classification

champion_before: immutable candidate identity or null
counters:
  node_invocations, generation_attempts, operator_attempts,
  offspring_by_operator, qa_rounds
```

### Reducers and ownership

- `candidates`, compilation/test/review results, fitness, archive,
  `qa_submissions`, `qa_findings`, QA terminal evidence, and promotion lineage
  are keyed append-only unions. Conflicting duplicate keys are
  `SYSTEM_FAILURE`.
- Candidate status follows exactly `PROPOSED -> COMPILED -> EVALUATED ->
  ARCHIVED` or `PROPOSED -> COMPILE_FAILED -> ARCHIVED`. No skip, rollback, or
  overwrite exists.
- Candidate bytes never change after `PROPOSED`. Every repair, mutation, and
  recombination creates a new ID and digest.
- `generation_population`, `generation_compiled`, `selected_parents`, and each
  variation batch are write-once.
- `frontier` is replaced only by deterministic `update_archive` from complete
  fitness records.
- `qa_standard` is controller-owned and write-once before `START`.
- Each QA-attempt status may advance only from the exact exit/output of
  `qa_gate.py`, its `verify` result, or controller closure after a lost champion
  compare. Model output cannot set it.
- `active_qa_attempt` points to at most one `STARTING` or `ROUND_OPEN` attempt.
  A terminal or closed session is never resumed.
- `qa_submissions` versions strictly increase within one QA attempt. One
  version binds one candidate and artifact digest; no overwrite or reuse exists.
- Only `qa_gate.py` may create or write `<attempt.workspace>/QA/`. The
  controller and all model nodes have read-only access to admitted structured
  results.
- Counters increment before activation and never decrease.
- `champion_before` is immutable. Only `promote_prompt_graph` may atomically
  update the external champion pointer.

## MODEL NODES

| Node | Prompt | Function |
| --- | --- | --- |
| `seed_population` | `prompts/seed_population.prompt.v1.md` | Create the diverse immutable generation-zero population. |
| `review_candidate` | `prompts/review_candidate.prompt.v1.md` | Independently inspect one compiled candidate; findings only. |
| `repair_candidate` | `prompts/repair_candidate.prompt.v1.md` | Create one locally repaired child from admitted findings. |
| `mutate_prompts` | `prompts/mutate_prompts.prompt.v1.md` | Mutate node-prompt genes while topology remains fixed. |
| `mutate_topology` | `prompts/mutate_topology.prompt.v1.md` | Mutate graph genes while prompt bytes remain fixed. |
| `recombine_candidates` | `prompts/recombine_candidates.prompt.v1.md` | Recombine compatible subgraphs from two parents. |

There is no external-review model prompt in this plan. External QA belongs
exclusively to the standardized gate below.

## DETERMINISTIC NODES

| Node | State transition |
| --- | --- |
| `compile_population` | Compile every proposed candidate; record a pass or deterministic failure for each. |
| `dispatch_candidate_checks` | Map every compiled candidate to `test_candidate` and `review_candidate` in parallel. |
| `test_candidate` | Execute the complete public development and regression denominator for one candidate. |
| `join_candidate_checks` | Join test and internal-review results for the same candidate ID only. |
| `join_population` | Wait for one joined result or compile failure for every generation candidate. |
| `score_population` | Compute all ten fitness dimensions and protected failures. |
| `update_archive` | Append every candidate and compute the constrained Pareto frontier. |
| `decide_generation` | Select QA submission, further evolution, or exhaustion from frozen guards. |
| `select_parents` | Select archived parents from fitness, diversity, and admitted failure coverage. |
| `merge_offspring` | Join the fixed variation plan, validate lineage, deduplicate, and construct the next population. |
| `prepare_qa_artifact` | Export the first eligible frozen candidate as `prompt_graph.v1.md`. |
| `prepare_qa_revision` | Export a later eligible frozen candidate as strictly newer `prompt_graph.vN.md`. |
| `open_qa_attempt` | Allocate a fresh isolated QA workspace and set one active attempt before its first submission. |
| `close_qa_attempt` | Close a verified terminal attempt that lost the champion race; never alter its QA evidence. |
| `capture_qa_result` | Bind gate stdout, exit code, session, round, candidate, artifact, and chain before findings are exposed. |
| `capture_qa_verification` | Bind the exact `verify` result to the terminal gate state and artifact. |
| `capture_qa_postmortem` | Bind the fresh-session postmortem classification after verified `QA_FAILED`. |
| `compare_with_champion` | Check protected gates and strict constrained-Pareto eligibility against the current champion. |
| `promote_prompt_graph` | Atomically compare-and-swap the champion and append promotion lineage. |

## STANDARDIZED QA-GATE NODES

These nodes invoke the named skill implementation. They are external action
nodes, not model prompts and not coordinator-authored reviews.

### `qa_gate_start`

```text
python3 .claude/skills/qa-gate-codex-run/scripts/qa_gate.py start
  --artifact <qa_workspace>/prompt_graph.v1.md
  --criteria-file plans/23_graph_eng_evol_01/qa_criteria.v1.md
  --focus "graph correctness, prompt-graph agreement, evolutionary integrity,
           authority separation, regression evidence, and promotion safety"
  --threshold blocker
  --max-iterations 5
  --transport app-server
  --ground plans/23_graph_eng_evol_01/evolutionary_approach/evolution_graph_approach.v1.md
  --ground plans/23_graph_eng_evol_01/run.prompt.md
```

### `qa_gate_round`

```text
python3 .claude/skills/qa-gate-codex-run/scripts/qa_gate.py round
  --qa-dir <qa_workspace>/QA
  --artifact <qa_workspace>/prompt_graph.vN.md
```

### `qa_gate_verify`

```text
python3 .claude/skills/qa-gate-codex-run/scripts/qa_gate.py verify
  --qa-dir <qa_workspace>/QA
```

### `qa_gate_postmortem`

```text
python3 .claude/skills/qa-gate-codex-run/scripts/qa_gate.py postmortem
  --qa-dir <qa_workspace>/QA
```

Do not invoke Codex directly for the decisive verdict. Do not write QA files by
hand. Do not report a pass that `qa_gate_verify` does not confirm.

## EXECUTION GRAPH

```text
START
  -> seed_population
  -> compile_population
       | at least one candidate compiled
       -> dispatch_candidate_checks
            -- map each compiled candidate ----------------+
            -> test_candidate --------------------------+  |
            -> review_candidate ------------------------+  |
            -> join_candidate_checks(candidate_id) <----+  |
            ------------------------------------------------+
       | no candidate compiled
       -> join_population with complete compile failures
  -> join_population(generation)
  -> score_population
  -> update_archive
  -> decide_generation
       | eligible candidate + no active QA attempt
       -> open_qa_attempt -> prepare_qa_artifact
          -> qa_gate_start -> capture_qa_result
       | eligible candidate + active attempt ROUND_OPEN
       -> prepare_qa_revision -> qa_gate_round -> capture_qa_result
       | no eligible candidate + generation budget
       -> select_parents
       | no budget
       -> CONVERGENCE_EXHAUSTED

capture_qa_result
  | exit 10 + ROUND_OPEN
  -> admit threshold findings -> select_parents
  | exit 0 + QA_PASSED
  -> qa_gate_verify -> capture_qa_verification
       | verified pass
       -> compare_with_champion
            | eligible -> promote_prompt_graph -> PROMOTED
            | ineligible + budget
            -> close_qa_attempt -> select_parents
            | ineligible + no budget -> CONVERGENCE_EXHAUSTED
       | verification problems
       -> QA_INTEGRITY_BREACH
  | exit 1 + QA_FAILED
  -> qa_gate_verify -> capture_qa_verification
       | record verified
       -> qa_gate_postmortem -> capture_qa_postmortem -> QA_GATE_FAILED
       | verification problems
       -> QA_INTEGRITY_BREACH
  | exit 2 + QA_ERROR
  -> qa_gate_verify -> capture_qa_verification
       | record verified + terminal remains QA_ERROR
       -> QA_ERROR
       | verification problems
       -> QA_INTEGRITY_BREACH
  | unexpected exit or malformed state
  -> SYSTEM_FAILURE

select_parents
  -> fan-out fixed variation plan --------------------------+
       repair_candidate          when local findings exist  |
       mutate_prompts            prompt genes only           |
       mutate_topology           graph genes only            |
       recombine_candidates      compatible two-parent genes |
  -> merge_offspring <---------------------------------------+
       | exact valid population
       -> increment generation -> compile_population
       | shortfall + operator budget
       -> select_parents
       | no operator/generation budget
       -> CONVERGENCE_EXHAUSTED
```

## EDGE GUARDS

| Source | Guard | Destination |
| --- | --- | --- |
| `START` | inputs and QA standard frozen | `seed_population` |
| `seed_population` | exact population size and unique digests | `compile_population` |
| `compile_population` | at least one compiled candidate | `dispatch_candidate_checks` |
| `compile_population` | complete compile failures for all candidates | `join_population` |
| `dispatch_candidate_checks` | compiled candidate ID | `test_candidate` and `review_candidate` |
| `test_candidate` | complete denominator | matching `join_candidate_checks` |
| `review_candidate` | complete verdict | matching `join_candidate_checks` |
| `join_candidate_checks` | matching test and review records | `join_population` |
| `join_population` | every generation candidate accounted for | `score_population` |
| `score_population` | complete fitness or deterministic failure vectors | `update_archive` |
| `update_archive` | archive append and frontier complete | `decide_generation` |
| `decide_generation` | eligible target and no active QA attempt | `open_qa_attempt` |
| `open_qa_attempt` | fresh workspace and active attempt bound | `prepare_qa_artifact` |
| `decide_generation` | eligible target and active attempt `ROUND_OPEN` | `prepare_qa_revision` |
| `decide_generation` | no eligible target and budget remains | `select_parents` |
| `prepare_qa_artifact` | frozen version 1 artifact | `qa_gate_start` |
| `prepare_qa_revision` | frozen strictly newer version artifact | `qa_gate_round` |
| `qa_gate_start` or `qa_gate_round` | raw process returned | `capture_qa_result` |
| `capture_qa_result` | exit `10` and state `ROUND_COMPLETE` | `select_parents` |
| `capture_qa_result` | exit `0` and state `QA_PASSED` | `qa_gate_verify` |
| `capture_qa_result` | exit `1` and state `QA_FAILED` | `qa_gate_verify` |
| `capture_qa_result` | exit `2` and state `QA_ERROR` | `qa_gate_verify` |
| `qa_gate_verify` | claimed pass and zero verification problems | `compare_with_champion` |
| `qa_gate_verify` | claimed failure and zero verification problems | `qa_gate_postmortem` |
| `qa_gate_verify` | claimed error and zero verification problems | `QA_ERROR` |
| `qa_gate_verify` | any verification problem | `QA_INTEGRITY_BREACH` |
| `qa_gate_postmortem` | complete bound classification | `QA_GATE_FAILED` |
| `compare_with_champion` | every promotion conjunct passes | `promote_prompt_graph` |
| `compare_with_champion` | ineligible and budget remains | `close_qa_attempt` |
| `close_qa_attempt` | terminal attempt preserved and active pointer cleared | `select_parents` |
| `select_parents` | local finding and repair quota | `repair_candidate` |
| `select_parents` | prompt mutation assignment | `mutate_prompts` |
| `select_parents` | topology mutation assignment | `mutate_topology` |
| `select_parents` | compatible pair and recombination quota | `recombine_candidates` |
| every variation operator | planned bound result | `merge_offspring` |
| `merge_offspring` | exact unique population and generation remains | `compile_population` |
| `merge_offspring` | child shortfall and attempt budget remains | `select_parents` |

Every node also has fail-closed routes for contract/state/integrity failure to
`SYSTEM_FAILURE` and external interruption to `INTERRUPTED`.

## CONTEXT GRAPH

| Node | Receives | Must not receive |
| --- | --- | --- |
| `seed_population` | approach, observations, public cases, champion structure | results, QA findings, QA session, rendered media |
| `review_candidate` | one compiled candidate and internal rubric | siblings, author history, QA session/results |
| `repair_candidate` | one parent, admitted findings, exact allowed diff | unrelated findings, raw QA conversation, hidden holdouts |
| `mutate_prompts` | one parent, admitted evidence, prompt-gene rules | topology-write authority, raw QA conversation |
| `mutate_topology` | one parent, admitted evidence, topology search space | prompt-write authority, raw QA conversation |
| `recombine_candidates` | exactly two parents and compatibility map | other candidates, raw QA conversation |
| `prepare_qa_artifact` / `prepare_qa_revision` | one frozen eligible candidate and complete public evidence | mutable candidate roots, hidden answers, author conversations |
| `qa_gate.py` | frozen artifact, criteria, focus, grounds | controller verdict suggestions, champion write authority |
| `select_parents` | archive fitness and admitted structured findings | private Codex reasoning, mutable QA controls |
| `promote_prompt_graph` | verified pass binding and champion comparison | unverified output or author preference |

## CONTROLLER TESTS

1. Exactly six model prompts exist and all are referenced once in `MODEL NODES`.
2. No prompt or node named `challenge_review` or `final_review` exists.
3. Every external QA path invokes the exact skill-owned `qa_gate.py`.
4. No graph node other than the gate process writes under `QA/`.
5. Exit codes `10`, `0`, `1`, and `2` map to distinct guarded states.
6. Gate criteria, focus, threshold, iteration bound, and transport are frozen
   before `START`.
7. `ROUND_OPEN` findings are captured before exposure and can only become
   selection pressure for a new immutable candidate.
8. QA artifact versions strictly increase in one session and bind candidate and
   artifact digests.
9. A child always recompiles and reevaluates; it inherits no parent verdict.
10. `QA_PASSED` cannot reach comparison until `verify` succeeds.
11. `QA_FAILED` runs verified postmortem and cannot reach promotion.
12. `QA_ERROR` is inconclusive and cannot reach another reviewer or promotion.
13. Prompt mutation and topology mutation quotas remain nonzero after generation
    zero.
14. Every parallel candidate and variation branch joins on its planned identity.
15. Every loop is bounded by generation, operator, QA-round, or repair counters.
16. Every non-promotion terminal preserves the prior champion.

## LOOP

Activate only nodes whose incoming guard is true and whose required state
projection is complete. Never infer an edge from prose, filenames, table order,
or a model recommendation. Persist each result through its declared reducer
before evaluating the next guard.

Continue generation and QA-round cycles only while their frozen counters allow.
When the standardized gate returns findings, evolve and reevaluate a new
candidate; never edit the reviewed candidate in place. When the gate returns a
terminal, follow its exact exit/state route. Only a verified `QA_PASSED` bound
to the unchanged candidate may enter champion comparison and promotion.
