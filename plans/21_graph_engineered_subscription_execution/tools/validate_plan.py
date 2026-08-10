#!/usr/bin/env python3
"""Deterministic bootstrap validation for the Plan 21 phase graph.

This is deliberately smaller than the production compiler created by P1. It
exists before P0 so the planning graph can reject structural contradictions
without asking a model to infer missing semantics.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "graph_engineered_subscription_execution.plan.v1.yaml"
SCHEMA_PATH = ROOT / "graph_engineered_subscription_execution.schema.v1.json"
PHASE_RESULT_SCHEMA_PATH = ROOT / "contracts" / "phase_result.schema.v1.json"
RUNTIME_STATE_SCHEMA_PATH = ROOT / "contracts" / "runtime_state.schema.v1.json"
CONTINUATION_SCHEMA_PATH = ROOT / "contracts" / "continuation.schema.v1.json"
RESUME_COMMAND_SCHEMA_PATH = ROOT / "contracts" / "resume_command.schema.v1.json"
PHASE_LEDGER_SCHEMA_PATH = ROOT / "contracts" / "phase_ledger.schema.v1.json"
BASELINE_SCHEMA_PATH = ROOT / "contracts" / "baseline_contract.schema.v1.json"


class PlanError(ValueError):
    pass


def _unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise PlanError(f"duplicate {label}")


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate_phase_event(event: dict[str, Any], node: dict[str, Any], current: dict[str, Any]) -> None:
    schema = json.loads(PHASE_RESULT_SCHEMA_PATH.read_text())
    errors = list(Draft202012Validator(schema).iter_errors(event))
    if errors:
        raise PlanError("phase event schema failure")
    for field in ("run_id", "graph_digest", "prompt_digest", "policy_digest", "schema_digest", "route_digest", "execution_contract_digest", "predecessor_event_hash", "checkpoint_hash", "attempt"):
        if event[field] != current[field]:
            raise PlanError(f"phase event stale binding: {field}")
    if event["node_id"] != node["id"]:
        raise PlanError("phase event node mismatch")
    test_ids = [item["id"] for item in event["test_results"]]
    _unique(test_ids, "phase test id")
    if set(test_ids) != set(node["required_test_ids"]):
        raise PlanError("phase event test denominator mismatch")
    if event["required_test_set_digest"] != _digest(sorted(node["required_test_ids"])):
        raise PlanError("phase event test-set digest mismatch")
    artifact_ids = list(event["artifact_hashes"])
    if set(artifact_ids) != set(node["authorized_outputs"]):
        raise PlanError("phase event artifact denominator mismatch")
    if event["required_artifact_set_digest"] != _digest(sorted(node["authorized_outputs"])):
        raise PlanError("phase event artifact-set digest mismatch")
    if event["outcome"] == "PASS" and any(item["status"] != "PASS" or item["evidence_hash"] is None for item in event["test_results"]):
        raise PlanError("PASS contains nonpassing evidence")


def validate_resume(continuation: dict[str, Any], command: dict[str, Any], current: dict[str, Any]) -> None:
    for path, document in ((CONTINUATION_SCHEMA_PATH, continuation), (RESUME_COMMAND_SCHEMA_PATH, command)):
        if list(Draft202012Validator(json.loads(path.read_text())).iter_errors(document)):
            raise PlanError("resume document schema failure")
    if continuation["run_id"] != current["run_id"] or command["run_id"] != current["run_id"]:
        raise PlanError("cross-run resume")
    for field in ("execution_contract_digest", "graph_digest", "prompt_digest", "policy_digest", "schema_digest", "route_digest", "checkpoint_hash"):
        if continuation[field] != current[field]:
            raise PlanError(f"stale resume binding: {field}")
    if continuation["source_event_hash"] != current["source_event_hash"]:
        raise PlanError("resume source-event mismatch")
    if continuation["suspended_node_id"] != continuation["allowed_resume_node_id"] or command["resume_node_id"] != continuation["allowed_resume_node_id"]:
        raise PlanError("cross-phase resume")
    if command["continuation_id"] != continuation["continuation_id"] or command["next_attempt"] != continuation["next_attempt"]:
        raise PlanError("resume continuation mismatch")
    if continuation["suspended_node_id"] != current["node_id"] or continuation["next_attempt"] != current["attempt"] + 1:
        raise PlanError("resume attempt/origin mismatch")
    if command["continuation_hash"] != _digest(continuation):
        raise PlanError("resume command does not bind exact continuation")


def validate_denominator(document: dict[str, Any]) -> None:
    categories = ("nodes", "edges", "guards", "side_effect_boundaries", "mutations", "historical_findings", "historical_anomalies")
    aggregate_names = ("node_count", "edge_count", "guard_count", "side_effect_boundary_count", "mutation_count", "historical_finding_count", "historical_anomaly_count")
    for category, aggregate in zip(categories, aggregate_names):
        ids = [record["id"] for record in document[category]]
        _unique(ids, f"{category} id")
        if document["aggregates"][aggregate] != len(ids):
            raise PlanError(f"{category} aggregate mismatch")


def validate_phase_ledger(ledger: dict[str, Any], current: dict[str, Any]) -> None:
    schema = json.loads(PHASE_LEDGER_SCHEMA_PATH.read_text())
    if list(Draft202012Validator(schema).iter_errors(ledger)):
        raise PlanError("phase ledger schema failure")
    for field in ("run_id", "node_id", "phase_attempt", "execution_contract_digest"):
        if ledger[field] != current[field]:
            raise PlanError(f"phase ledger stale binding: {field}")
    expected_phase_key = f"{current['execution_contract_digest']}:{current['node_id']}:{current['phase_attempt']}"
    if ledger["phase_key"] != expected_phase_key:
        raise PlanError("phase ledger key mismatch")
    subtask_ids = [entry["subtask_id"] for entry in ledger["subtasks"]]
    _unique(subtask_ids, "phase-ledger subtask id")
    if set(subtask_ids) != set(ledger["required_subtask_ids"]):
        raise PlanError("phase ledger subtask denominator mismatch")
    for entry in ledger["subtasks"]:
        expected = f"{expected_phase_key}:{entry['subtask_id']}:{entry['input_digest']}"
        if entry["idempotency_key"] != expected:
            raise PlanError("phase ledger idempotency-key mismatch")
    if ledger["complete"] != all(entry["state"] == "COMMITTED" for entry in ledger["subtasks"]):
        raise PlanError("phase ledger completion mismatch")


def validate(plan: dict[str, Any], schema: dict[str, Any]) -> None:
    errors = sorted(Draft202012Validator(schema).iter_errors(plan), key=lambda e: list(e.path))
    if errors:
        rendered = "; ".join(f"{'/'.join(map(str, e.path))}: {e.message}" for e in errors)
        raise PlanError(f"schema: {rendered}")

    nodes = {node["id"]: node for node in plan["nodes"]}
    node_ids = list(nodes)
    node_index = {node_id: index for index, node_id in enumerate(node_ids)}

    def ancestors(node_id: str) -> set[str]:
        result: set[str] = set()
        pending = list(nodes[node_id]["depends_on"])
        while pending:
            parent = pending.pop()
            if parent not in result:
                result.add(parent)
                pending.extend(nodes[parent]["depends_on"])
        return result
    edge_ids = [edge["id"] for edge in plan["edges"]]
    _unique([node["id"] for node in plan["nodes"]], "node id")
    _unique(edge_ids, "edge id")

    terminals = set(plan["state_schema"]["plan_terminal_states"])
    pauses = set(plan["state_schema"]["plan_pause_states"])
    guards = plan["guard_registry"]
    phase_result_schema = json.loads(PHASE_RESULT_SCHEMA_PATH.read_text())
    event_fields = set(phase_result_schema["properties"])
    event_failure_classes = {value for value in phase_result_schema["properties"]["failure_class"]["enum"] if value is not None}
    if set(plan["state_schema"]["failure_classes"]) != event_failure_classes:
        raise PlanError("plan failure classes disagree with phase event schema")
    required_admission_checks = {"current_run_binding", "monotonic_attempt", "predecessor_checkpoint_binding", "pinned_policy_schema_route_binding", "exact_required_tests", "all_required_tests_pass", "exact_required_artifacts", "artifact_hash_recompute", "legal_failure_mapping", "continuation_command_binding", "single_use_resume"}
    if set(plan["controller"]["admission_checks"]) != required_admission_checks:
        raise PlanError("phase controller admission checks are incomplete")
    runtime_state_schema = json.loads(RUNTIME_STATE_SCHEMA_PATH.read_text())
    if set(plan["state_schema"]["required_fields"]) != set(runtime_state_schema["required"]):
        raise PlanError("runtime state required fields disagree with typed state schema")
    used_guards = {edge["guard_id"] for edge in plan["edges"]}
    if used_guards != set(guards):
        raise PlanError("guard registry has missing or unused entries")
    for guard_id, guard in guards.items():
        fields = [predicate["field"] for predicate in guard["predicates"]]
        if len(fields) != len(set(fields)):
            raise PlanError(f"guard {guard_id} repeats a predicate field")
        unknown_fields = set(fields) - event_fields
        if unknown_fields:
            raise PlanError(f"guard {guard_id} uses unknown event fields {sorted(unknown_fields)}")
        root_validator = Draft202012Validator(phase_result_schema)
        for predicate in guard["predicates"]:
            if "equals" in predicate:
                property_schema = phase_result_schema["properties"][predicate["field"]]
                if not root_validator.evolve(schema=property_schema).is_valid(predicate["equals"]):
                    raise PlanError(f"guard {guard_id} predicate has wrong value type")
        if guard_id.endswith("_PASS"):
            dynamic = {p["field"]: p.get("equals_state") for p in guard["predicates"] if "equals_state" in p}
            required_dynamic = {
                "run_id": "current.run_id", "graph_digest": "current.graph_digest",
                "prompt_digest": "current.prompt_digest", "execution_contract_digest": "current.execution_contract_digest",
                "predecessor_event_hash": "current.predecessor_event_hash", "checkpoint_hash": "current.checkpoint_hash",
                "attempt": "current.attempt",
            }
            if dynamic != required_dynamic:
                raise PlanError(f"guard {guard_id} lacks exact current-attempt bindings")
    known_from = {"START", *node_ids, *pauses}
    known_to = {*node_ids, *terminals, *pauses}
    adjacency: dict[str, set[str]] = {}
    source_guard_outcomes: set[tuple[str, str, str]] = set()
    for edge in plan["edges"]:
        if edge["from"] not in known_from:
            raise PlanError(f"edge {edge['id']} has unknown source {edge['from']}")
        if edge["to"] not in known_to:
            raise PlanError(f"edge {edge['id']} has unknown target {edge['to']}")
        if edge["kind"] in {"repair", "retry"} and "max_attempts" not in edge:
            raise PlanError(f"edge {edge['id']} is unbounded")
        if edge["kind"] == "repair" and edge["from"] != edge["to"]:
            raise PlanError(f"repair edge {edge['id']} must target its owner")
        if edge["guard_id"] not in guards:
            raise PlanError(f"edge {edge['id']} has unregistered guard {edge['guard_id']}")
        outcome_predicates = [p["equals"] for p in guards[edge["guard_id"]]["predicates"] if p["field"] == "outcome"]
        if outcome_predicates != [edge["outcome"]]:
            raise PlanError(f"edge {edge['id']} outcome does not match its guard")
        guard_key = (edge["from"], edge["guard_id"], edge["outcome"])
        if guard_key in source_guard_outcomes:
            raise PlanError(f"duplicate source/guard/outcome {guard_key}")
        source_guard_outcomes.add(guard_key)
        predicates = guards[edge["guard_id"]]["predicates"]
        if edge["from"] in nodes and not any(p["field"] == "node_id" and p["equals"] == edge["from"] for p in predicates):
            raise PlanError(f"edge {edge['id']} guard does not bind its source node")
        if edge["kind"] == "resume" and not any(p["field"] == "resume_node_id" and p["equals"] == edge["to"] for p in predicates):
            raise PlanError(f"resume edge {edge['id']} guard does not bind its target")
        if edge["to"] in terminals and edge["kind"] != "terminal":
            raise PlanError(f"terminal edge {edge['id']} has kind {edge['kind']}")
        if edge["to"] == "PAUSED_PREREQUISITE" and edge["kind"] != "pause":
            raise PlanError(f"prerequisite edge {edge['id']} is not pause")
        if edge["to"] == "INTERRUPTED" and edge["kind"] != "interrupt":
            raise PlanError(f"interrupt edge {edge['id']} is not interrupt")
        if edge["from"] in pauses and edge["kind"] != "resume":
            raise PlanError(f"pause source {edge['id']} is not resume")
        adjacency.setdefault(edge["from"], set()).add(edge["to"])

    output_owners: dict[str, str] = {path: "PHASE_CONTROLLER" for path in plan["controller"]["authorized_outputs"]}
    for schema_ref in plan["controller"]["schemas"]:
        if not (ROOT / schema_ref).is_file():
            raise PlanError(f"missing controller schema {schema_ref}")
    for node in plan["nodes"]:
        for dep in node["depends_on"] + node["context_from"]:
            if dep not in nodes:
                raise PlanError(f"node {node['id']} references unknown node {dep}")
        prompt = ROOT / node["prompt"]
        if not prompt.is_file():
            raise PlanError(f"missing prompt {node['prompt']}")
        text = prompt.read_text()
        for header in ("# GOAL", "# TEST", "# LOOP"):
            if header not in text:
                raise PlanError(f"prompt {node['prompt']} lacks {header}")
        prompt_test_ids = {test_id for test_id in re.findall(r"\bP[0-9]+-T[0-9]{2}\b", text) if test_id.startswith(node["id"] + "-")}
        if prompt_test_ids != set(node["required_test_ids"]):
            raise PlanError(f"node {node['id']} required tests disagree with prompt")
        if not set(node["depends_on"]).issubset(node["context_from"]):
            raise PlanError(f"node {node['id']} context omits a dependency")
        incoming_success = {e["from"] for e in plan["edges"] if e["to"] == node["id"] and e["kind"] == "success"}
        if incoming_success != set(node["depends_on"]):
            raise PlanError(f"node {node['id']} dependencies disagree with success edges")
        expected_outcomes = {
            "REVISABLE": ("repair", node["id"]),
            "CONVERGENCE_EXHAUSTED": ("terminal", "SYSTEM_FAILURE"),
            "SYSTEM_FAILURE": ("terminal", "SYSTEM_FAILURE"),
            "INTERRUPTED": ("interrupt", "INTERRUPTED"),
        }
        expected_outcomes["PASS"] = ("terminal", "PLAN_APPROVED") if node["id"] == "P6" else ("success", None)
        for outcome, (kind, target) in expected_outcomes.items():
            matches = [e for e in plan["edges"] if e["from"] == node["id"] and e["outcome"] == outcome and e["kind"] == kind]
            if len(matches) != 1 or (target is not None and matches[0]["to"] != target):
                raise PlanError(f"node {node['id']} lacks exactly one valid {outcome} edge")
        for output in node["authorized_outputs"]:
            if output in output_owners:
                raise PlanError(f"output {output} owned by both {output_owners[output]} and {node['id']}")
            output_owners[output] = node["id"]
        ledger_suffix = f"results/ledgers/{node['id']}.attempt-{{attempt}}.ledger.v1.yaml"
        if not any(path.endswith(ledger_suffix) for path in node["authorized_outputs"]):
            raise PlanError(f"node {node['id']} lacks an immutable phase ledger")
        if "contracts/phase_ledger.schema.v1.json" not in node["output_schemas"]:
            raise PlanError(f"node {node['id']} lacks phase ledger schema")
        expected_phase_key = f"{{execution_contract_digest}}:{node['id']}:{{phase_attempt}}"
        if node["idempotency"]["phase_key_template"] != expected_phase_key:
            raise PlanError(f"node {node['id']} has invalid phase idempotency key")

    def artifact_owner(reference: str) -> tuple[str, str] | None:
        if not reference.startswith("artifact://"):
            return None
        producer, separator, relative = reference.removeprefix("artifact://").partition("/")
        if not separator or producer not in nodes or not relative:
            raise PlanError(f"invalid producer artifact reference {reference}")
        if relative not in nodes[producer]["authorized_outputs"]:
            raise PlanError(f"producer {producer} does not declare {relative}")
        return producer, relative

    def resolve_reference(reference: str, consumer: str, output_schema: bool = False) -> None:
        resolved_artifact = artifact_owner(reference)
        if resolved_artifact is not None:
            producer = resolved_artifact[0]
            if output_schema:
                if producer != consumer:
                    raise PlanError(f"node {consumer} claims another producer's output schema")
            elif producer not in ancestors(consumer) or producer not in nodes[consumer]["context_from"]:
                raise PlanError(f"node {consumer} consumes non-predecessor artifact {reference}")
            return
        if reference.startswith("state://"):
            field_name = reference.removeprefix("state://")
            if field_name not in plan["state_fields"]:
                raise PlanError(f"unknown state reference {reference}")
            writer = plan["state_fields"][field_name]["writers"][0]
            if writer not in ancestors(consumer) or writer not in nodes[consumer]["context_from"]:
                raise PlanError(f"node {consumer} consumes future or hidden state {reference}")
            if field_name not in nodes[consumer]["state_reads"]:
                raise PlanError(f"node {consumer} state input is not declared as a read")
            return
        if reference.startswith("contract://"):
            if reference not in plan["contract_registry"]:
                raise PlanError(f"unregistered contract reference {reference}")
            return
        if reference.startswith("repository://"):
            if reference != "repository://read-only":
                raise PlanError(f"unknown repository reference {reference}")
            return
        if "://" in reference:
            raise PlanError(f"unknown reference scheme {reference}")
        if not (ROOT / reference).exists():
            raise PlanError(f"missing local reference {reference}")

    for node in plan["nodes"]:
        for reference in node["authorized_inputs"] + node["input_schemas"]:
            resolve_reference(reference, node["id"])
        for reference in node["output_schemas"]:
            resolve_reference(reference, node["id"], output_schema=True)
        for output in node["authorized_outputs"]:
            if output.startswith("contract://") and output not in plan["contract_registry"]:
                raise PlanError(f"unregistered output contract {output}")
    for field_name, field in plan["state_fields"].items():
        reference = field["schema_ref"]
        resolved = artifact_owner(reference)
        if resolved is not None and resolved[0] != field["writers"][0]:
            raise PlanError(f"state field {field_name} schema is owned by another producer")
        elif resolved is None:
            if "://" in reference or not (ROOT / reference).is_file():
                raise PlanError(f"state field {field_name} has missing schema {reference}")

    # P2 and P6 have distinct, reversible prerequisite pauses.
    expected_pause_counts = {"P2": 2, "P6": 1}
    for node_id, expected_count in expected_pause_counts.items():
        matches = [e for e in plan["edges"] if e["from"] == node_id and e["to"] == "PAUSED_PREREQUISITE" and e["outcome"] == "PAUSED_PREREQUISITE"]
        if len(matches) != expected_count:
            raise PlanError(f"node {node_id} has wrong prerequisite pause count")
    for node_id in node_ids:
        matches = [e for e in plan["edges"] if e["from"] == "INTERRUPTED" and e["to"] == node_id and e["outcome"] == "RESUME"]
        if len(matches) != 1:
            raise PlanError(f"INTERRUPTED lacks resume edge to {node_id}")
    for node_id in ("P2", "P6"):
        matches = [e for e in plan["edges"] if e["from"] == "PAUSED_PREREQUISITE" and e["to"] == node_id and e["outcome"] == "RESUME"]
        if len(matches) != 1:
            raise PlanError(f"PAUSED_PREREQUISITE lacks resume edge to {node_id}")

    # State declarations are bidirectional: a node and the field registry must agree.
    fields = plan["state_fields"]
    for field_name, field in fields.items():
        if len(field["writers"]) != 1:
            raise PlanError(f"state field {field_name} must have one writer")
        for writer in field["writers"]:
            if field_name not in nodes[writer]["state_writes"]:
                raise PlanError(f"state field {field_name} writer declaration mismatch")
        for reader in field["readers"]:
            if field_name not in nodes[reader]["state_reads"]:
                raise PlanError(f"state field {field_name} reader declaration mismatch")
    for node in plan["nodes"]:
        expected_writes = {name for name, field in fields.items() if node["id"] in field["writers"]}
        expected_reads = {name for name, field in fields.items() if node["id"] in field["readers"]}
        if set(node["state_writes"]) != expected_writes:
            raise PlanError(f"node {node['id']} state writes disagree with registry")
        if set(node["state_reads"]) != expected_reads:
            raise PlanError(f"node {node['id']} state reads disagree with registry")

    reachable = {"START"}
    pending = ["START"]
    while pending:
        current = pending.pop()
        for target in adjacency.get(current, set()):
            if target not in reachable:
                reachable.add(target)
                pending.append(target)
    missing = set(node_ids) - reachable
    if missing:
        raise PlanError(f"unreachable nodes: {sorted(missing)}")

    for node_id in node_ids:
        seen = {node_id}
        pending = [node_id]
        reaches_terminal = False
        while pending:
            current = pending.pop()
            if current in terminals:
                reaches_terminal = True
                break
            for target in adjacency.get(current, set()):
                if target not in seen:
                    seen.add(target)
                    pending.append(target)
        if not reaches_terminal:
            raise PlanError(f"node {node_id} cannot reach a plan terminal")

    # Only the start/success dependency spine must be acyclic. Repair and
    # reversible pause/resume cycles are explicit and validated separately.
    non_loop_edges = [e for e in plan["edges"] if e["kind"] in {"start", "success"}]
    dag: dict[str, set[str]] = {}
    for edge in non_loop_edges:
        if edge["to"] in nodes:
            dag.setdefault(edge["from"], set()).add(edge["to"])
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise PlanError(f"unbounded control cycle includes {node}")
        if node in visited:
            return
        visiting.add(node)
        for target in dag.get(node, set()):
            visit(target)
        visiting.remove(node)
        visited.add(node)

    visit("START")

    if any(edge["to"] == "BLOCKED" for edge in plan["edges"]):
        raise PlanError("plan phases may not target unit BLOCKED")


def load() -> tuple[dict[str, Any], dict[str, Any]]:
    return yaml.safe_load(PLAN_PATH.read_text()), json.loads(SCHEMA_PATH.read_text())


def self_test(plan: dict[str, Any], schema: dict[str, Any]) -> None:
    mutations = []

    duplicate = copy.deepcopy(plan)
    duplicate["nodes"].append(copy.deepcopy(duplicate["nodes"][0]))
    mutations.append(("duplicate-node", duplicate))

    dangling = copy.deepcopy(plan)
    dangling["edges"][0]["to"] = "P999"
    mutations.append(("dangling-edge", dangling))

    unreachable = copy.deepcopy(plan)
    unreachable["edges"] = [e for e in unreachable["edges"] if e["to"] != "P4"]
    mutations.append(("unreachable-node", unreachable))

    unbounded = copy.deepcopy(plan)
    repair = next(e for e in unbounded["edges"] if e["kind"] == "repair")
    del repair["max_attempts"]
    mutations.append(("unbounded-repair", unbounded))

    unsafe_cycle = copy.deepcopy(plan)
    unsafe_cycle["edges"].append({
        "id": "E-UNSAFE-CYCLE", "from": "P6", "to": "P1",
        "guard_id": "UNSAFE_CYCLE", "outcome": "unsafe_cycle", "kind": "success"
    })
    mutations.append(("unbounded-cycle", unsafe_cycle))

    missing_owner = copy.deepcopy(plan)
    del missing_owner["nodes"][0]["owner"]
    mutations.append(("missing-node-contract", missing_owner))

    for name, edge_id in (
        ("missing-system", "E-P1-SYSTEM"),
        ("missing-repair", "E-P3-REPAIR"),
        ("missing-exhaustion", "E-P5-EXHAUSTED"),
        ("missing-pause", "E-P2-AUTH-PAUSE"),
        ("missing-resume", "E-INTERRUPTED-P4"),
    ):
        mutated = copy.deepcopy(plan)
        mutated["edges"] = [e for e in mutated["edges"] if e["id"] != edge_id]
        mutations.append((name, mutated))

    dependency_mismatch = copy.deepcopy(plan)
    next(n for n in dependency_mismatch["nodes"] if n["id"] == "P4")["depends_on"] = ["P2"]
    mutations.append(("dependency-mismatch", dependency_mismatch))

    context_mismatch = copy.deepcopy(plan)
    next(n for n in context_mismatch["nodes"] if n["id"] == "P5")["context_from"] = []
    mutations.append(("context-mismatch", context_mismatch))

    duplicate_guard = copy.deepcopy(plan)
    copied_edge = copy.deepcopy(next(e for e in duplicate_guard["edges"] if e["id"] == "E-P1-SYSTEM"))
    copied_edge["id"] = "E-P1-SYSTEM-DUP"
    duplicate_guard["edges"].append(copied_edge)
    mutations.append(("duplicate-guard-outcome", duplicate_guard))

    wrong_terminal_kind = copy.deepcopy(plan)
    next(e for e in wrong_terminal_kind["edges"] if e["id"] == "E-P6-APPROVED")["kind"] = "success"
    mutations.append(("wrong-terminal-kind", wrong_terminal_kind))

    duplicate_output = copy.deepcopy(plan)
    duplicate_output["nodes"][1]["authorized_outputs"].append(duplicate_output["nodes"][0]["authorized_outputs"][0])
    mutations.append(("duplicate-output-owner", duplicate_output))

    duplicate_state = copy.deepcopy(plan)
    duplicate_state["state_fields"]["P0_contract_bundle"]["writers"].append("P1")
    duplicate_state["nodes"][1]["state_writes"].append("P0_contract_bundle")
    mutations.append(("duplicate-state-owner", duplicate_state))

    missing_future_artifact = copy.deepcopy(plan)
    p3 = next(n for n in missing_future_artifact["nodes"] if n["id"] == "P3")
    p3["authorized_outputs"].remove("schemas/runtime_contract.schema.v1.json")
    mutations.append(("missing-producer-artifact", missing_future_artifact))

    missing_local_schema = copy.deepcopy(plan)
    next(n for n in missing_local_schema["nodes"] if n["id"] == "P0")["input_schemas"].append("contracts/not-real.schema.v1.json")
    mutations.append(("missing-local-schema", missing_local_schema))

    unknown_contract = copy.deepcopy(plan)
    next(n for n in unknown_contract["nodes"] if n["id"] == "P4")["authorized_inputs"].append("contract://P999/not-real")
    mutations.append(("unknown-contract", unknown_contract))

    future_artifact = copy.deepcopy(plan)
    p1 = next(n for n in future_artifact["nodes"] if n["id"] == "P1")
    p1["authorized_inputs"].append("artifact://P6/plans/21_graph_engineered_subscription_execution/supersession.v1.md")
    p1["context_from"].append("P6")
    mutations.append(("future-artifact", future_artifact))

    future_state = copy.deepcopy(plan)
    p1 = next(n for n in future_state["nodes"] if n["id"] == "P1")
    p1["authorized_inputs"].append("state://P6_release_bundle")
    p1["state_reads"].append("P6_release_bundle")
    future_state["state_fields"]["P6_release_bundle"]["readers"].append("P1")
    p1["context_from"].append("P6")
    mutations.append(("future-state", future_state))

    idempotency_collision = copy.deepcopy(plan)
    idempotency_collision["nodes"][1]["idempotency"]["phase_key_template"] = idempotency_collision["nodes"][0]["idempotency"]["phase_key_template"]
    mutations.append(("idempotency-collision", idempotency_collision))

    excessive_repair = copy.deepcopy(plan)
    next(e for e in excessive_repair["edges"] if e["kind"] == "repair")["max_attempts"] = 99
    mutations.append(("excessive-repair", excessive_repair))

    for name, mutated in mutations:
        try:
            validate(mutated, schema)
        except PlanError:
            continue
        raise PlanError(f"self-test mutation unexpectedly passed: {name}")

    # The exact fail-open events found by round-three QA must remain rejected.
    node = {item["id"]: item for item in plan["nodes"]}["P6"]
    sha = "0" * 64
    current = {"run_id": "run-0001", "graph_digest": sha, "prompt_digest": sha, "policy_digest": sha, "schema_digest": sha, "route_digest": sha, "execution_contract_digest": sha, "predecessor_event_hash": sha, "checkpoint_hash": sha, "attempt": 1}
    valid_event = {
        "version": "1.0", "event_id": sha, "run_id": current["run_id"], "node_id": "P6", "attempt": 1,
        "graph_digest": sha, "prompt_digest": sha, "policy_digest": sha, "schema_digest": sha, "route_digest": sha, "execution_contract_digest": sha, "predecessor_event_hash": sha,
        "checkpoint_hash": sha, "required_test_set_digest": _digest(sorted(node["required_test_ids"])),
        "required_artifact_set_digest": _digest(sorted(node["authorized_outputs"])), "outcome": "PASS",
        "failure_class": None, "repeat_signature": None, "reason_id": "ALL_TESTS_PASS", "pause_reason": None,
        "test_results": [{"id": test_id, "status": "PASS", "evidence_hash": sha} for test_id in node["required_test_ids"]],
        "artifact_hashes": {path: sha for path in node["authorized_outputs"]}, "resume_node_id": None,
        "continuation_hash": None, "resume_command_hash": None, "admission_status": "CONTROLLER_VERIFIED",
        "binding_valid": True, "evidence_complete": True, "continuation_valid": True, "failure_mapping_valid": True,
        "controller_validation": {"binding_valid": True, "test_set_exact": True, "all_tests_pass": True, "artifact_set_exact": True, "artifact_hashes_valid": True, "failure_mapping_valid": True, "continuation_valid": True},
    }
    validate_phase_event(valid_event, node, current)
    event_mutations = []
    empty_evidence = copy.deepcopy(valid_event); empty_evidence["test_results"] = []; empty_evidence["artifact_hashes"] = {}; event_mutations.append(("empty-evidence-pass", empty_evidence))
    failing_pass = copy.deepcopy(valid_event); failing_pass["test_results"][0]["status"] = "FAIL"; event_mutations.append(("failing-pass", failing_pass))
    missing_test = copy.deepcopy(valid_event); missing_test["test_results"].pop(); event_mutations.append(("missing-test", missing_test))
    missing_artifact = copy.deepcopy(valid_event); missing_artifact["artifact_hashes"].pop(next(iter(missing_artifact["artifact_hashes"]))); event_mutations.append(("missing-artifact", missing_artifact))
    wrong_run = copy.deepcopy(valid_event); wrong_run["run_id"] = "run-other"; event_mutations.append(("wrong-run", wrong_run))
    stale_policy = copy.deepcopy(valid_event); stale_policy["policy_digest"] = "1" * 64; event_mutations.append(("stale-policy", stale_policy))
    stale_schema = copy.deepcopy(valid_event); stale_schema["schema_digest"] = "1" * 64; event_mutations.append(("stale-schema", stale_schema))
    stale_route = copy.deepcopy(valid_event); stale_route["route_digest"] = "1" * 64; event_mutations.append(("stale-route", stale_route))
    wrong_test_digest = copy.deepcopy(valid_event); wrong_test_digest["required_test_set_digest"] = sha; event_mutations.append(("wrong-test-set-digest", wrong_test_digest))
    for name, event in event_mutations:
        try:
            validate_phase_event(event, node, current)
        except PlanError:
            continue
        raise PlanError(f"phase-event mutation unexpectedly passed: {name}")

    factory_pause = copy.deepcopy(valid_event)
    factory_pause.update({"outcome": "PAUSED_PREREQUISITE", "failure_class": "FACTORY_DEFECT", "reason_id": "AUTHENTICATION_MISSING", "pause_reason": {"kind": "AUTHENTICATION_MISSING", "evidence_hash": sha, "authorized_path": None}, "continuation_hash": sha})
    if Draft202012Validator(json.loads(PHASE_RESULT_SCHEMA_PATH.read_text())).is_valid(factory_pause):
        raise PlanError("illegal factory-defect pause unexpectedly passed")

    evidence = {"source": "local capability probe", "observed_at": "2026-08-09T12:00:00Z", "evidence_hash": sha}
    baseline = {
        "version": "1.0", "execution_contract_digest": sha,
        "protected_paths": ["plans/19_runtime_hardening"],
        "authorized_paths": {
            "P4": {"runtime_policy_schema": ["schemas/runtime.yaml"], "plan19_reconciliation": ["plans/19/reconcile.md"], "tests": ["tests/p4"]},
            "P5": {"runtime_policy_schema": ["schemas/eval.yaml"], "tests": ["tests/p5"]},
            "P6": {"fresh_test_roots": ["tmp/plan21"], "rt7_reconciliation": ["policy/deferred.v1.yaml"]},
        },
        "dirty_overlap_decisions": [{"path": "policy/deferred.v1.yaml", "owner": "user", "decision": "PROTECTED", "authorization_evidence": None}],
        "baseline_results": [{"id": "BASE-1", "command": "test baseline", "status": "PASS", "exit_code": 0, "evidence_hash": sha}],
        "capability_facts": {
            "claude_code": {"version": "2.1.226", "binary_sha256": sha, "auth_class": "CLAUDE_SUBSCRIPTION_OAUTH", "plan_subtype": "PRO", "metering_mode": "INCLUDED_SUBSCRIPTION_ONLY", "separately_billed_credits_enabled": False, "api_fallback_enabled": False, "native_executed_model_available": True, "evidence": evidence},
            "codex_cli": {"version": "0.147.0", "binary_sha256": sha, "auth_class": "CHATGPT_LOGIN", "plan_subtype": "PLUS", "metering_mode": "INCLUDED_SUBSCRIPTION_ONLY", "chatgpt_credits_enabled": False, "api_fallback_enabled": False, "requested_model": "gpt-5", "native_executed_model_available": False, "evidence": evidence},
            "provider_overrides": {name: False for name in ("ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN", "OPENAI_API_KEY", "CODEX_ACCESS_TOKEN", "OPENAI_BASE_URL", "OPENAI_API_BASE", "MODEL_PROVIDER", "API_KEY_HELPER")},
            "outer_sandbox": {"engine": "sandbox-exec", "engine_version": "1", "profile_sha256": sha, "policy_digest": sha, "resolved_roots": [{"path": "/staged/input", "purpose": "staged_input", "read": True, "write": False}, {"path": "/controller/output", "purpose": "controller_output", "read": True, "write": True}], "mount_policy": "DENY_UNDECLARED", "symlink_policy": "REJECT_ESCAPE", "network": {"mode": "DENY", "destinations": []}, "credential_boundary": "BROKERED_OUTSIDE_SANDBOX"},
        },
        "status_vocabularies": {"observed": {"unit": ["ACCEPTED", "BLOCKED"], "run": ["IN_PROGRESS", "PARTIAL", "INTERRUPTED", "BLOCKED", "COMPLETE"], "plan": ["draft", "qa", "approved", "blocked", "superseded"]}, "target": {"unit": ["ACCEPTED", "BLOCKED", "SYSTEM_FAILURE"], "run": ["IN_PROGRESS", "PARTIAL", "INTERRUPTED", "BLOCKED", "COMPLETE", "SYSTEM_FAILURE"], "plan": ["PLAN_APPROVED", "PAUSED_PREREQUISITE", "INTERRUPTED", "SYSTEM_FAILURE"]}},
        "status_migration": {"owner": "P4", "preserve_observed": True, "added_status": "SYSTEM_FAILURE", "reason_schema": "schemas/failure-reason.yaml", "checkpoint_semantics": "preserve_last_valid_fail_closed"},
    }
    baseline_validator = Draft202012Validator(json.loads(BASELINE_SCHEMA_PATH.read_text()))
    if not baseline_validator.is_valid(baseline):
        raise PlanError("valid baseline fixture failed")
    baseline_mutations = []
    claude_credits = copy.deepcopy(baseline); claude_credits["capability_facts"]["claude_code"]["separately_billed_credits_enabled"] = True; baseline_mutations.append(("claude-paid-credits", claude_credits))
    codex_credits = copy.deepcopy(baseline); codex_credits["capability_facts"]["codex_cli"]["chatgpt_credits_enabled"] = True; baseline_mutations.append(("codex-paid-credits", codex_credits))
    paid_override = copy.deepcopy(baseline); paid_override["capability_facts"]["provider_overrides"]["OPENAI_API_KEY"] = True; baseline_mutations.append(("paid-provider-override", paid_override))
    usage_seat = copy.deepcopy(baseline); usage_seat["capability_facts"]["claude_code"]["plan_subtype"] = "ENTERPRISE_USAGE_BASED"; baseline_mutations.append(("usage-based-seat", usage_seat))
    sandbox_write_only = copy.deepcopy(baseline); sandbox_write_only["capability_facts"]["outer_sandbox"]["resolved_roots"][1]["read"] = False; baseline_mutations.append(("sandbox-write-without-read", sandbox_write_only))
    for name, candidate in baseline_mutations:
        if baseline_validator.is_valid(candidate):
            raise PlanError(f"baseline contradiction unexpectedly passed: {name}")

    # Continuations are single-run, same-node, next-attempt capabilities bound
    # byte-for-byte by an independently authorized resume command.
    current_resume = {
        "run_id": "run-0001", "node_id": "P2", "attempt": 1,
        "source_event_hash": sha, "checkpoint_hash": sha, "graph_digest": sha,
        "prompt_digest": sha, "policy_digest": sha, "schema_digest": sha,
        "route_digest": sha, "execution_contract_digest": sha,
    }
    continuation = {
        "version": "1.0", "continuation_id": sha, "run_id": "run-0001",
        "suspended_node_id": "P2", "allowed_resume_node_id": "P2",
        "source_event_hash": sha, "checkpoint_hash": sha, "graph_digest": sha,
        "prompt_digest": sha, "policy_digest": sha, "schema_digest": sha,
        "route_digest": sha, "execution_contract_digest": sha, "next_attempt": 2,
        "reason_class": "AUTHENTICATION_MISSING", "consumed": False,
    }
    command = {
        "version": "1.0", "command_id": sha, "run_id": "run-0001",
        "continuation_id": sha, "continuation_hash": _digest(continuation),
        "resume_node_id": "P2", "next_attempt": 2,
        "operator_authorization_hash": sha,
    }
    validate_resume(continuation, command, current_resume)
    resume_mutations = []
    cross_run = copy.deepcopy(command); cross_run["run_id"] = "run-other"; resume_mutations.append(("cross-run-resume", continuation, cross_run))
    cross_phase = copy.deepcopy(command); cross_phase["resume_node_id"] = "P6"; resume_mutations.append(("cross-phase-resume", continuation, cross_phase))
    stale_source = copy.deepcopy(continuation); stale_source["source_event_hash"] = "1" * 64; stale_command = copy.deepcopy(command); stale_command["continuation_hash"] = _digest(stale_source); resume_mutations.append(("stale-source-resume", stale_source, stale_command))
    unbound = copy.deepcopy(command); unbound["continuation_hash"] = "1" * 64; resume_mutations.append(("unbound-resume", continuation, unbound))
    for name, candidate_continuation, candidate_command in resume_mutations:
        try:
            validate_resume(candidate_continuation, candidate_command, current_resume)
        except PlanError:
            continue
        raise PlanError(f"resume mutation unexpectedly passed: {name}")

    # The coverage helper enforces the non-vacuous aggregate invariants that
    # JSON Schema cannot express across array lengths and unique identifiers.
    record = {"id": "R1", "owner": "QA", "source_locator": "repo:path:1", "source_hash": sha, "evidence_requirement": "independent evidence"}
    mutation_kinds = [
        "MISSING_SYSTEM_EDGE", "MISSING_REPAIR_EDGE", "MISSING_EXHAUSTION_EDGE",
        "MISSING_PAUSE_EDGE", "MISSING_RESUME_EDGE", "GUARD_INVERSION",
        "GUARD_DUPLICATION", "DEPENDENCY_MISMATCH", "CONTEXT_LEAK",
        "DUPLICATE_OWNER", "TERMINAL_KIND", "REDUCER_ORDER", "CRASH_BEFORE",
        "CRASH_AFTER", "EVIDENCE_FREE_PASS", "CROSS_RUN_RESUME",
        "UNKNOWN_CONTRACT", "FUTURE_PRODUCER", "IDEMPOTENCY_COLLISION",
    ]
    denominator = {
        "version": "1.0", "source_digest": sha,
        "nodes": [record], "edges": [{**record, "id": "E1"}],
        "guards": [{**record, "id": "G1"}], "side_effect_boundaries": [{**record, "id": "S1"}],
        "mutations": [{**record, "id": f"M{index}", "kind": kind} for index, kind in enumerate(mutation_kinds, 1)],
        "historical_findings": [{**record, "id": "H1"}], "historical_anomalies": [],
        "aggregates": {"node_count": 1, "edge_count": 1, "guard_count": 1, "side_effect_boundary_count": 1, "mutation_count": 19, "historical_finding_count": 1, "historical_anomaly_count": 0},
        "process_thresholds": {"minimum_live_model_calls": 2, "minimum_cold_resume_processes": 2, "minimum_independent_reviewers": 3, "maximum_repair_attempts": 2, "required_unit_count": 3},
    }
    denominator_schema = json.loads((ROOT / "contracts" / "coverage_denominator.schema.v1.json").read_text())
    if list(Draft202012Validator(denominator_schema).iter_errors(denominator)):
        raise PlanError("valid denominator fixture failed its schema")
    validate_denominator(denominator)
    bad_count = copy.deepcopy(denominator); bad_count["aggregates"]["mutation_count"] = 20
    duplicate_id = copy.deepcopy(denominator); duplicate_id["mutations"][1]["id"] = duplicate_id["mutations"][0]["id"]
    for name, candidate in (("aggregate-mismatch", bad_count), ("duplicate-denominator-id", duplicate_id)):
        try:
            validate_denominator(candidate)
        except PlanError:
            continue
        raise PlanError(f"denominator mutation unexpectedly passed: {name}")

    current_ledger = {"run_id": "run-0001", "node_id": "P6", "phase_attempt": 1, "execution_contract_digest": sha}
    phase_key = f"{sha}:P6:1"
    ledger = {
        "version": "1.0", **current_ledger, "phase_key": phase_key,
        "required_subtask_ids": ["release-tests", "evidence-commit"],
        "subtasks": [
            {"subtask_id": "release-tests", "idempotency_key": f"{phase_key}:release-tests:{sha}", "input_digest": sha, "output_hashes": {"report": sha}, "state": "COMMITTED"},
            {"subtask_id": "evidence-commit", "idempotency_key": f"{phase_key}:evidence-commit:{sha}", "input_digest": sha, "output_hashes": {"bundle": sha}, "state": "COMMITTED"},
        ],
        "complete": True,
    }
    validate_phase_ledger(ledger, current_ledger)
    ledger_mutations = []
    wrong_phase_key = copy.deepcopy(ledger); wrong_phase_key["phase_key"] = f"{sha}:P5:1"; ledger_mutations.append(("wrong-phase-key", wrong_phase_key))
    duplicate_subtask = copy.deepcopy(ledger); duplicate_subtask["subtasks"][1]["subtask_id"] = "release-tests"; duplicate_subtask["subtasks"][1]["idempotency_key"] = f"{phase_key}:release-tests:{sha}"; ledger_mutations.append(("duplicate-subtask", duplicate_subtask))
    false_complete = copy.deepcopy(ledger); false_complete["subtasks"][0]["state"] = "INCOMPLETE"; ledger_mutations.append(("false-complete-ledger", false_complete))
    collided_key = copy.deepcopy(ledger); collided_key["subtasks"][1]["idempotency_key"] = collided_key["subtasks"][0]["idempotency_key"]; ledger_mutations.append(("collided-subtask-key", collided_key))
    for name, candidate in ledger_mutations:
        try:
            validate_phase_ledger(candidate, current_ledger)
        except PlanError:
            continue
        raise PlanError(f"phase-ledger mutation unexpectedly passed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    plan, schema = load()
    validate(plan, schema)
    if args.self_test:
        self_test(plan, schema)
    print("plan21_bootstrap=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
