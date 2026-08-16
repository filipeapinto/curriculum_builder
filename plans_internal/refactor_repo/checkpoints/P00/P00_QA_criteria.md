# P00 QA Criteria: Inventory Baseline and Behavioral Capture

## Goal
Verify that P00 has created a reproducible, schema-compliant repository inventory and behavioral baseline.

## Critical (Blocker) Criteria

1. **Authorization Boundary Respected**
   - Zero unauthorized paths written outside of:
     - `tools/refactor_repo/`
     - `schemas/repository_refactor_inventory.schema.v1.json`
     - `tests/refactor_repo/test_inventory.py`
     - `plans_internal/refactor_repo/inventory/`
     - `plans_internal/refactor_repo/baseline/`
     - `plans_internal/refactor_repo/checkpoints/P00/`
     - `plans_internal/refactor_repo/execution/P00/` (specific files only)
     - `failed_execution_evidence/`
   - **NO** `plans_internal/plans_internal/` nested paths.
   - git status must show only authorized untracked files.

2. **All Tests Pass**
   - All 16 tests in `tests/refactor_repo/test_inventory.py` must exit code 0.
   - Tests include: inventory read-only verification, schema validation, machine/human report equivalence, baseline capture/compare, fault injection.

3. **Inventory Completeness**
   - Inventory JSON must validate against `schemas/repository_refactor_inventory.schema.v1.json`.
   - `complete` field must be `true`.
   - `omissions` array must be empty.
   - `collection_failures` array must be empty.
   - Covers all top-level directories, Python imports, structured config, test subtrees, schema identifiers.

4. **Baseline Capture Success**
   - Baseline capture must exit code 0.
   - Output file must exist and be valid JSON.
   - `existing_failures` array must be empty.
   - Baseline must be re-executable (Test 14: baseline_capture_and_compare_are_equivalent_on_unchanged_repo passes).

5. **Checkpoint Integrity**
   - Checkpoint JSON must include: `phase`, `title`, `timestamp`, `inventory`, `baseline`, `tests`, `completion_gates`.
   - `completion_gates` object must show all gates passing:
     - `valid_journal: true`
     - `zero_unclosed_starts: true`
     - `all_tests_pass: true`
     - `authorized_paths_only: true`

## Major Criteria

6. **Inventory-Baseline Consistency**
   - Baseline was captured from the same git commit as inventory.
   - Baseline contains the same repository state as inventory describes.

7. **Rollback Capability**
   - All authorized outputs can be deleted without corrupting the repository.
   - `git reset --hard` returns repo to clean state at the same commit.

## Success Condition
All blocker criteria must pass (exit 0). One major criterion failure is acceptable (exit 0 if all blockers pass).
