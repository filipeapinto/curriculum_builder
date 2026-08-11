# GOAL

Implement `N32_WORKBOOK_TERMINALS` after N31. Integrate D25–D32, M07/M08, and
D30 for exact workbook assembly, render/page inventory, every-page review,
workbook-only repair, prerequisite classification, and final release candidate
routing through the pre-existing N22-owned D98.

N32 owns workbook behavior and terminal-candidate construction, not
`terminal.py` or D98. Workbook repair cannot change accepted unit bytes. D32
recomputes all current denominators. Only a named unavailable required external
fact may propose `PAUSED_PREREQUISITE`; D98 independently enforces the final guard.

# TEST

1. Missing/extra/reordered/wrong-hash unit blocks assembly.
2. Workbook PDF has positive contiguous inventory and every page in M07.
3. Missing/stale/failed/`NOT_RUN` workbook evidence blocks release.
4. M08/deterministic repair cannot alter accepted unit hashes.
5. Repeated defects exhaust before over-bound activation.
6. D32 recomputes evidence and ignores cached pass labels.
7. Workbook success/failure/pause candidates traverse the real N22-owned D98;
   N32 contains no terminal writer and cannot connect to END directly.
8. Only interruption/named prerequisite pause is resumable; false pause is rejected.
9. Fake full-run paths cannot emit/copy product `COMPLETE` evidence.
10. Crash at assembly/review/repair/release/D98 boundaries is idempotent.

Write `results/N32_WORKBOOK_TERMINALS.result.v1.md` with coverage/release
denominators, D98 integration traces, commands, and hashes.

# LOOP

Patch one workbook, page barrier, review reduction, repair, release, prerequisite,
or candidate builder. Route terminal-guard defects to N22. Stop if N32 must own
terminal.py, change accepted units, or bypass D98.

