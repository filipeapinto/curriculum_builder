# GOAL

Independently audit Run 27 from governing requirements through approved
specification, implementation, receipts, and live product evidence, then issue
the sole terminal recommendation.

The implementation author must not self-approve. Use the repository's witnessed
Claude-Codex QA-gate workflow (or the corrected specification's explicitly
approved independent audit mechanism) with read-only access. Verify its
hash-chain integrity after the verdict.

# TEST

1. Start the denominator with current user approval and the approved v2 digest;
   continue through Plans 20–22, retained product requirements, Run 27 criteria,
   final code/config/policy, complete test receipts, and live evidence.
2. Prove Plan 26 v1 and historical receipts/logs/results remained immutable and
   are not being used as provider-correctness or activation evidence.
3. Map every post-mortem PM finding and CA action to resolved evidence,
   intentionally historical evidence, or an open blocker. No item may disappear.
4. Recompute graph/spec/prompt/predecessor/output hashes and prove no stale
   descendant receipt is admitted.
5. Verify the final eight-job provider map, subscription-only prohibition,
   truthful preflight, least-privilege egress, production topology reachability,
   ownership closure, deterministic evidence, schema-bound status, and full
   regression denominator.
6. Recompute N70 unit and N80 workbook acceptance from raw product evidence.
7. Attempt to falsify activation with unauthorized-provider, same-family,
   false-ready, incomplete-denominator, stale-receipt, topology-bypass, and
   evidence-drift hypotheses.
8. Verify the independent gate result and its witnessed hash chain.
9. Emit a schema-valid N90 result with exactly one terminal recommendation:
   - `ACTIVATED` only if N60, N70, and N80 passed and every audit criterion holds;
   - `REMEDIATION_VERIFIED_NOT_ACTIVATED` only if implementation proof passed but
     an approved driver/live proof is truthfully unavailable;
   - `BLOCKED` for every unresolved implementation, integrity, evidence,
     convergence, or audit defect.

Report specification authority, implementation conformance, and product
activation as three separate conclusions.

# LOOP

Return each finding to its owning node, invalidate that node and all descendants,
and audit the new receipts only after forward rerun. Do not repair files inside
N90, waive findings, substitute broad reruns for broken lineage, or recommend an
unauthorized credential/provider. Stop after a verified terminal or honest
`BLOCKED`.
