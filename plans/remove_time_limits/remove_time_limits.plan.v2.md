# Remove Governing Curriculum-Generation Time Limits — Implementation Plan v2

## Status and correction

This plan supersedes v1 for execution. V1 incorrectly treated any pre-existing gate
failure other than `FR-P0-CLEAN` as a reason to stop. That rule blocked the requested
work because the repository already had an unrelated `FR-P0-NOSTALE` failure.

V2 uses regression-based acceptance:

- capture every pre-existing failure before editing;
- do not repair unrelated baseline failures;
- do not let them block the time-limit change;
- require the implementation to introduce no new failure or blocked gate and not
  worsen any existing failure;
- report retained baseline failures honestly rather than calling them passes.

The known `FR-P0-NOSTALE` failure and dirty-worktree `FR-P0-CLEAN` failure are
documented baseline conditions, not blockers for this task.

## Goal

Remove active lab-, phase/state-, run-, and outer implementation-task duration limits
while preserving non-time budgets, elapsed-time telemetry, infrastructure safety
timeouts, learner-facing duration guidance, historical artifacts, and all unrelated
user work.

Two independent 36,000-second rules are in scope:

1. `policy/limits.v1.yaml` — `per_run.max_seconds` for a curriculum meta run.
2. `plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md` — the
   outer implementation-task wall-time envelope.

## Exact implementation scope

Edit only these five existing files:

1. `policy/limits.v1.yaml`
   - Remove `per_lab.max_seconds` and `--max-lab-seconds`.
   - Remove the duration-only `per_phase.timeout_seconds` group and
     `--phase-timeout-seconds`.
   - Remove `per_run.max_seconds` and `--max-run-seconds`.
   - Preserve all remaining count, storage, concurrency, retry, and convergence limits.
2. `schemas/limits.schema.v1.json`
   - Remove `per_phase` from the top-level required list.
   - Remove the `per_phase` property block.
   - Preserve generic `per_lab` and `per_run` maps for non-time limits.
3. `runtime/run_curriculum.py`
   - Stop assuming `per_phase` exists when generating policy-backed CLI options.
   - Preserve generation of every remaining non-time option.
4. `plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md`
   - Remove the outer 36,000-second task envelope.
   - Remove `per-state` from the sentence describing binding limits.
   - Preserve prompt versions v1–v5 as history.
5. `tests/gates/fr_p4_policy_schemas.py`
   - Preserve generic numeric/flag validation.
   - Add a semantic `forbidden-time-limit` detector for duration-governing policy
     keys and flags, including renamed equivalents.

Add only these two implementation test files:

6. `tests/fixtures/time_limit_present.reject.yaml`
   - Contain a renamed duration cap such as `per_run.wall_clock_minutes` with
     `--deadline-minutes`.
   - Prove the semantic detector bites with `forbidden-time-limit`.
7. `tests/runtime/test_run_curriculum.py`
   - Prove parser construction succeeds without `per_phase`.
   - Prove all three removed flags are absent from help/actions and rejected with
     `SystemExit(2)`.
   - Prove representative non-time flags/defaults remain for every retained group.
   - Use mocked clocks to cross 900, 5,400, and 36,000 seconds and still reach
     simulated `ACCEPTED`.
   - Prove checkpoint `elapsed_seconds` remains numeric.

No eighth implementation path is authorized.

## Explicit preservation boundary

Do not change:

- `runtime/session_bridge.py`, including its 45-second network timeout and existing
  stale references;
- `runtime/capability_cycle.py`, including its 300-second subprocess timeout;
- `curricula/arduino_kit/teacher_framework.md`, including the 3–5 minute learner
  estimate;
- elapsed-time telemetry in runtime and policy files;
- generic non-time contracts in `policy/controller.v1.yaml`,
  `policy/checks.v1.yaml`, and `meta_prompt/curriculum.prompt.v1.md`;
- historical prompts v1–v5, deprecated files, research, and legacy runtime artifacts.

## Worktree protection

Before editing, record:

- `git status --porcelain=v1 --untracked-files=all` and its NUL-delimited form;
- cached and working-tree diffs for the seven authorized paths;
- byte copies and SHA-256 hashes of the five existing targets and three preservation
  files;
- whether the two new tests are absent;
- stdout, stderr, return code, emitted result JSON, counts, and per-gate status for all
  baseline checks.

Never stage, stash, commit, reset, restore, checkout, clean, delete, hide, or overwrite
user work. Use `apply_patch` for repository edits. Compare against the captured
working-tree state rather than only `HEAD`.

## Baseline-failure policy

Run before and after implementation:

```sh
python3 tests/gates/fr_p4_policy_schemas.py --check validate
python3 tests/gates/fr_p4_policy_schemas.py --check agreement
./tests/run_gates.sh 4
./tests/run_gates.sh 5
python3 -m unittest discover -s tests/runtime -v
python3 tests/check_meta_prompt.py
```

Pre-existing failures do not block editing when they are captured accurately and do
not prevent the task-specific checks from running. In particular:

- retain `FR-P0-NOSTALE` as `EXPECTED_PREEXISTING_FAILURE` when its stale-reference
  findings are unchanged or improved;
- retain `FR-P0-CLEAN` as `EXPECTED_DIRTY_BASELINE`, binding its result to a fresh full
  porcelain status capture and the expected authorized task-path additions;
- never relabel either gate as passing;
- require every newly added task-specific test and changed phase-4 agreement check to
  pass;
- after editing, reject any new `FAIL`/`BLOCKED`, any worsening of a baseline failure,
  or any unexplained dirty path.

A genuine stop condition is limited to a collision with user work, inability to apply
the seven-file change safely, ambiguous/stale test evidence, a new or worsened failure
caused by the task, or a required repair outside the allowlist. An unrelated baseline
failure is not itself a stop condition.

## Ordered implementation

1. Capture worktree, file, hash, and test baselines in a task-owned temporary evidence
   directory.
2. Classify the known `FR-P0-NOSTALE` and `FR-P0-CLEAN` failures as retained baseline
   conditions and continue.
3. Inventory active duration governance and allowed incidental/safety/history hits.
4. Edit policy, schema, runtime parser iteration, and current v6 prompt.
5. Add the semantic gate detector, renamed-cap fixture, and runtime regression tests.
6. Run direct checks, runtime tests, prompt validation, phase 4/5 suites, a supported
   simulated curriculum run, retention checks, and the residual-duration inventory.
7. Repair only failures caused by the seven-file task delta and only within the
   allowlist.
8. Compare post-edit results gate-by-gate with the captured baseline. Require no new or
   worsened failure.
9. Write `plans/remove_time_limits/remove_time_limits.result.v2.md` and append one
   execution entry to `plans/remove_time_limits/plans.log.md`.

## Acceptance criteria

- The three governing policy duration entries and flags are absent.
- The schema validates without `per_phase`; all retained non-time limits still validate.
- The runtime parser exposes no removed flag and rejects each legacy spelling.
- The current v6 prompt contains neither active duration instruction.
- A renamed duration-cap fixture fails with `forbidden-time-limit` while ordinary
  non-time limits pass.
- Mocked threshold-crossing simulation accepts and numeric elapsed telemetry remains.
- The supported integration simulation reports `ACCEPTED` with
  `simulated-controller-only` coverage.
- Infrastructure timeouts, learner estimate, telemetry, history, and unrelated user
  work remain unchanged.
- Direct task-specific checks pass.
- Phase suites contain no new `FAIL`/`BLOCKED`; retained baseline failures are unchanged
  or improved and are reported as expected pre-existing conditions.
- Final task delta is exactly the five edited files and two new tests.

## Result policy

The result must distinguish:

- `PASS_WITH_BASELINE_FAILURES` — the time-limit objective and all task-specific tests
  pass, with only unchanged/improved documented pre-existing failures remaining;
- `PASS` — all task checks and full suites pass;
- `FAIL` — the task introduces or cannot repair an in-scope regression;
- `BLOCKED` — a genuine worktree collision, evidence ambiguity, or required out-of-scope
  repair prevents safe completion.

Known unchanged `FR-P0-NOSTALE` and `FR-P0-CLEAN` results are compatible with
`PASS_WITH_BASELINE_FAILURES`.

