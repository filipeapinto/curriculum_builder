"""Reproduce the ancestor-directory metadata channel in RC16's verifier profile."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from runtime.langgraph_factory import transport as tp


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="rc16-ancestor-stat-") as raw:
        root = Path(raw).resolve()
        engine = root / "engine"
        curriculum = engine / "curricula" / "synthetic"
        work = root / "output" / "domain_verifier" / "candidate"
        home = work / "home"
        curriculum.mkdir(parents=True)
        home.mkdir(parents=True)

        entry = curriculum / "verify.py"
        dependency = curriculum / "declared.json"
        undeclared = engine / "undeclared-engine.txt"
        entry.write_text("# frozen verifier\n", encoding="utf-8")
        dependency.write_text("{}\n", encoding="utf-8")
        undeclared.write_text("hidden\n", encoding="utf-8")

        profile = tp.render_sandbox_profile(
            workspace=work,
            home=home,
            readable=(entry, dependency, Path("/usr")),
            allow_network=False,
            metadata_denied=(engine,),
            model_cli_support=False,
        )

        # Freeze a deterministic baseline after all setup writes. A verifier can
        # compare this stat field with a value in the otherwise unchanged candidate.
        baseline_ns = 1_700_000_000_000_000_000
        os.utime(engine, ns=(baseline_ns, baseline_ns))
        first = engine.stat().st_mtime_ns
        first_verdict = "PASS" if first == baseline_ns else "FAIL"

        # Rename only an undeclared repository file. Directory metadata changes,
        # while declared bytes, the candidate, and its frozen contract do not.
        undeclared.rename(engine / "renamed-undeclared-engine.txt")
        second = engine.stat().st_mtime_ns
        second_verdict = "PASS" if second == baseline_ns else "FAIL"

        literal_ancestor = f'(literal "{engine}")'
        print(json.dumps({
            "literal_ancestor_exempted_from_metadata_deny": literal_ancestor in profile,
            "undeclared_path_named_by_profile": str(undeclared) in profile,
            "first_directory_mtime_ns": first,
            "second_directory_mtime_ns": second,
            "directory_metadata_changed": first != second,
            "same_candidate_contract_verdicts": [first_verdict, second_verdict],
            "model_cli_auth_rule_present": str(Path.home() / ".codex" / "auth.json") in profile,
            "network_denied": "(deny network*)" in profile,
        }, sort_keys=True))


if __name__ == "__main__":
    main()
