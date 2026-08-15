"""Code-owned egress broker and external-data authorization gate (spec 7.4 and 9).

Every network path reachable from this Python process passes through `EgressGuard`.
Only `SourceRetriever` — the deterministic primary-source retriever used by D06B — may
open HTTP(S), and only for a locator and data class the run authorization record
already covers. Every other socket use is denied and receipted.
"""
from __future__ import annotations

import contextlib
import hashlib
import ipaddress
import json
import socket
import threading
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, Sequence
from urllib.parse import urlparse

import jsonschema
import yaml

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"

PROVIDERS: tuple[str, ...] = ("anthropic", "openai", "primary_source_hosts")

PROVIDER_DATA_CLASSES: Mapping[str, frozenset[str]] = MappingProxyType({
    "anthropic": frozenset({
        "manifest_unit_projection",
        "bounded_questions",
        "admitted_source_excerpts",
        "retrieved_source_files",
        "domain_parent_artifact",
        "content_parent_artifact",
        "visual_parent_artifact",
        "named_repair_findings",
        "schemas_and_rubrics",
    }),
    "openai": frozenset({
        "frozen_unit_artifacts",
        "frozen_workbook_artifacts",
        "deterministic_evidence",
        "shipped_pdf",
        "rasterized_pages",
        "schemas_and_rubrics",
    }),
    "primary_source_hosts": frozenset({"primary_source_bytes"}),
})

MODEL_API_HOSTS: frozenset[str] = frozenset({
    "api.openai.com",
    "chatgpt.com",
    "api.anthropic.com",
})


class EgressError(RuntimeError):
    """Base class for every containment failure raised by this module."""


class AuthorizationDenied(EgressError):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason


class EgressDenied(EgressError):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def canonical_digest(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def _load_schema(name: str) -> dict[str, Any]:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


@dataclass(frozen=True)
class AuthorizationRecord:
    """Run-scoped external-data authorization (spec 7.4).

    Credentials are not approval: this record is the only thing that grants a
    provider/data-class transmission, and it is checked before any child process or
    socket is created.
    """

    run_id: str
    curriculum_digest: str
    output_root: str
    approved_at_utc: str
    expires_at_utc: str
    providers: Mapping[str, Sequence[str]]

    def __post_init__(self) -> None:
        normalized: dict[str, tuple[str, ...]] = {}
        for provider, classes in dict(self.providers).items():
            if provider not in PROVIDERS:
                raise AuthorizationDenied("unknown_provider", provider)
            declared = tuple(sorted(set(classes)))
            unknown = set(declared) - PROVIDER_DATA_CLASSES[provider]
            if unknown:
                raise AuthorizationDenied(
                    "undeclared_data_class", f"{provider}: {sorted(unknown)}")
            normalized[provider] = declared
        object.__setattr__(self, "providers", MappingProxyType(normalized))
        object.__setattr__(self, "output_root", str(Path(self.output_root).resolve()))
        if len(self.curriculum_digest) != 64:
            raise AuthorizationDenied("malformed_curriculum_digest", self.curriculum_digest)

    def to_record(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "curriculum_digest": self.curriculum_digest,
            "output_root": self.output_root,
            "approved_at_utc": self.approved_at_utc,
            "expires_at_utc": self.expires_at_utc,
            "providers": {p: list(c) for p, c in self.providers.items()},
        }

    def digest(self) -> str:
        return canonical_digest(self.to_record())


def authorize_transmission(
    record: AuthorizationRecord | None,
    *,
    provider: str,
    data_classes: Iterable[str],
    curriculum_digest: str,
    run_id: str,
    output_root: Path | str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a granted authorization receipt, or raise before anything is transmitted."""
    requested = tuple(sorted(set(data_classes)))
    if not requested:
        raise AuthorizationDenied("no_data_class_requested")
    if record is None:
        raise AuthorizationDenied("authorization_absent", provider)
    if provider not in PROVIDERS:
        raise AuthorizationDenied("unknown_provider", provider)

    moment = now or utc_now()
    expires = datetime.fromisoformat(record.expires_at_utc)
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if moment >= expires:
        raise AuthorizationDenied("authorization_expired", record.expires_at_utc)
    if record.run_id != run_id:
        raise AuthorizationDenied("wrong_run_scope", f"{record.run_id} != {run_id}")
    if record.curriculum_digest != curriculum_digest:
        raise AuthorizationDenied("wrong_curriculum_digest", curriculum_digest)
    if record.output_root != str(Path(output_root).resolve()):
        raise AuthorizationDenied("wrong_output_scope", str(output_root))
    if provider not in record.providers:
        raise AuthorizationDenied("provider_not_authorized", provider)

    permitted = set(record.providers[provider])
    missing = [name for name in requested if name not in permitted]
    if missing:
        raise AuthorizationDenied("data_class_not_authorized", f"{provider}: {missing}")

    receipt = {
        "authorization_digest": record.digest(),
        "provider": provider,
        "data_classes": list(requested),
        "curriculum_digest": curriculum_digest,
        "run_id": run_id,
        "output_root": str(Path(output_root).resolve()),
        "approved_at_utc": record.approved_at_utc,
        "expires_at_utc": record.expires_at_utc,
        "checked_at_utc": moment.isoformat(),
        "decision": "granted",
    }
    receipt["receipt_id"] = canonical_digest(receipt)[:32]
    jsonschema.Draft202012Validator(
        _load_schema("internal_authorization_receipt.schema.json")).validate(receipt)
    return receipt


class ReceiptLog:
    """Append-only egress receipt sink; every allow and every denial lands here."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = Path(path) if path else None
        self._entries: list[dict[str, Any]] = []
        self._validator = jsonschema.Draft202012Validator(
            _load_schema("internal_egress_receipt.schema.json"))
        self._lock = threading.Lock()

    def append(self, receipt: Mapping[str, Any]) -> dict[str, Any]:
        entry = dict(receipt)
        entry.setdefault("recorded_at_utc", utc_now().isoformat())
        self._validator.validate(entry)
        with self._lock:
            self._entries.append(entry)
            if self._path is not None:
                self._path.parent.mkdir(parents=True, exist_ok=True)
                with self._path.open("a", encoding="utf-8") as handle:
                    handle.write(canonical_json(entry) + "\n")
        return entry

    @property
    def entries(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._entries)

    @property
    def denials(self) -> tuple[dict[str, Any], ...]:
        return tuple(e for e in self._entries if e["outcome"] == "denied")

    @property
    def allowed(self) -> tuple[dict[str, Any], ...]:
        return tuple(e for e in self._entries if e["outcome"] == "allowed")


@dataclass(frozen=True)
class _Grant:
    locator: str
    host: str
    port: int
    endpoints: frozenset[tuple[str, int]]
    authorization_receipt_id: str
    data_class: str


def _caller_origin() -> str:
    stack = traceback.extract_stack()[:-2]
    for frame in reversed(stack):
        if not frame.filename.endswith("egress.py"):
            return f"{Path(frame.filename).name}:{frame.lineno}"
    return "unknown"


class EgressGuard:
    """Process-wide socket interception.

    Patching happens on `socket.socket` itself, so raw sockets, `http.client`,
    `urllib`, and any third-party client all reach `_authorize` — there is no wrapper
    to route around. An unauthorized attempt is receipted and then raised.
    """

    def __init__(self, receipts: ReceiptLog) -> None:
        self.receipts = receipts
        self._local = threading.local()
        self._installed = False
        self._saved: dict[str, Any] = {}

    def install(self) -> None:
        if self._installed:
            return
        self._saved = {
            "connect": socket.socket.connect,
            "connect_ex": socket.socket.connect_ex,
            "create_connection": socket.create_connection,
        }
        guard = self

        def connect(sock, address):  # type: ignore[no-untyped-def]
            guard._authorize(address, channel="socket_connect")
            return guard._saved["connect"](sock, address)

        def connect_ex(sock, address):  # type: ignore[no-untyped-def]
            guard._authorize(address, channel="socket_connect_ex")
            return guard._saved["connect_ex"](sock, address)

        def create_connection(address, *args, **kwargs):  # type: ignore[no-untyped-def]
            guard._authorize(address, channel="create_connection")
            return guard._saved["create_connection"](address, *args, **kwargs)

        socket.socket.connect = connect  # type: ignore[method-assign]
        socket.socket.connect_ex = connect_ex  # type: ignore[method-assign]
        socket.create_connection = create_connection  # type: ignore[assignment]
        self._installed = True

    def uninstall(self) -> None:
        if not self._installed:
            return
        socket.socket.connect = self._saved["connect"]  # type: ignore[method-assign]
        socket.socket.connect_ex = self._saved["connect_ex"]  # type: ignore[method-assign]
        socket.create_connection = self._saved["create_connection"]  # type: ignore[assignment]
        self._installed = False

    def __enter__(self) -> "EgressGuard":
        self.install()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.uninstall()

    @property
    def installed(self) -> bool:
        return self._installed

    @property
    def _grant(self) -> _Grant | None:
        return getattr(self._local, "grant", None)

    @contextlib.contextmanager
    def granted(self, grant: _Grant):
        previous = self._grant
        self._local.grant = grant
        try:
            yield
        finally:
            self._local.grant = previous

    def _deny(self, target: str, *, channel: str, reason: str) -> None:
        self.receipts.append({
            "receipt_kind": "egress_denied",
            "channel": channel,
            "requested_target": target,
            "outcome": "denied",
            "denial_reason": reason,
            "traceback_origin": _caller_origin(),
        })
        raise EgressDenied(reason, target)

    def _authorize(self, address: Any, *, channel: str) -> None:
        if not isinstance(address, (tuple, list)) or len(address) < 2:
            self._deny(str(address), channel=channel, reason="unsupported_address_family")
        host, port = str(address[0]), int(address[1])
        target = f"{host}:{port}"
        grant = self._grant
        if grant is None:
            reason = ("direct_model_endpoint" if host in MODEL_API_HOSTS
                      else "unauthorized_socket_no_active_retrieval")
            self._deny(target, channel=channel, reason=reason)
        if host in MODEL_API_HOSTS:
            self._deny(target, channel=channel, reason="direct_model_endpoint")
        if (host, port) not in grant.endpoints:
            try:
                ipaddress.ip_address(host)
            except ValueError:
                self._deny(target, channel=channel, reason="host_not_pinned")
            self._deny(target, channel=channel, reason="dns_rebinding")
        self.receipts.append({
            "receipt_kind": "egress_allowed",
            "channel": channel,
            "requested_target": target,
            "outcome": "allowed",
            "authorization_receipt_id": grant.authorization_receipt_id,
            "locator": grant.locator,
            "resolved_host": grant.host,
            "data_class": grant.data_class,
        })


@dataclass(frozen=True)
class RetrievalPolicy:
    allowed_hosts: frozenset[str]
    max_bytes: int = 25_000_000
    max_redirects: int = 3
    require_tls: bool = True
    allow_private_addresses: bool = False
    allowed_content_types: frozenset[str] = frozenset({
        "text/html", "text/plain", "application/pdf", "application/json",
        "application/xhtml+xml", "text/markdown",
    })


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RETRIEVAL_HOSTS_PATH = REPO_ROOT / "policy" / "retrieval_hosts.v1.yaml"


class RetrievalHostProfileError(EgressError):
    """A named retrieval-host profile could not be loaded exactly as declared."""


def load_retrieval_host_profile(
    profile_name: str, *, path: Path | None = None,
) -> tuple[tuple[str, ...], str]:
    """Return `(hosts, policy_digest)` for one named profile (N30V7-F07, spec decision).

    A curriculum selects a profile by name; it never supplies hosts directly, and
    nothing here ever adds a host a model proposed for itself. Every host must be a
    bare, lowercase, wildcard-free hostname -- `SourceRetriever._check_host` already
    does exact-set membership, HTTPS, DNS/private-address, and allowlisted-redirect
    checks on top of whatever this returns; this function only guards the *shape* of
    the declared allowlist itself, before it ever reaches that enforcement.
    """
    document_path = path or DEFAULT_RETRIEVAL_HOSTS_PATH
    try:
        raw = document_path.read_text(encoding="utf-8")
    except OSError as error:
        raise RetrievalHostProfileError(f"cannot read retrieval host policy: {error}") from error
    document = yaml.safe_load(raw)
    if not isinstance(document, dict):
        raise RetrievalHostProfileError("retrieval host policy is not a mapping")
    profiles = document.get("profiles")
    if not isinstance(profiles, dict):
        raise RetrievalHostProfileError("retrieval host policy declares no profiles")
    profile = profiles.get(profile_name)
    if not isinstance(profile, dict):
        raise RetrievalHostProfileError(
            f"retrieval host profile {profile_name!r} is not declared in {document_path}")
    hosts = profile.get("hosts")
    if not isinstance(hosts, list) or not hosts:
        raise RetrievalHostProfileError(f"profile {profile_name!r} declares no hosts")
    normalized: list[str] = []
    for host in hosts:
        if not isinstance(host, str) or not host:
            raise RetrievalHostProfileError(f"profile {profile_name!r} carries a non-string host")
        if any(character in host for character in "*?/:@ "):
            raise RetrievalHostProfileError(
                f"profile {profile_name!r} host {host!r} is not a bare hostname "
                f"(no wildcards, no scheme, no port, no path)")
        if host != host.lower():
            raise RetrievalHostProfileError(
                f"profile {profile_name!r} host {host!r} must be lowercase")
        normalized.append(host)
    if len(set(normalized)) != len(normalized):
        raise RetrievalHostProfileError(f"profile {profile_name!r} declares a duplicate host")
    policy_digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return tuple(sorted(normalized)), policy_digest


@dataclass(frozen=True)
class RetrievalResponse:
    final_url: str
    status: int
    headers: Mapping[str, str]
    body: bytes
    redirect_chain: tuple[str, ...] = ()
    tls: Mapping[str, str] | None = None


def _default_resolver(host: str) -> tuple[str, ...]:
    infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    return tuple(sorted({info[4][0] for info in infos}))


def _default_opener(
    url: str,
    *,
    timeout: float,
    redirect_validator: Callable[[str, int], None],
    max_bytes: int,
) -> RetrievalResponse:
    import urllib.request

    chain: list[str] = []

    class _Tracker(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
            # Validate before urllib constructs or sends the redirected request.
            # Post-response inspection is too late for an egress boundary.
            redirect_validator(newurl, len(chain) + 1)
            chain.append(newurl)
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    opener = urllib.request.build_opener(_Tracker)
    with opener.open(url, timeout=timeout) as response:
        # Read at most one byte beyond the bound so an oversized body is denied
        # without buffering the complete attacker-controlled response.
        body = response.read(max_bytes + 1)
        return RetrievalResponse(
            final_url=response.geturl(),
            status=response.status,
            headers={k.lower(): v for k, v in response.headers.items()},
            body=body,
            redirect_chain=tuple(chain),
        )


class SourceRetriever:
    """The only authorized HTTP(S) egress path in this process (spec 7.4, D06B).

    The concrete retrieval strategy is D06B's; this class owns the boundary: what may
    be reached, under which authorization, and what is recorded about it.
    """

    def __init__(
        self,
        *,
        guard: EgressGuard,
        policy: RetrievalPolicy,
        resolver: Callable[[str], Sequence[str]] | None = None,
        opener: Callable[..., RetrievalResponse] | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.guard = guard
        self.policy = policy
        self._resolver = resolver or _default_resolver
        self._opener = opener or _default_opener
        self.timeout_seconds = timeout_seconds

    def _deny(self, locator: str, reason: str, **extra: Any) -> None:
        payload: dict[str, Any] = {
            "receipt_kind": "egress_denied",
            "channel": "source_retrieval",
            "requested_target": locator,
            "outcome": "denied",
            "denial_reason": reason,
        }
        payload.update(extra)
        self.guard.receipts.append(payload)
        raise EgressDenied(reason, locator)

    def _check_host(self, locator: str, host: str | None) -> str:
        if not host:
            self._deny(locator, "missing_host")
        host = host.lower()
        if host in MODEL_API_HOSTS:
            self._deny(locator, "direct_model_endpoint", resolved_host=host)
        if host not in self.policy.allowed_hosts:
            self._deny(locator, "host_not_allowlisted", resolved_host=host)
        return host

    def _validate_redirect_target(
        self,
        *,
        locator: str,
        target: str,
        redirect_ordinal: int | None,
        pinned_host: str,
        pinned_port: int,
        pinned_addresses: Sequence[str],
    ) -> None:
        """Fail closed before each redirect request and again after the response.

        The active socket grant is deliberately pinned to the original resolved
        endpoint. Redirects may remain on that exact HTTPS host/port only; a
        cross-host redirect requires a fresh top-level locator and authorization.
        """

        if redirect_ordinal is not None and redirect_ordinal > self.policy.max_redirects:
            self._deny(locator, "too_many_redirects", final_url=target,
                       redirect_chain=[target])
        parsed = urlparse(target)
        allowed_schemes = ("https",) if self.policy.require_tls else ("https", "http")
        if parsed.scheme not in allowed_schemes:
            self._deny(locator, "redirect_scheme_not_allowed", final_url=target,
                       redirect_chain=[target])
        raw_host = (parsed.hostname or "").lower()
        if raw_host in MODEL_API_HOSTS:
            self._deny(locator, "redirect_to_model_endpoint", final_url=target,
                       redirect_chain=[target],
                       resolved_host=raw_host)
        if raw_host not in self.policy.allowed_hosts:
            self._deny(locator, "redirect_to_unapproved_host", final_url=target,
                       redirect_chain=[target],
                       resolved_host=raw_host)
        host = self._check_host(locator, raw_host)
        try:
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
        except ValueError:
            self._deny(locator, "redirect_port_invalid", final_url=target,
                       redirect_chain=[target])
        if host != pinned_host:
            self._deny(locator, "redirect_host_not_pinned", final_url=target,
                       redirect_chain=[target],
                       resolved_host=host)
        if port != pinned_port:
            self._deny(locator, "redirect_port_not_pinned", final_url=target,
                       redirect_chain=[target],
                       resolved_host=host)
        addresses = tuple(self._resolver(host))
        if not addresses:
            self._deny(locator, "unresolvable_redirect_host", final_url=target,
                       redirect_chain=[target],
                       resolved_host=host)
        if not self.policy.allow_private_addresses:
            for address in addresses:
                if not ipaddress.ip_address(address).is_global:
                    self._deny(locator, "non_global_redirect_address",
                               final_url=target, redirect_chain=[target], resolved_host=host,
                               resolved_addresses=list(addresses))
        if not set(addresses).issubset(set(pinned_addresses)):
            self._deny(locator, "dns_rebinding", final_url=target,
                       redirect_chain=[target], resolved_host=host,
                       resolved_addresses=list(addresses))

    def fetch(
        self,
        locator: str,
        *,
        authorization_receipt: Mapping[str, Any] | None,
        data_class: str = "primary_source_bytes",
    ) -> tuple[bytes, dict[str, Any]]:
        if authorization_receipt is None:
            self._deny(locator, "authorization_absent")
        if authorization_receipt.get("provider") != "primary_source_hosts":
            self._deny(locator, "wrong_provider_authorization",
                       authorization_receipt_id=authorization_receipt.get("receipt_id"))
        if data_class not in authorization_receipt.get("data_classes", ()):
            self._deny(locator, "data_class_not_authorized",
                       authorization_receipt_id=authorization_receipt.get("receipt_id"))

        parsed = urlparse(locator)
        allowed_schemes = ("https",) if self.policy.require_tls else ("https", "http")
        if parsed.scheme not in allowed_schemes:
            self._deny(locator, "scheme_not_allowed")
        host = self._check_host(locator, parsed.hostname)
        try:
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
        except ValueError:
            self._deny(locator, "port_invalid")

        addresses = tuple(self._resolver(host))
        if not addresses:
            self._deny(locator, "unresolvable_host", resolved_host=host)
        if not self.policy.allow_private_addresses:
            for address in addresses:
                if not ipaddress.ip_address(address).is_global:
                    self._deny(locator, "non_global_address", resolved_host=host,
                               resolved_addresses=list(addresses))

        grant = _Grant(
            locator=locator,
            host=host,
            port=port,
            endpoints=frozenset({(host, port)} | {(a, port) for a in addresses}),
            authorization_receipt_id=str(authorization_receipt["receipt_id"]),
            data_class=data_class,
        )

        def validate_redirect(target: str, ordinal: int) -> None:
            self._validate_redirect_target(
                locator=locator, target=target, redirect_ordinal=ordinal,
                pinned_host=host, pinned_port=port, pinned_addresses=addresses)

        with self.guard.granted(grant):
            response = self._opener(
                locator,
                timeout=self.timeout_seconds,
                redirect_validator=validate_redirect,
                max_bytes=self.policy.max_bytes,
            )

        if len(response.redirect_chain) > self.policy.max_redirects:
            self._deny(locator, "too_many_redirects",
                       redirect_chain=list(response.redirect_chain))
        for ordinal, hop in enumerate(response.redirect_chain, start=1):
            self._validate_redirect_target(
                locator=locator, target=hop, redirect_ordinal=ordinal,
                pinned_host=host, pinned_port=port, pinned_addresses=addresses)
        self._validate_redirect_target(
            locator=locator, target=response.final_url, redirect_ordinal=None,
            pinned_host=host, pinned_port=port, pinned_addresses=addresses)
        if response.status != 200:
            self._deny(locator, "http_status_not_ok", http_status=response.status)
        if len(response.body) > self.policy.max_bytes:
            self._deny(locator, "response_too_large", byte_count=len(response.body))

        content_type = str(response.headers.get("content-type", "")).split(";")[0].strip().lower()
        if not content_type:
            self._deny(locator, "content_type_missing")
        if content_type not in self.policy.allowed_content_types:
            self._deny(locator, "content_type_not_allowed", content_type=content_type)

        receipt = self.guard.receipts.append({
            "receipt_kind": "egress_allowed",
            "channel": "source_retrieval",
            "requested_target": locator,
            "outcome": "allowed",
            "authorization_receipt_id": str(authorization_receipt["receipt_id"]),
            "locator": locator,
            "resolved_host": host,
            "resolved_addresses": list(addresses),
            "final_url": response.final_url,
            "redirect_chain": list(response.redirect_chain),
            "http_status": response.status,
            "tls": dict(response.tls) if response.tls else None,
            "content_type": content_type,
            "byte_count": len(response.body),
            "bytes_sha256": hashlib.sha256(response.body).hexdigest(),
            "data_class": data_class,
        })
        return response.body, receipt


def authorize_subprocess_transmission(
    record: AuthorizationRecord | None,
    *,
    provider: str,
    data_classes: Iterable[str],
    curriculum_digest: str,
    run_id: str,
    output_root: Path | str,
    receipts: ReceiptLog,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Gate a model-CLI child process on the run authorization record (spec 7.4).

    Called before the child process exists, so a denial cannot follow transmission.
    """
    requested = sorted(set(data_classes))
    try:
        receipt = authorize_transmission(
            record, provider=provider, data_classes=requested,
            curriculum_digest=curriculum_digest, run_id=run_id,
            output_root=output_root, now=now)
    except AuthorizationDenied as denied:
        receipts.append({
            "receipt_kind": "egress_denied",
            "channel": "subprocess_transmission",
            "requested_target": f"{provider}:{','.join(requested)}",
            "outcome": "denied",
            "denial_reason": denied.reason,
        })
        raise
    receipts.append({
        "receipt_kind": "egress_allowed",
        "channel": "subprocess_transmission",
        "requested_target": f"{provider}:{','.join(requested)}",
        "outcome": "allowed",
        "authorization_receipt_id": receipt["receipt_id"],
        "data_class": ",".join(requested),
    })
    return receipt
