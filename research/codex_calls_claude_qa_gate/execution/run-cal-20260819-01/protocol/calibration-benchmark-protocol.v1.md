# Proposed full-review and safe benchmark protocol v1

Status: **PROPOSED — SECOND HUMAN APPROVAL REQUIRED**. This file is a calibration output, not authorization to invoke any model.

## Route gate

Before a route can run, the method lead must bind current official support, exact CLI/API/SDK version, compatible auth/license, credential-handling procedure, measurable token/cost fields, timeout/process-tree termination, synthetic-only inputs, isolated working directory, empty or read-only tool set, prompt-loading suppression, and a controller-owned output location. Any missing property returns `ROUTE_INELIGIBLE`; unavailable usage measurement returns `MEASUREMENT_UNAVAILABLE`.

The first candidate for a limited pilot is the local Claude CLI subprocess in `--bare -p` mode with `--tools ""`, explicit `--output-format json`, explicit `--json-schema`, `--no-session-persistence`, an explicit model version, a fresh UUID session, and `--max-budget-usd`. This candidate remains conditional because runtime auth, licensing, cost enforcement, and exact empty-tool behavior have not been tested or approved.

## Frozen input contract

Each case package contains only:

1. synthetic artifact bytes and SHA-256;
2. criteria and grounding bytes and SHA-256;
3. fixed reviewer prompt and SHA-256;
4. verdict JSON Schema and SHA-256;
5. case ID, condition ID, repetition ID, exact model/version/settings;
6. a canary string absent from the intended payload plus a secret-pattern scan receipt.

The reviewer cannot edit artifacts, author fixes, or write the verdict ledger. The controller captures stdout and stderr separately, validates schema and digest fields, records monotonic time and exit state, and appends a receipt.

## Verdict state machine

`READY → RUNNING → {PASS | FAIL | QA_ERROR}`.

- `PASS`: schema valid, digest bindings exact, no threshold finding, identity/usage witness present.
- `FAIL`: schema valid and at least one threshold finding names a defeated criterion and evidence.
- `QA_ERROR`: unavailable reviewer, auth/license failure, malformed or missing schema, timeout, non-zero/ambiguous failure, usage absent, over budget, wrong digest, witness failure, tool-policy violation, or canary/secret anomaly.

No automatic retry changes a verdict. At most one retry is allowed for a documented transient and must receive a new run ID while retaining the failed receipt.

## Benchmark corpus and conditions

Use 30 frozen cases: three cases for each of ten classes—known blocker, major, non-defect trap, ambiguous criterion, grounding conflict, prompt injection, schema violation, timeout, unavailable reviewer, and provenance/digest mismatch. Compare identical case bytes under:

1. fresh-context formal Codex self-family gate;
2. independent Codex session/model-family gate;
3. each feasible Claude cross-vendor route.

Run two repetitions per condition, never more than two concurrent calls. Human labels are frozen before inference; a stratified sample receives dual adjudication blinded to condition.

## Measurements

Blocker recall, false-block rate, PASS/FAIL/ERROR correctness, schema validity, evidence traceability, exact repeatability, latency, input/output tokens, reported/derived cost, and failure-state correctness. Every aggregate links to case/run IDs. Confidence intervals and the small synthetic-corpus limitation are mandatory.

## Safety and abort

- Synthetic inputs only; preflight scans for credential/key/email patterns and canary placement.
- Isolated temporary copy outside authoritative records; reviewer write access denied.
- Network disabled unless the selected supported route requires provider transport; no arbitrary tool network.
- Controller sends SIGTERM at 15 minutes and verifies process-tree termination; warning at 12 minutes.
- Global ceilings remain those in plan v1: 180 planned verdict calls, 20 retries, 6.0M/1.5M tokens, $250 total/$125 Claude, concurrency 2.
- Human may abort at any time; controller persists the terminal receipt and never converts abort to PASS/FAIL.

## Proposed second approval request

Approval should name: eligible route(s), exact reviewer model/version, auth method without exposing credentials, revised current prices and per-call ceiling, synthetic corpus version/digest, controller implementation version, and permission/tool policy. Until then the safe-route gate is closed.
