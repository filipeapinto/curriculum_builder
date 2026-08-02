# Repository Guidelines

## Project Structure & Module Organization

- `policy/` contains the calibration, controller, route, limit, failure, and check manifests — the data code reads. `policy/routing/` holds the model-routing manifests. Put curriculum-specific rejection fixtures in `curricula/<name>/fixtures/`.
- `schemas/` holds the JSON Schemas that define valid YAML/JSON inputs. Keep a manifest and its matching schema version aligned.
- `meta_prompt/` contains the run contract and the prose a model reads. That contract is `curriculum.prompt.v1.md`, one file: given a curriculum root it produces that curriculum, and it does not know what subject it is teaching. It has no `section` assets — it states its own rules — and three `companion` assets its own table names, which are inputs a worker reads rather than contract text. Companions live in `meta_prompt/assets/`, and a file there that no table row names is unowned. `tests/meta_prompt_source.py` is the only definition of "the prompt" any checker uses, and `tests/check_meta_prompt.py` asks the separate question of whether an agent handed it could start. `meta_prompt/docs/` explains the contract in diagrams and is orientation only — where it and the contract disagree, the contract wins. The v6 meta prompt built a *generator* and is retired under `meta_prompt/deprecated/` with the six section assets it composed; nothing may read them.
- `curricula/<name>/` holds one curriculum's facts and evidence. `docs/` contains the explainer Markdown, Typst source, and rendered graphic. `plans/` is remediation/design history.
- `tests/` is the gate harness: `tests/run_gates.sh <phase>` runs every gate registered in `tests/gates/registry.py` with an activation phase at or below `<phase>`, in dependency order. `tests/fixtures/` and `tests/selftest/` are never read by a production check.
- Treat `plans/legacy_v3/` as archival reference only. Its runner targets a retired external directory layout and is not the local build entry point.

### Contract assets

The live asset set, stated here because a shape declared in one place is
self-certifying: whoever deletes an asset and its row in the prompt's own table can
delete its line in `tests/meta_prompt_source.py` in the same edit, and every check stays
green. This table is maintained for a human reader and is compared against that module
in both directions, so agreeing with it is evidence rather than restatement. Adding or
retiring a companion is an edit in three places, and that is the discipline, not an
oversight. `section` assets compose into the contract; `companion` assets are inputs a
worker reads. `curriculum.prompt.v1.md` states its own rules, so there are no `section`
rows to state — a `section` row appearing here is a contract that has been split again.

| Asset | Kind |
|---|---|
| `meta_prompt/assets/unit_prose.v1.md` | companion |
| `meta_prompt/assets/pedagogy.v1.md` | companion |
| `meta_prompt/assets/model_selector_prompt.v1.md` | companion |

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
python3 -c "import json,yaml; from jsonschema import Draft202012Validator as V; V(json.load(open('schemas/curriculum.schema.v5.json'))).validate(yaml.safe_load(open('curricula/arduino_kit/arduino_kit_curriculum.v5.yaml'))); V(json.load(open('schemas/calibration.schema.v1.json'))).validate(yaml.safe_load(open('policy/calibration.v1.yaml')))"
```

Render the architecture explainer after changing its Typst source:

```sh
typst compile docs/how_it_works.typ /tmp/how_it_works.pdf
```

Do not present an unexecuted check as a passing test. The check inventory is **two kinds of file**: `policy/checks.v1.yaml` holds the checks that bind every run regardless of curriculum, and `curricula/<name>/checks.v1.yaml` holds the checks whose subject is that curriculum's own files. Both validate against `schemas/checks.schema.v1.json`; only the owner differs, and the gates read them as one inventory.

## Style and Naming

Use two-space YAML indentation, valid JSON with two-space indentation, and concise sentence-case Markdown headings. Preserve the existing versioned-file pattern: `name.vN.yaml`, `name.vN.json`, and `name.vN.md`. Retention follows three distinct words with three distinct meanings — `deprecated/` for a superseded artifact nothing may read, `legacy_v3/` for a prior system retained as actively cited evidence, and `name.vN.ext` for in-place coexistence while both versions are live. Use `LNN` lab IDs and lowercase kebab-case slugs (for example, `safe-power`). Make changes narrowly: calibration, curriculum, schemas, and the meta prompt must remain consistent. Safety constraints are requirements, not editorial suggestions—never weaken a gate merely to make an artifact pass.

## Testing Guidance

For each changed YAML/JSON input, run its corresponding schema validation, then `./tests/run_gates.sh <phase>`. Add an adversarial fixture when introducing a rejection rule — under `tests/fixtures/` for a refactor gate, under `curricula/<name>/fixtures/` for curriculum evidence — and state its expected outcome in `policy/checks.v1.yaml`. Review rendered documentation visually for clipped text, missing graphics, and stale claims.

## Commit and Pull Request Guidance

Use short, imperative, scoped commits, such as `curriculum: clarify L01 power boundary`. Pull requests should explain the changed contract, list validated schemas/checks, link the relevant plan or issue, and include rendered-document screenshots when documentation visuals change.
