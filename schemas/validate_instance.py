#!/usr/bin/env python3
"""Generic file-level validator for YAML instances of this repo's house schemas.

A JSON Schema validates parsed data; it cannot see a file's name, its first
line, or which serialization produced that data. This script is the
mechanical enforcement the schemas' own $comment fields point to: filename
convention, the yaml-language-server $schema directive, that the file
actually parses as YAML, and only then the parsed data against the given
JSON Schema. All four checks must pass for an instance to be VALID.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import jsonschema
import yaml

FILENAME_RE = re.compile(r"\.v\d+\.ya?ml$")
DIRECTIVE_RE = re.compile(r"^#\s*yaml-language-server:\s*\$schema=(\S+)\s*$")


class InstanceValidationError(RuntimeError):
    """One of the four checks failed; the message names which one and why."""


def check_filename(instance_path: Path) -> None:
    if not FILENAME_RE.search(instance_path.name):
        raise InstanceValidationError(
            f"filename {instance_path.name!r} does not match the required "
            "*.v<N>.yaml / *.v<N>.yml convention"
        )


def check_directive(instance_path: Path, schema_path: Path) -> None:
    text = instance_path.read_text(encoding="utf-8")
    first_line = text.splitlines()[0].strip() if text else ""
    match = DIRECTIVE_RE.match(first_line)
    if not match:
        raise InstanceValidationError(
            "first line is not a '# yaml-language-server: $schema=...' "
            f"directive: {first_line!r}"
        )
    # The directive is relative to the instance file's own directory (the
    # convention yaml-language-server itself uses), while --schema may be
    # given relative to the caller's cwd or as an absolute path. Both must
    # resolve to the same canonical file before they can be compared.
    directive_target = (instance_path.parent / match.group(1)).resolve()
    expected_target = schema_path.resolve()
    if directive_target != expected_target:
        raise InstanceValidationError(
            f"directive points at {directive_target} but --schema resolves "
            f"to {expected_target}"
        )


def load_yaml(instance_path: Path) -> object:
    try:
        return yaml.safe_load(instance_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise InstanceValidationError(f"not valid YAML: {exc}") from exc


def validate_against_schema(data: object, schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator_cls = jsonschema.Draft202012Validator
    validator_cls.check_schema(schema)
    errors = sorted(validator_cls(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        details = "; ".join(f"{list(e.path)}: {e.message}" for e in errors[:10])
        raise InstanceValidationError(f"schema validation failed: {details}")


def validate_instance(schema_path: Path, instance_path: Path) -> None:
    check_filename(instance_path)
    check_directive(instance_path, schema_path)
    data = load_yaml(instance_path)
    validate_against_schema(data, schema_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--instance", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        validate_instance(args.schema, args.instance)
    except InstanceValidationError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(f"VALID: {args.instance} conforms to {args.schema}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
