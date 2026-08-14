# GOAL

Implement `plans/28_runtime_operations_docs/28_runtime_operations_docs.plan.v1.md`
exactly as scoped: replace the stale `docs/how_it_works.md` and add an
operations manual for the LangGraph curriculum-factory runtime
(`runtime/langgraph_factory` + `runtime/run_curriculum.py`), touching only
files under `docs/` plus `readme.md`. This document does not re-derive the
plan from scratch — read it in full before acting.

**Hard prerequisite, checked before any repository mutation:** Plan 27
(`plans/27_langgraph_curriculum_factory_remediation`) must have reached a
terminal state under its *current* graph version. Follow the plan's step 0
exactly: confirm the highest-numbered `implementation.graph.v*.yaml` directly
under `execution_package_v2/` (not under `deprecated/`) is `.v7.yaml`; confirm
that file's `result_pattern` resolves to `execution_package_v2/results/v7/{node_id}.result.v1.json`;
then read `execution_package_v2/results/v7/N90_REQUIREMENTS_FINAL_AUDIT.result.v1.json`
and confirm `outcome` is `PASSED` and `terminal_recommendation` is
`ACTIVATED` or `REMEDIATION_VERIFIED_NOT_ACTIVATED`.

If any of that fails — a newer graph version exists, the N90 result is
absent, `outcome` is `BLOCKED`, or `terminal_recommendation` is missing or
not one of those two values — **stop immediately**. Do not create or modify
any file under `docs/` or `readme.md`. Write the result file (see LOOP)
recording exactly what was found and why implementation did not proceed.
This is not a workaround-and-continue situation: there is no partial or
placeholder documentation to write instead.

# TEST

Use the ordered tests in
`plans/28_runtime_operations_docs/qa/execution_test.plan.v1.md`. Run
ROD-T00 through ROD-T09, strictly in order:

1. ROD-T00: capture the before-picture (git status, current `docs/how_it_works.md`, whether an operations manual already exists).
2. ROD-T01: confirm the step-0 path/field assumptions (graph v7 current, `result_pattern` matches) hold.
3. ROD-T02: confirm step 0 correctly reports "stop" if Plan 27 has not reached a terminal state.
4. ROD-T03: confirm a stop leaves zero documentation writes.
5. ROD-T04: once Plan 27 has actually concluded, confirm step 0 correctly reports "proceed" and records which terminal was found.
6. ROD-T05: confirm the pre-final-write recheck actually fires on a version change (tested with a throwaway stub, restored to zero trace afterward).
7. ROD-T06: confirm `docs/how_it_works.md`'s content matches the terminal actually found (ACTIVATED framing vs. REMEDIATION_VERIFIED_NOT_ACTIVATED framing).
8. ROD-T07: confirm the superseded content was preserved under `docs/deprecated/`, not deleted.
9. ROD-T08: confirm the operations manual's CLI/config claims are grounded in `runtime/run_curriculum.py` as it actually behaves.
10. ROD-T09: apply the final pass rule — an honest "gate tests pass; content tests not yet executable" report if Plan 27 is still unresolved, or a full pass only once every applicable test has actually run against real output.

# LOOP

On a test failure: fix only the in-scope artifact (a `docs/` file, `readme.md`,
or a genuine step-0 logic error in how this prompt itself was followed — never
runtime, policy, schema, or test code, which are out of scope by the plan).
Rerun that test and everything downstream of it in the ROD-T00→T09 order, and
continue until every currently-applicable test passes.

Stop conditions, restated from the plan: the step-0 prerequisite failing (Plan
27 not concluded, or its graph has moved past v7); any documentation claim
that cannot be grounded in a specific, citable, current repository file; or
the pre-final-write recheck detecting that Plan 27's terminal state or
current graph version changed during implementation — in that last case,
discard any draft written so far rather than publishing it, and re-report a
stop.

Write `plans/28_runtime_operations_docs/28_runtime_operations_docs.result.v1.md`
recording: the step-0 outcome (pass/stop and exactly why), the terminal state
found (if any), every file created or modified with its path, and — if
writing proceeded — the specific repository path each documented claim was
grounded in. Append the execution outcome to
`plans/28_runtime_operations_docs/plans.log.md`.

Completion may only be claimed once every currently-applicable test in
`qa/execution_test.plan.v1.md` has passed for real — a hand-traced or
dry-run pass never counts as the test having passed. If step 0 stops, the
correct, complete outcome is "ROD-T00 through ROD-T03 passed; implementation
correctly declined to proceed" — that is a valid completion of this prompt,
not a failure requiring a workaround.
