from __future__ import annotations

from copy import deepcopy
from typing import Any

from .gemini import GeminiSettingsError, audit_stream_events, resolve_alias


class CapabilityError(RuntimeError):
    pass


def route_required_by_unit(route_id: str, unit: dict[str, Any], *, forbidden_routes: set[str] | None = None) -> bool:
    if route_id in (forbidden_routes or set()):
        return False
    serialized = " ".join(str(value).lower() for value in unit.get("visual_roles", []))
    if route_id == "imagegen":
        return any(term in serialized for term in ("imagegen", "generative", "generated image"))
    return route_id in serialized


def remove_unavailable_route(document: dict[str, Any], route_id: str, *, required: bool) -> dict[str, Any]:
    routes = document.get("routes", [])
    matches = [route for route in routes if route.get("id") == route_id]
    if len(matches) != 1:
        raise CapabilityError(f"route must exist exactly once: {route_id}")
    route = matches[0]
    if required:
        raise CapabilityError(f"required route cannot be removed: {route_id}")
    if route.get("status") != "UNPROVEN" or route.get("command") is not None or route.get("proof") is not None:
        raise CapabilityError(f"only a genuinely unavailable route may be removed: {route_id}")
    updated = deepcopy(document)
    updated["routes"] = [item for item in updated["routes"] if item.get("id") != route_id]
    return updated


def validate_cross_family_proof(receipt: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    required = {"real_call", "decided_model", "executed_model", "policy_effort", "settings_sha256", "events"}
    missing = required - set(receipt)
    if missing:
        raise CapabilityError(f"cross-family proof missing fields: {sorted(missing)}")
    if receipt["real_call"] is not True:
        raise CapabilityError("cross-family route requires a real proof call")
    try:
        resolved = resolve_alias(settings, receipt["decided_model"])
        stream = audit_stream_events(receipt["events"], receipt["decided_model"])
    except GeminiSettingsError as error:
        raise CapabilityError(str(error)) from error
    if receipt["policy_effort"] != "max" or resolved["settings_sha256"] != receipt["settings_sha256"]:
        raise CapabilityError("max effort mapping or settings hash does not resolve")
    if receipt["executed_model"] != receipt["decided_model"] or stream["init_model"] != receipt["executed_model"]:
        raise CapabilityError("registered, decided, executed, and init model must agree")
    return {**resolved, **stream, "proof_valid": True}
