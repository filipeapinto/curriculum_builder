# RC15 independent QA criteria

Report only blocker findings: each finding must name the criterion it defeats,
a reproducible trigger, and the consequence. Style and optional hardening are
observations.

1. Historical integrity: graph v8 must still hash to
   `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`, and
   v9 must use distinct graph/contract/schema/prompt/result/state lineage without
   overwriting v8 evidence.
2. Package coherence: graph v9, approval schema v6, contract v6, prompts,
   scanner, validators, and package tests must bind to v9/results-v9 consistently;
   all digest claims must recompute and the real plan validator must pass.
3. Ownership: every changed production/runtime/test path must be in the exact
   sequential owner write set that implements it, without ambiguous ownership.
4. Complete freeze: D02 must bind every curriculum-owned domain input used by
   M02 or D08, including verifier code, fixtures, schemas, calibration, and
   sidecar dependencies. Missing declarations, path escape, duplicates, and
   post-D01 drift must fail before entry, and the complete domain-contract digest
   must participate in effective-run identity.
5. Closed verifier execution: D08 must re-hash the complete D02-frozen verifier
   input set and execute the exact frozen invocation and fixtures under a
   no-network sandbox that cannot read undeclared curriculum or engine files.
   Its candidate-bound receipt must identify the dependency digest set.
6. Replay invariance: changing undeclared or declared post-D02 repository bytes
   must never produce a different verdict for the same candidate and frozen
   contract. Declared drift must fail closed before verifier execution.
7. Bounded authoring: D07/M02 may see only admitted source claims and verified
   staged domain inputs. M02 must not claim admission or verifier authority.
8. First-version recovery: invalid initial domain/content/visual candidates must
   remain immutable and non-head; D19/M06 must target exact bytes; D20 must reject
   stale/out-of-bound/no-op repair; repaired children must retain validator
   lineage, admit as genesis where appropriate, and revalidate as exact heads.
9. Replay and physical admission: D08/D09/D12/D20 heads must have canonical bytes
   in ArtifactStore before downstream reads. Cross-node replay must be idempotent,
   conflicts must fail closed, and revalidation must preserve repaired bytes.
10. Regression proof: the focused, package, and full-runtime suites must execute
    successfully, including all six RC13 reproductions and RC14's unfrozen
    circuit-library reproduction.
11. Security/architecture preservation: exact-host retrieval, SSRF/redirect
    checks, tool-closed subscription CLIs, model assignments, topology, terminals,
    and no-billed-API/no-provider-SDK constraints must remain intact.
12. Entry safety: no blocker may make a fresh graph-v9 N00→N90 cascade dishonest,
    unverifiable, or unable to run the real N70/N80 path.
