"""Spec v8 section 10.13: reference integrity, enforced against the exceptions inventory.

Every live occurrence of an old identity or path the inventory's lexical scan finds
must fall under a location in ``plans_internal/refactor_repo/exceptions/identity_and_paths.v1.yaml``
(spec section 2's exceptions inventory, with its exact location, consumer, rationale,
and removal condition already on file) -- or it is a stale reference this test fails on.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from refactor_repo import collectors  # noqa: E402

EXCEPTIONS_PATH = (
    REPO_ROOT / "plans_internal/refactor_repo/exceptions/identity_and_paths.v1.yaml"
)


def _load_exceptions() -> list[dict[str, Any]]:
    data = yaml.safe_load(EXCEPTIONS_PATH.read_text(encoding="utf-8"))
    return data["exceptions"]


def _is_excepted(source_file: str, exceptions: list[dict[str, Any]]) -> bool:
    candidate = Path(source_file)
    return any(
        candidate.full_match(location)
        for exception in exceptions
        for location in exception["locations"]
    )


@pytest.fixture(scope="module")
def old_identity_references() -> list[dict[str, Any]]:
    scan_files = list(collectors.iter_scan_files(REPO_ROOT))
    return collectors.collect_old_identity_references(REPO_ROOT, scan_files)


def test_every_exception_names_a_real_location_with_full_provenance() -> None:
    exceptions = _load_exceptions()
    assert exceptions, "the exceptions inventory must not be empty once any exists"
    for exception in exceptions:
        for field in ("locations", "token", "consumer", "rationale", "removal_condition"):
            assert exception.get(field), f"exception missing {field}: {exception}"


def test_every_live_old_identity_reference_is_a_recorded_exception(
    old_identity_references: list[dict[str, Any]],
) -> None:
    exceptions = _load_exceptions()
    uncovered = sorted({
        reference["source_file"] for reference in old_identity_references
        if not _is_excepted(reference["source_file"], exceptions)
    })
    assert not uncovered, (
        "old identity/path references with no recorded exception (spec v8 section 2 "
        "requires either migration or an exceptions-inventory entry):\n"
        + "\n".join(f"  {path}" for path in uncovered)
    )
