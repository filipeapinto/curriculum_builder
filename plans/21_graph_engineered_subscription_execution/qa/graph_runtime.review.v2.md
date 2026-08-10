# Plan 21 graph-formalism and durable-runtime review — v2

## Verdict

**CHANGES REQUIRED — 1 Critical, 4 High, 1 Medium.** Round 2 is materially
better, but it is not a PASS. The revised plan closes the v1 P2/P4 dependency
deadlock, shared-log race, terminal namespace collapse, and corrupt-checkpoint
replay defect. It also ships a bootstrap validator that passes its bundled
self-test. The production compiler's own required semantics still make the
current phase manifest fail self-compilation, however: repair exhaustion and
interrupt/resume are asserted in prose but absent from the graph. The bootstrap
also accepts several safety-relevant mutations, and the coverage and baseline
schemas remain permissive enough for vacuous “typed” evidence.

The exit rule requires zero unresolved Critical or High findings. Falling
finding counts were not used as evidence of correctness.

## Executed verification

From the repository root I ran the exact shipped commands:

```text
python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan.py
plan21_bootstrap=PASS

python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan.py --self-test
plan21_bootstrap=PASS
```

I then imported `tools/validate_plan.py` and applied independent in-memory
mutations without writing source artifacts. The validator **accepted** all of
the following:

- removal of `E-P3-SYSTEM`;
- removal of every repair edge;
- removal of `E-P2-PAUSE`;
- changing P2's `depends_on` to `[]` while retaining `E-P1-P2`;
- removing P1 from P2's `context_from` while retaining the P1 contract input;
- duplicating the P1→P2 guard/outcome under a second edge id;
- changing the P6→PLAN_APPROVED terminal edge kind to `success`;
- assigning one authorized output to both P0 and P1; and
- assigning `P0_result` as a state write to both P0 and P1.

These are distinct from the bundled duplicate-id, dangling-edge, reachability,
unbounded-loop, unsafe-cycle, and missing-owner mutations.

## V1 remediation audit

| V1 item | Round-2 result | Evidence |
|---|---|---|
| Critical 1 — bootstrap deadlock / prompt control plane | **Partially fixed** | A pre-P0 deterministic validator now exists and P_ALL is explicitly operator-facing, but semantic false negatives remain (Finding 2), and the later P1 self-compile is internally unsatisfiable (Finding 1). |
| Critical 2 — terminal/failure inconsistency | **Mostly fixed, one residual** | Unit/run/plan vocabularies and explicit plan terminals are separated; no graph edge targets unit `BLOCKED`. P6 still instructs an illegal `BLOCKED` outcome after QA exhaustion (Finding 5). |
| Critical 3 — P2/P4 dependency deadlock | **Fixed** | P2 is sequential after P1; P2-T02 is adapter-local; repository-wide migration is P4-T04/T05. |
| High 4 — incomplete IR semantics | **Partially fixed** | Nodes gained ports, ownership, state access, side-effect, and idempotency fields. Typed state bindings, failure-class edges, exhaustion, and resume remain incomplete (Findings 1 and 3). |
| High 5 — concurrent shared log | **Fixed** | Sequential phases write immutable result events and every prompt now forbids shared-log append. |
| High 6 — invalid-checkpoint replay | **Fixed** | P3-T12/P3-T18 and P4-T14 distinguish replayable absence/incomplete state from fail-closed corruption. |
| Medium 7 — self-reported path/boundary denominator | **Partially fixed** | P0 now creates a denominator and later tests bind to it, but its schema permits empty/vacuous coverage and mutation sets (Finding 4). |

## Findings

### 1. Critical — P1-T12 cannot self-compile the current manifest because repair exhaustion and resume are not graph edges

**Evidence.**

- P1 requires first-class failure, retry, repair, interrupt, **resume**, and
  **exhaustion** edges in
  `plans/21_graph_engineered_subscription_execution/prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:5-9`.
  P1-T04 requires one legal edge for every outcome/failure class (`:19`), P1-T05
  requires exhaustion routes for repair/retry cycles (`:20`), and P1-T11
  requires version-pinned resume edges (`:26`). P1-T12 then requires this same
  Plan 21 manifest to compile with no prompt prose supplying missing semantics
  (`:27`).
- The plan declares `CONVERGENCE_EXHAUSTED` as a failure class at
  `plans/21_graph_engineered_subscription_execution/graph_engineered_subscription_execution.plan.v1.yaml:49-56`.
  Its seven repair edges (`:252-258`) contain only a self target and
  `max_attempts: 2`. None has a linked exhaustion edge, exhaustion guard, repeat
  signature, or `CONVERGENCE_EXHAUSTED` outcome. The generic system edges at
  `:260-266` have unrelated outcomes such as `compiler_unsound` and
  `runtime_invariant_failed`; nothing binds a repair counter crossing its limit
  to one of those edges.
- The graph invariant nevertheless asserts every repair cycle has a
  `SYSTEM_FAILURE` exhaustion disposition (`:280`). The shipped validator checks
  only that repair/retry has `max_attempts` and that repair is a self-loop
  (`tools/validate_plan.py:56-59`); it never verifies an exhaustion transition.
- Every phase has an interrupt edge to `INTERRUPTED` (`plan.v1.yaml:267-273`),
  and P2 has a prerequisite-pause edge (`:259`), but the manifest contains zero
  `kind: resume` edges. The schema permits the word `resume` as a kind
  (`graph_engineered_subscription_execution.schema.v1.json:91`) while its
  `from` pattern permits only `START` or P-nodes (`:87`), so it cannot express a
  transition out of `INTERRUPTED` or `PAUSED_PREREQUISITE`. P_ALL explicitly
  activates no downstream node at either state
  (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:30-36`) and supplies no
  deterministic resume contract.

**Impact.** If P1 implements the compiler demanded by P1-T04/T05/T11, that
compiler must reject the same manifest at P1-T12. If it accepts the manifest, it
has weakened or inferred the exact safety semantics P1 says must be explicit.
Either outcome stops before P2 and violates GE-03, GE-05, and GE-07. A paused
authentication prerequisite or external interrupt also has no graph-defined way
to resume the digest-pinned run.

**Required remediation.** Add explicit repair-exhaustion edges for every repair
cycle with the counter/signature predicate, `CONVERGENCE_EXHAUSTED` mapping, and
`SYSTEM_FAILURE` target. Represent pause/interrupt as resumable graph states (not
terminal-only targets), add version-pinned resume edges to the owning node or
first missing checkpoint, and extend the schema/validator accordingly. Then add
mutations that remove or misroute each exhaustion and resume edge and require
P1-T12 to compile the corrected bytes.

### 2. High — The shipped bootstrap validator does not enforce missing failure edges, outcome totality, dependency topology, or single ownership

**Evidence.**

- The bootstrap describes itself as rejecting structural contradictions before
  P0 (`plans/21_graph_engineered_subscription_execution/tools/validate_plan.py:2-6`),
  and P0-T11 says omission of a mandatory IR field/edge must fail
  (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:35`). The August rubric
  explicitly includes missing failure edges in compiled topology
  (`research/graph_engineering_sota.2026-08.md:147`).
- `validate()` checks JSON Schema, id uniqueness, reference existence, prompt
  headings, reachability, terminal reachability, bounded self-loop shape, and a
  DAG over non-loop edges (`tools/validate_plan.py:35-125`). It never compares
  `depends_on` with incoming success edges, `context_from` with authorized
  contract inputs, guards/outcomes for exclusivity and totality, terminal target
  with edge kind, or outputs/state writes for unique ownership.
- The independent mutations listed under Executed verification were all
  accepted. Most importantly, removing a required system-failure edge, every
  repair edge, or P2's only pause edge still returns success because each node
  can reach *some* terminal on the happy path. Duplicated guard/outcome and
  multiply-owned artifact/state mutations also pass.
- The bundled self-test contains only six mutations
  (`tools/validate_plan.py:132-168`) and therefore does not expose these false
  negatives.

**Impact.** The pre-P0 assurance layer can certify a graph with a missing failure
route, contradictory dependency contract, ambiguous transition, or concurrent
ownership. That is precisely the class of unsafe meta-plan shape the bootstrap
was added to prevent. P1 may later build a stronger compiler, but P0 already
executes under the weaker graph.

**Required remediation.** Enforce per-node outcome/failure totality, exactly one
start and declared success predecessor, dependency/edge/context consistency,
guard uniqueness or proven exclusive sets, terminal-kind correctness, unique
artifact and non-reduced state ownership, and required repair/pause/system/
interrupt/exhaustion/resume routes. Add each independent mutation above to the
shipped self-test with an expected invariant-specific error.

### 3. High — The “fully typed” phase state and P0 handoff contracts remain structurally untyped

**Evidence.**

- The node schema now requires `input_schemas`, `output_schemas`, `state_reads`,
  and `state_writes`
  (`plans/21_graph_engineered_subscription_execution/graph_engineered_subscription_execution.schema.v1.json:56-79`),
  which is a real improvement. But each state access is only a free string list;
  no field maps a state key to a JSON type/schema, reducer, default/identity,
  writer cardinality, or checkpoint serialization.
- The plan-level state contract is likewise a list of required field *names*
  plus vocabulary lists (`graph_engineered_subscription_execution.schema.v1.json:26-36`;
  `graph_engineered_subscription_execution.plan.v1.yaml:30-56`). Fields such as
  `node_attempt`, `authorized_input_hashes`, `check_results`, `edge_decision`,
  and `checkpoint_hash` have no declared types or per-field schemas.
- P1 says it builds an IR for typed ports and state writes and self-compiles the
  “fully typed” manifest
  (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:3-9,27`), but the current
  manifest provides no explicit binding between, for example, P1's
  `compiled_graph` state write and its `schemas/prompt_graph.schema.v1.json`
  output. A compiler would have to infer that relationship from names/order.
- The P0 baseline schema, which later phases trust for symbolic scope and status
  resolution, leaves `baseline_results` as arbitrary objects,
  `capability_facts` as an arbitrary object, and the three
  `status_vocabularies` values unconstrained
  (`contracts/baseline_contract.schema.v1.json:5-14`). Its `authorized_paths`
  requires P4/P5/P6 objects but gives those objects no required selector keys or
  path/schema shape (`:10`). Thus `{P4: {}, P5: {}, P6: {}}` satisfies that part
  of the schema while every downstream `contract://P0/authorized_paths/...`
  selector remains unresolved.

**Impact.** P0 can emit schema-valid but operationally unusable handoffs, and P1
cannot compile a fully typed state graph without conventions or prose inference.
This leaves GE-02 and GE-06 partial and weakens deterministic checkpoint/reducer
validation.

**Required remediation.** Define a state-field map whose entries carry type or
schema reference, writer(s), reducer/identity when applicable, serialization,
and checkpoint policy. Bind every node read/write to that map and every artifact
port to a specific schema. Tighten the baseline schema so every symbolic selector,
capability/auth fact, baseline result, and unit/run/plan vocabulary has a closed,
required structure; add negative fixtures for empty selector maps and mistyped
state values.

### 4. High — The independent coverage denominator can be schema-valid while empty, so P1-T15 and P6 coverage can pass vacuously

**Evidence.**

- P0 must freeze an independent denominator of nodes, edges, guards,
  side-effect boundaries, mutations, historical findings, and numeric process
  thresholds
  (`plans/21_graph_engineered_subscription_execution/prompts/P0_contract_and_evidence_freeze.prompt.v1.md:12-18`).
  P1-T15 says the denominator cannot shrink to the implementation
  (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:30`), and P6-T04/T05/
  T06/T18 rely on it for full path, boundary, crash, and process-quality coverage
  (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:14-16,28`).
- The denominator schema requires the property names but gives every array no
  `minItems`, gives each item no minimum/pattern, and defines
  `process_thresholds` only as an arbitrary object with one property
  (`contracts/coverage_denominator.schema.v1.json:5-14`). A denominator with
  empty nodes/edges/guards/boundaries/mutations and
  `process_thresholds: {anything: "not numeric"}` is schema-valid.
- The schema does not include the historical findings set named by the P0 goal,
  nor required mutation categories for guard inversion, missing failure edge,
  join-member omission, reducer order sensitivity, and admission/checkpoint
  crash sides. Nothing binds listed node/edge/guard ids to the source digest or
  Plan 19/P0 inventory beyond an opaque string.

**Impact.** The system under test can report complete coverage against a zero or
incomplete denominator, and numeric process release checks can receive
non-numeric thresholds. This leaves the v1 GE-12/GE-13 remediation non-biting.

**Required remediation.** Require non-empty, typed records (not strings) for
every denominator category, with source locator/hash, expected owners/outcomes,
and complete mutation classes. Require named numeric threshold fields and valid
ranges. Deterministically derive and cross-check node/edge/guard sets against the
frozen Plan 19/Plan 21 source inventories, and add an independent mutation that
removes one denominator row while leaving the implementation unchanged.

### 5. High — P6 still instructs the plan to record curriculum `BLOCKED` after QA non-convergence

**Evidence.**

- The revised manifest correctly separates unit `BLOCKED` from plan terminals
  (`plans/21_graph_engineered_subscription_execution/graph_engineered_subscription_execution.plan.v1.yaml:46-48`)
  and states that no plan-phase target may be `BLOCKED` (`:280-282`). P_ALL
  repeats that rule and routes defects to `SYSTEM_FAILURE`
  (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:25-28`).
- P6's loop nevertheless says: “if any Critical/High remains after round three,
  record `BLOCKED`”
  (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:36-42`). There is
  no uppercase `BLOCKED` plan terminal or edge. The document-level plan status
  enum contains lowercase `blocked`
  (`graph_engineered_subscription_execution.schema.v1.json:11`), so the wording
  is not a valid reference to that field either.

**Impact.** The exact non-convergence path the review protocol anticipates has
an illegal/ambiguous terminal instruction. Following it reproduces the false-
block class; refusing it leaves P6 without the mandated outcome after round
three.

**Required remediation.** Name the code-owned graph terminal and record schema
explicitly. A QA/release defect should take P6's `SYSTEM_FAILURE` edge (or a new
distinct plan-review-exhausted terminal if intentionally designed), while any
document status transition must use its exact lowercase enum and remain separate
from curriculum `BLOCKED`.

### 6. Medium — P2's declared side-effect class and idempotency key do not describe the whole phase node

**Evidence.**

- P2 is classified only as `external_model`
  (`plans/21_graph_engineered_subscription_execution/graph_engineered_subscription_execution.plan.v1.yaml:130-142`),
  yet the same node writes a runtime module, two schemas, a test module, and a
  result record in addition to executing two live CLI canaries. The schema has a
  `mixed` class specifically available
  (`graph_engineered_subscription_execution.schema.v1.json:74`).
- Its node idempotency key is
  `{execution_contract_digest}:P2:{request_digest}:{attempt}` (`plan.v1.yaml:142`),
  but P2 is a phase containing multiple build writes and at least two provider
  requests. The manifest does not define which request digest represents the
  node, how per-call keys compose into the phase checkpoint, or how replay of the
  build portion is separated from a legitimate transient canary retry.
- P2-T15 tests idempotent *request* replay
  (`prompts/P2_subscription_worker_adapter.prompt.v1.md:42`), not phase-node
  checkpoint replay across the combined workspace-write/external-model effects.

**Impact.** The compiler cannot accurately validate P2's complete side-effect
and replay contract from the node metadata, even though the driver-local adapter
may be correct.

**Required remediation.** Mark P2 `mixed` and define a phase-level idempotency/
checkpoint composition: immutable build artifact digest plus separately keyed
Claude and Codex canary tasks, with a deterministic phase result admission.
Add crash/replay tests between each sub-effect and the P2 result checkpoint.

## Rubric conclusion

GE-08, GE-09, GE-10, and GE-14 now have credible design coverage, and the v1
durable corruption split is properly repaired. GE-01/GE-03/GE-05 remain blocked
by the self-compile and bootstrap-totality findings; GE-02/GE-06 remain partial
because state/handoff types are not closed; GE-07 remains blocked by missing
phase resume/exhaustion transitions; and GE-12/GE-13 remain partial because the
coverage denominator can be empty.

**FAIL / CHANGES REQUIRED.** Resolve every Critical and High finding, extend the
bootstrap self-test with the accepted mutations above, and rerun the independent
review against the exact revised bytes. Do not approve based on the lower count.
