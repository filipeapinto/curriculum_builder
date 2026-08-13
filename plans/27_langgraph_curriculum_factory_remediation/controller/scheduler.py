#!/usr/bin/env python3
"""Run 27 deterministic node scheduler.

Corrections carried by this module against the Run 26 controller:

* PM-15 — descendant currency is *computed*, never a stored flag. A receipt is
  current only while its recomputed lineage fingerprint, its own final output
  digests, and every ancestor's currency still hold. Changing an admitted
  ancestor therefore invalidates every transitive descendant automatically,
  including descendants whose own bytes did not change.
* PM-17 — admission consumes only schema-valid JSON node results. There is no
  prose, Markdown, or bare ``status:`` line parser anywhere in this package.
* PM-19 — attempts are immutable and write-once, write-set violations fail
  before any merge journal is opened, merges are single-rename atomic with a
  replayable journal, interrupted attempts never merge implicitly, and
  re-admission is a named operation with a machine-readable reason code.
"""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Callable, Sequence

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import jsonschema  # noqa: E402

from core import (  # noqa: E402
    ADMISSIBLE_OUTCOMES,
    DEFAULT_PLAN_DIR,
    ControllerError,
    Graph,
    append_jsonl,
    atomic_write_text,
    canonical_digest,
    covers,
    load_json_strict,
    load_node_result,
    path_digest,
    read_jsonl,
    result_digest,
    serialize_record,
    sha256_bytes,
    sha256_file,
    utc_now,
    write_once_json,
    write_once_text,
)


RECOVERY_REASON_CODES = frozenset(
    {
        "INTERRUPTED_MERGE_COMPLETED",
        "EXTERNAL_PROCESS_KILL",
        "STATE_STORE_CORRUPTION",
        "ANCESTOR_REWORK_REVALIDATION",
    }
)

TERMINAL_MARKERS = ("merged.json", "failed.json", "interrupted.json", "abandoned.json")

RECEIPT_SCHEMA_PATH = DEFAULT_PLAN_DIR / "schemas/scheduler_receipt.schema.v1.json"
ATTEMPT_SCHEMA_PATH = DEFAULT_PLAN_DIR / "schemas/attempt_record.schema.v1.json"


def validate_against(schema_path: Path, record: dict[str, Any], what: str) -> None:
    """The controller's own bookkeeping is schema-bound too, not just node results."""

    schema = load_json_strict(schema_path, what=f"{what} schema")
    try:
        jsonschema.Draft202012Validator(schema).validate(record)
    except jsonschema.ValidationError as error:
        raise ControllerError(
            f"{what} does not validate against {schema_path.name}: {error.message}",
            code="SCHEMA_INVALID_CONTROLLER_RECORD",
        ) from error


class Attempt:
    def __init__(self, root: Path) -> None:
        self.root = root

    @property
    def attempt_id(self) -> str:
        return self.root.name

    @property
    def record_path(self) -> Path:
        return self.root / "attempt_record.json"

    @property
    def journal_path(self) -> Path:
        return self.root / "pending_merge.json"

    @property
    def logs_dir(self) -> Path:
        return self.root / "logs"

    @property
    def events_path(self) -> Path:
        return self.root / "events.jsonl"

    def record(self) -> dict[str, Any]:
        return load_json_strict(self.record_path, what=f"attempt {self.attempt_id}")

    def marker(self) -> str | None:
        for name in TERMINAL_MARKERS:
            if (self.root / name).is_file():
                return name.removesuffix(".json")
        return None

    def state(self) -> str:
        return self.marker() or "open"

    def log_path(self, name: str) -> Path:
        """Attempt-scoped, write-once evidence path."""

        if "/" in name or "\\" in name or name in {"", ".", ".."}:
            raise ControllerError(f"illegal log name: {name!r}", code="ILLEGAL_LOG_NAME")
        return self.logs_dir / name

    def write_log(self, name: str, text: str) -> Path:
        target = self.log_path(name)
        write_once_text(target, text)
        return target

    def event(self, event: str, **fields: Any) -> None:
        append_jsonl(self.events_path, {"at": utc_now(), "event": event, **fields})

    def events(self) -> list[dict[str, Any]]:
        return read_jsonl(self.events_path)


class Scheduler:
    def __init__(
        self,
        graph: Graph,
        state_dir: Path,
        run_id: str = "run27",
        runner: Callable[[Sequence[str], Path], tuple[int, str]] | None = None,
    ) -> None:
        self.graph = graph
        self.state_dir = Path(state_dir).resolve()
        self.run_id = run_id
        self.runner = runner or _default_runner
        self._digest_cache: dict[str, str | None] = {}

    # ---------------------------------------------------------------- layout

    @property
    def receipts_dir(self) -> Path:
        return self.state_dir / "receipts"

    @property
    def attempts_dir(self) -> Path:
        return self.state_dir / "attempts"

    @property
    def audit_path(self) -> Path:
        return self.state_dir / "audit.jsonl"

    def receipt_path(self, node_id: str) -> Path:
        return self.receipts_dir / f"{node_id}.receipt.v1.json"

    def attempt(self, node_id: str, attempt_id: str) -> Attempt:
        root = self.attempts_dir / node_id / attempt_id
        if not root.is_dir():
            raise ControllerError(
                f"{node_id}: unknown attempt {attempt_id}", code="UNKNOWN_ATTEMPT"
            )
        return Attempt(root)

    def attempts(self, node_id: str) -> list[Attempt]:
        root = self.attempts_dir / node_id
        if not root.is_dir():
            return []
        return [Attempt(item) for item in sorted(root.iterdir()) if item.is_dir()]

    # ---------------------------------------------------------------- digests

    def current_path_digest(self, relative: str) -> str | None:
        if relative not in self._digest_cache:
            self._digest_cache[relative] = path_digest(self.graph.repo_root, relative)
        return self._digest_cache[relative]

    def invalidate_digest_cache(self) -> None:
        self._digest_cache.clear()

    def receipt(self, node_id: str) -> dict[str, Any] | None:
        path = self.receipt_path(node_id)
        if not path.is_file():
            return None
        return load_json_strict(path, what=f"{node_id} receipt")

    def receipt_digest(self, node_id: str) -> str | None:
        path = self.receipt_path(node_id)
        return sha256_file(path) if path.is_file() else None

    def lineage_fingerprint(self, node_id: str) -> str:
        """Everything a receipt's continued validity depends on.

        Deliberately excludes the node's own attempt baseline: the baseline is a
        historical fact bound into the receipt, not a currency condition.
        """

        node = self.graph.node(node_id)
        return canonical_digest(
            {
                "node_id": node_id,
                "graph_sha256": self.graph.digest,
                "node_definition_sha256": self.graph.node_definition_digest(node_id),
                "prompt_sha256": self.graph.prompt_digest(node_id),
                "approved_spec_sha256": self.graph.source_spec_digest(),
                "predecessor_receipts": {
                    predecessor: self.receipt_digest(predecessor)
                    for predecessor in sorted(node["depends_on"])
                },
            }
        )

    def baseline(self, node_id: str) -> dict[str, str | None]:
        return {
            relative: self.current_path_digest(relative)
            for relative in self.graph.node(node_id)["writes"]
        }

    # ------------------------------------------------------------- invalidation

    def currency(self, node_id: str, _seen: frozenset[str] = frozenset()) -> dict[str, Any]:
        """PM-15: computed, transitive, and automatic."""

        if node_id in _seen:
            return {"node_id": node_id, "current": False, "reasons": ["dependency_cycle"]}
        seen = _seen | {node_id}
        reasons: list[str] = []
        receipt = self.receipt(node_id)
        if receipt is None:
            return {"node_id": node_id, "current": False, "reasons": ["no_receipt"]}
        if receipt.get("status") not in ADMISSIBLE_OUTCOMES:
            reasons.append(f"status_not_admissible:{receipt.get('status')}")
        expected = self.lineage_fingerprint(node_id)
        if receipt.get("lineage_fingerprint") != expected:
            reasons.append("lineage_fingerprint_changed")
        for relative, recorded in (receipt.get("final_outputs") or {}).items():
            if self.current_path_digest(relative) != recorded:
                reasons.append(f"final_output_changed:{relative}")
        for predecessor in self.graph.node(node_id)["depends_on"]:
            upstream = self.currency(predecessor, seen)
            if not upstream["current"]:
                reasons.append(f"ancestor_not_current:{predecessor}")
        return {"node_id": node_id, "current": not reasons, "reasons": reasons}

    def invalidated_descendants(self, node_id: str) -> list[str]:
        return [
            descendant
            for descendant in self.graph.descendants(node_id)
            if self.receipt(descendant) is not None
            and not self.currency(descendant)["current"]
        ]

    def entry_gate(self) -> dict[str, Any]:
        """Invariant 11: nothing runs without an admitted entry receipt bound to
        the current approved specification digest."""

        entry = self.graph.entry
        receipt = self.receipt(entry)
        if receipt is None:
            return {"admitted": False, "reason": f"no admitted {entry} receipt"}
        approved = self.graph.source_spec_digest()
        if approved is None:
            return {"admitted": False, "reason": "approved specification file is absent"}
        if receipt.get("approved_spec_sha256") != approved:
            return {
                "admitted": False,
                "reason": (
                    f"{entry} receipt binds approved spec "
                    f"{receipt.get('approved_spec_sha256')} but the current approved "
                    f"specification digest is {approved}"
                ),
            }
        state = self.currency(entry)
        if not state["current"]:
            return {"admitted": False, "reason": f"{entry} receipt is not current: {state['reasons']}"}
        if receipt.get("status") != "PASSED":
            return {"admitted": False, "reason": f"{entry} did not pass"}
        return {"admitted": True, "reason": None, "approved_spec_sha256": approved}

    def require_entry_gate(self, node_id: str) -> None:
        if node_id == self.graph.entry:
            return
        gate = self.entry_gate()
        if not gate["admitted"]:
            raise ControllerError(
                f"{node_id}: refused, the specification approval gate is not "
                f"admitted ({gate['reason']})",
                code="ENTRY_GATE_NOT_ADMITTED",
            )

    # ------------------------------------------------------------------ audit

    def audit_event(self, event: str, **fields: Any) -> None:
        append_jsonl(self.audit_path, {"at": utc_now(), "run_id": self.run_id, "event": event, **fields})

    def audit(self) -> list[dict[str, Any]]:
        return read_jsonl(self.audit_path)

    # ---------------------------------------------------------------- attempts

    def begin(self, node_id: str, parent_attempt_id: str | None = None) -> dict[str, Any]:
        self.graph.node(node_id)
        self.require_entry_gate(node_id)
        attempt_id = f"{node_id}-{utc_now().replace(':', '').replace('.', '')}-{uuid.uuid4().hex[:8]}"
        root = self.attempts_dir / node_id / attempt_id
        root.mkdir(parents=True, exist_ok=False)
        record = {
            "schema_version": 1,
            "attempt_id": attempt_id,
            "run_id": self.run_id,
            "node_id": node_id,
            "parent_attempt_id": parent_attempt_id,
            "created_at": utc_now(),
            "graph_sha256": self.graph.digest,
            "node_definition_sha256": self.graph.node_definition_digest(node_id),
            "prompt_sha256": self.graph.prompt_digest(node_id),
            "approved_spec_sha256": self.graph.source_spec_digest(),
            "predecessor_receipt_digests": {
                predecessor: self.receipt_digest(predecessor)
                for predecessor in sorted(self.graph.node(node_id)["depends_on"])
            },
            "baseline": self.baseline(node_id),
            "evidence_dir": (root / "logs").relative_to(self.state_dir).as_posix(),
        }
        validate_against(ATTEMPT_SCHEMA_PATH, record, f"{node_id} attempt record")
        write_once_json(Attempt(root).record_path, record)
        attempt = Attempt(root)
        attempt.event("attempt_created", parent_attempt_id=parent_attempt_id)
        self.audit_event(
            "attempt_created",
            node_id=node_id,
            attempt_id=attempt_id,
            parent_attempt_id=parent_attempt_id,
        )
        return record

    def resume(self, node_id: str, attempt_id: str) -> dict[str, Any]:
        """Invariant 6: an interrupted attempt never merges implicitly."""

        parent = self.attempt(node_id, attempt_id)
        state = parent.state()
        if state == "merged":
            raise ControllerError(
                f"{node_id}: attempt {attempt_id} already merged; resume would "
                "duplicate an admitted receipt",
                code="RESUME_OF_MERGED_ATTEMPT",
            )
        if state == "open":
            write_once_json(
                parent.root / "abandoned.json",
                {"at": utc_now(), "reason": "superseded_by_resume"},
            )
            parent.event("attempt_abandoned", reason="superseded_by_resume")
        child = self.begin(node_id, parent_attempt_id=attempt_id)
        parent.event("resumed_as", child_attempt_id=child["attempt_id"])
        self.audit_event(
            "attempt_resumed",
            node_id=node_id,
            parent_attempt_id=attempt_id,
            attempt_id=child["attempt_id"],
            parent_state=state,
        )
        return child

    def fail_attempt(self, attempt: Attempt, code: str, message: str, **fields: Any) -> None:
        write_once_json(
            attempt.root / "failed.json",
            {"at": utc_now(), "code": code, "message": message, **fields},
        )
        attempt.event("attempt_failed", code=code, message=message, **fields)
        self.audit_event(
            "attempt_failed",
            node_id=attempt.record()["node_id"],
            attempt_id=attempt.attempt_id,
            code=code,
        )

    # ------------------------------------------------------------- validation

    def validate_node_result(self, node_id: str) -> dict[str, Any]:
        """Read-only. Every admission precondition except the merge itself."""

        node = self.graph.node(node_id)
        result = load_node_result(self.graph, node_id)
        relative_result = self.graph.relative_result(node_id)
        problems: list[dict[str, str]] = []

        def fail(code: str, message: str) -> None:
            problems.append({"code": code, "message": message})

        if result["outcome"] not in ADMISSIBLE_OUTCOMES:
            fail("OUTCOME_NOT_ADMISSIBLE", f"outcome {result['outcome']!r} cannot be admitted")

        expected_predecessors = set(node["depends_on"])
        if set(result["predecessor_receipts"]) != expected_predecessors:
            fail(
                "PREDECESSOR_KEYS_MISMATCH",
                f"expected {sorted(expected_predecessors)}, "
                f"got {sorted(result['predecessor_receipts'])}",
            )
        for predecessor, declared in result["predecessor_receipts"].items():
            if predecessor not in expected_predecessors:
                continue
            actual = result_digest(self.graph, predecessor)
            if actual != declared:
                fail(
                    "PREDECESSOR_DIGEST_MISMATCH",
                    f"{predecessor}: result declares {declared} but the current "
                    f"predecessor result digest is {actual}",
                )

        if result["prompt_sha256"] != self.graph.prompt_digest(node_id):
            fail("PROMPT_DIGEST_MISMATCH", "prompt_sha256 does not bind the current prompt")
        approved = self.graph.source_spec_digest()
        if result["source_spec_sha256"] != approved and not (
            approved is None and node_id == self.graph.entry
        ):
            fail("SPEC_DIGEST_MISMATCH", "source_spec_sha256 does not bind the approved specification")

        # Invariant 5: the write-set decision happens before any merge journal.
        for item in result["changed_files"]:
            changed = item["path"]
            if changed == relative_result:
                fail("SELF_HASHING_RESULT", f"the result cannot hash itself: {changed}")
                continue
            if not any(covers(owner, changed) for owner in node["writes"]):
                fail("WRITE_SET_VIOLATION", f"changed path outside the declared write set: {changed}")
                continue
            target = self.graph.repo_root / changed
            if item["change"] == "deleted":
                if target.exists():
                    fail("DELETED_PATH_PRESENT", f"declared deleted but present: {changed}")
            elif not target.is_file():
                fail("CHANGED_FILE_MISSING", f"declared changed file is missing: {changed}")
            elif sha256_file(target) != item["sha256"]:
                fail("CHANGED_FILE_DIGEST_MISMATCH", f"changed-file digest mismatch: {changed}")

        for command in result["commands"]:
            log = self.graph.repo_root / command["log"]
            if not log.is_file():
                fail("COMMAND_LOG_MISSING", f"command log is missing: {command['log']}")
            elif sha256_file(log) != command["log_sha256"]:
                fail("COMMAND_LOG_DIGEST_MISMATCH", f"command-log digest mismatch: {command['log']}")
            if result["outcome"] == "PASSED" and command["exit_code"] != 0:
                fail("NONZERO_COMMAND_IN_PASSED", f"nonzero command: {command['argv']}")

        for evidence in result["evidence"]:
            if not (self.graph.repo_root / evidence).exists():
                fail("EVIDENCE_MISSING", f"evidence path is missing: {evidence}")

        for predecessor in node["depends_on"]:
            state = self.currency(predecessor)
            if not state["current"]:
                fail(
                    "PREDECESSOR_NOT_CURRENT",
                    f"{predecessor} is not current: {state['reasons']}",
                )

        return {
            "node_id": node_id,
            "valid": not problems,
            "outcome": result["outcome"],
            "result": relative_result,
            "result_sha256": sha256_file(self.graph.result_path(node_id)),
            "problems": problems,
        }

    # ------------------------------------------------------------ verification

    def run_verification(self, node_id: str, attempt: Attempt) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for index, argv in enumerate(self.graph.node(node_id)["verification"]):
            resolved = [sys.executable if item == "python3" else item for item in argv]
            exit_code, output = self.runner(resolved, self.graph.repo_root)
            log = attempt.write_log(f"verify_{index:02d}.log", output)
            records.append(
                {
                    "argv": list(argv),
                    "exit_code": exit_code,
                    "log": log.relative_to(self.state_dir).as_posix(),
                    "log_sha256": sha256_file(log),
                }
            )
            attempt.event("verification_command", argv=list(argv), exit_code=exit_code)
        return records

    # ----------------------------------------------------------------- admit

    def admit(
        self,
        node_id: str,
        attempt_id: str,
        *,
        recovery: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        attempt = self.attempt(node_id, attempt_id)
        state = attempt.state()
        if state != "open":
            raise ControllerError(
                f"{node_id}: attempt {attempt_id} is {state}; create a new attempt "
                "with resume before admitting",
                code="ATTEMPT_NOT_OPEN",
            )
        if attempt.journal_path.is_file():
            raise ControllerError(
                f"{node_id}: attempt {attempt_id} has an open merge journal; run "
                "recover before any further admission",
                code="MERGE_JOURNAL_OPEN",
            )
        record = attempt.record()
        if record["node_id"] != node_id:
            raise ControllerError(
                f"attempt {attempt_id} belongs to {record['node_id']}", code="ATTEMPT_NODE_MISMATCH"
            )
        self.require_entry_gate(node_id)
        self.invalidate_digest_cache()

        try:
            validation = self.validate_node_result(node_id)
        except ControllerError as error:
            self.fail_attempt(attempt, error.code, str(error))
            raise
        if not validation["valid"]:
            codes = sorted({problem["code"] for problem in validation["problems"]})
            message = "; ".join(
                f"{problem['code']}: {problem['message']}" for problem in validation["problems"]
            )
            self.fail_attempt(attempt, codes[0], message, problems=validation["problems"])
            raise ControllerError(f"{node_id}: {message}", code=codes[0])

        commands = self.run_verification(node_id, attempt)
        failed = [command for command in commands if command["exit_code"] != 0]
        if failed:
            message = "; ".join(f"{command['argv']} exited {command['exit_code']}" for command in failed)
            self.fail_attempt(attempt, "VERIFICATION_FAILED", message, commands=commands)
            raise ControllerError(f"{node_id}: verification failed: {message}", code="VERIFICATION_FAILED")

        if recovery is not None:
            if recovery.get("reason_code") not in RECOVERY_REASON_CODES:
                raise ControllerError(
                    f"unknown recovery reason code: {recovery.get('reason_code')!r}; "
                    f"legal codes are {sorted(RECOVERY_REASON_CODES)}",
                    code="UNKNOWN_RECOVERY_REASON",
                )
            expected = recovery.get("expect_result_sha256")
            if expected != validation["result_sha256"]:
                raise ControllerError(
                    f"{node_id}: re-admission must bind the exact artifact; declared "
                    f"{expected} but the result digest is {validation['result_sha256']}",
                    code="RECOVERY_ARTIFACT_MISMATCH",
                )

        result = load_node_result(self.graph, node_id)
        receipt = self._build_receipt(
            node_id=node_id,
            attempt=attempt,
            record=record,
            result=result,
            validation=validation,
            verification=commands,
            recovery=recovery,
        )
        return self._merge(attempt, receipt)

    def _build_receipt(
        self,
        *,
        node_id: str,
        attempt: Attempt,
        record: dict[str, Any],
        result: dict[str, Any],
        validation: dict[str, Any],
        verification: list[dict[str, Any]],
        recovery: dict[str, Any] | None,
    ) -> dict[str, Any]:
        baseline = record["baseline"]
        receipt = {
            "schema_version": 1,
            "receipt_id": f"{node_id}-{uuid.uuid4().hex}",
            "run_id": self.run_id,
            "node_id": node_id,
            "attempt_id": attempt.attempt_id,
            "parent_attempt_id": record["parent_attempt_id"],
            "status": result["outcome"],
            "admitted_at": utc_now(),
            "admission": "recovery_readmission" if recovery else "normal",
            "graph_sha256": self.graph.digest,
            "node_definition_sha256": self.graph.node_definition_digest(node_id),
            "prompt_sha256": self.graph.prompt_digest(node_id),
            "approved_spec_sha256": self.graph.source_spec_digest(),
            "baseline_sha256": canonical_digest(baseline),
            "baseline": baseline,
            "predecessor_receipts": {
                predecessor: self.receipt_digest(predecessor)
                for predecessor in sorted(self.graph.node(node_id)["depends_on"])
            },
            "predecessor_results": dict(result["predecessor_receipts"]),
            "lineage_fingerprint": self.lineage_fingerprint(node_id),
            "result_path": validation["result"],
            "result_sha256": validation["result_sha256"],
            "changed_files": result["changed_files"],
            "commands": result["commands"],
            "verification": verification,
            "evidence": result["evidence"],
            "final_outputs": {
                relative: self.current_path_digest(relative)
                for relative in self.graph.node(node_id)["writes"]
            },
        }
        if recovery is not None:
            receipt["recovery"] = {
                "reason_code": recovery["reason_code"],
                "reason": recovery["reason"],
                "expect_result_sha256": recovery["expect_result_sha256"],
                "superseded_receipt_sha256": self.receipt_digest(node_id),
                "verification_rerun": True,
            }
        validate_against(RECEIPT_SCHEMA_PATH, receipt, f"{node_id} scheduler receipt")
        return receipt

    def _merge(self, attempt: Attempt, receipt: dict[str, Any]) -> dict[str, Any]:
        """Invariant 8: journal, then one atomic rename. Never partial bytes."""

        node_id = receipt["node_id"]
        target = self.receipt_path(node_id)
        target.parent.mkdir(parents=True, exist_ok=True)
        serialized = serialize_record(receipt)
        previous = self.receipt(node_id)
        journal = {
            "at": utc_now(),
            "node_id": node_id,
            "attempt_id": attempt.attempt_id,
            "receipt": receipt,
            "receipt_sha256": sha256_bytes(serialized.encode("utf-8")),
            "previous_receipt": previous,
            "previous_receipt_sha256": self.receipt_digest(node_id),
        }
        write_once_json(attempt.journal_path, journal)
        attempt.event("merge_journaled", receipt_sha256=journal["receipt_sha256"])
        self.audit_event(
            "merge_journaled",
            node_id=node_id,
            attempt_id=attempt.attempt_id,
            receipt_sha256=journal["receipt_sha256"],
        )
        if previous is not None:
            history = self.receipts_dir / "history" / node_id / f"{journal['previous_receipt_sha256']}.json"
            if not history.exists():
                write_once_text(history, serialize_record(previous))
        atomic_write_text(target, serialized)
        return self._finish_merge(attempt, node_id, journal)

    def _finish_merge(self, attempt: Attempt, node_id: str, journal: dict[str, Any]) -> dict[str, Any]:
        outcome = {
            "at": utc_now(),
            "node_id": node_id,
            "attempt_id": attempt.attempt_id,
            "receipt": self.receipt_path(node_id).relative_to(self.state_dir).as_posix(),
            "receipt_sha256": journal["receipt_sha256"],
            "status": journal["receipt"]["status"],
            "admission": journal["receipt"]["admission"],
        }
        write_once_json(attempt.root / "merged.json", outcome)
        attempt.event("merge_completed", receipt_sha256=journal["receipt_sha256"])
        self.invalidate_digest_cache()
        invalidated = self.invalidated_descendants(node_id)
        self.audit_event(
            "node_admitted",
            node_id=node_id,
            attempt_id=attempt.attempt_id,
            status=outcome["status"],
            admission=outcome["admission"],
            receipt_sha256=outcome["receipt_sha256"],
            invalidated_descendants=invalidated,
        )
        if invalidated:
            self.audit_event(
                "descendants_invalidated", node_id=node_id, invalidated_descendants=invalidated
            )
        return {**outcome, "invalidated_descendants": invalidated}

    def recover(self, node_id: str, attempt_id: str) -> dict[str, Any]:
        """Complete or roll back an interrupted merge. Never accept partial bytes."""

        attempt = self.attempt(node_id, attempt_id)
        if (attempt.root / "merged.json").is_file():
            return {"node_id": node_id, "attempt_id": attempt_id, "action": "already_merged"}
        if not attempt.journal_path.is_file():
            if attempt.state() == "open":
                write_once_json(
                    attempt.root / "interrupted.json",
                    {"at": utc_now(), "code": "NO_MERGE_JOURNAL"},
                )
                attempt.event("attempt_interrupted", code="NO_MERGE_JOURNAL")
            self.audit_event(
                "attempt_interrupted", node_id=node_id, attempt_id=attempt_id, code="NO_MERGE_JOURNAL"
            )
            return {"node_id": node_id, "attempt_id": attempt_id, "action": "no_journal"}

        journal = load_json_strict(attempt.journal_path, what=f"{node_id} merge journal")
        current = self.receipt_digest(node_id)
        if current == journal["receipt_sha256"]:
            outcome = self._finish_merge(attempt, node_id, journal)
            self.audit_event(
                "merge_recovered", node_id=node_id, attempt_id=attempt_id, action="completed"
            )
            return {**outcome, "action": "completed"}

        if journal["previous_receipt"] is None:
            if self.receipt_path(node_id).exists():
                self.receipt_path(node_id).unlink()
        else:
            atomic_write_text(self.receipt_path(node_id), serialize_record(journal["previous_receipt"]))
        write_once_json(
            attempt.root / "interrupted.json",
            {
                "at": utc_now(),
                "code": "MERGE_INTERRUPTED",
                "rolled_back_to": journal["previous_receipt_sha256"],
                "rejected_receipt_sha256": journal["receipt_sha256"],
            },
        )
        attempt.event("merge_rolled_back", rolled_back_to=journal["previous_receipt_sha256"])
        self.invalidate_digest_cache()
        self.audit_event(
            "merge_recovered",
            node_id=node_id,
            attempt_id=attempt_id,
            action="rolled_back",
            rolled_back_to=journal["previous_receipt_sha256"],
        )
        return {
            "node_id": node_id,
            "attempt_id": attempt_id,
            "action": "rolled_back",
            "rolled_back_to": journal["previous_receipt_sha256"],
        }

    # ---------------------------------------------------------------- reporting

    def status(self) -> dict[str, Any]:
        self.invalidate_digest_cache()
        order = self.graph.order()
        nodes = []
        for node_id in order:
            receipt = self.receipt(node_id)
            state = self.currency(node_id)
            nodes.append(
                {
                    "node_id": node_id,
                    "status": receipt.get("status") if receipt else None,
                    "admission": receipt.get("admission") if receipt else None,
                    "receipt_sha256": self.receipt_digest(node_id),
                    "current": state["current"],
                    "reasons": state["reasons"],
                    "attempts": [
                        {"attempt_id": item.attempt_id, "state": item.state()}
                        for item in self.attempts(node_id)
                    ],
                }
            )
        blocked = [item["node_id"] for item in nodes if not item["current"]]
        return {
            "graph_id": self.graph.data["graph_id"],
            "graph_sha256": self.graph.digest,
            "approved_spec_sha256": self.graph.source_spec_digest(),
            "entry_gate": self.entry_gate(),
            "order": order,
            "nodes": nodes,
            "next_runnable": blocked[0] if blocked else None,
        }


def _default_runner(argv: Sequence[str], cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(
        list(argv),
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return completed.returncode, completed.stdout
