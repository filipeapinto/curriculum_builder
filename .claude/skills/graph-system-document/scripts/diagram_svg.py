#!/usr/bin/env python3
"""Render a documentation diagram as an accessible, self-contained <figure>.

Hand-plotting SVG coordinates is where documentation diagrams go wrong: labels
spill out of boxes, arrows cross through text, back-edges get scribbled over the
forward flow, and nobody notices until the page is in front of a reader. This
script computes the layout from the content, so the geometry is a consequence of
the text rather than a guess about it — and then inspects its own output for
overlap, clipping and unreachable nodes before handing it over.

Three archetypes, because they answer three different reader questions:

    flow      "what runs, in what order, and where does it go wrong?"
              stages as columns, typed edges, repair/back-edges routed through a
              dedicated gutter beneath the flow instead of across it.
    stack     "what are the parts and which side of a boundary do they sit on?"
              labelled groups (layers, trust zones, environments) holding boxes.
    sequence  "who talks to whom, in what order, over time?"
              actors as lifelines, ordered messages, notes.

Usage:
    python3 diagram_svg.py spec.json > figure.html      # <figure> with inline SVG
    python3 diagram_svg.py spec.json --svg-only --out docs/assets/graph.svg
    python3 diagram_svg.py --print-schema                # spec format + example

Exit 0 when the diagram rendered and self-inspection found nothing; 1 when the
spec is structurally broken (edge to an unknown node, duplicate id) or the render
inspects badly; 2 on usage error. Self-inspection findings go to stderr so the
figure itself stays pipeable.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys

# ---------------------------------------------------------------------------
# Geometry constants. Tuned for a ~1100px content column at 100% zoom, which is
# the width the guide template gives a full-bleed figure.
# ---------------------------------------------------------------------------

PAD = 28              # canvas margin
NODE_W = 208          # node box width (fixed, so columns align)
NODE_PAD_X = 14
NODE_PAD_Y = 12
COL_GAP = 96          # horizontal space between stage columns — room for labels
ROW_GAP = 26          # vertical space between nodes in a column
TITLE_SIZE = 14
NOTE_SIZE = 11.5
LABEL_SIZE = 11
LINE_H = 1.35
GUTTER_LANE = 34      # vertical space each back-edge lane occupies
CHAR_W = 0.56         # mean advance width of the UI sans stack, in em

EVIDENCE_MARK = {
    "declared": "declared",
    "observed": "observed",
    "inferred": "inferred",
    "unknown": "unknown",
    "conflicting": "conflicting",
}

# Node kinds differ by accent colour AND border treatment AND badge text, so the
# distinction survives greyscale printing and colour-blind readers.
KINDS = {
    "node":     {"accent": "#175cc2", "dash": None,    "badge": "",         "stadium": False},
    "gate":     {"accent": "#8d5b00", "dash": None,    "badge": "gate",     "stadium": False},
    "terminal": {"accent": "#087f67", "dash": None,    "badge": "terminal", "stadium": True},
    "external": {"accent": "#6b5bd2", "dash": "5 4",   "badge": "external", "stadium": False},
    "store":    {"accent": "#0f7490", "dash": "1 5",   "badge": "store",    "stadium": False},
    "human":    {"accent": "#b03060", "dash": "8 4",   "badge": "human",    "stadium": False},
}

EDGE_KINDS = {
    "forward":  {"accent": "#3d4c66", "dash": None,   "head": "arrow"},
    "branch":   {"accent": "#175cc2", "dash": "6 4",  "head": "arrow"},
    "repair":   {"accent": "#8d5b00", "dash": "3 4",  "head": "arrow"},
    "failure":  {"accent": "#b3261e", "dash": "8 5",  "head": "arrow"},
    "data":     {"accent": "#0f7490", "dash": "2 4",  "head": "arrow"},
}


def die(msg: str, code: int = 2) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(code)


def text_w(s: str, size: float) -> float:
    return len(s) * size * CHAR_W


def wrap(text: str, size: float, max_px: float) -> list[str]:
    """Greedy wrap on words, breaking over-long tokens (paths, snake_case ids)."""
    if not text:
        return []
    max_chars = max(6, int(max_px / (size * CHAR_W)))
    lines: list[str] = []
    for word in str(text).split():
        while len(word) > max_chars:
            cut = max_chars
            for sep in ("/", "_", "-", "."):
                idx = word.rfind(sep, 0, max_chars)
                if idx > max_chars * 0.5:
                    cut = idx + 1
                    break
            lines.append(word[:cut])
            word = word[cut:]
        if not lines or len(lines[-1]) + len(word) + 1 > max_chars:
            lines.append(word)
        else:
            lines[-1] += " " + word
    return lines


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "d"


# ---------------------------------------------------------------------------
# SVG primitives
# ---------------------------------------------------------------------------

def svg_text(x: float, y: float, lines: list[str], size: float, cls: str,
             anchor: str = "start") -> str:
    out = []
    for i, line in enumerate(lines):
        dy = y + i * size * LINE_H
        out.append(f'<text x="{x:.1f}" y="{dy:.1f}" class="{cls}" '
                   f'text-anchor="{anchor}">{esc(line)}</text>')
    return "".join(out)


def chip_rect(x: float, y: float, text: str) -> tuple:
    w = text_w(text, LABEL_SIZE) + 10
    h = LABEL_SIZE + 8
    return (x - w / 2, y - h / 2, w, h)


def overlaps(a: tuple, b: tuple) -> bool:
    ox = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    oy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return ox > 2 and oy > 2


def place_labels(pending: list[tuple], boxes: list[tuple]) -> str:
    """Nudge edge labels off whatever they landed on.

    An edge label that sits on a node or on another label is the defect readers
    notice first, and it is nearly always fixable by moving the label a few
    pixels along its own line — so do that here rather than making the writer
    shorten a label that was telling the truth.
    """
    out = []
    for x, y, text, axis in pending:
        best = None
        for step in (0, -20, 20, -40, 40, -62, 62, -86, 86):
            cand = chip_rect(x + step, y, text) if axis == "h" else chip_rect(x, y + step, text)
            if not any(overlaps(cand, (b[0], b[1], b[2], b[3])) for b in boxes):
                best = cand
                break
        if best is None:
            best = chip_rect(x, y, text)
        cx, cy = best[0] + best[2] / 2, best[1] + best[3] / 2
        markup, rect = label_chip(cx, cy, text)
        out.append(markup)
        boxes.append((*rect, f'label {text}'))
    return "".join(out)


def label_chip(x: float, y: float, text: str, cls: str = "elabel") -> tuple[str, tuple]:
    """A short edge label on an opaque plate, so a line never reads through it."""
    w = text_w(text, LABEL_SIZE) + 10
    h = LABEL_SIZE + 8
    rect = (x - w / 2, y - h / 2, w, h)
    markup = (f'<rect x="{rect[0]:.1f}" y="{rect[1]:.1f}" width="{w:.1f}" height="{h:.1f}" '
              f'rx="4" class="plate"/>'
              f'<text x="{x:.1f}" y="{y + LABEL_SIZE * 0.36:.1f}" class="{cls}" '
              f'text-anchor="middle">{esc(text)}</text>')
    return markup, rect


# ---------------------------------------------------------------------------
# Archetype: flow
# ---------------------------------------------------------------------------

def layout_flow(spec: dict) -> tuple[str, float, float, list[dict], list[tuple]]:
    nodes = spec.get("nodes") or []
    edges = spec.get("edges") or []
    stages = spec.get("stages") or []
    problems: list[dict] = []

    by_id = {}
    for n in nodes:
        nid = n.get("id")
        if not nid:
            die("every node needs an id")
        if nid in by_id:
            problems.append({"severity": "fail", "message": f"duplicate node id: {nid}"})
        by_id[nid] = n

    # Column assignment: declared stages win; otherwise longest-path from the
    # sources, which puts a node after everything that must precede it.
    if stages:
        order = {s["id"] if isinstance(s, dict) else s: i for i, s in enumerate(stages)}
        for n in nodes:
            st = n.get("stage")
            if st is not None and st not in order:
                problems.append({"severity": "fail",
                                 "message": f"node {n['id']} names unknown stage '{st}'"})
            n["_col"] = order.get(st, 0)
    else:
        depth = {n["id"]: 0 for n in nodes}
        fwd = [e for e in edges if (e.get("kind") or "forward") != "repair"]
        for _ in range(len(nodes)):
            changed = False
            for e in fwd:
                a, b = e.get("from"), e.get("to")
                if a in depth and b in depth and depth[b] < depth[a] + 1:
                    depth[b] = depth[a] + 1
                    changed = True
            if not changed:
                break
        for n in nodes:
            n["_col"] = depth[n["id"]]

    for e in edges:
        for end in ("from", "to"):
            if e.get(end) not in by_id:
                problems.append({"severity": "fail",
                                 "message": f"edge {e.get('from')}→{e.get('to')} references "
                                            f"unknown node '{e.get(end)}'"})
    if any(p["severity"] == "fail" for p in problems):
        return "", 0, 0, problems, []

    # Reachability is a documentation smell worth reporting, not a render error.
    reachable = {n["id"] for n in nodes if n.get("entry")} or \
                {n["id"] for n in nodes if n["_col"] == min(x["_col"] for x in nodes)}
    frontier = set(reachable)
    while frontier:
        nxt = {e["to"] for e in edges if e["from"] in frontier} - reachable
        reachable |= nxt
        frontier = nxt
    for n in nodes:
        if n["id"] not in reachable:
            problems.append({"severity": "warn",
                             "message": f"node '{n['id']}' is not reachable by any edge — "
                                        f"an orphan in the diagram is usually a missing edge "
                                        f"in the evidence"})

    cols: dict[int, list[dict]] = {}
    for n in nodes:
        cols.setdefault(n["_col"], []).append(n)

    # Measure each node, then place columns.
    for n in nodes:
        inner = NODE_W - 2 * NODE_PAD_X
        n["_title"] = wrap(n.get("label") or n["id"], TITLE_SIZE, inner)
        n["_note"] = wrap(n.get("note") or "", NOTE_SIZE, inner)
        kind = KINDS.get(n.get("kind") or "node", KINDS["node"])
        badge = kind["badge"] or (n.get("evidence") or "")
        n["_badge"] = badge
        h = NODE_PAD_Y * 2 + len(n["_title"]) * TITLE_SIZE * LINE_H
        if n["_note"]:
            h += 4 + len(n["_note"]) * NOTE_SIZE * LINE_H
        if badge:
            h += LABEL_SIZE + 4
        n["_h"] = max(58, h)

    stage_label_h = 30 if stages else 0
    top = PAD + stage_label_h
    max_col_h = 0.0
    for ci in sorted(cols):
        y = top
        for n in cols[ci]:
            n["_x"] = PAD + ci * (NODE_W + COL_GAP)
            n["_y"] = y
            y += n["_h"] + ROW_GAP
        max_col_h = max(max_col_h, y - ROW_GAP)

    # Vertically centre short columns against the tallest one; a ragged top edge
    # reads as meaning that isn't there.
    for ci in sorted(cols):
        colh = sum(n["_h"] for n in cols[ci]) + ROW_GAP * (len(cols[ci]) - 1)
        offset = (max_col_h - top - colh) / 2
        for n in cols[ci]:
            n["_y"] += offset

    # Only a genuine backwards jump earns a gutter lane. A same-column edge is a
    # short hop and belongs beside the column, not in a loop under the whole
    # diagram — routing it there is what makes repair loops stop standing out.
    back = [e for e in edges if by_id[e["to"]]["_col"] < by_id[e["from"]]["_col"]]
    gutter_h = (len(back) * GUTTER_LANE + 24) if back else 0
    width = PAD * 2 + (max(cols) + 1) * NODE_W + max(cols) * COL_GAP
    height = max_col_h + gutter_h + PAD

    body: list[str] = []
    boxes: list[tuple] = []

    if stages:
        for i, s in enumerate(stages):
            lbl = s.get("label") if isinstance(s, dict) else str(s)
            x = PAD + i * (NODE_W + COL_GAP)
            body.append(f'<text x="{x:.1f}" y="{PAD + 14:.1f}" class="stage">{esc(lbl).upper()}</text>')
            body.append(f'<line x1="{x:.1f}" y1="{PAD + 22:.1f}" x2="{x + NODE_W:.1f}" '
                        f'y2="{PAD + 22:.1f}" class="stagerule"/>')
            # Reserve the header band so edge labels route around it rather than
            # through it — a label sitting on a stage name reads as neither.
            boxes.append((x - 4, PAD, max(NODE_W, text_w(lbl.upper(), 11) * 1.15) + 8, 26,
                          f'stage header {lbl}'))

    for n in nodes:
        kind = KINDS.get(n.get("kind") or "node", KINDS["node"])
        x, y, h = n["_x"], n["_y"], n["_h"]
        rx = h / 2 if kind["stadium"] else 12
        dash = f' stroke-dasharray="{kind["dash"]}"' if kind["dash"] else ""
        body.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{NODE_W}" height="{h:.1f}" '
                    f'rx="{rx:.1f}" class="node" stroke="{kind["accent"]}"{dash}/>')
        if not kind["stadium"]:
            body.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="5" height="{h:.1f}" '
                        f'rx="2.5" fill="{kind["accent"]}"/>')
        ty = y + NODE_PAD_Y + TITLE_SIZE * 0.85
        body.append(svg_text(x + NODE_PAD_X, ty, n["_title"], TITLE_SIZE, "ntitle"))
        ty += len(n["_title"]) * TITLE_SIZE * LINE_H
        if n["_note"]:
            ty += 4
            body.append(svg_text(x + NODE_PAD_X, ty, n["_note"], NOTE_SIZE, "nnote"))
            ty += len(n["_note"]) * NOTE_SIZE * LINE_H
        if n["_badge"]:
            body.append(f'<text x="{x + NODE_PAD_X:.1f}" y="{ty + LABEL_SIZE * 0.6:.1f}" '
                        f'class="nbadge" fill="{kind["accent"]}">{esc(n["_badge"]).upper()}</text>')
        boxes.append((x, y, NODE_W, h, f'node {n["id"]}'))

    lane = 0
    pending: list[tuple] = []
    for e in edges:
        a, b = by_id[e["from"]], by_id[e["to"]]
        ek = EDGE_KINDS.get(e.get("kind") or "forward", EDGE_KINDS["forward"])
        dash = f' stroke-dasharray="{ek["dash"]}"' if ek["dash"] else ""
        style = f'class="edge" stroke="{ek["accent"]}"{dash} marker-end="url(#a-{slug(ek["accent"])})"'
        if e in back:
            lane += 1
            ly = max_col_h + lane * GUTTER_LANE - 10
            x1, y1 = a["_x"] + NODE_W / 2, a["_y"] + a["_h"]
            x2, y2 = b["_x"] + NODE_W / 2, b["_y"] + b["_h"]
            d = (f'M {x1:.1f} {y1:.1f} V {ly:.1f} H {x2:.1f} V {y2 + 6:.1f}')
            body.append(f'<path d="{d}" {style} fill="none"/>')
            if e.get("label"):
                pending.append(((x1 + x2) / 2, ly, e["label"], "h"))
        elif a["_col"] == b["_col"]:
            if a is b:                                    # self-loop: a tab on the right
                x, y1 = a["_x"] + NODE_W, a["_y"] + a["_h"] * 0.3
                y2 = a["_y"] + a["_h"] * 0.7
                d = f'M {x:.1f} {y1:.1f} H {x + 22:.1f} V {y2:.1f} H {x + 6:.1f}'
                lx, ly = x + 60, (y1 + y2) / 2
            else:                                          # straight down the column
                x1, y1 = a["_x"] + NODE_W / 2, a["_y"] + a["_h"]
                x2, y2 = b["_x"] + NODE_W / 2, b["_y"]
                if y2 < y1:                                # target sits above: hug the side
                    x = a["_x"] + NODE_W + 16
                    y1, y2 = a["_y"] + a["_h"] / 2, b["_y"] + b["_h"] / 2
                    d = (f'M {a["_x"] + NODE_W:.1f} {y1:.1f} H {x:.1f} V {y2:.1f} '
                         f'H {b["_x"] + NODE_W + 6:.1f}')
                    lx, ly = x + 46, (y1 + y2) / 2
                else:
                    d = f'M {x1:.1f} {y1:.1f} V {y2 - 6:.1f}'
                    lx, ly = x1 + 8 + text_w(e.get("label") or "", LABEL_SIZE) / 2, (y1 + y2) / 2
            body.append(f'<path d="{d}" {style} fill="none"/>')
            if e.get("label"):
                pending.append((lx, ly, e["label"], "v"))
        else:
            x1, y1 = a["_x"] + NODE_W, a["_y"] + a["_h"] / 2
            x2, y2 = b["_x"], b["_y"] + b["_h"] / 2
            xm = x1 + (x2 - x1) / 2
            d = (f'M {x1:.1f} {y1:.1f} H {xm:.1f} V {y2:.1f} H {x2 - 6:.1f}'
                 if abs(y1 - y2) > 2 else f'M {x1:.1f} {y1:.1f} H {x2 - 6:.1f}')
            body.append(f'<path d="{d}" {style} fill="none"/>')
            if e.get("label"):
                pending.append((xm, min(y1, y2) - 12 if abs(y1 - y2) > 2 else y1 - 12,
                                e["label"], "v"))

    body.append(place_labels(pending, boxes))
    return "".join(body), width, height, problems, boxes


# ---------------------------------------------------------------------------
# Archetype: stack (layers, trust zones, environments)
# ---------------------------------------------------------------------------

def layout_stack(spec: dict) -> tuple[str, float, float, list[dict], list[tuple]]:
    groups = spec.get("groups") or []
    problems: list[dict] = []
    if not groups:
        die("a stack diagram needs 'groups'")

    per_row = max(len(g.get("items") or []) for g in groups)
    per_row = max(1, min(per_row, 4))
    inner_w = NODE_W - 2 * NODE_PAD_X
    width = PAD * 2 + per_row * NODE_W + (per_row - 1) * 24 + 2 * 18
    body: list[str] = []
    boxes: list[tuple] = []
    y = PAD

    for g in groups:
        items = g.get("items") or []
        rows = math.ceil(len(items) / per_row) or 1
        cells = []
        for it in items:
            title = wrap(it.get("label") or "", TITLE_SIZE, inner_w)
            note = wrap(it.get("note") or "", NOTE_SIZE, inner_w)
            h = NODE_PAD_Y * 2 + len(title) * TITLE_SIZE * LINE_H
            if note:
                h += 4 + len(note) * NOTE_SIZE * LINE_H
            if it.get("evidence"):
                h += LABEL_SIZE + 4
            cells.append((it, title, note, max(56, h)))
        row_h = [max([c[3] for c in cells[r * per_row:(r + 1) * per_row]] or [56])
                 for r in range(rows)]
        ghead = 26
        gh = ghead + sum(row_h) + 20 * rows + 6
        dash = ' stroke-dasharray="7 5"' if g.get("boundary") else ""
        body.append(f'<rect x="{PAD:.1f}" y="{y:.1f}" width="{width - 2 * PAD:.1f}" '
                    f'height="{gh:.1f}" rx="14" class="group"{dash}/>')
        body.append(f'<text x="{PAD + 16:.1f}" y="{y + 19:.1f}" class="stage">'
                    f'{esc(g.get("label") or "").upper()}</text>')
        if g.get("note"):
            body.append(f'<text x="{width - PAD - 16:.1f}" y="{y + 19:.1f}" class="gnote" '
                        f'text-anchor="end">{esc(g["note"])}</text>')
        cy = y + ghead + 6
        for r in range(rows):
            row = cells[r * per_row:(r + 1) * per_row]
            for c, (it, title, note, h) in enumerate(row):
                x = PAD + 18 + c * (NODE_W + 24)
                kind = KINDS.get(it.get("kind") or "node", KINDS["node"])
                kdash = f' stroke-dasharray="{kind["dash"]}"' if kind["dash"] else ""
                body.append(f'<rect x="{x:.1f}" y="{cy:.1f}" width="{NODE_W}" '
                            f'height="{row_h[r]:.1f}" rx="12" class="node" '
                            f'stroke="{kind["accent"]}"{kdash}/>')
                body.append(f'<rect x="{x:.1f}" y="{cy:.1f}" width="5" '
                            f'height="{row_h[r]:.1f}" rx="2.5" fill="{kind["accent"]}"/>')
                ty = cy + NODE_PAD_Y + TITLE_SIZE * 0.85
                body.append(svg_text(x + NODE_PAD_X, ty, title, TITLE_SIZE, "ntitle"))
                ty += len(title) * TITLE_SIZE * LINE_H
                if note:
                    ty += 4
                    body.append(svg_text(x + NODE_PAD_X, ty, note, NOTE_SIZE, "nnote"))
                    ty += len(note) * NOTE_SIZE * LINE_H
                if it.get("evidence"):
                    body.append(f'<text x="{x + NODE_PAD_X:.1f}" y="{ty + LABEL_SIZE * 0.6:.1f}" '
                                f'class="nbadge" fill="{kind["accent"]}">'
                                f'{esc(it["evidence"]).upper()}</text>')
                boxes.append((x, cy, NODE_W, row_h[r], f'item {it.get("label")}'))
            cy += row_h[r] + 20
        y += gh + 22

    return "".join(body), width, y - 22 + PAD, problems, boxes


# ---------------------------------------------------------------------------
# Archetype: sequence
# ---------------------------------------------------------------------------

def layout_sequence(spec: dict) -> tuple[str, float, float, list[dict], list[tuple]]:
    actors = spec.get("actors") or []
    steps = spec.get("steps") or []
    problems: list[dict] = []
    if not actors:
        die("a sequence diagram needs 'actors'")
    ids = [a["id"] if isinstance(a, dict) else a for a in actors]
    lane_w = 236
    width = PAD * 2 + len(ids) * lane_w
    head_h = 62
    body: list[str] = []
    boxes: list[tuple] = []
    cx = {aid: PAD + i * lane_w + lane_w / 2 for i, aid in enumerate(ids)}

    y = PAD + head_h + 18
    drawn: list[str] = []
    for s in steps:
        frm, to = s.get("from"), s.get("to")
        if frm not in cx or (to is not None and to not in cx):
            problems.append({"severity": "fail",
                             "message": f"step '{s.get('label')}' names an unknown actor"})
            continue
        ek = EDGE_KINDS.get(s.get("kind") or "forward", EDGE_KINDS["forward"])
        dash = f' stroke-dasharray="{ek["dash"]}"' if ek["dash"] else ""
        lines = wrap(s.get("label") or "", LABEL_SIZE, lane_w * 1.3)
        # The label is written above its own arrow, so the block has to be
        # measured before anything is placed — otherwise a two-line message
        # draws straight through the arrow it belongs to.
        block_h = max(1, len(lines)) * LABEL_SIZE * LINE_H
        if to is None or to == frm:                       # a note / self-action
            x = cx[frm] + 16
            w = max(text_w(l, LABEL_SIZE) for l in lines) + 20
            h = block_h + 14
            body.append(f'<rect x="{x:.1f}" y="{y - 12:.1f}" width="{w:.1f}" height="{h:.1f}" '
                        f'rx="6" class="note"/>')
            body.append(svg_text(x + 10, y + 2, lines, LABEL_SIZE, "elabel"))
            boxes.append((x, y - 12, w, h, f'note {s.get("label")}'))
            arrow_y = y - 12 + h
        else:
            x1, x2 = cx[frm], cx[to]
            direction = 1 if x2 > x1 else -1
            arrow_y = y + block_h
            body.append(f'<path d="M {x1 + 6 * direction:.1f} {arrow_y:.1f} '
                        f'H {x2 - 8 * direction:.1f}" '
                        f'class="edge" stroke="{ek["accent"]}"{dash} fill="none" '
                        f'marker-end="url(#a-{slug(ek["accent"])})"/>')
            body.append(svg_text((x1 + x2) / 2, y, lines, LABEL_SIZE, "elabel", "middle"))
            tw = max(text_w(l, LABEL_SIZE) for l in lines) if lines else 0
            boxes.append(((x1 + x2) / 2 - tw / 2, y - LABEL_SIZE, tw, block_h + 4,
                          f'message {s.get("label")}'))
        if s.get("evidence"):
            body.append(f'<text x="{width - PAD:.1f}" y="{y:.1f}" class="nbadge" '
                        f'text-anchor="end">{esc(s["evidence"]).upper()}</text>')
        y = arrow_y + 34
        drawn.append(s.get("label") or "")

    height = y + 10
    for i, a in enumerate(actors):
        aid = ids[i]
        label = a.get("label") if isinstance(a, dict) else str(a)
        kind = KINDS.get((a.get("kind") if isinstance(a, dict) else None) or "node", KINDS["node"])
        x = PAD + i * lane_w + 14
        w = lane_w - 28
        lines = wrap(label, TITLE_SIZE, w - 24)
        body.insert(0, f'<line x1="{cx[aid]:.1f}" y1="{PAD + head_h:.1f}" x2="{cx[aid]:.1f}" '
                       f'y2="{height - 8:.1f}" class="lifeline"/>')
        body.insert(0, f'<rect x="{x:.1f}" y="{PAD:.1f}" width="{w:.1f}" '
                       f'height="{head_h - 8:.1f}" rx="12" class="node" stroke="{kind["accent"]}"/>')
        body.insert(1, svg_text(cx[aid], PAD + 24, lines, TITLE_SIZE, "ntitle", "middle"))
        boxes.append((x, PAD, w, head_h - 8, f'actor {label}'))

    return "".join(body), width, height, problems, boxes


# ---------------------------------------------------------------------------
# Self-inspection: the point of generating geometry is being able to check it
# ---------------------------------------------------------------------------

def inspect(boxes: list[tuple], width: float, height: float) -> list[dict]:
    found: list[dict] = []
    for i in range(len(boxes)):
        ax, ay, aw, ah, an = boxes[i]
        if ax < 0 or ay < 0 or ax + aw > width + 1 or ay + ah > height + 1:
            found.append({"severity": "fail",
                          "message": f"{an} is clipped by the canvas edge"})
        for j in range(i + 1, len(boxes)):
            bx, by, bw, bh, bn = boxes[j]
            ox = min(ax + aw, bx + bw) - max(ax, bx)
            oy = min(ay + ah, by + bh) - max(ay, by)
            if ox > 2 and oy > 2:
                found.append({"severity": "fail",
                              "message": f"{an} overlaps {bn} by {ox:.0f}×{oy:.0f}px"})
    return found


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

STYLE = """
.node{fill:var(--dg-card,#fff);stroke-width:1.6}
.group{fill:var(--dg-group,#f4f7fc);stroke:var(--dg-line,#c9d3e4);stroke-width:1.4}
.plate{fill:var(--dg-card,#fff);stroke:var(--dg-line,#d8deea);stroke-width:1}
.note{fill:var(--dg-note,#fff8e6);stroke:var(--dg-line,#d8deea);stroke-width:1.2}
.edge{stroke-width:1.9;stroke-linejoin:round;stroke-linecap:round}
.lifeline{stroke:var(--dg-line,#c9d3e4);stroke-width:1.2;stroke-dasharray:2 6}
.stagerule{stroke:var(--dg-line,#c9d3e4);stroke-width:2}
text{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;fill:var(--dg-ink,#172033)}
.ntitle{font-size:14px;font-weight:650}
.nnote{font-size:11.5px;fill:var(--dg-muted,#586278)}
.nbadge{font-size:10px;font-weight:700;letter-spacing:.08em}
.elabel{font-size:11px;fill:var(--dg-muted,#3d4c66)}
.stage{font-size:11px;font-weight:700;letter-spacing:.1em;fill:var(--dg-muted,#586278)}
.gnote{font-size:11px;fill:var(--dg-muted,#586278)}
"""

LAYOUTS = {"flow": layout_flow, "stack": layout_stack, "sequence": layout_sequence}


def markers() -> str:
    out = []
    for spec in EDGE_KINDS.values():
        c = spec["accent"]
        out.append(f'<marker id="a-{slug(c)}" viewBox="0 0 10 10" refX="9" refY="5" '
                   f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                   f'<path d="M 0 1 L 9 5 L 0 9 z" fill="{c}"/></marker>')
    return "<defs>" + "".join(out) + "</defs>"


def text_equivalent(spec: dict) -> str:
    """The table a screen-reader user, a printed page, or a diff actually gets."""
    t = spec.get("type")
    rows = []
    if t == "flow":
        rows.append("<tr><th scope=\"col\">From</th><th scope=\"col\">To</th>"
                    "<th scope=\"col\">Trigger</th><th scope=\"col\">Kind</th></tr>")
        for n in spec.get("nodes") or []:
            rows.append(f'<tr><td colspan="4"><strong>{esc(n.get("label") or n["id"])}</strong>'
                        f' — {esc(n.get("note") or "")} '
                        f'<em>{esc(n.get("evidence") or "")}</em></td></tr>')
        for e in spec.get("edges") or []:
            rows.append(f'<tr><td>{esc(e.get("from"))}</td><td>{esc(e.get("to"))}</td>'
                        f'<td>{esc(e.get("label") or "—")}</td>'
                        f'<td>{esc(e.get("kind") or "forward")}</td></tr>')
    elif t == "stack":
        rows.append('<tr><th scope="col">Group</th><th scope="col">Item</th>'
                    '<th scope="col">Detail</th><th scope="col">Evidence</th></tr>')
        for g in spec.get("groups") or []:
            for it in g.get("items") or []:
                rows.append(f'<tr><td>{esc(g.get("label"))}</td>'
                            f'<td>{esc(it.get("label"))}</td>'
                            f'<td>{esc(it.get("note") or "—")}</td>'
                            f'<td>{esc(it.get("evidence") or "—")}</td></tr>')
    else:
        rows.append('<tr><th scope="col">#</th><th scope="col">From</th><th scope="col">To</th>'
                    '<th scope="col">Message</th><th scope="col">Evidence</th></tr>')
        for i, s in enumerate(spec.get("steps") or [], 1):
            rows.append(f'<tr><td>{i}</td><td>{esc(s.get("from"))}</td>'
                        f'<td>{esc(s.get("to") or "(self)")}</td>'
                        f'<td>{esc(s.get("label"))}</td>'
                        f'<td>{esc(s.get("evidence") or "—")}</td></tr>')
    return "<table class=\"dg-equiv\">" + "".join(rows) + "</table>"


def render(spec: dict) -> tuple[str, list[dict]]:
    t = spec.get("type")
    if t not in LAYOUTS:
        die(f"unknown diagram type '{t}'. Use one of: {', '.join(LAYOUTS)}")
    body, width, height, problems, boxes = LAYOUTS[t](spec)
    if any(p["severity"] == "fail" for p in problems):
        return "", problems
    problems += inspect(boxes, width, height)

    did = slug(spec.get("id") or spec.get("title") or t)
    title = spec.get("title") or "Diagram"
    desc = spec.get("takeaway") or ""
    svg = (f'<svg viewBox="0 0 {width:.0f} {height:.0f}" width="100%" '
           f'style="max-width:{width:.0f}px" role="img" '
           f'aria-labelledby="{did}-t {did}-d" xmlns="http://www.w3.org/2000/svg">'
           f'<title id="{did}-t">{esc(title)}</title>'
           f'<desc id="{did}-d">{esc(desc)}</desc>'
           f'<style>{STYLE}</style>{markers()}{body}</svg>')
    return svg, problems


def figure(spec: dict, svg: str) -> str:
    ev = (spec.get("evidence") or "").lower()
    mark = EVIDENCE_MARK.get(ev, ev)
    meta = []
    if spec.get("scope"):
        meta.append(f'<span><strong>Scope:</strong> {esc(spec["scope"])}</span>')
    if mark:
        meta.append(f'<span class="ev ev-{esc(mark)}">{esc(mark)}</span>')
    if spec.get("sources"):
        srcs = ", ".join(f"<code>{esc(s)}</code>" for s in spec["sources"])
        meta.append(f'<span><strong>From:</strong> {srcs}</span>')
    return (f'<figure class="dg" id="fig-{slug(spec.get("id") or spec.get("title") or "d")}">\n'
            f'{svg}\n'
            f'<figcaption>\n'
            f'  <strong>{esc(spec.get("title") or "Diagram")}.</strong> '
            f'{esc(spec.get("takeaway") or "")}\n'
            f'  <span class="dg-meta">{" ".join(meta)}</span>\n'
            f'  <details><summary>Text equivalent</summary>\n{text_equivalent(spec)}\n</details>\n'
            f'</figcaption>\n</figure>')


SCHEMA = """Diagram spec (JSON). Only `type` and the archetype's own content are required.

Shared optional keys, all of which end up in the caption a reader relies on:
  id, title, takeaway, scope, evidence (declared|observed|inferred|unknown|conflicting),
  sources: ["src/graph.py:41", ...]

flow      — stages (columns), nodes, edges
  {"type":"flow","title":"Run path","takeaway":"Validation can send a draft back twice.",
   "scope":"src/graph.py @ 9f2c1a","evidence":"declared",
   "stages":[{"id":"in","label":"Intake"},{"id":"gen","label":"Generate"},{"id":"out","label":"Emit"}],
   "nodes":[{"id":"load","label":"load_brief","stage":"in","kind":"node","entry":true,
             "note":"validates against brief.schema.json","evidence":"declared"},
            {"id":"draft","label":"draft_lesson","stage":"gen","note":"claude-sonnet-5 · 3 retries"},
            {"id":"check","label":"validate","stage":"gen","kind":"gate"},
            {"id":"done","label":"emit_bundle","stage":"out","kind":"terminal"}],
   "edges":[{"from":"load","to":"draft"},
            {"from":"draft","to":"check","label":"draft ready"},
            {"from":"check","to":"done","label":"valid","kind":"branch"},
            {"from":"check","to":"draft","label":"invalid · max 2","kind":"repair"}]}

  node kinds: node · gate · terminal · external · store · human
  edge kinds: forward · branch · repair · failure · data
  A repair/back edge is routed through a gutter beneath the flow, one lane each,
  because a loop drawn across the forward path is the single most common way
  these diagrams become unreadable.

stack     — groups (layers, trust zones, environments) holding items
  {"type":"stack","title":"Deployment topology",
   "groups":[{"label":"Operator laptop","boundary":true,"note":"trust boundary",
              "items":[{"label":"CLI","note":"python -m factory","evidence":"declared"}]},
             {"label":"External","items":[{"label":"Anthropic API","kind":"external"}]}]}

sequence  — actors (lifelines) and ordered steps; omit `to` for a note/self-action
  {"type":"sequence","title":"Recovery after a failed run",
   "actors":[{"id":"op","label":"On-call operator","kind":"human"},
             {"id":"cli","label":"factory CLI"},{"id":"db","label":"Postgres checkpointer","kind":"store"}],
   "steps":[{"from":"op","to":"cli","label":"factory resume --run 41","evidence":"declared"},
            {"from":"cli","to":"db","label":"load checkpoint","kind":"data"},
            {"from":"cli","label":"replays from last committed node"},
            {"from":"cli","to":"op","label":"exit 1 if checkpoint is stale","kind":"failure"}]}
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?", help="path to the diagram spec JSON, or - for stdin")
    ap.add_argument("--out", help="write here instead of stdout")
    ap.add_argument("--svg-only", action="store_true",
                    help="emit bare SVG (for a standalone .svg asset) rather than a <figure>")
    ap.add_argument("--print-schema", action="store_true")
    args = ap.parse_args()

    if args.print_schema:
        print(SCHEMA)
        return 0
    if not args.spec:
        die("give a spec file, or --print-schema to see the format")

    raw = sys.stdin.read() if args.spec == "-" else open(args.spec, encoding="utf-8").read()
    try:
        spec = json.loads(raw)
    except json.JSONDecodeError as exc:
        die(f"spec is not valid JSON: {exc}")

    svg, problems = render(spec)
    fails = [p for p in problems if p["severity"] == "fail"]
    for p in problems:
        print(f"[{p['severity'].upper():4}] {p['message']}", file=sys.stderr)
    if fails:
        print("\nDiagram not emitted. Fix the spec — shortening labels, splitting a "
              "crowded stage into two, or removing an edge the evidence does not "
              "support — and render again.", file=sys.stderr)
        return 1

    out = svg if args.svg_only else figure(spec, svg)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(out + "\n")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(out)
    if not problems:
        print("self-inspection: no clipping, no overlap, no orphan nodes", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
