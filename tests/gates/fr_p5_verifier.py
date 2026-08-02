"""Phase-5 gate — a curriculum with no proven domain verifier does not run.

`plans/simplification/plan/simplification.plan.v3.md` §3 is the whole of this file's
reason. The research produced one number that governs the plan's shape: the closest
published proxy to designing a working circuit from datasheets, verified by simulation,
has a top-model pass rate of **8.15%**. The useful reading is not that electronics is
too hard —

    a domain is generatable exactly to the extent that it has a verifier which is
    not a model.

So genericity and safety turn out to be the same requirement, and it becomes a startup
precondition: **a curriculum declares a domain verifier, and the run refuses to start
without one.** The engine never knows what the verifier checks. It knows it must exist,
must be code, must be executable, and must have been proven against fixtures before any
unit is generated.

**The refusal is the assertion.** A precondition nothing exercises is a sentence, so
this gate does two things a declaration check would not: it *executes* every fixture the
curriculum names, against the verifier the curriculum names, and requires each to be
refused **for the code the curriculum declared** — a detector that rejects for the wrong
reason has stopped seeing what it was written to see. And it proves the refusal itself
against fixture curricula that declare no verifier and declare an unexecuted one.

The `proven` block is re-executed rather than believed. What the block adds is that the
curriculum *claimed* it: a curriculum recording `not_executed` is refused before the
engine spends anything on it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
import fr_p5_engine  # noqa: E402
from common import Evidence, Fixture, REPO_ROOT, gate_result, rel  # noqa: E402

FIXTURES = common.FIXTURES_DIR
CURRICULA_DIR = REPO_ROOT / "curricula"
RETIRED = "deprecated"

# The manifest a curriculum directory is read through. Resolved by convention at run
# time rather than by name: the engine may know that curricula declare themselves and
# must not know which curriculum is there.
MANIFEST_GLOB = "*_curriculum.v*.yaml"


def curriculum_manifests(ev: Evidence | None = None) -> list[Path]:
    """The highest-versioned manifest in each curriculum directory."""
    found: list[Path] = []
    entries = (
        ev.listdir(CURRICULA_DIR) if ev is not None
        else (sorted(CURRICULA_DIR.iterdir()) if CURRICULA_DIR.is_dir() else [])
    )
    for entry in entries:
        if not entry.is_dir() or entry.name == RETIRED:
            continue
        versioned = sorted(entry.glob(MANIFEST_GLOB))
        if versioned:
            found.append(versioned[-1])
    return found


def declaration_violations(doc, label: str) -> list[str]:
    """What is wrong with a curriculum's declaration, before anything is executed."""
    problems: list[str] = []
    verifier = ((doc or {}).get("domain") or {}).get("verifier")
    if not verifier:
        return [
            f"verifier-undeclared:{label} declares no domain verifier, so nothing but a "
            "model could tell whether its content is right. The run refuses to start."
        ]
    entry = verifier.get("entry_point")
    if not entry or not (REPO_ROOT / entry).is_file():
        problems.append(
            f"verifier-undeclared:{label} names entry point {entry!r}, which is not a file"
        )
    if not verifier.get("must_reject"):
        problems.append(
            f"verifier-unproven:{label} names no fixture its verifier must refuse; a "
            "detector that only ever accepts is not a verifier"
        )
    if not verifier.get("must_accept"):
        problems.append(
            f"verifier-unproven:{label} names no fixture its verifier must accept, so a "
            "verifier refusing everything would satisfy it entirely"
        )
    proven = verifier.get("proven") or {}
    if proven.get("result") != "all_fixtures_behaved":
        problems.append(
            f"verifier-unproven:{label} records result {proven.get('result')!r}; a "
            "curriculum whose fixtures have not been executed does not run"
        )
    return problems


def execution_violations(doc, label: str, ev: Evidence) -> list[str]:
    """Run the declared verifier against every fixture the curriculum names."""
    problems: list[str] = []
    verifier = ((doc or {}).get("domain") or {}).get("verifier") or {}
    entry = verifier.get("entry_point")
    if not entry or not (REPO_ROOT / entry).is_file():
        return problems  # already reported; there is nothing to run

    for row in verifier.get("must_reject") or []:
        fixture, expected = row.get("fixture"), str(row.get("expected_code", ""))
        proc = ev.run([sys.executable, entry, "--domain", str(fixture)])
        if proc.returncode == 0:
            problems.append(
                f"verifier-fixture-accepted:{label} — {fixture} must be refused for "
                f"{expected!r} and was accepted"
            )
        elif expected not in proc.stdout:
            problems.append(
                f"verifier-fixture-wrong-reason:{label} — {fixture} was refused, and not "
                f"for {expected!r}: {proc.stdout.strip().splitlines()[:1]}"
            )
    for fixture in verifier.get("must_accept") or []:
        proc = ev.run([sys.executable, entry, "--domain", str(fixture)])
        if proc.returncode != 0:
            problems.append(
                f"verifier-fixture-refused:{label} — {fixture} must be accepted and was "
                f"refused: {proc.stdout.strip().splitlines()[:1]}"
            )
    return problems


def check_verifier_required(ev: Evidence):
    manifests = curriculum_manifests(ev)
    problems: list[str] = []
    if not manifests:
        problems.append(
            "verifier-undeclared: no curriculum manifest was found at all, so the "
            "precondition is unmeasurable and is reported as such rather than as a pass"
        )

    executed = 0
    for path in manifests:
        doc = ev.parse(path)
        label = rel(path)
        ev.resolve(
            "the domain verifier",
            label + " domain.verifier",
            "the entry point and the fixtures it names",
        )
        found = declaration_violations(doc, label)
        problems += found
        if not found:
            problems += execution_violations(doc, label, ev)
            verifier = ((doc or {}).get("domain") or {}).get("verifier") or {}
            executed += len(verifier.get("must_reject") or []) + len(verifier.get("must_accept") or [])

    line = (
        f"FR-P5-VERIFIER-REQUIRED {'PASS' if not problems else 'FAIL'} "
        f"({len(manifests)} curricula, each declaring a verifier; {executed} declared "
        f"fixtures executed against it, each refused for its own declared code)"
    )
    undeclared = FIXTURES / "curriculum_without_verifier.reject.yaml"
    unproven = FIXTURES / "curriculum_verifier_unproven.reject.yaml"
    accept = FIXTURES / "curriculum_verifier_declared.accept.yaml"
    fixtures = [
        Fixture(
            name=rel(undeclared),
            kind="reject",
            expected_error="verifier-undeclared",
            detector=lambda: (
                declaration_violations(common._deserialize(undeclared), rel(undeclared)) or [None]
            )[0],
        ),
        Fixture(
            name=rel(unproven),
            kind="reject",
            expected_error="verifier-unproven",
            detector=lambda: (
                declaration_violations(common._deserialize(unproven), rel(unproven)) or [None]
            )[0],
        ),
        Fixture(
            name=rel(accept),
            kind="accept",
            detector=lambda: (
                declaration_violations(common._deserialize(accept), rel(accept)) or [None]
            )[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------

CHECKS_TABLE = {"verifier-required": check_verifier_required}


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
