# Run 27 RC27 — final-byte contract validation candidate

RC27 contains the unchanged, fully tested RC26 production bytes. RC26's exec channel
failed before session creation; it issued no finding or verdict. RC25's provisional
app-server result failed independent integrity verification. Neither is approval.

Authority hashes:

- graph v8 `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`;
- graph v9 `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`;
- schema v6 `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`;
- contract v6 `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`;
- spec `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.

D02 validates the verifier entry and all declared Python dependencies using the
minimal module set actually required by the active Arduino verifier. It accepts only
receiver-exact `re.compile` and refuses the named invalid-source regression fixtures:
indirect eval, dynamic native import, process fork, invalid dependency code,
safe-module OS/process access, and safe-module dynamic-code access.

D08 stages verified frozen bytes outside engine/output and executes them read-only,
without network, process fork, model credentials, or engine metadata exemptions. Its
trusted Python guard covers all reproduced path calls on `os` and `posix`, including
chdir, utime, mkfifo, mknod, and lchmod. The four direct invariant tests require the
same candidate/contract hashes, result, return code, and output hash before and after
an undeclared engine path is renamed.

Candidate and fixture bytes are checked before and after execution and bound into the
receipt. External staging, declared-drift refusal, immutable repair lineage, physical
ArtifactStore replay, bounded M02 input, exact-host retrieval, subscription-only
model CLIs, model assignments, graph topology, and terminal semantics remain intact.

Final-byte proof: package/focused 989 passed; full runtime 1366 passed, 2 skipped,
419 subtests passed; Plan 26 N13 freshly PASSED with no stale receipts; plan valid;
ownership 75/75; Python compilation and whitespace checks clean.

V8 history and five N70 failures remain preserved; V9 uses isolated result/state
paths. No billed API, provider SDK, direct model HTTP, wildcard host, fabricated
receipt, validation shortcut, or historical overwrite is introduced.
