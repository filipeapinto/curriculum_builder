# P03 checkpoint report — Move Production Source and Rewrite Runtime Imports

## 1. Identification

- Prompt: `plans_internal/refactor_repo/prompts/P03_source_move.prompt.v3.yaml`
- Baseline commit (t0): `ccacad34ef5a11cf7d05dea3c62612893a60cf7d` (P02S checkpoint, QA_PASSED)
- Execution worktree: `/Users/filipepinto/Projects/curriculum_builder_wt/refactor-p03-p10-direct`, branch `refactor-p03-p10-direct`
- Execution journal: `plans_internal/refactor_repo/execution/P03/execution_log.jsonl` (ACT-001..ACT-010, zero unclosed starts)
- Exceptions/residuals: `plans_internal/refactor_repo/exceptions/source_move.v1.yaml`

## 2. Changed / created paths and authorized-path conformance

`git status --porcelain` after the full P03 delta touches only:

- `runtime/**` (69 files deleted — moved out)
- `src/curriculum_factory/**` (69 files added/modified — moved in, plus 5 production-code path/identity fixes)
- `tests/runtime/**` (30 files codemod-rewritten; 8 of those additionally hand-fixed for mock/path/subprocess residuals the codemod cannot see)
- `tests/gates/fr_p5_unit.py` (no functional change; scanned, zero candidates)
- `plans_internal/refactor_repo/exceptions/source_move.v1.yaml` (new)
- `plans_internal/refactor_repo/checkpoints/P03/**`, `plans_internal/refactor_repo/execution/P03/**` (this checkpoint's own evidence)

No file outside these authorized_paths is staged. Two classes of test-run-induced drift outside authorized_paths (`plans/26_langgraph_curriculum_factory/results/evidence/N40_CLI_CUTOVER/*.txt`, nondeterministic tmp-path content written by an unrelated pre-existing test) were detected and reverted twice (once before mutation, once after the rollback rehearsal); confirmed absent from the final `git status`.

## 3. Test evidence (prompt tests 1–6; test 7 is the independent QA gate, §7)

### Test 1 — Resolved manifest grants exact non-overlapping mutation ownership

`prompts/resolved/prompt_manifest.resolved.v1.yaml` activates `P03_source_move.prompt.v3.yaml`. P03's authorized_paths (`runtime/`, `src/curriculum_factory/`, `tests/runtime/`, `tests/gates/fr_p5_unit.py`, `tests/check_meta_prompt.py`, `tests/meta_prompt_source.py`, `plans_internal/refactor_repo/exceptions/source_move.v1.yaml`, its own checkpoints/execution dirs) are disjoint from every other active prompt's declared paths per the same ownership-comparison method P02's `test1_ownership_check.py` established (P00/P01/P02/P02S own packaging/codemod-tool paths only; P04+ own resource/root, fixtures, schema, docs, release, test-tree, and rename paths, none of which overlap `src/curriculum_factory/` content mutation). The actual diff (§2) touches exactly this set and nothing else.

### Test 2 — Prerequisites and pre-move source map reconcile exactly

P01 (packaging skeleton, commit `967d702`) and P02 (import codemod, commit `d35aea3`) are both witnessed QA_PASSED and remotely checkpointed ancestors of `ccacad3`. Before the first move: captured `runtime/` file inventory and sha256 digest manifest (69 tracked files; `checkpoints/P03/baseline/t0/runtime_tree_sha256_t0.txt`), and ran P02's `rewrite_runtime_imports.py dry-run` reconciliation implicitly via the apply-then-verify sequence in §Test 4. Zero ambiguous transformation was found (0 `unsafe` diagnostics in either apply pass; see `codemod_diag_apply.*.json`).

### Test 3 — Source relocation preserves the complete production tree

`git mv` moved all 69 git-tracked `runtime/` files 1:1 to `src/curriculum_factory/`, preserving subpackage boundaries (`langgraph_factory/`, `langgraph_factory/nodes/`, `langgraph_factory/config/`, `langgraph_factory/prompts/`, `langgraph_factory/schemas/`) and non-Python resource-relative layout (`.mjs`, `*.prompt.md`, `*.schema.json`, `model_jobs.v1.yaml`). Verified: `git ls-files runtime/` → 0; `git ls-files src/curriculum_factory/` → 69; `find runtime -type f` (excluding the now-removed `__pycache__`) → none; the placeholder `src/curriculum_factory/__init__.py` (P01's `__all__ = []` skeleton) was replaced by the real moved `__init__.py`. No file was duplicated or omitted; `runtime/` was removed entirely once empty.

### Test 4 — Codemod application is complete and idempotent

Applied `tools/refactor_repo/rewrite_runtime_imports.py apply` to the authorized live surface:

```
# src/curriculum_factory/: files_changed=3 (evidence.py, persistence.py, run_curriculum.py),
#   files_scanned=47, files_parse_error=0, files_unsafe=0
# tests/runtime/ + tests/gates/fr_p5_unit.py + tests/check_meta_prompt.py + tests/meta_prompt_source.py:
#   files_changed=30, files_scanned=37, files_parse_error=0, files_unsafe=0
```

Second apply on the same roots: `files_changed=0` (84 files scanned) — idempotent.

Repo-wide `postcondition-scan --root .`: `files_scanned=263, files_with_residuals=33, residual_count=52`. Every residual is recorded with exact consumer/rationale/removal in `plans_internal/refactor_repo/exceptions/source_move.v1.yaml`: 9 P02 codemod-tool `before.py` fixtures + 2 `malformed_python` fixtures (intentional test input, owned by P02, permanent), 39 references across 21 files under `plans/26_.../evidence/` and `plans/27_.../execution_package_v2/` (frozen historical plan evidence, `plans/` never in P03's authorized_paths, must not be mutated), 1 reference in `plans_internal/refactor_repo/deprecated/phrase_rebrand_v1/` (deprecated asset), and 1 live functional residual at `tools/refactor_repo/baseline.py:137` (P00-owned, outside P03's authorized_paths — see §5).

Beyond the codemod's own scope (imports/qualified-names only, by design never string literals), a manual audit of every remaining textual `"runtime"` occurrence in the moved/authorized surface found and fixed five real functional bugs the codemod cannot see, all within `src/curriculum_factory/`:

1. `run_curriculum.py:65` — `PROG` constant (`"python3 -m runtime.run_curriculum"` → `"...curriculum_factory..."`), which drives the CLI's observable `--help`/error `prog` text.
2. `langgraph_factory/graph.py` — `PRODUCTION_BINDING_MODULES`, a load-bearing `__module__` allowlist gating which callables may supply a production node body; unfixed, every real node would be rejected post-move with `GraphBindingError`.
3. `run_curriculum.py:302` — `_capability_forbidden_paths()`'s `engine_root / "runtime"` → `engine_root / "src" / "curriculum_factory"`.
4. `session_bridge.py:97` and `curriculum_factory_graph.py:332` — `(engine / "runtime").glob("*.py")` → `(engine / "src" / "curriculum_factory").glob("*.py")`.
5. `capability_cycle.py:71` and three `finalize_evidence.py` literals — path/script-invocation text mechanically repointed to `src/curriculum_factory/...`.

And in `tests/runtime/` (mock targets, `__module__` comparisons, hardcoded static-inspection paths, and subprocess-child `sys.path`/import setups the codemod's import/qualified-name scope does not cover): 12 files fixed (`test_plan26_unit_graph.py`, `test_plan26_cli.py`, `test_plan26_workbook.py`, `test_plan26_persistence.py`, `test_run_curriculum.py`, `test_plan26_adversarial.py`, `test_plan26_topology.py`, `test_plan26_transport.py`, `test_plan26_state_reducers.py`, `test_curriculum_factory_graph.py`, `test_gemini.py`, plus the `LOCK_CHILD`/`ORPHAN_GRAPH_CHILD` subprocess scripts in `test_plan26_persistence.py`/`test_plan26_adversarial.py`).

### Test 5 — Installed imports and module origins use only curriculum_factory

Built a wheel (`python3 -m build --wheel`) from the moved tree and installed it into a fresh, isolated throwaway venv (`/tmp/p03_venv`, verified zero contamination from any pre-existing system-wide install). From repository root, `tests/runtime/`, and an external `/tmp` working directory:

```
curriculum_factory /private/tmp/p03_venv/lib/python3.13/site-packages/curriculum_factory/__init__.py
run_curriculum      .../site-packages/curriculum_factory/run_curriculum.py
graph                .../site-packages/curriculum_factory/langgraph_factory/graph.py
OK: resolves from installed distribution, not checkout
OK: runtime import fails as expected: No module named 'runtime'
```
(identical `site-packages` resolution repeated from `tests/runtime/` and `/tmp`). Confirmed via `pip show curriculum-factory`: non-editable install, `Location: .../p03_venv/...`.

### Test 6 — CLI interface matches the P00 baseline at the mechanical boundary

`curriculum-factory-run-curriculum --help` and `python3 -m curriculum_factory.run_curriculum --help` are byte-identical to each other; both exit 0. Compared against the t0 capture (`baseline/t0/behavioral_baseline...json`, `cli_help_and_invalid_input`): same flag set (`--engine-root`, `--curriculum`, `--output-root`, mutually-exclusive `--preflight|--unit|--all|--resume`, `--authorization`), same descriptions, same mutual-exclusion grouping; only the `prog=` string changed to the target identity (intended — see Test 4 item 1), which reflows argparse's usage-line wrapping (expected, cosmetic). No-args and `--engine-root x` both exit 2 with the same "missing required arguments" class of error, prog string updated accordingly.

### Test 7 — Regression delta is confined to predeclared/root-caused failures

Full baseline methodology (§ full detail in `checkpoints/P03/baseline/t0/` and `checkpoints/P03/t1/`):

- **t0** (before any P03 mutation, checkout via `python3 -m pytest -q tests/`, system Python): `80 failed, 1399 passed, 2 skipped, 9 errors, 419 subtests passed`. Independently re-verified byte-identical in a fully isolated venv + a separate throwaway worktree pinned at `ccacad3` (ruling out contamination from an unrelated system-wide editable install of `curriculum-factory` that points at a different, preserved dirty worktree — see `t1/pytest_full_t1.log` notes and ACT-008).
- **t1** (after the full move + all fixes above, installed-distribution venv per Test 5): `115 failed, 1364 passed, 2 skipped, 9 errors, 419 subtests passed`.
- Diff (`comm -13`/`comm -23` on sorted FAILED/ERROR id sets): **0 previously-passing test regressed unexplained; 35 new FAILED/ERROR ids**, every one individually root-caused and classified in `source_move.v1.yaml`:
  - **5**: checkpoint-scoped P01/P02 self-tests whose "as of this checkpoint, `runtime/` must still exist" assertions are the intended, causally demonstrated consequence of P03 completing its declared goal (`test_packaging_skeleton.py`×3, `test_rewrite_runtime_imports.py`×1), plus the already-disclosed `tools/refactor_repo/baseline.py:137` P00-owned live-import break (`test_inventory.py`×1). None are in P03's authorized_paths to fix.
  - **29**: the installed-distribution resource-root class P03's own goal statement explicitly hands to P04 ("isolate semantic root/resource repair for P04") — proven by direct invocation that `curriculum_factory.langgraph_factory.nodes.sources.D07_CORRELATE_AND_ADMIT_SOURCES` succeeds when `engine_root` is the real checkout, and only fails when `REPO_ROOT`/`CURRICULA_ROOT`/policy paths are computed as `Path(installed_package.__file__).resolve().parents[N]`, which lands inside `site-packages` once truly installed (a condition t0 never exercised either, since t0 never ran installed).
  - **1**: frozen Plan 26 harness evidence (`plans/26_.../implementation.graph.v3.yaml`, outside authorized_paths) correctly detecting that its tracked `state.py`/`reducers.py` path moved — same root-cause class as the archived-plan-evidence residual.

No test was weakened to reach this result; every fix in Test 4 was a genuine bug fix verified by rerunning the full suite (135→115 failed after the fixes, i.e. 20 real regressions eliminated), not a suppression.

## 4. Rollback checkpoint (actually executed, not merely analyzed)

`git stash push -u` → `git status --porcelain` empty, `git diff --stat HEAD` empty, `runtime/` physically restored with exactly 69 files (`git ls-files runtime/` == 69) — byte-identical to the `ccacad3` checkpoint. `git stash pop` → `src/curriculum_factory/` back to exactly 69 files, `runtime/` physically absent again, zero content loss (verified by direct file count, not just status). The round-trip left a harmless git rename-pair-detection cosmetic artifact (some entries showed as `D`+`A` instead of `R`) and re-surfaced the two already-known unrelated test-run side-effect classes (`plans/26_.../evidence/*.txt` drift, and three `tests/runtime/*.py` files that are genuine, already-accounted-for members of the Test 4 codemod pass) — both confirmed harmless and the former reverted again.

## 5. Residuals

Full detail: `plans_internal/refactor_repo/exceptions/source_move.v1.yaml` (5 categories, 52 postcondition-scan diagnostics + the 3 checkpoint-obsolescence tests + the 29-test resource-root class + the 1 frozen-harness test, all classified with consumer/rationale/removal/owner). Summary: nothing in this list is fixable within P03's authorized_paths; each is either permanent/intentional, archival, or explicitly owned by a named successor prompt (P04) or an unassigned out-of-manifest owner.

## 6. Non-claims

P03 does not claim: resource/root-relative loading correctness under true installation (P04's job by the prompt's own goal statement); retirement of P01/P02's now-superseded checkpoint self-tests (outside authorized_paths); reconciliation of frozen Plan 26/27 archival evidence (outside authorized_paths, and rewriting archives would falsify history); a fix for `tools/refactor_repo/baseline.py`'s now-broken `runtime.io` import (P00-owned, outside authorized_paths).

## 7. Independent QA gate (test 7)

Pending — submitted to `qa-gate-codex-run` after this report; results recorded under `checkpoints/P03/QA/`.
