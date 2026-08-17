# Design decisions, and the evidence behind them

Everything here was decided by rendering
`work-lib/specs/graph_doc_createtion_compile_skill/prompts/10_output/run/manifest.v1.json`
— 16 nodes, 23 edges, 7 of them repair — and looking at the result, on 16 August 2026.
Nothing here is inherited from a comparison article. Where a source's verdict and the
render disagreed, the render won and that is recorded.

Read this before changing the layout. Most of the obvious improvements were tried here
first, and several of them are why the current design looks the way it does.

## 1. D2 versus Graphviz, settled by rendering both

The research record
(`work-lib/research/workflow_graph_visualization/workflow_graph_visualization.sota.v2.md`
§9.2) left this open: sources rate D2 highest on visual quality and Graphviz highest on
cycle-heavy graphs, and this graph is moderate in size but cycle-heavy — exactly where
the two verdicts point apart. §10.1 named the fix: render the real manifest through both.
That was done. Both backends are still shipped, so the finding stays testable.

### What each produced

| | D2 / ELK | D2 / dagre | Graphviz `dot` LR | Graphviz `dot` TB |
|---|---|---|---|---|
| Canvas | 4751 × 3789 | 1000 × 3466 | **8212 × 591** | 1422 × 3766 |
| Aspect | 1.25 | 0.29 | **13.9** | 0.38 |
| Stage containers | drawn, and **scattered across the canvas** | drawn, coherent | not attempted (see §3) | not attempted |
| Node faces | **empty — markdown labels rendered as blank shapes** at d2 0.8.1 inside a classed container | plain single-line titles only | rich cards (HTML-like labels) | rich cards |
| Back-edges | crossed the whole canvas | wandered the full page height, crossing the spine repeatedly | bowed below the spine, legible | **crossed the spine repeatedly; labels floated unattached** |

### The findings

**Graphviz beats D2 on this graph, on two counts that are not close.**

1. **Node faces.** The single largest contributor to "not pedestrian" is that a node is
   a designed card — accent stripe, stage·kind tag, title, purpose, budget chip — not a
   box with a name in it. Graphviz's HTML-like labels express that directly. D2's shape
   labels cannot; its markdown labels can in principle, but at d2 0.8.1 a `|md ... |`
   label on a node carrying a class inside a container rendered as an **empty shape** —
   the containers drew, the nodes did not. That is a hard blocker, not a tuning issue.
2. **Container layout on a non-convex stage.** ELK scattered the eight stage containers
   across a 4751 × 3789 canvas with edges crossing everything. The cause is structural,
   not a bad option: `s4-artifact-manifest` is in stage S4 but sits topologically after
   *all* of S5, so no layout can make the S4 container convex without displacing S5.
   D2's headline advantage over Graphviz — stage grouping as a drawn container — is the
   thing this graph specifically defeats.

**But Graphviz does not win outright, because neither engine routes back-edges.** Under
`dot`, `constraint=false` with west ports on both ends was expected to push all seven
repair edges into a left channel. It did not. The spline solver put them wherever it
found room, which was across the forward spine, with their labels floating unattached to
any visible line. Seven of twenty-three edges rendered as noise. On a graph whose whole
point is *where a failure sends you back to*, that is a failed diagram no matter how good
the cards look.

### The decision

**Default `studio` — this skill's own layout and SVG compositor. `graphviz` and `d2`
stay behind `--backend` as working alternatives**, with `graphviz` the recommended
fallback for a wide or branchy forward graph, where a real ranking solver earns its
keep and `studio`'s single-column spine assumption breaks down.

This is not "we could not pick one". It is a narrower claim: for a manifest-shaped
graph — a deep chain with many long back-edges — the layout decision that matters is
back-edge routing, and that decision should be made explicitly rather than delegated to
a spline solver that has no idea which edges are the recovery structure.

## 2. How the back-edges are routed, and why

Seven repair edges, spans of 1, 2, 2, 4, 5, 7 and 9 ranks. Long back-edges are the
dominant cause of edge spaghetti in layered layouts; if they are illegible the diagram
has failed regardless of how it otherwise looks.

Four options were considered:

1. **Let the engine route them.** Rejected — that is exactly what was rendered and
   rejected in §1.
2. **Do not draw them; put a return tag on the source card and an inbound marker on the
   target.** Kills the spaghetti completely. Rejected because it also kills the thing a
   reader came for: the *reach* of a repair — how far back a failure throws you — is a
   spatial fact, and a text tag does not carry it.
3. **Draw them, and stratify them into a dedicated gutter.** Chosen.
4. **A separate second diagram showing only the repair graph.** Rejected as a default:
   it forces the reader to hold two pictures in their head to answer one question. Still
   a reasonable escape hatch above ~12 repair edges, where the gutter stops paying.

The chosen routing, precisely:

- The gutter sits to the **left of the spine**, between the stage rail and the cards, and
  is reserved — no forward edge, no card, no label ever enters it. That reservation is
  what makes the region readable as one thing.
- **One lane per repair edge.** Lanes are ordered by span, **widest outermost**. Ordering
  matters and the first implementation had it backwards: with short arcs outermost, every
  long route has to cross every short one on its way out. Widest-outermost makes the arcs
  nest, and nested intervals do not cross.
- Each route leaves the **left face of its source card**, runs horizontally to its lane,
  turns up the lane with a rounded corner, and re-enters the **left face of its target
  card** with an arrowhead. Orthogonal, three segments, no splines. A reader can follow it
  with a finger.
- Where a horizontal run must cross another lane's vertical run, it **hops** — the small
  break circuit diagrams use — so a crossing reads as a crossing and not as a junction.
- Two routes can land on the same node (`s2-evidence-extract` and `s4-compose` each
  receive two here). Entering at the same height would draw them as one line, so each
  endpoint gets **its own slot** on the card's left face.
- Each lane carries one pill at the midpoint of its vertical run: `<defect class> → <target
  stage> ×<recurrence limit>`. The class alone is ambiguous — two routes here are both
  `evidence` — and the target stage is what tells them apart without reading the table.
- **Crimson is spent on nothing else.** Not on emphasis, not on the terminal node, not on
  a heading. That single reservation is what makes the recovery structure findable in one
  glance, before any label is read. If you are tempted to use it for something else, the
  cost is the whole scheme.

## 3. Why `stage` is a rail and not a container

`s4-artifact-manifest` carries `stage: S4` and sits topologically after every node in S5.
Any convex box around S4 must therefore contain all of S5. Graphviz clusters and D2
containers both stretch to stay convex, so both would draw S4 swallowing S5 — a picture
that asserts a containment the pipeline does not have.

So stage is carried two ways instead, neither of which can lie:

- On the **node's own tag line** (`S4 · TOOL`), which is exact per node.
- On a **stage rail** down the left edge: one tinted band per *contiguous run* of a stage
  in topological order. S4 appears as two bands. That is not a rendering defect to hide;
  it is a real and slightly surprising fact about this pipeline, and a reader who notices
  it has learned something the JSON makes them work for.

A rail caption that does not fit its band is dropped rather than shrunk, because a caption
running into its neighbour makes two bands unreadable to save one.

## 4. What reaches the card, what reaches the sidebar, what is cut

Each node carries `id`, `kind`, `stage`, `purpose`, `reads[]`, `writes[]`,
`preconditions[]`, `postconditions[]`, `activation_guard`, `permission_requirements[]`,
`budget`, `admission_reason`, `defect_ownership`, `non_purpose`, `replay_behavior`,
`side_effects`, `tools_and_models`, and for `kind: agent` a prompt path, a validation
receipt and a QA binding. On sixteen cards that is several thousand words. All of it
cannot be on the picture; the only question is what the cut buys.

**The rule applied: the card carries what you scan, the manifest carries what you check.**
A field earns a place on the card only if a reader would use it to form a judgement about
the *shape* of the pipeline while looking at the shape.

| Field | Where it lands | Why |
|---|---|---|
| `id` | card title (stage prefix stripped, kebab expanded) | the handle everything else refers to |
| `kind` | accent stripe + tag | must be distinguishable at a glance; it is a colour, not a word to read |
| `stage` | tag + rail band | ditto |
| `purpose` | two wrapped lines on the card | the one field that answers "what is this node for" without a lookup |
| `budget` | mono chip, `$cost · latency · retries` | the cost of a repair loop is the reason recurrence limits exist; it belongs next to the loop |
| `repair_route.recurrence_limit` | `↩ ×N` pill on the card, and the lane label | marks a card as a place the run can bounce off |
| `defect_ownership` | lane label + sidebar table | names *what kind* of failure each route repairs |
| repair `condition` | sidebar table, one line under each route | the trigger is a sentence; sentences do not go on cards |
| conditional edge `condition` | a short pill on the edge | the pass condition is why the arrow exists |
| `reads` / `writes` | **counts only**, and only at `--detail full` | the paths are 100+ characters each; twelve of them on a card is a wall |
| `budgets` (graph total) | sidebar | one number for the whole page |
| `static_compile_checks` | sidebar, ticked list | answers the question seven back-edges provoke: *is any of this bounded?* `every_cycle_bounded` is the line that says yes |
| `escalation_decision.selected` | sidebar | why this is an orchestrator and not a graph runtime |
| `preconditions`, `postconditions`, `activation_guard`, `permission_requirements`, `admission_reason`, `non_purpose`, `replay_behavior`, `side_effects`, `tools_and_models`, prompt/QA receipts | **cut** | each is a contract to be *checked*, not a shape to be *seen*. They are grep-shaped, and the manifest is right there |

The cut is stated **on the diagram itself**, in the sidebar's *What this picture leaves
out*. A reader must never have to guess whether the picture is the whole truth; a diagram
that silently omits half the model is worse than one that admits it.

## 5. The render-and-verify loop

The strongest transferable finding in the research record (v2 §6.1) is a pattern, not a
tool: the two most-starred diagram skills in the ecosystem both render, then read the
raster they produced, detect layout defects, and iterate before delivering. No static
generator inspects its own output, which is why they all reproduce the same defects.

That pattern is implemented here in two halves, and both are needed:

- **`scripts/inspect_layout.py`** measures the SVG the renderer just wrote: overlapping
  text runs, type under 6.8 pt, labels spilling their card, text outside the canvas,
  over-truncation, unusable page proportions. Machine-checkable, fast, and it catches the
  boring repeatable failures before a human ever sees them. It works on the SVG rather
  than the raster on purpose: the SVG has exact coordinates, and OCR-ing a PNG to find
  text overlap would be guessing at something already known exactly.
- **The agent opens the PNG and looks at it**, per SKILL.md §3. The inspector cannot tell
  you a diagram is ugly, only that it is broken. Every defect fixed while building this
  skill — the 14:1 ribbon, the back-edges crossing the spine, the colliding rail captions,
  the dead third of the sidebar column — was found by looking, and none of them would have
  tripped a mechanical check.

Defects the inspector caught during construction, for calibration: two card-spill reports
that turned out to be the inspector miscounting `&#x27;` as six characters. Both the
renderer (emit a literal apostrophe) and the inspector (decode the entity) were fixed. A
measurement tool that lies is worse than no measurement tool.

## 6. Typography and palette

- **Near-white ground (`#F7F9FB`), white cards.** The ground separates the page from the
  document it will be pasted into; the cards then read as objects on it.
- **Ink navy (`#0F172A`) titles, slate (`#475569`) body, faint slate (`#94A3B8`) chips.**
  Three weights of grey do the hierarchy, so colour is free to carry meaning.
- **One hue per kind**: agent indigo `#3B4CCA`, tool cyan `#0E7490`, gate violet `#7C3AED`.
  Chosen to be distinguishable at stripe width and to survive greyscale printing as three
  different densities.
- **Edge hues**: sequential slate (structural, recedes), conditional green (a pass), a
  parallel fan-out cyan and dotted, repair crimson and dashed.
- **Helvetica Neue / Helvetica / Arial** for text, `SF Mono` / Menlo for the budget chip.
  A system stack, because a diagram that needs a font installed is a diagram that renders
  differently on the reviewer's machine. The chip is mono so `$0.50 · 5m · r2` aligns
  down the column and the eye can compare costs without reading them.
