#!/usr/bin/env python3
"""Bootstrap and adversarial validation for the immutable Plan 21 v2 overlay."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
V2_PATH = ROOT / "graph_engineered_subscription_execution.plan.v2.yaml"
V2_SCHEMA_PATH = ROOT / "graph_engineered_subscription_execution.schema.v2.json"


def _load_v1():
    spec = importlib.util.spec_from_file_location("plan21_v1_validator", ROOT / "tools" / "validate_plan.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen v1 validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V1 = _load_v1()


class V2Error(ValueError):
    pass


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_value(value: Any) -> str:
    return digest_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def load() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    delta = yaml.safe_load(V2_PATH.read_text())
    schema = json.loads(V2_SCHEMA_PATH.read_text())
    base_path = ROOT / delta["base"]["path"]
    if digest_bytes(base_path.read_bytes()) != delta["base"]["sha256"]:
        raise V2Error("frozen v1 base digest mismatch")
    base = yaml.safe_load(base_path.read_text())
    return delta, schema, base


def _schema_errors(schema: dict[str, Any], value: Any) -> list[Any]:
    return list(Draft202012Validator(schema).iter_errors(value))


def _resolve_schema_property(schema: dict[str, Any], dotted: str) -> bool:
    current = schema
    for segment in dotted.split("."):
        properties = current.get("properties", {})
        if segment not in properties:
            return False
        current = properties[segment]
    return True


def validate_registry(base: dict[str, Any]) -> None:
    used: set[str] = set()
    for node in base["nodes"]:
        used.update(ref for ref in node["authorized_inputs"] + node["authorized_outputs"] if ref.startswith("contract://"))
    registry = base["contract_registry"]
    if set(registry) != used:
        raise V2Error(f"registry usage mismatch: unused={sorted(set(registry)-used)} missing={sorted(used-set(registry))}")
    for name, entry in registry.items():
        schema_path = ROOT / entry["schema_ref"]
        if not schema_path.is_file():
            raise V2Error(f"registry {name} schema does not exist")
        owner_schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(owner_schema)
        if not _resolve_schema_property(owner_schema, entry["resolver"]):
            raise V2Error(f"registry {name} resolver does not exist in owner schema")


def effective_node(base: dict[str, Any], delta: dict[str, Any], node_id: str) -> dict[str, Any]:
    node = copy.deepcopy(next(item for item in base["nodes"] if item["id"] == node_id))
    override = delta["node_contract_overrides"][node_id]
    node["required_subtask_ids"] = list(override["required_subtask_ids"])
    node["authorized_outputs"] = node["authorized_outputs"] + list(override["additional_outputs"])
    return node


def _safe_source(root: Path, relative: str) -> Path:
    source = root / relative
    if source.is_symlink() or not source.is_file():
        raise V2Error(f"evidence source is not an existing regular file: {relative}")
    resolved_root = root.resolve()
    resolved = source.resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise V2Error(f"evidence source escapes root: {relative}")
    return resolved


def validate_evidence_manifest(manifest: dict[str, Any], event: dict[str, Any], node: dict[str, Any], current: dict[str, Any], evidence_root: Path) -> None:
    schema = json.loads((ROOT / "contracts" / "evidence_manifest.schema.v2.json").read_text())
    if _schema_errors(schema, manifest):
        raise V2Error("evidence manifest schema failure")
    for field in ("run_id", "node_id", "attempt", "graph_digest", "prompt_digest", "policy_digest", "schema_digest", "route_digest", "execution_contract_digest"):
        if manifest[field] != current[field]:
            raise V2Error(f"evidence manifest stale binding: {field}")
    tests = {entry["test_id"]: entry for entry in manifest["test_sources"]}
    if len(tests) != len(manifest["test_sources"]) or set(tests) != set(node["required_test_ids"]):
        raise V2Error("evidence manifest test denominator mismatch")
    artifacts = {entry["artifact_id"]: entry for entry in manifest["artifact_sources"]}
    if len(artifacts) != len(manifest["artifact_sources"]) or set(artifacts) != set(node["authorized_outputs"]):
        raise V2Error("evidence manifest artifact denominator mismatch")
    for test_id, entry in tests.items():
        if entry["source"]["path"] != current["resolved_test_evidence_paths"].get(test_id):
            raise V2Error(f"test evidence source is not the compiled source: {test_id}")
        source = _safe_source(evidence_root, entry["source"]["path"])
        data = source.read_bytes()
        actual = digest_bytes(data)
        if not data or entry["source"]["size"] != len(data) or entry["source"]["sha256"] != actual:
            raise V2Error(f"test evidence bytes disagree: {test_id}")
        event_result = next((item for item in event["test_results"] if item["id"] == test_id), None)
        if event_result is None or event_result["status"] != "PASS" or event_result["evidence_hash"] != actual:
            raise V2Error(f"event test evidence disagrees: {test_id}")
    for artifact_id, entry in artifacts.items():
        declared_paths = [item["path"] for item in entry["resolved_files"]]
        if declared_paths != current["resolved_artifact_paths"].get(artifact_id):
            raise V2Error(f"artifact sources are not the compiled resolution: {artifact_id}")
        records = []
        seen_paths = set()
        for declared in entry["resolved_files"]:
            if declared["path"] in seen_paths:
                raise V2Error(f"duplicate resolved artifact source: {artifact_id}")
            seen_paths.add(declared["path"])
            source = _safe_source(evidence_root, declared["path"])
            data = source.read_bytes()
            actual = digest_bytes(data)
            if not data or declared["size"] != len(data) or declared["sha256"] != actual:
                raise V2Error(f"artifact source bytes disagree: {artifact_id}")
            records.append({"path": declared["path"], "sha256": actual, "size": len(data)})
        aggregate = digest_value(sorted(records, key=lambda item: item["path"]))
        if entry["aggregate_sha256"] != aggregate or event["artifact_hashes"].get(artifact_id) != aggregate:
            raise V2Error(f"artifact aggregate disagrees: {artifact_id}")
    event_without_id = {key: value for key, value in event.items() if key != "event_id"}
    if event["event_id"] != digest_value(event_without_id):
        raise V2Error("event id is not a digest of admitted event bytes")


def validate_phase_event_v2(event: dict[str, Any], manifest: dict[str, Any], node: dict[str, Any], current: dict[str, Any], evidence_root: Path) -> None:
    V1.validate_phase_event(event, node, current)
    validate_evidence_manifest(manifest, event, node, current, evidence_root)


def validate_phase_ledger_v2(ledger: dict[str, Any], node: dict[str, Any], current: dict[str, Any]) -> None:
    V1.validate_phase_ledger(ledger, current)
    if set(ledger["required_subtask_ids"]) != set(node["required_subtask_ids"]):
        raise V2Error("ledger denominator is not the compiled node denominator")


def validate_resume_once(continuation: dict[str, Any], authorization: dict[str, Any], command: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    V1.validate_resume(continuation, command, current)
    auth_schema = json.loads((ROOT / "contracts" / "resume_authorization.schema.v2.json").read_text())
    if _schema_errors(auth_schema, authorization):
        raise V2Error("resume authorization schema failure")
    continuation_hash = digest_value(continuation)
    authorization_hash = digest_value(authorization)
    exact = {
        "run_id": continuation["run_id"], "continuation_id": continuation["continuation_id"],
        "continuation_hash": continuation_hash, "resume_node_id": continuation["allowed_resume_node_id"],
        "next_attempt": continuation["next_attempt"],
    }
    if any(authorization[field] != value for field, value in exact.items()):
        raise V2Error("authorization does not bind continuation")
    if command["operator_authorization_hash"] != authorization_hash:
        raise V2Error("command does not bind authorization record")
    signed_payload = {key: value for key, value in authorization.items() if key not in {"authorization_id", "signature"}}
    if authorization["authorization_id"] != digest_value(signed_payload):
        raise V2Error("authorization id does not bind signed payload")
    authorization_root = Path(current["authorization_root"]).resolve()
    authorization_path = Path(current["authorization_path"])
    if authorization_path.is_symlink() or not authorization_path.is_file() or authorization_root not in authorization_path.resolve().parents:
        raise V2Error("authorization record is not in the external authorization root")
    root_stat = authorization_root.stat()
    record_stat = authorization_path.stat()
    if root_stat.st_uid != current["authorization_root_owner_uid"] or root_stat.st_mode & 0o022 or record_stat.st_mode & 0o022:
        raise V2Error("authorization root/record ownership or mode is unsafe")
    for workspace in current["model_workspace_roots"]:
        workspace_path = Path(workspace).resolve()
        if authorization_root == workspace_path or workspace_path in authorization_root.parents or authorization_root in workspace_path.parents:
            raise V2Error("authorization root overlaps a model workspace")
    canonical_authorization = json.dumps(authorization, sort_keys=True, separators=(",", ":")).encode()
    if authorization_path.read_bytes() != canonical_authorization:
        raise V2Error("authorization object disagrees with external record bytes")
    public_key_path = Path(current["pinned_public_key_path"])
    if public_key_path.is_symlink() or not public_key_path.is_file() or digest_bytes(public_key_path.read_bytes()) != current["pinned_public_key_sha256"]:
        raise V2Error("pinned operator public key mismatch")
    now = datetime.fromisoformat(current["authorization_time"].replace("Z", "+00:00"))
    issued = datetime.fromisoformat(authorization["issued_at"].replace("Z", "+00:00"))
    expires = datetime.fromisoformat(authorization["expires_at"].replace("Z", "+00:00"))
    if not issued <= now < expires:
        raise V2Error("operator authorization is not currently valid")
    with tempfile.TemporaryDirectory(prefix="plan21-v2-signature-") as temp_name:
        message_path = Path(temp_name) / "message.bin"
        signature_path = Path(temp_name) / "signature.bin"
        message_path.write_bytes(json.dumps(signed_payload, sort_keys=True, separators=(",", ":")).encode())
        signature_path.write_bytes(base64.b64decode(authorization["signature"], validate=True))
        result = subprocess.run(["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(public_key_path), "-rawin", "-in", str(message_path), "-sigfile", str(signature_path)], capture_output=True, check=False)
        if result.returncode != 0:
            raise V2Error("operator authorization signature verification failed")
    if continuation["continuation_id"] in current["consumed_continuation_ids"] or command["command_id"] in current["consumed_command_ids"]:
        raise V2Error("resume capability already consumed")
    updated = copy.deepcopy(current)
    updated["consumed_continuation_ids"] = sorted([*current["consumed_continuation_ids"], continuation["continuation_id"]])
    updated["consumed_command_ids"] = sorted([*current["consumed_command_ids"], command["command_id"]])
    updated["checkpoint_generation"] = current["checkpoint_generation"] + 1
    return updated


def validate_assurance_bytes(document: dict[str, Any], allowed_roots: list[Path]) -> None:
    schema = json.loads((ROOT / "contracts" / "baseline_assurance_addendum.schema.v2.json").read_text())
    if _schema_errors(schema, document):
        raise V2Error("baseline assurance schema failure")
    profile = document["sandbox_profile"]
    resolved_sources: dict[str, Path] = {}
    for path_field, hash_field in (("profile_path", "profile_sha256"), ("engine_binary_path", "engine_binary_sha256"), ("root_resolution_evidence_path", "root_resolution_evidence_sha256")):
        raw = Path(profile[path_field])
        candidates = [raw] if raw.is_absolute() else [root / raw for root in allowed_roots]
        existing = next((candidate for candidate in candidates if candidate.is_file() and not candidate.is_symlink()), None)
        if existing is None or digest_bytes(existing.read_bytes()) != profile[hash_field]:
            raise V2Error(f"sandbox assurance source mismatch: {path_field}")
        resolved_sources[path_field] = existing
    profile_stat = resolved_sources["profile_path"].stat()
    engine_stat = resolved_sources["engine_binary_path"].stat()
    if profile_stat.st_uid != profile["expected_owner_uid"] or f"0{profile_stat.st_mode & 0o777:03o}" != profile["expected_mode"]:
        raise V2Error("sandbox profile owner/mode mismatch")
    if engine_stat.st_uid != profile["engine_expected_owner_uid"] or f"0{engine_stat.st_mode & 0o777:03o}" != profile["engine_expected_mode"]:
        raise V2Error("sandbox engine owner/mode mismatch")
    try:
        profile_document = json.loads(resolved_sources["profile_path"].read_text())
        root_document = json.loads(resolved_sources["root_resolution_evidence_path"].read_text())
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise V2Error("sandbox profile/root evidence is not canonical JSON") from error
    profile_schema = json.loads((ROOT / "contracts" / "sandbox_profile.schema.v2.json").read_text())
    root_schema = json.loads((ROOT / "contracts" / "sandbox_root_evidence.schema.v2.json").read_text())
    if _schema_errors(profile_schema, profile_document) or _schema_errors(root_schema, root_document):
        raise V2Error("sandbox profile/root evidence schema failure")
    roots = profile_document["resolved_roots"]
    root_paths = [entry["path"] for entry in roots]
    if len(root_paths) != len(set(root_paths)):
        raise V2Error("sandbox profile repeats a resolved root")
    roots_digest = digest_value(roots)
    if root_document["profile_sha256"] != profile["profile_sha256"] or root_document["resolved_roots"] != roots or root_document["resolved_roots_digest"] != roots_digest or profile["expected_resolved_roots_digest"] != roots_digest:
        raise V2Error("sandbox profile and independently resolved roots disagree")
    probe_ids = [entry["id"] for entry in root_document["escape_probe_results"]]
    if len(probe_ids) != len(set(probe_ids)) or set(probe_ids) != {"relative", "absolute", "traversal", "symlink", "mount", "network", "credential"}:
        raise V2Error("sandbox escape-probe denominator mismatch")
    for probe in root_document["escape_probe_results"]:
        raw = Path(probe["source_path"])
        candidates = [raw] if raw.is_absolute() else [root / raw for root in allowed_roots]
        source = next((candidate for candidate in candidates if candidate.is_file() and not candidate.is_symlink()), None)
        if source is None:
            raise V2Error(f"sandbox probe source absent: {probe['id']}")
        data = source.read_bytes()
        if len(data) != probe["source_size"] or digest_bytes(data) != probe["evidence_hash"]:
            raise V2Error(f"sandbox probe evidence mismatch: {probe['id']}")
    operator = document["operator_authority"]
    authorization_root = Path(operator["authorization_root"])
    public_key = Path(operator["pinned_public_key_path"])
    if not authorization_root.is_dir() or authorization_root.is_symlink() or authorization_root.stat().st_mode & 0o022:
        raise V2Error("operator authorization root is absent or writable by group/other")
    if public_key.is_symlink() or not public_key.is_file() or authorization_root.resolve() not in public_key.resolve().parents or digest_bytes(public_key.read_bytes()) != operator["pinned_public_key_sha256"]:
        raise V2Error("operator public key source mismatch")
    for workspace in allowed_roots:
        workspace = workspace.resolve()
        if workspace == authorization_root.resolve() or workspace in authorization_root.resolve().parents or authorization_root.resolve() in workspace.parents:
            raise V2Error("operator authorization root overlaps model/workspace roots")


def validate(delta: dict[str, Any], schema: dict[str, Any], base: dict[str, Any]) -> None:
    errors = _schema_errors(schema, delta)
    if errors:
        raise V2Error("v2 delta schema failure: " + "; ".join(error.message for error in errors))
    base_schema = json.loads((ROOT / "graph_engineered_subscription_execution.schema.v1.json").read_text())
    V1.validate(base, base_schema)
    for path in delta["contract_overrides"].values():
        schema_path = ROOT / path
        if not schema_path.is_file():
            raise V2Error(f"missing v2 contract: {path}")
        Draft202012Validator.check_schema(json.loads(schema_path.read_text()))
    for node_id, override in delta["node_contract_overrides"].items():
        prompt = ROOT / override["prompt_addendum"]
        if not prompt.is_file() or any(header not in prompt.read_text() for header in ("# GOAL", "# TEST", "# LOOP")):
            raise V2Error(f"invalid v2 prompt addendum: {node_id}")
    orchestrator = ROOT / delta["orchestrator_addendum"]
    if not orchestrator.is_file() or any(header not in orchestrator.read_text() for header in ("# GOAL", "# TEST", "# LOOP")):
        raise V2Error("invalid v2 orchestrator addendum")
    validate_registry(base)


def self_test(delta: dict[str, Any], schema: dict[str, Any], base: dict[str, Any]) -> None:
    sha = "0" * 64
    # Registry entries are validated even if an attacker adds an unused entry.
    bad_registry = copy.deepcopy(base)
    bad_registry["contract_registry"]["contract://bogus"] = {"owner": "P0", "resolver": "not.real", "schema_ref": "contracts/not-real.json"}
    try:
        validate_registry(bad_registry)
    except V2Error:
        pass
    else:
        raise V2Error("bogus registry entry unexpectedly passed")

    node = effective_node(base, delta, "P6")
    current = {"run_id": "run-0001", "node_id": "P6", "attempt": 1, "graph_digest": sha, "prompt_digest": sha, "policy_digest": sha, "schema_digest": sha, "route_digest": sha, "execution_contract_digest": sha, "predecessor_event_hash": sha, "checkpoint_hash": sha, "resolved_test_evidence_paths": {}, "resolved_artifact_paths": {}}
    with tempfile.TemporaryDirectory(prefix="plan21-v2-evidence-") as temp_name:
        evidence_root = Path(temp_name)
        test_sources = []
        test_results = []
        for test_id in node["required_test_ids"]:
            relative = f"tests/{test_id}.json"
            path = evidence_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            data = f'{{"test":"{test_id}","status":"PASS"}}'.encode()
            path.write_bytes(data)
            file_hash = digest_bytes(data)
            test_sources.append({"test_id": test_id, "status": "PASS", "source": {"path": relative, "sha256": file_hash, "size": len(data)}})
            test_results.append({"id": test_id, "status": "PASS", "evidence_hash": file_hash})
            current["resolved_test_evidence_paths"][test_id] = relative
        artifact_sources = []
        artifact_hashes = {}
        for index, artifact_id in enumerate(node["authorized_outputs"]):
            relative = f"artifacts/{index}.bin"
            path = evidence_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            data = f"artifact:{artifact_id}".encode()
            path.write_bytes(data)
            file_hash = digest_bytes(data)
            record = {"path": relative, "sha256": file_hash, "size": len(data)}
            aggregate = digest_value([record])
            artifact_sources.append({"artifact_id": artifact_id, "resolved_files": [record], "aggregate_sha256": aggregate})
            artifact_hashes[artifact_id] = aggregate
            current["resolved_artifact_paths"][artifact_id] = [relative]
        manifest = {"version": "2.0", **{key: current[key] for key in ("run_id", "node_id", "attempt", "graph_digest", "prompt_digest", "policy_digest", "schema_digest", "route_digest", "execution_contract_digest")}, "test_sources": test_sources, "artifact_sources": artifact_sources}
        event = {
            "version": "1.0", "event_id": sha, "run_id": current["run_id"], "node_id": "P6", "attempt": 1,
            "graph_digest": sha, "prompt_digest": sha, "policy_digest": sha, "schema_digest": sha, "route_digest": sha,
            "execution_contract_digest": sha, "predecessor_event_hash": sha, "checkpoint_hash": sha,
            "required_test_set_digest": digest_value(sorted(node["required_test_ids"])), "required_artifact_set_digest": digest_value(sorted(node["authorized_outputs"])),
            "outcome": "PASS", "failure_class": None, "repeat_signature": None, "reason_id": "ALL_TESTS_PASS", "pause_reason": None,
            "test_results": test_results, "artifact_hashes": artifact_hashes, "resume_node_id": None, "continuation_hash": None, "resume_command_hash": None,
            "admission_status": "CONTROLLER_VERIFIED", "binding_valid": True, "evidence_complete": True, "continuation_valid": True, "failure_mapping_valid": True,
            "controller_validation": {"binding_valid": True, "test_set_exact": True, "all_tests_pass": True, "artifact_set_exact": True, "artifact_hashes_valid": True, "failure_mapping_valid": True, "continuation_valid": True},
        }
        event["event_id"] = digest_value({key: value for key, value in event.items() if key != "event_id"})
        validate_phase_event_v2(event, manifest, node, current, evidence_root)
        fabricated = copy.deepcopy(event)
        fabricated["test_results"] = [{**item, "evidence_hash": sha} for item in fabricated["test_results"]]
        fabricated["artifact_hashes"] = {key: sha for key in fabricated["artifact_hashes"]}
        fabricated["event_id"] = digest_value({key: value for key, value in fabricated.items() if key != "event_id"})
        try:
            validate_phase_event_v2(fabricated, manifest, node, current, evidence_root)
        except (V2Error, V1.PlanError):
            pass
        else:
            raise V2Error("fabricated evidence hashes unexpectedly passed")
        missing_file = copy.deepcopy(manifest)
        missing_file["test_sources"][0]["source"]["path"] = "tests/not-real.json"
        try:
            validate_phase_event_v2(event, missing_file, node, current, evidence_root)
        except (V2Error, V1.PlanError):
            pass
        else:
            raise V2Error("nonexistent evidence source unexpectedly passed")

    ledger_current = {"run_id": "run-0001", "node_id": "P6", "phase_attempt": 1, "execution_contract_digest": sha}
    phase_key = f"{sha}:P6:1"
    one_subtask = {"version": "1.0", **ledger_current, "phase_key": phase_key, "required_subtask_ids": ["evidence-commit"], "subtasks": [{"subtask_id": "evidence-commit", "idempotency_key": f"{phase_key}:evidence-commit:{sha}", "input_digest": sha, "output_hashes": {"result": sha}, "state": "COMMITTED"}], "complete": True}
    try:
        validate_phase_ledger_v2(one_subtask, node, ledger_current)
    except V2Error:
        pass
    else:
        raise V2Error("self-denominated P6 ledger unexpectedly passed")

    with tempfile.TemporaryDirectory(prefix="plan21-v2-sandbox-") as temp_name:
        temp_root = Path(temp_name)
        workspace = temp_root / "workspace"
        auth_root = temp_root / "operator-authority"
        workspace.mkdir(); auth_root.mkdir()
        (workspace / "staged").mkdir(); (workspace / "output").mkdir()
        profile_path = workspace / "sandbox-profile.json"
        engine_path = workspace / "sandbox-engine"
        root_evidence_path = workspace / "root-evidence.json"
        public_key_path = auth_root / "operator-public.pem"
        engine_path.write_bytes(b"verified sandbox engine fixture")
        public_key_path.write_bytes(b"verified operator public key fixture")
        roots = [{"path": str(workspace / "staged"), "purpose": "staged_input", "read": True, "write": False}, {"path": str(workspace / "output"), "purpose": "controller_output", "read": True, "write": True}]
        profile_document = {"version": "2.0", "engine": "sandbox-exec", "resolved_roots": roots, "mount_policy": "DENY_UNDECLARED", "symlink_policy": "REJECT_ESCAPE", "network": {"mode": "DENY", "destinations": []}, "credential_boundary": "BROKERED_OUTSIDE_SANDBOX"}
        profile_path.write_bytes(json.dumps(profile_document, sort_keys=True, separators=(",", ":")).encode())
        probes = []
        for probe_id in ("relative", "absolute", "traversal", "symlink", "mount", "network", "credential"):
            source = workspace / f"probe-{probe_id}.json"
            data = json.dumps({"probe": probe_id, "status": "DENIED"}, sort_keys=True, separators=(",", ":")).encode()
            source.write_bytes(data)
            probes.append({"id": probe_id, "status": "DENIED", "source_path": str(source), "source_size": len(data), "evidence_hash": digest_bytes(data)})
        root_document = {"version": "2.0", "profile_sha256": digest_bytes(profile_path.read_bytes()), "resolved_roots": roots, "resolved_roots_digest": digest_value(roots), "escape_probe_results": probes}
        root_evidence_path.write_bytes(json.dumps(root_document, sort_keys=True, separators=(",", ":")).encode())
        profile_path.chmod(0o400); engine_path.chmod(0o500); root_evidence_path.chmod(0o400); public_key_path.chmod(0o400); auth_root.chmod(0o500)
        assurance = {"version": "2.0", "base_contract_hash": sha, "sandbox_profile": {"profile_path": str(profile_path), "profile_sha256": digest_bytes(profile_path.read_bytes()), "engine_binary_path": str(engine_path), "engine_binary_sha256": digest_bytes(engine_path.read_bytes()), "expected_owner_uid": os.getuid(), "expected_mode": "0400", "engine_expected_owner_uid": os.getuid(), "engine_expected_mode": "0500", "root_resolution_evidence_path": str(root_evidence_path), "root_resolution_evidence_sha256": digest_bytes(root_evidence_path.read_bytes()), "expected_resolved_roots_digest": digest_value(roots)}, "operator_authority": {"authorization_root": str(auth_root), "pinned_public_key_path": str(public_key_path), "pinned_public_key_sha256": digest_bytes(public_key_path.read_bytes()), "signature_algorithm": "Ed25519"}, "observed_unit_states": ["ACCEPTED", "ACCEPTED_PENDING_REVIEW", "BLOCKED", "SYSTEM_FAILURE"]}
        validate_assurance_bytes(assurance, [workspace])
        fabricated_assurance = copy.deepcopy(assurance)
        fabricated_assurance["sandbox_profile"]["root_resolution_evidence_sha256"] = sha
        try:
            validate_assurance_bytes(fabricated_assurance, [workspace])
        except V2Error:
            pass
        else:
            raise V2Error("fabricated sandbox assurance unexpectedly passed")
        auth_root.chmod(0o700)

    continuation = {"version": "1.0", "continuation_id": sha, "run_id": "run-0001", "suspended_node_id": "P2", "allowed_resume_node_id": "P2", "source_event_hash": sha, "checkpoint_hash": sha, "graph_digest": sha, "prompt_digest": sha, "policy_digest": sha, "schema_digest": sha, "route_digest": sha, "execution_contract_digest": sha, "next_attempt": 2, "reason_class": "AUTHENTICATION_MISSING", "consumed": False}
    with tempfile.TemporaryDirectory(prefix="plan21-v2-operator-") as temp_name:
        temp_root = Path(temp_name)
        auth_root = temp_root / "operator-authority"
        model_root = temp_root / "model-workspace"
        auth_root.mkdir(); model_root.mkdir()
        private_key = auth_root / "operator-private.pem"
        public_key = auth_root / "operator-public.pem"
        subprocess.run(["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private_key)], check=True, capture_output=True)
        subprocess.run(["openssl", "pkey", "-in", str(private_key), "-pubout", "-out", str(public_key)], check=True, capture_output=True)
        signed_payload = {"version": "2.0", "run_id": "run-0001", "continuation_id": sha, "continuation_hash": digest_value(continuation), "resume_node_id": "P2", "next_attempt": 2, "issued_by": "OPERATOR_AUTHORITY", "signer_key_id": "operator-key", "nonce": "0123456789abcdef", "issued_at": "2026-08-09T12:00:00Z", "expires_at": "2026-08-09T13:00:00Z"}
        message = auth_root / "message.bin"
        signature = auth_root / "signature.bin"
        message.write_bytes(json.dumps(signed_payload, sort_keys=True, separators=(",", ":")).encode())
        subprocess.run(["openssl", "pkeyutl", "-sign", "-inkey", str(private_key), "-rawin", "-in", str(message), "-out", str(signature)], check=True, capture_output=True)
        authorization = {"authorization_id": digest_value(signed_payload), **signed_payload, "signature": base64.b64encode(signature.read_bytes()).decode()}
        authorization_path = auth_root / "authorization.json"
        authorization_path.write_bytes(json.dumps(authorization, sort_keys=True, separators=(",", ":")).encode())
        for path in (private_key, public_key, message, signature, authorization_path):
            path.chmod(0o400)
        auth_root.chmod(0o500)
        auth_hash = digest_value(authorization)
        command = {"version": "1.0", "command_id": "1" * 64, "run_id": "run-0001", "continuation_id": sha, "continuation_hash": digest_value(continuation), "resume_node_id": "P2", "next_attempt": 2, "operator_authorization_hash": auth_hash}
        resume_current = {"run_id": "run-0001", "node_id": "P2", "attempt": 1, "source_event_hash": sha, "checkpoint_hash": sha, "graph_digest": sha, "prompt_digest": sha, "policy_digest": sha, "schema_digest": sha, "route_digest": sha, "execution_contract_digest": sha, "consumed_continuation_ids": [], "consumed_command_ids": [], "checkpoint_generation": 1, "authorization_root": str(auth_root), "authorization_path": str(authorization_path), "authorization_root_owner_uid": os.getuid(), "model_workspace_roots": [str(model_root)], "pinned_public_key_path": str(public_key), "pinned_public_key_sha256": digest_bytes(public_key.read_bytes()), "authorization_time": "2026-08-09T12:30:00Z"}
        updated = validate_resume_once(continuation, authorization, command, resume_current)
        try:
            validate_resume_once(continuation, authorization, command, updated)
        except V2Error:
            pass
        else:
            raise V2Error("identical resume unexpectedly passed twice")
        forged = copy.deepcopy(authorization)
        forged["signature"] = base64.b64encode(b"0" * 64).decode()
        authorization_path.chmod(0o600)
        authorization_path.write_bytes(json.dumps(forged, sort_keys=True, separators=(",", ":")).encode())
        authorization_path.chmod(0o400)
        forged_command = copy.deepcopy(command)
        forged_command["operator_authorization_hash"] = digest_value(forged)
        try:
            validate_resume_once(continuation, forged, forged_command, resume_current)
        except V2Error:
            pass
        else:
            raise V2Error("forged operator authorization unexpectedly passed")
        auth_root.chmod(0o700)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    delta, schema, base = load()
    validate(delta, schema, base)
    if args.self_test:
        self_test(delta, schema, base)
    print("plan21_v2_bootstrap=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
