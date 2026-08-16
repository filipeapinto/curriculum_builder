#!/usr/bin/env python3
"""Pre-refactor behavioral baseline capture (spec v8 section 7, "Behavioral baseline").

Usage:
    python3 tools/refactor_repo/baseline.py capture \\
        --repo-root /path/to/isolated/checkout --output-dir /path/to/write/into

    python3 tools/refactor_repo/baseline.py compare \\
        --first /path/to/first.json --second /path/to/second.json \\
        --normalization-rules /path/to/first.normalization.json

Every capture is read-only: it runs the documented CLI with ``--help`` and
with intentionally invalid arguments (both fail before touching the network
or the filesystem beyond argparse's own error path), collects test/gate
counts, records import origins, checks in-process schema resolution and
output-boundary containment, and hashes representative tracked artifacts. It
writes nothing into ``--repo-root``; all output goes to ``--output-dir``.
Nondeterministic fields (timestamps, absolute paths, wall-clock durations)
are named as ``normalization_rules`` in the capture itself, written before
any second capture is taken, so a later comparison can apply only rules
that were declared in advance rather than invented post hoc to force a match.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Rules a comparison may use to treat two capture fields as equivalent
# despite literal difference. These are declared once, here, before any
# second capture is ever taken — the prompt's "narrow written normalization
# rules" requirement (test 5).
NORMALIZATION_RULES = [
    "captured_at_utc: ignore literal value; both captures are expected to run at different times.",
    "repository_commit: ignore literal value only if both captures were taken against the same "
    "checkout state as recorded by tests_and_gates.pytest_collect.exit_code and collected_count; "
    "a differing commit is reported, never silently dropped.",
    "import_origin.origin: compared as origin_relative_to_repo_root (already computed at capture "
    "time by resolving against that capture's own repo_root), not the raw absolute origin, so two "
    "different checkout locations for the same relative module compare equal. The relative path "
    "itself changing (runtime/__init__.py -> src/curriculum_factory/__init__.py) is not normalized "
    "away: that is the intended P03 source move, a real and expected difference, not noise.",
    "cli_help_and_invalid_input[*].stdout_sha256/stderr_sha256: compared as literal digests; "
    "argparse output is deterministic for a fixed argv and program name, so no normalization "
    "is applied here — a changed digest is a real behavioral difference.",
    "output_containment: compared by which case (accepted/rejected) raised and which did not, "
    "not by the literal resolved path (which embeds the checkout's absolute location).",
]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run(cmd: list[str], cwd: Path, timeout: int = 60) -> dict:
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return {
            "command": " ".join(cmd),
            "exit_code": result.returncode,
            "stdout_sha256": sha256_text(result.stdout),
            "stderr_sha256": sha256_text(result.stderr),
            "stdout_len": len(result.stdout),
            "stderr_len": len(result.stderr),
        }
    except subprocess.TimeoutExpired:
        return {"command": " ".join(cmd), "exit_code": None, "error": "timeout"}
    except OSError as exc:
        return {"command": " ".join(cmd), "exit_code": None, "error": f"{type(exc).__name__}: {exc}"}


def capture_tests_and_gates(repo_root: Path) -> dict:
    collect = run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "tests/runtime", "tests/gates"],
        cwd=repo_root, timeout=120,
    )
    selftest = run([sys.executable, "tests/gates/selftest.py"], cwd=repo_root, timeout=120)
    return {"pytest_collect": collect, "gate_harness_selftest": selftest}


def capture_documented_commands(repo_root: Path) -> list[dict]:
    return [
        run([sys.executable, "-m", "curriculum_factory.run_curriculum", "--help"], cwd=repo_root / "src"),
    ]


def capture_import_origin(repo_root: Path) -> dict:
    code = "import sys; sys.path.insert(0, '.'); import curriculum_factory; print(curriculum_factory.__file__)"
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=repo_root / "src", capture_output=True, text=True, timeout=30,
    )
    origin = result.stdout.strip()
    relative = None
    try:
        relative = str(Path(origin).resolve().relative_to(repo_root.resolve()))
    except (ValueError, OSError):
        pass
    return {
        "exit_code": result.returncode,
        "origin": origin,
        "origin_relative_to_repo_root": relative,
        "mechanism": "repository-root sys.path injection (no installed distribution exists yet)",
    }


def capture_cli_help_and_invalid_input(repo_root: Path) -> list[dict]:
    return [
        run([sys.executable, "-m", "curriculum_factory.run_curriculum", "--help"], cwd=repo_root / "src"),
        run([sys.executable, "-m", "curriculum_factory.run_curriculum"], cwd=repo_root / "src"),  # missing required args
        run([sys.executable, "-m", "curriculum_factory.run_curriculum", "--engine-root", "x"], cwd=repo_root / "src"),  # partial args
    ]


def capture_schema_resolution(repo_root: Path) -> list[dict]:
    sys.path.insert(0, str(repo_root))
    import jsonschema  # noqa: E402

    results = []
    schemas_dir = repo_root / "schemas"
    for path in sorted(schemas_dir.glob("*.json")):
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator.check_schema(schema)
            results.append({"path": str(path.relative_to(repo_root)), "id": schema.get("$id", ""), "resolves": True})
        except Exception as exc:  # noqa: BLE001
            results.append({
                "path": str(path.relative_to(repo_root)), "resolves": False,
                "error": f"{type(exc).__name__}: {exc}",
            })
    return results


def capture_output_containment(repo_root: Path) -> dict:
    sys.path.insert(0, str(repo_root / "src"))
    from curriculum_factory.io import require_internal_output, BoundaryError  # noqa: E402

    accepted = {"raised": False, "case": "engine/outputs/run1"}
    try:
        require_internal_output(repo_root / "outputs" / "run1", repo_root)
    except BoundaryError as exc:
        accepted = {"raised": True, "case": "engine/outputs/run1", "error": str(exc)}

    rejected = {"raised": False, "case": "external /tmp path"}
    try:
        require_internal_output(Path("/tmp/refactor_repo_baseline_external"), repo_root)
        rejected = {"raised": False, "case": "external /tmp path"}
    except BoundaryError as exc:
        rejected = {"raised": True, "case": "external /tmp path", "error_type": type(exc).__name__}

    return {"accepted_case": accepted, "rejected_case": rejected}


REPRESENTATIVE_ARTIFACTS = [
    "curricula/arduino_kit/arduino_kit_curriculum.v5.yaml",
    "policy/controller.v1.yaml",
    "schemas/curriculum.schema.v5.json",
    "meta_prompt/curriculum.prompt.v1.md",
]


def capture_representative_artifacts(repo_root: Path) -> list[dict]:
    entries = []
    for relative in REPRESENTATIVE_ARTIFACTS:
        path = repo_root / relative
        if not path.exists():
            entries.append({"path": relative, "present": False})
            continue
        entries.append({
            "path": relative, "present": True,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size_bytes": path.stat().st_size,
        })
    return entries


def capture(repo_root: Path) -> dict:
    repo_root = repo_root.resolve()
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, capture_output=True, text=True,
    ).stdout.strip()

    tests_and_gates = capture_tests_and_gates(repo_root)
    existing_failures = []
    if tests_and_gates["pytest_collect"].get("exit_code") not in (0, None):
        existing_failures.append({
            "check": "pytest_collect", "exit_code": tests_and_gates["pytest_collect"].get("exit_code"),
        })
    if tests_and_gates["gate_harness_selftest"].get("exit_code") not in (0, None):
        existing_failures.append({
            "check": "gate_harness_selftest",
            "exit_code": tests_and_gates["gate_harness_selftest"].get("exit_code"),
        })

    document = {
        "captured_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repository_commit": commit,
        "tests_and_gates": tests_and_gates,
        "documented_commands": capture_documented_commands(repo_root),
        "import_origin": capture_import_origin(repo_root),
        "cli_help_and_invalid_input": capture_cli_help_and_invalid_input(repo_root),
        "schema_resolution": capture_schema_resolution(repo_root),
        "output_containment": capture_output_containment(repo_root),
        "representative_artifacts": capture_representative_artifacts(repo_root),
        "existing_failures": existing_failures,
        "normalization_rules": NORMALIZATION_RULES,
    }
    return document


def compare(first: dict, second: dict) -> dict:
    diffs = []
    equivalent = []

    def note(field: str, a, b, is_equivalent: bool):
        (equivalent if is_equivalent else diffs).append({"field": field, "first": a, "second": b})

    note("repository_commit",
         first["repository_commit"], second["repository_commit"],
         first["repository_commit"] == second["repository_commit"])

    for key in ("pytest_collect", "gate_harness_selftest"):
        a = first["tests_and_gates"][key]
        b = second["tests_and_gates"][key]
        note(f"tests_and_gates.{key}.exit_code", a.get("exit_code"), b.get("exit_code"),
             a.get("exit_code") == b.get("exit_code"))

    a_origin = first["import_origin"]["origin_relative_to_repo_root"]
    b_origin = second["import_origin"]["origin_relative_to_repo_root"]
    note("import_origin.origin (relative to repo root)", a_origin, b_origin, a_origin == b_origin)

    for i, (a, b) in enumerate(zip(first["cli_help_and_invalid_input"], second["cli_help_and_invalid_input"])):
        note(f"cli_help_and_invalid_input[{i}].exit_code", a.get("exit_code"), b.get("exit_code"),
             a.get("exit_code") == b.get("exit_code"))
        note(f"cli_help_and_invalid_input[{i}].stdout_sha256", a.get("stdout_sha256"), b.get("stdout_sha256"),
             a.get("stdout_sha256") == b.get("stdout_sha256"))
        note(f"cli_help_and_invalid_input[{i}].stderr_sha256", a.get("stderr_sha256"), b.get("stderr_sha256"),
             a.get("stderr_sha256") == b.get("stderr_sha256"))

    a_schema_ok = {s["path"]: s["resolves"] for s in first["schema_resolution"]}
    b_schema_ok = {s["path"]: s["resolves"] for s in second["schema_resolution"]}
    note("schema_resolution (path->resolves map)", a_schema_ok, b_schema_ok, a_schema_ok == b_schema_ok)

    note("output_containment.accepted_case.raised",
         first["output_containment"]["accepted_case"]["raised"],
         second["output_containment"]["accepted_case"]["raised"],
         first["output_containment"]["accepted_case"]["raised"]
         == second["output_containment"]["accepted_case"]["raised"])
    note("output_containment.rejected_case.raised",
         first["output_containment"]["rejected_case"]["raised"],
         second["output_containment"]["rejected_case"]["raised"],
         first["output_containment"]["rejected_case"]["raised"]
         == second["output_containment"]["rejected_case"]["raised"])

    a_artifacts = {a["path"]: a.get("sha256") for a in first["representative_artifacts"]}
    b_artifacts = {a["path"]: a.get("sha256") for a in second["representative_artifacts"]}
    note("representative_artifacts (path->sha256 map)", a_artifacts, b_artifacts, a_artifacts == b_artifacts)

    return {
        "equivalent_count": len(equivalent),
        "differing_count": len(diffs),
        "differences": diffs,
        "equivalent_fields": [e["field"] for e in equivalent],
        "verdict": "EQUIVALENT" if not diffs else "CHANGED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="mode", required=True)

    cap = sub.add_parser("capture")
    cap.add_argument("--repo-root", required=True, type=Path)
    cap.add_argument("--output-dir", required=True, type=Path)
    cap.add_argument("--label", default="capture")

    cmp_parser = sub.add_parser("compare")
    cmp_parser.add_argument("--first", required=True, type=Path)
    cmp_parser.add_argument("--second", required=True, type=Path)
    cmp_parser.add_argument("--output", required=True, type=Path)

    args = parser.parse_args(argv)

    if args.mode == "capture":
        document = capture(args.repo_root)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = document["captured_at_utc"].replace(":", "").replace("-", "")
        out_path = args.output_dir / f"behavioral_baseline.{args.label}.{stamp}.json"
        out_path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(out_path), "existing_failures": document["existing_failures"]}, indent=2))
        return 0

    if args.mode == "compare":
        first = json.loads(args.first.read_text(encoding="utf-8"))
        second = json.loads(args.second.read_text(encoding="utf-8"))
        result = compare(first, second)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0 if result["verdict"] == "EQUIVALENT" else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
