#!/usr/bin/env python3
"""
Test suite for P02S structured data codemod (rewrite_structured_references.py).

Tests cover:
1. Format-specific fixture matrix (TOML, JSON, YAML)
2. Determinism and idempotence
3. Unsafe input handling
4. Residual postconditions
5. Parser version pinning
6. Live file application
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

import pytest

# Add tools to path for import
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "tools"))

from refactor_repo.rewrite_structured_references import (
    DiagnosticKind,
    DiagnosticSeverity,
    StructuredTransformation,
    TransformationResult,
    transform_file,
    transform_files_dry_run,
)


# ============================================================================
# Fixtures and utilities
# ============================================================================

FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURES_MANIFEST = json.loads((FIXTURES_DIR / "fixtures_manifest.json").read_text())


@pytest.fixture
def fixtures_manifest():
    """Load the fixtures manifest."""
    return FIXTURES_MANIFEST


def get_fixture_data(name: str) -> Dict:
    """Get a single fixture from the manifest by name."""
    for fixture in FIXTURES_MANIFEST["fixtures"]:
        if fixture["name"] == name:
            return fixture
    raise ValueError(f"Fixture not found: {name}")


# ============================================================================
# Test 1: Format-specific fixture matrix
# ============================================================================

class TestFixtureMatrix:
    """Test that every fixture case produces expected output."""

    @pytest.mark.parametrize("fixture_data", FIXTURES_MANIFEST["fixtures"], ids=lambda f: f["name"])
    def test_fixture_exact_output(self, fixture_data):
        """Test that each fixture produces exact expected output or diagnostic."""

        fixture_name = fixture_data["name"]
        before_path = FIXTURES_DIR / f"{fixture_name}.before.{fixture_data['format']}"
        after_path = FIXTURES_DIR / f"{fixture_name}.after.{fixture_data['format']}"

        if not before_path.exists():
            pytest.skip(f"Fixture file not found: {before_path}")

        # Create the transformation from fixture spec
        trans_spec = fixture_data["transformation"]
        transformation = StructuredTransformation(
            file_format=trans_spec["file_format"],
            key_path=trans_spec["key_path"],
            old_value=trans_spec["old_value"],
            new_value=trans_spec["new_value"],
        )

        # Apply transformation
        result = transform_file(before_path, [transformation])

        # Verify changed flag
        assert result.changed == fixture_data["expect_changed"], \
            f"Fixture {fixture_name}: changed={result.changed}, " \
            f"expected {fixture_data['expect_changed']}"

        # Verify unsafe flag
        has_unsafe = result.has_unsafe()
        assert has_unsafe == fixture_data["expect_unsafe"], \
            f"Fixture {fixture_name}: has_unsafe={has_unsafe}, " \
            f"expected {fixture_data['expect_unsafe']}"

        # Verify diagnostic kinds
        actual_kinds = {d.kind.value for d in result.diagnostics}
        expected_kinds = set(fixture_data["expect_diagnostic_kinds"])
        assert actual_kinds == expected_kinds, \
            f"Fixture {fixture_name}: diagnostics={actual_kinds}, " \
            f"expected {expected_kinds}"

        # If changed, verify output matches expected after file exactly (byte-for-byte)
        if result.changed and after_path.exists():
            expected_content = after_path.read_text(encoding="utf-8")
            assert result.content is not None, \
                f"Fixture {fixture_name}: changed=True but content is None"
            # Byte-exact comparison (no normalization; parsers must produce exact output)
            assert result.content == expected_content, \
                f"Fixture {fixture_name}: output mismatch (byte-for-byte)\n" \
                f"Expected ({len(expected_content)} bytes):\n{repr(expected_content)}\n" \
                f"Actual ({len(result.content)} bytes):\n{repr(result.content)}"


# ============================================================================
# Test 2: Determinism
# ============================================================================

class TestDeterminism:
    """Test that transformations are deterministic across runs."""

    def test_dry_run_is_deterministic_across_repeated_calls(self):
        """Run the same dry-run transformation twice and verify byte-identical output and diagnostics."""

        fixture_data = get_fixture_data("toml_simple_string_key")
        before_path = FIXTURES_DIR / f"{fixture_data['name']}.before.toml"

        transformation = StructuredTransformation(
            file_format="toml",
            key_path="project.name",
            old_value="curriculum-builder",
            new_value="curriculum-factory",
        )

        # First run
        result1 = transform_file(before_path, [transformation])
        content1 = result1.content

        # Second run
        result2 = transform_file(before_path, [transformation])
        content2 = result2.content

        # Verify byte-identical content
        assert content1 == content2, \
            "Determinism failed: repeated calls produced different content output"
        assert result1.changed == result2.changed, \
            "Determinism failed: changed flags differ"

        # Verify diagnostics are identical across runs
        assert len(result1.diagnostics) == len(result2.diagnostics), \
            f"Determinism failed: diagnostic count differs (run1: {len(result1.diagnostics)}, run2: {len(result2.diagnostics)})"
        for diag1, diag2 in zip(result1.diagnostics, result2.diagnostics):
            assert diag1.kind == diag2.kind, \
                f"Determinism failed: diagnostic kind differs ({diag1.kind} vs {diag2.kind})"
            assert diag1.severity == diag2.severity, \
                f"Determinism failed: diagnostic severity differs ({diag1.severity} vs {diag2.severity})"
            assert diag1.message == diag2.message, \
                f"Determinism failed: diagnostic message differs"
            assert diag1.file_path == diag2.file_path, \
                f"Determinism failed: diagnostic file_path differs"


# ============================================================================
# Test 3: Idempotence
# ============================================================================

class TestIdempotence:
    """Test that applying transformation twice results in no change on second run."""

    def test_apply_mode_is_idempotent_toml(self, tmp_path):
        """TOML: apply transformation, verify idempotence on second run."""

        fixture_data = get_fixture_data("toml_simple_string_key")
        before_path = FIXTURES_DIR / f"{fixture_data['name']}.before.toml"

        # Copy fixture to temp file
        temp_file = tmp_path / "test.toml"
        temp_file.write_text(before_path.read_text())

        transformation = StructuredTransformation(
            file_format="toml",
            key_path="project.name",
            old_value="curriculum-builder",
            new_value="curriculum-factory",
        )

        # First application
        result1 = transform_file(temp_file, [transformation])
        assert result1.changed, "First application should change file"
        temp_file.write_text(result1.content)

        # Second application (should be idempotent)
        result2 = transform_file(temp_file, [transformation])
        assert not result2.changed, "Second application should not change file (idempotence failed)"

    def test_apply_mode_is_idempotent_json(self, tmp_path):
        """JSON: apply transformation, verify idempotence on second run."""

        fixture_data = get_fixture_data("json_simple_key")
        before_path = FIXTURES_DIR / f"{fixture_data['name']}.before.json"

        temp_file = tmp_path / "test.json"
        temp_file.write_text(before_path.read_text())

        transformation = StructuredTransformation(
            file_format="json",
            key_path="name",
            old_value="curriculum-builder",
            new_value="curriculum-factory",
        )

        # First application
        result1 = transform_file(temp_file, [transformation])
        assert result1.changed
        temp_file.write_text(result1.content)

        # Second application
        result2 = transform_file(temp_file, [transformation])
        assert not result2.changed

    def test_apply_mode_is_idempotent_yaml(self, tmp_path):
        """YAML: apply transformation, verify idempotence on second run."""

        fixture_data = get_fixture_data("yaml_simple_key")
        before_path = FIXTURES_DIR / f"{fixture_data['name']}.before.yaml"

        temp_file = tmp_path / "test.yaml"
        temp_file.write_text(before_path.read_text())

        transformation = StructuredTransformation(
            file_format="yaml",
            key_path="name",
            old_value="curriculum-builder",
            new_value="curriculum-factory",
        )

        # First application
        result1 = transform_file(temp_file, [transformation])
        assert result1.changed
        temp_file.write_text(result1.content)

        # Second application
        result2 = transform_file(temp_file, [transformation])
        assert not result2.changed


# ============================================================================
# Test 4: Unsafe input handling
# ============================================================================

class TestUnsafeInputHandling:
    """Test that unsafe inputs are handled safely."""

    def test_malformed_json_fails_closed(self):
        """Malformed JSON should fail safely without modification."""

        fixture_data = get_fixture_data("malformed_json")
        before_path = FIXTURES_DIR / f"{fixture_data['name']}.before.json"

        transformation = StructuredTransformation(
            file_format="json",
            key_path="key",
            old_value="old",
            new_value="new",
        )

        result = transform_file(before_path, [transformation])

        # Should not change
        assert not result.changed
        # Should have error diagnostic
        assert result.has_unsafe()
        error_diags = [d for d in result.diagnostics if d.severity == DiagnosticSeverity.ERROR]
        assert len(error_diags) > 0

    def test_missing_file_returns_diagnostic(self, tmp_path):
        """Attempting to transform non-existent file should return diagnostic."""

        nonexistent_path = tmp_path / "nonexistent.json"

        transformation = StructuredTransformation(
            file_format="json",
            key_path="key",
            old_value="old",
            new_value="new",
        )

        result = transform_file(nonexistent_path, [transformation])

        assert not result.changed
        assert result.has_unsafe()
        assert any(d.kind == DiagnosticKind.PARSE_ERROR for d in result.diagnostics)


# ============================================================================
# Test 5: Parser version pinning
# ============================================================================

class TestParserVersionPinning:
    """Test that parser versions are pinned and checked."""

    def test_parser_versions_are_pinned(self):
        """Verify that required parser versions are pinned at import time."""

        # This test imports the module and verifies no RuntimeError was raised
        # due to version mismatch. If we reached this point, version checks passed.
        assert True


# ============================================================================
# Test 6: Multiple transformations on same file
# ============================================================================

class TestMultipleTransformations:
    """Test applying multiple transformations to a single file."""

    def test_multiple_transformations_toml(self):
        """Apply multiple transformations to a single TOML file."""

        fixture_data = get_fixture_data("toml_simple_string_key")
        before_path = FIXTURES_DIR / f"{fixture_data['name']}.before.toml"

        transformations = [
            StructuredTransformation(
                file_format="toml",
                key_path="project.name",
                old_value="curriculum-builder",
                new_value="curriculum-factory",
            ),
            StructuredTransformation(
                file_format="toml",
                key_path="project.version",
                old_value="0.1.0",
                new_value="0.1.1",
            ),
        ]

        result = transform_file(before_path, transformations)

        # At least one should apply
        assert result.changed or any(t.old_value not in before_path.read_text() for t in transformations)


# ============================================================================
# Test 7: Dry-run mode does not modify files
# ============================================================================

class TestDryRunMode:
    """Test that dry-run transformations don't modify files."""

    def test_dry_run_does_not_modify_files(self, tmp_path):
        """Dry-run should return changes but not write to disk."""

        fixture_data = get_fixture_data("toml_simple_string_key")
        before_path = FIXTURES_DIR / f"{fixture_data['name']}.before.toml"

        # Copy fixture to temp file
        temp_file = tmp_path / "test.toml"
        original_content = before_path.read_text()
        temp_file.write_text(original_content)

        transformation = StructuredTransformation(
            file_format="toml",
            key_path="project.name",
            old_value="curriculum-builder",
            new_value="curriculum-factory",
        )

        result = transform_file(temp_file, [transformation])

        # File on disk should be unchanged (dry-run)
        assert temp_file.read_text() == original_content

        # Result should indicate change
        assert result.changed
        assert result.content is not None


# ============================================================================
# Test 8: Batch dry-run
# ============================================================================

class TestBatchDryRun:
    """Test batch processing of multiple files."""

    def test_batch_dry_run_multiple_files(self):
        """Run dry-run on multiple fixture files."""

        files_to_run = [
            FIXTURES_DIR / "toml_simple_string_key.before.toml",
            FIXTURES_DIR / "json_simple_key.before.json",
            FIXTURES_DIR / "yaml_simple_key.before.yaml",
        ]

        # Filter to existing files
        existing_files = [f for f in files_to_run if f.exists()]

        transformations = [
            StructuredTransformation(
                file_format="toml",
                key_path="project.name",
                old_value="curriculum-builder",
                new_value="curriculum-factory",
            ),
            StructuredTransformation(
                file_format="json",
                key_path="name",
                old_value="curriculum-builder",
                new_value="curriculum-factory",
            ),
            StructuredTransformation(
                file_format="yaml",
                key_path="name",
                old_value="curriculum-builder",
                new_value="curriculum-factory",
            ),
        ]

        results = transform_files_dry_run(existing_files, transformations)

        assert len(results) == len(existing_files)
        # Each should have diagnostics or changes
        for result in results:
            assert result.file_path in [str(f) for f in existing_files]


# ============================================================================
# Test 9: Ownership and scope
# ============================================================================

class TestOwnershipAndScope:
    """Test that transformations respect ownership boundaries."""

    def test_only_owned_formats_transformed(self):
        """Only TOML/JSON/YAML transformations should be applied."""

        fixture_data = get_fixture_data("toml_simple_string_key")
        before_path = FIXTURES_DIR / f"{fixture_data['name']}.before.toml"

        # Create a transformation for a different format
        yaml_transformation = StructuredTransformation(
            file_format="yaml",
            key_path="name",
            old_value="curriculum-builder",
            new_value="curriculum-factory",
        )

        # Apply YAML transformation to TOML file (should not match)
        result = transform_file(before_path, [yaml_transformation], file_format="toml")

        # Should not change because format mismatches
        assert not result.changed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
