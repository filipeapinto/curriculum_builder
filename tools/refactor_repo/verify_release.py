#!/usr/bin/env python3
"""Deterministic, network-free release checks for the repository refactor."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str], cwd: Path = ROOT) -> None:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(
            f"release check failed ({result.returncode}): {' '.join(command)}\n"
            f"{result.stdout}{result.stderr}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()

    spec = importlib.util.find_spec("curriculum_factory")
    if spec is None or not spec.origin:
        raise SystemExit("curriculum_factory is not installed")
    origin = Path(spec.origin).resolve()
    if ROOT in origin.parents:
        raise SystemExit(f"checkout import leak: {origin}")

    with tempfile.TemporaryDirectory(prefix="curriculum-factory-release-") as directory:
        scratch = Path(directory)
        wheels = scratch / "wheels"
        run(
            [sys.executable, "-m", "pip", "wheel", ".", "--no-deps", "--no-build-isolation", "-w", str(wheels)]
        )
        wheel = next(wheels.glob("curriculum_factory-*.whl"))
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
        required = (
            "curriculum_factory/__init__.py",
            "curriculum_factory/run_curriculum.py",
            "curriculum_factory/langgraph_factory/config/model_jobs.v1.yaml",
            "curriculum_factory/langgraph_factory/prompts/M01_research_unit_sources.prompt.md",
        )
        missing = [name for name in required if name not in names]
        if missing:
            raise SystemExit(f"wheel is missing package resources: {missing}")

    if not args.skip_tests:
        run([sys.executable, "-m", "pytest", "-q"])
    print(json.dumps({"ok": True, "installed_origin": str(origin), "wheel_resources": "verified"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
