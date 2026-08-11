#!/usr/bin/env python3
"""Deterministic execution controller for the Plan 26 prompt graph.

The controller schedules Claude Sonnet implementation prompts.  It is not the
curriculum factory runtime and intentionally contains no LangGraph replacement.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Iterable, Sequence

import jsonschema
import yaml


PLAN_DIR = Path(__file__).resolve().parent
REPO_ROOT = PLAN_DIR.parents[1]
DEFAULT_MANIFEST = PLAN_DIR / "implementation.graph.v3.yaml"
EPHEMERAL_NAMES = {".DS_Store", ".plan26-run", ".pytest_cache", "__pycache__"}
EPHEMERAL_SUFFIXES = {".pyc", ".pyo"}


class ControllerError(RuntimeError):
    """A deterministic controller invariant failed."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ignored(relative: Path) -> bool:
    return any(part in EPHEMERAL_NAMES for part in relative.parts) or relative.suffix in EPHEMERAL_SUFFIXES


def snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.relative_to(root).parts:
            continue
        relative = path.relative_to(root)
        if ignored(relative):
            continue
        result[relative.as_posix()] = sha256_file(path)
    return result


def path_digest(root: Path, relative: str) -> str | None:
    path = root / relative
    if path.is_file():
        return sha256_file(path)
    if path.is_dir():
        digest = hashlib.sha256()
        for child in sorted(path.rglob("*")):
            if not child.is_file():
                continue
            child_rel = child.relative_to(root)
            if ignored(child_rel):
                continue
            digest.update(child_rel.as_posix().encode())
            digest.update(b"\0")
            digest.update(sha256_file(child).encode())
            digest.update(b"\n")
        return digest.hexdigest()
    return None


def covers(owner: str, changed: str) -> bool:
    owner_path = Path(owner)
    changed_path = Path(changed)
    return owner_path == changed_path or owner_path in changed_path.parents


def paths_overlap(left: str, right: str) -> bool:
    return covers(left, right) or covers(right, left)


def run_command(
    argv: Sequence[str], cwd: Path, timeout: int, log_path: Path
) -> dict[str, Any]:
    started = utc_now()
    try:
        completed = subprocess.run(
            list(argv),
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        output = completed.stdout
        exit_code = completed.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + "\nTIMEOUT\n"
        exit_code = 124
        timed_out = True
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(output, encoding="utf-8")
    return {
        "argv": list(argv),
        "started_at": started,
        "finished_at": utc_now(),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "log": log_path.relative_to(cwd).as_posix() if log_path.is_relative_to(cwd) else str(log_path),
        "log_sha256": sha256_file(log_path),
        "tail": output[-4000:],
    }


@dataclasses.dataclass(frozen=True)
class Manifest:
    path: Path
    data: dict[str, Any]

    @property
    def nodes(self) -> dict[str, dict[str, Any]]:
        return self.data["nodes"]

    @property
    def digest(self) -> str:
        return sha256_file(self.path)

    @property
    def state_dir(self) -> Path:
        return REPO_ROOT / self.data["execution"]["state_dir"]

    @classmethod
    def load(cls, path: Path) -> "Manifest":
        absolute = path if path.is_absolute() else REPO_ROOT / path
        data = yaml.safe_load(absolute.read_text(encoding="utf-8"))
        schema_path = REPO_ROOT / data["schema"]
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(data)
        manifest = cls(path=absolute, data=data)
        manifest.validate_invariants()
        return manifest

    def validate_invariants(self) -> None:
        nodes = set(self.nodes)
        entry = self.data["entry"]
        if entry not in nodes:
            raise ControllerError(f"unknown entry node: {entry}")
        for node_id, node in self.nodes.items():
            prompt = REPO_ROOT / node["prompt"]
            if not prompt.is_file():
                raise ControllerError(f"{node_id}: missing prompt {node['prompt']}")
            unknown = set(node["depends_on"]) - nodes
            if unknown:
                raise ControllerError(f"{node_id}: unknown dependencies {sorted(unknown)}")
            if node_id in node["depends_on"]:
                raise ControllerError(f"{node_id}: self dependency")

        declared_edges = {(edge["from"], edge["to"]) for edge in self.data["edges"]}
        dependency_edges = {
            (dependency, node_id)
            for node_id, node in self.nodes.items()
            for dependency in node["depends_on"]
        }
        if declared_edges != dependency_edges:
            missing = sorted(dependency_edges - declared_edges)
            extra = sorted(declared_edges - dependency_edges)
            raise ControllerError(f"edge/dependency mismatch; missing={missing}, extra={extra}")

        order = self.topological_order()
        reachable = {entry}
        for node_id in order:
            if node_id == entry or any(dep in reachable for dep in self.nodes[node_id]["depends_on"]):
                reachable.add(node_id)
        if reachable != nodes:
            raise ControllerError(f"unreachable nodes: {sorted(nodes - reachable)}")

        for key, owner in self.data["rework_edges"].items():
            if owner not in nodes:
                raise ControllerError(f"rework owner {key} names unknown node {owner}")

        for index, left_id in enumerate(order):
            for right_id in order[index + 1 :]:
                if self.depends_transitively(left_id, right_id) or self.depends_transitively(right_id, left_id):
                    continue
                for left in self.nodes[left_id]["writes"]:
                    for right in self.nodes[right_id]["writes"]:
                        if paths_overlap(left, right):
                            raise ControllerError(
                                f"concurrently eligible write sets overlap: {left_id}:{left} and {right_id}:{right}"
                            )

    def topological_order(self) -> list[str]:
        remaining = {node_id: set(node["depends_on"]) for node_id, node in self.nodes.items()}
        order: list[str] = []
        while remaining:
            ready = sorted(node_id for node_id, dependencies in remaining.items() if not dependencies)
            if not ready:
                raise ControllerError(f"cycle detected among {sorted(remaining)}")
            order.extend(ready)
            for node_id in ready:
                remaining.pop(node_id)
            for dependencies in remaining.values():
                dependencies.difference_update(ready)
        return order

    def descendants(self, node_id: str) -> set[str]:
        result: set[str] = set()
        frontier = [node_id]
        while frontier:
            current = frontier.pop()
            for candidate, node in self.nodes.items():
                if current in node["depends_on"] and candidate not in result:
                    result.add(candidate)
                    frontier.append(candidate)
        return result

    def depends_transitively(self, node_id: str, possible_ancestor: str) -> bool:
        frontier = list(self.nodes[node_id]["depends_on"])
        seen: set[str] = set()
        while frontier:
            current = frontier.pop()
            if current == possible_ancestor:
                return True
            if current not in seen:
                seen.add(current)
                frontier.extend(self.nodes[current]["depends_on"])
        return False


class ReceiptStore:
    def __init__(self, manifest: Manifest) -> None:
        self.manifest = manifest
        self.root = manifest.state_dir
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, node_id: str) -> Path:
        return self.root / f"{node_id}.receipt.v1.json"

    def load(self, node_id: str) -> dict[str, Any] | None:
        path = self.path(node_id)
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def save(self, receipt: dict[str, Any]) -> None:
        schema_path = REPO_ROOT / self.manifest.data["execution"]["receipt_schema"]
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(receipt)
        target = self.path(receipt["node_id"])
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(target)

    def node_definition_digest(self, node_id: str) -> str:
        payload = {
            "node_id": node_id,
            "definition": self.manifest.nodes[node_id],
            "rules": self.manifest.data["rules"],
        }
        return sha256_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())

    def input_fingerprint(self, node_id: str) -> str | None:
        node = self.manifest.nodes[node_id]
        predecessors: dict[str, str] = {}
        for predecessor in node["depends_on"]:
            receipt = self.admissible(predecessor)
            if receipt is None:
                return None
            predecessors[predecessor] = sha256_file(self.path(predecessor))
        environment = {
            path: path_digest(REPO_ROOT, path)
            for path in self.manifest.data["execution"]["cache"]["environment_files"]
        }
        payload = {
            "node": node_id,
            "node_definition": self.node_definition_digest(node_id),
            "prompt": sha256_file(REPO_ROOT / node["prompt"]),
            "source_spec": sha256_file(REPO_ROOT / self.manifest.data["source_spec"]),
            "predecessors": predecessors,
            "environment": environment,
        }
        return sha256_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())

    def admissible(self, node_id: str, seen: set[str] | None = None) -> dict[str, Any] | None:
        seen = set() if seen is None else set(seen)
        if node_id in seen:
            return None
        seen.add(node_id)
        receipt = self.load(node_id)
        if receipt is None or receipt.get("node_definition_sha256") != self.node_definition_digest(node_id):
            return None
        if receipt.get("status") not in self.manifest.nodes[node_id].get("allowed_results", ["PASSED", "BLOCKED"]):
            return None
        if receipt.get("status") == "BLOCKED":
            return None
        if any(self.admissible(predecessor, seen) is None for predecessor in self.manifest.nodes[node_id]["depends_on"]):
            return None
        fingerprint = self.input_fingerprint_without_recursing(node_id)
        if fingerprint is None or receipt.get("input_fingerprint") != fingerprint:
            return None
        for relative, expected in receipt.get("outputs", {}).items():
            if path_digest(REPO_ROOT, relative) != expected:
                return None
        return receipt

    def input_fingerprint_without_recursing(self, node_id: str) -> str | None:
        node = self.manifest.nodes[node_id]
        predecessors: dict[str, str] = {}
        for predecessor in node["depends_on"]:
            predecessor_receipt = self.load(predecessor)
            if predecessor_receipt is None:
                return None
            if predecessor_receipt.get("status") not in {"PASSED", "NOT_AVAILABLE"}:
                return None
            if predecessor_receipt.get("node_definition_sha256") != self.node_definition_digest(predecessor):
                return None
            for relative, expected in predecessor_receipt.get("outputs", {}).items():
                if path_digest(REPO_ROOT, relative) != expected:
                    return None
            predecessors[predecessor] = sha256_file(self.path(predecessor))
        environment = {
            path: path_digest(REPO_ROOT, path)
            for path in self.manifest.data["execution"]["cache"]["environment_files"]
        }
        payload = {
            "node": node_id,
            "node_definition": self.node_definition_digest(node_id),
            "prompt": sha256_file(REPO_ROOT / node["prompt"]),
            "source_spec": sha256_file(REPO_ROOT / self.manifest.data["source_spec"]),
            "predecessors": predecessors,
            "environment": environment,
        }
        return sha256_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())


class Controller:
    def __init__(self, manifest: Manifest) -> None:
        self.manifest = manifest
        self.receipts = ReceiptStore(manifest)

    def status(self) -> dict[str, Any]:
        statuses: dict[str, str] = {}
        stale: list[str] = []
        for node_id in self.manifest.topological_order():
            receipt = self.receipts.admissible(node_id)
            if receipt:
                statuses[node_id] = receipt["status"]
            elif all(self.receipts.admissible(dep) for dep in self.manifest.nodes[node_id]["depends_on"]):
                statuses[node_id] = "READY"
                if self.receipts.load(node_id):
                    stale.append(node_id)
            else:
                statuses[node_id] = "PENDING"
        ready = [node_id for node_id, status in statuses.items() if status == "READY"]
        return {
            "graph_id": self.manifest.data["graph_id"],
            "graph_digest": self.manifest.digest,
            "statuses": statuses,
            "stale_receipts": stale,
            "ready": ready,
            "selected": self.select_disjoint(ready),
        }

    def select_disjoint(self, ready: Iterable[str]) -> list[str]:
        selected: list[str] = []
        owned: list[str] = []
        limit = self.manifest.data["execution"]["max_parallel"]
        for node_id in sorted(ready):
            writes = self.manifest.nodes[node_id]["writes"]
            if any(paths_overlap(candidate, existing) for candidate in writes for existing in owned):
                continue
            selected.append(node_id)
            owned.extend(writes)
            if len(selected) >= limit:
                break
        return selected

    def python_executable(self) -> str:
        override = os.environ.get("PLAN26_PYTHON")
        if override:
            candidate = Path(override)
            if not candidate.is_file() or not os.access(candidate, os.X_OK):
                raise ControllerError(f"PLAN26_PYTHON is not executable: {override}")
            return str(candidate)
        for value in self.manifest.data["execution"]["python_candidates"]:
            resolved = shutil.which(value)
            if resolved:
                return resolved
        raise ControllerError("no Plan 26 Python candidate is executable")

    def _verification(self, node_id: str, cwd: Path, attempt: str) -> list[dict[str, Any]]:
        commands: list[dict[str, Any]] = []
        timeout = self.manifest.data["execution"]["test_timeout_seconds"]
        log_root = self.receipts.root / "logs" / node_id
        for index, argv in enumerate(self.manifest.nodes[node_id].get("verification", []), start=1):
            resolved_argv = [self.python_executable() if value == "{python}" else value for value in argv]
            result = run_command(resolved_argv, cwd, timeout, log_root / f"{attempt}.test{index}.log")
            commands.append(result)
            if result["exit_code"] != 0:
                break
        return commands

    def adopt_v2(self, through: str | None = None) -> dict[str, Any]:
        adopted: list[str] = []
        stopped: dict[str, Any] | None = None
        for node_id in self.manifest.topological_order():
            if self.receipts.admissible(node_id):
                adopted.append(node_id)
            else:
                node = self.manifest.nodes[node_id]
                if not all(self.receipts.admissible(dep) for dep in node["depends_on"]):
                    stopped = {"node": node_id, "reason": "predecessor_not_adopted"}
                    break
                legacy_path = REPO_ROOT / self.manifest.data["execution"]["legacy_result_pattern"].format(node_id=node_id)
                if not legacy_path.is_file() or "status: PASSED" not in legacy_path.read_text(encoding="utf-8")[:1000]:
                    stopped = {"node": node_id, "reason": "legacy_result_not_passed"}
                    break
                commands = self._verification(node_id, REPO_ROOT, "adopt-v2")
                if any(command["exit_code"] != 0 for command in commands):
                    stopped = {"node": node_id, "reason": "focused_verification_failed", "commands": commands}
                    break
                outputs = {
                    relative: digest
                    for relative in node["writes"]
                    if (digest := path_digest(REPO_ROOT, relative)) is not None
                }
                missing = self._missing_required_outputs(node_id, outputs)
                if missing:
                    stopped = {"node": node_id, "reason": "required_output_missing", "paths": missing}
                    break
                receipt = self._receipt(
                    node_id=node_id,
                    status="PASSED",
                    outputs=outputs,
                    commands=commands,
                    source="adopted_v2_after_focused_verification",
                    changed_files=[],
                )
                self.receipts.save(receipt)
                adopted.append(node_id)
            if through == node_id:
                break
        return {"adopted": adopted, "stopped": stopped, "status": self.status()}

    def _receipt(
        self,
        node_id: str,
        status: str,
        outputs: dict[str, str],
        commands: list[dict[str, Any]],
        source: str,
        changed_files: list[str],
        findings: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        fingerprint = self.receipts.input_fingerprint_without_recursing(node_id)
        if fingerprint is None:
            raise ControllerError(f"{node_id}: cannot compute input fingerprint")
        return {
            "schema_version": 1,
            "graph_id": self.manifest.data["graph_id"],
            "graph_digest": self.manifest.digest,
            "node_definition_sha256": self.receipts.node_definition_digest(node_id),
            "node_id": node_id,
            "status": status,
            "input_fingerprint": fingerprint,
            "prompt_sha256": sha256_file(REPO_ROOT / self.manifest.nodes[node_id]["prompt"]),
            "outputs": outputs,
            "changed_files": changed_files,
            "commands": commands,
            "findings": findings or [],
            "source": source,
            "created_at": utc_now(),
        }

    def _prompt_packet(self, node_id: str) -> str:
        node = self.manifest.nodes[node_id]
        predecessor_summary = {
            dependency: {
                "status": self.receipts.load(dependency)["status"],
                "receipt": self.receipts.path(dependency).relative_to(REPO_ROOT).as_posix(),
                "outputs": self.receipts.load(dependency)["outputs"],
            }
            for dependency in node["depends_on"]
        }
        prompt = (REPO_ROOT / node["prompt"]).read_text(encoding="utf-8")
        return (
            "You are executing one node of the Plan 26 implementation prompt graph.\n"
            "The production curriculum factory MUST continue to use LangGraph exactly as specified.\n"
            "Do not implement a Python replacement for that production runtime.\n"
            f"Node: {node_id}\n"
            f"Declared writable paths: {json.dumps(node['writes'])}\n"
            f"Compact predecessor state: {json.dumps(predecessor_summary, sort_keys=True)}\n"
            "Do not read historical result Markdown or old evidence unless the node prompt names a specific file needed to diagnose a failure.\n"
            "Complete the node's own TEST/LOOP before returning. The controller independently verifies the focused test command.\n\n"
            "--- BEGIN NODE PROMPT (verbatim) ---\n"
            f"{prompt}"
            "\n--- END NODE PROMPT ---\n"
        )

    def _missing_required_outputs(self, node_id: str, outputs: dict[str, str]) -> list[str]:
        return [
            relative
            for relative in self.manifest.nodes[node_id]["writes"]
            if "/results/evidence/" not in relative and relative not in outputs
        ]

    def _node_reported_status(self, node_id: str, workspace: Path) -> str | None:
        relative = self.manifest.data["result_pattern"].format(node_id=node_id)
        path = workspace / relative
        if not path.is_file():
            return None
        match = re.search(r"(?m)^status:\s*(PASSED|NOT_AVAILABLE|BLOCKED)\s*$", path.read_text(encoding="utf-8"))
        return match.group(1) if match else None

    def _copy_workspace(self, node_id: str) -> tuple[tempfile.TemporaryDirectory[str], Path, dict[str, str]]:
        temporary = tempfile.TemporaryDirectory(prefix=f"plan26-{node_id.lower()}-")
        workspace = Path(temporary.name) / "repo"

        def ignore(directory: str, names: list[str]) -> set[str]:
            ignored_names = {name for name in names if name in EPHEMERAL_NAMES}
            relative = Path(directory).resolve().relative_to(REPO_ROOT.resolve()) if Path(directory).resolve() != REPO_ROOT.resolve() else Path()
            if relative.as_posix().startswith(self.manifest.data["execution"]["state_dir"]):
                ignored_names.update(names)
            return ignored_names

        shutil.copytree(REPO_ROOT, workspace, symlinks=True, ignore=ignore)
        return temporary, workspace, snapshot(workspace)

    def _run_isolated(self, node_id: str) -> dict[str, Any]:
        temporary, workspace, before = self._copy_workspace(node_id)
        try:
            command = list(self.manifest.data["execution"]["claude_command"])
            command.append(self._prompt_packet(node_id))
            attempt = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
            claude_result = run_command(
                command,
                workspace,
                self.manifest.data["execution"]["node_timeout_seconds"],
                self.receipts.root / "logs" / node_id / f"{attempt}.claude.log",
            )
            after = snapshot(workspace)
            changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
            allowed = self.manifest.nodes[node_id]["writes"]
            violations = [path for path in changed if not any(covers(owner, path) for owner in allowed)]
            if violations:
                return {"node_id": node_id, "status": "BLOCKED", "reason": "write_set_violation", "violations": violations, "commands": [claude_result]}
            if claude_result["exit_code"] != 0:
                return {"node_id": node_id, "status": "BLOCKED", "reason": "claude_failed", "commands": [claude_result]}
            reported_status = self._node_reported_status(node_id, workspace)
            allowed_results = self.manifest.nodes[node_id].get("allowed_results", ["PASSED", "BLOCKED"])
            if reported_status not in allowed_results or reported_status == "BLOCKED":
                return {
                    "node_id": node_id,
                    "status": "BLOCKED",
                    "reason": "node_did_not_report_an_admissible_status",
                    "reported_status": reported_status,
                    "commands": [claude_result],
                }
            verification = self._verification(node_id, workspace, attempt)
            if any(command_result["exit_code"] != 0 for command_result in verification):
                return {"node_id": node_id, "status": "BLOCKED", "reason": "verification_failed", "commands": [claude_result, *verification]}
            return {
                "node_id": node_id,
                "status": reported_status,
                "workspace": workspace,
                "temporary": temporary,
                "before": before,
                "after": after,
                "changed": changed,
                "commands": [claude_result, *verification],
            }
        except Exception:
            temporary.cleanup()
            raise

    def _merge(self, result: dict[str, Any]) -> dict[str, Any]:
        node_id = result["node_id"]
        workspace: Path = result["workspace"]
        before: dict[str, str] = result["before"]
        for relative in result["changed"]:
            current = path_digest(REPO_ROOT, relative)
            if current != before.get(relative):
                raise ControllerError(f"{node_id}: main workspace changed concurrently at {relative}")
        for relative in result["changed"]:
            source = workspace / relative
            target = REPO_ROOT / relative
            if source.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            elif target.exists():
                target.unlink()
        outputs = {
            relative: digest
            for relative in self.manifest.nodes[node_id]["writes"]
            if (digest := path_digest(REPO_ROOT, relative)) is not None
        }
        missing = self._missing_required_outputs(node_id, outputs)
        if missing:
            raise ControllerError(f"{node_id}: required outputs missing after merge: {missing}")
        receipt = self._receipt(
            node_id=node_id,
            status=result["status"],
            outputs=outputs,
            commands=result["commands"],
            source="claude_sonnet_isolated_workspace",
            changed_files=result["changed"],
        )
        self.receipts.save(receipt)
        result["temporary"].cleanup()
        return receipt

    def run_generation(self, dry_run: bool = False, only_node: str | None = None) -> dict[str, Any]:
        state = self.status()
        ready = state["ready"]
        if only_node:
            if only_node not in ready:
                raise ControllerError(f"{only_node} is not READY")
            selected = [only_node]
        else:
            selected = self.select_disjoint(ready)
        if dry_run or not selected:
            return {"dry_run": dry_run, "selected": selected, "status": state}

        results: list[dict[str, Any]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(selected)) as pool:
            futures = {pool.submit(self._run_isolated, node_id): node_id for node_id in selected}
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())

        passed: list[str] = []
        blocked: list[dict[str, Any]] = []
        for result in sorted(results, key=lambda item: item["node_id"]):
            if result["status"] == "PASSED":
                self._merge(result)
                passed.append(result["node_id"])
            else:
                blocked.append(result)
        return {"selected": selected, "passed": passed, "blocked": blocked, "status": self.status()}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    subcommands = result.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate")
    subcommands.add_parser("status")
    adopt = subcommands.add_parser("adopt-v2")
    adopt.add_argument("--through")
    run = subcommands.add_parser("run")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--node")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        manifest = Manifest.load(arguments.manifest)
        controller = Controller(manifest)
        if arguments.command == "validate":
            payload = {"valid": True, "graph_digest": manifest.digest, "topological_order": manifest.topological_order()}
        elif arguments.command == "status":
            payload = controller.status()
        elif arguments.command == "adopt-v2":
            payload = controller.adopt_v2(arguments.through)
        else:
            payload = controller.run_generation(dry_run=arguments.dry_run, only_node=arguments.node)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except (ControllerError, jsonschema.ValidationError, yaml.YAMLError, OSError) as exc:
        print(json.dumps({"error": type(exc).__name__, "message": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
