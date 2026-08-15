# Run 27 RC23 — closed verifier-language and filesystem boundary

## Decision requested

Review RC23 as the repaired successor to RC22 in the same QA session. RC22 correctly
failed on two executed blocker classes. RC23 closes both at their owning boundaries,
adds permanent exact-trigger regressions, refreshes Plan 26 N13, and reruns the full
suite. RC22's FAIL remains preserved and is not approval evidence.

## Immutable authority and lineage

- Graph v8 remains byte-identical at
  `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`,
  with its N00–N60 history and five failed N70 attempts intact.
- Active graph v9 remains
  `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`.
- Approval schema v6:
  `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`.
- Approval contract v6:
  `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`.
- Governing specification:
  `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.
- Fresh graph-v9 state/results remain isolated at `.run27_state_v9/` and
  `execution_package_v2/results/v9/`.

## RC22-QA-001 closure: closed Python-verifier language

D02 now enforces one policy over the entry point and every declared `.py`
dependency:

1. Imports are a closed allowlist containing the deterministic libraries needed by
   the active Arduino verifier, plus safe identifier roots backed by declared local
   Python dependencies. Process, native, dynamic-loader, networking, and interpreter
   modules cannot be introduced or shadowed as local dependencies.
2. Direct and indirect interpreter access is refused: dynamic builtins and reflective
   namespace functions are rejected on any name reference, not merely direct calls.
   Private/dunder attributes, import/reload/module registries, and exec/spawn/fork/
   system/popen/kill surfaces are rejected on attribute reference before aliasing.
3. `from` imports are checked at both module and imported-member boundaries.
4. The active Arduino verifier's ordinary `re.compile`, `Path`, `yaml`, and
   `jsonschema` use remains admitted by real D01→D02 execution.

The exact RC22 probes now pass: `getattr(builtins, 'eval')`, dynamic ctypes import,
`os.fork`, and indirect dependency eval all stop at D02 with `schema_contract`; the
dependency exploit cannot reach D08.

## RC22-QA-002 closure: complete reproduced path-operation guard

The trusted guard's one-path surface now also wraps `utime`, `mkfifo`, and `mknod`
on both `os` and `posix`. Exact host regressions run `chdir`, `utime`, and `mkfifo`
against an existing undeclared engine path and the same path after rename. Candidate
and contract digests, return codes, output digests, and FAIL verdicts remain identical
through normalized ENOENT behavior. D02 additionally refuses `os` imports, so these
operations are both statically blocked in admitted verifiers and normalized by the
trusted runtime guard if the transport boundary is tested directly.

## Carried-forward guarantees

External race-checked staging, read-only/no-network/no-fork sandboxing, candidate and
fixture pre/post hashes, complete receipt binding, immutable repair lineage, exact
ArtifactStore replay, bounded M02 authority, exact-host retrieval, SSRF/redirect
protection, subscription-only Claude/Codex CLIs, model assignments, topology, and
terminals are unchanged.

## Executed proof

- Execution-package suite: 176 passed.
- Focused runtime/repair plus package: 986 passed.
- Full runtime: 1363 passed, 2 skipped, 419 subtests passed.
- RC22 reviewer probes: active Arduino plus all four D02 bypass reproductions pass
  with the repaired production code.
- Host guard regressions: `chdir`, `utime`, and `mkfifo` all pass.
- Plan 26 N13 is freshly PASSED with no stale receipts after the final source bytes.
- Python compilation and whitespace validation pass.

No billed API, provider SDK, direct model HTTP call, fabricated receipt, validation
bypass, wildcard host, or historical overwrite is introduced.
