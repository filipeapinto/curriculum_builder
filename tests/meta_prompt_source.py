"""Where the prompt is, and what counts as the prompt.

Until v5 the contract was one file. v6 split it: a short prompt plus the `section`
assets its own asset table named, because it was building a *generator* and the
generator's rules needed room. `curriculum.prompt.v1.md` is not building anything — it
runs a curriculum — and it is one file again, with **no section assets at all**.

That is not a return to v5. What made v5 unsafe was that a reader could slice a section
out of the short file and be right about a contract most of whose rules lived elsewhere;
a checker reading the short file alone would report a full pass on a gutted document,
which is the misreporting `policy/failures.v1.yaml` calls B3. The composition machinery
below is what closed that, and it stays: it is what makes "the contract" a single
computable thing rather than whichever file a reader opened. With no section rows it
composes to the prompt itself, and the day a section row is added it composes to more.

So the subject of every check is still the **composed contract**. There is one place
that says how that composition is formed, and this is it — a second copy would be a
second answer to "what does the prompt say".

An asset row is ``| `path` | kind | role |`` with ``kind`` in {section, companion}.
A `section` composes. A `companion` never does: it is an input a worker or reviewer
reads, and treating it as contract text would let a unit-writing guide be read as a
rule binding the run.

Nothing here validates the manifest — see ``tests/check_meta_prompt.py``, which owns
the question of whether the contract is honest (every row resolving, no orphan asset,
no heading owned twice).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

PROMPT_REL = "meta_prompt/curriculum.prompt.v1.md"
ASSETS_REL = "meta_prompt/assets"

PROMPT = REPO / PROMPT_REL
ASSETS = REPO / ASSETS_REL

# ``| `meta_prompt/assets/pedagogy.v1.md` | companion | … |`` — the kind is a fixed word
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
    # Every row is a companion. `curriculum.prompt.v1.md` carries its own rules, so
    # there is nothing to compose and no `section` row to state. The three that remain
    # are inputs: how a unit reads, why each pedagogy field exists, and how the selector
    # decides. Deleting one is still visible here, which is the point of pinning them.
    ("meta_prompt/assets/unit_prose.v1.md", COMPANION,
     ("## Purpose", "## Required unit structure", "## Visual standard",
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
    "# Curriculum Prompt — v1",
    "## Mission",
    "## Inputs",
    "### Retained contracts",
    "## Precedence",
    "## What a unit is",
    "## One parent",
    "## Grounding",
    "## The domain verifier",
    "## Generic checks",
    "## Review",
    "## Routing",
    "## Proving it",
    "## Acceptance",
    "## Never hardcode",
    "## Companions",
    "## Execution",
    "## Final response",
)


ASSET_TABLE_HEADING = r"^## Companions\s*$"


def table_rows_loose(prompt_text: str) -> list[tuple[str, str]]:
    """Every row of the asset table, read without requiring backticks."""
    block = re.search(ASSET_TABLE_HEADING + r"(.*?)(?=^## )", prompt_text, re.M | re.S)
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


# The second authority the contract's shape is compared against.
#
# It used to be the folder plan's §4 target tree, and the comparison was switched off
# with a module-level flag when `simplification.plan.v3.md` §6 phase 5 retired most of
# that asset set and the two stopped agreeing. A flag set to `False` is not a
# replacement, and the reasons offered for it were not either: `FR-P1-GITKEEP` checks
# only that four `.gitkeep` files exist, and the pinned headings check the inside of a
# file that is still listed, never whether the list is right. With the comparison off,
# `EXPECTED` certified itself — whoever deleted an asset and its row in the prompt's own
# table could delete its line in this module in the same edit, and everything stayed
# green. That is precisely the failure this module's docstring describes.
#
# So the authority moves rather than disappearing. A finished plan's tree records what
# was true when that plan completed and must not be edited to track the present; AGENTS.md
# is the live map of the repository, written for a human reader, maintained for a
# different purpose, and read by a different gate (`FR-P1-DOC`). Its `### Contract assets`
# table is the declaration, and the two are compared in both directions.
DOC = REPO / "AGENTS.md"

ASSET_DOC_HEADING = r"^### Contract assets\s*$"
DOC_ROW = re.compile(r"^\|\s*`(?P<path>[^`]+)`\s*\|\s*(?P<kind>\w+)\s*\|\s*$", re.M)


def documented_assets(read=None) -> list[tuple[str, str]]:
    """The assets AGENTS.md declares, with the kind each row states."""
    if not DOC.exists():
        return []
    text = _read(DOC, read)
    block = re.search(ASSET_DOC_HEADING + r"(.*?)(?=^#{2,3} )", text, re.M | re.S)
    if not block:
        return []
    return [(m.group("path"), m.group("kind")) for m in DOC_ROW.finditer(block.group(1))]


def shape_problems(read=None) -> list[str]:
    """``EXPECTED`` against AGENTS.md's asset table, both directions.

    Without this the shape is self-certifying: whoever deletes an asset and its table
    row can delete its line here in the same edit, and every check stays green. The
    document is maintained for a different purpose and read by a different gate, so
    agreeing with it is evidence rather than restatement.
    """
    expected = [(path, kind) for path, kind, _ in EXPECTED]
    declared = documented_assets(read)
    problems = []
    if not declared:
        return ["assets: AGENTS.md's `### Contract assets` table names no assets, so the "
                "contract's shape rests on nothing but its own word"]
    for row in expected:
        if row not in declared:
            problems.append(
                f"assets: {row[0]} ({row[1]}) is part of the contract's shape and AGENTS.md "
                f"does not name it as such"
            )
    for row in declared:
        if row not in expected:
            problems.append(
                f"assets: AGENTS.md names {row[0]} ({row[1]}) and the contract's shape does "
                "not"
            )
    return problems
