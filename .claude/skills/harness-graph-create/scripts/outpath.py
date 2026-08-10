#!/usr/bin/env python3
"""Resolve the next free versioned output paths for a harness-graph render, so a
render is never overwritten and its PNG/spec/brief never drift to different
version numbers even though they live in different subfolders.

Every graph lives under one `visualizations/` folder beside the harness's own
source file, split into two subfolders so a reviewer can glance at just the
pictures or just the specs:

    <viz-dir>/pngs/<name>.v<N>.png
    <viz-dir>/prompts/<name>.v<N>.json
    <viz-dir>/prompts/<name>.v<N>.prompt.md

All three share one version number. Because they're split across two
directories, the version can't be found by listing just one folder — this
scans both `pngs/` and `prompts/` for the given `name` and takes the highest
version found across all three file types, so a version is never reused even
if (say) a PNG got deleted but its prompt.md didn't.

Usage:
    python3 outpath.py <viz-dir> <name>
        -> prints "<png-path> <json-path> <prompt-path>" to stdout, space-
           separated, and creates <viz-dir>/pngs/ and <viz-dir>/prompts/ if
           they don't exist yet (there is nothing to protect by deferring
           that — the version files themselves are never touched)

    python3 outpath.py <viz-dir> <name> --print-existing   # also list what was found, on stderr

Compose it in a shell script with `read`:
    read -r OUT_PNG OUT_JSON OUT_PROMPT <<< "$(python3 outpath.py plans/23_x/visualizations plan23.harness_graph)"
"""

import argparse
import re
import sys
from pathlib import Path

SUFFIXES = {"png": ".png", "json": ".json", "prompt": ".prompt.md"}


def highest_version(directory: Path, name: str, suffix: str) -> tuple[int, list[str]]:
    """Highest `.vN<suffix>` found for `name` in `directory` OR its `deprecated/`
    subfolder (0 if neither exists yet — nothing to protect against on a first
    run). Checking `deprecated/` too means moving a superseded version out of
    the way never frees up its version number for reuse."""
    pattern = re.compile(rf"^{re.escape(name)}\.v(\d+){re.escape(suffix)}$")
    highest = 0
    found = []
    for d in (directory, directory / "deprecated"):
        if not d.exists():
            continue
        for f in d.iterdir():
            m = pattern.match(f.name)
            if m:
                found.append(f"{d.name}/{f.name}" if d != directory else f.name)
                highest = max(highest, int(m.group(1)))
    return highest, found


def next_paths(viz_dir: Path, name: str) -> tuple[dict[str, Path], list[str]]:
    name = re.sub(r"\.v\d+$", "", name)  # tolerate a caller passing an already-versioned name
    pngs_dir = viz_dir / "pngs"
    prompts_dir = viz_dir / "prompts"

    found_all: list[str] = []
    highest = 0
    for kind, directory in (("png", pngs_dir), ("json", prompts_dir), ("prompt", prompts_dir)):
        h, found = highest_version(directory, name, SUFFIXES[kind])
        highest = max(highest, h)
        found_all += found

    pngs_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir.mkdir(parents=True, exist_ok=True)

    n = highest + 1
    return {
        "png": pngs_dir / f"{name}.v{n}{SUFFIXES['png']}",
        "json": prompts_dir / f"{name}.v{n}{SUFFIXES['json']}",
        "prompt": prompts_dir / f"{name}.v{n}{SUFFIXES['prompt']}",
    }, sorted(found_all)


def main():
    ap = argparse.ArgumentParser(
        description="Resolve the next free versioned {png,json,prompt.md} paths under "
                     "<viz-dir>/{pngs,prompts}/ (never overwrites)."
    )
    ap.add_argument("viz_dir", help="the harness's visualizations/ directory, "
                                     "e.g. plans/23_graph_eng_evol_01/visualizations")
    ap.add_argument("name", help="base name, no version/extension, e.g. plan23.harness_graph")
    ap.add_argument("--print-existing", action="store_true",
                     help="also report which versions already exist, on stderr")
    a = ap.parse_args()

    paths, found = next_paths(Path(a.viz_dir), a.name)
    if a.print_existing:
        msg = ", ".join(found) if found else "none"
        print(f"existing: {msg}", file=sys.stderr)
    print(f"{paths['png']} {paths['json']} {paths['prompt']}")


if __name__ == "__main__":
    main()
