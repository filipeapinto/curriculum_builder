"""Pure, fail-closed channel reducers for the Plan 26 factory state.

Every reducer has the LangGraph channel signature ``(existing, new) -> merged``
and is a pure function of its two arguments: no clock, no filesystem, no
ordering dependence. A violation raises a typed :class:`ReducerError`; nothing
is ever silently dropped, coerced, or merged best-effort.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable
from typing import Any

__all__ = [
    "ReducerError",
    "NonSerializableValue",
    "CorrelationKeyError",
    "WriteOnceConflict",
    "DuplicateConflict",
    "UnionConflict",
    "HeadAdvanceError",
    "ReplaceCurrentError",
    "StatusTransitionError",
    "CounterRegression",
    "AcceptOnceConflict",
    "TerminalConflict",
    "canonical_json",
    "canonical_digest",
    "correlation_key",
    "write_once",
    "append_unique",
    "append_unique_by",
    "union_disjoint",
    "advance_head",
    "replace_current",
    "monotonic_status",
    "monotonic_max",
    "accept_once",
    "write_episode_terminal_once",
    "REDUCER_CLASSES",
    "REDUCERS",
    "DEFAULT_CORRELATION_KEY",
    "HEAD_RECORD_FIELDS",
    "UNIT_STATUSES",
    "INITIAL_UNIT_STATUSES",
    "UNIT_STATUS_TRANSITIONS",
    "TERMINAL_KINDS",
]


class ReducerError(Exception):
    """Base class for every fail-closed reducer violation."""


class NonSerializableValue(ReducerError):
    """A value is not JSON-compatible and cannot be checkpointed."""


class CorrelationKeyError(ReducerError):
    """A record is missing, or malformed in, its declared correlation key."""


class WriteOnceConflict(ReducerError):
    """A write-once channel received a second, differing value."""


class DuplicateConflict(ReducerError):
    """An append-unique channel received a differing record under a used key."""


class UnionConflict(ReducerError):
    """A disjoint-union channel received a differing value for a used key."""


class HeadAdvanceError(ReducerError):
    """A head advance did not present the current head's child at version+1."""


class ReplaceCurrentError(ReducerError):
    """A replace-current channel received a value it cannot hold."""


class StatusTransitionError(ReducerError):
    """A status map received an undeclared or regressing transition."""


class CounterRegression(ReducerError):
    """A monotonic counter was asked to decrease or take a non-counter value."""


class AcceptOnceConflict(ReducerError):
    """An accepted receipt was rewritten with differing content."""


class TerminalConflict(ReducerError):
    """An episode was given an unknown or second, differing terminal."""


def _ensure_json_value(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise NonSerializableValue(f"{path}: non-finite float is not round-trip-stable JSON")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise NonSerializableValue(f"{path}: object key {key!r} is not a string")
            _ensure_json_value(item, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _ensure_json_value(item, f"{path}[{index}]")
        return
    raise NonSerializableValue(f"{path}: {type(value).__name__} is not JSON-compatible")


def canonical_json(value: Any) -> str:
    """Serialize ``value`` under the one Plan 26 canonical-JSON convention."""

    _ensure_json_value(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def canonical_digest(value: Any) -> str:
    """SHA-256 of the canonical-JSON encoding of ``value``."""

    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _equal(left: Any, right: Any) -> bool:
    return canonical_json(left) == canonical_json(right)


def _require_record(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CorrelationKeyError(f"{context}: expected a JSON object, got {type(value).__name__}")
    _ensure_json_value(value)
    return value


def _require_mapping_update(value: Any, error: type[ReducerError], context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise error(f"{context}: expected a keyed object update, got {type(value).__name__}")
    for key in value:
        if not isinstance(key, str):
            raise error(f"{context}: key {key!r} is not a string")
    return value


DEFAULT_CORRELATION_KEY: tuple[str, ...] = ("key",)


def correlation_key(record: dict[str, Any], key_fields: tuple[str, ...]) -> str:
    """Build the declared correlation key of ``record`` as a canonical string."""

    parts: list[Any] = []
    for field in key_fields:
        if field not in record:
            raise CorrelationKeyError(f"record is missing declared correlation field {field!r}")
        part = record[field]
        if not (part is None or isinstance(part, (str, bool, int))):
            raise CorrelationKeyError(
                f"correlation field {field!r} must be a scalar, got {type(part).__name__}"
            )
        parts.append(part)
    return canonical_json(parts)


def _tag(reducer_class: str, key_fields: tuple[str, ...] | None = None):
    def decorate(function: Callable[..., Any]) -> Callable[..., Any]:
        function.reducer_class = reducer_class  # type: ignore[attr-defined]
        function.correlation_key_fields = key_fields  # type: ignore[attr-defined]
        return function

    return decorate


@_tag("write_once")
def write_once(existing: Any, new: Any) -> Any:
    """Absent to one value; equal replay is idempotent; differing replay fails.

    ``new is None`` is a no-op rather than a value: an absent optional field and
    an explicit null are the same persisted state, so a null update can never
    contradict a recorded value.
    """

    if new is None:
        return existing
    _ensure_json_value(new)
    if existing is None:
        return new
    if _equal(existing, new):
        return existing
    raise WriteOnceConflict(
        f"write-once channel already holds {canonical_json(existing)}; "
        f"refusing differing value {canonical_json(new)}"
    )


def _append_unique(existing: Any, new: Any, key_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = list(existing) if existing else []
    if new is None:
        return merged
    updates = new if isinstance(new, list) else [new]
    index = {correlation_key(_require_record(rec, "existing entry"), key_fields): pos
             for pos, rec in enumerate(merged)}
    for candidate in updates:
        record = _require_record(candidate, "append-unique update")
        key = correlation_key(record, key_fields)
        seen = index.get(key)
        if seen is not None:
            if _equal(merged[seen], record):
                continue
            raise DuplicateConflict(
                f"append-unique key {key} already holds a differing record "
                f"({canonical_json(merged[seen])} vs {canonical_json(record)})"
            )
        index[key] = len(merged)
        merged.append(record)
    return merged


@_tag("append_unique", DEFAULT_CORRELATION_KEY)
def append_unique(existing: Any, new: Any) -> list[dict[str, Any]]:
    """Append by declared correlation key; equal replay idempotent, conflict fails."""

    return _append_unique(existing, new, DEFAULT_CORRELATION_KEY)


def append_unique_by(*key_fields: str) -> Callable[[Any, Any], list[dict[str, Any]]]:
    """Return an :func:`append_unique` reducer over an explicit correlation key."""

    if not key_fields:
        raise CorrelationKeyError("append_unique_by requires at least one correlation field")
    fields = tuple(key_fields)

    def reducer(existing: Any, new: Any) -> list[dict[str, Any]]:
        return _append_unique(existing, new, fields)

    reducer.__name__ = "append_unique_by(" + ",".join(fields) + ")"
    reducer.reducer_class = "append_unique"  # type: ignore[attr-defined]
    reducer.correlation_key_fields = fields  # type: ignore[attr-defined]
    return reducer


@_tag("union_disjoint")
def union_disjoint(existing: Any, new: Any) -> dict[str, Any]:
    """Associative/commutative map union for fan-out; differing key value fails."""

    merged: dict[str, Any] = dict(existing) if existing else {}
    if new is None:
        return merged
    update = _require_mapping_update(new, UnionConflict, "union-disjoint update")
    for key, value in update.items():
        _ensure_json_value(value)
        if key in merged:
            if _equal(merged[key], value):
                continue
            raise UnionConflict(
                f"disjoint-union key {key!r} already holds {canonical_json(merged[key])}; "
                f"refusing differing value {canonical_json(value)}"
            )
        merged[key] = value
    return merged


HEAD_RECORD_FIELDS: tuple[str, ...] = ("version", "parent_hash", "hash")


def _require_head(value: Any, context: str) -> dict[str, Any]:
    record = _require_record(value, context)
    for field in HEAD_RECORD_FIELDS:
        if field not in record:
            raise HeadAdvanceError(f"{context}: head record is missing {field!r}")
    version = record["version"]
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise HeadAdvanceError(f"{context}: head version must be an integer >= 1")
    if not isinstance(record["hash"], str) or not record["hash"]:
        raise HeadAdvanceError(f"{context}: head hash must be a non-empty string")
    parent = record["parent_hash"]
    if parent is not None and not isinstance(parent, str):
        raise HeadAdvanceError(f"{context}: parent_hash must be a string or null")
    return record


@_tag("advance_head")
def advance_head(existing: Any, new: Any) -> dict[str, Any]:
    """Accept only a child whose parent equals the old head at exactly version+1."""

    heads: dict[str, Any] = dict(existing) if existing else {}
    if new is None:
        return heads
    update = _require_mapping_update(new, HeadAdvanceError, "advance-head update")
    for key, candidate in update.items():
        child = _require_head(candidate, f"head {key!r}")
        current = heads.get(key)
        if current is None:
            if child["version"] != 1 or child["parent_hash"] is not None:
                raise HeadAdvanceError(
                    f"head {key!r}: genesis head must be version 1 with a null parent_hash"
                )
            heads[key] = child
            continue
        if _equal(current, child):
            continue
        if child["version"] != current["version"] + 1:
            raise HeadAdvanceError(
                f"head {key!r}: expected version {current['version'] + 1}, got {child['version']}"
            )
        if child["parent_hash"] != current["hash"]:
            raise HeadAdvanceError(
                f"head {key!r}: parent_hash {child['parent_hash']!r} is not the current head "
                f"hash {current['hash']!r}"
            )
        heads[key] = child
    return heads


@_tag("replace_current")
def replace_current(existing: Any, new: Any) -> Any:
    """Single-writer ephemeral field; ``None`` is the explicit clear after consumption."""

    if new is None:
        return None
    try:
        _ensure_json_value(new)
    except NonSerializableValue as error:
        raise ReplaceCurrentError(str(error)) from error
    return new


UNIT_STATUSES: tuple[str, ...] = (
    "PENDING",
    "SELECTED",
    "SOURCING",
    "BUILDING",
    "REVIEWING",
    "REPAIRING",
    "ACCEPTED",
    "BLOCKED",
)

INITIAL_UNIT_STATUSES: frozenset[str] = frozenset({"PENDING", "SELECTED"})

UNIT_STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    "PENDING": frozenset({"PENDING", "SELECTED", "BLOCKED"}),
    "SELECTED": frozenset({"SELECTED", "SOURCING", "BLOCKED"}),
    "SOURCING": frozenset({"SOURCING", "BUILDING", "BLOCKED"}),
    "BUILDING": frozenset({"BUILDING", "REVIEWING", "BLOCKED"}),
    "REVIEWING": frozenset({"REVIEWING", "REPAIRING", "ACCEPTED", "BLOCKED"}),
    "REPAIRING": frozenset({"REPAIRING", "REVIEWING", "BLOCKED"}),
    "ACCEPTED": frozenset({"ACCEPTED"}),
    "BLOCKED": frozenset({"BLOCKED"}),
}


@_tag("monotonic_status")
def monotonic_status(existing: Any, new: Any) -> dict[str, str]:
    """Only declared per-unit transitions; acceptance and blocking never regress."""

    statuses: dict[str, str] = dict(existing) if existing else {}
    if new is None:
        return statuses
    update = _require_mapping_update(new, StatusTransitionError, "status update")
    for unit_id, status in update.items():
        if status not in UNIT_STATUS_TRANSITIONS:
            raise StatusTransitionError(f"unit {unit_id!r}: unknown status {status!r}")
        current = statuses.get(unit_id)
        if current is None:
            if status not in INITIAL_UNIT_STATUSES:
                raise StatusTransitionError(
                    f"unit {unit_id!r}: first status must be one of "
                    f"{sorted(INITIAL_UNIT_STATUSES)}, got {status!r}"
                )
            statuses[unit_id] = status
            continue
        if status not in UNIT_STATUS_TRANSITIONS[current]:
            raise StatusTransitionError(
                f"unit {unit_id!r}: undeclared transition {current!r} -> {status!r}"
            )
        statuses[unit_id] = status
    return statuses


@_tag("monotonic_max")
def monotonic_max(existing: Any, new: Any) -> dict[str, int]:
    """Counters never decrease; equal replay is idempotent."""

    counters: dict[str, int] = dict(existing) if existing else {}
    if new is None:
        return counters
    update = _require_mapping_update(new, CounterRegression, "counter update")
    for key, value in update.items():
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise CounterRegression(f"counter {key!r} must be a non-negative integer, got {value!r}")
        current = counters.get(key)
        if current is not None and value < current:
            raise CounterRegression(f"counter {key!r} cannot regress from {current} to {value}")
        counters[key] = value
    return counters


@_tag("accept_once")
def accept_once(existing: Any, new: Any) -> dict[str, Any]:
    """Immutable accepted receipt per key; equal replay only."""

    receipts: dict[str, Any] = dict(existing) if existing else {}
    if new is None:
        return receipts
    update = _require_mapping_update(new, AcceptOnceConflict, "acceptance update")
    for key, receipt in update.items():
        _ensure_json_value(receipt)
        current = receipts.get(key)
        if current is None:
            receipts[key] = receipt
            continue
        if _equal(current, receipt):
            continue
        raise AcceptOnceConflict(
            f"accepted receipt {key!r} is immutable; refusing to rewrite "
            f"{canonical_json(current)} as {canonical_json(receipt)}"
        )
    return receipts


TERMINAL_KINDS: tuple[str, ...] = (
    "UNIT_ACCEPTED",
    "COMPLETE",
    "INTERRUPTED",
    "PAUSED_PREREQUISITE",
    "CONVERGENCE_EXHAUSTED",
    "SYSTEM_FAILURE",
)


@_tag("write_episode_terminal_once")
def write_episode_terminal_once(existing: Any, new: Any) -> Any:
    """Exactly one terminal per episode; a differing second write fails."""

    if new is None:
        return existing
    if not isinstance(new, dict):
        raise TerminalConflict(f"terminal must be a JSON object, got {type(new).__name__}")
    _ensure_json_value(new)
    if new.get("kind") not in TERMINAL_KINDS:
        raise TerminalConflict(f"unknown terminal kind {new.get('kind')!r}")
    if existing is None:
        return new
    if _equal(existing, new):
        return existing
    raise TerminalConflict(
        f"episode already terminated as {canonical_json(existing)}; "
        f"refusing second terminal {canonical_json(new)}"
    )


REDUCERS: dict[str, Callable[[Any, Any], Any]] = {
    "write_once": write_once,
    "append_unique": append_unique,
    "union_disjoint": union_disjoint,
    "advance_head": advance_head,
    "replace_current": replace_current,
    "monotonic_status": monotonic_status,
    "monotonic_max": monotonic_max,
    "accept_once": accept_once,
    "write_episode_terminal_once": write_episode_terminal_once,
}

REDUCER_CLASSES: tuple[str, ...] = tuple(REDUCERS)
