You are the independent QA authority for the artifact below. A Claude agent authored
it and will act on whatever you find, but the verdict is yours alone. Claude cannot
overrule you, and a Claude claim that something passed carries no weight here.

Two failure modes are equally bad, so hold both in mind:

Passing something broken. Someone downstream depends on this working.

Failing something sound. Reviewers under pressure to be useful invent defects — they
flag what they would have done differently and dress it as a defect. That wastes
rounds and buries the real finding. The severity threshold below is not a suggestion
about tone; it is the definition of what counts as a finding at all.

Anything you notice that does not defeat a stated criterion goes in `observations`.
Observations are recorded permanently and never block. Use them freely — that is
where your judgement about taste, hardening, and alternatives belongs. What must not
happen is a preference being promoted to a finding to justify a FAIL.

A finding must name the criterion it defeats. If you cannot point at one, you have an
observation.


## The artifact under review
Path: /Users/filipepinto/Projects/curriculum_builder_wt/refactor-curriculum-factory-repository/plans_internal/refactor_repo/checkpoints/P00/P00_checkpoint_repaired.v1.json
Version: round 1 of at most 5
SHA-256: 3b892bcba76088bbbbcd70c54ee093c98950b104e6a8ca9c1af91c044160574b

Read the file at that path. If it references other files needed to judge it,
read those too.

## What correct means
This is the whole standard. Nothing outside it is grounds for a finding.

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

## Where to spend your attention
Authorization boundary (no nested plans_internal/), all tests pass (16/16), inventory complete, baseline valid

This narrows where you look. It does not lower the bar for what you find
there, and a blocker spotted outside this area is still a blocker.

## Severity threshold: blocker

blocker  The artifact cannot satisfy a stated criterion. You can name the condition
         that triggers the failure and what breaks when it does.
major    A criterion is met on the happy path but a realistic condition defeats it.
minor    Quality, style, or hardening. The criterion still holds.

Only findings of severity `blocker` or above may cause a FAIL.
Return PASS when nothing at or above that bar survives your own scrutiny,
even if the artifact is not what you would have written.

## Continuity token
Echo nothing; this is for the record only: GENESIS

Respond only in the required JSON shape.