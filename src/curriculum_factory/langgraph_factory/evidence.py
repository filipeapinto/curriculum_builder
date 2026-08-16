"""Append-only, hash-chained product evidence for the Plan 26 output root.

Spec section 11.2's second persistence layer: ACT/EXEC activations, route and
execution receipts, checkpoint correlation, and the evidence index are durable
here regardless of what a LangGraph checkpoint contains. Every record carries a
monotonic ordinal and a hash covering its own canonical bytes plus its
predecessor's hash, so deletion, insertion, reorder, and byte-level tampering
are all detectable by recomputation.
"""

from __future__ import annotations

import fcntl
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from curriculum_factory.langgraph_factory.artifacts import (
    ArtifactStore,
    canonical_digest,
    canonical_json_bytes,
    file_digest,
    resolve_within,
)

GENESIS_HASH = "0" * 64
EVIDENCE_DIRNAME = "evidence"
LOG_AUDITS_DIRNAME = "log_audits"
EVIDENCE_RECORD_SCHEMA = "plan26.evidence_record.v1"
AUDIT_REPORT_SCHEMA = "plan26.log_audit.v1"

LOG_NAMES = (
    "events",
    "activations",
    "routes",
    "executions",
    "checkpoints",
    "index",
)

RESERVED_PAYLOAD_KEYS = frozenset({"schema", "ordinal", "prev_hash", "record_hash"})

COMMON_REQUIRED_FIELDS = ("run_id", "episode_id")

REQUIRED_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
    "events": ("kind", "node_id"),
    "activations": ("activation_id", "node_id", "phase"),
    "routes": ("activation_id", "node_id", "decision"),
    "executions": ("activation_id", "node_id", "status"),
    "checkpoints": ("checkpoint_id", "checkpoint_ns", "state_digest", "evidence_ordinal"),
    "index": ("key", "content_hash", "artifact_path"),
}

_RECORD_KEYS = frozenset({"schema", "ordinal", "prev_hash", "payload", "record_hash"})


class EvidenceError(Exception):
    pass


class EvidenceCorrupt(EvidenceError):
    pass


@dataclass(frozen=True)
class EvidenceRecord:
    log_name: str
    ordinal: int
    prev_hash: str
    record_hash: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class AuditResult:
    log_name: str
    status: str
    record_count: int
    high_water_mark: int
    broken_ordinal: int | None
    reason: str | None

    @property
    def passed(self) -> bool:
        return self.status == "PASS"

    def as_dict(self) -> dict[str, Any]:
        return {
            "log_name": self.log_name,
            "status": self.status,
            "record_count": self.record_count,
            "high_water_mark": self.high_water_mark,
            "broken_ordinal": self.broken_ordinal,
            "reason": self.reason,
        }


def _record_body(ordinal: int, prev_hash: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": EVIDENCE_RECORD_SCHEMA,
        "ordinal": ordinal,
        "prev_hash": prev_hash,
        "payload": dict(payload),
    }


def audit_log_file(path: Path, *, log_name: str | None = None) -> AuditResult:
    """Recompute the whole chain of a JSONL evidence file from its bytes."""
    path = Path(path)
    name = log_name if log_name is not None else path.stem
    if not path.exists():
        return AuditResult(name, "PASS", 0, 0, None, None)

    prev_hash = GENESIS_HASH
    expected_ordinal = 1
    verified = 0
    raw = path.read_bytes()
    lines = raw.split(b"\n")
    truncated = lines[-1] != b""
    if not truncated:
        lines.pop()

    for line in lines:
        def fail(reason: str) -> AuditResult:
            return AuditResult(name, "FAIL", len(lines), verified, expected_ordinal, reason)

        try:
            obj = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return fail(f"record is not valid JSON: {exc}")
        if not isinstance(obj, dict) or set(obj) != _RECORD_KEYS:
            return fail("record does not have the exact evidence record key set")
        if obj["schema"] != EVIDENCE_RECORD_SCHEMA:
            return fail(f"unexpected record schema {obj['schema']!r}")
        body = {k: v for k, v in obj.items() if k != "record_hash"}
        try:
            computed = canonical_digest(body)
        except ValueError as exc:
            return fail(f"record is not canonically serializable: {exc}")
        if computed != obj["record_hash"]:
            return fail("record hash does not cover its own bytes (tampered record)")
        if obj["ordinal"] != expected_ordinal:
            return fail(
                f"ordinal is {obj['ordinal']}, expected {expected_ordinal} "
                "(deleted, inserted, or reordered record)"
            )
        if obj["prev_hash"] != prev_hash:
            return fail("prev_hash does not match the preceding record hash (broken chain)")
        prev_hash = obj["record_hash"]
        verified = expected_ordinal
        expected_ordinal += 1

    if truncated:
        return AuditResult(
            name, "FAIL", len(lines), max(verified - 1, 0), verified,
            "final record is not newline terminated (torn append)",
        )
    return AuditResult(name, "PASS", len(lines), verified, None, None)


class EvidenceLog:
    """One append-only, hash-chained JSONL evidence file."""

    def __init__(self, root: Path, name: str) -> None:
        if name not in LOG_NAMES:
            raise EvidenceError(f"unknown evidence log: {name!r}")
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        (root / EVIDENCE_DIRNAME).mkdir(parents=True, exist_ok=True)
        self._root = root.resolve(strict=True)
        self._name = name
        self._relative = f"{EVIDENCE_DIRNAME}/{name}.jsonl"
        self._path = resolve_within(self._root, self._relative)

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._path

    def audit(self) -> AuditResult:
        return audit_log_file(self._path, log_name=self._name)

    def high_water_mark(self) -> int:
        return self.audit().high_water_mark

    def records(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        return [
            json.loads(line)
            for line in self._path.read_text(encoding="utf-8").splitlines()
            if line
        ]

    def append(self, payload: Mapping[str, Any]) -> EvidenceRecord:
        """Append one record; refuses forged chain fields and a broken chain."""
        if not isinstance(payload, Mapping):
            raise EvidenceError("evidence payload must be a mapping")
        forged = RESERVED_PAYLOAD_KEYS.intersection(payload)
        if forged:
            raise EvidenceError(
                f"caller may not supply chain fields {sorted(forged)}; "
                "ordinal and hashes are derived from the log itself"
            )
        missing = [
            field
            for field in COMMON_REQUIRED_FIELDS + REQUIRED_PAYLOAD_FIELDS[self._name]
            if field not in payload
        ]
        if missing:
            raise EvidenceError(
                f"{self._name} record is missing required fields {missing}"
            )

        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "a+b") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                audit = audit_log_file(self._path, log_name=self._name)
                if not audit.passed:
                    raise EvidenceCorrupt(
                        f"refusing to append to {self._name}: chain broken at ordinal "
                        f"{audit.broken_ordinal} ({audit.reason})"
                    )
                ordinal = audit.record_count + 1
                prev_hash = GENESIS_HASH
                if audit.record_count:
                    prev_hash = self.records()[-1]["record_hash"]
                body = _record_body(ordinal, prev_hash, payload)
                record_hash = canonical_digest(body)
                line = canonical_json_bytes({**body, "record_hash": record_hash}) + b"\n"
                handle.seek(0, os.SEEK_END)
                handle.write(line)
                handle.flush()
                os.fsync(handle.fileno())
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return EvidenceRecord(
            log_name=self._name,
            ordinal=ordinal,
            prev_hash=prev_hash,
            record_hash=record_hash,
            payload=dict(payload),
        )


class EvidenceStore:
    """The six append-only evidence logs plus their integrity audit reports."""

    def __init__(self, root: Path) -> None:
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        self._root = root.resolve(strict=True)
        self._artifacts = ArtifactStore(self._root)
        self._logs = {name: EvidenceLog(self._root, name) for name in LOG_NAMES}

    @property
    def root(self) -> Path:
        return self._root

    def log(self, name: str) -> EvidenceLog:
        if name not in self._logs:
            raise EvidenceError(f"unknown evidence log: {name!r}")
        return self._logs[name]

    def append(self, name: str, payload: Mapping[str, Any]) -> EvidenceRecord:
        return self.log(name).append(payload)

    def audit_all(self) -> dict[str, AuditResult]:
        return {name: log.audit() for name, log in self._logs.items()}

    def high_water_marks(self) -> dict[str, int]:
        return {name: result.high_water_mark for name, result in self.audit_all().items()}

    def write_audit_report(self) -> Path:
        """Write a content-addressed integrity report under ``evidence/log_audits/``."""
        results = self.audit_all()
        report = {
            "schema": AUDIT_REPORT_SCHEMA,
            "status": "PASS" if all(r.passed for r in results.values()) else "FAIL",
            "logs": {
                name: {
                    **result.as_dict(),
                    "file_digest": (
                        file_digest(self._logs[name].path)
                        if self._logs[name].path.exists()
                        else None
                    ),
                }
                for name, result in sorted(results.items())
            },
        }
        digest = canonical_digest(report)
        relative = f"{EVIDENCE_DIRNAME}/{LOG_AUDITS_DIRNAME}/audit.{digest}.json"
        path = self._artifacts.resolve(relative)
        payload = canonical_json_bytes({"report": report, "report_hash": digest})
        if path.is_file():
            if path.read_bytes() != payload:
                raise EvidenceCorrupt(f"content-addressed audit report differs at {relative}")
            return path
        return self._artifacts.put_bytes(relative, payload)
