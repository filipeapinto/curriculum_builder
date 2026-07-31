"""Can the meta prompt actually be executed?

The 31 gates check that the meta prompt does not *contradict* the repository — its
references resolve, it inlines no routing value, its release table maps to real check
ids. Not one of them asks whether an agent handed the prompt could **start**. That is
why the write boundary named a directory that has not existed for the life of this
repository while 31 gates passed.

This checker asks only that question, in six parts:

  1. **anchoring**    every variable in the write boundary is a path, not prose,
                      and resolves — or is explicitly supplied at invocation.
                      CREATOR is proved derivable by an *anchor*: some other
                      boundary line must equal CREATOR/<rel> where <rel> is this
                      file, so the derivation is subtraction and not a guess. A
                      CREATOR defined in terms of a variable supplied at
                      invocation is circular and fails. A name defined twice
                      fails: dict-building silently keeps the last.
  2. **inputs**       every path the contract names under CREATOR exists.
  3. **write order**  no step writes before the only authorized root exists, no
                      model is called before the logger, the startup precondition
                      is actually checked, and nothing is written outside V7.
  4. **no dangling**  every variable the prose names is defined in the boundary.
  5. **portability**  no absolute path is hard-coded in any source of the contract —
                      any filesystem root, not just /Users, and Windows drives.
  6. **assets**       the v6 split is honest: every asset row resolves, no file in
                      `meta_prompt/assets/` is unowned by the table, no `##` heading
                      is owned twice, and the prompt is smaller than the sections it
                      binds. Without this the split becomes a way to *pass* — move a
                      rule into an unlisted file and every other check stops seeing
                      it while still reporting a full pass.

Checks 1-5 read the **composed contract**: the prompt plus its section assets, as
`tests/meta_prompt_source.py` composes them. Reading the short v6 file alone would
report 5/5 on a document with most of its rules elsewhere.

Mutation-tested. What it still cannot see is semantic: it would pass a contract whose
paths all resolve and whose instructions contradict each other. Checks 1-6 are
mechanical properties, and "6/6" is a statement about those six and nothing wider.

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

sys.path.insert(0, str(Path(__file__).resolve().parent))

import meta_prompt_source as source  # noqa: E402

REPO = source.REPO
PROMPT = source.PROMPT
ASSETS = source.ASSETS

# Variables the prompt is allowed to leave unresolved because the invocation supplies
# them. Anything else in the boundary must resolve on disk.
SUPPLIED_AT_INVOCATION = {"OUTPUT_ROOT", "V7"}


def boundary_pairs(text: str) -> list[tuple[str, str]]:
    """In file order, so a name defined twice stays visible."""
    block = re.search(r"## Write boundary\s*\n+```text\n(.*?)```", text, re.S)
    if not block:
        raise SystemExit("FAIL anchoring: no write-boundary block")
    pairs = []
    for line in block.group(1).splitlines():
        m = re.match(r"^(\w+)\s*=\s*(.+?)\s*$", line)
        if m:
            pairs.append((m.group(1), m.group(2)))
    return pairs


def boundary(text: str) -> dict[str, str]:
    return dict(boundary_pairs(text))


def creator_derivable(value: str, variables: dict[str, str]) -> list[str]:
    """CREATOR is only derivable if some other line pins this file underneath it.

    Prose saying "derive it" proves nothing — the old check accepted any value
    containing the word "containing", which a circular definition also does. What
    makes the derivation mechanical is an anchor: a boundary line equal to
    CREATOR/<rel> where <rel> is this very file. Then CREATOR is this file's path
    minus <rel> — subtraction, not a guess.
    """
    problems = []
    if not re.search(r"\bthis (?:file|prompt)\b", value):
        problems.append(
            "anchoring: CREATOR does not resolve from this file's own location; a value "
            "that does not say so leaves the reader to choose a directory"
        )
    circular = sorted(n for n in SUPPLIED_AT_INVOCATION | {"CREATOR"}
                      if re.search(rf"\b{n}\b", value))
    if circular:
        problems.append(
            f"anchoring: CREATOR is defined in terms of {', '.join(circular)}, which is "
            "supplied at invocation or is CREATOR itself — the derivation is circular"
        )
    anchored = [
        n for n, v in variables.items()
        if n != "CREATOR" and v.startswith("CREATOR/")
        and (REPO / v[len("CREATOR/"):]) == PROMPT
    ]
    if not anchored:
        problems.append(
            "anchoring: no boundary line pins this file as CREATOR/<path>, so CREATOR "
            "can only be guessed at, never derived by subtraction"
        )
    return problems


def check_anchoring(text: str, output_root: Path | None) -> list[str]:
    problems = []
    variables = boundary(text)
    if not variables:
        return ["anchoring: the write boundary defines no variables"]

    seen: dict[str, str] = {}
    for name, value in boundary_pairs(text):
        if name in seen and seen[name] != value:
            problems.append(
                f"anchoring: {name} is defined twice, as {seen[name]!r} then {value!r}; "
                "only the last is read, and the disagreement is silent"
            )
        seen[name] = value

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
            problems += creator_derivable(value, variables)
            continue
        resolved = value.replace("CREATOR/", "")
        if not (REPO / resolved).exists():
            problems.append(f"anchoring: {name} = {value} does not resolve ({resolved})")

    for name in SUPPLIED_AT_INVOCATION:
        if name not in variables:
            problems.append(f"anchoring: {name} is never defined")
    if "OUTPUT_ROOT" in variables:
        declared = variables["OUTPUT_ROOT"]
        if "no default" not in declared:
            problems.append("anchoring: OUTPUT_ROOT does not state that it has no default")
        elif re.search(r"\bdefaults? to\b", declared):
            problems.append(
                f"anchoring: OUTPUT_ROOT says it has no default and then supplies one: {declared!r}"
            )

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


WRITE_VERB = re.compile(
    r"\b(write|writes|overwrite|overwrites|rewrite|rewrites|append|appends|create|creates|delete|deletes)\b",
    re.I)
PATHISH = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_.-]*(?:/[A-Za-z0-9_./-]*|\.(?:md|json|ya?ml|py|jpg)))$")
TARGET_PREP = {"to", "into", "onto"}
SOURCE_PREP = {"from", "of", "for", "in", "under", "within", "against", "beside"}


def writes_outside_v7(order: list[tuple[int, str]]) -> list[str]:
    """"Write only to `V7`" — the one boundary rule the Execution list could break.

    A path is this verb's target if it follows it directly or after to/into/onto; it
    is a source if it follows from/of/for/in. That distinction is what keeps step 7
    ("write traceability for every id in `policy/failures.v1.yaml`") from reading as
    a write into policy/. Obfuscated phrasing can still slip past — this catches the
    plain statement of the defect, which is how it would actually be written.
    """
    problems = []
    for n, body in order:
        for verb in WRITE_VERB.finditer(body):
            clause = re.split(r"(?<=[.;:])\s", body[verb.end():])[0]
            prep = None
            for i, word in enumerate(clause.split()):
                bare = word.strip("`.,;:()").strip()
                low = bare.lower()
                if low in SOURCE_PREP:
                    prep = "source"
                    continue
                if low in TARGET_PREP:
                    prep = "target"
                    continue
                hit = PATHISH.match(bare)
                if not hit:
                    if i >= 6:
                        break  # too far from the verb to be its object
                    continue
                path = hit.group(1)
                if (i == 0 or prep == "target") and not path.startswith(("V7", "OUTPUT_ROOT")):
                    problems.append(
                        f"write order: step {n} writes outside V7 — "
                        f"{verb.group(0).lower()} {path!r}. Everything but V7 is immutable."
                    )
                prep = None
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
    calls_model = first(r"\b(?:call|invoke)s?\s+(?:the\s+)?[\w-]*\s*model\b")

    if creates_root is None:
        problems.append("write order: no step creates V7")
    if builds_logger is None:
        problems.append("write order: no step builds the logger")
    if precondition is None:
        problems.append(
            "write order: no step checks the startup precondition, so a run would "
            "write into an OUTPUT_ROOT that already holds someone else's evidence"
        )
    if calls_model and builds_logger and calls_model < builds_logger:
        problems.append(
            f"write order: a model is called at step {calls_model} but the logger is not "
            f"built until step {builds_logger}; that call cannot be logged, and an "
            "unlogged model call is failure B1"
        )
    problems += writes_outside_v7(order)
    # "Never auto-increment, merge, delete or overwrite" — a step that does any of
    # these to existing evidence makes the startup precondition decorative.
    for n, body in order:
        destructive = sorted({m.group(0).lower() for m in
                              re.finditer(r"\b(delete|deletes|overwrit\w+|merges?)\b", body)})
        if destructive:
            problems.append(
                f"write order: step {n} says {', '.join(destructive)} — choosing which "
                "evidence to keep is a human decision an unattended run must not make"
            )
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
    defined = set(boundary(text)) | {"CREATOR", "RESEARCH"}
    body = text.split("```", 2)[-1]
    problems = []
    if "`RESEARCH`" in body and RESEARCH_DEFINED not in text:
        problems.append(
            "dangling: `RESEARCH` is used as a capability and the contract never "
            "defines it; it was only ever defined in this checker's own whitelist"
        )
    for name in sorted(set(re.findall(r"`([A-Z][A-Z0-9_]{2,})`", body))):
        if name in defined:
            continue
        if re.fullmatch(r"(META_[A-Z_]+|ACT|EXEC|[A-Z]+-[A-Z0-9-]+|PDF|QA|CLI|JSON|YAML"
                        r"|ACCEPTED|BLOCKED|SYSTEM_FAILURE|UNPROVEN|OFF)", name):
            continue  # controller states, record kinds, check ids — not path variables
        problems.append(f"dangling: `{name}` is used but defined in no boundary line")
    return problems


# Any filesystem root, not just this machine's. A prompt hardcoding /opt or C:\ is
# no more portable than one hardcoding /Users — the old pattern only caught the
# defect that happened to be found first.
ABSOLUTE = re.compile(
    r"(?<![\w~])/(?:Users|home|root|etc|var|opt|tmp|private|mnt|srv|usr|Volumes)(?:/[A-Za-z0-9_.-]+)+"
    r"|(?<![\w])[A-Za-z]:[\\/][A-Za-z0-9_.\\/-]+")


def check_portability(_text: str = "") -> list[str]:
    """Reported per source file. A line number in the composed contract names no
    file anyone can open, so the scan runs over each source and cites it by name.
    Companions are scanned too: an absolute path in a lab-writing guide is as
    unportable as one in the prompt."""
    problems = []
    prompt_text = read(PROMPT)
    files = [PROMPT] + [
        REPO / rel for rel, _ in source.asset_rows(prompt_text)
        if (REPO / rel).is_file()
    ]
    for path in files:
        body = read(path)
        for match in ABSOLUTE.finditer(body):
            line = body[: match.start()].count(chr(10)) + 1
            problems.append(
                f"portability: absolute path at {path.relative_to(REPO)}:{line}: "
                f"{match.group(0)[:60]}"
            )
    return problems


# ---------------------------------------------------------------------------
# 6. assets — is the split honest?

ASSETS_BLOCK = re.compile(r"^## Assets\s*$(.*?)(?=^## )", re.M | re.S)
TABLE_ROW = re.compile(r"^\|(?P<first>[^|]*)\|(?P<kind>[^|]*)\|", re.M)
HEADING = re.compile(r"^(#+)\s+(.*?)\s*$", re.M)
# Each section asset names the headings it owns, so the file itself says what it
# is and what it carries. Companions never carry it.
SECTION_BANNER = re.compile(r"<!--\s*section asset of .*?·\s*owns:\s*(.*?)\s*-->", re.S)

KINDS = {source.SECTION, source.COMPANION}

# `RESEARCH` is a capability, not a path, so it cannot be a boundary line — but a
# capability the contract never defines is a word the reader has to guess at.
RESEARCH_DEFINED = "`RESEARCH` — the network capability"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def declared_rows(prompt_text: str) -> list[tuple[str, str]]:
    """Every row of the asset table as ``(first cell, kind)``, header and rule
    excluded — read generically, so a row whose kind is a typo is *seen* and
    rejected rather than skipped by a stricter pattern."""
    block = ASSETS_BLOCK.search(prompt_text)
    if not block:
        return []
    rows = []
    for match in TABLE_ROW.finditer(block.group(1)):
        first, kind = match.group("first").strip(), match.group("kind").strip()
        if not first or set(first) <= {"-", ":"} or first.lower() == "asset":
            continue
        rows.append((first, kind))
    return rows


def check_assets(_text: str = "") -> list[str]:
    prompt_text = read(PROMPT)
    rows = declared_rows(prompt_text)
    problems = []
    if not rows:
        return ["assets: the prompt declares no asset table, so it binds nothing"]

    seen: dict[str, int] = {}
    paths = []
    for first, kind in rows:
        name = first.strip("`")
        seen[name] = seen.get(name, 0) + 1
        if kind not in KINDS:
            problems.append(
                f"assets: {name} is declared {kind!r}, which is neither section nor "
                "companion; a kind nothing recognises composes into nothing"
            )
        if not name.startswith(source.ASSETS_REL + "/"):
            problems.append(
                f"assets: {name} is listed but does not live under {source.ASSETS_REL}/, "
                "so the no-orphan rule below can never cover it"
            )
        if not (REPO / name).exists():
            problems.append(f"assets: {name} is declared but does not exist")
        paths.append(name)
    for name, count in sorted(seen.items()):
        if count > 1:
            problems.append(f"assets: {name} is listed {count} times; one file, one row")

    if not source.assets_of_kind(prompt_text, source.SECTION):
        problems.append(
            "assets: no row is a section, so the composed contract is the short file "
            "alone and every rule moved out of it is unbound"
        )

    # No orphans. A rule moved into a file the table does not name is a rule no
    # reader of this contract will ever see, and every other check would still pass.
    for path in sorted(ASSETS.glob("*")):
        if path.name.startswith("."):
            continue
        name = str(path.relative_to(REPO))
        if name not in paths:
            problems.append(
                f"assets: {name} is in ASSETS but no row names it — unowned prose is how "
                "a contract acquires a second author"
            )

    # One rule, one home: a heading owned by two sources is two authors again.
    owners: dict[str, list[str]] = {}
    for path in source.sources():
        for _, title in HEADING.findall(read(path)):
            owners.setdefault(title, []).append(str(path.relative_to(REPO)))
    for title, where in sorted(owners.items()):
        if len(where) > 1:
            problems.append(f"assets: heading {title!r} is stated in {', '.join(where)}")

    # The claim that the prompt is small, made checkable: it is the index, so it is
    # smaller than what it indexes.
    prompt_lines = len(prompt_text.splitlines())
    section_lines = sum(
        len(read(REPO / rel).splitlines())
        for rel in source.assets_of_kind(prompt_text, source.SECTION)
        if (REPO / rel).is_file()
    )
    if prompt_lines >= section_lines:
        problems.append(
            f"assets: the prompt is {prompt_lines} lines and the sections it binds are "
            f"{section_lines}; a prompt no smaller than its assets has not been split, "
            "it has been copied"
        )

    problems += source.table_problems(prompt_text)
    problems += banner_problems(rows)
    return problems


def banner_problems(rows: list[tuple[str, str]]) -> list[str]:
    """The banner is the asset's own claim; the table cell is the prompt's.

    Without this, one edited table cell silently shrinks the contract: flip a row
    from `section` to `companion` and that file leaves the composition, its rules
    stop being contract, and every other check still reports a full pass — the
    orphan rule cannot fire, because the row still names the file. So the two
    claims must agree, and each section must still carry the headings it claims to
    own. That is what makes deleting `## Precedence` a failure rather than a
    quieter contract.

    It does not make prose safe. A rule deleted from inside a heading this file
    still declares is invisible here, and only the run's own prompt hash — over
    the prompt and its section assets together — would catch it.
    """
    problems = []
    for first, kind in rows:
        name = first.strip("`")
        path = REPO / name
        if not path.is_file():
            continue  # already reported as unresolved
        banners = SECTION_BANNER.findall(read(path))
        if len(banners) > 1:
            problems.append(
                f"assets: {name} carries {len(banners)} section banners; only the first is "
                "read, so the others are claims about the file that nothing checks"
            )
        banner = banners[0] if banners else None
        if kind == source.SECTION and not banner:
            problems.append(
                f"assets: {name} is declared section but carries no section banner, so "
                "nothing in the file itself claims to be part of this contract"
            )
        elif kind == source.COMPANION and banner:
            problems.append(
                f"assets: {name} carries the section banner but the table declares it "
                "companion; one flipped cell is all it takes to drop a rule out of the "
                "contract while every check still passes"
            )
        if not banner:
            continue
        declared = {h.strip() for h in banner.split(",") if h.strip()}
        present = {f"{hashes} {title}" for hashes, title in HEADING.findall(read(path))}
        expected = set(source.EXPECTED_HEADINGS.get(name, ()))
        # Three claims, not one: the file's headings, the file's own banner, and the
        # shape held outside the contract. A banner edited to match a gutted file
        # satisfies the first two and fails the third, which is the point.
        for missing in sorted(declared - present):
            problems.append(f"assets: {name} claims to own {missing!r} and does not state it")
        for extra in sorted(present - declared):
            problems.append(f"assets: {name} states {extra!r}, which its banner does not claim")
        for dropped in sorted(expected - declared):
            problems.append(
                f"assets: {name} is expected to own {dropped!r} and its banner no longer "
                "claims it — a banner edited to match a gutted file certifies itself"
            )
        for added in sorted(declared - expected):
            problems.append(
                f"assets: {name} claims to own {added!r}, which is not part of the "
                "contract's shape"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=None,
                        help="where a run would write; checked for the V7 precondition")
    args = parser.parse_args()
    text = source.compose()

    parts = [
        ("anchoring", check_anchoring(text, args.output_root)),
        ("inputs", check_inputs(text)),
        ("write order", check_write_order(text)),
        ("no dangling", check_no_dangling(text)),
        ("portability", check_portability()),
        ("assets", check_assets()),
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
        sources = ", ".join(str(p.relative_to(REPO)) for p in source.sources())
        print(f"Read as one contract: {sources}")
        print("This says the prompt can be started and its inputs resolve.")
        print("It says nothing about whether the generator it describes can be built.")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
