#!/usr/bin/env python3
"""Regenerate the Markdown family slug/version/generator index."""
from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


class ModelExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.capturing = False
        self.blocks: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "script" and values.get("type") == "application/json" and values.get("id") == "family-model":
            self.capturing = True
            self.blocks.append([])

    def handle_data(self, data: str) -> None:
        if self.capturing:
            self.blocks[-1].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.capturing = False


def read_model(path: Path) -> dict[str, Any]:
    parser = ModelExtractor()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    if len(parser.blocks) != 1:
        raise ValueError("expected exactly one embedded family-model block")
    model = json.loads("".join(parser.blocks[0]))
    version = model.get("assurance", {}).get("version")
    if not isinstance(version, int) or version < 1:
        raise ValueError("assurance.version must be a positive integer")
    return model


def generator_type(model: dict[str, Any]) -> str:
    agent = model.get("assurance", {}).get("generator", {}).get("agent", "")
    if str(agent).lower() in {"claude", "codex"}:
        return str(agent).lower()
    source_paths = [str(item.get("path", "")) for item in model.get("sources", [])]
    if any("/.codex/skills/skill-family-doc-create/" in f"/{path}" for path in source_paths):
        return "codex"
    if any("/.claude/skills/skill-family-doc-create/" in f"/{path}" for path in source_paths):
        return "claude"
    raise ValueError("generator type is neither claude nor codex")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("families_root", help="Directory containing family subdirectories")
    args = parser.parse_args(argv)
    root = Path(args.families_root)
    errors: list[str] = []
    families: list[tuple[str, int, str]] = []

    candidates: dict[str, list[tuple[int, Path, dict[str, Any]]]] = {}
    versioned_guides = sorted(root.glob("*/*-guide.v*.html"))
    versioned_dirs = {guide.parent for guide in versioned_guides}
    legacy_guides = [
        guide for guide in sorted(root.glob("*/family-guide.html"))
        if guide.parent not in versioned_dirs
    ]
    for guide in versioned_guides + legacy_guides:
        try:
            model = read_model(guide)
            family = model.get("family", {})
            assurance = model.get("assurance", {})
            slug = str(family.get("slug") or guide.parent.name)
            expected = f"{slug}-guide.v{assurance['version']}.html"
            if guide.name != "family-guide.html" and guide.name != expected:
                raise ValueError(f"filename/version mismatch: expected {expected}")
            candidates.setdefault(slug, []).append((assurance["version"], guide, model))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{guide}: {exc}")

    for slug, versions in sorted(candidates.items()):
        seen = [item[0] for item in versions]
        if len(seen) != len(set(seen)):
            errors.append(f"{slug}: duplicate guide version")
            continue
        version, _guide, model = max(versions, key=lambda item: item[0])
        families.append((slug, version, generator_type(model)))

    if errors:
        print(json.dumps({"updated": False, "errors": errors}, indent=2))
        return 1

    root.mkdir(parents=True, exist_ok=True)
    output = root / "index.md"
    lines = ["# Skill families", "", "| Slug | Version | Type |", "|---|---:|---|"]
    lines.extend(f"| `{slug}` | v{version} | {kind} |" for slug, version, kind in families)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"updated": True, "index": str(output), "families": len(families)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
