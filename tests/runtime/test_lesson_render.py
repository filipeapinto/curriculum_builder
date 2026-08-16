"""Section 1 of plans/runtime_integrity_remediation — the field-aware lesson renderer.

Covers issue 001: no serialized object syntax and no literal schema field name reaches
the learner, every required field has a template branch, and one that does not raises.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re

import pytest

from curriculum_factory.lesson_render import (HANDLED_FIELDS, RendererError, domain_fact_lines,
                                   derived_records, render_adult_verification,
                                   render_elaborate, render_engage, render_evaluate,
                                   render_explain, render_explore, render_identification,
                                   render_recording_block, render_troubleshooting,
                                   render_unit)
from curriculum_factory.session_bridge import _markdown

ENGINE = Path(__file__).resolve().parents[2]
LAB_SCHEMA = json.loads((ENGINE / "schemas/lab.schema.v4.json").read_text())


def _fixture_unit() -> dict:
    return {
        "identity": {"unit_id": "L99", "slug": "test-subject", "kind": "foundation",
                     "title": "Test Subject: A Renderable Unit",
                     "subject_job_sentence": "A test subject exists so the renderer can be exercised."},
        "pedagogy": {
            "learning_objectives": [
                {"statement": "Identify the parts of the test subject accurately.",
                 "bloom_level": "remember", "success_criterion": "I can name each part."},
                {"statement": "Explain why the two halves stay separate from each other.",
                 "bloom_level": "understand", "success_criterion": "I can explain the separation."},
            ],
            "prior_knowledge": {"prerequisite_labs": ["L01"],
                                "assumed_ideas": ["Power stays off while building."],
                                "retrieval_prompt": "What did you check before touching anything last time?"},
            "misconceptions": [{"misconception": "Everything here is joined to everything else.",
                                "why_it_is_common": "The surface looks completely uniform from above.",
                                "confronted_by": "The map shows the boundary between the groups."}],
            "vocabulary": [{"term": "clip", "child_definition": "A hidden metal strip joining holes.",
                            "introduced_in": "explore"}],
            "scaffolding": {"adult_does": ["Keep the board disconnected."],
                            "child_does": ["Trace the map."],
                            "fading_note": "The child now leads the prediction."},
            "cognitive_load": {"segments": ["Look", "Predict", "Trace"],
                               "concrete_before_abstract": "The child points at real holes first."},
        },
        "sequence": {
            "engage": {"hook": "A grid of identical holes hides two different kinds of join.",
                       "eliciting_question": "Do you think every hole is joined?"},
            "explore": {
                "predict": {"question": "Which holes share a hidden clip?",
                            "options": ["the four beside it", "every hole in the column"],
                            "recorded_before_observing": True},
                "observe": {"what_to_observe": "Compare the map against the unpowered board.",
                            "record_method": "tick_or_circle",
                            "evidence_fields": ["prediction", "group found"]},
                "steps": [{"number": 1, "action": "Check the board is disconnected."},
                          {"number": 2, "action": "Circle your prediction."}],
                "expected_observation": "Holes in one short row group together.",
                "not_yet_outcome": {"symptom": "You cannot tell the groups apart.",
                                    "first_check": "Recount one row segment."},
            },
            "explain": {"what_you_saw": "You found a group and the gap, with the board unpowered throughout.",
                        "why_it_happened": ("A short internal metal clip sits under each row segment, so the "
                                            "holes above one clip behave as a single meeting point. The gap "
                                            "down the middle carries no clip at all, which is why the two "
                                            "sides never join through the board itself."),
                        "self_explanation_prompt": "Tell an adult why the two sides never join."},
            "elaborate": {"near_transfer": ["Trace a different group and predict its edge."],
                          "far_transfer": ["A muffin tin keeps its cups separate.",
                                           "An ice-cube tray joins water only within one compartment."]},
            "evaluate": {"success_criteria_checklist": ["I can name each part."],
                         "hinge_question": {"question": "Is the gap itself joined to anything?",
                                            "reveals": "Whether the learner sees the gap as a gap."}},
        },
        "content": {
            "identification": {"child_name": "test board", "technical_name": "solderless test board",
                               "distinguishing_features": "A rectangle of holes either side of a gap.",
                               "orientation_cue": "An adult verifies the map against the board.",
                               "parts": [{"label": "five-hole group", "role": "The basic joined unit."}]},
            "troubleshooting": [{"what_you_notice": "A part reaches holes you did not expect.",
                                 "likely_reason": "Its legs span two groups.",
                                 "safe_first_check": "Recount which group each leg sits in."}],
        },
        "safety": {"hazard_mode": "fully disconnected low-voltage identification",
                   "adult_verification": {"variant": "Standard test board",
                                          "marking": "Marked on the underside",
                                          "verified_configuration": "Not connected to any supply.",
                                          "limits": "No energized work in this unit.",
                                          "endpoint_check": "Adult confirms the board is disconnected.",
                                          "signoff_required": True}},
        "visuals": [
            {"role": "assembly_or_path_map", "source_kind": "deterministic_render",
             "supports_section": "assembly", "carries_exact_domain_fact": True,
             "provenance": {"file_hash": "0" * 64, "access_date": "2026-08-08",
                            "embedded_as": "assets/path_map.svg"},
             "omission_finding": "The map omits any powered configuration."},
            {"role": "expected_result", "source_kind": "deterministic_render",
             "supports_section": "evaluate", "carries_exact_domain_fact": True,
             "provenance": {"file_hash": "1" * 64, "access_date": "2026-08-08",
                            "embedded_as": "assets/evidence_card.svg"}},
            {"role": "subject_identification", "source_kind": "verified_photograph",
             "supports_section": "identification", "carries_exact_domain_fact": True,
             "provenance": {"file_hash": "2" * 64, "access_date": "2026-08-08",
                            "embedded_as": "assets/official_reference.jpg"}},
        ],
        "domain": {
            "electrical": {"behaviour": {"child_level": "Five holes in one short row share one clip."}},
            "build_map": {"map_kind": "connectivity", "relationship": "enumeration",
                          "traced_path": ["five-hole group", "centre gap"],
                          "evidence_card": {"prompt": "Trace which holes share a clip and tick each one.",
                                            "child_records": ["group found", "gap found"]},
                          "power_on_release": False},
        },
    }


def _schema_field_names_with_underscore() -> set[str]:
    names: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "properties" and isinstance(value, dict):
                    names.update(name for name in value if "_" in name)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(LAB_SCHEMA)
    return names


# --- per-function field shapes -------------------------------------------------------

@pytest.mark.parametrize("method", ["evidence_table", "drawing_prompt", "tick_or_circle",
                                    "adult_read_measurement"])
def test_every_record_method_has_a_recording_template(method):
    lines = render_recording_block({"what_to_observe": "x", "record_method": method,
                                    "evidence_fields": ["first field", "second field"]})
    body = "\n".join(lines)
    assert "Record what you found" in body
    assert "first field" in body and "second field" in body
    if method == "evidence_table":
        assert "| --- | --- |" in body
    if method == "tick_or_circle":
        assert "- [_] first field" in body
    if method == "adult_read_measurement":
        assert "written down by an adult" in body


def test_unknown_record_method_raises_rather_than_dropping():
    with pytest.raises(RendererError):
        render_recording_block({"what_to_observe": "x", "record_method": "telepathy"})


def test_recording_template_survives_absent_evidence_fields():
    for method in ["evidence_table", "drawing_prompt", "tick_or_circle", "adult_read_measurement"]:
        assert render_recording_block({"what_to_observe": "x", "record_method": method})


def test_predict_options_render_as_a_lettered_choice_list():
    unit = _fixture_unit()
    body = "\n".join(render_explore(unit["sequence"]["explore"], []))
    assert "**A.** the four beside it" in body
    assert "**B.** every hole in the column" in body
    assert "before you look" in body.lower()


def test_predict_without_options_still_renders_the_question():
    unit = _fixture_unit()
    del unit["sequence"]["explore"]["predict"]["options"]
    body = "\n".join(render_explore(unit["sequence"]["explore"], []))
    assert "Which holes share a hidden clip?" in body
    assert "**A.**" not in body


def test_worked_example_present_and_absent():
    from curriculum_factory.lesson_render import render_cognitive_load
    unit = _fixture_unit()
    absent = "\n".join(render_cognitive_load(unit["pedagogy"]["cognitive_load"]))
    assert "Worked example" not in absent
    unit["pedagogy"]["cognitive_load"]["worked_example"] = "An adult shows one group first."
    present = "\n".join(render_cognitive_load(unit["pedagogy"]["cognitive_load"]))
    assert "**Worked example.** An adult shows one group first." in present


def test_next_lab_link_present_and_absent():
    unit = _fixture_unit()
    absent = "\n".join(render_evaluate(unit["sequence"]["evaluate"], []))
    assert "Next:" not in absent
    unit["sequence"]["evaluate"]["next_lab_link"] = "L03 picks this idea up again."
    present = "\n".join(render_evaluate(unit["sequence"]["evaluate"], []))
    assert "*Next: L03 picks this idea up again.*" in present


def test_orientation_cue_present_and_absent():
    unit = _fixture_unit()
    present = "\n".join(render_identification(unit["content"]["identification"]))
    assert "**Which way round:**" in present
    del unit["content"]["identification"]["orientation_cue"]
    assert "**Which way round:**" not in "\n".join(
        render_identification(unit["content"]["identification"]))


def test_explain_keeps_observation_and_mechanism_separate():
    unit = _fixture_unit()
    body = "\n".join(render_explain(unit["sequence"]["explain"], []))
    assert body.index("**What you saw.**") < body.index("**Why it happened.**")
    assert "own words" in body


def test_vocabulary_is_defined_beside_its_first_use_not_in_a_glossary():
    unit = _fixture_unit()
    vocabulary = unit["pedagogy"]["vocabulary"]
    assert "New word — clip" in "\n".join(render_explore(unit["sequence"]["explore"], vocabulary))
    assert "New word — clip" not in "\n".join(render_engage(unit["sequence"]["engage"], vocabulary))


def test_elaborate_renders_two_labelled_lists():
    unit = _fixture_unit()
    body = "\n".join(render_elaborate(unit["sequence"]["elaborate"], []))
    assert "- Trace a different group and predict its edge." in body
    assert "- A muffin tin keeps its cups separate." in body


def test_troubleshooting_renders_a_three_column_table():
    unit = _fixture_unit()
    body = "\n".join(render_troubleshooting(unit["content"]["troubleshooting"]))
    assert "| What you notice | Why it happens | Your first check |" in body
    assert body.count("|") >= 12


def test_hinge_reveals_is_adult_facing_only():
    unit = _fixture_unit()
    child = "\n".join(render_evaluate(unit["sequence"]["evaluate"], []))
    assert "Whether the learner sees the gap as a gap." not in child
    adult = "\n".join(render_adult_verification(
        unit["safety"], objectives=unit["pedagogy"]["learning_objectives"],
        hinge_question=unit["sequence"]["evaluate"]["hinge_question"]))
    assert "Whether the learner sees the gap as a gap." in adult
    assert adult.startswith("## Adult verification (adult only)")
    assert "Adult signature:" in adult


def test_signoff_not_required_renders_an_explicit_statement():
    unit = _fixture_unit()
    unit["safety"]["adult_verification"]["signoff_required"] = False
    adult = "\n".join(render_adult_verification(unit["safety"]))
    assert "No adult signature is required" in adult


# --- assembled document --------------------------------------------------------------

def test_assembled_markdown_has_no_serialized_object_syntax_or_field_names():
    markdown = _markdown(_fixture_unit())
    assert "{" not in markdown and "}" not in markdown
    assert '":' not in markdown
    leaked = sorted(name for name in _schema_field_names_with_underscore() if name in markdown)
    assert leaked == [], f"literal schema field names reached the learner: {leaked}"


def test_assembled_markdown_carries_every_required_prose_block():
    markdown = _markdown(_fixture_unit())
    for heading in ["## Before we start", "## What I will learn", "## Why this matters",
                    "## Meet it", "### Who does what", "## Try it", "### Record what you found",
                    "## The map to follow", "## What happened", "### A common wrong idea",
                    "## What it solves", "## Check yourself", "## If something looks off",
                    "## Adult verification (adult only)"]:
        assert heading in markdown, f"missing block: {heading}"


def test_visuals_sit_beside_the_section_they_support():
    markdown = _markdown(_fixture_unit())
    assert markdown.index("official_reference.jpg") > markdown.index("## Meet it")
    assert markdown.index("official_reference.jpg") < markdown.index("## Try it")
    assert markdown.index("path_map.svg") > markdown.index("## The map to follow")
    assert markdown.index("path_map.svg") < markdown.index("## What happened")
    assert markdown.index("evidence_card.svg") > markdown.index("## Check yourself")


def test_retrieval_prompt_asks_for_recall_not_a_re_read():
    markdown = _markdown(_fixture_unit())
    section = markdown.split("## Before we start", 1)[1].split("##", 1)[0]
    assert "from memory" in section
    assert "without looking back" in section


def test_unrenderable_required_field_raises_renderer_error():
    unit = _fixture_unit()
    unit["sequence"]["explain"]["mechanism_diagram_caption"] = "a field with no template branch"
    with pytest.raises(RendererError) as raised:
        _markdown(unit)
    assert "mechanism_diagram_caption" in str(raised.value)


def test_empty_unknown_field_is_not_treated_as_unrendered():
    unit = _fixture_unit()
    unit["sequence"]["explain"]["mechanism_diagram_caption"] = ""
    assert _markdown(unit)


def test_every_handled_field_set_matches_the_schema():
    """Each entry in HANDLED_FIELDS covers exactly the schema properties at that location."""
    def properties_at(path: str) -> set[str]:
        node = LAB_SCHEMA["properties"]
        for part in path.split("."):
            if part.endswith("[]"):
                node = node[part[:-2]]["items"]
            else:
                node = node[part]
            node = node.get("properties", node)
        return set(node)

    for path, handled in HANDLED_FIELDS.items():
        assert properties_at(path) == handled, f"HANDLED_FIELDS drifted from the schema at {path}"


def test_unresolved_visual_role_is_stated_in_the_document():
    unit = _fixture_unit()
    unit["content"]["unresolved_visual_roles"] = [
        {"role": "photorealistic meter", "reason": "no verified photograph of the subject exists"}]
    markdown = _markdown(unit)
    assert "## Picture still needed (adult only)" in markdown
    assert "photorealistic meter" in markdown


# --- derivation ----------------------------------------------------------------------

def test_derived_records_resolve_against_the_unit_domain():
    from curriculum_factory.checks import check_derivation
    unit = _fixture_unit()
    unit["derived"] = derived_records(unit)
    assert unit["derived"]
    assert check_derivation(unit)


def test_every_derived_value_is_actually_rendered():
    unit = _fixture_unit()
    lines, derived = domain_fact_lines(unit["domain"])
    body = "\n".join(lines)
    for record in derived:
        assert record["rendered_value"] in body


def test_breadboard_map_kind_renders_its_own_fields():
    unit = _fixture_unit()
    unit["domain"]["build_map"] = {
        "map_kind": "breadboard", "orientation": "rails at top and bottom",
        "labelled_features": ["rows", "columns", "rails", "centre_trench", "rail_breaks"],
        "wire_endpoints": [{"from": "a1", "to": "e1"}],
        "placement_steps": ["Find one five-hole group."],
        "schematic_included": True,
        "safety_inset": {"shows": "The board stays disconnected throughout.",
                         "derived_from_circuit_data": True},
        "evidence_card": {"prompt": "Tick each place you can identify on the board.",
                          "child_records": ["group found"]},
    }
    lines, derived = domain_fact_lines(unit["domain"])
    body = "\n".join(lines)
    assert "Find one five-hole group." in body
    assert "centre trench" in body and "centre_trench" not in body
    assert "The board stays disconnected throughout." in body
    unit["derived"] = derived
    from curriculum_factory.checks import check_derivation
    assert check_derivation(unit)
