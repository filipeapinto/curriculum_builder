"""Independent, read-only collectors for the repository-refactor inventory.

Each ``collect_*`` function inspects the repository at ``repo_root`` through
git subprocess calls, plain filesystem reads, and Python's ``ast`` module. No
function in this module writes anything, anywhere. A collector that cannot
complete truthfully raises :class:`CollectorUnavailable` naming the reason;
the orchestrator in ``inventory.py`` turns that into a recorded omission and
a nonzero exit rather than an empty, falsely-successful field
(spec v8 section 7).
"""
from __future__ import annotations

import ast
import platform
import re
import subprocess
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any, Iterable


class CollectorUnavailable(RuntimeError):
    """A collector could not complete; caller records this as an omission."""


# ---------------------------------------------------------------------------
# Scan-scope policy.
#
# Lexical/text collectors (old-identity references, module-command text
# search) must not wade through this repository's own historical QA
# transcripts (hundreds of frozen Codex session/verdict/round files under
# plans/**/QA/, plans/**/results/, deprecated/ history, and the qa-gate
# skill's own synthetic eval workspaces) — those are retained evidence of
# unrelated past work, not the live identity/reference surface spec v8 §7
# asks the inventory to enumerate. This exclusion set is applied uniformly
# and is recorded verbatim in the machine report's provenance.configuration
# so the scope decision is auditable, not a silent omission.
EXCLUDED_DIR_NAMES = {
    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules",
    "deprecated", "QA", "results", "receipt_history", "logs", "exec",
    "release_candidate", "execution_package_v2",
}
EXCLUDED_DIR_PREFIXES = ("invalidated_by_",)
EXCLUDED_DIR_SUFFIXES = ("-workspace",)

# Ephemeral tool caches that routinely appear and disappear as a side effect
# of merely running this repository's own tooling (pytest, CPython bytecode
# compilation). These are never reported as inventory items at any
# directory depth — like .git, they are not repository content, and
# treating each one as a discovered item needing its own disposition would
# make "directories"/"test_subtrees" coverage nondeterministic across runs
# for no evidentiary value. A directory this set does not name is still
# either resolved by DIRECTORY_CLASSIFICATION/TEST_SUBTREE_META or, failing
# that, auto-classified as cache_or_scratch only if git proves it holds zero
# tracked and zero plain-untracked content — never silently skipped.
ALWAYS_SKIP_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}

# This refactor's own in-flight process artifacts (journal, checkpoints,
# generated inventory reports, orchestration routing log) are excluded from
# the lexical scans for the same reason: they are expected to *discuss* the
# old identities and would otherwise self-pollute the scan with references
# to the very strings the scan exists to find in production/doc material.
EXCLUDED_RELATIVE_PREFIXES = (
    "plans_internal/refactor_repo/execution",
    "plans_internal/refactor_repo/checkpoints",
    "plans_internal/refactor_repo/inventory",
    "plans_internal/refactor_repo/baseline",
    "plans_internal/refactor_repo/orchestration",
    # The inventory tool's own source and tests necessarily *contain* the
    # search patterns it looks for (regexes, docstrings, sample fixture
    # text) as literal text. Scanning them would make the tool find itself
    # rather than genuine repository evidence, so both are excluded from
    # every lexical/python-surface scan corpus.
    "tools/refactor_repo",
    "tests/refactor_repo",
)

TEXT_EXTENSIONS = {
    ".py", ".md", ".yml", ".yaml", ".toml", ".json", ".sh", ".html", ".cfg", ".ini", ".txt",
}


def _prune_dirs(dirnames: list[str]) -> None:
    keep = []
    for name in dirnames:
        if name in EXCLUDED_DIR_NAMES:
            continue
        if any(name.startswith(p) for p in EXCLUDED_DIR_PREFIXES):
            continue
        if any(name.endswith(s) for s in EXCLUDED_DIR_SUFFIXES):
            continue
        keep.append(name)
    dirnames[:] = keep


def iter_scan_files(repo_root: Path, extensions: set[str] = TEXT_EXTENSIONS) -> Iterable[Path]:
    """Yield live text files under ``repo_root``, applying the scan-scope policy above."""
    for dirpath, dirnames, filenames in _walk(repo_root):
        rel_dir = Path(dirpath).relative_to(repo_root).as_posix()
        if rel_dir != "." and any(
            rel_dir == p or rel_dir.startswith(p + "/") for p in EXCLUDED_RELATIVE_PREFIXES
        ):
            dirnames[:] = []
            continue
        _prune_dirs(dirnames)
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix in extensions:
                yield path


def _walk(repo_root: Path):
    import os

    for dirpath, dirnames, filenames in os.walk(repo_root):
        yield dirpath, dirnames, filenames


def _run_git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo_root, capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise CollectorUnavailable(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def rel(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


# ---------------------------------------------------------------------------
# provenance


def collect_git_provenance(repo_root: Path) -> dict[str, Any]:
    commit = _run_git(repo_root, "rev-parse", "HEAD").strip()
    status_out = _run_git(repo_root, "status", "--porcelain=v1", "-uall")
    changed_paths = [line[3:] for line in status_out.splitlines() if line.strip()]
    git_version = _run_git(repo_root, "--version").strip()
    return {
        "repository_commit": commit,
        "dirty_state": {"is_dirty": bool(changed_paths), "changed_paths": changed_paths},
        "tool_versions": {"python": platform.python_version(), "git": git_version},
    }


def collect_git_remote(repo_root: Path) -> str | None:
    try:
        out = _run_git(repo_root, "remote", "get-url", "origin").strip()
    except CollectorUnavailable:
        return None
    return out or None


# ---------------------------------------------------------------------------
# identities (spec v8 section 2)


def collect_identities(repo_root: Path, scan_files: list[Path]) -> list[dict[str, Any]]:
    remote = collect_git_remote(repo_root)
    readme = repo_root / "readme.md"
    readme_heading = None
    if readme.exists():
        first_line = readme.read_text(encoding="utf-8", errors="replace").splitlines()[0]
        readme_heading = first_line.lstrip("# ").strip()

    product_hits = _count_pattern(scan_files, re.compile(r"\bCurriculum Builder\b"))
    slug_hits = _count_pattern(scan_files, re.compile(r"\bcurriculum_builder\b"))
    package_hits = _count_pattern(
        scan_files,
        re.compile(r"\bruntime\.[A-Za-z_][\w.]*|(?<![\w./-])runtime/[\w./-]*\.py\b|-m runtime\b"),
    )

    identities = [
        {
            "identity": "Product name",
            "current_values": ["Curriculum Builder"] if product_hits else [],
            "target_value": "Curriculum Factory",
            "used_for": "Prose, headings, reports, and UI text (spec v8 section 2). "
            f"{product_hits} live occurrence(s) of the old prose name found in scope.",
        },
        {
            "identity": "Repository slug",
            "current_values": sorted({v for v in [readme_heading, _basename_of_remote(remote)] if v}),
            "target_value": "curriculum_factory",
            "used_for": "Git repository and checkout directory (spec v8 section 2). "
            f"Evidence: readme.md H1 heading and git remote 'origin' URL "
            f"({remote or 'not configured'}); {slug_hits} additional live textual occurrence(s).",
        },
        {
            "identity": "Python distribution",
            "current_values": [],
            "target_value": "curriculum-factory",
            "used_for": "Packaging metadata and installation (spec v8 section 2). No "
            "pyproject.toml, setup.py, or setup.cfg exists in this checkout, so no "
            "distribution name is currently declared; packaging is P01's scope.",
        },
        {
            "identity": "Python package",
            "current_values": ["runtime"],
            "target_value": "curriculum_factory",
            "used_for": "Imports and module execution (spec v8 section 2). "
            f"{package_hits} live occurrence(s) of qualified 'runtime.' imports, "
            "'runtime/*.py' paths, or '-m runtime' commands found in scope.",
        },
        {
            "identity": "Source root",
            "current_values": ["runtime/"],
            "target_value": "src/curriculum_factory/",
            "used_for": "Production Python code location (spec v8 section 2). The current "
            "production package sits at the repository root, not under a src/ layout.",
        },
    ]
    return identities


def _basename_of_remote(remote: str | None) -> str | None:
    if not remote:
        return None
    name = remote.rstrip("/").rsplit("/", 1)[-1]
    return name[:-4] if name.endswith(".git") else name


def _count_pattern(files: list[Path], pattern: re.Pattern) -> int:
    total = 0
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        total += len(pattern.findall(text))
    return total


# ---------------------------------------------------------------------------
# directories

DIRECTORY_CLASSIFICATION: dict[str, dict[str, Any]] = {
    ".claude": dict(
        owner_or_reader="Claude Code automation authors; consumed by the claude CLI/plugin "
        "runtime that reads .claude/skills, .claude/agents (if any), and plugin config.",
        lifecycle_class="repository_contract",
        proposed_disposition="Retain at repository root; out of the src/ production-code "
        "migration in spec v8 section 4, which only moves the Python production package.",
        evidence=[".claude/skills/qa-gate-codex-run/SKILL.md is the mandatory QA transport "
                  "for every refactor checkpoint (this prompt's test 6)."],
    ),
    ".github": dict(
        owner_or_reader="GitHub Actions; consumed by CI runners.",
        lifecycle_class="repository_contract",
        proposed_disposition="Retain; .github/workflows/plan26-lock-drift.yml is a named "
        "direct CI reference spec v8 section 4 requires updating if tests/ moves.",
        evidence=[".github/workflows/plan26-lock-drift.yml references requirements/plan26.lock "
                  "and tests/runtime/test_plan26_api_contract.py, tests/runtime/test_plan26_lock_drift.py."],
    ),
    "curricula": dict(
        owner_or_reader="runtime/capability_cycle.py, runtime/checks.py, runtime/readability.py "
        "read curriculum-owned domain files under here.",
        lifecycle_class="domain_input",
        proposed_disposition="Retain outside src/ (spec v8 section 4 explicitly keeps curricula/ "
        "outside src/); no P00 action.",
        evidence=["grep hits: runtime/capability_cycle.py, runtime/readability.py, runtime/checks.py "
                  "reference curricula/ paths."],
    ),
    "docs": dict(
        owner_or_reader="Human readers; runtime/capability_cycle.py and "
        "tests/gates/fr_p5_engine.py reference paths under docs/.",
        lifecycle_class="active_documentation",
        proposed_disposition="Retain outside src/ (spec v8 section 4); no P00 action.",
        evidence=["readme.md: 'See docs/how_it_works.md ... for the current architecture.'",
                  "grep hits: runtime/capability_cycle.py, tests/gates/fr_p5_engine.py."],
    ),
    "governance": dict(
        owner_or_reader="Human governance readers; no live runtime/*.py or tests/*.py reference found.",
        lifecycle_class="active_documentation",
        proposed_disposition="Retain; governance/governance.v3.html is the live document, "
        "governance/deprecated/ already holds superseded versions.",
        evidence=["governance/governance.v3.html present; governance/deprecated/governance.v1.html, "
                  "governance/deprecated/governance.v2.html hold prior versions."],
    ),
    "issues": dict(
        owner_or_reader="Human maintainers tracking open defects; no live runtime/*.py or "
        "tests/*.py reference found.",
        lifecycle_class="active_documentation",
        proposed_disposition="Retain; issues/001..007 plus issues/README.md are the open defect register.",
        evidence=["issues/README.md and issues/001-*.md .. issues/007-*.md present."],
    ),
    "meta_prompt": dict(
        owner_or_reader="runtime/controller.py, runtime/langgraph_factory/workbook.py, "
        "runtime/session_bridge.py read the active contract here.",
        lifecycle_class="repository_contract",
        proposed_disposition="Retain outside src/ (spec v8 section 4); no P00 action.",
        evidence=["readme.md: 'The active contract is meta_prompt/curriculum.prompt.v1.md.'",
                  "grep hits: runtime/controller.py, runtime/langgraph_factory/workbook.py, "
                  "runtime/session_bridge.py."],
    ),
    "plans": dict(
        owner_or_reader="Human plan authors and the qa-gate-codex-run skill; "
        "tests/gates/registry.py, tests/gates/fr_p0_structure.py, "
        "runtime/curriculum_factory_graph.py reference plans/ paths.",
        lifecycle_class="active_documentation",
        proposed_disposition="Retain; large tracked tree (1947 tracked paths at collection time) "
        "including nested frozen QA/results evidence from prior, unrelated remediation plans; "
        "out of scope for this refactor's identity/source moves.",
        evidence=["grep hits: tests/gates/registry.py, runtime/curriculum_factory_graph.py, "
                  "tests/gates/fr_p0_structure.py."],
    ),
    "plans_internal": dict(
        owner_or_reader="This refactor's own orchestrator and prompts (RUN_repository_refactor, "
        "P00..P10); no external runtime/*.py or tests/*.py reference found.",
        lifecycle_class="active_documentation",
        proposed_disposition="Retain; hosts this prompt, its schemas/checkpoints/execution log, "
        "and the QA gate session directories the qa-gate-codex-run skill writes.",
        evidence=["plans_internal/refactor_repo/prompts/P00_inventory_baseline.prompt.v3.yaml "
                  "is the executing prompt for this inventory."],
    ),
    "policy": dict(
        owner_or_reader="runtime/controller.py, runtime/checks.py, runtime/routing.py read "
        "policy/*.yaml, validated against schemas/*.schema.v1.json.",
        lifecycle_class="repository_contract",
        proposed_disposition="Retain outside src/ (spec v8 section 4 explicitly keeps policy/ "
        "outside src/); no P00 action.",
        evidence=["grep hits: runtime/controller.py, runtime/checks.py, runtime/routing.py."],
    ),
    "requirements": dict(
        owner_or_reader="tests/runtime/test_plan26_lock_drift.py, test_plan26_unit_graph.py, "
        "test_plan26_repair_acceptance.py, and .github/workflows/plan26-lock-drift.yml.",
        lifecycle_class="repository_contract",
        proposed_disposition="Retain; pinned dependency declaration (plan26.in) and hash-locked "
        "resolution (plan26.lock) consumed directly by name in CI.",
        evidence=["grep hits: tests/runtime/test_plan26_lock_drift.py, "
                  "tests/runtime/test_plan26_unit_graph.py, "
                  "tests/runtime/test_plan26_repair_acceptance.py; "
                  ".github/workflows/plan26-lock-drift.yml names requirements/plan26.lock verbatim."],
    ),
    "research": dict(
        owner_or_reader="Human research readers; runtime/model_worker.py references research/ paths.",
        lifecycle_class="retained_evidence",
        proposed_disposition="Retain; SOTA/state-of-the-art scan evidence, including this "
        "refactor's own research/repository_refactoring/repository_refactoring.sota.v1.md.",
        evidence=["grep hit: runtime/model_worker.py."],
    ),
    "runtime": dict(
        owner_or_reader="Legacy production Python package before the source-layout migration.",
        lifecycle_class="production_source",
        proposed_disposition="Move beneath src/curriculum_factory/; absent after the source move.",
        evidence=["spec v8 section 4 defines src/curriculum_factory/ as the target tree."],
    ),
    "src": dict(
        owner_or_reader="Python packaging tools and every consumer of the installed curriculum_factory package.",
        lifecycle_class="production_source",
        proposed_disposition="Retain as the sole production Python source root.",
        evidence=["pyproject.toml limits package discovery to src/; production modules reside in src/curriculum_factory/."],
    ),
    "schemas": dict(
        owner_or_reader="runtime/run_state.py, runtime/lesson_render.py, runtime/controller.py, "
        "schemas/validate_instance.py.",
        lifecycle_class="repository_contract",
        proposed_disposition="Retain outside src/ (spec v8 section 4); $id values under the "
        "https://example.invalid/curriculum_builder/ namespace are versioned contract "
        "identifiers per spec v8 section 3, not branding text — do not rewrite in place.",
        evidence=["grep hits: runtime/run_state.py, runtime/lesson_render.py, runtime/controller.py."],
    ),
    "tools": dict(
        owner_or_reader="Refactor authors and the qa-gate-codex-run skill; created by this "
        "P00 prompt itself (tools/refactor_repo/inventory.py, collectors.py, baseline.py).",
        lifecycle_class="repository_contract",
        proposed_disposition="Retain as refactor-support tooling outside src/curriculum_factory/; "
        "it is meta-tooling for this refactor, not shipped product source. Re-evaluate at the "
        "clean-room release phase whether it stays repo-only dev tooling or is retired once the "
        "refactor completes.",
        evidence=["Created under this prompt's authorized_paths entry 'tools/refactor_repo/' "
                  "(plans_internal/refactor_repo/prompts/P00_inventory_baseline.prompt.v3.yaml)."],
    ),
    "tests": dict(
        owner_or_reader="pytest and tests/run_gates.sh; see test_subtrees for the granular "
        "per-subdirectory package/import status, scope, cost, environment, CI lane, "
        "and direct references spec v8 section 7 asks for.",
        lifecycle_class="test_fixture",
        proposed_disposition="Coarse top-level classification only; the enum in "
        "schemas/repository_refactor_inventory.schema.v1.json has no distinct 'test code' "
        "category, so the whole tree maps to test_fixture here while test_subtrees carries "
        "the real per-subdirectory decision spec v8 section 4's 'Test-tree decision' requires.",
        evidence=["tests/run_gates.sh; tests/__init__.py; 131 tracked paths at collection time."],
    ),
    "failed_execution_evidence": dict(
        owner_or_reader="Retained evidence of prior failed refactor execution attempts; "
        "contains P00 and RUN execution logs from earlier checkpoint runs that did not complete.",
        lifecycle_class="retained_evidence",
        proposed_disposition="Retain as audit trail; these files document prior execution attempts "
        "and are useful for post-mortem analysis. No live code or production functionality depends on them. "
        "May be archived or purged after successful P00 completion and sign-off.",
        evidence=["failed_execution_evidence/P00_failed_evidence/execution_log.jsonl; "
                  "failed_execution_evidence/RUN_failed_evidence/execution_log.jsonl — execution journals "
                  "from earlier attempts."],
    ),
}


def collect_directories(repo_root: Path) -> list[dict[str, Any]]:
    entries = []
    for child in sorted(repo_root.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            continue
        name = child.name
        if name == ".git" or name in ALWAYS_SKIP_DIR_NAMES:
            # VCS-internal (.git), or an ephemeral tool cache never treated
            # as repository content; see ALWAYS_SKIP_DIR_NAMES.
            continue
        tracked_state = _tracked_state(repo_root, name)
        if name not in DIRECTORY_CLASSIFICATION:
            # A directory the fixed classification table has no entry for is
            # only auto-resolved when git proves it holds zero tracked and
            # zero plain-untracked content — i.e. it is entirely a
            # gitignored tool cache (e.g. a fresh .pytest_cache/ created by
            # merely running this repo's own test suite), never repository
            # content a human has not classified. Anything else stops the
            # run, per spec v8 section 7: "Do not rename or delete an
            # unresolved directory."
            if tracked_state != "ignored":
                raise CollectorUnavailable(
                    f"unresolved top-level directory: {name!r} has no lifecycle classification "
                    f"and is not a fully gitignored cache (tracked_state={tracked_state!r}); "
                    "spec v8 section 7 requires stopping rather than guessing."
                )
            entries.append({
                "path": f"{name}/",
                "owner_or_reader": "unattributed tool cache; entirely gitignored, no tracked content",
                "tracked_state": tracked_state,
                "lifecycle_class": "cache_or_scratch",
                "proposed_disposition": "auto-classified: fully gitignored ephemeral cache directory "
                "discovered at collection time (e.g. a test runner's own cache); safe to delete, "
                "regenerated on demand, carries no repository identity.",
                "evidence": [f"git status --porcelain=v1 --ignored=matching -uall -- {name} shows only "
                             "'!!' (ignored) entries and zero tracked or plain-untracked ('??') entries."],
            })
            continue
        meta = DIRECTORY_CLASSIFICATION[name]
        entries.append({
            "path": f"{name}/",
            "owner_or_reader": meta["owner_or_reader"],
            "tracked_state": tracked_state,
            "lifecycle_class": meta["lifecycle_class"],
            "proposed_disposition": meta["proposed_disposition"],
            "evidence": meta["evidence"],
        })
    return entries


def _tracked_state(repo_root: Path, dirname: str) -> str:
    tracked_out = _run_git(repo_root, "ls-files", "--", dirname)
    tracked = bool(tracked_out.strip())
    status_out = _run_git(repo_root, "status", "--porcelain=v1", "--ignored=matching", "-uall", "--", dirname)
    lines = [l for l in status_out.splitlines() if l.strip()]
    has_ignored = any(l.startswith("!!") for l in lines)
    has_untracked = any(l.startswith("??") for l in lines)
    if tracked and not (has_ignored or has_untracked):
        return "tracked"
    if not tracked and has_ignored and not has_untracked:
        return "ignored"
    if not tracked and has_untracked:
        return "untracked"
    if tracked and (has_ignored or has_untracked):
        return "mixed"
    return "tracked"


# ---------------------------------------------------------------------------
# python_surface


def collect_python_surface(repo_root: Path, py_files: list[Path], scan_files: list[Path]) -> dict[str, Any]:
    runtime_imports: list[dict[str, Any]] = []
    file_based_root_traversals: list[dict[str, Any]] = []
    absolute_checkout_paths: list[dict[str, Any]] = []
    entry_points: list[dict[str, Any]] = []

    file_traversal_re = re.compile(r".*__file__.*")
    abs_path_re = re.compile(r"['\"](/Users/[^'\"]+|/home/[^'\"]+|[A-Za-z]:\\\\[^'\"]+)['\"]")

    for path in py_files:
        source_file = rel(repo_root, path)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if "__file__" in line:
                file_based_root_traversals.append({
                    "source_file": source_file, "line": lineno, "expression": line.strip(),
                })
            for match in abs_path_re.finditer(line):
                absolute_checkout_paths.append({
                    "source_file": source_file, "line": lineno, "text": match.group(0),
                })

        try:
            tree = ast.parse(text, filename=source_file)
        except SyntaxError as exc:
            raise CollectorUnavailable(f"python_surface: {source_file} does not parse: {exc}") from exc

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "runtime" or alias.name.startswith("runtime."):
                        runtime_imports.append({
                            "source_file": source_file, "line": node.lineno,
                            "statement": ast.get_source_segment(text, node) or f"import {alias.name}",
                        })
            elif isinstance(node, ast.ImportFrom):
                if node.module and (node.module == "runtime" or node.module.startswith("runtime.")):
                    runtime_imports.append({
                        "source_file": source_file, "line": node.lineno,
                        "statement": ast.get_source_segment(text, node)
                        or f"from {node.module} import ...",
                    })

        if source_file.startswith("runtime/"):
            has_main_guard = any(
                isinstance(node, ast.If)
                and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"
                for node in ast.walk(tree)
            )
            if has_main_guard:
                module_dotted = source_file[len("runtime/"):-len(".py")].replace("/", ".")
                entry_points.append({
                    "source_file": source_file, "kind": "module_main_guard",
                    "target": f"python3 -m runtime.{module_dotted}",
                })

    runtime_module_commands: list[dict[str, Any]] = []
    cmd_re = re.compile(r"python3?\s+-m\s+runtime(?:\.[A-Za-z0-9_.]+)?")
    for path in scan_files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for match in cmd_re.finditer(line):
                runtime_module_commands.append({
                    "source_file": rel(repo_root, path), "line": lineno, "command": match.group(0),
                })

    return {
        "runtime_imports": runtime_imports,
        "runtime_module_commands": runtime_module_commands,
        "entry_points": entry_points,
        "file_based_root_traversals": file_based_root_traversals,
        "absolute_checkout_paths": absolute_checkout_paths,
    }


# ---------------------------------------------------------------------------
# old_identity_references


def collect_old_identity_references(repo_root: Path, scan_files: list[Path]) -> list[dict[str, Any]]:
    patterns = [
        ("Product name", re.compile(r"\bCurriculum Builder\b")),
        ("Repository slug", re.compile(r"\bcurriculum_builder\b")),
        ("Python package", re.compile(r"\bruntime\.[A-Za-z_][\w.]*|-m runtime\b")),
        ("Source root", re.compile(r"(?<![\w./-])runtime/[\w./-]*\.py\b")),
    ]
    references: list[dict[str, Any]] = []
    for path in scan_files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        source_file = rel(repo_root, path)
        for lineno, line in enumerate(text.splitlines(), 1):
            for identity, pattern in patterns:
                for match in pattern.finditer(line):
                    references.append({
                        "identity": identity, "source_file": source_file, "line": lineno,
                        "text": match.group(0),
                    })
    return references


# ---------------------------------------------------------------------------
# structured_configuration


STRUCTURED_CONFIG_CANDIDATES: list[tuple[str, str, str]] = [
    ("pyproject.toml", "toml", "Build backend, distribution metadata, package discovery (spec v8 section 4)."),
    ("setup.py", "cfg", "Legacy setuptools entry point."),
    ("setup.cfg", "cfg", "Legacy setuptools configuration."),
    ("MANIFEST.in", "cfg", "sdist inclusion rules."),
    ("tox.ini", "ini", "Multi-environment test runner configuration."),
    ("pytest.ini", "ini", "pytest discovery/configuration."),
    ("conftest.py", "cfg", "pytest fixtures/collection hooks (not present at repo root)."),
    (".pre-commit-config.yaml", "yaml", "Pre-commit hook configuration."),
    ("requirements/plan26.in", "cfg", "Declared (unpinned) Plan 26 dependency set."),
    ("requirements/plan26.lock", "cfg", "Hash-pinned resolved dependency set, verified in CI."),
    (".github/workflows/plan26-lock-drift.yml", "yaml", "CI: regenerates and diffs the dependency lock."),
]


def collect_structured_configuration(repo_root: Path) -> list[dict[str, Any]]:
    entries = []
    for relative, fmt, role in STRUCTURED_CONFIG_CANDIDATES:
        path = repo_root / relative
        present = path.exists()
        entries.append({
            "path": relative,
            "format": fmt if present else "absent",
            "role": role,
            "present": present,
        })
    return entries


# ---------------------------------------------------------------------------
# outputs_children


def collect_outputs_children(repo_root: Path) -> list[dict[str, Any]]:
    outputs_dir = repo_root / "outputs"
    if not outputs_dir.exists():
        return []
    entries = []
    for child in sorted(outputs_dir.iterdir(), key=lambda p: p.name):
        size = _dir_size(child) if child.is_dir() else child.stat().st_size
        entries.append({
            "path": f"outputs/{child.name}",
            "size_bytes": size,
            "producer": "unknown; requires manual attribution",
            "tracked_consumers": [],
            "untracked_consumers": [],
            "reproducible": "unknown",
            "evidence_value": "not yet assessed",
            "proposed_disposition": "assess in the fixture-migration phase (spec v8 section 6)",
        })
    return entries


def _dir_size(path: Path) -> int:
    total = 0
    for child in path.rglob("*"):
        if child.is_file():
            total += child.stat().st_size
    return total


# ---------------------------------------------------------------------------
# test_subtrees

TEST_SUBTREE_META: dict[str, dict[str, Any]] = {
    "gates": dict(
        scope="Repository quality-gate harness (FR-P* families: structure, retention, "
        "selector, calibration, policy schemas, engine, manifest, unit, verifier) run via "
        "tests/run_gates.sh, not pytest-collected directly.",
        environment_needs=["python3", "PyYAML", "jsonschema"],
    ),
    "runtime": dict(
        scope="pytest unit/contract/adversarial tests for the runtime/ package, including "
        "the Plan 26/27 LangGraph curriculum factory test modules.",
        environment_needs=["python3", "pytest", "PyYAML", "jsonschema"],
    ),
    "selftest": dict(
        scope="Currently empty except a tracked .gitkeep placeholder.",
        environment_needs=[],
    ),
    "fixtures": dict(
        scope="Shared accept/reject data fixtures consumed by tests/gates and tests/runtime.",
        environment_needs=[],
    ),
    "results": dict(
        scope="Generated per-run gate-result JSON (gitignored beyond a tracked .gitkeep); "
        "not durable evidence.",
        environment_needs=["python3"],
    ),
    "refactor_repo": dict(
        scope="pytest suite for tools/refactor_repo/ (this P00 inventory tool itself), "
        "created by this prompt.",
        environment_needs=["python3", "pytest", "jsonschema"],
    ),
}


def collect_test_subtrees(repo_root: Path, scan_files: list[Path]) -> list[dict[str, Any]]:
    tests_dir = repo_root / "tests"
    ci_text = ""
    ci_path = repo_root / ".github/workflows/plan26-lock-drift.yml"
    if ci_path.exists():
        ci_text = ci_path.read_text(encoding="utf-8", errors="replace")

    entries = []
    for child in sorted(tests_dir.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            continue
        name = child.name
        if name in ALWAYS_SKIP_DIR_NAMES:
            continue
        if name not in TEST_SUBTREE_META:
            tracked_state = _tracked_state(repo_root, f"tests/{name}")
            if tracked_state != "ignored":
                raise CollectorUnavailable(
                    f"unresolved tests/ subtree: {name!r} has no recorded scope/classification "
                    f"and is not a fully gitignored cache (tracked_state={tracked_state!r})."
                )
            entries.append({
                "path": f"tests/{name}/",
                "package_import_status": "no __init__.py",
                "scope": "auto-classified: fully gitignored ephemeral cache directory discovered "
                "at collection time; not a real test subtree.",
                "execution_cost": "n/a",
                "environment_needs": [],
                "ci_lane": [],
                "direct_references": [],
            })
            continue
        meta = TEST_SUBTREE_META[name]
        has_init = (child / "__init__.py").exists()
        py_count = sum(1 for _ in child.rglob("*.py"))
        ci_lane = [f"tests/{name}"] if f"tests/{name}" in ci_text else []
        direct_references = sorted({
            rel(repo_root, f) for f in scan_files
            if f"tests/{name}" in f.read_text(encoding="utf-8", errors="replace")
            and rel(repo_root, f) != f"tests/{name}"
        })[:50]
        entries.append({
            "path": f"tests/{name}/",
            "package_import_status": "importable (__init__.py present)" if has_init else "no __init__.py",
            "scope": meta["scope"],
            "execution_cost": f"unmeasured; {py_count} Python file(s) present at collection time",
            "environment_needs": meta["environment_needs"],
            "ci_lane": ci_lane,
            "direct_references": direct_references,
        })
    return entries


# ---------------------------------------------------------------------------
# schema_identifiers


def collect_schema_identifiers(repo_root: Path, scan_files: list[Path]) -> list[dict[str, Any]]:
    import json

    schemas_dir = repo_root / "schemas"
    entries = []
    schema_files = sorted(p for p in schemas_dir.glob("*.json"))
    for path in schema_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CollectorUnavailable(f"schema_identifiers: {path} does not parse as JSON: {exc}") from exc
        schema_id = data.get("$id", "")
        referenced_by = sorted({
            rel(repo_root, f) for f in scan_files
            if schema_id and schema_id in f.read_text(encoding="utf-8", errors="replace")
            and f.resolve() != path.resolve()
        }) if schema_id else []
        entries.append({
            "path": rel(repo_root, path),
            "id": schema_id,
            "referenced_by": referenced_by,
        })
    return entries


# ---------------------------------------------------------------------------
# environment


def collect_environment() -> dict[str, Any]:
    packages = sorted(
        (
            {"name": dist.metadata.get("Name", dist.metadata.get("Summary", "unknown")) or "unknown",
             "version": dist.version or "unknown"}
            for dist in importlib_metadata.distributions()
        ),
        key=lambda d: d["name"].lower(),
    )
    # de-duplicate (some environments list the same distribution twice via
    # multiple .dist-info paths on sys.path)
    seen = set()
    deduped = []
    for pkg in packages:
        key = (pkg["name"], pkg["version"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(pkg)
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "installed_packages": deduped,
    }
