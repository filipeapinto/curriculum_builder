# GOAL

Build and prove the Run 27 deterministic execution controller before it is used
for implementation nodes. Correct Run 26 PM-15, PM-17, and PM-19 rather than
copying the old controller unchanged.

After N10 is admitted, all later nodes must run through this controller. Keep
the production curriculum factory and the implementation scheduler separate.

# TEST

Implement the controller-owned files declared in the graph, including:

- `controller/run27_controller.py` with `verify-live-proof` and
  `verify-final-audit` commands;
- `controller/check_forbidden_production_refs.py`, enforcing the graph's scoped
  provider/import and credential-use policy without scanning plans, tests,
  outputs, or Run 26 history;
- `controller/verify_ownership.py`;
- `controller/verify_evidence_determinism.py`;
- `controller/verify_requirements_lineage.py`;
- the scheduler/attempt schemas and the three exact N10 test files named in the
  graph.

`schemas/node_result.schema.v1.json` is frozen before N00 and is a read-only
controller input. N10 must not edit, replace, or version it after N00 admission.
If it is insufficient, N10 returns `BLOCKED`; it does not retroactively change
the entry gate's result protocol.

Do not create a general-purpose controller test directory ownership claim; N60
owns its separately named cross-system adversarial test. The N10 tests must
prove:

1. Node admission consumes only schema-valid JSON results; Markdown and rich
   prose cannot change status.
2. Receipts bind graph, approved-spec, prompt, baseline, predecessor, command,
   log, changed-file, and final-output hashes.
3. Any admitted ancestor digest change invalidates every transitive descendant,
   including descendants whose own output bytes did not change.
4. Invalidated descendants cannot feed a join or final audit until rerun and
   re-receipted against current predecessor receipts.
5. Write-set violations fail before merge and retain an immutable attempt.
6. Interrupted attempts never merge implicitly. Resume creates a child attempt
   bound to the parent and current predecessor digests.
7. Recovery/re-admission is a named operation with a machine-readable reason,
   exact artifact binding, verification rerun, and immutable audit event.
8. A merge interruption is atomic or recoverable without accepting partially
   merged bytes.
9. Evidence/log paths are attempt-scoped and write-once.
10. Status, validation, dry-run, and audit commands are read-only.
11. The controller refuses to run N10 or any later node without an admitted N00
    receipt bound to the current approved v2 digest.
12. The Plan 27 graph validates and the complete controller test suite passes
    twice without changing tracked evidence bytes.
13. Every graph node has non-empty machine-runnable verification and the exact
    `validate_result.py --node NODE_ID` command.
14. Distinct nodes have no overlapping write paths, even when they are ordered.
15. N90 requires exactly one legal terminal recommendation; other nodes cannot
    provide one; only N00 may use the `BLOCKED_SPEC_NOT_APPROVED` outcome.

The result must enumerate every Run 26 controller behavior retained, replaced,
or rejected. Do not claim the old 537-event stream is clean evidence for the new
controller.

# LOOP

Repair one failing harness invariant at a time inside N10's exact declared
controller/schema/test paths. Rerun the focused test and then the complete N10
suite. Preserve each failed attempt. Stop with `BLOCKED` after three attempts at
the same unchanged finding; never weaken an assertion to admit the controller.
