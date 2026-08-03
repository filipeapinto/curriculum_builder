from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import time
from typing import Any

from .io import atomic_json, canonical_hash, require_within, sha256_file


class CheckpointError(RuntimeError):
    pass


class Checkpoints:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.directory = require_within(root / "checkpoints", root)
        self.directory.mkdir(parents=True, exist_ok=True)

    def write(self, *, ordinal: int, state: str, next_state: str, inputs: list[Path],
              outputs: list[Path], attempt: int, started_at: float,
              worker_identity: str = "controller", model: str | None = None,
              effort: str | None = None) -> Path:
        record: dict[str, Any] = {
            "checkpoint_version": 1, "ordinal": ordinal, "state": state,
            "next_state": next_state, "attempt": attempt,
            "elapsed_seconds": round(time.monotonic() - started_at, 6),
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "worker_identity": worker_identity,
            "inputs": [{"path": str(path.resolve()), "sha256": sha256_file(path)} for path in inputs],
            "outputs": [{"path": str(path.resolve()), "sha256": sha256_file(path)} for path in outputs],
            "executed_model": model, "executed_effort": effort,
        }
        record["record_hash"] = canonical_hash(record)
        path = self.directory / f"{ordinal:03d}_{state}.json"
        atomic_json(path, record, root=self.root)
        return path

    def valid_prefix(self) -> list[dict[str, Any]]:
        valid: list[dict[str, Any]] = []
        import json
        for path in sorted(self.directory.glob("*.json")):
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
                expected = value.pop("record_hash")
                if canonical_hash(value) != expected:
                    break
                for item in value["inputs"] + value["outputs"]:
                    file_path = Path(item["path"])
                    if not file_path.is_file() or sha256_file(file_path) != item["sha256"]:
                        raise CheckpointError(f"checkpoint hash mismatch: {file_path}")
                value["record_hash"] = expected
                valid.append(value)
            except CheckpointError:
                raise
            except Exception:
                break
        return valid
