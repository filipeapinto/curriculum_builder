"""Targeted repair engine: D17-D21 of spec section 6.2 and section 12.

Owns finding classification, one-partition-member repair planning, deterministic
vs. model routing, boundary-checked admission, and retest dispatch. Shared by the
unit repair cycle here and reused by the workbook repair cycle N32 builds over
`repair_requests`-shaped state (spec section 12's boundary/diff/invalidation-DAG
machinery is one engine, not a per-caller copy).

None of this module's functions carry a `NODE_CATALOGUE` row: D16-D23 are not
registered as graph nodes yet (that registration is N32's write, once
`workbook.py` exists to dispatch alongside them), so these are plain, narrowly
scoped `(state, runtime_context) -> update` callables in the same shape N23's
`model_nodes.py` uses for D90/D91 -- state-projected by hand, not by
`nodes.deterministic_node()`. A future registration step binds them to their
catalogue rows without changing this module.

Every finding this engine classifies is normalized to spec section 12's
`{finding_id, evidence_key, owner, boundary, parent_hash, fingerprint}` shape.
Owner is never trusted from a model: D08/D09/D12/D14 stamp `owner` themselves
(code-owned), and a model review's own `category` field is deliberately never
read as an owner -- `owner_for_review_category()` is the one place a category
string is mapped to the five-owner vocabulary, and an unmapped category is a
system fault, not a silent guess.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from . import reducers
from .nodes import (
    SystemFailure,
    candidate_payload,
    canonical_digest,
    latest_model_candidate,
    require,
    staged_dispatch,
    stream_id,
    worker_packet,
)

__all__ = [
    "REPAIR_OWNERS",
    "CHANNEL_BY_OWNER",
    "MODEL_ONLY_OWNERS",
    "DETERMINISTIC_ONLY_OWNERS",
    "CONDITIONAL_OWNERS",
    "RETEST_FIRST_NODE",
    "RETEST_ORDER_BY_OWNER",
    "MAX_REPAIR_CHILDREN_PER_CHAIN",
    "MAX_FINGERPRINT_REPEATS",
    "DETERMINISTIC_REPAIR_CANDIDATE_KIND",
    "RepairEngineError",
    "owner_for_review_category",
    "normalize_findings",
    "finding_fingerprint",
    "route_owner",
    "json_pointer_diff",
    "within_boundary",
    "D17_CLASSIFY_UNIT_FINDINGS",
    "D18_PLAN_TARGETED_UNIT_REPAIR",
    "D19_ROUTE_UNIT_REPAIR",
    "D20_ADMIT_UNIT_REPAIR",
    "D21_RETEST_REQUIRED_DESCENDANTS",
]


class RepairEngineError(SystemFailure):
    """A repair-engine invariant broke. Always a system fault, never a product one."""


# The exact five-owner vocabulary of spec section 12's table. Nothing outside
# this set is a legal `owner`; a finding naming anything else fails closed.
REPAIR_OWNERS: tuple[str, ...] = (
    "source interpretation",
    "curriculum domain",
    "unit content",
    "unit visual",
    "unit layout",
)

# The artifact-versions channel each owner's repair targets. Source
# interpretation shares the domain channel: an unsourced or wrongly-cited fact
# is a pointer inside the same admitted domain body a curriculum-domain defect
# would touch, differing only in which pointers are named and in dispatch
# eligibility below.
CHANNEL_BY_OWNER: Mapping[str, str] = {
    "curriculum domain": "domain",
    "source interpretation": "domain",
    "unit content": "content",
    "unit visual": "visuals",
    "unit layout": "layout",
}

# Spec section 12's per-owner repair-behavior column, collapsed to a decidable
# table. A curriculum-domain or unit-content defect is model-owned outright.
# Layout has a deterministic renderer/template repair path and no model path in
# this generation, so it is always deterministic. Source interpretation could
# legally refetch deterministically when a locator remains authorized; this
# generation always routes it to M06 rather than re-implementing a fetcher here
# (repair.py owns the routing table, not a second source-retrieval stack), and
# that choice is exactly the one spec section 12 leaves open ("M06 repairs only
# the named interpretation ... admission is code-owned"). Unit visual is the one
# genuinely conditional row: an authoritative/library visual is always
# rerun deterministically (a model may never assert authoritative circuit/pin
# detail per spec section 13), and a non-authoritative asset is model-eligible.
MODEL_ONLY_OWNERS: frozenset[str] = frozenset(
    {"curriculum domain", "unit content", "source interpretation"}
)
DETERMINISTIC_ONLY_OWNERS: frozenset[str] = frozenset({"unit layout"})
CONDITIONAL_OWNERS: frozenset[str] = frozenset({"unit visual"})

# The first deterministic node of each owner's fixed retest chain (spec section
# 12's table). Every value here is a real `RESUME_REENTRY_DESTINATIONS` member
# of `unit_graph.py`; the remaining steps of a chain are not dispatched by D21 at
# all -- they are the already-wired unit-path edges the first node's own success
# guard reaches on its own (D07 -> D08 -> D09 -> D10 -> ... -> D16).
RETEST_FIRST_NODE: Mapping[str, str] = {
    "source interpretation": "D07_CORRELATE_AND_ADMIT_SOURCES",
    "curriculum domain": "D08_VALIDATE_DOMAIN",
    "unit content": "D09_VALIDATE_CONTENT",
    "unit visual": "D10_COMPILE_VISUAL_BRIEFS",
    "unit layout": "D13_RENDER_UNIT",
}

RETEST_ORDER_BY_OWNER: Mapping[str, tuple[str, ...]] = {
    "source interpretation": (
        "D07_CORRELATE_AND_ADMIT_SOURCES", "D08_VALIDATE_DOMAIN", "D09_VALIDATE_CONTENT",
        "D10_COMPILE_VISUAL_BRIEFS", "D13_RENDER_UNIT", "D14_INVENTORY_AND_INSPECT_UNIT_PAGES",
        "D15_FREEZE_UNIT_REVIEW_PACKET", "D16_REDUCE_UNIT_EVIDENCE",
    ),
    "curriculum domain": (
        "D08_VALIDATE_DOMAIN", "D09_VALIDATE_CONTENT", "D10_COMPILE_VISUAL_BRIEFS",
        "D13_RENDER_UNIT", "D14_INVENTORY_AND_INSPECT_UNIT_PAGES",
        "D15_FREEZE_UNIT_REVIEW_PACKET", "D16_REDUCE_UNIT_EVIDENCE",
    ),
    "unit content": (
        "D09_VALIDATE_CONTENT", "D10_COMPILE_VISUAL_BRIEFS", "D13_RENDER_UNIT",
        "D14_INVENTORY_AND_INSPECT_UNIT_PAGES", "D15_FREEZE_UNIT_REVIEW_PACKET",
        "D16_REDUCE_UNIT_EVIDENCE",
    ),
    "unit visual": (
        "D10_COMPILE_VISUAL_BRIEFS", "D13_RENDER_UNIT", "D14_INVENTORY_AND_INSPECT_UNIT_PAGES",
        "D15_FREEZE_UNIT_REVIEW_PACKET", "D16_REDUCE_UNIT_EVIDENCE",
    ),
    "unit layout": (
        "D13_RENDER_UNIT", "D14_INVENTORY_AND_INSPECT_UNIT_PAGES",
        "D15_FREEZE_UNIT_REVIEW_PACKET", "D16_REDUCE_UNIT_EVIDENCE",
    ),
}

# Frozen limits (spec section 12): three repair children per owner/finding
# chain, two occurrences of the same fingerprint. The earliest reached bound
# controls -- `D18_PLAN_TARGETED_UNIT_REPAIR` checks both and never dispatches
# a fourth child or a third repeat of the same defect.
MAX_REPAIR_CHILDREN_PER_CHAIN = 3
MAX_FINGERPRINT_REPEATS = 2

# A model review's own `category` vocabulary is never trusted directly; this is
# the one code-owned mapping from a reviewer's free-text category to the fixed
# five-owner vocabulary. Substring match on a normalized (lowercased) category
# keeps the rubric free to phrase categories in prose while still refusing an
# unmapped one rather than guessing.
_REVIEW_CATEGORY_OWNER_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("source", "source interpretation"),
    ("citation", "source interpretation"),
    ("domain", "curriculum domain"),
    ("fact", "curriculum domain"),
    ("content", "unit content"),
    ("prose", "unit content"),
    ("pedagog", "unit content"),
    ("readab", "unit content"),
    ("safety", "unit content"),
    ("bloom", "unit content"),
    ("visual", "unit visual"),
    ("image", "unit visual"),
    ("diagram", "unit visual"),
    ("layout", "unit layout"),
    ("page", "unit layout"),
    ("render", "unit layout"),
)

DETERMINISTIC_REPAIR_CANDIDATE_KIND = "deterministic_repair_candidate"


def owner_for_review_category(category: Any) -> str | None:
    """Map one M05 review `category` string to a code-owned owner, or None.

    Never returns the model's own words: the return value is always one member
    of `REPAIR_OWNERS`, decided by this frozen table, or None when no keyword
    matches -- which the caller treats as an unknown-owner system fault, not a
    best guess.
    """

    if not isinstance(category, str) or not category:
        return None
    lowered = category.lower()
    for keyword, owner in _REVIEW_CATEGORY_OWNER_KEYWORDS:
        if keyword in lowered:
            return owner
    return None


def finding_fingerprint(owner: str, boundary: Sequence[str], message: Any) -> str:
    """The stable identity of a defect across repeated repair attempts.

    Keyed on owner, boundary pointers, and message -- not on `finding_id` (which
    a fresh classification pass may mint differently) and not on attempt number
    (which must never enter a fingerprint that exists to detect repeated
    failure across attempts).
    """

    return canonical_digest({"owner": owner, "boundary": sorted(boundary), "message": str(message)})


def normalize_findings(
    raw_findings: Sequence[Mapping[str, Any]],
    *,
    unit_id: str,
    source_node: str,
    artifact_heads: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Normalize a raw findings list to spec section 12's one shape.

    Fails closed (`SystemFailure`) on any finding with no owner, an owner
    outside the fixed vocabulary, or a missing pointer -- `D17` never routes a
    zero- or unknown-owner finding into a partition; it raises before one is
    built. A caller with only one already-classified finding (the D91
    model-repair-failure case) still goes through this function, so the same
    checks apply uniformly.
    """

    normalized: list[dict[str, Any]] = []
    for raw in raw_findings:
        if not isinstance(raw, Mapping):
            raise SystemFailure(
                "invalid_input", "a finding must be a JSON object", {"source_node": source_node}
            )
        owner = raw.get("owner")
        if owner not in REPAIR_OWNERS:
            raise SystemFailure(
                "invalid_input",
                f"finding declares owner {owner!r}, which is not one of the five known owners",
                {"unit_id": unit_id, "source_node": source_node, "owner": owner},
            )
        pointer = raw.get("pointer")
        if not isinstance(pointer, str) or not pointer:
            raise SystemFailure(
                "invalid_input", "finding declares no boundary pointer",
                {"unit_id": unit_id, "owner": owner},
            )
        channel = CHANNEL_BY_OWNER[owner]
        parent_head = artifact_heads.get(stream_id(unit_id, channel))
        parent_hash = parent_head.get("hash") if isinstance(parent_head, Mapping) else None
        message = raw.get("message", "")
        finding_id = canonical_digest(
            {"unit_id": unit_id, "owner": owner, "pointer": pointer, "message": str(message)}
        )
        raw_facts = raw.get("allowed_facts")
        allowed_facts = dict(raw_facts) if isinstance(raw_facts, Mapping) else {}
        normalized.append(
            {
                "finding_id": finding_id,
                "evidence_key": str(raw.get("check_id", source_node)),
                "owner": owner,
                "boundary": pointer,
                "parent_hash": parent_hash,
                "fingerprint": finding_fingerprint(owner, [pointer], message),
                "message": str(message),
                "unit_id": unit_id,
                "source_node": source_node,
                "allowed_facts": allowed_facts,
            }
        )
    return normalized


def route_owner(owner: str, *, state: Mapping[str, Any], findings: Sequence[Mapping[str, Any]]) -> str:
    """Deterministic-vs-model dispatch for one owner's findings (spec section 12)."""

    if owner in DETERMINISTIC_ONLY_OWNERS:
        return "deterministic"
    if owner in MODEL_ONLY_OWNERS:
        return "model"
    if owner not in CONDITIONAL_OWNERS:
        raise RepairEngineError("integrity", f"owner {owner!r} has no dispatch rule", {"owner": owner})
    # unit visual: deterministic only if every named key is an authoritative or
    # library visual brief; a model may never touch one (spec section 13).
    briefs = {
        brief.get("key"): brief
        for brief in state.get("visual_briefs", [])
        if isinstance(brief, Mapping)
    }
    for finding in findings:
        key = str(finding.get("boundary", "")).strip("/").split("/")[-1]
        brief = briefs.get(key)
        authoritative = bool(brief.get("authoritative")) if isinstance(brief, Mapping) else False
        if not authoritative:
            return "model"
    return "deterministic"


def _escape_token(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def json_pointer_diff(parent: Any, child: Any, path: str = "") -> set[str]:
    """Every leaf JSON pointer at which ``parent`` and ``child`` differ."""

    if parent == child:
        return set()
    if isinstance(parent, Mapping) and isinstance(child, Mapping):
        diffs: set[str] = set()
        for key in sorted(set(parent) | set(child)):
            sub = f"{path}/{_escape_token(str(key))}"
            if key not in parent or key not in child:
                diffs.add(sub)
            else:
                diffs |= json_pointer_diff(parent[key], child[key], sub)
        return diffs
    if isinstance(parent, list) and isinstance(child, list):
        diffs = set()
        for index in range(max(len(parent), len(child))):
            sub = f"{path}/{index}"
            if index >= len(parent) or index >= len(child):
                diffs.add(sub)
            else:
                diffs |= json_pointer_diff(parent[index], child[index], sub)
        return diffs
    return {path or "/"}


def within_boundary(pointer: str, allowed: Sequence[str]) -> bool:
    """Whether ``pointer`` is exactly, or nested under, one declared boundary pointer."""

    return any(pointer == allow or pointer.startswith(f"{allow}/") for allow in allowed)


def _guard(node_id: str, value: str, **detail: Any) -> dict[str, Any]:
    return {"node": node_id, "value": value, "detail": detail}


def _status_update(state: Mapping[str, Any], unit_id: str, target: str) -> dict[str, str]:
    """`{unit_id: target}` only when `reducers.UNIT_STATUS_TRANSITIONS` allows it.

    Mirrors `acceptance._status_update` (duplicated rather than imported: this
    module must not import `acceptance`, which itself imports `repair`). See
    that function's docstring for why a first-real-run repair classification
    reached directly from `SELECTED` legally records no transition.
    """

    current = (state.get("unit_status") or {}).get(unit_id)
    if current is None:
        return {unit_id: target} if target in reducers.INITIAL_UNIT_STATUSES else {}
    if target in reducers.UNIT_STATUS_TRANSITIONS.get(current, frozenset()):
        return {unit_id: target}
    return {}


def _attempt_key(unit_id: str, owner: str, fingerprint: str) -> str:
    return f"repair|{unit_id}|{owner}|{fingerprint}"


def _repeat_key(unit_id: str, owner: str, fingerprint: str) -> str:
    return f"repeat|{unit_id}|{owner}|{fingerprint}"


# --------------------------------------------------------------------------
# D17_CLASSIFY_UNIT_FINDINGS
# --------------------------------------------------------------------------


def D17_CLASSIFY_UNIT_FINDINGS(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Total one-owner partition of the current findings, or honest exhaustion.

    Reads whichever repairable branch reached it: a `pending_guard` carrying a
    `findings` list from D08/D09/D12/D14/D16, or a `pending_failure` a D91
    model-repair classification left with no structured findings at all. Every
    blocking finding appears in exactly one owner's partition entry; an
    unowned or cross-owner-contaminated finding is a system fault, never a
    silently dropped one (spec section 6.2 D17 row).
    """

    unit_id = state.get("selected_unit_id")
    require(isinstance(unit_id, str) and bool(unit_id), "invalid_input", "no unit is selected")
    require(
        unit_id not in (state.get("accepted_unit_receipts") or {}),
        "integrity",
        "an accepted unit can never re-enter finding classification",
        unit_id=unit_id,
    )

    artifact_heads = state.get("artifact_heads") or {}
    guard_record = state.get("pending_guard")
    pending_failure = state.get("pending_failure")
    update: dict[str, Any] = {}

    if isinstance(pending_failure, Mapping) and pending_failure.get("classification") == "repair":
        job_id = pending_failure.get("job_id")
        owner = {
            "M02_CREATE_UNIT_DOMAIN_DATA": "curriculum domain",
            "M03_WRITE_UNIT_CONTENT": "unit content",
            "M04_CREATE_UNIT_VISUALS": "unit visual",
            "M01_RESEARCH_UNIT_SOURCES": "source interpretation",
            "M06_REPAIR_NAMED_UNIT_ARTIFACT": None,
        }.get(job_id)
        require(
            owner in REPAIR_OWNERS,
            "invalid_input",
            f"model failure for {job_id!r} maps to no known repair owner",
            job_id=job_id,
        )
        raw_findings = [
            {
                "owner": owner,
                "pointer": f"/{CHANNEL_BY_OWNER[owner]}",
                "check_id": pending_failure.get("failure_class"),
                "message": pending_failure.get("detail") or pending_failure.get("message") or "",
            }
        ]
        source_node = "D91_CLASSIFY_MODEL_FAILURE"
        update["pending_failure"] = None
    else:
        require(isinstance(guard_record, Mapping), "invalid_input", "D17 has no findings to classify")
        detail = guard_record.get("detail") if isinstance(guard_record.get("detail"), Mapping) else {}
        raw_findings = detail.get("findings")
        require(
            isinstance(raw_findings, list) and bool(raw_findings),
            "invalid_input",
            "D17 was routed with an empty or missing findings list",
        )
        source_node = str(guard_record.get("node") or "")

    normalized = normalize_findings(
        raw_findings, unit_id=unit_id, source_node=source_node, artifact_heads=artifact_heads
    )

    by_owner: dict[str, list[dict[str, Any]]] = {}
    for finding in normalized:
        by_owner.setdefault(finding["owner"], []).append(finding)

    counters = dict(state.get("attempt_counters") or {})
    exhausted: list[dict[str, Any]] = []
    partitions: list[dict[str, Any]] = []
    for owner in REPAIR_OWNERS:
        members = by_owner.get(owner)
        if not members:
            continue
        # D17 owns only the repeated-fingerprint bound; the numeric attempt
        # bound is D18's row of spec section 6.2 ("D18 ... attempt bound =
        # exhaustion"), checked once D18 has reserved the next attempt ordinal.
        fingerprint = canonical_digest(sorted(m["fingerprint"] for m in members))
        repeat_key = _repeat_key(unit_id, owner, fingerprint)
        prior_repeats = int(counters.get(repeat_key, 0))
        if prior_repeats >= MAX_FINGERPRINT_REPEATS:
            exhausted.append({"owner": owner, "fingerprint": fingerprint, "bound": "fingerprint_bound", "repeats": prior_repeats})
            continue
        attempt_key = _attempt_key(unit_id, owner, fingerprint)
        prior_attempts = int(counters.get(attempt_key, 0))
        partitions.append(
            {
                "key": canonical_digest({"unit_id": unit_id, "owner": owner, "fingerprint": fingerprint, "attempt": prior_attempts + 1}),
                "unit_id": unit_id,
                "owner": owner,
                "findings": members,
                "fingerprint": fingerprint,
                "prior_repeats": prior_repeats,
                "prior_attempts": prior_attempts,
                "source_node": source_node,
            }
        )

    if exhausted:
        update.update(
            {
                "finding_partitions": partitions,
                "unit_status": _status_update(state, unit_id, "REPAIRING"),
                "pending_guard": _guard(
                    "D17_CLASSIFY_UNIT_FINDINGS", "convergence_exhausted",
                    unit_id=unit_id, exhausted=exhausted,
                ),
                "terminal_candidate": {
                    "kind": "CONVERGENCE_EXHAUSTED",
                    "bound": exhausted[0]["bound"],
                    "counters": counters,
                    "fingerprints": [dict(item) for item in exhausted],
                    "last_findings": normalized,
                },
            }
        )
        return update

    require(bool(partitions), "invalid_input", "no owner produced a repair partition")

    update.update(
        {
            "finding_partitions": partitions,
            "unit_status": _status_update(state, unit_id, "REPAIRING"),
            "pending_guard": _guard(
                "D17_CLASSIFY_UNIT_FINDINGS", "partition_complete",
                unit_id=unit_id, owners=[entry["owner"] for entry in partitions],
            ),
        }
    )
    return update


# --------------------------------------------------------------------------
# D18_PLAN_TARGETED_UNIT_REPAIR
# --------------------------------------------------------------------------


def D18_PLAN_TARGETED_UNIT_REPAIR(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Select exactly one partition member, in fixed owner order, and plan its repair."""

    unit_id = state.get("selected_unit_id")
    require(isinstance(unit_id, str) and bool(unit_id), "invalid_input", "no unit is selected")

    partitions = [
        entry
        for entry in state.get("finding_partitions") or []
        if isinstance(entry, Mapping) and entry.get("unit_id") == unit_id
    ]
    require(bool(partitions), "invalid_input", "D18 requires at least one classified partition")

    resolved = {
        entry.get("request_key")
        for entry in state.get("retest_results") or []
        if isinstance(entry, Mapping) and entry.get("unit_id") == unit_id and entry.get("resolved")
    }
    open_requests = {
        entry.get("partition_key")
        for entry in state.get("repair_requests") or []
        if isinstance(entry, Mapping)
        and entry.get("unit_id") == unit_id
        and entry.get("key") not in resolved
    }

    latest_by_owner: dict[str, dict[str, Any]] = {}
    for entry in partitions:
        latest_by_owner[entry["owner"]] = entry

    selected = None
    for owner in REPAIR_OWNERS:
        entry = latest_by_owner.get(owner)
        if entry is None or entry["key"] in open_requests:
            continue
        selected = entry
        break
    require(selected is not None, "invalid_input", "every classified partition already has an open repair request")

    counters = dict(state.get("attempt_counters") or {})
    attempt_key = _attempt_key(unit_id, selected["owner"], selected["fingerprint"])
    ordinal = int(counters.get(attempt_key, 0)) + 1
    if ordinal > MAX_REPAIR_CHILDREN_PER_CHAIN:
        return {
            "pending_guard": _guard(
                "D18_PLAN_TARGETED_UNIT_REPAIR", "convergence_exhausted",
                unit_id=unit_id, owner=selected["owner"], ordinal=ordinal,
            ),
            "terminal_candidate": {
                "kind": "CONVERGENCE_EXHAUSTED",
                "bound": "attempt_bound",
                "counters": counters,
                "fingerprints": [selected["fingerprint"]],
                "last_findings": selected["findings"],
            },
        }

    channel = CHANNEL_BY_OWNER[selected["owner"]]
    stream = stream_id(unit_id, channel)
    boundary_pointers = sorted({finding["boundary"] for finding in selected["findings"]})
    parent_hash = next(
        (finding["parent_hash"] for finding in selected["findings"] if finding.get("parent_hash")),
        None,
    )
    allowed_facts: dict[str, Any] = {}
    for finding in selected["findings"]:
        allowed_facts.update(finding.get("allowed_facts") or {})

    request = {
        "key": canonical_digest({"partition_key": selected["key"], "attempt": ordinal}),
        "partition_key": selected["key"],
        "unit_id": unit_id,
        "owner": selected["owner"],
        "channel": channel,
        "stream": stream,
        "finding_ids": [finding["finding_id"] for finding in selected["findings"]],
        "boundary": {"json_pointers": boundary_pointers},
        "parent_hash": parent_hash,
        "allowed_facts": allowed_facts,
        "next_child_version": None,
        "invalidated_descendants": list(RETEST_ORDER_BY_OWNER[selected["owner"]]),
        "retest_order": list(RETEST_ORDER_BY_OWNER[selected["owner"]]),
        "attempt_ordinal": ordinal,
        "fingerprint": selected["fingerprint"],
        "prior_repeats": selected["prior_repeats"],
        "max_children": MAX_REPAIR_CHILDREN_PER_CHAIN,
        "max_fingerprint_repeats": MAX_FINGERPRINT_REPEATS,
    }

    return {
        "attempt_counters": {attempt_key: ordinal},
        "repair_requests": [request],
        "pending_guard": _guard(
            "D18_PLAN_TARGETED_UNIT_REPAIR", "repair_planned",
            unit_id=unit_id, request_key=request["key"],
        ),
    }


# --------------------------------------------------------------------------
# D19_ROUTE_UNIT_REPAIR
# --------------------------------------------------------------------------


def _apply_pointer(body: Any, pointer: str, value: Any) -> Any:
    """Return a copy of ``body`` with ``pointer`` (RFC 6901) set to ``value``."""

    tokens = [tok.replace("~1", "/").replace("~0", "~") for tok in pointer.strip("/").split("/") if tok != ""]
    if not tokens:
        return json.loads(json.dumps(value))
    root = json.loads(json.dumps(body)) if isinstance(body, (dict, list)) else {}
    cursor = root
    for token in tokens[:-1]:
        if isinstance(cursor, list):
            index = int(token)
            cursor = cursor[index]
        else:
            cursor = cursor.setdefault(token, {})
    last = tokens[-1]
    if isinstance(cursor, list):
        index = int(last)
        while len(cursor) <= index:
            cursor.append(None)
        cursor[index] = value
    else:
        cursor[last] = value
    return root


def _deterministic_repair_candidate(
    request: Mapping[str, Any], parent_body: Mapping[str, Any]
) -> dict[str, Any]:
    """Apply a code-owned, boundary-scoped correction to the parent body.

    Every value this writes is derived from the request's own `allowed_facts`
    (facts the run already admitted), never invented: a deterministic repair
    with nothing admitted to correct a pointer with raises rather than leaving
    the pointer untouched, because a no-op staged as a repair would be an
    in-place repair wearing a versioned child's clothes.
    """

    body = parent_body
    allowed_facts = request.get("allowed_facts") or {}
    for pointer in request["boundary"]["json_pointers"]:
        if pointer not in allowed_facts:
            raise SystemFailure(
                "invalid_input",
                f"deterministic repair has no admitted fact for boundary pointer {pointer!r}",
                {"unit_id": request["unit_id"], "owner": request["owner"]},
            )
        body = _apply_pointer(body, pointer, allowed_facts[pointer])
    return body


def D19_ROUTE_UNIT_REPAIR(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Route the planned repair request to its deterministic producer or to M06."""

    unit_id = state.get("selected_unit_id")
    require(isinstance(unit_id, str) and bool(unit_id), "invalid_input", "no unit is selected")

    requests = [
        entry
        for entry in state.get("repair_requests") or []
        if isinstance(entry, Mapping) and entry.get("unit_id") == unit_id
    ]
    require(bool(requests), "invalid_input", "D19 requires a planned repair request")
    request = requests[-1]

    partitions = {
        entry["key"]: entry
        for entry in state.get("finding_partitions") or []
        if isinstance(entry, Mapping) and entry.get("unit_id") == unit_id
    }
    partition = partitions.get(request["partition_key"])
    require(partition is not None, "join", "the routed repair request names no known partition")
    findings = partition["findings"]

    invalidation = {
        "key": canonical_digest({"request_key": request["key"], "kind": "invalidation"}),
        "unit_id": unit_id,
        "request_key": request["key"],
        "owner": request["owner"],
        "invalidated_descendants": request["invalidated_descendants"],
        "retest_order": request["retest_order"],
    }

    route = route_owner(request["owner"], state=state, findings=findings)
    stream = request["stream"]
    heads = state.get("artifact_heads") or {}
    parent_head = heads.get(stream)

    if route == "model":
        artifact_versions = state.get("artifact_versions") or []
        parent_body = None
        if isinstance(parent_head, Mapping):
            for record in artifact_versions:
                if (
                    isinstance(record, Mapping)
                    and record.get("stream") == stream
                    and record.get("hash") == parent_head.get("hash")
                ):
                    parent_body = record.get("body")
                    break
        require(isinstance(parent_body, Mapping), "invalid_input", "no admitted parent body to repair", stream=stream)

        packet = worker_packet(
            run_id=state.get("run_id"),
            episode_id=state.get("episode_id"),
            correlation_key=f"{request['key']}/M06",
            projection={
                "owner": request["owner"],
                "findings": [
                    {
                        "finding_id": finding["finding_id"],
                        "owner": finding["owner"],
                        "pointer": finding["boundary"],
                        "message": finding["message"],
                    }
                    for finding in findings
                ],
                "parent": {
                    "artifact_name": f"{request['channel']}:{unit_id}",
                    "artifact_body": json.dumps(parent_body, sort_keys=True),
                    "channel": request["channel"],
                    "unit_id": unit_id,
                    "parent_sha256": parent_head.get("hash"),
                },
                "boundary": request["boundary"],
                "allowed_facts": request.get("allowed_facts") or {},
                "invalidated_descendants": request["invalidated_descendants"],
                "retest_order": request["retest_order"],
            },
        )
        return {
            "invalidations": [invalidation],
            "pending_packet": staged_dispatch("M06_REPAIR_NAMED_UNIT_ARTIFACT", [packet]),
            "pending_guard": _guard(
                "D19_ROUTE_UNIT_REPAIR", "model_repair", unit_id=unit_id, request_key=request["key"]
            ),
        }

    # Deterministic route: this node both selects and produces the candidate,
    # since D20 is the one and only admission authority and no intervening
    # dispatch node exists on the deterministic side (spec section 12: a
    # deterministic repair producer "receives no prompt").
    parent_body, current_hash, _current_version, _head_tracked, _body_keyed = _current_parent(state, stream)
    new_body = _deterministic_repair_candidate(request, parent_body)
    candidate = {
        "key": canonical_digest({"request_key": request["key"], "kind": "deterministic_candidate"}),
        "record_kind": DETERMINISTIC_REPAIR_CANDIDATE_KIND,
        "pre_admission": True,
        "stream": stream,
        "channel": request["channel"],
        "unit_id": unit_id,
        "request_key": request["key"],
        "owner": request["owner"],
        "parent_sha256": current_hash,
        "addressed_finding_ids": request["finding_ids"],
        "body": new_body,
    }
    return {
        "invalidations": [invalidation],
        "artifact_versions": [candidate],
        "pending_guard": _guard(
            "D19_ROUTE_UNIT_REPAIR", "deterministic_repair", unit_id=unit_id, request_key=request["key"]
        ),
    }


# --------------------------------------------------------------------------
# D20_ADMIT_UNIT_REPAIR
# --------------------------------------------------------------------------


def _latest_deterministic_candidate(
    artifact_versions: Sequence[Any], *, stream: str, request_key: str
) -> dict[str, Any] | None:
    matches = [
        dict(record)
        for record in artifact_versions
        if isinstance(record, Mapping)
        and record.get("record_kind") == DETERMINISTIC_REPAIR_CANDIDATE_KIND
        and record.get("stream") == stream
        and record.get("request_key") == request_key
    ]
    return matches[-1] if matches else None


# Bookkeeping keys this repair engine's own admitted records always carry,
# never a channel's content. Used only to recover a record's meaningful
# content when the record itself carries no `body` key (see `_record_content`
# below); domain/content admit a `body`-keyed record (`nodes/domain.py`,
# `nodes/content.py`) and are read directly, so this set is only consulted
# for a channel like layout that is not.
_RECORD_BOOKKEEPING_KEYS: frozenset[str] = frozenset(
    {
        "key", "stream", "version", "parent_hash", "hash", "record_kind",
        "pre_admission", "request_key", "owner", "attempt", "channel",
        "unit_id", "minted_by", "addressed_finding_ids",
    }
)


def _record_content(record: Mapping[str, Any]) -> dict[str, Any]:
    """The meaningful content fields of an admitted artifact record.

    Domain/content nest their content under a `body` key (`nodes/domain.py`,
    `nodes/content.py`); layout does not -- `D13_RENDER_UNIT` (`nodes/render
    .py`) writes `pdf_path`/`pdf_sha256`/... directly on the record, alongside
    only this engine's own fixed bookkeeping keys. Reading either shape
    uniformly here is what lets D19's boundary-scoped JSON-pointer patch and
    D20's diff/boundary check apply to a channel regardless of which
    convention its own producer uses, instead of silently seeing an empty
    parent body for a channel that never wraps one.
    """

    if "body" in record:
        return dict(record.get("body") or {})
    return {key: value for key, value in record.items() if key not in _RECORD_BOOKKEEPING_KEYS}


def _current_parent(state: Mapping[str, Any], stream: str) -> tuple[Any, str | None, int, bool, bool]:
    """The current parent body/hash/version of ``stream``, head-tracked or not.

    Domain/content/visuals advance through `artifact_heads` (`advance_head`);
    layout does not (it is admitted by D13 as a plain append-unique version,
    the same convention `review.py` already reads it under). Both shapes
    resolve to one parent here so D20 admits either uniformly, the fourth
    element tells the caller whether `artifact_heads` may legally be written,
    and the fifth tells the caller whether the parent record itself was
    `body`-keyed -- so a child D20 admits stays in the same shape convention
    its own channel's real producer already uses (`D20_ADMIT_UNIT_REPAIR`
    reads this rather than assuming every channel is `body`-keyed).
    """

    heads = state.get("artifact_heads") or {}
    head = heads.get(stream)
    artifact_versions = state.get("artifact_versions") or []
    if isinstance(head, Mapping):
        for record in artifact_versions:
            if (
                isinstance(record, Mapping)
                and record.get("stream") == stream
                and record.get("hash") == head.get("hash")
            ):
                return (
                    _record_content(record), head.get("hash"), int(head.get("version", 0)), True,
                    "body" in record,
                )
        return {}, head.get("hash"), int(head.get("version", 0)), True, True

    candidates = [
        record
        for record in artifact_versions
        if isinstance(record, Mapping)
        and record.get("stream") == stream
        and record.get("record_kind") not in (DETERMINISTIC_REPAIR_CANDIDATE_KIND, "model_candidate")
    ]
    if not candidates:
        return {}, None, 0, False, True
    latest = max(candidates, key=lambda record: record.get("version", 0))
    return (
        _record_content(latest), latest.get("hash"), int(latest.get("version", 0)), False,
        "body" in latest,
    )


def D20_ADMIT_UNIT_REPAIR(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Admit a boundary-checked child atomically, or refuse it as a system fault.

    Recomputes the parent/child diff itself rather than trusting a model's own
    `changed_path_manifest`: a diff pointer outside the declared boundary, or a
    child that does not descend from the current head, is `SystemFailure`
    ("out-of-bound/in-place = system", spec section 6.2 D20 row) -- never a
    routed repairable finding, because a boundary violation is a build/model
    defect, not a product outcome to retry.
    """

    unit_id = state.get("selected_unit_id")
    require(isinstance(unit_id, str) and bool(unit_id), "invalid_input", "no unit is selected")

    requests = [
        entry
        for entry in state.get("repair_requests") or []
        if isinstance(entry, Mapping) and entry.get("unit_id") == unit_id
    ]
    require(bool(requests), "invalid_input", "D20 requires a routed repair request")
    request = requests[-1]
    stream = request["stream"]
    boundary = request["boundary"]["json_pointers"]
    heads = state.get("artifact_heads") or {}
    parent_head = heads.get(stream)
    artifact_versions = state.get("artifact_versions") or []

    parent_body, current_hash, current_version, head_tracked, body_keyed = _current_parent(state, stream)

    model_candidate = latest_model_candidate(artifact_versions, channel=request["channel"], unit_id=unit_id)
    deterministic_candidate = _latest_deterministic_candidate(
        artifact_versions, stream=stream, request_key=request["key"]
    )
    require(
        (model_candidate is not None) != (deterministic_candidate is not None),
        "join",
        "D20 requires exactly one pending repair candidate: model or deterministic",
        unit_id=unit_id,
    )

    if model_candidate is not None:
        payload = candidate_payload(model_candidate, "M06 repair candidate")
        child = payload.get("candidate_child") or {}
        require(isinstance(child, Mapping), "schema_contract", "M06 candidate carries no candidate_child")
        try:
            new_body = json.loads(child.get("artifact_body", ""))
        except (TypeError, ValueError) as error:
            raise SystemFailure(
                "schema_contract", f"M06 candidate_child.artifact_body is not JSON: {error}"
            ) from error
        declared_parent_sha = model_candidate.get("parent_sha256")
    else:
        new_body = deterministic_candidate["body"]
        declared_parent_sha = deterministic_candidate.get("parent_sha256")

    require(
        declared_parent_sha == current_hash,
        "integrity",
        "the repair candidate's declared parent is not the current head (stale repair)",
        stream=stream, declared=declared_parent_sha, current=current_hash,
    )

    diff = json_pointer_diff(parent_body, new_body)
    require(bool(diff), "integrity", "a repair candidate makes no change (in-place, no-op repair)", stream=stream)
    out_of_bound = sorted(pointer for pointer in diff if not within_boundary(pointer, boundary))
    require(
        not out_of_bound,
        "integrity",
        "a repair candidate changed bytes outside its declared boundary",
        stream=stream, out_of_bound=out_of_bound, boundary=boundary,
    )

    child_record: dict[str, Any] = {
        "stream": stream,
        "version": current_version + 1,
        "parent_hash": current_hash,
        "hash": canonical_digest(new_body),
        "minted_by": "targeted_repair_admission",
        "unit_id": unit_id,
        "channel": request["channel"],
        "request_key": request["key"],
        "owner": request["owner"],
        "attempt": request["attempt_ordinal"],
    }
    # Admit the child in the same shape convention its own channel's real
    # producer already uses: `body`-keyed for domain/content (`nodes/domain
    # .py`, `nodes/content.py`), spread at top level for a channel like layout
    # that never wraps one (`nodes/render.py`) -- otherwise a channel's own
    # later real reader (D13/D14 for layout) would silently see a malformed
    # version instead of the admitted repair.
    if body_keyed:
        child_record["body"] = new_body
    else:
        child_record.update(new_body)
    child_record["key"] = canonical_digest({"stream": stream, "hash": child_record["hash"]})

    update: dict[str, Any] = {
        "artifact_versions": [child_record],
        "pending_guard": _guard(
            "D20_ADMIT_UNIT_REPAIR", "repair_admitted",
            unit_id=unit_id, request_key=request["key"], stream=stream,
        ),
    }
    if head_tracked:
        update["artifact_heads"] = {
            stream: {"version": child_record["version"], "parent_hash": child_record["parent_hash"], "hash": child_record["hash"]}
        }
    return update


# --------------------------------------------------------------------------
# D21_RETEST_REQUIRED_DESCENDANTS
# --------------------------------------------------------------------------


def D21_RETEST_REQUIRED_DESCENDANTS(state: Mapping[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Dispatch the earliest node of the fixed retest DAG, or close the frontier.

    Dispatches exactly once per repair admission: the first named node's own
    success guard already re-enters the rest of the normal unit path (D07
    through D16), so this never loops internally and never names a model node
    as the stored destination (spec section 6.2 D92/D21: a model destination in
    a stored frontier is a system fault).
    """

    unit_id = state.get("selected_unit_id")
    require(isinstance(unit_id, str) and bool(unit_id), "invalid_input", "no unit is selected")

    invalidations = [
        entry
        for entry in state.get("invalidations") or []
        if isinstance(entry, Mapping) and entry.get("unit_id") == unit_id
    ]
    require(bool(invalidations), "invalid_input", "D21 requires an admitted invalidation record")
    invalidation = invalidations[-1]

    dispatched = {
        entry.get("request_key")
        for entry in state.get("retest_results") or []
        if isinstance(entry, Mapping) and entry.get("unit_id") == unit_id
    }

    retest_order = invalidation["retest_order"]
    request_key = invalidation["request_key"]
    if not retest_order:
        return {
            "pending_guard": _guard(
                "D21_RETEST_REQUIRED_DESCENDANTS", "retest_frontier_complete", unit_id=unit_id
            )
        }

    result = {
        "key": canonical_digest({"request_key": request_key, "kind": "retest_dispatch"}),
        "unit_id": unit_id,
        "request_key": request_key,
        "owner": invalidation["owner"],
        "retest_order": list(retest_order),
        "dispatched_to": retest_order[0],
        "resolved": True,
    }

    if request_key in dispatched:
        return {
            "pending_guard": _guard(
                "D21_RETEST_REQUIRED_DESCENDANTS", "retest_frontier_complete", unit_id=unit_id
            )
        }

    return {
        "retest_results": [result],
        "pending_guard": _guard(
            "D21_RETEST_REQUIRED_DESCENDANTS", "retest_frontier_incomplete",
            unit_id=unit_id, destination=retest_order[0],
        ),
    }
