# GOAL

Execute Plan 21 node **P1 — Graph IR and production compiler** using P0's exact
digest. The shipped bootstrap validator allowed P0 to start; it is not the
production compiler. Implement a repository-native IR for typed node ports and
state writes, prompt/schema digests, owners, context predecessors,
side-effect/idempotency metadata, executable guard ids, entry/terminals,
fan-out/join groups, reducers, and first-class success, failure, retry, repair,
interrupt, resume, exhaustion, and terminal edges.

Deterministic code alone validates/promotes graphs and emits witness paths.
Models may propose candidates off-line but never fill missing IR fields.

# TEST

1. **P1-T01 — Schema positive.** A minimal valid sequential graph validates.
2. **P1-T02 — Contract strictness.** Unknown fields/versions, duplicate ids, or any missing mandatory node/edge field fail. Local schemas must exist; `contract://` must appear in the closed registry; `state://` must name a typed predecessor field; and `artifact://<producer>/...` must exactly equal an earlier producer output. Missing, future, hidden, or suffix-only matches fail.
3. **P1-T03 — Reachability.** Unreachable nodes, orphan terminals, and nodes unable to reach a terminal fail with witnesses.
4. **P1-T04 — Outcome totality.** Every outcome/failure class has one legal edge or proven mutually exclusive exhaustive guards.
5. **P1-T05 — Cycle safety.** Unbounded cycles fail; repair/retry cycles require limits, repeat signatures, and exhaustion routes.
6. **P1-T06 — Join/reducer safety.** Fan-out declares group and join membership; multiply written keys need associative, commutative deterministic reducers with identities.
7. **P1-T07 — Acceptance dominance.** Any curriculum START→ACCEPTED path bypassing deterministic gates or an independent judge fails with a witness.
8. **P1-T08 — Context graph.** Undeclared history or sibling-verdict leakage fails.
9. **P1-T09 — Ownership.** Every artifact/check has one owner and repair/terminal edge.
10. **P1-T10 — Replay contract.** Every phase compiles the exact `{execution_contract_digest}:Pn:{phase_attempt}` key, phase-ledger schema, typed activation fields, domain-separated subtask keys, and committed-task replay rule; constants, collisions, unknown placeholders, or missing ledgers fail.
11. **P1-T11 — Interrupt/resume.** The deterministic controller alone writes continuation and admitted resume events. Continuations bind run, suspended/allowed node, source event/checkpoint, all pinned digests, next attempt, reason, single-use command, and operator authorization; cross-run/phase, stale, originless, duplicate, or phase-authored resume fails.
12. **P1-T12 — Plan 21 self-compile.** The fully typed sequential P0→P1→P2→P3→P4→P5→P6 manifest compiles before P2 exists by resolving existing schemas, registered P0 selectors, typed `state://` ports, and exact producer-owned future artifacts. Controller-owned evidence-complete events, guards, repair exhaustion, phase ledgers, pause, interrupt, and bound resume compile without prompt prose.
13. **P1-T13 — Historical unsafe shapes.** Plan 20 monolithic finalize, in-session unbounded writer, missing failure edge, false block, and judge bypass all fail.
14. **P1-T14 — Determinism.** Identical bytes yield identical normalized IR/digest.
15. **P1-T15 — Independent denominator mutations.** Against P0's nonempty denominator, delete system/repair/exhaustion/pause/resume edges, invert or duplicate guards, change dependency/context declarations, change a terminal kind, duplicate output/state ownership, omit join members or contract fields, make reducers order-sensitive, and unbound loops; each fails and the denominator cannot shrink to the implementation.

# LOOP

Patch one schema, compiler invariant, fixture, or manifest owner. After change
rerun P1-T03/P1-T05/P1-T07–T10/P1-T14–T15, then affected tests. Never weaken
an assertion, delete a negative fixture, or move deterministic semantics to
prose.

Stop to SYSTEM_FAILURE if acceptance safety, loops, joins, or terminals cannot
be decided from IR or compilation executes a model. Before P2, compile Plan 21
and write the declared normalized graph, Markdown result, and phase ledger.
Submit the exact evidence set to `PHASE_CONTROLLER`; only its admitted immutable
event can select a guard. Do not append a shared log.
