# Plan 21 historical-regression and repository QA — v2

## Verdict

**FAIL — 3 Critical, 3 High, 0 Medium, 0 Low.** PASS requires zero Critical and High findings.

Round 2 closes the shared-log defect and adds explicit plan-level pause, system-failure, and interrupt edges. It also names the missing Plan 19 three-unit live run, exact-four workbook reviews, deferred-obligation mirror, and format-aware census tests. The revised package is still not executable as written. The shipped bootstrap passes, but P1's required self-compile cannot pass against future, nonexistent schemas and a dangling state contract; P2 requires identity-assurance registry policy that its input schema cannot represent and its output scope cannot change; and the mandatory RT-7 repair cannot be performed within P6's output scope or the dirty-work preservation rule. Three further High contradictions leave terminal routing, the historical denominator, and cold-process multi-unit resume under-specified or impossible.

## Audit basis

I rechecked the revised Plan 21 manifest, schema, bootstrap validator and self-test, three contract schemas, and all eight prompts against issues 001–007 and the complete historical corpus read in round 1: all QA under Plans 9 and 11–18, every Plan 19 review and P0–P6/P_ALL prompt, and Plan 20 QA v1–v3. I did not read another Plan 21 reviewer’s report.

Repository checks:

- Both declared bootstrap commands execute successfully and print `plan21_bootstrap=PASS`.
- The future P1–P3 artifacts `schemas/prompt_graph.schema.v1.json`, `schemas/worker_request.schema.v1.json`, `schemas/worker_receipt.schema.v1.json`, `schemas/graph_run.schema.v1.json`, `runtime/prompt_graph.py`, `runtime/subscription_worker.py`, and `runtime/graph_runtime.py` do not exist before execution.
- `policy/routing/model_registry.v1.yaml` currently contains only OpenAI models and no identity-assurance policy (`:10-43`); its schema forbids undeclared model fields (`schemas/model_registry.schema.v1.json:34-83`).
- The live RT-7 criterion still names the stale `curricula/<name>/units/` location (`policy/deferred.v1.yaml:98-103`; mirrored at `plans/03_folder_refactoring/folder_refactoring.plan.v6.md:1359`).
- `git status --short --untracked-files=all` marks three RT-7-mandated edit targets as pre-existing user work: `policy/checks.v1.yaml` and `tests/gates/fr_p5_unit.py` are modified, and `runtime/readability.py` is untracked.

## Findings

### Critical — C1: the shipped bootstrap exists, but P1's production self-compile target remains impossible

**Evidence.** P1-T02 requires unresolved prompts or schemas to fail, while P1-T12 requires the complete P0→P6 manifest to compile before P2 (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:17,27`). At that moment the manifest already references schemas that later phases, not P1, create: P2 owns `schemas/worker_request.schema.v1.json` and `schemas/worker_receipt.schema.v1.json` (`graph_engineered_subscription_execution.plan.v1.yaml:130-137`), and P3 owns `schemas/graph_run.schema.v1.json` (`:155-162`). P4 and P5 consume the latter (`:179-186,203-209`). Those files are absent now and remain absent at the required end-of-P1 self-compile point. Treating their paths as resolved schemas violates P1-T02; refusing them violates P1-T12.

The state graph is independently dangling: P4 reads `contract://P3/runtime_contract` (`graph_engineered_subscription_execution.plan.v1.yaml:179,188`), but P3's declared state writes are only `graph_run_events`, `checkpoints`, and `P3_result` (`:163-165`). No node produces a state value named `runtime_contract`.

The manifest also still lacks machine semantics needed by its own IR tests. P1 requires every failure class to have one legal edge and repair cycles to carry repeat signatures and exhaustion routes (`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:19-20`). The schema can encode only a guard id, optional attempt bound, join group, and reducer (`graph_engineered_subscription_execution.schema.v1.json:81-95`); it has no failure-class mapping, repeat signature, or linked exhaustion target. The actual repair edges contain only `max_attempts`, and the generic system edges are not linked to exhaustion or any declared failure class (`graph_engineered_subscription_execution.plan.v1.yaml:252-266`).

**Impact.** The bootstrap proves only the weaker planning schema. A conforming P1 compiler must reject its own mandated self-compile target, so P2 cannot legally begin. Silently treating future files, missing state producers, or generic failure prose as resolved recreates the historical impossible-baseline and false-compilation-evidence classes.

**Required remediation.** Make future schemas declared artifacts with producer-node ownership rather than resolved files at P1, or ship their contract schemas before P1 and authorize them accordingly. Add `runtime_contract` to P3's actual outputs/state writes or remove the P4 reference. Extend the IR with executable guard/failure mappings, repeat signatures, and explicit exhaustion targets, then make both bootstrap mutations and P1 self-compilation validate producer/consumer totality.

### Critical — C2: P2's required driver/role assurance registry cannot be represented or changed within P2

**Evidence.** P2 consumes `policy/routing/model_registry.v1.yaml`, but its write allowlist contains only the adapter, request/receipt schemas, tests, and result (`graph_engineered_subscription_execution.plan.v1.yaml:126-137`). P2-T13 nevertheless requires the registry to set a minimum assurance per driver and role (`prompts/P2_subscription_worker_adapter.prompt.v1.md:40`).

The current registry has only three OpenAI entries and no Claude driver or assurance field (`policy/routing/model_registry.v1.yaml:10-43`). Its current schema makes each model object `additionalProperties: false` and permits only `provider`, `role`, `strengths`, `reasoning_efforts`, `supports_pro_mode`, and `allowed_for` (`schemas/model_registry.schema.v1.json:34-83`). It therefore cannot encode the required `DRIVER_BOUND_REQUEST`/native assurance policy without changing the registry schema as well. Neither file is a P2 authorized output. P0's scope indirection cannot rescue this because the baseline-contract schema exposes authorized path groups only for P4, P5, and P6 (`contracts/baseline_contract.schema.v1.json:5-13`). P4 is too late: it depends on P3, which depends on P2 passing.

**Impact.** P2 must either fail its own T13, mutate two undeclared paths, or hide routing assurance in adapter code while falsely claiming the registry owns it. This repeats the Plan 20 schema/scope mismatch and impossible-route baseline.

**Required remediation.** Before P2, define and authorize a schema-valid driver/role assurance policy containing both Claude and Codex, or explicitly add the registry and its schema to P2's outputs with dirty-path handling. Add a negative test that the current OpenAI-only registry fails the two-driver contract and that an undeclared assurance field cannot be smuggled past schema validation.

### Critical — C3: Plan 19's mandatory RT-7 stale-path/mirror repair is required but impossible under P6's write and dirty-work contracts

**Evidence.** The historical Plan 19 release prompt makes RT-7 correction a mandatory test. It requires exact before/after criterion text; synchronized changes to at least `policy/deferred.v1.yaml`, `policy/checks.v1.yaml`, `tests/gates/fr_p5_unit.py`, `runtime/readability.py`, and the Plan 03 mirror; and reruns of FR-P2-DEFERRED plus four FR-P5 gates (`plans/19_curriculum_factory_production_loop_closure/prompts/P6_release_proof_debt_reconciliation.prompt.v1.md:163-175`). The live stale text remains in the registry and mirror (`policy/deferred.v1.yaml:98-103`; `plans/03_folder_refactoring/folder_refactoring.plan.v6.md:1359`).

Plan 21 now names RT-7 and the mirror, but requires only FR-P2-DEFERRED and FR-P4-CHECK-MAPPING; it omits the exact before/after record, repeated-site list, and FR-P5-READABILITY/BLOOM-VERBS/DERIVATION/RECEIPT-HASH reruns (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:33`). More fundamentally, P6 may write only fresh test roots, its result, and its supersession document (`graph_engineered_subscription_execution.plan.v1.yaml:226-232`), not the registry, mirror, checks, gate, or readability module. The plan also makes existing dirty work immutable (`:26`), while the repository status already marks three required targets as modified/untracked user work.

**Impact.** P6 cannot pass the historical mandatory repair without either writing outside scope and into protected user paths or weakening “reconcile” into a narrative disposition. That is the exact stale-authority/false-discharge pattern the Plan 19 test was designed to prevent.

**Required remediation.** Give the RT-7 correction a predeclared owner and safe write plan that names every required registry/mirror/code path and addresses current dirty overlaps before mutation. Preserve the exact before/after criterion and all five historical reruns. If user work prevents safe reconciliation, route honestly to the declared plan terminal; do not claim preservation through `supersession.v1.md` alone.

### High — H1: the P6 QA-exhaustion instruction reintroduces the forbidden `BLOCKED` plan-phase route

**Evidence.** The manifest's plan terminals are `PLAN_APPROVED`, `PAUSED_PREREQUISITE`, `SYSTEM_FAILURE`, and `INTERRUPTED` (`graph_engineered_subscription_execution.plan.v1.yaml:46-48`), and its invariant says `BLOCKED` is never a plan-phase target (`:280-282`). P_ALL repeats that rule and assigns contract/runtime defects to `SYSTEM_FAILURE` (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:25-28`). Yet P6 says that unresolved Critical/High findings after round three must “record BLOCKED” (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:38-42`). There is no P6→BLOCKED edge (`graph_engineered_subscription_execution.plan.v1.yaml:251,258,266,273`).

**Impact.** The exact non-convergence case the final review is expected to exercise has two incompatible terminal instructions. An executor must invent an edge, misuse the unit terminal, or disobey the P6 prompt, reproducing the false-block and schema-invalid-status class.

**Required remediation.** Route unresolved final QA to the existing P6 system-failure/exhaustion terminal, or introduce a separately named and schema-declared plan review status with a typed edge. Do not use unit `BLOCKED` for plan QA failure.

### High — H2: the format-aware census contract cannot encode the historical-finding denominator P0 requires

**Evidence.** P0 requires an independent denominator covering historical findings as well as graph structure and process thresholds (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:12-18`). But `coverage_denominator.schema.v1.json` is `additionalProperties: false` and permits only `version`, `source_digest`, `nodes`, `edges`, `guards`, `side_effect_boundaries`, `mutations`, and `process_thresholds`; there is no historical-finding or anomaly denominator (`contracts/coverage_denominator.schema.v1.json:3-15`). A schema-valid output therefore cannot include one.

The sibling findings schema also has no typed aggregate-count/reconciliation structure: it requires `findings` and an unconstrained array of arbitrary anomaly objects (`contracts/historical_findings.schema.v1.json:5-26`). P0-T10 expressly requires item-to-aggregate reconciliation for Plan 19 YAML and the Plan 20 v2 `2 Critical, 1 High`/two-heading anomaly (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:27,34-35`), but the durable contract does not require source-declared counts, reconciliation links, or anomaly evidence/disposition fields.

**Impact.** P0's required coverage record is schema-invalid if complete, while a schema-valid empty/untyped anomaly record can omit the very mismatch the revised test names. P5/P6 can then prove coverage relative to an implementation-shaped list, repeating the regression-suppression pattern.

**Required remediation.** Add required, typed historical-finding and anomaly denominators, source-declared severity counts, reconciliation status/evidence, and immutable source keys/digests. Make P0-T11 and P6-T24 mutate each format and count independently of the produced census.

### High — H3: the revised multi-unit test says interrupt and resume within one process, so it does not require Plan 19's cold `--resume` proof

**Evidence.** Plan 19 requires a three-unit live sequence that is interrupted during the third unit and then completes via `--resume` (`plans/19_curriculum_factory_production_loop_closure/prompts/P4_full_manifest_orchestration.prompt.v1.md:185-194`). Plan 21 instead says the fixture runs “through one `--all` process” while also requiring interrupt/resume (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:31`). Its generic live resume test likewise does not require a new process or the production `--resume` command (`:24`). P3 distinguishes an interrupt checkpoint from replayable resume (`prompts/P3_durable_graph_runtime.prompt.v1.md:22-24`), but no release test kills the first process and proves a second process can resume from durable bytes.

**Impact.** An implementation with only in-process pause/continuation can pass the current words while failing after a real process exit—the durable-resume behavior Plan 19 required and historical QA specifically hardened.

**Required remediation.** Define one run lifecycle, not one OS process: start the three-unit fixture with a real `--all` process, terminate/interrupt it during unit three, then use a separate clean `--resume` process against the same digest-bound root. Prove accepted bytes, manifest position, receipts, and coverage across the process boundary.

## Round-1 remediation status

| v1 finding | Round-2 assessment |
|---|---|
| C1 bootstrap/self-compile | **Partial.** The shipped bootstrap and mutations pass, but C1 above shows the mandatory production self-compile remains impossible. |
| C2 terminal taxonomy | **Partial.** Typed pause/system/interrupt edges now exist; P6's final-QA `BLOCKED` instruction remains contradictory (H1). |
| H1 shared log outside scope | **Closed.** Every phase now writes an immutable result and explicitly forbids shared-log appends; P_ALL writes nothing. |
| H2 multi-unit/exact-four | **Partial.** Exact-four and its 3/5, identity, session, sibling-context, and malformed negatives are present at P6-T22. The three-unit/Arduino test is present, but the process wording omits cold `--resume` (H3). |
| H3 deferred RT/mirror | **Partial.** IDs, mirror, RT-9 fixture, and two gates are named, but the mandatory RT-7 repair is outside scope and drops exact historical reruns (C3). |
| H4 census/anomalies | **Partial.** P0 now calls for format-aware parsing and names the Plan 20 anomaly, but its required denominator is forbidden by its own schema and aggregate anomalies remain untyped (H2). |

## Historical class ownership summary

Issues 001–007 retain named owners through P4-T07–T17, P5-T14/T15, and P6-T09. Dirty-work preservation, live baselines, executing gates, accepted-byte immutability, fail-closed corruption, cross-family isolation, and exact-four review negatives also have explicit tests. Those controls do not cure the three execution blockers above: the phase graph cannot self-compile, P2 cannot establish its routing policy within scope, and the preserved RT-7 contract cannot be executed without unauthorized/protected writes.

Round 3 should rerun both bootstrap commands, producer/consumer and schema-resolution mutations, a schema-valid two-driver registry fixture, the exact two-process three-unit lifecycle, and the complete RT-7 mirror/gate sequence before historical QA can pass.
