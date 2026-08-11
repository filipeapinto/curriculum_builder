# GOAL

Implement `N12_EVIDENCE_ARTIFACTS` after N00. Build repository-specific,
append-only product evidence and immutable artifact services separate from
LangGraph checkpoints.

Implement canonical containment, symlink rejection, staging/atomic admission,
version/head/parent relationships, content hashes, idempotency keys, hash-linked
events, activation/route/execution/checkpoint indexes, accepted-byte protection,
terminal ledger, evidence high-water marks, and independent integrity audit.

# TEST

1. Every admitted artifact is within the correct root and hash-addressed.
2. In-place parent/accepted mutation and symlink/path escape fail before write.
3. Equal replay is idempotent; conflicting duplicate admission fails.
4. Crash before/after staging/admission leaves either old valid state or one
   complete new artifact, never partial accepted evidence.
5. Event/index chains detect deletion, insertion, reorder, or byte change.
6. Product evidence cannot be fabricated from checkpoint or fake-test records.

Write `results/N12_EVIDENCE_ARTIFACTS.result.v1.md` with artifact protocol,
integrity/crash tests, commands, and hashes.

# LOOP

Fix only the path guard, artifact store, event ledger, index, or test fixture
owning the failure. Preserve forensic bytes. Stop if integrity can self-heal,
accepted bytes are writable, or a partial admission can appear committed.

