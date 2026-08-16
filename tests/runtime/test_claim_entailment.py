"""Section 6 of plans/runtime_integrity_remediation — source-claim entailment.

Covers issue 006: a claim's locator has to resolve inside the cached source bytes and the
located text has to support the bounded claim. A device-specific claim cited against a
source naming a different model, an unsupported number with no derivation behind it, and a
locator pointing at text the source does not contain are each rejected.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from curriculum_factory.checks import CheckFailure, check_claim_entailment
from tests.runtime import unit_fixture

ENGINE = unit_fixture.ENGINE
FIXTURES = ENGINE / "tests/fixtures"
SOURCE_ROOT = FIXTURES / "unit_claim_source"
RUN = unit_fixture.RUN_FIXTURE


def _fixture(name):
    return json.loads((FIXTURES / name).read_text())


@pytest.mark.parametrize("name,expected_code", [
    ("unit_claim_wrong_device.reject.json", "claim-wrong-device"),
    ("unit_claim_unsupported_number.reject.json", "claim-unsupported-number"),
    ("unit_claim_out_of_scope_source.reject.json", "claim-locator-text-absent"),
])
def test_reject_fixtures_are_rejected_for_the_right_reason(name, expected_code):
    with pytest.raises(CheckFailure) as raised:
        check_claim_entailment(_fixture(name), SOURCE_ROOT)
    assert expected_code in str(raised.value)


def test_the_accept_fixture_is_accepted():
    resolved = check_claim_entailment(_fixture("unit_claim_valid_exact_model.accept.json"),
                                      SOURCE_ROOT)
    assert len(resolved) == 1
    assert resolved[0]["derived"] is False


def test_a_derived_number_is_accepted_only_with_its_premises():
    unit = _fixture("unit_claim_unsupported_number.reject.json")
    with pytest.raises(CheckFailure):
        check_claim_entailment(unit, SOURCE_ROOT)
    unit["content"]["sourced_claims"][0]["derivation"] = {"premises": [
        "The cited guide states a good-quality breadboard is generally limited to around 2 A.",
        "1 A is half that figure, chosen as a deliberately conservative planning limit."]}
    resolved = check_claim_entailment(unit, SOURCE_ROOT)
    assert resolved[0]["derived"] is True


def test_a_numeric_rating_with_no_sourced_claim_at_all_is_rejected():
    unit = _fixture("unit_claim_valid_exact_model.accept.json")
    unit["domain"]["electrical"]["ratings_and_limits"].append(
        {"parameter": "invented ceiling", "absolute_max": "47", "unit": "V", "source": "recollection"})
    with pytest.raises(CheckFailure) as raised:
        check_claim_entailment(unit, SOURCE_ROOT)
    assert "claim-unsourced" in str(raised.value)


# --- the two concrete miscitations issue 006 names ------------------------------------

def test_l03s_jumper_rating_is_derived_with_premises_not_attributed():
    lab = json.loads((RUN / "L03/lab.json").read_text())
    rating = lab["domain"]["electrical"]["ratings_and_limits"][0]
    assert rating["absolute_max"] == "1" and rating["unit"] == "A"
    assert "derived" in rating["source"].lower()
    assert "2 A" in rating["source"], "the source says what it actually states, not 1 A"

    claim = next(entry for entry in lab["content"]["sourced_claims"]
                 if "1 A" in entry["claim"])
    assert claim["derivation"]["premises"], "the conservative figure carries its premises"
    assert len(claim["derivation"]["premises"]) >= 2
    assert "no jumper-wire current rating" in claim["evidence_scope"]


def _asserted(lab):
    """Everything the unit states, minus the entries whose job is to explain a correction."""
    trimmed = json.loads(json.dumps(lab))
    trimmed["content"].pop("sourced_claims", None)
    return json.dumps(trimmed)


def test_l03s_expansion_board_claim_is_scope_corrected():
    lab = json.loads((RUN / "L03/lab.json").read_text())
    assert "breadboard expansion board" not in _asserted(lab), \
        "the over-scoped 'expansion board is in the kit' claim is gone"
    claim = next(entry for entry in lab["content"]["sourced_claims"]
                 if "expansion row" in entry["claim"])
    assert "nothing about which board ships in any particular kit" in claim["evidence_scope"]


def test_l04_states_neither_removed_universal_claim():
    lab = json.loads((RUN / "L04/lab.json").read_text())
    blob = _asserted(lab)
    assert "200 mA" not in blob and "200mA" not in blob, \
        "the universal 200 mA threshold is gone"
    assert "shares one fuse" not in blob and "shares one small fuse" not in blob, \
        "the unsupported shared-fuse claim is gone"
    assert "10A socket" not in blob and "10 A socket" not in blob


@pytest.mark.parametrize("unit_id", ["L01", "L02", "L03", "L04"])
def test_every_shipped_unit_entails_its_own_numeric_claims(unit_id, tmp_path):
    lab = unit_fixture.lab_from_run(unit_id)
    _, unit_root = unit_fixture.build_run(tmp_path, unit_id=unit_id, lab=lab, regenerate=False)
    assert check_claim_entailment(lab, unit_root) is not None
