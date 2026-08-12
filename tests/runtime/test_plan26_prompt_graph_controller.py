from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
CONTROLLER_PATH = ROOT / "plans/26_langgraph_curriculum_factory/prompt_graph_controller.py"
SPEC = importlib.util.spec_from_file_location("plan26_prompt_graph_controller", CONTROLLER_PATH)
assert SPEC is not None and SPEC.loader is not None
controller_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = controller_module
SPEC.loader.exec_module(controller_module)


def manifest():
    return controller_module.Manifest.load(
        ROOT / "plans/26_langgraph_curriculum_factory/implementation.graph.v3.yaml"
    )


def test_v3_manifest_is_valid_and_acyclic():
    graph = manifest()
    order = graph.topological_order()
    assert order[0] == "N00_BASELINE_FREEZE"
    assert order[-1] == "N90_FINAL_AUDIT"
    assert set(order) == set(graph.nodes)


def test_controller_is_explicitly_not_the_production_runtime():
    source = CONTROLLER_PATH.read_text(encoding="utf-8")
    assert "from langgraph" not in source
    assert "import langgraph" not in source
    assert manifest().data["execution"]["claude_command"][3] == "sonnet"


def test_full_suite_is_reserved_for_n50():
    graph = manifest()
    full_commands = {
        node_id: command
        for node_id, node in graph.nodes.items()
        for command in node["verification"]
        if command[-1:] == ["tests/runtime"]
    }
    assert full_commands == {
        "N50_ADVERSARIAL_REGRESSION": ["{python}", "-m", "pytest", "-q", "tests/runtime"]
    }
    assert graph.nodes["N90_FINAL_AUDIT"]["test_lane"] == "audit"


def test_join_nodes_have_integration_verification():
    graph = manifest()
    for node_id in ("N20_GRAPH_COMPILER", "N30_UNIT_GRAPH", "N32_WORKBOOK_TERMINALS", "N40_CLI_CUTOVER"):
        assert graph.nodes[node_id]["test_lane"] == "join"
        assert graph.nodes[node_id]["verification"]


def test_initial_frontier_and_disjoint_selection_are_deterministic(tmp_path, monkeypatch):
    graph = manifest()
    monkeypatch.setitem(graph.data["execution"], "state_dir", str(tmp_path.relative_to(ROOT)) if tmp_path.is_relative_to(ROOT) else str(tmp_path))
    scheduler = controller_module.Controller(graph)
    state = scheduler.status()
    assert state["ready"] == ["N00_BASELINE_FREEZE"]
    assert state["selected"] == ["N00_BASELINE_FREEZE"]


def test_concurrent_fanout_write_sets_are_disjoint():
    graph = manifest()
    fanout = ["N10_DEPENDENCY_API", "N11_STATE_REDUCERS", "N12_EVIDENCE_ARTIFACTS", "N13_TRANSPORT_AUTH"]
    for index, left_id in enumerate(fanout):
        for right_id in fanout[index + 1 :]:
            assert not any(
                controller_module.paths_overlap(left, right)
                for left in graph.nodes[left_id]["writes"]
                for right in graph.nodes[right_id]["writes"]
            )


def test_prompt_packet_uses_compact_receipts_not_historical_markdown(tmp_path, monkeypatch):
    graph = manifest()
    monkeypatch.setitem(graph.data["execution"], "state_dir", str(tmp_path))
    scheduler = controller_module.Controller(graph)
    packet = scheduler._prompt_packet("N00_BASELINE_FREEZE", "/resolved/bin/python")
    assert "BEGIN NODE PROMPT (verbatim)" in packet
    assert "Do not read historical result Markdown" in packet
    assert "production curriculum factory MUST continue to use LangGraph" in packet


def test_prompt_packet_mandates_the_resolved_interpreter_for_pytest():
    graph = manifest()
    scheduler = controller_module.Controller(graph)
    packet = scheduler._prompt_packet("N00_BASELINE_FREEZE", "/resolved/bin/python")
    assert "Run every pytest command as /resolved/bin/python -m pytest" in packet
    assert "never use python3, python, or plain pytest" in packet


def test_placeholder_expansion_replaces_pattern_embedded_inside_a_larger_argument():
    expanded = controller_module.expand_placeholders(
        ["claude", "--allowedTools", "Read Edit Bash({python} -m pytest *)", "{python}"],
        "/resolved/bin/python",
    )
    assert expanded == [
        "claude",
        "--allowedTools",
        "Read Edit Bash(/resolved/bin/python -m pytest *)",
        "/resolved/bin/python",
    ]


def test_claude_command_has_no_unrestricted_permission_flag_and_exact_bash_scope():
    graph = manifest()
    scheduler = controller_module.Controller(graph)
    resolved_python = scheduler.python_executable()
    command = controller_module.expand_placeholders(
        graph.data["execution"]["claude_command"], resolved_python
    )
    joined = " ".join(command)
    assert "--dangerously-skip-permissions" not in joined
    assert "--allow-dangerously-skip-permissions" not in joined
    assert "bypassPermissions" not in joined
    assert "Bash(*)" not in joined
    assert "--permission-mode" in command
    assert command[command.index("--permission-mode") + 1] == "acceptEdits"
    allowed_tools = command[command.index("--allowedTools") + 1]
    assert allowed_tools == f"Read Edit Write Glob Grep Bash({resolved_python} -m pytest *)"


def test_resolved_interpreter_is_identical_across_command_prompt_and_verification():
    graph = manifest()
    scheduler = controller_module.Controller(graph)
    resolved_python = scheduler.python_executable()
    command = controller_module.expand_placeholders(
        graph.data["execution"]["claude_command"], resolved_python
    )
    packet = scheduler._prompt_packet("N00_BASELINE_FREEZE", resolved_python)
    verification_argv = controller_module.expand_placeholders(
        graph.nodes["N30_UNIT_GRAPH"]["verification"][0], resolved_python
    )
    assert resolved_python in " ".join(command)
    assert resolved_python in packet
    assert verification_argv[0] == resolved_python


def test_mechanical_revalidation_admits_a_receipt_after_a_harness_only_change():
    graph = manifest()
    scheduler = controller_module.Controller(graph)
    real_receipt = scheduler.receipts.load("N00_BASELINE_FREEZE")
    assert real_receipt is not None
    harness_only_change = dict(real_receipt, input_fingerprint="0" * 64)
    assert scheduler.receipts.mechanically_revalidate("N00_BASELINE_FREEZE", harness_only_change)


def test_mechanical_revalidation_rejects_a_receipt_with_a_stale_output_hash():
    graph = manifest()
    scheduler = controller_module.Controller(graph)
    real_receipt = scheduler.receipts.load("N00_BASELINE_FREEZE")
    assert real_receipt is not None
    tampered_outputs = dict(real_receipt["outputs"])
    a_key = next(iter(tampered_outputs))
    tampered_outputs[a_key] = "1" * 64
    tampered = dict(real_receipt, input_fingerprint="0" * 64, outputs=tampered_outputs)
    assert not scheduler.receipts.mechanically_revalidate("N00_BASELINE_FREEZE", tampered)


def test_mechanical_revalidation_rejects_a_receipt_with_a_recorded_nonzero_exit():
    graph = manifest()
    scheduler = controller_module.Controller(graph)
    real_receipt = scheduler.receipts.load("N00_BASELINE_FREEZE")
    assert real_receipt is not None
    tampered_commands = [dict(command, exit_code=1) for command in real_receipt["commands"]]
    tampered = dict(real_receipt, input_fingerprint="0" * 64, commands=tampered_commands)
    assert not scheduler.receipts.mechanically_revalidate("N00_BASELINE_FREEZE", tampered)


def test_passed_nodes_remain_admissible_and_n31_is_the_sole_frontier_after_harness_change():
    graph = manifest()
    scheduler = controller_module.Controller(graph)
    state = scheduler.status()
    passed = [
        "N00_BASELINE_FREEZE",
        "N10_DEPENDENCY_API",
        "N11_STATE_REDUCERS",
        "N12_EVIDENCE_ARTIFACTS",
        "N13_TRANSPORT_AUTH",
        "N20_GRAPH_COMPILER",
        "N21_PERSISTENCE_RESUME",
        "N22_DETERMINISTIC_NODES",
        "N23_MODEL_NODES",
        "N30_UNIT_GRAPH",
    ]
    for node_id in passed:
        assert state["statuses"][node_id] == "PASSED"
    assert state["statuses"]["N31_REPAIR_ACCEPTANCE"] == "READY"
    assert state["ready"] == ["N31_REPAIR_ACCEPTANCE"]
    assert state["selected"] == ["N31_REPAIR_ACCEPTANCE"]


def test_preflight_evaluation_passes_only_on_clean_run_with_marker_and_no_denials():
    evaluate = controller_module.Controller._evaluate_preflight
    envelope = {"result": "PREFLIGHT_OK: pytest 9.0.3", "permission_denials": []}
    passed, reason = evaluate(0, 0, [], envelope, "PREFLIGHT_OK: pytest 9.0.3")
    assert passed is True
    assert reason is None


def test_preflight_evaluation_fails_closed_on_permission_denial():
    evaluate = controller_module.Controller._evaluate_preflight
    envelope = {"result": "PREFLIGHT_OK: pytest 9.0.3", "permission_denials": [{"tool_name": "Bash"}]}
    passed, reason = evaluate(0, 0, [], envelope, "PREFLIGHT_OK: pytest 9.0.3")
    assert passed is False
    assert reason == "bash_permission_denied"


def test_preflight_evaluation_fails_closed_when_success_marker_is_missing_or_mismatched():
    evaluate = controller_module.Controller._evaluate_preflight
    envelope = {"result": "PREFLIGHT_OK: pytest 1.0.0", "permission_denials": []}
    passed, reason = evaluate(0, 0, [], envelope, "PREFLIGHT_OK: pytest 9.0.3")
    assert passed is False
    assert reason == "missing_or_mismatched_success_marker"


def test_preflight_evaluation_fails_closed_when_isolated_workspace_was_modified():
    evaluate = controller_module.Controller._evaluate_preflight
    envelope = {"result": "PREFLIGHT_OK: pytest 9.0.3", "permission_denials": []}
    passed, reason = evaluate(0, 0, ["some/file.py"], envelope, "PREFLIGHT_OK: pytest 9.0.3")
    assert passed is False
    assert reason == "isolated_workspace_modified"


def test_preflight_evaluation_fails_closed_on_nested_claude_nonzero_exit():
    evaluate = controller_module.Controller._evaluate_preflight
    passed, reason = evaluate(0, 1, [], None, "PREFLIGHT_OK: pytest 9.0.3")
    assert passed is False
    assert reason == "nested_claude_exit_nonzero"


def test_preflight_never_writes_a_node_receipt():
    source = inspect.getsource(controller_module.Controller.preflight)
    assert "self.receipts.save" not in source
    assert "receipts.save(" not in source
