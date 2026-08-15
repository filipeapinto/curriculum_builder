from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import yaml

from runtime.langgraph_factory import transport as tp
from runtime.langgraph_factory.nodes import inputs


class Context:
    @staticmethod
    def clock() -> str:
        return "2026-08-15T00:00:00Z"


def compile_contract(root: Path, entry_source: str, dependency_source: str | None = None):
    engine = root / "engine"
    curriculum = engine / "curricula" / "synthetic"
    fixtures = curriculum / "fixtures"
    fixtures.mkdir(parents=True)
    output = engine / "outputs" / "run27" / "live_unit"
    output.mkdir(parents=True)

    schema = curriculum / "domain.schema.v1.json"
    manifest_schema = curriculum / "manifest.domain.schema.v1.json"
    calibration = curriculum / "calibration.v1.yaml"
    entry = curriculum / "verify.py"
    dependency = curriculum / "helper.py"
    reject = fixtures / "reject.json"
    accept = fixtures / "accept.json"
    schema.write_text('{"type":"object"}\n', encoding="utf-8")
    manifest_schema.write_text(
        '{"$defs":{"config":{"type":"object"},"core_activity":{}}}\n',
        encoding="utf-8",
    )
    calibration.write_text("profile: test\n", encoding="utf-8")
    entry.write_text(entry_source, encoding="utf-8")
    reject.write_text('{"kind":"reject"}\n', encoding="utf-8")
    accept.write_text('{"kind":"accept"}\n', encoding="utf-8")
    dependencies: list[str] = []
    if dependency_source is not None:
        dependency.write_text(dependency_source, encoding="utf-8")
        dependencies.append(dependency.relative_to(engine).as_posix())

    def rel(path: Path) -> str:
        return path.relative_to(engine).as_posix()

    manifest = curriculum / "synthetic_curriculum.v1.yaml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "domain": {
                    "schema": rel(schema),
                    "manifest_schema": rel(manifest_schema),
                    "calibration": rel(calibration),
                    "config": {},
                    "verifier": {
                        "entry_point": rel(entry),
                        "invocation": f"python3 {rel(entry)} --domain <domain>",
                        "dependencies": dependencies,
                        "must_reject": [
                            {"fixture": rel(reject), "expected_code": "synthetic-reject"}
                        ],
                        "must_accept": [rel(accept)],
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
    return engine, output, compiled, transport


FIXTURE_LOGIC = """\
p = argparse.ArgumentParser()
p.add_argument("--domain", type=Path, required=True)
a = p.parse_args()
body = json.loads(a.domain.read_text())
if body.get("kind") == "reject":
    print("synthetic-reject: expected")
    raise SystemExit(1)
if body.get("kind") == "accept":
    raise SystemExit(0)
"""


def dependency_surface_probe(root: Path) -> dict[str, object]:
    entry_source = (
        "import argparse, json, sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
        "import helper\n"
        + FIXTURE_LOGIC
        + "print('candidate-after-dependency-import')\n"
    )
    dependency_source = "import subprocess\nprint('process-module-dependency-loaded')\n"
    engine, output, compiled, transport = compile_contract(
        root, entry_source, dependency_source
    )
    if "effective_run" not in compiled:
        return {"d02_result": "REJECTED", "failure": compiled.get("pending_failure")}
    contract = compiled["effective_run"]["domain_contract"]
    receipt = transport.verify_domain(body={"probe": "dependency"}, contract=contract)
    work_root = tp.domain_verifier_work_root(engine_root=engine, output_root=output)
    return {
        "d02_result": compiled["pending_guard"]["value"],
        "dependency_sha256": contract["verifier"]["dependencies"][0]["sha256"],
        "d08_result": receipt["result"],
        "candidate_output": receipt["candidate"]["output_excerpt"].strip(),
        "external_work_root": engine.resolve() not in work_root.parents
        and output.resolve() not in work_root.parents,
    }


def chdir_oracle_probe(root: Path) -> dict[str, object]:
    secret_parts = [*root.resolve().parts[1:], "engine", "undeclared-dir"]
    entry_source = (
        "import argparse, json, os\n"
        "from pathlib import Path\n"
        + FIXTURE_LOGIC
        + f"target = os.sep + os.path.join(*{secret_parts!r})\n"
        + "try:\n"
        + "    os.chdir(target)\n"
        + "except PermissionError:\n"
        + "    print('undeclared-existing: denied')\n"
        + "    raise SystemExit(0)\n"
        + "except FileNotFoundError:\n"
        + "    print('undeclared-absent: visible')\n"
        + "    raise SystemExit(1)\n"
        + "print('undeclared-existing: visible')\n"
        + "raise SystemExit(0)\n"
    )
    engine, _, compiled, transport = compile_contract(root, entry_source)
    undeclared = engine / "undeclared-dir"
    undeclared.mkdir()
    if "effective_run" not in compiled:
        return {"d02_result": "REJECTED", "failure": compiled.get("pending_failure")}
    contract = compiled["effective_run"]["domain_contract"]
    body = {"probe": "same-candidate"}
    first = transport.verify_domain(body=body, contract=contract)
    undeclared.rename(engine / "renamed-undeclared-dir")
    second = transport.verify_domain(body=body, contract=contract)
    return {
        "d02_result": compiled["pending_guard"]["value"],
        "same_candidate_sha256": first["candidate_sha256"] == second["candidate_sha256"],
        "same_contract_sha256": first["contract_sha256"] == second["contract_sha256"],
        "first_result": first["result"],
        "first_returncode": first["candidate"]["returncode"],
        "first_output": first["candidate"]["output_excerpt"].strip(),
        "second_result_after_rename": second["result"],
        "second_returncode": second["candidate"]["returncode"],
        "second_output": second["candidate"]["output_excerpt"].strip(),
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="rc21-dependency-surface-") as raw:
        dependency = dependency_surface_probe(Path(raw).resolve())
    with tempfile.TemporaryDirectory(prefix="rc21-chdir-oracle-") as raw:
        chdir = chdir_oracle_probe(Path(raw).resolve())
    print(json.dumps({"dependency_surface": dependency, "chdir_oracle": chdir}, indent=2))


def test_d02_dependency_surface(tmp_path: Path) -> None:
    entry_source = (
        "import argparse, json, sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
        "import helper\n"
        + FIXTURE_LOGIC
        + "print('candidate-after-dependency-import')\n"
    )
    _engine, _output, compiled, transport = compile_contract(
        tmp_path,
        entry_source,
        "import subprocess\nprint(eval(\"'dependency-dynamic-code-loaded'\"))\n",
    )
    assert compiled["pending_guard"]["value"] == "effective_run_compiled"
    contract = compiled["effective_run"]["domain_contract"]
    receipt = transport.verify_domain(body={"probe": "dependency"}, contract=contract)
    print(json.dumps({
        "d02_result": compiled["pending_guard"]["value"],
        "d08_result": receipt["result"],
        "candidate_output": receipt["candidate"]["output_excerpt"],
    }, indent=2))


def test_chdir_existence_oracle(tmp_path: Path) -> None:
    result = chdir_oracle_probe(tmp_path)
    print(json.dumps(result, indent=2))
    assert result["first_result"] == result["second_result_after_rename"]


if __name__ == "__main__":
    main()
