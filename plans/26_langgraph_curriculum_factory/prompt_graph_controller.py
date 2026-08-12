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
import signal
import shutil
import subprocess
import sys
import threading
import time
import uuid
from typing import Any, Callable, Iterable, Sequence

import jsonschema
import yaml


PLAN_DIR = Path(__file__).resolve().parent
REPO_ROOT = PLAN_DIR.parents[1]
DEFAULT_MANIFEST = PLAN_DIR / "implementation.graph.v3.yaml"
EPHEMERAL_NAMES = {".DS_Store", ".git", ".plan26-run", ".pytest_cache", "__pycache__"}
EPHEMERAL_SUFFIXES = {".pyc", ".pyo"}
ACTIVE_PROCESSES: set[subprocess.Popen[Any]] = set()
ACTIVE_PROCESSES_LOCK = threading.Lock()


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


def canonical_digest(value: Any) -> str:
    return sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def new_id(prefix: str) -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:10]}"


def write_new_text(path: Path, text: str) -> None:
    """Create an immutable artifact and fail rather than overwrite it."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(text)


def write_new_json(path: Path, value: Any) -> None:
    write_new_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def display_path(path: Path, root: Path | None = None) -> str:
    base = REPO_ROOT if root is None else root
    return path.relative_to(base).as_posix() if path.is_relative_to(base) else str(path)


class EventLog:
    """Append-only JSONL audit trail safe for concurrent scheduler threads."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, event: str, **fields: Any) -> dict[str, Any]:
        record = {
            "schema_version": 1,
            "event_id": new_id("event"),
            "occurred_at": utc_now(),
            "event": event,
            **fields,
        }
        payload = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
        try:
            os.write(descriptor, payload)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return record


def terminate_active_processes(signum: int, _frame: Any) -> None:
    """Do not orphan nested Claude/test processes when the controller stops."""

    with ACTIVE_PROCESSES_LOCK:
        processes = list(ACTIVE_PROCESSES)
    for process in processes:
        if process.poll() is not None:
            continue
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and any(process.poll() is None for process in processes):
        time.sleep(0.05)
    for process in processes:
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    raise SystemExit(128 + signum)


def ignored(relative: Path) -> bool:
    return any(part in EPHEMERAL_NAMES for part in relative.parts) or relative.suffix in EPHEMERAL_SUFFIXES


def copytree_ignore_for_sandbox(manifest: "Manifest") -> Callable[[str, list[str]], set[str]]:
    """Copytree ignore callback for a fresh, isolated node sandbox.

    Excludes ephemeral harness bookkeeping (.plan26-run, __pycache__, etc.)
    everywhere. Within the receipt state directory itself, keeps only the
    top-level *.receipt.v1.json files and excludes everything else (logs,
    the audit event log, receipt history, and — in configurations where
    attempt_dir is nested under state_dir — the attempt tree itself, which
    must never be copied into a sandbox it may itself be part of). The
    receipt files are the controller's actual admitted state — run.prompt
    describes every sandbox as an isolated copy of "the current dirty
    baseline", and those receipts are part of that baseline — so they are
    kept, meaning Controller methods like status()/receipts.load() behave
    the same way when a node's own verification runs them from inside a
    sandbox as they do against the live repo. An allowlist (keep only
    receipt files) rather than a denylist of known bulky subdirectory names
    is deliberate: it stays correct regardless of what else state_dir holds
    or how attempt_dir is configured relative to it.
    """
    state_dir = manifest.data["execution"]["state_dir"]

    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored_names = {name for name in names if name in EPHEMERAL_NAMES}
        directory_path = Path(directory).resolve()
        relative = (
            directory_path.relative_to(REPO_ROOT.resolve())
            if directory_path != REPO_ROOT.resolve()
            else Path()
        )
        if relative.as_posix() == state_dir:
            ignored_names.update(name for name in names if not name.endswith(".receipt.v1.json"))
        return ignored_names

    return ignore


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


def expand_placeholders(argv: Sequence[str], python_exe: str) -> list[str]:
    """Resolve the Plan 26 interpreter once and substitute it anywhere it
    appears inside any argument, including inside a combined tool-policy
    string such as ``Bash({python} -m pytest *)``."""

    return [value.replace("{python}", python_exe) for value in argv]


def run_command(
    argv: Sequence[str],
    cwd: Path,
    timeout: int,
    log_path: Path,
    event_log: EventLog | None = None,
    event_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    started = utc_now()
    fields = event_fields or {}
    log_path.parent.mkdir(parents=True, exist_ok=True)
    command_digest = canonical_digest(list(argv))
    if event_log:
        event_log.append(
            "command_started",
            command_sha256=command_digest,
            executable=argv[0],
            cwd=str(cwd),
            log=str(log_path),
            **fields,
        )
    try:
        with log_path.open("xb") as log_handle:
            process = subprocess.Popen(
                list(argv),
                cwd=cwd,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            with ACTIVE_PROCESSES_LOCK:
                ACTIVE_PROCESSES.add(process)
            try:
                process.wait(timeout=timeout)
                exit_code = process.returncode
                timed_out = False
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                log_handle.write(b"\nTIMEOUT\n")
                log_handle.flush()
                os.fsync(log_handle.fileno())
                exit_code = 124
                timed_out = True
            finally:
                with ACTIVE_PROCESSES_LOCK:
                    ACTIVE_PROCESSES.discard(process)
    except Exception:
        if event_log:
            event_log.append(
                "command_exception",
                command_sha256=command_digest,
                log=str(log_path),
                **fields,
            )
        raise
    output = log_path.read_text(encoding="utf-8", errors="replace")
    result = {
        "argv": list(argv),
        "started_at": started,
        "finished_at": utc_now(),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "log": log_path.relative_to(cwd).as_posix() if log_path.is_relative_to(cwd) else str(log_path),
        "log_sha256": sha256_file(log_path),
        "tail": output[-4000:],
    }
    if event_log:
        event_log.append(
            "command_finished",
            command_sha256=command_digest,
            exit_code=exit_code,
            timed_out=timed_out,
            log=str(log_path),
            log_sha256=result["log_sha256"],
            **fields,
        )
    return result


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


@dataclasses.dataclass(frozen=True)
class PatchRecord:
    path: Path
    data: dict[str, Any]
    digest: str


class PatchStore:
    """Load immutable prompt/context overlays and append-only revocations."""

    def __init__(self, manifest: Manifest) -> None:
        self.manifest = manifest
        execution = manifest.data["execution"]
        self.root = REPO_ROOT / execution["patch_dir"]
        self.schema_path = REPO_ROOT / execution["patch_schema"]
        self._cache: list[PatchRecord] | None = None

    def load(self) -> list[PatchRecord]:
        if self._cache is not None:
            return list(self._cache)
        if not self.root.exists():
            self._cache = []
            return []
        schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        records: list[PatchRecord] = []
        for path in sorted(self.root.glob("*.patch.v1.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator(schema).validate(data)
            if data["graph_id"] != self.manifest.data["graph_id"]:
                raise ControllerError(f"{path}: patch graph_id does not match")
            # base_graph_digest is provenance for which graph state the patch
            # author reviewed, not a functional gate: it is a whole-file hash,
            # so any edit anywhere in the graph (e.g. extending an unrelated
            # node's write set) would otherwise orphan every existing patch,
            # including ones whose target node never changed. Applicability to
            # a specific node is what actually matters, and that is enforced
            # separately in _affected_nodes (unknown target_node raises) and by
            # the node_definition digest feeding every admissibility check.
            records.append(PatchRecord(path=path, data=data, digest=sha256_file(path)))
        records.sort(key=lambda record: (record.data["created_at"], record.data["patch_id"]))
        ids = [record.data["patch_id"] for record in records]
        if len(ids) != len(set(ids)):
            raise ControllerError("duplicate patch_id in patch store")
        known: set[str] = set()
        for record in records:
            if record.data["action"] == "revoke":
                unknown = set(record.data["supersedes"]) - known
                if unknown:
                    raise ControllerError(
                        f"{record.data['patch_id']}: revokes unknown or later patches {sorted(unknown)}"
                    )
            known.add(record.data["patch_id"])
        self._cache = records
        return list(records)

    def _affected_nodes(self, record: PatchRecord) -> set[str]:
        target = record.data.get("target_node")
        if not target:
            return set()
        if target not in self.manifest.nodes:
            raise ControllerError(f"{record.data['patch_id']}: unknown target_node {target}")
        affected = {target}
        if record.data.get("scope") == "node_and_descendants":
            affected.update(self.manifest.descendants(target))
        return affected

    def chain_for_node(self, node_id: str) -> tuple[list[PatchRecord], list[PatchRecord]]:
        records = self.load()
        overlays = {record.data["patch_id"]: record for record in records if record.data["action"] == "overlay"}
        relevant_ids = {
            patch_id for patch_id, record in overlays.items() if node_id in self._affected_nodes(record)
        }
        revoked: set[str] = set()
        chain: list[PatchRecord] = []
        for record in records:
            if record.data["action"] == "overlay" and record.data["patch_id"] in relevant_ids:
                chain.append(record)
            elif record.data["action"] == "revoke":
                impacted = set(record.data["supersedes"]) & relevant_ids
                if impacted:
                    revoked.update(impacted)
                    chain.append(record)
        active = [
            record
            for record in chain
            if record.data["action"] == "overlay" and record.data["patch_id"] not in revoked
        ]
        return chain, active

    def chain_digest(self, node_id: str) -> str:
        chain, _active = self.chain_for_node(node_id)
        return canonical_digest(
            [{"patch_id": record.data["patch_id"], "sha256": record.digest} for record in chain]
        )

    def effective_prompt(self, node_id: str) -> tuple[str, dict[str, Any]]:
        base_path = REPO_ROOT / self.manifest.nodes[node_id]["prompt"]
        base = base_path.read_text(encoding="utf-8")
        chain, active = self.chain_for_node(node_id)
        sections = [base]
        for record in active:
            data = record.data
            sections.extend(
                [
                    "\n\n--- BEGIN APPROVED IMMUTABLE PATCH OVERLAY ---\n",
                    f"Patch ID: {data['patch_id']}\n",
                    f"Reason: {data['reason']}\n",
                    f"Expected effect: {data['expected_effect']}\n",
                    f"Instructions:\n{data['instructions'].rstrip()}\n",
                    "--- END APPROVED IMMUTABLE PATCH OVERLAY ---\n",
                ]
            )
            if data.get("context"):
                sections.extend(
                    [
                        "Patch context (JSON):\n",
                        json.dumps(data["context"], indent=2, sort_keys=True),
                        "\n",
                    ]
                )
        prompt = "".join(sections)
        provenance = {
            "base_prompt_sha256": sha256_file(base_path),
            "effective_prompt_sha256": sha256_bytes(prompt.encode()),
            "patch_chain_sha256": self.chain_digest(node_id),
            "patch_ids": [record.data["patch_id"] for record in chain],
            "active_patch_ids": [record.data["patch_id"] for record in active],
        }
        return prompt, provenance

    def status(self) -> dict[str, Any]:
        records = self.load()
        return {
            "patch_dir": display_path(self.root),
            "records": [
                {
                    "patch_id": record.data["patch_id"],
                    "action": record.data["action"],
                    "target_node": record.data.get("target_node"),
                    "sha256": record.digest,
                }
                for record in records
            ],
        }

    def create_overlay(
        self,
        patch_id: str,
        target_node: str,
        instructions: str,
        reason: str,
        expected_effect: str,
        scope: str,
        context: dict[str, Any] | None,
        dry_run: bool,
    ) -> dict[str, Any]:
        if target_node not in self.manifest.nodes:
            raise ControllerError(f"unknown target node: {target_node}")
        record = {
            "schema_version": 1,
            "patch_id": patch_id,
            "action": "overlay",
            "graph_id": self.manifest.data["graph_id"],
            "base_graph_digest": self.manifest.digest,
            "target_node": target_node,
            "scope": scope,
            "reason": reason,
            "expected_effect": expected_effect,
            "instructions": instructions,
            "context": context or {},
            "created_at": utc_now(),
        }
        schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(record)
        target = self.root / f"{patch_id}.patch.v1.yaml"
        affected = sorted(self._affected_nodes(PatchRecord(target, record, canonical_digest(record))))
        payload = {"path": display_path(target), "record": record, "affected_nodes": affected}
        if not dry_run:
            self.root.mkdir(parents=True, exist_ok=True)
            with target.open("x", encoding="utf-8") as handle:
                yaml.safe_dump(record, handle, sort_keys=False)
            self._cache = None
            payload["sha256"] = sha256_file(target)
        return payload

    def revoke(
        self,
        patch_id: str,
        supersedes: list[str],
        reason: str,
        expected_effect: str,
        dry_run: bool,
    ) -> dict[str, Any]:
        known = {record.data["patch_id"]: record for record in self.load()}
        unknown = set(supersedes) - set(known)
        if unknown:
            raise ControllerError(f"cannot revoke unknown patches: {sorted(unknown)}")
        if any(known[value].data["action"] != "overlay" for value in supersedes):
            raise ControllerError("a revocation may supersede overlay patches only")
        record = {
            "schema_version": 1,
            "patch_id": patch_id,
            "action": "revoke",
            "graph_id": self.manifest.data["graph_id"],
            "base_graph_digest": self.manifest.digest,
            "supersedes": supersedes,
            "reason": reason,
            "expected_effect": expected_effect,
            "created_at": utc_now(),
        }
        schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(record)
        target = self.root / f"{patch_id}.patch.v1.yaml"
        payload = {"path": display_path(target), "record": record}
        if not dry_run:
            self.root.mkdir(parents=True, exist_ok=True)
            with target.open("x", encoding="utf-8") as handle:
                yaml.safe_dump(record, handle, sort_keys=False)
            self._cache = None
            payload["sha256"] = sha256_file(target)
        return payload


class ReceiptStore:
    def __init__(self, manifest: Manifest, patches: PatchStore) -> None:
        self.manifest = manifest
        self.patches = patches
        self.root = manifest.state_dir
        self.root.mkdir(parents=True, exist_ok=True)
        self._digest_cache: dict[str, str | None] = {}

    def clear_digest_cache(self) -> None:
        self._digest_cache.clear()

    def current_digest(self, relative: str) -> str | None:
        if relative not in self._digest_cache:
            self._digest_cache[relative] = path_digest(REPO_ROOT, relative)
        return self._digest_cache[relative]

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
        serialized = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        if target.is_file():
            existing = target.read_bytes()
            if existing == serialized.encode():
                return
            history = self.root / "receipt_history" / receipt["node_id"]
            archive = history / f"{sha256_bytes(existing)}.receipt.v1.json"
            if not archive.exists():
                write_new_text(archive, existing.decode("utf-8"))
        temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
        write_new_text(temporary, serialized)
        os.replace(temporary, target)
        self.clear_digest_cache()

    def node_definition_digest(self, node_id: str) -> str:
        payload = {
            "node_id": node_id,
            "definition": self.manifest.nodes[node_id],
            "rules": self.manifest.data["rules"],
        }
        chain, _active = self.patches.chain_for_node(node_id)
        if chain:
            payload["patch_chain_sha256"] = self.patches.chain_digest(node_id)
        return canonical_digest(payload)

    def input_fingerprint(self, node_id: str) -> str | None:
        node = self.manifest.nodes[node_id]
        predecessors: dict[str, str] = {}
        for predecessor in node["depends_on"]:
            receipt = self.admissible(predecessor)
            if receipt is None:
                return None
            predecessors[predecessor] = sha256_file(self.path(predecessor))
        environment = {
            path: self.current_digest(path)
            for path in self.manifest.data["execution"]["cache"]["environment_files"]
        }
        _prompt, prompt_provenance = self.patches.effective_prompt(node_id)
        payload = {
            "node": node_id,
            "node_definition": self.node_definition_digest(node_id),
            "prompt": prompt_provenance["effective_prompt_sha256"],
            "source_spec": sha256_file(REPO_ROOT / self.manifest.data["source_spec"]),
            "predecessors": predecessors,
            "environment": environment,
        }
        return canonical_digest(payload)

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
        if fingerprint is None:
            return None
        if receipt.get("input_fingerprint") != fingerprint and not self.mechanically_revalidate(node_id, receipt):
            return None
        for relative, expected in receipt.get("outputs", {}).items():
            if self.current_digest(relative) != expected:
                return None
        return receipt

    def mechanically_revalidate(self, node_id: str, receipt: dict[str, Any]) -> bool:
        """Admit a receipt whose input_fingerprint no longer matches solely
        because permission-launcher/harness code changed, by checking the
        node-correctness-relevant facts directly instead of rerunning Claude:
        schema validity, recorded zero exits, current output hashes, and
        predecessor admissibility."""

        schema_path = REPO_ROOT / self.manifest.data["execution"]["receipt_schema"]
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        try:
            jsonschema.Draft202012Validator(schema).validate(receipt)
        except jsonschema.ValidationError:
            return False
        node = self.manifest.nodes[node_id]
        _prompt, prompt_provenance = self.patches.effective_prompt(node_id)
        if receipt.get("prompt_sha256") != prompt_provenance["effective_prompt_sha256"]:
            return False
        commands = receipt.get("commands") or []
        if any(command.get("exit_code") != 0 for command in commands):
            return False
        for relative, expected in receipt.get("outputs", {}).items():
            if self.current_digest(relative) != expected:
                return False
        return all(self.admissible(predecessor) is not None for predecessor in node["depends_on"])

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
                if self.current_digest(relative) != expected:
                    return None
            predecessors[predecessor] = sha256_file(self.path(predecessor))
        environment = {
            path: self.current_digest(path)
            for path in self.manifest.data["execution"]["cache"]["environment_files"]
        }
        _prompt, prompt_provenance = self.patches.effective_prompt(node_id)
        payload = {
            "node": node_id,
            "node_definition": self.node_definition_digest(node_id),
            "prompt": prompt_provenance["effective_prompt_sha256"],
            "source_spec": sha256_file(REPO_ROOT / self.manifest.data["source_spec"]),
            "predecessors": predecessors,
            "environment": environment,
        }
        return canonical_digest(payload)


@dataclasses.dataclass
class AttemptBranch:
    attempt_id: str
    node_id: str
    root: Path
    workspace: Path
    base: dict[str, str]
    start: dict[str, str]
    parent_attempt_id: str | None
    branch_id: str


class Controller:
    def __init__(self, manifest: Manifest) -> None:
        self.manifest = manifest
        self.patches = PatchStore(manifest)
        self.receipts = ReceiptStore(manifest, self.patches)
        execution = manifest.data["execution"]
        self.attempt_root = REPO_ROOT / execution["attempt_dir"]
        self.events = EventLog(REPO_ROOT / execution["audit_log"])
        self.run_id = new_id("run")

    def status(self) -> dict[str, Any]:
        self.receipts.clear_digest_cache()
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
            "harness_digest": self.harness_digest(),
            "statuses": statuses,
            "stale_receipts": stale,
            "ready": ready,
            "selected": self.select_disjoint(ready),
            "patches": self.patches.status(),
        }

    def harness_digest(self) -> str:
        """Digest of the launcher/scheduler code and schemas, recorded for
        audit only. It intentionally does not gate node admissibility: see
        ReceiptStore.mechanically_revalidate."""

        paths = [
            self.manifest.data["execution"]["controller"],
            self.manifest.data["schema"],
            self.manifest.data["execution"]["receipt_schema"],
            self.manifest.data["execution"]["patch_schema"],
        ]
        digest = hashlib.sha256()
        for relative in paths:
            digest.update(relative.encode())
            digest.update(b"\0")
            digest.update(sha256_file(REPO_ROOT / relative).encode())
            digest.update(b"\n")
        return digest.hexdigest()

    def predecessor_checkpoint(self, node_id: str) -> dict[str, str]:
        checkpoint: dict[str, str] = {}
        for dependency in self.manifest.nodes[node_id]["depends_on"]:
            path = self.receipts.path(dependency)
            if not path.is_file() or self.receipts.admissible(dependency) is None:
                raise ControllerError(f"{node_id}: predecessor {dependency} is not admissible")
            checkpoint[dependency] = sha256_file(path)
        return checkpoint

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

    def _verification(
        self, node_id: str, cwd: Path, attempt: str, resolved_python: str
    ) -> list[dict[str, Any]]:
        commands: list[dict[str, Any]] = []
        timeout = self.manifest.data["execution"]["test_timeout_seconds"]
        log_root = self.receipts.root / "logs" / node_id
        for index, argv in enumerate(self.manifest.nodes[node_id].get("verification", []), start=1):
            resolved_argv = expand_placeholders(argv, resolved_python)
            result = run_command(
                resolved_argv,
                cwd,
                timeout,
                log_root / f"{attempt}.test{index}.log",
                self.events,
                {
                    "run_id": self.run_id,
                    "attempt_id": attempt,
                    "node_id": node_id,
                    "stage": f"verification_{index}",
                },
            )
            commands.append(result)
            if result["exit_code"] != 0:
                break
        return commands

    def adopt_v2(self, through: str | None = None) -> dict[str, Any]:
        resolved_python = self.python_executable()
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
                commands = self._verification(node_id, REPO_ROOT, "adopt-v2", resolved_python)
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

    def rebase(self, node_id: str, attempt_id: str, dry_run: bool) -> dict[str, Any]:
        """Mechanically re-admit a retained attempt's own in-scope work after
        an upstream predecessor was legitimately invalidated and reworked
        (e.g. an ownership correction), without re-invoking Claude and
        without regenerating the retained work. Builds a fresh workspace from
        the current (post-rework) baseline, overlays only the retained
        attempt's own declared-write-set files on top, and re-runs the node's
        real verification commands against that combined state in isolation.
        Admission depends solely on that verification passing against the
        current baseline, not on any hash bookkeeping carried over from the
        original attempt — the same trust model as adopt_v2, applied to a
        predecessor rework instead of a v2-to-v3 migration. Nothing is merged
        into the live repo, and no receipt is saved, unless verification
        passes; a dry run stops before that, after validating preconditions.
        """
        node = self.manifest.nodes[node_id]
        if any(self.receipts.admissible(dependency) is None for dependency in node["depends_on"]):
            return {"node_id": node_id, "status": "BLOCKED", "reason": "predecessor_not_admissible"}
        attempt_root = self._find_attempt(node_id, attempt_id)
        attempt_metadata = json.loads((attempt_root / "attempt.json").read_text(encoding="utf-8"))
        if attempt_metadata.get("node_id") != node_id:
            raise ControllerError(f"{attempt_id}: retained attempt belongs to another node")
        _prompt, prompt_provenance = self.patches.effective_prompt(node_id)
        attempt_prompt_sha256 = attempt_metadata.get("patch_provenance", {}).get("effective_prompt_sha256")
        if attempt_prompt_sha256 != prompt_provenance["effective_prompt_sha256"]:
            raise ControllerError(f"{node_id}: prompt/patch chain changed since {attempt_id}; rebase no longer applies")
        attempt_workspace = attempt_root / "repo"
        reported_status = self._node_reported_status(node_id, attempt_workspace)
        allowed_results = node.get("allowed_results", ["PASSED", "BLOCKED"])
        if reported_status not in allowed_results or reported_status == "BLOCKED":
            raise ControllerError(f"{attempt_id}: retained attempt did not report an admissible status")
        if dry_run:
            return {
                "dry_run": True,
                "node_id": node_id,
                "attempt_id": attempt_id,
                "reported_status": reported_status,
                "status": self.status(),
            }

        resolved_python = self.python_executable()
        branch_id = new_id("rebase")
        root = self.attempt_root / node_id / branch_id
        root.mkdir(parents=True, exist_ok=False)
        workspace = root / "repo"

        shutil.copytree(
            REPO_ROOT, workspace, symlinks=True, ignore=copytree_ignore_for_sandbox(self.manifest)
        )
        base = snapshot(workspace)
        write_new_json(root / "base.snapshot.json", base)

        allowed = node["writes"]
        overlaid: list[str] = []
        for path in sorted(attempt_workspace.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(attempt_workspace)
            if ".git" in relative.parts or ignored(relative):
                continue
            relative_posix = relative.as_posix()
            if not any(covers(owner, relative_posix) for owner in allowed):
                continue
            target = workspace / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            overlaid.append(relative_posix)

        after = snapshot(workspace)
        write_new_json(root / "final.snapshot.json", after)
        changed = sorted(path for path in set(base) | set(after) if base.get(path) != after.get(path))
        violations = [path for path in changed if not any(covers(owner, path) for owner in allowed)]
        if violations:
            raise ControllerError(f"{node_id}: rebase overlay touched paths outside the declared write set: {violations}")

        verification = self._verification(node_id, workspace, branch_id, resolved_python)
        write_new_json(
            root / "verification_outcome.json",
            {
                "attempt_id": branch_id,
                "node_id": node_id,
                "source_attempt_id": attempt_id,
                "overlaid_files": overlaid,
                "commands": verification,
            },
        )
        self.events.append(
            "node_rebase_attempted",
            run_id=self.run_id,
            node_id=node_id,
            source_attempt_id=attempt_id,
            branch_id=branch_id,
            overlaid_files=overlaid,
        )
        if any(command["exit_code"] != 0 for command in verification):
            return {
                "node_id": node_id,
                "status": "BLOCKED",
                "reason": "verification_failed",
                "commands": verification,
                "branch_id": branch_id,
                "workspace": str(workspace),
            }

        for relative_path in changed:
            source = workspace / relative_path
            target = REPO_ROOT / relative_path
            if source.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            elif target.exists():
                target.unlink()

        outputs = {
            relative: digest
            for relative in node["writes"]
            if (digest := path_digest(REPO_ROOT, relative)) is not None
        }
        missing = self._missing_required_outputs(node_id, outputs)
        if missing:
            raise ControllerError(f"{node_id}: rebase merged state is missing required outputs: {missing}")

        receipt = self._receipt(
            node_id=node_id,
            status=reported_status,
            outputs=outputs,
            commands=verification,
            source=f"rebased_from_{attempt_id}_after_predecessor_rework",
            changed_files=changed,
            attempt_id=branch_id,
            branch_id=branch_id,
        )
        self.receipts.save(receipt)
        self.events.append(
            "node_rebased",
            run_id=self.run_id,
            node_id=node_id,
            source_attempt_id=attempt_id,
            branch_id=branch_id,
            changed_files=changed,
            status=receipt["status"],
        )
        return {
            "node_id": node_id,
            "status": receipt["status"],
            "branch_id": branch_id,
            "source_attempt_id": attempt_id,
            "changed_files": changed,
            "commands": verification,
            "status_after": self.status(),
        }

    def _receipt(
        self,
        node_id: str,
        status: str,
        outputs: dict[str, str],
        commands: list[dict[str, Any]],
        source: str,
        changed_files: list[str],
        findings: list[dict[str, str]] | None = None,
        attempt_id: str | None = None,
        branch_id: str | None = None,
        checkpoint: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        fingerprint = self.receipts.input_fingerprint_without_recursing(node_id)
        if fingerprint is None:
            raise ControllerError(f"{node_id}: cannot compute input fingerprint")
        _prompt, prompt_provenance = self.patches.effective_prompt(node_id)
        return {
            "schema_version": 1,
            "graph_id": self.manifest.data["graph_id"],
            "graph_digest": self.manifest.digest,
            "node_definition_sha256": self.receipts.node_definition_digest(node_id),
            "node_id": node_id,
            "status": status,
            "input_fingerprint": fingerprint,
            "prompt_sha256": prompt_provenance["effective_prompt_sha256"],
            "outputs": outputs,
            "changed_files": changed_files,
            "commands": commands,
            "findings": findings or [],
            "source": source,
            "created_at": utc_now(),
            "provenance": {
                "base_graph_digest": self.manifest.digest,
                "harness_digest": self.harness_digest(),
                **prompt_provenance,
                "attempt_id": attempt_id,
                "branch_id": branch_id,
                "checkpoint": checkpoint or self.predecessor_checkpoint(node_id),
            },
        }

    def _prompt_packet(self, node_id: str, resolved_python: str) -> str:
        node = self.manifest.nodes[node_id]
        predecessor_summary = {
            dependency: {
                "status": self.receipts.load(dependency)["status"],
                "receipt": self.receipts.path(dependency).relative_to(REPO_ROOT).as_posix(),
                "outputs": self.receipts.load(dependency)["outputs"],
            }
            for dependency in node["depends_on"]
        }
        prompt, prompt_provenance = self.patches.effective_prompt(node_id)
        return (
            "You are executing one node of the Plan 26 implementation prompt graph.\n"
            "The production curriculum factory MUST continue to use LangGraph exactly as specified.\n"
            "Do not implement a Python replacement for that production runtime.\n"
            f"Run every pytest command as {resolved_python} -m pytest ...; "
            "never use python3, python, or plain pytest.\n"
            f"Node: {node_id}\n"
            f"Patch provenance: {json.dumps(prompt_provenance, sort_keys=True)}\n"
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

    def _find_attempt(self, node_id: str, attempt_id: str) -> Path:
        path = self.attempt_root / node_id / attempt_id
        if not path.is_dir():
            raise ControllerError(f"{node_id}: retained attempt does not exist: {attempt_id}")
        return path

    def _heal_out_of_scope_contamination(
        self, node_id: str, workspace: Path, base: dict[str, str]
    ) -> None:
        """Silently revert any file outside the node's declared write set back
        to its base content, when the live repo still has that exact base
        content to restore from.

        Two situations produce this kind of out-of-scope drift without the
        agent (or a resumed parent attempt) ever intending to touch the file:
        an unrelated pre-existing test elsewhere in the required suite that
        rewrites a fixed-path evidence file with non-deterministic content
        merely by being executed, and a resumed branch's workspace starting
        as a copy of its parent's already-dirty final tree. An LLM agent
        cannot reliably reproduce such a file byte-for-byte from a patch
        instruction (whitespace and other incidental differences creep in),
        so this restores from REPO_ROOT deterministically instead — but only
        when REPO_ROOT's content still matches the recorded base exactly, so
        a genuine, intentional divergence in the live repo is never silently
        papered over. Called both before the agent's turn (to undo
        contamination inherited from a resumed parent) and after it (to undo
        side effects the agent's own verification runs produced), so the
        write-set violation gate only ever fires for changes actually inside
        the node's own scope.
        """
        allowed = self.manifest.nodes[node_id]["writes"] if node_id in self.manifest.nodes else []
        current = snapshot(workspace)
        for path in sorted(set(base) | set(current)):
            if base.get(path) == current.get(path):
                continue
            if any(covers(owner, path) for owner in allowed):
                continue
            target = workspace / path
            if base.get(path) is None:
                if target.exists():
                    target.unlink()
                continue
            source = REPO_ROOT / path
            if source.is_file() and sha256_file(source) == base[path]:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

    def _copy_workspace(self, node_id: str, parent_attempt_id: str | None = None) -> AttemptBranch:
        attempt_id = new_id("attempt")
        root = self.attempt_root / node_id / attempt_id
        root.mkdir(parents=True, exist_ok=False)
        workspace = root / "repo"
        checkpoint = self.predecessor_checkpoint(node_id) if node_id in self.manifest.nodes else {}

        if parent_attempt_id:
            parent = self._find_attempt(node_id, parent_attempt_id)
            parent_metadata = json.loads((parent / "attempt.json").read_text(encoding="utf-8"))
            if parent_metadata.get("node_id") != node_id:
                raise ControllerError(f"{parent_attempt_id}: retained attempt belongs to another node")
            if parent_metadata.get("graph_digest") != self.manifest.digest:
                raise ControllerError(
                    f"{node_id}: graph version changed since {parent_attempt_id}; start a clean branch"
                )
            if parent_metadata.get("checkpoint") != checkpoint:
                raise ControllerError(
                    f"{node_id}: predecessor checkpoint changed since {parent_attempt_id}; start a clean branch"
                )
            shutil.copytree(parent / "repo", workspace, symlinks=True)
            base = json.loads((parent / "base.snapshot.json").read_text(encoding="utf-8"))
            self._heal_out_of_scope_contamination(node_id, workspace, base)
        else:
            shutil.copytree(
                REPO_ROOT, workspace, symlinks=True, ignore=copytree_ignore_for_sandbox(self.manifest)
            )
            base = snapshot(workspace)
        start = snapshot(workspace)
        patch_provenance: dict[str, Any] = {}
        if node_id in self.manifest.nodes:
            _prompt, patch_provenance = self.patches.effective_prompt(node_id)
        branch_id = canonical_digest(
            {
                "node_id": node_id,
                "parent_attempt_id": parent_attempt_id,
                "checkpoint": checkpoint,
                "base_graph_digest": self.manifest.digest,
                "patch_chain_sha256": patch_provenance.get("patch_chain_sha256"),
            }
        )
        write_new_json(root / "base.snapshot.json", base)
        write_new_json(root / "start.snapshot.json", start)
        write_new_json(
            root / "attempt.json",
            {
                "schema_version": 1,
                "attempt_id": attempt_id,
                "node_id": node_id,
                "run_id": self.run_id,
                "branch_id": branch_id,
                "parent_attempt_id": parent_attempt_id,
                "created_at": utc_now(),
                "graph_digest": self.manifest.digest,
                "harness_digest": self.harness_digest(),
                "checkpoint": checkpoint,
                "patch_provenance": patch_provenance,
                "workspace": str(workspace),
                "base_snapshot_sha256": canonical_digest(base),
                "start_snapshot_sha256": canonical_digest(start),
            },
        )
        branch = AttemptBranch(
            attempt_id=attempt_id,
            node_id=node_id,
            root=root,
            workspace=workspace,
            base=base,
            start=start,
            parent_attempt_id=parent_attempt_id,
            branch_id=branch_id,
        )
        self.events.append(
            "attempt_created",
            run_id=self.run_id,
            attempt_id=attempt_id,
            node_id=node_id,
            branch_id=branch_id,
            parent_attempt_id=parent_attempt_id,
            checkpoint=checkpoint,
            attempt_path=str(root),
        )
        return branch

    def _write_attempt_outcome(self, branch: AttemptBranch, name: str, payload: dict[str, Any]) -> None:
        write_new_json(branch.root / name, payload)
        self.events.append(
            "attempt_outcome",
            run_id=self.run_id,
            attempt_id=branch.attempt_id,
            node_id=branch.node_id,
            branch_id=branch.branch_id,
            outcome_file=name,
            status=payload.get("status"),
            reason=payload.get("reason"),
        )

    def _blocked_result(
        self, branch: AttemptBranch, reason: str, commands: list[dict[str, Any]], **fields: Any
    ) -> dict[str, Any]:
        payload = {
            "attempt_id": branch.attempt_id,
            "node_id": branch.node_id,
            "branch_id": branch.branch_id,
            "status": "BLOCKED",
            "reason": reason,
            "commands": commands,
            **fields,
        }
        self._write_attempt_outcome(branch, "verification_outcome.json", payload)
        return payload

    def _run_isolated(self, node_id: str, parent_attempt_id: str | None = None) -> dict[str, Any]:
        resolved_python = self.python_executable()
        branch = self._copy_workspace(node_id, parent_attempt_id)
        workspace = branch.workspace
        try:
            packet = self._prompt_packet(node_id, resolved_python)
            write_new_text(branch.root / "effective_prompt.txt", packet)
            command = expand_placeholders(
                list(self.manifest.data["execution"]["claude_command"]), resolved_python
            )
            command.append(packet)
            attempt = branch.attempt_id
            claude_result = run_command(
                command,
                workspace,
                self.manifest.data["execution"]["node_timeout_seconds"],
                self.receipts.root / "logs" / node_id / f"{attempt}.claude.log",
                self.events,
                {
                    "run_id": self.run_id,
                    "attempt_id": attempt,
                    "node_id": node_id,
                    "stage": "claude_generation",
                },
            )
            self._heal_out_of_scope_contamination(node_id, workspace, branch.base)
            after = snapshot(workspace)
            write_new_json(branch.root / "final.snapshot.json", after)
            changed = sorted(path for path in set(branch.base) | set(after) if branch.base.get(path) != after.get(path))
            write_new_json(
                branch.root / "delta.json",
                {
                    "changed_files": changed,
                    "base_snapshot_sha256": canonical_digest(branch.base),
                    "final_snapshot_sha256": canonical_digest(after),
                },
            )
            allowed = self.manifest.nodes[node_id]["writes"]
            violations = [path for path in changed if not any(covers(owner, path) for owner in allowed)]
            if violations:
                return self._blocked_result(branch, "write_set_violation", [claude_result], violations=violations)
            if claude_result["exit_code"] != 0:
                return self._blocked_result(branch, "claude_failed", [claude_result])
            reported_status = self._node_reported_status(node_id, workspace)
            allowed_results = self.manifest.nodes[node_id].get("allowed_results", ["PASSED", "BLOCKED"])
            if reported_status not in allowed_results or reported_status == "BLOCKED":
                return self._blocked_result(
                    branch,
                    "node_did_not_report_an_admissible_status",
                    [claude_result],
                    reported_status=reported_status,
                )
            verification = self._verification(node_id, workspace, attempt, resolved_python)
            if any(command_result["exit_code"] != 0 for command_result in verification):
                return self._blocked_result(branch, "verification_failed", [claude_result, *verification])
            result = {
                "node_id": node_id,
                "status": reported_status,
                "branch": branch,
                "after": after,
                "changed": changed,
                "commands": [claude_result, *verification],
            }
            self._write_attempt_outcome(
                branch,
                "verification_outcome.json",
                {
                    "attempt_id": attempt,
                    "node_id": node_id,
                    "branch_id": branch.branch_id,
                    "status": reported_status,
                    "changed_files": changed,
                    "commands": result["commands"],
                },
            )
            return result
        except BaseException as exc:
            write_new_json(
                branch.root / "exception.json",
                {
                    "attempt_id": branch.attempt_id,
                    "node_id": node_id,
                    "exception_type": type(exc).__name__,
                    "message": str(exc),
                    "occurred_at": utc_now(),
                },
            )
            self.events.append(
                "attempt_exception",
                run_id=self.run_id,
                attempt_id=branch.attempt_id,
                node_id=node_id,
                exception_type=type(exc).__name__,
                message=str(exc),
            )
            raise

    @staticmethod
    def _parse_claude_json_envelope(log_path: Path) -> dict[str, Any] | None:
        for line in reversed(log_path.read_text(encoding="utf-8").splitlines()):
            candidate = line.strip()
            if candidate.startswith("{") and candidate.endswith("}"):
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue
        return None

    @staticmethod
    def _evaluate_preflight(
        reference_exit_code: int,
        claude_exit_code: int,
        changed_files: list[str],
        envelope: dict[str, Any] | None,
        expected_marker: str,
    ) -> tuple[bool, str | None]:
        if reference_exit_code != 0:
            return False, "controller_reference_pytest_failed"
        if claude_exit_code != 0:
            return False, "nested_claude_exit_nonzero"
        if changed_files:
            return False, "isolated_workspace_modified"
        if envelope is None:
            return False, "no_json_envelope"
        if envelope.get("permission_denials"):
            return False, "bash_permission_denied"
        result_text = str(envelope.get("result", ""))
        if "PREFLIGHT_FAILED" in result_text:
            return False, "nested_claude_reported_failure"
        if expected_marker not in result_text:
            return False, "missing_or_mismatched_success_marker"
        return True, None

    def preflight(self) -> dict[str, Any]:
        """Prove, cheaply and without touching repository files or receipts,
        that a nested non-interactive Sonnet session running under the exact
        node permission policy can actually execute the authorized pytest
        Bash command. Must be green before N30 (or any node) is launched."""

        resolved_python = self.python_executable()
        log_dir = self.receipts.root / "logs" / "preflight"
        branch = self._copy_workspace("preflight")
        attempt = branch.attempt_id

        reference = run_command(
            [resolved_python, "-m", "pytest", "--version"],
            REPO_ROOT,
            60,
            log_dir / f"{attempt}.reference.log",
            self.events,
            {
                "run_id": self.run_id,
                "attempt_id": attempt,
                "node_id": "preflight",
                "stage": "reference",
            },
        )
        expected_marker = f"PREFLIGHT_OK: {reference['tail'].strip()}"

        workspace = branch.workspace
        before = branch.base
        try:
            command = expand_placeholders(
                list(self.manifest.data["execution"]["claude_command"]), resolved_python
            )
            prompt = (
                "You are proving the Plan 26 non-interactive launcher before any node runs.\n"
                f"Run exactly this command using the Bash tool: {resolved_python} -m pytest --version\n"
                "Do not run any other command. Do not edit, create, or delete any file.\n"
                "When it succeeds, reply with only one line, exactly:\n"
                "PREFLIGHT_OK: <the exact stdout produced by that command>\n"
                "If the command is denied or fails, reply with only one line: PREFLIGHT_FAILED: <reason>.\n"
            )
            write_new_text(branch.root / "effective_prompt.txt", prompt)
            command.append(prompt)
            claude_log_path = log_dir / f"{attempt}.claude.log"
            claude_result = run_command(
                command,
                workspace,
                self.manifest.data["execution"]["test_timeout_seconds"],
                claude_log_path,
                self.events,
                {
                    "run_id": self.run_id,
                    "attempt_id": attempt,
                    "node_id": "preflight",
                    "stage": "nested_claude",
                },
            )
            after = snapshot(workspace)
            write_new_json(branch.root / "final.snapshot.json", after)
            changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))

            envelope = None
            if reference["exit_code"] == 0 and claude_result["exit_code"] == 0 and not changed:
                envelope = self._parse_claude_json_envelope(claude_log_path)
            passed, reason = self._evaluate_preflight(
                reference["exit_code"], claude_result["exit_code"], changed, envelope, expected_marker
            )

            payload = {
                "preflight": True,
                "passed": passed,
                "reason": reason,
                "resolved_python": resolved_python,
                "command": claude_result["argv"],
                "exit_code": claude_result["exit_code"],
                "log": str(claude_log_path),
                "log_sha256": claude_result["log_sha256"],
                "changed_files": changed,
            }
            result_log_path = log_dir / f"{attempt}.result.json"
            write_new_json(result_log_path, payload)
            self._write_attempt_outcome(branch, "verification_outcome.json", payload)
            return payload
        except BaseException as exc:
            write_new_json(
                branch.root / "exception.json",
                {
                    "attempt_id": attempt,
                    "node_id": "preflight",
                    "exception_type": type(exc).__name__,
                    "message": str(exc),
                    "occurred_at": utc_now(),
                },
            )
            raise

    def _merge(self, result: dict[str, Any]) -> dict[str, Any]:
        node_id = result["node_id"]
        branch: AttemptBranch = result["branch"]
        workspace = branch.workspace
        before = branch.base
        self.receipts.clear_digest_cache()
        for relative in result["changed"]:
            current = path_digest(REPO_ROOT, relative)
            if current != before.get(relative):
                raise ControllerError(f"{node_id}: main workspace changed concurrently at {relative}")
        backup_root = branch.root / "premerge"
        backup_manifest: dict[str, Any] = {}
        for relative in result["changed"]:
            target = REPO_ROOT / relative
            backup = backup_root / relative
            if target.is_file() or target.is_symlink():
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup, follow_symlinks=False)
                backup_manifest[relative] = {
                    "existed": True,
                    "sha256": sha256_file(target),
                    "backup": backup.relative_to(branch.root).as_posix(),
                }
            else:
                backup_manifest[relative] = {"existed": False, "sha256": None, "backup": None}
        write_new_json(branch.root / "premerge.manifest.json", backup_manifest)
        self.events.append(
            "merge_started",
            run_id=self.run_id,
            attempt_id=branch.attempt_id,
            node_id=node_id,
            changed_files=result["changed"],
            premerge_manifest_sha256=sha256_file(branch.root / "premerge.manifest.json"),
        )
        applied: list[str] = []
        try:
            for relative in result["changed"]:
                source = workspace / relative
                target = REPO_ROOT / relative
                if source.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    staged = target.with_name(f".{target.name}.{branch.attempt_id}.tmp")
                    shutil.copy2(source, staged)
                    os.replace(staged, target)
                elif target.exists() or target.is_symlink():
                    target.unlink()
                applied.append(relative)
                self.events.append(
                    "merge_path_applied",
                    run_id=self.run_id,
                    attempt_id=branch.attempt_id,
                    node_id=node_id,
                    path=relative,
                    output_sha256=path_digest(REPO_ROOT, relative),
                )
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
                source="claude_sonnet_retained_branch",
                changed_files=result["changed"],
                attempt_id=branch.attempt_id,
                branch_id=branch.branch_id,
                checkpoint=self.predecessor_checkpoint(node_id),
            )
            self.receipts.save(receipt)
            merge_outcome = {
                "attempt_id": branch.attempt_id,
                "node_id": node_id,
                "branch_id": branch.branch_id,
                "status": result["status"],
                "merged_files": result["changed"],
                "receipt": self.receipts.path(node_id).relative_to(REPO_ROOT).as_posix(),
                "receipt_sha256": sha256_file(self.receipts.path(node_id)),
            }
            self._write_attempt_outcome(branch, "merge_outcome.json", merge_outcome)
            self.events.append(
                "merge_completed",
                run_id=self.run_id,
                attempt_id=branch.attempt_id,
                node_id=node_id,
                receipt_sha256=merge_outcome["receipt_sha256"],
            )
            return receipt
        except BaseException:
            for relative in reversed(applied):
                target = REPO_ROOT / relative
                record = backup_manifest[relative]
                if record["existed"]:
                    backup = branch.root / record["backup"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    staged = target.with_name(f".{target.name}.{branch.attempt_id}.rollback.tmp")
                    shutil.copy2(backup, staged, follow_symlinks=False)
                    os.replace(staged, target)
                elif target.exists() or target.is_symlink():
                    target.unlink()
            self.events.append(
                "merge_rolled_back",
                run_id=self.run_id,
                attempt_id=branch.attempt_id,
                node_id=node_id,
                restored_files=applied,
            )
            raise

    def create_patch(
        self,
        patch_id: str,
        target_node: str,
        instructions: str,
        reason: str,
        expected_effect: str,
        scope: str,
        context: dict[str, Any] | None,
        dry_run: bool,
    ) -> dict[str, Any]:
        before = self.status()
        payload = self.patches.create_overlay(
            patch_id,
            target_node,
            instructions,
            reason,
            expected_effect,
            scope,
            context,
            dry_run,
        )
        if not dry_run:
            after = self.status()
            self.events.append(
                "patch_created",
                run_id=self.run_id,
                patch_id=patch_id,
                patch_sha256=payload["sha256"],
                target_node=target_node,
                scope=scope,
                statuses_before=before["statuses"],
                statuses_after=after["statuses"],
            )
            payload["status"] = after
        return payload

    def revoke_patch(
        self,
        patch_id: str,
        supersedes: list[str],
        reason: str,
        expected_effect: str,
        dry_run: bool,
    ) -> dict[str, Any]:
        before = self.status()
        payload = self.patches.revoke(
            patch_id, supersedes, reason, expected_effect, dry_run
        )
        if not dry_run:
            after = self.status()
            self.events.append(
                "patch_revoked",
                run_id=self.run_id,
                patch_id=patch_id,
                patch_sha256=payload["sha256"],
                supersedes=supersedes,
                statuses_before=before["statuses"],
                statuses_after=after["statuses"],
            )
            payload["status"] = after
        return payload

    def attempts_status(self) -> dict[str, Any]:
        attempts: list[dict[str, Any]] = []
        if self.attempt_root.exists():
            for metadata_path in sorted(self.attempt_root.glob("*/*/attempt.json")):
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                root = metadata_path.parent
                outcomes = sorted(path.name for path in root.glob("*outcome.json"))
                exception_path = root / "exception.json"
                attempts.append(
                    {
                        "attempt_id": metadata["attempt_id"],
                        "node_id": metadata["node_id"],
                        "branch_id": metadata["branch_id"],
                        "parent_attempt_id": metadata.get("parent_attempt_id"),
                        "created_at": metadata["created_at"],
                        "outcomes": outcomes,
                        "exception": json.loads(exception_path.read_text(encoding="utf-8")) if exception_path.is_file() else None,
                        "resumable": (root / "repo").is_dir(),
                        "path": root.relative_to(REPO_ROOT).as_posix(),
                    }
                )
        return {"attempt_count": len(attempts), "attempts": attempts}

    def audit_anchor(self) -> dict[str, Any]:
        """Hash-anchor all pre-existing scheduler artifacts without modifying them."""

        anchor_id = new_id("anchor")
        audit_root = self.receipts.root / "audit"
        entries: list[dict[str, Any]] = []
        results_root = PLAN_DIR / "results"
        if results_root.exists():
            for path in sorted(results_root.rglob("*")):
                if not path.is_file() or audit_root in path.parents:
                    continue
                entries.append(
                    {
                        "path": path.relative_to(REPO_ROOT).as_posix(),
                        "sha256": sha256_file(path),
                        "size": path.stat().st_size,
                        "mtime_ns": path.stat().st_mtime_ns,
                    }
                )
        payload = {
            "schema_version": 1,
            "anchor_id": anchor_id,
            "created_at": utc_now(),
            "graph_digest": self.manifest.digest,
            "harness_digest": self.harness_digest(),
            "entries": entries,
        }
        target = audit_root / "anchors" / f"{anchor_id}.json"
        write_new_json(target, payload)
        self.events.append(
            "audit_anchor_created",
            run_id=self.run_id,
            anchor_id=anchor_id,
            anchor_path=target.relative_to(REPO_ROOT).as_posix(),
            anchor_sha256=sha256_file(target),
            artifact_count=len(entries),
        )
        return {
            "anchor_id": anchor_id,
            "anchor_path": target.relative_to(REPO_ROOT).as_posix(),
            "anchor_sha256": sha256_file(target),
            "artifact_count": len(entries),
        }

    def postmortem(self) -> dict[str, Any]:
        events: list[dict[str, Any]] = []
        if self.events.path.is_file():
            for number, line in enumerate(self.events.path.read_text(encoding="utf-8").splitlines(), start=1):
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ControllerError(f"corrupt audit event at line {number}: {exc}") from exc
        counts: dict[str, int] = {}
        for event in events:
            name = str(event.get("event", "unknown"))
            counts[name] = counts.get(name, 0) + 1
        attempts = self.attempts_status()
        incomplete = [
            attempt
            for attempt in attempts["attempts"]
            if not attempt["outcomes"] and attempt["exception"] is None
        ]
        anchors = []
        anchor_root = self.receipts.root / "audit" / "anchors"
        if anchor_root.exists():
            anchors = [
                {
                    "path": path.relative_to(REPO_ROOT).as_posix(),
                    "sha256": sha256_file(path),
                }
                for path in sorted(anchor_root.glob("*.json"))
            ]
        return {
            "graph_digest": self.manifest.digest,
            "harness_digest": self.harness_digest(),
            "audit_log": self.events.path.relative_to(REPO_ROOT).as_posix(),
            "audit_log_sha256": sha256_file(self.events.path) if self.events.path.is_file() else None,
            "event_count": len(events),
            "event_counts": counts,
            "attempts": attempts,
            "incomplete_attempts": incomplete,
            "anchors": anchors,
            "patches": self.patches.status(),
            "current_status": self.status(),
        }

    def run_generation(
        self,
        dry_run: bool = False,
        only_node: str | None = None,
        resume_attempt: str | None = None,
    ) -> dict[str, Any]:
        state = self.status()
        ready = state["ready"]
        if only_node:
            if only_node not in ready:
                raise ControllerError(f"{only_node} is not READY")
            selected = [only_node]
        else:
            selected = self.select_disjoint(ready)
        if resume_attempt and (not only_node or selected != [only_node]):
            raise ControllerError("--resume-attempt requires exactly one --node")
        if dry_run or not selected:
            return {
                "dry_run": dry_run,
                "selected": selected,
                "resume_attempt": resume_attempt,
                "status": state,
            }

        results: list[dict[str, Any]] = []
        self.events.append(
            "generation_started",
            run_id=self.run_id,
            selected=selected,
            resume_attempt=resume_attempt,
            graph_digest=self.manifest.digest,
            harness_digest=self.harness_digest(),
        )
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(selected)) as pool:
            futures = {
                pool.submit(
                    self._run_isolated,
                    node_id,
                    resume_attempt if node_id == only_node else None,
                ): node_id
                for node_id in selected
            }
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())

        passed: list[str] = []
        blocked: list[dict[str, Any]] = []
        for result in sorted(results, key=lambda item: item["node_id"]):
            # _run_isolated already enforced reported_status in allowed_results
            # and reported_status != "BLOCKED" before returning this shape (the
            # "branch" key), so any status other than the literal string
            # "BLOCKED" here is a legitimate, admissible terminal outcome (e.g.
            # NOT_AVAILABLE for N60) that must be merged and receipted the same
            # way "PASSED" is — otherwise a node with an allowed non-PASSED
            # terminal can never become admissible, permanently starving any
            # descendant that depends on it.
            if result["status"] != "BLOCKED":
                self._merge(result)
                passed.append(result["node_id"])
            else:
                blocked.append(result)
        final = {"selected": selected, "passed": passed, "blocked": blocked, "status": self.status()}
        self.events.append(
            "generation_finished",
            run_id=self.run_id,
            selected=selected,
            passed=passed,
            blocked=[
                {
                    "node_id": item["node_id"],
                    "attempt_id": item.get("attempt_id"),
                    "reason": item.get("reason"),
                }
                for item in blocked
            ],
        )
        return final


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    subcommands = result.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate")
    subcommands.add_parser("status")
    subcommands.add_parser("patch-status")
    subcommands.add_parser("attempts")
    subcommands.add_parser("audit-anchor")
    subcommands.add_parser("postmortem")
    adopt = subcommands.add_parser("adopt-v2")
    adopt.add_argument("--through")
    subcommands.add_parser("preflight")
    run = subcommands.add_parser("run")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--node")
    run.add_argument("--resume-attempt")
    rebase = subcommands.add_parser("rebase")
    rebase.add_argument("--node", required=True)
    rebase.add_argument("--attempt", required=True)
    rebase.add_argument("--dry-run", action="store_true")
    create_patch = subcommands.add_parser("create-patch")
    create_patch.add_argument("--patch-id", required=True)
    create_patch.add_argument("--node", required=True)
    create_patch.add_argument("--instructions-file", type=Path, required=True)
    create_patch.add_argument("--reason", required=True)
    create_patch.add_argument("--expected-effect", required=True)
    create_patch.add_argument(
        "--scope", choices=["node_only", "node_and_descendants"], default="node_only"
    )
    create_patch.add_argument("--context-json", type=Path)
    create_patch.add_argument("--dry-run", action="store_true")
    revoke_patch = subcommands.add_parser("revoke-patch")
    revoke_patch.add_argument("--patch-id", required=True)
    revoke_patch.add_argument("--supersedes", action="append", required=True)
    revoke_patch.add_argument("--reason", required=True)
    revoke_patch.add_argument("--expected-effect", required=True)
    revoke_patch.add_argument("--dry-run", action="store_true")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    signal.signal(signal.SIGINT, terminate_active_processes)
    signal.signal(signal.SIGTERM, terminate_active_processes)
    controller: Controller | None = None
    try:
        exit_status = 0
        manifest = Manifest.load(arguments.manifest)
        controller = Controller(manifest)
        mutating = arguments.command in {
            "adopt-v2",
            "preflight",
            "run",
            "rebase",
            "create-patch",
            "revoke-patch",
            "audit-anchor",
        } and not getattr(arguments, "dry_run", False)
        if mutating:
            controller.events.append(
                "controller_invoked",
                run_id=controller.run_id,
                command=arguments.command,
                graph_digest=manifest.digest,
                harness_digest=controller.harness_digest(),
            )
        if arguments.command == "validate":
            payload = {"valid": True, "graph_digest": manifest.digest, "topological_order": manifest.topological_order()}
        elif arguments.command == "status":
            payload = controller.status()
        elif arguments.command == "patch-status":
            payload = controller.patches.status()
        elif arguments.command == "attempts":
            payload = controller.attempts_status()
        elif arguments.command == "audit-anchor":
            payload = controller.audit_anchor()
        elif arguments.command == "postmortem":
            payload = controller.postmortem()
        elif arguments.command == "adopt-v2":
            payload = controller.adopt_v2(arguments.through)
        elif arguments.command == "rebase":
            payload = controller.rebase(arguments.node, arguments.attempt, arguments.dry_run)
        elif arguments.command == "preflight":
            payload = controller.preflight()
            if not payload["passed"]:
                exit_status = 3
        elif arguments.command == "create-patch":
            instructions = arguments.instructions_file.read_text(encoding="utf-8")
            context = None
            if arguments.context_json:
                context = json.loads(arguments.context_json.read_text(encoding="utf-8"))
                if not isinstance(context, dict):
                    raise ControllerError("--context-json must contain a JSON object")
            payload = controller.create_patch(
                arguments.patch_id,
                arguments.node,
                instructions,
                arguments.reason,
                arguments.expected_effect,
                arguments.scope,
                context,
                arguments.dry_run,
            )
        elif arguments.command == "revoke-patch":
            payload = controller.revoke_patch(
                arguments.patch_id,
                arguments.supersedes,
                arguments.reason,
                arguments.expected_effect,
                arguments.dry_run,
            )
        else:
            payload = controller.run_generation(
                dry_run=arguments.dry_run,
                only_node=arguments.node,
                resume_attempt=arguments.resume_attempt,
            )
        if mutating:
            controller.events.append(
                "controller_completed",
                run_id=controller.run_id,
                command=arguments.command,
            )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return exit_status
    except (ControllerError, jsonschema.ValidationError, yaml.YAMLError, OSError, json.JSONDecodeError) as exc:
        if controller is not None:
            controller.events.append(
                "controller_failed",
                run_id=controller.run_id,
                command=arguments.command,
                exception_type=type(exc).__name__,
                message=str(exc),
            )
        print(json.dumps({"error": type(exc).__name__, "message": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
