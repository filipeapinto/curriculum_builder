# GOAL

Implement `N31_REPAIR_ACCEPTANCE` after N30. Integrate D17–D24 and M06 into the
same compiled graph for finding classification, targeted repair, invalidation/
retest, bounded convergence, immutable unit acceptance, checkpoint correlation,
coverage, and routing of terminal candidates through the already implemented,
N22-owned D98.

N31 owns repair/acceptance modules, not terminal.py. Every finding maps once;
attempts reserve before dispatch; repairs are versioned bounded children; D22
recomputes the full current unit denominator. Unit success/failure tests invoke
the real predecessor-provided D98 callable and never patch or replace it.

# TEST

1. Zero/multiple/unknown/model-selected finding owners fail.
2. Local repair changes only named paths/descendants; broad/in-place/stale repair fails.
3. Attempt/repeat bounds stop before an over-bound M06 call.
4. All invalidated descendants retest; stale evidence cannot pass.
5. Removing/failing/staling each acceptance member makes D22 reject.
6. Accepted bytes remain immutable across resume, later units, and repair.
7. Cursor advances only after checkpoint/evidence/log correlation flush.
8. D24 rejects missing/extra/reordered/wrong-hash coverage.
9. One-mode success and unit failure candidates traverse the real N22-owned D98;
   invalid terminal candidates are rejected, with no N31 write to terminal.py.
10. Crash at every repair/accept/checkpoint/D98 boundary is recoverable.

Write `results/N31_REPAIR_ACCEPTANCE.result.v1.md` with owner/retest maps,
denominator and real-D98 traces, commands, and hashes.

# LOOP

Patch one classifier, repair, admission, retest, acceptance, coverage, or fixture
owner. Route any D98 defect back to N22; do not write terminal code here. Never
widen repair or weaken a denominator.

