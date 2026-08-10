# Plan 23 — Evolutionary graph engineering with a standardized Codex QA gate

## 1. Purpose

Plan 23 evolves prompt graphs as graphs. A candidate is not a folder of prompts
executed in filename order. It is an immutable genotype containing model nodes,
deterministic nodes, typed state, reducers, execution edges, context edges,
guards, joins, loop bounds, and terminal behavior.

The decisive external quality gate is standardized on the existing local skill:

```text
.claude/skills/qa-gate-codex-run
```

The graph must invoke that skill through its owned `scripts/qa_gate.py` protocol.
It must not replace the gate with bespoke challenge/final-review prompts, direct
Codex calls, self-review, a subagent verdict, or a hand-written file under
`QA/`.

## 2. Correction from Plan 22

Plan 22 represented evolution as a cyclic population graph, but its decisive
review path used two custom model prompts. That duplicated review machinery and
did not use the repository's standard independent QA protocol.

Plan 23 makes these corrections:

1. Remove `challenge_review` and `final_review` from the model-node inventory.
2. Add controller-owned QA-gate nodes for `start`, `round`, `verify`, and
   `postmortem`.
3. Freeze one observable criteria file for the entire run.
4. Let `qa_gate.py` construct reviewer prompts, call Codex, validate verdicts,
   preserve the witnessed session, write the hash-chained record, and own the
   terminal QA state.
5. Route `ROUND_OPEN` findings back into evolutionary selection. A newly
   evaluated candidate becomes the next version in the same QA session.
6. Require successful `verify` output before champion comparison or promotion.

## 3. Graph-engineering model

### 3.1 Candidate genotype

Each candidate contains these independently addressable gene groups:

```text
prompt_genes:
  model-node prompt bytes and response schemas

topology_genes:
  model and deterministic nodes
  typed input/output ports
  execution edges and guards
  context edges and projections
  state fields and reducers
  fan-out and join definitions
  loop counters and terminal routes
```

Prompt mutation holds `topology_genes` byte-identical. Topology mutation holds
`prompt_genes` byte-identical. Recombination records the parent of every
inherited gene. Local repair may touch only the controller-authorized defect
boundary.

### 3.2 Execution graph and context graph

The execution graph decides which node may activate next. The context graph
separately decides what information each model node may read. An execution edge
never grants access to a predecessor's complete conversation.

Every dynamic edge has one controller-owned guard. Every parallel branch has a
candidate-bound join. Every cycle has a counter and an honest exit. Every
terminal is explicit.

### 3.3 Immutable candidates and append-only evidence

A candidate ID binds one digest forever. Compilation, tests, internal reviews,
fitness, archive dispositions, QA submissions, and promotion records are
append-only. Repair, mutation, and recombination always create a new candidate
ID. The current champion is changed only by an atomic promotion operation.

## 4. Population evolution

### 4.1 Seed

Generation zero contains at least four materially different candidates. The
population must explore both prompt-contract alternatives and topology
alternatives; renaming or reordering prose is not diversity.

### 4.2 Evaluate

Every proposed candidate is compiled. Every compiled candidate then enters two
parallel branches:

- deterministic development and regression tests;
- an isolated internal graph/prompt review.

The branches join by candidate ID. Scoring cannot begin until every candidate
in the generation has either a complete joined result or a deterministic
compile failure.

### 4.3 Fitness and archive

The controller computes fitness from complete evidence. At minimum it preserves
these dimensions:

1. graph closure;
2. state/reducer correctness;
3. execution-edge correctness;
4. context isolation;
5. prompt-contract completeness;
6. task and regression performance;
7. protected non-regression;
8. mutation attribution;
9. population diversity;
10. normalized graph complexity.

Selection uses a constrained Pareto frontier. A protected-dimension failure
cannot be traded away by aggregate improvement.

### 4.4 Variation

Later generations allocate an exact offspring plan before fan-out. The plan
includes at least one prompt mutation and at least one topology mutation, plus
recombination when compatible parents exist. Local repair is permitted only for
admitted local findings.

The operators execute in parallel and converge at `merge_offspring`. The merge
rejects duplicate digests, missing lineage, mixed mutation scopes, and inherited
evaluation. A complete next population returns to compilation.

## 5. Standardized external QA gate

### 5.1 Authority boundary

The QA gate is an external graph component whose implementation is owned by:

```text
.claude/skills/qa-gate-codex-run/scripts/qa_gate.py
```

The evolutionary controller may prepare an artifact, criteria, grounding,
focus, and fixed invocation arguments. It may read the script's structured
stdout and exit code. It may not:

- build or soften Codex's review prompt;
- manufacture or reinterpret the verdict;
- write or edit anything under the gate-owned `QA/` directory;
- change threshold, criteria, transport, or iteration limit after `start`;
- substitute a direct Codex call if the gate errors;
- treat `QA_ERROR` as either pass or failure;
- promote from an unverified QA record.

### 5.2 Frozen standard

The run freezes `qa_criteria.v1.md`, its digest, and these arguments before
candidate authoring begins:

```text
threshold: blocker
max_iterations: 5
transport: app-server
focus: graph correctness, prompt-graph agreement, evolutionary integrity,
       authority separation, regression evidence, and promotion safety
allow_execution: false
```

The criteria are observable conditions. Grounding is evidence, never a second
criteria list. The candidate cannot author either.

### 5.3 Artifact projection and version lineage

The controller exports the first eligible frozen candidate as a self-contained
text artifact named `prompt_graph.v1.md` in an isolated QA workspace. The
artifact binds candidate ID/digest, prompts, state/reducers, execution graph,
context graph, lineage, compilation identity, public test evidence, and
fitness. It contains no hidden holdout answers, author conversation, rendered
media, or mutable path aliases.

If the gate returns `ROUND_OPEN`, the findings become admitted selection
pressure. Evolution continues through normal selection, variation, compilation,
testing, review, scoring, and archive updates. The next eligible frozen
candidate is exported as `prompt_graph.vN.md`, where `N` is strictly greater
than the prior QA artifact version, then submitted with `qa_gate.py round` in
the same QA session. The gate moves superseded versions to `deprecated/`.

Internal candidate ancestry and QA artifact version are distinct fields. The
QA version means "next artifact shown to the same gate"; it does not erase the
candidate's population lineage.

### 5.4 Exact gate operations

First submission:

```text
python3 .claude/skills/qa-gate-codex-run/scripts/qa_gate.py start
  --artifact <qa-workspace>/prompt_graph.v1.md
  --criteria-file plans/23_graph_eng_evol_01/qa_criteria.v1.md
  --focus "graph correctness, prompt-graph agreement, evolutionary integrity,
           authority separation, regression evidence, and promotion safety"
  --threshold blocker
  --max-iterations 5
  --transport app-server
  --ground plans/23_graph_eng_evol_01/evolutionary_approach/evolution_graph_approach.v1.md
  --ground plans/23_graph_eng_evol_01/run.prompt.md
```

Later artifact submission:

```text
python3 .claude/skills/qa-gate-codex-run/scripts/qa_gate.py round
  --qa-dir <qa-workspace>/QA
  --artifact <qa-workspace>/prompt_graph.vN.md
```

A rebuttal is legal only when it cites the frozen criterion and contests a
misclassification. It uses `round --rebuttal` and may not accompany an
unchanged resubmission without a substantive criterion-based argument.

Only a `ROUND_OPEN` lineage resumes the same QA session. If a verified pass
cannot promote because the external champion changed concurrently, the
controller closes that QA attempt. Continued evolution opens a new isolated QA
workspace and a fresh gate session at `prompt_graph.v1.md`; it never tries to
`round` a terminal session.

Every terminal gate result is followed by:

```text
python3 .claude/skills/qa-gate-codex-run/scripts/qa_gate.py verify
  --qa-dir <qa-workspace>/QA
```

On `QA_FAILED`, and only after record verification, run:

```text
python3 .claude/skills/qa-gate-codex-run/scripts/qa_gate.py postmortem
  --qa-dir <qa-workspace>/QA
```

### 5.5 Exit-code routing

| Exit | Gate state | Graph route |
| --- | --- | --- |
| `10` | `ROUND_OPEN` | Capture threshold findings and route them to `select_parents`; do not promote. |
| `0` | `QA_PASSED` | Run `verify`; only verified pass may reach champion comparison. |
| `1` | `QA_FAILED` | Run `verify`, then `postmortem`; terminate without promotion. |
| `2` | `QA_ERROR` | Run `verify`, then terminate as unverified; do not substitute another reviewer. |
| other | usage/system error | Fail closed as `SYSTEM_FAILURE`. |

`verify` must confirm the hash chain, exact witnessed requests and responses,
turn/session binding, expected sandbox, working directory, workspace roots, and
artifact identity. Any verification problem blocks promotion.

### 5.6 Why one gate replaces two review prompts

The QA skill already supplies the standard reviewer prompt, schema enforcement,
severity threshold, resumed-session honesty audit, stall detection, terminal
states, Codex-session witness, hash chain, verification, and independent failure
diagnosis. Adding custom challenge and final-review prompts would create two
competing sources of QA truth and defeat standardization.

## 6. Execution topology

```text
START
  -> seed_population
  -> compile_population
  -> dispatch_candidate_checks
       -> test_candidate -----------+
       -> review_candidate ---------+-> join_candidate_checks
  -> join_population
  -> score_population
  -> update_archive
  -> decide_generation
       | eligible + no open QA session
       -> prepare_qa_artifact -> qa_gate_start
       | eligible + QA round open
       -> prepare_qa_revision -> qa_gate_round
       | no eligible candidate + budget
       -> select_parents

qa_gate_start | qa_gate_round
  | exit 10 ROUND_OPEN
  -> capture_qa_findings -> select_parents
  | exit 0 QA_PASSED
  -> qa_gate_verify -> compare_with_champion -> promote_prompt_graph
  | exit 1 QA_FAILED
  -> qa_gate_verify -> qa_gate_postmortem -> QA_GATE_FAILED
  | exit 2 QA_ERROR
  -> qa_gate_verify -> QA_ERROR

select_parents
  -> repair_candidate --------+
  -> mutate_prompts -----------+
  -> mutate_topology ----------+-> merge_offspring
  -> recombine_candidates -----+
  -> compile_population
```

This graph is cyclic. Prompt filenames therefore remain semantic and unnumbered;
execution order belongs to edges and guards.

## 7. Context isolation

| Node class | May receive | Must not receive |
| --- | --- | --- |
| Candidate authors | approach, public cases, admitted evidence, allowed genes | hidden holdouts, QA conversation, QA directory writes |
| Internal reviewer | one compiled candidate and internal rubric | sibling candidates, author history, QA session |
| QA preparation | one frozen eligible candidate and public evidence | mutable candidates, hidden answers, author conversation |
| `qa_gate.py` | frozen artifact, criteria, focus, grounding | controller verdict suggestions, mutable champion |
| Selection | archive fitness and admitted QA findings | raw private Codex session or hidden grounds |
| Promotion | verified QA pass and champion comparison evidence | author preference or unverified verdict |

The controller may disclose structured threshold findings after the gate has
captured them. It does not disclose raw reviewer chain-of-thought or permit
candidate prompts to address the reviewer directly.

## 8. Termination and promotion

The run reaches exactly one of:

- `PROMOTED`;
- `CONVERGENCE_EXHAUSTED`;
- `QA_GATE_FAILED`;
- `QA_ERROR`;
- `QA_INTEGRITY_BREACH`;
- `SYSTEM_FAILURE`;
- `INTERRUPTED`.

Promotion requires all of the following:

1. immutable candidate identity and complete lineage;
2. successful compilation;
3. complete internal evaluation and protected non-regression;
4. constrained-Pareto eligibility against the current champion;
5. `qa_gate.py` terminal state `QA_PASSED`;
6. successful `qa_gate.py verify` bound to the same artifact/session;
7. unchanged candidate digest after the reviewed round;
8. atomic compare-and-swap of the champion pointer.

No generation or QA budget exhaustion converts failure into success. The
previous champion remains unchanged on every non-promotion terminal.

## 9. Acceptance tests for Plan 23

1. No prompt file implements external challenge or final review.
2. The only decisive external QA authority is
   `.claude/skills/qa-gate-codex-run/scripts/qa_gate.py`.
3. The graph declares `start`, `round`, `verify`, and `postmortem` behavior.
4. Exit codes `0`, `1`, `2`, and `10` have distinct guarded routes.
5. `ROUND_OPEN` creates selection pressure and never edits the reviewed
   candidate.
6. Every resubmission uses a strictly newer artifact version in the same QA
   session.
7. The controller never writes under `QA/`.
8. Criteria, focus, severity threshold, transport, and maximum rounds freeze
   before the first gate call.
9. `QA_ERROR` remains inconclusive and blocks promotion.
10. `QA_FAILED` runs verified postmortem and blocks promotion.
11. A claimed pass without successful `verify` blocks promotion.
12. The graph retains population, prompt mutation, topology mutation,
    recombination, candidate-bound joins, Pareto selection, and bounded cycles.
