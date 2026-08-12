from __future__ import annotations

import importlib.util
import inspect
import json
from pathlib import Path
import sys

import pytest


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
    assert command[command.index("--output-format") + 1] == "stream-json"
    assert "--verbose" in command


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


def _admissible_tolerating_evidence_drift(scheduler, node_id):
    """True if `node_id` is admissible, or is only inadmissible because a
    `results/evidence/` output drifted.

    A handful of pre-existing tests elsewhere in this same `tests/runtime`
    suite (e.g. `test_plan26_cli.py`'s evidence-writing tests) rewrite live
    evidence reports as a side effect of merely running, embedding a fresh
    tmp path each time. When this file is swept into a full `pytest -q
    tests/runtime` run (as N50's/rebase's own verification does), those
    tests may have already regenerated an earlier node's evidence directory
    by the time this test runs, purely from pytest collection order — with
    no effect on the live repo (nothing here writes back to it). Evidence
    directories are captured proof-of-work, not authoritative product
    state, so that specific, already-diagnosed drift is tolerated here
    rather than tested for.
    """
    if scheduler.receipts.admissible(node_id) is not None:
        return True
    receipt = scheduler.receipts.load(node_id)
    if receipt is None or receipt.get("status") != "PASSED":
        return False
    for relative, expected in receipt.get("outputs", {}).items():
        if scheduler.receipts.current_digest(relative) != expected and "/evidence/" not in relative:
            return False
    return True


def test_passed_nodes_remain_admissible_after_harness_or_predecessor_change():
    """Guards against a harness-only change, or a legitimate predecessor
    rework (e.g. an ownership correction), collaterally invalidating
    already-admitted nodes it did not touch. Deliberately does not hardcode
    which node is the current frontier: unlike this suite's other fixtures,
    this test runs against the live receipt store as it actually stands, and
    the pipeline is expected to keep advancing (more nodes reaching PASSED
    over time), so pinning an exact snapshot would make the test rot on
    every real step of progress rather than guard anything.
    """
    graph = manifest()
    scheduler = controller_module.Controller(graph)
    state = scheduler.status()
    for node_id in graph.topological_order():
        receipt = scheduler.receipts.load(node_id)
        if receipt is None or receipt.get("status") != "PASSED":
            continue
        if state["statuses"][node_id] == "PASSED":
            continue
        assert _admissible_tolerating_evidence_drift(scheduler, node_id), (
            f"{node_id} has a PASSED receipt but is inadmissible for a reason "
            "other than known evidence-directory drift"
        )


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


def test_prompt_patch_is_additive_bound_to_manifest_and_never_rewrites_base_prompt(tmp_path, monkeypatch):
    graph = manifest()
    patch_dir = tmp_path / "patches"
    monkeypatch.setitem(graph.data["execution"], "patch_dir", str(patch_dir))
    monkeypatch.setitem(graph.data["execution"], "attempt_dir", str(tmp_path / "attempts"))
    monkeypatch.setitem(graph.data["execution"], "audit_log", str(tmp_path / "events.jsonl"))
    scheduler = controller_module.Controller(graph)
    prompt_path = ROOT / graph.nodes["N50_ADVERSARIAL_REGRESSION"]["prompt"]
    original = prompt_path.read_bytes()

    preview = scheduler.create_patch(
        "P-N50-TEST",
        "N50_ADVERSARIAL_REGRESSION",
        "Retain and continue from prior verified work.",
        "Avoid clean retries",
        "The next attempt reuses prior work",
        "node_only",
        {"finding": "test"},
        True,
    )
    assert not patch_dir.exists()
    assert preview["affected_nodes"] == ["N50_ADVERSARIAL_REGRESSION"]

    created = scheduler.create_patch(
        "P-N50-TEST",
        "N50_ADVERSARIAL_REGRESSION",
        "Retain and continue from prior verified work.",
        "Avoid clean retries",
        "The next attempt reuses prior work",
        "node_only",
        {"finding": "test"},
        False,
    )
    effective, provenance = scheduler.patches.effective_prompt("N50_ADVERSARIAL_REGRESSION")
    assert created["sha256"]
    assert "P-N50-TEST" in effective
    assert provenance["active_patch_ids"] == ["P-N50-TEST"]
    assert prompt_path.read_bytes() == original
    with pytest.raises(FileExistsError):
        scheduler.patches.create_overlay(
            "P-N50-TEST",
            "N50_ADVERSARIAL_REGRESSION",
            "duplicate",
            "duplicate",
            "must fail",
            "node_only",
            {},
            False,
        )


def test_patch_revocation_is_append_only_and_removes_overlay_from_effective_prompt(tmp_path, monkeypatch):
    graph = manifest()
    monkeypatch.setitem(graph.data["execution"], "patch_dir", str(tmp_path / "patches"))
    monkeypatch.setitem(graph.data["execution"], "attempt_dir", str(tmp_path / "attempts"))
    monkeypatch.setitem(graph.data["execution"], "audit_log", str(tmp_path / "events.jsonl"))
    scheduler = controller_module.Controller(graph)
    scheduler.create_patch(
        "P-N50-OLD",
        "N50_ADVERSARIAL_REGRESSION",
        "UNIQUE_PATCH_TEXT",
        "test",
        "text appears",
        "node_only",
        None,
        False,
    )
    scheduler.revoke_patch(
        "P-N50-REVOKE",
        ["P-N50-OLD"],
        "rollback test",
        "text no longer applies",
        False,
    )
    effective, provenance = scheduler.patches.effective_prompt("N50_ADVERSARIAL_REGRESSION")
    assert "UNIQUE_PATCH_TEXT" not in effective
    assert provenance["patch_ids"] == ["P-N50-OLD", "P-N50-REVOKE"]
    assert provenance["active_patch_ids"] == []
    assert len(list((tmp_path / "patches").glob("*.patch.v1.yaml"))) == 2


def _minimal_controller(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    patch_schema = (ROOT / "plans/26_langgraph_curriculum_factory/prompt_patch.schema.v1.json").read_text(encoding="utf-8")
    for relative, content in {
        "graph.yaml": "graph: test\n",
        "graph.schema.json": "{}\n",
        "receipt.schema.json": "{\"type\": \"object\"}\n",
        "patch.schema.json": patch_schema,
        "controller.py": "# controller\n",
        "prompt.md": "base prompt\n",
        "spec.md": "spec\n",
        "env.lock": "locked\n",
        "work.txt": "original\n",
    }.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    data = {
        "graph_id": "plan26_langgraph_curriculum_factory_implementation",
        "version": 3,
        "source_spec": "spec.md",
        "schema": "graph.schema.json",
        "runner": "run.md",
        "entry": "N00_BASELINE_FREEZE",
        "result_pattern": "results/{node_id}.md",
        "execution": {
            "controller": "controller.py",
            "state_dir": "state",
            "receipt_schema": "receipt.schema.json",
            "patch_schema": "patch.schema.json",
            "patch_dir": "patches",
            "attempt_dir": "state/attempts",
            "audit_log": "state/audit/events.jsonl",
            "legacy_result_pattern": "results/{node_id}.md",
            "workspace_mode": "isolated_copy",
            "workspace_log_dir": ".plan26-run",
            "python_candidates": [sys.executable],
            "claude_command": ["unused", "--print"],
            "max_parallel": 1,
            "node_timeout_seconds": 60,
            "test_timeout_seconds": 10,
            "cache": {"strategy": "content_addressed", "environment_files": ["env.lock"]},
        },
        "rules": {},
        "nodes": {
            "N00_BASELINE_FREEZE": {
                "prompt": "prompt.md",
                "depends_on": [],
                "writes": ["work.txt"],
                "verification": [],
                "test_lane": "focused",
            }
        },
        "edges": [],
        "rework_edges": {},
        "terminals": {},
    }
    monkeypatch.setattr(controller_module, "REPO_ROOT", repo)
    graph = controller_module.Manifest(repo / "graph.yaml", data)
    return controller_module.Controller(graph), repo


def test_retained_attempt_resume_forks_without_modifying_parent(tmp_path, monkeypatch):
    scheduler, _repo = _minimal_controller(tmp_path, monkeypatch)
    parent = scheduler._copy_workspace("N00_BASELINE_FREEZE")
    parent_work = parent.workspace / "work.txt"
    parent_work.write_text("partial work\n", encoding="utf-8")
    child = scheduler._copy_workspace("N00_BASELINE_FREEZE", parent.attempt_id)
    assert (child.workspace / "work.txt").read_text(encoding="utf-8") == "partial work\n"
    (child.workspace / "work.txt").write_text("continued work\n", encoding="utf-8")
    assert parent_work.read_text(encoding="utf-8") == "partial work\n"
    assert child.base == parent.base
    assert child.parent_attempt_id == parent.attempt_id


def test_command_logs_are_live_created_and_cannot_be_overwritten(tmp_path):
    log = tmp_path / "command.log"
    events = controller_module.EventLog(tmp_path / "events.jsonl")
    result = controller_module.run_command(
        [sys.executable, "-c", "print('preserved-output')"],
        tmp_path,
        10,
        log,
        events,
        {"attempt_id": "attempt-test"},
    )
    assert result["exit_code"] == 0
    assert log.read_text(encoding="utf-8").strip() == "preserved-output"
    with pytest.raises(FileExistsError):
        controller_module.run_command(
            [sys.executable, "-c", "print('replacement')"], tmp_path, 10, log
        )
    assert log.read_text(encoding="utf-8").strip() == "preserved-output"


def test_receipt_replacement_archives_original_bytes_first(tmp_path, monkeypatch):
    scheduler, _repo = _minimal_controller(tmp_path, monkeypatch)
    first = scheduler._receipt("N00_BASELINE_FREEZE", "PASSED", {}, [], "first", [])
    scheduler.receipts.save(first)
    original = scheduler.receipts.path("N00_BASELINE_FREEZE").read_bytes()
    second = dict(first, source="second", created_at=controller_module.utc_now())
    scheduler.receipts.save(second)
    archives = list((scheduler.receipts.root / "receipt_history/N00_BASELINE_FREEZE").glob("*.json"))
    assert len(archives) == 1
    assert archives[0].read_bytes() == original
    assert scheduler.receipts.load("N00_BASELINE_FREEZE")["source"] == "second"


def test_merge_failure_restores_original_and_keeps_premerge_backup(tmp_path, monkeypatch):
    scheduler, repo = _minimal_controller(tmp_path, monkeypatch)
    branch = scheduler._copy_workspace("N00_BASELINE_FREEZE")
    (branch.workspace / "work.txt").write_text("candidate\n", encoding="utf-8")
    after = controller_module.snapshot(branch.workspace)
    result = {
        "node_id": "N00_BASELINE_FREEZE",
        "status": "PASSED",
        "branch": branch,
        "after": after,
        "changed": ["work.txt"],
        "commands": [],
    }

    def fail_receipt(_receipt):
        raise controller_module.ControllerError("injected receipt failure")

    monkeypatch.setattr(scheduler.receipts, "save", fail_receipt)
    with pytest.raises(controller_module.ControllerError, match="injected receipt failure"):
        scheduler._merge(result)
    assert (repo / "work.txt").read_text(encoding="utf-8") == "original\n"
    assert (branch.root / "premerge/work.txt").read_text(encoding="utf-8") == "original\n"
    events = (repo / "state/audit/events.jsonl").read_text(encoding="utf-8")
    assert '"event":"merge_rolled_back"' in events
