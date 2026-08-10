#!/usr/bin/env python3
"""Render a harness's execution graph (lanes, gates, fan-out/in, loop-backs) as a
dark, neon-glow PNG, from a JSON graph spec. See ../references/graph_schema.md
for the full spec and worked examples.

Usage:
    python3 render_graph.py graph.json -o graph.png
    python3 render_graph.py graph.json -o graph.png --svg-out graph.svg  # keep the SVG
    cat graph.json | python3 render_graph.py - -o graph.png

Why SVG-then-rasterize rather than a diagramming library: the graph is a real
directed graph with lanes, fan-out, fan-in and loop-backs, not a single chain — it
needs an explicit layout model (grid position per node, orthogonal edge routing)
that a generic auto-layout library will not reproduce deterministically run to run.
Describing it as data and laying it out by hand, the way this repo's
plan-infographic skill already does for a simpler single-spine case, keeps the
result reproducible: the same JSON always produces the same picture. This is the
same deterministic-layout idea `plans/22_graph_eng_evol_01/graph.v1.png` was
hand-prompted into an image model for, minus the un-reproducibility: same look,
but the spec is a file you can diff, not a prompt that's gone the moment the chat
scrolls past it.

Layout model, briefly (full detail in references/graph_schema.md):
  - `lanes` is an ordered list of grid ROWS (top to bottom). Consecutive rows that
    share the same non-null `label` are drawn as one merged zone with one floating
    label, which is how a single semantic zone (e.g. "EVOLUTION") can span several
    rows of actual nodes (e.g. select_parents / the four operators / merge_offspring).
  - Every node sits at an explicit (lane, col) grid cell. Columns share one x-axis
    across all lanes, so nodes in different lanes still line up visually.
  - Edges route automatically from the geometry of their endpoints, with rounded
    (not sharp) corners so parallel runs read as pipes rather than wiring diagrams:
      * same lane, adjacent column      -> a straight arrow
      * same lane, skipped columns      -> a small bump above the row
      * forward, different lane         -> an orthogonal elbow via a shared bus
                                            row between the two lanes (this is
                                            what makes fan-out/fan-in "just work":
                                            edges that share a source/lane pair
                                            share a bus, which reads as a fan)
      * backward (loops, retries)       -> routed around the outside on a rail
                                            below the whole diagram, one rail
                                            depth per overlapping loop edge
  Edge `style` ("flow" default / "loop" / "check") only controls stroke (solid vs
  dashed) and colour — it does not change the geometry above. Reserve `style:
  "loop"` for a genuine return to an earlier point in the SAME run (a new
  generation, a retry); a finding or rejection that simply flows down into an
  already-adjacent lane is cheaper and clearer as a plain (dashed `check`, if you
  want it visually distinct) elbow — see references/graph_schema.md's rough-edge
  note on this before reaching for `loop` out of habit.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

# --------------------------------------------------------------------- palette
# Two themes, same five-role grammar, chosen with --theme at render time:
#   dark  — deep navy canvas, glowing role-coloured borders, solid-fill terminal
#           pills. The same visual language as plans/22_graph_eng_evol_01/
#           graph.v1.png, for reading on a screen at a glance.
#   light — white canvas, light role-tinted fills, no glow. For printing or
#           pasting into a doc, and the default: most consumers of a diagram
#           in this repo need it on white, and dark should be an opt-in.
# Every other visual choice (geometry, routing, rounded corners, terminal
# sizing) is identical between themes — only ink/fill/glow differ.
THEMES = {
    "dark": {
        "bg": "#0a0e1a", "card_fill": "#121a2b", "text": "#f1f5f9",
        "text_muted": "#93a3b8", "rule": "#28344a", "glow": True,
        "roles": {
            "primary": {"ink": "#22d3ee", "fill": "#0e2230"},
            "support": {"ink": "#34d399", "fill": "#0e2420"},
            "accent": {"ink": "#a78bfa", "fill": "#1c1a33"},
            "caution": {"ink": "#fbbf24", "fill": "#2a2110"},
            "alert": {"ink": "#f87171", "fill": "#2a1414"},
            "success": {"ink": "#16a34a", "fill": "#22c55e"},
            "failure": {"ink": "#b91c1c", "fill": "#ef4444"},
            "neutral": {"ink": "#94a3b8", "fill": "#1a2233"},
        },
    },
    "light": {
        "bg": "#ffffff", "card_fill": "#ffffff", "text": "#17202a",
        "text_muted": "#5f6b76", "rule": "#c8d0d7", "glow": False,
        "roles": {
            "primary": {"ink": "#174a7e", "fill": "#eaf2f9"},
            "support": {"ink": "#146447", "fill": "#e9f5ef"},
            "accent": {"ink": "#6b3fa0", "fill": "#f1ecf8"},
            "caution": {"ink": "#875b00", "fill": "#fbf3df"},
            "alert": {"ink": "#9b352d", "fill": "#faecea"},
            "success": {"ink": "#146447", "fill": "#22c55e"},
            "failure": {"ink": "#9b352d", "fill": "#ef4444"},
            "neutral": {"ink": "#17202a", "fill": "#eef1f4"},
        },
    },
}


# --------------------------------------------------------------------- geometry
COL_W = 230
COL_GAP = 70
COL_PITCH = COL_W + COL_GAP
LEFT_MARGIN = 40
X0 = LEFT_MARGIN

LANE_PITCH = 168
TOP_MARGIN = 110
BOTTOM_RAIL_GAP = 64   # space between the last lane and the first loop rail
LOOP_RAIL_DX = 50      # vertical spacing between stacked loop rails
RIGHT_MARGIN = 120
BOTTOM_MARGIN = 60

STAGE_H = 84
GATE_W, GATE_H = 210, 130
TERM_W, TERM_H = 190, 58

F_TITLE = 18.5
F_DETAIL = 13
F_EDGE = 13
F_LANE = 19
F_MAIN_TITLE = 30

BUMP_H = 40       # how far a same-lane skip edge arcs above its row
BUS_HUG = 30      # how far a cross-lane elbow's bus sits from its source row
CORNER_R = 18     # corner rounding radius for multi-segment edge paths
RAIL_JITTER = 17  # horizontal spacing between loop-rail edges that share an endpoint
RAIL_DOGLEG = 18  # length of the final straight run back onto the shared endpoint


def terminal_width(label: str) -> float:
    """A fixed TERM_W clips harnesses' own SCREAMING_SNAKE_CASE terminal names
    (QA_INTEGRITY_BREACH, CONVERGENCE_EXHAUSTED, ...) — widen to fit the label,
    capped so it can't bleed into the next column's node."""
    avg = F_TITLE * 0.62  # bold text runs wider than the 0.56 used for body copy
    needed = len(label) * avg + 44
    return max(TERM_W, min(needed, COL_PITCH - 30))


def wrap(text: str, font_size: float, max_px: float) -> list[str]:
    if not text:
        return []
    avg = font_size * 0.56
    limit = max(6, int(max_px / avg))
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if len(trial) <= limit or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_el(x, y, s, size, fill, weight=400, anchor="middle", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" font-style="{style}" text-anchor="{anchor}" '
            f'font-family="Helvetica,Arial,ui-sans-serif,sans-serif">{escape(s)}</text>')


def color_id(hexcolor: str) -> str:
    return "c" + hexcolor.lstrip("#")


def rounded_path(points: list[tuple[float, float]], radius: float = CORNER_R) -> str:
    """An SVG path through `points` with rounded (not mitred) corners, so a
    multi-segment route reads as a pipe/cable rather than a wiring schematic —
    this is most of what separates the neon-diagram look from a plain flowchart."""
    if len(points) <= 2:
        (x0, y0), (x1, y1) = points[0], points[-1]
        return f'M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}'
    d = [f'M{points[0][0]:.1f},{points[0][1]:.1f}']
    for i in range(1, len(points) - 1):
        x0, y0 = points[i - 1]
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        v1x, v1y = x1 - x0, y1 - y0
        l1 = max((v1x ** 2 + v1y ** 2) ** 0.5, 1e-6)
        v2x, v2y = x2 - x1, y2 - y1
        l2 = max((v2x ** 2 + v2y ** 2) ** 0.5, 1e-6)
        rr = min(radius, l1 / 2, l2 / 2)
        pa = (x1 - v1x / l1 * rr, y1 - v1y / l1 * rr)
        pb = (x1 + v2x / l2 * rr, y1 + v2y / l2 * rr)
        d.append(f'L{pa[0]:.1f},{pa[1]:.1f}')
        d.append(f'Q{x1:.1f},{y1:.1f} {pb[0]:.1f},{pb[1]:.1f}')
    d.append(f'L{points[-1][0]:.1f},{points[-1][1]:.1f}')
    return " ".join(d)


class Graph:
    def __init__(self, spec: dict):
        self.title = spec.get("title", "")
        self.lanes = spec.get("lanes", [])
        if not self.lanes:
            raise SystemExit("render_graph: `lanes` is empty — nothing to draw.")
        self.lane_index = {ln["id"]: i for i, ln in enumerate(self.lanes)}
        self.nodes = {n["id"]: n for n in spec.get("nodes", [])}
        if not self.nodes:
            raise SystemExit("render_graph: `nodes` is empty — nothing to draw.")
        self.edges = spec.get("edges", [])
        for n in self.nodes.values():
            if n["lane"] not in self.lane_index:
                raise SystemExit(f"render_graph: node {n['id']!r} references unknown lane {n['lane']!r}")
        for e in self.edges:
            if e["from"] not in self.nodes or e["to"] not in self.nodes:
                raise SystemExit(f"render_graph: edge {e!r} references an unknown node id")

    def node_kind(self, n: dict) -> str:
        return {"start": "terminal", "stop": "terminal"}.get(n["kind"], n["kind"])

    def node_size(self, n: dict) -> tuple[float, float]:
        kind = self.node_kind(n)
        if kind == "gate":
            return GATE_W, GATE_H
        if kind == "terminal":
            return terminal_width(n["label"]), TERM_H
        return COL_W, STAGE_H

    def cell_center(self, lane_id: str, col: int) -> tuple[float, float]:
        li = self.lane_index[lane_id]
        cx = X0 + col * COL_PITCH + COL_W / 2
        cy = TOP_MARGIN + li * LANE_PITCH + LANE_PITCH / 2
        return cx, cy

    def bounds(self) -> tuple[float, float]:
        max_col = max(n["col"] for n in self.nodes.values())
        width = X0 + (max_col + 1) * COL_PITCH + RIGHT_MARGIN
        height = TOP_MARGIN + len(self.lanes) * LANE_PITCH + BOTTOM_MARGIN
        return width, height

    def lane_bands(self) -> list[dict]:
        """Group consecutive rows sharing a label into one semantic zone, so a
        zone spanning several node rows (like the EVOLUTION section) gets one
        floating label instead of one per row."""
        bands = []
        i = 0
        while i < len(self.lanes):
            ln = self.lanes[i]
            label = ln.get("label")
            j = i
            while j + 1 < len(self.lanes) and self.lanes[j + 1].get("label") == label and label is not None:
                j += 1
            bands.append({"label": label, "role": ln.get("role"), "start": i, "end": j})
            i = j + 1
        return bands


def build(spec: dict, theme: str = "light") -> str:
    g = Graph(spec)
    width, base_height = g.bounds()

    th = THEMES[theme]
    BG, TEXT, TEXT_MUTED, RULE = th["bg"], th["text"], th["text_muted"], th["rule"]
    GLOW = th["glow"]
    glow_attr = ' filter="url(#glow)"' if GLOW else ""

    def role(name: str | None) -> dict:
        return th["roles"].get(name or "neutral", th["roles"]["neutral"])

    used_colors: set[str] = set()

    # ---- pass 1: classify every edge's route and count outer-rail edges -----
    # The canvas has to be tall enough to hold the rail before we emit the
    # <svg> header, so routing decisions happen before any string is written.
    routed = []
    loop_rail_used = 0
    for e in g.edges:
        a, b = g.nodes[e["from"]], g.nodes[e["to"]]
        style = e.get("style", "flow")
        stroke = {"flow": TEXT_MUTED, "loop": role("caution")["ink"], "check": role("accent")["ink"]}.get(style, TEXT_MUTED)
        used_colors.add(stroke)

        ax, ay = g.cell_center(a["lane"], a["col"])
        bx, by = g.cell_center(b["lane"], b["col"])
        aw, ah = g.node_size(a)
        bw, bh = g.node_size(b)
        li_a, li_b = g.lane_index[a["lane"]], g.lane_index[b["lane"]]
        dcol = b["col"] - a["col"]
        same_row = li_a == li_b

        # Routing is decided by geometry EXCEPT that only a genuine loop (or a
        # same-row edge with nowhere else to go) pays for the outer rail — an
        # ordinary forward transition that happens to land at an earlier column
        # (e.g. a gate's "no eligible target" edge dropping into an earlier-
        # numbered node in the lane below) still gets the cheap direct elbow,
        # not a trip around the whole diagram.
        if same_row and dcol == 1:
            kind = "straight"
        elif same_row and dcol > 1:
            kind = "bump"
        elif style == "loop" or (same_row and dcol <= 0):
            kind = "rail"
        else:
            kind = "elbow"

        rail_index = None
        if kind == "rail":
            rail_index = loop_rail_used
            loop_rail_used += 1

        routed.append(dict(e=e, style=style, stroke=stroke, ax=ax, ay=ay, bx=bx, by=by,
                            aw=aw, ah=ah, bw=bw, bh=bh, kind=kind, rail_index=rail_index))

    # Multiple rail edges sharing a source or target node would otherwise route
    # their vertical run down the exact same x, so they'd sit on top of each
    # other and read as one edge instead of several. Group rail edges by shared
    # endpoint and give each a small horizontal jitter for most of its run, with
    # a short dogleg back onto the true endpoint so the arrowhead still lands
    # exactly on the node.
    rail_edges = [r for r in routed if r["kind"] == "rail"]
    for r in rail_edges:
        r["jitter_a"] = 0.0
        r["jitter_b"] = 0.0

    def spread(edges: list[dict], key: str):
        if len(edges) < 2:
            return
        for i, r in enumerate(edges):
            r[key] = (i - (len(edges) - 1) / 2) * RAIL_JITTER

    from_groups: dict[str, list[dict]] = {}
    to_groups: dict[str, list[dict]] = {}
    for r in rail_edges:
        from_groups.setdefault(r["e"]["from"], []).append(r)
        to_groups.setdefault(r["e"]["to"], []).append(r)
    for group in from_groups.values():
        spread(group, "jitter_a")
    for group in to_groups.values():
        spread(group, "jitter_b")

    height = base_height
    if loop_rail_used:
        height = max(height, TOP_MARGIN + len(g.lanes) * LANE_PITCH + BOTTOM_RAIL_GAP
                     + loop_rail_used * LOOP_RAIL_DX + BOTTOM_MARGIN)

    out: list[str] = []
    out.append(
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}" '
        f'role="img" aria-label="{escape(g.title or "Harness execution graph")}" '
        f'xmlns="http://www.w3.org/2000/svg">'
    )
    out.append(f'<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" fill="{BG}"/>')

    # ---- zone labels (floating, no background tint) -------------------------
    # No full-width tinted band: at this dark/dense a filled band reads as more
    # visual weight than the zone boundary is worth. A bold, role-coloured label
    # floating above the zone's own left-most node is enough to read as a
    # section, the way graph.v1.png's own EVALUATION/EVOLUTION labels do.
    for band in g.lane_bands():
        if band["label"] is None:
            continue
        y0 = TOP_MARGIN + band["start"] * LANE_PITCH
        nodes_in_band = [n for n in g.nodes.values() if band["start"] <= g.lane_index[n["lane"]] <= band["end"]]
        label_x = min((g.cell_center(n["lane"], n["col"])[0] - g.node_size(n)[0] / 2 for n in nodes_in_band),
                      default=X0)
        r = role(band["role"])
        out.append(text_el(label_x, y0 + 22, band["label"].upper(), F_LANE, r["ink"], weight=700, anchor="start"))

    # ---- title ---------------------------------------------------------------
    if g.title:
        out.append(text_el(LEFT_MARGIN, 50, g.title, F_MAIN_TITLE, TEXT, weight=700, anchor="start"))

    # ---- pass 2: emit the routed edges ---------------------------------------
    for r in routed:
        e, style, stroke = r["e"], r["style"], r["stroke"]
        ax, ay, bx, by = r["ax"], r["ay"], r["bx"], r["by"]
        aw, ah, bw, bh = r["aw"], r["ah"], r["bw"], r["bh"]
        dash = ' stroke-dasharray="7 6"' if style in ("loop", "check") else ""
        marker = f"url(#ah_{color_id(stroke)})"

        if r["kind"] == "straight":
            x1, x2 = ax + aw / 2, bx - bw / 2
            points = [(x1, ay), (x2 - 2, by)]
            label_xy = ((x1 + x2) / 2, ay - 12)
        elif r["kind"] == "bump":
            y_bump = ay - ah / 2 - BUMP_H
            points = [(ax, ay - ah / 2), (ax, y_bump), (bx, y_bump), (bx, by - bh / 2 - 2)]
            label_xy = ((ax + bx) / 2, y_bump - 8)
        elif r["kind"] == "elbow":
            going_down = by > ay
            y_exit = ay + ah / 2 if going_down else ay - ah / 2
            y_entry = by - bh / 2 if going_down else by + bh / 2
            # Hug the bus close to the SOURCE row rather than the true midpoint.
            # An edge that skips several lanes still has to travel through the
            # rows in between; hugging the source keeps that horizontal run in
            # the source row's own whitespace margin instead of drifting into
            # an unrelated row's node band further down/up.
            bus_y = y_exit + BUS_HUG if going_down else y_exit - BUS_HUG
            if going_down and bus_y > y_entry:
                bus_y = (y_exit + y_entry) / 2
            if not going_down and bus_y < y_entry:
                bus_y = (y_exit + y_entry) / 2
            points = [(ax, y_exit), (ax, bus_y), (bx, bus_y), (bx, y_entry - (2 if going_down else -2))]
            if ax != bx:
                label_xy = ((ax + bx) / 2, bus_y - 8)
            else:
                # A same-column elbow (source and target directly above/below
                # each other) has no horizontal run to hang a label on near the
                # bus — and that bus row is exactly where OTHER edges leaving the
                # same source fan out, so a label parked there collides with
                # theirs. Anchor it by the target instead, where a divergent
                # branch's siblings have already spread apart.
                label_xy = (bx, y_entry - (16 if going_down else -22))
        else:  # rail
            rail_y = TOP_MARGIN + len(g.lanes) * LANE_PITCH + BOTTOM_RAIL_GAP + r["rail_index"] * LOOP_RAIL_DX
            y_exit = ay + ah / 2
            y_entry = by + bh / 2
            ja, jb = r.get("jitter_a", 0), r.get("jitter_b", 0)
            if ja or jb:
                # Several loop-backs share this source or target node — jitter
                # the long horizontal run sideways so the parallel edges stay
                # visually distinct, then dogleg back onto the true endpoint so
                # the arrowhead still lands exactly on the node.
                ax_j, bx_j = ax + ja, bx + jb
                points = [(ax, y_exit), (ax_j, y_exit + RAIL_DOGLEG), (ax_j, rail_y),
                          (bx_j, rail_y), (bx_j, y_entry - RAIL_DOGLEG), (bx, y_entry - 2)]
            else:
                points = [(ax, y_exit), (ax, rail_y), (bx, rail_y), (bx, y_entry - 2)]
            label_xy = ((ax + bx) / 2, rail_y + 18)

        path = rounded_path(points)
        out.append(f'<path d="{path}" fill="none" stroke="{stroke}" stroke-width="2.2"{dash} '
                    f'stroke-linecap="round" marker-end="{marker}"{glow_attr}/>')
        if e.get("label"):
            lx, ly = label_xy
            lw = len(e["label"]) * 7.2
            out.append(f'<rect x="{lx - lw / 2:.1f}" y="{ly - 13:.1f}" width="{lw:.1f}" height="18" '
                        f'fill="{BG}" opacity="0.92" rx="3"/>')
            out.append(text_el(lx, ly, e["label"], F_EDGE, stroke, weight=600))

    marker_defs = []
    for c in used_colors:
        marker_defs.append(
            f'<marker id="ah_{color_id(c)}" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
        )
    glow_filter = (
        '<filter id="glow" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="2.6" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    ) if GLOW else ""
    out.insert(2, f'<defs>{glow_filter}{"".join(marker_defs)}</defs>')

    # ---- nodes (drawn after edges so they sit on top of any bus lines) -------
    for n in g.nodes.values():
        kind = g.node_kind(n)
        cx, cy = g.cell_center(n["lane"], n["col"])
        w, h = g.node_size(n)
        role_name = n.get("role") or g.lanes[g.lane_index[n["lane"]]].get("role")
        r = role(role_name)
        if n.get("kind") == "start":
            role_name = n.get("role", "neutral")
            r = role(role_name)
        if n.get("kind") == "stop" and "role" not in n:
            role_name = "failure"
            r = role(role_name)

        if kind == "terminal":
            # success/failure terminals get a solid saturated fill in both
            # themes, so white text reads well; every other role's fill is
            # light in the light theme and would swallow white text.
            term_text = "#ffffff" if role_name in ("success", "failure") else TEXT
            out.append(f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.0f}" height="{h:.0f}" '
                        f'rx="{h / 2:.0f}" fill="{r["fill"]}" stroke="{r["ink"]}" stroke-width="2"{glow_attr}/>')
            out.append(text_el(cx, cy + 6, n["label"], F_TITLE, term_text, weight=700))
        elif kind == "gate":
            hw, hh = w / 2, h / 2
            out.append(f'<path d="M{cx},{cy - hh} L{cx + hw},{cy} L{cx},{cy + hh} L{cx - hw},{cy} Z" '
                        f'fill="{r["fill"]}" stroke="{r["ink"]}" stroke-width="2"{glow_attr}/>')
            lines = wrap(n["label"], F_DETAIL + 1, w - 100)
            ty = cy - (len(lines) - 1) * 9
            for line in lines:
                out.append(text_el(cx, ty + 5, line, F_DETAIL + 1, TEXT, weight=700))
                ty += 18
        else:  # stage
            out.append(f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.0f}" height="{h:.0f}" '
                        f'rx="10" fill="{r["fill"]}" stroke="{r["ink"]}" stroke-width="2"{glow_attr}/>')
            lines = wrap(n["label"], F_TITLE, w - 36)
            detail_lines = wrap(n.get("detail", ""), F_DETAIL, w - 36) if n.get("detail") else []
            block_h = len(lines) * 22 + (6 + len(detail_lines) * 16 if detail_lines else 0)
            ty = cy - block_h / 2 + 15
            for line in lines:
                out.append(text_el(cx, ty, line, F_TITLE, TEXT, weight=700))
                ty += 22
            if detail_lines:
                ty += 3
                for line in detail_lines:
                    out.append(text_el(cx, ty, line, F_DETAIL, TEXT_MUTED))
                    ty += 16

    out.append("</svg>")
    return "\n".join(out)


# ------------------------------------------------------------------------- io
def rasterize(svg_text: str, out_png: Path, bg: str, min_width: int = 1800) -> None:
    import re
    m = re.search(r'width="(\d+)"', svg_text)
    svg_w = int(m.group(1)) if m else min_width
    args = ["rsvg-convert", "-o", str(out_png), "--background-color", bg]
    if svg_w < min_width:
        args += ["--width", str(min_width)]
    args.append("-")
    proc = subprocess.run(args, input=svg_text.encode("utf-8"), capture_output=True)
    if proc.returncode != 0:
        sys.exit(f"render_graph: rsvg-convert failed:\n{proc.stderr.decode('utf-8', 'replace')}")


def main():
    ap = argparse.ArgumentParser(description="Render a harness execution-graph spec to a PNG.")
    ap.add_argument("spec", help="path to the graph JSON, or - for stdin")
    ap.add_argument("-o", "--out", required=True, help="PNG path to write")
    ap.add_argument("--theme", choices=sorted(THEMES), default="light",
                     help="light (white, print-safe, default) or dark (neon-glow, matches graph.v1.png)")
    ap.add_argument("--svg-out", help="also write the intermediate SVG here (optional, for debugging)")
    ap.add_argument("--force", action="store_true", help="allow overwriting an existing PNG (you almost never want this)")
    ap.add_argument("--min-width", type=int, default=1800)
    a = ap.parse_args()

    out_png = Path(a.out)
    if out_png.exists() and not a.force:
        sys.exit(
            f"render_graph: refusing to overwrite existing {out_png}.\n"
            f"  Resolve a new version instead — {Path(__file__).with_name('outpath.py').name} "
            f"resolves matching PNG/json/prompt.md paths together:\n"
            f"    read -r OUT_PNG OUT_JSON OUT_PROMPT <<< \"$(python3 "
            f"{Path(__file__).with_name('outpath.py')} <viz-dir> <name>)\"\n"
            f"  Pass --force only if you are certain the old file is disposable."
        )

    raw = sys.stdin.read() if a.spec == "-" else Path(a.spec).read_text(encoding="utf-8")
    svg = build(json.loads(raw), theme=a.theme)

    if a.svg_out:
        Path(a.svg_out).write_text(svg, encoding="utf-8")

    rasterize(svg, out_png, bg=THEMES[a.theme]["bg"], min_width=a.min_width)
    print(f"wrote {out_png}", file=sys.stderr)


if __name__ == "__main__":
    main()
