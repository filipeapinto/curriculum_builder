# RetryTracker Per-Unit State Reset — Implementation Plan v1

## Status and objective

Planning only; no implementation is authorized by this document's creation.

`runtime/retry.py` defines `RetryTracker`, whose `revision()` method records every
non-narrowing failed-check set in `self.failures` and raises `RetryLimit` once a given
set has been seen `repeat_threshold` times. That dictionary — like `self.revisions` and
`self.used` — is initialized once in `__init__` and never cleared. A `RetryTracker`
instance that spans more than one curriculum unit therefore carries one unit's
repeat-failure history into the next: a fresh unit whose content is entirely unrelated
can be refused a revision because an earlier unit already burned the budget for the same
check names, and the accumulated `revisions` count can exhaust the revision budget before
the second unit has attempted anything.

This plan makes the unit boundary explicit in `RetryTracker` and resets the per-unit
counters at that boundary. It changes `runtime/retry.py` and `tests/runtime/test_retry.py`
only.

It explicitly does **not**: wire `RetryTracker` into the controller or any other runtime
module (see step 0.2 — no production call site exists today, and creating one is a
separate change with its own design questions); change the subset comparison
`failed_checks < previous`; change the meaning, names, or values of any limit in
`policy/limits.v1.yaml`; or alter `RetryLimit` message strings that a caller might match.

## Exact work

### 0. Fail-fast preconditions

The plan was authored against a specific baseline. If the repository no longer matches it,
the remediation below may be wrong or already applied, so stop rather than adapt.

0.1 Confirm `runtime/retry.py` still has the defect as described: `RetryTracker.__init__`
assigns `self.failures: dict[tuple[str, ...], int] = {}`, `self.revisions = 0`, and
`self.used = {"malformed": 0, "transient": 0}`, and no method in the class reassigns or
clears any of those three after construction. If `RetryTracker` already exposes a
unit-boundary method, **stop**: the fix is already present in some form and this plan must
be re-scoped rather than applied on top.

0.2 Confirm the call-site fact this plan's scope depends on. Run a repository-wide search
for `RetryTracker` excluding `.git/`, `node_modules/`, and `__pycache__/`. At baseline the
only matches outside planning/eval material are `runtime/retry.py` and
`tests/runtime/test_retry.py` — there is **no production instantiation**. If a production
call site now exists, **stop**: that call site determines whether the tracker is
constructed per unit or per run, which changes which fix is correct, and this plan must be
re-scoped to cover it.

0.3 Capture the baseline test result: `python3 -m unittest discover -s tests/runtime -t .`
At baseline this reports `Ran 47 tests` / `OK`. Record the count and status. A failing
baseline must be reported, not worked around; do not proceed to step 1 with a red baseline.

0.4 Capture the baseline worktree state: `git status --porcelain`, verbatim, into the
result file. **This repository has a legitimately dirty worktree.** At the time this plan
was written `git diff --name-only` already listed six modified paths, including
`policy/limits.v1.yaml`, `schemas/limits.schema.v1.json`, `runtime/run_curriculum.py`,
`runtime/session_bridge.py`, and `tests/gates/fr_p4_policy_schemas.py`. That is the user's
uncommitted work. Under no circumstance may this plan's implementation run `git checkout`,
`git restore`, `git stash`, `git reset`, or `git clean` on any path — not to make a check
pass, not to "clean up". Every cleanliness assertion below is a **delta** against this
snapshot, never an absolute-clean assertion.

Both files this plan edits are **already in that snapshot as staged additions**:

```
A  runtime/retry.py
A  tests/runtime/test_retry.py
```

They are staged but never committed, which is why they do not appear in
`git diff --name-only` while they do appear in `git status --porcelain`. Expect them in
the baseline; their presence is not a precondition failure. What this plan's edits do to
them is change their porcelain code from `A ` (staged addition, worktree clean) to `AM`
(staged addition with a further unstaged modification) — the same transition already
visible in the baseline on `runtime/run_curriculum.py` and `runtime/session_bridge.py`.
That `A ` → `AM` transition on exactly these two paths is the expected, permitted delta;
every check below is written in those terms.

0.5 Capture the baseline gate result: `./tests/run_gates.sh 5`, recording **the complete
per-gate verdict list** into the result file. That captured list — not any list written in
this plan — is the authoritative baseline for every gate assertion below; the whole point
of step 0.5 is that the baseline is measured at implementation time rather than assumed.

For orientation only, the phase-5 state observed while this plan was being written was
`30 PASS, 4 FAIL, 4 BLOCKED, 0 SKIPPED of 38 registered`:

```
FR-P0-CLEAN          FAIL     (dirty worktree)
FR-P0-NOSTALE        FAIL     (8 stale-path hits)
FR-P2-DEFERRED       FAIL     (9 dangling deferred ids)
FR-P3-CAPS-OWNED     FAIL     (2 unowned cap copies under docs/research/)
FR-P2-BOUND          BLOCKED  (dependency FR-P2-DEFERRED failed)
FR-P2-SEL-MAPPED     BLOCKED  (dependency FR-P2-DEFERRED failed)
FR-P4-CHECK-MAPPING  BLOCKED  (dependency FR-P2-DEFERRED failed)
FR-P4-AGREEMENT      BLOCKED  (dependency FR-P4-CHECK-MAPPING blocked)
```

Every one of those eight is pre-existing, unrelated to `RetryTracker`, and out of scope. Do
not repair any of them under this plan. `FR-P0-CLEAN` in particular fails by construction
for any uncommitted change and will still be red after this work is applied; that is
expected and is not caused by this change.

Treat the block above as informational, not as a checklist to match. This repository's gate
state drifts with untracked and in-progress work, so the observed baseline may legitimately
differ by the time this plan is executed. If it does, record what step 0.5 actually
measured and proceed — a difference from the block above is not itself a finding, and it is
never grounds for repairing a gate. What matters is only that the step-0.5 capture is
complete and that step 4.2 compares against it.

### 1. Decide and record the reset scope from policy

This step produces no code change; it fixes the semantics the code in step 2 implements,
so that the choice is evidenced rather than assumed.

1.1 Read `policy/limits.v1.yaml`. The relevant entries are:
`per_lab.max_revisions` (value 3, rationale "a fourth attempt on the same failed-check set
is the repeat-failure signal"), `convergence.repeat_failure_threshold` (value 2, rationale
"the same failed-check set twice without narrowing ends the loop"), and
`per_lab.max_model_calls` (value 60, rationale "12 reviews + ~20 authoring calls + bounded
retries, with headroom").

1.2 Conclude and record in the result file: `max_revisions` is declared under `per_lab`,
and retries are budgeted inside the `per_lab` model-call allowance. Therefore
`self.revisions`, `self.failures`, and `self.used` are all **per-unit** state. All three
reset at a unit boundary. `self.limits`, `self.revision_limit`, and `self.repeat_threshold`
are configuration, not state, and must never be reset.

1.3 Record the one genuine ambiguity honestly rather than silently resolving it:
`repeat_failure_threshold` sits under `convergence`, not under `per_lab`. This plan treats
it as a per-unit threshold because the counter it governs (`self.failures`) keys on a
unit's own failed-check sets and is meaningless across units — but the policy file does not
say so in as many words. Note this in the result file as an assumption that a future policy
clarification could overturn; do not edit `policy/limits.v1.yaml` to resolve it.

### 2. Add an explicit unit boundary to `RetryTracker`

2.1 In `runtime/retry.py`, add an instance attribute `self.unit_id: str | None = None` to
`__init__`, alongside the existing attributes. Do not change any existing `__init__`
parameter, default, or attribute name.

2.2 Add a method to `RetryTracker`:

```python
def begin_unit(self, unit_id: str) -> None:
    if unit_id == self.unit_id:
        return
    self.unit_id = unit_id
    self.used = {kind: 0 for kind in self.limits}
    self.revisions = 0
    self.failures = {}
```

The early return is load-bearing, not an optimization: a caller that invokes
`begin_unit(current_unit)` once per attempt rather than once per unit must not silently
refill the budget it is supposed to be spending. Add a single short comment saying exactly
that, because the guard reads as a redundant fast path otherwise.

2.3 Rebuild `self.used` from `self.limits` keys rather than writing the literal
`{"malformed": 0, "transient": 0}` a second time, so the reset cannot drift from the
constructor if a limit kind is ever added.

2.4 Do not add validation of `unit_id` beyond what is written above (no emptiness check, no
type check, no "already seen this unit" error). `RetryTracker` is internal runtime code with
no external caller; validating a boundary that does not exist is out of scope.

2.5 Leave `retry()` and `revision()` bodies unchanged. Calling `revision()` or `retry()`
without ever calling `begin_unit()` must keep working exactly as it does today — a single
implicit unit with `unit_id` `None` — because that is the behaviour every existing test
depends on.

### 3. Cover the boundary in tests

Add to `tests/runtime/test_retry.py`, in the existing `RetryTests` class, using the same
`unittest` style already in the file. Do not modify or delete the three existing tests.

3.1 `test_begin_unit_resets_repeat_failures`: with `repeat_threshold=2`, drive a tracker to
one recorded repeat (`revision({"A", "B"}, {"A", "B"})`), call `begin_unit("unit-2")`, then
assert the counter has **restarted**, not that a larger budget exists. Concretely: after the
reset, `repeat_threshold - 1` further non-narrowing submissions of the same set succeed and
the `repeat_threshold`-th raises `RetryLimit` — with the default threshold of 2 that is one
successful call followed by one that raises, exactly the shape the pre-existing
`test_repeat_failure_limit` asserts for a fresh tracker.

Do not write this as "the set can be submitted `repeat_threshold` times before raising".
`revision()` raises when `self.failures[key] >= self.repeat_threshold`, so the
`repeat_threshold`-th submission is the one that raises; asserting otherwise produces a test
that fails against the *correct* fix and tempts an implementer into loosening `revision()`,
which step 2.5 forbids.

3.2 `test_begin_unit_resets_revision_count`: with `revision_limit=2`, exhaust the revision
budget for one unit, call `begin_unit("unit-2")`, and assert a further `revision()` call
succeeds.

3.3 `test_begin_unit_resets_retry_budget`: exhaust `retry("malformed")`, call
`begin_unit("unit-2")`, and assert `retry("malformed")` succeeds again.

3.4 `test_begin_unit_is_idempotent_within_a_unit`: call `begin_unit("unit-1")`, exhaust the
`malformed` retry budget, call `begin_unit("unit-1")` again with the *same* id, and assert
`retry("malformed")` still raises `RetryLimit`. This is the guard from step 2.2.

3.5 `test_begin_unit_preserves_configuration`: after `begin_unit("unit-2")`, assert
`tracker.limits`, `tracker.revision_limit`, and `tracker.repeat_threshold` are unchanged
from their constructed values.

3.6 `test_tracker_without_begin_unit_is_unchanged`: assert the pre-existing single-unit
behaviour still holds when `begin_unit` is never called — a tracker with
`repeat_threshold=2` still raises on the second repeat, exactly as
`test_repeat_failure_limit` asserts today.

### 4. Verify and record

4.1 Run the runtime suite and confirm the three pre-existing tests still pass alongside the
six new ones.

4.2 Re-run `./tests/run_gates.sh 5` and diff the per-gate verdicts against the step-0.5
baseline. Pass means **no gate moved from PASS to either FAIL or BLOCKED** — BLOCKED counts
as a regression because a gate can be knocked out by a newly failing dependency without
itself turning red. Any gate that was already FAIL or BLOCKED at the step-0.5 baseline and
still is remains the expected, already-recorded state: report it as unchanged, do not
repair it. Compare against the verdicts step 0.5 actually captured, not against any list
written in this plan.

4.3 Write the result file and append the log entry named under "Stop conditions and result".

## Verification sequence

1. `git status --porcelain` before any edit, recorded verbatim as **the baseline snapshot**
   (step 0.4) — pass means `runtime/retry.py` and `tests/runtime/test_retry.py` each appear
   with the porcelain code `A ` (staged addition, worktree clean). Their presence is
   expected, not a failure. What fails this step is either file carrying a worktree
   modification already (`AM` or ` M`), which would mean someone has edited it since the
   baseline was taken and this plan's premise no longer holds — stop and re-scope. Every
   other dirty path in that snapshot is the user's uncommitted work: expected, out of
   scope, and never to be reverted.
2. Repository-wide `RetryTracker` search — pass means the only non-planning matches are
   `runtime/retry.py` and `tests/runtime/test_retry.py`.
3. `python3 -m unittest discover -s tests/runtime -t .` before the change — pass means
   `Ran 47 tests` and `OK`.
4. Defect reproduction against the *unmodified* class, before any edit — pass requires
   both: (a) on a scratch copy outside the repository, a single `RetryTracker` instance
   driven through two simulated units shows the second unit inheriting the first's
   `failures` entries and raising `RetryLimit` early; and (b) **tests 3.1–3.5**, run
   against the unmodified source, error with
   `AttributeError: 'RetryTracker' object has no attribute 'begin_unit'`. Test 3.6 is
   deliberately excluded from 4(b): it never calls `begin_unit`, so it passes against the
   unmodified source by design — that is exactly what it is for, and its passing here is a
   pass of this step, not a failure. Expect five errors and one pass from the six new
   tests. Note that (b) alone proves only that the method is absent — it is the presence
   check, and (a) is what actually evidences the defect. Do not treat (b) as reproduction
   on its own.
5. `python3 -m unittest discover -s tests/runtime -t .` after the change — pass means
   `Ran 53 tests` and `OK`, with zero failures and zero errors.
6. `git status --porcelain` after the change, diffed against the step-0.4 baseline snapshot
   — pass means the **only** difference is that `runtime/retry.py` and
   `tests/runtime/test_retry.py` moved from porcelain code `A ` to `AM`. No other entry may
   appear, disappear, or change status, and no path may be added to the snapshot; if one
   has, uncommitted work was disturbed and that must be reported immediately, not silently
   corrected.
7. `./tests/run_gates.sh 5` after the change, diffed against the verdicts captured at step
   0.5 — pass means no gate moved from PASS to FAIL or from PASS to BLOCKED. Any gate that
   was FAIL or BLOCKED in the step-0.5 capture and still is matches the recorded baseline
   and is a pass, not a regression. The command exits non-zero whenever any gate is red, so
   judge this step on the per-gate diff, never on the exit status.

## Acceptance criteria

- `RetryTracker.begin_unit(unit_id)` exists and, when called with an id different from the
  current one, sets `self.failures` to `{}`, `self.revisions` to `0`, and every value in
  `self.used` to `0`.
- Calling `begin_unit` with the id already in force changes no counter.
- `self.limits`, `self.revision_limit`, and `self.repeat_threshold` are never mutated by
  `begin_unit`.
- `retry()` and `revision()` bodies are byte-for-byte unchanged from baseline.
- The three pre-existing tests in `tests/runtime/test_retry.py` are unmodified and pass.
- The runtime suite reports 53 tests, `OK`.
- The post-change `git status --porcelain` differs from the step-0.4 baseline snapshot only
  in that `runtime/retry.py` and `tests/runtime/test_retry.py` carry the porcelain code
  `AM` where the baseline had `A `. This is a delta assertion, not a clean-tree assertion:
  the baseline is legitimately dirty and must stay exactly as dirty as it was.
- No path present in the baseline snapshot was reverted, restored, stashed, reset, or
  cleaned. In particular `policy/limits.v1.yaml`, `schemas/limits.schema.v1.json`,
  `runtime/run_curriculum.py`, `runtime/session_bridge.py`, and
  `tests/gates/fr_p4_policy_schemas.py` retain their pre-existing uncommitted changes.
- No module under `runtime/` other than `retry.py` was edited by this work, and no file
  under `policy/` or `schemas/` was edited by this work.
- The phase-5 gate verdicts show no gate moving from PASS to FAIL, and none moving from PASS
  to BLOCKED, relative to the verdicts captured at step 0.5.

## Stop conditions and result

Stop on any of these rather than working around them:

- Step 0.1 finds `RetryTracker` already has a unit-boundary method, or its state attributes
  differ from the baseline described.
- Step 0.2 finds a production instantiation of `RetryTracker`. The correct fix depends on
  whether that call site builds one tracker per run or per unit; guessing is not permitted.
- Step 0.3 finds the runtime suite already failing at baseline.
- The scratch reproduction in verification step 4(a) does **not** show cross-unit carryover
  on the unmodified class. That would mean the defect is not what this plan describes, and
  the fix would be unverified against any real symptom.
- Any verification step requires editing a file outside `runtime/retry.py` and
  `tests/runtime/test_retry.py` to go green.
- Any check would only pass by reverting, restoring, stashing, resetting, or cleaning a path
  that was already dirty in the step-0.4 baseline snapshot. Stop and report; the user's
  uncommitted work outranks every check in this plan.
- A gate that was PASS in the step-0.5 capture is FAIL or BLOCKED afterwards. Report it; do
  not repair an unrelated gate under this plan.
- `policy/limits.v1.yaml` appears to need a change to make the semantics coherent. Raise it;
  do not edit policy under this plan.

Write `plans/_eval_rtd_ws/_eval_rtd_ws.result.v1.md` recording: the baseline test count and
status, the baseline `RetryTracker` search result, the verbatim step-0.4 `git status
--porcelain` baseline snapshot, the step-0.5 per-gate baseline verdicts, the reset-scope
decision from step 1.2 and the recorded ambiguity from step 1.3, the verification step 4(a)
scratch reproduction output and the 4(b) observations (five `AttributeError`s from tests
3.1–3.5 and test 3.6 passing), the final test count
and status, the post-change `git status --porcelain` together with its diff against the
baseline snapshot, the post-change per-gate verdicts diffed against the step-0.5 baseline —
naming **every** gate that the step-0.5 capture recorded as FAIL or BLOCKED, not a
pre-selected subset, so that the record shows the real phase-5 state rather than an
otherwise-green one — and any remaining failure. Append the execution outcome to `plans/_eval_rtd_ws/plans.log.md`.
