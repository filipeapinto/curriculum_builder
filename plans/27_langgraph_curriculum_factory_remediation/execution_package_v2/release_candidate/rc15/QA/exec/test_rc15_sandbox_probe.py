from pathlib import Path

from runtime.langgraph_factory import transport as tp
from runtime.langgraph_factory.artifacts import ArtifactStore
from runtime.langgraph_factory.nodes import inputs


class _Context:
    @staticmethod
    def clock():
        return "2026-08-15T00:00:00Z"


def test_undeclared_engine_metadata_cannot_change_a_verdict(tmp_path):
    engine = Path.cwd().resolve()
    probe = Path(
        "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/"
        "release_candidate/rc15/QA/exec"
    )
    curriculum = engine / probe / "rc15_synthetic_curriculum"
    forbidden = probe / "rc15_sandbox_probe_metadata.txt"
    frozen = inputs.D01_VALIDATE_AND_FREEZE_INPUTS(
        {"invocation": {
            "kind": "fresh",
            "contract_version": "test",
            "engine_root": str(engine),
            "curriculum_root": str(curriculum),
            "output_root": str(tmp_path),
            "mode": "one",
            "requested_unit_id": "U001",
            "authorization": {"purpose": "qa"},
            "episode_ordinal": 1,
            "prior_identity": None,
            "prior_terminal": None,
            "lease_open": False,
        }},
        _Context(),
    )
    compiled = inputs.D02_COMPILE_EFFECTIVE_RUN(frozen, _Context())
    contract = compiled["effective_run"]["domain_contract"]
    transport = object.__new__(tp.CliTransport)
    transport.engine_root = engine
    transport.output_root = tmp_path
    transport.render_root = tmp_path / "render"
    transport._artifacts = ArtifactStore(tmp_path)

    forbidden.write_text("1234", encoding="utf-8")
    first = transport.verify_domain(body={"kind": "stat"}, contract=contract)
    forbidden.write_text("12345", encoding="utf-8")
    second = transport.verify_domain(body={"kind": "stat"}, contract=contract)
    assert first["candidate_sha256"] == second["candidate_sha256"]
    assert first["result"] == second["result"], {
        "candidate_sha256": first["candidate_sha256"],
        "first_result": first["result"],
        "first_output": first["candidate"]["output_excerpt"],
        "second_result": second["result"],
        "second_output": second["candidate"]["output_excerpt"],
    }
