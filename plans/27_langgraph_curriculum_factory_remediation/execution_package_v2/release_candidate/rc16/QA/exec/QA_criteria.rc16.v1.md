# RC16 independent QA criteria

Report only blocker findings: each finding must name the criterion it defeats,
a reproducible trigger, and the consequence. Style and optional hardening are
observations.

1. Historical integrity: graph v8 must still hash to
   `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`, and
   v9 must retain separate graph/contract/schema/prompt/result/state lineage.
2. Package coherence: graph v9, approval schema v6, contract v6, prompts,
   scanner, validators, and package tests must consistently bind v9/results-v9;
   digest claims must recompute and the real plan validator must pass.
3. Ownership: every changed production/runtime/test path must have one exact
   sequential owner write set without ambiguity.
4. Complete freeze: D02 must bind every curriculum-owned domain input used by
   M02 or D08, including verifier code, fixtures, schemas, calibration, and
   sidecars. Missing declaration, path escape, duplicates, and drift must fail
   before entry, and the full contract digest must identify the effective run.
5. Closed verifier execution: D08 must re-hash the complete frozen verifier input
   set and execute the exact invocation/fixtures in a no-network sandbox. The
   process must have neither byte nor metadata access to undeclared curriculum or
   engine files, and must not receive model-CLI authentication/scratch rules.
6. Replay invariance: changing any undeclared repository file or any declared
   dependency after D02 must never yield a different verdict for the same candidate
   and frozen contract. Declared drift must fail before execution; undeclared bytes
   and metadata must be unobservable.
7. Bounded authoring: D07/M02 may see only admitted source claims and verified
   staged domain inputs, with no admission or verifier authority delegated to M02.
8. First-version recovery: invalid initial domain/content/visual candidates remain
   immutable non-head evidence; repair targets exact bytes, stays within the named
   scope, preserves validator lineage, and revalidates the exact repaired head.
9. Replay and physical admission: D08/D09/D12/D20 canonical bytes must exist in
   ArtifactStore before downstream reads; cross-node replay is idempotent, conflicts
   fail closed, and stale pre-repair state never replaces a repaired head.
10. Regression proof: focused, package, and full-runtime suites must pass, including
    the six RC13 triggers, RC14 dependency drift, and RC15 metadata-stat channel.
11. Security/architecture preservation: exact-host retrieval, SSRF/redirect checks,
    tool-closed subscription CLIs, model assignments, topology, terminals, and the
    no-billed-API/no-provider-SDK constraints remain intact.
12. Entry safety: no blocker may make a fresh graph-v9 N00→N90 cascade dishonest,
    unverifiable, or unable to run the real N70/N80 path.
