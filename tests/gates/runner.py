"""The gate runner — dependency order, ties by ID, cumulative execution.

Harness rule 2. ``run_gates.sh N`` builds the subgraph of gates with
``activation_phase <= N``, topologically sorts it breaking ties by ID, and runs it
in that order.

Four outcomes, and they are never interchanged:

``PASS``     the gate ran and its criteria held.
``FAIL``     the gate ran and its criteria did not hold.
``SKIPPED``  ``activation_phase`` is beyond the requested phase. Recorded, never silent.
``BLOCKED``  a dependency failed or was itself blocked. Not run, not skipped, never
             counted as a pass, and it propagates transitively.

``BLOCKED`` is a **gate-level** outcome. The run-level verdict for "this phase
cannot be approved" is ``HALTED``, and the two never appear in each other's place.

A dependency cycle is a hard error: the run aborts before any gate executes.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
from common import Evidence, GateFailure, GateOutcome, RESULTS_DIR  # noqa: E402

ROOT_GATE = "FR-P0-HARNESS"


class CycleError(Exception):
    """A dependency cycle. Reported before any gate executes."""


def load_registry():
    path = Path(os.environ.get("FR_GATE_REGISTRY", str(common.GATES_DIR / "registry.py")))
    spec = importlib.util.spec_from_file_location("fr_gate_registry", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.GATES


def topological_order(gates: list[dict]) -> list[str]:
    """Kahn's algorithm with ties broken by ID. Raises :class:`CycleError`."""
    ids = {g["id"] for g in gates}
    deps = {g["id"]: sorted(set(g["depends_on"]) & ids) for g in gates}
    indegree = {gid: len(deps[gid]) for gid in ids}
    ready = sorted(gid for gid, n in indegree.items() if n == 0)
    order: list[str] = []
    while ready:
        gid = ready.pop(0)
        order.append(gid)
        for other in sorted(ids):
            if gid in deps[other]:
                indegree[other] -= 1
                if indegree[other] == 0:
                    ready.append(other)
                    ready.sort()
    if len(order) != len(ids):
        stuck = sorted(ids - set(order))
        raise CycleError(f"dependency cycle among: {', '.join(stuck)}")
    return order


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _results_path(phase: int) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    candidate = RESULTS_DIR / f"gate_results.p{phase}.{stamp}.json"
    counter = 0
    while candidate.exists():  # never overwrite — self-test (e)
        counter += 1
        candidate = RESULTS_DIR / f"gate_results.p{phase}.{stamp}-{counter}.json"
    return candidate


def run(phase: int) -> int:
    gates = load_registry()
    by_id = {g["id"]: g for g in gates}
    in_scope = [g for g in gates if g["activation_phase"] <= phase]

    try:
        order = topological_order(in_scope)
    except CycleError as exc:
        print(f"HALTED: {exc}")
        print("no gate executed")
        return 3

    if in_scope and order and order[0] != ROOT_GATE and ROOT_GATE in by_id:
        # The root must be first; a registry that says otherwise is a graph defect.
        print(f"HALTED: {ROOT_GATE} is not the graph root (first was {order[0]})")
        return 3

    records: dict[str, dict] = {}
    status: dict[str, str] = {}
    common.RUN_STATE["phase"] = phase
    common.RUN_STATE["mechanisms"] = {}

    for gid in order:
        gate = by_id[gid]
        blocking = [d for d in gate["depends_on"] if status.get(d) in ("FAIL", "BLOCKED")]
        if blocking:
            dep = sorted(blocking)[0]
            reason = f"BLOCKED (dependency {dep} {'failed' if status[dep] == 'FAIL' else 'blocked'})"
            status[gid] = "BLOCKED"
            records[gid] = _record(gate, "BLOCKED", reason, [], "", 1)
            print(f"{gid} {reason}")
            continue

        ev = Evidence(gate_id=gid)
        try:
            module_name, func_name = gate["impl"].split(":")
            module = common.load_gate_module(module_name)
            func = getattr(module, func_name, None)
            if func is None:
                raise GateFailure(f"{gate['impl']} is declared but not implemented")
            outcome: GateOutcome = func(ev)
        except Exception as exc:  # noqa: BLE001 - a crashing gate is a failing gate
            outcome = GateOutcome(ok=False, detail=f"{type(exc).__name__}: {exc}")

        verdict = "PASS" if outcome.ok else "FAIL"
        status[gid] = verdict
        common.RUN_STATE["mechanisms"][gid] = ev.mechanisms()
        records[gid] = _record(
            gate, verdict, outcome.detail, outcome.fixtures, outcome.stdout or outcome.detail,
            0 if outcome.ok else 1, ev,
        )
        print(f"{gid} {verdict} [{ev.claim() or '-'}] {outcome.detail}")

    for gate in gates:
        if gate["activation_phase"] > phase:
            gid = gate["id"]
            status[gid] = "SKIPPED"
            note = f"SKIPPED (activates at phase {gate['activation_phase']})"
            records[gid] = _record(gate, "SKIPPED", note, [], "", 0)
            print(f"{gid} {note}")

    _class_drift_sweep(records, status, by_id)

    path = _results_path(phase)
    payload = {
        "phase": phase,
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "root_gate": ROOT_GATE,
        "root_gate_ran_first": bool(order) and order[0] == ROOT_GATE,
        "order": order,
        "registered": len(gates),
        "counts": {
            verdict: sum(1 for v in status.values() if v == verdict)
            for verdict in ("PASS", "FAIL", "SKIPPED", "BLOCKED")
        },
        "gates": [records[g["id"]] for g in gates],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"results: {common.rel(path) if path.is_relative_to(common.REPO_ROOT) else path}")

    counts = payload["counts"]
    print(
        f"phase {phase}: {counts['PASS']} PASS, {counts['FAIL']} FAIL, "
        f"{counts['BLOCKED']} BLOCKED, {counts['SKIPPED']} SKIPPED "
        f"of {len(gates)} registered"
    )
    return 0 if counts["FAIL"] == 0 and counts["BLOCKED"] == 0 else 1


def _record(gate, verdict, detail, fixtures, stdout, exit_code, ev=None) -> dict:
    return {
        "id": gate["id"],
        "activation_phase": gate["activation_phase"],
        "declared_claim_class": gate["claim_class"],
        "mechanisms_used": ev.mechanisms() if ev else [],
        "reported_claim_class": ev.claim() if ev else "",
        "depends_on": list(gate["depends_on"]),
        "command": gate["command"],
        "exit_code": exit_code,
        "stdout_digest": _digest(stdout),
        "status": verdict,
        "detail": detail,
        "fixtures": fixtures,
        "notes": ev.notes if ev else [],
    }


def _class_drift_sweep(records, status, by_id) -> None:
    """``FR-P0-REGISTRY`` (d), applied to every gate that ran in this run.

    The gate itself checks (a)-(c) and (d) over the gates completed before it; the
    sweep closes (d) over the gates that ran after it. Any drift found here fails
    ``FR-P0-REGISTRY``, which is where the plan puts the criterion — it is never
    silently dropped because of where the gate sits in the graph.
    """
    registry_id = "FR-P0-REGISTRY"
    if registry_id not in records or status.get(registry_id) == "SKIPPED":
        return
    drift = []
    for gid, record in records.items():
        if record["status"] not in ("PASS", "FAIL"):
            continue
        declared = set(by_id[gid]["claim_class"].split("+"))
        reported = set(record["mechanisms_used"])
        if declared != reported:
            drift.append(f"{gid}: declared {'+'.join(sorted(declared))}, reported {'+'.join(sorted(reported)) or '-'}")
    record = records[registry_id]
    record["class_drift"] = drift
    if drift:
        record["status"] = "FAIL"
        record["exit_code"] = 1
        record["detail"] = "claim-class-drift: " + "; ".join(drift)
        status[registry_id] = "FAIL"
        print(f"{registry_id} FAIL claim-class-drift: {'; '.join(drift)}")


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not argv[1].isdigit():
        print("usage: run_gates.sh <phase>")
        return 2
    return run(int(argv[1]))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
