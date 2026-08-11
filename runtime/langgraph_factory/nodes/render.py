"""Unit rendering and every-page inventory/inspection.

Owns D13 and D14. Between them they turn admitted artifacts into the actual
shipped PDF and then prove, page by page, that the PDF a learner would receive
is the one the evidence describes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import (
    SystemFailure,
    canonical_digest,
    check_record,
    deterministic_node,
    guard,
    latest_candidate,
    require,
    stream_id,
)

__all__ = [
    "RENDER_INPUT_CHANNELS",
    "D13_RENDER_UNIT",
    "D14_INVENTORY_AND_INSPECT_UNIT_PAGES",
]


RENDER_INPUT_CHANNELS: tuple[str, ...] = ("domain", "content", "visuals")


def _record(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), "schema_contract", f"{label} must be a JSON object")
    return dict(value)


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


# --------------------------------------------------------------------------
# D13
# --------------------------------------------------------------------------


@deterministic_node("D13_RENDER_UNIT")
def D13_RENDER_UNIT(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Render one deterministic layout source and unit PDF from the current heads."""

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")

    heads = projection["artifact_heads"]
    parents: dict[str, str] = {}
    for channel in RENDER_INPUT_CHANNELS:
        head = heads.get(stream_id(unit_id, channel))
        require(
            isinstance(head, dict),
            "invalid_input",
            f"rendering requires an admitted {channel} head",
            unit_id=unit_id,
        )
        parents[channel] = head["hash"]

    registry = getattr(runtime_context, "transport_registry", None)
    renderer = getattr(registry, "render_unit", None) if registry else None
    require(callable(renderer), "capability", "runtime context exposes no unit renderer")

    try:
        rendered = renderer(unit_id, parents)
    except Exception as error:  # noqa: BLE001 - a renderer or tool fault is a system failure
        raise SystemFailure(
            "tool",
            f"unit render failed for {unit_id}: {error}",
            {"unit_id": unit_id, "parents": parents},
        ) from error

    result = _record(rendered, f"render result for {unit_id}")
    for field in ("layout_path", "layout_sha256", "pdf_path", "pdf_sha256", "renderer"):
        require(field in result, "integrity", f"render result for {unit_id} has no {field!r}")

    pdf_path = Path(result["pdf_path"])
    require(pdf_path.is_file(), "integrity", "the rendered unit PDF does not exist", path=str(pdf_path))
    actual_pdf = _sha256_file(pdf_path)
    require(
        actual_pdf == result["pdf_sha256"],
        "integrity",
        "the rendered PDF's bytes do not match the renderer's declared hash",
        declared=result["pdf_sha256"],
        actual=actual_pdf,
    )

    layout_stream = stream_id(unit_id, "layout")
    current = heads.get(layout_stream) or {}
    version_record = {
        "key": canonical_digest({"stream": layout_stream, "pdf_sha256": actual_pdf}),
        "stream": layout_stream,
        "version": current.get("version", 0) + 1,
        "parent_hash": current.get("hash"),
        "hash": canonical_digest(
            {"layout": result["layout_sha256"], "pdf": actual_pdf, "parents": parents}
        ),
        "layout_path": result["layout_path"],
        "layout_sha256": result["layout_sha256"],
        "pdf_path": str(pdf_path),
        "pdf_sha256": actual_pdf,
        "parents": parents,
        "renderer": result["renderer"],
        "attempt": int(result.get("attempt", 1)),
    }

    check = check_record(
        scope="unit",
        owner=unit_id,
        head_hash=version_record["hash"],
        check_id="unit_render_receipt",
        attempt=version_record["attempt"],
        result="PASS",
        detail={"renderer": result["renderer"], "pdf_sha256": actual_pdf},
    )

    return {
        "artifact_versions": [version_record],
        "deterministic_checks": [check],
        "pending_guard": guard("D13_RENDER_UNIT", "unit_rendered", unit_id=unit_id),
    }


# --------------------------------------------------------------------------
# D14
# --------------------------------------------------------------------------


@deterministic_node("D14_INVENTORY_AND_INSPECT_UNIT_PAGES")
def D14_INVENTORY_AND_INSPECT_UNIT_PAGES(
    projection: dict[str, Any], runtime_context: Any
) -> dict[str, Any]:
    """Prove a positive contiguous page inventory and inspect every page.

    "Every page" is literal: a per-page result set that skips a page cannot
    support a review denominator that claims to have seen the whole unit.
    """

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")

    layout_stream = stream_id(unit_id, "layout")
    version = latest_candidate(projection["artifact_versions"], layout_stream)
    require(version is not None, "invalid_input", f"no rendered layout version on {layout_stream}")

    pdf_sha256 = version.get("pdf_sha256")
    require(isinstance(pdf_sha256, str) and pdf_sha256, "integrity", "the layout version has no PDF hash")

    pdf_path = Path(str(version.get("pdf_path")))
    require(pdf_path.is_file(), "integrity", "the rendered unit PDF is missing", path=str(pdf_path))
    actual = _sha256_file(pdf_path)
    require(
        actual == pdf_sha256,
        "integrity",
        "the unit PDF's bytes changed after rendering",
        declared=pdf_sha256,
        actual=actual,
    )

    registry = getattr(runtime_context, "transport_registry", None)
    inspector = getattr(registry, "inspect_pages", None) if registry else None
    require(callable(inspector), "capability", "runtime context exposes no page inspector")

    try:
        inspected = inspector(str(pdf_path), pdf_sha256)
    except Exception as error:  # noqa: BLE001 - a rasterizer or tool fault is a system failure
        raise SystemFailure(
            "tool",
            f"page inspection failed for {unit_id}: {error}",
            {"unit_id": unit_id, "pdf_sha256": pdf_sha256},
        ) from error

    report = _record(inspected, f"page inspection for {unit_id}")
    pages = report.get("pages")
    require(isinstance(pages, list), "schema_contract", "page inspection returned a non-list page set")

    attempt = int(version.get("attempt", 1))
    numbers = [page.get("number") for page in pages if isinstance(page, dict)]
    contiguous = numbers == list(range(1, len(pages) + 1))
    positive = len(pages) > 0

    inventory = {
        "key": f"{unit_id}/{pdf_sha256}",
        "unit_id": unit_id,
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
                "check_id": "unit_page_inventory",
                "owner": "unit layout",
                "pointer": "/pages",
                "message": (
                    "page inventory is empty" if not positive else f"page numbering is not 1..N: {numbers}"
                ),
            }
        )

    for page in pages:
        page_record = _record(page, "page inspection entry")
        number = page_record.get("number")
        problems = sorted(str(item) for item in page_record.get("problems", []) or [])
        unreadable = bool(page_record.get("unreadable"))
        if unreadable:
            problems = sorted({*problems, "unreadable"})
        # The review denominator is per page and by hash, so a page this node
        # cannot identify by its own bytes is a page D15 could not freeze.
        page_sha256 = page_record.get("page_sha256")
        require(
            isinstance(page_sha256, str) and len(page_sha256) == 64,
            "integrity",
            f"page {number} was inspected without a page hash",
            unit_id=unit_id,
        )
        image_path = page_record.get("image_path")
        require(
            isinstance(image_path, str) and bool(image_path),
            "integrity",
            f"page {number} was inspected without a rendered page image",
            unit_id=unit_id,
        )
        inspections.append(
            {
                "key": f"{unit_id}/{pdf_sha256}/{number}",
                "unit_id": unit_id,
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
                    "check_id": "unit_page_inspection",
                    "owner": "unit layout",
                    "pointer": f"/pages/{number}",
                    "message": f"page {number} failed inspection: {problems}",
                }
            )

    check = check_record(
        scope="unit",
        owner=unit_id,
        head_hash=pdf_sha256,
        check_id="unit_pages_inspected",
        attempt=attempt,
        result="PASS" if not findings else "FAIL",
        detail={"page_count": len(pages), "finding_count": len(findings)},
    )

    value = "pages_inspected" if not findings else "layout_repairable"
    return {
        "unit_page_inventories": [inventory],
        "unit_page_inspections": inspections,
        "deterministic_checks": [check],
        "pending_guard": guard(
            "D14_INVENTORY_AND_INSPECT_UNIT_PAGES", value, unit_id=unit_id, findings=findings
        ),
    }
