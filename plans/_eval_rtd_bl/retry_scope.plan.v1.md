# Retry Scope Correction — Implementation Plan v1

## Status and objective

Planning only. Creating this document authorizes no implementation.

`RetryTracker` in `runtime/retry.py` accumulates every retry budget in run-lifetime state
that is never reset or keyed by the unit being worked on. The reported symptom is one
unit's repeated failed-check set permanently blocking later, unrelated units. The
underlying defect is broader: the class holds **three** budgets — `used`, `revisions`,
`failures` — and none of them carries a scope.

The objective is to make scope explicit and structurally unavoidable in `RetryTracker`,
to bring the one live divergent reimplementation of the same rule into agreement with it,
and to make the policy-declared limits actually reachable from the CLI so the corrected
behavior is testable. Nothing else changes: no policy value moves, no state machine is
redesigned, no new retry loop is introduced.

## Grounded defect inventory

### D1 — repeat-failure state is never scoped or reset (reported)

`runtime/retry.py:16,26-30`. `self.failures` is keyed by `tuple(sorted(failed_checks))`
alone. A unit that fails `{A,B}` twice consumes the global budget for that key; any later
unit whose checks happen to fail as `{A,B}` raises `RetryLimit` on its first
non-narrowing revision.

### D2 — the same defect in `revisions` and `used`, unreported

`runtime/retry.py:12-14,19-21,31`. `self.revisions` is compared against `revision_limit`,
whose policy source is `policy/limits.v1.yaml:21` under `per_lab:` — it is explicitly a
per-lab budget held in run-lifetime state. `self.used` for `malformed`/`transient` is
likewise global. Correcting only `failures` leaves two of the three budgets carrying the
identical defect and produces the same class of cross-unit blocking.

### D3 — non-consecutive accumulation contradicts the policy rationale

`policy/limits.v1.yaml:51` defines the threshold as "the same failed-check set twice
without narrowing", and `:24` as "a fourth attempt on the same failed-check set". The code
counts occurrences of a set key across the whole object's lifetime, so `{A}` → `{B}` →
`{A}` trips the threshold even though the set changed in between. The user's own wording —
"twice in a row" — describes the intended rule, not the implemented one.

### D4 — `previous` is caller-owned, so the tracker cannot enforce its own rule

`runtime/retry.py:23`. The comparison baseline is supplied by the caller on every call.
The tracker holds the counter but not the baseline, so two callers, or one caller with a
bookkeeping slip, can desynchronize them. The reported bug is one instance of that split.

### D5 — the live rule is implemented a second time, in the controller, and diverges

`runtime/controller.py:183,196-203` maintains its own `failures_seen: dict[tuple[str, ...], int]`,
compares it against `self.limit_policy["convergence"]["repeat_failure_threshold"]["value"]`,
and raises `RuntimeFailure("REPEAT-FAILURE", ...)`. It never imports `RetryTracker`. It has
no narrowing comparison at all, and its dict is scoped to one `simulate()` call across the
state loop. **`RetryTracker` currently has no production caller** — `tests/runtime/test_retry.py`
is its only importer. A change confined to `runtime/retry.py` therefore alters no observable
runtime behavior, while the live copy keeps the same unreset-scope defect.

### D6 — the policy limits are registered as CLI flags and then discarded

`runtime/run_curriculum.py:30-34` generates `--max-lab-revisions`, `--repeat-failure-threshold`
and the rest from `runtime.limit_policy`, but `main()` never passes the parsed values to
`CurriculumRuntime`; `runtime/controller.py:201` reads the YAML default directly. Every
documented override is inert. No end-to-end test can drive the threshold, so the corrected
behavior would be provable only at unit level.

**Adjacent, explicitly out of scope:** `runtime/controller.py:203` `continue`s to the next
state after an injected failure rather than re-attempting the failed one, so `attempts` is
counted but no state is actually retried. That is a distinct state-machine defect. Record
it; do not fix it here.

## Exact work

### 1. Freeze a behavioral baseline before editing

- Capture `git status --porcelain=v2 -z --untracked-files=all` plus cached and working-tree
  diffs. The worktree is dirty with extensive unrelated staged user work; never stage,
  stash, reset, restore, clean, or overwrite it.
- Record current outcomes for `python3 -m unittest discover -s tests/runtime`,
  `./tests/run_gates.sh 4`, `./tests/run_gates.sh 5`, and one
  `--test-simulated-all` run into an external evidence root outside the repository.
- The implementation allowlist is exactly: `runtime/retry.py`, `runtime/controller.py`,
  `runtime/run_curriculum.py`, `tests/runtime/test_retry.py`,
  `tests/runtime/test_controller.py`, `tests/runtime/test_run_curriculum.py`, and this
  plan's own artifacts. A required change outside it is a stop, not an extension.

### 2. Make scope a required argument of `RetryTracker`

Replace the shared counters with per-scope state. The API becomes:

- `retry(self, kind: str, *, scope: str) -> None`
- `revision(self, scope: str, failed_checks: set[str]) -> None`
- `release(self, scope: str) -> None`

Required properties:

- `scope` is a required, non-defaulted parameter on both budget methods. It must not be
  optional and must not fall back to a shared bucket — an optional scope reintroduces D1
  the first time a caller omits it.
- All of `used`, `revisions`, the repeat counter, and the previous failed-check set live
  in one per-scope record, created on first use for that scope. Two scopes never share a
  counter.
- `revision_limit` and the malformed/transient limits apply per scope, matching their
  `per_lab:` policy source at `policy/limits.v1.yaml:15-24`.
- `release(scope)` drops a finished scope's record so a long run does not retain state for
  every completed unit. Releasing an unknown scope is a no-op; a released scope that is
  used again starts fresh, and callers must not release a scope they will reuse.
- Construction parameters, `RetryLimit`, and the existing message strings are unchanged, so
  failure identification in logs and gates is stable.

### 3. Move the narrowing baseline inside the tracker and make repeats consecutive

- Delete the `previous` parameter. The tracker stores the last failed-check set per scope
  and compares against it. This closes D4 by removing the caller's ability to supply a
  baseline at all.
- Repeat rule, per scope: on `revision(scope, failed)`, if there is no previous set, or
  `failed` is a strict subset of the previous set, reset the repeat counter to 1 for the
  newly observed set. If `failed` equals the previous set, increment. Raise
  `RetryLimit("repeated failure set did not narrow")` when the counter reaches
  `repeat_threshold`. A set that changes without narrowing resets the counter, because the
  policy clause at `policy/limits.v1.yaml:51` is about *the same* set recurring.
- Lateral thrash — a changing, never-narrowing set — is deliberately not caught here.
  `policy/limits.v1.yaml:52` `complexity_without_progress_cycles` is the policy's existing
  instrument for that, and inventing a second one is outside this correction.
- Check the revision-limit exhaustion before the repeat rule, preserving the current
  precedence at `runtime/retry.py:24-25` so an exhausted scope still reports
  `"revision limit reached"`.
- `revision(scope, set())` is a caller error: an empty failed-check set means the unit
  passed, and a passing attempt must not consume a revision. Raise `ValueError`. This is a
  deliberate behavior change from the current code, which silently treats `set()` as
  non-narrowing, and it invalidates the existing `test_revision_limit` fixture.

### 4. Replace the controller's divergent copy with the corrected tracker

- In `runtime/controller.py:161-203`, delete the inline `failures_seen` dict and use one
  `RetryTracker` built from `self.limit_policy`, catching `RetryLimit` and re-raising the
  existing `RuntimeFailure("REPEAT-FAILURE", injected)` so the failure id, terminal state,
  and gate expectations do not move.
- The scope key must be the unit being worked on. `simulate()` iterates *states*, not
  units, so this scope has no existing referent: use the single unit id when `lab_id`
  selects one, and otherwise a stable explicit run-level scope constant. Do not silently
  key on state — that would preserve D1 under a new name.
- Behavioral equivalence is required for the one existing test that exercises this path,
  `tests/runtime/test_controller.py:102-114`, which injects `"CHECK-X"` at every state and
  must still raise. Consecutive-repeat semantics preserve that outcome; verify it rather
  than assume it, and record in the result document any injection sequence whose outcome
  changes.

### 5. Plumb the parsed limit overrides through to the runtime

- Pass the parsed limit values from `runtime/run_curriculum.py:39-64` into the runtime so
  `--repeat-failure-threshold` and `--max-lab-revisions` actually bind, keeping the
  generated-flag mechanism at `:30-34` and the YAML values as defaults.
- Overrides apply to the tracker's construction only. Do not rewrite `policy/limits.v1.yaml`,
  do not change any declared value, and do not add flags the policy does not declare.
- This is included because without it the corrected threshold is unreachable end to end and
  step 6's cross-unit regression cannot be driven from the CLI. If plumbing proves to
  require changes beyond `run_curriculum.py` and the runtime constructor, stop and report
  rather than widening.

### 6. Add regression tests that fail against today's code

Rewrite `tests/runtime/test_retry.py` for the new API and add, at minimum:

- **Cross-unit independence (the reported defect):** unit `u1` hits `{A,B}` twice and
  raises; unit `u2` then hits `{A,B}` twice and must reach its own second attempt before
  raising, proving `u2` was never charged for `u1`.
- **Cross-unit independence for `revisions` and `used`:** exhaust each per-unit budget on
  `u1` and prove `u2` has a full budget.
- **Consecutiveness:** `{A}` → `{B}` → `{A}` must not raise at `repeat_threshold=2`.
- **Narrowing:** `{A,B}` → `{A}` → `{A}` raises on the third call, matching the current
  `test_repeat_failure_limit` outcome under the new API.
- **Scope is mandatory:** calling `revision` or `retry` without a scope is a `TypeError`.
- **Empty set:** `revision(scope, set())` raises `ValueError`.
- **Release:** a released scope restarts with a full budget, and releasing an unknown
  scope is a no-op.

## Verification sequence

1. Run the new `tests/runtime/test_retry.py` against the *unmodified* `runtime/retry.py`
   first and require the cross-unit tests to fail. A regression test that passes before the
   fix proves nothing.
2. Apply the fix; run the full runtime unit suite.
3. Run `tests/check_meta_prompt.py` and phase 4 and 5 gates; compare per gate id against
   the step 1 baseline.
4. Run `--test-static` and `--test-simulated-all` and require unchanged deterministic unit
   ordering, coverage, and terminal state.
5. Drive `--repeat-failure-threshold` from the CLI and prove the bound value, not the YAML
   default, governs the run.
6. Audit the final Git delta against the baseline and the step 1 allowlist.

## Acceptance criteria

- A scope that exhausts any budget cannot affect a different scope's budget, proven by
  test for all three of `used`, `revisions`, and repeat failures.
- `scope` cannot be omitted from either budget method.
- The narrowing baseline is owned by the tracker; no caller supplies `previous`.
- Repeat detection is consecutive and per scope, and its threshold and revision limit
  resolve from `policy/limits.v1.yaml` with CLI overrides binding.
- `runtime/controller.py` has exactly one repeat-failure implementation, the shared one,
  and still raises `RuntimeFailure("REPEAT-FAILURE", ...)` with an unchanged failure id.
- The new regression tests fail before the fix and pass after it.
- Phase 4 and 5 gates, contract checks, static and simulated runs show no new or worsened
  result against the captured baseline.
- The final delta touches only allowlisted paths and leaves all pre-existing dirty-worktree
  work byte-identical.

## Stop conditions and result

Stop on: a collision with pre-existing staged or unstaged user work; a required change
outside the allowlist; a gate that newly fails and cannot be repaired within scope; or a
controller behavior change that cannot be shown equivalent for existing injections. Do not
respond to a failing gate by relaxing a policy value, widening the allowlist, or making
`scope` optional.

Write `plans/_eval_rtd_bl/retry_scope.result.v1.md` with the baseline, changed paths, the
pre-fix failing-test evidence, test ids and exit codes, per-gate comparison, CLI-override
evidence, and any remaining failures. Append the outcome to `plans/_eval_rtd_bl/plans.log.md`;
never edit an earlier entry.
