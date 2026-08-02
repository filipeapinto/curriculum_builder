---
name: electronics-circuit-visualization
description: Render fact-bearing electronics visuals — breadboard build maps, schematic/netlist diagrams, unpowered power-path and connectivity maps, and safety insets — deterministically from structured circuit data, producing a typst source file and a compiled PNG in which every element traces back to a field in the input. Use this skill WHENEVER a diagram has to be *correct about a real circuit*: "draw the breadboard layout for this lab", "make the wiring diagram from this circuit JSON", "render the schematic from this netlist", "visualise the power path for L01", "I need the build map for this unit", "diagram which pin goes to which net", "make the safety inset for this build", or whenever a user hands over circuit data (nets, components with designators and pins, supply, wire_endpoints, terminals, coordinates, ratings) and wants a picture of it. Also use it proactively when someone is about to describe a circuit in prose and have an image model draw it — that path measures about 8% topological accuracy and is exactly what this skill exists to replace. SCOPE BOUNDARY: this skill is only for visuals that carry exact circuit or wiring facts a learner could be misled by. It is NOT for conceptual, illustrative or explanatory diagrams that assert no wiring (concept maps, timelines, pedagogy or process diagrams, generic infographics) — those belong to a general-purpose visualization skill, and forcing them through here will fail, because this skill refuses to draw anything the input data does not state.
---

# Electronics circuit visualization

A wiring diagram is not a picture of a circuit; it is a **claim about a circuit**, and a
child or a technician will act on it. If the diagram says the resistor sits between the
rail and the anode, someone builds it that way. So the only acceptable production route is
one where the diagram cannot say anything the data does not already say.

That rules out the obvious approach. A model narrating a circuit and an image generator
drawing the narration measures roughly **8% topological accuracy** on published circuit
work — the failure is not sloppiness, it is that nothing in that pipeline is *checkable*.
It also rules out the subtler version: a model hand-writing typst from the data. That
produces something that usually looks right, and no one can tell which elements were read
off the data and which were remembered, inferred, or tidied up.

So this skill splits the job. **You choose the role and hand over the file. A script does
the drawing.** `scripts/render_circuit.py` computes the geometry from the input document
and emits typst; you never author the diagram. In exchange, the render comes with a trace
manifest naming, for every string on the page, the JSON pointer it came from, and
`scripts/verify_trace.py` audits that manifest against the input. The audit is the
deliverable's warrant — run it, always, and show the user the result.

## The workflow

1. **Find the data.** One JSON document. Two shapes are accepted; the script detects which
   (see *Input shapes* below). If the user points at a lab or unit rather than a file, look
   for the circuit data it references and use that — never retype values into a new file.
2. **Pick the role** with the user's words, not your own inference. The roles are
   `breadboard`, `schematic`, `power_path`, `connectivity`, `safety_inset`.
3. **Render:**
   ```bash
   python3 scripts/render_circuit.py \
     --input <data>.json --role <role> --out <dir>/<name>
   ```
   It writes `<name>.typ`, `<name>.png` (landscape, white, 200 ppi, Helvetica, no network)
   and `<name>.trace.json`. Requires `typst` on PATH.
4. **Audit, every time:**
   ```bash
   python3 scripts/verify_trace.py \
     --input <data>.json --trace <dir>/<name>.trace.json --typ <dir>/<name>.typ
   ```
   PASS means: every data element's pointer resolves to the field it cites, no string
   reached the page without a trace entry, and every fixed label is in the renderer's closed
   vocabulary. **Report the PASS line to the user** — the counts are the evidence that the
   picture is trustworthy, and a diagram delivered without them is just a picture again.
5. **Look at the PNG** before you hand it over. The audit proves the elements are honest;
   it cannot see a collision or an overflowing box.

## When the data will not support the role

The renderer exits with status 2 and names the missing field:

```
cannot render role 'schematic': schematic role needs
/electrical/circuit/status == 'designed_verified'; this document says 'not_designed'
```

This is the skill working, not failing. Tell the user which field is missing and stop.
Do not fill the gap — not from the prose around the data, not from a datasheet you
recall, not from what the circuit "obviously" is. A missing field means nobody has
evidenced that fact yet, and inventing it puts an unevidenced claim on a page a child
will build from. If the role was simply wrong for the document (a `not_designed` circuit
can still have a path map), suggest the role the data does support.

## What the pictures are, and what they deliberately are not

Each role renders the facts the data actually holds, and marks the difference between a
fact and a drawing convention:

- **`schematic`** is a net-bus diagram, not a symbol-library schematic: named net rails,
  component boxes, one traced stub per pin with a junction dot, and the full connection
  table underneath. Component *positions* carry no meaning and the page says so. The
  topology is exactly the pin→net pairs in the data, which is the part that has to be right.
- **`breadboard`** draws a generic grid and plots only endpoints whose coordinate can be
  read (`e5`, `top rail 3`). An endpoint that cannot be parsed is **not guessed onto the
  board** — it drops to the wire table marked *position not asserted in the data*. Only
  the features listed in `labelled_features` get labelled.
- **`power_path` / `connectivity`** render the ordered path as a numbered chain, with each
  terminal's name, function and coordinate, the orientation statement verbatim, and the
  sources. Arrows are labelled *trace order* because that is what the array is; they are
  not current. Nothing gains a polarity mark that the data does not state — the foundation
  contract is polarity-neutral on purpose, and a `+` you added is a claim you cannot source.
- **`safety_inset`** leads with the inset's own `shows` string, then ratings with their
  sources, failure modes as wrong action → consequence → prevented by, and the power
  profile. Absolute maxima are the point of the page; they are never rounded or restated.

## Input shapes

Two documents are accepted, detected automatically:

| Shape | Recognised by | Roles it supports |
|---|---|---|
| Curriculum `domain` block | `electrical` and/or `build_map` at the top level | all five, depending on `build_map.map_kind` and `circuit.status` |
| `circuit_data` document | `terminals` and `legal_coordinates` at the top level | `power_path`, `connectivity` |

A wrapper object with a `domain` key is unwrapped, and pointers in the trace stay prefixed
`/domain/...` so they still resolve against the file the user gave you.

Read `references/input-shapes.md` when you need the exact field names — which fields each
role reads, which are required, and how a role degrades when an optional block is absent.

## Extending it

If a curriculum needs a role that does not exist, add a renderer function to
`render_circuit.py` and register it in `RENDERERS`. Three rules keep the guarantee intact:

- every string placed with `c.text()` passes either a `pointer` into the input or
  `chrome=True`, and any new whole-sentence label joins the `CHROME` set;
- anything that **captions a value with its field name** goes through `c.field_label(key)`,
  which derives the caption from the key. Choosing captions by hand is how a row ends up
  labelled `prevented by` next to a `current_protection` value — a page that lies while
  every individual label is legitimate somewhere else on it. Derived captions make that
  unrepresentable, and the verifier re-checks the derivation;
- nothing about the circuit is computed. Layout arithmetic only.

The canvas raises on an untraced string, and `verify_trace.py` independently re-derives
every check from the compiled `.typ`, so a renderer that quietly starts inventing content
fails the audit rather than shipping.

Do not add a "freehand" or "describe it yourself" path. The moment the page can contain
something the data does not, the audit stops meaning anything, and the diagram is back to
being a picture someone has to check by hand.
