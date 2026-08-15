# RC24 independent QA criteria

Complete all probes before verdict. Report only blockers with exact criterion,
trigger, consequence, and executed or directly inspectable evidence.

1. Recompute graph/spec/schema/contract hashes; preserve graph-v8 history and distinct
   graph-v9 result/state lineage; pass real plan, ownership, and complete-tree scans.
2. D02 binds entry plus every Python dependency and rejects direct, indirect, aliased,
   re-exported, reflected, or dynamically imported code/native/process/OS/network
   surfaces before entry, while admitting only the active `re.compile` use intended.
3. Reproduce all six named D02 attacks from RC22 rounds 1/2. Probe adjacent safe-module
   re-exports and aliases; none may cross D02 or execute during D08.
4. D08 stages race-checked bytes outside engine/output and runs only the staged closed
   snapshot under read-only, no-network, no-fork, no-model-auth authority.
5. All ordinary Python path operations are either unreachable after D02 or normalized
   by the trusted guard. Reproduce chdir, utime, mkfifo, lchmod, candidate overwrite,
   and existing-to-renamed path invariance with identical bound bytes/verdict evidence.
6. Declared drift and staged conflicts fail; undeclared repository byte/metadata/name
   changes cannot alter a same-candidate/frozen-contract verdict.
7. Candidate/fixture pre/post bytes and receipt bindings exactly identify execution.
8. Immutable repair lineage, bounded M02 authority, physical ArtifactStore replay,
   and D08/D09/D12/D20 exact-head idempotence remain correct.
9. Package/focused/full suites pass; exact-host/SSRF/redirect, subscription-only CLIs,
   model assignments, topology, terminals, and no-billed-API/provider-SDK remain intact.
10. A real fresh graph-v9 N00→N90 cascade through N70/N80 is honest and executable.
