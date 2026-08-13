# Plan 27 — LangGraph Curriculum Factory remediation

- Version: `1.0`
- Recorded: `2026-08-13`
- Status: `scaffolded_blocked_by_spec_approval`
- Canonical runner: `run.prompt.md`
- Canonical graph: `implementation.graph.v1.yaml`
- Incident source: `plans/26_langgraph_curriculum_factory/post_morten/postmortem.v2.md`
- Implementation authority after approval: corrected Plan 26 specification v2

## 1. Objective

Correct the provider, preflight, integration, evidence, scheduler, and audit
defects identified by the Run 26 post-mortem while preserving the verified
LangGraph product mechanics that remain compatible with the corrected
specification.

The target production profile is not inferred from this plan. It must come from
the corrected, independently verified, user-approved specification. At minimum,
that specification must retain the recorded subscription-only architecture:
Claude/Anthropic generation and repair, Codex/OpenAI cross-family judgment, no
Gemini production route, no billed API keys, no direct model HTTP APIs, and no
hidden fallback.

## 2. Authority order

Run 27 resolves conflicts in this order:

1. current explicit user direction and the hash-bound Run 27 approval record;
2. the independently verified corrected specification v2;
3. subscription-only requirements and supersession lineage in Plans 20–22;
4. retained Plan 25 product requirements and active meta-prompt invariants;
5. reusable Plan 26 LangGraph mechanics identified in post-mortem section 6;
6. current runtime and tests as implementation observations only;
7. Run 26 v1 specification, receipts, logs, and results as historical evidence.

Existing code never proves authorization. Installed CLI presence never proves
authentication, entitlement, data-transmission permission, or provider choice.

## 3. Scope

In scope:

- enforce the corrected eight-job provider/role/transport mapping;
- eliminate production Gemini/Google routes, credentials, models, egress, and
  fallback behavior;
- make preflight truthful and content-free, failing before transmission when a
  mandatory subscription driver is unusable;
- preserve generator/final-judge family separation and deterministic authority;
- harden descendant invalidation, recovery, receipt regeneration, and
  schema-bound result handling before reusing automated scheduling;
- make verification evidence deterministic or run-scoped;
- prove production-compiled reachability and close integration ownership;
- rerun complete regression/adversarial checks;
- run one authorized live unit and one authorized full-workbook proof;
- make the final audit start from requirements lineage.

Out of scope:

- redesigning curriculum pedagogy or product scope;
- weakening denominators, repair bounds, page review, persistence, or terminal
  authority;
- obtaining or recommending Gemini/Google credentials;
- introducing billed API keys, raw model APIs, or provider fallbacks;
- rewriting or deleting Run 26 historical evidence;
- claiming activation from tests, probes, compilation, or simulated transports.

## 4. Hard entry gate

`N00_SPEC_APPROVAL_GATE` is read-only with respect to production code. It must
prove:

- Plan 26 v1 still hashes to
  `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6`;
- the corrected v2 specification and correction result exist;
- the independent QA gate's verified `QA_PASSED` binds the exact v2 bytes;
- `plans/27_langgraph_curriculum_factory_remediation/contracts/spec_approval.v1.yaml`
  validates and binds those same bytes;
- the approval explicitly authorizes Plan 27 implementation remediation;
- no unresolved `USER_DECISION_REQUIRED` item authorizes affected implementation.

Any failure returns `BLOCKED_SPEC_NOT_APPROVED`. No other node may start.

## 5. Execution graph

```text
START
  -> N00 SPEC_APPROVAL_GATE
  -> N10 HARNESS_PROTOCOL
  -> N20 PROVIDER_TRANSPORT
  -> N30 PREFLIGHT_EGRESS
  -> N40 INTEGRATION_OWNERSHIP
  -> N50 EVIDENCE_AUDIT_CONTROLS
  -> N60 ADVERSARIAL_REGRESSION
  -> N70 LIVE_UNIT_PROOF
  -> N80 LIVE_WORKBOOK_PROOF
  -> N90 REQUIREMENTS_FINAL_AUDIT
       -> ACTIVATED
       -> REMEDIATION_VERIFIED_NOT_ACTIVATED
       -> BLOCKED
```

The graph is intentionally linear. Run 26 showed that apparently independent
nodes shared call sites, tests, and graph registration seams. Sequential
execution makes invalidation and artifact lineage unambiguous until N10 proves a
safer scheduler. Write ownership remains exclusive across nodes: ordering does
not authorize a downstream node to rewrite an admitted predecessor's output.

## 6. Node responsibilities

| Node | Responsibility | Post-mortem coverage |
|---|---|---|
| N00 | corrected-spec, independent-QA, and user-approval gate | PM-01–04, PM-20, PM-24; CA-01–05 |
| N10 | schema-bound results, descendant invalidation, recovery, receipts | PM-15, PM-17, PM-19; CA-08, CA-10 |
| N20 | provider roles, transports, configuration, model nodes | PM-01–04, PM-06–07, PM-22–23; CA-07 |
| N30 | truthful preflight, permitted auth, least-privilege egress | PM-06–08, PM-22; CA-06–07 |
| N40 | production graph reachability and ownership closure | PM-11–14, PM-18; CA-11 |
| N50 | deterministic evidence and requirements-level audit controls | PM-12, PM-16, PM-20, PM-24; CA-09 |
| N60 | full deterministic, integration, and adversarial suite | all retained regressions |
| N70 | real authorized one-unit product proof | CA-12 |
| N80 | real authorized full-workbook product proof | CA-12 |
| N90 | independent lineage-to-code-to-product final audit | PM-20, PM-22–24 |

## 7. Result and receipt protocol

Each node writes a human evidence report plus a JSON result conforming to
`schemas/node_result.schema.v1.json`. The scheduler reads only JSON. Markdown is
never parsed for admission.

Every node also declares non-empty executable verification in the graph,
including its focused/live/audit verifier and the exact result-schema validator.
Prompt prose is not a substitute for a scheduler command.

An admitted receipt binds:

- graph, corrected-spec, prompt, baseline, and predecessor receipt digests;
- exact changed paths and final hashes;
- commands, exit codes, denominators, and evidence paths;
- provider/driver identity evidence where applicable;
- node outcome and invalidated descendants.

If an admitted ancestor changes, every descendant receipt is invalid until it
is rerun and re-receipted. A final-audit rerun cannot substitute for missing
lineage.

## 8. Product invariants

- LangGraph remains the single compiled production graph.
- Code owns routing, reducers, joins, retries, acceptance, and terminals.
- Exactly eight schema-bound model jobs exist.
- Generating/mutating roles and final judgment remain different families.
- Staged input is least-privilege and content-aware before transmission.
- No accepted artifact is mutated; repair creates a new version and reruns the
  complete invalidation set.
- Unit/workbook acceptance uses exact, complete denominators including rendered
  page inspection.
- Resume refuses identity, input, graph, evidence, or accepted-byte drift.
- `ready: true` requires every mandatory production driver to prove permitted,
  usable subscription-backed operation without transmitting curriculum content.

## 9. Terminals

- `ACTIVATED`: N60 passed and N70/N80 produced authorized live product receipts;
  N90 independently verified requirements lineage, implementation conformance,
  evidence integrity, and product acceptance.
- `REMEDIATION_VERIFIED_NOT_ACTIVATED`: implementation and complete non-live
  verification passed, but an authorized Claude or Codex subscription driver
  could not be truthfully proven or a live proof could not run. No fallback is
  allowed and no user is directed toward an unauthorized provider.
- `BLOCKED_SPEC_NOT_APPROVED`: the N00 gate is missing, mismatched, unverified,
  unapproved, or contains an unresolved decision affecting implementation.
- `BLOCKED`: an implementation, integrity, evidence, convergence, or audit defect
  remains.

## 10. Completion rule

Only N90 may issue the Run 27 terminal. Test volume alone is not activation.
The final report must state three separate conclusions: specification authority,
implementation conformance, and live product activation.
