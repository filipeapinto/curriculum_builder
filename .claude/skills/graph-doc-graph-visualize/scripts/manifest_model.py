"""Read a compiled workflow manifest and reduce it to what a diagram can carry.

Every backend in this skill consumes this module, so the decision about what
reaches the picture is made once, here, rather than drifting between renderers.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

# --- what the picture carries -------------------------------------------------
# Node face:  stage tag, kind, display name, purpose gist, budget chip, repair mark.
# Edge:       type (encoded), condition gist (conditional/repair only).
# Annex:      repair-route table (source, target, defect class, limit, escape).
# Omitted:    reads/writes path lists, pre/postconditions, activation_guard,
#             permission_requirements, prompt/QA receipts. Rationale lives in
#             references/design-decisions.md.

KINDS = ("agent", "tool", "gate", "repair")
EDGE_TYPES = ("sequential", "conditional", "parallel", "repair")


@dataclass
class Node:
    id: str
    kind: str
    stage: str
    purpose: str
    display: str
    budget_cost: float | None
    budget_latency: int | None
    budget_retries: int | None
    defect_ownership: str | None
    repair_route: dict | None
    reads: int
    writes: int
    is_entry: bool = False
    is_terminal: bool = False
    # filled by the layout pass
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0
    rank: int = 0

    @property
    def budget_chip(self) -> str:
        bits = []
        if self.budget_cost is not None:
            bits.append(f"${self.budget_cost:.2f}")
        if self.budget_latency is not None:
            bits.append(_mins(self.budget_latency))
        if self.budget_retries is not None:
            bits.append(f"r{self.budget_retries}")
        return "  ·  ".join(bits)


@dataclass
class Edge:
    src: str
    dst: str
    type: str
    condition: str = ""
    # filled by the layout pass
    lane: int = 0
    span: int = 0


@dataclass
class Graph:
    nodes: list[Node]
    edges: list[Edge]
    run_id: str
    execution_shape: str
    entry: str
    terminals: list[str]
    budgets: dict = field(default_factory=dict)
    static_checks: dict = field(default_factory=dict)
    escalation: dict = field(default_factory=dict)

    def by_id(self, nid: str) -> Node:
        for n in self.nodes:
            if n.id == nid:
                return n
        raise KeyError(nid)

    @property
    def forward(self) -> list[Edge]:
        return [e for e in self.edges if e.type != "repair"]

    @property
    def repairs(self) -> list[Edge]:
        return [e for e in self.edges if e.type == "repair"]

    def counts(self) -> dict:
        c = {"nodes": len(self.nodes), "edges": len(self.edges)}
        for k in KINDS:
            c[k] = sum(1 for n in self.nodes if n.kind == k)
        for t in EDGE_TYPES:
            c[t] = sum(1 for e in self.edges if e.type == t)
        return c


def _mins(seconds: int) -> str:
    if seconds < 90:
        return f"{seconds}s"
    m = round(seconds / 60)
    if m < 90:
        return f"{m}m"
    h = seconds / 3600
    return f"{h:.1f}h".replace(".0h", "h")


def display_name(node_id: str) -> str:
    """`s6-review-mechanical` -> `Review Mechanical`. The stage prefix is shown
    separately as a tag, so repeating it in the title wastes the widest line."""
    stem = re.sub(r"^s\d+[-_]", "", node_id)
    words = re.split(r"[-_]", stem)
    return " ".join(w.capitalize() if w.islower() else w for w in words if w)


def gist(text: str, limit: int = 96) -> str:
    """First clause of a purpose, capped. Diagrams fail on prose, not on brevity."""
    if not text:
        return ""
    t = " ".join(text.split())
    for stop in (": ", " — ", ". "):
        i = t.find(stop)
        if 24 <= i <= limit:
            t = t[:i]
            break
    if len(t) > limit:
        cut = t[:limit].rsplit(" ", 1)[0]
        t = cut + "…"
    return t


def defect_word(node: Node) -> str:
    """The one word that names what a repair edge is repairing."""
    return (node.defect_ownership or "repair").strip()


def load(path: str | Path) -> Graph:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    for key in ("nodes", "edges"):
        if key not in raw or not isinstance(raw[key], list):
            raise ValueError(f"manifest has no `{key}` array: {path}")

    entry = raw.get("entry_node_id", "")
    terminals = list(raw.get("terminal_node_ids", []))

    nodes: list[Node] = []
    for n in raw["nodes"]:
        b = n.get("budget") or {}
        nodes.append(
            Node(
                id=n["id"],
                kind=n.get("kind", "agent"),
                stage=n.get("stage", ""),
                purpose=n.get("purpose", ""),
                display=display_name(n["id"]),
                budget_cost=b.get("max_cost_usd"),
                budget_latency=b.get("max_latency_seconds"),
                budget_retries=b.get("max_retries"),
                defect_ownership=n.get("defect_ownership"),
                repair_route=n.get("repair_route"),
                reads=len(n.get("reads") or []),
                writes=len(n.get("writes") or []),
                is_entry=n["id"] == entry,
                is_terminal=n["id"] in terminals,
            )
        )

    known = {n.id for n in nodes}
    edges: list[Edge] = []
    for e in raw["edges"]:
        src, dst = e["from"], e["to"]
        if src not in known or dst not in known:
            raise ValueError(f"edge references an unknown node: {src} -> {dst}")
        edges.append(
            Edge(src=src, dst=dst, type=e.get("type", "sequential"),
                 condition=e.get("condition", "") or "")
        )

    return Graph(
        nodes=nodes,
        edges=edges,
        run_id=raw.get("run_id", ""),
        execution_shape=raw.get("execution_shape", ""),
        entry=entry,
        terminals=terminals,
        budgets=raw.get("budgets") or {},
        static_checks=raw.get("static_compile_checks") or {},
        escalation=raw.get("escalation_decision") or {},
    )
