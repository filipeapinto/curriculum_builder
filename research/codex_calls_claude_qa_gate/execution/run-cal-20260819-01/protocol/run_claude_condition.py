#!/usr/bin/env python3
"""Run two repetitions of the frozen Claude condition at concurrency two."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORPUS = json.loads((ROOT / "synthetic-corpus.v1.json").read_text())
CONTROLLER = ROOT / "benchmark_controller.py"
OUT = ROOT.parent / "benchmark" / "claude-sonnet-5.receipts.jsonl"
OUT.parent.mkdir(parents=True, exist_ok=True)

SIM = {"timeout": "timeout", "unavailable_reviewer": "unavailable", "digest_mismatch": "digest-mismatch"}

def run(item):
    case, rep = item
    run_id = f"RUN-CLAUDE-{case['case_id']}-R{rep}"
    cmd = ["python3", str(CONTROLLER), "--case", case["case_id"], "--run-id", run_id]
    if case["failure_class"] in SIM:
        cmd += ["--simulate", SIM[case["failure_class"]]]
    else:
        cmd += ["--live"]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    line = proc.stdout.strip() or json.dumps({"run_id": run_id, "state": "QA_ERROR", "error": "EMPTY_CONTROLLER_OUTPUT"})
    try:
        record = json.loads(line)
    except json.JSONDecodeError:
        record = {"run_id": run_id, "state": "QA_ERROR", "error": "MALFORMED_CONTROLLER_OUTPUT", "raw": line[-1000:]}
    record["controller_exit"] = proc.returncode
    record["condition"] = "claude-sonnet-5"
    record["repetition"] = rep
    return run_id, record

items = [(case, rep) for case in CORPUS["cases"] for rep in (1, 2)]
records = []
with ThreadPoolExecutor(max_workers=2) as pool:
    futures = {pool.submit(run, item): item for item in items}
    for future in as_completed(futures):
        run_id, record = future.result()
        records.append((run_id, record))
        print(run_id, record.get("state") or record.get("verdict", {}).get("state"), flush=True)

with OUT.open("w", encoding="utf-8") as fh:
    for _, record in sorted(records):
        fh.write(json.dumps(record, sort_keys=True) + "\n")
print(OUT)
