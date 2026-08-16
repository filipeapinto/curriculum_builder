#!/usr/bin/env python3
"""P02S: Parser-based TOML/JSON/YAML codemod for structured reference and identity changes."""

import argparse
import importlib.metadata
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import tomli
    import tomli_w
except ImportError:
    tomli = None
    tomli_w = None

try:
    import yaml
except ImportError:
    yaml = None


def _assert_parser_versions():
    """Assert exact parser versions to fail closed on unexpected environments."""
    required_versions = {
        "PyYAML": "6.0.3",
        "tomli": "2.4.1",
        "tomli_w": "1.2.0",
    }
    for package, required_version in required_versions.items():
        try:
            actual = importlib.metadata.version(package)
            if actual != required_version:
                raise RuntimeError(
                    f"Parser version mismatch: {package} is {actual}, "
                    f"expected {required_version}. This codemod is not "
                    f"portable across parser versions."
                )
        except importlib.metadata.PackageNotFoundError:
            raise RuntimeError(
                f"Required parser not found: {package} {required_version}. "
                f"Install via: pip install {package}=={required_version}"
            )


_assert_parser_versions()


class DiagnosticKind(str, Enum):
    """Kinds of diagnostics emitted during transformation."""
    TOML_KEY_REWRITTEN = "toml_key_rewritten"
    JSON_KEY_REWRITTEN = "json_key_rewritten"
    YAML_KEY_REWRITTEN = "yaml_key_rewritten"
    UNSAFE_TOML_CONSTRUCT = "unsafe_toml_construct"
    UNSAFE_JSON_CONSTRUCT = "unsafe_json_construct"
    UNSAFE_YAML_CONSTRUCT = "unsafe_yaml_construct"
    PARSE_ERROR = "parse_error"
    UNEXPECTED_REFERENCE = "unexpected_reference"
    RESIDUAL_OLD_REFERENCE = "residual_old_reference"


class DiagnosticSeverity(str, Enum):
    """Severity levels for diagnostics."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Diagnostic:
    """A single diagnostic message from transformation."""
    kind: DiagnosticKind
    severity: DiagnosticSeverity
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    context: Optional[str] = None


@dataclass
class TransformationResult:
    """Result of a single file transformation."""
    file_path: str
    changed: bool
    content: Optional[str] = None
    diagnostics: List[Diagnostic] = field(default_factory=list)

    def has_unsafe(self) -> bool:
        """Return True if any diagnostic has ERROR severity."""
        return any(d.severity == DiagnosticSeverity.ERROR for d in self.diagnostics)


@dataclass
class StructuredTransformation:
    """Specifies a single structured reference transformation."""
    file_format: str  # "toml", "json", "yaml"
    key_path: str     # e.g., "project.name"
    old_value: str    # The old identity/reference value
    new_value: str    # The new identity/reference value
    match_type: str = "exact"
    recursive: bool = False


def _transform_toml(
    content: str,
    transformations: List[StructuredTransformation],
    file_path: str,
) -> TransformationResult:
    """Transform TOML content using tomli/tomli_w."""
    if tomli is None or tomli_w is None:
        return TransformationResult(
            file_path=file_path,
            changed=False,
            diagnostics=[
                Diagnostic(
                    kind=DiagnosticKind.PARSE_ERROR,
                    severity=DiagnosticSeverity.ERROR,
                    message="tomli/tomli_w not installed",
                    file_path=file_path,
                )
            ],
        )

    try:
        data = tomli.loads(content)
    except Exception as e:
        return TransformationResult(
            file_path=file_path,
            changed=False,
            diagnostics=[
                Diagnostic(
                    kind=DiagnosticKind.PARSE_ERROR,
                    severity=DiagnosticSeverity.ERROR,
                    message=f"TOML parse error: {e}",
                    file_path=file_path,
                )
            ],
        )

    changed = False
    diagnostics: List[Diagnostic] = []

    for trans in transformations:
        if trans.file_format != "toml":
            continue
        keys = trans.key_path.split(".")
        current = data
        for key in keys[:-1]:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                break
        else:
            final_key = keys[-1]
            if isinstance(current, dict) and final_key in current:
                old_val = current[final_key]
                if isinstance(old_val, str) and old_val == trans.old_value:
                    current[final_key] = trans.new_value
                    changed = True
                    diagnostics.append(
                        Diagnostic(
                            kind=DiagnosticKind.TOML_KEY_REWRITTEN,
                            severity=DiagnosticSeverity.INFO,
                            message=f'TOML key "{trans.key_path}" rewritten: "{trans.old_value}" → "{trans.new_value}"',
                            file_path=file_path,
                        )
                    )

    if changed:
        try:
            new_content = tomli_w.dumps(data)
            return TransformationResult(
                file_path=file_path,
                changed=True,
                content=new_content,
                diagnostics=diagnostics,
            )
        except Exception as e:
            return TransformationResult(
                file_path=file_path,
                changed=False,
                diagnostics=[
                    Diagnostic(
                        kind=DiagnosticKind.UNSAFE_TOML_CONSTRUCT,
                        severity=DiagnosticSeverity.ERROR,
                        message=f"TOML serialization failed: {e}",
                        file_path=file_path,
                    )
                ],
            )

    return TransformationResult(
        file_path=file_path,
        changed=False,
        diagnostics=diagnostics,
    )


def _transform_json(
    content: str,
    transformations: List[StructuredTransformation],
    file_path: str,
) -> TransformationResult:
    """Transform JSON content."""
    try:
        data = json.loads(content)
    except Exception as e:
        return TransformationResult(
            file_path=file_path,
            changed=False,
            diagnostics=[
                Diagnostic(
                    kind=DiagnosticKind.PARSE_ERROR,
                    severity=DiagnosticSeverity.ERROR,
                    message=f"JSON parse error: {e}",
                    file_path=file_path,
                )
            ],
        )

    changed = False
    diagnostics: List[Diagnostic] = []

    for trans in transformations:
        if trans.file_format != "json":
            continue
        keys = trans.key_path.split(".")
        current = data
        for key in keys[:-1]:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                break
        else:
            final_key = keys[-1]
            if isinstance(current, dict) and final_key in current:
                old_val = current[final_key]
                if isinstance(old_val, str) and old_val == trans.old_value:
                    current[final_key] = trans.new_value
                    changed = True
                    diagnostics.append(
                        Diagnostic(
                            kind=DiagnosticKind.JSON_KEY_REWRITTEN,
                            severity=DiagnosticSeverity.INFO,
                            message=f'JSON key "{trans.key_path}" rewritten: "{trans.old_value}" → "{trans.new_value}"',
                            file_path=file_path,
                        )
                    )

    if changed:
        try:
            new_content = json.dumps(data, indent=2)
            return TransformationResult(
                file_path=file_path,
                changed=True,
                content=new_content,
                diagnostics=diagnostics,
            )
        except Exception as e:
            return TransformationResult(
                file_path=file_path,
                changed=False,
                diagnostics=[
                    Diagnostic(
                        kind=DiagnosticKind.UNSAFE_JSON_CONSTRUCT,
                        severity=DiagnosticSeverity.ERROR,
                        message=f"JSON serialization failed: {e}",
                        file_path=file_path,
                    )
                ],
            )

    return TransformationResult(
        file_path=file_path,
        changed=False,
        diagnostics=diagnostics,
    )


def _transform_yaml(
    content: str,
    transformations: List[StructuredTransformation],
    file_path: str,
) -> TransformationResult:
    """Transform YAML content using PyYAML."""
    if yaml is None:
        return TransformationResult(
            file_path=file_path,
            changed=False,
            diagnostics=[
                Diagnostic(
                    kind=DiagnosticKind.PARSE_ERROR,
                    severity=DiagnosticSeverity.ERROR,
                    message="PyYAML not installed",
                    file_path=file_path,
                )
            ],
        )

    try:
        data = yaml.safe_load(content)
    except Exception as e:
        return TransformationResult(
            file_path=file_path,
            changed=False,
            diagnostics=[
                Diagnostic(
                    kind=DiagnosticKind.PARSE_ERROR,
                    severity=DiagnosticSeverity.ERROR,
                    message=f"YAML parse error: {e}",
                    file_path=file_path,
                )
            ],
        )

    changed = False
    diagnostics: List[Diagnostic] = []

    for trans in transformations:
        if trans.file_format != "yaml":
            continue
        keys = trans.key_path.split(".")
        current = data
        for key in keys[:-1]:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                break
        else:
            final_key = keys[-1]
            if isinstance(current, dict) and final_key in current:
                old_val = current[final_key]
                if isinstance(old_val, str) and old_val == trans.old_value:
                    current[final_key] = trans.new_value
                    changed = True
                    diagnostics.append(
                        Diagnostic(
                            kind=DiagnosticKind.YAML_KEY_REWRITTEN,
                            severity=DiagnosticSeverity.INFO,
                            message=f'YAML key "{trans.key_path}" rewritten: "{trans.old_value}" → "{trans.new_value}"',
                            file_path=file_path,
                        )
                    )

    if changed:
        try:
            new_content = yaml.dump(data, default_flow_style=False, sort_keys=False)
            return TransformationResult(
                file_path=file_path,
                changed=True,
                content=new_content,
                diagnostics=diagnostics,
            )
        except Exception as e:
            return TransformationResult(
                file_path=file_path,
                changed=False,
                diagnostics=[
                    Diagnostic(
                        kind=DiagnosticKind.UNSAFE_YAML_CONSTRUCT,
                        severity=DiagnosticSeverity.ERROR,
                        message=f"YAML serialization failed: {e}",
                        file_path=file_path,
                    )
                ],
            )

    return TransformationResult(
        file_path=file_path,
        changed=False,
        diagnostics=diagnostics,
    )


def transform_file(
    file_path: Path,
    transformations: List[StructuredTransformation],
    file_format: Optional[str] = None,
) -> TransformationResult:
    """Transform a single structured file."""
    if not file_path.exists():
        return TransformationResult(
            file_path=str(file_path),
            changed=False,
            diagnostics=[
                Diagnostic(
                    kind=DiagnosticKind.PARSE_ERROR,
                    severity=DiagnosticSeverity.ERROR,
                    message=f"File not found: {file_path}",
                    file_path=str(file_path),
                )
            ],
        )

    if file_format is None:
        suffix = file_path.suffix.lower()
        if suffix == ".toml":
            file_format = "toml"
        elif suffix == ".json":
            file_format = "json"
        elif suffix in (".yaml", ".yml"):
            file_format = "yaml"
        else:
            return TransformationResult(
                file_path=str(file_path),
                changed=False,
                diagnostics=[
                    Diagnostic(
                        kind=DiagnosticKind.PARSE_ERROR,
                        severity=DiagnosticSeverity.ERROR,
                        message=f"Unknown file format: {file_path.suffix}",
                        file_path=str(file_path),
                    )
                ],
            )

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return TransformationResult(
            file_path=str(file_path),
            changed=False,
            diagnostics=[
                Diagnostic(
                    kind=DiagnosticKind.PARSE_ERROR,
                    severity=DiagnosticSeverity.ERROR,
                    message=f"Failed to read file: {e}",
                    file_path=str(file_path),
                )
            ],
        )

    if file_format == "toml":
        return _transform_toml(content, transformations, str(file_path))
    elif file_format == "json":
        return _transform_json(content, transformations, str(file_path))
    elif file_format == "yaml":
        return _transform_yaml(content, transformations, str(file_path))
    else:
        return TransformationResult(
            file_path=str(file_path),
            changed=False,
            diagnostics=[
                Diagnostic(
                    kind=DiagnosticKind.PARSE_ERROR,
                    severity=DiagnosticSeverity.ERROR,
                    message=f"Unsupported format: {file_format}",
                    file_path=str(file_path),
                )
            ],
        )


def transform_files_dry_run(
    file_paths: List[Path],
    transformations: List[StructuredTransformation],
) -> List[TransformationResult]:
    """Run dry-run transformations on multiple files."""
    results = []
    for file_path in file_paths:
        result = transform_file(file_path, transformations)
        results.append(result)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P02S: Parser-based TOML/JSON/YAML codemod")
    parser.add_argument("--version", action="version", version="0.1.0")
    args = parser.parse_args()
    print("P02S codemod tool loaded successfully")
    sys.exit(0)
