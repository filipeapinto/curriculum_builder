#!/usr/bin/env python3
"""`python3 -m runtime.run_curriculum` — the sole production entry to the compiled
Plan 26 LangGraph curriculum factory (spec section 16).

This module parses and validates CLI syntax, canonicalizes paths, acquires the
per-output-root execution lock, prepares one episode invocation, builds the one
production graph (`runtime.langgraph_factory.graph.build_curriculum_factory_graph`),
invokes it exactly once, projects its structured output into the one printed JSON
object, and maps the result to an exit code. It runs no product step itself: it
holds no node body, no guard, no join, no acceptance rule, and no frontier
selection — every one of those lives inside the compiled graph, which is the only
thing here that ever decides what a run produced.

Two narrow, pure, side-effect-free helpers are imported from the graph package
rather than re-implemented: `_resolve_active_manifest` and `_frozen_input_records`
(`runtime.langgraph_factory.nodes.inputs`) are the exact functions the graph's own
input-freezing node uses to pick the active manifest and hash the frozen input
set. This module calls them once, before the graph exists, purely to fix the
identity seed and the authorization/transport digest a `RuntimeContext` needs
before the first invocation; the graph's input-freezing node independently
recomputes the same values inside the episode and is the sole authority the graph
itself trusts. Reusing the functions (rather than duplicating the hashing rule)
is what keeps the two computations from silently drifting apart; it is not a
second product path, because neither call site is reachable from the other and
neither one decides acceptance, routing, or a terminal.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from runtime.langgraph_factory import persistence as P
from runtime.langgraph_factory import transport as tp
from runtime.langgraph_factory.artifacts import canonical_digest
from runtime.langgraph_factory.egress import AuthorizationRecord, EgressGuard, ReceiptLog
from runtime.langgraph_factory.graph import build_curriculum_factory_graph, build_runtime_context
from runtime.langgraph_factory.nodes.inputs import (
    REQUIRED_CAPABILITIES,
    _frozen_input_records,
    _resolve_active_manifest,
)

__all__ = ["build_parser", "main"]

PROG = "python3 -m runtime.run_curriculum"
CONTRACT_VERSION = "1"

# spec section 14's exit-code column, restated here rather than imported: this
# module must not import a node body, guard, or terminal-writing function, and
# the mapping itself is fixed, spec-owned data, not a decision this CLI makes.
TERMINAL_EXIT_CODES: dict[str, int] = {
    "UNIT_ACCEPTED": 0,
    "COMPLETE": 0,
    "INTERRUPTED": 10,
    "PAUSED_PREREQUISITE": 11,
    "CONVERGENCE_EXHAUSTED": 12,
    "SYSTEM_FAILURE": 20,
}
SYSTEM_FAILURE_EXIT = 20
ARGUMENT_ERROR_EXIT = 2
NOT_READY_EXIT = 3

# FactoryState channels that belong to *this* episode and must never be seeded
# from a prior episode's checkpointed values: the graph's own bootstrap and
# resume nodes write them fresh, and a stale write_once value here would
# collide with that fresh write instead of being silently ignored.
_EPISODE_SCOPED_STATE_FIELDS: frozenset[str] = frozenset(
    {
        "invocation",
        "bootstrap_kind",
        "validated_recovery_envelope",
        "episode_id",
        "checkpoint_thread_id",
        "checkpoint_namespace",
        "resume_from",
        "pending_failure",
        "pending_packet",
        "pending_guard",
        "terminal_candidate",
        "terminal",
    }
)


class CliError(Exception):
    """Base class for a pre-episode CLI refusal; carries its own exit code."""

    exit_code = ARGUMENT_ERROR_EXIT

    def __init__(self, code: str, message: str, **detail: Any) -> None:
        super().__init__(message)
        self.code = code
        self.detail = detail


class CliArgumentError(CliError):
    """Malformed or contradictory CLI input. Exit 2, before any episode."""

    exit_code = ARGUMENT_ERROR_EXIT


class CliNotReadyError(CliError):
    """A syntactically valid invocation the run cannot safely start. Exit 3."""

    exit_code = NOT_READY_EXIT


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------- args


def build_parser() -> argparse.ArgumentParser:
    """The exact preflight/one/all/resume argument surface of spec section 16."""

    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Sole production CLI entry to the compiled Plan 26 curriculum factory.",
    )
    parser.add_argument("--engine-root", required=True, metavar="PATH")
    parser.add_argument("--curriculum", required=True, metavar="PATH")
    parser.add_argument("--output-root", required=True, metavar="PATH")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true", help="read-only readiness check; creates no run")
    mode.add_argument("--unit", metavar="UNIT_ID", help="run one requested unit plus its prerequisite closure")
    mode.add_argument("--all", action="store_true", help="run the full exact manifest")
    mode.add_argument("--resume", action="store_true", help="resume a legally resumable episode")

    parser.add_argument(
        "--authorization",
        metavar="PATH",
        help="external-data authorization record; required for --unit, --all, and --resume",
    )
    return parser


def _validate_args(args: argparse.Namespace) -> None:
    if args.preflight and args.authorization:
        raise CliArgumentError(
            "ARG-PREFLIGHT-NO-AUTHORIZATION",
            "--preflight is a read-only capability check and does not take --authorization",
        )
    if not args.preflight and not args.authorization:
        raise CliArgumentError(
            "ARG-AUTHORIZATION-REQUIRED",
            "--unit, --all, and --resume each require --authorization",
        )


# ---------------------------------------------------------------- path resolution


def _canonical_root(value: str, label: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()
    if not path.is_dir():
        raise CliArgumentError("ARG-NOT-A-DIRECTORY", f"{label} is not a directory: {path}", path=str(path))
    return path


def _canonical_output_root(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def _resolve_curriculum_root(value: str) -> Path:
    """Accept either a manifest file or a curriculum directory (spec section 16)."""

    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()
    if path.is_file():
        return path.parent
    if path.is_dir():
        return path
    raise CliArgumentError("ARG-CURRICULUM-NOT-FOUND", f"--curriculum does not exist: {path}", path=str(path))


def _read_authorization(value: str) -> dict[str, Any]:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()
    if not path.is_file():
        raise CliArgumentError(
            "ARG-AUTHORIZATION-NOT-FOUND", f"--authorization file not found: {path}", path=str(path)
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CliArgumentError(
            "ARG-AUTHORIZATION-UNREADABLE", f"--authorization is not readable JSON: {error}", path=str(path)
        ) from error
    if not isinstance(raw, dict):
        raise CliArgumentError("ARG-AUTHORIZATION-SHAPE", "--authorization must be a JSON object", path=str(path))
    missing = [key for key in ("approved_at_utc", "expires_at_utc", "providers") if key not in raw]
    if missing:
        raise CliArgumentError(
            "ARG-AUTHORIZATION-INCOMPLETE",
            f"--authorization is missing required field(s) {missing}",
            path=str(path),
        )
    return raw


def _collision_reason(output_root: Path) -> str | None:
    """spec section 16: a fresh output root must not exist, or exist empty."""

    if not output_root.exists():
        return None
    if not output_root.is_dir():
        return f"--output-root exists and is not a directory: {output_root}"
    if any(output_root.iterdir()):
        return (
            f"--output-root {output_root} is not empty and carries no resumable run; "
            "a fresh run requires a nonexistent or empty output root"
        )
    return None


# --------------------------------------------------------------------------- authorization/capability


def _authorization_envelope(raw: Mapping[str, Any], *, curriculum_digest: str, output_root: Path) -> dict[str, Any]:
    envelope = dict(raw)
    envelope["curriculum_digest"] = curriculum_digest
    envelope["output_root"] = str(output_root)
    return envelope


def _authorization_record(
    raw: Mapping[str, Any], *, run_id: str, curriculum_digest: str, output_root: Path
) -> AuthorizationRecord:
    return AuthorizationRecord(
        run_id=run_id,
        curriculum_digest=curriculum_digest,
        output_root=str(output_root),
        approved_at_utc=str(raw["approved_at_utc"]),
        expires_at_utc=str(raw["expires_at_utc"]),
        providers=raw.get("providers") or {},
    )


def _capability_forbidden_paths(engine_root: Path) -> list[Path]:
    return [path for path in (engine_root / "pyproject.toml", engine_root / "runtime") if path.exists()]


def _prove_live_capabilities(context: Any, engine_root: Path, output_root: Path) -> dict[str, Any]:
    """Prove the transport isolation facets before the first model transmission.

    Mutates the already-built `context.transport_registry` in place: the proof
    depends on `guard.installed`, and the guard the proof must observe is the
    exact one the transport will use to gate every real transmission, not a
    second guard built only to be thrown away.
    """

    transport = context.transport_registry
    guard = transport.guard
    probe_root = output_root / ".workspaces" / "_cli_capability_probe"
    proof = tp.prove_transport_capabilities(
        guard=guard,
        probe_root=probe_root,
        forbidden_paths=_capability_forbidden_paths(engine_root),
    )
    transport.capability_proof = proof
    return proof


def _preflight_capabilities() -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Bounded local capability probes only; never populates the real output root."""

    with tempfile.TemporaryDirectory(prefix="plan26-preflight-") as raw_probe_root:
        probe_root = Path(raw_probe_root)
        receipts = ReceiptLog()
        guard = EgressGuard(receipts)
        transport = tp.CliTransport(
            output_root=probe_root,
            run_id="preflight",
            curriculum_digest="0" * 64,
            authorization=None,
            receipts=receipts,
            guard=guard,
            ledger=tp.AttemptLedger(),
            capability_proof=None,
            evidence_root=probe_root / "evidence",
        )
        guard.install()
        try:
            results: dict[str, dict[str, Any]] = {}
            missing: list[str] = []
            for capability in REQUIRED_CAPABILITIES:
                proof = transport.prove_capability(capability)
                results[capability] = proof
                if proof.get("result") != "PASS":
                    missing.append(capability)
        finally:
            guard.uninstall()
    return results, missing


# --------------------------------------------------------------------------- preflight


def _run_preflight(engine_root: Path, curriculum_root: Path, output_root: Path) -> tuple[dict[str, Any], int]:
    collision = _collision_reason(output_root)
    capabilities, missing = _preflight_capabilities()
    ready = collision is None and not missing
    payload: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "kind": "PREFLIGHT",
        "ready": ready,
        "engine_root": str(engine_root),
        "curriculum_root": str(curriculum_root),
        "output_root": str(output_root),
        "capabilities": capabilities,
        "missing_capabilities": missing,
        "collision": collision,
    }
    return payload, (0 if ready else NOT_READY_EXIT)


# --------------------------------------------------------------------------- live invocation


def _acquire_lock(output_root: Path) -> P.ExecutionLock:
    lock = P.ExecutionLock(output_root)
    try:
        lock.acquire()
    except P.ExecutionLockUnavailable as error:
        raise CliNotReadyError("LOCK-UNAVAILABLE", str(error)) from error
    return lock


def _prepare_fresh(
    *, engine_root: Path, curriculum_root: Path, output_root: Path, mode: str, requested_unit_id: str | None,
    lock: P.ExecutionLock,
) -> tuple[P.EpisodeInvocation, dict[str, Any], str]:
    active_manifest_path = _resolve_active_manifest(curriculum_root)
    identity_seed = {
        "contract_version": CONTRACT_VERSION,
        "created_at": _utc_now_iso(),
        "engine_root": str(engine_root),
        "curriculum_root": str(curriculum_root),
        "active_manifest_path": str(active_manifest_path),
        "output_root": str(output_root),
        "mode": mode,
        "requested_unit_id": requested_unit_id,
    }
    try:
        invocation = P.prepare_episode_invocation(
            output_root=output_root, lock=lock, identity_seed=identity_seed, resume=False
        )
    except P.PersistenceError as error:
        raise CliNotReadyError("BOOTSTRAP-REFUSED", str(error)) from error

    frozen_digest = canonical_digest(_frozen_input_records(engine_root, curriculum_root, active_manifest_path))
    envelope = {
        "kind": "fresh",
        "contract_version": CONTRACT_VERSION,
        "engine_root": str(engine_root),
        "curriculum_root": str(curriculum_root),
        "output_root": str(output_root),
        "mode": mode,
        "requested_unit_id": requested_unit_id,
        "authorization": None,  # filled by the caller once it has curriculum_digest
        "episode_ordinal": invocation.episode_ordinal,
        "prior_identity": None,
        "prior_terminal": None,
        "lease_open": False,
    }
    return invocation, envelope, frozen_digest


def _prepare_resume(
    *, output_root: Path, lock: P.ExecutionLock, compiled: Any
) -> tuple[P.EpisodeInvocation, dict[str, Any], str, dict[str, Any]]:
    saver, connection = P.open_checkpoint_saver(output_root)
    try:
        view = P.ReadOnlyCheckpointView(compiled, saver)
        try:
            invocation = P.prepare_episode_invocation(
                output_root=output_root, lock=lock, resume=True, read_view=view
            )
        except P.PersistenceError as error:
            raise CliNotReadyError("RESUME-REFUSED", str(error)) from error

        seed_values: dict[str, Any] = {}
        if invocation.prior_thread_id is not None:
            prior = P.extract_prior_episode(view, invocation.prior_thread_id)
            seed_values = {
                key: value
                for key, value in prior.values.items()
                if key not in _EPISODE_SCOPED_STATE_FIELDS
            }
    finally:
        connection.close()

    identity = invocation.identity_envelope
    prior_terminal = None
    if invocation.resume_from is not None:
        prior_terminal = invocation.resume_from.get("terminal")

    bootstrap_kind = {
        P.BOOTSTRAP_RESUME: "resume",
        P.BOOTSTRAP_RECOVER_ORPHAN: "recover_orphan",
    }.get(invocation.bootstrap_kind, invocation.bootstrap_kind)

    envelope = {
        "kind": bootstrap_kind,
        "contract_version": identity.get("contract_version"),
        "engine_root": identity.get("engine_root"),
        "curriculum_root": identity.get("curriculum_root"),
        "output_root": identity.get("output_root"),
        "mode": identity.get("mode"),
        "requested_unit_id": identity.get("requested_unit_id"),
        "authorization": None,  # filled by the caller once it has curriculum_digest
        "episode_ordinal": invocation.episode_ordinal,
        "prior_identity": identity,
        "prior_terminal": None if bootstrap_kind == "recover_orphan" else prior_terminal,
        "lease_open": bootstrap_kind == "recover_orphan",
    }
    frozen_digest = str(seed_values.get("frozen_digest") or "")
    return invocation, envelope, frozen_digest, seed_values


def _invoke(
    *,
    engine_root: Path,
    output_root: Path,
    envelope: dict[str, Any],
    invocation: P.EpisodeInvocation,
    frozen_digest: str,
    authorization_raw: Mapping[str, Any],
    seed_values: Mapping[str, Any] | None,
    compiled: Any,
) -> dict[str, Any]:
    context = build_runtime_context(
        engine_root=engine_root,
        output_root=output_root,
        run_id=invocation.run_id,
        curriculum_digest=frozen_digest,
        authorization=_authorization_record(
            authorization_raw, run_id=invocation.run_id, curriculum_digest=frozen_digest, output_root=output_root
        ),
        capability_proof=None,
    )
    envelope["authorization"] = _authorization_envelope(
        authorization_raw, curriculum_digest=frozen_digest, output_root=output_root
    )

    guard = context.transport_registry.guard
    guard.install()
    try:
        _prove_live_capabilities(context, engine_root, output_root)
        graph_input: dict[str, Any] = {**(seed_values or {}), "invocation": envelope}
        return dict(compiled.invoke(graph_input, config=invocation.config, context=context))
    finally:
        guard.uninstall()


# --------------------------------------------------------------------------- output projection


def _project_result(output: Mapping[str, Any]) -> dict[str, Any]:
    terminal = output.get("terminal") or {}
    kind = terminal.get("kind")

    payload: dict[str, Any] = {
        "contract_version": output.get("contract_version"),
        "run_id": output.get("run_id"),
        "episode_id": output.get("episode_id"),
        "terminal": terminal,
        "mode": output.get("mode"),
        "requested_unit_id": output.get("requested_unit_id"),
        "checkpoint_id": None,
        "evidence_index_hash": canonical_digest(list(output.get("evidence_index_entries") or [])),
        "output_root": output.get("output_root"),
    }

    checkpoints = list(output.get("checkpoint_metadata") or [])
    if checkpoints:
        payload["checkpoint_id"] = checkpoints[-1].get("checkpoint_id")

    if kind == "UNIT_ACCEPTED":
        accepted = output.get("accepted_unit_receipts") or {}
        payload["accepted_receipt"] = accepted.get(output.get("requested_unit_id"))
    elif kind == "COMPLETE":
        audits = list(output.get("final_release_audits") or [])
        payload["release_receipt"] = audits[-1] if audits else None

    return payload


def _exit_code_for(payload: Mapping[str, Any]) -> int:
    terminal = payload.get("terminal") or {}
    kind = terminal.get("kind")
    return TERMINAL_EXIT_CODES.get(kind, SYSTEM_FAILURE_EXIT)


def _system_failure_payload(message: str, *, code: str) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "terminal": {
            "kind": "SYSTEM_FAILURE",
            "failure": {"class": "system", "cause": code, "message": message},
        },
    }


# --------------------------------------------------------------------------- main


def _run_live(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    engine_root = _canonical_root(args.engine_root, "--engine-root")
    curriculum_root = _resolve_curriculum_root(args.curriculum)
    output_root = _canonical_output_root(args.output_root)
    authorization_raw = _read_authorization(args.authorization)

    if not args.resume:
        collision = _collision_reason(output_root)
        if collision is not None:
            # Checked before the lock is acquired: acquiring the lock itself
            # would create `.langgraph/` inside `output_root`, which must not
            # happen for a collision this CLI is about to refuse anyway.
            raise CliNotReadyError("COLLISION", collision)

    if args.resume and P.read_identity_envelope(output_root) is None:
        # A read-only check, deliberately before the lock: an output root with no
        # Plan 26 identity envelope (a fresh path, or a Plan 25 root) is refused
        # without acquiring anything or writing a single byte into it — it stays
        # exactly the readable history it was.
        raise CliNotReadyError(
            "RESUME-NO-IDENTITY",
            f"--output-root has no Plan 26 run identity to resume: {output_root}",
        )

    lock = _acquire_lock(output_root)
    try:
        if args.resume:
            compiled = build_curriculum_factory_graph(engine_root=engine_root, output_root=output_root)
            invocation, envelope, frozen_digest, seed_values = _prepare_resume(
                output_root=output_root, lock=lock, compiled=compiled
            )
        else:
            mode = "all" if args.all else "one"
            requested_unit_id = None if args.all else args.unit
            invocation, envelope, frozen_digest = _prepare_fresh(
                engine_root=engine_root,
                curriculum_root=curriculum_root,
                output_root=output_root,
                mode=mode,
                requested_unit_id=requested_unit_id,
                lock=lock,
            )
            seed_values = None
            compiled = build_curriculum_factory_graph(engine_root=engine_root, output_root=output_root)

        output = _invoke(
            engine_root=engine_root,
            output_root=output_root,
            envelope=envelope,
            invocation=invocation,
            frozen_digest=frozen_digest,
            authorization_raw=authorization_raw,
            seed_values=seed_values,
            compiled=compiled,
        )
    finally:
        lock.release()

    payload = _project_result(output)
    return payload, _exit_code_for(payload)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        _validate_args(args)
        if args.preflight:
            engine_root = _canonical_root(args.engine_root, "--engine-root")
            curriculum_root = _resolve_curriculum_root(args.curriculum)
            output_root = _canonical_output_root(args.output_root)
            payload, code = _run_preflight(engine_root, curriculum_root, output_root)
        else:
            payload, code = _run_live(args)
    except CliError as error:
        print(f"{error.code}: {error}", file=sys.stderr)
        # A pre-episode refusal (bad arguments, collision, lock, resume identity)
        # writes no episode and no terminal record at all — exactly section 14's
        # "neither is a product terminal" — so the printed object carries no
        # `terminal` key rather than a fabricated or empty one.
        payload = {"contract_version": CONTRACT_VERSION, "error_code": error.code, "message": str(error)}
        print(json.dumps(payload))
        return error.exit_code
    except Exception as error:  # never let an unhandled fault look like anything but a failure
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        print(json.dumps(_system_failure_payload(str(error), code=type(error).__name__)))
        return SYSTEM_FAILURE_EXIT

    print(json.dumps(payload))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
