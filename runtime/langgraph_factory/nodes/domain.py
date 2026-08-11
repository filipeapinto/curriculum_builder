"""Curriculum-domain validation and admission.

Owns D08. A candidate domain version reaches this node from a model; nothing
about it is trusted until the curriculum's own executable verifier, the domain
schema, and the admitted source set have each said so.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from . import (
    SystemFailure,
    check_record,
    contract_reference,
    deterministic_node,
    guard,
    head_update,
    latest_candidate,
    require,
    require_current_parent,
    staged_dispatch,
    stream_id,
    worker_packet,
)

__all__ = ["DOMAIN_CHECK_IDS", "CURRICULUM_CONTRACTS", "D08_VALIDATE_DOMAIN"]


DOMAIN_CHECK_IDS: tuple[str, ...] = (
    "domain_schema_valid",
    "domain_facts_sourced",
    "domain_verifier_fixtures",
)

# The frozen contracts a unit's prose must satisfy. D09 validates against them,
# so M03 is handed the same two rather than a paraphrase of them.
CURRICULUM_CONTRACTS: tuple[str, ...] = (
    "schemas/curriculum.schema.v5.json",
    "meta_prompt/assets/unit_prose.v1.md",
)


def _load_json(path: Path, label: str) -> Any:
    require(path.is_file(), "schema_contract", f"{label} is missing", path=str(path))
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemFailure(
            "schema_contract", f"{label} is not parseable JSON: {error}", {"path": str(path)}
        ) from error


@deterministic_node("D08_VALIDATE_DOMAIN")
def D08_VALIDATE_DOMAIN(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Validate a candidate domain version and admit it, or emit repairable findings."""

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")
    stream = stream_id(unit_id, "domain")

    candidate = latest_candidate(projection["artifact_versions"], stream)
    require(
        candidate is not None,
        "invalid_input",
        f"no candidate domain version exists on {stream}",
    )
    require_current_parent(candidate, projection["artifact_heads"], stream)

    body = candidate.get("body")
    require(isinstance(body, dict), "schema_contract", "candidate domain body must be an object")

    engine_root = Path(projection["engine_root"])
    effective_run = projection["effective_run"]
    manifest_domain = None
    for unit in effective_run.get("unit_records", []):
        if isinstance(unit, dict) and unit.get("id") == unit_id:
            manifest_domain = unit
    require(manifest_domain is not None, "invalid_input", f"unit {unit_id!r} is not in the run")

    schema_relative = candidate.get("schema_path")
    require(
        isinstance(schema_relative, str) and schema_relative,
        "schema_contract",
        "candidate domain declares no schema path",
    )
    schema_path = (engine_root / schema_relative).resolve()
    require(
        engine_root in schema_path.parents,
        "integrity",
        "the declared domain schema escapes the engine root",
        schema=str(schema_path),
    )

    attempt = int(candidate.get("attempt", 1))
    head_hash = str(candidate["hash"])
    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    schema = _load_json(schema_path, "domain schema")
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(body),
        key=lambda error: list(error.absolute_path),
    )
    checks.append(
        check_record(
            scope="unit",
            owner=unit_id,
            head_hash=head_hash,
            check_id="domain_schema_valid",
            attempt=attempt,
            result="PASS" if not errors else "FAIL",
            detail={"error_count": len(errors)},
        )
    )
    for error in errors:
        findings.append(
            {
                "check_id": "domain_schema_valid",
                "owner": "curriculum domain",
                "pointer": "/" + "/".join(str(part) for part in error.absolute_path),
                "message": error.message,
            }
        )

    # Every declared domain fact must resolve to an admitted source: an
    # unsourced fact is exactly the defect the source path exists to prevent.
    admitted = {
        admission.get("fact_id"): admission
        for admission in projection["source_admissions"]
        if isinstance(admission, dict) and admission.get("unit_id") == unit_id
    }
    unsourced = sorted(
        str(fact.get("fact_id"))
        for fact in body.get("facts", [])
        if isinstance(fact, dict) and fact.get("fact_id") not in admitted
    )
    checks.append(
        check_record(
            scope="unit",
            owner=unit_id,
            head_hash=head_hash,
            check_id="domain_facts_sourced",
            attempt=attempt,
            result="PASS" if not unsourced else "FAIL",
            detail={"unsourced": unsourced, "admitted_count": len(admitted)},
        )
    )
    for fact_id in unsourced:
        findings.append(
            {
                "check_id": "domain_facts_sourced",
                "owner": "source interpretation",
                "pointer": f"/facts/{fact_id}",
                "message": f"domain fact {fact_id} resolves to no admitted source",
            }
        )

    verifier = candidate.get("verifier_result")
    verifier_passed = isinstance(verifier, dict) and verifier.get("result") == "all_fixtures_behaved"
    checks.append(
        check_record(
            scope="unit",
            owner=unit_id,
            head_hash=head_hash,
            check_id="domain_verifier_fixtures",
            attempt=attempt,
            result="PASS" if verifier_passed else "FAIL",
            detail={"declared": verifier},
        )
    )
    if not verifier_passed:
        findings.append(
            {
                "check_id": "domain_verifier_fixtures",
                "owner": "curriculum domain",
                "pointer": "/verifier",
                "message": "the curriculum executable verifier did not prove its fixtures",
            }
        )

    if findings:
        return {
            "deterministic_checks": checks,
            "pending_guard": guard(
                "D08_VALIDATE_DOMAIN", "domain_repairable", unit_id=unit_id, findings=findings
            ),
        }

    packet = worker_packet(
        run_id=projection["run_id"],
        episode_id=projection["episode_id"],
        correlation_key=f"{unit_id}/{head_hash}/content",
        projection={
            "unit": {
                "unit_id": unit_id,
                "title": manifest_domain.get("title"),
            },
            "admitted_domain": {
                "unit_id": unit_id,
                "domain_hash": head_hash,
                "version": candidate["version"],
                "facts": body.get("facts", []),
            },
            "curriculum_contracts": [
                contract_reference(engine_root, relative) for relative in CURRICULUM_CONTRACTS
            ],
            "admitted_evidence_references": [
                {"source_id": admission["key"], "fact_id": fact_id}
                for fact_id, admission in sorted(admitted.items(), key=lambda item: str(item[0]))
            ],
        },
    )

    return {
        "artifact_heads": head_update(candidate, stream),
        "deterministic_checks": checks,
        "pending_packet": staged_dispatch("M03_WRITE_UNIT_CONTENT", [packet]),
        "pending_guard": guard("D08_VALIDATE_DOMAIN", "domain_admitted", unit_id=unit_id),
    }
