"""Durable checkpoint mechanics for the Plan 26 curriculum factory (spec section 11).

This module owns the *mechanics* of persistence and resume, not the node bodies
that use them. It configures the synchronous `SqliteSaver` under
``<output_root>/.langgraph/checkpoints.sqlite3``, guards one writer with an
exclusive output lock, derives episode threads from the immutable ``run_id``,
extracts prior-episode state through read-only checkpoint APIs only, and
computes the deterministic resume frontier that D92/D96 record.

Three structural rules are enforced by construction rather than by convention:

* nothing here ever executes a graph — the read side is exposed only through
  `ReadOnlyCheckpointView`, which has no ``invoke``-shaped attribute at all, so
  a prior thread cannot be continued even by accident;
* every model destination on a recovered frontier is rewritten to the
  deterministic classifier ``D91`` before any caller can see it; and
* orphan recovery is handed services that raise on first touch, so a recovery
  episode cannot reach a transport, retriever, or renderer.

LangGraph is imported lazily inside the functions that need it so this module
stays importable in an interpreter without the hash-locked environment.
"""

from __future__ import annotations

import dataclasses
import fcntl
import hashlib
import json
import os
import signal
import sqlite3
import time
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, Callable

from runtime.langgraph_factory.artifacts import (
    bytes_digest,
    canonical_digest,
    canonical_json_bytes,
    file_digest,
    resolve_within,
)

__all__ = [
    "PersistenceError",
    "ExecutionLockUnavailable",
    "EpisodeLedgerError",
    "AdmissionConflict",
    "ResumeRefused",
    "CheckpointCorrupt",
    "RecoveryServiceForbidden",
    "InterruptionRequested",
    "LANGGRAPH_DIRNAME",
    "CHECKPOINT_DB_RELATIVE",
    "EXECUTION_LOCK_RELATIVE",
    "IDENTITY_ENVELOPE_RELATIVE",
    "EPISODE_LEDGER_RELATIVE",
    "ADMISSION_LEDGER_RELATIVE",
    "INTERRUPT_TOKEN_RELATIVE",
    "CHECKPOINT_NS",
    "COMPILED_GRAPH_NAME",
    "STRICT_MSGPACK_ENV",
    "SQLITE_BUSY_TIMEOUT_MS",
    "REQUIRED_PRAGMAS",
    "LOCK_LOSER_EXIT_CODE",
    "MODEL_NODE_IDS",
    "MODEL_CLASSIFICATION_ENTRY",
    "RESUMABLE_TERMINALS",
    "NON_RESUMABLE_TERMINALS",
    "INTERRUPT_CLASSIFICATIONS",
    "RESUME_DRIFT_CLASSES",
    "BOOTSTRAP_FRESH",
    "BOOTSTRAP_RESUME",
    "BOOTSTRAP_RECOVER_ORPHAN",
    "langgraph_dir",
    "checkpoint_db_path",
    "execution_lock_path",
    "episode_thread_id",
    "recovery_thread_id",
    "invoke_config",
    "state_digest",
    "open_episode_session",
    "compute_fresh_run_id",
    "write_identity_envelope",
    "read_identity_envelope",
    "ExecutionLock",
    "InterruptToken",
    "open_checkpoint_connection",
    "read_connection_pragmas",
    "verify_connection_pragmas",
    "open_checkpoint_saver",
    "flush_checkpoint_durability",
    "verify_checkpoint_integrity",
    "verify_persistence_integrity",
    "ReadOnlyCheckpointView",
    "PriorEpisodeReadout",
    "extract_prior_episode",
    "EpisodeLeaseLedger",
    "AdmissionLedger",
    "EpisodeInvocation",
    "prepare_episode_invocation",
    "validate_resume_inputs",
    "classify_join_members",
    "compute_resume_frontier",
    "build_interrupt_terminal_candidate",
    "record_checkpoint_correlation",
    "ForbiddenService",
    "build_recovery_services",
]


# --------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------


class PersistenceError(Exception):
    """Base class for every persistence/resume refusal."""


class ExecutionLockUnavailable(PersistenceError):
    """Another live process already holds this output root's execution lock."""


class EpisodeLedgerError(PersistenceError):
    """The append-only episode lease ledger rejected a record."""


class AdmissionConflict(PersistenceError):
    """A replayed admission key carried different bytes than the committed one."""


class CheckpointCorrupt(PersistenceError):
    """SQLite checkpoint state or the append-only ledger failed integrity checks."""


class RecoveryServiceForbidden(PersistenceError):
    """A recovery episode touched a product service it is not allowed to have."""


class InterruptionRequested(PersistenceError):
    """A new external transmission was attempted after the interrupt token was set."""


@dataclasses.dataclass(frozen=True)
class ResumeRefused(PersistenceError):
    """Resume is inadmissible; no product work may run.

    ``drift_class`` is one of `RESUME_DRIFT_CLASSES` so a caller (and D00R) can
    record *which* invariant broke without string-matching a message.
    """

    drift_class: str
    field: str
    expected: Any = None
    observed: Any = None

    def __str__(self) -> str:  # pragma: no cover - message formatting
        return (
            f"resume refused ({self.drift_class}): {self.field} "
            f"expected={self.expected!r} observed={self.observed!r}"
        )


# --------------------------------------------------------------------------
# Frozen names, paths, and configuration (spec 11.1)
# --------------------------------------------------------------------------

LANGGRAPH_DIRNAME = ".langgraph"
CHECKPOINT_DB_RELATIVE = f"{LANGGRAPH_DIRNAME}/checkpoints.sqlite3"
EXECUTION_LOCK_RELATIVE = f"{LANGGRAPH_DIRNAME}/execution.lock"
IDENTITY_ENVELOPE_RELATIVE = f"{LANGGRAPH_DIRNAME}/identity_envelope.json"
EPISODE_LEDGER_RELATIVE = f"{LANGGRAPH_DIRNAME}/episodes.jsonl"
ADMISSION_LEDGER_RELATIVE = f"{LANGGRAPH_DIRNAME}/admissions.jsonl"
INTERRUPT_TOKEN_RELATIVE = f"{LANGGRAPH_DIRNAME}/interrupt.token"

CHECKPOINT_NS = ""
COMPILED_GRAPH_NAME = "plan26_curriculum_factory"
STRICT_MSGPACK_ENV = "LANGGRAPH_STRICT_MSGPACK"
SQLITE_BUSY_TIMEOUT_MS = 30_000

REQUIRED_PRAGMAS: dict[str, Any] = {
    "journal_mode": "wal",
    "synchronous": 2,  # FULL
    "foreign_keys": 1,
    "busy_timeout": SQLITE_BUSY_TIMEOUT_MS,
}

LOCK_LOSER_EXIT_CODE = 3

MODEL_NODE_IDS = frozenset({"M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08"})
MODEL_CLASSIFICATION_ENTRY = "D91"

RESUMABLE_TERMINALS = frozenset({"INTERRUPTED", "PAUSED_PREREQUISITE"})
NON_RESUMABLE_TERMINALS = frozenset(
    {"UNIT_ACCEPTED", "COMPLETE", "CONVERGENCE_EXHAUSTED", "SYSTEM_FAILURE"}
)

# Mirrors D98's own vocabulary. Restated rather than imported because this
# module must not import any node module; the interop test asserts they agree.
INTERRUPT_CLASSIFICATIONS = frozenset({"graceful_signal", "crashed_episode"})

RESUME_DRIFT_CLASSES = (
    "identity",
    "frozen_digest",
    "executable",
    "evidence",
    "accepted_bytes",
    "terminal_legality",
    "checkpoint",
)

BOOTSTRAP_FRESH = "FRESH"
BOOTSTRAP_RESUME = "RESUME"
BOOTSTRAP_RECOVER_ORPHAN = "RECOVER_ORPHAN"

GENESIS_HASH = "0" * 64
EPISODE_RECORD_SCHEMA = "plan26.episode_lease.v1"
ADMISSION_RECORD_SCHEMA = "plan26.admission.v1"
IDENTITY_ENVELOPE_SCHEMA = "plan26.identity_envelope.v1"
RESUME_FRONTIER_SCHEMA = "plan26.resume_frontier.v1"
RESUME_READOUT_SCHEMA = "plan26.resume_readout.v1"

IDENTITY_SEED_FIELDS = (
    "contract_version",
    "created_at",
    "engine_root",
    "curriculum_root",
    "active_manifest_path",
    "output_root",
    "mode",
    "requested_unit_id",
)

# Strict persisted values, set before any langgraph serde module is imported.
os.environ.setdefault(STRICT_MSGPACK_ENV, "true")


def langgraph_dir(output_root: Path | str) -> Path:
    return Path(output_root) / LANGGRAPH_DIRNAME


def checkpoint_db_path(output_root: Path | str) -> Path:
    return Path(output_root) / CHECKPOINT_DB_RELATIVE


def execution_lock_path(output_root: Path | str) -> Path:
    return Path(output_root) / EXECUTION_LOCK_RELATIVE


def episode_thread_id(run_id: str, episode_ordinal: int) -> str:
    if not isinstance(run_id, str) or not run_id:
        raise PersistenceError("run_id must be a non-empty string")
    if not isinstance(episode_ordinal, int) or isinstance(episode_ordinal, bool):
        raise PersistenceError("episode_ordinal must be an int")
    if episode_ordinal < 1:
        raise PersistenceError("episode_ordinal is one-based")
    return f"{run_id}:episode:{episode_ordinal:06d}"


def recovery_thread_id(run_id: str, orphan_episode_ordinal: int) -> str:
    if not isinstance(run_id, str) or not run_id:
        raise PersistenceError("run_id must be a non-empty string")
    if not isinstance(orphan_episode_ordinal, int) or isinstance(orphan_episode_ordinal, bool):
        raise PersistenceError("orphan_episode_ordinal must be an int")
    if orphan_episode_ordinal < 1:
        raise PersistenceError("orphan_episode_ordinal is one-based")
    return f"{run_id}:recover:{orphan_episode_ordinal}"


def invoke_config(thread_id: str) -> dict[str, dict[str, str]]:
    """The exact invoke config of spec 11.1 — no extra configurable keys."""
    if not isinstance(thread_id, str) or not thread_id:
        raise PersistenceError("thread_id must be a non-empty string")
    return {"configurable": {"thread_id": thread_id, "checkpoint_ns": CHECKPOINT_NS}}


def _mkdir_langgraph(output_root: Path | str) -> Path:
    directory = langgraph_dir(output_root)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _guarded(output_root: Path | str, relative: str) -> Path:
    _mkdir_langgraph(output_root)
    return resolve_within(Path(output_root), relative)


def _json_safe(value: Any) -> Any:
    """Coerce a value into canonical-JSON territory without inventing content."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise PersistenceError("non-finite floats are not persistable")
        return value
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
    if isinstance(value, (list, tuple, set, frozenset)):
        items = list(value)
        if isinstance(value, (set, frozenset)):
            items = sorted(items, key=repr)
        return [_json_safe(item) for item in items]
    if isinstance(value, bytes):
        return {"__bytes_sha256__": bytes_digest(value)}
    return {"__repr_sha256__": hashlib.sha256(repr(value).encode("utf-8")).hexdigest()}


def state_digest(values: Any) -> str:
    """Canonical-JSON digest of a state mapping, per digest_algorithm.v1."""
    return canonical_digest(_json_safe(values))


# --------------------------------------------------------------------------
# Run identity
# --------------------------------------------------------------------------


def compute_fresh_run_id(identity_seed: Mapping[str, Any]) -> str:
    """Deterministically derive the canonical fresh ``run_id`` D01 recomputes.

    The same seed always yields the same id, so `prepare_episode_invocation()`
    and D01 can arrive at it independently and a disagreement is detectable.
    """
    missing = [field for field in IDENTITY_SEED_FIELDS if field not in identity_seed]
    if missing:
        raise PersistenceError(f"identity seed is missing required fields {missing}")
    unknown = sorted(set(identity_seed) - set(IDENTITY_SEED_FIELDS))
    if unknown:
        raise PersistenceError(f"identity seed carries unknown fields {unknown}")
    seed = {field: identity_seed[field] for field in IDENTITY_SEED_FIELDS}
    return f"run-{canonical_digest(seed)}"


def write_identity_envelope(
    output_root: Path | str, envelope: Mapping[str, Any]
) -> Path:
    """Exclusively create the immutable identity envelope; refuse any rewrite."""
    path = _guarded(output_root, IDENTITY_ENVELOPE_RELATIVE)
    body = {"schema": IDENTITY_ENVELOPE_SCHEMA, **_json_safe(dict(envelope))}
    payload = canonical_json_bytes({"envelope": body, "envelope_hash": canonical_digest(body)})
    if path.exists():
        if path.read_bytes() != payload:
            raise ResumeRefused("identity", "identity_envelope", "immutable bytes", "differing bytes")
        return path
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        os.write(fd, payload)
        os.fsync(fd)
    finally:
        os.close(fd)
    return path


def read_identity_envelope(output_root: Path | str) -> dict[str, Any] | None:
    path = Path(output_root) / IDENTITY_ENVELOPE_RELATIVE
    if not path.is_file():
        return None
    document = json.loads(path.read_bytes().decode("utf-8"))
    envelope = document["envelope"]
    if canonical_digest(envelope) != document["envelope_hash"]:
        raise CheckpointCorrupt("identity envelope hash does not cover its own bytes")
    return envelope


# --------------------------------------------------------------------------
# One-writer execution lock (spec 11.1, 11.4 step 1)
# --------------------------------------------------------------------------


class ExecutionLock:
    """Exclusive, non-blocking file lock over one output root.

    The loser of the race performs no write at all: the lock file is opened
    ``O_RDWR|O_CREAT`` (never truncating), so a failed acquisition leaves both
    the lock file's bytes and its mtime untouched.
    """

    def __init__(self, output_root: Path | str) -> None:
        self._output_root = Path(output_root)
        self._path = _guarded(self._output_root, EXECUTION_LOCK_RELATIVE)
        self._fd: int | None = None

    @property
    def path(self) -> Path:
        return self._path

    def is_held(self) -> bool:
        return self._fd is not None

    def acquire(self) -> "ExecutionLock":
        if self._fd is not None:
            raise PersistenceError("execution lock already held by this object")
        fd = os.open(self._path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(fd)
            raise ExecutionLockUnavailable(
                f"another process holds {self._path}; concurrent processes are out of scope"
            ) from exc
        self._fd = fd
        holder = canonical_json_bytes({"pid": os.getpid(), "acquired_at_ns": time.time_ns()})
        os.ftruncate(fd, 0)
        os.lseek(fd, 0, os.SEEK_SET)
        os.write(fd, holder + b"\n")
        os.fsync(fd)
        return self

    def release(self) -> None:
        if self._fd is None:
            return
        try:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
        finally:
            os.close(self._fd)
            self._fd = None

    def __enter__(self) -> "ExecutionLock":
        return self.acquire()

    def __exit__(self, *_exc: object) -> None:
        self.release()


# --------------------------------------------------------------------------
# Graceful interruption token (spec 11.3)
# --------------------------------------------------------------------------


class InterruptToken:
    """Process-safe SIGINT/SIGTERM token that gates new external transmission.

    The handler only assigns a bool and issues one `os.write` to a file
    descriptor opened up front, both of which are safe to do from signal
    context; the durable marker lets a later episode see that the previous one
    was asked to stop.
    """

    def __init__(self, output_root: Path | str | None = None) -> None:
        self._set = False
        self._reason: str | None = None
        self._marker_fd: int | None = None
        self._marker_path: Path | None = None
        self._previous: dict[int, Any] = {}
        if output_root is not None:
            self._marker_path = _guarded(output_root, INTERRUPT_TOKEN_RELATIVE)
            self._marker_fd = os.open(self._marker_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)

    @property
    def marker_path(self) -> Path | None:
        return self._marker_path

    def is_set(self) -> bool:
        return self._set

    @property
    def reason(self) -> str | None:
        return self._reason

    def set(self, reason: str = "requested") -> None:
        self._set = True
        self._reason = reason
        if self._marker_fd is not None:
            os.write(self._marker_fd, b"INTERRUPTED\n")

    def _handler(self, signum: int, _frame: Any) -> None:
        self._set = True
        self._reason = signal.Signals(signum).name
        if self._marker_fd is not None:
            os.write(self._marker_fd, b"INTERRUPTED\n")

    def install(self, signals: Sequence[int] = (signal.SIGINT, signal.SIGTERM)) -> "InterruptToken":
        for signum in signals:
            self._previous[signum] = signal.getsignal(signum)
            signal.signal(signum, self._handler)
        return self

    def restore(self) -> None:
        for signum, previous in self._previous.items():
            signal.signal(signum, previous)
        self._previous.clear()

    def guard_transmission(self, description: str) -> None:
        """Refuse to start a *new* external transmission once the token is set."""
        if self._set:
            raise InterruptionRequested(
                f"interrupt token set ({self._reason}); refusing new transmission: {description}"
            )

    def close(self) -> None:
        self.restore()
        if self._marker_fd is not None:
            os.close(self._marker_fd)
            self._marker_fd = None


# --------------------------------------------------------------------------
# SqliteSaver configuration (spec 11.1)
# --------------------------------------------------------------------------


def open_checkpoint_connection(output_root: Path | str) -> sqlite3.Connection:
    """Open the one checkpoint connection with the spec's durability pragmas."""
    _mkdir_langgraph(output_root)
    path = _guarded(output_root, CHECKPOINT_DB_RELATIVE)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute(f"PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}")
    conn.commit()
    return conn


def read_connection_pragmas(conn: sqlite3.Connection) -> dict[str, Any]:
    observed: dict[str, Any] = {}
    for name in REQUIRED_PRAGMAS:
        row = conn.execute(f"PRAGMA {name}").fetchone()
        value = row[0] if row else None
        observed[name] = value.lower() if isinstance(value, str) else value
    return observed


def verify_connection_pragmas(conn: sqlite3.Connection) -> dict[str, Any]:
    observed = read_connection_pragmas(conn)
    for name, expected in REQUIRED_PRAGMAS.items():
        if observed[name] != expected:
            raise CheckpointCorrupt(
                f"checkpoint connection pragma {name} is {observed[name]!r}, required {expected!r}"
            )
    return observed


def open_checkpoint_saver(output_root: Path | str) -> tuple[Any, sqlite3.Connection]:
    """Build the synchronous `SqliteSaver` exactly as spec section 3.3 selects it."""
    os.environ[STRICT_MSGPACK_ENV] = "true"
    from langgraph.checkpoint.sqlite import SqliteSaver  # lazy: locked env only

    conn = open_checkpoint_connection(output_root)
    saver = SqliteSaver(conn)
    saver.setup()
    # SqliteSaver.setup() may relax journal/synchronous; reassert then prove.
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute(f"PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}")
    conn.commit()
    verify_connection_pragmas(conn)
    return saver, conn


def flush_checkpoint_durability(conn: sqlite3.Connection, output_root: Path | str) -> dict[str, Any]:
    """Flush the SQLite file and WAL before a receipt or terminal may pass."""
    conn.commit()
    row = conn.execute("PRAGMA wal_checkpoint(FULL)").fetchone()
    db_path = checkpoint_db_path(output_root)
    for candidate in (db_path, Path(f"{db_path}-wal")):
        if candidate.is_file():
            fd = os.open(candidate, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    directory = langgraph_dir(output_root)
    dir_fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)
    return {"wal_checkpoint": list(row) if row else None, "db_sha256": file_digest(db_path)}


def verify_checkpoint_integrity(output_root: Path | str) -> dict[str, Any]:
    """Read-only SQLite integrity proof. Never repairs; raises on any damage."""
    path = checkpoint_db_path(output_root)
    if not path.is_file():
        raise CheckpointCorrupt(f"checkpoint database is missing at {path}")
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
        rows = conn.execute("PRAGMA integrity_check").fetchall()
        results = [row[0] for row in rows]
        if results != ["ok"]:
            raise CheckpointCorrupt(f"sqlite integrity_check failed: {results[:5]}")
        # A structurally valid file that is not a LangGraph checkpoint store is
        # equally unusable, so prove the saver's own table is present.
        names = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        if "checkpoints" not in names:
            raise CheckpointCorrupt(f"checkpoint database has no checkpoints table: {sorted(names)}")
    except sqlite3.DatabaseError as exc:
        raise CheckpointCorrupt(f"sqlite refused the checkpoint database: {exc}") from exc
    finally:
        if conn is not None:
            conn.close()
    return {"integrity_check": "ok", "db_sha256": file_digest(path)}


def verify_persistence_integrity(
    output_root: Path | str, evidence_store: Any | None = None
) -> dict[str, Any]:
    """Both persistence layers must verify independently; neither is repaired.

    Spec 11.2 keeps the checkpoint store and the append-only ledgers separate,
    so a failure in either one alone must block recovery.
    """
    report: dict[str, Any] = {"checkpoint": verify_checkpoint_integrity(output_root)}
    for name, ledger in (
        ("episode_ledger", EpisodeLeaseLedger(output_root)),
        ("admission_ledger", AdmissionLedger(output_root)),
    ):
        audit = ledger.audit()
        if audit["status"] != "PASS":
            raise CheckpointCorrupt(f"{name} failed integrity audit: {audit['reason']}")
        report[name] = audit
    if evidence_store is not None:
        audits = evidence_store.audit_all()
        failed = sorted(name for name, result in audits.items() if not result.passed)
        if failed:
            raise CheckpointCorrupt(f"append-only evidence logs failed integrity audit: {failed}")
        report["evidence"] = {name: result.as_dict() for name, result in sorted(audits.items())}
    return report


# --------------------------------------------------------------------------
# Read-only checkpoint extraction (spec 11.1, 11.3, 11.4 step 2)
# --------------------------------------------------------------------------


class ReadOnlyCheckpointView:
    """Read-only façade over a compiled graph and its saver.

    Deliberately exposes only `get_state`, `get_state_history`, `get_tuple`, and
    `list`. There is no attribute through which a prior thread could be
    continued, which is what makes "never resume the old thread" structural
    rather than a rule someone has to remember.
    """

    __slots__ = ("_read_state", "_read_history", "_read_tuple", "_read_list")

    def __init__(self, graph: Any, saver: Any) -> None:
        self._read_state = graph.get_state
        self._read_history = graph.get_state_history
        self._read_tuple = saver.get_tuple
        self._read_list = saver.list

    def get_state(self, config: Mapping[str, Any]) -> Any:
        return self._read_state(config)

    def get_state_history(self, config: Mapping[str, Any]) -> list[Any]:
        return list(self._read_history(config))

    def get_tuple(self, config: Mapping[str, Any]) -> Any:
        return self._read_tuple(config)

    def list(self, config: Mapping[str, Any]) -> list[Any]:
        return list(self._read_list(config))


@dataclasses.dataclass(frozen=True)
class PriorEpisodeReadout:
    """Everything a resume may learn about a prior episode, and nothing more."""

    thread_id: str
    checkpoint_id: str | None
    parent_checkpoint_id: str | None
    values: dict[str, Any]
    next: tuple[str, ...]
    tasks: tuple[dict[str, Any], ...]
    pending_writes: tuple[dict[str, Any], ...]
    state_digest: str
    history_length: int
    terminal: dict[str, Any] | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": RESUME_READOUT_SCHEMA,
            "thread_id": self.thread_id,
            "checkpoint_id": self.checkpoint_id,
            "parent_checkpoint_id": self.parent_checkpoint_id,
            "checkpoint_ns": CHECKPOINT_NS,
            "next": list(self.next),
            "tasks": [dict(task) for task in self.tasks],
            "pending_writes": [dict(write) for write in self.pending_writes],
            "state_digest": self.state_digest,
            "history_length": self.history_length,
            "terminal": self.terminal,
        }


def _pending_write_records(checkpoint_tuple: Any) -> tuple[dict[str, Any], ...]:
    raw = getattr(checkpoint_tuple, "pending_writes", None) or ()
    records: list[dict[str, Any]] = []
    for entry in raw:
        task_id, channel, value = entry[0], entry[1], entry[2]
        records.append(
            {
                "task_id": str(task_id),
                "channel": str(channel),
                "value_digest": state_digest(value),
            }
        )
    records.sort(key=lambda item: (item["task_id"], item["channel"], item["value_digest"]))
    return tuple(records)


def _task_records(snapshot: Any) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    for task in getattr(snapshot, "tasks", ()) or ():
        records.append(
            {
                "id": str(getattr(task, "id", "")),
                "name": str(getattr(task, "name", "")),
                "error": None if getattr(task, "error", None) is None else str(task.error),
                "interrupts": len(getattr(task, "interrupts", ()) or ()),
            }
        )
    records.sort(key=lambda item: (item["name"], item["id"]))
    return tuple(records)


def extract_prior_episode(view: ReadOnlyCheckpointView, thread_id: str) -> PriorEpisodeReadout:
    """Read a prior thread with read-only APIs only; never continues it."""
    if hasattr(view, "invoke") or hasattr(view, "stream"):  # pragma: no cover - defensive
        raise PersistenceError("checkpoint view must not expose an execution method")
    config = invoke_config(thread_id)
    snapshot = view.get_state(config)
    checkpoint_tuple = view.get_tuple(config)
    if snapshot is None or checkpoint_tuple is None:
        raise ResumeRefused("checkpoint", "prior_thread", thread_id, "no checkpoint found")
    configurable = dict(snapshot.config.get("configurable", {}))
    parent = getattr(checkpoint_tuple, "parent_config", None) or {}
    values = dict(_json_safe(snapshot.values))
    return PriorEpisodeReadout(
        thread_id=thread_id,
        checkpoint_id=configurable.get("checkpoint_id"),
        parent_checkpoint_id=dict(parent.get("configurable", {})).get("checkpoint_id"),
        values=values,
        next=tuple(str(item) for item in (snapshot.next or ())),
        tasks=_task_records(snapshot),
        pending_writes=_pending_write_records(checkpoint_tuple),
        state_digest=state_digest(values),
        history_length=len(view.get_state_history(config)),
        terminal=values.get("terminal"),
    )


# --------------------------------------------------------------------------
# Append-only, hash-chained ledgers under .langgraph/
# --------------------------------------------------------------------------


class _ChainedLedger:
    """Shared append-only JSONL chain with compare-and-swap ordinals."""

    schema = "plan26.chained.v1"

    def __init__(self, output_root: Path | str, relative: str) -> None:
        self._output_root = Path(output_root)
        self._path = _guarded(self._output_root, relative)

    @property
    def path(self) -> Path:
        return self._path

    def records(self) -> list[dict[str, Any]]:
        if not self._path.is_file():
            return []
        raw = self._path.read_bytes()
        if not raw:
            return []
        lines = raw.split(b"\n")
        if lines[-1] != b"":
            raise CheckpointCorrupt(f"{self._path.name}: final record is not newline terminated")
        lines.pop()
        prev_hash = GENESIS_HASH
        out: list[dict[str, Any]] = []
        for index, line in enumerate(lines, start=1):
            try:
                obj = json.loads(line.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise CheckpointCorrupt(f"{self._path.name}: record {index} is not JSON: {exc}") from exc
            body = {k: v for k, v in obj.items() if k != "record_hash"}
            if canonical_digest(body) != obj.get("record_hash"):
                raise CheckpointCorrupt(f"{self._path.name}: record {index} hash does not cover its bytes")
            if obj.get("ordinal") != index:
                raise CheckpointCorrupt(f"{self._path.name}: ordinal {obj.get('ordinal')} != {index}")
            if obj.get("prev_hash") != prev_hash:
                raise CheckpointCorrupt(f"{self._path.name}: broken chain at record {index}")
            prev_hash = obj["record_hash"]
            out.append(obj)
        return out

    def audit(self) -> dict[str, Any]:
        try:
            records = self.records()
        except CheckpointCorrupt as exc:
            return {"status": "FAIL", "reason": str(exc), "record_count": None}
        return {"status": "PASS", "reason": None, "record_count": len(records)}

    def _append(self, payload: Mapping[str, Any], *, expected_ordinal: int | None = None) -> dict[str, Any]:
        with open(self._path, "a+b") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                existing = self.records()
                ordinal = len(existing) + 1
                if expected_ordinal is not None and expected_ordinal != ordinal:
                    raise EpisodeLedgerError(
                        f"compare-and-swap failed: expected ordinal {expected_ordinal}, ledger is at {ordinal}"
                    )
                prev_hash = existing[-1]["record_hash"] if existing else GENESIS_HASH
                body = {
                    "schema": self.schema,
                    "ordinal": ordinal,
                    "prev_hash": prev_hash,
                    "payload": _json_safe(dict(payload)),
                }
                record = {**body, "record_hash": canonical_digest(body)}
                handle.seek(0, os.SEEK_END)
                handle.write(canonical_json_bytes(record) + b"\n")
                handle.flush()
                os.fsync(handle.fileno())
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return record


class EpisodeLeaseLedger(_ChainedLedger):
    """Append-only episode lease ledger; an unclosed lease is an orphan."""

    schema = EPISODE_RECORD_SCHEMA

    def __init__(self, output_root: Path | str) -> None:
        super().__init__(output_root, EPISODE_LEDGER_RELATIVE)

    def leases(self) -> list[dict[str, Any]]:
        state: dict[int, dict[str, Any]] = {}
        order: list[int] = []
        for record in self.records():
            payload = record["payload"]
            ordinal = int(payload["episode_ordinal"])
            if payload["state"] == "OPEN":
                if ordinal in state:
                    raise EpisodeLedgerError(f"episode ordinal {ordinal} opened twice")
                state[ordinal] = {**payload, "closed": False, "terminal": None}
                order.append(ordinal)
            else:
                if ordinal not in state:
                    raise EpisodeLedgerError(f"episode ordinal {ordinal} closed without an open lease")
                state[ordinal].update(
                    {"closed": True, "terminal": payload.get("terminal"), "closed_at": payload.get("at")}
                )
        return [state[ordinal] for ordinal in order]

    def next_episode_ordinal(self) -> int:
        return len(self.leases()) + 1

    def open_leases(self) -> list[dict[str, Any]]:
        return [lease for lease in self.leases() if not lease["closed"]]

    def open_lease(self) -> dict[str, Any] | None:
        """The episode a next invocation must deal with before anything else.

        A recovery lease is opened *while* its orphan is still open, so the
        orphan (the earliest non-recovery open lease) is what a resume must
        close; only if recovery itself died unclean is a recovery lease
        returned.
        """
        opens = self.open_leases()
        if not opens:
            return None
        product = [
            lease for lease in opens if lease["bootstrap_kind"] != BOOTSTRAP_RECOVER_ORPHAN
        ]
        return (product or opens)[0]

    def last_lease(self) -> dict[str, Any] | None:
        leases = self.leases()
        return leases[-1] if leases else None

    def open_episode(
        self, *, run_id: str, episode_ordinal: int, thread_id: str, bootstrap_kind: str
    ) -> dict[str, Any]:
        opens = self.open_leases()
        if bootstrap_kind == BOOTSTRAP_RECOVER_ORPHAN:
            if any(lease["bootstrap_kind"] == BOOTSTRAP_RECOVER_ORPHAN for lease in opens):
                raise EpisodeLedgerError("a recovery episode is already open")
            if not opens:
                raise EpisodeLedgerError("no orphaned episode to recover")
        elif opens:
            raise EpisodeLedgerError("an episode lease is still open; close or recover it first")
        expected = self.next_episode_ordinal()
        if episode_ordinal != expected:
            raise EpisodeLedgerError(
                f"episode ordinal {episode_ordinal} is not the next ordinal {expected}"
            )
        return self._append(
            {
                "state": "OPEN",
                "run_id": run_id,
                "episode_ordinal": episode_ordinal,
                "thread_id": thread_id,
                "bootstrap_kind": bootstrap_kind,
                "at": time.time_ns(),
            }
        )

    def close_episode(self, *, episode_ordinal: int, terminal: Mapping[str, Any]) -> dict[str, Any]:
        matching = [
            lease
            for lease in self.open_leases()
            if int(lease["episode_ordinal"]) == int(episode_ordinal)
        ]
        if not matching:
            raise EpisodeLedgerError(f"no open lease for episode ordinal {episode_ordinal}")
        lease = matching[0]
        return self._append(
            {
                "state": "CLOSED",
                "run_id": lease["run_id"],
                "episode_ordinal": episode_ordinal,
                "thread_id": lease["thread_id"],
                "terminal": _json_safe(dict(terminal)),
                "at": time.time_ns(),
            }
        )


class AdmissionLedger(_ChainedLedger):
    """Idempotent admission of committed work, keyed by activation key.

    Spec section 10: an equal replay is idempotent, a *different* replay under
    the same key is an integrity failure. This is what makes a crash between a
    committed side effect and its checkpoint non-duplicating on retry.
    """

    schema = ADMISSION_RECORD_SCHEMA

    def __init__(self, output_root: Path | str) -> None:
        super().__init__(output_root, ADMISSION_LEDGER_RELATIVE)

    def committed(self) -> dict[str, str]:
        return {
            record["payload"]["key"]: record["payload"]["output_hash"]
            for record in self.records()
        }

    def admit(self, key: str, output: Any) -> tuple[bool, str]:
        """Return ``(was_new, output_hash)``; raise on a differing duplicate."""
        if not isinstance(key, str) or not key:
            raise PersistenceError("admission key must be a non-empty string")
        output_hash = state_digest(output)
        with open(self._path, "a+b") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                existing = self.records()
                for record in existing:
                    if record["payload"]["key"] == key:
                        if record["payload"]["output_hash"] != output_hash:
                            raise AdmissionConflict(
                                f"admission key {key!r} already committed with a different output hash"
                            )
                        return False, output_hash
                ordinal = len(existing) + 1
                prev_hash = existing[-1]["record_hash"] if existing else GENESIS_HASH
                body = {
                    "schema": self.schema,
                    "ordinal": ordinal,
                    "prev_hash": prev_hash,
                    "payload": {"key": key, "output_hash": output_hash, "at": time.time_ns()},
                }
                record = {**body, "record_hash": canonical_digest(body)}
                handle.seek(0, os.SEEK_END)
                handle.write(canonical_json_bytes(record) + b"\n")
                handle.flush()
                os.fsync(handle.fileno())
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return True, output_hash


# --------------------------------------------------------------------------
# Resume admissibility (spec 11.4 steps 4-5)
# --------------------------------------------------------------------------


_DRIFT_FIELD_CLASSES: dict[str, str] = {
    "contract_version": "identity",
    "run_id": "identity",
    "created_at": "identity",
    "engine_root": "identity",
    "curriculum_root": "identity",
    "active_manifest_path": "identity",
    "output_root": "identity",
    "mode": "identity",
    "requested_unit_id": "identity",
    "frozen_digest": "frozen_digest",
    "frozen_inputs": "frozen_digest",
    "frozen_executable_identities": "executable",
    "evidence_chain_hashes": "evidence",
    "accepted_receipt_hashes": "accepted_bytes",
    "accepted_byte_digests": "accepted_bytes",
}


def validate_resume_inputs(
    *, expected: Mapping[str, Any], observed: Mapping[str, Any]
) -> None:
    """Refuse resume on any identity/digest/executable/evidence/accepted drift.

    ``expected`` is the immutable identity envelope merged with whatever the
    prior episode durably recorded (append-log chain hashes, accepted receipt
    and accepted-byte digests); ``observed`` is the freshly recomputed value of
    the same keys. An unclassified key is itself a refusal, because a difference
    nobody has assigned a drift class to cannot be judged safe.
    """
    for field in sorted(observed):
        drift_class = _DRIFT_FIELD_CLASSES.get(field)
        if drift_class is None:
            raise ResumeRefused("identity", field, "a classified resume input", "unknown field")
        if field not in expected:
            raise ResumeRefused(drift_class, field, "present in the resume baseline", "absent")
        if canonical_digest(_json_safe(expected[field])) != canonical_digest(
            _json_safe(observed[field])
        ):
            raise ResumeRefused(drift_class, field, expected[field], observed[field])


def _validate_terminal_legality(terminal: Mapping[str, Any] | None) -> str:
    if not terminal:
        raise ResumeRefused("terminal_legality", "terminal", "a recorded episode terminal", None)
    name = terminal.get("terminal") or terminal.get("kind") or terminal.get("name")
    if name in NON_RESUMABLE_TERMINALS:
        raise ResumeRefused(
            "terminal_legality", "terminal", sorted(RESUMABLE_TERMINALS), name
        )
    if name not in RESUMABLE_TERMINALS:
        raise ResumeRefused("terminal_legality", "terminal", sorted(RESUMABLE_TERMINALS), name)
    return str(name)


# --------------------------------------------------------------------------
# Deterministic resume frontier (spec 11.3, 11.4 steps 7-8)
# --------------------------------------------------------------------------


def classify_join_members(
    *, expected_keys: Iterable[str], completed_keys: Iterable[str]
) -> dict[str, Any]:
    """Split a denominator into completed/pending; a join is satisfied only when equal.

    Pending writes from a surviving sibling never shrink the denominator, so a
    fan-out with one crashed member cannot be joined as a partial result.
    """
    expected = sorted({str(key) for key in expected_keys})
    completed = sorted({str(key) for key in completed_keys})
    extra = sorted(set(completed) - set(expected))
    if extra:
        raise PersistenceError(f"completed members outside the denominator: {extra}")
    pending = sorted(set(expected) - set(completed))
    return {
        "expected": expected,
        "completed": completed,
        "pending": pending,
        "satisfied": not pending and bool(expected),
    }


def compute_resume_frontier(
    *,
    readout: PriorEpisodeReadout,
    denominators: Mapping[str, Mapping[str, Iterable[str]]] | None = None,
    evidence_high_water: Mapping[str, int] | None = None,
    reason: str = "resume",
) -> dict[str, Any]:
    """Deterministic, model-free frontier for the next episode.

    Any model destination is rewritten to `D91`: spec 11.3 forbids storing a
    model node as a resume destination, because an aborted model receipt must be
    classified before D90 can authorize another transmission.
    """
    destinations: list[str] = []
    reclassified: list[dict[str, str]] = []
    incomplete_task_names = sorted(
        {task["name"] for task in readout.tasks if task["name"]}
    )
    candidates = sorted(set(readout.next) | set(incomplete_task_names))
    for candidate in candidates:
        if candidate in MODEL_NODE_IDS:
            reclassified.append({"from": candidate, "to": MODEL_CLASSIFICATION_ENTRY})
            destinations.append(MODEL_CLASSIFICATION_ENTRY)
        else:
            destinations.append(candidate)
    destinations = sorted(set(destinations))
    reclassified.sort(key=lambda item: (item["from"], item["to"]))

    joins: dict[str, Any] = {}
    for join_name, spec in sorted((denominators or {}).items()):
        joins[join_name] = classify_join_members(
            expected_keys=spec.get("expected", ()),
            completed_keys=spec.get("completed", ()),
        )

    frontier = {
        "schema": RESUME_FRONTIER_SCHEMA,
        "reason": reason,
        "prior_thread_id": readout.thread_id,
        "prior_checkpoint_id": readout.checkpoint_id,
        "checkpoint_ns": CHECKPOINT_NS,
        "destinations": destinations,
        "reclassified_model_destinations": reclassified,
        "pending_writes": [dict(write) for write in readout.pending_writes],
        "joins": joins,
        "state_digest": readout.state_digest,
        "evidence_high_water": dict(sorted((evidence_high_water or {}).items())),
    }
    frontier["frontier_digest"] = canonical_digest(frontier)
    return frontier


def build_interrupt_terminal_candidate(
    *,
    run_id: str,
    episode_id: str,
    frontier: Mapping[str, Any],
    classification: str,
    heads: Mapping[str, str],
    high_water_marks: Mapping[str, Any],
) -> dict[str, Any]:
    """Exactly one `INTERRUPTED` terminal candidate for the episode D98 closes.

    D98 re-derives this terminal's precondition from state and rejects anything
    it cannot confirm, so `heads` must be the artifact heads current at the
    interrupt — they are passed in by the caller that holds live state rather
    than recomputed here, which cannot see it.
    """
    if classification not in INTERRUPT_CLASSIFICATIONS:
        raise PersistenceError(
            f"interrupt classification must be one of "
            f"{sorted(INTERRUPT_CLASSIFICATIONS)}, got {classification!r}"
        )
    candidate = {
        "kind": "INTERRUPTED",
        "classification": classification,
        "run_id": run_id,
        "episode_id": episode_id,
        "resume_frontier": dict(frontier),
        "resume_frontier_digest": frontier["frontier_digest"],
        "destinations": list(frontier["destinations"]),
        "heads": dict(heads),
        "high_water_marks": dict(high_water_marks),
    }
    candidate["candidate_digest"] = canonical_digest(candidate)
    return candidate


def record_checkpoint_correlation(
    evidence_store: Any,
    *,
    run_id: str,
    episode_id: str,
    node_id: str,
    activation_id: str,
    readout: PriorEpisodeReadout,
) -> Any:
    """Correlate one superstep's checkpoint with the append-only evidence layer."""
    marks = {
        name: value
        for name, value in evidence_store.high_water_marks().items()
        if name != "checkpoints"
    }
    return evidence_store.append(
        "checkpoints",
        {
            "run_id": run_id,
            "episode_id": episode_id,
            "node_id": node_id,
            "activation_id": activation_id,
            "checkpoint_id": readout.checkpoint_id or "",
            "parent_checkpoint_id": readout.parent_checkpoint_id,
            "checkpoint_ns": CHECKPOINT_NS,
            "thread_id": readout.thread_id,
            "state_digest": readout.state_digest,
            "next": list(readout.next),
            "tasks": [dict(task) for task in readout.tasks],
            "pending_writes": [dict(write) for write in readout.pending_writes],
            "evidence_ordinal": max(marks.values()) if marks else 0,
            "evidence_high_water": dict(sorted(marks.items())),
        },
    )


# --------------------------------------------------------------------------
# Orphan-recovery services (spec 11.3)
# --------------------------------------------------------------------------


class ForbiddenService:
    """A service a recovery episode must never reach; every touch raises."""

    __slots__ = ("_name",)

    def __init__(self, name: str) -> None:
        object.__setattr__(self, "_name", name)

    def __getattr__(self, item: str) -> Any:
        raise RecoveryServiceForbidden(
            f"orphan recovery may not use {object.__getattribute__(self, '_name')}.{item}"
        )

    def __call__(self, *_args: Any, **_kwargs: Any) -> Any:
        raise RecoveryServiceForbidden(
            f"orphan recovery may not call {object.__getattribute__(self, '_name')}"
        )

    def __repr__(self) -> str:
        return f"<forbidden {object.__getattribute__(self, '_name')}>"


def build_recovery_services() -> dict[str, ForbiddenService]:
    """The product services a `RECOVER_ORPHAN` runtime context must not hold."""
    return {
        "transport_registry": ForbiddenService("transport_registry"),
        "source_retriever": ForbiddenService("source_retriever"),
        "renderer": ForbiddenService("renderer"),
    }


# --------------------------------------------------------------------------
# The one pre-invocation helper (spec section 4, 11.1, 11.4)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class EpisodeInvocation:
    """Typed result of `prepare_episode_invocation()`, consumed first by D00."""

    bootstrap_kind: str
    run_id: str
    episode_id: str
    episode_ordinal: int
    thread_id: str
    checkpoint_ns: str
    config: dict[str, dict[str, str]]
    checkpoint_db_path: str
    identity_envelope: dict[str, Any]
    prior_thread_id: str | None
    prior_episode_ordinal: int | None
    resume_from: dict[str, Any] | None
    lease_record_hash: str

    def as_state_update(self) -> dict[str, Any]:
        """The episode fields D00 writes into `FactoryState` verbatim."""
        return {
            "bootstrap_kind": self.bootstrap_kind,
            "run_id": self.run_id,
            "episode_id": self.episode_id,
            "checkpoint_thread_id": self.thread_id,
            "checkpoint_namespace": self.checkpoint_ns,
            "resume_from": self.resume_from,
        }


def prepare_episode_invocation(
    *,
    output_root: Path | str,
    lock: ExecutionLock,
    identity_seed: Mapping[str, Any] | None = None,
    resume: bool = False,
    resume_baseline: Mapping[str, Any] | None = None,
    recomputed: Mapping[str, Any] | None = None,
    read_view: ReadOnlyCheckpointView | None = None,
) -> EpisodeInvocation:
    """Choose the next episode thread. Reads only; runs no product work.

    Fresh runs derive the canonical ``run_id`` from ``identity_seed`` and write
    the immutable identity envelope. Resumes read ``run_id`` back out of that
    envelope, refuse on any classified drift, and extract the prior episode
    through `ReadOnlyCheckpointView` alone. An unclosed prior lease means the
    process died before D98, so a `RECOVER_ORPHAN` thread is prepared against a
    *new* thread id — the orphan itself is never continued.
    """
    if not isinstance(lock, ExecutionLock) or not lock.is_held():
        raise PersistenceError(
            "prepare_episode_invocation requires the exclusive output lock to be held"
        )
    output_root = Path(output_root)
    _mkdir_langgraph(output_root)
    ledger = EpisodeLeaseLedger(output_root)
    envelope = read_identity_envelope(output_root)

    if not resume:
        if envelope is not None:
            raise ResumeRefused(
                "identity", "bootstrap_kind", "no prior identity envelope", "prior run present"
            )
        if identity_seed is None:
            raise PersistenceError("a fresh invocation requires an identity seed")
        run_id = compute_fresh_run_id(identity_seed)
        envelope = {**_json_safe(dict(identity_seed)), "run_id": run_id}
        write_identity_envelope(output_root, envelope)
        envelope = read_identity_envelope(output_root)
        ordinal = ledger.next_episode_ordinal()
        if ordinal != 1:
            raise EpisodeLedgerError("a fresh run cannot start at a non-first episode ordinal")
        thread_id = episode_thread_id(run_id, ordinal)
        record = ledger.open_episode(
            run_id=run_id,
            episode_ordinal=ordinal,
            thread_id=thread_id,
            bootstrap_kind=BOOTSTRAP_FRESH,
        )
        return EpisodeInvocation(
            bootstrap_kind=BOOTSTRAP_FRESH,
            run_id=run_id,
            episode_id=thread_id,
            episode_ordinal=ordinal,
            thread_id=thread_id,
            checkpoint_ns=CHECKPOINT_NS,
            config=invoke_config(thread_id),
            checkpoint_db_path=str(checkpoint_db_path(output_root)),
            identity_envelope=dict(envelope or {}),
            prior_thread_id=None,
            prior_episode_ordinal=None,
            resume_from=None,
            lease_record_hash=record["record_hash"],
        )

    if envelope is None:
        raise ResumeRefused("identity", "identity_envelope", "an immutable identity envelope", None)
    run_id = envelope.get("run_id")
    if not run_id:
        raise ResumeRefused("identity", "run_id", "a recorded run_id", None)
    if identity_seed is not None and compute_fresh_run_id(identity_seed) != run_id:
        raise ResumeRefused("identity", "run_id", run_id, compute_fresh_run_id(identity_seed))
    validate_resume_inputs(
        expected={**envelope, **dict(resume_baseline or {})}, observed=recomputed or {}
    )
    verify_persistence_integrity(output_root)

    orphan = ledger.open_lease()
    if orphan is not None:
        orphan_ordinal = int(orphan["episode_ordinal"])
        thread_id = recovery_thread_id(run_id, orphan_ordinal)
        readout = (
            extract_prior_episode(read_view, str(orphan["thread_id"]))
            if read_view is not None
            else None
        )
        ordinal = ledger.next_episode_ordinal()
        record = ledger.open_episode(
            run_id=run_id,
            episode_ordinal=ordinal,
            thread_id=thread_id,
            bootstrap_kind=BOOTSTRAP_RECOVER_ORPHAN,
        )
        return EpisodeInvocation(
            bootstrap_kind=BOOTSTRAP_RECOVER_ORPHAN,
            run_id=run_id,
            episode_id=thread_id,
            episode_ordinal=ordinal,
            thread_id=thread_id,
            checkpoint_ns=CHECKPOINT_NS,
            config=invoke_config(thread_id),
            checkpoint_db_path=str(checkpoint_db_path(output_root)),
            identity_envelope=dict(envelope),
            prior_thread_id=str(orphan["thread_id"]),
            prior_episode_ordinal=orphan_ordinal,
            resume_from=readout.as_dict() if readout is not None else None,
            lease_record_hash=record["record_hash"],
        )

    last = ledger.last_lease()
    if last is None:
        raise ResumeRefused("terminal_legality", "episode_ledger", "a prior episode", None)
    _validate_terminal_legality(last.get("terminal"))
    if read_view is None:
        raise PersistenceError("a resume requires a read-only checkpoint view")
    readout = extract_prior_episode(read_view, str(last["thread_id"]))
    ordinal = ledger.next_episode_ordinal()
    thread_id = episode_thread_id(run_id, ordinal)
    record = ledger.open_episode(
        run_id=run_id,
        episode_ordinal=ordinal,
        thread_id=thread_id,
        bootstrap_kind=BOOTSTRAP_RESUME,
    )
    return EpisodeInvocation(
        bootstrap_kind=BOOTSTRAP_RESUME,
        run_id=run_id,
        episode_id=thread_id,
        episode_ordinal=ordinal,
        thread_id=thread_id,
        checkpoint_ns=CHECKPOINT_NS,
        config=invoke_config(thread_id),
        checkpoint_db_path=str(checkpoint_db_path(output_root)),
        identity_envelope=dict(envelope),
        prior_thread_id=str(last["thread_id"]),
        prior_episode_ordinal=int(last["episode_ordinal"]),
        resume_from=readout.as_dict(),
        lease_record_hash=record["record_hash"],
    )


def open_episode_session(
    output_root: Path | str,
) -> tuple[Any, sqlite3.Connection, Callable[[], None]]:
    """Open the saver plus a closer, for callers that do not want the tuple dance."""
    saver, conn = open_checkpoint_saver(output_root)
    return saver, conn, conn.close
