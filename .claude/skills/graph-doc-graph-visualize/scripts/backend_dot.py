"""Graphviz DOT backend — styled, not default, and composed as a page.

Three deliberate decisions, all explained in references/design-decisions.md:

1. `rankdir=TB`. The spine runs top-to-bottom because this graph is 12 ranks
   deep and at most 3 wide; laid left-to-right it renders as a 14:1 ribbon no
   one can read on a page.
2. Repair edges are `constraint=false` with west ports at both ends, so all
   seven back-edges leave and re-enter on the left and share one gutter. A
   back-edge that participates in ranking drags its target upstream and turns
   the spine into spaghetti; excluded from ranking, it becomes an annotation on
   a spine that still reads.
3. `stage` is not a cluster. `s4-artifact-manifest` sits topologically after all
   of S5, so an S4 cluster would have to swallow S5 to stay convex. Stage is
   carried on the node's own tag line and by the stage rail instead, which
   costs nothing and lies about nothing.
"""

from __future__ import annotations

from html import escape

import palette as P
from manifest_model import Graph, Node, gist

CARD_W = 232


def _card(n: Node, detail: str) -> str:
    spec = P.KIND.get(n.kind, P.KIND["agent"])
    accent, kind_label = spec["accent"], spec["label"]
    tag = f"{n.stage}  ·  {kind_label}"
    if n.is_entry:
        tag += "  ·  ENTRY"
    if n.is_terminal:
        tag += "  ·  TERMINAL"

    rows = [
        f'<TR><TD COLSPAN="2" BGCOLOR="{accent}" HEIGHT="5" FIXEDSIZE="TRUE" '
        f'WIDTH="{CARD_W}"></TD></TR>',
        '<TR><TD COLSPAN="2" HEIGHT="6"></TD></TR>',
        f'<TR><TD ALIGN="LEFT" COLSPAN="2">'
        f'<FONT POINT-SIZE="7" COLOR="{accent}" FACE="{P.FONT}-Bold">'
        f'{escape(tag)}</FONT></TD></TR>',
        f'<TR><TD ALIGN="LEFT" COLSPAN="2">'
        f'<FONT POINT-SIZE="12.5" COLOR="{P.INK}" FACE="{P.FONT}-Bold">'
        f'{escape(n.display)}</FONT></TD></TR>',
    ]
    if detail in ("standard", "full"):
        rows.append(
            f'<TR><TD ALIGN="LEFT" COLSPAN="2">'
            f'<FONT POINT-SIZE="8" COLOR="{P.INK_SOFT}">'
            f'{_wrap(gist(n.purpose, 84), 36)}</FONT></TD></TR>'
        )
    rows.append('<TR><TD COLSPAN="2" HEIGHT="3"></TD></TR>')
    right = f"{n.reads} in / {n.writes} out" if detail == "full" else " "
    rows.append(
        f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="7.5" COLOR="{P.INK_FAINT}">'
        f'{escape(n.budget_chip)}</FONT></TD>'
        f'<TD ALIGN="RIGHT"><FONT POINT-SIZE="7.5" COLOR="{P.INK_FAINT}">'
        f'{escape(right)}</FONT></TD></TR>'
    )
    if n.repair_route:
        lim = n.repair_route.get("recurrence_limit")
        tgt = n.repair_route.get("target_node_id", "")
        rows.append(
            f'<TR><TD ALIGN="LEFT" COLSPAN="2">'
            f'<FONT POINT-SIZE="7.5" COLOR="{P.EDGE["repair"]["color"]}" '
            f'FACE="{P.FONT}-Bold">&#8617; {escape(tgt)} &#215;{lim}</FONT></TD></TR>'
        )
    rows.append('<TR><TD COLSPAN="2" HEIGHT="5"></TD></TR>')
    return (
        '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="2" '
        f'WIDTH="{CARD_W}">{"".join(rows)}</TABLE>>'
    )


def _wrap(text: str, width: int) -> str:
    if not text:
        return "&#32;"
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(escape(cur))
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(escape(cur))
    return '<BR ALIGN="LEFT"/>'.join(lines) + '<BR ALIGN="LEFT"/>'


def _legend() -> str:
    rows = ['<TR><TD ALIGN="LEFT" COLSPAN="2">'
            f'<FONT POINT-SIZE="10" FACE="{P.FONT}-Bold" COLOR="{P.INK}">'
            'HOW TO READ THIS</FONT></TD></TR>',
            '<TR><TD COLSPAN="2" HEIGHT="6"></TD></TR>',
            '<TR><TD ALIGN="LEFT" COLSPAN="2">'
            f'<FONT POINT-SIZE="7.5" FACE="{P.FONT}-Bold" COLOR="{P.INK_FAINT}">'
            'NODE KIND — the stripe above each card</FONT></TD></TR>']
    for kind in ("agent", "tool", "gate"):
        s = P.KIND[kind]
        rows.append(
            f'<TR><TD ALIGN="LEFT" WIDTH="26" BGCOLOR="{s["accent"]}">'
            f'<FONT POINT-SIZE="7" COLOR="{s["accent"]}">__</FONT></TD>'
            f'<TD ALIGN="LEFT"><FONT POINT-SIZE="8" COLOR="{P.INK_SOFT}">'
            f'{_kind_gloss(kind)}</FONT></TD></TR>'
        )
    rows.append('<TR><TD COLSPAN="2" HEIGHT="8"></TD></TR>')
    rows.append('<TR><TD ALIGN="LEFT" COLSPAN="2">'
                f'<FONT POINT-SIZE="7.5" FACE="{P.FONT}-Bold" COLOR="{P.INK_FAINT}">'
                'EDGE TYPE</FONT></TD></TR>')
    for et in ("sequential", "conditional", "parallel", "repair"):
        s = P.EDGE[et]
        glyph = "&#8212;&#8212;" if not s["dash"] else "&#8211; &#8211;"
        rows.append(
            f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="{s["color"]}" '
            f'FACE="{P.FONT}-Bold">{glyph}</FONT></TD>'
            f'<TD ALIGN="LEFT"><FONT POINT-SIZE="8" COLOR="{P.INK_SOFT}">'
            f'{escape(s["label"])}</FONT></TD></TR>'
        )
    rows.append('<TR><TD COLSPAN="2" HEIGHT="8"></TD></TR>')
    rows.append(
        '<TR><TD ALIGN="LEFT" COLSPAN="2">'
        f'<FONT POINT-SIZE="8" COLOR="{P.INK_SOFT}">'
        'Every repair back-edge runs in the left gutter.<BR ALIGN="LEFT"/>'
        'Its label names the defect class that owns it<BR ALIGN="LEFT"/>'
        'and how many times it may fire before the<BR ALIGN="LEFT"/>'
        'terminal escape takes over.<BR ALIGN="LEFT"/>'
        '</FONT></TD></TR>'
    )
    return ('<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" '
            f'WIDTH="300">{"".join(rows)}</TABLE>>')


def _kind_gloss(kind: str) -> str:
    return {
        "agent": "agent — runs a validated prompt",
        "tool": "tool — deterministic script",
        "gate": "gate — deterministic pass/fail",
    }[kind]


def _annex(g: Graph) -> str:
    hdr = ('<TR>'
           f'<TD ALIGN="LEFT"><FONT POINT-SIZE="7.5" FACE="{P.FONT}-Bold" '
           f'COLOR="{P.INK_FAINT}">WHEN IT FAILS HERE</FONT></TD>'
           f'<TD ALIGN="LEFT"><FONT POINT-SIZE="7.5" FACE="{P.FONT}-Bold" '
           f'COLOR="{P.INK_FAINT}">IT GOES BACK TO</FONT></TD>'
           f'<TD ALIGN="LEFT"><FONT POINT-SIZE="7.5" FACE="{P.FONT}-Bold" '
           f'COLOR="{P.INK_FAINT}">CLASS</FONT></TD>'
           f'<TD ALIGN="RIGHT"><FONT POINT-SIZE="7.5" FACE="{P.FONT}-Bold" '
           f'COLOR="{P.INK_FAINT}">MAX</FONT></TD>'
           '</TR>')
    rows = ['<TR><TD ALIGN="LEFT" COLSPAN="4">'
            f'<FONT POINT-SIZE="10" FACE="{P.FONT}-Bold" COLOR="{P.INK}">'
            'THE SEVEN REPAIR ROUTES</FONT></TD></TR>',
            '<TR><TD COLSPAN="4" HEIGHT="6"></TD></TR>', hdr,
            f'<TR><TD COLSPAN="4" BGCOLOR="{P.HAIRLINE}" HEIGHT="1"></TD></TR>']
    for e in g.repairs:
        src, dst = g.by_id(e.src), g.by_id(e.dst)
        lim = (src.repair_route or {}).get("recurrence_limit", "")
        rows.append(
            f'<TR>'
            f'<TD ALIGN="LEFT"><FONT POINT-SIZE="8" COLOR="{P.INK}">'
            f'{escape(src.stage)} {escape(src.display)}</FONT></TD>'
            f'<TD ALIGN="LEFT"><FONT POINT-SIZE="8" COLOR="{P.EDGE["repair"]["color"]}">'
            f'{escape(dst.stage)} {escape(dst.display)}</FONT></TD>'
            f'<TD ALIGN="LEFT"><FONT POINT-SIZE="8" COLOR="{P.INK_SOFT}">'
            f'{escape(src.defect_ownership or "")}</FONT></TD>'
            f'<TD ALIGN="RIGHT"><FONT POINT-SIZE="8" COLOR="{P.INK_SOFT}">'
            f'&#215;{lim}</FONT></TD>'
            f'</TR>'
        )
    return ('<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" '
            f'WIDTH="300">{"".join(rows)}</TABLE>>')


def emit(g: Graph, detail: str = "standard", title: str = "", subtitle: str = "") -> str:
    L = []
    a = L.append
    a("digraph manifest {")
    a(f'  bgcolor="{P.GROUND}";')
    a("  rankdir=TB; splines=spline; overlap=false; newrank=true;")
    a("  nodesep=0.55; ranksep=0.62; pad=0.45;")
    a(f'  fontname="{P.FONT}";')
    a(f'  node [shape=box, style="rounded,filled", fillcolor="{P.PAPER}", '
      f'color="{P.HAIRLINE}", penwidth=1.1, margin=0, fontname="{P.FONT}"];')
    a(f'  edge [fontname="{P.FONT}", fontsize=7.5, arrowsize=0.6, penwidth=1.4];')
    if title:
        head = f'<B>{escape(title)}</B>'
        if subtitle:
            head += (f'<BR ALIGN="LEFT"/><FONT POINT-SIZE="10" COLOR="{P.INK_SOFT}">'
                     f'{escape(subtitle)}</FONT><BR ALIGN="LEFT"/>')
        a(f'  labelloc="t"; labeljust="l"; fontsize=19; fontcolor="{P.INK}"; '
          f'label=<{head}>;')

    for n in g.nodes:
        extra = ""
        if n.is_entry or n.is_terminal:
            extra = f', color="{P.KIND[n.kind]["accent"]}", penwidth=2.0'
        a(f'  "{n.id}" [label={_card(n, detail)}{extra}];')

    for e in g.forward:
        s = P.EDGE[e.type]
        style = "dashed" if e.type == "parallel" else "solid"
        lbl = ""
        if e.type == "conditional":
            lbl = (f', label=" {escape(_condition_gist(e.condition))} ", '
                   f'fontcolor="{s["color"]}", labeldistance=1.4')
        elif e.type == "parallel":
            lbl = f', label=" in parallel ", fontcolor="{s["color"]}"'
        a(f'  "{e.src}" -> "{e.dst}" [color="{s["color"]}", style={style}, '
          f'penwidth={s["width"]}{lbl}];')

    for e in g.repairs:
        s = P.EDGE["repair"]
        src = g.by_id(e.src)
        lim = (src.repair_route or {}).get("recurrence_limit", "")
        lbl = f'{src.defect_ownership or "repair"} &#215;{lim}'
        a(f'  "{e.src}" -> "{e.dst}" [color="{s["color"]}", style=dashed, '
          f'penwidth={s["width"]}, constraint=false, tailport=w, headport=w, '
          f'label=<<FONT POINT-SIZE="7.5" COLOR="{s["color"]}">{lbl}</FONT>>, '
          f'arrowhead=vee, arrowsize=0.7];')

    # Legend and the repair annex are a disconnected component. dot packs
    # disconnected components left to right in declaration order, so declaring
    # them last puts the reading key beside the spine rather than on top of it.
    a("  subgraph cluster_key {")
    a('    style="rounded,filled"; fillcolor="#FFFFFF"; '
      f'color="{P.HAIRLINE}"; penwidth=1.1; margin=14; label="";')
    a(f'    "__legend" [label={_legend()}, shape=plaintext, fillcolor="{P.PAPER}", '
      'style="filled", color="#FFFFFF"];')
    a(f'    "__annex" [label={_annex(g)}, shape=plaintext, fillcolor="{P.PAPER}", '
      'style="filled", color="#FFFFFF"];')
    a('    "__legend" -> "__annex" [style=invis];')
    a("  }")
    a("}")
    return "\n".join(L)


def _condition_gist(c: str) -> str:
    if not c:
        return ""
    t = " ".join(c.split()).split(" — ")[0]
    for lead in ("outline_assessment.json records ", "review_mechanical.json records ",
                 "review_evidence.json records ", "review_disclosure.json records ",
                 "closure_comparison.json records ", "publication_findings.json records "):
        if t.startswith(lead):
            t = t[len(lead):]
            break
    if len(t) > 40:
        t = t[:40].rsplit(" ", 1)[0] + "…"
    return t
