# Curriculum Factory Graph v1

## 1. Product identity

This document is the canonical executable curriculum-factory graph. The graph is
the factory. It is not a description of work that later creates a factory.

One activation receives a supplied curriculum and returns either an accepted
curriculum product or a truthful non-success terminal. Producing, checking, or
reading this document is never a successful activation.

```text
ENGINE + CURRICULUM_ROOT + MANIFEST + OUTPUT_ROOT + RUN_MODE + FROZEN_CONTRACTS
  -> this graph
  -> accepted requested unit, or accepted complete workbook, or honest terminal
```

The engine graph contains no curriculum name, subject word, unit identifier, unit
count, or curriculum-specific verifier rule. Unit instances, order, prerequisites,
domain contracts, source needs, visual roles, and curriculum-owned checks are read
from the validated supplied manifest and its declared files.

## 2. Normative repository authority

The controller resolves `ENGINE` from
`meta_prompt/curriculum.prompt.v1.md`. These existing repository inputs are frozen
by content hash before activation:

- `meta_prompt/curriculum.prompt.v1.md` and the three files it declares under
  `meta_prompt/assets/`;
- `policy/calibration.v1.yaml`, `policy/checks.v1.yaml`,
  `policy/controller.v1.yaml`, `policy/failures.v1.yaml`,
  `policy/limits.v1.yaml`, `policy/routes.v1.yaml`, and `policy/deferred.v1.yaml`;
- every file under `policy/routing/` named by the governing prompt;
- `schemas/curriculum.schema.v5.json`, `schemas/lab.schema.v4.json`,
  `schemas/manifest_domain.metaschema.v1.json`,
  `schemas/routing_decision.schema.v2.json`,
  `schemas/execution_log.schema.v2.json`, and
  `schemas/run_lifecycle.schema.v1.json`;
- the supplied manifest; every curriculum-owned schema, verifier, fixture,
  calibration, check inventory, route input, and prose contract that it declares;
- the eight model prompts in section 7 of this graph, resolving each `prompts/...`
  path relative to this graph package directory
  (`plans/25_curriculum_factory_graph/`), never relative to the repository root; and
- the controller/runtime executable bytes used for this activation.

Precedence is the order in `meta_prompt/curriculum.prompt.v1.md`. A lower-ranked
input cannot soften a higher-ranked one. A contradiction is recorded and resolved
by precedence; an irresolvable missing or malformed active contract is
`SYSTEM_FAILURE`.

The existing runtime modules are callable mechanisms, not alternate graph
authority. In particular, the graph uses the contract behavior represented by
`runtime/controller.py`, `runtime/routing.py`, `runtime/checks.py`,
`runtime/checkpoint.py`, `runtime/logger.py`, `runtime/lesson_render.py`,
`runtime/pdf_inspect.py`, `runtime/run_state.py`, and `runtime/workbook.py`.
Where current code can simulate, bypass a cross-family review, accept pending
review, or mark a workbook complete before the evidence below exists, this graph
fails closed. The acceptance rules in section 13 are authoritative for a factory
activation.

## 3. Inputs, modes, and outputs

### 3.1 Required inputs

```text
engine_root: canonical existing directory
curriculum_root: canonical existing directory strictly beneath ENGINE/curricula/
manifest_path: canonical existing active manifest inside curriculum_root
output_root: canonical path strictly beneath ENGINE/outputs/
run_mode:
  kind: ONE_UNIT | ALL_UNITS | RESUME
  requested_unit_id: required only for ONE_UNIT; forbidden for ALL_UNITS
  resume_run_id: required only for RESUME
limits_override: optional values accepted only through flags declared by policy/limits.v1.yaml
interruption_signal: controller-owned external signal
```

For a fresh run, `output_root` must not exist. For `RESUME`, it must contain one
valid run whose immutable identity matches the recomputed identity. The controller
never auto-increments, merges, replaces, or silently reuses an output root.

### 3.2 Successful outputs

- `ONE_UNIT` returns the immutable accepted unit package, shipped unit PDF,
  complete evidence index, checkpoint, and terminal `UNIT_ACCEPTED`.
- `ALL_UNITS` or a resumed full run returns the immutable accepted unit packages
  for the exact manifest denominator, the assembled accepted workbook, its page
  renders and evidence index, final audit, and terminal `COMPLETE`.
- A resumed single-unit run returns the same product and terminal as `ONE_UNIT`.

No other output is success. Source records, intermediate artifacts, prompts,
reviews, check reports, page images, checkpoints, and this graph are evidence or
intermediates only.

## 4. Immutable run identity and compiled expansion

As `D01_VALIDATE_AND_FREEZE_RUN`'s first guarded operation, before any worker or
product activation, the controller canonicalizes and hashes the complete frozen input
set. It computes:

```text
run_id = sha256(
  graph_version + graph_sha256 + eight model-prompt sha256 values
  + canonical engine contract digest map
  + canonical curriculum contract digest map
  + manifest bytes and manifest path
  + output_root canonical path
  + normalized run_mode
  + effective numeric limits
)
```

`run_id`, input digests, mode, output boundary, manifest unit sequence, and
effective limits are write-once. A resume mismatch cannot create a new identity
inside the existing root and routes to `SYSTEM_FAILURE`.

`D02_COMPILE_MANIFEST_RUN` expands the validated `manifest.labs[]` in array order.
For each element it creates a `UnitInstance` keyed by `(run_id, unit_id)` and a
unit subgraph instance keyed by `(run_id, unit_id, artifact_epoch)`. It validates
unique IDs, declared count when present, resolvable and earlier prerequisites,
curriculum-owned domain/config contracts, verifier and fixtures, check inventories,
and declared visual roles. `ONE_UNIT` selects the named instance only after proving
it exists and that its declared prerequisites are available as frozen accepted
inputs or are included in the legal run scope. `ALL_UNITS` selects every instance
in manifest order. Directory enumeration never establishes order.

## 5. Typed state

The controller persists this logical state under `output_root`. Types ending in
`Map` are keyed maps; `AppendLog` never permits replacement or deletion.

```text
RunState {
  identity: WriteOnce<RunIdentity>
  frozen_inputs: WriteOnce<DigestMap>
  effective_limits: WriteOnce<LimitSet>
  effective_run: WriteOnce<EffectiveRun>
  status: Monotonic<INITIALIZING | ACTIVE | REPAIRING | ASSEMBLING | terminal>
  cursor: Monotonic<manifest_ordinal>
  unit_selections: AppendMap<(run_id, manifest_ordinal), UnitKey>

  route_decisions: AppendMap<(node_activation_id), RoutingDecisionV2>
  capability_receipts: AppendMap<(route_id, probe_id), CapabilityReceipt>
  actions: AppendLog<ExecutionLogV2Record>
  checkpoints: AppendMap<(run_id, ordinal), Checkpoint>

  source_requests: AppendMap<(run_id, unit_id, request_id), SourceRequest>
  retrieval_results: AppendMap<(run_id, unit_id, request_id, retrieval_result_id), RetrievalResult>
  source_results: AppendMap<(run_id, unit_id, request_id), SourceWorkerResult>
  admitted_sources: VersionMap<(run_id, unit_id, source_id, version), AdmittedSource>
  source_denominators: VersionMap<(run_id, unit_id, epoch), Denominator>

  unit_artifacts: VersionMap<(run_id, unit_id, artifact_type, version), Artifact>
  unit_heads: MonotonicMap<(run_id, unit_id, artifact_type), version>
  unit_checks: AppendMap<(run_id, unit_id, epoch, check_id), CheckResult>
  unit_page_inventory: VersionMap<(run_id, unit_id, pdf_version), PageInventory>
  unit_review_packets: AppendMap<(run_id, unit_id, epoch, review_id), ReviewPacket>
  unit_reviews: AppendMap<(run_id, unit_id, epoch, review_id), ReviewFindingSet>
  unit_repair_requests: AppendMap<(run_id, unit_id, repair_id), RepairRequest>
  unit_repairs: AppendMap<(run_id, unit_id, repair_id), RepairReceipt>
  unit_status: MonotonicMap<(run_id, unit_id), NOT_STARTED | ACTIVE | ACCEPTED | terminal>
  accepted_units: WriteOnceMap<(run_id, unit_id), AcceptedUnitReceipt>

  workbook_artifacts: VersionMap<(run_id, artifact_type, version), Artifact>
  workbook_heads: MonotonicMap<(run_id, artifact_type), version>
  workbook_checks: AppendMap<(run_id, epoch, check_id), CheckResult>
  workbook_page_inventory: VersionMap<(run_id, pdf_version), PageInventory>
  workbook_review_packets: AppendMap<(run_id, epoch, review_id), ReviewPacket>
  workbook_reviews: AppendMap<(run_id, epoch, review_id), ReviewFindingSet>
  workbook_repair_requests: AppendMap<(run_id, repair_id), RepairRequest>
  workbook_repairs: AppendMap<(run_id, repair_id), RepairReceipt>

  counters: MonotonicMap<CounterKey, nonnegative integer>
  invalidations: AppendMap<(repair_id, artifact_key), InvalidationRecord>
  evidence_index: VersionedAppend<EvidencePointer>
  terminal: WriteOncePerExecutionEpisode<TerminalRecord>
  terminal_history: AppendLog<TerminalRecord>
}
```

Important component types:

```text
Artifact = {owner, type, version, immutable_parent_version?, path, sha256,
            created_by_activation, schema_id?, status}
CheckResult = {check_id, subject_key, subject_sha256, result,
               blocking, executed_at, implementation_id, evidence[]}
result = PASS | FAIL | INVALID | NOT_RUN
PageInventory = {pdf_sha256, declared_page_count, pages[]}
pages[] = {page_number, raster_path, raster_sha256, deterministic_results[]}
ReviewPacket = {review_id, review_denominator_id, subject_sha256s[], rubric_sha256,
                randomized_presentation_seed, authorized_input_paths[]}
ReviewFindingSet = {review_id, subject_sha256s[], rubric_sha256, route_decision_id,
                    randomized_presentation_seed, findings[], verdict}
verdict = PASS | REPAIR_REQUIRED | INVALID
RepairRequest = {repair_id, failed_check_set, owner, allowed_paths[],
                 immutable_parent_versions[], required_child_versions[],
                 invalidated[], retest_order[], attempt, maximum}
RepairReceipt = {repair_id, failed_check_set, owner, allowed_paths[],
                 immutable_parent_versions[], new_versions[], invalidated[],
                 retest_order[], attempt, maximum}
```

## 6. Reducers and write authority

Only controller code applies reducers.

| Reducer | Rule |
| --- | --- |
| `write_once` | First valid write wins. Any later write, even byte-identical, is an integrity failure. |
| `append_unique` | Key must be new and payload must validate. Duplicate or conflicting keys are `SYSTEM_FAILURE`. |
| `advance_head` | Head may move only from version `n` to a newly admitted child version `n+1` with immutable parent `n`. |
| `advance_status` | Only a declared guarded execution edge may advance status; no rollback exists. |
| `increment_before_activation` | Counter increments durably before work begins, so a crash cannot erase an attempt. |
| `join_exact` | Reduce only when every member of the frozen denominator is present once and correlation keys match. Extra, cross-unit, stale, duplicate, failed, invalid, or `NOT_RUN` members prevent the join. |
| `reduce_checks` | Code recomputes the current blocking denominator and its subject hashes. A model verdict is one result, never the aggregate. |
| `accept_once` | Writes an accepted receipt only after section 13's complete conjunction passes. Accepted bytes and receipt never change. |
| `write_terminal_once` | Exactly one terminal is written per execution episode from the guards in section 14. Only an `INTERRUPTED` record may move, byte-unchanged, to append-only `terminal_history` when `D04` starts a validated resume episode. Model output has no terminal field with authority. |

Parallel writes are permitted only to disjoint keys allocated before fan-out. A
worker cannot write state directly: the controller stages its one declared output,
validates it, hashes it, and then applies the reducer.

## 7. Node catalogue

There are exactly eight model-worker node definitions and exactly eight prompt
files. Every other node is deterministic controller work.

### 7.1 Model-worker nodes

| Node | Prompt | Reads | Produces | Failure class |
| --- | --- | --- | --- | --- |
| `M01_RESEARCH_UNIT_SOURCES` | `prompts/research_unit_sources.prompt.v1.md` | one bounded source request for candidate-primary-source discovery, or that request plus controller-supplied retrieval results for interpretation | candidate primary-source locators or one structured source interpretation with claim scopes and locators; only controller-retrieved bytes may be admitted | malformed/extra output retries once; missing external fact may reach prerequisite classification; worker/tool failure is system failure |
| `M02_CREATE_UNIT_DOMAIN_DATA` | `prompts/create_unit_domain_data.prompt.v1.md` | manifest unit, admitted sources, domain schema, manifest-domain config, curriculum calibration | one new curriculum-owned domain artifact | deterministic schema/verifier failure is repairable when owned locally |
| `M03_WRITE_UNIT_CONTENT` | `prompts/write_unit_content.prompt.v1.md` | accepted domain artifact, manifest unit, engine unit schema, calibration, pedagogy/prose contracts | one complete seven-block unit artifact plus derivation and source-claim records | schema/derivation/content check failures are repairable when named |
| `M04_CREATE_UNIT_VISUALS` | `prompts/create_unit_visuals.prompt.v1.md` | one exact visual brief, admitted parent facts, allowed source assets, visual contract | one declared non-authoritative visual artifact and provenance response | only assigned visual may be repaired; exact technical authority is never delegated here |
| `M05_REVIEW_UNIT` | `prompts/review_unit.prompt.v1.md` | frozen current unit artifact, visual assets/receipts, shipped PDF, every page raster, frozen rubric and deterministic results | structured findings about actual output | invalid review retries once; reviewer never accepts or routes |
| `M06_REPAIR_UNIT_ARTIFACT` | `prompts/repair_unit_artifact.prompt.v1.md` | named findings, one owned parent artifact/version, allowed diff, required retests | one child version of the owned artifact | scope escape is system failure; repeated valid defect reaches convergence exhaustion |
| `M07_REVIEW_WORKBOOK` | `prompts/review_workbook.prompt.v1.md` | assembled workbook, every workbook page raster, assembly/coverage manifest, frozen rubric | structured findings about actual workbook | invalid review retries once; reviewer never writes release state |
| `M08_REPAIR_WORKBOOK` | `prompts/repair_workbook.prompt.v1.md` | named workbook-owned findings, immutable accepted-unit hashes, one workbook parent version, allowed diff | one child version of a workbook-owned artifact | any accepted-unit mutation is system failure; repeated defect reaches convergence exhaustion |

### 7.2 Deterministic nodes

| Node | Reads -> writes | Guarded failure route |
| --- | --- | --- |
| `D01_VALIDATE_AND_FREEZE_RUN` | raw inputs -> identity, frozen inputs, logger proof | invalid/missing/escaping input, occupied fresh root, invalid resume root, or logger failure -> `SYSTEM_FAILURE` |
| `D02_COMPILE_MANIFEST_RUN` | frozen manifest/contracts/mode -> effective run and all denominators | invalid manifest, unresolved prerequisite, missing verifier/check/schema, hardcoded or ambiguous expansion -> `SYSTEM_FAILURE` |
| `D03_PROVE_REQUIRED_CAPABILITIES` | effective run/routes -> capability receipts | required route/tool/model/render/retrieval failure -> `SYSTEM_FAILURE` |
| `D04_RESUME_OR_INITIALIZE` | identity/checkpoints -> cursor and active status | hash mismatch, invalid checkpoint, duplicate continuation, accepted overwrite -> `SYSTEM_FAILURE` |
| `D05_SELECT_NEXT_UNIT` | cursor/effective run/accepted units -> selected unit key | no legal selected unit when one is required -> `SYSTEM_FAILURE` |
| `D06_COMPILE_AND_RETRIEVE_SOURCE_REQUESTS` | selected unit/domain requirements -> source request denominator and allowlisted retrieval-result bytes/metadata | retrieval protocol/tool failure or incomplete denominator -> `SYSTEM_FAILURE`; a successful search proving a named required external fact unavailable may reach `D30_CLASSIFY_PREREQUISITE` |
| `D07_ADMIT_SOURCE_JOIN` | all `M01` results -> admitted sources/source checks | unresolved or inadmissible required source -> `D30_CLASSIFY_PREREQUISITE`; malformed identity/join -> `SYSTEM_FAILURE` |
| `D08_VALIDATE_DOMAIN` | `M02` output -> domain checks/admitted domain version | repairable named defect -> `D19_ROUTE_UNIT_REPAIR`; execution/integrity defect -> `SYSTEM_FAILURE` |
| `D09_VALIDATE_UNIT_CONTENT` | `M03` output -> unit schema, derivation, grounding, pedagogy, readability, safety checks | repairable named defect -> `D19_ROUTE_UNIT_REPAIR`; execution/integrity defect -> `SYSTEM_FAILURE` |
| `D10_COMPILE_VISUAL_BRIEFS` | current unit/domain/manifest roles -> visual denominator and briefs | undeclared/unsatisfied role or ambiguous parent -> `SYSTEM_FAILURE` |
| `D11_RENDER_DETERMINISTIC_VISUALS` | exact-fact briefs -> deterministic visual artifacts | renderer/tool/unsupported exact map -> `SYSTEM_FAILURE` |
| `D12_JOIN_AND_VERIFY_VISUALS` | deterministic assets and `M04` outputs -> visual checks/receipts/hashes | repairable visual defect -> `D19_ROUTE_UNIT_REPAIR`; missing/extra/stale/cross-unit asset -> `SYSTEM_FAILURE` |
| `D13_RENDER_UNIT` | current valid unit and visuals -> markdown/PDF/hash | command, missing asset, or render failure -> `SYSTEM_FAILURE` |
| `D14_INSPECT_UNIT_PAGES` | shipped unit PDF -> complete page inventory and deterministic PDF/page checks | content/layout defect -> `D19_ROUTE_UNIT_REPAIR`; tool or inventory failure -> `SYSTEM_FAILURE` |
| `D15_FREEZE_UNIT_REVIEW_PACKET` | current heads/checks/PDF/pages/rubrics -> immutable review denominator and one packet per required independent review | incomplete deterministic or review denominator -> `SYSTEM_FAILURE` |
| `D16_REDUCE_UNIT_EVIDENCE` | current check and review denominator -> PASS or named failure set | incomplete/invalid/stale evidence -> `SYSTEM_FAILURE`; named repairable set -> `D19`; pass -> `D22_ACCEPT_UNIT` |
| `D17_CLASSIFY_UNIT_FINDINGS` | reduced failed checks and ownership map -> repair groups | no unique owner/boundary/retest map -> `SYSTEM_FAILURE` |
| `D18_PLAN_UNIT_REPAIR` | one repair group/limits -> immutable repair request and invalidations | bound reached or repeated non-narrowing set -> `CONVERGENCE_EXHAUSTED` |
| `D19_ROUTE_UNIT_REPAIR` | named failures -> `D17`, then `D18`, then model or deterministic repair owner | classifier/controller/tool failure -> `SYSTEM_FAILURE` |
| `D20_ADMIT_UNIT_REPAIR` | repair output -> new artifact version/head and invalidation records | scope escape, parent mismatch, overwrite, missing child -> `SYSTEM_FAILURE` |
| `D21_RETEST_UNIT_DESCENDANTS` | invalidation records -> activations in frozen topological retest order | retest closure mismatch -> `SYSTEM_FAILURE` |
| `D22_ACCEPT_UNIT` | complete current unit denominator -> accepted receipt/status | any failed acceptance conjunct -> `SYSTEM_FAILURE` |
| `D23_CHECKPOINT_ACCEPTED_UNIT` | accepted receipt/evidence -> atomic checkpoint and lifecycle update | checkpoint/log/hash failure -> `SYSTEM_FAILURE` |
| `D24_COMPUTE_MANIFEST_COVERAGE` | manifest order and accepted receipts -> exact coverage | mismatch in full mode -> `SYSTEM_FAILURE`; more units -> `D05`; exact -> `D25` |
| `D25_ASSEMBLE_WORKBOOK` | exact accepted coverage -> assembly manifest and workbook PDF version | missing/changed/duplicate/out-of-order unit -> `SYSTEM_FAILURE` |
| `D26_RENDER_AND_INSPECT_WORKBOOK_PAGES` | shipped workbook PDF -> raster render of every page, complete page inventory, and deterministic workbook checks | workbook-owned defect -> `D29_ROUTE_WORKBOOK_REPAIR`; tool/inventory failure -> `SYSTEM_FAILURE` |
| `D27_FREEZE_WORKBOOK_REVIEW_PACKET` | workbook/coverage/pages/rubrics -> immutable review denominator and one packet per required independent review | incomplete denominator -> `SYSTEM_FAILURE` |
| `D28_REDUCE_WORKBOOK_EVIDENCE` | workbook checks and `M07` review -> PASS or named failure set | invalid/stale/incomplete evidence -> `SYSTEM_FAILURE`; repairable -> `D29`; pass -> `D32` |
| `D29_ROUTE_WORKBOOK_REPAIR` | named workbook findings/ownership/limits -> repair request | no unique workbook owner or bound reached -> `SYSTEM_FAILURE` or `CONVERGENCE_EXHAUSTED` as classified |
| `D30_CLASSIFY_PREREQUISITE` | failed source need and retrieval evidence -> prerequisite or system classification | only named unavailable externally supplied safety-critical fact -> `PAUSED_PREREQUISITE`; otherwise -> `SYSTEM_FAILURE` |
| `D31_ADMIT_WORKBOOK_REPAIR` | `M08` output -> new workbook version/head and invalidations | accepted-unit hash change, scope escape, overwrite -> `SYSTEM_FAILURE` |
| `D32_FINAL_RELEASE_AUDIT` | all frozen inputs, raw evidence, accepted units, workbook, pages/review -> release recomputation | any mismatch/missing result -> `SYSTEM_FAILURE`; complete conjunction -> `COMPLETE` |

Terminals are graph vertices. They receive only the controller-created terminal
record and write no artifact.

## 8. Execution graph and edges

```text
START
 -> D01_VALIDATE_AND_FREEZE_RUN
 -> D02_COMPILE_MANIFEST_RUN
 -> D03_PROVE_REQUIRED_CAPABILITIES
 -> D04_RESUME_OR_INITIALIZE
 -> D05_SELECT_NEXT_UNIT
 -> D06_COMPILE_AND_RETRIEVE_SOURCE_REQUESTS
 -> fan_out M01_RESEARCH_UNIT_SOURCES(request_id)
 -> D07_ADMIT_SOURCE_JOIN(unit_id, source_denominator_id)
 -> M02_CREATE_UNIT_DOMAIN_DATA
 -> D08_VALIDATE_DOMAIN
 -> M03_WRITE_UNIT_CONTENT
 -> D09_VALIDATE_UNIT_CONTENT
 -> D10_COMPILE_VISUAL_BRIEFS
 -> fan_out [D11_RENDER_DETERMINISTIC_VISUALS | M04_CREATE_UNIT_VISUALS](visual_id)
 -> D12_JOIN_AND_VERIFY_VISUALS(unit_id, visual_denominator_id)
 -> D13_RENDER_UNIT
 -> D14_INSPECT_UNIT_PAGES
 -> D15_FREEZE_UNIT_REVIEW_PACKET
 -> fan_out M05_REVIEW_UNIT(review_id)
 -> D16_REDUCE_UNIT_EVIDENCE
      | named repairable failures
      -> D19_ROUTE_UNIT_REPAIR -> D17_CLASSIFY_UNIT_FINDINGS
         -> D18_PLAN_UNIT_REPAIR
         -> [M06_REPAIR_UNIT_ARTIFACT | deterministic owner]
         -> D20_ADMIT_UNIT_REPAIR
         -> D21_RETEST_UNIT_DESCENDANTS
         -> first invalidated descendant
      | complete pass
      -> D22_ACCEPT_UNIT -> D23_CHECKPOINT_ACCEPTED_UNIT
         -> D24_COMPUTE_MANIFEST_COVERAGE
              | ONE_UNIT target accepted -> UNIT_ACCEPTED
              | ALL_UNITS and more manifest units -> D05_SELECT_NEXT_UNIT
              | ALL_UNITS exact accepted coverage -> D25_ASSEMBLE_WORKBOOK
 -> D25_ASSEMBLE_WORKBOOK
 -> D26_RENDER_AND_INSPECT_WORKBOOK_PAGES
 -> D27_FREEZE_WORKBOOK_REVIEW_PACKET
 -> fan_out M07_REVIEW_WORKBOOK(review_id)
 -> D28_REDUCE_WORKBOOK_EVIDENCE
      | named workbook-owned failures
      -> D29_ROUTE_WORKBOOK_REPAIR -> M08_REPAIR_WORKBOOK
         -> D31_ADMIT_WORKBOOK_REPAIR
         -> D25_ASSEMBLE_WORKBOOK
      | complete pass
      -> D32_FINAL_RELEASE_AUDIT -> COMPLETE
```

Universal edges:

- an external interruption observed between atomic operations routes from any
  active node to a committed checkpoint and `INTERRUPTED`;
- a missing required external safety-critical fact may reach
  `D30_CLASSIFY_PREREQUISITE` only from source admission or an explicit
  curriculum-owned physical-signoff check;
- contract, controller, route, worker, schema engine, renderer, join, evidence,
  state, or tool faults route to `SYSTEM_FAILURE`, never prerequisite pause;
- repair exhaustion routes only to `CONVERGENCE_EXHAUSTED`.

## 9. Guards, fan-outs, joins, and correlation

| Edge | Exact guard |
| --- | --- |
| `START -> D01` | all raw required arguments present |
| `D01 -> D02` | logger gate passed; canonical roots legal; frozen digests committed |
| `D02 -> D03` | effective run closed; all manifest instances and denominators derived |
| `D03 -> D04` | every route/tool required by the effective run has a current real capability receipt |
| `D04 -> D05` | fresh state created or resume prefix verified without changing accepted bytes |
| `D05 -> D06` | selected unit is the next legal manifest instance and prerequisites are accepted |
| `D06 -> M01[*]` | one activation per frozen source request with only its allowlisted retrieval results; counter incremented first |
| `M01[*] -> D07` | join key `(run_id, unit_id, source_denominator_id, request_id)`; every request exactly once |
| `D07 -> M02` | every required source admitted, hashed, scoped, and in the current denominator |
| `D08 -> M03` | domain schema and curriculum verifier both pass on the same domain hash |
| `D09 -> D10` | complete unit artifact is schema-valid and current pre-visual checks have one result |
| `D10 -> visual fan-out` | one activation per declared visual role with exactly one assigned owner |
| visual fan-out `-> D12` | join key `(run_id, unit_id, visual_denominator_id, visual_id)`; exact denominator |
| `D12 -> D13` | every required visual exists; provenance and artifact hashes resolve |
| `D14 -> D15` | shipped PDF hash fixed; declared page count equals every successfully rasterized page; no page omitted |
| `D15 -> M05[*]` | deterministic unit denominator complete; review denominator frozen from active checks/rubrics; author route family excluded where cross-family review is required |
| `M05[*] -> D16` | join key `(run_id, unit_id, review_denominator_id, review_id)`; every structured review valid, isolated, and bound to exact artifact/PDF/page hashes |
| `D16 -> D22` | all unit acceptance conjuncts in section 13.1 true |
| `D16 -> D19` | at least one named repairable current failure and no nonrepairable failure |
| `D18 -> repair` | unique owner, allowed boundary, immutable parent, invalidations, retest order, and remaining counter all exist |
| `D20 -> D21` | exactly one owned child version admitted and unchanged paths match their prior hashes |
| `D21 -> descendant` | activate only the earliest invalidated node; later descendants remain `NOT_RUN` until reached |
| `D23 -> D24` | accepted receipt and checkpoint hashes agree and lifecycle record includes the unit once |
| `D24 -> UNIT_ACCEPTED` | mode is single-unit and its exact requested unit is accepted |
| `D24 -> D05` | mode is full and a later manifest unit is not yet accepted |
| `D24 -> D25` | accepted unit IDs and hashes equal the full ordered manifest exactly |
| `D26 -> D27` | every shipped workbook page is raster-rendered, inventoried, and deterministically inspected |
| `D27 -> M07[*]` | coverage, assembly, PDF, page inventory, review denominator, and rubric digests are frozen |
| `M07[*] -> D28` | join key `(run_id, workbook_epoch, review_denominator_id, review_id)`; every required isolated review is valid and bound to the current workbook and every page |
| `D28 -> D32` | all workbook acceptance conjuncts in section 13.2 true |
| `D29 -> M08` | named workbook-owned defects only, accepted-unit hashes frozen, remaining counter |
| `D31 -> D25` | one new workbook-owned version admitted; every accepted-unit hash unchanged |
| `D32 -> COMPLETE` | independent deterministic recomputation proves section 13.3 exactly |

Research and visual fan-outs allocate their denominator and child keys before
dispatch. Composition is serial per unit. No join accepts a result correlated only
by filename, ordinal, conversation, or worker-provided identity.

## 10. Context graph

Execution adjacency confers no context. The controller creates a fresh isolated
request for each model activation and exposes only these edges:

Every model node also receives its immutable activation envelope and the validated
routing decision for that activation. Those records provide identity and containment,
not additional curriculum context or control authority.

| Model node | Authorized context edges | Explicitly absent |
| --- | --- | --- |
| `M01` | `SourceRequest.question`, allowed retrieval-result bytes/metadata, admission rules, response contract | manifest siblings, author/reviewer history, other requests, acceptance state |
| `M02` | selected manifest unit, current admitted sources, curriculum domain schema, manifest-domain config, curriculum calibration, curriculum prose calibration explicitly admitted by precedence | sibling units except declared accepted prerequisite projection, hidden fixtures, reviewer output, terminal state |
| `M03` | accepted domain artifact, selected manifest unit, engine lab schema, engine calibration, `unit_prose.v1.md`, `pedagogy.v1.md`, admitted source locator projection, current visual-role list | author history, sibling unit bodies, reviewer output, hidden tests, routing/terminal authority |
| `M04` | one `VisualBrief`, exact parent facts/pointers, admitted source assets for that brief, required size/format/accessibility/provenance fields | unrelated unit prose, unassigned visuals, unsafe technical facts not in the brief, verdicts, acceptance authority |
| `M05` | frozen current domain/unit/visual artifact bytes, source/derivation/receipt evidence, shipped PDF, every rasterized page, deterministic result set, frozen rubric, randomized presentation order | author or repair conversation, prior versions, sibling verdicts, expected terminal, controller preference |
| `M06` | named current findings, exactly one owned parent artifact and version, allowed change boundary, immutable dependencies, required retest list, output contract | unrelated artifacts, sibling unit content, acceptance state, broad regeneration authority |
| `M07` | exact coverage and assembly manifest, assembled workbook bytes, every workbook page raster, deterministic workbook results, frozen rubric, randomized presentation order | unit author history, unit review discussions, proposed release state, controller preference |
| `M08` | named workbook-owned findings, one workbook parent version, immutable accepted-unit hash list, allowed workbook diff, required retests | mutable unit source/content/assets/PDFs, author history, terminal authority |

Workers receive no repository-wide filesystem view. Their readable paths are the
staged authorized inputs; their writable surface is one preallocated output target.
Undeclared read, extra write, path escape, or output substitution prevents admission.

## 11. Repair and invalidation

The controller compiles an `OwnershipAndInvalidationMap` from artifact contracts
and the current check catalogues. Every repairable check must resolve to exactly one
row before live work:

| Owner family | May change | Immutable parent | Invalidates and retests in order |
| --- | --- | --- | --- |
| `source_interpretation` | one source-result interpretation, not cached source bytes | prior source result and retrieval hash | source admission -> domain -> unit -> affected visuals -> unit render/pages -> unit review -> reduction |
| `domain` | one unit domain artifact | prior domain version and admitted source hashes | domain schema/verifier -> unit content -> visuals derived from changed facts -> render/pages -> review -> reduction |
| `unit_content` | one unit content artifact, restricted to named JSON pointers | prior unit version and domain hash | unit schema/derivation/grounding/pedagogy/safety -> affected visuals -> render/pages -> review -> reduction |
| `unit_visual` | one named visual asset/receipt or visual metadata pointer | prior asset version, unit/domain hashes | visual hash/provenance -> render -> every unit page check -> review -> reduction |
| `unit_layout` | unit-owned render source/style only | accepted content/domain/visual hashes | render -> every unit page check -> review -> reduction |
| `workbook` | front matter, TOC, navigation, pagination, workbook style, assembly metadata | accepted unit packages and hashes | assembly coverage/hashes -> render every workbook page -> workbook review -> final audit |

Each repair request binds owner, allowed paths or JSON pointers, immutable parent
version, new required version, invalidated descendants, retest order, attempt, and
maximum. `policy/limits.v1.yaml` supplies the biting bound: the controller increments
before dispatch, stops before exceeding it, and also stops when the same failed-check
set repeats without narrowing at the declared threshold. Both routes end at
`CONVERGENCE_EXHAUSTED` with the last valid checkpoint.

A local failure never reactivates an ancestor outside its invalidation set. A
workbook repair cannot reopen, rewrite, or reaccept a unit. A repair model cannot
change its own allowed diff, counters, retest set, check results, or owner.

### 11.1 Complete loop catalogue

| Cycle | Durable counter key | Frozen maximum | Exit when exhausted |
| --- | --- | --- | --- |
| malformed model response retry | `(activation_id, malformed)` | `policy/limits.v1.yaml -> retry.malformed_structured_output.value` | `SYSTEM_FAILURE`; malformed output never enters state |
| transient source or visual capability retry | `(activation_id, transient)` | `policy/limits.v1.yaml -> retry.transient_worker_source_or_image_failure.value` | `SYSTEM_FAILURE`; only a successfully completed source search may be considered by `D30` |
| unit repair/retest | `(run_id, unit_id, failed_check_fingerprint)` plus total unit revisions | `per_lab.max_revisions.value` and `convergence.repeat_failure_threshold.value` | `CONVERGENCE_EXHAUSTED` before the next attempt |
| workbook repair/review | `(run_id, workbook_failed_check_fingerprint)` plus total workbook revisions | `convergence.max_meta_revision_cycles.value` and `convergence.repeat_failure_threshold.value` | `CONVERGENCE_EXHAUSTED` before the next attempt |
| manifest unit iteration | `cursor.manifest_ordinal` | length of `effective_run.ordered_unit_ids` | `UNIT_ACCEPTED` for the selected one-unit target, or workbook path after exact full coverage; it cannot cycle past the manifest |

Every counter is initialized by `D02`, incremented and checkpointed before its
activation, and never decremented on retry, interruption, or resume. There is no other
execution cycle.

## 12. Check and page denominators

`D02` compiles denominators from the engine inventory, curriculum inventory,
manifest declarations, schemas, verifier, routes, rubrics, and artifact contracts.
It does not use a model-generated checklist. At each reduction, code recomputes the
denominator and current subject hashes.

Every required item has exactly one current result. `PASS` is current only when its
subject hash equals the current head. A flag-only check such as
`TEXT-BLOOM-VERBS` must execute and record its findings but does not become blocking.
Missing, duplicate, stale, invalid, failed, or `NOT_RUN` blocking evidence prevents
acceptance.

For pages, the denominator is the page count read from the exact shipped PDF. The
controller rasterizes that PDF, assigns contiguous page numbers, hashes every raster,
and requires deterministic and review coverage for every page. Sampling is illegal.
A PDF that cannot yield a complete inventory is a system/tool failure, not a passed
zero-page product.

## 13. Acceptance conditions

### 13.1 Exact unit acceptance

`D22_ACCEPT_UNIT` may write one `AcceptedUnitReceipt` if and only if all are true for
the same current epoch and hashes:

1. the unit is the legal selected manifest unit and its prerequisites are accepted;
2. every required source request has one admitted primary-source result with cached
   bytes, locator, scope, access record, and resolving hash;
3. the current domain artifact passes the curriculum domain schema and the declared
   deterministic verifier proven against all declared fixtures;
4. the current unit contains all seven required blocks and passes the engine lab
   schema and curriculum domain schema;
5. every rendered factual claim resolves to its single domain parent, and every
   source-critical or numeric claim resolves to admitted supporting source bytes;
6. all current curriculum-owned domain checks, pedagogy/readability checks, safety
   checks, and engine checks have complete results; every blocking result is `PASS`;
7. every manifest-declared visual role resolves to an actual current artifact; exact
   technical facts come from deterministic renders; provenance and receipt hashes
   resolve to shipped bytes;
8. the shipped unit PDF hash resolves, its page count is positive, and every shipped
   page is rasterized, hashed, nonblank, legible, unclipped, and in the page denominator;
9. every review in the compiled unit review denominator is structurally isolated,
   valid, bound to its frozen rubric, and examines the actual frozen unit, actual
   shipped PDF, and every page; every required cross-family condition holds and no
   review returns a blocking finding;
10. all repair attempts and invalidation/retest histories are complete, within bound,
    and leave no stale descendant result;
11. the action log is append-only, monotonic, paired, and covers every activation,
    route decision, transition, repair, render, checkpoint, and terminal decision;
12. the acceptance receipt binds the unit/domain/visual/PDF/page/evidence hashes and
    is written once by controller code.

### 13.2 Exact workbook acceptance

`D28_REDUCE_WORKBOOK_EVIDENCE` may pass only if:

1. accepted unit IDs and hashes equal the ordered manifest exactly, with no missing,
   duplicate, extra, changed, pending-review, blocked, or out-of-order unit;
2. the assembly manifest binds each immutable accepted unit PDF exactly once and the
   assembled workbook hash resolves;
3. every workbook-owned deterministic check has one current `PASS` result;
4. the exact shipped workbook has a positive page inventory and every page is
   rasterized, hashed, inspected, and included in the denominator;
5. every review in the compiled workbook review denominator is valid, isolated,
   examines the actual assembled workbook and every page under its frozen rubric, and
   has no blocking finding;
6. workbook repair history changes only workbook-owned artifacts, stays within bound,
   and all invalidated checks were rerun; and
7. every accepted unit hash still equals its `AcceptedUnitReceipt`.

### 13.3 Final release

`D32_FINAL_RELEASE_AUDIT` independently recomputes the run identity, frozen digests,
manifest order, accepted-unit coverage, current heads, source/artifact/receipt hashes,
check denominators, page denominators, review bindings, repair histories, action-log
integrity, workbook hash, and terminal guard from raw records. It does not trust prior
aggregate verdict fields. `COMPLETE` is written only when that recomputation proves
sections 13.1 and 13.2 for the full manifest.

## 14. Explicit terminals

| Terminal | Sole reachability guard | Meaning |
| --- | --- | --- |
| `UNIT_ACCEPTED` | `ONE_UNIT` target has a section 13.1 accepted receipt and atomic checkpoint | The requested unit product is accepted; no workbook claim is made. |
| `COMPLETE` | `D32` independently proves exact full-manifest coverage and accepted workbook release | The complete workbook product is accepted. |
| `INTERRUPTED` | external interruption observed and the last complete atomic checkpoint plus exact resume identity were durably written | Work stopped externally; no acceptance beyond existing receipts is implied. |
| `PAUSED_PREREQUISITE` | `D30` proves a named externally supplied safety-critical fact is unavailable after declared source attempts and emits a resume requirement | The curriculum needs an external fact; factory/tool/worker defects are excluded. |
| `CONVERGENCE_EXHAUSTED` | a frozen repair maximum would be exceeded or the declared repeated non-narrowing failure threshold is met | Valid repair attempts did not converge; no new acceptance is claimed. |
| `SYSTEM_FAILURE` | contract, route, worker, tool, schema engine, verifier execution, renderer, state, join, log, hash, evidence, containment, or integrity failure | The factory failed; this is never relabeled as a curriculum prerequisite. |

The terminal record contains `run_id`, terminal, guard evidence, last checkpoint,
accepted product pointers if any, remaining work, and exact resume instruction when
resumable. No worker may emit or modify it. There is no prompt-, graph-, design-,
report-, or capability-success terminal.

## 15. Resume semantics

Every deterministic or model activation is preceded by a logged start and durable
counter increment and followed by output admission, a logged close, and an atomic
checkpoint at the declared boundary. A checkpoint binds run identity, graph position,
current heads, accepted receipts, input/output hashes, counters, and next legal node.

On `RESUME`, `D04` validates the complete checkpoint prefix and all referenced bytes.
It preserves accepted units byte-for-byte, discards no append-only evidence, and
reactivates the first incomplete or invalidated legal node exactly once. An activation
whose output was admitted before interruption is not rerun. Changed frozen input,
corrupt prefix, out-of-order cursor, consumed continuation, or attempt to overwrite
accepted work is `SYSTEM_FAILURE`.

## 16. Controller conformance assertions

An executor must establish all of these before reporting this graph runnable:

1. the eight model nodes map one-to-one to the eight prompt files in section 7;
2. no deterministic node has a prompt file;
3. every node in section 7 has state reads/writes, an execution edge, applicable
   context, and a failure route;
4. every fan-out has a frozen denominator and every join has the stated correlation
   key;
5. every cycle has a monotonic counter, numeric maximum, and exhaustion route;
6. manifest mutation changes the effective-run digest and expansion without an
   engine graph edit;
7. no model can route, join, aggregate, accept, checkpoint, resume, assemble, audit,
   or write terminal state;
8. no success terminal is reachable without the accepted curriculum product named
   by that terminal; and
9. a plan, prompt, graph document, capability probe, simulation, visualization, or
   review report cannot satisfy any acceptance conjunction.
