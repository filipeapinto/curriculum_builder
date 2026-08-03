#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

import yaml

from .capabilities import route_required_by_unit, validate_cross_family_proof
from .gemini import audit_stream_events, resolve_alias, write_run_local_settings
from .io import atomic_json, sha256_file


class CycleFailure(RuntimeError):
    pass


def package_root(binary: Path) -> Path:
    resolved = binary.resolve()
    if resolved.name != "index.js" or resolved.parent.name != "dist":
        raise CycleFailure(f"cannot derive Gemini CLI package root from {resolved}")
    return resolved.parents[1]


def evidence_files(cli_root: Path) -> dict[str, str]:
    core = cli_root / "node_modules/@google/gemini-cli-core/dist"
    genai = cli_root / "node_modules/@google/genai/dist/node/node.d.ts"
    paths = {
        "configuration": core / "docs/get-started/configuration.md",
        "generation_settings": core / "docs/cli/generation-settings.md",
        "headless": core / "docs/cli/headless.md",
        "model_config_service": core / "src/services/modelConfigService.js",
        "default_model_configs": core / "src/config/defaultModelConfigs.js",
        "sdk_types": genai,
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise CycleFailure(f"bundled evidence missing: {missing}")
    return {name: sha256_file(path) for name, path in paths.items()}


def prepare(task_root: Path, engine: Path, curriculum: Path, model: str) -> dict[str, Any]:
    task_root = task_root.resolve()
    proof = task_root / "capability_cycle/gemini_proof"
    proof.mkdir(parents=True, exist_ok=True)
    work = proof / "isolated_workdir"
    work.mkdir(exist_ok=True)
    settings_path, settings_hash = write_run_local_settings(proof, model)
    binary_name = shutil.which("gemini")
    node = shutil.which("node")
    if not binary_name or not node:
        raise CycleFailure("gemini or node executable missing")
    binary = Path(binary_name)
    cli_root = package_root(binary)
    version = subprocess.run([str(binary), "--version"], capture_output=True, text=True, check=True).stdout.strip()
    help_text = subprocess.run([str(binary), "--help"], capture_output=True, text=True, check=True).stdout
    if "--model" not in help_text or "--output-format" not in help_text:
        raise CycleFailure("installed help does not expose required model and stream controls")
    if "--effort" in help_text or "--reasoning-effort" in help_text:
        raise CycleFailure("unexpected direct effort flag requires re-analysis")
    environment = dict(os.environ)
    environment["GEMINI_CLI_SYSTEM_SETTINGS_PATH"] = str(settings_path)
    resolver = subprocess.run(
        [node, str(engine / "runtime/resolve_gemini_settings.mjs"), str(cli_root), model],
        cwd=work, env=environment, capture_output=True, text=True,
    )
    if resolver.returncode != 0:
        raise CycleFailure(f"installed settings resolver failed: {resolver.stderr}")
    resolver_audit = json.loads(resolver.stdout)
    resolved = resolver_audit["resolved_model_config"]
    if resolved.get("model") != model or resolved.get("generateContentConfig", {}).get("thinkingConfig", {}).get("thinkingLevel") != "HIGH":
        raise CycleFailure(f"installed resolver did not preserve explicit model/max effort: {resolved}")
    manifest = yaml.safe_load(max(curriculum.glob("*curriculum.v*.yaml")).read_text())
    l01 = manifest["labs"][0]
    imagegen_required = route_required_by_unit("imagegen", l01, forbidden_routes={"imagegen"})
    user_settings = Path.home() / ".gemini/settings.json"
    project_settings = work / ".gemini/settings.json"
    record = {
        "prepared_utc": datetime.now(timezone.utc).isoformat(),
        "cycle_number": 1,
        "model": model,
        "policy_effort": "max",
        "provider_control": {"thinkingLevel": "HIGH"},
        "mapping_basis": "installed SDK discrete ThinkingLevel enum contains only LOW and HIGH besides unspecified",
        "gemini_cli_version": version,
        "binary_path": str(binary.resolve()),
        "binary_sha256": sha256_file(binary.resolve()),
        "bundled_evidence_sha256": evidence_files(cli_root),
        "settings_path": str(settings_path),
        "settings_sha256": settings_hash,
        "resolver_audit": resolver_audit,
        "configuration_layer_audit": {
            "user_settings_path": str(user_settings),
            "user_settings_sha256": sha256_file(user_settings) if user_settings.is_file() else None,
            "project_settings_path": str(project_settings),
            "project_settings_exists": project_settings.exists(),
            "system_override_path": str(settings_path),
        },
        "research_divergence": {
            "recorded": True,
            "route": None,
            "meaning": "primary-source network reads remain an accepted capability divergence, not a route",
        },
        "imagegen_dependency_decision": {
            "required_by_first_unit": imagegen_required,
            "proof_calls": 0,
            "reason": "the task contract forbids generated images in L01; official and deterministic visuals cover all declared roles",
        },
    }
    atomic_json(proof / "prepared.json", record, root=task_root)
    return record


def live(task_root: Path, model: str) -> dict[str, Any]:
    task_root = task_root.resolve()
    proof = task_root / "capability_cycle/gemini_proof"
    prepared_path = proof / "prepared.json"
    prepared = json.loads(prepared_path.read_text())
    settings_path = Path(prepared["settings_path"])
    work = proof / "isolated_workdir"
    binary = Path(prepared["binary_path"])
    environment = dict(os.environ)
    environment["GEMINI_CLI_SYSTEM_SETTINGS_PATH"] = str(settings_path)
    command = [str(binary), "-m", model, "-s", "--approval-mode", "default",
               "--output-format", "stream-json", "Reply with exactly: ROUTE_OK. Do not use tools."]
    started = datetime.now(timezone.utc)
    result = subprocess.run(command, cwd=work, env=environment, capture_output=True, text=True, timeout=300)
    ended = datetime.now(timezone.utc)
    events = []
    parse_errors = []
    for line in result.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as error:
            parse_errors.append(str(error))
    settings = json.loads(settings_path.read_text())
    receipt: dict[str, Any] = {
        "real_call": True, "started_utc": started.isoformat(), "ended_utc": ended.isoformat(),
        "elapsed_seconds": (ended - started).total_seconds(), "command": command,
        "working_directory": str(work), "settings_path": str(settings_path),
        "settings_sha256": sha256_file(settings_path), "policy_effort": "max",
        "provider_control": {"thinkingLevel": "HIGH"}, "decided_model": model,
        "executed_model": next((event.get("model") for event in events if event.get("type") == "init"), None),
        "events": events, "parse_errors": parse_errors, "returncode": result.returncode,
        "stdout_sha256": hashlib.sha256(result.stdout.encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256(result.stderr.encode()).hexdigest(),
        "stdout": result.stdout, "stderr": result.stderr,
    }
    try:
        validated = validate_cross_family_proof(receipt, settings)
        success = result.returncode == 0 and not parse_errors
        receipt["validation"] = validated
        receipt["status"] = "PROVEN" if success else "FAILED"
    except Exception as error:
        receipt["status"] = "FAILED"
        receipt["validation_error"] = str(error)
    atomic_json(proof / "live_proof_receipt.json", receipt, root=task_root)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "live"])
    parser.add_argument("--task-root", type=Path, required=True)
    parser.add_argument("--engine", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--curriculum", type=Path, default=Path("curricula/arduino_kit"))
    parser.add_argument("--model", default="gemini-3-pro-preview")
    args = parser.parse_args()
    curriculum = args.curriculum if args.curriculum.is_absolute() else args.engine / args.curriculum
    value = prepare(args.task_root, args.engine.resolve(), curriculum.resolve(), args.model) if args.action == "prepare" else live(args.task_root, args.model)
    print(json.dumps(value, indent=2))
    return 0 if args.action == "prepare" or value.get("status") == "PROVEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
