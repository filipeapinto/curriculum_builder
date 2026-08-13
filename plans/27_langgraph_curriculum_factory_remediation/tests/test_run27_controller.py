"""Harness invariants for the Run 27 execution controller.

Every test builds a synthetic plan tree in ``tmp_path`` so that the controller is
exercised as a real program against a real repository layout, never as a mock.
The three tests that must observe the actual Plan 27 scaffold say so explicitly.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

TESTS_DIR = Path(__file__).resolve().parent
PLAN_DIR = TESTS_DIR.parent
REPO_ROOT = PLAN_DIR.parents[1]
CONTROLLER_DIR = PLAN_DIR / "controller"
REAL_GRAPH = PLAN_DIR / "implementation.graph.v1.yaml"
FROZEN_RESULT_SCHEMA = PLAN_DIR / "schemas/node_result.schema.v1.json"

if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

import core  # noqa: E402
import run27_controller  # noqa: E402
import scheduler as scheduler_module  # noqa: E402
from core import ControllerError, Graph, sha256_file, tree_digest  # noqa: E402
from scheduler import Scheduler  # noqa: E402


VERIFY_OK = [["python3", "-c", "print('verified')"]]

NODE_WRITES: dict[str, list[str]] = {
    "N00_SPEC_APPROVAL_GATE": [
        "plans/p27/results/N00_SPEC_APPROVAL_GATE.result.v1.json",
        "plans/p27/results/evidence/N00_SPEC_APPROVAL_GATE",
    ],
    "N10_HARNESS_PROTOCOL": [
        "plans/p27/work/n10.txt",
        "plans/p27/results/N10_HARNESS_PROTOCOL.result.v1.json",
        "plans/p27/results/evidence/N10_HARNESS_PROTOCOL",
    ],
    "N20_PROVIDER_TRANSPORT": [
        "plans/p27/work/n20.txt",
        "plans/p27/results/N20_PROVIDER_TRANSPORT.result.v1.json",
        "plans/p27/results/evidence/N20_PROVIDER_TRANSPORT",
    ],
    "N70_LIVE_UNIT_PROOF": [
        "outputs/live",
        "plans/p27/results/N70_LIVE_UNIT_PROOF.result.v1.json",
        "plans/p27/results/evidence/N70_LIVE_UNIT_PROOF",
    ],
    "N90_REQUIREMENTS_FINAL_AUDIT": [
        "plans/p27/results/N90_REQUIREMENTS_FINAL_AUDIT.result.v1.json",
        "plans/p27/results/evidence/N90_REQUIREMENTS_FINAL_AUDIT",
    ],
}

NODE_DEPENDS: dict[str, list[str]] = {
    "N00_SPEC_APPROVAL_GATE": [],
    "N10_HARNESS_PROTOCOL": ["N00_SPEC_APPROVAL_GATE"],
    "N20_PROVIDER_TRANSPORT": ["N10_HARNESS_PROTOCOL"],
    "N70_LIVE_UNIT_PROOF": ["N20_PROVIDER_TRANSPORT"],
    "N90_REQUIREMENTS_FINAL_AUDIT": ["N70_LIVE_UNIT_PROOF"],
}

NODE_ALLOWED: dict[str, list[str]] = {
    "N00_SPEC_APPROVAL_GATE": ["PASSED", "BLOCKED_SPEC_NOT_APPROVED", "BLOCKED"],
    "N10_HARNESS_PROTOCOL": ["PASSED", "BLOCKED"],
    "N20_PROVIDER_TRANSPORT": ["PASSED", "BLOCKED"],
    "N70_LIVE_UNIT_PROOF": ["PASSED", "NOT_AVAILABLE", "BLOCKED"],
    "N90_REQUIREMENTS_FINAL_AUDIT": ["PASSED", "BLOCKED"],
}

CHAIN = list(NODE_DEPENDS)


class Env:
    """A synthetic but structurally real plan tree."""

    def __init__(self, root: Path) -> None:
        self.repo = root / "repo"
        self.plan = self.repo / "plans/p27"
        self.state_dir = root / "state"
        self.graph_path = self.plan / "implementation.graph.v1.yaml"
        self._build()

    def _build(self) -> None:
        for relative in ("prompts", "schemas", "results/evidence", "work"):
            (self.plan / relative).mkdir(parents=True, exist_ok=True)
        (self.repo / "spec").mkdir(parents=True, exist_ok=True)
        (self.repo / "spec/spec.v2.md").write_text("# approved specification v2\n", encoding="utf-8")
        (self.plan / "incident.md").write_text("# incident\n", encoding="utf-8")
        (self.plan / "run.prompt.md").write_text("# runner\n", encoding="utf-8")
        (self.plan / "qa.md").write_text("# qa\n", encoding="utf-8")
        shutil.copy2(FROZEN_RESULT_SCHEMA, self.plan / "schemas/node_result.schema.v1.json")
        for node_id in CHAIN:
            (self.plan / f"prompts/{node_id}.prompt.md").write_text(
                f"# GOAL\n\n{node_id}\n", encoding="utf-8"
            )
        self.write_graph()

    def graph_document(self) -> dict[str, Any]:
        return {
            "graph_id": "plan27_synthetic_test_graph",
            "version": 1,
            "status": "TEST",
            "source_incident": "plans/p27/incident.md",
            "source_spec": "spec/spec.v2.md",
            "runner": "plans/p27/run.prompt.md",
            "qa_criteria": "plans/p27/qa.md",
            "node_result_schema": "plans/p27/schemas/node_result.schema.v1.json",
            "entry": "N00_SPEC_APPROVAL_GATE",
            "result_pattern": "plans/p27/results/{node_id}.result.v1.json",
            "rules": {
                "invalidate_all_descendants_on_ancestor_change": True,
                "markdown_status_is_authority": False,
            },
            "nodes": {
                node_id: {
                    "prompt": f"plans/p27/prompts/{node_id}.prompt.md",
                    "depends_on": NODE_DEPENDS[node_id],
                    "writes": NODE_WRITES[node_id],
                    "verification": VERIFY_OK,
                    "allowed_results": NODE_ALLOWED[node_id],
                }
                for node_id in CHAIN
            },
            "edges": [
                {"from": dependency, "to": node_id}
                for node_id, dependencies in NODE_DEPENDS.items()
                for dependency in dependencies
            ],
            "terminals": {
                "ACTIVATED": {},
                "REMEDIATION_VERIFIED_NOT_ACTIVATED": {},
                "BLOCKED_SPEC_NOT_APPROVED": {},
                "BLOCKED": {},
            },
        }

    def write_graph(self, document: dict[str, Any] | None = None) -> None:
        self.graph_path.write_text(
            yaml.safe_dump(document or self.graph_document(), sort_keys=True), encoding="utf-8"
        )

    def graph(self) -> Graph:
        return Graph.load(self.graph_path, self.repo)

    def scheduler(self) -> Scheduler:
        return Scheduler(self.graph(), self.state_dir, run_id="test")

    # ------------------------------------------------------------- artifacts

    def evidence_dir(self, node_id: str) -> Path:
        return self.plan / f"results/evidence/{node_id}"

    def artifact(self, node_id: str) -> str | None:
        for relative in NODE_WRITES[node_id]:
            if relative.endswith(".txt"):
                return relative
        return None

    def stage(self, node_id: str, body: str = "v1") -> dict[str, Any]:
        """Write the node's outputs and return its evidence/command/changed set."""

        evidence = self.evidence_dir(node_id)
        evidence.mkdir(parents=True, exist_ok=True)
        log_relative = f"plans/p27/results/evidence/{node_id}/run.log"
        (self.repo / log_relative).write_text(f"{node_id} verified\n", encoding="utf-8")

        changed = [
            {
                "path": log_relative,
                "change": "created",
                "sha256": sha256_file(self.repo / log_relative),
            }
        ]
        artifact = self.artifact(node_id)
        if artifact:
            target = self.repo / artifact
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"{node_id}:{body}\n", encoding="utf-8")
            changed.append(
                {"path": artifact, "change": "created", "sha256": sha256_file(target)}
            )
        if node_id == "N70_LIVE_UNIT_PROOF":
            live = self.repo / "outputs/live/unit.json"
            live.parent.mkdir(parents=True, exist_ok=True)
            live.write_text(json.dumps({"unit": body}) + "\n", encoding="utf-8")
            changed.append(
                {"path": "outputs/live/unit.json", "change": "created", "sha256": sha256_file(live)}
            )
        return {
            "changed_files": changed,
            "commands": [
                {
                    "argv": ["python3", "-c", "print('ok')"],
                    "exit_code": 0,
                    "log": log_relative,
                    "log_sha256": sha256_file(self.repo / log_relative),
                }
            ],
            "evidence": [log_relative],
        }

    def write_result(self, node_id: str, **overrides: Any) -> Path:
        graph = self.graph()
        staged = overrides.pop("staged", None)
        if staged is None:
            staged = self.stage(node_id, overrides.pop("body", "v1"))
        payload: dict[str, Any] = {
            "schema_version": 1,
            "run_id": "test",
            "node_id": node_id,
            "attempt_id": f"{node_id}-declared",
            "outcome": "PASSED",
            "source_spec_sha256": graph.source_spec_digest(),
            "prompt_sha256": graph.prompt_digest(node_id),
            "predecessor_receipts": {
                predecessor: core.result_digest(graph, predecessor)
                for predecessor in NODE_DEPENDS[node_id]
            },
            "changed_files": staged["changed_files"],
            "commands": staged["commands"],
            "evidence": staged["evidence"],
            "findings": [],
            "invalidated_descendants": [],
        }
        payload.update(overrides)
        path = graph.result_path(node_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def admit(self, node_id: str, **overrides: Any) -> dict[str, Any]:
        self.write_result(node_id, **overrides)
        sched = self.scheduler()
        attempt = sched.begin(node_id)
        return sched.admit(node_id, attempt["attempt_id"])

    def admit_through(self, last: str) -> None:
        for node_id in CHAIN:
            if node_id == "N90_REQUIREMENTS_FINAL_AUDIT":
                self.admit(node_id, terminal_recommendation="ACTIVATED")
            else:
                self.admit(node_id)
            if node_id == last:
                return


@pytest.fixture()
def env(tmp_path: Path) -> Env:
    return Env(tmp_path)


def run_cli(env: Env, *argv: str) -> tuple[int, dict[str, Any]]:
    process = subprocess.run(
        [
            sys.executable,
            str(CONTROLLER_DIR / "run27_controller.py"),
            "--graph",
            str(env.graph_path),
            "--repo-root",
            str(env.repo),
            "--state-dir",
            str(env.state_dir),
            "--run-id",
            "test",
            *argv,
        ],
        capture_output=True,
        text=True,
    )
    payload = json.loads(process.stdout.strip().splitlines()[-1]) if process.stdout.strip() else {}
    return process.returncode, payload


# ------------------------------------------------------- invariant 11: entry gate


def test_no_node_runs_without_an_admitted_entry_receipt(env: Env) -> None:
    sched = env.scheduler()
    with pytest.raises(ControllerError) as error:
        sched.begin("N10_HARNESS_PROTOCOL")
    assert error.value.code == "ENTRY_GATE_NOT_ADMITTED"
    assert not sched.entry_gate()["admitted"]
    assert not env.state_dir.exists()


def test_entry_receipt_stops_binding_when_the_approved_spec_changes(env: Env) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    assert env.scheduler().entry_gate()["admitted"]

    (env.repo / "spec/spec.v2.md").write_text("# a different specification\n", encoding="utf-8")
    sched = env.scheduler()
    gate = sched.entry_gate()
    assert not gate["admitted"]
    assert "approved spec" in gate["reason"]
    with pytest.raises(ControllerError) as error:
        sched.begin("N10_HARNESS_PROTOCOL")
    assert error.value.code == "ENTRY_GATE_NOT_ADMITTED"


# --------------------------------------------------- invariant 2: receipt binding


def test_receipt_binds_graph_spec_prompt_baseline_predecessor_and_output_digests(env: Env) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    env.admit("N10_HARNESS_PROTOCOL")

    sched = env.scheduler()
    graph = sched.graph
    receipt = sched.receipt("N10_HARNESS_PROTOCOL")
    result = json.loads(graph.result_path("N10_HARNESS_PROTOCOL").read_text(encoding="utf-8"))

    assert receipt["graph_sha256"] == sha256_file(env.graph_path)
    assert receipt["approved_spec_sha256"] == sha256_file(env.repo / "spec/spec.v2.md")
    assert receipt["prompt_sha256"] == sha256_file(
        env.plan / "prompts/N10_HARNESS_PROTOCOL.prompt.md"
    )
    assert receipt["node_definition_sha256"] == graph.node_definition_digest("N10_HARNESS_PROTOCOL")
    assert set(receipt["baseline"]) == set(NODE_WRITES["N10_HARNESS_PROTOCOL"])
    assert receipt["baseline_sha256"] == core.canonical_digest(receipt["baseline"])
    assert receipt["predecessor_receipts"] == {
        "N00_SPEC_APPROVAL_GATE": sched.receipt_digest("N00_SPEC_APPROVAL_GATE")
    }
    assert receipt["predecessor_results"] == result["predecessor_receipts"]
    assert receipt["result_sha256"] == sha256_file(graph.result_path("N10_HARNESS_PROTOCOL"))
    assert receipt["changed_files"] == result["changed_files"]
    assert receipt["commands"] == result["commands"]
    assert receipt["evidence"] == result["evidence"]
    assert receipt["lineage_fingerprint"] == sched.lineage_fingerprint("N10_HARNESS_PROTOCOL")

    for relative in NODE_WRITES["N10_HARNESS_PROTOCOL"]:
        assert receipt["final_outputs"][relative] == core.path_digest(env.repo, relative)
    for command in receipt["commands"]:
        assert sha256_file(env.repo / command["log"]) == command["log_sha256"]
    assert receipt["verification"], "the controller must rerun the graph's own verification"
    assert all(item["exit_code"] == 0 for item in receipt["verification"])


def test_receipt_and_attempt_records_validate_against_their_schemas(env: Env) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    sched = env.scheduler()
    receipt = sched.receipt("N00_SPEC_APPROVAL_GATE")
    attempt = sched.attempts("N00_SPEC_APPROVAL_GATE")[0]

    scheduler_module.validate_against(
        scheduler_module.RECEIPT_SCHEMA_PATH, receipt, "receipt"
    )
    scheduler_module.validate_against(
        scheduler_module.ATTEMPT_SCHEMA_PATH, attempt.record(), "attempt"
    )
    with pytest.raises(ControllerError):
        scheduler_module.validate_against(
            scheduler_module.RECEIPT_SCHEMA_PATH, {**receipt, "status": "BLOCKED"}, "receipt"
        )


# ---------------------------------- invariants 3 and 4: automatic invalidation


def test_changing_an_admitted_ancestor_invalidates_every_transitive_descendant(env: Env) -> None:
    env.admit_through("N20_PROVIDER_TRANSPORT")
    sched = env.scheduler()
    assert all(sched.currency(node)["current"] for node in CHAIN[:3])

    n20_before = core.path_digest(env.repo, "plans/p27/work/n20.txt")
    (env.repo / "plans/p27/work/n10.txt").write_text("N10_HARNESS_PROTOCOL:reworked\n", encoding="utf-8")

    sched = env.scheduler()
    assert sched.currency("N00_SPEC_APPROVAL_GATE")["current"]
    assert not sched.currency("N10_HARNESS_PROTOCOL")["current"]
    n20 = sched.currency("N20_PROVIDER_TRANSPORT")
    assert not n20["current"]
    assert any(reason.startswith("ancestor_not_current") for reason in n20["reasons"])
    # The descendant's own bytes never changed; it is invalidated purely by lineage.
    assert core.path_digest(env.repo, "plans/p27/work/n20.txt") == n20_before
    assert sched.invalidated_descendants("N10_HARNESS_PROTOCOL") == ["N20_PROVIDER_TRANSPORT"]


def test_readmitting_an_ancestor_invalidates_descendants_whose_bytes_are_unchanged(env: Env) -> None:
    env.admit_through("N20_PROVIDER_TRANSPORT")
    before = env.scheduler().receipt_digest("N10_HARNESS_PROTOCOL")

    env.admit("N10_HARNESS_PROTOCOL", body="v2")
    sched = env.scheduler()
    assert sched.receipt_digest("N10_HARNESS_PROTOCOL") != before
    assert sched.currency("N10_HARNESS_PROTOCOL")["current"]

    n20 = sched.currency("N20_PROVIDER_TRANSPORT")
    assert not n20["current"]
    assert "lineage_fingerprint_changed" in n20["reasons"]


def test_a_graph_edit_invalidates_the_whole_admitted_chain(env: Env) -> None:
    env.admit_through("N20_PROVIDER_TRANSPORT")
    document = env.graph_document()
    document["status"] = "TEST_EDITED"
    env.write_graph(document)

    sched = env.scheduler()
    for node_id in CHAIN[:3]:
        assert not sched.currency(node_id)["current"], node_id


def test_an_invalidated_descendant_cannot_feed_the_final_audit_until_rerun(env: Env) -> None:
    env.admit_through("N90_REQUIREMENTS_FINAL_AUDIT")
    report = run27_controller.verify_final_audit(env.scheduler(), "N90_REQUIREMENTS_FINAL_AUDIT")
    assert report["valid"], report["problems"]

    (env.repo / "plans/p27/work/n10.txt").write_text("N10_HARNESS_PROTOCOL:drift\n", encoding="utf-8")
    report = run27_controller.verify_final_audit(env.scheduler(), "N90_REQUIREMENTS_FINAL_AUDIT")
    assert not report["valid"]
    assert {problem["code"] for problem in report["problems"]} == {
        "INVALIDATED_RECEIPT_FEEDS_FINAL_AUDIT"
    }

    # Re-running and re-receipting the ancestor is not enough on its own: every
    # descendant must be re-receipted against the current predecessor receipts.
    env.admit("N10_HARNESS_PROTOCOL", body="drift")
    report = run27_controller.verify_final_audit(env.scheduler(), "N90_REQUIREMENTS_FINAL_AUDIT")
    assert not report["valid"]

    for node_id in ("N20_PROVIDER_TRANSPORT", "N70_LIVE_UNIT_PROOF"):
        env.admit(node_id)
    env.admit("N90_REQUIREMENTS_FINAL_AUDIT", terminal_recommendation="ACTIVATED")
    report = run27_controller.verify_final_audit(env.scheduler(), "N90_REQUIREMENTS_FINAL_AUDIT")
    assert report["valid"], report["problems"]


# ---------------------------------------- invariant 5: write-set violation


def test_a_write_set_violation_fails_before_merge_and_keeps_an_immutable_attempt(env: Env) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    staged = env.stage("N10_HARNESS_PROTOCOL")
    stray = env.repo / "plans/p27/work/not_mine.txt"
    stray.write_text("out of scope\n", encoding="utf-8")
    staged["changed_files"].append(
        {"path": "plans/p27/work/not_mine.txt", "change": "created", "sha256": sha256_file(stray)}
    )
    env.write_result("N10_HARNESS_PROTOCOL", staged=staged)

    sched = env.scheduler()
    attempt_id = sched.begin("N10_HARNESS_PROTOCOL")["attempt_id"]
    with pytest.raises(ControllerError) as error:
        sched.admit("N10_HARNESS_PROTOCOL", attempt_id)
    assert error.value.code == "WRITE_SET_VIOLATION"

    attempt = sched.attempt("N10_HARNESS_PROTOCOL", attempt_id)
    assert attempt.state() == "failed"
    assert not attempt.journal_path.exists(), "no merge may be journaled after a scope violation"
    assert sched.receipt("N10_HARNESS_PROTOCOL") is None
    failure = json.loads((attempt.root / "failed.json").read_text(encoding="utf-8"))
    assert failure["code"] == "WRITE_SET_VIOLATION"
    with pytest.raises(ControllerError):
        core.write_once_json(attempt.root / "failed.json", {"code": "rewritten"})
    with pytest.raises(ControllerError):
        core.write_once_json(attempt.record_path, {"tampered": True})


def test_a_failed_attempt_cannot_be_admitted_again_without_resuming(env: Env) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    env.write_result("N10_HARNESS_PROTOCOL", outcome="BLOCKED")
    sched = env.scheduler()
    attempt_id = sched.begin("N10_HARNESS_PROTOCOL")["attempt_id"]
    with pytest.raises(ControllerError) as error:
        sched.admit("N10_HARNESS_PROTOCOL", attempt_id)
    assert error.value.code == "OUTCOME_NOT_ADMISSIBLE"
    assert sched.receipt("N10_HARNESS_PROTOCOL") is None

    with pytest.raises(ControllerError) as error:
        sched.admit("N10_HARNESS_PROTOCOL", attempt_id)
    assert error.value.code == "ATTEMPT_NOT_OPEN"


# ------------------------------- invariants 6 and 8: interruption and recovery


def _interrupt_merge(monkeypatch: pytest.MonkeyPatch) -> None:
    def explode(path: Path, text: str) -> None:
        raise OSError("simulated process kill during the receipt replace")

    monkeypatch.setattr(scheduler_module, "atomic_write_text", explode)


def test_an_interrupted_merge_never_lands_partial_bytes_or_merges_implicitly(
    env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    env.write_result("N10_HARNESS_PROTOCOL")
    sched = env.scheduler()
    attempt_id = sched.begin("N10_HARNESS_PROTOCOL")["attempt_id"]

    _interrupt_merge(monkeypatch)
    with pytest.raises(OSError):
        sched.admit("N10_HARNESS_PROTOCOL", attempt_id)
    monkeypatch.undo()

    sched = env.scheduler()
    attempt = sched.attempt("N10_HARNESS_PROTOCOL", attempt_id)
    assert sched.receipt("N10_HARNESS_PROTOCOL") is None
    assert attempt.journal_path.is_file()
    assert not (attempt.root / "merged.json").exists()
    assert not sched.currency("N10_HARNESS_PROTOCOL")["current"]

    with pytest.raises(ControllerError) as error:
        sched.admit("N10_HARNESS_PROTOCOL", attempt_id)
    assert error.value.code == "MERGE_JOURNAL_OPEN"

    recovered = sched.recover("N10_HARNESS_PROTOCOL", attempt_id)
    assert recovered["action"] == "rolled_back"
    assert sched.receipt("N10_HARNESS_PROTOCOL") is None
    assert sched.attempt("N10_HARNESS_PROTOCOL", attempt_id).state() == "interrupted"


def test_resume_creates_a_child_attempt_bound_to_current_predecessor_digests(
    env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    env.write_result("N10_HARNESS_PROTOCOL")
    sched = env.scheduler()
    parent_id = sched.begin("N10_HARNESS_PROTOCOL")["attempt_id"]
    _interrupt_merge(monkeypatch)
    with pytest.raises(OSError):
        sched.admit("N10_HARNESS_PROTOCOL", parent_id)
    monkeypatch.undo()

    sched = env.scheduler()
    sched.recover("N10_HARNESS_PROTOCOL", parent_id)
    child = sched.resume("N10_HARNESS_PROTOCOL", parent_id)

    assert child["attempt_id"] != parent_id
    assert child["parent_attempt_id"] == parent_id
    assert child["predecessor_receipt_digests"] == {
        "N00_SPEC_APPROVAL_GATE": sched.receipt_digest("N00_SPEC_APPROVAL_GATE")
    }
    assert sched.attempt("N10_HARNESS_PROTOCOL", parent_id).state() == "interrupted"

    merged = sched.admit("N10_HARNESS_PROTOCOL", child["attempt_id"])
    assert merged["status"] == "PASSED"
    assert sched.currency("N10_HARNESS_PROTOCOL")["current"]

    with pytest.raises(ControllerError) as error:
        sched.resume("N10_HARNESS_PROTOCOL", child["attempt_id"])
    assert error.value.code == "RESUME_OF_MERGED_ATTEMPT"


def test_recovery_completes_a_merge_whose_rename_already_landed(
    env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    env.write_result("N10_HARNESS_PROTOCOL")
    sched = env.scheduler()
    attempt_id = sched.begin("N10_HARNESS_PROTOCOL")["attempt_id"]
    _interrupt_merge(monkeypatch)
    with pytest.raises(OSError):
        sched.admit("N10_HARNESS_PROTOCOL", attempt_id)
    monkeypatch.undo()

    sched = env.scheduler()
    attempt = sched.attempt("N10_HARNESS_PROTOCOL", attempt_id)
    journal = json.loads(attempt.journal_path.read_text(encoding="utf-8"))
    # The rename is atomic: either these exact bytes are present or none are.
    core.atomic_write_text(
        sched.receipt_path("N10_HARNESS_PROTOCOL"), core.serialize_record(journal["receipt"])
    )

    recovered = sched.recover("N10_HARNESS_PROTOCOL", attempt_id)
    assert recovered["action"] == "completed"
    assert sched.attempt("N10_HARNESS_PROTOCOL", attempt_id).state() == "merged"
    assert sched.currency("N10_HARNESS_PROTOCOL")["current"]


def test_a_rolled_back_merge_restores_the_previous_receipt_exactly(
    env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    env.admit("N10_HARNESS_PROTOCOL")
    sched = env.scheduler()
    original = sched.receipt_path("N10_HARNESS_PROTOCOL").read_bytes()

    env.write_result("N10_HARNESS_PROTOCOL", body="v2")
    attempt_id = sched.begin("N10_HARNESS_PROTOCOL")["attempt_id"]
    _interrupt_merge(monkeypatch)
    with pytest.raises(OSError):
        sched.admit("N10_HARNESS_PROTOCOL", attempt_id)
    monkeypatch.undo()

    sched = env.scheduler()
    sched.recover("N10_HARNESS_PROTOCOL", attempt_id)
    assert sched.receipt_path("N10_HARNESS_PROTOCOL").read_bytes() == original


# ---------------------------------------- invariant 7: named re-admission


def test_readmission_is_named_artifact_bound_verified_and_audited(env: Env) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    env.admit("N10_HARNESS_PROTOCOL")
    sched = env.scheduler()
    superseded = sched.receipt_digest("N10_HARNESS_PROTOCOL")
    result_sha = sha256_file(sched.graph.result_path("N10_HARNESS_PROTOCOL"))

    attempt_id = sched.begin("N10_HARNESS_PROTOCOL")["attempt_id"]
    with pytest.raises(ControllerError) as error:
        sched.admit(
            "N10_HARNESS_PROTOCOL",
            attempt_id,
            recovery={"reason_code": "BECAUSE_I_SAID_SO", "reason": "x", "expect_result_sha256": result_sha},
        )
    assert error.value.code == "UNKNOWN_RECOVERY_REASON"

    attempt_id = sched.resume("N10_HARNESS_PROTOCOL", attempt_id)["attempt_id"]
    with pytest.raises(ControllerError) as error:
        sched.admit(
            "N10_HARNESS_PROTOCOL",
            attempt_id,
            recovery={
                "reason_code": "EXTERNAL_PROCESS_KILL",
                "reason": "controller subprocess was killed by an outside mechanism",
                "expect_result_sha256": "0" * 64,
            },
        )
    assert error.value.code == "RECOVERY_ARTIFACT_MISMATCH"

    attempt_id = sched.resume("N10_HARNESS_PROTOCOL", attempt_id)["attempt_id"]
    merged = sched.admit(
        "N10_HARNESS_PROTOCOL",
        attempt_id,
        recovery={
            "reason_code": "EXTERNAL_PROCESS_KILL",
            "reason": "controller subprocess was killed by an outside mechanism",
            "expect_result_sha256": result_sha,
        },
    )
    assert merged["admission"] == "recovery_readmission"

    receipt = sched.receipt("N10_HARNESS_PROTOCOL")
    assert receipt["recovery"] == {
        "reason_code": "EXTERNAL_PROCESS_KILL",
        "reason": "controller subprocess was killed by an outside mechanism",
        "expect_result_sha256": result_sha,
        "superseded_receipt_sha256": superseded,
        "verification_rerun": True,
    }
    assert receipt["verification"] and all(item["exit_code"] == 0 for item in receipt["verification"])
    assert (sched.receipts_dir / "history/N10_HARNESS_PROTOCOL" / f"{superseded}.json").is_file()

    events = [event["event"] for event in sched.audit()]
    assert events.count("attempt_resumed") == 2
    admitted = [
        event
        for event in sched.audit()
        if event["event"] == "node_admitted" and event["node_id"] == "N10_HARNESS_PROTOCOL"
    ]
    assert admitted[-1]["admission"] == "recovery_readmission"


def test_verification_failure_blocks_admission_and_records_the_logs(env: Env) -> None:
    document = env.graph_document()
    document["nodes"]["N10_HARNESS_PROTOCOL"]["verification"] = [
        ["python3", "-c", "import sys; sys.exit(3)"]
    ]
    env.write_graph(document)
    env.admit("N00_SPEC_APPROVAL_GATE")
    env.write_result("N10_HARNESS_PROTOCOL")

    sched = env.scheduler()
    attempt_id = sched.begin("N10_HARNESS_PROTOCOL")["attempt_id"]
    with pytest.raises(ControllerError) as error:
        sched.admit("N10_HARNESS_PROTOCOL", attempt_id)
    assert error.value.code == "VERIFICATION_FAILED"
    assert sched.receipt("N10_HARNESS_PROTOCOL") is None
    assert (sched.attempt("N10_HARNESS_PROTOCOL", attempt_id).logs_dir / "verify_00.log").is_file()


# ---------------------------------------- invariant 9: attempt-scoped evidence


def test_attempt_evidence_paths_are_attempt_scoped_and_write_once(env: Env) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    env.write_result("N10_HARNESS_PROTOCOL")
    sched = env.scheduler()
    first = sched.attempt("N10_HARNESS_PROTOCOL", sched.begin("N10_HARNESS_PROTOCOL")["attempt_id"])
    second = sched.attempt("N10_HARNESS_PROTOCOL", sched.begin("N10_HARNESS_PROTOCOL")["attempt_id"])

    assert first.logs_dir != second.logs_dir
    assert first.logs_dir.is_relative_to(sched.attempts_dir / "N10_HARNESS_PROTOCOL")
    first.write_log("probe.log", "one")
    with pytest.raises(ControllerError) as error:
        first.write_log("probe.log", "two")
    assert error.value.code == "WRITE_ONCE_VIOLATION"
    assert first.log_path("probe.log").read_text(encoding="utf-8") == "one"
    second.write_log("probe.log", "independent")
    with pytest.raises(ControllerError):
        first.write_log("../escape.log", "nope")


# ---------------------------------------- invariant 10: read-only commands


READ_ONLY_INVOCATIONS = (
    ("status",),
    ("plan",),
    ("audit",),
    ("validate", "--node", "N10_HARNESS_PROTOCOL"),
    ("verify-live-proof", "--node", "N70_LIVE_UNIT_PROOF"),
    ("verify-final-audit", "--node", "N90_REQUIREMENTS_FINAL_AUDIT"),
)


def test_status_validate_dryrun_and_audit_commands_are_read_only(env: Env) -> None:
    env.admit_through("N90_REQUIREMENTS_FINAL_AUDIT")
    before_state = tree_digest(env.state_dir)
    before_repo = tree_digest(env.repo)

    first: list[dict[str, Any]] = []
    for argv in READ_ONLY_INVOCATIONS:
        _code, payload = run_cli(env, *argv)
        first.append(payload)
    assert tree_digest(env.state_dir) == before_state
    assert tree_digest(env.repo) == before_repo

    for index, argv in enumerate(READ_ONLY_INVOCATIONS):
        _code, payload = run_cli(env, *argv)
        assert payload == first[index], f"{argv} is not deterministic"
    assert tree_digest(env.state_dir) == before_state
    assert tree_digest(env.repo) == before_repo


def test_read_only_commands_do_not_create_the_state_directory(env: Env) -> None:
    for argv in (("status",), ("plan",), ("audit",)):
        code, payload = run_cli(env, *argv)
        assert code == 0, payload
        assert not env.state_dir.exists()


def test_validate_reports_problems_without_touching_any_attempt(env: Env) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    staged = env.stage("N10_HARNESS_PROTOCOL")
    staged["changed_files"][0]["sha256"] = "0" * 64
    env.write_result("N10_HARNESS_PROTOCOL", staged=staged)

    before = tree_digest(env.state_dir)
    code, payload = run_cli(env, "validate", "--node", "N10_HARNESS_PROTOCOL")
    assert code == 1
    assert "CHANGED_FILE_DIGEST_MISMATCH" in {item["code"] for item in payload["problems"]}
    assert tree_digest(env.state_dir) == before
    assert env.scheduler().attempts("N10_HARNESS_PROTOCOL") == []


# ------------------------------------------------------------ live proof


def test_verify_live_proof_requires_the_production_cli_and_real_outputs(env: Env) -> None:
    env.admit_through("N20_PROVIDER_TRANSPORT")
    env.write_result("N70_LIVE_UNIT_PROOF")
    sched = env.scheduler()

    report = run27_controller.verify_live_proof(sched, "N70_LIVE_UNIT_PROOF")
    assert not report["valid"]
    assert "NO_PRODUCTION_CLI_INVOCATION" in {item["code"] for item in report["problems"]}

    staged = env.stage("N70_LIVE_UNIT_PROOF")
    staged["commands"][0]["argv"] = ["python3", "runtime/run_curriculum.py", "--unit", "L01"]
    env.write_result("N70_LIVE_UNIT_PROOF", staged=staged)
    report = run27_controller.verify_live_proof(env.scheduler(), "N70_LIVE_UNIT_PROOF")
    assert report["valid"], report["problems"]


def test_verify_live_proof_rejects_simulated_evidence(env: Env) -> None:
    env.admit_through("N20_PROVIDER_TRANSPORT")
    staged = env.stage("N70_LIVE_UNIT_PROOF")
    staged["commands"][0]["argv"] = ["python3", "runtime/run_curriculum.py", "--unit", "L01"]
    log = env.repo / staged["evidence"][0]
    log.write_text("FAKE_TRANSPORT produced this unit\n", encoding="utf-8")
    digest = sha256_file(log)
    staged["commands"][0]["log_sha256"] = digest
    staged["changed_files"][0]["sha256"] = digest
    env.write_result("N70_LIVE_UNIT_PROOF", staged=staged)

    report = run27_controller.verify_live_proof(env.scheduler(), "N70_LIVE_UNIT_PROOF")
    assert not report["valid"]
    assert "SIMULATED_LIVE_EVIDENCE" in {item["code"] for item in report["problems"]}


def test_not_available_live_proof_must_name_an_open_finding(env: Env) -> None:
    env.admit_through("N20_PROVIDER_TRANSPORT")
    env.write_result("N70_LIVE_UNIT_PROOF", outcome="NOT_AVAILABLE")
    report = run27_controller.verify_live_proof(env.scheduler(), "N70_LIVE_UNIT_PROOF")
    assert not report["valid"]
    assert "UNEXPLAINED_NOT_AVAILABLE" in {item["code"] for item in report["problems"]}

    env.write_result(
        "N70_LIVE_UNIT_PROOF",
        outcome="NOT_AVAILABLE",
        findings=[
            {
                "id": "N70-F01",
                "severity": "major",
                "summary": "the approved subscription driver is unavailable in this environment",
                "disposition": "open",
            }
        ],
    )
    report = run27_controller.verify_live_proof(env.scheduler(), "N70_LIVE_UNIT_PROOF")
    assert report["valid"], report["problems"]


def test_verify_live_proof_refuses_a_node_that_cannot_report_not_available(env: Env) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    with pytest.raises(ControllerError) as error:
        run27_controller.verify_live_proof(env.scheduler(), "N10_HARNESS_PROTOCOL")
    assert error.value.code == "NOT_A_LIVE_PROOF_NODE"


# ------------------------------------------------------------ final audit


def test_activation_requires_live_proof_and_the_alternative_terminal_requires_unavailability(
    env: Env,
) -> None:
    env.admit_through("N20_PROVIDER_TRANSPORT")
    env.admit(
        "N70_LIVE_UNIT_PROOF",
        outcome="NOT_AVAILABLE",
        findings=[
            {
                "id": "N70-F01",
                "severity": "major",
                "summary": "no authorized live driver in this environment",
                "disposition": "open",
            }
        ],
    )
    env.admit("N90_REQUIREMENTS_FINAL_AUDIT", terminal_recommendation="ACTIVATED")
    report = run27_controller.verify_final_audit(env.scheduler(), "N90_REQUIREMENTS_FINAL_AUDIT")
    assert not report["valid"]
    assert "ACTIVATION_WITHOUT_LIVE_PROOF" in {item["code"] for item in report["problems"]}

    env.admit(
        "N90_REQUIREMENTS_FINAL_AUDIT",
        terminal_recommendation="REMEDIATION_VERIFIED_NOT_ACTIVATED",
    )
    report = run27_controller.verify_final_audit(env.scheduler(), "N90_REQUIREMENTS_FINAL_AUDIT")
    assert report["valid"], report["problems"]


def test_only_the_single_sink_node_may_be_final_audited(env: Env) -> None:
    env.admit("N00_SPEC_APPROVAL_GATE")
    with pytest.raises(ControllerError) as error:
        run27_controller.verify_final_audit(env.scheduler(), "N10_HARNESS_PROTOCOL")
    assert error.value.code == "NOT_THE_FINAL_AUDIT_NODE"
    assert env.scheduler().graph.final_audit_node() == "N90_REQUIREMENTS_FINAL_AUDIT"


# ------------------------------------------- contract verifier entry points


def write_contract(path: Path, kind: str, claims: list[dict[str, Any]]) -> Path:
    path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "kind": kind,
                "contract_id": f"{kind}.test.v1",
                "node_id": "N20_PROVIDER_TRANSPORT",
                "claims": claims,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


def run_verifier(script: str, env: Env, contract: Path) -> tuple[int, dict[str, Any]]:
    process = subprocess.run(
        [
            sys.executable,
            str(CONTROLLER_DIR / script),
            "--contract",
            str(contract),
            "--graph",
            str(env.graph_path),
            "--repo-root",
            str(env.repo),
        ],
        capture_output=True,
        text=True,
    )
    return process.returncode, json.loads(process.stdout.strip().splitlines()[-1])


def test_verify_ownership_accepts_a_true_contract_and_rejects_a_false_one(
    env: Env, tmp_path: Path
) -> None:
    env.admit_through("N20_PROVIDER_TRANSPORT")
    truthful = write_contract(
        tmp_path / "ownership.yaml",
        "integration_ownership",
        [
            {"type": "file_exists", "path": "plans/p27/work/n20.txt"},
            {
                "type": "owned_by_node",
                "path": "plans/p27/work/n20.txt",
                "node": "N20_PROVIDER_TRANSPORT",
            },
            {"type": "single_owner", "path": "plans/p27/work/n10.txt"},
        ],
    )
    code, payload = run_verifier("verify_ownership.py", env, truthful)
    assert code == 0 and payload["ok"], payload

    false = write_contract(
        tmp_path / "ownership_false.yaml",
        "integration_ownership",
        [
            {
                "type": "owned_by_node",
                "path": "plans/p27/work/n20.txt",
                "node": "N10_HARNESS_PROTOCOL",
            }
        ],
    )
    code, payload = run_verifier("verify_ownership.py", env, false)
    assert code == 1 and not payload["ok"]
    assert payload["failures"][0]["type"] == "owned_by_node"

    wrong_kind = write_contract(tmp_path / "wrong.yaml", "evidence_determinism", [{"type": "file_exists", "path": "x"}])
    code, payload = run_verifier("verify_ownership.py", env, wrong_kind)
    assert code == 1 and payload["code"] == "CONTRACT_KIND_MISMATCH"


def test_verify_evidence_determinism_detects_a_nondeterministic_command(
    env: Env, tmp_path: Path
) -> None:
    env.admit_through("N20_PROVIDER_TRANSPORT")
    stable = write_contract(
        tmp_path / "determinism.yaml",
        "evidence_determinism",
        [
            {
                "type": "command_repeats_identically",
                "argv": ["python3", "-c", "print('stable evidence')"],
                "exit_code": 0,
            },
            {
                "type": "paths_stable_under_command",
                "argv": ["python3", "-c", "print('no writes')"],
                "paths": ["plans/p27/work/n20.txt"],
            },
            {"type": "text_absent", "path": "plans/p27/work/n20.txt", "pattern": r"/var/folders/\S+"},
        ],
    )
    code, payload = run_verifier("verify_evidence_determinism.py", env, stable)
    assert code == 0 and payload["ok"], payload

    volatile = write_contract(
        tmp_path / "determinism_bad.yaml",
        "evidence_determinism",
        [
            {
                "type": "command_repeats_identically",
                "argv": ["python3", "-c", "import uuid; print(uuid.uuid4())"],
            },
            {
                "type": "paths_stable_under_command",
                "argv": [
                    "python3",
                    "-c",
                    "import pathlib,uuid; pathlib.Path('plans/p27/work/n20.txt').write_text(str(uuid.uuid4()))",
                ],
                "paths": ["plans/p27/work/n20.txt"],
            },
        ],
    )
    code, payload = run_verifier("verify_evidence_determinism.py", env, volatile)
    assert code == 1 and not payload["ok"]
    assert {item["type"] for item in payload["failures"]} == {
        "command_repeats_identically",
        "paths_stable_under_command",
    }


def test_verify_requirements_lineage_rejects_an_uncovered_requirement(
    env: Env, tmp_path: Path
) -> None:
    env.admit_through("N20_PROVIDER_TRANSPORT")
    (env.repo / "spec/requirements.md").write_text(
        "REQ-001 transport must be schema bound\nREQ-002 evidence must be deterministic\n",
        encoding="utf-8",
    )
    complete = write_contract(
        tmp_path / "lineage.yaml",
        "requirements_lineage",
        [
            {
                "type": "requirement",
                "id": "REQ-001",
                "source": "spec/requirements.md",
                "source_anchor": "transport must be schema bound",
                "implemented_by": ["plans/p27/work/n20.txt"],
                "evidence": ["plans/p27/results/evidence/N20_PROVIDER_TRANSPORT/run.log"],
            },
            {
                "type": "requirement",
                "id": "REQ-002",
                "source": "spec/requirements.md",
                "source_anchor": "evidence must be deterministic",
                "implemented_by": ["plans/p27/work/n20.txt"],
                "evidence": ["plans/p27/results/evidence/N20_PROVIDER_TRANSPORT/run.log"],
            },
            {
                "type": "requirement_ids_cover",
                "source": "spec/requirements.md",
                "pattern": r"REQ-\d{3}",
            },
        ],
    )
    code, payload = run_verifier("verify_requirements_lineage.py", env, complete)
    assert code == 0 and payload["ok"], payload

    partial = write_contract(
        tmp_path / "lineage_partial.yaml",
        "requirements_lineage",
        [
            {
                "type": "requirement",
                "id": "REQ-001",
                "source": "spec/requirements.md",
                "source_anchor": "transport must be schema bound",
                "implemented_by": ["plans/p27/work/n20.txt"],
                "evidence": [],
            },
            {
                "type": "requirement_ids_cover",
                "source": "spec/requirements.md",
                "pattern": r"REQ-\d{3}",
            },
        ],
    )
    code, payload = run_verifier("verify_requirements_lineage.py", env, partial)
    assert code == 1 and not payload["ok"]
    assert payload["failures"][0]["detail"] == "uncovered=['REQ-002']"

    lying = write_contract(
        tmp_path / "lineage_false.yaml",
        "requirements_lineage",
        [
            {
                "type": "requirement",
                "id": "REQ-001",
                "source": "spec/requirements.md",
                "source_anchor": "a sentence that is not in the source",
                "implemented_by": ["plans/p27/work/nowhere.txt"],
                "evidence": [],
            }
        ],
    )
    code, payload = run_verifier("verify_requirements_lineage.py", env, lying)
    assert code == 1 and "anchor" in payload["failures"][0]["detail"]


# ------------------------------- invariant 12: the real Plan 27 scaffold


def test_the_real_plan27_graph_validates() -> None:
    process = subprocess.run(
        [sys.executable, str(PLAN_DIR / "tools/validate_plan.py")],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    assert json.loads(process.stdout)["valid"] is True


def test_the_real_graph_loads_and_exposes_its_scheduling_shape() -> None:
    graph = Graph.load(REAL_GRAPH, REPO_ROOT)
    assert graph.entry == "N00_SPEC_APPROVAL_GATE"
    assert graph.final_audit_node() == "N90_REQUIREMENTS_FINAL_AUDIT"
    assert graph.live_proof_nodes() == ["N70_LIVE_UNIT_PROOF", "N80_LIVE_WORKBOOK_PROOF"]
    assert graph.descendants("N20_PROVIDER_TRANSPORT") == [
        "N30_PREFLIGHT_EGRESS",
        "N40_INTEGRATION_OWNERSHIP",
        "N50_EVIDENCE_AUDIT_CONTROLS",
        "N60_ADVERSARIAL_REGRESSION",
        "N70_LIVE_UNIT_PROOF",
        "N80_LIVE_WORKBOOK_PROOF",
        "N90_REQUIREMENTS_FINAL_AUDIT",
    ]


def test_the_real_repo_read_only_plan_command_is_stable_and_creates_no_state(
    tmp_path: Path,
) -> None:
    state = tmp_path / "unused_state"
    argv = [
        sys.executable,
        str(CONTROLLER_DIR / "run27_controller.py"),
        "--state-dir",
        str(state),
        "plan",
    ]
    first = subprocess.run(argv, cwd=str(REPO_ROOT), capture_output=True, text=True)
    second = subprocess.run(argv, cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert first.returncode == 0 and first.stdout == second.stdout
    assert not state.exists()
    assert json.loads(first.stdout)["order"][0] == "N00_SPEC_APPROVAL_GATE"
