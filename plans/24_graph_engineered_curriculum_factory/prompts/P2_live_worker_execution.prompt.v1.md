# P2 — Implement contained live worker execution

## GOAL

- `prompt_id`: `plan24.P2.live_worker_execution.v1`
- `role`: `worker_runtime_implementer`
- `objective`: Execute graph model/retrieval nodes through policy-selected live
  routes with sealed inputs, schema-bound outputs, observed identity, and
  append-only evidence.
- `non_goals`: Do not let workers route themselves, choose transitions, accept
  outputs, write controller state, browse unrelated repository files, or claim
  curriculum production from a canary.
- `authorized_inputs`: P0 authority, P1 graph/IR, routing policy and registry,
  worker artifact schemas, external capabilities declared by the run.
- `output_contract`: Selector-first adapter, containment staging, capability
  receipts, artifact admission, normalized failures, tests, live canaries, and
  P2 receipt.
- `completion_condition`: Every retained worker/route class has current live
  proof and every containment/admission negative control fails closed.

## TEST

1. A validated routing decision exists before each model call and the observed
   executed model equals the decision.
2. Worker workspaces contain only authorized staged inputs and one declared
   writable output target.
3. Requests and receipts bind graph/run/node IDs, input digests, prompt/schema,
   route/model, sandbox, timing, exit data, output digest, and failure class.
4. Missing route, timeout, mismatch, malformed response, extra file, path
   escape, undeclared read, stale output, and schema failure cannot mutate state.
5. Retries are bounded, idempotent, typed, and never convert capability proof
   into generated-unit evidence.

## LOOP

Retry only failures classified transient by frozen policy and within its bound.
Implementation defects return to their exact adapter/selector/containment
owner. A missing required external capability returns an honest
`PAUSED_PREREQUISITE` only when it is genuinely operator-supplied; factory and
tool defects are `SYSTEM_FAILURE`. Advance with verified P2 evidence only.
