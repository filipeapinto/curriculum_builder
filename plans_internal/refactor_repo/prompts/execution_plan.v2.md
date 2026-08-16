# Curriculum Factory repository refactor — bootstrap execution plan v2

Grounding specification:
`plans_internal/refactor_repo/refactor_repository.spec.v8.html`.

This document intentionally does not fix the final prompt count or exact production,
consumer, and test mutation paths. Specification §8 requires those to be derived after
the required inventory and behavioral baseline exist.

## Bootstrap

1. Execute `P00_inventory_baseline.prompt.v3.yaml`. It creates and runs the read-only,
   schema-versioned inventory and captures the behavioral baseline. It unblocks no
   implementation mutation.
2. Execute `P00A_post_inventory_decomposition.prompt.v3.yaml`. It consumes current P00
   evidence and writes, under `prompts/resolved/`, the exact execution plan and manifest.
   It activates a v3 template only when its boundaries exactly match inventory; otherwise
   it creates a new version under `prompts/generated/`. Every activated/generated prompt
   must validate against prompt schema v4 and receive witnessed `qa-gate-codex-run`
   approval before implementation.

No downstream prompt is executable merely because it appears in
`prompt_manifest.v3.yaml`; that file is a template catalogue, not the post-inventory
authorization manifest.

## Candidate phase topology

The following order constrains dependencies but not final prompt count:

| Candidate | Objective | Candidate prerequisites |
|---|---|---|
| P01 | final packaging metadata and buildable skeleton | P00A |
| P02 | Python import/qualified-name codemod | P00A |
| P02S | TOML/JSON/YAML parser-based codemods | P00A, P01 parser pins |
| P03 | mechanical production source move | P01, P02 |
| P04 | package resources, explicit data roots, output containment | P03 |
| P05 | output-consumer, fixture, and retained-evidence migration | P04 |
| P06 | schema identity decisions and reference closure | P04 |
| P07 | live human-facing identity/documentation closure | P04, P06 |
| P08 | full clean-room release, CLI acceptance, and combined codemod safety | P02S, P05, P06, P07 |
| P09 | evidence-supported test-tree organization | P02S, P08 |
| P10 | separately authorized external rename | P09 |

P00A must split/add/omit candidates when inventory evidence requires it. Optional
subsystem decomposition remains absent unless the five specification conditions are
proved and a new exact-target, independently gated prompt is generated.

## Ownership rules

- `pyproject.toml` has one owner: P01. It must predeclare final source discovery,
  package data, entry points, dependency pins, and test discovery defaults. Later
  prompts verify it and stop on a gap; they do not edit it.
- `.github/workflows/plan26-lock-drift.yml` has one owner: P09, using the proven P02S
  YAML codemod. P07 may inspect it read-only.
- When ordered phases necessarily touch one path, P00A assigns disjoint mutation units,
  such as P03 owning relocation/import-token changes and P04 owning resource/data-root
  semantics. The resolved manifest expands each unit to path plus structured key,
  symbol, transformation class, or move operation and tests pairwise disjointness.
- P05 consumer paths and P04 modules come from inventory. Candidate templates contain
  subsystem ceilings only; resolved ownership narrows them before execution.
- The complete CLI acceptance criterion and combined Python/TOML/JSON/YAML codemod-
  safety criterion belong to P08. P03/P04 CLI checks and P02/P02S codemod checks are
  prerequisite evidence for their partial implementation boundaries, not criterion 2
  or criterion 18 completion.
