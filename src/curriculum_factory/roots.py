"""The repository data root, resolved explicitly and never inferred.

``policy/``, ``schemas/``, ``curricula/``, ``meta_prompt/`` and run outputs belong
to the operator, not to the distribution. Where they live is therefore an input,
supplied as an argument, a CLI option, or ``CURRICULUM_FACTORY_REPOSITORY_ROOT``.

What this module exists to make impossible is the alternative: locating that data
by taking the installed package's own ``__file__`` and counting parent
directories. That expression is correct in a source checkout and silently wrong
everywhere else -- it resolves into ``site-packages``, where the operator's data
has never been. It does not raise at import time; it produces a plausible path
that fails much later, or worse, succeeds against the wrong tree.

So a missing root is an error raised *before* any work begins, and it says what to
supply. An invalid root is likewise rejected up front. Package-owned resources are
never reached through here; see :mod:`curriculum_factory.resources`.
"""

from __future__ import annotations

import os
from pathlib import Path

__all__ = [
    "RepositoryRootError",
    "ENV_VAR",
    "EXPECTED_ENTRIES",
    "repository_root",
    "configured_repository_root",
    "require_data_dir",
]

ENV_VAR = "CURRICULUM_FACTORY_REPOSITORY_ROOT"

#: Directories a repository root is expected to carry. Used to reject a wrong root
#: early and by name, rather than letting one missing file surface a thousand lines
#: later as a confusing read failure.
EXPECTED_ENTRIES: tuple[str, ...] = ("policy", "schemas", "curricula", "meta_prompt")


class RepositoryRootError(RuntimeError):
    """No repository root was supplied, or the one supplied is not usable."""


def _explain_missing() -> str:
    return (
        "no repository data root was supplied. This is required: policy/, schemas/, "
        "curricula/, meta_prompt/ and outputs/ belong to the caller, and the installed "
        "package's own location is never treated as the repository location. Supply it "
        "as an explicit argument, as --engine-root on the CLI, or by setting "
        f"{ENV_VAR}."
    )


def configured_repository_root() -> Path | None:
    """The root from the environment, if one is configured. No inference."""
    raw = os.environ.get(ENV_VAR)
    if raw is None or not raw.strip():
        return None
    return Path(raw).expanduser().resolve(strict=False)


def repository_root(explicit: Path | str | None = None, *, require_data: bool = False) -> Path:
    """Resolve the repository data root, or raise with an actionable message.

    Precedence is explicit argument, then ``CURRICULUM_FACTORY_REPOSITORY_ROOT``.
    There is deliberately no third fallback.

    With ``require_data`` the root must also carry the expected data directories,
    which catches a root that exists but points somewhere else entirely -- the
    failure mode that is otherwise indistinguishable from an empty repository.
    """
    candidate = Path(explicit).expanduser().resolve(strict=False) if explicit is not None \
        else configured_repository_root()
    if candidate is None:
        raise RepositoryRootError(_explain_missing())
    if not candidate.exists():
        raise RepositoryRootError(
            f"repository data root does not exist: {candidate}. Supply an existing "
            f"directory as an explicit argument, as --engine-root, or via {ENV_VAR}.")
    if not candidate.is_dir():
        raise RepositoryRootError(
            f"repository data root is not a directory: {candidate}")
    if require_data:
        missing = [name for name in EXPECTED_ENTRIES if not (candidate / name).is_dir()]
        if missing:
            raise RepositoryRootError(
                f"repository data root {candidate} is missing "
                f"{', '.join(missing)}. This usually means the supplied root is not the "
                f"repository root. Expected to find: {', '.join(EXPECTED_ENTRIES)}.")
    return candidate


def require_data_dir(name: str, explicit: Path | str | None = None) -> Path:
    """One repository-owned data directory, resolved from an explicit root.

    Fails before any work with a message naming both the directory and the root it
    was looked for under, so a wrong root is diagnosable from the error alone.
    """
    root = repository_root(explicit)
    directory = root / name
    if not directory.is_dir():
        raise RepositoryRootError(
            f"repository data directory {name!r} not found under {root}. Either the "
            f"supplied root is wrong or the repository is incomplete.")
    return directory
