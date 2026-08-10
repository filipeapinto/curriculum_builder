"""The run root's one authoritative lifecycle record.

`outputs/<run>/run_state.json` is written here and nowhere else. Nothing infers run
status from directory contents: a run that stopped says so, with a reason, and
`COMPLETE` is reachable only through `workbook.assemble()`.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import jsonschema


class RunStateError(RuntimeError):
    """A resume, transition or close that would record something untrue."""


STATE_FILE = "run_state.json"
SCHEMA = "schemas/run_lifecycle.schema.v1.json"

# A unit whose own acceptance.json records one of these has been carried as far as this
# run can carry it. Anything else is unfinished, however many files its directory holds.
_COMPLETED_STATES = {"ACCEPTED", "ACCEPTED_PENDING_REVIEW"}
_BLOCKED_STATES = {"BLOCKED"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def state_path(output_root: Path) -> Path:
    return Path(output_root) / STATE_FILE


def manifest_unit_ids(output_root: Path) -> list[str]:
    preflight = Path(output_root) / "results/gate_1_static_preflight.json"
    if not preflight.is_file():
        raise RunStateError(f"no static preflight record under {output_root} to read the manifest from")
    return list(json.loads(preflight.read_text()).get("unit_ids", []))


def read(output_root: Path) -> dict[str, Any] | None:
    path = state_path(output_root)
    return json.loads(path.read_text()) if path.is_file() else None


def validate(state: dict[str, Any], engine: Path) -> None:
    jsonschema.Draft202012Validator(json.loads((Path(engine) / SCHEMA).read_text())).validate(state)


def _scan_units(output_root: Path, manifest_ids: list[str]) -> dict[str, str]:
    """Each attempted unit's own recorded terminal state. A directory alone counts as nothing."""
    found: dict[str, str] = {}
    for unit_id in manifest_ids:
        acceptance = Path(output_root) / unit_id / "acceptance.json"
        if acceptance.is_file():
            found[unit_id] = json.loads(acceptance.read_text()).get("terminal_state", "UNKNOWN")
    return found


def _recompute(output_root: Path, base: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest_ids = manifest_unit_ids(output_root)
    states = _scan_units(output_root, manifest_ids)
    completed = [uid for uid in manifest_ids if states.get(uid) in _COMPLETED_STATES]
    blocked = [uid for uid in manifest_ids if states.get(uid) in _BLOCKED_STATES]
    failed = [uid for uid in manifest_ids
              if uid in states and states[uid] not in _COMPLETED_STATES | _BLOCKED_STATES]
    remaining = [uid for uid in manifest_ids if uid not in states]

    state = dict(base or {})
    meta_path = Path(output_root) / "meta_execution_state.json"
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text())
        for key in ("manifest_sha256", "prompt_sha256"):
            if meta.get(key):
                state[key] = meta[key]
    state.update({
        "manifest_unit_count": len(manifest_ids),
        "manifest_unit_ids": manifest_ids,
        "completed_unit_ids": completed,
        "blocked_unit_ids": blocked,
        "failed_unit_ids": failed,
        "remaining_unit_ids": remaining,
        "unit_states": states,
        "next_unit": remaining[0] if remaining else None,
        "updated_at": _now(),
    })
    state.setdefault("started_at", state["updated_at"])
    state.setdefault("workbook_assembled", False)
    state.setdefault("closed_at", None)
    if completed:
        last = completed[-1]
        state["resumable_checkpoint"] = {
            "unit_id": last,
            "hashes": json.loads((Path(output_root) / last / "interrupt_receipt.json").read_text())
            ["preserved_hashes"] if (Path(output_root) / last / "interrupt_receipt.json").is_file() else {},
        }
    return state


def _write(output_root: Path, state: dict[str, Any]) -> dict[str, Any]:
    state_path(output_root).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return state


def record_unit_transition(output_root: Path, unit_id: str, terminal_state: str) -> dict[str, Any]:
    """Called from `finalize()` once each unit's own acceptance.json is on disk.

    Never promotes the run to COMPLETE: while any manifest unit is unattempted the run is
    IN_PROGRESS, and declaring it stopped is `close_run`'s job.
    """
    output_root = Path(output_root)
    state = _recompute(output_root, read(output_root))
    state["current_unit"] = unit_id
    if state["remaining_unit_ids"]:
        state["run_status"] = "IN_PROGRESS"
        state.pop("terminal_reason", None)
        state["closed_at"] = None
    else:
        state["run_status"] = state.get("run_status", "IN_PROGRESS")
        if state["run_status"] == "COMPLETE" and not state.get("workbook_assembled"):
            state["run_status"] = "IN_PROGRESS"
    state["last_transition"] = None
    state.pop("last_transition", None)
    return _write(output_root, state)


def close_run(output_root: Path, reason: str, *, status: str = "PARTIAL") -> dict[str, Any]:
    """An explicit human decision that the run has stopped, with the reason stated.

    Never inferred. `COMPLETE` is not reachable here — only `workbook.assemble()` writes it.
    """
    if status not in {"PARTIAL", "INTERRUPTED", "BLOCKED"}:
        raise RunStateError(f"close_run records a stated stop, not {status!r}")
    if not reason or len(reason) < 20:
        raise RunStateError("close_run requires a stated terminal_reason")
    output_root = Path(output_root)
    state = _recompute(output_root, read(output_root))
    state["run_status"] = status
    state["terminal_reason"] = reason
    state["closed_at"] = _now()
    return _write(output_root, state)


def assert_resumable(output_root: Path, curriculum_hash: str, prompt_hash: str,
                     requested_unit: str) -> dict[str, Any]:
    """Refuse to start a unit whose inputs have moved, that is out of order, or that is done."""
    output_root = Path(output_root)
    state = read(output_root)
    if state is None:
        raise RunStateError(f"no {STATE_FILE} under {output_root}; this run has no lifecycle record")
    recorded_manifest = state.get("manifest_sha256")
    recorded_prompt = state.get("prompt_sha256")
    if recorded_manifest and recorded_manifest != curriculum_hash:
        raise RunStateError(
            f"manifest hash mismatch: run recorded {recorded_manifest}, caller has {curriculum_hash}")
    if recorded_prompt and recorded_prompt != prompt_hash:
        raise RunStateError(
            f"prompt hash mismatch: run recorded {recorded_prompt}, caller has {prompt_hash}")
    existing = (state.get("unit_states") or {}).get(requested_unit)
    if existing in _COMPLETED_STATES:
        raise RunStateError(
            f"{requested_unit} already records {existing}; refusing to overwrite an accepted unit")
    if state.get("next_unit") is not None and requested_unit != state["next_unit"]:
        raise RunStateError(
            f"{requested_unit} is out of order: the next unattempted unit is {state['next_unit']}")
    return state
