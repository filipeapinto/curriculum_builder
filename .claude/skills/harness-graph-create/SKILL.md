---
name: harness-graph-create
description: Render a harness's execution graph — swim-lanes, decision gates, fan-out/fan-in, loop-backs over persistent graph state — as a reproducible white-background PNG by default (dark neon-glow, matching graph.v1.png, available via --theme dark), plus a saved prompt/spec file documenting exactly what was drawn. Use this WHENEVER someone hands over a harness or graph-engineering definition and wants a picture of its control flow: a plan or run-prompt's "EXECUTION GRAPH" / "GRAPH STATE" section, a `prompt_graph` JSON, an explicit description of a harness's nodes/lanes/edges, or requests like "diagram this harness", "draw the execution graph", "show the harness as a graph", "make a graph like graph.v1.png", "visualize the graph engineering for this harness", "harness-graph-create", or "I need a picture of this controller's state machine". Also use it proactively whenever someone is about to hand-describe a computational graph to an image model in prose — that path produced the original graph.v1.png with no saved source, which is exactly the un-reproducible, un-auditable result this skill exists to replace. SCOPE BOUNDARY: this is for diagrams whose subject is a persistent computational/execution graph — explicit lanes, gates, fan-out/fan-in, edges that loop back over graph state. A plan's linear or simply-looping step sequence (no lanes, no persistent state, one spine) belongs to `plan-infographic` instead. An illustrative diagram of an idea for a learner (not a real control-flow) belongs to `curriculum-concept-visualization`. If what's on the table is a plan.md with numbered steps and maybe one retry loop, route there; if it's a controller/harness with a GRAPH STATE object and named nodes/edges, this is the right skill.
---

# Harness graph create

`plans/22_graph_eng_evol_01/graph.v1.png` is a good diagram — lanes, gates, a real
fan-out and fan-in, a loop-back — but nobody can regenerate it. It was produced by
describing the graph to an image model in prose, and the prose is gone. If the
harness's graph changes, or someone needs the same diagram in a different colour
scheme, or a reviewer asks "is this still accurate", there is nothing to go back
to. This skill exists to make that class of diagram **deterministic**: the same
graph spec always produces the same picture, and the spec itself is a deliverable,
not scratch work you throw away.

## What you're drawing

A harness's execution graph is not a plan's step list. A plan has one spine, maybe
with a retry loop; a harness has **persistent graph state** (candidates, an
archive, counters) and a controller that dispatches named nodes across it, with
real fan-out (one node's output feeds several downstream nodes in parallel), real
fan-in (several branches must all complete before the next node fires), and gates
whose failure sends the run back to an earlier point in the *same* run rather than
back to drafting. If the thing you're diagramming doesn't have at least one of
those — a gate, a fan-out/fan-in, or a loop over live state — it's probably a plan,
and `plan-infographic` is the right skill.

## Process

**1. Read the harness's actual graph definition — and nothing outside the
scope the user actually gave you.** Don't invent nodes, lanes, or edges from a
one-line description if a fuller source exists. But "a fuller source exists"
is not blanket permission to go find it: if the user points you at a specific
file or folder as the input, that pointer **is** the scope boundary, not a
starting point for you to widen. A folder of individual agent prompts (each
just a GOAL/TEST/LOOP contract) is not the same document as the orchestrating
plan's `EXECUTION GRAPH` section, even when both describe pieces of the same
harness and even when the orchestrating file is sitting right next to it — the
agent prompts only earn a node in the diagram for what they *themselves* say
about their own predecessor/successor (most model-node prompts state this
explicitly, e.g. `input edge: X -> this-node` / `next edge: this-node -> Y`
under their own `## GRAPH INTERFACE` heading — quote that, don't paraphrase
control flow from a different file). If drawing an accurate graph genuinely
requires content the user didn't hand you, stop and ask before pulling it in —
don't decide on their behalf that a richer, related source is what they must
have meant. Getting this wrong doesn't look like a small error: it looks like
a diagram stuffed with boxes the user never asked for and can't find the
source of, which is exactly the "why is X in here, I never gave you X"
reaction that means the whole render has to be redone from scratch.

If the user has only described the harness in prose, extract the
lanes/nodes/edges as best you can and **restate them back before rendering** —
"I'm reading this as 3 lanes (seed → evaluate → evolve), with a gate at X and a
loop back from Y to Z — is that right?" A wrong graph rendered beautifully is
still wrong, and the user is the only one who can catch it before it's drawn.

**2. Compress to a legible node count.** A harness with thirty internal state
transitions does not become thirty boxes any more than a twenty-step plan becomes
twenty boxes in `plan-infographic`. Group sub-steps that always happen together
into one node named for the movement they represent (plan 22's `dispatch_candidate
_checks` fanning into `test_candidate` / `review_candidate` / `join_candidate_
checks` is one fan-out-then-join movement, not three unrelated stops). Aim for
what a reader can trace with a finger in under a minute — `graph.v1.png` itself
has about twenty nodes across four lanes, which is close to the ceiling before a
diagram like this stops being legible.

**3. Resolve where the three files go, together, before writing any of them.**
Every graph lives under a `visualizations/` folder beside the harness's own
source file, split into `pngs/` and `prompts/` so a reviewer can look at just
the pictures or just the specs:

```
<harness-dir>/visualizations/pngs/<name>.v<N>.png
<harness-dir>/visualizations/prompts/<name>.v<N>.json
<harness-dir>/visualizations/prompts/<name>.v<N>.prompt.md
```

`scripts/outpath.py` resolves all three paths at once, sharing one version
number even though they land in two different subfolders (a plain per-folder
listing can't tell you the shared next version — that's the whole reason this
script exists rather than three separate `ls`):

```bash
read -r OUT_PNG OUT_JSON OUT_PROMPT <<< "$(python3 scripts/outpath.py <harness-dir>/visualizations <name>.harness_graph)"
```

Use `<name>.harness_graph` for a full harness diagram (`plan23.harness_graph`)
or `<name>.harness_graph` scoped by source (`plan23_prompts_only.harness_graph`)
if you deliberately narrowed the input — see the scope-boundary note in step 1.

**4. Write the JSON spec to `$OUT_JSON`.** Read `references/graph_schema.md`
first — it has the full field reference, the routing rules (which matter: they
decide whether an edge draws as a straight arrow, an elbow, or the outside loop
rail), and both palettes. Don't hand-place coordinates; the columns and lanes
you choose *are* the layout, so get them right in the data rather than fighting
the renderer.

**5. Render to `$OUT_PNG` and check the output before delivering:**

```bash
python3 scripts/render_graph.py "$OUT_JSON" -o "$OUT_PNG"   # add --theme dark for graph.v1.png's look
qlmanage -t -s 1200 -o . "$OUT_PNG"   # macOS: produces a viewable thumbnail
```

Open the thumbnail and actually look — the render script cannot see the things
that matter to a reader:
- Do any two labels overlap, or does a label sit on top of a line it isn't
  attached to?
- Does every lane's nodes visually line up to the same column grid as the lanes
  around it? If a column looks staggered, the `col` values are probably wrong,
  not the renderer.
- Do edges cross without a viewer being able to tell whether they connect? (Two
  lines crossing is fine and expected in a real graph; a line that looks like it
  enters the wrong box is not.)
- Does at least one gate exist, and does every gate's failure path go somewhere?
  A harness graph with no gates in it is almost always missing the conditions
  that made it worth drawing.

If something reads badly, it is almost always fixable by adjusting `col`/`lane`
in the spec (spread out a crowded column, move a node to its own row) rather than
by asking the renderer to lay differently — the renderer draws exactly the grid
you specify. Re-resolve fresh `$OUT_*` paths (step 3) before re-rendering — don't
reuse the same path with `--force`.

**6. Write the brief to `$OUT_PROMPT`, then tell the user what you wrote.**

| File | Contents |
|---|---|
| `visualizations/prompts/<name>.v<N>.json` | The graph spec — the editable source. |
| `visualizations/pngs/<name>.v<N>.png` | The render — white background by default, or dark neon-glow with `--theme dark` — the deliverable. |
| `visualizations/prompts/<name>.v<N>.prompt.md` | A short brief: one paragraph on what harness/graph this is and why it looks the way it does, plus the full JSON spec in a fenced block. Write it so a human *or an image-generation model* could reconstruct the same diagram from this file alone, with no other context — this is the artifact that makes the diagram auditable and regenerable, and it's the whole reason this skill exists instead of just handing back a PNG. |

Never overwrite — `scripts/outpath.py` enforces this: if `render_graph.py`
refuses a write, resolve a fresh set of paths rather than reaching for
`--force`. Tell the user which version you wrote and that older versions are
untouched — silence here is what makes people assume you replaced something.

**Deprecating a superseded version.** If a whole `<name>` line gets superseded
(the source it was scoped to turned out wrong, or a later version fixed
something structural rather than cosmetic), move its files to
`pngs/deprecated/` and `prompts/deprecated/` rather than deleting them —
`outpath.py` scans `deprecated/` too, so the version number stays retired
instead of being handed out again. Don't deprecate a version just because a
newer one exists; only when the older one is actively wrong or answers a
question nobody should ask anymore (a `<name>` built from the wrong source
file, the way `plan23.harness_graph` was superseded by
`plan23_prompts_only.harness_graph` once the scope boundary got corrected —
different `<name>`s, not different versions of one).

## Design constraints worth knowing

**White background by default; dark neon-glow (matching `graph.v1.png`) is
`--theme dark`, opt-in.** Two themes, one geometry engine — `references/
graph_schema.md` has both palettes. White is the default because most
consumers of a diagram in this repo need to print it, paste it into a doc, or
read it next to other white-background diagram-skill output; ask before
assuming dark is wanted just because the harness resembles `graph.v1.png`.
Whichever theme, keep the text big and bold and the grid tight — this class of
diagram is read on a screen or a page at a glance, not studied line by line,
so legibility comes from scale and contrast, not from restraint.

**SVG generation, not a diagramming library.** `scripts/render_graph.py` computes
an explicit grid layout and rounded orthogonal edge routing (plus a glow filter
on every stroke) from the JSON spec, then rasterizes with `rsvg-convert`. This
is the same deterministic-layout approach `plan-infographic`'s `flowdiagram.py`
uses for a single-spine plan, generalized to multiple lanes and real
fan-out/fan-in — it's what makes the same input always produce the same output,
which a general auto-layout algorithm does not reliably guarantee, and a
hand-prompted image model cannot guarantee at all.

**Reserve `style: "loop"` for a genuine return to an earlier point in the run.**
It routes all the way around the outside on a dedicated rail, which is the
right amount of visual weight for "start a new generation" or "retry the whole
thing" — and the wrong amount for "a finding flows down into the
already-adjacent evolution lane." The latter is a plain (optionally dashed
`check`) elbow. A diagram with three outer rails because every feedback path
got `style: "loop"` out of habit is exactly the clutter that makes a harness
graph unreadable; one true loop, drawn big, reads far better than three small
ones stacked on top of each other. See `references/graph_schema.md` for the
worked example.

**The prompt.md is a named requirement, not a nice-to-have.** A PNG with no
saved spec is a photograph of a moment — fine until the harness changes or
someone asks "why does this edge go there." The spec and the brief are what make
the picture answerable to that question later.
