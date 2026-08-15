from runtime.langgraph_factory.nodes import canonical_digest
from runtime.langgraph_factory.nodes.visuals import D12_VISUAL_BARRIER_AND_JOIN


unit_id = "U001"
content_hash = "c" * 64
domain_hash = "d" * 64
visual_stream = f"units/{unit_id}/visuals"

# D20's repaired genesis has corrected a reviewer-identified accessibility defect.
repaired_body = {
    "unit_id": unit_id,
    "visuals": {
        "v1": {
            "key": "v1",
            "unit_id": unit_id,
            "subset": "deterministic",
            "provenance": "deterministic_renderer",
            "sha256": "a" * 64,
            "format": "png",
            "accessibility_text": "Corrected accessible description",
        }
    },
}
repaired_hash = canonical_digest(repaired_body)
repaired_record = {
    "stream": visual_stream,
    "version": 1,
    "parent_hash": None,
    "hash": repaired_hash,
    "body": repaired_body,
}

# The pre-repair join input remains in state. D21 routes a visual repair through
# D10 and then D12; D12 reconstructs from this stale result rather than checking
# the repaired current head.
state = {
    "selected_unit_id": unit_id,
    "visual_denominators": {
        "denominator": {
            "unit_id": unit_id,
            "content_hash": content_hash,
            "deterministic_keys": ["v1"],
            "model_keys": [],
        }
    },
    "visual_briefs": [{"key": "v1", "unit_id": unit_id, "content_hash": content_hash}],
    "visual_results": {
        "v1": {
            "key": "v1",
            "unit_id": unit_id,
            "subset": "deterministic",
            "provenance": "deterministic_renderer",
            "content_hash": content_hash,
            "sha256": "a" * 64,
            "format": "png",
            "accessibility_text": "Original defective description",
        }
    },
    "artifact_versions": [repaired_record],
    "artifact_heads": {
        f"units/{unit_id}/content": {"version": 1, "parent_hash": None, "hash": content_hash},
        f"units/{unit_id}/domain": {"version": 1, "parent_hash": None, "hash": domain_hash},
        visual_stream: {"version": 1, "parent_hash": None, "hash": repaired_hash},
    },
    "run_id": "run",
    "episode_id": "episode",
}

result = D12_VISUAL_BARRIER_AND_JOIN(state, None)
print("guard:", result["pending_guard"]["value"])
print("candidate version:", result["artifact_versions"][0]["version"])
print("candidate parent:", result["artifact_versions"][0]["parent_hash"])
print("candidate accessibility:", result["artifact_versions"][0]["body"]["visuals"]["v1"]["accessibility_text"])
print("repaired accessibility:", repaired_body["visuals"]["v1"]["accessibility_text"])
print("repaired head:", repaired_hash)
