#!/usr/bin/env python3
"""Scoped provider/import and credential-use scanner for Run 27.

Two independent scopes, both declared by the graph and neither invented here:

``production``
    ``rules.forbidden_production_scan``. Walks only ``scan_roots``, honours
    ``excluded_roots`` (``plans``, ``tests``, ``outputs``) and ``excluded_globs``,
    and therefore never reads Plan 26 history, plan scaffolding, test sources, or
    generated outputs. Prohibited dispatch/import terms must not occur at all.
    Prohibited credential names may occur only inside an explicit absence/denial
    guard in a declared ``credential_absence_guard_paths`` file.

``tests``
    ``rules.retired_provider_test_scan``, a separately configured scope with its
    own roots and its own ``zero_occurrences_in_active_test_source`` policy. It
    exists because ``tools/validate_plan.py`` requires the owner of every
    migration-affected active test to run this command.

Use ``--scope production`` to run the production scope alone.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from core import DEFAULT_GRAPH_PATH, DEFAULT_REPO_ROOT, ControllerError, Graph  # noqa: E402


DENIAL_NAME_PATTERN = re.compile(
    r"(forbidden|prohibited|denied|denial|blocked|absent|absence|guard|reject|refuse)",
    re.IGNORECASE,
)


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    out = ["^"]
    index = 0
    while index < len(pattern):
        character = pattern[index]
        if pattern.startswith("**/", index):
            out.append("(?:.*/)?")
            index += 3
        elif pattern.startswith("**", index):
            out.append(".*")
            index += 2
        elif character == "*":
            out.append("[^/]*")
            index += 1
        elif character == "?":
            out.append("[^/]")
            index += 1
        else:
            out.append(re.escape(character))
            index += 1
    out.append("$")
    return re.compile("".join(out))


def excluded(relative: str, globs: Iterable[re.Pattern[str]], roots: Iterable[str]) -> bool:
    path = Path(relative)
    for root in roots:
        root_path = Path(root)
        if root_path == path or root_path in path.parents:
            return True
    return any(pattern.match(relative) for pattern in globs)


def collect_files(repo_root: Path, roots: Iterable[str]) -> list[str]:
    found: list[str] = []
    for root in roots:
        target = repo_root / root
        if target.is_file():
            found.append(Path(root).as_posix())
        elif target.is_dir():
            for item in sorted(target.rglob("*")):
                if item.is_file():
                    found.append(item.relative_to(repo_root).as_posix())
    return sorted(set(found))


def guard_regions(source: str) -> list[tuple[int, int]]:
    """Line ranges in which a credential name may legally appear.

    A credential name is legal only inside a denial-named function, or as part of
    a module-level denial-named constant. Anything else can configure,
    authenticate, dispatch, or provide a fallback, which the policy forbids.
    """

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    regions: list[tuple[int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if DENIAL_NAME_PATTERN.search(node.name):
                regions.append((node.lineno, node.end_lineno or node.lineno))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [item.id for item in targets if isinstance(item, ast.Name)]
            if any(DENIAL_NAME_PATTERN.search(name) for name in names):
                regions.append((node.lineno, node.end_lineno or node.lineno))
    return regions


def in_region(line_number: int, regions: Iterable[tuple[int, int]]) -> bool:
    return any(start <= line_number <= end for start, end in regions)


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def scan_production(graph: Graph) -> dict[str, Any]:
    scan = graph.rules.get("forbidden_production_scan")
    if not isinstance(scan, dict):
        raise ControllerError("graph has no forbidden_production_scan", code="MISSING_SCAN_SCOPE")
    globs = [glob_to_regex(pattern) for pattern in scan["excluded_globs"]]
    excluded_roots = list(scan["excluded_roots"])
    terms = [term.casefold() for term in scan["prohibited_dispatch_or_import_terms"]]
    credentials = list(scan["prohibited_credential_names"])
    guard_paths = {Path(item).as_posix() for item in scan["credential_absence_guard_paths"]}

    for root in scan["scan_roots"]:
        if excluded(Path(root).as_posix(), globs, excluded_roots):
            raise ControllerError(
                f"scan root falls under an excluded root: {root}", code="BAD_SCAN_SCOPE"
            )

    violations: list[dict[str, Any]] = []
    scanned: list[str] = []
    for relative in collect_files(graph.repo_root, scan["scan_roots"]):
        if excluded(relative, globs, excluded_roots):
            continue
        text = read_text(graph.repo_root / relative)
        if text is None:
            continue
        scanned.append(relative)
        lines = text.splitlines()
        regions = guard_regions(text) if relative in guard_paths and relative.endswith(".py") else []
        for number, line in enumerate(lines, start=1):
            guarded = relative in guard_paths and in_region(number, regions)
            # A credential name legally cited inside an absence guard is a denial,
            # not a provider reference, so it is masked before the dispatch/import
            # term scan. Otherwise "GEMINI_API_KEY" would report itself twice.
            masked = line
            if guarded:
                for credential in credentials:
                    masked = masked.replace(credential, "<denied_credential>")
            folded = masked.casefold()
            for term in terms:
                if term in folded:
                    violations.append(
                        {
                            "scope": "production",
                            "code": "PROHIBITED_PROVIDER_TERM",
                            "path": relative,
                            "line": number,
                            "term": term,
                            "text": line.strip()[:200],
                        }
                    )
            for credential in credentials:
                if credential not in line or guarded:
                    continue
                violations.append(
                    {
                        "scope": "production",
                        "code": (
                            "CREDENTIAL_OUTSIDE_GUARD_REGION"
                            if relative in guard_paths
                            else "CREDENTIAL_OUTSIDE_GUARD_FILE"
                        ),
                        "path": relative,
                        "line": number,
                        "term": credential,
                        "text": line.strip()[:200],
                    }
                )
    return {
        "scope": "production",
        "scanned_files": scanned,
        "excluded_roots": excluded_roots,
        "policy": scan["credential_occurrence_policy"],
        "violations": violations,
    }


def scan_tests(graph: Graph) -> dict[str, Any]:
    scan = graph.rules.get("retired_provider_test_scan")
    if not isinstance(scan, dict):
        raise ControllerError("graph has no retired_provider_test_scan", code="MISSING_SCAN_SCOPE")
    if scan["occurrence_policy"] != "zero_occurrences_in_active_test_source":
        raise ControllerError(
            f"unsupported occurrence policy: {scan['occurrence_policy']}", code="BAD_SCAN_SCOPE"
        )
    globs = [glob_to_regex(pattern) for pattern in scan["excluded_globs"]]
    terms = [term.casefold() for term in scan["prohibited_terms"]]
    violations: list[dict[str, Any]] = []
    scanned: list[str] = []
    for relative in collect_files(graph.repo_root, scan["scan_roots"]):
        if excluded(relative, globs, []) or not relative.endswith(".py"):
            continue
        text = read_text(graph.repo_root / relative)
        if text is None:
            continue
        scanned.append(relative)
        for number, line in enumerate(text.splitlines(), start=1):
            folded = line.casefold()
            for term in terms:
                if term in folded:
                    violations.append(
                        {
                            "scope": "tests",
                            "code": "RETIRED_PROVIDER_TERM_IN_ACTIVE_TEST",
                            "path": relative,
                            "line": number,
                            "term": term,
                            "text": line.strip()[:200],
                        }
                    )
    return {
        "scope": "tests",
        "scanned_files": scanned,
        "policy": scan["occurrence_policy"],
        "violations": violations,
    }


def run(graph: Graph, scope: str) -> dict[str, Any]:
    scopes: list[dict[str, Any]] = []
    if scope in {"production", "all"}:
        scopes.append(scan_production(graph))
    if scope in {"tests", "all"}:
        scopes.append(scan_tests(graph))
    violations = [item for report in scopes for item in report["violations"]]
    return {
        "command": "check-forbidden-production-refs",
        "graph_sha256": graph.digest,
        "requested_scope": scope,
        "scopes": scopes,
        "violations": violations,
        "valid": not violations,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    result.add_argument("--graph", type=Path, default=DEFAULT_GRAPH_PATH)
    result.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    result.add_argument("--scope", choices=("production", "tests", "all"), default="all")
    result.add_argument("--json", action="store_true", help="print the full report")
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        graph = Graph.load(arguments.graph, arguments.repo_root)
        report = run(graph, arguments.scope)
    except ControllerError as error:
        print(json.dumps({"ok": False, "code": error.code, "error": str(error)}, sort_keys=True))
        return 1
    if arguments.json:
        print(json.dumps({"ok": report["valid"], **report}, sort_keys=True))
    else:
        print(
            json.dumps(
                {
                    "ok": report["valid"],
                    "requested_scope": report["requested_scope"],
                    "scanned_files": sum(len(item["scanned_files"]) for item in report["scopes"]),
                    "violations": report["violations"],
                },
                sort_keys=True,
            )
        )
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
