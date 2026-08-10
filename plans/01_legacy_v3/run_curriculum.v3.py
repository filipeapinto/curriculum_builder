#!/usr/bin/env python3
"""Test or execute the v3 serial multi-agent curriculum contract."""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any
from urllib.parse import unquote
import xml.etree.ElementTree as ET

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[4]
TEMPLATES = ROOT / "work/elegoo_labs/templates"
PROMPT = TEMPLATES / "component_lab_orchestrator_prompt_v3.md"
MANIFEST = TEMPLATES / "curriculum_lab_specs_v2.yaml"
MANIFEST_SCHEMA = TEMPLATES / "curriculum_lab_specs.schema_v2.json"
OVERRIDES = TEMPLATES / "curriculum_lab_overrides_v3.yaml"
OVERRIDE_SCHEMA = TEMPLATES / "curriculum_lab_overrides.schema_v3.json"
SCHEMAS = TEMPLATES / "automation_schemas"
MAP_RENDERER = TEMPLATES / "automation/render_deterministic_map.py"
CONCEPT_RENDERER = TEMPLATES / "automation/render_concept_diagram.py"
TEST_DIR = TEMPLATES / "prompt_tests/v3"
FINAL_SCHEMA = SCHEMAS / "final_acceptance.schema_v1.json"
FINAL_OUTPUT_SCHEMA = SCHEMAS / "final_acceptance.output.schema_v1.json"
WORKBOOK_SCHEMA = SCHEMAS / "workbook_acceptance.schema_v1.json"
WORKBOOK_OUTPUT_SCHEMA = SCHEMAS / "workbook_acceptance.output.schema_v1.json"
ROUTING_SCHEMA = TEMPLATES / "model_selector/routing_decision.schema_v1.json"
BOARD_PROFILE_DIR = TEMPLATES / "automation/board_profiles"
REVIEW_ROLES = {"electronics", "pedagogy", "communication", "graphic"}
REQUIRED_VISUAL_KINDS = {
    "reference_plate",
    "photorealistic_support",
    "deterministic_technical_map",
    "expected_state",
    "safety_sequence",
}


class RunnerError(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise RunnerError(f"{label} is missing: {path}")
    return path


def require_directory(path: Path, label: str) -> Path:
    if not path.is_dir():
        raise RunnerError(f"{label} is missing: {path}")
    return path


def validate_file(path: Path, schema_name: str, *, yaml_document: bool = False) -> Any:
    require_file(path, f"Schema input for {schema_name}")
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8")) if yaml_document else load_json(path)
        jsonschema.Draft202012Validator(load_json(SCHEMAS / schema_name)).validate(value)
    except (json.JSONDecodeError, UnicodeDecodeError, yaml.YAMLError, jsonschema.ValidationError) as error:
        raise RunnerError(f"{path} does not validate against {schema_name}: {error}") from error
    return value


def resolve_dossier_path(dossier: Path, value: str, label: str) -> Path:
    if value.startswith(("http://", "https://")):
        raise RunnerError(f"{label} must identify a cached dossier file, not a URL: {value}")
    raw = Path(value)
    candidate = raw if raw.is_absolute() else dossier / raw
    resolved = candidate.resolve()
    dossier_resolved = dossier.resolve()
    if resolved != dossier_resolved and dossier_resolved not in resolved.parents:
        raise RunnerError(f"{label} escapes the lab dossier: {value}")
    return resolved


def resolve_controller_path(dossier: Path, controller_dir: Path, value: str, label: str) -> Path:
    raw = Path(value)
    if raw.is_absolute():
        return resolve_dossier_path(dossier, value, label)
    controller_candidate = (controller_dir / raw).resolve()
    if controller_candidate.exists():
        return resolve_dossier_path(dossier, str(controller_candidate), label)
    return resolve_dossier_path(dossier, value, label)


def resolve_output_path(output_root: Path, value: str, label: str) -> Path:
    if value.startswith(("http://", "https://")):
        raise RunnerError(f"{label} must identify a generated file, not a URL: {value}")
    raw = Path(value)
    candidate = raw if raw.is_absolute() else output_root / raw
    resolved = candidate.resolve()
    root_resolved = output_root.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise RunnerError(f"{label} escapes the output root: {value}")
    return resolved


def audit_deterministic_renderer_replay(
    dossier: Path,
    job: dict[str, Any],
    receipt: dict[str, Any],
    output_path: Path,
) -> None:
    """Re-render deterministic technical assets and require byte-identical output."""
    kind = job["kind"]
    if kind not in {"deterministic_technical_map", "concept_diagram"}:
        return

    input_paths = [
        resolve_dossier_path(dossier, value, f"{job['id']} deterministic input")
        for value in receipt["input_paths"]
    ]
    expected_tool = (
        "render_deterministic_map.py"
        if kind == "deterministic_technical_map"
        else "render_concept_diagram.py"
    )
    if receipt["tool"] != expected_tool:
        raise RunnerError(
            f"{kind} {job['id']} must be the unmodified output of {expected_tool}; "
            f"receipt names {receipt['tool']!r}"
        )
    if receipt["technical_evidence"] is not True:
        raise RunnerError(f"{kind} {job['id']} must be marked as technical evidence")

    with tempfile.TemporaryDirectory(prefix="elegoo-render-replay-") as temp_value:
        temp_dir = Path(temp_value)
        replay_output = temp_dir / output_path.name
        replay_receipt = temp_dir / "receipt.json"
        if kind == "deterministic_technical_map":
            if len(input_paths) < 2:
                raise RunnerError(
                    f"Deterministic map {job['id']} needs a circuit and at least one profile"
                )
            command = [
                sys.executable,
                str(MAP_RENDERER),
                "--input",
                str(input_paths[0]),
                "--job-id",
                job["id"],
                "--output",
                str(replay_output),
                "--receipt",
                str(replay_receipt),
            ]
            variant_prefix = "schema-validated circuit/profile/experiment SVG render; variant="
            if receipt["prompt_or_command"].startswith(variant_prefix):
                if len(input_paths) < 3:
                    raise RunnerError(
                        f"Variant map {job['id']} lacks an experiment input"
                    )
                profile_paths = input_paths[1:-1]
                variant = receipt["prompt_or_command"][len(variant_prefix):]
                if not variant:
                    raise RunnerError(f"Variant map {job['id']} has an empty variant ID")
                command.extend(
                    ["--experiment", str(input_paths[-1]), "--variant", variant]
                )
            elif (
                receipt["prompt_or_command"]
                == "schema-validated circuit/profile/experiment SVG render"
            ):
                profile_paths = input_paths[1:]
            else:
                raise RunnerError(
                    f"Deterministic map {job['id']} has a non-renderer command/overlay claim"
                )
            for profile_path in profile_paths:
                command.extend(["--profile", str(profile_path)])
        else:
            if len(input_paths) != 1:
                raise RunnerError(
                    f"Concept diagram {job['id']} must have exactly one structured input"
                )
            command = [
                sys.executable,
                str(CONCEPT_RENDERER),
                "--input",
                str(input_paths[0]),
                "--diagram-id",
                job["id"],
                "--output",
                str(replay_output),
                "--receipt",
                str(replay_receipt),
            ]

        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if completed.returncode != 0:
            raise RunnerError(
                f"Deterministic replay failed for {job['id']}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        generated_receipt = load_json(replay_receipt)
        for field in (
            "job_id",
            "kind",
            "tool",
            "tool_version",
            "input_hashes",
            "dimensions",
            "technical_evidence",
            "prompt_or_command",
        ):
            if receipt[field] != generated_receipt[field]:
                raise RunnerError(
                    f"Deterministic replay metadata mismatch for {job['id']}: {field}"
                )
        if replay_output.read_bytes() != output_path.read_bytes():
            raise RunnerError(
                f"Deterministic visual {job['id']} was edited after rendering; "
                "post-render overlays and manual SVG changes are forbidden"
            )


def audit_reference_svg_sources(
    dossier: Path, output_path: Path, source_path: Path, job_id: str
) -> None:
    """Require every SVG image link to resolve and at least one to match the official source."""
    if output_path.suffix.lower() != ".svg":
        return
    try:
        root = ET.fromstring(output_path.read_text(encoding="utf-8"))
    except (ET.ParseError, UnicodeDecodeError) as error:
        raise RunnerError(f"Reference plate {job_id} is not valid SVG/XML: {error}") from error

    image_nodes = [node for node in root.iter() if node.tag.endswith("}image") or node.tag == "image"]
    if not image_nodes:
        raise RunnerError(
            f"Reference plate {job_id} is an SVG but contains no embedded/linked source image"
        )
    linked_hashes: set[str] = set()
    for index, node in enumerate(image_nodes, start=1):
        href = node.attrib.get("href") or node.attrib.get(
            "{http://www.w3.org/1999/xlink}href"
        )
        if not href:
            raise RunnerError(f"Reference plate {job_id} image #{index} has no href")
        if href.startswith("data:"):
            try:
                metadata, payload = href.split(",", 1)
                if ";base64" not in metadata or not metadata.startswith("data:image/"):
                    raise ValueError("not a base64 image data URI")
                linked_hashes.add(hashlib.sha256(base64.b64decode(payload)).hexdigest())
            except (ValueError, binascii.Error) as error:
                raise RunnerError(
                    f"Reference plate {job_id} image #{index} has an invalid image data URI"
                ) from error
            continue
        if href.startswith(("http://", "https://", "file://")):
            raise RunnerError(
                f"Reference plate {job_id} image #{index} must use cached dossier evidence"
            )
        relative_value = unquote(href.split("#", 1)[0])
        linked_path = (output_path.parent / relative_value).resolve()
        dossier_resolved = dossier.resolve()
        if (
            linked_path != dossier_resolved
            and dossier_resolved not in linked_path.parents
        ):
            raise RunnerError(
                f"Reference plate {job_id} image #{index} escapes the dossier: {href}"
            )
        require_file(linked_path, f"Reference plate {job_id} image #{index}")
        linked_hashes.add(sha256(linked_path))

    official_hash = sha256(source_path)
    if official_hash not in linked_hashes:
        raise RunnerError(
            f"Reference plate {job_id} does not visibly embed/link its declared official source"
        )


def uses_controller(lab: dict[str, Any]) -> bool:
    if lab["core_activity"]["mode"] == "adult_led_controller_station":
        return True
    controller_scope = {
        "component_set": lab["component_set"],
        "required_explanation": lab["required_explanation"],
        "core_activity": lab["core_activity"],
        "safety_focus": lab["safety_focus"],
        "qa_focus": lab["qa_focus"],
    }
    return "controller" in json.dumps(controller_scope, sort_keys=True).lower()


def deep_merge(base: Any, patch: Any) -> Any:
    if isinstance(base, dict) and isinstance(patch, dict):
        result = dict(base)
        for key, value in patch.items():
            result[key] = deep_merge(result[key], value) if key in result else value
        return result
    return patch


def merged_manifest() -> dict[str, Any]:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    overrides = yaml.safe_load(OVERRIDES.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(load_json(MANIFEST_SCHEMA)).validate(manifest)
    jsonschema.Draft202012Validator(load_json(OVERRIDE_SCHEMA)).validate(overrides)
    merged = dict(manifest)
    merged["labs"] = [deep_merge(lab, overrides["labs"].get(lab["id"], {})) for lab in manifest["labs"]]
    jsonschema.Draft202012Validator(load_json(MANIFEST_SCHEMA)).validate(merged)
    expected = [f"L{i:02d}" for i in range(1, 36)]
    if [lab["id"] for lab in merged["labs"]] != expected:
        raise RunnerError("Merged manifest must contain L01 through L35 in order.")
    return merged


def renderer_version(path: Path) -> str:
    command = [
        sys.executable, "-c",
        "import runpy,sys; p=sys.argv[1]; sys.argv=[p]+sys.argv[2:]; runpy.run_path(p, run_name='__main__')",
        str(path), "--version",
    ]
    result = subprocess.run(command, cwd=Path(tempfile.gettempdir()), capture_output=True, text=True)
    if result.returncode != 0:
        raise RunnerError(f"Renderer preflight failed: {path.name}: {result.stderr}")
    return result.stdout.strip()


def codex_capabilities() -> dict[str, Any]:
    executable = shutil.which("codex")
    if not executable:
        raise RunnerError("The `codex` command is not available in PATH.")
    global_help = subprocess.run(
        [executable, "--help"], capture_output=True, text=True
    )
    exec_help = subprocess.run(
        [executable, "--enable", "multi_agent", "exec", "--help"],
        capture_output=True,
        text=True,
    )
    if global_help.returncode != 0 or "--enable" not in global_help.stdout:
        raise RunnerError("Codex CLI does not expose the required --enable feature flag")
    required_exec_flags = {"--json", "--output-schema", "--output-last-message", "--sandbox"}
    missing_flags = {
        flag for flag in required_exec_flags if flag not in exec_help.stdout
    }
    if exec_help.returncode != 0 or missing_flags:
        raise RunnerError(
            f"Codex exec lacks required automation flags: {sorted(missing_flags)}"
        )
    imagegen_skill = Path.home() / ".codex/skills/.system/imagegen/SKILL.md"
    if not imagegen_skill.is_file():
        raise RunnerError(
            f"The required $imagegen skill is unavailable: {imagegen_skill}"
        )
    return {
        "executable": executable,
        "multi_agent_enabled": True,
        "json_events": True,
        "imagegen_skill": str(imagegen_skill),
    }


def preflight() -> dict[str, Any]:
    manifest = merged_manifest()
    required_schemas = [
        "review_record.schema_v1.json", "decision_record.schema_v1.json", "state.schema_v1.json",
        "circuit.schema_v1.json", "experiment.schema_v1.json", "board_profile.schema_v1.json",
        "source_manifest.schema_v1.json", "visual_plan.schema_v1.json", "visual_receipt.schema_v1.json",
        "asset_manifest.schema_v1.json", "concept_diagram.schema_v1.json", "qa_checklist.schema_v1.json",
        "controller_manifest.schema_v1.json", "build_receipt.schema_v1.json",
        "expected_output.schema_v1.json", "final_acceptance.schema_v1.json",
        "final_acceptance.output.schema_v1.json", "manifest_trace.schema_v1.json",
        "workbook_acceptance.schema_v1.json", "workbook_acceptance.output.schema_v1.json",
        "workbook_assembly_manifest.schema_v1.json",
    ]
    for name in required_schemas:
        schema = load_json(SCHEMAS / name)
        jsonschema.Draft202012Validator.check_schema(schema)
    return {
        "status": "pass",
        "labs": len(manifest["labs"]),
        "map_renderer": renderer_version(MAP_RENDERER),
        "concept_renderer": renderer_version(CONCEPT_RENDERER),
        "codex": codex_capabilities(),
        "prompt_sha256": hashlib.sha256(PROMPT.read_bytes()).hexdigest(),
    }


def run_saved_test(path: Path) -> None:
    command = [
        sys.executable, "-c",
        "import runpy,sys; p=sys.argv[1]; sys.argv=[p]; runpy.run_path(p, run_name='__main__')",
        str(path),
    ]
    result = subprocess.run(command, cwd=Path(tempfile.gettempdir()), capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if result.returncode != 0:
        raise RunnerError(f"Prompt test failed: {path.name}")


def run_tests() -> None:
    run_saved_test(TEST_DIR / "test_l01_contract.py")
    run_saved_test(TEST_DIR / "test_concept_renderer.py")
    run_saved_test(TEST_DIR / "test_all_35_prompt_contract.py")
    run_saved_test(TEST_DIR / "test_representative_runtime_contracts.py")
    run_saved_test(TEST_DIR / "test_deterministic_renderer_replay.py")
    run_saved_test(TEST_DIR / "test_deterministic_renderer_visual_quality.py")
    run_saved_test(TEST_DIR / "test_reference_plate_source_integrity.py")
    run_saved_test(TEST_DIR / "test_runner_acceptance_audit.py")
    run_saved_test(TEST_DIR / "test_runner_workbook_audit.py")


def fresh_output(value: str) -> Path:
    output = Path(value).resolve() if Path(value).is_absolute() else (ROOT / value).resolve()
    if ROOT not in output.parents:
        raise RunnerError("Output root must be inside the workspace.")
    if output.exists():
        raise RunnerError(f"Refusing to update an existing version: {output}")
    output.mkdir(parents=True)
    return output


def run_codex_command(
    command: list[str],
    *,
    stdout_path: Path,
    stderr_path: Path,
    output_root: Path,
    progress_label: str,
) -> int:
    start = time.monotonic()
    next_heartbeat = start
    with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr_file:
        process = subprocess.Popen(
            command,
            cwd=Path(tempfile.gettempdir()),
            stdout=stdout_file,
            stderr=stderr_file,
            text=True,
        )
        while process.poll() is None:
            now = time.monotonic()
            if now >= next_heartbeat:
                try:
                    artifact_count = sum(
                        1 for path in output_root.rglob("*") if path.is_file()
                    )
                except OSError:
                    artifact_count = -1
                print(
                    json.dumps(
                        {
                            "progress": progress_label,
                            "elapsed_seconds": int(now - start),
                            "artifacts_written": artifact_count,
                        }
                    ),
                    flush=True,
                )
                next_heartbeat = now + 30
            time.sleep(2)
        return process.returncode


def audit_reviews(dossier: Path, phase: str) -> tuple[dict[str, dict[str, Any]], set[str]]:
    review_dir = require_directory(dossier / "reviews" / phase, f"{phase} review directory")
    review_paths = sorted(review_dir.glob("*.json"))
    if len(review_paths) != 4:
        raise RunnerError(
            f"{phase} review audit requires exactly four JSON records; found "
            f"{len(review_paths)} in {review_dir}"
        )
    records: dict[str, dict[str, Any]] = {}
    identities: set[str] = set()
    task_ids: set[str] = set()
    for path in review_paths:
        record = validate_file(path, "review_record.schema_v1.json")
        role = record["role"]
        if record["phase"] != phase:
            raise RunnerError(f"{path} declares phase {record['phase']!r}, expected {phase!r}")
        if path.stem != role:
            raise RunnerError(f"{path} filename must match its declared review role {role!r}")
        if role in records:
            raise RunnerError(f"Duplicate {phase} review role: {role}")
        if record["agent_identity"] in identities:
            raise RunnerError(
                f"{phase} reviews are not independent: duplicate agent_identity "
                f"{record['agent_identity']!r}"
            )
        if record["agent_task_id"] in task_ids:
            raise RunnerError(
                f"{phase} reviews are not distinct tasks: duplicate agent_task_id "
                f"{record['agent_task_id']!r}"
            )
        if record["verdict"] != "pass":
            raise RunnerError(f"Accepted dossier contains a non-passing {phase} review: {path}")
        identities.add(record["agent_identity"])
        task_ids.add(record["agent_task_id"])
        records[role] = record
    if set(records) != REVIEW_ROLES:
        raise RunnerError(
            f"{phase} review roles must be {sorted(REVIEW_ROLES)}; found {sorted(records)}"
        )
    return records, task_ids


def audit_visuals(dossier: Path) -> None:
    visual_plan = validate_file(dossier / "05_visual_plan.json", "visual_plan.schema_v1.json")
    asset_manifest = validate_file(dossier / "assets/manifest.json", "asset_manifest.schema_v1.json")
    jobs = visual_plan["jobs"]
    job_ids = [job["id"] for job in jobs]
    if len(job_ids) != len(set(job_ids)):
        raise RunnerError("05_visual_plan.json contains duplicate visual job IDs")
    planned_kinds = {job["kind"] for job in jobs}
    missing_kinds = REQUIRED_VISUAL_KINDS - planned_kinds
    if missing_kinds:
        raise RunnerError(f"Visual plan is missing mandatory jobs: {sorted(missing_kinds)}")

    assets = asset_manifest["assets"]
    asset_ids = [asset["id"] for asset in assets]
    if len(asset_ids) != len(set(asset_ids)):
        raise RunnerError("assets/manifest.json contains duplicate asset IDs")
    assets_by_id = {asset["id"]: asset for asset in assets}

    for job in jobs:
        job_id = job["id"]
        if job_id not in assets_by_id:
            raise RunnerError(f"Visual job {job_id!r} has no asset-manifest record")
        asset = assets_by_id[job_id]
        if asset["kind"] != job["kind"]:
            raise RunnerError(
                f"Visual job {job_id!r} kind mismatch: plan={job['kind']!r}, "
                f"asset={asset['kind']!r}"
            )
        if asset["output_path"] != job["output_path"]:
            raise RunnerError(f"Visual job {job_id!r} output path differs between plan and manifest")
        if asset["render_receipt_path"] != job["render_receipt_path"]:
            raise RunnerError(f"Visual job {job_id!r} receipt path differs between plan and manifest")

        output_path = resolve_dossier_path(dossier, asset["output_path"], f"{job_id} output")
        receipt_path = resolve_dossier_path(
            dossier, asset["render_receipt_path"], f"{job_id} render receipt"
        )
        require_file(output_path, f"Visual output for {job_id}")
        receipt = validate_file(receipt_path, "visual_receipt.schema_v1.json")
        output_hash = sha256(output_path)
        if asset["output_sha256"] != output_hash:
            raise RunnerError(
                f"Asset SHA-256 mismatch for {job_id}: manifest={asset['output_sha256']}, "
                f"actual={output_hash}"
            )
        if receipt["output_hash"] != output_hash:
            raise RunnerError(
                f"Receipt SHA-256 mismatch for {job_id}: receipt={receipt['output_hash']}, "
                f"actual={output_hash}"
            )
        if receipt["job_id"] != job_id or receipt["kind"] != job["kind"]:
            raise RunnerError(f"Receipt identity/kind mismatch for visual job {job_id}")
        receipt_output = resolve_dossier_path(
            dossier, receipt["output_path"], f"{job_id} receipt output"
        )
        if receipt_output != output_path:
            raise RunnerError(f"Receipt for {job_id} points to a different output file")
        if len(receipt["input_paths"]) != len(receipt["input_hashes"]):
            raise RunnerError(f"Receipt input path/hash counts differ for visual job {job_id}")
        for input_value, expected_hash in zip(
            receipt["input_paths"], receipt["input_hashes"], strict=True
        ):
            input_path = resolve_dossier_path(dossier, input_value, f"{job_id} receipt input")
            require_file(input_path, f"Receipt input for {job_id}")
            actual_hash = sha256(input_path)
            if actual_hash != expected_hash:
                raise RunnerError(
                    f"Receipt input SHA-256 mismatch for {job_id}: {input_path}"
                )
        undeclared_source_hashes = set(asset["source_hashes"]) - set(receipt["input_hashes"])
        if undeclared_source_hashes:
            raise RunnerError(
                f"Asset {job_id} declares source hashes absent from its production receipt: "
                f"{sorted(undeclared_source_hashes)}"
            )
        audit_deterministic_renderer_replay(dossier, job, receipt, output_path)

        if job["kind"] == "reference_plate":
            source_path = resolve_dossier_path(
                dossier, job["source_asset_path"], f"{job_id} reference source"
            )
            require_file(source_path, f"Reference source for {job_id}")
            audit_reference_svg_sources(dossier, output_path, source_path, job_id)
            if asset["source_provenance"]["source_type"] not in {
                "official_photo",
                "official_datasheet",
            }:
                raise RunnerError(
                    f"Reference plate {job_id} lacks official-photo/datasheet provenance"
                )
        if job["kind"] == "photorealistic_support":
            if asset["source_provenance"]["source_type"] != "imagegen_context":
                raise RunnerError(
                    f"Photorealistic asset {job_id} lacks ImageGen source provenance"
                )
            tool_name = receipt["tool"].lower().replace("_", "")
            if "imagegen" not in tool_name:
                raise RunnerError(
                    f"Photorealistic asset {job_id} receipt does not identify ImageGen: "
                    f"{receipt['tool']!r}"
                )
            if receipt["technical_evidence"] is not False:
                raise RunnerError(
                    f"Photorealistic asset {job_id} is incorrectly marked as technical evidence"
                )

    unplanned_assets = set(assets_by_id) - set(job_ids)
    if unplanned_assets:
        raise RunnerError(f"Asset manifest contains unplanned assets: {sorted(unplanned_assets)}")


def audit_controller(dossier: Path) -> None:
    controller_dir = require_directory(dossier / "06_controller", "Controller artifact directory")
    manifest = validate_file(
        controller_dir / "controller_manifest.json", "controller_manifest.schema_v1.json"
    )
    receipt = validate_file(
        controller_dir / "build_receipt.json", "build_receipt.schema_v1.json"
    )
    validate_file(controller_dir / "expected_output.json", "expected_output.schema_v1.json")
    require_file(controller_dir / "adult_upload_steps.md", "Adult controller upload steps")
    require_file(controller_dir / "build.stdout.log", "Controller build stdout")
    require_file(controller_dir / "build.stderr.log", "Controller build stderr")
    source_dir = require_directory(controller_dir / "source", "Controller source directory")

    if not manifest["source_files"]:
        raise RunnerError("Controller manifest contains no source files")
    for value in manifest["source_files"]:
        source_path = resolve_controller_path(
            dossier, controller_dir, value, "Controller source file"
        )
        require_file(source_path, "Controller source file")
        if source_dir.resolve() not in source_path.resolve().parents:
            raise RunnerError(f"Controller source file is outside 06_controller/source: {value}")

    stdout_path = resolve_controller_path(
        dossier, controller_dir, receipt["stdout_path"], "Controller build stdout path"
    )
    stderr_path = resolve_controller_path(
        dossier, controller_dir, receipt["stderr_path"], "Controller build stderr path"
    )
    require_file(stdout_path, "Controller build stdout path")
    require_file(stderr_path, "Controller build stderr path")
    for value, expected_hash in receipt["source_hashes"].items():
        source_path = resolve_controller_path(
            dossier, controller_dir, value, "Controller build source hash path"
        )
        require_file(source_path, "Controller build source hash path")
        actual_hash = sha256(source_path)
        if actual_hash != expected_hash:
            raise RunnerError(
                f"Controller source SHA-256 mismatch: {source_path}; "
                f"receipt={expected_hash}, actual={actual_hash}"
            )


def audit_dossier(
    lab: dict[str, Any], output_root: Path, runner_result: dict[str, Any]
) -> None:
    lab_id = lab["id"]
    if runner_result.get("lab_id") != lab_id:
        raise RunnerError(
            f"Runner result lab_id mismatch: requested {lab_id}, "
            f"received {runner_result.get('lab_id')!r}"
        )
    expected_dossier = output_root / "labs" / f"{lab_id}_{lab['slug']}"
    sibling_matches = sorted((output_root / "labs").glob(f"{lab_id}_*"))
    if sibling_matches != [expected_dossier]:
        raise RunnerError(
            f"Expected exactly one dossier at {expected_dossier}; found "
            f"{[str(path) for path in sibling_matches]}"
        )
    dossier = require_directory(expected_dossier, f"{lab_id} dossier")

    required_plain_files = [
        "00_manifest_trace.json",
        "01_authoring_plan.md",
        "01_component_research.md",
        "03_child_lab.md",
        "04_adult_technical_guide.md",
        "09_acceptance.md",
    ]
    for relative in required_plain_files:
        path = require_file(dossier / relative, f"Required dossier artifact {relative}")
        if path.stat().st_size == 0:
            raise RunnerError(f"Required dossier artifact is empty: {path}")
    require_directory(dossier / "references", "References directory")
    require_file(dossier / "references/official_kit_photo.jpg", "Cached official kit photograph")
    require_directory(dossier / "routing", "Routing decision directory")
    require_directory(dossier / "assets", "Assets directory")
    require_directory(dossier / "board_profiles", "Lab board-profile directory")

    trace = validate_file(
        dossier / "00_manifest_trace.json", "manifest_trace.schema_v1.json"
    )
    state = validate_file(dossier / "state.json", "state.schema_v1.json")
    plan_decision = validate_file(
        dossier / "plan_decision.json", "decision_record.schema_v1.json"
    )
    source_manifest = validate_file(
        dossier / "references/source_manifest.json", "source_manifest.schema_v1.json"
    )
    circuit = validate_file(
        dossier / "02_circuit.yaml", "circuit.schema_v1.json", yaml_document=True
    )
    experiment = validate_file(
        dossier / "02_experiment.yaml", "experiment.schema_v1.json", yaml_document=True
    )
    if lab_id == "L01":
        child_text = (dossier / "03_child_lab.md").read_text(encoding="utf-8")
        adult_text = (dossier / "04_adult_technical_guide.md").read_text(encoding="utf-8")
        for artifact_name, text in (
            ("03_child_lab.md", child_text),
            ("04_adult_technical_guide.md", adult_text),
        ):
            if re.search(r"\barrows?\b", text, flags=re.IGNORECASE):
                raise RunnerError(
                    f"{artifact_name} describes L01 teaching links as arrows; "
                    "the verified map uses arrow-free dashed paths and open gaps"
                )
        child_lower = child_text.lower()
        required_explanations = {
            "complete-loop explanation": ("complete", "loop"),
            "rail mechanism explanation": ("rail", "metal"),
            "source energy explanation": ("battery", "energy"),
        }
        for label, terms in required_explanations.items():
            if not all(term in child_lower for term in terms):
                raise RunnerError(
                    f"03_child_lab.md lacks the required L01 {label}: "
                    f"expected terms {terms}"
                )
    validate_file(
        dossier / "05_concept_diagrams.json", "concept_diagram.schema_v1.json"
    )
    checklist = validate_file(
        dossier / "qa_checklist.json", "qa_checklist.schema_v1.json"
    )
    qa_decision = validate_file(
        dossier / "qa_decision.json", "decision_record.schema_v1.json"
    )
    dossier_final = validate_file(
        dossier / "final_acceptance.json", "final_acceptance.schema_v1.json"
    )

    for artifact_name, artifact_lab_id in (
        ("00_manifest_trace.json", trace["lab_id"]),
        ("state.json", state["lab_id"]),
        ("02_experiment.yaml", experiment["lab_id"]),
        ("qa_checklist.json", checklist["lab_id"]),
        ("final_acceptance.json", dossier_final["lab_id"]),
    ):
        if artifact_lab_id != lab_id:
            raise RunnerError(
                f"{artifact_name} lab_id mismatch: expected {lab_id}, found {artifact_lab_id!r}"
            )
    if trace["merged_lab"] != lab:
        raise RunnerError("00_manifest_trace.json does not contain the authoritative merged lab")
    expected_trace_hashes = {
        "base_manifest_sha256": sha256(MANIFEST),
        "override_file_sha256": sha256(OVERRIDES),
        "manifest_schema_sha256": sha256(MANIFEST_SCHEMA),
        "merged_lab_sha256": canonical_sha256(lab),
    }
    for field, expected_hash in expected_trace_hashes.items():
        if trace[field] != expected_hash:
            raise RunnerError(
                f"00_manifest_trace.json {field} mismatch: "
                f"recorded={trace[field]}, expected={expected_hash}"
            )
    for collection_name in ("copied_reference_hashes", "copied_profile_hashes"):
        for value, expected_hash in trace[collection_name].items():
            copied_path = resolve_dossier_path(
                dossier, value, f"Manifest trace {collection_name} path"
            )
            require_file(copied_path, f"Manifest trace {collection_name} path")
            if sha256(copied_path) != expected_hash:
                raise RunnerError(
                    f"Manifest trace SHA-256 mismatch for {copied_path}"
                )
    if state["state"] != "ACCEPTED":
        raise RunnerError(f"Accepted runner result has non-ACCEPTED dossier state: {state['state']}")
    if plan_decision["decision"] != "AUTHOR" or plan_decision["next_state"] != "AUTHOR":
        raise RunnerError("Accepted dossier does not contain a final passing plan decision")
    if qa_decision["decision"] != "READY_FOR_FINAL" or qa_decision["next_state"] != "FINAL_ACCEPTANCE":
        raise RunnerError("Accepted dossier does not contain a READY_FOR_FINAL QA decision")
    for name, decision in (
        ("plan_decision.json", plan_decision),
        ("qa_decision.json", qa_decision),
    ):
        if (
            decision["failed_check_ids"]
            or decision["failed_artifacts"]
            or decision["required_changes"]
            or decision["blocked_claim"] is not None
            or decision["missing_source"] is not None
        ):
            raise RunnerError(f"Accepted dossier contains unresolved findings in {name}")
    if dossier_final != runner_result:
        raise RunnerError(
            "Dossier final_acceptance.json does not exactly match the runner's Codex result"
        )
    if dossier_final["decision"] != "ACCEPTED" or dossier_final["next_state"] != "ACCEPTED":
        raise RunnerError("audit_dossier may accept only an ACCEPTED final-acceptance record")

    plan_reviews, plan_task_ids = audit_reviews(dossier, "plan")
    qa_reviews, qa_task_ids = audit_reviews(dossier, "qa")
    if plan_task_ids & qa_task_ids:
        raise RunnerError(
            "Plan and QA reviews reuse agent_task_id values; distinct review tasks are required"
        )

    routing_paths = sorted((dossier / "routing").glob("*.json"))
    if not routing_paths:
        raise RunnerError("Accepted dossier contains no model-routing decision records")
    routed_task_ids: set[str] = set()
    routing_schema = load_json(ROUTING_SCHEMA)
    for path in routing_paths:
        try:
            record = load_json(path)
            jsonschema.Draft202012Validator(routing_schema).validate(record)
        except (json.JSONDecodeError, UnicodeDecodeError, jsonschema.ValidationError) as error:
            raise RunnerError(f"Invalid routing decision {path}: {error}") from error
        if record["status"] != "approved_to_run":
            raise RunnerError(f"Accepted dossier contains non-approved routing decision: {path}")
        if record["task_id"] in routed_task_ids:
            raise RunnerError(f"Duplicate routed task_id {record['task_id']!r}")
        routed_task_ids.add(record["task_id"])
    missing_review_routes = (plan_task_ids | qa_task_ids) - routed_task_ids
    if missing_review_routes:
        raise RunnerError(
            f"Review tasks lack routing decisions: {sorted(missing_review_routes)}"
        )

    checklist_ids = [item["id"] for item in checklist["checks"]]
    if len(checklist_ids) != len(set(checklist_ids)):
        raise RunnerError("QA checklist contains duplicate check IDs")
    for item in checklist["checks"]:
        if item["status"] != "pass":
            raise RunnerError(
                f"QA checklist is not complete: {item['id']} has status {item['status']!r}"
            )
        check_id = item["id"]
        for role in item["assigned_roles"]:
            matches = [check for check in qa_reviews[role]["checks"] if check["id"] == check_id]
            if len(matches) != 1 or matches[0]["status"] != "pass":
                raise RunnerError(
                    f"QA checklist check {check_id!r} is not passed exactly once by "
                    f"assigned role {role!r}"
                )

    expected_qa_paths = {
        resolve_dossier_path(dossier, value, "Final QA review path")
        for value in dossier_final["qa_review_paths"]
    }
    actual_qa_paths = {
        (dossier / "reviews/qa" / f"{role}.json").resolve() for role in REVIEW_ROLES
    }
    if expected_qa_paths != actual_qa_paths:
        raise RunnerError("final_acceptance.json does not cite the four audited QA review files")
    final_checklist_path = resolve_dossier_path(
        dossier, dossier_final["qa_checklist_path"], "Final QA checklist path"
    )
    if final_checklist_path != (dossier / "qa_checklist.json").resolve():
        raise RunnerError("final_acceptance.json cites the wrong QA checklist")
    if not dossier_final["evidence_paths"]:
        raise RunnerError("Accepted final_acceptance.json contains no evidence paths")
    for value in dossier_final["evidence_paths"]:
        if value.startswith(("http://", "https://")):
            continue
        evidence_path = resolve_dossier_path(dossier, value, "Final acceptance evidence path")
        require_file(evidence_path, "Final acceptance evidence path")

    profile_documents: dict[str, dict[str, Any]] = {}
    for profile_path in sorted(BOARD_PROFILE_DIR.glob("*.json")) + sorted(
        (dossier / "board_profiles").glob("*.json")
    ):
        profile = validate_file(profile_path, "board_profile.schema_v1.json")
        if profile["id"] in profile_documents:
            if profile_documents[profile["id"]] != profile:
                raise RunnerError(
                    f"Conflicting board/component profiles share ID {profile['id']!r}"
                )
            continue
        profile_documents[profile["id"]] = profile
    required_profile_ids = set(circuit["profile_refs"].values()) | {circuit["board_profile"]}
    missing_profiles = required_profile_ids - set(profile_documents)
    if missing_profiles:
        raise RunnerError(
            f"Circuit cites missing/unvalidated board profiles: {sorted(missing_profiles)}"
        )
    for component in source_manifest["components"]:
        if component["identity_confidence"] != "exact":
            raise RunnerError(
                f"Accepted dossier retains non-exact component identity for "
                f"{component['manifest_name']!r}: {component['identity_confidence']!r}"
            )
        profile_path = resolve_dossier_path(
            dossier, component["profile_path"], f"Source profile for {component['manifest_name']}"
        )
        validate_file(profile_path, "board_profile.schema_v1.json")
        source_value = component["datasheet_or_manual"]
        if not source_value.startswith(("http://", "https://")):
            source_path = resolve_dossier_path(
                dossier, source_value, f"Primary source for {component['manifest_name']}"
            )
            require_file(source_path, f"Primary source for {component['manifest_name']}")

    audit_visuals(dossier)
    if uses_controller(lab):
        audit_controller(dossier)


def execute_lab(lab: dict[str, Any], output_root: Path, model: str) -> dict[str, Any]:
    if not shutil.which("codex"):
        raise RunnerError("The `codex` command is not available in PATH.")
    result_dir = output_root / "_runner"
    result_dir.mkdir(exist_ok=True)
    result_path = result_dir / f"{lab['id']}.final_acceptance.json"
    task = f"""
Read and execute the complete contract in `{PROMPT}`.

Runtime values:
- WORKSPACE_ROOT: `{ROOT}`
- OUTPUT_ROOT: `{output_root}`
- RUN_MODE: single
- RUN_CONTEXT: outer_runner
- LAB_ID: {lab['id']}

Execute the required serial multi-agent plan/review/author/visual/QA/final-acceptance loop for this lab.
Create only the new dossier for {lab['id']}; do not alter earlier versions, templates, manifests, or other lab dossiers.
Your final response must be exactly the same JSON object written to the dossier's `final_acceptance.json` and must validate against `{FINAL_SCHEMA}`.
"""
    command = [
        "codex", "--enable", "multi_agent", "exec", "--skip-git-repo-check",
        "-C", str(ROOT), "--sandbox", "workspace-write", "--model", model,
        "--json", "--output-schema", str(FINAL_OUTPUT_SCHEMA),
        "--output-last-message", str(result_path), task,
    ]
    returncode = run_codex_command(
        command,
        stdout_path=result_dir / f"{lab['id']}.stdout.jsonl",
        stderr_path=result_dir / f"{lab['id']}.stderr.log",
        output_root=output_root,
        progress_label=lab["id"],
    )
    if returncode != 0:
        raise RunnerError(f"{lab['id']} Codex execution failed; inspect {result_dir}")
    try:
        result = load_json(result_path)
        jsonschema.Draft202012Validator(load_json(FINAL_SCHEMA)).validate(result)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError, jsonschema.ValidationError) as error:
        raise RunnerError(
            f"{lab['id']} returned an invalid final-acceptance result at {result_path}: {error}"
        ) from error
    if result["decision"] == "ACCEPTED":
        audit_dossier(lab, output_root, result)
    return result


def pdf_page_count(path: Path) -> int:
    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        result = subprocess.run(
            [pdfinfo, str(path)], capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Pages:"):
                    return int(line.split(":", 1)[1].strip())
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise RunnerError(
            "Cannot audit final PDF page count: neither pdfinfo nor pypdf is available"
        ) from error
    return len(PdfReader(str(path)).pages)


def audit_workbook(
    output_root: Path,
    labs: list[dict[str, Any]],
    runner_result: dict[str, Any],
) -> None:
    workbook = require_directory(output_root / "workbook", "Workbook dossier")
    dossier_final = validate_file(
        workbook / "final_acceptance.json", "workbook_acceptance.schema_v1.json"
    )
    if dossier_final != runner_result:
        raise RunnerError(
            "Workbook final_acceptance.json does not exactly match the runner result"
        )
    if dossier_final["decision"] != "ACCEPTED" or dossier_final["next_state"] != "ACCEPTED":
        raise RunnerError("Workbook audit may accept only an ACCEPTED record")

    markdown = require_file(workbook / "curriculum.md", "Assembled curriculum Markdown")
    pdf = require_file(workbook / "curriculum.pdf", "Final illustrated curriculum PDF")
    if not markdown.stat().st_size or not pdf.stat().st_size:
        raise RunnerError("Final workbook Markdown/PDF may not be empty")
    assembly = validate_file(
        workbook / "assembly_manifest.json",
        "workbook_assembly_manifest.schema_v1.json",
    )
    checklist = validate_file(
        workbook / "qa_checklist.json", "qa_checklist.schema_v1.json"
    )
    qa_decision = validate_file(
        workbook / "qa_decision.json", "decision_record.schema_v1.json"
    )
    require_file(workbook / "revision_log.md", "Workbook revision log")

    expected_lab_ids = [lab["id"] for lab in labs]
    if assembly["lab_order"] != expected_lab_ids:
        raise RunnerError("Workbook assembly manifest does not preserve L01-L35 order")
    if checklist["lab_id"] != "WORKBOOK":
        raise RunnerError("Workbook QA checklist lab_id must be WORKBOOK")
    if qa_decision["phase"] != "qa":
        raise RunnerError("Workbook QA decision must declare phase qa")
    if (
        qa_decision["decision"] != "READY_FOR_FINAL"
        or qa_decision["next_state"] != "FINAL_ACCEPTANCE"
        or qa_decision["failed_check_ids"]
        or qa_decision["failed_artifacts"]
        or qa_decision["required_changes"]
    ):
        raise RunnerError("Workbook QA decision contains unresolved findings")

    final_pdf = resolve_output_path(
        output_root, dossier_final["pdf_path"], "Workbook final PDF"
    )
    final_manifest = resolve_output_path(
        output_root,
        dossier_final["assembly_manifest_path"],
        "Workbook assembly manifest",
    )
    final_checklist = resolve_output_path(
        output_root, dossier_final["qa_checklist_path"], "Workbook QA checklist"
    )
    if final_pdf != pdf.resolve():
        raise RunnerError("Workbook final acceptance cites the wrong PDF")
    if final_manifest != (workbook / "assembly_manifest.json").resolve():
        raise RunnerError("Workbook final acceptance cites the wrong assembly manifest")
    if final_checklist != (workbook / "qa_checklist.json").resolve():
        raise RunnerError("Workbook final acceptance cites the wrong QA checklist")

    manifest_markdown = resolve_output_path(
        output_root, assembly["markdown_path"], "Assembly Markdown path"
    )
    manifest_pdf = resolve_output_path(
        output_root, assembly["pdf_path"], "Assembly PDF path"
    )
    if manifest_markdown != markdown.resolve() or manifest_pdf != pdf.resolve():
        raise RunnerError("Assembly manifest cites unexpected Markdown/PDF paths")
    actual_markdown_hash = sha256(markdown)
    actual_pdf_hash = sha256(pdf)
    if assembly["markdown_sha256"] != actual_markdown_hash:
        raise RunnerError("Assembly manifest Markdown SHA-256 does not match")
    if (
        assembly["pdf_sha256"] != actual_pdf_hash
        or dossier_final["pdf_sha256"] != actual_pdf_hash
    ):
        raise RunnerError("Final PDF SHA-256 does not match its acceptance records")

    actual_pages = pdf_page_count(pdf)
    if assembly["page_count"] != actual_pages:
        raise RunnerError(
            f"PDF page count mismatch: manifest={assembly['page_count']}, actual={actual_pages}"
        )
    final_render_paths = {
        resolve_output_path(output_root, value, "Rendered PDF page")
        for value in dossier_final["page_render_paths"]
    }
    disk_render_paths = {
        path.resolve() for path in (workbook / "page_renders").glob("*.png")
    }
    if final_render_paths != disk_render_paths or len(disk_render_paths) != actual_pages:
        raise RunnerError(
            "Rendered-page inventory must contain exactly one PNG for every PDF page"
        )
    for path in disk_render_paths:
        require_file(path, "Rendered PDF page")
        if path.stat().st_size == 0:
            raise RunnerError(f"Rendered PDF page is empty: {path}")

    reviews, _ = audit_reviews(workbook, "qa")
    expected_review_paths = {
        (workbook / "reviews/qa" / f"{role}.json").resolve() for role in REVIEW_ROLES
    }
    accepted_review_paths = {
        resolve_output_path(output_root, value, "Workbook QA review path")
        for value in dossier_final["qa_review_paths"]
    }
    if accepted_review_paths != expected_review_paths:
        raise RunnerError("Workbook final acceptance does not cite all four QA reviews")

    checklist_ids = [item["id"] for item in checklist["checks"]]
    if len(checklist_ids) != len(set(checklist_ids)):
        raise RunnerError("Workbook QA checklist contains duplicate check IDs")
    for item in checklist["checks"]:
        if item["status"] != "pass":
            raise RunnerError(
                f"Workbook QA check {item['id']!r} is not passed"
            )
        for role in item["assigned_roles"]:
            matches = [
                check for check in reviews[role]["checks"] if check["id"] == item["id"]
            ]
            if len(matches) != 1 or matches[0]["status"] != "pass":
                raise RunnerError(
                    f"Workbook check {item['id']!r} is not passed exactly once "
                    f"by assigned role {role!r}"
                )

    expected_acceptance_paths: set[Path] = set()
    required_source_paths: set[Path] = set()
    for lab in labs:
        dossier = output_root / "labs" / f"{lab['id']}_{lab['slug']}"
        acceptance_path = (dossier / "final_acceptance.json").resolve()
        accepted = validate_file(
            acceptance_path, "final_acceptance.schema_v1.json"
        )
        if accepted["lab_id"] != lab["id"] or accepted["decision"] != "ACCEPTED":
            raise RunnerError(f"Workbook includes a non-accepted lab: {lab['id']}")
        expected_acceptance_paths.add(acceptance_path)
        required_source_paths.update(
            {
                (dossier / "03_child_lab.md").resolve(),
                (dossier / "04_adult_technical_guide.md").resolve(),
            }
        )
        assets = validate_file(
            dossier / "assets/manifest.json", "asset_manifest.schema_v1.json"
        )
        required_source_paths.update(
            resolve_dossier_path(
                dossier, asset["output_path"], f"{lab['id']} workbook asset"
            )
            for asset in assets["assets"]
        )

    accepted_lab_paths = {
        resolve_output_path(output_root, value, "Workbook lab acceptance path")
        for value in dossier_final["lab_acceptance_paths"]
    }
    if accepted_lab_paths != expected_acceptance_paths:
        raise RunnerError("Workbook final acceptance does not cite exactly L01-L35")

    manifested_source_paths: set[Path] = set()
    source_lab_ids: set[str] = set()
    for source in assembly["sources"]:
        source_path = resolve_output_path(
            output_root, source["source_path"], "Workbook source"
        )
        require_file(source_path, "Workbook source")
        if sha256(source_path) != source["source_sha256"]:
            raise RunnerError(f"Workbook source SHA-256 mismatch: {source_path}")
        manifested_source_paths.add(source_path)
        source_lab_ids.add(source["lab_id"])
    if source_lab_ids != set(expected_lab_ids):
        raise RunnerError("Workbook assembly sources do not cover all 35 lab IDs")
    missing_sources = required_source_paths - manifested_source_paths
    if missing_sources:
        raise RunnerError(
            "Workbook assembly omits accepted text/assets: "
            f"{[str(path) for path in sorted(missing_sources)]}"
        )


def execute_workbook(
    output_root: Path, labs: list[dict[str, Any]], model: str
) -> dict[str, Any]:
    result_dir = output_root / "_runner"
    result_dir.mkdir(exist_ok=True)
    result_path = result_dir / "WORKBOOK.final_acceptance.json"
    task = f"""
Read and execute the complete contract in `{PROMPT}`.

Runtime values:
- WORKSPACE_ROOT: `{ROOT}`
- OUTPUT_ROOT: `{output_root}`
- RUN_MODE: all
- RUN_CONTEXT: workbook_only

All 35 lab dossiers have already passed the outer runner's independent audit.
Do not alter any lab dossier or template. Execute only Step 8: assemble the complete
illustrated curriculum, render the PDF, inspect every rendered page, run the four
independent serial workbook reviewers, loop revisions until all checks pass, and
write the workbook acceptance record.
Your final response must be exactly the same JSON object written to
`{output_root / 'workbook/final_acceptance.json'}` and must validate against
`{WORKBOOK_SCHEMA}`.
"""
    command = [
        "codex", "--enable", "multi_agent", "exec", "--skip-git-repo-check",
        "-C", str(ROOT), "--sandbox", "workspace-write", "--model", model,
        "--json", "--output-schema", str(WORKBOOK_OUTPUT_SCHEMA),
        "--output-last-message", str(result_path), task,
    ]
    returncode = run_codex_command(
        command,
        stdout_path=result_dir / "WORKBOOK.stdout.jsonl",
        stderr_path=result_dir / "WORKBOOK.stderr.log",
        output_root=output_root,
        progress_label="WORKBOOK",
    )
    if returncode != 0:
        raise RunnerError(f"Workbook Codex execution failed; inspect {result_dir}")
    try:
        result = load_json(result_path)
        jsonschema.Draft202012Validator(load_json(WORKBOOK_SCHEMA)).validate(result)
    except (
        FileNotFoundError,
        json.JSONDecodeError,
        UnicodeDecodeError,
        jsonschema.ValidationError,
    ) as error:
        raise RunnerError(
            f"Workbook returned an invalid acceptance result at {result_path}: {error}"
        ) from error
    if result["decision"] == "ACCEPTED":
        audit_workbook(output_root, labs, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--all", action="store_true")
    mode.add_argument("--lab-id")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--output-root")
    parser.add_argument("--model", default="gpt-5.6-sol")
    args = parser.parse_args()

    check = preflight()
    print(json.dumps({"preflight": check}))
    if args.test:
        run_tests()
        print(json.dumps({"tests": "pass", "labs_covered": 35}))
        return 0
    if args.preflight:
        return 0
    if not args.output_root:
        raise RunnerError("--output-root is required for generation.")
    manifest = merged_manifest()
    selected = manifest["labs"] if args.all else [next((lab for lab in manifest["labs"] if lab["id"] == args.lab_id), None)]
    if selected == [None]:
        raise RunnerError(f"Unknown lab ID: {args.lab_id}")
    output = fresh_output(args.output_root)
    summary: dict[str, Any] = {}
    for lab in selected:
        result = execute_lab(lab, output, args.model)
        summary[lab["id"]] = result["decision"]
        if result["decision"] != "ACCEPTED":
            break
    if args.all and len(summary) == len(manifest["labs"]) and all(
        value == "ACCEPTED" for value in summary.values()
    ):
        workbook_result = execute_workbook(output, manifest["labs"], args.model)
        summary["WORKBOOK"] = workbook_result["decision"]
    (output / "run_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    return 0 if all(value == "ACCEPTED" for value in summary.values()) else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RunnerError, jsonschema.ValidationError, yaml.YAMLError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
