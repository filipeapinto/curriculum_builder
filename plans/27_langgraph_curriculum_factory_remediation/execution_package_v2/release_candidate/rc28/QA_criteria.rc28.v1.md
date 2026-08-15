# RC28 independent correctness criteria

Complete every check before verdict. Report only release-blocking correctness findings
with a defeated criterion, reproducible trigger, consequence, and observed evidence.

1. Recompute all five authority hashes; preserve V8 history and distinct V9 state and
   result lineage; validate the plan, ownership contract, and complete-tree scan.
2. Run the active Arduino D01→D02 case and every named invalid-source regression. The
   active case must compile; every invalid case must stop before verifier execution.
3. Inspect equivalent aliases and module exports. The closed allowed module set must
   not grant code, native, process, network, OS, or mutable package authority.
4. Confirm every verifier fixture is re-hashed and schema-valid at D02, the candidate
   is validated from the same frozen schema bytes at D08, and declared-byte drift or
   staging races fail closed.
5. Run chdir/utime/mkfifo/lchmod invariance, candidate immutability, declared drift,
   external staging, staged conflict, and mutable parent-site-package tests.
6. Confirm the child uses `-I -S` without `PYTHONPATH` or package-directory grants;
   its receipt must bind the interpreter and every file-backed runtime module and
   refuse package, unstaged-engine, missing, changed, or malformed module records.
7. Confirm unchanged repository bytes/metadata cannot change the same candidate and
   frozen contract result, while changed declared or evaluated bytes stop execution.
8. Run immutable-failure, bounded-repair, exact-lineage, ArtifactStore, and
   D08/D09/D12/D20 replay/idempotence regressions.
9. Confirm exact-host retrieval/redirect rules, subscription CLI routes, model
   assignments, topology, and terminal outcomes match the governing specification.
10. Confirm package/focused and full-runtime suites plus the current Plan 26 N13
    receipt; then prove fresh isolated graph-v9 state supports genuine N00→N90 through
    the N70 and N80 product gates.
