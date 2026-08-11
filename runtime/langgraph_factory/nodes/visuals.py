"""Visual brief compilation, deterministic production, and the visual join barrier.

Owns D10, D11, and D12. The split between deterministic and model visuals is the
safety boundary of this stage: a visual that asserts an authoritative fact a
learner could build from is produced deterministically from the domain, never
requested from a model.
"""

from __future__ import annotations

from typing import Any

from . import (
    SystemFailure,
    canonical_digest,
    check_record,
    correlation_record,
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

__all__ = [
    "AUTHORITATIVE_VISUAL_KINDS",
    "MODEL_VISUAL_CONTRACT",
    "classify_visual_brief",
    "D10_COMPILE_VISUAL_BRIEFS",
    "D11_CREATE_DETERMINISTIC_VISUALS",
    "D12_VISUAL_BARRIER_AND_JOIN",
]


# A visual of one of these kinds asserts exact physical facts. It is produced
# from the domain by a deterministic renderer; a model may not invent it. The
# second group is M04's own refusal list: a kind it would reject is classified
# deterministic here rather than dispatched and bounced.
AUTHORITATIVE_VISUAL_KINDS: frozenset[str] = frozenset(
    {"build_map", "schematic", "netlist", "power_path", "connectivity", "safety_inset"}
) | frozenset(
    {"circuit", "pinout", "pin_map", "breadboard", "wiring", "electrical", "terminal_block"}
)

# What an M04 worker is permitted to do with a brief, stated from this module's
# own safety boundary rather than restated by hand at dispatch time.
MODEL_VISUAL_CONTRACT: dict[str, Any] = {
    "may_assert_authoritative_facts": False,
    "permitted_fact_source": "brief.permitted_facts",
    "required_output": "visual_candidate",
    "refused_kinds": sorted(AUTHORITATIVE_VISUAL_KINDS),
}


def _record(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), "schema_contract", f"{label} must be a JSON object")
    return dict(value)


def classify_visual_brief(brief: dict[str, Any]) -> str:
    """Return ``deterministic`` or ``model`` for one brief."""

    kind = brief.get("kind")
    if kind in AUTHORITATIVE_VISUAL_KINDS:
        return "deterministic"
    if brief.get("authoritative") is True:
        return "deterministic"
    return "model"


# --------------------------------------------------------------------------
# D10
# --------------------------------------------------------------------------


@deterministic_node("D10_COMPILE_VISUAL_BRIEFS")
def D10_COMPILE_VISUAL_BRIEFS(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Compile the exact visual denominator, split into deterministic and model subsets."""

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")

    heads = projection["artifact_heads"]
    content_head = heads.get(stream_id(unit_id, "content"))
    domain_head = heads.get(stream_id(unit_id, "domain"))
    require(
        isinstance(content_head, dict) and isinstance(domain_head, dict),
        "invalid_input",
        "visual brief compilation requires admitted domain and content heads",
    )

    candidate = latest_candidate(projection["artifact_versions"], stream_id(unit_id, "content"))
    require(candidate is not None, "invalid_input", "no content version is available")
    require(
        candidate.get("hash") == content_head.get("hash"),
        "integrity",
        "the available content version is not the admitted content head",
        candidate=candidate.get("hash"),
        head=content_head.get("hash"),
    )

    body = _record(candidate.get("body"), "content body")
    declared = body.get("visuals", [])
    require(isinstance(declared, list), "schema_contract", "content declares a non-list visual set")

    briefs: list[dict[str, Any]] = []
    deterministic_keys: list[str] = []
    model_keys: list[str] = []
    for ordinal, entry in enumerate(declared):
        brief_source = _record(entry, f"visual declaration {ordinal}")
        key = f"{unit_id}/visual/{brief_source.get('role', ordinal)}"
        subset = classify_visual_brief(brief_source)
        brief = {
            "key": key,
            "unit_id": unit_id,
            "role": brief_source.get("role"),
            "kind": brief_source.get("kind"),
            "subset": subset,
            "content_hash": content_head["hash"],
            "domain_hash": domain_head["hash"],
            "permitted_facts": sorted(
                str(fact) for fact in brief_source.get("permitted_facts", []) or []
            ),
        }
        if subset == "model" and brief_source.get("requests_authoritative_facts"):
            raise SystemFailure(
                "invalid_input",
                f"visual brief {key} requests authoritative facts from a model",
                {"key": key, "kind": brief_source.get("kind")},
            )
        briefs.append(brief)
        (deterministic_keys if subset == "deterministic" else model_keys).append(key)

    require(
        len(set(deterministic_keys) | set(model_keys)) == len(briefs),
        "join",
        "visual briefs declare duplicate keys",
    )

    denominator = {
        f"{unit_id}/{content_head['hash']}": {
            "unit_id": unit_id,
            "content_hash": content_head["hash"],
            "deterministic_keys": sorted(deterministic_keys),
            "model_keys": sorted(model_keys),
            "size": len(briefs),
        }
    }

    update: dict[str, Any] = {
        "visual_briefs": briefs,
        "visual_denominators": denominator,
    }

    if deterministic_keys:
        by_key = {brief["key"]: brief for brief in briefs}
        update["pending_packet"] = staged_dispatch(
            "D11_CREATE_DETERMINISTIC_VISUALS",
            [
                {
                    "brief": by_key[key],
                    "permitted_facts": by_key[key]["permitted_facts"],
                    "correlation": correlation_record(
                        projection["run_id"],
                        projection["episode_id"],
                        f"{unit_id}/{content_head['hash']}/{key}",
                    ),
                }
                for key in sorted(deterministic_keys)
            ],
        )

    value = "deterministic_visual_fanout" if deterministic_keys else "no_deterministic_visuals"
    update["pending_guard"] = guard(
        "D10_COMPILE_VISUAL_BRIEFS",
        value,
        unit_id=unit_id,
        deterministic_keys=sorted(deterministic_keys),
    )
    return update


# --------------------------------------------------------------------------
# D11
# --------------------------------------------------------------------------


@deterministic_node("D11_CREATE_DETERMINISTIC_VISUALS")
def D11_CREATE_DETERMINISTIC_VISUALS(
    projection: dict[str, Any], runtime_context: Any
) -> dict[str, Any]:
    """Produce one deterministic visual from its brief and permitted facts."""

    packet = projection["pending_packet"]
    require(isinstance(packet, dict) and bool(packet), "invalid_input", "no visual brief packet")
    brief = _record(packet.get("brief"), "visual brief")
    key = brief.get("key")
    require(isinstance(key, str) and key, "invalid_input", "the visual brief packet has no key")
    require(
        brief.get("subset") == "deterministic",
        "invalid_input",
        f"visual brief {key} is not in the deterministic subset",
        subset=brief.get("subset"),
    )

    renderer = getattr(runtime_context, "transport_registry", None)
    produce = getattr(renderer, "render_deterministic_visual", None) if renderer else None
    require(
        callable(produce),
        "capability",
        "runtime context exposes no deterministic visual renderer",
    )

    try:
        produced = produce(brief, packet.get("permitted_facts", brief.get("permitted_facts", [])))
    except Exception as error:  # noqa: BLE001 - a render fault is a system failure, never a finding
        raise SystemFailure(
            "tool",
            f"deterministic visual render failed for {key}: {error}",
            {"key": key, "kind": brief.get("kind")},
        ) from error

    result = _record(produced, f"visual result for {key}")
    for field in ("asset_path", "sha256", "format"):
        require(field in result, "integrity", f"visual result for {key} has no {field!r}")

    return {
        "visual_results": {
            key: {
                "key": key,
                "unit_id": brief.get("unit_id"),
                "subset": "deterministic",
                "provenance": "deterministic_renderer",
                "content_hash": brief.get("content_hash"),
                "domain_hash": brief.get("domain_hash"),
                "asset_path": result["asset_path"],
                "sha256": result["sha256"],
                "format": result["format"],
            }
        },
        "pending_guard": guard("D11_CREATE_DETERMINISTIC_VISUALS", "visual_produced", key=key),
    }


# --------------------------------------------------------------------------
# D12
# --------------------------------------------------------------------------


@deterministic_node("D12_VISUAL_BARRIER_AND_JOIN")
def D12_VISUAL_BARRIER_AND_JOIN(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Prove the exact visual denominator, then dispatch model briefs or admit the head.

    Entered twice per epoch: first to prove the deterministic subset is exactly
    complete before any model brief is dispatched, then to admit the visual head
    once the whole denominator has returned.
    """

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")

    denominator = None
    for value in projection["visual_denominators"].values():
        if isinstance(value, dict) and value.get("unit_id") == unit_id:
            denominator = value
    require(denominator is not None, "invalid_input", f"no visual denominator for {unit_id!r}")

    heads = projection["artifact_heads"]
    content_head = heads.get(stream_id(unit_id, "content"))
    require(isinstance(content_head, dict), "invalid_input", "no admitted content head")
    require(
        denominator["content_hash"] == content_head["hash"],
        "integrity",
        "the visual denominator was compiled against a superseded content head",
        denominator_parent=denominator["content_hash"],
        current_head=content_head["hash"],
    )

    expected_deterministic = set(denominator["deterministic_keys"])
    expected_model = set(denominator["model_keys"])
    results = projection["visual_results"]

    actual_deterministic = {
        key
        for key, value in results.items()
        if isinstance(value, dict)
        and value.get("unit_id") == unit_id
        and value.get("subset") == "deterministic"
    }
    missing = sorted(expected_deterministic - actual_deterministic)
    extra = sorted(actual_deterministic - expected_deterministic)
    require(
        not missing and not extra,
        "join",
        "the deterministic visual subset does not equal its frozen denominator",
        missing=missing,
        extra=extra,
    )

    stale = sorted(
        key
        for key in actual_deterministic
        if results[key].get("content_hash") != content_head["hash"]
    )
    require(
        not stale,
        "integrity",
        "a deterministic visual was produced against a superseded content head",
        stale=stale,
    )

    actual_model = {
        key
        for key, value in results.items()
        if isinstance(value, dict)
        and value.get("unit_id") == unit_id
        and value.get("subset") == "model"
    }

    if expected_model and actual_model != expected_model:
        pending = sorted(expected_model - actual_model)
        briefs = {
            brief["key"]: brief
            for brief in projection["visual_briefs"]
            if isinstance(brief, dict) and brief.get("key") in pending
        }
        require(
            sorted(briefs) == pending,
            "join",
            "a pending model visual key has no compiled brief",
            pending=pending,
        )
        evidence = {
            "key": canonical_digest(
                {"unit_id": unit_id, "phase": "deterministic_subset_proof", "keys": sorted(expected_deterministic)}
            ),
            "unit_id": unit_id,
            "phase": "deterministic_subset_proof",
            "result": "PASS",
            "deterministic_size": len(expected_deterministic),
            "pending_model_keys": pending,
        }
        packets = [
            worker_packet(
                run_id=projection["run_id"],
                episode_id=projection["episode_id"],
                correlation_key=f"{unit_id}/{content_head['hash']}/{key}",
                projection={
                    "brief": {
                        "brief_id": key,
                        "unit_id": unit_id,
                        "role": briefs[key].get("role"),
                        "visual_class": briefs[key].get("kind"),
                        "content_hash": briefs[key].get("content_hash"),
                        "authoritative": False,
                        "eligibility": "model_eligible",
                    },
                    "permitted_facts": briefs[key].get("permitted_facts", []),
                    "visual_contract": dict(MODEL_VISUAL_CONTRACT),
                },
            )
            for key in pending
        ]
        return {
            "visual_join_evidence": [evidence],
            "pending_packet": staged_dispatch("M04_CREATE_UNIT_VISUALS", packets),
            "pending_guard": guard(
                "D12_VISUAL_BARRIER_AND_JOIN", "model_visual_fanout", unit_id=unit_id, keys=pending
            ),
        }

    complete = expected_deterministic | expected_model
    actual = actual_deterministic | actual_model
    require(
        actual == complete,
        "join",
        "the accumulated visual set does not equal the complete denominator",
        missing=sorted(complete - actual),
        extra=sorted(actual - complete),
    )

    attempt = 1
    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for key in sorted(complete):
        result = _record(results[key], f"visual result {key}")
        valid = bool(result.get("sha256")) and bool(result.get("format"))
        provenance_ok = result.get("provenance") in ("deterministic_renderer", "model_candidate")
        checks.append(
            check_record(
                scope="unit",
                owner=unit_id,
                head_hash=content_head["hash"],
                check_id=f"visual_valid:{key}",
                attempt=attempt,
                result="PASS" if valid and provenance_ok else "FAIL",
                detail={"provenance": result.get("provenance"), "format": result.get("format")},
            )
        )
        if not (valid and provenance_ok):
            findings.append(
                {
                    "check_id": f"visual_valid:{key}",
                    "owner": "unit visual",
                    "pointer": f"/visuals/{key}",
                    "message": "visual candidate is missing hash, format, or declared provenance",
                }
            )

    join_evidence = {
        "key": canonical_digest({"unit_id": unit_id, "phase": "join", "keys": sorted(complete)}),
        "unit_id": unit_id,
        "phase": "join",
        "result": "FAIL" if findings else "PASS",
        "denominator_size": len(complete),
        "actual_size": len(actual),
    }

    if findings:
        return {
            "visual_join_evidence": [join_evidence],
            "deterministic_checks": checks,
            "pending_guard": guard(
                "D12_VISUAL_BARRIER_AND_JOIN",
                "visuals_repairable",
                unit_id=unit_id,
                findings=findings,
            ),
        }

    visual_stream = stream_id(unit_id, "visuals")
    candidate = {
        "stream": visual_stream,
        "version": (heads.get(visual_stream) or {}).get("version", 0) + 1,
        "parent_hash": (heads.get(visual_stream) or {}).get("hash"),
        "hash": canonical_digest(
            {"unit_id": unit_id, "visuals": {key: results[key]["sha256"] for key in sorted(complete)}}
        ),
    }
    require_current_parent(candidate, heads, visual_stream)

    return {
        "visual_join_evidence": [join_evidence],
        "deterministic_checks": checks,
        "artifact_heads": head_update(candidate, visual_stream),
        "pending_guard": guard("D12_VISUAL_BARRIER_AND_JOIN", "visuals_admitted", unit_id=unit_id),
    }
