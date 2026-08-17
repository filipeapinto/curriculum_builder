"""Studio backend — the default. Lays the graph out itself and writes SVG.

Why this exists at all is recorded in references/design-decisions.md, but the
short version is the back-edges. Seven of this graph's twenty-three edges run
backwards, up to nine ranks upstream. Both general layout engines were rendered
against the real manifest first: Graphviz `dot` and D2/dagre both route those
seven wherever the spline solver finds room, which is straight across the
forward spine. A reader then cannot tell the flow from the recovery, and the
recovery is what they came to read.

So the routing is not left to a solver here. It is a decision:

* The forward spine is a single top-to-bottom column, because the forward graph
  is a chain — fifteen ranks, and only one rank is wider than one node.
* Every repair edge is routed orthogonally through a reserved gutter to the left
  of the spine, one lane per edge, lanes ordered by span so the long routes sit
  outermost and the arcs nest rather than tangle.
* Where a horizontal run must cross another lane's vertical run, it hops it —
  the small break in the line that circuit diagrams use — so a crossing reads as
  a crossing instead of as a junction.
* Nothing but a repair edge is ever crimson. That is what makes the recovery
  structure findable in one glance without reading a label.
"""

from __future__ import annotations

from collections import defaultdict
from html import escape

import palette as P
from manifest_model import Graph, Node, gist

# --- geometry -----------------------------------------------------------------
MARGIN = 34
HEADER_H = 78
CARD_W = 262
CARD_H = 82
CARD_GAP_X = 26
RANK_PITCH = 116
RAIL_W = 46
RAIL_GAP = 12
LANE_W = 33
GUTTER_PAD = 26
SPINE_PAD = 34
PANEL_W = 352
PANEL_GAP = 34
CORNER = 9

FONT = "'Helvetica Neue', Helvetica, Arial, sans-serif"
FONT_MONO = "'SF Mono', Menlo, Consolas, monospace"

# Rough advance widths as a fraction of font size. Used only to wrap and to
# size pills; inspect_layout.py measures the truth from the rendered SVG.
ADV = 0.523
ADV_BOLD = 0.560


def _tw(text: str, size: float, bold: bool = False) -> float:
    return len(text) * size * (ADV_BOLD if bold else ADV)


def _wrap(text: str, size: float, width: float, max_lines: int = 2) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if _tw(trial, size) > width and cur:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
        else:
            cur = trial
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and words:
        joined = " ".join(lines)
        if len(joined) < len(text):
            last = lines[-1]
            while lines and _tw(last + "…", size) > width and " " in last:
                last = last.rsplit(" ", 1)[0]
            lines[-1] = last + "…"
    return lines


def _esc(t: str) -> str:
    # quote=False on purpose: an apostrophe is legal inside SVG text content,
    # and escaping it to `&#x27;` makes every downstream width measurement
    # count six characters where the reader sees one.
    return escape(t, quote=False).replace('"', "&quot;")


# --- layout -------------------------------------------------------------------
def _ranks(g: Graph) -> dict[str, int]:
    """Longest path over forward edges. Repair edges are excluded on purpose:
    a back-edge that participates in ranking pulls its target downstream and
    destroys the very ordering the reader is trying to follow."""
    indeg = defaultdict(int)
    out = defaultdict(list)
    for e in g.forward:
        out[e.src].append(e.dst)
        indeg[e.dst] += 1
    order, queue = [], [n.id for n in g.nodes if indeg[n.id] == 0]
    seen = set(queue)
    while queue:
        v = queue.pop(0)
        order.append(v)
        for w in out[v]:
            indeg[w] -= 1
            if indeg[w] == 0 and w not in seen:
                seen.add(w)
                queue.append(w)
    if len(order) != len(g.nodes):
        raise ValueError("the forward edge set (non-repair edges) contains a cycle; "
                         "studio layout needs an acyclic spine")
    rank = {n.id: 0 for n in g.nodes}
    for v in order:
        for w in out[v]:
            rank[w] = max(rank[w], rank[v] + 1)
    return rank


def _lanes(g: Graph, rank: dict[str, int]) -> list[tuple]:
    """One gutter lane per repair edge, widest span outermost.

    Nesting the spans is what keeps the arcs from tangling: a route that covers
    another route's whole interval is drawn around the outside of it, the way a
    subway map stacks parallel lines, so the picture has seven readable arcs
    instead of seven overlapping ones."""
    items = []
    for e in g.repairs:
        rs, rd = rank[e.src], rank[e.dst]
        items.append((abs(rs - rd), e, rs, rd))
    items.sort(key=lambda t: (-t[0], t[2]))
    return [(e, rs, rd, i) for i, (_, e, rs, rd) in enumerate(items)]


# --- drawing primitives -------------------------------------------------------
def _card_svg(n: Node, x: float, y: float, detail: str) -> list[str]:
    spec = P.KIND.get(n.kind, P.KIND["agent"])
    accent = spec["accent"]
    out = [
        f'<g class="card">',
        f'<rect x="{x:.1f}" y="{y+2:.1f}" width="{CARD_W}" height="{CARD_H}" rx="{CARD_W*0+10}" '
        f'fill="#0F172A" opacity="0.055"/>',
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{CARD_W}" height="{CARD_H}" rx="10" '
        f'fill="{P.PAPER}" stroke="{P.HAIRLINE}" stroke-width="1"/>',
        # kind stripe, clipped to the rounded top by a rect + a cover
        f'<path d="M{x:.1f},{y+10:.1f} a10,10 0 0 1 10,-10 h{CARD_W-20} '
        f'a10,10 0 0 1 10,10 v-4 a6,6 0 0 0 -6,-6 h{-(CARD_W-12)} '
        f'a6,6 0 0 0 -6,6 z" fill="{accent}"/>',
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{CARD_W}" height="5" rx="2.5" fill="{accent}"/>',
    ]
    if n.is_entry or n.is_terminal:
        out.append(
            f'<rect x="{x-2.5:.1f}" y="{y-2.5:.1f}" width="{CARD_W+5}" height="{CARD_H+5}" '
            f'rx="12" fill="none" stroke="{accent}" stroke-width="1.6" opacity="0.55"/>'
        )
    tag = f"{n.stage} · {spec['label']}"
    if n.is_entry:
        tag += " · ENTRY"
    if n.is_terminal:
        tag += " · TERMINAL"
    tx = x + 14
    out.append(
        f'<text x="{tx:.1f}" y="{y+21:.1f}" font-family="{FONT}" font-size="7.6" '
        f'font-weight="700" letter-spacing="0.9" fill="{accent}">{_esc(tag)}</text>'
    )
    out.append(
        f'<text x="{tx:.1f}" y="{y+38:.1f}" font-family="{FONT}" font-size="13.5" '
        f'font-weight="600" fill="{P.INK}">{_esc(n.display)}</text>'
    )
    if detail in ("standard", "full"):
        for i, line in enumerate(_wrap(" ".join(n.purpose.split()), 8.4, CARD_W - 28, 2)):
            out.append(
                f'<text x="{tx:.1f}" y="{y+52+i*11:.1f}" font-family="{FONT}" '
                f'font-size="8.4" fill="{P.INK_SOFT}">{_esc(line)}</text>'
            )
    chip = n.budget_chip
    out.append(
        f'<text x="{tx:.1f}" y="{y+CARD_H-9:.1f}" font-family="{FONT_MONO}" '
        f'font-size="7.6" fill="{P.INK_FAINT}">{_esc(chip)}</text>'
    )
    if detail == "full":
        io = f"{n.reads} in / {n.writes} out"
        out.append(
            f'<text x="{x+CARD_W-14:.1f}" y="{y+CARD_H-9:.1f}" text-anchor="end" '
            f'font-family="{FONT_MONO}" font-size="7.6" fill="{P.INK_FAINT}">'
            f'{_esc(io)}</text>'
        )
    if n.repair_route:
        lim = n.repair_route.get("recurrence_limit")
        c = P.EDGE["repair"]["color"]
        label = f"↩ ×{lim}"
        w = _tw(label, 7.8, True) + 12
        out.append(
            f'<rect x="{x+CARD_W-w-10:.1f}" y="{y+13:.1f}" width="{w:.1f}" height="13" '
            f'rx="6.5" fill="{P.KIND["repair"]["tint"]}"/>'
        )
        out.append(
            f'<text x="{x+CARD_W-10-w/2:.1f}" y="{y+22.5:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="7.8" font-weight="700" fill="{c}">'
            f'{_esc(label)}</text>'
        )
    out.append("</g>")
    return out


def _pill(x: float, y: float, text: str, color: str, tint: str,
          size: float = 8.0, anchor: str = "middle") -> list[str]:
    w = _tw(text, size, True) + 14
    if anchor == "middle":
        rx = x - w / 2
    elif anchor == "end":
        rx = x - w
    else:
        rx = x
    return [
        f'<rect x="{rx:.1f}" y="{y-8:.1f}" width="{w:.1f}" height="15" rx="7.5" '
        f'fill="{tint}" stroke="{color}" stroke-width="0.7" stroke-opacity="0.35"/>',
        f'<text x="{rx+w/2:.1f}" y="{y+2.6:.1f}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="{size}" font-weight="600" fill="{color}">'
        f'{_esc(text)}</text>',
    ]


def _hop_path(x0: float, y0: float, x1: float, y1: float, crossings: list[float],
              horizontal: bool) -> str:
    """A straight run that lifts over the vertical lanes it crosses."""
    d = [f"M{x0:.1f},{y0:.1f}"]
    if horizontal:
        step = 1 if x1 > x0 else -1
        for cx in sorted(crossings, reverse=step < 0):
            if min(x0, x1) + 3 < cx < max(x0, x1) - 3:
                d.append(f"L{cx - 4.5*step:.1f},{y0:.1f}")
                d.append(f"A4.5,4.5 0 0 {1 if step > 0 else 0} "
                         f"{cx + 4.5*step:.1f},{y0:.1f}")
        d.append(f"L{x1:.1f},{y1:.1f}")
    else:
        d.append(f"L{x1:.1f},{y1:.1f}")
    return " ".join(d)


# --- the page -----------------------------------------------------------------
def emit(g: Graph, detail: str = "standard", title: str = "", subtitle: str = "") -> str:
    rank = _ranks(g)
    lanes = _lanes(g, rank)
    n_lanes = max(1, len(lanes))

    by_rank: dict[int, list[Node]] = defaultdict(list)
    for n in g.nodes:
        by_rank[rank[n.id]].append(n)
    manifest_order = {n.id: i for i, n in enumerate(g.nodes)}
    for r in by_rank:
        by_rank[r].sort(key=lambda n: manifest_order[n.id])
    max_rank = max(by_rank)
    widest = max(len(v) for v in by_rank.values())

    spine_w = widest * CARD_W + (widest - 1) * CARD_GAP_X
    gutter_w = n_lanes * LANE_W + GUTTER_PAD
    x_rail = MARGIN
    x_gutter = x_rail + RAIL_W + RAIL_GAP
    x_spine = x_gutter + gutter_w + SPINE_PAD
    x_panel = x_spine + spine_w + PANEL_GAP
    W = x_panel + PANEL_W + MARGIN
    y0 = MARGIN + HEADER_H
    H = y0 + (max_rank + 1) * RANK_PITCH - (RANK_PITCH - CARD_H) + MARGIN

    # The sidebar is fixed-content and the spine is not. On a short graph the
    # spine is the shorter of the two, so the page has to grow to the sidebar
    # or the three cards overlap each other.
    _, _key_h, _ = _panel_key(g, x_panel, 0.0)
    _, _chk_h, _ = _panel_checks(g, x_panel, 0.0)
    _, _ref_h, _ = _panel_reference(g, x_panel, 0.0)
    SIDEBAR_MIN_GAP = 26.0
    needed = _key_h + _chk_h + _ref_h + 2 * SIDEBAR_MIN_GAP
    H = max(H, (y0 - 10) + needed + MARGIN)

    # node boxes
    pos: dict[str, tuple[float, float]] = {}
    for r, nodes in by_rank.items():
        row_w = len(nodes) * CARD_W + (len(nodes) - 1) * CARD_GAP_X
        sx = x_spine + (spine_w - row_w) / 2
        for i, n in enumerate(nodes):
            pos[n.id] = (sx + i * (CARD_W + CARD_GAP_X), y0 + r * RANK_PITCH)

    s: list[str] = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" '
      f'viewBox="0 0 {W:.0f} {H:.0f}" font-family="{FONT}">')
    a(f'<rect width="{W:.0f}" height="{H:.0f}" fill="{P.GROUND}"/>')
    a('<defs>')
    for name, color in (("seq", P.EDGE["sequential"]["color"]),
                        ("cond", P.EDGE["conditional"]["color"]),
                        ("par", P.EDGE["parallel"]["color"]),
                        ("rep", P.EDGE["repair"]["color"])):
        a(f'<marker id="ah-{name}" viewBox="0 0 10 10" refX="8.5" refY="5" '
          f'markerWidth="5.2" markerHeight="5.2" orient="auto-start-reverse">'
          f'<path d="M0,1.2 L9.4,5 L0,8.8 z" fill="{color}"/></marker>')
    a('</defs>')

    # --- header
    a(f'<text x="{MARGIN}" y="{MARGIN+26:.0f}" font-size="23" font-weight="700" '
      f'fill="{P.INK}" letter-spacing="-0.3">{_esc(title)}</text>')
    if subtitle:
        a(f'<text x="{MARGIN}" y="{MARGIN+46:.0f}" font-size="10.5" '
          f'fill="{P.INK_SOFT}">{_esc(subtitle)}</text>')
    a(f'<rect x="{MARGIN}" y="{MARGIN+56:.0f}" width="{W-2*MARGIN:.0f}" height="1" '
      f'fill="{P.HAIRLINE}"/>')

    # --- stage rail
    s += _stage_rail(g, rank, pos, x_rail)

    # --- forward edges, drawn under the cards
    fan_srcs = {e.src for e in g.forward if e.type == "parallel"}
    for e in g.forward:
        s += _forward_edge(g, e, pos, x_spine, spine_w)
    # One pill per fan-out, not one per branch: the parallelism is a single
    # fact about the source node, and two pills side by side read as two
    # different claims.
    for src in sorted(fan_srcs):
        sx, sy = pos[src]
        s += _pill(sx + CARD_W / 2, sy + CARD_H + 17, "runs in parallel",
                   P.EDGE["parallel"]["color"], P.PAPER, 8.0)

    # --- repair gutter
    s += _repair_gutter(g, lanes, rank, pos, x_gutter, n_lanes)

    # --- cards
    for n in g.nodes:
        x, y = pos[n.id]
        s += _card_svg(n, x, y, detail)

    # --- right sidebar, as two cards rather than one. A single card sized to
    # its content leaves a third of the column empty under it, which reads as a
    # mistake. Anchoring the reading key to the top and the reference tables to
    # the bottom makes the same content hold the whole column on purpose.
    top = y0 - 10
    bottom = H - MARGIN
    key_body, _, _ = _panel_key(g, x_panel, top)
    ref_body, _, _ = _panel_reference(g, x_panel, bottom - _ref_h)
    mid = max(top + _key_h + SIDEBAR_MIN_GAP,
              (top + _key_h + (bottom - _ref_h) - _chk_h) / 2)
    chk_body, _, _ = _panel_checks(g, x_panel, mid)
    s += key_body + chk_body + ref_body

    a("</svg>")
    return "\n".join(s)


def _stage_rail(g: Graph, rank, pos, x_rail) -> list[str]:
    """Contiguous runs of one stage, as tinted bands.

    `stage` is not drawn as a box around the nodes because S4 is not convex in
    this graph — `s4-artifact-manifest` sits below all of S5. A band per
    contiguous run shows that honestly: S4 simply appears twice, which is a fact
    about the pipeline worth seeing, not a rendering defect to hide."""
    out = []
    runs = []
    ordered = sorted(g.nodes, key=lambda n: (rank[n.id], n.id))
    cur_stage, start = None, None
    for n in ordered:
        if n.stage != cur_stage:
            if cur_stage is not None:
                runs.append((cur_stage, start, prev))
            cur_stage, start = n.stage, n
        prev = n
    if cur_stage is not None:
        runs.append((cur_stage, start, prev))

    for i, (st, first, last) in enumerate(runs):
        y_top = pos[first.id][1] - 8
        y_bot = pos[last.id][1] + CARD_H + 8
        band_h = y_bot - y_top
        tint = P.STAGE_TINTS[i % len(P.STAGE_TINTS)]
        out.append(
            f'<rect x="{x_rail:.1f}" y="{y_top:.1f}" width="{RAIL_W}" '
            f'height="{band_h:.1f}" rx="8" fill="{tint}" '
            f'stroke="{P.HAIRLINE}" stroke-width="1"/>'
        )
        cy = (y_top + y_bot) / 2
        cx = x_rail + RAIL_W / 2
        caption = P.STAGE_TITLES.get(st, "").upper()
        # A rail caption that does not fit its band is worse than no caption:
        # it runs into the neighbouring band and both become unreadable.
        code_w = _tw(st, 9.5, True) + 4
        full = f"{st}   {caption}"
        if _tw(full, 9, True) + 18 <= band_h:
            label = (f'{_esc(st)}   <tspan font-weight="400" font-size="8.2" '
                     f'fill="{P.INK_FAINT}">{_esc(caption)}</tspan>')
        elif code_w + 8 <= band_h:
            label = _esc(st)
        else:
            label = ""
        if label:
            out.append(
                f'<text transform="translate({cx:.1f},{cy:.1f}) rotate(-90)" '
                f'text-anchor="middle" font-size="9.5" font-weight="700" '
                f'letter-spacing="1.3" fill="{P.INK_SOFT}">{label}</text>'
            )
    return out


def _forward_edge(g: Graph, e, pos, x_spine, spine_w) -> list[str]:
    spec = P.EDGE[e.type]
    x1, y1 = pos[e.src]
    x2, y2 = pos[e.dst]
    sx, sy = x1 + CARD_W / 2, y1 + CARD_H
    tx, ty = x2 + CARD_W / 2, y2 - 5
    dash = f' stroke-dasharray="{spec["dash"]}"' if spec["dash"] else ""
    marker = {"sequential": "seq", "conditional": "cond", "parallel": "par"}[e.type]
    if abs(sx - tx) < 0.5:
        d = f"M{sx:.1f},{sy:.1f} L{tx:.1f},{ty:.1f}"
    else:
        m = (sy + ty) / 2
        d = (f"M{sx:.1f},{sy:.1f} C{sx:.1f},{m:.1f} {tx:.1f},{m:.1f} "
             f"{tx:.1f},{ty:.1f}")
    out = [f'<path d="{d}" fill="none" stroke="{spec["color"]}" '
           f'stroke-width="{spec["width"]}"{dash} marker-end="url(#ah-{marker})"/>']
    label = _cond_gist(e.condition) if e.type == "conditional" else ""
    if label:
        mx = (sx + tx) / 2
        my = (sy + ty) / 2
        anchor_x = max(mx, x_spine + spine_w / 2) + 14
        out += _pill(anchor_x, my, label, spec["color"],
                     "#FFFFFF", 8.0, anchor="start")
    return out


def _repair_gutter(g: Graph, lanes, rank, pos, x_gutter, n_lanes) -> list[str]:
    out = []
    color = P.EDGE["repair"]["color"]
    lane_x = {}
    for e, rs, rd, i in lanes:
        # i == 0 is the widest span, and it goes furthest from the spine, so the
        # arcs nest. The reverse — short arcs outermost — forces every long
        # route to cross every short one on the way out.
        lane_x[(e.src, e.dst)] = x_gutter + i * LANE_W + LANE_W / 2

    # Two repair routes can land on the same node (s2-evidence-extract and
    # s4-compose each receive two). Entering at the same height would draw them
    # as one line, so each endpoint gets its own slot on the card's left face.
    slots: dict[str, list[str]] = defaultdict(list)
    for e, _rs, _rd, _i in lanes:
        slots[e.dst].append(f"in:{e.src}")
        slots[e.src].append(f"out:{e.dst}")

    def y_at(node_id: str, key: str) -> float:
        keys = slots[node_id]
        k = keys.index(key)
        n = len(keys)
        lo, hi = 0.30, 0.74
        frac = lo if n == 1 else lo + (hi - lo) * k / (n - 1)
        return pos[node_id][1] + CARD_H * (frac if n > 1 else 0.55)

    all_x = sorted(lane_x.values())
    for e, rs, rd, i in lanes:
        sx0, sy0 = pos[e.src]
        tx0, ty0 = pos[e.dst]
        x = lane_x[(e.src, e.dst)]
        y_out = y_at(e.src, f"out:{e.dst}")
        y_in = y_at(e.dst, f"in:{e.src}")
        crossings = [c for c in all_x if c != x]
        # leave the source card on its left face, run left to the lane
        d1 = _hop_path(sx0 - 2, y_out, x + CORNER, y_out, crossings, True)
        # turn up the lane
        d2 = (f"M{x+CORNER:.1f},{y_out:.1f} A{CORNER},{CORNER} 0 0 0 "
              f"{x:.1f},{y_out-CORNER:.1f} L{x:.1f},{y_in+CORNER:.1f} "
              f"A{CORNER},{CORNER} 0 0 0 {x+CORNER:.1f},{y_in:.1f}")
        d3 = _hop_path(x + CORNER, y_in, tx0 - 7, y_in, crossings, True)
        for d in (d1, d2, d3):
            out.append(
                f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.7" '
                f'stroke-dasharray="6 3.5" stroke-linecap="round"/>'
            )
        out.append(
            f'<path d="M{tx0-7:.1f},{y_in:.1f} L{tx0-1:.1f},{y_in:.1f}" '
            f'stroke="{color}" stroke-width="1.7" marker-end="url(#ah-rep)"/>'
        )
        out.append(
            f'<circle cx="{sx0-2:.1f}" cy="{y_out:.1f}" r="2.6" fill="{color}"/>'
        )
        src, dst = g.by_id(e.src), g.by_id(e.dst)
        lim = (src.repair_route or {}).get("recurrence_limit", "")
        # Class alone is ambiguous — two routes here are both `evidence`. The
        # destination stage is what tells them apart at a glance.
        label = f'{src.defect_ownership or "repair"} → {dst.stage} ×{lim}'
        ly = (y_out + y_in) / 2
        out += _pill(x, ly, label, color, P.KIND["repair"]["tint"], 7.8)
    return out


class _Card:
    """A sidebar card that measures itself, so the caller can anchor it to the
    top or the bottom of the column without a second layout pass by hand."""

    PAD = 20

    def __init__(self, x: float, y: float, title: str = ""):
        self.x, self.y, self.w = x, y, PANEL_W
        self.out: list[str] = ["__BG__"]
        self.cy = y + self.PAD + 6
        if title:
            self.out.append(
                f'<text x="{x+self.PAD:.1f}" y="{self.cy:.1f}" font-size="13" '
                f'font-weight="700" fill="{P.INK}">{_esc(title)}</text>'
            )
            self.cy += 4

    def section(self, label: str, gap: float = 22.0):
        self.cy += gap
        self.out.append(
            f'<text x="{self.x+self.PAD:.1f}" y="{self.cy:.1f}" font-size="8" '
            f'font-weight="700" letter-spacing="1.5" fill="{P.INK_FAINT}">'
            f'{_esc(label)}</text>'
        )
        self.cy += 6
        self.out.append(
            f'<rect x="{self.x+self.PAD:.1f}" y="{self.cy:.1f}" '
            f'width="{self.w-2*self.PAD:.1f}" height="1" fill="{P.HAIRLINE}"/>'
        )
        self.cy += 14

    def text(self, s: str, size: float = 8.6, fill: str | None = None,
             dx: float = 0.0, advance: float = 0.0, anchor: str = "start",
             weight: int = 400):
        ax = self.x + self.PAD + dx
        if anchor == "end":
            ax = self.x + self.w - self.PAD - dx
        self.out.append(
            f'<text x="{ax:.1f}" y="{self.cy:.1f}" font-size="{size}" '
            f'text-anchor="{anchor}" font-weight="{weight}" '
            f'fill="{fill or P.INK_SOFT}">{_esc(s)}</text>'
        )
        self.cy += advance

    def raw(self, frag: str, advance: float = 0.0):
        self.out.append(frag)
        self.cy += advance

    def paragraph(self, s: str, size: float = 8.4, lines: int = 10):
        for line in _wrap(s, size, self.w - 2 * self.PAD, lines):
            self.text(line, size, P.INK_SOFT, advance=size * 1.35)

    def close(self) -> tuple[list[str], float]:
        h = self.cy - self.y + self.PAD
        self.out[self.out.index("__BG__")] = (
            f'<rect x="{self.x:.1f}" y="{self.y:.1f}" width="{self.w:.1f}" '
            f'height="{h:.1f}" rx="12" fill="{P.PAPER}" stroke="{P.HAIRLINE}" '
            f'stroke-width="1"/>'
        )
        return self.out, h


def _panel_key(g: Graph, x: float, y: float) -> tuple[list[str], float, int]:
    """Top card: how to decode the picture, and the seven repair routes."""
    c = _Card(x, y, "How to read this")

    c.section("NODE KIND — THE STRIPE ON EACH CARD")
    for kind, gloss in (("agent", "runs a prompt this family authored"),
                        ("tool", "deterministic script, no prompt"),
                        ("gate", "deterministic pass / fail")):
        spec = P.KIND[kind]
        c.raw(f'<rect x="{x+c.PAD:.1f}" y="{c.cy-8:.1f}" width="22" height="9" '
              f'rx="2" fill="{spec["accent"]}"/>')
        c.raw(f'<text x="{x+c.PAD+30:.1f}" y="{c.cy:.1f}" font-size="9" '
              f'fill="{P.INK}"><tspan font-weight="600">{kind}</tspan>'
              f'<tspan fill="{P.INK_SOFT}"> — {_esc(gloss)}</tspan></text>', 16)

    c.section("EDGE TYPE")
    for et in ("sequential", "conditional", "parallel", "repair"):
        spec = P.EDGE[et]
        dash = f' stroke-dasharray="{spec["dash"]}"' if spec["dash"] else ""
        c.raw(f'<path d="M{x+c.PAD:.1f},{c.cy-3:.1f} L{x+c.PAD+22:.1f},'
              f'{c.cy-3:.1f}" stroke="{spec["color"]}" '
              f'stroke-width="{spec["width"]}"{dash}/>')
        c.raw(f'<text x="{x+c.PAD+30:.1f}" y="{c.cy:.1f}" font-size="9" '
              f'fill="{P.INK_SOFT}">{_esc(spec["label"])}</text>', 16)

    n = len(g.repairs)
    c.section(f"THE {_spell(n).upper()} REPAIR ROUTE" + ("S" if n != 1 else ""))
    c.paragraph("One crimson lane in the gutter per route, outermost lane = "
                "longest reach. Read a lane as: this failure sends the run back "
                "there, at most this many times, then the terminal escape takes "
                "over.", 8.4)
    c.cy += 6
    cols = (0.0, 118.0, 232.0)
    c.raw(f'<text x="{x+c.PAD:.1f}" y="{c.cy:.1f}" font-size="7.4" '
          f'font-weight="700" letter-spacing="0.7" fill="{P.INK_FAINT}">FAILS AT</text>'
          f'<text x="{x+c.PAD+cols[1]:.1f}" y="{c.cy:.1f}" font-size="7.4" '
          f'font-weight="700" letter-spacing="0.7" fill="{P.INK_FAINT}">GOES BACK TO</text>'
          f'<text x="{x+c.PAD+cols[2]:.1f}" y="{c.cy:.1f}" font-size="7.4" '
          f'font-weight="700" letter-spacing="0.7" fill="{P.INK_FAINT}">CLASS</text>'
          f'<text x="{x+PANEL_W-c.PAD:.1f}" y="{c.cy:.1f}" font-size="7.4" '
          f'font-weight="700" letter-spacing="0.7" text-anchor="end" '
          f'fill="{P.INK_FAINT}">MAX</text>', 5)
    c.raw(f'<rect x="{x+c.PAD:.1f}" y="{c.cy:.1f}" width="{PANEL_W-2*c.PAD:.1f}" '
          f'height="1" fill="{P.HAIRLINE}"/>', 13)

    for e in g.repairs:
        src, dst = g.by_id(e.src), g.by_id(e.dst)
        lim = (src.repair_route or {}).get("recurrence_limit", "")
        c.raw(
            f'<text x="{x+c.PAD:.1f}" y="{c.cy:.1f}" font-size="8.6" '
            f'fill="{P.INK}">{_esc(src.stage)} {_esc(src.display)}</text>'
            f'<text x="{x+c.PAD+cols[1]:.1f}" y="{c.cy:.1f}" font-size="8.6" '
            f'fill="{P.EDGE["repair"]["color"]}">{_esc(dst.stage)} '
            f'{_esc(dst.display)}</text>'
            f'<text x="{x+c.PAD+cols[2]:.1f}" y="{c.cy:.1f}" font-size="8.6" '
            f'fill="{P.INK_SOFT}">{_esc(src.defect_ownership or "")}</text>'
            f'<text x="{x+PANEL_W-c.PAD:.1f}" y="{c.cy:.1f}" font-size="8.6" '
            f'text-anchor="end" fill="{P.INK_SOFT}">×{lim}</text>', 11)
        raw = " ".join(e.condition.split())
        trigger = raw.split(" — ", 1)[1] if " — " in raw else raw
        for line in _wrap(trigger, 7.8, PANEL_W - 2 * c.PAD - 10, 2):
            c.raw(f'<text x="{x+c.PAD+10:.1f}" y="{c.cy:.1f}" font-size="7.8" '
                  f'fill="{P.INK_FAINT}">{_esc(line)}</text>', 9.5)
        c.cy += 7

    body, h = c.close()
    return body, h, 1


def _panel_checks(g: Graph, x: float, y: float) -> tuple[list[str], float, int]:
    """Middle card: the compile-time checks this graph already passed.

    It belongs on the picture because it answers the question a reader asks
    immediately after seeing seven back-edges — is any of this actually bounded?
    `every_cycle_bounded` is the one line that says yes."""
    c = _Card(x, y)
    shape = g.escalation.get("selected") or g.execution_shape
    c.section("EXECUTION SHAPE", gap=10.0)
    c.text(shape.replace("_", " "), 10.5, P.INK, weight=600, advance=13)
    feats = ", ".join(g.escalation.get("decisive_features") or [])
    if feats:
        c.paragraph("decisive: " + feats.replace("_", " "), 8.2, 3)

    if g.static_checks:
        c.section("STATIC COMPILE CHECKS")
        ok_c, bad_c = "#15803D", P.EDGE["repair"]["color"]
        for key in sorted(g.static_checks):
            ok = bool(g.static_checks[key])
            col = ok_c if ok else bad_c
            mark = "✓" if ok else "✗"
            c.raw(
                f'<text x="{x+c.PAD:.1f}" y="{c.cy:.1f}" font-size="9" '
                f'font-weight="700" fill="{col}">{mark}</text>'
                f'<text x="{x+c.PAD+14:.1f}" y="{c.cy:.1f}" font-size="8.4" '
                f'fill="{P.INK_SOFT}">{_esc(key.replace("_", " "))}</text>', 12.5)
    body, h = c.close()
    return body, h, 1


def _panel_reference(g: Graph, x: float, y: float) -> tuple[list[str], float, int]:
    """Bottom card: the stage map, the budget ceiling, and an honest statement
    of what the picture is not carrying."""
    c = _Card(x, y)

    c.section("STAGE MAP", gap=10.0)
    stage_nodes = defaultdict(list)
    for n in g.nodes:
        stage_nodes[n.stage].append(n)
    for st in sorted(stage_nodes):
        c.raw(f'<text x="{x+c.PAD:.1f}" y="{c.cy:.1f}" font-size="8.6" '
              f'font-weight="700" fill="{P.INK}">{_esc(st)}</text>'
              f'<text x="{x+c.PAD+26:.1f}" y="{c.cy:.1f}" font-size="8.6" '
              f'fill="{P.INK_SOFT}">{_esc(P.STAGE_TITLES.get(st, ""))}</text>', 11)
        names = ", ".join(n.display for n in stage_nodes[st])
        for line in _wrap(names, 8.0, PANEL_W - 2 * c.PAD - 26, 2):
            c.raw(f'<text x="{x+c.PAD+26:.1f}" y="{c.cy:.1f}" font-size="8" '
                  f'fill="{P.INK_FAINT}">{_esc(line)}</text>', 10)
        c.cy += 4

    c.section("BUDGET CEILING")
    b = g.budgets or {}
    for label, val in (("total cost", f'${b.get("max_total_cost_usd", 0):,.0f}'),
                       ("total latency",
                        f'{b.get("max_total_latency_seconds", 0)/3600:.0f} h'),
                       ("total retries", str(b.get("max_total_retries", "")))):
        c.raw(f'<text x="{x+c.PAD:.1f}" y="{c.cy:.1f}" font-size="9" '
              f'fill="{P.INK_SOFT}">{_esc(label)}</text>'
              f'<text x="{x+PANEL_W-c.PAD:.1f}" y="{c.cy:.1f}" font-size="9" '
              f'text-anchor="end" font-weight="600" fill="{P.INK}">'
              f'{_esc(val)}</text>', 15)
    c.text("Each card carries its own ceiling: cost · latency · retries.",
           8.2, P.INK_FAINT, advance=12)

    c.section("WHAT THIS PICTURE LEAVES OUT")
    c.paragraph(
        "Every node also carries reads, writes, preconditions, postconditions, "
        "an activation guard, permission requirements and an admission reason. "
        "None of that fits on a card without making the card unreadable, and the "
        "manifest already holds it in a form you can grep. Read the picture for "
        "shape and recovery; read the manifest for contracts.", 8.4)

    body, h = c.close()
    return body, h, 1


def _spell(n: int) -> str:
    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
             7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    return words.get(n, str(n))


def _cond_gist(c: str) -> str:
    if not c:
        return ""
    t = " ".join(c.split()).split(" — ")[0]
    for lead in ("outline_assessment.json records ", "review_mechanical.json records ",
                 "review_evidence.json records ", "review_disclosure.json records ",
                 "closure_comparison.json records ", "publication_findings.json records "):
        if t.startswith(lead):
            t = t[len(lead):]
            break
    if len(t) > 38:
        t = t[:38].rsplit(" ", 1)[0] + "…"
    return t
