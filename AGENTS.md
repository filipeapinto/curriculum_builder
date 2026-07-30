# Repository Guidelines

## Project Structure & Module Organization

- `assets/` contains the curriculum, calibration, controller, route, and check manifests. Put rejection fixtures in `assets/fixtures/`.
- `schema/` holds the JSON Schemas that define valid YAML/JSON inputs. Keep a manifest and its matching schema version aligned.
- `meta_prompt/` contains the generator contract and model-routing policy; `pedagogy.md` records the teaching rationale.
- `docs/` contains the explainer Markdown, Typst source, and rendered graphic. `plans/` is remediation/design history.
- Treat `assets/legacy/` as archival reference only. Its runner targets a retired external directory layout and is not the local build entry point.

## Validation, Rendering, and Development

There is no package manifest, build system, or committed automated test suite. Validate every edited manifest against its schema before review. For the two active top-level YAML manifests:

```sh
python3 -c "import json,yaml; from jsonschema import Draft202012Validator as V; V(json.load(open('schema/curriculum.schema.v4.json'))).validate(yaml.safe_load(open('assets/curriculum.v4.yaml'))); V(json.load(open('schema/calibration.schema.v1.json'))).validate(yaml.safe_load(open('assets/calibration.v1.yaml')))"
```

Render the architecture explainer after changing its Typst source:

```sh
typst compile docs/how_it_works.typ /tmp/how_it_works.pdf
```

Do not present an unexecuted check as a passing test; `assets/checks.v1.yaml` is the authoritative check inventory.

## Style and Naming

Use two-space YAML indentation, valid JSON with two-space indentation, and concise sentence-case Markdown headings. Preserve the existing versioned-file pattern: `name.vN.yaml`, `name.vN.json`, and `name.vN.md`. Use `LNN` lab IDs and lowercase kebab-case slugs (for example, `safe-power`). Make changes narrowly: calibration, curriculum, schemas, and the meta prompt must remain consistent. Safety constraints are requirements, not editorial suggestions—never weaken a gate merely to make an artifact pass.

## Testing Guidance

For each changed YAML/JSON input, run its corresponding schema validation. Add an adversarial fixture under `assets/fixtures/` when introducing a rejection rule, and state its expected outcome in `assets/checks.v1.yaml`. Review rendered documentation visually for clipped text, missing graphics, and stale claims.

## Commit and Pull Request Guidance

This workspace has no accessible Git history, so no local convention can be inferred. Use short, imperative, scoped commits, such as `curriculum: clarify L01 power boundary`. Pull requests should explain the changed contract, list validated schemas/checks, link the relevant plan or issue, and include rendered-document screenshots when documentation visuals change.
