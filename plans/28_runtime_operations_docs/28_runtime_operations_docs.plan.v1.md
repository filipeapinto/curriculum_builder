# Runtime Operations Documentation — Implementation Plan v1

## Status and objective

Planning only; no implementation is authorized by this document's creation.

`docs/how_it_works.md` is the repository's only "how it works" document. It
is dated 2026-08-02, describes the earlier `meta_prompt/curriculum.prompt.v1.md`
contract design, states "the runtime controller, logger, renderer,
source-fetching run, and live model route... do not yet exist" and "zero
units have been generated," and never mentions `runtime/langgraph_factory` or
`runtime/run_curriculum.py`. No operator-facing runbook exists anywhere in the
repository: nothing documents how to invoke `runtime/run_curriculum.py`, what
configuration or subscription-driver prerequisites it needs, how to read its
evidence/receipt output, or how to diagnose and recover from a `BLOCKED` or
`NOT_AVAILABLE` outcome.

This plan replaces `docs/how_it_works.md` with an accurate description of the
LangGraph curriculum factory runtime, and adds an operations manual for
running it. It does not change any runtime code, policy, schema, or test —
only documentation under `docs/`. It does not resolve, reinterpret, or
second-guess Plan 27's terminal outcome; it consumes whatever that outcome
turns out to be.

**Hard prerequisite.** Plan 27
(`plans/27_langgraph_curriculum_factory_remediation`) must have reached a
terminal state before this plan's implementation prompt may write any
documentation describing runtime behavior as current or live. The runtime is
still under active, multi-round correction (`implementation.graph.v7.yaml` is
already the seventh revision of that graph); documentation written against an
unfinished target would misdescribe the system the moment the next
correction round lands, repeating exactly the failure this plan exists to
fix.

## Exact work

### 0. Fail-fast prerequisite check

`plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/`
has already been corrected across seven graph versions (`implementation.graph.v1.yaml`
through `.v7.yaml`, with v1–v6 moved to `deprecated/`), each superseding the
last after a real, evidenced defect — and each correction has moved
`result_pattern` to a new version-specific results directory
(`results/v6/` → `results/v7/`, etc.). There is no `CURRENT`/latest pointer
file in that package; nothing marks an older graph version's results as
stale once a newer version exists. A result file from a superseded version
can therefore sit on disk indefinitely still reading `PASSED`/`ACTIVATED`
even after that exact graph version has been corrected away. Do not trust a
version-pinned result path without first confirming that version is still
current.

Before any documentation write:

1. List `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v*.yaml`
   (files directly in that directory, not under `deprecated/`) and take the
   highest-numbered one as the current graph. If it is not
   `implementation.graph.v7.yaml`, stop: this plan's step 0 was written
   against v7's `result_pattern` and does not know the newer version's
   result path. Report the newer graph file found and do not proceed —
   re-scoping step 0 to the new version is a prerequisite fix to this plan
   itself, not something to improvise during implementation.
2. Read that graph file's own `result_pattern` field and confirm it resolves
   to `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/{node_id}.result.v1.json`
   (i.e. matches what step 1 expects). If it does not match, stop for the
   same reason as above.
3. Read `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N90_REQUIREMENTS_FINAL_AUDIT.result.v1.json`
   and confirm, in order:
   - the file exists;
   - `outcome` is `PASSED` (per `implementation.graph.v7.yaml`'s N90
     `allowed_results: [PASSED, BLOCKED]` — a `BLOCKED` outcome means Plan 27
     has not concluded and this plan must stop here);
   - `terminal_recommendation` is present and is exactly `"ACTIVATED"` or
     `"REMEDIATION_VERIFIED_NOT_ACTIVATED"` (the two terminals
     `plans/27_.../controller/run27_controller.py` accepts as a concluded
     audit; see `schemas/node_result.schema.v1.json`'s `terminal_recommendation`
     enum).

If any check in 1-3 fails, stop immediately. Do not write or edit any file
under `docs/`. Report which check failed and the exact file/field/value
observed. Re-running this check later, once Plan 27 has progressed (or once
this plan has been re-scoped to a newer graph version), is the correct next
action; there is no fallback documentation to write in the interim.

Immediately before the final documentation write in steps 1-2 (not only at
the start of implementation), repeat check 1 — confirm no newer
`implementation.graph.v*.yaml` has appeared since step 0 ran. If one has,
stop and discard any draft written so far rather than publishing it.

Record which of the two terminals was found — it determines the framing of
step 1 and step 2 below.

### 1. Rewrite `docs/how_it_works.md`

- If `terminal_recommendation` is `ACTIVATED`: rewrite the document to
  describe the current, live `runtime/langgraph_factory` architecture as the
  active system. Base every claim on the actual code and config at the time
  of writing — do not carry forward any wording from the old contract-based
  document that no longer applies. At minimum, cover:
  - the eight-job provider/role mapping and subscription-only routing
    (Claude generate/repair, Codex cross-family judge, no Gemini route, no
    billed API key, no fallback), sourced from `policy/routes.v1.yaml` and
    `policy/routing/model_registry.v1.yaml` as they exist at write time;
  - the per-unit execution flow implemented by
    `runtime/langgraph_factory/graph.py` / `unit_graph.py` (or whatever
    modules N40's integration-ownership work actually produced — verify
    against the repository, not against this plan's assumptions);
  - the evidence/persistence contract from `runtime/langgraph_factory/evidence.py`
    and `persistence.py` (or their actual post-N50 paths);
  - retire the "zero units generated" / "no runtime controller" framing and
    the old `meta_prompt/curriculum.prompt.v1.md`-centric description,
    moving it to `docs/deprecated/` per the existing convention in that
    directory (do not delete history).
- If `terminal_recommendation` is `REMEDIATION_VERIFIED_NOT_ACTIVATED`:
  rewrite the document to state plainly that the LangGraph runtime is
  implemented and independently verified but **not activated for production
  use**, name the specific reason recorded in the N90 result (e.g. which
  live-proof node reported `NOT_AVAILABLE` and why), and do not describe any
  runtime behavior as currently in live use. This mirrors the honesty
  requirement the graph itself enforces at its `REMEDIATION_VERIFIED_NOT_ACTIVATED`
  terminal guard — the documentation must not claim more than the system
  earned.
- Preserve the existing `## Where to read next` convention, updated to point
  at the real current files.

### 2. Write the operations manual

Create `docs/runtime_operations_manual.md` (or, if a more repository-idiomatic
location is found during implementation — e.g. alongside
`runtime/langgraph_factory/` — use that instead and record the choice in the
result file). Cover, sourced from the actual CLI and config at write time:

- exact invocation of `runtime/run_curriculum.py`: required flags, config
  file locations, and output-root conventions, verified by running
  `--help` (or reading its argument parser directly) rather than guessed;
- subscription-driver prerequisites (Claude Code / Codex CLI availability
  and authentication state) the CLI needs before a run will proceed past
  preflight;
- how to locate and read a run's evidence/receipt output — the on-disk shape
  produced by the evidence/persistence layer covered in step 1;
- how to interpret a `BLOCKED` or `NOT_AVAILABLE` result: where the
  triggering finding is recorded, and the documented recovery path (rerun,
  resume, or escalate) — do not invent a recovery procedure that isn't
  actually supported by the code; if none exists for a given failure mode,
  say so explicitly rather than omitting it.
- If `terminal_recommendation` is `REMEDIATION_VERIFIED_NOT_ACTIVATED`, state
  at the top of this manual that the procedures below describe a verified-but-
  not-activated system and must not be read as an invitation to run it in
  production.

### 3. Cross-link

Update `readme.md`'s `docs/how_it_works.md` reference and add a pointer to
the new operations manual, so a reader lands on both documents from the
repository root.

## Verification sequence

1. Confirm the step 0 prerequisite check was actually performed and its
   result (pass/stop) is recorded in the result file before checking
   anything else.
2. If stopped at step 0: confirm no file under `docs/` was created or
   modified, and that the result file states the exact blocking condition.
3. If proceeding: for every factual claim added to `docs/how_it_works.md`
   and the new operations manual about CLI flags, config, routing, or file
   paths, confirm it is grounded in a specific repository file (cite path)
   current at write time — not carried over from this plan or from
   `docs/how_it_works.md`'s prior (stale) revision.
4. Confirm `docs/how_it_works.md`'s superseded content is moved to
   `docs/deprecated/` per the existing convention, not deleted.
5. Confirm `readme.md` links resolve to real, existing paths.

## Acceptance criteria

- The implementation performed zero documentation writes if Plan 27 had not
  reached a terminal state at execution time, and said so plainly in the
  result file.
- If Plan 27 had reached `ACTIVATED`: `docs/how_it_works.md` describes the
  live LangGraph runtime, sourced from the repository as it existed at write
  time, and no longer claims zero units generated or a missing controller.
- If Plan 27 had reached `REMEDIATION_VERIFIED_NOT_ACTIVATED`: both documents
  state clearly, at the top, that the system is verified but not activated,
  and name the specific reason from the N90 result.
- `docs/runtime_operations_manual.md` (or its recorded alternate path) exists
  and covers CLI invocation, prerequisites, evidence reading, and
  BLOCKED/NOT_AVAILABLE recovery, each grounded in a cited repository path.
- `readme.md` links to both documents.
- No file outside `docs/` (and `readme.md`) was modified.

## Stop conditions and result

Stop on: the step 0 prerequisite failing (Plan 27 not concluded, or its
`execution_package_v2` graph has moved past v7); any factual claim about
runtime behavior that cannot be grounded in a specific, citable, current
repository file; or discovery that Plan 27's terminal state or current graph
version changed mid-implementation (the step-0 pre-final-write recheck
covers this — stop if it no longer matches what step 0 originally recorded).

Write `plans/28_runtime_operations_docs/28_runtime_operations_docs.result.v1.md`
recording: the step 0 outcome (pass/stop and why), the terminal state found,
every file created or modified with its path, and — if writing proceeded —
the specific repository paths each documented claim was grounded in. Append
the execution outcome to `plans/28_runtime_operations_docs/plans.log.md`.
