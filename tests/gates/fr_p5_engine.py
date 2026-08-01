"""Phase-5 gate — the engine layer knows that curricula exist, never which one.

``plans/simplification/plan/simplification.plan.v3.md`` §2 states the boundary: the
engine — ``policy/``, ``schemas/``, the meta prompt — holds premises, precedence, the
unit contract, generic checks, routing and the run, and knows about electronics
*never*; ``curricula/<name>/`` holds the domain *entirely*. §6 phase 0 asks for the
inventory that turns that from a claim into a number, and this gate is it.

**This gate is expected to fail.** It is a measurement of how much domain is welded
into the engine today, not a regression that guards a property already held. Its
verdict on the working tree is the deliverable; making it green by deleting the leaks
it names is the work of §6 phases 1-5, and doing that early destroys the measurement.

Two things it deliberately does not do.

It contains **no domain word**. A detector that hard-codes ``circuit`` is itself the
leak it exists to detect, and it would go stale the moment a second curriculum in an
unrelated domain arrives — which is the whole objective. The vocabulary is read from
the ``*_terms`` blocks of the curriculum manifests that ``policy/checks.v1.yaml``
itself names as owners, each carrying the anchored ``prose_pattern`` that
``FR-P3-SPLIT`` and ``FR-P3-NO-LITERALS`` already match on. That bounds what (b) can
see to what a curriculum has bothered to declare — a real limit, reported in the
gate's own output rather than hidden by it.

It contains **no version literal for the meta prompt**. ``tests/meta_prompt_source.py``
is, per AGENTS.md, the only definition of "the meta prompt" any checker uses, so the
engine's prompt file is asked of that module rather than spelled here.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import common  # noqa: E402
import meta_prompt_source  # noqa: E402
from common import Evidence, Fixture, REPO_ROOT, gate_result, read_named, rel  # noqa: E402

FIXTURES = common.FIXTURES_DIR

CHECKS = REPO_ROOT / "policy" / "checks.v1.yaml"
CURRICULA_DIR = REPO_ROOT / "curricula"

# The engine layer, by root. `meta_prompt/docs/` is orientation only (AGENTS.md) and
# `docs/` is regenerated explainer prose; neither is a contract, and neither is here.
ENGINE_ROOTS = ("policy", "schemas")

# Retention: `deprecated/` holds an artifact nothing may read. A leak in a file no
# consumer resolves is history, not debt, and counting it would inflate the
# measurement this gate exists to make honest.
RETIRED = "deprecated"

# The curriculum layer's own folder. Named once, here, because (a)'s whole subject is
# whether an engine file names a path *under* it.
CURRICULA_PREFIX = "curricula"


# ---------------------------------------------------------------------------
# What is in the engine layer


def engine_files() -> list[Path]:
    """Every engine file a domain term could hide in, ``deprecated/`` excluded."""
    found: list[Path] = []
    for root in ENGINE_ROOTS:
        for path in (REPO_ROOT / root).rglob("*"):
            if not path.is_file():
                continue
            if RETIRED in path.relative_to(REPO_ROOT).parts:
                continue
            if path.suffix.lower() in common.BINARY_SUFFIXES:
                continue
            found.append(path)
    found.append(meta_prompt_source.PROMPT)
    found += [p for p in meta_prompt_source.ASSETS.glob("*.md")]
    return sorted(set(found))


def curriculum_names(ev: Evidence | None = None) -> list[str]:
    """Which curricula exist. A directory listing *is* the assertion here — the engine
    is allowed to know that curricula exist, so the question is which names it must
    not contain, and that set is read at run time rather than written down."""
    entries = ev.listdir(CURRICULA_DIR) if ev is not None else sorted(CURRICULA_DIR.iterdir())
    return [p.name for p in entries if p.is_dir() and p.name != RETIRED]


# ---------------------------------------------------------------------------
# What the domain's words are, and which check ids the engine owns


def _check_entries(checks_doc) -> list[dict]:
    return [
        entry
        for value in (checks_doc or {}).values()
        if isinstance(value, list)
        for entry in value
        if isinstance(entry, dict) and "id" in entry
    ]


def engine_owned_checks(checks_doc) -> list[dict]:
    """Check ids whose declared ``owner`` is not a curriculum file.

    Ownership is what the manifest says, not what the id looks like. An id owned by a
    file under ``curricula/`` is the curriculum's assertion living in the engine's
    inventory — that is `G3`, and it is (a)'s subject through the owner path itself,
    not (b)'s.
    """
    return [
        entry
        for entry in _check_entries(checks_doc)
        if not str(entry.get("owner") or "").startswith(CURRICULA_PREFIX + "/")
    ]


def curriculum_owned_paths(checks_doc) -> list[str]:
    """The curriculum files the engine's own inventory names as owners."""
    return sorted(
        {
            str(entry["owner"])
            for entry in _check_entries(checks_doc)
            if str(entry.get("owner") or "").startswith(CURRICULA_PREFIX + "/")
        }
    )


def declared_domain_terms(paths, ev: Evidence | None = None):
    """Every term a curriculum declares about itself, with its anchored pattern.

    A ``*_terms`` block is the repository's existing way of saying "this word belongs
    to one curriculum and to no engine contract" — ``kit_terms`` is what ``FR-P3-SPLIT``
    and ``FR-P3-NO-LITERALS`` match on. This gate matches the same declarations against
    a different subject rather than keeping a second list, because a second
    hand-maintained copy of a vocabulary is exactly the defect that produces a
    detector which no longer sees what it was written to see.

    Returns ``(terms, problems)``. A declared term without a pattern is a problem, not
    a skip: authoring the pattern is part of authoring the term.
    """
    terms: list[tuple[str, str]] = []
    problems: list[str] = []
    for relative in paths:
        path = REPO_ROOT / relative
        if path.suffix.lower() not in (".yaml", ".yml") or not path.exists():
            continue
        doc = ev.read_for_resolution(path) if ev is not None else common._deserialize(path)
        for key, block in (doc or {}).items():
            if not key.endswith("_terms") or not isinstance(block, dict):
                continue
            for name, spec in block.items():
                pattern = (spec or {}).get("prose_pattern") if isinstance(spec, dict) else None
                if not pattern:
                    problems.append(f"term-without-prose-pattern:{relative}:{key}.{name}")
                    continue
                terms.append((str(name), pattern))
    return terms, problems


# ---------------------------------------------------------------------------
# The two relations


def engine_domain_violations(
    files, checks_doc, names: list[str], terms, ev: Evidence | None = None
) -> list[str]:
    """(a) no engine file names a ``curricula/<name>/`` path; (b) no engine-owned check
    id encodes a declared domain term.

    The scan root set is the caller's. A fixture is proven by a **separate** invocation
    pointed at the fixture path (rule 7), and that call passes no ``Evidence`` — the
    fixture run is not part of the production scan's evidence.
    """
    problems: list[str] = []

    for path in files:
        try:
            text = ev.text_of(path) if ev is not None else read_named(path)
        except (OSError, UnicodeDecodeError):
            continue
        hits: dict[str, list[int]] = {}
        for name in names:
            pattern = rf"{re.escape(CURRICULA_PREFIX)}/{re.escape(name)}/"
            for number, line in enumerate(text.splitlines(), start=1):
                found = ev.search(pattern, line) if ev is not None else re.findall(pattern, line)
                if found:
                    hits.setdefault(name, []).append(number)
        for name, lines in sorted(hits.items()):
            problems.append(
                f"engine-names-curriculum-path:{rel(path)} names "
                f"{CURRICULA_PREFIX}/{name}/ at line(s) {','.join(str(n) for n in lines)}"
            )

    for entry in engine_owned_checks(checks_doc):
        gate_id = str(entry["id"])
        for term, pattern in terms:
            found = ev.search(pattern, gate_id) if ev is not None else re.findall(pattern, gate_id)
            if found:
                problems.append(
                    f"engine-check-id-domain-term:{gate_id} is owned by "
                    f"{entry.get('owner')} and carries the curriculum-declared term {term!r}"
                )
    return problems


def _fixture_codes(path: Path, names: list[str], terms) -> str | None:
    """The distinct problem codes a fixture produces, or ``None`` if it is clean.

    Both legs are declared in one fixture's ``expected_error``, so a fixture that
    trips only one of them is recorded ``FAIL`` — each leg of the detector is proven
    to bite by its own code, and neither can go quiet behind the other.
    """
    problems = engine_domain_violations([path], common._deserialize(path), names, terms)
    if not problems:
        return None
    return " + ".join(sorted({p.split(":", 1)[0] for p in problems}))


# ---------------------------------------------------------------------------
# FR-P5-ENGINE-GENERIC


def check_engine_generic(ev: Evidence):
    names = curriculum_names(ev)
    checks_doc = ev.parse(CHECKS)
    sources = curriculum_owned_paths(checks_doc)
    ev.resolve(
        "every check owner under curricula/",
        rel(CHECKS),
        "the curriculum manifests that declare the domain's own terms",
    )
    terms, problems = declared_domain_terms(sources, ev)
    if not terms:
        problems.append(
            "no-domain-terms-declared: no curriculum manifest named as an owner in "
            f"{rel(CHECKS)} declares a *_terms block, so (b) is unmeasurable and is "
            "reported as such rather than as a pass"
        )

    files = engine_files()
    owned = engine_owned_checks(checks_doc)
    problems += engine_domain_violations(files, checks_doc, names, terms, ev)

    path_hits = [p for p in problems if p.startswith("engine-names-curriculum-path")]
    term_hits = [p for p in problems if p.startswith("engine-check-id-domain-term")]
    line = (
        f"FR-P5-ENGINE-GENERIC {'PASS' if not problems else 'FAIL'} "
        f"({len(names)} curricula, {len(terms)} declared domain terms, "
        f"{len(files)} engine files; (a) {len(path_hits)} files name a curriculum "
        f"directory, (b) {len(term_hits)} of {len(owned)} engine-owned check ids "
        f"carry a domain term)"
    )

    reject = FIXTURES / "engine_domain_leak.reject.yaml"
    accept = FIXTURES / "engine_generic.accept.yaml"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="engine-check-id-domain-term + engine-names-curriculum-path",
            detector=lambda: _fixture_codes(reject, names, terms),
        ),
        Fixture(
            name=rel(accept),
            kind="accept",
            detector=lambda: _fixture_codes(accept, names, terms),
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------

CHECKS_TABLE = {
    "engine-generic": check_engine_generic,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", required=True, choices=sorted(CHECKS_TABLE))
    args = parser.parse_args()
    ev = Evidence(gate_id=args.check)
    outcome = CHECKS_TABLE[args.check](ev)
    print(outcome.detail)
    for record in outcome.fixtures:
        print(f"  fixture {record['fixture']}: {record['outcome']} ({record['matched_error']})")
    print(f"  mechanisms: {ev.claim() or '-'}")
    return 0 if outcome.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
