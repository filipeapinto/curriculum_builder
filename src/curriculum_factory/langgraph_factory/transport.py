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
import shlex
import shutil
import signal
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import jsonschema
import yaml

from .. import checks, pdf_inspect, visual_maps
from .. import resources as package_resources
from .. import roots
from ..pdf_inspect import MIN_POINT_SIZE
from .artifacts import UNIT_SCOPE, ArtifactStore, ArtifactStream, canonical_digest
from .egress import (
    AuthorizationDenied,
    AuthorizationRecord,
    EgressGuard,
    ReceiptLog,
    authorize_subprocess_transmission,
    canonical_json,
    utc_now,
)

# Package-owned resources, addressed through importlib.resources rather than through
# this module's own __file__. On an ordinary unpacked wheel these are Paths and behave
# exactly as before; on a zipped or otherwise non-filesystem distribution they are
# Traversables, and every read below goes through an API that accepts one.
PACKAGE_ROOT = package_resources.package_root()
REGISTRY_PATH = package_resources.config_dir() / "model_jobs.v1.yaml"
SCHEMA_DIR = package_resources.schema_dir()
PROMPT_DIR = package_resources.prompt_dir()

# There is deliberately no REPO_ROOT here. It used to be PACKAGE_ROOT.parents[1], which
# is site-packages once this package is really installed. Repository-owned data is
# reached through curriculum_factory.roots, from a root the caller supplies.

AUTHORING_FAMILY = "anthropic"
REVIEW_FAMILY = "openai"

CLAUDE_PERMITTED_TOOLS = frozenset({"StructuredOutput"})

RESERVED_WORKSPACE_NAMES = frozenset({
    "authorized_input.json", "output.schema.json", "result.json",
    "cli_schema_projection.json",
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


def _read_resource_text(source: Any) -> str:
    """Read a package resource or a filesystem path, whichever the caller has.

    A Traversable and a Path both answer ``read_text``; only a Path can be handed to
    ``Path()``. Preferring the shared method is what lets the same code work when the
    distribution is not an unpacked directory.
    """
    reader = getattr(source, "read_text", None)
    if reader is None:
        return Path(source).read_text(encoding="utf-8")
    return reader(encoding="utf-8")


def _load_json(path: Any) -> dict[str, Any]:
    return json.loads(_read_resource_text(path))


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


_REGISTRY_CACHE: dict[str, Mapping[str, JobRoute]] = {}


def load_job_registry(path: Any = None) -> Mapping[str, JobRoute]:
    """The model job registry: the package's own by default, or an explicit file.

    The default is read as a package resource, not as a path derived from this
    module's location.
    """
    source = REGISTRY_PATH if path is None else path
    resolved = source if hasattr(source, "read_text") else Path(source).resolve()
    cache_key = str(resolved)
    if cache_key in _REGISTRY_CACHE:
        return _REGISTRY_CACHE[cache_key]
    document = yaml.safe_load(_read_resource_text(resolved))
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
        if route.cli not in {"codex", "claude"}:
            raise RouteRejected(f"unknown cli for {route.job_id}: {route.cli}")
        if route.cli == "claude" and route.family != AUTHORING_FAMILY:
            raise RouteRejected(f"claude route {route.job_id} must be family {AUTHORING_FAMILY}")
        if route.cli == "codex" and route.family != REVIEW_FAMILY:
            raise RouteRejected(f"codex route {route.job_id} must be family {REVIEW_FAMILY}")
        if route.job_id in routes:
            raise RouteRejected(f"duplicate job id {route.job_id}")
        routes[route.job_id] = route
    _REGISTRY_CACHE[cache_key] = routes
    return routes


def resolve_route(job_id: str, registry: Mapping[str, JobRoute] | None = None) -> JobRoute:
    routes = registry if registry is not None else load_job_registry()
    try:
        return routes[job_id]
    except KeyError:
        raise RouteRejected(f"unknown job id: {job_id!r}") from None


def _resolve_package_entry(directory: Any, name: str, label: str) -> Any:
    """One entry inside a package resource directory, containment-checked.

    The name must be bare. Rejecting a separator or a parent reference outright is
    what keeps a route from addressing anything outside the shipped directory, and it
    is a check that works on a Traversable, where there is no `.parent` to compare.
    """
    try:
        return package_resources._child(directory, name, label)
    except package_resources.ResourceError as error:
        raise RouteRejected(str(error)) from None


def resolve_prompt_path(route: JobRoute) -> Any:
    """The route's prompt, as a package resource -- never relative to the cwd."""
    return _resolve_package_entry(PROMPT_DIR, route.prompt, "prompt")


def resolve_schema_path(route: JobRoute) -> Any:
    return _resolve_package_entry(SCHEMA_DIR, route.schema, "schema")


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
    """The pinned Codex invocation (spec 7.3), corrected for observable identity (N30V7-F05).

    `--json` is not decoration: the JSONL event stream is the transport-isolation
    proof channel. But live evidence against the genuinely installed CLI (codex-cli
    0.147.0, N30V7-F05) proved that stream's `thread.started`/`turn.started`/
    `item.completed`/`turn.completed` events never carry a `model` field on any
    variant -- `--ephemeral`'s own on-disk rollout file is the only machine-readable
    Codex receipt that does (`turn_context.payload.model`, spec 7.3's "machine-readable
    Codex event/receipt"). `--ephemeral` is therefore dropped: every caller already runs
    this inside a disposable, per-activation `$CODEX_HOME` (`build_worker_environment`)
    or, for the driver-capability preflight probe, the operator's own real,
    already-authenticated `$CODEX_HOME` (`_probe_env`, by the same design that already
    accepted the real environment for that probe) -- so the rollout file this write adds
    is bounded to one of those two homes, never a shared, uncontrolled location.
    """
    return [
        "codex", "exec", "--ignore-user-config", "--ignore-rules",
        "-s", "read-only", "--skip-git-repo-check", "-C", str(workspace),
        "-m", model, "-c", f'model_reasoning_effort="{reasoning_effort}"',
        "--output-schema", "output.schema.json", "-o", "result.json",
        "--json", instruction,
    ]


def build_claude_argv(
    *,
    workspace: Path | str,
    model: str,
    effort: str,
    cli_schema_projection: Mapping[str, Any],
    tools: str = "",
) -> list[str]:
    """The pinned Claude invocation (spec 7.2).

    No positional instruction: `--tools ""` leaves the worker no file-reading tool, so
    the instruction and the authorized-input projection are delivered together on
    stdin (`build_claude_stdin_payload`), never as an argv token or a staged file the
    worker would have to open. `--json-schema` takes the CLI-schema projection inline
    as JSON text, not a file path — a live probe against the installed CLI proved a
    bare path argument and the canonical schema's own `$schema` dialect reference are
    both rejected (spec 7.2, N20-F03).

    `tools` defaults to empty (no change to every other job's contract). The one
    named exception is M01's `discover` phase (spec decision, N20V7-F13): it is
    dispatched with `tools="WebSearch"` so the worker can find and verify real
    candidate source locators instead of refusing outright when it has no way to
    confirm a URL exists. WebSearch is Claude Code's own built-in, subscription-
    authenticated tool -- it never touches this sandbox's file system or egress
    guard; the worker still cannot write a file (`--tools` grants nothing else),
    and `SourceRetriever` (egress.py) remains the only path that ever fetches,
    validates, hashes, or receipts source bytes. Every other job keeps `tools=""`.

    Permission mode tracks the same grant: `--permission-mode plan` (every other
    job) blocks tool execution outright even when a tool is named in `--tools` --
    live-verified (N20V7-F13): the worker refused to search at all, citing plan
    mode. `default` mode still headless-denies every call (no TTY to approve a
    prompt) -- also live-verified. `bypassPermissions` is the one mode that lets
    an already-`--tools`-restricted worker actually use the single tool it was
    granted without a prompt neither side can answer; it grants nothing `--tools`
    did not already name, so it is used only alongside a non-empty `tools`.
    """
    return [
        "claude", "--print",
        "--output-format", "stream-json", "--verbose",
        "--json-schema", canonical_json(dict(cli_schema_projection)),
        "--model", model, "--effort", effort,
        "--permission-mode", ("bypassPermissions" if tools else "plan"),
        "--tools", tools,
        "--add-dir", str(workspace),
        "--no-session-persistence",
        "--setting-sources", "",
    ]


def build_job_argv(
    route: JobRoute,
    *,
    workspace: Path,
    instruction: str | None = None,
    cli_schema_projection: Mapping[str, Any] | None = None,
    tools: str = "",
) -> list[str]:
    if route.cli == "codex":
        if instruction is None:
            raise RouteRejected(f"{route.job_id}: codex requires an instruction argument")
        return build_codex_argv(workspace=workspace, model=route.model,
                                reasoning_effort=route.reasoning_effort,
                                instruction=instruction)
    if cli_schema_projection is None:
        raise RouteRejected(f"{route.job_id}: claude requires a cli_schema_projection")
    return build_claude_argv(workspace=workspace, model=route.model,
                             effort=route.reasoning_effort,
                             cli_schema_projection=cli_schema_projection,
                             tools=tools)


def build_cli_schema_projection(schema: Mapping[str, Any]) -> dict[str, Any]:
    """The deterministic CLI-schema projection `--json-schema` actually accepts (spec 7.2).

    Strips `$schema` and any other dialect metadata the CLI's schema parameter does not
    accept, and rejects — never silently drops — an external `$ref` (one that does not
    resolve inside the document itself), since a silently dropped external reference
    would change validation semantics the canonical schema expresses. Pure function of
    the input schema, so two calls on the same canonical schema produce byte-identical
    output once serialized by `canonical_json`.
    """

    def _walk(node: Any, *, path: str) -> Any:
        if isinstance(node, Mapping):
            projected: dict[str, Any] = {}
            for key, value in node.items():
                if key == "$schema":
                    continue
                if key == "$ref":
                    if not (isinstance(value, str) and value.startswith("#")):
                        raise TransportError(
                            f"cli schema projection: external $ref not permitted at "
                            f"{path}: {value!r}")
                projected[key] = _walk(value, path=f"{path}/{key}")
            return projected
        if isinstance(node, list):
            return [_walk(item, path=f"{path}[{index}]") for index, item in enumerate(node)]
        return node

    return _walk(dict(schema), path="$")


def build_claude_stdin_payload(
    *,
    instruction: str,
    projection: Mapping[str, Any],
    verified_staged_inputs: Sequence[Mapping[str, Any]] = (),
) -> str:
    """The JSON-encoded `{instruction, authorized_input_projection}` document (spec 7.2).

    The same canonical projection also staged to `authorized_input.json` for durable
    receipt/audit hashing, delivered here on stdin because `--tools ""` leaves the
    Claude worker no file-reading tool to open that staged file with.
    """

    payload: dict[str, Any] = {
        "instruction": instruction,
        "authorized_input_projection": dict(projection),
    }
    if verified_staged_inputs:
        payload["verified_staged_inputs"] = [dict(item) for item in verified_staged_inputs]
    return canonical_json(payload)


def redact_command(argv: Sequence[str]) -> list[str]:
    """Redact any long token, not only the last one.

    Codex's instruction is the final argv token, but Claude's inline CLI-schema
    projection (`--json-schema <text>`) is not last, so redaction cannot assume
    position; any token long enough to carry instruction or schema content is
    redacted by its own hash instead.
    """
    redacted: list[str] = []
    for token in argv:
        if len(token) > 200:
            redacted.append(f"<redacted:{sha256_bytes(token.encode())[:16]}>")
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


def _cli_runtime_scratch_rule() -> str:
    """The Claude Code CLI's own per-UID coordination directory (`/tmp/claude-<uid>`).

    Live-verified (N70): the installed `claude` binary always touches this path on
    startup regardless of `$HOME`/`$TMPDIR` -- it is not workspace content and carries
    no curriculum data, but under this profile's `(deny default)` it is unreachable,
    and a concurrent fan-out of sandboxed launches reproducibly (not merely rarely)
    turned that into a fatal `EPERM` for some fraction of them. `/tmp` is itself a
    symlink to `/private/tmp` on macOS, so both forms are named (`_subpath_rules`'
    existing literal+resolved convention) -- sandbox-exec's own `subpath` matching is
    resolved-path-sensitive and silently would not have matched the symlink form alone.
    """
    return _subpath_rules([Path(f"/tmp/claude-{os.getuid()}")])


# The macOS system services genuinely needed to complete a Keychain item lookup
# (unlock + ACL check + certificate trust evaluation for the TLS handshake that
# follows) -- named individually rather than a blanket `(allow mach-lookup)`,
# live-verified (N70/N20 recovery) as the exact, narrow set sufficient for the
# real installed `claude` CLI's own subscription OAuth lookup.
_KEYCHAIN_MACH_SERVICES = (
    "com.apple.SecurityServer",
    "com.apple.securityd",
    "com.apple.trustd",
    "com.apple.trustd.agent",
    "com.apple.ocspd",
)


def _keychain_access_rule() -> str:
    """Read-only reach to the operator's real login keychain, plus the narrow
    mach-lookup set that completes an OAuth item fetch through it.

    Never the operator's `$HOME`: the isolated worker's own `$HOME` still points at
    its disposable per-activation directory (`build_worker_environment`); this is
    the one, single, explicitly-named exception, and it grants no read access to
    curriculum-unrelated files -- `~/Library/Keychains` is an encrypted database
    macOS itself still gates per-item by requesting-process ACL and Keychain
    unlock state (`security find-generic-password`, live-verified), not a plaintext
    credential this sandbox rule alone exposes.
    """
    keychains = _subpath_rules([Path.home() / "Library" / "Keychains"])
    services = " ".join(f'(global-name "{name}")' for name in _KEYCHAIN_MACH_SERVICES)
    return f"(allow file-read* {keychains})\n(allow mach-lookup {services})\n"


def _codex_auth_file_rule() -> str:
    """Read-only reach to the one real file `codex_auth_provision` symlinks in.

    sandbox-exec's own `subpath` matching resolves symlinks to their target before
    checking access (live-verified: the isolated `$CODEX_HOME`'s own `writable`
    rule did not cover this, since the symlink's *target* sits outside `home`), so
    the profile must name the real, operator-home file explicitly -- scoped to the
    one file, never the whole `~/.codex/` tree (which also holds unrelated session
    history this sandbox has no reason to read).
    """
    return f"(allow file-read* {_subpath_rules([Path.home() / '.codex' / 'auth.json'])})\n"


def claude_auth_provision(home: Path, *, real_home: Path | None = None) -> bool:
    """Give an isolated per-activation `home` the minimal, non-content-bearing local
    state the installed Claude Code CLI needs to recognize an already-authorized
    subscription account and complete the real macOS Keychain OAuth lookup for it.

    Never an API key, never the operator's full `$HOME`: this copies only the four
    fields (`oauthAccount`, `userID`, `hasCompletedOnboarding`, `autoUpdates`) the
    live-verified minimal-config path needs out of the operator's real
    `~/.claude.json` -- never its `projects`/history/session content -- and links
    (never copies) `~/Library/Keychains` read-only so the actual OAuth secret is
    still resolved through the real, ACL-gated Keychain item, never duplicated to
    disk. Returns ``False`` (a legitimate, honest "not provisioned", not an error)
    when the operator's own machine has no real subscription config to draw from --
    the sandboxed CLI then genuinely reports not logged in, exactly as it should.

    `real_home` defaults to `Path.home()`; a test may point it at a synthetic
    directory to prove the copy/link behavior without touching the operator's own
    real account state.
    """
    real_home = Path(real_home) if real_home is not None else Path.home()
    real_config = real_home / ".claude.json"
    if not real_config.is_file():
        return False
    try:
        data = json.loads(real_config.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, Mapping):
        return False
    oauth_account = data.get("oauthAccount")
    user_id = data.get("userID")
    if not isinstance(oauth_account, Mapping) or not isinstance(user_id, str) or not user_id:
        return False
    minimal = {
        "oauthAccount": dict(oauth_account),
        "userID": user_id,
        "hasCompletedOnboarding": True,
        "autoUpdates": False,
    }
    home = Path(home)
    (home / ".claude.json").write_text(canonical_json(minimal), encoding="utf-8")
    real_keychains = real_home / "Library" / "Keychains"
    if real_keychains.is_dir():
        library_dir = home / "Library"
        library_dir.mkdir(exist_ok=True)
        link_path = library_dir / "Keychains"
        if not link_path.exists():
            link_path.symlink_to(real_keychains)
    return True


def codex_auth_provision(codex_home: Path, *, real_codex_home: Path | None = None) -> bool:
    """Give an isolated per-activation `$CODEX_HOME` reach to the operator's existing
    Codex CLI subscription session -- never a fresh API key, never the operator's
    full `$HOME`.

    Materially different from `claude_auth_provision`: the installed Codex CLI's own
    subscription auth is not macOS-Keychain-mediated at all -- its ChatGPT OAuth
    session (`auth_mode: "chatgpt"`) lives as a bearer token directly inside
    `~/.codex/auth.json` (mode 0600), which is itself the credential, not a local
    pointer to one an OS access-control layer still gates per read. This still never
    copies the token to a new location (a symlink, resolved fresh on every read, so
    a real token rotation/refresh is reflected rather than silently going stale) and
    still names only this one file -- never `~/.codex/sessions/` or any other real
    Codex CLI state -- but the isolated `$CODEX_HOME` that receives it must remain
    exactly as disposable and workspace-scoped as it already is; this function grants
    no broader reach than that one link.
    """
    real_codex_home = Path(real_codex_home) if real_codex_home is not None else Path.home() / ".codex"
    real_auth = real_codex_home / "auth.json"
    if not real_auth.is_file():
        return False
    codex_home = Path(codex_home)
    codex_home.mkdir(parents=True, exist_ok=True)
    link_path = codex_home / "auth.json"
    if not link_path.exists():
        link_path.symlink_to(real_auth)
    return True


def render_sandbox_profile(
    *,
    workspace: Path,
    home: Path,
    readable: Sequence[Path] = (),
    allow_network: bool = True,
    metadata_denied: Sequence[Path] = (),
    model_cli_support: bool = True,
    workspace_writable: bool = True,
    allow_process_fork: bool = True,
) -> str:
    """Render a deny-by-default macOS sandbox profile.

    macOS process bootstrap requires broad metadata discovery. A deterministic
    verifier therefore runs a staged frozen snapshot outside the engine and
    denies all metadata under the engine repository. Subscription model CLIs
    additionally receive their narrowly named authentication and scratch rules.
    """
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
        "(allow process-exec*)",
        "(allow sysctl-read)",
        "(allow signal (target self))",
        "(allow file-read-metadata)",
    ]
    if allow_process_fork:
        lines.append("(allow process-fork)")
    if model_cli_support:
        lines.extend([
            f"(allow file-read* file-write* {_cli_runtime_scratch_rule()})",
            _keychain_access_rule(),
            _codex_auth_file_rule(),
        ])
    if metadata_denied:
        lines.append(
            f"(deny file-read-metadata (require-any {_subpath_rules(metadata_denied)}))"
        )
    if readable_rule:
        lines.append(f"(allow file-read* {readable_rule})")
    operation = "file-read* file-write*" if workspace_writable else "file-read*"
    lines.append(f"(allow {operation} {writable})")
    return "\n".join(lines) + "\n" + network


def domain_verifier_work_root(*, engine_root: Path, output_root: Path) -> Path:
    """A stable verifier namespace outside both the engine and its output tree."""

    engine = Path(engine_root).resolve()
    output = Path(output_root).resolve()
    namespace = sha256_bytes(str(output).encode("utf-8"))
    root = (
        Path(tempfile.gettempdir()).resolve()
        / "curriculum_factory_domain_verifier"
        / namespace
    ).resolve()
    if root == engine or engine in root.parents:
        raise VerifierFault(
            f"system temporary verifier root is inside the engine namespace: {root}")
    if root == output or output in root.parents:
        raise VerifierFault(
            f"system temporary verifier root is inside the output namespace: {root}")
    return root


VERIFIER_RUNTIME_MARKER = "__RUN27_VERIFIER_RUNTIME_MANIFEST__:"


VERIFIER_GUARD_SOURCE = r'''from __future__ import annotations
import builtins
import errno
import hashlib
import io
import json
import os
import posix
import runpy
import sys

if len(sys.argv) < 3:
    raise SystemExit("verifier-guard: expected DENIED_ROOT ENTRY [ARGS...]")

_DENIED_ROOT = os.path.normpath(os.path.abspath(sys.argv[1]))
_ENTRY = os.path.normpath(os.path.abspath(sys.argv[2]))
_VERIFIER_ARGS = list(sys.argv[3:])

def _normalized(path):
    if isinstance(path, int):
        return None
    try:
        value = os.fsdecode(path)
    except TypeError:
        return None
    if not os.path.isabs(value):
        value = os.path.join(os.getcwd(), value)
    return os.path.normpath(value)

def _under_denied(path):
    value = _normalized(path)
    return value is not None and (
        value == _DENIED_ROOT or value.startswith(_DENIED_ROOT + os.sep)
    )

def _missing(path):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), os.fspath(path))

_real_open = builtins.open
_real_io_open = io.open
_real_os_open = os.open
_real_stat = os.stat
_real_lstat = os.lstat
_real_listdir = os.listdir
_real_scandir = os.scandir
_real_readlink = os.readlink
_real_access = os.access
_RUNTIME_MARKER = "__RUN27_VERIFIER_RUNTIME_MANIFEST__:"

def _runtime_manifest():
    records = []
    seen = set()
    for name, module in sorted(sys.modules.items()):
        raw_path = getattr(module, "__file__", None)
        if not raw_path:
            continue
        path = os.path.realpath(os.fsdecode(raw_path))
        identity = (name, path)
        if identity in seen:
            continue
        seen.add(identity)
        try:
            with _real_open(path, "rb") as stream:
                digest = hashlib.sha256(stream.read()).hexdigest()
        except OSError as error:
            records.append({"module": name, "path": path, "error": repr(error)})
        else:
            records.append({"module": name, "path": path, "sha256": digest})
    return records

def _blocked_process(*args, **kwargs):
    raise PermissionError(errno.EPERM, "verifier child-process execution is forbidden")

def guarded_open(path, *args, **kwargs):
    if _under_denied(path):
        _missing(path)
    return _real_open(path, *args, **kwargs)

def guarded_io_open(path, *args, **kwargs):
    if _under_denied(path):
        _missing(path)
    return _real_io_open(path, *args, **kwargs)

def guarded_os_open(path, *args, **kwargs):
    if _under_denied(path):
        _missing(path)
    return _real_os_open(path, *args, **kwargs)

def guarded_stat(path, *args, **kwargs):
    if _under_denied(path):
        _missing(path)
    return _real_stat(path, *args, **kwargs)

def guarded_lstat(path, *args, **kwargs):
    if _under_denied(path):
        _missing(path)
    return _real_lstat(path, *args, **kwargs)

def guarded_listdir(path="."):
    if _under_denied(path):
        _missing(path)
    return _real_listdir(path)

def guarded_scandir(path="."):
    if _under_denied(path):
        _missing(path)
    return _real_scandir(path)

def guarded_readlink(path, *args, **kwargs):
    if _under_denied(path):
        _missing(path)
    return _real_readlink(path, *args, **kwargs)

def _guard_one_path(real):
    def guarded(path, *args, **kwargs):
        if _under_denied(path):
            _missing(path)
        return real(path, *args, **kwargs)
    return guarded

def _guard_two_paths(real):
    def guarded(source, destination, *args, **kwargs):
        if _under_denied(source):
            _missing(source)
        if _under_denied(destination):
            _missing(destination)
        return real(source, destination, *args, **kwargs)
    return guarded

builtins.open = guarded_open
io.open = guarded_io_open
os.open = guarded_os_open
os.stat = guarded_stat
os.lstat = guarded_lstat
os.listdir = guarded_listdir
os.scandir = guarded_scandir
os.readlink = guarded_readlink
os.access = lambda path, *args, **kwargs: False if _under_denied(path) else _real_access(path, *args, **kwargs)
posix.open = guarded_os_open
posix.stat = guarded_stat
posix.lstat = guarded_lstat
posix.listdir = guarded_listdir
posix.scandir = guarded_scandir
posix.readlink = guarded_readlink
for _module in (os, posix):
    for _name in (
        "chdir", "chmod", "lchmod", "chown", "lchown", "truncate", "unlink", "remove",
        "rmdir", "mkdir", "statvfs", "pathconf", "chflags", "lchflags",
        "getxattr", "listxattr", "removexattr", "setxattr", "chroot",
        "utime", "mkfifo", "mknod",
    ):
        _real = getattr(_module, _name, None)
        if _real is not None:
            setattr(_module, _name, _guard_one_path(_real))
    for _name in ("rename", "replace", "link", "symlink"):
        _real = getattr(_module, _name, None)
        if _real is not None:
            setattr(_module, _name, _guard_two_paths(_real))
for _module in (os, posix):
    for _name in dir(_module):
        if _name == "system" or _name == "popen" or _name.startswith("exec") or _name.startswith("spawn"):
            setattr(_module, _name, _blocked_process)

sys.argv = [_ENTRY, *_VERIFIER_ARGS]
try:
    runpy.run_path(_ENTRY, run_name="__main__")
finally:
    print(
        _RUNTIME_MARKER
        + json.dumps(_runtime_manifest(), sort_keys=True, separators=(",", ":")),
        file=sys.stderr,
    )
'''


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

    # sandbox-exec occasionally returns a transient bootstrap failure on a busy
    # host before evaluating the profile. Repeat only the positive staged-file
    # probe; forbidden-path probes are never retried into success and therefore
    # cannot be weakened by this availability tolerance.
    inside_attempts: list[Any] = []
    for _attempt in range(3):
        inside = run(
            ["/usr/bin/sandbox-exec", "-f", str(profile_path), "/bin/cat", str(probe_file)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        inside_attempts.append(inside)
        if inside.returncode == 0:
            break
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
            f"staged attempts={len(inside_attempts)}; "
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
    required_flags = {"codex": "--json", "claude": "--json-schema"}
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
            "mechanism": (
                "codex --json JSONL events; claude --output-format stream-json --verbose "
                "per-turn assistant message.model"),
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


def resolve_codex_home(env: Mapping[str, str]) -> Path:
    """The `$CODEX_HOME` a codex invocation under this exact `env` actually resolves to.

    Mirrors the installed CLI's own precedence: an explicit `CODEX_HOME` wins; absent
    that, it falls back to `$HOME/.codex`.
    """
    codex_home = env.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home)
    home = env.get("HOME") or str(Path.home())
    return Path(home) / ".codex"


def _codex_thread_id(event_stream: str) -> str | None:
    """The `thread_id` this exact `--json` stdout named, or ``None`` if it never did."""
    for line in event_stream.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, Mapping) and event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
            if isinstance(thread_id, str) and thread_id:
                return thread_id
    return None


def _rollout_session_id(path: Path) -> str | None:
    """The rollout file's own declared session id, from its leading `session_meta` line."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            first = handle.readline().strip()
    except OSError:
        return None
    if not first.startswith("{"):
        return None
    try:
        event = json.loads(first)
    except json.JSONDecodeError:
        return None
    if not isinstance(event, Mapping) or event.get("type") != "session_meta":
        return None
    payload = event.get("payload")
    if not isinstance(payload, Mapping):
        return None
    session_id = payload.get("session_id")
    return session_id if isinstance(session_id, str) and session_id else None


def _rollout_files_for_thread(codex_home: Path, thread_id: str) -> list[Path]:
    sessions_root = Path(codex_home) / "sessions"
    if not sessions_root.is_dir():
        return []
    return sorted(
        path for path in sessions_root.glob("**/rollout-*.jsonl")
        if path.is_file() and _rollout_session_id(path) == thread_id)


def _final_rollout_identity(path: Path) -> tuple[str | None, str | None]:
    """The last `turn_context.model` in the file (reroute supersedes initial), plus provider."""
    model: str | None = None
    provider: str | None = None
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, Mapping):
                continue
            payload = event.get("payload")
            if not isinstance(payload, Mapping):
                continue
            event_type = event.get("type")
            if event_type == "session_meta":
                observed_provider = payload.get("model_provider")
                if isinstance(observed_provider, str) and observed_provider:
                    provider = observed_provider
            elif event_type == "turn_context":
                observed_model = payload.get("model")
                if isinstance(observed_model, str) and observed_model:
                    model = observed_model
    return model, provider


def observe_codex_identity(event_stream: str, *, codex_home: Path) -> ObservedIdentity:
    """Read the executed model out of *this exact invocation's* on-disk rollout file.

    Live evidence (N30V7-F05, codex-cli 0.147.0) proved the `--json` stdout stream
    itself never carries a `model` field on any event it emits, so copying that stream
    can never satisfy this check -- there is nothing in it to copy. The on-disk rollout
    file `build_codex_argv` now leaves behind (having dropped `--ephemeral`) does carry
    it, in `turn_context.payload.model`.

    `codex_home` is not necessarily private to this one call: a real job's is a fresh,
    disposable per-activation `$CODEX_HOME`, but the driver-capability preflight probe
    deliberately runs against the operator's real, long-lived `~/.codex`, which can hold
    rollout files from unrelated, concurrent, or historical invocations. Matching "the
    newest rollout file" would silently attribute another process's model to this one.
    The only trustworthy key is `thread.started.thread_id` from *this* stdout, matched
    against each candidate file's own `session_meta.payload.session_id`; zero or more
    than one match is refused as an unobservable identity, never guessed.
    """
    thread_id = _codex_thread_id(event_stream)
    if thread_id is None:
        raise IdentityUnobservable(
            "codex event stream never emitted thread.started; no thread_id to bind a "
            "rollout file to, so route conformance cannot be claimed")
    matches = _rollout_files_for_thread(Path(codex_home), thread_id)
    if not matches:
        raise IdentityUnobservable(
            f"no rollout file under {codex_home} matched thread_id {thread_id!r}; "
            "route conformance cannot be claimed")
    if len(matches) > 1:
        raise IdentityUnobservable(
            f"{len(matches)} rollout files under {codex_home} matched thread_id "
            f"{thread_id!r}; refusing an ambiguous identity binding")
    model, provider = _final_rollout_identity(matches[0])
    if not model:
        raise IdentityUnobservable(
            f"rollout file {matches[0]} for thread_id {thread_id!r} names no "
            "turn_context.model; route conformance cannot be claimed")
    return ObservedIdentity(
        family=REVIEW_FAMILY,
        model=model,
        model_source=f"codex_rollout:turn_context.model:{matches[0].name}",
        family_source=(f"codex_rollout:model_provider={provider}" if provider
                        else "executable_identity:codex-cli"),
    )


def _iter_stream_json_events(stream_text: str) -> list[Mapping[str, Any]]:
    events: list[Mapping[str, Any]] = []
    for line in stream_text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, Mapping):
            events.append(event)
    return events


def observe_claude_identity(stream_text: str) -> ObservedIdentity:
    """Read the executed model from the per-turn assistant event's `message.model`.

    Never from the final envelope's aggregate `modelUsage` map: a live probe against
    the installed CLI (2.1.231) proved that map is not guaranteed single-entry (a
    probe recorded `claude-haiku-4-5-20251001` alongside the requested
    `claude-sonnet-5`), so it cannot be the identity source (spec 7.2, N20-F05). The
    per-turn assistant event with `parent_tool_use_id` null is the unambiguous signal;
    the last such event wins, matching Codex's reroute-supersedes-initial rule.
    """
    model: str | None = None
    for event in _iter_stream_json_events(stream_text):
        if event.get("type") != "assistant":
            continue
        if event.get("parent_tool_use_id") is not None:
            continue
        message = event.get("message")
        if not isinstance(message, Mapping):
            continue
        observed = message.get("model")
        if isinstance(observed, str) and observed:
            model = observed
    if not model:
        raise IdentityUnobservable(
            "claude stream-json output names no per-turn assistant message.model "
            "(parent_tool_use_id null); route conformance cannot be claimed")
    return ObservedIdentity(
        family=AUTHORING_FAMILY,
        model=model,
        model_source="claude_stream_json:assistant.message.model",
        family_source="executable_identity:claude-cli",
    )


def observe_identity(route: JobRoute, *, stdout: str, codex_home: Path | None = None) -> ObservedIdentity:
    if route.cli == "codex":
        if codex_home is None:
            raise IdentityUnobservable(
                f"{route.job_id}: codex identity observation requires codex_home")
        return observe_codex_identity(stdout, codex_home=codex_home)
    return observe_claude_identity(stdout)


def prove_claude_tool_closure(
    stream_text: str, *, permitted_tools: frozenset[str] = CLAUDE_PERMITTED_TOOLS,
) -> dict[str, Any]:
    """Inspect the stream-json init event's tool/MCP-server lists directly (spec 7.1 class 5).

    Independent of what `--tools`/`--setting-sources` claim: a live probe found
    `--setting-sources ""` still listed three claude.ai MCP servers (all
    `needs-auth`, no tool) in the init event (N20-F06). Closure requires no tool
    beyond the permitted structured-output channel, and no MCP server whose status
    is not an auth/connection failure (i.e. nothing actually invokable).
    """
    init_event: Mapping[str, Any] | None = None
    for event in _iter_stream_json_events(stream_text):
        if event.get("type") == "system" and event.get("subtype") == "init":
            init_event = event
            break
    if init_event is None:
        raise CapabilityProofFailed(
            "claude stream-json output carries no system/init event; tool/MCP closure "
            "is unproven")
    tools = init_event.get("tools")
    if not isinstance(tools, list):
        raise CapabilityProofFailed("claude init event carries no tools list")
    observed_tools = sorted(str(item) for item in tools)
    extra_tools = sorted(set(observed_tools) - set(permitted_tools))

    mcp_servers = init_event.get("mcp_servers")
    observed_servers = list(mcp_servers) if isinstance(mcp_servers, list) else []
    non_invokable_status = {"needs-auth", "failed", "disconnected", "error"}
    invokable_servers = [
        server for server in observed_servers
        if isinstance(server, Mapping)
        and str(server.get("status", "")).lower() not in non_invokable_status
    ]
    closed = not extra_tools and not invokable_servers
    return {
        "closed": closed,
        "observed_tools": observed_tools,
        "extra_tools": extra_tools,
        "observed_mcp_servers": observed_servers,
        "invokable_mcp_servers": invokable_servers,
    }


def require_claude_tool_closure(closure: Mapping[str, Any]) -> None:
    if not closure.get("closed"):
        raise CapabilityProofFailed(
            f"claude tool/MCP closure unproven: extra_tools={closure.get('extra_tools')} "
            f"invokable_mcp_servers={closure.get('invokable_mcp_servers')}")


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


def extract_claude_structured_output(stdout: str) -> str:
    """One registered deterministic extractor: the final stream-json result event's
    `structured_output` field.

    The only channel available for a Claude job: `--tools ""` leaves the worker no
    file-write tool, so it can never write `result.json` itself.
    """
    result_event: Mapping[str, Any] | None = None
    for event in _iter_stream_json_events(stdout):
        if event.get("type") == "result":
            result_event = event
    if result_event is None:
        raise ResultParseError("no_claude_result_event")
    structured = result_event.get("structured_output")
    if structured is None:
        raise ResultParseError("claude_result_carries_no_structured_output")
    if isinstance(structured, str):
        return structured
    return canonical_json(structured)


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
    elif route.cli == "claude":
        document = extract_claude_structured_output(stdout)
        source = "claude_stream_json_structured_output"
    else:
        raise ResultParseError("no_result_file_and_no_registered_envelope_extractor")
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
    cli_schema_projection_sha256: str | None = None
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
    cli_schema_projection: Mapping[str, Any] | None = None,
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
    if route.cli == "claude":
        claude_auth_provision(home)
    elif route.cli == "codex":
        codex_auth_provision(home / "codex")

    prompt_source = resolve_prompt_path(route)
    schema_source = resolve_schema_path(route)
    schema = _load_json(schema_source)
    assert_no_authoritative_fields(schema, label=f"{route.job_id} output schema")

    payload = {"projection": dict(projection), "authorization_receipt": dict(authorization_receipt)}
    input_path = root / "authorized_input.json"
    input_path.write_text(canonical_json(payload), encoding="utf-8")
    # materialize(), not copyfile(): the source is a package resource, which is only
    # guaranteed to be a real file on an unpacked distribution.
    package_resources.materialize(schema_source, root / "output.schema.json")
    package_resources.materialize(prompt_source, root / route.prompt)

    cli_schema_sha256: str | None = None
    if cli_schema_projection is not None:
        cli_schema_text = canonical_json(dict(cli_schema_projection))
        (root / "cli_schema_projection.json").write_text(cli_schema_text, encoding="utf-8")
        cli_schema_sha256 = sha256_bytes(cli_schema_text.encode("utf-8"))

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
        cli_schema_projection_sha256=cli_schema_sha256,
        staged_sha256=staged_digests,
    )
    workspace.baseline = workspace.inventory()
    return workspace


MAX_VERIFIED_STAGED_TEXT_CHARS = 240_000


class _VisibleHTMLText(HTMLParser):
    """Small deterministic visible-text projection for verified HTML bytes."""

    _BLOCKS = frozenset({
        "article", "aside", "blockquote", "br", "dd", "div", "dl", "dt",
        "figcaption", "figure", "footer", "h1", "h2", "h3", "h4", "h5",
        "h6", "header", "li", "main", "nav", "ol", "p", "pre", "section",
        "table", "tbody", "td", "th", "thead", "tr", "ul",
    })
    _HIDDEN = frozenset({"script", "style", "noscript", "svg", "template"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = tag.lower()
        if normalized in self._HIDDEN:
            self.hidden_depth += 1
        elif self.hidden_depth == 0 and normalized in self._BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        if normalized in self._HIDDEN:
            self.hidden_depth = max(0, self.hidden_depth - 1)
        elif self.hidden_depth == 0 and normalized in self._BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.hidden_depth == 0:
            self.parts.append(data)


def _normalize_staged_text(text: str) -> str:
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    compact: list[str] = []
    for line in lines:
        if line or (compact and compact[-1]):
            compact.append(line)
    return "\n".join(compact).strip()


def extract_verified_staged_text(path: Path) -> tuple[str, str]:
    """Project already hash-verified staged bytes into bounded, model-readable text."""

    raw = path.read_bytes()
    if raw.startswith(b"%PDF-"):
        executable = shutil.which("pdftotext")
        if executable is None:
            raise WorkspaceViolation(
                f"cannot project verified PDF staged input {path.name!r}: pdftotext unavailable")
        completed = subprocess.run(
            [executable, "-layout", str(path), "-"],
            capture_output=True, text=True, timeout=120)
        if completed.returncode != 0:
            raise WorkspaceViolation(
                f"cannot project verified PDF staged input {path.name!r}: "
                f"pdftotext exited {completed.returncode}: {completed.stderr.strip()[:500]}")
        pages = completed.stdout.split("\f")
        text = "\n".join(
            f"--- PAGE {number} ---\n{page}" for number, page in enumerate(pages, start=1)
            if page.strip())
        return _normalize_staged_text(text), "pdf_text"

    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise WorkspaceViolation(
            f"verified staged input {path.name!r} is neither PDF nor UTF-8 text") from error
    if re.search(r"<\s*(?:!doctype\s+html|html|body|article)\b", decoded[:16_384], re.I):
        parser = _VisibleHTMLText()
        parser.feed(decoded)
        parser.close()
        return _normalize_staged_text("".join(parser.parts)), "html_visible_text"
    return _normalize_staged_text(decoded), "utf8_text"


def build_verified_staged_inputs(
    *, workspace: Workspace, staged_inputs: Sequence[StagedInput]
) -> tuple[dict[str, Any], ...]:
    """Make verified staged files readable to a tool-closed Claude invocation.

    The workspace copy has already passed the source SHA-256 check.  The extracted
    text is separately hashed and bounded before it enters the authorized stdin
    document; no host, path, or sibling workspace becomes readable to the worker.
    """

    projected: list[dict[str, Any]] = []
    for item in staged_inputs:
        path = workspace.path / item.name
        if workspace.staged_sha256.get(item.name) != item.sha256:
            raise WorkspaceViolation(
                f"staged input {item.name!r} lacks the verified workspace digest")
        text, text_format = extract_verified_staged_text(path)
        truncated = len(text) > MAX_VERIFIED_STAGED_TEXT_CHARS
        bounded = text[:MAX_VERIFIED_STAGED_TEXT_CHARS]
        projected.append({
            "name": item.name,
            "source_sha256": item.sha256,
            "text_format": text_format,
            "text_sha256": sha256_bytes(bounded.encode("utf-8")),
            "truncated": truncated,
            "text": bounded,
        })
    return tuple(projected)


def build_worker_environment(*, home: Path, passthrough: Sequence[str] = ()) -> dict[str, str]:
    """Allowlisted environment over a dedicated temporary home; secrets pass by name only.

    `USER` is the one identity value carried through unconditionally, not behind
    `passthrough`: it is the real OS username, never a secret (already implicit in
    the process's real UID), but live-verified (N70/N20 recovery) as load-bearing
    for the installed Claude Code CLI's own macOS Keychain OAuth lookup to succeed
    at all under an otherwise fully isolated `$HOME`.
    """
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
    real_user = os.environ.get("USER")
    if real_user:
        environment["USER"] = real_user
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
    stdin: str | None = None,
    term_grace_seconds: float = 5.0,
) -> ProcessOutcome:
    """Process-group wall-clock timeout: TERM, wait five seconds, then KILL.

    `stdin` carries a Claude job's JSON-encoded `{instruction,
    authorized_input_projection}` document (spec 7.2); Codex jobs pass `None` and
    inherit no stdin, matching their existing positional-instruction shape.
    """
    process = subprocess.Popen(
        list(argv), cwd=str(cwd), env=dict(env), text=True,
        stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    termination = "exited"
    try:
        stdout, stderr = process.communicate(input=stdin, timeout=timeout_seconds)
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


# --------------------------------------------------- product capability surface
#
# D03, D11, D13 and D14 reach for five methods on `RuntimeContext.transport_registry`.
# They are capability work, not curriculum work: each does one bounded local job and
# raises on any tool fault, so the calling node classifies it as a system failure
# instead of letting a broken renderer reach the record as a product finding.

RENDER_TOOLS: tuple[str, ...] = ("pandoc", "typst")
RASTER_TOOLS: tuple[str, ...] = ("pdftoppm", "pdfinfo", "pdftotext", "pdfimages")
RENDER_DIRNAME = ".render"

# The nominal type size is recoverable from an ink box by pdf_inspect's constant,
# calibrated against this repository's own pandoc/typst/Helvetica toolchain.
_INK_BOX_RATIO = pdf_inspect._INK_BOX_RATIO
_BLANK_PAGE_RANGE = 2

_PAGE_SIZE_RE = re.compile(r'^width="([\d.]+)" height="([\d.]+)"')
_LINE_BOX_RE = re.compile(
    r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>', re.S)


class RenderFault(TransportError):
    """A renderer, rasterizer, or artifact-store fault. Never a product finding."""


class VerifierFault(TransportError):
    """The frozen curriculum verifier or its fixture proof could not run safely."""


class UnavailableExternalFact(TransportError):
    """A named required external fact no local probe can supply (spec 2.4 item 6)."""

    def __init__(self, fact: str, detail: str = "") -> None:
        super().__init__(f"{fact}: {detail}" if detail else fact)
        self.fact = fact


def rasterize_pages(pdf: Path, directory: Path, *, dpi: int = 200) -> list[Path]:
    """One PNG per shipped page.

    `checks.rasterize_and_check_nonblank` aborts on the first blank page. D14 owes a
    result for *every* page and treats a blank one as a product finding, so the blank
    audit happens per page in `inspect_pages` rather than here.
    """
    if not shutil.which("pdftoppm"):
        raise RenderFault("pdftoppm unavailable; the rasterizer capability is unproven")
    directory.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        ["pdftoppm", "-r", str(dpi), "-png", str(pdf), str(directory / "page")],
        capture_output=True, text=True, timeout=600)
    if completed.returncode != 0:
        raise RenderFault(f"rasterization failed: {completed.stderr.strip()[:500]}")
    pages = sorted(directory.glob("page-*.png"))
    declared = checks.pdf_page_count(pdf)
    if len(pages) != declared:
        raise RenderFault(f"rasterized {len(pages)} page(s) from a {declared}-page PDF")
    return pages


def page_is_blank(image_path: Path) -> bool:
    from PIL import Image

    with Image.open(image_path) as image:
        extrema = image.convert("L").getextrema()
    return extrema is None or (extrema[1] - extrema[0]) <= _BLANK_PAGE_RANGE


def page_text_problems(pdf: Path) -> dict[int, list[str]]:
    """Undersized and clipped text, per page, from one poppler pass.

    `pdf_inspect.text_legible` answers the same question for a whole document; D14's
    denominator is per page, so the same `-bbox-layout` output is split by page here.
    """
    if not shutil.which("pdftotext"):
        raise RenderFault("pdftotext unavailable; page inspection cannot be proven")
    completed = subprocess.run(
        ["pdftotext", "-bbox-layout", str(pdf), "-"],
        capture_output=True, text=True, timeout=600)
    if completed.returncode != 0:
        raise RenderFault(f"pdftotext failed: {completed.stderr.strip()[:500]}")
    problems: dict[int, list[str]] = {}
    for number, chunk in enumerate(completed.stdout.split("<page ")[1:], start=1):
        size = _PAGE_SIZE_RE.match(chunk)
        width = float(size.group(1)) if size else None
        height = float(size.group(2)) if size else None
        found: set[str] = set()
        for match in _LINE_BOX_RE.finditer(chunk):
            x_max, y_min, y_max = float(match.group(3)), float(match.group(2)), float(match.group(4))
            text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", match.group(5))).strip()
            if len(text) < 3:
                continue
            nominal = round((y_max - y_min) / _INK_BOX_RATIO, 2)
            if nominal < MIN_POINT_SIZE:
                found.add(f"text below {MIN_POINT_SIZE}pt ({nominal}pt): {text[:60]}")
            if width is not None and (x_max > width + 1 or y_max > (height or 0) + 1):
                found.add(f"line runs outside the page box: {text[:60]}")
        problems[number] = sorted(found)
    return problems


def compose_unit_markdown(unit_id: str, content: Mapping[str, Any]) -> str:
    """The deterministic layout source for one admitted unit content body."""
    sections = content.get("sections")
    if not isinstance(sections, list) or not sections:
        raise RenderFault(f"admitted content for {unit_id} declares no sections to render")
    lines = [f"# {unit_id}", ""]
    for ordinal, section in enumerate(sections):
        if not isinstance(section, Mapping):
            raise RenderFault(f"content section {ordinal} of {unit_id} is not an object")
        heading = section.get("heading")
        body = section.get("body")
        if not isinstance(heading, str) or not isinstance(body, str):
            raise RenderFault(f"content section {ordinal} of {unit_id} has no heading and body")
        lines += [f"## {heading}", "", body, ""]
    return "\n".join(lines) + "\n"


# Which deterministic renderer draws a brief of each authoritative kind. Topology kinds
# resolve through `visual_maps.render_map`, so the *domain's* own `map_kind` chooses the
# drawing, not the brief's word for it.
def _render_topology(domain: Mapping[str, Any]) -> str:
    return visual_maps.render_map(dict(domain))


def _render_power_path(domain: Mapping[str, Any]) -> str:
    return visual_maps.render_power_path(
        dict(domain.get("build_map") or {}), dict(domain.get("electrical") or {}))


def _render_parts(domain: Mapping[str, Any]) -> str:
    parts = domain.get("parts") or []
    if not parts:
        raise RenderFault("the domain names no parts to draw")
    return visual_maps.render_parts_diagram(list(parts), subject=str(domain.get("subject", "")))


def _render_safety_inset(domain: Mapping[str, Any]) -> str:
    failures = (domain.get("electrical") or {}).get("failure_modes") or []
    if not failures:
        raise RenderFault("the domain records no failure mode to draw a safety inset from")
    return visual_maps.render_warning_notice(dict(failures[0]))


# Poppler's utilities take `-v`, not `--version`, and print it on stderr.
_VERSION_FLAG = {name: "-v" for name in RASTER_TOOLS}


def tool_versions(names: Sequence[str]) -> dict[str, str]:
    """One real local invocation per tool; an absent or broken tool fails closed."""
    versions: dict[str, str] = {}
    for name in names:
        located = shutil.which(name)
        if not located:
            raise CapabilityProofFailed(f"executable not on PATH: {name}")
        completed = subprocess.run(
            [located, _VERSION_FLAG.get(name, "--version")],
            capture_output=True, text=True, timeout=60)
        printed = (completed.stdout or completed.stderr).strip().splitlines()
        if not printed:
            raise CapabilityProofFailed(f"{name} reports no version")
        versions[name] = printed[0]
    return versions


DETERMINISTIC_VISUAL_RENDERERS: Mapping[str, Callable[[Mapping[str, Any]], str]] = {
    "build_map": _render_topology,
    "breadboard": _render_topology,
    "wiring": _render_topology,
    "circuit": _render_topology,
    "electrical": _render_topology,
    "terminal_block": _render_topology,
    "connectivity": _render_topology,
    "schematic": _render_topology,
    "netlist": _render_topology,
    "power_path": _render_power_path,
    "pinout": _render_parts,
    "pin_map": _render_parts,
    "safety_inset": _render_safety_inset,
}


def _probe_model_cli_identity(transport: "CliTransport") -> dict[str, Any]:
    return {
        "executables": {
            name: transport.observe_executable(name)
            for name in sorted({route.cli for route in transport.registry.values()})
        }
    }


def _probe_retrieval(transport: "CliTransport") -> dict[str, Any]:
    if not transport.guard.installed:
        raise CapabilityProofFailed(
            "the process egress broker is not installed; no retrieval can be contained")
    return {"egress_broker": "EgressGuard", "mechanism": "socket.socket interception"}


def _probe_renderer(transport: "CliTransport") -> dict[str, Any]:
    return {"tools": tool_versions(RENDER_TOOLS)}


def _probe_rasterizer(transport: "CliTransport") -> dict[str, Any]:
    return {"tools": tool_versions(RASTER_TOOLS)}


def _probe_persistence(transport: "CliTransport") -> dict[str, Any]:
    probe_path = transport.output_root / RENDER_DIRNAME / "capability_probe.json"
    probe_path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json({"probe": "persistence", "at": utc_now().isoformat()})
    probe_path.write_text(payload, encoding="utf-8")
    written = probe_path.read_text(encoding="utf-8")
    probe_path.unlink()
    if written != payload:
        raise CapabilityProofFailed(f"the output root at {transport.output_root} does not read back")
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("create table probe (value text)")
        connection.execute("insert into probe values ('ok')")
        rows = connection.execute("select value from probe").fetchall()
    finally:
        connection.close()
    if rows != [("ok",)]:
        raise CapabilityProofFailed("the sqlite checkpoint engine does not round-trip a write")
    return {"output_root": str(transport.output_root), "sqlite_version": sqlite3.sqlite_version}


def _probe_logger(transport: "CliTransport") -> dict[str, Any]:
    evidence_root = transport.evidence_root
    evidence_root.mkdir(parents=True, exist_ok=True)
    probe_path = evidence_root / "capability_probe.log"
    with probe_path.open("a", encoding="utf-8") as handle:
        handle.write("")
    probe_path.unlink()
    return {"evidence_root": str(evidence_root)}


# One local probe per capability, in D03's own order. No entry may reach a model.
CAPABILITY_PROBES: Mapping[str, Callable[["CliTransport"], dict[str, Any]]] = {
    "model_cli_identity": _probe_model_cli_identity,
    "retrieval": _probe_retrieval,
    "renderer": _probe_renderer,
    "rasterizer": _probe_rasterizer,
    "persistence": _probe_persistence,
    "logger": _probe_logger,
}


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
        engine_root: Path | str | None = None,
    ) -> None:
        # The engine root is repository-owned data, so it is supplied, not inferred.
        # It used to default to this module's install location's grandparent, which is
        # site-packages once installed; roots.repository_root() raises an actionable
        # error instead of silently pointing there.
        self.engine_root = roots.repository_root(engine_root)
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
        self.render_root = self.output_root / RENDER_DIRNAME
        self._artifacts = ArtifactStore(self.output_root)
        self._render_attempts: dict[str, int] = {}

    def executable(self, name: str) -> ExecutableIdentity:
        if name not in self._executables:
            self._executables[name] = probe_executable(name)
        return self._executables[name]

    # -------------------------------------------- product capability surface (D03)

    def prove_capability(self, capability: str) -> dict[str, Any]:
        """One bounded local probe. Never a curriculum model job (spec 6.2, D03)."""
        probe = CAPABILITY_PROBES.get(capability)
        if probe is None:
            return {"result": "MISSING", "capability": capability,
                    "detail": f"no local probe is registered for {capability!r}"}
        try:
            detail = probe(self)
        except UnavailableExternalFact as error:
            return {"result": "UNAVAILABLE_EXTERNAL_FACT", "capability": capability,
                    "fact": error.fact, "detail": str(error)[:500]}
        except (TransportError, checks.CheckFailure, OSError, sqlite3.Error) as error:
            return {"result": "MISSING", "capability": capability, "detail": str(error)[:500]}
        return {"result": "PASS", "capability": capability, "detail": detail}

    def observe_executable(self, name: str) -> dict[str, Any]:
        """The installed executable's own identity, resolved and hashed on this host."""
        identity = self.executable(name)
        return {"name": identity.name, "path": identity.path,
                "sha256": identity.sha256, "version": identity.version}

    # ------------------------------------ product capability surface (D11/D13/D14)

    def verify_domain(
        self, *, body: Mapping[str, Any], contract: Mapping[str, Any]
    ) -> dict[str, Any]:
        """Execute one frozen curriculum verifier and its complete fixture suite.

        The model never supplies this result.  Every declared executable/fixture
        is re-hashed against D02's frozen reference, the invocation is parsed as
        argv (never a shell string), and the child runs under a no-network host
        sandbox with read access limited to the exact frozen verifier files and
        write access limited to one content-addressed verifier work directory.
        """

        verifier = contract.get("verifier")
        if not isinstance(verifier, Mapping):
            raise VerifierFault("the effective run carries no verifier declaration")

        def resolve_reference(reference: Any, label: str) -> Path:
            if not isinstance(reference, Mapping):
                raise VerifierFault(f"{label} is not a frozen file reference")
            relative = reference.get("path")
            expected = reference.get("sha256")
            if not isinstance(relative, str) or not relative or not isinstance(expected, str):
                raise VerifierFault(f"{label} lacks a path and SHA-256")
            path = (self.engine_root / relative).resolve()
            if path == self.engine_root or self.engine_root not in path.parents:
                raise VerifierFault(f"{label} escapes the engine root: {path}")
            if not path.is_file():
                raise VerifierFault(f"{label} is missing: {path}")
            actual = sha256_file(path)
            if actual != expected:
                raise VerifierFault(
                    f"{label} changed after D02 froze it: expected {expected}, got {actual}")
            return path

        schema_reference = contract.get("schema")
        schema_path: Path | None = None
        if schema_reference is not None:
            schema_path = resolve_reference(schema_reference, "domain schema")

        entry = resolve_reference(verifier.get("entry_point"), "domain verifier entry point")
        dependency_declarations = verifier.get("dependencies")
        if not isinstance(dependency_declarations, Sequence) or isinstance(
            dependency_declarations, (str, bytes)
        ):
            raise VerifierFault("verifier dependencies is not a sequence")
        if len(dependency_declarations) > 64:
            raise VerifierFault("verifier dependencies exceeds the frozen bound of 64")
        dependency_paths = tuple(
            resolve_reference(reference, f"verifier dependency {index}")
            for index, reference in enumerate(dependency_declarations, start=1)
        )
        if len(set(dependency_paths)) != len(dependency_paths):
            raise VerifierFault("verifier dependencies contain duplicate paths")
        invocation = verifier.get("invocation")
        if not isinstance(invocation, str):
            raise VerifierFault("domain verifier invocation is not a string")
        try:
            template = shlex.split(invocation)
        except ValueError as error:
            raise VerifierFault(f"domain verifier invocation is not valid argv: {error}") from error
        if not template or template.count("<domain>") != 1:
            raise VerifierFault("domain verifier invocation must contain exactly one <domain> token")

        entry_relative = str(verifier.get("entry_point", {}).get("path", ""))
        entry_positions = [
            index for index, token in enumerate(template)
            if token == entry_relative or (self.engine_root / token).resolve() == entry
        ]
        if len(entry_positions) != 1:
            raise VerifierFault(
                "domain verifier invocation must name its frozen entry point exactly once")

        executable_token = template[0]
        if executable_token in {"python", "python3"}:
            executable = Path(sys.executable).resolve()
        else:
            raise VerifierFault(
                "domain verifier invocation must use the isolated Python runner")

        reject_declarations = verifier.get("must_reject") or []
        accept_declarations = verifier.get("must_accept") or []
        if not isinstance(reject_declarations, Sequence) or isinstance(
            reject_declarations, (str, bytes)
        ):
            raise VerifierFault("verifier must_reject is not a sequence")
        if not isinstance(accept_declarations, Sequence) or isinstance(
            accept_declarations, (str, bytes)
        ):
            raise VerifierFault("verifier must_accept is not a sequence")
        if not reject_declarations or not accept_declarations:
            raise VerifierFault("verifier fixture suite requires reject and accept members")
        if len(reject_declarations) + len(accept_declarations) > 64:
            raise VerifierFault("verifier fixture suite exceeds the frozen bound of 64")
        prepared_rejects: list[tuple[Mapping[str, Any], str, Path]] = []
        for index, declaration in enumerate(reject_declarations, start=1):
            if not isinstance(declaration, Mapping):
                raise VerifierFault(f"reject fixture {index} is not an object")
            fixture_ref = declaration.get("fixture")
            expected_code = declaration.get("expected_code")
            if not isinstance(expected_code, str) or not expected_code:
                raise VerifierFault(f"reject fixture {index} declares no expected code")
            prepared_rejects.append((
                fixture_ref,
                expected_code,
                resolve_reference(fixture_ref, f"reject fixture {index}"),
            ))
        prepared_accepts = [
            (fixture_ref, resolve_reference(fixture_ref, f"accept fixture {index}"))
            for index, fixture_ref in enumerate(accept_declarations, start=1)
        ]

        body_bytes = canonical_json(dict(body)).encode("utf-8")
        body_sha256 = sha256_bytes(body_bytes)
        contract_without_digest = {key: value for key, value in contract.items() if key != "digest"}
        contract_sha256 = canonical_digest(contract_without_digest)
        declared_contract_sha256 = contract.get("digest")
        if declared_contract_sha256 is not None and declared_contract_sha256 != contract_sha256:
            raise VerifierFault(
                "domain contract digest does not match its frozen verifier inputs")
        work = (
            domain_verifier_work_root(
                engine_root=self.engine_root,
                output_root=self.output_root,
            )
            / contract_sha256
            / body_sha256
        )
        home = work / "home"
        frozen_root = work / "frozen"
        work.mkdir(parents=True, exist_ok=True)
        home.mkdir(parents=True, exist_ok=True)
        frozen_root.mkdir(parents=True, exist_ok=True)
        candidate_path = work / "candidate.json"
        if candidate_path.is_file():
            if candidate_path.read_bytes() != body_bytes:
                raise VerifierFault("content-addressed verifier candidate bytes conflict")
        else:
            candidate_path.write_bytes(body_bytes)

        def stage_reference(
            reference: Mapping[str, Any], source: Path, label: str
        ) -> Path:
            relative = reference.get("path")
            expected = reference.get("sha256")
            destination = (frozen_root / str(relative)).resolve()
            if destination == frozen_root or frozen_root not in destination.parents:
                raise VerifierFault(f"{label} staging path escapes the frozen snapshot")
            try:
                frozen_bytes = source.read_bytes()
            except OSError as error:
                raise VerifierFault(f"{label} could not be staged: {error}") from error
            actual = sha256_bytes(frozen_bytes)
            if actual != expected:
                raise VerifierFault(
                    f"{label} changed while its frozen snapshot was staged: "
                    f"expected {expected}, got {actual}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.is_file():
                if destination.read_bytes() != frozen_bytes:
                    raise VerifierFault(f"{label} staged bytes conflict with an existing snapshot")
            else:
                destination.write_bytes(frozen_bytes)
            return destination

        staged_entry = stage_reference(
            verifier["entry_point"], entry, "domain verifier entry point")
        staged_schema = (
            stage_reference(schema_reference, schema_path, "domain schema")
            if schema_path is not None and isinstance(schema_reference, Mapping)
            else None
        )
        staged_dependencies = tuple(
            stage_reference(reference, source, f"verifier dependency {index}")
            for index, (reference, source) in enumerate(
                zip(dependency_declarations, dependency_paths, strict=True), start=1)
        )
        staged_rejects = [
            (
                fixture_ref,
                expected_code,
                stage_reference(fixture_ref, source, f"reject fixture {index}"),
            )
            for index, (fixture_ref, expected_code, source) in enumerate(
                prepared_rejects, start=1)
        ]
        staged_accepts = [
            (fixture_ref, stage_reference(fixture_ref, source, f"accept fixture {index}"))
            for index, (fixture_ref, source) in enumerate(prepared_accepts, start=1)
        ]
        guard_path = work / "verifier_guard.py"
        guard_bytes = VERIFIER_GUARD_SOURCE.encode("utf-8")
        if guard_path.is_file():
            if guard_path.read_bytes() != guard_bytes:
                raise VerifierFault("verifier guard bytes conflict with an existing snapshot")
        else:
            guard_path.write_bytes(guard_bytes)

        profile = home / "verifier.sb"
        profile.write_text(
            render_sandbox_profile(
                workspace=work,
                home=home,
                readable=executable_read_roots(str(executable)),
                allow_network=False,
                metadata_denied=(self.engine_root,),
                model_cli_support=False,
                workspace_writable=False,
                allow_process_fork=False,
            ),
            encoding="utf-8",
        )
        environment = build_worker_environment(home=home)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"

        def run_one(domain_path: Path) -> dict[str, Any]:
            argv = list(template)
            verifier_args = argv[1:]
            verifier_entry_index = entry_positions[0] - 1
            verifier_args.pop(verifier_entry_index)
            verifier_args[verifier_args.index("<domain>")] = str(domain_path)
            argv = [
                str(executable),
                "-I",
                "-S",
                str(guard_path),
                str(self.engine_root),
                str(staged_entry),
                *verifier_args,
            ]
            expected_domain_sha256 = sha256_file(domain_path)
            completed = subprocess.run(
                build_sandboxed_argv(argv, profile_path=profile),
                cwd=str(work),
                env=environment,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if not domain_path.is_file() or sha256_file(domain_path) != expected_domain_sha256:
                raise VerifierFault(
                    f"verifier changed the exact input bytes at {domain_path}")
            raw_output = (completed.stdout or "") + (completed.stderr or "")
            marker_lines = [
                line[len(VERIFIER_RUNTIME_MARKER):]
                for line in raw_output.splitlines()
                if line.startswith(VERIFIER_RUNTIME_MARKER)
            ]
            if len(marker_lines) != 1:
                raise VerifierFault(
                    "verifier emitted no unique authenticated runtime-module manifest: "
                    f"{raw_output[:1_000]}")
            try:
                runtime_modules = json.loads(marker_lines[0])
            except json.JSONDecodeError as error:
                raise VerifierFault(
                    f"verifier runtime-module manifest is not valid JSON: {error}") from error
            if not isinstance(runtime_modules, list):
                raise VerifierFault("verifier runtime-module manifest is not a list")
            normalized_modules: list[dict[str, str]] = []
            for index, record in enumerate(runtime_modules, start=1):
                if not isinstance(record, Mapping):
                    raise VerifierFault(
                        f"verifier runtime-module record {index} is not an object")
                module_name = record.get("module")
                raw_path = record.get("path")
                observed_sha256 = record.get("sha256")
                if not all(isinstance(value, str) and value for value in (
                    module_name, raw_path, observed_sha256
                )):
                    raise VerifierFault(
                        f"verifier runtime-module record {index} is incomplete")
                module_path = Path(raw_path).resolve()
                if "site-packages" in module_path.parts or "dist-packages" in module_path.parts:
                    raise VerifierFault(
                        f"verifier loaded an unreceipted package module: {module_path}")
                if module_path == self.engine_root or self.engine_root in module_path.parents:
                    raise VerifierFault(
                        f"verifier loaded unstaged engine code: {module_path}")
                if not module_path.is_file():
                    raise VerifierFault(
                        f"verifier runtime module disappeared after execution: {module_path}")
                actual_sha256 = sha256_file(module_path)
                if actual_sha256 != observed_sha256:
                    raise VerifierFault(
                        f"verifier runtime module changed during execution: {module_path}")
                normalized_modules.append({
                    "module": module_name,
                    "path": str(module_path),
                    "sha256": actual_sha256,
                })
            normalized_modules.sort(key=lambda record: (record["module"], record["path"]))
            visible_lines = [
                line for line in raw_output.splitlines(keepends=True)
                if not line.startswith(VERIFIER_RUNTIME_MARKER)
            ]
            combined = "".join(visible_lines)[:20_000]
            codes = sorted(set(re.findall(r"(?m)^([a-z][a-z0-9-]{2,80}):", combined)))
            return {
                "returncode": completed.returncode,
                "codes": codes,
                "output_sha256": sha256_bytes(combined.encode("utf-8")),
                "output_excerpt": combined[:2_000],
                "runtime_modules": normalized_modules,
                "runtime_digest": canonical_digest(normalized_modules),
                "schema_valid": True,
            }

        fixtures: list[dict[str, Any]] = []
        for fixture_ref, expected_code, fixture in staged_rejects:
            result = run_one(fixture)
            if result["returncode"] == 0 or expected_code not in result["codes"]:
                raise VerifierFault(
                    f"reject fixture {fixture_ref.get('path')} behaved incorrectly: "
                    f"expected nonzero/{expected_code}, observed "
                    f"{result['returncode']}/{result['codes']}")
            fixtures.append({
                "path": fixture_ref.get("path"),
                "sha256": fixture_ref.get("sha256"),
                "expected": "reject",
                "expected_code": expected_code,
                **result,
            })

        for fixture_ref, fixture in staged_accepts:
            result = run_one(fixture)
            if result["returncode"] != 0:
                raise VerifierFault(
                    f"accept fixture {fixture_ref.get('path')} was rejected: "
                    f"{result['codes']}")
            fixtures.append({
                "path": fixture_ref.get("path"),
                "sha256": fixture_ref.get("sha256"),
                "expected": "accept",
                **result,
            })

        candidate = run_one(candidate_path)
        return {
            "result": "PASS" if candidate["returncode"] == 0 else "FAIL",
            "candidate_sha256": body_sha256,
            "contract_sha256": contract_sha256,
            "entry_point_sha256": verifier["entry_point"]["sha256"],
            "schema_sha256": (
                schema_reference.get("sha256")
                if staged_schema is not None and isinstance(schema_reference, Mapping)
                else None
            ),
            "guard_sha256": sha256_bytes(guard_bytes),
            "interpreter": {
                "path": str(executable),
                "sha256": sha256_file(executable),
                "version": platform.python_version(),
                "flags": ["-I", "-S"],
            },
            "dependency_sha256": [
                reference["sha256"] for reference in dependency_declarations
            ],
            "invocation_sha256": sha256_bytes(invocation.encode("utf-8")),
            "fixtures_result": "PASS",
            "fixtures": fixtures,
            "candidate": candidate,
        }

    def read_artifact_body(self, unit_id: str, channel: str, content_hash: str) -> dict[str, Any]:
        """The admitted artifact those bytes hash to, from the content-addressed store."""
        stream = ArtifactStream(scope=UNIT_SCOPE, channel=channel, unit_id=unit_id)
        path = self._artifacts.resolve(stream.blob_path(content_hash))
        if not path.is_file():
            raise RenderFault(
                f"no admitted {channel} artifact for {unit_id} at {content_hash} "
                f"under {self.output_root}")
        data = path.read_bytes()
        if sha256_bytes(data) != content_hash:
            raise RenderFault(f"the stored {channel} artifact for {unit_id} is not its own hash")
        body = json.loads(data)
        if not isinstance(body, dict):
            raise RenderFault(f"the admitted {channel} artifact for {unit_id} is not an object")
        return body

    def render_unit(self, unit_id: str, parents: Mapping[str, str]) -> dict[str, Any]:
        """Render one layout source and unit PDF from the admitted heads (D13)."""
        content_hash = parents.get("content")
        if not isinstance(content_hash, str) or not content_hash:
            raise RenderFault(f"render of {unit_id} was given no admitted content parent")
        content = self.read_artifact_body(unit_id, "content", content_hash)

        directory = self.render_root / unit_id / canonical_digest(dict(parents))
        directory.mkdir(parents=True, exist_ok=True)
        markdown = directory / f"{unit_id}.md"
        markdown.write_text(compose_unit_markdown(unit_id, content), encoding="utf-8")
        pdf = directory / f"{unit_id}.pdf"
        completed = subprocess.run(
            ["pandoc", str(markdown), "--resource-path", str(directory),
             "--pdf-engine=typst", "-V", "mainfont=Helvetica",
             "-V", "geometry:margin=0.8in", "-V", "fontsize=11pt", "-o", str(pdf)],
            cwd=str(directory), capture_output=True, text=True, timeout=600)
        if completed.returncode != 0:
            raise RenderFault(f"pandoc/typst failed for {unit_id}: {completed.stderr.strip()[:500]}")
        if not pdf.is_file():
            raise RenderFault(f"pandoc reported success but wrote no PDF for {unit_id}")

        self._render_attempts[unit_id] = self._render_attempts.get(unit_id, 0) + 1
        return {
            "layout_path": str(markdown),
            "layout_sha256": sha256_file(markdown),
            "pdf_path": str(pdf),
            "pdf_sha256": sha256_file(pdf),
            "renderer": "pandoc --pdf-engine=typst",
            "attempt": self._render_attempts[unit_id],
        }

    def inspect_pages(self, pdf_path: str, pdf_sha256: str) -> dict[str, Any]:
        """Rasterize and inspect every page of the exact shipped PDF (D14)."""
        path = Path(pdf_path)
        if not path.is_file():
            raise RenderFault(f"the PDF to inspect does not exist: {path}")
        actual = sha256_file(path)
        if actual != pdf_sha256:
            raise RenderFault(
                f"the PDF at {path} hashes to {actual}, not the declared {pdf_sha256}")

        images = rasterize_pages(path, self.render_root / "pages" / pdf_sha256)
        text_problems = page_text_problems(path)
        pages: list[dict[str, Any]] = []
        for number, image in enumerate(images, start=1):
            blank = page_is_blank(image)
            problems = list(text_problems.get(number, ()))
            if blank:
                problems.append("the page renders no ink")
            pages.append({
                "number": number,
                "page_sha256": sha256_file(image),
                "image_path": str(image),
                "problems": sorted(problems),
                "unreadable": blank,
            })
        return {"pdf_sha256": pdf_sha256, "pages": pages}

    def render_deterministic_visual(
        self, brief: Mapping[str, Any], permitted_facts: Sequence[str]
    ) -> dict[str, Any]:
        """Draw one authoritative visual from the admitted domain, never from a model (D11)."""
        kind = brief.get("kind")
        renderer = DETERMINISTIC_VISUAL_RENDERERS.get(str(kind))
        if renderer is None:
            raise RenderFault(f"no deterministic renderer for visual kind {kind!r}")
        unit_id, domain_hash, key = brief.get("unit_id"), brief.get("domain_hash"), brief.get("key")
        if not all(isinstance(value, str) and value for value in (unit_id, domain_hash, key)):
            raise RenderFault(f"visual brief {key!r} names no unit, domain head, and key")

        domain = self.read_artifact_body(str(unit_id), "domain", str(domain_hash))
        svg = renderer(domain)

        directory = self.render_root / str(unit_id) / "visuals" / str(domain_hash)
        directory.mkdir(parents=True, exist_ok=True)
        asset = directory / (re.sub(r"[^A-Za-z0-9._-]", "_", str(key)) + ".svg")
        asset.write_text(svg, encoding="utf-8")
        return {
            "asset_path": str(asset),
            "sha256": sha256_file(asset),
            "format": "svg",
            "permitted_facts": sorted(str(fact) for fact in permitted_facts or ()),
        }

    def execute(
        self,
        *,
        job_id: str,
        activation_id: str,
        episode_id: str,
        projection: Mapping[str, Any],
        staged_inputs: Sequence[StagedInput] = (),
        data_classes: Sequence[str] | None = None,
        web_search: bool = False,
    ) -> TransportResult:
        route = resolve_route(job_id, self.registry)
        resolve_prompt_path(route)
        resolve_schema_path(route)
        requested = tuple(data_classes) if data_classes is not None else route.data_classes
        undeclared = sorted(set(requested) - set(route.data_classes))
        if undeclared:
            raise RouteRejected(f"{route.job_id}: undeclared data classes {undeclared}")
        if web_search and route.cli != "claude":
            raise RouteRejected(f"{route.job_id}: web_search is a Claude-only tool grant")

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
                    authorization_receipt=authorization_receipt, web_search=web_search)
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
        web_search: bool = False,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        executable = self.executable(route.cli)
        cli_schema_projection = (
            build_cli_schema_projection(load_output_schema(route))
            if route.cli == "claude" else None)
        workspace = stage_workspace(
            output_root=self.output_root, episode_id=episode_id, activation_id=activation_id,
            route=route, projection=projection, authorization_receipt=authorization_receipt,
            staged_inputs=staged_inputs, cli_schema_projection=cli_schema_projection)
        instruction = (workspace.path / route.prompt).read_text(encoding="utf-8")
        stdin_text: str | None = None
        if route.cli == "claude":
            argv = build_job_argv(route, workspace=workspace.path,
                                  cli_schema_projection=cli_schema_projection,
                                  tools=("WebSearch" if web_search else ""))
            verified_staged_inputs = build_verified_staged_inputs(
                workspace=workspace, staged_inputs=staged_inputs)
            stdin_text = build_claude_stdin_payload(
                instruction=instruction,
                projection=projection,
                verified_staged_inputs=verified_staged_inputs,
            )
        else:
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
            timeout_seconds=route.timeout_seconds, stdin=stdin_text)
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
            "cli_schema_projection_sha256": workspace.cli_schema_projection_sha256,
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
            observed = observe_identity(
                route, stdout=outcome.stdout, codex_home=workspace.home / "codex")
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
        # The tempdir check above is the load-bearing one. This second clause used to
        # compare against a REPO_ROOT inferred from this module's install location,
        # which pointed at site-packages and so guarded nothing; it now compares
        # against the repository root only when the caller has actually configured one.
        product_root = roots.configured_repository_root()
        if product_root is not None and (
                root == product_root or root.is_relative_to(product_root)):
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
