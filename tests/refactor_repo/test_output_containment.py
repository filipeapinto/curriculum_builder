"""Spec v8 section 10.8: output containment.

A run directory beneath ``outputs/`` is accepted; every other kind of escape --
absolute, ``..`` traversal, a symlink, or a differently-cased alternate spelling
of the boundary -- is rejected before any artifact is created.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from curriculum_factory.io import BoundaryError, require_internal_output


@pytest.fixture
def engine(tmp_path: Path) -> Path:
    root = tmp_path / "engine"
    (root / "outputs").mkdir(parents=True)
    return root


def test_a_run_directory_beneath_outputs_is_accepted(engine: Path) -> None:
    resolved = require_internal_output(engine / "outputs" / "run1", engine)
    assert resolved == (engine / "outputs" / "run1").resolve()


def test_an_absolute_external_path_is_rejected(engine: Path, tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(BoundaryError):
        require_internal_output(outside, engine)
    assert not outside.exists() or list(outside.iterdir()) == []


def test_a_relative_traversal_escape_is_rejected(engine: Path) -> None:
    with pytest.raises(BoundaryError):
        require_internal_output(engine / "outputs" / ".." / ".." / "outside", engine)


def test_a_symlink_escape_is_rejected_before_any_write(engine: Path, tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (engine / "outputs" / "evil").symlink_to(outside)
    with pytest.raises(BoundaryError):
        require_internal_output(engine / "outputs" / "evil" / "run", engine)
    assert list(outside.iterdir()) == []


def test_an_alternate_case_spelling_of_the_boundary_is_rejected(engine: Path) -> None:
    # Never accepted textually as the boundary, even on a case-insensitive
    # filesystem where it may collide with the real outputs/ directory at the
    # OS level -- fail closed rather than assume normalization.
    with pytest.raises(BoundaryError):
        require_internal_output(engine / "OUTPUTS" / "run", engine)
