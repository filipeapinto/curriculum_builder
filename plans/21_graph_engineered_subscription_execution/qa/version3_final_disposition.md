# Plan 21 version 3 final disposition

Status: `UNAPPROVED_FINAL_QA_FAILED`

All three final v3 reviews failed. The package must not be executed or described
as state-of-the-art compliant. Findings that remain Critical/High across the
reviews are:

1. The compiler-owned command, test, artifact, and effective-node registries are
   not yet applied as immutable runtime inputs, so caller-supplied maps can
   shrink or substitute otherwise valid signed evidence.
2. Event, manifest, ledger, and subtask receipts attempt to contain one
   another's final content hashes, creating a cryptographic construction cycle.
   Linkage needs an acyclic commit protocol (for example: content-addressed
   evidence/receipts, then ledger root, then terminal event) with no back-edge.
3. Trust compares against a claimed model UID rather than the actual process
   credential; engine validation can be fooled by magic bytes; and the sandbox
   contract does not fully constrain writable/readable root purposes.
4. Resume CAS correctly serializes two callers, but is not composed in one
   transaction with verified authorization, activation outbox, and recovery;
   arbitrary unsigned identifiers can be consumed.
5. Subtask receipts can reuse an idempotency key or output source globally, and
   their command/output semantics are not bound tightly enough to compiled
   subtask definitions.
6. Missing external trust is described as a prerequisite pause but is not
   representable by the inherited phase-result failure mapping and graph edge.

Verified improvements remain useful evidence: Plan 20's August-2026 gap score,
the research rubric, goal/test/loop prompt suite, exact lifecycle/history
requirements, subscription-only metering distinctions, driver-bound Codex
identity honesty, 45-file behavioral-base binding, and the isolated SQLite
single-winner/cold-replay test. A successor must start from the final v3 review
reports and use a new version; v1-v3 are frozen failed designs.
