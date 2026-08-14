# Runtime Operations Documentation — Execution Test Plan v1

## Purpose and boundary

Test `plans/28_runtime_operations_docs/28_runtime_operations_docs.plan.v1.md`
without implementing it. Evidence for each test goes under
`plans/28_runtime_operations_docs/results/evidence/<test-id>/` (created by the
test run, not by this document). Tests must never write to `docs/`,
`readme.md`, or any runtime/policy/schema/test path — they read and assert
only. Tests must never modify or delete anything under
`plans/27_langgraph_curriculum_factory_remediation/` (it is another plan
package's live evidence).

## Availability stages

Plan 27 has not reached a terminal state as of this writing (`execution_package_v2/results/v7/`
contains only N00–N30 results). That means:

- `ROD-T00` through `ROD-T03` (baseline capture and the step-0 gate-logic
  checks) can run now, against the current, pre-terminal repository state.
- `ROD-T04` through `ROD-T08` (the actual documentation-content tests) cannot
  run for real today — Plan 27 hasn't produced a terminal N90 result, so
  there is no live implementation to test. They are written now so the
  package is ready, and must be executed for real only after Plan 27
  reaches `ACTIVATED` or `REMEDIATION_VERIFIED_NOT_ACTIVATED`. Until then,
  running them is only meaningful as a dry run against a synthetic/fixture
  N90 result (see `ROD-T04`'s note) — never against the live
  `plans/27_.../results/v7/` directory, since that would require fabricating
  a terminal outcome Plan 27 has not actually reached.
- `ROD-T09` (final audit and pass rule) applies only once `ROD-T04`-`ROD-T08`
  have actually run against a real terminal state — not against the dry run.

## Ordered tests

### ROD-T00 — Baseline capture

Capture, read-only: `git status --porcelain` (confirm clean or record what's
dirty before any test touches the tree), the current contents of
`docs/how_it_works.md`, and whether `docs/runtime_operations_manual.md` (or
any file matching `docs/*operations*`) already exists. This is the
before-picture every later test's diff is measured against.

### ROD-T01 — Step-0 path and field existence

Confirm `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml`
exists, its `result_pattern` field resolves to
`.../results/v7/{node_id}.result.v1.json`, and that no
`implementation.graph.v8.yaml` (or higher) exists directly under
`execution_package_v2/` (only under `deprecated/`, if at all). Pass requires
all three.

### ROD-T02 — Step-0 correctly stops pre-terminal

Confirm `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N90_REQUIREMENTS_FINAL_AUDIT.result.v1.json`
does not currently exist (or, if it does by the time this runs, that its
`outcome` is `BLOCKED`). Then run the plan's step-0 procedure by hand and
confirm it reports "stop" and identifies the correct missing/blocking
condition. Pass requires the procedure to stop, not proceed, given today's
state.

### ROD-T03 — No writes occur when step 0 stops

Given `ROD-T02`'s stop result, confirm no file under `docs/` or `readme.md`
was created or modified, and that a stop is the only outcome recorded (no
partial draft left behind). Compare against `ROD-T00`'s baseline.

### ROD-T04 — Step-0 gate opens correctly on a real terminal result (post-Plan-27 only)

Once Plan 27 has actually reached a terminal state: confirm
`results/v7/N90_REQUIREMENTS_FINAL_AUDIT.result.v1.json` exists, `outcome`
is `PASSED`, and `terminal_recommendation` is `ACTIVATED` or
`REMEDIATION_VERIFIED_NOT_ACTIVATED`. Confirm the implementation's step-0
run reports "proceed" and records which terminal was found. (Dry run note:
before Plan 27 concludes, this test may only be exercised by hand-tracing
the plan's logic against a hypothetical result — it must not be marked
passed from a hand-trace; only a run against a real N90 result counts.)

### ROD-T05 — Pre-final-write recheck fires on a version change

After a successful `ROD-T04` proceed, but before the final documentation
write, verify the implementation re-runs the step-0 graph-currency check
(not just the terminal-value check). This can be tested by temporarily
creating a throwaway `implementation.graph.v8.yaml` stub file directly under
`execution_package_v2/` (outside git tracking, deleted immediately after the
test) and confirming the implementation detects it and stops instead of
publishing. Restore repository state exactly afterward; this test must leave
zero trace.

### ROD-T06 — `docs/how_it_works.md` content matches the found terminal

If `ACTIVATED`: confirm the rewritten document no longer contains the
"zero units have been generated" / "does not yet contain the runtime
controller" claims, and that it names `runtime/langgraph_factory` and the
actual provider routing (Claude generate/repair, Codex judge) with citations
to real files current at write time. If `REMEDIATION_VERIFIED_NOT_ACTIVATED`:
confirm the document states plainly, near the top, that the system is
verified but not activated, and names the specific N90-recorded reason.

### ROD-T07 — Superseded content preserved, not deleted

Confirm the pre-rewrite content of `docs/how_it_works.md` (captured in
`ROD-T00`) was moved into `docs/deprecated/` rather than discarded, following
the existing convention already used for that directory (spot-check: an
existing file under `docs/deprecated/` from before this plan ran must still
be present and untouched).

### ROD-T08 — Operations manual grounded in real CLI/config

Confirm `docs/runtime_operations_manual.md` (or its recorded alternate path
from the result file) exists and that every flag, config path, or behavior
it documents for `runtime/run_curriculum.py` matches what
`python3 -m runtime.run_curriculum --help` (or direct inspection of its
argument parser) actually reports at test time. Confirm the
BLOCKED/NOT_AVAILABLE recovery guidance cites a real code path rather than
an invented one; if the document says no recovery procedure exists for a
given failure mode, confirm that's true rather than an omission.

### ROD-T09 — Final audit and pass rule

The package passes only if: `ROD-T00`-`ROD-T03` pass against the current
pre-terminal repository state, AND, after Plan 27 reaches a terminal state,
`ROD-T04`-`ROD-T08` all pass against the real (not dry-run) implementation
output, with `ROD-T05` leaving zero trace in the repository. If Plan 27 has
not yet reached a terminal state, the honest report is "gate tests pass;
content tests not yet executable" — never a claim that the documentation
itself has been verified before it has actually been written and checked.
