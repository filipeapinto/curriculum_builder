#!/usr/bin/env python3
"""One-turn independent challenge controller for the frozen package."""
import json, subprocess, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
FILES=[
    "sota-report.html","records/evidence-appraisal.md","records/feasibility-security-matrix.md",
    "benchmark/benchmark-summary.md","protocol/calibration-benchmark-protocol.v1.md",
    "benchmark/claude-sonnet-5.receipts.jsonl","benchmark/gpt-5.6-sol.receipts.jsonl",
    "benchmark/gpt-5.6-terra.receipts.jsonl",
]
parts=["Independently challenge this frozen SOTA package. Do not grant acceptance. Do not use tools; all evidence follows. Test evidence sufficiency, causal language, selection bias, corpus validity, omitted alternatives, feasibility, residual risk, and whether pilot-with-constraints is justified. Return only the required challenge schema."]
for rel in FILES:
    parts += [f"\n--- BEGIN {rel} ---\n",(ROOT/rel).read_text(),f"\n--- END {rel} ---\n"]
prompt="".join(parts)
with tempfile.TemporaryDirectory(prefix="sota-challenge-") as td:
    out=Path(td)/"challenge.json"
    cmd=["codex","--ask-for-approval","never","exec","--ephemeral","--ignore-user-config","--ignore-rules",
         "--sandbox","read-only","--model","gpt-5.5","-c",'model_reasoning_effort="xhigh"',
         "--output-schema",str(ROOT/"protocol/challenge.schema.json"),"--output-last-message",str(out),"-"]
    proc=subprocess.run(cmd,input=prompt,text=True,capture_output=True,timeout=900)
    if proc.returncode or not out.exists():
        raise SystemExit(json.dumps({"state":"QA_ERROR","exit":proc.returncode,"stderr":proc.stderr[-2000:]}))
    result=json.loads(out.read_text())
    print(json.dumps(result,indent=2,sort_keys=True))
