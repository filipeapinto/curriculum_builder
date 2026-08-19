#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor, as_completed
import json, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
CORPUS=json.loads((ROOT/"synthetic-corpus.v1.json").read_text())
CONTROLLER=ROOT/"codex_benchmark_controller.py"
SIM={"timeout":"timeout","unavailable_reviewer":"unavailable","digest_mismatch":"digest-mismatch"}

def one(model,case,rep):
    rid=f"RUN-{model}-{case['case_id']}-R{rep}"
    cmd=["python3",str(CONTROLLER),"--case",case["case_id"],"--run-id",rid,"--model",model]
    if case["failure_class"] in SIM: cmd += ["--simulate",SIM[case["failure_class"]]]
    proc=subprocess.run(cmd,text=True,capture_output=True)
    try: rec=json.loads(proc.stdout.strip())
    except Exception: rec={"run_id":rid,"case_id":case["case_id"],"state":"QA_ERROR","error":"MALFORMED_CONTROLLER_OUTPUT"}
    rec.update(condition=model,repetition=rep,controller_exit=proc.returncode)
    return rid,rec

for model in ("gpt-5.6-sol","gpt-5.6-terra"):
    records=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(one,model,c,r) for c in CORPUS["cases"] for r in (1,2)]
        for f in as_completed(futures):
            rid,rec=f.result(); records.append((rid,rec)); print(rid,rec.get("state") or rec.get("verdict",{}).get("state"),flush=True)
    out=ROOT.parent/"benchmark"/f"{model}.receipts.jsonl"
    with out.open("w") as fh:
        for _,rec in sorted(records): fh.write(json.dumps(rec,sort_keys=True)+"\n")
    print(out)
