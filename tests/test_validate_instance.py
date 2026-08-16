"""Focused tests for schemas/validate_instance.py's four independent checks."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from schemas.validate_instance import InstanceValidationError, main, validate_instance

REPO_ROOT = Path(__file__).resolve().parents[1]

MINIMAL_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["title"],
    "properties": {"title": {"type": "string", "minLength": 1}},
}


def _write_schema(tmp_path: Path, name: str = "thing.schema.v1.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(MINIMAL_SCHEMA), encoding="utf-8")
    return path


def _directive(schema_path: Path, instance_path: Path) -> str:
    import os

    rel = os.path.relpath(schema_path, start=instance_path.parent)
    return f"# yaml-language-server: $schema={rel}\n"


def test_valid_instance_passes(tmp_path: Path) -> None:
    schema_path = _write_schema(tmp_path)
    instance_path = tmp_path / "thing.v1.yaml"
    instance_path.write_text(_directive(schema_path, instance_path) + "title: hello\n", encoding="utf-8")

    validate_instance(schema_path, instance_path)  # must not raise


def test_wrong_filename_extension_rejected(tmp_path: Path) -> None:
    schema_path = _write_schema(tmp_path)
    instance_path = tmp_path / "thing.v1.json"
    instance_path.write_text(_directive(schema_path, instance_path) + "title: hello\n", encoding="utf-8")

    with pytest.raises(InstanceValidationError, match="filename"):
        validate_instance(schema_path, instance_path)


def test_filename_missing_version_rejected(tmp_path: Path) -> None:
    schema_path = _write_schema(tmp_path)
    instance_path = tmp_path / "thing.yaml"
    instance_path.write_text(_directive(schema_path, instance_path) + "title: hello\n", encoding="utf-8")

    with pytest.raises(InstanceValidationError, match="filename"):
        validate_instance(schema_path, instance_path)


def test_missing_directive_rejected(tmp_path: Path) -> None:
    schema_path = _write_schema(tmp_path)
    instance_path = tmp_path / "thing.v1.yaml"
    instance_path.write_text("title: hello\n", encoding="utf-8")

    with pytest.raises(InstanceValidationError, match="directive"):
        validate_instance(schema_path, instance_path)


def test_directive_pointing_at_different_schema_rejected(tmp_path: Path) -> None:
    schema_path = _write_schema(tmp_path, "thing.schema.v1.json")
    other_schema_path = _write_schema(tmp_path, "other.schema.v1.json")
    instance_path = tmp_path / "thing.v1.yaml"
    instance_path.write_text(_directive(other_schema_path, instance_path) + "title: hello\n", encoding="utf-8")

    with pytest.raises(InstanceValidationError, match="but --schema resolves"):
        validate_instance(schema_path, instance_path)


def test_directive_target_canonicalized_before_comparison(tmp_path: Path) -> None:
    """Same schema referenced through a differently-spelled but equivalent
    relative path (with a redundant ./ and a subdir round-trip) must still
    match once both sides are resolved to a canonical path."""
    schema_path = _write_schema(tmp_path)
    subdir = tmp_path / "nested"
    subdir.mkdir()
    instance_path = subdir / "thing.v1.yaml"
    equivalent_but_differently_spelled = f"./../nested/../{schema_path.name}"
    instance_path.write_text(
        f"# yaml-language-server: $schema={equivalent_but_differently_spelled}\ntitle: hello\n",
        encoding="utf-8",
    )

    validate_instance(schema_path, instance_path)  # must not raise


def test_malformed_yaml_rejected(tmp_path: Path) -> None:
    schema_path = _write_schema(tmp_path)
    instance_path = tmp_path / "thing.v1.yaml"
    instance_path.write_text(
        _directive(schema_path, instance_path) + "title: [unclosed\n", encoding="utf-8"
    )

    with pytest.raises(InstanceValidationError, match="not valid YAML"):
        validate_instance(schema_path, instance_path)


def test_schema_violation_rejected(tmp_path: Path) -> None:
    schema_path = _write_schema(tmp_path)
    instance_path = tmp_path / "thing.v1.yaml"
    # required 'title' is missing
    instance_path.write_text(_directive(schema_path, instance_path) + "not_title: hello\n", encoding="utf-8")

    with pytest.raises(InstanceValidationError, match="schema validation failed"):
        validate_instance(schema_path, instance_path)


def test_cli_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    schema_path = _write_schema(tmp_path)
    good_instance = tmp_path / "thing.v1.yaml"
    good_instance.write_text(_directive(schema_path, good_instance) + "title: hello\n", encoding="utf-8")

    assert main(["--schema", str(schema_path), "--instance", str(good_instance)]) == 0
    assert "VALID" in capsys.readouterr().out

    bad_instance = tmp_path / "thing.v1.json"
    bad_instance.write_text("title: hello\n", encoding="utf-8")
    assert main(["--schema", str(schema_path), "--instance", str(bad_instance)]) == 1
    assert "INVALID" in capsys.readouterr().err


def test_real_migrated_prompt_validates_against_v4() -> None:
    """End-to-end: the actual migrated create_system_doc prompt, against the
    actual repo schema, run through the same code path the CLI uses."""
    schema_path = REPO_ROOT / "schemas" / "prompt.schema.v4.json"
    instance_path = (
        REPO_ROOT / "plans_internal" / "create_system_doc" / "create_system_doc.prompt.v2.yaml"
    )
    validate_instance(schema_path, instance_path)  # must not raise
