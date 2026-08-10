# Plan 20 assessment against the August 2026 graph-engineering rubric

## Verdict

**Does not meet the state of the art: 2 pass, 6 partial, 6 fail.** Plan 20 has
useful fail-closed intent, a separate cross-family judge, structured Codex
output, and several negative controls. It is nevertheless an implementation
checklist around a monolithic bridge, not a compiled prompt-execution graph.
Its third internal QA round independently reached the same practical result:
2 Critical and 1 High findings, followed by a non-convergence stop.

## Rubric score

| Criterion | Result | Repository evidence |
|---|---|---|
| GE-01 explicit graph IR | FAIL | The plan is prose; it defines no machine-readable nodes, edges, terminals, or cycle set. |
| GE-02 atomic typed nodes | PARTIAL | It specifies a worker and QA gate, but `session_bridge.finalize()` still owns many distinct operations as one unit. |
| GE-03 explicit guards | PARTIAL | Acceptance and failure branches are described, but fan-out/join, per-state failure edges, and interrupt routing are inherited vaguely from Plan 19. |
| GE-04 goal–test–loop prompts | FAIL | Plan 20 ships no executable phase/node prompts and no per-node GOAL/TEST/LOOP contracts. |
| GE-05 compiled topology | FAIL | There is no compiler, reachability check, illegal-cycle check, witness trace, or temporal safety rule. |
| GE-06 typed state/reducers | PARTIAL | Receipt schemas are proposed, but shared graph state and deterministic parallel reducers are absent. |
| GE-07 durable execution | FAIL | Step 4 says to preserve a monolithic `finalize()` while claiming later migration into Plan 19's independently checkpointed 25-state graph; QA v3 demonstrates the contradiction. |
| GE-08 boundary isolation | FAIL | In-session Claude authoring has no process boundary and cannot satisfy Plan 19 P2-T05/T06/T08/T14. “In spirit” is not enforcement. |
| GE-09 independent evaluation | PASS | Claude author / Codex judge is cross-family and the missing judge fails closed. |
| GE-10 targeted recovery | PARTIAL | It preserves checks but defines no check-to-node/artifact repair graph for its own new architecture. |
| GE-11 trace/provenance | PARTIAL | Codex receipts are specified, but graph version, prompt hash, edge decisions, and end-to-end node lineage are not. |
| GE-12 path/fault testing | PARTIAL | Several negative controls exist, but no systematic guard-boundary/path coverage or graph fault injection exists. |
| GE-13 process-level evals | FAIL | Verification is outcome/gate oriented; it does not detect redundant paths, context leakage, or unnecessary re-verification. |
| GE-14 safe evolution | PASS | It protects historical outputs and asks for explicit supersession rather than silent drift. |

## Material architectural gaps

1. **A useful subscription-backed Claude boundary now exists.** The installed
   Claude Code 2.1.226 exposes non-interactive `-p`, JSON/stream-JSON output,
   `--json-schema`, tool allow/deny lists, and permission modes. Anthropic's
   [June 15 update](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)
   says its separate monthly Agent SDK credit change is paused; for now
   `claude -p` still draws from subscription usage limits. Plan 20's premise that authoring must be
   an unbounded in-session file write is therefore obsolete. Strict
   subscription-only execution must additionally prove that separately
   billed usage credits/overage and API fallback are disabled; authentication
   alone is not metering evidence. The machine is presently logged out of Claude (`claude auth status` reports
   `loggedIn: false`), so execution must stop until subscription OAuth is
   restored and its entitlement distinguished from Console billing; the plan
   itself can still be authored and approved.
2. **One adapter can support two families without two boundary contracts.** A
   normalized worker request/receipt interface can dispatch authoring to
   `claude -p` and judging to `codex exec`, with both receiving staged inputs,
   structured schemas, bounded tools, isolated working directories, and
   normalized failures. This preserves Plan 19's single-interface invariant
   while retaining cross-family evaluation.
3. **The control graph is implicit.** Plan 20 never defines or compiles the
   execution topology. It cannot prove every state is reachable, every failure
   has a terminal/recovery edge, all cycles are bounded, or no path bypasses
   the judge.
4. **Checkpoint granularity is wrong.** `session_bridge.finalize()` performs
   many checks in one non-checkpointed sweep. Replaying or interrupting it does
   not have node-level idempotency and cannot meet Plan 19 P3-T01/T03/T09/
   T14/T15/T20 while being preserved “exactly as-is.”
5. **Context flow is unspecified.** The plan changes execution providers but
   does not separately state what each node may see. It therefore cannot prove
   reviewer independence or prevent sibling-verdict/context leakage.
6. **The test loop is not graph-complete.** The plan has a linear verification
   list, not guard-boundary enumeration, witness traces, reducer tests,
   systematic fault injection, or process-efficiency measures.

Current capability evidence also shows that Codex CLI 0.147.0 JSONL does not
emit a native executed-model field. Plan 21 therefore records pinned requested
model plus official driver/auth/binary evidence as `DRIVER_BOUND_REQUEST`, with
native model explicitly null, instead of repeating Plan 20's unsupported claim
that exact execution identity was observed.

## Required disposition

Plan 20 remains historical evidence and must not be edited or implemented. Plan
21 supersedes it only after Plan 21's own contract-freeze phase records the
exact conflicts with Plan 19 and the current repository. No production or Plan
19 file is changed merely by creating Plan 21.
