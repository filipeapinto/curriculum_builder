# Run 27 RC26 — minimal active-verifier authority

## Decision requested

Review RC26 as a fresh immutable candidate. RC25's app-server reported PASS after a
policy flag/empty final message; independent verification rejected it as
`INTEGRITY_BREACH`, so it is not approval. RC26 further narrows D02's verifier import
surface and reruns every gate before opening a new exec-transport QA chain.

## Immutable bindings

- graph v8 `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`;
- graph v9 `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`;
- schema v6 `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`;
- contract v6 `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`;
- spec `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.

V8 history/failures remain intact; V9 uses isolated result/state namespaces.

## Closed verifier boundary

D02 now permits only the exact import roots used by the active verifier:
`__future__`, `argparse`, `json`, `jsonschema`, `pathlib`, `re`, `sys`, and `yaml`,
plus safe nonreserved local roots backed by declared Python dependencies. The same
AST policy validates entry and dependencies. It rejects dynamic/reflection names,
private interpreter attributes, forbidden module roots and re-exports, and every
fork/spawn/exec/system/popen/kill surface. Only receiver-exact `re.compile` is exempt.

Mandatory probes rejected at D02: indirect builtins eval, dynamic ctypes import,
`os.fork`, dependency-indirect-eval, `pathlib.os.posix_spawn`, and
`enum.bltns.eval`. Real Arduino D01→D02 remains admitted.

D08 still stages race-checked frozen bytes outside engine/output and runs read-only,
no-network, no-fork, no-model-auth, with no engine metadata exemption. The trusted
guard covers the complete reproduced native path surface on `os` and `posix`,
including `utime`, `mkfifo`, `mknod`, and `lchmod`. Direct host probes for chdir,
utime, mkfifo, and lchmod prove identical candidate/contract hashes, return codes,
output hashes, and FAIL verdicts across existing-to-renamed undeclared paths.

Candidate/fixture pre/post hashes and complete receipts remain bound. External
staging, declared drift, immutable repair lineage, physical ArtifactStore replay,
bounded M02, exact-host retrieval, subscription-only CLIs, model assignments,
topology, and terminals are unchanged.

## Final-byte validation

- Package/focused: 989 passed.
- Full runtime: 1366 passed, 2 skipped, 419 subtests passed.
- Plan 26 N13 freshly PASSED with no stale receipts.
- Plan valid; ownership 75/75; compilation/whitespace clean.

No billed API, provider SDK, direct model HTTP, wildcard host, fabricated receipt,
bypass, or historical overwrite is introduced.
