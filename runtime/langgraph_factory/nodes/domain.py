"""Curriculum-domain validation and admission.

Owns D08. A candidate domain version reaches this node from a model; nothing
about it is trusted until the curriculum's own executable verifier, the domain
schema, and the admitted source set have each said so.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

from . import (
    SystemFailure,
    candidate_payload,
    check_record,
    contract_reference,
    deterministic_node,
    guard,
    head_update,
    is_model_candidate,
    latest_candidate,
    mint_version,
    require,
    require_current_parent,
    staged_dispatch,
    stream_id,
    worker_packet,
)
from .sources import DOMAIN_SCHEMA_CONTRACT

__all__ = ["DOMAIN_CHECK_IDS", "CURRICULUM_CONTRACTS", "D08_VALIDATE_DOMAIN"]


DOMAIN_CHECK_IDS: tuple[str, ...] = (
    "domain_schema_valid",
    "domain_facts_sourced",
    "domain_verifier_fixtures",
)

VERIFIER_CODE_BOUNDARIES: dict[str, tuple[str, ...]] = {
    "domain-schema-invalid": ("/",),
    "polarity-unevidenced": ("/build_map", "/electrical/component_spec/parameters"),
    "supply-not-permitted": ("/power_profile",),
    "current-limit-absent": (
        "/electrical/ratings_and_limits",
        "/electrical/calculations",
    ),
    "rail-short": ("/electrical/circuit/nets",),
    "input-floating": ("/electrical/circuit",),
    "composed-circuit-invented": ("/circuit_reference",),
}

# The frozen contracts a unit's prose must satisfy. D09 validates against them,
# so M03 is handed the same two rather than a paraphrase of them. The first is a
# per-*unit* content contract: `curriculum.schema.v5.json` describes a whole
# curriculum manifest and shares no property with a unit content document, so
# holding one to the other admits nothing at all.
CURRICULUM_CONTRACTS: tuple[str, ...] = (
    "schemas/unit_content.schema.v1.json",
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


def _mint_domain_version(
    artifact_versions: list[Any],
    heads: dict[str, Any],
    stream: str,
    unit_id: str,
    schema_path: str,
) -> dict[str, Any] | None:
    """Mint the domain version M02's candidate authorizes, or None if it produced none.

    M02 emits `{"domain_version": {unit_id, fields, evidence_references}}` and no
    version or hash of its own. The artifact body is `fields` — the open document
    the curriculum's declared schema and the verifier pointer both address; the
    wrapper around it is lineage M02 already checked against the admitted sources.
    """

    records = [
        record for record in artifact_versions
        if is_model_candidate(record)
        and record.get("job_id") == "M02_CREATE_UNIT_DOMAIN_DATA"
        and record.get("channel") == "domain"
        and record.get("unit_id") == unit_id
    ]
    record = records[-1] if records else None
    if record is None:
        return None
    if any(
        isinstance(existing, dict)
        and existing.get("stream") == stream
        and existing.get("candidate_key") == record.get("key")
        for existing in artifact_versions
    ):
        return None
    payload = candidate_payload(record, f"domain candidate on {stream}")
    declared = payload.get("domain_version")
    require(
        isinstance(declared, dict),
        "schema_contract",
        "the domain candidate declares no domain_version",
    )
    body = declared.get("fields")
    require(
        isinstance(body, dict),
        "schema_contract",
        "the domain candidate declares no domain fields",
    )
    return mint_version(
        record,
        heads,
        stream,
        body=body,
        unit_id=unit_id,
        channel="domain",
        schema_path=schema_path,
        evidence_references=declared.get("evidence_references", []),
    )


@deterministic_node("D08_VALIDATE_DOMAIN")
def D08_VALIDATE_DOMAIN(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Validate a candidate domain version and admit it, or emit repairable findings."""

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")
    stream = stream_id(unit_id, "domain")

    heads = projection["artifact_heads"]
    effective_run = projection["effective_run"]
    domain_contract = effective_run.get("domain_contract")
    # Compatibility for isolated legacy fixtures. A production D02 always
    # supplies the complete compiled contract and never reaches this fallback.
    domain_schema = (
        domain_contract["schema"]["path"]
        if isinstance(domain_contract, dict)
        else effective_run.get("manifest_schema") or DOMAIN_SCHEMA_CONTRACT
    )
    minted = _mint_domain_version(
        projection["artifact_versions"], heads, stream, unit_id, str(domain_schema)
    )
    current_head = heads.get(stream)
    admitted_current = next(
        (
            record for record in projection["artifact_versions"]
            if isinstance(record, dict)
            and record.get("stream") == stream
            and isinstance(current_head, dict)
            and record.get("hash") == current_head.get("hash")
        ),
        None,
    )
    candidate = minted or admitted_current or latest_candidate(projection["artifact_versions"], stream)
    require(
        candidate is not None,
        "invalid_input",
        f"no candidate domain version exists on {stream}",
    )
    if candidate is admitted_current:
        require(
            candidate.get("version") == current_head.get("version")
            and candidate.get("hash") == current_head.get("hash"),
            "integrity",
            "the revalidated domain record is not the exact current head",
            stream=stream,
        )
    else:
        require_current_parent(candidate, heads, stream)

    body = candidate.get("body")
    require(isinstance(body, dict), "schema_contract", "candidate domain body must be an object")

    engine_root = Path(projection["engine_root"])
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

    if isinstance(domain_contract, dict):
        frozen_schema = domain_contract.get("schema")
        require(
            isinstance(frozen_schema, dict)
            and schema_relative == frozen_schema.get("path"),
            "integrity",
            "candidate domain names a schema other than the D02-frozen contract",
            candidate=schema_relative,
            frozen=(frozen_schema or {}).get("path") if isinstance(frozen_schema, dict) else None,
        )
        try:
            schema_bytes = schema_path.read_bytes()
        except OSError as error:
            raise SystemFailure("schema_contract", f"domain schema is unreadable: {error}") from error
        actual_schema_sha = hashlib.sha256(schema_bytes).hexdigest()
        require(
            actual_schema_sha == frozen_schema.get("sha256"),
            "integrity",
            "domain schema changed after D02 froze it",
            path=str(schema_path),
            expected=frozen_schema.get("sha256"),
            actual=actual_schema_sha,
        )
        try:
            schema = json.loads(schema_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise SystemFailure("schema_contract", f"domain schema is not valid JSON: {error}") from error
    else:
        # Isolated node fixtures may still supply the historic narrow state;
        # every production D02 output carries the complete contract above.
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

    # The M02 wrapper's evidence references are the only source identities the
    # model is allowed to cite. Re-check the relationship here because D08, not
    # the adapter, is admission authority.
    admitted_by_source = {
        admission.get("key"): admission
        for admission in projection["source_admissions"]
        if isinstance(admission, dict) and admission.get("unit_id") == unit_id
    }
    admitted_by_fact = {
        admission.get("fact_id"): admission
        for admission in admitted_by_source.values()
    }
    if isinstance(domain_contract, dict):
        evidence_references = candidate.get("evidence_references") or []
        cited = [
            str(reference.get("source_id"))
            for reference in evidence_references
            if isinstance(reference, dict)
        ]
        unsourced = sorted(set(cited) - set(admitted_by_source))
        if not cited:
            unsourced.append("<no-evidence-reference>")
    else:
        unsourced = sorted(
            str(fact.get("fact_id"))
            for fact in body.get("facts", [])
            if isinstance(fact, dict) and fact.get("fact_id") not in admitted_by_fact
        )
    checks.append(
        check_record(
            scope="unit",
            owner=unit_id,
            head_hash=head_hash,
            check_id="domain_facts_sourced",
            attempt=attempt,
            result="PASS" if not unsourced else "FAIL",
            detail={"unsourced": unsourced, "admitted_count": len(admitted_by_source)},
        )
    )
    for fact_id in unsourced:
        findings.append(
            {
                "check_id": "domain_facts_sourced",
                "owner": "source interpretation",
                "pointer": f"/facts/{fact_id}",
                "message": f"domain fact {fact_id} resolves to no admitted source",
                "parent_hash": head_hash,
            }
        )

    if isinstance(domain_contract, dict):
        verifier_service = getattr(runtime_context, "transport_registry", None)
        verify_domain = getattr(verifier_service, "verify_domain", None)
        require(callable(verify_domain), "capability", "runtime exposes no domain verifier service")
        verifier = verify_domain(body=body, contract=domain_contract)
        require(
            isinstance(verifier, dict)
            and verifier.get("candidate_sha256") == head_hash
            and verifier.get("fixtures_result") == "PASS",
            "integrity",
            "domain verifier returned an unbound or incomplete receipt",
            expected_candidate=head_hash,
            observed_candidate=(verifier or {}).get("candidate_sha256")
            if isinstance(verifier, dict) else None,
        )
        verifier_passed = verifier.get("result") == "PASS"
        verifier_codes = list((verifier.get("candidate") or {}).get("codes") or [])
    else:
        # Legacy node fixtures predate executable-verifier injection. Production
        # state cannot use this branch because D02 always writes domain_contract.
        declared = candidate.get("verifier_result", body.get("verifier_result"))
        verifier_passed = isinstance(declared, dict) and declared.get("result") == "all_fixtures_behaved"
        verifier_codes = [] if verifier_passed else ["legacy-verifier-failed"]
        verifier = {"result": "PASS" if verifier_passed else "FAIL", "declared": declared}
    checks.append(
        check_record(
            scope="unit",
            owner=unit_id,
            head_hash=head_hash,
            check_id="domain_verifier_fixtures",
            attempt=attempt,
            result="PASS" if verifier_passed else "FAIL",
            detail={"receipt": verifier},
        )
    )
    if not verifier_passed:
        for code in verifier_codes or ["verifier-rejected"]:
            # A schema error already has the validator's exact instance pointer;
            # do not add a second broad root finding for the same defect.
            if code == "domain-schema-invalid" and errors:
                continue
            for pointer in VERIFIER_CODE_BOUNDARIES.get(code, ("/",)):
                findings.append(
                    {
                        "check_id": "domain_verifier_fixtures",
                        "owner": "curriculum domain",
                        "pointer": pointer,
                        "message": f"curriculum verifier rejected the candidate with {code}",
                        "parent_hash": head_hash,
                    }
                )

    for finding in findings:
        finding.setdefault("parent_hash", head_hash)

    if findings:
        update: dict[str, Any] = {
            "deterministic_checks": checks,
            "pending_guard": guard(
                "D08_VALIDATE_DOMAIN", "domain_repairable", unit_id=unit_id, findings=findings
            ),
        }
        # Preserve a first-version candidate as immutable M06 parent bytes. It
        # remains pre-admission because no head update accompanies this record.
        if minted is not None:
            update["artifact_versions"] = [minted]
        return update

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
                "fields": body,
                "facts": body.get("facts", []),
            },
            "curriculum_contracts": [
                contract_reference(engine_root, relative) for relative in CURRICULUM_CONTRACTS
            ],
            "admitted_evidence_references": [
                {"source_id": source_id, "fact_id": admission["fact_id"]}
                for source_id, admission in sorted(
                    admitted_by_source.items(), key=lambda item: str(item[0])
                )
            ],
        },
    )

    update = {
        "artifact_heads": head_update(candidate, stream),
        "deterministic_checks": checks,
        "pending_packet": staged_dispatch("M03_WRITE_UNIT_CONTENT", [packet]),
        "pending_guard": guard("D08_VALIDATE_DOMAIN", "domain_admitted", unit_id=unit_id),
    }
    if minted is not None:
        update["artifact_versions"] = [minted]
    return update
