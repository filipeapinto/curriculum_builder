from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from runtime.langgraph_factory import transport as tp


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(path: Path, engine: Path) -> dict[str, str]:
    return {"path": path.relative_to(engine).as_posix(), "sha256": digest(path)}


with tempfile.TemporaryDirectory(prefix="rc18-staged-mutation-") as temp:
    temp_root = Path(temp)
    engine = temp_root / "engine"
    curriculum = engine / "curricula" / "synthetic"
    fixtures = curriculum / "fixtures"
    fixtures.mkdir(parents=True)

    entry = curriculum / "verify_domain.py"
    reject = fixtures / "reject.json"
    accept = fixtures / "accept.json"
    reject.write_text("{}", encoding="utf-8")
    accept.write_text("{}", encoding="utf-8")
    entry.write_text(
        """from pathlib import Path
import argparse, json
p = argparse.ArgumentParser()
p.add_argument('--domain', type=Path, required=True)
a = p.parse_args()
# The emitted verifier profile grants file-write* to the entire work root,
# including candidate.json. Mutate the frozen candidate during fixture execution.
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
            "entry_point": reference(entry, engine),
            "invocation": "python3 curricula/synthetic/verify_domain.py --domain <domain>",
            "dependencies": [],
            "must_reject": [
                {"fixture": reference(reject, engine), "expected_code": "synthetic-reject"}
            ],
            "must_accept": [reference(accept, engine)],
            "proven": {"result": "all_fixtures_behaved"},
        }
    }
    body = {"accept": False}
    output = temp_root / "output"
    transport = object.__new__(tp.CliTransport)
    transport.engine_root = engine.resolve()
    transport.output_root = output.resolve()

    # Nested sandbox-exec is prohibited by the QA runner. This bypasses only the
    # launcher; the generated profile is inspected below and explicitly permits
    # the write used by the verifier.
    original_builder = tp.build_sandboxed_argv
    tp.build_sandboxed_argv = lambda argv, *, profile_path: list(argv)
    try:
        receipt = transport.verify_domain(body=body, contract=contract)
    finally:
        tp.build_sandboxed_argv = original_builder

    contract_sha = tp.canonical_digest(contract)
    original_sha = tp.canonical_digest(body)
    work = (
        tp.domain_verifier_work_root(engine_root=engine, output_root=output)
        / contract_sha
        / original_sha
    )
    candidate = work / "candidate.json"
    profile = (work / "home" / "verifier.sb").read_text(encoding="utf-8")
    observed = {
        "original_body": body,
        "receipt_result": receipt["result"],
        "receipt_candidate_sha256": receipt["candidate_sha256"],
        "post_execution_candidate": json.loads(candidate.read_text(encoding="utf-8")),
        "post_execution_candidate_sha256": digest(candidate),
        "receipt_still_claims_original": receipt["candidate_sha256"] == original_sha,
        "executed_candidate_bytes_changed": digest(candidate) != original_sha,
        "profile_grants_work_root_write": (
            "(allow file-read* file-write*" in profile and str(work) in profile
        ),
        "work_root": str(work),
        "engine_root": str(engine.resolve()),
        "work_is_outside_engine": engine.resolve() not in work.parents,
    }
    print(json.dumps(observed, indent=2, sort_keys=True))
