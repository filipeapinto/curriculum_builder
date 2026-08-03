# Plan QA v2 — contracts, runtime, prompts, fixtures, and executable gates

## Gate verdict

**FAIL** — 0 Critical, 1 High, 2 Medium, 0 Low findings.

All six findings from `plan_qa.contracts.v1.md` are substantively remediated. The
revised plan has the right seven-file implementation inventory, distinguishes the two
36,000-second contracts, covers the missed v6 per-state instruction, uses the native
test runners, adds a biting renamed-cap fixture and parser tests, and defines honest
simulated threshold/telemetry evidence. One new High finding makes its stated native-
gate acceptance impossible in the repository's dirty-worktree workflow.

## Prior-finding disposition

| Prior finding | Disposition | Revised-plan evidence |
|---|---|---|
| H1 — missed active v6 per-state instruction/search gaps | **Remediated** | Lines 30–33 require both v6 edits; lines 161–169 search comma/descriptive variants and classify v1–v5 history. |
| H2 — pytest commands execute no gates | **Remediated** | Lines 112–121 use the two direct phase-4 checks, `run_gates.sh 4/5`, runtime unittest discovery, and the meta-prompt check. |
| H3 — no biting fixture or parser regression | **Remediated** | Lines 34–50 require a semantic detector, renamed-duration reject fixture, parser construction, removed-option rejection, retained defaults, threshold crossing, and telemetry assertions. |
| M1 — conditional edit scope | **Remediated** | Lines 52–66 explicitly retain controller/check/meta-prompt generic contracts and classify safety timeouts, telemetry, learner guidance, current prompt, and history. |
| M2 — representative run not executable/honestly labelled | **Remediated** | Lines 125–146 define an exact supported simulation, make the mocked-clock unittest authoritative, inspect checkpoint telemetry, and prohibit a live-generation claim. |
| M3 — conflated 36,000-second contracts | **Remediated** | Lines 3–10 distinguish `per_run.max_seconds` from the outer development-task envelope and require independent removal/proof. |

## New findings

### High — H4: the full-gate exit criterion is impossible in the required dirty-worktree state

**Evidence.** Revised-plan lines 123 and 184 require all six native commands to exit 0,
while also allowing a baseline-classified `FR-P0-CLEAN` exception. Those statements
cannot both hold:

- `tests/gates/fr_p0_structure.py:589–603` implements `FR-P0-CLEAN` as a literal
  `git status --porcelain` emptiness check; any dirty entry makes the gate fail.
- `tests/gates/runner.py:152–174` records that failure and returns exit 1 whenever any
  gate is `FAIL` or `BLOCKED`.
- `tests/gates/registry.py:105–111` activates `FR-P0-CLEAN` at phase 0, so both
  `./tests/run_gates.sh 4` and `./tests/run_gates.sh 5` execute it.
- The current target baseline is already dirty: `runtime/run_curriculum.py` and the
  current v6 prompt are staged additions, the runtime test suite is staged, and
  `plans/remove_time_limits/**` is untracked. Even from a clean baseline, the plan
  forbids staging/committing and requires five edits plus two new files, so the
  post-implementation worktree necessarily remains dirty.

The runner's JSON result is gitignored, but that does not change `FR-P0-CLEAN`'s
observation or the runner's nonzero exit.

**Required remediation.** Split the acceptance rule:

- Direct phase-4 checks, runtime unittests, and the meta-prompt check must exit 0.
- Run both full phase suites and require every task-relevant gate to pass with zero
  `BLOCKED`; allow runner exit 1 **only when** inspection of the generated JSON proves
  `FR-P0-CLEAN` is the sole failure and its dirty paths match the captured baseline plus
  the seven authorized task paths.
- Any other `FAIL`/`BLOCKED`, or any cleanliness delta outside that union, fails
  acceptance.

Remove “All six native verification commands exit 0” and the contradictory zero-failure
language. Do not weaken `FR-P0-CLEAN`, clean user work, stage, or commit merely to force
an exit-0 suite.

### Medium — M4: the route-telemetry retention command does not prove its stated target

**Evidence.** Revised-plan line 156 runs one `rg -F 'elapsed_seconds'` command against
`runtime/checkpoint.py`, `runtime/finalize_evidence.py`, and `policy/routes.v1.yaml`.
The first two contain the exact field, but `policy/routes.v1.yaml:128` says “elapsed
time,” not `elapsed_seconds`. Because ripgrep succeeds when any named file matches, the
combined command exits 0 without producing a route-policy line. This contradicts line
150's statement that each command produces the named retained line.

**Required remediation.** Use file-appropriate assertions, for example:

```sh
rg -n -F 'elapsed_seconds' runtime/checkpoint.py runtime/finalize_evidence.py
rg -n -F 'elapsed time' policy/routes.v1.yaml policy/controller.v1.yaml
```

Alternatively rely on recorded per-file hashes/task-delta comparison, but do not claim
the current combined grep verifies `policy/routes.v1.yaml`.

### Medium — M5: no pre-edit gate baseline supports the promised count-regression comparison

**Evidence.** Lines 78–97 capture file/status baselines before editing, but the ordered
procedure starts editing at line 103 without running the native gates or runtime suite
on that baseline. Lines 123 and 184 nevertheless require the final phase-4/5 counts not
to regress from “recorded pre-change” passing counts. Historical result files cannot
attribute a new failure in this already-dirty tree to this task versus another
pre-existing change.

**Required remediation.** Before the first implementation edit, run and record the two
focused checks, both phase suites, the runtime unittest suite, and the prompt check.
Save their return codes/counts and the phase-runner result JSON paths with the temporary
baseline evidence. Compare the post-edit results gate-by-gate, applying the explicit
`FR-P0-CLEAN` exception from H4. A pre-existing non-clean failure remains a baseline
condition; a newly failing or blocked task-relevant gate is a regression.

## Confirmed exact implementation scope

Subject to the H4/M4/M5 verification corrections, the revised edit scope matches the
repository:

### Existing edits

1. `policy/limits.v1.yaml`
2. `schemas/limits.schema.v1.json`
3. `runtime/run_curriculum.py`
4. `plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md`
5. `tests/gates/fr_p4_policy_schemas.py`

### New tests

1. `tests/fixtures/time_limit_present.reject.yaml`
2. `tests/runtime/test_run_curriculum.py`

The plan correctly leaves controller/check/meta-prompt generic contracts, infrastructure
timeouts, elapsed telemetry, learner duration guidance, v1–v5 prompt history, and legacy
v3 unchanged.

## Re-review evidence

- Re-read the complete revised plan and v1 QA report.
- Rechecked current target status, the phase-4 gate CLI/registry, `FR-P0-CLEAN`, runner
  exit/result behavior, runtime/controller/checkpoint clock use, route-policy telemetry,
  learner-duration text, prompt-version provenance, and the supported runtime/prompt
  test commands.
- `python3 tests/check_meta_prompt.py` currently reports 6/6 checks passing.
- No production, source, test, or plan file was modified by this reviewer.

## Agent-log entry for `plans.log.md`

- `/root/plan_qa_contracts` re-reviewed the revised remove-time-limits plan against all
  six prior QA findings and active repository contracts/runners. All prior findings are
  remediated, but the v2 review is **FAIL** with 0 Critical, 1 High, and 2 Medium new
  findings: the plan simultaneously requires exit 0 and permits the necessarily failing
  dirty-worktree `FR-P0-CLEAN` gate; its route-telemetry grep does not match the route
  file; and it lacks a pre-edit gate baseline for its no-regression comparison. The
  reviewer wrote only `qa/plan_qa.contracts.v2.md`.
