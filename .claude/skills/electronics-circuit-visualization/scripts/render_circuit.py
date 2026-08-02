#!/usr/bin/env python3
"""Render fact-bearing electronics visuals deterministically from structured circuit data.

Reads one JSON document (a curriculum `domain` block, or a `circuit_data` document),
emits typst source, compiles it to PNG, and writes a trace manifest recording, for
every string placed on the page, the JSON pointer it came from. Nothing is drawn that
is not either (a) traced to an input field or (b) a fixed label from the closed CHROME
vocabulary below. Geometry is computed here, in Python, from the data; typst only draws.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

FONT = "Helvetica"
INK = "#14181c"
MUTED = "#5c6670"
RULE = "#c9d1d9"
PANEL = "#f2f5f7"
ACCENT = "#0b5fa5"
WARN = "#b3421a"
WHITE = "#ffffff"

PAGE_W = 1120.0
PAGE_H = 700.0
MARGIN = 44.0

# Fixed page furniture: section headings and whole sentences only. Anything that names a
# field goes through Canvas.field_label instead, which derives the label from the key, so a
# row cannot be captioned with some other field's name. Membership here is checkable by
# script, which is what makes "is every element traceable?" a decidable question.
CHROME = {
    "TRACED PATH",
    "ORIENTATION, VERBATIM FROM THE DATA",
    "LEGAL COORDINATES",
    "RAIL TOPOLOGY",
    "RATINGS",
    "EVIDENCE CARD",
    "THE CHILD RECORDS",
    "PRIMARY SOURCES",
    "POWER-ON RELEASE",
    "SOURCE BUNDLE SHA-256",
    "NETS AND CONNECTIONS",
    "CONNECTION TABLE",
    "SUPPLY",
    "POWER-ON / POWER-OFF SEQUENCE",
    "SCHEMATIC SYMBOL",
    "BOARD MAP",
    "WIRE ENDPOINTS",
    "COMPONENTS PLACED",
    "PLACEMENT STEPS",
    "DMM PROBES",
    "SAFETY INSET",
    "RATINGS AND LIMITS",
    "FAILURE MODES",
    "POWER PROFILE",
    "CALCULATIONS",
    "LABELLED FEATURES",
    "trace order",
    "position not asserted in the data",
    "(empty in the source data)",
    "(absent from the source data)",
    "The grid below is a generic illustration. Only labelled positions are claims, and every one is a coordinate in the data.",
    "Placement on this page is layout only. The circuit facts are the pin-to-net pairs listed below.",
    "Every element on this page is rendered from the input document named below. Nothing here was inferred.",
}

POLARITY_MARK = {"anode": "anode", "cathode": "cathode", "positive": "positive", "negative": "negative", "none": ""}

ROLES = ("power_path", "connectivity", "breadboard", "schematic", "safety_inset")


# ---------------------------------------------------------------- data access


class Missing(Exception):
    """The declared role needs a field the input document does not carry."""


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def jstr(value) -> str:
    """Render a JSON scalar exactly as it stands in the document."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return json.dumps(value)
    return str(value)


class Doc:
    """The input document plus pointer bookkeeping, so every read is quotable."""

    def __init__(self, raw: dict, path: Path):
        if isinstance(raw, dict) and "domain" in raw and isinstance(raw["domain"], dict):
            self.root = raw["domain"]
            self.prefix = "/domain"
        else:
            self.root = raw
            self.prefix = ""
        self.path = path
        if "terminals" in self.root and "legal_coordinates" in self.root:
            self.shape = "circuit_data"
        elif "electrical" in self.root or "build_map" in self.root:
            self.shape = "domain"
        else:
            raise Missing(
                "Unrecognised input. Expected a curriculum `domain` block (with `electrical` "
                "and/or `build_map`) or a `circuit_data` document (with `terminals` and "
                "`legal_coordinates`)."
            )

    def get(self, pointer: str, default=Missing):
        node = self.root
        for part in [p for p in pointer.split("/") if p != ""]:
            if isinstance(node, list):
                try:
                    node = node[int(part)]
                except (ValueError, IndexError):
                    node = None
            elif isinstance(node, dict):
                node = node.get(part, None)
            else:
                node = None
            if node is None and default is not Missing:
                return default
        if node is None and default is not Missing:
            return default
        return node

    def ptr(self, pointer: str) -> str:
        return self.prefix + pointer


# ---------------------------------------------------------------- canvas


class Canvas:
    """Absolute-positioned typst drawing surface. Records a trace for every string."""

    def __init__(self, doc: Doc, role: str):
        self.doc = doc
        self.role = role
        self.body: list[str] = []
        self.trace: list[dict] = []
        self.max_y = 0.0
        self.h = PAGE_H

    def _reach(self, y):
        self.max_y = max(self.max_y, y)

    # -- primitives ------------------------------------------------

    def rect(self, x, y, w, h, fill=None, stroke=RULE, width=0.8, radius=3.0):
        self._reach(y + h)
        parts = [f"width: {w:.2f}pt", f"height: {h:.2f}pt", f"radius: {radius:.2f}pt"]
        parts.append(f'fill: rgb("{fill}")' if fill else "fill: none")
        parts.append(f'stroke: {width:.2f}pt + rgb("{stroke}")' if stroke else "stroke: none")
        self.body.append(f"#place(dx: {x:.2f}pt, dy: {y:.2f}pt, rect({', '.join(parts)}))")

    def line(self, x1, y1, x2, y2, color=RULE, width=0.8, dash=False):
        self._reach(max(y1, y2))
        d = ", dash: \"dashed\"" if dash else ""
        self.body.append(
            f"#place(dx: 0pt, dy: 0pt, line(start: ({x1:.2f}pt, {y1:.2f}pt), "
            f"end: ({x2:.2f}pt, {y2:.2f}pt), stroke: {width:.2f}pt + rgb(\"{color}\"){d}))"
        )

    def dot(self, x, y, r=2.6, color=ACCENT):
        self._reach(y + r)
        self.body.append(
            f"#place(dx: {x - r:.2f}pt, dy: {y - r:.2f}pt, "
            f'circle(radius: {r:.2f}pt, fill: rgb("{color}"), stroke: none))'
        )

    def arrow_right(self, x, y, size=6.0, color=MUTED):
        self.body.append(
            f"#place(dx: {x:.2f}pt, dy: {y - size / 2:.2f}pt, polygon(fill: rgb(\"{color}\"), "
            f"stroke: none, (0pt, 0pt), ({size:.2f}pt, {size / 2:.2f}pt), (0pt, {size:.2f}pt)))"
        )

    # -- text ------------------------------------------------------

    def text(self, x, y, s, *, pointer=None, chrome=False, size=10.0, weight="regular",
             color=INK, width=None, align_=None, tracking=0.0):
        """Place a string. Either `pointer` (a JSON pointer into the input) or chrome=True."""
        s = jstr(s)
        if not chrome and pointer is None:
            raise AssertionError(f"untraced string reached the page: {s!r}")
        if chrome and s not in CHROME:
            raise AssertionError(f"chrome string not in the closed vocabulary: {s!r}")
        opts = [f"size: {size:.1f}pt", f'fill: rgb("{color}")', f'weight: "{weight}"']
        if tracking:
            opts.append(f"tracking: {tracking:.2f}pt")
        self._reach(y + est_height(s, width or (PAGE_W - x - MARGIN), size))
        inner = f'text({", ".join(opts)}, "{esc(s)}")'
        if align_:
            inner = f"align({align_}, {inner})"
        if width:
            inner = f"box(width: {width:.2f}pt, {inner})"
        self.body.append(f"#place(dx: {x:.2f}pt, dy: {y:.2f}pt, {inner})")
        self.trace.append(
            {
                "text": s,
                "kind": "chrome" if chrome else "data",
                "pointer": None if chrome else self.doc.ptr(pointer),
            }
        )
        return est_height(s, width or (PAGE_W - x - MARGIN), size)

    def field_label(self, x, y, key, *, size=8.5, color=MUTED, weight="regular", width=None,
                    tracking=0.0):
        """Caption a value with its own field name, derived from the key rather than chosen.

        A free-chosen caption can be a legitimate word from elsewhere on the page and still
        be the wrong one for the row beside it — the audit would pass and the page would
        lie. Deriving the text from the key makes that failure unrepresentable.
        """
        s = key.replace("_", " ")
        opts = [f"size: {size:.1f}pt", f'fill: rgb("{color}")', f'weight: "{weight}"']
        if tracking:
            opts.append(f"tracking: {tracking:.2f}pt")
        inner = f'text({", ".join(opts)}, "{esc(s)}")'
        if width:
            inner = f"box(width: {width:.2f}pt, {inner})"
        self._reach(y + size * 1.35)
        self.body.append(f"#place(dx: {x:.2f}pt, dy: {y:.2f}pt, {inner})")
        self.trace.append({"text": s, "kind": "field_label", "field": key, "pointer": None})
        return size * 1.35

    def label(self, x, y, s, width=None):
        return self.text(x, y, s, chrome=True, size=8.5, weight="bold", color=MUTED,
                         tracking=0.7, width=width)

    def provenance(self, x, y, s):
        self.body.append(
            f"#place(dx: {x:.2f}pt, dy: {y:.2f}pt, "
            f'text(size: 8.0pt, fill: rgb("{MUTED}"), weight: "regular", "{esc(s)}"))'
        )
        self.trace.append({"text": s, "kind": "provenance", "pointer": None})

    # -- output ----------------------------------------------------

    def typst(self) -> str:
        head = (
            f"#set page(width: {PAGE_W:.0f}pt, height: {self.h:.0f}pt, margin: 0pt, "
            f'fill: rgb("{WHITE}"))\n'
            f'#set text(font: "{FONT}", fill: rgb("{INK}"), hyphenate: false)\n'
            f"#set par(leading: 0.55em, justify: false)\n"
        )
        return head + "\n".join(self.body) + "\n"


def est_height(s: str, width: float, size: float) -> float:
    """Conservative wrapped-height estimate so stacked blocks do not collide."""
    per_line = max(1.0, width / (size * 0.50))
    lines = max(1, math.ceil(len(str(s)) / per_line))
    return lines * size * 1.35


# ---------------------------------------------------------------- shared furniture


def header(c: Canvas, title_ptr: str, title: str, subtitle_ptr: str, subtitle: str, tag: str, tag_ptr: str):
    c.text(MARGIN, 30, title, pointer=title_ptr, size=21, weight="bold", width=PAGE_W - 2 * MARGIN - 260)
    c.text(MARGIN, 60, subtitle, pointer=subtitle_ptr, size=9.5, color=MUTED,
           width=PAGE_W - 2 * MARGIN - 260)
    if tag_ptr is None:
        # The role name is not a fact about the circuit, so it is stamped as provenance.
        c.provenance(PAGE_W - MARGIN - 250, 34, tag)
    else:
        c.text(PAGE_W - MARGIN - 250, 32, tag, pointer=tag_ptr, size=10, weight="bold",
               color=ACCENT, width=250, align_="right", tracking=0.8)
    c.line(MARGIN, 82, PAGE_W - MARGIN, 82, color=INK, width=1.4)


def footer(c: Canvas, doc: Doc):
    """Close the page. The page grows to the content rather than the content to the page."""
    y = max(c.max_y + 28, 320.0)
    c.line(MARGIN, y, PAGE_W - MARGIN, y, color=RULE)
    c.text(MARGIN, y + 8,
           "Every element on this page is rendered from the input document named below. Nothing here was inferred.",
           chrome=True, size=8.0, color=MUTED, width=700)
    c.provenance(MARGIN, y + 22, f"{doc.path.name} · role: {c.role}")
    sha = doc.get("/source_bundle_sha256", None)
    if sha:
        c.label(PAGE_W - MARGIN - 430, y + 8, "SOURCE BUNDLE SHA-256", width=430)
        c.text(PAGE_W - MARGIN - 430, y + 20, sha, pointer="/source_bundle_sha256",
               size=8.0, color=MUTED, width=430, align_="right")
    c.h = max(c.max_y + 26, 560.0)


def panel(c: Canvas, x, y, w, h, fill=PANEL):
    c.rect(x, y, w, h, fill=fill, stroke=RULE)


# ---------------------------------------------------------------- role: path maps


def render_path(c: Canvas, doc: Doc):
    """Unpowered power-path / connectivity map, from circuit_data or an unpowered_path_map."""
    if doc.shape == "circuit_data":
        title = doc.get("/component_identity/kit_roster_name", None)
        if title is None:
            raise Missing("circuit_data input is missing /component_identity/kit_roster_name")
        header(c, "/component_identity/kit_roster_name", title, "/id", doc.get("/id", ""),
               c.role, None)
        nodes = [
            {
                "idx_ptr": f"/terminals/{i}",
                "top": t.get("name", ""),
                "top_ptr": f"/terminals/{i}/name",
                "mid": t.get("function", ""),
                "mid_ptr": f"/terminals/{i}/function",
                "low": t.get("coordinate", ""),
                "low_ptr": f"/terminals/{i}/coordinate",
            }
            for i, t in enumerate(doc.get("/terminals", []) or [])
        ]
        if not nodes:
            raise Missing("circuit_data input carries no /terminals to draw")
    else:
        bm = doc.get("/build_map", None)
        if not isinstance(bm, dict) or bm.get("map_kind") not in ("power_path", "connectivity"):
            raise Missing(
                "domain input has no unpowered path map: /build_map/map_kind must be "
                "'power_path' or 'connectivity' for this role"
            )
        title = doc.get("/electrical/component_spec/part_family", None)
        if title is None:
            raise Missing("domain input is missing /electrical/component_spec/part_family")
        header(c, "/electrical/component_spec/part_family", title,
               "/electrical/behaviour/child_level", doc.get("/electrical/behaviour/child_level", ""),
               bm["map_kind"], "/build_map/map_kind")
        path = doc.get("/build_map/traced_path", []) or []
        nodes = [
            {"idx_ptr": f"/build_map/traced_path/{i}", "top": step,
             "top_ptr": f"/build_map/traced_path/{i}", "mid": None, "low": None}
            for i, step in enumerate(path)
        ]
        if not nodes:
            raise Missing("domain input carries no /build_map/traced_path to draw")

    # -- the chain
    c.label(MARGIN, 100, "TRACED PATH")
    n = len(nodes)
    gap = 46.0
    span = PAGE_W - 2 * MARGIN
    bw = (span - gap * (n - 1)) / n
    top, bh = 120.0, 118.0
    for i, node in enumerate(nodes):
        x = MARGIN + i * (bw + gap)
        panel(c, x, top, bw, bh)
        c.rect(x, top, 4, bh, fill=ACCENT, stroke=None, radius=0)
        c.text(x + 16, top + 14, str(i + 1), pointer=node["idx_ptr"], size=9, weight="bold",
               color=ACCENT)
        y = top + 32
        y += c.text(x + 16, y, node["top"], pointer=node["top_ptr"], size=12.5, weight="bold",
                    width=bw - 32)
        if node["mid"]:
            y += 4
            y += c.text(x + 16, y, node["mid"], pointer=node["mid_ptr"], size=9,
                        color=MUTED, width=bw - 32)
        if node["low"]:
            c.text(x + 16, top + bh - 20, node["low"], pointer=node["low_ptr"], size=8.5,
                   color=ACCENT, width=bw - 32)
        if i < n - 1:
            cy = top + bh / 2
            c.line(x + bw + 6, cy, x + bw + gap - 12, cy, color=MUTED, width=1.0)
            c.arrow_right(x + bw + gap - 12, cy)
    c.text(MARGIN, top + bh + 8, "trace order", chrome=True, size=8, color=MUTED)

    # -- left column: orientation, then whatever the shape carries
    y = 296.0
    lw = 600.0
    c.label(MARGIN, y, "ORIENTATION, VERBATIM FROM THE DATA", width=lw)
    orientation = doc.get("/orientation", None)
    orientation_ptr = "/orientation"
    if orientation is None and doc.shape == "domain":
        orientation = doc.get("/build_map/orientation", None)
        orientation_ptr = "/build_map/orientation"
    y += 14
    if orientation is not None:
        h = est_height(orientation, lw - 24, 10.5) + 20
        panel(c, MARGIN, y, lw, h)
        c.text(MARGIN + 12, y + 10, orientation, pointer=orientation_ptr, size=10.5, width=lw - 24)
        y += h + 18
    else:
        c.text(MARGIN, y, "(absent from the source data)", chrome=True, size=9.5, color=MUTED)
        y += 26

    coords = doc.get("/legal_coordinates", None)
    if coords:
        c.label(MARGIN, y, "LEGAL COORDINATES", width=lw)
        y += 16
        for i, co in enumerate(coords):
            c.dot(MARGIN + 4, y + 5, r=1.8, color=MUTED)
            y += c.text(MARGIN + 16, y, co, pointer=f"/legal_coordinates/{i}", size=9.5,
                        color=INK, width=lw - 16) + 3

    # -- right column
    rx = MARGIN + lw + 32
    rw = PAGE_W - MARGIN - rx
    ry = 296.0
    if doc.shape == "circuit_data":
        c.label(rx, ry, "RAIL TOPOLOGY", width=rw)
        ry += 15
        ry += c.text(rx, ry, doc.get("/rail_topology", None) if doc.get("/rail_topology", None)
                     is not None else None, pointer="/rail_topology", size=11, weight="bold",
                     width=rw) + 16
        c.label(rx, ry, "RATINGS", width=rw)
        ry += 15
        ratings = doc.get("/ratings", []) or []
        if not ratings:
            ry += c.text(rx, ry, "(empty in the source data)", chrome=True, size=9.5, color=MUTED,
                         width=rw) + 16
        else:
            for i, r in enumerate(ratings):
                ry += c.text(rx, ry, json.dumps(r, sort_keys=True), pointer=f"/ratings/{i}",
                             size=9, width=rw) + 4
            ry += 12
        c.label(rx, ry, "PRIMARY SOURCES", width=rw)
        ry += 15
        for i, src in enumerate(doc.get("/primary_sources", []) or []):
            ry += c.text(rx, ry, src.get("url_or_path", ""), pointer=f"/primary_sources/{i}/url_or_path",
                         size=8.5, color=ACCENT, width=rw) + 2
            ry += c.text(rx, ry, src.get("access_date", ""), pointer=f"/primary_sources/{i}/access_date",
                         size=8.5, color=MUTED, width=rw) + 2
            ry += c.text(rx, ry, src.get("claim_scope", ""), pointer=f"/primary_sources/{i}/claim_scope",
                         size=8.5, color=MUTED, width=rw) + 10
    else:
        card = doc.get("/build_map/evidence_card", None)
        if card:
            c.label(rx, ry, "EVIDENCE CARD", width=rw)
            ry += 15
            h = est_height(card.get("prompt", ""), rw - 24, 10.5) + 20
            panel(c, rx, ry, rw, h)
            c.text(rx + 12, ry + 10, card.get("prompt", ""), pointer="/build_map/evidence_card/prompt",
                   size=10.5, width=rw - 24)
            ry += h + 16
            c.label(rx, ry, "THE CHILD RECORDS", width=rw)
            ry += 16
            for i, rec in enumerate(card.get("child_records", []) or []):
                c.rect(rx, ry, 10, 10, fill=None, stroke=MUTED, width=0.9, radius=1.5)
                ry += c.text(rx + 18, ry, rec, pointer=f"/build_map/evidence_card/child_records/{i}",
                             size=9.5, width=rw - 18) + 6
        release = doc.get("/build_map/power_on_release", None)
        if release is not None:
            ry += 10
            c.label(rx, ry, "POWER-ON RELEASE", width=rw)
            ry += 15
            c.text(rx, ry, release, pointer="/build_map/power_on_release", size=13,
                   weight="bold", color=WARN if release is False else INK, width=rw)

    footer(c, doc)


# ---------------------------------------------------------------- role: schematic


def require_domain(doc: Doc, role: str):
    if doc.shape != "domain":
        raise Missing(
            f"the '{role}' role needs a curriculum domain block, and this is a circuit_data "
            "document — it carries terminals and coordinates, but no nets, components or "
            "build_map, so there is no topology or layout in it to draw. The roles this "
            "document supports are power_path and connectivity."
        )


def render_schematic(c: Canvas, doc: Doc):
    require_domain(doc, "schematic")
    circuit = doc.get("/electrical/circuit", None)
    if not isinstance(circuit, dict):
        raise Missing("schematic role needs /electrical/circuit")
    if circuit.get("status") != "designed_verified":
        raise Missing(
            "schematic role needs /electrical/circuit/status == 'designed_verified'; this "
            f"document says {circuit.get('status')!r}, so there is no topology to draw"
        )
    comps = circuit.get("components") or []
    nets = circuit.get("nets") or []
    supply = circuit.get("supply") or {}
    if not comps or not nets:
        raise Missing("schematic role needs both /electrical/circuit/components and /nets")

    title = doc.get("/electrical/component_spec/part_family", None)
    if title is None:
        raise Missing("domain input is missing /electrical/component_spec/part_family")
    sym = circuit.get("schematic_symbol", {}).get("symbol", "")
    header(c, "/electrical/component_spec/part_family", title,
           "/electrical/behaviour/adult_level", doc.get("/electrical/behaviour/adult_level", ""),
           sym, "/electrical/circuit/schematic_symbol/symbol")

    # Net ordering is derived, not chosen: supply positive on top, negative at the bottom.
    names = [n.get("name", "") for n in nets]
    pos, neg = supply.get("positive_net"), supply.get("negative_net")
    middle = sorted(n for n in names if n not in (pos, neg))
    order = ([pos] if pos in names else []) + middle + ([neg] if neg in names else [])
    net_index = {name: i for i, name in enumerate(order)}
    ptr_of_net = {n.get("name"): f"/electrical/circuit/nets/{i}/name" for i, n in enumerate(nets)}

    c.label(MARGIN, 100, "NETS AND CONNECTIONS")
    top, rowh = 132.0, 46.0
    left, right = MARGIN + 92, PAGE_W - MARGIN - 24
    for name in order:
        y = top + net_index[name] * rowh
        c.line(left, y, right, y, color=ACCENT, width=1.2)
        c.text(MARGIN, y - 6, name, pointer=ptr_of_net[name], size=10, weight="bold",
               color=ACCENT, width=84, align_="right")

    box_w, box_h = 96.0, 40.0
    slot = (right - left - 40) / max(1, len(comps))
    bottom_y = top + (len(order) - 1) * rowh
    cy = bottom_y + 78
    for ci, comp in enumerate(comps):
        x = left + 20 + ci * slot + (slot - box_w) / 2
        c.rect(x, cy, box_w, box_h, fill=PANEL, stroke=INK, width=1.0)
        c.text(x, cy + 6, comp.get("designator", ""),
               pointer=f"/electrical/circuit/components/{ci}/designator", size=11,
               weight="bold", width=box_w, align_="center")
        c.text(x, cy + 22, comp.get("value") or comp.get("part", ""),
               pointer=f"/electrical/circuit/components/{ci}/"
                       + ("value" if comp.get("value") else "part"),
               size=8.5, color=MUTED, width=box_w, align_="center")
        pins = comp.get("pins") or []
        for pi, pin in enumerate(pins):
            net = pin.get("net")
            if net not in net_index:
                continue
            px = x + box_w * (pi + 1) / (len(pins) + 1)
            py = top + net_index[net] * rowh
            c.line(px, py, px, cy, color=ACCENT, width=1.0)
            c.dot(px, py)
            c.text(px + 4, cy - 14, pin.get("pin", ""),
                   pointer=f"/electrical/circuit/components/{ci}/pins/{pi}/pin",
                   size=8, color=MUTED)
            polarity = pin.get("polarity")
            if polarity and polarity != "none":
                c.text(px + 4, py + 3, polarity,
                       pointer=f"/electrical/circuit/components/{ci}/pins/{pi}/polarity",
                       size=7.5, color=WARN)

    c.text(MARGIN, cy + box_h + 14,
           "Placement on this page is layout only. The circuit facts are the pin-to-net pairs listed below.",
           chrome=True, size=8.5, color=MUTED, width=560)

    # -- connection table (the netlist, verbatim)
    ty = cy + box_h + 40
    c.label(MARGIN, ty, "CONNECTION TABLE")
    ty += 16
    cols = [(MARGIN, 78, "designator"), (MARGIN + 78, 150, "part"), (MARGIN + 228, 90, "value"),
            (MARGIN + 318, 70, "pin"), (MARGIN + 388, 96, "net"), (MARGIN + 484, 90, "polarity")]
    for x, w, head in cols:
        c.field_label(x, ty, head, size=8, weight="bold", tracking=0.5, width=w)
    ty += 13
    c.line(MARGIN, ty, MARGIN + 574, ty, color=RULE)
    ty += 5
    for ci, comp in enumerate(comps):
        base = f"/electrical/circuit/components/{ci}"
        for pi, pin in enumerate(comp.get("pins") or []):
            cells = [
                (comp.get("designator", ""), f"{base}/designator"),
                (comp.get("part", ""), f"{base}/part"),
                (comp.get("value", ""), f"{base}/value") if comp.get("value") else (None, None),
                (pin.get("pin", ""), f"{base}/pins/{pi}/pin"),
                (pin.get("net", ""), f"{base}/pins/{pi}/net"),
                (pin.get("polarity", ""), f"{base}/pins/{pi}/polarity") if pin.get("polarity")
                else (None, None),
            ]
            for (x, w, _), (val, ptr) in zip(cols, cells):
                if val:
                    c.text(x, ty, val, pointer=ptr, size=9, width=w)
            ty += 14

    # -- supply block
    sx = MARGIN + 610
    sy = cy + box_h + 40
    sw = PAGE_W - MARGIN - sx
    c.label(sx, sy, "SUPPLY", width=sw)
    sy += 16
    for key in ("positive_net", "negative_net", "nominal_voltage"):
        if supply.get(key) is not None:
            c.field_label(sx, sy, key, width=110)
            c.text(sx + 116, sy, supply[key], pointer=f"/electrical/circuit/supply/{key}",
                   size=9.5, weight="bold", width=sw - 116)
            sy += 15
    seq = supply.get("sequence") or []
    if seq:
        sy += 8
        c.label(sx, sy, "POWER-ON / POWER-OFF SEQUENCE", width=sw)
        sy += 15
        for i, step in enumerate(seq):
            sy += c.text(sx, sy, step, pointer=f"/electrical/circuit/supply/sequence/{i}",
                         size=9, width=sw) + 4

    footer(c, doc)


# ---------------------------------------------------------------- role: breadboard

COORD_RE = re.compile(r"^\s*([a-jA-J])\s*[-_ ]?\s*(\d{1,2})\s*$")
RAIL_RE = re.compile(r"^\s*(top|bottom|upper|lower)[ _-]?rail(?:[ _-]?(\d{1,2}))?\s*$", re.I)

BOARD_COLS = 30  # columns drawn in the generic grid; a position is only claimed when data names it


def parse_coord(s: str):
    """Map a breadboard coordinate string to grid geometry, or None when it cannot be read.

    Guessing here would put an unevidenced position on the page, so an unreadable
    endpoint is routed to the wire table instead and explicitly marked unplaced.
    """
    if not isinstance(s, str):
        return None
    m = COORD_RE.match(s)
    if m:
        col = int(m.group(2))
        row = m.group(1).lower()
        if 1 <= col <= BOARD_COLS and row in "abcdefghij":
            return ("hole", "abcdefghij".index(row), col)
    m = RAIL_RE.match(s)
    if m:
        band = 0 if m.group(1).lower() in ("top", "upper") else 1
        col = int(m.group(2)) if m.group(2) else None
        return ("rail", band, col)
    return None


def render_breadboard(c: Canvas, doc: Doc):
    require_domain(doc, "breadboard")
    bm = doc.get("/build_map", None)
    if not isinstance(bm, dict) or bm.get("map_kind") != "breadboard":
        raise Missing("breadboard role needs /build_map/map_kind == 'breadboard'")

    title = doc.get("/electrical/component_spec/part_family", None)
    if title is None:
        raise Missing("domain input is missing /electrical/component_spec/part_family")
    header(c, "/electrical/component_spec/part_family", title,
           "/build_map/orientation", bm.get("orientation", ""), "breadboard", "/build_map/map_kind")

    # -- the board
    c.label(MARGIN, 100, "BOARD MAP")
    c.text(MARGIN + 90, 99,
           "The grid below is a generic illustration. Only labelled positions are claims, and every one is a coordinate in the data.",
           chrome=True, size=8, color=MUTED, width=560)
    bx, by = MARGIN, 130.0
    bw = 640.0
    pitch = bw / (BOARD_COLS + 1)
    rail_h = 14.0
    rows_h = pitch * 5
    trench = 16.0
    bh = rail_h * 2 + rows_h * 2 + trench + 28
    c.rect(bx, by, bw, bh, fill=PANEL, stroke=RULE)

    feats = bm.get("labelled_features") or []
    feat_ptr = {f: f"/build_map/labelled_features/{i}" for i, f in enumerate(feats)}

    def band_y(band):  # rail bands
        return by + 8 if band == 0 else by + bh - 8 - rail_h

    for band in (0, 1):
        y = band_y(band)
        c.rect(bx + 10, y, bw - 20, rail_h, fill=WHITE, stroke=RULE, radius=2)
        if "rails" in feat_ptr:
            c.text(bx + 14, y + 3, "rails", pointer=feat_ptr["rails"], size=7.5, color=MUTED)
        if "rail_breaks" in feat_ptr:
            for frac in (0.34, 0.67):
                gx = bx + 10 + (bw - 20) * frac
                c.line(gx, y, gx, y + rail_h, color=WARN, width=1.2)
            c.text(bx + 10 + (bw - 20) * 0.67 + 5, y + 3, "rail_breaks",
                   pointer=feat_ptr["rail_breaks"], size=7.5, color=WARN, width=80)

    grid_top = by + 8 + rail_h + 8

    def hole_xy(row_i, col):
        x = bx + pitch * col
        band = 0 if row_i < 5 else 1
        r = row_i if band == 0 else row_i - 5
        y = grid_top + (0 if band == 0 else rows_h + trench) + pitch * r + pitch / 2
        return x, y

    for row_i in range(10):
        for col in range(1, BOARD_COLS + 1):
            x, y = hole_xy(row_i, col)
            c.dot(x, y, r=1.1, color=RULE)
    if "centre_trench" in feat_ptr:
        ty = grid_top + rows_h
        c.rect(bx + 10, ty, bw - 20, trench, fill=WHITE, stroke=RULE, radius=1)
        c.text(bx + 14, ty + 3, "centre_trench", pointer=feat_ptr["centre_trench"],
               size=7.5, color=MUTED)
    if "rows" in feat_ptr:
        c.text(bx + 2, grid_top + 2, "rows", pointer=feat_ptr["rows"], size=7, color=MUTED)
    if "columns" in feat_ptr:
        c.text(bx + bw - 62, grid_top + 2, "columns", pointer=feat_ptr["columns"],
               size=7, color=MUTED, width=56, align_="right")

    # -- wires: drawn only where both endpoints parse
    wires = bm.get("wire_endpoints") or []
    unplaced = []
    for wi, w in enumerate(wires):
        a, b = parse_coord(w.get("from")), parse_coord(w.get("to"))
        if not a or not b:
            unplaced.append(wi)
            continue
        pts = []
        for p in (a, b):
            if p[0] == "hole":
                pts.append(hole_xy(p[1], p[2]))
            else:
                col = p[2] or 1
                pts.append((bx + pitch * col, band_y(p[1]) + rail_h / 2))
        c.line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], color=ACCENT, width=1.6)
        c.dot(*pts[0], r=2.4)
        c.dot(*pts[1], r=2.4)
        # A rail sits in a narrow band with a wire already running through it, so its label
        # goes outside the board entirely; a hole has room above it.
        for (px, py), p, key in zip(pts, (a, b), ("from", "to")):
            ly = (by - 11 if p[1] == 0 else by + bh + 3) if p[0] == "rail" else py - 11
            c.text(px + 5, ly, w.get(key, ""),
                   pointer=f"/build_map/wire_endpoints/{wi}/{key}", size=7.5, color=ACCENT)

    # -- wire table
    ty = by + bh + 30
    c.label(MARGIN, ty, "WIRE ENDPOINTS")
    ty += 16
    for x, w_, head in ((MARGIN, 170, "from"), (MARGIN + 170, 170, "to"), (MARGIN + 340, 120, "net")):
        c.field_label(x, ty, head, size=8, weight="bold", tracking=0.5, width=w_)
    ty += 13
    c.line(MARGIN, ty, MARGIN + 640, ty, color=RULE)
    ty += 5
    for wi, w in enumerate(wires):
        c.text(MARGIN, ty, w.get("from", ""), pointer=f"/build_map/wire_endpoints/{wi}/from",
               size=9, width=168)
        c.text(MARGIN + 170, ty, w.get("to", ""), pointer=f"/build_map/wire_endpoints/{wi}/to",
               size=9, width=168)
        if w.get("net"):
            c.text(MARGIN + 340, ty, w["net"], pointer=f"/build_map/wire_endpoints/{wi}/net",
                   size=9, width=118, color=ACCENT)
        if wi in unplaced:
            c.text(MARGIN + 462, ty, "position not asserted in the data", chrome=True, size=8,
                   color=WARN, width=178)
        ty += 14

    # -- right column
    rx = MARGIN + 672
    rw = PAGE_W - MARGIN - rx
    ry = 100.0
    placed = bm.get("components_placed") or []
    if placed:
        c.label(rx, ry, "COMPONENTS PLACED", width=rw)
        ry += 16
        for i, p in enumerate(placed):
            ry += c.text(rx, ry, p.get("part", ""), pointer=f"/build_map/components_placed/{i}/part",
                         size=10, weight="bold", width=rw)
            ry += c.text(rx, ry, p.get("value", ""), pointer=f"/build_map/components_placed/{i}/value",
                         size=8.5, color=MUTED, width=rw)
            ry += c.text(rx, ry, p.get("orientation", ""),
                         pointer=f"/build_map/components_placed/{i}/orientation", size=8.5,
                         color=MUTED, width=rw) + 8

    steps = bm.get("placement_steps") or []
    c.label(rx, ry, "PLACEMENT STEPS", width=rw)
    ry += 16
    for i, s in enumerate(steps):
        c.text(rx, ry, str(i + 1), pointer=f"/build_map/placement_steps/{i}", size=9,
               weight="bold", color=ACCENT, width=14)
        ry += c.text(rx + 18, ry, s, pointer=f"/build_map/placement_steps/{i}", size=9.5,
                     width=rw - 18) + 6

    probes = bm.get("dmm_probes")
    if probes:
        ry += 8
        c.label(rx, ry, "DMM PROBES", width=rw)
        ry += 16
        for i, pp in enumerate(probes.get("probe_points") or []):
            ry += c.text(rx, ry, pp, pointer=f"/build_map/dmm_probes/probe_points/{i}",
                         size=9, width=rw) + 3
        for key in ("lead_socket", "mode"):
            if probes.get(key):
                c.field_label(rx, ry, key, width=90)
                ry += c.text(rx + 96, ry, probes[key], pointer=f"/build_map/dmm_probes/{key}",
                             size=9, weight="bold", width=rw - 96) + 3

    inset = bm.get("safety_inset")
    if inset:
        ih = est_height(inset.get("shows", ""), rw - 24, 9.5) + 34
        iy = ry + 18
        c.rect(rx, iy, rw, ih, fill=WHITE, stroke=WARN, width=1.2)
        c.text(rx + 12, iy + 9, "SAFETY INSET", chrome=True, size=8.5, weight="bold",
               color=WARN, tracking=0.7, width=rw - 24)
        c.text(rx + 12, iy + 24, inset.get("shows", ""), pointer="/build_map/safety_inset/shows",
               size=9.5, width=rw - 24)

    footer(c, doc)


# ---------------------------------------------------------------- role: safety inset


def render_safety(c: Canvas, doc: Doc):
    require_domain(doc, "safety_inset")
    elec = doc.get("/electrical", None)
    inset = doc.get("/build_map/safety_inset", None)
    limits = (elec or {}).get("ratings_and_limits") or []
    failures = (elec or {}).get("failure_modes") or []
    if not limits and not failures and not inset:
        raise Missing(
            "safety_inset role needs at least one of /build_map/safety_inset, "
            "/electrical/ratings_and_limits, /electrical/failure_modes"
        )

    title = doc.get("/electrical/component_spec/part_family", None)
    if title is None:
        raise Missing("domain input is missing /electrical/component_spec/part_family")
    header(c, "/electrical/component_spec/part_family", title,
           "/electrical/behaviour/simplification_check",
           doc.get("/electrical/behaviour/simplification_check", ""), "safety_inset", None)

    y = 100.0
    if inset:
        c.label(MARGIN, y, "SAFETY INSET")
        y += 16
        h = est_height(inset.get("shows", ""), PAGE_W - 2 * MARGIN - 24, 14) + 26
        c.rect(MARGIN, y, PAGE_W - 2 * MARGIN, h, fill=WHITE, stroke=WARN, width=1.4)
        c.text(MARGIN + 14, y + 12, inset.get("shows", ""), pointer="/build_map/safety_inset/shows",
               size=14, width=PAGE_W - 2 * MARGIN - 28)
        y += h + 22

    lw = 520.0
    if limits:
        c.label(MARGIN, y, "RATINGS AND LIMITS", width=lw)
        ly = y + 16
        for x, w_, head in ((MARGIN, 190, "parameter"), (MARGIN + 190, 110, "absolute_max"),
                            (MARGIN + 300, 220, "source")):
            c.field_label(x, ly, head, size=8, weight="bold", tracking=0.5, width=w_)
        ly += 13
        c.line(MARGIN, ly, MARGIN + lw, ly, color=RULE)
        ly += 5
        for i, r in enumerate(limits):
            hgt = c.text(MARGIN, ly, r.get("parameter", ""),
                         pointer=f"/electrical/ratings_and_limits/{i}/parameter", size=9.5, width=186)
            c.text(MARGIN + 190, ly, f"{r.get('absolute_max', '')} {r.get('unit', '')}".strip(),
                   pointer=f"/electrical/ratings_and_limits/{i}/absolute_max", size=9.5,
                   weight="bold", color=WARN, width=106)
            hgt = max(hgt, c.text(MARGIN + 300, ly, r.get("source", ""),
                                  pointer=f"/electrical/ratings_and_limits/{i}/source", size=8.5,
                                  color=MUTED, width=218))
            ly += hgt + 6
        y_left_end = ly + 16
    else:
        y_left_end = y

    profile = doc.get("/power_profile", None)
    if profile:
        c.label(MARGIN, y_left_end, "POWER PROFILE", width=lw)
        py = y_left_end + 16
        for key in ("source", "nominal_voltage", "permitted_range", "current_protection",
                    "polarity", "evidence"):
            if profile.get(key) is None:
                continue
            c.field_label(MARGIN, py, key, width=120)
            py += c.text(MARGIN + 126, py, profile[key], pointer=f"/power_profile/{key}",
                         size=9.5, width=lw - 126) + 5

    rx = MARGIN + lw + 40
    rw = PAGE_W - MARGIN - rx
    ry = y
    if failures:
        c.label(rx, ry, "FAILURE MODES", width=rw)
        ry += 16
        for i, f in enumerate(failures):
            base = f"/electrical/failure_modes/{i}"
            block_top = ry
            c.rect(rx, block_top, 3, 10, fill=WARN, stroke=None, radius=0)
            ry += c.text(rx + 12, ry, f.get("wrong_action", ""), pointer=f"{base}/wrong_action",
                         size=10, weight="bold", width=rw - 12) + 3
            c.field_label(rx + 12, ry, "consequence", size=8, width=rw - 12)
            ry += 11
            ry += c.text(rx + 12, ry, f.get("consequence", ""), pointer=f"{base}/consequence",
                         size=9, color=INK, width=rw - 12) + 3
            c.field_label(rx + 12, ry, "prevented_by", size=8, width=rw - 12)
            ry += 11
            ry += c.text(rx + 12, ry, f.get("prevented_by", ""), pointer=f"{base}/prevented_by",
                         size=9, color=INK, width=rw - 12) + 3
            if f.get("reversible") is not None:
                c.field_label(rx + 12, ry, "reversible", size=8, width=70)
                ry += c.text(rx + 84, ry, f["reversible"], pointer=f"{base}/reversible",
                             size=9, weight="bold", width=rw - 84) + 12

    calcs = (elec or {}).get("calculations") or []
    if calcs:
        cy = c.max_y + 22
        c.label(MARGIN, cy, "CALCULATIONS", width=PAGE_W - 2 * MARGIN)
        cy += 16
        for i, calc in enumerate(calcs):
            base = f"/electrical/calculations/{i}"
            c.text(MARGIN, cy, calc.get("formula", ""), pointer=f"{base}/formula", size=9.5,
                   weight="bold", width=300)
            c.text(MARGIN + 310, cy, f"{calc.get('result', '')} {calc.get('unit', '')}".strip(),
                   pointer=f"{base}/result", size=9.5, color=ACCENT, width=110)
            cy += c.text(MARGIN + 430, cy, calc.get("margin_to_rating", ""),
                         pointer=f"{base}/margin_to_rating", size=9, color=MUTED, width=440) + 6

    footer(c, doc)


RENDERERS = {
    "power_path": render_path,
    "connectivity": render_path,
    "breadboard": render_breadboard,
    "schematic": render_schematic,
    "safety_inset": render_safety,
}


# ---------------------------------------------------------------- main


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--role", required=True, choices=ROLES)
    ap.add_argument("--out", required=True, type=Path, help="output path without extension")
    ap.add_argument("--ppi", type=int, default=200)
    ap.add_argument("--typst", default="typst")
    args = ap.parse_args(argv)

    raw = json.loads(args.input.read_text())
    try:
        doc = Doc(raw, args.input)
        canvas = Canvas(doc, args.role)
        RENDERERS[args.role](canvas, doc)
    except Missing as exc:
        print(f"cannot render role '{args.role}': {exc}", file=sys.stderr)
        return 2

    out = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    typ_path = out.with_suffix(".typ")
    png_path = out.with_suffix(".png")
    trace_path = out.with_suffix(".trace.json")

    typ_path.write_text(canvas.typst())
    trace_path.write_text(json.dumps(
        {
            "input": str(args.input),
            "role": args.role,
            "shape": doc.shape,
            "pointer_prefix": doc.prefix,
            "elements": canvas.trace,
        },
        indent=2,
    ) + "\n")

    proc = subprocess.run(
        [args.typst, "compile", str(typ_path), str(png_path), "--format", "png",
         "--ppi", str(args.ppi)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        return 1

    data = sum(1 for e in canvas.trace if e["kind"] == "data")
    chrome = sum(1 for e in canvas.trace if e["kind"] == "chrome")
    print(f"{typ_path}\n{png_path}\n{trace_path}")
    print(f"elements: {data} from data, {chrome} fixed labels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
