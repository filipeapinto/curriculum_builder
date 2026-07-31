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
ASSET_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(section|companion)\s*\|", re.M)

SECTION = "section"
COMPANION = "companion"


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
