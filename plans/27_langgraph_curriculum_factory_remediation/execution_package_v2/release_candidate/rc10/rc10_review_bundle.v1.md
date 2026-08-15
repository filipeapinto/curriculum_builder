# Run 27 RC10 — graph v9 live-defect recovery review bundle

## Decision requested

Independently determine whether graph v9 is safe to enter and capable of a fresh
N00→N90 cascade after genuine graph-v8 N70 attempt 5 exposed the defects below.
This is an engineering recovery only: the governing specification, topology,
terminals, eight model/effort assignments, exact-host policy, and
subscription-only Claude/Codex architecture are unchanged.

## Preserved predecessor

- Approved graph v8:
  `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml`
- Required SHA-256:
  `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`
- Its N00–N60 receipts/results and all five failed N70 attempts remain historical.
- The fifth attempt is archived at
  `outputs/run27/archive/live_unit_v8_attempt_05_domain_pre_admission_repair`.

## Live defects and corrections

1. D02 previously froze only `domain.manifest_schema`. It now compiles and hashes
   the artifact schema, manifest schema, config, curriculum calibration, verifier
   entry point/invocation, and all accept/reject fixtures. Path escape, missing
   members, drift, unproved fixtures, and oversized fixture suites fail closed.
2. D07 now passes M02 the claims and limitations from the exact admitted source
   interpretations and stages hash-verified schema/calibration/fixture text. M02
   cannot read repository paths and is explicitly forbidden to declare a verifier
   verdict.
3. D08 validates the artifact schema (not the manifest metaschema), checks exact
   admitted source identities, and calls the runtime verifier. The verifier
   re-hashes all frozen bytes, parses argv without a shell, executes the full
   positive/negative fixture suite and candidate in a no-network sandbox, and
   binds its receipt to the candidate body hash.
4. D08/D09/D12 preserve an invalid newly minted version as immutable
   pre-admission evidence without advancing a head. D19 routes M06 the exact parent
   bytes/hash. D20 checks the actual parent/child JSON-pointer diff and admits a
   repaired first version as physical/logical genesis (`version=1`,
   `parent_hash=null`) while retaining `repair_parent_hash`; the invalid parent is
   never a head.
5. Domain repairs inherit only code-owned schema/source lineage from the exact
   parent, allowing D08 revalidation without giving M06 authority over it.
6. The common graph boundary now persists each D08/D09/D12/D20 head body through
   `ArtifactStore` before downstream execution. Canonical bytes must hash to the
   logical head, and replay of the same head is idempotent.
7. Visual artifact bodies exclude output-root paths and upstream hashes so
   identical assets remain content-address stable across harmless declaration
   permutations; operational provenance remains in state/version metadata.

## Active package bindings

- Graph v9 SHA-256:
  `77e71cbf88d3436608e4c0928f0c6a501d1c054df150aae35deb6bb5f9911933`
- Approval schema v6 SHA-256:
  `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`
- Approval contract v6 SHA-256:
  `4381bc6ecc411ad48e43766391813728d8fcd1117f65240fb9c6388465142cdd`
- Governing specification SHA-256:
  `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`
- Fresh result namespace: `execution_package_v2/results/v9/`
- Fresh controller state namespace: `.run27_state_v9/`

Graph v9 adds exact ownership only where attempt 5 proved it was missing:
N20 owns verifier transport and the M02 prompt, N30 owns complete contract
freezing/source staging plus the curriculum schema/manifest, and N40 owns the
domain/content/visual admission modules, repair boundary, graph persistence bridge,
and their direct tests.

## Executed proof before review

- `python3 -m pytest -q tests/runtime/test_plan26_deterministic_nodes.py tests/runtime/test_plan26_transport.py tests/runtime/test_plan26_unit_graph.py tests/runtime/test_plan26_repair_acceptance.py tests/runtime/test_plan26_adversarial.py tests/runtime/test_plan26_model_nodes.py -x`
  → `792 passed`.
- `python3 -m pytest -q execution_package_v2/tests -x`
  → `175 passed`.
- The focused transport proof executes the real Arduino verifier and all declared
  fixtures inside the runtime sandbox, with both accepted and rejected candidate
  assertions.
- The repair proof executes invalid-v1 preservation → exact M06 parent packet →
  D20 genesis admission → D08 revalidation.
- The unit-graph proof reads all three admitted physical bodies and replays the
  same admissions without a duplicate version or head advance.

No billed API key, provider SDK, direct model HTTP call, wildcard retrieval host,
validation bypass, fabricated live receipt, or historical overwrite is introduced.

