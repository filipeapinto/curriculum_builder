# Plan QA v3 — final contract re-review

## Gate verdict

**PASS** — 0 Critical, 0 High, 1 Medium, 0 Low findings.

Every Critical/High/Medium finding from the v1 and v2 contract reviews is remediated.
The plan is implementation-ready: its active edit inventory matches the repository,
its fixtures and runtime tests exercise the actual absence contract, its prompt/history
classification is correct, and its dirty-worktree gate policy is executable without
weakening gates or disturbing user work. The remaining Medium observation concerns
how to make one audit comparison unambiguous; it does not block the implementation or
its acceptance result.

## Prior-finding closure

| Finding | Final disposition | Evidence in the revised plan |
|---|---|---|
| v1 H1 — incomplete active-prompt/search inventory | **Remediated** | Lines 30–33 require removal of both v6 duration instructions; lines 181–189 search exact, comma-formatted, descriptive, and unit-based variants and distinguish current code, the deliberate reject fixture, and history. |
| v1 H2 — pytest commands collect no gates | **Remediated** | Lines 119–128 use the repository-native direct gate CLIs, cumulative phase runner, unittest discovery, and meta-prompt check. |
| v1 H3 — no biting fixture/parser regression | **Remediated** | Lines 34–50 require semantic renamed-cap detection, a biting fixture, parser construction without `per_phase`, legacy-option rejection, retained defaults, mocked threshold crossing, and numeric telemetry. |
| v1 M1 — conditional/uncertain edit scope | **Remediated** | Lines 52–66 resolve the unchanged controller, checks, meta-prompt, safety timeouts, telemetry, learner estimate, superseded prompts, and legacy runner explicitly. |
| v1 M2 — representative run not executable or honestly labelled | **Remediated** | Lines 142–163 define an exact supported simulated run, make the mocked-clock test authoritative, and prohibit generated/live-coverage overclaiming. |
| v1 M3 — conflated 36,000-second contracts | **Remediated** | Lines 3–10 distinguish the policy run cap from the outer development-task envelope and require independent removal/proof. |
| v2 H4 — impossible exit-0 requirement with `FR-P0-CLEAN` | **Remediated** | Lines 132–140 define an exact exit-1 exception only for sole `FR-P0-CLEAN`, require parsing the emitted JSON, prohibit `|| true`/cleaning/staging, and fail every other nonzero/failed/blocked result. Lines 204–205 repeat the same acceptance contract. |
| v2 M4 — route telemetry grep used the wrong literal | **Remediated** | Lines 165–177 use separate file-appropriate checks: `elapsed_seconds` for runtime records and `elapsed time` for route/controller prose. All seven commands match the current repository. |
| v2 M5 — no pre-edit execution baseline | **Remediated** | Lines 96–101 require all six commands before editing, archive stdout/stderr/return codes and the exact emitted phase JSON, capture per-gate/count status, and stop on any non-clean pre-existing blocker. Lines 107–115 and 204–205 require post-edit comparison. |

## New finding

### Medium — M6: make the `FR-P0-CLEAN` full-status comparison mechanism explicit

**Evidence.** The plan correctly requires the sole allowed phase-suite failure to be
`FR-P0-CLEAN` and requires a fresh NUL-delimited status set to equal the captured
baseline union the seven authorized paths (lines 132–138). The gate itself, however,
formats `detail` from only the first 20 dirty entries at
`tests/gates/fr_p0_structure.py:599–603`. The current tree has 64 entries under
`git status --porcelain=v1 --untracked-files=all`. The emitted runner JSON stores the
full gate stdout only as `stdout_digest`, not as path data
(`tests/gates/runner.py:176–195`). Therefore the JSON's human-readable `detail` cannot
by itself supply every dirty path.

This does not make the proof impossible: the fresh `-z --untracked-files=all` status
set is authoritative for exact path equality, and the JSON independently proves that
`FR-P0-CLEAN` was the sole failure. The gate's `stdout_digest` can additionally be
reproduced from a contemporaneous plain `git status --porcelain` if exact binding to
what the gate observed is desired.

**Recommended remediation.** Clarify that the machine check uses:

1. the exact emitted JSON for result identity, counts, sole-failure status, and the
   `FR-P0-CLEAN` stdout digest;
2. a contemporaneous plain porcelain status whose digest must equal that JSON digest;
3. the fresh NUL-delimited `--untracked-files=all` status for exact normalized path-set
   equality against baseline union authorized task paths.

Do not attempt to parse the truncated `detail` as the complete dirty-path list.

## Final technical assessment

The seven-file scope is correct:

### Existing files to edit

1. `policy/limits.v1.yaml`
2. `schemas/limits.schema.v1.json`
3. `runtime/run_curriculum.py`
4. `plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md`
5. `tests/gates/fr_p4_policy_schemas.py`

### New files to add

1. `tests/fixtures/time_limit_present.reject.yaml`
2. `tests/runtime/test_run_curriculum.py`

The revised plan correctly preserves generic non-time limits, controller/check/meta-
prompt contracts, elapsed-time reporting, the 45-second HTTP safety timeout, the
300-second subprocess safety timeout, learner-facing duration guidance, prompt v1–v5
history, and the unimported legacy runner.

Repository checks made during final review confirmed all revised retention literals:

- `runtime/session_bridge.py:130` contains `urlopen(request, timeout=45)`;
- `runtime/capability_cycle.py:134` contains `timeout=300`;
- `curricula/arduino_kit/teacher_framework.md:294` contains the 3–5 minute estimate;
- checkpoint/finalize files contain `elapsed_seconds`;
- route/controller policy contains `elapsed time`.

No source, production, test, or plan file was modified by this reviewer.

## Agent-log entry for `plans.log.md`

- `/root/plan_qa_contracts` performed the final repository-backed re-review of the
  revised remove-time-limits plan. All nine findings from contract QA v1/v2 are
  remediated. Final verdict: **PASS** with 0 Critical, 0 High, 1 Medium, and 0 Low; the
  sole Medium recommends binding the truncated `FR-P0-CLEAN` detail to its full stdout
  digest and using the fresh NUL-delimited status for exact path equality. The reviewer
  wrote only `qa/plan_qa.contracts.v3.md`.
