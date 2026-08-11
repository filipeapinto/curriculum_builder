"""N13 egress broker and external-data authorization tests (spec 7.4, 9)."""
from __future__ import annotations

import hashlib
import http.client
import socket
import threading
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from runtime.langgraph_factory.egress import (
    MODEL_API_HOSTS,
    AuthorizationDenied,
    AuthorizationRecord,
    EgressDenied,
    EgressGuard,
    ReceiptLog,
    RetrievalPolicy,
    RetrievalResponse,
    SourceRetriever,
    authorize_subprocess_transmission,
    authorize_transmission,
)

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
            "openai": ["manifest_unit_projection", "schemas_and_rubrics"],
            "google": ["shipped_pdf", "rasterized_pages"],
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


# --------------------------------------------------------------- authorization record


def test_record_rejects_unknown_provider_and_undeclared_data_class(output_root: Path):
    with pytest.raises(AuthorizationDenied) as unknown:
        make_record(output_root, providers={"anthropic": ["shipped_pdf"]})
    assert unknown.value.reason == "unknown_provider"

    with pytest.raises(AuthorizationDenied) as undeclared:
        make_record(output_root, providers={"google": ["manifest_unit_projection"]})
    assert undeclared.value.reason == "undeclared_data_class"


@pytest.mark.parametrize(
    ("mutation", "expected_reason"),
    [
        ({"record": None}, "authorization_absent"),
        ({"run_id": "some-other-run"}, "wrong_run_scope"),
        ({"curriculum_digest": OTHER_DIGEST}, "wrong_curriculum_digest"),
        ({"provider": "google", "data_classes": ("shipped_pdf",),
          "output_root": "elsewhere"}, "wrong_output_scope"),
        ({"provider": "primary_source_hosts",
          "data_classes": ("primary_source_bytes",), "drop_provider": True},
         "provider_not_authorized"),
        ({"provider": "openai", "data_classes": ("named_repair_findings",)},
         "data_class_not_authorized"),
        ({"expired": True}, "authorization_expired"),
    ],
)
def test_authorization_fails_closed_for_every_scope_mismatch(
    tmp_path: Path, output_root: Path, mutation, expected_reason
):
    providers = None
    if mutation.get("drop_provider"):
        providers = {"openai": ["manifest_unit_projection"]}
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
            provider=mutation.get("provider", "openai"),
            data_classes=mutation.get("data_classes", ("manifest_unit_projection",)),
            curriculum_digest=mutation.get("curriculum_digest", CURRICULUM_DIGEST),
            run_id=mutation.get("run_id", RUN_ID),
            output_root=root,
        )
    assert denied.value.reason == expected_reason


def test_granted_receipt_carries_full_scope(output_root: Path):
    receipt = grant(make_record(output_root), output_root, provider="openai",
                    data_classes=("manifest_unit_projection",))
    assert receipt["decision"] == "granted"
    assert receipt["provider"] == "openai"
    assert receipt["curriculum_digest"] == CURRICULUM_DIGEST
    assert receipt["run_id"] == RUN_ID
    assert receipt["output_root"] == str(output_root.resolve())
    assert len(receipt["authorization_digest"]) == 64


def test_subprocess_authorization_receipts_both_outcomes(output_root: Path, receipts: ReceiptLog):
    authorize_subprocess_transmission(
        make_record(output_root), provider="openai",
        data_classes=("manifest_unit_projection",), curriculum_digest=CURRICULUM_DIGEST,
        run_id=RUN_ID, output_root=output_root, receipts=receipts)
    assert receipts.allowed[-1]["channel"] == "subprocess_transmission"

    with pytest.raises(AuthorizationDenied):
        authorize_subprocess_transmission(
            None, provider="openai", data_classes=("manifest_unit_projection",),
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
    return lambda url, *, timeout: RetrievalResponse(**payload)


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

    def rebinding_opener(url, *, timeout):
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

    def counting_opener(url, *, timeout):
        calls.append(url)
        return canned()(url, timeout=timeout)

    fetcher = retriever(guard, opener=counting_opener)
    with pytest.raises(EgressDenied) as absent:
        fetcher.fetch("https://standards.example.org/spec.html", authorization_receipt=None)
    assert absent.value.reason == "authorization_absent"

    wrong_provider = grant(make_record(output_root), output_root, provider="google",
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

    def connecting_opener(url, *, timeout):
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
