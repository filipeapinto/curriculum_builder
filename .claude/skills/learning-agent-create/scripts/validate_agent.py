#!/usr/bin/env python3
"""Preflight one created agent's artifact set.

Usage:
    validate_agent.py <CHECK-ID> [--repo <path>]

Answers one question: is this agent's artifact set complete and internally
consistent, or is there a dangling half? It is a preflight and not the
authority — `./tests/run_gates.sh 5` is, and it is what will actually reject a
malformed entry. This exists because the failure mode it catches is silent:
an id that validates against its schema while its fixture is missing, its
release surface never added, or its `verified_by` naming a gate that was
never registered, all look fine until the suite runs.

Exits non-zero if any check fails. Warnings do not affect the exit code.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("error: PyYAML is required (it is already a dependency of this repo)", file=sys.stderr)
    raise SystemExit(2)

METHODS = {"tree", "parse", "schema", "text", "mapping", "declaration", "execution"}
STAGES = {"static", "deterministic", "golden", "logger", "live-capability"}
ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(-[A-Z0-9]+)+$")
RESERVED_KEYS = {"checks_version", "schema", "release"}


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.passes: list[str] = []

    def ok(self, message: str) -> None:
        self.passes.append(message)

    def fail(self, message: str) -> None:
        self.failures.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def find_repo(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "policy" / "checks.v1.yaml").is_file():
            return candidate
    raise SystemExit("error: could not find a repo root holding policy/checks.v1.yaml")


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def inventories(repo: Path) -> list[Path]:
    found = [repo / "policy" / "checks.v1.yaml"]
    curricula = repo / "curricula"
    if curricula.is_dir():
        for entry in sorted(curricula.iterdir()):
            if entry.is_dir() and entry.name != "deprecated":
                candidate = entry / "checks.v1.yaml"
                if candidate.is_file():
                    found.append(candidate)
    return [path for path in found if path.is_file()]


def entries_of(document: dict) -> list[tuple[str, dict]]:
    out = []
    for key, value in document.items():
        if key in RESERVED_KEYS or not isinstance(value, list):
            continue
        for item in value:
            if isinstance(item, dict) and "id" in item:
                out.append((key, item))
    return out


def advertises(pattern: str, check_id: str) -> bool:
    if pattern.endswith("*"):
        return check_id.startswith(pattern[:-1])
    return pattern == check_id


def registry_gate_ids(repo: Path) -> set[str]:
    path = repo / "tests" / "gates" / "registry.py"
    if not path.is_file():
        return set()
    return set(re.findall(r'"id":\s*"(FR-[A-Z0-9-]+)"', path.read_text(encoding="utf-8")))


def deferred_ids(repo: Path) -> set[str]:
    path = repo / "policy" / "deferred.v1.yaml"
    if not path.is_file():
        return set()
    document = load_yaml(path)
    return {item["id"] for item in document.get("deferred", []) if isinstance(item, dict) and "id" in item}


def check_fixture(repo: Path, report: Report, declared: str) -> None:
    path = repo / declared
    if not (path.is_file() or path.is_dir()):
        report.fail(f"fixture {declared} does not exist")
        return
    report.ok(f"fixture {declared} exists")
    if ".reject." not in declared and not declared.endswith(".reject"):
        return
    stem = declared.replace(".reject", ".accept")
    if (repo / stem).is_file() or (repo / stem).is_dir():
        report.ok(f"accept counterpart {stem} exists")
        return
    # The pair need not be named by a mechanical swap — `unit_bloom_verb_below_level`
    # pairs with `unit_bloom_verb_matches_level`, because each name describes its own
    # condition rather than being the other's negation. Accept a shared prefix, and say
    # which file was taken as the partner so a wrong guess is visible rather than silent.
    slug = Path(declared).name.split(".reject")[0]
    segments = slug.split("_")
    partners = [
        candidate
        for candidate in sorted((repo / "tests" / "fixtures").glob("*.accept*"))
        if len({*segments} & {*candidate.name.split(".accept")[0].split("_")}) >= 2
        and candidate.name.split("_")[0] == segments[0]
    ]
    if partners:
        report.ok(
            f"accept counterpart for {declared} read as {partners[0].name} "
            f"(names do not pair by a .reject/.accept swap)"
        )
    else:
        report.fail(
            f"no accept counterpart for {declared} — a reject fixture alone proves the "
            f"detector refuses something, never that it admits the corrected form"
        )


def validate(check_id: str, repo: Path) -> Report:
    report = Report()

    if not ID_PATTERN.match(check_id):
        report.fail(f"{check_id} does not match ^[A-Z][A-Z0-9]*(-[A-Z0-9]+)+$")
    if check_id.startswith("FR-"):
        report.fail(f"{check_id} is FR- prefixed — that namespace belongs to refactor gates, not checks")

    homes = []
    for path in inventories(repo):
        document = load_yaml(path)
        for category, entry in entries_of(document):
            if entry["id"] == check_id:
                homes.append((path, category, entry, document))

    if not homes:
        report.fail(f"{check_id} appears in no check inventory")
        return report
    if len(homes) > 1:
        names = ", ".join(str(path.relative_to(repo)) for path, _, _, _ in homes)
        report.fail(f"{check_id} appears in more than one inventory ({names}) — one id, one home")
    path, category, entry, document = homes[0]
    report.ok(f"{check_id} found in {path.relative_to(repo)} under `{category}`")

    for field in ("asserts", "owner", "method"):
        if not entry.get(field):
            report.fail(f"required field `{field}` is missing or empty")
    if len(str(entry.get("asserts", ""))) < 10:
        report.fail("`asserts` is shorter than the 10-character floor its contract sets")

    method = entry.get("method")
    if method and method not in METHODS:
        report.fail(f"method {method!r} is not one of {sorted(METHODS)}")
    elif method:
        report.ok(f"method {method!r} is in the vocabulary")

    owner = entry.get("owner")
    if owner:
        owner_path = repo / owner
        if not owner_path.exists():
            report.fail(f"owner {owner} does not exist")
        else:
            report.ok(f"owner {owner} exists")
            try:
                if check_id in owner_path.read_text(encoding="utf-8"):
                    report.ok(f"owner {owner} names {check_id}")
                else:
                    report.fail(
                        f"owner {owner} does not name {check_id} — an owner is the file that "
                        f"states the rule, and a file that never mentions the id states nothing. "
                        f"(The executed gate checks only that the owner path exists; this is the "
                        f"stronger contract schemas/checks.schema.v1.json states, and a few "
                        f"pre-existing ids do not meet it.)"
                    )
            except (UnicodeDecodeError, IsADirectoryError):
                report.warn(f"owner {owner} is not readable as text; could not confirm it names the id")

    verified_by, deferred = entry.get("verified_by"), entry.get("deferred")
    if bool(verified_by) == bool(deferred):
        report.fail(
            "exactly one of `verified_by` or `deferred` is required — "
            f"got verified_by={verified_by!r}, deferred={deferred!r}. "
            "Being listed is not being executed, and the two are never conflated."
        )
    elif verified_by:
        if verified_by in registry_gate_ids(repo):
            report.ok(f"verified_by {verified_by} is a gate in tests/gates/registry.py")
        else:
            report.fail(f"verified_by {verified_by} is not a gate registered in tests/gates/registry.py")
    else:
        if deferred in deferred_ids(repo):
            report.ok(f"deferred {deferred} resolves in policy/deferred.v1.yaml")
        else:
            report.fail(f"deferred {deferred} is not an id in policy/deferred.v1.yaml")

    stage = entry.get("stage")
    if not stage:
        report.warn("no `stage` declared, so no release row can advertise this id")
    elif stage not in STAGES:
        report.fail(f"stage {stage!r} is not one of {sorted(STAGES)}")
    else:
        rows = [row for row in document.get("release", []) if row.get("stage") == stage]
        matched = [
            pattern
            for row in rows
            for pattern in row.get("advertises", [])
            if advertises(pattern, check_id)
        ]
        if matched:
            report.ok(f"advertised at stage {stage} by {', '.join(matched)}")
        elif not document.get("release"):
            report.warn(
                f"{path.relative_to(repo)} carries no release table; the engine's inventory is "
                f"advertised by the composed contract's release table — confirm {check_id} is in it"
            )
        else:
            report.fail(
                f"no release pattern in {path.relative_to(repo)} advertises {check_id} at stage "
                f"{stage} — an id with no surface has quietly stopped being claimed"
            )

    declared_fixtures = [
        str(value)
        for key in ("fixture", "artifact")
        for value in [entry.get(key)]
        if value and str(value).startswith("tests/fixtures/")
    ]
    if declared_fixtures:
        for declared in declared_fixtures:
            check_fixture(repo, report, declared)
    else:
        report.warn(
            "no `fixture` under tests/fixtures/ is declared — without a fixture pair the "
            "detector's behaviour is asserted rather than executed"
        )

    if owner == "policy/failures.v1.yaml":
        ledger = load_yaml(repo / "policy" / "failures.v1.yaml")
        naming = [
            item.get("id")
            for value in ledger.values()
            if isinstance(value, list)
            for item in value
            if isinstance(item, dict) and check_id in (item.get("checks") or [])
        ]
        if naming:
            report.ok(f"failure ledger entry {', '.join(naming)} names {check_id} in its `checks` list")
        else:
            report.fail(
                f"owner is the failure ledger but no entry there lists {check_id} under `checks` — "
                f"the link back is what makes the ledger this id's owner in more than name"
            )

    dossier = repo / "docs" / "agents" / f"{check_id}.md"
    if dossier.is_file() and dossier.stat().st_size > 0:
        report.ok(f"dossier {dossier.relative_to(repo)} exists")
    else:
        report.fail(
            f"no dossier at docs/agents/{check_id}.md — provenance carried from the scan has "
            f"nowhere to live, and a later reader cannot tell a verified citation from an invented one"
        )

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("check_id")
    parser.add_argument("--repo", default=None, help="repo root; found by walking up from cwd if omitted")
    args = parser.parse_args()

    repo = Path(args.repo).resolve() if args.repo else find_repo(Path.cwd().resolve())
    report = validate(args.check_id, repo)

    for message in report.passes:
        print(f"  ok    {message}")
    for message in report.warnings:
        print(f"  warn  {message}")
    for message in report.failures:
        print(f"  FAIL  {message}")

    verdict = "INCOMPLETE" if report.failures else "COMPLETE"
    print(
        f"\n{args.check_id}: artifact set {verdict} "
        f"({len(report.passes)} ok, {len(report.warnings)} warnings, {len(report.failures)} failures)"
    )
    print("This is a preflight. Run ./tests/run_gates.sh 5 for the authoritative verdict.")
    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
