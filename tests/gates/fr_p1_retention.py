"""Phase-1 gates — retention: three words, three meanings.

``deprecated/`` is a superseded artifact nothing may read; ``legacy_v3/`` is a prior
system retained as actively cited evidence; ``name.vN.ext`` is in-place coexistence
while both versions are live. Section 6 of the plan owns those definitions; these
gates prove the repository states and honours them.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
from common import Evidence, Fixture, GateFailure, REPO_ROOT, gate_result, rel  # noqa: E402

FIXTURES = common.FIXTURES_DIR

# The four folders section 4 gives a deprecated/ and section 6 requires a .gitkeep in.
DEPRECATED_FOLDERS = [
    "policy/deprecated",
    "curricula/deprecated",
    "schemas/deprecated",
    "meta_prompt/deprecated",
]

# Retained, never authorized: both v1 contracts stay in schemas/ for as long as any
# accepted record cites them (section 6). RT-6 is what eventually retires them.
RETAINED_CONTRACTS = [
    "schemas/execution_log.schema.v1.json",
    "schemas/routing_decision.schema.v1.json",
]


# ---------------------------------------------------------------------------
# FR-P1-GITKEEP


def gitkeep_violations(folders, tracked: set[str], ev: Evidence | None = None) -> list[str]:
    """A ``deprecated/`` without a tracked ``.gitkeep`` disappears on clone."""
    problems = []
    for folder in folders:
        keep = Path(folder) / ".gitkeep"
        present = ev.exists(keep) if ev is not None else keep.exists()
        if not present:
            problems.append(f"untracked-convention:{folder} has no .gitkeep")
            continue
        if tracked is not None and rel(keep) not in tracked:
            problems.append(f"untracked-convention:{rel(keep)} exists but git does not track it")
    return problems


def check_gitkeep(ev: Evidence):
    ev.note("gate_impl_fix: reads git's exit status — a failed `git ls-files` had "
            "read as 'the convention exists but git does not track it', naming an "
            "external fault as a repository defect")
    listing = ev.run(["git", "ls-files"])
    if listing.returncode != 0:
        raise GateFailure(
            f"external: git ls-files could not be run — {listing.stderr.strip()}. Whether the "
            "convention is tracked is unproven; this is the environment, not the repository."
        )
    tracked = set(listing.stdout.splitlines())
    problems = gitkeep_violations([REPO_ROOT / f for f in DEPRECATED_FOLDERS], tracked, ev)
    line = (
        f"FR-P1-GITKEEP {'PASS' if not problems else 'FAIL'} "
        f"({len(DEPRECATED_FOLDERS)} folders, {len(DEPRECATED_FOLDERS) - len(problems)} kept)"
    )

    def synthesized_detector():
        """An empty directory cannot be committed, which is the defect under test, so
        the fixture cannot be a committed file. It is built in a scratch tree."""
        scratch = Path(tempfile.mkdtemp(prefix="fr-gitkeep-"))
        try:
            (scratch / "deprecated").mkdir()
            found = gitkeep_violations([scratch / "deprecated"], set())
            return found[0] if found else None
        finally:
            import shutil

            shutil.rmtree(scratch, ignore_errors=True)

    fixtures = [
        Fixture(
            name="synthesized deprecated/ without .gitkeep",
            kind="reject",
            expected_error="untracked-convention",
            detector=synthesized_detector,
            synthesized=True,
        )
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P1-DOC


RETENTION_ROW = re.compile(r"^\|(?P<folder>[^|]+)\|(?P<answer>[^|]+)\|(?P<reason>[^|]+)\|\s*$", re.M)


def top_level_folders(ev: Evidence | None = None) -> list[str]:
    entries = ev.listdir(REPO_ROOT) if ev is not None else sorted(REPO_ROOT.iterdir())
    return sorted(p.name for p in entries if p.is_dir() and not p.name.startswith("."))


def retention_violations(doc_text: str, folders: list[str], ev: Evidence | None = None) -> list[str]:
    """Every top-level folder answered explicitly, with a reason."""
    rows = {}
    for match in RETENTION_ROW.finditer(doc_text):
        name = match.group("folder").strip().strip("`").rstrip("/")
        rows[name] = (match.group("answer").strip(), match.group("reason").strip())
    if ev is not None:
        for folder in folders:
            ev.resolve(f"{folder}/", "the repository root", "a row of AGENTS.md's retention table")
    problems = []
    for folder in folders:
        if folder not in rows:
            problems.append(f"retention-unanswered:{folder}")
            continue
        answer, reason = rows[folder]
        if not re.match(r"^(yes|no)\b", answer, re.I):
            problems.append(f"retention-unanswered:{folder} — '{answer}' is not an explicit yes/no")
        elif not reason:
            problems.append(f"retention-unanswered:{folder} — no reason given")
    return problems


def check_agents_doc(ev: Evidence):
    folders = top_level_folders(ev)
    text = ev.text_of(REPO_ROOT / "AGENTS.md")
    problems = retention_violations(text, folders, ev)
    line = (
        f"FR-P1-DOC {'PASS' if not problems else 'FAIL'} "
        f"({len(folders)} top-level folders, {len(folders) - len(problems)} answered)"
    )

    fixture = FIXTURES / "agents_missing_folder.reject.md"
    fixtures = [
        Fixture(
            name=rel(fixture),
            kind="reject",
            expected_error="retention-unanswered:docs",
            detector=lambda: (
                retention_violations(common.read_named(fixture), folders) or [None]
            )[0],
        )
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P1-SCHEMA-RETENTION


def retention_gate_violations(retired, scan_files, ev: Evidence | None = None) -> list[str]:
    """A schema may enter ``schemas/deprecated/`` only when nothing outside it refers
    to its basename. Vacuously true while the folder is empty — the gate is armed,
    not skipped."""
    problems = []
    for schema in retired:
        basename = Path(schema).name
        for path in scan_files:
            try:
                text = ev.text_of(path) if ev is not None else common.read_named(path)
            except (OSError, UnicodeDecodeError):
                continue
            hits = (
                ev.search(re.escape(basename), text) if ev is not None
                else re.findall(re.escape(basename), text)
            )
            if hits:
                if ev is not None:
                    ev.resolve(basename, rel(path), "the files inside schemas/deprecated/")
                problems.append(f"retired-schema-still-referenced:{basename} at {rel(path)}")
    return problems


def citations_of(basename: str, scan_files, ev: Evidence | None = None) -> list[str]:
    """Every production file naming ``basename``. The scan root set is rule 7's."""
    found = []
    for path in scan_files:
        try:
            text = ev.text_of(path) if ev is not None else common.read_named(path)
        except (OSError, UnicodeDecodeError):
            continue
        hits = (
            ev.search(re.escape(basename), text) if ev is not None
            else re.findall(re.escape(basename), text)
        )
        if hits:
            found.append(rel(path))
    return found


def check_schema_gate(ev: Evidence):
    deprecated = REPO_ROOT / "schemas" / "deprecated"
    retired = [p for p in ev.listdir(deprecated) if p.is_file() and p.name != ".gitkeep"]
    scan_files = [p for p in common.production_files() if deprecated not in p.parents]
    problems = retention_gate_violations(retired, scan_files, ev)

    # The other half of section 6's rule: a contract stays outside deprecated/ for as
    # long as anything still cites it, so the citations are counted, not assumed.
    still_cited = {}
    for contract in RETAINED_CONTRACTS:
        if not ev.exists(REPO_ROOT / contract):
            problems.append(f"retained-contract-missing:{contract}")
        if ev.exists(deprecated / Path(contract).name):
            problems.append(f"retained-contract-deprecated:{contract}")
        citing = citations_of(Path(contract).name, scan_files, ev)
        citing = [c for c in citing if c != contract]
        still_cited[Path(contract).name] = citing
    for contract in RETAINED_CONTRACTS:
        ev.resolve(
            Path(contract).name,
            "the retained-contract list section 6 defines",
            "schemas/, schemas/deprecated/ and every production file citing it",
        )

    state = "gate armed" if not retired else f"{len(retired)} retired"
    cited = ", ".join(f"{name} cited by {len(paths)}" for name, paths in still_cited.items())
    line = (
        f"FR-P1-SCHEMA-RETENTION {'PASS' if not problems else 'FAIL'} "
        f"({len(retired)} files, {state}; retained: {cited})"
    )

    reject = FIXTURES / "retired_but_referenced.reject.json"
    citing = FIXTURES / "retired_schema_manifest.reject.yaml"
    accept = FIXTURES / "schema_retired_unreferenced.accept.json"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="retired-schema-still-referenced",
            detector=lambda: (retention_gate_violations([reject], [citing]) or [None])[0],
        ),
        Fixture(
            name=rel(accept),
            kind="accept",
            detector=lambda: (retention_gate_violations([accept], [citing]) or [None])[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------

CHECKS = {
    "gitkeep": check_gitkeep,
    "agents-doc": check_agents_doc,
    "schema-gate": check_schema_gate,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", required=True, choices=sorted(CHECKS))
    args = parser.parse_args()
    ev = Evidence(gate_id=args.check)
    outcome = CHECKS[args.check](ev)
    print(outcome.detail)
    for record in outcome.fixtures:
        print(f"  fixture {record['fixture']}: {record['outcome']} ({record['matched_error']})")
    print(f"  mechanisms: {ev.claim() or '-'}")
    return 0 if outcome.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
