#!/usr/bin/env python3
"""Read-only structural validator for the Run 27 execution scaffold."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

import jsonschema
import yaml


PLAN_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PLAN_DIR.parents[1]
GRAPH_PATH = PLAN_DIR / "implementation.graph.v1.yaml"
RESULT_SCHEMA_PATH = PLAN_DIR / "schemas/node_result.schema.v1.json"
APPROVAL_SCHEMA_PATH = PLAN_DIR / "schemas/spec_approval.schema.v1.json"
RESULT_VALIDATOR_PATH = PLAN_DIR / "tools/validate_result.py"


class ValidationError(RuntimeError):
    pass


def repo_path(value: str) -> Path:
    return REPO_ROOT / value


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationError(f"{path}: expected a mapping")
    return value


def validate_schema_file(path: Path) -> None:
    schema = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def validate_result_schema_semantics() -> None:
    schema = json.loads(RESULT_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    digest = "0" * 64
    base = {
        "schema_version": 1,
        "run_id": "run-1",
        "node_id": "N10_HARNESS_PROTOCOL",
        "attempt_id": "attempt-1",
        "outcome": "PASSED",
        "source_spec_sha256": digest,
        "prompt_sha256": digest,
        "predecessor_receipts": {"N00_SPEC_APPROVAL_GATE": digest},
        "changed_files": [],
        "commands": [],
        "evidence": [],
        "findings": [],
        "invalidated_descendants": [],
    }
    if not validator.is_valid(base):
        raise ValidationError("ordinary node result must validate without a terminal recommendation")
    if validator.is_valid({**base, "terminal_recommendation": "BLOCKED"}):
        raise ValidationError("non-N90 result must reject terminal_recommendation")
    n90 = {
        **base,
        "node_id": "N90_REQUIREMENTS_FINAL_AUDIT",
        "predecessor_receipts": {"N80_LIVE_WORKBOOK_PROOF": digest},
    }
    if validator.is_valid(n90):
        raise ValidationError("N90 result must require terminal_recommendation")
    if not validator.is_valid({**n90, "terminal_recommendation": "ACTIVATED"}):
        raise ValidationError("passing N90 result must admit ACTIVATED")
    if validator.is_valid({**n90, "outcome": "BLOCKED", "terminal_recommendation": "ACTIVATED"}):
        raise ValidationError("blocked N90 result must reject ACTIVATED")
    if not validator.is_valid({**n90, "outcome": "BLOCKED", "terminal_recommendation": "BLOCKED"}):
        raise ValidationError("blocked N90 result must admit BLOCKED")
    n00_blocked = {
        **base,
        "node_id": "N00_SPEC_APPROVAL_GATE",
        "outcome": "BLOCKED_SPEC_NOT_APPROVED",
        "source_spec_sha256": None,
        "predecessor_receipts": {},
    }
    if not validator.is_valid(n00_blocked):
        raise ValidationError("N00 must admit BLOCKED_SPEC_NOT_APPROVED as an outcome")
    if validator.is_valid({**base, "outcome": "BLOCKED_SPEC_NOT_APPROVED"}):
        raise ValidationError("only N00 may emit BLOCKED_SPEC_NOT_APPROVED")


def topological_order(nodes: dict[str, Any]) -> list[str]:
    unknown = {
        dependency
        for node in nodes.values()
        for dependency in node["depends_on"]
        if dependency not in nodes
    }
    if unknown:
        raise ValidationError(f"unknown dependencies: {sorted(unknown)}")
    remaining = {node_id: set(node["depends_on"]) for node_id, node in nodes.items()}
    order: list[str] = []
    while remaining:
        ready = sorted(node_id for node_id, dependencies in remaining.items() if not dependencies)
        if not ready:
            raise ValidationError(f"dependency cycle: {sorted(remaining)}")
        order.extend(ready)
        for node_id in ready:
            remaining.pop(node_id)
        for dependencies in remaining.values():
            dependencies.difference_update(ready)
    return order


def paths_overlap(left: str, right: str) -> bool:
    left_path = Path(left)
    right_path = Path(right)
    return left_path == right_path or left_path in right_path.parents or right_path in left_path.parents


def validate_graph(graph: dict[str, Any]) -> list[str]:
    required = {
        "graph_id", "version", "status", "source_incident", "source_spec",
        "runner", "qa_criteria", "node_result_schema", "entry",
        "result_pattern", "rules", "nodes", "edges", "terminals",
    }
    missing = sorted(required - graph.keys())
    if missing:
        raise ValidationError(f"missing graph keys: {missing}")
    if graph["graph_id"] != "plan27_langgraph_curriculum_factory_remediation":
        raise ValidationError("unexpected graph_id")
    if graph["version"] != 1:
        raise ValidationError("unexpected graph version")
    nodes = graph["nodes"]
    if not isinstance(nodes, dict) or not nodes:
        raise ValidationError("nodes must be a non-empty mapping")
    if graph["entry"] not in nodes or nodes[graph["entry"]]["depends_on"]:
        raise ValidationError("entry must exist and have no dependencies")

    for path_key in ("source_incident", "runner", "qa_criteria", "node_result_schema"):
        if not repo_path(graph[path_key]).is_file():
            raise ValidationError(f"missing {path_key}: {graph[path_key]}")
    if not RESULT_VALIDATOR_PATH.is_file():
        raise ValidationError("missing tools/validate_result.py")

    for node_id, node in nodes.items():
        for key in ("prompt", "depends_on", "writes", "verification", "allowed_results"):
            if key not in node:
                raise ValidationError(f"{node_id}: missing {key}")
        if not repo_path(node["prompt"]).is_file():
            raise ValidationError(f"{node_id}: missing prompt {node['prompt']}")
        if not node["writes"]:
            raise ValidationError(f"{node_id}: empty write set")
        if len(node["writes"]) != len(set(node["writes"])):
            raise ValidationError(f"{node_id}: duplicate write path")
        if not node["verification"]:
            raise ValidationError(f"{node_id}: verification must contain machine-runnable commands")
        for command in node["verification"]:
            if not isinstance(command, list) or not command or not all(isinstance(item, str) for item in command):
                raise ValidationError(f"{node_id}: invalid verification command: {command!r}")
        required_result_validation = [
            "python3",
            "plans/27_langgraph_curriculum_factory_remediation/tools/validate_result.py",
            "--node",
            node_id,
        ]
        if required_result_validation not in node["verification"]:
            raise ValidationError(f"{node_id}: missing exact schema/result validation command")
        read_only_inputs = node.get("read_only_inputs", [])
        if not isinstance(read_only_inputs, list) or len(read_only_inputs) != len(set(read_only_inputs)):
            raise ValidationError(f"{node_id}: read_only_inputs must be a unique list")
        for read_only in read_only_inputs:
            if any(paths_overlap(read_only, owner) for owner in node["writes"]):
                raise ValidationError(f"{node_id}: read-only input overlaps its write set: {read_only}")

    order = topological_order(nodes)
    positions = {node_id: index for index, node_id in enumerate(order)}
    edge_pairs = {(edge["from"], edge["to"]) for edge in graph["edges"]}
    dependency_pairs = {
        (dependency, node_id)
        for node_id, node in nodes.items()
        for dependency in node["depends_on"]
    }
    if edge_pairs != dependency_pairs:
        raise ValidationError(
            f"edge/dependency mismatch: edges_only={sorted(edge_pairs - dependency_pairs)}, "
            f"dependencies_only={sorted(dependency_pairs - edge_pairs)}"
        )
    for source, target in edge_pairs:
        if positions[source] >= positions[target]:
            raise ValidationError(f"non-forward edge: {source} -> {target}")

    if graph["rules"].get("allow_parallel_ready_nodes") is not False:
        raise ValidationError("Run 27 must remain sequential until harness hardening passes")
    if graph["rules"].get("markdown_status_is_authority") is not False:
        raise ValidationError("Markdown status cannot be admission authority")

    frozen_before_entry = graph["rules"].get("frozen_before_entry")
    if not isinstance(frozen_before_entry, list) or not frozen_before_entry:
        raise ValidationError("rules.frozen_before_entry must be a non-empty list")
    if graph["node_result_schema"] not in frozen_before_entry:
        raise ValidationError("the N00 node-result schema must be frozen before entry")
    for frozen in frozen_before_entry:
        if not repo_path(frozen).is_file():
            raise ValidationError(f"frozen pre-entry path is missing: {frozen}")
        owners = [
            node_id
            for node_id, node in nodes.items()
            if any(paths_overlap(frozen, owner) for owner in node["writes"])
        ]
        if owners:
            raise ValidationError(f"frozen pre-entry path has a node owner: {frozen} -> {owners}")

    # A path has one graph owner. Ordering alone must not authorize a downstream
    # node to rewrite an admitted predecessor's output.
    for index, left_id in enumerate(order):
        for right_id in order[index + 1:]:
            overlaps = any(
                paths_overlap(left, right)
                for left in nodes[left_id]["writes"]
                for right in nodes[right_id]["writes"]
            )
            if overlaps:
                raise ValidationError(f"overlapping write ownership: {left_id}, {right_id}")
    for node_id, node in nodes.items():
        for read_only in node.get("read_only_inputs", []):
            prior_owners = [
                owner_id
                for owner_id in order[:positions[node_id]]
                if any(paths_overlap(read_only, owner) for owner in nodes[owner_id]["writes"])
            ]
            if len(prior_owners) != 1:
                raise ValidationError(
                    f"{node_id}: read-only input must have exactly one prior owner: "
                    f"{read_only} -> {prior_owners}"
                )

    scan = graph["rules"].get("forbidden_production_scan")
    required_scan_keys = {
        "scan_roots",
        "excluded_globs",
        "excluded_roots",
        "prohibited_dispatch_or_import_terms",
        "prohibited_credential_names",
        "credential_absence_guard_paths",
        "credential_occurrence_policy",
    }
    if not isinstance(scan, dict) or required_scan_keys - scan.keys():
        raise ValidationError("forbidden_production_scan is missing its typed scope")
    for key in required_scan_keys - {"credential_occurrence_policy"}:
        values = scan[key]
        if not isinstance(values, list) or not values or len(values) != len(set(values)):
            raise ValidationError(f"forbidden_production_scan.{key} must be a unique non-empty list")
    excluded_roots = [Path(value) for value in scan["excluded_roots"]]
    for root_value in scan["scan_roots"]:
        root = Path(root_value)
        if any(excluded == root or excluded in root.parents for excluded in excluded_roots):
            raise ValidationError(f"scan root falls under an excluded root: {root_value}")
        if not repo_path(root_value).exists():
            raise ValidationError(f"forbidden production scan root does not exist: {root_value}")
    for guard_value in scan["credential_absence_guard_paths"]:
        guard = Path(guard_value)
        if not any(Path(root) == guard or Path(root) in guard.parents for root in scan["scan_roots"]):
            raise ValidationError(f"credential absence guard is outside scan_roots: {guard_value}")

    test_scan = graph["rules"].get("retired_provider_test_scan")
    required_test_scan_keys = {
        "scan_roots", "excluded_globs", "prohibited_terms", "occurrence_policy"
    }
    if not isinstance(test_scan, dict) or required_test_scan_keys - test_scan.keys():
        raise ValidationError("retired_provider_test_scan is missing its typed scope")
    if test_scan["occurrence_policy"] != "zero_occurrences_in_active_test_source":
        raise ValidationError("active tests must use the zero-occurrence retirement policy")
    for key in ("scan_roots", "excluded_globs", "prohibited_terms"):
        values = test_scan[key]
        if not isinstance(values, list) or not values or len(values) != len(set(values)):
            raise ValidationError(f"retired_provider_test_scan.{key} must be a unique non-empty list")
    for root_value in test_scan["scan_roots"]:
        if not repo_path(root_value).is_dir():
            raise ValidationError(f"active test scan root does not exist: {root_value}")
    test_terms = [value.casefold() for value in test_scan["prohibited_terms"]]
    scan_command = [
        "python3",
        "plans/27_langgraph_curriculum_factory_remediation/controller/check_forbidden_production_refs.py",
    ]
    affected_owners: set[str] = set()
    for root_value in test_scan["scan_roots"]:
        root_path = repo_path(root_value)
        for test_path in sorted(root_path.rglob("*.py")):
            relative = test_path.relative_to(REPO_ROOT).as_posix()
            text = test_path.read_text(encoding="utf-8").casefold()
            if not any(term in text for term in test_terms):
                continue
            owners = [
                node_id
                for node_id, node in nodes.items()
                if any(paths_overlap(owner, relative) for owner in node["writes"])
            ]
            if len(owners) != 1:
                raise ValidationError(
                    f"migration-affected active test must have exactly one owner: "
                    f"{relative} -> {owners}"
                )
            affected_owners.add(owners[0])
    for owner in affected_owners:
        if scan_command not in nodes[owner]["verification"]:
            raise ValidationError(
                f"owner of migration-affected tests must run the zero-occurrence scan: {owner}"
            )

    expected_terminals = {
        "ACTIVATED", "REMEDIATION_VERIFIED_NOT_ACTIVATED",
        "BLOCKED_SPEC_NOT_APPROVED", "BLOCKED",
    }
    if set(graph["terminals"]) != expected_terminals:
        raise ValidationError("terminal set does not match the plan")
    return order


def main() -> int:
    try:
        validate_schema_file(RESULT_SCHEMA_PATH)
        validate_schema_file(APPROVAL_SCHEMA_PATH)
        validate_result_schema_semantics()
        graph = load_yaml(GRAPH_PATH)
        order = validate_graph(graph)
    except (OSError, json.JSONDecodeError, yaml.YAMLError, jsonschema.SchemaError, ValidationError) as error:
        print(json.dumps({"valid": False, "error": str(error)}, sort_keys=True))
        return 1
    print(json.dumps({"valid": True, "graph_id": graph["graph_id"], "order": order}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
