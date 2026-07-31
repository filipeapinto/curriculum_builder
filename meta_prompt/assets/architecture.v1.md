<!-- section asset of meta_curriculum_builder.prompt.v6.md · read whole -->

## What the generator must be

Code decides, models write. Python owns lab order, state transitions, routing,
retries, checkpoints, revision targeting, every audit, and every acceptance
decision. A model never advances a state, never aggregates a verdict, never
decides a lab is done. Deterministic work — merging, validating, hashing,
rendering, aggregating, auditing, logging — uses no model at all. The full
contract is `policy/controller.v1.yaml`.

Workers are deliberately starved. Each receives only its role, its stable check
ids, the selected lab data, accepted prerequisite artifacts, its authorized input
paths, its authorized output paths, and one output schema — the block of
`schemas/lab.schema.v3.json` it is authorized to write. A worker cannot choose a
transition, scan prior versions, change acceptance rules, or create an undeclared
file.

**Twelve isolated reviewer invocations per lab.** Three passes — plan, dossier QA,
rendered PDF — across four domains: electronics, pedagogy, communication, graphic.
Twelve separate bounded calls, never batched. Reviewing a dossier and reviewing the
printed page are different acts: a diagram correct in the data can be illegible at
print size, passing the first and failing the second. Isolation is structural, not
instructed — a reviewer's authorized input paths must not include any sibling's
verdict file, and a test must fail if such a path exists.

## What a lab must be

`schemas/lab.schema.v3.json` is the contract. Seven blocks, none optional:
identity, pedagogy, sequence (5E), electronics, content, safety, visuals. Every
lab validates against it before acceptance; the controller validates
deterministically, and a failure routes to targeted revision.

Do not restate that schema here or in v7. It already encodes the pedagogy caps,
the 5E ordering, the Predict-Observe-Explain rule, the electrical model, the
provenance fields and the safety enums. `meta_prompt/assets/component_lab_template.v1.md`
carries what a schema cannot — tone, child-language rules, the safety baseline in
sentences — and governs where the schema has no field.

Two rules the schema cannot express on its own:

**One parent for every fact.** Machine-readable circuit and experiment data is the
authority for parts, pins, values, endpoints, nets, voltage, current limiting,
ratings, measurements, controller I/O and power sequence. Prose steps, connection
tables, maps, schematics, troubleshooting and adult checks are generated from that
same data. Fail closed on any inconsistency, unsafe powered circuit, missing
rating, unbounded current, illegal pin, absent current limiting, supply mismatch or
ambiguous endpoint.

**Every electrical value carries a primary source.** `RESEARCH` locates the
official datasheet or manufacturer listing for each component, and records URL,
part or family, and access date beside the value and its measurement condition. No
datasheets ship in `CREATOR`; acquiring them is part of the run. A rating that
cannot be sourced is the one legitimate `BLOCKED` case. A value recalled rather
than sourced is a failed check, not a shortcut.
