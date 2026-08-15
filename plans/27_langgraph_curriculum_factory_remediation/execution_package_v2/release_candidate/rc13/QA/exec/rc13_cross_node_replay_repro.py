from pathlib import Path
from types import SimpleNamespace
import tempfile

from runtime.langgraph_factory import graph
from runtime.langgraph_factory.artifacts import ArtifactStore, canonical_digest


body = {"unit_id": "U001", "facts": [{"fact_id": "f1", "statement": "repaired"}]}
content_hash = canonical_digest(body)
stream = "units/U001/domain"
record = {
    "stream": stream,
    "version": 1,
    "parent_hash": None,
    "hash": content_hash,
    "body": body,
}
head = {"version": 1, "parent_hash": None, "hash": content_hash}

with tempfile.TemporaryDirectory(prefix="rc13-cross-node-") as directory:
    context = SimpleNamespace(path_guard=ArtifactStore(Path(directory)))

    # D20 physically admits a repaired first child as genesis.
    graph._persist_admitted_head_updates(
        "D20_ADMIT_UNIT_REPAIR",
        {"artifact_versions": []},
        {"artifact_versions": [record], "artifact_heads": {stream: head}},
        context,
    )
    print("D20 physical admission: PASS")

    # D08's required retest returns the already-admitted logical head again.
    # This must be an idempotent same-checkpoint/head replay.
    graph._persist_admitted_head_updates(
        "D08_VALIDATE_DOMAIN",
        {"artifact_versions": [record], "artifact_heads": {stream: head}},
        {"artifact_heads": {stream: head}},
        context,
    )
    print("D08 repaired-head revalidation: PASS")
