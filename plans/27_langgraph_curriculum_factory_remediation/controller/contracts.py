#!/usr/bin/env python3
"""Contract verification engine shared by the Run 27 node contract verifiers.

A contract is a YAML document that states falsifiable claims about the real
repository. Every claim is checked against current bytes; nothing is taken on
the contract's word. Later nodes author the contracts, this engine checks them.

    schema_version: 1
    kind: integration_ownership | evidence_determinism | requirements_lineage
    contract_id: <string>
    node_id: <graph node id>
    claims:
      - {type: ..., ...}
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

import yaml

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from core import ControllerError, Graph, covers, path_digest, sha256_file  # noqa: E402


KINDS = ("integration_ownership", "evidence_determinism", "requirements_lineage")

COMMON_CLAIMS = (
    "file_exists",
    "file_absent",
    "file_sha256",
    "tree_sha256",
    "text_contains",
    "text_absent",
)

CLAIMS_BY_KIND: dict[str, tuple[str, ...]] = {
    "integration_ownership": COMMON_CLAIMS
    + ("owned_by_node", "single_owner", "symbol_defined", "imports_module", "not_imports_module"),
    "evidence_determinism": COMMON_CLAIMS
    + ("command_repeats_identically", "paths_stable_under_command"),
    "requirements_lineage": COMMON_CLAIMS + ("requirement", "requirement_ids_cover"),
}


class Contract:
    def __init__(self, data: dict[str, Any], path: Path) -> None:
        self.data = data
        self.path = path

    @classmethod
    def load(cls, path: Path) -> "Contract":
        path = Path(path).resolve()
        if not path.is_file():
            raise ControllerError(f"missing contract: {path}", code="MISSING_CONTRACT")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ControllerError(f"{path}: contract must be a mapping", code="BAD_CONTRACT")
        for key in ("schema_version", "kind", "contract_id", "node_id", "claims"):
            if key not in data:
                raise ControllerError(f"{path}: contract is missing {key!r}", code="BAD_CONTRACT")
        if data["schema_version"] != 1:
            raise ControllerError(f"{path}: unsupported contract schema_version", code="BAD_CONTRACT")
        if data["kind"] not in KINDS:
            raise ControllerError(f"{path}: unknown contract kind {data['kind']!r}", code="BAD_CONTRACT")
        if not isinstance(data["claims"], list) or not data["claims"]:
            raise ControllerError(f"{path}: contract must state at least one claim", code="BAD_CONTRACT")
        return cls(data, path)

    @property
    def kind(self) -> str:
        return self.data["kind"]


def _repo_text(repo_root: Path, relative: str) -> str:
    target = repo_root / relative
    if not target.is_file():
        raise FileNotFoundError(relative)
    return target.read_text(encoding="utf-8")


def _run(argv: list[str], repo_root: Path) -> tuple[int, bytes]:
    resolved = [sys.executable if item == "python3" else item for item in argv]
    completed = subprocess.run(
        resolved,
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return completed.returncode, completed.stdout


def _imported_modules(source: str) -> set[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def _defined_symbols(source: str) -> set[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    symbols: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.add(node.name)
        elif isinstance(node, ast.Assign):
            symbols.update(item.id for item in node.targets if isinstance(item, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            symbols.add(node.target.id)
    return symbols


def _owners(graph: Graph, relative: str) -> list[str]:
    return sorted(
        node_id
        for node_id, node in graph.nodes.items()
        if any(covers(owner, relative) for owner in node["writes"])
    )


def check_claim(claim: dict[str, Any], graph: Graph, contract: Contract) -> dict[str, Any]:
    kind = claim.get("type")
    repo_root = graph.repo_root
    allowed = CLAIMS_BY_KIND[contract.kind]
    if kind not in allowed:
        return {"type": kind, "ok": False, "detail": f"claim type is not legal for {contract.kind}"}

    try:
        if kind == "file_exists":
            ok = (repo_root / claim["path"]).is_file()
            return {"type": kind, "path": claim["path"], "ok": ok, "detail": "" if ok else "missing"}
        if kind == "file_absent":
            ok = not (repo_root / claim["path"]).exists()
            return {"type": kind, "path": claim["path"], "ok": ok, "detail": "" if ok else "present"}
        if kind == "file_sha256":
            target = repo_root / claim["path"]
            if not target.is_file():
                return {"type": kind, "path": claim["path"], "ok": False, "detail": "missing"}
            actual = sha256_file(target)
            return {
                "type": kind,
                "path": claim["path"],
                "ok": actual == claim["sha256"],
                "detail": f"actual={actual}",
            }
        if kind == "tree_sha256":
            actual = path_digest(repo_root, claim["path"])
            return {
                "type": kind,
                "path": claim["path"],
                "ok": actual == claim["sha256"],
                "detail": f"actual={actual}",
            }
        if kind == "text_contains":
            text = _repo_text(repo_root, claim["path"])
            ok = claim["text"] in text
            return {"type": kind, "path": claim["path"], "ok": ok, "detail": "" if ok else "absent"}
        if kind == "text_absent":
            text = _repo_text(repo_root, claim["path"])
            matches = re.findall(claim["pattern"], text)
            return {
                "type": kind,
                "path": claim["path"],
                "ok": not matches,
                "detail": f"{len(matches)} match(es)",
            }
        if kind == "owned_by_node":
            owners = _owners(graph, claim["path"])
            ok = owners == [claim["node"]]
            return {"type": kind, "path": claim["path"], "ok": ok, "detail": f"owners={owners}"}
        if kind == "single_owner":
            owners = _owners(graph, claim["path"])
            return {"type": kind, "path": claim["path"], "ok": len(owners) == 1, "detail": f"owners={owners}"}
        if kind == "symbol_defined":
            symbols = _defined_symbols(_repo_text(repo_root, claim["path"]))
            ok = claim["symbol"] in symbols
            return {
                "type": kind,
                "path": claim["path"],
                "ok": ok,
                "detail": "" if ok else f"{claim['symbol']} is not defined at module level",
            }
        if kind in {"imports_module", "not_imports_module"}:
            modules = _imported_modules(_repo_text(repo_root, claim["path"]))
            present = claim["module"] in modules
            ok = present if kind == "imports_module" else not present
            return {"type": kind, "path": claim["path"], "ok": ok, "detail": f"present={present}"}
        if kind == "command_repeats_identically":
            argv = list(claim["argv"])
            runs = int(claim.get("runs", 2))
            observed = [_run(argv, repo_root) for _ in range(max(runs, 2))]
            codes = {item[0] for item in observed}
            outputs = {item[1] for item in observed}
            expected_code = claim.get("exit_code")
            ok = len(codes) == 1 and len(outputs) == 1
            if expected_code is not None:
                ok = ok and next(iter(codes)) == expected_code
            return {
                "type": kind,
                "argv": argv,
                "ok": ok,
                "detail": f"exit_codes={sorted(codes)} distinct_outputs={len(outputs)}",
            }
        if kind == "paths_stable_under_command":
            argv = list(claim["argv"])
            paths = list(claim["paths"])
            before = {item: path_digest(repo_root, item) for item in paths}
            exit_code, _output = _run(argv, repo_root)
            after = {item: path_digest(repo_root, item) for item in paths}
            drifted = sorted(item for item in paths if before[item] != after[item])
            expected_code = claim.get("exit_code")
            ok = not drifted and (expected_code is None or exit_code == expected_code)
            return {
                "type": kind,
                "argv": argv,
                "ok": ok,
                "detail": f"exit_code={exit_code} drifted={drifted}",
            }
        if kind == "requirement":
            problems: list[str] = []
            source = claim["source"]
            if not (repo_root / source).is_file():
                problems.append(f"missing source {source}")
            elif claim["source_anchor"] not in _repo_text(repo_root, source):
                problems.append(f"anchor {claim['source_anchor']!r} not found in {source}")
            for relative in list(claim.get("implemented_by", [])) + list(claim.get("evidence", [])):
                if not (repo_root / relative).exists():
                    problems.append(f"missing lineage path {relative}")
            if not claim.get("implemented_by"):
                problems.append("requirement claims no implementation")
            return {
                "type": kind,
                "id": claim["id"],
                "ok": not problems,
                "detail": "; ".join(problems),
            }
        if kind == "requirement_ids_cover":
            source = claim["source"]
            text = _repo_text(repo_root, source)
            declared = {
                item["id"]
                for item in contract.data["claims"]
                if item.get("type") == "requirement"
            }
            found = set(re.findall(claim["pattern"], text))
            missing = sorted(found - declared)
            return {
                "type": kind,
                "source": source,
                "ok": not missing,
                "detail": f"uncovered={missing}",
            }
    except FileNotFoundError as error:
        return {"type": kind, "ok": False, "detail": f"missing file: {error}"}
    except KeyError as error:
        return {"type": kind, "ok": False, "detail": f"claim is missing field {error}"}
    return {"type": kind, "ok": False, "detail": "unhandled claim type"}


def verify(contract_path: Path, graph: Graph, expected_kind: str) -> dict[str, Any]:
    contract = Contract.load(contract_path)
    if contract.kind != expected_kind:
        raise ControllerError(
            f"{contract_path}: expected a {expected_kind} contract, found {contract.kind}",
            code="CONTRACT_KIND_MISMATCH",
        )
    if contract.data["node_id"] not in graph.nodes:
        raise ControllerError(
            f"{contract_path}: node_id {contract.data['node_id']!r} is not in the graph",
            code="CONTRACT_NODE_UNKNOWN",
        )
    results = [check_claim(claim, graph, contract) for claim in contract.data["claims"]]
    failures = [item for item in results if not item["ok"]]
    return {
        "command": f"verify-{expected_kind}",
        "contract": Path(contract_path).name,
        "contract_id": contract.data["contract_id"],
        "node_id": contract.data["node_id"],
        "kind": contract.kind,
        "claims_checked": len(results),
        "claims": results,
        "failures": failures,
        "valid": not failures,
    }


def cli(expected_kind: str, description: str) -> Callable[[list[str] | None], int]:
    import argparse

    from core import DEFAULT_GRAPH_PATH, DEFAULT_REPO_ROOT

    def main(argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--contract", required=True, type=Path)
        parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH_PATH)
        parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
        arguments = parser.parse_args(argv)
        try:
            graph = Graph.load(arguments.graph, arguments.repo_root)
            report = verify(arguments.contract, graph, expected_kind)
        except ControllerError as error:
            print(json.dumps({"ok": False, "code": error.code, "error": str(error)}, sort_keys=True))
            return 1
        print(json.dumps({"ok": report["valid"], **report}, sort_keys=True))
        return 0 if report["valid"] else 1

    return main
