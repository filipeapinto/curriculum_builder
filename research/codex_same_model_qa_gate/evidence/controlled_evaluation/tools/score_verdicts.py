#!/usr/bin/env python3
"""Deterministically score committed, label-blind gate verdict records.

Input is JSON Lines supplied on stdin. Each record must contain only an operation
identifier, case_id, variant_id, repeat, and parsed verdict. Gold labels are read
only by this scorer after raw-output commitment.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = {x["case_id"]: x for x in json.loads((ROOT / "fixtures/private_labels/gold_labels.v1.json").read_text())["labels"]}
VALID = {"pass", "fail", "abstain"}

for line in sys.stdin:
    row = json.loads(line)
    prohibited = {"gold_status", "fault_category", "expected_case_verdict", "oracle_id", "risk_tier"}
    if prohibited.intersection(row):
        raise SystemExit("protocol-integrity failure: raw gate record contains private label field")
    label = LABELS.get(row.get("case_id"))
    if not label or row.get("verdict") not in VALID:
        row["scorer_status"] = "invalid"
        row["invalid_reason"] = "unknown_case_or_unparseable_verdict"
    else:
        verdict = row["verdict"]
        row["scorer_status"] = "valid"
        row["gold_status"] = label["gold_status"]
        row["outcome"] = (
            "false_pass" if label["gold_status"] == "fault_seeded" and verdict == "pass" else
            "false_block" if label["gold_status"] == "clean" and verdict == "fail" else
            "correct_or_abstain"
        )
    print(json.dumps(row, sort_keys=True))
