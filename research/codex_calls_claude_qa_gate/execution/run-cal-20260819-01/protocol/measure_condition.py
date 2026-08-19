#!/usr/bin/env python3
import json, sys
from collections import Counter, defaultdict
from pathlib import Path

root = Path(__file__).resolve().parent
corpus = json.loads((root / "synthetic-corpus.v1.json").read_text())
expected = {c["case_id"]: c["expected_state"] for c in corpus["cases"]}
path = Path(sys.argv[1])
rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
states = []
by_class = defaultdict(lambda: [0, 0])
cost = 0.0
tool_requests = 0
for row in rows:
    state = row.get("verdict", {}).get("state", row.get("state"))
    case_id = row["case_id"]
    exp = expected[case_id]
    states.append(state)
    cls = next(c["failure_class"] for c in corpus["cases"] if c["case_id"] == case_id)
    by_class[cls][1] += 1
    by_class[cls][0] += int(state == exp)
    cost += row.get("total_cost_usd", 0.0)
    usage = row.get("usage", {})
    server = usage.get("server_tool_use", {})
    tool_requests += server.get("web_search_requests", 0) + server.get("web_fetch_requests", 0)

semantic = [(r, expected[r["case_id"]]) for r in rows if expected[r["case_id"]] in {"PASS", "FAIL"}]
tp = sum((r.get("verdict", {}).get("state", r.get("state")) == "FAIL") and e == "FAIL" for r,e in semantic)
fn = sum((r.get("verdict", {}).get("state", r.get("state")) != "FAIL") and e == "FAIL" for r,e in semantic)
fp = sum((r.get("verdict", {}).get("state", r.get("state")) == "FAIL") and e == "PASS" for r,e in semantic)
tn = sum((r.get("verdict", {}).get("state", r.get("state")) == "PASS") and e == "PASS" for r,e in semantic)
result = {
    "receipt_count": len(rows), "state_counts": Counter(states),
    "exact_state_accuracy": sum(v[0] for v in by_class.values()) / len(rows),
    "by_failure_class": {k: {"correct": v[0], "total": v[1]} for k,v in sorted(by_class.items())},
    "blocker_recall": tp / (tp + fn) if tp + fn else None,
    "false_block_rate": fp / (fp + tn) if fp + tn else None,
    "live_cost_usd": cost, "server_web_tool_requests": tool_requests,
}
print(json.dumps(result, indent=2, sort_keys=True, default=dict))
