from pathlib import Path
import hashlib
import tempfile

import yaml

from runtime.langgraph_factory.nodes.inputs import D02_COMPILE_EFFECTIVE_RUN


with tempfile.TemporaryDirectory(prefix="rc13-d02-incomplete-") as directory:
    engine = Path(directory)
    curriculum = engine / "curricula" / "synthetic"
    curriculum.mkdir(parents=True)
    manifest = curriculum / "synthetic_curriculum.v1.yaml"
    manifest.write_text(
        yaml.safe_dump(
            {
                # Deliberately incomplete: no config/calibration/verifier.
                "domain": {
                    "schema": "curricula/synthetic/domain.schema.json",
                    "manifest_schema": "curricula/synthetic/manifest.schema.json",
                },
                "labs": [
                    {
                        "id": "U001",
                        "title": "Synthetic",
                        "sequence": {"prerequisites": []},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
    state = {
        "engine_root": str(engine),
        "curriculum_root": str(curriculum),
        "active_manifest_path": str(manifest),
        "mode": "one",
        "requested_unit_id": "U001",
        "frozen_inputs": [{"path": str(manifest), "sha256": digest, "role": "active_manifest"}],
    }

    result = D02_COMPILE_EFFECTIVE_RUN(state, None)
    print("guard:", result["pending_guard"]["value"])
    print("domain_contract:", result["effective_run"]["domain_contract"])
    print("pending_failure present:", "pending_failure" in result)
