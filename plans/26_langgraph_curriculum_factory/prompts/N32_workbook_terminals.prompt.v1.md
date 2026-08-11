# GOAL

Implement `N32_WORKBOOK_TERMINALS` after N31. Integrate D25–D32, M07/M08, and
D30/D98 terminal behavior for exact full-manifest workbook assembly, actual
render/page inventory, every-page independent review, workbook-only targeted
repair, final release recomputation, and six truthful terminals.

Workbook assembly consumes only immutable accepted units in exact manifest
order. Workbook repair cannot change unit bytes. D32 recomputes all current
unit/workbook/checkpoint/evidence/log denominators. `PAUSED_PREREQUISITE` is legal
only for a named required unavailable external fact; other faults are system failures.

# TEST

1. Missing/extra/reordered/wrong-hash unit blocks assembly.
2. Workbook PDF has positive contiguous inventory and every page in M07 result.
3. Missing/stale/failed/`NOT_RUN` workbook evidence blocks release.
4. M08 and deterministic repair cannot alter any accepted unit hash.
5. Repeated workbook defects exhaust before over-bound activation.
6. D32 ignores cached pass labels and recomputes current evidence.
7. Six terminals enforce exact guards, once per episode, only via D98→END.
8. Only interruption/named prerequisite pause resume; false pause is rejected.
9. Fake full-run path cannot emit/copy product `COMPLETE` evidence.
10. Crash at assembly/review/repair/release/terminal boundaries is idempotent.

Write `results/N32_WORKBOOK_TERMINALS.result.v1.md` with coverage/release
denominators, terminal truth table, commands, and hashes.

# LOOP

Patch one assembly, page barrier, review reduction, repair, release, prerequisite,
or terminal owner. Rerun coverage, unit-immutability, final-recompute, and truth-
table tests. Stop if workbook work can change accepted units or false success/pause is possible.

