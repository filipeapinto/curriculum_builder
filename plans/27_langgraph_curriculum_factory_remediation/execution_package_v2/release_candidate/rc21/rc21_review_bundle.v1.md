# Run 27 RC21 — immutable guarded-verifier review bundle

## Decision requested

Independently determine whether unchanged graph-v9 implementation bytes are safe
for a fresh N00→N90 cascade. RC20 carried the final candidate-immutability and
existence-normalization repairs, but its QA transport ended in `CODEX_EXIT_1` before
any verdict. RC21 re-submits those same bytes with bounded grounding; no RC20 result
is treated as a pass or failure.

## Historical and active bindings

- Graph v8 is preserved at
  `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`,
  including N00–N60 history and five failed N70 attempts.
- Graph v9: `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`.
- Approval schema v6: `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`.
- Approval contract v6: `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`.
- Governing specification: `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.
- Fresh v9 results/state remain isolated at `execution_package_v2/results/v9/`
  and `.run27_state_v9/`.

## Verifier boundary

1. The manifest must declare a bounded unique verifier dependency closure. D02
   resolves it inside the curriculum, matches D01-frozen bytes, and includes it in
   effective-run identity.
2. D02 parses the Python verifier and rejects embedded absolute paths, native or
   process escape modules, dynamic code execution, and process-launch calls.
3. D08 re-hashes each source and re-checks bytes during staging. It stages into a
   contract/candidate-addressed system-temp namespace that explicitly refuses
   containment beneath engine or output—even when N70 output is under the engine.
4. Relative layout is preserved under `frozen/`; conflicting staged bytes fail.
   Executed argv/cwd reference only external staged entry/candidate/fixtures.
5. The sandbox is no-network, read-only across the staged workspace, no-fork, and
   has no model auth/scratch rules. It grants no engine byte access and denies all
   engine metadata without exemptions.
6. A trusted Python guard normalizes open/stat/list/readlink/access operations on
   engine paths to identical ENOENT behavior and blocks exec/spawn/system/popen.
   Candidate/fixture hashes are checked before and after execution.
7. The receipt binds candidate, contract, guard, entry, dependency set, invocation,
   and complete fixture outcomes.

Permanent tests reproduce the two RC19 blockers: candidate overwrite is denied with
original bytes retained, and an existing-to-renamed undeclared engine path cannot
change the candidate/contract verdict. Earlier byte-drift, direct metadata, ancestor
metadata, and engine-nested-output attacks remain covered. The active Arduino
verifier and all declared fixtures pass through this boundary.

Repair/replay, bounded M02 authority, exact-host retrieval, subscription-only model
CLIs, topology, terminals, and no-billed-API/no-provider-SDK constraints are unchanged.

Executed proof: package 176 passed; focused runtime/repair 802 passed; combined 978
passed; full runtime 1355 passed, 2 skipped, 419 subtests passed. Plan 26 N13 is
current with no stale receipts; plan order, ownership 75/75, compilation, and
whitespace checks pass.
