# Remove Governing Curriculum Time Limits — Result v2

## Outcome

`PASS_WITH_BASELINE_FAILURES`

The seven-path implementation and all task-specific acceptance checks pass. The only
cumulative-gate failures are the unchanged documented `FR-P0-NOSTALE` and
`FR-P0-CLEAN` baseline conditions. The user confirmed that
`docs/research/sota_agents_research/action_log.jsonl` belongs to an intentionally
parallel `plans/sota_agents_pipeline` task and authorized treating it as external to
this work. It is therefore excluded from the time-limit task delta and was preserved
unchanged.

The authoritative evidence directory is
`/private/tmp/remove_time_limits_v2.nRaHLN`. An earlier incomplete capture directory
was abandoned before editing after a zsh-special-variable error; it is not used as
evidence.

## Implementation delta

Exactly five captured existing files differ from their pre-edit working-tree bytes:

- `policy/limits.v1.yaml`
- `schemas/limits.schema.v1.json`
- `runtime/run_curriculum.py`
- `plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md`
- `tests/gates/fr_p4_policy_schemas.py`

Exactly two implementation tests, both absent at baseline, were added:

- `tests/fixtures/time_limit_present.reject.yaml`
- `tests/runtime/test_run_curriculum.py`

No eighth implementation path was edited. The result file and the one appended
activity-log entry are required execution records, not implementation paths.

## Pre/post command evidence

| Command | Pre RC | Post RC | Evidence |
| --- | ---: | ---: | --- |
| `python3 tests/gates/fr_p4_policy_schemas.py --check validate` | 0 | 0 | `pre/commands/validate.*`, `post/commands/validate.*` |
| `python3 tests/gates/fr_p4_policy_schemas.py --check agreement` | 0 | 0 | `pre/commands/agreement.*`, `post/commands/agreement.*` |
| `./tests/run_gates.sh 4` | 1 | 1 | pre JSON `tests/results/gate_results.p4.20260803T140728.815975Z.json`; post JSON `tests/results/gate_results.p4.20260803T141133.154351Z.json` |
| `./tests/run_gates.sh 5` | 1 | 1 | pre JSON `tests/results/gate_results.p5.20260803T140732.446189Z.json`; post JSON `tests/results/gate_results.p5.20260803T141136.834494Z.json` |
| `python3 -m unittest discover -s tests/runtime -v` | 0 | 0 | 43 baseline tests and 47 post-edit tests pass |
| `python3 tests/check_meta_prompt.py` | 0 | 0 | 6/6 pre and post checks pass |

Post-only commands also passed with RC 0: the focused new runtime tests, supported
simulation, all five retention searches, and `git diff --check`. Exact stdout,
stderr, and RC files are under `focused/` and `post/commands/`.

## Gate regression comparison

Phase 4 retained `28 PASS, 2 FAIL, 0 BLOCKED, 8 SKIPPED`; phase 5 retained
`36 PASS, 2 FAIL, 0 BLOCKED, 0 SKIPPED`. The complete pre/post gate-id/status TSVs
are byte-identical (`phase4.status.diff.rc=0`, `phase5.status.diff.rc=0`). No passing
gate regressed and no new `FAIL` or `BLOCKED` appeared.

- `FR-P0-NOSTALE`: retained as `EXPECTED_PREEXISTING_FAILURE`. Status, detail,
  8-finding stale-reference set, and stdout digest `7b2936f4174cd063` are identical
  before and after. No authorized task path appears in the finding set.
- `FR-P0-CLEAN`: retained as `EXPECTED_DIRTY_BASELINE`. Its stdout digest changed
  from `1033e6916a86c9e1` to `f81b85891299de70`, as expected from the authorized
  implementation edits. The full NUL-delimited audit found 75 baseline dirty paths;
  baseline union the seven authorized paths yields 80 unique paths because two target
  paths were already staged at baseline. The task-produced set is exactly those 80.
  The task-produced set is exactly those 80 paths. The separately created 81st path is
  the user-confirmed external SOTA action log, not a time-limit task change or
  regression.

## Task-specific acceptance evidence

- Policy/schema: the lab, phase/state, and run duration entries and all three legacy
  flags are absent. The limits manifest validates without `per_phase`, while generic
  `per_lab` and `per_run` maps and all non-time limits remain.
- Parser: construction succeeds with no `per_phase`; help/actions omit
  `--max-lab-seconds`, `--phase-timeout-seconds`, and `--max-run-seconds`; each is
  rejected with `SystemExit(2)`. Representative defaults remain for `per_lab`,
  `per_run`, `convergence`, and `retry`.
- Semantic negative control: `time_limit_present.reject.yaml` is rejected as
  `forbidden-time-limit:per_run.wall_clock_minutes (--deadline-minutes)` while the
  active non-time policy passes.
- Mocked-duration regression: the simulation crosses 900, 5,400, and 36,000 seconds,
  reaches `ACCEPTED`, reports `simulated-controller-only`, and writes numeric
  checkpoint `elapsed_seconds` values.
- Supported integration simulation: RC 0 at
  `outputs/remove-time-limits-v2-acceptance`; terminal state `ACCEPTED`, coverage
  `simulated-controller-only`, 25 checkpoints, and every checkpoint elapsed value is
  numeric (`post/checkpoint_elapsed.rc=0`).
- Prompt v6: the active 36,000-second outer envelope and `per-state` binding text are
  absent. V1-v5 history was not edited.
- Diff hygiene: `git diff --check` returns 0.

## Preservation and residual inventory

The three preservation files are byte-identical to baseline and retain their original
SHA-256 values:

- `runtime/session_bridge.py`: `cf33899f51027d97761e70f6cbe945e4e647bf59711c6fbe41d19de5a21896f3`
- `runtime/capability_cycle.py`: `ddf5d11599f46dbcd99177a15cf5aca91b1bbc2f79a3c33f53f0940bd150791f`
- `curricula/arduino_kit/teacher_framework.md`: `4583f4f0f8a823fa68579b12b73dceb814b95184d9e9aec71d8cf4242affa17b`

The residual search produced 29 classified hits and no forbidden active governor:

- infrastructure/safety: the 45-second `urlopen` timeout and 300-second subprocess
  timeout;
- telemetry/non-time terminology: controller generic timeout/resource language and
  prompt-v6 cumulative wall-time reporting;
- deliberate tests: removed-flag spellings, mocked thresholds, detector vocabulary,
  the renamed reject fixture, and incidental-number accept fixture;
- learner/research guidance: the 3–5 minute estimate and research prose/numeric data;
- history: prompt v3-v5 duration rules and the handoff's old timeout-error reference.

Elapsed telemetry remains in `runtime/checkpoint.py`, `runtime/finalize_evidence.py`,
`policy/routes.v1.yaml`, and `policy/controller.v1.yaml`.

## Worktree, hashes, and Git safety

All seven post-edit implementation hashes are recorded in
`post/implementation_hashes.sha256`; baseline-to-current diffs are in `post/diffs/`.
Both the complete cached binary diff and cached raw NUL stream compare byte-for-byte
equal to baseline (`index_diff_cmp_rc=0`, `index_raw_cmp_rc=0`). No staging, stash,
commit, reset, restore, checkout, clean, deletion, hiding, or overwrite operation was
performed.

The external SOTA action log was first observed as an untracked 976-byte file with
mtime/ctime `2026-08-03T10:12:54-0400`; its first record is timestamped
`2026-08-03T14:12:54.476042Z`, after this task's baseline capture. The user identified
it as intentional parallel SOTA-pipeline work. Read-only discovery evidence is stored
in `post/unexpected_action_log.*` and `post/collision_final.*`; the confirming
reclassification audit is under `reclassified/`. That audit found no other external
delta, unchanged implementation and preservation hashes, a byte-identical Git index,
and `git diff --check` RC 0. All unrelated user work remains untouched.
