# RC18 independent QA criteria

Report only blocker findings, each with the defeated criterion, reproducible trigger,
and consequence. Style and optional hardening are observations.

1. Historical integrity: graph v8 retains SHA-256
   `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`;
   v9 uses separate graph/contract/schema/prompt/result/state lineage.
2. Package coherence and ownership: all active bindings/digests recompute; the real
   plan validator and exact ownership checks pass.
3. Complete freeze: D02 binds every curriculum-owned domain input used by M02/D08;
   missing declarations, escape, duplicates, oversize, and drift fail before entry.
4. External, race-free staging: for the prescribed engine-nested N70 output, the
   verifier work root must resolve outside engine and output roots. D08 must verify
   source bytes while staging into contract/candidate-addressed storage, preserve
   declared relative layout, reject conflicts, and execute only staged frozen bytes.
5. Closed sandbox: cwd and staged files are outside the engine. The verifier has no
   network, model auth, or model scratch rule; no byte or metadata visibility into
   undeclared engine paths, including files and directory/ancestor metadata; and no
   engine metadata exemption.
6. Replay invariance: declared drift fails before execution, while additions,
   removals, renames, and byte/metadata changes to undeclared repository paths cannot
   change the same candidate/frozen-contract verdict.
7. Bounded authoring and recovery: M02 has no admission/verifier authority; invalid
   first versions stay immutable/non-head; repairs are exact, bounded, lineage-safe,
   and revalidate exact repaired heads.
8. Physical replay: D08/D09/D12/D20 persist canonical bytes before reads, replay
   idempotently across nodes, fail conflicts closed, and preserve repaired heads.
9. Regression proof: focused, package, and full-runtime suites pass, including all
   RC13 triggers and RC14–RC17 byte/metadata/output-location attacks.
10. Security/architecture: exact-host retrieval, SSRF/redirect checks, tool-closed
    subscription CLIs, model assignments, topology, terminals, and no-billed-API/
    no-provider-SDK constraints remain intact.
11. Entry safety: no blocker prevents an honest, verifiable fresh graph-v9 N00→N90
    cascade through the real N70/N80 path.
