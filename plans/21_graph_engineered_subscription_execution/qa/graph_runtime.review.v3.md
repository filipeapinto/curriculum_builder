# Plan 21 graph-formalism and durable-runtime review — v3

## Verdict

**CHANGES REQUIRED — 1 Critical, 3 High, 1 Medium.** The exact current graph
passes the shipped bootstrap and expanded self-test, and the round-2 structural
repairs are real. This is still not a PASS. The immutable phase event that alone
selects graph edges is semantically fail-open: it validates `PASS` with failing
or zero tests, and every PASS guard checks only the asserted outcome. Resume
events are also unbound to the interrupted checkpoint and have no pre-activation
producer, producer/state references can point forward or to nonexistent local
contracts, and phase idempotency templates are not compiled against typed state.

The plan's exit rule requires zero unresolved Critical or High findings. This
verdict is based on executable counterexamples, not on comparison with earlier
finding counts.

## Executed checks

Both shipped commands passed from the repository root:

```text
python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan.py
plan21_bootstrap=PASS

python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan.py --self-test
plan21_bootstrap=PASS
```

I then ran independent in-memory mutations through the shipped `validate()` and
validated adversarial events directly against the shipped schemas. No source
artifact was changed.

The graph validator accepted all of these mutations:

- a nonexistent local node input schema;
- a nonexistent local state-field schema;
- `contract://P999/not_real` as an authorized input;
- P1 consuming a P6-produced artifact after adding P6 only to `context_from`;
- P1 reading P6 state after adding the bidirectional reader declarations but no
  P6 context or dependency;
- an `attempt` guard predicate whose equality value is a string even though the
  event field is an integer;
- the same constant idempotency key on every node;
- an idempotency placeholder absent from every typed state/event field; and
- changing a repair limit from 2 to 99 despite the denominator contract's
  maximum of 2.

Direct event-schema probes also showed the following are schema-valid:

- `outcome: PASS` with a `FAIL` test and `failure_class: FACTORY_DEFECT`;
- `outcome: PASS` with empty `test_results` and empty `artifact_hashes`;
- `CONVERGENCE_EXHAUSTED` with `failure_class: POLICY_VIOLATION`;
- `PAUSED_PREREQUISITE` with unit-domain `EXTERNAL_FACT_BLOCK`; and
- `RESUME` naming P6 with no interruption/checkpoint/event binding.

Finally, the strengthened coverage-denominator schema still accepted a record
whose one-element arrays had aggregate counts of 999, and accepted duplicate
mutation records with the same id.

## V2 remediation audit

| V2 finding | Current disposition |
|---|---|
| Critical — missing exhaustion/resume graph edges | **Structural edge gap fixed.** Exhaustion, prerequisite-pause, interrupt, and return edges now exist and are bootstrap-tested. Resume admission is still semantically incomplete (Finding 2). |
| High — bootstrap false negatives | **Named v2 mutations fixed.** The self-test now covers the exact missing-route, dependency/context, guard-duplication, terminal-kind, and duplicate-owner cases. Typed guard values and producer/data topology remain unchecked (Findings 1 and 3). |
| High — untyped state/P0 contracts | **Mostly fixed.** Closed runtime, phase-result, P0 bundle, baseline, identity, and state-field declarations exist. Phase-result cross-field semantics and producer ordering remain unsafe (Findings 1 and 3). |
| High — vacuous denominator | **Nonempty/numeric shape fixed; integrity partial.** Arrays and threshold fields are nonempty and typed, but category/aggregate/uniqueness invariants remain external and under-specified (Finding 5). |
| High — P6 `BLOCKED` on QA exhaustion | **Fixed.** P6 now emits `CONVERGENCE_EXHAUSTED` and routes to plan `SYSTEM_FAILURE`. |
| Medium — P2 side effects/idempotency | **P2-specific issue fixed.** P2 is `mixed` and its prompt defines composed build/Claude/Codex replay. General idempotency-template validation remains missing (Finding 4). |

## Findings

### 1. Critical — A schema-valid phase event can select PASS while its tests fail or never ran

**Evidence.**

- The plan makes immutable phase events the sole edge authority. P_ALL says each
  attempt writes a `contracts/phase_result.schema.v1.json` event and registered
  predicates over that event select the edge; Markdown/file presence cannot do
  so
  (`plans/21_graph_engineered_subscription_execution/prompts/P_ALL_graph_orchestrator.prompt.v1.md:30-38`).
- The phase-result schema requires `outcome`, `failure_class`, `test_results`, and
  hashes, but it gives `test_results` no `minItems` and `artifact_hashes` no
  `minProperties`
  (`plans/21_graph_engineered_subscription_execution/contracts/phase_result.schema.v1.json:5-30`).
  Its conditionals constrain resume target, repeat signature, and the presence of
  a string failure class for some outcomes only (`:32-35`). There is no rule that
  `PASS` requires all declared tests present and `status: PASS`, nonempty
  evidence/artifact hashes, `failure_class: null`, or `repeat_signature: null`.
- Direct Draft 2020-12 validation accepted both (a) a P1 `PASS` event carrying a
  `FAIL` test and `FACTORY_DEFECT`, and (b) a P1 `PASS` event with zero tests and
  zero artifacts.
- Every PASS guard checks only `node_id` and `outcome`, for example P1 at
  `graph_engineered_subscription_execution.plan.v1.yaml:111-117`. The bootstrap
  merely verifies edge outcome equals the guard's outcome predicate and that the
  guard binds its source node (`tools/validate_plan.py:82-91`); it never derives
  PASS from test evidence.
- The node's `tests` property is a prose range string, not an event-schema
  denominator (`graph_engineered_subscription_execution.schema.v1.json:111`;
  representative plan nodes at `plan.v1.yaml:187,216,245`). Nothing proves the
  event contains every declared test id.

**Impact.** A model-orchestrated phase can emit a schema-valid PASS assertion
despite deterministic test failure or non-execution, and deterministic routing
will take its success edge. This bypasses the goal-test-loop gate and can advance
all the way to `PLAN_APPROVED`; it directly violates GE-03, GE-05, GE-09, and the
plan's “models never own transitions or acceptance” invariant.

**Required remediation.** Make PASS admission a code-derived event, not an
executor-provided assertion. Bind each node to a machine-readable required-test
set and enforce exact test-id totality; for PASS require every required test
present exactly once, all PASS, non-null evidence hashes, required artifact
hashes present, `failure_class: null`, `repeat_signature: null`, and
`resume_node_id: null`. Add conditional schemas for every outcome/failure-class
pair and mutation tests for failing, missing, duplicate, NOT_RUN, extra, and
hashless tests. The PASS guard should consume the deterministic aggregate field
or recompute it, not trust `outcome: PASS` alone.

### 2. High — Resume edges are explicit but RESUME events are neither bound to the interrupted checkpoint nor owned before activation

**Evidence.**

- The manifest now has resume edges from the shared `INTERRUPTED` state to every
  phase and from `PAUSED_PREREQUISITE` to P2/P6
  (`plans/21_graph_engineered_subscription_execution/graph_engineered_subscription_execution.plan.v1.yaml:375-399`).
- A RESUME event contains only ordinary phase fields plus `resume_node_id`; the
  closed schema has no interrupted-event hash, pause reason, source node,
  checkpoint hash, last-valid-attempt, or graph/prompt digest fields
  (`contracts/phase_result.schema.v1.json:5-35`). Direct validation therefore
  accepted a RESUME-to-P6 event with no checkpoint binding.
- The RESUME guards check target `node_id`, `outcome: RESUME`, and
  `resume_node_id` only (`plan.v1.yaml:148-154`). P_ALL states that guard
  predicates are evaluated over that event (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:32-38`).
  There is no predicate proving the current run was interrupted at that target
  or that the named checkpoint is the last valid one.
- Each phase owns its own event output (for example P6 at
  `plan.v1.yaml:334-339`), but a RESUME event is needed to activate that phase.
  P_ALL writes no artifact (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:42-43`),
  and neither pause state is a typed node/owner. The graph therefore does not
  name who may author/admit the pre-activation RESUME event.

**Impact.** The explicit edges fix the prior missing-edge defect but not durable
resume authority. An unbound or operator-authored event can choose a return edge
without proving the interrupted phase/checkpoint, while strict output ownership
leaves no authorized component able to write that event. This breaks GE-03,
GE-07, GE-11, and cold-process replay semantics.

**Required remediation.** Add a deterministic pause/resume controller node or
checkpoint service as the sole RESUME-event producer. Persist a typed pause
record binding run, source node, source event hash, last valid checkpoint hash,
graph/prompt/policy/schema digests, reason, and the one legal return node. Require
the RESUME event to reference that record, and make the guard compare every
binding. Negative-test wrong target, stale run/digest, absent/corrupt pause
record, replayed resume, and resume written by a phase/model.

### 3. High — Artifact and state resolution checks ownership syntax but not existence or producer-before-consumer topology

**Evidence.**

- `artifact_owner()` validates only `artifact://` references and confirms the
  named producer declares a suffix-matching output
  (`plans/21_graph_engineered_subscription_execution/tools/validate_plan.py:142-160`).
  Local schema paths and `contract://` references return no resolution result;
  producer order is never checked.
- Independent mutations proved the validator accepts nonexistent local input and
  state schemas, an unregistered `contract://P999/not_real` input, and P1
  consuming a P6 artifact after merely adding P6 to `context_from`. That last
  graph is impossible at P1 execution even though the control dependency spine
  remains acyclic.
- State reader/writer declarations are checked bidirectionally
  (`tools/validate_plan.py:178-195`), but a reader is not required to include the
  writer in its context/dependency ancestry. Adding P1 as a reader of the
  P6-produced state field to both sides passed without P6 context.
- The current manifest itself mixes strict future-artifact references with
  unresolved contract references such as P2's
  `contract://P1/compiled_graph` (`plan.v1.yaml:227-240`) and P6's
  `contract://P5/evaluation_subgraph` (`:332-343`). The P0 baseline selector
  schema defines concrete path maps only for P4/P5/P6 scope categories
  (`contracts/baseline_contract.schema.v1.json:11-17`), not these P1/P2/P5
  producer aliases.
- P1-T02 explicitly says a schema reference must resolve to an existing
  authorized file or an earlier producer-owned artifact
  (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:16-18`), but the shipped
  pre-P0 assurance layer does not enforce the same rule.

**Impact.** A graph can compile at bootstrap with missing schemas, future-data
dependencies, or undeclared context flow. That permits impossible execution and
context leakage despite correct-looking owner labels, weakening GE-02, GE-05,
GE-06, and GE-08.

**Required remediation.** Resolve every local schema path and define a closed
registry for every `contract://` namespace. Require each artifact/state producer
to be a strict predecessor of every consumer in both the control and permitted
context graphs; reject future/cyclic dataflow. Replace suffix matching with
canonical exact output identities. Add the independent missing-local,
unknown-contract, future-producer, and future-state mutations to the bootstrap
self-test.

### 4. High — Idempotency keys are unchecked strings and several current templates reference no typed phase state

**Evidence.**

- The node schema constrains `idempotency_key` only as a string of length ten
  (`plans/21_graph_engineered_subscription_execution/graph_engineered_subscription_execution.schema.v1.json:109-110`).
  `validate()` performs no parsing, placeholder binding, uniqueness-domain, or
  side-effect coverage check.
- Independent mutation showed that the same constant key on all seven nodes and
  `{not_a_state_field}:P2` both pass validation.
- Current templates contain placeholders absent from the typed runtime-state,
  phase-result, and state-field registries: P2 uses `phase_attempt`, P4 uses
  `migration_unit`, P5 uses `candidate_digest`/`evaluator_id`, and P6 uses
  `test_id` (`graph_engineered_subscription_execution.plan.v1.yaml:244,297,321,346`).
  The phase-result schema exposes `attempt`, not `phase_attempt`
  (`contracts/phase_result.schema.v1.json:5-15`), and none of the other
  placeholders appears in `state_fields` (`plan.v1.yaml:59-108`) or
  `runtime_state.schema.v1.json:6-21`.
- P2's prompt now correctly specifies composed phase replay for its known
  subtasks (`prompts/P2_subscription_worker_adapter.prompt.v1.md:41-42`), but P4,
  P5, and P6 are also multi-effect phase nodes and do not define equivalent
  phase-result admission keys.

**Impact.** The compiler cannot derive a stable key from typed checkpoint state,
prove two logical tasks cannot collide, or prove a cold replay reuses the same
key. A syntactically present key can therefore satisfy P1-T10 while offering no
idempotency, violating GE-02 and GE-07.

**Required remediation.** Define a typed idempotency-key expression grammar and
an allowlist of fields available at node activation. Compile every placeholder,
require a stable phase-level key plus separately declared subtask keys for mixed
nodes, and prove key-domain separation across nodes/runs/artifacts. Add
constant-key, cross-node collision, unknown-placeholder, attempt-renumbering,
and cold-replay mutations.

### 5. Medium — The denominator is nonempty but its counts, record identities, and required mutation categories are not schema-enforced

**Evidence.**

- The revised denominator schema now requires nonempty record arrays and numeric
  thresholds, correctly resolving the v2 empty-list defect
  (`plans/21_graph_engineered_subscription_execution/contracts/coverage_denominator.schema.v1.json:6-20`).
- It does not require unique record ids, does not type mutation categories, and
  does not relate aggregate values to array lengths. Direct validation accepted
  one-element category arrays with every aggregate set to 999, then accepted a
  duplicated mutation record/id.
- P1-T15 names the required mutation categories
  (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:30`), and P0-T11 requires
  an altered aggregate to fail
  (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:35`), but the denominator
  artifact has no typed `kind` field from which those tests can prove category
  totality. The future census/check code must infer it from free-form ids.

**Impact.** A diligent implementation can add external checks, but the frozen
denominator itself does not carry enough typed information for independent
recomputation. Duplicate or missing mutation classes can still produce
schema-valid release evidence.

**Required remediation.** Add unique typed ids and a closed mutation-kind enum,
require all mandated kinds, and make a deterministic validator recompute every
aggregate from canonical records. Bind records to exact source ids/hashes and
test duplicate ids, missing kinds, count mismatch, and source-digest mismatch.

## Exit decision

The exhaustion routes, pause/interrupt edges, typed state registry, baseline
scope schemas, P2 composed replay, and P6 QA-failure routing are genuine
improvements. They do not compensate for a PASS event that can contradict its
own test evidence.

**FAIL / CHANGES REQUIRED.** Resolve the Critical and all High findings, add the
executed counterexamples to the shipped mutation suite, and rerun validation and
independent QA against the revised exact bytes. Do not approve Plan 21 based on
round count or reduced totals.
