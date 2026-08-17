"""D2 backend — stage containers, per-kind classes, markdown node faces.

Kept because D2 is the one engine that groups `stage` natively as a drawn
container. Its weakness on this graph is recorded in
references/design-decisions.md; this backend exists so that claim stays testable
rather than becoming folklore.
"""

from __future__ import annotations

import palette as P
from manifest_model import Graph, gist


def _md(n, detail: str) -> str:
    accent = P.KIND.get(n.kind, P.KIND["agent"])["accent"]
    lines = [f"### {n.display}"]
    if detail in ("standard", "full"):
        g = gist(n.purpose, 80)
        if g:
            lines.append(g)
    chip = n.budget_chip
    if chip:
        lines.append(f"`{chip}`")
    if n.repair_route:
        lim = n.repair_route.get("recurrence_limit")
        tgt = n.repair_route.get("target_node_id", "")
        lines.append(f"**↩ {tgt} ×{lim}**")
    body = "\n\n".join(lines)
    return body


def emit(g: Graph, detail: str = "standard", title: str = "", engine: str = "elk") -> str:
    L = []
    a = L.append
    a("vars: {")
    a("  d2-config: {")
    a(f"    layout-engine: {engine}")
    a("    theme-id: 0")
    a("    pad: 40")
    a("  }")
    a("}")
    a("")
    a("classes: {")
    for kind, spec in P.KIND.items():
        a(f"  {kind}: {{")
        a("    style: {")
        a(f'      fill: "{P.PAPER}"')
        a(f'      stroke: "{spec["accent"]}"')
        a("      stroke-width: 2")
        a("      border-radius: 10")
        a("      shadow: true")
        a(f'      font-color: "{P.INK}"')
        a("    }")
        a("  }")
    a("  stageband: {")
    a("    style: {")
    a(f'      fill: "{P.STAGE_TINTS[0]}"')
    a(f'      stroke: "{P.HAIRLINE}"')
    a("      stroke-width: 1")
    a("      border-radius: 12")
    a(f'      font-color: "{P.INK_SOFT}"')
    a("      font-size: 15")
    a("    }")
    a("  }")
    a("}")
    a("")
    if title:
        a(f'title: "{title}" {{ near: top-center; style.font-size: 26; '
          f'style.bold: true; style.font-color: "{P.INK}" }}')
        a("")

    stages = sorted({n.stage for n in g.nodes})
    for st in stages:
        caption = P.STAGE_TITLES.get(st, "")
        a(f'{st}: "{st}  ·  {caption}" {{')
        a("  class: stageband")
        for n in [x for x in g.nodes if x.stage == st]:
            if detail == "compact":
                a(f'  {n.id}: "{n.display}" {{')
            else:
                a(f'  {n.id}: |md')
                for line in _md(n, detail).splitlines():
                    a(f"    {line}")
                a("  | {")
            a(f"    class: {n.kind}")
            if n.is_entry or n.is_terminal:
                a("    style.stroke-width: 3")
            a("  }")
        a("}")
    a("")

    for e in g.edges:
        s = P.EDGE[e.type]
        src = f"{g.by_id(e.src).stage}.{e.src}"
        dst = f"{g.by_id(e.dst).stage}.{e.dst}"
        label = ""
        if e.type == "conditional":
            label = _gist(e.condition)
        elif e.type == "repair":
            n = g.by_id(e.src)
            lim = (n.repair_route or {}).get("recurrence_limit", "")
            label = f'{n.defect_ownership or "repair"} x{lim}'
        head = f'{src} -> {dst}'
        if label:
            head += f': "{label}"'
        a(head + " {")
        a("  style: {")
        a(f'    stroke: "{s["color"]}"')
        a(f'    stroke-width: {int(round(s["width"] * 1.2))}')
        if s["dash"]:
            a("    stroke-dash: 4")
        a("    font-size: 11")
        a(f'    font-color: "{s["color"]}"')
        a("  }")
        a("}")

    return "\n".join(L) + "\n"


def _gist(c: str) -> str:
    if not c:
        return ""
    t = " ".join(c.split()).split(" — ")[0].replace('"', "'")
    if len(t) > 44:
        t = t[:44].rsplit(" ", 1)[0] + "..."
    return t
