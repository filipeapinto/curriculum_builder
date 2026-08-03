# Retry Scope Planning Workflow — Final QA Audit v1

## Verdict

**PASS — 0 Critical, 0 High remaining.** The package is internally consistent, all four
High findings are materially remediated, and the plan targets the code that actually
enforces the rule rather than only the class named in the report.

## High-finding remediation map

| QA finding | Closed by |
| --- | --- |
| 1 — no production caller; controller copy diverges | Plan D5 and step 4; `RS-T05`; prompt GOAL item 3 |
| 2 — `revisions` and `used` share the defect | Plan D2 and step 2; `RS-T02`; prompt GOAL item 1 |
| 3 — CLI limit overrides are discarded | Plan D6 and step 5; `RS-T06`; prompt GOAL item 4 |
| 4 — optional scope; no controller unit referent | Plan step 2 (required, non-defaulted `scope`) and step 4 (unit id or named run constant, never state); `RS-T04`, `RS-T05`; prompt GOAL items 1 and 3 |

## Evidence

- **Grounded in the real code.** Every defect cites a line that was read:
  `runtime/retry.py:12-31`, `runtime/controller.py:183,196-203`,
  `runtime/run_curriculum.py:30-34`, `policy/limits.v1.yaml:21,24,50-52`,
  `tests/runtime/test_retry.py`, `tests/runtime/test_controller.py:102-114`. The claim that
  `RetryTracker` has no production caller was verified by a repository-wide search for the
  identifier, which returned only `runtime/retry.py` and its unit test.
- **The reported symptom is correctly located and correctly generalized.** The user
  described `failures` blocking later units. The plan reproduces that diagnosis and shows
  that `revisions` and `used` fail identically, that the narrowing rule is caller-owned,
  and that the live enforcement path is a second implementation. The scope of the fix grew
  only where the same root cause reaches; no unrelated cleanup was added.
- **Test cross-references resolve.** `RS-T02`–`RS-T05` map to plan steps 2, 3, 4 and 6;
  `RS-T06` maps to step 5; `RS-T07`–`RS-T09` map to the plan's verification sequence and
  allowlist. The prompt's TEST section enumerates `RS-T00`–`RS-T09` in the same order with
  the same stop semantics. Every test id referenced in the prompt exists in the test plan,
  and every test in the test plan is referenced by the prompt.
- **The regression test is falsifiable.** `RS-T01` requires the new tests to fail against
  the unmodified module before any edit, and makes that recorded failure a precondition for
  claiming success. This is the check that distinguishes a real fix from a rewritten test,
  and it is enforced in the plan, the test plan, and the prompt's LOOP.
- **Behavior changes are declared rather than absorbed.** Three intentional changes carry
  explicit tests: consecutive-only repeat counting (`RS-T03`), `ValueError` on an empty
  failed-check set (`RS-T04`), and the alternating-injection controller outcome, which
  `RS-T05` requires to be asserted and recorded rather than silently accepted. The
  `RetryLimit` message strings and the `REPEAT-FAILURE` failure id are pinned so log and
  gate expectations do not move.
- **Worktree safety is consistent across all four artifacts.** The plan, test plan, and
  prompt each state the same allowlist and the same prohibition on staging, stashing,
  resetting, restoring, cleaning, or overwriting the dirty worktree, which currently holds
  substantial unrelated staged user work.
- **Out-of-scope items are recorded, not fixed.** `runtime/controller.py:203` advancing to
  the next state instead of re-attempting the failed one, and lateral non-narrowing thrash
  (already owned by `policy/limits.v1.yaml:52`
  `complexity_without_progress_cycles`), appear in the plan, the QA notes, and the prompt as
  explicit non-goals.

## Residual risks, accepted

- **Step 5 is the widest part of the change.** Plumbing the parsed limits touches a call
  path with no current test coverage of its own. It is bounded by an explicit stop
  condition and by `RS-T06`'s requirement that both policy files stay byte-identical, but
  it is the item most likely to trigger a scope stop during execution.
- **`release()` permits use-after-release.** A scope released and then reused restarts with
  a full budget. `RS-T04` tests the intended semantics; nothing prevents a future caller
  from releasing a scope it will reuse. Acceptable now, since the only caller is the
  controller and it releases nothing.
- **`simulate()` has no per-unit loop.** The controller's scope key is therefore the
  selected unit or a run-level constant, not a genuine per-unit budget. The correction makes
  the tracker ready for a per-unit loop; it does not create one. Any future authoring loop
  must pass its own unit id, and the required `scope` parameter is what forces it to.
