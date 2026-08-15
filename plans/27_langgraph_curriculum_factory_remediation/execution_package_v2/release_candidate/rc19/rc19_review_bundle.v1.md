# Run 27 RC19 — external staged-verifier review bundle

## Decision requested

Independently determine whether graph v9 is safe to enter and capable of a fresh
N00→N90 cascade. RC14–RC17 found progressively narrower verifier-closure defects.
RC18 contained the final external-staging implementation, but its apparent QA pass
failed rollout verification because the response simultaneously said PASS and that
its required probes were unfinished. RC19 submits the same unchanged implementation
to a fresh QA session; no RC18 verdict is carried forward.

## Preserved lineage

- Graph v8 remains byte-identical at
  `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`.
- Its N00–N60 evidence and five failed N70 attempts remain historical; attempt 5
  is archived at `outputs/run27/archive/live_unit_v8_attempt_05_domain_pre_admission_repair`.
- RC10–RC18 and every QA/postmortem record remain intact. RC18 is explicitly an
  `INTEGRITY_BREACH`, not approval evidence.

## Closed verifier boundary

1. The curriculum schema requires a bounded unique verifier-dependency list; the
   active Arduino manifest declares every schema/calibration/library file read by
   `verify_domain.py`.
2. D02 resolves all verifier inputs within the curriculum, matches exact D01-frozen
   hashes, and binds the complete closure into effective-run identity.
3. D08 re-hashes entry, dependencies, and positive/negative fixtures, then hashes
   the bytes again while copying them into the staged snapshot. Source drift or a
   hash/copy race fails before execution.
4. `domain_verifier_work_root` derives a stable namespace beneath the resolved
   system temporary directory from the output-root digest. It rejects any root
   equal to or below the engine or output root. A direct regression uses the real
   shape `engine/outputs/run27/live_unit` and proves the resulting verifier root is
   outside both namespaces.
5. Contract and candidate digests address the work directory. `frozen/` preserves
   original relative layout, so relative sidecars resolve only to declared staged
   bytes; conflicting existing snapshot bytes fail closed.
6. Executed argv names the staged entry and staged candidate/fixture, with cwd at
   the external work directory. The sandbox denies network, omits model auth and
   scratch rules, permits no engine content reads, and denies all engine-root
   metadata without exemptions.
7. The receipt binds the recomputed contract, candidate, entry, dependency set,
   invocation, and complete fixture outcomes.

Host regressions prove declared workspace metadata works; an undeclared engine file
and the engine directory cannot be statted; engine-nested output maps outside the
engine; the active Arduino verifier/fixtures execute from the staged snapshot; and
declared dependency drift fails before execution.

## Carried-forward guarantees

- M02 has only admitted claims and verified staged inputs, with no admission or
  verifier authority.
- Invalid first domain/content/visual versions stay immutable and non-head; repair
  targets exact bytes, remains bounded, preserves lineage, and revalidates the exact
  repaired head.
- D08/D09/D12/D20 persist canonical bytes before reads, replay idempotently across
  nodes, reject conflicts, and never replace repaired heads with stale state.

## Active bindings and executed proof

- Graph v9: `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`.
- Approval schema v6: `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`.
- Approval contract v6: `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`.
- Governing specification: `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.
- Fresh results/state: `execution_package_v2/results/v9/` and `.run27_state_v9/`.
- Package: 176 passed; focused runtime/repair: 799 passed; combined: 975 passed.
- Full runtime: 1352 passed, 2 skipped, 419 subtests passed.
- Plan 26 N13 is current with no stale receipts; plan/ownership/compile/whitespace
  validations pass.

No billed API key, provider SDK, direct model HTTP call, wildcard retrieval host,
validation bypass, fabricated live receipt, or historical overwrite is introduced.
