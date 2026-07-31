"""Can the meta prompt actually be executed?

The 31 gates check that the meta prompt does not *contradict* the repository — its
references resolve, it inlines no routing value, its release table maps to real check
ids. Not one of them asks whether an agent handed the prompt could **start**. That is
why the write boundary named a directory that has not existed for the life of this
repository while 31 gates passed.

This checker asks only that question, in five parts:

  1. **anchoring**    every variable in the write boundary is a path, not prose,
                      and resolves — or is explicitly supplied at invocation.
  2. **inputs**       every path the prompt names under CREATOR exists.
  3. **write order**  no step writes before the only authorized root exists, and
                      nothing is written outside it.
  4. **no dangling**  every variable the prose names is defined in the boundary.
  5. **portability**  no absolute path is hard-coded anywhere in the prompt.

It is deliberately NOT one of the FR- gates. `FR-P0-REGISTRY` requires
`tests/gates/registry.py` to equal section 8 of the active folder-refactoring plan
exactly, in both directions; adding a gate would make the registry disagree with a
plan that is finished. Folding this in belongs with generalising the registry to
compose from several plans, which is its own piece of work. Until then this runs on
its own and is not counted as a gate — a check that runs and is honestly labelled
beats a gate that required weakening something to add.

    python3 tests/check_meta_prompt.py [--output-root PATH]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROMPT = REPO / "meta_prompt" / "meta_curriculum_builder.prompt.v5.md"

# Variables the prompt is allowed to leave unresolved because the invocation supplies
# them. Anything else in the boundary must resolve on disk.
SUPPLIED_AT_INVOCATION = {"OUTPUT_ROOT", "V7"}


def boundary(text: str) -> dict[str, str]:
    block = re.search(r"## Write boundary\s*\n+```text\n(.*?)```", text, re.S)
    if not block:
        raise SystemExit("FAIL anchoring: no write-boundary block")
    found = {}
    for line in block.group(1).splitlines():
        m = re.match(r"^(\w+)\s*=\s*(.+?)\s*$", line)
        if m:
            found[m.group(1)] = m.group(2)
    return found


def check_anchoring(text: str, output_root: Path | None) -> list[str]:
    problems = []
    variables = boundary(text)
    if not variables:
        return ["anchoring: the write boundary defines no variables"]

    for name, value in variables.items():
        # A value that reads as a sentence is the defect this check exists for.
        if name not in SUPPLIED_AT_INVOCATION and " " in value and "/" not in value:
            problems.append(f"anchoring: {name} is prose, not a path: {value!r}")
        if name in SUPPLIED_AT_INVOCATION:
            continue
        if value.startswith("/"):
            problems.append(f"anchoring: {name} is an absolute path; it resolves on one machine only")
            continue
        if name == "CREATOR":
            if "derive" not in value and "containing" not in value:
                problems.append("anchoring: CREATOR is neither derived nor a path")
            continue
        resolved = value.replace("CREATOR/", "")
        if not (REPO / resolved).exists():
            problems.append(f"anchoring: {name} = {value} does not resolve ({resolved})")

    for name in SUPPLIED_AT_INVOCATION:
        if name not in variables:
            problems.append(f"anchoring: {name} is never defined")
    if "OUTPUT_ROOT" in variables and "no default" not in variables["OUTPUT_ROOT"]:
        problems.append("anchoring: OUTPUT_ROOT does not state that it has no default")

    if output_root is not None:
        v7 = output_root / "templates_v7"
        if v7.exists():
            problems.append(
                f"precondition: {v7} already exists — a real run must stop here as "
                "META_SYSTEM_FAILURE, which is correct behaviour, not a defect"
            )
    return problems


def check_inputs(text: str) -> list[str]:
    problems = []
    named = sorted({
        m for m in re.findall(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:yaml|json|md|jpg|py))`", text)
    } | {
        m for m in re.findall(r"`((?:policy|schemas|curricula|meta_prompt|docs|plans|tests)/[a-z_/]*)`", text)
    })
    for path in named:
        if path.startswith(("V7/", "templates_v7")) or path in ("remediation_report.md",):
            continue  # produced by the run, not read by it
        if not (REPO / path).exists():
            problems.append(f"inputs: {path} is named but does not exist")
    return problems


def check_write_order(text: str) -> list[str]:
    """The logger must have somewhere legal to append before it appends."""
    problems = []
    steps = re.search(r"## Execution\s*\n+(.*?)\n\nLog the planned", text, re.S)
    if not steps:
        return ["write order: no Execution list found"]
    numbered = re.findall(r"^\s*(\d+)\.\s+(.*?)(?=\n\s*\d+\.|\Z)", steps.group(1), re.S | re.M)
    order = [(int(n), " ".join(body.split())) for n, body in numbered]

    def first(pattern):
        for n, body in order:
            if re.search(pattern, body, re.I):
                return n
        return None

    creates_root = first(r"create `?V7`?")
    builds_logger = first(r"build the logger")
    precondition = first(r"precondition|V7` exists")

    if creates_root is None:
        problems.append("write order: no step creates V7")
    if builds_logger is None:
        problems.append("write order: no step builds the logger")
    if creates_root and builds_logger and creates_root > builds_logger:
        problems.append(
            f"write order: the logger is built at step {builds_logger} but V7 — the only "
            f"authorized write target — is not created until step {creates_root}. The "
            "first record has nowhere legal to go."
        )
    if precondition and creates_root and precondition > creates_root:
        problems.append(
            f"write order: the startup precondition is checked at step {precondition}, "
            f"after V7 is created at step {creates_root}; it can then never fire."
        )
    return problems


def check_no_dangling(text: str) -> list[str]:
    defined = set(boundary(text)) | {"CREATOR", "ROOT", "RESEARCH"}
    body = text.split("```", 2)[-1]
    problems = []
    for name in sorted(set(re.findall(r"`([A-Z][A-Z0-9_]{2,})`", body))):
        if name in defined:
            continue
        if re.fullmatch(r"(META_[A-Z_]+|ACT|EXEC|[A-Z]+-[A-Z0-9-]+|PDF|QA|CLI|JSON|YAML"
                        r"|ACCEPTED|BLOCKED|SYSTEM_FAILURE|UNPROVEN|OFF)", name):
            continue  # controller states, record kinds, check ids — not path variables
        problems.append(f"dangling: `{name}` is used but defined in no boundary line")
    return problems


def check_portability(text: str) -> list[str]:
    hits = [
        f"portability: absolute path at line {text[:m.start()].count(chr(10)) + 1}: {m.group(0)[:60]}"
        for m in re.finditer(r"/Users/[A-Za-z0-9_./-]+", text)
    ]
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=None,
                        help="where a run would write; checked for the V7 precondition")
    args = parser.parse_args()
    text = PROMPT.read_text(encoding="utf-8")

    parts = [
        ("anchoring", check_anchoring(text, args.output_root)),
        ("inputs", check_inputs(text)),
        ("write order", check_write_order(text)),
        ("no dangling", check_no_dangling(text)),
        ("portability", check_portability(text)),
    ]
    failed = 0
    for name, problems in parts:
        if problems:
            failed += 1
            print(f"FAIL {name}")
            for p in problems:
                print(f"       {p}")
        else:
            print(f"PASS {name}")
    verdict = "EXECUTABLE" if not failed else "NOT EXECUTABLE"
    print(f"\nmeta prompt: {verdict} ({len(parts) - failed}/{len(parts)} checks pass)")
    if not failed:
        print("This says the prompt can be started and its inputs resolve.")
        print("It says nothing about whether the generator it describes can be built.")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
