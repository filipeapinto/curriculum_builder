"""N60 adversarial regression: the final campaign before any live curriculum
transmission (spec section 17.2; Run 27 prompt N60_adversarial_regression.v1).

Most of the mandatory adversarial matrix (spec 17.2's table) is already proven
production-level by `test_plan26_adversarial.py`'s 24 named rows, re-run
unmodified as part of this node's own required full-tree denominator (see
`plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N60_ADVERSARIAL_REGRESSION.result.v1.json`
for the exact commands/counts). This file adds only the cases that table does
not already name explicitly, closed against real production code -- nothing
here substitutes a mock for the property it claims to prove.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.langgraph_factory import transport as tp

requires_sandbox = pytest.mark.skipif(
    tp.sandbox_mechanism() == tp.SANDBOX_UNAVAILABLE,
    reason="host provides no process sandbox; transport fails closed instead of running",
)


# --------------------------------------------------------- output-schema escape


def test_output_schema_validation_ignores_a_tampered_workspace_copy(tmp_path: Path):
    """A worker process fully controls its own workspace after launch. If result
    validation trusted the workspace's own staged `output.schema.json`, a
    compromised or misbehaving worker could rewrite that file to something
    permissive and smuggle a non-conforming result past D03. `load_output_schema`
    only ever reads the package-owned schema (`resolve_schema_path`/`SCHEMA_DIR`);
    this proves that binding holds even when the staged copy is corrupted.
    """
    output_root = tmp_path / "output"
    output_root.mkdir()
    route = tp.resolve_route("M03_WRITE_UNIT_CONTENT")
    workspace = tp.stage_workspace(
        output_root=output_root, episode_id="ep-1", activation_id="act-1", route=route,
        projection={}, authorization_receipt={"receipt_id": "r"})
    try:
        (workspace.path / "output.schema.json").write_text("{}", encoding="utf-8")
        (workspace.path / "result.json").write_text(
            json.dumps({"anything": "goes", "no": "required fields here"}), encoding="utf-8")
        real_schema = tp.load_output_schema(route)
        assert real_schema != {}
        with pytest.raises(tp.ResultParseError) as error:
            tp.load_candidate(route, workspace=workspace.path, stdout="", schema=real_schema)
        assert error.value.failure_class == "schema_invalid_result"
    finally:
        workspace.destroy()


# ------------------------------------------------------------- identity overclaim


def test_a_rollout_bound_to_the_right_thread_id_but_the_wrong_model_is_still_rejected(
    tmp_path: Path,
):
    """N30V7-F05's repair (Run 27 N20 attempt-2) proved the rollout-binding
    mechanism itself is sound in isolation (`test_plan26_transport.py`'s
    `test_codex_identity_is_read_from_the_rollout_file_bound_by_thread_id` family).
    This closes the adjacent, integration-level overclaim case: a rollout file
    that *is* correctly bound to this exact invocation's `thread_id` (so identity
    observation succeeds) but names a different, unauthorized model than the
    frozen route decided. The full `observe_identity` -> `assert_identity_matches`
    pipeline, not `observe_codex_identity` alone, must still reject it.
    """
    thread_id = "01a00096-overclaim-thread"
    sessions_root = tmp_path / "sessions" / "2026" / "08" / "14"
    sessions_root.mkdir(parents=True)
    rollout = sessions_root / f"rollout-2026-08-14T00-00-00-{thread_id}.jsonl"
    rollout.write_text("\n".join([
        json.dumps({"type": "session_meta",
                   "payload": {"session_id": thread_id, "model_provider": "openai"}}),
        json.dumps({"type": "turn_context", "payload": {"model": "gpt-5-mini"}}),
        json.dumps({"type": "turn.completed", "usage": {}}),
    ]) + "\n", encoding="utf-8")
    stdout = json.dumps({"type": "thread.started", "thread_id": thread_id}) + "\n"

    route = tp.resolve_route("M05_REVIEW_ACTUAL_UNIT")  # decided model: gpt-5.6-sol
    observed = tp.observe_identity(route, stdout=stdout, codex_home=tmp_path)
    assert observed.model == "gpt-5-mini"
    with pytest.raises(tp.IdentityMismatch):
        tp.assert_identity_matches(route, observed)


# ------------------------------------------------ unreachable production topology


def test_the_final_repaired_production_graph_registers_exactly_its_full_binding_inventory(
    tmp_path: Path,
):
    """N60's own re-verification against the fully repaired system (post
    N20-N50), using the real production compile entry point -- N40 proves no
    undeclared/missing/unreachable registered node once per its own scope
    (`test_plan26_topology.py`); this proves the same undeclared/missing-node
    property again, unmodified, directly against the compiled object, as part
    of N60's independent final campaign rather than inherited by assertion. A
    node present in `compiled.nodes` but absent from `full_binding_inventory()`
    (or vice versa) is exactly the PM-11/PM-12 shape: a body that exists but
    was never really wired into the one production graph, or a stale
    registration nothing backs.
    """
    from runtime.langgraph_factory import graph as G

    output_root = tmp_path / "graph_output"
    output_root.mkdir()
    compiled = G.build_curriculum_factory_graph(
        engine_root=Path(__file__).resolve().parents[2], output_root=output_root)
    compiled_node_ids = {name for name in compiled.nodes if name not in ("__start__", "__end__")}
    expected = set(G.full_binding_inventory())
    assert compiled_node_ids == expected, (
        f"missing={sorted(expected - compiled_node_ids)} "
        f"undeclared={sorted(compiled_node_ids - expected)}"
    )
