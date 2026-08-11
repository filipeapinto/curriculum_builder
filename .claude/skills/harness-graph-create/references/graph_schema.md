# Harness graph schema

Read this when you're about to write the JSON spec for `scripts/render_graph.py`, or
when you need the exact meaning of a field.

Contents:
1. [The schema](#the-schema)
2. [Choosing lane, col and kind](#choosing-lane-col-and-kind)
3. [Edge styles and how routing actually works](#edge-styles-and-how-routing-actually-works)
4. [Palette](#palette)
5. [Worked example](#worked-example)

---

## The schema

```json
{
  "title": "Evolutionary Prompt Graph",
  "lanes": [
    {"id": "top", "label": null, "role": "neutral"},
    {"id": "eval", "label": "EVALUATION", "role": "primary"},
    {"id": "review", "label": "EXTERNAL REVIEW", "role": "caution"}
  ],
  "nodes": [
    {"id": "start", "kind": "start", "lane": "top", "col": 0, "label": "START"},
    {"id": "compile", "kind": "stage", "lane": "eval", "col": 1, "label": "Compile Population",
     "detail": "optional second line of prose"},
    {"id": "decide", "kind": "gate", "lane": "eval", "col": 3, "label": "Decide Generation"},
    {"id": "promoted", "kind": "terminal", "lane": "review", "col": 4, "label": "PROMOTED", "role": "success"}
  ],
  "edges": [
    {"from": "start", "to": "compile", "style": "flow"},
    {"from": "decide", "to": "compile", "label": "next generation", "style": "loop"}
  ],
  "legend": [
    {"swatch": "role:primary", "label": "Evaluation backbone"},
    {"swatch": "role:accent", "label": "Evolution / variation"},
    {"swatch": "edge:loop", "label": "Loop back (retry / next gen)"}
  ]
}
```

- `lanes` — an ordered list of grid **rows**, top to bottom. `label` is what's
  printed as a floating, role-coloured heading over the row's own left-most node
  (no background tint — at this palette's darkness a filled band is more visual
  weight than the boundary is worth), with a thin rule of the same colour
  underlining it out to the band's own right-most node, so a multi-row zone
  reads as one named section rather than a label floating loose over the rows
  below it; `role` also picks that row's node border/glow colour. A row with
  `label: null` draws no heading — use this for a plain row that shouldn't
  visually belong to any zone (a `START` row sitting above all the lanes, the
  way `graph.v1.png` draws it).
- `nodes` — every node needs `id`, `kind`, `lane` (a lane `id`), `col` (an integer
  grid column, shared across every lane so nodes in different rows still line up),
  and `label`. `detail` adds a second, smaller line inside a `stage` box.
  `role` overrides the node's own colour instead of inheriting its lane's.
- `edges` — `from`/`to` are node ids. `label` is optional. `style` is one of
  `flow` (default), `loop`, or `check` — see below.
- `legend` — optional. A boxed key drawn top-right, level with the title (the
  canvas widens automatically so it never overlaps the title or spills off the
  edge). Each item is `{"swatch": "...", "label": "..."}`: `swatch` is either
  `role:<name>` (draws that role's fill/ink as a small rounded swatch —
  matches whatever `role` a node or lane band actually uses) or
  `edge:<flow|loop|check>` (draws a short line sample in that edge style's
  colour, dashed for `loop`/`check`). `label` is free text — write what the
  colour or style *means in this harness*, not the role/style name itself
  ("Independent parallel review lane", not "accent"). Leave `legend` out
  entirely for a small graph where the role/style grammar is self-evident from
  the zone headings alone — a legend restating three colours a reader can
  already see in the two zone labels next to them is clutter, not polish. Add
  it once a graph has enough roles or edge styles in play (four or more
  role/style meanings, or any meaning — like a specific loop style — that
  isn't already spelled out by a zone heading) that a reader would otherwise
  have to guess what a colour or a dashed line stands for.

## Choosing lane, col and kind

**`kind`** — four values:
- `stage`: a rounded rectangle. The ordinary unit of work.
- `gate`: a diamond. Use it for anything the harness's own graph state describes
  as a decision — in plan 22's terms, anything with more than one outgoing edge
  guarded by a condition (`decide_generation`, `compare_with_champion`).
- `terminal`: a pill. Use it for `START` and for the graph's actual terminal
  states (`PROMOTED`, `CONVERGENCE_EXHAUSTED`, ...). Give it `role: "success"` or
  `role: "failure"` so it reads as an outcome, not just another step.
  `start`/`stop` are accepted as synonyms for `terminal` if that reads more
  naturally while you're transcribing a harness's own vocabulary.

**`lane`** — a lane is a *row*, not necessarily a whole semantic zone. If a zone
in the harness (like plan 22's `EVOLUTION` section, which contains
`select_parents`, four operators, and `merge_offspring` at different vertical
positions) needs more than one row of nodes, give it several consecutive lanes
that all share the same `label` — the renderer merges consecutive same-label rows
into one band automatically. A row that holds only one kind of node most of the
time (like a lane just for gates) is completely normal too.

**`col`** — a global left-to-right position shared by every lane. Assign columns
by when a node happens **in the harness's own control flow**, not by where it
looks tidy: if `decide_generation` guards a transition to both `freeze_for_review`
(continues right) and `select_parents` (drops into an earlier stage of the loop),
give `freeze_for_review` a higher column than `decide_generation` and don't worry
about `select_parents`'s column relative to it — the router handles a forward
edge landing at an earlier column just fine (see below). Two nodes can share a
column if they happen at the same point in the flow in different lanes.

## Edge styles and how routing actually works

`style` only controls the stroke — solid vs dashed, and colour. It does **not**
decide the path. The path is chosen from the geometry of the two endpoints:

| Endpoints | Path |
|---|---|
| same lane, adjacent column | a straight arrow |
| same lane, columns skipped | a small bump above the row, clearing the nodes between |
| different lane, any column | an elbow via a shared bus row between the two lanes |
| `style: "loop"`, or same lane going backward | routed around the **outside**, on a dedicated rail below the whole diagram |

The one thing worth understanding: **only a real loop pays for the outside
rail.** An ordinary forward transition that happens to land at an earlier column
(`decide_generation`'s "no eligible target, generation remains" edge into
`select_parents`, which sits earlier in the diagram than the gate that reaches it)
still gets the cheap direct elbow, because it changes lanes — it is not marked
`style: "loop"` and isn't in the "same lane, backward" case. Reserve `style:
"loop"` for edges that are genuinely returning the graph to an earlier state:
retries, "next generation", a rejected-review path back to variation. Use
`style: "check"` for a dashed edge that isn't a loop but also isn't the primary
forward path — an informational or monitoring relationship between lanes.

Fan-out and fan-in are not special cases — they fall out of the elbow rule for
free. If four edges all leave the same source into the same target lane, they all
compute the same bus row and read as one shared branch, the way
`select_parents -> {repair, mutate_prompts, mutate_topology, recombine_candidates}`
does in plan 22's own graph.

**Known rough edges** (fine for a first diagram; hand-adjust if they land badly):
the same-lane bump always arcs the same fixed height, so two skip-edges in one
row that overlap in column range will visually cross; edge labels are placed
just off the path with a canvas-coloured backdrop but a very dense diagram can
still get a label sitting close to another line — a gate with three or more
outgoing elbows fanning to different lanes is the case most likely to crowd,
since every label wants to sit close to the same shared exit point. If a
diagram is dense enough for this to matter, prefer fewer, more compressed
nodes over fighting the router — see "compress to a legible node count" in
`SKILL.md`. Also place a node directly under its *actual* source column where
you can (a downstream node one lane down and several columns over from the
node that actually feeds it is what produces a label sitting on top of an
unrelated line — see plan 23's `qa_gate_postmortem` in the worked example
below, which sits at the same column as `qa_gate_verify`, its real source,
rather than under the node it happens to be drawn near).

## Palette

Two themes, selected with `render_graph.py`'s `--theme` flag (`light`,
default, or `dark`). Same geometry, same five-role grammar, same field names
in the spec either way — a spec written for one theme renders correctly in
the other; only ink/fill/glow change.

**`light`** (default) — white canvas, light role-tinted fills, no glow. For
printing, pasting into a doc, or sitting next to this repo's other
white-background diagram-skill output.

| role | ink (border/text) | fill | use it for |
|---|---|---|---|
| `primary` | `#174a7e` (blue) | `#eaf2f9` | the evaluation/scoring backbone |
| `support` | `#146447` (green) | `#e9f5ef` | a secondary backbone |
| `accent` | `#6b3fa0` (purple) | `#f1ecf8` | the evolution/variation backbone |
| `caution` | `#875b00` (amber) | `#fbf3df` | external review, or anything gated |
| `alert` | `#9b352d` (red) | `#faecea` | — |
| `success` | `#146447` border | solid `#22c55e` fill | a `terminal` node that is the goal state |
| `failure` | `#9b352d` border | solid `#ef4444` fill | a `terminal` node that is a non-goal terminal |
| `neutral` | `#17202a` (dark grey) | `#eef1f4` | `START`, or anything with no zone of its own |

**`dark`** — deep navy canvas, glowing role-coloured borders, the same
visual language `plans/22_graph_eng_evol_01/graph.v1.png` used. Ask before
reaching for this instead of assuming it — see SKILL.md's design-constraints
note.

| role | ink (border/glow) | fill | use it for |
|---|---|---|---|
| `primary` | `#22d3ee` (cyan) | `#0e2230` | the evaluation/scoring backbone |
| `support` | `#34d399` (green) | `#0e2420` | a secondary backbone |
| `accent` | `#a78bfa` (purple) | `#1c1a33` | the evolution/variation backbone |
| `caution` | `#fbbf24` (amber) | `#2a2110` | external review, or anything gated |
| `alert` | `#f87171` (red) | `#2a1414` | — |
| `success` | `#16a34a` border | solid `#22c55e` fill | a `terminal` node that is the goal state |
| `failure` | `#b91c1c` border | solid `#ef4444` fill | a `terminal` node that is a non-goal terminal |
| `neutral` | `#94a3b8` (grey) | `#1a2233` | `START`, or anything with no zone of its own |

Colour is never the only carrier: zone labels and node shape (pill / rect /
diamond) distinguish everything colour does, so the diagram survives
greyscale in either theme. Terminal-node title text is solid white in both
themes (both themes give `success`/`failure` a solid saturated fill, which
white sits on cleanly); every other node's title text is the theme's body
text colour, not the role colour.

## Worked example

`plans/22_graph_eng_evol_01/run.prompt.md`'s own `EXECUTION GRAPH` and `GRAPH
STATE` sections are a real harness definition worth reading end to end before
writing a spec from scratch. `plans/23_graph_eng_evol_01/plan23.harness_graph
.v3.prompt.md` is a second full worked example (a later, QA-gated version of
the same evolutionary-run harness) with its complete JSON spec inline — its
`v1`/`v2` siblings in the same directory are earlier iterations kept for
history, and are worth a look specifically for what didn't work: `v1` shows
the label/rail/terminal-width bugs this schema's rough-edges notes above were
written from, and `v2` shows a correct-but-overloaded white-background render
before the palette and the loop-vs-elbow judgement call in "Edge styles" above
were fixed.

`evals/fixtures/plan22.harness_graph.v2.json` is the same plan-22 spec as
`v1` with a `legend` block added — diff it against `v1.json` to see exactly
what the field looks like in a real spec, and compare `v2.png` against
`v1.png` to see what it buys: a boxed key top-right and a rule under each
zone heading, without touching a single node or edge.

## Known rough edge: labels on a same-lane adjacent-column edge

A `straight` edge (same lane, adjacent column) only has `COL_GAP` (60px) of
horizontal room between the two boxes, and a label wider than that will
overlap both. This is different from the bump/elbow/rail cases, which have a
whole row or the outer margin to place a label in. Two ways out, both cheap:
drop the label on the common-path edge and let the *other* branch's label
imply it by contrast (e.g. an unlabeled "compiled" edge next to a labelled
"all failed" edge needs no label of its own), or insert a spare column so the
edge becomes a `bump` instead of a `straight` and the label arcs clear above
the row.
