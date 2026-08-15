# Run 27 RC14 — graph v9 replay-boundary recovery review bundle

## Decision requested

Independently determine whether graph v9 is safe to enter and capable of a fresh
N00→N90 cascade. RC13 correctly failed with six reproduced blockers. RC14 fixes
all six in the production paths and adds a direct regression for every trigger.
The governing specification, topology, terminals, eight model/effort assignments,
exact-host policy, and subscription-only Claude/Codex architecture are unchanged.

## Preserved lineage

- Approved graph v8 remains byte-identical at
  `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`.
- Graph-v8 N00–N60 receipts/results and all five failed N70 attempts remain
  historical. Attempt 5 remains archived under
  `outputs/run27/archive/live_unit_v8_attempt_05_domain_pre_admission_repair`.
- RC10–RC13 and their QA sessions are retained. RC13's verdict is FAIL and is
  not reused as approval evidence.

## RC13 blocker closure

1. `RC13-QA-001`: graph persistence now uses artifact-scoped admission identity
   and recognizes the exact physical current head before attempting admission.
   D20→D08/D09/D12 replay cannot create a node-scoped duplicate version.
2. `RC13-QA-002`: D09 compares an admitted-current content record with the real
   `content_head`; the undefined `current_head` branch is removed and executed by
   the repaired-content regression.
3. `RC13-QA-003`: D20 inherits `schema_path` and `domain_hash` for content from
   the unique immutable repair parent. The child is then revalidated by D09 as
   the exact current head without reminting.
4. `RC13-QA-004`: D12 detects an exact admitted-current visual record and
   validates its repaired portable body and content lineage. It no longer mints
   a stale successor from pre-repair `visual_results`. D20 also preserves the
   visual `parents` metadata required for this check.
5. `RC13-QA-005`: D02 now rejects a missing or incomplete domain declaration at
   the pre-entry freeze boundary. There is no nullable production
   `domain_contract` success path.
6. `RC13-QA-006`: D08 requires the candidate schema path to equal D02's frozen
   artifact-schema path, hashes the exact bytes it parses, and fails closed if
   that digest differs from the frozen SHA-256.

## Carried-forward live-defect repairs

- D02 freezes artifact/manifest schemas, config, calibration, verifier entry and
  invocation, and the complete positive/negative fixture set.
- D07 stages only verified inputs and exact admitted source claims/limitations;
  M02 cannot claim verifier or admission authority.
- The runtime verifier re-hashes frozen inputs, parses argv without a shell,
  runs candidate and fixtures in a no-network sandbox, and binds its receipt to
  the candidate body hash.
- Invalid initial domain/content/visual candidates remain immutable non-head
  evidence. D19/M06 target the exact bytes; D20 checks the actual JSON-pointer
  diff and admits a valid repaired first child as physical/logical genesis while
  retaining separate repair lineage.
- D08/D09/D12/D20 logical admissions persist canonical bytes through
  `ArtifactStore` before downstream execution.

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

- Focused runtime/repair suite: `796 passed`.
- Execution-package suite: `176 passed`.
- Combined exact focused/package denominator: `972 passed`.
- Full runtime suite after refreshing the legitimately stale Plan 26 N13
  transport receipt through its real host-level verifier:
  `1349 passed, 2 skipped, 419 subtests passed`.
- The real plan validator reports valid N00→N90 order.
- The direct regressions cover all six RC13 triggers, including cross-node
  physical replay, content lineage/current-head replay, repaired visual-head
  preservation, incomplete D02 refusal, and post-D02 schema drift refusal.

No billed API key, provider SDK, direct model HTTP call, wildcard retrieval host,
validation bypass, fabricated live receipt, or historical overwrite is introduced.
