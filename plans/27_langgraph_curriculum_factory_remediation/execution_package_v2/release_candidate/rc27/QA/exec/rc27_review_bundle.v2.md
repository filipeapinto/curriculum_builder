# Run 27 RC27 — D02/D08 closed-runtime repair

This is the second artifact in the existing RC27 QA session. Round 1 correctly
returned `FAIL` with two blockers. Those findings remain preserved in
`QA/rounds/round-01.response.json`; this artifact does not supersede or erase them.

Authority hashes remain unchanged:

- graph v8 `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`;
- graph v9 `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`;
- schema v6 `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`;
- contract v6 `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`;
- governing specification `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.

## RC27-B01 repair: no package parser crosses D02

The active Arduino verifier no longer imports PyYAML or jsonschema. Its two
curriculum-owned `.yaml` sidecars now contain strict JSON bytes, which preserves
their data model while allowing the isolated verifier to parse them with the standard
library. Exact JSON Schema admission moved to the trusted D08 transport and uses the
schema reference already frozen in the D02 contract.

D02's closed verifier import set is now only `__future__`, `argparse`, `json`,
`pathlib`, and `re`, plus individually frozen local Python dependencies. Both reported
forms (`import yaml; yaml.unsafe_load(...)` and `from yaml import unsafe_load as ...`)
are permanent invalid-source regressions and stop at D02.

## RC27-B02 repair: isolated interpreter and evaluated-byte receipt

D08 no longer enumerates parent `sys.path`, grants `site-packages` read access, or
sets `PYTHONPATH`. Every verifier child is invoked by the hashed resolved interpreter
with `-I -S`. The receipt binds the interpreter path, SHA-256, version and flags; the
trusted guard emits a single machine marker enumerating every file-backed module
remaining in `sys.modules`, and the parent independently re-hashes every path before
accepting the result. Any `site-packages`/`dist-packages` module, unstaged engine
module, missing module, changed module, incomplete record, invalid marker, or duplicate
marker fails closed as `VerifierFault`.

The schema, staged entry, every declared dependency, fixtures, candidate, invocation,
guard, interpreter, and runtime-module manifest are therefore all identified by the
receipt. Built-in/frozen modules have no separate file bytes and are bound by the
interpreter digest. A permanent adversarial test injects a mutable parent
`site-packages/yaml.py`, changes only that file between identical candidate/contract
runs, and requires identical FAIL verdicts, return codes, output hashes, and runtime
digests with no injected path present.

Relevant final-byte identities:

- `transport.py` `4e33658f9d1feb19feae7fd987e0b41e30f8116b333cc9d540c51683f5c06d40`;
- `inputs.py` `6104ad6c6177623385820453c74bf52aa859bee618e19f63c22bda95e3b598ff`;
- `verify_domain.py` `499beb54e8dcc66773c7efc68b994760da8722b266c24e62bb6f1102961bd96b`;
- calibration sidecar `a24fe5e4146bec2ed5bd12dae3f3c4278423c9d8c2b0277e8376fc6cb2d4a34d`;
- circuit sidecar `feb79e77d459dc7258a2d270c5e0365a3c18e5ddf4249722c0b10ad49cded4a0`.

## Final-byte proof

- New exact attack tests: 11 passed, including both PyYAML forms and mutable injected
  parent-site-package invariance.
- Transport/D02/verifier focused suites: 418 passed.
- Execution-package plus repair/D02 focused suites: 568 passed.
- Complete runtime suite: 1369 passed, 2 skipped, 419 subtests passed.
- Plan 26 N13 was freshly reminted after all source edits: `PASSED`, no stale receipts;
  receipt file SHA-256
  `7376972f59eb55e63c19e329f16bbcc6f062edf966ad7a5208c93d2352cc8df7`.
- Plan order valid; ownership 75/75; complete-tree scan 67 files/zero violations;
  Python compilation and whitespace checks clean.

External staging, immutable repair lineage, physical ArtifactStore replay, exact-host
retrieval, subscription-only model CLIs, model assignments, graph topology, terminal
semantics, preserved V8 failures, and isolated V9 state/result paths remain intact.
No billed API, provider SDK, direct model HTTP call, wildcard host, fabricated receipt,
validation shortcut, or historical overwrite is introduced.
