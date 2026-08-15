# RC20 independent QA criteria

Complete every required probe before verdict. Report only blocker findings, each
naming the defeated criterion, reproducible trigger, and consequence.

1. Historical integrity: graph v8 retains SHA-256
   `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`;
   v9 uses separate graph/contract/schema/prompt/result/state lineage.
2. Package coherence/ownership: bindings and digests recompute; real plan and exact
   ownership verification pass.
3. Complete freeze and code boundary: D02 binds every M02/D08 curriculum input and
   rejects missing declarations, escape, duplicates, oversize, drift, absolute-path
   literals, native/process escape modules, dynamic code, and process launching.
4. External race-free staging: production engine-nested N70 output maps to a work
   root outside engine/output. D08 verifies bytes during staging, preserves declared
   layout, rejects conflicts, and runs only staged frozen bytes and exact candidate.
5. Candidate/fixture immutability: the process has no workspace write authority;
   input hashes are checked before and after each run; mutation or restore attempts
   cannot yield a receipt for bytes other than those evaluated.
6. Existence-normalized sandbox: no network/model-auth/model-scratch/process-fork;
   no undeclared engine content/metadata visibility; all supported Python filesystem
   APIs return the same absent-path result for an engine path regardless of actual
   existence; process replacement/spawn bypasses are blocked.
7. Replay invariance: declared drift fails pre-execution, and undeclared repository
   add/remove/rename/content/metadata changes cannot alter the same candidate/frozen-
   contract verdict.
8. Bounded authoring/recovery: M02 has no verifier/admission authority; invalid first
   versions remain immutable/non-head; repairs are exact, bounded, lineage-safe, and
   exact-head revalidated.
9. Physical replay: D08/D09/D12/D20 persist canonical bytes before reads, replay
   idempotently, fail conflicts closed, and preserve repaired heads.
10. Regression proof: package/focused/full suites pass, including RC13 and all
    RC14–RC19 attack reproductions.
11. Security/architecture: exact-host retrieval, SSRF/redirect checks, tool-closed
    subscription CLIs, model assignments, topology, terminals, and no-billed-API/
    no-provider-SDK constraints remain intact.
12. Entry safety: a real fresh graph-v9 N00→N90 cascade through N70/N80 is honest,
    verifiable, and executable.
