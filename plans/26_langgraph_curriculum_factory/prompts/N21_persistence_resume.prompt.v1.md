# GOAL

Implement `N21_PERSISTENCE_RESUME` after N10/N11/N12. Configure synchronous
`SqliteSaver` under `<output>/.langgraph/checkpoints.sqlite3` with the exact
thread/namespace, durability, locking, episode, correlation, interrupt, orphan,
and resume contract in spec section 11.

Use WAL, FULL synchronization, foreign keys, busy timeout, strict persisted
values, one local writer lock, episode-derived thread IDs, root namespace, and
new episode threads for resume. D04 imports only reducer-validated prior state
and admissible pending writes. Never `invoke(None)` on an old thread or resume
directly into M01–M08.

# TEST

1. Checkpoint path/pragmas/thread/namespace match the spec.
2. State snapshots, `next/tasks`, pending writes, and evidence high-water marks correlate.
3. Crash around every checkpoint/admission boundary duplicates no committed work.
4. Successful fan-out pending writes survive sibling crash but cannot satisfy a partial join.
5. Resume refuses identity/digest/executable/evidence/accepted-byte drift.
6. Graceful interrupt writes one episode terminal and deterministic safe frontier.
7. Orphan recovery runs only D00/D96/D98 and performs zero product side effects.
8. Uncertain model activation enters D91 after D03, never direct redispatch.
9. Duplicate process has one lock winner; loser mutates nothing.
10. Either checkpoint or append-log corruption blocks recovery without self-repair.

Write `results/N21_PERSISTENCE_RESUME.result.v1.md` with configuration, episode
algorithm, crash matrix, commands, and hashes.

# LOOP

Use crash injection; never edit a failed run root. Patch one saver/configuration,
episode helper, correlation, interrupt, or recovery owner. Stop if committed
work can replay, prior threads must be invoked, or accepted bytes can change.

