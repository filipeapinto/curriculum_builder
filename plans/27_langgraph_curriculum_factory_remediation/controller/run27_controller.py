#!/usr/bin/env python3
"""Run 27 implementation-graph controller.

Mutating commands:  begin, admit, readmit, resume, recover
Read-only commands: status, plan, validate, audit, verify-live-proof,
                    verify-final-audit

Read-only commands never create the state directory, never write a receipt, and
never touch an attempt.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from core import (  # noqa: E402
    ADMISSIBLE_OUTCOMES,
    DEFAULT_GRAPH_PATH,
    DEFAULT_REPO_ROOT,
    DEFAULT_STATE_DIR,
    ControllerError,
    Graph,
    load_node_result,
    sha256_file,
)
from scheduler import RECOVERY_REASON_CODES, Scheduler  # noqa: E402


DEFAULT_LIVE_PROOF_CLI = "runtime/run_curriculum.py"
DEFAULT_FORBIDDEN_LIVE_MARKERS = (
    "SIMULATED",
    "FAKE_TRANSPORT",
    "MOCK_TRANSPORT",
    "STUB_TRANSPORT",
    "SYNTHETIC_CURRICULUM",
)

READ_ONLY_COMMANDS = frozenset(
    {"status", "plan", "validate", "audit", "verify-live-proof", "verify-final-audit"}
)


def build_scheduler(arguments: argparse.Namespace) -> Scheduler:
    graph = Graph.load(arguments.graph, arguments.repo_root)
    return Scheduler(graph, arguments.state_dir, run_id=arguments.run_id)


# --------------------------------------------------------------- live proof


def verify_live_proof(scheduler: Scheduler, node_id: str) -> dict[str, Any]:
    graph = scheduler.graph
    node = graph.node(node_id)
    problems: list[dict[str, str]] = []

    def fail(code: str, message: str) -> None:
        problems.append({"code": code, "message": message})

    if node_id not in graph.live_proof_nodes():
        raise ControllerError(
            f"{node_id} is not a live-proof node; the graph does not allow it to "
            "report NOT_AVAILABLE",
            code="NOT_A_LIVE_PROOF_NODE",
        )

    result = load_node_result(graph, node_id)
    outcome = result["outcome"]
    cli = graph.rules.get("live_proof_cli", DEFAULT_LIVE_PROOF_CLI)
    markers = tuple(graph.rules.get("live_proof_forbidden_markers", DEFAULT_FORBIDDEN_LIVE_MARKERS))

    log_paths = [command["log"] for command in result["commands"]]
    scanned = sorted({*log_paths, *result["evidence"]})

    if outcome == "PASSED":
        for command in result["commands"]:
            if command["exit_code"] != 0:
                fail("NONZERO_LIVE_COMMAND", f"{command['argv']} exited {command['exit_code']}")
        if not any(cli in " ".join(command["argv"]) for command in result["commands"]):
            fail(
                "NO_PRODUCTION_CLI_INVOCATION",
                f"a passing live proof must invoke the production CLI {cli}",
            )
        for relative in node["writes"]:
            target = graph.repo_root / relative
            if not target.exists():
                fail("LIVE_OUTPUT_MISSING", f"declared live output is missing: {relative}")
            elif target.is_dir() and not any(
                item.is_file() for item in target.rglob("*")
            ):
                fail("LIVE_OUTPUT_EMPTY", f"declared live output directory is empty: {relative}")
        for item in result["changed_files"]:
            target = graph.repo_root / item["path"]
            if item["change"] != "deleted":
                if not target.is_file():
                    fail("CHANGED_FILE_MISSING", f"missing changed file: {item['path']}")
                elif sha256_file(target) != item["sha256"]:
                    fail("CHANGED_FILE_DIGEST_MISMATCH", f"digest mismatch: {item['path']}")
        for relative in scanned:
            target = graph.repo_root / relative
            if not target.is_file():
                continue
            text = target.read_text(encoding="utf-8", errors="replace")
            for marker in markers:
                if marker in text:
                    fail(
                        "SIMULATED_LIVE_EVIDENCE",
                        f"{relative} contains the non-live marker {marker}",
                    )
    elif outcome == "NOT_AVAILABLE":
        if not any(finding["disposition"] == "open" for finding in result["findings"]):
            fail(
                "UNEXPLAINED_NOT_AVAILABLE",
                "NOT_AVAILABLE must carry at least one open finding naming why live "
                "proof could not be produced",
            )
    else:
        fail("OUTCOME_NOT_LIVE_PROOF", f"outcome {outcome!r} does not report live proof")

    for relative in result["evidence"]:
        if not (graph.repo_root / relative).exists():
            fail("EVIDENCE_MISSING", f"evidence path is missing: {relative}")

    for ancestor in graph.ancestors(node_id):
        if scheduler.receipt(ancestor) is None:
            continue
        state = scheduler.currency(ancestor)
        if not state["current"]:
            fail("ANCESTOR_NOT_CURRENT", f"{ancestor}: {state['reasons']}")

    return {
        "command": "verify-live-proof",
        "node_id": node_id,
        "outcome": outcome,
        "valid": not problems,
        "problems": problems,
    }


# -------------------------------------------------------------- final audit


def verify_final_audit(scheduler: Scheduler, node_id: str) -> dict[str, Any]:
    graph = scheduler.graph
    problems: list[dict[str, str]] = []

    def fail(code: str, message: str) -> None:
        problems.append({"code": code, "message": message})

    expected = graph.final_audit_node()
    if node_id != expected:
        raise ControllerError(
            f"{node_id} is not the final audit node; the graph's single sink is {expected}",
            code="NOT_THE_FINAL_AUDIT_NODE",
        )

    result = load_node_result(graph, node_id)
    terminal = result.get("terminal_recommendation")
    legal = set(graph.data["terminals"])
    if terminal is None:
        fail("NO_TERMINAL_RECOMMENDATION", "the final audit must recommend exactly one terminal")
    elif terminal not in legal:
        fail("ILLEGAL_TERMINAL", f"{terminal!r} is not one of {sorted(legal)}")

    outcomes: dict[str, str] = {}
    for other in graph.order():
        if other == node_id:
            continue
        try:
            other_result = load_node_result(graph, other)
        except ControllerError as error:
            fail("UPSTREAM_RESULT_UNUSABLE", f"{other}: {error}")
            continue
        outcomes[other] = other_result["outcome"]
        if other_result["outcome"] not in ADMISSIBLE_OUTCOMES:
            fail("UPSTREAM_NOT_ADMISSIBLE", f"{other} reported {other_result['outcome']}")
        if other_result.get("terminal_recommendation") is not None:
            fail("NON_AUDIT_TERMINAL", f"{other} may not recommend a terminal")

    live_nodes = [item for item in graph.live_proof_nodes() if item != node_id]
    if terminal == "ACTIVATED":
        for live in live_nodes:
            if outcomes.get(live) != "PASSED":
                fail(
                    "ACTIVATION_WITHOUT_LIVE_PROOF",
                    f"{live} reported {outcomes.get(live)!r}; ACTIVATED requires live proof",
                )
    elif terminal == "REMEDIATION_VERIFIED_NOT_ACTIVATED":
        if not any(outcomes.get(live) == "NOT_AVAILABLE" for live in live_nodes):
            fail(
                "NOT_ACTIVATED_WITHOUT_UNAVAILABLE_PROOF",
                "this terminal requires at least one live-proof node reporting NOT_AVAILABLE",
            )
    elif terminal == "BLOCKED" and result["outcome"] != "BLOCKED":
        fail("BLOCKED_TERMINAL_MISMATCH", "a BLOCKED terminal requires a BLOCKED outcome")

    for other in graph.order():
        if scheduler.receipt(other) is None:
            continue
        state = scheduler.currency(other)
        if not state["current"]:
            fail(
                "INVALIDATED_RECEIPT_FEEDS_FINAL_AUDIT",
                f"{other} is not current: {state['reasons']}",
            )

    for relative in result["evidence"]:
        if not (graph.repo_root / relative).exists():
            fail("EVIDENCE_MISSING", f"evidence path is missing: {relative}")

    return {
        "command": "verify-final-audit",
        "node_id": node_id,
        "outcome": result["outcome"],
        "terminal_recommendation": terminal,
        "upstream_outcomes": outcomes,
        "valid": not problems,
        "problems": problems,
    }


# ---------------------------------------------------------------------- CLI


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    result.add_argument("--graph", type=Path, default=DEFAULT_GRAPH_PATH)
    result.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    result.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    result.add_argument("--run-id", default="run27")
    subcommands = result.add_subparsers(dest="command", required=True)

    subcommands.add_parser("status")
    subcommands.add_parser("plan")
    subcommands.add_parser("audit")

    validate = subcommands.add_parser("validate")
    validate.add_argument("--node", required=True)

    begin = subcommands.add_parser("begin")
    begin.add_argument("--node", required=True)

    admit = subcommands.add_parser("admit")
    admit.add_argument("--node", required=True)
    admit.add_argument("--attempt", required=True)

    readmit = subcommands.add_parser("readmit")
    readmit.add_argument("--node", required=True)
    readmit.add_argument("--attempt", required=True)
    readmit.add_argument("--reason-code", required=True, choices=sorted(RECOVERY_REASON_CODES))
    readmit.add_argument("--reason", required=True)
    readmit.add_argument("--expect-result-sha256", required=True)

    resume = subcommands.add_parser("resume")
    resume.add_argument("--node", required=True)
    resume.add_argument("--attempt", required=True)

    recover = subcommands.add_parser("recover")
    recover.add_argument("--node", required=True)
    recover.add_argument("--attempt", required=True)

    live = subcommands.add_parser("verify-live-proof")
    live.add_argument("--node", required=True)

    audit = subcommands.add_parser("verify-final-audit")
    audit.add_argument("--node", required=True)
    return result


def dispatch(arguments: argparse.Namespace) -> dict[str, Any]:
    scheduler = build_scheduler(arguments)
    command = arguments.command
    if command == "status":
        return scheduler.status()
    if command == "plan":
        state = scheduler.status()
        return {
            "command": "plan",
            "order": state["order"],
            "entry_gate": state["entry_gate"],
            "next_runnable": state["next_runnable"],
            "not_current": [
                item["node_id"] for item in state["nodes"] if not item["current"]
            ],
        }
    if command == "audit":
        return {"command": "audit", "events": scheduler.audit()}
    if command == "validate":
        return scheduler.validate_node_result(arguments.node)
    if command == "begin":
        return scheduler.begin(arguments.node)
    if command == "admit":
        return scheduler.admit(arguments.node, arguments.attempt)
    if command == "readmit":
        return scheduler.admit(
            arguments.node,
            arguments.attempt,
            recovery={
                "reason_code": arguments.reason_code,
                "reason": arguments.reason,
                "expect_result_sha256": arguments.expect_result_sha256,
            },
        )
    if command == "resume":
        return scheduler.resume(arguments.node, arguments.attempt)
    if command == "recover":
        return scheduler.recover(arguments.node, arguments.attempt)
    if command == "verify-live-proof":
        return verify_live_proof(scheduler, arguments.node)
    if command == "verify-final-audit":
        return verify_final_audit(scheduler, arguments.node)
    raise ControllerError(f"unknown command: {command}", code="UNKNOWN_COMMAND")


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        payload = dispatch(arguments)
    except ControllerError as error:
        print(json.dumps({"ok": False, "code": error.code, "error": str(error)}, sort_keys=True))
        return 1
    ok = payload.get("valid", True)
    print(json.dumps({"ok": bool(ok), **payload}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
