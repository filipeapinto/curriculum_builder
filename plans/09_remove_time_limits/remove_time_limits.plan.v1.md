# Remove Governing Curriculum-Generation Time Limits — Implementation Plan v1

## Outcome

Remove active lab-, phase/state-, run-, and outer implementation-task duration governance while preserving all non-time budgets, elapsed-time telemetry, infrastructure-operation safety timeouts, learner-facing duration guidance, and historical records.

Two independent 36,000-second contracts are in scope and must be verified separately:

- `policy/limits.v1.yaml:49–52` is the active `per_run.max_seconds` policy cap for a meta run.
- `plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md:117–122` is an outer wall-time envelope for the complete implementation/development task, explicitly not an individual L01 run.

## Exact active edit inventory

Line numbers are pre-change references observed on 2026-08-03; use the symbols as stable anchors if dirty-worktree edits move them.

### Existing files to edit

1. `policy/limits.v1.yaml`
   - Delete lines 29–32, `per_lab.max_seconds` (`5400`, `--max-lab-seconds`, 90-minute rationale).
   - Delete all of lines 38–42, the duration-only `per_phase.timeout_seconds` group (`900`, `--phase-timeout-seconds`, 15-minute rationale).
   - Delete lines 49–52, `per_run.max_seconds` (`36000`, `--max-run-seconds`, 10-hour rationale).
   - Retain every non-time `per_lab`, `per_run`, `convergence`, and `retry` entry and the generic `behaviour_on_limit` contract.
2. `schemas/limits.schema.v1.json`
   - Remove `per_phase` from the required top-level groups at lines 8–16.
   - Remove the `per_phase` property block at lines 60–86.
   - Retain the generic `per_lab` and `per_run` entry maps at lines 33–59 and 87–113 because they still validate non-time limits.
3. `runtime/run_curriculum.py`
   - Change parser group iteration at lines 30–32 so it does not index the deleted `per_phase` group and continues to create flags for the supported/present non-time policy groups.
   - Do not add spellings for the removed flags elsewhere. This file currently exposes duration flags only indirectly from policy and contains no duration enforcement path.
4. `plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md`
   - Remove the line 122 outer-development-task 36,000-second bullet, independently from the policy cap removal.
   - At lines 139–141, remove `per-state` from “The active per-lab, per-state, retry, and convergence limits remain binding inside each attempt,” leaving the valid per-lab non-time, retry, and convergence classes binding.
   - v6 is the current prompt. Do not edit v1–v5.
5. `tests/gates/fr_p4_policy_schemas.py`
   - Preserve lines 237–252 generic numeric/flag validation for remaining limits.
   - Add a semantic detector for duration-governing policy entries. It must inspect policy group/key and flag semantics, reject the three legacy paths/flags, and also reject renamed duration keys/flags such as `per_run.wall_clock_minutes` / `--deadline-minutes`. It must not scan general prose, where incidental time is valid.
   - Give the detector a stable error id such as `forbidden-time-limit` and wire a biting reject fixture into `FR-P4-AGREEMENT` near lines 286–328.

### New test files to add

1. `tests/fixtures/time_limit_present.reject.yaml`
   - Use a semantically renamed duration cap, for example `per_run.wall_clock_minutes` with `--deadline-minutes`, not merely one of the three old spellings.
   - Expect the stable `forbidden-time-limit` error so an implementation that checks only old names cannot pass.
   - Keep ordinary non-time entries in the fixture or an existing accepting policy path to prove the detector does not reject all limits.
2. `tests/runtime/test_run_curriculum.py`
   - Construct `parser_for(CurriculumRuntime(ENGINE))` after `per_phase` is gone and prove parser construction succeeds.
   - Prove `--max-lab-seconds`, `--phase-timeout-seconds`, and `--max-run-seconds` are absent from option strings/help and each is rejected by `parse_args` with argparse's unknown-argument `SystemExit`.
   - Prove representative non-time flags remain and use their policy defaults (at minimum one each from retained `per_lab`, `per_run`, `convergence`, and `retry` groups).
   - Mock both monotonic clocks used by the simulation/checkpoint path so deterministic elapsed values cross the former 900-, 5,400-, and 36,000-second thresholds without waiting. Assert the simulation reaches its normal `ACCEPTED` terminal state and does not emit a duration-limit failure.
   - Inspect generated checkpoint JSON and assert `elapsed_seconds` remains present, numeric, and reflects the mocked progression. This is simulated-controller coverage, not live generated-curriculum evidence.

## Explicitly unchanged and verified

Do not edit these files for this change:

- `policy/controller.v1.yaml`: retain line 18 generic code ownership of timeouts because infrastructure-operation timeouts remain; it names no lab/phase/run duration, default, or flag. Retain line 83 elapsed-time telemetry and line 151's pointer to remaining non-time limit flags.
- `policy/checks.v1.yaml`: retain lines 266–268 and 308–312, which govern non-time convergence.
- `meta_prompt/curriculum.prompt.v1.md`: retain line 56, lines 96–97, line 283, and lines 377–379 as the generic contract for remaining non-time limits.
- `runtime/session_bridge.py:130`: retain `urlopen(..., timeout=45)` as a network-request safety timeout.
- `runtime/capability_cycle.py:134`: retain `subprocess.run(..., timeout=300)` as an external-subprocess safety timeout; line 146 remains telemetry.
- `runtime/checkpoint.py:21–34`, `runtime/finalize_evidence.py:20,93`, `policy/controller.v1.yaml:83`, and `policy/routes.v1.yaml:128`: retain elapsed-time observation/reporting.
- `curricula/arduino_kit/teacher_framework.md:294`: retain the learner-facing “3–5 minute build estimate.”
- `plans/simplification/prompt/implement_curriculum_runtime.prompt.v1.md` through `v5.md`: retain as superseded history. v3–v5 contain historical 36,000-second text. `plans/simplification/prompt/migrate_external_run_evidence.prompt.v2.md:39–51` establishes v6 as current and older versions as history.
- `plans/legacy_v3/run_curriculum.v3.py`: retain as an unimported historical executable artifact, including its 60-second transport timeout.

If an implementation search reveals another file, classify it before editing. Add it to scope only when it actively defines, maps, exposes, or enforces a lab/phase/run/outer-workflow duration cap. Telemetry, network/subprocess safeguards, learner activities, and superseded history remain non-targets.

## Invariants and non-goals

- Active curriculum generation and its outer implementation workflow have no governing duration cap expressed in seconds, minutes, hours, wall-clock deadlines, or renamed equivalents.
- The removed legacy CLI flags fail closed as unknown arguments; they are not accepted and ignored.
- Non-time limits—model calls, revisions, images, storage, concurrency, retry, and convergence—remain numeric, flagged, schema-valid, and exposed through the CLI.
- Elapsed-time fields remain present and numeric. Observability is not enforcement.
- The 45-second request timeout, 300-second subprocess timeout, and 3–5 minute learner estimate remain byte-identical to the recorded baseline.
- No live generation claim is made: the executable behavioral proof is a deterministic simulated controller run.
- Do not edit research, deprecated, archived, legacy, or superseded files solely to erase historical durations.

## Dirty-worktree baseline and protection

Before any implementation edit:

1. Record the complete status, including staged and untracked entries:

   ```sh
   git status --porcelain=v1 --untracked-files=all > /tmp/remove_time_limits.status.before
   ```

2. Inspect both sides of every target baseline; plain `git diff` is insufficient because intended targets already include staged work:

   ```sh
   git diff --cached -- policy/limits.v1.yaml schemas/limits.schema.v1.json runtime/run_curriculum.py plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md tests/gates/fr_p4_policy_schemas.py tests/fixtures/time_limit_present.reject.yaml tests/runtime/test_run_curriculum.py
   git diff -- policy/limits.v1.yaml schemas/limits.schema.v1.json runtime/run_curriculum.py plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md tests/gates/fr_p4_policy_schemas.py tests/fixtures/time_limit_present.reject.yaml tests/runtime/test_run_curriculum.py
   ```

3. Create a task-owned temporary baseline directory with `mktemp -d`; copy each existing target and the three preservation files into it, and record `shasum -a 256` for those copies. Record absence explicitly for the two new test files. Do not modify the index.
4. Before the first edit, execute and record the complete verification baseline:
   - run the two direct phase-4 checks, both cumulative phase suites, the runtime unittest discovery, and the meta-prompt check using the exact commands in **Native gates and tests** below;
   - save each command's stdout/stderr and numeric return code in the task-owned baseline directory;
   - for each phase suite, read the exact `results:` path emitted on stdout, copy that JSON into the baseline directory, and record its per-gate statuses and `counts` object;
   - save `git status --porcelain=v1 -z --untracked-files=all` as the machine-readable dirty-path baseline in addition to the human-readable status file;
   - if a direct check, runtime suite, or prompt check is nonzero, or a phase suite has any baseline failure/block other than `FR-P0-CLEAN`, stop before editing and report the pre-existing blocker. Do not broaden scope to repair it.
5. During implementation, preserve pre-existing staged and unstaged hunks. If a target cannot be edited without overwriting another author's work, stop and request direction.
6. At completion, compare each file to its recorded working-tree baseline—not merely to `HEAD` or the index—to isolate the task delta. Re-run `git diff --cached` and confirm the pre-existing staged content remains represented. Confirm the final status contains no unexplained additions, deletions, staging changes, or unrelated formatting churn.

## Ordered implementation

1. Capture the staged/unstaged/untracked file baseline, preservation hashes, and pre-edit execution results for both direct checks, phase 4/5, runtime unittests, and the prompt check.
2. Parse and archive both pre-edit phase JSON results; establish the exact per-gate/count baseline and confirm any nonzero suite result is caused only by `FR-P0-CLEAN`.
3. Run the broad pre-edit search below; classify current v6, v1–v5 history, telemetry, safety timeouts, and learner estimates before changing anything.
4. Edit `policy/limits.v1.yaml`, then `schemas/limits.schema.v1.json`; parse/validate the contract immediately.
5. Adapt only `runtime/run_curriculum.py`'s policy-group iteration.
6. Remove both active duration instructions from v6: the outer 36,000-second envelope and the per-state-binding phrase.
7. Add the semantic forbidden-time detector and renamed-duration rejection fixture without weakening generic limit validation.
8. Add parser, legacy-flag rejection, retained-option/default, mocked-duration-crossing, and elapsed-telemetry runtime tests.
9. Re-run focused native gates, phase suites, runtime unittests, prompt validation, the exact simulation, retention assertions, broad residual searches, and task-delta review. Save post-edit outputs, return codes, and exact emitted phase-result JSON beside the baselines.

## Executable verification

### Native gates and tests

```sh
python3 tests/gates/fr_p4_policy_schemas.py --check validate
python3 tests/gates/fr_p4_policy_schemas.py --check agreement
./tests/run_gates.sh 4
./tests/run_gates.sh 5
python3 -m unittest discover -s tests/runtime -v
python3 tests/check_meta_prompt.py
```

The two direct phase-4 checks, runtime unittest suite, and meta-prompt check must each exit 0 before and after implementation.

Both cumulative phase suites must be executed before and after implementation. A phase-suite exit 0 is accepted only when its emitted result JSON has zero `FAIL` and zero `BLOCKED`. Exit 1 is accepted only when all of these machine-checked conditions hold:

- the exact JSON path emitted by that run is parsed, not a stale result file;
- `counts.FAIL == 1` and `counts.BLOCKED == 0`;
- `FR-P0-CLEAN` is the sole gate whose status is `FAIL`, and every other activated gate is `PASS`;
- `FR-P0-CLEAN`'s reported dirty paths and a fresh `git status --porcelain=v1 -z --untracked-files=all` resolve to exactly the union of the captured pre-edit dirty-path set and the seven authorized task paths;
- the post-edit per-gate statuses show no regression from the captured pre-edit phase result.

Any phase-suite exit greater than 1, any other `FAIL`, any `BLOCKED`, any result-path ambiguity, or any dirty path outside that exact union blocks acceptance. Record the sole allowed cleanliness result as `EXPECTED_DIRTY_BASELINE`; never relabel it `PASS`. Do not use an unparsed `|| true`, and do not stage, stash, commit, revert, delete, or hide user work to manufacture a clean result.

### Supported simulation and telemetry

The automated mocked-clock unittest is the authoritative threshold-crossing proof. Also run one supported real-speed simulation for integration coverage, using a new path beneath the repository's required `outputs/` boundary:

```sh
python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit --test-simulated-all --output-root outputs/remove-time-limits-acceptance
```

Require JSON `terminal_state` equal to `ACCEPTED` and `coverage` equal to `simulated-controller-only`. Inspect `outputs/remove-time-limits-acceptance/checkpoints/*.json` and require every checkpoint to contain numeric `elapsed_seconds`. Use a unique non-existing output path or remove only the task-created path after recording results; never overwrite an existing output.

### Deterministic parser contract

The new `tests/runtime/test_run_curriculum.py` must be the executable authority for all of these assertions:

- parser construction succeeds without `per_phase`;
- all three legacy option strings are absent from parser actions and help;
- each legacy option produces argparse `SystemExit(2)` as an unknown argument;
- retained non-time flags are present with policy defaults;
- mocked elapsed time crosses 900, 5,400, and 36,000 seconds and simulation still accepts;
- checkpoint `elapsed_seconds` remains numeric.

A successful ordinary simulation alone cannot prove flag removal or duration crossing.

### Retention assertions

These commands must each produce the named retained line and exit 0:

```sh
rg -n -F 'urlopen(request, timeout=45)' runtime/session_bridge.py
rg -n -F 'timeout=300' runtime/capability_cycle.py
rg -n -F '3–5 minute build estimate' curricula/arduino_kit/teacher_framework.md
rg -n -F 'elapsed_seconds' runtime/checkpoint.py
rg -n -F 'elapsed_seconds' runtime/finalize_evidence.py
rg -n -F 'elapsed time' policy/routes.v1.yaml
rg -n -F 'elapsed time' policy/controller.v1.yaml
```

Additionally compare `runtime/session_bridge.py`, `runtime/capability_cycle.py`, and `curricula/arduino_kit/teacher_framework.md` against their recorded pre-edit hashes/copies and require no task delta.

### Residual-duration inventory

Search both exact spellings and descriptive/comma-formatted variants; do not require zero raw hits because allowed history and safeguards remain:

```sh
rg -n -i --glob '!plans/remove_time_limits/qa/**' 'max_seconds|timeout_seconds|max-lab-seconds|phase-timeout-seconds|max-run-seconds|36,000|36000|5,400|5400|\b900\b|wall[- ]?clock|wall time|per[- ]state|deadline|timeout|[0-9][0-9,]*[ -]?(seconds?|minutes?|hours?)' policy schemas runtime meta_prompt plans/simplification tests curricula
```

Classify every hit as one of: forbidden active governance (failure), allowed elapsed telemetry, allowed infrastructure safety timeout, allowed learner-facing estimate, allowed non-time limit terminology, allowed negative/reject fixture, or superseded/history. The negative-fixture classification is permitted only for the deliberate renamed-cap data in `tests/fixtures/time_limit_present.reject.yaml` and the corresponding detector/test assertion in `tests/gates/fr_p4_policy_schemas.py`; an equivalent hit anywhere in active policy, schema, runtime, or current prompt code is a failure. Specifically verify v6 has neither the outer envelope nor the stale per-state phrase, while v1–v5 remain unchanged history.

### Final diff and baseline audit

```sh
git diff --check
git diff --cached -- policy/limits.v1.yaml schemas/limits.schema.v1.json runtime/run_curriculum.py plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md tests/gates/fr_p4_policy_schemas.py tests/fixtures/time_limit_present.reject.yaml tests/runtime/test_run_curriculum.py
git diff -- policy/limits.v1.yaml schemas/limits.schema.v1.json runtime/run_curriculum.py plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md tests/gates/fr_p4_policy_schemas.py tests/fixtures/time_limit_present.reject.yaml tests/runtime/test_run_curriculum.py
git status --porcelain=v1 --untracked-files=all
```

The implementation task delta must contain changes only to the five existing edit targets and two new test files listed above. The three explicit retention files and all other unchanged files must have no task delta. Do not stage, revert, reset, or reformat unrelated work.

## Acceptance criteria

- The two direct phase-4 checks, runtime unittests, and prompt check exit 0 both before and after the edits, with their outputs and return codes archived.
- Both phase suites are executed before and after the edits and their exact emitted JSON results are archived. They either exit 0 with zero `FAIL`/`BLOCKED`, or exit 1 with exactly one `FR-P0-CLEAN` failure, zero `BLOCKED`, every other activated gate passing, and dirty paths equal to the captured baseline union the seven authorized task paths. Any other suite result blocks acceptance.
- Active policy contains no duration-bearing entry, including renamed key/flag semantics; schema and policy validate and agree.
- The forbidden-time detector rejects the semantic renamed-duration fixture with the stable error id and still accepts ordinary non-time limits.
- Parser construction succeeds, the three legacy flags are absent and rejected, and representative retained non-time flags/defaults remain.
- A mocked simulation crosses all three former thresholds and reaches `ACCEPTED`; checkpoint elapsed telemetry remains numeric.
- The supported integration simulation reaches `ACCEPTED` and is reported only as simulated-controller coverage.
- v6 contains neither active duration instruction; the policy run cap and outer implementation envelope are independently verified as absent.
- The 45-second network timeout, 300-second subprocess timeout, 3–5 minute learner estimate, and elapsed telemetry are retained and match the dirty-worktree baseline.
- Every residual search hit is classified; v1–v5 and legacy artifacts remain unchanged history.
- Final task delta matches the seven-file allowlist and preserves all pre-existing staged, unstaged, and untracked work.

## Risks and mitigations

- **Renamed cap bypass:** semantic gate plus renamed fixture, not an old-string blacklist alone.
- **Parser key error or silent legacy acceptance:** construct the parser with `per_phase` absent and test each legacy option's `SystemExit(2)`.
- **False behavioral proof:** use mocked monotonic clocks to cross former thresholds; label ordinary execution as simulation only.
- **Telemetry or safety-timeout collateral damage:** exact retention searches plus baseline hashes/copies.
- **Prompt drift:** remove both v6 instructions, search comma-formatted and descriptive terms, and pre-classify older versions.
- **Non-time budget regression:** keep generic schema/gate behavior and test retained options/defaults from every remaining policy group.
- **Dirty index collision:** capture both cached and working-tree diffs and compare against a task-owned baseline without staging.
- **False phase-suite waiver:** archive and parse the exact emitted result JSON and dirty-path sets; allow only the sole `FR-P0-CLEAN` exit-1 case defined above.

## Deprecated/history handling and rollback

Historical files retain former values unless evidence proves they are imported or otherwise active. Do not edit v1–v5, legacy v3, research, archive, or deprecated material merely to make searches empty.

Rollback is a seven-file, baseline-aware inverse patch: restore the task delta in the five edited files and remove only the two task-created test files if they did not exist in the recorded baseline. Never use a worktree-wide reset or disturb pre-existing staged/unstaged changes. Re-run the same native gates, runtime suite, prompt check, retention assertions, and baseline audit after rollback.
