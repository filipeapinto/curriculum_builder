from pathlib import Path
import json
import tempfile

from runtime.langgraph_factory.nodes import canonical_digest
from runtime.langgraph_factory.nodes.content import D09_VALIDATE_CONTENT
from runtime.langgraph_factory.repair import D20_ADMIT_UNIT_REPAIR


with tempfile.TemporaryDirectory(prefix="rc13-content-revalidation-") as directory:
    root = Path(directory)
    schema_path = root / "content.schema.json"
    schema_path.write_text(json.dumps({"type": "object"}), encoding="utf-8")

    unit_id = "U001"
    domain_stream = f"units/{unit_id}/domain"
    content_stream = f"units/{unit_id}/content"
    body = {"sections": [{"heading": "Test", "body": "Repaired content"}]}
    invalid_body = {"sections": [{"heading": "Test", "body": ""}]}
    invalid_hash = canonical_digest(invalid_body)
    invalid_record = {
        "stream": content_stream,
        "version": 1,
        "parent_hash": None,
        "hash": invalid_hash,
        "body": invalid_body,
        "schema_path": schema_path.name,
        "domain_hash": "d" * 64,
    }
    request = {
        "key": "repair-request",
        "unit_id": unit_id,
        "owner": "unit content",
        "channel": "content",
        "stream": content_stream,
        "boundary": {"json_pointers": ["/sections/0/body"]},
        "parent_hash": invalid_hash,
        "attempt_ordinal": 1,
    }
    model_candidate = {
        "record_kind": "model_candidate",
        "job_id": "M06_REPAIR_NAMED_UNIT_ARTIFACT",
        "channel": "content",
        "unit_id": unit_id,
        "parent_sha256": invalid_hash,
        "payload": {
            "candidate_child": {
                "artifact_name": f"content:{unit_id}",
                "artifact_body": json.dumps(body),
                "addressed_finding_ids": ["finding"],
            },
            "changed_path_manifest": [
                {
                    "json_pointer": "/sections/0/body",
                    "change_kind": "replace",
                    "finding_id": "finding",
                }
            ],
        },
    }
    pre_admission_state = {
        "selected_unit_id": unit_id,
        "artifact_versions": [invalid_record, model_candidate],
        "artifact_heads": {
            domain_stream: {"version": 1, "parent_hash": None, "hash": "d" * 64},
        },
        "repair_requests": [request],
    }
    admitted = D20_ADMIT_UNIT_REPAIR(pre_admission_state, None)
    content_record = admitted["artifact_versions"][0]
    content_hash = content_record["hash"]
    print("D20 child has schema_path:", "schema_path" in content_record)
    print("D20 child has domain_hash:", "domain_hash" in content_record)

    state = {
        "selected_unit_id": unit_id,
        "effective_run": {},
        "artifact_versions": [content_record],
        "artifact_heads": {
            domain_stream: {"version": 1, "parent_hash": None, "hash": "d" * 64},
            **admitted["artifact_heads"],
        },
        "engine_root": str(root),
    }

    # This is the state D20 -> D21 presents to D09 for a repaired first child.
    result = D09_VALIDATE_CONTENT(state, None)
    print(result)
