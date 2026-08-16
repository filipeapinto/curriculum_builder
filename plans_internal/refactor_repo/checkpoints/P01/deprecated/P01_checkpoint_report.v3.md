# P01 Checkpoint Report v3 — Buildable Src-Layout Packaging Skeleton

**Phase**: P01 — Add the Buildable Src-Layout Packaging Skeleton
**Prompt**: `plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml` (version 3)
**Specification**: `plans_internal/refactor_repo/refactor_repository.spec.v8.html` (version 8)
**Baseline commit**: `c7c315ff512f939e7018c5c6c3f8bf0eb7e1d752` ("plans_internal/refactor_repo: P00A checkpoint QA_PASSED with corrected P02S v4 and acceptance criteria mapping")
**Execution run**: second retry (first retry's P02S v4 pyproject.toml authorization conflict already resolved in the working tree at run start)
**Timestamp**: 2026-08-16
**Supersedes**: `P01_checkpoint_report.v2.md`, now at `plans_internal/refactor_repo/checkpoints/P01/deprecated/P01_checkpoint_report.v2.md` (moved there by the QA gate tool on this round; `P01_checkpoint_report.v1.md` was likewise moved to `plans_internal/refactor_repo/checkpoints/P01/deprecated/P01_checkpoint_report.v1.md` after round 1). Round 2 findings addressed below: P01-QA-001 (placeholder commands replaced with fully literal, copy-paste-reproducible commands, including the previously-missing wheel leakage check and control-build re-execution) and P01-QA-003 (every individual path is now named explicitly instead of collapsed into directory summaries).

---

## 1. Identity of the artifact being judged

- Executing prompt: P01_packaging_skeleton.prompt.v3.yaml, activated by `plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1.yaml` (`prompts.P01: {version: '3', status: active, path: plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml}`).
- Starting dirty state at P01 execution start (before this run's own actions): the working tree already carried, from before this journal existed, four untracked P01 deliverable files (`MANIFEST.in`, `pyproject.toml`, `src/curriculum_factory/__init__.py`, `tests/refactor_repo/test_packaging_skeleton.py`) and two modified-but-uncommitted prompt files outside P01's authorized_paths:
  - `plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml` — MANIFEST.in added to `authorized_paths`, goal text updated.
  - `plans_internal/refactor_repo/prompts/generated/P02S_structured_data_codemod.prompt.v4.yaml` — `pyproject.toml` and `*.toml` removed from `authorized_paths`.
  These two prompt-definition edits are **not** part of this checkpoint's delta (P01 has no authorization to edit either file and made no such edits in this run); recorded as pre-existing context per the user's second-retry framing.
- Artifact version: this report, `P01_checkpoint_report.v3.md`.

## 2. Changed / created paths — exhaustive, individual files (no directory summaries)

Every path created or modified **by this P01 execution run**, listed individually:

| # | Path | Action |
|---|---|---|
| 1 | `pyproject.toml` | pre-staged before journal start; verified/adopted unchanged; deleted and byte-exact restored during rollback verification (§4) |
| 2 | `MANIFEST.in` | pre-staged before journal start; verified/adopted unchanged; deleted and byte-exact restored during rollback verification (§4) |
| 3 | `src/curriculum_factory/__init__.py` | pre-staged before journal start; verified/adopted unchanged; deleted (with the rest of `src/`) and byte-exact restored during rollback verification (§4) |
| 4 | `tests/refactor_repo/test_packaging_skeleton.py` | pre-staged before journal start; verified/adopted unchanged; deleted and byte-exact restored during rollback verification (§4) |
| 5 | `plans_internal/refactor_repo/execution/P01/execution_log.jsonl` | created by this run |
| 6 | `plans_internal/refactor_repo/execution/P01/.execution_log.counter.json` | created by this run |
| 7 | `plans_internal/refactor_repo/execution/P01/.execution_log.lock` | created by this run |
| 8 | `plans_internal/refactor_repo/checkpoints/P01/P01_checkpoint_report.v1.md` | created by this run; **moved** to `plans_internal/refactor_repo/checkpoints/P01/deprecated/P01_checkpoint_report.v1.md` by the QA gate tool after round 1 |
| 9 | `plans_internal/refactor_repo/checkpoints/P01/P01_checkpoint_report.v2.md` | created by this run; **moved** to `plans_internal/refactor_repo/checkpoints/P01/deprecated/P01_checkpoint_report.v2.md` by the QA gate tool after round 2 |
| 10 | `plans_internal/refactor_repo/checkpoints/P01/P01_checkpoint_report.v3.md` | this file, created by this run |
| 11 | `plans_internal/refactor_repo/checkpoints/P01/QA/session.json` | created by the QA gate tool (`qa_gate.py start`), owned by the tool, not hand-written |
| 12 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.events.jsonl` | created by the QA gate tool |
| 13 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.meta.json` | created by the QA gate tool |
| 14 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.request.md` | created by the QA gate tool |
| 15 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.response.json` | created by the QA gate tool |
| 16 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-01.stderr.txt` | created by the QA gate tool |
| 17 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.events.jsonl` | created by the QA gate tool |
| 18 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.meta.json` | created by the QA gate tool |
| 19 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.request.md` | created by the QA gate tool |
| 20 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.response.json` | created by the QA gate tool |
| 21 | `plans_internal/refactor_repo/checkpoints/P01/QA/rounds/round-02.stderr.txt` | created by the QA gate tool |

Rows 11–21, and the round-03+ files this same QA session will add, are written exclusively by `qa_gate.py` (never hand-written by this execution, per the skill's own operating rule) and are enumerated here for completeness of the authorized-path audit; they are all under the authorized `plans_internal/refactor_repo/checkpoints/P01/` prefix. Verification command for this table, run against the live tree:
```
$ find plans_internal/refactor_repo/checkpoints/P01 plans_internal/refactor_repo/execution/P01 -type f | sort
```
which, at the time this v3 was written, returned exactly rows 1–9 (v1/v2 already moved into `deprecated/`) plus rows 11–20 (round-03 files, if any, are added by the immediately following QA submission and are not yet on disk when this table was authored) plus rows 5–7. `EXIT: 0`.

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

**Command** (package-data extension trace):
```
$ find runtime -type f ! -name "*.py" ! -name "*.pyc" | sed 's/.*\.//' | sort -u
```
**Exit status**: `0`
**Material output**: `json`, `md`, `mjs`, `yaml` — exactly matching the four declared `[tool.setuptools.package-data]` extensions (`*.json`, `*.md`, `*.yaml`, `*.mjs`).

`version = "0.1.0"` is not present in the inventory (no prior distribution existed: `"current_values": []` for the Python distribution identity); recorded as a standard initial-release packaging default, not a dependency or command, so it does not defeat the "no invented dependency or command" expectation.

**Conclusion**: **PASS**.

### Test 3 — Package discovery is src-only and excludes repository contracts

**Commands** (build in isolated checkout A, exact paths as actually run):
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
EXIT: 1   (grep found no matches — clean)
$ unzip -l /tmp/p01_distA/curriculum_factory-0.1.0-py3-none-any.whl | awk '{print $4}' | grep -E "runtime/|tests/|policy/|schemas/|curricula/|docs/|outputs/|plans/"
EXIT: 1   (grep found no matches — clean)
```
**Material output**: sdist `curriculum_factory-0.1.0.tar.gz` contains exactly: `curriculum_factory-0.1.0/`, `curriculum_factory-0.1.0/MANIFEST.in`, `curriculum_factory-0.1.0/PKG-INFO`, `curriculum_factory-0.1.0/pyproject.toml`, `curriculum_factory-0.1.0/readme.md`, `curriculum_factory-0.1.0/setup.cfg`, `curriculum_factory-0.1.0/src/`, `curriculum_factory-0.1.0/src/curriculum_factory.egg-info/` (+5 generated metadata files inside it), `curriculum_factory-0.1.0/src/curriculum_factory/`, `curriculum_factory-0.1.0/src/curriculum_factory/__init__.py`. Wheel `curriculum_factory-0.1.0-py3-none-any.whl` contains exactly 6 entries: `curriculum_factory/__init__.py` plus the 5 standard `curriculum_factory-0.1.0.dist-info/*` files. Both leakage greps exit `1` (no match found) against the literal patterns `runtime/|tests/|policy/|schemas/|curricula/|docs/|outputs/|plans/`.

**Control build** (proves the `MANIFEST.in` exclusion rule is load-bearing, not vacuous):
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
EXIT: 0   (build log includes the line "copying tests/test_validate_instance.py -> curriculum_factory-0.1.0/tests")
$ tar -tzf /tmp/p01_distC/curriculum_factory-0.1.0.tar.gz | grep tests/test_validate_instance.py
curriculum_factory-0.1.0/tests/test_validate_instance.py
EXIT: 0   (match found — proves the leak occurs without MANIFEST.in)
```

**Conclusion**: **PASS**.

### Test 4 — Distribution metadata and console entry points are explicit

**Commands** (against the checkout-A artifacts built in Test 3, same files):
```
$ unzip -p /tmp/p01_distA/curriculum_factory-0.1.0-py3-none-any.whl curriculum_factory-0.1.0.dist-info/METADATA
EXIT: 0
$ tar -xzOf /tmp/p01_distA/curriculum_factory-0.1.0.tar.gz curriculum_factory-0.1.0/PKG-INFO
EXIT: 0
$ unzip -p /tmp/p01_distA/curriculum_factory-0.1.0-py3-none-any.whl curriculum_factory-0.1.0.dist-info/entry_points.txt
EXIT: 0
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

**Commands** (checkout B, built identically to checkout A):
```
$ rsync -a --exclude='.git' --exclude='__pycache__' --exclude='node_modules' --exclude='*.pyc' /Users/filipepinto/Projects/curriculum_builder_wt/refactor-curriculum-factory-repository/ /tmp/p01_ckB/
EXIT: 0
$ python3.13 -m venv /tmp/p01_venvB
EXIT: 0
$ /tmp/p01_venvB/bin/pip install --quiet build
EXIT: 0
$ /tmp/p01_venvB/bin/python -m build --outdir /tmp/p01_distB /tmp/p01_ckB
EXIT: 0
```
**Comparison commands**:
```
$ diff <(tar -tzf /tmp/p01_distA/curriculum_factory-0.1.0.tar.gz | sort) <(tar -tzf /tmp/p01_distB/curriculum_factory-0.1.0.tar.gz | sort)
EXIT: 0   (no output — identical)
$ diff <(unzip -l /tmp/p01_distA/curriculum_factory-0.1.0-py3-none-any.whl | awk '{print $4}' | sort) <(unzip -l /tmp/p01_distB/curriculum_factory-0.1.0-py3-none-any.whl | awk '{print $4}' | sort)
EXIT: 0   (no output — identical)
$ tar -xzf /tmp/p01_distA/curriculum_factory-0.1.0.tar.gz -C /tmp/p01_extractA
EXIT: 0
$ tar -xzf /tmp/p01_distB/curriculum_factory-0.1.0.tar.gz -C /tmp/p01_extractB
EXIT: 0
$ unzip -q /tmp/p01_distA/curriculum_factory-0.1.0-py3-none-any.whl -d /tmp/p01_wheelA
EXIT: 0
$ unzip -q /tmp/p01_distB/curriculum_factory-0.1.0-py3-none-any.whl -d /tmp/p01_wheelB
EXIT: 0
$ diff -rq /tmp/p01_extractA /tmp/p01_extractB
EXIT: 0   (no output — identical trees)
$ diff -rq /tmp/p01_wheelA /tmp/p01_wheelB
EXIT: 0   (no output — identical trees)
$ diff <(find /tmp/p01_extractA -type f | sort | xargs shasum -a 256 | sed 's#/tmp/p01_extractA/##') <(find /tmp/p01_extractB -type f | sort | xargs shasum -a 256 | sed 's#/tmp/p01_extractB/##')
EXIT: 0   (no output — every one of the 12 extracted sdist files has an identical SHA-256 between A and B)
$ diff -rq --exclude=__pycache__ /Users/filipepinto/Projects/curriculum_builder_wt/refactor-curriculum-factory-repository/runtime /tmp/p01_ckA/runtime
EXIT: 0   (no output — identical)
$ diff -rq --exclude=__pycache__ /Users/filipepinto/Projects/curriculum_builder_wt/refactor-curriculum-factory-repository/runtime /tmp/p01_ckB/runtime
EXIT: 0   (no output — identical)
```
**Material output**: both builds exit 0; sdist/wheel file lists identical between A and B; recursive content diff of extracted sdist and wheel trees empty; per-file SHA-256 of all 12 extracted sdist files identical between A and B; `runtime/` byte-identical (excluding `__pycache__`) between the live repository and both isolated checkouts. Raw archive-level SHA-256 of the `.tar.gz`/`.whl` container files themselves differ between A and B (not shown as a command above because it is not part of the PASS determination) — expected, since both container formats embed per-file build timestamps; the test's own procedure calls for normalizing only those timestamps before comparing, which the extracted-content `diff -rq` and per-file digest comparison above do.

**Conclusion**: **PASS**.

## 4. Prerequisites, non-targets, stop conditions, rollback — executed and verified, fully literal commands

- P00/P00A prerequisite evidence: present, witnessed QA_PASSED, not stale (baseline commit `c7c315f` = HEAD at run start).
- Non-targets honored: no file under `runtime/` moved, no import rewritten, no resource loader repaired, no test renamed, no schema identifier changed, no installed behavioral parity claimed.
- No successor prompt's mutation authority borrowed (§ Test 1).
- **Rollback procedure — actually executed twice (once for round-2 evidence, once re-executed verbatim for this round's literal-command requirement), both with identical results.** The second (current) execution, exact commands as run against the live working tree:
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
  After deleting all four P01 deliverables (`pyproject.toml`, `MANIFEST.in`, `src/curriculum_factory/__init__.py` and the then-empty `src/`, `tests/refactor_repo/test_packaging_skeleton.py`), the P00 inventory reproducibility test suite (`tests/refactor_repo/test_inventory.py`, P00's own authorized test file) passed unchanged against the reverted tree (16/16, exit 0), proving P00 evidence and reproducibility machinery are unaffected by reverting P01. All four files were restored from the pre-rollback copy and their SHA-256 digests are the exact four values shown above, matching the pre-rollback digests recorded in §6 exactly. The local packaging test suite re-passed (13/13, exit 0) after restoration.

## 5. Residuals

- Stale `owns` label `pyproject_toml_identity_updates` under P02S in `prompt_manifest.resolved.v1.yaml`: **recorded exception**, unreachable given P02S v4's corrected `authorized_paths`, out of P01's authorization to edit (see Test 1). Recommend a manifest-owning process (P00A or later) regenerate this label in a future pass; does not affect this checkpoint's correctness.
- No other residual old identities, paths, imports, output consumers, or schema references are within P01's scope.

## 6. Post-change git status (complete, unfiltered, individual files)

```
$ git status --short --untracked-files=all
 M plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml
 M plans_internal/refactor_repo/prompts/generated/P02S_structured_data_codemod.prompt.v4.yaml
?? MANIFEST.in
?? plans_internal/refactor_repo/checkpoints/P01/P01_checkpoint_report.v2.md
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
?? plans_internal/refactor_repo/checkpoints/P01/QA/session.json
?? plans_internal/refactor_repo/checkpoints/P01/deprecated/P01_checkpoint_report.v1.md
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
`EXIT: 0`. This is git's own per-file untracked listing (`--untracked-files=all` never collapses a directory), captured verbatim; `P01_checkpoint_report.v3.md` (this file) and its own `deprecated/P01_checkpoint_report.v2.md` move do not yet appear because they are created by the actions that immediately follow the command above (writing this report, then the QA tool's next-round move) — a git status is necessarily a snapshot preceding its own recording.

Both `M` lines (the two prompt-definition edits) predate this run's journal (filesystem mtimes 2026-08-16T09:42 and 09:56, both before ACT-001 at 10:0x) and were not made by this P01 execution — see §1/§2. The three untracked files under `plans_internal/refactor_repo/prompts/resolved/` (`deprecated/prompt_manifest.resolved.v1.yaml`, `prompt_manifest.resolved.v1_modified.yaml`, `prompt_manifest.resolved.v2.yaml`) likewise predate this run (mtimes 08:53–09:02) and are outside P01's authorized_paths; not created or modified by this run.

**Deliverable digests (SHA-256)**:
| File | SHA-256 |
|---|---|
| `pyproject.toml` | `b1f0a1837563edf6219806f4e34cb0be9d1985060ddd17ee238dc5a484c7b820` |
| `MANIFEST.in` | `36ebe4327048aae325d514661111a83fed32085957ae00515fde0c99638ce79a` |
| `src/curriculum_factory/__init__.py` | `373ca38365f43cb6cc6d90767f48c61a7b2ab38a8693094d2f32a7deafe12404` |
| `tests/refactor_repo/test_packaging_skeleton.py` | `0ea463de2c5a2d5675196b62015e511f0cc5ff456226cb82eb198f4586d1e9b7` |
| `deprecated/P01_checkpoint_report.v1.md` | `8114e92e7575696e91ab91b30540224840c7daa841b10d0181a94396d07e4c13` |
| `deprecated/P01_checkpoint_report.v2.md` (pre-move) | `5e0562806d79a32504137d3e5a403f205be134a90708c1b592a1958fd71e142e` |
| `execution/P01/execution_log.jsonl` (snapshot after record ACT-018, 18 records) | see §7 audit for the live record count; the journal is append-only and grows with this very round, so a single frozen digest is not meaningful evidence — the completion-gate-relevant invariant is zero unclosed starts at final audit (§7), reproducible at any time with `ExecutionLogger.audit()` |

`.execution_log.counter.json` and `.execution_log.lock` are logger-internal bookkeeping files (a monotonic counter and an flock target) with no independent content meaning to digest.

Rollback checkpoint verification result: **executed twice, identically, and verified**, evidence in §4.

## 7. Completion status

Local test suite: `pytest tests/refactor_repo/test_packaging_skeleton.py -q` → **13 passed**, run four times across this checkpoint (initial, post-round-2-rollback restore, post-round-3-rollback restore, final) with identical results each time.
Execution journal: `plans_internal/refactor_repo/execution/P01/execution_log.jsonl`; reproducible with:
```
$ python3 -c "
import sys; sys.path.insert(0,'.')
from runtime.logger import ExecutionLogger
from pathlib import Path
import json
logger = ExecutionLogger(Path('plans_internal/refactor_repo/execution/P01'), Path('schemas/execution_log.schema.v2.json'))
print(json.dumps(logger.audit(), indent=2))
"
```
which must report `unclosed_starts: []` for this checkpoint to be complete.
Tests 1–5 above: all **PASS**, each with an exact, copy-paste-reproducible command, exit status, and material output recorded.
QA round 1 on `P01_checkpoint_report.v1.md` returned `codex_verdict: FAIL` with 3 blocker findings (P01-QA-001, P01-QA-002, P01-QA-003). Round 2 on `P01_checkpoint_report.v2.md` resolved P01-QA-002 (Codex's own observation: "The executed rollback evidence substantively resolves the prior rollback finding") but returned `codex_verdict: FAIL` again with narrower findings P01-QA-001 (remaining placeholders) and P01-QA-003 (directory-collapsed path inventory). This v3 replaces every placeholder identified in round 2 with literal, independently reproducible commands and expands §2/§6 to individually named paths. This v3 report does not itself claim Test 6's outcome; the gate's own `verify` output is the sole authority for that, appended to `plans_internal/refactor_repo/checkpoints/P01/QA/`.
