"""Role- and map-kind-driven visual generation for one unit.

Asset selection is driven by the curriculum manifest's declared `visual_roles` and by the
domain's own `map_kind`/`relationship`, never by filesystem sort order. A role that cannot
resolve to a verified asset is recorded as unresolved and blocks the unit; it is never
filled with an unrelated asset.
"""
from __future__ import annotations

from datetime import date
import hashlib
import html
import json
from pathlib import Path
import re
from typing import Any, Iterable

import yaml


class VisualMapError(RuntimeError):
    """A map kind, relationship or visual role this pipeline has no renderer for."""


# Visual-role classes, in match order. `photograph` deliberately precedes `safety` so a
# role named "safe disconnected setup photograph" is classed by what it is, not by the
# word "safe" inside it.
_ROLE_CLASSES: list[tuple[str, tuple[str, ...]]] = [
    ("evidence_card", ("evidence card", "tick-box", "tick box")),
    ("photograph", ("photorealistic", "photograph", "photo")),
    ("safety", ("red-x", "red x", "hazard", "warning", "danger", "inset")),
    ("map", ("map", "overlay", "route")),
    ("diagram", ("diagram", "illustration", "cutaway", "schematic")),
]

_CLASS_PLACEMENT = {
    "evidence_card": ("expected_result", "evaluate"),
    "photograph": ("subject_identification", "identification"),
    "safety": ("safety_or_troubleshooting", "troubleshooting"),
    "map": ("assembly_or_path_map", "assembly"),
    "diagram": ("orientation_and_parts", "identification"),
}

_STOPWORDS = {"a", "an", "and", "the", "of", "or", "verified", "deterministic", "child",
              "photorealistic", "photograph", "photo", "map", "diagram", "illustration",
              "overlay", "route", "card", "evidence", "types", "type", "safe"}


# --- svg primitives ------------------------------------------------------------------
#
# An SVG is scaled to the page's text width (about 455 pt) when it is placed, so a glyph's
# effective point size is `font_px * 455 / WIDTH`. Every size below is chosen so the
# smallest label still clears PDF-TEXT-LEGIBLE's 9 pt floor once that scaling is applied.

WIDTH = 1400
_SCALE_TO_PAGE = 455 / WIDTH
HEAD, SUB, BODY, LABEL, SMALL = 58, 38, 36, 34, 32
_ADVANCE = 0.52          # mean Helvetica advance as a fraction of the point size
_MARGIN = 70
_INK = "#17365D"
_WARN = "#C9472F"
_MUTED = "#5A6B7C"

PHOTO_REGIONS = "verified_photo_regions.v1.json"


def effective_point_size(font_px: float) -> float:
    return round(font_px * _SCALE_TO_PAGE, 2)


def _text(x: int, y: int, value: str, *, size: int = BODY, weight: str = "normal",
          fill: str = "#000000", anchor: str = "start") -> str:
    return (f'<text x="{x}" y="{y}" font-family="Helvetica" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">'
            f'{html.escape(str(value))}</text>')


def _wrap(value: str, width: int) -> list[str]:
    words, lines, current = str(value).split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _columns(x: int, size: int) -> int:
    """How many characters fit on one line from `x` to the right margin at `size`."""
    return max(8, int((WIDTH - _MARGIN - x) / (size * _ADVANCE)))


def _para(parts: list[str], x: int, y: int, value: str, *, size: int = BODY,
          weight: str = "normal", fill: str = "#000000") -> int:
    """Emit wrapped text and return the next free baseline."""
    for line in _wrap(value, _columns(x, size)):
        parts.append(_text(x, y, line, size=size, weight=weight, fill=fill))
        y += int(size * 1.32)
    return y


def _document(height: int, body: Iterable[str]) -> str:
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
             f'viewBox="0 0 {WIDTH} {height}">',
             f'<rect width="{WIDTH}" height="{height}" fill="white"/>']
    parts.extend(body)
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _heading(title: str, subtitle: str | None = None) -> tuple[list[str], int]:
    parts: list[str] = []
    y = _para(parts, _MARGIN, 84, title, size=HEAD, weight="bold", fill=_INK)
    if subtitle:
        y = _para(parts, _MARGIN, y + 12, subtitle, size=SUB, fill=_MUTED)
    return parts, y + 40


# --- map renderers -------------------------------------------------------------------

def render_power_path(build_map: dict[str, Any], electrical: dict[str, Any]) -> str:
    """A directed tracing sequence with per-edge labels taken from the electrical model."""
    points = build_map.get("traced_path", [])
    designed = (electrical.get("circuit") or {}).get("status") == "designed_verified"
    edge_label = "carries current" if designed else "not yet connected — you are only tracing"
    parts, y = _heading("Power path to trace",
                        "Follow the arrows in order. Nothing here is joined up yet.")
    for index, point in enumerate(points):
        parts.append(f'<circle cx="120" cy="{y}" r="24" fill="white" stroke="{_INK}" stroke-width="7"/>')
        parts.append(_text(120, y + 13, str(index + 1), size=LABEL, weight="bold", fill=_INK,
                           anchor="middle"))
        bottom = _para(parts, 200, y + 13, point, size=BODY)
        if index + 1 < len(points):
            parts.append(f'<line x1="120" y1="{y + 34}" x2="120" y2="{y + 92}" '
                         f'stroke="{_INK}" stroke-width="6"/>')
            parts.append(f'<path d="M 106 {y + 86} L 120 {y + 108} L 134 {y + 86} Z" fill="{_INK}"/>')
            parts.append(_text(200, y + 96, edge_label, size=SMALL, fill=_MUTED))
        y = max(bottom, y + 130)
    return _document(y + 40, parts)


def render_same_wire(build_map: dict[str, Any]) -> str:
    """The first two items are the two ends of one wire; anything further stands alone."""
    points = build_map.get("traced_path", [])
    if len(points) < 2:
        raise VisualMapError("same_wire needs at least two traced points")
    parts, y = _heading("One wire, two ends",
                        "The two ends joined by the dashed line are the same piece of wire. "
                        "Anything listed under them is a separate place, joined to nothing.")
    top = y + 30
    bottom = top + 220
    parts.append(f'<circle cx="200" cy="{top}" r="26" fill="{_INK}"/>')
    _para(parts, 260, top + 13, points[0], size=BODY)
    parts.append(f'<circle cx="200" cy="{bottom}" r="26" fill="{_INK}"/>')
    _para(parts, 260, bottom + 13, points[1], size=BODY)
    parts.append(f'<line x1="200" y1="{top + 30}" x2="200" y2="{bottom - 30}" '
                 f'stroke="{_INK}" stroke-width="8" stroke-dasharray="18 14"/>')
    parts.append(_text(240, (top + bottom) // 2 + 10, "same wire — one piece of metal",
                       size=LABEL, fill=_INK))
    y = bottom + 150
    if len(points) > 2:
        y = _para(parts, _MARGIN, y, "Also find, on its own — not joined to the wire:",
                  size=SUB, weight="bold", fill=_MUTED) + 20
        for point in points[2:]:
            parts.append(f'<rect x="184" y="{y - 30}" width="42" height="42" rx="8" '
                         f'fill="white" stroke="{_MUTED}" stroke-width="6"/>')
            y = max(_para(parts, 260, y, point, size=BODY), y + 60) + 30
    return _document(y + 40, parts)


def render_enumeration(build_map: dict[str, Any]) -> str:
    """Each item is its own thing to find. No line is drawn between any two of them."""
    points = build_map.get("traced_path", [])
    parts, y = _heading("Find each of these",
                        "These are separate places to point at. No line joins them, "
                        "because nothing here is connected to anything else.")
    for point in points:
        parts.append(f'<rect x="102" y="{y - 32}" width="46" height="46" rx="8" '
                     f'fill="white" stroke="{_INK}" stroke-width="7"/>')
        y = max(_para(parts, 200, y, point, size=BODY), y + 60) + 40
    return _document(y + 40, parts)


def render_breadboard(build_map: dict[str, Any]) -> str:
    """A cutaway of the clip groups, the centre trench and the rail breaks."""
    features = set(build_map.get("labelled_features", []))
    parts, y = _heading("Under the holes: the hidden clips",
                        build_map.get("orientation", ""))
    left, pitch, hole = 120, 56, 20
    if "rails" in features:
        y = _para(parts, _MARGIN, y, "power rail", size=SMALL, weight="bold", fill=_WARN) + 10
        for column in range(18):
            if "rail_breaks" in features and column == 9:
                continue
            parts.append(f'<rect x="{left + column * pitch}" y="{y + 14}" width="{hole}" '
                         f'height="{hole}" fill="#333333"/>')
        parts.append(f'<line x1="{left}" y1="{y}" x2="{left + 17 * pitch + hole}" y2="{y}" '
                     f'stroke="{_WARN}" stroke-width="6"/>')
        y += 66
        if "rail_breaks" in features:
            y = _para(parts, _MARGIN, y, "rail break — the rail stops part-way along, here",
                      size=LABEL, fill=_WARN) + 30
    for side, label in ((0, "top half"), (1, "bottom half")):
        y = _para(parts, _MARGIN, y, label, size=SMALL, weight="bold", fill=_MUTED) + 6
        for group in range(4):
            gx = left + group * (5 * pitch + 60)
            for column in range(5):
                parts.append(f'<rect x="{gx + column * pitch}" y="{y}" width="{hole}" '
                             f'height="{hole}" fill="#333333"/>')
            parts.append(f'<rect x="{gx - 12}" y="{y + 32}" width="{4 * pitch + hole + 24}" '
                         f'height="18" rx="9" fill="{_INK}"/>')
        y += 78
        y = _para(parts, _MARGIN, y, "one clip joins these five holes — and no others",
                  size=LABEL, fill=_INK) + 24
        if side == 0 and "centre_trench" in features:
            parts.append(f'<rect x="{_MARGIN}" y="{y}" width="{WIDTH - 2 * _MARGIN}" '
                         f'height="58" fill="#E8ECF1" stroke="{_MUTED}" stroke-width="4"/>')
            y = _para(parts, _MARGIN + 24, y + 40, "centre trench — no clip crosses this gap",
                      size=LABEL, weight="bold", fill=_INK) + 44
    for endpoint in build_map.get("wire_endpoints", []):
        y = _para(parts, _MARGIN, y,
                  f"planned connection: {endpoint['from']} to {endpoint['to']}", size=BODY) + 16
    inset = build_map.get("safety_inset") or {}
    if inset.get("shows"):
        y += 30
        lines = len(_wrap(inset["shows"], _columns(110, LABEL)))
        parts.append(f'<rect x="{_MARGIN}" y="{y - 46}" width="{WIDTH - 2 * _MARGIN}" '
                     f'height="{lines * 46 + 40}" rx="12" fill="white" stroke="{_WARN}" stroke-width="6"/>')
        y = _para(parts, 110, y, inset["shows"], size=LABEL, fill=_WARN) + 40
    return _document(y + 40, parts)


def render_map(domain: dict[str, Any]) -> str:
    """Dispatch on (map_kind, relationship). An unrecognized kind fails the unit."""
    build_map = domain.get("build_map") or {}
    kind = build_map.get("map_kind")
    if kind == "power_path":
        return render_power_path(build_map, domain.get("electrical") or {})
    if kind == "breadboard":
        return render_breadboard(build_map)
    if kind == "connectivity":
        relationship = build_map.get("relationship")
        if relationship == "same_wire":
            return render_same_wire(build_map)
        if relationship == "enumeration":
            return render_enumeration(build_map)
        raise VisualMapError(
            f"connectivity map needs a relationship of same_wire or enumeration, got: {relationship!r}")
    raise VisualMapError(f"no renderer for map kind: {kind!r}")


# --- other deterministic renders -----------------------------------------------------

def render_evidence_card(build_map: dict[str, Any], *, signoff_required: bool) -> str:
    """The learner's own tick list, from this unit's `child_records` — never generic."""
    card = build_map.get("evidence_card") or {}
    records = card.get("child_records") or []
    if not records:
        raise VisualMapError("evidence card has no child_records to render")
    parts, y = _heading("Evidence card", card.get("prompt", ""))
    for record in records:
        parts.append(f'<rect x="100" y="{y - 34}" width="48" height="48" rx="8" '
                     f'fill="white" stroke="{_INK}" stroke-width="6"/>')
        y = max(_para(parts, 180, y, record, size=BODY), y + 62) + 30
    if signoff_required:
        y += 40
        parts.append(f'<line x1="100" y1="{y}" x2="760" y2="{y}" stroke="{_INK}" stroke-width="4"/>')
        parts.append(_text(100, y + 48, "Adult signature", size=LABEL, fill=_MUTED))
        parts.append(f'<line x1="820" y1="{y}" x2="1330" y2="{y}" stroke="{_INK}" stroke-width="4"/>')
        parts.append(_text(820, y + 48, "Date", size=LABEL, fill=_MUTED))
        y += 80
    return _document(y + 40, parts)


def render_parts_diagram(parts_list: list[dict[str, Any]], *, subject: str) -> str:
    """Each named part of the subject, with what it is for. Every label is a data field."""
    if not parts_list:
        raise VisualMapError("parts diagram has no parts to render")
    body, y = _heading(f"The parts of the {subject}",
                       "Each label points at one part and says what it is for.")
    for index, part in enumerate(parts_list, 1):
        body.append(f'<circle cx="120" cy="{y}" r="28" fill="{_INK}"/>')
        body.append(_text(120, y + 13, str(index), size=LABEL, weight="bold", fill="white",
                          anchor="middle"))
        y = _para(body, 190, y + 13, part["label"], size=BODY, weight="bold")
        y = _para(body, 190, y + 6, part["role"], size=LABEL, fill=_MUTED) + 40
    return _document(y + 40, body)


def render_prohibited_connection(failure: dict[str, Any]) -> str:
    """A crossed-out connection: the thing that must never be done, drawn rather than only said."""
    body, y = _heading("Never do this", failure["wrong_action"])
    box_top = y + 20
    body.append(f'<rect x="150" y="{box_top}" width="420" height="200" rx="16" '
                f'fill="white" stroke="{_INK}" stroke-width="7"/>')
    body.append(_text(360, box_top + 112, "supply", size=BODY, anchor="middle"))
    body.append(f'<rect x="820" y="{box_top}" width="430" height="200" rx="16" '
                f'fill="white" stroke="{_INK}" stroke-width="7"/>')
    body.append(_text(1035, box_top + 92, "meter set to", size=LABEL, anchor="middle"))
    body.append(_text(1035, box_top + 136, "current mode", size=LABEL, anchor="middle"))
    body.append(f'<line x1="570" y1="{box_top + 70}" x2="820" y2="{box_top + 70}" '
                f'stroke="{_INK}" stroke-width="7"/>')
    body.append(f'<line x1="570" y1="{box_top + 130}" x2="820" y2="{box_top + 130}" '
                f'stroke="{_INK}" stroke-width="7"/>')
    body.append(f'<line x1="565" y1="{box_top + 20}" x2="825" y2="{box_top + 180}" '
                f'stroke="{_WARN}" stroke-width="22"/>')
    body.append(f'<line x1="825" y1="{box_top + 20}" x2="565" y2="{box_top + 180}" '
                f'stroke="{_WARN}" stroke-width="22"/>')
    y = box_top + 280
    for label, value in (("What would happen", failure.get("consequence")),
                         ("What keeps you safe", failure.get("prevented_by"))):
        if not value:
            continue
        y = _para(body, _MARGIN, y, label, size=SUB, weight="bold", fill=_WARN)
        y = _para(body, _MARGIN, y + 6, value, size=LABEL) + 30
    return _document(y + 40, body)


def render_warning_notice(failure: dict[str, Any]) -> str:
    body, y = _heading("Watch out for this", failure["wrong_action"])
    body.append(f'<rect x="{_MARGIN}" y="{y - 10}" width="{WIDTH - 2 * _MARGIN}" height="10" fill="{_WARN}"/>')
    y += 70
    for label, value in (("What would happen", failure.get("consequence")),
                         ("What keeps you safe", failure.get("prevented_by"))):
        if not value:
            continue
        y = _para(body, _MARGIN, y, label, size=SUB, weight="bold", fill=_WARN)
        y = _para(body, _MARGIN, y + 6, value, size=LABEL) + 30
    return _document(y + 40, body)


# --- role resolution -----------------------------------------------------------------

def classify_role(role: str) -> str:
    lowered = role.lower()
    for name, keywords in _ROLE_CLASSES:
        if any(keyword in lowered for keyword in keywords):
            return name
    raise VisualMapError(f"no renderer class for declared visual role: {role!r}")


def _tokens(value: str) -> set[str]:
    words = re.split(r"[^a-z0-9]+", value.lower())
    return {word for word in words if word and word not in _STOPWORDS}


def load_photo_regions(curriculum: Path) -> dict[str, Any]:
    path = curriculum / PHOTO_REGIONS
    if not path.is_file():
        return {"regions": [], "absent_subjects": [], "source_photographs": {}}
    return json.loads(path.read_text())


def match_photo_subject(role: str, regions: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    """Resolve a photographic role to a verified region, or to the recorded reason it cannot."""
    role_tokens = _tokens(role)
    for entry in regions.get("regions", []):
        if role_tokens & set(entry.get("subject_tokens", [])):
            return "resolved", entry
    for entry in regions.get("absent_subjects", []):
        if role_tokens & set(entry.get("subject_tokens", [])):
            return "absent", entry
    return "unknown", None


def _crop(source: Path, box: list[int], destination: Path) -> None:
    from PIL import Image
    with Image.open(source) as image:
        image.crop(tuple(box)).save(destination, quality=92)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest_unit(curriculum: Path, unit_id: str) -> dict[str, Any]:
    candidates = sorted(curriculum.glob("*curriculum*.y*ml"))
    if len(candidates) != 1:
        raise VisualMapError(f"expected one curriculum manifest under {curriculum}, found {candidates}")
    manifest = yaml.safe_load(candidates[0].read_text())
    for lab in manifest.get("labs", []):
        if lab["id"] == unit_id:
            return lab
    raise VisualMapError(f"{unit_id} is not in {candidates[0].name}")


def _domain_view(unit: dict[str, Any], seed: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize a lab document or a pre-authoring domain seed into one shape to render from."""
    if seed is not None:
        points = [item.get("name", item.get("coordinate", "point")).replace("_", " ")
                  for item in seed.get("terminals", [])] or \
                 [str(item) for item in seed.get("legal_coordinates", [])]
        return {
            "domain": {"build_map": {"map_kind": "connectivity", "relationship": "enumeration",
                                     "traced_path": points},
                       "electrical": {}},
            "parts": [{"label": item.get("name", "point").replace("_", " "),
                       "role": item.get("function", "")}
                      for item in seed.get("terminals", [])],
            "subject": seed.get("component_identity", {}).get("kit_roster_name", "subject"),
            "signoff_required": True,
        }
    return {
        "domain": unit["domain"],
        "parts": unit["content"]["identification"]["parts"],
        "subject": unit["content"]["identification"]["child_name"],
        "signoff_required": bool(unit["safety"]["adult_verification"]["signoff_required"]),
    }


def regenerate_assets(unit: dict[str, Any], curriculum: Path, output: Path, *,
                      unit_id: str | None = None,
                      seed: dict[str, Any] | None = None) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Write every declared visual role's asset under `output/assets` and receipt it.

    Callable independently of `prepare()`'s control flow: `prepare()` passes the frozen
    domain `seed` for a unit that has not been authored yet, and the regeneration path
    passes the finished lab document. Both write the same asset names, so re-finalizing
    picks up corrected bytes rather than stale ones.

    Returns the unit with each visual's `provenance.file_hash` recomputed from the bytes
    just written — bytes and receipt change in one place, so they cannot drift apart —
    and the list of roles that could not be resolved to a verified asset.
    """
    unit_id = unit_id or unit.get("identity", {}).get("unit_id") or unit.get("id")
    if not unit_id:
        raise VisualMapError("cannot regenerate assets without a unit id")
    declared = _manifest_unit(curriculum, unit_id).get("visual_roles", [])
    view = _domain_view(unit, seed)
    domain = view["domain"]
    regions = load_photo_regions(curriculum)

    assets = output / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    visuals: list[dict[str, Any]] = []
    unresolved: list[dict[str, str]] = []
    written: set[str] = set()

    def receipt(name: str, role: str, kind: str, history: list[str],
                *, extra: dict[str, Any] | None = None) -> None:
        schema_role, section = _CLASS_PLACEMENT[kind]
        provenance = {"publisher": "curriculum runtime deterministic renderer",
                      "item_or_family": f"{unit_id} {role}", "access_date": today,
                      "file_hash": _sha256(assets / name), "embedded_as": f"assets/{name}",
                      "crop_transform_history": history}
        provenance.update(extra or {})
        visuals.append({"role": schema_role, "source_kind": (
            "verified_photograph" if kind == "photograph" else "deterministic_render"),
            "supports_section": section, "carries_exact_domain_fact": True,
            "provenance": provenance,
            "omission_finding": _OMISSION[kind]})
        written.add(name)

    failures = (domain.get("electrical") or {}).get("failure_modes") or []
    card_rendered = False

    for role in declared:
        kind = classify_role(role)
        if kind == "photograph":
            status, entry = match_photo_subject(role, regions)
            if status != "resolved":
                reason = (entry or {}).get(
                    "finding", f"no verified photograph of this subject is declared in {PHOTO_REGIONS}")
                unresolved.append({"role": role, "reason": reason})
                continue
            source = curriculum / entry["source"]
            name = f"photo_{_slug(entry['subject'])}.jpg"
            box = entry["crop_box"]
            _crop(source, box, assets / name)
            receipt(name, role, kind,
                    [f"Cropped from {entry['source']} to the region containing the "
                     f"{entry['subject']} (pixels {box[0]},{box[1]} to {box[2]},{box[3]}).",
                     entry["verified_note"], f"Verified by {entry['verified_by']}."],
                    extra={k: v for k, v in
                           (regions.get("source_photographs", {}).get(entry["source"]) or {}).items()
                           if k in {"url", "publisher", "item_or_family"}})
        elif kind == "map":
            (assets / "path_map.svg").write_text(render_map(domain), encoding="utf-8")
            receipt("path_map.svg", role, kind,
                    ["Rendered from this unit's own build map data: "
                     f"{domain['build_map'].get('map_kind')}"
                     f"{'/' + domain['build_map']['relationship'] if domain['build_map'].get('relationship') else ''}."])
        elif kind == "evidence_card":
            (assets / "evidence_card.svg").write_text(
                render_evidence_card(domain["build_map"], signoff_required=view["signoff_required"]),
                encoding="utf-8")
            receipt("evidence_card.svg", role, kind,
                    ["Rendered from this unit's own evidence-card records."])
            card_rendered = True
        elif kind == "diagram":
            name = f"{_slug(role)}.svg"
            (assets / name).write_text(render_parts_diagram(view["parts"], subject=view["subject"]),
                                       encoding="utf-8")
            receipt(name, role, kind, ["Rendered from this unit's own named parts."])
        else:
            if not failures:
                unresolved.append({"role": role,
                                   "reason": "no failure mode is recorded in the domain data to render"})
                continue
            failure = failures[0]
            prohibited = any(word in role.lower() for word in ("red-x", "red x"))
            name = f"{_slug(role)}.svg"
            (assets / name).write_text(
                render_prohibited_connection(failure) if prohibited else render_warning_notice(failure),
                encoding="utf-8")
            receipt(name, role, kind, ["Rendered from this unit's own recorded failure mode."])

    # Every unit records what the learner found, whether or not its manifest names the card
    # as a role of its own.
    if not card_rendered and (domain.get("build_map") or {}).get("evidence_card"):
        (assets / "evidence_card.svg").write_text(
            render_evidence_card(domain["build_map"], signoff_required=view["signoff_required"]),
            encoding="utf-8")
        receipt("evidence_card.svg", "child evidence card", "evidence_card",
                ["Rendered from this unit's own evidence-card records."])

    for stale in sorted(assets.iterdir()):
        if stale.is_file() and stale.name not in written and stale.name != "manifest.json":
            stale.unlink()
    (assets / "manifest.json").write_text(json.dumps(
        {"assets": [{"embedded_as": f"assets/{name}", "sha256": _sha256(assets / name)}
                    for name in sorted(written)]}, indent=2) + "\n", encoding="utf-8")

    if "identity" in unit:
        unit["visuals"] = visuals
        unit["content"]["unresolved_visual_roles"] = unresolved
    return unit, unresolved


_OMISSION = {
    "photograph": "The photograph shows what the subject looks like and shows no wiring or connection.",
    "map": "The map shows only what can be traced with everything disconnected and unpowered.",
    "evidence_card": "The card records what was found and grants no permission to energize anything.",
    "diagram": "The diagram names parts only; it shows no powered or connected configuration.",
    "safety": "The picture shows what to avoid and shows no permitted live configuration.",
}
