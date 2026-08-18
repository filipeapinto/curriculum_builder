#!/usr/bin/env python3
"""Deterministic family-evidence inventory.

Walks a set of candidate component paths (skill directories, orchestrator files,
specifications, or arbitrary evidence paths) and reports what exists — file
digests, SKILL.md frontmatter, cross-references to sibling components, and
declared test/eval assets. It draws no conclusions about membership, topology,
or entry points: that synthesis belongs to the agent using this report, per
references/document-contract.md section 7. This script only tells the truth
about what is on disk.

Usage:
    python3 inspect_family.py <path> [<path> ...] [--json] [--out FILE]

Each <path> is typically a skill directory (e.g. work-lib/.claude/skills/graph-doc-grill)
but can be any file or directory relevant to the family (an orchestrator script,
an engineering spec, a shared-state directory).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
SKILL_NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
SKILL_DESC_RE = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)


def sha256_of(path: Path) -> str:
    try:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return f"sha256:{h.hexdigest()}"
    except OSError:
        return "unavailable"


def parse_skill_frontmatter(text: str) -> dict[str, Any]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    block = m.group(1)
    name_m = SKILL_NAME_RE.search(block)
    desc_m = SKILL_DESC_RE.search(block)
    return {
        "name": name_m.group(1).strip() if name_m else None,
        "description": desc_m.group(1).strip() if desc_m else None,
    }


def classify_file(rel: str) -> str:
    lower = rel.lower()
    base = Path(rel).name.lower()
    if base == "skill.md":
        return "skill_manifest"
    if "/references/" in f"/{lower}" or lower.startswith("references/"):
        return "reference"
    if "/scripts/" in f"/{lower}" or lower.startswith("scripts/"):
        return "script"
    if "/assets/" in f"/{lower}" or lower.startswith("assets/"):
        return "asset"
    if "/evals/" in f"/{lower}" or lower.startswith("evals/"):
        return "eval_asset"
    if base.startswith("blocked"):
        return "blocker_record"
    if base.startswith("superseded"):
        return "supersession_notice"
    if lower.endswith((".spec.html", ".spec.v1.html", ".spec.v2.html")) or ".spec." in lower:
        return "specification"
    if lower.endswith(".schema.json") or lower.endswith(".schema.v1.json"):
        return "schema"
    return "other"


def inventory_path(root: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "path": str(root),
        "exists": root.exists(),
    }
    if not root.exists():
        entry["error"] = "path does not exist"
        return entry

    files: list[dict[str, Any]] = []
    if root.is_file():
        candidates = [root]
        base_dir = root.parent
    else:
        candidates = sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts)
        base_dir = root

    skill_md_meta = None
    references_other_components: set[str] = set()

    for p in candidates:
        try:
            rel = str(p.relative_to(base_dir))
        except ValueError:
            rel = p.name
        kind = classify_file(rel)
        record: dict[str, Any] = {
            "relative_path": rel,
            "kind": kind,
            "bytes": p.stat().st_size,
            "digest": sha256_of(p),
        }
        if kind == "skill_manifest" or p.name == "SKILL.md":
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""
            meta = parse_skill_frontmatter(text)
            record["frontmatter"] = meta
            if p.name == "SKILL.md" and skill_md_meta is None:
                skill_md_meta = meta
            # Look for mentions of other skill-style identifiers (kebab-case,
            # 2+ hyphens) that could indicate a cross-family reference. This is
            # a *signal* for the agent to verify, not proof of membership.
            for token in re.findall(r"\b[a-z0-9]+(?:-[a-z0-9]+){2,}\b", text):
                if token != root.name:
                    references_other_components.add(token)
        files.append(record)

    entry["is_directory"] = root.is_dir()
    entry["skill_manifest"] = skill_md_meta
    entry["file_count"] = len(files)
    entry["files"] = files
    entry["referenced_identifiers"] = sorted(references_other_components)
    entry["has_evals"] = any(f["kind"] == "eval_asset" for f in files)
    entry["has_scripts"] = any(f["kind"] == "script" for f in files)
    entry["has_blocker_record"] = any(f["kind"] == "blocker_record" for f in files)
    entry["has_supersession_notice"] = any(f["kind"] == "supersession_notice" for f in files)
    return entry


def cross_reference(inventories: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Report, for each input path's skill name, which other input paths' names
    it textually references. Purely observational — membership is an agent
    decision per document-contract.md section 7, not something this script
    should assert.
    """
    names = {}
    for inv in inventories:
        meta = inv.get("skill_manifest") or {}
        name = meta.get("name")
        if name:
            names[name] = inv["path"]

    result: dict[str, list[str]] = {}
    for inv in inventories:
        meta = inv.get("skill_manifest") or {}
        name = meta.get("name")
        if not name:
            continue
        refs = [n for n in inv.get("referenced_identifiers", []) if n in names and n != name]
        if refs:
            result[name] = sorted(refs)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Component paths to inventory")
    parser.add_argument("--out", help="Write JSON report to this file instead of stdout")
    args = parser.parse_args(argv)

    inventories = [inventory_path(Path(p)) for p in args.paths]
    report = {
        "tool": "inspect_family.py",
        "input_count": len(args.paths),
        "components": inventories,
        "textual_cross_references": cross_reference(inventories),
        "notes": [
            "textual_cross_references is a signal, not proof of membership — verify",
            "each pair against an orchestrator relationship, dependency/handoff, common",
            "specification, shared-state contract, or explicit user declaration before",
            "admitting it (document-contract.md section 7).",
        ],
    }

    text = json.dumps(report, indent=2, sort_keys=False)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)

    missing = [c["path"] for c in inventories if not c.get("exists")]
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
