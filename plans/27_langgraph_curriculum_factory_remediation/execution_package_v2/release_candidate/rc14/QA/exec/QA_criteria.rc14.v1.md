# RC14 independent QA criteria

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
   M02 or D08, reject drift/escape/incomplete proof before entry, and include the
   contract digest in effective-run identity. D08 must parse the hash-verified
   frozen artifact-schema bytes, not later replacement bytes.
5. Bounded authoring: D07/M02 may see only admitted source claims and verified
   staged domain inputs. M02 must not claim admission or verifier authority.
6. Executable verification: D08 must use a deterministic candidate-bound receipt
   produced by the exact frozen invocation and complete positive/negative fixture
   suite under a no-network sandbox; model-declared verdicts cannot satisfy it.
7. First-version recovery: invalid initial domain/content/visual candidates must
   remain immutable and non-head; D19/M06 must target exact bytes; D20 must reject
   stale/out-of-bound/no-op repair; repaired children must retain validator
   lineage, admit as genesis where appropriate, and revalidate as exact heads.
8. Replay and physical admission: D08/D09/D12/D20 heads must have canonical bytes
   in ArtifactStore before downstream reads. Same logical heads must replay
   idempotently across different admitting nodes; conflicts must fail closed.
   Revalidation must never replace repaired bytes with stale pre-repair state.
9. Regression proof: the focused, package, and full-runtime suites must execute
   successfully, including all six RC13 reproduction paths.
10. Security/architecture preservation: exact-host retrieval, SSRF/redirect
    checks, tool-closed subscription CLIs, model assignments, topology, terminals,
    and no-billed-API/no-provider-SDK constraints must remain intact.
11. Entry safety: no blocker may make a fresh graph-v9 N00→N90 cascade dishonest,
    unverifiable, or unable to run the real N70/N80 path.
