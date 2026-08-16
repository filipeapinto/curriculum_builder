from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .io import atomic_json, sha256_file


class GeminiSettingsError(RuntimeError):
    pass


def max_effort_settings(model_id: str) -> dict[str, Any]:
    if not model_id or any(char.isspace() for char in model_id):
        raise GeminiSettingsError("explicit Gemini model id is required")
    return {
        "modelConfigs": {
            "aliases": {
                model_id: {
                    "modelConfig": {
                        "model": model_id,
                        "generateContentConfig": {
                            "thinkingConfig": {"thinkingLevel": "HIGH"}
                        },
                    },
                }
            }
        },
        "tools": {"core": [], "allowed": []},
        "mcpServers": {},
        "mcp": {"allowed": []},
        "useWriteTodos": False,
    }


def write_run_local_settings(root: Path, model_id: str) -> tuple[Path, str]:
    root = root.resolve()
    path = root / "routing" / "gemini_system_settings.json"
    atomic_json(path, max_effort_settings(model_id), root=root)
    return path, sha256_file(path)


def resolve_alias(settings: dict[str, Any], model_id: str) -> dict[str, Any]:
    try:
        alias = settings["modelConfigs"]["aliases"][model_id]["modelConfig"]
        thinking = alias["generateContentConfig"]["thinkingConfig"]
    except (KeyError, TypeError) as error:
        raise GeminiSettingsError("missing model alias or thinking control") from error
    if alias.get("model") != model_id:
        raise GeminiSettingsError("alias key and underlying explicit model must agree")
    if thinking != {"thinkingLevel": "HIGH"}:
        raise GeminiSettingsError("policy max must resolve exactly to thinkingLevel HIGH")
    tools = settings.get("tools", {})
    if tools.get("core") != [] or tools.get("allowed") != []:
        raise GeminiSettingsError("tool discovery and execution must be disabled")
    if settings.get("mcp", {}).get("allowed") != [] or settings.get("mcpServers") != {}:
        raise GeminiSettingsError("MCP discovery must be disabled")
    return {
        "alias": model_id,
        "model": model_id,
        "policy_effort": "max",
        "provider_control": {"thinkingLevel": "HIGH"},
        "tools_disabled": True,
        "settings_sha256": hashlib.sha256(
            (json.dumps(settings, indent=2, sort_keys=True) + "\n").encode("utf-8")
        ).hexdigest(),
    }


def audit_stream_events(events: list[dict[str, Any]], decided_model: str) -> dict[str, Any]:
    init_models = [event.get("model") for event in events if event.get("type") == "init"]
    if len(init_models) != 1:
        raise GeminiSettingsError(f"expected exactly one init event, found {len(init_models)}")
    if init_models[0] != decided_model:
        raise GeminiSettingsError("Gemini init.model differs from decided model")
    tool_events = [event for event in events if "tool" in str(event.get("type", "")).lower()]
    if tool_events:
        raise GeminiSettingsError("tool-use event observed on no-tools route")
    return {"init_model": init_models[0], "tool_use_events": 0}
