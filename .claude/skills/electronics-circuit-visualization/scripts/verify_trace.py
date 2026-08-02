#!/usr/bin/env python3
"""Audit a rendered circuit visual: does every element on the page come from the input?

Three checks, run against the compiled artefacts rather than against the renderer's
intentions, so the audit stays honest even if the renderer changes:

  1. resolves   — every data element's JSON pointer resolves in the input document, and
                  the string on the page is that field's value.
  2. no strays  — every text literal in the .typ appears in the trace. A string that
                  reached the page without a trace entry is an unevidenced claim.
  3. chrome     — every fixed label is in the renderer's closed CHROME vocabulary.

Exit code 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_circuit import CHROME, FONT, jstr  # noqa: E402

STR_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')
NON_TEXT = {FONT, "bold", "regular", "medium", "light", "dashed", "png"}
HEX_RE = re.compile(r"^#[0-9a-fA-F]{3,8}$")


def unesc(s: str) -> str:
    return s.replace('\\"', '"').replace("\\\\", "\\")


def resolve(root, pointer: str):
    node = root
    for part in [p for p in pointer.split("/") if p != ""]:
        if isinstance(node, list):
            try:
                node = node[int(part)]
            except (ValueError, IndexError):
                return (False, None)
        elif isinstance(node, dict):
            if part not in node:
                return (False, None)
            node = node[part]
        else:
            return (False, None)
    return (True, node)


def all_keys(node) -> set[str]:
    if isinstance(node, dict):
        return set(node) | {k for v in node.values() for k in all_keys(v)}
    if isinstance(node, list):
        return {k for v in node for k in all_keys(v)}
    return set()


def flatten(node) -> list[str]:
    """Every scalar reachable under a node, as it would be rendered."""
    if isinstance(node, dict):
        return [s for v in node.values() for s in flatten(v)]
    if isinstance(node, list):
        return [s for v in node for s in flatten(v)]
    return [jstr(node)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--trace", required=True, type=Path)
    ap.add_argument("--typ", required=True, type=Path)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    root = json.loads(args.input.read_text())
    trace = json.loads(args.trace.read_text())
    typ = args.typ.read_text()
    elements = trace["elements"]

    failures: list[str] = []
    checked = 0

    for el in elements:
        if el["kind"] != "data":
            continue
        checked += 1
        ok, node = resolve(root, el["pointer"])
        if not ok:
            failures.append(f"pointer does not resolve: {el['pointer']} (text {el['text']!r})")
            continue
        page_text = el["text"]
        candidates = flatten(node)
        exact = page_text in candidates
        # composed cells (e.g. "12 V" from absolute_max + unit) and 1-based step numbers
        composed = any(page_text in c or c in page_text for c in candidates if c)
        index_badge = page_text.isdigit() and el["pointer"].rstrip("/").split("/")[-1].isdigit() \
            and int(page_text) == int(el["pointer"].rstrip("/").split("/")[-1]) + 1
        if not (exact or composed or index_badge):
            failures.append(
                f"page text not found in the field it cites: {el['pointer']} "
                f"page={page_text!r} data={candidates[:3]!r}"
            )

    traced_texts = {el["text"] for el in elements}
    strays = []
    for raw in STR_RE.findall(typ):
        s = unesc(raw)
        if s in NON_TEXT or HEX_RE.match(s) or s == "":
            continue
        if s not in traced_texts:
            strays.append(s)
    for s in sorted(set(strays)):
        failures.append(f"string on the page with no trace entry: {s!r}")

    for el in elements:
        if el["kind"] == "chrome" and el["text"] not in CHROME:
            failures.append(f"fixed label outside the closed vocabulary: {el['text']!r}")

    keys = all_keys(root)
    for el in elements:
        if el["kind"] != "field_label":
            continue
        derived = el["field"].replace("_", " ")
        if el["text"] != derived:
            failures.append(
                f"field caption is not its own field name: shown {el['text']!r}, "
                f"field {el['field']!r}"
            )
        elif el["field"] not in keys:
            failures.append(f"field caption names a field the input does not have: {el['field']!r}")

    data_n = sum(1 for e in elements if e["kind"] == "data")
    chrome_n = sum(1 for e in elements if e["kind"] == "chrome")
    field_n = sum(1 for e in elements if e["kind"] == "field_label")
    prov_n = sum(1 for e in elements if e["kind"] == "provenance")

    if failures:
        print("FAIL")
        for f in failures:
            print(f"  - {f}")
        print(f"\n{len(failures)} problem(s); {checked} data element(s) checked")
        return 1

    if not args.quiet:
        print("PASS")
        print(f"  {data_n} data elements, all resolving to fields in {args.input.name}")
        print(f"  {chrome_n} fixed labels, all in the closed vocabulary")
        print(f"  {field_n} field captions, each naming its own field in {args.input.name}")
        print(f"  {prov_n} provenance line(s)")
        print("  0 untraced strings in the typst source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
