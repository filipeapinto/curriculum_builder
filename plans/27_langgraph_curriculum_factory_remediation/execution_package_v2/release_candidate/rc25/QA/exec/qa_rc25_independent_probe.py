from __future__ import annotations

import json
import sys
from pathlib import Path


REPO = Path("/Users/filipepinto/Projects/curriculum_builder")
RC22_EXEC = (
    REPO
    / "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2"
    / "release_candidate/rc22/QA/exec"
)
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(RC22_EXEC))

from qa_rc22_adversarial_probe import (  # noqa: E402
    _compile_synthetic,
    _fixture_verifier_prefix,
)


def probe_yaml_dynamic_code(root: Path, source: str) -> dict:
    _engine, _output, compiled, transport = _compile_synthetic(
        root,
        entry_source=source + _fixture_verifier_prefix() + "raise SystemExit(0)\n",
    )
    evidence = {
        "d02_guard": compiled.get("pending_guard", {}).get("value"),
        "d02_failure": compiled.get("pending_failure"),
    }
    if "effective_run" in compiled:
        receipt = transport.verify_domain(
            body={"probe": "yaml-dynamic-code"},
            contract=compiled["effective_run"]["domain_contract"],
        )
        evidence.update(
            {
                "d08_result": receipt["result"],
                "candidate_returncode": receipt["candidate"]["returncode"],
                "candidate_output": receipt["candidate"]["output_excerpt"].strip(),
            }
        )
    return evidence


def main() -> None:
    import tempfile

    cases = {
        "safe_module_reexport": (
            "import yaml\n"
            "print(yaml.unsafe_load(\"!!python/object/apply:builtins.eval "
            "[\\\"'yaml-dynamic-code-loaded'\\\"]\"))\n"
        ),
        "safe_module_import_alias": (
            "from yaml import unsafe_load as parse_yaml\n"
            "print(parse_yaml(\"!!python/object/apply:builtins.eval "
            "[\\\"'yaml-alias-dynamic-code-loaded'\\\"]\"))\n"
        ),
    }
    results = {}
    for name, source in cases.items():
        with tempfile.TemporaryDirectory(prefix=f"rc25-{name}-") as temp:
            results[name] = probe_yaml_dynamic_code(Path(temp), source)
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
