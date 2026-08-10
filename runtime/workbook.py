"""Workbook assembly — the only path by which a run may be recorded COMPLETE."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
from typing import Any

from . import run_state
from .checks import CheckFailure, rasterize_and_check_nonblank


class WorkbookError(RuntimeError):
    """Assembly was asked to produce a workbook the run does not have the units for."""


def assemble(output_root: Path) -> dict[str, Any]:
    """Concatenate every completed unit's PDF and write the coverage receipt.

    `run_status` becomes COMPLETE only here, and only when coverage is exact and the
    assembled PDF actually rasterizes nonblank.
    """
    output_root = Path(output_root)
    state = run_state.read(output_root)
    if state is None:
        raise WorkbookError(f"no run state under {output_root}")
    expected = state["manifest_unit_ids"]
    included = state["completed_unit_ids"]
    coverage = {"expected": len(expected), "included": len(included)}

    workbook = output_root / "workbook"
    workbook.mkdir(parents=True, exist_ok=True)
    (workbook / "coverage.json").write_text(
        json.dumps({**coverage, "expected_unit_ids": expected, "included_unit_ids": included},
                   indent=2) + "\n", encoding="utf-8")

    if included != expected:
        missing = [unit for unit in expected if unit not in included]
        raise WorkbookError(
            f"coverage is {len(included)} of {len(expected)}; {len(missing)} units are not "
            f"completed, so this run cannot be COMPLETE (first missing: {missing[0]})")

    pdfs = [output_root / unit / "document" / f"{unit}.pdf" for unit in included]
    absent = [str(pdf) for pdf in pdfs if not pdf.is_file()]
    if absent:
        raise WorkbookError(f"completed units without a shipped PDF: {absent}")

    target = workbook / "workbook.pdf"
    if shutil.which("pdfunite"):
        result = subprocess.run(["pdfunite", *[str(pdf) for pdf in pdfs], str(target)],
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise WorkbookError(f"pdfunite failed: {result.stderr}")
    else:
        raise WorkbookError("pdfunite unavailable; the workbook cannot be assembled")

    try:
        pages = rasterize_and_check_nonblank(target, workbook / "page_renders", dpi=150)
    except CheckFailure as error:
        raise WorkbookError(f"assembled workbook does not rasterize nonblank: {error}") from error

    state = run_state._recompute(output_root, state)
    state.update({"run_status": "COMPLETE", "workbook_assembled": True,
                  "workbook_coverage": coverage, "closed_at": run_state._now()})
    state.pop("terminal_reason", None)
    run_state._write(output_root, state)
    return {"workbook": str(target), "pages": len(pages), "coverage": coverage}
