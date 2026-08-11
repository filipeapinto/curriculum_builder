"""Durable typed state and reducers for the Plan 25 curriculum factory graph."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

from .io import atomic_json, canonical_hash, require_within


class FactoryStateError(RuntimeError):
    """A reducer, identity, checkpoint, or terminal invariant was violated."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class FactoryStateStore:
    """One atomic state document plus an append-only activation/event stream.

    Workers never receive this object. Only the controller invokes its reducers.
    """

    STATE_NAME = "factory_state.json"
    EVENTS_NAME = "factory_events.jsonl"

    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.state_path = require_within(self.root / self.STATE_NAME, self.root)
        self.events_path = require_within(self.root / self.EVENTS_NAME, self.root)

    def exists(self) -> bool:
        return self.state_path.is_file()

    def read(self) -> dict[str, Any]:
        if not self.state_path.is_file():
            raise FactoryStateError(f"missing {self.STATE_NAME} under {self.root}")
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def initialize(self, identity: dict[str, Any], frozen_inputs: dict[str, str],
                   effective_limits: dict[str, Any]) -> dict[str, Any]:
        if self.state_path.exists() or self.events_path.exists():
            raise FactoryStateError("factory state is write-once and already exists")
        state: dict[str, Any] = {
            "state_version": 1,
            "identity": identity,
            "frozen_inputs": frozen_inputs,
            "effective_limits": effective_limits,
            "effective_run": None,
            "status": "INITIALIZING",
            "cursor": 0,
            "unit_selections": {},
            "route_decisions": {},
            "capability_receipts": {},
            "source_requests": {},
            "retrieval_results": {},
            "source_results": {},
            "admitted_sources": {},
            "unit_artifacts": {},
            "unit_heads": {},
            "unit_checks": {},
            "unit_page_inventory": {},
            "unit_review_packets": {},
            "unit_reviews": {},
            "unit_repair_requests": {},
            "unit_repairs": {},
            "unit_status": {},
            "accepted_units": {},
            "workbook_artifacts": {},
            "workbook_heads": {},
            "workbook_checks": {},
            "workbook_page_inventory": {},
            "workbook_review_packets": {},
            "workbook_reviews": {},
            "workbook_repair_requests": {},
            "workbook_repairs": {},
            "counters": {},
            "invalidations": {},
            "checkpoints": {},
            "terminal": None,
            "terminal_history": [],
            "created_utc": utc_now(),
            "updated_utc": utc_now(),
        }
        atomic_json(self.state_path, state, root=self.root)
        self.events_path.touch(exist_ok=False)
        self.append_event("STATE_INITIALIZED", {"run_id": identity["run_id"]})
        return state

    def _write(self, state: dict[str, Any]) -> dict[str, Any]:
        state["updated_utc"] = utc_now()
        atomic_json(self.state_path, state, root=self.root)
        return state

    def append_event(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        event = {
            "ordinal": self.event_count() + 1,
            "event_type": event_type,
            "recorded_utc": utc_now(),
            "payload": payload,
        }
        event["event_hash"] = canonical_hash(event)
        encoded = json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n"
        descriptor = os.open(self.events_path, os.O_WRONLY | os.O_APPEND)
        try:
            os.write(descriptor, encoded.encode("utf-8"))
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return event

    def events(self) -> list[dict[str, Any]]:
        if not self.events_path.is_file():
            return []
        events = [json.loads(line) for line in self.events_path.read_text().splitlines() if line]
        for index, event in enumerate(events, 1):
            digest = event.pop("event_hash")
            if event["ordinal"] != index or canonical_hash(event) != digest:
                raise FactoryStateError(f"factory event chain invalid at ordinal {index}")
            event["event_hash"] = digest
        return events

    def event_count(self) -> int:
        if not self.events_path.is_file():
            return 0
        return sum(1 for line in self.events_path.read_text().splitlines() if line)

    def write_once(self, field: str, value: Any) -> None:
        state = self.read()
        if state.get(field) is not None:
            raise FactoryStateError(f"write-once field already set: {field}")
        state[field] = value
        self._write(state)
        self.append_event("WRITE_ONCE", {"field": field, "value_hash": canonical_hash(value)})

    def append_unique(self, field: str, key: str, value: Any) -> None:
        state = self.read()
        mapping = state.get(field)
        if not isinstance(mapping, dict):
            raise FactoryStateError(f"append reducer target is not a map: {field}")
        if key in mapping:
            raise FactoryStateError(f"duplicate append key: {field}[{key}]")
        mapping[key] = value
        self._write(state)
        self.append_event("APPEND_UNIQUE", {
            "field": field, "key": key, "value_hash": canonical_hash(value)})

    def replace_current(self, field: str, key: str, value: Any,
                        *, previous_version: int | None = None) -> None:
        """Advance a versioned head, never overwrite an artifact version."""
        state = self.read()
        heads = state.get(field)
        if not isinstance(heads, dict):
            raise FactoryStateError(f"head reducer target is not a map: {field}")
        current = heads.get(key)
        if previous_version is not None and current != previous_version:
            raise FactoryStateError(
                f"head mismatch for {field}[{key}]: expected {previous_version}, found {current}")
        if current is not None and not isinstance(value, int):
            raise FactoryStateError("versioned heads must be integer versions")
        if current is not None and value != current + 1:
            raise FactoryStateError(f"head must advance exactly once: {current} -> {value}")
        heads[key] = value
        self._write(state)
        self.append_event("ADVANCE_HEAD", {"field": field, "key": key, "value": value})

    def set_status(self, status: str) -> None:
        state = self.read()
        if state.get("terminal") is not None:
            raise FactoryStateError("status cannot advance after terminal")
        state["status"] = status
        self._write(state)
        self.append_event("STATUS", {"status": status})

    def set_cursor(self, ordinal: int) -> None:
        state = self.read()
        current = int(state.get("cursor", 0))
        if ordinal < current or ordinal > current + 1:
            raise FactoryStateError(f"cursor may advance by at most one: {current} -> {ordinal}")
        state["cursor"] = ordinal
        self._write(state)
        self.append_event("CURSOR", {"ordinal": ordinal})

    def increment(self, key: str, maximum: int) -> int:
        state = self.read()
        used = int(state["counters"].get(key, 0))
        if used >= maximum:
            raise FactoryStateError(f"counter exhausted before activation: {key} ({used}/{maximum})")
        state["counters"][key] = used + 1
        self._write(state)
        self.append_event("COUNTER", {"key": key, "used": used + 1, "maximum": maximum})
        return used + 1

    def update_unit_status(self, unit_id: str, status: str) -> None:
        order = {"NOT_STARTED": 0, "ACTIVE": 1, "ACCEPTED": 2}
        if status not in order:
            raise FactoryStateError(f"illegal unit status: {status}")
        state = self.read()
        current = state["unit_status"].get(unit_id, "NOT_STARTED")
        if order[status] < order[current] or order[status] > order[current] + 1:
            raise FactoryStateError(f"illegal unit status transition: {current} -> {status}")
        state["unit_status"][unit_id] = status
        self._write(state)
        self.append_event("UNIT_STATUS", {"unit_id": unit_id, "status": status})

    def write_terminal(self, terminal: str, guard: dict[str, Any]) -> dict[str, Any]:
        allowed = {"UNIT_ACCEPTED", "COMPLETE", "INTERRUPTED", "PAUSED_PREREQUISITE",
                   "CONVERGENCE_EXHAUSTED", "SYSTEM_FAILURE"}
        if terminal not in allowed:
            raise FactoryStateError(f"illegal terminal: {terminal}")
        state = self.read()
        if state.get("terminal") is not None:
            raise FactoryStateError("terminal is write-once")
        record = {"terminal": terminal, "guard": guard, "recorded_utc": utc_now(),
                  "run_id": state["identity"]["run_id"]}
        record["record_hash"] = canonical_hash(record)
        state["terminal"] = record
        state["status"] = terminal
        self._write(state)
        self.append_event("TERMINAL", record)
        return record

    def validate_identity(self, expected_run_id: str) -> None:
        actual = self.read()["identity"]["run_id"]
        if actual != expected_run_id:
            raise FactoryStateError(f"resume identity mismatch: expected {expected_run_id}, found {actual}")

    def resume_interrupted(self) -> None:
        state = self.read()
        terminal = state.get("terminal")
        if terminal is None:
            state["status"] = "ACTIVE"
        elif terminal.get("terminal") == "INTERRUPTED":
            state["terminal_history"].append(terminal)
            state["terminal"] = None
            state["status"] = "ACTIVE"
        else:
            raise FactoryStateError(
                f"only INTERRUPTED may resume; run records {terminal.get('terminal')}")
        self._write(state)
        self.append_event("RESUME", {"prior_terminal": terminal})
