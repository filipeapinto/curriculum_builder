#!/usr/bin/env python3
"""P02S: parser-based TOML/JSON/YAML codemod for structured reference and identity changes.

Two ways to target a rewrite:

* ``key_path`` given -- rewrite exactly one dotted key, only when its current value
  matches ``old_value`` (whole-value match by default, or substring with
  ``match_type="substring"``).
* ``key_path`` omitted -- walk every string value in the document and replace any
  occurrence of ``old_value`` as a substring, wherever it appears.

Every format is parsed with a library that can reproduce the parts of the document
this tool does not touch -- comments, quote style, anchors, block-scalar style --
so a rewrite never collaterally reformats content it was not asked to change. JSON
has no such library (it also has no comments to lose), so instead this tool proves
losslessness directly: it re-serializes the parsed, unmodified document and refuses
to transform the file unless that output is byte-identical to the input.
"""

from __future__ import annotations

import argparse
import difflib
import importlib.metadata
import io
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import tomlkit
    from tomlkit.exceptions import TOMLKitError
    from tomlkit.items import String as TomlString
except ImportError:  # pragma: no cover - exercised only in a broken environment
    tomlkit = None
    TOMLKitError = Exception
    TomlString = None

try:
    from ruamel.yaml import YAML, YAMLError
    from ruamel.yaml.comments import TaggedScalar
    from ruamel.yaml.constructor import DuplicateKeyError
    from ruamel.yaml.scalarstring import (
        DoubleQuotedScalarString,
        FoldedScalarString,
        LiteralScalarString,
        SingleQuotedScalarString,
    )
except ImportError:  # pragma: no cover - exercised only in a broken environment
    YAML = None
    YAMLError = Exception
    TaggedScalar = None
    DuplicateKeyError = None
    LiteralScalarString = FoldedScalarString = None
    SingleQuotedScalarString = DoubleQuotedScalarString = None


def _assert_parser_versions() -> None:
    """Assert exact parser versions to fail closed on unexpected environments."""
    required_versions = {
        "tomlkit": "0.15.1",
        "ruamel.yaml": "0.19.1",
    }
    for package, required_version in required_versions.items():
        try:
            actual = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            raise RuntimeError(
                f"Required parser not found: {package} {required_version}. "
                f"Install via: pip install {package}=={required_version}"
            )
        if actual != required_version:
            raise RuntimeError(
                f"Parser version mismatch: {package} is {actual}, "
                f"expected {required_version}. This codemod is not "
                f"portable across parser versions."
            )


_assert_parser_versions()


class DiagnosticKind(str, Enum):
    """Kinds of diagnostics emitted during transformation."""
    REWRITE_VALUE = "rewrite_value"
    PARSE_ERROR = "parse_error"
    MALFORMED_INPUT = "malformed_input"
    DUPLICATE_KEY = "duplicate_key"
    UNSUPPORTED_TAG = "unsupported_tag"
    ROUND_TRIP_FIDELITY_UNSUPPORTED = "round_trip_fidelity_unsupported"
    RESIDUAL_OLD_REFERENCE = "residual_old_reference"
    UNEXPECTED_NEW_REFERENCE = "unexpected_new_reference"


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
    """Specifies one structured reference rewrite.

    ``key_path`` targets exactly one dotted key. Leaving it unset rewrites every
    string value in the document that contains ``old_value`` as a substring.
    """
    file_format: str  # "toml", "json", "yaml"
    old_value: str
    new_value: str
    key_path: Optional[str] = None
    match_type: str = "exact"  # "exact" or "substring"; applies only with key_path


# --------------------------------------------------------------------------------
# YAML plain-scalar ambiguity: values that would silently change type if left
# unquoted (e.g. a replacement value of "true" parsing back as a boolean).
# --------------------------------------------------------------------------------

_YAML_BOOL_OR_NULL = re.compile(
    r"^(?:true|false|yes|no|on|off|null|~)$", re.IGNORECASE)
_YAML_INT = re.compile(r"^[-+]?(0b[0-1_]+|0o?[0-7_]+|0x[0-9a-fA-F_]+|[0-9][0-9_]*)$")
_YAML_FLOAT = re.compile(
    r"^[-+]?(\.inf|\.nan|[0-9][0-9_]*\.[0-9_]*([eE][-+]?[0-9]+)?|"
    r"\.[0-9_]+([eE][-+]?[0-9]+)?)$", re.IGNORECASE)


def _yaml_plain_is_ambiguous(text: str) -> bool:
    if text == "":
        return True
    return bool(_YAML_BOOL_OR_NULL.match(text) or _YAML_INT.match(text)
                or _YAML_FLOAT.match(text))


def _wrap_yaml_value(old_item: Any, new_text: str) -> Any:
    """Rebuild a replacement value in the same scalar style as ``old_item``."""
    if isinstance(old_item, LiteralScalarString):
        return LiteralScalarString(new_text)
    if isinstance(old_item, FoldedScalarString):
        return FoldedScalarString(new_text)
    if isinstance(old_item, SingleQuotedScalarString):
        return SingleQuotedScalarString(new_text)
    if isinstance(old_item, DoubleQuotedScalarString):
        return DoubleQuotedScalarString(new_text)
    if _yaml_plain_is_ambiguous(new_text):
        return SingleQuotedScalarString(new_text)
    return new_text


def _wrap_toml_value(old_item: Any, new_text: str) -> Any:
    if isinstance(old_item, TomlString):
        return TomlString.from_raw(new_text, type_=old_item.type)
    return new_text


# --------------------------------------------------------------------------------
# Tree walking: apply either a single targeted key_path rewrite, or a global
# substring rewrite over every string leaf.
# --------------------------------------------------------------------------------

def _apply_targeted(container: Any, transformation: StructuredTransformation,
                     wrap) -> bool:
    keys = transformation.key_path.split(".")
    current = container
    for key in keys[:-1]:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return False
    final_key = keys[-1]
    if not (isinstance(current, dict) and final_key in current):
        return False
    old_item = current[final_key]
    if not isinstance(old_item, str):
        return False
    text = str(old_item)
    if transformation.match_type == "substring":
        if transformation.old_value not in text:
            return False
        new_text = text.replace(transformation.old_value, transformation.new_value)
    else:
        if text != transformation.old_value:
            return False
        new_text = transformation.new_value
    current[final_key] = wrap(old_item, new_text)
    return True


def _apply_global(node: Any, old_value: str, new_value: str, wrap) -> int:
    """Recursively replace ``old_value`` substrings in every string leaf.

    Returns the number of leaves changed.
    """
    if isinstance(node, dict):
        count = 0
        for key in list(node.keys()):
            child = node[key]
            if isinstance(child, str) and old_value in child:
                node[key] = wrap(child, str(child).replace(old_value, new_value))
                count += 1
            else:
                count += _apply_global(child, old_value, new_value, wrap)
        return count
    if isinstance(node, list):
        count = 0
        for index, child in enumerate(node):
            if isinstance(child, str) and old_value in child:
                node[index] = wrap(child, str(child).replace(old_value, new_value))
                count += 1
            else:
                count += _apply_global(child, old_value, new_value, wrap)
        return count
    return 0


def _postconditions(final_text: str,
                     transformations: List[StructuredTransformation],
                     file_path: str) -> List[Diagnostic]:
    """Flag old references this tool could not reach (e.g. inside a key name).

    A pre-existing occurrence of ``new_value`` is not itself flagged here: a file
    that already used the new identity before this rewrite ran is the intended end
    state, not an anomaly.
    """
    diagnostics: List[Diagnostic] = []
    seen_old: set[str] = set()
    for trans in transformations:
        if trans.old_value not in seen_old and trans.old_value in final_text:
            seen_old.add(trans.old_value)
            diagnostics.append(Diagnostic(
                kind=DiagnosticKind.RESIDUAL_OLD_REFERENCE,
                severity=DiagnosticSeverity.WARNING,
                message=f'old reference "{trans.old_value}" remains in {file_path} '
                        f"outside any value this tool rewrites (for example, a key "
                        f"or table name)",
                file_path=file_path,
            ))
    return diagnostics


# --------------------------------------------------------------------------------
# JSON
# --------------------------------------------------------------------------------

class _DuplicateJSONKeyError(ValueError):
    def __init__(self, key: str):
        super().__init__(f"duplicate key: {key!r}")
        self.key = key


def _no_duplicate_keys(pairs):
    seen: Dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise _DuplicateJSONKeyError(key)
        seen[key] = value
    return seen


def _canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _transform_json(content: str, transformations: List[StructuredTransformation],
                     file_path: str) -> TransformationResult:
    try:
        data = json.loads(content, object_pairs_hook=_no_duplicate_keys)
    except _DuplicateJSONKeyError as error:
        return TransformationResult(file_path=file_path, changed=False, diagnostics=[
            Diagnostic(kind=DiagnosticKind.DUPLICATE_KEY, severity=DiagnosticSeverity.ERROR,
                       message=f"JSON has a duplicate key: {error.key}", file_path=file_path)])
    except json.JSONDecodeError as error:
        return TransformationResult(file_path=file_path, changed=False, diagnostics=[
            Diagnostic(kind=DiagnosticKind.MALFORMED_INPUT, severity=DiagnosticSeverity.ERROR,
                       message=f"JSON parse error: {error}", file_path=file_path)])

    if _canonical_json(data) != content:
        return TransformationResult(file_path=file_path, changed=False, diagnostics=[
            Diagnostic(
                kind=DiagnosticKind.ROUND_TRIP_FIDELITY_UNSUPPORTED,
                severity=DiagnosticSeverity.ERROR,
                message=(f"{file_path} is not in this tool's canonical JSON "
                          f"formatting (2-space indent); rewriting it would "
                          f"reformat content beyond the intended change, so no "
                          f"rewrite was applied"),
                file_path=file_path)])

    relevant = [t for t in transformations if t.file_format == "json"]
    diagnostics: List[Diagnostic] = []
    changed = False
    for trans in relevant:
        if trans.key_path is not None:
            if _apply_targeted(data, trans, lambda old, new: new):
                changed = True
                diagnostics.append(Diagnostic(
                    kind=DiagnosticKind.REWRITE_VALUE, severity=DiagnosticSeverity.INFO,
                    message=f'JSON key "{trans.key_path}" rewritten: '
                            f'"{trans.old_value}" -> "{trans.new_value}"',
                    file_path=file_path))
        else:
            count = _apply_global(data, trans.old_value, trans.new_value,
                                   lambda old, new: new)
            if count:
                changed = True
                diagnostics.append(Diagnostic(
                    kind=DiagnosticKind.REWRITE_VALUE, severity=DiagnosticSeverity.INFO,
                    message=f'JSON: {count} value(s) rewritten '
                            f'"{trans.old_value}" -> "{trans.new_value}"',
                    file_path=file_path))

    final_content = _canonical_json(data) if changed else content
    diagnostics.extend(_postconditions(final_content, relevant, file_path))
    return TransformationResult(
        file_path=file_path, changed=changed,
        content=final_content if changed else None, diagnostics=diagnostics)


# --------------------------------------------------------------------------------
# TOML
# --------------------------------------------------------------------------------

def _transform_toml(content: str, transformations: List[StructuredTransformation],
                     file_path: str) -> TransformationResult:
    if tomlkit is None:
        return TransformationResult(file_path=file_path, changed=False, diagnostics=[
            Diagnostic(kind=DiagnosticKind.MALFORMED_INPUT, severity=DiagnosticSeverity.ERROR,
                       message="tomlkit is not installed", file_path=file_path)])
    try:
        doc = tomlkit.parse(content)
    except TOMLKitError as error:
        return TransformationResult(file_path=file_path, changed=False, diagnostics=[
            Diagnostic(kind=DiagnosticKind.MALFORMED_INPUT, severity=DiagnosticSeverity.ERROR,
                       message=f"TOML parse error: {error}", file_path=file_path)])

    relevant = [t for t in transformations if t.file_format == "toml"]
    diagnostics: List[Diagnostic] = []
    changed = False
    for trans in relevant:
        if trans.key_path is not None:
            if _apply_targeted(doc, trans, _wrap_toml_value):
                changed = True
                diagnostics.append(Diagnostic(
                    kind=DiagnosticKind.REWRITE_VALUE, severity=DiagnosticSeverity.INFO,
                    message=f'TOML key "{trans.key_path}" rewritten: '
                            f'"{trans.old_value}" -> "{trans.new_value}"',
                    file_path=file_path))
        else:
            count = _apply_global(doc, trans.old_value, trans.new_value, _wrap_toml_value)
            if count:
                changed = True
                diagnostics.append(Diagnostic(
                    kind=DiagnosticKind.REWRITE_VALUE, severity=DiagnosticSeverity.INFO,
                    message=f'TOML: {count} value(s) rewritten '
                            f'"{trans.old_value}" -> "{trans.new_value}"',
                    file_path=file_path))

    if changed:
        try:
            final_content = tomlkit.dumps(doc)
        except TOMLKitError as error:
            return TransformationResult(file_path=file_path, changed=False, diagnostics=[
                Diagnostic(kind=DiagnosticKind.MALFORMED_INPUT, severity=DiagnosticSeverity.ERROR,
                           message=f"TOML serialization failed: {error}", file_path=file_path)])
    else:
        final_content = content

    diagnostics.extend(_postconditions(final_content, relevant, file_path))
    return TransformationResult(
        file_path=file_path, changed=changed,
        content=final_content if changed else None, diagnostics=diagnostics)


# --------------------------------------------------------------------------------
# YAML
# --------------------------------------------------------------------------------

def _find_unsupported_tag(node: Any) -> Optional[str]:
    if TaggedScalar is not None and isinstance(node, TaggedScalar):
        return str(node.tag)
    if isinstance(node, dict):
        for value in node.values():
            found = _find_unsupported_tag(value)
            if found:
                return found
    elif isinstance(node, list):
        for value in node:
            found = _find_unsupported_tag(value)
            if found:
                return found
    return None


def _yaml_engine() -> "YAML":
    engine = YAML(typ="rt")
    engine.preserve_quotes = True
    engine.width = 4096  # do not rewrap lines this tool was not asked to touch
    return engine


def _transform_yaml(content: str, transformations: List[StructuredTransformation],
                     file_path: str) -> TransformationResult:
    if YAML is None:
        return TransformationResult(file_path=file_path, changed=False, diagnostics=[
            Diagnostic(kind=DiagnosticKind.MALFORMED_INPUT, severity=DiagnosticSeverity.ERROR,
                       message="ruamel.yaml is not installed", file_path=file_path)])
    engine = _yaml_engine()
    try:
        data = engine.load(content)
    except YAMLError as error:
        return TransformationResult(file_path=file_path, changed=False, diagnostics=[
            Diagnostic(kind=DiagnosticKind.MALFORMED_INPUT, severity=DiagnosticSeverity.ERROR,
                       message=f"YAML parse error: {error}", file_path=file_path)])

    if data is None:
        data = {}

    unsupported = _find_unsupported_tag(data)
    if unsupported is not None:
        return TransformationResult(file_path=file_path, changed=False, diagnostics=[
            Diagnostic(
                kind=DiagnosticKind.UNSUPPORTED_TAG, severity=DiagnosticSeverity.ERROR,
                message=f"{file_path} uses the custom tag {unsupported}, which this "
                        f"tool does not know how to rewrite safely",
                file_path=file_path)])

    canary = io.StringIO()
    engine.dump(data, canary)
    if canary.getvalue() != content:
        return TransformationResult(file_path=file_path, changed=False, diagnostics=[
            Diagnostic(
                kind=DiagnosticKind.ROUND_TRIP_FIDELITY_UNSUPPORTED,
                severity=DiagnosticSeverity.ERROR,
                message=(f"{file_path} does not round-trip byte-identically through "
                          f"this tool's YAML engine before any change is made "
                          f"(for example, an unusual null spelling or sequence "
                          f"indent); rewriting it risks reformatting content beyond "
                          f"the intended change, so no rewrite was applied"),
                file_path=file_path)])

    relevant = [t for t in transformations if t.file_format == "yaml"]
    diagnostics: List[Diagnostic] = []
    changed = False
    for trans in relevant:
        if trans.key_path is not None:
            if _apply_targeted(data, trans, _wrap_yaml_value):
                changed = True
                diagnostics.append(Diagnostic(
                    kind=DiagnosticKind.REWRITE_VALUE, severity=DiagnosticSeverity.INFO,
                    message=f'YAML key "{trans.key_path}" rewritten: '
                            f'"{trans.old_value}" -> "{trans.new_value}"',
                    file_path=file_path))
        else:
            count = _apply_global(data, trans.old_value, trans.new_value, _wrap_yaml_value)
            if count:
                changed = True
                diagnostics.append(Diagnostic(
                    kind=DiagnosticKind.REWRITE_VALUE, severity=DiagnosticSeverity.INFO,
                    message=f'YAML: {count} value(s) rewritten '
                            f'"{trans.old_value}" -> "{trans.new_value}"',
                    file_path=file_path))

    if changed:
        buffer = io.StringIO()
        engine.dump(data, buffer)
        final_content = buffer.getvalue()
    else:
        final_content = content

    diagnostics.extend(_postconditions(final_content, relevant, file_path))
    return TransformationResult(
        file_path=file_path, changed=changed,
        content=final_content if changed else None, diagnostics=diagnostics)


# --------------------------------------------------------------------------------
# Public entry points
# --------------------------------------------------------------------------------

_TRANSFORMERS = {
    "toml": _transform_toml,
    "json": _transform_json,
    "yaml": _transform_yaml,
}


def transform_file(
    file_path: Path,
    transformations: List[StructuredTransformation],
    file_format: Optional[str] = None,
) -> TransformationResult:
    """Transform a single structured file."""
    file_path = Path(file_path)
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

    resolved_format = file_format or file_path.suffix.lstrip(".").lower()
    transformer = _TRANSFORMERS.get(resolved_format)
    if transformer is None:
        return TransformationResult(
            file_path=str(file_path), changed=False,
            diagnostics=[Diagnostic(
                kind=DiagnosticKind.PARSE_ERROR, severity=DiagnosticSeverity.ERROR,
                message=f"Unsupported format: {resolved_format}", file_path=str(file_path))])

    content = file_path.read_text(encoding="utf-8")
    return transformer(content, transformations, str(file_path))


def transform_files_dry_run(
    file_paths: List[Path],
    transformations: List[StructuredTransformation],
) -> List[TransformationResult]:
    """Run dry-run transformations on multiple files."""
    return [transform_file(path, transformations) for path in file_paths]


def apply_file(file_path: Path, transformations: List[StructuredTransformation]) -> TransformationResult:
    """Transform a file and, if changed and safe, write the result back."""
    result = transform_file(file_path, transformations)
    if result.changed and not result.has_unsafe() and result.content is not None:
        Path(file_path).write_text(result.content, encoding="utf-8")
    return result


def _cli() -> int:
    parser = argparse.ArgumentParser(
        description="P02S: parser-based TOML/JSON/YAML identity codemod")
    parser.add_argument("--version", action="version", version="0.2.0")
    parser.add_argument("paths", nargs="*", type=Path, help="files to transform")
    parser.add_argument("--old", help="old value to replace")
    parser.add_argument("--new", help="new value to replace it with")
    parser.add_argument("--apply", action="store_true",
                         help="write changes to disk (default: dry-run diff only)")
    args = parser.parse_args()

    if not args.paths:
        return 0
    if not args.old or not args.new:
        parser.error("--old and --new are required when paths are given")

    unsafe = False
    for path in args.paths:
        file_format = path.suffix.lstrip(".").lower()
        transformation = StructuredTransformation(
            file_format=file_format, old_value=args.old, new_value=args.new)
        result = (apply_file(path, [transformation]) if args.apply
                  else transform_file(path, [transformation]))
        for diagnostic in result.diagnostics:
            print(f"[{diagnostic.severity.value}] {diagnostic.kind.value}: {diagnostic.message}",
                  file=sys.stderr)
        if result.has_unsafe():
            unsafe = True
        if result.changed and result.content is not None and not args.apply:
            before = path.read_text(encoding="utf-8")
            diff = difflib.unified_diff(
                before.splitlines(keepends=True), result.content.splitlines(keepends=True),
                fromfile=f"a/{path}", tofile=f"b/{path}")
            sys.stdout.writelines(diff)
    return 1 if unsafe else 0


if __name__ == "__main__":
    raise SystemExit(_cli())
