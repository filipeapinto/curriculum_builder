"""The node-result admission protocol.

Run 26 PM-17: the old controller read a bare ``status:`` line out of whatever the
node printed, so bold Markdown, an explanatory suffix, or a domain verdict such
as ``ACTIVATED`` produced nine ``node_did_not_report_an_admissible_status``
events against work that was actually correct. Admission here consumes exactly
one thing: a JSON document that validates against the frozen
``schemas/node_result.schema.v1.json``.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

import jsonschema
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

from core import (  # noqa: E402
    ControllerError,
    Graph,
    load_node_result,
    paths_overlap,
    sha256_file,
)
from scheduler import Scheduler  # noqa: E402


DIGEST = "0" * 64
CONTROLLER_MODULES = (
    "core.py",
    "scheduler.py",
    "run27_controller.py",
    "contracts.py",
    "check_forbidden_production_refs.py",
)


# ------------------------------------------------------------ minimal plan


class MiniPlan:
    def __init__(self, root: Path) -> None:
        self.repo = root / "repo"
        self.plan = self.repo / "plans/mini"
        self.state_dir = root / "state"
        self.graph_path = self.plan / "graph.yaml"
        for relative in ("prompts", "schemas", "results"):
            (self.plan / relative).mkdir(parents=True, exist_ok=True)
        (self.repo / "spec").mkdir(parents=True, exist_ok=True)
        (self.repo / "spec/spec.v2.md").write_text("# spec v2\n", encoding="utf-8")
        (self.plan / "incident.md").write_text("# incident\n", encoding="utf-8")
        (self.plan / "prompts/N00.md").write_text("# GOAL\n", encoding="utf-8")
        shutil.copy2(FROZEN_RESULT_SCHEMA, self.plan / "schemas/node_result.schema.v1.json")
        self.graph_path.write_text(
            yaml.safe_dump(
                {
                    "graph_id": "mini",
                    "version": 1,
                    "source_spec": "spec/spec.v2.md",
                    "node_result_schema": "plans/mini/schemas/node_result.schema.v1.json",
                    "entry": "N00_SPEC_APPROVAL_GATE",
                    "result_pattern": "plans/mini/results/{node_id}.result.v1.json",
                    "rules": {},
                    "nodes": {
                        "N00_SPEC_APPROVAL_GATE": {
                            "prompt": "plans/mini/prompts/N00.md",
                            "depends_on": [],
                            "writes": ["plans/mini/results/N00_SPEC_APPROVAL_GATE.result.v1.json"],
                            "verification": [["python3", "-c", "print('ok')"]],
                            "allowed_results": ["PASSED", "BLOCKED_SPEC_NOT_APPROVED", "BLOCKED"],
                        }
                    },
                    "edges": [],
                    "terminals": {},
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    @property
    def result_path(self) -> Path:
        return self.plan / "results/N00_SPEC_APPROVAL_GATE.result.v1.json"

    def graph(self) -> Graph:
        return Graph.load(self.graph_path, self.repo)

    def scheduler(self) -> Scheduler:
        return Scheduler(self.graph(), self.state_dir, run_id="test")

    def valid_result(self, **overrides: Any) -> dict[str, Any]:
        graph = self.graph()
        payload: dict[str, Any] = {
            "schema_version": 1,
            "run_id": "test",
            "node_id": "N00_SPEC_APPROVAL_GATE",
            "attempt_id": "a1",
            "outcome": "PASSED",
            "source_spec_sha256": graph.source_spec_digest(),
            "prompt_sha256": graph.prompt_digest("N00_SPEC_APPROVAL_GATE"),
            "predecessor_receipts": {},
            "changed_files": [],
            "commands": [],
            "evidence": [],
            "findings": [],
            "invalidated_descendants": [],
        }
        payload.update(overrides)
        return payload

    def write(self, text: str) -> None:
        self.result_path.write_text(text, encoding="utf-8")

    def write_json(self, payload: dict[str, Any]) -> None:
        self.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


@pytest.fixture()
def mini(tmp_path: Path) -> MiniPlan:
    return MiniPlan(tmp_path)


# ------------------------------- invariant 1: only schema-valid JSON admits


MARKDOWN_RESULTS = (
    "# N00 report\n\nstatus: PASSED\n",
    "**status: PASSED**\n\nEverything verified.\n",
    "status: PASSED (all verification commands exited zero)\n",
    "## Verdict\n\nACTIVATED\n",
    "status: IMPLEMENTED_NOT_ACTIVATED\n",
)


@pytest.mark.parametrize("body", MARKDOWN_RESULTS)
def test_markdown_and_prose_cannot_report_a_status(mini: MiniPlan, body: str) -> None:
    mini.write(body)
    with pytest.raises(ControllerError) as error:
        load_node_result(mini.graph(), "N00_SPEC_APPROVAL_GATE")
    assert error.value.code == "NON_JSON_RESULT"

    sched = mini.scheduler()
    attempt_id = sched.begin("N00_SPEC_APPROVAL_GATE")["attempt_id"]
    with pytest.raises(ControllerError) as error:
        sched.admit("N00_SPEC_APPROVAL_GATE", attempt_id)
    assert error.value.code == "NON_JSON_RESULT"
    assert sched.receipt("N00_SPEC_APPROVAL_GATE") is None


def test_json_wrapped_in_markdown_fences_is_not_a_result(mini: MiniPlan) -> None:
    mini.write("```json\n" + json.dumps(mini.valid_result()) + "\n```\n")
    with pytest.raises(ControllerError) as error:
        load_node_result(mini.graph(), "N00_SPEC_APPROVAL_GATE")
    assert error.value.code == "NON_JSON_RESULT"


def test_prose_inside_a_valid_result_cannot_override_the_outcome(mini: MiniPlan) -> None:
    mini.write_json(
        mini.valid_result(
            outcome="BLOCKED",
            findings=[
                {
                    "id": "F01",
                    "severity": "minor",
                    "summary": "**status: PASSED** everything actually worked, honestly",
                    "disposition": "resolved",
                }
            ],
        )
    )
    result = load_node_result(mini.graph(), "N00_SPEC_APPROVAL_GATE")
    assert result["outcome"] == "BLOCKED"

    sched = mini.scheduler()
    attempt_id = sched.begin("N00_SPEC_APPROVAL_GATE")["attempt_id"]
    with pytest.raises(ControllerError) as error:
        sched.admit("N00_SPEC_APPROVAL_GATE", attempt_id)
    assert error.value.code == "OUTCOME_NOT_ADMISSIBLE"
    assert sched.receipt("N00_SPEC_APPROVAL_GATE") is None


@pytest.mark.parametrize(
    "mutation,expected",
    [
        ({"outcome": "COMPLETE"}, "SCHEMA_INVALID_RESULT"),
        ({"schema_version": 2}, "SCHEMA_INVALID_RESULT"),
        ({"prompt_sha256": "not-a-digest"}, "SCHEMA_INVALID_RESULT"),
        ({"status": "PASSED"}, "SCHEMA_INVALID_RESULT"),
        ({"node_id": "N01_SOMETHING_ELSE"}, "SCHEMA_INVALID_RESULT"),
    ],
)
def test_a_result_that_does_not_validate_is_refused(
    mini: MiniPlan, mutation: dict[str, Any], expected: str
) -> None:
    payload = mini.valid_result()
    payload.update(mutation)
    mini.write_json(payload)
    with pytest.raises(ControllerError) as error:
        load_node_result(mini.graph(), "N00_SPEC_APPROVAL_GATE")
    assert error.value.code in {expected, "NODE_ID_MISMATCH", "OUTCOME_NOT_ALLOWED"}


def test_a_missing_required_field_is_refused(mini: MiniPlan) -> None:
    payload = mini.valid_result()
    payload.pop("invalidated_descendants")
    mini.write_json(payload)
    with pytest.raises(ControllerError) as error:
        load_node_result(mini.graph(), "N00_SPEC_APPROVAL_GATE")
    assert error.value.code == "SCHEMA_INVALID_RESULT"


def test_an_outcome_outside_the_graphs_allowed_results_is_refused(mini: MiniPlan) -> None:
    mini.write_json(mini.valid_result(outcome="NOT_AVAILABLE"))
    with pytest.raises(ControllerError) as error:
        load_node_result(mini.graph(), "N00_SPEC_APPROVAL_GATE")
    assert error.value.code == "OUTCOME_NOT_ALLOWED"


def test_no_controller_module_scrapes_a_status_token_out_of_text() -> None:
    forbidden = ('startswith("status', "startswith('status", 'split("status', "re.search(r\"status")
    for name in CONTROLLER_MODULES:
        source = (CONTROLLER_DIR / name).read_text(encoding="utf-8")
        for needle in forbidden:
            assert needle not in source, f"{name} appears to scrape a Run 26 status line"


# ------------------------- invariant 15: terminal recommendation vocabulary


@pytest.fixture(scope="module")
def frozen_validator() -> jsonschema.Draft202012Validator:
    schema = json.loads(FROZEN_RESULT_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def base_result(**overrides: Any) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "run_id": "run27",
        "node_id": "N10_HARNESS_PROTOCOL",
        "attempt_id": "a1",
        "outcome": "PASSED",
        "source_spec_sha256": DIGEST,
        "prompt_sha256": DIGEST,
        "predecessor_receipts": {"N00_SPEC_APPROVAL_GATE": DIGEST},
        "changed_files": [],
        "commands": [],
        "evidence": [],
        "findings": [],
        "invalidated_descendants": [],
    }
    payload.update(overrides)
    return payload


def test_only_the_final_audit_node_may_recommend_a_terminal(
    frozen_validator: jsonschema.Draft202012Validator,
) -> None:
    assert frozen_validator.is_valid(base_result())
    for terminal in ("ACTIVATED", "REMEDIATION_VERIFIED_NOT_ACTIVATED", "BLOCKED"):
        assert not frozen_validator.is_valid(base_result(terminal_recommendation=terminal))


def test_the_final_audit_node_must_recommend_exactly_one_legal_terminal(
    frozen_validator: jsonschema.Draft202012Validator,
) -> None:
    audit = base_result(
        node_id="N90_REQUIREMENTS_FINAL_AUDIT",
        predecessor_receipts={"N80_LIVE_WORKBOOK_PROOF": DIGEST},
    )
    assert not frozen_validator.is_valid(audit)
    assert frozen_validator.is_valid({**audit, "terminal_recommendation": "ACTIVATED"})
    assert frozen_validator.is_valid(
        {**audit, "terminal_recommendation": "REMEDIATION_VERIFIED_NOT_ACTIVATED"}
    )
    assert not frozen_validator.is_valid(
        {**audit, "terminal_recommendation": "BLOCKED_SPEC_NOT_APPROVED"}
    )
    assert not frozen_validator.is_valid(
        {**audit, "outcome": "BLOCKED", "terminal_recommendation": "ACTIVATED"}
    )
    assert frozen_validator.is_valid(
        {**audit, "outcome": "BLOCKED", "terminal_recommendation": "BLOCKED"}
    )


def test_only_the_entry_gate_may_emit_blocked_spec_not_approved(
    frozen_validator: jsonschema.Draft202012Validator,
) -> None:
    assert not frozen_validator.is_valid(base_result(outcome="BLOCKED_SPEC_NOT_APPROVED"))
    assert frozen_validator.is_valid(
        base_result(
            node_id="N00_SPEC_APPROVAL_GATE",
            outcome="BLOCKED_SPEC_NOT_APPROVED",
            source_spec_sha256=None,
            predecessor_receipts={},
        )
    )


def test_a_deleted_changed_file_must_carry_a_null_digest(
    frozen_validator: jsonschema.Draft202012Validator,
) -> None:
    assert frozen_validator.is_valid(
        base_result(changed_files=[{"path": "a", "change": "deleted", "sha256": None}])
    )
    assert not frozen_validator.is_valid(
        base_result(changed_files=[{"path": "a", "change": "deleted", "sha256": DIGEST}])
    )
    assert not frozen_validator.is_valid(
        base_result(changed_files=[{"path": "a", "change": "created", "sha256": None}])
    )


# ------------------- invariants 13 and 14: the real graph's node contracts


@pytest.fixture(scope="module")
def real_graph() -> Graph:
    return Graph.load(REAL_GRAPH, REPO_ROOT)


def test_every_node_has_machine_runnable_verification_including_its_result_check(
    real_graph: Graph,
) -> None:
    for node_id, node in real_graph.nodes.items():
        assert node["verification"], f"{node_id} has no verification"
        for command in node["verification"]:
            assert isinstance(command, list) and command
            assert all(isinstance(item, str) for item in command)
        assert [
            "python3",
            "plans/27_langgraph_curriculum_factory_remediation/tools/validate_result.py",
            "--node",
            node_id,
        ] in node["verification"], f"{node_id} is missing its exact result validation command"


def test_distinct_nodes_never_share_a_write_path(real_graph: Graph) -> None:
    order = real_graph.order()
    for index, left in enumerate(order):
        for right in order[index + 1 :]:
            clashes = [
                (owned, other)
                for owned in real_graph.node(left)["writes"]
                for other in real_graph.node(right)["writes"]
                if paths_overlap(owned, other)
            ]
            assert not clashes, f"{left} and {right} both claim {clashes}"


def test_the_result_schema_is_frozen_before_entry_and_owned_by_no_node(real_graph: Graph) -> None:
    frozen = real_graph.rules["frozen_before_entry"]
    relative = real_graph.data["node_result_schema"]
    assert relative in frozen
    for node_id, node in real_graph.nodes.items():
        for owned in node["writes"]:
            assert not paths_overlap(relative, owned), f"{node_id} claims the frozen schema"


def test_the_admitted_entry_result_still_validates_and_binds_current_bytes(
    real_graph: Graph,
) -> None:
    result = load_node_result(real_graph, "N00_SPEC_APPROVAL_GATE")
    assert result["outcome"] == "PASSED"
    assert result["prompt_sha256"] == real_graph.prompt_digest("N00_SPEC_APPROVAL_GATE")
    assert result["source_spec_sha256"] == real_graph.source_spec_digest()
    for item in result["changed_files"]:
        assert sha256_file(REPO_ROOT / item["path"]) == item["sha256"]
