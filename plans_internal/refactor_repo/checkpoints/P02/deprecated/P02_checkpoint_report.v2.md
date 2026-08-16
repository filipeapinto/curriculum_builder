# P02 checkpoint report — Build and Prove the Syntax-Aware Import Codemod

**Prompt**: `plans_internal/refactor_repo/prompts/P02_import_codemod.prompt.v3.yaml` (version 3)
**Specification**: `plans_internal/refactor_repo/refactor_repository.spec.v8.html` (version 8)
**Baseline commit**: `967d702a3f569da6234ba115b2748ead76107619` ("refactor(repo): complete P01 packaging skeleton") — `git log -1 --format='%H'` run before any P02 action.
**Starting dirty state**: 3 pre-existing untracked paths (predate this run's journal, carried over unchanged from P01's checkpoint: `plans_internal/refactor_repo/prompts/resolved/deprecated/`, `plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1_modified.yaml`, `plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v2.yaml`). Confirmed via `git status --short --untracked-files=all` at ACT-001/002 (see execution log).
**Artifact version being judged**: this file, `P02_checkpoint_report.v2.md`.
**Supersedes**: `P02_checkpoint_report.v1.md` (retained on disk, not deleted). v1 documented the deliverable at an earlier point in this same run (33 files / 38 tests / 15 fixture cases); mid-run, before v1 was submitted to QA, this action discovered the tool/test/manifest had grown a further, coherent capability (§9) that v1's counts did not yet reflect. v2 documents the final state: 35 files / 43 tests / 16 fixture cases. No content in v1 was wrong about what it covered — the fixture matrix, transformer, and every test v1 described are unchanged and still pass; v2 adds the `unexpected_new_reference` postcondition capability and its evidence on top.

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

**`tests/refactor_repo/codemod/`** (34 files):

| path | purpose |
|---|---|
| `test_rewrite_runtime_imports.py` | pytest suite (43 tests) |
| `fixtures/fixtures_manifest.json` | 16-case fixture-class metadata |
| `fixtures/aliased_import/{before,after}.py` | fixture pair |
| `fixtures/already_migrated/{before,after}.py` | fixture pair |
| `fixtures/ambiguous_shadowed_param/{before,after}.py` | fixture pair |
| `fixtures/ambiguous_shadowed_reassign/{before,after}.py` | fixture pair |
| `fixtures/comment_non_target/{before,after}.py` | fixture pair |
| `fixtures/dotted_submodule_import/{before,after}.py` | fixture pair |
| `fixtures/dynamic_import_computed/{before,after}.py` | fixture pair |
| `fixtures/dynamic_import_literal/{before,after}.py` | fixture pair |
| `fixtures/from_import_aliased_module/{before,after}.py` | fixture pair |
| `fixtures/malformed_python/{before,after}.py` | fixture pair |
| `fixtures/mixed_old_new/{before,after}.py` | fixture pair |
| `fixtures/multiline_from_import/{before,after}.py` | fixture pair |
| `fixtures/relative_import_non_target/{before,after}.py` | fixture pair |
| `fixtures/simple_import/{before,after}.py` | fixture pair |
| `fixtures/string_literal_non_target/{before,after}.py` | fixture pair |
| `fixtures/unexpected_new_reference/{before,after}.py` | fixture pair (16th case, §9) |

(1 tool + 1 test module + 1 manifest + 16 fixture cases × 2 files = 35. `__pycache__/` under `tests/refactor_repo/codemod/` is gitignored — `.gitignore:8:__pycache__/` — and is not a deliverable.)

**Journal (authorized, self-describing):** `plans_internal/refactor_repo/execution/P02/execution_log.jsonl`, `.execution_log.counter.json`, `.execution_log.lock`.

**Checkpoint (authorized, this action):** `plans_internal/refactor_repo/checkpoints/P02/{P02_checkpoint_report.v1.md,P02_checkpoint_report.v2.md}` and everything the `qa-gate-codex-run` skill subsequently writes under `plans_internal/refactor_repo/checkpoints/P02/QA/`.

**Modified**: none. **Moved**: none. **Deleted**: none in the final state (two rollback drills, §4, deleted-then-restored the deliverable files transiently during this run; the working tree at the time this report was written contains all 35, byte-identical to their pre-rollback digests — see §4).

**Authorized-path conformance**: `git status --short --untracked-files=all`, captured after this report existed on disk (§6), shows every new/changed path falling under `tools/refactor_repo/rewrite_runtime_imports.py`, `tests/refactor_repo/codemod/`, `plans_internal/refactor_repo/checkpoints/P02/`, or `plans_internal/refactor_repo/execution/P02/{execution_log.jsonl,.execution_log.counter.json,.execution_log.lock}` — P02's exact `authorized_paths` — plus the 3 pre-existing untracked paths identified in §1, unchanged and outside this checkpoint's delta.

## 3. Test evidence (prompt tests 1–6; test 7 is the independent QA gate, §7)

### Test 1 — Resolved manifest grants exact non-overlapping mutation ownership

`prompt_manifest.resolved.v1.yaml` activates `P02` at version `3`, `status: active`, `path: plans_internal/refactor_repo/prompts/P02_import_codemod.prompt.v3.yaml`, `depends_on: [P01]`, `owns: [python_import_and_qualified_name_codemod_tooling]` — matching the executing prompt file exactly.

Command used to extract every active prompt's `authorized_paths:` block:
```
for f in plans_internal/refactor_repo/prompts/P0*.prompt.v3.yaml plans_internal/refactor_repo/prompts/generated/*.yaml; do
  echo "== $f =="
  awk '/^authorized_paths:/{flag=1; print; next} flag && /^[a-zA-Z]/{flag=0} flag' "$f"
done
```
Result: P02's two mutation-bearing entries (`tools/refactor_repo/rewrite_runtime_imports.py`, `tests/refactor_repo/codemod/`) do not appear, as a prefix or literal match, in any other active prompt's `authorized_paths` (P00's own prompt is `status: completed` with a QA_PASSED checkpoint, closed before P02 began — no live overlap; P02S: distinct filenames `tools/refactor_repo/rewrite_structured_references.py`, `tests/refactor_repo/structured_codemod/`; P03–P09: `runtime/`, `src/`, `tests/runtime/`, `tests/fixtures/…`, none under `tests/refactor_repo/codemod/`).

**One overlap-in-*declared-authorization-surface*, not in actual mutation, is recorded transparently**: the active `P02S` prompt (`plans_internal/refactor_repo/prompts/generated/P02S_structured_data_codemod.prompt.v4.yaml`) declares wildcard `authorized_paths` entries `"*.json"`, `"*.yaml"`, `"*.yml"` broad enough to also textually match `tests/refactor_repo/codemod/fixtures/fixtures_manifest.json`. This is a pre-existing characteristic of the P02S v4 prompt (outside P02's `authorized_paths` to edit), and has produced **zero actual overlapping mutation**: P02S `depends_on: [P02]` (runs after this checkpoint), P02's diff never touches TOML/JSON/YAML *identity* content (P02S's real `owns` grant), and `fixtures_manifest.json` carries no old/new-identity strings. Recorded as a residual observation for P02S's own author — not a P02 blocker.

Every unit this checkpoint's diff actually touches (the 35 files in §2, all Python-import-codemod tooling/tests/fixtures) is owned by P02 exactly once. **PASS.**

### Test 2 — Fixture matrix covers every required transformation class

Command: `python3 -m pytest tests/refactor_repo/codemod/test_rewrite_runtime_imports.py::test_fixture_matrix_covers_every_required_class -q`
```
1 passed in <1s
```
`fixtures_manifest.json` tags 16 cases across the classes: `import`, `module_qualified_name`, `aliased_import`, `multiline_import`, `from_import`, `preserved_comments_formatting`, `strings`, `dynamic_imports`, `ambiguous_references`, `already_migrated`, `malformed_input`, `mixed_old_new_qualified_names`, `explicit_non_target`, `unexpected_new_reference` — a strict superset of the prompt's required set. Every case has an `expect_diagnostic_kinds` list (a named diagnostic) or is explicitly a documented no-op. Comments and ordinary strings are asserted byte-identical where the prompt requires it. **PASS.**

### Test 3 — Dry-run is deterministic, reviewable, and write-free

Command: `python3 -m pytest tests/refactor_repo/codemod/test_rewrite_runtime_imports.py -k "dry_run" -q`
```
3 passed in <2s
```
`test_dry_run_is_deterministic_across_repeated_calls`, `test_dry_run_cli_never_writes_input_files`, `test_dry_run_cli_diff_is_byte_identical_across_two_runs`. **PASS.**

### Test 4 — Apply mode produces exact fixtures and is idempotent

Command: `python3 -m pytest tests/refactor_repo/codemod/test_rewrite_runtime_imports.py -k "apply_mode" -q`
```
8 passed in <2s
```
`test_apply_mode_matches_fixture_and_is_idempotent`, parametrized over the 8 fixture cases expected to change: first apply matches `fixtures/<name>/after.py` exactly; second apply is a byte-identical, zero-`files_changed` no-op, read directly from the tool's own diagnostics report. **PASS.**

### Test 5 — Unsafe and residual references fail closed

Command: `python3 -m pytest tests/refactor_repo/codemod/test_rewrite_runtime_imports.py -k "unsafe or residual or malformed or shadowed or unexpected_new" -q`
```
13 passed in <3s
```
- `dynamic_import_literal` / `dynamic_import_computed` / `malformed_python`: as in v1 (§3 test 5 evidence unchanged — `dynamic_import_literal` warning, content unchanged; `dynamic_import_unresolvable` unsafe, file unchanged; `parse_error` unsafe, no crash, file unchanged).
- `ambiguous_shadowed_param` / `ambiguous_shadowed_reassign`: shadowed identifier never renamed, `non_target_shadowed` diagnostic present.
- `mixed_old_new`: both `runtime`/`curriculum_factory` imports resolve to `curriculum_factory`; `duplicate_import_after_rewrite` warning (not blocking).
- `scan_residuals()`: zero `residual_old_reference` findings on clean post-rewrite output; at least one on unmigrated input; never misreports a shadowed local.
- **New in v2** — `scan_residuals(..., check_unexpected_new_root=True)` and the CLI `--check-unexpected-new-root` flag (`postcondition-scan` mode): on the new `unexpected_new_reference` fixture (an import-bound `curriculum_factory` reference with no corresponding rewrite having occurred), both the in-process API and the CLI report an `unexpected_new_reference` diagnostic (`severity=blocker`) when the flag is enabled, and report nothing when it is disabled (default, backward-compatible with every pre-existing call site) — `test_postcondition_scan_reports_unexpected_new_root_references_when_enabled`, `test_postcondition_scan_ignores_unexpected_new_root_when_disabled`, `test_postcondition_scan_cli_with_check_unexpected_new_root_flag` (asserts `returncode != 0` with the flag), `test_postcondition_scan_cli_without_flag_ignores_unexpected_new_root` (asserts `returncode == 0` without it) — all 4 passed. This directly implements the prompt's test 5 language "unexpected new references cannot pass silently" as an opt-in, explicit check a successor prompt (P03+) can run after each of its own mutation passes. **PASS.**

### Test 6 — Live repository rehearsal is dry-run only

Command:
```
python3 -m tools.refactor_repo.rewrite_runtime_imports dry-run \
  --root runtime --root tests/runtime --root tests/gates \
  --repo-root . \
  --diagnostics-out /tmp/p02_live_final.json \
  --diff-out /tmp/p02_live_final.diff
```
```
exit=0
{'files_parse_error': 0, 'files_scanned': 94, 'files_unsafe': 0, 'files_would_change': 33}
Counter({'rewrite_import': 163, 'non_target_shadowed': 10})
```
Re-run against the final (35-file) tool version; identical to the count reported under v1 (the new capability is additive and opt-in, so it does not change dry-run's default behavior).

- **Candidate-count reconciliation with P00**: `plans_internal/refactor_repo/inventory/20260816_074507/repository_refactor_inventory.20260816T114511Z.v1.json` → `python_surface.runtime_imports` length `163` == live `rewrite_import` count `163`, exactly. Candidate file set is set-equal (asserted in `test_live_dry_run_rehearsal_reconciles_with_p00_and_writes_nothing`) to P00's 33 unique `source_file` values.
- **The 10 `non_target_shadowed` findings, explained** (correctly excluded, none in the P00 count): `runtime/langgraph_factory/graph.py:375` (`def node(state: ..., runtime: Runtime[RuntimeContext])`, LangGraph's own `Runtime` type) and `:376` (`getattr(runtime, "context", None)`); `runtime/session_bridge.py:54,55,56,57,58,68,78` (`runtime = CurriculumRuntime(engine)` local instance and its uses in `prepare()`); `tests/runtime/test_plan26_topology.py:265` (`def _placeholder_node(state, runtime): # pragma: no cover`). Read directly at each site to confirm.
- **Zero unsafe findings** on the real tree; the 4 unsafe/2-parse-error/2-dynamic-import diagnostics observed in an earlier unscoped full-repo run all traced to this checkpoint's own deliberately adversarial fixtures (excluded once the rehearsal was scoped to `runtime/`+`tests/runtime/`+`tests/gates/`, matching P00's own scan scope).
- **Write-freedom**: `git status --short` non-`??` line count was `0` both before and after this invocation. **PASS.**

**Discovered pre-existing defect (out of P02 scope, not a P02 test failure)** — unchanged from v1: `tools/refactor_repo/collectors.py`'s `DIRECTORY_CLASSIFICATION` table (P00-owned, not in P02's `authorized_paths`) has no entry for the top-level `src/` directory P01 created, so `python3 tools/refactor_repo/inventory.py` now exits `1` (`CollectorUnavailable: unresolved top-level directory: 'src'`, swallowed into an invalid empty `directories: []` report). Reproduced directly via `collectors.collect_directories(Path('.').resolve())`. A P01-introduced regression in a P00-owned file, confirmed unrelated to any P02 change, out of scope to fix here, and not a P02 blocker since none of P02's 6 local tests invoke `inventory.py` (the live-rehearsal test reads the already-generated static P00 JSON artifact from disk).

## 4. Rollback checkpoint (actually executed twice, not merely analyzed)

The rollback drill was executed **twice** in this run: once against the 33-file/38-test state (before the §9 discovery), and again against the final 35-file/43-test state, to prove rollback still holds after the deliverable grew.

Final-state literal commands and results:
```
mkdir -p /tmp/p02_rollback_backup2
cp tools/refactor_repo/rewrite_runtime_imports.py /tmp/p02_rollback_backup2/
cp -R tests/refactor_repo/codemod /tmp/p02_rollback_backup2/codemod
find tools/refactor_repo/rewrite_runtime_imports.py tests/refactor_repo/codemod -type f -not -path "*__pycache__*" | sort | xargs shasum -a 256 > /tmp/p02_pre_rollback_digests2.txt
# 35 lines
rm -f tools/refactor_repo/rewrite_runtime_imports.py
rm -rf tests/refactor_repo/codemod
git status --short --untracked-files=all
# ?? plans_internal/refactor_repo/checkpoints/P02/P02_checkpoint_report.v1.md
# ?? plans_internal/refactor_repo/execution/P02/.execution_log.counter.json
# ?? plans_internal/refactor_repo/execution/P02/.execution_log.lock
# ?? plans_internal/refactor_repo/execution/P02/execution_log.jsonl
# ?? plans_internal/refactor_repo/prompts/resolved/deprecated/prompt_manifest.resolved.v1.yaml
# ?? plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1_modified.yaml
# ?? plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v2.yaml
shasum -a 256 plans_internal/refactor_repo/inventory/20260816_074507/repository_refactor_inventory.20260816T114511Z.v1.json
# 28ae20d5671358e0777d1dc5e3e73df43a8aa5dcd1e4e30dd0333f9ced897314  (unchanged before/after)
python3 -m pytest tests/refactor_repo/test_packaging_skeleton.py -q
# 13 passed in 0.01s
cp /tmp/p02_rollback_backup2/rewrite_runtime_imports.py tools/refactor_repo/rewrite_runtime_imports.py
mkdir -p tests/refactor_repo
cp -R /tmp/p02_rollback_backup2/codemod tests/refactor_repo/codemod
find tools/refactor_repo/rewrite_runtime_imports.py tests/refactor_repo/codemod -type f -not -path "*__pycache__*" | sort | xargs shasum -a 256 > /tmp/p02_post_restore_digests2.txt
diff /tmp/p02_pre_rollback_digests2.txt /tmp/p02_post_restore_digests2.txt
# (zero output: byte-identical restore of all 35 files)
python3 -m pytest tests/refactor_repo/codemod/test_rewrite_runtime_imports.py -q
# 43 passed in 39.73s
```
Rollback is exercisable and reversible against the final deliverable state; restored content is byte-for-byte identical to the pre-rollback state, the full P02 test suite re-passes, P00's inventory artifact digest is untouched, and P01's own test suite is unaffected. Both backup directories (`/tmp/p02_rollback_backup`, `/tmp/p02_rollback_backup2`) removed after verification (outside the repository, not deliverables).

## 5. Residuals

| residual | classification | disposition |
|---|---|---|
| `libcst==1.8.2` is not recorded in `requirements/plan26.in`/`.lock` | recorded exception (out of P02 `authorized_paths`) | Formalize in a requirements-owning prompt (P02S or a maintenance pass); enforced meanwhile by an in-tool version assertion (§1) |
| P02S v4's `"*.json"`/`"*.yaml"`/`"*.yml"` wildcard `authorized_paths` textually cover `fixtures_manifest.json` | recorded observation, zero actual overlapping mutation | Out of P02 scope; flagged for P02S's own author |
| `tools/refactor_repo/collectors.py`'s `DIRECTORY_CLASSIFICATION` has no entry for `src/` (P01-introduced, P00-owned) | pre-existing blocker, out of P02 `authorized_paths` | Not a P02 blocker; recorded for a future P00-owning maintenance pass |
| No genuine dynamic-import-of-`runtime` or malformed-Python file exists in the live `runtime/`/`tests/` tree | confirmed resolved | none — informational |
| Zero `rewrite_reference` (bare qualified-name usage) diagnostics in the live tree | confirmed resolved | none — informational; explains 163 `rewrite_import` + 0 `rewrite_reference` accounting for all 163 P00-counted statements |
| `--check-unexpected-new-root` is opt-in (default `False`) and not yet invoked by any successor prompt | by design in this checkpoint | A successor (P03+) should run `postcondition-scan --check-unexpected-new-root` after each of its own mutation passes; not P02's job to invoke against files it does not own |

No old (`runtime`) residual reference and no unexpected new (`curriculum_factory`) reference passes silently: `scan_residuals()` is exercised against both migrated and unmigrated content, and its `check_unexpected_new_root` mode (§3 test 5, §9) closes the "unexpected new reference" half of that requirement explicitly rather than by inference.

## 6. Post-change git status and reviewable diff

Captured via `git status --short --untracked-files=all`, run **after** this report (`P02_checkpoint_report.v2.md`) existed on disk, immediately before submission to `qa-gate-codex-run`:

```
?? plans_internal/refactor_repo/checkpoints/P02/
?? plans_internal/refactor_repo/execution/P02/
?? plans_internal/refactor_repo/prompts/resolved/deprecated/
?? plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1_modified.yaml
?? plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v2.yaml
?? tests/refactor_repo/codemod/
?? tools/refactor_repo/rewrite_runtime_imports.py
```

Zero tracked (`M `/` M`) lines — every P02 path is newly created. Every individual file under `plans_internal/refactor_repo/checkpoints/P02/` and `plans_internal/refactor_repo/execution/P02/` at the time of this capture:

```
plans_internal/refactor_repo/checkpoints/P02/P02_checkpoint_report.v1.md
plans_internal/refactor_repo/checkpoints/P02/P02_checkpoint_report.v2.md
plans_internal/refactor_repo/execution/P02/.execution_log.counter.json
plans_internal/refactor_repo/execution/P02/.execution_log.lock
plans_internal/refactor_repo/execution/P02/execution_log.jsonl
```

Rollback-checkpoint verification result: **PASS** (§4 — delete/verify/restore cycle actually executed twice, restored digests byte-identical both times, dependent test suite unaffected).

## 7. Independent QA gate (test 7)

Not yet run at the time this v2 was written to disk. To be gated with `qa-gate-codex-run`, criteria `plans_internal/refactor_repo/prompts/checkpoint_qa_criteria.v1.md`, grounding this prompt plus P00 evidence plus `refactor_repository.spec.v8.html`, threshold `blocker`, at most 5 iterations. This report will not be represented as complete until that gate records a witnessed, verified `QA_PASSED`.

## 8. Non-claims

This report does not claim: that `libcst` is repo-pinned in a requirements file (it is not — §1, §5); that the P00 inventory tool currently runs successfully (it does not, for reasons unrelated to P02 — §3 test 6, §5); that P02S's wildcard authorization has been narrowed (it has not — §5); or that `--check-unexpected-new-root` has been invoked against the live repository by this checkpoint (it has not — it is a capability for successor prompts to use, exercised here only against fixtures — §5, §9). It claims exactly what §3's six tests demonstrate with reproducible commands and exit statuses, and defers completion to the independent QA gate in §7.

## 9. Mid-run discovery and reconciliation (transparency note)

While preparing this checkpoint (after v1 was written but before it was submitted to QA), an `Edit` tool call on `tools/refactor_repo/rewrite_runtime_imports.py` failed with "File has been modified since read," indicating the file had changed since this action last read it. Investigation found `tools/refactor_repo/rewrite_runtime_imports.py`, `tests/refactor_repo/codemod/test_rewrite_runtime_imports.py`, and `fixtures/fixtures_manifest.json` had each grown a coherent, mutually-consistent extension beyond what this action had itself most recently written: a `check_unexpected_new_root` parameter on `scan_residuals()` (default `False`, fully backward-compatible), a matching `--check-unexpected-new-root` CLI flag on `postcondition-scan` mode, a 16th fixture case (`unexpected_new_reference`), and 4 new tests exercising both the API and the CLI surface of the addition.

This action could not determine with certainty how this change was introduced (no `Edit`/`Write` call for it appears in this action's own tool-call history), but reviewed it in full (§3 test 5, §9 above), found it correct, internally consistent across all four touched files, non-breaking to every pre-existing test and behavior, and a direct, faithful implementation of a requirement this prompt's own test 5 states explicitly ("unexpected new references cannot pass silently") that this action's own v1 design had covered only by argument, not by a dedicated mechanism. One fixture directory the addition depended on had been deleted by this action's own earlier rollback drill (§4, first pass, which predates this discovery) and was restored with the content observed before deletion. This action then re-ran the full test suite (43/43 pass), re-verified live-rehearsal reconciliation (unchanged: 163/163, 33/33 files), re-verified file-content stability across a 15-second wait (three sha256 digests unchanged), and re-executed the full rollback drill against this final state (§4, second pass) before adopting it into this checkpoint. Recorded in `plans_internal/refactor_repo/execution/P02/execution_log.jsonl` at ACT-010.
