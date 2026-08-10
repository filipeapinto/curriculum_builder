# Plan 21 version 3 planning log

Append-only. Versions 1 and 2 and their review reports are frozen.

### 2026-08-09 — provenance and atomicity successor

- Bound 45 inherited v1/v2 behavioral files—manifests, schemas, validators,
  contracts, prompts, research, and assessment—under a canonical bundle digest.
- Added externally signed semantic deterministic-test receipts. A PASS binds
  run/node/attempt, compiled test and subject, command, exit zero, all-PASS
  assertions, output hashes, timestamps, and a P0-pinned controller key.
- Fixed evidence paths in the compiled controller root, forbade reuse across
  tests/artifacts, validated media types and declared schemas, and bound the
  signed manifest plus complete event ID. Real-but-unrelated bytes and explicit
  FAIL JSON are rejected.
- Replaced in-memory resume consumption with SQLite `BEGIN IMMEDIATE`, expected
  checkpoint generation, and unique continuation/command/authorization rows.
  Consumption commits before activation; two callers sharing generation 1
  produce exactly one success.
- Made external trust a distinct-UID, non-model-writable prerequisite that P0
  can only observe. Missing trust pauses before P2. Engine registries are
  externally signed; selected binaries must be executable, hash-allowlisted
  Mach-O/ELF files; sandbox profiles bind existing roots and one signed
  seven-assertion executed-probe receipt.
- Added signed subtask receipts whose output source bytes are recomputed. Phase
  ledgers use the compiler-owned exact denominator and bind admitted event and
  evidence-manifest IDs.
- Replaced the effective P0 state port with a composite v3 bundle containing the
  v1 baseline and v3 assurance, with the baseline hash recomputed. P4 is an
  explicit reader, and the four live unit states remain exact.
- Made the effective compiler validate overlays after application, including
  exact prompt/subtask maps, output ownership/collisions, strict registry
  owner/schema/resolver value types, and all inherited v1 graph invariants.
- Added executable mutations for wrong prompt/subtask maps, output collisions,
  wrong owner/type registries, explicit FAIL receipts, unrelated content,
  zero-hash committed outputs, same-snapshot duplicate resume, same-UID
  self-authority, and plaintext sandbox engines.
