# Retry Scope Correction Plan v1 — Focused QA

## Verdict

**CHANGES REQUIRED — 0 Critical, 4 High.** Reviewed against the draft of v1, whose fix was
confined to keying `RetryTracker.failures` per unit. The diagnosis of the reported symptom
is correct, but as drafted the change is unobservable at runtime, leaves two of the three
budgets carrying the identical defect, cannot be driven end to end, and re-opens the same
hole through an optional parameter. All four findings are remediated in the current v1;
the mapping is recorded in `final_audit.v1.md`.

## Findings

### 1. High — the class being fixed has no production caller, and the live copy diverges

**Evidence.** `runtime/retry.py` is imported only by `tests/runtime/test_retry.py`. No
module under `runtime/` references `RetryTracker`. The behavior the user describes is
implemented independently at `runtime/controller.py:183` as
`failures_seen: dict[tuple[str, ...], int]`, incremented at `:197`, compared against
`self.limit_policy["convergence"]["repeat_failure_threshold"]["value"]` at `:201`, and
raising `RuntimeFailure("REPEAT-FAILURE", injected)` at `:202`. That copy has no narrowing
comparison at all and is scoped to a whole `simulate()` call.

**Impact.** A change confined to `runtime/retry.py` alters nothing a run can observe. The
user would receive a green test suite and an unchanged defect, while the only code path
that actually enforces the rule keeps the same unreset-scope bug. This is the single most
consequential gap in the draft.

**Minimal required remediation.** Bring the controller onto the corrected tracker in the
same change, deleting the inline dict rather than leaving two implementations. Preserve the
`REPEAT-FAILURE` failure id and terminal state so gate and log expectations do not move,
and require the existing `tests/runtime/test_controller.py:102-114` injection to still
raise.

### 2. High — `revisions` and `used` carry the identical defect and were left unfixed

**Evidence.** `runtime/retry.py:12-14` initializes `self.used` and `self.revisions` once
per object; `:19-21` and `:31` mutate them with no scope key and no reset. `revision_limit`
derives from `policy/limits.v1.yaml:21`, which sits under `per_lab:` and is described at
`:24` as bounding "a fourth attempt on the same failed-check set" — a per-lab budget.

**Impact.** With `max_revisions: 3`, a shared tracker exhausts the *whole run's* revision
budget after three revisions total, regardless of unit. Fixing only `failures` produces a
partial correction that will be reported later as a new bug with an identical root cause,
and any regression test written only against `failures` will not detect it.

**Minimal required remediation.** Scope all three budgets in one per-scope record rather
than keying a single dict, and require cross-unit independence tests for `used` and
`revisions`, not only for repeat failures.

### 3. High — the policy limits are unreachable from the CLI, so the fix cannot be proven end to end

**Evidence.** `runtime/run_curriculum.py:30-34` registers a flag for every entry in
`runtime.limit_policy`, including `--repeat-failure-threshold` and `--max-lab-revisions`.
`main()` at `:39-64` never passes the parsed values to `CurriculumRuntime`, and
`runtime/controller.py:201` reads the YAML value directly. The parsed overrides are
discarded.

**Impact.** Every documented limit override is inert today. The draft's verification
sequence assumes the threshold can be configured for a regression run; it cannot. Any
end-to-end test written against the flag would silently exercise the default value and
would pass whether or not the fix works — the worst possible test outcome.

**Minimal required remediation.** Plumb the parsed values into the runtime as tracker
construction parameters, keeping the YAML as defaults and changing no declared value. Keep
this narrow and make it an explicit stop if it cannot be done inside `run_curriculum.py`
and the runtime constructor.

### 4. High — an optional `scope` parameter reintroduces the defect, and the controller has no unit referent

**Evidence.** The draft proposed `revision(failed_checks, previous=None, unit_id=None)`
with a shared bucket when `unit_id` is absent, for compatibility with the existing tests.
Separately, `runtime/controller.py:185` iterates `self.states`, while `units` at `:174-176`
is a manifest list filtered by `lab_id`; the injected key at `:196` is `(injected,)`, a
check name. There is no per-unit loop in `simulate()` for a unit-scoped counter to attach
to.

**Impact.** A defaulted scope means the defective shared-bucket path survives as the
default behavior, and every future caller that omits the argument silently reproduces the
original bug — while the test suite, which does pass a scope, stays green. Combined with
the missing referent in the controller, an implementer would most likely key the counter on
state name, which is the same defect renamed.

**Minimal required remediation.** Make `scope` a required, non-defaulted parameter on both
budget methods and accept that every existing call site must be updated; remove `previous`
from the signature entirely so the tracker owns its own baseline. State explicitly what the
controller's scope key is — the selected unit id, or a named run-level constant — and
forbid keying on state.

## Notes carried forward, not findings

- The draft counted repeats non-consecutively, contradicting `policy/limits.v1.yaml:51`
  ("the same failed-check set twice without narrowing"). Corrected in v1 step 3; called out
  here because it changes semantics and needs its own test rather than being folded into
  the scope fix.
- `runtime/controller.py:203` advances to the next state after an injected failure instead
  of re-attempting it, so `attempts` counts attempts that never happen. A distinct
  state-machine defect. v1 correctly records it as out of scope.
