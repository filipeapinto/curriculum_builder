"""Immutable, content-addressed artifact store for the Plan 26 output root.

Filesystem source of truth for spec section 15: canonical containment,
staging plus atomic admission, version/parent chains, head pointers, and
write-protected accepted bytes. Independent of LangGraph checkpoints.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

STAGING_DIRNAME = ".staging"
QUARANTINE_DIRNAME = ".staging_orphans"
UNIT_SCOPE = "units"
WORKBOOK_SCOPE = "workbook"
UNIT_CHANNELS = ("domain", "content", "visuals", "layout")
WORKBOOK_CHANNELS = ("workbook",)
ACCEPTED_SEGMENT = "accepted"
VERSION_RECORD_SCHEMA = "plan26.artifact_version.v1"

_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")

_ACCEPTED_FILE_MODE = 0o444
_ACCEPTED_DIR_MODE = 0o555


class ArtifactError(Exception):
    pass


class PathEscape(ArtifactError):
    pass


class AcceptedImmutable(ArtifactError):
    pass


class ArtifactConflict(ArtifactError):
    pass


class HeadAdvanceError(ArtifactError):
    pass


class IntegrityError(ArtifactError):
    pass


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_digest(obj: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def bytes_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _require_token(value: str, field: str) -> str:
    if not isinstance(value, str) or not _TOKEN_RE.match(value):
        raise ArtifactError(f"invalid {field}: {value!r}")
    return value


def _require_hash(value: str, field: str) -> str:
    if not isinstance(value, str) or not _HASH_RE.match(value):
        raise ArtifactError(f"invalid {field}: {value!r}")
    return value


def resolve_within(root: Path, relative: str | PurePosixPath) -> Path:
    """Resolve ``relative`` strictly below ``root``; reject every escape."""
    root_resolved = Path(root).resolve(strict=True)
    rel = PurePosixPath(str(relative))
    if rel.is_absolute() or str(rel).startswith(("/", "\\")):
        raise PathEscape(f"absolute path rejected: {relative!r}")
    parts = rel.parts
    if not parts:
        raise PathEscape("empty relative path rejected")
    for part in parts:
        if part in ("", ".", "..") or "\x00" in part or os.sep in part:
            raise PathEscape(f"illegal path component {part!r} in {relative!r}")
    probe = root_resolved
    for part in parts:
        probe = probe / part
        if probe.is_symlink():
            raise PathEscape(f"symlink component rejected: {probe}")
    target = root_resolved.joinpath(*parts)
    realpath = Path(os.path.realpath(target))
    if realpath != target or not realpath.is_relative_to(root_resolved):
        raise PathEscape(f"path escapes root: {relative!r}")
    return target


@dataclass(frozen=True)
class ArtifactStream:
    scope: str
    channel: str
    unit_id: str | None = None

    def __post_init__(self) -> None:
        if self.scope == UNIT_SCOPE:
            if self.unit_id is None:
                raise ArtifactError("unit stream requires unit_id")
            _require_token(self.unit_id, "unit_id")
            if self.channel not in UNIT_CHANNELS:
                raise ArtifactError(f"invalid unit channel: {self.channel!r}")
        elif self.scope == WORKBOOK_SCOPE:
            if self.unit_id is not None:
                raise ArtifactError("workbook stream must not carry unit_id")
            if self.channel not in WORKBOOK_CHANNELS:
                raise ArtifactError(f"invalid workbook channel: {self.channel!r}")
        else:
            raise ArtifactError(f"invalid scope: {self.scope!r}")

    @property
    def stream_id(self) -> str:
        if self.scope == UNIT_SCOPE:
            return f"{UNIT_SCOPE}/{self.unit_id}/{self.channel}"
        return f"{WORKBOOK_SCOPE}/{self.channel}"

    @property
    def base(self) -> str:
        if self.scope == UNIT_SCOPE:
            return f"{UNIT_SCOPE}/{self.unit_id}"
        return WORKBOOK_SCOPE

    @property
    def versions_dir(self) -> str:
        return f"{self.base}/versions/{self.channel}"

    @property
    def head_path(self) -> str:
        return f"{self.base}/heads/{self.channel}.json"

    def blob_path(self, content_hash: str) -> str:
        return f"{self.versions_dir}/blobs/{_require_hash(content_hash, 'content_hash')}"

    def record_path(self, version: int) -> str:
        return f"{self.versions_dir}/records/{int(version):06d}.json"

    def key_path(self, idempotency_key: str) -> str:
        digest = hashlib.sha256(idempotency_key.encode("utf-8")).hexdigest()
        return f"{self.versions_dir}/keys/{digest}.json"

    def accepted_dir(self, receipt_hash: str) -> str:
        return f"{self.base}/{ACCEPTED_SEGMENT}/{_require_hash(receipt_hash, 'receipt_hash')}"


@dataclass(frozen=True)
class VersionRecord:
    stream_id: str
    scope: str
    unit_id: str | None
    channel: str
    version: int
    parent_hash: str | None
    content_hash: str
    byte_size: int
    artifact_path: str
    idempotency_key: str
    record_hash: str

    def body(self) -> dict[str, Any]:
        return {
            "schema": VERSION_RECORD_SCHEMA,
            "stream_id": self.stream_id,
            "scope": self.scope,
            "unit_id": self.unit_id,
            "channel": self.channel,
            "version": self.version,
            "parent_hash": self.parent_hash,
            "content_hash": self.content_hash,
            "byte_size": self.byte_size,
            "artifact_path": self.artifact_path,
            "idempotency_key": self.idempotency_key,
        }


def _record_from_body(body: Mapping[str, Any]) -> VersionRecord:
    return VersionRecord(
        stream_id=body["stream_id"],
        scope=body["scope"],
        unit_id=body["unit_id"],
        channel=body["channel"],
        version=body["version"],
        parent_hash=body["parent_hash"],
        content_hash=body["content_hash"],
        byte_size=body["byte_size"],
        artifact_path=body["artifact_path"],
        idempotency_key=body["idempotency_key"],
        record_hash=canonical_digest(dict(body)),
    )


class ArtifactStore:
    def __init__(self, root: Path) -> None:
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        self._root = root.resolve(strict=True)

    @property
    def root(self) -> Path:
        return self._root

    def resolve(self, relative: str) -> Path:
        return resolve_within(self._root, relative)

    def _assert_admissible(self, relative: str, target: Path) -> None:
        parts = PurePosixPath(relative).parts
        if ACCEPTED_SEGMENT in parts:
            index = parts.index(ACCEPTED_SEGMENT)
            receipt_parts = parts[: index + 2]
            if len(receipt_parts) == index + 2:
                receipt_dir = self._root.joinpath(*receipt_parts)
                if receipt_dir.exists():
                    raise AcceptedImmutable(
                        f"accepted receipt {'/'.join(receipt_parts)} is sealed; refusing to write {relative}"
                    )
        if target.exists():
            raise ArtifactConflict(f"refusing to overwrite existing artifact: {relative}")

    def stage(self, data: bytes) -> Path:
        """Write ``data`` to a staging file that is not yet visible at any final path."""
        staging = self._root / STAGING_DIRNAME
        staging.mkdir(parents=True, exist_ok=True)
        handle, name = tempfile.mkstemp(dir=staging, prefix="stage-", suffix=".part")
        with os.fdopen(handle, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        return Path(name)

    def commit(self, staged: Path, relative: str, *, overwrite: bool = False) -> Path:
        staged = Path(staged)
        if staged.parent.resolve() != (self._root / STAGING_DIRNAME).resolve():
            raise ArtifactError(f"staged file is not in the store staging area: {staged}")
        target = self.resolve(relative)
        if not overwrite:
            self._assert_admissible(relative, target)
        elif ACCEPTED_SEGMENT in PurePosixPath(relative).parts:
            raise AcceptedImmutable(f"accepted bytes are never overwritten: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staged, target)
        self._fsync_dir(target.parent)
        return target

    def put_bytes(self, relative: str, data: bytes, *, overwrite: bool = False) -> Path:
        target = self.resolve(relative)
        if not overwrite:
            self._assert_admissible(relative, target)
        elif ACCEPTED_SEGMENT in PurePosixPath(relative).parts:
            raise AcceptedImmutable(f"accepted bytes are never overwritten: {relative}")
        staged = self.stage(data)
        try:
            return self.commit(staged, relative, overwrite=overwrite)
        except BaseException:
            staged.unlink(missing_ok=True)
            raise

    @staticmethod
    def _fsync_dir(directory: Path) -> None:
        handle = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(handle)
        finally:
            os.close(handle)

    def recover_staging(self) -> list[dict[str, Any]]:
        """Quarantine orphaned staged bytes left by a crash before rename."""
        staging = self._root / STAGING_DIRNAME
        if not staging.is_dir():
            return []
        quarantine = self._root / QUARANTINE_DIRNAME
        recovered: list[dict[str, Any]] = []
        for orphan in sorted(staging.iterdir()):
            if not orphan.is_file() or orphan.is_symlink():
                continue
            data = orphan.read_bytes()
            digest = bytes_digest(data)
            quarantine.mkdir(parents=True, exist_ok=True)
            destination = quarantine / f"{digest}-{orphan.name}"
            os.replace(orphan, destination)
            recovered.append(
                {
                    "staged_name": orphan.name,
                    "quarantine_path": str(destination.relative_to(self._root)),
                    "content_hash": digest,
                    "byte_size": len(data),
                }
            )
        if recovered:
            self._fsync_dir(quarantine)
        return recovered

    def read_version(self, stream: ArtifactStream, version: int) -> VersionRecord | None:
        path = self.resolve(stream.record_path(version))
        if not path.is_file():
            return None
        stored = json.loads(path.read_text(encoding="utf-8"))
        record = _record_from_body(stored["record"])
        if record.record_hash != stored["record_hash"]:
            raise IntegrityError(f"version record hash mismatch at {stream.record_path(version)}")
        return record

    def latest_version(self, stream: ArtifactStream) -> VersionRecord | None:
        records_dir = self.resolve(f"{stream.versions_dir}/records")
        if not records_dir.is_dir():
            return None
        versions = sorted(int(p.stem) for p in records_dir.glob("*.json"))
        if not versions:
            return None
        return self.read_version(stream, versions[-1])

    def admit_version(
        self,
        stream: ArtifactStream,
        *,
        data: bytes,
        version: int,
        parent_hash: str | None,
        idempotency_key: str,
    ) -> VersionRecord:
        """Admit immutable artifact bytes as ``version`` of ``stream``."""
        if not isinstance(data, (bytes, bytearray)):
            raise ArtifactError("artifact data must be raw bytes")
        data = bytes(data)
        version = int(version)
        if version < 1:
            raise ArtifactError(f"version must be >= 1, got {version}")
        _require_token(idempotency_key, "idempotency_key")
        if parent_hash is not None:
            _require_hash(parent_hash, "parent_hash")

        content_hash = bytes_digest(data)
        body = {
            "schema": VERSION_RECORD_SCHEMA,
            "stream_id": stream.stream_id,
            "scope": stream.scope,
            "unit_id": stream.unit_id,
            "channel": stream.channel,
            "version": version,
            "parent_hash": parent_hash,
            "content_hash": content_hash,
            "byte_size": len(data),
            "artifact_path": stream.blob_path(content_hash),
            "idempotency_key": idempotency_key,
        }
        record = _record_from_body(body)

        key_relative = stream.key_path(idempotency_key)
        key_path = self.resolve(key_relative)
        if key_path.is_file():
            claimed = json.loads(key_path.read_text(encoding="utf-8"))
            existing = self.read_version(stream, claimed["version"])
            if existing is None:
                raise IntegrityError(f"idempotency key {idempotency_key!r} points at a missing version record")
            if existing.record_hash != record.record_hash:
                raise ArtifactConflict(
                    f"idempotency key {idempotency_key!r} already admitted a different artifact "
                    f"({existing.content_hash} != {content_hash})"
                )
            return existing

        existing_version = self.read_version(stream, version)
        if existing_version is not None:
            raise ArtifactConflict(
                f"version {version} of {stream.stream_id} already exists "
                f"({existing_version.content_hash})"
            )

        predecessor = self.read_version(stream, version - 1) if version > 1 else None
        if version == 1:
            if parent_hash is not None:
                raise ArtifactConflict("version 1 must declare parent_hash=None")
        else:
            if predecessor is None:
                raise ArtifactConflict(
                    f"version {version} of {stream.stream_id} has no admitted parent version {version - 1}"
                )
            if parent_hash != predecessor.content_hash:
                raise ArtifactConflict(
                    f"declared parent {parent_hash} does not match version {version - 1} "
                    f"content hash {predecessor.content_hash}"
                )

        blob_relative = stream.blob_path(content_hash)
        blob_path = self.resolve(blob_relative)
        if blob_path.is_file():
            if file_digest(blob_path) != content_hash:
                raise IntegrityError(f"content-addressed blob is corrupt: {blob_relative}")
        else:
            self.put_bytes(blob_relative, data)

        self.put_bytes(
            stream.record_path(version),
            canonical_json_bytes({"record": body, "record_hash": record.record_hash}),
        )
        self.put_bytes(
            key_relative,
            canonical_json_bytes(
                {
                    "idempotency_key": idempotency_key,
                    "stream_id": stream.stream_id,
                    "version": version,
                    "content_hash": content_hash,
                    "record_hash": record.record_hash,
                }
            ),
        )
        return record

    def current_head(self, stream: ArtifactStream) -> VersionRecord | None:
        path = self.resolve(stream.head_path)
        if not path.is_file():
            return None
        stored = json.loads(path.read_text(encoding="utf-8"))
        record = _record_from_body(stored["record"])
        if record.record_hash != stored["record_hash"]:
            raise IntegrityError(f"head record hash mismatch at {stream.head_path}")
        return record

    def advance_head(self, stream: ArtifactStream, record: VersionRecord) -> VersionRecord:
        """Advance the head pointer to a child of the current head only."""
        if record.stream_id != stream.stream_id:
            raise HeadAdvanceError(
                f"record belongs to {record.stream_id}, not {stream.stream_id}"
            )
        admitted = self.read_version(stream, record.version)
        if admitted is None or admitted.record_hash != record.record_hash:
            raise HeadAdvanceError(
                f"version {record.version} of {stream.stream_id} is not an admitted artifact"
            )
        current = self.current_head(stream)
        if current is None:
            if record.version != 1 or record.parent_hash is not None:
                raise HeadAdvanceError(
                    "first head must be version 1 with parent_hash=None, "
                    f"got version {record.version} parent {record.parent_hash}"
                )
        else:
            if record.version != current.version + 1:
                raise HeadAdvanceError(
                    f"head advances one version at a time: current {current.version}, "
                    f"proposed {record.version}"
                )
            if record.parent_hash != current.content_hash:
                raise HeadAdvanceError(
                    f"declared parent {record.parent_hash} is not the current head "
                    f"{current.content_hash}"
                )
        self.put_bytes(
            stream.head_path,
            canonical_json_bytes({"record": record.body(), "record_hash": record.record_hash}),
            overwrite=True,
        )
        return record

    def accept(
        self,
        stream: ArtifactStream,
        *,
        receipt_hash: str,
        files: Mapping[str, bytes],
    ) -> dict[str, str]:
        """Copy bytes into a write-protected ``accepted/<receipt_hash>/`` directory."""
        _require_hash(receipt_hash, "receipt_hash")
        if not files:
            raise ArtifactError("accept requires at least one file")
        payload = {}
        for name, data in files.items():
            if not isinstance(data, (bytes, bytearray)):
                raise ArtifactError(f"accepted file {name!r} must be raw bytes")
            payload[name] = bytes(data)

        accepted_relative = stream.accepted_dir(receipt_hash)
        accepted_dir = self.resolve(accepted_relative)
        targets = {
            name: self.resolve(f"{accepted_relative}/{name}") for name in payload
        }

        if accepted_dir.exists():
            present = {
                str(p.relative_to(accepted_dir).as_posix())
                for p in accepted_dir.rglob("*")
                if p.is_file()
            }
            if present != set(payload):
                raise AcceptedImmutable(
                    f"accepted receipt {receipt_hash} already exists with a different file set"
                )
            for name, data in payload.items():
                if file_digest(targets[name]) != bytes_digest(data):
                    raise AcceptedImmutable(
                        f"accepted receipt {receipt_hash} already exists with different bytes for {name!r}"
                    )
            return {name: bytes_digest(data) for name, data in payload.items()}

        staged = {name: self.stage(data) for name, data in payload.items()}
        try:
            for name, source in staged.items():
                target = targets[name]
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(source, target)
                self._fsync_dir(target.parent)
        except BaseException:
            for source in staged.values():
                Path(source).unlink(missing_ok=True)
            raise

        for target in targets.values():
            os.chmod(target, _ACCEPTED_FILE_MODE)
        for directory in sorted(
            {p for p in accepted_dir.rglob("*") if p.is_dir()} | {accepted_dir},
            key=lambda p: len(p.parts),
            reverse=True,
        ):
            os.chmod(directory, _ACCEPTED_DIR_MODE)
        return {name: bytes_digest(data) for name, data in payload.items()}

    def verify_artifact(self, record: VersionRecord) -> bool:
        """Recompute the digest from the bytes on disk; never trusts a claim."""
        path = self.resolve(record.artifact_path)
        if not path.is_file():
            return False
        return file_digest(path) == record.content_hash and path.stat().st_size == record.byte_size

    def is_write_protected(self, relative: str) -> bool:
        path = self.resolve(relative)
        if not path.exists():
            return False
        return not bool(stat.S_IMODE(path.stat().st_mode) & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
