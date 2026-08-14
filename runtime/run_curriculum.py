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
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from runtime.langgraph_factory import persistence as P
from runtime.langgraph_factory import transport as tp
from runtime.langgraph_factory.artifacts import canonical_digest
from runtime.langgraph_factory.egress import (
    PROVIDER_DATA_CLASSES,
    PROVIDERS,
    AuthorizationRecord,
    EgressGuard,
    ReceiptLog,
)
from runtime.langgraph_factory.graph import build_curriculum_factory_graph, build_runtime_context
from runtime.langgraph_factory.nodes.inputs import (
    DRIVER_CAPABILITY_FIELDS,
    MANDATORY_DRIVER_CLIS,
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


# ------------------------------------------------------------- driver capability proof
#
# spec 7.1's five differentiated proof classes, corrected after the Run 26 false-ready
# defect (binaries present, one required provider unauthenticated, preflight still
# reported ready): a single undifferentiated flag never proves a CLI driver is really
# usable. Every field below is genuine and independently checkable; `ready` requires
# every mandatory field for every mandatory driver in `MANDATORY_DRIVER_CLIS`, so one
# unproven field makes the whole driver -- and the whole proof -- not ready.
#
# This is the production CLI's own logic (not a node body, so it may call
# `runtime.langgraph_factory.transport` directly, exactly as `_prove_live_capabilities`
# already does): it never reimplements N20's provider allowlist or data-class mapping,
# consuming `egress.PROVIDERS`/`egress.PROVIDER_DATA_CLASSES` read-only for the
# `approved_data_boundary` field, and it wires N20's tool/MCP-closure check (spec 7.1 class five,
# `transport.prove_claude_tool_closure`/`require_claude_tool_closure`) into this real
# dispatch path rather than leaving it a standalone, unwired function.

_FORBIDDEN_AUTH_ENV_VARS: tuple[str, ...] = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "OPENAI_API_KEY",
    "CLAUDE_API_KEY",
    "CODEX_API_KEY",
)

_PROBE_TIMEOUT_SECONDS = 60

# A fixed, hardcoded literal: no curriculum digest, output root, file path, or source
# text is ever interpolated into it, which is what makes `content_free_operation`
# provable rather than merely asserted.
_PROBE_INSTRUCTION: str = (
    'Preflight capability probe. Do not read, write, or invoke any tool. '
    'Reply with exactly the structured object {"ok": true} and nothing else.'
)

_PROBE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["ok"],
    "properties": {"ok": {"type": "boolean"}},
}

_TOOL_CLOSURE_NOT_APPLICABLE: dict[str, Any] = {
    "status": "not_applicable",
    "reason": "tool/MCP closure applies to the claude worker channel only",
}


def _probe_env() -> dict[str, str]:
    """The real ambient environment, minus every forbidden credential.

    Unlike a real M0x job's disposable, fully isolated `$HOME` (spec 7.2's
    content-isolation boundary: untrusted curriculum content must never see the
    operator's real home), this probe carries no curriculum content at all, so there
    is nothing to isolate it *from* -- it deliberately runs under the operator's real,
    already-authenticated environment, because "observable subscription-backed
    usability" means observing whether *this* machine's installed CLI is actually
    logged in right now, not whether a freshly emptied home would be. Stripping the
    forbidden credential names here is belt-and-suspenders: `permitted_auth_mode`
    already refuses to launch the probe at all once one is present.
    """

    return {key: value for key, value in os.environ.items() if key not in _FORBIDDEN_AUTH_ENV_VARS}


def _prove_one_driver(
    cli: str,
    *,
    model: str,
    provider: str,
    data_classes: Sequence[str],
    runner: Callable[..., tp.ProcessOutcome],
    workspace: Path,
) -> dict[str, Any]:
    fields: dict[str, Any] = {}

    try:
        identity = tp.probe_executable(cli)
    except tp.CapabilityProofFailed as error:
        fields["executable_identity"] = {
            "status": "FAIL", "reason": "executable_unproven", "detail": str(error),
        }
    else:
        fields["executable_identity"] = {
            "status": "PASS", "path": identity.path, "sha256": identity.sha256, "version": identity.version,
        }

    forbidden_present = sorted(name for name in _FORBIDDEN_AUTH_ENV_VARS if os.environ.get(name))
    if forbidden_present:
        fields["permitted_auth_mode"] = {
            "status": "FAIL", "reason": "forbidden_api_key_present", "credentials": forbidden_present,
        }
    else:
        fields["permitted_auth_mode"] = {"status": "PASS", "mode": "subscription"}

    # A preflight/driver-level check, never a per-job one: preflight explicitly takes
    # no `--authorization` (spec 16), so it has no run-scoped `AuthorizationRecord` to
    # evaluate a data class against -- that per-job, per-run check is
    # `egress.authorize_subprocess_transmission`'s own job at real dispatch time,
    # already exercised by N20's suite, and not re-derivable here without either
    # fabricating an authorization or reimplementing its rule. What a driver-level
    # proof *can* honestly establish, read-only against `egress.PROVIDERS`, is that
    # this driver's provider is still one of the approved, non-retired classes at
    # all -- an unapproved or retired provider fails closed here rather than only at
    # first real transmission.
    if provider not in PROVIDERS:
        fields["approved_data_boundary"] = {
            "status": "FAIL", "reason": "unapproved_provider", "provider": provider,
        }
    else:
        fields["approved_data_boundary"] = {
            "status": "PASS",
            "provider": provider,
            "registered_data_classes": sorted(set(data_classes)),
            "provider_data_classes": sorted(PROVIDER_DATA_CLASSES.get(provider, frozenset())),
        }

    fields["content_free_operation"] = {
        "status": "PASS",
        "probe_instruction_sha256": hashlib.sha256(_PROBE_INSTRUCTION.encode("utf-8")).hexdigest(),
        "transmitted_authorized_input_projection": {},
    }

    if fields["permitted_auth_mode"]["status"] != "PASS":
        fields["observable_subscription_backed_usability"] = {
            "status": "FAIL", "reason": "skipped_forbidden_auth_mode",
        }
        fields["tool_mcp_closure"] = (
            {"status": "FAIL", "reason": "skipped_forbidden_auth_mode"} if cli == "claude"
            else dict(_TOOL_CLOSURE_NOT_APPLICABLE)
        )
        failed_fields = sorted(name for name, detail in fields.items() if detail.get("status") == "FAIL")
        return {
            "cli": cli, "model": model, "provider": provider, "ready": not failed_fields,
            "failed_fields": failed_fields, "fields": fields,
        }

    probe_stdin: str | None = None
    if cli == "claude":
        projection = tp.build_cli_schema_projection(_PROBE_SCHEMA)
        probe_stdin = tp.build_claude_stdin_payload(instruction=_PROBE_INSTRUCTION, projection={})
        argv = tp.build_claude_argv(
            workspace=workspace, model=model, effort="low", cli_schema_projection=projection)
    else:
        # `build_codex_argv` pins `--output-schema output.schema.json -o result.json`,
        # both resolved against `-C <workspace>` (spec 7.2): codex reads the schema
        # from that staged file rather than accepting one inline, so the probe must
        # stage it exactly as a real job would, with the same content-free literal.
        (workspace / "output.schema.json").write_text(
            tp.canonical_json(_PROBE_SCHEMA), encoding="utf-8")
        argv = tp.build_codex_argv(
            workspace=workspace, model=model, reasoning_effort="low", instruction=_PROBE_INSTRUCTION)

    try:
        outcome = runner(
            argv, cwd=workspace, env=_probe_env(), timeout_seconds=_PROBE_TIMEOUT_SECONDS, stdin=probe_stdin,
        )
    except OSError as error:
        fields["observable_subscription_backed_usability"] = {
            "status": "FAIL", "reason": "probe_launch_failed", "detail": str(error),
        }
        fields["tool_mcp_closure"] = (
            {"status": "FAIL", "reason": "no_stream_output_to_evaluate_closure"} if cli == "claude"
            else dict(_TOOL_CLOSURE_NOT_APPLICABLE)
        )
        failed_fields = sorted(name for name, detail in fields.items() if detail.get("status") == "FAIL")
        return {
            "cli": cli, "model": model, "provider": provider, "ready": not failed_fields,
            "failed_fields": failed_fields, "fields": fields,
        }

    if outcome.returncode != 0:
        fields["observable_subscription_backed_usability"] = {
            "status": "FAIL", "reason": "nonzero_bounded_probe",
            "returncode": outcome.returncode, "termination": outcome.termination,
            "stderr": outcome.stderr[:500],
        }
    else:
        try:
            observed = (
                tp.observe_claude_identity(outcome.stdout) if cli == "claude"
                else tp.observe_codex_identity(outcome.stdout)
            )
        except tp.IdentityUnobservable as error:
            fields["observable_subscription_backed_usability"] = {
                "status": "FAIL", "reason": "malformed_or_unobservable_output", "detail": str(error),
            }
        else:
            if observed.model != model:
                fields["observable_subscription_backed_usability"] = {
                    "status": "FAIL", "reason": "model_driver_mismatch",
                    "expected_model": model, "observed_model": observed.model,
                }
            else:
                fields["observable_subscription_backed_usability"] = {
                    "status": "PASS", "observed_model": observed.model,
                }

    if cli == "claude":
        closure: Mapping[str, Any] | None = None
        try:
            closure = tp.prove_claude_tool_closure(outcome.stdout)
            tp.require_claude_tool_closure(closure)
        except tp.CapabilityProofFailed as error:
            fields["tool_mcp_closure"] = {
                "status": "FAIL", "reason": str(error),
                "observed_tools": closure.get("observed_tools") if closure else None,
                "invokable_mcp_servers": closure.get("invokable_mcp_servers") if closure else None,
            }
        else:
            fields["tool_mcp_closure"] = {"status": "PASS", "closure": dict(closure)}
    else:
        fields["tool_mcp_closure"] = dict(_TOOL_CLOSURE_NOT_APPLICABLE)

    failed_fields = sorted(
        name for name, detail in fields.items()
        if detail.get("status") not in ("PASS", "not_applicable")
    )
    return {
        "cli": cli, "model": model, "provider": provider, "ready": not failed_fields,
        "failed_fields": failed_fields, "fields": fields,
    }


def _prove_driver_capabilities(
    *, runner: Callable[..., tp.ProcessOutcome] | None = None, workspace: Path | None = None,
) -> dict[str, Any]:
    """The real, differentiated per-driver capability proof spec 7.1 requires.

    Bounded and content-free: no curriculum artifact, source text, PDF, rendered page,
    evidence, or user-owned file is ever read or transmitted by this probe. Never a
    curriculum model job -- exactly the same "bounded local capability check" contract
    `tp.prove_transport_capabilities` already carries for the transport-isolation
    facets, extended here to the driver identity/auth/usability/closure/boundary
    facets spec 7.1 additionally requires.
    """

    registry = tp.load_job_registry()
    routes_by_cli: dict[str, list[tp.JobRoute]] = {}
    for route in registry.values():
        routes_by_cli.setdefault(route.cli, []).append(route)

    active_runner = runner or tp.run_process
    with tempfile.TemporaryDirectory(prefix="plan26-driver-probe-") as raw_workspace:
        probe_workspace = workspace or Path(raw_workspace)
        drivers: dict[str, dict[str, Any]] = {}
        for cli in MANDATORY_DRIVER_CLIS:
            cli_routes = routes_by_cli.get(cli, ())
            if not cli_routes:
                drivers[cli] = {
                    "cli": cli, "model": None, "provider": None, "ready": False,
                    "failed_fields": list(DRIVER_CAPABILITY_FIELDS),
                    "fields": {
                        name: {"status": "FAIL", "reason": "no_registered_route_for_driver"}
                        for name in DRIVER_CAPABILITY_FIELDS
                    },
                }
                continue
            models = {route.model for route in cli_routes}
            providers = {route.provider for route in cli_routes}
            if len(models) != 1 or len(providers) != 1:
                drivers[cli] = {
                    "cli": cli, "model": sorted(models), "provider": sorted(providers), "ready": False,
                    "failed_fields": list(DRIVER_CAPABILITY_FIELDS),
                    "fields": {
                        name: {"status": "FAIL", "reason": "ambiguous_driver_route_binding"}
                        for name in DRIVER_CAPABILITY_FIELDS
                    },
                }
                continue
            model = next(iter(models))
            provider = next(iter(providers))
            data_classes = sorted({data_class for route in cli_routes for data_class in route.data_classes})
            drivers[cli] = _prove_one_driver(
                cli, model=model, provider=provider, data_classes=data_classes,
                runner=active_runner, workspace=probe_workspace,
            )
        ready = all(detail["ready"] for detail in drivers.values())
    return {"ready": ready, "drivers": drivers}


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
    # spec 7.1: the same real, differentiated driver-capability proof preflight uses,
    # attached to the exact registry instance the compiled graph's own capability-proof
    # gate reads (best-effort there, for registries that expose it), so a live run's
    # first transmission is gated by the same proof preflight already reported. This
    # is also the hard, unconditional stop that actually closes Run 26's false-ready
    # defect at the one real production entry point: raised here, before
    # `compiled.invoke()` is ever reached, exactly like `prove_transport_capabilities`
    # above already stops a live run on an unproven transport-isolation facet.
    driver_proof = _prove_driver_capabilities(runner=transport.runner)
    transport.driver_capability_proof = driver_proof
    if not driver_proof["ready"]:
        not_ready = sorted(name for name, detail in driver_proof["drivers"].items() if not detail["ready"])
        raise tp.CapabilityProofFailed(
            f"required driver capability unproven for: {not_ready}")
    return proof


def _preflight_capabilities() -> tuple[dict[str, dict[str, Any]], list[str], dict[str, Any]]:
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
            driver_capabilities = _prove_driver_capabilities(runner=transport.runner)
            if not driver_capabilities["ready"]:
                missing.append("driver_capability_proof")
        finally:
            guard.uninstall()
    return results, missing, driver_capabilities


# --------------------------------------------------------------------------- preflight


def _run_preflight(engine_root: Path, curriculum_root: Path, output_root: Path) -> tuple[dict[str, Any], int]:
    collision = _collision_reason(output_root)
    capabilities, missing, driver_capabilities = _preflight_capabilities()
    ready = collision is None and not missing
    payload: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "kind": "PREFLIGHT",
        "ready": ready,
        "engine_root": str(engine_root),
        "curriculum_root": str(curriculum_root),
        "output_root": str(output_root),
        "capabilities": capabilities,
        "driver_capabilities": driver_capabilities,
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
