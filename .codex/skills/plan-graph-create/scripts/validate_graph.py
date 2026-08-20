#!/usr/bin/env python3
"""Validate structural invariants of a plan-graph-create JSON artifact."""

import json
import sys
from pathlib import Path

REQUIRED_TOP = {"schema_version", "graph_id", "plan", "budgets", "protected_paths", "nodes", "edges", "traceability"}
KINDS = {"goal", "prompt_test", "implement", "result_test", "repair", "tool", "human_gate", "challenge", "verify"}
CONDITIONS = {"pass", "fail", "blocked", "approved", "always"}
REQUIRED_NODE = {"id", "kind", "title", "depends_on", "executor", "inputs", "outputs", "acceptance", "budget", "retry", "terminal_routes"}


def validate(data: dict, base: Path) -> list[str]:
    errors = []
    missing = REQUIRED_TOP - data.keys()
    if missing:
        errors.append(f"missing top-level members: {sorted(missing)}")
        return errors
    if data["schema_version"] != "1.0":
        errors.append("schema_version must be 1.0")
    nodes = data["nodes"]
    if not isinstance(nodes, list) or not nodes:
        errors.append("nodes must be a nonempty array")
        return errors
    ids = [node.get("id") for node in nodes if isinstance(node, dict)]
    if None in ids or len(ids) != len(nodes):
        errors.append("every node must be an object with an id")
    if len(ids) != len(set(ids)):
        errors.append("node ids must be unique")
    known = set(ids)
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id", "<unknown>")
        absent = REQUIRED_NODE - node.keys()
        if absent:
            errors.append(f"{node_id}: missing members {sorted(absent)}")
        if node.get("kind") not in KINDS:
            errors.append(f"{node_id}: invalid kind")
        for dependency in node.get("depends_on", []):
            if dependency not in known:
                errors.append(f"{node_id}: unknown dependency {dependency}")
        retry = node.get("retry", {})
        attempts = retry.get("max_attempts") if isinstance(retry, dict) else None
        if not isinstance(attempts, int) or attempts < 1:
            errors.append(f"{node_id}: retry.max_attempts must be a positive integer")
        executor = node.get("executor", {})
        if isinstance(executor, dict) and executor.get("type") == "model":
            for field in ("model", "effort", "routing_basis", "prompt_path"):
                if not executor.get(field):
                    errors.append(f"{node_id}: model executor missing {field}")
            prompt = executor.get("prompt_path")
            if prompt and not (base / prompt).is_file():
                errors.append(f"{node_id}: prompt_path does not exist: {prompt}")
    for edge in data["edges"]:
        if edge.get("from") not in known or edge.get("to") not in known:
            errors.append(f"edge references unknown node: {edge}")
        if edge.get("condition") not in CONDITIONS:
            errors.append(f"edge has invalid condition: {edge}")
    seen_requirements = set()
    for record in data["traceability"]:
        requirement = record.get("requirement_id")
        if not requirement or requirement in seen_requirements:
            errors.append(f"traceability requirement missing or duplicated: {requirement}")
        seen_requirements.add(requirement)
        for field in ("node_ids", "test_node_ids"):
            values = record.get(field)
            if not values:
                errors.append(f"{requirement}: {field} must be nonempty")
            elif any(value not in known for value in values):
                errors.append(f"{requirement}: {field} references unknown node")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_graph.py PLAN_GRAPH.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1]).resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    errors = validate(data, path.parent)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"VALID: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
