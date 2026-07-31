# Repository Guidelines

## Project Structure & Module Organization

- `policy/` contains the calibration, controller, route, limit, failure, and check manifests — the data code reads. `policy/routing/` holds the model-routing manifests. Put curriculum-specific rejection fixtures in `curricula/<name>/fixtures/`.
- `schemas/` holds the JSON Schemas that define valid YAML/JSON inputs. Keep a manifest and its matching schema version aligned.
- `meta_prompt/` contains the generator contract and the prose a model reads. Since v6 that contract is `meta_curriculum_builder.prompt.v6.md` plus the assets its own asset table names: a `section` asset is part of the contract, a `companion` is an input a worker reads. Both live in `meta_prompt/assets/` — `meta_prompt/assets/pedagogy.v1.md` records the teaching rationale — and a file there that no table row names is unowned. `tests/check_meta_prompt.py` composes the prompt with its sections and is the only definition of "the meta prompt" any checker uses.
- `curricula/<name>/` holds one curriculum's facts and evidence. `docs/` contains the explainer Markdown, Typst source, and rendered graphic. `plans/` is remediation/design history.
- `tests/` is the gate harness: `tests/run_gates.sh <phase>` runs every gate registered in `tests/gates/registry.py` with an activation phase at or below `<phase>`, in dependency order. `tests/fixtures/` and `tests/selftest/` are never read by a production check.
- Treat `plans/legacy_v3/` as archival reference only. Its runner targets a retired external directory layout and is not the local build entry point.

## Retention

Three words, three meanings, and none of them is a synonym for the others.
`deprecated/` holds an artifact superseded by a newer version of itself, retained for
history — **nothing may read it**. `plans/legacy_v3/` holds a prior *system*, retained
as evidence and actively cited: `policy/failures.v1.yaml` requires a path and line
from it for every A-series defect. `name.vN.ext` is in-place coexistence while both
versions are live, which is why a superseded contract stays in `schemas/` rather than
moving. Every `deprecated/` carries a `.gitkeep`, or the convention disappears on
clone.

Every top-level folder is answered here explicitly, so no folder's retention is left
to inference:

| Folder | Keeps a `deprecated/`? | Why |
|---|---|---|
| `policy/` | yes | a manifest is superseded in place; the prior version is history a run must never read |
| `curricula/` | yes | a retired curriculum is evidence of what was taught, never a live input |
| `schemas/` | yes — gated | a schema may enter only when zero accepted artifacts and zero manifests reference it, because `--resume` refuses to mutate accepted work and the contract a lab was accepted under must keep resolving |
| `meta_prompt/` | yes | a superseded prompt is read by nobody, but it records why a contract changed |
| `tests/` | no | a gate outlives no rule; when the rule goes, the gate that proved it is deleted, and an archived detector is a second copy nothing keeps equal |
| `docs/` | no | explainers are regenerated from `how_it_works.typ`; an archive of stale claims is a drift risk rather than a record |
| `plans/` | yes | every plan and prompt pair below the active version lives in `plans/<topic>/deprecated/`, which is what keeps the executing agent off a superseded plan |

## Validation, Rendering, and Development

There is no package manifest or build system. The committed automated checks are the gate harness under `tests/`. Validate every edited manifest against its schema before review. For the two top-level manifests the harness itself validates:

```sh
python3 -c "import json,yaml; from jsonschema import Draft202012Validator as V; V(json.load(open('schemas/curriculum.schema.v4.json'))).validate(yaml.safe_load(open('curricula/arduino_kit/arduino_kit_curriculum.v4.yaml'))); V(json.load(open('schemas/calibration.schema.v1.json'))).validate(yaml.safe_load(open('policy/calibration.v1.yaml')))"
```

Render the architecture explainer after changing its Typst source:

```sh
typst compile docs/how_it_works.typ /tmp/how_it_works.pdf
```

Do not present an unexecuted check as a passing test; `policy/checks.v1.yaml` is the authoritative check inventory.

## Style and Naming

Use two-space YAML indentation, valid JSON with two-space indentation, and concise sentence-case Markdown headings. Preserve the existing versioned-file pattern: `name.vN.yaml`, `name.vN.json`, and `name.vN.md`. Retention follows three distinct words with three distinct meanings — `deprecated/` for a superseded artifact nothing may read, `legacy_v3/` for a prior system retained as actively cited evidence, and `name.vN.ext` for in-place coexistence while both versions are live. Use `LNN` lab IDs and lowercase kebab-case slugs (for example, `safe-power`). Make changes narrowly: calibration, curriculum, schemas, and the meta prompt must remain consistent. Safety constraints are requirements, not editorial suggestions—never weaken a gate merely to make an artifact pass.

## Testing Guidance

For each changed YAML/JSON input, run its corresponding schema validation, then `./tests/run_gates.sh <phase>`. Add an adversarial fixture when introducing a rejection rule — under `tests/fixtures/` for a refactor gate, under `curricula/<name>/fixtures/` for curriculum evidence — and state its expected outcome in `policy/checks.v1.yaml`. Review rendered documentation visually for clipped text, missing graphics, and stale claims.

## Commit and Pull Request Guidance

Use short, imperative, scoped commits, such as `curriculum: clarify L01 power boundary`. Pull requests should explain the changed contract, list validated schemas/checks, link the relevant plan or issue, and include rendered-document screenshots when documentation visuals change.
