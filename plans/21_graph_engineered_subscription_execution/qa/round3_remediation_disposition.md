# Round-three remediation disposition

Status: `UNAPPROVED_REMEDIATION_REQUIRED` until three targeted closure
addenda independently report zero unresolved Critical/High findings.

This disposition accepts every Critical/High finding in the three `v3` review
files. The revised package introduces controller-admitted, evidence-complete
phase events; exact current-run and current-attempt guard bindings; typed
same-run/same-node continuations and resume commands; closed failure mappings;
closed subscription metering and sandbox contracts; producer-resolvable ports;
phase ledgers and idempotency; restored historical lifecycle vocabulary; and a
non-vacuous typed denominator with deterministic cross-field validation.

Required closure probes:

1. Attempt a P6 PASS with empty, missing, duplicated, failing, null-hash, wrong
   set-digest, wrong-run, wrong-attempt, stale-contract, or stale-checkpoint
   evidence. Every case must fail controller admission.
2. Attempt originless, cross-run, cross-phase, stale-source, stale-digest,
   skipped-attempt, hash-unbound, or replayed resume. Every case must fail.
3. Delete or corrupt each mandatory edge, local schema, registered contract,
   producer artifact, state dependency, owner, idempotency key, denominator
   mutation kind, ID, or aggregate. Every case must fail deterministically.
4. Validate that logged-out Claude maps to `AUTHENTICATION_MISSING`; an
   authenticated but unproven included-only allocation maps to
   `SUBSCRIPTION_ENTITLEMENT_UNPROVEN`; and separately billed credits/overage,
   ChatGPT credits, API fallback, usage-based seats, and contradictory override
   combinations cannot satisfy P2 PASS.
5. Recheck Plan 19 run-state vocabulary, cold second-process resume, exact four
   workbook judges, live multi-unit `--all`, RT-7 exact scope/pause behavior,
   and format-aware historical census without weakening prior evidence.

The closure addenda may write only their own review files. A failed targeted
closure yields `UNAPPROVED_REQUIRES_NEW_VERSION`; it does not authorize a
fourth full review or further edits to version 1.
