# Plan 21 historical-regression and repository QA — v3

## Verdict

**FAIL — 3 Critical, 1 High, 0 Medium, 0 Low.** PASS requires zero unresolved Critical or High findings.

The exact current package passes both bootstrap commands, and all eight shipped JSON Schemas are themselves valid Draft 2020-12 schemas. All six round-2 findings received material remediations. The final graph still admits two concrete historical bypasses: a schema-valid `PASS` event with no tests or artifact evidence advances any phase, and the shared pause state accepts an originless `RESUME_P6` event that bypasses P3–P5 after a P2 pause. P0's closed run-status vocabulary also contradicts the live repository and the Plan 19 contract it promises to freeze. Finally, failure-class semantics remain absent from the executable guards, allowing a factory defect to select a prerequisite pause.

## Audit basis

I independently re-read the exact current Plan 21 manifest, sibling schema, bootstrap validator, all contract schemas and data, and all node/orchestrator prompts. I checked them against issues 001–007 and the previously read complete Critical/High corpus under Plans 9, 11–18, all Plan 19 reviews/prompts, and Plan 20 QA v1–v3. I did not read or coordinate with another Plan 21 reviewer.

Commands and repository facts:

- `python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan.py` → `plan21_bootstrap=PASS`.
- The same command with `--self-test` → `plan21_bootstrap=PASS`.
- `Draft202012Validator.check_schema` accepts the Plan schema and all seven contract schemas.
- `contracts/identity_assurance_policy.v1.yaml` validates against its sibling schema and declares both Claude/Anthropic and Codex/OpenAI (`contracts/identity_assurance_policy.v1.yaml:1-14`).
- Current capability facts still reproduce: Claude Code 2.1.226 reports logged out/auth method none; Codex CLI 0.147.0 reports ChatGPT login.
- The five later-phase schemas are correctly absent now and represented as producer-owned `artifact://` references rather than falsely existing inputs.
- RT-7's stale text remains live (`policy/deferred.v1.yaml:98-103`; `plans/03_folder_refactoring/folder_refactoring.plan.v6.md:1359`). Four mandatory repair targets are currently dirty: the Plan 03 mirror is staged-added, `policy/checks.v1.yaml` and `tests/gates/fr_p5_unit.py` are modified, and `runtime/readability.py` is untracked. The revised P6 contract therefore correctly requires a prerequisite pause unless the user explicitly authorizes those exact writes.

## Findings

### Critical — C1: an empty-evidence `PASS` event is schema-valid and deterministically advances the graph

**Evidence.** The sole routing authority is the phase event: P_ALL says Markdown and file presence cannot select an edge and that registered guards evaluate the immutable event (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:32-38`). But `phase_result.schema.v1.json` gives `test_results` no `minItems`, gives `artifact_hashes` no `minProperties`, and imposes no conditional rule that a `PASS` event contain every declared test with `PASS` plus hashes for required outputs (`contracts/phase_result.schema.v1.json:16-35`).

Every success guard checks only `node_id` and `outcome: PASS` (`graph_engineered_subscription_execution.plan.v1.yaml:111-117`), and those guards directly advance P0→P1 through P5→P6 and P6→PLAN_APPROVED (`:354-360`). I instantiated a P5 event with a valid version/run/node/attempt/digest, `outcome: PASS`, null failure/repeat/resume fields, `reason_id: demo`, `test_results: []`, and `artifact_hashes: {}`. Draft 2020-12 validation reported `SCHEMA_VALID`; the registered P5_PASS predicates also match it.

The bootstrap verifies that each node declares a phase-event output and schema but never relates a node's declared tests or outputs to the event contents (`tools/validate_plan.py:104-140`). P6-T01/P6-T10 cannot save the graph because P6 itself can emit the same empty-evidence PASS event and reach approval.

**Impact.** Every phase can advance without executing any GOAL/TEST/LOOP test and without producing its required artifacts. This directly reproduces issue 002's missing-required-check acceptance bypass and the prior non-executing-test/false-evidence findings across Plans 9–20.

**Required remediation.** Compile each node's exact test-id denominator and required evidence outputs into its phase-result contract. A PASS event must contain exactly the required tests, all PASS, with non-null evidence hashes, plus hashes/schema-validation results for every required non-event output; the event itself needs an explicit non-recursive treatment. Add bootstrap/P1 mutations for empty, missing, duplicate, extra, NOT_RUN, and null-evidence tests and for missing/extra artifact hashes. Demonstrate that the concrete empty-evidence event above fails before any success guard evaluation.

### Critical — C2: shared pause/interrupt states allow cross-phase resume bypass, while no authorized actor owns resume-event creation

**Evidence.** All pause/interrupt resume guards bind only the new event's `node_id`, `outcome`, and `resume_node_id` (`graph_engineered_subscription_execution.plan.v1.yaml:148-154`). The phase-event schema contains no suspended-node id, predecessor pause-event hash, checkpoint hash, prior attempt, or continuation token (`contracts/phase_result.schema.v1.json:5-35`). Thus nothing proves which node actually entered the shared `PAUSED_PREREQUISITE` or `INTERRUPTED` state.

The graph has P2 and P6 entering the same prerequisite state, followed by separate edges from that state to either P2 or P6 (`graph_engineered_subscription_execution.plan.v1.yaml:375-378`). It similarly allows the shared interrupt state to resume to every P0–P6 node (`:386-399`). The bootstrap requires those outgoing edges but checks only that a resume guard names its target (`tools/validate_plan.py:92-101,169-176`); it never requires target = suspended origin.

I instantiated a schema-valid event with `node_id: P6`, `outcome: RESUME`, and `resume_node_id: P6`, with no prior-pause linkage. It validates and matches RESUME_P6. Consequently this legal graph path exists:

`START → P0 → P1 → P2 → PAUSED_PREREQUISITE → P6 → PLAN_APPROVED`

It bypasses P3, P4, and P5 despite the strict-sequential invariant (`graph_engineered_subscription_execution.plan.v1.yaml:403`). There is also an ownership deadlock: a P6 resume event is in P6's output scope (`:334-339`), but P6 cannot be activated to write it until that same event selects the resume edge. If an external controller may write it, that controller and its authority are absent from the node/output registry.

**Impact.** A forged or misrouted resume can skip the durable runtime, migration, and evaluator graph and still approve the plan. Enforcing phase output ownership instead makes every resume impossible. This reproduces acceptance bypass, stale/forged state, and non-executable resume behavior from issues 002/007 and Plan 18/19 QA.

**Required remediation.** Use distinct typed pause continuations or persist `suspended_node_id`, source event/checkpoint hash, attempt, graph digest, and an unforgeable continuation id. Resume guards must prove the continuation targets the exact suspended node and original dependency closure. Declare one deterministic controller as the authorized resume-event writer, or make the suspended source node own a pre-activation resume request distinct from its result event. Add negative witness tests for P2-pause→P6, P0-interrupt→P6, changed-digest resume, originless resume, and duplicate resume.

### Critical — C3: P0's mandatory run-status vocabulary contradicts the live repository and Plan 19 lifecycle

**Evidence.** P0 must freeze the actual repository and capture separate unit/run/plan vocabularies (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:8-18`). Its output schema instead hard-codes the run values as `RUNNING`, `INTERRUPTED`, `COMPLETED`, and `SYSTEM_FAILURE` (`contracts/baseline_contract.schema.v1.json:40-43`).

The live authoritative schema uses `IN_PROGRESS`, `PARTIAL`, `INTERRUPTED`, `BLOCKED`, and `COMPLETE` (`schemas/run_lifecycle.schema.v1.json:20-28`), and runtime writes exactly `IN_PROGRESS`, `PARTIAL`, `INTERRUPTED`, and `BLOCKED`, reserving `COMPLETE` for workbook assembly (`runtime/run_state.py:109-145`; `runtime/workbook.py:1-64`). Plan 19 records this same vocabulary and explicitly requires adding a representable run-level SYSTEM_FAILURE without losing the existing states (`plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:56-61`; `prompts/P4_full_manifest_orchestration.prompt.v1.md:36-40`). Plan 21's own P4-T17 requires partial/interrupted/blocked/failed/complete coverage (`prompts/P4_curriculum_graph_migration.prompt.v1.md:35`), and P6-T16 names `COMPLETE` (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:26`).

**Impact.** A schema-valid P0 contract must falsely rename `IN_PROGRESS`/`COMPLETE`, omit `PARTIAL` and run-level `BLOCKED`, and claim `SYSTEM_FAILURE` is already in the live run schema. An honest inventory fails P0's output schema. This is the exact issue-007 lifecycle-truth and impossible-baseline class.

**Required remediation.** Represent observed and target vocabularies separately. Freeze the live values exactly, then declare a typed migration adding SYSTEM_FAILURE (and its reason/checkpoint semantics) while preserving `IN_PROGRESS`, `PARTIAL`, `INTERRUPTED`, `BLOCKED`, and `COMPLETE`, unless P4 explicitly migrates every producer/consumer and records the mapping. Add a P0 mutation/fixture against the current schema and runtime constants so renamed or omitted states fail.

### High — H1: executable guards do not bind failure classes or reasons, so factory defects can select prerequisite pauses

**Evidence.** The phase-result schema permits any listed failure class with any `REVISABLE`, `PAUSED_PREREQUISITE`, `SYSTEM_FAILURE`, or `CONVERGENCE_EXHAUSTED` outcome; it requires a string but defines no valid outcome/class pair (`contracts/phase_result.schema.v1.json:12-15,32-35`). The two prerequisite guards check only node id and outcome, not failure class, reason id, auth evidence, dirty-overlap path, or authorization decision (`graph_engineered_subscription_execution.plan.v1.yaml:146-147`).

A P2 event with `outcome: PAUSED_PREREQUISITE` and `failure_class: FACTORY_DEFECT` is schema-valid and matches SUBSCRIPTION_AUTH_MISSING. Likewise a generic P6 pause event can select PROTECTED_RT7_OVERLAP without naming a dirty RT-7 path. This contradicts P1-T04's outcome/failure totality requirement (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:19`) and the invariant that factory defects become SYSTEM_FAILURE (`graph_engineered_subscription_execution.plan.v1.yaml:408`). The bootstrap's guard checks validate field existence and outcome equality only (`tools/validate_plan.py:57-101`).

**Impact.** The revised terminal names are syntactically separated, but the classifier can still disguise a factory defect as a prerequisite pause or route another invalid class through a revisable/system edge. That preserves the historical false-block/failure-reclassification defect under a new label.

**Required remediation.** Define closed outcome↔failure-class mappings and typed pause reasons/evidence. SUBSCRIPTION_AUTH_MISSING must require the exact auth/entitlement reason and evidence; PROTECTED_RT7_OVERLAP must require an exact P0-protected path and missing user authorization. Add mutations for every illegal class/outcome pair, including the concrete factory-defect pause above.

## Round-2 remediation verification

| Round-2 item | Final assessment |
|---|---|
| C1 producer-owned future artifacts / runtime contract | **Closed.** `artifact://` ownership is machine-checked (`tools/validate_plan.py:142-162,325-328`), and P3 now produces and writes `P3_runtime_contract` (`graph_engineered_subscription_execution.plan.v1.yaml:250-270`). |
| C2 two-driver assurance policy | **Closed.** A pre-existing closed policy/schema declares both drivers and P2 consumes it read-only (`graph_engineered_subscription_execution.plan.v1.yaml:227-239`; `contracts/identity_assurance_policy.v1.yaml:1-14`). |
| C3 RT-7 scope, exact sites/gates, dirty overlap | **Closed at plan-design level.** P6 names every historical site and gate, exact before/after text, and the protected-overlap pause (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:33`; plan `:334-340,375-378`). Given current dirty paths, actual execution must pause absent new user authorization. |
| H1 QA exhaustion terminal | **Closed.** P6 emits CONVERGENCE_EXHAUSTED and routes to SYSTEM_FAILURE, never BLOCKED (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:41-45`; plan `:368-374`). |
| H2 census/anomaly denominator | **Closed.** Historical findings, anomalies, aggregates, owners, evidence requirements, and numeric thresholds are typed and mandatory (`contracts/coverage_denominator.schema.v1.json:5-20`; `contracts/historical_findings.schema.v1.json:5-31`). |
| H3 cold multi-unit resume | **Closed.** P6-T14 and P6-T21 require a first real process followed by a separate clean `--resume` process (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:24,31`). |

## Historical ownership summary

The current prompts retain explicit owners for issues 001–007: raw JSON/rendering, acceptance dominance and required checks, visual truth, L04 safety/evidence, POE, claim entailment, and run lifecycle. P6-T10/T11 retain the prior Plans 9–20 Critical/High matrix; P6-T22 preserves exactly four isolated workbook reviews and its 3/5, duplicate identity/role, shared-session, sibling-verdict, and malformed negatives; P6-T23 preserves literal RT debt, mirror, RT-9 fixture, sites, gates, and dirty-work pause; and P6-T24 independently reruns the format-aware census.

Those test owners are not effective while C1 permits all of them to be omitted, C2 permits the evaluator/migration phases to be skipped on resume, and C3 prevents an honest lifecycle baseline. A further revision and independent re-review are required before PASS.
