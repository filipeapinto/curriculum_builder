# Execute Removal of Governing Curriculum Time Limits — Prompt v2

Work in `/Users/filipepinto/Projects/curriculum_builder`.

Read this prompt and
`plans/remove_time_limits/remove_time_limits.plan.v2.md` completely before editing.
V2 supersedes the v1 execution prompt. Do not repeat planning or stop merely because
the repository retains a documented unrelated baseline failure.

## GOAL

Remove all active duration governance for curriculum labs, controller phases/states,
complete curriculum runs, and the current outer implementation task. Preserve
non-time budgets, elapsed-time telemetry, infrastructure safety timeouts,
learner-facing time guidance, historical files, and every unrelated user change.

### Authorized implementation delta

Edit exactly these five existing files:

1. `policy/limits.v1.yaml`
   - Delete `per_lab.max_seconds` / `--max-lab-seconds`.
   - Delete all of the duration-only `per_phase.timeout_seconds` group /
     `--phase-timeout-seconds`.
   - Delete `per_run.max_seconds` / `--max-run-seconds`.
   - Preserve every non-time limit and generic limit behavior.
2. `schemas/limits.schema.v1.json`
   - Delete top-level required `per_phase` and its property block.
   - Preserve generic `per_lab` and `per_run` entry schemas.
3. `runtime/run_curriculum.py`
   - Adapt the policy-group iteration so it does not require `per_phase` and still
     exposes every remaining policy-backed option.
4. `plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md`
   - Delete the outer 36,000-second implementation-task envelope.
   - Remove `per-state` from the binding-limits sentence while preserving valid
     per-lab non-time, retry, and convergence limits.
5. `tests/gates/fr_p4_policy_schemas.py`
   - Keep generic value/flag validation.
   - Add semantic rejection of duration-governing policy keys/flags with stable error
     id `forbidden-time-limit`.

Add exactly these two tests:

6. `tests/fixtures/time_limit_present.reject.yaml`
   - Use a renamed cap such as `per_run.wall_clock_minutes` /
     `--deadline-minutes` and prove the semantic detector bites.
7. `tests/runtime/test_run_curriculum.py`
   - Test parser construction without `per_phase`.
   - Test absence/help omission and `SystemExit(2)` rejection for all three legacy
     flags.
   - Test representative retained defaults from `per_lab`, `per_run`, `convergence`,
     and `retry`.
   - Mock the relevant monotonic clocks so simulated elapsed time crosses 900, 5,400,
     and 36,000 seconds, reaches `ACCEPTED`, and retains numeric checkpoint
     `elapsed_seconds`.

Do not edit any eighth implementation file. Write final evidence to
`plans/remove_time_limits/remove_time_limits.result.v2.md` and append one entry to
`plans/remove_time_limits/plans.log.md` only after final gate/status capture.

### Required preservation

Leave unchanged:

- `runtime/session_bridge.py`, including `timeout=45` and its pre-existing stale
  `assets/` references;
- `runtime/capability_cycle.py`, including `timeout=300`;
- `curricula/arduino_kit/teacher_framework.md`, including the 3–5 minute estimate;
- elapsed-time telemetry and generic non-time contracts;
- current user changes and the Git index;
- prompt v1–v5 history, legacy, deprecated, archive, and research files.

Never stage, stash, commit, reset, restore, checkout, clean, delete, hide, or overwrite
user work. Use `apply_patch` for repository edits. Do not weaken or remove an unrelated
gate to obtain a pass.

## TESTS

### 1. Capture the pre-edit baseline

Create a task-owned evidence directory with `mktemp -d`. Record its path. Before any
implementation edit, save:

- plain and NUL-delimited `git status --porcelain=v1 --untracked-files=all`;
- cached and working-tree diffs for all seven authorized paths;
- byte copies and SHA-256 hashes of the five existing targets plus
  `runtime/session_bridge.py`, `runtime/capability_cycle.py`, and
  `curricula/arduino_kit/teacher_framework.md`;
- explicit presence/absence and contents of the two new test paths;
- stdout, stderr, numeric return code, and exact emitted phase-result JSON for:

```sh
python3 tests/gates/fr_p4_policy_schemas.py --check validate
python3 tests/gates/fr_p4_policy_schemas.py --check agreement
./tests/run_gates.sh 4
./tests/run_gates.sh 5
python3 -m unittest discover -s tests/runtime -v
python3 tests/check_meta_prompt.py
```

Parse each baseline result by gate id, status, count, detail/digest, and finding set.

### 2. Baseline failures are regression references, not blockers

Continue when baseline commands contain unrelated pre-existing failures. Specifically:

- classify `FR-P0-NOSTALE` as `EXPECTED_PREEXISTING_FAILURE`; record its complete
  stale-reference finding set and do not repair it;
- classify `FR-P0-CLEAN` as `EXPECTED_DIRTY_BASELINE`; bind it to separately captured
  full porcelain status and a fresh NUL-delimited normalized dirty-path set;
- record any other pre-existing non-pass result and continue unless it prevents the
  seven authorized files from being edited or prevents task-specific tests from
  executing at all.

Do not label a failing baseline gate as passing. The post-edit requirement is: no new
`FAIL`/`BLOCKED`, no worsening of any captured failure, and no unexplained dirty path.

Stop before editing only for a genuine collision with user work, missing/ambiguous
baseline evidence that cannot be recaptured, an existing new-test path that cannot be
safely preserved, or inability to make the authorized change without an eighth file.

### 3. Required post-edit checks

Rerun and archive all six baseline commands. Also run:

```sh
python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit --test-simulated-all --output-root outputs/remove-time-limits-v2-acceptance
rg -n -F 'urlopen(request, timeout=45)' runtime/session_bridge.py
rg -n -F 'timeout=300' runtime/capability_cycle.py
rg -n -F '3–5 minute build estimate' curricula/arduino_kit/teacher_framework.md
rg -n -F 'elapsed_seconds' runtime/checkpoint.py runtime/finalize_evidence.py
rg -n -F 'elapsed time' policy/routes.v1.yaml policy/controller.v1.yaml
git diff --check
```

Use a fresh simulation output sibling if the literal output path exists. Require
`terminal_state == "ACCEPTED"`, `coverage == "simulated-controller-only"`, and numeric
`elapsed_seconds` in every generated checkpoint.

Run and archive this residual inventory:

```sh
rg -n -i --glob '!plans/remove_time_limits/qa/**' 'max_seconds|timeout_seconds|max-lab-seconds|phase-timeout-seconds|max-run-seconds|36,000|36000|5,400|5400|\b900\b|wall[- ]?clock|wall time|per[- ]state|deadline|timeout|[0-9][0-9,]*[ -]?(seconds?|minutes?|hours?)' policy schemas runtime meta_prompt plans/simplification tests curricula
```

Classify each hit as forbidden active governance, elapsed telemetry, infrastructure
safety timeout, learner guidance, non-time terminology, deliberate negative fixture,
or superseded/history. Any governing hit in active policy/runtime/current prompt is a
failure; allowed incidental and historical hits remain.

### 4. Regression-based cumulative-gate acceptance

For each pre/post phase 4 and phase 5 invocation, use only the exact `results:` JSON
path emitted by that invocation. Reject missing, ambiguous, or stale JSON.

Post-edit acceptance requires:

1. Every gate that passed before still passes, except a gate may improve.
2. No new gate id has status `FAIL` or `BLOCKED`.
3. Every pre-existing `FAIL`/`BLOCKED` is unchanged or improved:
   - for `FR-P0-NOSTALE`, the stale-reference set must be identical or smaller and
     must contain no authorized task path introduced by this work;
   - for `FR-P0-CLEAN`, a changed digest/detail is expected because of authorized
     edits, but the complete dirty-path set must equal the pre-edit set union the seven
     authorized implementation paths, with no unexplained path;
   - for any other baseline failure, compare its machine-readable finding identity,
     severity/status, and detail/digest and require no worsening attributable to the
     task.
4. The direct changed checks (`validate`, `agreement`), all new runtime tests, and the
   meta-prompt check pass after editing. If a direct command had an unrelated baseline
   failure, its task-relevant assertions must still demonstrably pass and its
   pre-existing failure must not worsen.

Phase-suite process exit 1 is compatible with `PASS_WITH_BASELINE_FAILURES` when and
only when all non-pass results satisfy the comparison above. Never relabel those gates
as passing and never use an unparsed `|| true`.

### 5. Final scope audit

Before writing result/log evidence:

- compare the five edited files against their captured working-tree copies;
- confirm the two new tests were absent or safely preserved at baseline;
- prove the Git index/cached diffs are unchanged;
- parse fresh NUL-delimited status and account for every path;
- require the implementation delta to be exactly the five existing edits and two new
  tests;
- compare the three preservation files byte-for-byte and by SHA-256;
- require `git diff --check` to exit 0.

## LOOP

1. Read v2 plan/prompt and relevant repository files.
2. Capture complete file, index, status, hash, and test baselines.
3. Record pre-existing failures as regression references and continue; do not repeat
   the v1 mistake of treating unchanged `FR-P0-NOSTALE` as a blocker.
4. Inventory governing versus allowed time-related occurrences.
5. Apply the four product/contract edits, then add the semantic detector and two biting
   test artifacts, staying inside the seven-file allowlist.
6. Run all direct, runtime, prompt, cumulative, simulation, retention, residual, and
   diff checks.
7. If the task causes a failure, diagnose and repair it only within the seven
   authorized paths; rerun the affected check and full post-edit acceptance set.
8. Repeat until the time-limit objective passes with no new/worsened failure or a
   genuine stop condition occurs. Do not impose a time limit on this loop.
9. Write `plans/remove_time_limits/remove_time_limits.result.v2.md` containing:
   - `PASS`, `PASS_WITH_BASELINE_FAILURES`, `FAIL`, or `BLOCKED`;
   - evidence-directory path and exact implementation delta;
   - pre/post command return codes and emitted JSON paths;
   - gate-by-gate regression comparison and complete treatment of every retained
     baseline failure;
   - parser, removed-flag, retained-default, mocked-threshold, telemetry, simulation,
     retention, residual-inventory, status-path, digest, index, and diff evidence;
   - confirmation that no unrelated work or forbidden Git operation occurred.
10. Append one concise execution entry to `plans/remove_time_limits/plans.log.md`.

Completion is achieved when all time-limit acceptance criteria pass and the only
remaining non-pass gates, if any, are unchanged or improved pre-existing conditions.
Unrelated baseline failures are reported honestly but do not block completion.

