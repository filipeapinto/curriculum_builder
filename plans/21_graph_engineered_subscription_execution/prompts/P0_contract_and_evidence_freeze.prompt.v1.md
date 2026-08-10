# GOAL

Execute Plan 21 node **P0 — Contract and evidence freeze**. First run the
shipped bootstrap validator and self-test named in the plan. Then read the Plan
21 package, Plan 19 plan/prompts/reviews, Plan 20 plan/QA/log, issues 001–007,
and every prior QA source named by `anti_regression_sources`.

Freeze the actual repository before implementation. P0 may write only its
declared outputs. It must not edit runtime, policy, schema, test, curriculum,
Plan 19, Plan 20, historical output, or unrelated dirty files.

The contracts must capture protected dirty paths; relevant hashes; baseline
tests/gates; CLI/auth facts without tokens; provider/key/base-URL/helper
override status; Plan 19/20 dispositions; a format-aware historical finding
census; exact P1–P6 paths/schemas; fresh roots; digest algorithm; separate
observed and target unit/run/plan status vocabularies plus an explicit P4
migration; and an independent denominator of required
nodes, edges, guards, side-effect boundaries, mutation operators, historical
findings, and process-quality thresholds.

# TEST

Run in order; record command, exit code, and evidence hash.

0. **P0-T00 — Shipped bootstrap.** `bootstrap.command` and `bootstrap.self_test_command` both exist before P0 and pass without a model or production compiler.
1. **P0-T01 — Schema validation.** Plan 21 validates against its sibling schema.
2. **P0-T02 — Protected work.** Capture complete `git status --porcelain=v1 -z`; no P0 write overlaps a pre-existing dirty path.
3. **P0-T03 — Executable historical census.** Build/test `historical_census.py` for Markdown headings, YAML finding/disposition records, aggregate counts, and path/filename anomalies. Every item or unresolved aggregate gets a stable id, source evidence, disposition, and later owner; later-fixed findings remain.
4. **P0-T04 — Plan conflict map.** Every affected Plan 19/20 claim is cited by file/line, classified unchanged/retargeted/retired/superseded, and owned by a later node. Include the deliberate Codex driver-bound identity supersession.
5. **P0-T05 — Live baseline.** Run current runtime tests/applicable gates without edits; record stable pass/fail/blocked identities, not a demanded clean exit.
6. **P0-T06 — Subscription and metering facts.** Record Claude/Codex versions, auth, plan/seat subtype, included-allocation metering, separately billed credit/overage enablement, API fallback, provenance, and evidence hashes without tokens. Claude logout is factual and later yields `AUTHENTICATION_MISSING`; any unprovable included-allocation-only fact later yields `SUBSCRIPTION_ENTITLEMENT_UNPROVEN`.
7. **P0-T07 — Provider precedence and sandbox reconstruction.** Populate every closed override name with set/unset only; record sandbox engine/version/profile bytes and digest, canonical absolute roots/purposes/read-write flags, mount/symlink policy, credential boundary, and network destinations. Reject write roots that are not readable/authorized, aliases, symlink escape, and contradictory auth/metering combinations. Never print secret values.
8. **P0-T08 — Digest determinism.** Two canonical recomputations match byte-for-byte.
9. **P0-T09 — Scope and reference totality.** Resolve every registered `contract://P0/authorized_paths/...` selector to canonical concrete paths and schemas; reject unregistered contracts, missing local schemas, future producer/state references, or historical output targets.
10. **P0-T10 — Source anomaly reconciliation.** Item records reconcile to aggregate counts. Record Plan 20 QA v2's declared `2 Critical, 1 High` but two Critical headings, and parse Plan 19 YAML dispositions rather than dropping them.
11. **P0-T11 — Biting mutations.** In temporary copies add Markdown/YAML findings, duplicate ids, remove a required mutation kind, change an aggregate count, omit a mandatory IR field/edge, contradict live lifecycle values, expand sandbox/credit routing, and alter a bound byte; census, denominator, bootstrap, relational baseline, and digest checks each fail.

# LOOP

Repair only the inventory, conflict map, census, coverage denominator, scope
map, or digest recipe named by failure. Rerun P0-T00–T04 and P0-T08, then the
failed test and later tests. Never “fix” baseline production failures.

Stop to SYSTEM_FAILURE if protected work cannot be separated, a source is
unreadable, status vocabularies cannot be reconciled without invented intent,
or the same factual mismatch recurs twice. Write every declared P0 output and
the phase ledger. Submit the exact test/artifact evidence set to
`PHASE_CONTROLLER`; only it may recompute hashes and admit the schema-valid P0
routing event. The Markdown result is explanatory evidence, not an edge
selector. Do not append a shared log.
