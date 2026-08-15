from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import yaml

from runtime.langgraph_factory import transport as tp
from runtime.langgraph_factory.nodes import inputs


REPO = Path("/Users/filipepinto/Projects/curriculum_builder")


class Context:
    @staticmethod
    def clock() -> str:
        return "2026-08-15T00:00:00Z"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_case(root: Path, output_name: str) -> tuple[Path, Path, dict, tp.CliTransport]:
    engine = root / "engine"
    curriculum = engine / "curricula" / "synthetic"
    fixtures = curriculum / "fixtures"
    fixtures.mkdir(parents=True, exist_ok=True)
    output = engine / "outputs" / output_name
    output.mkdir(parents=True, exist_ok=True)

    schema = curriculum / "domain.schema.v1.json"
    manifest_schema = curriculum / "manifest.domain.schema.v1.json"
    calibration = curriculum / "calibration.v1.yaml"
    entry = curriculum / "verify.py"
    reject = fixtures / "reject.json"
    accept = fixtures / "accept.json"
    manifest = curriculum / "synthetic_curriculum.v1.yaml"

    schema.write_text('{"type":"object"}\n', encoding="utf-8")
    manifest_schema.write_text(
        '{"$defs":{"config":{"type":"object"},"core_activity":{}}}\n',
        encoding="utf-8",
    )
    calibration.write_text("profile: qa\n", encoding="utf-8")
    reject.write_text('{"kind":"reject"}\n', encoding="utf-8")
    accept.write_text('{"kind":"accept"}\n', encoding="utf-8")
    entry.write_text(
        "import argparse, json\n"
        "from pathlib import Path\n"
        "p=argparse.ArgumentParser(); p.add_argument('--domain', type=Path, required=True)\n"
        "body=json.loads(p.parse_args().domain.read_text())\n"
        "if body.get('kind') == 'reject': print('synthetic-reject: expected'); raise SystemExit(1)\n"
        "if body.get('kind') == 'accept': raise SystemExit(0)\n"
        "print('original-entry: reject candidate'); raise SystemExit(1)\n",
        encoding="utf-8",
    )

    def relative(path: Path) -> str:
        return path.relative_to(engine).as_posix()

    manifest.write_text(
        yaml.safe_dump(
            {
                "domain": {
                    "schema": relative(schema),
                    "manifest_schema": relative(manifest_schema),
                    "calibration": relative(calibration),
                    "config": {},
                    "verifier": {
                        "entry_point": relative(entry),
                        "invocation": f"python3 {relative(entry)} --domain <domain>",
                        "dependencies": [],
                        "must_reject": [
                            {
                                "fixture": relative(reject),
                                "expected_code": "synthetic-reject",
                            }
                        ],
                        "must_accept": [relative(accept)],
                        "proven": {"result": "all_fixtures_behaved"},
                    },
                },
                "labs": [
                    {
                        "id": "U001",
                        "title": "Synthetic",
                        "sequence": {"prerequisites": [], "prepares_for": []},
                        "required_explanation": ["fact"],
                        "core_activity": {},
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    frozen = inputs.D01_VALIDATE_AND_FREEZE_INPUTS(
        {
            "invocation": {
                "contract_version": "qa",
                "engine_root": str(engine),
                "curriculum_root": str(curriculum),
                "output_root": str(output),
                "mode": "one",
                "requested_unit_id": "U001",
                "authorization": {"purpose": "qa"},
            }
        },
        Context(),
    )
    compiled = inputs.D02_COMPILE_EFFECTIVE_RUN(frozen, Context())
    transport = object.__new__(tp.CliTransport)
    transport.engine_root = engine.resolve()
    transport.output_root = output.resolve()
    return engine, entry, compiled, transport


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="rc28-qa-") as raw:
        root = Path(raw).resolve()
        engine, entry, compiled, baseline_transport = build_case(root, "baseline")
        assert compiled["pending_guard"]["value"] == "effective_run_compiled"
        contract = compiled["effective_run"]["domain_contract"]
        body = {"probe": "same-candidate"}
        declared_entry_sha = contract["verifier"]["entry_point"]["sha256"]

        original_builder = tp.build_sandboxed_argv
        tp.build_sandboxed_argv = lambda argv, *, profile_path: list(argv)
        try:
            baseline = baseline_transport.verify_domain(body=body, contract=contract)

            raced_output = engine / "outputs" / "raced"
            raced_output.mkdir(parents=True)
            raced_transport = object.__new__(tp.CliTransport)
            raced_transport.engine_root = engine.resolve()
            raced_transport.output_root = raced_output.resolve()

            original_run = tp.subprocess.run
            mutated = False
            executed_entry_sha = None

            def race_run(argv, *args, **kwargs):
                nonlocal mutated, executed_entry_sha
                if not mutated:
                    staged_entry = Path(argv[5])
                    staged_entry.write_text(
                        "import argparse, json\n"
                        "from pathlib import Path\n"
                        "p=argparse.ArgumentParser(); p.add_argument('--domain', type=Path, required=True)\n"
                        "body=json.loads(p.parse_args().domain.read_text())\n"
                        "if body.get('kind') == 'reject': print('synthetic-reject: expected'); raise SystemExit(1)\n"
                        "if body.get('kind') == 'accept': raise SystemExit(0)\n"
                        "print('raced-entry: accept candidate'); raise SystemExit(0)\n",
                        encoding="utf-8",
                    )
                    executed_entry_sha = sha256(staged_entry)
                    mutated = True
                return original_run(argv, *args, **kwargs)

            tp.subprocess.run = race_run
            try:
                raced = raced_transport.verify_domain(body=body, contract=contract)
            finally:
                tp.subprocess.run = original_run
        finally:
            tp.build_sandboxed_argv = original_builder

        print(
            json.dumps(
                {
                    "d02": compiled["pending_guard"]["value"],
                    "candidate_same": baseline["candidate_sha256"] == raced["candidate_sha256"],
                    "contract_same": baseline["contract_sha256"] == raced["contract_sha256"],
                    "declared_entry_sha": declared_entry_sha,
                    "raced_executed_entry_sha": executed_entry_sha,
                    "receipt_entry_sha": raced["entry_point_sha256"],
                    "baseline_result": baseline["result"],
                    "baseline_output": baseline["candidate"]["output_excerpt"].strip(),
                    "raced_result": raced["result"],
                    "raced_output": raced["candidate"]["output_excerpt"].strip(),
                    "raced_runtime_entry_record": [
                        record
                        for record in raced["candidate"]["runtime_modules"]
                        if record["path"].endswith("/frozen/curricula/synthetic/verify.py")
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
