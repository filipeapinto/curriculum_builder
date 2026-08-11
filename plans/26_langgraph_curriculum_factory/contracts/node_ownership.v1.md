# N00 node ownership and layout freeze

The spec (section 15) proposes a filesystem layout and labels it explicitly
"none is created in this pass" — it is illustrative, not binding. The binding
write-set contract is `implementation.graph.v2.yaml`. Where the two disagree
or the graph is silent, this document is the one resolution; later node
prompts MUST follow it rather than re-deriving ownership from the spec.

## D00–D98 / M01–M08 -> owning N-node

Every deterministic (`D`) and model (`M`) node from spec section 6 is owned
by exactly one graph N-node, which implements its body. Registration
(`add_node`/`add_edge`/`add_conditional_edges`) is owned separately (see
"Topology ownership" below) because a node's body and its graph wiring are
written at different times in the dependency order.

| Spec node(s) | Owning N-node | Rationale |
|---|---|---|
| D00, D00R, D01, D02, D03 | N22_DETERMINISTIC_NODES (`nodes/inputs.py`) | bootstrap/freeze/effective-run/capability bodies; D03's capability probe calls into N13's transport module via `RuntimeContext`, not a compile-time import, so N22 has no dependency on N13 |
| D04, D92, D96 | N22_DETERMINISTIC_NODES (`nodes/inputs.py`), using N21's persistence primitives via `RuntimeContext` | resume/interrupt node bodies; the durable mechanics (SqliteSaver, `prepare_episode_invocation`) live in N21's `persistence.py` and are consumed, not re-implemented |
| D05 | N22_DETERMINISTIC_NODES (`nodes/sources.py`) | unit cursor selection |
| D06, D06B | N22_DETERMINISTIC_NODES (`nodes/sources.py`) | source request compilation and controller-fetched retrieval |
| D07 | N22_DETERMINISTIC_NODES (`nodes/sources.py`) | admission join |
| D08 | N22_DETERMINISTIC_NODES (`nodes/domain.py`) | domain validation/admission |
| D09 | N22_DETERMINISTIC_NODES (`nodes/content.py`) | content validation/admission |
| D10, D11, D12 | N22_DETERMINISTIC_NODES (`nodes/visuals.py`) | visual brief compilation, deterministic visual production, barrier/join |
| D13 | N22_DETERMINISTIC_NODES (`nodes/render.py`) | unit rendering |
| D14, D15 | N22_DETERMINISTIC_NODES (`nodes/render.py`, `nodes/review.py`) | page inventory/inspection; review-packet freeze |
| D16 | N31_REPAIR_ACCEPTANCE (`acceptance.py`) | unit evidence denominator reduction — paired with D22/D23 acceptance logic, not a one-off stub |
| D17, D18, D19, D20, D21 | N31_REPAIR_ACCEPTANCE (`repair.py`) | targeted repair engine: classification, planning, routing, admission, retest; shared boundary/diff/invalidation-DAG machinery reused by workbook repair |
| D22, D23 | N31_REPAIR_ACCEPTANCE (`acceptance.py`) | unit acceptance and checkpoint-correlation receipt |
| D24 | N32_WORKBOOK_TERMINALS (`workbook.py`) | exact manifest coverage proof; owns both the one-mode unit-terminal branch and the all-mode workbook branch |
| D25 | N32_WORKBOOK_TERMINALS (`workbook.py`) | workbook assembly |
| D26, D27 | N32_WORKBOOK_TERMINALS (`workbook.py`) | workbook render/inventory/inspect, review-packet freeze |
| D28 | N32_WORKBOOK_TERMINALS (`workbook.py`), calling N31's `acceptance.py` reduction primitive | workbook evidence denominator reduction reuses the unit reduction engine over a different denominator shape |
| D29, D31 | N32_WORKBOOK_TERMINALS (`workbook.py`), calling N31's `repair.py` engine | workbook-owned repair planning/admission reuses the targeted-repair engine with workbook boundaries |
| D30 | N22_DETERMINISTIC_NODES (`nodes/sources.py`) | prerequisite classification, adjacent to D06/D06B/D07 |
| D32 | N32_WORKBOOK_TERMINALS (`workbook.py`) | final release recomputation |
| D90, D91 | N23_MODEL_NODES (`model_nodes.py`) | attempt reservation and failure classification are model-attempt bookkeeping, colocated with the eight job dispatchers that consume them |
| D98 | N22_DETERMINISTIC_NODES (`nodes/terminal.py`) for `SYSTEM_FAILURE`/`INTERRUPTED`/`PAUSED_PREREQUISITE`/`CONVERGENCE_EXHAUSTED`; N32_WORKBOOK_TERMINALS (`workbook.py`) for `UNIT_ACCEPTED`/`COMPLETE` | terminal-writing is one function (`write_terminal`) in `nodes/terminal.py`; N32 calls it for the two product terminals it can reach, it does not fork the implementation |
| M01–M08 | N23_MODEL_NODES (`model_nodes.py`) | exactly the eight frozen job dispatchers, transported through N13 |

## Topology (registration) ownership

- N20_GRAPH_COMPILER (`graph.py`, `routing.py`): builds `StateGraph`,
  registers the fixed skeleton (`START -> D00 -> {D01.., D00R..} -> D04 ->
  D05`, the orphan-recovery `D00 -> D96 -> D98 -> END` path), and writes every
  pure guard function from spec section 8.2 in `routing.py`. It imports node
  bodies from N22/N23 but does not implement them.
- N30_UNIT_GRAPH (`unit_graph.py`): extends the graph N20 built with the full
  per-unit loop (`D06` through the `D16/D22/D23 -> D05` cycle, the D10-D12
  visual `Send` map/reduce, the D06/D06B/D07 source `Send` map/reduce, and
  the D17-D21 repair cycle edges). It is additive registration over the same
  `StateGraph` instance/module, not a second graph.
- N32_WORKBOOK_TERMINALS additionally registers the `D24 all-mode -> D25 ->
  ... -> D32 -> D98(COMPLETE)` branch and the workbook repair cycle
  (`D28 -> D29 -> D90/M08 -> D31 -> D26`), since that topology cannot exist
  before the workbook engine (`workbook.py`) it dispatches to has been
  written.

`build_curriculum_factory_graph()` itself (the one function spec section 4
names) is finalized in N30, once source/unit/visual wiring exists, but the
module file `graph.py` is created in N20; N30 edits the same file rather than
creating a parallel one. This is a sequential (not concurrent) write to
`runtime/langgraph_factory/graph.py` — legal because N30 depends on N20
(`all_of`) and the scheduler never selects both in the same generation.

## Naming: nodes/ package vs. top-level engine modules

`nodes/repair.py` and `nodes/workbook.py` (spec section 15's proposed
layout) are NOT created. Instead:

- `runtime/langgraph_factory/repair.py` (top-level, owned by N31) is the one
  targeted-repair engine, used by both unit (D17-D21) and workbook (D29,
  D31) repair.
- `runtime/langgraph_factory/acceptance.py` (top-level, owned by N31) is the
  one denominator-reduction/acceptance engine, used by both D16/D22/D23
  (unit) and D28 (workbook).
- `runtime/langgraph_factory/workbook.py` (top-level, owned by N32) is the
  workbook assembly/coverage/release engine (D24, D25, D26, D27, D29, D31,
  D32) plus the two product-terminal call sites.
- `nodes/` (owned by N22) contains exactly: `inputs.py`, `sources.py`,
  `domain.py`, `content.py`, `visuals.py`, `render.py`, `review.py`,
  `terminal.py`. There is no `nodes/repair.py` or `nodes/workbook.py`.

This resolves the spec's illustrative duplicate basenames (`repair.py` /
`workbook.py` appearing both inside and outside `nodes/`) into one file per
concept, matching `implementation.graph.v2.yaml`'s actual write sets exactly.

## `context.py` gap

Spec section 15 lists `context.py` in the proposed layout but no graph node's
`writes` set names it. Resolution: `RuntimeContext` construction (opening
services: path guards, evidence writer, subprocess transport registry,
source retriever, signal token, clock) is implemented as a factory function
inside `runtime/langgraph_factory/graph.py`, owned by N20. No standalone
`context.py` file is created. `RuntimeContext` the *type* (a frozen
dataclass, not checkpointed) lives in `state.py` per spec section 5.1,
owned by N11.
