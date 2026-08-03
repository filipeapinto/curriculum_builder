from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any

import jsonschema


class CheckFailure(RuntimeError):
    pass


def resolve_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise CheckFailure(f"invalid JSON pointer: {pointer}")
    value = document
    for raw in pointer[1:].split("/"):
        part = raw.replace("~1", "/").replace("~0", "~")
        try:
            value = value[int(part)] if isinstance(value, list) else value[part]
        except (KeyError, IndexError, ValueError, TypeError) as error:
            raise CheckFailure(f"pointer does not resolve: {pointer}") from error
    return value


def check_derivation(unit: dict[str, Any]) -> list[dict[str, Any]]:
    derived = unit.get("derived", [])
    if not derived:
        raise CheckFailure("derivation-absent")
    checked = []
    for item in derived:
        pointer = item["domain_pointer"]
        expected = resolve_pointer(unit["domain"], pointer)
        if item["rendered_value"] != expected:
            raise CheckFailure(f"derivation-value-mismatch: {pointer}")
        checked.append({"pointer": pointer, "value": expected})
    return checked


def check_receipts(unit: dict[str, Any], artifact_root: Path) -> list[dict[str, Any]]:
    receipts = unit.get("visual_receipts") or unit.get("visuals", {}).get("receipts", [])
    if not receipts:
        raise CheckFailure("receipt-absent")
    results = []
    root = artifact_root.resolve()
    for receipt in receipts:
        relative = receipt.get("embedded_as") or receipt.get("provenance", {}).get("embedded_as")
        recorded = receipt.get("file_hash") or receipt.get("provenance", {}).get("file_hash")
        path = (root / relative).resolve()
        if root not in path.parents or not path.is_file():
            raise CheckFailure(f"receipt-path-unresolved: {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if recorded != actual:
            raise CheckFailure(f"receipt-hash-mismatch: {relative}")
        results.append({"path": str(path), "sha256": actual})
    return results


def validate_unit(unit: dict[str, Any], engine_schema: Path, domain_schema: Path) -> None:
    jsonschema.Draft202012Validator(json.loads(engine_schema.read_text())).validate(unit)
    jsonschema.Draft202012Validator(json.loads(domain_schema.read_text())).validate(unit["domain"])


def pdf_page_count(pdf: Path) -> int:
    if not shutil.which("pdfinfo"):
        raise CheckFailure("pdfinfo unavailable")
    result = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    if result.returncode != 0:
        raise CheckFailure(f"pdfinfo failed: {result.stderr}")
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise CheckFailure("PDF page count absent")


def rasterize_and_check_nonblank(pdf: Path, directory: Path, *, dpi: int = 200) -> list[Path]:
    if not shutil.which("pdftoppm"):
        raise CheckFailure("pdftoppm unavailable")
    directory.mkdir(parents=True, exist_ok=True)
    prefix = directory / "page"
    result = subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(pdf), str(prefix)],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise CheckFailure(f"rasterization failed: {result.stderr}")
    pages = sorted(directory.glob("page-*.png"))
    if len(pages) != pdf_page_count(pdf):
        raise CheckFailure("raster page count differs from shipped PDF")
    try:
        from PIL import Image, ImageStat
    except ImportError as error:
        raise CheckFailure("Pillow unavailable for nonblank audit") from error
    for page in pages:
        with Image.open(page) as image:
            extrema = image.convert("L").getextrema()
            if extrema is None or extrema[1] - extrema[0] <= 2:
                raise CheckFailure(f"blank PDF page: {page}")
    return pages
