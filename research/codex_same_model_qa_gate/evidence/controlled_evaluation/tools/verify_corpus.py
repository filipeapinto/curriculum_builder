#!/usr/bin/env python3
"""Read-only integrity verification for the frozen blinded corpus."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "fixtures/gate_visible/corpus_cases.v1.json"
PRIVATE = ROOT / "fixtures/private_labels/gold_labels.v1.json"

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def main():
    public = json.loads(PUBLIC.read_text())
    private = json.loads(PRIVATE.read_text())
    cases, labels = public["cases"], private["labels"]
    assert len(cases) == len(labels) == 60
    assert len({c["case_id"] for c in cases}) == 60
    assert len({l["case_id"] for l in labels}) == 60
    public_ids, private_ids = {c["case_id"] for c in cases}, {l["case_id"] for l in labels}
    assert public_ids == private_ids
    for klass in ("code", "document_or_plan"):
        ids = {c["case_id"] for c in cases if c["artifact_class"] == klass}
        selected = [l for l in labels if l["case_id"] in ids]
        assert len(selected) == 30
        assert Counter(l["gold_status"] for l in selected) == {"fault_seeded": 18, "clean": 12}
        faults = [l for l in selected if l["gold_status"] == "fault_seeded"]
        categories = Counter(l["fault_category"] for l in faults)
        assert len(categories) >= 5
        assert max(categories.values()) <= 6
    # A gate-visible bundle must not contain private verdict or taxonomy keys.
    forbidden = {"gold_status", "fault_category", "expected_case_verdict", "oracle_id", "risk_tier"}
    assert not any(forbidden.intersection(c) for c in cases)
    print(json.dumps({
        "status": "passed", "case_count": len(cases),
        "public_bundle_sha256": digest(public), "private_label_sha256": digest(private),
        "case_digests": {c["case_id"]: digest(c) for c in cases}
    }, sort_keys=True))

if __name__ == "__main__":
    main()
