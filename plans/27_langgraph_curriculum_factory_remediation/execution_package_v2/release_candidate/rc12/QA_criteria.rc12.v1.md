# RC12 independent QA criteria

Report only blocker findings: each finding must name the criterion it defeats,
a reproducible trigger, and the consequence. Style and optional hardening are
observations.

1. Historical integrity: graph v8 must still hash to
   `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`, and
   v9 must use distinct graph/contract/schema/prompt/result/state lineage without
   overwriting v8 evidence.
2. Package coherence: graph v9, approval schema v6, contract v6, prompts,
   scanner, validators, and package tests must bind to v9/results-v9 consistently;
   all live digest claims must recompute and the real plan validator must pass.
3. Ownership: every changed production/runtime/test path must be in the exact
   sequential owner write set that implements it, with no ambiguous ownership or
   expansion into unrelated provider/test surfaces.
4. Complete freeze: D02 must bind all curriculum-owned domain inputs used by M02
   or D08 (artifact/manifest schemas, config, calibration, verifier and fixtures),
   reject drift/escape/incomplete proof, and include the contract digest in the
   effective-run identity.
5. Bounded authoring: D07/M02 may see only admitted source claims and verified
   staged domain inputs. M02 must not claim admission or verifier authority.
6. Executable verification: D08 must validate the correct artifact schema and use
   a deterministic, candidate-hash-bound verifier receipt produced by executing the
   exact frozen invocation and complete positive/negative fixture suite under a
   no-network sandbox. A model-declared verdict cannot satisfy this criterion.
7. First-version recovery: an invalid initial domain/content/visual candidate must
   remain immutable and non-head, D19/M06 must target its exact bytes/hash, D20 must
   reject stale/out-of-bound/no-op repair, and a valid repaired first child must be
   admitted as genesis while retaining separate repair lineage and revalidating.
8. Physical admission: every logical domain/content/visual/repaired head must have
   canonical bytes in ArtifactStore before a downstream reader runs; replay of the
   same checkpoint/head must be idempotent and conflicting bytes must fail closed.
9. Regression proof: the cited focused and package suites must execute successfully,
   including real verifier polarity, contract drift, exact staging, repair/retest,
   physical store, and replay cases. Do not accept assertions based only on source
   inspection where execution is available.
10. Security/architecture preservation: exact-host retrieval, SSRF/redirect checks,
    tool-closed subscription CLIs, model assignments, topology, terminals, and the
    no-billed-API/no-provider-SDK constraints must remain intact.
11. Entry safety: there must be no blocker that would make a fresh graph-v9
    N00→N90 cascade dishonest, unverifiable, or unable to run the real N70/N80 path.



