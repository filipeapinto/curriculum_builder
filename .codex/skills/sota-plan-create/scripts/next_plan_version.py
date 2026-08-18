#!/usr/bin/env python3
"""Print the next unused versioned plan path without creating it."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: next_plan_version.py PLAN_DIRECTORY PLAN_STEM EXTENSION", file=sys.stderr)
        return 2

    directory = Path(sys.argv[1])
    stem = sys.argv[2]
    extension = sys.argv[3].lstrip(".")
    if not stem or not extension:
        print("plan stem and extension must be nonempty", file=sys.stderr)
        return 2

    pattern = re.compile(rf"^{re.escape(stem)}\.v([1-9][0-9]*)\.{re.escape(extension)}$")
    versions = []
    if directory.exists():
        versions = [
            int(match.group(1))
            for path in directory.iterdir()
            if path.is_file() and (match := pattern.match(path.name))
        ]

    candidate = directory / f"{stem}.v{max(versions, default=0) + 1}.{extension}"
    if candidate.exists():
        print(f"refusing existing path: {candidate}", file=sys.stderr)
        return 1
    print(candidate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

