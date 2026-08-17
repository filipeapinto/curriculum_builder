#!/usr/bin/env python3
"""Look at the render before delivering it.

    inspect_layout.py --svg <file.svg> [--report <report.json>] [--strict]

Static generators reproduce the same defects forever because none of them ever
reads its own output. This closes that loop mechanically: it measures the SVG
the renderer just wrote and reports overlapping text, microtype, text spilling
past its card, colliding edge labels, and a page whose proportions no one can
use. Exit 1 when a defect at `blocker` severity is present (or, with --strict,
at `warn` too).

Mechanical inspection is half the loop. It cannot tell you the picture is ugly,
only that it is broken — an agent still has to open the raster and look. What it
buys is that the boring, repeatable failures never reach the human reviewer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

TEXT_RE = re.compile(
    r'<text\b(?P<attrs>[^>]*)>(?P<body>.*?)</text>', re.S)
RECT_RE = re.compile(r'<rect\b(?P<attrs>[^>]*?)/?>')
SVG_RE = re.compile(r'<svg\b(?P<attrs>[^>]*)>')
ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')
TAG_RE = re.compile(r"<[^>]+>")

# Advance-width factors. Deliberately generous: an inspector that under-reports
# overlap is worse than useless, so it errs toward calling a near-miss a miss.
ADV = 0.545
ADV_BOLD = 0.585
MIN_FONT_PT = 6.8


@dataclass
class Defect:
    code: str
    severity: str
    detail: str
    where: str = ""


def _attrs(s: str) -> dict:
    return dict(ATTR_RE.findall(s))


def _f(d: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(str(d.get(key, default)).replace("px", ""))
    except ValueError:
        return default


@dataclass
class TextBox:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    size: float

    def overlaps(self, o: "TextBox", pad: float = 0.0) -> bool:
        return not (self.x1 + pad <= o.x0 or o.x1 + pad <= self.x0
                    or self.y1 + pad <= o.y0 or o.y1 + pad <= self.y0)


def _text_boxes(svg: str) -> list[TextBox]:
    boxes = []
    for m in TEXT_RE.finditer(svg):
        a = _attrs(m.group("attrs"))
        body = TAG_RE.sub("", m.group("body"))
        body = (body.replace("&amp;", "&").replace("&lt;", "<")
                    .replace("&gt;", ">").replace("&quot;", '"')
                    .replace("&#39;", "'").replace("&#x27;", "'")
                    .replace("&#215;", "\u00d7").replace("&#8617;", "\u21a9"))
        body = " ".join(body.split())
        if not body:
            continue
        size = _f(a, "font-size", 10.0)
        bold = str(a.get("font-weight", "")) in ("bold", "600", "700", "800")
        tracking = _f(a, "letter-spacing")
        w = len(body) * size * (ADV_BOLD if bold else ADV) + tracking * len(body)
        x = _f(a, "x")
        y = _f(a, "y")
        anchor = a.get("text-anchor", "start")
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        if "rotate(-90)" in m.group("attrs") or "rotate(90)" in m.group("attrs"):
            # A rotated rail caption occupies a tall, narrow box; measuring it
            # as if it were horizontal would report false collisions with the
            # whole left column.
            tm = re.search(r"translate\(([-\d.]+),([-\d.]+)\)", m.group("attrs"))
            cx, cy = (float(tm.group(1)), float(tm.group(2))) if tm else (x, y)
            boxes.append(TextBox(cx - size * 0.75, cy - w / 2,
                                 cx + size * 0.75, cy + w / 2, body, size))
            continue
        boxes.append(TextBox(x, y - size * 0.82, x + w, y + size * 0.24, body, size))
    return boxes


def inspect(svg_path: Path) -> tuple[list[Defect], dict]:
    svg = svg_path.read_text(encoding="utf-8")
    defects: list[Defect] = []

    m = SVG_RE.search(svg)
    if not m:
        return [Defect("no-svg-root", "blocker", "file has no <svg> root")], {}
    root = _attrs(m.group("attrs"))
    W, H = _f(root, "width"), _f(root, "height")
    metrics = {"width": W, "height": H,
               "aspect": round(W / H, 3) if H else 0.0}

    if H and not (0.35 <= W / H <= 3.2):
        defects.append(Defect(
            "page-proportion", "blocker",
            f"page is {W:.0f}x{H:.0f} (aspect {W/H:.2f}); a ribbon this extreme "
            f"cannot be read on a page or a screen"))

    boxes = _text_boxes(svg)
    metrics["text_runs"] = len(boxes)

    small = [b for b in boxes if b.size < MIN_FONT_PT]
    if small:
        defects.append(Defect(
            "microtype", "warn",
            f"{len(small)} text run(s) below {MIN_FONT_PT}pt — smallest "
            f"{min(b.size for b in small):.1f}pt",
            "; ".join(sorted({b.text[:28] for b in small})[:4])))

    # Overlapping text is the defect that most reliably makes a diagram look
    # amateur, and the one a generator never notices.
    overlaps = []
    for i, b in enumerate(boxes):
        for o in boxes[i + 1:]:
            if abs(b.y0 - o.y0) > 60:
                continue
            if b.overlaps(o, pad=-1.0):
                overlaps.append((b, o))
    metrics["text_overlaps"] = len(overlaps)
    if overlaps:
        sample = "; ".join(f"{b.text[:24]!r} x {o.text[:24]!r}"
                           for b, o in overlaps[:5])
        defects.append(Defect(
            "text-overlap", "blocker",
            f"{len(overlaps)} pair(s) of text runs overlap", sample))

    # Text escaping the page.
    off = [b for b in boxes if b.x0 < -2 or b.x1 > W + 2 or b.y0 < -2 or b.y1 > H + 2]
    if off:
        defects.append(Defect(
            "text-out-of-bounds", "blocker",
            f"{len(off)} text run(s) fall outside the canvas",
            "; ".join(sorted({b.text[:28] for b in off})[:4])))

    # Cards are the white rounded rects; text should stay inside the one it
    # belongs to. A title that spills its card is the classic truncation bug.
    cards = []
    for rm in RECT_RE.finditer(svg):
        a = _attrs(rm.group("attrs"))
        if _f(a, "rx") < 6:
            continue
        w, h = _f(a, "width"), _f(a, "height")
        if w < 120 or h < 40:
            continue
        cards.append((_f(a, "x"), _f(a, "y"), _f(a, "x") + w, _f(a, "y") + h))
    metrics["cards"] = len(cards)
    spills = 0
    for b in boxes:
        for (cx0, cy0, cx1, cy1) in cards:
            inside_v = cy0 <= b.y0 and b.y1 <= cy1
            starts_in = cx0 <= b.x0 <= cx1
            if inside_v and starts_in and b.x1 > cx1 - 2:
                spills += 1
                break
    if spills:
        defects.append(Defect(
            "text-spills-card", "warn",
            f"{spills} text run(s) reach or cross the right edge of their card"))

    truncated = [b for b in boxes if b.text.rstrip().endswith("…")]
    metrics["truncated_runs"] = len(truncated)
    if len(truncated) > max(6, len(boxes) * 0.12):
        defects.append(Defect(
            "over-truncated", "warn",
            f"{len(truncated)} text runs end in an ellipsis — the labels are "
            f"being cut rather than shortened"))

    if not defects:
        metrics["clean"] = True
    return defects, metrics


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--svg", required=True)
    ap.add_argument("--report", default=None)
    ap.add_argument("--strict", action="store_true",
                    help="treat `warn` as failing too")
    args = ap.parse_args(argv)

    path = Path(args.svg)
    if not path.is_file():
        print(f"inspect_layout: no such file: {path}", file=sys.stderr)
        return 2

    defects, metrics = inspect(path)
    worst = {"blocker": 2, "warn": 1}
    level = max((worst[d.severity] for d in defects), default=0)
    status = "clean" if level == 0 else ("warn" if level == 1 else "blocker")
    report = {"svg": str(path), "status": status,
              "metrics": metrics, "defects": [asdict(d) for d in defects]}
    text = json.dumps(report, indent=2) + "\n"
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(text, encoding="utf-8")
    print(text)
    if level == 2 or (args.strict and level >= 1):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
