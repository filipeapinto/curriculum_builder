"""Spec v8 section 10.17: behavioral differential, unit-tested at the comparator itself.

``compare()`` must not report a difference for a field spec v8 section 7's
``normalization_rules`` declares equivalent, and must not silently hide a field that
genuinely differs -- both directions were previously untested, and the import-origin
field had a real bug (it compared un-stripped absolute paths after the P03 source
move introduced a second path segment the old stripper did not know about).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from refactor_repo import baseline  # noqa: E402


def _document(**overrides):
    base = {
        "repository_commit": "a" * 40,
        "tests_and_gates": {
            "pytest_collect": {"exit_code": 0},
            "gate_harness_selftest": {"exit_code": 0},
        },
        "import_origin": {
            "origin": "/checkout/src/curriculum_factory/__init__.py",
            "origin_relative_to_repo_root": "src/curriculum_factory/__init__.py",
        },
        "cli_help_and_invalid_input": [
            {"exit_code": 0, "stdout_sha256": "h1", "stderr_sha256": "e1"},
        ],
        "schema_resolution": [{"path": "a.json", "resolves": True}],
        "output_containment": {
            "accepted_case": {"raised": False},
            "rejected_case": {"raised": True},
        },
        "representative_artifacts": [{"path": "a.json", "sha256": "digest1"}],
    }
    base.update(overrides)
    return base


def test_a_different_absolute_checkout_prefix_for_the_same_relative_module_is_equivalent():
    first = _document(import_origin={
        "origin": "/one/checkout/src/curriculum_factory/__init__.py",
        "origin_relative_to_repo_root": "src/curriculum_factory/__init__.py",
    })
    second = _document(import_origin={
        "origin": "/somewhere/else/src/curriculum_factory/__init__.py",
        "origin_relative_to_repo_root": "src/curriculum_factory/__init__.py",
    })
    result = baseline.compare(first, second)
    assert "import_origin.origin (relative to repo root)" in result["equivalent_fields"]


def test_a_genuinely_different_relative_module_location_is_reported_as_a_difference():
    first = _document(import_origin={
        "origin": "/checkout/runtime/__init__.py",
        "origin_relative_to_repo_root": "runtime/__init__.py",
    })
    second = _document(import_origin={
        "origin": "/checkout/src/curriculum_factory/__init__.py",
        "origin_relative_to_repo_root": "src/curriculum_factory/__init__.py",
    })
    result = baseline.compare(first, second)
    fields = {d["field"] for d in result["differences"]}
    assert "import_origin.origin (relative to repo root)" in fields
    assert result["verdict"] == "CHANGED"


def test_identical_documents_compare_equivalent_on_every_field() -> None:
    document = _document()
    result = baseline.compare(document, _document())
    assert result["differences"] == []
    assert result["verdict"] == "EQUIVALENT"
