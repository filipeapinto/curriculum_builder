# GOAL

Execute Plan 21 node **P5 — Evaluator-optimizer acceptance**. Build a fail-closed
evaluation subgraph:

`candidate → deterministic gates → independent evaluator fan-out → deterministic join → accept | targeted repair | honest terminal`.

Each evaluator receives only the candidate, source/check evidence, and its own
rubric. It cannot see author conversation, sibling verdicts, or controller
conclusions. Deterministic code validates verdict schemas, aggregates results,
selects the single owned repair edge, and enforces convergence. Measure process
quality as well as final correctness so repeated or redundant review is visible.

# TEST

1. **P5-T01 — Acceptance dominance.** Static and runtime tests prove no path reaches ACCEPTED before all blocking deterministic gates and required evaluators pass.
2. **P5-T02 — Cross-family independence.** Author and final judge families differ; same-family or shared-session assignments fail.
3. **P5-T03 — Context isolation.** Evaluator inputs contain no sibling verdict, author transcript/session, unrelated repository file, or prior terminal conclusion.
4. **P5-T04 — Typed verdict.** Verdict, check ids, evidence locators, severity, repair target, and confidence/rationale fields validate; free prose alone cannot drive control.
5. **P5-T05 — Missing/malformed verdict.** Nonzero exit, empty, malformed, schema-invalid, or identity-mismatched verdict is non-accepting.
6. **P5-T06 — Deterministic-first.** A candidate failing a cheap deterministic gate does not consume judge execution unless policy explicitly requires diagnostic review.
7. **P5-T07 — Parallel fan-out.** Independent specialist evaluators run from the same immutable candidate digest and join with order-independent semantics.
8. **P5-T08 — Disagreement handling.** Conflicting verdicts follow a declared deterministic adjudication/repair edge; the author never resolves the vote.
9. **P5-T09 — Single repair owner.** Every failed check maps to exactly one artifact/node or a non-revisable terminal; zero/multiple owners fail.
10. **P5-T10 — Targeted repair.** Repair request contains only failed checks, bounded evidence, and one output schema; unrelated artifact hashes stay fixed.
11. **P5-T11 — Retest closure.** After repair, rerun the failed check plus all downstream dependents; unrelated independent checks may reuse digest-bound results.
12. **P5-T12 — Repeat-failure convergence.** Same failure signature terminates at policy threshold; changed failure signatures remain within total revision budget.
13. **P5-T13 — Judge prompt injection.** Candidate text cannot alter rubric, tools, output schema, family, edge, or terminal authority.
14. **P5-T14 — False positive controls.** Raw JSON lesson, irrelevant visual, unsupported numeric claim, missing POE observation, and partial run all fail the intended gates.
15. **P5-T15 — False negative controls.** Valid exact-model evidence, readable lesson, truthful visual, observable activity, and complete run pass without gratuitous repair.
16. **P5-T16 — Review trace.** Recompute candidate/evidence/prompt/route/verdict/join hashes from receipts.
17. **P5-T17 — Process metrics.** Record evaluator diversity, duplicate-finding rate, unnecessary-path ratio, repeated-evaluator count, and context bytes.
18. **P5-T18 — Redundancy and phase replay.** Unchanged candidate digest cannot trigger an evaluator again without a recorded invalidation reason; the P5 phase ledger prevents committed evaluator calls from repeating across process death and prevents PASS before every required verdict/artifact commits.
19. **P5-T19 — Human interrupt.** Any declared human/safety approval is a checkpointed graph gate with typed resume input.
20. **P5-T20 — Honest BLOCKED.** Only named external fact absence with search receipts blocks; judge unavailability and factory defects do not masquerade as domain blocks.
21. **P5-T21 — Historical QA corpus.** Replay P0's stable anti-regression fixtures and prove each prior Critical/High class is caught by its assigned control.
22. **P5-T22 — Live evaluator-optimizer loop.** Inject one revisable defect into a fresh live candidate; observe one targeted repair, dependent retest, independent final verdict, and justified acceptance.

# LOOP

For any failure, name the evaluator node, deterministic gate, join, ownership
map, or fixture. Patch one owner; rerun P5-T01–T05, P5-T09–T13, and P5-T16,
then the failed test and affected downstream closure. A loop iteration must
reduce a named failed-check set or terminate; do not add more self-review calls
as a generic response.

Stop if evaluator independence cannot be demonstrated, a model must aggregate
or accept, a missing verdict can be ignored, repair ownership is ambiguous, or
the loop can run without a measurable convergence bound. Write
`plans/21_graph_engineered_subscription_execution/results/P5.result.v1.md`
with graph, context manifests, fixtures, live trace, process metrics, tests,
hashes, and the declared P5 phase ledger. Submit the exact test/artifact evidence
set to `PHASE_CONTROLLER`; only it admits routing. Do not append a shared log.
