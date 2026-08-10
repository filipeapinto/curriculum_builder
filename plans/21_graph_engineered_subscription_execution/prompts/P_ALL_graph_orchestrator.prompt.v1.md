# GOAL

Sequence Plan 21 as an operator-facing launch prompt. This prompt is not the
control plane and never selects an edge from prose. Before P0, run the shipped
deterministic `bootstrap.command` and `bootstrap.self_test_command`. After P1,
the production compiler must compile the fully typed manifest before P2.

The implementation order is strictly sequential:

`P0 → P1 → P2 → P3 → P4 → P5 → P6`.

Read the plan, schema, research, assessment, and all node prompts in full. This
orchestrator changes no node scope, test, loop, status route, or output.

# TEST

Before activating a node, `PHASE_CONTROLLER` confirms:

1. current run, attempt, predecessor event/checkpoint, graph, prompt, policy,
   schema, route, and P0 execution-contract digests match;
2. registered symbolic scopes and typed predecessor state have resolved;
3. the event has exactly the node's compiled test ids and authorized artifact
   ids, every required PASS test has non-null evidence, and hashes recompute;
4. failure-class/outcome/reason mapping is legal; and
5. the selected guard and edge are unique in the compiled graph.

P0 starts only after the bootstrap passes. P2 starts only after P1 self-compiles
Plan 21. Claude auth/entitlement absence selects `PAUSED_PREREQUISITE`, not unit
`BLOCKED`. Contract/runtime defects select `SYSTEM_FAILURE`; external interrupt
selects `INTERRUPTED`. No plan-phase edge targets curriculum `BLOCKED`.

# LOOP

Follow each node's LOOP. A phase writes only its declared artifacts and phase
ledger. `PHASE_CONTROLLER` is the sole writer of immutable admitted events at
its declared template; it recomputes rather than trusts the phase's claimed
outcome. Markdown results and file presence cannot select an edge. On
`PAUSED_PREREQUISITE` or `INTERRUPTED`, the controller writes a continuation
binding the exact suspended node, run, source event/checkpoint, pinned digests,
reason, and next attempt. It admits a single-use RESUME only from a matching
operator-authorized resume command and only back to that same node; cross-run,
cross-phase, stale, originless, replayed, or phase-authored resume fails closed.
On `SYSTEM_FAILURE`, activate none. Never skip, edit downstream scope early,
use a shared append log, or substitute simulated/prewritten model artifacts.

Approval occurs only after P6-T24 and final independent QA pass. This prompt
writes no artifact.
