"""Can the meta prompt actually be executed?

The 31 gates check that the meta prompt does not *contradict* the repository — its
references resolve, it inlines no routing value, its release table maps to real check
ids. Not one of them asks whether an agent handed the prompt could **start**. That is
why the write boundary named a directory that has not existed for the life of this
repository while 31 gates passed.

This checker asks only that question, in five parts:

  1. **anchoring**    every variable in the write boundary is a path, not prose,
                      and resolves — or is explicitly supplied at invocation.
                      CREATOR is proved derivable by an *anchor*: some other
                      boundary line must equal CREATOR/<rel> where <rel> is this
                      file, so the derivation is subtraction and not a guess. A
                      CREATOR defined in terms of a variable supplied at
                      invocation is circular and fails. A name defined twice
                      fails: dict-building silently keeps the last.
  2. **inputs**       every path the prompt names under CREATOR exists.
  3. **write order**  no step writes before the only authorized root exists, no
                      model is called before the logger, the startup precondition
                      is actually checked, and nothing is written outside V7.
  4. **no dangling**  every variable the prose names is defined in the boundary.
  5. **portability**  no absolute path is hard-coded anywhere in the prompt —
                      any filesystem root, not just /Users, and Windows drives.

Mutation-tested. What it still cannot see is semantic: it would pass a prompt whose
paths all resolve and whose instructions contradict each other. Checks 1-5 are
mechanical properties, and "5/5" is a statement about those five and nothing wider.

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


# Any filesystem root, not just this machine's. A prompt hardcoding /opt or C:\ is
# no more portable than one hardcoding /Users — the old pattern only caught the
# defect that happened to be found first.
ABSOLUTE = re.compile(
    r"(?<![\w~])/(?:Users|home|root|etc|var|opt|tmp|private|mnt|srv|usr|Volumes)(?:/[A-Za-z0-9_.-]+)+"
    r"|(?<![\w])[A-Za-z]:[\\/][A-Za-z0-9_.\\/-]+")


def check_portability(text: str) -> list[str]:
    return [
        f"portability: absolute path at line {text[:m.start()].count(chr(10)) + 1}: {m.group(0)[:60]}"
        for m in ABSOLUTE.finditer(text)
    ]


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
