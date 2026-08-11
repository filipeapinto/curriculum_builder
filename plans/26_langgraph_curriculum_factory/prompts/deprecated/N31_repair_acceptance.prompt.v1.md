# GOAL

Implement `N31_REPAIR_ACCEPTANCE` after N30. Integrate D17–D24 and M06 into the
same compiled graph for total finding classification, one-owner targeted repair,
descendant invalidation/retest, bounded convergence, immutable unit acceptance,
accepted checkpoint correlation, and exact effective-run coverage.

Every finding maps exactly once. Attempts/fingerprints reserve before dispatch.
Repair creates a versioned child and declared diff; admission enforces parent,
boundary, invalidations, and retest order. D22 recomputes the full current unit
denominator. Only a requested target with accepted prerequisite closure may
reach `UNIT_ACCEPTED` through D98.

# TEST

1. Zero/multiple/unknown/model-selected finding owners fail classification.
2. Local repair changes only named paths and descendants; broad/in-place/stale-parent repair fails.
3. Attempt/repeat bounds stop before an over-bound M06 call.
4. Every invalidated descendant is regenerated/retested; stale evidence cannot pass.
5. Remove/fail/stale each acceptance member in turn; D22 rejects all cases.
6. Accepted receipt/bytes are immutable across resume, later units, and repair.
7. Cursor advances only after checkpoint/evidence/log correlation flush.
8. D24 rejects missing/extra/reordered/wrong-hash coverage.
9. One-mode success semantics and all failure terminals match the truth table.
10. Crash at every repair/accept/checkpoint boundary is idempotently recoverable.

Write `results/N31_REPAIR_ACCEPTANCE.result.v1.md` with owner/retest maps,
denominator manifest, crash tests, commands, and hashes.

# LOOP

Patch one classifier, request, repair producer, admission check, retest edge,
acceptance guard, or fixture. Never widen repair or weaken a denominator. Stop
if accepted bytes can mutate or convergence can exceed policy.
