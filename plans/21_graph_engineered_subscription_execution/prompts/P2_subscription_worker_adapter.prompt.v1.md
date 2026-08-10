# GOAL

Execute Plan 21 node **P2 — Subscription worker adapter**. Build one normalized
request/receipt interface with two drivers:

- Claude Code `claude -p` authoring, safe mode (not bare), no session
  persistence, bounded tools, structured JSON/schema output, and unambiguous
  subscription-plan entitlement with machine-verifiable included-allocation-only
  metering and separately billed credits/overage disabled; and
- Codex `codex exec` judging, ChatGPT login, ephemeral/config-isolated call,
  structured output/events, included ChatGPT allocation with credits/API fallback
  disabled, and a reconstructable outer readable-root OS sandbox. `-C` plus
  read-only alone is not structural read isolation.

The controller admits model bytes. Prefer bounded sealed stdin and tool-free
Claude; split oversized tasks instead of broadening access. Normalize provider,
family, requested model, optional native observed model, identity assurance,
auth class, CLI binary/version/hash, argv digest, prompt/input/output hashes,
events, result, usage/timing, and failure.

Codex CLI 0.147.0 exposes no native executed-model field. Record
`identity_assurance: DRIVER_BOUND_REQUEST`, the pinned `-m` argv and registry
authorization, and `native_observed_model: null`. This can establish driver/
provider family and requested-model authorization, not native observation. A
model self-report is never evidence. P0 explicitly records the supersession of
Plan 19's native equality assertion for this driver.

# TEST

1. **P2-T01 — Schemas.** Both family fixtures validate; unknown fields/secrets fail or redact.
2. **P2-T02 — Adapter-local unity.** Both drivers implement the shared interface; no provider bypass exists inside the new adapter. Repository-wide migration is exclusively P4-T04/P4-T05.
3. **P2-T03 — Auth/entitlement/metering.** Codex proves ChatGPT login, plan subtype, included-allocation-only mode, ChatGPT credits disabled, and API fallback disabled. Claude proves allowlisted subscription OAuth/seat subtype, included-allocation-only mode, separately billed usage credits/overage disabled, and API fallback disabled. Generic first-party, Console OAuth, usage-based Enterprise, login alone, or unprovable metering selects `PAUSED_PREREQUISITE`.
4. **P2-T04 — No paid override.** Any closed override set, separately billed credits/overage, API fallback, pay-as-you-go seat, or contradictory capability combination fails before launch; log names/status and evidence hashes only.
5. **P2-T05 — Claude canary.** Real structured output plus native identity fields actually exposed by the CLI.
6. **P2-T06 — Codex canary.** Real structured output/events with DRIVER_BOUND_REQUEST and null native model unless this exact version proves otherwise.
7. **P2-T07 — Read containment.** Reconstruct the frozen sandbox engine/profile from bytes and canonical roots; outer containment denies relative, absolute, traversal, symlink, mount, undeclared-root, network-destination, and credential-boundary escapes without leakage.
8. **P2-T08 — Output containment.** Models cannot write admitted paths; controller atomically writes exactly one validated output.
9. **P2-T09 — Malformed output.** Extra/missing/mixed/schema-invalid output rejects atomically.
10. **P2-T10 — Path escape.** Traversal/symlink output escape rejects prelaunch/admission.
11. **P2-T11 — Tool policy.** CLI args and sandbox profile digests equal frozen role policy; widening fails.
12. **P2-T12 — Prompt injection.** Input cannot alter tools, route, schema, identity policy, edge, or terminal.
13. **P2-T13 — Identity assurance.** The pre-existing, read-only `contracts/identity_assurance_policy.v1.yaml` defines both drivers, roles, provider/family, authentication class, and minimum assurance. Native identity, when present, must match; driver-bound Codex evidence never populates or claims native identity. P2 must not invent or edit the policy to fit a receipt.
14. **P2-T14 — Failures.** Auth, entitlement, rate limit, timeout, exit, malformed output, policy violation, and external fact block remain distinct.
15. **P2-T15 — Composed phase replay.** The phase ledger under `{execution_contract_digest}:P2:{phase_attempt}` enumerates adapter build, Claude canary, Codex canary, and result-evidence commit with domain-separated subtask keys. Crash/restart before and after each commit cannot duplicate calls/receipts, overwrite output, skip uncommitted work, or admit PASS before every declared artifact is committed.
16. **P2-T16 — Cross-family.** Author/judge provider drivers and families differ before execution.
17. **P2-T17 — Judge context.** No author session/transcript or sibling verdict.
18. **P2-T18 — Historical regressions.** Disabled provider, unsupported effort, untestable receipt, dirty deletion, exec/review confusion, and Gemini-shaped receipt mismatch are biting fixtures.

# LOOP

Fix one adapter, driver, schema, sandbox profile, or fixture. Rerun P2-T01–T04,
P2-T07–T09, P2-T13, and P2-T16 for both drivers, then affected tests. Repeat
real calls only for policy-declared transient failures.

Pause—do not work around—with `AUTHENTICATION_MISSING` when Claude is logged
out, or `SUBSCRIPTION_ENTITLEMENT_UNPROVEN` when included-allocation-only
metering cannot be proven and separately billed credits excluded. Stop to SYSTEM_FAILURE
if paid routing, structured output, declared identity assurance, or structural
containment cannot be proven. Write declared outputs and the phase ledger only.
`PHASE_CONTROLLER` writes any pause continuation and alone admits the routing
event after exact test/artifact/binding validation; the phase and Markdown
result cannot drive routing. No shared log.
