#!/usr/bin/env python3
"""Build a source register for a system-documentation run.

The register answers one question a reader will ask months from now: *what
exactly was inspected, and at which version?* Doing this in code rather than in
prose costs no model tokens and cannot drift from the filesystem.

Usage:
    python3 source_register.py PATH_OR_GLOB [PATH_OR_GLOB ...]
        [--root DIR] [--scope TEXT] [--json OUT.json] [--md OUT.md]
        [--merge PRIOR.json]

Emits a markdown table on stdout by default. With --merge, compares against a
prior register and marks each row added / changed / unchanged / missing, which
is what update mode needs to decide which sections to revisit.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob as _glob
import hashlib
import json
import os
import subprocess
import sys

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache",
             ".pytest_cache", "dist", "build", ".next", ".terraform"}
MAX_BYTES = 8 * 1024 * 1024


def _git(root: str, *args: str) -> str:
    try:
        out = subprocess.run(["git", "-C", root, *args], capture_output=True,
                             text=True, timeout=15)
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


def _expand(patterns: list[str], root: str) -> list[str]:
    found: list[str] = []
    for pat in patterns:
        p = pat if os.path.isabs(pat) else os.path.join(root, pat)
        if os.path.isdir(p):
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                found.extend(os.path.join(dirpath, f) for f in filenames)
            continue
        matches = _glob.glob(p, recursive=True)
        if matches:
            found.extend(m for m in matches if os.path.isfile(m))
        elif os.path.isfile(p):
            found.append(p)
        else:
            found.append("\0MISSING\0" + p)
    seen, ordered = set(), []
    for f in found:
        if f not in seen:
            seen.add(f)
            ordered.append(f)
    return ordered


def _digest(path: str) -> tuple[str, int, int]:
    h = hashlib.sha256()
    size = os.path.getsize(path)
    lines = 0
    with open(path, "rb") as fh:
        while chunk := fh.read(65536):
            h.update(chunk)
            lines += chunk.count(b"\n")
    return h.hexdigest()[:12], size, lines


def build(patterns: list[str], root: str, scope: str) -> dict:
    root = os.path.abspath(root)
    head = _git(root, "rev-parse", "--short", "HEAD")
    dirty = bool(_git(root, "status", "--porcelain"))
    rows = []
    for path in _expand(patterns, root):
        if path.startswith("\0MISSING\0"):
            rows.append({"path": os.path.relpath(path[9:], root), "status": "missing",
                         "note": "pattern matched nothing; record as an evidence gap"})
            continue
        rel = os.path.relpath(path, root)
        try:
            if os.path.getsize(path) > MAX_BYTES:
                rows.append({"path": rel, "status": "skipped",
                             "note": f"larger than {MAX_BYTES} bytes; inspect explicitly"})
                continue
            sha, size, lines = _digest(path)
        except OSError as exc:
            rows.append({"path": rel, "status": "unreadable", "note": str(exc)})
            continue
        mtime = _dt.datetime.fromtimestamp(
            os.path.getmtime(path), _dt.timezone.utc).isoformat(timespec="seconds")
        rows.append({"path": rel, "status": "inspected", "sha256_12": sha,
                     "bytes": size, "lines": lines, "mtime_utc": mtime,
                     "last_commit": _git(root, "log", "-1", "--format=%h %ad",
                                         "--date=short", "--", rel)})
    return {
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "root": root,
        "git_head": head or "(not a git repository)",
        "worktree_dirty": dirty,
        "scope": scope,
        "sources": rows,
    }


def merge(current: dict, prior_path: str) -> dict:
    with open(prior_path) as fh:
        prior = json.load(fh)
    old = {r["path"]: r for r in prior.get("sources", [])}
    for row in current["sources"]:
        was = old.pop(row["path"], None)
        if was is None:
            row["change"] = "added"
        elif was.get("sha256_12") != row.get("sha256_12"):
            row["change"] = "changed"
        else:
            row["change"] = "unchanged"
    for path, row in old.items():
        row["change"] = "gone"
        row["status"] = "missing"
        current["sources"].append(row)
    current["compared_against"] = {"path": prior_path,
                                   "git_head": prior.get("git_head"),
                                   "generated_utc": prior.get("generated_utc")}
    return current


def to_md(reg: dict) -> str:
    has_change = any("change" in r for r in reg["sources"])
    head = ["Source", "Version / last commit", "Freshness (UTC)", "Scope inspected"]
    if has_change:
        head.insert(1, "Change")
    out = [f"<!-- register generated {reg['generated_utc']} at "
           f"{reg['git_head']}{' (dirty worktree)' if reg['worktree_dirty'] else ''} -->",
           "", "| " + " | ".join(head) + " |",
           "|" + "|".join(["---"] * len(head)) + "|"]
    for r in sorted(reg["sources"], key=lambda x: x["path"]):
        if r["status"] != "inspected":
            ver, fresh = f"_{r['status']}_", r.get("note", "")
        else:
            ver = r.get("last_commit") or f"sha256:{r['sha256_12']}"
            fresh = r.get("mtime_utc", "")
        cells = [f"`{r['path']}`", ver, fresh, reg["scope"]]
        if has_change:
            cells.insert(1, r.get("change", "—"))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("patterns", nargs="+")
    ap.add_argument("--root", default=".")
    ap.add_argument("--scope", default="full file")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--md", dest="md_out")
    ap.add_argument("--merge", dest="prior")
    args = ap.parse_args()

    reg = build(args.patterns, args.root, args.scope)
    if args.prior:
        reg = merge(reg, args.prior)
    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w") as fh:
            json.dump(reg, fh, indent=2)
    md = to_md(reg)
    if args.md_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.md_out)), exist_ok=True)
        with open(args.md_out, "w") as fh:
            fh.write(md + "\n")
    print(md)
    missing = [r["path"] for r in reg["sources"] if r["status"] == "missing"]
    if missing:
        print(f"\n{len(missing)} pattern(s) resolved to nothing — document these as "
              f"evidence gaps, do not quietly drop them: {', '.join(missing[:8])}",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
