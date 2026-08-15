# RC19 independent QA criteria

Report only blocker findings, each naming the defeated criterion, reproducible
trigger, and consequence. A PASS is valid only after every required probe finishes;
reasoning that says review or probes remain underway is not a completed verdict.

1. Historical integrity: graph v8 retains SHA-256
   `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`;
   v9 retains separate graph/contract/schema/prompt/result/state lineage.
2. Package coherence/ownership: active bindings and digests recompute; the real
   plan validator and exact ownership verifier pass.
3. Complete freeze: D02 binds every curriculum-owned input used by M02/D08;
   missing declarations, escape, duplicates, oversize, and drift fail pre-entry.
4. External race-free staging: for engine-nested production N70 output, the work
   root resolves outside engine and output roots. D08 verifies bytes during staging,
   preserves declared layout, rejects conflicts, and executes only staged frozen
   entry/dependency/fixture bytes plus the exact candidate.
5. Closed sandbox: cwd/staged files are external; no network/model-auth/model-scratch
   rules; no undeclared engine byte or metadata visibility, including file and
   directory/ancestor metadata; no engine metadata exemptions.
6. Replay invariance: declared drift fails before execution; undeclared repository
   add/remove/rename/content/metadata changes cannot alter the same candidate and
   frozen-contract verdict.
7. Bounded authoring/recovery: M02 has no verifier/admission authority; invalid first
   versions stay immutable/non-head; repair is exact, bounded, lineage-preserving,
   and exact-head revalidated.
8. Physical replay: D08/D09/D12/D20 persist canonical bytes before reads, replay
   idempotently, fail conflicts closed, and preserve repaired heads.
9. Regression proof: package, focused, and full-runtime suites pass, including all
   RC13 and RC14–RC17 attacks.
10. Security/architecture: exact-host retrieval, SSRF/redirect checks, tool-closed
    subscription CLIs, model assignments, topology, terminals, and no-billed-API/
    no-provider-SDK constraints remain intact.
11. Entry safety: a fresh graph-v9 N00→N90 cascade through real N70/N80 is honest,
    verifiable, and executable.
