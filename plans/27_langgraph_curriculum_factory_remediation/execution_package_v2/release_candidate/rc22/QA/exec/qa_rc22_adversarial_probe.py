from __future__ import annotations

import json
import importlib.util
from pathlib import Path

import pytest
import yaml

from runtime.langgraph_factory import transport as tp
from runtime.langgraph_factory.nodes import inputs


REPO = Path(__file__).resolve().parents[7]


class Context:
    @staticmethod
    def clock() -> str:
        return "2026-08-15T00:00:00Z"


def _compile_synthetic(
    root: Path,
    *,
    entry_source: str,
    dependency_source: str | None = None,
) -> tuple[Path, Path, dict, tp.CliTransport]:
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

    def relative(path: Path) -> str:
        return path.relative_to(engine).as_posix()

    manifest = curriculum / "synthetic_curriculum.v1.yaml"
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
                        "dependencies": dependencies,
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
    return engine, output, compiled, transport


def _fixture_verifier_prefix() -> str:
    return (
        "import argparse, json\n"
        "from pathlib import Path\n"
        "p=argparse.ArgumentParser(); p.add_argument('--domain', type=Path, required=True)\n"
        "a=p.parse_args(); body=json.loads(a.domain.read_text())\n"
        "if body.get('kind') == 'reject': print('synthetic-reject: expected'); raise SystemExit(1)\n"
        "if body.get('kind') == 'accept': raise SystemExit(0)\n"
    )


def test_real_active_arduino_d01_to_d02() -> None:
    engine = REPO
    curriculum = engine / "curricula" / "arduino_kit"
    output = Path("/private/tmp/rc22-active-arduino-output")
    state = inputs.D01_VALIDATE_AND_FREEZE_INPUTS(
        {
            "invocation": {
                "contract_version": "qa",
                "engine_root": str(engine),
                "curriculum_root": str(curriculum),
                "output_root": str(output),
                "mode": "one",
                "requested_unit_id": "L01",
                "authorization": {"purpose": "qa"},
            }
        },
        Context(),
    )
    update = inputs.D02_COMPILE_EFFECTIVE_RUN(state, Context())
    print(
        json.dumps(
            {
                "d01": state["pending_guard"]["value"],
                "frozen_input_count": len(state["frozen_inputs"]),
                "d02": update.get("pending_guard", {}).get("value"),
                "failure": update.get("pending_failure"),
            },
            indent=2,
        )
    )
    assert update["pending_guard"]["value"] == "effective_run_compiled"


@pytest.mark.parametrize(
    "source",
    [
        "import builtins\nvalue = getattr(builtins, 'eval')('40 + 2')\n",
        "import importlib\nctypes = importlib.import_module('ctypes')\n",
        "import os\nchild = os.fork()\n",
    ],
    ids=["indirect-eval", "dynamic-native-import", "fork"],
)
def test_d02_rejects_indirect_dynamic_native_and_process_surfaces(
    tmp_path: Path, source: str
) -> None:
    entry = source + _fixture_verifier_prefix() + "raise SystemExit(0)\n"
    _engine, _output, compiled, _transport = _compile_synthetic(
        tmp_path, entry_source=entry
    )
    print(json.dumps(compiled, indent=2, default=str))
    assert "pending_failure" in compiled
    assert compiled["pending_failure"]["cause"] == "schema_contract"


def test_d02_rejects_indirect_dynamic_code_in_dependency(tmp_path: Path) -> None:
    _engine, _output, compiled, _transport = _compile_synthetic(
        tmp_path,
        entry_source=(
            "import sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
            "import helper\n"
            + _fixture_verifier_prefix()
            + "raise SystemExit(0)\n"
        ),
        dependency_source=(
            "import builtins\n"
            "value = getattr(builtins, 'eval')('40 + 2')\n"
        ),
    )
    print(json.dumps(compiled, indent=2, default=str))
    assert "pending_failure" in compiled
    assert compiled["pending_failure"]["cause"] == "schema_contract"


def test_indirect_dynamic_code_dependency_crosses_d02_and_executes(
    tmp_path: Path,
) -> None:
    _engine, _output, compiled, transport = _compile_synthetic(
        tmp_path,
        entry_source=(
            "import sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
            "import helper\n"
            + _fixture_verifier_prefix()
            + "raise SystemExit(0)\n"
        ),
        dependency_source=(
            "import builtins\n"
            "print(getattr(builtins, 'eval')(\"'indirect-dynamic-code-loaded'\"))\n"
        ),
    )
    assert compiled["pending_guard"]["value"] == "effective_run_compiled"
    receipt = transport.verify_domain(
        body={"probe": "indirect-dynamic-code"},
        contract=compiled["effective_run"]["domain_contract"],
    )
    evidence = {
        "d02": compiled["pending_guard"]["value"],
        "d08": receipt["result"],
        "candidate_output": receipt["candidate"]["output_excerpt"].strip(),
    }
    print(json.dumps(evidence, indent=2))
    assert receipt["result"] == "PASS"
    assert "indirect-dynamic-code-loaded" in receipt["candidate"]["output_excerpt"]


def test_rc19_required_staging_and_race_probes() -> None:
    path = (
        REPO
        / "plans/27_langgraph_curriculum_factory_remediation"
        / "execution_package_v2/release_candidate/rc19/QA/exec"
        / "rc19_required_verifier_probes.py"
    )
    spec = importlib.util.spec_from_file_location("rc19_required_verifier_probes", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


@pytest.mark.parametrize("operation", ["utime", "mkfifo"])
def test_undeclared_engine_path_operation_is_invariant(
    tmp_path: Path, operation: str
) -> None:
    engine_target = tmp_path / "engine" / "undeclared"
    parts = list(engine_target.resolve().parts[1:])
    operation_source = {
        "utime": "os.utime(target, None)",
        "mkfifo": "os.mkfifo(target)",
    }[operation]
    entry = (
        "import os\n"
        + _fixture_verifier_prefix()
        + f"target = os.sep + os.path.join(*{parts!r})\n"
        + "try:\n"
        + f"    {operation_source}\n"
        + "except PermissionError:\n"
        + "    print('permission'); raise SystemExit(0)\n"
        + "except FileNotFoundError:\n"
        + "    print('missing'); raise SystemExit(1)\n"
        + "except FileExistsError:\n"
        + "    print('exists'); raise SystemExit(2)\n"
        + "print('completed'); raise SystemExit(3)\n"
    )
    engine, _output, compiled, transport = _compile_synthetic(
        tmp_path, entry_source=entry
    )
    assert "effective_run" in compiled
    contract = compiled["effective_run"]["domain_contract"]
    engine_target.mkdir()
    first = transport.verify_domain(body={"probe": "same"}, contract=contract)
    engine_target.rmdir()
    second = transport.verify_domain(body={"probe": "same"}, contract=contract)
    evidence = {
        "operation": operation,
        "same_candidate": first["candidate_sha256"] == second["candidate_sha256"],
        "same_contract": first["contract_sha256"] == second["contract_sha256"],
        "existing": first["candidate"],
        "absent": second["candidate"],
    }
    print(json.dumps(evidence, indent=2))
    assert first["result"] == second["result"]
