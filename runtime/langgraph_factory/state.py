"""Typed Plan 26 factory state, graph input/output schemas, and runtime context.

`FactoryState` is the complete persisted state of spec section 5.2. Every field
declares exactly one reducer through ``typing.Annotated``, which is the channel
convention `StateGraph` reads structurally; no LangGraph import is needed to
declare it. Persisted values are JSON-compatible and content-addressed only.

`RuntimeContext` is deliberately outside that state: it holds opened services
and is never checkpointed, never serialized, and never carries a model client
or routing authority.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Any, TypedDict, get_type_hints

from .reducers import (
    accept_once,
    advance_head,
    append_unique,
    append_unique_by,
    monotonic_max,
    monotonic_status,
    replace_current,
    union_disjoint,
    write_episode_terminal_once,
    write_once,
)

__all__ = [
    "Record",
    "RecordList",
    "RecordMap",
    "FactoryInput",
    "FactoryState",
    "FactoryOutput",
    "RuntimeContext",
    "RuntimeContextViolation",
    "StateInventoryError",
    "FACTORY_STATE_FIELDS",
    "FACTORY_INPUT_FIELDS",
    "FACTORY_OUTPUT_FIELDS",
    "FIELD_REDUCERS",
    "FIELD_REDUCER_CLASSES",
    "RUNTIME_CONTEXT_FIELDS",
    "FORBIDDEN_RUNTIME_CONTEXT_FIELDS",
    "validate_state_inventory",
    "reducer_for",
]

Record = dict[str, Any]
RecordList = list[Record]
RecordMap = dict[str, Record]


class StateInventoryError(Exception):
    """The supplied state does not match the frozen spec section 5.2 inventory."""


class RuntimeContextViolation(Exception):
    """A runtime context was constructed with a forbidden field or value."""


# `deterministic_checks` is the one field whose correlation key the spec names
# explicitly (section 5.2); every other append-unique channel keys on the
# writer-computed `key` string.
_DETERMINISTIC_CHECK_APPEND = append_unique_by("scope", "owner", "head_hash", "check_id", "attempt")


class FactoryInput(TypedDict):
    """Graph input schema: the one envelope `run_curriculum` supplies to D00."""

    invocation: Record


class FactoryState(TypedDict, total=False):
    """Complete persisted state (spec section 5.2), one declared reducer per field.

    Every `write_once` channel is declared `X | None`. LangGraph seeds a reduced
    channel by calling its annotated type when that type is zero-arg constructible,
    so `Annotated[str, write_once]` would start at `''` rather than unset and
    `write_once` would reject the channel's own first write; a union is not
    constructible, so the channel stays unset until something writes it.
    """

    # Episode bootstrap
    invocation: Annotated[Record | None, replace_current]
    validated_recovery_envelope: Annotated[Record | None, replace_current]
    bootstrap_kind: Annotated[str | None, write_once]

    # Immutable run identity
    contract_version: Annotated[str | None, write_once]
    run_id: Annotated[str | None, write_once]
    created_at: Annotated[str | None, write_once]
    engine_root: Annotated[str | None, write_once]
    curriculum_root: Annotated[str | None, write_once]
    active_manifest_path: Annotated[str | None, write_once]
    output_root: Annotated[str | None, write_once]
    mode: Annotated[str | None, write_once]
    requested_unit_id: Annotated[str | None, write_once]

    # Frozen inputs and authorization
    frozen_inputs: Annotated[RecordList | None, write_once]
    frozen_digest: Annotated[str | None, write_once]
    frozen_executable_identities: Annotated[RecordList | None, write_once]
    external_authorizations: Annotated[RecordList | None, write_once]
    effective_run: Annotated[Record | None, write_once]

    # Episode and resume frontier
    episode_id: Annotated[str | None, write_once]
    checkpoint_thread_id: Annotated[str | None, write_once]
    checkpoint_namespace: Annotated[str | None, write_once]
    resume_from: Annotated[Record | None, write_once]
    resume_frontier: Annotated[Record | None, replace_current]

    # Unit scheduling
    cursor: Annotated[dict[str, int], monotonic_max]
    selected_unit_id: Annotated[str | None, replace_current]
    unit_status: Annotated[dict[str, str], monotonic_status]

    # Sources
    source_requests: Annotated[RecordList, append_unique]
    source_denominators: Annotated[RecordMap, union_disjoint]
    source_discoveries: Annotated[RecordMap, union_disjoint]
    retrievals: Annotated[RecordMap, union_disjoint]
    source_interpretations: Annotated[RecordMap, union_disjoint]
    source_admissions: Annotated[RecordList, append_unique]
    source_join_evidence: Annotated[RecordList, append_unique]

    # Artifacts and deterministic checks
    artifact_versions: Annotated[RecordList, append_unique]
    artifact_heads: Annotated[RecordMap, advance_head]
    deterministic_checks: Annotated[RecordList, _DETERMINISTIC_CHECK_APPEND]

    # Visuals
    visual_briefs: Annotated[RecordList, append_unique]
    visual_denominators: Annotated[RecordMap, union_disjoint]
    visual_results: Annotated[RecordMap, union_disjoint]
    visual_join_evidence: Annotated[RecordList, append_unique]

    # Unit rendering and review
    unit_page_inventories: Annotated[RecordList, append_unique]
    unit_page_inspections: Annotated[RecordList, append_unique]
    review_packets: Annotated[RecordList, append_unique]
    unit_reviews: Annotated[RecordList, append_unique]

    # Targeted repair
    finding_partitions: Annotated[RecordList, append_unique]
    repair_requests: Annotated[RecordList, append_unique]
    invalidations: Annotated[RecordList, append_unique]
    retest_plans: Annotated[RecordList, append_unique]
    retest_results: Annotated[RecordList, append_unique]
    attempt_counters: Annotated[dict[str, int], monotonic_max]
    failure_fingerprints: Annotated[RecordList, append_unique]

    # Unit acceptance
    accepted_unit_receipts: Annotated[RecordMap, accept_once]
    accepted_unit_checkpoint_receipts: Annotated[RecordList, append_unique]

    # Workbook
    workbook_versions: Annotated[RecordList, append_unique]
    workbook_head: Annotated[RecordMap, advance_head]
    workbook_coverage: Annotated[RecordList, append_unique]
    workbook_page_inventories: Annotated[RecordList, append_unique]
    workbook_page_inspections: Annotated[RecordList, append_unique]
    workbook_review_packets: Annotated[RecordList, append_unique]
    workbook_reviews: Annotated[RecordList, append_unique]
    workbook_finding_partitions: Annotated[RecordList, append_unique]
    workbook_repair_requests: Annotated[RecordList, append_unique]
    workbook_invalidations: Annotated[RecordList, append_unique]
    workbook_retests: Annotated[RecordList, append_unique]
    final_release_audits: Annotated[RecordList, append_unique]

    # Execution evidence
    route_decisions: Annotated[RecordList, append_unique]
    model_execution_receipts: Annotated[RecordList, append_unique]
    activation_receipts: Annotated[RecordList, append_unique]
    capability_receipts: Annotated[RecordList, append_unique]
    evidence_index_entries: Annotated[RecordList, append_unique]
    log_audit_receipts: Annotated[RecordList, append_unique]
    checkpoint_metadata: Annotated[RecordList, append_unique]

    # Ephemeral, code-owned routing fields
    pending_failure: Annotated[Record | None, replace_current]
    pending_packet: Annotated[Record | None, replace_current]
    pending_guard: Annotated[Record | None, replace_current]
    terminal_candidate: Annotated[Record | None, replace_current]

    # Terminal ledger
    terminal: Annotated[Record | None, write_episode_terminal_once]
    terminal_history: Annotated[RecordList, append_unique]


class FactoryOutput(TypedDict, total=False):
    """Graph output schema: a projection of persisted channels, never new state.

    `run_curriculum` derives the printed result's `accepted_receipt`,
    `release_receipt`, `checkpoint_id`, and `evidence_index_hash` from
    `accepted_unit_receipts`, `final_release_audits`, `checkpoint_metadata`, and
    `evidence_index_entries` respectively; none of them is a separate channel.
    """

    contract_version: str
    run_id: str
    episode_id: str
    mode: str
    requested_unit_id: str | None
    output_root: str
    terminal: Record | None
    accepted_unit_receipts: RecordMap
    final_release_audits: RecordList
    checkpoint_metadata: RecordList
    evidence_index_entries: RecordList


FACTORY_STATE_FIELDS: tuple[str, ...] = tuple(FactoryState.__annotations__)
FACTORY_INPUT_FIELDS: tuple[str, ...] = tuple(FactoryInput.__annotations__)
FACTORY_OUTPUT_FIELDS: tuple[str, ...] = tuple(FactoryOutput.__annotations__)


def _declared_reducers() -> dict[str, Callable[[Any, Any], Any]]:
    hints = get_type_hints(FactoryState, include_extras=True)
    declared: dict[str, Callable[[Any, Any], Any]] = {}
    for field in FACTORY_STATE_FIELDS:
        metadata = [item for item in getattr(hints[field], "__metadata__", ()) if callable(item)]
        if len(metadata) != 1:
            raise StateInventoryError(
                f"field {field!r} must declare exactly one reducer, found {len(metadata)}"
            )
        declared[field] = metadata[0]
    return declared


FIELD_REDUCERS: dict[str, Callable[[Any, Any], Any]] = _declared_reducers()

FIELD_REDUCER_CLASSES: dict[str, str] = {
    field: getattr(reducer, "reducer_class") for field, reducer in FIELD_REDUCERS.items()
}


def reducer_for(field: str) -> Callable[[Any, Any], Any]:
    """Return the one declared reducer for ``field``, rejecting unknown fields."""

    try:
        return FIELD_REDUCERS[field]
    except KeyError:
        raise StateInventoryError(f"unknown state field {field!r}") from None


def validate_state_inventory(fields: object) -> None:
    """Reject any state whose field set is not exactly the spec section 5.2 set."""

    if isinstance(fields, dict):
        present = set(fields)
    else:
        present = set(fields)  # type: ignore[arg-type]
    expected = set(FACTORY_STATE_FIELDS)
    missing = sorted(expected - present)
    unknown = sorted(present - expected)
    if missing or unknown:
        raise StateInventoryError(
            f"state inventory mismatch: missing={missing} unknown={unknown}"
        )


FORBIDDEN_RUNTIME_CONTEXT_FIELDS: frozenset[str] = frozenset(
    {
        "model_client",
        "model_clients",
        "model",
        "llm",
        "chat_model",
        "router",
        "routing_authority",
        "routing",
        "selector",
        "state",
    }
)


@dataclasses.dataclass(frozen=True, slots=True)
class RuntimeContext:
    """Opened services for one invocation. Never checkpointed, never serialized.

    Holds exactly the services spec section 5.2 permits. A model client or any
    routing authority is forbidden here: model transmission is the transport
    boundary's job and routing is code-owned, so putting either in the context
    would let a node reach a model or a route without going through them.
    """

    engine_root: Path
    output_root: Path
    path_guard: object
    evidence_service: object
    transport_registry: object
    source_retriever: object
    signal_token: object
    clock: Callable[[], Any]

    def __post_init__(self) -> None:
        declared = {field.name for field in dataclasses.fields(self)}
        forbidden = declared & FORBIDDEN_RUNTIME_CONTEXT_FIELDS
        if forbidden:
            raise RuntimeContextViolation(
                f"runtime context must not hold a model client or routing authority: "
                f"{sorted(forbidden)}"
            )
        for name in sorted(FORBIDDEN_RUNTIME_CONTEXT_FIELDS):
            if hasattr(self, name):
                raise RuntimeContextViolation(
                    f"runtime context must not expose attribute {name!r}"
                )
        for name in ("engine_root", "output_root"):
            if not isinstance(getattr(self, name), Path):
                raise RuntimeContextViolation(f"{name} must be a pathlib.Path")
        for name in ("path_guard", "evidence_service", "transport_registry",
                     "source_retriever", "signal_token"):
            if getattr(self, name) is None:
                raise RuntimeContextViolation(f"{name} service is required")
        if not callable(self.clock):
            raise RuntimeContextViolation("clock must be callable")


RUNTIME_CONTEXT_FIELDS: tuple[str, ...] = tuple(
    field.name for field in dataclasses.fields(RuntimeContext)
)
