#!/usr/bin/env python3
"""Validate structural invariants of a plan-createe HTML artifact."""
from __future__ import annotations
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REQUIRED = {"summary", "source", "scope", "work", "flow", "verification", "decisions", "risks", "delivery", "approval"}
ALLOWED = {"draft", "awaiting approval", "approved", "superseded", "rejected"}

class Inspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.contract = ""
        self.capture = False
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"] or "")
        if tag == "script" and values.get("id") == "plan-createe-contract":
            self.capture = True
    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.capture:
            self.capture = False
    def handle_data(self, data: str) -> None:
        if self.capture:
            self.contract += data

def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("usage: validate_plan.py PLAN_PATH [ISSUE_REPORT_PATH]", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    parser = Inspector()
    parser.feed(text)
    ids = set(parser.ids)
    missing = sorted(REQUIRED - ids)
    if missing:
        errors.append(f"missing required section ids: {', '.join(missing)}")
    duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
    if duplicates:
        errors.append(f"duplicate ids: {', '.join(duplicates)}")
    for href in parser.hrefs:
        if href.startswith("#") and href[1:] not in ids:
            errors.append(f"unresolved internal link: {href}")
    if re.search(r"\b(TODO|TBD|PLACEHOLDER)\b|\{\{[^}]+\}\}", text, re.I):
        errors.append("unfinished template placeholder found")
    try:
        data = json.loads(parser.contract)
    except (json.JSONDecodeError, TypeError) as exc:
        errors.append(f"invalid or missing plan-createe-contract JSON: {exc}")
        data = {}
    if data:
        if data.get("schema") != "repo.plan-createe/v1":
            errors.append("unexpected contract schema")
        if data.get("status") not in ALLOWED:
            errors.append("invalid status")
        if not isinstance(data.get("plan_version"), int) or data["plan_version"] < 1:
            errors.append("plan_version must be a positive integer")
        for key in ("work_packages", "acceptance_tests", "open_decisions"):
            values = data.get(key)
            if not isinstance(values, list) or len(values) != len(set(values)):
                errors.append(f"{key} must be an array of unique values")
    if len(sys.argv) == 3:
        issue = Path(sys.argv[2])
        if not issue.is_file():
            errors.append(f"issue report not found: {issue}")
        elif data and data.get("source_issue") not in {str(issue), issue.as_posix()} and issue.name not in text:
            errors.append("source issue is not visibly identified")
        else:
            issue_name = issue.name
            match = re.match(r"^(?P<slug>.+?)\.issue_report\.v[1-9][0-9]*\.[^.]+$", issue_name)
            if match:
                slug = match.group("slug")
                try:
                    relative_plan = path.resolve().relative_to(Path.cwd().resolve())
                except ValueError:
                    relative_plan = None
                if relative_plan is not None:
                    expected_parent = Path("plans") / slug
                    if relative_plan.parent != expected_parent:
                        errors.append(f"plan must be placed under {expected_parent}/")
                    expected_name = re.compile(rf"^{re.escape(slug)}\.solution_plan\.v[1-9][0-9]*\.[^.]+$")
                    if not expected_name.match(relative_plan.name):
                        errors.append(f"plan filename must match {slug}.solution_plan.vN.<extension>")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
