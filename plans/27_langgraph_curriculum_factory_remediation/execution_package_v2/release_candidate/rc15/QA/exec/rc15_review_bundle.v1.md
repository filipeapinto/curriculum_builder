# Run 27 RC15 — closed verifier-input review bundle

## Decision requested

Independently determine whether graph v9 is safe to enter and capable of a fresh
N00→N90 cascade. RC14 correctly failed because the Arduino verifier could read a
curriculum-owned sidecar that D02 had not digest-bound. RC15 closes that class of
input: a curriculum must declare every verifier dependency, D02 freezes each exact
file into the effective-run digest, and D08 grants the verifier only those frozen
files, its frozen fixtures/entry point, the exact candidate, and executable runtime
dependencies. The specification, topology, terminals, eight model assignments,
exact-host retrieval policy, and subscription-only Claude/Codex architecture are
unchanged.

## Preserved lineage

- Approved graph v8 remains byte-identical at
  `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`.
- Graph-v8 N00–N60 receipts/results and all five failed N70 attempts remain
  historical. Attempt 5 remains archived under
  `outputs/run27/archive/live_unit_v8_attempt_05_domain_pre_admission_repair`.
- RC10–RC14 and every QA session are retained. RC14's `FAIL` verdict and
  `RC14-QA-001` reproduction are historical evidence, not approval evidence.

## RC14 blocker closure

`RC14-QA-001` demonstrated that changing only
`curricula/arduino_kit/circuit_library.v1.yaml` after D02 could change the same
candidate's verdict. RC15 closes the failure at both boundaries:

1. `curriculum.schema.v5.json` requires a bounded, unique `verifier.dependencies`
   array of curriculum-relative file paths.
2. The active Arduino manifest declares the domain schema, calibration, and
   circuit library used by `verify_domain.py`.
3. D02 resolves every declaration inside the active curriculum, requires the
   exact D01-frozen digest, and incorporates the frozen references in the domain
   contract and effective-run digest. Missing, escaped, duplicate, oversized, or
   drifted dependencies fail before entry.
4. `CliTransport.verify_domain` re-hashes every dependency before invoking the
   verifier. Its no-network sandbox no longer reads the whole engine root; it can
   read only the frozen entry point, frozen dependencies, frozen fixtures, exact
   candidate workspace, and required executable/runtime roots.
5. The verifier receipt records the ordered dependency SHA-256 set. A direct
   regression changes only a dependency after contract compilation and proves a
   `VerifierFault` occurs before verifier execution. The active Arduino verifier
   and complete positive/negative fixture suite also pass under the reduced
   sandbox.

## Carried-forward blocker closure

- D07/M02 sees only admitted source claims and verified staged domain inputs;
  M02 cannot claim verifier or admission authority.
- D08 parses the exact hash-verified artifact-schema bytes and binds its receipt
  to the candidate bytes and frozen verifier invocation.
- Invalid initial domain/content/visual candidates remain immutable non-head
  evidence. D19/M06 targets exact bytes, and D20 admits bounded valid repairs
  while preserving validator and repair lineage.
- D08/D09/D12/D20 persist canonical artifact bytes before downstream reads,
  replay idempotently across admitting nodes, and never replace repaired heads
  with stale pre-repair state.

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

N70, N80, and N90 controller commands bind the v9 state directory explicitly.
The shared historical controller default is unchanged.

## Executed proof before review

- Focused runtime/repair tests: `797 passed`.
- Execution-package tests: `176 passed`.
- Combined exact focused/package denominator: `973 passed`.
- Full runtime tests after refreshing the legitimately stale Plan 26 N13
  transport receipt: `1350 passed, 2 skipped, 419 subtests passed`.
- The Plan 26 controller reports no stale receipts.
- The real plan validator reports valid N00→N90 order; ownership verification,
  Python compilation, and whitespace validation pass.
- Direct regressions cover all six RC13 findings plus RC14's post-D02 verifier
  dependency drift. The active verifier executes successfully with only its
  declared dependency closure.

No billed API key, provider SDK, direct model HTTP call, wildcard retrieval host,
validation bypass, fabricated live receipt, or historical overwrite is introduced.
