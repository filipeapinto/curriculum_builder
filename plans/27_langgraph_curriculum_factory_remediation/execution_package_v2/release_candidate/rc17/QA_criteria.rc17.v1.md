# RC17 independent QA criteria

Report only blocker findings: each finding must name the criterion it defeats,
a reproducible trigger, and the consequence. Style and optional hardening are
observations.

1. Historical integrity: graph v8 retains SHA-256
   `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`;
   v9 retains distinct graph/contract/schema/prompt/result/state lineage.
2. Package coherence: every v9 package binding and digest recomputes, the real
   plan validator passes, and ownership remains exact and non-ambiguous.
3. Complete freeze: D02 binds every curriculum-owned domain input used by M02 or
   D08. Missing declarations, escape, duplicates, oversize, and byte drift fail
   before entry; the complete digest identifies the effective run.
4. Race-free staging: D08 must verify source bytes while copying them into a
   contract-and-candidate-addressed snapshot, preserve the required relative
   layout, reject staged conflicts, and execute only staged entry/dependency/
   fixture bytes plus the exact candidate.
5. Closed sandbox: the verifier runs outside the engine working directory under
   no-network, no-model-auth, no-model-scratch rules. It has neither byte nor
   metadata access to undeclared curriculum/engine files, including engine-root
   and ancestor-directory metadata; no engine metadata exemptions are permitted.
6. Replay invariance: any add/remove/rename/content change to undeclared repository
   paths and any post-D02 declared drift cannot change the same candidate/frozen
   contract verdict. Declared drift fails before execution; undeclared repository
   state is unobservable.
7. Bounded authoring: D07/M02 sees only admitted claims and verified staged inputs,
   with no admission or verifier authority.
8. Repair/replay: invalid first candidates stay immutable/non-head; repairs target
   exact bytes, remain bounded, preserve lineage, and revalidate exact repaired
   heads. D08/D09/D12/D20 physical admission and cross-node replay remain correct.
9. Regression proof: focused, package, and full-runtime suites pass, including six
   RC13 triggers and the RC14–RC16 byte/direct-metadata/ancestor-metadata attacks.
10. Security/architecture preservation: exact-host retrieval, SSRF/redirect checks,
    tool-closed subscription CLIs, model assignments, topology, terminals, and
    no-billed-API/no-provider-SDK constraints remain intact.
11. Entry safety: no blocker may make a fresh graph-v9 N00→N90 cascade dishonest,
    unverifiable, or unable to execute the real N70/N80 path.
