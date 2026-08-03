# GOAL

Implement the plan at `plans/_eval_rtd_ws/_eval_rtd_ws.plan.v1.md`. Read it
first and follow it; this prompt does not restate it in different words, and
where the two ever appear to disagree, the plan wins.

In short: `RetryTracker` in `runtime/retry.py` initializes `self.failures`,
`self.revisions` and `self.used` in `__init__` and never clears them, so one
tracker instance spanning several curriculum units carries an earlier unit's
repeat-failure history into a later one and can refuse a fresh unit a revision
on entirely unrelated content. Add an explicit `begin_unit(unit_id)` boundary
that resets those three, and cover it with tests.

Scope is exactly two files: `runtime/retry.py` and
`tests/runtime/test_retry.py`. Plus the result file and the log named under
LOOP. Nothing else.

Explicitly out of scope: wiring `RetryTracker` into the controller or any other
runtime module; changing the `failed_checks < previous` subset comparison;
changing any name, value or meaning in `policy/limits.v1.yaml`; altering
`RetryLimit` message strings; and repairing any gate that was already red.

## Before you mutate anything

Plan step 0 is fail-fast, and its checks are `RTD-T01`, `RTD-T02` and `RTD-T03`
in the test plan. Run them before touching `runtime/retry.py`. If any fails,
**stop and report** — do not adapt the plan around it:

- `RetryTracker` already has a unit-boundary method, or its state attributes
  differ from the plan's description → the fix may already be present in some
  form; the plan needs re-scoping.
- A production instantiation of `RetryTracker` now exists → that call site
  decides whether the tracker is built per run or per unit, which decides which
  fix is correct. Guessing is not permitted.
- The scratch reproduction does not show cross-unit carryover → the defect is
  not what the plan describes.
- The runtime suite is already failing at baseline → report it; do not work
  around a red baseline.

## The worktree constraint, up front

This repository has a legitimately dirty worktree containing the user's
uncommitted work, and both files you are about to edit are already staged
additions (`A ` in `git status --porcelain`).

Never run `git commit`, `git checkout`, `git restore`, `git stash`,
`git reset`, or `git clean` on any path, for any reason, including making a
check pass or cleaning up afterwards. If a check would only go green by
reverting a path that was already dirty at baseline, that check fails and you
report it. The user's uncommitted work outranks every test in this package.

# TEST

Use the ordered tests in `plans/_eval_rtd_ws/qa/execution_test.plan.v1.md`. Run
RTD-T00 through RTD-T13, strictly in order:

1. RTD-T00: captures the read-only baseline — 47 tests OK, the verbatim
   `git status --porcelain` snapshot, and the complete per-gate verdict list
   that every later comparison is measured against.
2. RTD-T01: proves the defect is still present exactly as the plan describes it.
3. RTD-T02: proves no production `RetryTracker` call site exists, which is what
   the plan's scope depends on.
4. RTD-T03: reproduces cross-unit carryover on a scratch copy of the unmodified
   class — this is what actually evidences the defect.
5. RTD-T04: proves `begin_unit` is absent — tests 3.1–3.5 error with
   `AttributeError`, test 3.6 passes by design. Five errors, one pass.
6. RTD-T05: proves the step-2 code shape is as specified, including that the
   `retry()` and `revision()` bodies are byte-for-byte unchanged.
7. RTD-T06: proves the six new tests exist and the three pre-existing ones are
   untouched.
8. RTD-T07: proves the post-change suite reports `Ran 53 tests` / `OK`.
9. RTD-T08: proves the reset semantics and configuration preservation the
   acceptance criteria name, as behaviour rather than code shape.
10. RTD-T09: proves a tracker that never calls `begin_unit` behaves exactly as
    it did at baseline.
11. RTD-T10: proves the porcelain delta is only `A ` → `AM` on the two target
    files, and that no other uncommitted work moved.
12. RTD-T11: proves no gate moved from PASS to FAIL or from PASS to BLOCKED
    relative to the RTD-T00 capture.
13. RTD-T12: proves the change touched only the two files it claims to touch.
14. RTD-T13: proves the result file and log entry are complete and true to what
    was actually observed.

# LOOP

On a test failure, fix only the in-scope artifact — `runtime/retry.py` or
`tests/runtime/test_retry.py` — then rerun that test and everything downstream
of it, not just the one that failed. Editing `runtime/retry.py` invalidates
RTD-T05 onward; editing the test file invalidates RTD-T06 onward. Continue
until every applicable test passes.

Two failure modes to resist, both of which the plan forecloses:

- If a new test fails, suspect the test before the fix. Plan step 2.5 forbids
  loosening `retry()` or `revision()` to make anything go green. In particular,
  `revision()` raises when `self.failures[key] >= self.repeat_threshold`, so the
  `repeat_threshold`-th submission is the one that raises — a test asserting
  otherwise is the thing that's wrong.
- If a gate is red, check the RTD-T00 capture before assuming you caused it.
  Four gates were FAIL and four BLOCKED when the plan was written, all
  pre-existing and all out of scope.

## Stop conditions

Stop and report rather than working around any of these:

- `RetryTracker` already has a unit-boundary method, or its state attributes
  differ from the plan's baseline description.
- A production instantiation of `RetryTracker` exists.
- The runtime suite is already failing at baseline.
- The RTD-T03 scratch reproduction does not show cross-unit carryover.
- Any verification step would require editing a file outside `runtime/retry.py`
  and `tests/runtime/test_retry.py` to go green.
- Any check would only pass by reverting, restoring, stashing, resetting, or
  cleaning a path that was already dirty in the RTD-T00 baseline snapshot.
- A gate that was PASS in the RTD-T00 capture is FAIL or BLOCKED afterwards.
- `policy/limits.v1.yaml` appears to need a change to make the semantics
  coherent. Raise it; do not edit policy under this plan.

## Result and log

Write `plans/_eval_rtd_ws/_eval_rtd_ws.result.v1.md` recording everything
RTD-T13 enumerates: the baseline test count and status, the `RetryTracker`
search result, the verbatim baseline porcelain snapshot, the per-gate baseline
verdicts naming every gate captured as FAIL or BLOCKED rather than a
pre-selected subset, the step-1.2 reset-scope decision and the step-1.3 recorded
ambiguity, the RTD-T03 reproduction output, the RTD-T04 observation in its true
shape (five `AttributeError`s from tests 3.1–3.5 and test 3.6 passing), the
final test count and status, the post-change porcelain with its diff against the
baseline, the post-change per-gate verdicts diffed against the baseline, and any
remaining failure.

Append the execution outcome to `plans/_eval_rtd_ws/plans.log.md` as a new
entry. The log is append-only: never edit or remove a prior entry, including
your own — a correction is always a new entry.

Completion may be claimed only when every applicable test id from RTD-T00 to
RTD-T13 has passed, with its evidence in the result file. A partial or blocked
state is reported as exactly that: which ids passed, which failed, which never
ran, and why. `FR-P0-CLEAN` remaining red afterwards is expected and is not a
failure of this work — report it as unchanged baseline state, and do not
describe phase 5 as clean.
