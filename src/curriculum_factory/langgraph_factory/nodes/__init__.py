"""Deterministic node bodies for the Plan 26 curriculum factory graph.

Each `D` node in spec section 6.2 is exactly one bounded callable in exactly one
module of this package. A node body never loops over units, never registers a
graph edge, and never calls a model transport: it reads a narrow projection of
`FactoryState`, does one bounded piece of work, and returns a typed channel
update that `FactoryState`'s declared reducers admit or reject.

The projection is the structural isolation boundary of spec section 9. A node is
handed exactly the state fields its catalogue row authorizes and nothing else, so
execution adjacency grants no context: a node physically cannot read a channel it
was not authorized to read, even though the graph hands the whole state in.

Expected failures are classified into `pending_failure` here; unexpected
exceptions deliberately propagate to the common node boundary that N20 wires,
because a node that swallows an unknown error would let the episode continue on
unproven state.
"""

from __future__ import annotations

import dataclasses
import hashlib
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from ..reducers import canonical_digest, canonical_json
from ..state import FACTORY_STATE_FIELDS, FIELD_REDUCER_CLASSES

__all__ = [
    "NodeError",
    "ExpectedFailure",
    "SystemFailure",
    "PrerequisitePause",
    "ConvergenceExhausted",
    "CatalogueViolation",
    "NodeSpec",
    "NODE_CATALOGUE",
    "OWNED_NODE_IDS",
    "COMMON_OUTPUT_CHANNELS",
    "FAILURE_CLASSES",
    "SYSTEM_CAUSES",
    "PAUSE_CAUSES",
    "EXHAUSTION_CAUSES",
    "project",
    "channel_default",
    "deterministic_node",
    "guard",
    "failure_record",
    "node_registry",
    "canonical_digest",
    "canonical_json",
    "require",
    "stream_id",
    "latest_candidate",
    "MODEL_CANDIDATE_KIND",
    "is_model_candidate",
    "candidate_payload",
    "candidate_field",
    "latest_model_candidate",
    "mint_version",
    "require_current_parent",
    "head_update",
    "check_record",
    "sha256_file",
    "contract_reference",
    "correlation_record",
    "worker_packet",
    "staged_dispatch",
]


class NodeError(Exception):
    """Base class for every typed deterministic-node fault."""


class CatalogueViolation(NodeError):
    """A node read or wrote a channel its frozen catalogue row does not authorize."""


class ExpectedFailure(NodeError):
    """A failure the catalogue classifies, which becomes a `pending_failure` record.

    Anything not derived from this class is unexpected by definition and is left
    to propagate: the common node boundary routes it to `SYSTEM_FAILURE` rather
    than letting a node decide that an unknown error was survivable.
    """

    failure_class = "system"

    def __init__(self, cause: str, message: str, evidence: Mapping[str, Any] | None = None):
        super().__init__(message)
        self.cause = cause
        self.evidence = dict(evidence or {})


class SystemFailure(ExpectedFailure):
    """A capability, authorization, tool, schema, integrity, identity, join,
    persistence, or log fault: never a product outcome."""

    failure_class = "system"


class PrerequisitePause(ExpectedFailure):
    """Exactly one named required external fact is unavailable.

    Only a named unavailable external fact may pause. A tool, transport, schema,
    or integrity fault raises :class:`SystemFailure` instead — spec section 2.4
    item 6 records that conflating the two is how a broken run previously
    reported itself as merely waiting.
    """

    failure_class = "pause"


class ConvergenceExhausted(ExpectedFailure):
    """A numeric attempt or repeated-fingerprint bound was reached before acceptance."""

    failure_class = "exhaustion"


FAILURE_CLASSES: tuple[str, ...] = ("system", "pause", "exhaustion")

SYSTEM_CAUSES: tuple[str, ...] = (
    "unhandled",
    "unexpected",
    "invalid_input",
    "identity",
    "integrity",
    "schema_contract",
    "capability",
    "authorization",
    "tool",
    "join",
    "persistence",
    "log",
)

PAUSE_CAUSES: tuple[str, ...] = ("required_external_fact_unavailable",)

EXHAUSTION_CAUSES: tuple[str, ...] = ("attempt_bound", "fingerprint_bound")

CAUSES_BY_CLASS: dict[str, tuple[str, ...]] = {
    "system": SYSTEM_CAUSES,
    "pause": PAUSE_CAUSES,
    "exhaustion": EXHAUSTION_CAUSES,
}

# Spec section 6.1: every node may classify a failure and every outgoing guard
# first reads that classification, so these two channels are authorized on every
# node in addition to its catalogue row.
COMMON_OUTPUT_CHANNELS: tuple[str, ...] = ("pending_failure", "pending_guard")


@dataclasses.dataclass(frozen=True, slots=True)
class NodeSpec:
    """One frozen row of the spec section 6.2 catalogue."""

    node_id: str
    module: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    failure_classes: tuple[str, ...]
    guards: tuple[str, ...]

    def __post_init__(self) -> None:
        for field in self.inputs:
            if field not in FACTORY_STATE_FIELDS:
                raise CatalogueViolation(f"{self.node_id}: unknown input channel {field!r}")
        for field in self.outputs:
            if field not in FACTORY_STATE_FIELDS:
                raise CatalogueViolation(f"{self.node_id}: unknown output channel {field!r}")
        for name in self.failure_classes:
            if name not in FAILURE_CLASSES:
                raise CatalogueViolation(f"{self.node_id}: unknown failure class {name!r}")
        if len(set(self.inputs)) != len(self.inputs):
            raise CatalogueViolation(f"{self.node_id}: duplicate input channel")
        if len(set(self.outputs)) != len(self.outputs):
            raise CatalogueViolation(f"{self.node_id}: duplicate output channel")


def _spec(
    node_id: str,
    module: str,
    *,
    inputs: Iterable[str],
    outputs: Iterable[str],
    failures: Iterable[str] = (),
    guards: Iterable[str] = (),
) -> NodeSpec:
    return NodeSpec(
        node_id=node_id,
        module=module,
        inputs=tuple(inputs),
        outputs=tuple(outputs),
        failure_classes=tuple(failures),
        guards=tuple(guards),
    )


_IDENTITY_FIELDS: tuple[str, ...] = (
    "contract_version",
    "run_id",
    "created_at",
    "engine_root",
    "curriculum_root",
    "active_manifest_path",
    "output_root",
    "mode",
    "requested_unit_id",
    "frozen_inputs",
    "frozen_digest",
    "frozen_executable_identities",
    "external_authorizations",
)


NODE_CATALOGUE: dict[str, NodeSpec] = {
    row.node_id: row
    for row in (
        _spec(
            "D00_BOOTSTRAP_EPISODE",
            "inputs",
            inputs=("invocation", "run_id", "frozen_digest", "terminal", "terminal_history"),
            outputs=("bootstrap_kind", "invocation"),
            failures=("system",),
            guards=("fresh", "resume", "recover_orphan"),
        ),
        _spec(
            "D00R_REVALIDATE_RESUME_IDENTITY",
            "inputs",
            inputs=("invocation", *_IDENTITY_FIELDS, "terminal_history"),
            outputs=("validated_recovery_envelope", "evidence_index_entries"),
            failures=("system",),
            guards=("resume_identity_proven",),
        ),
        _spec(
            "D01_VALIDATE_AND_FREEZE_INPUTS",
            "inputs",
            inputs=("invocation",),
            outputs=_IDENTITY_FIELDS,
            failures=("system",),
            guards=("inputs_frozen",),
        ),
        _spec(
            "D02_COMPILE_EFFECTIVE_RUN",
            "inputs",
            inputs=(
                "engine_root",
                "curriculum_root",
                "active_manifest_path",
                "mode",
                "requested_unit_id",
                "frozen_inputs",
            ),
            outputs=("effective_run",),
            failures=("system",),
            guards=("effective_run_compiled",),
        ),
        _spec(
            "D03_PROVE_CAPABILITIES",
            "inputs",
            inputs=(
                "invocation",
                "validated_recovery_envelope",
                "effective_run",
                "frozen_executable_identities",
                "external_authorizations",
                "frozen_digest",
                "run_id",
                "engine_root",
                "output_root",
            ),
            outputs=("capability_receipts",),
            failures=("system", "pause"),
            guards=("capabilities_proven", "prerequisite_unavailable"),
        ),
        _spec(
            "D04_INITIALIZE_OR_RESUME",
            "inputs",
            inputs=(
                "bootstrap_kind",
                "invocation",
                "validated_recovery_envelope",
                "capability_receipts",
                "effective_run",
                *_IDENTITY_FIELDS,
                "terminal_history",
                "artifact_heads",
                "attempt_counters",
                "cursor",
                "unit_status",
                "accepted_unit_receipts",
            ),
            outputs=(
                "episode_id",
                "checkpoint_thread_id",
                "checkpoint_namespace",
                "resume_from",
                "terminal_history",
                "artifact_heads",
                "attempt_counters",
                "cursor",
                "unit_status",
                "effective_run",
                *_IDENTITY_FIELDS,
            ),
            failures=("system",),
            guards=("fresh_initialized", "resume_imported"),
        ),
        _spec(
            "D92_REENTER_VALIDATED_FRONTIER",
            "inputs",
            inputs=(
                "resume_frontier",
                "artifact_heads",
                "attempt_counters",
                "model_execution_receipts",
                "activation_receipts",
                "capability_receipts",
                "external_authorizations",
            ),
            outputs=("evidence_index_entries", "pending_guard"),
            failures=("system",),
            guards=("deterministic_reentry", "incomplete_model_activation"),
        ),
        _spec(
            "D96_GRACEFUL_INTERRUPT_GATE",
            "inputs",
            inputs=(
                "invocation",
                "validated_recovery_envelope",
                "resume_frontier",
                "artifact_heads",
                "attempt_counters",
                "checkpoint_metadata",
                "evidence_index_entries",
                "selected_unit_id",
                "episode_id",
                "run_id",
            ),
            outputs=("terminal_candidate", "resume_frontier"),
            failures=("system",),
            guards=("interrupted",),
        ),
        _spec(
            "D05_SELECT_NEXT_UNIT",
            "sources",
            inputs=("effective_run", "cursor", "accepted_unit_receipts", "unit_status"),
            outputs=("selected_unit_id", "unit_status", "cursor"),
            failures=("system",),
            guards=("unit_selected", "manifest_exhausted"),
        ),
        _spec(
            "D06_COMPILE_SOURCE_REQUESTS",
            "sources",
            inputs=(
                "effective_run",
                "selected_unit_id",
                "source_admissions",
                "engine_root",
                "run_id",
                "episode_id",
                "external_authorizations",
            ),
            outputs=("source_requests", "source_denominators", "pending_packet"),
            failures=("pause",),
            guards=("discovery_fanout",),
        ),
        _spec(
            "D06B_RETRIEVE_SOURCE_CANDIDATES",
            "sources",
            inputs=(
                "selected_unit_id",
                "source_requests",
                "source_denominators",
                "source_discoveries",
                "external_authorizations",
                "effective_run",
                "run_id",
                "episode_id",
            ),
            outputs=("retrievals", "pending_packet"),
            failures=("system", "pause"),
            guards=("interpretation_fanout",),
        ),
        _spec(
            "D07_CORRELATE_AND_ADMIT_SOURCES",
            "sources",
            inputs=(
                "selected_unit_id",
                "source_requests",
                "source_denominators",
                "source_discoveries",
                "retrievals",
                "source_interpretations",
                "effective_run",
                "engine_root",
                "run_id",
                "episode_id",
            ),
            outputs=("source_admissions", "source_join_evidence", "pending_packet"),
            failures=("system",),
            guards=("sources_admitted", "prerequisite_unresolved"),
        ),
        _spec(
            "D30_CLASSIFY_PREREQUISITE",
            "sources",
            inputs=(
                "selected_unit_id",
                "pending_failure",
                "source_requests",
                "source_denominators",
                "retrievals",
                "attempt_counters",
            ),
            outputs=("evidence_index_entries", "terminal_candidate", "resume_frontier"),
            failures=("system",),
            guards=("prerequisite_pause",),
        ),
        _spec(
            "D08_VALIDATE_DOMAIN",
            "domain",
            inputs=(
                "selected_unit_id",
                "effective_run",
                "artifact_versions",
                "artifact_heads",
                "source_admissions",
                "engine_root",
                "run_id",
                "episode_id",
            ),
            outputs=(
                "artifact_versions",
                "artifact_heads",
                "deterministic_checks",
                "pending_packet",
            ),
            failures=("system",),
            guards=("domain_admitted", "domain_repairable"),
        ),
        _spec(
            "D09_VALIDATE_CONTENT",
            "content",
            inputs=(
                "selected_unit_id",
                "effective_run",
                "artifact_versions",
                "artifact_heads",
                "engine_root",
            ),
            outputs=("artifact_versions", "artifact_heads", "deterministic_checks"),
            failures=("system",),
            guards=("content_admitted", "content_repairable"),
        ),
        _spec(
            "D10_COMPILE_VISUAL_BRIEFS",
            "visuals",
            inputs=(
                "selected_unit_id",
                "artifact_heads",
                "artifact_versions",
                "engine_root",
                "run_id",
                "episode_id",
            ),
            outputs=("visual_briefs", "visual_denominators", "pending_packet"),
            failures=("system",),
            guards=("deterministic_visual_fanout", "no_deterministic_visuals"),
        ),
        _spec(
            "D11_CREATE_DETERMINISTIC_VISUALS",
            "visuals",
            inputs=("pending_packet",),
            outputs=("visual_results",),
            failures=("system",),
            guards=("visual_produced",),
        ),
        _spec(
            "D12_VISUAL_BARRIER_AND_JOIN",
            "visuals",
            inputs=(
                "selected_unit_id",
                "visual_denominators",
                "visual_briefs",
                "visual_results",
                "artifact_versions",
                "artifact_heads",
                "run_id",
                "episode_id",
            ),
            outputs=(
                "visual_join_evidence",
                "artifact_versions",
                "artifact_heads",
                "deterministic_checks",
                "pending_packet",
            ),
            failures=("system",),
            guards=("model_visual_fanout", "visuals_admitted", "visuals_repairable"),
        ),
        _spec(
            "D13_RENDER_UNIT",
            "render",
            inputs=("selected_unit_id", "artifact_heads", "engine_root", "output_root"),
            outputs=("artifact_versions", "deterministic_checks"),
            failures=("system",),
            guards=("unit_rendered",),
        ),
        _spec(
            "D14_INVENTORY_AND_INSPECT_UNIT_PAGES",
            "render",
            inputs=("selected_unit_id", "artifact_heads", "artifact_versions", "output_root"),
            outputs=("unit_page_inventories", "unit_page_inspections", "deterministic_checks"),
            failures=("system",),
            guards=("pages_inspected", "layout_repairable"),
        ),
        _spec(
            "D15_FREEZE_UNIT_REVIEW_PACKET",
            "review",
            inputs=(
                "selected_unit_id",
                "artifact_heads",
                "unit_page_inventories",
                "unit_page_inspections",
                "deterministic_checks",
                "source_admissions",
                "artifact_versions",
                "engine_root",
                "run_id",
                "episode_id",
            ),
            outputs=("review_packets", "pending_packet"),
            failures=("system",),
            guards=("review_packet_frozen",),
        ),
        _spec(
            "D98_WRITE_TERMINAL",
            "terminal",
            inputs=(
                "terminal_candidate",
                "terminal",
                "terminal_history",
                "episode_id",
                "run_id",
                "mode",
                "requested_unit_id",
                "effective_run",
                "accepted_unit_receipts",
                "final_release_audits",
                "workbook_head",
                "artifact_heads",
                "attempt_counters",
                "failure_fingerprints",
                "checkpoint_metadata",
                "evidence_index_entries",
                "pending_failure",
                "resume_frontier",
                "output_root",
            ),
            outputs=("terminal", "terminal_history"),
            failures=("system",),
            guards=("terminated",),
        ),
    )
}

OWNED_NODE_IDS: tuple[str, ...] = tuple(NODE_CATALOGUE)


_DEFAULT_BY_REDUCER_CLASS: dict[str, Callable[[], Any]] = {
    "write_once": lambda: None,
    "replace_current": lambda: None,
    "write_episode_terminal_once": lambda: None,
    "append_unique": list,
    "union_disjoint": dict,
    "advance_head": dict,
    "monotonic_status": dict,
    "monotonic_max": dict,
    "accept_once": dict,
}


def channel_default(field: str) -> Any:
    """The empty value of ``field``, derived from its declared reducer class."""

    return _DEFAULT_BY_REDUCER_CLASS[FIELD_REDUCER_CLASSES[field]]()


def project(node_id: str, state: Mapping[str, Any]) -> dict[str, Any]:
    """Build the narrow authorized projection of ``state`` for ``node_id``.

    Fields absent from ``state`` take their channel's empty value, so a node
    body never distinguishes "never written" from "written empty" and never
    branches on a key it was not authorized to see.
    """

    spec = NODE_CATALOGUE[node_id]
    projection: dict[str, Any] = {}
    for field in spec.inputs:
        value = state.get(field)
        projection[field] = channel_default(field) if value is None else value
    return projection


def failure_record(
    node_id: str,
    error: ExpectedFailure,
    *,
    at: str | None = None,
) -> dict[str, Any]:
    """Normalize a classified failure into the one `pending_failure` shape."""

    failure_class = error.failure_class
    permitted = CAUSES_BY_CLASS[failure_class]
    if error.cause not in permitted:
        raise CatalogueViolation(
            f"{node_id}: cause {error.cause!r} is not declared for class {failure_class!r}"
        )
    record: dict[str, Any] = {
        "node": node_id,
        "class": failure_class,
        "cause": error.cause,
        "message": str(error),
        "evidence": error.evidence,
    }
    if at is not None:
        record["at"] = at
    return record


def guard(node_id: str, value: str, **detail: Any) -> dict[str, Any]:
    """Build the `pending_guard` record a routing function reads.

    The node states its deterministic classification; `routing.py` (N20) decides
    the destination. Keeping those separate is why a node body can never name an
    edge.
    """

    spec = NODE_CATALOGUE[node_id]
    if value not in spec.guards:
        raise CatalogueViolation(f"{node_id}: undeclared guard value {value!r}")
    return {"node": node_id, "value": value, "detail": detail}


def require(condition: bool, cause: str, message: str, **evidence: Any) -> None:
    """Fail closed with a typed system failure when ``condition`` does not hold."""

    if not condition:
        raise SystemFailure(cause, message, evidence)


def deterministic_node(node_id: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Bind a bounded callable to its frozen catalogue row.

    The wrapper narrows state to the authorized projection, rejects any update
    naming an unauthorized channel, and converts a classified
    :class:`ExpectedFailure` into `pending_failure`. Every other exception is
    re-raised untouched.
    """

    spec = NODE_CATALOGUE[node_id]
    authorized = frozenset(spec.outputs) | frozenset(COMMON_OUTPUT_CHANNELS)

    def decorate(body: Callable[..., Any]) -> Callable[..., Any]:
        def node(state: Mapping[str, Any], runtime_context: Any = None) -> dict[str, Any]:
            projection = project(node_id, state)
            try:
                update = body(projection, runtime_context)
            except ExpectedFailure as error:
                # Spec 6.1: every outgoing guard reads `pending_failure` first, so a
                # classified failure clears any stale routing classification.
                #
                # A terminal_candidate is built here too, not left for some later
                # node to supply: `_failure_destination` (routing.py) routes
                # straight to D98_WRITE_TERMINAL the moment `pending_failure` is
                # truthy, with no classifier hop in between for a deterministic
                # node's failure (unlike a model node's, which D91 gets to shape
                # first). Without one, D98's own independent revalidation always
                # rejected a bare `None` candidate as "not a JSON object" --
                # discarding the real, already-classified failure into an
                # uninformative generic rejection. The same gap, and the same fix,
                # as graph.py's `_boundary` (N40V7-F12): shape matches every other
                # SYSTEM_FAILURE writer exactly. `state` here is the full incoming
                # state, before `project()` narrows it to this node's own
                # projection, so `artifact_heads`/`evidence_index_entries` are
                # still reachable.
                full_state = state if isinstance(state, Mapping) else {}
                artifact_heads = full_state.get("artifact_heads") or {}
                return {
                    "pending_failure": failure_record(node_id, error),
                    "pending_guard": None,
                    "terminal_candidate": {
                        "kind": "SYSTEM_FAILURE",
                        "failure": {"class": error.failure_class, "cause": error.cause},
                        "node": node_id,
                        "safe_heads": {
                            stream: head.get("hash")
                            for stream, head in sorted(artifact_heads.items())
                            if isinstance(head, dict)
                        },
                        "audit_high_water_mark": len(full_state.get("evidence_index_entries") or []),
                    },
                }
            if not isinstance(update, dict):
                raise CatalogueViolation(
                    f"{node_id}: node body returned {type(update).__name__}, expected a dict update"
                )
            unauthorized = sorted(set(update) - authorized)
            if unauthorized:
                raise CatalogueViolation(
                    f"{node_id}: update writes unauthorized channels {unauthorized}"
                )
            return update

        node.__name__ = node_id
        node.__qualname__ = node_id
        node.__doc__ = body.__doc__
        node.node_id = node_id  # type: ignore[attr-defined]
        node.node_spec = spec  # type: ignore[attr-defined]
        node.node_body = body  # type: ignore[attr-defined]
        return node

    return decorate


def stream_id(unit_id: str, channel: str) -> str:
    """The one artifact-stream identifier convention for head and version keys."""

    return f"units/{unit_id}/{channel}"


def latest_candidate(
    artifact_versions: Iterable[Mapping[str, Any]], stream: str
) -> dict[str, Any] | None:
    """The highest-version candidate record on ``stream``, or None."""

    candidates = [
        dict(record)
        for record in artifact_versions
        if isinstance(record, Mapping) and record.get("stream") == stream
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda record: record.get("version", 0))


# The `record_kind` a model adapter stamps on its pre-admission descriptor. Such a
# record carries the model's own output under `payload` and deliberately carries no
# `version`/`hash` pair, because spec 2.4 makes admission code-owned: the version a
# model artifact enters state under is minted here, by the node that validated it.
MODEL_CANDIDATE_KIND = "model_candidate"


def is_model_candidate(record: Any) -> bool:
    """True for a pre-admission model candidate descriptor."""

    return isinstance(record, Mapping) and record.get("record_kind") == MODEL_CANDIDATE_KIND


def candidate_payload(record: Mapping[str, Any], label: str) -> dict[str, Any]:
    """The model's own output off a pre-admission candidate record."""

    payload = record.get("payload")
    require(isinstance(payload, Mapping), "schema_contract", f"{label} carries no candidate payload")
    return dict(payload)


def candidate_field(record: Mapping[str, Any], field: str, default: Any = None) -> Any:
    """A lineage field off a record, falling back to a model candidate's payload.

    Every model job schema is closed, so a payload can never carry an admission
    field; the fallback can only reach lineage the projection itself declared.
    """

    if field in record:
        return record[field]
    if is_model_candidate(record):
        payload = record.get("payload")
        if isinstance(payload, Mapping) and field in payload:
            return payload[field]
    return default


def latest_model_candidate(
    artifact_versions: Iterable[Mapping[str, Any]], *, channel: str, unit_id: str
) -> dict[str, Any] | None:
    """The newest pre-admission model candidate on one unit's channel, or None."""

    matches = [
        dict(record)
        for record in artifact_versions
        if is_model_candidate(record)
        and record.get("channel") == channel
        and record.get("unit_id") == unit_id
    ]
    return matches[-1] if matches else None


def mint_version(
    candidate: Mapping[str, Any],
    heads: Mapping[str, Any],
    stream: str,
    *,
    body: Mapping[str, Any],
    **lineage: Any,
) -> dict[str, Any]:
    """Mint the versioned artifact record a validated model candidate authorizes.

    Version and parent are `advance_head`'s own rule (the current head's successor,
    parented on the current head's hash, genesis at version 1 with a null parent),
    and the hash is the canonical digest of the body this node derived — never a
    value read off the model's record.
    """

    current = heads.get(stream) if isinstance(heads, Mapping) else None
    current = current if isinstance(current, Mapping) else {}
    record = {
        "stream": stream,
        "version": int(current.get("version", 0)) + 1,
        "parent_hash": current.get("hash"),
        "hash": canonical_digest(body),
        "body": dict(body),
        "minted_by": "deterministic_admission",
        "candidate_key": candidate.get("key"),
        "candidate_sha256": candidate.get("candidate_sha256"),
        "attempt": int(candidate.get("attempt", 1)),
    }
    record.update(lineage)
    record["key"] = canonical_digest({"stream": stream, "hash": record["hash"]})
    return record


def require_current_parent(
    candidate: Mapping[str, Any], heads: Mapping[str, Any], stream: str
) -> None:
    """Fail closed unless ``candidate`` descends from the current head of ``stream``.

    This is the stale-parent gate. `advance_head` would also reject the write,
    but by then the node has already run its checks and would report a PASS
    against bytes that are no longer current — so the check happens first.
    """

    current = heads.get(stream)
    current_hash = current.get("hash") if isinstance(current, Mapping) else None
    current_version = current.get("version", 0) if isinstance(current, Mapping) else 0
    parent_hash = candidate.get("parent_hash")
    version = candidate.get("version")
    if parent_hash != current_hash:
        raise SystemFailure(
            "integrity",
            f"candidate on {stream} declares parent {parent_hash!r}, "
            f"which is not the current head {current_hash!r}",
            {"stream": stream, "declared_parent": parent_hash, "current_head": current_hash},
        )
    if version != current_version + 1:
        raise SystemFailure(
            "integrity",
            f"candidate on {stream} is version {version!r}, expected {current_version + 1}",
            {"stream": stream, "version": version, "expected": current_version + 1},
        )


def head_update(candidate: Mapping[str, Any], stream: str) -> dict[str, Any]:
    """The `advance_head` update a validated candidate authorizes."""

    for field in ("version", "parent_hash", "hash"):
        if field not in candidate:
            raise SystemFailure(
                "schema_contract",
                f"candidate on {stream} has no {field!r}",
                {"stream": stream},
            )
    return {
        stream: {
            "version": candidate["version"],
            "parent_hash": candidate["parent_hash"],
            "hash": candidate["hash"],
        }
    }


def check_record(
    *,
    scope: str,
    owner: str,
    head_hash: str,
    check_id: str,
    attempt: int,
    result: str,
    detail: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """One `deterministic_checks` entry under the frozen correlation key."""

    if result not in ("PASS", "FAIL"):
        raise CatalogueViolation(f"check {check_id!r}: result must be PASS or FAIL, got {result!r}")
    return {
        "scope": scope,
        "owner": owner,
        "head_hash": head_hash,
        "check_id": check_id,
        "attempt": attempt,
        "result": result,
        "detail": dict(detail or {}),
    }


def sha256_file(path: Path) -> str:
    """The sha256 of a file's current bytes, read incrementally."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def contract_reference(engine_root: Any, relative: str) -> dict[str, Any]:
    """Name one frozen engine-root contract file by path and current bytes."""

    root = Path(str(engine_root)).resolve()
    path = (root / relative).resolve()
    require(
        root in path.parents,
        "integrity",
        f"engine contract {relative!r} escapes the engine root",
        path=str(path),
    )
    require(
        path.is_file(),
        "schema_contract",
        f"engine contract {relative!r} is missing",
        path=str(path),
    )
    return {"path": relative, "sha256": sha256_file(path)}


def correlation_record(run_id: Any, episode_id: Any, key: str | None = None) -> dict[str, Any]:
    """The correlation every worker dispatch carries (spec section 10).

    A fan-out member additionally carries the code-computed `correlation_key`
    that binds it to exactly one denominator slot.
    """

    require(
        isinstance(run_id, str) and bool(run_id),
        "invalid_input",
        "a worker dispatch requires the frozen run identity",
    )
    require(
        isinstance(episode_id, str) and bool(episode_id),
        "invalid_input",
        "a worker dispatch requires the current episode identity",
    )
    record = {"run_id": run_id, "episode_id": episode_id}
    if key is not None:
        require(
            isinstance(key, str) and bool(key),
            "invalid_input",
            "a fan-out member requires a non-empty correlation key",
        )
        record["correlation_key"] = key
    return record


def worker_packet(
    *,
    run_id: Any,
    episode_id: Any,
    correlation_key: str,
    projection: Mapping[str, Any],
    **extra: Any,
) -> dict[str, Any]:
    """One bounded worker packet: its correlation and its spec section 9 projection.

    No `reservation` is staged here. D90 mints one per member from this packet's
    correlation and attaches it before dispatch, because the attempt counter must
    be committed by the one node that owns it.
    """

    return {
        "correlation": correlation_record(run_id, episode_id, correlation_key),
        **dict(projection),
        **extra,
    }


def staged_dispatch(destination: str, packets: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The `pending_packet` value a dispatching node persists before any dispatch."""

    require(bool(packets), "join", f"no worker packet was staged for {destination}")
    return {"dispatch": destination, "packets": [dict(packet) for packet in packets]}


def node_registry() -> dict[str, Callable[..., Any]]:
    """Resolve every owned node body by stable ID.

    Imported lazily so this package's shared primitives can be imported by the
    node modules themselves without a circular import.
    """

    from . import content, domain, inputs, render, review, sources, terminal, visuals

    modules = {
        "inputs": inputs,
        "sources": sources,
        "domain": domain,
        "content": content,
        "visuals": visuals,
        "render": render,
        "review": review,
        "terminal": terminal,
    }
    registry: dict[str, Callable[..., Any]] = {}
    for node_id, spec in NODE_CATALOGUE.items():
        module = modules[spec.module]
        callable_ = getattr(module, node_id, None)
        if callable_ is None:
            raise CatalogueViolation(f"{node_id} is not implemented in nodes/{spec.module}.py")
        registry[node_id] = callable_
    return registry
