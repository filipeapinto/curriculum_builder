# Run 27 RC24 — closed verifier authority review bundle

## Decision requested

Independently decide whether these exact graph-v9 production bytes are safe to enter
for a genuine fresh N00→N90 cascade. RC22 round 1 formally failed with two blockers.
Round 2 reproduced two adjacent variants but ended `QA_ERROR/CODEX_EXIT_1` before a
formal verdict, so it is inconclusive and supplies only raw defect evidence. RC24
closes every formal and raw trigger and starts a fresh review chain.

## Preserved authority and history

- Graph v8 is immutable at
  `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`,
  including N00–N60 and five failed N70 attempts.
- Graph v9: `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`.
- Approval schema v6:
  `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`.
- Approval contract v6:
  `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`.
- Governing specification:
  `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.
- V9 results/state remain isolated under `execution_package_v2/results/v9/` and
  `.run27_state_v9/`; graph-v8 attempt 5 remains archived.

## Closed D02 Python authority

One validator is applied to the verifier entry and every declared `.py` dependency.
It uses a deterministic-library import allowlist plus declared, safe local import
roots. Forbidden dynamic-loader, native, process, network, interpreter, and OS roots
cannot be imported or shadowed. Reflective/dynamic builtin names are rejected on any
reference. Private interpreter attributes, module/import registries, forbidden module
re-exports, every fork/spawn name, exec/system/popen/kill surfaces, and dynamic
builtins exposed as attributes are rejected before execution.

`compile` is not broadly exempt: only the exact AST receiver `re.compile` is allowed.
This admits the active Arduino verifier while refusing re-exported or direct dynamic
compilation.

Mandatory reproduced closures:

- `getattr(builtins, 'eval')`;
- `importlib.import_module('ctypes')`;
- `os.fork()`;
- indirect eval in a declared Python dependency;
- `pathlib.os.posix_spawn(...)`;
- `enum.bltns.eval(...)`.

All six now return D02 `schema_contract`; active Arduino D01→D02 returns
`effective_run_compiled`.

## Closed D08 filesystem boundary

The external, contract/candidate-addressed staged snapshot remains read-only,
no-network, no-fork, without model auth/scratch or engine metadata exemptions. The
trusted guard covers builtins/io/open, access, stat/list/readlink, every reproduced
one/two-path operation, and all exec/spawn/system/popen calls on both `os` and `posix`.
The native one-path table now includes `utime`, `mkfifo`, `mknod`, and macOS `lchmod`.

Permanent direct-transport host tests require existing-to-renamed undeclared engine
paths to retain identical candidate/contract digests, return codes, output digests,
and FAIL verdicts for `chdir`, `utime`, `mkfifo`, and `lchmod`. D02 independently
blocks admitted verifier access through `os` or safe-module OS re-exports.

Candidate/fixture bytes are pre/post hashed. Receipts bind the candidate, recomputed
contract, trusted guard, entry, dependency closure, invocation, and fixture outcomes.

## Carried-forward guarantees

Race-checked external staging, declared-drift refusal, immutable first failures,
bounded exact repairs, physical ArtifactStore replay across D08/D09/D12/D20, bounded
M02 authority, exact-host retrieval, SSRF/redirect refusal, subscription-only
Claude/Codex CLIs, model assignments, topology, and terminals remain unchanged.

## Executed proof after final bytes

- Execution-package/focused combined: 989 passed.
- Full runtime: 1366 passed, 2 skipped, 419 subtests passed.
- Exact host path-oracle set: 4 passed.
- Exact D02 active/bypass set: 6 passed.
- Plan 26 N13: freshly PASSED, no stale receipts.
- Plan order valid; ownership 75/75; Python compilation and whitespace checks pass.

No billed API, provider SDK, direct model HTTP call, wildcard host, fabricated receipt,
validation bypass, or historical overwrite is introduced.
