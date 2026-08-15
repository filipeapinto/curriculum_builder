# Run 27 RC18 — external staged-verifier review bundle

## Decision requested

Independently determine whether graph v9 is safe to enter and capable of a fresh
N00→N90 cascade. RC17 correctly found that the prescribed N70 output lives beneath
the engine, so its staged verifier was still inside the metadata-denied namespace.
RC18 places every verifier workspace under a namespaced system-temporary root that
is explicitly proven outside both engine and output roots. It then executes only
a byte-exact D02-frozen snapshot there while denying all engine metadata. The
specification, graph, model assignments, exact-host policy, and subscription-only
Claude/Codex architecture are unchanged.

## Preserved lineage

- Graph v8 remains byte-identical at
  `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`.
- Its N00–N60 results/receipts and five failed N70 attempts remain historical;
  attempt 5 remains archived under
  `outputs/run27/archive/live_unit_v8_attempt_05_domain_pre_admission_repair`.
- RC10–RC17 and all QA sessions remain intact. RC14–RC17 failures are preserved
  engineering evidence, never approval evidence.

## Verifier closure and real-N70 integration

1. The curriculum schema requires a bounded unique dependency list; the active
   Arduino manifest declares the schema, calibration, and circuit library its
   verifier reads.
2. D02 resolves every verifier file inside the active curriculum, matches the
   exact D01-frozen digest, and binds the complete closure into effective-run
   identity.
3. D08 re-hashes all entry/dependency/fixture sources and re-checks the bytes while
   staging, closing both post-D02 drift and hash/copy races.
4. `domain_verifier_work_root` derives a stable per-output namespace beneath the
   resolved system temporary directory and refuses it if it is equal to or below
   either the engine or output root. A direct regression uses the exact production
   shape—`output = engine/outputs/run27/live_unit`—and proves the selected verifier
   root is outside both.
5. Under that external root, contract and candidate digests identify the work
   directory. `frozen/` preserves declared curriculum-relative layout, while
   conflicting staged bytes fail closed.
6. The argv points to the staged entry and staged candidate/fixture, and cwd is the
   external work directory. The sandbox denies network, omits model CLI auth and
   scratch rules, grants no engine byte reads, and denies metadata for the entire
   engine root with no exemptions.
7. The receipt binds candidate, recomputed contract, entry, dependency set,
   invocation, and complete fixture outcomes.

Host regressions prove: declared workspace metadata remains usable; direct stat of
an undeclared engine file fails; stat of the engine directory itself fails; an
engine-nested N70 output still maps to an external verifier root; the active Arduino
verifier and fixtures run from staged bytes; and declared drift fails pre-execution.

## Carried-forward recovery guarantees

- M02 authoring remains bounded and has no verifier/admission authority.
- Invalid initial domain/content/visual versions remain immutable non-head evidence;
  repair stays exact, bounded, lineage-preserving, and exact-head revalidated.
- D08/D09/D12/D20 physical persistence and cross-node replay remain fail-closed and
  idempotent, without stale repair overwrite.

## Active bindings and executed proof

- Graph v9: `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`.
- Approval schema v6: `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`.
- Approval contract v6: `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`.
- Governing specification: `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.
- Fresh results: `execution_package_v2/results/v9/`; fresh explicit state:
  `.run27_state_v9/`.
- Focused runtime/repair: `799 passed`; package: `176 passed`; combined:
  `975 passed`.
- Full runtime after final Plan 26 N13 refresh:
  `1352 passed, 2 skipped, 419 subtests passed`.
- Plan 26 reports no stale receipts. Plan validation, ownership verification,
  compilation, and whitespace validation pass.

No billed API key, provider SDK, direct model HTTP call, wildcard retrieval host,
validation bypass, fabricated live receipt, or historical overwrite is introduced.
