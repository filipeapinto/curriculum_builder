#!/usr/bin/env python3
"""Print the next unused version for an immutable issue-report series."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: next_issue_report_version.py <output-directory> <report-stem>", file=sys.stderr)
        return 2

    directory = Path(sys.argv[1])
    stem = sys.argv[2]
    if not directory.is_dir():
        print(f"output directory does not exist: {directory}", file=sys.stderr)
        return 2
    if not stem or Path(stem).name != stem:
        print("report-stem must be one filename stem without path separators", file=sys.stderr)
        return 2

    pattern = re.compile(rf"^{re.escape(stem)}\.v([1-9][0-9]*)\.html$")
    versions = [
        int(match.group(1))
        for path in directory.iterdir()
        if path.is_file() and (match := pattern.match(path.name))
    ]
    version = max(versions, default=0) + 1
    candidate = directory / f"{stem}.v{version}.html"
    if candidate.exists():
        print(f"refusing existing path: {candidate}", file=sys.stderr)
        return 1
    print(candidate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
