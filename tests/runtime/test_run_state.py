"""Section 7 of plans/runtime_integrity_remediation — the run-level lifecycle record.

Covers issue 007: the run root says what it actually did. A run with 4 of 35 units done
reports 31 remaining and never COMPLETE; COMPLETE is reachable only through workbook
assembly with exact coverage; and resuming refuses a moved input or an accepted unit.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from runtime import run_state, workbook
from runtime.run_state import RunStateError
from runtime.workbook import WorkbookError
from tests.runtime import unit_fixture

ENGINE = unit_fixture.ENGINE
SCHEMA = json.loads((ENGINE / "schemas/run_lifecycle.schema.v1.json").read_text())
MANIFEST_IDS = [f"L{index:02d}" for index in range(1, 36)]


def _run_root(tmp_path, completed=("L01", "L02", "L03", "L04"),
              terminal_state="ACCEPTED_PENDING_REVIEW"):
    """The real arduino_kit_run_v2 shape: a 35-unit manifest with four units attempted."""
    root = tmp_path / "run"
    (root / "results").mkdir(parents=True)
    (root / "results/gate_1_static_preflight.json").write_text(
        json.dumps({"unit_ids": MANIFEST_IDS, "unit_count": len(MANIFEST_IDS)}))
    (root / "meta_execution_state.json").write_text(json.dumps(
        {"authorized_roots": {}, "manifest_sha256": "a" * 64, "prompt_sha256": "b" * 64}))
    for unit_id in completed:
        (root / unit_id).mkdir()
        (root / unit_id / "acceptance.json").write_text(
            json.dumps({"terminal_state": terminal_state, "unit_id": unit_id}))
    return root


def test_a_partly_done_run_reports_what_is_left(tmp_path):
    root = _run_root(tmp_path)
    state = run_state.record_unit_transition(root, "L04", "ACCEPTED_PENDING_REVIEW")
    jsonschema.Draft202012Validator(SCHEMA).validate(state)

    assert state["run_status"] not in {"COMPLETE", "ACCEPTED"}
    assert state["run_status"] == "IN_PROGRESS"
    assert state["manifest_unit_count"] == 35
    assert len(state["completed_unit_ids"]) == 4
    assert len(state["remaining_unit_ids"]) == 31
    assert state["next_unit"] == "L05"
    assert state["workbook_assembled"] is False
    assert (root / "run_state.json").is_file()


def test_a_blocked_unit_is_not_counted_as_completed(tmp_path):
    root = _run_root(tmp_path, completed=("L01", "L02"))
    (root / "L03").mkdir()
    (root / "L03/acceptance.json").write_text(json.dumps({"terminal_state": "BLOCKED"}))
    state = run_state.record_unit_transition(root, "L03", "BLOCKED")
    assert state["blocked_unit_ids"] == ["L03"]
    assert "L03" not in state["completed_unit_ids"]
    assert "L03" not in state["remaining_unit_ids"], "an attempted unit is not unattempted"
    assert state["next_unit"] == "L04"


def test_close_run_states_a_reason_rather_than_inferring_a_stop(tmp_path):
    root = _run_root(tmp_path)
    run_state.record_unit_transition(root, "L04", "ACCEPTED_PENDING_REVIEW")
    reason = ("Four of thirty-five units were attempted; L05 through L35 were never generated "
              "under this plan's scope.")
    state = run_state.close_run(root, reason)
    jsonschema.Draft202012Validator(SCHEMA).validate(state)
    assert state["run_status"] == "PARTIAL"
    assert state["terminal_reason"] == reason
    assert state["closed_at"]


def test_close_run_refuses_an_empty_reason_and_refuses_complete(tmp_path):
    root = _run_root(tmp_path)
    run_state.record_unit_transition(root, "L04", "ACCEPTED_PENDING_REVIEW")
    with pytest.raises(RunStateError):
        run_state.close_run(root, "stopped")
    with pytest.raises(RunStateError):
        run_state.close_run(root, "a" * 40, status="COMPLETE")


def test_the_schema_refuses_a_stated_stop_with_no_reason():
    state = {"run_status": "PARTIAL", "manifest_unit_count": 1, "manifest_unit_ids": ["L01"],
             "completed_unit_ids": [], "blocked_unit_ids": [], "failed_unit_ids": [],
             "remaining_unit_ids": ["L01"], "workbook_assembled": False, "updated_at": "now"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(SCHEMA).validate(state)


def test_the_schema_refuses_complete_without_coverage_or_a_workbook():
    state = {"run_status": "COMPLETE", "manifest_unit_count": 2, "manifest_unit_ids": ["L01", "L02"],
             "completed_unit_ids": ["L01"], "blocked_unit_ids": [], "failed_unit_ids": [],
             "remaining_unit_ids": ["L02"], "workbook_assembled": False, "updated_at": "now"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(SCHEMA).validate(state)


def test_assemble_refuses_complete_with_incomplete_coverage(tmp_path):
    root = _run_root(tmp_path)
    run_state.record_unit_transition(root, "L04", "ACCEPTED_PENDING_REVIEW")
    with pytest.raises(WorkbookError) as raised:
        workbook.assemble(root)
    assert "coverage is 4 of 35" in str(raised.value)
    assert json.loads((root / "run_state.json").read_text())["run_status"] != "COMPLETE"
    coverage = json.loads((root / "workbook/coverage.json").read_text())
    assert coverage == {"expected": 35, "included": 4,
                        "expected_unit_ids": MANIFEST_IDS,
                        "included_unit_ids": ["L01", "L02", "L03", "L04"]}


def test_assemble_refuses_when_a_completed_unit_has_no_shipped_pdf(tmp_path):
    root = tmp_path / "run"
    (root / "results").mkdir(parents=True)
    (root / "results/gate_1_static_preflight.json").write_text(
        json.dumps({"unit_ids": ["L01"], "unit_count": 1}))
    (root / "L01").mkdir()
    (root / "L01/acceptance.json").write_text(json.dumps({"terminal_state": "ACCEPTED"}))
    run_state.record_unit_transition(root, "L01", "ACCEPTED")
    with pytest.raises(WorkbookError) as raised:
        workbook.assemble(root)
    assert "without a shipped PDF" in str(raised.value)


def test_assert_resumable_rejects_a_hash_mismatch(tmp_path):
    root = _run_root(tmp_path)
    run_state.record_unit_transition(root, "L04", "ACCEPTED_PENDING_REVIEW")
    with pytest.raises(RunStateError) as raised:
        run_state.assert_resumable(root, "c" * 64, "b" * 64, "L05")
    assert "manifest hash mismatch" in str(raised.value)
    with pytest.raises(RunStateError) as raised:
        run_state.assert_resumable(root, "a" * 64, "d" * 64, "L05")
    assert "prompt hash mismatch" in str(raised.value)


def test_assert_resumable_refuses_to_overwrite_an_accepted_unit(tmp_path):
    for state in ("ACCEPTED", "ACCEPTED_PENDING_REVIEW"):
        root = _run_root(tmp_path / state, terminal_state=state)
        run_state.record_unit_transition(root, "L04", state)
        with pytest.raises(RunStateError) as raised:
            run_state.assert_resumable(root, "a" * 64, "b" * 64, "L02")
        assert "refusing to overwrite an accepted unit" in str(raised.value)


def test_assert_resumable_refuses_a_unit_out_of_order(tmp_path):
    root = _run_root(tmp_path)
    run_state.record_unit_transition(root, "L04", "ACCEPTED_PENDING_REVIEW")
    with pytest.raises(RunStateError) as raised:
        run_state.assert_resumable(root, "a" * 64, "b" * 64, "L09")
    assert "out of order" in str(raised.value)
    assert run_state.assert_resumable(root, "a" * 64, "b" * 64, "L05")


def test_assert_resumable_refuses_a_run_with_no_lifecycle_record(tmp_path):
    root = _run_root(tmp_path)
    with pytest.raises(RunStateError) as raised:
        run_state.assert_resumable(root, "a" * 64, "b" * 64, "L05")
    assert "no run_state.json" in str(raised.value)


def test_finalize_records_the_transition_without_a_separate_call(tmp_path):
    """Section 3's wiring: the run record updates as part of the production path."""
    from runtime.session_bridge import finalize
    lab = unit_fixture.lab_from_run("L02")
    run_root, unit_root = unit_fixture.build_run(
        tmp_path, unit_id="L02", lab=lab, manifest_unit_ids=["L01", "L02", "L03"])
    summary = finalize(ENGINE, unit_root, curriculum=unit_fixture.CURRICULUM)
    state = json.loads((run_root / "run_state.json").read_text())
    jsonschema.Draft202012Validator(SCHEMA).validate(state)
    assert state["unit_states"]["L02"] == summary["terminal_state"]
    assert state["current_unit"] == "L02"
    assert state["remaining_unit_ids"] == ["L01", "L03"]
