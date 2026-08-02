# Input shapes and what each role reads

Field-level reference for `render_circuit.py`. Read this when a render refuses, when you
need to know whether a document can support a role before you run it, or when you are
adding a renderer.

## Contents

- [Shape A — curriculum `domain` block](#shape-a--curriculum-domain-block)
- [Shape B — `circuit_data` document](#shape-b--circuit_data-document)
- [Role → field map](#role--field-map)
- [Coordinate parsing on the breadboard](#coordinate-parsing-on-the-breadboard)
- [Rules the renderer holds to](#rules-the-renderer-holds-to)

## Shape A — curriculum `domain` block

Recognised by `electrical` and/or `build_map` at the top level. This is the shape a
curriculum's own domain schema defines (in the reference curriculum,
`curricula/<name>/domain.schema.v1.json`). The blocks the renderer reads:

```
electrical
  component_spec.part_family            → page title (required by every domain role)
  behaviour.child_level                 → subtitle on path maps
  behaviour.adult_level                 → subtitle on schematics
  behaviour.simplification_check        → subtitle on safety insets
  circuit.status                        → 'not_designed' | 'designed_verified'
  circuit.nets[].name                   → net rails
  circuit.components[].designator/part/value
  circuit.components[].pins[].pin/net/polarity
  circuit.supply.positive_net/negative_net/nominal_voltage/sequence[]
  circuit.schematic_symbol.symbol       → header tag on schematics
  ratings_and_limits[].parameter/absolute_max/unit/source
  failure_modes[].wrong_action/consequence/prevented_by/reversible
  calculations[].formula/result/unit/margin_to_rating

build_map  (one of two kinds, discriminated by map_kind)
  breadboard:
    orientation, labelled_features[], wire_endpoints[].from/to/net,
    components_placed[].part/value/orientation, placement_steps[],
    dmm_probes.probe_points[]/lead_socket/mode, safety_inset.shows
  power_path | connectivity:
    traced_path[], evidence_card.prompt, evidence_card.child_records[],
    power_on_release

power_profile
  source, nominal_voltage, permitted_range, current_protection, polarity, evidence
```

A document may also arrive wrapped: `{"domain": { ... }}`. It is unwrapped, and trace
pointers keep the `/domain` prefix so they resolve against the original file.

## Shape B — `circuit_data` document

Recognised by `terminals` **and** `legal_coordinates` at the top level. This is the
single-parent electrical-fact document (`schemas/circuit_data.schema.v1.json` in the
reference repo) that prose, tables and maps are all generated from.

```
id                                   → subtitle
component_identity.kit_roster_name   → page title (required)
primary_sources[].url_or_path/access_date/claim_scope
orientation                          → quoted verbatim in its own panel
terminals[].name/function/coordinate → the numbered chain
legal_coordinates[]                  → listed in full
rail_topology                        → rendered as the literal JSON value, including null
ratings[]                            → listed, or marked empty when the array is empty
source_bundle_sha256                 → footer stamp
```

Note what is *not* here: no nets, no components, no supply. That is why this shape supports
only the path roles. A `circuit_data` document handed to `--role schematic` refuses.

## Role → field map

| Role | Needs | Refuses when |
|---|---|---|
| `power_path`, `connectivity` | Shape B `terminals` (non-empty), or Shape A `build_map.map_kind ∈ {power_path, connectivity}` with `traced_path` | neither present; title field missing |
| `breadboard` | Shape A `build_map.map_kind == "breadboard"` | any other `map_kind`, or Shape B |
| `schematic` | Shape A `electrical.circuit.status == "designed_verified"` with `components` and `nets` | `status == "not_designed"`, missing components or nets, or Shape B |
| `safety_inset` | Shape A, at least one of `build_map.safety_inset`, `electrical.ratings_and_limits`, `electrical.failure_modes` | none of the three present |

Optional blocks degrade quietly and visibly: absent `components_placed`, `dmm_probes`,
`supply.sequence`, `power_profile` or `calculations` simply omit their section. An empty
array that the data *does* carry is rendered as `(empty in the source data)`, because "the
data says nothing here" and "the data says nothing exists here" are different facts.

## Coordinate parsing on the breadboard

Only two coordinate grammars are plotted:

- **hole** — `^[a-jA-J] ?-?_? ?\d{1,2}$`, column 1–30. `e5`, `E5`, `e-5`, `e_5`.
- **rail** — `^(top|bottom|upper|lower)[ _-]?rail([ _-]?\d{1,2})?$`. `top rail 3`,
  `bottom_rail`, `lower rail 12`. Without a number the endpoint lands at column 1.

Anything else — `module output terminal block`, `screw terminal A`, a net name — is
**not** placed. It appears in the wire table flagged *position not asserted in the data*.
Widening this grammar is fine; guessing a position for a string it cannot read is not,
because a plotted hole is a claim about where a wire goes.

## Rules the renderer holds to

1. `Canvas.text()` accepts a `pointer` or `chrome=True`, and raises on neither. There is no
   third way to get a string onto the page.
2. Fixed labels live in the `CHROME` set at the top of `render_circuit.py` and are whole
   sentences or section headings only. Anything not in it raises at render time and fails
   the audit at verify time.
3. Field captions come from `Canvas.field_label(key)`, which derives the caption from the
   key (`permitted_range` → `permitted range`). The verifier re-derives it and additionally
   requires the key to exist somewhere in the input, so a caption cannot name a field the
   document does not have — nor a *different* field that happens to be legitimate elsewhere
   on the page, which is the failure this replaced.
4. Nothing is computed *about the circuit* — no derived currents, no inferred polarity, no
   completed nets. Arithmetic is layout arithmetic only. The one exception is the 1-based
   step number on ordered items, which the verifier recognises and checks against the array
   index it cites.
5. No dates, no timestamps, no randomness: the same input and role produce byte-identical
   `.typ` output, so a diff between two renders is a diff between two datasets.
