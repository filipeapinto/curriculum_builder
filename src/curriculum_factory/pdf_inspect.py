"""PDF-level inspection: PDF-TEXT-LEGIBLE and PDF-ASSET-RESOLVES.

The same poppler toolchain family `checks.py` already uses for `pdfinfo`/`pdftoppm`.
`PDF-VISUAL-REVIEW`'s recording mechanism lives here too — this module implements the
verdict-required rule, not automated computer vision, and says so rather than implying
the review is automated.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any

from .checks import CheckFailure

MIN_POINT_SIZE = 9.0

# `pdftotext -bbox-layout` reports each line's ink box, not its nominal type size. Measured
# against this repository's own pandoc/typst/Helvetica toolchain at 8, 9, 11 and 14 pt, the
# ink box is a constant 0.92 of the nominal size, so the nominal size is recoverable.
_INK_BOX_RATIO = 0.92

# One line item per shipped page, each explicitly answered before a unit may be ACCEPTED.
VISUAL_REVIEW_CRITERIA = ("relevance", "semantic_truthfulness", "legibility", "correct_placement")


def _require(tool: str) -> None:
    if not shutil.which(tool):
        raise CheckFailure(f"{tool} unavailable")


def font_sizes(pdf: Path) -> list[tuple[float, str]]:
    """Every rendered line's nominal type size, with the line it was measured from."""
    _require("pdftotext")
    result = subprocess.run(["pdftotext", "-bbox-layout", str(pdf), "-"],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise CheckFailure(f"pdftotext failed: {result.stderr}")
    measured: dict[float, str] = {}
    for match in re.finditer(
            r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>',
            result.stdout, re.S):
        height = float(match.group(4)) - float(match.group(2))
        if height <= 0:
            continue
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", match.group(5))).strip()
        if len(text) < 3:
            continue
        measured.setdefault(round(height / _INK_BOX_RATIO, 2), text)
    return sorted(measured.items())


def text_legible(pdf: Path, *, minimum: float = MIN_POINT_SIZE) -> dict[str, Any]:
    """Body text is at or above `minimum` points and no line runs off the page box."""
    _require("pdftotext")
    sizes = font_sizes(pdf)
    if not sizes:
        raise CheckFailure("PDF-TEXT-LEGIBLE: the document renders no extractable text at all")
    undersized = [(size, text[:60]) for size, text in sizes if size < minimum]
    clipped = clipped_lines(pdf)
    problems = []
    if undersized:
        problems.append(f"text below {minimum}pt: {undersized}")
    if clipped:
        problems.append(f"{len(clipped)} line(s) run outside the page box")
    return {"sizes": [size for size, _ in sizes], "smallest": sizes[0][0],
            "clipped": clipped, "problems": problems}


def clipped_lines(pdf: Path) -> list[str]:
    """Lines whose bounding box leaves the page box — the reliable signal for clipped text."""
    _require("pdftotext")
    result = subprocess.run(["pdftotext", "-bbox-layout", str(pdf), "-"],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise CheckFailure(f"pdftotext failed: {result.stderr}")
    clipped: list[str] = []
    page_width = page_height = None
    for line in result.stdout.splitlines():
        page = re.search(r'<page width="([\d.]+)" height="([\d.]+)"', line)
        if page:
            page_width, page_height = float(page.group(1)), float(page.group(2))
            continue
        box = re.search(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)"', line)
        if box and page_width:
            x_max, y_max = float(box.group(3)), float(box.group(4))
            if x_max > page_width + 1 or y_max > page_height + 1:
                clipped.append(line.strip()[:120])
    return clipped


def embedded_image_hashes(pdf: Path, workdir: Path) -> list[str]:
    """SHA-256 of every image actually embedded in the shipped PDF."""
    _require("pdfimages")
    workdir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["pdfimages", "-png", str(pdf), str(workdir / "img")],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise CheckFailure(f"pdfimages failed: {result.stderr}")
    return [hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(workdir.glob("img-*.png"))]


def _thumbprint(path: Path) -> tuple[int, ...]:
    """A 16x16 grayscale signature — survives re-encoding, fails on a different picture."""
    from PIL import Image
    with Image.open(path) as image:
        return tuple(image.convert("L").resize((16, 16)).tobytes())


def _distance(left: tuple[int, ...], right: tuple[int, ...]) -> float:
    return sum(abs(a - b) for a, b in zip(left, right)) / len(left)


MAX_THUMBPRINT_DISTANCE = 12.0


def assets_resolve(pdf: Path, visuals: list[dict[str, Any]], artifact_root: Path,
                   workdir: Path) -> dict[str, Any]:
    """Every declared visual's receipt resolves, and its picture is the one in the PDF.

    A raster asset is re-encoded when it is placed, so a byte-identical match is not the
    testable claim; what is checked is that the receipt still resolves against the bytes on
    disk and that an image perceptually equal to it is embedded in the shipped PDF. A
    receipt that does not resolve is a failed gate, not a warning.
    """
    problems: list[str] = []
    declared: list[dict[str, Any]] = []
    for visual in visuals:
        relative = visual["provenance"]["embedded_as"]
        path = (Path(artifact_root) / relative).resolve()
        if not path.is_file():
            problems.append(f"PDF-ASSET-RESOLVES: receipted asset is not on disk: {relative}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != visual["provenance"]["file_hash"]:
            problems.append(
                f"PDF-ASSET-RESOLVES: receipt does not match the shipped bytes: {relative}")
        declared.append({"embedded_as": relative, "sha256": actual, "path": path})

    embedded = []
    workdir.mkdir(parents=True, exist_ok=True)
    _require("pdfimages")
    result = subprocess.run(["pdfimages", "-png", str(pdf), str(workdir / "img")],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise CheckFailure(f"pdfimages failed: {result.stderr}")
    for extracted in sorted(workdir.glob("img-*.png")):
        embedded.append(_thumbprint(extracted))

    raster = [item for item in declared
              if item["path"].suffix.lower() in {".jpg", ".jpeg", ".png"}]
    for item in raster:
        signature = _thumbprint(item["path"])
        closest = min((_distance(signature, other) for other in embedded), default=None)
        if closest is None or closest > MAX_THUMBPRINT_DISTANCE:
            problems.append(
                f"PDF-ASSET-RESOLVES: no image in the shipped PDF matches the receipted picture "
                f"for {item['embedded_as']} (closest signature distance "
                f"{'none embedded' if closest is None else round(closest, 1)})")
    return {"declared": [{"embedded_as": item["embedded_as"], "sha256": item["sha256"]}
                         for item in declared],
            "embedded_image_count": len(embedded), "problems": problems}


def visual_review_template(pages: int, visuals: list[dict[str, Any]]) -> dict[str, Any]:
    """The structured reviewer verdict PDF-VISUAL-REVIEW requires before ACCEPTED."""
    return {
        "reviewed": False,
        "reviewer": None,
        "scope": "one line item per shipped page, plus one per declared visual",
        "pages": [{"page": index + 1, **{name: None for name in VISUAL_REVIEW_CRITERIA}}
                  for index in range(pages)],
        "visuals": [{"role": visual["role"],
                     "embedded_as": visual["provenance"]["embedded_as"],
                     **{name: None for name in VISUAL_REVIEW_CRITERIA}}
                    for visual in visuals],
        "note": ("This is the recording mechanism and the block-if-absent rule, not automated "
                 "computer vision. An unfilled verdict blocks acceptance; it never passes by default."),
    }


def visual_review_problems(verdict: dict[str, Any] | None) -> list[str]:
    if not verdict:
        return ["PDF-VISUAL-REVIEW: no reviewer verdict is attached"]
    if not verdict.get("reviewed"):
        return ["PDF-VISUAL-REVIEW: the reviewer verdict is attached but not filled in"]
    problems: list[str] = []
    if not verdict.get("reviewer"):
        problems.append("PDF-VISUAL-REVIEW: the verdict names no reviewer")
    for group in ("pages", "visuals"):
        for item in verdict.get(group, []):
            for name in VISUAL_REVIEW_CRITERIA:
                if item.get(name) not in {"pass", "fail", "n/a"}:
                    problems.append(
                        f"PDF-VISUAL-REVIEW: {group} item {item.get('page', item.get('role'))} "
                        f"leaves {name} unanswered")
                elif item.get(name) == "fail":
                    problems.append(
                        f"PDF-VISUAL-REVIEW: {group} item {item.get('page', item.get('role'))} "
                        f"fails {name}")
    return problems
