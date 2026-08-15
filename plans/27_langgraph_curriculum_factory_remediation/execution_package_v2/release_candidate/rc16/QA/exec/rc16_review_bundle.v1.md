# Run 27 RC16 — byte-and-metadata-closed verifier review bundle

## Decision requested

Independently determine whether graph v9 is safe to enter and capable of a fresh
N00→N90 cascade. RC14 found an unfrozen verifier sidecar; RC15 then found that
global metadata access could still let an undeclared repository file's size alter
a verdict. RC16 closes both channels. Every legitimate verifier file is declared,
frozen, and re-hashed, while the verifier sandbox denies both byte and metadata
access to undeclared engine files. The specification, topology, terminals, model
assignments, exact-host policy, and subscription-only Claude/Codex architecture
remain unchanged.

## Preserved lineage

- Approved graph v8 remains byte-identical at
  `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`.
- Graph-v8 N00–N60 receipts/results and all five failed N70 attempts remain
  historical. Attempt 5 remains archived under
  `outputs/run27/archive/live_unit_v8_attempt_05_domain_pre_admission_repair`.
- RC10–RC15 and every QA record remain intact. RC14's sidecar finding and RC15's
  metadata-channel finding are preserved failure evidence, not approval evidence.

## RC14 and RC15 blocker closure

1. `curriculum.schema.v5.json` requires a bounded, unique
   `verifier.dependencies` array. The Arduino manifest declares every file read by
   `verify_domain.py`: domain schema, calibration, and circuit library.
2. D02 resolves each declaration within the active curriculum, requires the exact
   D01-frozen digest, and includes all references in the domain contract and
   effective-run identity. Missing, escaped, duplicate, oversized, or drifted
   dependencies fail before entry.
3. D08 re-hashes the entry point, dependencies, and complete accept/reject fixture
   suite before execution, and records the ordered dependency digest set in its
   candidate-bound receipt.
4. The verifier uses a distinct no-network sandbox profile without model-CLI
   scratch or subscription-authentication rules. Content reads remain limited to
   the exact frozen files, executable/runtime roots, and candidate workspace.
5. macOS process bootstrap needs general metadata access. The verifier profile
   therefore adds a dominant metadata-deny filter for the entire engine root,
   with exemptions only for exact frozen/readable files and literal ancestor
   directories needed for path traversal. Sibling/undeclared repository files
   remain unobservable by `stat`, while declared files remain executable.
6. A permanent host regression proves an allowed declared file can be statted and
   an undeclared sibling cannot. The active Arduino verifier and all its fixtures
   pass under this profile. The separate dependency-drift regression proves a
   changed declared sidecar fails before execution.

## Carried-forward blocker closure

- D07/M02 sees only admitted source claims and verified staged domain inputs;
  M02 cannot claim admission or verifier authority.
- D08 parses the exact frozen artifact-schema bytes.
- Invalid initial domain/content/visual candidates remain immutable non-head
  evidence. D19/M06 targets exact bytes, while D20 bounds and validates repairs
  and preserves validator/repair lineage.
- D08/D09/D12/D20 persist canonical bytes before downstream reads, replay
  idempotently across nodes, and preserve repaired heads during revalidation.

## Active package bindings

- Graph v9 SHA-256:
  `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`
- Approval schema v6 SHA-256:
  `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`
- Approval contract v6 SHA-256:
  `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`
- Governing specification SHA-256:
  `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`
- Fresh result namespace: `execution_package_v2/results/v9/`
- Fresh controller state namespace: `.run27_state_v9/`

N70, N80, and N90 bind the v9 state directory explicitly. The historical default
state directory is unchanged.

## Executed proof before review

- Focused runtime/repair tests: `798 passed`.
- Execution-package tests: `176 passed`.
- Combined exact focused/package denominator: `974 passed`.
- Full runtime tests after the final Plan 26 N13 receipt refresh:
  `1351 passed, 2 skipped, 419 subtests passed`.
- The Plan 26 controller reports no stale receipts.
- The real plan validator, integration-ownership verifier, Python compilation,
  and whitespace validation pass.
- Direct regressions cover all six RC13 findings, RC14's declared-sidecar drift,
  and RC15's undeclared metadata-stat channel.

No billed API key, provider SDK, direct model HTTP call, wildcard retrieval host,
validation bypass, fabricated live receipt, or historical overwrite is introduced.
