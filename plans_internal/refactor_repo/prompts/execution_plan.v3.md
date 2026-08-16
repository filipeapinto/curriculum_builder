# Curriculum Factory repository refactor — autonomous execution plan v3

Grounding specification:
`plans_internal/refactor_repo/refactor_repository.spec.v8.html`.

Run exactly one entrypoint:
`plans_internal/refactor_repo/prompts/RUN_repository_refactor.prompt.v1.yaml`.

That prompt is the controller. Do not manually start P00–P10 alongside it. It runs one
fresh `general-purpose` child pinned to `sonnet` at a time, waits for the child, applies
the full acceptance gate, publishes the successful checkpoint, and only then advances.

## Autonomous sequence

1. Establish or safely resume a clean linked worktree on
   `refactor/curriculum-factory-repository`. Preserve the user's original worktree.
2. Run `P00_inventory_baseline.prompt.v3.yaml` and require all tests, a valid closed
   journal, exact scope, and witnessed `QA_PASSED` from `qa-gate-codex-run`.
3. Stage exactly P00's accepted delta, create its local checkpoint commit, non-force
   push it to `origin`, and prove the remote branch SHA equals local `HEAD`.
4. Run and publish `P00A_post_inventory_decomposition.prompt.v3.yaml` through the same
   gate. P00A consumes the committed P00 inventory and creates the resolved manifest,
   resolved plan, and any inventory-required generated prompt versions.
5. Validate `prompts/resolved/prompt_manifest.resolved.v1.yaml`, compute its
   deterministic topological order, and execute every active prompt exactly once. A v3
   template is not executable unless that resolved manifest activates its exact version
   and mutation units.
6. After every successful active prompt, repeat the exact-delta commit, non-force push,
   and remote-SHA verification before invoking its successor. Stop immediately on any
   test, journal, scope, QA, commit, push, authentication, or SHA-verification failure.
7. Invoke P10 in resolved order, but do not perform its repository/check-out rename
   without P10's separate exact authorization. This request authorizes checkpoint
   commits and pushes only; it does not authorize the rename.
8. After all child checkpoints, run independent QA for the RUN closeout package. Once it
   passes, close the tracked ledger/journal, make the final RUN evidence commit, push it
   without force, verify the remote SHA read-only, and make no tracked write afterward.

## Per-prompt publication gate

A prompt is publishable only when all of these are true:

- every prompt-defined test passes with retained commands and outputs;
- its execution-log-v2 journal validates and has zero unclosed starts;
- its actual and staged deltas equal its resolved paths and mutation selectors;
- the sanctioned QA verifier exits 0 with witnessed `QA_PASSED`;
- no secret, unrelated change, successor change, or original-worktree change is staged.

The commit subject is `refactor(repo): complete <prompt-id>`. The commit records the
prompt path/version, QA session/artifact, test evidence, and previous checkpoint. Push
only with the non-force refspec
`HEAD:refs/heads/refactor/curriculum-factory-repository`, then compare the remote SHA to
local `HEAD`. A failed prompt is never committed or pushed.

## Inventory-derived boundaries

This plan intentionally does not freeze the final implementation prompt count or exact
production, consumer, and test mutation paths. Specification §8 requires those to be
derived after P00. P00A can activate, split, omit, or replace candidate templates, but
each generated prompt must conform to `schemas/prompt.schema.v4.json`, have exact
non-overlapping ownership, use the governed model selection, and pass independent prompt
QA before execution.

The candidate dependency topology remains:

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
| P08 | full clean-room release, CLI acceptance, combined codemod safety | P02S, P05, P06, P07 |
| P09 | evidence-supported test-tree organization | P02S, P08 |
| P10 | separately authorized external rename | P09 |

`pyproject.toml` remains solely owned by P01.
`.github/workflows/plan26-lock-drift.yml` remains solely owned by P09. P08 owns the
complete CLI and combined codemod-safety acceptance criteria. P00A resolves all other
ordered shared-path units before implementation.

## Recovery and stopping

On restart, reconcile the orchestration ledger, child journals and QA witnesses, local
commit graph, and GitHub branch SHA. Resume only a unique incomplete transition. Never
repeat a remotely verified child, skip an unpushed local checkpoint, reset, amend,
rewrite history, force push, or hide a failure.

A missing P10 rename authorization is a safe pause, not completion or failure. Any other
ambiguous/divergent state stops for operator review with the isolated evidence intact
and the last verified GitHub checkpoint unchanged.
