# Plan QA — Final Tests and Acceptance Re-review v3

## Verdict

**PASS** — 0 Critical, 0 High, 1 Medium, 0 Low.

Every v1 and v2 Critical/High finding is remediated. The revised plan now provides a complete, executable path to remove active lab, phase/state, run, and outer-task duration governance while retaining incidental time guidance, elapsed telemetry, infrastructure safety timeouts, non-time budgets, and historical records. One medium-strength audit-detail finding remains; it does not create a Critical/High implementation or acceptance blocker.

## Prior-finding remediation audit

### v1 findings

| Finding | Final status | Evidence in revised plan |
|---|---|---|
| QA-H1: pytest collected zero gates | **Remediated** | Native direct gate commands, phase runners, unittest discovery, and prompt validation are specified at lines 120–128. |
| QA-H2: central behavior lacked deterministic proof | **Remediated** | Lines 45–50 and 154–163 require parser construction, rejection of all legacy flags, retained defaults, mocked crossings of all three former thresholds, acceptance, and numeric checkpoint telemetry. |
| QA-H3: incidental/safety time retention was not verified | **Remediated** | Lines 55–64 define unchanged evidence; lines 165–179 use exact per-file assertions and baseline hashes; acceptance line 215 requires retention. |
| QA-M1: exact-string detector had no renamed-cap biting fixture | **Remediated** | Lines 35–44 require semantic key/flag inspection, stable `forbidden-time-limit`, a renamed-cap reject fixture, and proof that ordinary non-time limits remain accepted. |
| QA-M2: staged dirty baseline was not isolated | **Remediated** | Lines 79–105 capture cached/working diffs, file copies/hashes, machine-readable status, pre-edit execution results, and emitted phase JSON without staging or disturbing user work. |
| QA-M3: controller timeout wording was undecided | **Remediated** | Line 56 explicitly retains generic code ownership for infrastructure-operation timeouts and distinguishes it from removed generation-duration caps. |
| QA-L1: old prompt hits were not pre-classified | **Remediated** | Line 63 explicitly classifies v1–v5 as superseded history and v6 as current. |

### v2 findings

| Finding | Final status | Evidence in revised plan |
|---|---|---|
| QA2-H1: phase suites could not both preserve dirt and exit 0 | **Remediated** | Lines 130–140 and acceptance lines 204–205 no longer demand suite exit 0 unconditionally. They accept exit 1 only for exactly one `FR-P0-CLEAN` failure, zero BLOCKED, all other activated gates passing, exact result JSON, baseline-union dirty paths, and no per-gate regression. Any other result blocks acceptance. |
| QA2-M1: residual classification omitted the reject fixture | **Remediated** | Line 189 adds `allowed negative/reject fixture`, restricts it to the named fixture and detector assertion, and fails equivalent hits in active policy/schema/runtime/current prompt code. |
| QA2-L1: multi-file telemetry grep could pass partially | **Remediated** | Lines 173–176 split telemetry checks per file and use the actual term present in each file (`elapsed_seconds` or `elapsed time`). |

## New finding

### Medium — QA3-M1: The emitted phase JSON does not itself expose the complete dirty-path set

**Evidence**

- Revised plan lines 132–140 correctly require parsing the exact emitted result JSON and machine-checking that `FR-P0-CLEAN`'s dirty paths equal the captured baseline plus the seven task paths.
- `tests/gates/fr_p0_structure.py:600–603` places only `dirty[:20]` in the gate detail.
- `tests/gates/runner.py:172–184` stores `stdout_digest`, not the gate's raw stdout, in each JSON gate record.
- The present worktree has more than 20 dirty status entries, so neither the JSON detail nor captured runner stdout contains the complete list. The JSON digest can bind the gate to a separately captured exact `git status --porcelain` byte stream, but the plan does not explicitly require that digest recomputation.

**Impact**

The narrow dirty-suite waiver is otherwise sound: sole-failure identity, counts, blocking state, and the fresh full status set are all available. Without binding the fresh status bytes to `stdout_digest`, however, the assertion about the exact status observed by `FR-P0-CLEAN` is slightly stronger than the archived evidence directly demonstrates.

**Required remediation**

When applying the allowed exit-1 waiver, capture `git status --porcelain` byte-for-byte immediately with the suite result, recompute the runner's 16-character SHA-256 digest convention, and require equality with the `FR-P0-CLEAN.stdout_digest` value in that exact JSON. Separately normalize and compare `git status --porcelain=v1 -z --untracked-files=all` to the baseline-plus-seven-path union. Alternatively, narrow the prose to say the exact union is established by the fresh full-status capture while the JSON establishes sole-failure identity and counts.

This is Medium because it affects audit binding for the expected dirty-gate waiver, not the product change, duration-removal proof, retained-time safeguards, or the ability to identify any non-cleanliness gate regression.

## Final assessment

- **Scope clarity:** Complete and decisive. Both active 36,000-second contracts and the stale v6 per-state binding are explicitly targeted.
- **Acceptance criteria:** Executable and appropriately fail-closed, including a narrow dirty-worktree suite waiver.
- **Regression coverage:** Strong. It covers semantic renamed caps, all legacy CLI flags, retained non-time flags/defaults, former threshold crossing, and elapsed telemetry.
- **Retention boundary:** Explicitly verifies the 45-second network timeout, 300-second subprocess timeout, learner-facing estimate, and telemetry without broad timeout removal.
- **Dirty-worktree preservation:** Baseline-aware and non-destructive; no staging, stashing, reverting, or hiding is permitted.
- **Historical/deprecated handling:** Correctly retains v1–v5, legacy, research, archive, and deprecated evidence unless shown active.
- **Overall outcome:** The plan fully achieves the requested removal of governing hourly/minute duration caps without removing incidental time information or infrastructure safety timeouts. No Critical/High plan defect remains.

## Agent-log entry for `plans.log.md`

- `/root/plan_qa_tests` completed final re-review of revised `remove_time_limits.plan.v1.md` and wrote `qa/plan_qa.tests.v3.md`. All v1 and v2 findings are remediated; verdict **PASS** (0 Critical, 0 High, 1 Medium, 0 Low). The remaining Medium asks the implementation audit to bind `FR-P0-CLEAN.stdout_digest` to a separately captured full status stream because the emitted gate detail truncates dirty paths after 20 entries. No plan, production, source, policy, schema, prompt implementation, or test file was modified by this role.
