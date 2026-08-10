"""Section 2 of plans/runtime_integrity_remediation — the role- and map-kind-driven pipeline.

Covers issue 003: asset selection follows the declared role and the domain's own map kind,
a same-wire pair renders as connected, an enumeration renders as unjoined points, an
unrecognized map kind fails the unit, and an unresolvable role blocks it rather than being
filled with an unrelated asset.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.visual_maps import (VisualMapError, classify_role, load_photo_regions,
                                 match_photo_subject, regenerate_assets, render_breadboard,
                                 render_enumeration, render_evidence_card, render_map,
                                 render_parts_diagram, render_power_path, render_same_wire)
from tests.runtime import unit_fixture

ENGINE = unit_fixture.ENGINE
CURRICULUM = unit_fixture.CURRICULUM


def _connectivity(traced, relationship):
    return {"map_kind": "connectivity", "relationship": relationship, "traced_path": traced,
            "evidence_card": {"prompt": "Tick each place you can identify on the board.",
                              "child_records": ["first place found"]},
            "power_on_release": False}


# --- one test per (map_kind, relationship) -------------------------------------------

def test_power_path_renders_a_directed_sequence_with_truthful_edge_labels():
    svg = render_power_path({"traced_path": ["source lead end", "module DC input", "rail"]},
                            {"circuit": {"status": "not_designed"}})
    assert "source lead end" in svg and "module DC input" in svg
    assert "not yet connected" in svg
    assert "NOT CONNECTED" not in svg
    assert svg.count("<path") == 2, "one arrow head per edge"


def test_power_path_says_carries_current_only_for_a_verified_circuit():
    svg = render_power_path({"traced_path": ["a", "b"]}, {"circuit": {"status": "designed_verified"}})
    assert "carries current" in svg


def test_same_wire_connects_exactly_the_first_two_items():
    svg = render_same_wire({"traced_path": ["wire endpoint a", "wire endpoint b"]})
    assert "same wire" in svg
    assert "stroke-dasharray" in svg
    assert "Also find, on its own" not in svg


def test_same_wire_with_three_items_matches_l03s_real_shape():
    """Items 0 and 1 are the connected dashed pair; item 2 is its own unconnected point."""
    build_map = _connectivity(["wire endpoint a", "wire endpoint b", "expansion board row"], "same_wire")
    svg = render_map({"build_map": build_map, "electrical": {}})
    assert "wire endpoint a" in svg and "wire endpoint b" in svg
    assert "expansion board row" in svg, "the third item must not be dropped"
    assert svg.count("stroke-dasharray") == 1, "only the wire pair is joined by the dashed link"
    assert "Also find, on its own — not joined to the wire:" in svg
    # The third item is rendered after the dashed pair, as its own labelled point.
    assert svg.index("expansion board row") > svg.index("same wire — one piece of metal")


def test_enumeration_joins_nothing():
    build_map = _connectivity(["com socket", "v omega ma socket", "ten a socket", "mode dial"],
                              "enumeration")
    svg = render_map({"build_map": build_map, "electrical": {}})
    for item in build_map["traced_path"]:
        assert item in svg
    assert "stroke-dasharray" not in svg
    assert "<line" not in svg, "an enumeration draws no connecting line at all"


def test_connectivity_without_a_relationship_fails_rather_than_guessing():
    with pytest.raises(VisualMapError) as raised:
        render_map({"build_map": {"map_kind": "connectivity", "traced_path": ["a", "b"]},
                    "electrical": {}})
    assert "relationship" in str(raised.value)


def test_breadboard_renders_clip_groups_the_trench_and_the_rail_break():
    svg = render_breadboard({
        "map_kind": "breadboard", "orientation": "rails top and bottom",
        "labelled_features": ["rows", "columns", "rails", "centre_trench", "rail_breaks"],
        "wire_endpoints": [{"from": "a1", "to": "e1"}],
        "placement_steps": ["Find one five-hole group."], "schematic_included": True,
        "safety_inset": {"shows": "The board stays disconnected throughout.",
                         "derived_from_circuit_data": True}})
    assert "one clip joins these five holes" in svg
    assert "centre trench — no clip crosses this gap" in svg
    assert "rail break — the rail stops part-way along, here" in svg
    assert "The board stays disconnected throughout." in svg


def test_unrecognized_map_kind_fails_the_unit():
    with pytest.raises(VisualMapError) as raised:
        render_map({"build_map": {"map_kind": "mystery", "traced_path": ["a"]}, "electrical": {}})
    assert "mystery" in str(raised.value)


# --- evidence card -------------------------------------------------------------------

def test_evidence_card_reflects_the_units_own_child_records():
    svg = render_evidence_card({"evidence_card": {
        "prompt": "Tick each socket you can find on the meter.",
        "child_records": ["COM socket found", "mode dial found"]}}, signoff_required=True)
    assert "COM socket found" in svg and "mode dial found" in svg
    assert "Adult signature" in svg
    for generic in ("Trace each dashed teaching link", "Tick each place you can identify",
                    "Keep every connection open"):
        assert generic not in svg, "the three hardcoded generic lines must be gone"


def test_evidence_card_without_records_fails_rather_than_shipping_empty():
    with pytest.raises(VisualMapError):
        render_evidence_card({"evidence_card": {"prompt": "x", "child_records": []}},
                             signoff_required=False)


def test_parts_diagram_names_only_fields_the_unit_declares():
    svg = render_parts_diagram([{"label": "centre trench", "role": "Keeps the two sides apart."}],
                               subject="breadboard")
    assert "centre trench" in svg and "Keeps the two sides apart." in svg


# --- role resolution -----------------------------------------------------------------

@pytest.mark.parametrize("role,expected", [
    ("verified photorealistic kit-identification photograph", "photograph"),
    ("safe disconnected setup photograph", "photograph"),
    ("deterministic verified power-path and orientation map", "map"),
    ("child tick-box evidence card", "evidence_card"),
    ("photorealistic breadboard", "photograph"),
    ("cutaway clip illustration", "diagram"),
    ("deterministic connectivity map", "map"),
    ("rail-break warning", "safety"),
    ("photorealistic wire types", "photograph"),
    ("connection endpoint diagram", "diagram"),
    ("deterministic route overlay", "map"),
    ("loose-wire hazard", "safety"),
    ("photorealistic meter", "photograph"),
    ("deterministic jack-and-dial map", "map"),
    ("probe placement diagram", "diagram"),
    ("current-mode red-X", "safety"),
])
def test_every_declared_role_in_l01_l04_classifies(role, expected):
    assert classify_role(role) == expected


def test_a_role_with_no_renderer_class_fails_closed():
    with pytest.raises(VisualMapError):
        classify_role("interpretive dance")


def test_photo_subject_resolution_matches_what_the_photograph_actually_contains():
    regions = load_photo_regions(CURRICULUM)
    assert match_photo_subject("photorealistic breadboard", regions)[0] == "resolved"
    assert match_photo_subject("photorealistic wire types", regions)[0] == "resolved"
    assert match_photo_subject("verified photorealistic kit-identification photograph", regions)[0] == "resolved"
    assert match_photo_subject("photorealistic meter", regions)[0] == "absent"
    assert match_photo_subject("safe disconnected setup photograph", regions)[0] == "absent"


# --- end to end ----------------------------------------------------------------------

def test_regenerate_assets_selects_by_role_and_keeps_receipts_in_step(tmp_path):
    lab = unit_fixture.lab_from_run("L02")
    _, unit_root = unit_fixture.build_run(tmp_path, unit_id="L02", lab=lab, regenerate=False)
    lab, unresolved = regenerate_assets(lab, CURRICULUM, unit_root, unit_id="L02")

    assert unresolved == [], "every L02 role resolves once the breadboard crop is declared"
    names = sorted(path.name for path in (unit_root / "assets").iterdir())
    assert "path_map.svg" in names and "evidence_card.svg" in names
    assert "photo_breadboard.jpg" in names
    assert "official_reference.jpg" not in names, "the whole-kit shot is no longer substituted"

    import hashlib
    for visual in lab["visuals"]:
        path = unit_root / visual["provenance"]["embedded_as"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == visual["provenance"]["file_hash"]

    photo = next(v for v in lab["visuals"] if v["source_kind"] == "verified_photograph")
    assert any("breadboard" in step for step in photo["provenance"]["crop_transform_history"])


def test_an_unresolvable_role_is_recorded_rather_than_substituted(tmp_path):
    lab = unit_fixture.lab_from_run("L04")
    _, unit_root = unit_fixture.build_run(tmp_path, unit_id="L04", lab=lab, regenerate=False)
    lab, unresolved = regenerate_assets(lab, CURRICULUM, unit_root, unit_id="L04")

    assert [entry["role"] for entry in unresolved] == ["photorealistic meter"]
    assert "multimeter" in unresolved[0]["reason"]
    assert lab["content"]["unresolved_visual_roles"] == unresolved
    assert not any(v["source_kind"] == "verified_photograph" for v in lab["visuals"]), \
        "an unresolved photographic role ships no photograph at all, not a substitute"
    assert not (unit_root / "assets/official_reference.jpg").exists()


def test_an_unresolvable_role_writes_a_blocked_acceptance_rather_than_raising(tmp_path):
    """The graceful path: finalize() reaches its acceptance.json write and records BLOCKED."""
    lab = unit_fixture.lab_from_run("L04")
    _, unit_root = unit_fixture.build_run(tmp_path, unit_id="L04", lab=lab)
    from runtime.session_bridge import finalize
    summary = finalize(ENGINE, unit_root, curriculum=CURRICULUM)

    assert summary["terminal_state"] == "BLOCKED"
    assert (unit_root / "acceptance.json").is_file()
    assert "photorealistic meter" in json.dumps(summary["unresolved_visual_roles"])
    assert "photorealistic meter" in summary["claim"]
