"""Plan 26 topology gate (spec sections 3.3, 4, 8): N20's compiled skeleton.

Every assertion here runs against a real `StateGraph`/`CompiledStateGraph` built
from the real N22/N23 callables. Nothing is mocked: a simulated compilation
would prove that a stand-in compiles, which is the one thing this file exists to
rule out.

Scope. N20 registers the fixed skeleton:

    START -> D00 -> {D01 -> D02, D00R} -> D03 -> D04 -> {D05, D92}
    D00 -> D96 -> D98 -> END        (orphan recovery)

N30 has since registered the per-unit path (D05-D15 with its source and visual
`Send` map/reduce) into the same builder, and N31/N32 still owe the repair,
acceptance, and workbook branches. So these tests assert N20's properties —
binding rejection by stable ID, bounded cycles, worker->barrier fan-out shape,
model nodes holding no routing or acceptance authority — against whatever
topology is actually compiled now, rather than against a frozen skeleton
snapshot that a later graph node would falsify by doing its job.

Skips only where the hash-locked environment is absent; the node's evidence was
produced by running this file inside it.
"""

import ast
import hashlib
import re
import shutil
import tempfile
import unittest
from pathlib import Path

try:  # pragma: no cover - environment probe, not behavior
    import langgraph  # noqa: F401
    import langgraph.checkpoint.sqlite  # noqa: F401
except ModuleNotFoundError as exc:  # pragma: no cover
    raise unittest.SkipTest(
        "plan26 hash-locked environment not installed "
        "(python3 -m pip install --require-hashes -r requirements/plan26.lock): "
        f"{exc}"
    ) from exc

import pytest
from langgraph._internal._constants import RESERVED
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Send

from runtime.langgraph_factory import graph as G
from runtime.langgraph_factory import model_nodes as mn
from runtime.langgraph_factory import routing as R
from runtime.langgraph_factory import transport as tp
from runtime.langgraph_factory.nodes import NODE_CATALOGUE, node_registry
from runtime.langgraph_factory.state import (
    FACTORY_STATE_FIELDS,
    FactoryInput,
    FactoryOutput,
    FactoryState,
    RuntimeContext,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPH_PY = REPO_ROOT / "runtime" / "langgraph_factory" / "graph.py"
ROUTING_PY = REPO_ROOT / "runtime" / "langgraph_factory" / "routing.py"

# Spec 8.1: "There is no edge from a model directly to acceptance, terminal,
# checkpoint initialization, unit selection, workbook assembly, or release",
# plus resume re-entry (spec 6.2 D92 forbids a model as a stored destination).
#
# The reduction nodes D16/D28 are deliberately NOT here: spec 8.1 wires
# `M05 -> D16` and `M07 -> D28` on purpose, because a review is *evidence for*
# the code-computed denominator, not the reduction itself. "Models hold no
# reduction authority" is proven below as a channel-authority property, which is
# where that authority actually lives.
AUTHORITY_NODES = frozenset({
    "D04_INITIALIZE_OR_RESUME",
    "D05_SELECT_NEXT_UNIT",
    "D22_ACCEPT_UNIT",
    "D23_CHECKPOINT_ACCEPTED_UNIT",
    "D24_PROVE_EXACT_MANIFEST_COVERAGE",
    "D25_ASSEMBLE_WORKBOOK",
    "D32_RECOMPUTE_FINAL_RELEASE",
    "D92_REENTER_VALIDATED_FRONTIER",
    "D98_WRITE_TERMINAL",
    END,
})

# (dispatching node, fan-out guard value) -> (dispatching guard, worker, barrier).
# The barrier is the deterministic node that owns the fan-out's denominator and to
# which the worker returns; for M01 that is the next node of whichever superstep
# the phase advance selects. A model fan-out's dispatching guard resolves to D90,
# not to the worker: the `Send`s are emitted by D90's guard, from the packet D90
# restaged with one committed attempt reservation per member.
FANOUT_SHAPES = {
    ("D06_COMPILE_SOURCE_REQUESTS", "discovery_fanout"): (
        R.route_source_discovery_fanout,
        "M01_RESEARCH_UNIT_SOURCES",
        "D06B_RETRIEVE_SOURCE_CANDIDATES",
    ),
    ("D06B_RETRIEVE_SOURCE_CANDIDATES", "interpretation_fanout"): (
        R.route_source_interpretation_fanout,
        "M01_RESEARCH_UNIT_SOURCES",
        "D07_CORRELATE_AND_ADMIT_SOURCES",
    ),
    ("D10_COMPILE_VISUAL_BRIEFS", "deterministic_visual_fanout"): (
        R.route_visual_briefs,
        "D11_CREATE_DETERMINISTIC_VISUALS",
        "D12_VISUAL_BARRIER_AND_JOIN",
    ),
    ("D12_VISUAL_BARRIER_AND_JOIN", "model_visual_fanout"): (
        R.route_visual_barrier,
        "M04_CREATE_UNIT_VISUALS",
        "D12_VISUAL_BARRIER_AND_JOIN",
    ),
}


def _send_emitting_guard(source: str, value: str):
    """The guard that actually emits the `Send`s for this fan-out, and its record.

    For a model fan-out that is D90's guard reading D90's restaged packet, because
    spec 6.2 requires the attempt counter to be committed before dispatch; for a
    deterministic fan-out it is the dispatching node's own guard.
    """

    if R.FANOUT_GUARDS[source][value] == R.ATTEMPT_RESERVATION:
        return R.route_attempt_reservation, R.ATTEMPT_RESERVATION, "authorized"
    return FANOUT_SHAPES[(source, value)][0], source, value


@pytest.fixture(scope="module")
def output_root():
    root = Path(tempfile.mkdtemp(prefix="plan26_n20_topology_"))
    yield root
    shutil.rmtree(root, ignore_errors=True)


@pytest.fixture(scope="module")
def compiled(output_root) -> CompiledStateGraph:
    return G.build_curriculum_factory_graph(engine_root=REPO_ROOT, output_root=output_root)


def fresh_builder() -> StateGraph:
    return StateGraph(
        FactoryState,
        context_schema=RuntimeContext,
        input_schema=FactoryInput,
        output_schema=FactoryOutput,
    )


# ======================================================= state/channel precondition


def test_the_state_schema_declares_no_langgraph_reserved_channel_name():
    """A reserved channel name makes the production state schema uncompilable.

    LangGraph 1.2.9 rejects `checkpoint_ns` (and `checkpoint_id`, `configurable`,
    ...) as channel names in `validate_graph`, so any such field in
    `FactoryState` fails compilation of the one production graph.
    """

    clashes = sorted(set(FACTORY_STATE_FIELDS) & set(RESERVED))
    assert clashes == [], (
        f"FactoryState declares LangGraph-reserved channel name(s) {clashes}; "
        f"owner N11_STATE_REDUCERS (rework edge `state_or_reducer`)"
    )


# ====================================================== TEST 1: the catalogue compiles


def test_the_available_catalogue_compiles_against_real_node_callables(compiled):
    bindings = G.binding_inventory()
    registry = node_registry()

    assert compiled.name == G.GRAPH_NAME == "plan26_curriculum_factory"
    assert isinstance(compiled, CompiledStateGraph)

    # 22 deterministic bodies (N22) + 8 model adapters + D90/D91 (N23), all real
    # callables.
    assert set(registry) == set(NODE_CATALOGUE)
    assert len(registry) == 22
    assert set(mn.MODEL_NODE_ADAPTERS) == set(mn.MODEL_NODE_IDS)
    assert len(mn.MODEL_NODE_ADAPTERS) == 8
    assert set(mn.MODEL_BOOKKEEPING_NODES) == {R.ATTEMPT_RESERVATION, R.MODEL_FAILURE_CLASSIFIER}
    assert set(bindings) == (
        set(registry) | set(mn.MODEL_NODE_ADAPTERS) | set(mn.MODEL_BOOKKEEPING_NODES)
    )
    assert len(bindings) == 32

    # P-N20-001 (root cause: N90 finding F1, closed by N31's approved rework
    # P-N31-001): once a downstream graph node correctly wires D16-D23/M06 into
    # the one production graph, the compiled node set is wider than
    # `binding_inventory()` by design — D16-D23 carry no `NODE_CATALOGUE` row
    # and were never part of that function's contract (see its own docstring).
    # This asserts the invariant that actually holds in every generation: every
    # node this node's own skeleton requires, plus everything `binding_
    # inventory()` declares, is present in the compiled graph. A genuinely
    # missing or wrong skeleton node still fails this.
    drawn = compiled.get_graph()
    compiled_nodes = set(drawn.nodes) - {START, END}
    skeleton_required = set(G._skeleton_required_nodes()) | set(bindings)
    assert skeleton_required <= compiled_nodes, sorted(skeleton_required - compiled_nodes)

    for node_id, body in bindings.items():
        module = G._binding_record(node_id, body)["module"]
        assert module.startswith("runtime.langgraph_factory."), (node_id, module)


def test_start_has_exactly_one_edge_and_d98_is_the_only_registered_end_edge(compiled):
    drawn = compiled.get_graph()
    starts = [edge for edge in drawn.edges if edge.source == START]
    assert [edge.target for edge in starts] == ["D00_BOOTSTRAP_EPISODE"]

    registered_end_sources = sorted(
        source for source, target in G.SKELETON_NORMAL_EDGES if target == END
    )
    assert registered_end_sources == ["D98_WRITE_TERMINAL"]

    # D98's body is the real N22-owned terminal writer, not a local shim.
    d98 = node_registry()["D98_WRITE_TERMINAL"]
    assert G._binding_record("D98_WRITE_TERMINAL", d98)["module"] == (
        "runtime.langgraph_factory.nodes.terminal"
    )

    # LangGraph draws a dead-end node as reaching END. In this skeleton the only
    # such nodes are the frontier N30 still owes; nothing else leaks to END.
    drawn_end = {edge.source for edge in drawn.edges if edge.target == END}
    assert drawn_end - {"D98_WRITE_TERMINAL"} <= set(G.DEFERRED_TOPOLOGY)
    for node_id in drawn_end - {"D98_WRITE_TERMINAL"}:
        assert G.DEFERRED_TOPOLOGY[node_id] == "N30_UNIT_GRAPH"


def test_the_skeleton_wires_exactly_the_declared_edges(compiled):
    topology = G.compiled_topology(compiled)
    edges = {(source, target) for source, target, _ in topology["edges"]}

    for source, target in (
        (START, "D00_BOOTSTRAP_EPISODE"),
        ("D00_BOOTSTRAP_EPISODE", "D01_VALIDATE_AND_FREEZE_INPUTS"),
        ("D00_BOOTSTRAP_EPISODE", "D00R_REVALIDATE_RESUME_IDENTITY"),
        ("D00_BOOTSTRAP_EPISODE", "D96_GRACEFUL_INTERRUPT_GATE"),
        ("D01_VALIDATE_AND_FREEZE_INPUTS", "D02_COMPILE_EFFECTIVE_RUN"),
        ("D02_COMPILE_EFFECTIVE_RUN", "D03_PROVE_CAPABILITIES"),
        ("D00R_REVALIDATE_RESUME_IDENTITY", "D03_PROVE_CAPABILITIES"),
        ("D03_PROVE_CAPABILITIES", "D04_INITIALIZE_OR_RESUME"),
        ("D04_INITIALIZE_OR_RESUME", "D05_SELECT_NEXT_UNIT"),
        ("D04_INITIALIZE_OR_RESUME", "D92_REENTER_VALIDATED_FRONTIER"),
        ("D96_GRACEFUL_INTERRUPT_GATE", "D98_WRITE_TERMINAL"),
        ("D98_WRITE_TERMINAL", END),
    ):
        assert (source, target) in edges, f"missing skeleton edge {source} -> {target}"

    # Orphan recovery reaches no product node: D00's recovery branch and D96's
    # single successor are the whole of it.
    assert {t for s, t in edges if s == "D96_GRACEFUL_INTERRUPT_GATE"} == {
        "D98_WRITE_TERMINAL"
    }


# ============================================ TEST 2: bad bindings fail by stable ID


def _placeholder_node(state, runtime):  # pragma: no cover - never registered
    return {}


def test_a_missing_callable_fails_the_build_by_stable_id():
    bindings = G.binding_inventory()
    bindings.pop("D98_WRITE_TERMINAL")
    with pytest.raises(G.GraphBindingError, match=r"N20-BIND-MISSING:D98_WRITE_TERMINAL"):
        G.register_skeleton(fresh_builder(), bindings)


def test_a_test_only_or_placeholder_callable_fails_the_build_by_stable_id():
    bindings = G.binding_inventory()
    bindings["D05_SELECT_NEXT_UNIT"] = _placeholder_node
    with pytest.raises(G.GraphBindingError, match=r"N20-BIND-PLACEHOLDER:D05_SELECT_NEXT_UNIT"):
        G.register_skeleton(fresh_builder(), bindings)


def test_a_duplicate_callable_fails_the_build_by_stable_id():
    bindings = G.binding_inventory()
    bindings["D05_SELECT_NEXT_UNIT"] = bindings["D13_RENDER_UNIT"]
    with pytest.raises(G.GraphBindingError, match=r"N20-BIND-DUPLICATE:"):
        G.register_skeleton(fresh_builder(), bindings)


def test_an_uncallable_binding_fails_the_build_by_stable_id():
    bindings = G.binding_inventory()
    bindings["D05_SELECT_NEXT_UNIT"] = "not a callable"
    with pytest.raises(G.GraphBindingError, match=r"N20-BIND-UNCALLABLE:D05_SELECT_NEXT_UNIT"):
        G.register_skeleton(fresh_builder(), bindings)


def test_a_dangling_skeleton_destination_fails_the_build_by_stable_id(monkeypatch):
    # Pin the required set to the real skeleton so the dangling-endpoint check is
    # what rejects the edge, not the missing-binding check that shadows it.
    required = G._skeleton_required_nodes()
    monkeypatch.setattr(G, "_skeleton_required_nodes", lambda: required)
    monkeypatch.setattr(
        G,
        "SKELETON_NORMAL_EDGES",
        G.SKELETON_NORMAL_EDGES + (("D98_WRITE_TERMINAL", "D99_NOT_A_NODE"),),
    )
    with pytest.raises(G.GraphBindingError, match=r"N20-EDGE-DANGLING:D99_NOT_A_NODE"):
        G.register_skeleton(fresh_builder(), G.binding_inventory())


def test_a_wired_node_with_no_callable_fails_the_build_by_stable_id(monkeypatch):
    monkeypatch.setattr(
        G,
        "SKELETON_NORMAL_EDGES",
        G.SKELETON_NORMAL_EDGES + (("D98_WRITE_TERMINAL", "D99_NOT_A_NODE"),),
    )
    with pytest.raises(G.GraphBindingError, match=r"N20-BIND-MISSING:D99_NOT_A_NODE"):
        G.register_skeleton(fresh_builder(), G.binding_inventory())


def test_an_unwired_undeclared_node_fails_the_build_by_stable_id(compiled, monkeypatch):
    # P-N20-001: the victim is read from the live table AND filtered against the
    # live compiled topology, not just picked as the alphabetically-first key. A
    # `DEFERRED_TOPOLOGY` entry whose node a downstream graph node has since
    # wired is no longer undeclared-and-unwired -- popping it would not
    # reproduce N20-NODE-UNDECLARED, so it is not a valid victim any more. Only
    # a key with no compiled edge at all is still what this negative case needs.
    wired_endpoints = {
        endpoint
        for source, target, _ in G.compiled_topology(compiled)["edges"]
        for endpoint in (source, target)
    }
    candidates = sorted(set(G.DEFERRED_TOPOLOGY) - wired_endpoints)
    assert candidates, (
        "every DEFERRED_TOPOLOGY entry is now wired into the compiled graph, so "
        "this fixture needs a human decision (a real registered-but-unwired-and-"
        "undeclared node to pop), not a silent skip"
    )
    node_id = candidates[0]
    deferred = dict(G.DEFERRED_TOPOLOGY)
    deferred.pop(node_id)
    monkeypatch.setattr(G, "DEFERRED_TOPOLOGY", deferred)
    with pytest.raises(
        G.GraphBindingError, match=rf"N20-NODE-UNDECLARED:{re.escape(node_id)}"
    ):
        G.register_skeleton(fresh_builder(), G.binding_inventory())


def test_an_unrouted_declared_guard_value_fails_the_build_by_stable_id(monkeypatch):
    destinations = {k: dict(v) for k, v in R.GUARD_DESTINATIONS.items()}
    destinations["D05_SELECT_NEXT_UNIT"].pop("manifest_exhausted")
    monkeypatch.setattr(R, "GUARD_DESTINATIONS", destinations)
    with pytest.raises(R.RoutingViolation, match=r"N20-GUARD-UNROUTED:D05_SELECT_NEXT_UNIT"):
        G.register_skeleton(fresh_builder(), G.binding_inventory())


# ================================================= TEST 3: cycles cross a real guard


def _simple_cycles(edges) -> set[frozenset[str]]:
    """Every simple cycle of the compiled graph, as its node set.

    Each cycle is enumerated once by only extending a path through nodes that
    sort after its entry point, so `A -> B -> A` is not also reported as
    `B -> A -> B`.
    """

    successors: dict[str, set[str]] = {}
    for source, target in edges:
        successors.setdefault(source, set()).add(target)

    cycles: set[frozenset[str]] = set()

    def walk(node, start, path):
        for target in sorted(successors.get(node, ())):
            if target == start and len(path) >= 2:
                cycles.add(frozenset(path))
            elif target not in path and target > start:
                walk(target, start, path | {target})

    for start in sorted(successors):
        walk(start, start, {start})
    return cycles


def _cycle_bounds(cycle: frozenset[str]) -> list[str]:
    """The members of `cycle` that stop it repeating indefinitely.

    A node bounds a cycle if it either declares an exhaustion guard value whose
    destination leaves the cycle, or dispatches a fan-out that refuses to repeat
    without a freshly staged worker projection — the guard invents no projection,
    so a further lap requires work some node committed a denominator to.
    """

    bounds: list[str] = []
    for node_id in sorted(cycle):
        row = R.GUARD_DESTINATIONS.get(node_id, {})
        if any("exhausted" in value and row[value] not in cycle for value in row):
            bounds.append(node_id)
            continue
        if node_id not in R.FANOUT_GUARDS:
            continue
        for value in R.FANOUT_GUARDS[node_id]:
            guard, guard_node, guard_value = _send_emitting_guard(node_id, value)
            with pytest.raises(R.RoutingViolation, match="no staged"):
                guard({"pending_guard": {"node": guard_node, "value": guard_value, "detail": {}}})
        bounds.append(node_id)
    return bounds


def test_every_cycle_in_the_compiled_graph_crosses_an_exhaustion_guard(compiled):
    """No wired cycle can repeat forever, and none of them is a closed trap.

    Spec 8.1 wires real loops — the M01 discovery superstep, the visual barrier's
    worker/barrier join, and (once N31/N32 land) the repair and workbook cycles.
    What the graph must never contain is a cycle with no deterministic bound, so
    this asserts the bound for every cycle that is actually compiled and holds
    the frozen guard rows the not-yet-wired cycles will close through.
    """

    edges = {
        (source, target)
        for source, target, _ in G.compiled_topology(compiled)["edges"]
        if target != END
    }
    cycles = _simple_cycles(edges)

    # Not vacuous: spec 8.1's own discovery superstep is wired and is a cycle. It
    # runs through D90, which is where the attempt bound that closes it is committed.
    assert frozenset({
        "D06B_RETRIEVE_SOURCE_CANDIDATES",
        R.ATTEMPT_RESERVATION,
        "M01_RESEARCH_UNIT_SOURCES",
    }) in cycles

    for cycle in sorted(cycles, key=sorted):
        assert _cycle_bounds(cycle), (
            f"cycle {sorted(cycle)} crosses no exhaustion guard and no fan-out "
            "dispatcher, so nothing stops it repeating"
        )
        exits = {
            target
            for source, target in edges
            if source in cycle and target not in cycle
        } - {R.INTERRUPT_GATE, R.TERMINAL}
        assert exits, f"cycle {sorted(cycle)} reaches no product node outside itself"

    # Every loop-closing guard row exhausts deterministically before repeating.
    for node_id in ("D17_CLASSIFY_UNIT_FINDINGS", "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR"):
        assert R.GUARD_DESTINATIONS[node_id]["convergence_exhausted"] == R.TERMINAL
    assert R.GUARD_DESTINATIONS["D18_PLAN_TARGETED_UNIT_REPAIR"]["convergence_exhausted"] == (
        R.TERMINAL
    )
    assert R.GUARD_DESTINATIONS["D90_RESERVE_MODEL_ATTEMPT"]["exhausted"] == R.TERMINAL
    assert R.GUARD_DESTINATIONS["D91_CLASSIFY_MODEL_FAILURE"]["exhausted"] == R.TERMINAL
    # The unit loop only closes back to D05 through acceptance, never directly.
    assert R.GUARD_DESTINATIONS["D23_CHECKPOINT_ACCEPTED_UNIT"]["checkpoint_correlated"] == (
        "D05_SELECT_NEXT_UNIT"
    )


# ================================== TEST 4: models hold no acceptance/route authority


def test_no_model_node_has_an_edge_to_an_authority_node(compiled):
    edges = {
        (source, target)
        for source, target, _ in G.compiled_topology(compiled)["edges"]
    }
    for source, target in edges:
        if source in mn.MODEL_NODE_IDS:
            assert target not in AUTHORITY_NODES, f"model edge {source} -> {target}"

    for job_id, destination in R.MODEL_RESULT_DESTINATIONS.items():
        assert job_id in mn.MODEL_NODE_IDS
        assert destination not in AUTHORITY_NODES, (job_id, destination)

    # M01's two supersteps are the remaining model successors.
    assert R.route_m01_research({"source_discoveries": {"k": {}}}) == (
        "D06B_RETRIEVE_SOURCE_CANDIDATES"
    )
    assert R.route_m01_research({"source_interpretations": {"k": {}}}) == (
        "D07_CORRELATE_AND_ADMIT_SOURCES"
    )
    for destination in ("D06B_RETRIEVE_SOURCE_CANDIDATES", "D07_CORRELATE_AND_ADMIT_SOURCES"):
        assert destination not in AUTHORITY_NODES


def test_a_model_node_holds_no_acceptance_reduction_or_terminal_channel_authority():
    """Where the authority actually lives: the channels a model may write.

    `M05 -> D16` is a legal edge precisely because M05 cannot write the reduction
    result, the accepted receipt, any artifact head, or the terminal — D16
    recomputes the denominator from evidence it does not control.
    """

    forbidden = {
        "artifact_heads",
        "accepted_unit_receipts",
        "accepted_unit_checkpoint_receipts",
        "deterministic_checks",
        "workbook_head",
        "final_release_audits",
        "cursor",
        "resume_frontier",
        "terminal",
        "terminal_history",
        "terminal_candidate",
    }
    assert mn.MODEL_NODE_WRITABLE_FIELDS & forbidden == set()
    assert forbidden <= set(FACTORY_STATE_FIELDS)
    assert mn.FORBIDDEN_MODEL_NODE_FIELDS & mn.MODEL_NODE_WRITABLE_FIELDS == set()

    # The reducers that consume a review are deterministic nodes, and their
    # destinations are decided by the code-owned table, not by the review body.
    assert R.GUARD_DESTINATIONS["D16_REDUCE_UNIT_EVIDENCE"] == {
        "unit_denominator_passed": "D22_ACCEPT_UNIT",
        "unit_findings_repairable": "D17_CLASSIFY_UNIT_FINDINGS",
    }
    assert R.GUARD_DESTINATIONS["D28_REDUCE_WORKBOOK_EVIDENCE"] == {
        "workbook_denominator_passed": "D32_RECOMPUTE_FINAL_RELEASE",
        "workbook_findings_repairable": "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR",
    }


def test_routing_never_lets_a_model_result_name_its_own_destination():
    """A guard reads code-owned tables and result *presence*, never a model body."""

    tree = ast.parse(ROUTING_PY.read_text(encoding="utf-8"))
    model_result_guards = {
        "_route_model_result",
        "route_m01_research",
        "route_m02_domain",
        "route_m03_content",
        "route_m04_visual",
        "route_m05_unit_review",
        "route_m06_unit_repair",
        "route_m07_workbook_review",
        "route_m08_workbook_repair",
    }
    # The only model-written channels a guard may touch, and only to test that a
    # result set exists — never to read a value out of a model's output body.
    allowed_reads = {"source_discoveries", "source_interpretations"}
    seen = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name not in model_result_guards:
            continue
        seen.add(node.name)
        body = list(node.body)
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            body = body[1:]  # the docstring is prose, not behavior
        for statement in body:
            for inner in ast.walk(statement):
                if not (isinstance(inner, ast.Constant) and isinstance(inner.value, str)):
                    continue
                value = inner.value
                if value in allowed_reads:
                    continue
                assert value not in mn.MODEL_NODE_WRITABLE_FIELDS, (
                    f"{node.name} reads model-written channel {value!r}"
                )
                assert value in R.MODEL_RESULT_DESTINATIONS.values() or value in (
                    set(R.MODEL_RESULT_DESTINATIONS)
                    | {"D06B_RETRIEVE_SOURCE_CANDIDATES", "D07_CORRELATE_AND_ADMIT_SOURCES"}
                ) or "no result set exists" in value, (
                    f"{node.name} names non-destination string {value!r}"
                )
    assert seen == model_result_guards


def test_a_stored_frontier_may_not_name_a_model_node():
    state = {
        "pending_guard": {
            "node": "D92_REENTER_VALIDATED_FRONTIER",
            "value": "deterministic_reentry",
            "detail": {"destination": "M03_WRITE_UNIT_CONTENT"},
        }
    }
    with pytest.raises(R.RoutingViolation, match="is a model node"):
        R.route_frontier_reentry(state)


# ========================================== TEST 5: Send follows worker->barrier only


def test_every_registered_fanout_has_the_worker_to_barrier_shape(compiled):
    """Every compiled fan-out is worker->barrier, the only shape spec 10 allows.

    One `Send` per staged worker projection, all naming a single worker node, and
    the worker's only forward destination is the deterministic node that owns the
    denominator — never a second fan-out and never an authority node. This is the
    same property the guard-level tests below prove in isolation, asserted here
    against the graph that actually compiled.

    A model fan-out reaches its worker through D90, so the compiled shape is
    dispatcher -> D90 -> worker -> barrier: spec 6.2 requires the attempt counter
    committed before dispatch, and every adapter refuses an unreserved packet.
    """

    declared = {
        (source, value): dispatch
        for source, row in R.FANOUT_GUARDS.items()
        for value, dispatch in row.items()
    }
    assert set(FANOUT_SHAPES) == set(declared), (
        "a fan-out guard was registered or removed without updating the shape "
        "table this test checks it against"
    )

    edges = {(source, target) for source, target, _ in G.compiled_topology(compiled)["edges"]}
    for (source, value), (dispatch_guard, worker, barrier) in sorted(FANOUT_SHAPES.items()):
        dispatch = declared[(source, value)]
        assert dispatch not in mn.MODEL_NODE_IDS, (
            f"{source} dispatches straight to model node {dispatch} with no reservation"
        )
        assert (source, dispatch) in edges, f"{source} has no compiled edge to {dispatch}"
        if dispatch == R.ATTEMPT_RESERVATION:
            assert (dispatch, worker) in edges, f"D90 has no compiled edge to worker {worker}"
        else:
            assert dispatch == worker
        assert (worker, barrier) in edges, f"worker {worker} has no compiled edge to {barrier}"
        assert barrier not in mn.MODEL_NODE_IDS, f"{barrier} is a model node, not a barrier"

        projections = [{"key": f"{source}/{index}"} for index in range(3)]
        packet = {"dispatch": worker, "packets": projections}
        routed = dispatch_guard(
            {"pending_guard": {"node": source, "value": value, "detail": {}},
             "pending_packet": packet}
        )
        if dispatch == R.ATTEMPT_RESERVATION:
            assert routed == R.ATTEMPT_RESERVATION

        emitting, guard_node, guard_value = _send_emitting_guard(source, value)
        sends = emitting(
            {
                "pending_guard": {"node": guard_node, "value": guard_value, "detail": {}},
                "pending_packet": packet,
            }
        )
        assert [type(item) for item in sends] == [Send, Send, Send]
        assert {item.node for item in sends} == {worker}
        assert [item.arg for item in sends] == projections

    # A worker's forward successors are exactly the barriers declared for it, so
    # a fanned-out worker rejoins a denominator and fans out no further. D91 is
    # excluded with the other non-forward edges: a model worker's failure edge is
    # a recovery edge, not a second barrier.
    barriers: dict[str, set[str]] = {}
    for _guard, worker, barrier in FANOUT_SHAPES.values():
        barriers.setdefault(worker, set()).add(barrier)
    for worker, expected in sorted(barriers.items()):
        successors = {target for source, target in edges if source == worker} - {
            R.INTERRUPT_GATE,
            R.TERMINAL,
            R.MODEL_FAILURE_CLASSIFIER,
            END,
        }
        assert successors == expected, (worker, sorted(successors), sorted(expected))


def test_no_compiled_edge_enters_a_model_node_except_from_d90(compiled):
    """Spec 6.2 D90: the attempt counter is committed *before* dispatch.

    The counter cannot be minted by the dispatching node (it would be committed
    in the same superstep as the dispatch) nor invented at routing time, so the
    only compiled predecessor a model worker may have is D90. Every N23 adapter
    enforces the same rule from the other side by raising `AttemptNotReserved`.
    """

    for node_id, row in R.GUARD_DESTINATIONS.items():
        for value, destination in row.items():
            assert destination not in mn.MODEL_NODE_IDS, (
                f"{node_id}.{value} routes to {destination} with no reservation"
            )

    edges = {(source, target) for source, target, _ in G.compiled_topology(compiled)["edges"]}
    entered = {target for _source, target in edges if target in mn.MODEL_NODE_IDS}
    assert entered, "no model node is wired, so this would pass vacuously"
    for worker in sorted(entered):
        predecessors = {source for source, target in edges if target == worker}
        assert predecessors == {R.ATTEMPT_RESERVATION}, (worker, sorted(predecessors))


def test_a_fanout_guard_emits_one_send_per_staged_worker_projection():
    packet = {
        "dispatch": "M04_CREATE_UNIT_VISUALS",
        "briefs": [{"key": "u1/visual/a"}, {"key": "u1/visual/b"}],
    }
    # The dispatcher hands the staged map to D90 rather than to the worker: no
    # `Send` may be emitted before the attempt counter is committed (spec 6.2).
    assert R.route_visual_barrier(
        {
            "pending_guard": {
                "node": "D12_VISUAL_BARRIER_AND_JOIN",
                "value": "model_visual_fanout",
                "detail": {},
            },
            "pending_packet": packet,
        }
    ) == R.ATTEMPT_RESERVATION

    sends = R.route_attempt_reservation(
        {
            "pending_guard": {
                "node": R.ATTEMPT_RESERVATION,
                "value": "authorized",
                "detail": {"job_id": "M04_CREATE_UNIT_VISUALS"},
            },
            "pending_packet": packet,
        }
    )
    assert [type(item) for item in sends] == [Send, Send]
    assert {item.node for item in sends} == {"M04_CREATE_UNIT_VISUALS"}
    assert [item.arg["key"] for item in sends] == ["u1/visual/a", "u1/visual/b"]
    # Worker -> barrier: the worker's declared return destination is the barrier
    # that owns the denominator, which is a normal edge, not another Send.
    assert R.MODEL_RESULT_DESTINATIONS["M04_CREATE_UNIT_VISUALS"] == (
        "D12_VISUAL_BARRIER_AND_JOIN"
    )


def test_a_fanout_guard_refuses_an_unstaged_or_mixed_dispatch():
    base = {
        "pending_guard": {
            "node": R.ATTEMPT_RESERVATION,
            "value": "authorized",
            "detail": {"job_id": "M04_CREATE_UNIT_VISUALS"},
        }
    }
    with pytest.raises(R.RoutingViolation, match="no staged"):
        R.route_attempt_reservation(dict(base))
    with pytest.raises(R.RoutingViolation, match="no dispatch destination"):
        R.route_attempt_reservation({**base, "pending_packet": {"briefs": [{"key": "a"}]}})
    with pytest.raises(R.RoutingViolation, match="no non-empty worker projection"):
        R.route_attempt_reservation(
            {**base, "pending_packet": {"dispatch": "M04_CREATE_UNIT_VISUALS", "briefs": []}}
        )


# ============================= TEST 6: arbitrary manifest lengths and empty subsets


def test_no_curriculum_specific_manifest_length_or_order_is_hardcoded():
    for path in (GRAPH_PY, ROUTING_PY):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                assert not re.match(r"^(U|L)\d{2,}", node.value), (
                    f"{path.name} names curriculum unit {node.value!r}"
                )
        for forbidden in (
            "unit_count",
            "UNIT_COUNT",
            "MANIFEST_LENGTH",
            "manifest_length",
            "expected_units",
        ):
            assert forbidden not in source, f"{path.name} hardcodes {forbidden!r}"
        # No node is created per known unit: registration reads only the frozen
        # catalogue, never a manifest.
        assert "manifest" not in source.replace("manifest_path", "").replace(
            "manifest coverage", ""
        ).replace("MANIFEST_COVERAGE", "").lower() or "for unit" not in source


def test_the_builder_registers_a_fixed_node_set_independent_of_any_manifest(compiled):
    # P-N20-001: subset, not equality, for the same reason as the catalogue test
    # above — a downstream node's legitimate widening of the compiled graph
    # beyond `binding_inventory()` must not falsify this fixture.
    drawn = set(compiled.get_graph().nodes) - {START, END}
    skeleton_required = set(G._skeleton_required_nodes()) | set(G.binding_inventory())
    assert skeleton_required <= drawn
    assert not [node for node in drawn if re.search(r"(unit|lesson)_\d", node.lower())]


def test_an_empty_deterministic_visual_subset_routes_straight_to_the_barrier():
    state = {
        "pending_guard": {
            "node": "D10_COMPILE_VISUAL_BRIEFS",
            "value": "no_deterministic_visuals",
            "detail": {},
        }
    }
    assert R.route_visual_briefs(state) == "D12_VISUAL_BARRIER_AND_JOIN"


def test_an_exhausted_manifest_routes_to_coverage_proof_at_any_length():
    state = {
        "pending_guard": {
            "node": "D05_SELECT_NEXT_UNIT",
            "value": "manifest_exhausted",
            "detail": {},
        }
    }
    assert R.route_unit_selection(state) == "D24_PROVE_EXACT_MANIFEST_COVERAGE"


# ================================================ TEST 7: digest stability and drift


def test_identical_real_bindings_yield_an_identical_digest(output_root):
    first = G.build_curriculum_factory_graph(engine_root=REPO_ROOT, output_root=output_root)
    second = G.build_curriculum_factory_graph(engine_root=REPO_ROOT, output_root=output_root)
    assert first is not second
    assert G.graph_digest(first) == G.graph_digest(second)
    assert len(G.graph_digest(first)) == 64


def test_a_changed_callable_changes_the_digest(compiled, monkeypatch):
    baseline = G.graph_digest(compiled)
    drifted = G.binding_inventory()
    drifted["D05_SELECT_NEXT_UNIT"] = drifted["D13_RENDER_UNIT"]
    monkeypatch.setattr(G, "binding_inventory", lambda: drifted)
    assert G.graph_digest(compiled) != baseline


def test_a_changed_state_schema_changes_the_digest(compiled, monkeypatch):
    baseline = G.graph_digest(compiled)
    reducers = dict(G.FIELD_REDUCER_CLASSES)
    reducers["cursor"] = "append_unique"
    monkeypatch.setattr(G, "FIELD_REDUCER_CLASSES", reducers)
    assert G.graph_digest(compiled) != baseline


def test_a_changed_prompt_or_schema_file_changes_the_digest(compiled, monkeypatch, tmp_path):
    baseline = G.graph_digest(compiled)
    real = tp.resolve_prompt_path(tp.resolve_route("M03_WRITE_UNIT_CONTENT"))
    drifted = tmp_path / real.name
    drifted.write_bytes(real.read_bytes() + b"\n# drift\n")
    assert hashlib.sha256(drifted.read_bytes()).hexdigest() != (
        hashlib.sha256(real.read_bytes()).hexdigest()
    )

    original = tp.resolve_prompt_path

    def patched(route):
        path = original(route)
        return drifted if path.name == real.name else path

    monkeypatch.setattr(G.tp, "resolve_prompt_path", patched)
    assert G.graph_digest(compiled) != baseline


def test_the_digest_ignores_python_object_identity(compiled):
    payload_one = G.compiled_topology(compiled)
    payload_two = G.compiled_topology(compiled)
    assert payload_one == payload_two
    assert G._canonical_digest(payload_one) == G._canonical_digest(payload_two)


# ============================================ TEST 8: no handwritten fallback controller


def test_production_graph_imports_contain_no_fallback_controller():
    tree = ast.parse(GRAPH_PY.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
            imported.update(f"{node.module or ''}.{alias.name}" for alias in node.names)

    for forbidden in (
        "runtime.curriculum_factory_graph",
        "curriculum_factory_graph",
        "CurriculumFactoryGraph",
        "runtime.session_bridge",
    ):
        assert not any(forbidden in name for name in imported), forbidden

    source = GRAPH_PY.read_text(encoding="utf-8")
    for forbidden in ("CurriculumFactoryGraph", "test_simulated", "fallback_controller"):
        assert forbidden not in source, f"graph.py references {forbidden!r}"

    # The forbidden model-invocation dependencies stay out of the production path.
    for forbidden in (
        "langchain",
        "langchain_openai",
        "langchain_google_genai",
        "openai",
        "google.generativeai",
    ):
        assert not any(
            name == forbidden or name.startswith(f"{forbidden}.") for name in imported
        ), forbidden


def test_only_one_builder_and_one_compile_call_exist():
    tree = ast.parse(GRAPH_PY.read_text(encoding="utf-8"))
    builders = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("build_")
        and "graph" in node.name
    ]
    assert builders == ["build_curriculum_factory_graph"]

    compiles = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "compile"
    ]
    assert len(compiles) == 1


# ================================================== boundary and context behaviour


def test_the_node_boundary_injects_the_runtime_context_langgraph_would_not():
    """LangGraph passes `Runtime`, never the opened services.

    N22/N23 bodies take the context as an explicit second argument, so without
    this boundary every node would silently run with `runtime_context=None`.
    """

    seen = {}

    def body(state, context):
        seen["context"] = context
        return {"pending_guard": {"node": "X", "value": "ok"}}

    bound = G._boundary("X", body, model_node=False)

    class FakeRuntime:
        context = "the-context"

    assert bound({}, FakeRuntime()) == {"pending_guard": {"node": "X", "value": "ok"}}
    assert seen["context"] == "the-context"


def test_the_node_boundary_classifies_an_unexpected_exception_as_a_system_failure():
    def body(state, context):
        raise ValueError("unexpected")

    bound = G._boundary("X", body, model_node=False)

    class FakeRuntime:
        context = None

    update = bound({}, FakeRuntime())
    assert update["pending_failure"]["class"] == "system"
    assert update["pending_failure"]["cause"] == "unhandled"
    assert update["pending_guard"] is None
    assert R.decide("X", update) == R.TERMINAL


def test_a_graceful_signal_at_the_boundary_routes_through_the_interrupt_gate():
    class Token:
        def is_set(self):
            return True

    class FakeRuntime:
        class context:
            signal_token = Token()

    def body(state, context):
        return {"pending_guard": {"node": "D01_VALIDATE_AND_FREEZE_INPUTS", "value": "inputs_frozen"}}

    update = G._boundary("D01_VALIDATE_AND_FREEZE_INPUTS", body, model_node=False)({}, FakeRuntime())
    assert update["pending_guard"]["interrupt_requested"] is True
    assert R.route_frozen_inputs(update) == R.INTERRUPT_GATE


def test_a_classified_failure_outranks_a_graceful_interrupt():
    state = {
        "pending_failure": {"class": "system", "cause": "integrity"},
        "pending_guard": {"node": "D01", "value": None, "interrupt_requested": True},
    }
    assert R.route_frozen_inputs(state) == R.TERMINAL


def test_an_undeclared_guard_value_raises_rather_than_routing():
    state = {"pending_guard": {"node": "D05_SELECT_NEXT_UNIT", "value": "invented"}}
    with pytest.raises(R.RoutingViolation, match="undeclared guard value"):
        R.route_unit_selection(state)


def test_every_declared_guard_value_of_every_owned_node_has_a_destination():
    R.assert_guard_table_total(NODE_CATALOGUE)
    for node_id, spec in NODE_CATALOGUE.items():
        for value in spec.guards:
            if (node_id, value) in R.NORMAL_EDGE_GUARDS:
                continue
            assert (
                value in R.GUARD_DESTINATIONS.get(node_id, {})
                or value in R.DYNAMIC_GUARDS.get(node_id, {})
                or value in R.FANOUT_GUARDS.get(node_id, {})
            ), (node_id, value)


def test_the_runtime_context_factory_holds_no_model_client_or_routing_authority(tmp_path):
    context = G.build_runtime_context(
        engine_root=REPO_ROOT,
        output_root=tmp_path,
        run_id="run-topology",
        curriculum_digest="0" * 64,
    )
    assert isinstance(context, RuntimeContext)
    for forbidden in ("model_client", "llm", "router", "routing_authority", "state"):
        assert not hasattr(context, forbidden)
    assert isinstance(context.transport_registry, tp.CliTransport)
    assert not isinstance(context.transport_registry, tp.FakeCliTransport)
    assert callable(context.clock)
