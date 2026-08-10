# Graph-Engineered Subscription Execution — planning log

Append-only. Do not rewrite earlier entries.

### 2026-08-09 — initial research and architecture decision

- Researched prompt reasoning graphs, execution graphs, durable state,
  evaluator-optimizer loops, graph verification, boundary testing, and graph
  evolution through the 2026-08-09 cutoff.
- Assessed Plan 20 at 2 pass / 6 partial / 6 fail against a 14-property rubric.
- Selected one normalized invocation interface with two subscription-backed CLI
  drivers: Claude Code for authoring and Codex CLI for cross-family judgment.
- Recorded that Codex is currently logged in with ChatGPT while Claude Code is
  installed but logged out; implementation must stop at capability proof until
  Claude subscription OAuth is restored.
- Protected Plan 20, Plan 19, existing outputs, and the dirty worktree from
  modification during planning.

### 2026-08-09 — independent QA round 1 disposition

- Three independent reviews found blocking graph, history, and subscription
  defects. All Critical/High findings were accepted.
- Added a shipped deterministic bootstrap validator and mutation self-tests;
  made the implementation phases sequential; expanded the typed node/edge IR;
  separated unit, run, and plan statuses; and added first-class repair,
  prerequisite-pause, system-failure, and interrupt edges.
- Removed shared phase log writes, separated replayable missing/incomplete
  checkpoints from fail-closed corruption, and added independent coverage
  denominators plus historical-format census contracts.
- Moved repository-wide adapter migration to P4; documented Codex
  `DRIVER_BOUND_REQUEST` identity assurance; required unambiguous Claude
  subscription entitlement and outer readable-root containment.
- Added live three-unit `--all`, exact-four workbook review, literal deferred
  debt/mirror, and independent census release tests.
- Corrected the paused Anthropic monthly-credit statement: `claude -p`
  currently draws from subscription usage limits.

### 2026-08-09 — independent QA round 2 disposition

- Accepted all round-two Critical/High findings; the remaining gaps were in
  executable contract semantics, not prose quality.
- Added a closed phase-result event schema, guard predicate registry, explicit
  convergence-exhaustion routes, and resumable prerequisite/interrupt states.
- Made state-field schemas, single writers, readers, reducers, serialization,
  checkpoint policy, dependency/context agreement, and output ownership
  machine-checkable. Added producer-owned `artifact://` references so P1 can
  compile the complete manifest before later producers exist.
- Strengthened bootstrap mutations for mandatory system/repair/exhaustion/
  pause/resume edges, guard duplication, terminal kind, dependency/context
  mismatch, and duplicate output/state ownership.
- Replaced arbitrary P0 contract maps with closed path, capability, sandbox,
  status, historical-census, anomaly, aggregate, and numeric-threshold schemas;
  added a pre-existing two-driver identity-assurance policy that P2 cannot edit.
- Made P2 phase-level idempotency compose build and both live canaries; added
  the P3 runtime contract producer; made P6 resume a separate cold process; and
  restored Plan 19's exact RT-7 sites, mirror, gates, and fail-closed dirty-work
  pause. QA exhaustion now routes to plan SYSTEM_FAILURE, never BLOCKED.

### 2026-08-09 — independent QA round 3 disposition

- Kept the package unapproved after all three reviewers independently produced
  executable evidence-free PASS or originless resume counterexamples.
- Replaced self-asserted phase outcomes with controller-admitted events bound to
  the current run, node, attempt, graph, prompt, execution contract,
  predecessor, checkpoint, exact required-test set, exact artifact set, and
  recomputed hashes. A PASS now requires nonempty, denominator-exact, all-PASS
  test evidence and every authorized artifact hash.
- Added typed, controller-owned continuation and operator-authorized resume
  command contracts. Resume is single-use and binds the source event,
  checkpoint, all pinned digests, same suspended node, same run, and next
  attempt; cross-run, cross-phase, stale, originless, and replayed commands fail.
- Closed outcome/failure/reason combinations; separated logged-out Claude from
  unproven included-allocation entitlement; and made separately billed Claude
  credits/overage, ChatGPT credits, API fallback, usage-based seats, and
  contradictory provider overrides fail the subscription-only proof.
- Restored the live Plan 19 run vocabulary, added an explicit P4 status
  migration, made sandbox claims reconstructable, and added exact P6 reads of
  every predecessor bundle plus the frozen anti-regression source contract.
- Added immutable per-phase ledgers and domain-separated phase/subtask
  idempotency for P0–P6. Strengthened the bootstrap against unknown contracts,
  future producers, missing schemas, idempotency collisions, evidence-free
  PASS, failing/missing evidence, cross-run/cross-phase/stale resume, duplicate
  denominator IDs, and aggregate mismatch.
- The review protocol permits one reviewer-specific closure addendum against
  these frozen remediations; it is not a fourth full review. Any unresolved
  Critical/High closure finding requires a new plan version rather than another
  in-place QA loop.
