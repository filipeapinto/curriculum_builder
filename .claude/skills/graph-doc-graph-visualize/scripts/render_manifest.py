#!/usr/bin/env python3
"""Render a compiled workflow manifest to a diagram.

    render_manifest.py --manifest <in.json> --out <out.svg|out.png>
                       [--backend studio|graphviz|d2] [--detail compact|standard|full]
                       [--title TEXT] [--keep-source] [--status-path PATH]

Exit 0 on success with the artifact at --out. Exit non-zero on failure, with a
status record at <out>.failure.json (or --status-path) naming the stage and the
reason. See SKILL.md `## Machine contract` for A1–A7.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import backend_d2  # noqa: E402
import backend_dot  # noqa: E402
import backend_studio  # noqa: E402
import manifest_model  # noqa: E402

BACKENDS = ("studio", "graphviz", "d2")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class Failure(Exception):
    def __init__(self, stage: str, reason: str):
        super().__init__(reason)
        self.stage, self.reason = stage, reason


def _fail(out: Path, status_path: Path | None, stage: str, reason: str) -> int:
    rec = {"status": "failed", "stage": stage, "reason": reason,
           "output_path": str(out)}
    target = status_path or Path(str(out) + ".failure.json")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass
    print(f"[graph-doc-graph-visualize] FAILED at {stage}: {reason}", file=sys.stderr)
    print(f"[graph-doc-graph-visualize] status record: {target}", file=sys.stderr)
    return 2


def _run(cmd: list[str], stage: str) -> None:
    exe = shutil.which(cmd[0])
    if not exe:
        raise Failure(stage, f"required binary `{cmd[0]}` is not on PATH")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout).strip().splitlines()[-3:]
        raise Failure(stage, f"`{cmd[0]}` exited {proc.returncode}: {' / '.join(tail)}")


def _svg_to_png(svg: Path, png: Path, scale: float) -> None:
    """SVG is the native artifact. PNG is a conversion, and every converter here
    is a local process — no rasteriser in this chain touches the network."""
    if shutil.which("rsvg-convert"):
        _run(["rsvg-convert", "-z", str(scale), str(svg), "-o", str(png)], "raster")
        return
    if shutil.which("inkscape"):
        _run(["inkscape", str(svg), "--export-type=png",
              f"--export-filename={png}", f"--export-dpi={96*scale:.0f}"], "raster")
        return
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(url=str(svg), write_to=str(png), scale=scale)
        return
    except ImportError:
        pass
    raise Failure("raster", "no SVG rasteriser found — install rsvg-convert "
                            "(`brew install librsvg`), inkscape, or the cairosvg "
                            "Python package, or ask for --out <name>.svg instead")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--manifest", required=True,
                    help="path to a compiled workflow manifest JSON (A1)")
    ap.add_argument("--out", required=True,
                    help="exact output path; .svg or .png decides the format (A2)")
    ap.add_argument("--backend", default="studio", choices=BACKENDS)
    ap.add_argument("--detail", default="standard",
                    choices=("compact", "standard", "full"))
    ap.add_argument("--title", default="Document-creation workflow graph")
    ap.add_argument("--subtitle", default=None)
    ap.add_argument("--scale", type=float, default=1.5,
                    help="raster scale when --out is .png")
    ap.add_argument("--d2-engine", default="elk", choices=("elk", "dagre", "tala"))
    ap.add_argument("--keep-source", action="store_true",
                    help="also write the intermediate .dot/.d2/.svg beside --out")
    ap.add_argument("--status-path", default=None,
                    help="where the failure record goes (default <out>.failure.json)")
    args = ap.parse_args(argv)

    out = Path(args.out)
    status_path = Path(args.status_path) if args.status_path else None
    src = Path(args.manifest)

    try:
        if not src.is_file():
            raise Failure("input", f"manifest not found: {src}")
        try:
            g = manifest_model.load(src)
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            raise Failure("input", f"manifest is not a readable workflow manifest: {exc}")
        if not g.nodes:
            raise Failure("input", "manifest contains no nodes")

        suffix = out.suffix.lower()
        if suffix not in (".svg", ".png"):
            raise Failure("input", f"--out must end in .svg or .png, got `{suffix}`")
        out.parent.mkdir(parents=True, exist_ok=True)

        c = g.counts()
        subtitle = args.subtitle if args.subtitle is not None else (
            f'{g.run_id}  ·  {c["nodes"]} nodes, {c["edges"]} edges  ·  '
            f'{c["repair"]} repair routes  ·  {g.execution_shape}'
        )

        # Intermediates live in a scratch directory unless the caller asked to
        # keep them. Deriving them from --out would let a PNG render clobber an
        # unrelated `<stem>.svg` sitting beside it, which A2 forbids.
        scratch = Path(tempfile.mkdtemp(prefix="graph-doc-graph-visualize-"))
        work = out.with_suffix("") if args.keep_source else (scratch / out.stem)
        try:
            if args.backend == "studio":
                svg_text = backend_studio.emit(g, args.detail, args.title, subtitle)
                svg_path = out if suffix == ".svg" else Path(str(work) + ".svg")
                svg_path.write_text(svg_text, encoding="utf-8")
            elif args.backend == "graphviz":
                dot_path = Path(str(work) + ".dot")
                dot_path.write_text(
                    backend_dot.emit(g, args.detail, args.title, subtitle),
                    encoding="utf-8")
                svg_path = out if suffix == ".svg" else Path(str(work) + ".svg")
                _run(["dot", "-Tsvg", str(dot_path), "-o", str(svg_path)], "layout")
            else:
                d2_path = Path(str(work) + ".d2")
                d2_path.write_text(
                    backend_d2.emit(g, args.detail, args.title, args.d2_engine),
                    encoding="utf-8")
                svg_path = out if suffix == ".svg" else Path(str(work) + ".svg")
                _run(["d2", "--layout", args.d2_engine, str(d2_path),
                      str(svg_path)], "layout")

            if suffix == ".png":
                _svg_to_png(svg_path, out, args.scale)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

        # A3: prove the artifact rather than trusting the exit code above.
        if not out.is_file() or out.stat().st_size == 0:
            raise Failure("verify", f"no non-empty artifact at {out}")
        blob = out.read_bytes()
        if suffix == ".png":
            if not blob.startswith(PNG_MAGIC):
                raise Failure("verify", f"{out} is not a PNG (bad signature)")
        else:
            head = blob[:4096].decode("utf-8", "replace")
            if "<svg" not in head:
                raise Failure("verify", f"{out} does not contain an <svg> root")
            if b"</svg>" not in blob[-2048:]:
                raise Failure("verify", f"{out} is a truncated SVG")

        stale = status_path or Path(str(out) + ".failure.json")
        stale.unlink(missing_ok=True)
        print(f"[graph-doc-graph-visualize] OK -> {out} "
              f"({args.backend}, {args.detail}, {len(blob)} bytes)")
        return 0

    except Failure as f:
        return _fail(out, status_path, f.stage, f.reason)
    except Exception as exc:  # noqa: BLE001 - any crash must still signal A4
        return _fail(out, status_path, "internal", f"{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
