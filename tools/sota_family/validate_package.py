#!/usr/bin/env python3
"""Validate the non-waivable SOTA family package before plan-specific checks."""

import argparse
import json
import re
import sys
from pathlib import Path

import jsonschema

PLAN_MARKERS = ("decision", "scope", "method", "flow", "roles", "allocation", "budget", "outputs", "tests", "approval")
STATE_VALUES = {
    "research_support": {"SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE", "BLOCKED"},
    "execution": {"NOT_STARTED", "RUNNING", "BLOCKED", "FAILED", "COMPLETE"},
    "verification": {"NOT_RUN", "PASS", "FAIL", "BLOCKED"},
    "human_acceptance": {"PENDING", "ACCEPTED", "REJECTED", "REVISION_REQUESTED"},
    "implementation_authority": {"NONE", "LIMITED", "GRANTED", "REVOKED"},
}


def check_plan(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [f"plan missing universal section id={marker}" for marker in PLAN_MARKERS if not re.search(rf'id=["\']{marker}["\']', text)]


def check_log(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    schema_path = Path(__file__).resolve().parents[2] / "schemas" / "execution_log.schema.v2.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(data)
    except jsonschema.ValidationError as exc:
        errors.append(f"execution log schema failure: {exc.json_path}: {exc.message}")
    if data.get("log_version") != "2.0" or not isinstance(data.get("records"), list):
        return ["execution-log.json must use the repository v2 envelope"]
    starts = {r.get("id") for r in data["records"] if r.get("status") == "started"}
    closes = {r.get("closes") for r in data["records"] if r.get("closes")}
    if starts - closes:
        errors.append(f"unclosed activities: {sorted(starts - closes)}")
    for record in data["records"]:
        if record.get("action_kind") == "model_call" and not record.get("decision_id"):
            errors.append(f"model activity lacks decision_id: {record.get('id')}")
    return errors


def check_report(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<script[^>]+id=["\']sota-state-envelope["\'][^>]*>(.*?)</script>', text, re.S)
    if not match:
        return ["report missing script#sota-state-envelope"]
    states = json.loads(match.group(1))
    errors = []
    for field, allowed in STATE_VALUES.items():
        if states.get(field) not in allowed:
            errors.append(f"invalid or missing report state: {field}")
    return errors


def validate(root: Path) -> list[str]:
    errors = []
    plan_dir, runs_dir = root / "plan", root / "runs"
    plans = sorted(plan_dir.glob("*.plan.v*.html")) if plan_dir.is_dir() else []
    if not plans:
        errors.append("missing versioned plan under plan/")
    else:
        errors.extend(check_plan(plans[-1]))
    if not runs_dir.is_dir():
        return errors + ["missing runs/ directory"]
    for run in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
        report, log = run / "report.html", run / "execution-log.json"
        if not report.is_file(): errors.append(f"{run.name}: missing report.html")
        else: errors.extend(f"{run.name}: {e}" for e in check_report(report))
        if not log.is_file(): errors.append(f"{run.name}: missing execution-log.json")
        else: errors.extend(f"{run.name}: {e}" for e in check_log(log))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("study_root", type=Path)
    args = parser.parse_args()
    try: errors = validate(args.study_root)
    except (OSError, ValueError, json.JSONDecodeError) as exc: errors = [str(exc)]
    if errors:
        print("FAIL")
        for error in errors: print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
