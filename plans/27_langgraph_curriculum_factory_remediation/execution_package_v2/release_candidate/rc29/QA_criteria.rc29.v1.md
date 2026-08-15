# RC29 independent software-correctness criteria

Use source inspection and the repository's committed tests. Do not create new payloads,
probe external systems, or perform security research. Report only blocker-severity
software defects with a criterion, reproducible committed test/input, consequence,
and observed evidence.

1. Recompute the five authority hashes and validate preserved V8/V9 lineage, plan,
   ownership, and complete-tree scan.
2. Run the committed active D01→D02 and invalid-source tests. The active Arduino case
   compiles and all invalid committed cases stop at D02.
3. Confirm from source that the allowed verifier imports match active documented needs
   and exclude package, process, network, native, and OS surfaces.
4. Run the committed fixture-schema, candidate-schema drift, staging, and immutability
   regressions; confirm D02/D08 use hash-checked frozen bytes.
5. Run the committed filesystem-normalization and mutable-parent-package isolation
   regressions and confirm identical inputs retain identical outcomes.
6. Confirm child argv contains `-I -S`, environment has no `PYTHONPATH`, the verifier
   profile grants no package root, and receipts identify the interpreter plus every
   file-backed child module with independent post-execution hashes.
7. Run committed repair, lineage, ArtifactStore, and D08/D09/D12/D20 replay and
   idempotence tests.
8. Confirm exact-host retrieval, redirects, subscription CLI routes, model assignments,
   topology, and terminal outcomes against the governing specification.
9. Confirm the claimed focused/full test censuses and current Plan 26 N13 receipt.
10. Confirm a fresh isolated V9 state can begin N00 and structurally supports the
    prescribed genuine N00→N90 cascade through N70 and N80.
