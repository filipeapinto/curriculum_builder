"""N31 acceptance tests: targeted repair (D17-D21) and unit acceptance (D16, D22, D23).

Ten TEST items from `prompts/N31_repair_acceptance.prompt.v2.md`. Every function
under test is called directly and unmodified from `runtime.langgraph_factory.repair`
/ `acceptance`; TEST 9 additionally calls the real, unmodified
`runtime.langgraph_factory.nodes.terminal.write_terminal` (N22's D98) rather than a
stand-in, and no test in this file writes to `nodes/terminal.py`.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any

try:  # pragma: no cover - environment probe, not behavior
    import langgraph  # noqa: F401
except ModuleNotFoundError as exc:  # pragma: no cover
    raise unittest.SkipTest(
        "plan26 hash-locked environment not installed "
        "(python3 -m pip install --require-hashes -r requirements/plan26.lock): "
        f"{exc}"
    ) from exc

import pytest

from runtime.langgraph_factory import acceptance, repair
from runtime.langgraph_factory import graph as G
from runtime.langgraph_factory import unit_graph as U
from runtime.langgraph_factory.nodes import terminal
from runtime.langgraph_factory.nodes import domain as domain_nodes
from runtime.langgraph_factory.nodes import content as content_nodes
from runtime.langgraph_factory.nodes.domain import DOMAIN_CHECK_IDS
from runtime.langgraph_factory.nodes.content import CONTENT_CHECK_IDS
from runtime.langgraph_factory.nodes import SystemFailure, canonical_digest, stream_id
from runtime.langgraph_factory.state import FIELD_REDUCERS
from runtime.langgraph_factory import reducers as red
from tests.runtime import test_plan26_unit_graph as UG

REPO_ROOT = Path(__file__).resolve().parents[2]

RUN = "run-n31"
EPISODE = "ep-n31"
UNIT = "U001"


@pytest.fixture(scope="module")
def compiled() -> Any:
    output_root = Path(tempfile.mkdtemp(prefix="plan26-n31-"))
    return G.build_curriculum_factory_graph(engine_root=REPO_ROOT, output_root=output_root)


def _apply(state: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    """Merge one node's return value into ``state`` through the real field reducers."""

    merged = dict(state)
    for field, value in update.items():
        merged[field] = FIELD_REDUCERS[field](merged.get(field), value)
    return merged


def _domain_body() -> dict[str, Any]:
    return {
        "unit_id": UNIT,
        "facts": [{"fact_id": "f1", "statement": "a fact"}],
        "verifier_result": {"result": "all_fixtures_behaved"},
    }


def _content_body() -> dict[str, Any]:
    return {
        "unit_id": UNIT,
        "sections": [{"section_id": "s1", "heading": "h", "body": "b"}],
        "claims": [],
        "derivations": [],
    }


def _visuals_body() -> dict[str, Any]:
    return {"unit_id": UNIT}


def _head(version: int, parent_hash: str | None, hash_: str) -> dict[str, Any]:
    return {"version": version, "parent_hash": parent_hash, "hash": hash_}


def _passing_state() -> dict[str, Any]:
    """A unit whose full denominator currently passes (spec section 13.1)."""

    domain_body = _domain_body()
    content_body = _content_body()
    visuals_body = _visuals_body()
    domain_hash = canonical_digest(domain_body)
    content_hash = canonical_digest(content_body)
    visuals_hash = canonical_digest(visuals_body)
    pdf_sha256 = "f" * 64
    page_sha = "a" * 64

    domain_stream = stream_id(UNIT, "domain")
    content_stream = stream_id(UNIT, "content")
    visuals_stream = stream_id(UNIT, "visuals")

    deterministic_checks = [
        {
            "scope": "unit", "owner": UNIT, "head_hash": domain_hash,
            "check_id": check_id, "attempt": 1, "result": "PASS", "detail": {},
        }
        for check_id in DOMAIN_CHECK_IDS
    ] + [
        {
            "scope": "unit", "owner": UNIT, "head_hash": content_hash,
            "check_id": check_id, "attempt": 1, "result": "PASS", "detail": {},
        }
        for check_id in CONTENT_CHECK_IDS
    ]

    review_candidate = {
        "key": "candidate:review-1",
        "record_kind": "model_candidate",
        "pre_admission": True,
        "job_id": "M05_REVIEW_ACTUAL_UNIT",
        "unit_pdf_sha256": pdf_sha256,
        "payload": {
            "overall_findings": [],
            "page_findings": [{"page_number": 1, "page_sha256": page_sha, "findings": []}],
        },
    }

    return {
        "run_id": RUN,
        "episode_id": EPISODE,
        "selected_unit_id": UNIT,
        "effective_run": {"target_closure": [UNIT]},
        "cursor": {"manifest_ordinal": 1, "accepted_ordinal": 0},
        "unit_status": {UNIT: "REVIEWING"},
        "artifact_heads": {
            domain_stream: _head(1, None, domain_hash),
            content_stream: _head(1, None, content_hash),
        },
        "artifact_versions": [
            {"key": f"{domain_stream}@1", "stream": domain_stream, "version": 1, "parent_hash": None, "hash": domain_hash, "body": domain_body},
            {"key": f"{content_stream}@1", "stream": content_stream, "version": 1, "parent_hash": None, "hash": content_hash, "body": content_body},
            {"key": f"{visuals_stream}@1", "stream": visuals_stream, "version": 1, "parent_hash": None, "hash": visuals_hash, "body": visuals_body},
        ],
        "deterministic_checks": deterministic_checks,
        "source_admissions": [{"key": "s1", "unit_id": UNIT, "sha256": "b" * 64}],
        "visual_join_evidence": [{"key": "vje1", "unit_id": UNIT, "phase": "join", "result": "PASS"}],
        "unit_page_inventories": [
            {"key": "inv1", "unit_id": UNIT, "pdf_sha256": pdf_sha256, "page_count": 1, "contiguous": True, "result": "PASS"}
        ],
        "unit_page_inspections": [
            {"key": "insp1", "unit_id": UNIT, "pdf_sha256": pdf_sha256, "page": 1, "page_sha256": page_sha, "problems": [], "result": "PASS"}
        ],
        "unit_reviews": [review_candidate],
        "repair_requests": [],
        "retest_results": [],
        "accepted_unit_receipts": {},
        "evidence_index_entries": [],
        "checkpoint_metadata": [],
        "attempt_counters": {},
    }


# ---------------------------------------------------------------------------
# TEST 1: zero/multiple/unknown/model-selected finding owners fail
# ---------------------------------------------------------------------------


def test_d17_rejects_a_finding_with_no_owner() -> None:
    state = _passing_state()
    state["pending_guard"] = {
        "node": "D08_VALIDATE_DOMAIN", "value": "domain_repairable",
        "detail": {"unit_id": UNIT, "findings": [{"check_id": "x", "pointer": "/facts/0", "message": "m"}]},
    }
    with pytest.raises(SystemFailure):
        repair.D17_CLASSIFY_UNIT_FINDINGS(state, None)


def test_d17_rejects_a_finding_with_an_unknown_owner() -> None:
    state = _passing_state()
    state["pending_guard"] = {
        "node": "D08_VALIDATE_DOMAIN", "value": "domain_repairable",
        "detail": {"unit_id": UNIT, "findings": [{"owner": "mystery owner", "check_id": "x", "pointer": "/facts/0", "message": "m"}]},
    }
    with pytest.raises(SystemFailure):
        repair.D17_CLASSIFY_UNIT_FINDINGS(state, None)


def test_d17_partitions_a_multi_owner_findings_list_into_separate_owner_entries() -> None:
    """A single D08 call can raise findings against two owners; D17 splits them."""

    state = _passing_state()
    state["pending_guard"] = {
        "node": "D08_VALIDATE_DOMAIN", "value": "domain_repairable",
        "detail": {
            "unit_id": UNIT,
            "findings": [
                {"owner": "curriculum domain", "check_id": "domain_schema_valid", "pointer": "/facts/0/statement", "message": "bad schema"},
                {"owner": "source interpretation", "check_id": "domain_facts_sourced", "pointer": "/facts/1", "message": "unsourced"},
            ],
        },
    }
    update = repair.D17_CLASSIFY_UNIT_FINDINGS(state, None)
    owners = {entry["owner"] for entry in update["finding_partitions"]}
    assert owners == {"curriculum domain", "source interpretation"}
    assert update["pending_guard"]["value"] == "partition_complete"


def test_review_finding_category_is_never_trusted_as_an_owner() -> None:
    """A model-selected `category` is mapped through a fixed table; unmapped fails closed."""

    assert repair.owner_for_review_category("visual clarity") == "unit visual"
    assert repair.owner_for_review_category("totally unrelated nonsense") is None

    state = _passing_state()
    state["unit_reviews"][0]["payload"]["overall_findings"] = [
        {"finding_id": "f1", "severity": "blocking", "category": "totally unrelated nonsense",
         "description": "d", "evidence_reference": "/whatever"}
    ]
    with pytest.raises(SystemFailure):
        acceptance.compute_unit_denominator(state, UNIT)


# ---------------------------------------------------------------------------
# TEST 2: local repair changes only named paths/descendants
# ---------------------------------------------------------------------------


def _repair_cycle_state(*, boundary_pointer: str = "/facts/0/statement") -> dict[str, Any]:
    state = _passing_state()
    state["pending_guard"] = {
        "node": "D08_VALIDATE_DOMAIN", "value": "domain_repairable",
        "detail": {
            "unit_id": UNIT,
            "findings": [{"owner": "curriculum domain", "check_id": "domain_schema_valid", "pointer": boundary_pointer, "message": "bad"}],
        },
    }
    state = _apply(state, repair.D17_CLASSIFY_UNIT_FINDINGS(state, None))
    state = _apply(state, repair.D18_PLAN_TARGETED_UNIT_REPAIR(state, None))
    return state


def test_a_correctly_scoped_model_repair_admits() -> None:
    state = _repair_cycle_state()
    request = state["repair_requests"][-1]
    domain_stream = stream_id(UNIT, "domain")
    parent_hash = state["artifact_heads"][domain_stream]["hash"]
    new_body = dict(_domain_body())
    new_body["facts"] = [{"fact_id": "f1", "statement": "corrected statement"}]
    candidate = {
        "key": "candidate:m06-1", "record_kind": "model_candidate", "pre_admission": True,
        "job_id": "M06_REPAIR_NAMED_UNIT_ARTIFACT", "channel": "domain", "unit_id": UNIT,
        "parent_sha256": parent_hash,
        "payload": {
            "candidate_child": {
                "artifact_name": f"domain:{UNIT}", "artifact_body": json.dumps(new_body, sort_keys=True),
                "addressed_finding_ids": request["finding_ids"],
            },
            "changed_path_manifest": [
                {"json_pointer": "/facts/0/statement", "change_kind": "replace", "finding_id": request["finding_ids"][0]}
            ],
        },
    }
    state["artifact_versions"] = state["artifact_versions"] + [candidate]
    update = repair.D20_ADMIT_UNIT_REPAIR(state, None)
    assert update["pending_guard"]["value"] == "repair_admitted"
    assert update["artifact_heads"][domain_stream]["version"] == 2


def test_an_invalid_first_domain_version_repairs_into_a_revalidatable_genesis(
    tmp_path: Path,
) -> None:
    """A failed v1 is immutable evidence, never a head or physical version 1.

    M06 repairs the exact failed bytes; D20 admits the child as genesis while
    retaining separate repair lineage and deterministic schema/source metadata.
    D08 can then revalidate that admitted child without reminting the old M02
    candidate or trusting a model-authored verifier verdict.
    """

    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["unit_id", "facts"],
        "properties": {
            "unit_id": {"const": UNIT},
            "facts": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["fact_id", "statement"],
                    "properties": {
                        "fact_id": {"type": "string"},
                        "statement": {"type": "string", "minLength": 3},
                    },
                },
            },
        },
    }
    schema_path = tmp_path / "domain.schema.json"
    schema_path.write_text(json.dumps(schema), encoding="utf-8")
    for relative in domain_nodes.CURRICULUM_CONTRACTS:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((REPO_ROOT / relative).read_bytes())

    stream = stream_id(UNIT, "domain")
    invalid_body = {"unit_id": UNIT, "facts": [{"fact_id": "f1", "statement": ""}]}
    invalid_hash = canonical_digest(invalid_body)
    invalid_version = {
        "key": "invalid-v1",
        "stream": stream,
        "version": 1,
        "parent_hash": None,
        "hash": invalid_hash,
        "body": invalid_body,
        "schema_path": schema_path.name,
        "evidence_references": [{"source_id": "s1", "source_location": "p.1"}],
        "unit_id": UNIT,
        "channel": "domain",
    }
    state = {
        "run_id": RUN,
        "episode_id": EPISODE,
        "selected_unit_id": UNIT,
        "engine_root": str(tmp_path),
        "effective_run": {
            "unit_records": [{"id": UNIT, "title": "test"}],
            "domain_contract": {"schema": {
                "path": schema_path.name,
                "sha256": hashlib.sha256(schema_path.read_bytes()).hexdigest(),
            }},
        },
        "artifact_heads": {},
        "artifact_versions": [invalid_version],
        "source_admissions": [{"key": "s1", "fact_id": "f1", "unit_id": UNIT}],
        "repair_requests": [],
        "attempt_counters": {},
        "pending_guard": {
            "node": "D08_VALIDATE_DOMAIN",
            "value": "domain_repairable",
            "detail": {
                "unit_id": UNIT,
                "findings": [{
                    "owner": "curriculum domain",
                    "check_id": "domain_schema_valid",
                    "pointer": "/facts/0/statement",
                    "message": "must be non-empty",
                    "parent_hash": invalid_hash,
                }],
            },
        },
    }
    state = _apply(state, repair.D17_CLASSIFY_UNIT_FINDINGS(state, None))
    state = _apply(state, repair.D18_PLAN_TARGETED_UNIT_REPAIR(state, None))
    routed = repair.D19_ROUTE_UNIT_REPAIR(state, None)
    assert routed["pending_guard"]["value"] == "model_repair"
    packet = routed["pending_packet"]["packets"][0]
    assert packet["parent"]["parent_sha256"] == invalid_hash
    assert json.loads(packet["parent"]["artifact_body"]) == invalid_body

    request = state["repair_requests"][-1]
    repaired_body = {
        "unit_id": UNIT,
        "facts": [{"fact_id": "f1", "statement": "corrected"}],
    }
    model_repair = {
        "key": "candidate:m06-preadmission",
        "record_kind": "model_candidate",
        "pre_admission": True,
        "job_id": "M06_REPAIR_NAMED_UNIT_ARTIFACT",
        "channel": "domain",
        "unit_id": UNIT,
        "parent_sha256": invalid_hash,
        "payload": {
            "candidate_child": {
                "artifact_name": f"domain:{UNIT}",
                "artifact_body": json.dumps(repaired_body, sort_keys=True),
                "addressed_finding_ids": request["finding_ids"],
            },
            "changed_path_manifest": [{
                "json_pointer": "/facts/0/statement",
                "change_kind": "replace",
                "finding_id": request["finding_ids"][0],
            }],
        },
    }
    state = _apply(state, routed)
    state["artifact_versions"] = state["artifact_versions"] + [model_repair]
    admitted = repair.D20_ADMIT_UNIT_REPAIR(state, None)
    child = admitted["artifact_versions"][0]
    assert child["version"] == 1
    assert child["parent_hash"] is None
    assert child["repair_parent_hash"] == invalid_hash
    assert child["schema_path"] == schema_path.name
    assert child["evidence_references"] == invalid_version["evidence_references"]

    class PassingVerifier:
        def verify_domain(self, *, body: Any, contract: Any) -> dict[str, Any]:
            return {
                "result": "PASS",
                "candidate_sha256": canonical_digest(body),
                "fixtures_result": "PASS",
                "fixtures": [{"expected": "accept", "returncode": 0}],
                "candidate": {"returncode": 0, "codes": []},
            }

    state = _apply(state, admitted)
    revalidated = domain_nodes.D08_VALIDATE_DOMAIN(
        state,
        SimpleNamespace(transport_registry=PassingVerifier()),
    )
    assert revalidated["pending_guard"]["value"] == "domain_admitted"
    assert revalidated["artifact_heads"][stream]["hash"] == child["hash"]


def test_content_repair_inherits_lineage_and_revalidates_the_exact_head() -> None:
    """D20 retains D09 authority metadata and D09 accepts current-head replay."""

    state = _passing_state()
    domain_stream = stream_id(UNIT, "domain")
    content_stream = stream_id(UNIT, "content")
    domain_hash = state["artifact_heads"][domain_stream]["hash"]
    parent_body = {
        "unit_id": UNIT,
        "sections": [{"section_id": "s1", "heading": "h", "body": "bad"}],
        "evidence_references": [{
            "section_id": "s1", "source_id": "s1", "source_location": "p.1"
        }],
        "visuals": [],
    }
    parent_hash = canonical_digest(parent_body)
    state["engine_root"] = str(REPO_ROOT)
    state["effective_run"] = {"unit_records": [{"id": UNIT, "title": "test"}]}
    state["artifact_heads"][content_stream] = _head(1, None, parent_hash)
    state["artifact_versions"] = [
        record for record in state["artifact_versions"] if record.get("stream") != content_stream
    ] + [{
        "key": "content-parent",
        "stream": content_stream,
        "version": 1,
        "parent_hash": None,
        "hash": parent_hash,
        "body": parent_body,
        "schema_path": "schemas/unit_content.schema.v1.json",
        "domain_hash": domain_hash,
        "unit_id": UNIT,
        "channel": "content",
    }]
    state["pending_guard"] = {
        "node": "D09_VALIDATE_CONTENT",
        "value": "content_repairable",
        "detail": {"unit_id": UNIT, "findings": [{
            "owner": "unit content",
            "check_id": "content_schema_valid",
            "pointer": "/sections/0/body",
            "message": "replace bad body",
            "parent_hash": parent_hash,
        }]},
    }
    state = _apply(state, repair.D17_CLASSIFY_UNIT_FINDINGS(state, None))
    state = _apply(state, repair.D18_PLAN_TARGETED_UNIT_REPAIR(state, None))
    request = state["repair_requests"][-1]
    repaired_body = json.loads(json.dumps(parent_body))
    repaired_body["sections"][0]["body"] = "Corrected content body"
    state["artifact_versions"] += [{
        "key": "candidate:m06-content",
        "record_kind": "model_candidate",
        "job_id": "M06_REPAIR_NAMED_UNIT_ARTIFACT",
        "channel": "content",
        "unit_id": UNIT,
        "parent_sha256": parent_hash,
        "payload": {
            "candidate_child": {
                "artifact_name": f"content:{UNIT}",
                "artifact_body": json.dumps(repaired_body, sort_keys=True),
                "addressed_finding_ids": request["finding_ids"],
            },
            "changed_path_manifest": [{
                "json_pointer": "/sections/0/body",
                "change_kind": "replace",
                "finding_id": request["finding_ids"][0],
            }],
        },
    }]

    admitted = repair.D20_ADMIT_UNIT_REPAIR(state, None)
    child = admitted["artifact_versions"][0]
    assert child["schema_path"] == "schemas/unit_content.schema.v1.json"
    assert child["domain_hash"] == domain_hash

    state = _apply(state, admitted)
    revalidated = content_nodes.D09_VALIDATE_CONTENT(state, None)
    assert revalidated["pending_guard"]["value"] == "content_admitted"
    assert revalidated["artifact_heads"][content_stream]["hash"] == child["hash"]
    assert "artifact_versions" not in revalidated


def test_a_broad_repair_outside_its_boundary_is_refused() -> None:
    state = _repair_cycle_state()
    request = state["repair_requests"][-1]
    domain_stream = stream_id(UNIT, "domain")
    parent_hash = state["artifact_heads"][domain_stream]["hash"]
    new_body = dict(_domain_body())
    # Touches an undeclared pointer (verifier_result) in addition to the named one.
    new_body["facts"] = [{"fact_id": "f1", "statement": "corrected statement"}]
    new_body["verifier_result"] = {"result": "not_run"}
    candidate = {
        "key": "candidate:m06-broad", "record_kind": "model_candidate", "pre_admission": True,
        "job_id": "M06_REPAIR_NAMED_UNIT_ARTIFACT", "channel": "domain", "unit_id": UNIT,
        "parent_sha256": parent_hash,
        "payload": {
            "candidate_child": {
                "artifact_name": f"domain:{UNIT}", "artifact_body": json.dumps(new_body, sort_keys=True),
                "addressed_finding_ids": request["finding_ids"],
            },
            "changed_path_manifest": [
                {"json_pointer": "/facts/0/statement", "change_kind": "replace", "finding_id": request["finding_ids"][0]},
                {"json_pointer": "/verifier_result", "change_kind": "replace", "finding_id": request["finding_ids"][0]},
            ],
        },
    }
    state["artifact_versions"] = state["artifact_versions"] + [candidate]
    with pytest.raises(SystemFailure):
        repair.D20_ADMIT_UNIT_REPAIR(state, None)


def test_an_in_place_no_op_repair_is_refused() -> None:
    state = _repair_cycle_state()
    request = state["repair_requests"][-1]
    domain_stream = stream_id(UNIT, "domain")
    parent_hash = state["artifact_heads"][domain_stream]["hash"]
    unchanged_body = _domain_body()  # identical to parent
    candidate = {
        "key": "candidate:m06-noop", "record_kind": "model_candidate", "pre_admission": True,
        "job_id": "M06_REPAIR_NAMED_UNIT_ARTIFACT", "channel": "domain", "unit_id": UNIT,
        "parent_sha256": parent_hash,
        "payload": {
            "candidate_child": {
                "artifact_name": f"domain:{UNIT}", "artifact_body": json.dumps(unchanged_body, sort_keys=True),
                "addressed_finding_ids": request["finding_ids"],
            },
            "changed_path_manifest": [
                {"json_pointer": "/facts/0/statement", "change_kind": "replace", "finding_id": request["finding_ids"][0]}
            ],
        },
    }
    state["artifact_versions"] = state["artifact_versions"] + [candidate]
    with pytest.raises(SystemFailure):
        repair.D20_ADMIT_UNIT_REPAIR(state, None)


def test_a_stale_parent_repair_is_refused() -> None:
    state = _repair_cycle_state()
    request = state["repair_requests"][-1]
    new_body = dict(_domain_body())
    new_body["facts"] = [{"fact_id": "f1", "statement": "corrected statement"}]
    candidate = {
        "key": "candidate:m06-stale", "record_kind": "model_candidate", "pre_admission": True,
        "job_id": "M06_REPAIR_NAMED_UNIT_ARTIFACT", "channel": "domain", "unit_id": UNIT,
        "parent_sha256": "0" * 64,  # not the current head
        "payload": {
            "candidate_child": {
                "artifact_name": f"domain:{UNIT}", "artifact_body": json.dumps(new_body, sort_keys=True),
                "addressed_finding_ids": request["finding_ids"],
            },
            "changed_path_manifest": [
                {"json_pointer": "/facts/0/statement", "change_kind": "replace", "finding_id": request["finding_ids"][0]}
            ],
        },
    }
    state["artifact_versions"] = state["artifact_versions"] + [candidate]
    with pytest.raises(SystemFailure):
        repair.D20_ADMIT_UNIT_REPAIR(state, None)


def test_a_deterministic_layout_repair_changes_only_its_allowed_pointer() -> None:
    state = _passing_state()
    layout_stream = stream_id(UNIT, "layout")
    layout_body = {"unit_id": UNIT, "template": "v1", "page_count": 1}
    layout_hash = canonical_digest(layout_body)
    state["artifact_versions"] = state["artifact_versions"] + [
        {"key": f"{layout_stream}@1", "stream": layout_stream, "version": 1, "parent_hash": None, "hash": layout_hash, "body": layout_body}
    ]
    state["pending_guard"] = {
        "node": "D14_INVENTORY_AND_INSPECT_UNIT_PAGES", "value": "layout_repairable",
        "detail": {
            "unit_id": UNIT,
            "findings": [{
                "owner": "unit layout", "check_id": "unit_page_inventory", "pointer": "/template",
                "message": "wrong template", "allowed_facts": {"/template": "v2"},
            }],
        },
    }
    state = _apply(state, repair.D17_CLASSIFY_UNIT_FINDINGS(state, None))
    state = _apply(state, repair.D18_PLAN_TARGETED_UNIT_REPAIR(state, None))
    assert state["pending_guard"]["value"] == "repair_planned"
    update = repair.D19_ROUTE_UNIT_REPAIR(state, None)
    assert update["pending_guard"]["value"] == "deterministic_repair"
    candidate = update["artifact_versions"][0]
    assert candidate["body"]["template"] == "v2"
    assert candidate["body"]["page_count"] == 1  # only the named pointer changed
    state = _apply(state, update)
    admitted = repair.D20_ADMIT_UNIT_REPAIR(state, None)
    # layout is append-only versioned, not `artifact_heads`-tracked (matching
    # `review.py`'s own `latest_candidate` convention for this channel).
    assert "artifact_heads" not in admitted
    admitted_versions = [v for v in admitted["artifact_versions"] if v["stream"] == layout_stream]
    assert admitted_versions[0]["version"] == 2
    assert admitted_versions[0]["body"]["template"] == "v2"


# ---------------------------------------------------------------------------
# TEST 3: attempt/repeat bounds stop before an over-bound M06 call
# ---------------------------------------------------------------------------


def test_attempt_bound_exhausts_before_a_fourth_repair_child() -> None:
    state = _passing_state()
    state["attempt_counters"] = {
        f"repair|{UNIT}|curriculum domain|{canonical_digest([repair.finding_fingerprint('curriculum domain', ['/facts/0/statement'], 'bad')])}": repair.MAX_REPAIR_CHILDREN_PER_CHAIN
    }
    state["pending_guard"] = {
        "node": "D08_VALIDATE_DOMAIN", "value": "domain_repairable",
        "detail": {
            "unit_id": UNIT,
            "findings": [{"owner": "curriculum domain", "check_id": "domain_schema_valid", "pointer": "/facts/0/statement", "message": "bad"}],
        },
    }
    state = _apply(state, repair.D17_CLASSIFY_UNIT_FINDINGS(state, None))
    update = repair.D18_PLAN_TARGETED_UNIT_REPAIR(state, None)
    assert update["pending_guard"]["value"] == "convergence_exhausted"
    assert update["terminal_candidate"]["kind"] == "CONVERGENCE_EXHAUSTED"
    assert update["terminal_candidate"]["bound"] == "attempt_bound"


def test_fingerprint_repeat_bound_exhausts_at_d17() -> None:
    state = _passing_state()
    fingerprint = canonical_digest(
        [repair.finding_fingerprint("curriculum domain", ["/facts/0/statement"], "bad")]
    )
    state["attempt_counters"] = {
        f"repeat|{UNIT}|curriculum domain|{fingerprint}": repair.MAX_FINGERPRINT_REPEATS
    }
    state["pending_guard"] = {
        "node": "D08_VALIDATE_DOMAIN", "value": "domain_repairable",
        "detail": {
            "unit_id": UNIT,
            "findings": [{"owner": "curriculum domain", "check_id": "domain_schema_valid", "pointer": "/facts/0/statement", "message": "bad"}],
        },
    }
    update = repair.D17_CLASSIFY_UNIT_FINDINGS(state, None)
    assert update["pending_guard"]["value"] == "convergence_exhausted"
    assert update["terminal_candidate"]["bound"] == "fingerprint_bound"


# ---------------------------------------------------------------------------
# TEST 4: all invalidated descendants retest; stale evidence cannot pass
# ---------------------------------------------------------------------------


def test_d21_dispatches_the_first_retest_node_of_the_owners_fixed_chain() -> None:
    state = _repair_cycle_state()
    state = _apply(state, repair.D19_ROUTE_UNIT_REPAIR(state, None))
    update = repair.D21_RETEST_REQUIRED_DESCENDANTS(state, None)
    assert update["pending_guard"]["value"] == "retest_frontier_incomplete"
    assert update["pending_guard"]["detail"]["destination"] == repair.RETEST_FIRST_NODE["curriculum domain"]
    assert update["retest_results"][0]["dispatched_to"] == "D08_VALIDATE_DOMAIN"


def test_stale_evidence_at_an_old_head_cannot_pass_the_denominator() -> None:
    """A check recorded against a superseded head is invisible to the reduction."""

    state = _passing_state()
    domain_stream = stream_id(UNIT, "domain")
    # Advance the domain head without refreshing its checks: the old checks
    # were recorded against the old (now-stale) head_hash.
    new_hash = canonical_digest({"unit_id": UNIT, "facts": []})
    state["artifact_heads"][domain_stream] = _head(2, state["artifact_heads"][domain_stream]["hash"], new_hash)
    result = acceptance.compute_unit_denominator(state, UNIT)
    assert not result.passed
    assert any(f["owner"] == "curriculum domain" for f in result.findings)


# ---------------------------------------------------------------------------
# TEST 5: removing/failing/staling each acceptance member makes D22 reject
# ---------------------------------------------------------------------------


def test_d22_accepts_a_fully_passing_denominator() -> None:
    state = _passing_state()
    update = acceptance.D22_ACCEPT_UNIT(state, None)
    assert update["pending_guard"]["value"] == "unit_accepted"
    assert UNIT in update["accepted_unit_receipts"]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda s: s.__setitem__("source_admissions", []),
        lambda s: s["deterministic_checks"].__setitem__(0, {**s["deterministic_checks"][0], "result": "FAIL"}),
        lambda s: s.__setitem__("visual_join_evidence", []),
        lambda s: s.__setitem__("unit_page_inspections", []),
        lambda s: s.__setitem__("unit_reviews", []),
    ],
    ids=["source", "domain_check", "visuals", "pages", "review"],
)
def test_removing_or_failing_any_single_member_makes_d22_reject(mutate) -> None:
    state = _passing_state()
    mutate(state)
    with pytest.raises(SystemFailure):
        acceptance.D22_ACCEPT_UNIT(state, None)


def test_staling_the_content_head_makes_d22_reject() -> None:
    state = _passing_state()
    content_stream = stream_id(UNIT, "content")
    new_hash = canonical_digest({"unit_id": UNIT, "sections": []})
    state["artifact_heads"][content_stream] = _head(2, state["artifact_heads"][content_stream]["hash"], new_hash)
    with pytest.raises(SystemFailure):
        acceptance.D22_ACCEPT_UNIT(state, None)


# ---------------------------------------------------------------------------
# TEST 6: accepted bytes remain immutable across resume, later units, and repair
# ---------------------------------------------------------------------------


def test_accept_once_refuses_a_differing_second_write_for_the_same_unit() -> None:
    state = _passing_state()
    # Two independent computations against the same pre-acceptance state (as a
    # crash-before-durable-write replay would see) agree byte-for-byte.
    first = acceptance.D22_ACCEPT_UNIT(state, None)
    second = acceptance.D22_ACCEPT_UNIT(state, None)
    assert first["accepted_unit_receipts"] == second["accepted_unit_receipts"]

    merged = _apply(state, first)
    replayed = red.accept_once(merged["accepted_unit_receipts"], second["accepted_unit_receipts"])
    assert replayed == merged["accepted_unit_receipts"]

    tampered = {UNIT: {**merged["accepted_unit_receipts"][UNIT], "receipt_hash": "deadbeef"}}
    with pytest.raises(red.AcceptOnceConflict):
        red.accept_once(merged["accepted_unit_receipts"], tampered)

    # D22 itself refuses to reconsider a unit its own state already accepted.
    with pytest.raises(SystemFailure):
        acceptance.D22_ACCEPT_UNIT(merged, None)


def test_an_already_accepted_unit_can_never_re_enter_classification_or_planning() -> None:
    state = _passing_state()
    state["accepted_unit_receipts"] = {UNIT: {"receipt_hash": "x" * 64}}
    state["pending_guard"] = {
        "node": "D08_VALIDATE_DOMAIN", "value": "domain_repairable",
        "detail": {"unit_id": UNIT, "findings": [{"owner": "curriculum domain", "check_id": "x", "pointer": "/facts/0", "message": "m"}]},
    }
    with pytest.raises(SystemFailure):
        repair.D17_CLASSIFY_UNIT_FINDINGS(state, None)


# ---------------------------------------------------------------------------
# TEST 7: cursor advances only after checkpoint/evidence/log correlation flush
# ---------------------------------------------------------------------------


def test_d23_writes_checkpoint_metadata_and_cursor_in_the_same_update() -> None:
    state = _passing_state()
    accept_update = acceptance.D22_ACCEPT_UNIT(state, None)
    state = _apply(state, accept_update)
    update = acceptance.D23_CHECKPOINT_ACCEPTED_UNIT(state, None)
    assert "checkpoint_metadata" in update and "cursor" in update
    assert update["cursor"]["accepted_ordinal"] == 1
    assert update["checkpoint_metadata"][0]["checkpoint_id"]
    assert update["accepted_unit_checkpoint_receipts"][0]["checkpoint_id"] == update["checkpoint_metadata"][0]["checkpoint_id"]


def test_d23_refuses_to_advance_the_cursor_with_no_accepted_receipt() -> None:
    state = _passing_state()
    with pytest.raises(SystemFailure):
        acceptance.D23_CHECKPOINT_ACCEPTED_UNIT(state, None)


# ---------------------------------------------------------------------------
# TEST 8: D24-shaped coverage rejects missing/extra/reordered/wrong-hash
# ---------------------------------------------------------------------------


def test_coverage_proof_rejects_missing_extra_reordered_and_wrong_hash() -> None:
    receipts = {
        "U001": {"receipt_hash": "1" * 64},
        "U002": {"receipt_hash": "2" * 64},
    }
    ordered = ["U001", "U002"]
    passed, rejections = acceptance.prove_exact_manifest_coverage(
        ordered, receipts, [{"unit_id": "U001", "receipt_hash": "1" * 64}, {"unit_id": "U002", "receipt_hash": "2" * 64}]
    )
    assert passed and not rejections

    # missing
    passed, rejections = acceptance.prove_exact_manifest_coverage(
        ordered, receipts, [{"unit_id": "U001", "receipt_hash": "1" * 64}]
    )
    assert not passed

    # extra
    passed, rejections = acceptance.prove_exact_manifest_coverage(
        ordered, receipts,
        [{"unit_id": "U001", "receipt_hash": "1" * 64}, {"unit_id": "U002", "receipt_hash": "2" * 64}, {"unit_id": "U003", "receipt_hash": "3" * 64}],
    )
    assert not passed

    # reordered
    passed, rejections = acceptance.prove_exact_manifest_coverage(
        ordered, receipts, [{"unit_id": "U002", "receipt_hash": "2" * 64}, {"unit_id": "U001", "receipt_hash": "1" * 64}]
    )
    assert not passed

    # wrong hash
    passed, rejections = acceptance.prove_exact_manifest_coverage(
        ordered, receipts, [{"unit_id": "U001", "receipt_hash": "0" * 64}, {"unit_id": "U002", "receipt_hash": "2" * 64}]
    )
    assert not passed


# ---------------------------------------------------------------------------
# TEST 9: real D98 traverses one-mode success and unit-failure candidates
# ---------------------------------------------------------------------------


def _d98_projection(state: dict[str, Any]) -> dict[str, Any]:
    from runtime.langgraph_factory.nodes import project

    full = {
        **state,
        "terminal": None,
        "terminal_history": [],
        "mode": "one",
        "requested_unit_id": UNIT,
        "final_release_audits": [],
        "workbook_head": {},
        "failure_fingerprints": [],
        "resume_frontier": None,
        "pending_failure": None,
        "output_root": "/tmp/out",
    }
    return project("D98_WRITE_TERMINAL", full)


def test_a_unit_accepted_candidate_traverses_the_real_d98_and_is_accepted() -> None:
    assert terminal.write_terminal.__module__ == "runtime.langgraph_factory.nodes.terminal"

    state = _passing_state()
    state = _apply(state, acceptance.D22_ACCEPT_UNIT(state, None))
    state = _apply(state, acceptance.D23_CHECKPOINT_ACCEPTED_UNIT(state, None))

    receipt = state["accepted_unit_receipts"][UNIT]
    checkpoint = state["checkpoint_metadata"][-1]
    state["terminal_candidate"] = {
        "kind": "UNIT_ACCEPTED",
        "unit_id": UNIT,
        "receipt_hash": receipt["receipt_hash"],
        "closure_receipt_hashes": {UNIT: receipt["receipt_hash"]},
        "denominator": receipt["denominator"],
        "log_high_water_mark": 0,
        "checkpoint_id": checkpoint["checkpoint_id"],
    }
    projection = _d98_projection(state)
    record = terminal.write_terminal(projection, None)
    assert record["terminal"]["kind"] == "UNIT_ACCEPTED"
    assert record["terminal"]["validation"]["accepted"] is True


def test_a_tampered_unit_accepted_candidate_is_rejected_by_the_real_d98() -> None:
    state = _passing_state()
    state = _apply(state, acceptance.D22_ACCEPT_UNIT(state, None))
    state = _apply(state, acceptance.D23_CHECKPOINT_ACCEPTED_UNIT(state, None))
    receipt = state["accepted_unit_receipts"][UNIT]
    checkpoint = state["checkpoint_metadata"][-1]
    state["terminal_candidate"] = {
        "kind": "UNIT_ACCEPTED",
        "unit_id": UNIT,
        "receipt_hash": "not-the-real-hash",
        "closure_receipt_hashes": {UNIT: receipt["receipt_hash"]},
        "denominator": receipt["denominator"],
        "log_high_water_mark": 0,
        "checkpoint_id": checkpoint["checkpoint_id"],
    }
    projection = _d98_projection(state)
    record = terminal.write_terminal(projection, None)
    assert record["terminal"]["kind"] == "SYSTEM_FAILURE"
    assert record["terminal"]["validation"]["accepted"] is False


def test_a_convergence_exhausted_candidate_from_d17_traverses_the_real_d98() -> None:
    state = _passing_state()
    state["attempt_counters"] = {
        f"repair|{UNIT}|curriculum domain|{canonical_digest([repair.finding_fingerprint('curriculum domain', ['/facts/0/statement'], 'bad')])}": repair.MAX_REPAIR_CHILDREN_PER_CHAIN
    }
    state["pending_guard"] = {
        "node": "D08_VALIDATE_DOMAIN", "value": "domain_repairable",
        "detail": {
            "unit_id": UNIT,
            "findings": [{"owner": "curriculum domain", "check_id": "domain_schema_valid", "pointer": "/facts/0/statement", "message": "bad"}],
        },
    }
    state = _apply(state, repair.D17_CLASSIFY_UNIT_FINDINGS(state, None))
    exhaustion = repair.D18_PLAN_TARGETED_UNIT_REPAIR(state, None)
    candidate = dict(exhaustion["terminal_candidate"])
    state["terminal_candidate"] = candidate
    projection = _d98_projection(state)
    record = terminal.write_terminal(projection, None)
    assert record["terminal"]["kind"] == "CONVERGENCE_EXHAUSTED"
    assert record["terminal"]["validation"]["accepted"] is True


# ---------------------------------------------------------------------------
# TEST 10: crash at every repair/accept/checkpoint/D98 boundary is recoverable
# ---------------------------------------------------------------------------


def test_repeating_d22_after_a_crash_replays_idempotently() -> None:
    """A crash right after D22 returns, before the write is durable, is safe to redo."""

    state = _passing_state()
    first = acceptance.D22_ACCEPT_UNIT(state, None)
    again = acceptance.D22_ACCEPT_UNIT(state, None)
    assert first["accepted_unit_receipts"] == again["accepted_unit_receipts"]
    merged_once = _apply(state, first)
    merged_twice = _apply(merged_once, again)
    assert merged_once["accepted_unit_receipts"] == merged_twice["accepted_unit_receipts"]


def test_repeating_d23_after_a_crash_replays_idempotently() -> None:
    state = _passing_state()
    state = _apply(state, acceptance.D22_ACCEPT_UNIT(state, None))
    first = acceptance.D23_CHECKPOINT_ACCEPTED_UNIT(state, None)
    again = acceptance.D23_CHECKPOINT_ACCEPTED_UNIT(state, None)
    assert first["checkpoint_metadata"] == again["checkpoint_metadata"]
    merged_once = _apply(state, first)
    merged_twice = _apply(merged_once, again)
    assert merged_once["cursor"] == merged_twice["cursor"]


def test_re_admitting_the_same_repair_after_the_head_already_advanced_fails_closed() -> None:
    """A crash between D20's write and the next checkpoint never corrupts the head:
    replaying D20 against the now-advanced head fails closed rather than silently
    re-applying a second, unaccounted-for repair."""

    state = _repair_cycle_state()
    request = state["repair_requests"][-1]
    domain_stream = stream_id(UNIT, "domain")
    parent_hash = state["artifact_heads"][domain_stream]["hash"]
    new_body = dict(_domain_body())
    new_body["facts"] = [{"fact_id": "f1", "statement": "corrected statement"}]
    candidate = {
        "key": "candidate:m06-crash", "record_kind": "model_candidate", "pre_admission": True,
        "job_id": "M06_REPAIR_NAMED_UNIT_ARTIFACT", "channel": "domain", "unit_id": UNIT,
        "parent_sha256": parent_hash,
        "payload": {
            "candidate_child": {
                "artifact_name": f"domain:{UNIT}", "artifact_body": json.dumps(new_body, sort_keys=True),
                "addressed_finding_ids": request["finding_ids"],
            },
            "changed_path_manifest": [
                {"json_pointer": "/facts/0/statement", "change_kind": "replace", "finding_id": request["finding_ids"][0]}
            ],
        },
    }
    state["artifact_versions"] = state["artifact_versions"] + [candidate]
    update = repair.D20_ADMIT_UNIT_REPAIR(state, None)
    state = _apply(state, update)  # the durable, post-crash state
    with pytest.raises(SystemFailure):
        repair.D20_ADMIT_UNIT_REPAIR(state, None)


def test_a_crash_before_the_terminal_write_still_lets_d98_be_invoked_cleanly() -> None:
    state = _passing_state()
    state = _apply(state, acceptance.D22_ACCEPT_UNIT(state, None))
    state = _apply(state, acceptance.D23_CHECKPOINT_ACCEPTED_UNIT(state, None))
    receipt = state["accepted_unit_receipts"][UNIT]
    checkpoint = state["checkpoint_metadata"][-1]
    state["terminal_candidate"] = {
        "kind": "UNIT_ACCEPTED", "unit_id": UNIT, "receipt_hash": receipt["receipt_hash"],
        "closure_receipt_hashes": {UNIT: receipt["receipt_hash"]}, "denominator": receipt["denominator"],
        "log_high_water_mark": 0, "checkpoint_id": checkpoint["checkpoint_id"],
    }
    projection = _d98_projection(state)
    record_a = terminal.write_terminal(projection, None)
    # A crash right after D98 returns but before its write lands: re-deriving the
    # same projection and revalidating produces the byte-identical record.
    record_b = terminal.write_terminal(projection, None)
    assert record_a["terminal"] == record_b["terminal"]


# ==========================================================================
# P-N31-001 required proof: D16-D23 are real, wired members of the one
# production compiled graph (`graph.build_curriculum_factory_graph`), not
# merely function-level tested. Every assertion below runs the real compiled
# graph (`compiled.get_graph()`, `compiled.stream()`/`invoke()`), never a
# declared table alone -- N90's own audit (finding F1) checked exactly this
# way and found D16-D23 unwired; this is what makes that finding closed.
# ==========================================================================


def test_d16_through_d23_and_m06_are_members_of_the_compiled_production_graph(compiled) -> None:
    nodes = set(compiled.get_graph().nodes)
    for node_id in acceptance.UNIT_REPAIR_TOPOLOGY_SOURCES:
        assert node_id in nodes, node_id


def test_binding_inventory_return_value_is_unchanged_by_this_nodes_wiring() -> None:
    """N30's own tests recompute their expectation directly from `binding_
    inventory()`'s return value; P-N31-001 requires that value stay provably
    unchanged even though `build_curriculum_factory_graph` now compiles
    against the wider `unit_repair_binding_inventory()`."""

    narrow = set(G.binding_inventory())
    assert narrow.isdisjoint(acceptance.UNIT_REPAIR_NODE_BODIES)
    widened = set(G.unit_repair_binding_inventory())
    assert widened == narrow | set(acceptance.UNIT_REPAIR_NODE_BODIES)


def test_the_six_n31_owned_deferred_edges_are_now_real_wired_edges(compiled) -> None:
    """Every `unit_graph.DEFERRED_EDGES` row N31 owns is a real compiled edge.

    Not merely absent from a "still deferred" set (the way N30's own frozen
    tests check the *other* rows stay deferred): each row here must appear as
    an actual conditional edge of the real compiled graph.
    """

    owned = [row for row in U.DEFERRED_EDGES if row[3] == "N31_REPAIR_ACCEPTANCE"]
    assert len(owned) == 6

    edges = {(source, target) for source, target, _conditional in G.compiled_topology(compiled)["edges"]}
    for source, _value, destination, _owner in owned:
        assert (source, destination) in edges, (source, destination)


def test_widening_the_bindings_raises_no_topology_or_binding_error(tmp_path) -> None:
    """`validate_bindings`'s placeholder/duplicate/uncallable checks and
    `register_unit_path`'s N30-EDGE-* checks all pass for D16-D23 exactly as
    they already do for the pre-existing skeleton -- proven by actually
    compiling, not by re-reading source."""

    output_root = tmp_path / "widen-check"
    output_root.mkdir()
    compiled = G.build_curriculum_factory_graph(engine_root=REPO_ROOT, output_root=output_root)
    assert "D16_REDUCE_UNIT_EVIDENCE" in set(compiled.get_graph().nodes)


def test_a_clean_one_unit_episode_reaches_d22_accept_unit_via_the_d16_pass_fast_path(
    tmp_path, monkeypatch
) -> None:
    """A real run of the real compiled graph: D16 passes on its first call (no
    repair), and D22/D23 really mint and checkpoint the accepted receipt."""

    fixture = UG._build_episode_fixture(tmp_path)
    result = UG._run_episode(monkeypatch, fixture)

    assert "D16_REDUCE_UNIT_EVIDENCE" in result["trace"]
    assert "D17_CLASSIFY_UNIT_FINDINGS" not in result["trace"]
    assert "D22_ACCEPT_UNIT" in result["trace"]
    assert "D23_CHECKPOINT_ACCEPTED_UNIT" in result["trace"]

    state = result["state"]
    receipt = (state.get("accepted_unit_receipts") or {}).get("U001")
    assert receipt is not None and receipt["receipt_hash"]
    assert state["cursor"]["accepted_ordinal"] == 1


def test_a_full_d17_through_d21_repair_and_retest_loop_reaches_d22_accept_unit(
    tmp_path, monkeypatch
) -> None:
    """A real run of the real compiled graph exercising the other half of D16:
    a deterministic-repair-owned (`unit layout`) finding really traverses
    D17 -> D18 -> D19 -> D20 -> D21 -> the real retest chain back to D16,
    which then passes and really reaches D22/D23.

    The unit's real D14 page inspection finds nothing to repair on its own
    (the test double renders/inspects deterministically and cleanly), so this
    seeds a `layout_repairable` finding onto the checkpoint right after D14's
    own real, clean pass -- the standard "stop the stream, `update_state`,
    resume" technique this file's sibling `test_plan26_unit_graph.py` already
    uses for crash recovery (`test_a_hard_crash_is_recovered_as_an_orphan_
    without_continuing_its_thread`). Everything downstream of that seed is
    then real, unmodified D17-D21/D13-D16/D22/D23 execution over the one real
    compiled graph: the finding is classified for real, D19 dispatches the
    real deterministic route (`unit layout` is `repair.DETERMINISTIC_ONLY_
    OWNERS`), D20 really admits a boundary-checked child, D21 really
    dispatches `D13_RENDER_UNIT` (the retest chain's first node), and the
    real (deterministic, idempotent) test-double renderer/inspector really
    re-runs and passes again, closing the loop back to a real, passing D16.
    """

    fixture = UG._build_episode_fixture(tmp_path)
    lock, invocation, envelope = UG._prepare_episode(fixture)
    context = UG._HarnessContext(fixture["engine"], fixture["output_root"], fixture["sandbox"])
    monkeypatch.setattr(
        G,
        "build_model_node_context",
        lambda _context, **_kwargs: UG._scripted_model_context(fixture["sandbox"]),
    )
    compiled = G.build_curriculum_factory_graph(
        engine_root=fixture["engine"], output_root=fixture["output_root"]
    )

    trace: list[str] = []
    stream = compiled.stream(
        {"invocation": envelope}, config=invocation.config, stream_mode="updates", context=context
    )
    for chunk in stream:
        trace.extend(chunk)
        if "D14_INVENTORY_AND_INSPECT_UNIT_PAGES" in chunk:
            break
    stream.close()

    before = compiled.get_state(invocation.config).values
    assert before["pending_guard"]["node"] == "D14_INVENTORY_AND_INSPECT_UNIT_PAGES"
    assert before["pending_guard"]["value"] == "pages_inspected", (
        "the real page inspection must have really passed cleanly, so the "
        "repair loop below is proven to start from a seeded finding, not a "
        "real product defect this fixture happens to have"
    )

    seeded_finding = {
        "owner": "unit layout",
        "pointer": "/repair_probe",
        "check_id": "unit_page_inventory",
        "message": "N31 required-proof seed: synthetic layout defect",
        "allowed_facts": {"/repair_probe": "synthetic-repair-note"},
    }
    compiled.update_state(
        invocation.config,
        {
            "pending_guard": {
                "node": "D14_INVENTORY_AND_INSPECT_UNIT_PAGES",
                "value": "layout_repairable",
                "detail": {"unit_id": "U001", "findings": [seeded_finding]},
            }
        },
    )

    resumed_trace: list[str] = []
    resumed = compiled.stream(None, config=invocation.config, stream_mode="updates", context=context)
    try:
        for chunk in resumed:
            resumed_trace.extend(chunk)
    except KeyError as error:
        missing = error.args[0] if error.args else None
        declared = {row[2] for row in U.DEFERRED_EDGES}
        if missing not in declared:
            raise
    lock.release()

    # The real repair/retest loop this generation owns, traversed in order.
    loop = (
        "D17_CLASSIFY_UNIT_FINDINGS",
        "D18_PLAN_TARGETED_UNIT_REPAIR",
        "D19_ROUTE_UNIT_REPAIR",
        "D20_ADMIT_UNIT_REPAIR",
        "D21_RETEST_REQUIRED_DESCENDANTS",
        "D13_RENDER_UNIT",
        "D14_INVENTORY_AND_INSPECT_UNIT_PAGES",
        "D16_REDUCE_UNIT_EVIDENCE",
        "D22_ACCEPT_UNIT",
        "D23_CHECKPOINT_ACCEPTED_UNIT",
    )
    positions = [resumed_trace.index(node_id) for node_id in loop]
    assert positions == sorted(positions), resumed_trace
    # A real deterministic repair candidate was admitted, boundary-scoped to
    # exactly the seeded finding's own pointer.
    repair_requests = [
        record for record in compiled.get_state(invocation.config).values.get("repair_requests") or []
        if record.get("owner") == "unit layout"
    ]
    assert repair_requests
    assert repair_requests[-1]["boundary"]["json_pointers"] == ["/repair_probe"]

    final_state = compiled.get_state(invocation.config).values
    receipt = (final_state.get("accepted_unit_receipts") or {}).get("U001")
    assert receipt is not None and receipt["receipt_hash"]
    assert final_state["cursor"]["accepted_ordinal"] == 1
