#!/usr/bin/env python3
"""Validate a plan-create package under plans/<slug>/.

Checks, for the latest version N found:
  - all six artifacts exist (plan, plan_qa, execution_test.plan, prompt,
    final_audit, plans.log.md)
  - each document has its required section headers
  - both verdict lines are well-formed
  - a PASS/APPROVED verdict actually carries "0 Critical, 0 High"
  - every <PREFIX>-T<NN> id in the prompt's TEST section has a matching
    "### <PREFIX>-T<NN> " heading in the execution test plan, and vice versa

Exits 0 with "OK" if everything checks out, otherwise prints every problem
found and exits 1. This does not judge content quality -- only structure and
internal consistency, which is exactly the kind of thing a distracted
revision pass drifts on.

Usage:
    validate_plan_package.py plans/<slug>
"""

import re
import sys
from pathlib import Path

PLAN_SECTIONS = [
    "## Status and objective",
    "## Exact work",
    "## Verification sequence",
    "## Acceptance criteria",
    "## Stop conditions and result",
]
PLAN_QA_SECTIONS = ["## Verdict", "## Findings"]
TEST_PLAN_SECTIONS = ["## Purpose and boundary", "## Ordered tests", "## Final audit and pass rule"]
PROMPT_SECTIONS = ["# GOAL", "# TEST", "# LOOP"]
FINAL_AUDIT_SECTIONS = ["## Verdict", "## Evidence"]

PLAN_QA_VERDICT_RE = re.compile(
    r"\*\*(APPROVED|CHANGES REQUIRED) — (\d+) Critical, (\d+) High\.\*\*"
)
FINAL_AUDIT_VERDICT_RE = re.compile(
    r"\*\*(PASS|CHANGES REQUIRED) — (\d+) Critical, (\d+) High remaining\.\*\*"
)
TEST_ID_RE = re.compile(r"\b([A-Z]{2,4}-T\d{2})\b")
TEST_HEADING_RE = re.compile(r"^###\s+([A-Z]{2,4}-T\d{2})\s+—", re.MULTILINE)


def find_latest_version(root: Path, glob_pattern: str) -> int:
    versions = []
    for path in root.glob(glob_pattern):
        m = re.search(r"\.v(\d+)\.md$", path.name)
        if m:
            versions.append(int(m.group(1)))
    return max(versions) if versions else 0


def check_sections(problems, label, text, required_sections):
    for section in required_sections:
        if section not in text:
            problems.append(f"{label}: missing required section {section!r}")


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    root = Path(argv[1])
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    slug = root.name
    problems = []

    plan_version = find_latest_version(root, f"{slug}.plan.v*.md")
    if plan_version == 0:
        print(f"error: no {slug}.plan.vN.md found under {root}", file=sys.stderr)
        return 2
    v = plan_version

    paths = {
        "plan": root / f"{slug}.plan.v{v}.md",
        "plan_qa": root / "qa" / f"plan_qa.v{v}.md",
        "test_plan": root / "qa" / f"execution_test.plan.v{v}.md",
        "prompt": root / "prompts" / f"{slug}.prompt.v{v}.md",
        "final_audit": root / "qa" / f"final_audit.v{v}.md",
        "log": root / "plans.log.md",
    }

    texts = {}
    for label, path in paths.items():
        if not path.exists():
            problems.append(f"missing artifact for v{v}: {path}")
            continue
        texts[label] = path.read_text()

    if "plan" in texts:
        check_sections(problems, "plan", texts["plan"], PLAN_SECTIONS)
    if "plan_qa" in texts:
        check_sections(problems, "plan_qa", texts["plan_qa"], PLAN_QA_SECTIONS)
        m = PLAN_QA_VERDICT_RE.search(texts["plan_qa"])
        if not m:
            problems.append("plan_qa: no well-formed verdict line found")
        elif m.group(1) == "APPROVED" and (m.group(2) != "0" or m.group(3) != "0"):
            problems.append(
                f"plan_qa: verdict says APPROVED but reports {m.group(2)} Critical, "
                f"{m.group(3)} High -- APPROVED requires 0/0"
            )
    if "test_plan" in texts:
        check_sections(problems, "test_plan", texts["test_plan"], TEST_PLAN_SECTIONS)
    if "prompt" in texts:
        check_sections(problems, "prompt", texts["prompt"], PROMPT_SECTIONS)
    if "final_audit" in texts:
        check_sections(problems, "final_audit", texts["final_audit"], FINAL_AUDIT_SECTIONS)
        m = FINAL_AUDIT_VERDICT_RE.search(texts["final_audit"])
        if not m:
            problems.append("final_audit: no well-formed verdict line found")
        elif m.group(1) == "PASS" and (m.group(2) != "0" or m.group(3) != "0"):
            problems.append(
                f"final_audit: verdict says PASS but reports {m.group(2)} Critical, "
                f"{m.group(3)} High remaining -- PASS requires 0/0"
            )

    if "log" in texts and "## Entries" not in texts["log"]:
        problems.append("plans.log.md: missing '## Entries' section")

    if "prompt" in texts and "test_plan" in texts:
        test_section = texts["prompt"].split("# TEST", 1)[-1].split("# LOOP", 1)[0]
        prompt_ids = set(TEST_ID_RE.findall(test_section))
        plan_ids = set(TEST_HEADING_RE.findall(texts["test_plan"]))

        orphan_in_prompt = sorted(prompt_ids - plan_ids)
        orphan_in_plan = sorted(plan_ids - prompt_ids)
        if orphan_in_prompt:
            problems.append(
                f"prompt TEST section references id(s) not in execution test plan: "
                f"{', '.join(orphan_in_prompt)}"
            )
        if orphan_in_plan:
            problems.append(
                f"execution test plan defines id(s) never referenced in prompt TEST "
                f"section: {', '.join(orphan_in_plan)}"
            )
        if not prompt_ids:
            problems.append("prompt TEST section: no test ids found (expected <PREFIX>-T<NN>)")

    if problems:
        print(f"FAIL — {len(problems)} problem(s) in {root}:\n")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"OK — plans/{slug} v{v} package is structurally valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
