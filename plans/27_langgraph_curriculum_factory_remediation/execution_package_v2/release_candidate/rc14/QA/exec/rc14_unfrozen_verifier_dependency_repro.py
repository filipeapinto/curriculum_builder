from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile

import yaml

from runtime.langgraph_factory.artifacts import ArtifactStore
from runtime.langgraph_factory.nodes import inputs
from runtime.langgraph_factory.transport import CliTransport


REPO_ROOT = Path("/Users/filipepinto/Projects/curriculum_builder")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


with tempfile.TemporaryDirectory(prefix="rc14-unfrozen-verifier-") as raw:
    engine = (Path(raw) / "engine").resolve()
    curriculum = engine / "curricula" / "arduino_kit"
    curriculum.parent.mkdir(parents=True)
    shutil.copytree(REPO_ROOT / "curricula" / "arduino_kit", curriculum)

    manifest_path = curriculum / "arduino_kit_curriculum.v5.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    unit_records = inputs.manifest_unit_records(manifest)
    frozen = {
        str(path.resolve()): digest(path)
        for path in curriculum.rglob("*")
        if path.is_file()
    }
    contract = inputs._compile_domain_contract(
        manifest,
        engine_root=engine,
        curriculum_root=curriculum,
        frozen=frozen,
        unit_records=unit_records,
    )

    library = curriculum / "circuit_library.v1.yaml"
    library_before = digest(library)
    contract_text = json.dumps(contract, sort_keys=True)
    print("library path appears in contract:", "circuit_library.v1.yaml" in contract_text)
    print("library digest appears in contract:", library_before in contract_text)

    output = Path(raw) / "output"
    transport = object.__new__(CliTransport)
    transport.engine_root = engine
    transport.output_root = output
    transport.render_root = output / "render"
    transport._artifacts = ArtifactStore(output)

    candidate = json.loads(
        (curriculum / "fixtures" / "domain_no_current_limit.reject.json").read_text(
            encoding="utf-8"
        )
    )
    candidate["electrical"]["calculations"][0]["purpose"] = "current_limiting"
    before = transport.verify_domain(body=candidate, contract=contract)
    print("candidate sha256 before drift:", before["candidate_sha256"])
    print("candidate result before drift:", before["fixtures_result"], before["result"])
    print("candidate codes before drift:", before["candidate"]["codes"])

    library.write_text("circuits: []\n", encoding="utf-8")
    print("library digest changed:", digest(library) != library_before)
    after = transport.verify_domain(body=candidate, contract=contract)
    print("candidate sha256 unchanged:", after["candidate_sha256"] == before["candidate_sha256"])
    print("candidate codes after drift:", after["candidate"]["codes"])
    print("receipt returned after drift:", after["fixtures_result"], after["result"])
