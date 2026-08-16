# P01 Checkpoint Report v2 — Buildable Src-Layout Packaging Skeleton

**Phase**: P01 — Add the Buildable Src-Layout Packaging Skeleton
**Prompt**: `plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml` (version 3)
**Specification**: `plans_internal/refactor_repo/refactor_repository.spec.v8.html` (version 8)
**Baseline commit**: `c7c315ff512f939e7018c5c6c3f8bf0eb7e1d752` ("plans_internal/refactor_repo: P00A checkpoint QA_PASSED with corrected P02S v4 and acceptance criteria mapping")
**Execution run**: second retry (first retry's P02S v4 pyproject.toml authorization conflict already resolved in the working tree at run start)
**Timestamp**: 2026-08-16
**Supersedes**: `P01_checkpoint_report.v1.md` (deprecated by the QA gate after round 1; findings P01-QA-001, P01-QA-002, P01-QA-003 addressed below with re-executed, command-exact evidence)

---

## 1. Identity of the artifact being judged

- Executing prompt: P01_packaging_skeleton.prompt.v3.yaml, activated by `plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1.yaml` (`prompts.P01: {version: '3', status: active, path: plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml}`).
- Starting dirty state at P01 execution start (before this run's own actions): the working tree already carried, from before this journal existed, four untracked P01 deliverable files (`MANIFEST.in`, `pyproject.toml`, `src/curriculum_factory/__init__.py`, `tests/refactor_repo/test_packaging_skeleton.py`) and two modified-but-uncommitted prompt files outside P01's authorized_paths:
  - `plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml` — MANIFEST.in added to `authorized_paths`, goal text updated.
  - `plans_internal/refactor_repo/prompts/generated/P02S_structured_data_codemod.prompt.v4.yaml` — `pyproject.toml` and `*.toml` removed from `authorized_paths`.
  These two prompt-definition edits are **not** part of this checkpoint's delta (P01 has no authorization to edit either file and made no such edits in this run); recorded as pre-existing context per the user's second-retry framing.
- Artifact version: this report, `P01_checkpoint_report.v2.md`.

## 2. Changed / created paths and authorization boundary

Paths created or modified **by this P01 execution run**:

| Path | Action | Within P01 authorized_paths? |
|---|---|---|
| `pyproject.toml` | pre-staged before journal start, verified/adopted unchanged | yes (exact) |
| `MANIFEST.in` | pre-staged before journal start, verified/adopted unchanged | yes (exact) |
| `src/curriculum_factory/__init__.py` | pre-staged before journal start, verified/adopted unchanged (also deleted and restored byte-exact during rollback verification, §4) | yes (exact) |
| `tests/refactor_repo/test_packaging_skeleton.py` | pre-staged before journal start, verified/adopted unchanged (also deleted and restored byte-exact during rollback verification, §4) | yes (exact) |
| `plans_internal/refactor_repo/execution/P01/execution_log.jsonl` | created by this run | yes (exact) |
| `plans_internal/refactor_repo/execution/P01/.execution_log.counter.json` | created by this run | yes (exact) |
| `plans_internal/refactor_repo/execution/P01/.execution_log.lock` | created by this run | yes (exact) |
| `plans_internal/refactor_repo/checkpoints/P01/` (report v1, v2, QA/) | created by this run | yes (prefix) |

No file outside this list was modified by this run. Pre-existing changes to `plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml` and `plans_internal/refactor_repo/prompts/generated/P02S_structured_data_codemod.prompt.v4.yaml`, and the pre-existing untracked manifest-resolution artifacts under `plans_internal/refactor_repo/prompts/resolved/`, predate this run and are not this checkpoint's delta (see full raw `git status` in §6).

## 3. Prompt tests — exact commands, exit statuses, and conclusions

### Test 1 — Resolved manifest grants exact non-overlapping mutation ownership

**Command**:
```
python3 - <<'PY'
import yaml, sys, glob
manifest = yaml.safe_load(open('plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1.yaml'))
p01 = manifest['prompts']['P01']
assert p01['version'] == '3' and p01['status'] == 'active'
assert p01['path'] == 'plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml'
p01_paths = {'pyproject.toml', 'MANIFEST.in', 'src/curriculum_factory/__init__.py', 'tests/refactor_repo/test_packaging_skeleton.py'}
other_prompt_files = [f for f in sorted(set(glob.glob('plans_internal/refactor_repo/prompts/P0*.yaml')) | set(glob.glob('plans_internal/refactor_repo/prompts/generated/*.yaml'))) if 'P01_packaging_skeleton' not in f]
conflicts = []
for f in other_prompt_files:
    aps = set(yaml.safe_load(open(f)).get('authorized_paths', []))
    overlap = aps & p01_paths
    if overlap: conflicts.append((f, overlap))
print("EXACT_OVERLAPS_WITH_P01:", conflicts if conflicts else "NONE")
sys.exit(0 if not conflicts else 1)
PY
```
**Exit status**: `0`
**Material output**: `EXACT_OVERLAPS_WITH_P01: NONE` — enumerated all 12 other prompt files' (P00, P00A, P02, P02S v3, P02S v4, P03–P09) `authorized_paths` and intersected each against P01's exact four paths; zero intersections. The live P02S v4 file's `authorized_paths` (`*.json`, `*.yaml`, `*.yml`, `*requirements*.txt`, `.github/workflows/**/*.yaml`, `.github/workflows/**/*.yml`, plus its own checkpoint/execution/tool paths) contains no `*.toml` or `pyproject.toml` entry, confirming the second-retry fix holds in the file P02S actually executes under.
P03 and P04 list the broader directory prefix `src/curriculum_factory/`, which will later contain more than `__init__.py`; this is not a live conflict because P03/P04 `depends_on` chains (P03 → P02S → P02 → P01; P04 → P03) run strictly after P01 completes, and this checkpoint's own `test_src_curriculum_factory_package_exists_and_is_minimal` proves the directory currently contains only `__init__.py` — nothing P03/P04 would add exists yet.
The resolved manifest's stale `owns` label `pyproject_toml_identity_updates` for P02S is a documentation artifact from before the second-retry `authorized_paths` fix; P02S's actual enforcement surface (`authorized_paths`) cannot reach `pyproject.toml`, so no concrete unit is shared. Recorded as a non-blocking residual in §5, not silently ignored.

**Conclusion**: **PASS**.

### Test 2 — P00 prerequisite and metadata provenance are satisfied

**Prerequisite verification**:
- P00 repaired checkpoint witnessed QA_PASSED: `plans_internal/refactor_repo/checkpoints/P00/QA_repaired/rounds/round-02.response.json` → `"verdict": "PASS"` (committed `93c07ba`).
- P00A checkpoint v9 witnessed QA_PASSED: `plans_internal/refactor_repo/checkpoints/P00A/QA/rounds/round-05.response.json` → `"verdict": "PASS"` (committed `c7c315f`, current HEAD).

**Command** (provenance trace):
```
python3 - <<'PY'
import json, tomllib, sys
inv = json.load(open('plans_internal/refactor_repo/inventory/repair_20260816_120500/repository_refactor_inventory.20260816T122829Z.v1.json'))
pj = tomllib.load(open('pyproject.toml', 'rb'))
identities = {i['identity']: i for i in inv['identities']}
assert pj['project']['name'] == identities['Python distribution']['target_value'] == 'curriculum-factory'
assert identities['Python package']['target_value'] == 'curriculum_factory'
assert identities['Source root']['target_value'] == 'src/curriculum_factory/'
plan26 = open('requirements/plan26.in').read()
assert '>=3.13,<3.14' in plan26 and pj['project']['requires-python'] == '>=3.13,<3.14'
core_deps = {'langgraph==1.2.9','langgraph-checkpoint-sqlite==3.1.0','jsonschema==4.26.0','PyYAML==6.0.3','Pillow==12.2.0'}
assert set(pj['project']['dependencies']) == core_deps
assert set(pj['project']['optional-dependencies']['dev']) == {'pytest==9.0.3'}
readme = open('readme.md').read()
assert pj['project']['description'] in readme.replace('\n', ' ')
entry_points = {e['source_file']: e for e in inv['python_surface']['entry_points']}
expected_scripts = {
    'curriculum-factory-run-curriculum': 'curriculum_factory.run_curriculum:main',
    'curriculum-factory-session-bridge': 'curriculum_factory.session_bridge:main',
    'curriculum-factory-capability-cycle': 'curriculum_factory.capability_cycle:main',
    'curriculum-factory-finalize-evidence': 'curriculum_factory.finalize_evidence:main',
}
assert pj['project']['scripts'] == expected_scripts
assert set(entry_points.keys()) == {'runtime/run_curriculum.py','runtime/session_bridge.py','runtime/capability_cycle.py','runtime/finalize_evidence.py'}
assert all(e['kind'] == 'module_main_guard' for e in entry_points.values())
print("ALL_PROVENANCE_ASSERTIONS_PASSED")
PY
```
**Exit status**: `0`
**Material output**: `ALL_PROVENANCE_ASSERTIONS_PASSED`
`package-data` extensions (`*.json`, `*.md`, `*.yaml`, `*.mjs`) were traced separately: `find runtime -type f ! -name "*.py" ! -name "*.pyc" | sed 's/.*\.//' | sort -u` → `json`, `md`, `mjs`, `yaml` (exit 0), exactly matching the four declared package-data extensions. `version = "0.1.0"` is not present in the inventory (no prior distribution existed: `"current_values": []` for the Python distribution identity); it is recorded as a standard initial-release packaging default, not a dependency or command, so it does not defeat the "no invented dependency or command" expectation.

**Conclusion**: **PASS**.

### Test 3 — Package discovery is src-only and excludes repository contracts

**Commands** (build + inspect, checkout A of the two isolated checkouts used in Test 5):
```
$ rsync -a --exclude='.git' --exclude='__pycache__' --exclude='node_modules' --exclude='*.pyc' . /tmp/p01_ckA/     exit=0
$ python3.13 -m venv /tmp/p01_venvA && /tmp/p01_venvA/bin/pip install --quiet build                                exit=0
$ /tmp/p01_venvA/bin/python -m build --outdir /tmp/p01_distA /tmp/p01_ckA                                          exit=0
$ tar -tzf /tmp/p01_distA/*.tar.gz | grep -E "runtime/|tests/|policy/|schemas/|curricula/|docs/|outputs/|plans/"   grep_exit=1 (no matches)
```
**Material output**: sdist contains exactly 16 tar entries — `MANIFEST.in`, `PKG-INFO`, `pyproject.toml`, `readme.md`, `setup.cfg`, `src/`, `src/curriculum_factory.egg-info/` (+5 generated metadata files), `src/curriculum_factory/`, `src/curriculum_factory/__init__.py`. Wheel contains exactly 6 entries — `curriculum_factory/__init__.py` + 5 standard `dist-info` files. Leakage grep against both archives exits `1` (no match). An earlier control run with `MANIFEST.in` temporarily removed (same probe methodology) produced exit `0` from the identical grep against `tests/test_validate_instance.py` (the sole repository-root `tests/test*.py` file), proving the `MANIFEST.in` exclusion rule (`exclude tests/test*.py`) is load-bearing.

**Conclusion**: **PASS**.

### Test 4 — Distribution metadata and console entry points are explicit

**Commands**:
```
$ unzip -p /tmp/p01_distA/*.whl curriculum_factory-0.1.0.dist-info/METADATA           exit=0
$ tar -xzOf /tmp/p01_distA/*.tar.gz curriculum_factory-0.1.0/PKG-INFO                  exit=0
$ unzip -p /tmp/p01_distA/*.whl curriculum_factory-0.1.0.dist-info/entry_points.txt    exit=0
```
**Material output**: `METADATA` and `PKG-INFO` are byte-identical: `Name: curriculum-factory`, `Version: 0.1.0`, `Requires-Python: <3.14,>=3.13` (same constraint as declared, reordered by the metadata writer), 5 `Requires-Dist` runtime pins, `Provides-Extra: dev` + `Requires-Dist: pytest==9.0.3; extra == "dev"`. `entry_points.txt`:
```
[console_scripts]
curriculum-factory-capability-cycle = curriculum_factory.capability_cycle:main
curriculum-factory-finalize-evidence = curriculum_factory.finalize_evidence:main
curriculum-factory-run-curriculum = curriculum_factory.run_curriculum:main
curriculum-factory-session-bridge = curriculum_factory.session_bridge:main
```
matches all 4 P00-classified `module_main_guard` commands exactly. No console script was invoked; runtime invocation is explicitly deferred to P03.

**Conclusion**: **PASS**.

### Test 5 — Skeleton builds reproducibly without source movement

**Commands** (checkout B built identically to checkout A above, then compared):
```
$ rsync ... /tmp/p01_ckB/                                                                                exit=0
$ python3.13 -m venv /tmp/p01_venvB && /tmp/p01_venvB/bin/pip install --quiet build                      exit=0
$ /tmp/p01_venvB/bin/python -m build --outdir /tmp/p01_distB /tmp/p01_ckB                                exit=0
$ diff <(tar -tzf /tmp/p01_distA/*.tar.gz | sort) <(tar -tzf /tmp/p01_distB/*.tar.gz | sort)              exit=0 (identical)
$ diff <(unzip -l /tmp/p01_distA/*.whl|awk '{print $4}'|sort) <(unzip -l /tmp/p01_distB/*.whl|awk '{print $4}'|sort)   exit=0 (identical)
$ tar -xzf .../distA/*.tar.gz -C extractA && tar -xzf .../distB/*.tar.gz -C extractB
$ unzip -q .../distA/*.whl -d wheelA && unzip -q .../distB/*.whl -d wheelB
$ diff -rq extractA extractB                                                                              exit=0 (identical)
$ diff -rq wheelA wheelB                                                                                  exit=0 (identical)
$ diff <(find extractA -type f|sort|xargs shasum -a 256|sed s#extractA/##) <(same for extractB)           exit=0 (identical)
$ diff -rq --exclude=__pycache__ <live-repo>/runtime /tmp/p01_ckA/runtime                                 exit=0 (identical)
$ diff -rq --exclude=__pycache__ <live-repo>/runtime /tmp/p01_ckB/runtime                                 exit=0 (identical)
```
**Material output**: both builds exit 0; sdist/wheel file lists identical between A and B; recursive content diff of extracted sdist and wheel trees empty; per-file SHA-256 of all 12 extracted sdist files identical between A and B; `runtime/` byte-identical (excluding `__pycache__`) between the live repository and both isolated checkouts. Raw archive-level SHA-256 of the `.tar.gz`/`.whl` files themselves differ between A and B — expected, since both container formats embed per-file build timestamps; the test's own procedure calls for normalizing only those timestamps before comparing, which the extracted-content diff and per-file digest comparison above do.

**Conclusion**: **PASS**.

## 4. Prerequisites, non-targets, stop conditions, rollback — executed and verified

- P00/P00A prerequisite evidence: present, witnessed QA_PASSED, not stale (baseline commit `c7c315f` = HEAD at run start).
- Non-targets honored: no file under `runtime/` moved, no import rewritten, no resource loader repaired, no test renamed, no schema identifier changed, no installed behavioral parity claimed.
- No successor prompt's mutation authority borrowed (§ Test 1).
- **Rollback procedure — actually executed, not merely analyzed.** Commands run, in order:
  ```
  $ cp pyproject.toml MANIFEST.in tests/refactor_repo/test_packaging_skeleton.py src/curriculum_factory/__init__.py /tmp/p01_rollback_backup/...   exit=0
  $ rm -f pyproject.toml MANIFEST.in tests/refactor_repo/test_packaging_skeleton.py && rm -rf src                                                  exit=0
  $ python3 -m pytest tests/refactor_repo/test_inventory.py -q                                                                                     exit=0, "16 passed in 39.03s"
  $ cp /tmp/p01_rollback_backup/... <back to originals>                                                                                             exit=0
  $ python3 -c "<sha256 each restored file against pre-rollback digest>"                                                                            exit=0, ALL_MATCH
  $ python3 -m pytest tests/refactor_repo/test_packaging_skeleton.py -q                                                                             exit=0, "13 passed"
  ```
  After deleting all four P01 deliverables (`pyproject.toml`, `MANIFEST.in`, `src/curriculum_factory/__init__.py` and the now-empty `src/`, `tests/refactor_repo/test_packaging_skeleton.py`), the P00 inventory reproducibility test suite (`tests/refactor_repo/test_inventory.py`, P00's own authorized test file) was run against the reverted tree and passed unchanged (16/16), proving P00 evidence and reproducibility machinery are unaffected by reverting P01. All four files were then restored from the pre-rollback backup and their SHA-256 digests verified to match the pre-rollback values exactly (`pyproject.toml=b1f0a183...`, `MANIFEST.in=36ebe432...`, `src/curriculum_factory/__init__.py=373ca383...`, `tests/refactor_repo/test_packaging_skeleton.py=0ea463de...`), and the local packaging test suite re-passed (13/13) after restoration.

## 5. Residuals

- Stale `owns` label `pyproject_toml_identity_updates` under P02S in `prompt_manifest.resolved.v1.yaml`: **recorded exception**, unreachable given P02S v4's corrected `authorized_paths`, out of P01's authorization to edit (see Test 1). Recommend a manifest-owning process (P00A or later) regenerate this label in a future pass; does not affect this checkpoint's correctness.
- No other residual old identities, paths, imports, output consumers, or schema references are within P01's scope.

## 6. Post-change git status (complete, unfiltered)

```
$ git status --short --untracked-files=all
 M plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml
 M plans_internal/refactor_repo/prompts/generated/P02S_structured_data_codemod.prompt.v4.yaml
?? MANIFEST.in
?? plans_internal/refactor_repo/checkpoints/P01/
?? plans_internal/refactor_repo/execution/P01/
?? plans_internal/refactor_repo/prompts/resolved/deprecated/prompt_manifest.resolved.v1.yaml
?? plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1_modified.yaml
?? plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v2.yaml
?? pyproject.toml
?? src/curriculum_factory/__init__.py
?? tests/refactor_repo/test_packaging_skeleton.py
```
Both `M` lines (the two prompt-definition edits) predate this run's journal (filesystem mtimes 2026-08-16T09:42 and 09:56, both before ACT-001 at 10:0x) and were not made by this P01 execution — see §1/§2. The three untracked files under `plans_internal/refactor_repo/prompts/resolved/` (`deprecated/prompt_manifest.resolved.v1.yaml`, `prompt_manifest.resolved.v1_modified.yaml`, `prompt_manifest.resolved.v2.yaml`) likewise predate this run (mtimes 08:53–09:02) and are outside P01's authorized_paths; not created or modified by this run.

**Deliverable digests (SHA-256)**:
| File | SHA-256 |
|---|---|
| `pyproject.toml` | `b1f0a1837563edf6219806f4e34cb0be9d1985060ddd17ee238dc5a484c7b820` |
| `MANIFEST.in` | `36ebe4327048aae325d514661111a83fed32085957ae00515fde0c99638ce79a` |
| `src/curriculum_factory/__init__.py` | `373ca38365f43cb6cc6d90767f48c61a7b2ab38a8693094d2f32a7deafe12404` |
| `tests/refactor_repo/test_packaging_skeleton.py` | `0ea463de2c5a2d5675196b62015e511f0cc5ff456226cb82eb198f4586d1e9b7` |
| `P01_checkpoint_report.v1.md` | `8114e92e7575696e91ab91b30540224840c7daa841b10d0181a94396d07e4c13` |
| `execution/P01/execution_log.jsonl` (snapshot after record ACT-014, 14 records) | `eba5f9b299bed30dccf49258a8deaa6696c51d037152fbaaa927793ee28bf69a` |

The execution journal is append-only by design (schema `execution_log.schema.v2.json`); the digest above is an immutable-prefix snapshot as of the record count noted, not a final value — later records in this same checkpoint (recording this report's own creation and Test 6) necessarily extend the file. The completion-gate-relevant invariant is zero unclosed starts at final audit, verified in §7, not a frozen file digest. `.execution_log.counter.json` and `.execution_log.lock` are logger-internal bookkeeping files (a monotonic counter and an flock target) with no independent content meaning to digest.

Rollback checkpoint verification result: **executed and verified**, evidence in §4 (`pytest tests/refactor_repo/test_inventory.py` exit 0/16-passed post-revert; all 4 restored files SHA-256-matched pre-rollback digests; `pytest tests/refactor_repo/test_packaging_skeleton.py` exit 0/13-passed post-restore).

## 7. Completion status

Local test suite: `pytest tests/refactor_repo/test_packaging_skeleton.py -q` → **13 passed**, run three times across this checkpoint (initial, post-rollback restore, final) with identical results each time.
Execution journal: `plans_internal/refactor_repo/execution/P01/execution_log.jsonl`; `ExecutionLogger.audit()` at the time this v2 report was finalized: `records=14, starts=7, completions=7, failures=0, monotonic=true, unclosed_starts=[]`.
Tests 1–5 above: all **PASS**, each with an exact command, exit status, and material output recorded.
QA round 1 (transport=exec) on `P01_checkpoint_report.v1.md` returned `codex_verdict: FAIL` with 3 blocker findings (P01-QA-001, P01-QA-002, P01-QA-003), all addressed above in this v2 with re-executed, command-exact evidence. This v2 report does not itself claim Test 6's outcome; the gate's own `verify` output is the sole authority for that, appended to `plans_internal/refactor_repo/checkpoints/P01/QA/`.
