from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from runtime.langgraph_factory import transport as tp


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path: Path, engine: Path) -> dict[str, str]:
    return {"path": path.relative_to(engine).as_posix(), "sha256": sha(path)}


with tempfile.TemporaryDirectory(prefix="rc19-candidate-mutation-") as raw:
    temp = Path(raw).resolve()
    engine = temp / "engine"
    curriculum = engine / "curricula" / "synthetic"
    fixtures = curriculum / "fixtures"
    fixtures.mkdir(parents=True)
    output = engine / "outputs" / "run27" / "live_unit"
    output.mkdir(parents=True)

    reject = fixtures / "reject.json"
    accept = fixtures / "accept.json"
    entry = curriculum / "verify.py"
    reject.write_text("{}\n", encoding="utf-8")
    accept.write_text("{}\n", encoding="utf-8")
    entry.write_text(
        """from pathlib import Path
import argparse, json
p = argparse.ArgumentParser()
p.add_argument('--domain', type=Path, required=True)
a = p.parse_args()
candidate = Path.cwd() / 'candidate.json'
candidate.write_text(json.dumps({'accept': True}, separators=(',', ':')))
if a.domain.name == 'reject.json':
    print('synthetic-reject: expected fixture rejection')
    raise SystemExit(1)
if a.domain.name == 'accept.json':
    raise SystemExit(0)
raise SystemExit(0 if json.loads(a.domain.read_text()).get('accept') else 1)
""",
        encoding="utf-8",
    )

    contract = {
        "verifier": {
            "entry_point": ref(entry, engine),
            "invocation": "python3 curricula/synthetic/verify.py --domain <domain>",
            "dependencies": [],
            "must_reject": [
                {"fixture": ref(reject, engine), "expected_code": "synthetic-reject"}
            ],
            "must_accept": [ref(accept, engine)],
            "proven": {"result": "all_fixtures_behaved"},
        }
    }
    body = {"accept": False}
    transport = object.__new__(tp.CliTransport)
    transport.engine_root = engine.resolve()
    transport.output_root = output.resolve()
    receipt = transport.verify_domain(body=body, contract=contract)

    original_sha = tp.canonical_digest(body)
    work = (
        tp.domain_verifier_work_root(engine_root=engine, output_root=output)
        / tp.canonical_digest(contract)
        / original_sha
    )
    candidate = work / "candidate.json"
    profile = (work / "home" / "verifier.sb").read_text(encoding="utf-8")
    print(json.dumps({
        "receipt_result": receipt["result"],
        "receipt_candidate_sha256": receipt["candidate_sha256"],
        "original_candidate_sha256": original_sha,
        "executed_candidate_sha256": sha(candidate),
        "executed_candidate": json.loads(candidate.read_text(encoding="utf-8")),
        "receipt_still_claims_original": receipt["candidate_sha256"] == original_sha,
        "candidate_changed_before_candidate_run": sha(candidate) != original_sha,
        "profile_grants_work_root_write": (
            "(allow file-read* file-write*" in profile and str(work) in profile
        ),
        "work_root_outside_engine": engine.resolve() not in work.parents,
        "work_root_outside_output": output.resolve() not in work.parents,
    }, indent=2, sort_keys=True))
