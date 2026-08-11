# Plan 26 implementation graph QA criteria v3

These criteria bind every implementation node and the final audit. Version 3
changes only execution efficiency and enforcement; it does not weaken product
acceptance or replace the required production LangGraph runtime.

## Reject immediately

- Implementing a project-management graph instead of the curriculum factory.
- Replacing LangGraph with a handwritten production controller or silent legacy fallback.
- Importing or invoking LangChain chat wrappers, provider SDKs, or direct model HTTP APIs.
- Allowing a model to choose routing, joins, retries, admission, acceptance, resume, or terminals.
- Claiming product success from code, prompts, tests, compilation, probes, simulation, or fake transports.
- Admitting a partial, duplicate, extra, stale, failed, `NOT_RUN`, or cross-unit denominator member.
- Replaying a committed external call or mutating accepted bytes.
- Resuming after identity, digest, evidence, checkpoint, executable, or accepted-byte drift.
- Using `PAUSED_PREREQUISITE` for a tool, transport, schema, render, integrity, or implementation fault.
- Admitting a scheduler receipt after a required command returned nonzero.
- Admitting a node that wrote outside its manifest write set.
- Reusing a cached node after its graph, prompt, spec, predecessor receipt, lock, contract, or output hash changed.

## Efficient verification policy

1. Every node runs its focused deterministic verification in an isolated workspace.
2. Major joins run integration slices covering their newly composed boundary.
3. N50 runs the complete deterministic, integration, adversarial, and regression suite.
4. N90 independently audits the immutable N50 suite receipt instead of rerunning an unchanged suite.
5. No test is deleted, weakened, skipped, or waived to improve execution time.
6. Historical Markdown and raw logs remain auditable but are not injected into ordinary node context.
7. Claude Sonnet receives compact predecessor receipts and retrieves additional evidence only when needed.
8. Successful nodes are cached only by verified content hashes; changed inputs invalidate the node and descendants.

## Required final proof

1. Exact pinned dependency and official API-contract tests.
2. Complete typed state/reducer authority and topology reports.
3. Exactly eight model jobs with package-relative prompts and schemas.
4. Structural model-workspace isolation and authorization before transmission.
5. Exact fan-out/barrier and every-page denominators.
6. Dual checkpoint/evidence correlation and full crash/resume matrix.
7. Targeted immutable repair and accepted-unit/workbook release denominators.
8. One production CLI path with no legacy/simulation fallback.
9. Full deterministic, integration, adversarial, and regression suites.
10. Authorized live product evidence before activation; otherwise the truthful verdict is `IMPLEMENTED_NOT_ACTIVATED`.
11. Runtime egress enforcement proves that only authorized source retrieval and sandboxed registered model CLI operations can access the network.
12. CI regenerates the dependency lock and fails on any byte drift.
