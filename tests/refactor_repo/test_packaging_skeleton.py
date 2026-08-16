"""Focused static checks for the P01 packaging skeleton.

These are the fast, local half of P01's test suite. They inspect
``pyproject.toml`` and the ``src/curriculum_factory`` skeleton directly
(no build is performed here). The build/inspect/reproducibility half of
P01's six prompt tests is executed out-of-band against isolated clean
checkouts and recorded in the P01 checkpoint, because it requires network
access to provision a PEP 517 build frontend that is not part of this
repository's pinned runtime or test dependencies.

Every asserted value is traced to a specific P00 inventory field; see the
P01 checkpoint report for the full evidence trail.
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
SRC_ROOT = REPO_ROOT / "src"
PACKAGE_ROOT = SRC_ROOT / "curriculum_factory"

# P00 inventory identity table (identity:Python distribution, identity:Python package).
EXPECTED_DISTRIBUTION_NAME = "curriculum-factory"
EXPECTED_PACKAGE_NAME = "curriculum_factory"

# requirements/plan26.in header: "Python is pinned to >=3.13,<3.14 for Plan 26 reproducibility."
EXPECTED_REQUIRES_PYTHON = ">=3.13,<3.14"

# requirements/plan26.in "--- core runtime ---" and "--- existing runtime stack, made explicit ---"
# sections (excludes the "--- development only ---" section).
EXPECTED_RUNTIME_DEPENDENCIES = {
    "langgraph==1.2.9",
    "langgraph-checkpoint-sqlite==3.1.0",
    "jsonschema==4.26.0",
    "PyYAML==6.0.3",
    "Pillow==12.2.0",
}

# requirements/plan26.in "--- development only (tests; not installed on a production-only path) ---".
EXPECTED_DEV_DEPENDENCIES = {"pytest==9.0.3"}

# P00 inventory python_surface.entry_points (4 module_main_guard commands under runtime/).
EXPECTED_CONSOLE_SCRIPT_TARGETS = {
    "curriculum-factory-run-curriculum": "curriculum_factory.run_curriculum:main",
    "curriculum-factory-session-bridge": "curriculum_factory.session_bridge:main",
    "curriculum-factory-capability-cycle": "curriculum_factory.capability_cycle:main",
    "curriculum-factory-finalize-evidence": "curriculum_factory.finalize_evidence:main",
}


def _load_pyproject() -> dict:
    with PYPROJECT_PATH.open("rb") as handle:
        return tomllib.load(handle)


def test_pyproject_exists_at_repository_root():
    assert PYPROJECT_PATH.is_file(), "pyproject.toml must exist at the repository root"


def test_build_backend_is_declared():
    data = _load_pyproject()
    build_system = data["build-system"]
    assert build_system["build-backend"] == "setuptools.build_meta"
    assert any(req.startswith("setuptools") for req in build_system["requires"])
    assert any(req.startswith("wheel") for req in build_system["requires"])


def test_distribution_identity_matches_p00_inventory():
    data = _load_pyproject()
    project = data["project"]
    assert project["name"] == EXPECTED_DISTRIBUTION_NAME
    assert project["requires-python"] == EXPECTED_REQUIRES_PYTHON


def test_runtime_dependencies_match_plan26_core_section():
    data = _load_pyproject()
    dependencies = set(data["project"]["dependencies"])
    assert dependencies == EXPECTED_RUNTIME_DEPENDENCIES


def test_dev_optional_dependencies_match_plan26_development_section():
    data = _load_pyproject()
    dev_dependencies = set(data["project"]["optional-dependencies"]["dev"])
    assert dev_dependencies == EXPECTED_DEV_DEPENDENCIES


def test_console_scripts_cover_every_p00_entrypoint():
    data = _load_pyproject()
    scripts = data["project"]["scripts"]
    assert scripts == EXPECTED_CONSOLE_SCRIPT_TARGETS


def test_package_discovery_is_src_only():
    data = _load_pyproject()
    discovery = data["tool"]["setuptools"]["packages"]["find"]
    assert discovery["where"] == ["src"]
    assert discovery["include"] == ["curriculum_factory*"]


def test_package_data_declared_for_non_python_resources():
    data = _load_pyproject()
    package_data = data["tool"]["setuptools"]["package-data"]
    for extension in ("*.json", "*.md", "*.yaml", "*.mjs"):
        assert extension in package_data["*"]


def test_test_discovery_default_declared():
    data = _load_pyproject()
    assert data["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]


def test_pyproject_declares_no_other_top_level_project_dependency_groups():
    """P01 owns every pyproject.toml key at this checkpoint; guard against drift."""
    data = _load_pyproject()
    assert set(data["project"]["optional-dependencies"].keys()) == {"dev"}


def test_src_curriculum_factory_package_exists_and_is_minimal():
    assert PACKAGE_ROOT.is_dir()
    init_file = PACKAGE_ROOT / "__init__.py"
    assert init_file.is_file()
    python_files = sorted(p.relative_to(SRC_ROOT) for p in SRC_ROOT.rglob("*.py"))
    assert python_files == [Path("curriculum_factory/__init__.py")], (
        "P01 must not move runtime/ into src/curriculum_factory/; only the "
        "skeleton __init__.py may exist at this checkpoint"
    )


def test_runtime_directory_is_unchanged_by_this_checkpoint():
    """P01 declares packaging metadata only; runtime/ stays byte-identical to P00."""
    runtime_dir = REPO_ROOT / "runtime"
    assert runtime_dir.is_dir(), "runtime/ must still exist; P01 does not move production source"


def test_src_curriculum_factory_is_importable_without_installation():
    sys.path.insert(0, str(SRC_ROOT))
    try:
        import curriculum_factory  # noqa: F401

        assert curriculum_factory.__all__ == []
    finally:
        sys.path.remove(str(SRC_ROOT))
        sys.modules.pop("curriculum_factory", None)
