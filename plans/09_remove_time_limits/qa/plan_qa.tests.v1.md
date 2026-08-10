# Plan QA — Tests and Acceptance Review v1

## Verdict

**FAIL** — 0 Critical, 3 High, 3 Medium, 1 Low. A PASS requires zero Critical/High findings.

The plan identifies the three current policy caps correctly and draws the right boundary around elapsed-time telemetry, learner-facing time estimates, non-time budgets, and infrastructure-operation timeouts. Its implementation sequence is directionally sound. However, its stated verification does not execute the repository's gate harness, does not deterministically prove the central no-duration-stop behavior, and does not verify that explicitly preserved time information and safety timeouts survive unchanged.

## Findings

### High — QA-H1: The two listed gate commands execute zero tests

**Evidence**

- Plan lines 57–62 label `python3 -m pytest tests/gates/fr_p4_policy_schemas.py` and `python3 -m pytest tests/gates` as exact verification.
- `tests/gates/fr_p4_policy_schemas.py` exposes a custom `main()` requiring `--check`; it contains no pytest test functions.
- `tests/gates/registry.py:248–278` gives the executable commands, including `python3 tests/gates/fr_p4_policy_schemas.py --check validate` and `--check agreement`.
- `tests/run_gates.sh:1–14` is the repository's suite entry point.
- Direct execution of the plan's focused command returned exit code 5 with `collected 0 items` and `no tests ran`. The directory command likewise collected zero items.

**Impact**

The advertised focused and broad regression checks cannot pass and do not exercise the changed gate. This makes the acceptance procedure non-executable as written.

**Required remediation**

Replace both pytest commands with the repository-native commands. At minimum, run the changed checks directly (`--check validate` and `--check agreement`) and run `./tests/run_gates.sh 4` plus `./tests/run_gates.sh 5`. State expected nonzero-safe counts or, at minimum, require zero FAIL/BLOCKED and preserve the known phase-4 baseline. Add `python3 -m unittest discover -s tests/runtime -v` for the runtime/parser regression described in QA-H2.

### High — QA-H2: The central behavioral acceptance claim has no deterministic regression test

**Evidence**

- Plan lines 71–74 require help-text absence, unknown-argument rejection, a representative run that is not duration-terminated, and continued elapsed-time telemetry, but none has an exact command or named automated test.
- The intended test edit at lines 20 and 41 is limited to `tests/gates/fr_p4_policy_schemas.py`; the plan does not identify a runtime test edit.
- `runtime/run_curriculum.py:30–32` is the only consumer of all three duration entries and merely creates argparse options.
- `runtime/controller.py:31` loads the limit policy; its only later `limit_policy` use is the non-time convergence threshold at line 201. A normal simulated run therefore already succeeds before the cap removal and cannot prove that the change removed duration governance.
- Existing `tests/runtime/test_controller.py` checks simulated acceptance and convergence behavior but does not inspect parser options, rejected legacy flags, mocked elapsed thresholds, or elapsed telemetry retention.

**Impact**

A representative run is a false-positive test for this change: it does not traverse any duration-cap enforcement. The implementation could retain a hidden alias, accept a removed flag, or damage telemetry while still satisfying the proposed run check.

**Required remediation**

Add a named runtime test target (in `tests/runtime/test_controller.py` or a focused CLI test module) that:

1. builds `parser_for(CurriculumRuntime(...))` and proves all three option strings are absent;
2. proves each legacy flag raises argparse's unknown-argument `SystemExit`;
3. executes a deterministic simulation with a mocked monotonic clock crossing the former 900/5,400/36,000-second thresholds and proves the run reaches its normal terminal state; and
4. inspects checkpoint/log output to prove elapsed-time fields remain present and numeric.

List the exact unittest command in verification. A ten-hour real run is neither necessary nor an acceptable substitute for this deterministic test.

### High — QA-H3: Preservation of incidental time information and infrastructure safety timeouts is not tested or diff-guarded

**Evidence**

- Plan lines 28–31 correctly require retaining `runtime/session_bridge.py`'s `urlopen(..., timeout=45)`, `runtime/capability_cycle.py`'s `subprocess.run(..., timeout=300)`, and `curricula/arduino_kit/teacher_framework.md`'s “3–5 minute” learner estimate.
- The exact search at line 62 searches neither `timeout=45` nor `timeout=300`, and it omits the `curricula` tree entirely.
- The final scoped diff at line 64 includes none of those three preservation targets.
- `git diff --check` only checks patch whitespace/errors; it does not prove those values or files remained unchanged.

**Impact**

The task's essential negative boundary—remove governing curriculum duration caps without removing incidental time information or safety timeouts—can regress while every listed exact check still succeeds.

**Required remediation**

Add explicit post-change assertions for the three retained facts, preferably exact `rg`/small Python checks with failure-on-absence semantics. Also compare each preservation file against the recorded dirty-worktree baseline or include it in a task-delta allowlist audit. Include `curricula`, `runtime/session_bridge.py`, and `runtime/capability_cycle.py` in the final classification report without treating their allowed hits as failures.

### Medium — QA-M1: The absence gate is specified too narrowly and has no biting fixture

**Evidence**

- Plan lines 20 and 41 require only an assertion that the three known entries/flags are absent.
- `tests/gates/fr_p4_policy_schemas.py:237–252` currently validates generic number/flag shape.
- The schema intentionally permits arbitrary property names beneath `per_lab` and `per_run` through `additionalProperties`; after the edit, a cap such as `per_run.wall_clock_minutes` / `--deadline-minutes` would remain schema-valid.
- The plan mentions “focused gate tests and fixtures” at line 51 but names no new reject fixture or expected detector error for duration governance.

**Impact**

The regression gate can pass after the same policy is reintroduced under a different duration-bearing key or flag, and no negative fixture proves the new detector can bite.

**Required remediation**

Define the detector contract and add at least one reject fixture using a renamed duration cap, while retaining an accepting fixture for ordinary non-time limits. Require a stable error id. The detector should cover duration-governance semantics in policy keys/flags, not only the three original spellings; avoid scanning general prose where incidental time is valid.

### Medium — QA-M2: Dirty-worktree protection does not account explicitly for staged target baselines

**Evidence**

- Current status includes staged pre-existing changes in two intended targets: `M  meta_prompt/curriculum.prompt.v1.md` and `A  plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md`. The runtime itself and its tests are also staged additions.
- Plan line 46 says to inspect diffs, but the exact final command at line 64 is plain `git diff`, which compares the working tree to the index and does not show the already staged baseline.
- No baseline hash/snapshot or `git diff --cached` inspection is specified.

**Impact**

An implementer can misunderstand staged user content as task-created content or lose the ability to distinguish the task delta from the pre-existing index state. This is especially important because the plan intentionally edits a staged new file.

**Required remediation**

Before edits, record `git status --porcelain=v1 --untracked-files=all`, inspect both `git diff --cached -- <targets>` and `git diff -- <targets>`, and hash or copy the exact target baselines to a task-owned temporary location. Do not stage. At completion, compare the working-tree task delta against the recorded index/baseline and confirm all pre-existing status entries remain represented.

### Medium — QA-M3: Controller timeout ownership is left as an implementation-time judgment

**Evidence**

- Plan lines 16 and 38 say to “determine” or narrow `policy/controller.v1.yaml:18` only if necessary.
- The actual text is `retries, timeouts, stall detection, resource limits`; it states code ownership but specifies no duration value or curriculum-generation deadline.
- The plan simultaneously requires preserving network/subprocess timeouts, which remain appropriately code-owned.

**Impact**

The implementer has no objective acceptance rule for whether this line changes. Removing `timeouts` broadly could incorrectly erase infrastructure ownership; retaining it without clarification could be misread as retained generation-duration governance.

**Required remediation**

Make the disposition explicit: retain generic code ownership of infrastructure-operation timeouts, or narrowly rewrite it to say so. Require no controller edit unless it states or maps to a lab/phase/run duration cap. Add the decided wording to the post-change classification.

### Low — QA-L1: Historical prompt hits are discoverable but not pre-classified in the evidence table

**Evidence**

- Active-tree search finds the same 36,000-second text in `implement_curriculum_runtime.prompt.v3.md`, `v4.md`, and `v5.md`.
- `plans/simplification/prompt/migrate_external_run_evidence.prompt.v2.md:47–50` explicitly classifies v4/v5 as byte-unchanged history and v6 as current; version ordering likewise makes v3 older.
- The plan's general history rule and remaining-hit classification can handle these, but the evidence inventory lists only v6.

**Impact**

This is unlikely to cause a wrong edit, but the exact search will produce expected hits that may surprise the implementer.

**Required remediation**

Pre-classify v3–v5 as retained historical versions in the inventory and cite the active v6 evidence. Do not edit them solely to make the search empty.

## Coverage assessment

- **Scope clarity:** Mostly correct; the controller `timeouts` disposition needs a firm decision.
- **Acceptance criteria:** Outcome-oriented, but incomplete until the central behavior and retention boundary have deterministic checks.
- **Executable tests:** Fails because both pytest commands collect zero tests.
- **Regression coverage:** Incomplete for CLI removal, duration-crossing behavior, telemetry retention, renamed caps, and preserved safety/incidental time.
- **Dirty-worktree preservation:** Correct intent, insufficient handling of staged target baselines.
- **Deprecated/history handling:** Correct; older prompt versions should remain historical and be classified rather than rewritten.
- **Achievement of requested outcome:** The intended edits would remove the three known governing definitions and their CLI exposure, but the current verification cannot prove the full outcome or its required non-removals.

## Agent-log entry for `plans.log.md`

- `/root/plan_qa_tests` completed independent test/acceptance QA of `remove_time_limits.plan.v1.md` and wrote `qa/plan_qa.tests.v1.md`. Verdict: **FAIL** (0 Critical, 3 High, 3 Medium, 1 Low). High findings: the proposed pytest commands collect zero tests; the no-duration-stop/telemetry claim lacks a deterministic runtime regression; and preservation of the 45-second network timeout, 300-second subprocess timeout, and learner-facing 3–5 minute estimate is not verified. No production, source, policy, schema, prompt implementation, or test file was modified by this role.
