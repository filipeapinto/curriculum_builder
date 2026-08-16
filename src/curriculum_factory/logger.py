from __future__ import annotations

from datetime import date
import fcntl
import json
import os
from pathlib import Path
from typing import Any

import jsonschema

from .io import atomic_json, canonical, require_within


class LogError(RuntimeError):
    pass


class ExecutionLogger:
    """Exclusive-locking JSONL store whose records conform to execution-log v2."""

    def __init__(self, root: Path, schema_path: Path):
        self.root = canonical(root)
        self.path = require_within(self.root / "execution_log.jsonl", self.root)
        self.counter_path = require_within(self.root / ".execution_log.counter.json", self.root)
        self.lock_path = require_within(self.root / ".execution_log.lock", self.root)
        self.schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock_path.touch(exist_ok=True)
        if not self.counter_path.exists():
            atomic_json(self.counter_path, {"next_id": 1}, root=self.root)
        self.path.touch(exist_ok=True)

    def _records_unlocked(self) -> list[dict[str, Any]]:
        records = []
        for line_number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise LogError(f"invalid JSONL at line {line_number}: {error}") from error
        return records

    def records(self) -> list[dict[str, Any]]:
        with self.lock_path.open("r+") as lock:
            fcntl.flock(lock, fcntl.LOCK_SH)
            try:
                return self._records_unlocked()
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def _validate_record(self, record: dict[str, Any]) -> None:
        candidate = {"log_version": "2.0", "records": [record]}
        jsonschema.Draft202012Validator(self.schema).validate(candidate)

    def _append(self, prefix: str, payload: dict[str, Any]) -> str:
        with self.lock_path.open("r+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                counter = json.loads(self.counter_path.read_text(encoding="utf-8"))
                number = counter["next_id"]
                record_id = f"{prefix}-{number:03d}"
                record = {"id": record_id, **payload}
                self._validate_record(record)
                encoded = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
                descriptor = os.open(self.path, os.O_WRONLY | os.O_APPEND)
                try:
                    os.write(descriptor, encoded.encode("utf-8"))
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
                atomic_json(self.counter_path, {"next_id": number + 1}, root=self.root)
                return record_id
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    @staticmethod
    def _base(action: str, action_kind: str, authorized_paths: list[str], trigger: str,
              expected: str, input_quality: str = "complete") -> dict[str, Any]:
        return {
            "date": date.today().isoformat(),
            "action": action,
            "action_kind": action_kind,
            "input_quality": input_quality,
            "authorized_paths": authorized_paths,
            "trigger": trigger,
            "expected": expected,
        }

    def start(self, *, action: str, action_kind: str, authorized_paths: list[str],
              trigger: str, expected: str, decision_id: str | None = None,
              input_quality: str = "complete", notes: str | None = None) -> str:
        if action_kind == "model_call" and not decision_id:
            raise LogError("model call refused: a valid decision_id is required before invocation")
        payload = self._base(action, action_kind, authorized_paths, trigger, expected, input_quality)
        payload.update({"status": "started", "result": "pending"})
        if decision_id:
            payload["decision_id"] = decision_id
        if notes:
            payload["notes"] = notes
        return self._append("ACT", payload)

    def _require_open(self, start_id: str, records: list[dict[str, Any]]) -> dict[str, Any]:
        starts = {r["id"]: r for r in records if r.get("status") == "started"}
        closes = [r.get("closes") for r in records if r.get("closes")]
        if start_id not in starts:
            raise LogError(f"operation refused: start record does not exist: {start_id}")
        if start_id in closes:
            raise LogError(f"operation refused: start is already closed: {start_id}")
        return starts[start_id]

    def complete(self, start_id: str, *, result: str, notes: str | None = None,
                 skipped: bool = False) -> str:
        records = self.records()
        started = self._require_open(start_id, records)
        payload = self._base(started["action"], started["action_kind"],
                             started["authorized_paths"], started["trigger"],
                             started["expected"], started["input_quality"])
        payload.update({"status": "skipped" if skipped else "completed", "closes": start_id,
                        "result": result})
        if "decision_id" in started:
            payload["decision_id"] = started["decision_id"]
        if notes:
            payload["notes"] = notes
        return self._append("ACT", payload)

    def fail(self, start_id: str, *, failure_type: str, what_failed: str,
             expected: str, notes: str | None = None) -> str:
        records = self.records()
        started = self._require_open(start_id, records)
        payload = {
            "date": date.today().isoformat(), "closes": start_id,
            "failure_type": failure_type, "input_quality": started["input_quality"],
            "authorized_paths": started["authorized_paths"], "trigger": started["trigger"],
            "what_failed": what_failed, "expected": expected,
        }
        if notes:
            payload["notes"] = notes
        return self._append("EXEC", payload)

    def audit(self, *, required_checkpoint_ids: set[str] | None = None,
              required_transition_ids: set[str] | None = None) -> dict[str, Any]:
        records = self.records()
        numbers = [int(record["id"].split("-", 1)[1]) for record in records]
        monotonic = numbers == sorted(numbers) and len(numbers) == len(set(numbers))
        starts = {r["id"] for r in records if r.get("status") == "started"}
        closes = [r["closes"] for r in records if "closes" in r]
        unknown = sorted(set(closes) - starts)
        duplicate = sorted({item for item in closes if closes.count(item) > 1})
        unclosed = sorted(starts - set(closes))
        jsonschema.Draft202012Validator(self.schema).validate(
            {"log_version": "2.0", "records": records, "unclosed_starts": unclosed}
        )
        notes = "\n".join(str(r.get("notes", "")) for r in records)
        missing_checkpoints = sorted((required_checkpoint_ids or set()) - set(notes.split()))
        missing_transitions = sorted((required_transition_ids or set()) - set(notes.split()))
        return {
            "records": len(records), "starts": len(starts),
            "completions": sum(r.get("status") in {"completed", "skipped"} for r in records),
            "failures": sum(r["id"].startswith("EXEC-") for r in records),
            "monotonic": monotonic, "unclosed_starts": unclosed,
            "unknown_closes": unknown, "duplicate_closes": duplicate,
            "missing_checkpoints": missing_checkpoints,
            "missing_transitions": missing_transitions,
        }
