# Calibration report — Codex→Claude independent QA gate

Run `RUN-CAL-20260819-01` executed approved plan `codex_calls_claude_qa_gate.plan.v1.html` (SHA-256 `28878edec101a917a2b98a5e14d05e019387c9ff20bd2ff27bccc87e8eacee82`). Terminal calibration status: **COMPLETE — STOPPED AT SECOND HUMAN GATE**.

## Outcome

Calibration found a plausible, officially documented Claude CLI subprocess route and a direct API/Agent SDK evidence path worth full appraisal. The installed Claude Code 2.1.233 help surface advertises non-interactive operation, JSON/streaming output, JSON Schema, session, permission/tool, persistence, MCP, timeout-adjacent process, and budget controls. Current official Claude documentation additionally recommends bare mode for scripted calls and documents structured output, session metadata, usage, and client-estimated cost fields. Current official OpenAI documentation confirms Codex can operate non-interactively with read-only sandboxing, JSONL events, and output schemas.

This is **not** a recommendation to adopt or pilot. Authentication, license suitability, runtime access, exact model selection, spend enforcement, failure behavior, witness integrity, and reviewer quality remain untested. The shared-host design also cannot provide strong host integrity.

## Calibration deliverables

- `records/capability-inventory.md` — versions, hashes, advertised controls, unavailable observations.
- `records/threat-vocabulary.md` — frozen independence dimensions and ten threat hypotheses.
- `records/query-log.md` and `records/source-register.csv` — six query families and all 24 capped candidates.
- `protocol/calibration-benchmark-protocol.v1.md` — human-reviewable safe-route and benchmark proposal.
- `records/execution-log.md`, `records/budget-ledger.md`, and `approval.md` — audit/authority records.

## Pilot-search yield

The calibration reached the 24-candidate hard ceiling: 22 candidates were reachable and plausibly relevant, one was an obvious false-positive bibliographic match, and one obsolete/invalid attestation URL returned 404. Official integration evidence had high preliminary yield (16/16 reachable across Claude, Anthropic API, and Codex strata). The evaluator-reliability stratum yielded three relevant original studies from four candidates. Provenance/security sources need query repair during a full review because one candidate URL was invalid and the remaining sources span specifications, guidance, and implementation rather than a homogeneous evidence class.

No full-text appraisal or synthesis was performed; calibration decisions only estimate yield and route later screening.

## Proposed full-review strata and revised estimates

Retain the plan's 120-candidate ceiling, but allocate it provisionally as follows for second-gate review: 24 Claude CLI/Agent SDK, 20 Anthropic API/structured-output/usage, 20 Codex controller/sandbox/MCP, 28 evaluator reliability and correlated-error research, 16 provenance/supply-chain/prompt-injection controls, and 12 mature implementations. The existing 60-full-text and 36-included ceilings remain plausible. Because official integration yield was higher than expected while research-query precision was mixed, no ceiling increase is justified; the method lead should use the remaining capacity to expand evaluator-bias and provenance families, not vendor documentation.

Budget confidence remains low until current reviewer model and route prices are selected. No live call should occur under the placeholder $125 Claude sub-ceiling alone; the second approval must set an exact per-call ceiling from current official pricing and a measured pilot token envelope.

## Safe-route assessment

The local Claude CLI subprocess is the leading *candidate* for a bounded pilot because the current surface can suppress ambient project context (`--bare`), disable tools, avoid session persistence, request schema-bound JSON, identify the session, and set a dollar ceiling. The direct API/Agent SDK remains a comparison route because it may offer cleaner programmatic control and receipts. MCP is evidence-relevant but not yet preferred: it adds configuration and trust surfaces without proving stronger reviewer isolation.

Any later route must score independence separately:

| Dimension | Local Claude subprocess, current calibration estimate |
|---|---|
| Process | plausible: separate executable/process |
| Context | potentially strong with bare mode and frozen payload; untested |
| Model family | potentially distinct; exact model/version not selected |
| Vendor | distinct from Codex/OpenAI if Anthropic-served model is verified |
| Host integrity | weak: shared user/host can alter local inputs, outputs, and witnesses |

## Deviations and limitations

No material deviation occurred. The integrated search surface returned no payload, so official documentation indexes and deterministic primary-source URLs were resolved directly; this did not change eligibility, scope, or the 24-source ceiling. Local help output is volatile and was captured as an observation with executable digests. Authentication state and credentials were deliberately not inspected. Candidate availability was checked, but most candidates were not full-text appraised during calibration.

## Required human decision

Calibration stops here. To authorize the full evidence review and any live/synthetic benchmark, the repository owner must explicitly approve the proposed protocol, eligible route(s), exact Claude model/version, credential method, current price-derived ceilings, synthetic corpus digest, controller implementation, and tool/permission policy. Until that second approval, the safe-route gate remains closed and every artifact is **unbenchmarked**.
