"""Per-unit topology: the D05-through-D15 loop, both `Send` map/reduces, resume re-entry.

This module is additive registration over the one `StateGraph` N20 builds in
`graph.py`. It creates no graph and calls no `compile()`: `register_unit_path`
receives the builder N20 already populated with `add_node` and adds only the
edges spec section 8.1's "normal unit path" declares.

Two things it deliberately does not do.

It registers no node body. N20's `validate_bindings` restricts a production
binding to `runtime.langgraph_factory.nodes` and `runtime.langgraph_factory
.model_nodes`, so a callable authored here could not be a node even if this
module wanted one — which is the guarantee that keeps "the graph compiled"
meaning "the graph compiled against the owned node bodies".

It invents no `Send` projection. Every fan-out edge translates the packet the
dispatching node staged (spec section 10: the denominator is immutable and
persisted before dispatch). A projection materialized at routing time would be
one no denominator committed to, so where a node stages nothing, the fan-out
guard raises rather than improvising — see `BLOCKING_GAPS`.

`DEFERRED_EDGES` is the frozen record of every guard destination this path
declares whose node body does not exist yet, with the owning graph node. The
conditional edge is still registered over the destinations that do exist, so the
interrupt and failure branches are real; a run that takes a deferred branch
fails loudly at the edge instead of silently halting.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from . import routing

__all__ = [
    "UNIT_NORMAL_EDGES",
    "UNIT_BRANCHES",
    "MODEL_BRANCH_DESTINATIONS",
    "RESUME_REENTRY_DESTINATIONS",
    "DEFERRED_EDGES",
    "BLOCKING_GAPS",
    "UnitTopologyError",
    "branch_destinations",
    "deferred_destinations",
    "unit_path_nodes",
    "register_unit_path",
]


class UnitTopologyError(RuntimeError):
    """A per-unit edge names a node the builder cannot resolve."""


# Spec 8.2's two documented map/reduce return edges. They are normal edges, not
# conditional ones: the worker returns through `union_disjoint` and the barrier —
# never the worker — decides what happens next.
UNIT_NORMAL_EDGES: tuple[tuple[str, str], ...] = (
    ("D11_CREATE_DETERMINISTIC_VISUALS", "D12_VISUAL_BARRIER_AND_JOIN"),
    ("M04_CREATE_UNIT_VISUALS", "D12_VISUAL_BARRIER_AND_JOIN"),
)

# Every conditional edge of the normal unit path, in spec 8.1 order. The guard is
# N20's; this module owns only which node it is attached to.
UNIT_BRANCHES: tuple[tuple[str, Callable[[Mapping[str, Any]], Any]], ...] = (
    ("D92_REENTER_VALIDATED_FRONTIER", routing.route_frontier_reentry),
    ("D05_SELECT_NEXT_UNIT", routing.route_unit_selection),
    ("D06_COMPILE_SOURCE_REQUESTS", routing.route_source_discovery_fanout),
    ("D06B_RETRIEVE_SOURCE_CANDIDATES", routing.route_source_interpretation_fanout),
    ("D07_CORRELATE_AND_ADMIT_SOURCES", routing.route_source_admission),
    ("D30_CLASSIFY_PREREQUISITE", routing.route_prerequisite),
    ("D08_VALIDATE_DOMAIN", routing.route_domain_validation),
    ("D09_VALIDATE_CONTENT", routing.route_content_validation),
    ("D10_COMPILE_VISUAL_BRIEFS", routing.route_visual_briefs),
    ("D12_VISUAL_BARRIER_AND_JOIN", routing.route_visual_barrier),
    ("D13_RENDER_UNIT", routing.route_unit_render),
    ("D14_INVENTORY_AND_INSPECT_UNIT_PAGES", routing.route_page_inspection),
    ("D15_FREEZE_UNIT_REVIEW_PACKET", routing.route_review_packet),
    ("M01_RESEARCH_UNIT_SOURCES", routing.route_m01_research),
    ("M02_CREATE_UNIT_DOMAIN_DATA", routing.route_m02_domain),
    ("M03_WRITE_UNIT_CONTENT", routing.route_m03_content),
    ("M05_REVIEW_ACTUAL_UNIT", routing.route_m05_unit_review),
)

# A model node's own guard has no `GUARD_DESTINATIONS` row: its accepted result
# goes where `MODEL_RESULT_DESTINATIONS` says, and its failure goes to the
# classifier. M01's two supersteps are resolved by result presence, so both of
# its destinations are declared here rather than chosen by the model.
MODEL_BRANCH_DESTINATIONS: Mapping[str, tuple[str, ...]] = {
    "M01_RESEARCH_UNIT_SOURCES": (
        "D06B_RETRIEVE_SOURCE_CANDIDATES",
        "D07_CORRELATE_AND_ADMIT_SOURCES",
        routing.MODEL_FAILURE_CLASSIFIER,
        routing.INTERRUPT_GATE,
    ),
    "M02_CREATE_UNIT_DOMAIN_DATA": (
        "D08_VALIDATE_DOMAIN",
        routing.MODEL_FAILURE_CLASSIFIER,
        routing.INTERRUPT_GATE,
    ),
    "M03_WRITE_UNIT_CONTENT": (
        "D09_VALIDATE_CONTENT",
        routing.MODEL_FAILURE_CLASSIFIER,
        routing.INTERRUPT_GATE,
    ),
    "M05_REVIEW_ACTUAL_UNIT": (
        "D16_REDUCE_UNIT_EVIDENCE",
        routing.MODEL_FAILURE_CLASSIFIER,
        routing.INTERRUPT_GATE,
    ),
}

# D92 may name only a deterministic node with current parents (spec 6.2). These
# are exactly the deterministic nodes of this path that a validated frontier can
# re-enter; D11 is absent deliberately — it is a `Send` worker whose incomplete
# members are re-dispatched by D10's guard, never re-entered directly.
RESUME_REENTRY_DESTINATIONS: tuple[str, ...] = (
    "D05_SELECT_NEXT_UNIT",
    "D06_COMPILE_SOURCE_REQUESTS",
    "D06B_RETRIEVE_SOURCE_CANDIDATES",
    "D07_CORRELATE_AND_ADMIT_SOURCES",
    "D08_VALIDATE_DOMAIN",
    "D09_VALIDATE_CONTENT",
    "D10_COMPILE_VISUAL_BRIEFS",
    "D12_VISUAL_BARRIER_AND_JOIN",
    "D13_RENDER_UNIT",
    "D14_INVENTORY_AND_INSPECT_UNIT_PAGES",
    "D15_FREEZE_UNIT_REVIEW_PACKET",
    "D30_CLASSIFY_PREREQUISITE",
)

# (source, guard value, destination, owning graph node). Every row is a real
# spec 8.2 edge whose destination node body is not implemented yet; the row is
# the contract the owner implements against.
DEFERRED_EDGES: tuple[tuple[str, str, str, str], ...] = (
    ("D05_SELECT_NEXT_UNIT", "manifest_exhausted",
     "D24_PROVE_EXACT_MANIFEST_COVERAGE", "N32_WORKBOOK_TERMINALS"),
    ("D08_VALIDATE_DOMAIN", "domain_repairable",
     "D17_CLASSIFY_UNIT_FINDINGS", "N31_REPAIR_ACCEPTANCE"),
    ("D09_VALIDATE_CONTENT", "content_repairable",
     "D17_CLASSIFY_UNIT_FINDINGS", "N31_REPAIR_ACCEPTANCE"),
    ("D12_VISUAL_BARRIER_AND_JOIN", "visuals_repairable",
     "D17_CLASSIFY_UNIT_FINDINGS", "N31_REPAIR_ACCEPTANCE"),
    ("D14_INVENTORY_AND_INSPECT_UNIT_PAGES", "layout_repairable",
     "D17_CLASSIFY_UNIT_FINDINGS", "N31_REPAIR_ACCEPTANCE"),
    ("D92_REENTER_VALIDATED_FRONTIER", "incomplete_model_activation",
     "D91_CLASSIFY_MODEL_FAILURE", "N23_MODEL_NODES"),
    ("M01_RESEARCH_UNIT_SOURCES", "model_failure",
     "D91_CLASSIFY_MODEL_FAILURE", "N23_MODEL_NODES"),
    ("M02_CREATE_UNIT_DOMAIN_DATA", "model_failure",
     "D91_CLASSIFY_MODEL_FAILURE", "N23_MODEL_NODES"),
    ("M03_WRITE_UNIT_CONTENT", "model_failure",
     "D91_CLASSIFY_MODEL_FAILURE", "N23_MODEL_NODES"),
    ("M05_REVIEW_ACTUAL_UNIT", "model_failure",
     "D91_CLASSIFY_MODEL_FAILURE", "N23_MODEL_NODES"),
    ("M05_REVIEW_ACTUAL_UNIT", "review_returned",
     "D16_REDUCE_UNIT_EVIDENCE", "N31_REPAIR_ACCEPTANCE"),
)

# What this path cannot execute, and who owns each gap. These are structural,
# reproducible facts about the current tree, not judgements: each row names the
# exact call that fails and the rework edge from `implementation.graph.v2.yaml`.
BLOCKING_GAPS: tuple[Mapping[str, str], ...] = (
    {
        "fingerprint": "plan26/n30/write-once-channel-default-conflict",
        "owner": "N11_STATE_REDUCERS",
        "rework_edge": "state_or_reducer",
        "detail": (
            "A `write_once` channel annotated with a zero-arg-constructible type "
            "(`str`, `RecordList`, `Record`) is initialized by LangGraph's "
            "`BinaryOperatorAggregate` to that type's empty value, so the reducer "
            "sees a non-None `existing` on the node's *first* write and raises "
            "`WriteOnceConflict`. 17 of the 19 `write_once` channels are affected, "
            "including `run_id`, `mode` and `effective_run`, so no episode can "
            "complete D01. The two unaffected channels are annotated `X | None`, "
            "which leaves the channel unset and bypasses the operator."
        ),
    },
    {
        "fingerprint": "plan26/n30/model-packet-not-staged",
        "owner": "N22_DETERMINISTIC_NODES",
        "rework_edge": "deterministic_node",
        "detail": (
            "D06, D06B, D07, D08 and D15 do not stage a `pending_packet` worker "
            "projection and their catalogue rows do not authorize one, so no "
            "M01/M02/M03/M05 dispatch can carry the reservation, correlation and "
            "spec section 9 projection its adapter requires."
        ),
    },
    {
        "fingerprint": "plan26/n30/visual-fanout-packet-not-staged",
        "owner": "N22_DETERMINISTIC_NODES",
        "rework_edge": "deterministic_node",
        "detail": (
            "D10 does not stage a `pending_packet` for the deterministic visual "
            "map, and D12's staged M04 briefs are bare brief records rather than "
            "M04 packets (`brief`, `permitted_facts`, `visual_contract`, "
            "`reservation`, `correlation`)."
        ),
    },
    {
        "fingerprint": "plan26/n30/d90-d91-not-registrable",
        "owner": "N23_MODEL_NODES",
        "rework_edge": "model_node_or_projection",
        "detail": (
            "`reserve_model_attempt` and `classify_model_failure` are keyword-only "
            "helpers, not `(state, context)` node callables, so D90/D91 cannot be "
            "registered; every model node's failure edge and the whole attempt "
            "reservation/retry cycle have no destination."
        ),
    },
)


def branch_destinations(source: str, available: Sequence[str]) -> tuple[str, ...]:
    """Every destination `source` declares that a node body currently exists for."""

    declared = set(MODEL_BRANCH_DESTINATIONS.get(source, routing.guard_destinations(source)))
    if source == "D92_REENTER_VALIDATED_FRONTIER":
        declared.update(RESUME_REENTRY_DESTINATIONS)
    return tuple(sorted(declared & set(available)))


def deferred_destinations(source: str, available: Sequence[str]) -> tuple[str, ...]:
    """Every destination `source` declares that has no node body yet."""

    declared = set(MODEL_BRANCH_DESTINATIONS.get(source, routing.guard_destinations(source)))
    if source == "D92_REENTER_VALIDATED_FRONTIER":
        declared.update(RESUME_REENTRY_DESTINATIONS)
    return tuple(sorted(declared - set(available)))


def unit_path_nodes() -> tuple[str, ...]:
    """Every node this module wires as an edge source or a normal-edge endpoint."""

    nodes = {source for source, _ in UNIT_BRANCHES}
    for source, target in UNIT_NORMAL_EDGES:
        nodes.update({source, target})
    return tuple(sorted(nodes))


def register_unit_path(builder: Any, available: Sequence[str]) -> dict[str, tuple[str, ...]]:
    """Add the per-unit edges to the builder N20 already registered nodes on.

    Returns the resolved path map per source, so the caller can assert the
    registered topology rather than trusting this function's own description of
    it. Adds no node and compiles nothing.
    """

    available = tuple(available)
    known = set(available)
    for node_id in unit_path_nodes():
        if node_id not in known:
            raise UnitTopologyError(
                f"N30-EDGE-DANGLING:{node_id}: the unit path names a node with no "
                f"registered body"
            )

    declared_deferred = {(source, destination) for source, _, destination, _ in DEFERRED_EDGES}
    resolved: dict[str, tuple[str, ...]] = {}
    for source, _ in UNIT_BRANCHES:
        for destination in deferred_destinations(source, available):
            if (source, destination) not in declared_deferred:
                raise UnitTopologyError(
                    f"N30-EDGE-UNDECLARED:{source}: destination {destination!r} has no "
                    f"node body and is not declared in DEFERRED_EDGES"
                )

    for source, target in UNIT_NORMAL_EDGES:
        builder.add_edge(source, target)

    for source, path in UNIT_BRANCHES:
        destinations = branch_destinations(source, available)
        if not destinations:
            raise UnitTopologyError(
                f"N30-EDGE-EMPTY:{source}: every declared destination is deferred"
            )
        builder.add_conditional_edges(
            source, path, {target: target for target in destinations}
        )
        resolved[source] = destinations
    return resolved
