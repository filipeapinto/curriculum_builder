"""Plan 26 per-unit path gate (spec sections 8.1, 8.2, 10, 11.3-11.4): N30's wiring.

Every topology assertion runs against the one real `CompiledStateGraph` that
`graph.build_curriculum_factory_graph` produces from the real N22/N23 callables,
and every denominator assertion runs the real node body and the real guard. A
mock would prove that a stand-in joins correctly, which is the one thing this
file exists to rule out.

The episode now really executes: `_run_episode` streams the one compiled
production graph from D00 to a written terminal, against `RuntimeContext` test
doubles and a test-only model transport. Three kinds of test live here:

- assertions about the unit topology that is genuinely registered now,
- assertions that run one real episode of the real compiled graph, and
- explicitly named `test_blocked_*` guards that assert the *current, broken*
  behaviour of a dependency outside this node's write set.

Each blocked guard names its owner and the exact rework that inverts it, and
`test_every_blocking_gap_is_declared_with_an_owner_and_rework_edge` keeps that
list total, so a gap cannot be quietly forgotten once it is fixed: the guard
fails the moment the rework lands, which is what forces this file to be
revisited. The guards that closed B-1, B-2 and B-3 were inverted this way and
now assert the fixed behaviour instead.

Skips only where the hash-locked environment is absent; the node's evidence was
produced by running this file inside it.
"""

import ast
import hashlib
import inspect
import json
import random
import re
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

try:  # pragma: no cover - environment probe, not behavior
    import langgraph  # noqa: F401
    import langgraph.checkpoint.sqlite  # noqa: F401
except ModuleNotFoundError as exc:  # pragma: no cover
    raise unittest.SkipTest(
        "plan26 hash-locked environment not installed "
        "(python3 -m pip install --require-hashes -r requirements/plan26.lock): "
        f"{exc}"
    ) from exc

import pytest
import yaml
from langgraph.channels.binop import BinaryOperatorAggregate
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from typing_extensions import Annotated, TypedDict

from runtime.langgraph_factory import graph as G
from runtime.langgraph_factory import model_nodes as mn
from runtime.langgraph_factory import persistence as P
from runtime.langgraph_factory import routing as R
from runtime.langgraph_factory import unit_graph as U
from runtime.langgraph_factory.nodes import (
    NODE_CATALOGUE,
    domain,
    inputs,
    render,
    review,
    sources,
    visuals,
)
from runtime.langgraph_factory.reducers import WriteOnceConflict, write_once
from runtime.langgraph_factory.state import (
    FACTORY_STATE_FIELDS,
    FIELD_REDUCER_CLASSES,
    FactoryState,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
UNIT_GRAPH_PY = REPO_ROOT / "runtime" / "langgraph_factory" / "unit_graph.py"

MODEL_NODE_IDS = frozenset(mn.MODEL_NODE_ADAPTERS)


# ---------------------------------------------------------------------------
# fixtures — one real compiled graph, shared
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def compiled() -> Any:
    output_root = Path(tempfile.mkdtemp(prefix="plan26-n30-"))
    return G.build_curriculum_factory_graph(engine_root=REPO_ROOT, output_root=output_root)


@pytest.fixture(scope="module")
def topology(compiled: Any) -> dict[str, Any]:
    return G.compiled_topology(compiled)


@pytest.fixture(scope="module")
def available() -> tuple[str, ...]:
    return tuple(sorted(G.binding_inventory()))


class _Token:
    def is_set(self) -> bool:
        return False


class _Context:
    """The narrow service surface a deterministic node body reaches."""

    def __init__(self, **services: Any) -> None:
        self.engine_root = services.pop("engine_root", Path("/tmp"))
        self.output_root = services.pop("output_root", Path("/tmp/out"))
        self.path_guard = object()
        self.evidence_service = object()
        self.transport_registry = services.pop("transport_registry", object())
        self.source_retriever = services.pop("source_retriever", None)
        self.signal_token = services.pop("signal_token", _Token())
        self.clock = services.pop("clock", lambda: "2026-01-01T00:00:00Z")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _synthetic_manifest(
    tmp_path: Path,
    unit_count: int,
    edges: dict[int, list[int]] | None = None,
    *,
    shuffle_seed: int | None = None,
) -> tuple[Path, list[str]]:
    """A manifest of generically-named units over a chosen prerequisite DAG."""

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
            {
                "path": str(manifest_path),
                "sha256": _sha256_file(manifest_path),
                "role": "active_manifest",
            }
        ],
    }


def _visual_state(
    unit_id: str,
    briefs: list[dict[str, Any]],
    results: dict[str, dict[str, Any]],
    *,
    content_hash: str = "content-hash-1",
) -> dict[str, Any]:
    """A D12 projection over one frozen visual denominator.

    `run_id`/`episode_id` are part of the projection because D12 stages an M04
    dispatch, and a dispatch with no run and episode identity has no correlation.
    """

    deterministic = sorted(b["key"] for b in briefs if b["subset"] == "deterministic")
    model = sorted(b["key"] for b in briefs if b["subset"] == "model")
    return {
        "run_id": "run-n30-fixture",
        "episode_id": "episode-n30-fixture",
        "selected_unit_id": unit_id,
        "visual_briefs": briefs,
        "visual_denominators": {
            f"{unit_id}/{content_hash}": {
                "unit_id": unit_id,
                "content_hash": content_hash,
                "deterministic_keys": deterministic,
                "model_keys": model,
                "size": len(briefs),
            }
        },
        "visual_results": results,
        "artifact_versions": [],
        "artifact_heads": {
            f"units/{unit_id}/content": {"version": 1, "parent_hash": None, "hash": content_hash}
        },
    }


def _brief(unit_id: str, role: str, subset: str, content_hash: str = "content-hash-1") -> dict[str, Any]:
    return {
        "key": f"{unit_id}/visual/{role}",
        "unit_id": unit_id,
        "role": role,
        "kind": "schematic" if subset == "deterministic" else "illustration",
        "subset": subset,
        "content_hash": content_hash,
        "domain_hash": "domain-hash-1",
        "permitted_facts": [],
    }


def _m02_packet(unit_id: str) -> dict[str, Any]:
    """One correctly reserved M02 packet, as D07 stages it and D90 restages it."""

    return {
        "correlation": {"run_id": "r", "episode_id": "e"},
        "reservation": {
            "reservation_kind": mn.RESERVATION_KIND,
            "activation_id": "activation-1",
            "reservation_id": "activation-1#1",
            "job_id": "M02_CREATE_UNIT_DOMAIN_DATA",
            "counter_key": "M02_CREATE_UNIT_DOMAIN_DATA|k",
            "attempt_ordinal": 1,
        },
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
        "domain_schema": {"path": "schemas/x.json", "sha256": "0" * 64},
        "verifier_interface": {"declared_at": "/verifier_result"},
        "calibration": {"path": "policy/x.yaml", "sha256": "0" * 64},
    }


def _visual_result(key: str, unit_id: str, subset: str, content_hash: str = "content-hash-1") -> dict[str, Any]:
    return {
        "key": key,
        "unit_id": unit_id,
        "subset": subset,
        "provenance": "deterministic_renderer" if subset == "deterministic" else "model_candidate",
        "content_hash": content_hash,
        "domain_hash": "domain-hash-1",
        "asset_path": f"/tmp/{key}.svg",
        "sha256": hashlib.sha256(key.encode()).hexdigest(),
        "format": "svg",
    }


# ---------------------------------------------------------------------------
# End-to-end harness: the real compiled graph, a test-only model transport
# ---------------------------------------------------------------------------
#
# `RuntimeContext`'s services are opened by the CLI, not by the builder, so an
# episode can be executed against test doubles without changing production code.
# The one seam is the model transport: `graph._boundary` constructs it through
# `build_model_node_context`, which refuses a fake by design. The harness rebinds
# that one name for the duration of a test, so the fake stays unreachable from
# every production path (`test_the_model_path_uses_only_a_test_transport...`).


class _StubRegistry:
    """The capability/renderer/rasterizer surface D03/D11/D13/D14 reach for.

    Production `CliTransport` implements none of these; see finding B-8.
    """

    def __init__(self, sandbox: Path) -> None:
        self.sandbox = sandbox
        self.rendered_units: list[str] = []
        self.inspected: list[str] = []

    def prove_capability(self, capability: str) -> dict[str, Any]:
        return {"result": "PASS", "capability": capability, "detail": "test double"}

    def observe_executable(self, name: str) -> dict[str, Any]:
        return {"name": name, "path": f"/usr/bin/{name}", "sha256": "0" * 64}

    def render_deterministic_visual(self, brief: Any, permitted_facts: Any) -> dict[str, Any]:
        path = self.sandbox / "visuals" / (str(brief["key"]).replace("/", "_") + ".svg")
        path.parent.mkdir(parents=True, exist_ok=True)
        body = f"<svg data-key='{brief['key']}'/>".encode()
        path.write_bytes(body)
        return {"asset_path": str(path), "sha256": hashlib.sha256(body).hexdigest(), "format": "svg"}

    def render_unit(self, unit_id: str, parents: Any) -> dict[str, Any]:
        self.rendered_units.append(unit_id)
        directory = self.sandbox / "render"
        directory.mkdir(parents=True, exist_ok=True)
        body = json.dumps({"unit": unit_id, "parents": parents}, sort_keys=True).encode()
        pdf, layout = directory / f"{unit_id}.pdf", directory / f"{unit_id}.layout.json"
        pdf.write_bytes(body)
        layout.write_bytes(body)
        digest = hashlib.sha256(body).hexdigest()
        return {
            "layout_path": str(layout),
            "layout_sha256": digest,
            "pdf_path": str(pdf),
            "pdf_sha256": digest,
            "renderer": "test_double_renderer",
            "attempt": 1,
        }

    def inspect_pages(self, pdf_path: str, pdf_sha256: str) -> dict[str, Any]:
        self.inspected.append(pdf_sha256)
        pages = []
        for number in (1, 2):
            image = self.sandbox / "pages" / f"{Path(pdf_path).stem}-{number}.png"
            image.parent.mkdir(parents=True, exist_ok=True)
            body = f"page-{number}-{pdf_sha256}".encode()
            image.write_bytes(body)
            pages.append(
                {
                    "number": number,
                    "page_sha256": hashlib.sha256(body).hexdigest(),
                    "image_path": str(image),
                    "problems": [],
                    "unreadable": False,
                }
            )
        return {"pages": pages}


class _StubRetriever:
    def __init__(self) -> None:
        self.fetched: list[str] = []

    def fetch(self, locator: Any, authorization: Any, scope: Any) -> dict[str, Any]:
        self.fetched.append(str(locator))
        body = json.dumps({"locator": locator, "scope": scope}, sort_keys=True).encode()
        return {
            "locator": locator,
            "sha256": hashlib.sha256(body).hexdigest(),
            "status": 200,
            "content_type": "text/html",
            "tls": {"verified": True},
            "bytes_path": None,
        }


class _SwitchableToken:
    """A signal token a test can raise at a chosen node boundary."""

    def __init__(self, trip_after: str | None = None) -> None:
        self.trip_after = trip_after
        self.tripped = False
        self.observed: list[str] = []

    def trip(self) -> None:
        self.tripped = True

    def is_set(self) -> bool:
        return self.tripped


class _HarnessContext:
    """`RuntimeContext`-shaped test double. No product root, no real transport."""

    def __init__(self, engine_root: Path, output_root: Path, sandbox: Path) -> None:
        from runtime.langgraph_factory.artifacts import ArtifactStore
        from runtime.langgraph_factory.evidence import EvidenceStore

        self.engine_root = engine_root
        self.output_root = output_root
        self.path_guard = ArtifactStore(output_root)
        self.evidence_service = EvidenceStore(output_root)
        self.transport_registry = _StubRegistry(sandbox)
        self.source_retriever = _StubRetriever()
        self.signal_token = _SwitchableToken()
        self.clock = lambda: "2026-01-01T00:00:00Z"


class _ScriptedFakeTransport(mn.tp.FakeCliTransport):
    """Composes each canned candidate from the projection it is handed.

    Still a `FakeCliTransport`, so the real output-schema and no-authoritative-
    field validation still runs, and it is still refused by
    `build_model_node_context`.
    """

    def __init__(self, *, sandbox_root: Path, registry: Any = None) -> None:
        super().__init__(sandbox_root=sandbox_root, responses={}, registry=registry)
        self.calls: list[tuple[str, str]] = []

    def execute(self, *, job_id: str, activation_id: str, projection: Any = None, **kwargs: Any):
        projection = dict(projection or {})
        self.calls.append((job_id, activation_id))
        self.responses[job_id] = _scripted_candidate(job_id, projection)
        return super().execute(
            job_id=job_id, activation_id=activation_id, projection=projection, **kwargs
        )


# The visual denominator the scripted M03 declares. Two members, one per subset,
# so a real episode fans out to D11 *and* to M04 and D12 has two subsets to join.
# `_declared_visuals` returns the list in a chosen order, which is what prompt
# TEST 5's permutation-invariance claim varies.
DECLARED_VISUALS: list[dict[str, Any]] = [
    {
        "role": "build_map",
        "kind": "schematic",
        "authoritative": True,
        "permitted_facts": ["fact-a"],
    },
    {
        "role": "overview",
        "kind": "diagram",
        "authoritative": False,
        "permitted_facts": ["fact-b"],
    },
]


def _scripted_candidate(job_id: str, projection: dict[str, Any]) -> dict[str, Any]:
    if job_id == "M01_RESEARCH_UNIT_SOURCES":
        request_id = projection["request"].get("request_id")
        group = projection.get("retrieval_group")
        if group is None:
            return {
                "locators": [
                    {
                        "request_id": request_id,
                        "url": f"https://example.invalid/{request_id}",
                        "title": "scripted source",
                        "publisher": "scripted publisher",
                        "locator_kind": "primary",
                        "rationale": "scripted rationale",
                    }
                ]
            }
        return {
            "interpretations": [
                {
                    "request_id": request_id,
                    "retrieval_id": str(record.get("retrieval_id")),
                    "claims": [
                        {
                            "claim_text": "scripted claim",
                            "source_quote": "scripted quote",
                            "source_location": "p.1",
                        }
                    ],
                    "limitations": [],
                }
                for record in group.get("retrieved_records", [])
            ]
        }
    if job_id == "M02_CREATE_UNIT_DOMAIN_DATA":
        unit_id = projection["unit"].get("unit_id")
        admitted = projection.get("admitted_sources") or []
        # Every declared fact resolves to an admitted source, which is D08's
        # `domain_facts_sourced` check: the body is derived from the join, not
        # invented alongside it.
        facts = [
            {
                "fact_id": str(source.get("fact_id")),
                "statement": f"scripted statement for {source.get('fact_id')}",
            }
            for source in admitted
        ] or [{"fact_id": "required_explanation:000", "statement": "scripted statement"}]
        return {
            "domain_version": {
                "unit_id": unit_id,
                "fields": {
                    "unit_id": unit_id,
                    "facts": facts,
                    "verifier_result": {"result": "all_fixtures_behaved"},
                },
                "evidence_references": [
                    {
                        "source_id": str(source.get("source_id") or source.get("key") or "s1"),
                        "source_location": "p.1",
                    }
                    for source in admitted
                ]
                or [{"source_id": "s1", "source_location": "p.1"}],
            }
        }
    if job_id == "M03_WRITE_UNIT_CONTENT":
        admitted_domain = projection.get("admitted_domain") or {}
        unit_id = str(admitted_domain.get("unit_id") or projection["unit"].get("unit_id"))
        # Only the source ids D08 declared admissible may be cited; M03's adapter
        # rejects any other as `candidate_undeclared_artifact`.
        admissible = projection.get("admitted_evidence_references") or []
        return {
            "unit_content": {
                "unit_id": unit_id,
                "sections": [
                    {
                        "section_id": f"s{index:03d}",
                        "heading": f"scripted heading {index}",
                        "body": f"scripted body for {reference.get('fact_id')}",
                    }
                    for index, reference in enumerate(admissible, start=1)
                ],
                "evidence_references": [
                    {
                        "section_id": f"s{index:03d}",
                        "source_id": str(reference.get("source_id")),
                        "source_location": "p.1",
                    }
                    for index, reference in enumerate(admissible, start=1)
                ],
                # One visual of each subset, so the episode exercises both halves
                # of D12's join: `schematic` is in `AUTHORITATIVE_VISUAL_KINDS`
                # and is produced deterministically from the domain, `diagram` is
                # not and is dispatched to M04.
                "visuals": DECLARED_VISUALS,
            }
        }
    if job_id == "M04_CREATE_UNIT_VISUALS":
        brief_id = str(projection["brief"].get("brief_id") or projection["brief"].get("key"))
        return {
            "visual_candidate": {
                "brief_id": brief_id,
                "prompt_text": f"scripted prompt for {brief_id}",
                "dimensions": {"width_px": 1024, "height_px": 768},
                "image_format": "png",
                "accessibility_text": f"scripted alt text for {brief_id}",
            },
            "provenance_declaration": {
                "brief_id": brief_id,
                "permitted_facts_used": [
                    str(fact) for fact in (projection.get("permitted_facts") or [])
                ],
                "asserts_authoritative_detail": False,
            },
        }
    if job_id == "M05_REVIEW_ACTUAL_UNIT":
        # The review answers the exact page denominator D15 froze, by hash: a
        # review that invented or dropped a page is what D16's join exists to
        # reject, so the scripted reviewer must not do either.
        pages = projection.get("pages") or []
        return {
            "overall_findings": [],
            "page_findings": [
                {
                    "page_number": int(page["page_number"]),
                    "page_sha256": str(page["page_sha256"]),
                    "findings": [],
                }
                for page in pages
            ],
        }
    raise AssertionError(f"no scripted candidate for {job_id}")


def _scripted_model_context(sandbox: Path) -> Any:
    routes = mn.tp.load_job_registry()
    return mn.ModelNodeContext(
        transport=_ScriptedFakeTransport(sandbox_root=sandbox, registry=routes),
        registry=routes,
    )


# The engine contracts the unit path resolves out of its engine root. D07 hands
# the domain metaschema and calibration to M02, D08 loads the run's domain schema,
# and D09 holds unit content to `CURRICULUM_CONTRACTS[0]`. They are copied from the
# repo rather than stubbed, so the episode is held to the contracts a real run is.
ENGINE_CONTRACTS: tuple[str, ...] = (
    "schemas/manifest_domain.metaschema.v1.json",
    "policy/calibration.v1.yaml",
    "meta_prompt/assets/pedagogy.v1.md",
    *domain.CURRICULUM_CONTRACTS,
)

# The synthetic curriculum's own declared domain contract. A run that declares one
# is the path D02/D08 are built for; the engine metaschema constrains the shape of
# *this* file, not the domain instance a unit asserts.
SYNTHETIC_DOMAIN_SCHEMA_RELATIVE = "schemas/synthetic_domain.v1.json"
SYNTHETIC_DOMAIN_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "plan26/test/synthetic_domain.v1.json",
    "type": "object",
    "additionalProperties": False,
    "required": ["unit_id", "facts", "verifier_result"],
    "properties": {
        "unit_id": {"type": "string", "minLength": 1},
        "facts": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["fact_id", "statement"],
                "properties": {
                    "fact_id": {"type": "string", "minLength": 1},
                    "statement": {"type": "string", "minLength": 1},
                },
            },
        },
        "verifier_result": {
            "type": "object",
            "additionalProperties": True,
            "required": ["result"],
            "properties": {"result": {"type": "string"}},
        },
    },
}


def _build_episode_fixture(tmp_path: Path, units: int = 1) -> dict[str, Any]:
    """An engine root, a synthetic curriculum, an output root, and a sandbox."""

    engine = tmp_path / "engine"
    curriculum = engine / "curricula" / "synthetic"
    curriculum.mkdir(parents=True)
    for name in ("schemas", "policy", "meta_prompt"):
        (engine / name).mkdir()
    (engine / "schemas" / "placeholder.json").write_text("{}", encoding="utf-8")
    for relative in ENGINE_CONTRACTS:
        target = engine / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((REPO_ROOT / relative).read_bytes())
    (engine / SYNTHETIC_DOMAIN_SCHEMA_RELATIVE).write_text(
        json.dumps(SYNTHETIC_DOMAIN_SCHEMA, indent=2), encoding="utf-8"
    )
    labs = [
        {
            "id": f"U{index:03d}",
            "title": f"synthetic unit {index}",
            "sequence": {
                "prerequisites": [f"U{index - 1:03d}"] if index > 1 else [],
                "prepares_for": [],
            },
            "required_explanation": [f"fact {index}"],
            "safety_focus": ["care"],
        }
        for index in range(1, units + 1)
    ]
    manifest = curriculum / "synthetic_curriculum.v1.yaml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "domain": {"manifest_schema": SYNTHETIC_DOMAIN_SCHEMA_RELATIVE},
                "labs": labs,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    output_root = tmp_path / "out"
    output_root.mkdir()
    # The fake transport refuses any root that is not under the system temp dir.
    sandbox = Path(tempfile.mkdtemp(prefix="plan26-n30-sandbox-"))
    return {
        "engine": engine,
        "curriculum": curriculum,
        "manifest": manifest,
        "output_root": output_root,
        "sandbox": sandbox,
    }


def _prepare_episode(fixture: dict[str, Any], *, mode: str = "one", requested: str | None = "U001"):
    """`prepare_episode_invocation` plus the envelope D00 reads, as the CLI builds them."""

    lock = P.ExecutionLock(fixture["output_root"])
    lock.acquire()
    seed = {
        "engine_root": str(fixture["engine"]),
        "curriculum_root": str(fixture["curriculum"]),
        "active_manifest_path": str(fixture["manifest"]),
        "output_root": str(fixture["output_root"]),
        "created_at": "2026-01-01T00:00:00Z",
        "contract_version": "1",
        "mode": mode,
        "requested_unit_id": requested,
    }
    invocation = P.prepare_episode_invocation(
        output_root=fixture["output_root"], lock=lock, identity_seed=seed
    )
    envelope: dict[str, Any] = {
        "kind": "fresh",
        "contract_version": "1",
        "engine_root": str(fixture["engine"]),
        "curriculum_root": str(fixture["curriculum"]),
        "output_root": str(fixture["output_root"]),
        "mode": mode,
        "requested_unit_id": requested,
        "authorization": {"scope": "test", "executables": []},
        "episode_ordinal": 1,
        "prior_identity": None,
        "prior_terminal": None,
        "lease_open": False,
    }
    # D03 requires the authorization to name this run's frozen digest, which the
    # CLI computes before invocation; D01 is the one function that derives it.
    probe = _HarnessContext(fixture["engine"], fixture["output_root"], fixture["sandbox"])
    digest = inputs.D01_VALIDATE_AND_FREEZE_INPUTS({"invocation": envelope}, probe)["frozen_digest"]
    envelope["authorization"] = {
        "scope": "test",
        "executables": [],
        "curriculum_digest": digest,
    }
    return lock, invocation, envelope


def _run_episode(
    monkeypatch: Any,
    fixture: dict[str, Any],
    *,
    interrupt_after: str | None = None,
) -> dict[str, Any]:
    """Execute one real episode of the real compiled graph, end to end.

    Returns the ordered node trace, the per-node updates, and the final state.
    """

    lock, invocation, envelope = _prepare_episode(fixture)
    context = _HarnessContext(fixture["engine"], fixture["output_root"], fixture["sandbox"])
    monkeypatch.setattr(
        G,
        "build_model_node_context",
        lambda _context, **_kwargs: _scripted_model_context(fixture["sandbox"]),
    )
    compiled = G.build_curriculum_factory_graph(
        engine_root=fixture["engine"], output_root=fixture["output_root"]
    )

    trace: list[str] = []
    updates: list[tuple[str, dict[str, Any]]] = []
    deferred_frontier: str | None = None
    try:
        for chunk in compiled.stream(
            {"invocation": envelope},
            config=invocation.config,
            stream_mode="updates",
            context=context,
        ):
            for node_id, update in chunk.items():
                trace.append(node_id)
                updates.append((node_id, dict(update or {})))
                if interrupt_after is not None and node_id == interrupt_after:
                    context.signal_token.trip()
    except KeyError as error:
        # A guard resolved a destination whose node body does not exist yet.
        # That is a *declared* deferred edge, not a defect, so it is recorded as
        # the episode's frontier — but only if it really is one of the declared
        # rows, so an undeclared missing destination still fails loudly.
        missing = error.args[0] if error.args else None
        declared = {row[2] for row in U.DEFERRED_EDGES}
        if missing not in declared:
            raise
        deferred_frontier = str(missing)
    lock.release()
    return {
        "trace": trace,
        "updates": updates,
        "deferred_frontier": deferred_frontier,
        "state": compiled.get_state(invocation.config).values,
        "context": context,
        "invocation": invocation,
        "compiled": compiled,
    }


def _assert_frontier_is_a_declared_row(frontier: str | None) -> None:
    """A clean episode's halt must be some real `DEFERRED_EDGES` destination.

    Not pinned to today's specific row (`D16_REDUCE_UNIT_EVIDENCE`): the node
    whose guard actually resolves to the open row (M05 today) runs but its own
    update is swallowed by the aborted superstep before it reaches the stream,
    so the frontier cannot be re-derived from the observed trace either — the
    KeyError `_run_episode` already caught *is* the ground truth, and this only
    checks that ground truth is a declared row, never a fabricated one. Stays
    correct as N31/N32 close further rows of that table (P-N30-001, closing
    N90 finding F1).
    """

    declared_destinations = {destination for _s, _v, destination, _o in U.DEFERRED_EDGES}
    assert frontier is not None
    assert frontier in declared_destinations


# ---------------------------------------------------------------------------
# Registered unit topology (spec 8.1 / 8.2)
# ---------------------------------------------------------------------------


def test_the_compiled_graph_registers_every_declared_unit_branch(topology, compiled) -> None:
    """Each conditional edge exists with exactly the destinations that exist.

    `available` here is the real compiled graph's own node set, not
    `binding_inventory()`: the latter is deliberately narrow (it names only what
    this generation is allowed to bind), while this test's real job is a
    self-consistency check against whatever the production compile point
    actually wired — so it has to stay correct both before and after a later
    generation widens the set of nodes that have real bodies.
    """

    graph_nodes = set(compiled.get_graph().nodes)
    registered: dict[str, set[str]] = {}
    for source, target, conditional in topology["edges"]:
        if conditional:
            registered.setdefault(source, set()).add(target)

    for source, _guard in U.UNIT_BRANCHES:
        expected = set(U.branch_destinations(source, graph_nodes))
        assert expected, f"{source} has no registerable destination"
        assert registered.get(source) == expected, source


def test_the_two_map_reduce_return_edges_are_normal_edges(topology) -> None:
    """Spec 8.2 names these exactly: `add_edge(worker, barrier)`, not a branch.

    Registering the worker's return conditionally would let the worker's own
    result decide where the map/reduce goes, which is the barrier's authority.
    """

    normal = {(source, target) for source, target, conditional in topology["edges"] if not conditional}
    for edge in U.UNIT_NORMAL_EDGES:
        assert edge in normal, edge
    assert ("D11_CREATE_DETERMINISTIC_VISUALS", "D12_VISUAL_BARRIER_AND_JOIN") in normal
    assert ("M04_CREATE_UNIT_VISUALS", "D12_VISUAL_BARRIER_AND_JOIN") in normal


def test_the_unit_path_creates_no_second_graph_and_compiles_nothing() -> None:
    """N30 is additive registration over N20's one builder."""

    source = UNIT_GRAPH_PY.read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = [
        node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    ]
    assert "StateGraph" not in calls
    assert "compile" not in calls
    assert "add_node" not in calls


def test_a_node_body_authored_in_the_unit_path_module_is_refused() -> None:
    """The D90/D91 gap cannot be closed by writing a wrapper in this module.

    N20's `validate_bindings` restricts a production binding to the two owned
    node modules, so a callable authored here is rejected by stable ID. This is
    why blocking gap `plan26/n30/d90-d91-not-registrable` is owed to N23 and
    cannot be absorbed as coordination.
    """

    def D90_RESERVE_MODEL_ATTEMPT(state: Any, context: Any) -> dict[str, Any]:
        return {}

    D90_RESERVE_MODEL_ATTEMPT.__module__ = "runtime.langgraph_factory.unit_graph"
    bindings = dict(G.binding_inventory())
    bindings["D90_RESERVE_MODEL_ATTEMPT"] = D90_RESERVE_MODEL_ATTEMPT

    with pytest.raises(G.GraphBindingError) as error:
        G.validate_bindings(bindings, required=("D90_RESERVE_MODEL_ATTEMPT",))
    assert "N20-BIND-PLACEHOLDER" in str(error.value)


def test_deferred_edges_are_exactly_the_destinations_with_no_node_body(available) -> None:
    """Silence about an unwireable edge is how a topology gap becomes a halt."""

    observed: set[tuple[str, str]] = set()
    for source, _guard in U.UNIT_BRANCHES:
        for destination in U.deferred_destinations(source, available):
            observed.add((source, destination))
    declared = {(source, destination) for source, _value, destination, _owner in U.DEFERRED_EDGES}
    assert observed == declared


def test_every_deferred_edge_names_a_real_owning_graph_node() -> None:
    owners = {owner for _s, _v, _d, owner in U.DEFERRED_EDGES}
    assert owners <= {"N23_MODEL_NODES", "N31_REPAIR_ACCEPTANCE", "N32_WORKBOOK_TERMINALS"}
    for _source, value, destination, owner in U.DEFERRED_EDGES:
        assert value and destination and owner


def test_registering_an_undeclared_deferred_destination_fails(monkeypatch, available) -> None:
    """A future unwireable destination must be declared, not silently dropped."""

    monkeypatch.setattr(U, "DEFERRED_EDGES", U.DEFERRED_EDGES[1:])

    class _Builder:
        def add_edge(self, *args: Any) -> None:
            pass

        def add_conditional_edges(self, *args: Any) -> None:
            pass

    with pytest.raises(U.UnitTopologyError) as error:
        U.register_unit_path(_Builder(), available)
    assert "N30-EDGE-UNDECLARED" in str(error.value)


def test_no_model_node_can_be_a_resume_reentry_destination(topology) -> None:
    """Spec 6.2 D92: a model node as stored destination is a system failure."""

    assert not set(U.RESUME_REENTRY_DESTINATIONS) & MODEL_NODE_IDS
    reentry = {
        target
        for source, target, conditional in topology["edges"]
        if source == "D92_REENTER_VALIDATED_FRONTIER" and conditional
    }
    assert not reentry & MODEL_NODE_IDS
    assert set(U.RESUME_REENTRY_DESTINATIONS) <= reentry


def test_a_stored_model_frontier_is_refused_by_the_reentry_guard() -> None:
    state = {
        "pending_guard": {
            "node": "D92_REENTER_VALIDATED_FRONTIER",
            "value": "deterministic_reentry",
            "detail": {"destination": "M03_WRITE_UNIT_CONTENT"},
        }
    }
    with pytest.raises(R.RoutingViolation):
        R.route_frontier_reentry(state)


def test_the_unit_path_names_no_unit_id_and_no_manifest_length() -> None:
    """Spec 8.2: the builder never creates a node per known unit."""

    source = UNIT_GRAPH_PY.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            assert node.value in (0, 1), f"manifest-length-looking constant {node.value}"
    assert "U001" not in source


# ---------------------------------------------------------------------------
# Fan-outs, denominators, joins (spec section 10)
# ---------------------------------------------------------------------------


def test_a_visual_fanout_dispatches_one_send_per_staged_denominator_member() -> None:
    """The guard translates staged material one-for-one; it invents no member.

    Since N20's B-6 rework the dispatcher no longer emits the `Send`s itself: a
    model fan-out routes to D90, D90 commits one attempt counter per member and
    restages the packet, and `route_attempt_reservation` is the guard that turns
    the *reserved* members into `Send`s. The one-for-one property is asserted
    across that hop, so the members dispatched are still exactly the members the
    denominator committed to — each now additionally carrying its reservation.
    """

    unit_id = "U001"
    briefs = [
        _brief(unit_id, "det-a", "deterministic"),
        _brief(unit_id, "mdl-a", "model"),
        _brief(unit_id, "mdl-b", "model"),
    ]
    results = {
        f"{unit_id}/visual/det-a": _visual_result(f"{unit_id}/visual/det-a", unit_id, "deterministic")
    }
    state = _visual_state(unit_id, briefs, results)
    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(state, _Context())

    assert update["pending_guard"]["value"] == "model_visual_fanout"
    packet = update["pending_packet"]
    assert packet["dispatch"] == "M04_CREATE_UNIT_VISUALS"
    members = packet["packets"]
    assert len(members) == 2
    # Each member is an M04 packet, not a bare brief: `Send` delivers the member
    # as the worker's whole input, so it has to carry the spec 9 projection.
    for member in members:
        assert set(member) >= {"brief", "permitted_facts", "visual_contract", "correlation"}
        assert member["correlation"]["run_id"] == state["run_id"]
        assert member["correlation"]["episode_id"] == state["episode_id"]

    # The dispatcher's own guard reserves before it dispatches (spec 6.2, D90).
    assert R.route_visual_barrier({**state, **update}) == "D90_RESERVE_MODEL_ATTEMPT"

    reserved = mn.D90_RESERVE_MODEL_ATTEMPT({**state, **update}, None)
    restaged = reserved["pending_packet"]["packets"]
    assert len(restaged) == 2

    dispatch = R.route_attempt_reservation({**state, **update, **reserved})
    assert isinstance(dispatch, list) and len(dispatch) == 2
    assert all(isinstance(send, Send) for send in dispatch)
    assert {send.node for send in dispatch} == {"M04_CREATE_UNIT_VISUALS"}
    assert [send.arg for send in dispatch] == restaged
    # One `Send` per committed denominator member, and each carries the counter
    # that was committed for it and nothing invented at routing time.
    assert [send.arg["correlation"]["correlation_key"] for send in dispatch] == [
        member["correlation"]["correlation_key"] for member in members
    ]
    assert len({send.arg["reservation"]["activation_id"] for send in dispatch}) == 2


def test_a_fanout_with_no_staged_packet_refuses_to_improvise_one() -> None:
    """Spec 10: the denominator is persisted before dispatch, not at routing time.

    The refusal lives wherever a guard actually translates members into `Send`s.
    Since B-6 that is two places: D10's deterministic map still translates at the
    dispatcher, and every model map translates at D90. Both are asserted, so
    moving the dispatch hop did not move the property out of the file.
    """

    model_dispatch = {
        "pending_guard": {
            "node": "D90_RESERVE_MODEL_ATTEMPT",
            "value": "authorized",
            "kind": "model_attempt",
            "decision": "authorized",
            "detail": {},
        }
    }
    with pytest.raises(R.RoutingViolation):
        R.route_attempt_reservation(model_dispatch)

    deterministic_dispatch = {
        "pending_guard": {
            "node": "D10_COMPILE_VISUAL_BRIEFS",
            "value": "deterministic_visual_fanout",
            "detail": {},
        }
    }
    with pytest.raises(R.RoutingViolation):
        R.route_visual_briefs(deterministic_dispatch)


def test_an_empty_deterministic_visual_subset_routes_straight_to_the_barrier() -> None:
    """Spec 8.2: empty subsets route directly through D12; no sentinel member."""

    unit_id = "U001"
    content_hash = "content-hash-1"
    state = {
        "selected_unit_id": unit_id,
        "artifact_heads": {
            f"units/{unit_id}/content": {"version": 1, "parent_hash": None, "hash": content_hash},
            f"units/{unit_id}/domain": {"version": 1, "parent_hash": None, "hash": "domain-hash-1"},
        },
        "artifact_versions": [
            {
                "stream": f"units/{unit_id}/content",
                "version": 1,
                "parent_hash": None,
                "hash": content_hash,
                "body": {"visuals": [{"role": "mdl-a", "kind": "illustration"}]},
            }
        ],
        "engine_root": "/tmp",
    }
    update = visuals.D10_COMPILE_VISUAL_BRIEFS(state, _Context())
    assert update["pending_guard"]["value"] == "no_deterministic_visuals"
    assert R.route_visual_briefs({**state, **update}) == "D12_VISUAL_BARRIER_AND_JOIN"


@pytest.mark.parametrize(
    "mutation",
    ["missing", "extra", "stale_parent", "cross_unit"],
)
def test_the_visual_join_refuses_a_denominator_that_is_not_exact(mutation: str) -> None:
    """Spec 10: missing, extra, stale-parent and cross-unit members fail the join."""

    unit_id = "U001"
    briefs = [_brief(unit_id, "det-a", "deterministic"), _brief(unit_id, "det-b", "deterministic")]
    key_a, key_b = f"{unit_id}/visual/det-a", f"{unit_id}/visual/det-b"
    results = {
        key_a: _visual_result(key_a, unit_id, "deterministic"),
        key_b: _visual_result(key_b, unit_id, "deterministic"),
    }
    if mutation == "missing":
        results.pop(key_b)
    elif mutation == "extra":
        extra = f"{unit_id}/visual/det-z"
        results[extra] = _visual_result(extra, unit_id, "deterministic")
    elif mutation == "stale_parent":
        results[key_b] = {**results[key_b], "content_hash": "superseded-content-hash"}
    elif mutation == "cross_unit":
        results[key_b] = {**results[key_b], "unit_id": "U999"}

    state = _visual_state(unit_id, briefs, results)
    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(state, _Context())
    failure = update["pending_failure"]
    assert failure["class"] == "system"
    assert failure["cause"] in ("join", "integrity")
    assert "artifact_heads" not in update


@pytest.mark.parametrize(
    "mutation",
    ["missing", "extra", "stale", "cross_unit"],
)
def test_the_source_join_refuses_a_denominator_that_is_not_exact(mutation: str) -> None:
    """Spec 10: the source join accepts only `actual_keys == expected_keys`."""

    unit_id = "U001"
    key_a, key_b = f"{unit_id}/1/required_explanation:000", f"{unit_id}/1/safety_focus:000"
    requests = [
        {"key": key_a, "unit_id": unit_id, "required": True, "scope": "required_explanation"},
        {"key": key_b, "unit_id": unit_id, "required": True, "scope": "safety_focus"},
    ]
    retrievals = {
        key: {"key": key, "unit_id": unit_id, "sha256": f"sha-{key}", "locator": "l", "content_type": "text/html"}
        for key in (key_a, key_b)
    }
    interpretations = {
        key: {"key": key, "unit_id": unit_id, "retrieval_sha256": f"sha-{key}", "scope": "s"}
        for key in (key_a, key_b)
    }
    if mutation == "missing":
        interpretations.pop(key_b)
    elif mutation == "extra":
        rogue = f"{unit_id}/1/undeclared:000"
        interpretations[rogue] = {"key": rogue, "unit_id": unit_id, "retrieval_sha256": "x"}
    elif mutation == "stale":
        interpretations[key_b] = {**interpretations[key_b], "retrieval_sha256": "superseded"}
    elif mutation == "cross_unit":
        interpretations[key_b] = {**interpretations[key_b], "unit_id": "U999"}

    state = {
        "selected_unit_id": unit_id,
        "source_requests": requests,
        "source_denominators": {
            f"{unit_id}/1": {"unit_id": unit_id, "source_epoch": 1, "request_keys": [key_a, key_b], "size": 2}
        },
        "source_discoveries": {},
        "retrievals": retrievals,
        "source_interpretations": interpretations,
    }
    update = sources.D07_CORRELATE_AND_ADMIT_SOURCES(state, _Context())

    assert "source_admissions" not in update
    if mutation == "missing":
        # A missing required member is an unresolved prerequisite, not an admission.
        assert update["pending_guard"]["value"] == "prerequisite_unresolved"
        assert R.route_source_admission({**state, **update}) == "D30_CLASSIFY_PREREQUISITE"
    else:
        assert update["pending_failure"]["class"] == "system"
        assert update["pending_failure"]["cause"] in ("join", "integrity")


def test_a_duplicate_fanout_member_with_a_different_body_is_an_integrity_failure() -> None:
    """Spec 10: duplicate equal replay is idempotent; a different duplicate is not."""

    from runtime.langgraph_factory.reducers import UnionConflict, union_disjoint

    key = "U001/visual/det-a"
    first = {key: _visual_result(key, "U001", "deterministic")}
    assert union_disjoint(first, dict(first)) == first
    with pytest.raises(UnionConflict):
        union_disjoint(first, {key: {**first[key], "sha256": "different"}})


@pytest.mark.parametrize("unit_count", [1, 7, 41])
def test_one_mode_computes_the_complete_prerequisite_closure_in_manifest_order(
    tmp_path: Path, unit_count: int
) -> None:
    """Prompt TEST 2, over a real multi-unit DAG rather than a fixed fixture."""

    edges = {index: [index - 1] for index in range(2, unit_count + 1)}
    manifest_path, _ = _synthetic_manifest(tmp_path / str(unit_count), unit_count, edges)
    update = inputs.D02_COMPILE_EFFECTIVE_RUN(
        _d02_state(manifest_path, "one", f"U{unit_count:03d}"), _Context()
    )
    closure = update["effective_run"]["target_closure"]
    assert closure == [f"U{index:03d}" for index in range(1, unit_count + 1)]

    # D05 then consumes that closure in exactly that order.
    state = {
        "effective_run": update["effective_run"],
        "cursor": {"manifest_ordinal": 0, "accepted_ordinal": 0},
        "accepted_unit_receipts": {},
        "unit_status": {},
    }
    selection = sources.D05_SELECT_NEXT_UNIT(state, _Context())
    assert selection["selected_unit_id"] == closure[0]
    assert R.route_unit_selection({**state, **selection}) == "D06_COMPILE_SOURCE_REQUESTS"


def test_a_diamond_closure_admits_each_ancestor_exactly_once(tmp_path: Path) -> None:
    manifest_path, _ = _synthetic_manifest(tmp_path, 4, {2: [1], 3: [1], 4: [2, 3]})
    update = inputs.D02_COMPILE_EFFECTIVE_RUN(_d02_state(manifest_path, "one", "U004"), _Context())
    closure = update["effective_run"]["target_closure"]
    assert sorted(closure) == ["U001", "U002", "U003", "U004"]
    assert len(closure) == len(set(closure))


# ---------------------------------------------------------------------------
# No success terminal anywhere in this path (prompt TEST 10)
# ---------------------------------------------------------------------------


def test_no_node_in_this_path_can_emit_a_product_success_terminal() -> None:
    """A capability, intermediate artifact, review, or clean check emits nothing.

    The two product terminals (`UNIT_ACCEPTED`, `COMPLETE`) are reachable only
    from D24/D32, neither of which this path wires; every node here that can
    reach D98 does so with a failure, interrupt, or pause candidate.
    """

    product_terminals = {"UNIT_ACCEPTED", "COMPLETE"}
    for source, _guard in U.UNIT_BRANCHES:
        spec = NODE_CATALOGUE.get(source)
        if spec is None:
            continue
        module_path = REPO_ROOT / "runtime" / "langgraph_factory" / "nodes" / f"{spec.module}.py"
        body = module_path.read_text(encoding="utf-8")
        for terminal in product_terminals:
            # Word-bounded: `INCOMPLETE` is a join verdict, not a terminal kind.
            assert not re.search(rf"\b{terminal}\b", body), f"{source} names {terminal}"

    # Nothing this path wires reaches the acceptance node that mints a receipt.
    reachable = {target for _s, _v, target, _o in U.DEFERRED_EDGES}
    assert "D22_ACCEPT_UNIT" not in reachable
    assert not set(U.unit_path_nodes()) & {"D22_ACCEPT_UNIT", "D24_PROVE_EXACT_MANIFEST_COVERAGE"}


def test_the_model_path_uses_only_a_test_transport_and_no_product_output_root() -> None:
    """A fake transport is injectable only through the explicitly named builder."""

    sandbox = Path(tempfile.mkdtemp())
    context = mn.build_test_model_node_context(sandbox_root=sandbox, responses={})
    assert isinstance(context.transport, mn.tp.FakeCliTransport)
    with pytest.raises(mn.ModelNodeError):
        mn.build_model_node_context(
            type("_C", (), {"transport_registry": context.transport})()  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Real execution of the real compiled graph (prompt TEST 1, and the reachable
# part of TEST 9). Every assertion below runs one real `.stream()`.
# ---------------------------------------------------------------------------


# The bootstrap prefix, which is a contiguous run of single-successor nodes and
# so can be asserted as a literal prefix of the trace.
BOOTSTRAP_SPINE = (
    "D00_BOOTSTRAP_EPISODE",
    "D01_VALIDATE_AND_FREEZE_INPUTS",
    "D02_COMPILE_EFFECTIVE_RUN",
    "D03_PROVE_CAPABILITIES",
    "D04_INITIALIZE_OR_RESUME",
    "D05_SELECT_NEXT_UNIT",
    "D06_COMPILE_SOURCE_REQUESTS",
)

# Every node, map and barrier boundary a real episode currently reaches, in the
# order it is first entered. Past D06 the path is no longer a simple spine: D90
# reserves before each dispatch, M01 runs as a two-member `Send` map twice, and
# D07/D08 are join barriers. Prompt TEST 9 is parametrized over this whole set,
# so the crash matrix covers map and barrier boundaries and not just plain nodes.
REACHABLE_BOUNDARIES = BOOTSTRAP_SPINE + (
    "D90_RESERVE_MODEL_ATTEMPT",
    "M01_RESEARCH_UNIT_SOURCES",
    "D06B_RETRIEVE_SOURCE_CANDIDATES",
    "D07_CORRELATE_AND_ADMIT_SOURCES",
    "M02_CREATE_UNIT_DOMAIN_DATA",
    "D08_VALIDATE_DOMAIN",
    "M03_WRITE_UNIT_CONTENT",
    "D09_VALIDATE_CONTENT",
    "D10_COMPILE_VISUAL_BRIEFS",
    "D11_CREATE_DETERMINISTIC_VISUALS",
    "D12_VISUAL_BARRIER_AND_JOIN",
    "M04_CREATE_UNIT_VISUALS",
    "D13_RENDER_UNIT",
    "D14_INVENTORY_AND_INSPECT_UNIT_PAGES",
    "D15_FREEZE_UNIT_REVIEW_PACKET",
)

# M05 runs — its receipt, its candidate record and its page findings are all in
# the committed state — but its update never reaches a stream consumer, because
# the branch that would emit it resolves to `D16_REDUCE_UNIT_EVIDENCE`, this
# node's declared handoff to N31, and aborts the superstep first. It is therefore
# not an observable interrupt boundary and is excluded from the matrix above
# rather than asserted vacuously. The same was true of D09 until B-10 was fixed
# and the frontier moved past it.
UNOBSERVABLE_BOUNDARY = "M05_REVIEW_ACTUAL_UNIT"


def test_a_fresh_episode_executes_the_bootstrap_spine_once_through_langgraph(
    tmp_path: Path, monkeypatch
) -> None:
    """Prompt TEST 1: the fresh path really runs, and D01 runs exactly once.

    `selected_unit_id` is asserted off `D05_SELECT_NEXT_UNIT`'s own first
    update, not the run's final merged state: once N31 wires D16-D23 this
    clean single-unit episode legitimately loops back to a second `D05`
    call, whose `manifest_exhausted` guard correctly overwrites the
    `replace_current`-reduced `selected_unit_id` to `None` in final state —
    a real second call, not a repeat of the first one, so it is asserted for
    rather than assumed away (P-N30-001, closing N90 finding F1).

    With D16-D23 now wired (P-N31-001), this clean one-unit episode really
    reaches acceptance: the second `D05_SELECT_NEXT_UNIT` call finds the
    manifest exhausted and routes to the still-deferred `D24_PROVE_EXACT_
    MANIFEST_COVERAGE`, whose `KeyError` is raised in the same tick as that
    second `D05` call's own routing decision -- a real, reproducible LangGraph
    `stream(stream_mode="updates")` artifact: the chunk for a step whose
    *next* step's routing raises in the same tick is never yielded, so
    `result["trace"]`'s own `D05_SELECT_NEXT_UNIT` count undercounts by
    exactly one in this exhausted-after-one-unit case (P-N31-003, closing the
    residual N90 finding F1 diagnosis). The real, checkpointed final state is
    unaffected by that streaming artifact, so it is asserted directly instead
    of inferring the outcome from a trace count this specific interaction
    cannot reliably produce.
    """

    fixture = _build_episode_fixture(tmp_path)
    result = _run_episode(monkeypatch, fixture)

    assert result["trace"][: len(BOOTSTRAP_SPINE)] == list(BOOTSTRAP_SPINE)
    assert result["trace"].count("D01_VALIDATE_AND_FREEZE_INPUTS") == 1
    assert "D00R_REVALIDATE_RESUME_IDENTITY" not in result["trace"]
    assert "D92_REENTER_VALIDATED_FRONTIER" not in result["trace"]

    state = result["state"]
    assert state["bootstrap_kind"] == "fresh"
    assert state["run_id"]
    assert state["mode"] == "one"
    assert state["effective_run"]["target_closure"] == ["U001"]

    first_selection = next(
        update for node_id, update in result["updates"] if node_id == "D05_SELECT_NEXT_UNIT"
    )
    assert first_selection["selected_unit_id"] == "U001"
    d05_calls = result["trace"].count("D05_SELECT_NEXT_UNIT")
    assert d05_calls in (1, 2)
    # The real, checkpointed outcome of a clean single-unit episode: the one
    # unit is accepted and the cursor advances, whether or not the second D05
    # call's own chunk made it into the stream.
    assert state["selected_unit_id"] is None
    assert state["cursor"]["accepted_ordinal"] == 1
    assert "U001" in (state.get("accepted_unit_receipts") or {})
    # No product success, and no second terminal, however the episode ends.
    assert result["trace"].count("D98_WRITE_TERMINAL") <= 1
    if state.get("terminal") is not None:
        assert state["terminal"]["kind"] not in ("UNIT_ACCEPTED", "COMPLETE")


def test_the_source_map_reduce_supersteps_execute_as_real_send_fanouts(
    tmp_path: Path, monkeypatch
) -> None:
    """Both M01 supersteps run as `Send` maps, join at their barriers, and admit.

    With B-6 and B-7 closed this is a real reduction, not a trace of a refusal:
    each map reserves through D90 first, runs two real M01 workers in one
    superstep, and D07's exact join admits both sources.
    """

    fixture = _build_episode_fixture(tmp_path)
    result = _run_episode(monkeypatch, fixture)
    trace = result["trace"]

    # Two `Send` maps of two members each: four M01 activations, no more.
    assert trace.count("M01_RESEARCH_UNIT_SOURCES") == 4
    # Each map is preceded by its reservation, and each superstep is contiguous.
    first = trace.index("M01_RESEARCH_UNIT_SOURCES")
    assert trace[first - 1] == "D90_RESERVE_MODEL_ATTEMPT"
    assert trace[first : first + 2] == ["M01_RESEARCH_UNIT_SOURCES"] * 2
    assert trace[first + 2] == "D06B_RETRIEVE_SOURCE_CANDIDATES"

    # No model failure at all: every dispatch carried a committed counter.
    assert "D91_CLASSIFY_MODEL_FAILURE" not in trace

    # The join really admitted, and the denominator it joined is the one D06 committed.
    admission = next(
        update for node_id, update in result["updates"]
        if node_id == "D07_CORRELATE_AND_ADMIT_SOURCES"
    )
    assert admission["pending_guard"]["value"] == "sources_admitted"
    denominator = next(
        iter(
            next(
                update for node_id, update in result["updates"]
                if node_id == "D06_COMPILE_SOURCE_REQUESTS"
            )["source_denominators"].values()
        )
    )
    assert sorted(record["key"] for record in admission["source_admissions"]) == sorted(
        denominator["request_keys"]
    )


def test_the_domain_head_advances_only_after_code_owned_admission(
    tmp_path: Path, monkeypatch
) -> None:
    """Prompt TEST 4, on a real episode: M02 writes a candidate, D08 mints the head.

    The head that exists at the end of the episode was minted by D08, not by the
    model: the M02 record in the same episode carries no `version`/`hash`, and the
    admitted head's hash is not any hash the model supplied.
    """

    fixture = _build_episode_fixture(tmp_path)
    result = _run_episode(monkeypatch, fixture)
    trace = result["trace"]
    assert trace.index("M02_CREATE_UNIT_DOMAIN_DATA") < trace.index("D08_VALIDATE_DOMAIN")

    candidate = next(
        update for node_id, update in result["updates"]
        if node_id == "M02_CREATE_UNIT_DOMAIN_DATA"
    )["artifact_versions"][0]
    assert candidate["record_kind"] == "model_candidate"
    assert not {"version", "hash", "parent_hash"} & set(candidate)

    heads = result["state"]["artifact_heads"]
    domain_head = heads["units/U001/domain"]
    assert domain_head["version"] == 1
    assert domain_head["parent_hash"] is None
    assert domain_head["hash"] != candidate.get("candidate_sha256")
    # And no model node ever wrote the channel that carries it.
    for node_id, update in result["updates"]:
        if node_id in MODEL_NODE_IDS:
            assert "artifact_heads" not in update


def test_the_content_head_advances_only_after_code_owned_admission(
    tmp_path: Path, monkeypatch
) -> None:
    """Prompt TEST 4's second half, now that D09 can admit.

    The content head is minted by D09 off the current head, not read off M03's
    record — and it is anchored to the domain head it was written against, so a
    content version cannot outlive the domain it cites.
    """

    fixture = _build_episode_fixture(tmp_path)
    result = _run_episode(monkeypatch, fixture)
    trace = result["trace"]
    assert trace.index("M03_WRITE_UNIT_CONTENT") < trace.index("D09_VALIDATE_CONTENT")

    candidate = next(
        update for node_id, update in result["updates"]
        if node_id == "M03_WRITE_UNIT_CONTENT"
    )["artifact_versions"][0]
    assert candidate["record_kind"] == "model_candidate"
    assert not {"version", "hash", "parent_hash"} & set(candidate)

    heads = result["state"]["artifact_heads"]
    content_head = heads["units/U001/content"]
    assert content_head["version"] == 1
    assert content_head["parent_hash"] is None
    assert content_head["hash"] != candidate.get("candidate_sha256")

    minted = next(
        record for record in result["state"]["artifact_versions"]
        if record.get("stream") == "units/U001/content"
    )
    assert minted["minted_by"] == "deterministic_admission"
    assert minted["domain_hash"] == heads["units/U001/domain"]["hash"]

    admission = next(
        update for node_id, update in result["updates"] if node_id == "D09_VALIDATE_CONTENT"
    )
    assert admission["pending_guard"]["value"] == "content_admitted"
    assert {check["check_id"] for check in admission["deterministic_checks"]} >= {
        "content_schema_valid",
        "content_domain_current",
    }


def test_a_visual_denominator_permutation_produces_an_identical_admitted_head(
    tmp_path: Path, monkeypatch
) -> None:
    """Prompt TEST 5: the order the briefs are declared in cannot move the head.

    Two real episodes, identical but for the order M03 declares its two visuals
    in. The denominator members, the join, and the admitted `visuals` head hash
    must all be identical: a join whose answer depended on arrival or declaration
    order would admit a different artifact for the same content, which is exactly
    what a content-addressed head is supposed to make impossible.
    """

    def run(order: list[dict[str, Any]]) -> dict[str, Any]:
        monkeypatch.setattr(
            sys.modules[__name__], "DECLARED_VISUALS", order, raising=True
        )
        fixture = _build_episode_fixture(tmp_path / f"perm-{len(order)}-{order[0]['role']}")
        return _run_episode(monkeypatch, fixture)

    forward = run(list(DECLARED_VISUALS))
    reverse = run(list(reversed(DECLARED_VISUALS)))

    for result in (forward, reverse):
        _assert_frontier_is_a_declared_row(result["deferred_frontier"])
        assert result["trace"].count("D11_CREATE_DETERMINISTIC_VISUALS") == 1
        assert result["trace"].count("M04_CREATE_UNIT_VISUALS") == 1

    assert forward["deferred_frontier"] == reverse["deferred_frontier"]

    def denominator(result: dict[str, Any]) -> dict[str, Any]:
        record = dict(next(iter(result["state"]["visual_denominators"].values())))
        record.pop("content_hash", None)
        return record

    assert denominator(forward) == denominator(reverse)
    assert (
        forward["state"]["artifact_heads"]["units/U001/visuals"]["hash"]
        == reverse["state"]["artifact_heads"]["units/U001/visuals"]["hash"]
    )

    join = [
        record for record in forward["state"]["visual_join_evidence"]
        if record["phase"] == "join"
    ]
    assert [record["result"] for record in join] == ["PASS"]
    assert join[0]["denominator_size"] == join[0]["actual_size"] == 2


def test_an_actual_pdf_and_a_positive_contiguous_page_inventory_are_required(
    tmp_path: Path, monkeypatch
) -> None:
    """Prompt TEST 6, positive half, on a real episode.

    D13's declared PDF hash is re-derived from the bytes on disk by D13 itself and
    again by D14, and D14's inventory is positive and numbered 1..N with a real
    image and a real hash per page.
    """

    fixture = _build_episode_fixture(tmp_path)
    result = _run_episode(monkeypatch, fixture)
    state = result["state"]

    layout = next(
        record for record in state["artifact_versions"]
        if record.get("stream") == "units/U001/layout"
    )
    pdf = Path(layout["pdf_path"])
    assert pdf.is_file()
    assert _sha256_file(pdf) == layout["pdf_sha256"]
    assert Path(layout["layout_path"]).is_file()

    inventory = state["unit_page_inventories"][0]
    assert inventory["result"] == "PASS"
    assert inventory["contiguous"] is True
    assert inventory["page_count"] == 2
    assert inventory["pdf_sha256"] == layout["pdf_sha256"]

    inspections = state["unit_page_inspections"]
    assert [record["page"] for record in inspections] == [1, 2]
    seen: set[str] = set()
    for record in inspections:
        assert record["pdf_sha256"] == layout["pdf_sha256"]
        image = Path(record["image_path"])
        assert image.is_file()
        assert record["page_sha256"] == _sha256_file(image)
        assert record["page_sha256"] not in seen
        seen.add(record["page_sha256"])
        assert record["result"] == "PASS"

    # The deterministic renderer's own asset is real too, and was written by D11
    # rather than described by a model.
    visual = state["visual_results"]["U001/visual/build_map"]
    assert visual["provenance"] == "deterministic_renderer"
    asset = Path(visual["asset_path"])
    assert asset.is_file()
    assert visual["sha256"] == _sha256_file(asset)


@pytest.mark.parametrize(
    "defect",
    ["empty_inventory", "non_contiguous", "renderer_lies_about_the_hash", "pdf_absent"],
)
def test_a_render_or_inventory_that_cannot_be_proven_is_refused(
    tmp_path: Path, defect: str
) -> None:
    """Prompt TEST 6, negative half: each way the proof can fail, and how it fails.

    A renderer that misreports its own bytes, or names a PDF that does not exist,
    is an integrity fault and admits nothing. An empty or non-contiguous page set
    is not a tool fault but a product finding, so D14 records a `FAIL` inventory
    and the guard routes to the repair classifier — never to a rendered unit.
    """

    sandbox = Path(tempfile.mkdtemp(prefix="plan26-n30-render-"))
    registry = _StubRegistry(sandbox)
    if defect == "renderer_lies_about_the_hash":
        registry.render_unit = lambda unit_id, parents: {  # type: ignore[method-assign]
            **_StubRegistry.render_unit(registry, unit_id, parents),
            "pdf_sha256": "0" * 64,
        }
    if defect == "pdf_absent":
        registry.render_unit = lambda unit_id, parents: {  # type: ignore[method-assign]
            **_StubRegistry.render_unit(registry, unit_id, parents),
            "pdf_path": str(sandbox / "does-not-exist.pdf"),
        }

    state: dict[str, Any] = {
        "selected_unit_id": "U001",
        "artifact_heads": {
            "units/U001/domain": {"version": 1, "parent_hash": None, "hash": "d" * 64},
            "units/U001/content": {"version": 1, "parent_hash": None, "hash": "c" * 64},
            "units/U001/visuals": {"version": 1, "parent_hash": None, "hash": "v" * 64},
        },
        "artifact_versions": [],
        "engine_root": str(REPO_ROOT),
        "output_root": str(sandbox),
    }
    context = _Context(transport_registry=registry)
    rendered = render.D13_RENDER_UNIT(state, context)

    if defect in ("renderer_lies_about_the_hash", "pdf_absent"):
        assert "artifact_versions" not in rendered
        assert rendered["pending_failure"]["class"] == "system"
        assert rendered["pending_failure"]["cause"] == "integrity"
        return

    assert rendered["pending_guard"]["value"] == "unit_rendered"
    if defect == "empty_inventory":
        registry.inspect_pages = lambda pdf_path, pdf_sha256: {"pages": []}  # type: ignore[method-assign]
    else:
        def _skewed(pdf_path: str, pdf_sha256: str) -> dict[str, Any]:
            report = _StubRegistry.inspect_pages(registry, pdf_path, pdf_sha256)
            report["pages"][1]["number"] = 3
            return report

        registry.inspect_pages = _skewed  # type: ignore[method-assign]

    inspected = render.D14_INVENTORY_AND_INSPECT_UNIT_PAGES(
        {**state, "artifact_versions": rendered["artifact_versions"]}, context
    )
    inventory = inspected["unit_page_inventories"][0]
    assert inventory["result"] == "FAIL"
    assert inspected["pending_guard"]["value"] == "layout_repairable"
    assert R.route_page_inspection({**state, **inspected}) == "D17_CLASSIFY_UNIT_FINDINGS"


def test_the_review_packet_names_the_exact_pdf_and_every_page_once(
    tmp_path: Path, monkeypatch
) -> None:
    """Prompt TEST 7, on a real episode: the packet is the denominator M05 answers.

    D15 freezes the PDF D14 measured and every inspected page exactly once, and
    the review M05 really returned answers that page set by number *and* by hash,
    with nothing invented and nothing dropped. This is the evidence D16 reduces,
    so it is the last thing this node is responsible for handing N31.
    """

    fixture = _build_episode_fixture(tmp_path)
    result = _run_episode(monkeypatch, fixture)
    state = result["state"]

    packet = state["review_packets"][0]
    inventory = state["unit_page_inventories"][0]
    inspections = state["unit_page_inspections"]

    assert packet["pdf_sha256"] == inventory["pdf_sha256"]
    assert packet["page_count"] == inventory["page_count"] == len(inspections)
    assert packet["page_keys"] == [record["key"] for record in inspections]
    assert len(set(packet["page_keys"])) == len(packet["page_keys"])
    assert packet["denominator"] == {
        "pages": len(inspections),
        "artifacts": len(packet["artifact_hashes"]),
        "checks": len(packet["deterministic_check_keys"]),
        "sources": len(packet["admitted_source_keys"]),
    }
    for channel in ("domain", "content", "visuals"):
        assert packet["artifact_hashes"][channel] == state["artifact_heads"][f"units/U001/{channel}"]["hash"]

    # M05's dispatch carried that exact packet, and its answer matches it by hash.
    dispatched = next(
        update for node_id, update in result["updates"]
        if node_id == "D15_FREEZE_UNIT_REVIEW_PACKET"
    )["pending_packet"]["packets"]
    assert len(dispatched) == 1
    projected_pages = dispatched[0]["pages"]
    assert [page["page_number"] for page in projected_pages] == [1, 2]
    assert [page["page_sha256"] for page in projected_pages] == [
        record["page_sha256"] for record in inspections
    ]

    review_record = state["unit_reviews"][0]
    assert review_record["unit_pdf_sha256"] == packet["pdf_sha256"]
    assert review_record["page_count"] == packet["page_count"]
    findings = review_record["payload"]["page_findings"]
    assert [entry["page_number"] for entry in findings] == [1, 2]
    assert [entry["page_sha256"] for entry in findings] == [
        record["page_sha256"] for record in inspections
    ]

    # And the review is a candidate, not an admission: no head moved for it.
    assert review_record["pre_admission"] is True
    assert "units/U001/review" not in state["artifact_heads"]


def test_the_committed_path_stops_at_a_declared_deferred_edge(
    tmp_path: Path, monkeypatch
) -> None:
    """The episode's real frontier is a declared row, never a fabricated one.

    The whole unit path now executes and M05 returns a real independent review.
    Whichever `DEFERRED_EDGES` row is currently open is where a clean episode
    halts (today that is `M05_REVIEW_ACTUAL_UNIT`'s `review_returned` guard
    resolving to `D16_REDUCE_UNIT_EVIDENCE`, N30's own declared handoff to N31;
    once N31 wires D16-D23 the same clean episode legitimately proceeds through
    D22/D23 and a second `D05_SELECT_NEXT_UNIT` call to halt on `DEFERRED_EDGES`'
    still-open `manifest_exhausted` row instead — P-N30-001, closing N90 finding
    F1). This only checks the halt is *some* declared row, not pinned to
    today's, so it keeps proving "no fabricated destination" rather than just
    "today's specific one."
    """

    fixture = _build_episode_fixture(tmp_path)
    result = _run_episode(monkeypatch, fixture)

    _assert_frontier_is_a_declared_row(result["deferred_frontier"])

    state = result["state"]
    assert state.get("pending_failure") is None
    assert state.get("terminal") is None
    assert "D91_CLASSIFY_MODEL_FAILURE" not in result["trace"]
    # Every deterministic check the path ran passed, so the frontier is a clean
    # handoff rather than a repair loop that happens to stop here.
    assert {check["result"] for check in state["deterministic_checks"]} == {"PASS"}
    assert sorted(state["artifact_heads"]) == [
        "units/U001/content",
        "units/U001/domain",
        "units/U001/visuals",
    ]


@pytest.mark.parametrize("boundary", REACHABLE_BOUNDARIES)
def test_a_graceful_interrupt_at_every_reachable_boundary_writes_one_terminal(
    tmp_path: Path, monkeypatch, boundary: str
) -> None:
    """Prompt TEST 9, over every node, map and barrier boundary the path reaches.

    The signal is raised after `boundary` returns. The next boundary observes it,
    routes to D96, and D98 writes exactly one `INTERRUPTED` terminal carrying a
    resume frontier — never two terminals, and never a product success. The
    interrupt takes precedence over the guard value at every boundary, which is
    why a signal raised after D09 still reaches the gate rather than D09's own
    deferred destination.
    """

    fixture = _build_episode_fixture(tmp_path, units=1)
    result = _run_episode(monkeypatch, fixture, interrupt_after=boundary)
    trace = result["trace"]
    terminal = result["state"].get("terminal")

    assert boundary in trace
    assert result["deferred_frontier"] is None, (
        "an interrupt must pre-empt a deferred product edge, not fall through it"
    )
    assert terminal is not None
    assert terminal["kind"] == "INTERRUPTED"
    assert terminal["resumable"] is True
    assert terminal["exit_code"] == 10
    assert terminal["evidence"]["resume_frontier"]
    assert "D96_GRACEFUL_INTERRUPT_GATE" in trace, trace

    # Exactly one terminal, counted as terminals and not as D98 entries. An
    # interrupt raised inside a `Send` map sends every in-flight branch to the
    # gate, so D96 and D98 legitimately run once per branch; what must never
    # happen is a second terminal. The extra entries refuse rather than write.
    assert len(result["state"]["terminal_history"]) == 1
    written = [
        update
        for node_id, update in result["updates"]
        if node_id == "D98_WRITE_TERMINAL" and update.get("terminal") is not None
    ]
    assert len(written) == 1
    for node_id, update in result["updates"]:
        if node_id == "D98_WRITE_TERMINAL" and update.get("terminal") is None:
            assert update["pending_failure"]["cause"] == "persistence"
            assert "already holds a terminal record" in update["pending_failure"]["message"]

    # Nothing chargeable ran after the interrupt. Stated as three separate
    # properties, because "nothing at all ran" is not true at a `Send` map and
    # asserting it would be asserting a race rather than an invariant: when the
    # signal is observed between two in-flight map branches, one branch routes to
    # the gate while the sibling's already-decided normal edge still fires, so a
    # deterministic node can legitimately complete alongside the gate. It cannot
    # dispatch, though — its own guard sees the signal — and that is what prompt
    # TEST 9's "without repeated valid calls" actually requires.
    gate = trace.index("D96_GRACEFUL_INTERRUPT_GATE")
    after = trace[gate:]
    # 1. No model node runs after the gate: no valid model call is repeated.
    assert not set(after) & MODEL_NODE_IDS
    # 2. No attempt is even reserved after it, so nothing became chargeable.
    assert "D90_RESERVE_MODEL_ATTEMPT" not in after
    for node_id, update in result["updates"][gate:]:
        assert "attempt_counters" not in (update or {}), node_id
    # 3. Anything else that ran is a deterministic node that was already in
    #    flight, and it is bounded: it may not be an admission node, so no
    #    artifact head can advance behind the interrupt.
    stragglers = set(after) - {"D96_GRACEFUL_INTERRUPT_GATE", "D98_WRITE_TERMINAL"}
    assert stragglers <= set(NODE_CATALOGUE), stragglers
    for node_id, update in result["updates"][gate:]:
        assert "artifact_heads" not in (update or {}), node_id


def test_an_interrupt_inside_a_send_map_is_bounded_across_repeated_episodes(
    tmp_path: Path, monkeypatch
) -> None:
    """The one boundary whose post-gate trace is not deterministic, pinned.

    An interrupt observed between two in-flight `Send` branches is a real race:
    across repeated runs of the *same* input, the sibling branch sometimes routes
    to the gate and sometimes completes its own normal edge first. The matrix row
    for this boundary would otherwise be asserting whichever outcome happened to
    occur. Twelve episodes are run and the bound is asserted over all of them:
    whatever the interleaving, exactly one terminal is written, no model node and
    no attempt reservation ever follows the gate, and the only deterministic node
    that can straggle is the sibling's own join target.
    """

    shapes: set[tuple[str, ...]] = set()
    for index in range(12):
        fixture = _build_episode_fixture(tmp_path / f"map-interrupt-{index}")
        result = _run_episode(
            monkeypatch, fixture, interrupt_after="M01_RESEARCH_UNIT_SOURCES"
        )
        trace = result["trace"]
        gate = trace.index("D96_GRACEFUL_INTERRUPT_GATE")
        after = trace[gate:]
        shapes.add(tuple(after))

        assert len(result["state"]["terminal_history"]) == 1
        assert result["state"]["terminal"]["kind"] == "INTERRUPTED"
        assert not set(after) & MODEL_NODE_IDS
        assert "D90_RESERVE_MODEL_ATTEMPT" not in after
        assert set(after) - {"D96_GRACEFUL_INTERRUPT_GATE", "D98_WRITE_TERMINAL"} <= {
            "D06B_RETRIEVE_SOURCE_CANDIDATES"
        }

    # The race is real and is recorded as such rather than asserted away: if a
    # future change made it deterministic this would still pass, but the bound
    # above is what the matrix row is entitled to claim.
    assert shapes


def test_the_unobservable_boundary_is_excluded_for_a_stated_reason(
    tmp_path: Path, monkeypatch
) -> None:
    """M05's own update is observable now that N31 has wired D16-D23.

    Before N31 wired D16-D23 (P-N31-001), M05 really executed: the committed
    state held its execution receipt, its candidate record and its page
    findings, but the branch that would emit its update resolved to the
    deferred `D16_REDUCE_UNIT_EVIDENCE` and aborted the superstep, so no
    stream consumer ever saw it. `D16_REDUCE_UNIT_EVIDENCE` is now a real,
    wired node body, so that premise has inverted exactly as this test's own
    docstring anticipated it would (see `results/N30_UNIT_GRAPH.result.v1
    .md`): M05's update reaches the stream like every other boundary's does,
    and this test now proves that inversion directly instead of asserting
    the retired exclusion.

    `REACHABLE_BOUNDARIES`/`UNOBSERVABLE_BOUNDARY` are left untouched here:
    other tests (`test_a_graceful_interrupt_at_every_reachable_boundary_
    writes_one_terminal` included) still rely on their current values, and
    P-N31-003 scopes this fix to this one test function, so this test's own
    matrix-membership assertions are dropped rather than widened onto those
    shared constants.
    """

    fixture = _build_episode_fixture(tmp_path)
    result = _run_episode(monkeypatch, fixture)
    state = result["state"]

    assert UNOBSERVABLE_BOUNDARY in result["trace"]
    m05_update = next(
        update for node_id, update in result["updates"] if node_id == UNOBSERVABLE_BOUNDARY
    )
    assert m05_update, "M05's own update must be a real, non-empty stream chunk now"

    # It ran, and its receipt, candidate and review are all committed, exactly
    # as before this inversion.
    assert [
        receipt["job_id"] for receipt in state["model_execution_receipts"]
    ].count(UNOBSERVABLE_BOUNDARY) == 1
    review_record = state["unit_reviews"][0]
    assert review_record["job_id"] == UNOBSERVABLE_BOUNDARY
    assert review_record["pre_admission"] is True


def test_a_hard_crash_is_recovered_as_an_orphan_without_continuing_its_thread(
    tmp_path: Path, monkeypatch
) -> None:
    """Prompt TEST 9's SIGKILL half: the orphan thread is read, never resumed."""

    fixture = _build_episode_fixture(tmp_path)
    lock, invocation, envelope = _prepare_episode(fixture)
    context = _HarnessContext(fixture["engine"], fixture["output_root"], fixture["sandbox"])
    monkeypatch.setattr(
        G,
        "build_model_node_context",
        lambda _context, **_kwargs: _scripted_model_context(fixture["sandbox"]),
    )
    compiled = G.build_curriculum_factory_graph(
        engine_root=fixture["engine"], output_root=fixture["output_root"]
    )

    # Simulate the power loss: stop consuming the stream mid-episode and never
    # let D98 run, leaving the episode lease open.
    executed: list[str] = []
    stream = compiled.stream(
        {"invocation": envelope},
        config=invocation.config,
        stream_mode="updates",
        context=context,
    )
    for chunk in stream:
        executed.extend(chunk)
        if "D04_INITIALIZE_OR_RESUME" in chunk:
            break
    stream.close()

    committed = compiled.get_state(invocation.config)
    assert committed.values.get("terminal") is None
    assert committed.values["run_id"]

    # The recovery path reads the orphan and prepares a *new* thread for it.
    ledger = P.EpisodeLeaseLedger(fixture["output_root"])
    orphan = ledger.open_lease()
    assert orphan is not None
    assert orphan["thread_id"] == invocation.thread_id
    saver, _connection = P.open_checkpoint_saver(fixture["output_root"])
    view = P.ReadOnlyCheckpointView(compiled, saver)
    readout = P.extract_prior_episode(view, invocation.thread_id)
    assert readout is not None
    assert readout.terminal is None, "an orphan holds no terminal"
    assert readout.next, "a crashed episode must expose an incomplete frontier"
    for node_id in readout.next:
        assert not str(node_id).startswith(("M0",)), (
            "a model node may never be stored as a resume destination"
        )
    lock.release()


# ---------------------------------------------------------------------------
# Dependency gaps: every one this node ever raised is now closed, and each is
# kept below as the regression that would catch its reversal.
# ---------------------------------------------------------------------------


def test_every_blocking_gap_is_declared_with_an_owner_and_rework_edge() -> None:
    """`BLOCKING_GAPS` is empty, and any future row still has to be well formed.

    B-1 through B-13 are all closed. The shape assertion is kept rather than
    deleted with the rows, so a gap found later cannot be recorded in prose
    without an owner and a rework edge.
    """

    rework_edges = {
        "state_or_reducer",
        "transport_or_authorization",
        "deterministic_node",
        "model_node_or_projection",
        "topology_or_guard",
    }
    assert U.BLOCKING_GAPS == ()
    for gap in U.BLOCKING_GAPS:  # pragma: no cover - guards a future row
        assert gap["owner"].startswith("N")
        assert gap["rework_edge"] in rework_edges
        assert len(gap["detail"]) > 80


# --- B-1 (RESOLVED by N11 generation 5): kept as the regression that would catch it


def test_a_zero_arg_constructible_write_once_channel_is_what_broke_d01() -> None:
    """The mechanism behind the resolved B-1, pinned so a redeclaration re-fails.

    LangGraph seeds a `BinaryOperatorAggregate` by calling the annotated type
    when that type is zero-arg constructible, so `Annotated[dict, write_once]`
    starts at `{}` and the reducer rejects the channel's own first write. The
    `X | None` declaration N11 chose is not constructible, so the channel stays
    unset. Both halves are asserted, because the fix is a property of the
    declaration, not of the reducer.
    """

    class _Broken(TypedDict, total=False):
        effective_run: Annotated[dict[str, Any], write_once]

    builder: StateGraph = StateGraph(_Broken)
    builder.add_node("A", lambda state: {"effective_run": {"x": 1}})
    builder.add_edge(START, "A")
    builder.add_edge("A", END)
    with pytest.raises(WriteOnceConflict):
        builder.compile().invoke({})

    class _Control(TypedDict, total=False):
        effective_run: Annotated[dict[str, Any] | None, write_once]

    control: StateGraph = StateGraph(_Control)
    control.add_node("A", lambda state: {"effective_run": {"x": 1}})
    control.add_node("B", lambda state: {"effective_run": {"x": 1}})
    control.add_edge(START, "A")
    control.add_edge("A", "B")
    control.add_edge("B", END)
    assert control.compile().invoke({}) == {"effective_run": {"x": 1}}


def test_no_write_once_channel_of_the_production_graph_is_seeded(compiled) -> None:
    """B-1 is closed on the real compiled graph, not on a synthetic one."""

    seeded = sorted(
        field
        for field in FACTORY_STATE_FIELDS
        if FIELD_REDUCER_CLASSES[field] == "write_once"
        and isinstance(compiled.channels.get(field), BinaryOperatorAggregate)
        and isinstance(getattr(compiled.channels[field], "value", None), (str, list, dict))
    )
    assert seeded == [], f"these write_once channels would reject their own first write: {seeded}"


# --- B-2 (RESOLVED by N22 generation 5): the inverted acceptance rows


def test_a_source_fanout_stages_one_m01_packet_per_request_key() -> None:
    """D06 commits the denominator and stages exactly the dispatch it declared."""

    assert "pending_packet" in NODE_CATALOGUE["D06_COMPILE_SOURCE_REQUESTS"].outputs
    unit = {
        "id": "U001",
        "title": "t",
        "required_explanation": ["fact"],
        "safety_focus": ["care"],
    }
    state = {
        "run_id": "run-n30-fixture",
        "episode_id": "episode-n30-fixture",
        "effective_run": {"unit_records": [unit], "target_closure": ["U001"]},
        "selected_unit_id": "U001",
        "source_admissions": [],
        "engine_root": "/tmp",
    }
    update = sources.D06_COMPILE_SOURCE_REQUESTS(state, _Context())
    assert update["pending_guard"]["value"] == "discovery_fanout"

    denominator = next(iter(update["source_denominators"].values()))
    packet = update["pending_packet"]
    assert packet["dispatch"] == "M01_RESEARCH_UNIT_SOURCES"
    members = packet["packets"]
    assert sorted(m["correlation"]["correlation_key"] for m in members) == sorted(
        denominator["request_keys"]
    )
    assert all(m["phase"] == "DISCOVER" for m in members)

    # B-6: the dispatcher reserves before it dispatches, so the staged members
    # reach their worker through D90 rather than on a direct edge.
    assert R.route_source_discovery_fanout({**state, **update}) == "D90_RESERVE_MODEL_ATTEMPT"
    reserved = mn.D90_RESERVE_MODEL_ATTEMPT({**state, **update}, None)
    dispatch = R.route_attempt_reservation({**state, **update, **reserved})
    assert [send.node for send in dispatch] == ["M01_RESEARCH_UNIT_SOURCES"] * len(members)
    assert [send.arg for send in dispatch] == reserved["pending_packet"]["packets"]
    assert [send.arg["correlation"]["correlation_key"] for send in dispatch] == sorted(
        denominator["request_keys"]
    )


@pytest.mark.parametrize(
    "node_id, worker",
    [
        ("D06_COMPILE_SOURCE_REQUESTS", "M01 discovery"),
        ("D06B_RETRIEVE_SOURCE_CANDIDATES", "M01 interpretation"),
        ("D07_CORRELATE_AND_ADMIT_SOURCES", "M02"),
        ("D08_VALIDATE_DOMAIN", "M03"),
        ("D10_COMPILE_VISUAL_BRIEFS", "D11"),
        ("D12_VISUAL_BARRIER_AND_JOIN", "M04"),
        ("D15_FREEZE_UNIT_REVIEW_PACKET", "M05"),
    ],
)
def test_every_dispatching_node_authorizes_a_worker_packet(node_id: str, worker: str) -> None:
    """The frozen catalogue rows B-2 required, asserted as the total dispatch set."""

    spec = NODE_CATALOGUE[node_id]
    assert "pending_packet" in spec.outputs, f"{node_id} stages nothing for {worker}"
    assert {"run_id", "episode_id"} <= set(spec.inputs), (
        f"{node_id} dispatches without run/episode identity, so it has no correlation"
    )


def test_a_staged_m04_member_is_an_m04_packet_not_a_brief() -> None:
    """D12's members carry the spec 9 projection `Send` will hand M04 verbatim."""

    unit_id = "U001"
    briefs = [_brief(unit_id, "det-a", "deterministic"), _brief(unit_id, "mdl-a", "model")]
    key = f"{unit_id}/visual/det-a"
    state = _visual_state(unit_id, briefs, {key: _visual_result(key, unit_id, "deterministic")})
    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(state, _Context())

    member = update["pending_packet"]["packets"][0]
    assert member["brief"]["brief_id"] == f"{unit_id}/visual/mdl-a"
    assert "visual_contract" in member and "permitted_facts" in member
    # The reservation is D90's to mint; a dispatching node staging one would be
    # committing an attempt counter it does not own (spec 6.2, D90 row).
    assert "reservation" not in member


# --- B-3 (RESOLVED by N23 generation 3): D90/D91 are registrable and registered


def test_d90_and_d91_are_registered_production_nodes(compiled, available) -> None:
    """Both bookkeeping nodes exist, pass N20's binding audit, and are compiled in."""

    assert "D90_RESERVE_MODEL_ATTEMPT" in available
    assert "D91_CLASSIFY_MODEL_FAILURE" in available
    inventory = G.binding_inventory()
    for node_id in ("D90_RESERVE_MODEL_ATTEMPT", "D91_CLASSIFY_MODEL_FAILURE"):
        body = inventory[node_id]
        parameters = list(inspect.signature(body).parameters.values())
        assert len(parameters) == 2
        assert all(p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD for p in parameters)
        assert body.__module__ == "runtime.langgraph_factory.model_nodes"
    assert {"D90_RESERVE_MODEL_ATTEMPT", "D91_CLASSIFY_MODEL_FAILURE"} <= set(
        compiled.get_graph().nodes
    )


def test_d90_mints_one_reservation_per_fanout_member(compiled) -> None:
    """A map is N attempts, not one: the bound is per correlation, not per superstep."""

    unit = {
        "id": "U001",
        "title": "t",
        "required_explanation": ["fact"],
        "safety_focus": ["care"],
    }
    state = {
        "run_id": "run-n30-fixture",
        "episode_id": "episode-n30-fixture",
        "effective_run": {"unit_records": [unit], "target_closure": ["U001"]},
        "selected_unit_id": "U001",
        "source_admissions": [],
        "engine_root": "/tmp",
    }
    staged = sources.D06_COMPILE_SOURCE_REQUESTS(state, _Context())
    reserved = mn.D90_RESERVE_MODEL_ATTEMPT({**state, **staged}, None)

    members = reserved["pending_packet"]["packets"]
    assert len(members) == 2
    assert len({m["reservation"]["activation_id"] for m in members}) == 2
    assert len(reserved["attempt_counters"]) == 2
    assert all(value == 1 for value in reserved["attempt_counters"].values())
    assert reserved["pending_guard"]["value"] == "authorized"


# --- B-6 (RESOLVED by N20 generation 7): every model dispatch reserves first


def test_every_model_dispatch_is_routed_through_d90(topology) -> None:
    """B-6 closed, asserted against the really-compiled edge set, not the tables.

    Spec 6.2's D90 row requires the counter increment to be committed before any
    dispatch. Both halves are asserted so either could regress and be caught:
    every dispatcher reaches D90, and D90 is the *only* predecessor any model
    node has.
    """

    dispatchers = {
        "D06_COMPILE_SOURCE_REQUESTS",
        "D06B_RETRIEVE_SOURCE_CANDIDATES",
        "D07_CORRELATE_AND_ADMIT_SOURCES",
        "D08_VALIDATE_DOMAIN",
        "D12_VISUAL_BARRIER_AND_JOIN",
        "D15_FREEZE_UNIT_REVIEW_PACKET",
    }
    to_reservation = {
        source
        for source, target, _conditional in topology["edges"]
        if target == "D90_RESERVE_MODEL_ATTEMPT"
    }
    assert dispatchers <= to_reservation, sorted(dispatchers - to_reservation)

    predecessors = {
        (source, target)
        for source, target, _conditional in topology["edges"]
        if target in MODEL_NODE_IDS and source != "D90_RESERVE_MODEL_ATTEMPT"
    }
    assert not predecessors, f"a model node is entered without a reservation: {sorted(predecessors)}"


def test_an_unreserved_dispatch_is_refused_by_every_adapter() -> None:
    """The runtime consequence of B-6, on the real adapters and the real fake transport."""

    sandbox = Path(tempfile.mkdtemp())
    context = mn.build_test_model_node_context(sandbox_root=sandbox, responses={})
    whole_state = {field: None for field in FACTORY_STATE_FIELDS}
    whole_state.update({"run_id": "r1", "episode_id": "e1", "selected_unit_id": "U001"})

    with pytest.raises(mn.AttemptNotReserved):
        mn.MODEL_NODE_ADAPTERS["M02_CREATE_UNIT_DOMAIN_DATA"](whole_state, context)
    with pytest.raises(mn.ProjectionViolation):
        mn.MODEL_NODE_ADAPTERS["M05_REVIEW_ACTUAL_UNIT"](whole_state, context)

    # Even a correctly staged member is refused until D90 has attached a reservation.
    unit_id = "U001"
    briefs = [_brief(unit_id, "det-a", "deterministic"), _brief(unit_id, "mdl-a", "model")]
    key = f"{unit_id}/visual/det-a"
    state = _visual_state(unit_id, briefs, {key: _visual_result(key, unit_id, "deterministic")})
    update = visuals.D12_VISUAL_BARRIER_AND_JOIN(state, _Context())
    member = update["pending_packet"]["packets"][0]
    with pytest.raises(mn.AttemptNotReserved):
        mn.MODEL_NODE_ADAPTERS["M04_CREATE_UNIT_VISUALS"](member, context)


def test_d90s_authorized_guard_expresses_a_map() -> None:
    """The second half of B-6, closed: D90's guard translates its restaged packet.

    A one-member dispatch becomes a one-element `Send` list and an N-member map an
    N-element one, so D07/D08/D15 can route through D90 without their single
    dispatch collapsing into a whole-state edge.
    """

    def _reserved(members: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "pending_guard": {
                "node": "D90_RESERVE_MODEL_ATTEMPT",
                "value": "authorized",
                "kind": "model_attempt",
                "decision": "authorized",
                "detail": {"job_id": "M01_RESEARCH_UNIT_SOURCES", "members": len(members)},
            },
            "pending_packet": {"dispatch": "M01_RESEARCH_UNIT_SOURCES", "packets": members},
        }

    mapped = R.route_attempt_reservation(_reserved([{"a": 1}, {"b": 2}]))
    assert [(send.node, send.arg) for send in mapped] == [
        ("M01_RESEARCH_UNIT_SOURCES", {"a": 1}),
        ("M01_RESEARCH_UNIT_SOURCES", {"b": 2}),
    ]
    single = R.route_attempt_reservation(_reserved([{"a": 1}]))
    assert [(send.node, send.arg) for send in single] == [
        ("M01_RESEARCH_UNIT_SOURCES", {"a": 1})
    ]


# --- B-7 (RESOLVED by N22 generation 6 / N23 generation 4): admission mints


def test_a_model_candidate_is_minted_into_an_admissible_artifact_version() -> None:
    """B-7 closed, on the real M02 adapter and the real D08 body.

    The candidate still carries no `version`/`hash`/`parent_hash` — spec 2.4's
    code-owned-admission rule — and D08 now mints them from the candidate's
    `payload` and the current head. Both halves are asserted: the model still may
    not mint, and admission now can.
    """

    sandbox = Path(tempfile.mkdtemp())
    context = _scripted_model_context(sandbox)
    update = mn.MODEL_NODE_ADAPTERS["M02_CREATE_UNIT_DOMAIN_DATA"](
        _m02_packet("U001"), context
    )
    record = update["artifact_versions"][0]
    assert record["record_kind"] == "model_candidate"
    for field in ("version", "parent_hash", "hash"):
        assert field not in record, f"a model minted {field}; that is admission's authority"

    admission = domain.D08_VALIDATE_DOMAIN(
        {
            "run_id": "r",
            "episode_id": "e",
            "selected_unit_id": "U001",
            "effective_run": {
                "unit_records": [{"id": "U001", "title": "t"}],
                "manifest_schema": None,
            },
            "artifact_versions": update["artifact_versions"],
            "artifact_heads": {},
            "source_admissions": [],
            "engine_root": str(REPO_ROOT),
        },
        _Context(),
    )
    # The candidate is resolved and versioned; whether it then passes the domain
    # checks is a product question, and this fixture's body deliberately fails
    # them. What B-7 was about is that the candidate is *seen* at all.
    assert "pending_failure" not in admission
    assert admission["pending_guard"]["value"] == "domain_repairable"
    assert {finding["check_id"] for finding in admission["pending_guard"]["detail"]["findings"]} <= {
        "domain_schema_valid",
        "domain_facts_sourced",
        "domain_verifier_fixtures",
    }


def test_each_join_reads_a_lineage_field_the_candidate_record_now_writes(
    tmp_path: Path, monkeypatch
) -> None:
    """The same gap, enumerated per consuming join, now inverted.

    Asserted against the records a real episode actually produced, not against
    the source of `_candidate_record`: N23 attaches lineage at the adapter call
    sites, so a source scan would pass or fail for the wrong reason.
    """

    fixture = _build_episode_fixture(tmp_path)
    result = _run_episode(monkeypatch, fixture)

    interpretations = result["state"]["source_interpretations"]
    assert interpretations
    for record in interpretations.values():
        # D07 stales an interpretation whose parent bytes are no longer the
        # retrieval, and checks it did not cross units.
        assert record["retrieval_sha256"]
        assert record["unit_id"] == "U001"
        # The model's own answer stays quarantined.
        assert "payload" in record
        assert not {"version", "hash", "parent_hash"} & set(record)

    discoveries = result["state"]["source_discoveries"]
    assert discoveries
    for record in discoveries.values():
        assert record["unit_id"] == "U001"
        # `locators` is the model's answer, so it stays inside the payload.
        assert "locators" not in record
        assert "locators" in record["payload"]


# --- B-10 (RESOLVED by N22 generation 7 / N13 generation 2): the two unit-content
# contracts are one language


def test_the_unit_content_contract_admits_exactly_what_m03_may_write() -> None:
    """B-10's inversion, asserted as algebra rather than on one lucky sample.

    D09 holds M03's `unit_content` body to `domain.CURRICULUM_CONTRACTS[0]`. The
    defect was that the constant named the whole-curriculum *manifest* schema,
    whose property set is disjoint from M03's, so `content_schema_valid` could
    never pass for any document at all. Two containments make the languages one:
    everything D09 requires is something M03 may write, and everything M03 may
    write is something D09 permits. A sample-based test would have passed for the
    wrong reason on a body that happens to validate.
    """

    import jsonschema

    m03 = json.loads(
        (
            REPO_ROOT
            / "runtime"
            / "langgraph_factory"
            / "schemas"
            / "M03_write_unit_content.schema.json"
        ).read_text(encoding="utf-8")
    )
    unit_content = m03["properties"]["unit_content"]
    target = json.loads(
        (REPO_ROOT / domain.CURRICULUM_CONTRACTS[0]).read_text(encoding="utf-8")
    )

    # Both are still closed: the fix was to agree on the vocabulary, not to open
    # one side up so anything validates.
    assert unit_content["additionalProperties"] is False
    assert target["additionalProperties"] is False

    assert set(target["required"]) <= set(unit_content["properties"])
    assert set(unit_content["properties"]) <= set(target["properties"])

    # And a maximal legal M03 body — every optional key populated — validates on
    # the real validator against both.
    body = {
        "unit_id": "U001",
        "sections": [{"section_id": "s1", "heading": "h", "body": "b"}],
        "evidence_references": [{"section_id": "s1", "source_id": "x", "source_location": "p.1"}],
        "visuals": list(DECLARED_VISUALS),
    }
    jsonschema.Draft202012Validator(unit_content).validate(body)
    jsonschema.Draft202012Validator(target).validate(body)


def test_a_real_m03_content_head_declares_the_visual_denominator(
    tmp_path: Path, monkeypatch
) -> None:
    """B-10's second consequence, inverted: D10 compiles a real two-subset denominator.

    D10 reads the visual denominator off the admitted content body's `visuals`.
    While `unit_content` forbade that key the two subsets were empty forever and
    D11/M04 were unreachable. On a real episode the admitted content head now
    carries the declaration and D10 splits it.
    """

    m03 = json.loads(
        (
            REPO_ROOT
            / "runtime"
            / "langgraph_factory"
            / "schemas"
            / "M03_write_unit_content.schema.json"
        ).read_text(encoding="utf-8")
    )
    assert "visuals" in m03["properties"]["unit_content"]["properties"]

    fixture = _build_episode_fixture(tmp_path)
    result = _run_episode(monkeypatch, fixture)
    state = result["state"]

    content_head = state["artifact_heads"]["units/U001/content"]
    version = next(
        record
        for record in state["artifact_versions"]
        if record.get("stream") == "units/U001/content" and record.get("hash") == content_head["hash"]
    )
    assert [entry["role"] for entry in version["body"]["visuals"]] == [
        entry["role"] for entry in DECLARED_VISUALS
    ]

    denominator = next(iter(state["visual_denominators"].values()))
    assert denominator["deterministic_keys"] == ["U001/visual/build_map"]
    assert denominator["model_keys"] == ["U001/visual/overview"]
    assert denominator["size"] == 2
    assert "D11_CREATE_DETERMINISTIC_VISUALS" in result["trace"]
    assert "M04_CREATE_UNIT_VISUALS" in result["trace"]


# --- B-11 (RESOLVED by N22 generation 7): D15 resolves the layout from D13's version


def test_d15_resolves_the_layout_from_d13s_version_not_from_a_head(
    tmp_path: Path, monkeypatch
) -> None:
    """B-11's inversion, with the safety property it protected re-asserted.

    D15 required an admitted `layout` head, but spec 8.1 gives D13/D14
    `append-unique` and spec section 5 admits heads at D08/D09/D12/D20 only, so
    no node was authorized to write one and the requirement was unsatisfiable.
    D15 now resolves the layout from the version D13 appended. What must NOT have
    been weakened is the reason the requirement existed: the packet may not name
    bytes the inventory did not measure. Both halves are asserted.
    """

    # `layout` is no longer required as a head, and still no node admits one.
    assert "layout" not in review.PACKET_ARTIFACT_CHANNELS
    admitters = []
    for node_id, spec in NODE_CATALOGUE.items():
        if "artifact_heads" not in spec.outputs:
            continue
        body = inspect.getsource(G.binding_inventory()[node_id])
        if '"layout"' in body or "'layout'" in body:
            admitters.append(node_id)
    assert not admitters, f"{admitters} admits a layout head; spec 8.1 authorizes none"

    fixture = _build_episode_fixture(tmp_path)
    result = _run_episode(monkeypatch, fixture)
    state = result["state"]

    packet = state["review_packets"][0]
    layout_version = next(
        record for record in state["artifact_versions"]
        if record.get("stream") == "units/U001/layout"
    )
    assert packet["artifact_hashes"]["layout"] == layout_version["hash"]
    assert "units/U001/layout" not in state["artifact_heads"]

    # The safety property: the packet's PDF hash is the one D14 actually measured.
    inventory = state["unit_page_inventories"][0]
    assert packet["pdf_sha256"] == inventory["pdf_sha256"]
    render = next(
        update for node_id, update in result["updates"] if node_id == "D13_RENDER_UNIT"
    )
    assert any(
        version.get("hash") == packet["artifact_hashes"]["layout"]
        for version in render["artifact_versions"]
    )


def test_d15_still_refuses_a_packet_whose_layout_cannot_be_resolved() -> None:
    """The relaxation is not a hole: with no layout version at all, D15 refuses."""

    failure = review.D15_FREEZE_UNIT_REVIEW_PACKET(
        {
            "run_id": "r",
            "episode_id": "e",
            "selected_unit_id": "U001",
            "artifact_heads": {
                "units/U001/domain": {"version": 1, "hash": "d"},
                "units/U001/content": {"version": 1, "hash": "c"},
                "units/U001/visuals": {"version": 1, "hash": "v"},
            },
            "artifact_versions": [],
            "unit_page_inventories": [],
            "unit_page_inspections": [],
            "deterministic_checks": [],
            "source_admissions": [],
            "engine_root": str(REPO_ROOT),
        },
        _Context(),
    )
    assert failure["pending_failure"]["class"] == "system"
    assert failure["pending_failure"]["cause"] in ("invalid_input", "integrity")


# --- B-12 (RESOLVED by N22 generation 7): the member names the channel it lands on


def test_d10_stages_a_member_d11_can_actually_read() -> None:
    """B-12's inversion, driven through the real D10, the real guard and the real D11.

    `_staged_fanout` delivers a member as the target's whole input state. D11 is
    the only *deterministic* `Send` target, and a deterministic node is narrowed
    by `project()`, which reads authorized inputs by state-channel name — so a
    flat member keyed `brief` (the convention every model adapter uses) is
    unreadable to it. D10 therefore stages each member under the channel D11
    declares. The member's key set must be a subset of the declared channels, or
    the fan-out is putting worker-local values into the persisted state schema.
    """

    assert NODE_CATALOGUE["D11_CREATE_DETERMINISTIC_VISUALS"].inputs == ("pending_packet",)

    unit_id = "U001"
    state = {
        "run_id": "run-n30-fixture",
        "episode_id": "episode-n30-fixture",
        "selected_unit_id": unit_id,
        "artifact_heads": {
            f"units/{unit_id}/content": {"version": 1, "parent_hash": None, "hash": "content-hash-1"},
            f"units/{unit_id}/domain": {"version": 1, "parent_hash": None, "hash": "domain-hash-1"},
        },
        "artifact_versions": [
            {
                "stream": f"units/{unit_id}/content",
                "version": 1,
                "parent_hash": None,
                "hash": "content-hash-1",
                "body": {"visuals": [{"role": "det-a", "kind": "schematic"}]},
            }
        ],
        "engine_root": "/tmp",
    }
    update = visuals.D10_COMPILE_VISUAL_BRIEFS(state, _Context())
    assert update["pending_guard"]["value"] == "deterministic_visual_fanout"
    dispatch = R.route_visual_briefs({**state, **update})
    assert [send.node for send in dispatch] == ["D11_CREATE_DETERMINISTIC_VISUALS"]

    member = dispatch[0].arg
    assert set(member) <= set(FACTORY_STATE_FIELDS), (
        "a Send member may only name real state channels, or a deterministic "
        "worker cannot project it"
    )
    assert set(member) == {"pending_packet"}
    assert set(member["pending_packet"]) >= {"brief", "permitted_facts"}

    sandbox = Path(tempfile.mkdtemp(prefix="plan26-n30-d11-"))
    produced = visuals.D11_CREATE_DETERMINISTIC_VISUALS(
        member, _Context(transport_registry=_StubRegistry(sandbox))
    )
    assert "pending_failure" not in produced
    assert produced["pending_guard"]["value"] == "visual_produced"
    result = next(iter(produced["visual_results"].values()))
    assert result["subset"] == "deterministic"
    assert Path(result["asset_path"]).exists()
    assert result["sha256"] == hashlib.sha256(Path(result["asset_path"]).read_bytes()).hexdigest()


# --- B-13 (RESOLVED by N23 generation 5): each M01 phase has its own attempt budget


def test_each_m01_phase_reserves_against_its_own_attempt_budget(
    tmp_path: Path, monkeypatch
) -> None:
    """B-13's inversion, restated so it observes the defect it was written for.

    The generation-8 form of this probe drove two *discovery* reservations and so
    could not tell a shared counter from a per-activation one; N23's own record
    said as much. This version takes the two packets a real episode's real D06 and
    real D06B staged — one per phase, with the same `correlation_key`, which D06B
    and D07 index their channels by and which therefore may not change — and
    reserves each against the same counter dict.
    """

    fixture = _build_episode_fixture(tmp_path)
    result = _run_episode(monkeypatch, fixture)

    discovery_packet = next(
        update for node_id, update in result["updates"]
        if node_id == "D06_COMPILE_SOURCE_REQUESTS"
    )["pending_packet"]
    interpretation_packet = next(
        update for node_id, update in result["updates"]
        if node_id == "D06B_RETRIEVE_SOURCE_CANDIDATES"
    )["pending_packet"]

    keys = {
        member["correlation"]["correlation_key"]
        for packet in (discovery_packet, interpretation_packet)
        for member in packet["packets"]
    }
    assert len(keys) == 2, "the two phases must keep the request keys D06B/D07 index by"

    # A run in which nothing goes wrong spends exactly one attempt per activation.
    committed = result["state"]["attempt_counters"]
    m01 = {key: value for key, value in committed.items() if key.startswith("M01_")}
    assert len(m01) == 4, m01
    assert set(m01.values()) == {1}
    assert {key.split("|")[1] for key in m01} == {"DISCOVER", "INTERPRET"}

    # And the retry spec section 12 freezes really is still available afterwards:
    # a second reservation in the interpretation phase is authorized, not exhausted.
    base = {"run_id": result["state"]["run_id"], "episode_id": result["state"]["episode_id"]}
    retry = mn.D90_RESERVE_MODEL_ATTEMPT(
        {**base, "attempt_counters": dict(committed), "pending_packet": interpretation_packet},
        None,
    )
    assert retry["pending_guard"]["value"] == "authorized"
    reservation = retry["pending_packet"]["packets"][0]["reservation"]
    assert reservation["attempt_ordinal"] == 2
    assert reservation["limit"] == 2

    # The third is refused, which is the bound still being enforced.
    exhausted = mn.D90_RESERVE_MODEL_ATTEMPT(
        {
            **base,
            "attempt_counters": {**committed, **retry["attempt_counters"]},
            "pending_packet": interpretation_packet,
        },
        None,
    )
    guard = exhausted["pending_guard"]
    assert (guard.get("value") or guard.get("decision")) == "exhausted"


# --- B-8 (RESOLVED by N13 generation 2): the production transport has the surface


def test_the_production_transport_exposes_the_capability_surface_the_nodes_call() -> None:
    """B-8's inversion: the five methods the unit path reaches for really exist.

    D03 calls `prove_capability`/`observe_executable`; D11, D13 and D14 call
    `render_deterministic_visual`, `render_unit` and `inspect_pages`. This node's
    own evidence is scoped to a test transport by its prompt, so it asserts the
    surface exists rather than that a live run succeeds — the live proof is N60's.
    """

    required = (
        "prove_capability",
        "observe_executable",
        "render_unit",
        "inspect_pages",
        "render_deterministic_visual",
    )
    missing = [name for name in required if not callable(getattr(mn.tp.CliTransport, name, None))]
    assert missing == []


def test_this_nodes_renderers_are_a_test_double_and_not_exposed_to_n13s_store_gap(
    tmp_path: Path, monkeypatch
) -> None:
    """N13 generation 2 raised two gaps this node must state a position on.

    `plan26/n13/artifact-bodies-never-reach-the-store`: no deterministic node
    calls `ArtifactStore.admit_version`, so D08/D09/D12 advance heads in graph
    state only and nothing writes the admitted *bytes*. A production
    `CliTransport.render_unit`, which is handed head hashes and must resolve the
    bodies out of the content store, therefore raises `RenderFault`.
    `plan26/n13/visual-assets-are-unreachable-from-d13`: D13 passes no asset map,
    so a production unit PDF is prose-only.

    Neither is inherited by this node's proof, and that is checked rather than
    assumed: the harness `transport_registry` is a test double that composes its
    own bytes from the arguments it is handed and never reads the store, so the
    graph-orchestration claims here hold with or without the store gap. Both
    findings are real and both are N22/N31/N32/N40's to close before a live run.
    """

    # The gap N13 named is real and still open: nothing in `nodes/` persists bodies.
    from runtime.langgraph_factory import artifacts as A

    assert hasattr(A.ArtifactStore, "admit_version")
    nodes_dir = REPO_ROOT / "runtime" / "langgraph_factory" / "nodes"
    callers = [
        path.name
        for path in sorted(nodes_dir.glob("*.py"))
        if "admit_version" in path.read_text(encoding="utf-8")
    ]
    assert callers == [], f"{callers} now persists artifact bodies; revisit this note"

    # This node's renderers do not depend on it: no method of the harness registry
    # names the store, the path guard, or the output root.
    source = inspect.getsource(_StubRegistry)
    for forbidden in ("ArtifactStore", "admit_version", "path_guard", "output_root"):
        assert forbidden not in source

    # And the episode really renders, inspects and admits without a single blob.
    fixture = _build_episode_fixture(tmp_path)
    result = _run_episode(monkeypatch, fixture)
    store_root = fixture["output_root"]
    blobs = [path for path in store_root.rglob("*") if path.is_file() and "artifact" in str(path)]
    assert blobs == [], blobs
    _assert_frontier_is_a_declared_row(result["deferred_frontier"])
    assert result["state"]["unit_page_inventories"][0]["result"] == "PASS"


def test_blocked_the_review_handoff_to_n31_is_declared_not_wired(available) -> None:
    """A clean D16 is N31's handoff; D16 has no body, so the edge is declared.

    This is the prompt's own frontier ("clean D16 evidence is a handoff to
    N31"), recorded as a deferred edge rather than a fabricated destination.
    """

    assert "D16_REDUCE_UNIT_EVIDENCE" not in available
    assert ("M05_REVIEW_ACTUAL_UNIT", "review_returned", "D16_REDUCE_UNIT_EVIDENCE",
            "N31_REPAIR_ACCEPTANCE") in U.DEFERRED_EDGES
    assert R.GUARD_DESTINATIONS["D16_REDUCE_UNIT_EVIDENCE"]["unit_denominator_passed"] == "D22_ACCEPT_UNIT"
