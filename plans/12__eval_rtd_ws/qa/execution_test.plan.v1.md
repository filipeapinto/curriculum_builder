# RetryTracker Per-Unit State Reset — Execution Test Plan v1

## Purpose and boundary

Test `plans/_eval_rtd_ws/_eval_rtd_ws.plan.v1.md` as it executes, without
re-deciding it. Every test below either captures evidence the plan requires or
checks a claim the plan makes; none of them re-derive the fix or extend its
scope.

Evidence goes in exactly two places: `plans/_eval_rtd_ws/_eval_rtd_ws.result.v1.md`
(the per-test observations, verbatim command output where the plan asks for it)
and an appended entry in `plans/_eval_rtd_ws/plans.log.md`. Nothing else is
written outside `runtime/retry.py` and `tests/runtime/test_retry.py`.

What these tests must never do:

- Run `git commit`, `git checkout`, `git restore`, `git stash`, `git reset`, or
  `git clean` on any path, for any reason. This repository's worktree is
  legitimately dirty with the user's uncommitted work; that work outranks every
  check here. A test that would only pass by reverting a dirty path fails
  instead, and is reported.
- Edit any file other than `runtime/retry.py`, `tests/runtime/test_retry.py`,
  the result file, and the log. In particular no file under `policy/`,
  `schemas/`, or `tests/gates/`, and no `runtime/` module other than `retry.py`.
- Repair any gate that was already FAIL or BLOCKED at the `RTD-T00` capture.
  Those are pre-existing and out of scope.
- Modify or delete the three pre-existing tests in `tests/runtime/test_retry.py`.

`RTD-T00` through `RTD-T04` are read-only with respect to the repository: they
observe and reproduce, they do not change `runtime/retry.py`. Repository
mutation begins at `RTD-T05`.

## Ordered tests

### RTD-T00 — Read-only baseline capture

Covers plan steps 0.3, 0.4 and 0.5. Before any edit, capture and record verbatim
into the result file:

- `python3 -m unittest discover -s tests/runtime -t .` — the test count and
  status line.
- `git status --porcelain` — the complete output, as **the baseline snapshot**
  every later delta is measured against.
- `./tests/run_gates.sh 5` — the complete per-gate verdict list, which becomes
  the authoritative gate baseline. Judge nothing on this command's exit status;
  it exits non-zero whenever any gate is red.

Pass requires all three captured and recorded, and requires the test baseline to
read `Ran 47 tests` / `OK`. A red test baseline is a stop condition, not
something to work around: report it and halt. The porcelain snapshot must show
`runtime/retry.py` and `tests/runtime/test_retry.py` with code `A ` — staged
additions, worktree clean. The gate capture must be complete; recording only the
gates that happen to be red loses the PASS entries that later comparisons need.

Do not compare the captured gate list against the informational block in plan
step 0.5 and treat a difference as a failure. That block is orientation only;
this capture is the baseline.

### RTD-T01 — Fail-fast: the defect is still present as described

Covers plan step 0.1. Read `runtime/retry.py` and confirm `RetryTracker.__init__`
assigns `self.failures: dict[tuple[str, ...], int] = {}`, `self.revisions = 0`,
and `self.used = {"malformed": 0, "transient": 0}`, and that no method in the
class reassigns or clears any of those three after construction.

Pass means the baseline matches. If `RetryTracker` already exposes a
unit-boundary method, or its state attributes differ from that description, this
test **fails as a stop condition**: the plan must be re-scoped, not applied on
top. Record which of the two it was.

### RTD-T02 — Fail-fast: no production call site exists

Covers plan step 0.2. Search the repository for `RetryTracker`, excluding
`.git/`, `node_modules/`, and `__pycache__/`. Record the full hit list in the
result file, classified into production code versus planning/eval material.

Pass means the only non-planning matches are `runtime/retry.py` and
`tests/runtime/test_retry.py`. If a production instantiation now exists, this
test **fails as a stop condition** — that call site determines whether the
tracker is built per run or per unit, which decides which fix is correct.

### RTD-T03 — Defect reproduction on a scratch copy

Covers plan verification step 4(a). Outside the repository (e.g. `/tmp/rtd/`),
copy the unmodified `runtime/retry.py` and drive one `RetryTracker` instance
through two simulated units: record a non-narrowing failed-check set for unit 1,
then submit unit 2's first `revision()` with the same set.

Pass means unit 2's first revision raises `RetryLimit` off unit 1's inherited
`failures` entry. Record the observed traceback or exception message verbatim.

If carryover does **not** reproduce, this is a stop condition: the defect is not
what the plan describes and the fix would be unverified against any real
symptom. This test is what actually evidences the defect — `RTD-T04` does not
substitute for it.

### RTD-T04 — Method-absence check against the unmodified source

Covers plan verification step 4(b). Still before any edit to
`runtime/retry.py`, write tests 3.1–3.6 exactly as plan step 3 specifies and run
them against the unmodified source.

Pass requires exactly this shape: tests 3.1–3.5 each error with
`AttributeError: 'RetryTracker' object has no attribute 'begin_unit'`, and test
3.6 **passes**. Five errors and one pass. Test 3.6 never calls `begin_unit`, so
its passing here is by design and is part of the pass condition, not a defect.

Record the observation as what it is. A result file claiming all six new tests
errored with `AttributeError` is a false record even though it sounds tidier.

### RTD-T05 — Phase 2: the unit boundary is implemented as specified

Covers plan step 2. After editing `runtime/retry.py`, confirm each of:

- `__init__` gained `self.unit_id: str | None = None` and no existing parameter,
  default, or attribute name changed.
- `begin_unit(self, unit_id: str) -> None` exists and matches step 2.2: early
  return when `unit_id == self.unit_id`, then set `self.unit_id`, rebuild
  `self.used` from `self.limits` keys, zero `self.revisions`, empty
  `self.failures`.
- `self.used` is rebuilt from `self.limits` rather than from a second literal
  `{"malformed": 0, "transient": 0}` (step 2.3).
- A short comment states why the early return is load-bearing — that a caller
  invoking `begin_unit` once per attempt must not silently refill the budget it
  is spending (step 2.2).
- No `unit_id` validation beyond the above was added (step 2.4).
- The bodies of `retry()` and `revision()` are byte-for-byte unchanged from
  baseline (step 2.5). Diff them explicitly; do not eyeball this.

Pass requires all six. The `retry()`/`revision()` check is the one that matters
most: a fix that loosens either body to make a test pass is the wrong fix, and
plan step 2.5 forbids it.

### RTD-T06 — Phase 3: the six new tests exist and the three old ones are intact

Covers plan step 3. Confirm `tests/runtime/test_retry.py` now contains
`test_begin_unit_resets_repeat_failures`, `test_begin_unit_resets_revision_count`,
`test_begin_unit_resets_retry_budget`, `test_begin_unit_is_idempotent_within_a_unit`,
`test_begin_unit_preserves_configuration`, and
`test_tracker_without_begin_unit_is_unchanged`, all in the existing `RetryTests`
class in the file's existing `unittest` style.

Confirm by diff that the three pre-existing tests are unmodified and undeleted.

Pass requires nine tests in the file, six new and three untouched. Specifically
check that 3.1 asserts the counter **restarts** — `repeat_threshold - 1` further
non-narrowing submissions succeed and the `repeat_threshold`-th raises — and not
that the set "can be submitted `repeat_threshold` times before raising". The
second phrasing fails against the correct fix and tempts an implementer into
loosening `revision()`.

### RTD-T07 — Post-change suite

Covers plan step 4.1 and verification step 5. Run
`python3 -m unittest discover -s tests/runtime -t .`

Pass means `Ran 53 tests` and `OK`, with zero failures and zero errors — the 47
baseline plus the six new tests. Record the count and status verbatim.

### RTD-T08 — Acceptance: reset semantics and configuration preservation

Covers the plan's first three acceptance criteria, checked as behaviour rather
than as code shape. Against the patched source, confirm:

- `begin_unit` with an id different from the current one sets `self.failures` to
  `{}`, `self.revisions` to `0`, and every value in `self.used` to `0`.
- `begin_unit` with the id already in force changes no counter.
- `self.limits`, `self.revision_limit`, and `self.repeat_threshold` are not
  mutated by `begin_unit`.

Pass requires all three. `RTD-T06` proves the tests were written; this test
proves the behaviour they assert is the behaviour the acceptance criteria name.

### RTD-T09 — Regression: a tracker that never calls `begin_unit` is unchanged

Covers plan step 2.5. Confirm that calling `revision()` or `retry()` without
ever calling `begin_unit()` behaves exactly as it did at baseline — one implicit
unit with `unit_id` of `None`.

Pass means the three pre-existing tests pass unmodified (already implied by
`RTD-T07`, checked here as its own claim) and test 3.6 passes. This is the
negative case: the fix must add a boundary, not change what happens when nobody
uses it.

### RTD-T10 — Porcelain delta against the RTD-T00 snapshot

Covers plan verification step 6 and its acceptance criterion. Run
`git status --porcelain` after the change and diff it against the `RTD-T00`
baseline snapshot.

Pass means the **only** difference is that `runtime/retry.py` and
`tests/runtime/test_retry.py` moved from code `A ` to `AM`. No other entry may
appear, disappear, or change status.

If any other entry changed, uncommitted work was disturbed: report it
immediately and do not silently correct it. Confirm explicitly that
`policy/limits.v1.yaml`, `schemas/limits.schema.v1.json`,
`runtime/run_curriculum.py`, `runtime/session_bridge.py`, and
`tests/gates/fr_p4_policy_schemas.py` still carry their pre-existing uncommitted
changes. This is a delta assertion, never a clean-tree assertion — the baseline
is legitimately dirty and must stay exactly as dirty as it was.

### RTD-T11 — Gate diff against the RTD-T00 capture

Covers plan step 4.2 and verification step 7. Re-run `./tests/run_gates.sh 5`
and diff the per-gate verdicts against the verdicts captured in `RTD-T00`.

Pass means no gate moved from PASS to FAIL **and** none moved from PASS to
BLOCKED. A gate can be knocked out by a newly failing dependency without itself
turning red, so BLOCKED counts as a regression.

Any gate FAIL or BLOCKED in the `RTD-T00` capture that is still FAIL or BLOCKED
matches the recorded baseline and is a pass. Do not repair it. Judge this test
on the per-gate diff, never on the command's exit status.

### RTD-T12 — Change scope containment

Covers the plan's scope-boundary acceptance criteria. Confirm from the
`RTD-T10` porcelain delta and from `git diff` that this work edited only
`runtime/retry.py` and `tests/runtime/test_retry.py`.

Pass means no module under `runtime/` other than `retry.py` was edited, no file
under `policy/` or `schemas/` was edited, and no path in the `RTD-T00` snapshot
was reverted, restored, stashed, reset, or cleaned.

### RTD-T13 — Result file and log completeness

Covers the plan's "Stop conditions and result" section. Confirm
`plans/_eval_rtd_ws/_eval_rtd_ws.result.v1.md` exists and records: the baseline
test count and status; the `RetryTracker` search result; the verbatim `RTD-T00`
porcelain snapshot; the `RTD-T00` per-gate baseline verdicts naming **every**
gate captured as FAIL or BLOCKED, not a pre-selected subset; the reset-scope
decision from plan step 1.2 and the recorded ambiguity from step 1.3; the
`RTD-T03` reproduction output and the `RTD-T04` observation in its true shape
(five `AttributeError`s from tests 3.1–3.5, test 3.6 passing); the final test
count and status; the post-change porcelain with its diff against the baseline;
the post-change per-gate verdicts diffed against the baseline; and any remaining
failure.

Confirm the execution outcome was appended to `plans/_eval_rtd_ws/plans.log.md`
as a new entry, never by editing an existing one.

Pass requires every listed item present and each one true against what was
actually observed. A result file that records a tidier story than the run
produced fails this test.

## Final audit and pass rule

The package passes only when `RTD-T00` through `RTD-T13` have all passed. There
is no partial pass and no "passed except".

The stop-condition tests are not optional gates to route around. If `RTD-T01`,
`RTD-T02` or `RTD-T03` fails, the correct outcome is to halt and report — the
plan's premise no longer holds, and continuing would implement a fix for a
defect that isn't there or isn't shaped as described. Record which stop
condition fired and stop; do not adapt the plan mid-run.

A blocked or partial state must be reported as exactly that. State which test
ids passed, which failed, which never ran, and why. Specifically:

- Pre-existing red gates carried from the `RTD-T00` capture are reported as
  unchanged baseline state, not as this change's failures, and not as a clean
  phase 5.
- `FR-P0-CLEAN` will still be red afterwards; it fails by construction for any
  uncommitted change. Saying so is honest reporting, not an excuse.
- If a check would only go green by editing something outside
  `runtime/retry.py` and `tests/runtime/test_retry.py`, or by touching a path
  that was already dirty at baseline, that check fails and is reported. The
  user's uncommitted work outranks every test here.

Claiming completion requires every applicable test id above to have passed, with
its evidence in the result file.
