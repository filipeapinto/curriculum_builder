"""The one terminal writer for the whole factory (D98).

This is the only module anywhere in the package that may write the `terminal`
channel. Every other node — including the workbook engine's two product-terminal
call sites — reaches a terminal by producing a `terminal_candidate` and letting
this node decide whether the evidence actually supports it.

The decision matters more than any other in the system: a terminal that claims
`UNIT_ACCEPTED` or `COMPLETE` is the run telling a human that real curriculum was
produced and reviewed. So D98 does not trust the guard that proposed the
candidate. It re-derives each terminal's exact precondition from the state it can
see, and a candidate whose evidence is missing, stale, or incomplete is written
as `SYSTEM_FAILURE` with the rejection recorded — never as the success it asked
for, and never as no terminal at all, because an episode that ends without a
terminal record is an episode nobody can audit.
"""

from __future__ import annotations

import dataclasses
from typing import Any

from ..reducers import TERMINAL_KINDS
from . import canonical_digest, deterministic_node, guard, require

__all__ = [
    "TERMINAL_KINDS",
    "TerminalGuard",
    "TERMINAL_GUARDS",
    "TerminalValidation",
    "validate_terminal_candidate",
    "write_terminal",
    "D98_WRITE_TERMINAL",
]


@dataclasses.dataclass(frozen=True, slots=True)
class TerminalGuard:
    """One row of the spec section 14 terminal table."""

    kind: str
    exit_code: int
    resumable: bool
    claims_product_success: bool
    required_fields: tuple[str, ...]


TERMINAL_GUARDS: dict[str, TerminalGuard] = {
    guard_row.kind: guard_row
    for guard_row in (
        TerminalGuard(
            kind="UNIT_ACCEPTED",
            exit_code=0,
            resumable=False,
            claims_product_success=True,
            required_fields=(
                "unit_id",
                "receipt_hash",
                "closure_receipt_hashes",
                "denominator",
                "log_high_water_mark",
                "checkpoint_id",
            ),
        ),
        TerminalGuard(
            kind="COMPLETE",
            exit_code=0,
            resumable=False,
            claims_product_success=True,
            required_fields=(
                "release_audit_key",
                "workbook_hash",
                "coverage",
                "unit_receipt_hashes",
                "log_high_water_mark",
                "checkpoint_id",
            ),
        ),
        TerminalGuard(
            kind="INTERRUPTED",
            exit_code=10,
            resumable=True,
            claims_product_success=False,
            required_fields=("classification", "resume_frontier", "heads", "high_water_marks"),
        ),
        TerminalGuard(
            kind="PAUSED_PREREQUISITE",
            exit_code=11,
            resumable=True,
            claims_product_success=False,
            required_fields=("fact", "attempts", "required_resume_condition", "resume_frontier"),
        ),
        TerminalGuard(
            kind="CONVERGENCE_EXHAUSTED",
            exit_code=12,
            resumable=False,
            claims_product_success=False,
            required_fields=("bound", "counters", "fingerprints", "last_findings"),
        ),
        TerminalGuard(
            kind="SYSTEM_FAILURE",
            exit_code=20,
            resumable=False,
            claims_product_success=False,
            required_fields=("failure", "node", "safe_heads", "audit_high_water_mark"),
        ),
    )
}

_INTERRUPT_CLASSIFICATIONS: frozenset[str] = frozenset({"graceful_signal", "crashed_episode"})
_EXHAUSTION_BOUNDS: frozenset[str] = frozenset({"attempt_bound", "fingerprint_bound"})


@dataclasses.dataclass(frozen=True, slots=True)
class TerminalValidation:
    """The outcome of independently re-deriving a candidate's precondition."""

    accepted: bool
    kind: str | None
    rejections: tuple[str, ...]

    def as_record(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "kind": self.kind,
            "rejections": list(self.rejections),
        }


def _missing_fields(candidate: dict[str, Any], guard_row: TerminalGuard) -> list[str]:
    return [
        f"missing required field {field!r} for {guard_row.kind}"
        for field in guard_row.required_fields
        if candidate.get(field) is None
    ]


def _validate_unit_accepted(candidate: dict[str, Any], projection: dict[str, Any]) -> list[str]:
    rejections: list[str] = []
    if projection["mode"] != "one":
        rejections.append(f"UNIT_ACCEPTED requires mode 'one', state holds {projection['mode']!r}")

    unit_id = candidate.get("unit_id")
    requested = projection["requested_unit_id"]
    if unit_id != requested:
        rejections.append(
            f"UNIT_ACCEPTED names unit {unit_id!r} but the run requested {requested!r}"
        )

    effective_run = projection["effective_run"] or {}
    closure = effective_run.get("target_closure") or []
    if not closure:
        rejections.append("UNIT_ACCEPTED requires a non-empty frozen target closure")
    if unit_id is not None and unit_id not in closure:
        rejections.append(f"UNIT_ACCEPTED names unit {unit_id!r}, which is outside the closure")

    accepted = projection["accepted_unit_receipts"]
    unaccepted = [member for member in closure if member not in accepted]
    if unaccepted:
        rejections.append(
            f"UNIT_ACCEPTED requires an accepted receipt for the entire closure; "
            f"missing {sorted(unaccepted)}"
        )

    declared_closure = candidate.get("closure_receipt_hashes") or {}
    if not isinstance(declared_closure, dict):
        rejections.append("closure_receipt_hashes must be a mapping of unit id to receipt hash")
    else:
        for member in closure:
            receipt = accepted.get(member)
            current = receipt.get("receipt_hash") if isinstance(receipt, dict) else None
            if current is None:
                continue
            if declared_closure.get(member) != current:
                rejections.append(
                    f"closure receipt hash for {member!r} is stale "
                    f"(claimed {declared_closure.get(member)!r}, current {current!r})"
                )

    target_receipt = accepted.get(unit_id) if unit_id is not None else None
    if not isinstance(target_receipt, dict):
        rejections.append(f"no accepted receipt exists for the target unit {unit_id!r}")
    elif target_receipt.get("receipt_hash") != candidate.get("receipt_hash"):
        rejections.append(
            "the candidate's target receipt hash is not the current accepted receipt hash"
        )

    rejections.extend(_validate_checkpoint(candidate, projection, "UNIT_ACCEPTED"))
    return rejections


def _validate_complete(candidate: dict[str, Any], projection: dict[str, Any]) -> list[str]:
    rejections: list[str] = []
    if projection["mode"] != "all":
        rejections.append(f"COMPLETE requires mode 'all', state holds {projection['mode']!r}")

    audits = projection["final_release_audits"]
    if not audits:
        rejections.append("COMPLETE requires a final release audit")
        audit = None
    else:
        audit = audits[-1]
        if not isinstance(audit, dict) or audit.get("result") != "PASS":
            rejections.append("COMPLETE requires the final release audit to pass")
        if audit.get("key") != candidate.get("release_audit_key"):
            rejections.append("the candidate names a release audit that is not the current one")

    workbook_head = projection["workbook_head"] or {}
    current_workbook = None
    for value in workbook_head.values():
        if isinstance(value, dict):
            current_workbook = value.get("hash")
    if current_workbook is None:
        rejections.append("COMPLETE requires a current workbook head")
    elif candidate.get("workbook_hash") != current_workbook:
        rejections.append(
            "the candidate's workbook hash is not the current workbook head hash"
        )
    if isinstance(audit, dict) and audit.get("workbook_hash") not in (None, current_workbook):
        rejections.append("the final release audit was computed against a superseded workbook")

    effective_run = projection["effective_run"] or {}
    ordered = list(effective_run.get("ordered_unit_ids") or [])
    accepted = projection["accepted_unit_receipts"]
    if not ordered:
        rejections.append("COMPLETE requires a non-empty frozen manifest order")
    receipt_ids = sorted(accepted)
    if sorted(ordered) != receipt_ids:
        rejections.append(
            "COMPLETE requires exact manifest coverage; "
            f"manifest {sorted(ordered)} vs accepted {receipt_ids}"
        )

    declared = candidate.get("unit_receipt_hashes") or {}
    if not isinstance(declared, dict):
        rejections.append("unit_receipt_hashes must be a mapping of unit id to receipt hash")
    else:
        if sorted(declared) != sorted(ordered):
            rejections.append(
                "the candidate's unit receipt set is not exactly the frozen manifest order"
            )
        for unit_id in ordered:
            receipt = accepted.get(unit_id)
            current = receipt.get("receipt_hash") if isinstance(receipt, dict) else None
            if current is not None and declared.get(unit_id) != current:
                rejections.append(f"unit receipt hash for {unit_id!r} is stale")

    rejections.extend(_validate_checkpoint(candidate, projection, "COMPLETE"))
    return rejections


def _validate_checkpoint(
    candidate: dict[str, Any], projection: dict[str, Any], kind: str
) -> list[str]:
    rejections: list[str] = []
    checkpoints = projection["checkpoint_metadata"]
    if not checkpoints:
        rejections.append(f"{kind} requires checkpoint correlation metadata")
        return rejections
    latest = checkpoints[-1]
    current_id = latest.get("checkpoint_id") if isinstance(latest, dict) else None
    if candidate.get("checkpoint_id") != current_id:
        rejections.append(
            f"{kind} names checkpoint {candidate.get('checkpoint_id')!r}, "
            f"which is not the current checkpoint {current_id!r}"
        )
    evidence_entries = projection["evidence_index_entries"]
    declared_mark = candidate.get("log_high_water_mark")
    if isinstance(declared_mark, int) and declared_mark > len(evidence_entries):
        rejections.append(
            f"{kind} claims a log high-water mark of {declared_mark} "
            f"above the {len(evidence_entries)} recorded evidence entries"
        )
    return rejections


def _validate_interrupted(candidate: dict[str, Any], projection: dict[str, Any]) -> list[str]:
    rejections: list[str] = []
    classification = candidate.get("classification")
    if classification not in _INTERRUPT_CLASSIFICATIONS:
        rejections.append(
            f"INTERRUPTED requires a signal or crash classification, got {classification!r}"
        )
    frontier = candidate.get("resume_frontier")
    if not isinstance(frontier, dict) or not frontier:
        rejections.append("INTERRUPTED requires a resume frontier")
    heads = candidate.get("heads")
    if not isinstance(heads, dict):
        rejections.append("INTERRUPTED requires the current artifact heads")
    else:
        current = {
            stream: head.get("hash")
            for stream, head in projection["artifact_heads"].items()
            if isinstance(head, dict)
        }
        stale = sorted(
            stream for stream, value in heads.items() if current.get(stream, value) != value
        )
        if stale:
            rejections.append(f"INTERRUPTED reports stale heads for {stale}")
    marks = candidate.get("high_water_marks")
    if not isinstance(marks, dict):
        rejections.append("INTERRUPTED requires checkpoint and evidence high-water marks")
    return rejections


def _validate_paused(candidate: dict[str, Any], projection: dict[str, Any]) -> list[str]:
    rejections: list[str] = []
    fact = candidate.get("fact")
    if not isinstance(fact, str) or not fact:
        rejections.append("PAUSED_PREREQUISITE requires exactly one named required external fact")
    attempts = candidate.get("attempts")
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 0:
        rejections.append("PAUSED_PREREQUISITE requires a non-negative attempt count")
    condition = candidate.get("required_resume_condition")
    if not isinstance(condition, str) or not condition:
        rejections.append("PAUSED_PREREQUISITE requires a named resume condition")

    # Only an unavailable external fact may pause. A tool, integrity, or schema
    # fault wearing a pause candidate would make a broken run look resumable.
    failure = projection["pending_failure"]
    if isinstance(failure, dict) and failure.get("class") != "pause":
        rejections.append(
            f"PAUSED_PREREQUISITE cannot carry a {failure.get('class')!r} failure "
            f"(cause {failure.get('cause')!r})"
        )
    return rejections


def _validate_exhausted(candidate: dict[str, Any], projection: dict[str, Any]) -> list[str]:
    rejections: list[str] = []
    bound = candidate.get("bound")
    if bound not in _EXHAUSTION_BOUNDS:
        rejections.append(
            f"CONVERGENCE_EXHAUSTED requires a named bound in {sorted(_EXHAUSTION_BOUNDS)}, got {bound!r}"
        )
    counters = candidate.get("counters")
    fingerprints = candidate.get("fingerprints")
    if not isinstance(counters, dict):
        rejections.append("CONVERGENCE_EXHAUSTED requires the attempt counters that were reached")
    if not isinstance(fingerprints, list):
        rejections.append("CONVERGENCE_EXHAUSTED requires the recorded failure fingerprints")

    # Exhaustion is a claim that work was actually attempted and kept failing.
    # With no counters and no fingerprints in state, that claim is unsupported.
    if not projection["attempt_counters"] and not projection["failure_fingerprints"]:
        rejections.append(
            "CONVERGENCE_EXHAUSTED requires recorded attempt counters or failure fingerprints"
        )

    if candidate.get("last_findings") is None:
        rejections.append("CONVERGENCE_EXHAUSTED requires the last findings that failed to converge")

    accepted_all = False
    effective_run = projection["effective_run"] or {}
    closure = effective_run.get("target_closure") or []
    if closure and all(member in projection["accepted_unit_receipts"] for member in closure):
        accepted_all = True
    if accepted_all:
        rejections.append(
            "CONVERGENCE_EXHAUSTED cannot be reached once the full acceptance denominator passed"
        )
    return rejections


def _validate_system_failure(candidate: dict[str, Any], projection: dict[str, Any]) -> list[str]:
    rejections: list[str] = []
    failure = candidate.get("failure")
    if not isinstance(failure, dict):
        rejections.append("SYSTEM_FAILURE requires a typed failure record")
    else:
        if not failure.get("class"):
            rejections.append("SYSTEM_FAILURE requires a failure class")
        if not failure.get("cause"):
            rejections.append("SYSTEM_FAILURE requires a failure cause")
    if not candidate.get("node"):
        rejections.append("SYSTEM_FAILURE requires the node that failed")
    if not isinstance(candidate.get("safe_heads"), dict):
        rejections.append("SYSTEM_FAILURE requires the safe artifact heads")
    mark = candidate.get("audit_high_water_mark")
    if isinstance(mark, bool) or not isinstance(mark, int) or mark < 0:
        rejections.append("SYSTEM_FAILURE requires a non-negative audit high-water mark")
    return rejections


_VALIDATORS = {
    "UNIT_ACCEPTED": _validate_unit_accepted,
    "COMPLETE": _validate_complete,
    "INTERRUPTED": _validate_interrupted,
    "PAUSED_PREREQUISITE": _validate_paused,
    "CONVERGENCE_EXHAUSTED": _validate_exhausted,
    "SYSTEM_FAILURE": _validate_system_failure,
}


def validate_terminal_candidate(
    candidate: Any, projection: dict[str, Any]
) -> TerminalValidation:
    """Independently re-derive whether ``candidate``'s terminal guard actually holds.

    This never consults the guard that produced the candidate. It reads the same
    state D98 reads and answers the question the guard was supposed to answer.
    """

    if not isinstance(candidate, dict):
        return TerminalValidation(False, None, ("terminal candidate is not a JSON object",))

    kind = candidate.get("kind")
    if kind not in TERMINAL_KINDS:
        return TerminalValidation(False, None, (f"unknown terminal kind {kind!r}",))

    guard_row = TERMINAL_GUARDS[kind]
    rejections = _missing_fields(candidate, guard_row)
    rejections.extend(_VALIDATORS[kind](candidate, projection))
    return TerminalValidation(not rejections, kind, tuple(rejections))


def _terminal_record(
    kind: str,
    candidate: dict[str, Any],
    projection: dict[str, Any],
    validation: TerminalValidation,
) -> dict[str, Any]:
    guard_row = TERMINAL_GUARDS[kind]
    record = {
        "kind": kind,
        "episode_id": projection["episode_id"],
        "run_id": projection["run_id"],
        "mode": projection["mode"],
        "requested_unit_id": projection["requested_unit_id"],
        "exit_code": guard_row.exit_code,
        "resumable": guard_row.resumable,
        "evidence": candidate,
        "validation": validation.as_record(),
        "heads": {
            stream: head.get("hash")
            for stream, head in sorted(projection["artifact_heads"].items())
            if isinstance(head, dict)
        },
        "audit_high_water_mark": len(projection["evidence_index_entries"]),
    }
    record["key"] = canonical_digest(record)
    return record


def _rejection_terminal(
    candidate: Any, projection: dict[str, Any], validation: TerminalValidation
) -> dict[str, Any]:
    """Build the SYSTEM_FAILURE record that replaces an unsupported candidate."""

    proposed = candidate.get("kind") if isinstance(candidate, dict) else None
    replacement = {
        "kind": "SYSTEM_FAILURE",
        "failure": {
            "class": "system",
            "cause": "integrity",
            "message": f"terminal candidate {proposed!r} failed independent revalidation",
        },
        "node": "D98_WRITE_TERMINAL",
        "safe_heads": {
            stream: head.get("hash")
            for stream, head in sorted(projection["artifact_heads"].items())
            if isinstance(head, dict)
        },
        "audit_high_water_mark": len(projection["evidence_index_entries"]),
        "rejected_candidate_kind": proposed,
        "rejections": list(validation.rejections),
    }
    return _terminal_record("SYSTEM_FAILURE", replacement, projection, validation)


def write_terminal(projection: dict[str, Any], runtime_context: Any = None) -> dict[str, Any]:
    """Validate the deterministic terminal candidate and write the one episode terminal.

    The sole terminal-writing implementation in the package. N32's two product
    terminals call this function rather than forking it, so there is exactly one
    place where a run can claim it succeeded.
    """

    existing = projection["terminal"]
    require(
        existing is None,
        "persistence",
        "this episode already holds a terminal record",
        existing_kind=existing.get("kind") if isinstance(existing, dict) else None,
    )

    candidate = projection["terminal_candidate"]
    validation = validate_terminal_candidate(candidate, projection)

    if validation.accepted:
        record = _terminal_record(validation.kind, dict(candidate), projection, validation)
    else:
        record = _rejection_terminal(candidate, projection, validation)

    return {
        "terminal": record,
        "terminal_history": [record],
        "pending_guard": guard("D98_WRITE_TERMINAL", "terminated", kind=record["kind"]),
    }


D98_WRITE_TERMINAL = deterministic_node("D98_WRITE_TERMINAL")(write_terminal)
