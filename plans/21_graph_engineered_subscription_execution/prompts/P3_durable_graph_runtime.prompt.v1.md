# GOAL

Execute Plan 21 node **P3 — Durable graph runtime** only after P1 and P2 pass
against the same P0 digest. Execute compiled prompt graphs with typed state,
code-owned edge guards, deterministic reducers, per-node checkpoints,
idempotency, interrupt/resume, bounded targeted repair, and immutable accepted
artifacts. A model may produce a typed artifact or verdict; it may not choose
the next node, merge state, classify a terminal, or admit bytes.

# TEST

1. **P3-T01 — Compiled-only execution.** Raw/uncompiled graph input is refused.
2. **P3-T02 — State schema.** Every checkpoint/event contains all Plan 21 required fields and rejects unknown node/state/version ids.
3. **P3-T03 — Deterministic edges.** Identical state selects the same edge; model prose cannot alter a guard.
4. **P3-T04 — Sequential path.** A two-node graph records enter/exit/checkpoint/edge events in order.
5. **P3-T05 — Parallel all-of join.** Both branches complete before join; completion order does not change reduced state or digest.
6. **P3-T06 — Branch failure.** One failed sibling preserves successful pending writes but the join cannot accept partial state.
7. **P3-T07 — Bounded repair loop.** Failed test targets one owned artifact, records attempts, and exits on pass.
8. **P3-T08 — Convergence exhaustion.** Repeated identical failures stop at the policy bound with last valid checkpoint preserved.
9. **P3-T09 — Atomic admission.** Crash between model return and admission leaves no partial accepted artifact.
10. **P3-T10 — Idempotent replay at both levels.** Runtime node replay and the P3 implementation phase ledger use domain-separated keys; cold restart duplicates neither committed side effects/events nor skips an incomplete implementation subtask.
11. **P3-T11 — Interrupt.** Interrupt before/after a model node yields a truthful state and complete checkpoint.
12. **P3-T12 — Replayable resume.** Only `ABSENT` or crash-truncated `INCOMPLETE` checkpoints replay under the original idempotency key; valid predecessors are not rebuilt.
13. **P3-T13 — Version pin.** Changed graph/prompt/policy/schema/route digest blocks resume unless an explicit migration creates a new run version.
14. **P3-T14 — Accepted immutability.** Accepted artifact overwrite is rejected, including through resume or repair.
15. **P3-T15 — Failure taxonomy.** Transient, invalid output, policy violation, revisable check, external fact block, factory defect, and exhausted loop follow distinct edges.
16. **P3-T16 — Terminal authority.** Invalid BLOCKED/ACCEPTED/SYSTEM_FAILURE records are rejected before write.
17. **P3-T17 — Event provenance.** Recomputed hashes link request, route, prompt, output, check, edge, and checkpoint.
18. **P3-T18 — Corruption is fail-closed.** On-disk byte flip, hash mismatch, corrupt record, or unauthorized mutation preserves forensic bytes and reaches SYSTEM_FAILURE; it is never replayed or silently repaired.
19. **P3-T19 — Process metrics.** Record node/edge counts, repeated-path ratio, redundant-evaluator count, and context bytes without capturing hidden reasoning.
20. **P3-T20 — Live mixed-family miniature.** Claude authors a tiny schema artifact, deterministic code checks it, Codex judges it, and the graph reaches the justified terminal with complete trace.
21. **P3-T21 — Independent crash denominator.** Inject death immediately before/after every admission and checkpoint boundary frozen by P0; every boundary is covered even if runtime instrumentation omits it.

# LOOP

Map each failure to exactly one executor, edge evaluator, reducer, checkpoint
service, schema, or fixture. Patch one owner. Rerun P3-T01–T03, P3-T09–T10,
P3-T13–T17, then the failed boundary and later dependent tests. For injected
crashes, never repair the run root by hand.

Stop if a side effect cannot be made idempotent/checkpointed, resume can change
graph version or overwrite accepted work, joins are order-dependent, or a model
must choose control flow. Write the full authorized repository path
`plans/21_graph_engineered_subscription_execution/results/P3.result.v1.md`.
It contains state diagrams, event schema, crash matrix, live trace, test
results, and hashes.
Also write the typed producer contract
`plans/21_graph_engineered_subscription_execution/results/P3.runtime_contract.v1.yaml`
under `schemas/runtime_contract.schema.v1.json` and the declared P3 phase ledger.
Submit the exact test/artifact evidence set to `PHASE_CONTROLLER`; only it may
admit the routing event. Do not append a shared log.
