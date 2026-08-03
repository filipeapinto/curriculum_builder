# Plan QA — Tests and Acceptance Re-review v2

## Verdict

**FAIL** — 0 Critical, 1 High, 1 Medium, 1 Low. A PASS requires zero Critical/High findings.

The revision substantively remedies all seven v1 QA findings. It now identifies both active 36,000-second contracts, uses the repository-native runners, specifies deterministic CLI and mocked-threshold tests, protects retained timeouts/guidance, adds a semantic biting fixture, accounts for the staged dirty baseline, fixes the controller disposition, and pre-classifies historical prompt versions. One new High contradiction makes the cumulative gate acceptance impossible in the current dirty worktree.

## Prior-finding remediation audit

| Prior finding | Status | Revised-plan evidence |
|---|---|---|
| QA-H1: pytest commands collect zero tests | **Remediated** | Lines 113–120 use the custom gate entry points, `./tests/run_gates.sh 4/5`, runtime unittest discovery, and prompt validation. No pytest command remains. |
| QA-H2: no deterministic behavioral regression | **Remediated** | Lines 45–50 and 136–145 require parser construction, legacy-flag rejection, retained defaults, mocked crossings of 900/5,400/36,000 seconds, normal acceptance, and numeric checkpoint telemetry. |
| QA-H3: retained time information/safety timeouts unverified | **Remediated** | Lines 55–64 establish explicit unchanged dispositions; lines 150–158 add retention assertions and baseline comparison; acceptance line 191 requires all retained facts. |
| QA-M1: exact-name-only detector with no biting fixture | **Remediated** | Lines 35–44 require a semantic detector, stable `forbidden-time-limit` id, renamed-cap reject fixture, and an ordinary non-time accepting path. |
| QA-M2: staged dirty baseline not handled | **Remediated** | Lines 79–98 require complete porcelain status, cached and working-tree diffs, copies/hashes, absence records for new files, no staging, and final baseline comparison. |
| QA-M3: controller timeout ownership ambiguous | **Remediated** | Line 56 explicitly retains controller timeout ownership because the statement maps to no generation-duration value/flag and infrastructure timeouts remain code-owned. |
| QA-L1: v3–v5 history not pre-classified | **Remediated** | Line 63 explicitly retains v1–v5 as superseded history and cites the repository evidence establishing v6 as current. |

## New findings

### High — QA2-H1: The cumulative gate exit-code requirement is impossible in the protected dirty worktree

**Evidence**

- Revised plan lines 117–118 require `./tests/run_gates.sh 4` and `./tests/run_gates.sh 5`.
- Line 123 then says, “All commands must exit 0,” while also instructing the implementer to baseline-classify `FR-P0-CLEAN` and not erase user changes.
- Acceptance line 184 repeats that all six native commands exit 0 while allowing a baseline-classified cleanliness-only exception for phase 4/5 results.
- `tests/gates/registry.py:105–110` registers `FR-P0-CLEAN` at activation phase 0, so it necessarily runs in both phase 4 and phase 5.
- `tests/gates/fr_p0_structure.py:589–603` makes that gate fail whenever `git status --porcelain` contains any entry.
- The current worktree contains many staged, unstaged, and untracked user entries. The implementation will also add/modify seven allowlisted paths. Therefore `FR-P0-CLEAN` must fail in both suite runs unless the implementer stages, reverts, hides, or removes work—actions the plan correctly forbids.
- `tests/gates/runner.py` treats any FAIL as a nonzero run verdict. A prose classification cannot change its process exit code.

**Impact**

The revised acceptance remains unsatisfiable as written: preserving the dirty worktree guarantees two required commands do not exit 0, while making them exit 0 would violate the preservation rules. This is an executable-test blocker, not a product regression.

**Required remediation**

Make the exception operational and consistent in both verification and acceptance:

1. Require the two direct changed gates, runtime unittest suite, and prompt check to exit 0.
2. Run both cumulative phase suites and explicitly permit their process to exit nonzero **only** when the recorded result contains exactly the baseline-expected `FR-P0-CLEAN` failure and no other FAIL/BLOCKED result attributable to it or to the task.
3. Inspect the emitted ignored JSON result (or captured stdout) and require every non-cleanliness gate to pass. Record the clean-gate failure as `EXPECTED_DIRTY_BASELINE`, not as a passing gate.
4. Remove the contradictory “all six commands exit 0” language. Do not use `|| true` without parsing and asserting the result, and do not stage/stash/revert user work to manufacture a clean result.

If repository policy insists that phase suites can only validate a committed clean tree, classify those two suite checks as deferred commit-time verification and rely on the direct changed-gate and runtime tests for this dirty-worktree implementation pass.

### Medium — QA2-M1: The residual-hit classification omits the deliberately forbidden reject fixture

**Evidence**

- Lines 40–44 require new `tests/fixtures/time_limit_present.reject.yaml` containing `per_run.wall_clock_minutes` and `--deadline-minutes`.
- The residual search at line 165 includes `tests` and searches `wall[- ]?clock` and `deadline`, so the new fixture is guaranteed to appear.
- Line 169 permits only these classifications: forbidden active governance, elapsed telemetry, infrastructure timeout, learner estimate, non-time terminology, or history. A non-active negative fixture is none of those. Calling it forbidden active governance would incorrectly fail the intended biting test data.

**Impact**

The “classify every hit” criterion is ambiguous for a guaranteed, intentional hit and can cause either a false failure or a dishonest classification.

**Required remediation**

Add `allowed negative/reject fixture` as an explicit classification, require the hit to occur only in the named fixture/test assertion, and continue to fail any equivalent hit in active policy/runtime/prompt code.

### Low — QA2-L1: One multi-file telemetry assertion can pass without checking every named file

**Evidence**

- Line 156 runs one command: `rg -n -F 'elapsed_seconds' runtime/checkpoint.py runtime/finalize_evidence.py policy/routes.v1.yaml`.
- `policy/routes.v1.yaml:128` says `elapsed time`, not `elapsed_seconds`.
- `rg` exits 0 when any supplied file matches, so matches in the first two files allow the command to pass while producing no line from `policy/routes.v1.yaml`, contrary to the statement that each command must produce the named retained line.

**Impact**

The runtime checkpoint telemetry is already covered by the new deterministic test and the seven-file delta allowlist prevents collateral edits to these files, so this does not block the core outcome. The command is nevertheless weaker than its prose claim.

**Required remediation**

Split the assertion per file or search the correct term in each file, for example `elapsed_seconds` in checkpoint/finalize code and `elapsed time` in `policy/routes.v1.yaml`. Require every individual command to exit 0.

## Overall assessment

- **Scope clarity:** Complete. Both policy and outer-workflow duration governance are in scope; incidental, safety, telemetry, non-time, and historical material are decisively out of scope.
- **Acceptance criteria:** Strong after the revision, except for the impossible cumulative-suite exit-code rule.
- **Executable tests:** Correct native runners and deterministic runtime coverage are specified; the dirty-gate contradiction must be resolved.
- **Regression coverage:** Covers exact legacy flags, renamed caps, retained non-time defaults, threshold crossing, and telemetry.
- **Dirty-worktree preservation:** Thorough and baseline-aware.
- **Deprecated/history handling:** Clear and evidence-backed.
- **Requested outcome:** The planned seven-file task delta fully targets the active governing duration caps without authorizing removal of incidental time or infrastructure timeouts. Once QA2-H1 is corrected, no substantive implementation-scope blocker remains.

## Agent-log entry for `plans.log.md`

- `/root/plan_qa_tests` re-reviewed revised `remove_time_limits.plan.v1.md` and wrote `qa/plan_qa.tests.v2.md`. All seven v1 findings are substantively remediated. Verdict remains **FAIL** (0 Critical, 1 High, 1 Medium, 1 Low): phase-4/5 suites necessarily fail active `FR-P0-CLEAN` in the protected dirty worktree, contradicting the requirement that all six commands exit 0; residual classification also needs a negative-fixture category, and one telemetry assertion should be split per file. No plan, production, source, policy, schema, prompt implementation, or test file was modified by this role.
