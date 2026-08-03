# curriculum_builder

A contract-first, curriculum-neutral pipeline for producing curriculum units from a
supplied manifest and curriculum-owned domain rules.

The active contract is `meta_prompt/curriculum.prompt.v1.md`. It reads an immutable
engine plus one immutable curriculum, writes only below a required output root, and
derives the unit count from the supplied manifest.

## Current state

The repository currently provides policy, schemas, fixtures, curriculum-owned domain
verification, and the repository gate harness. The runtime controller, logger,
renderer, source-fetching run, and live model routes do not yet exist, and no unit has
been generated. Those boundaries are tracked by `RT-5` and `RT-7` in
`policy/deferred.v1.yaml`.

The current Arduino curriculum uses
`curricula/arduino_kit/arduino_kit_curriculum.v5.yaml`. Superseded contracts and
documentation are retained in their respective `deprecated/` folders.

See `docs/how_it_works.md` and
`docs/png/curriculum_pipeline_infographic.v2.png` for the current architecture. The
ImageGen production brief is in
`docs/prompts/curriculum_pipeline_infographic.v2.prompt.md`.
