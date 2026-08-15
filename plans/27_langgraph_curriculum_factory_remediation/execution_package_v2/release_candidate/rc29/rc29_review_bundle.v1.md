# Run 27 RC29 — deterministic verifier isolation candidate

RC29 contains the same source bytes that passed RC28's local validation. RC28's
apparent QA pass was invalidated by `verify`: the Codex turn was stopped by a policy
classifier during defensive regression execution and its explicitly interim response
was incorrectly recorded as `PASS`. A fresh-session postmortem classified that as
`INTEGRITY_BREACH`, not an artifact deficiency. RC27/RC28 records remain preserved.

Authority hashes remain:

- graph v8 `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`;
- graph v9 `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`;
- schema v6 `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`;
- contract v6 `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`;
- specification `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.

## Correctness boundary

D02 defines a closed, deterministic Python subset for the curriculum verifier. The
active script uses only `argparse`, `json`, `pathlib`, and `re`; the historical YAML-
named sidecars contain strict JSON bytes. D02 parses and validates the entry and every
declared Python dependency, then re-hashes and schema-validates every frozen accept and
reject fixture. The committed invalid-source regression cases all fail at D02.

D08 reads and hashes the same frozen schema bytes before validating the exact candidate.
It stages schema, verifier, declared dependencies, and fixtures in an external content-
addressed snapshot. The child has no parent package search path: D08 never enumerates
`sys.path`, never grants package directories, never sets `PYTHONPATH`, and invokes the
resolved hashed interpreter with `-I -S`.

The trusted guard always emits one runtime manifest. The parent requires a unique valid
marker and independently re-hashes each file-backed child module. Package paths,
unstaged engine paths, missing/changed files, incomplete records, or malformed markers
fail closed. Each result binds the normalized module list/digest, and the top receipt
binds interpreter path/SHA/version/flags, schema, entry, dependencies, fixtures,
candidate, invocation, and guard. Built-in/frozen modules are part of the interpreter
binary identity.

The committed isolation regression injects a mutable package directory into the parent
test process, changes only that module between identical contract/candidate calls, and
requires identical verdict, return code, output hash, and runtime digest with no
injected path observed. Existing committed tests also cover filesystem normalization,
candidate immutability, declared drift, external staging, and staged conflicts.

Final source identities:

- transport `1512dba21864af7884e60dd5150aabeb1bddffeb9627f56a751631c01e2e1c9f`;
- D02 inputs `23b932bfbf66c3fd2d0f35fa369fe45707a1a164484dc7e56a1835c34f533b7a`;
- active verifier `499beb54e8dcc66773c7efc68b994760da8722b266c24e62bb6f1102961bd96b`;
- calibration `a24fe5e4146bec2ed5bd12dae3f3c4278423c9d8c2b0277e8376fc6cb2d4a34d`;
- circuit library `feb79e77d459dc7258a2d270c5e0365a3c18e5ddf4249722c0b10ad49cded4a0`;
- D02 tests `602070adeba0921f6cf5b5ac313f10fe9328c8f78500db1e7a4f7889ed9da0b4`;
- transport tests `9641a1cc94a111b2c5cc0fd6f4293458af6d1fd78541bc849080a4c78d5b500e`.

Final executed proof:

- exact committed regression set: 12 passed;
- transport/D02/verifier suites: 419 passed;
- package plus repair/D02 suites: 569 passed;
- complete runtime: 1370 passed, 2 skipped, 419 subtests passed;
- Plan 26 N13: current `PASSED`, no stale receipts, SHA-256
  `3a739b6712498c1cff382e65d90b5d1eb125f4a57c97375defe294b032c6414c`;
- plan valid, ownership 75/75, complete-tree scan 67/zero violations, clean
  compilation and whitespace.

V8 history, V9 isolation, repair/replay, exact-host retrieval, subscription-only CLIs,
model assignments, topology, and terminal semantics remain unchanged. No billed API,
provider SDK, direct model HTTP, wildcard host, fabricated receipt, validation shortcut,
or historical overwrite is introduced.
