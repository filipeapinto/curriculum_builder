"""Shared harness machinery: paths, scan roots, evidence recording, fixtures.

Three things live here because getting any of them slightly different per gate is
how the defects this suite exists to catch got in.

**Scan roots (harness rule 7).** ``production_files`` is the one production scan
root set, stated by exclusion. It never yields anything under ``tests/`` or
``plans/``. Excluding a root forbids *globbing or grepping* it; opening a **named**
file under it — the registry, a named section of the active plan — is not a scan
and is done directly with :func:`read_named`.

**Mechanisms (harness rule 6).** A gate never declares what it did; it *does*
things through :class:`Evidence`, which records the mechanism each operation maps
to under the plan's normative operation-to-mechanism table. ``FR-P0-REGISTRY`` (d)
compares that recording against the class declared in the registry, as sets.

**Fixtures (harness rule 3).** A ``.reject.`` fixture must fail for its declared
``expected_error``; failing for another reason is a gate failure, not a pass. A
``.accept.`` fixture must pass.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO_ROOT / "tests"
GATES_DIR = TESTS_DIR / "gates"
FIXTURES_DIR = TESTS_DIR / "fixtures"
SELFTEST_DIR = TESTS_DIR / "selftest"
RESULTS_DIR = Path(os.environ.get("FR_RESULTS_DIR", str(TESTS_DIR / "results")))

PLAN_DIR = REPO_ROOT / "plans" / "folder_refactoring"

# Gate-family ownership is declared data, not a constant in a gate — see the manifest
# for why. ``FOLDER_FAMILY`` is named here only so the folder family's resolution can
# be shown to be unchanged; every other consumer asks the manifest.
GATE_FAMILIES_MANIFEST = GATES_DIR / "gate_families.v1.yaml"
FOLDER_FAMILY = "folder_refactoring"

# Rule 7 — the production scan root set, stated by exclusion and never
# re-enumerated. A second hand-maintained copy is the defect this plan keeps
# closing, so this is exactly rule 7's list and nothing else: adding a root here
# would narrow a normative scan set without declaring it, which is how a detector
# stops seeing the file it exists to check.
PRODUCTION_EXCLUDED_TOP_LEVEL = frozenset({"tests", "plans", ".git"})
PRODUCTION_EXCLUDED_ANYWHERE = frozenset({".git"})

# Not roots — file kinds a text scan cannot read. Bytecode caches are build output
# of this harness, never repository content.
BINARY_SUFFIXES = frozenset(
    {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".pyc", ".pyo"}
)

MECHANISM_ORDER = ("tree", "parse", "schema", "text", "mapping", "declaration", "execution")

# Populated by the runner as each gate finishes, so FR-P0-REGISTRY (d) can compare
# a declared claim class against the mechanisms an implementation actually reported.
RUN_STATE: dict = {"phase": None, "mechanisms": {}}


# ---------------------------------------------------------------------------
# Scan roots


def production_files(suffixes: Optional[Iterable[str]] = None) -> list[Path]:
    """Every text file in the production scan root set, rule 7's exclusions applied.

    Enumerating a directory solely to select the files to scan is not ``tree``
    (rule 6, subsumption rule 2), so this function records no mechanism.
    """
    wanted = frozenset(suffixes) if suffixes else None
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        rel_dir = Path(dirpath).relative_to(REPO_ROOT)
        parts = rel_dir.parts
        dirnames[:] = [
            d
            for d in dirnames
            if d not in PRODUCTION_EXCLUDED_ANYWHERE
            and not (not parts and d in PRODUCTION_EXCLUDED_TOP_LEVEL)
        ]
        if parts and parts[0] in PRODUCTION_EXCLUDED_TOP_LEVEL:
            continue
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path.suffix.lower() in BINARY_SUFFIXES:
                continue
            if wanted is not None and path.suffix.lower() not in wanted:
                continue
            found.append(path)
    return sorted(found)


def rel(path: Path | str) -> str:
    """Repository-relative POSIX path, for printing and for path literals."""
    return Path(path).resolve().relative_to(REPO_ROOT).as_posix()


def read_named(path: Path | str) -> str:
    """Open one **named** file, including under an excluded root (rule 7)."""
    return Path(path).read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Evidence — what a gate actually did


class GateFailure(Exception):
    """Raised by a gate implementation to fail with a stated reason."""


@dataclass
class Evidence:
    """Records the mechanism behind every operation a gate performs.

    Subsumption (rule 6) is applied in :meth:`mechanisms`: ``declaration``
    subsumes the ``text`` and ``schema`` legs it is built from, and a mechanism
    used only to reach another mechanism's input is never recorded in the first
    place — the helpers below choose what to record, the gate does not.
    """

    gate_id: str
    _order: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    # -- recording ----------------------------------------------------------
    def _record(self, mechanism: str) -> None:
        if mechanism not in MECHANISM_ORDER:
            raise ValueError(f"{mechanism!r} is not a mechanism in rule 6's table")
        if mechanism not in self._order:
            self._order.append(mechanism)

    def mechanisms(self) -> list[str]:
        found = list(self._order)
        if "declaration" in found:
            found = [m for m in found if m not in ("text", "schema")]
        return found

    def claim(self) -> str:
        return "+".join(self.mechanisms())

    def note(self, line: str) -> None:
        self.notes.append(line)

    # -- tree ---------------------------------------------------------------
    def exists(self, path: Path | str) -> bool:
        """Assert a **named** path does or does not exist."""
        self._record("tree")
        return Path(path).exists()

    def listdir(self, path: Path | str) -> list[Path]:
        """List a **named** directory as an assertion about what is in it."""
        self._record("tree")
        target = Path(path)
        return sorted(target.iterdir()) if target.is_dir() else []

    def select(self, paths: Iterable[Path]) -> list[Path]:
        """Enumeration solely to select files to parse or scan — not ``tree``."""
        return sorted(paths)

    # -- parse --------------------------------------------------------------
    def parse(self, path: Path | str):
        """Deserialize a file in order to read a value out of it."""
        self._record("parse")
        return _deserialize(Path(path))

    # -- schema -------------------------------------------------------------
    def validate(self, instance_path: Path | str, schema_path: Path | str) -> Optional[str]:
        """Validate an instance against a JSON Schema. Returns None or an error."""
        self._record("schema")
        instance = _deserialize(Path(instance_path))
        schema = _deserialize(Path(schema_path))
        return _validate_obj(instance, schema)

    def validate_obj(self, instance, schema_path: Path | str) -> Optional[str]:
        self._record("schema")
        return _validate_obj(instance, _deserialize(Path(schema_path)))

    def schema_is_valid(self, schema_path: Path | str) -> Optional[str]:
        """Assert a file is itself a usable JSON Schema."""
        self._record("schema")
        import jsonschema

        try:
            schema = _deserialize(Path(schema_path))
            jsonschema.Draft202012Validator.check_schema(schema)
        except Exception as exc:  # noqa: BLE001 - reported, not raised
            return f"{type(exc).__name__}:{exc}"
        return None

    # -- text ---------------------------------------------------------------
    def text_of(self, path: Path | str) -> str:
        """Read a file's contents in order to search it."""
        self._record("text")
        return read_named(path)

    def search(self, pattern: str, haystack: str, flags: int = 0) -> list[str]:
        self._record("text")
        return re.findall(pattern, haystack, flags)

    def glob(self, root: Path | str, pattern: str) -> list[Path]:
        """Enumerate a **named** directory where the enumeration *is* the
        assertion — which files exist there, at which version. Not a scan of their
        contents, and the one question ``plans/`` is legitimately asked (rule 7)."""
        self._record("tree")
        return sorted(Path(root).rglob(pattern))

    # -- mapping ------------------------------------------------------------
    def read_for_resolution(self, path: Path | str):
        """Deserialize a file **solely** to resolve one of its values against
        another file.

        Subsumption rule 4: a mechanism used only to reach another mechanism's
        input is not reported separately, so this is ``mapping`` and not
        ``parse``. Use :meth:`parse` instead whenever the value read out of the
        file is itself part of what the gate claims.
        """
        self._record("mapping")
        return _deserialize(Path(path))

    def subschema(self, schema_path: Path | str, *keys: str) -> dict:
        """One named ``$defs`` branch of a schema, with ``$defs`` carried along so
        internal ``$ref``s still resolve. Reported by whatever validates it."""
        schema = _deserialize(Path(schema_path))
        node = schema
        for key in keys:
            node = node[key]
        return {**node, "$defs": schema.get("$defs", {})}

    def resolve(self, what: str, found_in: str, against: str) -> None:
        """Resolve an id or path found in one file against another.

        The three operands are mandatory and recorded. A ``mapping`` claim names
        *what* was resolved, *where it was found* and *what it was resolved
        against*, so ``FR-P0-REGISTRY`` (d) compares evidence rather than two
        declarations.
        """
        self._record("mapping")
        self.notes.append(f"resolved {what} in {found_in} against {against}")

    def import_gate_module(self, module: str):
        """Read or import a module under ``tests/gates/`` to resolve an id."""
        self._record("mapping")
        return load_gate_module(module)

    # -- declaration --------------------------------------------------------
    def declaration(self, comparison: str = "python") -> None:
        """A rule is stated, a conforming record validates, a violating one does
        not, and the residual comparison is performed here."""
        self._record("declaration")
        self.notes.append(f"comparison: {comparison}")

    # -- execution ----------------------------------------------------------
    def run(self, args: list[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        self._record("execution")
        return subprocess.run(
            args,
            cwd=str(cwd or REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )

    def import_and_call(self, module: str):
        """Import a module under ``tests/gates/`` in order to call it."""
        self._record("execution")
        return load_gate_module(module)


def _deserialize(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        import yaml

        return yaml.safe_load(text)
    return json.loads(text)


def _validate_obj(instance, schema) -> Optional[str]:
    import jsonschema

    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    if not errors:
        return None
    return f"ValidationError:{errors[0].message}"


def gate_module_search_path() -> list[Path]:
    """Where gate implementations are looked up.

    ``FR_GATES_DIR`` lets ``selftest.py`` point the runner at a synthetic gate set
    in a scratch directory without touching the repository tree (rule 8).
    """
    extra = os.environ.get("FR_GATES_DIR")
    return ([Path(extra)] if extra else []) + [GATES_DIR]


def load_gate_module(module: str):
    for directory in gate_module_search_path():
        path = directory / f"{module}.py"
        if path.exists():
            break
    else:
        raise GateFailure(f"gate module {module!r} is declared but not implemented")
    spec = importlib.util.spec_from_file_location(f"fr_gates.{module}", path)
    assert spec and spec.loader
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


# ---------------------------------------------------------------------------
# Fixtures


@dataclass
class Fixture:
    """One fixture and the outcome rule 3 demands of it.

    ``detector`` returns the error a detector produced, or ``None`` for a clean
    pass. A ``reject`` fixture passes only when that error matches
    ``expected_error``; an ``accept`` fixture passes only when it is ``None``.
    """

    name: str
    kind: str  # "reject" | "accept"
    detector: Callable[[], Optional[str]]
    expected_error: str = ""
    synthesized: bool = False

    def evaluate(self) -> dict:
        try:
            actual = self.detector()
        except Exception as exc:  # noqa: BLE001 - a crashing detector is a failure
            actual = f"{type(exc).__name__}:{exc}"
        record = {
            "fixture": self.name,
            "kind": self.kind,
            "expected_error": self.expected_error,
            "matched_error": actual,
            "synthesized": self.synthesized,
        }
        if self.kind == "reject":
            if actual is None:
                record["outcome"] = "FAIL"
                record["why"] = "fixture was accepted; it must be rejected"
            elif _error_matches(self.expected_error, actual):
                record["outcome"] = "PASS"
            else:
                record["outcome"] = "FAIL"
                record["why"] = "rejected for a different reason than declared"
        else:
            if actual is None:
                record["outcome"] = "PASS"
            else:
                record["outcome"] = "FAIL"
                record["why"] = "positive fixture was rejected"
        return record


def _error_matches(expected: str, actual: str) -> bool:
    norm = lambda s: re.sub(r"\s+", " ", s).strip()
    return norm(expected) in norm(actual)


@dataclass
class GateOutcome:
    ok: bool
    detail: str
    fixtures: list[dict] = field(default_factory=list)
    stdout: str = ""


def gate_result(ok: bool, detail: str, fixtures: Optional[list[Fixture]] = None,
                stdout: str = "") -> GateOutcome:
    records = [f.evaluate() for f in (fixtures or [])]
    fixtures_ok = all(r["outcome"] == "PASS" for r in records)
    return GateOutcome(ok=ok and fixtures_ok, detail=detail, fixtures=records, stdout=stdout)


# ---------------------------------------------------------------------------
# Gate families — which plan owns which gate ids


def load_gate_families() -> list[dict]:
    """The declared gate families, validated against their own schema first.

    Validation happens here, without an :class:`Evidence`, on purpose. Every manifest
    in this repository is validated against a contract before it is trusted, and this
    one decides which plan a gate is checked against — an invalid one would not fail a
    gate, it would silently compare the registry to the wrong document. Doing it in
    the loader means the harness refuses to run rather than reporting a comparison it
    could not make, and it does not add a ``schema`` leg to the claim class of every
    gate that happens to need a plan path.
    """
    doc = _deserialize(GATE_FAMILIES_MANIFEST)
    pointer = (doc or {}).get("schema")
    if not pointer:
        raise GateFailure(
            f"gate-families-manifest-invalid: {rel(GATE_FAMILIES_MANIFEST)} names no schema"
        )
    schema_path = REPO_ROOT / pointer
    if not schema_path.exists():
        raise GateFailure(
            f"gate-families-manifest-invalid: it names {pointer}, which does not exist"
        )
    error = _validate_obj(doc, _deserialize(schema_path))
    if error:
        raise GateFailure(f"gate-families-manifest-invalid: {error}")

    families = doc["families"]
    seen: dict[str, str] = {}
    for family in families:
        for prefix in family["id_prefixes"]:
            if prefix in seen:
                raise GateFailure(
                    f"gate-families-manifest-invalid: prefix {prefix!r} is claimed by both "
                    f"{seen[prefix]!r} and {family['family']!r}"
                )
            seen[prefix] = family["family"]
    return families


def family_by_name(name: str, families: Optional[list[dict]] = None) -> dict:
    for family in families if families is not None else load_gate_families():
        if family["family"] == name:
            return family
    raise GateFailure(f"no gate family named {name!r} is declared")


def family_of_gate_id(gate_id: str, families: list[dict]) -> Optional[dict]:
    """The family owning a gate id, by longest matching prefix, or ``None``.

    ``None`` is a reportable state, never a default owner: a gate nobody's plan
    declares must fail loudly rather than be filed under whichever family sorts first.
    """
    best: Optional[tuple[int, dict]] = None
    for family in families:
        for prefix in family["id_prefixes"]:
            if gate_id.startswith(prefix) and (best is None or len(prefix) > best[0]):
                best = (len(prefix), family)
    return best[1] if best else None


# ---------------------------------------------------------------------------
# Reading a family's plan — named files under plans/, never a glob (rule 7)


def family_plan_path(family: dict) -> Path:
    """The highest-versioned plan at that family's plan folder root. Named, then
    opened. The glob is non-recursive, so a superseded plan under ``deprecated/`` is
    never resolved as the owner."""
    directory = REPO_ROOT / family["plan_dir"]
    stem = family["plan_stem"]
    versions = sorted(
        int(m.group(1))
        for m in (
            re.match(rf"{re.escape(stem)}\.v(\d+)\.md$", p.name)
            for p in directory.glob(f"{stem}.v*.md")
        )
        if m
    )
    if not versions:
        raise GateFailure(f"no {stem}.v*.md at the {family['family']} plan folder root")
    return directory / f"{stem}.v{versions[-1]}.md"


def active_plan_path() -> Path:
    """The folder family's active plan.

    Behaviour is unchanged — the highest-versioned ``folder_refactoring.plan.v*.md``
    at ``plans/folder_refactoring/`` — but the folder name and the stem are now read
    from the family manifest rather than written here, so the folder family is
    resolved by exactly the code every other family is.
    """
    return family_plan_path(family_by_name(FOLDER_FAMILY))


def plan_section(text: str, number: int) -> str:
    """The body of ``## <number>. ...`` up to the next ``## `` heading."""
    match = re.search(rf"^## {number}\. .*$", text, re.M)
    if not match:
        raise GateFailure(f"section {number} not found in the plan")
    start = match.end()
    nxt = re.search(r"^## \d+\. ", text[start:], re.M)
    return text[start : start + nxt.start()] if nxt else text[start:]
