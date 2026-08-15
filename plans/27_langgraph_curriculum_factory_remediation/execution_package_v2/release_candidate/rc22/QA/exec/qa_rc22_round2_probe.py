from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from runtime.langgraph_factory import transport as tp

from qa_rc22_adversarial_probe import _compile_synthetic, _fixture_verifier_prefix


def test_d02_rejects_dynamic_surface_reexported_by_safe_module(tmp_path: Path) -> None:
    source = (
        "import enum\n"
        "print(enum.bltns.eval(\"'reexported-dynamic-code-loaded'\"))\n"
        + _fixture_verifier_prefix()
        + "raise SystemExit(0)\n"
    )
    _engine, _output, compiled, transport = _compile_synthetic(
        tmp_path,
        entry_source=source,
    )
    print(json.dumps(compiled, indent=2, default=str))
    receipt = transport.verify_domain(
        body={"probe": "dynamic"},
        contract=compiled["effective_run"]["domain_contract"],
    )
    print(json.dumps(receipt, indent=2, default=str))
    assert compiled["pending_failure"]["cause"] == "schema_contract"


@pytest.mark.skipif(
    tp.sandbox_mechanism() == tp.SANDBOX_UNAVAILABLE,
    reason="host sandbox unavailable",
)
def test_lchmod_engine_path_is_invariant(tmp_path: Path) -> None:
    undeclared = tmp_path / "engine" / "undeclared"
    parts = list(undeclared.resolve().parts[1:])
    entry_source = (
        "import pathlib\n"
        + _fixture_verifier_prefix()
        + f"target = pathlib.os.sep + pathlib.os.path.join(*{parts!r})\n"
        "try: pathlib.os.lchmod(target, 0o600)\n"
        "except PermissionError: print('permission'); raise SystemExit(0)\n"
        "except FileNotFoundError: print('missing'); raise SystemExit(1)\n"
        "print('completed'); raise SystemExit(2)\n"
    )
    engine, _output, compiled, transport = _compile_synthetic(
        tmp_path,
        entry_source=entry_source,
    )
    assert compiled["pending_guard"]["value"] == "effective_run_compiled"
    contract = compiled["effective_run"]["domain_contract"]
    undeclared.write_text("hidden\n", encoding="utf-8")
    body = {"probe": "same"}

    first = transport.verify_domain(body=body, contract=contract)
    undeclared.rename(engine / "renamed")
    second = transport.verify_domain(body=body, contract=contract)
    evidence = {
        "same_candidate": first["candidate_sha256"] == second["candidate_sha256"],
        "same_contract": first["contract_sha256"] == second["contract_sha256"],
        "existing": first["candidate"],
        "absent": second["candidate"],
    }
    print(json.dumps(evidence, indent=2))
    assert first["result"] == second["result"]
