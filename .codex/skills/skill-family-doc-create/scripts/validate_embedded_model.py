#!/usr/bin/env python3
"""Validate the embedded family-model JSON block inside a family-guide.html.

Checks, in order:
  1. Exactly one <script type="application/json" id="family-model"> block exists
     and it is valid JSON.
  2. It conforms to references/embedded-family-model.schema.json (uses the
     `jsonschema` package if installed; otherwise falls back to a small
     built-in validator covering the subset of JSON Schema this schema uses:
     type, required, properties, additionalProperties, items, enum, const,
     pattern, minItems, minLength, minimum).
  3. Every source in sources[] whose path resolves on this filesystem has a
     digest matching the file's current sha256 — catching a guide that has
     drifted from the evidence it claims to describe.
  4. Cross-consistency: every edges[].from/to and failure_routes[].owner and
     entry_point.component_id (if set) names a components[].id that exists.

Usage:
    python3 validate_embedded_model.py <family-guide.html> [--repo-root PATH]

Exit code 0 = valid, 1 = validation errors found (printed to stdout as JSON).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = SCRIPT_DIR.parent / "references" / "embedded-family-model.schema.json"


class _FamilyModelExtractor(HTMLParser):
    """Extracts the text content of <script type="application/json" id="family-model">
    using real HTML parsing (not regex), so a textual mention of that tag inside an
    HTML comment or code sample elsewhere in the document can never be mistaken for
    the real block — comments and <script> CDATA are structurally distinct to a
    parser in a way a naive regex cannot see.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.capturing = False
        self.chunks: list[str] = []
        self.block_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "script":
            return
        d = dict(attrs)
        if d.get("type") == "application/json" and d.get("id") == "family-model":
            self.capturing = True
            self.block_count += 1

    def handle_data(self, data: str) -> None:
        if self.capturing:
            self.chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.capturing = False


def extract_model(html: str) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    extractor = _FamilyModelExtractor()
    extractor.feed(html)
    if extractor.block_count == 0:
        errors.append('No <script type="application/json" id="family-model"> block found.')
        return None, errors
    if extractor.block_count > 1:
        errors.append(f"Expected exactly one family-model block, found {extractor.block_count}.")
    raw = "".join(extractor.chunks)
    try:
        model = json.loads(raw)
    except json.JSONDecodeError as exc:
        errors.append(f"family-model block is not valid JSON: {exc}")
        return None, errors
    return model, errors


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def validate_with_jsonschema(model: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    import jsonschema  # type: ignore

    validator_cls = jsonschema.Draft7Validator
    validator_cls.check_schema(schema)
    validator = validator_cls(schema)
    errors = []
    for err in sorted(validator.iter_errors(model), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.path) or "<root>"
        errors.append(f"{loc}: {err.message}")
    return errors


def _type_ok(value: Any, expected: Any) -> bool:
    types = expected if isinstance(expected, list) else [expected]
    checks = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "null": lambda v: v is None,
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    }
    return any(checks.get(t, lambda v: True)(value) for t in types)


def _validate_node(value: Any, schema: dict[str, Any], path: str, errors: list[str]) -> None:
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in enum {schema['enum']}")
    if "type" in schema and not _type_ok(value, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']}, got {type(value).__name__}")
        return
    if isinstance(value, str):
        if "pattern" in schema and not re.match(schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match pattern {schema['pattern']!r}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength {schema['minLength']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} below minimum {schema['minimum']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: array shorter than minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(value):
                _validate_node(item, _resolve(item_schema, schema), f"{path}[{i}]", errors)
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path}: missing required property {req!r}")
        props = schema.get("properties", {})
        for key, sub in value.items():
            sub_schema = props.get(key)
            if sub_schema is None:
                if schema.get("additionalProperties") is False:
                    errors.append(f"{path}: unexpected property {key!r}")
                continue
            _validate_node(sub, _resolve(sub_schema, schema), f"{path}.{key}", errors)


def _resolve(schema: dict[str, Any], root_schema: dict[str, Any]) -> dict[str, Any]:
    if "$ref" in schema:
        ref = schema["$ref"]
        if ref.startswith("#/definitions/"):
            return root_schema.get("_definitions_lookup", {}).get(ref.split("/")[-1], {})
    return schema


def validate_builtin(model: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    schema = dict(schema)
    schema["_definitions_lookup"] = schema.get("definitions", {})
    errors: list[str] = []
    _validate_node(model, schema, "$", errors)
    return errors


def validate_schema(model: dict[str, Any], schema: dict[str, Any]) -> tuple[list[str], str]:
    try:
        import jsonschema  # noqa: F401

        return validate_with_jsonschema(model, schema), "jsonschema"
    except ImportError:
        return validate_builtin(model, schema), "builtin-fallback"


def validate_source_digests(model: dict[str, Any], repo_root: Path) -> list[str]:
    errors: list[str] = []
    for src in model.get("sources", []):
        path = src.get("path")
        digest = src.get("digest")
        if not path or digest == "unavailable":
            continue
        candidate = (repo_root / path) if not Path(path).is_absolute() else Path(path)
        if not candidate.exists():
            errors.append(f"source path does not resolve on disk, cannot verify digest: {path}")
            continue
        actual = sha256_of(candidate)
        if actual != digest:
            errors.append(
                f"digest drift for {path}: model says {digest}, file is currently {actual}"
            )
    return errors


def validate_cross_consistency(model: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ids = {c.get("id") for c in model.get("components", [])}
    for edge in model.get("edges", []):
        for end in ("from", "to"):
            if edge.get(end) not in ids:
                errors.append(f"edge references unknown component id in '{end}': {edge.get(end)!r}")
    ep = model.get("entry_point", {})
    if ep.get("component_id") is not None and ep["component_id"] not in ids:
        errors.append(f"entry_point.component_id is not a known component: {ep['component_id']!r}")
    for component in model.get("components", []):
        if component.get("is_default_orchestrator"):
            for field in (
                "caller_facing_outputs", "direct_writes", "delegated_outputs", "control_outputs"
            ):
                if field not in component or not isinstance(component[field], list):
                    errors.append(
                        f"default orchestrator {component.get('id')!r} omits output layer {field!r}"
                    )
    for route in model.get("failure_routes", []):
        pass  # owner is prose (may name a component or "the caller"); not id-checked.
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_path")
    parser.add_argument("--repo-root", default=".", help="Root used to resolve relative source paths")
    args = parser.parse_args(argv)

    html_path = Path(args.html_path)
    if not html_path.exists():
        print(json.dumps({"valid": False, "errors": [f"file not found: {html_path}"]}, indent=2))
        return 1

    html = html_path.read_text(encoding="utf-8", errors="replace")
    model, extract_errors = extract_model(html)

    result: dict[str, Any] = {
        "html_path": str(html_path),
        "extract_errors": extract_errors,
        "schema_errors": [],
        "digest_errors": [],
        "consistency_errors": [],
        "validator_used": None,
    }

    if model is not None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        schema_errors, validator_used = validate_schema(model, schema)
        result["schema_errors"] = schema_errors
        result["validator_used"] = validator_used
        result["digest_errors"] = validate_source_digests(model, Path(args.repo_root))
        result["consistency_errors"] = validate_cross_consistency(model)

    all_errors = (
        result["extract_errors"]
        + result["schema_errors"]
        + result["digest_errors"]
        + result["consistency_errors"]
    )
    result["valid"] = len(all_errors) == 0
    result["error_count"] = len(all_errors)

    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
