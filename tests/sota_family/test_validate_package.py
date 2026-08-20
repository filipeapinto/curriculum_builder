import json
from pathlib import Path

from tools.sota_family.validate_package import validate


PLAN = """<!doctype html><html><body>{}</body></html>""".format("".join(f'<section id="{x}"></section>' for x in ("decision", "scope", "method", "flow", "roles", "allocation", "budget", "outputs", "tests", "approval")))
STATES = {"study_id":"S-1","plan_id":"P-1","run_id":"R-1","research_support":"SUPPORTED","execution":"COMPLETE","verification":"PASS","human_acceptance":"PENDING","implementation_authority":"NONE"}


def make_study(tmp_path: Path) -> Path:
    root = tmp_path / "study"
    (root / "plan").mkdir(parents=True)
    run = root / "runs" / "R-1"
    run.mkdir(parents=True)
    (root / "plan" / "study.plan.v1.html").write_text(PLAN, encoding="utf-8")
    (run / "report.html").write_text(f'<script type="application/json" id="sota-state-envelope">{json.dumps(STATES)}</script>', encoding="utf-8")
    common = {"date":"2026-08-20","action":"Run family validation fixture","action_kind":"test","input_quality":"complete","authorized_paths":[str(root)],"trigger":"fixture setup","expected":"family validation passes"}
    records = [
        {**common,"id":"ACT-001","status":"started","result":"pending"},
        {**common,"id":"ACT-002","status":"completed","closes":"ACT-001","result":"validation passed"}
    ]
    (run / "execution-log.json").write_text(json.dumps({"log_version":"2.0","records":records,"unclosed_starts":[]}), encoding="utf-8")
    return root


def test_minimal_and_complex_packages_pass(tmp_path):
    root = make_study(tmp_path)
    assert validate(root) == []
    (root / "runs" / "R-1" / "evidence").mkdir()
    assert validate(root) == []


def test_missing_required_file_fails(tmp_path):
    root = make_study(tmp_path)
    (root / "runs" / "R-1" / "report.html").unlink()
    assert any("missing report.html" in error for error in validate(root))


def test_combined_or_missing_state_fails(tmp_path):
    root = make_study(tmp_path)
    report = root / "runs" / "R-1" / "report.html"
    bad = dict(STATES); bad.pop("human_acceptance")
    report.write_text(f'<script id="sota-state-envelope">{json.dumps(bad)}</script>', encoding="utf-8")
    assert any("human_acceptance" in error for error in validate(root))


def test_unpaired_activity_fails(tmp_path):
    root = make_study(tmp_path)
    log = root / "runs" / "R-1" / "execution-log.json"
    record = {"id":"ACT-001","date":"2026-08-20","action":"Run incomplete fixture action","action_kind":"test","status":"started","input_quality":"complete","authorized_paths":[str(root)],"trigger":"fixture setup","expected":"failure is detected","result":"pending"}
    log.write_text(json.dumps({"log_version":"2.0","records":[record],"unclosed_starts":[]}), encoding="utf-8")
    assert any("unclosed activities" in error for error in validate(root))


def test_same_seeded_defect_has_same_family_outcome(tmp_path):
    first = make_study(tmp_path / "minimal")
    second = make_study(tmp_path / "complex")
    for root in (first, second):
        (root / "runs" / "R-1" / "report.html").unlink()
    assert validate(first) == validate(second)
