from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import yaml

from runtime.langgraph_factory.nodes import inputs


REPO = Path("/Users/filipepinto/Projects/curriculum_builder")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_contract(
    manifest: dict, engine: Path, curriculum: Path, frozen: dict[str, str]
) -> tuple[str, str]:
    try:
        inputs._compile_domain_contract(
            manifest,
            engine_root=engine,
            curriculum_root=curriculum,
            frozen=frozen,
            unit_records=inputs.manifest_unit_records(manifest),
        )
    except Exception as error:  # the probe records the fail-closed class and message
        return type(error).__name__, str(error)
    return "COMPILED", ""


with tempfile.TemporaryDirectory(prefix="rc19-d02-boundary-") as raw:
    engine = Path(raw).resolve() / "engine"
    curriculum = engine / "curricula" / "arduino_kit"
    curriculum.parent.mkdir(parents=True)
    shutil.copytree(REPO / "curricula" / "arduino_kit", curriculum)
    manifest_path = curriculum / "arduino_kit_curriculum.v5.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    frozen = {
        str(path.resolve()): sha(path)
        for path in curriculum.rglob("*")
        if path.is_file()
    }

    results: dict[str, tuple[str, str]] = {}
    results["baseline"] = compile_contract(manifest, engine, curriculum, frozen)

    missing = copy.deepcopy(manifest)
    del missing["domain"]["verifier"]["dependencies"]
    results["missing_dependencies"] = compile_contract(missing, engine, curriculum, frozen)

    escape = copy.deepcopy(manifest)
    escape["domain"]["verifier"]["dependencies"] = ["outside-curriculum.json"]
    results["dependency_escape"] = compile_contract(escape, engine, curriculum, frozen)

    duplicate = copy.deepcopy(manifest)
    dependency = duplicate["domain"]["verifier"]["dependencies"][0]
    duplicate["domain"]["verifier"]["dependencies"] = [dependency, dependency]
    results["duplicate_dependencies"] = compile_contract(
        duplicate, engine, curriculum, frozen
    )

    oversize = copy.deepcopy(manifest)
    oversize["domain"]["verifier"]["dependencies"] = [
        f"curricula/arduino_kit/nonexistent-{index}.json" for index in range(65)
    ]
    results["oversize_dependencies"] = compile_contract(
        oversize, engine, curriculum, frozen
    )

    drift_path = curriculum / "circuit_library.v1.yaml"
    drift_path.write_text("circuits: []\n", encoding="utf-8")
    results["declared_drift"] = compile_contract(manifest, engine, curriculum, frozen)

    print(json.dumps({
        name: {"outcome": outcome, "detail": detail[:300]}
        for name, (outcome, detail) in results.items()
    }, indent=2, sort_keys=True))
