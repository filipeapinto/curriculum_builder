#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time
from typing import Any

from .io import atomic_json, sha256_file


def command_record(command: list[str], engine: Path) -> dict[str, Any]:
    start = time.monotonic()
    result = subprocess.run(command, cwd=engine, capture_output=True, text=True)
    return {
        "command": command, "returncode": result.returncode,
        "elapsed_seconds": round(time.monotonic() - start, 6),
        "stdout": result.stdout, "stderr": result.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-root", type=Path, required=True)
    parser.add_argument("--engine", type=Path, required=True)
    parser.add_argument("--outcome", required=True)
    args = parser.parse_args()
    task_root = args.task_root.resolve()
    engine = args.engine.resolve()
    validations = [
        command_record(["python3", "-m", "unittest", "discover", "-s", "tests/runtime", "-v"], engine),
        command_record(["./tests/run_gates.sh", "4"], engine),
        command_record(["./tests/run_gates.sh", "5"], engine),
        command_record(["python3", "tests/check_meta_prompt.py"], engine),
        command_record(["python3", "src/curriculum_factory/run_curriculum.py", "--curriculum", "curricula/arduino_kit", "--test-static"], engine),
        command_record(["python3", "src/curriculum_factory/run_curriculum.py", "--curriculum", "curricula/arduino_kit", "--test-simulated-all"], engine),
    ]
    current_status = subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all"],
                                    cwd=engine, capture_output=True, text=True, check=True).stdout
    task_changes = [line for line in current_status.splitlines()
                    if line[3:].startswith("src/curriculum_factory/") or line[3:].startswith("tests/runtime/")
                    or line[3:] in {"policy/routes.v1.yaml", "policy/routing/model_registry.v1.yaml",
                                   "policy/routing/routing_policy.v1.yaml"}]
    policies = {
        "policy/routes.v1.yaml": engine / "policy/routes.v1.yaml",
        "policy/routing/model_registry.v1.yaml": engine / "policy/routing/model_registry.v1.yaml",
        "policy/routing/routing_policy.v1.yaml": engine / "policy/routing/routing_policy.v1.yaml",
    }
    before_names = {
        "policy/routes.v1.yaml": task_root / "policy_before/routes.v1.yaml",
        "policy/routing/model_registry.v1.yaml": task_root / "policy_before/model_registry.v1.yaml",
        "policy/routing/routing_policy.v1.yaml": task_root / "policy_before/routing_policy.v1.yaml",
    }
    policy_audit = {}
    for name, current in policies.items():
        before = before_names[name]
        diff = subprocess.run(["git", "diff", "--no-index", "--", str(before), str(current)],
                              cwd=engine, capture_output=True, text=True)
        policy_audit[name] = {
            "before_sha256": sha256_file(before), "after_sha256": sha256_file(current),
            "changed": before.read_bytes() != current.read_bytes(), "exact_diff": diff.stdout,
        }
    proof_path = task_root / "capability_cycle/gemini_proof/live_proof_receipt.json"
    proof = json.loads(proof_path.read_text())
    validation_path = task_root / "validation_results.json"
    atomic_json(validation_path, {"recorded_utc": datetime.now(timezone.utc).isoformat(),
                                  "validations": validations}, root=task_root)
    scope_path = task_root / "final_audit.json"
    audit = {
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "outcome": args.outcome,
        "write_scope": {"task_owned_changes": task_changes,
                        "allowlist": ["src/curriculum_factory/**", "tests/runtime/**", "three unchanged policy files"],
                        "current_status": current_status,
                        "preexisting_baseline": str(task_root / "dirty_worktree_baseline.txt")},
        "policy_audit": policy_audit,
        "live_proof": {"path": str(proof_path), "status": proof["status"],
                       "returncode": proof["returncode"], "init_model": proof["executed_model"],
                       "tool_use_events": sum("tool" in str(event.get("type", "")).lower() for event in proof["events"])},
        "l01_attempt_permitted": False,
        "l01_reason": "single capability cycle did not prove a declared cross-family judge",
    }
    atomic_json(scope_path, audit, root=task_root)
    ledger_path = task_root / "task_ledger.json"
    ledger = json.loads(ledger_path.read_text())
    finished = datetime.now(timezone.utc)
    started = datetime.fromisoformat(ledger["started_at"])
    ledger.update({
        "finished_at": finished.isoformat(), "status": args.outcome,
        "elapsed_seconds": round((finished - started.astimezone(timezone.utc)).total_seconds(), 6),
        "clean_live_l01_attempts": 0, "implementation_correction_cycles": 0,
        "capability_enablement_cycles": 1, "model_calls": 1,
        "cross_family_cli_calls": 1, "primary_source_fetches": 0,
        "imagegen_proof_calls": 0, "aggregate_acceptance_output_bytes": 0,
        "attempts": [], "validation_results": str(validation_path),
        "final_audit": str(scope_path), "capability_receipt": str(proof_path),
    })
    atomic_json(ledger_path, ledger, root=task_root)
    print(json.dumps(ledger, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
