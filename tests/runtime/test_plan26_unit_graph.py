"""Plan 26 per-unit path gate (spec sections 8.1, 8.2, 10, 11.3-11.4): N30's wiring.

Every topology assertion runs against the one real `CompiledStateGraph` that
`graph.build_curriculum_factory_graph` produces from the real N22/N23 callables,
and every denominator assertion runs the real node body and the real guard. A
mock would prove that a stand-in joins correctly, which is the one thing this
file exists to rule out.

This node is **BLOCKED**, and the file is written to say so precisely rather
than to look green. Two kinds of test live here:

- assertions about the unit topology that is genuinely registered now, and
- explicitly named `test_blocked_*` guards that assert the *current, broken*
  behaviour of a dependency outside this node's write set.

Each blocked guard names its owner and the exact rework that inverts it, and
`test_every_blocking_gap_is_declared_with_an_owner` keeps that list total, so a
gap cannot be quietly forgotten once it is fixed: the guard fails the moment the
rework lands, which is what forces this file to be revisited.

Skips only where the hash-locked environment is absent; the node's evidence was
produced by running this file inside it.
"""

import ast
import hashlib
import random
import re
import tempfile
import unittest
from pathlib import Path
from typing import Any

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
import yaml
from langgraph.channels.binop import BinaryOperatorAggregate
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from typing_extensions import Annotated, TypedDict

from runtime.langgraph_factory import graph as G
from runtime.langgraph_factory import model_nodes as mn
from runtime.langgraph_factory import routing as R
from runtime.langgraph_factory import unit_graph as U
from runtime.langgraph_factory.nodes import NODE_CATALOGUE, inputs, sources, visuals
from runtime.langgraph_factory.reducers import WriteOnceConflict, write_once
from runtime.langgraph_factory.state import (
    FACTORY_STATE_FIELDS,
    FIELD_REDUCER_CLASSES,
    FactoryState,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
UNIT_GRAPH_PY = REPO_ROOT / "runtime" / "langgraph_factory" / "unit_graph.py"

MODEL_NODE_IDS = frozenset(mn.MODEL_NODE_ADAPTERS)


# ---------------------------------------------------------------------------
# fixtures — one real compiled graph, shared
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def compiled() -> Any:
    output_root = Path(tempfile.mkdtemp(prefix="plan26-n30-"))
    return G.build_curriculum_factory_graph(engine_root=REPO_ROOT, output_root=output_root)


@pytest.fixture(scope="module")
def topology(compiled: Any) -> dict[str, Any]:
    return G.compiled_topology(compiled)


@pytest.fixture(scope="module")
def available() -> tuple[str, ...]:
    return tuple(sorted(G.binding_inventory()))


class _Token:
    def is_set(self) -> bool:
        return False


class _Context:
    """The narrow service surface a deterministic node body reaches."""

    def __init__(self, **services: Any) -> None:
        self.engine_root = services.pop("engine_root", Path("/tmp"))
        self.output_root = services.pop("output_root", Path("/tmp/out"))
        self.path_guard = object()
        self.evidence_service = object()
        self.transport_registry = services.pop("transport_registry", object())
        self.source_retriever = services.pop("source_retriever", None)
        self.signal_token = services.pop("signal_token", _Token())
        self.clock = services.pop("clock", lambda: "2026-01-01T00:00:00Z")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _synthetic_manifest(
    tmp_path: Path,
    unit_count: int,
    edges: dict[int, list[int]] | None = None,
    *,
    shuffle_seed: int | None = None,
) -> tuple[Path, list[str]]:
    """A manifest of generically-named units over a chosen prerequisite DAG."""

    unit_ids = [f"U{index:03d}" for index in range(1, unit_count + 1)]
    units = []
    for index, unit_id in enumerate(unit_ids, start=1):
        prerequisites = [unit_ids[target - 1] for target in (edges or {}).get(index, [])]
        units.append(
            {
                "id": unit_id,
                "title": f"synthetic unit {index}",
                "sequence": {"prerequisites": prerequisites, "prepares_for": []},
                "required_explanation": [f"fact {index}"],
            }
        )
    if shuffle_seed is not None:
        random.Random(shuffle_seed).shuffle(units)
    curriculum_root = tmp_path / "curricula" / "synthetic"
    curriculum_root.mkdir(parents=True, exist_ok=True)
    path = curriculum_root / "synthetic_curriculum.v1.yaml"
    path.write_text(yaml.safe_dump({"labs": units}, sort_keys=False), encoding="utf-8")
    return path, [unit["id"] for unit in units]


def _d02_state(manifest_path: Path, mode: str, requested: str | None) -> dict[str, Any]:
    return {
        "engine_root": str(manifest_path.parents[2]),
        "curriculum_root": str(manifest_path.parent),
        "active_manifest_path": str(manifest_path),
        "mode": mode,
        "requested_unit_id": requested,
        "frozen_inputs": [
            {
                "path": str(manifest_path),
                "sha256": _sha256_file(manifest_path),
                "role": "active_manifest",
            }
        ],
    }


def _visual_state(
    unit_id: str,
    briefs: list[dict[str, Any]],
    results: dict[str, dict[str, Any]],
    *,
    content_hash: str = "content-hash-1",
) -> dict[str, Any]:
    """A D12 projection over one frozen visual denominator."""

    deterministic = sorted(b["key"] for b in briefs if b["subset"] == "deterministic")
    model = sorted(b["key"] for b in briefs if b["subset"] == "model")
    return {
        "selected_unit_id": unit_id,
        "visual_briefs": briefs,
        "visual_denominators": {
            f"{unit_id}/{content_hash}": {
                "unit_id": unit_id,
                "content_hash": content_hash,
                "deterministic_keys": deterministic,
                "model_keys": model,
                "size": len(briefs),
            }
        },
        "visual_results": results,
        "artifact_versions": [],
        "artifact_heads": {
            f"units/{unit_id}/content": {"version": 1, "parent_hash": None, "hash": content_hash}
        },
    }


def _brief(unit_id: str, role: str, subset: str, content_hash: str = "content-hash-1") -> dict[str, Any]:
    return {
        "key": f"{unit_id}/visual/{role}",
        "unit_id": unit_id,
        "role": role,
        "kind": "schematic" if subset == "deterministic" else "illustration",
        "subset": subset,
        "content_hash": content_hash,
        "domain_hash": "domain-hash-1",
        "permitted_facts": [],
    }


def _visual_result(key: str, unit_id: str, subset: str, content_hash: str = "content-hash-1") -> dict[str, Any]:
    return {
        "key": key,
        "unit_id": unit_id,
        "subset": subset,
        "provenance": "deterministic_renderer" if subset == "deterministic" else "model_candidate",
        "content_hash": content_hash,
        "domain_hash": "domain-hash-1",
        "asset_path": f"/tmp/{key}.svg",
        "sha256": hashlib.sha256(key.encode()).hexdigest(),
        "format": "svg",
    }


# ---------------------------------------------------------------------------
# Registered unit topology (spec 8.1 / 8.2)
# ---------------------------------------------------------------------------


def test_the_compiled_graph_registers_every_declared_unit_branch(topology, available) -> None:
    """Each conditional edge exists with exactly the destinations that exist."""

    registered: dict[str, set[str]] = {}
    for source, target, conditional in topology["edges"]:
        if conditional:
            registered.setdefault(source, set()).add(target)

    for source, _guard in U.UNIT_BRANCHES:
        expected = set(U.branch_destinations(source, available))
        assert expected, f"{source} has no registerable destination"
        assert registered.get(source) == expected, source


def test_the_two_map_reduce_return_edges_are_normal_edges(topology) -> None:
    """Spec 8.2 names these exactly: `add_edge(worker, barrier)`, not a branch.

    Registering the worker's return conditionally would let the worker's own
    result decide where the map/reduce goes, which is the barrier's authority.
    """

    normal = {(source, target) for source, target, conditional in topology["edges"] if not conditional}
    for edge in U.UNIT_NORMAL_EDGES:
        assert edge in normal, edge
    assert ("D11_CREATE_DETERMINISTIC_VISUALS", "D12_VISUAL_BARRIER_AND_JOIN") in normal
    assert ("M04_CREATE_UNIT_VISUALS", "D12_VISUAL_BARRIER_AND_JOIN") in normal


def test_the_unit_path_creates_no_second_graph_and_compiles_nothing() -> None:
    """N30 is additive registration over N20's one builder."""

    source = UNIT_GRAPH_PY.read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = [
        node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    ]
    assert "StateGraph" not in calls
    assert "compile" not in calls
    assert "add_node" not in calls


def test_a_node_body_authored_in_the_unit_path_module_is_refused() -> None:
    """The D90/D91 gap cannot be closed by writing a wrapper in this module.

    N20's `validate_bindings` restricts a production binding to the two owned
    node modules, so a callable authored here is rejected by stable ID. This is
    why blocking gap `plan26/n30/d90-d91-not-registrable` is owed to N23 and
    cannot be absorbed as coordination.
    """

    def D90_RESERVE_MODEL_ATTEMPT(state: Any, context: Any) -> dict[str, Any]:
        return {}

    D90_RESERVE_MODEL_ATTEMPT.__module__ = "runtime.langgraph_factory.unit_graph"
    bindings = dict(G.binding_inventory())
    bindings["D90_RESERVE_MODEL_ATTEMPT"] = D90_RESERVE_MODEL_ATTEMPT

    with pytest.raises(G.GraphBindingError) as error:
        G.validate_bindings(bindings, required=("D90_RESERVE_MODEL_ATTEMPT",))
    assert "N20-BIND-PLACEHOLDER" in str(error.value)


def test_deferred_edges_are_exactly_the_destinations_with_no_node_body(available) -> None:
    """Silence about an unwireable edge is how a topology gap becomes a halt."""

    observed: set[tuple[str, str]] = set()
    for source, _guard in U.UNIT_BRANCHES:
        for destination in U.deferred_destinations(source, available):
            observed.add((source, destination))
    declared = {(source, destination) for source, _value, destination, _owner in U.DEFERRED_EDGES}
    assert observed == declared


def test_every_deferred_edge_names_a_real_owning_graph_node() -> None:
    owners = {owner for _s, _v, _d, owner in U.DEFERRED_EDGES}
    assert owners <= {"N23_MODEL_NODES", "N31_REPAIR_ACCEPTANCE", "N32_WORKBOOK_TERMINALS"}
    for _source, value, destination, owner in U.DEFERRED_EDGES:
        assert value and destination and owner


def test_registering_an_undeclared_deferred_destination_fails(monkeypatch, available) -> None:
    """A future unwireable destination must be declared, not silently dropped."""

    monkeypatch.setattr(U, "DEFERRED_EDGES", U.DEFERRED_EDGES[1:])

    class _Builder:
        def add_edge(self, *args: Any) -> None:
            pass

        def add_conditional_edges(self, *args: Any) -> None:
            pass

    with pytest.raises(U.UnitTopologyError) as error:
        U.register_unit_path(_Builder(), available)
    assert "N30-EDGE-UNDECLARED" in str(error.value)


def test_no_model_node_can_be_a_resume_reentry_destination(topology) -> None:
    """Spec 6.2 D92: a model node as stored destination is a system failure."""

    assert not set(U.RESUME_REENTRY_DESTINATIONS) & MODEL_NODE_IDS
    reentry = {
        target
        for source, target, conditional in topology["edges"]
        if source == "D92_REENTER_VALIDATED_FRONTIER" and conditional
    }
    assert not reentry & MODEL_NODE_IDS
    assert set(U.RESUME_REENTRY_DESTINATIONS) <= reentry


def test_a_stored_model_frontier_is_refused_by_the_reentry_guard() -> None:
    state = {
        "pending_guard": {
            "node": "D92_REENTER_VALIDATED_FRONTIER",
            "value": "deterministic_reentry",
            "detail": {"destination": "M03_WRITE_UNIT_CONTENT"},
        }
    }
    with pytest.raises(R.RoutingViolation):
        R.route_frontier_reentry(state)


def test_the_unit_path_names_no_unit_id_and_no_manifest_length() -> None:
    """Spec 8.2: the builder never creates a node per known unit."""

    source = UNIT_GRAPH_PY.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            assert node.value in (0, 1), f"manifest-length-looking constant {node.value}"
    assert "U001" not in source


# ---------------------------------------------------------------------------
# Fan-outs, denominators, joins (spec section 10)
# ---------------------------------------------------------------------------


def test_a_visual_fanout_dispatches_one_send_per_staged_denominator_member() -> None:
    """The guard translates staged material one-for-one; it invents no member."""

    unit_id = "U001"
    briefs = [
        _brief(unit_id, "det-a", "deterministic"),
        _brief(unit_id, "mdl-a", "model"),
        _brief(unit_id, "mdl-b", "model"),
    ]
    results = {
        f"{unit_id}/visual/det-a": _visual_result(f"{unit_id}/visual/det-a", unit_id, "deterministic")
    }
    state = _visual_state(unit_id, briefs, results)
    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(state, _Context())

    assert update["pending_guard"]["value"] == "model_visual_fanout"
    packet = update["pending_packet"]
    assert packet["dispatch"] == "M04_CREATE_UNIT_VISUALS"
    assert len(packet["briefs"]) == 2

    dispatch = R.route_visual_barrier({**state, **update})
    assert isinstance(dispatch, list) and len(dispatch) == 2
    assert all(isinstance(send, Send) for send in dispatch)
    assert {send.node for send in dispatch} == {"M04_CREATE_UNIT_VISUALS"}


def test_a_fanout_with_no_staged_packet_refuses_to_improvise_one() -> None:
    """Spec 10: the denominator is persisted before dispatch, not at routing time."""

    state = {
        "pending_guard": {
            "node": "D12_VISUAL_BARRIER_AND_JOIN",
            "value": "model_visual_fanout",
            "detail": {},
        }
    }
    with pytest.raises(R.RoutingViolation):
        R.route_visual_barrier(state)


def test_an_empty_deterministic_visual_subset_routes_straight_to_the_barrier() -> None:
    """Spec 8.2: empty subsets route directly through D12; no sentinel member."""

    unit_id = "U001"
    content_hash = "content-hash-1"
    state = {
        "selected_unit_id": unit_id,
        "artifact_heads": {
            f"units/{unit_id}/content": {"version": 1, "parent_hash": None, "hash": content_hash},
            f"units/{unit_id}/domain": {"version": 1, "parent_hash": None, "hash": "domain-hash-1"},
        },
        "artifact_versions": [
            {
                "stream": f"units/{unit_id}/content",
                "version": 1,
                "parent_hash": None,
                "hash": content_hash,
                "body": {"visuals": [{"role": "mdl-a", "kind": "illustration"}]},
            }
        ],
        "engine_root": "/tmp",
    }
    update = visuals.D10_COMPILE_VISUAL_BRIEFS(state, _Context())
    assert update["pending_guard"]["value"] == "no_deterministic_visuals"
    assert R.route_visual_briefs({**state, **update}) == "D12_VISUAL_BARRIER_AND_JOIN"


@pytest.mark.parametrize(
    "mutation",
    ["missing", "extra", "stale_parent", "cross_unit"],
)
def test_the_visual_join_refuses_a_denominator_that_is_not_exact(mutation: str) -> None:
    """Spec 10: missing, extra, stale-parent and cross-unit members fail the join."""

    unit_id = "U001"
    briefs = [_brief(unit_id, "det-a", "deterministic"), _brief(unit_id, "det-b", "deterministic")]
    key_a, key_b = f"{unit_id}/visual/det-a", f"{unit_id}/visual/det-b"
    results = {
        key_a: _visual_result(key_a, unit_id, "deterministic"),
        key_b: _visual_result(key_b, unit_id, "deterministic"),
    }
    if mutation == "missing":
        results.pop(key_b)
    elif mutation == "extra":
        extra = f"{unit_id}/visual/det-z"
        results[extra] = _visual_result(extra, unit_id, "deterministic")
    elif mutation == "stale_parent":
        results[key_b] = {**results[key_b], "content_hash": "superseded-content-hash"}
    elif mutation == "cross_unit":
        results[key_b] = {**results[key_b], "unit_id": "U999"}

    state = _visual_state(unit_id, briefs, results)
    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(state, _Context())
    failure = update["pending_failure"]
    assert failure["class"] == "system"
    assert failure["cause"] in ("join", "integrity")
    assert "artifact_heads" not in update


@pytest.mark.parametrize(
    "mutation",
    ["missing", "extra", "stale", "cross_unit"],
)
def test_the_source_join_refuses_a_denominator_that_is_not_exact(mutation: str) -> None:
    """Spec 10: the source join accepts only `actual_keys == expected_keys`."""

    unit_id = "U001"
    key_a, key_b = f"{unit_id}/1/required_explanation:000", f"{unit_id}/1/safety_focus:000"
    requests = [
        {"key": key_a, "unit_id": unit_id, "required": True, "scope": "required_explanation"},
        {"key": key_b, "unit_id": unit_id, "required": True, "scope": "safety_focus"},
    ]
    retrievals = {
        key: {"key": key, "unit_id": unit_id, "sha256": f"sha-{key}", "locator": "l", "content_type": "text/html"}
        for key in (key_a, key_b)
    }
    interpretations = {
        key: {"key": key, "unit_id": unit_id, "retrieval_sha256": f"sha-{key}", "scope": "s"}
        for key in (key_a, key_b)
    }
    if mutation == "missing":
        interpretations.pop(key_b)
    elif mutation == "extra":
        rogue = f"{unit_id}/1/undeclared:000"
        interpretations[rogue] = {"key": rogue, "unit_id": unit_id, "retrieval_sha256": "x"}
    elif mutation == "stale":
        interpretations[key_b] = {**interpretations[key_b], "retrieval_sha256": "superseded"}
    elif mutation == "cross_unit":
        interpretations[key_b] = {**interpretations[key_b], "unit_id": "U999"}

    state = {
        "selected_unit_id": unit_id,
        "source_requests": requests,
        "source_denominators": {
            f"{unit_id}/1": {"unit_id": unit_id, "source_epoch": 1, "request_keys": [key_a, key_b], "size": 2}
        },
        "source_discoveries": {},
        "retrievals": retrievals,
        "source_interpretations": interpretations,
    }
    update = sources.D07_CORRELATE_AND_ADMIT_SOURCES(state, _Context())

    assert "source_admissions" not in update
    if mutation == "missing":
        # A missing required member is an unresolved prerequisite, not an admission.
        assert update["pending_guard"]["value"] == "prerequisite_unresolved"
        assert R.route_source_admission({**state, **update}) == "D30_CLASSIFY_PREREQUISITE"
    else:
        assert update["pending_failure"]["class"] == "system"
        assert update["pending_failure"]["cause"] in ("join", "integrity")


def test_a_duplicate_fanout_member_with_a_different_body_is_an_integrity_failure() -> None:
    """Spec 10: duplicate equal replay is idempotent; a different duplicate is not."""

    from runtime.langgraph_factory.reducers import UnionConflict, union_disjoint

    key = "U001/visual/det-a"
    first = {key: _visual_result(key, "U001", "deterministic")}
    assert union_disjoint(first, dict(first)) == first
    with pytest.raises(UnionConflict):
        union_disjoint(first, {key: {**first[key], "sha256": "different"}})


@pytest.mark.parametrize("unit_count", [1, 7, 41])
def test_one_mode_computes_the_complete_prerequisite_closure_in_manifest_order(
    tmp_path: Path, unit_count: int
) -> None:
    """Prompt TEST 2, over a real multi-unit DAG rather than a fixed fixture."""

    edges = {index: [index - 1] for index in range(2, unit_count + 1)}
    manifest_path, _ = _synthetic_manifest(tmp_path / str(unit_count), unit_count, edges)
    update = inputs.D02_COMPILE_EFFECTIVE_RUN(
        _d02_state(manifest_path, "one", f"U{unit_count:03d}"), _Context()
    )
    closure = update["effective_run"]["target_closure"]
    assert closure == [f"U{index:03d}" for index in range(1, unit_count + 1)]

    # D05 then consumes that closure in exactly that order.
    state = {
        "effective_run": update["effective_run"],
        "cursor": {"manifest_ordinal": 0, "accepted_ordinal": 0},
        "accepted_unit_receipts": {},
        "unit_status": {},
    }
    selection = sources.D05_SELECT_NEXT_UNIT(state, _Context())
    assert selection["selected_unit_id"] == closure[0]
    assert R.route_unit_selection({**state, **selection}) == "D06_COMPILE_SOURCE_REQUESTS"


def test_a_diamond_closure_admits_each_ancestor_exactly_once(tmp_path: Path) -> None:
    manifest_path, _ = _synthetic_manifest(tmp_path, 4, {2: [1], 3: [1], 4: [2, 3]})
    update = inputs.D02_COMPILE_EFFECTIVE_RUN(_d02_state(manifest_path, "one", "U004"), _Context())
    closure = update["effective_run"]["target_closure"]
    assert sorted(closure) == ["U001", "U002", "U003", "U004"]
    assert len(closure) == len(set(closure))


# ---------------------------------------------------------------------------
# No success terminal anywhere in this path (prompt TEST 10)
# ---------------------------------------------------------------------------


def test_no_node_in_this_path_can_emit_a_product_success_terminal() -> None:
    """A capability, intermediate artifact, review, or clean check emits nothing.

    The two product terminals (`UNIT_ACCEPTED`, `COMPLETE`) are reachable only
    from D24/D32, neither of which this path wires; every node here that can
    reach D98 does so with a failure, interrupt, or pause candidate.
    """

    product_terminals = {"UNIT_ACCEPTED", "COMPLETE"}
    for source, _guard in U.UNIT_BRANCHES:
        spec = NODE_CATALOGUE.get(source)
        if spec is None:
            continue
        module_path = REPO_ROOT / "runtime" / "langgraph_factory" / "nodes" / f"{spec.module}.py"
        body = module_path.read_text(encoding="utf-8")
        for terminal in product_terminals:
            # Word-bounded: `INCOMPLETE` is a join verdict, not a terminal kind.
            assert not re.search(rf"\b{terminal}\b", body), f"{source} names {terminal}"

    # Nothing this path wires reaches the acceptance node that mints a receipt.
    reachable = {target for _s, _v, target, _o in U.DEFERRED_EDGES}
    assert "D22_ACCEPT_UNIT" not in reachable
    assert not set(U.unit_path_nodes()) & {"D22_ACCEPT_UNIT", "D24_PROVE_EXACT_MANIFEST_COVERAGE"}


def test_the_model_path_uses_only_a_test_transport_and_no_product_output_root() -> None:
    """A fake transport is injectable only through the explicitly named builder."""

    sandbox = Path(tempfile.mkdtemp())
    context = mn.build_test_model_node_context(sandbox_root=sandbox, responses={})
    assert isinstance(context.transport, mn.tp.FakeCliTransport)
    with pytest.raises(mn.ModelNodeError):
        mn.build_model_node_context(
            type("_C", (), {"transport_registry": context.transport})()  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# BLOCKED: dependency gaps outside this node's write set
# ---------------------------------------------------------------------------


def test_every_blocking_gap_is_declared_with_an_owner_and_rework_edge() -> None:
    rework_edges = {
        "state_or_reducer",
        "deterministic_node",
        "model_node_or_projection",
        "topology_or_guard",
    }
    fingerprints = {gap["fingerprint"] for gap in U.BLOCKING_GAPS}
    assert fingerprints == {
        "plan26/n30/write-once-channel-default-conflict",
        "plan26/n30/model-packet-not-staged",
        "plan26/n30/visual-fanout-packet-not-staged",
        "plan26/n30/d90-d91-not-registrable",
    }
    for gap in U.BLOCKING_GAPS:
        assert gap["owner"].startswith("N")
        assert gap["rework_edge"] in rework_edges
        assert len(gap["detail"]) > 80


def test_blocked_a_write_once_channel_refuses_its_own_first_write() -> None:
    """`plan26/n30/write-once-channel-default-conflict` -> N11_STATE_REDUCERS.

    LangGraph initializes a `BinaryOperatorAggregate` to the annotation's empty
    value, so `write_once` sees a non-None `existing` on the first write and
    raises. No episode can complete D01, which is why no end-to-end run of this
    path exists in this node's evidence.

    Inverts when N11 either annotates the affected channels `X | None` (which
    leaves the channel unset, as the control case below proves) or teaches
    `write_once` to treat the declared empty default as absent.
    """

    class _Broken(TypedDict, total=False):
        effective_run: Annotated[dict[str, Any], write_once]

    builder: StateGraph = StateGraph(_Broken)
    builder.add_node("A", lambda state: {"effective_run": {"x": 1}})
    builder.add_edge(START, "A")
    builder.add_edge("A", END)
    with pytest.raises(WriteOnceConflict):
        builder.compile().invoke({})

    class _Control(TypedDict, total=False):
        effective_run: Annotated[dict[str, Any] | None, write_once]

    control: StateGraph = StateGraph(_Control)
    control.add_node("A", lambda state: {"effective_run": {"x": 1}})
    control.add_node("B", lambda state: {"effective_run": {"x": 1}})
    control.add_edge(START, "A")
    control.add_edge("A", "B")
    control.add_edge("B", END)
    assert control.compile().invoke({}) == {"effective_run": {"x": 1}}


def test_blocked_the_affected_write_once_channels_are_named(compiled) -> None:
    """The blast radius of the same gap, read off the real production channels."""

    # An affected channel is one LangGraph could construct an empty default for.
    # A channel annotated `X | None` is left at the MISSING sentinel instead, and
    # its first write bypasses the operator entirely.
    affected = sorted(
        field
        for field in FACTORY_STATE_FIELDS
        if FIELD_REDUCER_CLASSES[field] == "write_once"
        and isinstance(compiled.channels.get(field), BinaryOperatorAggregate)
        and isinstance(getattr(compiled.channels[field], "value", None), (str, list, dict))
    )
    assert "run_id" in affected
    assert "effective_run" in affected
    assert "mode" in affected
    assert len(affected) == 17
    assert "requested_unit_id" not in affected
    assert "resume_from" not in affected


def test_blocked_a_source_fanout_has_no_staged_packet_to_dispatch() -> None:
    """`plan26/n30/model-packet-not-staged` -> N22_DETERMINISTIC_NODES.

    D06 computes the request denominator and declares `discovery_fanout`, but
    stages no `pending_packet`, and its catalogue row does not authorize one, so
    the fan-out guard has nothing to translate. The guard raising here is the
    correct behaviour (spec 10) — the defect is upstream.

    Inverts when D06 stages one M01 discovery packet per request key.
    """

    assert "pending_packet" not in NODE_CATALOGUE["D06_COMPILE_SOURCE_REQUESTS"].outputs
    unit = {
        "id": "U001",
        "title": "t",
        "required_explanation": ["fact"],
        "safety_focus": ["care"],
    }
    state = {
        "effective_run": {"unit_records": [unit], "target_closure": ["U001"]},
        "selected_unit_id": "U001",
        "source_admissions": [],
        "engine_root": "/tmp",
    }
    update = sources.D06_COMPILE_SOURCE_REQUESTS(state, _Context())
    assert update["pending_guard"]["value"] == "discovery_fanout"
    assert "pending_packet" not in update

    with pytest.raises(R.RoutingViolation) as error:
        R.route_source_discovery_fanout({**state, **update})
    assert "no staged `pending_packet`" in str(error.value)


@pytest.mark.parametrize(
    "node_id, staging_node",
    [
        ("D06_COMPILE_SOURCE_REQUESTS", "M01 discovery"),
        ("D06B_RETRIEVE_SOURCE_CANDIDATES", "M01 interpretation"),
        ("D07_CORRELATE_AND_ADMIT_SOURCES", "M02"),
        ("D08_VALIDATE_DOMAIN", "M03"),
        ("D10_COMPILE_VISUAL_BRIEFS", "D11"),
        ("D15_FREEZE_UNIT_REVIEW_PACKET", "M05"),
    ],
)
def test_blocked_no_dispatching_node_authorizes_a_worker_packet(node_id: str, staging_node: str) -> None:
    """Same gap, stated as the frozen catalogue rows that must change."""

    assert "pending_packet" not in NODE_CATALOGUE[node_id].outputs, (
        f"{node_id} now stages a packet for {staging_node}; revisit this gap"
    )


def test_blocked_a_model_node_on_a_plain_edge_receives_no_reservation() -> None:
    """`plan26/n30/model-packet-not-staged` -> N22_DETERMINISTIC_NODES.

    A conditional edge that names a node passes the whole `FactoryState`, but
    every adapter requires a D90 reservation, a correlation, and its spec 9
    projection. Until D07/D08/D15 stage packets, D07 -> M02, D08 -> M03 and
    D15 -> M05 cannot carry a dispatch.

    Inverts when the dispatching node stages the packet and the edge becomes a
    single-member `Send`.
    """

    sandbox = Path(tempfile.mkdtemp())
    context = mn.build_test_model_node_context(sandbox_root=sandbox, responses={})
    whole_state = {field: None for field in FACTORY_STATE_FIELDS}
    whole_state.update({"run_id": "r1", "episode_id": "e1", "selected_unit_id": "U001"})

    with pytest.raises(mn.AttemptNotReserved):
        mn.MODEL_NODE_ADAPTERS["M02_CREATE_UNIT_DOMAIN_DATA"](whole_state, context)
    with pytest.raises(mn.ProjectionViolation):
        mn.MODEL_NODE_ADAPTERS["M05_REVIEW_ACTUAL_UNIT"](whole_state, context)


def test_blocked_the_staged_m04_briefs_are_not_m04_packets() -> None:
    """`plan26/n30/visual-fanout-packet-not-staged` -> N22_DETERMINISTIC_NODES.

    D12 does stage a packet, but its members are bare brief records. `Send`
    delivers each member as the worker's whole input, and M04 requires a
    `brief`/`permitted_facts`/`visual_contract` packet with a reservation and a
    correlation key.

    Inverts when D12 stages M04 packets rather than briefs.
    """

    sandbox = Path(tempfile.mkdtemp())
    context = mn.build_test_model_node_context(sandbox_root=sandbox, responses={})
    unit_id = "U001"
    briefs = [_brief(unit_id, "det-a", "deterministic"), _brief(unit_id, "mdl-a", "model")]
    key = f"{unit_id}/visual/det-a"
    state = _visual_state(unit_id, briefs, {key: _visual_result(key, unit_id, "deterministic")})
    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(state, _Context())

    member = update["pending_packet"]["briefs"][0]
    assert "brief" not in member and "reservation" not in member
    with pytest.raises(mn.ProjectionViolation):
        mn.MODEL_NODE_ADAPTERS["M04_CREATE_UNIT_VISUALS"](member, context)


def test_blocked_d90_and_d91_have_no_registrable_node_callable() -> None:
    """`plan26/n30/d90-d91-not-registrable` -> N23_MODEL_NODES.

    Both are keyword-only helpers taking arguments no `add_node` callable
    receives, so the attempt-reservation/retry cycle and every model node's
    failure edge have no destination.

    Inverts when `model_nodes` exports `(state, context) -> update` callables
    named `D90_RESERVE_MODEL_ATTEMPT` and `D91_CLASSIFY_MODEL_FAILURE`.
    """

    import inspect

    inventory = G.binding_inventory()
    assert "D90_RESERVE_MODEL_ATTEMPT" not in inventory
    assert "D91_CLASSIFY_MODEL_FAILURE" not in inventory

    for helper in (mn.reserve_model_attempt, mn.classify_model_failure):
        parameters = list(inspect.signature(helper).parameters.values())
        assert parameters[0].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        keyword_only = [p for p in parameters[1:] if p.kind is inspect.Parameter.KEYWORD_ONLY]
        required_keyword_only = [p for p in keyword_only if p.default is inspect.Parameter.empty]
        assert required_keyword_only, f"{helper.__name__} would be node-shaped"


def test_blocked_the_review_handoff_to_n31_is_declared_not_wired(available) -> None:
    """A clean D16 is N31's handoff; D16 has no body, so the edge is declared.

    This is the prompt's own frontier ("clean D16 evidence is a handoff to
    N31"), recorded as a deferred edge rather than a fabricated destination.
    """

    assert "D16_REDUCE_UNIT_EVIDENCE" not in available
    assert ("M05_REVIEW_ACTUAL_UNIT", "review_returned", "D16_REDUCE_UNIT_EVIDENCE",
            "N31_REPAIR_ACCEPTANCE") in U.DEFERRED_EDGES
    assert R.GUARD_DESTINATIONS["D16_REDUCE_UNIT_EVIDENCE"]["unit_denominator_passed"] == "D22_ACCEPT_UNIT"
