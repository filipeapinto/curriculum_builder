# Plan 21 historical-regression and repository QA — v1

## Verdict

**FAIL — 2 Critical, 4 High, 0 Medium, 0 Low.** PASS requires zero Critical and High findings.

The Plan 21 YAML validates against its sibling JSON Schema, the locally stated CLI/auth facts reproduce (`claude` 2.1.226 logged out; `codex-cli` 0.147.0 logged in with ChatGPT), and the prompts cover issues 001–007 at a useful high level. The package is not executable or historically complete as written. Its orchestrator requires a compiler before the phase that creates that compiler, its own failure graph sends every stop to `BLOCKED` despite reserving that terminal for external safety facts, every node prompt writes an artifact outside its node allowlist, and material Plan 19 release/debt requirements have no biting Plan 21 test. The historical census also cannot prove the completeness it claims from the source formats it names.

## Audit basis

Read in full: issues 001–007; every file under the Plan 21 `anti_regression_sources` paths (Plans 9, 11–18 QA; all Plan 19 reviews); all Plan 19 phase prompts; and Plan 20 QA v1–v3. I also read the complete Plan 21 plan, schema, assessment, research note, all prompts, and log. No source or plan artifact was edited.

Repository checks independently established:

- `graph_engineered_subscription_execution.plan.v1.yaml` currently validates against `graph_engineered_subscription_execution.schema.v1.json`.
- Neither `runtime/prompt_graph.py` nor `runtime/graph_runtime.py` exists before Plan 21 execution.
- The declared terminal set is `ACCEPTED`, `BLOCKED`, `SYSTEM_FAILURE`, `INTERRUPTED`, but the actual plan edge targets contain only phase nodes, `APPROVED`, and `BLOCKED`.
- `claude auth status` reports `loggedIn: false`, `authMethod: none`; `codex login status` reports ChatGPT login.

## Findings

### Critical — C1: the orchestrator has a circular compiler bootstrap, and the self-compile target lacks the IR fields P1 says are mandatory

**Evidence.** `prompts/P_ALL_graph_orchestrator.prompt.v1.md:13-19` requires the plan graph to be compiled **before activating a node**, including P0. The compiler is not created until P1: the plan makes P1 depend on P0 and authorizes `runtime/prompt_graph.py` only at `graph_engineered_subscription_execution.plan.v1.yaml:67-79`; that file does not exist now. Thus the stated orchestrator cannot activate P0.

Even after bypassing that bootstrap, P1 cannot self-compile the current plan without inventing contract data. P1 requires nodes to carry typed state, schema digests, authorized inputs, side-effect class, idempotency strategy, and owners, and requires explicit bounded-repair/interrupt/resume edges (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:4-13`). The actual plan schema permits only `id`, `prompt`, `role`, `goal`, `depends_on`, `authorized_outputs`, `tests`, `loop`, and `stop_conditions` for nodes and only `from`, `to`, `guard`, and `kind` for edges (`graph_engineered_subscription_execution.schema.v1.json:74-99`). Nevertheless P1-T12 requires this exact Plan 21 graph to compile (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:31`), while the P1 node authorizes no machine-readable normalized graph manifest (`graph_engineered_subscription_execution.plan.v1.yaml:72-76`). Schema validation passing therefore proves only the weaker planning schema, not the IR P1 says is executable.

**Impact.** The advertised `P0 → (P1 || P2) → ...` path cannot begin as written. If an implementer silently treats schema validation as compilation or fills missing IR properties with defaults, the compiled graph and its acceptance/failure proofs become invented evidence. This reproduces the historical impossible-baseline, stale-contract, and non-executing-test classes.

**Required remediation.** Define a bootstrap that can run before P1 (for example, P0 performs only sibling-schema validation and P1 compilation begins after P1 is implemented), then extend the Plan 21 manifest/schema with every mandatory IR field or authorize and ship a complete source graph manifest that P1 compiles without inference. Authorize the normalized compiled graph artifact explicitly. Add a pre-P0 test proving the bootstrap command exists now and a mutation test showing omission of each mandatory IR field fails.

### Critical — C2: every phase failure is routed to `BLOCKED`, contradicting the plan's terminal taxonomy and making P1 edge-totality/self-compile unsatisfiable

**Evidence.** The plan declares four terminals and seven distinct failure classes (`graph_engineered_subscription_execution.plan.v1.yaml:39-51`) and says `BLOCKED` is reserved for a named unavailable external safety-critical fact, while factory defects become `SYSTEM_FAILURE` (`:188`). But all seven failure edges target `BLOCKED` with only a generic `Pn_stop_condition` guard (`:173-179`); there is no edge to `SYSTEM_FAILURE` or `INTERRUPTED`, and none of the seven failure classes appears in an edge guard. P2 explicitly stops for logged-out auth, API-key billing, malformed structured output, unobservable identity, or unprovable isolation (`prompts/P2_subscription_worker_adapter.prompt.v1.md:51-54`), and the orchestrator directs any stopped node onto the `BLOCKED` edge (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:27-30`). Those are auth/policy/factory/tool conditions, not unavailable safety-critical curriculum facts.

P1-T04 simultaneously says every nonterminal outcome/failure class must have exactly one legal edge (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:23`), and P1-T12 says the current Plan 21 graph compiles (`:31`). Both cannot hold against the edge table above.

**Impact.** The current, already-known Claude logout would be recorded as `BLOCKED` in direct violation of the plan's own invariant. Factory defects, invalid output, transient failures, convergence exhaustion, and interrupts have no truthful plan-level terminal route. This reproduces issues 002/007 and the Plan 19/18 false-block and lifecycle findings.

**Required remediation.** Extend the edge schema and graph with typed outcome/failure guards and explicit `SYSTEM_FAILURE` and `INTERRUPTED` targets (plus a declared convergence-exhausted disposition). Permit `BLOCKED` only for `EXTERNAL_FACT_BLOCK` with the required fact/search evidence. Add one self-graph fixture per failure class and assert the known Claude-logout case cannot select `BLOCKED`.

### High — H1: all seven node prompts append `plans.log.md` outside their declared output scopes

**Evidence.** The plan's first constraint says each phase prompt authorizes only its declared outputs (`graph_engineered_subscription_execution.plan.v1.yaml:12-14`). P0's declared outputs are only its result and baseline contract (`:58-60`), yet the P0 prompt says it may append a log and then requires that write (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:14-17,53-54`). The same unauthorized append appears in P1 (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:43-46`), P2 (`prompts/P2_subscription_worker_adapter.prompt.v1.md:51-55`), P3 (`prompts/P3_durable_graph_runtime.prompt.v1.md:40-43`), P4 (`prompts/P4_curriculum_graph_migration.prompt.v1.md:52-56`), P5 (`prompts/P5_evaluator_optimizer_acceptance.prompt.v1.md:47-51`), and P6 (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:40-44`). None of the corresponding node `authorized_outputs` lists includes `plans/21_graph_engineered_subscription_execution/plans.log.md` (`graph_engineered_subscription_execution.plan.v1.yaml:58-60,72-76,88-93,105-110,122-126,138-141,153-156`). The all-node orchestrator says it changes no authorized output (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:7-9`).

**Impact.** A compliant executor must either refuse every node at its final step or mutate a path outside the compiled allowlist. That defeats P0/P6 dirty-work proofs and repeats the historical scope-delta and dirty-worktree hazards.

**Required remediation.** Either add the exact log path to every node's authorized outputs with an append-only byte-delta rule, or remove node-authored log writes and give one explicitly authorized deterministic graph logger sole ownership. Add a test that compares each prompt's required writes with the node allowlist and fails on either a missing or extra path.

### High — H2: the claimed Plan 19 preservation has no biting test for its live multi-unit `--all` proof or exactly four isolated workbook reviews

**Evidence.** Plan 21 P4 promises to preserve Plan 19's workbook and production contracts (`prompts/P4_curriculum_graph_migration.prompt.v1.md:3-8`). Plan 19 requires a bounded three-unit fixture with live routed workers for **every** unit and a real Arduino-kit `--all` attempt (`plans/19_curriculum_factory_production_loop_closure/prompts/P4_full_manifest_orchestration.prompt.v1.md:185-201`). It also requires exactly four schema-valid, isolated workbook reviews; this was a remediated High finding (`reviews/phase_review.iteration1.yaml:27-29`) and is an explicit test (`prompts/P5_workbook_release_loop.prompt.v1.md:139-147`).

Plan 21 tests only one live full-state unit in P4-T24 (`prompts/P4_curriculum_graph_migration.prompt.v1.md:42`) and one fresh live unit in P6-T13 (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:23`). P4-T16 tests manifest order abstractly and P6-T16 tests coverage/workbook truth (`P4` `:34-42`; `P6` `:26`) but neither requires a single-process live multi-unit run with a P2 receipt for every unit or a fresh Arduino `--all` attempt. P5's evaluator fan-out tests do not set the workbook review count to four, and P6 never tests the 3/5-review, duplicate-role, shared-session, or sibling-verdict negatives Plan 19 requires.

**Impact.** Plan 21 can pass with one live unit and a workbook assembled from fixture/prewritten acceptance records, while autonomous consecutive-unit production or the four-review release gate remains broken. That silently drops approved Plan 19 Critical/High remediations despite P4's preservation claim.

**Required remediation.** Add a live bounded multi-unit `--all` test (at least the Plan 19 three-unit fixture) with per-unit P2 route/receipt proof, interrupt/resume, manifest-order coverage, and zero manual artifacts; add the fresh Arduino `--all` attempt with truthful stop classification. Add an exact-four workbook-review test and biting 3/5, duplicate-role, shared-session, sibling-verdict, malformed-verdict negatives.

### High — H3: Plan 19's deferred-obligation reconciliation can disappear behind a generic supersession record

**Evidence.** Plan 19 P6 requires criterion-by-criterion disposition of RT-1, RT-2, RT-3, RT-4, RT-5, RT-7, and RT-10, quoting each live criterion, citing evidence, preserving the RT-6/RT-8/RT-9 constraints, updating the folder-refactoring mirror, and rerunning the mapping/deferred gates (`plans/19_curriculum_factory_production_loop_closure/prompts/P6_release_proof_debt_reconciliation.prompt.v1.md:23-32,177-196,252-258`). Plan 21 says it preserves Plan 19 contracts (`prompts/P4_curriculum_graph_migration.prompt.v1.md:5-8`) but its only final requirement is that `supersession.v1.md` name Plan 19/20 dispositions and remaining blockers (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:30`). No Plan 21 test names an RT id, the mirrored Plan 03 catalogue, `FR-P2-DEFERRED`, or the literal-criterion/no-discharge rule.

**Impact.** A generic “remaining blocker” paragraph can satisfy P6-T20 while individual obligations are silently closed, omitted, or left inconsistent with their mirror. This is the exact false-discharge/stale-authority class repeatedly found in Plans 16, 18, and 19.

**Required remediation.** Add a P6 test that reads the live deferred registry, quotes and disposes every Plan 19-owned RT criterion individually, verifies the Plan 03 mirror and reserved RT-9 negative fixture, and reruns `FR-P2-DEFERRED`/`FR-P4-CHECK-MAPPING` after any disposition. Unproven criteria must remain unchanged blockers, not be weakened or hidden by supersession.

### High — H4: the historical census rule cannot prove that every prior Critical/High finding was included

**Evidence.** P0-T03 counts “every Critical/High heading” (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:31-34`). Several named sources do not encode findings that way. Plan 19 review YAML records aggregate severity counts and finding IDs/actions but no per-finding severity or heading (`plans/19_curriculum_factory_production_loop_closure/reviews/phase_review.iteration1.yaml:4-14`, continuing through `:83`; the later review files use the same disposition shape). Plan 20 QA v2 declares `2 Critical, 1 High` (`plans/20_subscription_only_execution_model/qa/plan_qa.v2.md:3-5`) but contains only two finding headings, both Critical (`:27`, `:84`), with no High heading. A heading-only census therefore cannot reconcile the declared count and will either omit an asserted High finding or invent its identity.

P0-T10 mutates an “unrecorded historical finding” (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:40`) but no P0-authorized executable census checker or source-format/count reconciliation is specified; the only P0 outputs are a Markdown result and YAML contract (`graph_engineered_subscription_execution.plan.v1.yaml:58-60`). P5-T21 and P6-T10 replay only IDs P0 froze, so an omission at P0 becomes self-consistent false evidence downstream (`prompts/P5_evaluator_optimizer_acceptance.prompt.v1.md:36`; `prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:20`).

**Impact.** The anti-regression suite can prove completeness relative to an incomplete P0 list. This is a regression-suppression pattern: later tests certify the census rather than the full source corpus.

**Required remediation.** Define an executable census contract that handles Markdown headings, YAML finding IDs/dispositions, aggregate counts, and source anomalies. Require count-to-item reconciliation; where per-item severity is unavailable, conservatively include every disposition and label severity unresolved rather than omit it. Treat Plan 20 v2's count/heading mismatch as a required anomaly with an evidence-backed disposition. Authorize the checker/test artifact explicitly and make P0-T10 mutation-test that implementation.

## Historical class ownership audit

| Historical regression class | Plan 21 owner/test | Assessment |
|---|---|---|
| Raw JSON / dropped learner fields | P4-T07, P5-T14, P6-T09 | Covered at class level. |
| Acceptance bypass / missing required checks | P1-T07, P4-T11, P5-T01/T05, P6-T09 | Covered at class level. |
| Visual truth, POE, claim entailment, L04 safety | P4-T08/T09/T10, P5-T14/T15, P6-T09 | Covered only if P0 creates issue-specific biting fixtures; P6-T09 is the final owner. |
| Run lifecycle / accepted immutability / resume | P3-T11–T17, P4-T14/T17, P6-T14/T16 | Covered, subject to C2's missing truthful terminal edges. |
| Dirty-work preservation | P0-T02/T09, P6-T12 | Design present, but H1 violates its own allowlist. |
| Schema-invalid instructions / impossible baselines | P0-T01, P1-T01/T12, P6-T01 | Not covered for the actual bootstrap/IR mismatch; C1. |
| Prior QA census completeness | P0-T03/T10, P5-T21, P6-T10 | Self-referential and incomplete; H4. |
| Plan 19 live multi-unit and four-review release proof | No biting owner | Missing; H2. |
| Plan 19 deferred-debt truth/mirror | Generic P4-T03/P6-T20 only | Missing literal owner/test; H3. |
| False evidence / regression suppression | P6-T10/T17/T19 | Strong downstream controls, but they cannot recover items omitted by H2–H4. |

## Required re-review

After remediation, rerun schema validation and conduct a fresh independent historical review. PASS is possible only when the bootstrap is executable from the current repository, every failure class has a truthful typed edge, prompt writes equal declared output scopes, and the omitted Plan 19/historical controls have committed biting tests.
