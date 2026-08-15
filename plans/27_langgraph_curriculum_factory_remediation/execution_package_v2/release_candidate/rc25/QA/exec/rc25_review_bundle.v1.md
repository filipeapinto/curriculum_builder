# Run 27 RC25 — unchanged RC24 bytes, fresh QA transport

## Decision requested

Review the exact production bytes described by RC24. RC24's exec transport ended
`QA_ERROR/CODEX_EXIT_1` before establishing a review session and made no finding or
verdict. RC25 changes no production source; it starts a fresh independent chain via
the sanctioned app-server transport. RC22's formal FAIL and raw round-2 probes remain
mandatory defect history, never approval.

## Authority

- Graph v8: `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`.
- Graph v9: `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`.
- Approval schema v6:
  `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`.
- Approval contract v6:
  `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`.
- Governing spec:
  `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.
- V8 history and five N70 failures remain intact. V9 state/results remain isolated.

## Exact mandatory closures

D02 applies a closed import/name/attribute policy to the verifier entry and every
declared Python dependency. It admits only exact `re.compile` while refusing:

- `getattr(builtins, 'eval')`;
- dynamic ctypes import;
- `os.fork`;
- indirect dependency eval;
- `pathlib.os.posix_spawn`;
- `enum.bltns.eval`.

Forbidden module re-exports, dynamic/reflection names, private interpreter surfaces,
and every fork/spawn/exec/system/popen/kill surface are rejected before entry.

D08 stages only race-checked frozen bytes outside engine/output and runs read-only,
no-network, no-fork, with no model credentials or engine metadata exemptions. Its
trusted `os`/`posix` guard includes the complete reproduced native path set, including
`utime`, `mkfifo`, `mknod`, and `lchmod`. Direct host probes for chdir, utime, mkfifo,
and lchmod require identical candidate/contract digests, return codes, output digests,
and FAIL verdicts across existing-to-renamed undeclared paths.

Candidate/fixture pre/post hashing, complete receipts, external staging, declared
drift refusal, exact repair/replay, bounded M02 authority, ArtifactStore physical
heads, exact-host retrieval, subscription-only model CLIs, model assignments,
topology, and terminals are unchanged.

## Executed proof

- Package/focused: 989 passed.
- Full runtime: 1366 passed, 2 skipped, 419 subtests passed.
- Exact D02 set: 6 passed; direct host path-oracle set: 4 passed.
- Plan 26 N13: freshly PASSED, no stale receipts.
- Plan valid; ownership 75/75; compile and whitespace checks pass.

No billed API, provider SDK, direct model HTTP call, wildcard host, fabricated receipt,
validation bypass, or historical overwrite is introduced.
