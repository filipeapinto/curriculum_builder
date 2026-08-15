# Run 27 RC20 — immutable guarded-verifier review bundle

## Decision requested

Independently determine whether graph v9 is safe to enter and capable of a fresh
N00→N90 cascade. RC19 found that an otherwise external staged verifier could still
overwrite its candidate and distinguish denied-existing from absent engine paths.
RC20 makes the staged workspace read-only during execution and runs the verifier
through a trusted guard that normalizes every ordinary engine filesystem operation
to `FileNotFoundError`, independent of host existence. D02 additionally rejects
absolute filesystem literals and process/native escape surfaces. The specification,
graph, model assignments, retrieval policy, and subscription-only architecture are
unchanged.

## Preserved lineage

- Graph v8 remains byte-identical at
  `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`.
- Its N00–N60 evidence and five failed N70 attempts remain historical; attempt 5
  stays archived at `outputs/run27/archive/live_unit_v8_attempt_05_domain_pre_admission_repair`.
- RC10–RC19 and all QA/postmortem records remain intact. None of their failed or
  integrity-breached verdicts is approval evidence.

## Complete verifier closure

1. The curriculum schema requires a bounded unique dependency list; the Arduino
   manifest declares every schema/calibration/library file its verifier reads.
2. D02 resolves all verifier inputs inside the curriculum, matches D01-frozen hashes,
   and binds the closure into effective-run identity. It parses the Python entry and
   rejects absolute path literals, native/process modules, dynamic code execution,
   and process-launch calls before entry.
3. D08 re-hashes all source inputs and hashes the bytes again during staging. It
   stages beneath an output-namespaced system-temp root proven outside engine/output,
   preserves declared relative layout, and rejects conflicting snapshot bytes.
4. Candidate, guard, entry, dependencies, and fixtures are all written before the
   sandbox starts. The verifier profile then grants the workspace read-only access,
   denies process forking, denies network, omits model auth/scratch rules, grants no
   engine content reads, and denies engine metadata without exemptions.
5. The trusted guard wraps `open`, `io.open`, `os.open`, stat/lstat, listdir/scandir,
   readlink, access, and the underlying `posix` functions. Any engine-root path gets
   the same `ENOENT` whether it exists or not. It blocks process exec/spawn/system/
   popen surfaces and runs the staged entry with only the original verifier args.
6. D08 hashes each candidate/fixture immediately before execution and again after;
   any byte change fails closed. The receipt binds candidate, recomputed contract,
   guard, entry, dependency set, invocation, and fixture outcomes.

Permanent regressions reproduce both RC19 attacks: a verifier attempting to rewrite
`candidate.json` fails and the original bytes remain; a verifier branching on
PermissionError versus FileNotFoundError returns the identical verdict before and
after an undeclared engine-file rename. D02 separately rejects the embedded absolute
path. Prior RC14–RC17 byte, metadata, ancestor, and nested-output attacks remain
covered, and the active Arduino verifier/fixtures pass through the guarded runner.

## Carried-forward guarantees

- M02 has no admission/verifier authority and sees only admitted/verified inputs.
- Invalid first domain/content/visual versions stay immutable/non-head; exact bounded
  repairs preserve lineage and revalidate the exact repaired head.
- D08/D09/D12/D20 canonical persistence and cross-node replay remain idempotent,
  conflict-closed, and resistant to stale repair overwrite.

## Bindings and executed proof

- Graph v9: `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`.
- Approval schema v6: `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`.
- Approval contract v6: `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`.
- Governing specification: `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.
- Fresh results/state: `execution_package_v2/results/v9/`, `.run27_state_v9/`.
- Package: 176 passed; focused runtime/repair: 802 passed; combined: 978 passed.
- Full runtime after final N13 refresh: 1355 passed, 2 skipped, 419 subtests passed.
- Plan 26 has no stale receipts; plan/ownership/compile/whitespace checks pass.

No billed API key, provider SDK, direct model HTTP call, wildcard retrieval host,
validation bypass, fabricated live receipt, or historical overwrite is introduced.
