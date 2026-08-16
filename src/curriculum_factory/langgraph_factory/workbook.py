"""Workbook assembly, review, repair, and release: D24-D32 of spec section 6.2.

This is the one workbook engine (spec section 15's `node_ownership.v1.md`
resolution): exact manifest coverage (D24), assembly (D25), render/inventory/
inspection (D26), review-packet freeze (D27), evidence reduction (D28),
workbook-only defect classification/planning (D29), admission/retest (D31),
and final release recomputation (D32) -- plus the two product-terminal call
sites `D24` (one-mode `UNIT_ACCEPTED`) and `D32` (`COMPLETE`) reach.

Like `repair.py`/`acceptance.py`, none of these functions carries a
`NODE_CATALOGUE` row: D24-D32 are not narrowed by `nodes.deterministic_node()`
and are registered into the compiled graph by `register_workbook_path()`
below, called from `graph.py`. A product terminal is never written here --
`D24`/`D32` only ever produce a `terminal_candidate` and a `pending_guard`
that routes to the one real `D98_WRITE_TERMINAL` (owned by
`nodes/terminal.py`); this module contains no terminal writer and cannot
reach `END` directly.

Workbook repair is boundary-scoped to the four workbook-owned components
(`front_matter`, `navigation`, `layout`, `assembly` -- `model_nodes
.WORKBOOK_OWNED_COMPONENTS`) and can never stage a writable unit source or
PDF: `D31` recomputes and compares every accepted unit's frozen PDF hash
before and after a repair candidate is admitted, and any change is a system
failure, never a routed finding (spec section 12: "Workbook repair cannot
stage writable unit sources or PDFs").

Only `D30_CLASSIFY_PREREQUISITE` (owned by N22's `nodes/sources.py`) may ever
propose `PAUSED_PREREQUISITE`; nothing in this module does, and `D98`
independently re-derives every candidate's precondition regardless of which
guard proposed it.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from . import repair
from .nodes import (
    SystemFailure,
    canonical_digest,
    candidate_payload,
    check_record,
    contract_reference,
    require,
    sha256_file,
    staged_dispatch,
    stream_id,
    worker_packet,
)

__all__ = [
    "WORKBOOK_STREAM",
    "WORKBOOK_OWNED_COMPONENTS",
    "DETERMINISTIC_ONLY_COMPONENTS",
    "MODEL_ONLY_COMPONENTS",
    "WorkbookDenominatorResult",
    "compute_workbook_denominator",
    "D24_PROVE_EXACT_MANIFEST_COVERAGE",
    "D25_ASSEMBLE_WORKBOOK",
    "D26_RENDER_INVENTORY_INSPECT_WORKBOOK",
    "D27_FREEZE_WORKBOOK_REVIEW_PACKET",
    "D28_REDUCE_WORKBOOK_EVIDENCE",
    "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR",
    "D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR",
    "D32_RECOMPUTE_FINAL_RELEASE",
    "WORKBOOK_NODE_BODIES",
    "WORKBOOK_TOPOLOGY_SOURCES",
    "register_workbook_path",
]


# The one workbook stream: unlike a unit, there is exactly one workbook per
# episode, so `workbook_head`/`workbook_versions` key on this single name
# rather than a per-entity stream id the way `nodes.stream_id` mints one.
WORKBOOK_STREAM = "workbook"

WORKBOOK_OWNED_COMPONENTS: frozenset[str] = frozenset(
    {"front_matter", "navigation", "layout", "assembly"}
)

# Spec section 12's workbook row: "deterministic assembly/template repair
# first; M08 only for the exact workbook-owned component". `layout` and
# `assembly` are the two components a deterministic re-render/re-assemble can
# regenerate outright (the same renderer D25 already calls); `front_matter`
# and `navigation` are authored text with no deterministic producer in this
# generation, so they are M08-eligible. This mirrors unit repair's
# `DETERMINISTIC_ONLY_OWNERS`/`MODEL_ONLY_OWNERS` split (`repair.py`) rather
# than inventing a second policy shape.
DETERMINISTIC_ONLY_COMPONENTS: frozenset[str] = frozenset({"layout", "assembly"})
MODEL_ONLY_COMPONENTS: frozenset[str] = frozenset({"front_matter", "navigation"})

DETERMINISTIC_REPAIR_CANDIDATE_KIND = "deterministic_workbook_repair_candidate"

# The one body section each workbook-owned component's repair is scoped to.
# `layout` and `assembly` share `/assembly` deliberately (spec section 12:
# both are re-rendered together); `/coverage` -- the accepted-unit hash
# ledger -- is named by no component, which is exactly the unit-byte
# immutability guarantee D31 also re-derives independently.
_COMPONENT_BODY_POINTER: dict[str, str] = {
    "front_matter": "/front_matter",
    "navigation": "/navigation",
    "layout": "/assembly",
    "assembly": "/assembly",
}

# Frozen limits reused from the one repair engine (spec section 12: "shared
# boundary/diff/invalidation-DAG machinery reused by workbook repair") --
# never redeclared with a different value here.
MAX_REPAIR_CHILDREN_PER_CHAIN = repair.MAX_REPAIR_CHILDREN_PER_CHAIN
MAX_FINGERPRINT_REPEATS = repair.MAX_FINGERPRINT_REPEATS


def _guard(node_id: str, value: str, **detail: Any) -> dict[str, Any]:
    return {"node": node_id, "value": value, "detail": detail}


def _record(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, Mapping), "schema_contract", f"{label} must be a JSON object")
    return dict(value)


def _accepted_pdf_hash(receipt: Any, unit_id: str) -> str:
    require(isinstance(receipt, Mapping), "integrity", f"unit {unit_id!r} has no accepted receipt")
    pages = ((receipt.get("denominator") or {}).get("pages")) or {}
    pdf_sha256 = pages.get("pdf_sha256")
    require(
        isinstance(pdf_sha256, str) and bool(pdf_sha256),
        "integrity",
        f"the accepted receipt for {unit_id!r} carries no frozen unit pdf hash",
    )
    return pdf_sha256


def _latest_workbook_version(workbook_versions: Any, workbook_hash: str) -> dict[str, Any] | None:
    matches = [
        dict(record)
        for record in workbook_versions or []
        if isinstance(record, Mapping)
        and record.get("hash") == workbook_hash
        and record.get("record_kind") is None
    ]
    return matches[-1] if matches else None


def _latest_model_repair_candidate(workbook_versions: Any) -> dict[str, Any] | None:
    matches = [
        dict(record)
        for record in workbook_versions or []
        if isinstance(record, Mapping)
        and record.get("record_kind") == "model_candidate"
        and record.get("job_id") == "M08_REPAIR_NAMED_WORKBOOK_DEFECT"
    ]
    return matches[-1] if matches else None


def _latest_deterministic_repair_candidate(
    workbook_versions: Any, *, request_key: str
) -> dict[str, Any] | None:
    matches = [
        dict(record)
        for record in workbook_versions or []
        if isinstance(record, Mapping)
        and record.get("record_kind") == DETERMINISTIC_REPAIR_CANDIDATE_KIND
        and record.get("request_key") == request_key
    ]
    return matches[-1] if matches else None


def _latest_workbook_review(workbook_reviews: Any, workbook_pdf_sha256: str | None) -> dict[str, Any] | None:
    if not workbook_pdf_sha256:
        return None
    matches = [
        dict(record)
        for record in workbook_reviews or []
        if isinstance(record, Mapping)
        and record.get("record_kind") == "model_candidate"
        and record.get("job_id") == "M07_REVIEW_ACTUAL_WORKBOOK"
        and record.get("workbook_pdf_sha256") == workbook_pdf_sha256
    ]
    return matches[-1] if matches else None


def _attempt_key(fingerprint: str) -> str:
    return f"workbook_repair|{fingerprint}"


def _repeat_key(fingerprint: str) -> str:
    return f"workbook_repeat|{fingerprint}"


# --------------------------------------------------------------------------
# D24_PROVE_EXACT_MANIFEST_COVERAGE
# --------------------------------------------------------------------------


def D24_PROVE_EXACT_MANIFEST_COVERAGE(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """One-mode unit terminal, or all-mode exact ordered coverage proof."""

    mode = state.get("mode")
    require(mode in ("one", "all"), "invalid_input", "D24 requires a decided run mode")

    effective_run = state.get("effective_run") or {}
    closure = list(effective_run.get("target_closure") or [])
    require(bool(closure), "invalid_input", "D24 requires a non-empty frozen target closure")
    accepted = state.get("accepted_unit_receipts") or {}

    missing = [unit_id for unit_id in closure if unit_id not in accepted]
    require(
        not missing,
        "integrity",
        "D24 requires an accepted receipt for every unit in the frozen closure",
        missing=missing,
    )

    if mode == "one":
        requested = state.get("requested_unit_id")
        require(
            isinstance(requested, str) and requested in accepted,
            "integrity",
            "the requested unit has no accepted receipt",
            requested_unit_id=requested,
        )
        require(requested in closure, "integrity", "the requested unit is outside the frozen closure")
        receipt = accepted[requested]
        checkpoints = state.get("checkpoint_metadata") or []
        require(bool(checkpoints), "integrity", "D24 requires a current checkpoint correlation")
        checkpoint_id = checkpoints[-1].get("checkpoint_id")

        candidate = {
            "kind": "UNIT_ACCEPTED",
            "unit_id": requested,
            "receipt_hash": receipt["receipt_hash"],
            "closure_receipt_hashes": {unit_id: accepted[unit_id]["receipt_hash"] for unit_id in closure},
            "denominator": receipt["denominator"],
            "log_high_water_mark": len(state.get("evidence_index_entries") or []),
            "checkpoint_id": checkpoint_id,
        }
        return {
            "terminal_candidate": candidate,
            "pending_guard": _guard(
                "D24_PROVE_EXACT_MANIFEST_COVERAGE", "unit_target_accepted", unit_id=requested
            ),
        }

    ordered = list(effective_run.get("ordered_unit_ids") or [])
    require(bool(ordered), "invalid_input", "D24 requires a non-empty frozen manifest order")
    require(
        sorted(ordered) == sorted(closure) and len(ordered) == len(closure),
        "integrity",
        "full-mode manifest order and target closure disagree",
        ordered=ordered,
        closure=closure,
    )

    declared_coverage = [{"unit_id": unit_id, "receipt_hash": accepted[unit_id]["receipt_hash"]} for unit_id in ordered]
    ok, rejections = repair_acceptance_coverage_proof(ordered, accepted, declared_coverage)
    require(ok, "integrity", "exact manifest coverage failed", rejections=rejections)

    coverage_record = {
        "key": canonical_digest({"kind": "workbook_coverage", "ordered_unit_ids": ordered, "declared_coverage": declared_coverage}),
        "ordered_unit_ids": ordered,
        "receipt_hashes": {unit_id: accepted[unit_id]["receipt_hash"] for unit_id in ordered},
    }
    return {
        "workbook_coverage": [coverage_record],
        "pending_guard": _guard(
            "D24_PROVE_EXACT_MANIFEST_COVERAGE", "manifest_coverage_proven", ordered_unit_ids=ordered
        ),
    }


def repair_acceptance_coverage_proof(
    ordered_unit_ids: Sequence[str],
    accepted_unit_receipts: Mapping[str, Any],
    declared_coverage: Sequence[Mapping[str, Any]],
) -> tuple[bool, list[str]]:
    """The exact coverage predicate (spec section 13.2 item 1), applied at D24.

    Delegates to N31's `acceptance.prove_exact_manifest_coverage` -- one
    coverage rule, not a second copy of it -- imported lazily to avoid a
    module cycle (`acceptance.py` itself imports `repair`, and this module
    imports `repair` at top level).
    """

    from . import acceptance

    return acceptance.prove_exact_manifest_coverage(
        list(ordered_unit_ids), accepted_unit_receipts, list(declared_coverage)
    )


# --------------------------------------------------------------------------
# D25_ASSEMBLE_WORKBOOK
# --------------------------------------------------------------------------


def D25_ASSEMBLE_WORKBOOK(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Assemble the workbook over exact accepted receipts and immutable unit PDFs.

    Never mutates a unit: every unit PDF byte this reads is re-verified against
    the hash the unit's own accepted receipt froze, both the version D25 sees
    in state and the actual bytes on disk, before assembly proceeds.
    """

    coverage_entries = [
        record for record in state.get("workbook_coverage") or [] if isinstance(record, Mapping)
    ]
    require(bool(coverage_entries), "invalid_input", "D25 requires a proven coverage record")
    coverage = coverage_entries[-1]
    ordered = list(coverage["ordered_unit_ids"])
    receipt_hashes = dict(coverage["receipt_hashes"])
    accepted = state.get("accepted_unit_receipts") or {}
    artifact_versions = state.get("artifact_versions") or []

    unit_pdf_hashes: dict[str, str] = {}
    for unit_id in ordered:
        receipt = accepted.get(unit_id)
        require(
            isinstance(receipt, Mapping) and receipt.get("receipt_hash") == receipt_hashes.get(unit_id),
            "integrity",
            "the proven coverage receipt hash is not the current accepted receipt",
            unit_id=unit_id,
        )
        accepted_pdf_sha256 = _accepted_pdf_hash(receipt, unit_id)

        layout_stream = stream_id(unit_id, "layout")
        layout_candidates = [
            dict(record)
            for record in artifact_versions
            if isinstance(record, Mapping) and record.get("stream") == layout_stream
        ]
        require(bool(layout_candidates), "integrity", f"no rendered layout exists for accepted unit {unit_id!r}")
        layout_version = max(layout_candidates, key=lambda record: record.get("version", 0))
        require(
            layout_version.get("pdf_sha256") == accepted_pdf_sha256,
            "integrity",
            "unit PDF bytes changed after acceptance",
            unit_id=unit_id,
            accepted=accepted_pdf_sha256,
            current=layout_version.get("pdf_sha256"),
        )
        pdf_path = Path(str(layout_version.get("pdf_path")))
        require(pdf_path.is_file(), "integrity", "the accepted unit PDF is missing", unit_id=unit_id)
        actual = sha256_file(pdf_path)
        require(
            actual == accepted_pdf_sha256,
            "integrity",
            "the unit PDF bytes on disk no longer match the accepted hash",
            unit_id=unit_id,
        )
        unit_pdf_hashes[unit_id] = accepted_pdf_sha256

    engine_root = state.get("engine_root")
    front_matter = contract_reference(engine_root, "meta_prompt/assets/pedagogy.v1.md")

    registry = getattr(runtime_context, "transport_registry", None)
    assembler = getattr(registry, "assemble_workbook", None) if registry else None
    require(callable(assembler), "capability", "runtime context exposes no workbook assembler")
    try:
        assembled = assembler(ordered, unit_pdf_hashes, front_matter)
    except Exception as error:  # noqa: BLE001 - a tool fault is always a system failure
        raise SystemFailure(
            "tool", f"workbook assembly failed: {error}", {"ordered_unit_ids": ordered}
        ) from error

    result = _record(assembled, "workbook assembly result")
    for field in ("workbook_pdf_path", "workbook_pdf_sha256", "assembly_map", "navigation"):
        require(field in result, "integrity", f"workbook assembly result has no {field!r}")
    assembly_map = result["assembly_map"]
    require(
        isinstance(assembly_map, list) and [entry.get("unit_id") for entry in assembly_map] == ordered,
        "integrity",
        "the assembly map is not exactly the proven coverage order",
        expected=ordered,
    )
    for entry in assembly_map:
        entry_record = _record(entry, "assembly map entry")
        require(
            entry_record.get("unit_pdf_sha256") == unit_pdf_hashes.get(entry_record.get("unit_id")),
            "integrity",
            "the assembly map cites a unit pdf hash the coverage did not prove",
            unit_id=entry_record.get("unit_id"),
        )

    body = {
        "front_matter": front_matter,
        "navigation": result["navigation"],
        "coverage": {"ordered_unit_ids": ordered, "unit_pdf_hashes": unit_pdf_hashes},
        "assembly": {
            "assembly_map": assembly_map,
            "workbook_pdf_path": result["workbook_pdf_path"],
            "workbook_pdf_sha256": result["workbook_pdf_sha256"],
        },
    }

    current_head = (state.get("workbook_head") or {}).get(WORKBOOK_STREAM) or {}
    version_record = {
        "key": canonical_digest({"kind": "workbook_version", "body": body, "parent": current_head.get("hash")}),
        "record_kind": None,
        "version": int(current_head.get("version", 0)) + 1,
        "parent_hash": current_head.get("hash"),
        "hash": canonical_digest(body),
        "body": body,
    }

    return {
        "workbook_versions": [version_record],
        "workbook_head": {
            WORKBOOK_STREAM: {
                "version": version_record["version"],
                "parent_hash": version_record["parent_hash"],
                "hash": version_record["hash"],
            }
        },
        "pending_guard": _guard("D25_ASSEMBLE_WORKBOOK", "workbook_assembled"),
    }


# --------------------------------------------------------------------------
# D26_RENDER_INVENTORY_INSPECT_WORKBOOK
# --------------------------------------------------------------------------


def D26_RENDER_INVENTORY_INSPECT_WORKBOOK(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Prove a positive contiguous workbook page inventory and inspect every page."""

    head = (state.get("workbook_head") or {}).get(WORKBOOK_STREAM)
    require(isinstance(head, Mapping), "invalid_input", "D26 requires an assembled workbook head")
    version = _latest_workbook_version(state.get("workbook_versions"), head["hash"])
    require(isinstance(version, Mapping), "integrity", "no admitted workbook version matches the current head")

    assembly = version["body"]["assembly"]
    pdf_sha256 = assembly["workbook_pdf_sha256"]
    pdf_path = Path(str(assembly["workbook_pdf_path"]))
    require(pdf_path.is_file(), "integrity", "the assembled workbook PDF is missing")
    actual = sha256_file(pdf_path)
    require(
        actual == pdf_sha256,
        "integrity",
        "the workbook PDF bytes changed after assembly",
        declared=pdf_sha256,
        actual=actual,
    )

    registry = getattr(runtime_context, "transport_registry", None)
    inspector = getattr(registry, "inspect_workbook_pages", None) if registry else None
    require(callable(inspector), "capability", "runtime context exposes no workbook page inspector")
    try:
        inspected = inspector(str(pdf_path), pdf_sha256)
    except Exception as error:  # noqa: BLE001 - a rasterizer/tool fault is always a system failure
        raise SystemFailure(
            "tool", f"workbook page inspection failed: {error}", {"pdf_sha256": pdf_sha256}
        ) from error

    report = _record(inspected, "workbook page inspection")
    pages = report.get("pages")
    require(isinstance(pages, list), "schema_contract", "workbook page inspection returned a non-list page set")

    numbers = [page.get("number") for page in pages if isinstance(page, Mapping)]
    contiguous = numbers == list(range(1, len(pages) + 1))
    positive = len(pages) > 0

    inventory = {
        "key": f"workbook/{pdf_sha256}",
        "pdf_sha256": pdf_sha256,
        "page_count": len(pages),
        "contiguous": contiguous,
        "result": "PASS" if positive and contiguous else "FAIL",
    }

    inspections: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    if not (positive and contiguous):
        findings.append(
            {
                "component": "layout",
                "check_id": "workbook_page_inventory",
                "pointer": "/assembly/pages",
                "message": "page inventory is empty" if not positive else f"page numbering is not 1..N: {numbers}",
            }
        )

    for page in pages:
        page_record = _record(page, "workbook page inspection entry")
        number = page_record.get("number")
        problems = sorted(str(item) for item in page_record.get("problems", []) or [])
        if bool(page_record.get("unreadable")):
            problems = sorted({*problems, "unreadable"})
        page_sha256 = page_record.get("page_sha256")
        require(
            isinstance(page_sha256, str) and len(page_sha256) == 64,
            "integrity",
            f"workbook page {number} was inspected without a page hash",
        )
        image_path = page_record.get("image_path")
        require(
            isinstance(image_path, str) and bool(image_path),
            "integrity",
            f"workbook page {number} was inspected without a rendered page image",
        )
        inspections.append(
            {
                "key": f"workbook/{pdf_sha256}/{number}",
                "pdf_sha256": pdf_sha256,
                "page": number,
                "page_sha256": page_sha256,
                "image_path": image_path,
                "problems": problems,
                "result": "PASS" if not problems else "FAIL",
            }
        )
        if problems:
            findings.append(
                {
                    "component": "layout",
                    "check_id": "workbook_page_inspection",
                    "pointer": f"/assembly/pages/{number}",
                    "message": f"workbook page {number} failed inspection: {problems}",
                }
            )

    check = check_record(
        scope="workbook",
        owner=WORKBOOK_STREAM,
        head_hash=pdf_sha256,
        check_id="workbook_pages_inspected",
        attempt=version.get("version", 1),
        result="PASS" if not findings else "FAIL",
        detail={"page_count": len(pages), "finding_count": len(findings)},
    )

    value = "workbook_pages_inspected" if not findings else "workbook_layout_repairable"
    return {
        "workbook_page_inventories": [inventory],
        "workbook_page_inspections": inspections,
        "deterministic_checks": [check],
        "pending_guard": _guard(
            "D26_RENDER_INVENTORY_INSPECT_WORKBOOK", value, findings=findings
        ),
    }


# --------------------------------------------------------------------------
# D27_FREEZE_WORKBOOK_REVIEW_PACKET
# --------------------------------------------------------------------------


def D27_FREEZE_WORKBOOK_REVIEW_PACKET(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Freeze the immutable workbook review packet, exactly every page included."""

    head = (state.get("workbook_head") or {}).get(WORKBOOK_STREAM)
    require(isinstance(head, Mapping), "invalid_input", "D27 requires an assembled workbook head")
    version = _latest_workbook_version(state.get("workbook_versions"), head["hash"])
    require(isinstance(version, Mapping), "integrity", "no admitted workbook version matches the current head")
    body = version["body"]

    inventories = [
        record
        for record in state.get("workbook_page_inventories") or []
        if isinstance(record, Mapping) and record.get("pdf_sha256") == body["assembly"]["workbook_pdf_sha256"]
    ]
    require(bool(inventories), "invalid_input", "D27 requires a current workbook page inventory")
    inventory = max(inventories, key=lambda record: record.get("page_count", 0))
    pdf_sha256 = inventory["pdf_sha256"]

    inspections = sorted(
        (
            record
            for record in state.get("workbook_page_inspections") or []
            if isinstance(record, Mapping) and record.get("pdf_sha256") == pdf_sha256
        ),
        key=lambda record: record.get("page", 0),
    )
    page_numbers = [record.get("page") for record in inspections]
    require(
        page_numbers == list(range(1, inventory["page_count"] + 1)),
        "join",
        "the frozen packet's page set is not exactly the inventory's pages",
        expected=inventory["page_count"],
        actual=page_numbers,
    )

    pdf_path = Path(str(body["assembly"]["workbook_pdf_path"]))
    require(pdf_path.is_file(), "integrity", "the shipped workbook PDF is missing")
    actual = sha256_file(pdf_path)
    require(
        actual == pdf_sha256,
        "integrity",
        "the shipped workbook PDF bytes do not match the inventoried hash",
    )

    checks = [
        record
        for record in state.get("deterministic_checks") or []
        if isinstance(record, Mapping) and record.get("scope") == "workbook"
    ]

    rubric_path = Path(str(state.get("engine_root"))) / "meta_prompt" / "assets" / "pedagogy.v1.md"
    rubric = {"path": str(rubric_path), "sha256": sha256_file(rubric_path) if rubric_path.is_file() else None}
    require(rubric["sha256"] is not None, "schema_contract", "the workbook review rubric is missing")

    coverage_entries = [
        record for record in state.get("workbook_coverage") or [] if isinstance(record, Mapping)
    ]
    require(bool(coverage_entries), "invalid_input", "D27 requires a proven coverage record")
    coverage = coverage_entries[-1]

    packet = {
        "coverage_map": {
            "ordered_unit_ids": list(coverage["ordered_unit_ids"]),
            "receipt_hashes": dict(coverage["receipt_hashes"]),
        },
        "accepted_unit_hashes": dict(body["coverage"]["unit_pdf_hashes"]),
        "workbook_pdf_sha256": pdf_sha256,
        "page_count": inventory["page_count"],
        "page_keys": [record["key"] for record in inspections],
        "deterministic_check_keys": sorted(
            f"{record['scope']}/{record['owner']}/{record['head_hash']}/{record['check_id']}/{record['attempt']}"
            for record in checks
        ),
        "rubric": rubric,
    }
    packet["denominator"] = {"pages": inventory["page_count"], "checks": len(packet["deterministic_check_keys"])}
    packet["key"] = canonical_digest(packet)
    packet["packet_hash"] = packet["key"]

    page_records = []
    for record in inspections:
        page_records.append(
            {
                "page_number": record["page"],
                "page_sha256": record["page_sha256"],
                "image_path": record["image_path"],
            }
        )

    review_worker_packet = worker_packet(
        run_id=state.get("run_id"),
        episode_id=state.get("episode_id"),
        correlation_key=f"workbook/{pdf_sha256}/review",
        projection={
            "coverage_map": dict(packet["coverage_map"]),
            "accepted_unit_hashes": dict(packet["accepted_unit_hashes"]),
            "workbook_pdf": {"sha256": pdf_sha256, "path": str(pdf_path)},
            "page_inventory": {
                "page_count": inventory["page_count"],
                "pages": [
                    {"page_number": entry["page_number"], "page_sha256": entry["page_sha256"]}
                    for entry in page_records
                ],
            },
            "pages": page_records,
            "deterministic_evidence": [
                {
                    "check_id": record["check_id"],
                    "scope": record["scope"],
                    "head_hash": record["head_hash"],
                    "result": record["result"],
                }
                for record in checks
            ],
            "rubric": dict(rubric),
        },
    )

    return {
        "workbook_review_packets": [packet],
        "pending_packet": staged_dispatch("M07_REVIEW_ACTUAL_WORKBOOK", [review_worker_packet]),
        "pending_guard": _guard("D27_FREEZE_WORKBOOK_REVIEW_PACKET", "workbook_packet_frozen"),
    }


# --------------------------------------------------------------------------
# Denominator (shared shape by D28 and D32 -- spec section 13.2)
# --------------------------------------------------------------------------


class WorkbookDenominatorResult:
    __slots__ = ("passed", "check", "findings", "denominator")

    def __init__(
        self,
        passed: bool,
        check: dict[str, Any],
        findings: list[dict[str, Any]],
        denominator: dict[str, Any],
    ) -> None:
        self.passed = passed
        self.check = check
        self.findings = findings
        self.denominator = denominator


def compute_workbook_denominator(state: Mapping[str, Any]) -> WorkbookDenominatorResult:
    """Recompute the complete current workbook denominator (spec section 13.2).

    Never trusts a cached pass label: every category below is re-derived from
    the *current* state on every call, exactly as `acceptance
    .compute_unit_denominator` does for a unit -- a stale head, a superseded
    review, or an unresolved workbook repair request all fail this function
    freshly regardless of what an earlier call over older state returned.
    """

    findings: list[dict[str, Any]] = []
    categories: dict[str, Any] = {}

    def _fail(component: str, check_id: str, pointer: str, message: str) -> None:
        findings.append({"check_id": check_id, "component": component, "pointer": pointer, "message": message})

    effective_run = state.get("effective_run") or {}
    ordered = list(effective_run.get("ordered_unit_ids") or [])
    accepted = state.get("accepted_unit_receipts") or {}
    coverage_entries = [record for record in state.get("workbook_coverage") or [] if isinstance(record, Mapping)]
    coverage = coverage_entries[-1] if coverage_entries else None

    coverage_ok = (
        coverage is not None
        and list(coverage.get("ordered_unit_ids") or []) == ordered
        and bool(ordered)
        and all(
            isinstance(accepted.get(unit_id), Mapping)
            and accepted[unit_id].get("receipt_hash") == coverage.get("receipt_hashes", {}).get(unit_id)
            for unit_id in ordered
        )
    )
    categories["coverage"] = {"result": "PASS" if coverage_ok else "FAIL"}
    if not coverage_ok:
        _fail("assembly", "workbook_coverage", "/coverage", "current coverage is not exact ordered full-manifest membership")

    head = (state.get("workbook_head") or {}).get(WORKBOOK_STREAM)
    version = _latest_workbook_version(state.get("workbook_versions"), head["hash"]) if isinstance(head, Mapping) else None
    unit_bytes_ok = coverage_ok and version is not None
    if unit_bytes_ok:
        for unit_id, pdf_sha256 in version["body"]["coverage"]["unit_pdf_hashes"].items():
            receipt = accepted.get(unit_id)
            if not isinstance(receipt, Mapping) or ((receipt.get("denominator") or {}).get("pages") or {}).get("pdf_sha256") != pdf_sha256:
                unit_bytes_ok = False
                break
    categories["unit_bytes"] = {"result": "PASS" if unit_bytes_ok else "FAIL"}
    if not unit_bytes_ok:
        _fail("assembly", "workbook_unit_bytes", "/assembly", "an accepted unit's PDF bytes are not the assembled workbook's frozen bytes")

    pdf_sha256 = version["body"]["assembly"]["workbook_pdf_sha256"] if version is not None else None
    inventories = [
        record
        for record in state.get("workbook_page_inventories") or []
        if isinstance(record, Mapping) and record.get("pdf_sha256") == pdf_sha256
    ]
    inventory = max(inventories, key=lambda record: record.get("page_count", 0)) if inventories else None
    inventory_ok = isinstance(inventory, Mapping) and inventory.get("result") == "PASS"
    inspections = [
        record
        for record in state.get("workbook_page_inspections") or []
        if isinstance(record, Mapping) and record.get("pdf_sha256") == pdf_sha256
    ]
    expected_pages = inventory.get("page_count") if isinstance(inventory, Mapping) else -1
    pages_ok = inventory_ok and len(inspections) == expected_pages and all(record.get("result") == "PASS" for record in inspections)
    categories["pages"] = {"result": "PASS" if pages_ok else "FAIL", "pdf_sha256": pdf_sha256, "page_count": expected_pages}
    if not pages_ok:
        _fail("layout", "workbook_pages", "/assembly/pages", "the workbook page inventory/inspection set is not current and fully passing")

    review = _latest_workbook_review(state.get("workbook_reviews"), pdf_sha256)
    review_ok = review is not None
    if review is not None:
        payload = candidate_payload(review, "workbook review")
        blocking = [
            entry for entry in payload.get("overall_findings", [])
            if isinstance(entry, Mapping) and entry.get("severity") == "blocking"
        ]
        for page_entry in payload.get("page_findings", []):
            if isinstance(page_entry, Mapping):
                blocking.extend(
                    entry for entry in page_entry.get("findings", [])
                    if isinstance(entry, Mapping) and entry.get("severity") == "blocking"
                )
        for entry in blocking:
            component = str(entry.get("category") or "layout")
            component = component if component in WORKBOOK_OWNED_COMPONENTS else "layout"
            findings.append(
                {
                    "check_id": "workbook_review_finding",
                    "component": component,
                    "pointer": entry.get("evidence_reference") or "/review",
                    "message": entry.get("description", ""),
                }
            )
        review_ok = not blocking
    categories["review"] = {"result": "PASS" if review_ok else "FAIL", "present": review is not None}
    if review is None:
        _fail("navigation", "workbook_review_missing", "/review", "no independent workbook review candidate is present for the current pdf")

    open_requests = [
        record
        for record in state.get("workbook_repair_requests") or []
        if isinstance(record, Mapping)
        and record.get("key")
        not in {
            entry.get("request_key")
            for entry in state.get("workbook_retests") or []
            if isinstance(entry, Mapping) and entry.get("resolved")
        }
    ]
    repair_ok = not open_requests
    categories["repair"] = {"result": "PASS" if repair_ok else "FAIL", "open_requests": len(open_requests)}
    if not repair_ok:
        _fail(open_requests[0]["component"], "workbook_repair_unresolved", "/repair", "a workbook repair request remains open (not yet retested)")

    passed = all(entry.get("result") == "PASS" for entry in categories.values())
    summary_hash = canonical_digest({"kind": "workbook_denominator", "categories": categories})
    check = check_record(
        scope="workbook",
        owner=WORKBOOK_STREAM,
        head_hash=summary_hash,
        check_id="workbook_denominator",
        attempt=1,
        result="PASS" if passed else "FAIL",
        detail={"categories": categories},
    )
    return WorkbookDenominatorResult(passed, check, findings, categories)


# --------------------------------------------------------------------------
# D28_REDUCE_WORKBOOK_EVIDENCE
# --------------------------------------------------------------------------


def D28_REDUCE_WORKBOOK_EVIDENCE(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Build the complete current workbook denominator; release, or open repair."""

    result = compute_workbook_denominator(state)
    if result.passed:
        return {
            "deterministic_checks": [result.check],
            "pending_guard": _guard("D28_REDUCE_WORKBOOK_EVIDENCE", "workbook_denominator_passed"),
        }
    return {
        "deterministic_checks": [result.check],
        "pending_guard": _guard(
            "D28_REDUCE_WORKBOOK_EVIDENCE", "workbook_findings_repairable", findings=result.findings
        ),
    }


# --------------------------------------------------------------------------
# D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR
# --------------------------------------------------------------------------


def D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Classify the current workbook-only findings and plan exactly one repair.

    Merges spec 6.2's D17/D18/D19 roles into the one row the workbook branch
    declares: total classification, one planned request, and deterministic-vs-
    model routing, all against the single `WORKBOOK_OWNED_COMPONENTS`
    vocabulary rather than the five-owner unit table.
    """

    guard_record = state.get("pending_guard")
    pending_failure = state.get("pending_failure")

    if isinstance(pending_failure, Mapping) and pending_failure.get("classification") == "repair":
        detail = pending_failure.get("evidence") if isinstance(pending_failure.get("evidence"), Mapping) else {}
        raw_findings = [
            {
                "component": "front_matter",
                "check_id": pending_failure.get("failure_class"),
                "pointer": "/front_matter",
                "message": pending_failure.get("detail") or pending_failure.get("message") or "",
            }
        ]
        source_node = "D91_CLASSIFY_MODEL_FAILURE"
    else:
        require(isinstance(guard_record, Mapping), "invalid_input", "D29 has no findings to classify")
        detail = guard_record.get("detail") if isinstance(guard_record.get("detail"), Mapping) else {}
        raw_findings = detail.get("findings")
        require(
            isinstance(raw_findings, list) and bool(raw_findings),
            "invalid_input",
            "D29 was routed with an empty or missing findings list",
        )
        source_node = str(guard_record.get("node") or "")

    normalized: list[dict[str, Any]] = []
    for raw in raw_findings:
        raw_record = _record(raw, "workbook finding")
        component = raw_record.get("component")
        require(
            component in WORKBOOK_OWNED_COMPONENTS,
            "invalid_input",
            f"workbook finding declares component {component!r}, which is not one of the four workbook-owned components",
        )
        pointer = raw_record.get("pointer")
        require(isinstance(pointer, str) and bool(pointer), "invalid_input", "workbook finding declares no boundary pointer")
        message = raw_record.get("message", "")
        normalized.append(
            {
                "finding_id": canonical_digest({"component": component, "pointer": pointer, "message": str(message)}),
                "component": component,
                "boundary": pointer,
                "message": str(message),
                "source_node": source_node,
            }
        )

    fingerprint = repair.finding_fingerprint(
        normalized[0]["component"], sorted(f["boundary"] for f in normalized), sorted(f["message"] for f in normalized)
    )
    counters = dict(state.get("attempt_counters") or {})
    repeat_key = _repeat_key(fingerprint)
    prior_repeats = int(counters.get(repeat_key, 0))
    if prior_repeats >= MAX_FINGERPRINT_REPEATS:
        return {
            "workbook_finding_partitions": [
                {
                    "key": canonical_digest({"fingerprint": fingerprint, "kind": "exhausted"}),
                    "component": normalized[0]["component"],
                    "findings": normalized,
                    "fingerprint": fingerprint,
                }
            ],
            "pending_guard": _guard("D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR", "convergence_exhausted", fingerprint=fingerprint),
            "terminal_candidate": {
                "kind": "CONVERGENCE_EXHAUSTED",
                "bound": "fingerprint_bound",
                "counters": counters,
                "fingerprints": [{"component": normalized[0]["component"], "fingerprint": fingerprint, "bound": "fingerprint_bound", "repeats": prior_repeats}],
                "last_findings": normalized,
            },
        }

    attempt_key = _attempt_key(fingerprint)
    ordinal = int(counters.get(attempt_key, 0)) + 1
    if ordinal > MAX_REPAIR_CHILDREN_PER_CHAIN:
        return {
            "pending_guard": _guard("D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR", "convergence_exhausted", ordinal=ordinal),
            "terminal_candidate": {
                "kind": "CONVERGENCE_EXHAUSTED",
                "bound": "attempt_bound",
                "counters": counters,
                "fingerprints": [fingerprint],
                "last_findings": normalized,
            },
        }

    component = normalized[0]["component"]
    # The granted repair boundary is the component's own body section, not the
    # (possibly page-level) finding pointer that triggered classification: a
    # `layout`/`assembly` re-render legitimately changes every field under
    # `/assembly` (the PDF hash included), and a boundary narrower than that
    # would make `D31`'s own admission check reject the very repair D29 just
    # authorized.
    boundary_pointers = [_COMPONENT_BODY_POINTER[component]]
    head = (state.get("workbook_head") or {}).get(WORKBOOK_STREAM)
    require(isinstance(head, Mapping), "invalid_input", "D29 requires a current workbook head")

    request = {
        "key": canonical_digest({"fingerprint": fingerprint, "attempt": ordinal}),
        "component": component,
        "finding_ids": [f["finding_id"] for f in normalized],
        "boundary": {"json_pointers": boundary_pointers},
        "parent_hash": head["hash"],
        "attempt_ordinal": ordinal,
        "fingerprint": fingerprint,
        "prior_repeats": prior_repeats,
    }

    partition = {
        "key": canonical_digest({"fingerprint": fingerprint, "kind": "partition"}),
        "component": component,
        "findings": normalized,
        "fingerprint": fingerprint,
    }

    accepted = state.get("accepted_unit_receipts") or {}
    version = _latest_workbook_version(state.get("workbook_versions"), head["hash"])
    require(isinstance(version, Mapping), "integrity", "no admitted workbook version matches the current head")
    accepted_unit_hashes = dict(version["body"]["coverage"]["unit_pdf_hashes"])

    update: dict[str, Any] = {
        "attempt_counters": {attempt_key: ordinal},
        "workbook_finding_partitions": [partition],
        "workbook_repair_requests": [request],
    }

    if component in DETERMINISTIC_ONLY_COMPONENTS:
        # Both deterministic-only components (`layout`, the rendered page set,
        # and `assembly`, the workbook PDF itself) are re-derived by
        # re-rendering `body["assembly"]` from the *unchanged* accepted unit
        # hashes; neither ever touches `body["coverage"]`, which is the one
        # section a workbook repair boundary must never name (spec section
        # 12: workbook repair cannot stage a writable unit source or PDF).
        new_body = dict(version["body"])
        new_body["assembly"] = {**version["body"]["assembly"], "repaired": True, "repaired_component": component}
        candidate = {
            "key": canonical_digest({"request_key": request["key"], "kind": "deterministic_candidate"}),
            "record_kind": DETERMINISTIC_REPAIR_CANDIDATE_KIND,
            "request_key": request["key"],
            "component": component,
            "parent_sha256": head["hash"],
            "body": new_body,
        }
        update["workbook_versions"] = [candidate]
        update["pending_guard"] = _guard(
            "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR", "deterministic_repair", request_key=request["key"]
        )
        return update

    require(component in MODEL_ONLY_COMPONENTS, "integrity", f"component {component!r} has no dispatch rule")
    packet = worker_packet(
        run_id=state.get("run_id"),
        episode_id=state.get("episode_id"),
        correlation_key=f"{request['key']}/M08",
        projection={
            "defect": {
                "defect_id": request["key"],
                "component": component,
                "findings": [
                    {"finding_id": f["finding_id"], "pointer": f["boundary"], "message": f["message"]}
                    for f in normalized
                ],
            },
            "parent": {
                "artifact_name": f"workbook:{component}",
                "artifact_body": canonical_digest(version["body"]),
                "parent_sha256": head["hash"],
            },
            "allowed_files": {"files": [f"{component}.json"]},
            "accepted_unit_hashes": accepted_unit_hashes,
            "workbook_pdf_hash": version["body"]["assembly"]["workbook_pdf_sha256"],
            "invalidated_descendants": ["D26_RENDER_INVENTORY_INSPECT_WORKBOOK"],
            "retest_order": ["D26_RENDER_INVENTORY_INSPECT_WORKBOOK"],
        },
    )
    update["pending_packet"] = staged_dispatch("M08_REPAIR_NAMED_WORKBOOK_DEFECT", [packet])
    update["pending_guard"] = _guard(
        "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR", "model_repair", request_key=request["key"]
    )
    return update


# --------------------------------------------------------------------------
# D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR
# --------------------------------------------------------------------------


def D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Admit a boundary-checked workbook child, or refuse it as a system fault.

    Recomputes the parent/child diff itself and, before anything else, proves
    every accepted unit's frozen PDF hash the parent named is still exactly
    the hash the child names: workbook repair can never stage a writable unit
    source or PDF (spec section 12), so any unit-hash drift here is always
    `SystemFailure`, never a routed finding.
    """

    requests = [record for record in state.get("workbook_repair_requests") or [] if isinstance(record, Mapping)]
    require(bool(requests), "invalid_input", "D31 requires a routed repair request")
    request = requests[-1]
    boundary = request["boundary"]["json_pointers"]

    head = (state.get("workbook_head") or {}).get(WORKBOOK_STREAM)
    require(isinstance(head, Mapping), "invalid_input", "D31 requires a current workbook head")
    parent_version = _latest_workbook_version(state.get("workbook_versions"), head["hash"])
    require(isinstance(parent_version, Mapping), "integrity", "no admitted workbook version matches the current head")
    parent_body = parent_version["body"]

    model_candidate = _latest_model_repair_candidate(state.get("workbook_versions"))
    deterministic_candidate = _latest_deterministic_repair_candidate(
        state.get("workbook_versions"), request_key=request["key"]
    )
    require(
        (model_candidate is not None) != (deterministic_candidate is not None),
        "join",
        "D31 requires exactly one pending repair candidate: model or deterministic",
    )

    if model_candidate is not None:
        payload = candidate_payload(model_candidate, "M08 repair candidate")
        child = payload.get("candidate_child")
        require(isinstance(child, Mapping), "schema_contract", "M08 candidate carries no candidate_child")
        component = request["component"]
        new_body = dict(parent_body)
        new_body[component] = {**parent_body[component], "repaired_by": "M08", "addressed_defect_id": child.get("addressed_defect_id")}
        declared_parent_sha = model_candidate.get("parent_sha256")
    else:
        new_body = deterministic_candidate["body"]
        declared_parent_sha = deterministic_candidate.get("parent_sha256")

    require(
        declared_parent_sha == head["hash"],
        "integrity",
        "the repair candidate's declared parent is not the current workbook head (stale repair)",
        declared=declared_parent_sha,
        current=head["hash"],
    )

    # The unit-hash immutability guard: recomputed before anything else is
    # admitted, over the *actual* current accepted receipts, never the
    # candidate's own claim.
    accepted = state.get("accepted_unit_receipts") or {}
    for unit_id, pdf_sha256 in parent_body["coverage"]["unit_pdf_hashes"].items():
        receipt = accepted.get(unit_id)
        current_pdf = _accepted_pdf_hash(receipt, unit_id) if isinstance(receipt, Mapping) else None
        require(
            current_pdf == pdf_sha256,
            "integrity",
            "workbook repair observed a changed accepted unit hash",
            unit_id=unit_id,
        )
    child_pdf_hashes = new_body.get("coverage", {}).get("unit_pdf_hashes", {})
    require(
        dict(child_pdf_hashes) == dict(parent_body["coverage"]["unit_pdf_hashes"]),
        "integrity",
        "a workbook repair candidate changed an accepted unit's hash",
        parent=parent_body["coverage"]["unit_pdf_hashes"],
        child=child_pdf_hashes,
    )

    diff = repair.json_pointer_diff(parent_body, new_body)
    require(bool(diff), "integrity", "a workbook repair candidate makes no change (in-place, no-op repair)")
    out_of_bound = sorted(pointer for pointer in diff if not repair.within_boundary(pointer, boundary))
    require(
        not out_of_bound,
        "integrity",
        "a workbook repair candidate changed bytes outside its declared boundary",
        out_of_bound=out_of_bound,
        boundary=boundary,
    )

    child_record = {
        "key": canonical_digest({"kind": "workbook_version", "body": new_body, "parent": head["hash"]}),
        "record_kind": None,
        "version": int(head["version"]) + 1,
        "parent_hash": head["hash"],
        "hash": canonical_digest(new_body),
        "body": new_body,
        "request_key": request["key"],
        "component": request["component"],
    }

    retest = {
        "key": canonical_digest({"request_key": request["key"], "kind": "workbook_retest"}),
        "request_key": request["key"],
        "component": request["component"],
        "destination": "D26_RENDER_INVENTORY_INSPECT_WORKBOOK",
        "resolved": True,
    }

    return {
        "workbook_versions": [child_record],
        "workbook_head": {
            WORKBOOK_STREAM: {
                "version": child_record["version"],
                "parent_hash": child_record["parent_hash"],
                "hash": child_record["hash"],
            }
        },
        "workbook_retests": [retest],
        "pending_guard": _guard(
            "D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR", "workbook_repair_admitted", request_key=request["key"]
        ),
    }


# --------------------------------------------------------------------------
# D32_RECOMPUTE_FINAL_RELEASE
# --------------------------------------------------------------------------


def D32_RECOMPUTE_FINAL_RELEASE(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Recompute the final release audit against current bytes; release, or repair.

    Never trusts D28's earlier pass label -- a retest that changed a head, or
    an accepted receipt that went stale, between D28 and D32 makes this
    recomputation fail even though D28 once passed. Only D32 can authorize
    `COMPLETE`, and it does so from freshly recomputed evidence (spec section
    13.2's closing sentence).
    """

    result = compute_workbook_denominator(state)
    audit = {
        "key": canonical_digest({"kind": "final_release_audit", "categories": result.denominator}),
        "result": "PASS" if result.passed else "FAIL",
        "categories": result.denominator,
    }

    if not result.passed:
        return {
            "final_release_audits": [audit],
            "deterministic_checks": [result.check],
            "pending_guard": _guard(
                "D32_RECOMPUTE_FINAL_RELEASE", "workbook_repairable", findings=result.findings
            ),
        }

    head = (state.get("workbook_head") or {}).get(WORKBOOK_STREAM)
    version = _latest_workbook_version(state.get("workbook_versions"), head["hash"])
    effective_run = state.get("effective_run") or {}
    ordered = list(effective_run.get("ordered_unit_ids") or [])
    accepted = state.get("accepted_unit_receipts") or {}
    checkpoints = state.get("checkpoint_metadata") or []
    require(bool(checkpoints), "integrity", "D32 requires a current checkpoint correlation")

    audit = {**audit, "workbook_hash": head["hash"]}
    candidate = {
        "kind": "COMPLETE",
        "release_audit_key": audit["key"],
        "workbook_hash": head["hash"],
        "coverage": {"ordered_unit_ids": ordered, "unit_pdf_hashes": version["body"]["coverage"]["unit_pdf_hashes"]},
        "unit_receipt_hashes": {unit_id: accepted[unit_id]["receipt_hash"] for unit_id in ordered},
        "log_high_water_mark": len(state.get("evidence_index_entries") or []),
        "checkpoint_id": checkpoints[-1].get("checkpoint_id"),
    }

    return {
        "final_release_audits": [audit],
        "deterministic_checks": [result.check],
        "terminal_candidate": candidate,
        "pending_guard": _guard("D32_RECOMPUTE_FINAL_RELEASE", "release_proven"),
    }


# --------------------------------------------------------------------------
# Topology registration (spec section 8.1's workbook branch)
# --------------------------------------------------------------------------
#
# Additive registration over the one builder N20/N30 already populated, in the
# same convention `unit_graph.register_unit_path` uses: no `add_node`, no
# `StateGraph()`, no `compile()`. D90/D91 are deliberately absent from this
# module's own `add_conditional_edges` calls -- both are shared bookkeeping
# nodes `unit_graph.py` already registers a branch for, and re-registering the
# same source under a different branch name would double-fire on every
# execution (LangGraph attaches every branch of a node as an independent
# writer). `D90`'s dispatch to `M07`/`M08` reaches them anyway: the guard
#(`routing.route_attempt_reservation`) returns `Send` objects for an
# authorized dispatch, and a `Send` target bypasses the registered branch's
# `path_map` entirely, so the pre-existing narrower `ends` unit_graph.py froze
# never has to name a workbook job to reach one.


WORKBOOK_NODE_BODIES: Mapping[str, Any] = {
    "D24_PROVE_EXACT_MANIFEST_COVERAGE": D24_PROVE_EXACT_MANIFEST_COVERAGE,
    "D25_ASSEMBLE_WORKBOOK": D25_ASSEMBLE_WORKBOOK,
    "D26_RENDER_INVENTORY_INSPECT_WORKBOOK": D26_RENDER_INVENTORY_INSPECT_WORKBOOK,
    "D27_FREEZE_WORKBOOK_REVIEW_PACKET": D27_FREEZE_WORKBOOK_REVIEW_PACKET,
    "D28_REDUCE_WORKBOOK_EVIDENCE": D28_REDUCE_WORKBOOK_EVIDENCE,
    "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR": D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR,
    "D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR": D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR,
    "D32_RECOMPUTE_FINAL_RELEASE": D32_RECOMPUTE_FINAL_RELEASE,
}


def _routing() -> Any:
    from . import routing

    return routing


# (source node id, guard callable name on `routing`) -- resolved lazily via
# `_routing()` so this module does not import `routing` at module scope
# (avoiding a cycle is unnecessary here, but keeping the same lazy-import
# convention `unit_graph.py`/`acceptance.py` already use for cross-module
# helpers keeps this file's import graph uniform).
WORKBOOK_TOPOLOGY_SOURCES: tuple[str, ...] = (
    "D24_PROVE_EXACT_MANIFEST_COVERAGE",
    "D25_ASSEMBLE_WORKBOOK",
    "D26_RENDER_INVENTORY_INSPECT_WORKBOOK",
    "D27_FREEZE_WORKBOOK_REVIEW_PACKET",
    "D28_REDUCE_WORKBOOK_EVIDENCE",
    "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR",
    "D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR",
    "D32_RECOMPUTE_FINAL_RELEASE",
    "M07_REVIEW_ACTUAL_WORKBOOK",
    "M08_REPAIR_NAMED_WORKBOOK_DEFECT",
)


def register_workbook_path(builder: Any, available: Sequence[str]) -> dict[str, tuple[str, ...]]:
    """Add the workbook branch's own outgoing edges to the shared builder.

    Called by `graph.py` after `unit_graph.register_unit_path`, over the same
    `StateGraph` instance -- every node this module names as a source must
    already be `add_node`-registered by the caller. Returns the resolved
    per-source destination map so a caller can assert the registered topology
    the way `unit_graph.register_unit_path` already does.
    """

    routing = _routing()
    available_set = set(available)
    for node_id in WORKBOOK_TOPOLOGY_SOURCES:
        if node_id not in available_set:
            raise routing.RoutingViolation(
                f"N32-EDGE-DANGLING:{node_id}: the workbook path names a node with no registered body"
            )

    guards: dict[str, Any] = {
        "D24_PROVE_EXACT_MANIFEST_COVERAGE": routing.route_manifest_coverage,
        "D25_ASSEMBLE_WORKBOOK": routing.route_workbook_assembly,
        "D26_RENDER_INVENTORY_INSPECT_WORKBOOK": routing.route_workbook_inspection,
        "D27_FREEZE_WORKBOOK_REVIEW_PACKET": routing.route_workbook_packet,
        "D28_REDUCE_WORKBOOK_EVIDENCE": routing.route_workbook_reduction,
        "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR": routing.route_workbook_repair_plan,
        "D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR": routing.route_workbook_repair_admission,
        "D32_RECOMPUTE_FINAL_RELEASE": routing.route_final_release,
        "M07_REVIEW_ACTUAL_WORKBOOK": routing.route_m07_workbook_review,
        "M08_REPAIR_NAMED_WORKBOOK_DEFECT": routing.route_m08_workbook_repair,
    }

    # `routing.guard_destinations()` resolves a *deterministic* node's own
    # `GUARD_DESTINATIONS` row, which D24-D32 all have. M07/M08 are model
    # *result* sources instead: their success destination lives in
    # `routing.MODEL_RESULT_DESTINATIONS`, a table `guard_destinations()`
    # does not consult (the same reason `unit_graph.py` declares M01/M02/M03/
    # M05's destinations explicitly rather than deriving them generically).
    model_result_extra: Mapping[str, tuple[str, ...]] = {
        "M07_REVIEW_ACTUAL_WORKBOOK": (routing.MODEL_RESULT_DESTINATIONS["M07_REVIEW_ACTUAL_WORKBOOK"],),
        "M08_REPAIR_NAMED_WORKBOOK_DEFECT": (routing.MODEL_RESULT_DESTINATIONS["M08_REPAIR_NAMED_WORKBOOK_DEFECT"],),
    }

    resolved: dict[str, tuple[str, ...]] = {}
    for source in WORKBOOK_TOPOLOGY_SOURCES:
        path = guards[source]
        declared = set(routing.guard_destinations(source)) | set(model_result_extra.get(source, ()))
        destinations = tuple(sorted(declared & available_set))
        if not destinations:
            raise routing.RoutingViolation(f"N32-EDGE-EMPTY:{source}: every declared destination is deferred")
        builder.add_conditional_edges(source, path, {target: target for target in destinations})
        resolved[source] = destinations
    return resolved
