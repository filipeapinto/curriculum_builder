# GOAL

Execute Plan 21 node **P6 — End-to-end release and supersession**. Prove the
compiled subscription-only graph from clean, fresh output roots. Audit every
guard boundary and every historical anti-regression ID frozen by P0. Publish a
supersession record only when evidence—not file presence or declining finding
counts—shows that Plan 21 is executable and Plan 20 must remain historical.

# TEST

1. **P6-T01 — Artifact/schema validation.** Plan, graph IR, policies, routes, registries, requests, receipts, checkpoints, results, and terminals validate.
2. **P6-T02 — Static graph clean.** Compiler reports no unreachable/orphan node, illegal cycle, unsafe acceptance path, undefined reducer, or missing failure edge.
3. **P6-T03 — Subscription-only proof.** Live Claude author and Codex judge receipts prove subscription auth; no API-key/raw HTTP/Gemini path executes.
4. **P6-T04 — Full path coverage.** Tests cover every node, legal edge, guard outcome, terminal, repair edge, interrupt, and resume edge.
5. **P6-T05 — Boundary perturbation.** For every guard, replay to its boundary and perturb prerequisite/condition; illegal crossing is rejected.
6. **P6-T06 — Crash and phase-ledger recovery.** Fault injection before/after every release-test subtask, side effect, admission, and checkpoint commit yields deterministic cold recovery; committed tests/model calls do not repeat and incomplete work cannot be skipped.
7. **P6-T07 — Context noninterference.** Adding an unrelated hidden sibling artifact/verdict cannot change a node that is not authorized to receive it.
8. **P6-T08 — Reducer determinism.** Parallel completion permutations yield identical normalized state and terminal.
9. **P6-T09 — Historical issue 001–007.** Each issue's biting fixture fails before acceptance; valid controls pass.
10. **P6-T10 — Prior Critical/High matrix.** Every P0 anti-regression ID has an assigned passing test and evidence hash; no “fixed elsewhere” waiver is accepted.
11. **P6-T11 — Plan 20 Criticals.** Structural containment, receipt schema, route schema, P2 interface, and P3 checkpoint/state mapping regressions are all explicitly negative-tested.
12. **P6-T12 — Dirty-work preservation.** Compare with P0 status-bytes; no unrelated user path was modified, deleted, reverted, or absorbed into Plan 21 scope.
13. **P6-T13 — Fresh live unit.** Complete unit uses only traceable adapter artifacts and reaches the justified terminal.
14. **P6-T14 — Cold-process interrupt/resume.** Start a real process, interrupt it mid-graph, then launch a separate clean process with `--resume`; it must not recompute accepted predecessors, reuse in-memory state, or require manual edits.
15. **P6-T15 — Targeted live repair.** One local defect changes only its owned bytes and converges within bounds.
16. **P6-T16 — Run/workbook truth.** Partial coverage cannot become COMPLETE; complete accepted coverage assembles with all-page review and immutable units.
17. **P6-T17 — Independent recomputation.** A separate auditor derives terminal and coverage from immutable inputs/receipts without controller conclusions.
18. **P6-T18 — Process quality.** Compare path counts, unnecessary-path ratio, repeated evaluations, context bytes, retries, revisions, and model usage to P0's numeric thresholds/denominator; exceeded or missing metrics fail release.
19. **P6-T19 — Independent final QA.** Three independent roles from the plan's review protocol report zero unresolved Critical/High findings after evidence-backed dispositions.
20. **P6-T20 — Supersession consistency.** `supersession.v1.md` names exact Plan 19/20 dispositions, graph/prompt versions, migration boundary, rollback/new-run rule, and remaining external blockers without overstating completion.
21. **P6-T21 — Live multi-unit orchestration.** Start a bounded three-unit fixture through a real `--all` process with a P2 route/receipt per unit and manifest order; terminate the first process during unit 3, then use a separate clean `--resume` process to finish with zero manual artifacts or in-process memory dependence. A fresh Arduino `--all` attempt advances or stops with its truthful class.
22. **P6-T22 — Exactly four workbook reviews.** Four schema-valid isolated roles run on the immutable workbook candidate; 3/5 reviews, duplicate role/identity, shared session, sibling-verdict access, and malformed verdict all fail.
23. **P6-T23 — Deferred debt literalism and RT-7 repair.** Quote and dispose RT-1/2/3/4/5/7/10 individually; preserve RT-6/8/9 and the RT-9 negative fixture. For RT-7, record exact before/after criterion text and replace the stale `curricula/<name>/units/` locator with the P0-frozen authoritative `<output_root>/<UNIT_ID>/` contract at every repeated site: `policy/deferred.v1.yaml`, `policy/checks.v1.yaml`, `tests/gates/fr_p5_unit.py` (module docstring and `unit_files()`), `runtime/readability.py`, and the RT-7 row in `plans/03_folder_refactoring/folder_refactoring.plan.v6.md`. Rerun `FR-P2-DEFERRED`, `FR-P5-READABILITY`, `FR-P5-BLOOM-VERBS`, `FR-P5-DERIVATION`, `FR-P5-RECEIPT-HASH`, and `FR-P4-CHECK-MAPPING`, reporting scanned-unit counts honestly. If any named site is pre-existing dirty work not explicitly authorized for P6 by the user and frozen as `AUTHORIZED_FOR_P6` in P0, emit `PAUSED_PREREQUISITE` through `PROTECTED_RT7_OVERLAP` without writing it. Never lower the evidentiary bar; unproven criteria remain unchanged blockers.
24. **P6-T24 — Census completeness.** Re-run the format-aware historical census against the original corpus and reconcile every aggregate count/anomaly independently of P0's frozen list.

# LOOP

Attribute every failure to one node, edge, contract, prompt, schema, or fixture.
Repair that owner, rerun static compilation, P6-T01–T03, the complete historical
matrix P6-T09–T12, then the failed test and dependency closure. Repeat final
three-way QA after any material plan/runtime/prompt change. Maximum three QA
rounds; if any Critical/High remains after round three, emit the P6 phase event
with outcome `CONVERGENCE_EXHAUSTED`, failure class `CONVERGENCE_EXHAUSTED`,
and route to plan `SYSTEM_FAILURE`. Never record plan-phase or unit `BLOCKED`
for QA non-convergence.

Stop if evidence is simulated/prewritten/manually edited, a historical
Critical/High class is untested or reproduced, live auth is not subscription
based, full path coverage is unavailable, or independent recomputation differs
from the controller. Write
`plans/21_graph_engineered_subscription_execution/results/P6.result.v1.md`,
`plans/21_graph_engineered_subscription_execution/supersession.v1.md`, and the
declared P6 phase ledger. Submit the exact twenty-four-test and complete artifact
set to `PHASE_CONTROLLER`; only it may admit a P6 PASS event and approval edge.
Write no shared log. Approval requires all twenty-four tests and zero unresolved
Critical/High independent findings.
