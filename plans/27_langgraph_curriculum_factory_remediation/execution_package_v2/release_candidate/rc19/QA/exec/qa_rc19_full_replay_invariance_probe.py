from __future__ import annotations

import json
import tempfile
from pathlib import Path

import yaml

from runtime.langgraph_factory import transport as tp
from runtime.langgraph_factory.nodes import inputs


class Context:
    @staticmethod
    def clock() -> str:
        return "2026-08-15T00:00:00Z"


with tempfile.TemporaryDirectory(prefix="rc19-full-replay-") as raw:
    temp = Path(raw).resolve()
    engine = temp / "engine"
    curriculum = engine / "curricula" / "synthetic"
    fixtures = curriculum / "fixtures"
    fixtures.mkdir(parents=True)
    output = engine / "outputs" / "run27" / "live_unit"
    output.mkdir(parents=True)

    undeclared = engine / "undeclared.txt"
    undeclared.write_text("hidden\n", encoding="utf-8")
    schema = curriculum / "domain.schema.v1.json"
    manifest_schema = curriculum / "manifest.domain.schema.v1.json"
    calibration = curriculum / "calibration.v1.yaml"
    entry = curriculum / "verify.py"
    reject = fixtures / "reject.json"
    accept = fixtures / "accept.json"
    schema.write_text('{"type":"object"}\n', encoding="utf-8")
    manifest_schema.write_text(
        '{"$defs":{"config":{"type":"object"},"core_activity":{}}}\n',
        encoding="utf-8",
    )
    calibration.write_text("profile: test\n", encoding="utf-8")
    reject.write_text('{"kind":"reject"}\n', encoding="utf-8")
    accept.write_text('{"kind":"accept"}\n', encoding="utf-8")
    entry.write_text(
        f'''from pathlib import Path
import argparse, json
p = argparse.ArgumentParser()
p.add_argument("--domain", type=Path, required=True)
a = p.parse_args()
body = json.loads(a.domain.read_text())
if body.get("kind") == "reject":
    print("synthetic-reject: expected fixture rejection")
    raise SystemExit(1)
if body.get("kind") == "accept":
    raise SystemExit(0)
try:
    Path({str(undeclared)!r}).stat()
except PermissionError:
    print("undeclared-existing: denied")
    raise SystemExit(0)
except FileNotFoundError:
    print("undeclared-absent: visible")
    raise SystemExit(1)
raise SystemExit(2)
''',
        encoding="utf-8",
    )

    def rel(path: Path) -> str:
        return path.relative_to(engine).as_posix()

    manifest = curriculum / "synthetic_curriculum.v1.yaml"
    manifest.write_text(
        yaml.safe_dump({
            "domain": {
                "schema": rel(schema),
                "manifest_schema": rel(manifest_schema),
                "calibration": rel(calibration),
                "config": {},
                "verifier": {
                    "entry_point": rel(entry),
                    "invocation": f"python3 {rel(entry)} --domain <domain>",
                    "dependencies": [],
                    "must_reject": [{
                        "fixture": rel(reject),
                        "expected_code": "synthetic-reject",
                    }],
                    "must_accept": [rel(accept)],
                    "proven": {"result": "all_fixtures_behaved"},
                },
            },
            "labs": [{
                "id": "U001",
                "title": "Synthetic",
                "sequence": {"prerequisites": [], "prepares_for": []},
                "required_explanation": ["fact"],
                "core_activity": {},
            }],
        }, sort_keys=False),
        encoding="utf-8",
    )

    frozen = inputs.D01_VALIDATE_AND_FREEZE_INPUTS({"invocation": {
        "contract_version": "qa",
        "engine_root": str(engine),
        "curriculum_root": str(curriculum),
        "output_root": str(output),
        "mode": "one",
        "requested_unit_id": "U001",
        "authorization": {"purpose": "qa"},
    }}, Context())
    compiled = inputs.D02_COMPILE_EFFECTIVE_RUN(frozen, Context())
    contract = compiled["effective_run"]["domain_contract"]

    transport = object.__new__(tp.CliTransport)
    transport.engine_root = engine.resolve()
    transport.output_root = output.resolve()
    candidate = {"probe": "same-candidate"}
    first = transport.verify_domain(body=candidate, contract=contract)
    undeclared.rename(engine / "renamed-undeclared.txt")
    second = transport.verify_domain(body=candidate, contract=contract)

    print(json.dumps({
        "d01_guard": frozen["pending_guard"]["value"],
        "d02_guard": compiled["pending_guard"]["value"],
        "compiled_dependencies": contract["verifier"]["dependencies"],
        "same_candidate_sha256": first["candidate_sha256"] == second["candidate_sha256"],
        "same_contract_sha256": first["contract_sha256"] == second["contract_sha256"],
        "first_result": first["result"],
        "first_output": first["candidate"]["output_excerpt"].strip(),
        "second_result_after_rename": second["result"],
        "second_output": second["candidate"]["output_excerpt"].strip(),
    }, indent=2, sort_keys=True))
