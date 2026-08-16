# P01 Checkpoint Report v4 — Buildable Src-Layout Packaging Skeleton

**Phase**: P01 — Add the Buildable Src-Layout Packaging Skeleton
**Prompt**: `plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml` (version 3)
**Specification**: `plans_internal/refactor_repo/refactor_repository.spec.v8.html` (version 8)
**Baseline commit**: `c7c315ff512f939e7018c5c6c3f8bf0eb7e1d752` ("plans_internal/refactor_repo: P00A checkpoint QA_PASSED with corrected P02S v4 and acceptance criteria mapping")
**Execution run**: second retry (first retry's P02S v4 pyproject.toml authorization conflict already resolved in the working tree at run start)
**Timestamp**: 2026-08-16
**Supersedes**: `P01_checkpoint_report.v3.md`, moved by the QA gate tool to `plans_internal/refactor_repo/checkpoints/P01/deprecated/P01_checkpoint_report.v3.md` on this round (v1 and v2 were likewise moved to that `deprecated/` directory after rounds 1 and 2). Round 3 finding P01-QA-003 addressed below: §6's git status is now captured **after** this v4 file was written to disk (and before it is submitted to the QA tool, so the prior version has not yet been moved to `deprecated/` by the tool at capture time), so it reflects the actual on-disk state of the artifact being judged rather than a pre-existing snapshot.

---

## 1. Identity of the artifact being judged

- Executing prompt: P01_packaging_skeleton.prompt.v3.yaml, activated by `plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1.yaml` (`prompts.P01: {version: '3', status: active, path: plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml}`).
- Starting dirty state at P01 execution start (before this run's own actions): the working tree already carried, from before this journal existed, four untracked P01 deliverable files (`MANIFEST.in`, `pyproject.toml`, `src/curriculum_factory/__init__.py`, `tests/refactor_repo/test_packaging_skeleton.py`) and two modified-but-uncommitted prompt files outside P01's authorized_paths:
  - `plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml` — MANIFEST.in added to `authorized_paths`, goal text updated.
  - `plans_internal/refactor_repo/prompts/generated/P02S_structured_data_codemod.prompt.v4.yaml` — `pyproject.toml` and `*.toml` removed from `authorized_paths`.
  These two prompt-definition edits are **not** part of this checkpoint's delta; recorded as pre-existing context per the user's second-retry framing.
- Artifact version: this report, `P01_checkpoint_report.v4.md`.

## 2. Changed / created paths — exhaustive, individual files (no directory summaries)

Every path created or modified **by this P01 execution run**, listed individually:

| # | Path | Action |
|---|---|---|
| 1 | `pyproject.toml` | pre-staged before journal start; verified/adopted unchanged; deleted and byte-exact restored during rollback verification (§4), twice |
| 2 | `MANIFEST.in` | pre-staged before journal start; verified/adopted unchanged; deleted and byte-exact restored during rollback verification (§4), twice |
| 3 | `src/curriculum_factory/__init__.py` | pre-staged before journal start; verified/adopted unchanged; deleted (with the rest of `src/`) and byte-exact restored during rollback verification (§4), twice |
| 4 | `tests/refactor_repo/test_packaging_skeleton.py` | pre-staged before journal start; verified/adopted unchanged; deleted and byte-exact restored during rollback verification (§4), twice |
| 5 | `plans_internal/refactor_repo/execution/P01/execution_log.jsonl` | created by this run |
| 6 | `plans_internal/refactor_repo/execution/P01/.execution_log.counter.json` | created by this run |
| 7 | `plans_internal/refactor_repo/execution/P01/.execution_log.lock` | created by this run |
| 8 | `plans_internal/refactor_repo/checkpoints/P01/P01_checkpoint_report.v1.md` | created; moved to `plans_internal/refactor_repo/checkpoints/P01/deprecated/P01_checkpoint_report.v1.md` after round 1 |
| 9 | `plans_internal/refactor_repo/checkpoints/P01/P01_checkpoint_report.v2.md` | created; moved to `plans_internal/refactor_repo/checkpoints/P01/deprecated/P01_checkpoint_report.v2.md` after round 2 |
| 10 | `plans_internal/refactor_repo/checkpoints/P01/P01_checkpoint_report.v3.md` | created; moved to `plans_internal/refactor_repo/checkpoints/P01/deprecated/P01_checkpoint_report.v3.md` after round 3 |
| 11 | `plans_internal/refactor_repo/checkpoints/P01/P01_checkpoint_report.v4.md` | this file, created by this run |
| 12 | `plans_internal/refactor_repo/checkpoints/P01/QA/session.json` | created/updated by the QA gate tool, not hand-written |
| 13 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.events.jsonl` | created by the QA gate tool |
| 14 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.meta.json` | created by the QA gate tool |
| 15 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.request.md` | created by the QA gate tool |
| 16 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.response.json` | created by the QA gate tool |
| 17 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.stderr.txt` | created by the QA gate tool |
| 18 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.events.jsonl` | created by the QA gate tool |
| 19 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.meta.json` | created by the QA gate tool |
| 20 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.request.md` | created by the QA gate tool |
| 21 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.response.json` | created by the QA gate tool |
| 22 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.stderr.txt` | created by the QA gate tool |
| 23 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-03.events.jsonl` | created by the QA gate tool |
| 24 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-03.meta.json` | created by the QA gate tool |
| 25 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-03.request.md` | created by the QA gate tool |
| 26 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-03.response.json` | created by the QA gate tool |
| 27 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-03.stderr.txt` | created by the QA gate tool |

Rows 12–27, and the round-04+ files this same QA session may add, are written exclusively by `qa_gate.py` (never hand-written by this execution). All rows are under the authorized `plans_internal/refactor_repo/checkpoints/P01/` prefix. Verification command: `find plans_internal/refactor_repo/checkpoints/P01 plans_internal/refactor_repo/execution/P01 -type f | sort`, `EXIT: 0`.

No file outside this list was modified by this run. Pre-existing changes to `plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml` and `plans_internal/refactor_repo/prompts/generated/P02S_structured_data_codemod.prompt.v4.yaml`, and the pre-existing untracked manifest-resolution artifacts under `plans_internal/refactor_repo/prompts/resolved/`, predate this run and are not this checkpoint's delta (full raw `git status` in §6).

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
**Material output**: `EXACT_OVERLAPS_WITH_P01: NONE` — enumerated all 12 other prompt files' (P00, P00A, P02, P02S v3, P02S v4, P03–P09) `authorized_paths` and intersected each against P01's exact four paths; zero intersections. The live P02S v4 file's `authorized_paths` contains no `*.toml` or `pyproject.toml` entry, confirming the second-retry fix holds in the file P02S actually executes under.
P03 and P04 list the broader directory prefix `src/curriculum_factory/`; this is not a live conflict because P03/P04 `depends_on` chains run strictly after P01 completes, and this checkpoint's own `test_src_curriculum_factory_package_exists_and_is_minimal` proves the directory currently contains only `__init__.py`.
The resolved manifest's stale `owns` label `pyproject_toml_identity_updates` for P02S is a documentation artifact from before the second-retry `authorized_paths` fix; P02S's actual enforcement surface (`authorized_paths`) cannot reach `pyproject.toml`. Recorded as a non-blocking residual in §5.

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

**Command** (package-data extension trace):
```
$ find runtime -type f ! -name "*.py" ! -name "*.pyc" | sed 's/.*\.//' | sort -u
```
**Exit status**: `0`
**Material output**: `json`, `md`, `mjs`, `yaml` — exactly matching the four declared `[tool.setuptools.package-data]` extensions.

`version = "0.1.0"` is not present in the inventory; recorded as a standard initial-release packaging default, not a dependency or command.

**Conclusion**: **PASS**.

### Test 3 — Package discovery is src-only and excludes repository contracts

**Commands** (build in isolated checkout A):
```
$ rsync -a --exclude='.git' --exclude='__pycache__' --exclude='node_modules' --exclude='*.pyc' /Users/filipepinto/Projects/curriculum_builder_wt/refactor-curriculum-factory-repository/ /tmp/p01_ckA/
EXIT: 0
$ python3.13 -m venv /tmp/p01_venvA
EXIT: 0
$ /tmp/p01_venvA/bin/pip install --quiet build
EXIT: 0
$ /tmp/p01_venvA/bin/python -m build --outdir /tmp/p01_distA /tmp/p01_ckA
EXIT: 0
$ tar -tzf /tmp/p01_distA/curriculum_factory-0.1.0.tar.gz | grep -E "runtime/|tests/|policy/|schemas/|curricula/|docs/|outputs/|plans/"
EXIT: 1   (no matches — clean)
$ unzip -l /tmp/p01_distA/curriculum_factory-0.1.0-py3-none-any.whl | awk '{print $4}' | grep -E "runtime/|tests/|policy/|schemas/|curricula/|docs/|outputs/|plans/"
EXIT: 1   (no matches — clean)
```
**Material output**: sdist `curriculum_factory-0.1.0.tar.gz` contains exactly `curriculum_factory-0.1.0/`, `.../MANIFEST.in`, `.../PKG-INFO`, `.../pyproject.toml`, `.../readme.md`, `.../setup.cfg`, `.../src/`, `.../src/curriculum_factory.egg-info/` (+5 files inside), `.../src/curriculum_factory/`, `.../src/curriculum_factory/__init__.py`. Wheel contains exactly 6 entries: `curriculum_factory/__init__.py` plus 5 standard `dist-info` files.

**Control build**:
```
$ rsync -a --exclude='.git' --exclude='__pycache__' --exclude='node_modules' --exclude='*.pyc' /Users/filipepinto/Projects/curriculum_builder_wt/refactor-curriculum-factory-repository/ /tmp/p01_ckC/
EXIT: 0
$ rm /tmp/p01_ckC/MANIFEST.in
EXIT: 0
$ python3.13 -m venv /tmp/p01_venvC
EXIT: 0
$ /tmp/p01_venvC/bin/pip install --quiet build
EXIT: 0
$ /tmp/p01_venvC/bin/python -m build --sdist --outdir /tmp/p01_distC /tmp/p01_ckC
EXIT: 0   (build log: "copying tests/test_validate_instance.py -> curriculum_factory-0.1.0/tests")
$ tar -tzf /tmp/p01_distC/curriculum_factory-0.1.0.tar.gz | grep tests/test_validate_instance.py
curriculum_factory-0.1.0/tests/test_validate_instance.py
EXIT: 0   (match found — proves the leak occurs without MANIFEST.in)
```

**Conclusion**: **PASS**.

### Test 4 — Distribution metadata and console entry points are explicit

**Commands**:
```
$ unzip -p /tmp/p01_distA/curriculum_factory-0.1.0-py3-none-any.whl curriculum_factory-0.1.0.dist-info/METADATA
EXIT: 0
$ tar -xzOf /tmp/p01_distA/curriculum_factory-0.1.0.tar.gz curriculum_factory-0.1.0/PKG-INFO
EXIT: 0
$ unzip -p /tmp/p01_distA/curriculum_factory-0.1.0-py3-none-any.whl curriculum_factory-0.1.0.dist-info/entry_points.txt
EXIT: 0
```
**Material output**: `METADATA` and `PKG-INFO` byte-identical: `Name: curriculum-factory`, `Version: 0.1.0`, `Requires-Python: <3.14,>=3.13`, 5 `Requires-Dist` runtime pins, `Provides-Extra: dev` + `Requires-Dist: pytest==9.0.3; extra == "dev"`. `entry_points.txt` lists all 4 console scripts matching the 4 P00-classified `module_main_guard` commands exactly. No console script was invoked; runtime invocation deferred to P03.

**Conclusion**: **PASS**.

### Test 5 — Skeleton builds reproducibly without source movement

**Commands** (checkout B):
```
$ rsync -a --exclude='.git' --exclude='__pycache__' --exclude='node_modules' --exclude='*.pyc' /Users/filipepinto/Projects/curriculum_builder_wt/refactor-curriculum-factory-repository/ /tmp/p01_ckB/
EXIT: 0
$ python3.13 -m venv /tmp/p01_venvB
EXIT: 0
$ /tmp/p01_venvB/bin/pip install --quiet build
EXIT: 0
$ /tmp/p01_venvB/bin/python -m build --outdir /tmp/p01_distB /tmp/p01_ckB
EXIT: 0
$ diff <(tar -tzf /tmp/p01_distA/curriculum_factory-0.1.0.tar.gz | sort) <(tar -tzf /tmp/p01_distB/curriculum_factory-0.1.0.tar.gz | sort)
EXIT: 0
$ diff <(unzip -l /tmp/p01_distA/curriculum_factory-0.1.0-py3-none-any.whl | awk '{print $4}' | sort) <(unzip -l /tmp/p01_distB/curriculum_factory-0.1.0-py3-none-any.whl | awk '{print $4}' | sort)
EXIT: 0
$ tar -xzf /tmp/p01_distA/curriculum_factory-0.1.0.tar.gz -C /tmp/p01_extractA
EXIT: 0
$ tar -xzf /tmp/p01_distB/curriculum_factory-0.1.0.tar.gz -C /tmp/p01_extractB
EXIT: 0
$ unzip -q /tmp/p01_distA/curriculum_factory-0.1.0-py3-none-any.whl -d /tmp/p01_wheelA
EXIT: 0
$ unzip -q /tmp/p01_distB/curriculum_factory-0.1.0-py3-none-any.whl -d /tmp/p01_wheelB
EXIT: 0
$ diff -rq /tmp/p01_extractA /tmp/p01_extractB
EXIT: 0
$ diff -rq /tmp/p01_wheelA /tmp/p01_wheelB
EXIT: 0
$ diff <(find /tmp/p01_extractA -type f | sort | xargs shasum -a 256 | sed 's#/tmp/p01_extractA/##') <(find /tmp/p01_extractB -type f | sort | xargs shasum -a 256 | sed 's#/tmp/p01_extractB/##')
EXIT: 0
$ diff -rq --exclude=__pycache__ /Users/filipepinto/Projects/curriculum_builder_wt/refactor-curriculum-factory-repository/runtime /tmp/p01_ckA/runtime
EXIT: 0
$ diff -rq --exclude=__pycache__ /Users/filipepinto/Projects/curriculum_builder_wt/refactor-curriculum-factory-repository/runtime /tmp/p01_ckB/runtime
EXIT: 0
```
**Material output**: both builds exit 0; sdist/wheel file lists identical between A and B; recursive content diff of extracted sdist and wheel trees empty; per-file SHA-256 of all 12 extracted sdist files identical between A and B; `runtime/` byte-identical between the live repository and both isolated checkouts. Raw archive-level SHA-256 of the container files differ (expected: embedded build timestamps); the extracted-content and per-file digest comparisons above are the normalized comparison the test calls for.

**Conclusion**: **PASS**.

## 4. Prerequisites, non-targets, stop conditions, rollback — executed and verified, fully literal commands

- P00/P00A prerequisite evidence: present, witnessed QA_PASSED, not stale.
- Non-targets honored: no file under `runtime/` moved, no import rewritten, no resource loader repaired, no test renamed, no schema identifier changed, no installed behavioral parity claimed.
- No successor prompt's mutation authority borrowed (§ Test 1).
- **Rollback procedure — executed three times across this checkpoint (round 1 evidence gathering, round 2's literal re-run, and once more identically), all with identical results.** Most recent execution, exact commands:
  ```
  $ cp pyproject.toml /tmp/p01_rollback_v2/pyproject.toml
  EXIT: 0
  $ cp MANIFEST.in /tmp/p01_rollback_v2/MANIFEST.in
  EXIT: 0
  $ cp tests/refactor_repo/test_packaging_skeleton.py /tmp/p01_rollback_v2/test_packaging_skeleton.py
  EXIT: 0
  $ cp src/curriculum_factory/__init__.py /tmp/p01_rollback_v2/__init__.py
  EXIT: 0
  $ rm -f pyproject.toml MANIFEST.in tests/refactor_repo/test_packaging_skeleton.py
  EXIT: 0
  $ rm -rf src
  EXIT: 0
  $ python3 -m pytest tests/refactor_repo/test_inventory.py -q
  ................                                                         [100%]
  16 passed in 44.29s
  EXIT: 0
  $ cp /tmp/p01_rollback_v2/pyproject.toml pyproject.toml
  EXIT: 0
  $ cp /tmp/p01_rollback_v2/MANIFEST.in MANIFEST.in
  EXIT: 0
  $ mkdir -p src/curriculum_factory
  EXIT: 0
  $ cp /tmp/p01_rollback_v2/__init__.py src/curriculum_factory/__init__.py
  EXIT: 0
  $ cp /tmp/p01_rollback_v2/test_packaging_skeleton.py tests/refactor_repo/test_packaging_skeleton.py
  EXIT: 0
  $ shasum -a 256 pyproject.toml MANIFEST.in src/curriculum_factory/__init__.py tests/refactor_repo/test_packaging_skeleton.py
  b1f0a1837563edf6219806f4e34cb0be9d1985060ddd17ee238dc5a484c7b820  pyproject.toml
  36ebe4327048aae325d514661111a83fed32085957ae00515fde0c99638ce79a  MANIFEST.in
  373ca38365f43cb6cc6d90767f48c61a7b2ab38a8693094d2f32a7deafe12404  src/curriculum_factory/__init__.py
  0ea463de2c5a2d5675196b62015e511f0cc5ff456226cb82eb198f4586d1e9b7  tests/refactor_repo/test_packaging_skeleton.py
  EXIT: 0
  $ python3 -m pytest tests/refactor_repo/test_packaging_skeleton.py -q
  .............                                                            [100%]
  13 passed in 0.02s
  EXIT: 0
  ```
  After deleting all four P01 deliverables, the P00 inventory reproducibility test suite passed unchanged against the reverted tree (16/16, exit 0). All four files were restored and their SHA-256 digests are the exact four values shown above, matching the digests recorded in §6 exactly. The local packaging test suite re-passed (13/13, exit 0) after restoration.

## 5. Residuals

- Stale `owns` label `pyproject_toml_identity_updates` under P02S in `prompt_manifest.resolved.v1.yaml`: **recorded exception**, unreachable given P02S v4's corrected `authorized_paths`, out of P01's authorization to edit. Recommend a manifest-owning process regenerate this label in a future pass; does not affect this checkpoint's correctness.
- No other residual old identities, paths, imports, output consumers, or schema references are within P01's scope.

## 6. Post-change git status — captured after this v4 file was written to disk

```
$ git status --short --untracked-files=all
 M plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml
 M plans_internal/refactor_repo/prompts/generated/P02S_structured_data_codemod.prompt.v4.yaml
?? MANIFEST.in
?? plans_internal/refactor_repo/checkpoints/P01/P01_checkpoint_report.v3.md
?? plans_internal/refactor_repo/checkpoints/P01/P01_checkpoint_report.v4.md
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.events.jsonl
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.meta.json
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.request.md
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.response.json
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.stderr.txt
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.events.jsonl
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.meta.json
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.request.md
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.response.json
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.stderr.txt
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-03.events.jsonl
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-03.meta.json
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-03.request.md
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-03.response.json
?? plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-03.stderr.txt
?? plans_internal/refactor_repo/checkpoints/P01/QA/session.json
?? plans_internal/refactor_repo/checkpoints/P01/deprecated/P01_checkpoint_report.v1.md
?? plans_internal/refactor_repo/checkpoints/P01/deprecated/P01_checkpoint_report.v2.md
?? plans_internal/refactor_repo/execution/P01/.execution_log.counter.json
?? plans_internal/refactor_repo/execution/P01/.execution_log.lock
?? plans_internal/refactor_repo/execution/P01/execution_log.jsonl
?? plans_internal/refactor_repo/prompts/resolved/deprecated/prompt_manifest.resolved.v1.yaml
?? plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1_modified.yaml
?? plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v2.yaml
?? pyproject.toml
?? src/curriculum_factory/__init__.py
?? tests/refactor_repo/test_packaging_skeleton.py
```
`EXIT: 0`. Captured after `P01_checkpoint_report.v4.md` was written to disk and before this round's submission to `qa_gate.py`, so it shows v4 present at its active path and v3 still at its pre-move path (the QA tool moves the previous version into `deprecated/` only as a side effect of accepting the next `round` submission, which necessarily happens after this status was captured). `deprecated/P01_checkpoint_report.v1.md` and `deprecated/P01_checkpoint_report.v2.md` are already present from rounds 1 and 2's moves. Both `M` lines and the three untracked files under `plans_internal/refactor_repo/prompts/resolved/` predate this run's journal (see §1/§2) and are not this checkpoint's delta.

**Deliverable digests (SHA-256)**:
| File | SHA-256 |
|---|---|
| `pyproject.toml` | `b1f0a1837563edf6219806f4e34cb0be9d1985060ddd17ee238dc5a484c7b820` |
| `MANIFEST.in` | `36ebe4327048aae325d514661111a83fed32085957ae00515fde0c99638ce79a` |
| `src/curriculum_factory/__init__.py` | `373ca38365f43cb6cc6d90767f48c61a7b2ab38a8693094d2f32a7deafe12404` |
| `tests/refactor_repo/test_packaging_skeleton.py` | `0ea463de2c5a2d5675196b62015e511f0cc5ff456226cb82eb198f4586d1e9b7` |
| `deprecated/P01_checkpoint_report.v1.md` | `8114e92e7575696e91ab91b30540224840c7daa841b10d0181a94396d07e4c13` |
| `deprecated/P01_checkpoint_report.v2.md` | `5e0562806d79a32504137d3e5a403f205be134a90708c1b592a1958fd71e142e` |

`.execution_log.counter.json` and `.execution_log.lock` are logger-internal bookkeeping files with no independent content meaning to digest. `execution_log.jsonl` is append-only and growing with this very round; the completion-gate-relevant invariant is zero unclosed starts at final audit (§7), reproducible at any time with `ExecutionLogger.audit()`, not a frozen digest.

Rollback checkpoint verification result: **executed three times, identically, and verified**, evidence in §4.

## 7. Completion status

Local test suite: `pytest tests/refactor_repo/test_packaging_skeleton.py -q` → **13 passed**, run five times across this checkpoint with identical results each time.
Execution journal: `plans_internal/refactor_repo/execution/P01/execution_log.jsonl`; reproducible with `ExecutionLogger.audit()`, which must report `unclosed_starts: []` for this checkpoint to be complete.
Tests 1–5 above: all **PASS**, each with an exact, copy-paste-reproducible command, exit status, and material output recorded.
QA round 1 on v1 returned 3 blockers. Round 2 on v2 resolved the rollback finding, returned 2 narrower blockers. Round 3 on v3 resolved the command-literalness and path-inventory findings, returned 1 remaining blocker (P01-QA-003: the git status snapshot in v3 predated v3's own existence on disk). This v4 fixes that by capturing git status after v4 was written (§6), before submission to the QA tool. This v4 report does not itself claim Test 6's outcome; the gate's own `verify` output is the sole authority for that.
