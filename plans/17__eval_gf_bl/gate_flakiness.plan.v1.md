# Gate Flakiness — Implementation Plan v1

## Status and objective

Planning only; no implementation is authorized by this document's creation.

Diagnose and eliminate the reported class of defect in which a phase 4 or phase 5 gate
run returns a different verdict than an immediately preceding run, with no change to
repository source between the two runs.

This plan revises v1 in place after focused QA. It carries the remediations for one
Critical and four High findings recorded in `qa/plan_qa.v1.md`.

## What the reported symptom actually is

A read-only reproduction was performed before this plan was written, with results
redirected out of the repository via `FR_RESULTS_DIR`:

```
FR_RESULTS_DIR=$T/r1 ./tests/run_gates.sh 4   → exit 1
FR_RESULTS_DIR=$T/r2 ./tests/run_gates.sh 4   → exit 1
FR_RESULTS_DIR=$T/r51 ./tests/run_gates.sh 5  → exit 1
FR_RESULTS_DIR=$T/r52 ./tests/run_gates.sh 5  → exit 1
```

Back-to-back output was **byte-identical apart from the results filename**. This
falsifies the intuitive hypothesis and fixes the plan's direction:

- The harness is **not** internally nondeterministic. Gate order is Kahn with ties broken
  by sorted id (`tests/gates/runner.py:52-71`). There is no `random`, `uuid`, `hash()`,
  sampling, threading, or network call anywhere under `tests/gates/`. Phase 4 and phase 5
  checks were additionally executed under `PYTHONHASHSEED` ∈ {0,1,2,7,999,12345,424242}
  with identical output.
- The flake is **ambient state drift between runs**. Several gates that run during phases 4
  and 5 take a mutable, non-source part of the machine as their subject: the git worktree,
  the git index, agent scratch under `.claude/`, generated run output under `outputs/`, and
  OS files. Between two runs, an unrelated tool writes one of those, and the verdict moves.
  From the developer's seat this is indistinguishable from a flaky test, because *the source
  under test genuinely did not change*.

The reproduction captured three live instances of exactly that mechanism:

| Gate | Observed verdict | Subject that drifted |
| --- | --- | --- |
| `FR-P0-CLEAN` | FAIL, 30+ dirty entries | the developer's uncommitted work (`tests/gates/fr_p0_structure.py:589-603`) |
| `FR-P0-NOSTALE` | FAIL, 8 hits | 3 of 8 hits are in `.claude/skills/curriculum-concept-visualization/`, authored by an agent in the most recent commit |
| `FR-P3-CAPS-OWNED` | FAIL, 2 hits | both hits in `docs/research/**`, prose that merely quotes a cap name |

`common.production_files()` (`tests/gates/common.py:75-101`) defines the scan set by
exclusion of `{"tests", "plans", ".git"}` (`common.py:55`). Enumerated live it is **645
files, of which 448 are under `outputs/`, 53 under `.claude/`, 5 under `.pytest_cache/`,
and 1 is a `.DS_Store`** — 78% of the normative "production" corpus is generated output,
agent scratch, build cache, and Finder droppings, all of which change without a commit.

## Blast radius, and why this reaches phase 4

Ambient drift is not confined to the gate that observes it. `FR-P2-DEFERRED`
(`fr_p2_selector.py:333`) greps every production file for `RT-<n>` identifiers, and it is a
declared dependency of `FR-P4-CHECK-MAPPING` (`registry.py:276`), which is a declared
dependency of `FR-P4-AGREEMENT` (`registry.py:260`). A single agent log under `.claude/`
containing the string `RT-9` flips `FR-P2-DEFERRED` to FAIL and **BLOCKS two phase-4
gates**. All four pass today; nothing in the harness prevents the next tool invocation from
breaking them.

A second, independent mechanism can move a verdict *after the gate has been reported*.
`common.RUN_STATE` (`common.py:68`) accumulates each gate's reported mechanisms, and
`_class_drift_sweep` (`runner.py:196-231`) rewrites an already-recorded `PASS` into `FAIL`
at `runner.py:224-228` when a gate's reported class differs from its declared
`claim_class`. Several phase-5 gates record their class **conditionally on data**:
`fr_p5_verifier.py:151-153` only records `execution` if `declaration_violations` came back
empty; `fr_p5_manifest.py:140-144` only records `schema` if `declared_contract` resolved.
So a curriculum-data change silently flips the phase-0 gate `FR-P0-REGISTRY`.

## Design principle

Two categories are currently conflated and must be separated:

1. **Repository content under review** — authored, version-controlled source that a
   detector must see. Narrowing this set silently disables a detector. `common.py:53-56`
   already warns about exactly this, and that warning is binding.
2. **Ambient artifacts** — generated output, agent scratch, build caches, OS files. These
   are not authored, are not reviewed, and must never be a gate's subject.

The discriminator must be **derived, not hand-maintained**. A second literal name list is
the defect `common.py:53-56` exists to prevent. Git tracking status is the existing
single source of truth for "authored content", and the repository already uses it
(`fr_p0_structure.py:278-292`).

**Critical-remediation constraint.** Tracking status alone is unsafe: a newly authored,
not-yet-added source file would become invisible to every detector, which converts a
flakiness fix into a silent correctness regression. Therefore the scan set is
`tracked ∪ untracked-and-not-ignored`, minus an explicitly declared ambient set, and the
ambient set is declared **once**, in data, and asserted to be a subset of what `.gitignore`
already excludes. An untracked file that git would keep stays in the scan set.

## Exact work

### 0. Freeze a reproduction corpus before any edit

- Capture `git status --porcelain=v2 -z --untracked-files=all`, `git diff --binary`, and
  `git diff --cached --binary` to an external root under `/private/tmp/`. Never stage,
  stash, reset, restore, or clean. The worktree is dirty with unrelated user work and must
  survive this task byte-identical.
- Record the full phase-4 and phase-5 baseline: exit codes, per-gate id → status, and each
  gate's detail line, with `FR_RESULTS_DIR` pointed outside the repository. Every later
  comparison is against this frozen record, by gate id, never by aggregate count.
- Build a frozen corpus fixture that pins the scan set: the sorted list of paths
  `production_files()` returns today plus each file's SHA-256. This is the artifact that
  makes "did the verdict move because the code changed, or because the corpus changed?"
  answerable.

### 1. Make drift observable before fixing anything

No cause is repaired until it has been *demonstrated* to move a verdict. The diagnostic
lands first, because today the result JSON records the verdict but not the subject, so two
differing runs cannot be attributed.

- Extend the result record written at `runner.py:155-166` with a `run_environment` block:
  the resolved scan-set size and its SHA-256 digest-of-digests; the git `HEAD`, index, and
  worktree-dirty state; the values of `FR_GATE_REGISTRY`, `FR_RESULTS_DIR`, `FR_GATES_DIR`,
  and `FR_PHASE`; `sys.executable` and its version; and `PYTHONHASHSEED`.
- Add `tests/gates/run_diff.py`: given two result JSON files, report per-gate status
  transitions and, for any transition, the scan-set delta between the two runs. A gate that
  moved with an empty scan-set delta and an identical `run_environment` is a real
  nondeterminism bug; a gate that moved alongside a corpus delta is ambient drift, and the
  delta names the file responsible.
- Add a determinism self-test to `tests/gates/selftest.py`: execute the requested phase
  twice in one invocation against the frozen corpus and require byte-identical per-gate
  status and detail. This is the permanent regression test for the whole class.

### 2. Separate the ambient set from repository content

- Add `PRODUCTION_AMBIENT` to `tests/gates/common.py` beside the existing rule-7 exclusion,
  declared once as data and documented as the *ambient* category, not a second copy of the
  content category: `outputs/`, `.claude/`, `.pytest_cache/`, `__pycache__/`, `.DS_Store`.
- Change `production_files()` (`common.py:75-101`) to return
  `(tracked ∪ untracked-not-ignored) − PRODUCTION_AMBIENT`, resolved from
  `git ls-files -z --cached --others --exclude-standard`. Preserve `BINARY_SUFFIXES`
  filtering, and additionally skip extensionless non-UTF-8 files so `.DS_Store`-shaped
  files cannot be read as text (`common.py:60-62` misses them today).
- Add an assertion that every `PRODUCTION_AMBIENT` entry is actually ignored or generated —
  if a member becomes tracked authored content, the harness fails loudly rather than
  silently narrowing a normative scan set.
- If git is unavailable or errors, raise rather than fall back to a filesystem walk. The
  precedent is `check_clean` (`fr_p0_structure.py:591-595`): an empty result from a failed
  git is never a pass.

### 3. Correct the two gates whose subject is the developer's machine

- `FR-P0-CLEAN` (`fr_p0_structure.py:589-603`) cannot pass on any working machine with
  in-flight edits, yet it runs at every phase (`registry.py:104-111`, `activation_phase: 0`)
  and owns the run's exit code. Constrain its subject to paths inside the scan set defined
  in step 2, so unrelated user work in `plans/`, `docs/`, and `outputs/` does not fail a
  phase-5 run. Do not delete the gate, do not exempt tracked source, and do not downgrade
  its outcome — it still guards `APPROVED`.
- `FR-P0-NOSTALE` (`fr_p0_structure.py:278-292`) resolves its scan set from `git ls-files`,
  i.e. the **index**, so `git add` of an unrelated file changes its subject between runs.
  Route it through the step-2 scan set so index state is no longer an input.

### 4. Remove the retroactive class-drift flip

- Make each phase-5 gate's reported mechanism set reflect the mechanisms the gate
  *implements*, not the branches its data happened to take. `fr_p5_verifier.py:151-153` and
  `fr_p5_manifest.py:140-144` must record `execution` and `schema` respectively on every
  path, including the early-return path.
- Keep `_class_drift_sweep` (`runner.py:196-231`). It is the correct closure of
  `FR-P0-REGISTRY` (d) and must not be weakened; the defect is the conditional recording it
  observes, not the sweep.

### 5. Pin the execution environment

- `tests/run_gates.sh:14-15` execs `python3` from `$PATH` while every in-gate subprocess
  uses `sys.executable` (`common.py:274-282`). Resolve both to one interpreter and record it.
- `ev.run` passes no `env=`, so `FR-P5-VERIFIER-REQUIRED` executes curriculum-supplied code
  (`fr_p5_verifier.py:109-128`) under the caller's whole environment; a `PYTHONPATH` change
  makes the verifier exit non-zero and be reported as `verifier-fixture-accepted`, i.e. an
  environment fault reported as a curriculum defect. Pass an explicit minimal environment
  and classify a subprocess failure that is not a fixture verdict as an environment error.
- Set `PYTHONHASHSEED=0` and `LC_ALL=C.UTF-8` in `run_gates.sh`. Hash-seed sensitivity is
  present but not currently expressed by the data; pinning is one line and removes the
  variable from every future investigation.
- Record all four `FR_*` overrides in the result record (step 1) rather than removing them.
  `FR_PHASE` (`fr_p0_structure.py:756`) is the one exception: it makes the standalone
  command documented at `registry.py:45` disagree with the runner-executed code, so
  `check_registry` must take the phase from `RUN_STATE` and fail explicitly when it is
  absent, instead of silently reading a shell variable.

### 6. Deferred, with reasons

These were found during diagnosis, are not demonstrated to have moved a verdict, and are
**out of scope** for this task. Record them; do not fix them here.

- `fr_p5_verifier.py:62` resolves curriculum versions lexicographically
  (`sorted(...)[-1]`), so `v10` sorts before `v5`. Latent until a v10 exists.
  `common.family_plan_path` (`common.py:531-540`) already parses the version as `int` and is
  the model for the fix.
- `common._validate_obj` (`common.py:299-306`) reports only `errors[0].message`, and
  `FR-P4-FIXTURE-BITES` (`fr_p4_policy_schemas.py:393`) asserts a literal message string.
  Three errors are produced for that fixture and the sort happens to select the expected
  one.
- The same sort key is a list of mixed `str`/`int` path segments, which would raise
  `TypeError` on a comparison that is currently unreachable; `runner.py:130-131` would
  report it as a gate FAIL rather than an environment fault.
- `verify_domain.py:87-91` caps errors at `[:5]` after sorting, over a jsonschema iteration
  order that is set-based for `additionalProperties`-as-object.
- `common.merged_check_inventory` (`common.py:438-453`) and the inline merge at
  `fr_p4_policy_schemas.py:177-182` are two different implementations of the same merge, so
  `FR-P4-CHECK-MAPPING` and `FR-P4-AGREEMENT` can see different declared id sets.
- `fr_p5_unit.py:206` derives Bloom ordering from YAML key order, so reordering keys in
  `policy/calibration.v1.yaml` — a no-op to a human — inverts `below`/`above` verdicts.

## Verification sequence

1. Run the step-1 determinism self-test; require identical twin runs.
2. Run phases 4 and 5 and compare per gate id against the frozen step-0 baseline. Any
   change must be individually justified as an intended step-2/3/4 effect.
3. Prove each repaired cause with the negative test that failed before the fix.
4. Re-run the full phase 0 through 5 sweep; no gate outside phases 4 and 5 may regress.
5. Confirm the user's dirty worktree is byte-identical to the step-0 capture.

## Acceptance criteria

- Two consecutive runs of phase 4 and of phase 5 produce identical per-gate status and
  detail, and this is enforced by a permanent self-test rather than by observation.
- Writing a file under `outputs/`, `.claude/`, or `.pytest_cache/`, or creating a
  `.DS_Store`, cannot change any gate verdict. Each is proven by a negative test.
- Adding an untracked, non-ignored source file **is** still seen by the detectors. The
  fix does not narrow the reviewed corpus.
- `git add` of an unrelated file does not change `FR-P0-NOSTALE`'s subject.
- A phase-5 data change cannot retroactively flip `FR-P0-REGISTRY`.
- Every gate whose verdict changed relative to baseline is named, with the intended cause.
- No deferred item in step 6 was fixed opportunistically.
- The result record identifies the interpreter, scan-set digest, git state, and every
  `FR_*` override, so a future divergence is attributable from artifacts alone.

## Stop conditions and result

Stop on: a collision with pre-existing user work; a required repair outside
`tests/gates/**` and `tests/run_gates.sh`; a baseline `PASS` becoming `FAIL` that cannot be
explained as an intended effect; or discovery that a proposed exclusion would hide authored
content. Do not respond to a failing gate by weakening its assertion, by adding a waiver,
or by moving a gate to a later activation phase.

`FR-P0-CLEAN` will fail for as long as this task's own edits are uncommitted. That is
correct behavior and is not to be "fixed"; compare it against baseline by gate id, not by
requiring exit 0.

Write `plans/_eval_gf_bl/gate_flakiness.result.v1.md` with the baseline, the per-gate
comparison, each demonstrated cause and its negative test, the deferred list, and remaining
failures. Append the outcome to `plans/_eval_gf_bl/plans.log.md`.
