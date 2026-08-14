"""N22 acceptance tests: the deterministic node catalogue.

Nine TEST items from `prompts/N22_deterministic_nodes.prompt.v2.md`, scoped to the
node set `contracts/node_ownership.v1.md` assigns to N22.
"""

from __future__ import annotations

import ast
import hashlib
import json
import random
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from runtime.langgraph_factory import nodes as node_pkg
from runtime.langgraph_factory.nodes import (
    NODE_CATALOGUE,
    ConvergenceExhausted,
    PrerequisitePause,
    SystemFailure,
    canonical_digest,
    content,
    domain,
    inputs,
    node_registry,
    project,
    render,
    review,
    sources,
    terminal,
    visuals,
)
from runtime.langgraph_factory.state import FIELD_REDUCER_CLASSES

PACKAGE_ROOT = Path(node_pkg.__file__).resolve().parent
FACTORY_ROOT = PACKAGE_ROOT.parent
REPO_ROOT = FACTORY_ROOT.parents[1]
CURRICULA_ROOT = REPO_ROOT / "curricula"
NODE_MODULES = (inputs, sources, domain, content, visuals, render, review, terminal)

# Every worker dispatch is correlated to a run and an episode (spec section 10),
# so a node that stages one reads both.
_CORRELATION = {"run_id": "run-1", "episode_id": "ep-1"}


def _inspected_page(number: int, **overrides: Any) -> dict[str, Any]:
    """One page as the rasterizing inspector reports it."""

    return {
        "number": number,
        "problems": [],
        "page_sha256": hashlib.sha256(f"page-{number}".encode()).hexdigest(),
        "image_path": f"/tmp/page-{number}.png",
        **overrides,
    }


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


class _Token:
    def __init__(self, value: bool = False) -> None:
        self._value = value

    def is_set(self) -> bool:
        return self._value


class _Registry:
    """A stub of the runtime context's transport registry.

    It is deliberately not the real transport: these tests exercise node logic,
    and a node that reached a real CLI here would be a node violating its own
    contract.
    """

    def __init__(self, **handlers: Any) -> None:
        self._handlers = handlers

    def __getattr__(self, name: str) -> Any:
        try:
            return self._handlers[name]
        except KeyError:
            raise AttributeError(name) from None


class _Context:
    def __init__(self, **services: Any) -> None:
        self.engine_root = services.pop("engine_root", Path("/tmp"))
        self.output_root = services.pop("output_root", Path("/tmp/out"))
        self.path_guard = object()
        self.evidence_service = object()
        self.transport_registry = services.pop("transport_registry", _Registry())
        self.source_retriever = services.pop("source_retriever", None)
        self.signal_token = services.pop("signal_token", _Token())
        self.clock = services.pop("clock", lambda: "2026-01-01T00:00:00Z")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _synthetic_manifest(
    tmp_path: Path, unit_count: int, edges: dict[int, list[int]] | None = None, *, shuffle_seed: int | None = None
) -> tuple[Path, list[str]]:
    """Write a manifest with ``unit_count`` generically-named units and a chosen DAG."""

    unit_ids = [f"U{index:03d}" for index in range(1, unit_count + 1)]
    units = []
    for index, unit_id in enumerate(unit_ids, start=1):
        prerequisites = [unit_ids[target - 1] for target in (edges or {}).get(index, [])]
        units.append(
            {
                "id": unit_id,
                "title": f"synthetic unit {index}",
                "sequence": {"prerequisites": prerequisites, "prepares_for": []},
                "required_explanation": [f"fact {index}"],
            }
        )
    if shuffle_seed is not None:
        random.Random(shuffle_seed).shuffle(units)
    curriculum_root = tmp_path / "curricula" / "synthetic"
    curriculum_root.mkdir(parents=True, exist_ok=True)
    path = curriculum_root / "synthetic_curriculum.v1.yaml"
    path.write_text(yaml.safe_dump({"labs": units}, sort_keys=False), encoding="utf-8")
    return path, [unit["id"] for unit in units]


def _d02_state(manifest_path: Path, mode: str, requested: str | None) -> dict[str, Any]:
    return {
        "engine_root": str(manifest_path.parents[2]),
        "curriculum_root": str(manifest_path.parent),
        "active_manifest_path": str(manifest_path),
        "mode": mode,
        "requested_unit_id": requested,
        "frozen_inputs": [
            {"path": str(manifest_path), "sha256": _sha256_file(manifest_path), "role": "active_manifest"}
        ],
    }


# ---------------------------------------------------------------------------
# TEST 1 — one implementation per owned node; one terminal writer
# ---------------------------------------------------------------------------


OWNED_NODE_IDS = (
    "D00_BOOTSTRAP_EPISODE",
    "D00R_REVALIDATE_RESUME_IDENTITY",
    "D01_VALIDATE_AND_FREEZE_INPUTS",
    "D02_COMPILE_EFFECTIVE_RUN",
    "D03_PROVE_CAPABILITIES",
    "D04_INITIALIZE_OR_RESUME",
    "D92_REENTER_VALIDATED_FRONTIER",
    "D96_GRACEFUL_INTERRUPT_GATE",
    "D05_SELECT_NEXT_UNIT",
    "D06_COMPILE_SOURCE_REQUESTS",
    "D06B_RETRIEVE_SOURCE_CANDIDATES",
    "D07_CORRELATE_AND_ADMIT_SOURCES",
    "D30_CLASSIFY_PREREQUISITE",
    "D08_VALIDATE_DOMAIN",
    "D09_VALIDATE_CONTENT",
    "D10_COMPILE_VISUAL_BRIEFS",
    "D11_CREATE_DETERMINISTIC_VISUALS",
    "D12_VISUAL_BARRIER_AND_JOIN",
    "D13_RENDER_UNIT",
    "D14_INVENTORY_AND_INSPECT_UNIT_PAGES",
    "D15_FREEZE_UNIT_REVIEW_PACKET",
    "D98_WRITE_TERMINAL",
)


def test_catalogue_covers_exactly_the_owned_node_set() -> None:
    assert sorted(NODE_CATALOGUE) == sorted(OWNED_NODE_IDS)
    assert len(OWNED_NODE_IDS) == 22


def test_every_owned_node_has_exactly_one_implementation() -> None:
    registry = node_registry()
    assert sorted(registry) == sorted(OWNED_NODE_IDS)

    definitions: dict[str, list[str]] = {}
    for module in NODE_MODULES:
        tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
        for statement in tree.body:
            name = getattr(statement, "name", None) or (
                statement.targets[0].id
                if isinstance(statement, ast.Assign) and isinstance(statement.targets[0], ast.Name)
                else None
            )
            if name in NODE_CATALOGUE:
                definitions.setdefault(name, []).append(module.__name__)
    assert sorted(definitions) == sorted(OWNED_NODE_IDS)
    for node_id, modules in definitions.items():
        assert modules == [f"runtime.langgraph_factory.nodes.{NODE_CATALOGUE[node_id].module}"], node_id


def test_terminal_module_is_the_sole_terminal_writer() -> None:
    """No module in the nodes package but `terminal.py` produces a `terminal` update."""

    offenders: list[str] = []
    for path in sorted(PACKAGE_ROOT.rglob("*.py")):
        if path == Path(terminal.__file__) or "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for statement in ast.walk(tree):
            if not isinstance(statement, ast.Dict):
                continue
            keys = [key.value for key in statement.keys if isinstance(key, ast.Constant)]
            # A channel update is a dict whose keys are all state channels. The
            # module registry also has a "terminal" key, but its siblings are
            # module names, so it is structurally not an update.
            if "terminal" in keys and all(key in FIELD_REDUCER_CLASSES for key in keys):
                offenders.append(f"{path.relative_to(PACKAGE_ROOT)}:{statement.lineno}")
    assert offenders == [], f"a second terminal writer exists: {offenders}"

    writers = [
        node_id for node_id, spec in NODE_CATALOGUE.items() if "terminal" in spec.outputs
    ]
    assert writers == ["D98_WRITE_TERMINAL"]


def test_no_node_but_d98_can_write_a_terminal_even_if_it_tries() -> None:
    """The channel authorization check, not convention, is what enforces sole ownership."""

    for node_id in OWNED_NODE_IDS:
        if node_id == "D98_WRITE_TERMINAL":
            continue

        @node_pkg.deterministic_node(node_id)
        def impostor(projection: dict[str, Any], context: Any) -> dict[str, Any]:
            return {"terminal": {"kind": "COMPLETE"}}

        with pytest.raises(node_pkg.CatalogueViolation, match="unauthorized channels"):
            impostor({}, None)


def test_write_terminal_is_the_only_terminal_producing_callable() -> None:
    producers: list[str] = []
    tree = ast.parse(Path(terminal.__file__).read_text(encoding="utf-8"))
    for function in tree.body:
        if not isinstance(function, ast.FunctionDef):
            continue
        for statement in ast.walk(function):
            if isinstance(statement, ast.Dict) and any(
                isinstance(key, ast.Constant) and key.value == "terminal"
                for key in statement.keys
            ):
                producers.append(function.name)
    assert sorted(set(producers)) == ["write_terminal"]


# ---------------------------------------------------------------------------
# TEST 2 — projection/update fields equal the frozen catalogue
# ---------------------------------------------------------------------------


# Transcribed from spec section 6.2's "Output / reducer" column: the reducer
# words the spec itself uses for each node, checked against N11's declared
# channel reducers. This catches a node writing the right channel name through
# the wrong reducer class as surely as it catches a wrong channel.
SPEC_OUTPUT_REDUCERS: dict[str, set[str]] = {
    "D00_BOOTSTRAP_EPISODE": {"write_once", "replace_current"},
    "D00R_REVALIDATE_RESUME_IDENTITY": {"append_unique", "replace_current"},
    "D01_VALIDATE_AND_FREEZE_INPUTS": {"write_once"},
    "D02_COMPILE_EFFECTIVE_RUN": {"write_once"},
    "D03_PROVE_CAPABILITIES": {"append_unique"},
    "D04_INITIALIZE_OR_RESUME": {
        "write_once",
        "append_unique",
        "advance_head",
        "monotonic_max",
        "monotonic_status",
    },
    "D92_REENTER_VALIDATED_FRONTIER": {"append_unique", "replace_current"},
    "D96_GRACEFUL_INTERRUPT_GATE": {"replace_current"},
    "D05_SELECT_NEXT_UNIT": {"replace_current", "monotonic_max", "monotonic_status"},
    "D06_COMPILE_SOURCE_REQUESTS": {"append_unique", "union_disjoint", "replace_current"},
    "D06B_RETRIEVE_SOURCE_CANDIDATES": {"union_disjoint", "replace_current"},
    "D07_CORRELATE_AND_ADMIT_SOURCES": {"append_unique", "replace_current"},
    "D30_CLASSIFY_PREREQUISITE": {"append_unique", "replace_current"},
    "D08_VALIDATE_DOMAIN": {"append_unique", "advance_head", "replace_current"},
    "D09_VALIDATE_CONTENT": {"append_unique", "advance_head"},
    "D10_COMPILE_VISUAL_BRIEFS": {"append_unique", "union_disjoint", "replace_current"},
    "D11_CREATE_DETERMINISTIC_VISUALS": {"union_disjoint"},
    "D12_VISUAL_BARRIER_AND_JOIN": {"append_unique", "advance_head", "replace_current"},
    "D13_RENDER_UNIT": {"append_unique"},
    "D14_INVENTORY_AND_INSPECT_UNIT_PAGES": {"append_unique"},
    "D15_FREEZE_UNIT_REVIEW_PACKET": {"append_unique", "replace_current"},
    "D98_WRITE_TERMINAL": {"write_episode_terminal_once", "append_unique"},
}

# Transcribed from spec section 6.2's "Explicit retry and failure class" column.
SPEC_FAILURE_CLASSES: dict[str, set[str]] = {
    "D00_BOOTSTRAP_EPISODE": {"system"},
    "D00R_REVALIDATE_RESUME_IDENTITY": {"system"},
    "D01_VALIDATE_AND_FREEZE_INPUTS": {"system"},
    "D02_COMPILE_EFFECTIVE_RUN": {"system"},
    "D03_PROVE_CAPABILITIES": {"system", "pause"},
    "D04_INITIALIZE_OR_RESUME": {"system"},
    "D92_REENTER_VALIDATED_FRONTIER": {"system"},
    "D96_GRACEFUL_INTERRUPT_GATE": {"system"},
    "D05_SELECT_NEXT_UNIT": {"system"},
    "D06_COMPILE_SOURCE_REQUESTS": {"pause"},
    "D06B_RETRIEVE_SOURCE_CANDIDATES": {"system", "pause"},
    "D07_CORRELATE_AND_ADMIT_SOURCES": {"system"},
    "D30_CLASSIFY_PREREQUISITE": {"system"},
    "D08_VALIDATE_DOMAIN": {"system"},
    "D09_VALIDATE_CONTENT": {"system"},
    "D10_COMPILE_VISUAL_BRIEFS": {"system"},
    "D11_CREATE_DETERMINISTIC_VISUALS": {"system"},
    "D12_VISUAL_BARRIER_AND_JOIN": {"system"},
    "D13_RENDER_UNIT": {"system"},
    "D14_INVENTORY_AND_INSPECT_UNIT_PAGES": {"system"},
    "D15_FREEZE_UNIT_REVIEW_PACKET": {"system"},
    "D98_WRITE_TERMINAL": {"system"},
}


@pytest.mark.parametrize("node_id", OWNED_NODE_IDS)
def test_output_reducer_classes_match_the_spec_catalogue(node_id: str) -> None:
    spec = NODE_CATALOGUE[node_id]
    actual = {FIELD_REDUCER_CLASSES[field] for field in spec.outputs}
    assert actual == SPEC_OUTPUT_REDUCERS[node_id], node_id


@pytest.mark.parametrize("node_id", OWNED_NODE_IDS)
def test_failure_classes_match_the_spec_catalogue(node_id: str) -> None:
    assert set(NODE_CATALOGUE[node_id].failure_classes) == SPEC_FAILURE_CLASSES[node_id]


@pytest.mark.parametrize("node_id", OWNED_NODE_IDS)
def test_projection_is_exactly_the_authorized_input_set(node_id: str) -> None:
    """A node sees its declared inputs and nothing else, whatever state it is handed."""

    fat_state = {field: {"leaked": True} for field in FIELD_REDUCER_CLASSES}
    projection = project(node_id, fat_state)
    assert sorted(projection) == sorted(NODE_CATALOGUE[node_id].inputs)


def test_no_node_writes_an_unauthorized_channel(tmp_path: Path) -> None:
    manifest_path, unit_ids = _synthetic_manifest(tmp_path, 3, {2: [1], 3: [2]})
    state = _d02_state(manifest_path, "one", unit_ids[2])
    update = inputs.D02_COMPILE_EFFECTIVE_RUN(state, _Context())
    assert set(update) <= set(NODE_CATALOGUE["D02_COMPILE_EFFECTIVE_RUN"].outputs) | {
        "pending_failure",
        "pending_guard",
    }
    assert "effective_run" in update


def test_writing_an_unauthorized_channel_is_rejected() -> None:
    @node_pkg.deterministic_node("D05_SELECT_NEXT_UNIT")
    def rogue(projection: dict[str, Any], context: Any) -> dict[str, Any]:
        return {"terminal": {"kind": "COMPLETE"}}

    with pytest.raises(node_pkg.CatalogueViolation, match="unauthorized channels"):
        rogue({}, None)


# ---------------------------------------------------------------------------
# TEST 3 — expected failures are typed; unexpected failures propagate
# ---------------------------------------------------------------------------


def test_expected_pause_lands_in_pending_failure_with_the_pause_class() -> None:
    state = {
        "selected_unit_id": "U001",
        "source_requests": [
            {"key": "U001/1/f", "unit_id": "U001", "required": True, "scope": "required_explanation"}
        ],
        "source_denominators": {
            "U001/1": {"unit_id": "U001", "source_epoch": 1, "request_keys": ["U001/1/f"], "size": 1}
        },
        "source_discoveries": {},
        "external_authorizations": [{"providers": {"primary_source_hosts": ["primary_source_bytes"]}, "approved_at_utc": "2026-01-01T00:00:00Z", "expires_at_utc": "2099-01-01T00:00:00Z", "curriculum_digest": "c" * 64, "output_root": "/tmp/out"}],
    }
    context = _Context(source_retriever=_Registry(fetch=lambda *args: {}))
    update = sources.D06B_RETRIEVE_SOURCE_CANDIDATES(state, context)

    failure = update["pending_failure"]
    assert failure["class"] == "pause"
    assert failure["cause"] == "required_external_fact_unavailable"
    assert failure["node"] == "D06B_RETRIEVE_SOURCE_CANDIDATES"
    assert "retrievals" not in update, "a paused node must not admit partial retrievals"


def test_expected_system_failure_lands_in_pending_failure_with_the_system_class() -> None:
    state = {
        "effective_run": {"target_closure": ["U001", "U002"]},
        "cursor": {"manifest_ordinal": 0, "accepted_ordinal": 9},
        "accepted_unit_receipts": {},
        "unit_status": {},
    }
    update = sources.D05_SELECT_NEXT_UNIT(state, _Context())
    assert update["pending_failure"]["class"] == "system"
    assert update["pending_failure"]["cause"] == "integrity"
    assert update["pending_guard"] is None


def test_a_retrieval_tool_fault_is_a_system_failure_not_a_pause() -> None:
    """Spec 2.4/6: only a named unavailable fact may pause; a tool fault may not."""

    def exploding_fetch(*args: Any) -> Any:
        raise ConnectionResetError("TLS handshake aborted")

    state = {
        "selected_unit_id": "U001",
        "source_requests": [
            {"key": "U001/1/f", "unit_id": "U001", "required": True, "scope": "required_explanation"}
        ],
        "source_denominators": {
            "U001/1": {"unit_id": "U001", "source_epoch": 1, "request_keys": ["U001/1/f"], "size": 1}
        },
        "source_discoveries": {"U001/1/f": {"locators": [
            {"request_id": "U001/1/f", "url": "https://example.invalid/a", "title": "t",
             "publisher": "p", "locator_kind": "primary", "rationale": "why"}]}},
        "external_authorizations": [{"providers": {"primary_source_hosts": ["primary_source_bytes"]}, "approved_at_utc": "2026-01-01T00:00:00Z", "expires_at_utc": "2099-01-01T00:00:00Z", "curriculum_digest": "c" * 64, "output_root": "/tmp/out"}],
    }
    context = _Context(source_retriever=_Registry(fetch=exploding_fetch))
    update = sources.D06B_RETRIEVE_SOURCE_CANDIDATES(state, context)
    assert update["pending_failure"]["class"] == "system"
    assert update["pending_failure"]["cause"] == "tool"


def test_D06B_calls_the_real_source_retriever_fetch_signature() -> None:
    """N30V7-F03 regression: D06B's own call into SourceRetriever.fetch (egress.py)
    passed a third positional argument -- `requests[request_key].get("scope")`, a
    fact-category tag like "applications", never a legitimate `data_class` -- against
    a keyword-only `authorization_receipt`/`data_class` signature, always raising
    "SourceRetriever.fetch() takes 2 positional arguments but 4 were given" the
    moment a real discovery ever produced a locator to retrieve. Every prior test
    here stubbed `fetch` with `lambda *args: ...`, which accepts any positional
    call shape and so never caught the mismatch -- live-verified against a real
    N70 production run reaching this exact call for the first time. This stub
    mirrors the real method's keyword-only contract exactly.
    """

    def real_shaped_fetch(locator: str, *, authorization_receipt: Any,
                          data_class: str = "primary_source_bytes") -> dict[str, Any]:
        assert authorization_receipt is not None
        assert data_class == "primary_source_bytes"
        return {"sha256": "a" * 64, "status": 200, "content_type": "text/html"}

    state = {
        "selected_unit_id": "U001",
        "run_id": "run-x",
        "episode_id": "ep-x",
        "effective_run": {"unit_records": [{"id": "U001", "title": "Unit One"}]},
        "source_requests": [
            {"key": "U001/1/f", "unit_id": "U001", "required": True, "scope": "applications",
             "source_epoch": 1, "fact_id": "f", "question": "q?"}
        ],
        "source_denominators": {
            "U001/1": {"unit_id": "U001", "source_epoch": 1, "request_keys": ["U001/1/f"], "size": 1}
        },
        "source_discoveries": {"U001/1/f": {"locators": [
            {"request_id": "U001/1/f", "url": "https://example.invalid/a", "title": "t",
             "publisher": "p", "locator_kind": "primary", "rationale": "why"}]}},
        "external_authorizations": [{"providers": {"primary_source_hosts": ["primary_source_bytes"]}, "approved_at_utc": "2026-01-01T00:00:00Z", "expires_at_utc": "2099-01-01T00:00:00Z", "curriculum_digest": "c" * 64, "output_root": "/tmp/out"}],
    }
    context = _Context(source_retriever=_Registry(fetch=real_shaped_fetch))
    update = sources.D06B_RETRIEVE_SOURCE_CANDIDATES(state, context)

    assert "pending_failure" not in update
    assert update["retrievals"]["U001/1/f"]["sha256"] == "a" * 64


def test_D06B_mints_a_real_provider_scoped_receipt_not_the_raw_declaration() -> None:
    """N30V7-F06 regression: D06B passed the raw, multi-provider authorization
    DECLARATION straight through as if it were already a per-provider RECEIPT.
    `SourceRetriever.fetch` requires `authorization_receipt["provider"] ==
    "primary_source_hosts"` -- a field the raw declaration never carries -- so
    every real retrieval was denied with `wrong_provider_authorization`, live-
    verified against a real N70 production run only after WebSearch (N20V7-F13)
    and the locator.url fix (N30V7-F05) let a genuine retrieval attempt happen
    for the first time. D06B now mints a real receipt via `authorize_transmission`
    from the frozen (write-once) declaration plus its own trusted `run_id`.
    """

    seen: dict[str, Any] = {}

    def recording_fetch(locator: str, *, authorization_receipt: Any,
                        data_class: str = "primary_source_bytes") -> dict[str, Any]:
        seen["receipt"] = authorization_receipt
        return {"sha256": "b" * 64, "status": 200, "content_type": "text/html"}

    state = {
        "selected_unit_id": "U001",
        "run_id": "run-x",
        "episode_id": "ep-x",
        "effective_run": {"unit_records": [{"id": "U001", "title": "Unit One"}]},
        "source_requests": [
            {"key": "U001/1/f", "unit_id": "U001", "required": True, "scope": "applications",
             "source_epoch": 1, "fact_id": "f", "question": "q?"}
        ],
        "source_denominators": {
            "U001/1": {"unit_id": "U001", "source_epoch": 1, "request_keys": ["U001/1/f"], "size": 1}
        },
        "source_discoveries": {"U001/1/f": {"locators": [
            {"request_id": "U001/1/f", "url": "https://example.invalid/a", "title": "t",
             "publisher": "p", "locator_kind": "primary", "rationale": "why"}]}},
        "external_authorizations": [{"providers": {"primary_source_hosts": ["primary_source_bytes"]},
                                     "approved_at_utc": "2026-01-01T00:00:00Z",
                                     "expires_at_utc": "2099-01-01T00:00:00Z",
                                     "curriculum_digest": "c" * 64, "output_root": "/tmp/out"}],
    }
    context = _Context(source_retriever=_Registry(fetch=recording_fetch))
    update = sources.D06B_RETRIEVE_SOURCE_CANDIDATES(state, context)

    assert "pending_failure" not in update
    assert seen["receipt"]["provider"] == "primary_source_hosts"
    assert "primary_source_bytes" in seen["receipt"]["data_classes"]


def test_D06B_denies_retrieval_when_the_declaration_never_authorized_source_hosts() -> None:
    """The provider check must still deny honestly when primary_source_hosts truly
    isn't authorized -- proving the fix does not just always pass.
    """

    state = {
        "selected_unit_id": "U001",
        "run_id": "run-x",
        "episode_id": "ep-x",
        "effective_run": {"unit_records": [{"id": "U001", "title": "Unit One"}]},
        "source_requests": [
            {"key": "U001/1/f", "unit_id": "U001", "required": True, "scope": "applications",
             "source_epoch": 1, "fact_id": "f", "question": "q?"}
        ],
        "source_denominators": {
            "U001/1": {"unit_id": "U001", "source_epoch": 1, "request_keys": ["U001/1/f"], "size": 1}
        },
        "source_discoveries": {"U001/1/f": {"locators": [
            {"request_id": "U001/1/f", "url": "https://example.invalid/a", "title": "t",
             "publisher": "p", "locator_kind": "primary", "rationale": "why"}]}},
        "external_authorizations": [{"providers": {"anthropic": ["schemas_and_rubrics"]},
                                     "approved_at_utc": "2026-01-01T00:00:00Z",
                                     "expires_at_utc": "2099-01-01T00:00:00Z",
                                     "curriculum_digest": "c" * 64, "output_root": "/tmp/out"}],
    }
    context = _Context(source_retriever=_Registry(fetch=lambda *a, **k: {}))
    update = sources.D06B_RETRIEVE_SOURCE_CANDIDATES(state, context)

    assert update["pending_failure"]["class"] == "system"
    assert update["pending_failure"]["cause"] == "tool"


def test_an_unexpected_exception_is_not_caught_inside_the_node(monkeypatch: Any) -> None:
    class Unexpected(Exception):
        pass

    def explode(*args: Any, **kwargs: Any) -> Any:
        raise Unexpected("a defect nobody classified")

    monkeypatch.setattr(sources, "compile_unit_source_requests", explode)
    state = {
        "effective_run": {"unit_records": [{"id": "U001", "required_explanation": ["a"]}]},
        "selected_unit_id": "U001",
        "source_admissions": [],
        "engine_root": "/tmp",
    }
    with pytest.raises(Unexpected):
        sources.D06_COMPILE_SOURCE_REQUESTS(state, _Context())


def test_every_declared_failure_class_is_reachable_by_a_typed_exception() -> None:
    assert PrerequisitePause("required_external_fact_unavailable", "x").failure_class == "pause"
    assert SystemFailure("tool", "x").failure_class == "system"
    assert ConvergenceExhausted("attempt_bound", "x").failure_class == "exhaustion"

    with pytest.raises(node_pkg.CatalogueViolation):
        node_pkg.failure_record("D05_SELECT_NEXT_UNIT", SystemFailure("not_a_cause", "x"))


# ---------------------------------------------------------------------------
# TEST 4 — manifest-neutral closure over 1, 7, and 41-unit DAGs
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("unit_count", [1, 7, 41])
def test_closure_of_a_linear_chain_is_the_whole_prefix(tmp_path: Path, unit_count: int) -> None:
    edges = {index: [index - 1] for index in range(2, unit_count + 1)}
    manifest_path, _ = _synthetic_manifest(tmp_path / str(unit_count), unit_count, edges)
    target = f"U{unit_count:03d}"

    update = inputs.D02_COMPILE_EFFECTIVE_RUN(
        _d02_state(manifest_path, "one", target), _Context()
    )
    effective_run = update["effective_run"]
    assert effective_run["target_closure"] == [f"U{i:03d}" for i in range(1, unit_count + 1)]
    assert len(effective_run["ordered_unit_ids"]) == unit_count


@pytest.mark.parametrize("unit_count", [1, 7, 41])
@pytest.mark.parametrize("seed", [1, 2, 3])
def test_closure_is_manifest_order_neutral_under_shuffling(
    tmp_path: Path, unit_count: int, seed: int
) -> None:
    """Declaration order changes; the computed closure set does not."""

    edges = {index: [index - 1] for index in range(2, unit_count + 1)}
    root = tmp_path / f"{unit_count}-{seed}"
    manifest_path, declared_order = _synthetic_manifest(root, unit_count, edges, shuffle_seed=seed)
    target = f"U{unit_count:03d}"

    update = inputs.D02_COMPILE_EFFECTIVE_RUN(
        _d02_state(manifest_path, "one", target), _Context()
    )
    effective_run = update["effective_run"]
    assert set(effective_run["target_closure"]) == {f"U{i:03d}" for i in range(1, unit_count + 1)}
    # The closure is emitted in the manifest's own declared order, whatever it is.
    assert effective_run["target_closure"] == [
        unit_id for unit_id in declared_order if unit_id in set(effective_run["target_closure"])
    ]
    assert effective_run["ordered_unit_ids"] == declared_order


def test_closure_is_a_partial_slice_not_the_whole_manifest(tmp_path: Path) -> None:
    """A 41-unit manifest with a shallow target closes over only its ancestors."""

    edges = {index: [1] for index in range(2, 42)}
    edges[3] = [2]
    manifest_path, _ = _synthetic_manifest(tmp_path, 41, edges)

    update = inputs.D02_COMPILE_EFFECTIVE_RUN(
        _d02_state(manifest_path, "one", "U003"), _Context()
    )
    assert update["effective_run"]["target_closure"] == ["U001", "U002", "U003"]


def test_diamond_closure_admits_each_ancestor_exactly_once(tmp_path: Path) -> None:
    manifest_path, _ = _synthetic_manifest(tmp_path, 7, {2: [1], 3: [1], 4: [2, 3], 7: [4]})
    update = inputs.D02_COMPILE_EFFECTIVE_RUN(
        _d02_state(manifest_path, "one", "U007"), _Context()
    )
    closure = update["effective_run"]["target_closure"]
    assert closure == ["U001", "U002", "U003", "U004", "U007"]
    assert len(closure) == len(set(closure))


def test_all_mode_closure_is_the_entire_ordered_manifest(tmp_path: Path) -> None:
    manifest_path, order = _synthetic_manifest(tmp_path, 41, {i: [i - 1] for i in range(2, 42)})
    update = inputs.D02_COMPILE_EFFECTIVE_RUN(_d02_state(manifest_path, "all", None), _Context())
    assert update["effective_run"]["target_closure"] == order
    assert update["effective_run"]["mode"] == "all"


def test_a_prerequisite_cycle_is_rejected_by_name(tmp_path: Path) -> None:
    manifest_path, _ = _synthetic_manifest(tmp_path, 7, {1: [3], 2: [1], 3: [2]})
    update = inputs.D02_COMPILE_EFFECTIVE_RUN(
        _d02_state(manifest_path, "one", "U002"), _Context()
    )
    failure = update["pending_failure"]
    assert failure["class"] == "system"
    assert failure["cause"] == "schema_contract"
    assert "cycle" in failure["message"]


def test_a_self_referential_prerequisite_is_a_cycle(tmp_path: Path) -> None:
    manifest_path, _ = _synthetic_manifest(tmp_path, 3, {2: [2]})
    update = inputs.D02_COMPILE_EFFECTIVE_RUN(
        _d02_state(manifest_path, "one", "U002"), _Context()
    )
    assert "cycle" in update["pending_failure"]["message"]


def test_an_unknown_prerequisite_id_is_rejected(tmp_path: Path) -> None:
    manifest_path, _ = _synthetic_manifest(tmp_path, 3, {})
    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    raw["labs"][1]["sequence"]["prerequisites"] = ["U999"]
    manifest_path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")

    update = inputs.D02_COMPILE_EFFECTIVE_RUN(
        _d02_state(manifest_path, "one", "U002"), _Context()
    )
    assert update["pending_failure"]["cause"] == "schema_contract"
    assert "U999" in update["pending_failure"]["message"]


def test_an_unknown_requested_target_is_rejected(tmp_path: Path) -> None:
    manifest_path, _ = _synthetic_manifest(tmp_path, 7, {})
    update = inputs.D02_COMPILE_EFFECTIVE_RUN(
        _d02_state(manifest_path, "one", "U404"), _Context()
    )
    assert update["pending_failure"]["cause"] == "invalid_input"


def test_a_manifest_altered_after_freezing_is_rejected(tmp_path: Path) -> None:
    manifest_path, _ = _synthetic_manifest(tmp_path, 3, {})
    state = _d02_state(manifest_path, "one", "U002")
    manifest_path.write_text(manifest_path.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")

    update = inputs.D02_COMPILE_EFFECTIVE_RUN(state, _Context())
    assert update["pending_failure"]["cause"] == "integrity"


def test_a_deep_chain_does_not_exhaust_the_interpreter_stack(tmp_path: Path) -> None:
    """The closure is iterative, so depth is bounded by the manifest, not by Python."""

    depth = 2000
    unit_records = [
        {"id": f"U{index:04d}", "sequence": {"prerequisites": [f"U{index - 1:04d}"] if index > 1 else []}}
        for index in range(1, depth + 1)
    ]
    closure = inputs.compile_prerequisite_closure(unit_records, f"U{depth:04d}")
    assert len(closure) == depth


# ---------------------------------------------------------------------------
# TEST 5 — stale inputs fail closed
# ---------------------------------------------------------------------------


def test_d07_rejects_an_interpretation_derived_from_superseded_bytes() -> None:
    state = {
        "selected_unit_id": "U001",
        "source_denominators": {
            "U001/1": {"unit_id": "U001", "source_epoch": 1, "request_keys": ["k1"], "size": 1}
        },
        "source_discoveries": {},
        "retrievals": {"k1": {"unit_id": "U001", "sha256": "current" * 8, "locator": "x"}},
        "source_interpretations": {"k1": {"unit_id": "U001", "retrieval_sha256": "stale" * 8}},
        "source_requests": [],
    }
    update = sources.D07_CORRELATE_AND_ADMIT_SOURCES(state, _Context())
    assert update["pending_failure"]["cause"] == "integrity"
    assert "source_admissions" not in update


def test_d07_rejects_a_cross_unit_join_member() -> None:
    state = {
        "selected_unit_id": "U001",
        "source_denominators": {
            "U001/1": {"unit_id": "U001", "source_epoch": 1, "request_keys": ["k1"], "size": 1}
        },
        "source_discoveries": {},
        "retrievals": {"k1": {"unit_id": "U002", "sha256": "a" * 64, "locator": "x"}},
        "source_interpretations": {"k1": {"unit_id": "U001", "retrieval_sha256": "a" * 64}},
        "source_requests": [],
    }
    update = sources.D07_CORRELATE_AND_ADMIT_SOURCES(state, _Context())
    assert update["pending_failure"]["cause"] == "join"


def test_d08_rejects_a_candidate_whose_parent_is_not_the_current_head(tmp_path: Path) -> None:
    state = {
        "selected_unit_id": "U001",
        "effective_run": {"unit_records": [{"id": "U001"}]},
        "artifact_versions": [
            {
                "stream": "units/U001/domain",
                "version": 2,
                "parent_hash": "superseded" * 6,
                "hash": "child" * 12,
                "body": {},
                "schema_path": "schemas/x.json",
            }
        ],
        "artifact_heads": {
            "units/U001/domain": {"version": 1, "parent_hash": None, "hash": "current" * 8}
        },
        "source_admissions": [],
        "engine_root": str(tmp_path),
    }
    update = domain.D08_VALIDATE_DOMAIN(state, _Context())
    assert update["pending_failure"]["cause"] == "integrity"
    assert "artifact_heads" not in update


def test_d09_rejects_content_derived_from_a_superseded_domain(tmp_path: Path) -> None:
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    (schema_dir / "content.json").write_text(json.dumps({"type": "object"}), encoding="utf-8")

    state = {
        "selected_unit_id": "U001",
        "effective_run": {"unit_records": [{"id": "U001"}]},
        "artifact_versions": [
            {
                "stream": "units/U001/content",
                "version": 1,
                "parent_hash": None,
                "hash": "c" * 64,
                "body": {},
                "schema_path": "schemas/content.json",
                "domain_hash": "superseded" * 6,
            }
        ],
        "artifact_heads": {
            "units/U001/domain": {"version": 2, "parent_hash": "old" * 20, "hash": "current" * 8}
        },
        "engine_root": str(tmp_path),
    }
    update = content.D09_VALIDATE_CONTENT(state, _Context())
    assert update["pending_failure"]["cause"] == "integrity"
    assert "artifact_heads" not in update


def test_d12_rejects_a_denominator_compiled_against_a_superseded_content_head() -> None:
    state = {
        "selected_unit_id": "U001",
        "visual_denominators": {
            "k": {
                "unit_id": "U001",
                "content_hash": "superseded" * 6,
                "deterministic_keys": [],
                "model_keys": [],
                "size": 0,
            }
        },
        "visual_briefs": [],
        "visual_results": {},
        "artifact_versions": [],
        "artifact_heads": {"units/U001/content": {"version": 1, "parent_hash": None, "hash": "cur" * 21}},
    }
    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(state, _Context())
    assert update["pending_failure"]["cause"] == "integrity"


def test_d12_rejects_a_deterministic_visual_produced_against_a_stale_content_head() -> None:
    head = "cur" * 21
    state = {
        "selected_unit_id": "U001",
        "visual_denominators": {
            "k": {
                "unit_id": "U001",
                "content_hash": head,
                "deterministic_keys": ["v1"],
                "model_keys": [],
                "size": 1,
            }
        },
        "visual_briefs": [],
        "visual_results": {
            "v1": {
                "key": "v1",
                "unit_id": "U001",
                "subset": "deterministic",
                "content_hash": "stale" * 12,
                "sha256": "a" * 64,
                "format": "svg",
                "provenance": "deterministic_renderer",
            }
        },
        "artifact_versions": [],
        "artifact_heads": {"units/U001/content": {"version": 1, "parent_hash": None, "hash": head}},
    }
    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(state, _Context())
    assert update["pending_failure"]["cause"] == "integrity"
    assert "artifact_heads" not in update


def test_d12_rejects_a_missing_deterministic_denominator_member() -> None:
    head = "cur" * 21
    state = {
        "selected_unit_id": "U001",
        "visual_denominators": {
            "k": {
                "unit_id": "U001",
                "content_hash": head,
                "deterministic_keys": ["v1", "v2"],
                "model_keys": [],
                "size": 2,
            }
        },
        "visual_briefs": [],
        "visual_results": {
            "v1": {
                "key": "v1",
                "unit_id": "U001",
                "subset": "deterministic",
                "content_hash": head,
                "sha256": "a" * 64,
                "format": "svg",
                "provenance": "deterministic_renderer",
            }
        },
        "artifact_versions": [],
        "artifact_heads": {"units/U001/content": {"version": 1, "parent_hash": None, "hash": head}},
    }
    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(state, _Context())
    assert update["pending_failure"]["cause"] == "join"
    assert update["pending_failure"]["evidence"]["missing"] == ["v2"]


def test_d14_rejects_a_pdf_whose_bytes_changed_after_rendering(tmp_path: Path) -> None:
    pdf = tmp_path / "unit.pdf"
    pdf.write_bytes(b"%PDF-1.7 original")
    frozen_hash = hashlib.sha256(pdf.read_bytes()).hexdigest()
    pdf.write_bytes(b"%PDF-1.7 tampered")

    state = {
        "selected_unit_id": "U001",
        "artifact_heads": {},
        "artifact_versions": [
            {
                "stream": "units/U001/layout",
                "version": 1,
                "parent_hash": None,
                "hash": "h" * 64,
                "pdf_path": str(pdf),
                "pdf_sha256": frozen_hash,
            }
        ],
        "output_root": str(tmp_path),
    }
    update = render.D14_INVENTORY_AND_INSPECT_UNIT_PAGES(state, _Context())
    assert update["pending_failure"]["cause"] == "integrity"
    assert "unit_page_inventories" not in update


def test_d14_reports_a_noncontiguous_inventory_as_a_layout_finding(tmp_path: Path) -> None:
    pdf = tmp_path / "unit.pdf"
    pdf.write_bytes(b"%PDF-1.7 ok")
    pdf_hash = hashlib.sha256(pdf.read_bytes()).hexdigest()

    registry = _Registry(
        inspect_pages=lambda path, digest: {"pages": [_inspected_page(1), _inspected_page(3)]}
    )
    state = {
        "selected_unit_id": "U001",
        "artifact_heads": {},
        "artifact_versions": [
            {
                "stream": "units/U001/layout",
                "version": 1,
                "parent_hash": None,
                "hash": "h" * 64,
                "pdf_path": str(pdf),
                "pdf_sha256": pdf_hash,
            }
        ],
        "output_root": str(tmp_path),
    }
    update = render.D14_INVENTORY_AND_INSPECT_UNIT_PAGES(state, _Context(transport_registry=registry))
    assert update["unit_page_inventories"][0]["result"] == "FAIL"
    assert update["pending_guard"]["value"] == "layout_repairable"


def test_d13_rejects_a_renderer_that_misreports_its_own_pdf_hash(tmp_path: Path) -> None:
    pdf = tmp_path / "unit.pdf"
    pdf.write_bytes(b"%PDF-1.7 real")
    registry = _Registry(
        render_unit=lambda unit_id, parents: {
            "layout_path": str(tmp_path / "unit.typ"),
            "layout_sha256": "l" * 64,
            "pdf_path": str(pdf),
            "pdf_sha256": "f" * 64,
            "renderer": "stub",
        }
    )
    state = {
        "selected_unit_id": "U001",
        "artifact_heads": {
            f"units/U001/{channel}": {"version": 1, "parent_hash": None, "hash": f"{channel}-h"}
            for channel in ("domain", "content", "visuals")
        },
        "engine_root": str(tmp_path),
        "output_root": str(tmp_path),
    }
    update = render.D13_RENDER_UNIT(state, _Context(transport_registry=registry))
    assert update["pending_failure"]["cause"] == "integrity"
    assert "artifact_versions" not in update


def _layout_version(pdf_path: Path, pdf_sha256: str, unit_id: str = "U001") -> dict[str, Any]:
    """One appended layout version of the shape D13 writes.

    B-11: layout has no admitted head — D13 is append-unique — so D15 resolves the
    layout it names from the appended version, and every D15 fixture supplies one.
    """

    return {
        "stream": f"units/{unit_id}/layout",
        "version": 1,
        "parent_hash": None,
        "hash": "layout-h",
        "layout_path": str(pdf_path.with_suffix(".typ")),
        "layout_sha256": "l" * 64,
        "pdf_path": str(pdf_path),
        "pdf_sha256": pdf_sha256,
        "renderer": "stub",
    }


def test_d15_rejects_a_packet_whose_page_set_is_not_the_full_inventory(tmp_path: Path) -> None:
    state = {
        "selected_unit_id": "U001",
        "artifact_heads": {
            f"units/U001/{channel}": {"version": 1, "parent_hash": None, "hash": f"{channel}-h"}
            for channel in ("domain", "content", "visuals")
        },
        "unit_page_inventories": [
            {"unit_id": "U001", "pdf_sha256": "p" * 64, "page_count": 3, "result": "PASS"}
        ],
        "unit_page_inspections": [
            {"key": "k1", "unit_id": "U001", "pdf_sha256": "p" * 64, "page": 1, "result": "PASS"},
            {"key": "k3", "unit_id": "U001", "pdf_sha256": "p" * 64, "page": 3, "result": "PASS"},
        ],
        "deterministic_checks": [],
        "source_admissions": [],
        "engine_root": str(tmp_path),
        "artifact_versions": [_layout_version(tmp_path / "unit.pdf", "p" * 64)],
    }
    update = review.D15_FREEZE_UNIT_REVIEW_PACKET(state, _Context())
    assert update["pending_failure"]["cause"] == "join"
    assert "review_packets" not in update


def test_d15_refuses_a_packet_with_no_resolvable_layout(tmp_path: Path) -> None:
    """B-11: the layout is required, and required from D13's version, not a head.

    The packet names the bytes the reviewer answers about, so a state with no
    rendered layout is refused — but the refusal is about the render, not about an
    admitted head no node in the graph is authorized to write.
    """

    state = {
        "selected_unit_id": "U001",
        "artifact_heads": {
            f"units/U001/{channel}": {"version": 1, "parent_hash": None, "hash": f"{channel}-h"}
            for channel in ("domain", "content", "visuals", "layout")
        },
        "unit_page_inventories": [
            {"unit_id": "U001", "pdf_sha256": "p" * 64, "page_count": 1, "result": "PASS"}
        ],
        "unit_page_inspections": [],
        "deterministic_checks": [],
        "source_admissions": [],
        "engine_root": str(tmp_path),
        "artifact_versions": [],
    }
    update = review.D15_FREEZE_UNIT_REVIEW_PACKET(state, _Context())
    assert update["pending_failure"]["cause"] == "invalid_input"
    assert "rendered layout version" in update["pending_failure"]["message"]


def test_d92_rejects_a_frontier_whose_parents_are_no_longer_current() -> None:
    state = {
        "resume_frontier": {
            "destination": "D13_RENDER_UNIT",
            "parent_hashes": {"units/U001/content": "stale" * 12},
        },
        "artifact_heads": {"units/U001/content": {"version": 2, "parent_hash": "x", "hash": "fresh" * 12}},
        "attempt_counters": {},
        "model_execution_receipts": [],
        "activation_receipts": [],
        "capability_receipts": [{"key": "c"}],
        "external_authorizations": [{"providers": ["openai"]}],
    }
    update = inputs.D92_REENTER_VALIDATED_FRONTIER(state, _Context())
    assert update["pending_failure"]["cause"] == "integrity"


def test_d92_rejects_a_model_node_as_a_resume_destination() -> None:
    state = {
        "resume_frontier": {"destination": "M03_WRITE_UNIT_CONTENT", "parent_hashes": {}},
        "artifact_heads": {},
        "attempt_counters": {},
        "model_execution_receipts": [],
        "activation_receipts": [],
        "capability_receipts": [{"key": "c"}],
        "external_authorizations": [{"providers": ["openai"]}],
    }
    update = inputs.D92_REENTER_VALIDATED_FRONTIER(state, _Context())
    assert update["pending_failure"]["cause"] == "invalid_input"
    assert "model node" in update["pending_failure"]["message"]


def test_d92_routes_an_unaccounted_activation_to_failure_classification() -> None:
    state = {
        "resume_frontier": {"destination": "D13_RENDER_UNIT", "parent_hashes": {}},
        "artifact_heads": {},
        "attempt_counters": {},
        "model_execution_receipts": [],
        "activation_receipts": [{"activation_id": "act-1"}],
        "capability_receipts": [{"key": "c"}],
        "external_authorizations": [{"providers": ["openai"]}],
    }
    update = inputs.D92_REENTER_VALIDATED_FRONTIER(state, _Context())
    assert update["pending_guard"]["value"] == "incomplete_model_activation"
    assert update["pending_guard"]["detail"]["activations"] == ["act-1"]


# ---------------------------------------------------------------------------
# TEST 6 — one-owner scoping (prompt/ownership reconciliation)
# ---------------------------------------------------------------------------


def test_repair_and_acceptance_nodes_are_not_in_the_n22_catalogue() -> None:
    """`node_ownership.v1.md` assigns D16-D29, D31, D32 to N31/N32, not N22.

    The N22 prompt's TEST item 6 assumes repair-plan ownership. The frozen
    ownership contract is the binding resolution, so this asserts the boundary
    rather than implementing another node's work.
    """

    foreign = {
        "D16_REDUCE_UNIT_EVIDENCE",
        "D17_CLASSIFY_UNIT_FINDINGS",
        "D18_PLAN_TARGETED_UNIT_REPAIR",
        "D19_ROUTE_UNIT_REPAIR",
        "D20_ADMIT_UNIT_REPAIR",
        "D21_RETEST_REQUIRED_DESCENDANTS",
        "D22_ACCEPT_UNIT",
        "D23_CHECKPOINT_ACCEPTED_UNIT",
        "D24_PROVE_EXACT_MANIFEST_COVERAGE",
        "D25_ASSEMBLE_WORKBOOK",
        "D28_REDUCE_WORKBOOK_EVIDENCE",
        "D32_RECOMPUTE_FINAL_RELEASE",
    }
    assert foreign & set(NODE_CATALOGUE) == set()

    source = "".join(Path(module.__file__).read_text(encoding="utf-8") for module in NODE_MODULES)
    for node_id in foreign:
        assert f"def {node_id}" not in source


def test_d30_prerequisite_classification_is_one_owner_scoped() -> None:
    """D30 owns prerequisite classification alone, and only for a pause cause."""

    owners = [node_id for node_id, spec in NODE_CATALOGUE.items() if "prerequisite" in " ".join(spec.guards)]
    assert owners == ["D30_CLASSIFY_PREREQUISITE"] or set(owners) == {
        "D03_PROVE_CAPABILITIES",
        "D07_CORRELATE_AND_ADMIT_SOURCES",
        "D30_CLASSIFY_PREREQUISITE",
    }
    # Only D30 may produce the pause terminal candidate.
    candidate_writers = sorted(
        node_id
        for node_id, spec in NODE_CATALOGUE.items()
        if "terminal_candidate" in spec.outputs
    )
    assert candidate_writers == ["D30_CLASSIFY_PREREQUISITE", "D96_GRACEFUL_INTERRUPT_GATE"]


def test_d30_refuses_to_pause_on_a_non_pause_failure() -> None:
    state = {
        "selected_unit_id": "U001",
        "pending_failure": {"class": "system", "cause": "tool", "node": "D06B", "evidence": {}},
        "source_requests": [],
        "source_denominators": {"k": {"unit_id": "U001", "source_epoch": 1, "request_keys": ["r"]}},
        "retrievals": {},
        "attempt_counters": {},
    }
    update = sources.D30_CLASSIFY_PREREQUISITE(state, _Context())
    assert update["pending_failure"]["class"] == "system"
    # N40V7-F12-style regression (deterministic_node's own ExpectedFailure catch,
    # nodes/__init__.py): a terminal_candidate is now built alongside pending_failure,
    # so D98 never again rejects this as a bare, uninformative "not a JSON object".
    candidate = update["terminal_candidate"]
    assert candidate["kind"] == "SYSTEM_FAILURE"
    assert candidate["node"] == "D30_CLASSIFY_PREREQUISITE"
    assert candidate["failure"]["class"] == "system"


def test_d30_refuses_to_pause_on_more_than_one_unresolved_fact() -> None:
    state = {
        "selected_unit_id": "U001",
        "pending_failure": None,
        "source_requests": [],
        "source_denominators": {
            "k": {"unit_id": "U001", "source_epoch": 1, "request_keys": ["r1", "r2"]}
        },
        "retrievals": {},
        "attempt_counters": {},
    }
    update = sources.D30_CLASSIFY_PREREQUISITE(state, _Context())
    assert update["pending_failure"]["cause"] == "invalid_input"
    assert "exactly one" in update["pending_failure"]["message"]


def test_d30_emits_a_pause_candidate_for_one_named_fact() -> None:
    state = {
        "selected_unit_id": "U001",
        "pending_failure": {
            "class": "pause",
            "cause": "required_external_fact_unavailable",
            "node": "D06B_RETRIEVE_SOURCE_CANDIDATES",
            "evidence": {"facts": [{"request_key": "U001/1/f", "reason": "no locator"}]},
        },
        "source_requests": [],
        "source_denominators": {"k": {"unit_id": "U001", "source_epoch": 1, "request_keys": ["U001/1/f"]}},
        "retrievals": {},
        "attempt_counters": {"retrieval:U001/1/f": 2},
    }
    update = sources.D30_CLASSIFY_PREREQUISITE(state, _Context())
    candidate = update["terminal_candidate"]
    assert candidate["kind"] == "PAUSED_PREREQUISITE"
    assert candidate["fact"] == "U001/1/f"
    assert candidate["attempts"] == 2
    assert update["resume_frontier"]["destination"] == "D06B_RETRIEVE_SOURCE_CANDIDATES"


# ---------------------------------------------------------------------------
# TEST 7 — D98 independently rejects invalid candidates
# ---------------------------------------------------------------------------


def _terminal_state(**overrides: Any) -> dict[str, Any]:
    state: dict[str, Any] = {
        "terminal_candidate": None,
        "terminal": None,
        "terminal_history": [],
        "episode_id": "ep-1",
        "run_id": "run-1",
        "mode": "one",
        "requested_unit_id": "U002",
        "effective_run": {"ordered_unit_ids": ["U001", "U002"], "target_closure": ["U001", "U002"]},
        "accepted_unit_receipts": {},
        "final_release_audits": [],
        "workbook_head": {},
        "artifact_heads": {},
        "attempt_counters": {},
        "failure_fingerprints": [],
        "checkpoint_metadata": [{"checkpoint_id": "ckpt-9"}],
        "evidence_index_entries": [{"key": "e1"}, {"key": "e2"}],
        "pending_failure": None,
        "resume_frontier": None,
        "output_root": "/tmp/out",
    }
    state.update(overrides)
    return state


def _accepted(unit_id: str, digest: str) -> dict[str, Any]:
    return {"unit_id": unit_id, "receipt_hash": digest}


def _valid_unit_accepted_state() -> tuple[dict[str, Any], dict[str, Any]]:
    receipts = {"U001": _accepted("U001", "h1" * 32), "U002": _accepted("U002", "h2" * 32)}
    candidate = {
        "kind": "UNIT_ACCEPTED",
        "unit_id": "U002",
        "receipt_hash": "h2" * 32,
        "closure_receipt_hashes": {"U001": "h1" * 32, "U002": "h2" * 32},
        "denominator": {"entries": 14},
        "log_high_water_mark": 2,
        "checkpoint_id": "ckpt-9",
    }
    return candidate, _terminal_state(accepted_unit_receipts=receipts, terminal_candidate=candidate)


def _valid_complete_state() -> tuple[dict[str, Any], dict[str, Any]]:
    receipts = {"U001": _accepted("U001", "h1" * 32), "U002": _accepted("U002", "h2" * 32)}
    audit = {"key": "audit-1", "result": "PASS", "workbook_hash": "wb" * 32}
    candidate = {
        "kind": "COMPLETE",
        "release_audit_key": "audit-1",
        "workbook_hash": "wb" * 32,
        "coverage": {"units": 2},
        "unit_receipt_hashes": {"U001": "h1" * 32, "U002": "h2" * 32},
        "log_high_water_mark": 2,
        "checkpoint_id": "ckpt-9",
    }
    state = _terminal_state(
        mode="all",
        requested_unit_id=None,
        accepted_unit_receipts=receipts,
        final_release_audits=[audit],
        workbook_head={"workbook": {"version": 1, "parent_hash": None, "hash": "wb" * 32}},
        terminal_candidate=candidate,
    )
    return candidate, state


def test_d98_accepts_a_fully_supported_unit_accepted_candidate() -> None:
    candidate, state = _valid_unit_accepted_state()
    validation = terminal.validate_terminal_candidate(candidate, project("D98_WRITE_TERMINAL", state))
    assert validation.accepted, validation.rejections

    update = terminal.D98_WRITE_TERMINAL(state, _Context())
    assert update["terminal"]["kind"] == "UNIT_ACCEPTED"
    assert update["terminal"]["exit_code"] == 0
    assert update["terminal"]["resumable"] is False
    assert update["terminal_history"] == [update["terminal"]]


def test_d98_accepts_a_fully_supported_complete_candidate() -> None:
    candidate, state = _valid_complete_state()
    update = terminal.D98_WRITE_TERMINAL(state, _Context())
    assert update["terminal"]["kind"] == "COMPLETE"
    assert update["terminal"]["exit_code"] == 0


@pytest.mark.parametrize(
    "mutate,expected_fragment",
    [
        (lambda c, s: s.update(mode="all"), "requires mode 'one'"),
        (lambda c, s: c.update(unit_id="U001"), "but the run requested"),
        (lambda c, s: s["accepted_unit_receipts"].pop("U001"), "entire closure"),
        (lambda c, s: c.update(receipt_hash="forged" * 8), "current accepted receipt hash"),
        (lambda c, s: c["closure_receipt_hashes"].update({"U001": "stale" * 8}), "is stale"),
        (lambda c, s: c.update(checkpoint_id="ckpt-old"), "not the current checkpoint"),
        (lambda c, s: s.update(checkpoint_metadata=[]), "checkpoint correlation metadata"),
        (lambda c, s: c.update(log_high_water_mark=99), "above the 2 recorded"),
        (lambda c, s: c.pop("denominator"), "missing required field 'denominator'"),
    ],
)
def test_d98_rejects_an_unsupported_unit_accepted_candidate(mutate: Any, expected_fragment: str) -> None:
    candidate, state = _valid_unit_accepted_state()
    mutate(candidate, state)
    state["terminal_candidate"] = candidate

    validation = terminal.validate_terminal_candidate(candidate, project("D98_WRITE_TERMINAL", state))
    assert not validation.accepted
    assert any(expected_fragment in reason for reason in validation.rejections), validation.rejections

    update = terminal.D98_WRITE_TERMINAL(state, _Context())
    assert update["terminal"]["kind"] == "SYSTEM_FAILURE"
    assert update["terminal"]["evidence"]["rejected_candidate_kind"] == "UNIT_ACCEPTED"


@pytest.mark.parametrize(
    "mutate,expected_fragment",
    [
        (lambda c, s: s.update(mode="one"), "requires mode 'all'"),
        (lambda c, s: s.update(final_release_audits=[]), "requires a final release audit"),
        (
            lambda c, s: s["final_release_audits"].__setitem__(0, {"key": "audit-1", "result": "FAIL"}),
            "release audit to pass",
        ),
        (lambda c, s: c.update(release_audit_key="other"), "not the current one"),
        (lambda c, s: c.update(workbook_hash="forged" * 8), "current workbook head hash"),
        (lambda c, s: s.update(workbook_head={}), "current workbook head"),
        (lambda c, s: s["accepted_unit_receipts"].pop("U001"), "exact manifest coverage"),
        (lambda c, s: c["unit_receipt_hashes"].update({"U002": "stale" * 8}), "is stale"),
    ],
)
def test_d98_rejects_an_unsupported_complete_candidate(mutate: Any, expected_fragment: str) -> None:
    candidate, state = _valid_complete_state()
    mutate(candidate, state)
    state["terminal_candidate"] = candidate

    validation = terminal.validate_terminal_candidate(candidate, project("D98_WRITE_TERMINAL", state))
    assert not validation.accepted
    assert any(expected_fragment in reason for reason in validation.rejections), validation.rejections
    assert terminal.D98_WRITE_TERMINAL(state, _Context())["terminal"]["kind"] == "SYSTEM_FAILURE"


def test_d98_rejects_a_complete_candidate_with_an_extra_accepted_unit() -> None:
    candidate, state = _valid_complete_state()
    state["accepted_unit_receipts"]["U999"] = _accepted("U999", "h9" * 32)
    validation = terminal.validate_terminal_candidate(candidate, project("D98_WRITE_TERMINAL", state))
    assert not validation.accepted
    assert any("exact manifest coverage" in reason for reason in validation.rejections)


def test_d98_accepts_a_supported_interrupt_candidate_and_rejects_a_bare_one() -> None:
    heads = {"units/U001/content": {"version": 1, "parent_hash": None, "hash": "c" * 64}}
    valid = {
        "kind": "INTERRUPTED",
        "classification": "graceful_signal",
        "resume_frontier": {"destination": "D13_RENDER_UNIT"},
        "heads": {"units/U001/content": "c" * 64},
        "high_water_marks": {"evidence_records": 2},
    }
    state = _terminal_state(artifact_heads=heads, terminal_candidate=valid)
    assert terminal.validate_terminal_candidate(valid, project("D98_WRITE_TERMINAL", state)).accepted
    update = terminal.D98_WRITE_TERMINAL(state, _Context())
    assert update["terminal"]["kind"] == "INTERRUPTED"
    assert update["terminal"]["exit_code"] == 10
    assert update["terminal"]["resumable"] is True

    invalid = dict(valid, classification="wishful", heads={"units/U001/content": "stale" * 12})
    rejections = terminal.validate_terminal_candidate(
        invalid, project("D98_WRITE_TERMINAL", state)
    ).rejections
    assert any("classification" in reason for reason in rejections)
    assert any("stale heads" in reason for reason in rejections)


def test_d98_accepts_a_supported_pause_candidate_and_rejects_a_disguised_tool_fault() -> None:
    valid = {
        "kind": "PAUSED_PREREQUISITE",
        "fact": "U001/1/required_explanation:000",
        "attempts": 3,
        "required_resume_condition": "the named fact becomes retrievable",
        "resume_frontier": {"destination": "D06B_RETRIEVE_SOURCE_CANDIDATES"},
    }
    state = _terminal_state(terminal_candidate=valid)
    assert terminal.validate_terminal_candidate(valid, project("D98_WRITE_TERMINAL", state)).accepted
    assert terminal.D98_WRITE_TERMINAL(state, _Context())["terminal"]["exit_code"] == 11

    disguised = _terminal_state(
        terminal_candidate=valid,
        pending_failure={"class": "system", "cause": "tool", "node": "D13_RENDER_UNIT"},
    )
    validation = terminal.validate_terminal_candidate(valid, project("D98_WRITE_TERMINAL", disguised))
    assert not validation.accepted
    assert any("cannot carry a 'system' failure" in reason for reason in validation.rejections)
    assert terminal.D98_WRITE_TERMINAL(disguised, _Context())["terminal"]["kind"] == "SYSTEM_FAILURE"


def test_d98_rejects_an_exhaustion_candidate_with_no_recorded_attempts() -> None:
    candidate = {
        "kind": "CONVERGENCE_EXHAUSTED",
        "bound": "fingerprint_bound",
        "counters": {},
        "fingerprints": [],
        "last_findings": [],
    }
    bare = _terminal_state(terminal_candidate=candidate)
    validation = terminal.validate_terminal_candidate(candidate, project("D98_WRITE_TERMINAL", bare))
    assert not validation.accepted
    assert any("recorded attempt counters" in reason for reason in validation.rejections)

    supported = _terminal_state(
        terminal_candidate=candidate,
        attempt_counters={"repair:U001:content": 3},
        failure_fingerprints=[{"key": "fp-1"}],
    )
    assert terminal.validate_terminal_candidate(candidate, project("D98_WRITE_TERMINAL", supported)).accepted
    assert terminal.D98_WRITE_TERMINAL(supported, _Context())["terminal"]["exit_code"] == 12


def test_d98_rejects_exhaustion_once_the_full_denominator_passed() -> None:
    candidate = {
        "kind": "CONVERGENCE_EXHAUSTED",
        "bound": "attempt_bound",
        "counters": {"a": 3},
        "fingerprints": [{"key": "fp"}],
        "last_findings": [],
    }
    state = _terminal_state(
        terminal_candidate=candidate,
        attempt_counters={"a": 3},
        accepted_unit_receipts={
            "U001": _accepted("U001", "h1" * 32),
            "U002": _accepted("U002", "h2" * 32),
        },
    )
    validation = terminal.validate_terminal_candidate(candidate, project("D98_WRITE_TERMINAL", state))
    assert not validation.accepted
    assert any("acceptance denominator passed" in reason for reason in validation.rejections)


def test_d98_accepts_a_typed_system_failure_and_rejects_an_untyped_one() -> None:
    valid = {
        "kind": "SYSTEM_FAILURE",
        "failure": {"class": "system", "cause": "tool", "message": "renderer exited 1"},
        "node": "D13_RENDER_UNIT",
        "safe_heads": {},
        "audit_high_water_mark": 2,
    }
    state = _terminal_state(terminal_candidate=valid)
    assert terminal.validate_terminal_candidate(valid, project("D98_WRITE_TERMINAL", state)).accepted
    assert terminal.D98_WRITE_TERMINAL(state, _Context())["terminal"]["exit_code"] == 20

    untyped = dict(valid, failure={"message": "something broke"})
    rejections = terminal.validate_terminal_candidate(
        untyped, project("D98_WRITE_TERMINAL", state)
    ).rejections
    assert any("failure class" in reason for reason in rejections)


@pytest.mark.parametrize("candidate", [None, "COMPLETE", 42, [], {"kind": "ACCEPTED_PENDING_REVIEW"}, {}])
def test_d98_rejects_a_malformed_or_unknown_candidate(candidate: Any) -> None:
    state = _terminal_state(terminal_candidate=candidate)
    validation = terminal.validate_terminal_candidate(candidate, project("D98_WRITE_TERMINAL", state))
    assert not validation.accepted
    update = terminal.D98_WRITE_TERMINAL(state, _Context())
    assert update["terminal"]["kind"] == "SYSTEM_FAILURE"


def test_d98_terminal_guard_table_matches_spec_section_14() -> None:
    expected = {
        "UNIT_ACCEPTED": (0, False, True),
        "COMPLETE": (0, False, True),
        "INTERRUPTED": (10, True, False),
        "PAUSED_PREREQUISITE": (11, True, False),
        "CONVERGENCE_EXHAUSTED": (12, False, False),
        "SYSTEM_FAILURE": (20, False, False),
    }
    assert sorted(terminal.TERMINAL_GUARDS) == sorted(expected)
    for kind, (exit_code, resumable, success) in expected.items():
        row = terminal.TERMINAL_GUARDS[kind]
        assert (row.exit_code, row.resumable, row.claims_product_success) == (
            exit_code,
            resumable,
            success,
        ), kind


# ---------------------------------------------------------------------------
# TEST 8 — one terminal write; no node body declares graph edges
# ---------------------------------------------------------------------------


def test_a_second_terminal_write_is_refused() -> None:
    candidate, state = _valid_unit_accepted_state()
    first = terminal.D98_WRITE_TERMINAL(state, _Context())
    state["terminal"] = first["terminal"]

    second = terminal.D98_WRITE_TERMINAL(state, _Context())
    assert "terminal" not in second
    assert second["pending_failure"]["cause"] == "persistence"


def test_the_write_once_reducer_refuses_a_differing_second_terminal() -> None:
    from runtime.langgraph_factory.reducers import TerminalConflict, write_episode_terminal_once

    candidate, state = _valid_unit_accepted_state()
    first = terminal.D98_WRITE_TERMINAL(state, _Context())["terminal"]

    assert write_episode_terminal_once(first, first) == first
    with pytest.raises(TerminalConflict):
        write_episode_terminal_once(first, dict(first, kind="COMPLETE"))


def test_no_node_body_declares_a_graph_edge_or_references_end() -> None:
    forbidden = ("add_edge", "add_node", "add_conditional_edges", "StateGraph", "Send")
    offenders: list[str] = []
    for module in NODE_MODULES:
        source = Path(module.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        for statement in ast.walk(tree):
            if isinstance(statement, ast.Attribute) and statement.attr in forbidden:
                offenders.append(f"{module.__name__}:{statement.lineno}:{statement.attr}")
            if isinstance(statement, ast.Name) and statement.id in (*forbidden, "END"):
                offenders.append(f"{module.__name__}:{statement.lineno}:{statement.id}")
            if isinstance(statement, (ast.Import, ast.ImportFrom)):
                names = [alias.name for alias in statement.names]
                module_name = getattr(statement, "module", "") or ""
                assert "langgraph" not in module_name, f"{module.__name__} imports langgraph"
                assert not any("langgraph" in name for name in names), module.__name__
    assert offenders == [], f"a node body declares graph topology: {offenders}"


def test_no_node_module_imports_a_forbidden_model_dependency() -> None:
    forbidden = ("langchain", "langchain_openai", "openai")
    for module in NODE_MODULES + (node_pkg,):
        tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
        for statement in ast.walk(tree):
            if isinstance(statement, ast.ImportFrom):
                assert not any(
                    (statement.module or "").startswith(name) for name in forbidden
                ), f"{module.__name__} imports {statement.module}"
            if isinstance(statement, ast.Import):
                for alias in statement.names:
                    assert not any(alias.name.startswith(name) for name in forbidden), alias.name


def test_the_interrupt_gate_reaches_no_transport_retrieval_or_renderer() -> None:
    """D96 runs while the episode is stopping; an external call here could lose the frontier."""

    body = ast.parse(Path(inputs.__file__).read_text(encoding="utf-8"))
    gate = next(
        node
        for node in body.body
        if isinstance(node, ast.FunctionDef) and node.name == "D96_GRACEFUL_INTERRUPT_GATE"
    )
    attributes = {
        node.attr for node in ast.walk(gate) if isinstance(node, ast.Attribute)
    }
    assert not attributes & {
        "transport_registry",
        "source_retriever",
        "render_unit",
        "inspect_pages",
        "fetch",
        "execute",
    }


def test_d96_produces_an_interrupt_candidate_and_a_resume_frontier() -> None:
    class _Set:
        def is_set(self) -> bool:
            return True

    state = {
        "invocation": {"kind": "fresh"},
        "validated_recovery_envelope": None,
        "resume_frontier": {"destination": "D13_RENDER_UNIT"},
        "artifact_heads": {"units/U001/content": {"version": 1, "parent_hash": None, "hash": "c" * 64}},
        "attempt_counters": {"a": 1},
        "checkpoint_metadata": [{"checkpoint_id": "ckpt-3"}],
        "evidence_index_entries": [{"key": "e"}],
        "selected_unit_id": "U001",
        "episode_id": "ep-1",
        "run_id": "run-1",
    }
    update = inputs.D96_GRACEFUL_INTERRUPT_GATE(state, _Context(signal_token=_Set()))
    assert update["terminal_candidate"]["kind"] == "INTERRUPTED"
    assert update["terminal_candidate"]["classification"] == "graceful_signal"
    assert update["resume_frontier"]["destination"] == "D13_RENDER_UNIT"
    assert update["terminal_candidate"]["high_water_marks"]["last_checkpoint_id"] == "ckpt-3"


def test_d96_refuses_to_interrupt_without_a_signal_or_recovery_envelope() -> None:
    state = {
        "invocation": {},
        "validated_recovery_envelope": None,
        "resume_frontier": None,
        "artifact_heads": {},
        "attempt_counters": {},
        "checkpoint_metadata": [],
        "evidence_index_entries": [],
        "selected_unit_id": None,
        "episode_id": "ep-1",
        "run_id": "run-1",
    }
    update = inputs.D96_GRACEFUL_INTERRUPT_GATE(state, _Context())
    assert update["pending_failure"]["cause"] == "invalid_input"


# ---------------------------------------------------------------------------
# TEST 9 — static scan for curriculum constants
# ---------------------------------------------------------------------------


N22_SOURCE_FILES = tuple(
    sorted(
        path
        for path in PACKAGE_ROOT.rglob("*.py")
        if "__pycache__" not in path.parts
    )
)


def test_the_owned_file_set_is_exactly_the_frozen_layout() -> None:
    names = sorted(path.name for path in N22_SOURCE_FILES)
    assert names == [
        "__init__.py",
        "content.py",
        "domain.py",
        "inputs.py",
        "render.py",
        "review.py",
        "sources.py",
        "terminal.py",
        "visuals.py",
    ]


@pytest.mark.parametrize("path", N22_SOURCE_FILES, ids=lambda path: path.name)
def test_no_curriculum_name_appears_in_production_source(path: Path) -> None:
    installed = sorted(
        directory.name
        for directory in CURRICULA_ROOT.iterdir()
        if directory.is_dir()
    )
    assert installed, "no curriculum is installed; the neutrality scan would be vacuous"
    source = path.read_text(encoding="utf-8").lower()
    for name in installed:
        assert name.lower() not in source, f"{path.name} names curriculum {name!r}"
        for token in name.split("_"):
            if len(token) > 3:
                assert token.lower() not in source, f"{path.name} names curriculum token {token!r}"


@pytest.mark.parametrize("path", N22_SOURCE_FILES, ids=lambda path: path.name)
def test_no_unit_id_literal_appears_in_production_source(path: Path) -> None:
    unit_id_pattern = re.compile(r"\b[LU]\d{2,3}\b")
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = unit_id_pattern.search(line)
        assert match is None, f"{path.name}:{lineno} contains unit id literal {match.group()!r}"


@pytest.mark.parametrize("path", N22_SOURCE_FILES, ids=lambda path: path.name)
def test_no_hardcoded_unit_count_appears_in_production_source(path: Path) -> None:
    """No integer literal in this package may stand in for a manifest's unit count."""

    installed_counts = set()
    for manifest in CURRICULA_ROOT.rglob("*curriculum.v*.yaml"):
        if "deprecated" in manifest.parts:
            continue
        raw = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        installed_counts.add(len(raw.get("labs", [])))
    assert installed_counts, "no installed manifest to derive a unit count from"

    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            assert node.value not in installed_counts, (
                f"{path.name}:{node.lineno} hardcodes {node.value}, "
                f"which is an installed manifest's unit count"
            )


def test_the_closure_algorithm_reads_unit_ids_only_from_the_manifest() -> None:
    """No node function may compare against a string that looks like a unit id."""

    tree = ast.parse(Path(inputs.__file__).read_text(encoding="utf-8"))
    pattern = re.compile(r"^[LU]\d{2,3}$")
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert not pattern.match(node.value), f"unit id constant {node.value!r} at line {node.lineno}"


# ---------------------------------------------------------------------------
# happy-path coverage for the remaining owned nodes
# ---------------------------------------------------------------------------


def test_d00_classifies_a_fresh_invocation() -> None:
    state = {
        "invocation": {
            "kind": "fresh",
            "contract_version": "v1",
            "engine_root": "/engine",
            "curriculum_root": "/engine/curricula/x",
            "output_root": "/out",
            "mode": "one",
            "requested_unit_id": "U002",
            "authorization": {"providers": ["openai"]},
            "episode_ordinal": 0,
            "prior_identity": None,
            "prior_terminal": None,
            "lease_open": False,
        },
        "run_id": None,
        "frozen_digest": None,
        "terminal": None,
        "terminal_history": [],
    }
    update = inputs.D00_BOOTSTRAP_EPISODE(state, _Context())
    assert update["bootstrap_kind"] == "fresh"
    assert update["pending_guard"]["value"] == "fresh"
    assert "prior_terminal" not in update["invocation"], "bootstrap-only evidence must not persist"
    assert "lease_open" not in update["invocation"]


def test_d00_refuses_a_fresh_invocation_over_an_existing_identity() -> None:
    state = {
        "invocation": {"kind": "fresh", "episode_ordinal": 0},
        "run_id": "existing",
        "frozen_digest": "d",
        "terminal": None,
        "terminal_history": [],
    }
    update = inputs.D00_BOOTSTRAP_EPISODE(state, _Context())
    assert update["pending_failure"]["cause"] == "identity"


def test_d00_refuses_to_resume_a_final_terminal() -> None:
    state = {
        "invocation": {
            "kind": "resume",
            "episode_ordinal": 1,
            "prior_identity": {"run_id": "r"},
            "prior_terminal": {"kind": "COMPLETE"},
        },
        "run_id": "r",
        "frozen_digest": "d",
        "terminal": None,
        "terminal_history": [],
    }
    update = inputs.D00_BOOTSTRAP_EPISODE(state, _Context())
    assert update["pending_failure"]["cause"] == "identity"
    assert "not legally resumable" in update["pending_failure"]["message"]


def test_d00_routes_an_open_lease_with_no_terminal_to_recovery() -> None:
    state = {
        "invocation": {
            "kind": "recover_orphan",
            "episode_ordinal": 2,
            "prior_identity": {"run_id": "r"},
            "prior_terminal": None,
            "lease_open": True,
        },
        "run_id": "r",
        "frozen_digest": "d",
        "terminal": None,
        "terminal_history": [],
    }
    update = inputs.D00_BOOTSTRAP_EPISODE(state, _Context())
    assert update["bootstrap_kind"] == "recover_orphan"
    assert update["pending_guard"]["value"] == "recover_orphan"


def test_d00_rejects_an_envelope_with_undeclared_fields() -> None:
    state = {
        "invocation": {"kind": "fresh", "episode_ordinal": 0, "backdoor": True},
        "run_id": None,
        "frozen_digest": None,
        "terminal": None,
        "terminal_history": [],
    }
    update = inputs.D00_BOOTSTRAP_EPISODE(state, _Context())
    assert update["pending_failure"]["cause"] == "schema_contract"


def test_d00r_rejects_a_frozen_input_whose_bytes_drifted(tmp_path: Path) -> None:
    frozen_file = tmp_path / "policy.yaml"
    frozen_file.write_text("a: 1", encoding="utf-8")
    frozen_inputs = [{"path": str(frozen_file), "sha256": _sha256_file(frozen_file), "role": "engine_policy"}]
    frozen_file.write_text("a: 2", encoding="utf-8")

    authorization = {"providers": ["openai"]}
    state = {
        "invocation": {
            "contract_version": "v1",
            "engine_root": "/engine",
            "curriculum_root": "/engine/curricula/x",
            "output_root": "/out",
            "mode": "one",
            "requested_unit_id": "U002",
            "authorization": [authorization],
        },
        "contract_version": "v1",
        "run_id": "r",
        "created_at": "t",
        "engine_root": "/engine",
        "curriculum_root": "/engine/curricula/x",
        "active_manifest_path": "/engine/curricula/x/m.v1.yaml",
        "output_root": "/out",
        "mode": "one",
        "requested_unit_id": "U002",
        "frozen_inputs": frozen_inputs,
        "frozen_digest": canonical_digest(frozen_inputs),
        "frozen_executable_identities": [],
        "external_authorizations": [authorization],
        "terminal_history": [{"kind": "INTERRUPTED"}],
    }
    update = inputs.D00R_REVALIDATE_RESUME_IDENTITY(state, _Context())
    assert update["pending_failure"]["cause"] == "identity"
    assert update["pending_failure"]["evidence"]["drifted_inputs"][0]["path"] == str(frozen_file)


def test_d00r_admits_an_identical_resume_identity(tmp_path: Path) -> None:
    frozen_file = tmp_path / "policy.yaml"
    frozen_file.write_text("a: 1", encoding="utf-8")
    frozen_inputs = [{"path": str(frozen_file), "sha256": _sha256_file(frozen_file), "role": "engine_policy"}]
    authorization = {"providers": ["openai"]}
    state = {
        "invocation": {
            "contract_version": "v1",
            "engine_root": "/engine",
            "curriculum_root": "/engine/curricula/x",
            "output_root": "/out",
            "mode": "all",
            "requested_unit_id": None,
            "authorization": [authorization],
        },
        "contract_version": "v1",
        "run_id": "r",
        "created_at": "t",
        "engine_root": "/engine",
        "curriculum_root": "/engine/curricula/x",
        "active_manifest_path": "/engine/curricula/x/m.v1.yaml",
        "output_root": "/out",
        "mode": "all",
        "requested_unit_id": None,
        "frozen_inputs": frozen_inputs,
        "frozen_digest": canonical_digest(frozen_inputs),
        "frozen_executable_identities": [],
        "external_authorizations": [authorization],
        "terminal_history": [{"kind": "PAUSED_PREREQUISITE"}],
    }
    update = inputs.D00R_REVALIDATE_RESUME_IDENTITY(state, _Context())
    assert update["validated_recovery_envelope"]["run_id"] == "r"
    assert update["evidence_index_entries"][0]["result"] == "PASS"


def test_d01_freezes_an_identity_over_a_real_engine_tree(tmp_path: Path) -> None:
    engine_root = tmp_path / "engine"
    (engine_root / "schemas").mkdir(parents=True)
    (engine_root / "schemas" / "unit.json").write_text("{}", encoding="utf-8")
    curriculum_root = engine_root / "curricula" / "synthetic"
    curriculum_root.mkdir(parents=True)
    (curriculum_root / "synthetic_curriculum.v2.yaml").write_text("labs: []", encoding="utf-8")
    (curriculum_root / "synthetic_curriculum.v1.yaml").write_text("labs: []", encoding="utf-8")
    output_root = tmp_path / "out"

    state = {
        "invocation": {
            "kind": "fresh",
            "contract_version": "plan26.v1",
            "engine_root": str(engine_root),
            "curriculum_root": str(curriculum_root),
            "output_root": str(output_root),
            "mode": "all",
            "requested_unit_id": None,
            "authorization": {"providers": ["openai"], "curriculum_digest": None},
            "episode_ordinal": 0,
        }
    }
    update = inputs.D01_VALIDATE_AND_FREEZE_INPUTS(state, _Context())
    assert update["active_manifest_path"].endswith("synthetic_curriculum.v2.yaml")
    assert update["frozen_digest"] == canonical_digest(update["frozen_inputs"])
    assert len(update["run_id"]) == 64
    assert update["mode"] == "all"
    assert update["requested_unit_id"] is None


def test_d01_refuses_a_run_with_no_authorization_record(tmp_path: Path) -> None:
    engine_root = tmp_path / "engine"
    curriculum_root = engine_root / "curricula" / "synthetic"
    curriculum_root.mkdir(parents=True)
    (curriculum_root / "synthetic_curriculum.v1.yaml").write_text("labs: []", encoding="utf-8")

    state = {
        "invocation": {
            "kind": "fresh",
            "contract_version": "plan26.v1",
            "engine_root": str(engine_root),
            "curriculum_root": str(curriculum_root),
            "output_root": str(tmp_path / "out"),
            "mode": "all",
            "requested_unit_id": None,
            "authorization": {},
            "episode_ordinal": 0,
        }
    }
    update = inputs.D01_VALIDATE_AND_FREEZE_INPUTS(state, _Context())
    assert update["pending_failure"]["cause"] == "authorization"


def test_d01_refuses_a_relative_traversal_root(tmp_path: Path) -> None:
    state = {
        "invocation": {
            "kind": "fresh",
            "contract_version": "v1",
            "engine_root": f"{tmp_path}/engine/../engine",
            "curriculum_root": str(tmp_path),
            "output_root": str(tmp_path / "out"),
            "mode": "all",
            "requested_unit_id": None,
            "authorization": {"providers": []},
            "episode_ordinal": 0,
        }
    }
    update = inputs.D01_VALIDATE_AND_FREEZE_INPUTS(state, _Context())
    assert update["pending_failure"]["cause"] == "invalid_input"


def _driver_capability_fields(*, status: str = "PASS") -> dict[str, Any]:
    return {name: {"status": status} for name in inputs.DRIVER_CAPABILITY_FIELDS}


def _driver_capability_proof(**driver_overrides: Any) -> dict[str, Any]:
    """A ready `driver_capability_proof` fixture, overridable per driver.

    `driver_overrides["claude"] = {"ready": False, "failed_fields": [...], ...}`
    replaces that one driver's entry wholesale; every other mandatory driver stays
    a passing, fully-differentiated (no single flag) fixture.
    """

    drivers: dict[str, Any] = {
        cli: {
            "cli": cli,
            "model": "claude-sonnet-5" if cli == "claude" else "gpt-5.6-sol",
            "provider": "anthropic" if cli == "claude" else "openai",
            "ready": True,
            "failed_fields": [],
            "fields": _driver_capability_fields(),
        }
        for cli in inputs.MANDATORY_DRIVER_CLIS
    }
    for cli, patch in driver_overrides.items():
        drivers[cli] = patch
    return {"ready": all(detail["ready"] for detail in drivers.values()), "drivers": drivers}


def test_d03_proves_capabilities_and_records_one_receipt_each() -> None:
    registry = _Registry(
        prove_capability=lambda name: {"result": "PASS", "capability": name},
        observe_executable=lambda name: {"path": f"/usr/bin/{name}", "sha256": "e" * 64},
        driver_capability_proof=_driver_capability_proof(),
    )
    authorization = {"providers": ["openai"], "curriculum_digest": "fd", "output_root": "/out"}
    state = {
        "invocation": {"kind": "fresh"},
        "validated_recovery_envelope": None,
        "effective_run": {"ordered_unit_ids": ["U001"]},
        "frozen_executable_identities": [{"name": "codex", "path": "/usr/bin/codex", "sha256": "e" * 64}],
        "external_authorizations": [authorization],
        "frozen_digest": "fd",
        "run_id": "r",
        "engine_root": "/engine",
        "output_root": "/out",
    }
    update = inputs.D03_PROVE_CAPABILITIES(state, _Context(transport_registry=registry))
    kinds = [receipt["capability"] for receipt in update["capability_receipts"]]
    assert set(inputs.REQUIRED_CAPABILITIES) <= set(kinds)
    driver_receipts = [r for r in update["capability_receipts"] if r["capability"] == "driver_capability_proof"]
    assert len(driver_receipts) == 1
    assert driver_receipts[0]["proof"]["ready"] is True
    assert update["pending_guard"]["value"] == "capabilities_proven"


def test_d03_refuses_an_authorization_scoped_to_another_run() -> None:
    registry = _Registry(
        prove_capability=lambda name: {"result": "PASS"},
        driver_capability_proof=_driver_capability_proof(),
    )
    state = {
        "invocation": {"kind": "fresh"},
        "validated_recovery_envelope": None,
        "effective_run": {"ordered_unit_ids": ["U001"]},
        "frozen_executable_identities": [],
        "external_authorizations": [{"providers": ["openai"], "curriculum_digest": "other"}],
        "frozen_digest": "fd",
        "run_id": "r",
        "engine_root": "/engine",
        "output_root": "/out",
    }
    update = inputs.D03_PROVE_CAPABILITIES(state, _Context(transport_registry=registry))
    assert update["pending_failure"]["cause"] == "authorization"


def test_d03_refuses_an_executable_whose_identity_drifted() -> None:
    registry = _Registry(
        prove_capability=lambda name: {"result": "PASS"},
        observe_executable=lambda name: {"path": "/usr/bin/codex", "sha256": "different" * 7},
        driver_capability_proof=_driver_capability_proof(),
    )
    state = {
        "invocation": {"kind": "fresh"},
        "validated_recovery_envelope": None,
        "effective_run": {"ordered_unit_ids": ["U001"]},
        "frozen_executable_identities": [{"name": "codex", "path": "/usr/bin/codex", "sha256": "e" * 64}],
        "external_authorizations": [{"providers": [], "curriculum_digest": "fd"}],
        "frozen_digest": "fd",
        "run_id": "r",
        "engine_root": "/engine",
        "output_root": "/out",
    }
    update = inputs.D03_PROVE_CAPABILITIES(state, _Context(transport_registry=registry))
    assert update["pending_failure"]["cause"] == "identity"


def test_d03_pauses_on_exactly_one_unavailable_external_fact() -> None:
    def prove(name: str) -> dict[str, Any]:
        if name == "retrieval":
            return {"result": "UNAVAILABLE_EXTERNAL_FACT", "fact": "primary source host offline"}
        return {"result": "PASS"}

    state = {
        "invocation": {"kind": "fresh"},
        "validated_recovery_envelope": None,
        "effective_run": {"ordered_unit_ids": ["U001"]},
        "frozen_executable_identities": [],
        "external_authorizations": [{"providers": [], "curriculum_digest": "fd"}],
        "frozen_digest": "fd",
        "run_id": "r",
        "engine_root": "/engine",
        "output_root": "/out",
    }
    update = inputs.D03_PROVE_CAPABILITIES(
        state,
        _Context(
            transport_registry=_Registry(
                prove_capability=prove, driver_capability_proof=_driver_capability_proof()
            )
        ),
    )
    assert update["pending_failure"]["class"] == "pause"


def test_d03_skips_the_driver_gate_for_a_registry_that_never_exposes_the_proof() -> None:
    """A registry built for an unrelated topology/plumbing test (the pre-N30
    contract: `prove_capability`/`observe_executable` only) is not forced to
    fabricate a `driver_capability_proof` it was never asked to carry -- this
    attribute gets the same optional, best-effort duck-typed treatment
    `observe_executable` already gets a few lines above it. The production CLI
    (`runtime.run_curriculum._prove_live_capabilities`) is the actual, unconditional
    stop: it always populates this attribute on the real registry before invoking the
    graph at all, and raises outright if it is not ready -- proven separately in
    `tests/runtime/test_run_curriculum.py`."""
    registry = _Registry(prove_capability=lambda name: {"result": "PASS"})
    state = {
        "invocation": {"kind": "fresh"},
        "validated_recovery_envelope": None,
        "effective_run": {"ordered_unit_ids": ["U001"]},
        "frozen_executable_identities": [],
        "external_authorizations": [{"providers": [], "curriculum_digest": "fd"}],
        "frozen_digest": "fd",
        "run_id": "r",
        "engine_root": "/engine",
        "output_root": "/out",
    }
    update = inputs.D03_PROVE_CAPABILITIES(state, _Context(transport_registry=registry))
    assert "pending_failure" not in update
    assert update["pending_guard"]["value"] == "capabilities_proven"


def test_d03_refuses_when_one_mandatory_driver_field_is_unproven() -> None:
    """Run 26's exact false-ready condition, reproduced at the D03 gate: binaries
    present (`executable_identity` PASS), but the provider is unauthenticated
    (`observable_subscription_backed_usability` FAIL) -- `ready` must be false and
    D03 must refuse, never silently admit a driver with one failed field."""
    failing_claude = {
        "cli": "claude", "model": "claude-sonnet-5", "provider": "anthropic",
        "ready": False,
        "failed_fields": ["observable_subscription_backed_usability"],
        "fields": {
            **_driver_capability_fields(),
            "observable_subscription_backed_usability": {
                "status": "FAIL", "reason": "nonzero_bounded_probe",
            },
        },
    }
    registry = _Registry(
        prove_capability=lambda name: {"result": "PASS"},
        driver_capability_proof=_driver_capability_proof(claude=failing_claude),
    )
    state = {
        "invocation": {"kind": "fresh"},
        "validated_recovery_envelope": None,
        "effective_run": {"ordered_unit_ids": ["U001"]},
        "frozen_executable_identities": [],
        "external_authorizations": [{"providers": [], "curriculum_digest": "fd"}],
        "frozen_digest": "fd",
        "run_id": "r",
        "engine_root": "/engine",
        "output_root": "/out",
    }
    update = inputs.D03_PROVE_CAPABILITIES(state, _Context(transport_registry=registry))
    assert update["pending_failure"]["cause"] == "capability"
    assert update["pending_failure"]["evidence"]["not_ready_drivers"] == ["claude"]
    assert "driver_capability_proof" in update["pending_failure"]["evidence"]["missing"]


def test_d03_refuses_when_a_driver_capability_proof_omits_a_required_field() -> None:
    """A registry that reports `ready: true` but is missing one of the six
    differentiated fields (e.g. a stale or buggy CLI build) must not be trusted at
    face value: D03 validates the proof's own shape, not just its top-level flag."""
    incomplete_claude = {
        "cli": "claude", "model": "claude-sonnet-5", "provider": "anthropic",
        "ready": True, "failed_fields": [],
        "fields": {name: {"status": "PASS"} for name in inputs.DRIVER_CAPABILITY_FIELDS
                   if name != "tool_mcp_closure"},
    }
    registry = _Registry(
        prove_capability=lambda name: {"result": "PASS"},
        driver_capability_proof=_driver_capability_proof(claude=incomplete_claude),
    )
    state = {
        "invocation": {"kind": "fresh"},
        "validated_recovery_envelope": None,
        "effective_run": {"ordered_unit_ids": ["U001"]},
        "frozen_executable_identities": [],
        "external_authorizations": [{"providers": [], "curriculum_digest": "fd"}],
        "frozen_digest": "fd",
        "run_id": "r",
        "engine_root": "/engine",
        "output_root": "/out",
    }
    update = inputs.D03_PROVE_CAPABILITIES(state, _Context(transport_registry=registry))
    assert update["pending_failure"]["cause"] == "capability"
    assert "required proof field" in update["pending_failure"]["message"]


def test_d04_opens_a_fresh_episode_with_the_frozen_thread_id_format() -> None:
    state = {
        "bootstrap_kind": "fresh",
        "invocation": {"episode_ordinal": 3},
        "validated_recovery_envelope": None,
        "capability_receipts": [{"key": "c"}],
        "effective_run": {"ordered_unit_ids": ["U001"]},
        "run_id": "abc",
        "contract_version": "v1",
        "created_at": "t",
        "engine_root": "/engine",
        "curriculum_root": "/engine/curricula/x",
        "active_manifest_path": "/m",
        "output_root": "/out",
        "mode": "one",
        "requested_unit_id": "U001",
        "frozen_inputs": [],
        "frozen_digest": "fd",
        "frozen_executable_identities": [],
        "external_authorizations": [{}],
        "terminal_history": [],
        "artifact_heads": {},
        "attempt_counters": {},
        "cursor": {},
        "unit_status": {},
        "accepted_unit_receipts": {},
    }
    update = inputs.D04_INITIALIZE_OR_RESUME(state, _Context())
    assert update["checkpoint_thread_id"] == "abc:episode:000003"
    assert update["checkpoint_namespace"] == ""
    assert update["pending_guard"]["value"] == "fresh_initialized"


def test_d04_refuses_to_resume_without_a_validated_recovery_envelope() -> None:
    state = {
        "bootstrap_kind": "resume",
        "invocation": {"episode_ordinal": 4},
        "validated_recovery_envelope": None,
        "capability_receipts": [{"key": "c"}],
        "effective_run": {},
        "run_id": "abc",
        "contract_version": "v1",
        "created_at": "t",
        "engine_root": "/e",
        "curriculum_root": "/c",
        "active_manifest_path": "/m",
        "output_root": "/o",
        "mode": "one",
        "requested_unit_id": "U001",
        "frozen_inputs": [],
        "frozen_digest": "fd",
        "frozen_executable_identities": [],
        "external_authorizations": [{}],
        "terminal_history": [{"kind": "INTERRUPTED"}],
        "artifact_heads": {},
        "attempt_counters": {},
        "cursor": {},
        "unit_status": {},
        "accepted_unit_receipts": {},
    }
    update = inputs.D04_INITIALIZE_OR_RESUME(state, _Context())
    assert update["pending_failure"]["cause"] == "invalid_input"


def test_d05_selects_the_first_unaccepted_closure_member() -> None:
    state = {
        "effective_run": {"target_closure": ["U001", "U002", "U003"]},
        "cursor": {"manifest_ordinal": 1, "accepted_ordinal": 1},
        "accepted_unit_receipts": {"U001": {"receipt_hash": "h"}},
        "unit_status": {"U001": "ACCEPTED"},
    }
    update = sources.D05_SELECT_NEXT_UNIT(state, _Context())
    assert update["selected_unit_id"] == "U002"
    assert update["unit_status"] == {"U002": "SELECTED"}
    assert update["cursor"] == {"manifest_ordinal": 2, "accepted_ordinal": 1}


def test_d05_reports_exhaustion_when_every_closure_member_is_accepted() -> None:
    state = {
        "effective_run": {"target_closure": ["U001", "U002"]},
        "cursor": {"manifest_ordinal": 2, "accepted_ordinal": 2},
        "accepted_unit_receipts": {"U001": {"receipt_hash": "a"}, "U002": {"receipt_hash": "b"}},
        "unit_status": {},
    }
    update = sources.D05_SELECT_NEXT_UNIT(state, _Context())
    assert update["selected_unit_id"] is None
    assert update["pending_guard"]["value"] == "manifest_exhausted"


def test_d06_compiles_a_positive_denominator_scaled_to_the_unit() -> None:
    unit = {
        "id": "U001",
        "required_explanation": ["a", "b"],
        "safety_focus": "c",
        "applications": ["d"],
    }
    state = {
        "effective_run": {"unit_records": [unit]},
        "selected_unit_id": "U001",
        "source_admissions": [],
        "engine_root": "/engine",
        **_CORRELATION,
    }
    update = sources.D06_COMPILE_SOURCE_REQUESTS(state, _Context())
    denominator = next(iter(update["source_denominators"].values()))
    assert denominator["size"] == len(update["source_requests"]) == 4
    assert sorted(request["required"] for request in update["source_requests"]) == [
        False,
        True,
        True,
        True,
    ]
    assert update["pending_guard"]["value"] == "discovery_fanout"


def test_d06_grants_m01_discover_exactly_the_resolved_retrieval_hosts() -> None:
    """N30V7-F07: D06 reads the frozen `resolved_hosts` (D01's own binding of the
    curriculum's named profile) and hands them to M01 as `discovery_authority.
    allowed_hosts` -- never a host the model itself proposed, and nothing at all
    when no authorization was ever frozen.
    """
    unit = {"id": "U001", "required_explanation": ["a"]}
    base = {
        "effective_run": {"unit_records": [unit]}, "selected_unit_id": "U001",
        "source_admissions": [], "engine_root": "/engine", **_CORRELATION,
    }
    granted = sources.D06_COMPILE_SOURCE_REQUESTS(
        {**base, "external_authorizations": [
            {"resolved_hosts": ["learn.sparkfun.com", "www.arduino.cc"]}]},
        _Context())
    packet = granted["pending_packet"]["packets"][0]
    assert packet["discovery_authority"]["allowed_hosts"] == [
        "learn.sparkfun.com", "www.arduino.cc"]

    ungranted = sources.D06_COMPILE_SOURCE_REQUESTS(
        {**base, "external_authorizations": []}, _Context())
    packet2 = ungranted["pending_packet"]["packets"][0]
    assert packet2["discovery_authority"]["allowed_hosts"] == []


def test_d06_scales_with_the_unit_rather_than_a_fixed_count() -> None:
    small = {"id": "U001", "required_explanation": ["a"]}
    large = {"id": "U002", "required_explanation": [f"fact {index}" for index in range(19)]}
    base = {"source_admissions": [], "engine_root": "/engine", **_CORRELATION}

    small_update = sources.D06_COMPILE_SOURCE_REQUESTS(
        {**base, "effective_run": {"unit_records": [small]}, "selected_unit_id": "U001"}, _Context()
    )
    large_update = sources.D06_COMPILE_SOURCE_REQUESTS(
        {**base, "effective_run": {"unit_records": [large]}, "selected_unit_id": "U002"}, _Context()
    )
    assert len(small_update["source_requests"]) == 1
    assert len(large_update["source_requests"]) == 19


def test_d07_admits_a_complete_correlated_join() -> None:
    digest = "a" * 64
    state = {
        "selected_unit_id": "U001",
        "source_denominators": {
            "U001/1": {"unit_id": "U001", "source_epoch": 1, "request_keys": ["k1", "k2"], "size": 2}
        },
        "source_discoveries": {},
        "retrievals": {
            "k1": {"unit_id": "U001", "sha256": digest, "locator": "l1", "content_type": "text/html"},
            "k2": {"unit_id": "U001", "sha256": digest, "locator": "l2", "content_type": "text/html"},
        },
        "source_interpretations": {
            "k1": {"unit_id": "U001", "retrieval_sha256": digest, "scope": "required_explanation"},
            "k2": {"unit_id": "U001", "retrieval_sha256": digest, "scope": "applications"},
        },
        "source_requests": [],
        "effective_run": {"unit_records": [{"id": "U001", "title": "t"}]},
        "engine_root": str(REPO_ROOT),
        **_CORRELATION,
    }
    update = sources.D07_CORRELATE_AND_ADMIT_SOURCES(state, _Context())
    assert len(update["source_admissions"]) == 2
    assert update["source_join_evidence"][0]["result"] == "PASS"
    assert update["pending_guard"]["value"] == "sources_admitted"


def test_d07_routes_a_missing_member_to_prerequisite_classification() -> None:
    digest = "a" * 64
    state = {
        "selected_unit_id": "U001",
        "source_denominators": {
            "U001/1": {"unit_id": "U001", "source_epoch": 1, "request_keys": ["k1", "k2"], "size": 2}
        },
        "source_discoveries": {},
        "retrievals": {"k1": {"unit_id": "U001", "sha256": digest, "locator": "l1"}},
        "source_interpretations": {"k1": {"unit_id": "U001", "retrieval_sha256": digest}},
        "source_requests": [{"key": "k2", "required": True}],
    }
    update = sources.D07_CORRELATE_AND_ADMIT_SOURCES(state, _Context())
    assert update["pending_guard"]["value"] == "prerequisite_unresolved"
    assert update["pending_guard"]["detail"]["required_missing"] == ["k2"]
    assert "source_admissions" not in update


def test_d10_refuses_to_send_an_authoritative_visual_to_a_model() -> None:
    head = "c" * 64
    state = {
        "selected_unit_id": "U001",
        "artifact_heads": {
            "units/U001/content": {"version": 1, "parent_hash": None, "hash": head},
            "units/U001/domain": {"version": 1, "parent_hash": None, "hash": "d" * 64},
        },
        "artifact_versions": [
            {
                "stream": "units/U001/content",
                "version": 1,
                "parent_hash": None,
                "hash": head,
                "body": {
                    "visuals": [
                        {"role": "photo", "kind": "illustration", "requests_authoritative_facts": True}
                    ]
                },
            }
        ],
        "engine_root": "/engine",
    }
    update = visuals.D10_COMPILE_VISUAL_BRIEFS(state, _Context())
    assert update["pending_failure"]["cause"] == "invalid_input"


def test_d10_splits_authoritative_and_illustrative_briefs() -> None:
    head = "c" * 64
    state = {
        "selected_unit_id": "U001",
        "artifact_heads": {
            "units/U001/content": {"version": 1, "parent_hash": None, "hash": head},
            "units/U001/domain": {"version": 1, "parent_hash": None, "hash": "d" * 64},
        },
        "artifact_versions": [
            {
                "stream": "units/U001/content",
                "version": 1,
                "parent_hash": None,
                "hash": head,
                "body": {
                    "visuals": [
                        {"role": "wiring", "kind": "build_map"},
                        {"role": "cover", "kind": "illustration"},
                    ]
                },
            }
        ],
        "engine_root": "/engine",
        **_CORRELATION,
    }
    update = visuals.D10_COMPILE_VISUAL_BRIEFS(state, _Context())
    denominator = next(iter(update["visual_denominators"].values()))
    assert denominator["deterministic_keys"] == ["U001/visual/wiring"]
    assert denominator["model_keys"] == ["U001/visual/cover"]
    assert update["pending_guard"]["value"] == "deterministic_visual_fanout"


def test_d10_routes_directly_to_the_barrier_when_no_deterministic_brief_exists() -> None:
    head = "c" * 64
    state = {
        "selected_unit_id": "U001",
        "artifact_heads": {
            "units/U001/content": {"version": 1, "parent_hash": None, "hash": head},
            "units/U001/domain": {"version": 1, "parent_hash": None, "hash": "d" * 64},
        },
        "artifact_versions": [
            {
                "stream": "units/U001/content",
                "version": 1,
                "parent_hash": None,
                "hash": head,
                "body": {"visuals": [{"role": "cover", "kind": "illustration"}]},
            }
        ],
        "engine_root": "/engine",
    }
    update = visuals.D10_COMPILE_VISUAL_BRIEFS(state, _Context())
    assert update["pending_guard"]["value"] == "no_deterministic_visuals"


def test_d11_treats_a_render_fault_as_a_system_failure_not_a_finding() -> None:
    def explode(brief: Any, facts: Any) -> Any:
        raise RuntimeError("typst exited 1")

    state = {
        "pending_packet": {
            "brief": {"key": "U001/visual/wiring", "subset": "deterministic", "kind": "build_map"}
        }
    }
    update = visuals.D11_CREATE_DETERMINISTIC_VISUALS(
        state, _Context(transport_registry=_Registry(render_deterministic_visual=explode))
    )
    assert update["pending_failure"]["cause"] == "tool"


def test_d11_refuses_a_brief_outside_the_deterministic_subset() -> None:
    state = {"pending_packet": {"brief": {"key": "k", "subset": "model"}}}
    update = visuals.D11_CREATE_DETERMINISTIC_VISUALS(
        state, _Context(transport_registry=_Registry(render_deterministic_visual=lambda *a: {}))
    )
    assert update["pending_failure"]["cause"] == "invalid_input"


def test_d12_dispatches_model_briefs_only_after_the_deterministic_subset_is_exact() -> None:
    head = "c" * 64
    state = {
        "selected_unit_id": "U001",
        "visual_denominators": {
            "k": {
                "unit_id": "U001",
                "content_hash": head,
                "deterministic_keys": ["v1"],
                "model_keys": ["v2"],
                "size": 2,
            }
        },
        "visual_briefs": [
            {"key": "v2", "unit_id": "U001", "subset": "model", "kind": "illustration"}
        ],
        **_CORRELATION,
        "visual_results": {
            "v1": {
                "key": "v1",
                "unit_id": "U001",
                "subset": "deterministic",
                "content_hash": head,
                "sha256": "a" * 64,
                "format": "svg",
                "provenance": "deterministic_renderer",
            }
        },
        "artifact_versions": [],
        "artifact_heads": {"units/U001/content": {"version": 1, "parent_hash": None, "hash": head}},
    }
    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(state, _Context())
    assert update["pending_guard"]["value"] == "model_visual_fanout"
    assert update["pending_packet"]["dispatch"] == "M04_CREATE_UNIT_VISUALS"
    member = update["pending_packet"]["packets"][0]
    assert member["brief"]["brief_id"] == "v2"
    assert member["brief"]["eligibility"] == "model_eligible"
    assert set(member) == {"brief", "permitted_facts", "visual_contract", "correlation"}
    assert "artifact_heads" not in update


def test_d12_admits_the_visual_head_once_the_denominator_is_complete() -> None:
    head = "c" * 64
    results = {
        key: {
            "key": key,
            "unit_id": "U001",
            "subset": subset,
            "content_hash": head,
            "sha256": f"{key}-hash",
            "format": "svg",
            "provenance": "deterministic_renderer" if subset == "deterministic" else "model_candidate",
        }
        for key, subset in (("v1", "deterministic"), ("v2", "model"))
    }
    state = {
        "selected_unit_id": "U001",
        "visual_denominators": {
            "k": {
                "unit_id": "U001",
                "content_hash": head,
                "deterministic_keys": ["v1"],
                "model_keys": ["v2"],
                "size": 2,
            }
        },
        "visual_briefs": [],
        "visual_results": results,
        "artifact_versions": [],
        "artifact_heads": {"units/U001/content": {"version": 1, "parent_hash": None, "hash": head}},
    }
    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(state, _Context())
    assert update["pending_guard"]["value"] == "visuals_admitted"
    admitted = update["artifact_heads"]["units/U001/visuals"]
    assert admitted["version"] == 1 and admitted["parent_hash"] is None


def test_d13_and_d14_produce_a_contiguous_inventory_for_every_page(tmp_path: Path) -> None:
    pdf = tmp_path / "unit.pdf"
    pdf.write_bytes(b"%PDF-1.7 rendered")
    pdf_hash = hashlib.sha256(pdf.read_bytes()).hexdigest()

    registry = _Registry(
        render_unit=lambda unit_id, parents: {
            "layout_path": str(tmp_path / "unit.typ"),
            "layout_sha256": "l" * 64,
            "pdf_path": str(pdf),
            "pdf_sha256": pdf_hash,
            "renderer": "typst-stub",
        },
        inspect_pages=lambda path, digest: {
            "pages": [_inspected_page(number) for number in range(1, 5)]
        },
    )
    context = _Context(transport_registry=registry)
    render_state = {
        "selected_unit_id": "U001",
        "artifact_heads": {
            f"units/U001/{channel}": {"version": 1, "parent_hash": None, "hash": f"{channel}-h"}
            for channel in ("domain", "content", "visuals")
        },
        "engine_root": str(tmp_path),
        "output_root": str(tmp_path),
    }
    render_update = render.D13_RENDER_UNIT(render_state, context)
    version = render_update["artifact_versions"][0]
    assert version["pdf_sha256"] == pdf_hash

    inspect_update = render.D14_INVENTORY_AND_INSPECT_UNIT_PAGES(
        {
            "selected_unit_id": "U001",
            "artifact_heads": {},
            "artifact_versions": [version],
            "output_root": str(tmp_path),
        },
        context,
    )
    inventory = inspect_update["unit_page_inventories"][0]
    assert inventory["page_count"] == 4 and inventory["contiguous"] is True
    assert len(inspect_update["unit_page_inspections"]) == 4
    assert inspect_update["pending_guard"]["value"] == "pages_inspected"


def test_d15_freezes_a_packet_covering_every_page(tmp_path: Path) -> None:
    rubric = tmp_path / "meta_prompt" / "assets"
    rubric.mkdir(parents=True)
    (rubric / "pedagogy.v1.md").write_text("# rubric", encoding="utf-8")
    pdf = tmp_path / "unit.pdf"
    pdf.write_bytes(b"%PDF-1.7 frozen")
    pdf_sha256 = hashlib.sha256(pdf.read_bytes()).hexdigest()

    state = {
        "selected_unit_id": "U001",
        "artifact_heads": {
            f"units/U001/{channel}": {"version": 1, "parent_hash": None, "hash": f"{channel}-h"}
            for channel in ("domain", "content", "visuals")
        },
        "unit_page_inventories": [
            {"unit_id": "U001", "pdf_sha256": pdf_sha256, "page_count": 2, "result": "PASS"}
        ],
        "unit_page_inspections": [
            {
                "key": f"k{number}",
                "unit_id": "U001",
                "pdf_sha256": pdf_sha256,
                "page": number,
                "page_sha256": f"{number}" * 64,
                "image_path": f"/tmp/page-{number}.png",
            }
            for number in (1, 2)
        ],
        "deterministic_checks": [
            {
                "scope": "unit",
                "owner": "U001",
                "head_hash": "h",
                "check_id": "c",
                "attempt": 1,
                "result": "PASS",
            }
        ],
        "source_admissions": [{"key": "s1", "unit_id": "U001"}],
        "engine_root": str(tmp_path),
        "artifact_versions": [_layout_version(pdf, pdf_sha256)],
        **_CORRELATION,
    }
    update = review.D15_FREEZE_UNIT_REVIEW_PACKET(state, _Context())
    packet = update["review_packets"][0]
    assert packet["denominator"] == {"pages": 2, "artifacts": 4, "checks": 1, "sources": 1}
    # B-11: the layout the packet names comes from D13's appended version, and
    # every other artifact hash from its admitted head.
    assert packet["artifact_hashes"]["layout"] == "layout-h"
    assert packet["packet_hash"] == packet["key"]
    assert len(packet["page_keys"]) == 2


# ---------------------------------------------------------------------------
# Staged worker packets (N30 finding B-2, spec sections 9 and 10)
# ---------------------------------------------------------------------------


DISPATCHING_NODE_IDS: tuple[str, ...] = (
    "D06_COMPILE_SOURCE_REQUESTS",
    "D06B_RETRIEVE_SOURCE_CANDIDATES",
    "D07_CORRELATE_AND_ADMIT_SOURCES",
    "D08_VALIDATE_DOMAIN",
    "D10_COMPILE_VISUAL_BRIEFS",
    "D12_VISUAL_BARRIER_AND_JOIN",
    "D15_FREEZE_UNIT_REVIEW_PACKET",
)


@pytest.mark.parametrize("node_id", DISPATCHING_NODE_IDS)
def test_every_dispatching_node_authorizes_a_worker_packet(node_id: str) -> None:
    """A node that dispatches must be able to persist what it dispatches."""

    spec = NODE_CATALOGUE[node_id]
    assert "pending_packet" in spec.outputs
    assert {"run_id", "episode_id"} <= set(spec.inputs)


def _install_curriculum_contracts(engine_root: Path) -> None:
    """Copy the real `CURRICULUM_CONTRACTS` files into a synthetic engine root.

    B-10: a stub stands in for the contract without being it, which is how D09
    came to validate unit content against the whole-curriculum manifest schema
    without any test noticing. Every state built here is held to the bytes a real
    run is held to.
    """

    for relative in domain.CURRICULUM_CONTRACTS:
        source = REPO_ROOT / relative
        assert source.is_file(), f"engine contract {relative} is missing from the repo"
        target = engine_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())


def _domain_admission_state(tmp_path: Path) -> dict[str, Any]:
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    (schema_dir / "domain.json").write_text(json.dumps({"type": "object"}), encoding="utf-8")
    _install_curriculum_contracts(tmp_path)
    (schema_dir / "manifest_domain.metaschema.v1.json").write_text("{}", encoding="utf-8")
    policy = tmp_path / "policy"
    policy.mkdir()
    (policy / "calibration.v1.yaml").write_text("{}", encoding="utf-8")
    return {
        "selected_unit_id": "U001",
        "effective_run": {"unit_records": [{"id": "U001", "title": "t"}]},
        "artifact_versions": [
            {
                "stream": "units/U001/domain",
                "version": 1,
                "parent_hash": None,
                "hash": "d" * 64,
                "body": {"facts": [{"fact_id": "f1"}]},
                "schema_path": "schemas/domain.json",
                "verifier_result": {"result": "all_fixtures_behaved"},
            }
        ],
        "artifact_heads": {},
        "source_admissions": [{"key": "s1", "unit_id": "U001", "fact_id": "f1"}],
        "engine_root": str(tmp_path),
        **_CORRELATION,
    }


def _staged_members(update: dict[str, Any], destination: str) -> list[dict[str, Any]]:
    packet = update["pending_packet"]
    assert packet["dispatch"] == destination
    members = packet["packets"]
    assert members
    for member in members:
        assert member["correlation"]["run_id"] == _CORRELATION["run_id"]
        assert member["correlation"]["episode_id"] == _CORRELATION["episode_id"]
        assert member["correlation"]["correlation_key"]
        assert "reservation" not in member
    return members


def test_a_staged_discovery_packet_is_an_admissible_m01_discovery_projection() -> None:
    from runtime.langgraph_factory import model_nodes as mn

    unit = {"id": "U001", "title": "t", "required_explanation": ["a"], "safety_focus": ["b"]}
    update = sources.D06_COMPILE_SOURCE_REQUESTS(
        {
            "effective_run": {"unit_records": [unit]},
            "selected_unit_id": "U001",
            "source_admissions": [],
            "engine_root": "/engine",
            **_CORRELATION,
        },
        _Context(),
    )
    members = _staged_members(update, "M01_RESEARCH_UNIT_SOURCES")
    assert len(members) == len(update["source_requests"])
    keys = {member["correlation"]["correlation_key"] for member in members}
    assert keys == {request["key"] for request in update["source_requests"]}
    for member in members:
        assert member["phase"] == "DISCOVER"
        projection = mn.build_projection("M01_discovery", member)
        assert set(projection) == {"request", "unit", "source_rules", "discovery_authority"}


def test_a_staged_interpretation_packet_carries_only_its_own_retrieval_group() -> None:
    from runtime.langgraph_factory import model_nodes as mn

    digest = "a" * 64
    update = sources.D06B_RETRIEVE_SOURCE_CANDIDATES(
        {
            "selected_unit_id": "U001",
            "source_requests": [
                {
                    "key": "U001/1/required_explanation:000",
                    "unit_id": "U001",
                    "source_epoch": 1,
                    "fact_id": "required_explanation:000",
                    "question": "q",
                    "required": True,
                    "scope": "required_explanation",
                }
            ],
            "source_denominators": {
                "U001/1": {
                    "unit_id": "U001",
                    "source_epoch": 1,
                    "request_keys": ["U001/1/required_explanation:000"],
                    "size": 1,
                }
            },
            "source_discoveries": {
                "U001/1/required_explanation:000": {"locators": [
                    {"request_id": "U001/1/required_explanation:000",
                     "url": "https://example.test/a", "title": "t", "publisher": "p",
                     "locator_kind": "primary", "rationale": "why"}]}
            },
            "external_authorizations": [{"providers": {"primary_source_hosts": ["primary_source_bytes"]},
                                         "approved_at_utc": "2026-01-01T00:00:00Z",
                                         "expires_at_utc": "2099-01-01T00:00:00Z",
                                         "curriculum_digest": "c" * 64, "output_root": "/tmp/out"}],
            "effective_run": {"unit_records": [{"id": "U001", "title": "t"}]},
            **_CORRELATION,
        },
        _Context(
            source_retriever=_Registry(
                fetch=lambda locator, *, authorization_receipt, data_class="primary_source_bytes": {
                    "sha256": digest,
                    "status": 200,
                    "content_type": "text/html",
                    "bytes_path": "/tmp/a.html",
                }
            )
        ),
    )
    members = _staged_members(update, "M01_RESEARCH_UNIT_SOURCES")
    assert len(members) == 1
    assert members[0]["phase"] == "INTERPRET"
    projection = mn.build_projection("M01_interpretation", members[0])
    group = projection["retrieval_group"]
    assert [record["retrieval_id"] for record in group["retrieved_records"]] == [
        "U001/1/required_explanation:000"
    ]
    assert "discovery_authority" not in projection


def test_a_staged_domain_packet_is_an_admissible_m02_projection(tmp_path: Path) -> None:
    from runtime.langgraph_factory import model_nodes as mn

    digest = "a" * 64
    (tmp_path / "schemas").mkdir()
    (tmp_path / "schemas" / "manifest_domain.metaschema.v1.json").write_text("{}", encoding="utf-8")
    (tmp_path / "policy").mkdir()
    (tmp_path / "policy" / "calibration.v1.yaml").write_text("{}", encoding="utf-8")

    update = sources.D07_CORRELATE_AND_ADMIT_SOURCES(
        {
            "selected_unit_id": "U001",
            "source_denominators": {
                "U001/1": {
                    "unit_id": "U001",
                    "source_epoch": 1,
                    "request_keys": ["k1"],
                    "size": 1,
                }
            },
            "source_discoveries": {},
            "retrievals": {
                "k1": {
                    "unit_id": "U001",
                    "sha256": digest,
                    "locator": "l1",
                    "content_type": "text/html",
                }
            },
            "source_interpretations": {
                "k1": {"unit_id": "U001", "retrieval_sha256": digest, "scope": "s"}
            },
            "source_requests": [],
            "effective_run": {"unit_records": [{"id": "U001", "title": "t"}]},
            "engine_root": str(tmp_path),
            **_CORRELATION,
        },
        _Context(),
    )
    members = _staged_members(update, "M02_CREATE_UNIT_DOMAIN_DATA")
    projection = mn.build_projection("M02_domain", members[0])
    assert projection["unit"]["unit_id"] == "U001"
    assert [source["source_id"] for source in projection["admitted_sources"]] == ["k1"]
    assert projection["domain_schema"]["sha256"]


def test_a_staged_content_packet_is_an_admissible_m03_projection(tmp_path: Path) -> None:
    from runtime.langgraph_factory import model_nodes as mn

    update = domain.D08_VALIDATE_DOMAIN(_domain_admission_state(tmp_path), _Context())
    assert update["pending_guard"]["value"] == "domain_admitted"
    members = _staged_members(update, "M03_WRITE_UNIT_CONTENT")
    projection = mn.build_projection("M03_content", members[0])
    assert projection["admitted_domain"]["domain_hash"] == "d" * 64
    assert len(projection["curriculum_contracts"]) == 2
    assert [item["source_id"] for item in projection["admitted_evidence_references"]] == ["s1"]


def test_a_repairable_domain_stages_no_content_packet(tmp_path: Path) -> None:
    """A failing stage dispatches nothing: only an admitted head authorizes M03."""

    state = _domain_admission_state(tmp_path)
    state["artifact_versions"][0]["verifier_result"] = {"result": "fixtures_failed"}
    update = domain.D08_VALIDATE_DOMAIN(state, _Context())
    assert update["pending_guard"]["value"] == "domain_repairable"
    assert "pending_packet" not in update


def test_a_staged_deterministic_visual_packet_is_what_d11_consumes() -> None:
    head = "c" * 64
    update = visuals.D10_COMPILE_VISUAL_BRIEFS(
        {
            "selected_unit_id": "U001",
            "artifact_heads": {
                "units/U001/content": {"version": 1, "parent_hash": None, "hash": head},
                "units/U001/domain": {"version": 1, "parent_hash": None, "hash": "d" * 64},
            },
            "artifact_versions": [
                {
                    "stream": "units/U001/content",
                    "version": 1,
                    "parent_hash": None,
                    "hash": head,
                    "body": {
                        "visuals": [
                            {"role": "wiring", "kind": "build_map", "permitted_facts": ["f1"]}
                        ]
                    },
                }
            ],
            "engine_root": "/engine",
            **_CORRELATION,
        },
        _Context(),
    )
    packet = update["pending_packet"]
    assert packet["dispatch"] == "D11_CREATE_DETERMINISTIC_VISUALS"
    member = packet["packets"][0]

    # B-12: `_staged_fanout` translates each staged member into `Send(dest, member)`
    # unchanged, so the member arrives as D11's *whole input state* and is narrowed
    # by `project()` on channel name. A member naming anything that is not a channel
    # is a member D11 cannot read, so it is handed to the real D11 unadapted here.
    assert set(member) <= set(FIELD_REDUCER_CLASSES)
    assert member["pending_packet"]["brief"]["subset"] == "deterministic"
    assert member["pending_packet"]["permitted_facts"] == ["f1"]

    produced = visuals.D11_CREATE_DETERMINISTIC_VISUALS(
        member,
        _Context(
            transport_registry=_Registry(
                render_deterministic_visual=lambda brief, facts: {
                    "asset_path": "/tmp/a.svg",
                    "sha256": "b" * 64,
                    "format": "svg",
                }
            )
        ),
    )
    assert produced["pending_guard"]["value"] == "visual_produced"


def test_an_empty_deterministic_subset_stages_no_packet() -> None:
    head = "c" * 64
    update = visuals.D10_COMPILE_VISUAL_BRIEFS(
        {
            "selected_unit_id": "U001",
            "artifact_heads": {
                "units/U001/content": {"version": 1, "parent_hash": None, "hash": head},
                "units/U001/domain": {"version": 1, "parent_hash": None, "hash": "d" * 64},
            },
            "artifact_versions": [
                {
                    "stream": "units/U001/content",
                    "version": 1,
                    "parent_hash": None,
                    "hash": head,
                    "body": {"visuals": [{"role": "cover", "kind": "illustration"}]},
                }
            ],
            "engine_root": "/engine",
            **_CORRELATION,
        },
        _Context(),
    )
    assert update["pending_guard"]["value"] == "no_deterministic_visuals"
    assert "pending_packet" not in update


def test_a_staged_visual_packet_is_an_admissible_m04_projection() -> None:
    from runtime.langgraph_factory import model_nodes as mn

    head = "c" * 64
    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(
        {
            "selected_unit_id": "U001",
            "visual_denominators": {
                "k": {
                    "unit_id": "U001",
                    "content_hash": head,
                    "deterministic_keys": [],
                    "model_keys": ["v2"],
                    "size": 1,
                }
            },
            "visual_briefs": [
                {
                    "key": "v2",
                    "unit_id": "U001",
                    "subset": "model",
                    "role": "cover",
                    "kind": "illustration",
                    "content_hash": head,
                    "permitted_facts": ["f1"],
                }
            ],
            "visual_results": {},
            "artifact_versions": [],
            "artifact_heads": {
                "units/U001/content": {"version": 1, "parent_hash": None, "hash": head}
            },
            **_CORRELATION,
        },
        _Context(),
    )
    members = _staged_members(update, "M04_CREATE_UNIT_VISUALS")
    projection = mn.build_projection("M04_visual", members[0])
    assert set(projection) == {"brief", "permitted_facts", "visual_contract"}
    assert projection["brief"]["brief_id"] == "v2"
    mn._assert_visual_brief_eligible(projection["brief"])


def test_a_kind_m04_would_refuse_is_classified_deterministic() -> None:
    """M04's refusal list and D10's split are the same boundary, not two."""

    from runtime.langgraph_factory import model_nodes as mn

    for klass in mn.AUTHORITATIVE_VISUAL_CLASSES:
        assert visuals.classify_visual_brief({"kind": klass}) == "deterministic"


def test_a_staged_review_packet_is_an_admissible_m05_projection(tmp_path: Path) -> None:
    from runtime.langgraph_factory import model_nodes as mn

    assets = tmp_path / "meta_prompt" / "assets"
    assets.mkdir(parents=True)
    (assets / "pedagogy.v1.md").write_text("# rubric", encoding="utf-8")
    pdf = tmp_path / "unit.pdf"
    pdf.write_bytes(b"%PDF-1.7 reviewed")
    pdf_sha256 = hashlib.sha256(pdf.read_bytes()).hexdigest()

    update = review.D15_FREEZE_UNIT_REVIEW_PACKET(
        {
            "selected_unit_id": "U001",
            "artifact_heads": {
                f"units/U001/{channel}": {
                    "version": 1,
                    "parent_hash": None,
                    "hash": f"{channel}-h",
                }
                for channel in ("domain", "content", "visuals")
            },
            "unit_page_inventories": [
                {"unit_id": "U001", "pdf_sha256": pdf_sha256, "page_count": 2, "result": "PASS"}
            ],
            "unit_page_inspections": [
                {
                    "key": f"k{number}",
                    "unit_id": "U001",
                    "pdf_sha256": pdf_sha256,
                    "page": number,
                    "page_sha256": f"{number}" * 64,
                    "image_path": f"/tmp/page-{number}.png",
                }
                for number in (1, 2)
            ],
            "deterministic_checks": [
                {
                    "scope": "unit",
                    "owner": "U001",
                    "head_hash": "h",
                    "check_id": "c",
                    "attempt": 1,
                    "result": "PASS",
                    "detail": {"note": "n"},
                }
            ],
            "source_admissions": [{"key": "s1", "unit_id": "U001"}],
            "engine_root": str(tmp_path),
            "artifact_versions": [_layout_version(pdf, pdf_sha256)],
            **_CORRELATION,
        },
        _Context(),
    )
    members = _staged_members(update, "M05_REVIEW_ACTUAL_UNIT")
    projection = mn.build_projection("M05_unit_review", members[0])
    assert mn._page_denominator(projection, label="M05") == {1: "1" * 64, 2: "2" * 64}
    # `attempt` is a review-denied name, so the reviewer sees the check, not the
    # number of tries it took to pass it.
    assert all("attempt" not in record for record in projection["deterministic_evidence"])


def test_no_staged_packet_carries_a_reservation_it_did_not_earn() -> None:
    """D90 mints reservations; a deterministic node only requests one."""

    source = "".join(
        (PACKAGE_ROOT / f"{name}.py").read_text(encoding="utf-8")
        for name in ("sources", "domain", "visuals", "review")
    )
    assert "reservation_kind" not in source
    assert "attempt_ordinal" not in source


# ---------------------------------------------------------------------------
# B-7 rework — the deterministic node mints the version, the model never does
# ---------------------------------------------------------------------------


def _model_update(
    job_id: str,
    packet: dict[str, Any],
    candidate: dict[str, Any],
    correlation_key: str | None = None,
) -> dict[str, Any]:
    """Run one real model adapter over a canned candidate, with a real reservation."""

    import tempfile

    from runtime.langgraph_factory import model_nodes as mn

    registry = mn.tp.load_job_registry()
    sandbox = Path(tempfile.mkdtemp(prefix="plan26-n22-b7-"))
    context = mn.ModelNodeContext(
        transport=mn.tp.FakeCliTransport(
            sandbox_root=sandbox, responses={job_id: candidate}, registry=registry
        ),
        registry=registry,
    )
    staged = dict(packet)
    staged["correlation"] = dict(_CORRELATION)
    if correlation_key is not None:
        staged["correlation"]["correlation_key"] = correlation_key
    staged["reservation"] = {
        "reservation_kind": mn.RESERVATION_KIND,
        "activation_id": "activation-1",
        "reservation_id": "activation-1#1",
        "job_id": job_id,
        "counter_key": f"{job_id}|k",
        "attempt_ordinal": 1,
    }
    return mn.MODEL_NODE_ADAPTERS[job_id](staged, context)


def _m02_candidate_versions(unit_id: str = "U001", **fields: Any) -> list[dict[str, Any]]:
    packet = {
        "unit": {"unit_id": unit_id, "title": "t"},
        "admitted_sources": [
            {
                "source_id": "s1",
                "fact_id": "f1",
                "locator": "l",
                "sha256": "0" * 64,
                "content_type": "text/html",
                "scope": "required_explanation",
            }
        ],
        "domain_schema": {"path": sources.DOMAIN_SCHEMA_CONTRACT, "sha256": "0" * 64},
        "verifier_interface": {"declared_at": "/verifier_result"},
    }
    candidate = {
        "domain_version": {
            "unit_id": unit_id,
            "fields": {
                "facts": [{"fact_id": "f1"}],
                "verifier_result": {"result": "all_fixtures_behaved"},
                **fields,
            },
            "evidence_references": [{"source_id": "s1", "source_location": "p.1"}],
        }
    }
    return _model_update("M02_CREATE_UNIT_DOMAIN_DATA", packet, candidate)["artifact_versions"]


def _domain_state_from_model(tmp_path: Path, heads: dict[str, Any] | None = None) -> dict[str, Any]:
    schemas = tmp_path / "schemas"
    schemas.mkdir()
    (schemas / "manifest_domain.metaschema.v1.json").write_text(
        json.dumps({"type": "object"}), encoding="utf-8"
    )
    _install_curriculum_contracts(tmp_path)
    return {
        "selected_unit_id": "U001",
        "effective_run": {"unit_records": [{"id": "U001", "title": "t"}]},
        "artifact_versions": _m02_candidate_versions(),
        "artifact_heads": dict(heads or {}),
        "source_admissions": [{"key": "s1", "unit_id": "U001", "fact_id": "f1"}],
        "engine_root": str(tmp_path),
        **_CORRELATION,
    }


def test_d08_admits_a_real_m02_candidate_the_model_never_versioned(tmp_path: Path) -> None:
    """B-7: the candidate carries no version or hash, so D08 mints both."""

    state = _domain_state_from_model(tmp_path)
    record = state["artifact_versions"][0]
    assert record["record_kind"] == "model_candidate"
    assert not {"stream", "version", "parent_hash", "hash", "body"} & set(record)

    update = domain.D08_VALIDATE_DOMAIN(state, _Context())

    assert update["pending_guard"]["value"] == "domain_admitted"
    body = record["payload"]["domain_version"]["fields"]
    head = update["artifact_heads"]["units/U001/domain"]
    assert head == {"version": 1, "parent_hash": None, "hash": canonical_digest(body)}
    minted = update["artifact_versions"][0]
    assert minted["body"] == body
    assert minted["schema_path"] == sources.DOMAIN_SCHEMA_CONTRACT
    assert minted["candidate_sha256"] == record["candidate_sha256"]


def test_an_admitted_domain_version_is_the_current_heads_successor(tmp_path: Path) -> None:
    """The minted version is `advance_head`'s own rule, read off the head."""

    heads = {"units/U001/domain": {"version": 2, "parent_hash": "a" * 64, "hash": "b" * 64}}
    update = domain.D08_VALIDATE_DOMAIN(_domain_state_from_model(tmp_path, heads), _Context())
    head = update["artifact_heads"]["units/U001/domain"]
    assert head["version"] == 3
    assert head["parent_hash"] == "b" * 64


def test_two_domain_candidates_differing_in_body_mint_different_hashes(tmp_path: Path) -> None:
    """The minted hash is the canonical digest of the body, so it tracks the bytes."""

    state = _domain_state_from_model(tmp_path)
    first = domain.D08_VALIDATE_DOMAIN(state, _Context())
    state["artifact_versions"] = _m02_candidate_versions(extra_field={"changed": True})
    second = domain.D08_VALIDATE_DOMAIN(state, _Context())
    assert (
        first["artifact_heads"]["units/U001/domain"]["hash"]
        != second["artifact_heads"]["units/U001/domain"]["hash"]
    )


def test_the_contract_d09_validates_against_admits_every_legal_m03_body() -> None:
    """B-10: the author's output schema and the admitting contract are one language.

    D08 hands M03 `CURRICULUM_CONTRACTS` and D09 validates M03's answer against
    `CURRICULUM_CONTRACTS[0]`. When the two describe different documents — as they
    did when the constant named the whole-curriculum manifest schema — the
    intersection is empty and no content can ever be admitted, whatever the model
    writes. Proven as schema algebra and then on the real validator, so it holds
    for every legal body rather than for one sample.

    Inverts when a document M03 may legally emit is one D09's contract rejects.
    """

    import jsonschema

    contract = json.loads(
        (REPO_ROOT / domain.CURRICULUM_CONTRACTS[0]).read_text(encoding="utf-8")
    )
    unit_content = json.loads(
        (FACTORY_ROOT / "schemas" / "M03_write_unit_content.schema.json").read_text(
            encoding="utf-8"
        )
    )["properties"]["unit_content"]

    assert set(contract["required"]) <= set(unit_content["properties"])
    assert set(unit_content["properties"]) <= set(contract["properties"])

    body: dict[str, Any] = {
        "unit_id": "U001",
        "sections": [{"section_id": "s1", "heading": "h", "body": "b"}],
        "evidence_references": [
            {"section_id": "s1", "source_id": "x", "source_location": "p.1"}
        ],
    }
    jsonschema.Draft202012Validator(unit_content).validate(body)
    jsonschema.Draft202012Validator(contract).validate(body)

    # D10 compiles the visual denominator off this same body, so the contract must
    # admit the declaration it reads or every unit ships with no visuals at all.
    with_visuals = {
        **body,
        "visuals": [{"role": "wiring", "kind": "build_map", "permitted_facts": ["f1"]}],
    }
    jsonschema.Draft202012Validator(contract).validate(with_visuals)
    assert "visuals" in contract["properties"]


def test_d09_admits_a_real_m03_candidate_against_the_admitted_domain_head(tmp_path: Path) -> None:
    """The content path has the same gap and the same fix."""

    _install_curriculum_contracts(tmp_path)
    domain_hash = "d" * 64
    packet = {
        "unit": {"unit_id": "U001", "title": "t"},
        "admitted_domain": {
            "unit_id": "U001",
            "domain_hash": domain_hash,
            "version": 1,
            "facts": [{"fact_id": "f1"}],
        },
        "curriculum_contracts": [{"path": content.CURRICULUM_CONTRACTS[0], "sha256": "0" * 64}],
    }
    candidate = {
        "unit_content": {
            "unit_id": "U001",
            "sections": [{"section_id": "s1", "heading": "h", "body": "b"}],
            "evidence_references": [
                {"section_id": "s1", "source_id": "s1", "source_location": "p.1"}
            ],
        }
    }
    versions = _model_update("M03_WRITE_UNIT_CONTENT", packet, candidate)["artifact_versions"]
    update = content.D09_VALIDATE_CONTENT(
        {
            "selected_unit_id": "U001",
            "effective_run": {"unit_records": [{"id": "U001", "title": "t"}]},
            "artifact_versions": versions,
            "artifact_heads": {
                "units/U001/domain": {"version": 1, "parent_hash": None, "hash": domain_hash}
            },
            "engine_root": str(tmp_path),
        },
        _Context(),
    )
    assert update["pending_guard"]["value"] == "content_admitted"
    body = versions[0]["payload"]["unit_content"]
    assert update["artifact_heads"]["units/U001/content"] == {
        "version": 1,
        "parent_hash": None,
        "hash": canonical_digest(body),
    }
    assert update["artifact_versions"][0]["domain_hash"] == domain_hash


def test_d06b_reads_locators_from_the_discovery_candidates_payload(tmp_path: Path) -> None:
    """The join field M01 emits lives under `payload`, not on the record."""

    from runtime.langgraph_factory.nodes import candidate_field

    packet = {
        "request": {"request_id": "U001/f1", "question": "q", "scope": "required_explanation"},
        "unit": {"unit_id": "U001", "title": "t"},
        "source_rules": dict(sources.SOURCE_RULES),
        "discovery_authority": {
            "phase": "DISCOVER",
            "locators_only": True,
            "may_retrieve_bytes": False,
            "allowed_hosts": ["example.invalid"],
        },
    }
    candidate = {
        "locators": [
            {
                "request_id": "U001/f1",
                "url": "https://example.invalid/f1",
                "title": "t",
                "publisher": "p",
                "locator_kind": "primary",
                "rationale": "r",
            }
        ]
    }
    update = _model_update(
        "M01_RESEARCH_UNIT_SOURCES", {**packet, "phase": "DISCOVER"}, candidate, "U001/f1"
    )
    record = next(iter(update["source_discoveries"].values()))
    assert "locators" not in record
    assert candidate_field(record, "locators") == candidate["locators"]


def test_a_model_visual_candidate_joins_under_its_brief_key(tmp_path: Path) -> None:
    """M04 keys on its activation; the denominator is keyed on the brief."""

    content_hash = "c" * 64
    brief = {
        "key": "U001/visual/diagram",
        "unit_id": "U001",
        "role": "diagram",
        "kind": "illustration",
        "subset": "model",
        "content_hash": content_hash,
        "domain_hash": "d" * 64,
        "permitted_facts": ["f1"],
    }
    packet = {
        "brief": {
            "brief_id": brief["key"],
            "unit_id": "U001",
            "role": "diagram",
            "visual_class": "illustration",
            "content_hash": content_hash,
            "authoritative": False,
            "eligibility": "model_eligible",
        },
        "permitted_facts": ["f1"],
        "visual_contract": dict(visuals.MODEL_VISUAL_CONTRACT),
    }
    candidate = {
        "visual_candidate": {
            "brief_id": brief["key"],
            "prompt_text": "p",
            "dimensions": {"width_px": 100, "height_px": 100},
            "image_format": "png",
            "accessibility_text": "a",
        },
        "provenance_declaration": {
            "brief_id": brief["key"],
            "permitted_facts_used": ["f1"],
            "asserts_authoritative_detail": False,
        },
    }
    results = _model_update(
        "M04_CREATE_UNIT_VISUALS", packet, candidate, f"U001/{content_hash}/{brief['key']}"
    )["visual_results"]
    assert brief["key"] not in results

    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(
        {
            "selected_unit_id": "U001",
            "visual_denominators": {
                "k": {
                    "unit_id": "U001",
                    "content_hash": content_hash,
                    "deterministic_keys": [],
                    "model_keys": [brief["key"]],
                    "size": 1,
                }
            },
            "visual_briefs": [brief],
            "visual_results": results,
            "artifact_versions": [],
            "artifact_heads": {
                "units/U001/content": {"version": 1, "parent_hash": None, "hash": content_hash}
            },
            **_CORRELATION,
        },
        _Context(),
    )
    assert update["pending_guard"]["value"] == "visuals_admitted"
    assert update["artifact_heads"]["units/U001/visuals"]["version"] == 1


def test_no_node_reads_an_admission_field_off_a_model_candidate() -> None:
    """Version, hash, and parent are minted here; a node never reads one from a model."""

    from runtime.langgraph_factory import model_nodes as mn
    from runtime.langgraph_factory.nodes import mint_version

    minted = mint_version({"key": "candidate:x"}, {}, "units/U001/domain", body={"a": 1})
    assert set(mn.ADMISSION_OWNED_CANDIDATE_FIELDS) <= set(minted)
    assert minted["version"] == 1 and minted["parent_hash"] is None
    assert minted["hash"] == canonical_digest({"a": 1})
    assert minted["minted_by"] == "deterministic_admission"


def test_the_domain_body_is_held_to_the_contract_the_run_declares(tmp_path: Path) -> None:
    """The schema is the run's own, never a path the model chose."""

    state = _domain_state_from_model(tmp_path)
    declared = tmp_path / "curricula" / "synthetic" / "manifest.domain.schema.v1.json"
    declared.parent.mkdir(parents=True)
    declared.write_text(
        json.dumps({"type": "object", "required": ["absent"]}), encoding="utf-8"
    )
    state["effective_run"]["manifest_schema"] = "curricula/synthetic/manifest.domain.schema.v1.json"

    update = domain.D08_VALIDATE_DOMAIN(state, _Context())

    assert update["pending_guard"]["value"] == "domain_repairable"
    assert [finding["check_id"] for finding in update["pending_guard"]["detail"]["findings"]] == [
        "domain_schema_valid"
    ]
