#!/usr/bin/env python3
"""Compile a concept diagram and check the things a reader cannot check for themselves.

This script says nothing about whether the explanation on the page is any good --
that is not mechanically knowable, and it is the one part of this job you cannot
delegate. What it does check is the class of failure that is invisible in the
source and obvious in print: the page silently split in two, the sheet that came
out portrait, an asset pulled off the network, a font that will not exist on the
machine that opens it, or a page that is almost entirely blank because a block
collapsed.

    python3 scripts/build_diagram.py <file>.typ [--out <file>.png] [--ppi 200]
"""

from __future__ import annotations

import argparse
import re
import struct
import subprocess
import sys
from pathlib import Path

NETWORK = re.compile(r"https?://", re.IGNORECASE)
ALLOWED_FONTS = {"Helvetica", "Helvetica Neue"}
FONT_DECL = re.compile(r'font\s*:\s*"([^"]+)"')


def fail(msg: str) -> None:
    print(f"FAIL  {msg}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--ppi", type=int, default=200)
    ap.add_argument("--min-width", type=int, default=2000)
    args = ap.parse_args()

    src: Path = args.source
    if not src.exists():
        fail(f"no such source file: {src}")
        return 2
    out: Path = args.out or src.with_suffix(".png")

    text = src.read_text(encoding="utf-8")
    problems: list[str] = []

    # Typst resolves absolute paths against its own project root, so a diagram
    # can only import the house style if a copy sits beside it. Keeping that copy
    # next to the source is also what makes the .typ still compile on someone
    # else's machine a year from now.
    if 'import "house.typ"' in text:
        beside = src.parent / "house.typ"
        canonical = Path(__file__).resolve().parent.parent / "assets" / "house.typ"
        if not beside.exists() or beside.read_text(encoding="utf-8") != canonical.read_text(encoding="utf-8"):
            beside.write_text(canonical.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"      copied house style to {beside}")

    # Sources are read locally so the page renders the same in a year and on a
    # machine with no network. A remote asset is a diagram with an expiry date.
    for hit in NETWORK.findall(text):
        problems.append(f"source references the network ({hit}...); inline the content instead")

    bad_fonts = {f for f in FONT_DECL.findall(text) if f not in ALLOWED_FONTS}
    if bad_fonts:
        problems.append(
            f"non-system font(s) {sorted(bad_fonts)}; use Helvetica so the file opens identically everywhere"
        )

    if problems:
        for p in problems:
            fail(p)
        return 2

    cmd = ["typst", "compile", "--format", "png", "--ppi", str(args.ppi), str(src), str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stderr = proc.stderr.strip()

    if proc.returncode != 0:
        if "multiple images" in stderr or "multiple pages" in stderr:
            fail(
                "the diagram spilled onto a second page. A concept diagram is one sheet by "
                "definition -- cut content or shrink a band rather than letting it wrap."
            )
        else:
            fail("typst failed to compile:")
        print(stderr, file=sys.stderr)
        return 2

    if stderr:
        print("typst warnings:", file=sys.stderr)
        print(stderr, file=sys.stderr)

    width, height = png_size(out)
    if width is None:
        fail(f"{out} is not a readable PNG")
        return 2

    if height >= width:
        fail(f"page is {width}x{height} -- portrait or square; these diagrams are landscape")
        return 2
    if width < args.min_width:
        fail(f"page is only {width}px wide; it will not stay legible in print")
        return 2

    coverage = ink_coverage(out)
    cov_note = ""
    if coverage is not None:
        cov_note = f"  ink {coverage:.1%}"
        if coverage < 0.005:
            fail(f"the page is {1 - coverage:.1%} blank -- something did not render")
            return 2

    print(f"OK    {out}  {width}x{height}px @ {args.ppi}ppi  landscape  white{cov_note}")
    print("      Now open the PNG and read it. Overlapping labels, a box that clipped its")
    print("      own text, and an explanation that does not land are all invisible here.")
    return 0


def png_size(path: Path) -> tuple[int | None, int | None]:
    with path.open("rb") as fh:
        head = fh.read(24)
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return None, None
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def ink_coverage(path: Path) -> float | None:
    try:
        from PIL import Image
    except ImportError:
        return None
    with Image.open(path) as im:
        pixels = im.convert("L").resize((320, 240)).tobytes()
    return sum(1 for p in pixels if p < 245) / len(pixels)


if __name__ == "__main__":
    sys.exit(main())
