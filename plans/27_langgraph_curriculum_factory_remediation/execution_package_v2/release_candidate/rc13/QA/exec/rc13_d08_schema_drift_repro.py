from pathlib import Path
from types import SimpleNamespace
import hashlib
import json
import tempfile

from runtime.langgraph_factory.nodes import canonical_digest
from runtime.langgraph_factory.nodes.domain import CURRICULUM_CONTRACTS, D08_VALIDATE_DOMAIN


class PassingVerifier:
    def verify_domain(self, *, body, contract):
        return {
            "result": "PASS",
            "candidate_sha256": canonical_digest(body),
            "fixtures_result": "PASS",
            "candidate": {"returncode": 0, "codes": []},
        }


with tempfile.TemporaryDirectory(prefix="rc13-d08-schema-drift-") as directory:
    root = Path(directory).resolve()
    for relative in CURRICULUM_CONTRACTS:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}", encoding="utf-8")
    schema = root / "domain.schema.json"
    original = {
        "type": "object",
        "required": ["required_field"],
        "properties": {"required_field": {"type": "string"}},
    }
    schema.write_text(json.dumps(original), encoding="utf-8")
    frozen_sha = hashlib.sha256(schema.read_bytes()).hexdigest()

    # Drift after D02/M02 staging: the replacement now admits the candidate.
    schema.write_text(json.dumps({"type": "object"}), encoding="utf-8")
    body = {"other": "not valid under the frozen schema"}
    body_hash = canonical_digest(body)
    stream = "units/U001/domain"
    state = {
        "selected_unit_id": "U001",
        "effective_run": {
            "unit_records": [{"id": "U001", "title": "Synthetic"}],
            "domain_contract": {"schema": {"path": schema.name, "sha256": frozen_sha}},
        },
        "artifact_versions": [
            {
                "stream": stream,
                "version": 1,
                "parent_hash": None,
                "hash": body_hash,
                "body": body,
                "schema_path": schema.name,
                "evidence_references": [{"source_id": "s1"}],
            }
        ],
        "artifact_heads": {},
        "source_admissions": [{"key": "s1", "fact_id": "f1", "unit_id": "U001"}],
        "engine_root": str(root),
        "run_id": "run",
        "episode_id": "episode",
    }
    result = D08_VALIDATE_DOMAIN(
        state, SimpleNamespace(transport_registry=PassingVerifier())
    )
    print("frozen schema sha256:", frozen_sha)
    print("current schema sha256:", hashlib.sha256(schema.read_bytes()).hexdigest())
    print("result:", result)
