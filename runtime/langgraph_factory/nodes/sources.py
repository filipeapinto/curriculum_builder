"""Unit selection, source request/retrieval compilation, admission, and prerequisites.

Owns D05, D06, D06B, D07, and D30. The source path's whole job is to turn a
manifest unit into a *closed* set of admitted primary-source facts: every node
here fails closed rather than admitting a fact whose retrieval, hash, or
correlation cannot be reproduced.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from . import (
    PrerequisitePause,
    SystemFailure,
    candidate_field,
    canonical_digest,
    contract_reference,
    deterministic_node,
    guard,
    require,
    staged_dispatch,
    worker_packet,
)
from ..egress import AuthorizationRecord, EgressDenied, authorize_transmission

__all__ = [
    "SOURCE_REQUEST_FIELDS",
    "SOURCE_RULES",
    "DOMAIN_SCHEMA_CONTRACT",
    "DOMAIN_CALIBRATION_CONTRACT",
    "compile_unit_source_requests",
    "D05_SELECT_NEXT_UNIT",
    "D06_COMPILE_SOURCE_REQUESTS",
    "D06B_RETRIEVE_SOURCE_CANDIDATES",
    "D07_CORRELATE_AND_ADMIT_SOURCES",
    "D30_CLASSIFY_PREREQUISITE",
]


# The rules an M01 worker is bound by in either phase. They are the engine's own
# invariants, stated to the worker: D06B retrieves every byte, so a locator set
# is all a discovery may produce, and D07 admits nothing whose request
# correlation it cannot reproduce.
SOURCE_RULES: dict[str, Any] = {
    "primary_sources_only": True,
    "max_locators_per_request": 3,
    "must_cite_request_id": True,
    "bytes_retrieved_by": "controller",
}

DOMAIN_SCHEMA_CONTRACT = "schemas/manifest_domain.metaschema.v1.json"
DOMAIN_CALIBRATION_CONTRACT = "policy/calibration.v1.yaml"


SOURCE_REQUEST_FIELDS: tuple[str, ...] = (
    "key",
    "unit_id",
    "source_epoch",
    "fact_id",
    "question",
    "required",
    "scope",
)

# The manifest keys that declare facts a unit's content must be grounded in.
# These are engine-contract key names, not curriculum values: any manifest using
# the frozen schema declares them, whatever its subject.
_FACT_BEARING_KEYS: tuple[str, ...] = (
    "required_explanation",
    "core_activity",
    "safety_focus",
    "applications",
)


def _record(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), "schema_contract", f"{label} must be a JSON object")
    return dict(value)


def _unit_projection(unit: dict[str, Any]) -> dict[str, Any]:
    """The bounded unit facts a worker may see: identity and declared scope only."""

    return {
        "unit_id": unit.get("id"),
        "title": unit.get("title"),
        "declared_scope": {
            key: unit[key] for key in _FACT_BEARING_KEYS if unit.get(key) is not None
        },
    }


def _request_projection(request: dict[str, Any]) -> dict[str, Any]:
    """One source request, named by the identifier the candidate must cite back."""

    return {
        "request_id": request["key"],
        "unit_id": request["unit_id"],
        "source_epoch": request["source_epoch"],
        "fact_id": request["fact_id"],
        "question": request["question"],
        "required": request["required"],
        "scope": request["scope"],
    }


def _persist_retrieved_bytes(
    *, output_root: str, body: bytes, expected_sha256: str,
) -> tuple[str, str]:
    """Persist controller-retrieved bytes for one hash-bound staged input."""

    actual = hashlib.sha256(body).hexdigest()
    require(actual == expected_sha256, "integrity",
            "retrieval body does not match its egress receipt hash",
            expected_sha256=expected_sha256, actual_sha256=actual)
    directory = Path(output_root).resolve() / ".retrieved_sources"
    directory.mkdir(parents=True, exist_ok=True)
    source_path = directory / f"{actual}.bin"
    if source_path.exists():
        require(source_path.is_file() and not source_path.is_symlink(), "integrity",
                "retrieval staging target is not a regular file", path=str(source_path))
        require(hashlib.sha256(source_path.read_bytes()).hexdigest() == actual, "integrity",
                "retrieval staging target collides with different bytes", path=str(source_path))
    else:
        try:
            with source_path.open("xb") as handle:
                handle.write(body)
        except FileExistsError:
            require(source_path.is_file() and not source_path.is_symlink(), "integrity",
                    "retrieval staging target raced with a non-file", path=str(source_path))
            require(hashlib.sha256(source_path.read_bytes()).hexdigest() == actual, "integrity",
                    "retrieval staging race produced different bytes", path=str(source_path))
    return str(source_path), f"retrieved-{actual}.bin"


def _unit_record(effective_run: dict[str, Any], unit_id: str) -> dict[str, Any]:
    for unit in effective_run.get("unit_records", []):
        if isinstance(unit, dict) and unit.get("id") == unit_id:
            return unit
    raise SystemFailure(
        "invalid_input",
        f"unit {unit_id!r} is not in the frozen effective run",
        {"unit_id": unit_id},
    )


# --------------------------------------------------------------------------
# D05
# --------------------------------------------------------------------------


@deterministic_node("D05_SELECT_NEXT_UNIT")
def D05_SELECT_NEXT_UNIT(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Select the next required unaccepted unit in frozen manifest order."""

    effective_run = projection["effective_run"]
    require(bool(effective_run), "invalid_input", "unit selection requires a frozen effective run")

    closure = effective_run.get("target_closure")
    require(
        isinstance(closure, list) and bool(closure),
        "invalid_input",
        "the frozen effective run declares an empty target closure",
    )

    accepted = projection["accepted_unit_receipts"]
    cursor = dict(projection["cursor"])
    manifest_ordinal = cursor.get("manifest_ordinal", 0)
    accepted_ordinal = cursor.get("accepted_ordinal", 0)

    require(
        0 <= manifest_ordinal <= len(closure),
        "integrity",
        "the manifest cursor is outside the frozen closure",
        manifest_ordinal=manifest_ordinal,
        closure_size=len(closure),
    )
    require(
        accepted_ordinal == len([unit_id for unit_id in closure if unit_id in accepted]),
        "integrity",
        "the accepted cursor disagrees with the accepted receipt set",
        accepted_ordinal=accepted_ordinal,
        accepted_receipts=len([unit_id for unit_id in closure if unit_id in accepted]),
    )

    remaining = [unit_id for unit_id in closure if unit_id not in accepted]
    if not remaining:
        return {
            "cursor": {"manifest_ordinal": len(closure), "accepted_ordinal": accepted_ordinal},
            "selected_unit_id": None,
            "pending_guard": guard("D05_SELECT_NEXT_UNIT", "manifest_exhausted"),
        }

    selected = remaining[0]
    return {
        "selected_unit_id": selected,
        "unit_status": {selected: "SELECTED"},
        "cursor": {
            "manifest_ordinal": closure.index(selected) + 1,
            "accepted_ordinal": accepted_ordinal,
        },
        "pending_guard": guard("D05_SELECT_NEXT_UNIT", "unit_selected", unit_id=selected),
    }


# --------------------------------------------------------------------------
# D06
# --------------------------------------------------------------------------


def compile_unit_source_requests(unit: dict[str, Any], source_epoch: int) -> list[dict[str, Any]]:
    """Derive one bounded, named request per fact the unit must be grounded in.

    Manifest-neutral: fact identifiers are derived from the unit's own declared
    keys and values, so a unit with more or fewer declared facts produces
    correspondingly more or fewer requests.
    """

    unit_id = unit["id"]
    requests: list[dict[str, Any]] = []
    for key in _FACT_BEARING_KEYS:
        value = unit.get(key)
        if value is None:
            continue
        entries = value if isinstance(value, list) else [value]
        for ordinal, entry in enumerate(entries):
            fact_id = f"{key}:{ordinal:03d}"
            request = {
                "key": f"{unit_id}/{source_epoch}/{fact_id}",
                "unit_id": unit_id,
                "source_epoch": source_epoch,
                "fact_id": fact_id,
                "question": canonical_digest({"unit_id": unit_id, "fact_id": fact_id, "claim": entry}),
                "required": key in ("required_explanation", "safety_focus"),
                "scope": key,
            }
            requests.append(request)
    return requests


@deterministic_node("D06_COMPILE_SOURCE_REQUESTS")
def D06_COMPILE_SOURCE_REQUESTS(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Compile the complete positive source-request denominator for one unit."""

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")
    unit = _unit_record(projection["effective_run"], unit_id)

    authorizations = projection["external_authorizations"]
    allowed_hosts: list[str] = []
    if authorizations:
        latest = _record(authorizations[-1], "external authorization")
        allowed_hosts = sorted(
            host for host in (latest.get("resolved_hosts") or []) if isinstance(host, str))

    reusable = {
        admission.get("fact_id")
        for admission in projection["source_admissions"]
        if isinstance(admission, dict) and admission.get("unit_id") == unit_id
    }
    source_epoch = 1 + max(
        (
            admission.get("source_epoch", 0)
            for admission in projection["source_admissions"]
            if isinstance(admission, dict) and admission.get("unit_id") == unit_id
        ),
        default=0,
    )

    requests = [
        request
        for request in compile_unit_source_requests(unit, source_epoch)
        if request["fact_id"] not in reusable
    ]

    unresolvable = [
        request["fact_id"]
        for request in requests
        if request["required"] and not request["question"]
    ]
    if unresolvable:
        raise PrerequisitePause(
            "required_external_fact_unavailable",
            "a required fact has no bounded question that could resolve it",
            {"unit_id": unit_id, "fact_ids": sorted(unresolvable)},
        )

    require(
        bool(requests) or bool(reusable),
        "invalid_input",
        f"unit {unit_id!r} declares no fact-bearing content to ground",
        unit_id=unit_id,
    )

    denominator = {
        f"{unit_id}/{source_epoch}": {
            "unit_id": unit_id,
            "source_epoch": source_epoch,
            "request_keys": sorted(request["key"] for request in requests),
            "reused_fact_ids": sorted(reusable),
            "size": len(requests),
        }
    }

    run_id = projection["run_id"]
    episode_id = projection["episode_id"]
    packets = [
        worker_packet(
            run_id=run_id,
            episode_id=episode_id,
            correlation_key=request["key"],
            phase="DISCOVER",
            projection={
                "request": _request_projection(request),
                "unit": _unit_projection(unit),
                "source_rules": dict(SOURCE_RULES),
                "discovery_authority": {
                    "phase": "DISCOVER",
                    "locators_only": True,
                    "may_retrieve_bytes": False,
                    "allowed_hosts": allowed_hosts,
                },
            },
        )
        for request in sorted(requests, key=lambda item: item["key"])
    ]

    return {
        "source_requests": requests,
        "source_denominators": denominator,
        "pending_packet": staged_dispatch("M01_RESEARCH_UNIT_SOURCES", packets),
        "pending_guard": guard(
            "D06_COMPILE_SOURCE_REQUESTS",
            "discovery_fanout",
            unit_id=unit_id,
            request_keys=sorted(request["key"] for request in requests),
        ),
    }


# --------------------------------------------------------------------------
# D06B
# --------------------------------------------------------------------------


@deterministic_node("D06B_RETRIEVE_SOURCE_CANDIDATES")
def D06B_RETRIEVE_SOURCE_CANDIDATES(
    projection: dict[str, Any], runtime_context: Any
) -> dict[str, Any]:
    """Retrieve source bytes deterministically under the frozen host allowlist.

    Retrieval is the controller's job, never a model worker's: a model that could
    fetch its own bytes could also fabricate their provenance.
    """

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")

    denominator_key = None
    denominator = None
    for key, value in sorted(projection["source_denominators"].items()):
        if isinstance(value, dict) and value.get("unit_id") == unit_id:
            denominator_key, denominator = key, value
    require(
        denominator is not None,
        "invalid_input",
        f"no source denominator exists for unit {unit_id!r}",
    )

    requests = {
        request["key"]: request
        for request in projection["source_requests"]
        if isinstance(request, dict) and request.get("key") in denominator["request_keys"]
    }
    require(
        sorted(requests) == sorted(denominator["request_keys"]),
        "join",
        "the request set does not equal the frozen request denominator",
        expected=sorted(denominator["request_keys"]),
        actual=sorted(requests),
    )

    retriever = getattr(runtime_context, "source_retriever", None)
    require(retriever is not None, "capability", "runtime context exposes no source retriever")
    fetch = getattr(retriever, "fetch", None)
    require(callable(fetch), "capability", "the source retriever exposes no fetch operation")

    authorizations = projection["external_authorizations"]
    require(
        bool(authorizations),
        "authorization",
        "retrieval requires a current external-data authorization record",
    )
    authorization_raw = _record(authorizations[-1], "external authorization")
    authorization_record = AuthorizationRecord(
        run_id=projection["run_id"],
        curriculum_digest=authorization_raw.get("curriculum_digest", ""),
        output_root=authorization_raw.get("output_root", ""),
        approved_at_utc=str(authorization_raw.get("approved_at_utc", "")),
        expires_at_utc=str(authorization_raw.get("expires_at_utc", "")),
        providers=authorization_raw.get("providers") or {},
    )

    retrievals: dict[str, Any] = {}
    unavailable: list[dict[str, Any]] = []
    for request_key, discovery in sorted(projection["source_discoveries"].items()):
        if request_key not in requests:
            continue
        record = _record(discovery, f"discovery for {request_key}")
        locators = candidate_field(record, "locators") or []
        require(
            isinstance(locators, list),
            "schema_contract",
            f"discovery for {request_key} declares a non-list locator set",
        )
        if not locators:
            if requests[request_key].get("required"):
                unavailable.append({"request_key": request_key, "reason": "no locator discovered"})
            continue
        candidate_failures: list[dict[str, Any]] = []
        for locator in locators:
            locator_url = candidate_field(locator, "url")
            require(
                isinstance(locator_url, str) and locator_url,
                "schema_contract",
                f"discovery for {request_key} declares a locator with no url",
            )
            try:
                authorization_receipt = authorize_transmission(
                    authorization_record, provider="primary_source_hosts",
                    data_classes=["primary_source_bytes"],
                    curriculum_digest=authorization_record.curriculum_digest,
                    run_id=authorization_record.run_id,
                    output_root=authorization_record.output_root)
                response = fetch(locator_url, authorization_receipt=authorization_receipt)
            except (FileNotFoundError, EgressDenied) as error:
                # An untrusted candidate may be gone, forbidden, redirected out
                # of policy, or return a non-OK status. Try the remaining
                # bounded candidates in their model-produced order. If none is
                # retrievable, the named fact is unavailable; no bytes are
                # fabricated and no security denial is weakened.
                candidate_failures.append({
                    "locator": locator,
                    "reason": getattr(error, "reason", str(error)),
                })
                continue
            except Exception as error:  # noqa: BLE001 - classified below, never swallowed
                # A transport, network, or integrity fault is a system failure.
                # Only a named unavailable fact may pause.
                raise SystemFailure(
                    "tool",
                    f"deterministic retrieval failed for {request_key}: {error}",
                    {"request_key": request_key, "locator": locator},
                ) from error

            require(
                isinstance(response, tuple) and len(response) == 2,
                "schema_contract",
                f"retrieval response for {request_key} must be a (body, receipt) tuple",
            )
            body, receipt = response
            require(
                isinstance(body, bytes),
                "schema_contract",
                f"retrieval response for {request_key} carries non-byte content",
            )
            response_record = _record(receipt, f"retrieval receipt for {request_key}")
            for field in ("bytes_sha256", "http_status", "content_type"):
                require(
                    field in response_record,
                    "integrity",
                    f"retrieval receipt for {request_key} has no {field!r}",
                )
            source_path, staged_name = _persist_retrieved_bytes(
                output_root=authorization_record.output_root,
                body=body,
                expected_sha256=response_record["bytes_sha256"],
            )
            retrievals[request_key] = {
                "key": request_key,
                "unit_id": unit_id,
                "source_epoch": denominator["source_epoch"],
                "locator": locator,
                "sha256": response_record["bytes_sha256"],
                "status": response_record["http_status"],
                "content_type": response_record["content_type"],
                "tls": response_record.get("tls"),
                "bytes_path": staged_name,
                "source_path": source_path,
            }
            break
        if request_key not in retrievals and requests[request_key].get("required"):
            unavailable.append({
                "request_key": request_key,
                "reason": "all locator candidates unavailable",
                "candidates": candidate_failures,
            })

    missing_required = [
        {"request_key": key, "reason": "not retrieved"}
        for key, request in sorted(requests.items())
        if request.get("required") and key not in retrievals
    ]
    for entry in missing_required:
        if entry["request_key"] not in {item["request_key"] for item in unavailable}:
            unavailable.append(entry)

    if unavailable:
        raise PrerequisitePause(
            "required_external_fact_unavailable",
            "a named required external fact could not be retrieved",
            {"unit_id": unit_id, "denominator": denominator_key, "facts": unavailable},
        )

    unit = _unit_projection(_unit_record(projection["effective_run"], unit_id))
    run_id = projection["run_id"]
    episode_id = projection["episode_id"]
    packets: list[dict[str, Any]] = []
    for request_key in sorted(retrievals):
        retrieval = retrievals[request_key]
        group = {
            "group_id": canonical_digest(
                {"request_id": request_key, "retrieval_sha256": retrieval["sha256"]}
            ),
            "unit_id": unit_id,
            "source_epoch": retrieval["source_epoch"],
            "retrieved_records": [
                {
                    "retrieval_id": request_key,
                    "locator": retrieval["locator"],
                    "sha256": retrieval["sha256"],
                    "content_type": retrieval["content_type"],
                    "bytes_path": retrieval["bytes_path"],
                }
            ],
        }
        packets.append(
            worker_packet(
                run_id=run_id,
                episode_id=episode_id,
                correlation_key=request_key,
                phase="INTERPRET",
                projection={
                    "request": _request_projection(requests[request_key]),
                    "unit": unit,
                    "source_rules": dict(SOURCE_RULES),
                    "retrieval_group": group,
                },
                staged_inputs=[{
                    "name": retrieval["bytes_path"],
                    "source_path": retrieval["source_path"],
                    "sha256": retrieval["sha256"],
                }],
            )
        )

    return {
        "retrievals": retrievals,
        "pending_packet": staged_dispatch("M01_RESEARCH_UNIT_SOURCES", packets),
        "pending_guard": guard(
            "D06B_RETRIEVE_SOURCE_CANDIDATES",
            "interpretation_fanout",
            unit_id=unit_id,
            retrieval_keys=sorted(retrievals),
        ),
    }


# --------------------------------------------------------------------------
# D07
# --------------------------------------------------------------------------


@deterministic_node("D07_CORRELATE_AND_ADMIT_SOURCES")
def D07_CORRELATE_AND_ADMIT_SOURCES(
    projection: dict[str, Any], runtime_context: Any
) -> dict[str, Any]:
    """Join discovery, retrieval, and interpretation against the exact denominator."""

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")

    denominator = None
    for value in projection["source_denominators"].values():
        if isinstance(value, dict) and value.get("unit_id") == unit_id:
            denominator = value
    require(denominator is not None, "invalid_input", f"no source denominator for {unit_id!r}")

    expected = set(denominator["request_keys"])
    retrievals = projection["retrievals"]
    interpretations = projection["source_interpretations"]
    requests_by_key = {
        request.get("key"): request
        for request in projection["source_requests"]
        if isinstance(request, dict)
    }

    # Cross-unit contamination is a join failure, not a filterable condition: a
    # member keyed to another unit means the fan-out correlation itself is wrong.
    for label, collection in (("retrievals", retrievals), ("interpretations", interpretations)):
        foreign = sorted(
            key
            for key, value in collection.items()
            if isinstance(value, dict)
            and candidate_field(value, "unit_id") not in (None, unit_id)
            and key in expected
        )
        require(
            not foreign,
            "join",
            f"{label} contain members correlated to another unit",
            keys=foreign,
        )

    interpreted = {key for key in interpretations if key in expected}
    missing = sorted(expected - interpreted)
    extra = sorted(
        key for key in interpretations if key not in expected and _keyed_to(interpretations[key], unit_id)
    )
    require(not extra, "join", "interpretations contain members outside the denominator", keys=extra)

    stale: list[dict[str, Any]] = []
    for key in sorted(interpreted):
        interpretation = _record(interpretations[key], f"interpretation {key}")
        parent = candidate_field(interpretation, "retrieval_sha256")
        retrieval = retrievals.get(key)
        current = retrieval.get("sha256") if isinstance(retrieval, dict) else None
        if parent != current:
            stale.append({"key": key, "interpreted_from": parent, "current": current})
    require(
        not stale,
        "integrity",
        "an interpretation was derived from bytes that are no longer the retrieval",
        stale=stale,
    )

    if missing:
        required_missing = sorted(
            key
            for key in missing
            if any(
                request.get("key") == key and request.get("required")
                for request in projection["source_requests"]
                if isinstance(request, dict)
            )
        )
        return {
            "source_join_evidence": [
                {
                    "key": canonical_digest({"unit_id": unit_id, "missing": missing}),
                    "unit_id": unit_id,
                    "result": "INCOMPLETE",
                    "missing": missing,
                    "required_missing": required_missing,
                }
            ],
            "pending_guard": guard(
                "D07_CORRELATE_AND_ADMIT_SOURCES",
                "prerequisite_unresolved",
                unit_id=unit_id,
                missing=missing,
                required_missing=required_missing,
            ),
        }

    admissions: list[dict[str, Any]] = []
    for key in sorted(expected):
        interpretation = _record(interpretations[key], f"interpretation {key}")
        retrieval = _record(retrievals[key], f"retrieval {key}")
        admissions.append(
            {
                "key": key,
                "unit_id": unit_id,
                "source_epoch": denominator["source_epoch"],
                "fact_id": key.rsplit("/", 1)[-1],
                "locator": retrieval.get("locator"),
                "sha256": retrieval.get("sha256"),
                "content_type": retrieval.get("content_type"),
                "interpretation_hash": canonical_digest(interpretation),
                "scope": candidate_field(
                    interpretation, "scope", requests_by_key.get(key, {}).get("scope")
                ),
            }
        )

    join_evidence = {
        "key": canonical_digest({"unit_id": unit_id, "admitted": [a["key"] for a in admissions]}),
        "unit_id": unit_id,
        "result": "PASS",
        "denominator_size": len(expected),
        "admitted_size": len(admissions),
    }

    engine_root = projection["engine_root"]
    packet = worker_packet(
        run_id=projection["run_id"],
        episode_id=projection["episode_id"],
        correlation_key=f"{unit_id}/{denominator['source_epoch']}/domain",
        projection={
            "unit": _unit_projection(_unit_record(projection["effective_run"], unit_id)),
            "admitted_sources": [
                {
                    "source_id": admission["key"],
                    "fact_id": admission["fact_id"],
                    "locator": admission["locator"],
                    "sha256": admission["sha256"],
                    "content_type": admission["content_type"],
                    "scope": admission["scope"],
                }
                for admission in admissions
            ],
            "domain_schema": contract_reference(engine_root, DOMAIN_SCHEMA_CONTRACT),
            "verifier_interface": {
                "declared_at": "/verifier_result",
                "required_result": "all_fixtures_behaved",
                "proven_by": "D08_VALIDATE_DOMAIN",
            },
            "calibration": contract_reference(engine_root, DOMAIN_CALIBRATION_CONTRACT),
        },
    )

    return {
        "source_admissions": admissions,
        "source_join_evidence": [join_evidence],
        "pending_packet": staged_dispatch("M02_CREATE_UNIT_DOMAIN_DATA", [packet]),
        "pending_guard": guard(
            "D07_CORRELATE_AND_ADMIT_SOURCES", "sources_admitted", unit_id=unit_id
        ),
    }


def _keyed_to(value: Any, unit_id: str) -> bool:
    return isinstance(value, dict) and candidate_field(value, "unit_id") == unit_id


# --------------------------------------------------------------------------
# D30
# --------------------------------------------------------------------------


@deterministic_node("D30_CLASSIFY_PREREQUISITE")
def D30_CLASSIFY_PREREQUISITE(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Classify an unresolved source requirement as a pause, or refuse to.

    Only a named unavailable required external fact may pause an episode. Every
    other cause reaching this node is a system failure: a run that reports
    "waiting for a source" when its renderer is broken is a run that will be
    resumed forever.
    """

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")

    failure = projection["pending_failure"]
    named: list[str] = []
    if isinstance(failure, dict):
        failure_class = failure.get("class")
        require(
            failure_class == "pause",
            "invalid_input",
            f"prerequisite classification received a {failure_class!r} failure, which cannot pause",
            failure_cause=failure.get("cause"),
            failure_node=failure.get("node"),
        )
        evidence = failure.get("evidence") or {}
        named = sorted(
            str(entry.get("request_key") or entry.get("fact_id"))
            for entry in evidence.get("facts", [])
            if isinstance(entry, dict)
        )
        named += sorted(str(value) for value in evidence.get("fact_ids", []))

    denominator = None
    for value in projection["source_denominators"].values():
        if isinstance(value, dict) and value.get("unit_id") == unit_id:
            denominator = value
    require(denominator is not None, "invalid_input", f"no source denominator for {unit_id!r}")

    if not named:
        named = sorted(set(denominator["request_keys"]) - set(projection["retrievals"]))

    require(
        bool(named),
        "invalid_input",
        "prerequisite classification found no named unresolved requirement",
        unit_id=unit_id,
    )
    require(
        len(named) == 1,
        "invalid_input",
        "exactly one named required external fact may pause an episode",
        named=named,
    )

    fact = named[0]
    attempts = projection["attempt_counters"].get(f"retrieval:{fact}", 0)

    record = {
        "kind": "prerequisite_classification",
        "unit_id": unit_id,
        "fact": fact,
        "attempts": attempts,
        "source_epoch": denominator["source_epoch"],
        "required_resume_condition": f"named external fact {fact} becomes retrievable",
    }
    record["key"] = canonical_digest(record)

    resume_frontier = {
        "destination": "D06B_RETRIEVE_SOURCE_CANDIDATES",
        "selected_unit_id": unit_id,
        "parent_hashes": {},
        "blocked_on": fact,
    }

    candidate = {
        "kind": "PAUSED_PREREQUISITE",
        "unit_id": unit_id,
        "fact": fact,
        "attempts": attempts,
        "locators": sorted(
            str(value.get("locator"))
            for key, value in projection["retrievals"].items()
            if key == fact and isinstance(value, dict)
        ),
        "required_resume_condition": record["required_resume_condition"],
        "resume_frontier": resume_frontier,
    }

    return {
        "evidence_index_entries": [record],
        "terminal_candidate": candidate,
        "resume_frontier": resume_frontier,
        "pending_guard": guard("D30_CLASSIFY_PREREQUISITE", "prerequisite_pause", fact=fact),
    }
