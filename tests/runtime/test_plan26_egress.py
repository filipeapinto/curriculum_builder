"""N13 egress broker and external-data authorization tests (spec 7.4, 9)."""
from __future__ import annotations

import hashlib
import http.client
import io
import socket
import threading
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from curriculum_factory.langgraph_factory.egress import (
    MODEL_API_HOSTS,
    PROVIDER_DATA_CLASSES,
    PROVIDERS,
    AuthorizationDenied,
    AuthorizationRecord,
    EgressDenied,
    EgressGuard,
    ReceiptLog,
    RetrievalHostProfileError,
    RetrievalPolicy,
    RetrievalResponse,
    SourceRetriever,
    _default_opener,
    authorize_subprocess_transmission,
    authorize_transmission,
    load_retrieval_host_profile,
)

# The repository data root is the checkout this test file lives in, computed from the
# test file's own location -- never from the installed package's location, which is
# site-packages once curriculum_factory is really installed.
REPO_ROOT = Path(__file__).resolve().parents[2]

CURRICULUM_DIGEST = "a" * 64
OTHER_DIGEST = "b" * 64
RUN_ID = "run-plan26-egress"


def make_record(output_root: Path, **overrides) -> AuthorizationRecord:
    payload = {
        "run_id": RUN_ID,
        "curriculum_digest": CURRICULUM_DIGEST,
        "output_root": str(output_root),
        "approved_at_utc": "2026-08-11T00:00:00+00:00",
        "expires_at_utc": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "providers": {
            "anthropic": ["manifest_unit_projection", "schemas_and_rubrics"],
            "openai": ["shipped_pdf", "rasterized_pages"],
            "primary_source_hosts": ["primary_source_bytes"],
        },
    }
    payload.update(overrides)
    return AuthorizationRecord(**payload)


@pytest.fixture()
def output_root(tmp_path: Path) -> Path:
    root = tmp_path / "output"
    root.mkdir()
    return root


@pytest.fixture()
def receipts() -> ReceiptLog:
    return ReceiptLog()


@pytest.fixture()
def guard(receipts: ReceiptLog):
    broker = EgressGuard(receipts)
    broker.install()
    try:
        yield broker
    finally:
        broker.uninstall()


def grant(record: AuthorizationRecord, output_root: Path, provider="primary_source_hosts",
          data_classes=("primary_source_bytes",)):
    return authorize_transmission(
        record, provider=provider, data_classes=data_classes,
        curriculum_digest=CURRICULUM_DIGEST, run_id=RUN_ID, output_root=output_root)


# ------------------------------------------------ retired third-party provider is gone


def test_the_allowlist_carries_exactly_the_three_approved_provider_classes():
    """spec 7.4: no authorization class for any provider other than anthropic, openai,
    and primary_source_hosts exists in this specification."""
    assert PROVIDERS == ("anthropic", "openai", "primary_source_hosts")
    assert set(PROVIDER_DATA_CLASSES) == {"anthropic", "openai", "primary_source_hosts"}


def test_the_retired_provider_class_is_dropped_not_merely_renamed(output_root: Path):
    """The old review-family provider key does not survive under a new spelling: it is
    unknown to the allowlist and cannot authorize or transmit anything."""
    with pytest.raises(AuthorizationDenied) as denied:
        make_record(output_root, providers={"third_party_review": ["shipped_pdf"]})
    assert denied.value.reason == "unknown_provider"

    record = make_record(output_root)
    with pytest.raises(AuthorizationDenied) as via_transmission:
        authorize_transmission(
            record, provider="third_party_review", data_classes=("shipped_pdf",),
            curriculum_digest=CURRICULUM_DIGEST, run_id=RUN_ID, output_root=output_root)
    assert via_transmission.value.reason == "unknown_provider"


def test_the_retired_providers_model_api_hosts_are_dropped_entirely():
    """spec 7.4: the retired review-family provider's model-API hosts are removed from
    the allowlist entirely, not merely relabeled — MODEL_API_HOSTS now names only the
    two approved providers' own endpoints."""
    assert MODEL_API_HOSTS == frozenset({"api.openai.com", "chatgpt.com", "api.anthropic.com"})
    assert len(MODEL_API_HOSTS) == 3


def test_a_host_no_longer_on_the_allowlist_still_fails_closed_not_open(
    guard: EgressGuard, receipts: ReceiptLog
):
    """Dropping a host from MODEL_API_HOSTS must never silently widen access: an
    unpinned model-style endpoint still hits the generic no-active-retrieval denial,
    it does not become reachable just because it is no longer named explicitly."""
    unpinned_host = "unpinned-model-endpoint.example.net"
    assert unpinned_host not in MODEL_API_HOSTS
    with pytest.raises(EgressDenied) as denied:
        socket.socket().connect((unpinned_host, 443))
    assert denied.value.reason == "unauthorized_socket_no_active_retrieval"
    assert receipts.denials[-1]["denial_reason"] == "unauthorized_socket_no_active_retrieval"


# --------------------------------------------------------------- authorization record


def test_record_rejects_unknown_provider_and_undeclared_data_class(output_root: Path):
    with pytest.raises(AuthorizationDenied) as unknown:
        make_record(output_root, providers={"azure": ["shipped_pdf"]})
    assert unknown.value.reason == "unknown_provider"

    with pytest.raises(AuthorizationDenied) as undeclared:
        make_record(output_root, providers={"openai": ["manifest_unit_projection"]})
    assert undeclared.value.reason == "undeclared_data_class"


@pytest.mark.parametrize(
    ("mutation", "expected_reason"),
    [
        ({"record": None}, "authorization_absent"),
        ({"run_id": "some-other-run"}, "wrong_run_scope"),
        ({"curriculum_digest": OTHER_DIGEST}, "wrong_curriculum_digest"),
        ({"provider": "openai", "data_classes": ("shipped_pdf",),
          "output_root": "elsewhere"}, "wrong_output_scope"),
        ({"provider": "primary_source_hosts",
          "data_classes": ("primary_source_bytes",), "drop_provider": True},
         "provider_not_authorized"),
        ({"provider": "anthropic", "data_classes": ("named_repair_findings",)},
         "data_class_not_authorized"),
        ({"expired": True}, "authorization_expired"),
    ],
)
def test_authorization_fails_closed_for_every_scope_mismatch(
    tmp_path: Path, output_root: Path, mutation, expected_reason
):
    providers = None
    if mutation.get("drop_provider"):
        providers = {"anthropic": ["manifest_unit_projection"]}
    kwargs = {}
    if mutation.get("expired"):
        kwargs["expires_at_utc"] = "2020-01-01T00:00:00+00:00"
    if providers is not None:
        kwargs["providers"] = providers
    record = None if "record" in mutation else make_record(output_root, **kwargs)

    root = tmp_path / "elsewhere" if mutation.get("output_root") == "elsewhere" else output_root
    root.mkdir(exist_ok=True)

    with pytest.raises(AuthorizationDenied) as denied:
        authorize_transmission(
            record,
            provider=mutation.get("provider", "anthropic"),
            data_classes=mutation.get("data_classes", ("manifest_unit_projection",)),
            curriculum_digest=mutation.get("curriculum_digest", CURRICULUM_DIGEST),
            run_id=mutation.get("run_id", RUN_ID),
            output_root=root,
        )
    assert denied.value.reason == expected_reason


def test_granted_receipt_carries_full_scope(output_root: Path):
    receipt = grant(make_record(output_root), output_root, provider="anthropic",
                    data_classes=("manifest_unit_projection",))
    assert receipt["decision"] == "granted"
    assert receipt["provider"] == "anthropic"
    assert receipt["curriculum_digest"] == CURRICULUM_DIGEST
    assert receipt["run_id"] == RUN_ID
    assert receipt["output_root"] == str(output_root.resolve())
    assert len(receipt["authorization_digest"]) == 64


def test_subprocess_authorization_receipts_both_outcomes(output_root: Path, receipts: ReceiptLog):
    authorize_subprocess_transmission(
        make_record(output_root), provider="anthropic",
        data_classes=("manifest_unit_projection",), curriculum_digest=CURRICULUM_DIGEST,
        run_id=RUN_ID, output_root=output_root, receipts=receipts)
    assert receipts.allowed[-1]["channel"] == "subprocess_transmission"

    with pytest.raises(AuthorizationDenied):
        authorize_subprocess_transmission(
            None, provider="anthropic", data_classes=("manifest_unit_projection",),
            curriculum_digest=CURRICULUM_DIGEST, run_id=RUN_ID,
            output_root=output_root, receipts=receipts)
    assert receipts.denials[-1]["denial_reason"] == "authorization_absent"


# ------------------------------------------------------------------------ egress guard


def test_raw_socket_connect_is_denied_and_receipted(guard: EgressGuard, receipts: ReceiptLog):
    with pytest.raises(EgressDenied) as denied:
        socket.socket().connect(("example.org", 443))
    assert denied.value.reason == "unauthorized_socket_no_active_retrieval"
    assert receipts.denials[-1]["channel"] == "socket_connect"
    assert receipts.denials[-1]["requested_target"] == "example.org:443"
    assert receipts.denials[-1]["traceback_origin"]


@pytest.mark.parametrize("host", sorted(MODEL_API_HOSTS))
def test_direct_model_endpoint_is_denied(guard: EgressGuard, receipts: ReceiptLog, host: str):
    with pytest.raises(EgressDenied) as denied:
        socket.create_connection((host, 443), timeout=1)
    assert denied.value.reason == "direct_model_endpoint"
    assert receipts.denials[-1]["requested_target"] == f"{host}:443"


def test_urllib_and_http_client_cannot_route_around_the_broker(
    guard: EgressGuard, receipts: ReceiptLog
):
    with pytest.raises(EgressDenied):
        urllib.request.urlopen("http://example.org/data.json", timeout=1)
    with pytest.raises(EgressDenied):
        http.client.HTTPSConnection("api.openai.com", timeout=1).connect()
    reasons = {entry["denial_reason"] for entry in receipts.denials}
    assert "unauthorized_socket_no_active_retrieval" in reasons
    assert "direct_model_endpoint" in reasons


def test_connect_ex_is_also_brokered(guard: EgressGuard, receipts: ReceiptLog):
    with pytest.raises(EgressDenied):
        socket.socket().connect_ex(("example.org", 443))
    assert receipts.denials[-1]["channel"] == "socket_connect_ex"


def test_guard_uninstall_restores_the_stdlib(receipts: ReceiptLog):
    original = socket.socket.connect
    broker = EgressGuard(receipts)
    broker.install()
    assert socket.socket.connect is not original
    broker.uninstall()
    assert socket.socket.connect is original


# -------------------------------------------------------------------- source retriever


def retriever(guard: EgressGuard, *, opener, resolver=None, **policy_kwargs) -> SourceRetriever:
    policy = RetrievalPolicy(allowed_hosts=frozenset({"standards.example.org"}), **policy_kwargs)
    return SourceRetriever(
        guard=guard, policy=policy,
        resolver=resolver or (lambda host: ("93.184.216.34",)),
        opener=opener)


def canned(body=b"<html>ok</html>", **overrides):
    payload = {
        "final_url": "https://standards.example.org/spec.html",
        "status": 200,
        "headers": {"content-type": "text/html; charset=utf-8"},
        "body": body,
        "redirect_chain": (),
        "tls": {"protocol": "TLSv1.3", "cipher": "TLS_AES_256_GCM_SHA384",
                "peer_subject": "CN=standards.example.org"},
    }
    payload.update(overrides)
    def open_canned(url, *, timeout, redirect_validator, max_bytes):
        for ordinal, target in enumerate(payload["redirect_chain"], start=1):
            redirect_validator(target, ordinal)
        return RetrievalResponse(**payload)
    return open_canned


def test_authorized_retrieval_records_full_metadata(
    guard: EgressGuard, receipts: ReceiptLog, output_root: Path
):
    receipt_grant = grant(make_record(output_root), output_root)
    body = b"<html>primary source</html>"
    fetcher = retriever(guard, opener=canned(body))
    payload, receipt = fetcher.fetch(
        "https://standards.example.org/spec.html", authorization_receipt=receipt_grant)

    assert payload == body
    assert receipt["outcome"] == "allowed"
    assert receipt["resolved_host"] == "standards.example.org"
    assert receipt["resolved_addresses"] == ["93.184.216.34"]
    assert receipt["final_url"] == "https://standards.example.org/spec.html"
    assert receipt["http_status"] == 200
    assert receipt["tls"]["protocol"] == "TLSv1.3"
    assert receipt["bytes_sha256"] == hashlib.sha256(body).hexdigest()
    assert receipt["byte_count"] == len(body)
    assert receipt["authorization_receipt_id"] == receipt_grant["receipt_id"]
    assert receipt["data_class"] == "primary_source_bytes"


@pytest.mark.parametrize(
    ("locator", "opener_kwargs", "expected_reason"),
    [
        ("http://standards.example.org/x", {}, "scheme_not_allowed"),
        ("https://unlisted.example.net/x", {}, "host_not_allowlisted"),
        ("https://api.openai.com/v1/responses", {}, "direct_model_endpoint"),
        ("https://standards.example.org/x",
         {"redirect_chain": ("https://evil.example.net/x",),
          "final_url": "https://evil.example.net/x"},
         "redirect_to_unapproved_host"),
        ("https://standards.example.org/x",
         {"redirect_chain": ("https://api.openai.com/v1/responses",),
          "final_url": "https://api.openai.com/v1/responses"},
         "redirect_to_model_endpoint"),
        ("https://standards.example.org/x", {"status": 404}, "http_status_not_ok"),
        ("https://standards.example.org/x",
         {"headers": {"content-type": "application/x-msdownload"}},
         "content_type_not_allowed"),
        ("https://standards.example.org/x", {"headers": {}},
         "content_type_missing"),
        ("https://standards.example.org/x",
         {"redirect_chain": ("http://standards.example.org:443/downgrade",),
          "final_url": "http://standards.example.org:443/downgrade"},
         "redirect_scheme_not_allowed"),
    ],
)
def test_retrieval_denials_are_receipted(
    guard: EgressGuard, receipts: ReceiptLog, output_root: Path,
    locator, opener_kwargs, expected_reason
):
    receipt_grant = grant(make_record(output_root), output_root)
    fetcher = retriever(guard, opener=canned(**opener_kwargs))
    with pytest.raises(EgressDenied) as denied:
        fetcher.fetch(locator, authorization_receipt=receipt_grant)
    assert denied.value.reason == expected_reason
    assert receipts.denials[-1]["denial_reason"] == expected_reason


def test_redirect_bound_is_enforced_before_the_excess_request(
    guard: EgressGuard, output_root: Path,
):
    receipt_grant = grant(make_record(output_root), output_root)
    attempted = ["https://standards.example.org/start"]
    targets = [
        f"https://standards.example.org/hop-{index}" for index in range(1, 5)
    ]

    def redirecting_opener(url, *, timeout, redirect_validator, max_bytes):
        for ordinal, target in enumerate(targets, start=1):
            redirect_validator(target, ordinal)
            attempted.append(target)  # models the request only after validation
        raise AssertionError("the fourth redirect must be denied before this point")

    fetcher = retriever(guard, opener=redirecting_opener, max_redirects=3)
    with pytest.raises(EgressDenied) as denied:
        fetcher.fetch(attempted[0], authorization_receipt=receipt_grant)
    assert denied.value.reason == "too_many_redirects"
    assert attempted == [targets[0].replace("hop-1", "start"), *targets[:3]]


def test_default_opener_validates_before_urllib_constructs_the_redirect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exercise the production urllib hook, not a SourceRetriever opener stub.

    This catches either removing the callback from `_Tracker.redirect_request`
    or moving it below `super().redirect_request`: in both regressions urllib
    would construct a follow-up request before the policy denial.
    """

    events: list[str] = []

    def base_redirect_request(self, req, fp, code, msg, headers, newurl):
        events.append("urllib_constructed_redirect")
        return object()

    monkeypatch.setattr(
        urllib.request.HTTPRedirectHandler,
        "redirect_request",
        base_redirect_request,
    )

    class RedirectingOpener:
        def __init__(self, handler) -> None:
            self.handler = handler

        def open(self, url, *, timeout):
            request = self.handler.redirect_request(
                object(), object(), 302, "Found", {},
                "http://standards.example.org:443/downgrade",
            )
            events.append("urllib_would_follow_redirect")
            raise AssertionError(f"redirect unexpectedly survived validation: {request!r}")

    def build_redirecting_opener(handler_type):
        return RedirectingOpener(handler_type())

    monkeypatch.setattr(urllib.request, "build_opener", build_redirecting_opener)

    def deny_before_follow(target: str, ordinal: int) -> None:
        events.append("validated_redirect")
        assert target == "http://standards.example.org:443/downgrade"
        assert ordinal == 1
        raise EgressDenied("redirect_scheme_not_allowed", target)

    with pytest.raises(EgressDenied) as denied:
        _default_opener(
            "https://standards.example.org/start",
            timeout=1.0,
            redirect_validator=deny_before_follow,
            max_bytes=1024,
        )

    assert denied.value.reason == "redirect_scheme_not_allowed"
    assert events == ["validated_redirect"]


def test_default_opener_surfaces_http_error_as_a_policy_checkable_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """urllib's HTTPError is a status-bearing response, not a tool crash."""

    error = urllib.error.HTTPError(
        "https://standards.example.org/forbidden",
        403,
        "Forbidden",
        {"Content-Type": "text/html"},
        io.BytesIO(b"denied"),
    )

    class DenyingOpener:
        def open(self, url, *, timeout):
            raise error

    monkeypatch.setattr(
        urllib.request, "build_opener", lambda handler_type: DenyingOpener())
    response = _default_opener(
        "https://standards.example.org/forbidden",
        timeout=1.0,
        redirect_validator=lambda target, ordinal: None,
        max_bytes=1024,
    )

    assert response.status == 403
    assert response.final_url == "https://standards.example.org/forbidden"
    assert response.headers == {"content-type": "text/html"}
    assert response.body == b"denied"


def test_default_opener_identifies_the_retriever_with_a_stable_user_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Public sources must not see urllib's commonly blocked default token."""

    observed: dict[str, object] = {}

    class Response:
        status = 200
        headers = {"Content-Type": "text/html"}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self, bound):
            return b"ok"

        def geturl(self):
            return "https://standards.example.org/source"

    class CapturingOpener:
        def open(self, request, *, timeout):
            observed["request"] = request
            observed["timeout"] = timeout
            return Response()

    monkeypatch.setattr(
        urllib.request, "build_opener", lambda handler_type: CapturingOpener())
    response = _default_opener(
        "https://standards.example.org/source",
        timeout=1.0,
        redirect_validator=lambda target, ordinal: None,
        max_bytes=1024,
    )

    request = observed["request"]
    assert isinstance(request, urllib.request.Request)
    assert request.full_url == "https://standards.example.org/source"
    assert request.get_method() == "GET"
    assert request.get_header("User-agent") == "curriculum-builder/1.0"
    assert observed["timeout"] == 1.0
    assert response.body == b"ok"


def test_load_retrieval_host_profile_returns_the_declared_electronics_profile(tmp_path: Path):
    """N30V7-F07: a curriculum selects a profile by name; it never supplies hosts."""

    from curriculum_factory.langgraph_factory.egress import default_retrieval_hosts_path

    # The repository root is supplied explicitly; the package never infers it.
    hosts, digest = load_retrieval_host_profile("electronics", repository_root=REPO_ROOT)
    assert hosts == (
        "docs.arduino.cc", "learn.adafruit.com", "learn.sparkfun.com",
        "support.microbit.org", "www.allaboutcircuits.com", "www.arduino.cc",
        "www.cpsc.gov",
    )
    assert len(digest) == 64
    # Same file, same bytes, same digest -- a deterministic binding, not a random one.
    _, digest2 = load_retrieval_host_profile(
        "electronics", path=default_retrieval_hosts_path(REPO_ROOT))
    assert digest == digest2


def test_load_retrieval_host_profile_rejects_an_unknown_profile_name():
    with pytest.raises(RetrievalHostProfileError, match="not declared"):
        load_retrieval_host_profile("does-not-exist", repository_root=REPO_ROOT)


def test_load_retrieval_host_profile_rejects_a_wildcard_host(tmp_path: Path):
    path = tmp_path / "retrieval_hosts.v1.yaml"
    path.write_text(
        "retrieval_hosts_version: '1.0'\n"
        "profiles:\n"
        "  bad:\n"
        "    hosts: ['*.example.org']\n",
        encoding="utf-8")
    with pytest.raises(RetrievalHostProfileError, match="bare hostname"):
        load_retrieval_host_profile("bad", path=path)


def test_load_retrieval_host_profile_rejects_a_url_instead_of_a_bare_host(tmp_path: Path):
    path = tmp_path / "retrieval_hosts.v1.yaml"
    path.write_text(
        "retrieval_hosts_version: '1.0'\n"
        "profiles:\n"
        "  bad:\n"
        "    hosts: ['https://example.org/']\n",
        encoding="utf-8")
    with pytest.raises(RetrievalHostProfileError, match="bare hostname"):
        load_retrieval_host_profile("bad", path=path)


def test_oversized_response_is_denied(guard: EgressGuard, output_root: Path):
    receipt_grant = grant(make_record(output_root), output_root)
    fetcher = retriever(guard, opener=canned(b"x" * 4096), max_bytes=1024)
    with pytest.raises(EgressDenied) as denied:
        fetcher.fetch("https://standards.example.org/big",
                      authorization_receipt=receipt_grant)
    assert denied.value.reason == "response_too_large"


def test_non_global_resolution_is_denied(guard: EgressGuard, output_root: Path):
    receipt_grant = grant(make_record(output_root), output_root)
    fetcher = retriever(guard, opener=canned(), resolver=lambda host: ("169.254.169.254",))
    with pytest.raises(EgressDenied) as denied:
        fetcher.fetch("https://standards.example.org/meta",
                      authorization_receipt=receipt_grant)
    assert denied.value.reason == "non_global_address"


def test_dns_rebinding_to_an_unpinned_address_is_denied(
    guard: EgressGuard, receipts: ReceiptLog, output_root: Path
):
    receipt_grant = grant(make_record(output_root), output_root)

    def rebinding_opener(url, *, timeout, redirect_validator, max_bytes):
        socket.create_connection(("203.0.113.9", 443), timeout=1)
        raise AssertionError("rebinding connect should never be permitted")

    fetcher = retriever(guard, opener=rebinding_opener)
    with pytest.raises(EgressDenied) as denied:
        fetcher.fetch("https://standards.example.org/spec.html",
                      authorization_receipt=receipt_grant)
    assert denied.value.reason == "dns_rebinding"
    assert receipts.denials[-1]["requested_target"] == "203.0.113.9:443"


def test_unauthorized_retrieval_makes_no_connection(guard: EgressGuard, output_root: Path):
    calls: list[str] = []

    def counting_opener(url, *, timeout, redirect_validator, max_bytes):
        calls.append(url)
        return canned()(url, timeout=timeout)

    fetcher = retriever(guard, opener=counting_opener)
    with pytest.raises(EgressDenied) as absent:
        fetcher.fetch("https://standards.example.org/spec.html", authorization_receipt=None)
    assert absent.value.reason == "authorization_absent"

    wrong_provider = grant(make_record(output_root), output_root, provider="openai",
                           data_classes=("shipped_pdf",))
    with pytest.raises(EgressDenied) as mismatched:
        fetcher.fetch("https://standards.example.org/spec.html",
                      authorization_receipt=wrong_provider)
    assert mismatched.value.reason == "wrong_provider_authorization"
    assert calls == []


def test_only_the_retriever_may_egress_to_an_allowlisted_host(
    guard: EgressGuard, receipts: ReceiptLog, output_root: Path
):
    """The same host the retriever may reach is still denied to any other caller."""
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    port = listener.getsockname()[1]
    accepted: list[socket.socket] = []
    thread = threading.Thread(target=lambda: accepted.append(listener.accept()[0]), daemon=True)
    thread.start()

    receipt_grant = grant(make_record(output_root), output_root)

    def connecting_opener(url, *, timeout, redirect_validator, max_bytes):
        connection = socket.create_connection(("127.0.0.1", port), timeout=2)
        connection.close()
        return RetrievalResponse(
            final_url=f"http://localhost:{port}/spec.txt", status=200,
            headers={"content-type": "text/plain"}, body=b"source bytes")

    policy = RetrievalPolicy(
        allowed_hosts=frozenset({"localhost"}), require_tls=False,
        allow_private_addresses=True)
    fetcher = SourceRetriever(
        guard=guard, policy=policy, resolver=lambda host: ("127.0.0.1",),
        opener=connecting_opener)

    body, receipt = fetcher.fetch(
        f"http://localhost:{port}/spec.txt", authorization_receipt=receipt_grant)
    assert body == b"source bytes"
    assert receipt["outcome"] == "allowed"
    thread.join(timeout=2)

    with pytest.raises(EgressDenied) as denied:
        socket.create_connection(("127.0.0.1", port), timeout=1)
    assert denied.value.reason == "unauthorized_socket_no_active_retrieval"
    for opened in accepted:
        opened.close()
    listener.close()


def test_grant_does_not_leak_past_the_retrieval(guard: EgressGuard, output_root: Path):
    receipt_grant = grant(make_record(output_root), output_root)
    fetcher = retriever(guard, opener=canned())
    fetcher.fetch("https://standards.example.org/spec.html",
                  authorization_receipt=receipt_grant)
    with pytest.raises(EgressDenied) as denied:
        socket.socket().connect(("93.184.216.34", 443))
    assert denied.value.reason == "unauthorized_socket_no_active_retrieval"
