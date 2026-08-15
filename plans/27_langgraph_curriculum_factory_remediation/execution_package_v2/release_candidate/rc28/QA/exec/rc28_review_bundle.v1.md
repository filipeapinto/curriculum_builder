# Run 27 RC28 — closed verifier-runtime release candidate

RC28 is a fresh formal candidate because RC27 round 1 correctly failed and its
post-repair continuation ended `QA_ERROR/CODEX_MALFORMED_VERDICT` without a verdict.
Both records remain preserved. RC28 carries the repaired final bytes and asks a new
independent session to evaluate them from scratch.

Authority hashes:

- graph v8 `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`;
- graph v9 `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`;
- schema v6 `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`;
- contract v6 `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`;
- governing specification `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.

## D02 closes the verifier language and validates fixtures

The active verifier imports only `argparse`, `json`, `pathlib`, and `re` from the
standard library. Curriculum sidecars retain their declared historical `.yaml`
paths but now contain strict JSON bytes. PyYAML and jsonschema no longer enter the
verifier child.

D02 accepts only `__future__`, those four roots, and individually frozen local Python
dependencies. It validates the entry and every Python dependency, and it now parses,
re-hashes, and validates every reject/accept fixture against the frozen domain schema
before execution. Exact regressions reject both reported PyYAML unsafe-load forms,
indirect eval/import/fork, safe-module process/dynamic re-exports, invalid dependency
code, and schema-invalid frozen fixtures.

D08 independently reads and hashes the same frozen schema bytes before validating the
exact candidate. Thus the engine validates all fixtures at D02 and the candidate at
D08 before the curriculum verifier script is entered; the script owns only its six
curriculum-specific electrical rules.

## D08 has no mutable package import surface

D08 stages the hashed schema, entry, dependencies, and fixtures into a content-
addressed work root outside engine/output. It no longer enumerates parent `sys.path`,
grants package directories, or exports `PYTHONPATH`. The child runs under the resolved,
hashed interpreter with `-I -S`, a read-only/no-network/no-fork verifier profile, and
the trusted filesystem/process guard.

The guard emits exactly one machine runtime-manifest marker in `finally`. The parent
requires that marker, parses every file-backed module record, rejects any package or
unstaged-engine path, independently re-hashes every module after execution, and binds
the normalized list and digest into each fixture/candidate result. The receipt also
binds interpreter path/SHA/version/flags, schema, entry, declared dependencies,
fixtures, candidate, invocation, and guard. Built-in/frozen modules have no separate
file bytes and are bound by the interpreter digest.

The reported mutable-site-package attack is permanent: an injected parent
`site-packages/yaml.py` is changed from allow to deny between identical contract and
candidate runs; both remain identical FAIL/return-code/output/runtime-digest results,
and the injected path never appears in the runtime manifest.

## Final-byte identities and proof

- `transport.py` `1512dba21864af7884e60dd5150aabeb1bddffeb9627f56a751631c01e2e1c9f`;
- `inputs.py` `23b932bfbf66c3fd2d0f35fa369fe45707a1a164484dc7e56a1835c34f533b7a`;
- active verifier `499beb54e8dcc66773c7efc68b994760da8722b266c24e62bb6f1102961bd96b`;
- calibration sidecar `a24fe5e4146bec2ed5bd12dae3f3c4278423c9d8c2b0277e8376fc6cb2d4a34d`;
- circuit sidecar `feb79e77d459dc7258a2d270c5e0365a3c18e5ddf4249722c0b10ad49cded4a0`;
- D02 regression file `602070adeba0921f6cf5b5ac313f10fe9328c8f78500db1e7a4f7889ed9da0b4`;
- transport regression file `9641a1cc94a111b2c5cc0fd6f4293458af6d1fd78541bc849080a4c78d5b500e`.

Executed after the final source and fixture bytes:

- exact repaired attack set: 12 passed;
- transport/D02/verifier focused suites: 419 passed;
- execution-package plus repair/D02 focused suites: 569 passed;
- complete runtime suite: 1370 passed, 2 skipped, 419 subtests passed;
- Plan 26 N13: freshly `PASSED`, no stale receipts, receipt SHA-256
  `3a739b6712498c1cff382e65d90b5d1eb125f4a57c97375defe294b032c6414c`;
- plan valid; ownership 75/75; complete-tree scan 67/zero violations;
  compilation and whitespace checks clean.

All earlier external-staging, candidate immutability, repair lineage, ArtifactStore
replay, exact-host retrieval, subscription-only CLI, topology, terminal, and isolated
V9-history guarantees remain. No billed API, provider SDK, direct model HTTP, wildcard
host, fabricated receipt, shortcut, or historical overwrite is introduced.
