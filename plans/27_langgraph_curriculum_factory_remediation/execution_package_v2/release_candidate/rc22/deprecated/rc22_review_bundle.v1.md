# Run 27 RC22 — closed Python-verifier boundary review bundle

## Decision requested

Independently determine whether the graph-v9 implementation is safe to enter and
capable of a genuine fresh N00→N90 cascade. RC21 found three blockers by executing
the active curriculum and adversarial probes. RC22 fixes all three production paths
and adds permanent regressions for their exact triggers. No RC21 failure evidence is
treated as approval evidence.

## Preserved lineage and authority

- Approved graph v8 remains immutable at
  `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`.
- Graph-v8 N00–N60 history and all five failed N70 attempts remain preserved; live
  attempt 5 is archived at
  `outputs/run27/archive/live_unit_v8_attempt_05_domain_pre_admission_repair`.
- Active graph v9: `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`.
- Approval schema v6:
  `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`.
- Approval contract v6:
  `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`.
- Governing specification:
  `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.
- Fresh graph-v9 state/results are isolated at `.run27_state_v9/` and
  `execution_package_v2/results/v9/`; the historical default is unchanged.

## RC21 blocker closure

1. `RC21-QA-001`: D02's AST policy now distinguishes direct dynamic-code calls
   (`compile`, `eval`, `exec`, `__import__`) from ordinary attribute methods.
   `re.compile(...)` is permitted. A permanent regression runs real D01→D02 with
   the active Arduino v5 curriculum and requires `effective_run_compiled`.
2. `RC21-QA-002`: the same UTF-8/AST policy is applied to every declared `.py`
   verifier dependency after D01-frozen path and digest validation. A malicious
   `helper.py` containing `subprocess`/`eval` is rejected by D02 before D08.
3. `RC21-QA-003`: the trusted runtime guard now covers `os` and `posix` one-path
   and two-path metadata/mutation operations, including `chdir`, and blocks all
   exec/spawn/system/popen surfaces. An existing undeclared engine directory and
   the same path after rename both produce the same candidate/frozen-contract FAIL
   verdict through normalized ENOENT behavior.

## Closed verifier and replay boundary

- The curriculum schema requires a bounded, unique dependency closure. D02 resolves
  all declared verifier bytes inside the curriculum, matches D01-frozen hashes, and
  binds them into the effective-run/domain-contract identity.
- D08 re-hashes every source and verifies staged bytes. It preserves declared layout
  in a contract/candidate-addressed system-temp directory that refuses containment
  beneath the engine or output root, including engine-nested N70 output.
- Execution is limited to the staged Python verifier entry, candidate, dependencies,
  and fixtures. The sandbox is read-only, no-network, no-fork, without model auth or
  scratch permissions, and denies engine bytes and metadata without exemptions.
- Candidate and fixture bytes are hashed before and after execution. The receipt
  binds candidate, contract, trusted guard, entry, dependencies, invocation, and
  complete fixture outcomes.
- D08/D09/D12/D20 persist and replay exact ArtifactStore heads; immutable first
  failures, repair lineage, bounded M02 authority, and exact-head revalidation remain
  covered by the full repair/replay suite.

## Executed pre-review proof

- Execution-package suite: 176 passed.
- Focused runtime/repair suite: 804 passed.
- Combined exact package/focused suite: 980 passed.
- Full runtime: 1357 passed, 2 skipped, 419 subtests passed.
- Plan 26 N13 was refreshed after the final transport/input changes and reports
  PASSED with no stale receipts.
- Python compilation and whitespace validation pass; active hashes above were
  recomputed from disk.

Exact-host retrieval, SSRF/redirect protections, eight model/effort assignments,
subscription-only Claude/Codex CLIs, topology, terminals, and the prohibition on
billed APIs/provider SDKs remain unchanged.
