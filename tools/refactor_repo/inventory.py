#!/usr/bin/env python3
"""Read-only, schema-versioned repository inventory (spec v8 section 7).

Usage:
    python3 tools/refactor_repo/inventory.py \\
        --repo-root /path/to/checkout \\
        --output-dir /path/to/write/reports/into \\
        [--fail-collector <collector-name>]

This tool never writes anywhere except ``--output-dir``. It reads the
repository at ``--repo-root`` through git subprocess calls, plain filesystem
reads, and Python's ``ast`` module; it never renames, moves, deletes,
reformats, or otherwise mutates anything under ``--repo-root``. Every
generated JSON report validates against
schemas/repository_refactor_inventory.schema.v1.json. Collection failures
(including a fault deliberately injected via ``--fail-collector``, used by
test 1's fault-injection case) are recorded as omissions or collection
failures and cause a nonzero exit rather than an empty, falsely-successful
field.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import collectors  # noqa: E402

try:
    import jsonschema
except ImportError:  # pragma: no cover - jsonschema is a repo-wide dependency already in use
    jsonschema = None

COLLECTOR_NAMES = [
    "git_provenance", "identities", "directories", "python_surface",
    "old_identity_references", "structured_configuration", "outputs_children",
    "test_subtrees", "schema_identifiers", "environment",
]


def build_inventory(repo_root: Path, command: str, fail_collector: str | None) -> tuple[dict, bool]:
    omissions: list[dict[str, str]] = []
    collection_failures: list[dict[str, str]] = []

    def run(name: str, fn):
        if fail_collector == name:
            omissions.append({
                "collector": name,
                "reason": "fault injected via --fail-collector for test-1 fault-injection verification",
            })
            return None
        try:
            return fn()
        except collectors.CollectorUnavailable as exc:
            omissions.append({"collector": name, "reason": str(exc)})
            return None
        except Exception as exc:  # noqa: BLE001 - must record, never silently swallow
            collection_failures.append({"collector": name, "error": f"{type(exc).__name__}: {exc}"})
            return None

    scan_files = list(collectors.iter_scan_files(repo_root))
    py_files = [p for p in scan_files if p.suffix == ".py"]

    git_prov = run("git_provenance", lambda: collectors.collect_git_provenance(repo_root))
    identities = run("identities", lambda: collectors.collect_identities(repo_root, scan_files))
    directories = run("directories", lambda: collectors.collect_directories(repo_root))
    python_surface = run(
        "python_surface", lambda: collectors.collect_python_surface(repo_root, py_files, scan_files)
    )
    old_identity_references = run(
        "old_identity_references", lambda: collectors.collect_old_identity_references(repo_root, scan_files)
    )
    structured_configuration = run(
        "structured_configuration", lambda: collectors.collect_structured_configuration(repo_root)
    )
    outputs_children = run("outputs_children", lambda: collectors.collect_outputs_children(repo_root))
    test_subtrees = run("test_subtrees", lambda: collectors.collect_test_subtrees(repo_root, scan_files))
    schema_identifiers = run(
        "schema_identifiers", lambda: collectors.collect_schema_identifiers(repo_root, scan_files)
    )
    environment = run("environment", lambda: collectors.collect_environment())

    complete = not omissions and not collection_failures

    provenance = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repository_commit": (git_prov or {}).get("repository_commit", "unknown"),
        "dirty_state": (git_prov or {}).get("dirty_state", {"is_dirty": False, "changed_paths": []}),
        "tool_versions": (git_prov or {}).get("tool_versions", {"python": "unknown", "git": "unknown"}),
        "command": command,
        "configuration": {
            "excluded_dir_names": sorted(collectors.EXCLUDED_DIR_NAMES),
            "excluded_dir_prefixes": list(collectors.EXCLUDED_DIR_PREFIXES),
            "excluded_dir_suffixes": list(collectors.EXCLUDED_DIR_SUFFIXES),
            "excluded_relative_prefixes": list(collectors.EXCLUDED_RELATIVE_PREFIXES),
            "text_extensions": sorted(collectors.TEXT_EXTENSIONS),
            "scan_file_count": len(scan_files),
            "python_file_count": len(py_files),
            "fail_collector": fail_collector or "",
        },
        "omissions": omissions,
        "collection_failures": collection_failures,
        "complete": complete,
    }

    document = {
        "inventory_version": "1.0",
        "schema": "schemas/repository_refactor_inventory.schema.v1.json",
        "provenance": provenance,
        "identities": identities if identities is not None else [],
        "directories": directories if directories is not None else [],
        "python_surface": python_surface if python_surface is not None else {
            "runtime_imports": [], "runtime_module_commands": [], "entry_points": [],
            "file_based_root_traversals": [], "absolute_checkout_paths": [],
        },
        "old_identity_references": old_identity_references if old_identity_references is not None else [],
        "structured_configuration": structured_configuration if structured_configuration is not None else [],
        "outputs_children": outputs_children if outputs_children is not None else [],
        "test_subtrees": test_subtrees if test_subtrees is not None else [],
        "schema_identifiers": schema_identifiers if schema_identifiers is not None else [],
        "environment": environment if environment is not None else {
            "python_version": "unknown", "platform": "unknown", "installed_packages": [],
        },
    }
    return document, complete


# ---------------------------------------------------------------------------
# Stable item identifiers shared between the machine and human reports (used
# by test 4 to prove the two reports describe the same inventory).


def compute_stable_ids(document: dict) -> dict[str, str]:
    ids: dict[str, str] = {}
    for item in document.get("identities", []):
        ids[f"identity:{item['identity']}"] = item["target_value"]
    for item in document.get("directories", []):
        ids[f"directory:{item['path']}"] = item["proposed_disposition"]
    ps = document.get("python_surface", {})
    for item in ps.get("runtime_imports", []):
        ids[f"import:{item['source_file']}:{item['line']}"] = item["statement"]
    for item in ps.get("runtime_module_commands", []):
        ids[f"modcmd:{item['source_file']}:{item['line']}"] = item["command"]
    for item in ps.get("entry_points", []):
        ids[f"entrypoint:{item['source_file']}:{item['kind']}:{item['target']}"] = item["target"]
    for item in ps.get("file_based_root_traversals", []):
        ids[f"traversal:{item['source_file']}:{item['line']}"] = item["expression"]
    for item in ps.get("absolute_checkout_paths", []):
        ids[f"abspath:{item['source_file']}:{item['line']}"] = item["text"]
    for item in document.get("old_identity_references", []):
        ids[f"oldref:{item['source_file']}:{item['line']}:{item['identity']}"] = item["text"]
    for item in document.get("structured_configuration", []):
        ids[f"config:{item['path']}"] = "present" if item["present"] else "absent"
    for item in document.get("outputs_children", []):
        ids[f"outputs:{item['path']}"] = item["proposed_disposition"]
    for item in document.get("test_subtrees", []):
        ids[f"testsubtree:{item['path']}"] = item["package_import_status"]
    for item in document.get("schema_identifiers", []):
        ids[f"schema:{item['path']}"] = item["id"]
    return ids


def render_human_report(document: dict) -> str:
    prov = document["provenance"]
    lines: list[str] = []
    lines.append("# Repository refactor inventory — human report")
    lines.append("")
    lines.append(f"- inventory_version: `{document['inventory_version']}`")
    lines.append(f"- schema: `{document['schema']}`")
    lines.append(f"- generated_at_utc: `{prov['generated_at_utc']}`")
    lines.append(f"- repository_commit: `{prov['repository_commit']}`")
    lines.append(f"- dirty: `{prov['dirty_state']['is_dirty']}` "
                 f"({len(prov['dirty_state']['changed_paths'])} changed path(s))")
    lines.append(f"- tool_versions: `{prov['tool_versions']}`")
    lines.append(f"- command: `{prov['command']}`")
    lines.append(f"- complete: `{prov['complete']}`")
    if prov["omissions"]:
        lines.append(f"- omissions: {len(prov['omissions'])} — "
                     + "; ".join(f"{o['collector']}: {o['reason']}" for o in prov["omissions"]))
    if prov["collection_failures"]:
        lines.append(f"- collection_failures: {len(prov['collection_failures'])} — "
                     + "; ".join(f"{c['collector']}: {c['error']}" for c in prov["collection_failures"]))
    lines.append("")

    lines.append("## Identities (spec v8 section 2)")
    lines.append("")
    lines.append("| identity | current value(s) | target |")
    lines.append("|---|---|---|")
    for item in document["identities"]:
        current = ", ".join(item["current_values"]) or "(none found)"
        lines.append(f"| {item['identity']} | {current} | {item['target_value']} |")
    lines.append("")

    lines.append("## Directories")
    lines.append("")
    lines.append("| path | tracked_state | lifecycle_class | disposition |")
    lines.append("|---|---|---|---|")
    for item in document["directories"]:
        lines.append(f"| {item['path']} | {item['tracked_state']} | {item['lifecycle_class']} | "
                     f"{item['proposed_disposition'][:100]} |")
    lines.append("")

    ps = document["python_surface"]
    lines.append("## Python surface")
    lines.append("")
    lines.append(f"- runtime_imports: {len(ps['runtime_imports'])}")
    lines.append(f"- runtime_module_commands: {len(ps['runtime_module_commands'])}")
    lines.append(f"- entry_points: {len(ps['entry_points'])}")
    lines.append(f"- file_based_root_traversals: {len(ps['file_based_root_traversals'])}")
    lines.append(f"- absolute_checkout_paths: {len(ps['absolute_checkout_paths'])}")
    lines.append("")

    lines.append("## Old identity references")
    lines.append("")
    by_identity: dict[str, int] = {}
    for item in document["old_identity_references"]:
        by_identity[item["identity"]] = by_identity.get(item["identity"], 0) + 1
    for identity, count in sorted(by_identity.items()):
        lines.append(f"- {identity}: {count} occurrence(s)")
    lines.append("")

    lines.append("## Structured configuration")
    lines.append("")
    for item in document["structured_configuration"]:
        lines.append(f"- {item['path']}: present={item['present']} — {item['role']}")
    lines.append("")

    lines.append(f"## outputs/ children: {len(document['outputs_children'])}")
    lines.append("")
    if not document["outputs_children"]:
        lines.append("outputs/ does not exist in this checkout at collection time "
                     "(gitignored runtime write boundary; empty between runs).")
    lines.append("")

    lines.append("## Test subtrees")
    lines.append("")
    for item in document["test_subtrees"]:
        lines.append(f"- {item['path']}: {item['package_import_status']} — {item['scope']}")
    lines.append("")

    lines.append(f"## Schema identifiers: {len(document['schema_identifiers'])} schema file(s)")
    lines.append("")

    env = document["environment"]
    lines.append("## Environment")
    lines.append("")
    lines.append(f"- python_version: {env['python_version']}")
    lines.append(f"- platform: {env['platform']}")
    lines.append(f"- installed_packages: {len(env['installed_packages'])}")
    lines.append("")

    lines.append("## Stable item identifier appendix (machine-comparable)")
    lines.append("")
    lines.append("Every row below is mechanically derived from the same `compute_stable_ids()` "
                 "function applied to the JSON report generated in the same run; a comparison "
                 "script must find the identical set of ids in both reports (test 4).")
    lines.append("")
    lines.append("```")
    for stable_id, disposition in sorted(compute_stable_ids(document).items()):
        # Every appendix row must be exactly one line: a multi-line import
        # statement's embedded newlines would otherwise appear as bare
        # continuation lines with no id, corrupting the id set a comparison
        # script recovers by splitting on tabs (test 4).
        flat_id = str(stable_id).replace("\n", " ").replace("\t", " ")
        flat_disposition = str(disposition).replace("\n", " ").replace("\t", " ")
        lines.append(f"{flat_id}\t{flat_disposition}")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def validate_document(document: dict, schema_path: Path) -> None:
    if jsonschema is None:
        raise RuntimeError("jsonschema is required to validate the inventory but is not importable")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(document)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--schema", type=Path, default=None,
                        help="defaults to <repo-root>/schemas/repository_refactor_inventory.schema.v1.json")
    parser.add_argument("--fail-collector", choices=COLLECTOR_NAMES, default=None,
                        help="deliberately make one collector unavailable (fault-injection test only)")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    schema_path = args.schema.resolve() if args.schema else repo_root / "schemas/repository_refactor_inventory.schema.v1.json"
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    command = "python3 tools/refactor_repo/inventory.py --repo-root <repo-root> --output-dir <output-dir>" \
        + (f" --fail-collector {args.fail_collector}" if args.fail_collector else "")

    document, complete = build_inventory(repo_root, command, args.fail_collector)

    try:
        validate_document(document, schema_path)
    except Exception as exc:  # noqa: BLE001
        print(f"INVENTORY BUG: generated document fails its own schema: {exc}", file=sys.stderr)
        return 1

    timestamp = document["provenance"]["generated_at_utc"].replace(":", "").replace("-", "")
    json_path = output_dir / f"repository_refactor_inventory.{timestamp}.v1.json"
    md_path = output_dir / f"repository_refactor_inventory.{timestamp}.v1.md"
    json_path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_human_report(document), encoding="utf-8")

    pip_inspect_path = output_dir / f"pip_inspect.{timestamp}.json"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "inspect"], capture_output=True, text=True, timeout=60,
        )
        pip_inspect_path.write_text(result.stdout, encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        pip_inspect_path.write_text(json.dumps({"error": f"{type(exc).__name__}: {exc}"}), encoding="utf-8")

    summary = {
        "complete": complete,
        "omissions": document["provenance"]["omissions"],
        "collection_failures": document["provenance"]["collection_failures"],
        "json_report": str(json_path),
        "human_report": str(md_path),
        "counts": {k: (len(v) if isinstance(v, list) else None) for k, v in document.items()
                   if k not in {"provenance", "python_surface", "environment"}},
    }
    print(json.dumps(summary, indent=2))

    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
