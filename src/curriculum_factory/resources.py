"""Access to resources the package owns and ships.

Everything reachable from here is *package-owned*: immutable, versioned with the
code, meaningless without it, and declared in both wheel and sdist. It is read
through :mod:`importlib.resources`, so it keeps working when the distribution is
not an unpacked directory tree -- a zipped wheel, a zipimport loader, or any other
importer that only offers a ``Traversable``.

The rule this module exists to enforce is that a package resource is never located
by asking where the package's own ``__file__`` happens to be and then counting
parent directories. That inference is what silently retargets an installed
package's resource reads into ``site-packages``; see the P03 handoff.

Repository-owned data -- ``policy/``, ``schemas/``, ``curricula/``,
``meta_prompt/`` and run outputs -- is *not* here. It belongs to the caller and is
reached only through an explicit root; see :mod:`curriculum_factory.roots`.
"""

from __future__ import annotations

import json
import shutil
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any

__all__ = [
    "ResourceError",
    "package_root",
    "config_dir",
    "prompt_dir",
    "schema_dir",
    "job_registry_text",
    "prompt_text",
    "package_schema",
    "package_file",
    "materialize",
]

_FACTORY = "curriculum_factory.langgraph_factory"


class ResourceError(RuntimeError):
    """A package-owned resource is missing, unreadable, or names an escape."""


def package_root() -> Traversable:
    """The distribution's own root, as a Traversable rather than a Path.

    Deliberately not a ``Path``: converting a Traversable to a filesystem path is
    the assumption this module exists to avoid. Use :func:`materialize` when a real
    file on disk is genuinely required.
    """
    return resources.files("curriculum_factory")


def _factory_dir(name: str) -> Traversable:
    # `files(package) / subdir`, not `files(package.subdir)`: config/, prompts/ and
    # schemas/ are resource directories, not importable packages, and only the first
    # form is defined for them.
    directory = resources.files(_FACTORY) / name
    if not directory.is_dir():
        raise ResourceError(
            f"the installed distribution has no {name}/ resource directory; the wheel "
            f"or sdist is missing its declared package data")
    return directory


def config_dir() -> Traversable:
    return _factory_dir("config")


def prompt_dir() -> Traversable:
    return _factory_dir("prompts")


def schema_dir() -> Traversable:
    return _factory_dir("schemas")


def _child(directory: Traversable, name: str, label: str) -> Traversable:
    """Resolve one entry inside a package resource directory.

    ``name`` must be a bare filename. A separator or a parent reference would let a
    caller address something outside the resource directory, so it is rejected
    rather than normalised -- the same containment stance
    :func:`curriculum_factory.io.require_within` takes for repository paths.
    """
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        raise ResourceError(f"{label} name must be a bare filename, got {name!r}")
    candidate = directory / name
    if not candidate.is_file():
        raise ResourceError(f"{label} not found in the installed distribution: {name}")
    return candidate


def _read_text(entry: Traversable, label: str) -> str:
    try:
        return entry.read_text(encoding="utf-8")
    except OSError as error:  # pragma: no cover - surfaced verbatim to the caller
        raise ResourceError(f"cannot read {label}: {error}") from error


def job_registry_text() -> str:
    """The model job registry, ``config/model_jobs.v1.yaml``."""
    return _read_text(_child(config_dir(), "model_jobs.v1.yaml", "job registry"),
                      "job registry")


def prompt_text(name: str) -> str:
    """One shipped model prompt, by bare filename."""
    return _read_text(_child(prompt_dir(), name, "prompt"), f"prompt {name}")


def package_schema(name: str) -> dict[str, Any]:
    """One package-internal JSON schema, parsed, by bare filename."""
    text = _read_text(_child(schema_dir(), name, "schema"), f"schema {name}")
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise ResourceError(f"schema {name} is not valid JSON: {error}") from error


def package_file(name: str) -> Traversable:
    """A file at the distribution root, by bare filename."""
    return _child(package_root(), name, "package file")


def materialize(entry: Traversable, destination: Path) -> Path:
    """Copy a package resource to a real path the caller owns.

    For the cases where a resource must exist on disk to be useful at all -- a
    script handed to another process, for instance. The caller supplies the
    destination, so nothing here assumes the distribution is writable or unpacked.
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with resources.as_file(entry) as concrete:
        shutil.copyfile(concrete, destination)
    return destination
