"""Phase-0 gates — harness registry, tree, references, parsing, validation, history.

Every path literal this module searches for lives in this file, which is exactly why
harness rule 7 excludes ``tests/gates/**`` from the production scan root set: a
detector must contain the literals it hunts, so scanning its own source would make
``FR-P0-NOSTALE`` flag itself on the first run.

Reading a **named** file under an excluded root is not a scan (rule 7). This module
opens the folder plan's sections 4 and 5, **each gate family's catalogue section** and
``tests/gates/registry.py`` by name, and ``FR-P0-PLANREF`` deliberately globs
``plans/folder_refactoring/`` — for version relationships only, never for path
literals. Which plan owns which gate family, and which of its sections holds the
catalogue, is read from ``tests/gates/gate_families.v1.yaml`` rather than written
here: a folder name in a detector is what made every gate belong to one plan.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
from common import (  # noqa: E402
    Evidence,
    Fixture,
    GateFailure,
    PLAN_DIR,
    REPO_ROOT,
    active_plan_path,
    gate_result,
    plan_section,
    read_named,
    rel,
)

FIXTURES = common.FIXTURES_DIR

# The stale-path terms. Each is anchored so an ordinary word never trips it.
STALE_TERMS = [
    ("assets/", r"(?<![A-Za-z0-9_./])assets/"),
    ("schema/", r"(?<![A-Za-z0-9_./])schema/"),
    ("meta_prompt/routing/", r"meta_prompt/routing/"),
    ("work/elegoo_labs", r"work/elegoo_labs"),
    ("pedagogy.md", r"(?<![A-Za-z0-9_./])pedagogy\.md"),
]

# The four source directories and the one root file the moves retire.
RETIRED_PATHS = ["assets", "schema", "meta_prompt/routing", "pedagogy.md"]


# ---------------------------------------------------------------------------
# Reading the active plan's sections 4 and 5


def parse_target_tree(section4: str) -> list[dict]:
    """Section 4's tree, one entry per line, as ``{path, name, annotation, is_dir}``.

    Section 4 owns the *destination list*; section 5 owns the rationale and the
    rule grouping. Continuation lines carrying only wrapped annotation text have no
    connector and are skipped.
    """
    block = re.search(r"```\n(curriculum_builder/\n.*?)```", section4, re.S)
    if not block:
        raise GateFailure("section 4 has no target-tree code block")
    entries: list[dict] = []
    parents: dict[int, str] = {}
    for line in block.group(1).splitlines():
        connector = re.search(r"(├── |└── )", line)
        if not connector:
            continue
        depth = connector.start() // 4
        rest = line[connector.end():]
        name = rest.split("  ")[0].strip()
        if not name:
            continue
        annotation = rest[rest.index(name) + len(name):].strip()
        is_dir = name.endswith("/")
        prefix = [parents[d] for d in range(depth) if d in parents]
        path = "/".join(prefix + [name.rstrip("/")])
        if is_dir:
            parents[depth] = name.rstrip("/")
            for deeper in [d for d in parents if d > depth]:
                del parents[deeper]
        entries.append(
            {"path": path, "name": name.rstrip("/"), "annotation": annotation, "is_dir": is_dir}
        )
    return entries


def parse_move_rules(section5: str) -> list[dict]:
    """Section 5's 13 rows as ``{n, source, dest, files}``."""
    rules = []
    for line in section5.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not cells[0].isdigit():
            continue
        rules.append(
            {
                "n": int(cells[0]),
                "source": cells[1].strip("`"),
                "dest": cells[2].strip("`"),
                "files": int(cells[3]),
            }
        )
    return rules


def _marker_source(annotation: str) -> str:
    """The source a ``←`` marker names, or ``""`` when there is no marker."""
    if "←" not in annotation:
        return ""
    tail = annotation.split("←", 1)[1].strip()
    tail = re.sub(r"^(was|from)\s+", "", tail)
    return tail.split()[0] if tail.split() else ""


def resolve_destinations(entries: list[dict], rules: list[dict]) -> dict[int, list[str]]:
    """Group section 4's destinations under section 5's 13 rules.

    A row whose ``From`` is a glob or a directory cannot be expanded at run time —
    this very gate asserts those source directories no longer exist — so its
    destinations are the section-4 entries directly under its ``To`` folder that are
    neither ``NEW`` in a later phase, nor a retention ``.gitkeep``, nor claimed by
    another rule through a ``←`` marker naming a different source.
    """
    by_path = {e["path"]: e for e in entries}
    grouped: dict[int, list[str]] = {}

    for rule in rules:
        source, dest = rule["source"], rule["dest"]
        is_group = source.endswith("/") or "*" in source
        if not is_group:
            target = dest + Path(source).name if dest.endswith("/") else dest
            grouped[rule["n"]] = [target]
            continue

        folder = dest.rstrip("/")
        suffix = Path(source).suffix if "*" in source else ""
        picked = []
        for entry in entries:
            if entry["is_dir"] or str(Path(entry["path"]).parent) != folder:
                continue
            if "NEW" in entry["annotation"] or entry["name"] == ".gitkeep":
                continue
            if entry["name"].endswith(".gitkeep"):
                continue
            if suffix and not entry["name"].endswith(suffix):
                continue
            marker = _marker_source(entry["annotation"])
            if marker and not source.startswith(marker.rstrip("/")):
                continue  # claimed by a different rule
            picked.append(entry["path"])
        grouped[rule["n"]] = sorted(picked)

    del by_path
    return grouped


def destination_files(ev: Evidence | None = None):
    """The destination list section 8 requires, read from sections 4 and 5.

    When an ``Evidence`` is passed, the plan is read through it and every rule is
    resolved through it, so the gate's ``text`` and ``mapping`` claims are made by
    the work rather than beside it.
    """
    plan_path = active_plan_path()
    plan = ev.text_of(plan_path) if ev is not None else read_named(plan_path)
    entries = parse_target_tree(plan_section(plan, 4))
    rules = parse_move_rules(plan_section(plan, 5))
    grouped = resolve_destinations(entries, rules)
    if ev is not None:
        for rule in rules:
            ev.resolve(
                f"move rule {rule['n']} ({rule['source']} → {rule['dest']})",
                f"{rel(plan_path)} section 5",
                f"{rel(plan_path)} section 4's tree entries",
            )
    files = [p for n in sorted(grouped) for p in grouped[n]]
    return files, rules, grouped


# ---------------------------------------------------------------------------
# FR-P0-TREE


def check_tree(ev: Evidence):
    plan = ev.text_of(active_plan_path())
    entries = parse_target_tree(plan_section(plan, 4))
    _, rules, grouped = destination_files(ev)

    problems: list[str] = []
    if len(rules) != 13:
        problems.append(f"section 5 declares {len(rules)} rules, expected 13")

    known = {e["path"] for e in entries}
    total = 0
    for rule in rules:
        resolved = grouped[rule["n"]]
        total += len(resolved)
        if len(resolved) != rule["files"]:
            problems.append(
                f"rule {rule['n']} ({rule['source']} → {rule['dest']}): "
                f"resolved {len(resolved)} files, section 5 declares {rule['files']}"
            )
        for path in resolved:
            if path not in known:
                problems.append(f"rule {rule['n']}: {path} is not an entry in section 4's tree")

    if total != 26:
        problems.append(f"resolved {total} destination files, section 5's counts total 26")

    # Every section-4 entry carrying a ← marker must be one of the destinations.
    destinations = {p for paths in grouped.values() for p in paths}
    for entry in entries:
        if entry["is_dir"] or not _marker_source(entry["annotation"]):
            continue
        if "NEW" in entry["annotation"]:
            continue
        if entry["path"] not in destinations:
            problems.append(f"{entry['path']} carries a ← marker but no rule claims it")

    missing = [p for p in sorted(destinations) if not ev.exists(REPO_ROOT / p)]
    problems.extend(f"missing destination: {p}" for p in missing)

    legacy = [p for p in RETIRED_PATHS if ev.exists(REPO_ROOT / p)]
    problems.extend(f"retired path still exists: {p}" for p in legacy)

    line = (
        f"FR-P0-TREE {'PASS' if not problems else 'FAIL'} "
        f"({len(rules)} rules, {total - len(missing)}/{total} files, {len(legacy)} legacy paths)"
    )
    return gate_result(not problems, line if not problems else line + " — " + "; ".join(problems),
                       stdout=line)


# ---------------------------------------------------------------------------
# FR-P0-NOSTALE


def scan_for_stale(paths, ev: Evidence | None = None) -> list[str]:
    """Every stale-path hit in the given files. The scan root set is the caller's.

    A detector is proven against its own fixture by a **separate** invocation
    pointed at the fixture path (rule 7) — that call passes no ``Evidence``,
    because the fixture run is not part of the production scan's evidence.
    """
    hits = []
    for path in paths:
        try:
            text = ev.text_of(path) if ev is not None else read_named(path)
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in STALE_TERMS:
                found = ev.search(pattern, line) if ev is not None else re.findall(pattern, line)
                if found:
                    hits.append(f"stale-path:{label} at {rel(path)}:{number}")
    return hits


def _tracked_production_files(ev: Evidence) -> list[Path]:
    """Tracked files, minus rule 7's exclusions. ``plans/**`` is excluded on purpose
    and permanently: a plan that describes a move must name the paths it moves."""
    listing = ev.run(["git", "ls-files"])
    if listing.returncode != 0:
        raise GateFailure(f"git ls-files failed: {listing.stderr.strip()}")
    files = []
    for name in listing.stdout.splitlines():
        top = name.split("/")[0]
        if top in common.PRODUCTION_EXCLUDED_TOP_LEVEL or top in common.PRODUCTION_EXCLUDED_ANYWHERE:
            continue
        path = REPO_ROOT / name
        if path.suffix.lower() in common.BINARY_SUFFIXES or not path.exists():
            continue
        files.append(path)
    return files


def check_stale(ev: Evidence):
    files = _tracked_production_files(ev)
    hits = scan_for_stale(files, ev)
    line = f"FR-P0-NOSTALE {'PASS' if not hits else 'FAIL'} ({len(hits)} hits, {len(files)} files scanned)"

    fixture = FIXTURES / "stale_reference.reject.md"
    fixtures = [
        Fixture(
            name=rel(fixture),
            kind="reject",
            expected_error="stale-path:assets/",
            detector=lambda: (scan_for_stale([fixture]) or [None])[0],
        )
    ]
    detail = line if not hits else line + " — " + "; ".join(hits[:20])
    return gate_result(not hits, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P0-PLANREF


def _plan_pairs(folder: Path, ev: Evidence | None = None) -> dict[str, dict[int, Path]]:
    found = {"plan": {}, "prompt": {}}
    listing = (
        ev.glob(folder, "folder_refactoring.*.v*.md") if ev is not None
        else sorted(folder.rglob("folder_refactoring.*.v*.md"))
    )
    for path in listing:
        match = re.match(r"folder_refactoring\.(plan|prompt)\.v(\d+)\.md$", path.name)
        if match:
            found[match.group(1)][int(match.group(2))] = path
    return found


def planref_violations(folder: Path, ev: Evidence | None = None) -> list[str]:
    """The four version relationships, checked against any plan folder.

    This is the one place a production gate globs ``plans/`` — for version
    relationships only, never for path literals (rule 7).
    """
    read = (lambda p: ev.text_of(p)) if ev is not None else read_named
    found = _plan_pairs(folder, ev)
    problems: list[str] = []
    if not found["plan"] or not found["prompt"]:
        return ["plan-ref-stale: no versioned plan/prompt pair found"]

    top_plan, top_prompt = max(found["plan"]), max(found["prompt"])
    if top_plan != top_prompt:
        problems.append(
            f"plan-ref-stale: highest plan is v{top_plan} but highest prompt is v{top_prompt}"
        )
    version = max(top_plan, top_prompt)

    plan_path = folder / f"folder_refactoring.plan.v{version}.md"
    prompt_path = folder / f"folder_refactoring.prompt.v{version}.md"
    for path in (plan_path, prompt_path):
        present = ev.exists(path) if ev is not None else path.exists()
        if not present:
            problems.append(f"plan-ref-stale: {path.name} is not at the plan folder root")
    if problems:
        return problems

    if ev is not None:
        ev.resolve(
            f"the v{version} plan named by the prompt's goal",
            prompt_path.name,
            f"the versioned files present in {rel(folder)}",
        )
    prompt_text = read(prompt_path)
    goal = re.search(r"^## Goal$(.*?)^## ", prompt_text, re.S | re.M)
    goal_text = goal.group(1) if goal else prompt_text
    if f"folder_refactoring.plan.v{version}.md" not in goal_text:
        problems.append(
            f"plan-ref-stale: {prompt_path.name}'s goal does not name "
            f"folder_refactoring.plan.v{version}.md"
        )

    plan_text = read(plan_path)
    try:
        tree = plan_section(plan_text, 4)
        ledger = plan_section(plan_text, 10)
    except GateFailure as exc:
        return problems + [f"plan-ref-stale: {exc}"]
    if f"folder_refactoring.plan.v{version}.md" not in tree or \
            f"folder_refactoring.prompt.v{version}.md" not in tree:
        problems.append(f"plan-ref-stale: section 4 does not name the v{version} pair as active")
    if f"v{version}" not in ledger:
        problems.append(f"plan-ref-stale: section 10 does not name v{version} as the active pair")

    for kind in ("plan", "prompt"):
        for number, path in found[kind].items():
            if number < version and path.parent.name != "deprecated":
                problems.append(f"plan-ref-stale: {path.name} is superseded but not under deprecated/")
    return problems


def check_planref(ev: Evidence):
    problems = planref_violations(PLAN_DIR, ev)
    pairs = _plan_pairs(PLAN_DIR, ev)
    version = max(pairs["plan"] or {0: None})
    archived = sum(
        1
        for kind in ("plan", "prompt")
        for number, path in pairs[kind].items()
        if path.parent.name == "deprecated"
    )
    line = (
        f"FR-P0-PLANREF {'PASS' if not problems else 'FAIL'} "
        f"(active pair v{version}, {archived} superseded files archived)"
    )
    if not problems and archived != 2 * (version - 1):
        problems.append(
            f"plan-ref-stale: expected {2 * (version - 1)} archived files, found {archived}"
        )

    fixture_dir = FIXTURES / "planref_stale_pair.reject"
    fixtures = [
        Fixture(
            name=rel(fixture_dir),
            kind="reject",
            expected_error="plan-ref-stale",
            detector=lambda: (planref_violations(fixture_dir) or [None])[0],
        )
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P0-PARSE


def parse_error(path: Path, ev: Evidence | None = None) -> str | None:
    try:
        ev.parse(path) if ev is not None else common._deserialize(path)
    except Exception as exc:  # noqa: BLE001 - the error text is the evidence
        return f"{type(exc).__module__}.{type(exc).__name__}: {exc}"
    return None


def check_parse(ev: Evidence):
    targets = ev.select(
        [p for root in ("policy", "curricula") for p in (REPO_ROOT / root).rglob("*.yaml")]
        + [p for root in ("schemas", "curricula") for p in (REPO_ROOT / root).rglob("*.json")]
    )
    problems = []
    for path in targets:
        error = parse_error(path, ev)
        if error:
            problems.append(f"{rel(path)}: {error}")
    line = f"FR-P0-PARSE {'PASS' if not problems else 'FAIL'} ({len(targets)} files parsed)"

    malformed = FIXTURES / "malformed_manifest.reject.yaml"
    fixtures = [
        Fixture(
            name=rel(malformed),
            kind="reject",
            expected_error="yaml.scanner.ScannerError",
            detector=lambda: parse_error(malformed),
        )
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P0-SCHEMA


# gate_impl_fix: the pairing follows the live contract rather than a constant naming
# the one this repository started with. A gate pinned to a superseded pairing validates
# a retired contract and reports it as the live one — a wrong subject, not a weakened
# criterion, and the criterion is unchanged: the live curriculum validates against the
# contract it declares, and the calibration against its own.
CURRICULUM_INSTANCE = "curricula/arduino_kit/arduino_kit_curriculum.v5.yaml"
CURRICULUM_SCHEMA = "schemas/curriculum.schema.v5.json"
CALIBRATION_INSTANCE = "policy/calibration.v1.yaml"
CALIBRATION_SCHEMA = "schemas/calibration.schema.v1.json"


def check_schema(ev: Evidence):
    """AGENTS.md's validation command at the new paths. Both schema paths are
    literals here, so no cross-file resolution occurs and the class is ``schema``
    alone, deliberately."""
    problems = []
    for instance, schema in (
        (CURRICULUM_INSTANCE, CURRICULUM_SCHEMA),
        (CALIBRATION_INSTANCE, CALIBRATION_SCHEMA),
    ):
        error = ev.validate(REPO_ROOT / instance, REPO_ROOT / schema)
        if error:
            problems.append(f"{instance}: {error}")
    line = f"FR-P0-SCHEMA {'PASS' if not problems else 'FAIL'} (2 manifests validated)"

    reject = FIXTURES / "curriculum_missing_labs.reject.yaml"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="ValidationError:'labs' is a required property",
            detector=lambda: common._validate_obj(
                common._deserialize(reject), common._deserialize(REPO_ROOT / CURRICULUM_SCHEMA)
            ),
        )
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P0-HISTORY


def check_history(ev: Evidence):
    files, rules, grouped = destination_files(ev)

    root = ev.run(["git", "rev-list", "--max-parents=0", "HEAD"])
    if root.returncode != 0:
        raise GateFailure(f"external: git could not be run — {root.stderr.strip()}")
    baseline = root.stdout.split()
    if not baseline:
        raise GateFailure("no baseline commit found")
    baseline_sha = baseline[-1]

    problems = []
    followed = 0
    for path in files:
        log = ev.run(["git", "log", "--follow", "--format=%H", "--", path])
        if log.returncode != 0:
            raise GateFailure(
                f"external: git log --follow {path} failed — {log.stderr.strip()}. "
                "This is the environment, not the repository; provenance is unproven, "
                "not lost."
            )
        if baseline_sha in log.stdout.split():
            followed += 1
        else:
            problems.append(f"git log --follow {path} does not reach the baseline commit")
        ev.resolve(path, "section 4's target tree", f"the history of {path} back to {baseline_sha[:8]}")

    # gate_impl_fix: the rename is recorded in the commit that performed it, not at
    # the tip. Reading HEAD passed at phase 0 and then failed at phase 1 for a
    # repository that had not changed — a wrong subject, not a weakened criterion.
    # The claim is unchanged: each rule-1 file's own history must contain an R entry
    # from its schema/ source rather than an A/D pair.
    ev.note("gate_impl_fix: (b) reads each file's own history, not HEAD, so the "
            "rename stays provable once later phases land on top of it")
    pairs = []
    for dest in grouped.get(1, []):
        shown = ev.run(
            ["git", "log", "--follow", "--name-status", "-M", "--format=commit:%h", "--", dest]
        )
        if shown.returncode != 0:
            raise GateFailure(
                f"external: git log --name-status {dest} failed — {shown.stderr.strip()}"
            )
        found = None
        for line in shown.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) == 3 and parts[0].startswith("R") and parts[2] == dest:
                found = (parts[1], parts[0])
                break
        if found is None:
            problems.append(
                f"{dest} is not recorded as a rename anywhere in its history (added/deleted instead)"
            )
            continue
        source, score = found
        if not source.startswith("schema/"):
            problems.append(f"{dest} is a rename from {source}, not from schema/")
        pairs.append(f"{source} → {dest} ({score})")

    line = (
        f"FR-P0-HISTORY {'PASS' if not problems else 'FAIL'} "
        f"({followed}/{len(files)} files follow to baseline; "
        f"rule-1 renames: {', '.join(pairs) or 'none'})"
    )
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, stdout=line)


# ---------------------------------------------------------------------------
# FR-P0-DEPS and FR-P0-CLEAN


def check_deps(ev: Evidence):
    proc = ev.run([sys.executable, "-c", "import jsonschema, yaml; print('DEPS OK')"])
    ok = proc.returncode == 0 and "DEPS OK" in proc.stdout
    detail = "DEPS OK" if ok else f"environment: {proc.stderr.strip() or proc.stdout.strip()}"
    return gate_result(ok, detail, stdout=proc.stdout)


def check_clean(ev: Evidence):
    ev.note("gate_impl_fix: reads git's exit status — an empty result from a failed "
            "`git status` had read as a clean worktree, which is a false PASS on the "
            "one gate that guards APPROVED")
    proc = ev.run(["git", "status", "--porcelain"])
    if proc.returncode != 0:
        raise GateFailure(
            f"external: git status could not be run — {proc.stderr.strip()}. The worktree is "
            "unproven, not clean; an empty result from a failed git is never a pass."
        )
    dirty = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    detail = "FR-P0-CLEAN PASS (worktree clean)" if not dirty else (
        "FR-P0-CLEAN FAIL — " + "; ".join(dirty[:20])
    )
    return gate_result(not dirty, detail, stdout=proc.stdout)


# ---------------------------------------------------------------------------
# FR-P0-REGISTRY


GATE_HEADER = re.compile(r"^\*\*`(FR-[A-Z0-9\-]+)`\*\*\s*·", re.M)


def parse_gate_catalogue(section8: str) -> dict[str, dict]:
    """Section 8's gate headers. The encoding is fixed by the plan: everything after
    an em dash in a header field is rationale, and ``depends_on`` is the set of
    backticked ``FR-`` ids appearing anywhere in that field."""
    catalogue: dict[str, dict] = {}
    matches = list(GATE_HEADER.finditer(section8))
    for index, match in enumerate(matches):
        gate_id = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section8)
        body = section8[match.start():end]
        header_lines = []
        for line in body.splitlines():
            if re.match(r"^`(python3|git|\./)", line):
                break
            header_lines.append(line)
        header = " ".join(header_lines)
        fields = header.split("·")
        if len(fields) < 4:
            continue
        phase = fields[1].strip()
        if gate_id == "FR-ALL" or not phase.isdigit():
            continue  # FR-ALL is the regression run, not one of the 31 gates
        catalogue[gate_id] = {
            "activation_phase": int(phase),
            "claim_class": fields[2].strip().strip("`"),
            "depends_on": sorted(set(re.findall(r"`(FR-[A-Z0-9\-]+)`", "·".join(fields[3:])))),
        }
    return catalogue


def compare_registry(
    catalogues: dict[str, dict[str, dict]], families: list[dict], gates: list[dict]
) -> list[str]:
    """(a)-(c): the registry against **each family's** catalogue section.

    The registry composes from several plans, each owning the gate-id prefixes the
    family manifest gives it. A registered gate is compared against the catalogue of
    the family its id belongs to — never against the union — so a gate declared by one
    plan and prefixed for another is a reported mismatch rather than an accidental
    pass, and a gate no family owns is reported rather than filed somewhere.
    """
    problems = []
    registered = {g["id"]: g for g in gates}
    for family in families:
        name = family["family"]
        for gate_id, declared in catalogues.get(name, {}).items():
            owner = common.family_of_gate_id(gate_id, families)
            if owner is None or owner["family"] != name:
                problems.append(
                    f"gate-family-mismatch:{gate_id} is declared by {name} but its id prefix "
                    f"is owned by {owner['family'] if owner else 'no family'}"
                )
            entry = registered.get(gate_id)
            if entry is None:
                problems.append(f"gate-declared-in-plan-not-registered:{gate_id}")
                continue
            problems += _compare_one(gate_id, entry, declared)
    for gate_id in registered:
        owner = common.family_of_gate_id(gate_id, families)
        if owner is None:
            problems.append(f"gate-family-unowned:{gate_id}")
        elif gate_id not in catalogues.get(owner["family"], {}):
            problems.append(f"gate-registered-not-in-plan:{gate_id}")
    return problems


def _compare_one(gate_id: str, entry: dict, declared: dict) -> list[str]:
    """One registered gate against the catalogue entry that declares it.

    Unchanged from the single-family form: phase equal, claim class equal **as a
    set**, ``depends_on`` equal as a set.
    """
    problems = []
    if entry["activation_phase"] != declared["activation_phase"]:
        problems.append(
            f"phase-mismatch:{gate_id} registry={entry['activation_phase']} "
            f"plan={declared['activation_phase']}"
        )
    if set(entry["claim_class"].split("+")) != set(declared["claim_class"].split("+")):
        problems.append(
            f"class-mismatch:{gate_id} registry={entry['claim_class']} "
            f"plan={declared['claim_class']}"
        )
    if set(entry["depends_on"]) != set(declared["depends_on"]):
        problems.append(
            f"depends-mismatch:{gate_id} registry={sorted(entry['depends_on'])} "
            f"plan={declared['depends_on']}"
        )
    return problems


def compare_claim_classes(gates: list[dict], reported: dict[str, list[str]]) -> list[str]:
    """(d): declared claim class against the mechanisms an implementation reported,
    **as sets** — evidence order is recorded but never compared."""
    problems = []
    registered = {g["id"]: g for g in gates}
    for gate_id, mechanisms in reported.items():
        entry = registered.get(gate_id)
        if entry is None:
            continue
        declared = set(entry["claim_class"].split("+"))
        if declared != set(mechanisms):
            problems.append(
                f"claim-class-drift:{gate_id} declared={'+'.join(sorted(declared))} "
                f"reported={'+'.join(sorted(mechanisms)) or '-'}"
            )
    return problems


def load_registry_module(path: Path):
    spec = importlib.util.spec_from_file_location(f"fr_registry_{path.stem}_{id(path)}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def family_catalogues(ev: Evidence) -> tuple[list[dict], dict[str, dict[str, dict]]]:
    """Every declared family, and the gate catalogue its own plan states.

    Each family's plan is a **named** file opened under an excluded root (rule 7),
    resolved through the family manifest rather than through a folder name written
    into this module.
    """
    families = common.load_gate_families()
    catalogues: dict[str, dict[str, dict]] = {}
    for family in families:
        plan_path = common.family_plan_path(family)
        section = plan_section(ev.text_of(plan_path), family["catalogue_section"])
        catalogues[family["family"]] = parse_gate_catalogue(section)
        ev.resolve(
            f"the {family['family']} family's gate ids",
            f"{rel(plan_path)} section {family['catalogue_section']}",
            "tests/gates/registry.py",
        )
    return families, catalogues


def check_registry(ev: Evidence):
    families, catalogues = family_catalogues(ev)
    registry = ev.import_gate_module("registry")
    gates = registry.GATES
    phase = common.RUN_STATE.get("phase")
    phase = int(os.environ.get("FR_PHASE", 0)) if phase is None else phase

    problems = compare_registry(catalogues, families, gates)

    implemented = 0
    implemented_by_family: dict[str, int] = {f["family"]: 0 for f in families}
    for gate in gates:
        if gate["activation_phase"] > phase:
            continue
        module_name, func_name = gate["impl"].split(":")
        try:
            module = common.load_gate_module(module_name)
        except GateFailure:
            problems.append(f"gate-not-implemented:{gate['id']} ({gate['impl']})")
            continue
        if getattr(module, func_name, None) is None:
            problems.append(f"gate-not-implemented:{gate['id']} ({gate['impl']})")
        else:
            implemented += 1
            owner = common.family_of_gate_id(gate["id"], families)
            if owner is not None:
                implemented_by_family[owner["family"]] += 1

    problems += compare_claim_classes(gates, common.RUN_STATE.get("mechanisms", {}))

    declared_count = sum(len(c) for c in catalogues.values())
    breakdown = ", ".join(
        f"{f['family']} {len(catalogues.get(f['family'], {}))} declared/"
        f"{implemented_by_family[f['family']]} implemented"
        for f in families
    )
    line = (
        f"FR-P0-REGISTRY {'PASS' if not problems else 'FAIL'} "
        f"({declared_count} declared, {implemented} implemented, "
        f"{declared_count - implemented} pending, "
        f"{sum(1 for p in problems if p.startswith('claim-class-drift'))} class drift; "
        f"families: {breakdown})"
    )

    missing_fixture = FIXTURES / "registry_missing_gate.reject.py"
    drift_fixture = FIXTURES / "registry_class_drift.reject.py"
    unowned_fixture = FIXTURES / "registry_unowned_family.reject.py"
    fixtures = [
        Fixture(
            name=rel(missing_fixture),
            kind="reject",
            expected_error="gate-declared-in-plan-not-registered",
            detector=lambda: (
                compare_registry(
                    catalogues, families, load_registry_module(missing_fixture).GATES
                )
                or [None]
            )[0],
        ),
        Fixture(
            name=rel(unowned_fixture),
            kind="reject",
            expected_error="gate-family-unowned",
            detector=lambda: (
                compare_registry(
                    catalogues, families, load_registry_module(unowned_fixture).GATES
                )
                or [None]
            )[0],
        ),
        Fixture(
            name=rel(drift_fixture),
            kind="reject",
            expected_error="claim-class-drift",
            detector=lambda: (
                compare_claim_classes(
                    load_registry_module(drift_fixture).GATES,
                    load_registry_module(drift_fixture).REPORTED_MECHANISMS,
                )
                or [None]
            )[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------

CHECKS = {
    "registry": check_registry,
    "tree": check_tree,
    "stale": check_stale,
    "planref": check_planref,
    "parse": check_parse,
    "schema": check_schema,
    "history": check_history,
    "deps": check_deps,
    "clean": check_clean,
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
