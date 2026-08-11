"""Unit review-packet freeze.

Owns D15. The packet is the exact, immutable set of bytes the independent
reviewer will see. Freezing it here — rather than letting the review node gather
its own inputs — is what makes the review's denominator checkable afterwards.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import (
    canonical_digest,
    deterministic_node,
    guard,
    latest_candidate,
    require,
    sha256_file as _sha256_file,
    staged_dispatch,
    stream_id,
    worker_packet,
)

__all__ = ["PACKET_ARTIFACT_CHANNELS", "D15_FREEZE_UNIT_REVIEW_PACKET"]


PACKET_ARTIFACT_CHANNELS: tuple[str, ...] = ("domain", "content", "visuals", "layout")


@deterministic_node("D15_FREEZE_UNIT_REVIEW_PACKET")
def D15_FREEZE_UNIT_REVIEW_PACKET(
    projection: dict[str, Any], runtime_context: Any
) -> dict[str, Any]:
    """Freeze the immutable review packet, its denominator, and its hash."""

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")

    heads = projection["artifact_heads"]
    artifact_hashes: dict[str, str] = {}
    for channel in PACKET_ARTIFACT_CHANNELS:
        head = heads.get(stream_id(unit_id, channel))
        require(
            isinstance(head, dict),
            "invalid_input",
            f"the review packet requires an admitted {channel} head",
            unit_id=unit_id,
        )
        artifact_hashes[channel] = head["hash"]

    inventories = [
        record
        for record in projection["unit_page_inventories"]
        if isinstance(record, dict) and record.get("unit_id") == unit_id
    ]
    require(bool(inventories), "invalid_input", "the review packet requires a page inventory")
    inventory = max(inventories, key=lambda record: record.get("page_count", 0))
    pdf_sha256 = inventory["pdf_sha256"]

    inspections = sorted(
        (
            record
            for record in projection["unit_page_inspections"]
            if isinstance(record, dict)
            and record.get("unit_id") == unit_id
            and record.get("pdf_sha256") == pdf_sha256
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

    # The packet names the shipped PDF, so its bytes must still be the bytes the
    # inventory measured; a packet built over a re-rendered PDF would send the
    # reviewer one document and the denominator another.
    layout_version = latest_candidate(projection["artifact_versions"], stream_id(unit_id, "layout"))
    if layout_version is not None and layout_version.get("pdf_path"):
        pdf_path = Path(str(layout_version["pdf_path"]))
        require(pdf_path.is_file(), "integrity", "the shipped unit PDF is missing")
        actual = _sha256_file(pdf_path)
        require(
            actual == pdf_sha256,
            "integrity",
            "the shipped PDF's bytes do not match the inventoried PDF hash",
            declared=pdf_sha256,
            actual=actual,
        )

    checks = [
        record
        for record in projection["deterministic_checks"]
        if isinstance(record, dict) and record.get("owner") == unit_id
    ]
    admissions = [
        record
        for record in projection["source_admissions"]
        if isinstance(record, dict) and record.get("unit_id") == unit_id
    ]

    rubric_path = Path(projection["engine_root"]) / "meta_prompt" / "assets" / "pedagogy.v1.md"
    rubric = {
        "path": str(rubric_path),
        "sha256": _sha256_file(rubric_path) if rubric_path.is_file() else None,
    }
    require(
        rubric["sha256"] is not None,
        "schema_contract",
        "the review rubric is missing from the engine root",
        path=str(rubric_path),
    )

    packet = {
        "unit_id": unit_id,
        "artifact_hashes": artifact_hashes,
        "pdf_sha256": pdf_sha256,
        "page_count": inventory["page_count"],
        "page_keys": [record["key"] for record in inspections],
        "deterministic_check_keys": sorted(
            f"{record['scope']}/{record['owner']}/{record['head_hash']}/{record['check_id']}/{record['attempt']}"
            for record in checks
        ),
        "admitted_source_keys": sorted(record["key"] for record in admissions),
        "rubric": rubric,
    }
    packet["denominator"] = {
        "pages": inventory["page_count"],
        "artifacts": len(artifact_hashes),
        "checks": len(packet["deterministic_check_keys"]),
        "sources": len(packet["admitted_source_keys"]),
    }
    packet["key"] = canonical_digest(packet)
    packet["packet_hash"] = packet["key"]

    page_records = []
    for record in inspections:
        page_sha256 = record.get("page_sha256")
        image_path = record.get("image_path")
        require(
            isinstance(page_sha256, str) and len(page_sha256) == 64,
            "integrity",
            f"page {record.get('page')} has no hash to freeze into the review denominator",
        )
        require(
            isinstance(image_path, str) and bool(image_path),
            "integrity",
            f"page {record.get('page')} has no rendered image for the reviewer",
        )
        page_records.append(
            {
                "page_number": record["page"],
                "page_sha256": page_sha256,
                "image_path": image_path,
            }
        )

    review_worker_packet = worker_packet(
        run_id=projection["run_id"],
        episode_id=projection["episode_id"],
        correlation_key=f"{unit_id}/{pdf_sha256}/review",
        projection={
            "unit_artifacts": dict(artifact_hashes),
            "unit_pdf": {
                "sha256": pdf_sha256,
                "path": str(layout_version["pdf_path"]) if layout_version else None,
            },
            "page_inventory": {
                "page_count": inventory["page_count"],
                "pages": [
                    {"page_number": entry["page_number"], "page_sha256": entry["page_sha256"]}
                    for entry in page_records
                ],
            },
            "pages": page_records,
            # A reviewer sees which checks ran and how they came out, never how
            # many attempts it took to get there: `attempt` is a denied name.
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
        "review_packets": [packet],
        "pending_packet": staged_dispatch("M05_REVIEW_ACTUAL_UNIT", [review_worker_packet]),
        "pending_guard": guard(
            "D15_FREEZE_UNIT_REVIEW_PACKET", "review_packet_frozen", unit_id=unit_id
        ),
    }
