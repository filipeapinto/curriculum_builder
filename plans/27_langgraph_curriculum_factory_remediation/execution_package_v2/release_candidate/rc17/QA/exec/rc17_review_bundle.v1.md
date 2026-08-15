# Run 27 RC17 — staged frozen-verifier review bundle

## Decision requested

Independently determine whether graph v9 is safe to enter and capable of a fresh
N00→N90 cascade. RC14 exposed an unfrozen sidecar, RC15 exposed direct metadata
reads, and RC16 exposed ancestor-directory metadata. RC17 removes the verifier
from the repository namespace entirely: after re-hashing each D02-bound input,
the runtime stages a byte-exact frozen snapshot into a contract-and-candidate-
addressed work directory, executes only that snapshot, and denies all engine-root
metadata without exemptions. The specification, graph, model assignments,
retrieval policy, and subscription-only architecture are unchanged.

## Preserved lineage

- Graph v8 remains byte-identical at
  `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`.
- Its N00–N60 results/receipts and five failed N70 attempts remain historical;
  attempt 5 remains archived under
  `outputs/run27/archive/live_unit_v8_attempt_05_domain_pre_admission_repair`.
- RC10–RC16 and all QA records remain intact. The RC14, RC15, and RC16 findings
  are retained as failure evidence and are not reused as approval evidence.

## Closed verifier input and execution boundary

1. The curriculum schema requires a bounded, unique verifier dependency list.
   The active Arduino manifest declares the domain schema, calibration, and
   circuit library read by its verifier.
2. D02 resolves every verifier file within the active curriculum, matches it to
   D01-frozen bytes, and binds the complete closure into the domain-contract and
   effective-run digests.
3. Before any process starts, D08 re-hashes the entry point, dependencies, and
   positive/negative fixtures. It reads each source once more while staging and
   verifies the staged bytes against the frozen SHA-256, closing the hash/copy
   race.
4. The work directory is namespaced by recomputed contract digest and candidate
   digest. A conflicting prior snapshot fails closed. The original curriculum-
   relative layout is preserved beneath `frozen/`, so verifier-relative sidecars
   resolve only to staged declared files.
5. The executed argv points at the staged entry and staged candidate/fixture; the
   process working directory is the isolated work directory, never the engine.
   Its sandbox has no network or model-CLI auth/scratch rules, no engine byte
   access, and a dominant metadata deny for the entire engine root with zero
   literal or subpath exemptions.
6. The receipt binds candidate, recomputed contract, entry, dependency set,
   invocation, and fixture outcomes.

Permanent host regressions prove that declared workspace metadata remains usable,
while both an undeclared engine file and the engine directory itself cannot be
statted. The active Arduino verifier and all declared fixtures execute successfully
from the staged snapshot. Declared dependency drift fails before staging/execution.

## Carried-forward blocker closure

- D07/M02 is bounded to admitted claims and verified staged inputs and has no
  admission/verifier authority.
- Invalid initial domain/content/visual candidates remain immutable non-head
  evidence; exact-byte repair, bounded diffs, lineage preservation, and exact-head
  revalidation remain enforced.
- D08/D09/D12/D20 persist canonical bytes before downstream reads, cross-node
  replay is idempotent, and stale pre-repair state cannot overwrite repaired heads.

## Active package bindings and proof

- Graph v9: `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`.
- Approval schema v6: `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`.
- Approval contract v6: `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`.
- Governing specification: `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.
- Fresh results: `execution_package_v2/results/v9/`.
- Fresh state: `.run27_state_v9/` (explicitly bound by N70/N80/N90).
- Focused runtime/repair: `798 passed`; package: `176 passed`; combined:
  `974 passed`.
- Full runtime after final Plan 26 N13 refresh:
  `1351 passed, 2 skipped, 419 subtests passed`.
- Plan 26 reports no stale receipts; plan validation, ownership verification,
  Python compilation, and whitespace validation pass.

No billed API key, provider SDK, direct model HTTP call, wildcard retrieval host,
validation bypass, fabricated live receipt, or historical overwrite is introduced.
