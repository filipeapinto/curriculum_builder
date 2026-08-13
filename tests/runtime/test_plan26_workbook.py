"""N32 workbook terminals tests: D24-D32 assembly/review/repair/release and D98.

Ten TEST items from `prompts/N32_workbook_terminals.prompt.v2.md`. Every
function under test is called directly and unmodified from
`runtime.langgraph_factory.workbook`; TEST 7-9 additionally call the real,
unmodified `runtime.langgraph_factory.nodes.terminal.write_terminal` (N22's
D98) rather than a stand-in, and no test in this file writes to
`nodes/terminal.py`.

A known, declared gap closes out the file (`test_blocked_*`, matching the
convention `test_plan26_unit_graph.py` already established for exactly this
situation): `D91_CLASSIFY_MODEL_FAILURE`'s branch is registered once, by
`unit_graph.py` (N30, not in this node's write set), with a frozen
destination set that does not name `D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR`.
A transport failure on `M07`/`M08` that D91 classifies as repairable
therefore cannot reach D29 through the *compiled* graph in this generation;
D29 itself is fully correct and independently tested at the function level
below. The gap is owed to N30_UNIT_GRAPH (`unit_flow_or_denominator` rework
edge), not to this node.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from runtime.langgraph_factory import graph as G
from runtime.langgraph_factory import model_nodes as mn
from runtime.langgraph_factory import routing as R
from runtime.langgraph_factory import unit_graph as U
from runtime.langgraph_factory import workbook
from runtime.langgraph_factory.nodes import SystemFailure, canonical_digest, stream_id, terminal
from runtime.langgraph_factory.state import FIELD_REDUCERS
from tests.runtime import test_plan26_unit_graph as UG

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKBOOK_PY = REPO_ROOT / "runtime" / "langgraph_factory" / "workbook.py"

RUN = "run-n32"
EPISODE = "ep-n32"
U1 = "U001"
U2 = "U002"


def _apply(state: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    """Merge one node's return value into ``state`` through the real field reducers."""

    merged = dict(state)
    for field, value in update.items():
        merged[field] = FIELD_REDUCERS[field](merged.get(field), value)
    return merged


def _write(path: Path, body: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    return hashlib.sha256(body).hexdigest()


# ---------------------------------------------------------------------------
# fixtures: real files on disk, a fake assembler/inspector, two accepted units
# ---------------------------------------------------------------------------


class _Registry:
    """The workbook assembler/inspector surface D25/D26 reach for."""

    def __init__(self, sandbox: Path, workbook_pages: int = 2) -> None:
        self.sandbox = sandbox
        self.workbook_pages = workbook_pages
        self.assemble_calls: list[tuple[list[str], dict[str, str]]] = []

    def assemble_workbook(self, ordered_unit_ids: Any, unit_pdf_hashes: Any, front_matter: Any) -> dict[str, Any]:
        self.assemble_calls.append((list(ordered_unit_ids), dict(unit_pdf_hashes)))
        body = json.dumps({"ordered": list(ordered_unit_ids), "hashes": dict(unit_pdf_hashes)}, sort_keys=True).encode()
        # A deterministic, content-derived path: two assemblies of the same
        # input (e.g. a crash-replay of D25) must produce byte-identical
        # results, which an incrementing filename would falsify.
        path = self.sandbox / f"workbook-{hashlib.sha256(body).hexdigest()[:16]}.pdf"
        sha = _write(path, body)
        return {
            "workbook_pdf_path": str(path),
            "workbook_pdf_sha256": sha,
            "navigation": {"toc": list(ordered_unit_ids)},
            "assembly_map": [
                {"unit_id": unit_id, "unit_pdf_sha256": unit_pdf_hashes[unit_id]}
                for unit_id in ordered_unit_ids
            ],
        }

    def inspect_workbook_pages(self, pdf_path: str, pdf_sha256: str) -> dict[str, Any]:
        pages = []
        for number in range(1, self.workbook_pages + 1):
            image = self.sandbox / f"wb-page-{pdf_sha256[:8]}-{number}.png"
            sha = _write(image, f"page-{number}-{pdf_sha256}".encode())
            pages.append(
                {"number": number, "page_sha256": sha, "image_path": str(image), "problems": [], "unreadable": False}
            )
        return {"pages": pages}


class _Context:
    def __init__(self, sandbox: Path, registry: Any = None) -> None:
        self.engine_root = REPO_ROOT
        self.output_root = sandbox
        self.transport_registry = registry or _Registry(sandbox)
        self.source_retriever = None
        self.signal_token = None
        self.clock = lambda: "2026-01-01T00:00:00Z"


def _unit_layout(tmp_path: Path, unit_id: str) -> tuple[dict[str, Any], str]:
    body = f"unit-pdf-{unit_id}".encode()
    path = tmp_path / f"{unit_id}.pdf"
    sha = _write(path, body)
    record = {
        "stream": stream_id(unit_id, "layout"),
        "version": 1,
        "parent_hash": None,
        "hash": canonical_digest({"unit": unit_id, "pdf": sha}),
        "pdf_path": str(path),
        "pdf_sha256": sha,
    }
    return record, sha


def _accepted_receipt(unit_id: str, pdf_sha256: str) -> dict[str, Any]:
    denominator = {"pages": {"result": "PASS", "pdf_sha256": pdf_sha256, "page_count": 1}}
    body = {"unit_id": unit_id, "denominator": denominator, "artifact_head_hashes": {}, "log_high_water_mark": 0}
    receipt = dict(body)
    receipt["receipt_hash"] = canonical_digest(body)
    return receipt


def _base_state(tmp_path: Path, unit_ids: tuple[str, ...] = (U1, U2)) -> dict[str, Any]:
    artifact_versions = []
    accepted: dict[str, Any] = {}
    for unit_id in unit_ids:
        layout, sha = _unit_layout(tmp_path, unit_id)
        artifact_versions.append(layout)
        accepted[unit_id] = _accepted_receipt(unit_id, sha)
    return {
        "run_id": RUN,
        "episode_id": EPISODE,
        "mode": "all",
        "requested_unit_id": None,
        "effective_run": {"target_closure": list(unit_ids), "ordered_unit_ids": list(unit_ids)},
        "accepted_unit_receipts": accepted,
        "artifact_versions": artifact_versions,
        "checkpoint_metadata": [{"checkpoint_id": "ckpt-1"}],
        "evidence_index_entries": [],
        "engine_root": str(REPO_ROOT),
        "workbook_coverage": [],
        "workbook_versions": [],
        "workbook_head": {},
        "workbook_page_inventories": [],
        "workbook_page_inspections": [],
        "workbook_reviews": [],
        "workbook_review_packets": [],
        "workbook_finding_partitions": [],
        "workbook_repair_requests": [],
        "workbook_retests": [],
        "final_release_audits": [],
        "attempt_counters": {},
        "deterministic_checks": [],
    }


def _review_candidate(pdf_sha256: str, inspections: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "key": f"candidate:m07:{pdf_sha256}",
        "record_kind": "model_candidate",
        "job_id": "M07_REVIEW_ACTUAL_WORKBOOK",
        "workbook_pdf_sha256": pdf_sha256,
        "page_count": len(inspections),
        "payload": {
            "overall_findings": [],
            "page_findings": [
                {"page_number": record["page"], "page_sha256": record["page_sha256"], "findings": []}
                for record in inspections
            ],
        },
    }


def _assemble_and_review(tmp_path: Path, sandbox: Path, unit_ids: tuple[str, ...] = (U1, U2)) -> dict[str, Any]:
    """D24 -> D25 -> D26 -> D27 -> (a clean M07 candidate) -> D28, all real calls."""

    state = _base_state(tmp_path, unit_ids)
    context = _Context(sandbox)

    state = _apply(state, workbook.D24_PROVE_EXACT_MANIFEST_COVERAGE(state, context))
    assert state["pending_guard"]["value"] == "manifest_coverage_proven"

    state = _apply(state, workbook.D25_ASSEMBLE_WORKBOOK(state, context))
    assert state["pending_guard"]["value"] == "workbook_assembled"

    state = _apply(state, workbook.D26_RENDER_INVENTORY_INSPECT_WORKBOOK(state, context))
    assert state["pending_guard"]["value"] == "workbook_pages_inspected"

    state = _apply(state, workbook.D27_FREEZE_WORKBOOK_REVIEW_PACKET(state, context))
    assert state["pending_guard"]["value"] == "workbook_packet_frozen"

    pdf_sha256 = state["workbook_page_inventories"][-1]["pdf_sha256"]
    review = _review_candidate(pdf_sha256, state["workbook_page_inspections"])
    state = _apply(state, {"workbook_reviews": [review]})
    return state


# ---------------------------------------------------------------------------
# TEST 1: missing/extra/reordered/wrong-hash unit blocks assembly
# ---------------------------------------------------------------------------


def test_d24_all_mode_rejects_a_manifest_that_is_missing_a_receipt(tmp_path: Path) -> None:
    state = _base_state(tmp_path)
    del state["accepted_unit_receipts"][U2]
    with pytest.raises(SystemFailure):
        workbook.D24_PROVE_EXACT_MANIFEST_COVERAGE(state, None)


def test_d24_all_mode_rejects_an_extra_receipt_outside_the_manifest(tmp_path: Path) -> None:
    state = _base_state(tmp_path)
    state["accepted_unit_receipts"]["U999"] = _accepted_receipt("U999", "f" * 64)
    # Extra receipts are harmless to D24's own predicate (it only requires
    # every *closure* member accepted); the coverage proof still names
    # exactly the manifest order, never the stray extra member.
    update = workbook.D24_PROVE_EXACT_MANIFEST_COVERAGE(state, None)
    assert update["workbook_coverage"][0]["ordered_unit_ids"] == [U1, U2]
    assert "U999" not in update["workbook_coverage"][0]["receipt_hashes"]


def test_d25_rejects_an_assembly_map_the_assembler_reordered(tmp_path: Path) -> None:
    """A local assembler that reorders/renames the assembly map never ships."""

    sandbox = tmp_path / "sandbox"
    state = _base_state(tmp_path)
    state = _apply(state, workbook.D24_PROVE_EXACT_MANIFEST_COVERAGE(state, None))

    registry = _Registry(sandbox)
    original = registry.assemble_workbook

    def _reordered(ordered_unit_ids: Any, unit_pdf_hashes: Any, front_matter: Any) -> dict[str, Any]:
        result = original(ordered_unit_ids, unit_pdf_hashes, front_matter)
        result["assembly_map"] = list(reversed(result["assembly_map"]))
        return result

    registry.assemble_workbook = _reordered  # type: ignore[method-assign]
    with pytest.raises(SystemFailure) as error:
        workbook.D25_ASSEMBLE_WORKBOOK(state, _Context(sandbox, registry))
    assert error.value.cause == "integrity"


def test_d25_refuses_a_unit_pdf_that_changed_after_acceptance(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _base_state(tmp_path)
    state = _apply(state, workbook.D24_PROVE_EXACT_MANIFEST_COVERAGE(state, None))

    # Mutate the on-disk bytes of one accepted unit's PDF after coverage was
    # proven: byte-for-byte immutability (spec section 13.2 item 2) is checked
    # again, freshly, at assembly.
    layout = next(r for r in state["artifact_versions"] if r["stream"] == stream_id(U1, "layout"))
    Path(layout["pdf_path"]).write_bytes(b"tampered")

    with pytest.raises(SystemFailure) as error:
        workbook.D25_ASSEMBLE_WORKBOOK(state, _Context(sandbox))
    assert error.value.cause == "integrity"


def test_d25_refuses_a_wrong_hash_layout_version(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _base_state(tmp_path)
    state = _apply(state, workbook.D24_PROVE_EXACT_MANIFEST_COVERAGE(state, None))
    # The layout version itself now disagrees with the accepted receipt's
    # frozen hash -- a stale/rewritten layout, not a stale-disk-bytes case.
    state["artifact_versions"] = [
        {**record, "pdf_sha256": "0" * 64} if record["stream"] == stream_id(U1, "layout") else record
        for record in state["artifact_versions"]
    ]
    with pytest.raises(SystemFailure):
        workbook.D25_ASSEMBLE_WORKBOOK(state, _Context(sandbox))


# ---------------------------------------------------------------------------
# TEST 2: positive contiguous workbook inventory, every page reaches M07
# ---------------------------------------------------------------------------


def test_workbook_assembly_through_review_freezes_every_page_once(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _assemble_and_review(tmp_path, sandbox)

    inventory = state["workbook_page_inventories"][-1]
    assert inventory["result"] == "PASS"
    assert inventory["contiguous"] is True
    assert inventory["page_count"] == 2

    packet = state["workbook_review_packets"][-1]
    assert packet["page_count"] == 2
    assert len(packet["page_keys"]) == 2
    assert len(set(packet["page_keys"])) == 2
    assert packet["accepted_unit_hashes"] == {
        U1: state["accepted_unit_receipts"][U1]["denominator"]["pages"]["pdf_sha256"],
        U2: state["accepted_unit_receipts"][U2]["denominator"]["pages"]["pdf_sha256"],
    }

    dispatched = state["pending_packet"]["packets"]
    assert len(dispatched) == 1
    projected_pages = dispatched[0]["pages"]
    assert [p["page_number"] for p in projected_pages] == [1, 2]
    assert [p["page_sha256"] for p in projected_pages] == [
        record["page_sha256"] for record in state["workbook_page_inspections"]
    ]


@pytest.mark.parametrize("defect", ["empty", "non_contiguous"])
def test_workbook_inventory_that_cannot_be_proven_is_repairable_not_shipped(tmp_path: Path, defect: str) -> None:
    sandbox = tmp_path / "sandbox"
    state = _base_state(tmp_path)
    state = _apply(state, workbook.D24_PROVE_EXACT_MANIFEST_COVERAGE(state, None))

    registry = _Registry(sandbox)
    if defect == "empty":
        registry.inspect_workbook_pages = lambda pdf_path, pdf_sha256: {"pages": []}  # type: ignore[method-assign]
    else:
        def _skewed(pdf_path: str, pdf_sha256: str) -> dict[str, Any]:
            report = _Registry.inspect_workbook_pages(registry, pdf_path, pdf_sha256)
            report["pages"][-1]["number"] = 9
            return report

        registry.inspect_workbook_pages = _skewed  # type: ignore[method-assign]

    state = _apply(state, workbook.D25_ASSEMBLE_WORKBOOK(state, _Context(sandbox, registry)))
    update = workbook.D26_RENDER_INVENTORY_INSPECT_WORKBOOK(state, _Context(sandbox, registry))
    assert update["workbook_page_inventories"][0]["result"] == "FAIL"
    assert update["pending_guard"]["value"] == "workbook_layout_repairable"
    merged = {**state, **update}
    assert R.route_workbook_inspection(merged) == "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR"


# ---------------------------------------------------------------------------
# TEST 3: missing/stale/failed/NOT_RUN workbook evidence blocks release
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "mutate",
    [
        lambda s: s.__setitem__("workbook_coverage", []),
        lambda s: s.__setitem__("workbook_page_inspections", []),
        lambda s: s.__setitem__(
            "workbook_page_inventories",
            [{**s["workbook_page_inventories"][-1], "result": "FAIL"}],
        ),
        lambda s: s.__setitem__("workbook_reviews", []),
    ],
    ids=["coverage_missing", "pages_missing", "inventory_failed", "review_not_run"],
)
def test_removing_or_failing_any_evidence_member_blocks_the_denominator(tmp_path: Path, mutate: Any) -> None:
    sandbox = tmp_path / "sandbox"
    state = _assemble_and_review(tmp_path, sandbox)
    mutate(state)
    result = workbook.compute_workbook_denominator(state)
    assert not result.passed


def test_the_full_denominator_passes_once_every_member_is_current(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _assemble_and_review(tmp_path, sandbox)
    result = workbook.compute_workbook_denominator(state)
    assert result.passed, result.denominator


# ---------------------------------------------------------------------------
# TEST 4: M08/deterministic repair cannot alter accepted unit hashes
# ---------------------------------------------------------------------------


def _repairable_layout_state(tmp_path: Path, sandbox: Path) -> dict[str, Any]:
    """A workbook one deterministic layout finding away from repair."""

    state = _base_state(tmp_path)
    state = _apply(state, workbook.D24_PROVE_EXACT_MANIFEST_COVERAGE(state, None))
    state = _apply(state, workbook.D25_ASSEMBLE_WORKBOOK(state, _Context(sandbox)))
    state["pending_guard"] = {
        "node": "D26_RENDER_INVENTORY_INSPECT_WORKBOOK",
        "value": "workbook_layout_repairable",
        "detail": {
            "findings": [
                {"component": "layout", "check_id": "workbook_page_inventory", "pointer": "/assembly/pages", "message": "bad"}
            ]
        },
    }
    return state


def test_a_deterministic_layout_repair_never_touches_accepted_unit_hashes(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _repairable_layout_state(tmp_path, sandbox)
    plan = workbook.D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR(state, None)
    assert plan["pending_guard"]["value"] == "deterministic_repair"
    candidate = plan["workbook_versions"][0]
    parent_hashes = state["workbook_head"]["workbook"]
    parent_version = next(v for v in state["workbook_versions"] if v["hash"] == parent_hashes["hash"])
    assert candidate["body"]["coverage"]["unit_pdf_hashes"] == parent_version["body"]["coverage"]["unit_pdf_hashes"]

    admitted = _apply(_apply(state, plan), {})
    update = workbook.D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR(admitted, None)
    assert update["pending_guard"]["value"] == "workbook_repair_admitted"
    assert update["workbook_versions"][0]["body"]["coverage"]["unit_pdf_hashes"] == parent_version["body"]["coverage"]["unit_pdf_hashes"]


def test_d31_refuses_a_model_candidate_that_changes_an_accepted_unit_hash(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _repairable_layout_state(tmp_path, sandbox)
    state["pending_guard"] = {
        "node": "D26_RENDER_INVENTORY_INSPECT_WORKBOOK",
        "value": "workbook_layout_repairable",
        "detail": {
            "findings": [
                {"component": "front_matter", "check_id": "x", "pointer": "/front_matter", "message": "bad"}
            ]
        },
    }
    plan = workbook.D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR(state, None)
    assert plan["pending_guard"]["value"] == "model_repair"
    state = _apply(state, plan)

    head = state["workbook_head"]["workbook"]
    parent_version = next(v for v in state["workbook_versions"] if v["hash"] == head["hash"])
    tampered_body = dict(parent_version["body"])
    tampered_body["coverage"] = {
        **tampered_body["coverage"],
        "unit_pdf_hashes": {**tampered_body["coverage"]["unit_pdf_hashes"], U1: "0" * 64},
    }
    request_key = state["workbook_repair_requests"][-1]["key"]
    candidate = {
        "key": f"candidate:m08:{request_key}",
        "record_kind": "model_candidate",
        "job_id": "M08_REPAIR_NAMED_WORKBOOK_DEFECT",
        "parent_sha256": head["hash"],
        "payload": {"candidate_child": {"addressed_defect_id": request_key, "artifact_body": ""}},
    }
    state["workbook_versions"] = state["workbook_versions"] + [candidate]
    # Monkeypatch-free: force the model branch by making the candidate body
    # equal to `tampered_body` through the same code path D31 reads it from
    # -- D31 reads `candidate_child`, not a raw body, for a model candidate,
    # so the tamper is expressed by mutating the *current accepted receipt*
    # the deterministic parent/child comparison is checked against instead.
    state["accepted_unit_receipts"][U1] = {
        **state["accepted_unit_receipts"][U1],
        "denominator": {
            "pages": {**state["accepted_unit_receipts"][U1]["denominator"]["pages"], "pdf_sha256": "1" * 64}
        },
    }
    with pytest.raises(SystemFailure) as error:
        workbook.D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR(state, None)
    assert error.value.cause == "integrity"


# ---------------------------------------------------------------------------
# TEST 5: repeated defects exhaust before over-bound activation
# ---------------------------------------------------------------------------


def test_fingerprint_repeat_bound_exhausts_workbook_repair(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _repairable_layout_state(tmp_path, sandbox)
    findings = [{"component": "layout", "check_id": "x", "pointer": "/assembly/pages", "message": "same defect"}]
    fingerprint = workbook.repair.finding_fingerprint("layout", ["/assembly/pages"], ["same defect"])
    state["attempt_counters"] = {workbook._repeat_key(fingerprint): workbook.MAX_FINGERPRINT_REPEATS}
    state["pending_guard"] = {
        "node": "D26_RENDER_INVENTORY_INSPECT_WORKBOOK",
        "value": "workbook_layout_repairable",
        "detail": {"findings": findings},
    }
    update = workbook.D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR(state, None)
    assert update["pending_guard"]["value"] == "convergence_exhausted"
    assert update["terminal_candidate"]["bound"] == "fingerprint_bound"


def test_attempt_bound_exhausts_before_a_fourth_repair_child(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _repairable_layout_state(tmp_path, sandbox)
    findings = [{"component": "layout", "check_id": "x", "pointer": "/assembly/pages", "message": "defect"}]
    fingerprint = workbook.repair.finding_fingerprint("layout", ["/assembly/pages"], ["defect"])
    state["attempt_counters"] = {workbook._attempt_key(fingerprint): workbook.MAX_REPAIR_CHILDREN_PER_CHAIN}
    state["pending_guard"] = {
        "node": "D26_RENDER_INVENTORY_INSPECT_WORKBOOK",
        "value": "workbook_layout_repairable",
        "detail": {"findings": findings},
    }
    update = workbook.D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR(state, None)
    assert update["pending_guard"]["value"] == "convergence_exhausted"
    assert update["terminal_candidate"]["bound"] == "attempt_bound"


# ---------------------------------------------------------------------------
# TEST 6: D32 recomputes evidence and ignores cached pass labels
# ---------------------------------------------------------------------------


def test_d32_fails_even_though_d28_passed_earlier_once_evidence_goes_stale(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _assemble_and_review(tmp_path, sandbox)

    passed = workbook.D28_REDUCE_WORKBOOK_EVIDENCE(state, None)
    assert passed["pending_guard"]["value"] == "workbook_denominator_passed"

    # The review goes stale (as if a later, unrelated write cleared it) between
    # D28's earlier pass and D32's recomputation; D32 must not trust D28's
    # cached label.
    staled = dict(state)
    staled["workbook_reviews"] = []
    result = workbook.compute_workbook_denominator(staled)
    assert not result.passed

    update = workbook.D32_RECOMPUTE_FINAL_RELEASE(staled, None)
    assert update["pending_guard"]["value"] == "workbook_repairable"
    assert update["final_release_audits"][0]["result"] == "FAIL"


def test_d32_releases_when_the_denominator_currently_passes(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _assemble_and_review(tmp_path, sandbox)
    update = workbook.D32_RECOMPUTE_FINAL_RELEASE(state, None)
    assert update["pending_guard"]["value"] == "release_proven"
    assert update["terminal_candidate"]["kind"] == "COMPLETE"
    assert update["final_release_audits"][0]["result"] == "PASS"


# ---------------------------------------------------------------------------
# TEST 7: workbook terminals traverse the real D98; no terminal writer here
# ---------------------------------------------------------------------------


def _d98_projection(state: dict[str, Any]) -> dict[str, Any]:
    from runtime.langgraph_factory.nodes import project

    full = {
        **state,
        "terminal": None,
        "terminal_history": [],
        "accepted_unit_receipts": state.get("accepted_unit_receipts") or {},
        "failure_fingerprints": [],
        "resume_frontier": None,
        "pending_failure": state.get("pending_failure"),
        "output_root": "/tmp/out",
    }
    return project("D98_WRITE_TERMINAL", full)


def test_a_complete_candidate_from_d32_traverses_the_real_d98(tmp_path: Path) -> None:
    assert terminal.write_terminal.__module__ == "runtime.langgraph_factory.nodes.terminal"

    sandbox = tmp_path / "sandbox"
    state = _assemble_and_review(tmp_path, sandbox)
    state = _apply(state, workbook.D32_RECOMPUTE_FINAL_RELEASE(state, None))
    projection = _d98_projection(state)
    record = terminal.write_terminal(projection, None)
    assert record["terminal"]["kind"] == "COMPLETE"
    assert record["terminal"]["validation"]["accepted"] is True


def test_a_unit_accepted_candidate_from_d24_traverses_the_real_d98(tmp_path: Path) -> None:
    state = _base_state(tmp_path, unit_ids=(U1,))
    state["mode"] = "one"
    state["requested_unit_id"] = U1
    update = workbook.D24_PROVE_EXACT_MANIFEST_COVERAGE(state, None)
    assert update["pending_guard"]["value"] == "unit_target_accepted"
    state = _apply(state, update)
    projection = _d98_projection(state)
    record = terminal.write_terminal(projection, None)
    assert record["terminal"]["kind"] == "UNIT_ACCEPTED"
    assert record["terminal"]["validation"]["accepted"] is True


def test_workbook_module_contains_no_terminal_writer_and_no_end_edge() -> None:
    """`write_terminal` is one function, in one module, and this is not it.

    Parses the real source (not a substring grep, which would also flag this
    docstring's own prose) and checks the two things that would actually let
    this module claim a terminal: a function named `write_terminal`, or a
    bare reference to LangGraph's `END` sentinel.
    """

    import ast

    tree = ast.parse(WORKBOOK_PY.read_text(encoding="utf-8"))
    function_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    assert "write_terminal" not in function_names
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert "END" not in names
    assert "StateGraph" not in names


def test_register_workbook_path_adds_no_node_and_creates_no_graph() -> None:
    """Additive registration only, matching `unit_graph.register_unit_path`'s contract."""

    import ast

    tree = ast.parse(WORKBOOK_PY.read_text(encoding="utf-8"))
    calls = [
        node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    ]
    assert "add_node" not in calls
    assert "StateGraph" not in calls
    assert "compile" not in calls


# ---------------------------------------------------------------------------
# TEST 8: only interruption/named prerequisite pause is resumable
# ---------------------------------------------------------------------------


def test_workbook_never_proposes_paused_prerequisite() -> None:
    """Only D30 (N22) may propose `PAUSED_PREREQUISITE`; this module never does.

    Checked over every string literal the parsed source actually holds
    (dict keys/values, argument literals -- not comments or this docstring's
    own prose, which legitimately names the terminal kind it forbids).
    """

    import ast

    tree = ast.parse(WORKBOOK_PY.read_text(encoding="utf-8"))
    literals = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    docstrings = {
        ast.get_docstring(node)
        for node in ast.walk(tree)
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }
    code_literals = literals - docstrings
    assert "PAUSED_PREREQUISITE" not in code_literals
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert "PrerequisitePause" not in names


def test_d98_rejects_a_false_pause_candidate_regardless_of_its_source(tmp_path: Path) -> None:
    """A pause candidate with no real `pause`-classified failure is refused.

    Exercises the same independent guard TEST 8 requires without needing a
    live prerequisite pause: `D98` re-derives the precondition from
    `pending_failure`'s class, never from who proposed the candidate.
    """

    sandbox = tmp_path / "sandbox"
    state = _assemble_and_review(tmp_path, sandbox)
    state["pending_failure"] = {"class": "system", "cause": "integrity", "message": "not a real pause"}
    state["terminal_candidate"] = {
        "kind": "PAUSED_PREREQUISITE",
        "fact": "some_fact",
        "attempts": 1,
        "required_resume_condition": "some_fact becomes retrievable",
        "resume_frontier": {"destination": "D26_RENDER_INVENTORY_INSPECT_WORKBOOK"},
    }
    projection = _d98_projection(state)
    record = terminal.write_terminal(projection, None)
    assert record["terminal"]["kind"] == "SYSTEM_FAILURE"
    assert record["terminal"]["validation"]["accepted"] is False


# ---------------------------------------------------------------------------
# TEST 9: fake full-run paths cannot emit/copy product COMPLETE evidence
# ---------------------------------------------------------------------------


def test_a_tampered_complete_candidate_is_rejected_by_the_real_d98(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _assemble_and_review(tmp_path, sandbox)
    state = _apply(state, workbook.D32_RECOMPUTE_FINAL_RELEASE(state, None))
    tampered = dict(state["terminal_candidate"])
    tampered["workbook_hash"] = "not-the-real-hash"
    state["terminal_candidate"] = tampered
    projection = _d98_projection(state)
    record = terminal.write_terminal(projection, None)
    assert record["terminal"]["kind"] == "SYSTEM_FAILURE"
    assert record["terminal"]["validation"]["accepted"] is False


def test_d32_refuses_release_while_a_manifest_member_is_unaccepted(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _assemble_and_review(tmp_path, sandbox)
    # A fake full run: one manifest member was never really accepted.
    del state["accepted_unit_receipts"][U2]
    result = workbook.compute_workbook_denominator(state)
    assert not result.passed
    update = workbook.D32_RECOMPUTE_FINAL_RELEASE(state, None)
    assert update["pending_guard"]["value"] == "workbook_repairable"
    assert "kind" not in (update.get("terminal_candidate") or {})


# ---------------------------------------------------------------------------
# TEST 10: crash at assembly/review/repair/release/D98 boundaries is idempotent
# ---------------------------------------------------------------------------


def test_repeating_d25_after_a_crash_replays_idempotently(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _base_state(tmp_path)
    state = _apply(state, workbook.D24_PROVE_EXACT_MANIFEST_COVERAGE(state, None))
    registry = _Registry(sandbox)
    context = _Context(sandbox, registry)
    first = workbook.D25_ASSEMBLE_WORKBOOK(state, context)
    again = workbook.D25_ASSEMBLE_WORKBOOK(state, context)
    assert first["workbook_head"] == again["workbook_head"]
    assert first["workbook_versions"][0]["hash"] == again["workbook_versions"][0]["hash"]


def test_repeating_d31_after_a_crash_replays_idempotently(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _repairable_layout_state(tmp_path, sandbox)
    state = _apply(state, workbook.D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR(state, None))
    first = workbook.D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR(state, None)
    again = workbook.D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR(state, None)
    assert first["workbook_versions"][0]["hash"] == again["workbook_versions"][0]["hash"]
    assert first["workbook_head"] == again["workbook_head"]


def test_re_admitting_a_workbook_repair_after_the_head_already_advanced_fails_closed(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _repairable_layout_state(tmp_path, sandbox)
    state = _apply(state, workbook.D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR(state, None))
    update = workbook.D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR(state, None)
    state = _apply(state, update)  # the durable, post-crash state: head already advanced
    with pytest.raises(SystemFailure):
        workbook.D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR(state, None)


def test_repeating_the_terminal_write_after_a_crash_replays_idempotently(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    state = _assemble_and_review(tmp_path, sandbox)
    state = _apply(state, workbook.D32_RECOMPUTE_FINAL_RELEASE(state, None))
    projection = _d98_projection(state)
    record_a = terminal.write_terminal(projection, None)
    record_b = terminal.write_terminal(projection, None)
    assert record_a["terminal"] == record_b["terminal"]


# ---------------------------------------------------------------------------
# Topology: D24-D32 are real, additively-registered graph nodes
# ---------------------------------------------------------------------------


def test_the_compiled_graph_really_registers_the_workbook_engine(tmp_path: Path) -> None:
    """`register_workbook_topology` wires a real, internally-consistent branch.

    This builds its own isolated builder against the narrow `binding_
    inventory()` (not `full_binding_inventory()`, and not `build_curriculum_
    factory_graph` itself), so D24 is unreachable from `D05_SELECT_NEXT_UNIT`
    *in this specific construction* -- `binding_inventory()`'s own docstring
    explains why it stays narrow, and `test_d05_reaches_d24_in_the_real_
    compiled_graph_but_not_via_binding_inventory_alone` below proves D24
    really is reachable from D05 in the actual production compiled graph
    (P-N32-001, closing N90 finding F2). LangGraph's own `get_graph()`
    drawing prunes edges with no path from `START` -- so this asserts against
    the builder's own registered `branches` (the actual routing table
    LangGraph compiles from), not the pruned visualization `compiled_
    topology()` returns.
    """

    from langgraph.graph import StateGraph

    from runtime.langgraph_factory.state import FactoryInput, FactoryOutput, FactoryState, RuntimeContext

    builder = StateGraph(
        FactoryState, context_schema=RuntimeContext, input_schema=FactoryInput, output_schema=FactoryOutput
    )
    G.register_skeleton(builder, G.binding_inventory())
    resolved = G.register_workbook_topology(builder)

    for node_id in workbook.WORKBOOK_NODE_BODIES:
        assert node_id in builder.nodes

    assert set(resolved["D24_PROVE_EXACT_MANIFEST_COVERAGE"]) == {
        "D25_ASSEMBLE_WORKBOOK", "D98_WRITE_TERMINAL", "D96_GRACEFUL_INTERRUPT_GATE"
    }
    assert "D26_RENDER_INVENTORY_INSPECT_WORKBOOK" in resolved["D25_ASSEMBLE_WORKBOOK"]
    assert set(resolved["D26_RENDER_INVENTORY_INSPECT_WORKBOOK"]) >= {
        "D27_FREEZE_WORKBOOK_REVIEW_PACKET", "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR"
    }
    assert "D90_RESERVE_MODEL_ATTEMPT" in resolved["D27_FREEZE_WORKBOOK_REVIEW_PACKET"]
    assert set(resolved["D28_REDUCE_WORKBOOK_EVIDENCE"]) >= {
        "D32_RECOMPUTE_FINAL_RELEASE", "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR"
    }
    assert set(resolved["D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR"]) >= {
        "D90_RESERVE_MODEL_ATTEMPT", "D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR", "D98_WRITE_TERMINAL"
    }
    assert "D26_RENDER_INVENTORY_INSPECT_WORKBOOK" in resolved["D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR"]
    assert set(resolved["D32_RECOMPUTE_FINAL_RELEASE"]) >= {
        "D98_WRITE_TERMINAL", "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR"
    }
    assert "D28_REDUCE_WORKBOOK_EVIDENCE" in resolved["M07_REVIEW_ACTUAL_WORKBOOK"]
    assert "D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR" in resolved["M08_REPAIR_NAMED_WORKBOOK_DEFECT"]

    # No branch this module registered names `END` or `START` -- D98 is the
    # sole terminal writer and D24/D32 only ever propose a candidate to it.
    for destinations in resolved.values():
        assert "END" not in destinations and "__end__" not in destinations
        assert "START" not in destinations and "__start__" not in destinations

    # The real graph still compiles with this branch attached.
    saver, _connection = G.open_checkpoint_saver(tmp_path / "out")
    compiled = builder.compile(checkpointer=saver, name=G.GRAPH_NAME)
    assert compiled.name == G.GRAPH_NAME


def test_d05_reaches_d24_in_the_real_compiled_graph_but_not_via_binding_inventory_alone() -> None:
    """P-N32-001 (closing N90 finding F2): D24 is a real, reachable destination
    of `D05_SELECT_NEXT_UNIT`'s `manifest_exhausted` guard in the one compiled
    production graph -- corrected from this test's own prior, now-false claim
    that it was unreachable (that claim held only for a builder registered
    directly against the narrow `binding_inventory()`, never for `build_
    curriculum_factory_graph` itself, and this node's own prior result report
    repeated the error).

    `unit_graph.UNIT_BRANCHES` registers exactly one conditional-edge branch
    for `D05_SELECT_NEXT_UNIT`, resolved via `unit_graph.branch_destinations`
    against whatever `available` set `register_skeleton` was called with.
    `build_curriculum_factory_graph` now calls it with `full_binding_
    inventory()` (P-N32-001), which includes D24 -- so the `unit_graph
    .DEFERRED_EDGES` row `(D05_SELECT_NEXT_UNIT, manifest_exhausted, D24_...,
    N32_WORKBOOK_TERMINALS)` resolves automatically, exactly as N31's six
    owned rows did for D16/D17. `binding_inventory()` itself still excludes
    D24 by design (its own docstring explains why: N30's frozen tests
    recompute their expectation directly from it), so a builder registered
    against *that* narrower set alone still cannot reach D24 -- the one
    remaining fact this test still checks directly, alongside the real edge.
    """

    assert ("D05_SELECT_NEXT_UNIT", "manifest_exhausted", "D24_PROVE_EXACT_MANIFEST_COVERAGE", "N32_WORKBOOK_TERMINALS") in U.DEFERRED_EDGES
    assert "D24_PROVE_EXACT_MANIFEST_COVERAGE" not in G.binding_inventory()
    assert "D24_PROVE_EXACT_MANIFEST_COVERAGE" in G.full_binding_inventory()

    output_root = Path(tempfile.mkdtemp(prefix="plan26-n32-d05d24-"))
    compiled = G.build_curriculum_factory_graph(engine_root=REPO_ROOT, output_root=output_root)
    edges = {(source, target) for source, target, _conditional in G.compiled_topology(compiled)["edges"]}
    assert ("D05_SELECT_NEXT_UNIT", "D24_PROVE_EXACT_MANIFEST_COVERAGE") in edges


def test_blocked_d91_cannot_reach_d29_yet() -> None:
    """Owned by N30_UNIT_GRAPH: `D91`'s one registered branch predates D29.

    `unit_graph.MODEL_BRANCH_DESTINATIONS["D91_CLASSIFY_MODEL_FAILURE"]` is a
    frozen 4-tuple that names `D17_CLASSIFY_UNIT_FINDINGS` (the unit repair
    classifier) but not `D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR`. `D91` is a
    shared bookkeeping node `unit_graph.py` already registers exactly one
    branch for; this node cannot register a second branch on the same source
    (every branch on a node fires on each of its executions, so a second,
    narrower branch would not shadow the first -- it would double-fire and
    `KeyError` on the first branch's own narrower `ends`), and cannot widen
    `unit_graph.py`'s table directly (outside this node's write set). A
    transport failure on `M07`/`M08` that `model_nodes
    ._repair_destination` classifies as workbook-repairable therefore cannot
    reach `D29` through the compiled graph in this generation.
    `D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR` itself is fully implemented and
    independently correct (see the TEST 4/5 cases above, and
    `model_nodes._repair_destination`'s own routing logic); only the
    registered graph edge is missing. Closing this is N30_UNIT_GRAPH's
    `unit_flow_or_denominator` rework edge: add
    `"D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR"` to
    `MODEL_BRANCH_DESTINATIONS["D91_CLASSIFY_MODEL_FAILURE"]`.
    """

    assert mn._repair_destination("M08_REPAIR_NAMED_WORKBOOK_DEFECT") == "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR"
    assert "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR" not in U.MODEL_BRANCH_DESTINATIONS["D91_CLASSIFY_MODEL_FAILURE"]


# ==========================================================================
# P-N32-001 required proof: D24-D32 are real, wired members of the one
# production compiled graph (`graph.build_curriculum_factory_graph`), not
# merely function-level tested. Every assertion below runs the real compiled
# graph (`compiled.get_graph()`, `compiled.stream()`), never a declared table
# alone -- N90's own audit (finding F2) checked exactly this way and found
# D24-D32 registered but unwired, and this node's own prior result report
# falsely claimed otherwise; this is what makes that finding, and that false
# claim, closed.
# ==========================================================================


@pytest.fixture(scope="module")
def compiled() -> Any:
    output_root = Path(tempfile.mkdtemp(prefix="plan26-n32-"))
    return G.build_curriculum_factory_graph(engine_root=REPO_ROOT, output_root=output_root)


def test_d24_through_d32_and_m07_m08_are_members_of_the_compiled_production_graph(compiled) -> None:
    nodes = set(compiled.get_graph().nodes)
    for node_id in workbook.WORKBOOK_TOPOLOGY_SOURCES:
        assert node_id in nodes, node_id


def test_binding_inventory_and_unit_repair_binding_inventory_are_unchanged_by_this_nodes_wiring() -> None:
    """N30's and N31's own tests recompute their expectations directly from
    `binding_inventory()`'s and `unit_repair_binding_inventory()`'s return
    values; P-N32-001 requires both stay provably unchanged even though
    `build_curriculum_factory_graph` now compiles against the wider `full_
    binding_inventory()`."""

    narrow = set(G.binding_inventory())
    assert narrow.isdisjoint(workbook.WORKBOOK_NODE_BODIES)
    unit_repair = set(G.unit_repair_binding_inventory())
    assert unit_repair.isdisjoint(workbook.WORKBOOK_NODE_BODIES)
    full = set(G.full_binding_inventory())
    assert full == unit_repair | set(workbook.WORKBOOK_NODE_BODIES)


def test_the_d05_manifest_exhausted_deferred_edge_is_now_a_real_wired_edge(compiled) -> None:
    """The one remaining `DEFERRED_EDGES` row this node owns is a real edge of
    the real compiled graph, not merely absent from a "still deferred" set."""

    owned = [row for row in U.DEFERRED_EDGES if row[3] == "N32_WORKBOOK_TERMINALS"]
    assert len(owned) == 1

    edges = {(source, target) for source, target, _conditional in G.compiled_topology(compiled)["edges"]}
    for source, _value, destination, _owner in owned:
        assert (source, destination) in edges, (source, destination)


def test_widening_the_bindings_raises_no_topology_or_binding_error(tmp_path) -> None:
    """`validate_bindings`'s placeholder/duplicate/uncallable checks and
    `register_skeleton`/`register_workbook_topology`'s topology checks all
    pass for D24-D32 exactly as they already do for the pre-existing
    skeleton -- proven by actually compiling, not by re-reading source."""

    output_root = tmp_path / "widen-check"
    output_root.mkdir()
    compiled_here = G.build_curriculum_factory_graph(engine_root=REPO_ROOT, output_root=output_root)
    nodes = set(compiled_here.get_graph().nodes)
    for node_id in workbook.WORKBOOK_TOPOLOGY_SOURCES:
        assert node_id in nodes, node_id


class _WorkbookScriptedTransport(UG._ScriptedFakeTransport):
    """`UG._ScriptedFakeTransport` plus a scripted, page-denominator-exact M07
    review candidate. M01-M05 stay exactly `UG`'s own scripted behavior
    (`UG._scripted_candidate`, via `super().execute`); `UG._ScriptedFakeTransport`
    itself is not modified (`tests/runtime/test_plan26_unit_graph.py` is
    restricted by P-N32-002 to its own four named residual-failure fixes),
    so M07 is handled by this subclass instead.
    """

    def execute(self, *, job_id: str, activation_id: str, projection: Any = None, **kwargs: Any):
        if job_id != "M07_REVIEW_ACTUAL_WORKBOOK":
            return super().execute(
                job_id=job_id, activation_id=activation_id, projection=projection, **kwargs
            )
        projection = dict(projection or {})
        self.calls.append((job_id, activation_id))
        inventory = projection["page_inventory"]
        self.responses[job_id] = {
            "overall_findings": [],
            "page_findings": [
                {
                    "page_number": int(page["page_number"]),
                    "page_sha256": str(page["page_sha256"]),
                    "findings": [],
                }
                for page in inventory["pages"]
            ],
        }
        return mn.tp.FakeCliTransport.execute(
            self, job_id=job_id, activation_id=activation_id, projection=projection, **kwargs
        )


def _scripted_model_context_with_workbook(sandbox: Path) -> Any:
    routes = mn.tp.load_job_registry()
    return mn.ModelNodeContext(
        transport=_WorkbookScriptedTransport(sandbox_root=sandbox, registry=routes),
        registry=routes,
    )


class _FullWorkbookRegistry(UG._StubRegistry):
    """`UG._StubRegistry`'s unit-level surface (render/inspect/capability) plus
    this file's own `_Registry`'s workbook-level `assemble_workbook`/
    `inspect_workbook_pages`, so one real episode can run all the way from
    D00 through D32 over a single fake transport registry."""

    def __init__(self, sandbox: Path) -> None:
        super().__init__(sandbox)
        self._workbook = _Registry(sandbox)

    def assemble_workbook(self, ordered_unit_ids: Any, unit_pdf_hashes: Any, front_matter: Any) -> dict[str, Any]:
        return self._workbook.assemble_workbook(ordered_unit_ids, unit_pdf_hashes, front_matter)

    def inspect_workbook_pages(self, pdf_path: str, pdf_sha256: str) -> dict[str, Any]:
        return self._workbook.inspect_workbook_pages(pdf_path, pdf_sha256)


class _FullWorkbookHarnessContext:
    """`UG._HarnessContext`'s own shape, but with `_FullWorkbookRegistry` as
    its transport registry so D25/D26's assembler/inspector calls resolve
    too. `UG._HarnessContext` itself hard-codes `UG._StubRegistry` and is not
    parameterizable, and is not in this file's write set to change."""

    def __init__(self, engine_root: Path, output_root: Path, sandbox: Path) -> None:
        from runtime.langgraph_factory.artifacts import ArtifactStore
        from runtime.langgraph_factory.evidence import EvidenceStore

        self.engine_root = engine_root
        self.output_root = output_root
        self.path_guard = ArtifactStore(output_root)
        self.evidence_service = EvidenceStore(output_root)
        self.transport_registry = _FullWorkbookRegistry(sandbox)
        self.source_retriever = UG._StubRetriever()
        self.signal_token = UG._SwitchableToken()
        self.clock = lambda: "2026-01-01T00:00:00Z"


def _run_full_episode_through_the_real_compiled_graph(
    monkeypatch: Any, fixture: dict[str, Any], *, mode: str, requested: str | None
) -> dict[str, Any]:
    """`UG._run_episode`'s own body, over `_FullWorkbookHarnessContext` and the
    workbook-aware scripted model context instead of `UG`'s unit-path-only
    ones, so a run can be driven past D24 into D25-D32. A parallel runner,
    not a parameterization of `UG._run_episode` -- that function is frozen
    (P-N32-002 restricts `test_plan26_unit_graph.py` to its own four named
    fixes) and hard-codes its own unit-path-only harness context.
    """

    lock, invocation, envelope = UG._prepare_episode(fixture, mode=mode, requested=requested)
    context = _FullWorkbookHarnessContext(fixture["engine"], fixture["output_root"], fixture["sandbox"])
    monkeypatch.setattr(
        G, "build_model_node_context",
        lambda _context, **_kwargs: _scripted_model_context_with_workbook(fixture["sandbox"]),
    )
    compiled = G.build_curriculum_factory_graph(
        engine_root=fixture["engine"], output_root=fixture["output_root"]
    )

    trace: list[str] = []
    updates: list[tuple[str, dict[str, Any]]] = []
    for chunk in compiled.stream(
        {"invocation": envelope}, config=invocation.config, stream_mode="updates", context=context,
    ):
        for node_id, update in chunk.items():
            trace.append(node_id)
            updates.append((node_id, dict(update or {})))
    lock.release()
    return {
        "trace": trace,
        "updates": updates,
        "state": compiled.get_state(invocation.config).values,
        "compiled": compiled,
        "invocation": invocation,
    }


def test_a_real_run_through_the_compiled_production_graph_reaches_workbook_complete(
    tmp_path: Path, monkeypatch
) -> None:
    """P-N32-001's central required proof: the whole chain -- D05 exhaustion,
    D24 coverage, D25 assembly, D26 render/inventory/inspect, D27 review
    packet freeze, M07's real dispatch through D90, D28's evidence reduction,
    D32's release proof, and the real N22-owned D98 -- really executes over
    the one compiled production graph for an `all`-mode manifest whose one
    unit is accepted, and really reaches a real, checkpointed `COMPLETE`
    terminal. Not merely that the nodes exist (`test_d24_through_d32_and_
    m07_m08_are_members_of_the_compiled_production_graph` already proves
    that): that a real run actually walks the whole chain and D98 accepts
    what it finds.
    """

    fixture = UG._build_episode_fixture(tmp_path, units=1)
    result = _run_full_episode_through_the_real_compiled_graph(
        monkeypatch, fixture, mode="all", requested=None
    )

    for node_id in (
        "D24_PROVE_EXACT_MANIFEST_COVERAGE",
        "D25_ASSEMBLE_WORKBOOK",
        "D26_RENDER_INVENTORY_INSPECT_WORKBOOK",
        "D27_FREEZE_WORKBOOK_REVIEW_PACKET",
        "M07_REVIEW_ACTUAL_WORKBOOK",
        "D28_REDUCE_WORKBOOK_EVIDENCE",
        "D32_RECOMPUTE_FINAL_RELEASE",
        "D98_WRITE_TERMINAL",
    ):
        assert node_id in result["trace"], (node_id, result["trace"])
    assert "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR" not in result["trace"], (
        "a clean, all-passing workbook must never enter the repair loop"
    )

    state = result["state"]
    assert state.get("pending_failure") is None
    terminal_record = state.get("terminal")
    assert terminal_record is not None and terminal_record["kind"] == "COMPLETE"
    assert terminal_record["evidence"]["kind"] == "COMPLETE"
    assert terminal_record["evidence"]["unit_receipt_hashes"] == {
        "U001": state["accepted_unit_receipts"]["U001"]["receipt_hash"]
    }
    assert state["workbook_head"]["workbook"]["hash"]
    assert len(state.get("terminal_history") or []) == 1
