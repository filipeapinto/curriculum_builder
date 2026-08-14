"""N23 model node tests (spec 6.3 model job table, spec 9 context isolation)."""
from __future__ import annotations

import ast
import copy
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from runtime.langgraph_factory import model_nodes as mn
from runtime.langgraph_factory import transport as tp
from runtime.langgraph_factory.nodes import terminal as nt
from runtime.langgraph_factory.reducers import (
    DuplicateConflict,
    HeadAdvanceError,
    advance_head,
    append_unique,
    monotonic_max,
    union_disjoint,
)
from runtime.langgraph_factory.state import (
    FACTORY_STATE_FIELDS,
    FIELD_REDUCER_CLASSES,
    RuntimeContext,
)

RUN_ID = "run-plan26-model-nodes"
EPISODE_ID = "ep-n23"
SHA = "0" * 64
CONTENT_HASH = "c" * 64

# Spec section 9's table, transcribed. The test asserts the code equals this, so a
# projection can never quietly widen without this literal transcription changing too.
SPEC_SECTION_9 = {
    "M01_discovery": {
        "included": ("request", "unit", "source_rules", "discovery_authority"),
        "excluded_doc": "sibling requests/units, author history, acceptance, output tree",
    },
    "M01_interpretation": {
        "included": ("request", "unit", "source_rules", "retrieval_group"),
        "excluded_doc": "network/repository access, other retrieval groups, "
                        "routing/acceptance state",
    },
    "M02_domain": {
        "included": ("unit", "admitted_sources", "domain_schema", "domain_config",
                     "verifier_interface", "calibration"),
        "excluded_doc": "content drafts, reviews, sibling units, terminals",
    },
    "M03_content": {
        "included": ("unit", "admitted_domain", "curriculum_contracts",
                     "admitted_evidence_references"),
        "excluded_doc": "rejected domain versions, reviewer history, sibling artifacts, "
                        "acceptance state",
    },
    "M04_visual": {
        "included": ("brief", "permitted_facts", "visual_contract"),
        "excluded_doc": "authoritative circuit/pin/electrical invention, other briefs, "
                        "full state",
    },
    "M05_unit_review": {
        "included": ("unit_artifacts", "unit_pdf", "page_inventory", "pages",
                     "deterministic_evidence", "rubric"),
        "excluded_doc": "author/repair history, prompts/outputs from M01-M04/M06, counters, "
                        "desired verdict",
    },
    "M06_unit_repair": {
        "included": ("owner", "findings", "parent", "boundary", "allowed_facts",
                     "invalidated_descendants", "retest_order"),
        "excluded_doc": "unrelated findings/artifacts, accepted bytes, sibling units, "
                        "routing/terminal state",
    },
    "M07_workbook_review": {
        "included": ("coverage_map", "accepted_unit_hashes", "workbook_pdf",
                     "page_inventory", "pages", "deterministic_evidence", "rubric"),
        "excluded_doc": "author and unit repair history, desired verdict, mutable unit sources",
    },
    "M08_workbook_repair": {
        "included": ("defect", "parent", "allowed_files", "accepted_unit_hashes",
                     "workbook_pdf_hash", "invalidated_descendants", "retest_order"),
        "excluded_doc": "unit content/domain/visual sources, unrelated workbook defects, "
                        "acceptance/terminal authority",
    },
}

EXPECTED_FAMILY = {
    "M01_RESEARCH_UNIT_SOURCES": "anthropic",
    "M02_CREATE_UNIT_DOMAIN_DATA": "anthropic",
    "M03_WRITE_UNIT_CONTENT": "anthropic",
    "M04_CREATE_UNIT_VISUALS": "anthropic",
    "M05_REVIEW_ACTUAL_UNIT": "openai",
    "M06_REPAIR_NAMED_UNIT_ARTIFACT": "anthropic",
    "M07_REVIEW_ACTUAL_WORKBOOK": "openai",
    "M08_REPAIR_NAMED_WORKBOOK_DEFECT": "anthropic",
}


# ------------------------------------------------------------------- transport double


class RecordingTransport:
    """Records every dispatch. Not a graph-buildable transport: only tests hold it."""

    def __init__(self, responses: dict[str, dict[str, Any]],
                 errors: list[Exception] | None = None,
                 observed_family: dict[str, str] | None = None) -> None:
        self.responses = responses
        self.errors = list(errors or [])
        self.observed_family = observed_family or {}
        self.calls: list[dict[str, Any]] = []

    def execute(self, *, job_id: str, activation_id: str, episode_id: str,
                projection: Any, staged_inputs: Any = (), **_: Any) -> tp.TransportResult:
        self.calls.append({"job_id": job_id, "activation_id": activation_id,
                           "episode_id": episode_id, "projection": copy.deepcopy(projection),
                           "staged_inputs": tuple(staged_inputs)})
        if self.errors:
            raise self.errors.pop(0)
        route = tp.resolve_route(job_id)
        receipt = {
            "activation_id": activation_id,
            "job_id": job_id,
            "decided_family": route.family,
            "decided_model": route.model,
            "observed_family": self.observed_family.get(job_id, route.family),
            "observed_model": route.model,
            "outcome": "candidate_produced",
        }
        return tp.TransportResult(candidate=copy.deepcopy(self.responses[job_id]),
                                  receipt=receipt, attempts=(receipt,))


# ------------------------------------------------------------------------- candidates


CANDIDATES: dict[str, dict[str, Any]] = {
    "M01_discovery": {
        "locators": [{"request_id": "REQ-1", "url": "https://example.org/datasheet",
                      "title": "Datasheet", "publisher": "Acme",
                      "locator_kind": "primary", "rationale": "manufacturer document"}],
    },
    "M01_interpretation": {
        "interpretations": [{"request_id": "REQ-1", "retrieval_id": "RET-1",
                             "claims": [{"claim_text": "rated 20 mA",
                                         "source_quote": "20 mA",
                                         "source_location": "p. 2"}],
                             "limitations": []}],
    },
    "M02_CREATE_UNIT_DOMAIN_DATA": {
        "domain_version": {"unit_id": "U01", "fields": {"forward_current_ma": 20},
                           "evidence_references": [{"source_id": "SRC-1",
                                                    "source_location": "p. 2"}]},
    },
    "M03_WRITE_UNIT_CONTENT": {
        "unit_content": {"unit_id": "U01",
                         "sections": [{"section_id": "s1", "heading": "Levers",
                                       "body": "A lever pivots."}],
                         "evidence_references": [{"section_id": "s1", "source_id": "SRC-1",
                                                  "source_location": "p. 2"}]},
    },
    "M04_CREATE_UNIT_VISUALS": {
        "visual_candidate": {"brief_id": "B1", "prompt_text": "a pivoting lever",
                             "dimensions": {"width_px": 1024, "height_px": 768},
                             "image_format": "png",
                             "accessibility_text": "a lever on a fulcrum"},
        "provenance_declaration": {"brief_id": "B1",
                                   "permitted_facts_used": ["a lever pivots"],
                                   "asserts_authoritative_detail": False},
    },
    "M06_REPAIR_NAMED_UNIT_ARTIFACT": {
        "candidate_child": {"artifact_name": "content.json", "artifact_body": "{}",
                            "addressed_finding_ids": ["F1"]},
        "changed_path_manifest": [{"json_pointer": "/sections/0/body",
                                   "change_kind": "replace", "finding_id": "F1"}],
    },
    "M08_REPAIR_NAMED_WORKBOOK_DEFECT": {
        "candidate_child": {"artifact_name": "workbook.typ", "artifact_body": "#set page()",
                            "addressed_defect_id": "D1"},
        "changed_file_manifest": [{"staged_file_name": "navigation.typ",
                                   "change_kind": "replace", "defect_id": "D1"}],
    },
}


def page_hash(number: int) -> str:
    return f"{number:x}" * 64


def review_candidate(page_count: int = 2) -> dict[str, Any]:
    return {
        "overall_findings": [],
        "page_findings": [{"page_number": number, "page_sha256": page_hash(number),
                           "findings": []}
                          for number in range(1, page_count + 1)],
    }


CANDIDATES["M05_REVIEW_ACTUAL_UNIT"] = review_candidate()
CANDIDATES["M07_REVIEW_ACTUAL_WORKBOOK"] = review_candidate()


# ---------------------------------------------------------------------------- packets


def reservation_for(job_id: str, *, correlation_key: str = "corr-1",
                    activation_id: str = "act-1",
                    state: dict[str, Any] | None = None) -> dict[str, Any]:
    update = mn.reserve_model_attempt(state or {}, job_id=job_id,
                                      correlation_key=correlation_key,
                                      activation_id=activation_id)
    return update["pending_guard"]["reservation"]


def correlation(correlation_key: str = "corr-1") -> dict[str, Any]:
    return {"run_id": RUN_ID, "episode_id": EPISODE_ID, "correlation_key": correlation_key}


UNIT = {"unit_id": "U01", "title": "Levers", "objectives": ["explain a lever"]}
SOURCE_RULES = {"primary_source_required": True, "admission_policy": "primary_only"}
REQUEST = {"request_id": "REQ-1", "question": "What is the rated forward current?"}


def packet_for(spec_name: str) -> dict[str, Any]:
    job_id = mn.PROJECTION_SPECS[spec_name].job_id
    base = {"correlation": correlation(),
            "reservation": reservation_for(job_id)}
    if spec_name == "M01_discovery":
        base.update({"phase": "DISCOVER", "request": dict(REQUEST), "unit": dict(UNIT),
                     "source_rules": dict(SOURCE_RULES),
                     "discovery_authority": {"granted": True, "scope": "hosted_discovery"}})
    elif spec_name == "M01_interpretation":
        base.update({"phase": "INTERPRET", "request": dict(REQUEST), "unit": dict(UNIT),
                     "source_rules": dict(SOURCE_RULES),
                     "retrieval_group": {
                         "retrieval_group_hash": SHA,
                         "retrieved_records": [{"retrieval_id": "RET-1", "sha256": SHA,
                                         "content_type": "text/html",
                                         "staged_name": "ret-1.html"}]}})
    elif spec_name == "M02_domain":
        base.update({"unit": dict(UNIT),
                     "admitted_sources": [{"source_id": "SRC-1", "excerpt": "20 mA",
                                           "source_scope": "unit"}],
                     "domain_schema": {"$id": "domain.v1", "type": "object"},
                     "domain_config": {"unit_system": "SI"},
                     "verifier_interface": {"name": "verify_domain",
                                            "signature": "(domain) -> findings"},
                     "calibration": {"fixtures": ["fx-1"]}})
    elif spec_name == "M03_content":
        base.update({"unit": dict(UNIT),
                     "admitted_domain": {"unit_id": "U01", "domain_sha256": SHA,
                                         "fields": {"forward_current_ma": 20}},
                     "curriculum_contracts": {"schema": "unit.v1",
                                              "readability": "grade-6",
                                              "safety": "no live mains"},
                     "admitted_evidence_references": [{"source_id": "SRC-1",
                                                       "source_location": "p. 2"}]})
    elif spec_name == "M04_visual":
        base.update({"brief": {"brief_id": "B1", "unit_id": "U01",
                               "visual_class": "conceptual", "content_hash": CONTENT_HASH,
                               "eligibility": "model_eligible", "authoritative": False,
                               "description": "a lever on a fulcrum"},
                     "permitted_facts": ["a lever pivots"],
                     "visual_contract": {"width_px": 1024, "height_px": 768,
                                         "image_format": "png",
                                         "accessibility": "alt text required"}})
    elif spec_name == "M05_unit_review":
        base.update({"unit_artifacts": {"domain_sha256": SHA, "content_sha256": SHA,
                                        "visual_sha256": [SHA]},
                     "unit_pdf": {"name": "unit.pdf", "sha256": SHA},
                     "page_inventory": page_inventory(2),
                     "pages": page_images(2),
                     "deterministic_evidence": {"checks": [{"check_id": "render",
                                                            "observed": "2 pages"}]},
                     "rubric": {"rubric_sha256": SHA, "criteria": ["legibility"]}})
    elif spec_name == "M06_unit_repair":
        base.update({"owner": "unit_content",
                     "findings": [{"finding_id": "F1", "owner": "unit_content",
                                   "severity": "blocking", "description": "unclear body"}],
                     "parent": {"artifact_name": "content.json", "unit_id": "U01",
                                "channel": "content", "parent_sha256": SHA},
                     "boundary": {"json_pointers": ["/sections/0/body"],
                                  "files": ["content.json"], "region": "section s1"},
                     "allowed_facts": ["a lever pivots"],
                     "invalidated_descendants": ["render", "review"],
                     "retest_order": ["render", "pages", "review"]})
    elif spec_name == "M07_workbook_review":
        base.update({"coverage_map": [{"position": 1, "unit_id": "U01", "unit_sha256": SHA}],
                     "accepted_unit_hashes": {"U01": SHA},
                     "workbook_pdf": {"name": "workbook.pdf", "sha256": SHA},
                     "page_inventory": page_inventory(2),
                     "pages": page_images(2),
                     "deterministic_evidence": {"checks": [{"check_id": "assemble",
                                                            "observed": "2 pages"}]},
                     "rubric": {"rubric_sha256": SHA, "criteria": ["navigation"]}})
    elif spec_name == "M08_workbook_repair":
        base.update({"defect": {"defect_id": "D1", "component": "navigation",
                                "description": "table of contents is stale"},
                     "parent": {"artifact_name": "workbook.typ", "parent_sha256": SHA},
                     "allowed_files": {"files": ["navigation.typ", "front_matter.typ"]},
                     "accepted_unit_hashes": {"U01": SHA},
                     "workbook_pdf_hash": SHA,
                     "invalidated_descendants": ["assemble", "render"],
                     "retest_order": ["assemble", "render", "pages"]})
    else:  # pragma: no cover - the table above is exhaustive
        raise AssertionError(spec_name)
    return base


def page_inventory(count: int) -> dict[str, Any]:
    return {"page_count": count,
            "pages": [{"page_number": number, "page_sha256": page_hash(number)}
                      for number in range(1, count + 1)]}


def page_images(count: int) -> list[dict[str, Any]]:
    return [{"page_number": number, "page_sha256": page_hash(number),
             "image_name": f"page-{number}.png"}
            for number in range(1, count + 1)]


ADAPTER_FOR_SPEC = {
    "M01_discovery": mn.m01_discover_unit_sources,
    "M01_interpretation": mn.m01_interpret_unit_sources,
    "M02_domain": mn.m02_create_unit_domain_data,
    "M03_content": mn.m03_write_unit_content,
    "M04_visual": mn.m04_create_unit_visuals,
    "M05_unit_review": mn.m05_review_actual_unit,
    "M06_unit_repair": mn.m06_repair_named_unit_artifact,
    "M07_workbook_review": mn.m07_review_actual_workbook,
    "M08_workbook_repair": mn.m08_repair_named_workbook_defect,
}


def candidate_for(spec_name: str) -> dict[str, Any]:
    if spec_name.startswith("M01"):
        return copy.deepcopy(CANDIDATES[spec_name])
    return copy.deepcopy(CANDIDATES[mn.PROJECTION_SPECS[spec_name].job_id])


def context_for(spec_name: str, *, candidate: dict[str, Any] | None = None,
                errors: list[Exception] | None = None,
                observed_family: dict[str, str] | None = None,
                ) -> tuple[mn.ModelNodeContext, RecordingTransport]:
    job_id = mn.PROJECTION_SPECS[spec_name].job_id
    payload = candidate if candidate is not None else candidate_for(spec_name)
    transport = RecordingTransport({job_id: payload}, errors=errors,
                                   observed_family=observed_family)
    return mn.ModelNodeContext(transport=transport, registry=tp.load_job_registry()), transport


def run(spec_name: str, *, packet: dict[str, Any] | None = None,
        candidate: dict[str, Any] | None = None,
        errors: list[Exception] | None = None,
        observed_family: dict[str, str] | None = None) -> dict[str, Any]:
    context, _ = context_for(spec_name, candidate=candidate, errors=errors,
                             observed_family=observed_family)
    return ADAPTER_FOR_SPEC[spec_name](packet or packet_for(spec_name), context)


# ==================================================== TEST 1: eight jobs, family split


def test_exactly_eight_model_nodes_and_adapters():
    assert len(mn.MODEL_NODE_IDS) == 8
    assert len(mn.MODEL_NODE_ADAPTERS) == 8
    assert set(mn.MODEL_NODE_ADAPTERS) == set(mn.MODEL_NODE_IDS)
    assert set(mn.MODEL_NODE_IDS) == set(tp.load_job_registry())


def test_family_split_matches_the_frozen_registry():
    registry = tp.load_job_registry()
    assert mn.MODEL_NODE_FAMILIES == EXPECTED_FAMILY
    for job_id, family in EXPECTED_FAMILY.items():
        assert registry[job_id].family == family
        assert registry[job_id].cli == ("codex" if family == "openai" else "claude")
    claude = {job for job, family in EXPECTED_FAMILY.items() if family == "anthropic"}
    codex = {job for job, family in EXPECTED_FAMILY.items() if family == "openai"}
    assert claude == {"M01_RESEARCH_UNIT_SOURCES", "M02_CREATE_UNIT_DOMAIN_DATA",
                      "M03_WRITE_UNIT_CONTENT", "M04_CREATE_UNIT_VISUALS",
                      "M06_REPAIR_NAMED_UNIT_ARTIFACT",
                      "M08_REPAIR_NAMED_WORKBOOK_DEFECT"}
    assert codex == {"M05_REVIEW_ACTUAL_UNIT", "M07_REVIEW_ACTUAL_WORKBOOK"}


def test_a_projection_exists_for_every_job_and_both_m01_phases():
    assert set(mn.PROJECTION_SPECS) == set(SPEC_SECTION_9)
    covered = {spec.job_id for spec in mn.PROJECTION_SPECS.values()}
    assert covered == set(mn.MODEL_NODE_IDS)
    m01 = [name for name, spec in mn.PROJECTION_SPECS.items()
           if spec.job_id == "M01_RESEARCH_UNIT_SOURCES"]
    assert sorted(m01) == ["M01_discovery", "M01_interpretation"]


def test_build_model_nodes_registers_exactly_eight_callables(tmp_path):
    context = mn.build_test_model_node_context(
        sandbox_root=tmp_path, responses={"M03_WRITE_UNIT_CONTENT":
                                          CANDIDATES["M03_WRITE_UNIT_CONTENT"]})
    nodes = mn.build_model_nodes(context)
    assert sorted(nodes) == sorted(mn.MODEL_NODE_IDS)
    assert all(callable(node) for node in nodes.values())


# ============================================ TEST 2: projections equal spec section 9


@pytest.mark.parametrize("spec_name", sorted(SPEC_SECTION_9))
def test_every_projection_equals_the_spec_section_9_row(spec_name):
    spec = mn.PROJECTION_SPECS[spec_name]
    expected = SPEC_SECTION_9[spec_name]
    assert spec.allowed == expected["included"]
    assert spec.excluded_doc == expected["excluded_doc"]
    projection = mn.build_projection(spec_name, packet_for(spec_name))
    assert set(projection) <= set(spec.allowed)
    assert set(spec.required) <= set(projection)


@pytest.mark.parametrize("spec_name", sorted(SPEC_SECTION_9))
def test_a_poisoned_full_state_cannot_widen_any_projection(spec_name):
    """Handing a builder the whole state must not leak one field past its allowlist."""

    poisoned: dict[str, Any] = {field: {"leaked": field} for field in FACTORY_STATE_FIELDS}
    poisoned["desired_verdict"] = "ACCEPT"
    poisoned["author_history"] = ["M03 wrote this"]
    poisoned["sibling_units"] = ["U02", "U03"]
    poisoned.update(packet_for(spec_name))

    spec = mn.PROJECTION_SPECS[spec_name]
    projection = mn.build_projection(spec_name, poisoned)
    assert set(projection) <= set(spec.allowed)
    leaked = mn._collect_keys(projection) & (set(FACTORY_STATE_FIELDS) | spec.denied)
    assert leaked == set(), f"{spec_name} leaked {sorted(leaked)}"
    assert "ACCEPT" not in mn._collect_values(projection)


@pytest.mark.parametrize("spec_name", sorted(SPEC_SECTION_9))
def test_every_projection_is_control_field_free(spec_name):
    projection = mn.build_projection(spec_name, packet_for(spec_name))
    tp.assert_no_authoritative_fields(projection, label=spec_name)


def test_a_nested_desired_verdict_is_rejected_for_a_review():
    packet = packet_for("M05_unit_review")
    packet["rubric"] = {**packet["rubric"], "desired_verdict": "ACCEPT"}
    with pytest.raises(mn.ProjectionViolation, match="structurally excluded"):
        mn.build_projection("M05_unit_review", packet)


def test_a_review_projection_cannot_carry_author_or_counter_history():
    for poison in ({"author_history": ["M03"]}, {"attempt_count": 2},
                   {"prior_findings": ["F1"]}):
        packet = packet_for("M07_workbook_review")
        packet["deterministic_evidence"] = {**packet["deterministic_evidence"], **poison}
        with pytest.raises(mn.ProjectionViolation):
            mn.build_projection("M07_workbook_review", packet)


def test_m01_discovery_and_interpretation_are_distinct_projections():
    discovery = mn.build_projection("M01_discovery", packet_for("M01_discovery"))
    interpretation = mn.build_projection("M01_interpretation",
                                         packet_for("M01_interpretation"))
    assert "discovery_authority" in discovery and "retrieval_group" not in discovery
    assert "retrieval_group" in interpretation
    assert "discovery_authority" not in interpretation
    assert ADAPTER_FOR_SPEC["M01_discovery"] is not ADAPTER_FOR_SPEC["M01_interpretation"]


def test_an_interpretation_packet_may_not_smuggle_discovery_authority():
    """The allowlist is the mechanism: an unlisted key is never copied, not filtered."""

    packet = packet_for("M01_interpretation")
    packet["discovery_authority"] = {"granted": True, "scope": "hosted_discovery"}
    projection = mn.build_projection("M01_interpretation", packet)
    assert "discovery_authority" not in projection
    assert "hosted_discovery" not in mn._collect_values(projection)

    packet["retrieval_group"] = {**packet["retrieval_group"],
                                 "discovery_authority": {"granted": True}}
    with pytest.raises(mn.ProjectionViolation, match="structurally excluded"):
        mn.build_projection("M01_interpretation", packet)


def test_m01_phase_selection_reads_the_explicit_packet_phase():
    context, transport = context_for("M01_discovery")
    update = mn.m01_research_unit_sources(packet_for("M01_discovery"), context)
    assert "source_discoveries" in update
    assert transport.calls[0]["projection"].keys() == {
        "request", "unit", "source_rules", "discovery_authority"}
    with pytest.raises(mn.ProjectionViolation, match="phase"):
        mn.m01_research_unit_sources({"phase": "GUESS"}, context)


def test_m01_output_schema_carries_no_top_level_combinator_the_real_api_rejects():
    """N70 live-verified defect: Claude's tool-use API rejects `oneOf`/`allOf`/`anyOf`
    at a `--json-schema` tool's document root ('input_schema does not support oneOf,
    allOf, or anyOf at the top level') -- confirmed live, 5/5 reproductions, against
    the real M01 schema before this fix, and 0/5 after replacing the top-level
    `oneOf` with an equivalent `if`/`then`/`else`. Every M01 discovery/interpretation
    call in the one real production unit run this whole lineage has ever attempted
    hit this identically; the graph's own retry/exhaustion machinery worked exactly
    as designed and still could not route around a schema the API would never accept.
    This is a static, cheap proxy for that live proof: no job schema may carry a
    top-level combinator, ever, regardless of which job it belongs to.
    """
    route = tp.resolve_route("M01_RESEARCH_UNIT_SOURCES")
    schema = tp.load_output_schema(route)
    assert not any(key in schema for key in ("oneOf", "allOf", "anyOf"))


def test_m01_schema_still_enforces_exactly_one_of_locators_or_interpretations():
    """The `if`/`then`/`else` replacement must be a semantically exact substitute for
    the retired top-level `oneOf`, not a weakening: locators-only and
    interpretations-only both validate; neither, and both together, must still fail.
    """
    route = tp.resolve_route("M01_RESEARCH_UNIT_SOURCES")
    schema = tp.load_output_schema(route)
    validator = jsonschema.Draft202012Validator(schema)

    locator = {"request_id": "r1", "url": "https://example.com", "title": "t",
               "publisher": "p", "locator_kind": "primary", "rationale": "why"}
    interpretation = {"request_id": "r1", "retrieval_id": "ret-1",
                       "claims": [{"claim_text": "c", "source_quote": "q",
                                   "source_location": "p.1"}], "limitations": []}

    assert validator.is_valid({"locators": [locator]})
    assert validator.is_valid({"interpretations": [interpretation]})
    assert not validator.is_valid({})
    assert not validator.is_valid({"locators": [locator], "interpretations": [interpretation]})


def test_m04_refuses_an_authoritative_brief():
    for poison in ({"authoritative": True}, {"visual_class": "circuit"},
                   {"visual_class": "pinout"}, {"eligibility": "deterministic_only"}):
        packet = packet_for("M04_visual")
        packet["brief"] = {**packet["brief"], **poison}
        context, transport = context_for("M04_visual")
        with pytest.raises(mn.ProjectionViolation):
            mn.m04_create_unit_visuals(packet, context)
        assert transport.calls == []


def test_a_staged_input_the_projection_never_names_is_refused():
    packet = packet_for("M05_unit_review")
    packet["staged_inputs"] = [{"name": "sibling-unit.pdf", "source_path": "/tmp/x",
                                "sha256": SHA}]
    context, transport = context_for("M05_unit_review")
    with pytest.raises(mn.ProjectionViolation, match="not declared by the projection"):
        mn.m05_review_actual_unit(packet, context)
    assert transport.calls == []


# ================================= TEST 3: output schemas reject control/undeclared/broad


@pytest.mark.parametrize("job_id", sorted(EXPECTED_FAMILY))
def test_every_job_schema_is_closed_and_control_free(job_id):
    schema = tp.load_output_schema(tp.resolve_route(job_id))
    assert schema["additionalProperties"] is False
    tp.assert_no_authoritative_fields(schema, label=job_id)


def test_the_frozen_schema_rejects_a_terminal_field(tmp_path):
    poisoned = {**CANDIDATES["M03_WRITE_UNIT_CONTENT"], "terminal": "UNIT_ACCEPTED"}
    fake = tp.FakeCliTransport(sandbox_root=tmp_path,
                               responses={"M03_WRITE_UNIT_CONTENT": poisoned})
    with pytest.raises(jsonschema.ValidationError):
        fake.execute(job_id="M03_WRITE_UNIT_CONTENT", activation_id="act-1")


@pytest.mark.parametrize("field", ["terminal", "next_node", "accept", "verdict", "route"])
def test_the_adapter_rejects_an_injected_control_field(field):
    poisoned = {**CANDIDATES["M03_WRITE_UNIT_CONTENT"], field: "COMPLETE"}
    update = run("M03_content", candidate=poisoned)
    assert "artifact_versions" not in update
    assert update["pending_failure"]["failure_class"] == "candidate_control_field"


def test_the_adapter_closes_the_one_object_the_schema_leaves_open():
    """`M02.domain_version.fields` is free-form in N13's schema; the adapter still closes it."""

    schema = tp.load_output_schema(tp.resolve_route("M02_CREATE_UNIT_DOMAIN_DATA"))
    fields_schema = schema["properties"]["domain_version"]["properties"]["fields"]
    assert fields_schema["additionalProperties"] is True  # the disclosed N13 schema gap

    poisoned = copy.deepcopy(CANDIDATES["M02_CREATE_UNIT_DOMAIN_DATA"])
    poisoned["domain_version"]["fields"] = {"terminal": "UNIT_ACCEPTED"}
    jsonschema.Draft202012Validator(schema).validate(poisoned)  # schema alone admits it

    update = run("M02_domain", candidate=poisoned)
    assert "artifact_versions" not in update
    assert update["pending_failure"]["failure_class"] == "candidate_control_field"


def test_n13_still_rejects_the_open_object_at_its_own_parse_boundary(tmp_path):
    """The schema gap is not an escape: N13 rejects the same candidate before N23 sees it."""

    poisoned = copy.deepcopy(CANDIDATES["M02_CREATE_UNIT_DOMAIN_DATA"])
    poisoned["domain_version"]["fields"] = {"terminal": "UNIT_ACCEPTED"}
    fake = tp.FakeCliTransport(sandbox_root=tmp_path,
                               responses={"M02_CREATE_UNIT_DOMAIN_DATA": poisoned})
    with pytest.raises(tp.TransportError, match="control-plane fields"):
        fake.execute(job_id="M02_CREATE_UNIT_DOMAIN_DATA", activation_id="act-1")


def test_undeclared_artifacts_are_rejected():
    cases = {
        "M01_discovery": ("locators", 0, "request_id", "REQ-OTHER"),
        "M01_interpretation": ("interpretations", 0, "retrieval_id", "RET-OTHER"),
    }
    for spec_name, (channel, index, field, value) in cases.items():
        candidate = candidate_for(spec_name)
        candidate[channel][index][field] = value
        update = run(spec_name, candidate=candidate)
        assert update["pending_failure"]["failure_class"] == "candidate_undeclared_artifact"

    domain = candidate_for("M02_domain")
    domain["domain_version"]["evidence_references"][0]["source_id"] = "SRC-UNADMITTED"
    assert run("M02_domain", candidate=domain)["pending_failure"]["failure_class"] == \
        "candidate_undeclared_artifact"

    content = candidate_for("M03_content")
    content["unit_content"]["evidence_references"][0]["section_id"] = "s-unknown"
    assert run("M03_content", candidate=content)["pending_failure"]["failure_class"] == \
        "candidate_undeclared_artifact"

    visual = candidate_for("M04_visual")
    visual["provenance_declaration"]["permitted_facts_used"] = ["an undeclared fact"]
    assert run("M04_visual", candidate=visual)["pending_failure"]["failure_class"] == \
        "candidate_undeclared_artifact"


def test_a_model_visual_may_not_assert_authoritative_detail():
    visual = candidate_for("M04_visual")
    visual["provenance_declaration"]["asserts_authoritative_detail"] = True
    update = run("M04_visual", candidate=visual)
    assert "visual_results" not in update
    assert update["pending_failure"]["failure_class"] == "candidate_authoritative_visual"


def test_m06_rejects_a_pointer_outside_the_declared_boundary():
    candidate = candidate_for("M06_unit_repair")
    candidate["changed_path_manifest"] = [{"json_pointer": "/sections/1/heading",
                                           "change_kind": "replace", "finding_id": "F1"}]
    update = run("M06_unit_repair", candidate=candidate)
    assert "artifact_versions" not in update
    assert update["pending_failure"]["failure_class"] == "candidate_boundary_violation"


def test_m06_rejects_an_unnamed_finding_and_a_renamed_artifact():
    candidate = candidate_for("M06_unit_repair")
    candidate["candidate_child"]["addressed_finding_ids"] = ["F-OTHER"]
    assert run("M06_unit_repair", candidate=candidate)["pending_failure"]["failure_class"] \
        == "candidate_boundary_violation"

    candidate = candidate_for("M06_unit_repair")
    candidate["candidate_child"]["artifact_name"] = "domain.json"
    assert run("M06_unit_repair", candidate=candidate)["pending_failure"]["failure_class"] \
        == "candidate_boundary_violation"


def test_m06_refuses_findings_spanning_more_than_one_owner():
    packet = packet_for("M06_unit_repair")
    packet["findings"] = packet["findings"] + [{"finding_id": "F2", "owner": "unit_domain",
                                                "severity": "major", "description": "x"}]
    context, transport = context_for("M06_unit_repair")
    with pytest.raises(mn.RepairBoundaryViolation, match="span owners"):
        mn.m06_repair_named_unit_artifact(packet, context)
    assert transport.calls == []


def test_m06_refuses_an_empty_boundary():
    packet = packet_for("M06_unit_repair")
    packet["boundary"] = {"json_pointers": [], "files": []}
    context, transport = context_for("M06_unit_repair")
    with pytest.raises(mn.RepairBoundaryViolation, match="non-empty"):
        mn.m06_repair_named_unit_artifact(packet, context)
    assert transport.calls == []


def test_m08_rejects_a_file_outside_the_declared_boundary():
    candidate = candidate_for("M08_workbook_repair")
    candidate["changed_file_manifest"] = [{"staged_file_name": "unit_U01_content.typ",
                                           "change_kind": "replace", "defect_id": "D1"}]
    update = run("M08_workbook_repair", candidate=candidate)
    assert "workbook_versions" not in update
    assert update["pending_failure"]["failure_class"] == "candidate_boundary_violation"


def test_m08_refuses_a_unit_owned_defect():
    packet = packet_for("M08_workbook_repair")
    packet["defect"] = {**packet["defect"], "component": "unit_content"}
    context, transport = context_for("M08_workbook_repair")
    with pytest.raises(mn.RepairBoundaryViolation, match="not workbook-owned"):
        mn.m08_repair_named_workbook_defect(packet, context)
    assert transport.calls == []


def test_m08_rejects_a_child_addressing_another_defect():
    candidate = candidate_for("M08_workbook_repair")
    candidate["candidate_child"]["addressed_defect_id"] = "D2"
    assert run("M08_workbook_repair", candidate=candidate)["pending_failure"][
        "failure_class"] == "candidate_boundary_violation"


# ======================== TEST 4: M05/M07 exact page denominator and different family


@pytest.mark.parametrize("spec_name", ["M05_unit_review", "M07_workbook_review"])
@pytest.mark.parametrize("mutation", ["missing_page", "extra_page", "duplicate_page",
                                      "zero_pages", "wrong_hash"])
def test_review_packets_require_the_exact_frozen_page_denominator(spec_name, mutation):
    packet = packet_for(spec_name)
    if mutation == "missing_page":
        packet["pages"] = packet["pages"][:1]
    elif mutation == "extra_page":
        packet["pages"] = packet["pages"] + [{"page_number": 3,
                                              "page_sha256": page_hash(3),
                                              "image_name": "page-3.png"}]
    elif mutation == "duplicate_page":
        packet["pages"] = packet["pages"] + [dict(packet["pages"][0])]
    elif mutation == "zero_pages":
        packet["page_inventory"] = {"page_count": 0, "pages": []}
    else:
        packet["pages"][1]["page_sha256"] = "f" * 64

    context, transport = context_for(spec_name)
    with pytest.raises(mn.PageDenominatorViolation):
        ADAPTER_FOR_SPEC[spec_name](packet, context)
    assert transport.calls == []


@pytest.mark.parametrize("spec_name", ["M05_unit_review", "M07_workbook_review"])
@pytest.mark.parametrize("mutation", ["missing_finding", "extra_finding",
                                      "duplicate_finding", "wrong_page_hash"])
def test_review_findings_must_cover_every_page_exactly(spec_name, mutation):
    candidate = review_candidate(2)
    if mutation == "missing_finding":
        candidate["page_findings"] = candidate["page_findings"][:1]
    elif mutation == "extra_finding":
        candidate["page_findings"].append({"page_number": 3, "page_sha256": page_hash(3),
                                           "findings": []})
    elif mutation == "duplicate_finding":
        candidate["page_findings"].append(dict(candidate["page_findings"][0]))
    else:
        candidate["page_findings"][1]["page_sha256"] = "f" * 64

    update = run(spec_name, candidate=candidate)
    channel = "unit_reviews" if spec_name == "M05_unit_review" else "workbook_reviews"
    assert channel not in update
    assert update["pending_failure"]["failure_class"] == "candidate_page_denominator"


@pytest.mark.parametrize("spec_name", ["M05_unit_review", "M07_workbook_review"])
def test_a_review_executing_in_the_authoring_family_is_a_system_fault(spec_name):
    job_id = mn.PROJECTION_SPECS[spec_name].job_id
    with pytest.raises(mn.FamilyViolation, match="authoring family"):
        run(spec_name, observed_family={job_id: tp.AUTHORING_FAMILY})


@pytest.mark.parametrize("job_id", ["M05_REVIEW_ACTUAL_UNIT", "M07_REVIEW_ACTUAL_WORKBOOK"])
def test_n13_identity_primitive_also_rejects_the_authoring_family(job_id):
    route = tp.resolve_route(job_id)
    assert route.is_review
    observed = tp.ObservedIdentity(model=route.model, family=tp.AUTHORING_FAMILY,
                                   model_source="test", family_source="test")
    with pytest.raises(tp.IdentityMismatch):
        tp.assert_identity_matches(route, observed)


@pytest.mark.parametrize("spec_name", ["M05_unit_review", "M07_workbook_review"])
def test_a_conforming_review_records_the_page_denominator(spec_name):
    update = run(spec_name)
    channel = "unit_reviews" if spec_name == "M05_unit_review" else "workbook_reviews"
    assert update[channel][0]["page_count"] == 2
    assert update[channel][0]["review_kind"] == (
        "unit" if spec_name == "M05_unit_review" else "workbook")


# ======================================== TEST 5: retry always traverses D91 then D90


def test_transport_is_invoked_from_exactly_one_call_site():
    assert mn.transport_call_sites() == ["_dispatch"]


def test_no_adapter_holds_a_second_transport_reference():
    source = Path(mn.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    executes = [node for node in ast.walk(tree)
                if isinstance(node, ast.Attribute) and node.attr == "execute"]
    assert len(executes) == 1


@pytest.mark.parametrize("reservation", [
    None,
    {"activation_id": "act-1"},
    {"reservation_kind": "guess", "job_id": "M03_WRITE_UNIT_CONTENT",
     "attempt_ordinal": 1, "activation_id": "act-1", "reservation_id": "act-1#1"},
    {"reservation_kind": mn.RESERVATION_KIND, "job_id": "M02_CREATE_UNIT_DOMAIN_DATA",
     "attempt_ordinal": 1, "activation_id": "act-1", "reservation_id": "act-1#1"},
    {"reservation_kind": mn.RESERVATION_KIND, "job_id": "M03_WRITE_UNIT_CONTENT",
     "attempt_ordinal": 0, "activation_id": "act-1", "reservation_id": "act-1#1"},
    {"reservation_kind": mn.RESERVATION_KIND, "job_id": "M03_WRITE_UNIT_CONTENT",
     "attempt_ordinal": 1, "reservation_id": "act-1#1"},
])
def test_an_adapter_refuses_to_dispatch_without_a_valid_d90_reservation(reservation):
    packet = packet_for("M03_content")
    if reservation is None:
        packet.pop("reservation")
    else:
        packet["reservation"] = reservation
    context, transport = context_for("M03_content")
    with pytest.raises(mn.AttemptNotReserved):
        mn.m03_write_unit_content(packet, context)
    assert transport.calls == []


def test_a_reservation_beyond_the_frozen_limit_is_refused():
    packet = packet_for("M03_content")
    packet["reservation"] = {**packet["reservation"],
                             "attempt_ordinal": mn.MODEL_NODE_ATTEMPT_LIMIT + 1}
    context, transport = context_for("M03_content")
    with pytest.raises(mn.AttemptNotReserved, match="exceeds the frozen limit"):
        mn.m03_write_unit_content(packet, context)
    assert transport.calls == []


def test_a_malformed_result_yields_a_classifiable_failure_not_a_candidate():
    context, transport = context_for(
        "M03_content", errors=[tp.ResultParseError("malformed_json", "expecting value")])
    update = mn.m03_write_unit_content(packet_for("M03_content"), context)
    assert len(transport.calls) == 1
    assert "artifact_versions" not in update
    failure = update["pending_failure"]
    assert failure["failure_class"] == "malformed_json"
    assert failure["requires_classification_by"] == "D91_CLASSIFY_MODEL_FAILURE"


def test_a_retry_traverses_d91_then_d90_before_the_second_transport_call():
    job_id = "M03_WRITE_UNIT_CONTENT"
    transport = RecordingTransport({job_id: CANDIDATES[job_id]},
                                   errors=[tp.ResultParseError("malformed_json", "boom")])
    context = mn.ModelNodeContext(transport=transport, registry=tp.load_job_registry())

    state: dict[str, Any] = {}
    first = mn.reserve_model_attempt(state, job_id=job_id, correlation_key="corr-1",
                                     activation_id="act-1")
    state["attempt_counters"] = monotonic_max(state.get("attempt_counters"),
                                              first["attempt_counters"])
    packet = {**packet_for("M03_content"),
              "reservation": first["pending_guard"]["reservation"]}
    failed = mn.m03_write_unit_content(packet, context)
    assert len(transport.calls) == 1

    classified = mn.classify_model_failure(failed["pending_failure"], attempts_used=1)
    assert classified["pending_guard"]["decision"] == "retry"
    assert classified["pending_guard"]["destination"] == "D90_RESERVE_MODEL_ATTEMPT"
    assert "terminal_candidate" not in classified
    assert len(transport.calls) == 1, "D91 must not itself call the transport"

    second = mn.reserve_model_attempt(state, job_id=job_id, correlation_key="corr-1",
                                      activation_id="act-2")
    assert second["pending_guard"]["reservation"]["attempt_ordinal"] == 2
    state["attempt_counters"] = monotonic_max(state["attempt_counters"],
                                              second["attempt_counters"])
    succeeded = mn.m03_write_unit_content(
        {**packet, "reservation": second["pending_guard"]["reservation"]}, context)
    assert len(transport.calls) == 2
    assert succeeded["artifact_versions"][0]["record_kind"] == "model_candidate"


def test_d90_commits_the_counter_before_dispatch_and_stops_at_the_limit():
    job_id = "M03_WRITE_UNIT_CONTENT"
    key = mn.attempt_counter_key(job_id, "corr-1")
    first = mn.reserve_model_attempt({}, job_id=job_id, correlation_key="corr-1",
                                     activation_id="act-1")
    assert first["attempt_counters"] == {key: 1}
    assert first["pending_guard"]["decision"] == "authorized"

    second = mn.reserve_model_attempt({"attempt_counters": {key: 1}}, job_id=job_id,
                                      correlation_key="corr-1", activation_id="act-2")
    assert second["attempt_counters"] == {key: 2}

    third = mn.reserve_model_attempt({"attempt_counters": {key: 2}}, job_id=job_id,
                                     correlation_key="corr-1", activation_id="act-3")
    assert third["pending_guard"]["decision"] == "exhausted"
    assert "activation_receipts" not in third
    assert set(third) <= mn.RESERVE_ATTEMPT_WRITABLE_FIELDS
    assert monotonic_max({key: 2}, third["attempt_counters"]) == {key: 2}


def test_d90_refuses_a_job_that_is_not_one_of_the_eight():
    with pytest.raises(mn.ModelNodeError, match="not one of the eight"):
        mn.reserve_model_attempt({}, job_id="M09_INVENTED", correlation_key="c",
                                 activation_id="a")


@pytest.mark.parametrize("failure_class", sorted(mn.POLICY_OR_CONTENT_FAILURE_CLASSES))
def test_policy_and_content_failures_route_to_repair_never_to_a_transport_retry(failure_class):
    classified = mn.classify_model_failure(
        {"failure_class": failure_class, "job_id": "M06_REPAIR_NAMED_UNIT_ARTIFACT",
         "counter_key": "k"}, attempts_used=1)
    assert classified["pending_guard"]["decision"] == "repair"
    assert classified["pending_guard"]["destination"] == "D17_CLASSIFY_UNIT_FINDINGS"
    assert "terminal_candidate" not in classified


def test_a_workbook_content_failure_routes_to_the_workbook_repair_planner():
    classified = mn.classify_model_failure(
        {"failure_class": "candidate_boundary_violation",
         "job_id": "M08_REPAIR_NAMED_WORKBOOK_DEFECT", "counter_key": "k"},
        attempts_used=1)
    assert classified["pending_guard"]["destination"] == "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR"


def test_a_retryable_failure_at_the_limit_becomes_exhaustion():
    state = {"attempt_counters": {"k": mn.MODEL_NODE_ATTEMPT_LIMIT}}
    classified = mn.classify_model_failure(
        {"failure_class": "timeout", "job_id": "M03_WRITE_UNIT_CONTENT",
         "counter_key": "k"}, attempts_used=mn.MODEL_NODE_ATTEMPT_LIMIT, state=state)
    assert classified["pending_guard"]["decision"] == "exhausted"
    assert classified["terminal_candidate"]["kind"] == "CONVERGENCE_EXHAUSTED"
    # N30V7-F05-shaped regression, generalized (N20V7-F0x): this must be the exact
    # same key/shape D98's real, independent revalidation (nodes/terminal.py) requires
    # -- not merely what this module's own writer happens to produce. A prior version
    # of this function wrote "terminal_kind" instead of "kind", which every D91-proposed
    # exhaustion/system-failure terminal would then always fail D98's revalidation for,
    # undetected here because this test never round-tripped through the real validator.
    projection = {"attempt_counters": state["attempt_counters"], "failure_fingerprints": [{}],
                  "effective_run": None, "accepted_unit_receipts": {}}
    validation = nt.validate_terminal_candidate(classified["terminal_candidate"], projection)
    assert validation.accepted, validation.rejections
    assert validation.kind == "CONVERGENCE_EXHAUSTED"


@pytest.mark.parametrize("failure_class", ["IdentityMismatch", "CapabilityProofFailed",
                                           "WorkspaceViolation", "something_unknown"])
def test_integrity_failures_are_never_retried(failure_class):
    classified = mn.classify_model_failure(
        {"failure_class": failure_class, "job_id": "M05_REVIEW_ACTUAL_UNIT",
         "counter_key": "k"}, attempts_used=1)
    assert classified["pending_guard"]["decision"] == "system"
    assert classified["terminal_candidate"]["kind"] == "SYSTEM_FAILURE"
    validation = nt.validate_terminal_candidate(classified["terminal_candidate"], {})
    assert validation.accepted, validation.rejections
    assert validation.kind == "SYSTEM_FAILURE"


def test_d91_writes_only_deterministic_classification_channels():
    classified = mn.classify_model_failure(
        {"failure_class": "timeout", "job_id": "M03_WRITE_UNIT_CONTENT",
         "counter_key": "k"}, attempts_used=1)
    assert set(classified) <= mn.CLASSIFY_FAILURE_WRITABLE_FIELDS


def test_reusing_one_reservation_for_a_second_dispatch_conflicts_in_the_ledger():
    """Two different results under one reservation cannot both land in state."""

    packet = packet_for("M03_content")
    first = run("M03_content", packet=packet)
    other = candidate_for("M03_content")
    other["unit_content"]["sections"][0]["body"] = "A lever pivots about a fulcrum."
    second = run("M03_content", packet=packet, candidate=other)

    merged = append_unique(None, first["activation_receipts"])
    with pytest.raises(DuplicateConflict):
        append_unique(merged, second["activation_receipts"])


# ==================================== TEST 6: candidates never touch a head or terminal


@pytest.mark.parametrize("spec_name", sorted(SPEC_SECTION_9))
def test_every_adapter_writes_only_pre_admission_candidate_channels(spec_name):
    update = run(spec_name)
    assert set(update) <= mn.MODEL_NODE_WRITABLE_FIELDS
    assert set(update) & mn.FORBIDDEN_MODEL_NODE_FIELDS == set()
    for forbidden in ("artifact_heads", "workbook_head", "accepted_unit_receipts",
                      "terminal", "terminal_candidate", "unit_status"):
        assert forbidden not in update


@pytest.mark.parametrize("spec_name", sorted(SPEC_SECTION_9))
def test_a_model_update_can_never_satisfy_an_advance_head_update(spec_name):
    update = run(spec_name)
    for field, value in update.items():
        records = value if isinstance(value, list) else (
            list(value.values()) if isinstance(value, dict) else [value])
        for record in records:
            if not isinstance(record, dict):
                continue
            assert not {"version", "hash"} <= set(record)
            with pytest.raises(HeadAdvanceError):
                advance_head({}, {"unit/U01/content": record})


@pytest.mark.parametrize("spec_name", sorted(SPEC_SECTION_9))
def test_every_candidate_record_is_marked_pre_admission(spec_name):
    update = run(spec_name)
    candidates = [record for field in mn.MODEL_NODE_WRITABLE_FIELDS
                  if field in update and field not in {"model_execution_receipts",
                                                       "activation_receipts",
                                                       "pending_failure"}
                  for record in (update[field] if isinstance(update[field], list)
                                 else update[field].values())]
    assert candidates, spec_name
    for record in candidates:
        assert record["pre_admission"] is True
        assert record["record_kind"] == "model_candidate"


def candidates_in(update: dict[str, Any]) -> list[dict[str, Any]]:
    return [record for field in mn.MODEL_NODE_WRITABLE_FIELDS
            if field in update and field not in {"model_execution_receipts",
                                                 "activation_receipts", "pending_failure"}
            for record in (update[field] if isinstance(update[field], list)
                           else update[field].values())]


# B-7: the lineage a deterministic join indexes a candidate by is the dispatcher's, so
# the projection must carry it onto the record. `payload` stays quarantined as the only
# thing the model itself authored.
LINEAGE = [
    ("M01_discovery", "source_discoveries", {"unit_id": "U01"}),
    ("M01_interpretation", "source_interpretations",
     {"unit_id": "U01", "retrieval_sha256": SHA}),
    ("M02_domain", "artifact_versions", {"unit_id": "U01"}),
    ("M03_content", "artifact_versions", {"unit_id": "U01"}),
    ("M04_visual", "visual_results",
     {"unit_id": "U01", "subset": "model", "content_hash": CONTENT_HASH}),
]


@pytest.mark.parametrize("spec_name,field,expected", LINEAGE,
                         ids=[row[0] for row in LINEAGE])
def test_a_candidate_carries_the_lineage_its_consuming_join_indexes_by(spec_name, field,
                                                                      expected):
    record = candidates_in(run(spec_name))[0]
    assert {key: record.get(key) for key in expected} == expected
    assert field in run(spec_name)


def test_the_lineage_tracks_the_dispatchers_brief_not_the_models_unchanged_answer():
    """One identical model answer, two content epochs: the record follows the brief."""

    superseded = packet_for("M04_visual")
    superseded["brief"]["content_hash"] = "d" * 64
    first = candidates_in(run("M04_visual"))[0]
    second = candidates_in(run("M04_visual", packet=superseded))[0]
    assert first["payload"] == second["payload"]
    assert (first["content_hash"], second["content_hash"]) == (CONTENT_HASH, "d" * 64)


def test_the_discovery_locators_a_join_reads_stay_inside_the_models_payload():
    """D06B's locators are the model's own answer, so they are read out of `payload`."""

    record = candidates_in(run("M01_discovery"))[0]
    assert record["payload"]["locators"][0]["request_id"] == "REQ-1"
    assert "locators" not in record, "model output is never promoted to a lineage field"


@pytest.mark.parametrize("spec_name", sorted(SPEC_SECTION_9))
def test_no_candidate_record_may_carry_an_admission_owned_field(spec_name):
    """The property the whole pre-admission design exists to guarantee."""

    for record in candidates_in(run(spec_name)):
        assert mn.ADMISSION_OWNED_CANDIDATE_FIELDS & set(record) == set()
        assert {"version", "hash", "parent_hash"} & set(record) == set()


@pytest.mark.parametrize("field", sorted(mn.ADMISSION_OWNED_CANDIDATE_FIELDS))
def test_an_adapter_that_tried_to_mint_a_version_is_refused_by_the_module(field):
    dispatch = mn._Dispatch(spec=mn.PROJECTION_SPECS["M02_domain"], route=None,
                            projection={}, correlation=correlation(),
                            reservation={"reservation_id": "r-1", "activation_id": "a-1"},
                            candidate={}, receipt={}, attempts=())
    with pytest.raises(mn.ModelNodeError, match="deterministic admission authority"):
        mn._candidate_record(dispatch, **{field: SHA})


def test_the_writable_and_forbidden_field_sets_are_real_and_disjoint():
    assert mn.MODEL_NODE_WRITABLE_FIELDS <= set(FACTORY_STATE_FIELDS)
    assert mn.FORBIDDEN_MODEL_NODE_FIELDS <= set(FACTORY_STATE_FIELDS)
    assert mn.MODEL_NODE_WRITABLE_FIELDS & mn.FORBIDDEN_MODEL_NODE_FIELDS == set()
    for field in ("artifact_heads", "workbook_head"):
        assert FIELD_REDUCER_CLASSES[field] == "advance_head"
        assert field in mn.FORBIDDEN_MODEL_NODE_FIELDS
    assert FIELD_REDUCER_CLASSES["accepted_unit_receipts"] == "accept_once"


def test_candidate_channels_use_the_reducers_the_spec_declares():
    expected = {"source_discoveries": "union_disjoint",
                "source_interpretations": "union_disjoint",
                "visual_results": "union_disjoint",
                "artifact_versions": "append_unique",
                "workbook_versions": "append_unique",
                "unit_reviews": "append_unique",
                "workbook_reviews": "append_unique"}
    for field, reducer_class in expected.items():
        assert FIELD_REDUCER_CLASSES[field] == reducer_class


def test_fan_out_updates_merge_through_the_declared_reducers():
    first = run("M04_visual")
    merged = union_disjoint(None, first["visual_results"])
    assert union_disjoint(merged, first["visual_results"]) == merged

    domain = run("M02_domain")
    versions = append_unique(None, domain["artifact_versions"])
    assert append_unique(versions, domain["artifact_versions"]) == versions


def test_an_update_that_names_a_head_is_refused_by_the_module():
    with pytest.raises(mn.ModelNodeError, match="deterministic-node authority"):
        mn._assert_model_node_update({"artifact_heads": {"unit/U01/content": {}}})


# ====================================== TEST 7: fake transports only in test builds


def runtime_context_with(transport: Any) -> RuntimeContext:
    return RuntimeContext(engine_root=Path("/tmp/engine"), output_root=Path("/tmp/out"),
                          path_guard=object(), evidence_service=object(),
                          transport_registry=transport, source_retriever=object(),
                          signal_token=object(), clock=lambda: "now")


def test_the_production_context_refuses_a_fake_transport(tmp_path):
    fake = tp.FakeCliTransport(sandbox_root=tmp_path, responses={})
    with pytest.raises(mn.ModelNodeError, match="build_test_model_node_context"):
        mn.build_model_node_context(runtime_context_with(fake))


def test_the_production_context_refuses_any_non_transport_object():
    with pytest.raises(mn.ModelNodeError, match="CliTransport"):
        mn.build_model_node_context(runtime_context_with(RecordingTransport({})))


def test_only_the_named_test_builder_and_its_guard_mention_the_fake_transport():
    tree = ast.parse(Path(mn.__file__).read_text(encoding="utf-8"))
    mentions: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Attribute) and inner.attr == "FakeCliTransport":
                mentions.add(node.name)
            if isinstance(inner, ast.Name) and inner.id == "FakeCliTransport":
                mentions.add(node.name)
    assert mentions == {"_assert_production_transport", "build_test_model_node_context"}


def test_the_production_builder_always_passes_through_the_transport_guard():
    tree = ast.parse(Path(mn.__file__).read_text(encoding="utf-8"))
    builders = {node.name: node for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
                and any(isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
                        and inner.func.id == "ModelNodeContext" for inner in ast.walk(node))}
    assert set(builders) == {"build_model_node_context", "build_test_model_node_context"}
    production = builders["build_model_node_context"]
    guarded = any(isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
                  and inner.func.id == "_assert_production_transport"
                  for inner in ast.walk(production))
    assert guarded


def test_the_test_builder_produces_a_usable_fake_context(tmp_path):
    context = mn.build_test_model_node_context(
        sandbox_root=tmp_path,
        responses={"M03_WRITE_UNIT_CONTENT": CANDIDATES["M03_WRITE_UNIT_CONTENT"]})
    update = mn.m03_write_unit_content(packet_for("M03_content"), context)
    assert set(update) <= mn.MODEL_NODE_WRITABLE_FIELDS
    assert update["artifact_versions"][0]["channel"] == "content"


def test_the_fake_transport_still_refuses_a_product_root():
    with pytest.raises(tp.TransportError):
        mn.build_test_model_node_context(sandbox_root=Path(__file__).parent, responses={})


# ------------------------------------------------- D90/D91 as registrable node bodies


def member(correlation_key: str, **extra: Any) -> dict[str, Any]:
    return {"correlation": correlation(correlation_key), **extra}


def staged(job_id: str, *keys: str, member_key: str = "packets") -> dict[str, Any]:
    return {"dispatch": job_id, member_key: [member(key) for key in keys]}


def test_d90_mints_one_reservation_per_fanout_member():
    job_id = "M01_RESEARCH_UNIT_SOURCES"
    state = {"pending_packet": staged(job_id, "req-1", "req-2", "req-3")}

    update = mn.D90_RESERVE_MODEL_ATTEMPT(state, None)

    keys = [mn.attempt_counter_key(job_id, f"req-{n}") for n in (1, 2, 3)]
    assert update["attempt_counters"] == {key: 1 for key in keys}
    assert set(update) <= mn.RESERVE_ATTEMPT_WRITABLE_FIELDS

    members = update["pending_packet"]["packets"]
    assert len(members) == 3
    reservations = [item["reservation"] for item in members]
    assert {item["counter_key"] for item in reservations} == set(keys)
    assert len({item["activation_id"] for item in reservations}) == 3
    assert len({item["reservation_id"] for item in reservations}) == 3
    for reservation in reservations:
        assert reservation["attempt_ordinal"] == 1
    assert len(update["activation_receipts"]) == 3


def test_a_reserved_fanout_member_is_dispatchable_by_the_model_adapter():
    """The reservation D90 mints is the one `_resolve_reservation` accepts."""

    job_id = "M01_RESEARCH_UNIT_SOURCES"
    state = {"pending_packet": staged(job_id, "req-1")}
    reservation = mn.D90_RESERVE_MODEL_ATTEMPT(state, None)["pending_packet"]["packets"][0]
    assert mn._resolve_reservation(reservation, job_id=job_id)["attempt_ordinal"] == 1


def test_a_second_superstep_reserves_the_next_ordinal_per_correlation():
    job_id = "M04_CREATE_UNIT_VISUALS"
    key = mn.attempt_counter_key(job_id, "vis-1")
    state = {"pending_packet": staged(job_id, "vis-1", member_key="briefs"),
             "attempt_counters": {key: 1}}

    update = mn.D90_RESERVE_MODEL_ATTEMPT(state, None)

    assert update["attempt_counters"] == {key: 2}
    reservation = update["pending_packet"]["briefs"][0]["reservation"]
    assert reservation["attempt_ordinal"] == 2


def test_d90_restages_only_the_member_d91_authorized_a_retry_for():
    job_id = "M01_RESEARCH_UNIT_SOURCES"
    retried = mn.attempt_counter_key(job_id, "req-2")
    state = {
        "pending_packet": staged(job_id, "req-1", "req-2", "req-3"),
        "attempt_counters": {mn.attempt_counter_key(job_id, f"req-{n}"): 1
                             for n in (1, 2, 3)},
        "pending_guard": {"kind": "model_failure", "decision": "retry",
                          "counter_key": retried, "job_id": job_id},
    }

    update = mn.D90_RESERVE_MODEL_ATTEMPT(state, None)

    assert update["attempt_counters"] == {retried: 2}
    members = update["pending_packet"]["packets"]
    assert len(members) == 1
    assert members[0]["correlation"]["correlation_key"] == "req-2"
    assert members[0]["reservation"]["attempt_ordinal"] == 2


def test_a_retry_that_names_no_staged_member_is_refused():
    job_id = "M01_RESEARCH_UNIT_SOURCES"
    state = {
        "pending_packet": staged(job_id, "req-1"),
        "pending_guard": {"kind": "model_failure", "decision": "retry",
                          "counter_key": mn.attempt_counter_key(job_id, "gone"),
                          "job_id": job_id},
    }
    with pytest.raises(mn.ModelNodeError, match="matches no staged member"):
        mn.D90_RESERVE_MODEL_ATTEMPT(state, None)


def test_one_exhausted_member_exhausts_the_whole_superstep():
    job_id = "M01_RESEARCH_UNIT_SOURCES"
    at_limit = mn.attempt_counter_key(job_id, "req-2")
    state = {"pending_packet": staged(job_id, "req-1", "req-2"),
             "attempt_counters": {at_limit: mn.MODEL_NODE_ATTEMPT_LIMIT}}

    update = mn.D90_RESERVE_MODEL_ATTEMPT(state, None)

    assert update["pending_guard"]["value"] == "exhausted"
    assert "pending_packet" not in update, "no partial map may be dispatched"
    assert "activation_receipts" not in update
    assert update["pending_guard"]["detail"]["exhausted"][0]["counter_key"] == at_limit


def test_m01s_two_phases_each_get_their_own_attempt_budget():
    """B-13: a run in which nothing goes wrong must not spend M01's whole budget."""

    job_id = "M01_RESEARCH_UNIT_SOURCES"
    request_key = "U001/1/required_explanation:000"

    def reserve(phase: str, counters: dict[str, int]) -> dict[str, Any]:
        return mn.D90_RESERVE_MODEL_ATTEMPT(
            {"pending_packet": {"dispatch": job_id,
                                "packets": [member(request_key, phase=phase)]},
             "attempt_counters": counters}, None)

    discovery = reserve("DISCOVER", {})
    interpretation = reserve("INTERPRET", dict(discovery["attempt_counters"]))

    assert discovery["pending_guard"]["value"] == "authorized"
    assert interpretation["pending_guard"]["value"] == "authorized"
    assert monotonic_max(discovery["attempt_counters"],
                         interpretation["attempt_counters"]) == {
        mn.attempt_counter_key(job_id, request_key, "DISCOVER"): 1,
        mn.attempt_counter_key(job_id, request_key, "INTERPRET"): 1,
    }
    for update in (discovery, interpretation):
        staged_member = update["pending_packet"]["packets"][0]
        assert staged_member["correlation"]["correlation_key"] == request_key, (
            "D06B and D07 index their joins by the correlation key, so only D90's "
            "counter key may widen")
        assert staged_member["reservation"]["attempt_ordinal"] == 1


def test_the_frozen_limit_still_binds_within_one_m01_phase():
    job_id = "M01_RESEARCH_UNIT_SOURCES"
    request_key = "U001/1/required_explanation:000"
    packet = {"dispatch": job_id, "packets": [member(request_key, phase="DISCOVER")]}

    counters: dict[str, int] = {}
    ordinals = []
    for _ in range(mn.MODEL_NODE_ATTEMPT_LIMIT):
        update = mn.D90_RESERVE_MODEL_ATTEMPT(
            {"pending_packet": packet, "attempt_counters": counters}, None)
        assert update["pending_guard"]["value"] == "authorized"
        counters = monotonic_max(counters, update["attempt_counters"])
        ordinals.append(
            update["pending_packet"]["packets"][0]["reservation"]["attempt_ordinal"])

    assert ordinals == list(range(1, mn.MODEL_NODE_ATTEMPT_LIMIT + 1))
    exhausted = mn.D90_RESERVE_MODEL_ATTEMPT(
        {"pending_packet": packet, "attempt_counters": counters}, None)
    assert exhausted["pending_guard"]["value"] == "exhausted"
    assert exhausted["pending_guard"]["detail"]["exhausted"][0]["counter_key"] == (
        mn.attempt_counter_key(job_id, request_key, "DISCOVER"))


def test_a_phased_retry_restages_only_the_phase_d91_named():
    job_id = "M01_RESEARCH_UNIT_SOURCES"
    request_key = "U001/1/required_explanation:000"
    retried = mn.attempt_counter_key(job_id, request_key, "INTERPRET")
    state = {
        "pending_packet": {"dispatch": job_id,
                           "packets": [member(request_key, phase="INTERPRET")]},
        "attempt_counters": {
            mn.attempt_counter_key(job_id, request_key, "DISCOVER"): 1,
            retried: 1,
        },
        "pending_guard": {"kind": "model_failure", "decision": "retry",
                          "counter_key": retried, "job_id": job_id},
    }

    update = mn.D90_RESERVE_MODEL_ATTEMPT(state, None)

    assert update["attempt_counters"] == {retried: 2}, (
        "a transport fault on interpretation must not spend discovery's budget")
    assert update["pending_packet"]["packets"][0]["reservation"]["attempt_ordinal"] == 2


def test_the_real_m01_dispatchers_reserve_against_distinct_counters():
    """N30's regression case, driven through the real D06 body.

    D06 and D06B stage the same `correlation_key` on purpose — D06B indexes
    `source_discoveries` and D07 indexes `source_interpretations` by it — so the
    phase is the only thing that may separate the two attempt budgets.
    """

    from runtime.langgraph_factory.nodes import sources

    state = {
        "run_id": RUN_ID,
        "episode_id": EPISODE_ID,
        "effective_run": {
            "unit_records": [{"id": "U001", "title": "t",
                              "required_explanation": ["fact"],
                              "safety_focus": ["care"]}],
            "target_closure": ["U001"],
        },
        "selected_unit_id": "U001",
        "source_admissions": [],
        "engine_root": "/tmp",
    }
    staged_discovery = sources.D06_COMPILE_SOURCE_REQUESTS(state, None)
    discovery_members = staged_discovery["pending_packet"]["packets"]
    assert {item["phase"] for item in discovery_members} == {"DISCOVER"}

    # D06B restages the same correlations under the interpretation phase.
    staged_interpretation = {"pending_packet": {
        **staged_discovery["pending_packet"],
        "packets": [{**item, "phase": "INTERPRET"} for item in discovery_members]}}

    discovery = mn.D90_RESERVE_MODEL_ATTEMPT({**state, **staged_discovery}, None)
    interpretation = mn.D90_RESERVE_MODEL_ATTEMPT(
        {**state, "attempt_counters": discovery["attempt_counters"],
         **staged_interpretation}, None)

    assert discovery["pending_guard"]["value"] == "authorized"
    assert interpretation["pending_guard"]["value"] == "authorized"
    assert not set(discovery["attempt_counters"]) & set(
        interpretation["attempt_counters"]), "the two phases must not share a counter"
    assert set(discovery["attempt_counters"].values()) == {1}
    assert set(interpretation["attempt_counters"].values()) == {1}
    assert [item["correlation"]["correlation_key"]
            for item in interpretation["pending_packet"]["packets"]] == [
        item["correlation"]["correlation_key"] for item in discovery_members]


def test_a_staged_member_with_an_unusable_phase_is_refused():
    job_id = "M01_RESEARCH_UNIT_SOURCES"
    state = {"pending_packet": {"dispatch": job_id,
                                "packets": [member("req-1", phase=1)]}}
    with pytest.raises(mn.ModelNodeError, match="non-string phase"):
        mn.D90_RESERVE_MODEL_ATTEMPT(state, None)


def test_d90_refuses_to_reserve_for_an_unstaged_dispatch():
    with pytest.raises(mn.ModelNodeError, match="no `pending_packet` is staged"):
        mn.D90_RESERVE_MODEL_ATTEMPT({}, None)
    with pytest.raises(mn.ModelNodeError, match="not one of the eight"):
        mn.D90_RESERVE_MODEL_ATTEMPT(
            {"pending_packet": {"dispatch": "D11_CREATE_DETERMINISTIC_VISUALS",
                                "packets": [member("x")]}}, None)


def test_d90_guard_routes_through_the_frozen_guard_table():
    from runtime.langgraph_factory import routing

    job_id = "M01_RESEARCH_UNIT_SOURCES"
    at_limit = {"pending_packet": staged(job_id, "req-1"),
                "attempt_counters": {mn.attempt_counter_key(job_id, "req-1"):
                                     mn.MODEL_NODE_ATTEMPT_LIMIT}}
    exhausted = mn.D90_RESERVE_MODEL_ATTEMPT(at_limit, None)
    assert routing.route_attempt_reservation(exhausted) == "D98_WRITE_TERMINAL"


def test_an_authorized_reservation_dispatches_one_worker_per_restaged_member():
    pytest.importorskip("langgraph")  # an authorized fan-out is a real `Send` list
    from runtime.langgraph_factory import routing

    job_id = "M01_RESEARCH_UNIT_SOURCES"
    authorized = mn.D90_RESERVE_MODEL_ATTEMPT(
        {"pending_packet": staged(job_id, "req-1", "req-2")}, None)
    sends = routing.route_attempt_reservation(authorized)

    assert [send.node for send in sends] == [job_id, job_id]
    assert sorted(send.arg["reservation"]["counter_key"] for send in sends) == [
        mn.attempt_counter_key(job_id, "req-1"),
        mn.attempt_counter_key(job_id, "req-2"),
    ], "each dispatched worker carries its own committed counter"


def test_d91_classifies_the_pending_failure_against_the_committed_counter():
    from runtime.langgraph_factory import routing

    job_id = "M03_WRITE_UNIT_CONTENT"
    key = mn.attempt_counter_key(job_id, "u01")
    state = {"attempt_counters": {key: 1},
             "pending_failure": {"job_id": job_id, "counter_key": key,
                                 "failure_class": "timeout", "attempt_ordinal": 1}}

    update = mn.D91_CLASSIFY_MODEL_FAILURE(state, None)

    assert update["pending_guard"]["decision"] == "retry"
    assert update["pending_failure"] is None, "an uncleared failure routes D90 to terminal"
    assert routing.route_model_failure(update) == "D90_RESERVE_MODEL_ATTEMPT"


def test_d91_at_the_committed_limit_exhausts_rather_than_retrying():
    from runtime.langgraph_factory import routing

    job_id = "M03_WRITE_UNIT_CONTENT"
    key = mn.attempt_counter_key(job_id, "u01")
    state = {"attempt_counters": {key: mn.MODEL_NODE_ATTEMPT_LIMIT},
             "pending_failure": {"job_id": job_id, "counter_key": key,
                                 "failure_class": "timeout", "attempt_ordinal": 1}}

    update = mn.D91_CLASSIFY_MODEL_FAILURE(state, None)

    assert update["pending_guard"]["decision"] == "exhausted"
    assert update["terminal_candidate"]["kind"] == "CONVERGENCE_EXHAUSTED"
    assert routing.route_model_failure(update) == "D98_WRITE_TERMINAL"
    projection = {"attempt_counters": state["attempt_counters"], "failure_fingerprints": [{}],
                  "effective_run": None, "accepted_unit_receipts": {}}
    validation = nt.validate_terminal_candidate(update["terminal_candidate"], projection)
    assert validation.accepted, validation.rejections


def test_d91_repair_destination_resolves_through_the_dynamic_guard():
    from runtime.langgraph_factory import routing

    job_id = "M05_REVIEW_ACTUAL_UNIT"
    key = mn.attempt_counter_key(job_id, "u01")
    state = {"attempt_counters": {key: 1},
             "pending_failure": {"job_id": job_id, "counter_key": key,
                                 "failure_class": "content_violation"}}

    update = mn.D91_CLASSIFY_MODEL_FAILURE(state, None)

    assert update["pending_guard"]["decision"] == "repair"
    assert routing.route_model_failure(update) == "D17_CLASSIFY_UNIT_FINDINGS"


def test_d91_repair_leaves_the_classified_pending_failure_for_d17_to_consume():
    """N20V7-F09 corrected regression (an earlier fix here was itself wrong --
    live-verified against a real N70 production run): D91's own outgoing edge
    (routing.route_model_failure) reads pending_guard, never pending_failure,
    so nothing about D91's own routing needs pending_failure cleared on
    "repair". D17_CLASSIFY_UNIT_FINDINGS (repair.py) reads exactly this
    classified pending_failure to build its one raw finding for a model-repair
    job, then clears it itself once consumed. Nulling it in D91 instead left
    D17 with no findings to classify at all ("routed with an empty or missing
    findings list") the moment a real M01 discovery sub-request failed content
    policy and D91 routed it to D17 for repair.
    """
    from runtime.langgraph_factory import repair, routing

    job_id = "M01_RESEARCH_UNIT_SOURCES"
    key = mn.attempt_counter_key(job_id, "u01")
    state = {"attempt_counters": {key: 1},
             "pending_failure": {"job_id": job_id, "counter_key": key,
                                 "failure_class": "candidate_undeclared_artifact",
                                 "detail": "discovery must emit locators, not interpretations"}}

    update = mn.D91_CLASSIFY_MODEL_FAILURE(state, None)
    assert update["pending_guard"]["decision"] == "repair"
    assert update["pending_failure"]["classification"] == "repair", \
        "D17 reads this tag directly; nulling pending_failure here starves D17 of its finding"
    assert routing.route_model_failure(update) == "D17_CLASSIFY_UNIT_FINDINGS"

    d17_state = {**state, **update, "selected_unit_id": "u01", "accepted_unit_receipts": {}}
    d17_update = repair.D17_CLASSIFY_UNIT_FINDINGS(d17_state, None)

    assert d17_update["pending_failure"] is None, "D17 must clear it itself once consumed"
    assert d17_update["finding_partitions"], "D91's classified failure must become a real partition"
    merged = {**d17_state, **d17_update}
    assert routing.route_finding_classification(merged) == "D18_PLAN_TARGETED_UNIT_REPAIR"


def test_d91_classifies_an_activation_d92_could_not_account_for():
    job_id = "M02_CREATE_UNIT_DOMAIN_DATA"
    reserved = mn.D90_RESERVE_MODEL_ATTEMPT(
        {"pending_packet": staged(job_id, "u01")}, None)
    activation = reserved["activation_receipts"][0]
    state = {
        "attempt_counters": reserved["attempt_counters"],
        "activation_receipts": reserved["activation_receipts"],
        "pending_guard": {"node": "D92_REENTER_VALIDATED_FRONTIER",
                          "value": "incomplete_model_activation",
                          "detail": {"activations": [activation["activation_id"]]}},
    }

    update = mn.D91_CLASSIFY_MODEL_FAILURE(state, None)

    assert update["pending_guard"]["decision"] == "retry"
    assert update["failure_fingerprints"][0]["failure_class"] == "aborted_activation"
    assert update["failure_fingerprints"][0]["counter_key"] == activation["counter_key"]


def test_an_incomplete_activation_with_no_reservation_receipt_is_refused():
    state = {"pending_guard": {"node": "D92_REENTER_VALIDATED_FRONTIER",
                               "value": "incomplete_model_activation",
                               "detail": {"activations": ["act-unknown"]}}}
    with pytest.raises(mn.ModelNodeError, match="no reservation receipt"):
        mn.D91_CLASSIFY_MODEL_FAILURE(state, None)


@pytest.mark.parametrize("node_id", sorted(mn.MODEL_BOOKKEEPING_NODES))
def test_the_bookkeeping_nodes_have_the_node_body_calling_convention(node_id):
    """`add_node` binds a body by position; a keyword-only helper is not one."""

    import inspect

    body = mn.MODEL_BOOKKEEPING_NODES[node_id]
    assert body.__name__ == node_id
    assert body.__module__ == "runtime.langgraph_factory.model_nodes"
    parameters = list(inspect.signature(body).parameters.values())
    assert len(parameters) == 2
    assert [p.kind for p in parameters] == [inspect.Parameter.POSITIONAL_OR_KEYWORD] * 2
    assert all(p.default is inspect.Parameter.empty for p in parameters)


def test_the_bookkeeping_nodes_register_on_a_real_state_graph():
    """The proof B-3 asked for: a real `add_node` of the exported callables."""

    pytest.importorskip("langgraph")
    from runtime.langgraph_factory import graph as G

    bindings = {**G.binding_inventory(), **mn.MODEL_BOOKKEEPING_NODES}
    inventory = G.validate_bindings(bindings, required=tuple(mn.MODEL_BOOKKEEPING_NODES))
    for node_id in mn.MODEL_BOOKKEEPING_NODES:
        assert inventory[node_id]["module"] == "runtime.langgraph_factory.model_nodes"

    from langgraph.graph import StateGraph

    from runtime.langgraph_factory.state import FactoryState

    builder = StateGraph(FactoryState)
    for node_id, body in mn.MODEL_BOOKKEEPING_NODES.items():
        builder.add_node(node_id, G._boundary(node_id, body, model_node=False))
    assert set(mn.MODEL_BOOKKEEPING_NODES) <= set(builder.nodes)
