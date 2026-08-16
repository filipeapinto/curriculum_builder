# P02S Checkpoint QA Criteria v1

## Acceptance Criteria for P02S Structured Data Codemod

### Criterion 1: Format-Specific Implementation

**Observable condition:** The codemod tool must implement separate, format-specific parsers for TOML, JSON, and YAML that preserve semantic round-trip fidelity to the degree supported by each format's parser library.

**Check:**
- TOML: tomli (read) and tomli_w (write) implementations exist and are used
- JSON: stdlib json implementation used
- YAML: PyYAML safe_load/dump implementations used
- Each parser is importable at tool load time; tool fails if not available

**Pass criteria:**
- Tool imports all 3 required parsers without errors
- Each parser is explicitly version-pinned (PyYAML==6.0.3, tomli==2.4.1, tomli_w==1.2.0)
- Version mismatch raises RuntimeError at import time

### Criterion 2: Test Coverage and Fixture Matrix

**Observable condition:** Comprehensive fixtures must cover required syntax, semantics, and error cases for all three formats, demonstrating that transformations work correctly across format-specific differences.

**Check:**
- At least 3 fixtures per format (TOML, JSON, YAML) demonstrating:
  - Simple key-value transformation
  - Nested key transformation
  - No-change case (value mismatch or missing key)
  - At least 1 error case (malformed input)
- Fixtures have .before and .after files with exact expected outputs
- Test suite parameterizes all fixtures and verifies exact output match

**Pass criteria:**
- 10 or more total fixtures covering all 3 formats
- All fixtures pass transformation test (exact output or exact diagnostic)
- Unrelated keys and structure remain unchanged after transformation

### Criterion 3: Determinism and Exact Commands

**Observable condition:** Transformations must produce identical output across repeated runs on the same input, verifiable by byte-exact comparison.

**Check:**
- Run transform_file() twice on identical input with identical configuration
- Compare result.content byte-for-byte across both runs
- Verify diagnostics list is identical

**Pass criteria:**
- No randomness or timestamp injection in output
- Byte-identical content produced on repeated runs
- Test explicitly compares content strings for equality

### Criterion 4: Idempotence

**Observable condition:** Applying a transformation twice must result in no changes on the second application, proving the transformation is single-run.

**Check:**
- Apply transformation to file, write result.content back to disk
- Re-apply transformation to the updated file
- Verify result.changed == False on second application
- Test covers all 3 formats

**Pass criteria:**
- Second application reports changed=False for all formats
- No further modifications occur after first application
- Idempotence holds across TOML, JSON, and YAML

### Criterion 5: Unsafe Input Handling

**Observable condition:** Files with malformed syntax, type mismatches, or unsafe constructs must fail closed with actionable diagnostic messages, without modifying the input file.

**Check:**
- Malformed JSON (invalid syntax) → parse_error diagnostic, file unchanged
- Malformed YAML (invalid syntax) → parse_error diagnostic, file unchanged
- Missing target key → no change, no diagnostic (safe)
- Type mismatch (e.g., transforming int as string) → no change (safe)
- Tool raises no unhandled exceptions; all errors caught as diagnostics

**Pass criteria:**
- All malformed inputs produce error diagnostics or silent no-op
- No file is modified when an error diagnostic is present
- result.has_unsafe() returns True only when file is not modified

### Criterion 6: Diagnostic Clarity

**Observable condition:** Diagnostics must be actionable and format-specific, identifying the file, key, transformation, and severity level.

**Check:**
- Each diagnostic contains: kind (toml_key_rewritten, json_key_rewritten, etc.), severity (info/warning/error), message, file_path
- Messages state the key path, old value, and new value
- Diagnostic kinds are specific to the format (not generic)

**Pass criteria:**
- Every transformation success includes a diagnostic with kind like "toml_key_rewritten"
- Every error includes severity=error
- Messages are human-readable and quote values

### Criterion 7: Scope and Ownership

**Observable condition:** Transformations must respect format boundaries (TOML/JSON/YAML) and only apply transformations that match both the file format and key path.

**Check:**
- A YAML transformation applied to a TOML file should not match
- A JSON transformation applied to a YAML file should not match
- Only transformations where file_format matches the actual format are applied
- Authorized paths in resolved manifest match deliverables

**Pass criteria:**
- Format mismatch results in no change and no diagnostic (format ignored)
- All delivered files within authorized P02S paths
- No transformation crosses format boundaries

### Criterion 8: Parser Version Stability

**Observable condition:** The tool must assert exact parser versions at import time and fail closed if versions don't match, ensuring reproducibility across environments.

**Check:**
- Tool asserts PyYAML==6.0.3 at module import
- Tool asserts tomli and tomli_w versions
- Version mismatch raises RuntimeError with actionable message
- importlib.metadata.version() used to query installed versions

**Pass criteria:**
- Tool imports raise RuntimeError if any required parser version is missing
- Version numbers match the pinned versions exactly
- Error message explains what version was expected vs. found

### Criterion 9: No Write Side Effects in Dry-Run

**Observable condition:** Calling transform_file() with a file path must not modify the file, even though it computes and returns the transformed content.

**Check:**
- Copy fixture file to temp location
- Call transform_file() on it
- Verify file on disk is unchanged (byte-identical to before)
- Verify result.content contains the transformed content (not None)

**Pass criteria:**
- File on disk remains unchanged after transform_file() call
- result.content is not None when changed=True
- No files written, only reads and in-memory computation

## Grounding Sources

- P02S Prompt: `plans_internal/refactor_repo/prompts/generated/P02S_structured_data_codemod.prompt.v4.yaml`
- P02S Specification Section: `plans_internal/refactor_repo/refactor_repository.spec.v8.html` (section on structured transformations)
- Resolved Manifest: `plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v2.yaml` (P02S owns: toml_json_yaml_codemod_tooling, structured_file_transformations_all_formats)

## Non-Criteria Observations

The following are outside the scope of these criteria and will be recorded as observations if Codex notices them:

- Code style, naming conventions, docstring format
- Comments and inline documentation quality
- Whether diagnostic kinds could be extended for additional cases
- Performance characteristics or optimization opportunities
- Typing or type hints completeness
