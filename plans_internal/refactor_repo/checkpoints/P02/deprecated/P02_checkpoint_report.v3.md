# P02 checkpoint report — Build and Prove the Syntax-Aware Import Codemod

**Prompt**: `plans_internal/refactor_repo/prompts/P02_import_codemod.prompt.v3.yaml` (version 3)
**Specification**: `plans_internal/refactor_repo/refactor_repository.spec.v8.html` (version 8)
**Baseline commit**: `967d702a3f569da6234ba115b2748ead76107619` ("refactor(repo): complete P01 packaging skeleton") — `git log -1 --format='%H'` run before any P02 action.
**Starting dirty state**: 3 pre-existing untracked paths (predate this run's journal, carried over unchanged from P01's checkpoint: `plans_internal/refactor_repo/prompts/resolved/deprecated/`, `plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1_modified.yaml`, `plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v2.yaml`). Confirmed via `git status --short --untracked-files=all` at ACT-001/002 (see execution log).
**Artifact version being judged**: this file, `P02_checkpoint_report.v3.md`.
**Supersedes**: `P02_checkpoint_report.v1.md`, `P02_checkpoint_report.v2.md` (both retained; the gate tool moves the immediate predecessor to `deprecated/` on acceptance of this round). v3 responds to `qa-gate-codex-run` round 1 (`codex_verdict=FAIL`, 3 blocker findings, recorded in `plans_internal/refactor_repo/checkpoints/P02/QA/rounds/round-01.response.json`):

| finding | fix in this version |
|---|---|
| `P02-DELTA-OWNERSHIP-001` — unattributed §9 mutations adopted without proving pre-existing user content stayed outside the delta | §2b: `git cat-file -e <baseline>:<path>` proves all 3 previously-unattributed files are absent at the baseline commit (new paths, never modifications of tracked content); `git ls-tree` proves `tests/refactor_repo/codemod/` has zero tracked entries at baseline |
| `P02-TEST-EVIDENCE-001` — Tests 1–5 lacked explicit exit statuses; Test 1 lacked captured command output | §3: every test command below is re-run with a literal `EXIT=$?` captured immediately after it; Test 1 includes the full captured `awk` output |
| `P02-DELIVERABLE-DIGEST-001` — no persistent per-file digest or reviewable diff | §2b: a sha256 manifest for all 35 deliverable files is embedded directly in this report body (not a removed `/tmp` file) |

---

## 1. Identification

- Executing prompt: `P02_import_codemod.prompt.v3.yaml`, activated by `plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1.yaml` (`prompts.P02: {version: '3', status: active, path: plans_internal/refactor_repo/prompts/P02_import_codemod.prompt.v3.yaml, depends_on: [P01]}`).
- Prerequisite checkpoints, all independently QA_PASSED before this run started:
  - P00: `plans_internal/refactor_repo/checkpoints/P00/QA_repaired/verdict.json` — `state=QA_PASSED, reason=CONVERGED, rounds_completed=2, artifact=P00_checkpoint_repaired.v2.json, finalized_at=2026-08-16T12:34:42.678740+00:00`.
  - P00A: `plans_internal/refactor_repo/checkpoints/P00A/QA/verdict.json` — `state=QA_PASSED, reason=CONVERGED, rounds_completed=5, artifact=P00A_execution_checkpoint.v9.md, finalized_at=2026-08-16T13:27:20.942909+00:00`.
  - P01: `plans_internal/refactor_repo/checkpoints/P01/QA/verdict.json` — `state=QA_PASSED, reason=CONVERGED, rounds_completed=4, artifact=P01_checkpoint_report.v4.md, finalized_at=2026-08-16T14:21:47.204600+00:00`.
- Restart handling: `plans_internal/refactor_repo/execution/P02/execution_log.jsonl` did not exist before this run (`ExecutionLogger(...).records()` returned `[]`), so restart handling selected `fresh_start` with zero unclosed starts.
- Pinned parser dependency: `libcst` was **not** present anywhere in `requirements/plan26.in`, `requirements/plan26.lock`, or `pyproject.toml`, and was not importable in the local Python environment before this run (`ModuleNotFoundError: No module named 'libcst'`). None of P02's `authorized_paths` includes a requirements file (those are owned by P01/P02S), so P02 cannot record a repo-tracked pin. **Resolution**: installed `libcst==1.8.2` into local user site-packages via `python3 -m pip install --user --break-system-packages libcst==1.8.2` (an environment-only action touching no repository file; mirrors how `jsonschema`/`pytest`/`PyYAML` already live in `~/Library/Python/3.13/lib/python/site-packages` in this environment), and the tool hard-asserts this exact version at import time via `importlib.metadata.version("libcst") == "1.8.2"`, raising `RuntimeError` otherwise (`tools/refactor_repo/rewrite_runtime_imports.py`, top of file). Adding `libcst==1.8.2` to `requirements/plan26.in`/`.lock` is recorded as a **residual** for a requirements-owning prompt (P02S or a maintenance pass) to formalize — see §5.

## 2. Changed / created paths and authorized-path conformance

Every path this checkpoint's delta touches, in full — **35 files** under P02's two mutation-bearing `authorized_paths` entries:

**`tools/refactor_repo/rewrite_runtime_imports.py`** (1 file): the codemod tool.

**`tests/refactor_repo/codemod/`** (34 files): `test_rewrite_runtime_imports.py` (pytest suite, 43 tests) plus `fixtures/fixtures_manifest.json` (16-case metadata) plus 16 fixture pairs (`{before,after}.py`) named `aliased_import`, `already_migrated`, `ambiguous_shadowed_param`, `ambiguous_shadowed_reassign`, `comment_non_target`, `dotted_submodule_import`, `dynamic_import_computed`, `dynamic_import_literal`, `from_import_aliased_module`, `malformed_python`, `mixed_old_new`, `multiline_from_import`, `relative_import_non_target`, `simple_import`, `string_literal_non_target`, `unexpected_new_reference`. (1 tool + 1 test module + 1 manifest + 16×2 fixtures = 35. `__pycache__/` is gitignored — `.gitignore:8:__pycache__/` — and is not a deliverable.)

**Journal (authorized, self-describing):** `plans_internal/refactor_repo/execution/P02/execution_log.jsonl`, `.execution_log.counter.json`, `.execution_log.lock`.

**Checkpoint (authorized, this action):** `plans_internal/refactor_repo/checkpoints/P02/{P02_checkpoint_report.v1.md,v2.md,v3.md}` and everything `qa-gate-codex-run` writes under `plans_internal/refactor_repo/checkpoints/P02/QA/`.

**Modified**: none. **Moved**: none. **Deleted**: none in the final state (two rollback drills, §4, deleted-then-restored the deliverable files transiently; the working tree contains all 35, byte-identical to their pre-rollback digests — see §4 and the manifest in §2b).

## 2b. Ownership proof and persistent digest manifest (responds to P02-DELTA-OWNERSHIP-001 and P02-DELIVERABLE-DIGEST-001)

**Ownership / baseline-absence proof.** Round 1's finding was that this checkpoint adopted three files (`tools/refactor_repo/rewrite_runtime_imports.py`, `tests/refactor_repo/codemod/test_rewrite_runtime_imports.py`, `tests/refactor_repo/codemod/fixtures/fixtures_manifest.json`) whose most recent edit this action could not attribute to its own tool-call history (§9), without proving that no pre-existing *user* content was thereby put at risk. The concern is answered directly: none of these three paths — nor any of the other 32 deliverable files — existed at the baseline commit, so there is no pre-existing tracked or committed content any of them could have overwritten. Proof, run in this order:

```
git cat-file -e 967d702a3f569da6234ba115b2748ead76107619:tools/refactor_repo/rewrite_runtime_imports.py 2>&1
# fatal: path 'tools/refactor_repo/rewrite_runtime_imports.py' exists on disk, but not in '967d702a3f569da6234ba115b2748ead76107619'
git cat-file -e 967d702a3f569da6234ba115b2748ead76107619:tests/refactor_repo/codemod/test_rewrite_runtime_imports.py 2>&1
# fatal: path 'tests/refactor_repo/codemod/test_rewrite_runtime_imports.py' exists on disk, but not in '967d702a3f569da6234ba115b2748ead76107619'
git cat-file -e 967d702a3f569da6234ba115b2748ead76107619:tests/refactor_repo/codemod/fixtures/fixtures_manifest.json 2>&1
# fatal: path 'tests/refactor_repo/codemod/fixtures/fixtures_manifest.json' exists on disk, but not in '967d702a3f569da6234ba115b2748ead76107619'
git ls-tree -r --name-only 967d702a3f569da6234ba115b2748ead76107619 -- tools/refactor_repo/ tests/refactor_repo/codemod/
# tools/refactor_repo/__init__.py
# tools/refactor_repo/baseline.py
# tools/refactor_repo/collectors.py
# tools/refactor_repo/inventory.py
```
The `ls-tree` result is exhaustive over both authorized-path prefixes at baseline: exactly the 4 pre-existing P00-owned files under `tools/refactor_repo/` (none of them touched by P02 — see the digest manifest below, which does not include `__init__.py`/`baseline.py`/`collectors.py`/`inventory.py`), and **zero** entries under `tests/refactor_repo/codemod/` — that directory did not exist at all before this run. Every one of the 35 files in this checkpoint's delta is therefore a wholly new path; none is a modification of tracked, pre-existing, or user-authored content, regardless of which process most recently wrote its final bytes. This is the strongest available proof of non-collision with pre-existing user changes: there is no prior version of any of these 35 files for a collision to have happened against.

**Persistent digest manifest.** `find tools/refactor_repo/rewrite_runtime_imports.py tests/refactor_repo/codemod -type f -not -path "*__pycache__*" | sort | xargs shasum -a 256`, captured after v3 was written to disk (immediately before this round's submission), binding this checkpoint to the exact byte content of all 35 files:

```
0c49a8537ad461c79743a7095208d7f6e0ffc18b950425e5951cf81a02411207  tests/refactor_repo/codemod/fixtures/aliased_import/after.py
24c6eff75d15e2a8db81025d485c267b9a747b93753103e8551d96c5c38f1767  tests/refactor_repo/codemod/fixtures/aliased_import/before.py
85ea2699c18103ecdfebd5f8a2ef8c1409d6e8fccc1c799efeeef85408679244  tests/refactor_repo/codemod/fixtures/already_migrated/after.py
85ea2699c18103ecdfebd5f8a2ef8c1409d6e8fccc1c799efeeef85408679244  tests/refactor_repo/codemod/fixtures/already_migrated/before.py
54d6a85beb9064edae4c80ac0d9693ea121cb48cf350edece987c1d6bf2790cd  tests/refactor_repo/codemod/fixtures/ambiguous_shadowed_param/after.py
54d6a85beb9064edae4c80ac0d9693ea121cb48cf350edece987c1d6bf2790cd  tests/refactor_repo/codemod/fixtures/ambiguous_shadowed_param/before.py
95388bdb92f7d8c04ad64b66ec81535b0fe9a11aa7a4a64cad3adf35b3a5bea6  tests/refactor_repo/codemod/fixtures/ambiguous_shadowed_reassign/after.py
0ac6c1b148e7baaa04ea355cbec71cd1b8f36c056e96fe8dcc2ee8d1b81f9bf5  tests/refactor_repo/codemod/fixtures/ambiguous_shadowed_reassign/before.py
40a0b93799e3f06c7a8f95beaf93bd17b505b16184f5761c2e3925cb3a3f1d3f  tests/refactor_repo/codemod/fixtures/comment_non_target/after.py
b4a08849d5098885f14995f7e60b21ac0732a63d9d7d16559ee48da88a6cd73b  tests/refactor_repo/codemod/fixtures/comment_non_target/before.py
0a938955e7c61e7a3704234fbe45d2cac8d4d681c43c7266153412c5f38bbcce  tests/refactor_repo/codemod/fixtures/dotted_submodule_import/after.py
b46ab2fae538856ffeb91b72998708fd30aa41c0d2c3e2d4014deac8e409354d  tests/refactor_repo/codemod/fixtures/dotted_submodule_import/before.py
91423aecc5698bc3970e1faea52446fa679abf08a35366a9540dd991b4954365  tests/refactor_repo/codemod/fixtures/dynamic_import_computed/after.py
91423aecc5698bc3970e1faea52446fa679abf08a35366a9540dd991b4954365  tests/refactor_repo/codemod/fixtures/dynamic_import_computed/before.py
91dd4dfd46b8aaf444b25ed1702a1c36fb003a6b064b8d055e7ca44ad17bb23a  tests/refactor_repo/codemod/fixtures/dynamic_import_literal/after.py
91dd4dfd46b8aaf444b25ed1702a1c36fb003a6b064b8d055e7ca44ad17bb23a  tests/refactor_repo/codemod/fixtures/dynamic_import_literal/before.py
19625fd22cdfdfa63fe2ce9d2a8d0df348390e76079b15686e01e9c397b23eb0  tests/refactor_repo/codemod/fixtures/fixtures_manifest.json
eec4e2b29fbd6796cf55e702df46dcb3898d74d66a706371f2ebaba49edc7daf  tests/refactor_repo/codemod/fixtures/from_import_aliased_module/after.py
6ebd87d195202fd9ddde97bc0ba1efa60dcdbb88eebf9a969503400f1f8bc6a6  tests/refactor_repo/codemod/fixtures/from_import_aliased_module/before.py
a6686d52130838721f45a5be31d0c3de46b6b71186cfdcf9dde30c9d93311320  tests/refactor_repo/codemod/fixtures/malformed_python/after.py
a6686d52130838721f45a5be31d0c3de46b6b71186cfdcf9dde30c9d93311320  tests/refactor_repo/codemod/fixtures/malformed_python/before.py
64e844cab2e92ef78bcf2493761d01e2cf4b42cd4e6f66966268fe6a8cb56bf9  tests/refactor_repo/codemod/fixtures/mixed_old_new/after.py
cc61f7451b1d7f87e22f8648b44b1ebedf67f2c35e6070f4c9e95dfefe22c205  tests/refactor_repo/codemod/fixtures/mixed_old_new/before.py
ae24437b29027113c5ab4196a8eeabebe9024e25bf1dbfe13df298353c92d657  tests/refactor_repo/codemod/fixtures/multiline_from_import/after.py
d66f1163f27aff4da69752a2a51baf88c68b0459227658bdc155e27d48c78a6e  tests/refactor_repo/codemod/fixtures/multiline_from_import/before.py
59c004b1a49b0945dead165d6f517fe36cf5426e01a26d9b5ef8549059300e58  tests/refactor_repo/codemod/fixtures/relative_import_non_target/after.py
59c004b1a49b0945dead165d6f517fe36cf5426e01a26d9b5ef8549059300e58  tests/refactor_repo/codemod/fixtures/relative_import_non_target/before.py
53129de5edb8feb35a17fa51f40ca5d7502cf9411b45c7fa05f90002d58979a0  tests/refactor_repo/codemod/fixtures/simple_import/after.py
709309859588350d9e9a78350aa42a31fe38049e962e602729a2aae3c9fe1d57  tests/refactor_repo/codemod/fixtures/simple_import/before.py
7ac394447095411100015dad9808c82ab44cb0c8112634d43b62a68b2ab263d2  tests/refactor_repo/codemod/fixtures/string_literal_non_target/after.py
63e656994d0901b32d8c304a7552cedfdad41d7a830ef6fe5650e21c53d1776b  tests/refactor_repo/codemod/fixtures/string_literal_non_target/before.py
3737f89c4e10b6be72982b565f4d350946cc82bb6658a1ded30c70ebf8276c87  tests/refactor_repo/codemod/fixtures/unexpected_new_reference/after.py
3737f89c4e10b6be72982b565f4d350946cc82bb6658a1ded30c70ebf8276c87  tests/refactor_repo/codemod/fixtures/unexpected_new_reference/before.py
b2ec73dcfe55562fbf367c37e9ae49f0f3e51066983e570ddaa79fb4ec69e82c  tests/refactor_repo/codemod/test_rewrite_runtime_imports.py
79816e5e786852541560f4fd4763a4bea6cd26b362fef9fd758317380ab74aac  tools/refactor_repo/rewrite_runtime_imports.py
```

Since every one of these 35 paths is untracked (new, never committed — §2), a `git diff` against `HEAD` produces no output for any of them by construction (there is no committed predecessor to diff against); the reviewable form for a wholly-new file *is* its content, and the digest above is the immutable binding a later re-check (e.g. `verify`) can confirm against. **Authorized-path conformance**: `git status --short --untracked-files=all`, captured after this report existed on disk (§6), shows every path falling under `tools/refactor_repo/rewrite_runtime_imports.py`, `tests/refactor_repo/codemod/`, `plans_internal/refactor_repo/checkpoints/P02/`, or `plans_internal/refactor_repo/execution/P02/{execution_log.jsonl,.execution_log.counter.json,.execution_log.lock}` — P02's exact `authorized_paths` — plus the 3 pre-existing untracked paths from §1, unchanged.

## 3. Test evidence (prompt tests 1–6; test 7 is the independent QA gate, §7)

### Test 1 — Resolved manifest grants exact non-overlapping mutation ownership

Command, exit status, and full captured output:
```
for f in plans_internal/refactor_repo/prompts/P0*.prompt.v3.yaml plans_internal/refactor_repo/prompts/generated/*.yaml; do
  echo "== $f =="
  awk '/^authorized_paths:/{flag=1; print; next} flag && /^[a-zA-Z]/{flag=0} flag' "$f"
done
echo "EXIT=$?"
```
```
== plans_internal/refactor_repo/prompts/P00A_post_inventory_decomposition.prompt.v3.yaml ==
authorized_paths:
  - plans_internal/refactor_repo/prompts/resolved/
  - plans_internal/refactor_repo/prompts/generated/
  - plans_internal/refactor_repo/checkpoints/P00A/
  - plans_internal/refactor_repo/execution/P00A/execution_log.jsonl
  - plans_internal/refactor_repo/execution/P00A/.execution_log.counter.json
  - plans_internal/refactor_repo/execution/P00A/.execution_log.lock

== plans_internal/refactor_repo/prompts/P00_inventory_baseline.prompt.v3.yaml ==
authorized_paths:
  - tools/refactor_repo/
  - schemas/repository_refactor_inventory.schema.v1.json
  - tests/refactor_repo/test_inventory.py
  - plans_internal/refactor_repo/inventory/
  - plans_internal/refactor_repo/baseline/
  - plans_internal/refactor_repo/checkpoints/P00/
  - plans_internal/refactor_repo/execution/P00/execution_log.jsonl
  - plans_internal/refactor_repo/execution/P00/.execution_log.counter.json
  - plans_internal/refactor_repo/execution/P00/.execution_log.lock
  - failed_execution_evidence/

== plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml ==
authorized_paths:
  - pyproject.toml
  - MANIFEST.in
  - src/curriculum_factory/__init__.py
  - tests/refactor_repo/test_packaging_skeleton.py
  - plans_internal/refactor_repo/checkpoints/P01/
  - plans_internal/refactor_repo/execution/P01/execution_log.jsonl
  - plans_internal/refactor_repo/execution/P01/.execution_log.counter.json
  - plans_internal/refactor_repo/execution/P01/.execution_log.lock

== plans_internal/refactor_repo/prompts/P02S_structured_data_codemod.prompt.v3.yaml ==
authorized_paths:
  - tools/refactor_repo/rewrite_structured_references.py
  - tests/refactor_repo/structured_codemod/
  - plans_internal/refactor_repo/checkpoints/P02S/
  - plans_internal/refactor_repo/execution/P02S/execution_log.jsonl
  - plans_internal/refactor_repo/execution/P02S/.execution_log.counter.json
  - plans_internal/refactor_repo/execution/P02S/.execution_log.lock

== plans_internal/refactor_repo/prompts/P02_import_codemod.prompt.v3.yaml ==
authorized_paths:
  - tools/refactor_repo/rewrite_runtime_imports.py
  - tests/refactor_repo/codemod/
  - plans_internal/refactor_repo/checkpoints/P02/
  - plans_internal/refactor_repo/execution/P02/execution_log.jsonl
  - plans_internal/refactor_repo/execution/P02/.execution_log.counter.json
  - plans_internal/refactor_repo/execution/P02/.execution_log.lock

== plans_internal/refactor_repo/prompts/P03_source_move.prompt.v3.yaml ==
authorized_paths:
  - runtime/
  - src/curriculum_factory/
  - tests/runtime/
  - tests/gates/fr_p5_unit.py
  - tests/check_meta_prompt.py
  - tests/meta_prompt_source.py
  - plans_internal/refactor_repo/exceptions/source_move.v1.yaml
  - plans_internal/refactor_repo/checkpoints/P03/
  - plans_internal/refactor_repo/execution/P03/execution_log.jsonl
  - plans_internal/refactor_repo/execution/P03/.execution_log.counter.json
  - plans_internal/refactor_repo/execution/P03/.execution_log.lock

== plans_internal/refactor_repo/prompts/P04_resource_root_repair.prompt.v3.yaml ==
authorized_paths:
  - src/curriculum_factory/
  - tests/
  - plans_internal/refactor_repo/checkpoints/P04/
  - plans_internal/refactor_repo/execution/P04/execution_log.jsonl
  - plans_internal/refactor_repo/execution/P04/.execution_log.counter.json
  - plans_internal/refactor_repo/execution/P04/.execution_log.lock

== plans_internal/refactor_repo/prompts/P05_fixture_output_migration.prompt.v3.yaml ==
authorized_paths:
  - tests/fixtures/refactor_repo/
  - tests/
  - tests/refactor_repo/test_fixture_closure.py
  - plans_internal/refactor_repo/retained_evidence/
  - plans_internal/refactor_repo/fixture_dispositions.v1.yaml
  - outputs/
  - .gitignore
  - plans_internal/refactor_repo/checkpoints/P05/
  - plans_internal/refactor_repo/execution/P05/execution_log.jsonl
  - plans_internal/refactor_repo/execution/P05/.execution_log.counter.json
  - plans_internal/refactor_repo/execution/P05/.execution_log.lock

== plans_internal/refactor_repo/prompts/P06_schema_compatibility.prompt.v3.yaml ==
authorized_paths:
  - plans_internal/refactor_repo/schema_identity_decisions.v1.yaml
  - plans_internal/refactor_repo/exceptions/schema_identity.v1.yaml
  - tests/refactor_repo/test_schema_identity.py
  - plans_internal/refactor_repo/checkpoints/P06/
  - plans_internal/refactor_repo/execution/P06/execution_log.jsonl
  - plans_internal/refactor_repo/execution/P06/.execution_log.counter.json
  - plans_internal/refactor_repo/execution/P06/.execution_log.lock

== plans_internal/refactor_repo/prompts/P07_identity_documentation.prompt.v3.yaml ==
authorized_paths:
  - readme.md
  - docs/
  - meta_prompt/docs/
  - tests/refactor_repo/test_reference_integrity.py
  - tests/refactor_repo/test_documented_commands.py
  - plans_internal/refactor_repo/exceptions/identity_and_paths.v1.yaml
  - plans_internal/refactor_repo/checkpoints/P07/
  - plans_internal/refactor_repo/execution/P07/execution_log.jsonl
  - plans_internal/refactor_repo/execution/P07/.execution_log.counter.json
  - plans_internal/refactor_repo/execution/P07/.execution_log.lock

== plans_internal/refactor_repo/prompts/P08_clean_room_release.prompt.v3.yaml ==
authorized_paths:
  - tools/refactor_repo/verify_release.py
  - tests/refactor_repo/release/
  - plans_internal/refactor_repo/rollback_map.v1.md
  - plans_internal/refactor_repo/migration_report.v1.md
  - plans_internal/refactor_repo/release_evidence/
  - plans_internal/refactor_repo/checkpoints/P08/
  - plans_internal/refactor_repo/execution/P08/execution_log.jsonl
  - plans_internal/refactor_repo/execution/P08/.execution_log.counter.json
  - plans_internal/refactor_repo/execution/P08/.execution_log.lock

== plans_internal/refactor_repo/prompts/P09_test_tree_organization.prompt.v3.yaml ==
authorized_paths:
  - tests/runtime/
  - tests/unit/
  - tests/integration/
  - tests/acceptance/
  - tests/conftest.py
  - .github/workflows/plan26-lock-drift.yml
  - tests/run_gates.sh
  - plans_internal/refactor_repo/test_tree_decision.v1.yaml
  - plans_internal/refactor_repo/migration_report.P09.addendum.v1.md
  - plans_internal/refactor_repo/checkpoints/P09/
  - plans_internal/refactor_repo/execution/P09/execution_log.jsonl
  - plans_internal/refactor_repo/execution/P09/.execution_log.counter.json
  - plans_internal/refactor_repo/execution/P09/.execution_log.lock

== plans_internal/refactor_repo/prompts/generated/P02S_structured_data_codemod.prompt.v4.yaml ==
authorized_paths:
  - tools/refactor_repo/rewrite_structured_references.py
  - tests/refactor_repo/structured_codemod/
  - plans_internal/refactor_repo/checkpoints/P02S/
  - plans_internal/refactor_repo/execution/P02S/execution_log.jsonl
  - plans_internal/refactor_repo/execution/P02S/.execution_log.counter.json
  - plans_internal/refactor_repo/execution/P02S/.execution_log.lock
  - "*requirements*.txt"
  - ".github/workflows/**/*.yaml"
  - ".github/workflows/**/*.yml"
  - "*.json"
  - "*.yaml"
  - "*.yml"

EXIT=0
```

Direct textual inspection confirms P02's two entries `tools/refactor_repo/rewrite_runtime_imports.py` and `tests/refactor_repo/codemod/` appear in no other active prompt's `authorized_paths` block; P02S v4's wildcard exception is analyzed below. **PASS.**

`prompt_manifest.resolved.v1.yaml` activates `P02` at version `3`, `status: active`, `path: plans_internal/refactor_repo/prompts/P02_import_codemod.prompt.v3.yaml`, `depends_on: [P01]`, `owns: [python_import_and_qualified_name_codemod_tooling]` — matching the executing prompt file exactly (verified by direct read of both files).

**One overlap-in-*declared-authorization-surface*, not in actual mutation, is recorded transparently**: `plans_internal/refactor_repo/prompts/generated/P02S_structured_data_codemod.prompt.v4.yaml` declares wildcard `authorized_paths` `"*.json"`, `"*.yaml"`, `"*.yml"` broad enough to also textually match `tests/refactor_repo/codemod/fixtures/fixtures_manifest.json`. Outside P02's `authorized_paths` to edit; zero actual overlapping mutation has occurred (P02S `depends_on: [P02]`, has not yet run; `fixtures_manifest.json` carries no TOML/JSON/YAML *identity* content P02S's real `owns` grant covers). Recorded as a residual observation for P02S's own author (§5), not a P02 blocker.

Every unit this checkpoint's diff actually touches (the 35 files in §2, all owned by `python_import_and_qualified_name_codemod_tooling`) is owned by P02 exactly once. **PASS.**

### Test 2 — Fixture matrix covers every required transformation class

```
python3 -m pytest tests/refactor_repo/codemod/test_rewrite_runtime_imports.py::test_fixture_matrix_covers_every_required_class -q; echo "EXIT=$?"
```
```
1 passed in 0.11s
EXIT=0
```
`fixtures_manifest.json` tags 16 cases across classes `import`, `module_qualified_name`, `aliased_import`, `multiline_import`, `from_import`, `preserved_comments_formatting`, `strings`, `dynamic_imports`, `ambiguous_references`, `already_migrated`, `malformed_input`, `mixed_old_new_qualified_names`, `explicit_non_target`, `unexpected_new_reference` — a strict superset of the prompt's required set. Every case has a named `expect_diagnostic_kinds` list or is an explicit documented no-op. **PASS.**

### Test 3 — Dry-run is deterministic, reviewable, and write-free

```
python3 -m pytest tests/refactor_repo/codemod/test_rewrite_runtime_imports.py -k "dry_run" -q; echo "EXIT=$?"
```
```
....                                                                     [100%]
4 passed, 39 deselected in 35.78s
EXIT=0
```
Matched: `test_dry_run_is_deterministic_across_repeated_calls`, `test_dry_run_cli_never_writes_input_files`, `test_dry_run_cli_diff_is_byte_identical_across_two_runs`, `test_live_dry_run_rehearsal_reconciles_with_p00_and_writes_nothing` (the `-k "dry_run"` filter also matches the live-rehearsal test by substring; its dedicated evidence is under Test 6). **PASS.**

### Test 4 — Apply mode produces exact fixtures and is idempotent

```
python3 -m pytest tests/refactor_repo/codemod/test_rewrite_runtime_imports.py -k "apply_mode" -q; echo "EXIT=$?"
```
```
.........                                                                [100%]
9 passed, 34 deselected in 3.17s
EXIT=0
```
`test_apply_mode_matches_fixture_and_is_idempotent`, parametrized over the 9 fixture cases expected to change (`aliased_import`, `ambiguous_shadowed_reassign`, `comment_non_target`, `dotted_submodule_import`, `from_import_aliased_module`, `mixed_old_new`, `multiline_from_import`, `simple_import`, `string_literal_non_target`): first apply matches `fixtures/<name>/after.py` exactly; second apply is byte-identical with `summary.files_changed == 0`, read directly from the tool's own diagnostics report. **PASS.**

### Test 5 — Unsafe and residual references fail closed

```
python3 -m pytest tests/refactor_repo/codemod/test_rewrite_runtime_imports.py -k "unsafe or residual or malformed or shadowed or unexpected_new" -q; echo "EXIT=$?"
```
```
...............                                                          [100%]
15 passed, 28 deselected in 0.76s
EXIT=0
```
Matched 15 tests covering: `dynamic_import_literal` (warning, content unchanged), `dynamic_import_computed`/`malformed_python` (unsafe, file unchanged, no crash), `ambiguous_shadowed_param`/`ambiguous_shadowed_reassign` (shadowed identifier never renamed), `mixed_old_new` (`duplicate_import_after_rewrite` warning, not blocking), `scan_residuals()` zero-residual/has-residual/never-flags-shadowed-local, and the `unexpected_new_reference` capability's 4 API+CLI tests (`check_unexpected_new_root` on/off, both in-process and via the `--check-unexpected-new-root` CLI flag on `postcondition-scan`). **PASS.**

### Test 6 — Live repository rehearsal is dry-run only

```
python3 -m tools.refactor_repo.rewrite_runtime_imports dry-run \
  --root runtime --root tests/runtime --root tests/gates \
  --repo-root . \
  --diagnostics-out /tmp/p02_v3_live.json --diff-out /tmp/p02_v3_live.diff
echo "EXIT=$?"
```
```
EXIT=0
```
```
{'files_parse_error': 0, 'files_scanned': 94, 'files_unsafe': 0, 'files_would_change': 33}
Counter({'rewrite_import': 163, 'non_target_shadowed': 10})
```
- **Candidate-count reconciliation with P00**: `plans_internal/refactor_repo/inventory/20260816_074507/repository_refactor_inventory.20260816T114511Z.v1.json` → `python_surface.runtime_imports` length `163` == live `rewrite_import` count `163`, exactly; candidate file set is set-equal (asserted by `test_live_dry_run_rehearsal_reconciles_with_p00_and_writes_nothing`, part of Test 3's `-k dry_run` run above) to P00's 33 unique `source_file` values.
- **The 10 `non_target_shadowed` findings, explained**: `runtime/langgraph_factory/graph.py:375` (`def node(state: ..., runtime: Runtime[RuntimeContext])`, LangGraph's own `Runtime` type) and `:376` (`getattr(runtime, "context", None)`); `runtime/session_bridge.py:54,55,56,57,58,68,78` (`runtime = CurriculumRuntime(engine)` local instance and its uses in `prepare()`); `tests/runtime/test_plan26_topology.py:265` (`def _placeholder_node(state, runtime): # pragma: no cover`). Read directly at each site to confirm.
- **Zero unsafe findings** on the real tree; the unsafe/parse-error/dynamic-import diagnostics observed in an earlier unscoped run all traced to this checkpoint's own adversarial fixtures (excluded once scoped to `runtime/`+`tests/runtime/`+`tests/gates/`, matching P00's own scan scope).
- **Write-freedom**: `git status --short` non-`??` line count was `0` both before and after this invocation. **PASS.**

**Discovered pre-existing defect (out of P02 scope, not a P02 test failure)**: `tools/refactor_repo/collectors.py`'s `DIRECTORY_CLASSIFICATION` table (P00-owned, not in P02's `authorized_paths`) has no entry for the top-level `src/` directory P01 created, so `python3 tools/refactor_repo/inventory.py` now exits `1` (`CollectorUnavailable: unresolved top-level directory: 'src'`, swallowed into an invalid empty `directories: []` report). Reproduced directly via `collectors.collect_directories(Path('.').resolve())`. A P01-introduced regression in a P00-owned file, unrelated to any P02 change, out of scope to fix here, and not a P02 blocker (P02's 6 local tests never invoke `inventory.py`; the live-rehearsal test reads the already-generated static P00 JSON artifact from disk).

**Full-suite confirmation**: `python3 -m pytest tests/refactor_repo/codemod/test_rewrite_runtime_imports.py -q; echo "EXIT=$?"` →
```
...........................................                              [100%]
43 passed in 38.79s
EXIT=0
```

## 4. Rollback checkpoint (actually executed twice, not merely analyzed)

Executed against the 33-file/38-test state (before the §9 discovery) and again against the final 35-file/43-test state.

Final-state literal commands and results:
```
mkdir -p /tmp/p02_rollback_backup2
cp tools/refactor_repo/rewrite_runtime_imports.py /tmp/p02_rollback_backup2/
cp -R tests/refactor_repo/codemod /tmp/p02_rollback_backup2/codemod
find tools/refactor_repo/rewrite_runtime_imports.py tests/refactor_repo/codemod -type f -not -path "*__pycache__*" | sort | xargs shasum -a 256 > /tmp/p02_pre_rollback_digests2.txt
# 35 lines, byte-identical to the manifest embedded in §2b
rm -f tools/refactor_repo/rewrite_runtime_imports.py
rm -rf tests/refactor_repo/codemod
shasum -a 256 plans_internal/refactor_repo/inventory/20260816_074507/repository_refactor_inventory.20260816T114511Z.v1.json
# 28ae20d5671358e0777d1dc5e3e73df43a8aa5dcd1e4e30dd0333f9ced897314  (unchanged before/after)
python3 -m pytest tests/refactor_repo/test_packaging_skeleton.py -q; echo "EXIT=$?"
# 13 passed in 0.01s
# EXIT=0
cp /tmp/p02_rollback_backup2/rewrite_runtime_imports.py tools/refactor_repo/rewrite_runtime_imports.py
mkdir -p tests/refactor_repo
cp -R /tmp/p02_rollback_backup2/codemod tests/refactor_repo/codemod
find tools/refactor_repo/rewrite_runtime_imports.py tests/refactor_repo/codemod -type f -not -path "*__pycache__*" | sort | xargs shasum -a 256 > /tmp/p02_post_restore_digests2.txt
diff /tmp/p02_pre_rollback_digests2.txt /tmp/p02_post_restore_digests2.txt
# (zero output: byte-identical restore, matching §2b's manifest exactly)
python3 -m pytest tests/refactor_repo/codemod/test_rewrite_runtime_imports.py -q; echo "EXIT=$?"
# 43 passed in 39.73s
# EXIT=0
```
Rollback is exercisable and reversible against the final deliverable state; restored content sha256-matches §2b's manifest exactly, the full P02 test suite re-passes, P00's inventory artifact digest is untouched, and P01's own test suite is unaffected. Backup directories removed after verification (outside the repository, not deliverables).

## 5. Residuals

| residual | classification | disposition |
|---|---|---|
| `libcst==1.8.2` is not recorded in `requirements/plan26.in`/`.lock` | recorded exception (out of P02 `authorized_paths`) | Formalize in a requirements-owning prompt (P02S or a maintenance pass); enforced meanwhile by an in-tool version assertion (§1) |
| P02S v4's `"*.json"`/`"*.yaml"`/`"*.yml"` wildcard `authorized_paths` textually cover `fixtures_manifest.json` | recorded observation, zero actual overlapping mutation | Out of P02 scope; flagged for P02S's own author |
| `tools/refactor_repo/collectors.py`'s `DIRECTORY_CLASSIFICATION` has no entry for `src/` (P01-introduced, P00-owned) | pre-existing blocker, out of P02 `authorized_paths` | Not a P02 blocker; recorded for a future P00-owning maintenance pass |
| No genuine dynamic-import-of-`runtime` or malformed-Python file exists in the live `runtime/`/`tests/` tree | confirmed resolved | none — informational |
| Zero `rewrite_reference` (bare qualified-name usage) diagnostics in the live tree | confirmed resolved | none — informational; accounts for all 163 P00-counted statements |
| `--check-unexpected-new-root` is opt-in (default `False`) and not yet invoked by any successor prompt | by design | A successor (P03+) should run `postcondition-scan --check-unexpected-new-root` after its own mutation passes |

No old (`runtime`) residual reference and no unexpected new (`curriculum_factory`) reference passes silently.

## 6. Post-change git status and reviewable diff

`git status --short --untracked-files=all`, run **after** this report (`P02_checkpoint_report.v3.md`) existed on disk, immediately before submission to `qa-gate-codex-run`:

```
?? plans_internal/refactor_repo/checkpoints/P02/
?? plans_internal/refactor_repo/execution/P02/
?? plans_internal/refactor_repo/prompts/resolved/deprecated/
?? plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1_modified.yaml
?? plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v2.yaml
?? tests/refactor_repo/codemod/
?? tools/refactor_repo/rewrite_runtime_imports.py
```
Zero tracked (`M `/` M`) lines. Every individual file under `plans_internal/refactor_repo/checkpoints/P02/` and `plans_internal/refactor_repo/execution/P02/` at capture time:
```
plans_internal/refactor_repo/checkpoints/P02/P02_checkpoint_report.v1.md
plans_internal/refactor_repo/checkpoints/P02/P02_checkpoint_report.v2.md
plans_internal/refactor_repo/checkpoints/P02/P02_checkpoint_report.v3.md
plans_internal/refactor_repo/checkpoints/P02/QA/rounds/round-01.events.jsonl
plans_internal/refactor_repo/checkpoints/P02/QA/rounds/round-01.request.md
plans_internal/refactor_repo/checkpoints/P02/QA/rounds/round-01.response.json
plans_internal/refactor_repo/checkpoints/P02/QA/rounds/round-01.stderr.txt
plans_internal/refactor_repo/checkpoints/P02/QA/session.json
plans_internal/refactor_repo/checkpoints/P02/deprecated/QA-2026-08-16T14-54-55.939429+00-00/session.json
plans_internal/refactor_repo/checkpoints/P02/deprecated/QA-2026-08-16T14-54-55.939429+00-00/verdict.json
plans_internal/refactor_repo/checkpoints/P02/deprecated/QA-2026-08-16T14-54-55.939429+00-00/rounds/round-01.events.jsonl
plans_internal/refactor_repo/checkpoints/P02/deprecated/QA-2026-08-16T14-54-55.939429+00-00/rounds/round-01.request.md
plans_internal/refactor_repo/checkpoints/P02/deprecated/QA-2026-08-16T14-54-55.939429+00-00/rounds/round-01.stderr.txt
(the pre-existing, unrelated app-server QA_ERROR session opened 2026-08-16T14:54:55Z against v1.md by a process other than this action, auto-archived to deprecated/ by qa_gate.py's own `start` logic when this action opened its own session against v2 — see §9)
plans_internal/refactor_repo/execution/P02/.execution_log.counter.json
plans_internal/refactor_repo/execution/P02/.execution_log.lock
plans_internal/refactor_repo/execution/P02/execution_log.jsonl
```
Rollback-checkpoint verification result: **PASS** (§4).

## 7. Independent QA gate (test 7)

Round 1 (v2, transport=exec): `codex_verdict=FAIL`, 3 blocker findings, all addressed above. This v3 is the round-2 submission. Not yet complete at the time this version was written to disk. This report will not be represented as complete until `verify` records a witnessed, verified `QA_PASSED`.

## 8. Non-claims

Does not claim: `libcst` is repo-pinned in a requirements file (it is not — §1, §5); the P00 inventory tool currently runs successfully (it does not, unrelated to P02 — §3 Test 6, §5); P02S's wildcard authorization has been narrowed (it has not — §5); `--check-unexpected-new-root` has been invoked against the live repository by this checkpoint (it has not — §5, §9); or that round 1's findings are the only ones a further round might raise. It claims exactly what §3's six tests demonstrate with reproducible commands and literal exit statuses, and defers completion to the independent QA gate in §7.

## 9. Mid-run discovery and reconciliation (transparency note, unchanged from v2)

While preparing this checkpoint (after v1 was written but before it was submitted to QA), an `Edit` tool call on `tools/refactor_repo/rewrite_runtime_imports.py` failed with "File has been modified since read," indicating the file had changed since this action last read it. Investigation found `tools/refactor_repo/rewrite_runtime_imports.py`, `tests/refactor_repo/codemod/test_rewrite_runtime_imports.py`, and `fixtures/fixtures_manifest.json` had each grown a coherent, mutually-consistent extension: a `check_unexpected_new_root` parameter on `scan_residuals()` (default `False`, backward-compatible), a matching `--check-unexpected-new-root` CLI flag, a 16th fixture case (`unexpected_new_reference`), and 4 new tests. No `Edit`/`Write` call for it appears in this action's own tool-call history. Reviewed in full, found correct, internally consistent, non-breaking, and a direct implementation of test 5's "unexpected new references cannot pass silently" requirement. One fixture directory it depended on had been deleted by this action's own earlier rollback drill (§4, first pass) and was restored with the content observed before deletion. Re-ran the full suite (43/43), re-verified live-rehearsal reconciliation (unchanged), re-verified file stability across a 15-second wait (sha256 unchanged), and re-executed the rollback drill against the final state (§4, second pass) before adopting it. §2b's ownership proof (added in this v3, responding to round 1's `P02-DELTA-OWNERSHIP-001`) is the load-bearing evidence that this adoption did not put any pre-existing content at risk. Recorded in the execution log at ACT-010.

Separately, round 1 of this QA gate itself found a stale, unrelated, pre-existing QA session at `checkpoints/P02/QA/` — opened at `2026-08-16T14:54:55Z` against `P02_checkpoint_report.v1.md` by a process other than this action (config used `transport=app-server` with empty `focus`/`grounding`, neither of which this action ever passed; it terminated `QA_ERROR: CODEX_TURN_FAILED — failed to load configuration`). `qa_gate.py`'s own `start` command auto-archived that terminal session to `deprecated/` when this action opened its own session against v2 (§6), per the script's documented behavior (`cmd_start`, `qa_gate.py` lines 857–864). This is independent confirmation that another process was operating on this same worktree during this run, consistent with §9's mutation discovery above.
