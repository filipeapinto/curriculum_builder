# GOAL

Implement `N50_ADVERSARIAL_REGRESSION` after N40. Encode and run the complete
Plan 26 section 17 matrix, QA rejection criteria, full suites/gates, and explicit
cross-node proofs for runtime egress enforcement and CI lock-drift ownership.

Fake tests prove orchestration only. Inject SIGINT/hard death around every node,
fan-out member, process, admission, checkpoint, acceptance, and terminal boundary.

# TEST

1. Every section 17.2 adversarial row has a passing executable test.
2. Reducer/topology/transport/persistence/unit/repair/workbook/CLI suites pass.
3. Crash denominator is independently enumerated and fully covered.
4. Completion permutations do not change state, hashes, or acceptance.
5. Forbidden imports/dependencies and second-production-path scans pass.
6. Runtime egress tests prove unauthorized Python HTTP/socket/model-endpoint,
   redirect, sandbox-bypass, and unapproved retrieval attempts make zero egress.
7. CI configuration invokes N10's deterministic lock regeneration; controlled
   drift fails CI, while clean regeneration is byte-identical.
8. Full runtime/gate suites have no new or worsened baseline failure.
9. Fake outputs cannot be copied/promoted into product roots.
10. Reports contain commands, exits, environment/package hashes, and evidence.

Write `results/N50_ADVERSARIAL_REGRESSION.result.v1.md` with row-to-test matrix,
egress and CI lock-drift proof, regression comparison, commands, and hashes.

# LOOP

Route implementation failures through the manifest rework map; N50 may edit only
its enumeration/fixtures. Runtime egress failures return to N13; lock/CI drift
failures return to N10. Invalidate descendants and never weaken a negative test.

