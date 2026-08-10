# Retry Scope Correction — Execution Test Plan v1

## Purpose and boundary

Test `plans/_eval_rtd_bl/retry_scope.plan.v1.md` as executed. This document does not
implement it.

Evidence goes to an external root, `/private/tmp/retry-scope-test-<UTC>/`, never into the
repository. The worktree is dirty with substantial unrelated staged user work: no test may
stage, stash, reset, restore, clean, or rewrite it. Runtime output goes to a fresh
test-owned child of `outputs/`, removed only after its assertions complete.

## Ordering rule

`RS-T00` and `RS-T01` run **before any edit to `runtime/retry.py`**. `RS-T01` is the only
test whose required outcome is a failure, and it is the test that gives every later test
meaning. `RS-T02` through `RS-T09` run after the fix, in order.

## Ordered tests

### RS-T00 — Read-only baseline capture

Create the external evidence root and capture, hashing each artifact:

1. `git status --porcelain=v2 -z --untracked-files=all`, `git diff --binary`, and
   `git diff --cached --binary`.
2. The index object id and working-tree SHA-256 for every allowlisted path:
   `runtime/retry.py`, `runtime/controller.py`, `runtime/run_curriculum.py`,
   `tests/runtime/test_retry.py`, `tests/runtime/test_controller.py`,
   `tests/runtime/test_run_curriculum.py`.
3. `python3 -m unittest discover -s tests/runtime -v`, with exit code and per-test outcome.
4. `./tests/run_gates.sh 4` and `./tests/run_gates.sh 5`, preserving generated JSON, exit
   codes, and per-gate states.
5. `python3 tests/check_meta_prompt.py`.
6. `python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit --test-static`.
7. One `--test-simulated-all` run into a fresh explicit test-owned output root, preserving
   `simulated_acceptance.json` and the terminal state.

Repository-read-only apart from the test-owned output root, which is removed after its
evidence is copied out. Hash the whole bundle.

### RS-T01 — Pre-fix regression proof (required failure)

Write the new `tests/runtime/test_retry.py` and run it against the **unmodified**
`runtime/retry.py`. Required outcome:

- The cross-unit repeat-failure test fails, and its failure message shows the second unit
  raising `RetryLimit` on an attempt that should still have budget.
- The cross-unit `revisions` and cross-unit `used` tests fail for the same reason.
- The consecutiveness test (`{A}` → `{B}` → `{A}` must not raise) fails.
- The mandatory-scope test fails, because the current signature accepts the call.

A new regression test that passes before the fix proves nothing and must be rewritten, not
waived. Record the exact failure output externally; it is the evidence that the reported
defect existed and that the test detects it. Only after this passes-by-failing may
`runtime/retry.py` be edited.

### RS-T02 — Per-scope budget isolation

After the fix, for each of the three budgets independently:

- **Repeat failures:** exhaust `u1` with the identical set at `repeat_threshold`, assert
  `RetryLimit`; then run `u2` through the same sequence and assert it raises only on its
  own final attempt, never earlier.
- **Revisions:** exhaust `revision_limit` on `u1`, assert `"revision limit reached"`, then
  assert `u2` accepts a full `revision_limit` count.
- **Malformed/transient retries:** exhaust each kind on `u1`, then assert `u2` has a full
  budget for both kinds.

Also assert the negative direction: interleaving `u1` and `u2` calls produces the same
per-scope outcomes as running them separately. Order independence is the property the
original defect violated.

### RS-T03 — Narrowing and consecutiveness semantics

- `{A,B}` → `{A}` → `{A}` raises on the third call, matching the pre-fix
  `test_repeat_failure_limit` outcome under the new API.
- `{A}` → `{B}` → `{A}` does not raise at `repeat_threshold=2`.
- `{A,B}` → `{A,C}` → `{A,B}` does not raise; lateral thrash is explicitly not this rule's
  job.
- A strict-subset narrowing resets the counter; an identical set increments it.
- Revision-limit exhaustion is reported before the repeat rule when both would fire, and
  the message is still `"revision limit reached"`.
- The `RetryLimit` message strings for both conditions are byte-identical to the pre-fix
  strings captured in `RS-T00`.

### RS-T04 — API contract

- `revision` and `retry` raise `TypeError` when called without a scope. Assert on the
  signature as well, so a later defaulted parameter fails this test.
- `previous` is not accepted by `revision`; passing it raises `TypeError`.
- `revision(scope, set())` raises `ValueError` and consumes no revision — assert the
  budget is unchanged afterward.
- `release(scope)` on a live scope restores a full budget on next use; `release` on an
  unknown scope is a no-op and raises nothing.
- Two distinct scopes never share a mutable object: mutate state for one and assert the
  other's record is untouched by identity, not only by value.

### RS-T05 — Controller has exactly one implementation, with equivalent behavior

- Assert no `failures_seen` identifier and no inline threshold comparison remains in
  `runtime/controller.py`; assert it imports and constructs `RetryTracker`.
- `tests/runtime/test_controller.py:102-114`, which injects `"CHECK-X"` at every state,
  must still raise `RuntimeFailure`, and the failure id must still be exactly
  `REPEAT-FAILURE` with the injected check as its message. Assert the failure id and
  terminal state, not merely that an exception occurred.
- Add an injection sequence that alternates two check names and assert the resulting
  outcome, then record it in the result document as an intentional semantic change if it
  differs from pre-fix behavior. Do not let a changed outcome pass silently.
- Assert the controller's scope key is the selected unit id when `lab_id` is given, and the
  named run-level constant otherwise. A scope key derived from state name fails this test.

### RS-T06 — CLI overrides actually bind

- Run `--test-simulated-all` with `--repeat-failure-threshold` set to a value different
  from `policy/limits.v1.yaml:50`, with an injected repeating failure, and assert the run
  terminates according to the **flag** value, not the YAML default.
- Repeat for `--max-lab-revisions`.
- Run once with no flag and assert the YAML default still governs.
- Assert `policy/limits.v1.yaml` and `schemas/limits.schema.v1.json` are byte-identical to
  `RS-T00`. The fix binds the declared limits; it does not change them.

### RS-T07 — Gate and contract baseline comparison

Run `./tests/run_gates.sh 4`, `./tests/run_gates.sh 5`, and
`python3 tests/check_meta_prompt.py`. Compare with `RS-T00` **by gate id**, not by
aggregate counts: a baseline `PASS` may not become `FAIL` or `BLOCKED`; a baseline failure
may not worsen; the `SKIPPED` set for the same requested phase may not change unexpectedly.
New, missing, crashed, or unrecorded gate ids fail. Preserve exit codes and generated JSON;
remove only test-owned result files.

### RS-T08 — Static and simulated execution regression

Repeat the full runtime unit suite, `--test-static`, and `--test-simulated-all` from
`RS-T00`. Require identical deterministic unit ordering and `unit_ids`, terminal
`ACCEPTED` with `simulated-controller-only` coverage, a clean log audit with no unclosed
starts, duplicate closes, or missing checkpoints/transitions, and no new failure. Use a
fresh output root; confirm the existing-output refusal
(`PRECONDITION-OUTPUT-ROOT-EXISTS`) still fires and leaves the existing root
byte-identical; then remove only the test-owned output.

### RS-T09 — Worktree and delta audit

Compare the final repository against `RS-T00`. Pass only if:

- the cached diff and every pre-existing index object are unchanged — execution staged
  nothing;
- pre-existing unstaged and untracked bytes outside the allowlist are byte-identical;
- every changed path is in the plan's step 1 allowlist, and no path was created or deleted
  outside it;
- no unrelated file mode, symlink target, or hash changed.

Save the final binary cached and working diffs plus a machine-readable allowlist comparison
to the external root.

## Final audit and pass rule

After any repair, rerun `RS-T02` through `RS-T05`, then rerun every later test whose
evidence may have changed. Pass only when `RS-T01` is evidenced as having failed before the
fix, `RS-T02` through `RS-T09` all pass, both gate phases show no regression, and the final
delta matches the allowlist.

Do not waive, reorder, or weaken a test. A failing gate is not remedied by relaxing a
policy value, widening the allowlist, or making `scope` optional. Record test ids,
commands, exit codes, artifact hashes, per-gate comparisons, and the final verdict in
`plans/_eval_rtd_bl/retry_scope.result.v1.md`, and append the outcome to
`plans/_eval_rtd_bl/plans.log.md` without editing any prior entry.
