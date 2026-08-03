# Execute Remove Governing Curriculum-Generation Time Limits — Prompt v1

You are the implementation executor. Work only in `/Users/filipepinto/Projects/curriculum_builder`.

Read this prompt completely before acting. Also read the approved plan at
`plans/remove_time_limits/remove_time_limits.plan.v1.md` and the two final plan-QA
reports at `plans/remove_time_limits/qa/plan_qa.contracts.v3.md` and
`plans/remove_time_limits/qa/plan_qa.tests.v3.md`. This prompt is the execution
contract. If repository evidence conflicts with it in a way that cannot be resolved
inside the seven-file implementation allowlist, stop and report the conflict; do not
broaden scope.

## GOAL

Remove active lab-, phase/state-, run-, and outer implementation-task duration
governance while retaining non-time budgets, elapsed-time telemetry,
infrastructure-operation safety timeouts, learner-facing duration guidance, and
historical records.

Two separate 36,000-second contracts must be removed and proved absent independently:

1. `policy/limits.v1.yaml` has the active `per_run.max_seconds` policy cap for a meta
   run.
2. `plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md` has an
   outer wall-time envelope for the complete implementation/development task, not an
   individual L01 run.

### Exact implementation allowlist

Edit only these five existing implementation files:

1. `policy/limits.v1.yaml`
   - Delete `per_lab.max_seconds`, including its value, flag, and rationale.
   - Delete the complete duration-only `per_phase.timeout_seconds` group.
   - Delete `per_run.max_seconds`, including its value, flag, and rationale.
   - Preserve all non-time `per_lab`, `per_run`, `convergence`, and `retry` entries and
     the generic `behaviour_on_limit` contract.
2. `schemas/limits.schema.v1.json`
   - Remove `per_phase` from the required top-level groups.
   - Remove the `per_phase` property block.
   - Retain the generic `per_lab` and `per_run` entry maps because they validate
     remaining non-time limits.
3. `runtime/run_curriculum.py`
   - Adapt only the policy-group iteration so parser construction does not index the
     removed `per_phase` group and continues to expose supported/present non-time
     policy groups.
   - Do not retain or add aliases for the removed duration flags.
4. `plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md`
   - Remove the outer 36,000-second complete-development-task bullet.
   - Remove `per-state` from the sentence saying active limits remain binding, leaving
     the valid per-lab non-time, retry, and convergence classes binding.
   - Do not edit prompt v1 through v5.
5. `tests/gates/fr_p4_policy_schemas.py`
   - Preserve generic numeric/flag validation for remaining limits.
   - Add a semantic duration-governance detector that inspects policy group/key and
     flag semantics. It must reject the three legacy paths/flags and renamed duration
     keys/flags such as `per_run.wall_clock_minutes` / `--deadline-minutes`.
   - Do not scan general prose, where incidental time remains valid.
   - Emit the stable error id `forbidden-time-limit` and wire the new reject fixture
     into `FR-P4-AGREEMENT`.

Add only these two implementation test files; first record whether each is absent:

6. `tests/fixtures/time_limit_present.reject.yaml`
   - Use a semantically renamed cap such as `per_run.wall_clock_minutes` with
     `--deadline-minutes`, not just a legacy spelling.
   - Expect `forbidden-time-limit`.
   - Retain ordinary non-time entries so the fixture does not imply that all limits
     are forbidden.
7. `tests/runtime/test_run_curriculum.py`
   - Construct `parser_for(CurriculumRuntime(ENGINE))` after `per_phase` is removed.
   - Prove `--max-lab-seconds`, `--phase-timeout-seconds`, and `--max-run-seconds` are
     absent from parser option strings and help and that each is rejected by
     `parse_args` with argparse `SystemExit(2)`.
   - Prove at least one retained option and policy default from each of `per_lab`,
     `per_run`, `convergence`, and `retry`.
   - Mock both monotonic clocks used by the simulation/checkpoint path so elapsed
     values deterministically cross 900, 5,400, and 36,000 seconds without waiting.
     Require normal `ACCEPTED` termination and no duration-limit failure.
   - Inspect generated checkpoint JSON and require numeric `elapsed_seconds` that
     reflects mocked progression.

The mandatory execution evidence files are not implementation-scope expansion:

- Write the final result to
  `plans/remove_time_limits/remove_time_limits.result.v1.md` only after the final
  phase-suite/status binding checks, so it cannot contaminate their seven-path union.
- Append one execution activity entry to
  `plans/remove_time_limits/plans.log.md`; never rewrite existing history.

Do not edit the approved plan, this prompt, any QA report, or any other repository
file. Repository-generated output below `outputs/` may be created only for the required
simulation and must use a fresh task-owned path. Do not overwrite an existing output.

### Required preservation boundary

Leave these files and facts unchanged from the captured working-tree baseline:

- `policy/controller.v1.yaml`: generic code ownership of operational timeouts,
  elapsed-time telemetry, and the pointer to remaining non-time limit flags.
- `policy/checks.v1.yaml` and `meta_prompt/curriculum.prompt.v1.md`: generic non-time
  limit/convergence contracts.
- `runtime/session_bridge.py`: `urlopen(request, timeout=45)` network safety timeout.
- `runtime/capability_cycle.py`: `timeout=300` subprocess safety timeout and telemetry.
- `runtime/checkpoint.py`, `runtime/finalize_evidence.py`,
  `policy/controller.v1.yaml`, and `policy/routes.v1.yaml`: elapsed-time observation.
- `curricula/arduino_kit/teacher_framework.md`: learner-facing “3–5 minute build
  estimate.”
- `plans/simplification/prompt/implement_curriculum_runtime.prompt.v1.md` through
  `v5.md`: superseded history, including expected historical duration text.
- `plans/legacy_v3/run_curriculum.v3.py`: unimported historical artifact.

Do not erase valid occurrences of time in telemetry, safety controls, learner guidance,
negative fixtures, or history merely to make a text search empty.

### Non-negotiable worktree rules

- Preserve every pre-existing staged, unstaged, and untracked user change.
- Never stage, stash, commit, revert, reset, restore, checkout, clean, delete, or hide
  user work. Do not alter the index. In particular, do not use `git add`, `git stash`,
  `git commit`, `git revert`, `git reset`, `git restore`, `git checkout`, or
  `git clean`.
- Use `apply_patch` for repository source/test/prompt edits. Do not perform broad
  formatting or generated rewrites.
- Compare against the captured working-tree baseline, not only `HEAD` or the index.
- If a target cannot be changed without overwriting pre-existing work, stop and ask
  for direction. Do not manufacture a clean gate result.

## TESTS

All evidence must be captured in a task-owned directory created with `mktemp -d`.
Record that directory in the result artifact. Save stdout, stderr, and the numeric
return code for every pre- and post-edit command. Do not mask a return code with an
unparsed `|| true`.

### A. Mandatory pre-edit baseline

Before the first implementation edit:

1. Capture complete human- and machine-readable status:

   ```sh
   git status --porcelain=v1 --untracked-files=all > "$EVIDENCE_DIR/status.before.txt"
   git status --porcelain=v1 -z --untracked-files=all > "$EVIDENCE_DIR/status.before.z"
   ```

2. Capture both index and working-tree diffs for all seven authorized paths:

   ```sh
   git diff --cached -- policy/limits.v1.yaml schemas/limits.schema.v1.json runtime/run_curriculum.py plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md tests/gates/fr_p4_policy_schemas.py tests/fixtures/time_limit_present.reject.yaml tests/runtime/test_run_curriculum.py
   git diff -- policy/limits.v1.yaml schemas/limits.schema.v1.json runtime/run_curriculum.py plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md tests/gates/fr_p4_policy_schemas.py tests/fixtures/time_limit_present.reject.yaml tests/runtime/test_run_curriculum.py
   ```

   Save both outputs. Do not change the index.

3. Copy each existing authorized target and these three preservation files into the
   evidence directory, preserving relative identity, and record SHA-256 hashes of the
   copies:

   - `runtime/session_bridge.py`
   - `runtime/capability_cycle.py`
   - `curricula/arduino_kit/teacher_framework.md`

   Explicitly record absence for each new test file if absent. If either already
   exists, treat it as user work and stop rather than overwrite it unless its complete
   current contents are demonstrably this task's intended baseline and can be safely
   preserved.

4. Run the six native commands below before edits, capture outputs/return codes, and
   apply all direct-check and phase-suite rules in sections B and C:

   ```sh
   python3 tests/gates/fr_p4_policy_schemas.py --check validate
   python3 tests/gates/fr_p4_policy_schemas.py --check agreement
   ./tests/run_gates.sh 4
   ./tests/run_gates.sh 5
   python3 -m unittest discover -s tests/runtime -v
   python3 tests/check_meta_prompt.py
   ```

5. For each phase suite, extract the exact `results:` path emitted by that invocation,
   reject missing/ambiguous paths, copy that exact JSON into the evidence directory,
   parse its `counts` and every gate status, and retain it as the gate-by-gate baseline.

Stop before editing if either direct phase-4 check, the runtime unittest suite, or the
meta-prompt check is nonzero. Also stop if a phase suite has any pre-existing failure
or block other than the narrowly permitted sole `FR-P0-CLEAN` failure in section C.
Do not broaden scope to repair a baseline blocker.

### B. Direct post-edit checks

After implementation, rerun and require exit 0 for:

```sh
python3 tests/gates/fr_p4_policy_schemas.py --check validate
python3 tests/gates/fr_p4_policy_schemas.py --check agreement
python3 -m unittest discover -s tests/runtime -v
python3 tests/check_meta_prompt.py
```

The runtime test module is the executable authority for parser construction, all three
legacy-flag absences/rejections, retained options/defaults in all four remaining groups,
crossing all former thresholds, normal acceptance, and numeric elapsed telemetry.

### C. Cumulative phase suites and the sole dirty-worktree waiver

Run `./tests/run_gates.sh 4` and `./tests/run_gates.sh 5` after implementation. For
each run, archive stdout/stderr/return code and the exact emitted result JSON.

Accept suite exit 0 only if parsed JSON has `counts.FAIL == 0` and
`counts.BLOCKED == 0`.

Accept suite exit 1 only if every condition below is machine-checked:

1. The exact JSON emitted by that invocation, not a stale result file, is parsed.
2. `counts.FAIL == 1`, `counts.BLOCKED == 0`, `FR-P0-CLEAN` is the sole `FAIL`, and
   every other activated gate is `PASS`.
3. Post-edit per-gate statuses have no regression from that phase's captured pre-edit
   result.
4. Immediately with the suite result, capture plain `git status --porcelain`
   byte-for-byte, including its final newline behavior. Inspect the current
   `FR-P0-CLEAN` implementation and runner digest function rather than assuming their
   behavior. In the repository version reviewed for this prompt, the gate runs plain
   `git status --porcelain`, the runner computes
   `sha256(stdout.encode("utf-8")).hexdigest()[:16]`, and the JSON field is
   `FR-P0-CLEAN.stdout_digest`. If that algorithm and stdout source remain
   discoverable, recompute the digest from the separately captured full plain-status
   stream and require exact equality with the JSON digest.
5. Independently capture a fresh
   `git status --porcelain=v1 -z --untracked-files=all` stream and parse its complete
   NUL-delimited records. Compare the normalized full dirty-path set for exact equality
   with: captured pre-edit dirty-path set union the seven authorized implementation
   paths. Handle rename/copy records correctly; do not parse the gate's human-readable
   `detail`, which truncates after 20 entries. Set equality, not prefix/subset equality,
   is required, so truncation cannot hide paths.

If the exact digest algorithm or the gate's stdout source is no longer discoverable,
do not claim digest equivalence. Record that fact and require the full plain status plus
fresh NUL-delimited exact path-set verification; the emitted JSON may then establish
only sole-failure identity/counts, while the full captures establish status/path scope.

Record the sole allowed failure as `EXPECTED_DIRTY_BASELINE`, never `PASS`.
Any suite exit greater than 1, any other `FAIL`, any `BLOCKED`, any result-path
ambiguity, any digest mismatch when digest equivalence is claimed, any path-set
mismatch, or any gate regression blocks acceptance.

### D. Supported simulation and telemetry

Use a unique, non-existing path under the required `outputs/` boundary; do not
overwrite any output:

```sh
python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit --test-simulated-all --output-root outputs/remove-time-limits-acceptance
```

If that literal path exists, choose a fresh task-specific sibling and record it.
Require JSON `terminal_state == "ACCEPTED"` and
`coverage == "simulated-controller-only"`. Inspect every generated
`checkpoints/*.json` and require numeric `elapsed_seconds`. This is simulated
controller coverage, never evidence of live generated curriculum. Preserve the output
or remove only the task-created output after its evidence is safely archived and only
if needed to maintain the scoped status set.

### E. Retention checks

Each command must independently find its named line and exit 0:

```sh
rg -n -F 'urlopen(request, timeout=45)' runtime/session_bridge.py
rg -n -F 'timeout=300' runtime/capability_cycle.py
rg -n -F '3–5 minute build estimate' curricula/arduino_kit/teacher_framework.md
rg -n -F 'elapsed_seconds' runtime/checkpoint.py
rg -n -F 'elapsed_seconds' runtime/finalize_evidence.py
rg -n -F 'elapsed time' policy/routes.v1.yaml
rg -n -F 'elapsed time' policy/controller.v1.yaml
```

Compare `runtime/session_bridge.py`, `runtime/capability_cycle.py`, and
`curricula/arduino_kit/teacher_framework.md` byte-for-byte and by SHA-256 against their
captured pre-edit copies. Require no task delta.

### F. Residual-duration inventory

Run and archive:

```sh
rg -n -i --glob '!plans/remove_time_limits/qa/**' 'max_seconds|timeout_seconds|max-lab-seconds|phase-timeout-seconds|max-run-seconds|36,000|36000|5,400|5400|\b900\b|wall[- ]?clock|wall time|per[- ]state|deadline|timeout|[0-9][0-9,]*[ -]?(seconds?|minutes?|hours?)' policy schemas runtime meta_prompt plans/simplification tests curricula
```

Classify every hit in the result artifact as exactly one of: forbidden active
governance (failure), allowed elapsed telemetry, allowed infrastructure safety timeout,
allowed learner-facing estimate, allowed non-time limit terminology, allowed
negative/reject fixture, or superseded/history. The negative-fixture category is
permitted only for the deliberate renamed-cap data in
`tests/fixtures/time_limit_present.reject.yaml` and corresponding detector/test
assertion in `tests/gates/fr_p4_policy_schemas.py`. An equivalent hit in active policy,
schema, runtime, or current prompt code is failure. Verify v6 has neither active
duration instruction and v1-v5 remain unchanged history.

### G. Final diff and baseline audit

Before writing the result artifact or appending the execution log, run and archive:

```sh
git diff --check
git diff --cached -- policy/limits.v1.yaml schemas/limits.schema.v1.json runtime/run_curriculum.py plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md tests/gates/fr_p4_policy_schemas.py tests/fixtures/time_limit_present.reject.yaml tests/runtime/test_run_curriculum.py
git diff -- policy/limits.v1.yaml schemas/limits.schema.v1.json runtime/run_curriculum.py plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md tests/gates/fr_p4_policy_schemas.py tests/fixtures/time_limit_present.reject.yaml tests/runtime/test_run_curriculum.py
git status --porcelain=v1 --untracked-files=all
```

Require `git diff --check` exit 0. Compare every authorized file to its recorded
working-tree baseline to isolate this task's implementation delta. Re-run the cached
diff and prove pre-existing staged content remains represented and the index was not
changed. The implementation delta must be exactly the five existing edits and two new
tests, with no unexplained path, deletion, staging change, or formatting churn.

After all checks are complete, write the required result and append the execution log.
The result file is an expected evidence artifact outside the seven implementation
paths; because it is created after phase/status binding, do not rerun a phase suite and
then pretend the prior seven-path status union included it. The existing untracked
`plans.log.md` path should already be part of the captured dirty baseline; appending to
it must not be mistaken for an implementation edit.

## LOOP

Execute the following loop without imposing a time limit:

1. **Orient and protect.** Read the plan/final QA reports and the relevant repository
   code. Create the evidence directory, capture status/diffs/copies/hashes, confirm the
   two new test paths' baseline state, and run/archive the complete pre-edit test
   baseline.
2. **Stop on a bad baseline.** If any pre-edit stop condition in TESTS A/C holds,
   write a blocked result and append a blocked execution log entry without editing the
   seven implementation files.
3. **Inventory.** Run the broad residual search and classify active current contracts,
   superseded history, telemetry, infrastructure safety timeouts, learner guidance,
   non-time limits, and the planned negative fixture.
4. **Edit contracts narrowly.** Edit policy, schema, runtime parser iteration, and the
   current v6 prompt in that order. Immediately parse/validate policy/schema contracts.
5. **Add biting tests and gate.** Implement the semantic detector, renamed-duration
   reject fixture, and runtime parser/threshold/telemetry tests. Do not weaken generic
   numeric/flag checks.
6. **Test.** Run the direct post-edit checks, both cumulative suites with exact JSON
   parsing/status binding, the supported simulation, retention assertions, residual
   inventory, and final diff/baseline audit.
7. **Repair only in scope.** If a test fails because of the task delta, diagnose it and
   patch only the seven authorized implementation files, then rerun the affected test
   and the complete post-edit acceptance set. Preserve all user work. Repeat until all
   acceptance conditions hold or an explicit stop condition is reached.
8. **Stop rather than expand.** Stop if repair requires any eighth implementation file,
   overwriting pre-existing work, changing the index, weakening a gate, hiding dirt,
   accepting an ambiguous/stale phase result, or claiming evidence that was not
   established. Do not revert partial task work; document the exact blocker and current
   safe state.
9. **Report.** Write
   `plans/remove_time_limits/remove_time_limits.result.v1.md` with:
   - final verdict: `PASS`, `FAIL`, or `BLOCKED`;
   - evidence-directory path;
   - exact implementation delta and confirmation that only seven implementation paths
     changed;
   - pre/post command return codes and archived-output locations;
   - exact phase JSON paths/copies, counts, every non-pass status, gate-by-gate
     regression comparison, `EXPECTED_DIRTY_BASELINE` classification where applicable,
     plain-status digest binding result and algorithm (or an explicit statement that
     equivalence was not claimable), and NUL-delimited exact path-set result;
   - parser/legacy-option/retained-default/mocked-threshold/telemetry results;
   - supported simulation terminal state, coverage label, and checkpoint result;
   - preservation hashes and retention assertions;
   - every residual-search hit classification, including current-vs-history treatment;
   - cached/working-tree baseline audit and explicit confirmation that no stage, stash,
     commit, revert, reset, restore, checkout, clean, or unrelated edit occurred;
   - any unresolved issue without overstating acceptance.
10. **Log.** Append, without rewriting history, one concise execution activity entry to
    `plans/remove_time_limits/plans.log.md` naming the executor, verdict, seven-file
    implementation scope, tests run, expected dirty-gate disposition, result-artifact
    path, and preservation of user work.

Completion requires every GOAL invariant and TEST acceptance condition. A successful
ordinary simulation is not a substitute for the deterministic parser and mocked-clock
tests, and an expected cleanliness failure is never relabeled as a passing gate.
