"""Where the meta prompt is, and what counts as the meta prompt.

Until v5 the contract was one file, so every reader could slice a section out of it
and be right. v6 split it: a short prompt that states the mission, the boundary and
the order of work, plus the `section` assets its own asset table names. `## Routing`
is no longer *in* the prompt — it is in an asset the prompt binds, and it binds with
the same force. A checker that kept reading the short file alone would report a
5/5 pass on a document with most of its rules removed, which is the exact shape of
the misreporting `policy/failures.v1.yaml` calls B3.

So the subject of every check is the **composed contract**: the prompt followed by
its section assets, in the order the table gives. There is one place that says how
that composition is formed, and this is it — a second copy would be a second answer
to "what does the prompt say".

An asset row is ``| `path` | kind | role |`` with ``kind`` in {section, companion}.
A `section` composes. A `companion` never does: it is an input a worker or reviewer
reads, and treating it as contract text would let a lab-writing guide be read as a
rule binding the generator.

Nothing here validates the manifest — see ``tests/check_meta_prompt.py``, which owns
the question of whether the split is honest (every row resolving, no orphan asset,
no heading owned twice, the prompt smaller than the assets it binds).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

PROMPT_REL = "meta_prompt/meta_curriculum_builder.prompt.v6.md"
ASSETS_REL = "meta_prompt/assets"

PROMPT = REPO / PROMPT_REL
ASSETS = REPO / ASSETS_REL

# ``| `meta_prompt/assets/inputs.v1.md` | section | … |`` — the kind is a fixed word
# in its own column, never inferred from the role text beside it.
ASSET_ROW = re.compile(r"^ {0,3}\|\s*`([^`]+)`\s*\|\s*(section|companion)\s*\|", re.M)

# The same rows read loosely — no backticks required, any word as the kind. The
# composer must use the strict form (a path is a path), but a checker that reads
# only the strict form cannot see a row the composer has silently dropped. Both
# readings must agree; ``table_problems`` is where that is asserted. Stripping two
# backticks was enough to remove a whole section from the contract with every
# check still green.
ROW_ANY = re.compile(r"^ {0,3}\|(?P<first>[^|]*)\|(?P<kind>[^|]*)\|", re.M)

SECTION = "section"
COMPANION = "companion"

# The contract's shape, held here so it is not the contract's own word for it.
# A prompt that drops a section row, adds one, reorders them, or renames a heading
# is checked against this; without it the table is self-certifying and deleting an
# asset together with its row passes everything. Adding a section is meant to be an
# edit here too — that is the same discipline ``tests/gates/registry.py`` keeps
# with the plan's gate catalogue.
EXPECTED: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("meta_prompt/assets/inputs.v1.md", SECTION,
     ("## Inputs", "### Retained contracts", "## Precedence")),
    ("meta_prompt/assets/architecture.v1.md", SECTION,
     ("## What the generator must be", "## What a lab must be")),
    ("meta_prompt/assets/routing.v1.md", SECTION, ("## Routing",)),
    ("meta_prompt/assets/proving.v1.md", SECTION, ("## Proving it", "## Release gates")),
    ("meta_prompt/assets/logging.v1.md", SECTION,
     ("## The action log", "## Convergence and drift")),
    ("meta_prompt/assets/deliverables.v1.md", SECTION, ("## Deliverables",)),
    # A companion carries no banner — it is not contract text — so what is pinned
    # here is its top-level structure, the floor below which it has been gutted
    # rather than edited. Its `###` detail is free to change.
    ("meta_prompt/assets/component_lab_template.v1.md", COMPANION,
     ("## Purpose", "## Required lab structure", "## Visual standard",
      "## Child-language rules", "## Safety baseline")),
    ("meta_prompt/assets/pedagogy.v1.md", COMPANION,
     ("## The spine: 5E instructional model", "## Inside Explore: Predict–Observe–Explain",
      "## Misconceptions: conceptual change", "## Prior knowledge and retrieval practice",
      "## Vocabulary and cognitive load", "## Objectives and success criteria",
      "## Scaffolding and fading", "## Dual coding", "## Where pedagogy meets safety",
      "## What the schema deliberately does not encode")),
    ("meta_prompt/assets/model_selector_prompt.v1.md", COMPANION,
     ("## Role", "## Read first", "## Input", "## Procedure", "## Output constraints")),
)

EXPECTED_HEADINGS = {path: headings for path, _, headings in EXPECTED}

# The prompt carries no banner — it is the thing banners name — so its own headings
# are pinned here. Without this the file at the top of the contract was the easiest
# to gut: deleting `## Final response`, the entire reporting contract, passed.
PROMPT_HEADINGS = (
    "# ELEGOO Meta-Curriculum Prompt — v6",
    "## Mission",
    "## Write boundary",
    "## Assets",
    "## Execution",
    "## Final response",
)


def table_rows_loose(prompt_text: str) -> list[tuple[str, str]]:
    """Every row of the asset table, read without requiring backticks."""
    block = re.search(r"^## Assets\s*$(.*?)(?=^## )", prompt_text, re.M | re.S)
    if not block:
        return []
    rows = []
    for match in ROW_ANY.finditer(block.group(1)):
        first, kind = match.group("first").strip(), match.group("kind").strip()
        if not first or set(first) <= {"-", ":"} or first.lower() == "asset":
            continue
        rows.append((first.strip("`"), kind))
    return rows


def table_problems(prompt_text: str) -> list[str]:
    """The asset table against this module's expectation, and against itself."""
    problems = []
    strict = [(path, kind) for path, kind in asset_rows(prompt_text)]
    loose = table_rows_loose(prompt_text)
    for path, kind in loose:
        if (path, kind) not in strict:
            problems.append(
                f"assets: the row for {path} ({kind}) is not read by the composer — a row "
                "the checker can see and the composer cannot is a section silently "
                "dropped from the contract"
            )
    expected = [(path, kind) for path, kind, _ in EXPECTED]
    if strict != expected:
        missing = [row for row in expected if row not in strict]
        extra = [row for row in strict if row not in expected]
        for path, kind in missing:
            problems.append(f"assets: {path} ({kind}) is expected by the contract's shape and is not in the table")
        for path, kind in extra:
            problems.append(f"assets: {path} ({kind}) is in the table and is not part of the contract's shape")
        if not missing and not extra:
            problems.append(
                f"assets: the table lists the right assets in the wrong order — "
                f"{[p for p, _ in strict]}; composition and the prompt hash both follow "
                "this order, so reordering changes the hash of an unchanged contract"
            )
    return problems


def _read(path: Path, read=None) -> str:
    """``read`` is the gate's ``Evidence.text_of`` when a gate is composing, so the
    files a claim rests on are recorded as read rather than read behind its back."""
    return read(path) if read is not None else path.read_text(encoding="utf-8")


def asset_rows(prompt_text: str) -> list[tuple[str, str]]:
    """Every ``(path, kind)`` in the asset table, in file order."""
    return [(m.group(1), m.group(2)) for m in ASSET_ROW.finditer(prompt_text)]


def assets_of_kind(prompt_text: str, kind: str) -> list[str]:
    return [path for path, found in asset_rows(prompt_text) if found == kind]


def sources(read=None) -> list[Path]:
    """The prompt, then its section assets, in table order.

    This is also the hashing order the prompt's own convergence rule names: a hash
    over the short file alone would let a rule change under a run reporting itself
    unchanged.
    """
    text = _read(PROMPT, read)
    return [PROMPT] + [REPO / rel for rel in assets_of_kind(text, SECTION)]


def compose(read=None) -> str:
    """The composed contract. Sections are joined with a blank line so a heading
    always starts a line, which is what every section-slicing reader depends on."""
    return "\n".join(_read(path, read) for path in sources(read))


PLAN = REPO / "plans" / "folder_refactoring" / "folder_refactoring.plan.v6.md"


def plan_assets(read=None) -> list[tuple[str, str]]:
    """The assets §4's target tree names under ``meta_prompt/assets/``, with the kind
    each annotation declares — ``section: …`` or ``companion: …``."""
    if not PLAN.exists():
        return []
    text = _read(PLAN, read)
    rows = []
    inside = False
    for line in text.splitlines():
        if re.search(r"├── assets/", line):
            inside = True
            continue
        if inside:
            match = re.search(r"[├└]── ([A-Za-z0-9_.-]+\.md)\s+(\w+):", line)
            if not match:
                if re.search(r"[├└]── ", line) and "│   │" not in line:
                    break  # left the assets/ block
                continue
            rows.append((f"{ASSETS_REL}/{match.group(1)}", match.group(2)))
    return rows


def shape_problems(read=None) -> list[str]:
    """``EXPECTED`` against the plan's tree, both directions.

    Without this the shape is self-certifying: whoever deletes a section asset and
    its table row can delete its line here in the same edit, and every check stays
    green. The plan is maintained for a different purpose by a different gate, so
    agreeing with it is evidence rather than restatement.
    """
    expected = [(path, kind) for path, kind, _ in EXPECTED]
    declared = plan_assets(read)
    problems = []
    if not declared:
        return ["assets: the plan's §4 tree names no assets, so the contract's shape rests "
                "on nothing but its own word"]
    for row in expected:
        if row not in declared:
            problems.append(
                f"assets: {row[0]} ({row[1]}) is part of the contract's shape and the plan's "
                f"§4 tree does not name it as such"
            )
    for row in declared:
        if row not in expected:
            problems.append(
                f"assets: the plan's §4 tree names {row[0]} ({row[1]}) and the contract's "
                "shape does not"
            )
    return problems
