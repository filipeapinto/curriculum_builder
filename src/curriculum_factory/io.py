from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


class BoundaryError(RuntimeError):
    pass


def canonical(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def require_within(path: Path, root: Path, label: str = "path") -> Path:
    resolved = canonical(path)
    boundary = canonical(root)
    if resolved != boundary and boundary not in resolved.parents:
        raise BoundaryError(f"{label} escapes authorized root {boundary}: {resolved}")
    return resolved


def require_internal_output(output_root: Path, engine: Path) -> Path:
    output = canonical(output_root)
    base = canonical(engine / "outputs")
    if output != base and base not in output.parents:
        raise BoundaryError(f"output root must be beneath {base}: {output}")
    return output


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def atomic_json(path: Path, value: Any, *, root: Path) -> None:
    target = require_within(path, root, "write")
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        directory_fd = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
