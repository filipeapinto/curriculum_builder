"""Section 3 of plans/runtime_integrity_remediation — fail-closed acceptance.

Covers issue 002: the required set is built from the two real check catalogues, every id
gets one explicit result, a check that cannot reach its subject records NOT_RUN_BLOCKED
rather than PASS, a cross-family bypass cannot coexist with ACCEPTED, and re-entry is
opt-in.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil

import jsonschema
import pytest
import yaml

from runtime.checks import CheckFailure, required_checks_for
from runtime.logger import LogError
from runtime.session_bridge import finalize
from tests.runtime import unit_fixture

ENGINE = unit_fixture.ENGINE
CURRICULUM = unit_fixture.CURRICULUM


def _accepted_unit(tmp_path, unit_id="L02"):
    """A unit whose every role resolves — the baseline the negative fixtures perturb."""
    lab = unit_fixture.lab_from_run(unit_id)
    run_root, unit_root = unit_fixture.build_run(tmp_path, unit_id=unit_id, lab=lab)
    return run_root, unit_root


# --- the required set is the catalogue's, not a hardcoded dict ------------------------

def test_required_set_is_built_from_both_catalogues():
    inventory = required_checks_for(ENGINE, CURRICULUM)
    required = inventory["required"]
    for check_id in ("LAB-SCHEMA-VALID", "TEXT-READABILITY-BAND", "TEXT-BLOOM-VERBS",
                     "DOC-DERIVED-FROM-SOURCE", "RECEIPT-HASH-RESOLVES", "PDF-ASSET-RESOLVES",
                     "PDF-TEXT-LEGIBLE", "PDF-VISUAL-REVIEW"):
        assert required[check_id]["source"] == "engine"
        assert required[check_id]["asserts"], "the catalogue's own assertion text is carried through"
    for check_id in ("DOMAIN-VERIFIER", "VISUAL-ROLES-COMPLETE"):
        assert required[check_id]["source"] == "curriculum"
    assert required["TEXT-BLOOM-VERBS"]["blocking"] is False, "this check flags and never blocks"
    assert inventory["checks_version"] == {"engine": "1.0", "curriculum": "1.0"}


def test_an_uncatalogued_required_id_is_a_hard_error(tmp_path):
    scratch = tmp_path / "curriculum"
    shutil.copytree(CURRICULUM, scratch)
    catalogue = yaml.safe_load((scratch / "checks.v1.yaml").read_text())
    catalogue["lab_document"] = [entry for entry in catalogue["lab_document"]
                                 if entry["id"] != "DOMAIN-VERIFIER"]
    (scratch / "checks.v1.yaml").write_text(yaml.safe_dump(catalogue))
    with pytest.raises(CheckFailure) as raised:
        required_checks_for(ENGINE, scratch)
    assert "DOMAIN-VERIFIER" in str(raised.value)


# --- the two new curriculum ids are schema- and stage-legal ---------------------------

def test_curriculum_catalogue_validates_and_stages_the_two_new_ids():
    schema = json.loads((ENGINE / "schemas/checks.schema.v1.json").read_text())
    catalogue = yaml.safe_load((CURRICULUM / "checks.v1.yaml").read_text())
    errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(catalogue)]
    assert errors == []

    entries = {entry["id"]: entry
               for value in catalogue.values() if isinstance(value, list)
               for entry in value if isinstance(entry, dict) and "id" in entry}
    assert entries["DOMAIN-VERIFIER"]["stage"] == "deterministic"
    assert entries["DOMAIN-VERIFIER"]["verified_by"] == "FR-P5-VERIFIER-REQUIRED"
    assert "deferred" not in entries["DOMAIN-VERIFIER"]
    assert entries["VISUAL-ROLES-COMPLETE"]["stage"] == "deterministic"
    assert entries["VISUAL-ROLES-COMPLETE"]["deferred"] == "RT-5"
    assert "verified_by" not in entries["VISUAL-ROLES-COMPLETE"]

    deterministic = next(row for row in catalogue["release"] if row["stage"] == "deterministic")
    static = next(row for row in catalogue["release"] if row["stage"] == "static")
    assert "DOMAIN-VERIFIER" in deterministic["advertises"]
    assert "VISUAL-ROLES-COMPLETE" in deterministic["advertises"]
    assert "DOMAIN-VERIFIER" not in static["advertises"]
    assert "VISUAL-ROLES-COMPLETE" not in static["advertises"]


# --- every id gets one explicit result ------------------------------------------------

def test_every_required_check_gets_one_explicit_result(tmp_path):
    _, unit_root = _accepted_unit(tmp_path)
    finalize(ENGINE, unit_root, curriculum=CURRICULUM)
    record = json.loads((unit_root / "results/unit_checks.json").read_text())
    required = set(required_checks_for(ENGINE, CURRICULUM)["required"])
    assert set(record["checks"]) == required, "no id is silently absent"
    for check_id, entry in record["checks"].items():
        assert entry["result"] in {"PASS", "FAIL", "NOT_RUN_BLOCKED"}, check_id
        assert entry["reason"], f"{check_id} records a result with no reason"
    assert record["checks_version"] == {"engine": "1.0", "curriculum": "1.0"}
    assert "DOMAIN-SCHEMA-VALID" not in record["checks"], "no uncatalogued id is invented"


# --- (a) a raw-JSON body is rejected --------------------------------------------------

def test_a_field_with_no_template_branch_is_rejected_through_the_gate(tmp_path):
    """The route by which raw JSON used to reach the page is closed at both ends."""
    from runtime.lesson_render import RendererError
    lab = unit_fixture.lab_from_run("L02")
    lab["sequence"]["explain"]["serialized_leftovers"] = '{"what_you_saw": "raw json"}'
    _, unit_root = unit_fixture.build_run(tmp_path, unit_id="L02", lab=lab)
    with pytest.raises((RendererError, jsonschema.ValidationError)):
        finalize(ENGINE, unit_root, curriculum=CURRICULUM)


def test_the_shipped_document_carries_no_serialized_object_syntax(tmp_path):
    _, unit_root = _accepted_unit(tmp_path)
    finalize(ENGINE, unit_root, curriculum=CURRICULUM)
    body = (unit_root / "document/L02.md").read_text()
    assert "{" not in body and "}" not in body and '":' not in body
    for field in ("recorded_before_observing", "what_you_saw", "safe_first_check",
                  "record_method", "hinge_question"):
        assert field not in body


# --- (b) an irrelevant image is rejected by PDF-ASSET-RESOLVES ------------------------

def test_an_irrelevant_image_is_rejected_by_pdf_asset_resolves(tmp_path):
    """An asset swapped after the PDF shipped: the receipt names a picture the PDF lacks."""
    import hashlib
    from PIL import Image
    from runtime import pdf_inspect
    lab = unit_fixture.lab_from_run("L02")
    _, unit_root = unit_fixture.build_run(tmp_path, unit_id="L02", lab=lab)
    finalize(ENGINE, unit_root, curriculum=CURRICULUM)
    pdf = unit_root / "document/L02.pdf"
    lab = json.loads((unit_root / "workers/lab.json").read_text())

    clean = pdf_inspect.assets_resolve(pdf, lab["visuals"], unit_root, tmp_path / "clean")
    assert clean["problems"] == []

    photo = next(v for v in lab["visuals"] if v["source_kind"] == "verified_photograph")
    swapped = unit_root / photo["provenance"]["embedded_as"]
    Image.new("RGB", (900, 600), (11, 22, 33)).save(swapped, quality=92)
    photo["provenance"]["file_hash"] = hashlib.sha256(swapped.read_bytes()).hexdigest()

    dirty = pdf_inspect.assets_resolve(pdf, lab["visuals"], unit_root, tmp_path / "dirty")
    assert any("no image in the shipped PDF matches the receipted picture" in problem
               for problem in dirty["problems"])


def test_a_receipt_that_stops_resolving_aborts_before_acceptance(tmp_path):
    """The receipt/bytes link is a hard abort, not a warning — no acceptance.json is written."""
    from PIL import Image
    lab = unit_fixture.lab_from_run("L02")
    _, unit_root = unit_fixture.build_run(tmp_path, unit_id="L02", lab=lab)
    lab = json.loads((unit_root / "workers/lab.json").read_text())
    photo = next(v for v in lab["visuals"] if v["source_kind"] == "verified_photograph")
    Image.new("RGB", (900, 600), (11, 22, 33)).save(unit_root / photo["provenance"]["embedded_as"],
                                                    quality=92)
    with pytest.raises(CheckFailure) as raised:
        finalize(ENGINE, unit_root, curriculum=CURRICULUM)
    assert "receipt-hash-mismatch" in str(raised.value)
    assert not (unit_root / "acceptance.json").exists()


# --- (c) clipped or undersized text is rejected by PDF-TEXT-LEGIBLE -------------------

def test_undersized_text_is_rejected_by_pdf_text_legible(tmp_path):
    """A visual whose labels are too small once the page scales it down."""
    import runtime.visual_maps as visual_maps
    from runtime import pdf_inspect
    lab = unit_fixture.lab_from_run("L02")
    _, unit_root = unit_fixture.build_run(tmp_path, unit_id="L02", lab=lab, regenerate=False)
    original = visual_maps.BODY, visual_maps.LABEL, visual_maps.SMALL, visual_maps.SUB
    visual_maps.BODY = visual_maps.LABEL = visual_maps.SMALL = visual_maps.SUB = 12
    try:
        lab, _ = visual_maps.regenerate_assets(lab, CURRICULUM, unit_root, unit_id="L02")
    finally:
        visual_maps.BODY, visual_maps.LABEL, visual_maps.SMALL, visual_maps.SUB = original
    (unit_root / "workers/lab.json").write_text(json.dumps(lab, indent=2))

    summary = finalize(ENGINE, unit_root, curriculum=CURRICULUM)
    record = json.loads((unit_root / "results/unit_checks.json").read_text())["checks"]
    assert record["PDF-TEXT-LEGIBLE"]["result"] == "FAIL"
    assert "below 9.0pt" in record["PDF-TEXT-LEGIBLE"]["reason"]
    assert summary["terminal_state"] != "ACCEPTED"
    assert pdf_inspect.MIN_POINT_SIZE == 9.0


# --- (d) a check with no implementation for its subject records NOT_RUN_BLOCKED -------

def test_a_check_that_cannot_reach_its_subject_records_not_run_blocked(tmp_path):
    _, unit_root = _accepted_unit(tmp_path)
    summary = finalize(ENGINE, unit_root, curriculum=CURRICULUM)
    record = json.loads((unit_root / "results/unit_checks.json").read_text())["checks"]
    assert record["PDF-VISUAL-REVIEW"]["result"] == "NOT_RUN_BLOCKED", (
        "no reviewer has filled the verdict, so the check never reached its subject")
    assert record["PDF-VISUAL-REVIEW"]["result"] != "PASS"
    assert summary["terminal_state"] != "ACCEPTED"
    assert "PDF-VISUAL-REVIEW" in summary["blocking_failures"]


def test_a_filled_reviewer_verdict_lets_the_check_pass(tmp_path):
    _, unit_root = _accepted_unit(tmp_path)
    finalize(ENGINE, unit_root, curriculum=CURRICULUM)
    unit_fixture.fill_visual_review(unit_root)
    finalize(ENGINE, unit_root, reentry_reason="reviewer verdict now filled in",
             curriculum=CURRICULUM)
    record = json.loads((unit_root / "results/unit_checks.json").read_text())["checks"]
    assert record["PDF-VISUAL-REVIEW"]["result"] == "PASS"


def test_a_failed_reviewer_criterion_blocks(tmp_path):
    _, unit_root = _accepted_unit(tmp_path)
    finalize(ENGINE, unit_root, curriculum=CURRICULUM)
    unit_fixture.fill_visual_review(unit_root, verdict="fail")
    summary = finalize(ENGINE, unit_root, reentry_reason="reviewer rejected the pages",
                       curriculum=CURRICULUM)
    record = json.loads((unit_root / "results/unit_checks.json").read_text())["checks"]
    assert record["PDF-VISUAL-REVIEW"]["result"] == "FAIL"
    assert summary["terminal_state"] == "BLOCKED"


# --- (e) a cross-family bypass cannot coexist with ACCEPTED ---------------------------

def test_a_cross_family_bypass_forces_a_non_accepted_terminal_state(tmp_path):
    from runtime.lesson_render import derived_records
    _, unit_root = _accepted_unit(tmp_path)
    finalize(ENGINE, unit_root, curriculum=CURRICULUM)
    unit_fixture.fill_visual_review(unit_root)
    lab = json.loads((unit_root / "workers/lab.json").read_text())
    lab["content"]["derived"] = derived_records(lab)
    (unit_root / "workers/lab.json").write_text(json.dumps(lab, indent=2))

    summary = finalize(ENGINE, unit_root, reentry_reason="score with every check reachable",
                       curriculum=CURRICULUM)
    assert summary["blocking_failures"] == [], summary["blocking_failures"]
    assert "cross-family judge bypassed" in summary["routing_divergence"]
    assert summary["terminal_state"] == "ACCEPTED_PENDING_REVIEW"
    assert summary["terminal_state"] != "ACCEPTED", (
        "the disclosure string no longer co-exists with ACCEPTED")


# --- (f) re-entry is opt-in -----------------------------------------------------------

def test_finalize_twice_with_a_reentry_reason_succeeds(tmp_path):
    _, unit_root = _accepted_unit(tmp_path)
    first = finalize(ENGINE, unit_root, curriculum=CURRICULUM)
    second = finalize(ENGINE, unit_root, reentry_reason="regenerated under section 9",
                      curriculum=CURRICULUM)
    assert second["reentry_reason"] == "regenerated under section 9"
    assert second["terminal_state"] == first["terminal_state"]
    assert (unit_root / "document/assets").is_dir()


def test_finalize_twice_without_a_reentry_reason_still_raises(tmp_path):
    _, unit_root = _accepted_unit(tmp_path)
    finalize(ENGINE, unit_root, curriculum=CURRICULUM)
    with pytest.raises(LogError):
        finalize(ENGINE, unit_root, curriculum=CURRICULUM)


def test_reentry_opens_a_new_act_and_never_reuses_the_closed_one(tmp_path):
    _, unit_root = _accepted_unit(tmp_path)
    finalize(ENGINE, unit_root, curriculum=CURRICULUM)
    original = json.loads((unit_root / "worker_request.json").read_text())["model_start_id"]
    finalize(ENGINE, unit_root, reentry_reason="second pass", curriculum=CURRICULUM)
    records = [json.loads(line) for line in
               (unit_root / "execution_log.jsonl").read_text().splitlines()]
    closes = [record["closes"] for record in records if "closes" in record]
    assert closes.count(original) == 1, "the original ACT is closed exactly once, ever"
    resumes = [record for record in records if record.get("action_kind") == "resume"]
    assert resumes, "re-entry opens its own ACT"
