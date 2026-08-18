#!/usr/bin/env python3
"""Structural, accessibility, and coverage checks for a family-guide.html.

This script never judges prose quality — that is what stage 6's independent
content QA is for (references/document-contract.md, spec section 5 "Render"
and "Validate and inspect"). It only checks things that are objectively true
or false:

  - Standalone: no external stylesheet/script/image/iframe references (the
    file must open with no network access).
  - Required sections present (ids from assets/family-guide.template.html).
  - Heading hierarchy doesn't skip levels in a way that breaks navigation.
  - Every <img> has alt text; every <table> has <thead> and <tbody>.
  - Every in-page nav link (href="#...") resolves to an existing id.
  - The embedded family-model's components[] each appear (by id or name) in
    the component-reference table — catches an inventory the prose
    forgot to mention, or a table row invented that isn't in the model.
  - A quality-and-evidence section exists and uses only the controlled
    status vocabulary, never a bare "passed"/"failed" string as a status.

Usage:
    python3 validate_family_html.py <family-guide.html>

Exit code 0 = all checks pass, 1 = one or more failures (printed as JSON).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

REQUIRED_SECTION_IDS = [
    "overview",
    "system-context",
    "quick-start",
    "runtime-scenarios",
    "component-reference",
    "artifact-state-model",
    "failure-recovery",
    "requirements-constraints",
    "quality-evidence",
    "decisions-drift-risks",
    "version-provenance",
]

CONTROLLED_STATUSES = {
    "NOT_RUN", "NO_EVIDENCE_FOUND", "PARTIAL", "PASS", "FAIL", "BLOCKED", "NOT_APPLICABLE",
}

EXTERNAL_REF_RE = re.compile(
    r'\b(?:src|href)\s*=\s*["\'](https?:)?//[^"\']+["\']',
    re.IGNORECASE,
)


class StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.headings: list[tuple[int, str]] = []
        self.section_ids: set[str] = set()
        self.imgs_missing_alt = 0
        self.tables: list[dict[str, bool]] = []
        self._table_stack: list[dict[str, bool]] = []
        self.hrefs_internal: list[str] = []
        self.script_srcs: list[str] = []
        self.link_hrefs: list[str] = []
        self._heading_stack_min = 6

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = dict(attrs)
        if "id" in attrs_d and attrs_d["id"]:
            self.ids.add(attrs_d["id"])
            if tag == "section":
                self.section_ids.add(attrs_d["id"])
        if re.match(r"^h[1-6]$", tag):
            level = int(tag[1])
            self.headings.append((level, attrs_d.get("id", "")))
        if tag == "img" and not attrs_d.get("alt"):
            self.imgs_missing_alt += 1
        if tag == "a" and attrs_d.get("href", "").startswith("#"):
            self.hrefs_internal.append(attrs_d["href"][1:])
        if tag == "script" and attrs_d.get("src"):
            self.script_srcs.append(attrs_d["src"])
        if tag == "link" and attrs_d.get("href"):
            self.link_hrefs.append(attrs_d["href"])
        if tag == "table":
            self._table_stack.append({"thead": False, "tbody": False})
        if tag == "thead" and self._table_stack:
            self._table_stack[-1]["thead"] = True
        if tag == "tbody" and self._table_stack:
            self._table_stack[-1]["tbody"] = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self._table_stack:
            self.tables.append(self._table_stack.pop())


def check_standalone(html: str) -> list[str]:
    errors = []
    for m in EXTERNAL_REF_RE.finditer(html):
        errors.append(f"external resource reference found (not standalone): {m.group(0)}")
    if re.search(r"<link[^>]+rel=[\"']stylesheet[\"']", html, re.IGNORECASE):
        errors.append("external <link rel=\"stylesheet\"> found; CSS must be embedded")
    return errors


def check_headings(headings: list[tuple[int, str]]) -> list[str]:
    errors = []
    if not headings:
        return ["document has no headings"]
    if headings[0][0] != 1:
        errors.append(f"first heading is h{headings[0][0]}, expected h1")
    prev = headings[0][0]
    for level, _id in headings[1:]:
        if level > prev + 1:
            errors.append(f"heading level jumps from h{prev} to h{level} (skips a level)")
        prev = level
    return errors


def check_tables(tables: list[dict[str, bool]]) -> list[str]:
    errors = []
    for i, t in enumerate(tables):
        if not t["thead"]:
            errors.append(f"table #{i + 1} missing <thead>")
        if not t["tbody"]:
            errors.append(f"table #{i + 1} missing <tbody>")
    return errors


def check_internal_links(hrefs: list[str], ids: set[str]) -> list[str]:
    errors = []
    for target in hrefs:
        if target and target not in ids:
            errors.append(f'in-page link href="#{target}" has no matching id')
    return errors


def check_required_sections(section_ids: set[str]) -> list[str]:
    missing = [s for s in REQUIRED_SECTION_IDS if s not in section_ids]
    return [f"missing required section id: {s}" for s in missing]


def check_required_section_order(html: str) -> list[str]:
    positions = []
    for section_id in REQUIRED_SECTION_IDS:
        match = re.search(rf'<section[^>]+id=["\']{re.escape(section_id)}["\']', html)
        if match:
            positions.append((section_id, match.start()))
    actual = [section_id for section_id, _ in sorted(positions, key=lambda item: item[1])]
    expected = [section_id for section_id in REQUIRED_SECTION_IDS if section_id in actual]
    return [] if actual == expected else [f"required sections out of order: {actual}; expected {expected}"]


def check_required_views(html: str) -> list[str]:
    errors = []
    for section_id, label in (
        ("system-context", "system context"),
        ("runtime-scenarios", "runtime scenarios"),
        ("artifact-state-model", "artifact/state model"),
    ):
        match = re.search(
            rf'<section[^>]+id=["\']{re.escape(section_id)}["\'][^>]*>(.*?)</section>',
            html,
            re.DOTALL,
        )
        body = match.group(1) if match else ""
        has_view = bool(
            re.search(r'<svg\b|class=["\'][^"\']*\b(?:flow|pipeline|interface-map|context-view)\b', body, re.IGNORECASE)
        )
        if not has_view:
            errors.append(f"{label} section has no required visualization")
    return errors


class _FamilyModelExtractor(HTMLParser):
    """See scripts/validate_embedded_model.py for why this uses real HTML parsing
    (script CDATA vs. comment text) rather than a regex."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.capturing = False
        self.chunks: list[str] = []
        self.block_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "script":
            return
        d = dict(attrs)
        if d.get("type") == "application/json" and d.get("id") == "family-model":
            self.capturing = True
            self.block_count += 1

    def handle_data(self, data: str) -> None:
        if self.capturing:
            self.chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.capturing = False


def extract_model(html: str) -> dict[str, Any] | None:
    extractor = _FamilyModelExtractor()
    extractor.feed(html)
    if extractor.block_count != 1:
        return None
    try:
        return json.loads("".join(extractor.chunks))
    except json.JSONDecodeError:
        return None


def check_component_coverage(html: str, model: dict[str, Any] | None) -> list[str]:
    if model is None:
        return ["no embedded family-model found; cannot check component coverage"]
    errors = []
    family_map_match = re.search(
        r'<section[^>]+id="component-reference".*?</section>', html, re.DOTALL
    )
    family_map_html = family_map_match.group(0) if family_map_match else ""
    for component in model.get("components", []):
        cid = component.get("id", "")
        if cid and cid not in family_map_html and cid not in html:
            errors.append(f"component '{cid}' from embedded model does not appear in the document")
    return errors


def check_system_context_interfaces(html: str, model: dict[str, Any] | None) -> list[str]:
    if model is None:
        return ["no embedded family-model found; cannot check system-context interfaces"]
    match = re.search(r'<section[^>]+id=["\']system-context["\'][^>]*>(.*?)</section>', html, re.DOTALL)
    body = match.group(1) if match else ""
    text = re.sub(r"<[^>]+>", " ", body)
    errors = []
    for component in model.get("components", []):
        cid = component.get("id", "")
        if cid and cid not in text:
            errors.append(f"system context omits full component identifier '{cid}'")
    for label in ("Responsibility", "IN", "OUT", "Complete example"):
        if not re.search(rf"\b{re.escape(label)}\b", text, re.IGNORECASE):
            errors.append(f"system context interface map omits required label '{label}'")
    for pattern, description in (
        (r"family boundary", "explicit family boundary"),
        (r"outside boundary|external runtime|external dependencies", "external runtime/validators"),
        (r"closure_receipt\.json", "exact success output"),
        (r"BLOCKED\.md", "exact blocked output"),
        (r"review utility dependency", "review-to-visualize dependency"),
        (r"visualization alternate entry", "visualization alternate entry"),
        (r"review rejection", "review rejection route"),
        (r"test repair", "test repair route"),
        (r"caller-facing result", "orchestrator caller-facing result"),
        (r"direct writes", "orchestrator direct writes"),
        (r"delegated outputs", "orchestrator delegated outputs"),
        (r"control outputs", "orchestrator control outputs"),
    ):
        if not re.search(pattern, text, re.IGNORECASE):
            errors.append(f"system context omits {description}")
    return errors


def check_evaluation_statuses(html: str, model: dict[str, Any] | None) -> list[str]:
    errors = []
    if model is None:
        return errors
    evaluations = model.get("evaluations", {})
    for layer in ("component_tests", "family_integration", "documentation_evaluation"):
        for result in evaluations.get(layer, []):
            status = result.get("status")
            if status not in CONTROLLED_STATUSES:
                errors.append(
                    f"evaluations.{layer} entry {result.get('name')!r} has non-controlled status {status!r}"
                )
    tests_section = re.search(
        r'<section[^>]+id="quality-evidence".*?</section>', html, re.DOTALL
    )
    if tests_section and re.search(r">\s*(passed|failed)\s*<", tests_section.group(0), re.IGNORECASE):
        errors.append(
            "quality-evidence section appears to use a bare 'passed'/'failed' string "
            "instead of the controlled status vocabulary"
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_path")
    args = parser.parse_args(argv)

    html_path = Path(args.html_path)
    if not html_path.exists():
        print(json.dumps({"valid": False, "errors": [f"file not found: {html_path}"]}, indent=2))
        return 1

    html = html_path.read_text(encoding="utf-8", errors="replace")

    sp = StructureParser()
    sp.feed(html)

    model = extract_model(html)

    checks = {
        "standalone": check_standalone(html),
        "required_sections": check_required_sections(sp.section_ids),
        "required_section_order": check_required_section_order(html),
        "required_architecture_views": check_required_views(html),
        "heading_hierarchy": check_headings(sp.headings),
        "tables_well_formed": check_tables(sp.tables),
        "internal_links_resolve": check_internal_links(sp.hrefs_internal, sp.ids),
        "images_have_alt": (
            [f"{sp.imgs_missing_alt} <img> element(s) missing alt text"]
            if sp.imgs_missing_alt
            else []
        ),
        "family_model_present": [] if model is not None else ["no embedded family-model json block found"],
        "component_coverage": check_component_coverage(html, model),
        "system_context_interfaces": check_system_context_interfaces(html, model),
        "evaluation_status_vocabulary": check_evaluation_statuses(html, model),
        "print_media_query": [] if "@media print" in html else ["no @media print rule found"],
    }

    all_errors = [f"{check}: {e}" for check, errs in checks.items() for e in errs]
    result = {
        "html_path": str(html_path),
        "checks": checks,
        "valid": len(all_errors) == 0,
        "error_count": len(all_errors),
    }
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
