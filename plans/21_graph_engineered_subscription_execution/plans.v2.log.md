# Plan 21 version 2 planning log

Append-only. Version 1 and all of its QA reports remain frozen.

### 2026-08-09 — successor created after failed targeted closure

- Bound the v2 overlay to the exact SHA-256 of the frozen v1 graph manifest.
- Added source-bearing evidence manifests. Controller admission now uses the
  compiled test/artifact denominators and resolved source paths, requires
  existing regular files under authorized roots, recomputes file sizes and
  SHA-256 values, computes deterministic artifact aggregates, and binds the
  event ID to the complete admitted event.
- Added externally owned Ed25519 resume authorizations. The controller verifies
  exact external authorization bytes against a P0-pinned public key, requires a
  safe OS-owned root outside every model workspace, checks time/run/node/attempt
  bindings, and atomically persists continuation and command consumption before
  activation. Exact replay is a hard failure.
- Made every registry entry—not merely referenced entries—subject to usage,
  schema existence/meta-validation, resolver existence, producer order, and
  resolved-value validation.
- Bound sandbox proof to existing profile, engine, independently resolved-root,
  and seven escape-probe source files, including byte hashes, OS owner/mode,
  exact roots, and a non-model-writable operator authority root.
- Moved phase-ledger denominators into compiled P0–P6 node contracts. A ledger
  may report completion but can never choose which subtasks were required.
- Restored exact live unit states: `ACCEPTED`, `ACCEPTED_PENDING_REVIEW`,
  `BLOCKED`, and `SYSTEM_FAILURE`; the pending-review state is explicitly
  nonterminal and P4 owns migration.
- Added GOAL/TEST/LOOP v2 prompt addenda for P0–P6 and P_ALL while preserving the
  audited v1 prompts as the immutable base.
- Expanded the bootstrap self-test with real temporary evidence bytes, missing
  sources, fabricated hashes, self-denominated P6 ledger, real Ed25519 signing
  and forged-signature rejection, duplicate resume consumption, and executable
  sandbox/profile/root/probe evidence.
