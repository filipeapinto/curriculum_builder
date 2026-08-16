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


## Before you assess anything: audit the record

You have been in this session since round 1. You remember what you actually said.

Below is the round history as it appears on disk. Claude assembled the artifact and
the fixes; the file record could be wrong, whether by error or by convenience. Compare
it against your own memory and report in `honesty_audit`:

- `rounds_you_recall` — how many verdicts you personally issued, counted from your own
  memory of this conversation, not from the history below.
- `prior_rounds_consistent` — false if the history below attributes to you any verdict
  you did not give, claims a round that did not happen, or reports a finding of yours
  as resolved when you never saw it resolved.
- `discrepancies` — name each one specifically.

If your memory and the record disagree, say so plainly. That disagreement matters more
than this round's verdict, and it is the one thing nobody else can check for us.

### Round history on disk
- Round 1 (2026-08-16T15:26:57.799471+00:00): you returned FAIL with 3 finding(s) at threshold: TOML parser availability and versions are not enforced at import time; Fixture tests do not verify byte-exact expected output; Determinism test does not compare diagnostics for equality


## The artifact under review
Path: /Users/filipepinto/Projects/curriculum_builder_wt/refactor-curriculum-factory-repository/plans_internal/refactor_repo/checkpoints/P02S/P02S_checkpoint_report.v2.md
Version: round 2 of at most 5
SHA-256: 263b8a7752ebd52067243c68f680e70923afaf0886cd6dff7da6b3643654c3bf

Read the file at that path. If it references other files needed to judge it,
read those too.

## What correct means
This is the whole standard. Nothing outside it is grounds for a finding.

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

## Where to spend your attention
P02S structured codemod tool, fixtures, determinism, idempotence, unsafe cases

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
Echo nothing; this is for the record only: 75f661897af478275ea0af907fb8175871717dd3a2f16ecae971cd8ee2a9e09a

Respond only in the required JSON shape.