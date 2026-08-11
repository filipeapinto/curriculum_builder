# Plan 26 — LangGraph Curriculum Factory

Status: implementation specification, version 1

Date: 2026-08-11

Baseline: Plan 25 and its current runtime implementation remain unchanged
Normative keywords: **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are binding as used below.

## 0. Governing decision

**The compiled LangGraph graph is the curriculum factory.** It accepts a frozen engine/curriculum/run envelope and produces admitted evidence, accepted unit packages, and, for a full run, one accepted workbook. LangGraph does not manage a project that later creates a factory. A CLI may validate invocation syntax, acquire a run lock, compile the graph, and invoke it; it may not implement a parallel pipeline, infer acceptance, or turn implementation activity into product success.

Only actual curriculum products can be successful:

- `UNIT_ACCEPTED` means the requested unit, after its complete transitive prerequisite closure was executed in manifest order, has a current accepted receipt and shipped PDF.
- `COMPLETE` means the workbook covers the full active manifest exactly and has passed final release recomputation.

A graph definition, compiled graph, prompt, capability probe, simulation, test, checkpoint, review report, or implementation milestone is never product success.

## 1. Scope and non-goals

### 1.1 Scope

Plan 26 replaces the custom Plan 25 orchestration mechanics with a compiled `StateGraph` while preserving the Plan 25 curriculum-factory product boundary. It specifies:

1. a manifest-neutral graph whose runtime unit sequence is data, not graph structure;
2. typed checkpointed state with code-owned reducers and guards;
3. eight, and only eight, model job types transported through `codex exec` or `gemini`;
4. deterministic retrieval, admission, validation, rendering, evidence reduction, repair planning, acceptance, assembly, and terminal authority;
5. local durable LangGraph checkpoints plus repository-specific append-only product evidence;
6. bounded targeted repair and exact resume behavior; and
7. one production CLI-to-graph path.

The factory input is the canonical engine root, one supplied curriculum directory or exact active manifest, one fresh or resumable output root, mode (`one`, `all`, or `resume`), optional requested unit ID, and the frozen policies, schemas, routes, checks, limits, prompts, curriculum contracts, executable identities, and hashes selected by code.

For `one`, `D02_COMPILE_EFFECTIVE_RUN` MUST recursively compute the target's complete transitive prerequisite closure from manifest `prerequisites`, reject cycles or unknown IDs, and filter the full manifest order by closure membership. It MUST NOT hardcode a curriculum name, subject, unit count, unit ID, or sequence.

### 1.2 Explicit non-goals and rejected designs

The following are prohibited:

- project-management phase graphs such as “specify, implement, test, promote”;
- prompt evolution, candidate comparison, prompt/graph promotion, or graph candidates;
- implementation completion, test completion, or factory compilation as success;
- simulation or fake-model evidence as curriculum product evidence;
- model-selected routing, joins, retries, validation, acceptance, checkpointing, resume, assembly, release, or terminals;
- LangChain chat-model wrappers, `ChatOpenAI`, `ChatGoogleGenerativeAI`, provider SDKs, or direct HTTP model APIs;
- a second non-LangGraph production pipeline or silent fallback to the legacy FSM;
- in-place repair of a current or accepted artifact; and
- workbook repair that changes an accepted unit or unit PDF.

Plan 23 remains historical design input, Plan 24 remains historical project-plan input, and Plan 25 remains the current baseline until Plan 26 is implemented and activated. This specification changes none of them.

## 2. Evidence-based baseline assessment

### 2.1 What Plan 25 gets right

[`plans/25_curriculum_factory_graph/curriculum_factory.graph.v1.md`](../25_curriculum_factory_graph/curriculum_factory.graph.v1.md) correctly establishes the graph as the factory, manifest-neutral effective runs, deterministic authority, eight model job types, bounded joins and repair cycles, actual all-page review, immutable accepted units, exact workbook coverage, and the six-terminal vocabulary. Its state/reducer sections, context graph, denominators, and unit/workbook acceptance lists are retained as product requirements. [`qa_criteria.v1.md`](../25_curriculum_factory_graph/qa_criteria.v1.md) correctly rejects `NOT_RUN`, stale evidence, review bypass, incomplete joins, and success without shipped curriculum output. The current Plan 25 prompts correctly separate Codex authoring/repair from Gemini review; Plan 26 relocates equivalent prompts into its package rather than resolving a repository-root `prompts/` directory.

Plan 23's useful contributions are typed reducer semantics, distinct execution and context graphs, denominator-first fan-out/join, and bounded cycles. Its candidate/promotion product is rejected. Plan 24's useful contribution is its explicit implementation dependency ordering; its `FACTORY_PROVEN` project graph is not the production factory and is rejected.

### 2.2 What the current controller implements

[`runtime/curriculum_factory_graph.py`](../../runtime/curriculum_factory_graph.py) is a handwritten Plan 25 controller. `CurriculumFactoryGraph.run()` performs D01–D32/M01–M08 in Python loops. `_activate()` owns activation counters, log pairs, and manual snapshots; `_model()` owns malformed-output retry; `_produce_unit()` and `_workbook()` own iteration, repair routing, and termination. It already:

- resolves the active manifest and derives a one-unit prerequisite closure in manifest order;
- freezes input hashes and a run identity;
- uses `codex exec` for authoring/research/visual/repair work and `gemini` for review through [`runtime/model_worker.py`](../../runtime/model_worker.py);
- retrieves source bytes in the controller, hashes/admission-checks them, creates versioned artifacts, runs repository checks, creates deterministic visual maps, renders PDF, rasterizes and inspects pages, reviews actual page images, and assembles a workbook; and
- writes state, events, checkpoints, receipts, evidence, and one Plan 25 terminal.

[`runtime/factory_state.py`](../../runtime/factory_state.py) implements a monolithic atomic JSON state document plus append-only JSONL events and custom reducers. [`runtime/checkpoint.py`](../../runtime/checkpoint.py) implements ordinal JSON snapshots and a hash chain. [`runtime/run_curriculum.py`](../../runtime/run_curriculum.py) exposes both the live controller and legacy simulation flags.

### 2.3 Reuse, adaptation, replacement

| Mechanism | Plan 26 disposition | Reason |
|---|---|---|
| `controller.CurriculumRuntime` manifest/schema/domain resolution and static preflight | adapt behind deterministic nodes | repository contract knowledge remains valid; lifecycle ownership moves to the graph |
| `routing.Selector` code-owned route validation | reuse/adapt | model-family policy remains deterministic |
| `checks.py` schema, derivation, grounding, readability, Bloom, receipt, raster checks | reuse unchanged where signatures permit | product-specific deterministic QA |
| `lesson_render.py`, `pdf_inspect.py`, `visual_maps.py` | reuse/adapt | rendering, page/asset inspection, and deterministic visuals remain repository-specific |
| curriculum `verifier.py`, fixtures, schemas, calibration, circuit libraries | reuse unchanged | curriculum-owned executable contract |
| `logger.ExecutionLogger` append-only ACT/EXEC evidence and audit | reuse/adapt | LangGraph checkpoints are not an audit log |
| `io.py` hashing, canonical paths, atomic writes | reuse unchanged | deterministic containment and integrity |
| `model_worker.CodexWorker` and `GeminiReviewer` subprocess/staging concepts | adapt into package transport | CLI transport is correct; receipts, identity observation, authorization, and isolation require strengthening |
| `CurriculumFactoryGraph.run`, `_activate`, `_model`, `_produce_unit`, `_workbook` | replace | these are custom orchestration, branching, retry, loop, and join mechanics |
| `FactoryStateStore` as production state/reducer engine | replace | `StateGraph` channels and reducers own state updates |
| `Checkpoints` as production cursor/resume engine | replace | `SqliteSaver` and `StateSnapshot.next/tasks` own durable graph progress |
| repository append-only events, route/execution receipts, artifact manifests, acceptance receipts, terminal ledger | retain and strengthen | product evidence is durable, inspectable, and hash-correlated separately from graph recovery |
| `controller.simulate`, `--test-simulated*`, `session_bridge.py`, `CROSS_FAMILY_BYPASS`, `ACCEPTED_PENDING_REVIEW` | historical/test compatibility only; prohibited in Plan 26 production | each can bypass the actual product denominator |
| `workbook.assemble()` terminal behavior | replace; PDF concatenation may be extracted | the legacy helper can claim completion without Plan 26 workbook review/release evidence |

### 2.4 Baseline mismatches Plan 26 must correct

1. The runtime is not LangGraph and manually reconstructs continuation rather than using checkpointed scheduled tasks.
2. Current accepted-unit receipts do not prove the entire Plan 25 denominator, append-log integrity, and checkpoint correlation in one recomputed record.
3. Current unit repair classification selects one priority owner rather than mapping every named finding exactly once and proving a complete partition.
4. Route receipts record the selected model but do not independently observe and prove the model actually executed; Gemini identity is asserted rather than observed from CLI output.
5. Source discovery/retrieval and external curriculum/page transmission have no frozen, explicit per-provider authorization gate.
6. Some source/tool failures are classified as missing prerequisite evidence; only a named unavailable required external fact may pause. Tool, transport, schema, or integrity faults are system failures.
7. Current manual resume re-enters coarse Python loops. Plan 26 resumes from the persisted LangGraph task frontier and current artifact heads without overwriting accepted bytes.
8. `run_state.py` treats `ACCEPTED_PENDING_REVIEW` as complete, `session_bridge.py` can bypass cross-family review, and the legacy workbook path can complete after weak checks. None may be reachable from Plan 26.
9. Model staging captures only partial process evidence and current repair boundaries can be broader than exact JSON pointers/files plus descendants.
10. The repository has no packaging or lock file and LangGraph is neither declared nor installed. Plan 26 must introduce a reproducible dependency contract during implementation, not in this specification pass.

## 3. Dependency and official API contract

### 3.1 Selected versions

| Class | Required direct package | Exact version | Use |
|---|---|---:|---|
| core runtime | `langgraph` | `1.2.9` | `StateGraph`, typed reducers, `START`, `END`, conditional routing, loops, `Send`, compiled execution |
| checkpoint persistence | `langgraph-checkpoint-sqlite` | `3.1.0` | synchronous `SqliteSaver` below the output root |
| existing runtime/test stack, made explicit in lock | `jsonschema`, `PyYAML`, `Pillow`, `pytest` | `4.26.0`, `6.0.3`, `12.2.0`, `9.0.3` | current repository imports and tests; pytest is development-only |

Python is pinned to `>=3.13,<3.14` for Plan 26 reproducibility (the inspected environment is 3.13.1); both selected LangGraph packages support Python 3.10 or newer. `langgraph-checkpoint` and other transitive packages MUST be resolved once and hash-locked, not added as an independently floating direct requirement.

Forbidden model-invocation dependencies include `langchain`, `langchain-openai`, `langchain-google-genai`, `openai`, `google-generativeai`, and any HTTP client introduced to call a model endpoint. A transitive `langchain-core` package required internally by LangGraph does not authorize use of chat-model wrappers. Repository HTTP retrieval remains permitted only for deterministic primary-source retrieval.

### 3.2 Reproducible installation

Implementation MUST add `requirements/plan26.in` containing exact direct pins and `requirements/plan26.lock` containing the complete transitive resolution with hashes. Installation is `python3 -m pip install --require-hashes -r requirements/plan26.lock` into an isolated Python 3.13 environment. CI compares a regenerated lock against the committed lock and fails on drift. No dependency is installed by this specification pass.

Before activation, an API-contract test MUST import the exact pinned wheels and prove the selected signatures/behavior. Failure blocks implementation activation; it does not select a fallback version.

### 3.3 Selected official API surface

The implementation uses only:

- `StateGraph(State, context_schema=RuntimeContext, input_schema=FactoryInput, output_schema=FactoryOutput)`, channel reducers declared with `typing.Annotated`, and `compile(checkpointer=..., name="plan26_curriculum_factory")`;
- `from langgraph.graph import StateGraph, START, END`;
- `add_node`, `add_edge`, and `add_conditional_edges` for normal edges, branches, and loops;
- `from langgraph.types import Send` for denominator-first dynamic fan-out;
- `CompiledStateGraph.invoke`, `get_state`, and `get_state_history` for execution and read-only recovery inspection;
- `from langgraph.checkpoint.sqlite import SqliteSaver`, constructed over `sqlite3.connect(path, check_same_thread=False)`, plus its read-only `get_tuple`/`list` methods to inspect prior checkpoints and pending writes.

No subgraph is selected for v1: one graph and the official root checkpoint namespace make resume and evidence correlation auditable. Map/reduce follows the official pattern: a conditional edge returns `Send` packets to one worker node and that worker has a normal edge to a deterministic reducer/barrier. Visual work uses two sequential map/reduce supersteps—D11 deterministic briefs first, then M04 eligible model briefs—around D12; it never uses a multi-start static edge with dynamic `Send` instances. Product retries are explicit graph cycles; LangGraph `RetryPolicy` is not configured for product nodes because invisible automatic retries would evade durable counters and execution receipts.

Official sources verified on 2026-08-11:

- [LangGraph PyPI release and Python requirement](https://pypi.org/project/langgraph/)
- [LangGraph overview; LangGraph can be used without LangChain](https://docs.langchain.com/oss/python/langgraph/overview)
- [StateGraph API](https://reference.langchain.com/python/langgraph/graph/state/StateGraph)
- [StateGraph compile API](https://reference.langchain.com/python/langgraph/graph/state/StateGraph/compile)
- [Graph API: edges, conditional edges, loops, Send](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [Official Send map/reduce worker-to-reducer example](https://docs.langchain.com/oss/python/langgraph/use-graph-api#map-reduce-and-the-send-api)
- [Send API](https://reference.langchain.com/python/langgraph/types/Send)
- [Multi-start edge/join semantics](https://reference.langchain.com/python/langgraph/graph/state/StateGraph/add_edge)
- [Persistence, threads, supersteps, pending writes, and StateSnapshot](https://docs.langchain.com/oss/python/langgraph/persistence)
- [CheckpointTuple pending writes](https://reference.langchain.com/python/langgraph.checkpoint/base/CheckpointTuple/pending_writes)
- [SQLite checkpoint package release](https://pypi.org/project/langgraph-checkpoint-sqlite/)
- [SqliteSaver 3.1.0 API and single-process suitability](https://reference.langchain.com/python/langgraph.checkpoint.sqlite/SqliteSaver)
- [Interrupt/resume and idempotent side-effect rules](https://docs.langchain.com/oss/python/langgraph/interrupts)

The public core reference was labeled 1.2.8 when checked while PyPI published 1.2.9. The implementation gate therefore proves these unchanged public APIs against 1.2.9 before any Plan 26 run. This is a validation requirement, not an open version choice.

## 4. Compiled graph ownership and one production path

The production builder is:

```python
runtime.langgraph_factory.graph.build_curriculum_factory_graph(
    *, engine_root: Path, output_root: Path
) -> CompiledStateGraph
```

`build_curriculum_factory_graph` creates the typed builder, registers every node/edge, opens the output-root `SqliteSaver`, and compiles exactly once. `runtime.run_curriculum.main()` is adapted into the sole production entry point. It parses/validates syntax, canonicalizes paths, acquires the output-root exclusive lock, constructs the graph, supplies `FactoryInput` and `RuntimeContext`, invokes it, verifies the structured `FactoryOutput` against the terminal ledger, prints one JSON result, and maps the terminal to an exit code.

`runtime.langgraph_factory.persistence.prepare_episode_invocation()` is the only pre-invocation helper. It deterministically computes or revalidates `run_id`, chooses the next episode-derived `thread_id`, and, for resume, reads prior `StateSnapshot`/`CheckpointTuple` data without invoking the prior thread. It cannot call product functions, transmit data, select a product frontier, or mutate accepted artifacts. Its output is a typed `EpisodeInvocation` consumed first by D00. D01 independently recomputes the fresh-run identity, and D00R independently revalidates a resume identity; disagreement is fatal.

The CLI MUST NOT call deterministic product functions in pipeline order, decide a next node, inspect a model result to route, write acceptance, or fall back. For a Plan 26 invocation it MUST reject legacy `--test-simulated*`, session-bridge, legacy FSM, and custom `CurriculumFactoryGraph` selection. Test modules may import fakes explicitly; production imports MUST have no fake-transport branch.

## 5. Typed LangGraph state

### 5.1 Schemas and reducer rules

`FactoryInput`, `FactoryState`, `FactoryOutput`, and `RuntimeContext` live in `runtime/langgraph_factory/state.py` as `TypedDict`/frozen dataclasses. Persisted state contains JSON-compatible values and content-addressed path references only; it never embeds PDF/page bytes or secrets. Runtime context holds opened services and is not checkpointed.

Reducer functions in `reducers.py` are pure, type-checking, and fail closed:

- `write_once`: absent to one value; equal replay is idempotent; differing replay fails.
- `append_unique`: append by declared correlation key; equal replay is idempotent; duplicate conflict fails.
- `union_disjoint`: associative/commutative map union for fan-out; conflict fails.
- `advance_head`: accepts only a child whose immutable parent equals the old head and version is old+1.
- `replace_current`: single-writer ephemeral routing/packet field; cleared explicitly after consumption.
- `monotonic_status`: only declared state transitions.
- `monotonic_max`: counters cannot decrease; increments are prepared by one deterministic counter node before dispatch.
- `accept_once`: immutable accepted receipt; equal replay only.
- `write_episode_terminal_once`: exactly one terminal per episode; differing second write fails.

### 5.2 Complete persisted state

| Field | Class/reducer | Mutation authority |
|---|---|---|
| `invocation` (fresh/resume/recover-orphan envelope and requested authorization), `validated_recovery_envelope` | replace-current per episode | graph input consumed by D00; D00R alone writes the validated envelope |
| `bootstrap_kind` | episode write-once | D00 |
| `contract_version` | write-once | D01 fresh; D04 may import the identical prior value into an empty episode thread |
| `run_id`, `created_at`, `engine_root`, `curriculum_root`, `active_manifest_path`, `output_root` | immutable/write-once | D01 fresh; D04 byte-identical import only |
| `mode`, `requested_unit_id` | immutable/write-once | D01 fresh; D04 byte-identical import only |
| `frozen_inputs` (path, SHA-256, role), `frozen_digest`, `frozen_executable_identities`, `external_authorizations` | immutable/write-once | D01 fresh; D00R compares and D04 imports identical values only |
| `effective_run` (ordered IDs, manifest records, target closure, manifest digest, denominator ID) | immutable/write-once | D02 fresh; D04 byte-identical import only |
| `episode_id`, `checkpoint_thread_id`, `checkpoint_ns`, `resume_from`, `resume_frontier` | episode-keyed append/replace-current frontier | D04; D30/D96 may set the resumable frontier |
| `cursor` (manifest ordinal, accepted ordinal), `selected_unit_id` | monotonic/replace-current | D05/D23 |
| `unit_status` by unit | monotonic status map | D05, validation/reduction/acceptance nodes |
| `source_requests`, `source_denominators` | append-unique/write-once per unit epoch | D06 |
| `source_discoveries`, `retrievals`, `source_interpretations` | union-disjoint by correlation key | M01, D06B, M01 |
| `source_admissions`, `source_join_evidence` | append-unique | D07 only |
| `artifact_versions` (domain, content, visual, layout/unit PDF) | append-unique immutable records | M02/M03/M04/M06 and deterministic producers; admitted only by D08/D09/D12/D20 |
| `artifact_heads` | version-headed/advance-head | admission nodes only |
| `deterministic_checks` | append-unique by `(scope, owner, head_hash, check_id, attempt)` | D08, D09, D12–D14, D20–D21, D26, D31–D32 |
| `visual_briefs`, `visual_denominators` | append-unique/write-once per content head | D10 |
| `visual_results`, `visual_join_evidence` | union-disjoint/append-unique | D11, M04, D12 |
| `unit_page_inventories`, `unit_page_inspections` | append-unique by PDF hash/page key | D14 |
| `review_packets`, `unit_reviews` | append-unique | D15, M05 |
| `finding_partitions`, `repair_requests` | append-unique | D17/D18 |
| `invalidations`, `retest_plans`, `retest_results` | append-unique | D19/D20/D21 |
| `attempt_counters`, `failure_fingerprints` | monotonic-max/append-unique | D90 counter gate and D17/D29 classifier |
| `accepted_unit_receipts` | accept-once | D22 |
| `accepted_unit_checkpoint_receipts` | append-unique | D23 |
| `workbook_versions`, `workbook_head` | append-unique/version-headed | D25/D31 |
| `workbook_coverage`, `workbook_page_inventories`, `workbook_page_inspections` | append-unique by workbook hash | D24/D26 |
| `workbook_review_packets`, `workbook_reviews` | append-unique | D27/M07 |
| `workbook_finding_partitions`, `workbook_repair_requests`, `workbook_invalidations`, `workbook_retests` | append-unique | D29/D31 |
| `final_release_audits` | append-unique by workbook head hash | D32 |
| `route_decisions`, `model_execution_receipts`, `activation_receipts`, `capability_receipts` | append-only/append-unique, episode-keyed | deterministic router, transport boundary, every node, D03 |
| `evidence_index_entries`, `log_audit_receipts` | append-only/append-unique | evidence writer and acceptance reducers |
| `checkpoint_metadata` (checkpoint ID, state digest, evidence high-water mark) | append-only | checkpoint-correlation hook after each superstep |
| `pending_failure`, `pending_packet`, `pending_guard` | replace-current | producing node; next deterministic classifier consumes/clears |
| `terminal_candidate` | replace-current, code-owned | deterministic guard/classifier only |
| `terminal` | write-once per episode | D98 |
| `terminal_history` | append-only | D04 moves only a validated prior resumable terminal; D98 appends current terminal mirror |

Derived, not persisted: resolved current artifact bodies, filesystem bytes, recomputed acceptance denominator, next scheduled node, and graph visualization. They are reconstructed from immutable versions/heads, `StateSnapshot.next/tasks`, and hashed filesystem artifacts. `execution_evidence` is represented by the append-only receipt/index fields rather than a mutable summary blob.

Runtime context contains only `engine_root`, `output_root`, the path-guard/evidence services, subprocess transport registry, source retriever, signal token, and clock. It contains no model client or routing authority. Nodes receive an explicit projection builder; passing the whole state to a model transport is forbidden.

## 6. LangGraph node catalogue

### 6.1 Catalogue notation and common rules

Every node is registered under the stable ID below. “Input” is its authorized state projection, not adjacency-derived context. “Update/reducer” names the only channels written. All product nodes use no automatic LangGraph retry. Replay is idempotent by correlation key and immutable content hash. A node catches classified expected failures into `pending_failure`; an unexpected exception is caught by the common node boundary and routed to `SYSTEM_FAILURE`. Each completed node is a checkpoint boundary at the following superstep; external side effects are staged then atomically admitted so replay cannot duplicate them. Every outgoing guard first checks `pending_failure` and a graceful interrupt token.

### 6.2 Deterministic nodes

| Stable ID | Authorized input | Output / reducer | Explicit retry and failure class | Outgoing guard |
|---|---|---|---|---|
| `D00_BOOTSTRAP_EPISODE` | typed `EpisodeInvocation`, presence/absence of prior immutable identity, prior terminal/lease summary | `bootstrap_kind` and sanitized invocation / episode write-once+replace-current | none; invalid fresh/resume/recovery combination = system | fresh -> D01; legal resume -> D00R; orphan recovery -> D96 only |
| `D00R_REVALIDATE_RESUME_IDENTITY` | immutable prior identity, supplied canonical roots/manifest/authorization, read-only prior snapshot/tuple digests | comparison receipt and validated recovery envelope / append-unique | none; any frozen digest/root/mode/target mismatch or illegal terminal = system | D03 |
| `D01_VALIDATE_AND_FREEZE_INPUTS` | raw `FactoryInput`, path guards | identity, canonical roots, frozen list/digest, authorization declaration / write-once | none; invocation/path/freeze/logger fault = system | D02 or D98 |
| `D02_COMPILE_EFFECTIVE_RUN` | frozen active manifest, mode, target | immutable effective run and denominator / write-once | none; schema/DAG/unknown target = system | D03 |
| `D03_PROVE_CAPABILITIES` | fresh effective-run/frozen fields or D00R's validated recovery envelope, plus current episode authorization | model CLI identity, retrieval, renderer, rasterizer, persistence and logger proof receipts / episode-keyed append-unique | one local probe per capability, no curriculum model job; executable identity mismatch, missing capability/authorization = system | D04 or D98 |
| `D04_INITIALIZE_OR_RESUME` | bootstrap kind, immutable identity/effective run, validated recovery envelope, current capability proofs, terminal ledger | episode metadata; on resume, reducer-validated import of the last full checkpoint plus admissible completed pending writes, recovered heads/counters/history / episode-keyed append | none; divergent pending write/evidence, changed identity, illegal resume, or accepted-byte mismatch = system | fresh -> D05; resume -> D92 |
| `D05_SELECT_NEXT_UNIT` | effective order, cursor, accepted receipts | selected unit/status / replace-current+monotonic | none; cursor inconsistency = system | D06 or D24 |
| `D06_COMPILE_SOURCE_REQUESTS` | one manifest unit, curriculum evidence contract, admitted reusable sources | bounded requests and complete denominator / append-unique | none; no bounded request for required fact = pause | M01 discovery fan-out |
| `D06B_RETRIEVE_SOURCE_CANDIDATES` | discovery locators, source request, retrieval allowlist | controller-fetched bytes/metadata/hash/TLS/status receipts / union-disjoint | frozen transport limit; unavailable named required fact = pause; network/tool/integrity fault = system | M01 interpretation fan-out |
| `D07_CORRELATE_AND_ADMIT_SOURCES` | exact denominator, discoveries, retrievals, interpretations, admission policy | admission manifest/join checks / append-unique | none; missing fact = D30; bad join/stale/cross-unit = system | M02 or D30 |
| `D08_VALIDATE_DOMAIN` | candidate domain version, admitted sources, schema/config/verifier/fixtures/calibration | admitted domain head and checks or findings / append+advance-head | none | M03, D17, or D98 |
| `D09_VALIDATE_CONTENT` | candidate content, current admitted domain, engine contracts/checks | admitted content head and complete content checks / append+advance-head | none | D10, D17, or D98 |
| `D10_COMPILE_VISUAL_BRIEFS` | content head, domain head, visual rules/library | exact briefs split into deterministic/model subsets and one complete denominator / append-unique | none; authoritative model visual request = system | deterministic subset nonempty -> D11 `Send` fan-out; empty -> D12 |
| `D11_CREATE_DETERMINISTIC_VISUALS` | one deterministic brief, permitted facts, library | immutable visual candidate / union-disjoint | one deterministic attempt; render fault = system | normal edge to D12 after the D11 map superstep |
| `D12_VISUAL_BARRIER_AND_JOIN` | exact denominator/subsets, accumulated D11/M04 results, parent hashes | first entry: exact deterministic-subset proof and M04 `Send` dispatch; final entry: admitted visual heads, provenance/hash/join checks / append+advance-head | none; missing/extra/duplicate/stale deterministic member = system; invalid visual = unit finding | incomplete exact model subset -> M04 fan-out; complete denominator -> D13 or D17 |
| `D13_RENDER_UNIT` | current domain/content/visual heads, renderer contract | versioned layout source and PDF candidates with hashes / append-unique | one deterministic activation per version; renderer/tool fault = system | D14 |
| `D14_INVENTORY_AND_INSPECT_UNIT_PAGES` | exact PDF hash, inspection contracts | positive contiguous inventory and per-page/asset inspection / append-unique | none; zero/noncontiguous/unreadable = layout finding | D15 or D17 |
| `D15_FREEZE_UNIT_REVIEW_PACKET` | frozen actual unit artifacts, shipped PDF, every page, deterministic evidence, rubric | immutable packet/denominator/hash / append-unique | none; packet mismatch = system | M05 |
| `D16_REDUCE_UNIT_EVIDENCE` | complete current unit evidence | code-computed denominator result / append check | none | D22 if all pass; otherwise D17 |
| `D17_CLASSIFY_UNIT_FINDINGS` | failed checks/review findings, owner taxonomy, history | total one-owner partition and fingerprints / append-unique | none; unowned/multi-owned = system; repeated bound = exhaustion | D18 or D98 |
| `D18_PLAN_TARGETED_UNIT_REPAIR` | one partition entry selected deterministically by topo/manifest order, heads, limits | one repair request with boundary/parent/descendants/retests / append-unique | none; attempt bound = exhaustion | D19 |
| `D19_ROUTE_UNIT_REPAIR` | repair request, deterministic-vs-model repair table | invalidation record and exact repair target / append-unique | none | deterministic repair producer, or D90 then M06 |
| `D20_ADMIT_UNIT_REPAIR` | immutable parent, candidate child/diff, boundary, invalidations | admitted child head and boundary proof / append+advance-head | none; out-of-bound/in-place = system | D21 |
| `D21_RETEST_REQUIRED_DESCENDANTS` | retest DAG, current heads, invalidations | ordered retest results / append-unique | none | first producing/validation node required, then D16 |
| `D22_ACCEPT_UNIT` | recomputed complete unit denominator | immutable accepted receipt and accepted byte set / accept-once | none; any absent/stale result remains not accepted | D23 |
| `D23_CHECKPOINT_ACCEPTED_UNIT` | accepted receipt, current checkpoint/evidence/log heads | checkpoint correlation receipt, cursor advance / append+monotonic | none; persistence/log mismatch = system | D05 |
| `D24_PROVE_EXACT_MANIFEST_COVERAGE` | effective manifest and accepted receipts | ordered exact coverage proof / append-unique | none; one-mode target accepted = unit terminal; full mismatch = system | D25 or D98 |
| `D25_ASSEMBLE_WORKBOOK` | exact accepted receipts and immutable unit PDFs, front-matter contract | workbook version/head and assembly map / append+advance-head | none; unit byte mutation = system | D26 |
| `D26_RENDER_INVENTORY_INSPECT_WORKBOOK` | workbook head, render/inspection contracts | actual PDF hash, contiguous page inventory, every-page inspection / append-unique | none; local layout defect = repair finding; tool fault = system | D27 or D29 |
| `D27_FREEZE_WORKBOOK_REVIEW_PACKET` | exact coverage, immutable unit hashes, workbook PDF, all pages, evidence/rubric | immutable workbook packet/denominator / append-unique | none; mismatch = system | M07 |
| `D28_REDUCE_WORKBOOK_EVIDENCE` | complete current workbook evidence | code-computed denominator result / append check | none | D32 if pass; otherwise D29 |
| `D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR` | failed workbook-only checks/findings, heads/history/limits | total partition, fingerprint, one request, invalidations/retests / append-unique | none; unit-owned finding = system; repeated/numeric bound = exhaustion | D90 then M08/deterministic repair |
| `D30_CLASSIFY_PREREQUISITE` | named unresolved source requirement and attempts | prerequisite record / append-unique | none; only required unavailable external fact pauses; all other causes system | D98 |
| `D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR` | immutable workbook parent, candidate/diff, boundary, accepted unit hashes | child workbook head, boundary proof, retests / append+advance-head | none; changed unit hash = system | D26 |
| `D32_RECOMPUTE_FINAL_RELEASE` | all current workbook/unit/evidence/checkpoint/log records | final release audit / append-unique | none; any denominator failure routes appropriate repair if still repairable, else system/exhaustion | D98 COMPLETE or D29 |
| `D90_RESERVE_MODEL_ATTEMPT` | job correlation key, limits, fingerprints | counter increment committed before dispatch / monotonic max | none; limit = exhaustion | the authorized model node |
| `D91_CLASSIFY_MODEL_FAILURE` | execution receipt/error class/counter | retry decision or terminal candidate / append+replace | only one malformed/transient retry when frozen limit permits; policy/content failures are repaired, not transport-retried | D90 or D98 |
| `D92_REENTER_VALIDATED_FRONTIER` | persisted deterministic `resume_frontier`, recovered pending writes/receipts, current capabilities/authorization/counters | frontier validation receipt and one deterministic destination / append+replace | none; a model node as stored destination, unaccounted active attempt, or stale parent = system | named deterministic re-entry node only; incomplete model activation -> D91, never directly to M01–M08 |
| `D96_GRACEFUL_INTERRUPT_GATE` | signal token/current safe boundary, or D00-validated orphan recovery envelope | interrupted episode candidate, deterministic resume frontier, and high-water marks / replace-current | none; cannot invoke transport/retrieval/render | D98 |
| `D98_WRITE_TERMINAL` | deterministic terminal candidate and supporting evidence | terminal record, history mirror, structured output / write-once+append | no retry; write/audit failure emits emergency system record by atomic evidence service | END |

Deterministic repair producers are functions selected inside D19/D29 for source refetch/interpretation invalidation, layout recompilation, or workbook-owned front matter/navigation/assembly changes. They are not model job types and receive no prompt.

### 6.3 Exactly eight model job types

| Stable ID / job type / CLI | Authorized input | Output / reducer | Retry/failure | Outgoing guard |
|---|---|---|---|---|
| `M01_RESEARCH_UNIT_SOURCES` / `research_unit_sources` / Codex | one request and phase-specific discovery authority, or controller-fetched results | locators or interpretations / union-disjoint | one schema/transport retry via D91; no admission authority | discovery -> D06B; interpretation -> D07 |
| `M02_CREATE_UNIT_DOMAIN_DATA` / `create_unit_domain_data` / Codex | one unit, admitted sources, domain schema/config/calibration | candidate domain version / append-unique | D91 only | D08 |
| `M03_WRITE_UNIT_CONTENT` / `write_unit_content` / Codex | current admitted domain and engine curriculum contracts | candidate complete unit content / append-unique | D91 only | D09 |
| `M04_CREATE_UNIT_VISUALS` / `create_unit_visuals` / Codex | one eligible non-authoritative brief and permitted facts | one visual candidate/provenance declaration / union-disjoint | D91 only | normal edge to D12 after the M04 map superstep |
| `M05_REVIEW_ACTUAL_UNIT` / `review_actual_unit` / Gemini | immutable unit review packet including PDF and every page | structured overall and per-page findings / append-unique | D91 only; family mismatch = system | D16 |
| `M06_REPAIR_NAMED_UNIT_ARTIFACT` / `repair_named_unit_artifact` / Codex | one named finding partition, owner, immutable parent, exact boundary/retest order | candidate child and changed-path manifest / append-unique | D91 only | D20 |
| `M07_REVIEW_ACTUAL_WORKBOOK` / `review_actual_workbook` / Gemini | immutable coverage/workbook packet including every page | structured overall and per-page findings / append-unique | D91 only; family mismatch = system | D28 |
| `M08_REPAIR_NAMED_WORKBOOK_DEFECT` / `repair_named_workbook_defect` / Codex | one workbook-owned defect, immutable parent and accepted-unit hashes | candidate workbook-owned child and changed-file manifest / append-unique | D91 only | D31 |

No deterministic node has a prompt path or calls a model transport. Model outputs are candidates/findings only; admission and all guards remain code-owned.

## 7. CLI model transport contract

### 7.1 Common transport envelope

`runtime/langgraph_factory/transport.py` adapts the current subprocess approach. At D03, executables are resolved with `shutil.which`, canonicalized, hashed where readable, and probed for version/model-list capability. The frozen route selects exact model ID, family, reasoning/effort, timeout, and retry limit. A transport MUST reject any request whose job type, family, model, or data classes differ from the frozen route.

The Plan 26 package's `config/model_jobs.v1.yaml` freezes the job-to-task/family mapping and delegates Codex model selection to the existing frozen registry/policy. With the inspected active policy, the decided routes are exact: M01 `component_research` -> `gpt-5.6-sol`/`xhigh`; M02 and M06 `final_acceptance` -> `gpt-5.6-sol`/`max`; M03 `child_explanatory_writing` -> `gpt-5.6-sol`/`high`; M04 `photorealistic_visual_prompt` -> `gpt-5.6-sol`/`high`; and M08 `workbook_assembly` -> `gpt-5.6-sol`/`high`. M05/M07 are frozen to family `google`, model `gemini-3-pro-preview`, and reasoning policy `cli_model_default` because the inspected Gemini command exposes no effort argument. D03 must prove that exact model/default under the exact CLI version; it may not falsely record Plan 25's asserted `max` effort. These values live in frozen configuration, not graph topology, and a future policy change creates a different run identity.

Each activation gets a disposable directory under `<output>/.workspaces/<episode>/<activation>/`, mode `0700`, with only:

- `authorized_input.json`, the exact projection and provider/data-authorization receipt;
- `output.schema.json`, copied from `runtime/langgraph_factory/schemas/`;
- one package-relative prompt copied from `Path(__file__).resolve().parent / "prompts" / <registered-name>`;
- explicit input artifacts copied or hard-linked read-only after path and hash validation; and
- no repository, output-root, sibling-unit, author-history, secrets, home configuration, or network credential files.

The process working directory is that directory. Environment variables are constructed from an allowlist and a dedicated temporary home/config directory; proxy/model credentials required by the installed CLI may be passed by name but are never written to state/logs. The request instruction identifies only the staged filenames. stdout, stderr, return code, start/end UTC, duration, PID, executable path/hash/version, command with secrets redacted, decided route, observed executed model/family, input/schema/prompt/output hashes, and timeout/termination are captured in an immutable execution receipt. Full bounded streams are stored below durable evidence; console output is not trusted.

Timeouts are process-group wall-clock limits from frozen policy. Timeout sends TERM, waits five seconds, then KILL, records partial output, and returns a classified transport failure. Nonzero return, signal exit, missing result, malformed JSON, schema failure, extra files, or path escape never reaches an artifact channel. One frozen malformed/transient retry is reserved by D90 and produces a distinct activation/receipt. Content disagreement is not a transport retry.

JSON is read from the designated result file first. If the CLI only emits an outer JSON envelope, a registered deterministic extractor parses exactly one JSON document; prose fences, multiple candidates, trailing material, NaN, duplicate keys, or undeclared properties fail. `jsonschema` validates the job schema before the graph sees a candidate.

### 7.2 Codex transport

Codex authoring, research, visual, and repair nodes invoke the current noninteractive pattern, pinned by an argument-construction test:

```text
codex exec --ephemeral --ignore-user-config --ignore-rules
  -s read-only --skip-git-repo-check -C <workspace>
  -m <frozen-model> -c model_reasoning_effort="<frozen-effort>"
  --output-schema output.schema.json -o result.json <instruction>
```

The selected model and reasoning policy come only from the frozen code-owned route. The receipt distinguishes `decided_model` from `executed_model`: implementation MUST extract the executed identity from a machine-readable Codex event/receipt produced by the installed CLI and compare it to the decision. Merely copying the decision is invalid. If the pinned CLI cannot emit observable identity, D03 fails before transmission; no run may claim route conformance.

Read-only Codex sandboxing does not substitute for filesystem isolation. The worker receives only the staged workspace. Source discovery may return locators, but the worker cannot retrieve/admit bytes; D06B performs deterministic retrieval. M01 interpretation receives only the retrieved records copied into its workspace.

### 7.3 Gemini transport

Independent review nodes invoke:

```text
gemini -m <frozen-review-model> -s --approval-mode default
  --output-format json <instruction>
```

Gemini runs in the same isolated staging model. Review route validation requires `executed_family != authoring_family` and the active v1 contract requires one Gemini judge activation per unit/workbook review epoch, with a finding result for every page. The executed model/family MUST be observed from the Gemini machine-readable initialization/result envelope and compared with the frozen decision. If it cannot be observed, D03 fails. `M07` is review only; `M08` remains a Codex repair job.

### 7.4 External-data authorization and containment

Before any subprocess or network transmission, D01 hashes a required authorization record and D03 proves it covers the exact run:

- `openai`: permits transmission of the selected manifest-unit projection, bounded questions, admitted/retrieved source excerpts or files, domain/content/visual parent artifacts, named repair findings, and schemas/rubrics needed by M01–M04/M06/M08;
- `google`: permits transmission of frozen actual unit/workbook artifacts, deterministic evidence, shipped PDFs, and every rasterized page required by M05/M07; and
- `primary_source_hosts`: permits deterministic retrieval from admitted candidate primary-source locators under URL/size/type/redirect limits.

The record lists permitted providers, data classes, curriculum digest, output/run scope, and approval timestamp. It is not a blanket consent and credentials are not approval. A projection builder computes a data manifest and refuses undeclared classes before creating the child process. Absent or mismatched authorization causes `SYSTEM_FAILURE` before transmission for a live invocation; read-only preflight returns `AUTHORIZATION_REQUIRED` without a product terminal. There is no redaction-based silent downgrade, same-family review, or offline simulation fallback.

## 8. Execution edges and deterministic guards

### 8.1 Normal graph

The builder registers this root graph; bracketed dispatches are `Send` lists and every named decision is a pure guard in `routing.py`:

```text
START
 -> D00_BOOTSTRAP_EPISODE

 fresh:
 -> D01_VALIDATE_AND_FREEZE_INPUTS
 -> D02_COMPILE_EFFECTIVE_RUN
 -> D03_PROVE_CAPABILITIES
 -> D04_INITIALIZE_OR_RESUME
 -> D05_SELECT_NEXT_UNIT

 legal resume:
 -> D00R_REVALIDATE_RESUME_IDENTITY
 -> D03_PROVE_CAPABILITIES
 -> D04_INITIALIZE_OR_RESUME
 -> D92_REENTER_VALIDATED_FRONTIER
 -> one deterministic first-incomplete node

 orphaned/crashed episode recovery:
 -> D96_GRACEFUL_INTERRUPT_GATE
 -> D98_WRITE_TERMINAL(INTERRUPTED)
 -> END

 normal unit path:
 -> D06_COMPILE_SOURCE_REQUESTS
 -> [M01_RESEARCH_UNIT_SOURCES phase=DISCOVER per request]
 -> D06B_RETRIEVE_SOURCE_CANDIDATES
 -> [M01_RESEARCH_UNIT_SOURCES phase=INTERPRET per request/retrieval group]
 -> D07_CORRELATE_AND_ADMIT_SOURCES
 -> M02_CREATE_UNIT_DOMAIN_DATA -> D08_VALIDATE_DOMAIN
 -> M03_WRITE_UNIT_CONTENT -> D09_VALIDATE_CONTENT
 -> D10_COMPILE_VISUAL_BRIEFS
 -> [D11_CREATE_DETERMINISTIC_VISUALS per deterministic brief]
 -> D12_VISUAL_BARRIER_AND_JOIN
 -> [M04_CREATE_UNIT_VISUALS per eligible model brief]
 -> D12_VISUAL_BARRIER_AND_JOIN
 -> D13_RENDER_UNIT
 -> D14_INVENTORY_AND_INSPECT_UNIT_PAGES
 -> D15_FREEZE_UNIT_REVIEW_PACKET
 -> M05_REVIEW_ACTUAL_UNIT
 -> D16_REDUCE_UNIT_EVIDENCE
    PASS -> D22_ACCEPT_UNIT -> D23_CHECKPOINT_ACCEPTED_UNIT -> D05
    FAIL -> D17_CLASSIFY_UNIT_FINDINGS -> D18_PLAN_TARGETED_UNIT_REPAIR
         -> D19_ROUTE_UNIT_REPAIR
         -> D90_RESERVE_MODEL_ATTEMPT when model-owned
         -> M06_REPAIR_NAMED_UNIT_ARTIFACT or deterministic repair producer
         -> D20_ADMIT_UNIT_REPAIR
         -> D21_RETEST_REQUIRED_DESCENDANTS
         -> earliest invalidated producer/check in topological order -> D16

D05 when no next required unit
 -> D24_PROVE_EXACT_MANIFEST_COVERAGE
    one mode -> D98_WRITE_TERMINAL(UNIT_ACCEPTED) -> END
    all mode -> D25_ASSEMBLE_WORKBOOK
 -> D26_RENDER_INVENTORY_INSPECT_WORKBOOK
 -> D27_FREEZE_WORKBOOK_REVIEW_PACKET
 -> M07_REVIEW_ACTUAL_WORKBOOK
 -> D28_REDUCE_WORKBOOK_EVIDENCE
    PASS -> D32_RECOMPUTE_FINAL_RELEASE -> D98_WRITE_TERMINAL(COMPLETE) -> END
    FAIL -> D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR
         -> D90_RESERVE_MODEL_ATTEMPT when model-owned
         -> M08_REPAIR_NAMED_WORKBOOK_DEFECT or deterministic workbook repair
         -> D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR
         -> D26
```

`START` has exactly one edge to D00. D98 has exactly one edge to `END`. D00's orphan-recovery branch has only D96/D98/END destinations. There is no edge from a model directly to acceptance, terminal, checkpoint initialization, unit selection, workbook assembly, or release.

### 8.2 Complete conditional-edge rules

The following guards are exhaustive; an unknown return value is a system failure:

| From | Deterministic condition | To |
|---|---|---|
| every node | graceful signal is set after the node reaches an atomic boundary | D96 then D98 `INTERRUPTED` |
| every node | `pending_failure.class` is unhandled/unexpected, integrity, identity, schema-contract, tool, or persistence | D98 `SYSTEM_FAILURE` |
| D00 | no prior identity and invocation is fresh | D01 |
| D00 | prior identity exists, last terminal is legally resumable, and invocation is resume | D00R |
| D00 | prior episode lease is open without terminal | D96 recovery-only; no product node |
| D00R | every supplied/frozen identity digest and prior checkpoint/evidence binding matches | D03 |
| D03/D06/D07/D30 | exactly one named required external fact is unavailable after allowed retrieval, with locator/question evidence | D98 `PAUSED_PREREQUISITE` |
| D03 | every required capability and authorization receipt passes | D04 |
| D04 | fresh episode initialization passes | D05 |
| D04 | resume import/reduction passes | D92 |
| D92 | stored frontier is a deterministic node with current parents | that deterministic node |
| D92 | prior model activation was incomplete/aborted | D91; any later model retry must pass D90 |
| D05 | required unaccepted unit exists at cursor | D06 |
| D05 | no required unit remains | D24 |
| D06 | complete positive request denominator exists | `Send(M01, discovery packet)` for every key |
| M01 discovery superstep | result set exists | D06B |
| D06B | complete retrieval denominator prepared | `Send(M01, interpretation packet)` for every key |
| M01 interpretation superstep | result set exists | D07 |
| D07 | exact join and admission pass | M02 |
| D08/D09/D12/D14 | current candidate fails repairable product check | D17 |
| D08/D09/D12/D14 | current candidate passes stage | next normal node |
| D10 | deterministic subset is nonempty | one `Send(D11, brief_packet)` per deterministic key |
| D10 | deterministic subset is empty | D12 directly |
| D11 map superstep | all scheduled D11 tasks returned through `union_disjoint` | normal `D11 -> D12` edge, matching the official Send map/reduce pattern |
| D12 first entry | deterministic actual keys equal the frozen deterministic subset and model subset is nonempty | one `Send(M04, brief_packet)` per model key |
| D12 first/final entry | model subset is empty, or accumulated actual keys equal the complete denominator | verify/admit, then D13 or D17 |
| M04 map superstep | all scheduled M04 tasks returned through `union_disjoint` | normal `M04 -> D12` edge |
| D16 | all current unit denominator entries pass | D22 |
| D16 | one or more repairable findings | D17 |
| D17/D29 | any fingerprint reaches repeat bound or numeric attempts are exhausted | D98 `CONVERGENCE_EXHAUSTED` |
| D17/D29 | exact total owner partition exists and bound remains | D18 or repair dispatch |
| D18/D29 | repair requires a model | D90 then M06/M08 |
| D18/D29 | repair is deterministic | D19/deterministic producer |
| D21 | another invalidated descendant remains | earliest node in fixed retest DAG |
| D21 | retest frontier complete | D16 |
| D24 | mode `one`, target receipt present/current, closure accepted | D98 `UNIT_ACCEPTED` |
| D24 | mode `all`, exact ordered full-manifest receipt set passes | D25 |
| D28 | workbook denominator fails repairably | D29 |
| D28 | workbook denominator passes | D32 |
| D32 | release recomputation passes without stale member | D98 `COMPLETE` |
| D32 | repairable workbook-owned current defect remains and bound remains | D29 |

Dynamic manifest expansion is state-driven: D02 freezes an ordered list of arbitrary length and the D05/D23 loop consumes it. The builder never creates a node per known unit. `Send(node_id, packet)` packets contain only one worker projection plus correlation metadata. Visuals use the documented map/reduce shape twice: D10 `Send`s to D11 and `add_edge("D11_CREATE_DETERMINISTIC_VISUALS", "D12_VISUAL_BARRIER_AND_JOIN")`; after exact deterministic-subset reduction, D12 `Send`s to M04 and `add_edge("M04_CREATE_UNIT_VISUALS", "D12_VISUAL_BARRIER_AND_JOIN")`. Empty subsets route directly through D12, so no sentinel or mixed static/dynamic multi-start join exists. D12 admits only when the complete precommitted denominator matches.

## 9. Context graph and structural isolation

Execution adjacency grants no context. Each projection schema has `additionalProperties: false`, is materialized by code, hashed, and staged alone.

| Model job | Included context | Structurally excluded |
|---|---|---|
| M01 discovery | one bounded question, unit ID/title/objectives strictly needed for it, primary-source/admission rules, discovery authority | sibling requests/units, author history, acceptance, output tree |
| M01 interpretation | same request plus only its controller-retrieved bytes/metadata/hashes | network/repository access, other retrieval groups, routing/acceptance state |
| M02 domain | one manifest unit, admitted source scopes/excerpts, domain schema/config/verifier interface, fixtures/calibration needed for the unit | content drafts, reviews, sibling units, terminals |
| M03 content | accepted current domain, engine curriculum/schema/grounding/pedagogy/readability/safety contracts, admitted evidence references | rejected domain versions, reviewer history, sibling artifacts, acceptance state |
| M04 visual | one exact eligible brief, permitted facts, dimensions/format/accessibility contract | authoritative circuit/pin/electrical invention, other briefs, full state |
| M05 unit review | frozen current domain/content/visuals, shipped unit PDF, every page image, page inventory, deterministic evidence and rubric | author/repair history, prompts/outputs from M01–M04/M06, counters, desired verdict |
| M06 unit repair | named findings for exactly one owner, immutable parent bytes/hash, exact JSON pointers/files/region, allowed facts, invalidated descendants and retest order | unrelated findings/artifacts, accepted bytes, sibling units, routing/terminal state |
| M07 workbook review | exact ordered coverage map, immutable accepted-unit hashes, actual workbook PDF, every workbook page, inventory/evidence/rubric | author and unit repair history, desired verdict, mutable unit sources |
| M08 workbook repair | one workbook-owned defect, immutable workbook parent, allowed front-matter/navigation/layout/assembly files, immutable accepted-unit/PDF hashes | unit content/domain/visual sources, unrelated workbook defects, acceptance/terminal authority |

The worker process has a fresh workspace and allowlisted environment, no mount/link to the engine or output root, and read-only sandboxing. Only path-validated, hash-checked staged copies are visible. The dedicated temporary home contains no user configuration or repository discovery metadata. On supported platforms the implementation MUST add an OS process sandbox that denies filesystem access outside the workspace; D03 fails if this isolation cannot be proven. Process egress is restricted to the selected CLI provider endpoints needed to execute Codex or Gemini. Interpretation, authoring, review, and repair receive no browsing/discovery authority; M01 discovery alone may use the Codex CLI's explicitly proven hosted discovery capability. Direct source bytes are always retrieved by D06B under the separate primary-source-host authorization. Workspace inventories before/after execution reject undeclared reads/writes to the extent observable, and every durable output is copied through a validating admission boundary before the workspace is deleted.

## 10. Fan-outs, joins, and correlation keys

Every denominator is immutable and persisted before dispatch. A join accepts a map only when `actual_keys == expected_keys`, all values validate, and every member binds the current parent hashes/epoch.

| Join | Correlation key | Denominator contents |
|---|---|---|
| source discovery | `(run_id, unit_id, source_epoch, request_id, "discover")` | every compiled source request |
| source retrieval | `(run_id, unit_id, source_epoch, request_id, retrieval_id)` | every admitted candidate locator selected by code |
| source interpretation | `(run_id, unit_id, source_epoch, request_id, retrieval_group_hash, "interpret")` | every required request/retrieval group |
| visual result | `(run_id, unit_id, content_head_hash, visual_epoch, brief_id)` | every deterministic or eligible model brief, with producer class |
| unit page review | `(run_id, unit_id, pdf_sha256, review_epoch, review_id, page_number, page_sha256, rubric_sha256)` | all integers `1..page_count`; page count must be positive |
| workbook page review | `(run_id, workbook_sha256, review_epoch, review_id, page_number, page_sha256, rubric_sha256)` | all integers `1..page_count`; page count must be positive |

Missing, failed, invalid, or `NOT_RUN` members leave the join failed and route to a repair/failure classifier. Duplicate equal replay is idempotent only when it has the same activation and output hash; any different duplicate is integrity failure. Extra, stale-parent, stale-rubric, wrong-epoch, cross-unit, wrong-page-hash, or unknown keys cause `SYSTEM_FAILURE`, not best-effort reduction. A failed worker remains an explicit failed result until D91 authorizes a new attempt under a new activation key; it cannot be omitted from the denominator.

Unit/workbook review is one cross-family judge activation per review epoch under the active v1 contract, but its structured result must contain exactly one result for every denominator page plus overall findings. A future frozen policy may increase judge count only by changing the input contract and denominator; it may not weaken exact all-page coverage.

## 11. Checkpointing, interruption, and resume

### 11.1 Selected saver and identity

The saver is `SqliteSaver` 3.1.0 at:

```text
<output_root>/.langgraph/checkpoints.sqlite3
```

It uses SQLite WAL mode, `PRAGMA synchronous=FULL`, foreign keys, a busy timeout, `LANGGRAPH_STRICT_MSGPACK=true`, and one process guarded by `<output_root>/.langgraph/execution.lock`. Persisted state is restricted to the JSON-compatible Plan 26 schema; arbitrary checkpoint classes are forbidden. This local single-process constraint matches the official description of `SqliteSaver` as lightweight synchronous persistence. Multiple concurrent processes or distributed workers are out of scope and fail preflight.

`checkpoint_ns` is always the official root namespace `""`; Plan 26 uses no subgraphs and does not assign an episode namespace. Each execution episode has a new thread whose ID is deterministically related to immutable `run_id`:

```text
<run_id>:episode:<six-digit-ordinal>
```

An orphan-recovery invocation uses `<run_id>:recover:<orphan-episode-ordinal>` and is logically the closing continuation of that orphan, not a product-work episode. New threads start with empty LangGraph state, so a resumed episode cannot accidentally re-execute D01 against restored write-once channels. `prepare_episode_invocation()` computes the same canonical fresh `run_id` required by D01 only to configure the first thread. On resume it reads `run_id` from the immutable identity envelope and verifies it before choosing the next thread; D00R and D04 repeat the validation inside the graph.

The invoke config is exactly:

```python
{
  "configurable": {
    "thread_id": f"{run_id}:episode:{episode_ordinal:06d}",
    "checkpoint_ns": "",
  }
}
```

The graph is invoked synchronously and the SQLite transaction is committed at every checkpointer write. LangGraph creates state snapshots at superstep boundaries and pending writes for completed sibling fan-out tasks. The implementation records the resulting `checkpoint_id`, `StateSnapshot.next/tasks`, state digest, and evidence high-water mark in the append-only checkpoint-correlation ledger after each superstep. SQLite file and WAL are flushed before an accepted-unit checkpoint receipt or terminal can pass. A resume reads the previous episode with `get_state`/`get_state_history` and `SqliteSaver.get_tuple`; it never invokes the previous thread with `None`.

### 11.2 Two persistence layers

LangGraph checkpoints provide recoverable state/frontier and pending-write fault tolerance. They do not replace:

- ACT/EXEC append-only activation pairs;
- route decision and observed execution receipts;
- retrieved-source bytes/hashes/admission manifests;
- immutable artifact versions and current-head records;
- checks, page inventories/inspections, review packets/results;
- repair/invalidations/retests;
- accepted-unit/workbook/final-release receipts; or
- the append-only episode/terminal ledger.

Every record includes `run_id`, `episode_id`, node/activation ID, checkpoint namespace and preceding/latest checkpoint ID where available, state digest, evidence ordinal, and record hash. D22, D23, D32, and D98 audit both layers and their correlation.

### 11.3 Graceful interruption and crash recovery

SIGINT/SIGTERM set a process-safe token. No new external transmission starts after it is set. An active subprocess is terminated through the timeout protocol and records an aborted execution receipt. The active node returns at an atomic boundary; D96 records a deterministic `resume_frontier`, current heads, pending denominator members, latest committed checkpoint/evidence ordinals, and terminal candidate `INTERRUPTED`; D98 writes exactly one episode terminal then `END`. A model node is never stored as a resume destination: an interrupted model activation maps to D91, which must classify the aborted receipt before D90 can authorize any later transmission.

A power loss/SIGKILL cannot execute D98. On the next `--resume`, `prepare_episode_invocation()` uses only read methods to obtain the orphan thread's latest full snapshot, `StateSnapshot.next/tasks`, and `CheckpointTuple.pending_writes`. It MUST NOT call `invoke(None)` on that thread. It invokes a new recovery thread with `bootstrap_kind=RECOVER_ORPHAN`; the compiled graph has an exclusive `D00 -> D96 -> D98 -> END` path for that kind. Recovery runtime context contains no model transport, retriever, or renderer, and those services raise if accessed. D96 validates completed pending writes against append-only activation/output receipts, converts any pending model task to deterministic D91, records the resumable frontier, and D98 closes the orphan as `INTERRUPTED/recovered_after_unclean_exit`. Only after that graph reaches `END` may the same CLI command prepare and invoke the next episode thread through D00R/D03/D04. Thus crash recovery cannot execute a saved product or model frontier before current identity, capability, and external-data authorization checks.

### 11.4 Resume algorithm

Resume is legal only after `INTERRUPTED` or `PAUSED_PREREQUISITE`:

1. acquire the exclusive output lock and read the immutable identity envelope;
2. use read-only checkpoint APIs to locate the last episode thread, its latest full snapshot, task frontier, and pending writes; never invoke that thread;
3. if its lease is orphaned, run only the new recovery thread's D00/D96/D98 path described above;
4. re-resolve the supplied engine/curriculum/manifest and recompute every frozen digest and executable hash; differing frozen input refuses resume before product work;
5. validate terminal legality, SQLite integrity, prior history, pending writes, append-log hash chain, artifact heads, accepted receipt hashes, and accepted bytes in D00R;
6. start a new episode thread with empty LangGraph state; D04 reducer-imports the last full state byte-identically except episode/current-terminal fields, merges only completed pending writes that have matching immutable execution evidence, moves the prior resumable terminal to history, and preserves counters/fingerprints;
7. reconstruct a deterministic first-incomplete frontier from prior `StateSnapshot.next/tasks`, denominators, current heads, invalidations, and cursor. D92 rejects a model destination and routes an incomplete model attempt through D91/D90;
8. completed fan-out members with valid pending writes/receipts are not dispatched again; incomplete members remain in the denominator and are dispatched only after the appropriate deterministic guard; and
9. never overwrite, rerender, or reassemble an accepted unit. Accepted hashes are rechecked before continuation.

The output lock plus an append-only episode lease with compare-and-swap ordinal prevents duplicate continuation. A second process exits before graph invocation. `UNIT_ACCEPTED`, `COMPLETE`, `CONVERGENCE_EXHAUSTED`, and `SYSTEM_FAILURE` are not resumable; a new fresh output root/run is required. A paused prerequisite may resume only with the same frozen inputs and a newly available external source/capability explicitly described by the prior prerequisite record.

LangGraph's dynamic `interrupt()`/`Command(resume=...)` API is intentionally not used in v1 because the product contract requires every execution episode—including interruption—to write one terminal and reach `END`. Episode-derived threads, read-only checkpoint extraction, a persisted deterministic `resume_frontier`, and D04 reducer import preserve LangGraph checkpoint evidence without executing an unsafe old frontier.

## 12. Targeted repair architecture

Every repairable finding is normalized to `{finding_id, evidence_key, owner, boundary, parent_hash, fingerprint}`. D17/D29 proves a total partition: each blocking finding appears once, has exactly one owner, and no owner receives an unrelated finding. Repairs execute one partition member at a time in fixed owner/topological order.

Every `RepairRequest` contains:

- exactly one owner and named finding set;
- exact allowed JSON pointers, file paths, SVG element IDs, page/layout region, or workbook-owned component;
- immutable parent version/hash and next child version number;
- allowed evidence/facts and prohibited boundaries;
- descendants to invalidate and a fixed topological retest list;
- attempt number reserved before activation;
- normalized failure fingerprint and its prior count; and
- maximums from frozen limits: three repair children per owner/finding chain, two occurrences of the same fingerprint, and the repository global model-call/storage limits. The earliest reached bound controls.

The child is staged separately. D20/D31 compares full parent/child trees and structured diffs, rejects changed bytes outside the boundary, then admits atomically and advances the head. Parents remain immutable.

| Owner | Repair behavior | Invalidated descendants and retest order |
|---|---|---|
| source interpretation | refetch deterministically only if locator remains authorized; M06 repairs only the named interpretation against one request/retrieval group; admission is code-owned | source admission -> domain verifier/schema -> content grounding/derivation -> affected visuals -> render/pages -> review -> unit reduction |
| curriculum domain | M06 changes only named domain pointers against admitted facts | domain schema/verifier/fixtures -> content facts/derivation -> affected visuals -> render/pages -> review -> reduction |
| unit content | M06 changes only named content pointers/sections | unit schema -> grounding/derivation/pedagogy/readability/safety -> affected visuals -> render/pages -> review -> reduction |
| unit visual | deterministic producer reruns an authoritative/library visual; M06 changes only an eligible non-authoritative asset/brief | provenance/hash/asset checks -> render/pages -> review -> reduction |
| unit layout | deterministic renderer/template repair is preferred; M06 only if the named layout source is model-owned | render -> every-page inventory/inspection -> review -> reduction |
| workbook front matter/navigation/layout/assembly | deterministic assembly/template repair first; M08 only for the exact workbook-owned component | coverage and immutable unit hashes -> assemble/render -> every-page inventory/inspection -> review -> final release |

A local defect never regenerates a whole unit. Regeneration of a descendant occurs only when its declared parent hash changed and the invalidation DAG names it. Workbook repair cannot stage writable unit sources or PDFs; D31 compares all accepted-unit hashes before and after and routes any change to `SYSTEM_FAILURE`. Bound exhaustion is honest `CONVERGENCE_EXHAUSTED`, never acceptance with warnings.

## 13. Deterministic product QA and acceptance

### 13.1 Unit denominator

D16 builds the complete denominator from frozen contracts and the current heads; D22 recomputes it immediately before acceptance. All entries must be `PASS`, current, unique, schema-valid, and hash-bound. Required evidence is:

1. every source request/retrieval/interpretation join member and admitted primary-source manifest;
2. source identity, type, scope, retrieval status, bytes, SHA-256, correlation, and grounding resolution;
3. curriculum-domain schema and curriculum executable verifier/fixtures/calibration;
4. complete unit schema;
5. exact fact-to-parent JSON-pointer derivation and domain equality where required;
6. every sourced claim resolved to admitted evidence;
7. pedagogy, Bloom progression, readability, completeness, and required safety checks selected by active contracts;
8. every required actual visual, deterministic/model eligibility, provenance, source/brief/parent hashes, format and asset-resolution checks;
9. actual rendered unit PDF hash and renderer receipt;
10. a positive contiguous `1..N` page inventory and inspection result for every page, including nonblank/legibility/clipping and asset checks;
11. one independent Gemini review of the frozen actual unit/PDF and exactly every page under the active v1 contract, with observed cross-family identity;
12. complete repair partition, immutable parent/child history, invalidations, and required current retests;
13. append-only ACT/EXEC, route/execution receipt, artifact, and evidence-index integrity through the acceptance high-water mark; and
14. current LangGraph checkpoint/state digest correlation plus an immutable accepted receipt/checkpoint receipt.

The accepted receipt enumerates every denominator key and evidence hash, artifact-head hash, page/review denominator, log high-water mark, and checkpoint ID. Missing, stale, duplicate, invalid, failed, unresolved, or `NOT_RUN` evidence blocks acceptance. Warnings may exist only for nonblocking criteria explicitly frozen as nonblocking; they cannot stand in for a required entry.

### 13.2 Workbook denominator

D28/D32 require all unit criteria through immutable accepted receipts and additionally:

1. exact ordered equality between active-manifest unit IDs and accepted receipt IDs—no missing, extra, duplicate, reordered, or cross-run unit;
2. byte-for-byte current equality of every accepted unit artifact/PDF to its receipt hash;
3. actual assembled workbook and assembly map without unit mutation;
4. positive contiguous workbook page inventory and inspection of every page;
5. one observed cross-family Gemini workbook review with a result for exactly every workbook page and overall navigation/coverage findings;
6. workbook-only repair parent/child/boundary/invalidation/retest integrity;
7. append-log, evidence index, checkpoint, and terminal-precondition integrity; and
8. final release recomputation against current bytes after all repair/review work.

Only D32 can authorize `COMPLETE`, and it does so from recomputed current evidence, not a cached review verdict.

## 14. Terminal design

No model schema contains an authoritative terminal field. Guards create `terminal_candidate`; only D98 validates the guard and writes the terminal ledger before `END`.

| Terminal | Exact deterministic guard | Persisted evidence | Resume | CLI exit |
|---|---|---|---|---:|
| `UNIT_ACCEPTED` | mode is one; target and entire effective closure have current accepted receipts; target receipt/checkpoint integrity passes | target/closure receipt hashes, denominator, log/checkpoint heads | no | 0 |
| `COMPLETE` | mode is all; D32 final release audit passes exact full manifest/current workbook | final audit, coverage, unit/workbook hashes, all-page evidence, log/checkpoint heads | no | 0 |
| `INTERRUPTED` | graceful signal at atomic boundary, or retrospectively proven open crashed episode | frontier, heads, pending members, checkpoint/evidence high-water marks, signal/crash classification | yes | 10 |
| `PAUSED_PREREQUISITE` | one named required external fact remains unavailable after authorized bounded attempts; no tool/integrity fault | question/fact, attempts, locators/status, required resume condition | yes | 11 |
| `CONVERGENCE_EXHAUSTED` | numeric attempt or repeated-fingerprint bound reached before full acceptance denominator | counters, fingerprints, last findings/heads/retests | no | 12 |
| `SYSTEM_FAILURE` | invalid input after episode start, capability/authorization/tool/schema/integrity/identity/join/persistence/log fault not classed above | typed failure, node/activation, receipts, safe heads and audit high-water mark | no | 20 |

Each terminal maps `D98 -> END` and each episode has exactly one terminal record. CLI argument errors before an episode exit 2 and preflight-not-ready exits 3; neither is a product terminal. Preflight-ready exits 0 with `kind: PREFLIGHT`, never `UNIT_ACCEPTED`/`COMPLETE`.

## 15. Filesystem and artifact layout

Proposed implementation layout (none is created in this pass):

```text
runtime/langgraph_factory/
  __init__.py
  graph.py                 # builder/compile only
  state.py reducers.py routing.py
  context.py persistence.py evidence.py transport.py
  config/model_jobs.v1.yaml # eight frozen job/task/family routes
  nodes/
    inputs.py sources.py domain.py content.py visuals.py
    render.py review.py repair.py workbook.py terminal.py
  schemas/                 # eight model output schemas and internal receipts
  prompts/                 # eight package-relative prompt files

requirements/plan26.in
requirements/plan26.lock

<output_root>/
  identity/run.json
  immutable_inputs/manifest.json curriculum_contracts.json frozen_files.json
  .langgraph/checkpoints.sqlite3 execution.lock episode_ledger.jsonl
  .workspaces/<episode>/<activation>/             # disposable; never product evidence
  evidence/events.jsonl activations.jsonl routes.jsonl executions.jsonl
  evidence/checkpoints.jsonl index.jsonl log_audits/
  sources/<unit>/<source_epoch>/requests/ retrievals/ interpretations/ admissions/
  units/<unit>/
    versions/domain/ content/ visuals/ layout/
    heads/domain.json content.json visuals.json layout.json
    checks/ pages/ reviews/ repairs/ retests/
    accepted/<receipt_hash>/receipt.json unit.pdf artifacts/
  workbook/
    versions/ heads/workbook.json coverage/ pages/ reviews/ repairs/ release/
    accepted/<release_hash>/workbook.pdf receipt.json
  terminals/<episode_id>.json
  terminal_history.jsonl
```

The supplied engine/curriculum and `immutable_inputs` are immutable source inputs. `versions/` are append-only intermediate artifacts; `heads/` are small atomically replaced pointers validated by `advance_head`; `accepted/` is immutable and write-protected after receipt. `.workspaces` is disposable and excluded from evidence except its captured inventory/receipts. `evidence/`, checkpoint database, terminal files, source bytes, reviews, and receipts are durable. All paths are resolved below canonical roots, symlink escapes are rejected, and accepted files are never hard-linked to writable version files.

## 16. CLI contract

The sole module is `python3 -m runtime.run_curriculum`. Exact commands are:

```bash
# Read-only preflight; creates no run and cannot succeed as a product
python3 -m runtime.run_curriculum \
  --preflight \
  --engine-root . \
  --curriculum curricula/arduino_kit/arduino_kit_curriculum.v5.yaml \
  --output-root outputs/plan26-preflight

# One requested unit plus its transitive prerequisite closure
python3 -m runtime.run_curriculum \
  --engine-root . \
  --curriculum curricula/arduino_kit/arduino_kit_curriculum.v5.yaml \
  --output-root outputs/plan26-L12 \
  --unit L12 \
  --authorization external-data.authorization.json

# Full exact manifest
python3 -m runtime.run_curriculum \
  --engine-root . \
  --curriculum curricula/arduino_kit/arduino_kit_curriculum.v5.yaml \
  --output-root outputs/plan26-full \
  --all \
  --authorization external-data.authorization.json

# Resume a legally resumable episode
python3 -m runtime.run_curriculum \
  --engine-root . \
  --curriculum curricula/arduino_kit/arduino_kit_curriculum.v5.yaml \
  --output-root outputs/plan26-full \
  --resume \
  --authorization external-data.authorization.json
```

The Arduino manifest is an acceptance example only. Graph modules may contain none of `arduino`, `L12`, `L01`, `35`, or an assumed sequence. The resolver also accepts a curriculum directory and selects its exact active manifest by the existing repository contract; the identity stores the resolved manifest path/hash.

A fresh live output root must not exist or must be an existing empty directory containing no run identity. Preflight treats its output path as a collision probe and does not populate it. Resume requires an existing Plan 26 identity, checkpoint DB, episode ledger, and a resumable last terminal. `--unit`, `--all`, and `--resume` are mutually exclusive; resume derives original mode/target and refuses overrides.

Every invocation prints exactly one JSON object to stdout. A live result contains `contract_version`, `run_id`, `episode_id`, `terminal`, `mode`, `requested_unit_id`, `accepted_receipt` or `release_receipt`, `checkpoint_id`, `evidence_index_hash`, and `output_root`; human diagnostics go to stderr. Exit codes are section 14. When Codex/Gemini/retrieval credentials, executable identity, observable model identity, or external-data authorization are unavailable, preflight reports specific failed capability and exits 3. A live run that somehow reaches D03 with the same absence writes `SYSTEM_FAILURE` before transmission; it never simulates or switches family.

## 17. Test and adversarial acceptance matrix

### 17.1 Test layers

| Layer | Required proof |
|---|---|
| reducer/unit | write-once conflict, disjoint union associativity, head parent/version enforcement, monotonic counters/status, terminal once, exact partition |
| graph topology | START/END ownership, all node IDs/edges, exactly eight model job types, models cannot reach guarded authorities, arbitrary manifest lengths/DAGs |
| fake-transport integration | complete branch/loop/fan-out behavior, failure classification, targeted invalidation, bounds, structured receipts; terminal is marked `test_evidence_only` and cannot be copied to product output |
| live transport contract | isolated staging, package prompt resolution, CLI arguments, observed model identity, JSON/schema failure, timeouts, provider authorization |
| interruption/resume | each superstep and each fan-out member, pending-write reuse, crash recovery, identity drift refusal, lock/duplicate prevention, accepted-byte preservation |
| rendering/product | real renderer/rasterizer, positive contiguous pages, every-page inspections and cross-family reviews, actual PDF hashes, exact workbook coverage/final audit |
| live product acceptance | authorized real Codex/Gemini/source/render execution on actual curriculum; only this layer can establish curriculum quality |

Fake models prove orchestration only. They cannot establish source truth, curriculum quality, review independence in substance, `UNIT_ACCEPTED`, or `COMPLETE` in a release output root. Test graph outputs use a separate temporary root and an unmistakable non-product terminal envelope.

### 17.2 Mandatory adversarial cases

| Attack/fault | Expected result | Verification test |
|---|---|---|
| graph/test/prompt/capability/simulation presented as product | no success terminal | `test_no_nonproduct_success` |
| manifest has 1, 7, or 41 shuffled/DAG units | exact computed order/closure | `test_manifest_neutral_dynamic_run` |
| source/model output proposes next node/acceptance/terminal | ignored/rejected schema | `test_models_have_no_control_fields` |
| prompt resolved from cwd or root `prompts/` | preflight/system failure | `test_prompts_are_package_relative` |
| malformed/multiple/trailing CLI JSON | one bounded retry then failure | `test_malformed_cli_output_fails_closed` |
| decided model differs from observed executed model | system failure | `test_executed_model_must_match_route` |
| reviewer family equals any author/repair family | system failure | `test_same_family_review_rejected` |
| missing/duplicate/extra/stale/cross-unit source or visual member | join failure; no admission | `test_exact_fanout_denominators` |
| page 0, gap, duplicate, wrong hash, or omitted review page | no acceptance | `test_every_unit_page_required`, `test_every_workbook_page_required` |
| stale artifact/check/review/receipt hash | no acceptance/system integrity failure | `test_stale_hash_rejected` |
| repair changes unrelated pointer/file or parent in place | system failure; parent unchanged | `test_repair_boundary_and_immutability` |
| local defect attempts whole-unit regeneration | request/admission rejected | `test_local_repair_is_targeted` |
| counter/fingerprint exceeds frozen bound | convergence exhausted before activation | `test_repair_bound_reserved_first` |
| resume tries to rewrite accepted unit/PDF | system failure; bytes unchanged | `test_resume_preserves_accepted_bytes` |
| two resume processes | one lock winner; loser exits 2 | `test_duplicate_continuation_prevented` |
| workbook missing/extra/reordered accepted unit | no assembly/complete | `test_workbook_exact_manifest_coverage` |
| workbook repair changes any unit hash | system failure | `test_workbook_repair_cannot_change_unit` |
| legacy FSM/session bridge/simulation flag on Plan 26 | invocation rejected | `test_no_second_production_factory` |
| absent OpenAI/Google/retrieval authorization | fail before process/network call | `test_external_data_authorization_precedes_transmission` |
| sibling files visible in worker | preflight/system isolation failure | `test_worker_context_is_structurally_bounded` |
| checkpoint valid but append log corrupt, or converse | no acceptance/resume | `test_dual_persistence_correlation` |
| resume input reaches D01 or changes `created_at`/another global write-once field | topology/reducer failure; D01 activation count remains one for the run | `test_resume_bootstrap_skips_fresh_write_once_nodes` |
| orphan recovery tries `invoke(None)`, transport, retrieval, render, or a saved product frontier | test fails before side effect; only D00/D96/D98 execute | `test_orphan_recovery_is_read_only_and_terminal_only` |
| checkpoint namespace differs from root `""`, or thread ID lacks run/episode relation | invocation rejected | `test_checkpoint_thread_and_namespace_contract` |
| mixed static/dynamic visual predecessor join or empty visual subset | topology test rejects mixed join; barrier executes exactly once per map superstep and handles empty subset | `test_visual_send_reduce_barrier` |

Integration must inject SIGINT before/after each node and during each CLI process. It verifies one terminal per episode, `StateSnapshot.next/tasks` reconstruction, no repeated valid fan-out work, current counters, and identical accepted hashes after resume. Hard-crash tests seed snapshots whose saved next task is each of M01–M08 and prove recovery makes zero external calls before D03 in the later episode. API-contract tests pin the `StateGraph`, sequential `Send`-worker-to-reducer pattern, `SqliteSaver.get_tuple` pending writes, episode-derived threads, root namespace, `get_state`, and history behavior used here.

## 18. Migration and retirement boundary

Plan 26 activation is an atomic production cutover, not a long-lived dual run:

| Module/mechanism | Status after activation |
|---|---|
| `runtime/io.py`, deterministic portions of `checks.py`, curriculum verifiers/schemas/contracts | reused unchanged unless an interface adapter is required |
| `controller.CurriculumRuntime`, `routing.Selector`, `lesson_render.py`, `pdf_inspect.py`, `visual_maps.py`, logger, safe workbook concatenation primitive | adapted behind Plan 26 nodes/services |
| `model_worker.py` | replaced in production by `langgraph_factory.transport`; retained temporarily for Plan 25 historical tests |
| `curriculum_factory_graph.py` custom controller | replaced in production; retained read-only for Plan 25 historical/test compatibility |
| `factory_state.py`, `checkpoint.py`, `run_state.py` orchestration/lifecycle roles | replaced by typed graph state/SqliteSaver; historical tests may retain imports |
| `session_bridge.py`, `CROSS_FAMILY_BYPASS`, `ACCEPTED_PENDING_REVIEW` | prohibited from production Plan 26 |
| `controller.simulate`, CLI `--test-simulated*`, capability-only finalization | moved to test-only entry points or rejected by production CLI |
| legacy `workbook.assemble()` completion/terminal behavior | prohibited; only a nonterminal concatenate primitive may be extracted |

Cutover gates: the full Plan 26 tests pass; a live authorized acceptance run produces actual accepted artifacts; import/dependency audit shows `runtime.run_curriculum` reaches only `build_curriculum_factory_graph`; CLI help exposes no legacy simulation path; and a static call-graph test proves no second production factory. Only then may Plan 26 become active. Existing Plan 25 output roots remain readable historical evidence but are not resumable by Plan 26 because their identity/checkpoint format differs. No automatic migration fabricates LangGraph checkpoints.

## 19. Traceability matrix

| Prompt requirement | Specification | Node/state | Proposed implementation | Verification |
|---|---|---|---|---|
| graph is executable factory; thin CLI; one path | 0, 1, 4, 16, 18 | START–D98; FactoryInput/Output | `graph.py`, `run_curriculum.py` | `test_no_second_production_factory` |
| preserve Plan 25 product boundary and assess baseline | 1–2 | all | migration adapters | baseline/migration audit |
| exact dependencies/current official APIs | 3 | compiled graph/checkpointer metadata | requirements locks, `graph.py`, `persistence.py` | API-contract/lock tests |
| typed complete state, reducers, authorities | 5 | all listed channels | `state.py`, `reducers.py` | reducer/property tests |
| every deterministic/model node and exactly eight jobs | 6 | D00–D98, M01–M08 | `nodes/*`, `graph.py` | topology/catalog test |
| Codex author/source/visual/repair, Gemini independent review | 6.3, 7 | routes/execution receipts | `transport.py` | CLI/family/model identity tests |
| no wrappers/provider SDK/model HTTP | 1.2, 3, 7 | capability receipts | locks/import audit | forbidden-import test |
| complete graph/conditional edges/loops | 8 | cursor, guards, invalidations | `graph.py`, `routing.py` | topology/path coverage |
| bounded context, no adjacency context | 9 | pending packets/review packets | projection schemas/transport | structural isolation test |
| denominator-first fan-out/join/correlation | 8, 10 | source/visual/page denominators | `routing.py`, source/visual/review nodes | exact denominator adversaries |
| durable checkpointer/resume/interrupt | 11 | checkpoint metadata, episode/terminal history | `persistence.py`, D04/D96/D98 | interruption matrix |
| append-only evidence beyond checkpoints | 2.3, 5, 11, 13 | evidence/receipt/log fields | `evidence.py`, logger adapter | dual-layer audit test |
| targeted versioned repair and retests | 12 | heads, repair, invalidation, attempts/fingerprints | repair nodes/reducers | repair boundary/bound tests |
| unit acceptance complete denominator | 13.1 | deterministic checks, pages, reviews, accepted receipts | D16/D22/D23 | missing/stale/NOT_RUN matrix |
| full exact workbook and final release | 13.2 | coverage/workbook/pages/release | D24–D32 | coverage/unit immutability tests |
| exact terminal vocabulary/guards/END/exits | 14 | terminal/history/candidate | D98, CLI | terminal truth-table tests |
| package/output filesystem layout and prompt paths | 7, 15 | artifact paths/heads/index | package/evidence/path services | containment/path tests |
| exact preflight/one/all/resume commands; Arduino example neutral | 16 | input/effective run | CLI/D02 | CLI and neutral-manifest tests |
| live external authorization before transmission | 7.4, 16 | external authorizations/capabilities | D01/D03/transport | zero-call authorization test |
| fake vs live acceptance and adversarial tests | 17 | test-only envelope | test suites | CI test classification |
| migrate/retire custom controller without two factories | 18 | production import graph | CLI/build module | static call-graph test |
| success only actual requested unit or full workbook | 0, 13, 14 | accepted receipts/final audit | D22/D32/D98 | no-nonproduct-success test |
| no hardcoded curriculum name/count/order | 1.1, 8, 16 | effective run/cursor | D02/D05 | arbitrary-manifest test/static search |
| actual visuals, PDFs, all-page inspection/review | 6, 10, 13 | visual/page inventories/reviews | D10–D16, D26–D28 | real render/all-page tests |
| resolved decisions/no deferred architecture | 20 | contract metadata | all above | spec lint for banned placeholders |

## 20. Resolved decisions and remaining external prerequisites

### 20.1 Resolved decisions

1. The factory is one compiled root `StateGraph`, not subgraphs or a project graph.
2. Core/persistence pins are `langgraph==1.2.9` and `langgraph-checkpoint-sqlite==3.1.0`; synchronous SQLite is bounded to one local process with a lock and full durability settings.
3. `checkpoint_ns` is always the root `""`; each episode uses `thread_id=<run_id>:episode:<ordinal>`. Resume reads the prior thread without invoking it, then D04 imports validated state into the new episode thread.
4. Product retries are explicit graph loops, not LangGraph automatic retry policies.
5. Dynamic units use a manifest-derived state list and cursor; source/visual work uses denominator-first `Send` fan-out.
6. There are exactly eight model job types. Codex performs source/authoring/eligible visual/repair jobs; Gemini performs actual-output review. No wrapper or provider API is allowed.
7. One Gemini judge activation per unit/workbook review epoch is selected because the active meta-prompt contract requires one different-family judge per pass; every page remains an exact member of its result denominator.
8. All model inputs are package-schema projections staged in isolated workspaces; prompts are package-relative.
9. LangGraph checkpoints recover orchestration; repository append-only evidence proves the product. Acceptance audits both.
10. Every artifact is versioned/headed, every repair is one-owner/one-boundary, and accepted units are immutable through workbook work.
11. All six terminals are deterministic and episode-final; only interruption and a named external prerequisite pause are resumable.
12. Plan 26 adapts `runtime.run_curriculum` into the only production entry and retires legacy FSM/simulation/session-bridge routes from production.

### 20.2 External prerequisites before implementation activation

These are prerequisites, not undecided architecture:

- generate and commit the hash lock from the selected pins, then run the specified API-contract smoke test against the 1.2.9 wheel because the official reference page was one patch behind;
- confirm the installed `codex` and `gemini` CLI versions provide machine-readable observed executed-model identity; otherwise Plan 26 preflight must remain failed rather than infer identity;
- obtain a run-scoped external-data authorization record covering the precise OpenAI, Google, and primary-source data classes;
- provide live credentials/network access for Codex, Gemini, and authorized primary sources, plus working Pandoc/Typst/Poppler/render tools; and
- prove the host OS workspace sandbox can structurally deny reads outside each staged CLI workspace.

No architectural choice is deferred. If any prerequisite is absent, implementation may build/test deterministic orchestration with fakes but may not activate the production path or claim curriculum acceptance.

## 21. Specification quality-gate checklist

- [x] The compiled LangGraph graph, not a project-management graph, is the curriculum factory.
- [x] Only actual accepted unit/workbook artifacts are successful products.
- [x] Model calls use `codex exec` and `gemini`; wrappers/provider APIs are forbidden.
- [x] Routing, joins, retry counters, validation, repair admission, acceptance, persistence correlation, assembly, release, and terminals are deterministic.
- [x] Every model node has a bounded projection and structured output schema.
- [x] The selected LangGraph/checkpointer APIs, versions, thread/namespace, superstep, pending-write, and resume behavior are concrete.
- [x] All fan-out and page denominators reject missing, duplicate, extra, stale, invalid, failed, `NOT_RUN`, and cross-unit members.
- [x] Unit/workbook acceptance requires actual visuals, actual PDFs, every-page inspection, and independent actual-output review.
- [x] No graph, prompt, capability probe, simulation, test, report, or checkpoint is a product.
- [x] There is one production execution path and no curriculum-specific constant in graph implementation.
- [x] Plan 25 deterministic product mechanisms are preserved while custom orchestration is replaced.
- [x] The implementation phase is not performed by this specification.
