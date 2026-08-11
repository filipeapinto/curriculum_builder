from __future__ import annotations

import importlib.util
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
    packet = scheduler._prompt_packet("N00_BASELINE_FREEZE")
    assert "BEGIN NODE PROMPT (verbatim)" in packet
    assert "Do not read historical result Markdown" in packet
    assert "production curriculum factory MUST continue to use LangGraph" in packet
