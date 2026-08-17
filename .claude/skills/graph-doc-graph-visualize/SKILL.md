---
name: graph-doc-graph-visualize
description: Render a compiled workflow manifest (manifest.v1.json / manifest-draft.v1.json from the graph-doc-* family, or any nodes+typed-edges JSON of that shape) as a publication-grade diagram a human can actually reason from — stage rail, per-kind node cards carrying purpose and budget, typed edges, and every repair back-edge routed through a dedicated nested gutter instead of scribbled across the forward flow. Produces SVG or PNG at an exact path, then mechanically inspects its own render for overlapping text, microtype, spilled labels and unusable page proportions before delivering. Use this whenever someone wants to SEE a workflow graph, manifest, pipeline or DAG rather than read its JSON — "draw the graph for this manifest", "visualize manifest.v1.json", "what does this pipeline actually look like", "diagram the workflow graph", "show me the repair loops", "picture of the document-creation graph", "render the compiled manifest", "I need this graph in the report" — and also proactively whenever a reader is trying to decide how to restructure a pipeline, where a failure routes back to, or whether the cycles are bounded, because those questions are answered by the picture far faster than by grepping the manifest. Prefer this over hand-rolling Graphviz or Mermaid for anything manifest-shaped; default-styled flowchart output is exactly what this skill exists to replace.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# graph-doc-graph-visualize: draw the graph so the recovery structure is the thing you see

## What this produces, and what it does not

One diagram, at exactly the path you name, from one compiled manifest. SVG is the
native artifact; PNG is a local rasterisation of it. Nothing else is written unless
you ask for `--keep-source`.

This skill does not decide what the graph *is*. Its caller supplies the approved
manifest. It does not edit that manifest. If the manifest looks wrong, report the
problem; do not draw a corrected graph that was never approved.

It also does not draw the **meta-graph** — the skill family itself
(`goal-define → graph-define → graph-build → graph-test`). That is fixed for every
run and belongs in the documentation of how the family works. This skill draws the
*created* graph: the one a specific manifest describes, different for every document.

## Machine contract

A strict, non-interactive entry point, suitable for admission as a graph node under
`graph-doc-graph-define/references/operator-library.md`'s A1–A7. Everything below is
what a caller checks; nothing here depends on a conversational turn.

**Invocation.**

```bash
python3 .claude/skills/graph-doc-graph-visualize/scripts/render_manifest.py \
  --manifest <path/to/manifest.v1.json> \
  --out      <path/to/diagram.svg|png> \
  [--backend studio|graphviz|d2] [--detail compact|standard|full] \
  [--title TEXT] [--subtitle TEXT] [--scale 1.5] [--keep-source] \
  [--status-path <path>]
```

**A1 — Named input path.** `--manifest` is the single required input: a JSON file
carrying `nodes[]` and typed `edges[]` in the shape required by
`plans_internal/create_system_doc/system_documentation_artifact.schema.v6.json`'s
`graph_visualization.manifest`, or a compatible workflow manifest. The skill reads that
file and nothing else. It does not follow `intake_ref`, `prompt_path`, `reads[]` or `writes[]`
to disk — those are drawn as declarations, never opened.

**A2 — Named output path.** `--out` is the exact artifact path. The extension decides
the format (`.svg` or `.png`; anything else fails at stage `input`). No directory is
inferred, nothing is renamed, and nothing is written "beside the source". With
`--keep-source` the intermediate `.dot`/`.d2`/`.svg` is additionally written beside
`--out` with the same stem — that is the only case where a second file appears, and
it only ever appears when asked for.

**A3 — Checkable artifact.** After exit 0 the caller asserts:

```bash
# PNG
test -s "<out>" && file "<out>" | grep -q "PNG image data"
# SVG
test -s "<out>" && head -c 4096 "<out>" | grep -q "<svg" && tail -c 2048 "<out>" | grep -q "</svg>"
```

The script runs that same check on itself before exiting 0, so a truncated or
zero-byte artifact is a failure, not a success with a bad file.

**A4 — Failure signal.** On any failure the script exits **non-zero** (2) and writes a
status record to `<out>.failure.json`, or to `--status-path` when given:

```json
{"status": "failed", "stage": "input|layout|raster|verify|internal",
 "reason": "<one line>", "output_path": "<out>"}
```

No artifact is written at `--out` on failure, and a stale `.failure.json` from a
previous run is removed on success. Known failure signatures a caller can match:
`manifest not found`, `manifest is not a readable workflow manifest`,
`--out must end in .svg or .png`, `required binary \`dot\` is not on PATH`,
`required binary \`d2\` is not on PATH`, `no SVG rasteriser found`,
`the forward edge set (non-repair edges) contains a cycle`.

**A5 — No required interactive turn.** Every input comes from `--manifest` and the
flags. Ambiguity resolves to a declared default (`--backend studio`,
`--detail standard`, title and subtitle derived from the manifest's own `run_id`,
counts and `execution_shape`) or to an A4 failure. The script never asks a question.

**A6 — Declared side effects and permissions.**

| | |
|---|---|
| Network access | **None.** No fetch, no icon CDN, no telemetry, no package install at runtime. `studio` needs no external binary at all; `graphviz` shells out to local `dot`; `d2` shells out to local `d2`. PNG output shells out to a local rasteriser (`rsvg-convert`, `inkscape`, or the `cairosvg` Python package), whichever is present. |
| Writes outside the output path | **None**, except: `<out>.failure.json` (or `--status-path`) on failure, and the intermediate source file beside `--out` only when `--keep-source` is passed. Parent directories of `--out` are created if missing. |
| Reads outside the input path | **None.** Only `--manifest` is opened. |
| Publication / outbound contact | **None.** Nothing is published, posted, uploaded or emailed. |
| Process execution | Local subprocesses only: `dot`, `d2`, `rsvg-convert`, `inkscape` — each invoked with fixed argument lists, never a shell string. |
| Permission class | `execution`. Not `release`. |

**A7 — Cost class.** Deterministic and cheap: no model call, no network. Under 2 s and
under $0.00 for a 16-node graph on a laptop. Budget as `max_cost_usd: 0.0`,
`max_latency_seconds: 60`, `max_retries: 1`.

## The design, in one paragraph

The graph this serves is fifteen ranks deep, at most two nodes wide, and **a third of
its edges run backwards** — repair routes reaching up to nine ranks upstream. That
shape, not a style preference, drives every decision: the spine runs top-to-bottom
because laid left-to-right it renders as an unreadable 14:1 ribbon; the repair edges
are lifted out of the layout entirely and routed through a reserved gutter, one lane
each, widest span outermost so the arcs nest instead of tangling; and crimson is
reserved for repair alone, so the recovery structure is findable before you read a
single label. The full argument, including what was rendered and rejected, is in
[`references/design-decisions.md`](references/design-decisions.md) — read it before
changing the layout, because most obvious "improvements" were tried there first.

## Workflow

### 1. Read the manifest before you render it

Open the manifest and note four things, because they determine whether the defaults
fit: how many ranks deep the forward graph is, how many repair edges there are and how
far they reach, whether any stage is non-contiguous in topological order, and how long
the `purpose` strings are. A graph with forty nodes and no back-edges wants different
treatment from this one; see *When the defaults do not fit* below.

### 2. Render

```bash
python3 scripts/render_manifest.py --manifest <manifest> --out <out.svg>
```

`--detail` picks how much of each node reaches its card:

| `--detail` | On the card face |
|---|---|
| `compact` | stage · kind tag, name, budget chip |
| `standard` *(default)* | the above plus a two-line purpose and the repair-origin mark |
| `full` | the above plus the node's `reads`/`writes` counts |

Everything else — `reads[]` and `writes[]` themselves, `preconditions`,
`postconditions`, `activation_guard`, `permission_requirements`, `admission_reason`,
prompt and QA receipts — is deliberately **not** on the picture. The reasoning is in
`references/design-decisions.md` §4, and the diagram says so itself in its sidebar,
so a reader is never left wondering whether the picture is the whole truth.

### 3. Inspect the render — mechanically, then with your eyes

This is the part that separates this skill from every static generator, and it is not
optional. Generators reproduce the same defects forever because none of them ever
looks at what it produced.

```bash
python3 scripts/inspect_layout.py --svg <out.svg> --report <out>.inspect.json
```

It measures the SVG and reports overlapping text runs, type below 6.8 pt, labels
spilling their card, text outside the canvas, over-truncation, and page proportions
outside a usable range. Exit 1 means a blocker; `--strict` fails on warnings too.

Then **open the raster and look at it.** The inspector cannot tell you a diagram is
ugly, only that it is broken. Read the image and answer specifically:

- Can you trace the forward flow without your eye being caught by a back-edge?
- Does every repair arc read as a single continuous route from source to target?
- Is any label sitting on top of a line in a way that makes the line ambiguous?
- Is the page balanced, or is there a large void the composition does not justify?
- Can you tell `agent` from `tool` from `gate` without consulting the legend?

Name what is wrong in those terms, fix it, re-render, look again. Do not grade the
output by reading the code that produced it.

### 4. Deliver

Report the artifact path, the backend, the inspector's status, and — if you iterated —
what was wrong at each round. If the inspector still reports a blocker you could not
resolve, say so plainly rather than shipping it quietly.

## Backends

Three, and the choice was settled by rendering the real manifest through each rather
than by reputation. `references/design-decisions.md` §1 has the evidence.

| `--backend` | What it is | Use it when |
|---|---|---|
| `studio` *(default)* | This skill's own layout and SVG compositor. No external layout engine. | Always, for manifest-shaped graphs. It is the only one that routes back-edges deliberately. |
| `graphviz` | Styled DOT through local `dot`. HTML-label cards, `constraint=false` back-edges. | The forward graph is wide or branchy rather than a chain, where a real ranking solver earns its keep. Requires `dot`. |
| `d2` | D2 containers per stage, classes per kind, through local `d2`. | You want `stage` drawn as an actual container and the stages are contiguous in topological order. Requires `d2`. |

## When the defaults do not fit

- **A wide, branchy forward graph** (many nodes per rank). `studio`'s single-column
  spine assumes a chain. Use `--backend graphviz`, which will rank it properly.
- **A stage that is not contiguous in topological order** — as `S4` is here, sitting
  both before and after all of `S5`. Do not force it into a container; a convex box
  would have to swallow the stages in between and would be a lie about the flow.
  `studio` draws such a stage as two rail bands, which is the honest rendering.
- **More than ~12 repair edges.** The gutter widens by one lane each and eventually
  costs more page than it earns. Fall back to `--detail compact` and consider
  splitting the diagram by stage range.
- **A forward edge set with a cycle.** `studio` fails at stage `internal` with
  `the forward edge set (non-repair edges) contains a cycle`. That is a manifest
  defect — a cycle that is not typed `repair` — and belongs back with
  the manifest owner, not routed around here.

## Common failure modes

- **Grading the picture by reading the code.** Symptom: "it renders, so it's fine."
  Fix: open the PNG. Every real defect this skill has fixed was found by looking.
- **Letting back-edges into the ranking.** Symptom: the spine reorders itself around
  a repair route and the forward flow stops being a flow. Fix: back-edges annotate the
  layout, they never constrain it.
- **Putting the whole node on the card.** Symptom: eight-point paragraphs inside a
  box. Fix: the card carries what you scan; the manifest carries what you check.
- **Stage boxes over a non-convex stage.** Symptom: a container that swallows two
  other stages to stay rectangular. Fix: rail bands, or no grouping at all.
- **Colour spent on decoration.** Symptom: crimson used for emphasis somewhere other
  than a repair edge, and the back-edges stop being findable at a glance.

## Quality gate

Before delivering: the artifact exists at `--out` and passes its A3 check; the
inspector reports `clean` (or every remaining `warn` is named and justified in the
report); and you have read the rendered image and can state what it shows. A file that
exists is not a diagram that works.
