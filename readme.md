# Curriculum Factory

A contract-first, curriculum-neutral pipeline for producing curriculum units from a
supplied manifest and curriculum-owned domain rules.

The Python distribution is `curriculum-factory`; its installed package is
`curriculum_factory`, with production sources under `src/curriculum_factory/`.

The active contract is `meta_prompt/curriculum.prompt.v1.md`. It reads an immutable
engine plus one immutable curriculum, writes only below a required output root, and
derives the unit count from the supplied manifest.

## Install and verify

```sh
python3 -m pip install -e '.[dev]'
python3 -m pytest -q
curriculum-factory-run-curriculum --help
```

Repository-owned policy, schemas, curricula, and generated outputs remain outside the
installed package. Commands that consume them accept an explicit repository/data root;
generated artifacts are restricted to that root's ignored `outputs/` boundary.

The current Arduino curriculum uses
`curricula/arduino_kit/arduino_kit_curriculum.v5.yaml`. Superseded contracts and
documentation are retained in their respective `deprecated/` folders.

See `docs/images/png/curriculum_pipeline_infographic.v2.png` for the current architecture. The
ImageGen production brief is in
`docs/images/prompts/curriculum_pipeline_infographic.v2.prompt.md`.
