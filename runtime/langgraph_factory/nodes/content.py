"""Unit content validation and admission.

Owns D09. Content is validated against the *currently admitted* domain head, not
the domain the author happened to see: a content version derived from a
superseded domain is stale by definition and is refused here rather than
discovered at review.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from . import (
    SystemFailure,
    check_record,
    deterministic_node,
    guard,
    head_update,
    latest_candidate,
    require,
    require_current_parent,
    stream_id,
)

__all__ = ["CONTENT_CHECK_IDS", "D09_VALIDATE_CONTENT"]


CONTENT_CHECK_IDS: tuple[str, ...] = (
    "content_schema_valid",
    "content_domain_current",
    "content_derivation_resolves",
    "content_claims_grounded",
)


@deterministic_node("D09_VALIDATE_CONTENT")
def D09_VALIDATE_CONTENT(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Validate candidate unit content against the admitted domain, or emit findings."""

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")
    content_stream = stream_id(unit_id, "content")
    domain_stream = stream_id(unit_id, "domain")

    heads = projection["artifact_heads"]
    domain_head = heads.get(domain_stream)
    require(
        isinstance(domain_head, dict),
        "invalid_input",
        "content validation requires an admitted domain head",
        stream=domain_stream,
    )

    candidate = latest_candidate(projection["artifact_versions"], content_stream)
    require(candidate is not None, "invalid_input", f"no candidate content on {content_stream}")
    require_current_parent(candidate, heads, content_stream)

    body = candidate.get("body")
    require(isinstance(body, dict), "schema_contract", "candidate content body must be an object")

    attempt = int(candidate.get("attempt", 1))
    head_hash = str(candidate["hash"])
    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    engine_root = Path(projection["engine_root"])
    schema_relative = candidate.get("schema_path")
    require(
        isinstance(schema_relative, str) and schema_relative,
        "schema_contract",
        "candidate content declares no schema path",
    )
    schema_path = (engine_root / schema_relative).resolve()
    require(
        engine_root in schema_path.parents,
        "integrity",
        "the declared content schema escapes the engine root",
        schema=str(schema_path),
    )
    require(schema_path.is_file(), "schema_contract", "the declared content schema is missing")
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemFailure(
            "schema_contract", f"content schema is not parseable JSON: {error}"
        ) from error

    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(body),
        key=lambda error: list(error.absolute_path),
    )
    checks.append(
        check_record(
            scope="unit",
            owner=unit_id,
            head_hash=head_hash,
            check_id="content_schema_valid",
            attempt=attempt,
            result="PASS" if not errors else "FAIL",
            detail={"error_count": len(errors)},
        )
    )
    for error in errors:
        findings.append(
            {
                "check_id": "content_schema_valid",
                "owner": "unit content",
                "pointer": "/" + "/".join(str(part) for part in error.absolute_path),
                "message": error.message,
            }
        )

    # A content candidate names the domain hash it derived from. A mismatch is a
    # stale parent, not a repairable content defect: the content was written
    # against facts that are no longer admitted.
    declared_domain = candidate.get("domain_hash")
    domain_current = declared_domain == domain_head.get("hash")
    if not domain_current:
        raise SystemFailure(
            "integrity",
            "candidate content was derived from a domain version that is no longer the head",
            {
                "declared_domain_hash": declared_domain,
                "current_domain_hash": domain_head.get("hash"),
                "unit_id": unit_id,
            },
        )
    checks.append(
        check_record(
            scope="unit",
            owner=unit_id,
            head_hash=head_hash,
            check_id="content_domain_current",
            attempt=attempt,
            result="PASS",
            detail={"domain_hash": declared_domain},
        )
    )

    unresolved = sorted(
        str(entry.get("pointer"))
        for entry in body.get("derivations", [])
        if isinstance(entry, dict) and not _resolves(body, entry.get("pointer"))
    )
    checks.append(
        check_record(
            scope="unit",
            owner=unit_id,
            head_hash=head_hash,
            check_id="content_derivation_resolves",
            attempt=attempt,
            result="PASS" if not unresolved else "FAIL",
            detail={"unresolved": unresolved},
        )
    )
    for pointer in unresolved:
        findings.append(
            {
                "check_id": "content_derivation_resolves",
                "owner": "unit content",
                "pointer": pointer,
                "message": f"declared derivation pointer {pointer} does not resolve",
            }
        )

    declared_evidence = {
        str(entry.get("evidence_key"))
        for entry in body.get("claims", [])
        if isinstance(entry, dict)
    }
    admitted_facts = {
        str(admission.get("fact_id"))
        for admission in body.get("admitted_facts", [])
        if isinstance(admission, dict)
    } or set(declared_evidence)
    ungrounded = sorted(declared_evidence - admitted_facts)
    checks.append(
        check_record(
            scope="unit",
            owner=unit_id,
            head_hash=head_hash,
            check_id="content_claims_grounded",
            attempt=attempt,
            result="PASS" if not ungrounded else "FAIL",
            detail={"ungrounded": ungrounded},
        )
    )
    for key in ungrounded:
        findings.append(
            {
                "check_id": "content_claims_grounded",
                "owner": "unit content",
                "pointer": f"/claims/{key}",
                "message": f"claim {key} resolves to no admitted evidence",
            }
        )

    if findings:
        return {
            "deterministic_checks": checks,
            "pending_guard": guard(
                "D09_VALIDATE_CONTENT", "content_repairable", unit_id=unit_id, findings=findings
            ),
        }

    return {
        "artifact_heads": head_update(candidate, content_stream),
        "deterministic_checks": checks,
        "pending_guard": guard("D09_VALIDATE_CONTENT", "content_admitted", unit_id=unit_id),
    }


def _resolves(document: Any, pointer: Any) -> bool:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        return False
    current = document
    for raw in pointer.lstrip("/").split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            if token not in current:
                return False
            current = current[token]
        elif isinstance(current, list):
            if not token.isdigit() or int(token) >= len(current):
                return False
            current = current[int(token)]
        else:
            return False
    return True
