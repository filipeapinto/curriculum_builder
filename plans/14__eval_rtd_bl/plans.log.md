# Retry Scope Correction Planning Log

Append-only record for the planning, QA, test-planning, and implementation-prompt workflow.
Existing entries must not be edited or removed; later corrections are new entries.

## Objective

`RetryTracker` in `runtime/retry.py` holds three retry budgets in run-lifetime state that is
never scoped or reset, so one unit's exhausted budget blocks every later unit. Make scope a
required, non-defaulted part of the API; bring the divergent live copy of the repeat-failure
rule in `runtime/controller.py` onto it; and make the policy-declared limits reachable from
the CLI so the correction is provable end to end.

## Entry template

```text
### <UTC timestamp> — <agent/task>
- Action: <work performed>
- Paths touched: <paths, or none>
- Evidence/decision: <verification or decision rationale>
- Issues: <critical/high findings, blockers, or none>
```

## Entries

### 2026-08-03T15:19:01Z — planner

- Action: Read `runtime/retry.py` in full, then traced every reference to `RetryTracker`,
  `RetryLimit`, and the repeat-failure limits across `runtime/`, `tests/`, `policy/`, and
  `schemas/` before writing anything.
- Paths touched: None (read-only).
- Evidence/decision: A repository-wide identifier search returned only `runtime/retry.py`
  and `tests/runtime/test_retry.py` — the class has **no production caller**. The rule is
  independently reimplemented at `runtime/controller.py:183,196-203` as `failures_seen`,
  with no narrowing comparison and a `simulate()`-lifetime scope. `runtime/run_curriculum.py:30-34`
  registers limit flags that `main()` then discards. The reported symptom is real but is one
  of three budgets carrying the same defect.
- Issues: A fix confined to `runtime/retry.py` would have changed no observable behavior.

### 2026-08-03T15:24:00Z — planner

- Action: Authored implementation plan v1 with a six-item grounded defect inventory (D1–D6),
  a required-`scope` API, tracker-owned narrowing baseline, controller consolidation, limit
  plumbing, and falsifiable regression tests.
- Paths touched: `plans/_eval_rtd_bl/retry_scope.plan.v1.md`.
- Evidence/decision: Chose a required `scope` parameter over a per-unit-instance convention.
  A convention is unenforceable and is precisely the discipline that failed here; a required
  parameter makes the defect unrepresentable. Recorded `runtime/controller.py:203`
  (advancing past a failed state rather than re-attempting it) as an adjacent defect, out of
  scope.
- Issues: None pending Critical/High QA.

### 2026-08-03T15:31:00Z — plan_qa

- Action: Completed focused Critical/High QA of the plan draft against the repository,
  the limits policy, the existing tests, and the dirty worktree.
- Paths touched: `plans/_eval_rtd_bl/qa/plan_qa.v1.md`.
- Evidence/decision: Verdict CHANGES REQUIRED, 0 Critical and 4 High. The draft fixed only
  `failures` keying: unobservable at runtime given the missing caller and the divergent
  controller copy; `revisions` and `used` left defective; CLI limit overrides discarded so no
  end-to-end test could drive the threshold; and an optional `scope` parameter that would
  have preserved the defective shared bucket as the default path.
- Issues: Four High findings, all remediable within the original scope.

### 2026-08-03T15:36:00Z — planner

- Action: Incorporated all four High remediations into plan v1 without broadening the
  objective.
- Paths touched: `plans/_eval_rtd_bl/retry_scope.plan.v1.md`.
- Evidence/decision: Made `scope` required and non-defaulted and removed `previous`
  entirely; scoped all three budgets in one per-scope record; added controller consolidation
  with a pinned `REPEAT-FAILURE` failure id and an explicit prohibition on keying by state
  name; added narrow limit plumbing with its own stop condition. Also corrected repeat
  counting to consecutive-only, matching `policy/limits.v1.yaml:51`.
- Issues: None. Limit plumbing is the widest remaining item and carries an explicit stop.

### 2026-08-03T15:42:00Z — qa_test_plan

- Action: Authored the ordered execution test plan, RS-T00 through RS-T09.
- Paths touched: `plans/_eval_rtd_bl/qa/execution_test.plan.v1.md`.
- Evidence/decision: Placed RS-T01 — the new tests run against the **unmodified** module and
  required to fail — before any edit, since a regression test that passes before the fix
  proves nothing. Remaining tests cover per-scope isolation for all three budgets, narrowing
  and consecutiveness, the API contract, controller single-implementation and behavioral
  equivalence, CLI override binding, gate-by-gate comparison, static/simulated regression,
  and a final worktree and allowlist audit.
- Issues: None.

### 2026-08-03T15:47:00Z — prompt_writer

- Action: Authored the Claude Code implementation prompt with explicit GOAL, TEST, and LOOP
  sections derived from the corrected plan and the execution test plan.
- Paths touched: `plans/_eval_rtd_bl/prompts/retry_scope.prompt.v1.md`.
- Evidence/decision: GOAL fixes the five allowed edits and the exact allowlist; TEST
  enumerates RS-T00–RS-T09 in order and makes RS-T01's recorded pre-fix failure a
  precondition for any success claim; LOOP forbids the specific escape hatches most likely to
  be reached for — making `scope` optional, keying the controller on state, relaxing a policy
  value, widening the allowlist, or deleting a failing assertion.
- Issues: None.

### 2026-08-03T15:52:00Z — final_auditor

- Action: Completed the final standing audit of the plan, focused QA, execution test plan,
  implementation prompt, and log.
- Paths touched: `plans/_eval_rtd_bl/qa/final_audit.v1.md`.
- Evidence/decision: PASS, 0 Critical and 0 High remaining. All four High findings map to
  named plan steps, test ids, and prompt items; every test id referenced by the prompt exists
  in the test plan and vice versa; the three intentional behavior changes each carry a test;
  and worktree-safety rules are stated identically in all four artifacts.
- Issues: None blocking. Three residual risks accepted and recorded: limit plumbing is the
  widest change, `release()` permits use-after-release, and `simulate()` still has no
  per-unit loop — the correction readies the tracker for one rather than creating it.
