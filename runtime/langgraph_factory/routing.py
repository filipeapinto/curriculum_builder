"""Pure routing guards for every conditional edge in spec section 8.2.

A guard is a total function of persisted state to one stable destination ID. It
reads no service, no clock, no filesystem, and no model result body: routing
authority is code-owned, so a guard that could consult a model or a service
would be a routing authority a model could reach.

Two rules from the section 8.2 header apply before any node-specific rule, in
this order:

1. a classified `pending_failure` routes to the terminal writer (to D91 for a
   model node, whose failures are the one class a classifier may retry);
2. a graceful interrupt observed at the node's atomic boundary routes to the
   interrupt gate.

Failure precedence over interruption is deliberate: an episode that broke and
was also asked to stop is not merely `INTERRUPTED`, and recording it as such
would hide the fault from the terminal ledger.

An undeclared guard value raises `RoutingViolation` rather than resolving to a
terminal. A value outside the frozen table means the guard table and the node
body disagree — a code defect, not a run outcome — and laundering it into
`SYSTEM_FAILURE` would report the *run* as broken when it is the *build* that
is. `assert_guard_table_total()` is called by the builder so that defect fails
compilation instead of waiting for the edge to be taken.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

__all__ = [
    "RoutingViolation",
    "TERMINAL",
    "INTERRUPT_GATE",
    "MODEL_FAILURE_CLASSIFIER",
    "ATTEMPT_RESERVATION",
    "GUARD_DESTINATIONS",
    "NORMAL_EDGE_GUARDS",
    "DYNAMIC_GUARDS",
    "FANOUT_GUARDS",
    "MODEL_RESULT_DESTINATIONS",
    "decide",
    "guard_destinations",
    "assert_guard_table_total",
    "interrupt_requested",
    "route_bootstrap",
    "route_resume_identity",
    "route_frozen_inputs",
    "route_effective_run",
    "route_capabilities",
    "route_initialize_or_resume",
    "route_frontier_reentry",
    "route_unit_selection",
    "route_source_discovery_fanout",
    "route_source_interpretation_fanout",
    "route_source_admission",
    "route_domain_validation",
    "route_content_validation",
    "route_visual_briefs",
    "route_visual_barrier",
    "route_unit_render",
    "route_page_inspection",
    "route_review_packet",
    "route_unit_reduction",
    "route_finding_classification",
    "route_repair_plan",
    "route_repair_dispatch",
    "route_repair_admission",
    "route_retest_frontier",
    "route_unit_acceptance",
    "route_accepted_checkpoint",
    "route_manifest_coverage",
    "route_workbook_assembly",
    "route_workbook_inspection",
    "route_workbook_packet",
    "route_workbook_reduction",
    "route_workbook_repair_plan",
    "route_workbook_repair_admission",
    "route_final_release",
    "route_prerequisite",
    "route_attempt_reservation",
    "route_model_failure",
    "route_interrupt_gate",
    "route_m01_research",
    "route_m02_domain",
    "route_m03_content",
    "route_m04_visual",
    "route_m05_unit_review",
    "route_m06_unit_repair",
    "route_m07_workbook_review",
    "route_m08_workbook_repair",
]


class RoutingViolation(RuntimeError):
    """A guard was asked to route a state it does not declare a destination for."""


# Stable IDs used by more than one guard row.
TERMINAL = "D98_WRITE_TERMINAL"
INTERRUPT_GATE = "D96_GRACEFUL_INTERRUPT_GATE"
MODEL_FAILURE_CLASSIFIER = "D91_CLASSIFY_MODEL_FAILURE"
ATTEMPT_RESERVATION = "D90_RESERVE_MODEL_ATTEMPT"

# The complete spec section 8.2 table: (emitting node, declared guard value) ->
# one stable destination. Guard values are exactly the vocabulary each node
# declares (`NodeSpec.guards` for the nodes N22 owns); rows for nodes N31/N32
# still owe are declared here first so those nodes implement against a frozen
# destination rather than inventing one.
GUARD_DESTINATIONS: Mapping[str, Mapping[str, str]] = {
    "D00_BOOTSTRAP_EPISODE": {
        "fresh": "D01_VALIDATE_AND_FREEZE_INPUTS",
        "resume": "D00R_REVALIDATE_RESUME_IDENTITY",
        "recover_orphan": INTERRUPT_GATE,
    },
    "D00R_REVALIDATE_RESUME_IDENTITY": {
        "resume_identity_proven": "D03_PROVE_CAPABILITIES",
    },
    "D01_VALIDATE_AND_FREEZE_INPUTS": {
        "inputs_frozen": "D02_COMPILE_EFFECTIVE_RUN",
    },
    "D02_COMPILE_EFFECTIVE_RUN": {
        "effective_run_compiled": "D03_PROVE_CAPABILITIES",
    },
    "D03_PROVE_CAPABILITIES": {
        "capabilities_proven": "D04_INITIALIZE_OR_RESUME",
        "prerequisite_unavailable": TERMINAL,
    },
    "D04_INITIALIZE_OR_RESUME": {
        "fresh_initialized": "D05_SELECT_NEXT_UNIT",
        "resume_imported": "D92_REENTER_VALIDATED_FRONTIER",
    },
    "D92_REENTER_VALIDATED_FRONTIER": {
        "incomplete_model_activation": MODEL_FAILURE_CLASSIFIER,
    },
    "D05_SELECT_NEXT_UNIT": {
        "unit_selected": "D06_COMPILE_SOURCE_REQUESTS",
        "manifest_exhausted": "D24_PROVE_EXACT_MANIFEST_COVERAGE",
    },
    "D07_CORRELATE_AND_ADMIT_SOURCES": {
        "sources_admitted": "M02_CREATE_UNIT_DOMAIN_DATA",
        "prerequisite_unresolved": "D30_CLASSIFY_PREREQUISITE",
    },
    "D08_VALIDATE_DOMAIN": {
        "domain_admitted": "M03_WRITE_UNIT_CONTENT",
        "domain_repairable": "D17_CLASSIFY_UNIT_FINDINGS",
    },
    "D09_VALIDATE_CONTENT": {
        "content_admitted": "D10_COMPILE_VISUAL_BRIEFS",
        "content_repairable": "D17_CLASSIFY_UNIT_FINDINGS",
    },
    "D10_COMPILE_VISUAL_BRIEFS": {
        "no_deterministic_visuals": "D12_VISUAL_BARRIER_AND_JOIN",
    },
    "D11_CREATE_DETERMINISTIC_VISUALS": {
        "visual_produced": "D12_VISUAL_BARRIER_AND_JOIN",
    },
    "D12_VISUAL_BARRIER_AND_JOIN": {
        "visuals_admitted": "D13_RENDER_UNIT",
        "visuals_repairable": "D17_CLASSIFY_UNIT_FINDINGS",
    },
    "D13_RENDER_UNIT": {
        "unit_rendered": "D14_INVENTORY_AND_INSPECT_UNIT_PAGES",
    },
    "D14_INVENTORY_AND_INSPECT_UNIT_PAGES": {
        "pages_inspected": "D15_FREEZE_UNIT_REVIEW_PACKET",
        "layout_repairable": "D17_CLASSIFY_UNIT_FINDINGS",
    },
    "D15_FREEZE_UNIT_REVIEW_PACKET": {
        "review_packet_frozen": "M05_REVIEW_ACTUAL_UNIT",
    },
    "D16_REDUCE_UNIT_EVIDENCE": {
        "unit_denominator_passed": "D22_ACCEPT_UNIT",
        "unit_findings_repairable": "D17_CLASSIFY_UNIT_FINDINGS",
    },
    "D17_CLASSIFY_UNIT_FINDINGS": {
        "partition_complete": "D18_PLAN_TARGETED_UNIT_REPAIR",
        "convergence_exhausted": TERMINAL,
    },
    "D18_PLAN_TARGETED_UNIT_REPAIR": {
        "repair_planned": "D19_ROUTE_UNIT_REPAIR",
        "convergence_exhausted": TERMINAL,
    },
    "D19_ROUTE_UNIT_REPAIR": {
        "model_repair": ATTEMPT_RESERVATION,
        "deterministic_repair": "D20_ADMIT_UNIT_REPAIR",
    },
    "D20_ADMIT_UNIT_REPAIR": {
        "repair_admitted": "D21_RETEST_REQUIRED_DESCENDANTS",
    },
    "D21_RETEST_REQUIRED_DESCENDANTS": {
        "retest_frontier_complete": "D16_REDUCE_UNIT_EVIDENCE",
    },
    "D22_ACCEPT_UNIT": {
        "unit_accepted": "D23_CHECKPOINT_ACCEPTED_UNIT",
    },
    "D23_CHECKPOINT_ACCEPTED_UNIT": {
        "checkpoint_correlated": "D05_SELECT_NEXT_UNIT",
    },
    "D24_PROVE_EXACT_MANIFEST_COVERAGE": {
        "unit_target_accepted": TERMINAL,
        "manifest_coverage_proven": "D25_ASSEMBLE_WORKBOOK",
    },
    "D25_ASSEMBLE_WORKBOOK": {
        "workbook_assembled": "D26_RENDER_INVENTORY_INSPECT_WORKBOOK",
    },
    "D26_RENDER_INVENTORY_INSPECT_WORKBOOK": {
        "workbook_pages_inspected": "D27_FREEZE_WORKBOOK_REVIEW_PACKET",
        "workbook_layout_repairable": "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR",
    },
    "D27_FREEZE_WORKBOOK_REVIEW_PACKET": {
        "workbook_packet_frozen": "M07_REVIEW_ACTUAL_WORKBOOK",
    },
    "D28_REDUCE_WORKBOOK_EVIDENCE": {
        "workbook_denominator_passed": "D32_RECOMPUTE_FINAL_RELEASE",
        "workbook_findings_repairable": "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR",
    },
    "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR": {
        "model_repair": ATTEMPT_RESERVATION,
        "deterministic_repair": "D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR",
        "convergence_exhausted": TERMINAL,
    },
    "D30_CLASSIFY_PREREQUISITE": {
        "prerequisite_pause": TERMINAL,
    },
    "D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR": {
        "workbook_repair_admitted": "D26_RENDER_INVENTORY_INSPECT_WORKBOOK",
    },
    "D32_RECOMPUTE_FINAL_RELEASE": {
        "release_proven": TERMINAL,
        "workbook_repairable": "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR",
    },
    "D90_RESERVE_MODEL_ATTEMPT": {
        "exhausted": TERMINAL,
    },
    "D91_CLASSIFY_MODEL_FAILURE": {
        "retry": ATTEMPT_RESERVATION,
        "system": TERMINAL,
        "exhausted": TERMINAL,
    },
    "D96_GRACEFUL_INTERRUPT_GATE": {
        "interrupted": TERMINAL,
    },
}

# Guard values satisfied by a normal edge rather than a conditional one. D98 is
# the only terminal writer and its one outgoing edge is `END`: routing it
# conditionally would create a second way to leave the graph.
NORMAL_EDGE_GUARDS: frozenset[tuple[str, str]] = frozenset(
    {("D98_WRITE_TERMINAL", "terminated")}
)

# Guard values whose destination is carried in the emitting node's own guard
# record because only that node can compute it. The value is still frozen; only
# the destination is state-derived, and it is checked against the permitted set
# below so a stored frontier can never name a model node or an unknown node.
DYNAMIC_GUARDS: Mapping[str, Mapping[str, str]] = {
    "D92_REENTER_VALIDATED_FRONTIER": {"deterministic_reentry": "destination"},
    "D21_RETEST_REQUIRED_DESCENDANTS": {"retest_frontier_incomplete": "destination"},
    "D90_RESERVE_MODEL_ATTEMPT": {"authorized": "job_id"},
    "D91_CLASSIFY_MODEL_FAILURE": {"repair": "destination"},
}

# Guard values that dispatch a `Send` fan-out instead of naming one destination.
FANOUT_GUARDS: Mapping[str, Mapping[str, str]] = {
    "D06_COMPILE_SOURCE_REQUESTS": {"discovery_fanout": "M01_RESEARCH_UNIT_SOURCES"},
    "D06B_RETRIEVE_SOURCE_CANDIDATES": {"interpretation_fanout": "M01_RESEARCH_UNIT_SOURCES"},
    "D10_COMPILE_VISUAL_BRIEFS": {
        "deterministic_visual_fanout": "D11_CREATE_DETERMINISTIC_VISUALS"
    },
    "D12_VISUAL_BARRIER_AND_JOIN": {"model_visual_fanout": "M04_CREATE_UNIT_VISUALS"},
}

# Where a model node's accepted result goes. A model never names its own next
# node; this table is the only place the destination exists, and none of these
# destinations is an acceptance, reduction, resume, or terminal authority.
MODEL_RESULT_DESTINATIONS: Mapping[str, str] = {
    "M02_CREATE_UNIT_DOMAIN_DATA": "D08_VALIDATE_DOMAIN",
    "M03_WRITE_UNIT_CONTENT": "D09_VALIDATE_CONTENT",
    "M04_CREATE_UNIT_VISUALS": "D12_VISUAL_BARRIER_AND_JOIN",
    "M05_REVIEW_ACTUAL_UNIT": "D16_REDUCE_UNIT_EVIDENCE",
    "M06_REPAIR_NAMED_UNIT_ARTIFACT": "D20_ADMIT_UNIT_REPAIR",
    "M07_REVIEW_ACTUAL_WORKBOOK": "D28_REDUCE_WORKBOOK_EVIDENCE",
    "M08_REPAIR_NAMED_WORKBOOK_DEFECT": "D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR",
}

# A stored resume frontier or retest destination may only name a deterministic
# node. Spec 6.2 D92: "a model node as stored destination ... = system".
_MODEL_ID_PREFIXES = ("M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08")


def _record(state: Mapping[str, Any], field: str) -> Mapping[str, Any] | None:
    value = state.get(field)
    return value if isinstance(value, Mapping) else None


def interrupt_requested(state: Mapping[str, Any]) -> bool:
    """Whether the node boundary observed a graceful signal at its atomic boundary.

    The boundary (owned by `graph.py`) reads the signal token and records the
    observation on the guard record, so this stays a pure function of state.
    """

    guard = _record(state, "pending_guard")
    return bool(guard and guard.get("interrupt_requested"))


def _failure_destination(state: Mapping[str, Any], *, model_node: bool) -> str | None:
    failure = _record(state, "pending_failure")
    if not failure:
        return None
    return MODEL_FAILURE_CLASSIFIER if model_node else TERMINAL


def _guard_value(state: Mapping[str, Any], node_id: str) -> tuple[Mapping[str, Any], str]:
    guard = _record(state, "pending_guard")
    if guard is None:
        raise RoutingViolation(f"{node_id}: no guard record was produced for routing")
    if guard.get("node") not in (None, node_id):
        raise RoutingViolation(
            f"{node_id}: guard record was emitted by {guard.get('node')!r}"
        )
    value = guard.get("value")
    if not isinstance(value, str):
        raise RoutingViolation(f"{node_id}: guard value {value!r} is not a declared value")
    return guard, value


def _dynamic_destination(node_id: str, guard: Mapping[str, Any], detail_key: str) -> str:
    detail = guard.get("detail")
    destination = detail.get(detail_key) if isinstance(detail, Mapping) else None
    if not isinstance(destination, str) or not destination:
        raise RoutingViolation(
            f"{node_id}: guard carries no {detail_key!r} destination"
        )
    return destination


def decide(node_id: str, state: Mapping[str, Any], *, model_node: bool = False) -> str:
    """Resolve the one destination `node_id` authorizes for `state`."""

    failure = _failure_destination(state, model_node=model_node)
    if failure is not None:
        return failure
    if interrupt_requested(state):
        return INTERRUPT_GATE
    guard, value = _guard_value(state, node_id)
    dynamic = DYNAMIC_GUARDS.get(node_id, {})
    if value in dynamic:
        destination = _dynamic_destination(node_id, guard, dynamic[value])
        if node_id in ("D92_REENTER_VALIDATED_FRONTIER", "D21_RETEST_REQUIRED_DESCENDANTS"):
            if destination.startswith(_MODEL_ID_PREFIXES):
                raise RoutingViolation(
                    f"{node_id}: {destination!r} is a model node and may not be a "
                    f"stored deterministic destination"
                )
        return destination
    destinations = GUARD_DESTINATIONS.get(node_id, {})
    if value in destinations:
        return destinations[value]
    if value in FANOUT_GUARDS.get(node_id, {}):
        raise RoutingViolation(
            f"{node_id}: guard value {value!r} dispatches a Send fan-out and must be "
            f"routed by its fan-out guard, not by a single-destination edge"
        )
    raise RoutingViolation(f"{node_id}: undeclared guard value {value!r}")


def guard_destinations(node_id: str) -> tuple[str, ...]:
    """Every destination `node_id`'s conditional edge may return, for its path map."""

    declared = set(GUARD_DESTINATIONS.get(node_id, {}).values())
    declared.update(FANOUT_GUARDS.get(node_id, {}).values())
    declared.add(TERMINAL)
    declared.add(INTERRUPT_GATE)
    if node_id.startswith(_MODEL_ID_PREFIXES):
        declared.add(MODEL_FAILURE_CLASSIFIER)
    return tuple(sorted(declared))


def assert_guard_table_total(catalogue: Mapping[str, Any]) -> None:
    """Fail closed when a node declares a guard value this table cannot route.

    Called by the builder so a table/body disagreement fails compilation by
    stable ID instead of surfacing as a `RoutingViolation` on a rare edge.
    """

    for node_id, spec in catalogue.items():
        declared = {
            value
            for value in getattr(spec, "guards", ())
            if (node_id, value) not in NORMAL_EDGE_GUARDS
        }
        routed = (
            set(GUARD_DESTINATIONS.get(node_id, {}))
            | set(DYNAMIC_GUARDS.get(node_id, {}))
            | set(FANOUT_GUARDS.get(node_id, {}))
        )
        missing = sorted(declared - routed)
        if missing:
            raise RoutingViolation(
                f"N20-GUARD-UNROUTED:{node_id}: declared guard values {missing} have no "
                f"destination in the section 8.2 table"
            )


# --------------------------------------------------------------------- fan-out guards


def _staged_fanout(state: Mapping[str, Any], node_id: str) -> list[Any]:
    """One `Send` per member of the staged fan-out packet, worker->barrier only.

    The dispatching node stages the exact worker projections in `pending_packet`
    before the fan-out is taken (spec section 10: the denominator is immutable
    and persisted before dispatch). This guard translates that staged material
    one-for-one; it never materializes a projection itself, because a projection
    invented at routing time would be one no denominator committed to.
    """

    from langgraph.types import Send  # lazy: only the fan-out path needs it

    packet = _record(state, "pending_packet")
    if packet is None:
        raise RoutingViolation(
            f"{node_id}: a fan-out guard was taken with no staged `pending_packet`"
        )
    destination = packet.get("dispatch")
    if not isinstance(destination, str) or not destination:
        raise RoutingViolation(f"{node_id}: staged packet names no dispatch destination")
    members = packet.get("packets")
    if members is None:
        members = packet.get("briefs")
    if not isinstance(members, Sequence) or isinstance(members, (str, bytes)) or not members:
        raise RoutingViolation(
            f"{node_id}: staged packet carries no non-empty worker projection list"
        )
    return [Send(destination, member) for member in members]


def _fanout_or_single(state: Mapping[str, Any], node_id: str) -> Any:
    failure = _failure_destination(state, model_node=False)
    if failure is not None:
        return failure
    if interrupt_requested(state):
        return INTERRUPT_GATE
    _, value = _guard_value(state, node_id)
    if value in FANOUT_GUARDS.get(node_id, {}):
        return _staged_fanout(state, node_id)
    return decide(node_id, state)


# ------------------------------------------------------------------ skeleton guards


def route_bootstrap(state: Mapping[str, Any]) -> str:
    """D00: fresh, legal resume, or orphan recovery (recovery reaches no product node)."""

    return decide("D00_BOOTSTRAP_EPISODE", state)


def route_resume_identity(state: Mapping[str, Any]) -> str:
    """D00R: every supplied and frozen identity digest matches."""

    return decide("D00R_REVALIDATE_RESUME_IDENTITY", state)


def route_frozen_inputs(state: Mapping[str, Any]) -> str:
    """D01: inputs are frozen, or the episode terminates."""

    return decide("D01_VALIDATE_AND_FREEZE_INPUTS", state)


def route_effective_run(state: Mapping[str, Any]) -> str:
    """D02: the effective run compiled from the frozen manifest."""

    return decide("D02_COMPILE_EFFECTIVE_RUN", state)


def route_capabilities(state: Mapping[str, Any]) -> str:
    """D03: every capability/authorization receipt passes, or a named fact pauses."""

    return decide("D03_PROVE_CAPABILITIES", state)


def route_initialize_or_resume(state: Mapping[str, Any]) -> str:
    """D04: fresh initialization to D05, validated resume import to D92."""

    return decide("D04_INITIALIZE_OR_RESUME", state)


def route_interrupt_gate(state: Mapping[str, Any]) -> str:
    """D96: the interrupt gate only ever reaches the terminal writer."""

    return decide("D96_GRACEFUL_INTERRUPT_GATE", state)


# ------------------------------------------------------------- unit-loop guards (N30)


def route_frontier_reentry(state: Mapping[str, Any]) -> str:
    """D92: the stored deterministic frontier node, or D91 for an incomplete attempt."""

    return decide("D92_REENTER_VALIDATED_FRONTIER", state)


def route_unit_selection(state: Mapping[str, Any]) -> str:
    """D05: the next required unaccepted unit, or exact-coverage proof."""

    return decide("D05_SELECT_NEXT_UNIT", state)


def route_source_discovery_fanout(state: Mapping[str, Any]) -> Any:
    """D06: one `Send` to M01 discovery per compiled request key."""

    return _fanout_or_single(state, "D06_COMPILE_SOURCE_REQUESTS")


def route_source_interpretation_fanout(state: Mapping[str, Any]) -> Any:
    """D06B: one `Send` to M01 interpretation per retrieval group."""

    return _fanout_or_single(state, "D06B_RETRIEVE_SOURCE_CANDIDATES")


def route_source_admission(state: Mapping[str, Any]) -> str:
    """D07: exact join and admission pass, or a named prerequisite is unresolved."""

    return decide("D07_CORRELATE_AND_ADMIT_SOURCES", state)


def route_domain_validation(state: Mapping[str, Any]) -> str:
    """D08: admitted domain head, or a repairable product finding."""

    return decide("D08_VALIDATE_DOMAIN", state)


def route_content_validation(state: Mapping[str, Any]) -> str:
    """D09: admitted content head, or a repairable product finding."""

    return decide("D09_VALIDATE_CONTENT", state)


def route_visual_briefs(state: Mapping[str, Any]) -> Any:
    """D10: `Send` per deterministic brief, or straight to the barrier when empty."""

    return _fanout_or_single(state, "D10_COMPILE_VISUAL_BRIEFS")


def route_visual_barrier(state: Mapping[str, Any]) -> Any:
    """D12: `Send` per eligible model brief, then admit the complete denominator."""

    return _fanout_or_single(state, "D12_VISUAL_BARRIER_AND_JOIN")


def route_unit_render(state: Mapping[str, Any]) -> str:
    """D13: the rendered unit reaches page inventory and inspection."""

    return decide("D13_RENDER_UNIT", state)


def route_page_inspection(state: Mapping[str, Any]) -> str:
    """D14: every page inspected, or a repairable layout finding."""

    return decide("D14_INVENTORY_AND_INSPECT_UNIT_PAGES", state)


def route_review_packet(state: Mapping[str, Any]) -> str:
    """D15: the frozen review packet is handed to the review family."""

    return decide("D15_FREEZE_UNIT_REVIEW_PACKET", state)


# --------------------------------------------------------- repair/acceptance (N31)


def route_unit_reduction(state: Mapping[str, Any]) -> str:
    """D16: the code-computed unit denominator accepts or opens repair."""

    return decide("D16_REDUCE_UNIT_EVIDENCE", state)


def route_finding_classification(state: Mapping[str, Any]) -> str:
    """D17: a total one-owner partition plans repair, or the bound is exhausted."""

    return decide("D17_CLASSIFY_UNIT_FINDINGS", state)


def route_repair_plan(state: Mapping[str, Any]) -> str:
    """D18: one planned repair request, or an exhausted attempt bound."""

    return decide("D18_PLAN_TARGETED_UNIT_REPAIR", state)


def route_repair_dispatch(state: Mapping[str, Any]) -> str:
    """D19: a model repair reserves an attempt first; deterministic repair does not."""

    return decide("D19_ROUTE_UNIT_REPAIR", state)


def route_repair_admission(state: Mapping[str, Any]) -> str:
    """D20: an admitted child head must retest its invalidated descendants."""

    return decide("D20_ADMIT_UNIT_REPAIR", state)


def route_retest_frontier(state: Mapping[str, Any]) -> str:
    """D21: the earliest remaining node in the fixed retest DAG, or reduction."""

    return decide("D21_RETEST_REQUIRED_DESCENDANTS", state)


def route_unit_acceptance(state: Mapping[str, Any]) -> str:
    """D22: an accepted unit is correlated to a checkpoint before the cursor moves."""

    return decide("D22_ACCEPT_UNIT", state)


def route_accepted_checkpoint(state: Mapping[str, Any]) -> str:
    """D23: the accepted unit returns to selection — the one product loop."""

    return decide("D23_CHECKPOINT_ACCEPTED_UNIT", state)


# ------------------------------------------------------------ workbook/terminal (N32)


def route_manifest_coverage(state: Mapping[str, Any]) -> str:
    """D24: one-mode unit terminal, or all-mode workbook assembly."""

    return decide("D24_PROVE_EXACT_MANIFEST_COVERAGE", state)


def route_workbook_assembly(state: Mapping[str, Any]) -> str:
    """D25: the assembled workbook is rendered and inspected."""

    return decide("D25_ASSEMBLE_WORKBOOK", state)


def route_workbook_inspection(state: Mapping[str, Any]) -> str:
    """D26: every workbook page inspected, or a workbook-owned repair."""

    return decide("D26_RENDER_INVENTORY_INSPECT_WORKBOOK", state)


def route_workbook_packet(state: Mapping[str, Any]) -> str:
    """D27: the frozen workbook packet is handed to the review family."""

    return decide("D27_FREEZE_WORKBOOK_REVIEW_PACKET", state)


def route_workbook_reduction(state: Mapping[str, Any]) -> str:
    """D28: the workbook denominator releases or opens workbook repair."""

    return decide("D28_REDUCE_WORKBOOK_EVIDENCE", state)


def route_workbook_repair_plan(state: Mapping[str, Any]) -> str:
    """D29: model or deterministic workbook repair, or an exhausted bound."""

    return decide("D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR", state)


def route_workbook_repair_admission(state: Mapping[str, Any]) -> str:
    """D31: an admitted workbook child re-enters render/inspect."""

    return decide("D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR", state)


def route_final_release(state: Mapping[str, Any]) -> str:
    """D32: the release recomputation completes, or a repairable defect remains."""

    return decide("D32_RECOMPUTE_FINAL_RELEASE", state)


def route_prerequisite(state: Mapping[str, Any]) -> str:
    """D30: a named unavailable external fact is the only pause cause."""

    return decide("D30_CLASSIFY_PREREQUISITE", state)


# ------------------------------------------------------------- model attempt guards


def route_attempt_reservation(state: Mapping[str, Any]) -> str:
    """D90: the reserved attempt authorizes exactly one model node, or exhausts."""

    return decide("D90_RESERVE_MODEL_ATTEMPT", state)


def route_model_failure(state: Mapping[str, Any]) -> str:
    """D91: one transport retry through D90, a repair owner, or a terminal."""

    guard = _record(state, "pending_guard")
    if guard is None or guard.get("kind") != "model_failure":
        raise RoutingViolation(
            "D91_CLASSIFY_MODEL_FAILURE: no model-failure classification is present"
        )
    value = guard.get("decision")
    if not isinstance(value, str):
        raise RoutingViolation(f"D91_CLASSIFY_MODEL_FAILURE: undeclared decision {value!r}")
    dynamic = DYNAMIC_GUARDS["D91_CLASSIFY_MODEL_FAILURE"]
    if value in dynamic:
        return _dynamic_destination("D91_CLASSIFY_MODEL_FAILURE", guard, dynamic[value])
    destinations = GUARD_DESTINATIONS["D91_CLASSIFY_MODEL_FAILURE"]
    if value in destinations:
        return destinations[value]
    raise RoutingViolation(f"D91_CLASSIFY_MODEL_FAILURE: undeclared decision {value!r}")


# ----------------------------------------------------------------- model result guards


def _route_model_result(state: Mapping[str, Any], job_id: str) -> str:
    failure = _failure_destination(state, model_node=True)
    if failure is not None:
        return failure
    if interrupt_requested(state):
        return INTERRUPT_GATE
    return MODEL_RESULT_DESTINATIONS[job_id]


def route_m01_research(state: Mapping[str, Any]) -> str:
    """M01: the discovery superstep reaches retrieval; interpretation reaches the join.

    The phase is read from the accumulated result maps, not from the model's
    output body: a model that could name its own next node would hold routing
    authority.
    """

    failure = _failure_destination(state, model_node=True)
    if failure is not None:
        return failure
    if interrupt_requested(state):
        return INTERRUPT_GATE
    interpretations = state.get("source_interpretations")
    if isinstance(interpretations, Mapping) and interpretations:
        return "D07_CORRELATE_AND_ADMIT_SOURCES"
    discoveries = state.get("source_discoveries")
    if isinstance(discoveries, Mapping) and discoveries:
        return "D06B_RETRIEVE_SOURCE_CANDIDATES"
    raise RoutingViolation("M01_RESEARCH_UNIT_SOURCES: no result set exists to route on")


def route_m02_domain(state: Mapping[str, Any]) -> str:
    """M02: a domain candidate is only ever validated, never admitted by its author."""

    return _route_model_result(state, "M02_CREATE_UNIT_DOMAIN_DATA")


def route_m03_content(state: Mapping[str, Any]) -> str:
    """M03: a content candidate reaches content validation."""

    return _route_model_result(state, "M03_WRITE_UNIT_CONTENT")


def route_m04_visual(state: Mapping[str, Any]) -> str:
    """M04: every model visual returns to the barrier that owns the denominator."""

    return _route_model_result(state, "M04_CREATE_UNIT_VISUALS")


def route_m05_unit_review(state: Mapping[str, Any]) -> str:
    """M05: a review is evidence for the code-computed reduction, not a verdict."""

    return _route_model_result(state, "M05_REVIEW_ACTUAL_UNIT")


def route_m06_unit_repair(state: Mapping[str, Any]) -> str:
    """M06: a repair candidate must pass boundary admission."""

    return _route_model_result(state, "M06_REPAIR_NAMED_UNIT_ARTIFACT")


def route_m07_workbook_review(state: Mapping[str, Any]) -> str:
    """M07: a workbook review is evidence for the workbook reduction."""

    return _route_model_result(state, "M07_REVIEW_ACTUAL_WORKBOOK")


def route_m08_workbook_repair(state: Mapping[str, Any]) -> str:
    """M08: a workbook repair candidate must pass workbook boundary admission."""

    return _route_model_result(state, "M08_REPAIR_NAMED_WORKBOOK_DEFECT")
