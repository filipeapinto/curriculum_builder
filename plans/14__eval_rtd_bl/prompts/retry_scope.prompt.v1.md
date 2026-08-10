# GOAL

Implement `plans/_eval_rtd_bl/retry_scope.plan.v1.md` exactly, using
`plans/_eval_rtd_bl/qa/execution_test.plan.v1.md` as the acceptance procedure.

`RetryTracker` in `runtime/retry.py` keeps three retry budgets — `used`, `revisions`, and
the repeat-failure counter — in run-lifetime state that is never scoped or reset. One
unit's exhausted budget blocks every later unit. Make scope explicit and structurally
unavoidable, bring the one divergent live copy of the rule onto it, and make the
policy-declared limits reachable so the correction is provable end to end.

Do exactly this and nothing more:

1. **`runtime/retry.py`** — replace the shared counters with one per-scope record holding
   `used`, `revisions`, the repeat counter, and the previous failed-check set. The API
   becomes `retry(kind, *, scope)`, `revision(scope, failed_checks)`, and `release(scope)`.
   `scope` is **required and non-defaulted** on both budget methods; there is no shared
   fallback bucket. Delete the `previous` parameter — the tracker owns its own baseline.
   Keep the constructor parameters, the `RetryLimit` class, and both existing message
   strings unchanged.

2. **Repeat rule, per scope** — no previous set, or `failed` a strict subset of it, resets
   the counter to 1 for the newly observed set; `failed` equal to the previous set
   increments it; raise `RetryLimit("repeated failure set did not narrow")` at
   `repeat_threshold`. A set that changes without narrowing resets the counter. Check
   revision-limit exhaustion first, preserving today's precedence at `runtime/retry.py:24-25`.
   `revision(scope, set())` raises `ValueError` and consumes no revision. Lateral thrash is
   out of scope — `policy/limits.v1.yaml:52` already owns it.

3. **`runtime/controller.py:183,196-203`** — delete the inline
   `failures_seen: dict[tuple[str, ...], int]` and use one `RetryTracker` built from
   `self.limit_policy`, catching `RetryLimit` and re-raising the existing
   `RuntimeFailure("REPEAT-FAILURE", injected)` unchanged. The scope key is the selected
   unit id when `lab_id` is given and a named run-level constant otherwise. **Never key on
   state name** — that is the original defect renamed.

4. **`runtime/run_curriculum.py:39-64`** — pass the limit values already parsed at `:30-34`
   into the runtime so `--repeat-failure-threshold` and `--max-lab-revisions` actually
   bind, with the YAML as defaults. Change no declared policy value and add no flag the
   policy does not declare.

5. **Tests** — rewrite `tests/runtime/test_retry.py` for the new API with the cases listed
   in `RS-T02` through `RS-T04`, and update `tests/runtime/test_controller.py` assertions
   per `RS-T05`.

The allowlist is exactly: `runtime/retry.py`, `runtime/controller.py`,
`runtime/run_curriculum.py`, `tests/runtime/test_retry.py`,
`tests/runtime/test_controller.py`, `tests/runtime/test_run_curriculum.py`, and this
workflow's artifacts under `plans/_eval_rtd_bl/`. A required change outside it is a stop.

The worktree is dirty with extensive unrelated staged user work. Never stage, stash, reset,
restore, clean, or overwrite it. Do not fix `runtime/controller.py:203`, which advances to
the next state after an injected failure instead of re-attempting it — record it as an
adjacent defect and leave it.

# TEST

Follow `plans/_eval_rtd_bl/qa/execution_test.plan.v1.md`, in order, with evidence written
to an external root and never into the repository.

1. **RS-T00** — capture and hash the read-only baseline: git status and both diffs,
   allowlisted-path hashes, the runtime unit suite, phase 4 and 5 gates,
   `check_meta_prompt.py`, `--test-static`, and one `--test-simulated-all` run.
2. **RS-T01 — do this before editing `runtime/retry.py`.** Write the new tests and run them
   against the unmodified module. The cross-unit repeat, cross-unit `revisions`, cross-unit
   `used`, consecutiveness, and mandatory-scope tests **must fail**. Record the failure
   output. If any of them passes here, the test is wrong; rewrite it. Only then edit
   `runtime/retry.py`.
3. **RS-T02** — per-scope isolation for all three budgets, including interleaved calls
   producing the same outcomes as separate runs.
4. **RS-T03** — narrowing and consecutiveness, message strings byte-identical to baseline.
5. **RS-T04** — API contract: `TypeError` without a scope and for `previous`, `ValueError`
   on an empty set with the budget unchanged, `release` semantics, and per-scope record
   isolation asserted by identity.
6. **RS-T05** — no `failures_seen` remains; `tests/runtime/test_controller.py:102-114`
   still raises with failure id exactly `REPEAT-FAILURE`; the alternating-injection outcome
   is asserted and recorded; the scope key is the unit id or the run-level constant.
7. **RS-T06** — `--repeat-failure-threshold` and `--max-lab-revisions` bind from the CLI,
   the YAML default governs when no flag is given, and both policy files are byte-identical
   to baseline.
8. **RS-T07** — phase 4 and 5 gates plus `check_meta_prompt.py` compared **by gate id**
   against baseline; no new or worsened result.
9. **RS-T08** — unit suite, `--test-static`, `--test-simulated-all`: unchanged unit
   ordering and `unit_ids`, terminal `ACCEPTED` with `simulated-controller-only` coverage,
   clean log audit, and `PRECONDITION-OUTPUT-ROOT-EXISTS` still fires without mutating the
   existing root.
10. **RS-T09** — final delta audit: nothing staged, pre-existing bytes outside the
    allowlist identical, every changed path allowlisted, no unrelated mode, symlink, or
    hash change.

RS-T01's recorded failure is required evidence. A run that cannot show the new tests
failing before the fix has not proven the defect and may not claim success.

# LOOP

Work the tests in order. On a failure, record the test id, command, exit code, evidence
hashes, and the narrow root cause; change only the in-scope artifact that caused it; then
rerun RS-T02 through RS-T05 and every later test whose evidence may have changed. Continue
until RS-T01 is evidenced as failed-before-fix and RS-T02 through RS-T09 all pass.

Do not waive, reorder, or weaken a test. Never respond to a failure by making `scope`
optional or defaulted, keying the controller on state name, relaxing a value in
`policy/limits.v1.yaml`, widening the allowlist, deleting or rewriting a failing assertion,
or touching pre-existing user work. Stop and report on a collision with staged or unstaged
user work, a required change outside the allowlist, a controller behavior change that
cannot be shown equivalent for existing injections, or a gate that newly fails and cannot
be repaired in scope.

Write `plans/_eval_rtd_bl/retry_scope.result.v1.md` with the baseline, the RS-T01 pre-fix
failure evidence, changed paths, test ids and exit codes, per-gate comparison, CLI-override
evidence, the alternating-injection outcome, remaining failures, and the final verdict.
Append — never rewrite — the outcome to `plans/_eval_rtd_bl/plans.log.md`. Claim completion
only when every test has passed and the final delta matches the allowlist.
