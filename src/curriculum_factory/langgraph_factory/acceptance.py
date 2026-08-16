"""Unit evidence reduction and acceptance: D16, D22, D23 of spec section 6.2.

`compute_unit_denominator()` is the one reduction engine spec section 13.1
describes -- built by `D16_REDUCE_UNIT_EVIDENCE` before repair, and recomputed
byte-for-byte by `D22_ACCEPT_UNIT` immediately before minting an accepted
receipt, off whatever the *current* heads are at that moment. A retest that
changed a head between the two calls changes what this function sees; nothing
here caches or trusts its own earlier answer.

Like `repair.py`, none of this module's functions carry a `NODE_CATALOGUE` row
yet -- registration into the compiled graph is N32's write, once `workbook.py`
exists to dispatch the workbook branch alongside them.

Known scope of this generation's denominator (documented rather than silently
assumed): it enforces source admission, the domain and content check sets, the
visual join, the page inventory/inspection set, one independent unit review
with all findings mapped through a code-owned owner table, and open-repair
closure. It treats the append-only evidence/log layer and the LangGraph
checkpoint layer as structurally present rather than independently
re-auditing them byte-for-byte here (spec section 13.1 items 13-14) --
`checkpoint_metadata`/`evidence_index_entries` shape is enforced by the state
reducers themselves (`reducers.py`), and this generation does not yet call an
external hash-chain audit from inside D22. A denominator category is never
removed to make a fixture pass; a future generation only ever tightens this.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from . import reducers, repair, routing
from .nodes import (
    SystemFailure,
    candidate_payload,
    canonical_digest,
    check_record,
    require,
    stream_id,
)
from .nodes.content import CONTENT_CHECK_IDS
from .nodes.domain import DOMAIN_CHECK_IDS

__all__ = [
    "DenominatorResult",
    "compute_unit_denominator",
    "prove_exact_manifest_coverage",
    "D16_REDUCE_UNIT_EVIDENCE",
    "D22_ACCEPT_UNIT",
    "D23_CHECKPOINT_ACCEPTED_UNIT",
    "UNIT_REPAIR_TOPOLOGY_SOURCES",
    "UNIT_REPAIR_NODE_BODIES",
    "unit_repair_destinations",
    "register_unit_repair_path",
]


@dataclass(frozen=True)
class DenominatorResult:
    passed: bool
    check: dict[str, Any]
    findings: list[dict[str, Any]] = field(default_factory=list)
    denominator: dict[str, Any] = field(default_factory=dict)


def _guard(node_id: str, value: str, **detail: Any) -> dict[str, Any]:
    return {"node": node_id, "value": value, "detail": detail}


def _status_update(state: Mapping[str, Any], unit_id: str, target: str) -> dict[str, str]:
    """`{unit_id: target}` only when `reducers.UNIT_STATUS_TRANSITIONS` allows it.

    `D05_SELECT_NEXT_UNIT` is the only node this generation that sets an
    initial `unit_status` (`SELECTED`); no deterministic node between it and
    D16 advances through `SOURCING`/`BUILDING` yet (a real, code-owned gap
    outside this module's write set), so a first-real-run D16 call legally
    has no declared transition to make. Recording nothing in that case is
    honest about what actually happened rather than raising a
    `StatusTransitionError` for a gap this module does not own, or
    fabricating an intermediate status no node ever produced. Once a unit
    reaches `REVIEWING`/`REPAIRING` the declared cycle between them is real
    and this always records it.
    """

    current = (state.get("unit_status") or {}).get(unit_id)
    if current is None:
        return {unit_id: target} if target in reducers.INITIAL_UNIT_STATUSES else {}
    if target in reducers.UNIT_STATUS_TRANSITIONS.get(current, frozenset()):
        return {unit_id: target}
    return {}


def _latest_unit_review(unit_reviews: Any, pdf_sha256: str | None) -> dict[str, Any] | None:
    if not pdf_sha256:
        return None
    matches = [
        dict(record)
        for record in unit_reviews or []
        if isinstance(record, Mapping)
        and record.get("record_kind") == "model_candidate"
        and record.get("job_id") == "M05_REVIEW_ACTUAL_UNIT"
        and record.get("unit_pdf_sha256") == pdf_sha256
    ]
    return matches[-1] if matches else None


def compute_unit_denominator(state: Mapping[str, Any], unit_id: str) -> DenominatorResult:
    """Recompute the complete current unit denominator (spec section 13.1)."""

    heads = state.get("artifact_heads") or {}
    checks = [
        record
        for record in state.get("deterministic_checks") or []
        if isinstance(record, Mapping) and record.get("owner") == unit_id
    ]
    findings: list[dict[str, Any]] = []
    categories: dict[str, Any] = {}

    def _fail(owner: str, check_id: str, pointer: str, message: str) -> None:
        findings.append({"check_id": check_id, "owner": owner, "pointer": pointer, "message": message})

    # 1-2. source admission and correlation.
    admissions = [
        record
        for record in state.get("source_admissions") or []
        if isinstance(record, Mapping) and record.get("unit_id") == unit_id
    ]
    admissions_ok = bool(admissions) and all(
        isinstance(record.get("sha256"), str) and record.get("sha256") for record in admissions
    )
    categories["source_admissions"] = {"result": "PASS" if admissions_ok else "FAIL", "count": len(admissions)}
    if not admissions_ok:
        _fail("source interpretation", "unit_source_admissions", "/sources", "no admitted source with a resolved sha256")

    # 3, 5. curriculum-domain schema/verifier/fixtures and fact-to-source resolution.
    domain_stream = stream_id(unit_id, "domain")
    domain_head = heads.get(domain_stream)
    domain_hash = domain_head.get("hash") if isinstance(domain_head, Mapping) else None
    domain_checks = {
        record["check_id"]: record
        for record in checks
        if record.get("check_id") in DOMAIN_CHECK_IDS and record.get("head_hash") == domain_hash
    }
    domain_ok = domain_hash is not None and all(
        domain_checks.get(check_id, {}).get("result") == "PASS" for check_id in DOMAIN_CHECK_IDS
    )
    categories["domain"] = {"result": "PASS" if domain_ok else "FAIL", "head_hash": domain_hash}
    if not domain_ok:
        _fail("curriculum domain", "unit_domain_denominator", "/domain", "the admitted domain head has no current passing check set")

    # 4, 6. unit schema and every sourced claim resolved.
    content_stream = stream_id(unit_id, "content")
    content_head = heads.get(content_stream)
    content_hash = content_head.get("hash") if isinstance(content_head, Mapping) else None
    content_checks = {
        record["check_id"]: record
        for record in checks
        if record.get("check_id") in CONTENT_CHECK_IDS and record.get("head_hash") == content_hash
    }
    content_ok = content_hash is not None and all(
        content_checks.get(check_id, {}).get("result") == "PASS" for check_id in CONTENT_CHECK_IDS
    )
    categories["content"] = {"result": "PASS" if content_ok else "FAIL", "head_hash": content_hash}
    if not content_ok:
        _fail("unit content", "unit_content_denominator", "/content", "the admitted content head has no current passing check set")

    # 8. every required actual visual, provenance, and asset resolution.
    visual_join = [
        record
        for record in state.get("visual_join_evidence") or []
        if isinstance(record, Mapping) and record.get("unit_id") == unit_id and record.get("phase") == "join"
    ]
    visuals_ok = bool(visual_join) and visual_join[-1].get("result") == "PASS"
    categories["visuals"] = {"result": "PASS" if visuals_ok else "FAIL"}
    if not visuals_ok:
        _fail("unit visual", "unit_visual_denominator", "/visuals", "the visual join has no current passing result")

    # 9-10. rendered PDF and a positive contiguous page inventory/inspection.
    inventories = [
        record
        for record in state.get("unit_page_inventories") or []
        if isinstance(record, Mapping) and record.get("unit_id") == unit_id
    ]
    inventory = max(inventories, key=lambda record: record.get("page_count", 0)) if inventories else None
    pdf_sha256 = inventory.get("pdf_sha256") if isinstance(inventory, Mapping) else None
    inventory_ok = isinstance(inventory, Mapping) and inventory.get("result") == "PASS"
    inspections = [
        record
        for record in state.get("unit_page_inspections") or []
        if isinstance(record, Mapping) and record.get("unit_id") == unit_id and record.get("pdf_sha256") == pdf_sha256
    ]
    expected_pages = inventory.get("page_count") if isinstance(inventory, Mapping) else -1
    inspections_ok = (
        inventory_ok
        and len(inspections) == expected_pages
        and all(record.get("result") == "PASS" for record in inspections)
    )
    categories["pages"] = {"result": "PASS" if inspections_ok else "FAIL", "pdf_sha256": pdf_sha256, "page_count": expected_pages}
    if not inspections_ok:
        _fail("unit layout", "unit_layout_denominator", "/pages", "the page inventory/inspection set is not current and fully passing")

    # 11. one independent review of the frozen actual unit, every page included.
    review = _latest_unit_review(state.get("unit_reviews"), pdf_sha256)
    review_ok = review is not None
    if review is not None:
        payload = candidate_payload(review, "unit review")
        blocking = [
            entry
            for entry in payload.get("overall_findings", [])
            if isinstance(entry, Mapping) and entry.get("severity") == "blocking"
        ]
        for page_entry in payload.get("page_findings", []):
            if isinstance(page_entry, Mapping):
                blocking.extend(
                    entry for entry in page_entry.get("findings", [])
                    if isinstance(entry, Mapping) and entry.get("severity") == "blocking"
                )
        for entry in blocking:
            owner = repair.owner_for_review_category(entry.get("category"))
            require(
                owner is not None,
                "invalid_input",
                f"review finding category {entry.get('category')!r} maps to no known owner",
                unit_id=unit_id,
            )
            findings.append(
                {
                    "check_id": "unit_review_finding",
                    "owner": owner,
                    "pointer": entry.get("evidence_reference") or "/review",
                    "message": entry.get("description", ""),
                }
            )
        review_ok = not blocking
    categories["review"] = {"result": "PASS" if review_ok else "FAIL", "present": review is not None}
    if review is None:
        _fail("unit content", "unit_review_missing", "/review", "no independent unit review candidate is present for the current pdf")

    # 12. complete repair partition, immutable history, and required current retests.
    unit_repair_requests = [
        record
        for record in state.get("repair_requests") or []
        if isinstance(record, Mapping) and record.get("unit_id") == unit_id
    ]
    resolved_keys = {
        record.get("request_key")
        for record in state.get("retest_results") or []
        if isinstance(record, Mapping) and record.get("unit_id") == unit_id and record.get("resolved")
    }
    open_requests = [record for record in unit_repair_requests if record.get("key") not in resolved_keys]
    repair_ok = not open_requests
    categories["repair"] = {"result": "PASS" if repair_ok else "FAIL", "open_requests": len(open_requests)}
    if not repair_ok:
        _fail(open_requests[0]["owner"], "unit_repair_unresolved", "/repair", "a repair request remains open (not yet retested)")

    passed = all(entry.get("result") == "PASS" for entry in categories.values())
    summary_hash = canonical_digest({"unit_id": unit_id, "categories": categories})
    check = check_record(
        scope="unit",
        owner=unit_id,
        head_hash=summary_hash,
        check_id="unit_denominator",
        attempt=1,
        result="PASS" if passed else "FAIL",
        detail={"categories": categories},
    )
    return DenominatorResult(passed=passed, check=check, findings=findings, denominator=categories)


def prove_exact_manifest_coverage(
    ordered_unit_ids: Any,
    accepted_unit_receipts: Mapping[str, Any],
    declared_coverage: Any,
) -> tuple[bool, list[str]]:
    """The D24 coverage predicate (spec section 13.2 item 1), as a reusable primitive.

    N32 owns `D24_PROVE_EXACT_MANIFEST_COVERAGE`'s node body and graph wiring;
    this function is the exact predicate it needs and is exercised directly
    here so the coverage rule itself -- exact order, exact membership, exact
    current hash -- is proven against this module's own receipt shape before
    N32 ever calls it.
    """

    ordered = list(ordered_unit_ids)
    declared = [dict(entry) for entry in declared_coverage]
    rejections: list[str] = []

    declared_ids = [entry.get("unit_id") for entry in declared]
    if declared_ids != ordered:
        rejections.append(
            f"coverage declares {declared_ids}, which is not exactly the frozen manifest order {ordered}"
        )

    for entry in declared:
        unit_id = entry.get("unit_id")
        receipt = accepted_unit_receipts.get(unit_id)
        current_hash = receipt.get("receipt_hash") if isinstance(receipt, Mapping) else None
        if current_hash is None:
            rejections.append(f"unit {unit_id!r} has no accepted receipt")
        elif entry.get("receipt_hash") != current_hash:
            rejections.append(
                f"unit {unit_id!r} coverage hash {entry.get('receipt_hash')!r} is not the current "
                f"receipt hash {current_hash!r}"
            )

    return (not rejections, rejections)


# --------------------------------------------------------------------------
# D16_REDUCE_UNIT_EVIDENCE
# --------------------------------------------------------------------------


def D16_REDUCE_UNIT_EVIDENCE(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Build the complete current unit denominator; accept it, or open repair."""

    unit_id = state.get("selected_unit_id")
    require(isinstance(unit_id, str) and bool(unit_id), "invalid_input", "no unit is selected")
    require(
        unit_id not in (state.get("accepted_unit_receipts") or {}),
        "integrity",
        "an accepted unit can never re-enter denominator reduction",
        unit_id=unit_id,
    )

    result = compute_unit_denominator(state, unit_id)
    if result.passed:
        return {
            "deterministic_checks": [result.check],
            "unit_status": _status_update(state, unit_id, "REVIEWING"),
            "pending_guard": _guard(
                "D16_REDUCE_UNIT_EVIDENCE", "unit_denominator_passed", unit_id=unit_id
            ),
        }
    return {
        "deterministic_checks": [result.check],
        "unit_status": _status_update(state, unit_id, "REVIEWING"),
        "pending_guard": _guard(
            "D16_REDUCE_UNIT_EVIDENCE", "unit_findings_repairable",
            unit_id=unit_id, findings=result.findings,
        ),
    }


# --------------------------------------------------------------------------
# D22_ACCEPT_UNIT
# --------------------------------------------------------------------------


def D22_ACCEPT_UNIT(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Recompute the full denominator immediately before minting an accepted receipt.

    Never trusts D16's earlier pass: a retest that changed a head between the
    two calls, or evidence that went stale, makes this recomputation fail even
    though D16 once passed. Any absent, stale, or failing member blocks
    acceptance outright (spec section 6.2 D22 row) -- there is no partial or
    warned acceptance path.
    """

    unit_id = state.get("selected_unit_id")
    require(isinstance(unit_id, str) and bool(unit_id), "invalid_input", "no unit is selected")
    accepted = state.get("accepted_unit_receipts") or {}
    require(unit_id not in accepted, "integrity", "unit is already accepted", unit_id=unit_id)

    result = compute_unit_denominator(state, unit_id)
    require(
        result.passed,
        "integrity",
        "D22 recomputation does not currently pass; acceptance is refused",
        unit_id=unit_id, categories=result.denominator,
    )

    heads = state.get("artifact_heads") or {}
    unit_stream_hashes = {
        stream: head.get("hash")
        for stream, head in heads.items()
        if isinstance(head, Mapping) and stream.startswith(f"units/{unit_id}/")
    }
    receipt_body = {
        "unit_id": unit_id,
        "denominator": result.denominator,
        "artifact_head_hashes": unit_stream_hashes,
        "log_high_water_mark": len(state.get("evidence_index_entries") or []),
    }
    receipt = dict(receipt_body)
    receipt["receipt_hash"] = canonical_digest(receipt_body)

    return {
        "accepted_unit_receipts": {unit_id: receipt},
        "deterministic_checks": [result.check],
        "pending_guard": _guard("D22_ACCEPT_UNIT", "unit_accepted", unit_id=unit_id, receipt_hash=receipt["receipt_hash"]),
    }


# --------------------------------------------------------------------------
# D23_CHECKPOINT_ACCEPTED_UNIT
# --------------------------------------------------------------------------


def D23_CHECKPOINT_ACCEPTED_UNIT(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Correlate the accepted receipt to a checkpoint, then advance the cursor.

    The cursor's `accepted_ordinal` is written in the same update as the
    checkpoint-correlation record, never before it: `D05_SELECT_NEXT_UNIT`'s
    own invariant (`accepted_ordinal == len(accepted receipts in closure)`)
    would otherwise be satisfiable by a cursor that outran its correlation
    evidence, which is exactly the ordering spec section 6.2's D23 row and
    this node's own TEST 7 forbid.
    """

    unit_id = state.get("selected_unit_id")
    require(isinstance(unit_id, str) and bool(unit_id), "invalid_input", "no unit is selected")
    accepted = state.get("accepted_unit_receipts") or {}
    receipt = accepted.get(unit_id)
    require(isinstance(receipt, Mapping), "integrity", "D23 requires an accepted receipt", unit_id=unit_id)

    evidence_entries = state.get("evidence_index_entries") or []
    existing_checkpoints = state.get("checkpoint_metadata") or []
    checkpoint_id = f"ckpt-{unit_id}-{receipt['receipt_hash'][:16]}"

    checkpoint_record = {
        "key": canonical_digest({"unit_id": unit_id, "checkpoint_id": checkpoint_id}),
        "unit_id": unit_id,
        "checkpoint_id": checkpoint_id,
        "receipt_hash": receipt["receipt_hash"],
        "run_id": state.get("run_id"),
        "episode_id": state.get("episode_id"),
        "evidence_ordinal": len(evidence_entries),
        "prior_checkpoint_count": len(existing_checkpoints),
    }

    correlation_record = {
        "key": canonical_digest({"unit_id": unit_id, "checkpoint_id": checkpoint_id, "kind": "accepted_unit_checkpoint"}),
        "unit_id": unit_id,
        "checkpoint_id": checkpoint_id,
        "receipt_hash": receipt["receipt_hash"],
    }

    effective_run = state.get("effective_run") or {}
    closure = effective_run.get("target_closure") or []
    cursor = dict(state.get("cursor") or {})
    manifest_ordinal = cursor.get("manifest_ordinal", closure.index(unit_id) + 1 if unit_id in closure else 0)
    accepted_ordinal = len([member for member in closure if member in accepted]) if closure else cursor.get("accepted_ordinal", 0) + 1
    if unit_id not in closure:
        # Defensive: D05 always selects from the closure, so this is unreachable
        # in the real pipeline; kept explicit rather than silently trusting
        # an out-of-closure cursor advance.
        raise SystemFailure("integrity", "checkpointed unit is not in the frozen target closure", {"unit_id": unit_id})

    return {
        "checkpoint_metadata": [checkpoint_record],
        "accepted_unit_checkpoint_receipts": [correlation_record],
        "cursor": {"manifest_ordinal": manifest_ordinal, "accepted_ordinal": accepted_ordinal},
        "pending_guard": _guard(
            "D23_CHECKPOINT_ACCEPTED_UNIT", "checkpoint_correlated",
            unit_id=unit_id, checkpoint_id=checkpoint_id,
        ),
    }


# --------------------------------------------------------------------------
# Topology registration (spec section 8.2's unit repair/acceptance cycle)
# --------------------------------------------------------------------------
#
# Additive registration over the one builder N20/N30 already populated, in the
# same convention `unit_graph.register_unit_path`/`workbook.register_workbook_
# path` use: no `add_node`, no `StateGraph()`, no `compile()`. Unlike
# `workbook.register_workbook_path`, this module's own node bodies (D16, D22,
# D23 here; D17-D21 in `repair.py`) are *not* added by this function -- they
# are already members of `graph.unit_repair_binding_inventory()`, the widened
# set `graph.register_skeleton` itself `add_node`s before this function ever
# runs, so this only adds the edges neither `unit_graph.py` nor
# `register_skeleton` own: the loop internal to D16-D23 (spec section 8.2's
# "D16 FAIL -> D17 -> D18 -> D19 -> ... -> D20 -> D21 -> ... -> D16" cycle) and
# D22 -> D23 -> D05, plus M06's own result edge (the one N31-owned model job,
# wired here for the same reason `workbook.py` wires M07/M08 itself: neither
# is a `unit_graph.UNIT_BRANCHES` source).
#
# D08/D09/D12/D14/D91's own edges to D17, and M05's own edge to D16, are never
# added here: those six rows are declared in `unit_graph.DEFERRED_EDGES` and
# resolve automatically the moment D16/D17 are members of the `available`
# sequence `unit_graph.register_unit_path` receives -- `unit_graph.py` is
# frozen (N30's write) and already correct for exactly this widening.


def _repair_routing() -> Any:
    from . import routing

    return routing


UNIT_REPAIR_NODE_BODIES: Mapping[str, Any] = {
    "D16_REDUCE_UNIT_EVIDENCE": D16_REDUCE_UNIT_EVIDENCE,
    "D17_CLASSIFY_UNIT_FINDINGS": repair.D17_CLASSIFY_UNIT_FINDINGS,
    "D18_PLAN_TARGETED_UNIT_REPAIR": repair.D18_PLAN_TARGETED_UNIT_REPAIR,
    "D19_ROUTE_UNIT_REPAIR": repair.D19_ROUTE_UNIT_REPAIR,
    "D20_ADMIT_UNIT_REPAIR": repair.D20_ADMIT_UNIT_REPAIR,
    "D21_RETEST_REQUIRED_DESCENDANTS": repair.D21_RETEST_REQUIRED_DESCENDANTS,
    "D22_ACCEPT_UNIT": D22_ACCEPT_UNIT,
    "D23_CHECKPOINT_ACCEPTED_UNIT": D23_CHECKPOINT_ACCEPTED_UNIT,
}

# The one N31-owned model job (`M06_REPAIR_NAMED_UNIT_ARTIFACT`) is a real
# conditional-edge source too, alongside the eight deterministic nodes above:
# neither is a `unit_graph.UNIT_BRANCHES` source, so both are wired by this
# module's own `register_unit_repair_path`, not by N30's frozen table.
UNIT_REPAIR_TOPOLOGY_SOURCES: tuple[str, ...] = (
    "D16_REDUCE_UNIT_EVIDENCE",
    "D17_CLASSIFY_UNIT_FINDINGS",
    "D18_PLAN_TARGETED_UNIT_REPAIR",
    "D19_ROUTE_UNIT_REPAIR",
    "D20_ADMIT_UNIT_REPAIR",
    "D21_RETEST_REQUIRED_DESCENDANTS",
    "D22_ACCEPT_UNIT",
    "D23_CHECKPOINT_ACCEPTED_UNIT",
    "M06_REPAIR_NAMED_UNIT_ARTIFACT",
)


def unit_repair_destinations(source: str, available: Sequence[str]) -> tuple[str, ...]:
    """Every destination `source` declares that a node body currently exists for.

    Two rows need help beyond `routing.guard_destinations()`'s generic table
    lookup, for the same reason `unit_graph.branch_destinations` special-cases
    `D92_REENTER_VALIDATED_FRONTIER`: `D21_RETEST_REQUIRED_DESCENDANTS`'
    `retest_frontier_incomplete` guard value carries a *state-derived*
    destination (one of `repair.RETEST_FIRST_NODE`'s values), not a row of
    `routing.GUARD_DESTINATIONS`; and `M06_REPAIR_NAMED_UNIT_ARTIFACT`'s
    accepted-result destination lives in `routing.MODEL_RESULT_DESTINATIONS`,
    a table `guard_destinations()` deliberately does not consult (the same
    reason `workbook.register_workbook_path` adds `model_result_extra` for
    M07/M08 rather than trusting `guard_destinations()` alone).
    """

    routing = _repair_routing()
    declared = set(routing.guard_destinations(source))
    if source == "D21_RETEST_REQUIRED_DESCENDANTS":
        declared.update(repair.RETEST_FIRST_NODE.values())
    if source == "M06_REPAIR_NAMED_UNIT_ARTIFACT":
        declared.add(routing.MODEL_RESULT_DESTINATIONS["M06_REPAIR_NAMED_UNIT_ARTIFACT"])
    return tuple(sorted(declared & set(available)))


def register_unit_repair_path(builder: Any, available: Sequence[str]) -> dict[str, tuple[str, ...]]:
    """Add the unit repair/acceptance cycle's own outgoing edges to the shared builder.

    Called by `graph.py` (via `register_unit_repair_topology`) after
    `register_skeleton` -- which has already `add_node`-registered every
    member of `UNIT_REPAIR_NODE_BODIES` because `graph.unit_repair_binding_
    inventory()` is part of the bindings `register_skeleton` receives -- and
    after `unit_graph.register_unit_path`, over the same `StateGraph`
    instance. Returns the resolved per-source destination map so a caller can
    assert the registered topology the way `unit_graph.register_unit_path`
    already does.
    """

    routing = _repair_routing()
    available_set = set(available)
    for node_id in UNIT_REPAIR_TOPOLOGY_SOURCES:
        if node_id not in available_set:
            raise routing.RoutingViolation(
                f"N31-EDGE-DANGLING:{node_id}: the unit repair path names a node with no "
                f"registered body"
            )

    guards: dict[str, Any] = {
        "D16_REDUCE_UNIT_EVIDENCE": routing.route_unit_reduction,
        "D17_CLASSIFY_UNIT_FINDINGS": routing.route_finding_classification,
        "D18_PLAN_TARGETED_UNIT_REPAIR": routing.route_repair_plan,
        "D19_ROUTE_UNIT_REPAIR": routing.route_repair_dispatch,
        "D20_ADMIT_UNIT_REPAIR": routing.route_repair_admission,
        "D21_RETEST_REQUIRED_DESCENDANTS": routing.route_retest_frontier,
        "D22_ACCEPT_UNIT": routing.route_unit_acceptance,
        "D23_CHECKPOINT_ACCEPTED_UNIT": routing.route_accepted_checkpoint,
        "M06_REPAIR_NAMED_UNIT_ARTIFACT": routing.route_m06_unit_repair,
    }

    resolved: dict[str, tuple[str, ...]] = {}
    for source in UNIT_REPAIR_TOPOLOGY_SOURCES:
        path = guards[source]
        destinations = unit_repair_destinations(source, available)
        if not destinations:
            raise routing.RoutingViolation(f"N31-EDGE-EMPTY:{source}: every declared destination is deferred")
        builder.add_conditional_edges(source, path, {target: target for target in destinations})
        resolved[source] = destinations
    return resolved
