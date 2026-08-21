#!/usr/bin/env python3
"""Validate observable invariants of a generated issue-report HTML file."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class ReportParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.href_ids: set[str] = set()
        self.required_sections: set[str] = set()
        self.contract_text: list[str] = []
        self.in_contract = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        node_id = values.get("id")
        if node_id:
            self.ids.add(node_id)
        href = values.get("href")
        if href and href.startswith("#"):
            self.href_ids.add(href[1:])
        if tag == "section" and values.get("data-required-section") == "true" and node_id:
            self.required_sections.add(node_id)
        if tag == "script" and node_id == "issue-report-template-contract":
            self.in_contract = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.in_contract:
            self.in_contract = False

    def handle_data(self, data: str) -> None:
        if self.in_contract:
            self.contract_text.append(data)


def parse(path: Path) -> tuple[ReportParser, str]:
    text = path.read_text(encoding="utf-8")
    parser = ReportParser()
    parser.feed(text)
    return parser, text


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: validate_issue_report.py <report-path> <template-path>", file=sys.stderr)
        return 2

    report_path, template_path = map(Path, sys.argv[1:])
    failures: list[str] = []
    for path, label in ((report_path, "report"), (template_path, "template")):
        if not path.is_file():
            failures.append(f"{label} is missing: {path}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    report, report_text = parse(report_path)
    template, _ = parse(template_path)

    placeholders = sorted(set(re.findall(r"\{\{+[^{}]+\}\}+", report_text)))
    if placeholders:
        failures.append("unresolved placeholders: " + ", ".join(placeholders))
    missing_sections = sorted(template.required_sections - report.required_sections)
    if missing_sections:
        failures.append("missing required sections: " + ", ".join(missing_sections))
    missing_targets = sorted(report.href_ids - report.ids)
    if missing_targets:
        failures.append("broken internal links: " + ", ".join(missing_targets))
    if not report.contract_text:
        failures.append("missing issue-report-template-contract JSON")
    else:
        try:
            contract = json.loads("".join(report.contract_text))
            required = set(contract.get("required_sections", []))
            absent = sorted(required - report.required_sections)
            if absent:
                failures.append("contract sections absent: " + ", ".join(absent))
        except json.JSONDecodeError as exc:
            failures.append(f"invalid template contract JSON: {exc}")
    if not re.search(r"\b(VERIFIED|PARTIALLY_VERIFIED|CONTRADICTED|UNRESOLVED)\b", report_text):
        failures.append("missing canonical overall verification result")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    digest = hashlib.sha256(report_path.read_bytes()).hexdigest()
    print(f"PASS: {report_path}")
    print(f"sha256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
