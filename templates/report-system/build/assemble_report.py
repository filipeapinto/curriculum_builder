#!/usr/bin/env python3
"""Assemble a standalone HTML report from versioned shared sources."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SYSTEM_ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = SYSTEM_ROOT / "components"
STYLES = SYSTEM_ROOT / "styles"
INCLUDE = re.compile(r"{{>\s*([a-z0-9-]+)\s*}}")


def shared_css() -> str:
    files = (STYLES / "report-tokens.v1.css", STYLES / "report-system.v1.css")
    return "\n\n".join(path.read_text(encoding="utf-8").rstrip() for path in files)


def expand_components(source: str) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        matches = sorted(COMPONENTS.glob(f"{name}.v*.html"))
        if len(matches) != 1:
            raise ValueError(f"component {name!r} resolved to {len(matches)} files")
        return matches[0].read_text(encoding="utf-8").rstrip()

    previous = None
    while source != previous:
        previous = source
        source = INCLUDE.sub(replace, source)
    if "{{>" in source:
        raise ValueError("unresolved component include")
    return source


def assemble(source_path: Path) -> str:
    source = source_path.read_text(encoding="utf-8")
    output = expand_components(source)
    output = output.replace("{{{REPORT_SYSTEM_CSS}}}", shared_css())
    if "{{{REPORT_SYSTEM_CSS}}}" in output:
        raise ValueError("shared CSS placeholder was not resolved")
    return output.rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--check", action="store_true", help="fail if output differs; do not write")
    args = parser.parse_args()
    rendered = assemble(args.source)
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"stale generated report: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
