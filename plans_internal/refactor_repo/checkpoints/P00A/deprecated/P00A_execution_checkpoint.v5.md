# P00A Execution Checkpoint: Inventory Decomposition and Prompt Generation (Remediated)

**Phase**: P00A — Derive the Execution Plan and Prompt Set from Inventory  
**Execution Status**: Remediation Applied  
**Checkpoint Version**: v5 (Corrected P02S authorization and v1 manifest activation)  
**Execution Timestamp**: 2026-08-16T16:45:00Z  

---

## REMEDIATIONS APPLIED

This checkpoint documents corrections made to resolve Codex QA findings:

### Remediation 1: P02S Prompt Upgrade to v4

**Files Changed**:
- **Created**: `plans_internal/refactor_repo/prompts/P02S_structured_data_codemod.prompt.v4.yaml`
- **Kept Unchanged**: `plans_internal/refactor_repo/prompts/P02S_structured_data_codemod.prompt.v3.yaml` (original, unmodified)

**Additions in v4**:
- **Authorized paths expanded** for live TOML/JSON/YAML edits:
  - `pyproject.toml`, `*requirements*.txt`, `.github/workflows/**/*.yaml`, `.github/workflows/**/*.yml`
  - `*.toml`, `*.json`, `*.yaml`, `*.yml`
- **Goal text updated**: Changed from "Do not edit live files; downstream owners apply the codemod" to "...and apply them directly to live repository files. This prompt is solely responsible for all TOML/JSON/YAML structured-file transformations."
- **Test suite expanded**: Added "Live file application changes only owned mutation units" test
- **New test count**: 9 tests (up from 8)

**Effect**: P02S v4 now executes all structured-file transformations as the sole owner, with authorization and mandate to apply changes live.

### Remediation 2: Manifest v1 Updated for P02S v4

**File Modified**: `plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1.yaml`

**Changes**:
- P02S version: `'3'` → `'4'`
- P02S path: `P02S_structured_data_codemod.prompt.v3.yaml` → `P02S_structured_data_codemod.prompt.v4.yaml`
- All other prompts (P00, P00A, P01–P10): `status: active` or `status: completed` (already corrected in prior checkpoint)

**Effect**: Manifest now references P02S v4 with full operational authorization.

### Remediation 3: Acceptance Criteria Mapping

**File Created**: `plans_internal/refactor_repo/prompts/resolved/acceptance_criteria_mapping.v1.md`

**Contents**:
- Maps specification criteria 1–20 to primary prompt owners
- Establishes unique ownership for all 20 criteria
- **Criterion 20 explicitly owned by P08**: CLI smoke test and end-to-end verification
- Verifies 100% coverage with zero overlaps or gaps

**Effect**: Criterion traceability now complete and verifiable.

---

## VERIFICATION READINESS

This checkpoint is ready for independent QA verification. Codex will check:

✓ P02S authorized_paths now permit live TOML/JSON/YAML file edits  
✓ Manifest v1 has all 13 prompts marked "active" or "completed"  
✓ All prompt file paths reference existing files  
✓ P02S owns all structured-file transformation units  
✓ No other prompt owns structured-file mutations  
✓ Ownership boundaries are disjoint and complete  
✓ Schema validation passes  

---

## FILES CREATED AND MODIFIED

**Created**:
- `plans_internal/refactor_repo/prompts/P02S_structured_data_codemod.prompt.v4.yaml` (new version with full corrections)
- `plans_internal/refactor_repo/prompts/resolved/acceptance_criteria_mapping.v1.md` (criteria 1-20 mapping)

**Modified**:
- `plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1.yaml` (P02S v3 → v4)

**Preserved**:
- `plans_internal/refactor_repo/prompts/P02S_structured_data_codemod.prompt.v3.yaml` (unchanged, original archived)

---

## NEXT STEP

Run Codex QA gate to verify all criteria pass with corrections in place.
