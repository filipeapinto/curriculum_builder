"""The one production `StateGraph`: bindings, skeleton topology, and compilation.

This module owns registration, not node bodies. Every callable it registers is
resolved from N22's `node_registry()` or N23's `MODEL_NODE_ADAPTERS`; a binding
that is missing, placeholder, test-only, duplicated, or dangling fails the build
by stable ID rather than compiling into a graph that would look complete.

It also owns the two things no node body can own:

- the common node boundary (spec section 6.1), which injects `RuntimeContext`,
  records a graceful interrupt observed at the node's atomic boundary, and turns
  an unexpected exception into a classified `pending_failure` instead of letting
  an unproven state continue;
- the `RuntimeContext` factory itself (spec section 5.2), which opens the path
  guard, evidence writer, transport registry, source retriever, signal token and
  clock, and holds no model client and no routing authority.

Scope of this generation: the fixed skeleton only — `START -> D00 -> {D01 fresh
path, D00R resume path} -> D03 -> D04 -> {D05, D92}` plus the orphan-recovery
`D00 -> D96 -> D98 -> END` branch. The per-unit loop, the source/visual `Send`
map/reduce, and the workbook branch are registered by N30 and N32 into this same
builder; `DEFERRED_TOPOLOGY` names their owner for every node registered here
but not yet wired, so an undeclared unwired node still fails compilation.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import re
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from langgraph.errors import GraphBubbleUp
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime

from . import acceptance, routing, transport as tp, unit_graph, workbook
from .artifacts import ArtifactStore
from .egress import EgressGuard, ReceiptLog, RetrievalPolicy, SourceRetriever
from .evidence import EvidenceStore
from .model_nodes import (
    MODEL_BOOKKEEPING_NODES,
    MODEL_NODE_ADAPTERS,
    build_model_node_context,
)
from .nodes import NODE_CATALOGUE, node_registry
from .persistence import InterruptToken, open_checkpoint_saver
from .state import (
    FACTORY_INPUT_FIELDS,
    FACTORY_OUTPUT_FIELDS,
    FACTORY_STATE_FIELDS,
    FIELD_REDUCER_CLASSES,
    FactoryInput,
    FactoryOutput,
    FactoryState,
    RuntimeContext,
)

__all__ = [
    "GRAPH_NAME",
    "GraphBindingError",
    "DEFERRED_TOPOLOGY",
    "SKELETON_NORMAL_EDGES",
    "SKELETON_BRANCHES",
    "build_runtime_context",
    "binding_inventory",
    "unit_repair_binding_inventory",
    "full_binding_inventory",
    "validate_bindings",
    "register_skeleton",
    "register_unit_repair_topology",
    "register_workbook_topology",
    "build_curriculum_factory_graph",
    "compiled_topology",
    "graph_digest",
    "contract_digests",
]

GRAPH_NAME = "plan26_curriculum_factory"


class GraphBindingError(RuntimeError):
    """A production binding or edge was rejected before compilation."""


# Only these modules may supply a production node body. A callable from anywhere
# else — a test module, a notebook, a locally defined lambda — is rejected by
# stable ID, so "the graph compiled" can never mean "the graph compiled against
# a stand-in".
PRODUCTION_BINDING_MODULES: tuple[str, ...] = (
    "runtime.langgraph_factory.nodes",
    "runtime.langgraph_factory.model_nodes",
    "runtime.langgraph_factory.workbook",
    "runtime.langgraph_factory.repair",
    "runtime.langgraph_factory.acceptance",
)

PLACEHOLDER_NAME_MARKERS: tuple[str, ...] = (
    "stub",
    "placeholder",
    "fake",
    "dummy",
    "mock",
    "sample",
    "example",
    "todo",
    "noop",
    "test",
)

PLACEHOLDER_SOURCE_MARKERS: tuple[str, ...] = (
    "raise NotImplementedError",
    "TODO: implement",
    "placeholder implementation",
)

# Registered here, wired by a later graph node. A node that is neither wired by
# the skeleton/unit-path tables `_validate_topology` inspects nor declared here
# fails the build: silence about an unwired node is how a topology gap becomes
# a silent halt at runtime.
#
# D16 and D17 need no row: once their bodies are members of `available`, they
# are reached as real *destinations* of already-wired `unit_graph.UNIT_BRANCHES`
# sources (D08/D09/D12/D14/D91 -> D17, M05 -> D16 -- the six rows `unit_graph
# .DEFERRED_EDGES` names), so `_validate_topology`'s own `wired` set already
# contains them. D18-D23 are reached only from *inside* the unit repair cycle
# itself (D17 -> D18 -> ... -> D21 -> D16, D22 -> D23 -> D05), which is wired by
# `acceptance.register_unit_repair_path` (via `register_unit_repair_topology`,
# called after `register_skeleton` returns) rather than by any table
# `_validate_topology` reads -- so they are declared deferred here for the same
# reason M06/M07/M08 are: really wired, by a registration step this function
# does not itself see.
#
# D24 needs no row either, for the same reason D16/D17 do not: it is
# `D05_SELECT_NEXT_UNIT`'s own `manifest_exhausted` destination, a row
# `unit_graph.DEFERRED_EDGES` already names, so once D24 is a member of
# `available` it is a real destination `unit_graph.branch_destinations`
# resolves and `_validate_topology`'s `wired` set already contains it. D30 is
# an N22-owned node already wired as a normal member of `unit_graph
# .UNIT_BRANCHES`, not part of this node's own D24-D32 engine at all. D25-D29,
# D31, D32 are reached only from *inside* the workbook branch itself, which is
# wired by `workbook.register_workbook_path` (via `register_workbook_topology`,
# called after `register_unit_repair_topology` returns) rather than by any
# table `_validate_topology` reads -- so they are declared deferred here for
# the same reason D18-D23 are.
DEFERRED_TOPOLOGY: Mapping[str, str] = {
    "D18_PLAN_TARGETED_UNIT_REPAIR": "N31_REPAIR_ACCEPTANCE",
    "D19_ROUTE_UNIT_REPAIR": "N31_REPAIR_ACCEPTANCE",
    "D20_ADMIT_UNIT_REPAIR": "N31_REPAIR_ACCEPTANCE",
    "D21_RETEST_REQUIRED_DESCENDANTS": "N31_REPAIR_ACCEPTANCE",
    "D22_ACCEPT_UNIT": "N31_REPAIR_ACCEPTANCE",
    "D23_CHECKPOINT_ACCEPTED_UNIT": "N31_REPAIR_ACCEPTANCE",
    "M06_REPAIR_NAMED_UNIT_ARTIFACT": "N31_REPAIR_ACCEPTANCE",
    "D25_ASSEMBLE_WORKBOOK": "N32_WORKBOOK_TERMINALS",
    "D26_RENDER_INVENTORY_INSPECT_WORKBOOK": "N32_WORKBOOK_TERMINALS",
    "D27_FREEZE_WORKBOOK_REVIEW_PACKET": "N32_WORKBOOK_TERMINALS",
    "D28_REDUCE_WORKBOOK_EVIDENCE": "N32_WORKBOOK_TERMINALS",
    "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR": "N32_WORKBOOK_TERMINALS",
    "D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR": "N32_WORKBOOK_TERMINALS",
    "D32_RECOMPUTE_FINAL_RELEASE": "N32_WORKBOOK_TERMINALS",
    "M07_REVIEW_ACTUAL_WORKBOOK": "N32_WORKBOOK_TERMINALS",
    "M08_REPAIR_NAMED_WORKBOOK_DEFECT": "N32_WORKBOOK_TERMINALS",
}

SKELETON_NORMAL_EDGES: tuple[tuple[str, str], ...] = (
    (START, "D00_BOOTSTRAP_EPISODE"),
    ("D96_GRACEFUL_INTERRUPT_GATE", "D98_WRITE_TERMINAL"),
    ("D98_WRITE_TERMINAL", END),
)

SKELETON_BRANCHES: tuple[tuple[str, Callable[[Mapping[str, Any]], str]], ...] = (
    ("D00_BOOTSTRAP_EPISODE", routing.route_bootstrap),
    ("D01_VALIDATE_AND_FREEZE_INPUTS", routing.route_frozen_inputs),
    ("D02_COMPILE_EFFECTIVE_RUN", routing.route_effective_run),
    ("D00R_REVALIDATE_RESUME_IDENTITY", routing.route_resume_identity),
    ("D03_PROVE_CAPABILITIES", routing.route_capabilities),
    ("D04_INITIALIZE_OR_RESUME", routing.route_initialize_or_resume),
)


# --------------------------------------------------------------- runtime context


def _utc_clock() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_runtime_context(
    *,
    engine_root: Path | str,
    output_root: Path | str,
    run_id: str,
    curriculum_digest: str,
    authorization: Any = None,
    capability_proof: Mapping[str, Any] | None = None,
    retrieval_hosts: Sequence[str] = (),
    clock: Callable[[], Any] = _utc_clock,
    env_passthrough: Sequence[str] = (),
) -> RuntimeContext:
    """Open the services one invocation may reach (spec section 5.2).

    Constructed by the CLI after `prepare_episode_invocation` has fixed the run
    identity, and supplied to `invoke(context=...)`; it is deliberately not built
    inside the builder, because the transport and the authorization it enforces
    are bound to a run identity that does not exist at build time.
    """

    engine_root = Path(engine_root).resolve()
    output_root = Path(output_root).resolve()
    receipts = ReceiptLog(output_root / ".evidence" / "egress_receipts.jsonl")
    egress_guard = EgressGuard(receipts)
    return RuntimeContext(
        engine_root=engine_root,
        output_root=output_root,
        path_guard=ArtifactStore(output_root),
        evidence_service=EvidenceStore(output_root),
        transport_registry=tp.CliTransport(
            output_root=output_root,
            run_id=run_id,
            curriculum_digest=curriculum_digest,
            authorization=authorization,
            receipts=receipts,
            guard=egress_guard,
            ledger=tp.AttemptLedger(),
            capability_proof=capability_proof,
            env_passthrough=env_passthrough,
        ),
        source_retriever=SourceRetriever(
            guard=egress_guard,
            policy=RetrievalPolicy(allowed_hosts=frozenset(retrieval_hosts)),
        ),
        signal_token=InterruptToken(output_root),
        clock=clock,
    )


# ----------------------------------------------------------------- node boundary


def _mark_interrupt(update: Mapping[str, Any], node_id: str) -> dict[str, Any]:
    """Record a graceful signal on the guard record so routing stays pure."""

    marked = dict(update)
    guard = marked.get("pending_guard")
    guard = dict(guard) if isinstance(guard, Mapping) else {"node": node_id, "value": None}
    guard["interrupt_requested"] = True
    marked["pending_guard"] = guard
    return marked


def _boundary(node_id: str, body: Callable[..., Any], *, model_node: bool) -> Callable[..., Any]:
    """Wrap one node body in the common boundary of spec section 6.1.

    LangGraph injects `Runtime`, not the opened services, so the boundary is also
    the only place the `RuntimeContext` reaches a node body — N22's and N23's
    callables take it as an explicit argument precisely so they cannot fetch it
    themselves.
    """

    def node(state: Mapping[str, Any], runtime: Runtime[RuntimeContext]) -> dict[str, Any]:
        context = getattr(runtime, "context", None)
        try:
            if model_node:
                update = body(state, build_model_node_context(context))
            else:
                update = body(state, context)
        except GraphBubbleUp:
            # LangGraph's own control flow (interrupt/resume propagation) is not a
            # product failure and must reach the engine untouched.
            raise
        except Exception as error:  # the classified-failure contract of spec 6.1
            return {
                "pending_failure": {
                    "node": node_id,
                    "class": "system",
                    "cause": "unhandled",
                    "message": f"{type(error).__name__}: {error}",
                    "evidence": {"boundary": "node"},
                },
                "pending_guard": None,
            }
        token = getattr(context, "signal_token", None)
        if token is not None and bool(getattr(token, "is_set", lambda: False)()):
            return _mark_interrupt(update, node_id)
        return dict(update)

    node.__name__ = node_id
    node.__qualname__ = node_id
    node.__doc__ = getattr(body, "__doc__", None)
    node.plan26_binding = _binding_record(node_id, body)  # type: ignore[attr-defined]
    return node


def _underlying(body: Callable[..., Any]) -> Callable[..., Any]:
    """The authored function behind a decorated node, for identity and audit."""

    return getattr(body, "node_body", body)


def _binding_record(node_id: str, body: Callable[..., Any]) -> dict[str, Any]:
    target = _underlying(body)
    try:
        source = inspect.getsource(target)
    except (OSError, TypeError):  # pragma: no cover - a source-less callable is rejected
        source = ""
    return {
        "node_id": node_id,
        "module": getattr(target, "__module__", ""),
        "qualname": getattr(target, "__qualname__", ""),
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "source_lines": len(source.splitlines()),
    }


# ------------------------------------------------------------ binding validation


def binding_inventory() -> dict[str, Callable[..., Any]]:
    """Every node callable N20's own skeleton/unit-path tables resolve against.

    N31's unit-repair-cycle nodes (D16-D23) carry no `NODE_CATALOGUE` row and
    are deliberately absent from *this* function's return value even though
    they are real, wired members of the compiled production graph: several of
    N30's own tests in `test_plan26_unit_graph.py` independently recompute
    their expectation directly from this function's return value, so it stays
    exactly what it was before N31 (per N90 finding F1's own resolution --
    `full_binding_inventory()`/`unit_repair_binding_inventory()` below are the
    functions that widen it; this one never does). Use `unit_repair_binding_
    inventory()` for the actual widened set `build_curriculum_factory_graph`
    compiles against.

    N32's workbook engine (D24-D32, `workbook.WORKBOOK_NODE_BODIES`) is
    likewise absent from *this* function deliberately, not by oversight: D24
    is `D05_SELECT_NEXT_UNIT`'s own `manifest_exhausted` destination, and
    `unit_graph.DEFERRED_EDGES`/`unit_graph.UNIT_BRANCHES` (N30's frozen,
    already-verified tables) declare that edge deferred to N32 by name. If D24
    entered this function, `unit_graph.register_unit_path`'s *own*
    `available`-derived destination set for `D05_SELECT_NEXT_UNIT` would
    silently widen to include it -- correct for a production run, but it
    would falsify N30's own already-passing topology tests, which independently
    recompute their expectation from this exact function's return value.
    `register_workbook_topology` registers the workbook engine as an additive
    step over its own separate builder (N32 exercises it directly, not through
    `build_curriculum_factory_graph`), so the unit path's registered edges stay
    byte-identical to what they were before N32 and the workbook branch is
    still fully real -- just not reachable from `D05` in this generation,
    exactly as `unit_graph.DEFERRED_EDGES` documents.
    """

    bindings: dict[str, Callable[..., Any]] = dict(node_registry())
    for job_id, adapter in MODEL_NODE_ADAPTERS.items():
        bindings[job_id] = adapter
    bindings.update(MODEL_BOOKKEEPING_NODES)
    return bindings


def unit_repair_binding_inventory() -> dict[str, Callable[..., Any]]:
    """`binding_inventory()` plus this node's own D16-D23 unit-repair-cycle bodies.

    The set `build_curriculum_factory_graph` actually compiles the one
    production graph against (N90 finding F1): D16-D23 become real, reachable
    members of that graph, while D24-D32 (N32's still-deferred workbook
    engine) stay absent, exactly as `binding_inventory()`'s own docstring
    documents for that pair. Kept separate from `binding_inventory()` itself
    so N30's tests, which recompute their expectation directly from that
    function's return value, stay unaffected by this widening.
    """

    bindings = dict(binding_inventory())
    bindings.update(acceptance.UNIT_REPAIR_NODE_BODIES)
    return bindings


def full_binding_inventory() -> dict[str, Callable[..., Any]]:
    """`unit_repair_binding_inventory()` plus N32's workbook engine (D24-D32).

    The complete node set this generation's node bodies span. Kept separate
    from `binding_inventory()` itself for the reason documented there.
    """

    bindings = dict(unit_repair_binding_inventory())
    bindings.update(workbook.WORKBOOK_NODE_BODIES)
    return bindings


def _reject(code: str, node_id: str, detail: str) -> None:
    raise GraphBindingError(f"{code}:{node_id}: {detail}")


def validate_bindings(
    bindings: Mapping[str, Callable[..., Any]],
    *,
    required: Sequence[str],
) -> dict[str, dict[str, Any]]:
    """Reject a missing, placeholder, test-only, duplicate, or unusable binding."""

    for node_id in required:
        if node_id not in bindings:
            _reject("N20-BIND-MISSING", node_id, "no production callable is registered")

    seen: dict[tuple[str, str], str] = {}
    inventory: dict[str, dict[str, Any]] = {}
    for node_id in sorted(bindings):
        body = bindings[node_id]
        if not callable(body):
            _reject("N20-BIND-UNCALLABLE", node_id, f"binding is {type(body).__name__}")
        record = _binding_record(node_id, body)
        module = record["module"]
        if not any(
            module == allowed or module.startswith(f"{allowed}.")
            for allowed in PRODUCTION_BINDING_MODULES
        ):
            _reject("N20-BIND-PLACEHOLDER", node_id, f"module {module!r} is not a production node module")
        lowered = f"{module}.{record['qualname']}".lower()
        # Whole-word match, not substring: `D31_ADMIT_AND_RETEST_...` legitimately
        # contains "test" inside "retest", and a placeholder heuristic that
        # rejected every real "retest"/"latest"/"contest" binding would be a false
        # positive on the spec's own vocabulary, not a caught stand-in.
        marker = next(
            (m for m in PLACEHOLDER_NAME_MARKERS if re.search(rf"(?<![a-z]){re.escape(m)}(?![a-z])", lowered)),
            None,
        )
        if marker is not None:
            _reject("N20-BIND-PLACEHOLDER", node_id, f"binding name declares {marker!r}")
        if not record["source_sha256"] or record["source_lines"] == 0:
            _reject("N20-BIND-PLACEHOLDER", node_id, "binding has no readable source")
        source = inspect.getsource(_underlying(body))
        marker = next((m for m in PLACEHOLDER_SOURCE_MARKERS if m in source), None)
        if marker is not None:
            _reject("N20-BIND-PLACEHOLDER", node_id, f"binding body declares {marker!r}")
        identity = (module, record["qualname"])
        if identity in seen:
            _reject(
                "N20-BIND-DUPLICATE",
                node_id,
                f"shares callable {module}.{record['qualname']} with {seen[identity]}",
            )
        seen[identity] = node_id
        inventory[node_id] = record
    return inventory


def _validate_topology(registered: Sequence[str]) -> None:
    known = set(registered) | {START, END}
    wired: set[str] = set()
    for source, target in SKELETON_NORMAL_EDGES:
        for endpoint in (source, target):
            if endpoint not in known:
                _reject("N20-EDGE-DANGLING", endpoint, f"edge {source} -> {target} names an unregistered node")
        wired.update({source, target})
    for source, path in SKELETON_BRANCHES:
        if source not in known:
            _reject("N20-EDGE-DANGLING", source, "conditional edge source is not registered")
        wired.add(source)
        for target in routing.guard_destinations(source):
            if target not in known:
                _reject(
                    "N20-EDGE-DANGLING",
                    target,
                    f"{source} branch {path.__name__} names an unregistered destination",
                )
            wired.add(target)
    for source, target in unit_graph.UNIT_NORMAL_EDGES:
        wired.update({source, target})
    for source, _ in unit_graph.UNIT_BRANCHES:
        wired.add(source)
        wired.update(unit_graph.branch_destinations(source, registered))
    for node_id in registered:
        if node_id in wired:
            continue
        owner = DEFERRED_TOPOLOGY.get(node_id)
        if owner is None:
            _reject(
                "N20-NODE-UNDECLARED",
                node_id,
                "is registered but neither wired by the skeleton nor declared deferred",
            )


# ---------------------------------------------------------------- registration


def register_skeleton(
    builder: StateGraph,
    bindings: Mapping[str, Callable[..., Any]],
) -> dict[str, dict[str, Any]]:
    """Register every available node and the fixed skeleton edges.

    N30 and N32 extend the same builder by adding their own `add_node`-free
    `add_edge`/`add_conditional_edges` calls after this returns; nothing here is
    rewritten by them, so the skeleton stays the one place START, the recovery
    branch, and the single edge to END are decided.
    """

    routing.assert_guard_table_total(NODE_CATALOGUE)
    inventory = validate_bindings(bindings, required=_skeleton_required_nodes())
    _validate_topology(sorted(bindings))

    for node_id in sorted(bindings):
        model_node = node_id in MODEL_NODE_ADAPTERS
        builder.add_node(node_id, _boundary(node_id, bindings[node_id], model_node=model_node))

    for source, target in SKELETON_NORMAL_EDGES:
        builder.add_edge(source, target)

    for source, path in SKELETON_BRANCHES:
        destinations = routing.guard_destinations(source)
        builder.add_conditional_edges(source, path, {target: target for target in destinations})

    unit_graph.register_unit_path(builder, sorted(bindings))

    return inventory


def register_unit_repair_topology(builder: StateGraph, available: Sequence[str]) -> dict[str, tuple[str, ...]]:
    """Wire D16-D23's internal repair/acceptance cycle, additively over `register_skeleton`.

    Called from `build_curriculum_factory_graph` immediately after `register_
    skeleton` (which has already `add_node`-registered every member of
    `unit_repair_binding_inventory()`, D16-D23 included) and after `unit_graph
    .register_unit_path` (run inside `register_skeleton` itself). This closes
    N90 finding F1 for the six DEFERRED_EDGES rows N31 owns: those six edges
    are not added here -- they are `unit_graph.py`'s own rows, and resolve
    automatically the moment D16/D17 are members of the bindings `register_
    skeleton` receives -- this function adds only the loop internal to D16-D23
    itself, which no other module owns.
    """

    return acceptance.register_unit_repair_path(builder, available)


def register_workbook_topology(builder: StateGraph) -> dict[str, tuple[str, ...]]:
    """Register D24-D32 and wire the workbook branch, additively over `register_skeleton`.

    Not called by `build_curriculum_factory_graph`: this generation's single
    compile point is the N20-owned skeleton/unit-path catalogue only (spec
    section 8's D00-D23/M01-M06/D90/D91), and `binding_inventory()`'s own
    docstring documents why D24-D32 must stay absent from it. N32 owns wiring
    this function into whatever the production compile point becomes once the
    workbook branch is in scope; until then it is exercised directly, over its
    own builder, the way N32's own topology test already does.
    `register_skeleton` itself must never see these bindings; this function
    adds exactly the nodes `register_skeleton` did not, then wires them over
    the *full* merged node set so `workbook.register_workbook_path` can
    resolve `D90`/`D91`/`D98`/M07/M08 as real, already-registered targets.
    """

    workbook_bindings = dict(workbook.WORKBOOK_NODE_BODIES)
    validate_bindings(workbook_bindings, required=tuple(workbook_bindings))
    for node_id in sorted(workbook_bindings):
        if node_id in builder.nodes:
            # `build_curriculum_factory_graph` now compiles against `full_
            # binding_inventory()`, so `register_skeleton` has already added
            # these nodes; only N32's own direct-builder topology test still
            # calls this function before any `add_node` for D24-D32 exists.
            continue
        builder.add_node(node_id, _boundary(node_id, workbook_bindings[node_id], model_node=False))
    return workbook.register_workbook_path(builder, sorted(full_binding_inventory()))


def _skeleton_required_nodes() -> tuple[str, ...]:
    required = {source for source, _ in SKELETON_BRANCHES}
    for source, target in SKELETON_NORMAL_EDGES:
        required.update({source, target})
    for source, _ in SKELETON_BRANCHES:
        required.update(routing.guard_destinations(source))
    return tuple(sorted(required - {START, END}))


def build_curriculum_factory_graph(
    *, engine_root: Path, output_root: Path
) -> CompiledStateGraph:
    """Build and compile the one production graph (spec section 4).

    Compiles exactly once, over the output-root `SqliteSaver` N21 opens. The
    returned graph is invoked with `context=build_runtime_context(...)`; no
    services are captured at build time, so the compiled object carries no
    run identity and no authorization.

    Compiles against `full_binding_inventory()`, not `binding_inventory()` or
    `unit_repair_binding_inventory()`: D16-D23 (N31's unit repair/acceptance
    cycle) and D24-D32 (N32's workbook engine) are both real, wired members of
    the one compiled production graph (N90 findings F1 and F2). `register_
    unit_repair_topology` is called immediately after `register_skeleton` to
    wire the loop internal to D16-D23 that no other module owns; `register_
    workbook_topology` is called immediately after that to wire D24-D32's own
    internal loop additively over the same builder. Once D24-D32's bodies are
    members of the bindings `register_skeleton` passes to `unit_graph
    .register_unit_path`, the `(D05_SELECT_NEXT_UNIT, manifest_exhausted) ->
    D24_PROVE_EXACT_MANIFEST_COVERAGE` row in `unit_graph.DEFERRED_EDGES`
    resolves automatically, the same way N31's six rows did.
    """

    engine_root = Path(engine_root).resolve()
    output_root = Path(output_root).resolve()
    builder: StateGraph = StateGraph(
        FactoryState,
        context_schema=RuntimeContext,
        input_schema=FactoryInput,
        output_schema=FactoryOutput,
    )
    bindings = full_binding_inventory()
    register_skeleton(builder, bindings)
    register_unit_repair_topology(builder, sorted(bindings))
    register_workbook_topology(builder)
    saver, _connection = open_checkpoint_saver(output_root)
    return builder.compile(checkpointer=saver, name=GRAPH_NAME)


# ---------------------------------------------------------------------- digest


def _canonical_digest(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def compiled_topology(compiled: CompiledStateGraph) -> dict[str, Any]:
    """The node/edge structure of an actually compiled graph, not a declared one."""

    drawn = compiled.get_graph()
    return {
        "name": compiled.name,
        "nodes": sorted(drawn.nodes),
        "edges": sorted(
            [edge.source, edge.target, bool(edge.conditional)] for edge in drawn.edges
        ),
    }


def contract_digests() -> dict[str, str]:
    """File digests of every frozen model prompt and output schema.

    Folded into the graph digest so prompt or schema drift is visible as graph
    drift: the same topology over a changed prompt is not the same graph.
    """

    digests: dict[str, str] = {}
    registry = tp.load_job_registry()
    for job_id in sorted(registry):
        route = registry[job_id]
        for path in (tp.resolve_prompt_path(route), tp.resolve_schema_path(route)):
            path = Path(path)
            digests[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


def graph_digest(compiled: CompiledStateGraph) -> str:
    """Canonical-JSON digest over topology, bindings, state schema, and contracts.

    Identical real bindings give an identical digest; a changed node body,
    reducer declaration, prompt, or schema changes it. Python object identity is
    deliberately not an input, so two builds in one process and two builds in two
    processes agree.
    """

    payload = {
        "topology": compiled_topology(compiled),
        "bindings": [
            _binding_record(node_id, body)
            for node_id, body in sorted(binding_inventory().items())
        ],
        "state": {
            "fields": [[field, FIELD_REDUCER_CLASSES[field]] for field in FACTORY_STATE_FIELDS],
            "input": list(FACTORY_INPUT_FIELDS),
            "output": list(FACTORY_OUTPUT_FIELDS),
        },
        "contracts": contract_digests(),
    }
    return _canonical_digest(payload)
