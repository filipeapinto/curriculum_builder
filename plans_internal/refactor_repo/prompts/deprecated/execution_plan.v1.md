# Curriculum Factory repository refactor — execution plan v1

Grounding specification:
`plans_internal/refactor_repo/refactor_repository.spec.v8.html`.

This plan is based on the repository observed on 15 August 2026: production code
occupies `runtime/` (47 Python files plus package resources), no `pyproject.toml`
exists, 32 test modules occupy the importable `tests/runtime/` tree, the Plan 26
workflow names that tree directly, and ignored `outputs/` contains roughly 70 MB
across hundreds of generated files. Those figures are decomposition evidence, not
facts that execution may reuse: P00 must recollect them immediately before work.

## Ordered checkpoints

| ID | Principal objective | Depends on | Reviewable checkpoint | Successors |
|---|---|---|---|---|
| P00 | Build the read-only inventory and capture the behavioral baseline | none | schema-valid inventory plus baseline report | P01, P02 |
| P01 | Add a buildable src-layout packaging skeleton | P00 | wheel/sdist skeleton and inspected metadata | P03 |
| P02 | Build and prove the syntax-aware import codemod | P00 | codemod, fixtures, dry-run, idempotence proof | P03 |
| P03 | Move the production package mechanically and rewrite imports | P01, P02 | source-map parity, installed import/CLI checkpoint | P04 |
| P04 | Repair packaged resources, repository data roots, and output containment | P03 | resource/root tests and installed-distribution checks | P05, P06, P07 |
| P05 | Migrate durable output consumers and restore empty-output independence | P04 | fixture manifests and consumer-closure proof | P08 |
| P06 | Record and enforce schema identifier compatibility decisions | P04 | identifier ledger and resolution tests | P07, P08 |
| P07 | Close product/repository identity and documentation references | P04, P06 | exceptions ledger and executable documentation checks | P08 |
| P08 | Run clean-room release verification and produce migration/rollback reports | P05, P06, P07 | clean-checkout evidence and final repository checkpoint | P09 |
| P09 | Organize the test tree only as supported by collected evidence | P08 | retained or moved test layout with shadowing proof | P10 |
| P10 | Inventory and, only after explicit authorization, perform the external rename | P09 | external-operation evidence or a truthful pending-authorization report | complete |

P10 does not inherit authorization from earlier repository prompts. Optional
subsystem decomposition is not scheduled: the current inventory has not established
the five required conditions in specification §4. If P00/P08 evidence later supports
it, author a new prompt with an exact target tree, non-overlapping mutation ownership,
schema-v4 validation, and its own `qa-gate-codex-run` result before any move.

## Global execution rules

- Execute in ID order and never run a prompt whose prerequisites have not passed.
- Capture baseline commit, dirty state, and verification result at every checkpoint.
- Preserve all pre-existing user changes. Use a clean linked worktree or equivalent
  isolated checkout for baseline, build, installation, and clean-room comparisons.
- A prompt's `authorized_paths` is its complete mutation boundary. Discovery outside
  that boundary is read-only. Stop when a required correction would cross it.
- Repository rollback is a revert of the checkpoint commit in the isolated branch,
  followed by that prompt's pre-change verification. P10 defines separate recovery
  for non-Git systems.
- Every prompt writes append-only execution evidence and finishes with the witnessed
  QA protocol in `.claude/skills/qa-gate-codex-run`; `QA_ERROR` is unverified, never a
  pass.
