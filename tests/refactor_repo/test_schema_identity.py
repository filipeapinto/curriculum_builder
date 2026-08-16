import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOTS = (
    ROOT / "schemas",
    ROOT / "curricula",
    ROOT / "src/curriculum_factory/langgraph_factory/schemas",
)


def live_schemas():
    for root in SCHEMA_ROOTS:
        for path in root.rglob("*.json"):
            if "deprecated" in path.parts:
                continue
            try:
                document = json.loads(path.read_text())
            except json.JSONDecodeError:
                continue
            if isinstance(document, dict) and "$id" in document:
                yield path, document


def test_live_schema_ids_are_unique_and_local_refs_resolve():
    schemas = list(live_schemas())
    assert schemas
    ids = [document["$id"] for _, document in schemas]
    assert len(ids) == len(set(ids))
    for path, document in schemas:
        assert isinstance(document["$id"], str) and document["$id"]
        stack = [document]
        while stack:
            value = stack.pop()
            if isinstance(value, dict):
                ref = value.get("$ref")
                if isinstance(ref, str) and ref.startswith("#/"):
                    target = document
                    for token in ref[2:].split("/"):
                        target = target[token.replace("~1", "/").replace("~0", "~")]
                stack.extend(value.values())
            elif isinstance(value, list):
                stack.extend(value)


def test_identity_ledger_declares_preservation_policy():
    ledger = (ROOT / "plans_internal/refactor_repo/schema_identity_decisions.v1.yaml").read_text()
    assert "action: preserve" in ledger
    assert "consumer_absence_claimed: false" in ledger
