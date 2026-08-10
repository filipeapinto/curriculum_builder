# Plan 21 graph-formalism and durable-runtime review — v1

## Verdict

**CHANGES REQUIRED — 3 Critical, 3 High, 1 Medium.** Plan 21 correctly adopts
the August 2026 vocabulary of compiled topology, typed state, deterministic
guards, durable checkpoints, independent evaluation, targeted repair, and
process-level evidence. Its implementation prompts also contain many strong
positive and negative test intentions. The shipped plan graph is not yet an
executable instance of that architecture, however. It cannot bootstrap its own
compiler, cannot represent two of its declared terminals or any repair/resume
edge, routes non-domain failures to `BLOCKED` contrary to its own invariant, and
deadlocks before P3 because P2 requires a migration that only P4 may perform.

This is therefore **not a PASS**. Under the declared exit rule, a PASS requires
zero unresolved Critical or High findings.

## Review basis

I reviewed the August 2026 research rubric, Plan 20 gap assessment, Plan 21
schema and YAML, all Plan 21 prompts, Plan 19 P0-P6 prompts where they define
the inherited state/runtime contract, and all three Plan 20 QA rounds. I also
validated the YAML against its JSON Schema and ran in-memory negative mutations.
The unmodified schema accepted a duplicate node id, a dangling `P999` edge, an
orphaned graph with no P6 terminal path, and an added unbounded P6-to-P0 cycle.
That is expected of a shape schema only, but it proves schema validation cannot
serve as the pre-P1 compilation step the orchestrator requires.

## Findings

### 1. Critical — The execution graph cannot bootstrap: P0 requires a compiler that P1 has not built, and the model-bearing orchestrator is outside the graph

**Evidence.**

- `prompts/P_ALL_graph_orchestrator.prompt.v1.md:13-19` requires the plan graph
  to be compiled before activating *a node*, which includes P0.
- `graph_engineered_subscription_execution.plan.v1.yaml:67-76` makes the graph
  compiler a P1 deliverable, and `:71` makes P1 depend on P0. No
  `runtime/prompt_graph.py`, `schemas/prompt_graph.schema.v1.json`, or
  `tests/runtime/test_prompt_graph.py` exists before P1.
- `prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:31-33` does not
  self-compile Plan 21 until P1-T12, after P1 has already been activated and
  implemented.
- P0-T01 is only JSON Schema validation
  (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:31`), while the current
  schema's node/edge arrays and shallow edge fields
  (`graph_engineered_subscription_execution.schema.v1.json:43-51,74-99`) do not
  enforce uniqueness, reference resolution, reachability, cycle safety, or
  failure-edge totality. The negative mutation probe described above confirms
  all four unsafe shapes pass this validation.
- The entity that actually activates nodes, reads their narrative result fields,
  and selects edges is `prompts/P_ALL_graph_orchestrator.prompt.v1.md`, but it is
  not a node in `graph_engineered_subscription_execution.plan.v1.yaml:52-162`.
  It consequently has no typed input/output schema, owner, receipt, checkpoint,
  idempotency contract, or compiled incoming/outgoing edge.

**Impact.** The plan has no conforming first transition. Running P0/P1 through
the prose orchestrator makes an uncompiled model prompt the effective control
plane; refusing uncompiled execution means the plan never starts. Either choice
violates GE-01, GE-03, GE-05, GE-07, and GE-11 and recreates Plan 20's implicit
orchestration problem at the meta-plan layer.

**Required remediation.** Ship a deterministic bootstrap validator/compiler and
its biting tests as an already-present Plan 21 planning artifact, or explicitly
define a minimal non-model bootstrap state that validates and compiles the phase
graph before P0. Put orchestration/activation inside the typed runtime contract
(or make it a code-owned runner, not a prompt). P1 may then build the production
graph compiler, but P1-T12 must no longer be the first point at which the running
plan can be proven safe.

### 2. Critical — Terminal and failure routing is internally inconsistent and makes `SYSTEM_FAILURE` and `INTERRUPTED` unreachable

**Evidence.**

- The Plan 21 state vocabulary declares `ACCEPTED`, `BLOCKED`, `SYSTEM_FAILURE`,
  and `INTERRUPTED`
  (`graph_engineered_subscription_execution.plan.v1.yaml:39-43`).
- The edge schema permits only `APPROVED` or `BLOCKED` as terminal targets
  (`graph_engineered_subscription_execution.schema.v1.json:90-99`). The YAML
  uses `APPROVED`, not declared `ACCEPTED`, at
  `graph_engineered_subscription_execution.plan.v1.yaml:172`, and its graph
  invariant repeats `APPROVED` at `:180-182`. No edge can target declared
  `SYSTEM_FAILURE` or `INTERRUPTED`.
- Every phase stop condition routes to `BLOCKED`
  (`graph_engineered_subscription_execution.plan.v1.yaml:173-179`), including
  compiler/design defects, unprovable isolation, unsafe joins, and missing QA
  evidence. Yet the same plan reserves `BLOCKED` for a named unavailable
  external safety-critical fact (`:188-189`).
- P2 explicitly treats missing Claude authentication as its expected stop
  (`prompts/P2_subscription_worker_adapter.prompt.v1.md:51-54`; plan YAML
  `:97-99`), while P5-T20 says judge unavailability and factory defects must not
  masquerade as a domain block
  (`prompts/P5_evaluator_optimizer_acceptance.prompt.v1.md:35`). Plan 19's
  inherited rule likewise says tool/model/factory defects are system failures,
  never `BLOCKED`
  (`plans/19_curriculum_factory_production_loop_closure/prompts/P3_production_unit_state_machine.prompt.v1.md:169-174`).

**Impact.** A conforming compiler must reject the Plan 21 graph for undeclared
`APPROVED`, missing edges to declared terminals, and contradiction between the
failure edges and the `BLOCKED` invariant. A permissive compiler instead
collapses authentication, implementation defects, interrupts, and genuine
external fact absence into one misleading state. That breaks GE-03, GE-05,
GE-07, and the historical false-block controls.

**Required remediation.** Separate phase-run status from curriculum-domain
terminal status if both are needed, then use one canonical vocabulary in the
schema, manifest, events, and prompts. Add explicit code-owned edges for
interrupt, resumable pause, factory/system failure, external-fact block, and
convergence exhaustion. Restrict `BLOCKED` to its declared evidence shape; route
missing authentication and implementation/runtime defects to the appropriate
non-domain terminal.

### 3. Critical — P2 cannot pass within its authorized scope, so the P1/P2 join can never activate P3

**Evidence.**

- P2 depends only on P0 and may write only the new adapter, its schemas/test, and
  its result (`graph_engineered_subscription_execution.plan.v1.yaml:83-99`).
- P2-T02 nevertheless requires **every production model role** to import the
  shared adapter and requires a scan to fail on direct Claude, Codex, or Gemini
  production subprocesses
  (`prompts/P2_subscription_worker_adapter.prompt.v1.md:25-27`). The current
  repository still has the direct Gemini production mechanism in
  `runtime/capability_cycle.py` and imports its provider-specific boundary from
  `runtime/gemini.py`; these are the exact Plan 20 paths Plan 21 intends to
  retire.
- Migrating all production roles and retiring Gemini is assigned to P4
  (`prompts/P4_curriculum_graph_migration.prompt.v1.md:10-15,22-24`), and P4 is
  downstream of P3 (`graph_engineered_subscription_execution.plan.v1.yaml:117-132`).
- P3 is an all-of join that cannot start until P1 and P2 pass
  (`graph_engineered_subscription_execution.plan.v1.yaml:167-169` and
  `prompts/P_ALL_graph_orchestrator.prompt.v1.md:21-23`).

**Impact.** P2-T02 must fail against the live pre-P4 tree, but P2 is forbidden to
make the changes needed to pass it. Therefore P2 never emits a passing result,
P3 never starts, and P4 never reaches the migration that would make P2-T02 true.
This is an executable dependency deadlock, not merely an imprecise test.

**Required remediation.** In P2, test that the new adapter itself provides one
normalized interface and has no provider-specific bypass within its own
boundary. Move the repository-wide caller/reachability scan exclusively to P4
(where P4-T04 already states it), or authorize and schedule the caller migration
before P2 completion. Preserve a final P6 scan proving no old production route
remains reachable.

### 4. High — The shipped IR cannot encode the node, state, guard, join, reducer, and loop semantics that Plan 21 says it compiles

**Evidence.**

- GE-02 requires role, goal, authorized inputs/outputs, schemas, owner, and
  side-effect class; GE-06 requires typed state and deterministic reducers
  (`research/graph_engineering_sota.2026-08.md:143-150`). P1 repeats those
  requirements and adds idempotency strategy
  (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:3-13`).
- The shipped node schema requires only id, prompt, role, goal, dependencies,
  outputs, test prose, loop prose, and stop-condition prose
  (`graph_engineered_subscription_execution.schema.v1.json:74-88`). It has no
  authorized inputs, input/output schema references, owner, side-effect class,
  idempotency strategy, context predecessors, or state-write declaration.
- `state_schema` is only three lists of strings, not a typed schema or reducer
  registry (`graph_engineered_subscription_execution.schema.v1.json:33-41`;
  plan YAML `:23-51`).
- Edge `kind` supports only `start`, `success`, `join`, and `failure`
  (`graph_engineered_subscription_execution.schema.v1.json:90-99`). It cannot
  represent the fixed, conditional, fan-out, bounded-repair, interrupt, resume,
  or exhausted edge types P1 mandates
  (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:7-13`). The phase
  `loop` fields are prose strings, not graph edges.
- The P0 fan-out is inferred from two ordinary success edges, and the all-of join
  is inferred from two incoming edges carrying the same free-form guard text
  (`graph_engineered_subscription_execution.plan.v1.yaml:164-169`). There is no
  join id, membership set, contribution schema, reducer name, identity element,
  conflict policy, or atomic activation rule despite the claimed invariant at
  `:185-187`.

**Impact.** P1-T12's Plan 21 self-compile cannot both enforce P1-T04 through
P1-T11 and accept the current manifest. If implementation silently enriches the
manifest from prompt prose, the prose/model again owns semantics the IR was
supposed to make code-owned. This blocks GE-01 through GE-07 rather than merely
deferring their implementation.

**Required remediation.** Extend the plan IR and manifest now with explicit
entry/terminal declarations; typed node ports and state writes; artifact/check
ownership; side-effect/idempotency metadata; executable guard identifiers with
declared exhaustive outcomes; named fan-out/join groups; reducer specifications;
and first-class retry, repair, interrupt, resume, exhaustion, and terminal edges.
Make the corrected manifest pass the same compiler and mutation suite required
of future production graphs.

### 5. High — Parallel P1/P2 perform an unauthorized, multiply-owned append to the same log with no reducer or idempotency semantics

**Evidence.**

- The plan says each phase prompt authorizes only its declared outputs
  (`graph_engineered_subscription_execution.plan.v1.yaml:12-14`). No node's
  `authorized_outputs` includes `plans.log.md`; for P1 and P2 see `:72-76` and
  `:88-93`.
- Nevertheless, P0 and every later node prompt orders the executor to append the
  log (P0 `prompts/P0_contract_and_evidence_freeze.prompt.v1.md:53-55`; P1
  `prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:43-46`; P2
  `prompts/P2_subscription_worker_adapter.prompt.v1.md:51-55`; P3
  `prompts/P3_durable_graph_runtime.prompt.v1.md:40-43`; P4
  `prompts/P4_curriculum_graph_migration.prompt.v1.md:52-56`; P5
  `prompts/P5_evaluator_optimizer_acceptance.prompt.v1.md:47-51`; P6
  `prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:40-44`).
- P1 and P2 may execute concurrently
  (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:21-23`). Their concurrent
  append side effect has no single owner, idempotency key, atomic writer, event
  schema, ordering rule, or deterministic reducer. That conflicts directly with
  P1-T06/P1-T09
  (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:25-29`) and the
  deterministic parallel invariant
  (`graph_engineered_subscription_execution.plan.v1.yaml:185-190`).

**Impact.** A correct self-compiler should reject the graph for undeclared output
and ambiguous ownership. If not rejected, completion order makes log bytes and
hashes nondeterministic; replay can duplicate entries, and a crash can separate a
passing result from its log record. This violates GE-06, GE-07, GE-10, and GE-11.

**Required remediation.** Either give each node an immutable per-node event/result
artifact and deterministically materialize the human log after the join, or define
one code-owned append service with atomic records, schema, idempotency key
`(run_id,node_id,attempt,event_type)`, and deterministic projection semantics.
Declare that service/output in the graph and test concurrent completion, crash,
and replay permutations.

### 6. High — “Invalid checkpoint” is replayable in Plan 21, regressing the inherited stale-hash fail-closed rule

**Evidence.**

- P3-T12 says resume starts at the first “missing/invalid node”
  (`prompts/P3_durable_graph_runtime.prompt.v1.md:23-25`), and P4-T14 repeats
  “first invalid/missing checkpoint” with no manual repair
  (`prompts/P4_curriculum_graph_migration.prompt.v1.md:31-33`). Neither test
  distinguishes a cleanly absent/incomplete checkpoint from a present checkpoint
  whose recorded input/output hash fails validation.
- The inherited Plan 19 negative control is explicit: a checkpoint whose recorded
  hash no longer matches disk **halts** and is never silently repaired or treated
  as a valid prefix
  (`plans/19_curriculum_factory_production_loop_closure/prompts/P3_production_unit_state_machine.prompt.v1.md:180-190`). Plan 19 P6 also forbids continuing
  past an unresolved hash mismatch
  (`plans/19_curriculum_factory_production_loop_closure/prompts/P6_release_proof_debt_reconciliation.prompt.v1.md:123-127`).
- Plan 21 P3-T13 blocks only changed graph/prompt/policy/schema/route digests
  (`prompts/P3_durable_graph_runtime.prompt.v1.md:24`); it does not close the
  artifact/checkpoint-hash case. P3-T17 proves hash linkage but does not prescribe
  fail-closed resume behavior (`:28`).

**Impact.** An implementation can satisfy the literal Plan 21 resume tests by
re-running from a tampered or corrupted checkpoint. That destroys evidence of
unexpected mutation and can overwrite non-accepted-but-valid downstream work,
reproducing a historical runtime-integrity class the migration promises to
preserve.

**Required remediation.** Define distinct checkpoint states and edges:
`ABSENT/INCOMPLETE` may replay under the original idempotency key;
`HASH_MISMATCH/CORRUPT/UNAUTHORIZED_MUTATION` must fail closed to a named system
terminal and preserve forensic bytes; a declared version migration creates a new
run lineage. Add separate biting tests for each state, including an on-disk byte
flip, missing checkpoint, crash-truncated checkpoint, and version mismatch.

### 7. Medium — Several “every boundary/path” tests have no independent coverage denominator and can pass vacuously

**Evidence.**

- P3-T18 requests process death at “every boundary”
  (`prompts/P3_durable_graph_runtime.prompt.v1.md:29`), while P6-T04 through
  P6-T06 request every legal edge, guard outcome, and crash boundary
  (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:14-16`). P6-T18
  fails only on unexplained redundancy (`:28`) without a policy threshold or
  deterministic expected range.
- The plan does not freeze an independent boundary inventory, guard truth table,
  edge/path coverage manifest, or mutation set before the runtime/compiler under
  test emits its own graph. If that implementation omits a guard, side-effect
  boundary, or edge, its self-reported denominator shrinks and “100%” can still
  pass.
- By contrast, P0-T10 has concrete biting mutations
  (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:40`) and Plan 19 names
  exact runtime refusals and mutation expectations. The later Plan 21 totality
  checks do not consistently carry that precision forward.

**Impact.** Dynamic tests may verify all *reported* paths while missing a required
path or durability boundary, weakening GE-12 and GE-13 despite clean coverage
figures.

**Required remediation.** Freeze a canonical guard/boundary/side-effect inventory
from the corrected IR before runtime execution, require coverage against that
independent denominator, and add mutation operators that delete each failure
edge, invert each guard, omit each join member, make each reducer order-sensitive,
and crash immediately before/after each admission and checkpoint commit. Define
numeric process-quality thresholds or a deterministic baseline comparison rather
than “unexplained redundancy.”

## Rubric disposition

| Rubric | Review result | Reason |
|---|---|---|
| GE-01 | FAIL | The running Plan 21 graph is not a complete IR and cannot bootstrap compilation. |
| GE-02 | FAIL | Node inputs, schemas, owners, side-effect classes, and idempotency are absent from the shipped node contract. |
| GE-03 | FAIL | Repair/retry/interrupt/resume/exhaustion edges are unrepresentable; join guards are free text. |
| GE-04 | PARTIAL | Prompts have GOAL/TEST/LOOP sections, but their loops are prose and several convergence/repair edges are not executable graph data. |
| GE-05 | FAIL | The first compiler exists only after the graph must already have executed P0 and entered P1. |
| GE-06 | FAIL | State is an untyped field-name list; reducers and the concurrent log merge are undefined. |
| GE-07 | FAIL | Terminal routing, replay eligibility, idempotency, interrupt, and resume semantics are incomplete or contradictory. |
| GE-08 | PARTIAL | P2 specifies a strong normalized boundary, but its repository-wide adoption test is phase-deadlocked. |
| GE-09 | PASS (design intent) | Cross-family judge separation and fail-closed verdict validation are explicit. |
| GE-10 | PARTIAL | Check ownership and targeted repair are required, but repair edges are prose and cannot self-compile. |
| GE-11 | PARTIAL | Desired trace fields are named, but orchestrator and shared-log events lack typed durable ownership. |
| GE-12 | PARTIAL | Broad path/fault coverage is requested, but several completeness denominators are self-reported. |
| GE-13 | PARTIAL | Process metrics are named without release thresholds or an independently frozen expected baseline. |
| GE-14 | PASS (design intent) | Version pinning, offline candidate evaluation, explicit promotion, and new-run migration are stated. |

## Exit decision

**FAIL / CHANGES REQUIRED.** Do not approve or execute Plan 21 beyond planning QA
until the three Critical and three High findings are resolved in the schema,
manifest, and prompts and the corrected graph passes an independent bootstrap
compile plus the mutation suite.
