"""CLI model transport for the Plan 26 curriculum factory (spec sections 6.3, 7, 9).

Eight frozen job routes, package-relative prompts and schemas, disposable per-activation
workspaces under an OS sandbox, observed-versus-decided model identity, and a single
frozen malformed/transient retry. No LangChain wrapper, no provider SDK, no direct model
HTTP endpoint: the only way to a model is a child process of the pinned CLI.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import jsonschema
import yaml

from .egress import (
    AuthorizationDenied,
    AuthorizationRecord,
    EgressGuard,
    ReceiptLog,
    authorize_subprocess_transmission,
    canonical_json,
    utc_now,
)

PACKAGE_ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = PACKAGE_ROOT / "config" / "model_jobs.v1.yaml"
SCHEMA_DIR = PACKAGE_ROOT / "schemas"
PROMPT_DIR = PACKAGE_ROOT / "prompts"
REPO_ROOT = PACKAGE_ROOT.parents[1]

AUTHORING_FAMILY = "openai"
REVIEW_FAMILY = "google"

RESERVED_WORKSPACE_NAMES = frozenset({
    "authorized_input.json", "output.schema.json", "result.json",
})
STAGED_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")

FORBIDDEN_MODEL_FIELDS = frozenset({
    "accept", "acceptance", "accepted", "admission", "admit", "admitted", "approval",
    "approved", "complete", "decision", "exit_code", "failed", "final", "gate", "join",
    "next", "next_node", "outcome", "pass", "pass_fail", "passed", "resume",
    "resume_frontier", "retries", "retry", "route", "routing", "status", "terminal",
    "terminal_candidate", "terminal_kind", "verdict",
})

REQUIRED_CAPABILITY_FACETS = (
    "filesystem_isolation",
    "python_process_egress_broker",
    "identity_observation",
)


class TransportError(RuntimeError):
    """Base class for every transport rejection."""


class RouteRejected(TransportError):
    pass


class CapabilityProofFailed(TransportError):
    pass


class IdentityUnobservable(TransportError):
    pass


class IdentityMismatch(TransportError):
    pass


class WorkspaceViolation(TransportError):
    pass


class AttemptLimitExceeded(TransportError):
    pass


class TransportRetryable(TransportError):
    """Malformed or transient failure; eligible for the one frozen retry."""

    def __init__(self, failure_class: str, detail: str = "") -> None:
        super().__init__(f"{failure_class}: {detail}" if detail else failure_class)
        self.failure_class = failure_class


class ResultParseError(TransportRetryable):
    pass


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- registry


@dataclass(frozen=True)
class JobRoute:
    job_id: str
    job_type: str
    cli: str
    family: str
    provider: str
    model: str
    task_class: str | None
    reasoning_effort: str
    schema: str
    prompt: str
    timeout_seconds: int
    retry_limit: int
    data_classes: tuple[str, ...]

    @property
    def is_review(self) -> bool:
        return self.family == REVIEW_FAMILY


_REGISTRY_CACHE: dict[Path, Mapping[str, JobRoute]] = {}


def load_job_registry(path: Path | str = REGISTRY_PATH) -> Mapping[str, JobRoute]:
    resolved = Path(path).resolve()
    if resolved in _REGISTRY_CACHE:
        return _REGISTRY_CACHE[resolved]
    document = yaml.safe_load(resolved.read_text(encoding="utf-8"))
    entries = document.get("jobs") or []
    declared = int(document.get("job_count", 0))
    if declared != 8 or len(entries) != 8:
        raise RouteRejected(
            f"registry must declare exactly eight jobs, found {len(entries)} (declared {declared})")
    routes: dict[str, JobRoute] = {}
    for entry in entries:
        route = JobRoute(
            job_id=entry["job_id"],
            job_type=entry["job_type"],
            cli=entry["cli"],
            family=entry["family"],
            provider=entry["provider"],
            model=entry["model"],
            task_class=entry.get("task_class"),
            reasoning_effort=entry["reasoning_effort"],
            schema=entry["schema"],
            prompt=entry["prompt"],
            timeout_seconds=int(entry["timeout_seconds"]),
            retry_limit=int(entry["retry_limit"]),
            data_classes=tuple(entry["data_classes"]),
        )
        if route.cli not in {"codex", "gemini"}:
            raise RouteRejected(f"unknown cli for {route.job_id}: {route.cli}")
        if route.cli == "codex" and route.family != AUTHORING_FAMILY:
            raise RouteRejected(f"codex route {route.job_id} must be family {AUTHORING_FAMILY}")
        if route.cli == "gemini" and route.family != REVIEW_FAMILY:
            raise RouteRejected(f"gemini route {route.job_id} must be family {REVIEW_FAMILY}")
        if route.job_id in routes:
            raise RouteRejected(f"duplicate job id {route.job_id}")
        routes[route.job_id] = route
    _REGISTRY_CACHE[resolved] = routes
    return routes


def resolve_route(job_id: str, registry: Mapping[str, JobRoute] | None = None) -> JobRoute:
    routes = registry if registry is not None else load_job_registry()
    try:
        return routes[job_id]
    except KeyError:
        raise RouteRejected(f"unknown job id: {job_id!r}") from None


def resolve_prompt_path(route: JobRoute) -> Path:
    """Resolve the prompt relative to this package, never the process cwd."""
    candidate = (PROMPT_DIR / route.prompt).resolve()
    if candidate.parent != PROMPT_DIR:
        raise RouteRejected(f"prompt escapes package prompt directory: {route.prompt!r}")
    if not candidate.is_file():
        raise RouteRejected(f"prompt does not resolve inside the package: {route.prompt!r}")
    return candidate


def resolve_schema_path(route: JobRoute) -> Path:
    candidate = (SCHEMA_DIR / route.schema).resolve()
    if candidate.parent != SCHEMA_DIR:
        raise RouteRejected(f"schema escapes package schema directory: {route.schema!r}")
    if not candidate.is_file():
        raise RouteRejected(f"schema does not resolve inside the package: {route.schema!r}")
    return candidate


def load_output_schema(route: JobRoute) -> dict[str, Any]:
    return _load_json(resolve_schema_path(route))


def collect_property_names(schema: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(schema, Mapping):
        for key, value in schema.items():
            if key == "properties" and isinstance(value, Mapping):
                names.update(str(name) for name in value)
            if isinstance(value, (Mapping, list)):
                names |= collect_property_names(value)
    elif isinstance(schema, list):
        for item in schema:
            names |= collect_property_names(item)
    return names


def assert_no_authoritative_fields(schema_or_value: Any, *, label: str) -> None:
    """Reject any routing/acceptance/terminal field in a model schema or candidate."""
    if isinstance(schema_or_value, Mapping) and "properties" in schema_or_value:
        names = collect_property_names(schema_or_value)
    else:
        names = _collect_object_keys(schema_or_value)
    offending = sorted(name for name in names if name.lower() in FORBIDDEN_MODEL_FIELDS)
    if offending:
        raise TransportError(f"{label} declares control-plane fields: {offending}")


def _collect_object_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, Mapping):
        keys.update(str(key) for key in value)
        for item in value.values():
            keys |= _collect_object_keys(item)
    elif isinstance(value, list):
        for item in value:
            keys |= _collect_object_keys(item)
    return keys


# ------------------------------------------------------------------------ executables


@dataclass(frozen=True)
class ExecutableIdentity:
    name: str
    path: str
    sha256: str | None
    version: str


def probe_executable(name: str, *, runner: Callable[..., Any] | None = None) -> ExecutableIdentity:
    located = shutil.which(name)
    if not located:
        raise CapabilityProofFailed(f"executable not on PATH: {name}")
    path = Path(located).resolve()
    try:
        digest: str | None = sha256_file(path)
    except OSError:
        digest = None
    run = runner or subprocess.run
    completed = run([str(path), "--version"], capture_output=True, text=True, timeout=60)
    if completed.returncode != 0:
        raise CapabilityProofFailed(f"{name} --version failed with {completed.returncode}")
    version = (completed.stdout or completed.stderr).strip().splitlines()[0]
    return ExecutableIdentity(name=name, path=str(path), sha256=digest, version=version)


# ---------------------------------------------------------------------- argv builders


def build_codex_argv(
    *,
    workspace: Path | str,
    model: str,
    reasoning_effort: str,
    instruction: str,
) -> list[str]:
    """The pinned Codex invocation (spec 7.2).

    `--json` is not decoration: the JSONL event stream is the only machine-readable
    channel this CLI offers for the executed model identity that 7.2 requires.
    """
    return [
        "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
        "-s", "read-only", "--skip-git-repo-check", "-C", str(workspace),
        "-m", model, "-c", f'model_reasoning_effort="{reasoning_effort}"',
        "--output-schema", "output.schema.json", "-o", "result.json",
        "--json", instruction,
    ]


def build_gemini_argv(*, model: str, instruction: str) -> list[str]:
    """The pinned Gemini invocation (spec 7.3)."""
    return [
        "gemini", "-m", model, "-s", "--approval-mode", "default",
        "--output-format", "json", instruction,
    ]


def build_job_argv(route: JobRoute, *, workspace: Path, instruction: str) -> list[str]:
    if route.cli == "codex":
        return build_codex_argv(workspace=workspace, model=route.model,
                                reasoning_effort=route.reasoning_effort,
                                instruction=instruction)
    if route.reasoning_effort != "cli_model_default":
        raise RouteRejected(
            f"{route.job_id}: gemini exposes no effort argument; "
            f"reasoning must be cli_model_default, not {route.reasoning_effort!r}")
    return build_gemini_argv(model=route.model, instruction=instruction)


def redact_command(argv: Sequence[str]) -> list[str]:
    redacted: list[str] = []
    for index, token in enumerate(argv):
        if index == len(argv) - 1 and len(token) > 200:
            redacted.append(f"<instruction:{sha256_bytes(token.encode())[:16]}>")
        else:
            redacted.append(token)
    return redacted


# --------------------------------------------------------------------- host sandbox


SANDBOX_UNAVAILABLE = "none"

INSTALL_PREFIXES = ("/opt/homebrew", "/usr/local", "/opt", "/usr", "/Library", "/System")


def executable_read_roots(executable_path: Path | str) -> tuple[Path, ...]:
    """The installation prefix the CLI needs to read to run at all.

    A packaged CLI is a symlink into a versioned cellar and may load its interpreter and
    shared libraries from a sibling package, so allowing only the binary's own directory
    aborts the process before it starts.
    """
    resolved = Path(executable_path).resolve()
    for prefix in INSTALL_PREFIXES:
        if resolved.is_relative_to(prefix):
            return (Path(prefix),)
    return (resolved.parent,)


def sandbox_mechanism() -> str:
    if sys.platform == "darwin" and shutil.which("sandbox-exec"):
        return "sandbox-exec"
    return SANDBOX_UNAVAILABLE


def _subpath_rules(paths: Sequence[Path]) -> str:
    seen: list[str] = []
    for path in paths:
        for candidate in {str(path), str(Path(path).resolve())}:
            if candidate not in seen:
                seen.append(candidate)
    return " ".join(f'(subpath "{candidate}")' for candidate in seen)


def render_sandbox_profile(
    *,
    workspace: Path,
    home: Path,
    readable: Sequence[Path] = (),
    allow_network: bool = True,
) -> str:
    writable = _subpath_rules([Path(workspace), Path(home)])
    readable_rule = _subpath_rules(list(readable)) if readable else ""
    network = (
        '(allow network-outbound (remote tcp "*:443") (remote tcp "*:80")'
        ' (remote udp "*:53") (remote unix-socket))\n(allow system-socket)\n'
        if allow_network else "(deny network*)\n"
    )
    lines = [
        "(version 1)",
        "(deny default)",
        '(import "system.sb")',
        "(allow process-exec* process-fork)",
        "(allow sysctl-read)",
        "(allow file-read-metadata)",
        "(allow signal (target self))",
    ]
    if readable_rule:
        lines.append(f"(allow file-read* {readable_rule})")
    lines.append(f"(allow file-read* file-write* {writable})")
    return "\n".join(lines) + "\n" + network


def build_sandboxed_argv(
    argv: Sequence[str],
    *,
    profile_path: Path,
) -> list[str]:
    mechanism = sandbox_mechanism()
    if mechanism == SANDBOX_UNAVAILABLE:
        raise CapabilityProofFailed(
            f"no host process sandbox available on {sys.platform}; refusing to launch a model CLI")
    return ["/usr/bin/sandbox-exec", "-f", str(profile_path), *argv]


def prove_workspace_isolation(
    *,
    workspace: Path,
    home: Path,
    forbidden_paths: Sequence[Path],
    runner: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Run a real probe inside the constructed sandbox and record what it could reach."""
    mechanism = sandbox_mechanism()
    if mechanism == SANDBOX_UNAVAILABLE:
        return {"mechanism": SANDBOX_UNAVAILABLE, "enforced": False,
                "evidence": f"no sandbox mechanism on {sys.platform}",
                "readable_forbidden_paths": [str(p) for p in forbidden_paths]}

    run = runner or subprocess.run
    workspace = Path(workspace).resolve()
    home = Path(home).resolve()
    probe_file = workspace / "isolation_probe.txt"
    probe_file.write_text("probe\n", encoding="utf-8")
    profile_path = home / "isolation_probe.sb"
    profile_path.write_text(
        render_sandbox_profile(workspace=workspace, home=home, allow_network=False),
        encoding="utf-8")

    inside = run(["/usr/bin/sandbox-exec", "-f", str(profile_path), "/bin/cat", str(probe_file)],
                 capture_output=True, text=True, timeout=60)
    leaked: list[str] = []
    for target in forbidden_paths:
        attempt = run(
            ["/usr/bin/sandbox-exec", "-f", str(profile_path), "/bin/cat", str(target)],
            capture_output=True, text=True, timeout=60)
        if attempt.returncode == 0:
            leaked.append(str(target))
    probe_file.unlink()

    enforced = inside.returncode == 0 and not leaked
    return {
        "mechanism": mechanism,
        "enforced": enforced,
        "evidence": (
            f"staged read rc={inside.returncode}; "
            f"{len(forbidden_paths)} forbidden path(s) probed; {len(leaked)} readable"),
        "readable_forbidden_paths": leaked,
    }


# ------------------------------------------------------------------- capability proof


def prove_transport_capabilities(
    *,
    guard: EgressGuard,
    probe_root: Path,
    forbidden_paths: Sequence[Path],
    registry: Mapping[str, JobRoute] | None = None,
    runner: Callable[..., Any] | None = None,
    identity_help: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Build the D03 transport capability proof; unproven required facets fail closed."""
    probe_root = Path(probe_root).resolve()
    workspace = probe_root / "workspace"
    home = probe_root / "home"
    workspace.mkdir(parents=True, exist_ok=True)
    home.mkdir(parents=True, exist_ok=True)
    isolation = prove_workspace_isolation(
        workspace=workspace, home=home, forbidden_paths=forbidden_paths, runner=runner)

    routes = registry if registry is not None else load_job_registry()
    clis = sorted({route.cli for route in routes.values()})
    required_flags = {"codex": "--json", "gemini": "--output-format"}
    observed_flags: dict[str, bool] = {}
    for cli in clis:
        help_text = (identity_help or {}).get(cli)
        if help_text is None:
            run = runner or subprocess.run
            args = [cli, "exec", "--help"] if cli == "codex" else [cli, "--help"]
            completed = run(args, capture_output=True, text=True, timeout=60)
            help_text = f"{completed.stdout}\n{completed.stderr}"
        observed_flags[cli] = required_flags[cli] in help_text

    facets: dict[str, dict[str, Any]] = {
        "filesystem_isolation": {
            "required": True,
            "enforced": bool(isolation["enforced"]),
            "mechanism": str(isolation["mechanism"]),
            "evidence": str(isolation["evidence"]),
            "limitation": None,
        },
        "python_process_egress_broker": {
            "required": True,
            "enforced": guard.installed,
            "mechanism": "socket.socket interception by EgressGuard",
            "evidence": f"guard installed={guard.installed}",
            "limitation": None,
        },
        "identity_observation": {
            "required": True,
            "enforced": all(observed_flags.values()),
            "mechanism": "codex --json JSONL events; gemini --output-format json stats.models",
            "evidence": canonical_json(observed_flags),
            "limitation": None,
        },
        "subprocess_network_scope": {
            "required": False,
            "enforced": isolation["mechanism"] != SANDBOX_UNAVAILABLE,
            "mechanism": "sandbox-exec network-outbound port scoping",
            "evidence": "outbound restricted to tcp 443/80 and udp 53",
            "limitation": (
                "sandbox-exec cannot pin an outbound host; the model CLI subprocess is "
                "constrained by port, not by provider hostname"),
        },
    }
    unsatisfied = sorted(
        name for name, facet in facets.items() if facet["required"] and not facet["enforced"])
    proof = {
        "proved_at_utc": utc_now().isoformat(),
        "platform": f"{platform.system()} {platform.release()}",
        "facets": facets,
        "satisfied": not unsatisfied,
        "unsatisfied_required_facets": unsatisfied,
    }
    jsonschema.Draft202012Validator(
        _load_json(SCHEMA_DIR / "internal_capability_proof.schema.json")).validate(proof)
    return proof


def require_capability_proof(proof: Mapping[str, Any] | None) -> None:
    if proof is None:
        raise CapabilityProofFailed("no transport capability proof was produced")
    missing = list(proof.get("unsatisfied_required_facets") or [])
    if not proof.get("satisfied") or missing:
        raise CapabilityProofFailed(
            f"required transport capability facets unproven: {missing or 'unknown'}")


# ------------------------------------------------------------------- identity observation


@dataclass(frozen=True)
class ObservedIdentity:
    family: str
    model: str
    model_source: str
    family_source: str


_CODEX_IDENTITY_EVENTS = ("session_configured", "thread.started", "turn.started", "model_reroute")


def observe_codex_identity(event_stream: str) -> ObservedIdentity:
    """Read the executed model out of the Codex JSONL event stream.

    Copying the decision here would defeat the whole check, so an event stream that
    never names a model is an unobservable identity, not a silent pass.
    """
    model: str | None = None
    model_source: str | None = None
    provider: str | None = None
    for line in event_stream.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, Mapping):
            continue
        payloads: list[tuple[str, Mapping[str, Any]]] = []
        inner = event.get("msg")
        if isinstance(inner, Mapping) and isinstance(inner.get("type"), str):
            payloads.append((inner["type"], inner))
        if isinstance(event.get("type"), str):
            body = event.get("payload")
            payloads.append((event["type"], body if isinstance(body, Mapping) else event))
        for event_type, payload in payloads:
            if event_type not in _CODEX_IDENTITY_EVENTS:
                continue
            observed = payload.get("model")
            if isinstance(observed, str) and observed:
                model, model_source = observed, event_type
            for key in ("model_provider_id", "provider", "model_provider"):
                value = payload.get(key)
                if isinstance(value, str) and value:
                    provider = value
    if not model:
        raise IdentityUnobservable(
            "codex event stream names no executed model; route conformance cannot be claimed")
    return ObservedIdentity(
        family=AUTHORING_FAMILY,
        model=model,
        model_source=f"codex_event:{model_source}",
        family_source=(f"codex_event:{provider}" if provider else "executable_identity:codex-cli"),
    )


def observe_gemini_identity(stdout: str) -> ObservedIdentity:
    """Read the executed model out of the Gemini JSON envelope's session metrics."""
    try:
        envelope = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise IdentityUnobservable(f"gemini envelope is not JSON: {error}") from error
    stats = envelope.get("stats") if isinstance(envelope, Mapping) else None
    models = stats.get("models") if isinstance(stats, Mapping) else None
    if not isinstance(models, Mapping) or not models:
        raise IdentityUnobservable(
            "gemini envelope carries no stats.models; executed identity is unobservable")
    called = [
        name for name, metrics in models.items()
        if isinstance(metrics, Mapping)
        and int((metrics.get("api") or {}).get("totalRequests", 0) or 0) > 0
    ]
    if len(called) != 1:
        raise IdentityUnobservable(
            f"gemini envelope reports {len(called)} models with requests; expected exactly one")
    return ObservedIdentity(
        family=REVIEW_FAMILY,
        model=called[0],
        model_source="gemini_envelope:stats.models",
        family_source="executable_identity:gemini-cli",
    )


def observe_identity(route: JobRoute, *, stdout: str) -> ObservedIdentity:
    if route.cli == "codex":
        return observe_codex_identity(stdout)
    return observe_gemini_identity(stdout)


def assert_identity_matches(route: JobRoute, observed: ObservedIdentity) -> None:
    if observed.model != route.model:
        raise IdentityMismatch(
            f"{route.job_id}: decided model {route.model!r} but executed {observed.model!r}")
    if observed.family != route.family:
        raise IdentityMismatch(
            f"{route.job_id}: decided family {route.family!r} but executed {observed.family!r}")
    if route.is_review and observed.family == AUTHORING_FAMILY:
        raise IdentityMismatch(
            f"{route.job_id}: review must not execute in the authoring family")


# ------------------------------------------------------------------------ JSON parsing


def _reject_duplicate_keys(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    seen: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise ResultParseError("duplicate_json_key", key)
        seen[key] = value
    return seen


def _reject_constant(name: str) -> Any:
    raise ResultParseError("non_finite_json_constant", name)


def parse_single_json_document(text: str) -> dict[str, Any]:
    """Parse exactly one JSON object; anything else is a malformed transport result."""
    if not text or not text.strip():
        raise ResultParseError("empty_result")
    if "```" in text:
        raise ResultParseError("fenced_result")
    stripped = text.lstrip()
    decoder = json.JSONDecoder(
        object_pairs_hook=_reject_duplicate_keys, parse_constant=_reject_constant)
    try:
        value, end = decoder.raw_decode(stripped)
    except json.JSONDecodeError as error:
        raise ResultParseError("malformed_json", str(error)) from error
    if stripped[end:].strip():
        raise ResultParseError("trailing_material", stripped[end:].strip()[:120])
    if not isinstance(value, dict):
        raise ResultParseError("result_is_not_an_object", type(value).__name__)
    return value


def extract_envelope_response(stdout: str) -> str:
    """One registered deterministic extractor for CLIs that emit an outer envelope."""
    envelope = parse_single_json_document(stdout)
    response = envelope.get("response")
    if not isinstance(response, str) or not response.strip():
        raise ResultParseError("envelope_carries_no_response")
    return response


def load_candidate(
    route: JobRoute,
    *,
    workspace: Path,
    stdout: str,
    schema: Mapping[str, Any],
) -> tuple[dict[str, Any], str]:
    result_path = Path(workspace) / "result.json"
    if result_path.is_file():
        document = result_path.read_text(encoding="utf-8")
        source = "result_file"
    else:
        document = extract_envelope_response(stdout)
        source = "envelope_extractor"
    candidate = parse_single_json_document(document)
    try:
        jsonschema.Draft202012Validator(dict(schema)).validate(candidate)
    except jsonschema.ValidationError as error:
        raise ResultParseError("schema_invalid_result", error.message) from error
    assert_no_authoritative_fields(candidate, label=f"{route.job_id} candidate")
    if route.job_id == "M01_RESEARCH_UNIT_SOURCES" and len(candidate) != 1:
        raise ResultParseError("m01_must_emit_exactly_one_phase_key")
    return candidate, source


# --------------------------------------------------------------------- attempt ledger


@dataclass(frozen=True)
class AttemptReservation:
    reservation_id: str
    activation_id: str
    job_id: str
    attempt_ordinal: int
    reserved_at_utc: str


class AttemptLedger:
    """D90's reservation surface: an attempt is committed before any process exists."""

    def __init__(self, *, attempts_per_activation: int = 2) -> None:
        self.attempts_per_activation = attempts_per_activation
        self._reserved: dict[str, list[AttemptReservation]] = {}

    def reserve(self, *, activation_id: str, job_id: str) -> AttemptReservation:
        existing = self._reserved.setdefault(activation_id, [])
        if len(existing) >= self.attempts_per_activation:
            raise AttemptLimitExceeded(
                f"{activation_id}: {len(existing)} attempts already reserved")
        reservation = AttemptReservation(
            reservation_id=f"{activation_id}#{len(existing) + 1}",
            activation_id=activation_id,
            job_id=job_id,
            attempt_ordinal=len(existing) + 1,
            reserved_at_utc=utc_now().isoformat(),
        )
        existing.append(reservation)
        return reservation

    def reservations(self, activation_id: str) -> tuple[AttemptReservation, ...]:
        return tuple(self._reserved.get(activation_id, ()))

    @property
    def total_reserved(self) -> int:
        return sum(len(items) for items in self._reserved.values())


# ------------------------------------------------------------------------- workspaces


@dataclass(frozen=True)
class StagedInput:
    name: str
    source_path: Path
    sha256: str


@dataclass
class Workspace:
    path: Path
    home: Path
    prompt_sha256: str
    schema_sha256: str
    input_sha256: str
    staged_sha256: dict[str, str] = field(default_factory=dict)
    baseline: dict[str, str] = field(default_factory=dict)

    def inventory(self) -> dict[str, str]:
        found: dict[str, str] = {}
        for item in sorted(self.path.rglob("*")):
            if item.is_file():
                found[str(item.relative_to(self.path))] = sha256_file(item)
        return found

    def assert_no_undeclared_writes(self, *, permitted_new: Sequence[str] = ()) -> None:
        after = self.inventory()
        allowed = set(permitted_new)
        for name, digest in after.items():
            if name in self.baseline:
                if self.baseline[name] != digest:
                    raise WorkspaceViolation(f"worker mutated staged file {name!r}")
            elif name not in allowed:
                raise WorkspaceViolation(f"worker wrote undeclared file {name!r}")

    def destroy(self) -> None:
        shutil.rmtree(self.path, ignore_errors=True)
        shutil.rmtree(self.home, ignore_errors=True)


def stage_workspace(
    *,
    output_root: Path | str,
    episode_id: str,
    activation_id: str,
    route: JobRoute,
    projection: Mapping[str, Any],
    authorization_receipt: Mapping[str, Any],
    staged_inputs: Sequence[StagedInput] = (),
    home_root: Path | str | None = None,
) -> Workspace:
    """Build the disposable activation directory described by spec 7.1."""
    root = Path(output_root).resolve() / ".workspaces" / episode_id / activation_id
    if root.exists():
        raise WorkspaceViolation(f"activation workspace already exists: {root}")
    root.mkdir(parents=True, mode=0o700)
    os.chmod(root, 0o700)

    home_parent = Path(home_root).resolve() if home_root else Path(tempfile.gettempdir()).resolve()
    home_parent.mkdir(parents=True, exist_ok=True)
    home = Path(tempfile.mkdtemp(prefix="plan26-home-", dir=str(home_parent)))
    os.chmod(home, 0o700)

    prompt_source = resolve_prompt_path(route)
    schema_source = resolve_schema_path(route)
    schema = _load_json(schema_source)
    assert_no_authoritative_fields(schema, label=f"{route.job_id} output schema")

    payload = {"projection": dict(projection), "authorization_receipt": dict(authorization_receipt)}
    input_path = root / "authorized_input.json"
    input_path.write_text(canonical_json(payload), encoding="utf-8")
    shutil.copyfile(schema_source, root / "output.schema.json")
    shutil.copyfile(prompt_source, root / route.prompt)

    staged_digests: dict[str, str] = {}
    reserved = RESERVED_WORKSPACE_NAMES | {route.prompt}
    for item in staged_inputs:
        if not STAGED_NAME_PATTERN.match(item.name) or item.name in reserved:
            raise WorkspaceViolation(f"illegal staged input name: {item.name!r}")
        source = Path(item.source_path)
        if source.is_symlink() or not source.is_file():
            raise WorkspaceViolation(f"staged input is not a regular file: {source}")
        actual = sha256_file(source)
        if actual != item.sha256:
            raise WorkspaceViolation(
                f"staged input {item.name!r} hash {actual} != declared {item.sha256}")
        shutil.copyfile(source, root / item.name)
        os.chmod(root / item.name, stat.S_IRUSR)
        staged_digests[item.name] = actual

    workspace = Workspace(
        path=root,
        home=home,
        prompt_sha256=sha256_file(prompt_source),
        schema_sha256=sha256_file(schema_source),
        input_sha256=sha256_file(input_path),
        staged_sha256=staged_digests,
    )
    workspace.baseline = workspace.inventory()
    return workspace


def build_worker_environment(*, home: Path, passthrough: Sequence[str] = ()) -> dict[str, str]:
    """Allowlisted environment over a dedicated temporary home; secrets pass by name only."""
    home = Path(home)
    environment = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
        "HOME": str(home),
        "TMPDIR": str(home),
        "XDG_CONFIG_HOME": str(home / "config"),
        "XDG_CACHE_HOME": str(home / "cache"),
        "CODEX_HOME": str(home / "codex"),
        "LANG": "C.UTF-8",
    }
    for child in ("config", "cache", "codex"):
        (home / child).mkdir(parents=True, exist_ok=True)
    for name in passthrough:
        value = os.environ.get(name)
        if value is not None:
            environment[name] = value
    return environment


# ---------------------------------------------------------------------- process runner


@dataclass(frozen=True)
class ProcessOutcome:
    returncode: int | None
    stdout: str
    stderr: str
    pid: int | None
    termination: str


def run_process(
    argv: Sequence[str],
    *,
    cwd: Path,
    env: Mapping[str, str],
    timeout_seconds: int,
    term_grace_seconds: float = 5.0,
) -> ProcessOutcome:
    """Process-group wall-clock timeout: TERM, wait five seconds, then KILL."""
    process = subprocess.Popen(
        list(argv), cwd=str(cwd), env=dict(env), text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    termination = "exited"
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        termination = "timeout_term"
        _signal_group(process, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=term_grace_seconds)
        except subprocess.TimeoutExpired:
            termination = "timeout_kill"
            _signal_group(process, signal.SIGKILL)
            stdout, stderr = process.communicate()
    if termination == "exited" and process.returncode is not None and process.returncode < 0:
        termination = "signal"
    return ProcessOutcome(
        returncode=process.returncode, stdout=stdout or "", stderr=stderr or "",
        pid=process.pid, termination=termination)


def _signal_group(process: subprocess.Popen[str], number: int) -> None:
    try:
        os.killpg(os.getpgid(process.pid), number)
    except (ProcessLookupError, PermissionError):
        process.send_signal(number)


# -------------------------------------------------------------------------- transport


@dataclass(frozen=True)
class TransportResult:
    candidate: dict[str, Any]
    receipt: dict[str, Any]
    attempts: tuple[dict[str, Any], ...]


class CliTransport:
    """Contained CLI model transport. The only path from this package to a model."""

    def __init__(
        self,
        *,
        output_root: Path | str,
        run_id: str,
        curriculum_digest: str,
        authorization: AuthorizationRecord | None,
        receipts: ReceiptLog,
        guard: EgressGuard,
        ledger: AttemptLedger,
        capability_proof: Mapping[str, Any] | None,
        registry: Mapping[str, JobRoute] | None = None,
        runner: Callable[..., ProcessOutcome] | None = None,
        evidence_root: Path | str | None = None,
        env_passthrough: Sequence[str] = (),
        keep_workspaces: bool = False,
        executables: Mapping[str, ExecutableIdentity] | None = None,
    ) -> None:
        self.output_root = Path(output_root).resolve()
        self.run_id = run_id
        self.curriculum_digest = curriculum_digest
        self.authorization = authorization
        self.receipts = receipts
        self.guard = guard
        self.ledger = ledger
        self.capability_proof = capability_proof
        self.registry = registry if registry is not None else load_job_registry()
        self.runner = runner or run_process
        self.evidence_root = (
            Path(evidence_root).resolve() if evidence_root
            else self.output_root / ".evidence" / "transport")
        self.env_passthrough = tuple(env_passthrough)
        self.keep_workspaces = keep_workspaces
        self._receipt_validator = jsonschema.Draft202012Validator(
            _load_json(SCHEMA_DIR / "internal_execution_receipt.schema.json"))
        self._executables: dict[str, ExecutableIdentity] = dict(executables or {})

    def executable(self, name: str) -> ExecutableIdentity:
        if name not in self._executables:
            self._executables[name] = probe_executable(name)
        return self._executables[name]

    def execute(
        self,
        *,
        job_id: str,
        activation_id: str,
        episode_id: str,
        projection: Mapping[str, Any],
        staged_inputs: Sequence[StagedInput] = (),
        data_classes: Sequence[str] | None = None,
    ) -> TransportResult:
        route = resolve_route(job_id, self.registry)
        resolve_prompt_path(route)
        resolve_schema_path(route)
        requested = tuple(data_classes) if data_classes is not None else route.data_classes
        undeclared = sorted(set(requested) - set(route.data_classes))
        if undeclared:
            raise RouteRejected(f"{route.job_id}: undeclared data classes {undeclared}")

        authorization_receipt = authorize_subprocess_transmission(
            self.authorization, provider=route.provider, data_classes=requested,
            curriculum_digest=self.curriculum_digest, run_id=self.run_id,
            output_root=self.output_root, receipts=self.receipts)

        require_capability_proof(self.capability_proof)

        attempts: list[dict[str, Any]] = []
        last_error: TransportRetryable | None = None
        for attempt_index in range(route.retry_limit + 1):
            attempt_activation = (
                activation_id if attempt_index == 0 else f"{activation_id}.retry{attempt_index}")
            reservation = self.ledger.reserve(
                activation_id=activation_id, job_id=route.job_id)
            try:
                candidate, receipt = self._attempt(
                    route=route, reservation=reservation,
                    activation_id=attempt_activation, episode_id=episode_id,
                    projection=projection, staged_inputs=staged_inputs,
                    authorization_receipt=authorization_receipt)
            except TransportRetryable as error:
                attempts.append(error.receipt)  # type: ignore[attr-defined]
                last_error = error
                continue
            attempts.append(receipt)
            return TransportResult(candidate=candidate, receipt=receipt,
                                   attempts=tuple(attempts))
        assert last_error is not None
        raise last_error

    def _attempt(
        self,
        *,
        route: JobRoute,
        reservation: AttemptReservation,
        activation_id: str,
        episode_id: str,
        projection: Mapping[str, Any],
        staged_inputs: Sequence[StagedInput],
        authorization_receipt: Mapping[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        executable = self.executable(route.cli)
        workspace = stage_workspace(
            output_root=self.output_root, episode_id=episode_id, activation_id=activation_id,
            route=route, projection=projection, authorization_receipt=authorization_receipt,
            staged_inputs=staged_inputs)
        instruction = (workspace.path / route.prompt).read_text(encoding="utf-8")
        argv = build_job_argv(route, workspace=workspace.path, instruction=instruction)
        profile_path = workspace.home / "profile.sb"
        profile_path.write_text(
            render_sandbox_profile(
                workspace=workspace.path, home=workspace.home,
                readable=executable_read_roots(executable.path)),
            encoding="utf-8")
        sandboxed = build_sandboxed_argv(argv, profile_path=profile_path)
        environment = build_worker_environment(
            home=workspace.home, passthrough=self.env_passthrough)

        started = utc_now()
        monotonic = time.monotonic()
        outcome = self.runner(
            sandboxed, cwd=workspace.path, env=environment,
            timeout_seconds=route.timeout_seconds)
        ended = utc_now()

        evidence_dir = self.evidence_root / episode_id / activation_id
        evidence_dir.mkdir(parents=True, exist_ok=True)
        stdout_path = evidence_dir / "stdout.txt"
        stderr_path = evidence_dir / "stderr.txt"
        stdout_path.write_text(outcome.stdout, encoding="utf-8")
        stderr_path.write_text(outcome.stderr, encoding="utf-8")

        receipt: dict[str, Any] = {
            "activation_id": activation_id,
            "attempt_ordinal": reservation.attempt_ordinal,
            "reservation_id": reservation.reservation_id,
            "job_id": route.job_id,
            "job_type": route.job_type,
            "decided_family": route.family,
            "decided_model": route.model,
            "decided_reasoning_effort": route.reasoning_effort,
            "observed_family": None,
            "observed_model": None,
            "observed_identity_source": None,
            "executable_path": executable.path,
            "executable_sha256": executable.sha256,
            "executable_version": executable.version,
            "redacted_command": redact_command(sandboxed),
            "returncode": outcome.returncode,
            "pid": outcome.pid,
            "started_utc": started.isoformat(),
            "ended_utc": ended.isoformat(),
            "duration_seconds": round(time.monotonic() - monotonic, 6),
            "timeout_seconds": route.timeout_seconds,
            "termination": outcome.termination,
            "workspace_path": str(workspace.path),
            "authorized_input_sha256": workspace.input_sha256,
            "output_schema_sha256": workspace.schema_sha256,
            "prompt_sha256": workspace.prompt_sha256,
            "staged_input_sha256": dict(workspace.staged_sha256),
            "result_sha256": None,
            "stdout_evidence_path": str(stdout_path),
            "stderr_evidence_path": str(stderr_path),
            "stdout_sha256": sha256_bytes(outcome.stdout.encode("utf-8")),
            "stderr_sha256": sha256_bytes(outcome.stderr.encode("utf-8")),
            "sandbox_mechanism": sandbox_mechanism(),
            "authorization_receipt_id": str(authorization_receipt["receipt_id"]),
            "outcome": "transport_failure",
            "failure_class": None,
            "failure_detail": None,
            "workspace_inventory_before": sorted(workspace.baseline),
            "workspace_inventory_after": sorted(workspace.inventory()),
        }

        try:
            if outcome.termination in {"timeout_term", "timeout_kill"}:
                raise TransportRetryable("timeout", outcome.termination)
            if outcome.returncode != 0:
                raise TransportRetryable("nonzero_exit", str(outcome.returncode))
            observed = observe_identity(route, stdout=outcome.stdout)
            receipt["observed_family"] = observed.family
            receipt["observed_model"] = observed.model
            receipt["observed_identity_source"] = (
                f"{observed.model_source}|{observed.family_source}")
            assert_identity_matches(route, observed)
            candidate, source = load_candidate(
                route, workspace=workspace.path, stdout=outcome.stdout,
                schema=load_output_schema(route))
            workspace.assert_no_undeclared_writes(permitted_new=("result.json",))
        except TransportError as error:
            receipt["failure_class"] = getattr(error, "failure_class", type(error).__name__)
            receipt["failure_detail"] = str(error)[:2000]
            receipt["workspace_inventory_after"] = sorted(workspace.inventory())
            self._finalize(receipt, workspace)
            if isinstance(error, TransportRetryable):
                error.receipt = receipt  # type: ignore[attr-defined]
            raise

        result_path = workspace.path / "result.json"
        receipt["result_sha256"] = (
            sha256_file(result_path) if result_path.is_file()
            else sha256_bytes(canonical_json(candidate).encode("utf-8")))
        receipt["observed_identity_source"] = f"{receipt['observed_identity_source']}|{source}"
        receipt["outcome"] = "candidate_produced"
        receipt["workspace_inventory_after"] = sorted(workspace.inventory())
        self._finalize(receipt, workspace)
        return candidate, receipt

    def _finalize(self, receipt: dict[str, Any], workspace: Workspace) -> None:
        self._receipt_validator.validate(receipt)
        if not self.keep_workspaces:
            workspace.destroy()


class FakeCliTransport:
    """Test-only transport.

    It refuses any root outside the system temporary directory and validates its canned
    responses against the real job schema, so it can neither touch a product root nor
    return a field that could be read as a terminal.
    """

    def __init__(
        self,
        *,
        sandbox_root: Path | str,
        responses: Mapping[str, Mapping[str, Any]],
        registry: Mapping[str, JobRoute] | None = None,
    ) -> None:
        root = Path(sandbox_root).resolve()
        temp_root = Path(tempfile.gettempdir()).resolve()
        if not root.is_relative_to(temp_root):
            raise TransportError(
                f"fake transport root must live under {temp_root}, got {root}")
        if root == REPO_ROOT or REPO_ROOT in root.parents or root.is_relative_to(REPO_ROOT):
            raise TransportError("fake transport must not address a product root")
        self.sandbox_root = root
        self.responses = {job: dict(payload) for job, payload in responses.items()}
        self.registry = registry if registry is not None else load_job_registry()

    def execute(self, *, job_id: str, activation_id: str, **_: Any) -> TransportResult:
        route = resolve_route(job_id, self.registry)
        candidate = self.responses.get(job_id)
        if candidate is None:
            raise RouteRejected(f"fake transport has no canned response for {job_id}")
        jsonschema.Draft202012Validator(load_output_schema(route)).validate(candidate)
        assert_no_authoritative_fields(candidate, label=f"fake {job_id} candidate")
        receipt = {
            "activation_id": activation_id,
            "job_id": route.job_id,
            "decided_model": route.model,
            "decided_family": route.family,
            "observed_identity_source": "fake_transport",
            "outcome": "candidate_produced",
            "sandbox_mechanism": "fake_transport_no_process",
        }
        return TransportResult(candidate=dict(candidate), receipt=receipt, attempts=(receipt,))
