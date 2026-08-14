# GOAL

Finish Run 27 autonomously under the currently approved execution graph, starting
from the live admitted frontier and continuing through
`N90_REQUIREMENTS_FINAL_AUDIT`. This is one terminal task, not one task per node.

Reconstruct state from the active graph, its result pattern, schema-valid results,
receipts, evidence, hashes, tests, and current filesystem bytes. Do not trust a
status summary when machine-readable evidence is available.

At this prompt's creation, graph v7 is approved; N00, N10, and N20 are admitted
`PASSED`; N30 is not admitted; and N30 exposed a real ancestor defect in N20:
`observe_codex_identity` cannot parse the real Codex CLI event stream. Preserve
all existing attempts. Investigate the actual live CLI output, repair and
re-admit N20 through the controller's recovery mechanism, rerun invalidated N30,
then continue through N40, N50, N60, N70, N80, and N90.

# EXECUTION

1. Remain the active root orchestrator. A dispatched or completed worker does not
   own the terminal objective; monitor it, independently verify its work, and
   continue immediately.
2. Execute every node prompt and verification command. Admit only schema-valid
   results with valid receipts, hashes, evidence, predecessor bindings, and write
   scope.
3. Repair ordinary failures autonomously inside the owning node's write set.
   Preserve each failed attempt, add deterministic positive and negative regression
   proof, rerun verification, and continue.
4. When a descendant exposes an ancestor defect, recover/re-admit the ancestor,
   invalidate affected descendants, and rerun forward. Never overwrite an admitted
   result or historical evidence.
5. Every retry uses a new attempt-scoped directory and new log paths. Never use
   `rm`, wildcard deletion, cleanup commands, destructive Git commands, or output
   redirection to an existing evidence file. Replace unsafe commands with safe,
   non-destructive alternatives and continue without asking the user.
6. Preserve unrelated changes and every prior graph, release candidate, QA session,
   result, receipt, log, and attempt. Do not commit, push, publish, or open a PR.
7. N70 and N80 require real production CLI/graph proof. Do not substitute fake
   transports, simulations, hand-authored intermediates, or fabricated evidence.
   Use `NOT_AVAILABLE` only where the graph permits it and real evidence proves it.
8. Follow the approved model/effort assignments exactly. Do not touch the unrelated
   active Gemini pipeline or bypass sandbox, credential, schema, QA, or write-set
   controls.
9. If a genuine graph/schema/contract defect is outside node authority, perform the
   complete versioned recovery and independent-QA loop autonomously. Continue across
   ordinary RC failures. Pause only after one final chain-valid `QA_PASSED` candidate
   requires explicit approval of exact new digests; make one consolidated approval
   request with the full digests and an exact approval sentence.

# COMPLETION GATE

Before sending any final response, reread this file and the active approved graph,
then validate the live result files. You may stop only when:

- N90 has produced a schema-valid result containing exactly one legal graph
  terminal; or
- a completed, independently verified graph-recovery candidate requires the user's
  explicit approval of exact previously unseen digests.

A passed or failed node, test failure, denied unsafe command, worker dispatch,
worker completion, background task, context compaction, progress summary, ready next
node, or failed intermediate RC is **not** permission to stop. If N90 is not terminal
and exact-digest approval is not required, continue from the actual admitted
frontier without asking what to do next.

