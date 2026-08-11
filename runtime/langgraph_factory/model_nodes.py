"""The eight model job adapters (spec 6.3) plus D90/D91 attempt bookkeeping.

Each adapter is thin: it proves a D90 reservation exists, materializes exactly one
authorized projection from spec section 9's allowlist, invokes the frozen N13
transport once, validates the structured candidate against the declared boundary,
and returns a typed pre-admission state update.

A model node can never admit, merge, route, accept, resume, or terminate. It writes
only the candidate channels in ``MODEL_NODE_WRITABLE_FIELDS``; every head, accepted
receipt, and terminal channel is code-owned by a deterministic node.
"""

from __future__ import annotations

import ast
import copy
import dataclasses
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import jsonschema

from . import transport as tp
from .reducers import canonical_digest
from .state import RuntimeContext

__all__ = [
    "MODEL_NODE_IDS",
    "MODEL_NODE_FAMILIES",
    "MODEL_NODE_ATTEMPT_LIMIT",
    "MODEL_NODE_WRITABLE_FIELDS",
    "FORBIDDEN_MODEL_NODE_FIELDS",
    "ADMISSION_OWNED_CANDIDATE_FIELDS",
    "PROJECTION_SPECS",
    "ProjectionSpec",
    "ModelNodeContext",
    "ModelNodeError",
    "ProjectionViolation",
    "RepairBoundaryViolation",
    "PageDenominatorViolation",
    "CandidateRejected",
    "AttemptNotReserved",
    "FamilyViolation",
    "build_projection",
    "build_model_node_context",
    "build_test_model_node_context",
    "build_model_nodes",
    "reserve_model_attempt",
    "classify_model_failure",
    "MODEL_BOOKKEEPING_NODES",
    "D90_RESERVE_MODEL_ATTEMPT",
    "D91_CLASSIFY_MODEL_FAILURE",
    "m01_research_unit_sources",
    "m01_discover_unit_sources",
    "m01_interpret_unit_sources",
    "m02_create_unit_domain_data",
    "m03_write_unit_content",
    "m04_create_unit_visuals",
    "m05_review_actual_unit",
    "m06_repair_named_unit_artifact",
    "m07_review_actual_workbook",
    "m08_repair_named_workbook_defect",
]


# --------------------------------------------------------------------------- errors


class ModelNodeError(RuntimeError):
    """A model node boundary was violated. Never retried by this module."""


class ProjectionViolation(ModelNodeError):
    """The dispatching deterministic node offered an inadmissible packet."""


class RepairBoundaryViolation(ProjectionViolation):
    """A repair packet or candidate reaches outside its one declared boundary."""


class PageDenominatorViolation(ProjectionViolation):
    """A review packet or finding set does not match the exact frozen page set."""


class CandidateRejected(ModelNodeError):
    """A structured model candidate failed schema, control-field, or scope validation."""


class AttemptNotReserved(ModelNodeError):
    """No D90 reservation was committed before this dispatch."""


class FamilyViolation(ModelNodeError):
    """A route executed in a family the frozen registry does not authorize."""


# ------------------------------------------------------------------------ constants

MODEL_NODE_IDS: tuple[str, ...] = (
    "M01_RESEARCH_UNIT_SOURCES",
    "M02_CREATE_UNIT_DOMAIN_DATA",
    "M03_WRITE_UNIT_CONTENT",
    "M04_CREATE_UNIT_VISUALS",
    "M05_REVIEW_ACTUAL_UNIT",
    "M06_REPAIR_NAMED_UNIT_ARTIFACT",
    "M07_REVIEW_ACTUAL_WORKBOOK",
    "M08_REPAIR_NAMED_WORKBOOK_DEFECT",
)

MODEL_NODE_FAMILIES: Mapping[str, str] = {
    "M01_RESEARCH_UNIT_SOURCES": tp.AUTHORING_FAMILY,
    "M02_CREATE_UNIT_DOMAIN_DATA": tp.AUTHORING_FAMILY,
    "M03_WRITE_UNIT_CONTENT": tp.AUTHORING_FAMILY,
    "M04_CREATE_UNIT_VISUALS": tp.AUTHORING_FAMILY,
    "M05_REVIEW_ACTUAL_UNIT": tp.REVIEW_FAMILY,
    "M06_REPAIR_NAMED_UNIT_ARTIFACT": tp.AUTHORING_FAMILY,
    "M07_REVIEW_ACTUAL_WORKBOOK": tp.REVIEW_FAMILY,
    "M08_REPAIR_NAMED_WORKBOOK_DEFECT": tp.AUTHORING_FAMILY,
}

# One original activation plus at most one D91-authorized retry, matching the frozen
# per-route `retry_limit: 1`. D91 may never exceed this.
MODEL_NODE_ATTEMPT_LIMIT = 2

RESERVATION_KIND = "model_attempt_reservation"

MODEL_NODE_WRITABLE_FIELDS: frozenset[str] = frozenset({
    "source_discoveries",
    "source_interpretations",
    "artifact_versions",
    "visual_results",
    "unit_reviews",
    "workbook_reviews",
    "workbook_versions",
    "model_execution_receipts",
    "activation_receipts",
    "pending_failure",
})

FORBIDDEN_MODEL_NODE_FIELDS: frozenset[str] = frozenset({
    "artifact_heads",
    "workbook_head",
    "accepted_unit_receipts",
    "accepted_unit_checkpoint_receipts",
    "terminal",
    "terminal_history",
    "terminal_candidate",
    "unit_status",
    "source_admissions",
    "deterministic_checks",
    "final_release_audits",
    "pending_guard",
    "resume_frontier",
    "cursor",
})

ADMISSION_OWNED_CANDIDATE_FIELDS: frozenset[str] = frozenset({
    "version", "hash", "parent_hash",
})

RESERVE_ATTEMPT_WRITABLE_FIELDS: frozenset[str] = frozenset({
    "attempt_counters", "activation_receipts", "pending_guard", "pending_packet",
})

CLASSIFY_FAILURE_WRITABLE_FIELDS: frozenset[str] = frozenset({
    "failure_fingerprints", "pending_failure", "pending_guard", "terminal_candidate",
})

# Transient or malformed transport outcomes: the only class D91 may send back to D90.
RETRYABLE_FAILURE_CLASSES: frozenset[str] = frozenset({
    "empty_result",
    "fenced_result",
    "malformed_json",
    "trailing_material",
    "result_is_not_an_object",
    "duplicate_json_key",
    "non_finite_json_constant",
    "envelope_carries_no_response",
    "schema_invalid_result",
    "m01_must_emit_exactly_one_phase_key",
    "timeout",
    "nonzero_exit",
    # An activation D92 found with no execution receipt: nobody observed its
    # outcome, so it is transient by construction and a later attempt must still
    # pass D90 (spec 6.2 D92, section 11.3).
    "aborted_activation",
})

# Content the model actually produced but that violates its declared scope. These are
# repaired through the targeted-repair engine; re-running the same transport call
# would only reproduce them.
POLICY_OR_CONTENT_FAILURE_CLASSES: frozenset[str] = frozenset({
    "candidate_control_field",
    "candidate_undeclared_artifact",
    "candidate_boundary_violation",
    "candidate_page_denominator",
    "candidate_authoritative_visual",
    "policy_refusal",
    "content_violation",
})

# Integrity faults. Never retried, never repaired: they become a system terminal.
SYSTEM_FAILURE_CLASSES: frozenset[str] = frozenset({
    "IdentityMismatch",
    "IdentityUnobservable",
    "RouteRejected",
    "CapabilityProofFailed",
    "WorkspaceViolation",
    "AttemptLimitExceeded",
    "AuthorizationDenied",
    "family_violation",
})

# A model brief that would invent an authoritative circuit/pin/electrical fact is
# never eligible for M04; a deterministic producer owns those (spec 9, section 13).
AUTHORITATIVE_VISUAL_CLASSES: frozenset[str] = frozenset({
    "circuit", "schematic", "netlist", "pinout", "pin_map", "breadboard",
    "wiring", "electrical", "power_path", "terminal_block",
})

WORKBOOK_OWNED_COMPONENTS: frozenset[str] = frozenset({
    "front_matter", "navigation", "layout", "assembly",
})

# Persisted state channels and verdict hints that may never enter any projection.
DENIED_PROJECTION_NAMES: frozenset[str] = frozenset({
    "artifact_heads", "workbook_head", "accepted_unit_receipts",
    "accepted_unit_checkpoint_receipts", "terminal", "terminal_history",
    "terminal_candidate", "route_decisions", "pending_guard", "pending_failure",
    "resume_frontier", "resume_from", "attempt_counters", "failure_fingerprints",
    "unit_reviews", "workbook_reviews", "review_packets", "workbook_review_packets",
    "repair_requests", "workbook_repair_requests", "retest_plans", "retest_results",
    "workbook_retests", "invalidations", "workbook_invalidations",
    "finding_partitions", "workbook_finding_partitions", "unit_status", "cursor",
    "model_execution_receipts", "activation_receipts", "capability_receipts",
    "checkpoint_metadata", "final_release_audits", "evidence_index_entries",
    "log_audit_receipts", "external_authorizations", "source_admissions",
    "deterministic_checks", "output_root", "engine_root", "curriculum_root",
    "active_manifest_path", "frozen_inputs", "effective_run", "invocation",
    "desired_verdict", "expected_verdict", "target_verdict", "author_history",
    "repair_history", "reviewer_history", "sibling_units", "full_state", "state",
})

# Additional names a review job may never see: anything that hints at the wanted
# outcome, or that reveals who authored or repaired the artifact under review.
REVIEW_DENIED_NAMES: frozenset[str] = frozenset({
    "verdict", "prior_findings", "previous_findings", "prompt", "prompts",
    "model_output", "model_outputs", "job_outputs", "author_notes", "authored_by",
    "attempt", "attempts", "attempt_count", "counter", "counters", "retry_count",
})


# ------------------------------------------------------------------- projection table


@dataclasses.dataclass(frozen=True)
class ProjectionSpec:
    """One row of spec section 9's context table, materialized as code."""

    name: str
    job_id: str
    family: str
    allowed: tuple[str, ...]
    required: tuple[str, ...]
    denied: frozenset[str]
    excluded_doc: str

    @property
    def is_review(self) -> bool:
        return self.family == tp.REVIEW_FAMILY


def _spec(
    name: str,
    job_id: str,
    allowed: tuple[str, ...],
    required: tuple[str, ...],
    denied: Sequence[str],
    excluded_doc: str,
) -> ProjectionSpec:
    family = MODEL_NODE_FAMILIES[job_id]
    extra = REVIEW_DENIED_NAMES if family == tp.REVIEW_FAMILY else frozenset()
    return ProjectionSpec(
        name=name,
        job_id=job_id,
        family=family,
        allowed=allowed,
        required=required,
        denied=DENIED_PROJECTION_NAMES | frozenset(denied) | extra,
        excluded_doc=excluded_doc,
    )


PROJECTION_SPECS: Mapping[str, ProjectionSpec] = {
    "M01_discovery": _spec(
        "M01_discovery", "M01_RESEARCH_UNIT_SOURCES",
        allowed=("request", "unit", "source_rules", "discovery_authority"),
        required=("request", "unit", "source_rules", "discovery_authority"),
        denied=("sibling_requests", "source_requests", "retrievals", "retrieval_group"),
        excluded_doc="sibling requests/units, author history, acceptance, output tree",
    ),
    "M01_interpretation": _spec(
        "M01_interpretation", "M01_RESEARCH_UNIT_SOURCES",
        allowed=("request", "unit", "source_rules", "retrieval_group"),
        required=("request", "unit", "source_rules", "retrieval_group"),
        denied=("discovery_authority", "browsing_authority", "network_access",
                "repository_access", "other_retrieval_groups"),
        excluded_doc="network/repository access, other retrieval groups, "
                     "routing/acceptance state",
    ),
    "M02_domain": _spec(
        "M02_domain", "M02_CREATE_UNIT_DOMAIN_DATA",
        allowed=("unit", "admitted_sources", "domain_schema", "domain_config",
                 "verifier_interface", "calibration"),
        required=("unit", "admitted_sources", "domain_schema", "verifier_interface"),
        denied=("unit_content", "content_drafts", "sibling_artifacts"),
        excluded_doc="content drafts, reviews, sibling units, terminals",
    ),
    "M03_content": _spec(
        "M03_content", "M03_WRITE_UNIT_CONTENT",
        allowed=("unit", "admitted_domain", "curriculum_contracts",
                 "admitted_evidence_references"),
        required=("unit", "admitted_domain", "curriculum_contracts"),
        denied=("rejected_domain_versions", "sibling_artifacts", "acceptance_state"),
        excluded_doc="rejected domain versions, reviewer history, sibling artifacts, "
                     "acceptance state",
    ),
    "M04_visual": _spec(
        "M04_visual", "M04_CREATE_UNIT_VISUALS",
        allowed=("brief", "permitted_facts", "visual_contract"),
        required=("brief", "permitted_facts", "visual_contract"),
        denied=("visual_briefs", "other_briefs", "authoritative_facts", "netlist",
                "wiring", "schematic", "pinout"),
        excluded_doc="authoritative circuit/pin/electrical invention, other briefs, "
                     "full state",
    ),
    "M05_unit_review": _spec(
        "M05_unit_review", "M05_REVIEW_ACTUAL_UNIT",
        allowed=("unit_artifacts", "unit_pdf", "page_inventory", "pages",
                 "deterministic_evidence", "rubric"),
        required=("unit_artifacts", "unit_pdf", "page_inventory", "pages",
                  "deterministic_evidence", "rubric"),
        denied=("repair_requests", "sibling_artifacts"),
        excluded_doc="author/repair history, prompts/outputs from M01-M04/M06, counters, "
                     "desired verdict",
    ),
    "M06_unit_repair": _spec(
        "M06_unit_repair", "M06_REPAIR_NAMED_UNIT_ARTIFACT",
        allowed=("owner", "findings", "parent", "boundary", "allowed_facts",
                 "invalidated_descendants", "retest_order"),
        required=("owner", "findings", "parent", "boundary"),
        denied=("unrelated_findings", "accepted_bytes", "sibling_units", "routing"),
        excluded_doc="unrelated findings/artifacts, accepted bytes, sibling units, "
                     "routing/terminal state",
    ),
    "M07_workbook_review": _spec(
        "M07_workbook_review", "M07_REVIEW_ACTUAL_WORKBOOK",
        allowed=("coverage_map", "accepted_unit_hashes", "workbook_pdf",
                 "page_inventory", "pages", "deterministic_evidence", "rubric"),
        required=("coverage_map", "accepted_unit_hashes", "workbook_pdf",
                  "page_inventory", "pages", "deterministic_evidence", "rubric"),
        denied=("mutable_unit_sources", "unit_sources", "repair_requests"),
        excluded_doc="author and unit repair history, desired verdict, mutable unit sources",
    ),
    "M08_workbook_repair": _spec(
        "M08_workbook_repair", "M08_REPAIR_NAMED_WORKBOOK_DEFECT",
        allowed=("defect", "parent", "allowed_files", "accepted_unit_hashes",
                 "workbook_pdf_hash", "invalidated_descendants", "retest_order"),
        required=("defect", "parent", "allowed_files", "accepted_unit_hashes"),
        denied=("unit_content", "unit_domain", "unit_visual_sources", "other_defects",
                "acceptance_state"),
        excluded_doc="unit content/domain/visual sources, unrelated workbook defects, "
                     "acceptance/terminal authority",
    ),
}


# --------------------------------------------------------------------------- helpers


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ProjectionViolation(f"{label} must be a mapping, got {type(value).__name__}")
    return value


def _collect_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, Mapping):
        keys.update(str(key) for key in value)
        for item in value.values():
            keys |= _collect_keys(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            keys |= _collect_keys(item)
    return keys


def _assert_no_denied_names(projection: Mapping[str, Any], spec: ProjectionSpec) -> None:
    present = _collect_keys(projection)
    offending = sorted(name for name in present if name in spec.denied)
    if offending:
        raise ProjectionViolation(
            f"{spec.name} projection carries structurally excluded fields {offending}; "
            f"spec 9 excludes: {spec.excluded_doc}")


def build_projection(spec_name: str, packet: Mapping[str, Any]) -> dict[str, Any]:
    """Materialize one projection from its allowlist alone.

    The allowlist is read, never the packet's key set, so handing this function a
    whole ``FactoryState`` cannot widen the result: unlisted channels are not copied
    and unreachable, and any excluded name nested inside an allowed value is rejected.
    """

    spec = PROJECTION_SPECS[spec_name]
    _require_mapping(packet, f"{spec.name} packet")
    missing = [name for name in spec.required
               if packet.get(name) is None]
    if missing:
        raise ProjectionViolation(f"{spec.name} packet is missing required {missing}")
    projection = {name: copy.deepcopy(packet[name])
                  for name in spec.allowed if packet.get(name) is not None}
    _assert_no_denied_names(projection, spec)
    tp.assert_no_authoritative_fields(projection, label=f"{spec.name} projection")
    return projection


def _resolve_reservation(packet: Mapping[str, Any], *, job_id: str) -> Mapping[str, Any]:
    reservation = packet.get("reservation")
    if not isinstance(reservation, Mapping):
        raise AttemptNotReserved(
            f"{job_id}: no D90 reservation in the packet; D90_RESERVE_MODEL_ATTEMPT must "
            f"commit a counter before any dispatch")
    if reservation.get("reservation_kind") != RESERVATION_KIND:
        raise AttemptNotReserved(f"{job_id}: reservation is not a {RESERVATION_KIND}")
    if reservation.get("job_id") != job_id:
        raise AttemptNotReserved(
            f"{job_id}: reservation was minted for {reservation.get('job_id')!r}")
    ordinal = reservation.get("attempt_ordinal")
    if not isinstance(ordinal, int) or isinstance(ordinal, bool) or not 1 <= ordinal:
        raise AttemptNotReserved(f"{job_id}: reservation has no positive attempt ordinal")
    if ordinal > MODEL_NODE_ATTEMPT_LIMIT:
        raise AttemptNotReserved(
            f"{job_id}: attempt {ordinal} exceeds the frozen limit "
            f"{MODEL_NODE_ATTEMPT_LIMIT}")
    for field in ("activation_id", "reservation_id"):
        if not isinstance(reservation.get(field), str) or not reservation[field]:
            raise AttemptNotReserved(f"{job_id}: reservation is missing {field}")
    return reservation


def _resolve_correlation(packet: Mapping[str, Any], *, job_id: str,
                         needs_key: bool) -> Mapping[str, Any]:
    correlation = _require_mapping(packet.get("correlation"), f"{job_id} correlation")
    for field in ("run_id", "episode_id"):
        if not isinstance(correlation.get(field), str) or not correlation[field]:
            raise ProjectionViolation(f"{job_id}: correlation is missing {field}")
    if needs_key and (not isinstance(correlation.get("correlation_key"), str)
                      or not correlation["correlation_key"]):
        raise ProjectionViolation(
            f"{job_id}: a fan-out job requires a code-computed correlation_key")
    return correlation


def _staged_inputs(packet: Mapping[str, Any], projection: Mapping[str, Any],
                   *, job_id: str) -> tuple[tp.StagedInput, ...]:
    declared = packet.get("staged_inputs") or ()
    if not isinstance(declared, Sequence) or isinstance(declared, (str, bytes)):
        raise ProjectionViolation(f"{job_id}: staged_inputs must be a sequence")
    referenced = _collect_values(projection)
    staged: list[tp.StagedInput] = []
    for item in declared:
        record = _require_mapping(item, f"{job_id} staged input")
        name = record.get("name")
        if not isinstance(name, str) or not name:
            raise ProjectionViolation(f"{job_id}: staged input has no name")
        if name not in referenced:
            raise ProjectionViolation(
                f"{job_id}: staged input {name!r} is not declared by the projection")
        staged.append(tp.StagedInput(name=name,
                                     source_path=Path(str(record["source_path"])),
                                     sha256=str(record["sha256"])))
    return tuple(staged)


def _collect_values(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        for item in value.values():
            found |= _collect_values(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            found |= _collect_values(item)
    elif isinstance(value, str):
        found.add(value)
    return found


# ------------------------------------------------------------- candidate validation


def _schema_for(route: tp.JobRoute) -> dict[str, Any]:
    return tp.load_output_schema(route)


def _resolve_ref(schema: Mapping[str, Any], root: Mapping[str, Any]) -> Mapping[str, Any]:
    ref = schema.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return schema
    node: Any = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _assert_closed(value: Any, schema: Mapping[str, Any], root: Mapping[str, Any],
                   *, path: str, label: str) -> None:
    """Enforce closed-object semantics even where a schema leaves an object open.

    N13's schemas already declare ``additionalProperties: false`` at every level but
    one (``M02.domain_version.fields``, which is intentionally free-form). Rather than
    trust that, every object in a candidate is checked here before it can reach state.
    """

    schema = _resolve_ref(schema, root)
    if isinstance(value, Mapping):
        properties = schema.get("properties")
        if isinstance(properties, Mapping):
            undeclared = sorted(set(map(str, value)) - set(map(str, properties)))
            if undeclared:
                raise CandidateRejected(
                    f"{label}: undeclared properties {undeclared} at {path}")
            for key, item in value.items():
                subschema = properties.get(key)
                if isinstance(subschema, Mapping):
                    _assert_closed(item, subschema, root, path=f"{path}/{key}", label=label)
        else:
            tp.assert_no_authoritative_fields(value, label=f"{label} at {path}")
    elif isinstance(value, list):
        items = schema.get("items")
        if isinstance(items, Mapping):
            for index, item in enumerate(value):
                _assert_closed(item, items, root, path=f"{path}[{index}]", label=label)


CANDIDATE_VALIDATION_ERRORS = (jsonschema.ValidationError, tp.TransportError,
                               CandidateRejected)


def _validate_candidate_shape(candidate: Mapping[str, Any], route: tp.JobRoute) -> None:
    schema = _schema_for(route)
    jsonschema.Draft202012Validator(schema).validate(dict(candidate))
    tp.assert_no_authoritative_fields(candidate, label=f"{route.job_id} candidate")
    _assert_closed(candidate, schema, schema, path="$", label=f"{route.job_id} candidate")


def _assert_subset(actual: Sequence[str], declared: Sequence[str], *, label: str,
                   error: type[ModelNodeError]) -> None:
    extra = sorted(set(actual) - set(declared))
    if extra:
        raise error(f"{label}: undeclared {extra}; declared {sorted(set(declared))}")


def _page_denominator(projection: Mapping[str, Any], *, label: str) -> dict[int, str]:
    inventory = _require_mapping(projection.get("page_inventory"), f"{label} page_inventory")
    count = inventory.get("page_count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise PageDenominatorViolation(f"{label}: page_count must be a positive integer")
    declared: dict[int, str] = {}
    entries = inventory.get("pages")
    if not isinstance(entries, list) or not entries:
        raise PageDenominatorViolation(f"{label}: page_inventory.pages is empty")
    for entry in entries:
        record = _require_mapping(entry, f"{label} page entry")
        number = record.get("page_number")
        digest = record.get("page_sha256")
        if not isinstance(number, int) or isinstance(number, bool):
            raise PageDenominatorViolation(f"{label}: page_number must be an integer")
        if number in declared:
            raise PageDenominatorViolation(f"{label}: duplicate page {number}")
        if not isinstance(digest, str) or len(digest) != 64:
            raise PageDenominatorViolation(f"{label}: page {number} has no sha256")
        declared[number] = digest
    expected = set(range(1, count + 1))
    if set(declared) != expected:
        raise PageDenominatorViolation(
            f"{label}: inventory covers {sorted(declared)}, denominator is "
            f"{sorted(expected)}")
    supplied = projection.get("pages")
    if not isinstance(supplied, list):
        raise PageDenominatorViolation(f"{label}: pages must be a list")
    seen: dict[int, str] = {}
    for entry in supplied:
        record = _require_mapping(entry, f"{label} page image")
        number = record.get("page_number")
        digest = record.get("page_sha256")
        if number in seen:
            raise PageDenominatorViolation(f"{label}: duplicate page image {number}")
        if number not in declared:
            raise PageDenominatorViolation(f"{label}: page image {number} is not in the denominator")
        if digest != declared[number]:
            raise PageDenominatorViolation(f"{label}: page {number} image hash differs from inventory")
        seen[number] = str(digest)
    if set(seen) != expected:
        raise PageDenominatorViolation(
            f"{label}: page images cover {sorted(seen)}, denominator is {sorted(expected)}")
    return declared


def _assert_findings_cover_pages(candidate: Mapping[str, Any], denominator: Mapping[int, str],
                                 *, label: str) -> None:
    seen: set[int] = set()
    for entry in candidate.get("page_findings", []):
        number = entry.get("page_number")
        if number in seen:
            raise CandidateRejected(f"{label}: duplicate page finding for page {number}")
        if number not in denominator:
            raise CandidateRejected(f"{label}: finding for undeclared page {number}")
        if entry.get("page_sha256") != denominator[number]:
            raise CandidateRejected(f"{label}: page {number} finding cites the wrong page hash")
        seen.add(int(number))
    if seen != set(denominator):
        missing = sorted(set(denominator) - seen)
        raise CandidateRejected(f"{label}: no finding result for pages {missing}")


def _assert_visual_brief_eligible(brief: Mapping[str, Any]) -> None:
    if brief.get("authoritative") is True:
        raise ProjectionViolation(
            "M04: an authoritative brief is produced deterministically, never by a model")
    klass = str(brief.get("visual_class", "")).lower()
    if klass in AUTHORITATIVE_VISUAL_CLASSES:
        raise ProjectionViolation(
            f"M04: visual_class {klass!r} asserts authoritative circuit/pin/electrical "
            f"detail and is not model-eligible")
    if brief.get("eligibility") != "model_eligible":
        raise ProjectionViolation("M04: brief is not marked model_eligible")


# ---------------------------------------------------------------------------- context


@dataclasses.dataclass(frozen=True)
class ModelNodeContext:
    """Everything a model adapter may reach. No state, no routing, no head authority."""

    transport: Any
    registry: Mapping[str, tp.JobRoute]


def _assert_production_transport(transport: Any) -> None:
    """Production adapters accept the real contained transport and nothing else."""

    if isinstance(transport, tp.FakeCliTransport):
        raise ModelNodeError(
            "a fake transport is only injectable through build_test_model_node_context")
    if not isinstance(transport, tp.CliTransport):
        raise ModelNodeError(
            f"production model nodes require transport.CliTransport, got "
            f"{type(transport).__name__}")


def build_model_node_context(context: RuntimeContext, *,
                             registry: Mapping[str, tp.JobRoute] | None = None,
                             ) -> ModelNodeContext:
    """The one production construction path. It can only bind the real transport."""

    transport = context.transport_registry
    _assert_production_transport(transport)
    return ModelNodeContext(
        transport=transport,
        registry=registry if registry is not None else tp.load_job_registry(),
    )


def build_test_model_node_context(*, sandbox_root: Path | str,
                                  responses: Mapping[str, Mapping[str, Any]],
                                  registry: Mapping[str, tp.JobRoute] | None = None,
                                  ) -> ModelNodeContext:
    """Test-only graph build. Named explicitly so no production path can select it."""

    routes = registry if registry is not None else tp.load_job_registry()
    return ModelNodeContext(
        transport=tp.FakeCliTransport(sandbox_root=sandbox_root, responses=responses,
                                      registry=routes),
        registry=routes,
    )


# ---------------------------------------------------------------- D90 / D91 bookkeeping


def attempt_counter_key(job_id: str, correlation_key: str,
                        phase: str | None = None) -> str:
    """The counter one attempt budget is spent against.

    The phase widens the key without touching `correlation_key` itself: M01's
    discovery and interpretation activations must keep the same correlation key,
    because D06B indexes `source_discoveries` and D07 indexes
    `source_interpretations` by it, but they are two independent activations and
    each owns its own retry budget.
    """

    if phase:
        return f"{job_id}|{phase}|{correlation_key}"
    return f"{job_id}|{correlation_key}"


def reserve_model_attempt(
    state: Mapping[str, Any],
    *,
    job_id: str,
    correlation_key: str,
    activation_id: str,
    phase: str | None = None,
    limit: int = MODEL_NODE_ATTEMPT_LIMIT,
    fingerprints: Sequence[Mapping[str, Any]] = (),
    clock: Callable[[], str] = _utc_now,
) -> dict[str, Any]:
    """D90: commit the counter increment before the transport call exists.

    The increment is returned as a ``monotonic_max`` update, so an attempt that never
    returns still leaves a durable reservation and the bound stays enforceable.
    """

    if job_id not in MODEL_NODE_FAMILIES:
        raise ModelNodeError(f"D90: {job_id!r} is not one of the eight model jobs")
    counters = state.get("attempt_counters") or {}
    key = attempt_counter_key(job_id, correlation_key, phase)
    current = int(counters.get(key, 0))
    now = clock()
    if current >= limit:
        return {
            "attempt_counters": {key: current},
            "pending_guard": {
                "kind": "model_attempt",
                "decision": "exhausted",
                "job_id": job_id,
                "counter_key": key,
                "attempts_used": current,
                "limit": limit,
                "fingerprints": [dict(item) for item in fingerprints],
                "reserved_at_utc": now,
            },
        }
    ordinal = current + 1
    reservation_id = f"{activation_id}#{ordinal}"
    reservation = {
        "reservation_kind": RESERVATION_KIND,
        "reservation_id": reservation_id,
        "activation_id": activation_id,
        "job_id": job_id,
        "counter_key": key,
        "attempt_ordinal": ordinal,
        "limit": limit,
        "reserved_at_utc": now,
    }
    return {
        "attempt_counters": {key: ordinal},
        "activation_receipts": [{"key": f"reservation:{reservation_id}", **reservation}],
        "pending_guard": {
            "kind": "model_attempt",
            "decision": "authorized",
            "job_id": job_id,
            "counter_key": key,
            "reservation": reservation,
        },
    }


def _repair_destination(job_id: Any) -> str:
    if job_id in {"M07_REVIEW_ACTUAL_WORKBOOK", "M08_REPAIR_NAMED_WORKBOOK_DEFECT"}:
        return "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR"
    return "D17_CLASSIFY_UNIT_FINDINGS"


def classify_model_failure(
    failure: Mapping[str, Any],
    *,
    attempts_used: int,
    limit: int = MODEL_NODE_ATTEMPT_LIMIT,
    clock: Callable[[], str] = _utc_now,
) -> dict[str, Any]:
    """D91: decide retry, repair, exhaustion, or system from one execution failure.

    A retry is authorized only for a malformed/transient transport class that is still
    inside the frozen limit, and it must go back through D90. Policy and content
    failures are repaired, never transport-retried; integrity faults are terminal.
    """

    _require_mapping(failure, "D91 failure")
    failure_class = str(failure.get("failure_class") or "unknown")
    job_id = failure.get("job_id")
    counter_key = failure.get("counter_key")
    now = clock()
    fingerprint = (f"{job_id}|{counter_key}|{failure_class}")

    if failure_class in SYSTEM_FAILURE_CLASSES:
        decision, destination, terminal = "system", "D98_WRITE_TERMINAL", "SYSTEM_FAILURE"
    elif failure_class in POLICY_OR_CONTENT_FAILURE_CLASSES:
        decision, destination, terminal = "repair", _repair_destination(job_id), None
    elif failure_class in RETRYABLE_FAILURE_CLASSES:
        if attempts_used < limit:
            decision, destination, terminal = "retry", "D90_RESERVE_MODEL_ATTEMPT", None
        else:
            decision, destination, terminal = (
                "exhausted", "D98_WRITE_TERMINAL", "CONVERGENCE_EXHAUSTED")
    else:
        decision, destination, terminal = "system", "D98_WRITE_TERMINAL", "SYSTEM_FAILURE"

    update: dict[str, Any] = {
        "failure_fingerprints": [{
            "key": f"{fingerprint}|{attempts_used}",
            "fingerprint": fingerprint,
            "job_id": job_id,
            "counter_key": counter_key,
            "failure_class": failure_class,
            "attempts_used": attempts_used,
            "limit": limit,
            "classified_at_utc": now,
        }],
        "pending_failure": {**dict(failure), "classification": decision},
        "pending_guard": {
            "kind": "model_failure",
            "decision": decision,
            "destination": destination,
            # `routing.route_model_failure` resolves the dynamic `repair`
            # destination out of `detail`, so the same fact is carried where the
            # guard table reads it.
            "detail": {"destination": destination, "job_id": job_id,
                       "counter_key": counter_key},
            "job_id": job_id,
            "counter_key": counter_key,
            "failure_class": failure_class,
            "attempts_used": attempts_used,
            "limit": limit,
        },
    }
    if terminal is not None:
        update["terminal_candidate"] = {
            "terminal_kind": terminal,
            "cause": failure_class,
            "job_id": job_id,
            "counter_key": counter_key,
            "fingerprint": fingerprint,
            "proposed_at_utc": now,
        }
    return update


# --------------------------------------------------------- D90 / D91 node callables


ATTEMPT_RESERVATION_NODE = "D90_RESERVE_MODEL_ATTEMPT"
MODEL_FAILURE_NODE = "D91_CLASSIFY_MODEL_FAILURE"


def _staged_dispatch(state: Mapping[str, Any]) -> tuple[str, str, list[Mapping[str, Any]]]:
    """The job, the member list key, and the members of the staged dispatch packet.

    The member list key is read back rather than normalized because
    `routing._staged_fanout` translates whichever of `packets`/`briefs` the
    dispatching node used, and D90 must restage under the same name.
    """

    packet = state.get("pending_packet")
    if not isinstance(packet, Mapping):
        raise ModelNodeError(
            f"{ATTEMPT_RESERVATION_NODE}: no `pending_packet` is staged; a reservation "
            f"can only be minted for a dispatch the denominator already committed to")
    job_id = packet.get("dispatch")
    if job_id not in MODEL_NODE_FAMILIES:
        raise ModelNodeError(
            f"{ATTEMPT_RESERVATION_NODE}: staged packet dispatches {job_id!r}, which is "
            f"not one of the eight model jobs")
    member_key = "packets" if packet.get("packets") is not None else "briefs"
    members = packet.get(member_key)
    if (not isinstance(members, Sequence) or isinstance(members, (str, bytes))
            or not members):
        raise ModelNodeError(
            f"{ATTEMPT_RESERVATION_NODE}: staged packet carries no non-empty "
            f"{member_key!r} member list")
    return job_id, member_key, [_require_mapping(m, f"{job_id} member") for m in members]


def _retry_counter_key(state: Mapping[str, Any]) -> str | None:
    """The one counter key D91 authorized a further attempt for, if it did."""

    guard = state.get("pending_guard")
    if not isinstance(guard, Mapping) or guard.get("kind") != "model_failure":
        return None
    if guard.get("decision") != "retry":
        return None
    key = guard.get("counter_key")
    if not isinstance(key, str) or not key:
        raise ModelNodeError(
            f"{ATTEMPT_RESERVATION_NODE}: a classified retry names no counter key")
    return key


def _activation_phase(member: Mapping[str, Any]) -> str | None:
    """The activation kind a staged member declares, if its job has more than one.

    Only M01 dispatches two structurally different activations (`DISCOVER` and
    `INTERPRET`) under one correlation key, and its dispatchers already stage the
    distinction; every other job stages no `phase` and keeps an unwidened key.
    """

    phase = member.get("phase")
    if phase is None:
        return None
    if not isinstance(phase, str) or not phase:
        raise ModelNodeError(
            f"{ATTEMPT_RESERVATION_NODE}: staged member declares a non-string phase "
            f"{phase!r}, so its attempt budget could not be keyed")
    return phase


def _activation_id(correlation: Mapping[str, Any], *, counter_key: str,
                   ordinal: int) -> str:
    """One activation identity per attempt, derived so no two attempts share one.

    D92 accounts for an interrupted attempt by matching activation ids against
    execution receipts, so the ordinal is part of the identity: reusing it across
    attempts would make an unobserved attempt indistinguishable from an observed one.
    """

    return (f"{correlation['run_id']}/{correlation['episode_id']}/{counter_key}"
            f"/attempt-{ordinal}")


def D90_RESERVE_MODEL_ATTEMPT(state: Mapping[str, Any],
                              context: Any) -> dict[str, Any]:
    """D90: commit one attempt counter per staged dispatch member, before dispatch.

    A map superstep stages N worker projections and each is a separate attempt
    against its own correlation, so this reserves per member and returns the
    packet restaged with each member's reservation attached — the fan-out guard
    then translates exactly what was reserved. A D91-authorized retry names one
    counter key, and only that member is re-reserved and restaged: the other
    members' results are already committed and are not re-dispatched.

    Any member at the frozen limit exhausts the whole superstep rather than
    dispatching a partial map, so the bound can never be crossed by a sibling.
    """

    job_id, member_key, members = _staged_dispatch(state)
    retry_key = _retry_counter_key(state)
    counters = state.get("attempt_counters") or {}

    reserved_counters: dict[str, int] = {}
    receipts: list[dict[str, Any]] = []
    restaged: list[dict[str, Any]] = []
    reservations: dict[str, Any] = {}
    exhausted: list[dict[str, Any]] = []

    for member in members:
        correlation = _resolve_correlation(member, job_id=job_id, needs_key=True)
        phase = _activation_phase(member)
        key = attempt_counter_key(job_id, correlation["correlation_key"], phase)
        if retry_key is not None and key != retry_key:
            continue
        ordinal = int(counters.get(key, 0)) + 1
        update = reserve_model_attempt(
            state, job_id=job_id, correlation_key=correlation["correlation_key"],
            phase=phase,
            activation_id=_activation_id(correlation, counter_key=key, ordinal=ordinal))
        guard = update["pending_guard"]
        reserved_counters.update(update["attempt_counters"])
        if guard["decision"] == "exhausted":
            exhausted.append({"counter_key": key, "attempts_used": guard["attempts_used"],
                              "limit": guard["limit"]})
            continue
        reservation = guard["reservation"]
        reservations[key] = reservation
        receipts.extend(update["activation_receipts"])
        restaged.append({**member, "reservation": reservation})

    if retry_key is not None and not (restaged or exhausted):
        raise ModelNodeError(
            f"{ATTEMPT_RESERVATION_NODE}: classified retry {retry_key!r} matches no "
            f"staged member, so there is nothing to re-dispatch")

    if exhausted:
        return {
            "attempt_counters": reserved_counters,
            "pending_guard": {
                "node": ATTEMPT_RESERVATION_NODE,
                "value": "exhausted",
                "kind": "model_attempt",
                "decision": "exhausted",
                "detail": {"job_id": job_id, "exhausted": exhausted,
                           "limit": MODEL_NODE_ATTEMPT_LIMIT},
            },
        }

    packet = dict(state["pending_packet"])
    packet[member_key] = restaged
    return {
        "attempt_counters": reserved_counters,
        "activation_receipts": receipts,
        "pending_packet": packet,
        "pending_guard": {
            "node": ATTEMPT_RESERVATION_NODE,
            "value": "authorized",
            "kind": "model_attempt",
            "decision": "authorized",
            "detail": {"job_id": job_id, "reservations": reservations,
                       "members": len(restaged)},
        },
    }


def _aborted_activation(state: Mapping[str, Any]) -> dict[str, Any]:
    """The failure record for an activation D92 could not account for.

    D92 hands D91 activation ids, not a failure: the reservation receipt is the
    only place the job and counter that attempt belongs to still exist.
    """

    guard = state.get("pending_guard")
    detail = guard.get("detail") if isinstance(guard, Mapping) else None
    activations = detail.get("activations") if isinstance(detail, Mapping) else None
    if not isinstance(activations, Sequence) or isinstance(activations, (str, bytes)):
        raise ModelNodeError(
            f"{MODEL_FAILURE_NODE}: no model failure and no incomplete activation to "
            f"classify")
    pending = sorted(str(item) for item in activations)
    if not pending:
        raise ModelNodeError(f"{MODEL_FAILURE_NODE}: the incomplete activation list is empty")
    activation_id = pending[0]
    reservation = next(
        (record for record in (state.get("activation_receipts") or ())
         if isinstance(record, Mapping)
         and record.get("activation_id") == activation_id
         and record.get("reservation_kind") == RESERVATION_KIND),
        None)
    if reservation is None:
        raise ModelNodeError(
            f"{MODEL_FAILURE_NODE}: activation {activation_id!r} has no reservation "
            f"receipt, so the attempt it belongs to cannot be identified")
    return {
        "job_id": reservation["job_id"],
        "counter_key": reservation["counter_key"],
        "activation_id": activation_id,
        "reservation_id": reservation["reservation_id"],
        "attempt_ordinal": reservation["attempt_ordinal"],
        "failure_class": "aborted_activation",
        "detail": f"activation {activation_id} has no execution receipt",
        "unclassified_activations": pending[1:],
    }


def D91_CLASSIFY_MODEL_FAILURE(state: Mapping[str, Any],
                               context: Any) -> dict[str, Any]:
    """D91: classify one model failure, or one activation D92 could not account for.

    The attempt count is read from the committed counter rather than from the
    failure record, so a retry is authorized against the reservation that is
    actually durable. A `retry` clears `pending_failure`: D90 is the next node,
    and an uncleared failure would route it to the terminal writer instead.
    """

    failure = state.get("pending_failure")
    if not isinstance(failure, Mapping):
        failure = _aborted_activation(state)
    counter_key = failure.get("counter_key")
    counters = state.get("attempt_counters") or {}
    attempts_used = int(counters.get(counter_key, failure.get("attempt_ordinal") or 1))
    update = classify_model_failure(failure, attempts_used=attempts_used)
    if update["pending_guard"]["decision"] == "retry":
        update["pending_failure"] = None
    return update


# Registrable by stable ID: both are `(state, context) -> update` callables owned
# by this module, which is what N20's binding-owner audit requires of a node body.
MODEL_BOOKKEEPING_NODES: Mapping[str, Callable[..., dict[str, Any]]] = {
    ATTEMPT_RESERVATION_NODE: D90_RESERVE_MODEL_ATTEMPT,
    MODEL_FAILURE_NODE: D91_CLASSIFY_MODEL_FAILURE,
}


# ------------------------------------------------------------------- shared dispatch


@dataclasses.dataclass(frozen=True)
class _Dispatch:
    spec: ProjectionSpec
    route: tp.JobRoute
    projection: dict[str, Any]
    correlation: Mapping[str, Any]
    reservation: Mapping[str, Any]
    candidate: dict[str, Any]
    receipt: dict[str, Any]
    attempts: tuple[dict[str, Any], ...]


def _execution_receipts(dispatch_receipts: Sequence[Mapping[str, Any]], *,
                        spec: ProjectionSpec, reservation: Mapping[str, Any],
                        correlation: Mapping[str, Any],
                        projection_sha256: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, receipt in enumerate(dispatch_receipts, start=1):
        records.append({
            "key": f"{reservation['reservation_id']}#{index}",
            "job_id": spec.job_id,
            "projection_name": spec.name,
            "reservation_id": reservation["reservation_id"],
            "activation_id": reservation["activation_id"],
            "attempt_ordinal": reservation["attempt_ordinal"],
            "run_id": correlation["run_id"],
            "episode_id": correlation["episode_id"],
            "projection_sha256": projection_sha256,
            "receipt": dict(receipt),
        })
    return records


def _activation_receipt(*, spec: ProjectionSpec, reservation: Mapping[str, Any],
                        correlation: Mapping[str, Any], projection_sha256: str,
                        candidate_sha256: str | None, executed_family: str | None,
                        executed_model: str | None, result: str) -> dict[str, Any]:
    return {
        "key": f"activation:{reservation['reservation_id']}",
        "job_id": spec.job_id,
        "projection_name": spec.name,
        "reservation_id": reservation["reservation_id"],
        "activation_id": reservation["activation_id"],
        "attempt_ordinal": reservation["attempt_ordinal"],
        "run_id": correlation["run_id"],
        "episode_id": correlation["episode_id"],
        "decided_family": spec.family,
        "executed_family": executed_family,
        "executed_model": executed_model,
        "projection_sha256": projection_sha256,
        "candidate_sha256": candidate_sha256,
        "result": result,
    }


def _executed_family(receipt: Mapping[str, Any]) -> str | None:
    observed = receipt.get("observed_family")
    return observed if isinstance(observed, str) and observed else receipt.get("decided_family")


def _failure_update(*, spec: ProjectionSpec, reservation: Mapping[str, Any],
                    correlation: Mapping[str, Any], projection_sha256: str,
                    failure_class: str, detail: str,
                    receipts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "model_execution_receipts": _execution_receipts(
            receipts, spec=spec, reservation=reservation, correlation=correlation,
            projection_sha256=projection_sha256),
        "activation_receipts": [_activation_receipt(
            spec=spec, reservation=reservation, correlation=correlation,
            projection_sha256=projection_sha256, candidate_sha256=None,
            executed_family=None, executed_model=None, result="failed")],
        "pending_failure": {
            "job_id": spec.job_id,
            "projection_name": spec.name,
            "counter_key": reservation["counter_key"],
            "activation_id": reservation["activation_id"],
            "reservation_id": reservation["reservation_id"],
            "attempt_ordinal": reservation["attempt_ordinal"],
            "failure_class": failure_class,
            "detail": detail[:2000],
            "requires_classification_by": "D91_CLASSIFY_MODEL_FAILURE",
        },
    }


def _dispatch(spec_name: str, packet: Mapping[str, Any], context: ModelNodeContext,
              *, needs_correlation_key: bool = False,
              ) -> tuple[_Dispatch | None, dict[str, Any] | None]:
    """The module's only transport call site.

    Returning ``(None, failure_update)`` rather than raising keeps a model failure a
    routable state fact: D91 classifies it and only D90 may authorize another attempt.
    """

    spec = PROJECTION_SPECS[spec_name]
    route = tp.resolve_route(spec.job_id, context.registry)
    if route.family != spec.family:
        raise FamilyViolation(
            f"{spec.job_id}: frozen registry family {route.family!r} != {spec.family!r}")
    reservation = _resolve_reservation(packet, job_id=spec.job_id)
    correlation = _resolve_correlation(packet, job_id=spec.job_id,
                                       needs_key=needs_correlation_key)
    projection = build_projection(spec_name, packet)
    projection_sha256 = canonical_digest(projection)
    staged = _staged_inputs(packet, projection, job_id=spec.job_id)

    try:
        result = context.transport.execute(
            job_id=spec.job_id,
            activation_id=reservation["activation_id"],
            episode_id=correlation["episode_id"],
            projection=projection,
            staged_inputs=staged,
        )
    except tp.TransportError as error:
        failure_class = getattr(error, "failure_class", type(error).__name__)
        receipts = [getattr(error, "receipt", None) or {"outcome": "transport_failure"}]
        return None, _failure_update(
            spec=spec, reservation=reservation, correlation=correlation,
            projection_sha256=projection_sha256, failure_class=str(failure_class),
            detail=str(error), receipts=receipts)

    executed_family = _executed_family(result.receipt)
    if spec.is_review and executed_family == tp.AUTHORING_FAMILY:
        raise FamilyViolation(
            f"{spec.job_id}: a review executed in the authoring family "
            f"{tp.AUTHORING_FAMILY!r}")
    if executed_family is not None and executed_family != spec.family:
        raise FamilyViolation(
            f"{spec.job_id}: executed family {executed_family!r} != decided {spec.family!r}")

    candidate = dict(result.candidate)
    return _Dispatch(spec=spec, route=route, projection=projection,
                     correlation=correlation, reservation=reservation,
                     candidate=candidate, receipt=dict(result.receipt),
                     attempts=tuple(dict(item) for item in result.attempts)), None


def _reject(dispatch: _Dispatch, failure_class: str, detail: str) -> dict[str, Any]:
    return _failure_update(
        spec=dispatch.spec, reservation=dispatch.reservation,
        correlation=dispatch.correlation,
        projection_sha256=canonical_digest(dispatch.projection),
        failure_class=failure_class, detail=detail, receipts=dispatch.attempts)


def _accept(dispatch: _Dispatch, channel_update: Mapping[str, Any]) -> dict[str, Any]:
    projection_sha256 = canonical_digest(dispatch.projection)
    candidate_sha256 = canonical_digest(dispatch.candidate)
    update: dict[str, Any] = dict(channel_update)
    update["model_execution_receipts"] = _execution_receipts(
        dispatch.attempts, spec=dispatch.spec, reservation=dispatch.reservation,
        correlation=dispatch.correlation, projection_sha256=projection_sha256)
    update["activation_receipts"] = [_activation_receipt(
        spec=dispatch.spec, reservation=dispatch.reservation,
        correlation=dispatch.correlation, projection_sha256=projection_sha256,
        candidate_sha256=candidate_sha256,
        executed_family=_executed_family(dispatch.receipt),
        executed_model=dispatch.receipt.get("observed_model")
        or dispatch.receipt.get("decided_model"),
        result="candidate_produced")]
    _assert_model_node_update(update)
    return update


def _assert_model_node_update(update: Mapping[str, Any]) -> None:
    unknown = sorted(set(update) - MODEL_NODE_WRITABLE_FIELDS)
    if unknown:
        raise ModelNodeError(
            f"a model node may not write {unknown}; admission, heads, and terminals are "
            f"deterministic-node authority")


def _candidate_record(dispatch: _Dispatch, **extra: Any) -> dict[str, Any]:
    """A pre-admission candidate descriptor.

    Two kinds of key, and the split is the point. The model's own output is quarantined
    under ``payload``; every other key is *lineage* the projection already knew before the
    model ran (which unit, which retrieved bytes, which content epoch), so a deterministic
    node can correlate the candidate without trusting the model for it.

    It deliberately carries no ``version``/``hash``/``parent_hash``, so it cannot be
    replayed as an ``advance_head`` update; only a deterministic admission node mints a
    head record, and ``ADMISSION_OWNED_CANDIDATE_FIELDS`` is enforced here rather than
    left to convention.
    """

    minted = sorted(ADMISSION_OWNED_CANDIDATE_FIELDS & set(extra))
    if minted:
        raise ModelNodeError(
            f"{dispatch.spec.job_id}: a model candidate may not carry {minted}; minting an "
            f"artifact version is deterministic admission authority")
    record = {
        "key": f"candidate:{dispatch.reservation['reservation_id']}",
        "record_kind": "model_candidate",
        "pre_admission": True,
        "job_id": dispatch.spec.job_id,
        "projection_name": dispatch.spec.name,
        "run_id": dispatch.correlation["run_id"],
        "episode_id": dispatch.correlation["episode_id"],
        "activation_id": dispatch.reservation["activation_id"],
        "reservation_id": dispatch.reservation["reservation_id"],
        "projection_sha256": canonical_digest(dispatch.projection),
        "candidate_sha256": canonical_digest(dispatch.candidate),
        "payload": dispatch.candidate,
    }
    record.update(extra)
    return record


# --------------------------------------------------------------------- M01 (two phases)


def m01_discover_unit_sources(packet: Mapping[str, Any],
                              context: ModelNodeContext) -> dict[str, Any]:
    """M01 `phase=DISCOVER`: one bounded question under discovery authority.

    Distinct from interpretation by construction, not by an internal branch: this
    projection is the only one that carries discovery authority, and it can never
    carry retrieved bytes.
    """

    dispatch, failure = _dispatch("M01_discovery", packet, context,
                                  needs_correlation_key=True)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    if "locators" not in dispatch.candidate:
        return _reject(dispatch, "candidate_undeclared_artifact",
                       "discovery must emit locators, not interpretations")
    request_id = dispatch.projection["request"].get("request_id")
    for locator in dispatch.candidate["locators"]:
        if locator.get("request_id") != request_id:
            return _reject(dispatch, "candidate_undeclared_artifact",
                           f"locator cites request {locator.get('request_id')!r}, "
                           f"projection declared {request_id!r}")
    key = dispatch.correlation["correlation_key"]
    return _accept(dispatch, {"source_discoveries": {key: _candidate_record(
        dispatch, phase="DISCOVER", request_id=request_id,
        unit_id=dispatch.projection["unit"].get("unit_id"))}})


def m01_interpret_unit_sources(packet: Mapping[str, Any],
                               context: ModelNodeContext) -> dict[str, Any]:
    """M01 `phase=INTERPRET`: the same request plus only its retrieved bytes.

    Discovery authority is a denied name here, so an interpretation packet that tries
    to carry browsing authority is rejected before any process starts.
    """

    dispatch, failure = _dispatch("M01_interpretation", packet, context,
                                  needs_correlation_key=True)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    if "interpretations" not in dispatch.candidate:
        return _reject(dispatch, "candidate_undeclared_artifact",
                       "interpretation must emit interpretations, not locators")
    request_id = dispatch.projection["request"].get("request_id")
    group = dispatch.projection["retrieval_group"]
    retrieval_ids = [str(item.get("retrieval_id"))
                     for item in group.get("retrieved_records", [])]
    for interpretation in dispatch.candidate["interpretations"]:
        if interpretation.get("request_id") != request_id:
            return _reject(dispatch, "candidate_undeclared_artifact",
                           f"interpretation cites request {interpretation.get('request_id')!r}")
        if str(interpretation.get("retrieval_id")) not in retrieval_ids:
            return _reject(dispatch, "candidate_undeclared_artifact",
                           f"interpretation cites undeclared retrieval "
                           f"{interpretation.get('retrieval_id')!r}")
    key = dispatch.correlation["correlation_key"]
    return _accept(dispatch, {"source_interpretations": {key: _candidate_record(
        dispatch, phase="INTERPRET", request_id=request_id,
        unit_id=dispatch.projection["unit"].get("unit_id"),
        retrieval_sha256=_retrieval_sha256(group))}})


def _retrieval_sha256(group: Mapping[str, Any]) -> str | None:
    """The sha256 of the bytes this interpretation was derived from.

    Read off the retrieval group the dispatcher staged, never off the model's answer:
    D07 stales an interpretation whose parent bytes are no longer the retrieval, and a
    model-supplied parent hash would let a stale interpretation vouch for itself. A
    group whose records disagree has no single parent, so the record claims none and
    D07 refuses it rather than admitting an unproven lineage.
    """

    hashes = {record.get("sha256") for record in group.get("retrieved_records", [])
              if isinstance(record, Mapping)}
    return hashes.pop() if len(hashes) == 1 else None


def m01_research_unit_sources(packet: Mapping[str, Any],
                              context: ModelNodeContext) -> dict[str, Any]:
    """Select the phase from the packet's explicit `phase`, never from hidden state."""

    phase = packet.get("phase")
    if phase == "DISCOVER":
        return m01_discover_unit_sources(packet, context)
    if phase == "INTERPRET":
        return m01_interpret_unit_sources(packet, context)
    raise ProjectionViolation(
        f"M01 packet must declare phase DISCOVER or INTERPRET, got {phase!r}")


# ---------------------------------------------------------------------- M02-M04, M06


def m02_create_unit_domain_data(packet: Mapping[str, Any],
                                context: ModelNodeContext) -> dict[str, Any]:
    dispatch, failure = _dispatch("M02_domain", packet, context)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    domain = dispatch.candidate["domain_version"]
    unit_id = dispatch.projection["unit"].get("unit_id")
    if domain.get("unit_id") != unit_id:
        return _reject(dispatch, "candidate_undeclared_artifact",
                       f"domain names unit {domain.get('unit_id')!r}, projection declared "
                       f"{unit_id!r}")
    admitted = [str(item.get("source_id"))
                for item in dispatch.projection["admitted_sources"]]
    cited = [str(item.get("source_id")) for item in domain.get("evidence_references", [])]
    try:
        _assert_subset(cited, admitted, label="M02 evidence_references",
                       error=CandidateRejected)
    except CandidateRejected as error:
        return _reject(dispatch, "candidate_undeclared_artifact", str(error))
    return _accept(dispatch, {"artifact_versions": [_candidate_record(
        dispatch, channel="domain", scope="units", unit_id=unit_id)]})


def m03_write_unit_content(packet: Mapping[str, Any],
                           context: ModelNodeContext) -> dict[str, Any]:
    dispatch, failure = _dispatch("M03_content", packet, context)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    content = dispatch.candidate["unit_content"]
    unit_id = dispatch.projection["unit"].get("unit_id")
    if content.get("unit_id") != unit_id:
        return _reject(dispatch, "candidate_undeclared_artifact",
                       f"content names unit {content.get('unit_id')!r}")
    declared_sections = [str(item.get("section_id")) for item in content.get("sections", [])]
    admitted = [str(item.get("source_id"))
                for item in dispatch.projection.get("admitted_evidence_references", [])]
    for reference in content.get("evidence_references", []):
        if str(reference.get("section_id")) not in declared_sections:
            return _reject(dispatch, "candidate_undeclared_artifact",
                           f"evidence cites unknown section {reference.get('section_id')!r}")
        if admitted and str(reference.get("source_id")) not in admitted:
            return _reject(dispatch, "candidate_undeclared_artifact",
                           f"evidence cites unadmitted source {reference.get('source_id')!r}")
    return _accept(dispatch, {"artifact_versions": [_candidate_record(
        dispatch, channel="content", scope="units", unit_id=unit_id)]})


def m04_create_unit_visuals(packet: Mapping[str, Any],
                            context: ModelNodeContext) -> dict[str, Any]:
    """Exactly one eligible, non-authoritative brief per activation."""

    brief = _require_mapping(packet.get("brief"), "M04 brief")
    _assert_visual_brief_eligible(brief)
    dispatch, failure = _dispatch("M04_visual", packet, context,
                                  needs_correlation_key=True)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    brief_id = dispatch.projection["brief"].get("brief_id")
    candidate = dispatch.candidate
    if candidate["visual_candidate"].get("brief_id") != brief_id:
        return _reject(dispatch, "candidate_undeclared_artifact",
                       f"visual answers brief {candidate['visual_candidate'].get('brief_id')!r}")
    provenance = candidate["provenance_declaration"]
    if provenance.get("brief_id") != brief_id:
        return _reject(dispatch, "candidate_undeclared_artifact",
                       "provenance declares a different brief")
    if provenance.get("asserts_authoritative_detail") is True:
        return _reject(dispatch, "candidate_authoritative_visual",
                       "a model visual may not assert authoritative circuit/pin detail")
    permitted = [str(item) for item in dispatch.projection["permitted_facts"]]
    try:
        _assert_subset([str(item) for item in provenance.get("permitted_facts_used", [])],
                       permitted, label="M04 permitted_facts_used", error=CandidateRejected)
    except CandidateRejected as error:
        return _reject(dispatch, "candidate_undeclared_artifact", str(error))
    key = dispatch.correlation["correlation_key"]
    return _accept(dispatch, {"visual_results": {key: _candidate_record(
        dispatch, channel="visuals", scope="units", brief_id=brief_id, subset="model",
        unit_id=dispatch.projection["brief"].get("unit_id"),
        content_hash=dispatch.projection["brief"].get("content_hash"))}})


def m06_repair_named_unit_artifact(packet: Mapping[str, Any],
                                   context: ModelNodeContext) -> dict[str, Any]:
    """One named finding boundary against one immutable parent."""

    _assert_unit_repair_boundary(packet)
    dispatch, failure = _dispatch("M06_unit_repair", packet, context)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    boundary = dispatch.projection["boundary"]
    parent = dispatch.projection["parent"]
    declared_pointers = [str(item) for item in boundary.get("json_pointers", [])]
    finding_ids = [str(item.get("finding_id")) for item in dispatch.projection["findings"]]
    child = dispatch.candidate["candidate_child"]
    if child.get("artifact_name") != parent.get("artifact_name"):
        return _reject(dispatch, "candidate_boundary_violation",
                       f"child renames the artifact to {child.get('artifact_name')!r}")
    try:
        _assert_subset([str(item) for item in child.get("addressed_finding_ids", [])],
                       finding_ids, label="M06 addressed_finding_ids",
                       error=RepairBoundaryViolation)
        _assert_subset([str(item.get("json_pointer"))
                        for item in dispatch.candidate["changed_path_manifest"]],
                       declared_pointers, label="M06 changed_path_manifest",
                       error=RepairBoundaryViolation)
        _assert_subset([str(item.get("finding_id"))
                        for item in dispatch.candidate["changed_path_manifest"]],
                       finding_ids, label="M06 manifest finding_id",
                       error=RepairBoundaryViolation)
    except RepairBoundaryViolation as error:
        return _reject(dispatch, "candidate_boundary_violation", str(error))
    return _accept(dispatch, {"artifact_versions": [_candidate_record(
        dispatch, channel=str(parent.get("channel", "content")), scope="units",
        owner=dispatch.projection["owner"], unit_id=parent.get("unit_id"),
        parent_sha256=parent.get("parent_sha256"))]})


def _assert_unit_repair_boundary(packet: Mapping[str, Any]) -> None:
    boundary = _require_mapping(packet.get("boundary"), "M06 boundary")
    pointers = boundary.get("json_pointers")
    if not isinstance(pointers, list) or not pointers:
        raise RepairBoundaryViolation(
            "M06: repair requires a non-empty declared json_pointers boundary")
    findings = packet.get("findings")
    owner = packet.get("owner")
    if not isinstance(findings, list) or not findings:
        raise RepairBoundaryViolation("M06: exactly one owner's findings are required")
    owners = {item.get("owner") for item in findings if isinstance(item, Mapping)}
    if owners != {owner}:
        raise RepairBoundaryViolation(
            f"M06: findings span owners {sorted(map(str, owners))}, declared {owner!r}")


def _assert_workbook_repair_boundary(packet: Mapping[str, Any]) -> None:
    allowed = _require_mapping(packet.get("allowed_files"), "M08 allowed_files")
    files = allowed.get("files")
    if not isinstance(files, list) or not files:
        raise RepairBoundaryViolation(
            "M08: repair requires a non-empty declared workbook-owned file list")


# ------------------------------------------------------------------------- M05 / M07


def m05_review_actual_unit(packet: Mapping[str, Any],
                           context: ModelNodeContext) -> dict[str, Any]:
    """Gemini review of the frozen actual unit packet, every page included."""

    denominator = _page_denominator(packet, label="M05")
    dispatch, failure = _dispatch("M05_unit_review", packet, context)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    try:
        _assert_findings_cover_pages(dispatch.candidate, denominator, label="M05")
    except CandidateRejected as error:
        return _reject(dispatch, "candidate_page_denominator", str(error))
    return _accept(dispatch, {"unit_reviews": [_candidate_record(
        dispatch, review_kind="unit", page_count=len(denominator),
        unit_pdf_sha256=dispatch.projection["unit_pdf"].get("sha256"))]})


def m07_review_actual_workbook(packet: Mapping[str, Any],
                               context: ModelNodeContext) -> dict[str, Any]:
    """Gemini review of the frozen actual workbook packet, every page included."""

    denominator = _page_denominator(packet, label="M07")
    dispatch, failure = _dispatch("M07_workbook_review", packet, context)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    try:
        _assert_findings_cover_pages(dispatch.candidate, denominator, label="M07")
    except CandidateRejected as error:
        return _reject(dispatch, "candidate_page_denominator", str(error))
    return _accept(dispatch, {"workbook_reviews": [_candidate_record(
        dispatch, review_kind="workbook", page_count=len(denominator),
        workbook_pdf_sha256=dispatch.projection["workbook_pdf"].get("sha256"))]})


# ------------------------------------------------------------------------------- M08


def m08_repair_named_workbook_defect(packet: Mapping[str, Any],
                                     context: ModelNodeContext) -> dict[str, Any]:
    """Exactly one workbook-owned defect against the immutable workbook parent."""

    defect = _require_mapping(packet.get("defect"), "M08 defect")
    component = str(defect.get("component", ""))
    if component not in WORKBOOK_OWNED_COMPONENTS:
        raise RepairBoundaryViolation(
            f"M08: {component!r} is not workbook-owned; unit-owned defects are repaired "
            f"by M06 against the unit, never here")
    _assert_workbook_repair_boundary(packet)
    dispatch, failure = _dispatch("M08_workbook_repair", packet, context)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    allowed_files = [str(item) for item in dispatch.projection["allowed_files"]["files"]]
    defect_id = str(dispatch.projection["defect"].get("defect_id"))
    child = dispatch.candidate["candidate_child"]
    if str(child.get("addressed_defect_id")) != defect_id:
        return _reject(dispatch, "candidate_boundary_violation",
                       f"child addresses defect {child.get('addressed_defect_id')!r}, "
                       f"declared {defect_id!r}")
    try:
        _assert_subset([str(item.get("staged_file_name"))
                        for item in dispatch.candidate["changed_file_manifest"]],
                       allowed_files, label="M08 changed_file_manifest",
                       error=RepairBoundaryViolation)
        _assert_subset([str(item.get("defect_id"))
                        for item in dispatch.candidate["changed_file_manifest"]],
                       [defect_id], label="M08 manifest defect_id",
                       error=RepairBoundaryViolation)
    except RepairBoundaryViolation as error:
        return _reject(dispatch, "candidate_boundary_violation", str(error))
    parent = dispatch.projection["parent"]
    return _accept(dispatch, {"workbook_versions": [_candidate_record(
        dispatch, channel="workbook", scope="workbook", defect_id=defect_id,
        parent_sha256=parent.get("parent_sha256"))]})


# ------------------------------------------------------------------ node registration


MODEL_NODE_ADAPTERS: Mapping[str, Callable[..., dict[str, Any]]] = {
    "M01_RESEARCH_UNIT_SOURCES": m01_research_unit_sources,
    "M02_CREATE_UNIT_DOMAIN_DATA": m02_create_unit_domain_data,
    "M03_WRITE_UNIT_CONTENT": m03_write_unit_content,
    "M04_CREATE_UNIT_VISUALS": m04_create_unit_visuals,
    "M05_REVIEW_ACTUAL_UNIT": m05_review_actual_unit,
    "M06_REPAIR_NAMED_UNIT_ARTIFACT": m06_repair_named_unit_artifact,
    "M07_REVIEW_ACTUAL_WORKBOOK": m07_review_actual_workbook,
    "M08_REPAIR_NAMED_WORKBOOK_DEFECT": m08_repair_named_workbook_defect,
}


def build_model_nodes(context: ModelNodeContext) -> dict[str, Callable[[Mapping[str, Any]],
                                                                      dict[str, Any]]]:
    """Bind the eight adapters to one context for `add_node` registration by N20/N30."""

    return {job_id: (lambda packet, _adapter=adapter: _adapter(packet, context))
            for job_id, adapter in MODEL_NODE_ADAPTERS.items()}


def transport_call_sites() -> list[str]:
    """Every function in this module that invokes a transport, for audit by test."""

    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    sites: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if (isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "execute"):
                sites.append(node.name)
    return sorted(set(sites))
