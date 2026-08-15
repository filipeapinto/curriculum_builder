# RC27 independent correctness criteria

Complete all checks before verdict. Report only release-blocking correctness findings
with criterion, reproducible input, consequence, and observed evidence.

1. Recompute all five authority hashes; preserve V8 history and distinct V9 state and
   result lineage; validate the real plan, ownership contract, and complete-tree scan.
2. Run the active Arduino D01→D02 case and every named invalid-source regression. The
   active case must compile; every invalid case must stop before verifier execution.
3. Inspect entry/dependency validation for equivalent aliases and module exports. The
   minimal allowed module set must not grant code, native, process, network, or OS
   authority beyond the documented active verifier behavior.
4. Run the direct chdir, utime, mkfifo, and lchmod invariance cases plus candidate
   immutability, declared-drift, external-staging, and staged-conflict tests.
5. Confirm D08 executes only frozen staged bytes under the stated read-only and
   isolation properties, and its receipt identifies every evaluated byte source.
6. Confirm unchanged repository files and metadata cannot alter a result for the same
   candidate and frozen contract; changed declared bytes must stop execution.
7. Run repair/replay tests for immutable initial failures, bounded repairs, exact
   lineage, ArtifactStore bytes, and D08/D09/D12/D20 idempotence.
8. Confirm exact-host retrieval and redirect rules, subscription CLI routes, model
   assignments, graph topology, and terminal outcomes match the governing spec.
9. Confirm the package and full runtime suites and the current Plan 26 N13 receipt.
10. Confirm a fresh isolated graph-v9 state can begin N00 and supports the prescribed
    genuine N00→N90 execution through the N70 and N80 product proofs.
