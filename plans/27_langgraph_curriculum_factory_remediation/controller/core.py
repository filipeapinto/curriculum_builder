#!/usr/bin/env python3
"""Shared primitives for the Run 27 implementation scheduler.

This module is deliberately independent of the Plan 26 controller. It provides
only hashing, path, graph, and schema-bound result loading. No function in this
module reads status from prose or Markdown.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import jsonschema
import yaml


EPHEMERAL_NAMES = frozenset({".DS_Store", ".git", ".pytest_cache", "__pycache__"})
EPHEMERAL_SUFFIXES = frozenset({".pyc", ".pyo"})

CONTROLLER_DIR = Path(__file__).resolve().parent
DEFAULT_PLAN_DIR = CONTROLLER_DIR.parent
DEFAULT_REPO_ROOT = DEFAULT_PLAN_DIR.parents[1]
DEFAULT_GRAPH_PATH = DEFAULT_PLAN_DIR / "implementation.graph.v1.yaml"
DEFAULT_STATE_DIR = DEFAULT_PLAN_DIR / ".run27_state"

ADMISSIBLE_OUTCOMES = frozenset({"PASSED", "NOT_AVAILABLE"})


class ControllerError(RuntimeError):
    """Every refusal raised by the scheduler and its verifiers."""

    def __init__(self, message: str, code: str = "CONTROLLER_ERROR") -> None:
        super().__init__(message)
        self.code = code


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_digest(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


def serialize_record(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def is_ephemeral(path: Path) -> bool:
    if path.suffix in EPHEMERAL_SUFFIXES:
        return True
    return any(part in EPHEMERAL_NAMES for part in path.parts)


def tree_digest(root: Path) -> str:
    entries: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if is_ephemeral(relative):
            continue
        entries[relative.as_posix()] = sha256_file(path)
    return canonical_digest({"tree": entries})


def path_digest(repo_root: Path, relative: str) -> str | None:
    """Digest a declared write path. Directories digest as their file tree."""

    target = repo_root / relative
    if target.is_dir():
        return tree_digest(target)
    if target.is_file():
        return sha256_file(target)
    return None


def write_once_text(path: Path, text: str) -> None:
    """Create an artifact exactly once. Rewriting an attempt artifact is a defect."""

    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise ControllerError(
            f"write-once artifact already exists: {path}", code="WRITE_ONCE_VIOLATION"
        ) from error


def write_once_json(path: Path, value: Any) -> None:
    write_once_text(path, serialize_record(value))


def atomic_write_text(path: Path, text: str) -> None:
    """Replace a file's whole content in one rename. Never leaves partial bytes."""

    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(f".{path.name}.{os.getpid()}.staging")
    with staging.open("w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(staging, path)


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_text(record) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def covers(owner: str, changed: str) -> bool:
    owner_path = Path(owner)
    changed_path = Path(changed)
    return owner_path == changed_path or owner_path in changed_path.parents


def paths_overlap(left: str, right: str) -> bool:
    left_path = Path(left)
    right_path = Path(right)
    return (
        left_path == right_path
        or left_path in right_path.parents
        or right_path in left_path.parents
    )


def load_json_strict(path: Path, *, what: str) -> dict[str, Any]:
    """Parse a JSON object. Markdown, prose, and bare status lines are refused here."""

    if not path.is_file():
        raise ControllerError(f"{what}: missing file {path}", code="MISSING_ARTIFACT")
    raw = path.read_text(encoding="utf-8")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ControllerError(
            f"{what}: {path} is not machine-readable JSON ({error}); "
            "prose and Markdown cannot report a node status",
            code="NON_JSON_RESULT",
        ) from error
    if not isinstance(value, dict):
        raise ControllerError(
            f"{what}: {path} is not a JSON object", code="NON_JSON_RESULT"
        )
    return value


class Graph:
    """The Run 27 implementation graph, loaded read-only."""

    def __init__(self, data: dict[str, Any], path: Path, repo_root: Path) -> None:
        self.data = data
        self.path = path
        self.repo_root = repo_root
        self.digest = sha256_file(path)

    @classmethod
    def load(cls, graph_path: Path | None = None, repo_root: Path | None = None) -> "Graph":
        graph_path = Path(graph_path) if graph_path else DEFAULT_GRAPH_PATH
        graph_path = graph_path.resolve()
        if repo_root is None:
            repo_root = DEFAULT_REPO_ROOT
        repo_root = Path(repo_root).resolve()
        if not graph_path.is_file():
            raise ControllerError(f"missing graph: {graph_path}", code="MISSING_GRAPH")
        data = yaml.safe_load(graph_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "nodes" not in data:
            raise ControllerError(f"{graph_path}: not a graph mapping", code="MISSING_GRAPH")
        return cls(data, graph_path, repo_root)

    @property
    def nodes(self) -> dict[str, Any]:
        return self.data["nodes"]

    @property
    def entry(self) -> str:
        return self.data["entry"]

    @property
    def rules(self) -> dict[str, Any]:
        return self.data.get("rules", {})

    def node(self, node_id: str) -> dict[str, Any]:
        if node_id not in self.nodes:
            raise ControllerError(f"unknown node: {node_id}", code="UNKNOWN_NODE")
        return self.nodes[node_id]

    def order(self) -> list[str]:
        remaining = {
            node_id: set(node["depends_on"]) for node_id, node in self.nodes.items()
        }
        unknown = {
            dependency
            for dependencies in remaining.values()
            for dependency in dependencies
            if dependency not in self.nodes
        }
        if unknown:
            raise ControllerError(f"unknown dependencies: {sorted(unknown)}", code="BAD_GRAPH")
        order: list[str] = []
        while remaining:
            ready = sorted(
                node_id for node_id, pending in remaining.items() if not pending
            )
            if not ready:
                raise ControllerError(
                    f"dependency cycle: {sorted(remaining)}", code="BAD_GRAPH"
                )
            order.extend(ready)
            for node_id in ready:
                remaining.pop(node_id)
            for pending in remaining.values():
                pending.difference_update(ready)
        return order

    def descendants(self, node_id: str) -> list[str]:
        """Every transitive descendant, in graph order."""

        found: set[str] = set()
        frontier = {node_id}
        while frontier:
            nxt: set[str] = set()
            for candidate, node in self.nodes.items():
                if candidate in found:
                    continue
                if frontier & set(node["depends_on"]):
                    found.add(candidate)
                    nxt.add(candidate)
            frontier = nxt
        return [item for item in self.order() if item in found]

    def ancestors(self, node_id: str) -> list[str]:
        found: set[str] = set()
        frontier = set(self.node(node_id)["depends_on"])
        while frontier:
            found |= frontier
            frontier = {
                dependency
                for item in frontier
                for dependency in self.node(item)["depends_on"]
            } - found
        return [item for item in self.order() if item in found]

    def node_definition_digest(self, node_id: str) -> str:
        return canonical_digest(
            {"node_id": node_id, "definition": self.node(node_id), "rules": self.rules}
        )

    def result_path(self, node_id: str) -> Path:
        return self.repo_root / self.data["result_pattern"].format(node_id=node_id)

    def relative_result(self, node_id: str) -> str:
        return self.data["result_pattern"].format(node_id=node_id)

    def prompt_digest(self, node_id: str) -> str:
        prompt = self.repo_root / self.node(node_id)["prompt"]
        if not prompt.is_file():
            raise ControllerError(f"{node_id}: missing prompt {prompt}", code="MISSING_PROMPT")
        return sha256_file(prompt)

    def source_spec_digest(self) -> str | None:
        spec = self.repo_root / self.data["source_spec"]
        return sha256_file(spec) if spec.is_file() else None

    def result_schema(self) -> dict[str, Any]:
        return load_json_strict(
            self.repo_root / self.data["node_result_schema"], what="node result schema"
        )

    def live_proof_nodes(self) -> list[str]:
        """Nodes the graph allows to report NOT_AVAILABLE are the live-proof nodes."""

        return [
            node_id
            for node_id in self.order()
            if "NOT_AVAILABLE" in self.node(node_id)["allowed_results"]
        ]

    def final_audit_node(self) -> str:
        sinks = [
            node_id
            for node_id in self.order()
            if not any(node_id in node["depends_on"] for node in self.nodes.values())
        ]
        if len(sinks) != 1:
            raise ControllerError(
                f"graph must have exactly one final audit node, found {sinks}",
                code="BAD_GRAPH",
            )
        return sinks[0]


def load_node_result(graph: Graph, node_id: str) -> dict[str, Any]:
    """Load a node result. Admission consumes only schema-valid JSON."""

    result_path = graph.result_path(node_id)
    result = load_json_strict(result_path, what=f"{node_id} result")
    schema = graph.result_schema()
    try:
        jsonschema.Draft202012Validator(schema).validate(result)
    except jsonschema.ValidationError as error:
        raise ControllerError(
            f"{node_id}: result does not validate against the frozen node result "
            f"schema: {error.message}",
            code="SCHEMA_INVALID_RESULT",
        ) from error
    if result["node_id"] != node_id:
        raise ControllerError(
            f"{node_id}: result declares node_id {result['node_id']!r}",
            code="NODE_ID_MISMATCH",
        )
    if result["outcome"] not in graph.node(node_id)["allowed_results"]:
        raise ControllerError(
            f"{node_id}: outcome {result['outcome']!r} is not allowed by the graph",
            code="OUTCOME_NOT_ALLOWED",
        )
    return result


def result_digest(graph: Graph, node_id: str) -> str | None:
    path = graph.result_path(node_id)
    return sha256_file(path) if path.is_file() else None


def missing_paths(repo_root: Path, relatives: Iterable[str]) -> list[str]:
    return [item for item in relatives if not (repo_root / item).exists()]
