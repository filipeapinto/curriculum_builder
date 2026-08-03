# Gate Flakiness — Execution Test Plan v1

## Purpose and boundary

Test `plans/_eval_gf_bl/gate_flakiness.plan.v1.md` without implementing it. This plan is
the acceptance procedure; it does not authorize edits.

Evidence goes under `/private/tmp/gate-flakiness-test-<UTC>/`, never the repository. Every
gate invocation in every test sets `FR_RESULTS_DIR` to a fresh subdirectory of that root,
so no test writes into `tests/results/` — which already holds 274 accumulated files and is
never truncated (`runner.py:78-86`).

Tests never stage, stash, restore, reset, or clean. The worktree carries unrelated user
work and must end byte-identical to `GF-T00`.

The implementation-allowed set is `tests/gates/**` and `tests/run_gates.sh`. A test that
requires an edit outside it is a stop, not a waiver.

## Ordered tests

### GF-T00 — Read-only baseline and corpus freeze

Before any edit:

1. `git status --porcelain=v2 -z --untracked-files=all`, `git diff --binary`, and
   `git diff --cached --binary`, stored raw with SHA-256.
2. `./tests/run_gates.sh 4` and `./tests/run_gates.sh 5`, each twice, into four separate
   external results directories. Record exit codes and the full per-gate `id → (status,
   detail)` map for each.
3. The full phase 0–5 sweep, once, per gate id. This is the regression guard for step 4 of
   the plan, whose effects reach `FR-P0-REGISTRY`.
4. The frozen corpus: the sorted output of `common.production_files()` with SHA-256 per
   file, plus the count broken down by top-level directory.
5. `sys.executable`, `python3 --version`, `which python3`, `PYTHONHASHSEED`, `LC_ALL`, and
   the four `FR_*` overrides.

Pass when the two phase-4 runs and the two phase-5 runs are identical except for the
results filename. If they are **not** identical, that is a live in-process nondeterminism
bug: capture both records, stop, and report it — the plan's diagnosis would be incomplete
and must be revised before implementation.

Expected at time of writing: exit 1 on both phases; phase 5 reports 35 PASS, 3 FAIL, 0
BLOCKED, 0 SKIPPED of 38; the failures are `FR-P0-CLEAN`, `FR-P0-NOSTALE`, and
`FR-P3-CAPS-OWNED`. A different baseline is not a failure of this test, but it must be
recorded as the baseline actually used.

### GF-T01 — Ambient drift reproduction, before any fix

Prove the bug exists and that the fix has something to fix. In an external scratch copy of
the repository — never the working repository — inject each of the following one at a time
and re-run the affected phase:

1. A file under `.claude/` containing the string `RT-9`. Require `FR-P2-DEFERRED` to move
   to FAIL and require `FR-P4-CHECK-MAPPING` and `FR-P4-AGREEMENT` to become BLOCKED
   (`registry.py:276`, `registry.py:260`).
2. A file under `outputs/` containing a `SEL-*` identifier absent from the manifest.
   Require `FR-P2-SEL-MAPPED` (`fr_p2_selector.py:550`) to move to FAIL.
3. A `.DS_Store` in a scanned directory. Require it to appear in a scan set and be read as
   text (it has no `Path.suffix`, so `BINARY_SUFFIXES` at `common.py:60-62` misses it).
4. `git add` of one unrelated file. Require `FR-P0-NOSTALE`'s scanned-file count to change
   (`fr_p0_structure.py:278-292`).

Each injection must be reverted and the phase re-run to the `GF-T00` verdict before the
next is applied. An injection that does **not** move a verdict is recorded as such; the
corresponding plan step then has no demonstrated cause and must be deferred under the
plan's own rule.

### GF-T02 — Diagnostic lands first and is itself deterministic

After plan step 1 only, with no scan-set change yet:

- Re-run both phases and require the per-gate map to equal `GF-T00` exactly. The diagnostic
  must be observation-only; if adding it moves a verdict, it is instrumenting the thing it
  measures.
- Require the result record to contain `run_environment` with the scan-set digest, git
  `HEAD`/index/dirty state, the four `FR_*` values, interpreter path and version, and
  `PYTHONHASHSEED`.
- Feed `run_diff.py` the two `GF-T00` phase-5 records and require "no transitions". Feed it
  a `GF-T00` record and a `GF-T01` injected record and require it to name the transitioned
  gate **and** the injected file in the scan-set delta. A diff tool that reports the
  transition without attributing it does not satisfy the plan's purpose.
- Run the new determinism self-test and require it to pass. Then, in an external copy,
  perturb one gate to return a time-dependent verdict and require the self-test to FAIL.
  A self-test that has never been seen to fail is not evidence.

### GF-T03 — Scan-set correctness, both directions

After plan step 2. Both directions are required; either alone is a defect.

**Must be excluded** — adding each of these must leave every gate verdict unchanged:
a file under `outputs/`, a file under `.claude/`, a `.pytest_cache/` entry, a
`__pycache__/` entry, and a `.DS_Store`. Re-run `GF-T01`'s injections 1–3 and require them
to be inert.

**Must be included** — each of these must still be scanned, proven by injecting a defect
the corresponding detector is required to catch:
a tracked source file; an **untracked, non-ignored** newly authored source file (finding 2
of QA — this is the case the naive fix loses); a file in a directory that did not exist at
`GF-T00`; and a file whose name resembles an ambient path but is tracked authored content.

Additionally:

- Diff the new scan set against the `GF-T00` frozen corpus and require every removed path to
  be a member of the declared ambient set. A removal outside it fails this test.
- Require the ambient-membership assertion to fail when an ambient entry is made tracked
  authored content.
- Simulate git failing (`git` returning non-zero) and require a raised error, not a
  filesystem-walk fallback and not an empty-set pass.

### GF-T04 — `FR-P0-CLEAN` and `FR-P0-NOSTALE` subject correction

After plan step 3:

- Dirty a path outside the scan set (`plans/`, `docs/`, `outputs/`) and require
  `FR-P0-CLEAN` to be unaffected.
- Dirty a tracked source file inside the scan set and require `FR-P0-CLEAN` to FAIL and to
  name it. The gate must still guard `APPROVED`; assert its outcome semantics are unchanged
  and that it was not moved to a later `activation_phase` (`registry.py:104-111`).
- Make `git status` itself fail and require `GateFailure`, preserving the existing
  false-PASS defense at `fr_p0_structure.py:591-595`.
- Stage and unstage an unrelated file and require `FR-P0-NOSTALE`'s scanned-file count and
  verdict to be unchanged across all four index states.

### GF-T05 — Retroactive class-drift flip

After plan step 4:

- Assert `fr_p5_verifier.py` records `execution` and `fr_p5_manifest.py` records `schema` on
  **every** path, including the early return, by exercising a curriculum with a declaration
  defect and one with an unresolvable `declared_contract`.
- Require `FR-P0-REGISTRY` to remain PASS in both cases, where before the fix
  `_class_drift_sweep` (`runner.py:196-231`) rewrote it to FAIL at `runner.py:224-228`.
- Assert the sweep is still present and still fires: introduce a genuine declared-versus-
  reported mismatch and require `FR-P0-REGISTRY` to FAIL. The sweep must not be weakened;
  only the conditional recording it observes may change.

### GF-T06 — Environment pinning

After plan step 5:

- Require `run_gates.sh` and in-gate subprocesses to resolve to the same interpreter, and
  require it to appear in the result record.
- Run both phases with `PYTHONPATH` polluted and require `FR-P5-VERIFIER-REQUIRED`
  (`fr_p5_verifier.py:109-128`) to report an environment error, **not**
  `verifier-fixture-accepted` or `wrong-reason`. An environment fault reported as a
  curriculum defect is the specific misclassification under test.
- Run both phases under `PYTHONHASHSEED` ∈ {0, 1, 42, 999} and `LC_ALL` ∈ {C, C.UTF-8,
  en_US.UTF-8} and require identical per-gate maps.
- Set each of `FR_GATE_REGISTRY`, `FR_RESULTS_DIR`, `FR_GATES_DIR`, `FR_PHASE` and require
  each to be recorded in the result. Run `FR-P0-REGISTRY` standalone as documented at
  `registry.py:45` with `FR_PHASE` set to a wrong value and require an explicit failure
  rather than a silently different `gate-not-implemented` count
  (`fr_p0_structure.py:756`).

### GF-T07 — Full-sweep regression and per-gate justification

Run phases 0 through 5 and compare per gate id against `GF-T00`. Produce a table of every
gate whose status or detail changed, each mapped to the plan step that intended it. Any
unexplained change fails. Any gate outside phases 4 and 5 that regressed fails. New gate
ids, missing gate ids, crashes, and `SKIPPED`-membership changes for the same requested
phase all fail.

`FR-P0-CLEAN` failing on the implementation's own uncommitted edits is expected and is not
a failure of this test.

### GF-T08 — Deferred-scope audit

Diff the implementation against `GF-T00`. Require that none of the plan's step-6 deferred
items was touched: `fr_p5_verifier.py:62`, `common.py:299-306`, `verify_domain.py:87-91`,
`common.py:438-453`, `fr_p4_policy_schemas.py:177-182`, `fr_p5_unit.py:206`. Require every
changed path to be within `tests/gates/**` or `tests/run_gates.sh`. Require no assertion to
have been weakened, no waiver added, and no `activation_phase` changed.

### GF-T09 — Worktree integrity

Compare the repository to `GF-T00`. Pass only if the cached diff and every pre-existing
index object are unchanged, execution staged nothing, pre-existing unstaged and untracked
bytes outside the allowed set are identical, and no unrelated mode, symlink target, or file
hash changed. Confirm `tests/results/` gained no files.

## Final audit and pass rule

After every repair, re-run `GF-T02`'s determinism self-test immediately, then re-run the
failed test and every later test whose evidence may have changed. After all tests, re-run
`GF-T07` and `GF-T09` once more.

Pass only when: `GF-T01` demonstrated the bug before the fix; `GF-T03` passed in **both**
directions; every verdict change in `GF-T07` is justified; `GF-T08` shows no deferred item
was fixed; and the worktree is intact. Exit code 0 is not required and must not be pursued.

Record test ids, commands, exit codes, artifact hashes, the per-gate comparison table, the
demonstrated-cause list, and the final verdict in
`plans/_eval_gf_bl/gate_flakiness.result.v1.md`. Append the outcome to the shared log;
never edit prior entries.
