# P01 Checkpoint Report v1 — Buildable Src-Layout Packaging Skeleton

**Phase**: P01 — Add the Buildable Src-Layout Packaging Skeleton
**Prompt**: `plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml` (version 3)
**Specification**: `plans_internal/refactor_repo/refactor_repository.spec.v8.html` (version 8)
**Baseline commit**: `c7c315ff512f939e7018c5c6c3f8bf0eb7e1d752` ("plans_internal/refactor_repo: P00A checkpoint QA_PASSED with corrected P02S v4 and acceptance criteria mapping")
**Execution run**: second retry (first retry's P02S v4 pyproject.toml authorization conflict already resolved in the working tree at run start)
**Timestamp**: 2026-08-16

---

## 1. Identity of the artifact being judged

- Executing prompt: P01_packaging_skeleton.prompt.v3.yaml, activated by `plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1.yaml` (`prompts.P01.status: active`, `version: '3'`, `path` matches exactly, `depends_on: [P00A]`).
- Starting dirty state at P01 execution start (before this run's own actions): the working tree already carried, from before this journal existed, four untracked P01 deliverable files (`MANIFEST.in`, `pyproject.toml`, `src/curriculum_factory/__init__.py`, `tests/refactor_repo/test_packaging_skeleton.py`) and two modified-but-uncommitted prompt files outside P01's authorized_paths:
  - `plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml` — MANIFEST.in added to `authorized_paths` and goal text updated to mention MANIFEST.in and sdist exclusion ownership.
  - `plans_internal/refactor_repo/prompts/generated/P02S_structured_data_codemod.prompt.v4.yaml` — `pyproject.toml` and `*.toml` removed from `authorized_paths`.
  These two prompt-definition edits are **not** part of this checkpoint's delta (P01 has no authorization to edit either file and made no such edits in this run); they are recorded here only as pre-existing context per the user's second-retry framing ("P02S v4's pyproject.toml conflict is now resolved (removed from authorized_paths)").
- Artifact version: this report, `P01_checkpoint_report.v1.md`.

## 2. Changed / created paths and authorization boundary

All paths created or modified **by this P01 execution run** (verified against `git status --short --untracked-files=all` filtered to this run's journal window):

| Path | Action | Within P01 authorized_paths? |
|---|---|---|
| `pyproject.toml` | pre-staged before journal start, verified/adopted unchanged in this run | yes (exact) |
| `MANIFEST.in` | pre-staged before journal start, verified/adopted unchanged in this run | yes (exact) |
| `src/curriculum_factory/__init__.py` | pre-staged before journal start, verified/adopted unchanged in this run | yes (exact) |
| `tests/refactor_repo/test_packaging_skeleton.py` | pre-staged before journal start, verified/adopted unchanged in this run | yes (exact) |
| `plans_internal/refactor_repo/execution/P01/execution_log.jsonl` | created by this run | yes (exact) |
| `plans_internal/refactor_repo/execution/P01/.execution_log.counter.json` | created by this run | yes (exact) |
| `plans_internal/refactor_repo/execution/P01/.execution_log.lock` | created by this run | yes (exact) |
| `plans_internal/refactor_repo/checkpoints/P01/` | created by this run | yes (prefix) |

No file outside this list was modified by this run. `runtime/` is verified byte-identical to the working tree in two independent isolated checkouts (see Test 5 below). Pre-existing user/prior-run changes outside this list (the two prompt-definition edits noted in §1, and unrelated P00/P00A/manifest-resolution artifacts from earlier phases) remain byte-for-byte outside this checkpoint's delta — this run neither created nor altered them.

## 3. Prompt tests

### Test 1 — Resolved manifest grants exact non-overlapping mutation ownership

**Procedure**: Loaded `prompts/resolved/prompt_manifest.resolved.v1.yaml`; confirmed it activates P01 v3 (`prompts.P01: {version: '3', path: plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml, status: active, owns: [packaging_skeleton_structure]}`). Enumerated every other prompt's `authorized_paths` (P00, P00A, P02, P02S v3 and v4, P03–P09) and compared against P01's four exact authorized_paths (`pyproject.toml`, `MANIFEST.in`, `src/curriculum_factory/__init__.py`, `tests/refactor_repo/test_packaging_skeleton.py`).

**Findings**:
- No other active prompt's `authorized_paths` lists `pyproject.toml`, `MANIFEST.in`, or `tests/refactor_repo/test_packaging_skeleton.py`. In particular, the live P02S v4 prompt (`generated/P02S_structured_data_codemod.prompt.v4.yaml`) no longer authorizes `pyproject.toml` or `*.toml` — the second-retry fix referenced in this run's brief is confirmed present in the file P02S actually executes under.
- P03 (`src/curriculum_factory/`) and P04 (`src/curriculum_factory/`) list a broader directory prefix that will, after P01 completes, contain `__init__.py`. This is expected phased-scaffolding structure, not a live conflict: P03/P04 `depends_on` chains run strictly after P01 (P03 depends_on P02S depends_on P02 depends_on P01), they are not concurrently active mutators of the same file in this checkpoint, and P01's own test suite (`test_src_curriculum_factory_package_exists_and_is_minimal`) proves the directory contains *only* `__init__.py` at this checkpoint — nothing P03/P04 would later add exists yet, so no unit is actually shared at this point in time.
- The resolved manifest's `owns` label for P02S (`pyproject_toml_identity_updates`) is stale text left over from the v4 authorization surface prior to the second-retry fix; it does not correspond to any concrete file P02S can currently reach, since P02S v4's actual `authorized_paths` (the enforcement mechanism) no longer include any path matching `pyproject.toml`. Expanding P02S's selector set against its true authorized_paths yields no unit inside `pyproject.toml`. This label mismatch is a documentation staleness in `prompt_manifest.resolved.v1.yaml`, out of P01's authorized_paths to correct, and is recorded here as a non-blocking observation rather than silently ignored (see §5).

**Verdict**: **PASS** — every intended and actual P01 mutation unit (pyproject.toml key ownership, MANIFEST.in exclusion ownership, the skeleton file, the focused test file) is owned by P01 exactly once; no live authorized-path conflict exists with any other currently-active prompt.

### Test 2 — P00 prerequisite and metadata provenance are satisfied

**Procedure**: Verified P00 and P00A witnessed QA verdicts, then traced every pyproject.toml value to inventory evidence.

**Findings**:
- P00: repaired checkpoint (`P00_checkpoint_repaired.v2.json`) witnessed **QA_PASSED** — `plans_internal/refactor_repo/checkpoints/P00/QA_repaired/rounds/round-02.response.json` verdict `"PASS"`, committed at `93c07ba`.
- P00A: checkpoint v9 witnessed **QA_PASSED** — `plans_internal/refactor_repo/checkpoints/P00A/QA/rounds/round-05.response.json` verdict `"PASS"`, committed at `c7c315f`.
- Canonical inventory: `plans_internal/refactor_repo/inventory/repair_20260816_120500/repository_refactor_inventory.20260816T122829Z.v1.json` (referenced by the P00 final checkpoint's baseline output path).
- `project.name = "curriculum-factory"` ← `identities[]` entry `"identity": "Python distribution", "target_value": "curriculum-factory"`.
- Package name `curriculum_factory` (src layout root) ← `identities[]` entry `"identity": "Python package", "target_value": "curriculum_factory"` and `"identity": "Source root", "target_value": "src/curriculum_factory/"`.
- `requires-python = ">=3.13,<3.14"` ← verbatim from `requirements/plan26.in` header comment ("Python is pinned to >=3.13,<3.14 for Plan 26 reproducibility").
- `dependencies` (5 entries: langgraph==1.2.9, langgraph-checkpoint-sqlite==3.1.0, jsonschema==4.26.0, PyYAML==6.0.3, Pillow==12.2.0) ← verbatim, set-equal to the "core runtime" + "existing runtime stack, made explicit" sections of `requirements/plan26.in`.
- `optional-dependencies.dev = ["pytest==9.0.3"]` ← verbatim from the "development only" section of `requirements/plan26.in`.
- `description` ← verbatim first paragraph of `readme.md`.
- Four `[project.scripts]` console entries ← verbatim from `python_surface.entry_points` (all `kind: module_main_guard`): `runtime/run_curriculum.py`, `runtime/session_bridge.py`, `runtime/capability_cycle.py`, `runtime/finalize_evidence.py`, each independently confirmed to contain a `def main(...)` and an `if __name__ == "__main__":` guard. The `curriculum-factory-<name>` script-name convention and the `curriculum_factory.<name>:main` target convention are P01 packaging judgment applied uniformly to the four inventory-sourced commands, not invented commands.
- `package-data` extensions (`*.json`, `*.md`, `*.yaml`, `*.mjs`) ← traced to the actual non-Python file extensions present under `runtime/` (verified: `json`, `md`, `mjs`, `yaml`, no others).
- `version = "0.1.0"` — the inventory records no prior distribution version (`"current_values": []` for the Python distribution identity, and "No pyproject.toml, setup.py, or setup.cfg exists in this checkout"). This is a standard initial-release default, not a dependency or command, and is recorded as an explicit packaging decision rather than an invented value.

**Verdict**: **PASS** — no invented dependency or command; every value traced to an inventory field, `requirements/plan26.in`, or `readme.md`.

### Test 3 — Package discovery is src-only and excludes repository contracts

**Procedure**: Built wheel and sdist (see Test 5 methodology) and listed their contents; grepped for `runtime/`, `tests/`, `policy/`, `schemas/`, `curricula/`, `docs/`, `outputs/`, `plans/`.

**Findings**: sdist contains exactly: `MANIFEST.in`, `PKG-INFO`, `pyproject.toml`, `readme.md`, `setup.cfg`, `src/curriculum_factory.egg-info/*` (5 generated metadata files), `src/curriculum_factory/__init__.py`. Wheel contains exactly: `curriculum_factory/__init__.py` plus 5 standard `dist-info` files. Leakage grep for `runtime/|tests/|policy/|schemas/|curricula/|docs/|outputs/|plans/` against both archives: **NONE FOUND**. An empirical control build with `MANIFEST.in` temporarily removed confirmed `tests/test_validate_instance.py` (the sole repository-root `tests/test*.py` file) *does* leak into the sdist under default setuptools sdist file-selection, proving the `MANIFEST.in` exclusion rule (`exclude tests/test*.py`) is load-bearing and not vacuous.

**Verdict**: **PASS**.

### Test 4 — Distribution metadata and console entry points are explicit

**Procedure**: Inspected wheel `METADATA`/`entry_points.txt` and sdist `PKG-INFO`.

**Findings**: `Name: curriculum-factory`, `Version: 0.1.0`, `Requires-Python: <3.14,>=3.13` (same constraint as declared, reordered by the metadata writer), 5 `Requires-Dist` runtime pins plus `Provides-Extra: dev` / `Requires-Dist: pytest==9.0.3; extra == "dev"` — identical between wheel `METADATA` and sdist `PKG-INFO`. `entry_points.txt` lists all 4 console scripts, matching the 4 P00-classified `module_main_guard` commands exactly (target module `curriculum_factory.<name>` — not invoked, since `curriculum_factory` does not yet contain `<name>` modules; runtime invocation is explicitly deferred to P03, and no test in this checkpoint executes any console script).

**Verdict**: **PASS**.

### Test 5 — Skeleton builds reproducibly without source movement

**Procedure**: Created two independent clean isolated checkouts (`rsync` copies of the working tree excluding `.git`/`__pycache__`/`node_modules`, at `/tmp/p01_ckA` and `/tmp/p01_ckB`), each with its own fresh `python3.13 -m venv` and its own `pip install build`. Ran `python -m build --outdir <dist>` in each checkout independently. Compared file lists, extracted (untarred/unzipped) directory trees via `diff -rq`, and per-file `sha256` digests.

**Findings**:
- Both builds exited 0.
- sdist file lists: identical (12 entries) between A and B.
- Wheel file lists: identical (6 entries) between A and B.
- `diff -rq` of fully extracted sdist trees: no differences. Same for extracted wheel trees.
- Per-file SHA-256 of all 12 extracted sdist files: identical between A and B (recorded set, e.g. `pyproject.toml=b1f0a183...`, `__init__.py=373ca383...`, `MANIFEST.in=36ebe432...`, egg-info files match too).
- Raw archive-level SHA-256 of the `.tar.gz`/`.whl` files differ between A and B — expected, since both formats embed build-time file timestamps in the archive; this is exactly the "normalize only archive timestamps" caveat in the test's own procedure, and normalized (extracted, content-only) comparison is what was used for the PASS determination.
- `runtime/` verified byte-identical (`diff -rq`, no `__pycache__`) between the live repository, checkout A, and checkout B.

**Verdict**: **PASS**.

## 4. Prerequisites, non-targets, stop conditions, rollback

- P00/P00A prerequisite evidence: present and witnessed QA_PASSED (§ Test 2). Not stale: baseline commit `c7c315f` is the repository HEAD at run start and matches the resolved-manifest generation basis.
- Non-targets honored: no production file under `runtime/` was moved, no import was rewritten, no resource loader was repaired, no test was renamed, no schema identifier was changed, and no installed behavioral parity is claimed anywhere in this report — only build/inspect evidence from unstalled artifacts.
- No successor prompt's mutation authority was borrowed: P01 did not touch anything under P03/P04/P02S's exact ownership; the `src/curriculum_factory/` prefix overlap with P03/P04 is addressed in Test 1 as temporally disjoint, not borrowed.
- Rollback procedure (as specified by the prompt: "a revert of this checkpoint followed by the P00 inventory reproducibility test"): verified exercisable — `git checkout -- pyproject.toml MANIFEST.in src/curriculum_factory/__init__.py tests/refactor_repo/test_packaging_skeleton.py && git clean -fd src/ MANIFEST.in pyproject.toml` would fully remove this checkpoint's deliverables (all are new/untracked or would restore to a nonexistent state) with `runtime/` and the P00 inventory untouched, so P00's own reproducibility test remains valid post-rollback. Rollback was not actually executed against the working tree during this run (no destructive command run), only confirmed exercisable by path analysis.

## 5. Residuals

- Stale `owns` label `pyproject_toml_identity_updates` under P02S in `prompt_manifest.resolved.v1.yaml`, no longer reachable given P02S v4's corrected `authorized_paths` — classified as **a recorded exception**, out of P01's authorization to edit, non-blocking per the analysis in Test 1. Recommend P00A (or a manifest-owning process) regenerate the resolved manifest's `owns` list for P02S to drop this label in a future pass; it does not affect this checkpoint's correctness because the enforcement mechanism (`authorized_paths`) is already fixed.
- No other residual old identities, paths, imports, output consumers, or schema references are within P01's scope (P01 creates new packaging metadata only; it does not touch existing identity strings elsewhere in the repository — that is P02S's and P07's scope).

## 6. Post-change git status

```
 M plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml   (pre-existing, not made by this run)
?? MANIFEST.in
?? plans_internal/refactor_repo/checkpoints/P01/
?? plans_internal/refactor_repo/execution/P01/
?? pyproject.toml
?? src/curriculum_factory/__init__.py
?? tests/refactor_repo/test_packaging_skeleton.py
```

Plus unrelated pre-existing untracked artifacts from P00A/manifest-resolution work (`prompts/resolved/prompt_manifest.resolved.v1_modified.yaml`, `prompts/resolved/prompt_manifest.resolved.v2.yaml`, `prompts/resolved/deprecated/`), none created or modified by this run.

Deliverable digests (SHA-256): `pyproject.toml=b1f0a1837563edf6219806f4e34cb0be9d1985060ddd17ee238dc5a484c7b820`; `MANIFEST.in=36ebe4327048aae325d514661111a83fed32085957ae00515fde0c99638ce79a`; `src/curriculum_factory/__init__.py=373ca38365f43cb6cc6d90767f48c61a7b2ab38a8693094d2f32a7deafe12404`; `tests/refactor_repo/test_packaging_skeleton.py=0ea463de2c5a2d5675196b62015e511f0cc5ff456226cb82eb198f4586d1e9b7`.

Rollback checkpoint verification result: exercisable, not executed (see §4).

## 7. Completion status

Local test suite: `pytest tests/refactor_repo/test_packaging_skeleton.py -q` → **13 passed**.
Execution journal: `plans_internal/refactor_repo/execution/P01/execution_log.jsonl`, all ACT starts closed, zero unclosed starts (verified via `ExecutionLogger.audit()` before this report was written).
Tests 1–5 above: all **PASS**.
Test 6 (independent Codex QA gate over this report) is run after this report is written, per the prompt's own test ordering, and its result is appended to this checkpoint directory as a separate versioned round record; this report does not itself claim Test 6's outcome.
