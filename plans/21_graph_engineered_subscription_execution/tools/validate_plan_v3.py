#!/usr/bin/env python3
"""Deterministic bootstrap for Plan 21 v3 provenance and atomicity contracts."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import os
import sqlite3
import stat
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "graph_engineered_subscription_execution.plan.v3.yaml"
SCHEMA_PATH = ROOT / "graph_engineered_subscription_execution.schema.v3.json"


def _load_v2():
    spec = importlib.util.spec_from_file_location("plan21_v2_validator", ROOT / "tools" / "validate_plan_v2.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v2 validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V2 = _load_v2()
V1 = V2.V1


class V3Error(ValueError):
    pass


EXPECTED_SUBTASKS = {
    "P0": ["repository-inventory", "historical-census", "coverage-denominator", "baseline-contract", "assurance-addendum", "evidence-commit"],
    "P1": ["ir-schema", "compiler", "registry-resolver", "static-mutations", "self-compile", "evidence-commit"],
    "P2": ["adapter-build", "claude-capability", "codex-capability", "sandbox-profile-proof", "claude-canary", "codex-canary", "evidence-commit"],
    "P3": ["runtime-state", "checkpoint-store", "atomic-resume-consume", "crash-matrix", "evidence-commit"],
    "P4": ["status-migration", "adapter-migration", "policy-migration", "regression-suite", "evidence-commit"],
    "P5": ["generator-run", "deterministic-checks", "isolated-judges", "verdict-reducer", "repair-loop", "evidence-commit"],
    "P6": ["static-graph", "full-paths", "guard-boundaries", "fault-injection", "live-three-unit", "cold-resume", "four-judges", "historical-matrix", "independent-recompute", "supersession", "evidence-commit"],
}
EXPECTED_PROMPTS = {node: f"prompts/v3/{name}" for node, name in {
    "P0": "P0_trust_and_composite_contract.addendum.v3.md", "P1": "P1_effective_graph_compiler.addendum.v3.md",
    "P2": "P2_signed_execution_evidence.addendum.v3.md", "P3": "P3_atomic_resume_store.addendum.v3.md",
    "P4": "P4_composite_state_migration.addendum.v3.md", "P5": "P5_signed_evaluator_evidence.addendum.v3.md",
    "P6": "P6_provenance_release.addendum.v3.md", "P_ALL": "P_ALL_graph_orchestrator.addendum.v3.md",
}.items()}
EXPECTED_V2_ADDITIONAL_OUTPUTS = {"P0": ["plans/21_graph_engineered_subscription_execution/results/P0.assurance_addendum.v2.yaml"], "P1": [], "P2": [], "P3": [], "P4": [], "P5": [], "P6": []}


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_value(value: Any) -> str:
    return digest_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def behavioral_paths() -> list[Path]:
    paths = [
        ROOT / "graph_engineered_subscription_execution.plan.v1.yaml", ROOT / "graph_engineered_subscription_execution.schema.v1.json", ROOT / "tools/validate_plan.py",
        ROOT / "graph_engineered_subscription_execution.plan.v2.yaml", ROOT / "graph_engineered_subscription_execution.schema.v2.json", ROOT / "tools/validate_plan_v2.py",
        ROOT / "research/graph_engineering_sota.2026-08.md", ROOT / "assessment/plan20_gap_assessment.v1.md",
    ]
    paths += list((ROOT / "contracts").glob("*"))
    paths = [path for path in paths if ".v3." not in path.name]
    paths += list((ROOT / "prompts").glob("*.md")) + list((ROOT / "prompts/v2").glob("*.md"))
    return sorted({path for path in paths if path.is_file()})


def behavioral_digest() -> tuple[int, str]:
    records = [{"path": str(path.relative_to(ROOT)), "sha256": digest_bytes(path.read_bytes())} for path in behavioral_paths()]
    return len(records), digest_value(records)


def _schema(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text())


def _errors(schema: dict[str, Any], value: Any) -> list[Any]:
    return list(Draft202012Validator(schema).iter_errors(value))


def _schema_node(schema: dict[str, Any], dotted: str) -> dict[str, Any] | None:
    current = schema
    for segment in dotted.split("."):
        current = current.get("properties", {}).get(segment)
        if current is None:
            return None
    if "$ref" in current and current["$ref"].startswith("#/$defs/"):
        current = schema["$defs"][current["$ref"].split("/")[-1]]
    return current


def validate_registry_strict(base: dict[str, Any]) -> None:
    V2.validate_registry(base)
    for name, entry in base["contract_registry"].items():
        expected_owner = "PLAN" if name == "contract://anti_regression_sources" else "P0"
        expected_schema = "graph_engineered_subscription_execution.schema.v1.json" if expected_owner == "PLAN" else "contracts/baseline_contract.schema.v1.json"
        if entry["owner"] != expected_owner or entry["schema_ref"] != expected_schema:
            raise V3Error(f"registry owner/schema mismatch: {name}")
        node = _schema_node(_schema(entry["schema_ref"]), entry["resolver"])
        if node is None:
            raise V3Error(f"registry resolver absent: {name}")
        if expected_owner == "P0" and (node.get("type") != "array" or node.get("minItems", 0) < 1):
            raise V3Error(f"registry resolver has wrong value type: {name}")
        if expected_owner == "PLAN" and node.get("type") != "array":
            raise V3Error(f"registry resolver has wrong value type: {name}")


def validate_effective_overlays(v3: dict[str, Any], v2_delta: dict[str, Any], base: dict[str, Any]) -> None:
    if v3["required_subtask_ids"] != EXPECTED_SUBTASKS:
        raise V3Error("v3 subtask contract differs from compiled authority")
    if v3["prompt_addenda"] != EXPECTED_PROMPTS:
        raise V3Error("v3 prompt map differs from compiled authority")
    for node_id, path in EXPECTED_PROMPTS.items():
        prompt = ROOT / path
        if not prompt.is_file() or any(header not in prompt.read_text() for header in ("# GOAL", "# TEST", "# LOOP")):
            raise V3Error(f"invalid v3 prompt: {node_id}")
    output_owner: dict[str, str] = {}
    for node in base["nodes"]:
        override = v2_delta["node_contract_overrides"][node["id"]]
        if override["required_subtask_ids"] != EXPECTED_SUBTASKS[node["id"]]:
            raise V3Error(f"inherited subtask mutation: {node['id']}")
        if override["additional_outputs"] != EXPECTED_V2_ADDITIONAL_OUTPUTS[node["id"]]:
            raise V3Error(f"inherited output mutation: {node['id']}")
        for output in node["authorized_outputs"] + override["additional_outputs"]:
            if output in output_owner:
                raise V3Error(f"effective output collision: {output}")
            output_owner[output] = node["id"]
    state = v3["effective_graph_overrides"]["P0_contract_bundle"]
    if state != {"schema_ref": "contracts/p0_contract_bundle.schema.v3.json", "writer": "P0", "readers": ["P1", "P2", "P4", "P5", "P6"], "required_components": ["baseline_v1", "assurance_v3"]}:
        raise V3Error("effective P0 state override is not exact")
    expected_overrides = {
        "artifact_contract_registry": {"producer": "P1", "consumers": ["PHASE_CONTROLLER", "P2", "P3", "P4", "P5", "P6"], "coverage": "every_effective_node_authorized_output", "entry_fields": ["artifact_id", "resolver", "media_type", "schema_ref", "source_path_template"]},
        "trust_prerequisites": {"owner": "EXTERNAL_OPERATOR", "mutable_by_phases": False, "required_before": "P2", "absence_route": "PAUSED_PREREQUISITE", "absence_failure_class": "EXTERNAL_FACT_BLOCK"},
        "compiled_evidence_sources": {"test_path_template": "controller_evidence_root/{run_id}/{node_id}/tests/{test_id}.receipt.v3.json", "artifact_paths_from": "artifact_contract_registry", "ledger_path_template": "controller_evidence_root/{run_id}/{node_id}/ledgers/{subtask_id}.receipt.v3.json", "root_owner": "PHASE_CONTROLLER_SERVICE", "model_write_access": False},
        "resume_store": {"owner": "PHASE_CONTROLLER", "engine": "sqlite", "transaction": "BEGIN_IMMEDIATE_COMPARE_AND_SWAP", "unique_keys": ["continuation_id", "command_id", "authorization_id"], "consume_before_activation": True, "cold_process_test": True},
    }
    for key, expected in expected_overrides.items():
        if v3["effective_graph_overrides"][key] != expected:
            raise V3Error(f"effective override differs from compiled authority: {key}")
    validate_registry_strict(base)


def validate_external_trust(trust: dict[str, Any], model_roots: list[Path]) -> bool:
    schema = _schema("contracts/external_trust.schema.v3.json")
    if _errors(schema, trust):
        raise V3Error("external trust schema failure")
    if trust["status"] == "UNAVAILABLE":
        return False
    root = Path(trust["authority_root"])
    if root.is_symlink() or not root.is_dir():
        raise V3Error("external authority root absent")
    root_stat = root.stat()
    if root_stat.st_uid != trust["authority_uid"] or trust["authority_uid"] == trust["model_uid"] or root_stat.st_mode & 0o022:
        raise V3Error("external authority is not distinct and non-model-writable")
    for path_field, hash_field in (("controller_public_key_path", "controller_public_key_sha256"), ("operator_public_key_path", "operator_public_key_sha256")):
        path = Path(trust[path_field])
        if path.is_symlink() or not path.is_file() or root.resolve() not in path.resolve().parents or digest_bytes(path.read_bytes()) != trust[hash_field] or path.stat().st_mode & 0o022:
            raise V3Error(f"external trust key mismatch: {path_field}")
    for model_root in model_roots:
        resolved = model_root.resolve()
        if resolved == root.resolve() or resolved in root.resolve().parents or root.resolve() in resolved.parents:
            raise V3Error("external authority overlaps model workspace")
    return True


def _verify_signature(document: dict[str, Any], id_field: str, public_key: Path) -> None:
    payload = {key: value for key, value in document.items() if key not in {id_field, "signature"}}
    if document[id_field] != digest_value(payload):
        raise V3Error(f"{id_field} does not bind signed payload")
    with tempfile.TemporaryDirectory(prefix="plan21-v3-signature-") as temp_name:
        message = Path(temp_name) / "message.bin"
        signature = Path(temp_name) / "signature.bin"
        message.write_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
        try:
            signature.write_bytes(base64.b64decode(document["signature"], validate=True))
        except Exception as error:
            raise V3Error("invalid signature encoding") from error
        result = subprocess.run(["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(public_key), "-rawin", "-in", str(message), "-sigfile", str(signature)], capture_output=True, check=False)
        if result.returncode != 0:
            raise V3Error("signature verification failed")


def validate_test_receipt(receipt: dict[str, Any], current: dict[str, Any], public_key: Path) -> None:
    if _errors(_schema("contracts/test_receipt.schema.v3.json"), receipt):
        raise V3Error("test receipt semantic schema failure")
    for field in ("run_id", "node_id", "attempt"):
        if receipt[field] != current[field]:
            raise V3Error(f"test receipt stale binding: {field}")
    if receipt["test_id"] not in current["required_test_ids"] or receipt["subject_digest"] != current["test_subject_digests"].get(receipt["test_id"]):
        raise V3Error("test receipt is not bound to compiled test subject")
    if datetime.fromisoformat(receipt["completed_at"].replace("Z", "+00:00")) < datetime.fromisoformat(receipt["started_at"].replace("Z", "+00:00")):
        raise V3Error("test receipt time order invalid")
    _verify_signature(receipt, "receipt_id", public_key)


def validate_source(path: Path, expected_hash: str, expected_size: int) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise V3Error(f"source absent or symlink: {path}")
    data = path.read_bytes()
    if not data or len(data) != expected_size or digest_bytes(data) != expected_hash:
        raise V3Error(f"source bytes disagree: {path}")
    return data


def _validate_artifact_content(data: bytes, media_type: str, schema_ref: str | None) -> None:
    document: Any = None
    if media_type == "application/json":
        try:
            document = json.loads(data)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise V3Error("JSON artifact is not parseable") from error
    elif media_type == "application/yaml":
        try:
            document = yaml.safe_load(data)
        except yaml.YAMLError as error:
            raise V3Error("YAML artifact is not parseable") from error
    elif media_type == "text/markdown":
        try:
            text = data.decode()
        except UnicodeDecodeError as error:
            raise V3Error("Markdown artifact is not UTF-8") from error
        if not text.strip() or "#" not in text:
            raise V3Error("Markdown artifact lacks substantive structured content")
    if schema_ref is not None:
        schema_path = ROOT / schema_ref
        if document is None or not schema_path.is_file():
            raise V3Error("artifact schema is absent or incompatible with media type")
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        if _errors(schema, document):
            raise V3Error("artifact does not validate against compiled schema")


def validate_evidence_manifest(manifest: dict[str, Any], event: dict[str, Any], current: dict[str, Any], trust: dict[str, Any]) -> None:
    if not validate_external_trust(trust, [Path(path) for path in current["model_workspace_roots"]]):
        raise V3Error("external trust unavailable; evidence admission must pause")
    if _errors(_schema("contracts/evidence_manifest.schema.v3.json"), manifest):
        raise V3Error("evidence manifest schema failure")
    root = Path(current["controller_evidence_root"])
    if root.is_symlink() or not root.is_dir() or root.stat().st_uid != current["controller_uid"] or current["controller_uid"] == current["model_uid"] or root.stat().st_mode & 0o022:
        raise V3Error("controller evidence root is not distinct and protected")
    expected_manifest_path = root / current["run_id"] / current["node_id"] / f"attempt-{current['attempt']}.manifest.v3.json"
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    if expected_manifest_path.is_symlink() or not expected_manifest_path.is_file() or expected_manifest_path.read_bytes() != canonical:
        raise V3Error("manifest object is not the exact compiler-resolved controller file")
    for field in ("run_id", "node_id", "attempt", "graph_digest", "prompt_digest", "policy_digest", "schema_digest", "route_digest", "execution_contract_digest"):
        if manifest[field] != current[field]:
            raise V3Error(f"manifest stale binding: {field}")
    tests = {entry["test_id"]: entry for entry in manifest["test_receipts"]}
    artifacts = {entry["artifact_id"]: entry for entry in manifest["artifact_sources"]}
    if len(tests) != len(manifest["test_receipts"]) or set(tests) != set(current["required_test_ids"]):
        raise V3Error("manifest test denominator differs from compiled node")
    if len(artifacts) != len(manifest["artifact_sources"]) or set(artifacts) != set(current["artifact_contract_registry"]):
        raise V3Error("manifest artifact denominator differs from compiled registry")
    used_paths = set()
    controller_key = Path(trust["controller_public_key_path"])
    for test_id, entry in tests.items():
        expected = root / current["run_id"] / current["node_id"] / "tests" / f"{test_id}.receipt.v3.json"
        if Path(entry["path"]).resolve() != expected.resolve() or str(expected) in used_paths:
            raise V3Error("test receipt path is not unique/compiler-resolved")
        used_paths.add(str(expected))
        data = validate_source(expected, entry["sha256"], entry["size"])
        try:
            receipt = json.loads(data)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise V3Error("test evidence is not a semantic receipt") from error
        validate_test_receipt(receipt, current, controller_key)
        result = next((item for item in event["test_results"] if item["id"] == test_id), None)
        if result is None or result["status"] != "PASS" or result["evidence_hash"] != entry["sha256"]:
            raise V3Error("event does not bind signed test receipt")
    for artifact_id, entry in artifacts.items():
        compiled = current["artifact_contract_registry"][artifact_id]
        if {key: entry[key] for key in ("path", "media_type", "schema_ref")} != {key: compiled[key] for key in ("path", "media_type", "schema_ref")}:
            raise V3Error("artifact entry differs from compiler resolver/schema")
        path = Path(entry["path"])
        if str(path.resolve()) in used_paths:
            raise V3Error("one source file is reused across evidence categories")
        used_paths.add(str(path.resolve()))
        data = validate_source(path, entry["sha256"], entry["size"])
        _validate_artifact_content(data, entry["media_type"], entry["schema_ref"])
        if event["artifact_hashes"].get(artifact_id) != entry["sha256"]:
            raise V3Error("event does not bind validated artifact bytes")
    _verify_signature(manifest, "manifest_id", controller_key)
    if current["evidence_manifest_id"] != manifest["manifest_id"]:
        raise V3Error("runtime state does not bind evidence manifest")
    if event["event_id"] != digest_value({key: value for key, value in event.items() if key != "event_id"}):
        raise V3Error("event ID does not bind complete event")


def validate_sandbox_assurance(assurance: dict[str, Any], current: dict[str, Any]) -> None:
    trust = assurance["external_trust"]
    if not validate_external_trust(trust, [Path(path) for path in current["model_workspace_roots"]]):
        raise V3Error("sandbox assurance unavailable; P2 must pause")
    registry_path = Path(assurance["sandbox_engine_registry_path"])
    registry_data = validate_source(registry_path, assurance["sandbox_engine_registry_sha256"], registry_path.stat().st_size if registry_path.exists() else 0)
    registry = json.loads(registry_data)
    if _errors(_schema("contracts/sandbox_engine_registry.schema.v3.json"), registry):
        raise V3Error("sandbox engine registry schema failure")
    _verify_signature(registry, "registry_id", Path(trust["operator_public_key_path"]))
    sandbox = assurance["sandbox"]
    if sandbox is None or _errors(_schema("contracts/sandbox_assurance.schema.v3.json"), sandbox):
        raise V3Error("sandbox assurance schema failure")
    entries = [entry for entry in registry["entries"] if entry["engine"] == sandbox["selected_engine"]]
    if len(entries) != 1:
        raise V3Error("sandbox engine selection is not unique and allowlisted")
    validate_engine_entry(entries[0])
    profile_path = Path(sandbox["profile_path"])
    profile_data = validate_source(profile_path, sandbox["profile_sha256"], profile_path.stat().st_size if profile_path.exists() else 0)
    profile = json.loads(profile_data)
    if _errors(_schema("contracts/sandbox_profile.schema.v2.json"), profile) or profile["engine"] != sandbox["selected_engine"] or profile["resolved_roots"] != sandbox["resolved_roots"]:
        raise V3Error("sandbox profile differs from typed assurance")
    root_paths = [entry["path"] for entry in sandbox["resolved_roots"]]
    if len(root_paths) != len(set(root_paths)):
        raise V3Error("sandbox roots duplicate")
    for entry in sandbox["resolved_roots"]:
        path = Path(entry["path"])
        if not path.exists() or path.is_symlink():
            raise V3Error("sandbox resolved root does not exist")
    probe_path = Path(sandbox["probe_receipt_path"])
    probe_data = validate_source(probe_path, sandbox["probe_receipt_sha256"], sandbox["probe_receipt_size"])
    receipt = json.loads(probe_data)
    probe_current = {**current, "run_id": receipt.get("run_id"), "node_id": "P2", "attempt": receipt.get("attempt"), "required_test_ids": ["P2-T07"], "test_subject_digests": {"P2-T07": digest_value({"profile_sha256": sandbox["profile_sha256"], "engine_sha256": entries[0]["binary_sha256"], "resolved_roots": sandbox["resolved_roots"]})}}
    validate_test_receipt(receipt, probe_current, Path(trust["controller_public_key_path"]))
    assertion_ids = [item["id"] for item in receipt["assertions"]]
    required = ["relative", "absolute", "traversal", "symlink", "mount", "network", "credential"]
    if len(assertion_ids) != len(set(assertion_ids)) or sorted(assertion_ids) != sorted(required):
        raise V3Error("sandbox signed probe denominator mismatch")


def validate_subtask_receipt_sources(receipt: dict[str, Any], evidence_root: Path) -> None:
    if _errors(_schema("contracts/subtask_receipt.schema.v3.json"), receipt):
        raise V3Error("subtask receipt schema failure")
    seen = set()
    for source in receipt["output_sources"]:
        if source["path"] in seen:
            raise V3Error("duplicate subtask output source")
        seen.add(source["path"])
        path = Path(source["path"])
        if not path.is_absolute():
            path = evidence_root / path
        validate_source(path, source["sha256"], source["size"])


def validate_phase_ledger(ledger: dict[str, Any], current: dict[str, Any], evidence_root: Path, public_key: Path) -> None:
    if _errors(_schema("contracts/phase_ledger.schema.v3.json"), ledger):
        raise V3Error("phase ledger schema failure")
    for field in ("run_id", "node_id"):
        if ledger[field] != current[field]:
            raise V3Error(f"ledger stale binding: {field}")
    if ledger["phase_attempt"] != current["attempt"] or ledger["execution_contract_digest"] != current["execution_contract_digest"] or ledger["admitted_event_id"] != current["admitted_event_id"] or ledger["evidence_manifest_id"] != current["evidence_manifest_id"]:
        raise V3Error("ledger event/manifest/current binding mismatch")
    required = EXPECTED_SUBTASKS[current["node_id"]]
    entries = {entry["subtask_id"]: entry for entry in ledger["subtasks"]}
    if ledger["required_subtask_ids"] != required or len(entries) != len(ledger["subtasks"]) or set(entries) != set(required):
        raise V3Error("ledger denominator differs from compiled node")
    for subtask_id, entry in entries.items():
        expected_path = evidence_root / current["run_id"] / current["node_id"] / "ledgers" / f"{subtask_id}.receipt.v3.json"
        if Path(entry["receipt_path"]).resolve() != expected_path.resolve():
            raise V3Error("ledger receipt path is not compiler-resolved")
        data = validate_source(expected_path, entry["receipt_sha256"], entry["receipt_size"])
        receipt = json.loads(data)
        validate_subtask_receipt_sources(receipt, evidence_root)
        for field, value in (("run_id", current["run_id"]), ("node_id", current["node_id"]), ("attempt", current["attempt"]), ("subtask_id", subtask_id), ("admitted_event_id", current["admitted_event_id"]), ("evidence_manifest_id", current["evidence_manifest_id"]), ("input_digest", entry["input_digest"])):
            if receipt[field] != value:
                raise V3Error(f"subtask receipt binding mismatch: {field}")
        _verify_signature(receipt, "receipt_id", public_key)


def initialize_resume_store(path: Path, run_id: str, checkpoint_hash: str, generation: int) -> None:
    with sqlite3.connect(path) as connection:
        connection.executescript("""
        CREATE TABLE run_state(run_id TEXT PRIMARY KEY, checkpoint_hash TEXT NOT NULL, generation INTEGER NOT NULL);
        CREATE TABLE consumed_resume(continuation_id TEXT PRIMARY KEY, command_id TEXT UNIQUE NOT NULL, authorization_id TEXT UNIQUE NOT NULL, run_id TEXT NOT NULL, generation INTEGER NOT NULL);
        """)
        connection.execute("INSERT INTO run_state VALUES(?,?,?)", (run_id, checkpoint_hash, generation))


def consume_resume_atomic(path: Path, *, run_id: str, checkpoint_hash: str, expected_generation: int, continuation_id: str, command_id: str, authorization_id: str) -> bool:
    connection = sqlite3.connect(path, isolation_level=None, timeout=5)
    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute("SELECT checkpoint_hash,generation FROM run_state WHERE run_id=?", (run_id,)).fetchone()
        if row != (checkpoint_hash, expected_generation):
            connection.execute("ROLLBACK")
            return False
        connection.execute("INSERT INTO consumed_resume VALUES(?,?,?,?,?)", (continuation_id, command_id, authorization_id, run_id, expected_generation + 1))
        changed = connection.execute("UPDATE run_state SET generation=generation+1 WHERE run_id=? AND checkpoint_hash=? AND generation=?", (run_id, checkpoint_hash, expected_generation)).rowcount
        if changed != 1:
            connection.execute("ROLLBACK")
            return False
        connection.execute("COMMIT")
        return True
    except sqlite3.IntegrityError:
        connection.execute("ROLLBACK")
        return False
    finally:
        connection.close()


def validate_p0_bundle(bundle: dict[str, Any]) -> None:
    if set(bundle) != {"version", "baseline_v1", "assurance_v3"} or bundle["version"] != "3.0":
        raise V3Error("P0 composite bundle envelope invalid")
    baseline_schema = _schema("contracts/baseline_contract.schema.v1.json")
    if _errors(baseline_schema, bundle["baseline_v1"]):
        raise V3Error("P0 baseline v1 invalid")
    assurance = bundle["assurance_v3"]
    if assurance["base_contract_hash"] != digest_value(bundle["baseline_v1"]):
        raise V3Error("P0 assurance does not bind baseline bytes")
    if assurance["observed_unit_states"] != ["ACCEPTED", "ACCEPTED_PENDING_REVIEW", "BLOCKED", "SYSTEM_FAILURE"]:
        raise V3Error("P0 observed lifecycle vocabulary invalid")
    validate_external_trust(assurance["external_trust"], [])


def validate_engine_entry(entry: dict[str, Any]) -> None:
    path = Path(entry["binary_path"])
    data = validate_source(path, entry["binary_sha256"], path.stat().st_size if path.exists() else 0)
    if not os.access(path, os.X_OK):
        raise V3Error("sandbox engine is not executable")
    if data.startswith(b"\xcf\xfa\xed\xfe") or data.startswith(b"\xfe\xed\xfa\xcf"):
        actual_format = "MACH_O"
    elif data.startswith(b"\x7fELF"):
        actual_format = "ELF"
    else:
        raise V3Error("sandbox engine is not a recognized executable binary")
    if entry["binary_format"] != actual_format:
        raise V3Error("sandbox engine binary format mismatch")


def validate(v3: dict[str, Any], schema: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    errors = _errors(schema, v3)
    if errors:
        raise V3Error("v3 schema failure: " + "; ".join(error.message for error in errors))
    count, bundle_hash = behavioral_digest()
    if count != v3["behavioral_base"]["file_count"] or bundle_hash != v3["behavioral_base"]["sha256"]:
        raise V3Error("behavioral base file set/digest mismatch")
    v2_delta, v2_schema, base = V2.load()
    V2.validate(v2_delta, v2_schema, base)
    for contract in v3["contracts"].values():
        path = ROOT / contract
        if not path.is_file():
            raise V3Error(f"missing v3 contract: {contract}")
        Draft202012Validator.check_schema(json.loads(path.read_text()))
    validate_effective_overlays(v3, v2_delta, base)
    return v2_delta, base


def self_test(v3: dict[str, Any], v2_delta: dict[str, Any], base: dict[str, Any]) -> None:
    sha = "0" * 64
    shrunk = copy.deepcopy(v3); shrunk["required_subtask_ids"]["P6"] = ["evidence-commit"] * 5
    try:
        validate_effective_overlays(shrunk, v2_delta, base)
    except V3Error:
        pass
    else:
        raise V3Error("P6 subtask shrink unexpectedly passed")
    wrong_prompt = copy.deepcopy(v3); wrong_prompt["prompt_addenda"]["P6"] = v3["prompt_addenda"]["P5"]
    try:
        validate_effective_overlays(wrong_prompt, v2_delta, base)
    except V3Error:
        pass
    else:
        raise V3Error("wrong prompt mapping unexpectedly passed")
    wrong_owner = copy.deepcopy(base); wrong_owner["contract_registry"]["contract://anti_regression_sources"]["owner"] = "P0"
    try:
        validate_registry_strict(wrong_owner)
    except (V3Error, V2.V2Error):
        pass
    else:
        raise V3Error("wrong registry owner unexpectedly passed")
    wrong_type = copy.deepcopy(base); wrong_type["contract_registry"]["contract://anti_regression_sources"]["resolver"] = "goal"
    try:
        validate_registry_strict(wrong_type)
    except (V3Error, V2.V2Error):
        pass
    else:
        raise V3Error("wrong-type registry resolver unexpectedly passed")
    collided_v2 = copy.deepcopy(v2_delta)
    collided_v2["node_contract_overrides"]["P1"]["additional_outputs"] = [base["nodes"][0]["authorized_outputs"][0]]
    try:
        validate_effective_overlays(v3, collided_v2, base)
    except V3Error:
        pass
    else:
        raise V3Error("effective output collision unexpectedly passed")
    explicit_fail = {"version": "3.0", "receipt_id": sha, "run_id": "run-0001", "node_id": "P6", "attempt": 1, "test_id": "P6-T01", "runner": "DETERMINISTIC_TEST_RUNNER", "subject_digest": sha, "command_digest": sha, "exit_code": 0, "assertions": [{"id": "actual-result", "status": "FAIL", "observed_digest": sha}], "stdout_sha256": sha, "stderr_sha256": sha, "started_at": "2026-08-09T12:00:00Z", "completed_at": "2026-08-09T12:01:00Z", "signer_key_id": "controller-key", "signature": "A" * 86 + "=="}
    if not _errors(_schema("contracts/test_receipt.schema.v3.json"), explicit_fail):
        raise V3Error("explicit FAIL test receipt unexpectedly passed")
    try:
        _validate_artifact_content(b"this is unrelated plain text", "application/json", None)
    except V3Error:
        pass
    else:
        raise V3Error("unrelated plain text artifact unexpectedly passed JSON validation")
    with tempfile.TemporaryDirectory(prefix="plan21-v3-ledger-") as temp_name:
        root = Path(temp_name)
        output = root / "output.bin"; output.write_bytes(b"committed output")
        receipt = {"version": "3.0", "receipt_id": sha, "run_id": "run-0001", "node_id": "P6", "attempt": 1, "subtask_id": "static-graph", "input_digest": sha, "state": "COMMITTED", "output_sources": [{"artifact_id": "report", "path": str(output), "sha256": sha, "size": len(output.read_bytes())}], "admitted_event_id": sha, "evidence_manifest_id": sha, "signer_key_id": "controller-key", "signature": "A" * 86 + "=="}
        try:
            validate_subtask_receipt_sources(receipt, root)
        except V3Error:
            pass
        else:
            raise V3Error("zero-hash committed output unexpectedly passed")
    with tempfile.TemporaryDirectory(prefix="plan21-v3-resume-") as temp_name:
        store = Path(temp_name) / "resume.sqlite3"
        initialize_resume_store(store, "run-0001", sha, 1)
        first = consume_resume_atomic(store, run_id="run-0001", checkpoint_hash=sha, expected_generation=1, continuation_id=sha, command_id="1" * 64, authorization_id="2" * 64)
        second = consume_resume_atomic(store, run_id="run-0001", checkpoint_hash=sha, expected_generation=1, continuation_id=sha, command_id="1" * 64, authorization_id="2" * 64)
        if not first or second:
            raise V3Error("SQLite resume compare-and-swap is not single-use")
    with tempfile.TemporaryDirectory(prefix="plan21-v3-trust-") as temp_name:
        root = Path(temp_name)
        controller = root / "controller.pem"; operator = root / "operator.pem"
        controller.write_bytes(b"same uid controller"); operator.write_bytes(b"same uid operator")
        trust = {"status": "AVAILABLE", "reason": None, "authority_root": str(root), "authority_uid": os.getuid(), "model_uid": os.getuid(), "controller_public_key_path": str(controller), "controller_public_key_sha256": digest_bytes(controller.read_bytes()), "operator_public_key_path": str(operator), "operator_public_key_sha256": digest_bytes(operator.read_bytes())}
        try:
            validate_external_trust(trust, [])
        except V3Error:
            pass
        else:
            raise V3Error("same-uid self authority unexpectedly passed")
        engine = root / "fake-engine"; engine.write_bytes(b"plain text pretending to be sandbox"); engine.chmod(0o700)
        entry = {"binary_path": str(engine), "binary_sha256": digest_bytes(engine.read_bytes()), "binary_format": "MACH_O"}
        try:
            validate_engine_entry(entry)
        except V3Error:
            pass
        else:
            raise V3Error("plain-text sandbox engine unexpectedly passed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    v3 = yaml.safe_load(PLAN_PATH.read_text())
    schema = json.loads(SCHEMA_PATH.read_text())
    v2_delta, base = validate(v3, schema)
    if args.self_test:
        self_test(v3, v2_delta, base)
    print("plan21_v3_bootstrap=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
