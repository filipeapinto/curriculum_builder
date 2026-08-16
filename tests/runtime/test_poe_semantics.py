"""Section 5 of plans/runtime_integrity_remediation — Predict-Observe-Explain semantics.

Covers issue 005: for each unit, the prediction, the observation, the evidence fields, the
explanation and the visuals all name the same event, and a block whose only evidence is
"look at the answer map" is rejected.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from tests.runtime import unit_fixture

ENGINE = unit_fixture.ENGINE
RUN = unit_fixture.RUN_FIXTURE

# The named event each unit's whole POE cycle has to be about, as words that must appear
# together across the prediction, the observation, the evidence fields and the explanation.
SHARED_EVENT = {
    "L02": {"clip", "trench"},
    "L03": {"wire", "expansion"},
    "L04": {"socket", "dial"},
}


def _unit(unit_id):
    return json.loads((RUN / unit_id / "lab.json").read_text())


def poe_violations(lab: dict) -> list[str]:
    """A POE block earns its name only when every part of it refers to one real event."""
    problems: list[str] = []
    explore = lab["sequence"]["explore"]
    observe = explore["observe"]
    fields = observe.get("evidence_fields") or []
    if not fields:
        problems.append("poe-no-evidence-fields: the learner is given nowhere to record what they found")
    visuals = lab.get("visuals", [])
    if not any(visual["supports_section"] in {"explore", "assembly", "identification"}
               for visual in visuals):
        problems.append("poe-no-observable-subject: no visual supports the section the learner observes in")
    only_map = [visual for visual in visuals
                if visual["role"] == "assembly_or_path_map"] == visuals
    if only_map and not fields:
        problems.append("poe-answer-map-only: the only referenced visual is the assembly map itself")
    if explore["predict"].get("recorded_before_observing") is not True:
        problems.append("poe-prediction-not-committed: the prediction is not recorded before observing")
    return problems


@pytest.mark.parametrize("unit_id", ["L02", "L03", "L04"])
def test_the_whole_cycle_names_the_same_event(unit_id):
    lab = _unit(unit_id)
    explore = lab["sequence"]["explore"]
    words = SHARED_EVENT[unit_id]
    observed = " ".join([explore["observe"]["what_to_observe"],
                         " ".join(explore["observe"]["evidence_fields"]),
                         explore["expected_observation"],
                         lab["sequence"]["explain"]["what_you_saw"]]).lower()
    for word in words:
        assert word in observed, f"{unit_id}: '{word}' is not named across the whole cycle"


@pytest.mark.parametrize("unit_id", ["L02", "L03", "L04"])
def test_evidence_fields_record_the_prediction_and_the_named_locations(unit_id):
    lab = _unit(unit_id)
    fields = lab["sequence"]["explore"]["observe"]["evidence_fields"]
    assert any("prediction" in field.lower() for field in fields), \
        f"{unit_id}: the learner is never asked to record their own prediction"
    assert len(fields) >= 3, f"{unit_id}: too few things to record for the cycle to be evidence"


@pytest.mark.parametrize("unit_id", ["L02", "L03", "L04"])
def test_the_visuals_support_the_section_the_observation_happens_in(unit_id):
    lab = _unit(unit_id)
    sections = {visual["supports_section"] for visual in lab["visuals"]}
    assert "assembly" in sections, f"{unit_id}: no map supports the assembly the learner traces"
    assert poe_violations(lab) == []


def test_l02_observes_the_cutaway_the_map_actually_renders():
    lab = _unit("L02")
    assert lab["domain"]["build_map"]["map_kind"] == "breadboard"
    observe = lab["sequence"]["explore"]["observe"]["what_to_observe"].lower()
    assert "cutaway" in observe
    records = " ".join(lab["domain"]["build_map"]["evidence_card"]["child_records"]).lower()
    assert "five holes" in records and "trench" in records


def test_l03_separates_the_wire_pair_from_the_expansion_row():
    lab = _unit("L03")
    build_map = lab["domain"]["build_map"]
    assert build_map["relationship"] == "same_wire"
    assert len(build_map["traced_path"]) == 3
    observe = lab["sequence"]["explore"]["observe"]["what_to_observe"].lower()
    assert "two ends" in observe or "both" in observe
    assert "on its own" in observe or "joined to nothing" in observe
    fields = " ".join(lab["sequence"]["explore"]["observe"]["evidence_fields"]).lower()
    assert "expansion row" in fields
    assert "not connected" not in lab["sequence"]["explain"]["what_you_saw"].lower()


def test_l04_observes_the_jack_and_dial_diagram_and_takes_no_measurement():
    lab = _unit("L04")
    assert lab["domain"]["build_map"]["relationship"] == "enumeration"
    observe = lab["sequence"]["explore"]["observe"]["what_to_observe"].lower()
    assert "diagram" in observe
    assert "switched off" in observe or "meter off" in observe or "no measurement" in observe
    fields = " ".join(lab["sequence"]["explore"]["observe"]["evidence_fields"]).lower()
    assert "socket" in fields and "dial" in fields


def test_a_look_at_the_answer_map_block_is_rejected():
    """The exact failure mode issue 005 names: the map is the only evidence and records nothing."""
    lab = _unit("L03")
    lab["sequence"]["explore"]["observe"]["evidence_fields"] = []
    lab["visuals"] = [visual for visual in lab["visuals"]
                      if visual["role"] == "assembly_or_path_map"]
    problems = poe_violations(lab)
    assert any("poe-answer-map-only" in problem for problem in problems)
    assert any("poe-no-evidence-fields" in problem for problem in problems)


def test_an_uncommitted_prediction_is_rejected():
    lab = _unit("L02")
    lab["sequence"]["explore"]["predict"]["recorded_before_observing"] = False
    assert any("poe-prediction-not-committed" in problem for problem in poe_violations(lab))


_FUNCTION_WORDS = {
    "about", "across", "after", "again", "against", "already", "although", "another", "anything",
    "because", "before", "being", "below", "between", "could", "different", "during", "each",
    "either", "every", "further", "having", "here", "into", "itself", "might", "must", "neither",
    "other", "over", "same", "should", "since", "some", "such", "than", "that", "their", "them",
    "then", "there", "these", "they", "this", "those", "through", "throughout", "under", "until",
    "were", "what", "when", "where", "which", "while", "with", "within", "without", "would", "your",
}


def _stems(text: str) -> set[str]:
    """Crude stems, so 'socket' and 'sockets' are the same noun to this test."""
    found = set()
    for word in re.findall(r"[a-z]{4,}", text.lower()):
        if word in _FUNCTION_WORDS:
            continue
        for suffix in ("ing", "ed", "es", "s"):
            if word.endswith(suffix) and len(word) - len(suffix) >= 4:
                word = word[: -len(suffix)]
                break
        found.add(word)
    return found


@pytest.mark.parametrize("unit_id", ["L02", "L03", "L04"])
def test_no_explanation_asserts_a_result_the_steps_never_exposed(unit_id):
    """`what_you_saw` may only name things the steps or the map actually put in front of the learner."""
    lab = _unit(unit_id)
    explore = lab["sequence"]["explore"]
    exposed = _stems(" ".join(
        [step["action"] for step in explore["steps"]]
        + explore["observe"]["evidence_fields"]
        + [explore["observe"]["what_to_observe"], explore["expected_observation"]]
        + lab["domain"]["build_map"]["evidence_card"]["child_records"]))
    missing = sorted(_stems(lab["sequence"]["explain"]["what_you_saw"]) - exposed
                     - _stems(" ".join(part["label"] for part
                                       in lab["content"]["identification"]["parts"])))
    # A handful of ordinary verbs of seeing are not claims about the subject.
    missing = [word for word in missing
               if word not in {"found", "chos", "saw", "look", "point", "trac", "took"}]
    assert missing == [], f"{unit_id}: the explanation names {missing}, which no step or field exposed"
