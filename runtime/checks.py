from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any

import jsonschema
import yaml

from .readability import bloom_flags, text_violations


class CheckFailure(RuntimeError):
    pass


ENGINE_CHECKS = "policy/checks.v1.yaml"
CURRICULUM_CHECKS = "checks.v1.yaml"
CHECKS_CONTRACT = "schemas/checks.schema.v1.json"

# The engine-owned ids every generated unit owes. Naming them here is not the hardcoding
# issue 002 records: what each id asserts, and whether it exists at all, is read from the
# catalogue below, and an id this list names that the catalogue does not hold is a hard
# error — that is exactly the uncatalogued-check problem.
ENGINE_REQUIRED = ("LAB-SCHEMA-VALID", "TEXT-READABILITY-BAND", "TEXT-BLOOM-VERBS",
                   "DOC-DERIVED-FROM-SOURCE", "RECEIPT-HASH-RESOLVES", "PDF-ASSET-RESOLVES",
                   "PDF-TEXT-LEGIBLE", "PDF-VISUAL-REVIEW")
CURRICULUM_REQUIRED = ("DOMAIN-VERIFIER", "VISUAL-ROLES-COMPLETE")

# TEXT-BLOOM-VERBS flags and never blocks: human raters agree with each other on Bloom
# level only 46.58% of the time, so a recorded flag is the assertion, not a verdict.
NON_BLOCKING = frozenset({"TEXT-BLOOM-VERBS"})


def _catalogue_entries(path: Path) -> tuple[dict[str, dict[str, Any]], str]:
    document = yaml.safe_load(path.read_text())
    entries: dict[str, dict[str, Any]] = {}
    for value in document.values():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and "id" in item:
                    entries[item["id"]] = item
    return entries, str(document.get("checks_version", ""))


def required_checks_for(engine: Path, curriculum: Path) -> dict[str, Any]:
    """The required check set for one unit, built from the two catalogues rather than a dict.

    `policy/checks.v1.yaml` owns the ids that bind every run; `curricula/<name>/checks.v1.yaml`
    owns the ids whose subject is this curriculum. Both are read as one inventory, and both
    `checks_version` values are returned so `unit_checks.json` can record what it was scored
    against.
    """
    engine_entries, engine_version = _catalogue_entries(Path(engine) / ENGINE_CHECKS)
    curriculum_entries, curriculum_version = _catalogue_entries(Path(curriculum) / CURRICULUM_CHECKS)

    required: dict[str, dict[str, Any]] = {}
    for source, entries, ids in (("engine", engine_entries, ENGINE_REQUIRED),
                                 ("curriculum", curriculum_entries, CURRICULUM_REQUIRED)):
        for check_id in ids:
            if check_id not in entries:
                raise CheckFailure(
                    f"{check_id} is required of every unit but is not in the {source} catalogue; "
                    "an uncatalogued check is the defect, not the missing entry")
            required[check_id] = {"source": source, "asserts": entries[check_id].get("asserts", ""),
                                  "stage": entries[check_id].get("stage"),
                                  "blocking": check_id not in NON_BLOCKING}
    return {"required": required,
            "checks_version": {"engine": engine_version, "curriculum": curriculum_version}}


def readability_problems(text: str, calibration: Path) -> list[str]:
    """TEXT-READABILITY-BAND against real rendered child-facing text, not a fixture."""
    declared = (yaml.safe_load(Path(calibration).read_text()) or {}).get("readability") or {}
    band, metric = declared.get("band"), str(declared.get("metric", ""))
    if not (isinstance(band, list) and len(band) == 2):
        return ["readability-band-missing: calibration declares no two-element band"]
    return text_violations(text, band, metric)


def bloom_report(unit: dict[str, Any], calibration: Path) -> list[str]:
    """TEXT-BLOOM-VERBS. Records every disagreement and blocks on none of them."""
    table = (yaml.safe_load(Path(calibration).read_text()) or {}).get("bloom_verbs") or {}
    return bloom_flags(unit, table)


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
    derived = unit.get("derived") or (unit.get("content") or {}).get("derived") or []
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


# --- source-claim entailment (issue 006) ---------------------------------------------

_NUMBER = re.compile(r"\d")
_UNIT_WORDS = ("mA", "A", "V", "mV", "ohm", "kohm", "Mohm", "W", "mW", "percent")


def _claimful_strings(unit: dict[str, Any]) -> list[tuple[str, str]]:
    """Every numeric claim a unit makes, and where it sits.

    Scoped to numbers on purpose. A number is a claim about the world that some source
    either states or does not; prose with no number in it is the unit's own instruction to
    a learner, and demanding a citation for it would turn this check into a formality.
    """
    found: list[tuple[str, str]] = []
    verification = ((unit.get("safety") or {}).get("adult_verification") or {})
    for field in ("limits", "endpoint_check"):
        value = verification.get(field)
        if isinstance(value, str) and _NUMBER.search(value):
            found.append((f"safety.adult_verification.{field}", value))
    electrical = (unit.get("domain") or {}).get("electrical") or {}
    for index, rating in enumerate(electrical.get("ratings_and_limits") or []):
        parts = [str(rating.get(key, "")) for key in ("parameter", "absolute_max", "typical", "unit")]
        text = " ".join(part for part in parts if part)
        if _NUMBER.search(text):
            found.append((f"domain.electrical.ratings_and_limits[{index}]", text))
    spec = (electrical.get("component_spec") or {}).get("parameters") or []
    for index, parameter in enumerate(spec):
        value = str(parameter.get("value", ""))
        if _NUMBER.search(value):
            found.append((f"domain.electrical.component_spec.parameters[{index}]",
                          f"{parameter.get('name', '')} {value} {parameter.get('unit', '')}".strip()))
    return found


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip().lower()


def _numbers(value: str) -> set[str]:
    """Quantities only. A digit inside a part number like DM-100 is a name, not a measurement."""
    return {match.group(0) for match in re.finditer(r"(?<![A-Za-z0-9.-])\d+(?:\.\d+)?", value)}


def check_claim_entailment(unit: dict[str, Any], source_root: Path) -> list[dict[str, Any]]:
    """Every numeric or safety-critical claim resolves to a source that actually supports it.

    Fails a device-specific claim whose cited source is generic or names a different model
    unless `subject_scope.model_independent` carries a justification; requires
    `derivation.premises` for a conservative or derived number and forbids attributing it
    to a source that states a different figure.
    """
    source_root = Path(source_root)
    claims = ((unit.get("content") or {}).get("sourced_claims")) or []
    problems: list[str] = []
    resolved: list[dict[str, Any]] = []

    by_text = {claim["claim"]: claim for claim in claims}
    for location, text in _claimful_strings(unit):
        lowered = text.lower()
        if not any(claim.lower() in lowered or lowered in claim.lower()
                   or _numbers(claim) & _numbers(text) for claim in by_text):
            problems.append(f"claim-unsourced: {location} states a number with no sourced_claims entry")

    for index, claim in enumerate(claims):
        locator = claim["source_locator"]
        path = (source_root / locator["path"]).resolve()
        if source_root.resolve() not in path.parents and path != source_root.resolve():
            problems.append(f"claim-locator-escapes-root: {locator['path']}")
            continue
        if not path.is_file():
            problems.append(f"claim-locator-unresolved: {locator['path']} is not a cached source")
            continue
        body = _normalize(path.read_text(errors="replace"))
        anchor = _normalize(str(locator["section_or_line"]))
        if anchor and anchor not in body:
            problems.append(
                f"claim-locator-text-absent: the cited text is not in {locator['path']} "
                f"({claim['claim'][:60]!r})")
            continue

        scope = claim["subject_scope"]
        exact = scope.get("exact_model")
        if exact:
            if _normalize(exact) not in body:
                problems.append(
                    f"claim-wrong-device: {exact!r} is not named anywhere in {locator['path']}, "
                    f"so it cannot support a claim scoped to that exact model")
                continue
        elif not scope.get("justification"):
            problems.append("claim-scope-unjustified: a model-independent claim states no justification")
            continue

        stated = _numbers(claim["claim"])
        supported = _numbers(anchor) if anchor else set()
        derivation = claim.get("derivation")
        if stated and supported and not stated <= supported:
            if not derivation or not derivation.get("premises"):
                problems.append(
                    f"claim-unsupported-number: {sorted(stated - supported)} is not stated by the "
                    f"cited text ({sorted(supported)}), and no derivation premises are recorded")
                continue
        resolved.append({"claim": claim["claim"], "path": locator["path"],
                         "derived": bool(derivation)})

    if problems:
        raise CheckFailure("; ".join(problems))
    return resolved
