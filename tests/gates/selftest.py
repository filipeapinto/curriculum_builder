"""FR-P0-HARNESS — the harness is proven before it is trusted (harness rule 8).

This gate is the root of the dependency graph. Its seven self-tests are the
behaviours no per-gate fixture reaches: phase selection, exit propagation, result
integrity, wrong-reason detection, no-overwrite, scan isolation, and dependency
order. If it fails, every other result in the run is unreliable — report ``HALTED``
and report no other gate's outcome.

Every input it uses is synthetic. The synthetic registries and gate modules are
written into ``tests/selftest/`` and a scratch directory; none of them touches the
repository tree, and none of them is ever seen by a production scan.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
from common import Evidence, SELFTEST_DIR, TESTS_DIR, gate_result, rel  # noqa: E402

RUN_GATES = TESTS_DIR / "run_gates.sh"

SYNTH_GATES_SOURCE = '''\
"""Synthetic gates for FR-P0-HARNESS. Never part of the production suite."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
import common
from common import Evidence, Fixture, gate_result


def passing(ev: Evidence):
    ev.run([sys.executable, "-c", "print('ok')"])
    Path(ORDER_LOG).open("a").write("passing\\n")
    return gate_result(True, "synthetic pass")


def failing(ev: Evidence):
    ev.run([sys.executable, "-c", "print('ok')"])
    Path(ORDER_LOG).open("a").write("failing\\n")
    return gate_result(False, "synthetic failure, injected on purpose")


def dependant(ev: Evidence):
    ev.run([sys.executable, "-c", "print('ok')"])
    Path(ORDER_LOG).open("a").write("dependant\\n")
    return gate_result(True, "synthetic dependant")


def grandchild(ev: Evidence):
    ev.run([sys.executable, "-c", "print('ok')"])
    Path(ORDER_LOG).open("a").write("grandchild\\n")
    return gate_result(True, "synthetic grandchild")


def wrong_reason(ev: Evidence):
    ev.run([sys.executable, "-c", "print('ok')"])
    fixture = Fixture(
        name="synthetic.reject",
        kind="reject",
        expected_error="expected-constraint-violation",
        detector=lambda: "ParseError: the file did not even parse",
    )
    return gate_result(True, "gate body passes; its fixture fails for the wrong reason", [fixture])


ORDER_LOG = __ORDER_LOG__
'''


def _write_case(scratch: Path, name: str, gates: list[dict], order_log: Path) -> Path:
    module = scratch / "synth_gates.py"
    module.write_text(
        SYNTH_GATES_SOURCE.replace("__ORDER_LOG__", repr(str(order_log))), encoding="utf-8"
    )
    registry = scratch / f"registry_{name}.py"
    registry.write_text("GATES = " + json.dumps(gates, indent=2) + "\n", encoding="utf-8")
    return registry


def _gate(gid: str, phase: int, deps: list[str], impl: str) -> dict:
    return {
        "id": gid,
        "activation_phase": phase,
        "claim_class": "execution",
        "depends_on": deps,
        "command": f"synthetic {gid}",
        "impl": f"synth_gates:{impl}",
    }


def _run(registry: Path, phase: int, results: Path, gates_dir: Path, use_shell: bool = False):
    env = dict(os.environ)
    env.update(
        {
            "FR_GATE_REGISTRY": str(registry),
            "FR_RESULTS_DIR": str(results),
            "FR_GATES_DIR": str(gates_dir),
        }
    )
    if use_shell:
        args = ["/bin/sh", str(RUN_GATES), str(phase)]
    else:
        args = [sys.executable, str(common.GATES_DIR / "runner.py"), str(phase)]
    proc = subprocess.run(args, capture_output=True, text=True, env=env, cwd=str(common.REPO_ROOT))
    payloads = []
    for path in sorted(results.glob("*.json")):
        payloads.append(json.loads(path.read_text(encoding="utf-8")))
    return proc, payloads


def gate_harness(ev: Evidence):
    """Run the seven self-tests. Each is named in the result record."""
    SELFTEST_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    scratch = Path(tempfile.mkdtemp(prefix="fr-selftest-"))
    try:
        results.append(_selftest_phase_selection(ev, scratch))
        results.append(_selftest_exit_propagation(ev, scratch))
        results.append(_selftest_result_integrity(ev, scratch))
        results.append(_selftest_wrong_reason(ev, scratch))
        results.append(_selftest_no_overwrite(ev, scratch))
        results.append(_selftest_scan_isolation(ev, scratch))
        results.append(_selftest_dependency_order(ev, scratch))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    failed = [r for r in results if not r["ok"]]
    names = ", ".join(f"({r['id']}) {r['name']}: {'PASS' if r['ok'] else 'FAIL'}" for r in results)
    detail = f"FR-P0-HARNESS {'PASS' if not failed else 'FAIL'} (7 self-tests) — {names}"
    if failed:
        detail += " | " + "; ".join(f"{r['id']}: {r['why']}" for r in failed)
    return gate_result(not failed, detail, stdout=detail)


def _case(scratch: Path, name: str) -> tuple[Path, Path]:
    case = scratch / name
    (case / "results").mkdir(parents=True, exist_ok=True)
    return case, case / "results"


def _selftest_phase_selection(ev: Evidence, scratch: Path) -> dict:
    case, results = _case(scratch, "phase_selection")
    gates = [_gate("SYN-A", 0, [], "passing"), _gate("SYN-LATER", 4, ["SYN-A"], "passing")]
    registry = _write_case(case, "phase", gates, case / "order.log")
    proc, payloads = _run(registry, 0, results, case)
    ev.resolve("SYN-LATER", "the synthetic registry", "its entry in the result record")
    record = {r["id"]: r for r in payloads[0]["gates"]} if payloads else {}
    ok = (
        bool(payloads)
        and record.get("SYN-LATER", {}).get("status") == "SKIPPED"
        and "activates at phase 4" in record.get("SYN-LATER", {}).get("detail", "")
        and record.get("SYN-A", {}).get("status") == "PASS"
    )
    return {
        "id": "a",
        "name": "phase selection",
        "ok": ok,
        "why": "a gate registered at activation_phase 4 was not SKIPPED at N=0"
        + f" (stdout: {proc.stdout[-300:]})",
    }


def _selftest_exit_propagation(ev: Evidence, scratch: Path) -> dict:
    case, results = _case(scratch, "exit_propagation")
    gates = [_gate("SYN-A", 0, [], "failing")]
    registry = _write_case(case, "exit", gates, case / "order.log")
    proc, _ = _run(registry, 0, results, case, use_shell=True)
    return {
        "id": "b",
        "name": "exit propagation",
        "ok": proc.returncode != 0,
        "why": "an injected failing gate did not make run_gates.sh exit non-zero",
    }


def _selftest_result_integrity(ev: Evidence, scratch: Path) -> dict:
    case, results = _case(scratch, "result_integrity")
    gates = [
        _gate("SYN-A", 0, [], "passing"),
        _gate("SYN-B", 0, ["SYN-A"], "passing"),
        _gate("SYN-LATER", 3, ["SYN-A"], "passing"),
    ]
    registry = _write_case(case, "integrity", gates, case / "order.log")
    proc, payloads = _run(registry, 0, results, case)
    ev.resolve("every synthetic gate id", "the synthetic registry", "the result record's entries")
    recorded = [g["id"] for g in payloads[0]["gates"]] if payloads else []
    ok = sorted(recorded) == sorted(g["id"] for g in gates) and len(recorded) == len(set(recorded))
    return {
        "id": "c",
        "name": "result integrity",
        "ok": ok,
        "why": f"the JSON does not hold exactly one entry per registered gate: {recorded}",
    }


def _selftest_wrong_reason(ev: Evidence, scratch: Path) -> dict:
    case, results = _case(scratch, "wrong_reason")
    gates = [_gate("SYN-A", 0, [], "wrong_reason")]
    registry = _write_case(case, "wrongreason", gates, case / "order.log")
    proc, payloads = _run(registry, 0, results, case)
    record = payloads[0]["gates"][0] if payloads else {}
    fixture = (record.get("fixtures") or [{}])[0]
    ok = record.get("status") == "FAIL" and fixture.get("outcome") == "FAIL"
    return {
        "id": "d",
        "name": "wrong-reason detection",
        "ok": ok,
        "why": "a fixture failing with an error other than its expected_error was not recorded FAIL",
    }


def _selftest_no_overwrite(ev: Evidence, scratch: Path) -> dict:
    case, results = _case(scratch, "no_overwrite")
    gates = [_gate("SYN-A", 0, [], "passing")]
    registry = _write_case(case, "overwrite", gates, case / "order.log")
    _run(registry, 0, results, case)
    _run(registry, 0, results, case)
    written = sorted(results.glob("*.json"))
    return {
        "id": "e",
        "name": "no-overwrite",
        "ok": len(written) == 2,
        "why": f"two runs produced {len(written)} result files, not two",
    }


def _selftest_scan_isolation(ev: Evidence, scratch: Path) -> dict:
    """A production detector pointed at the production root does not read
    ``tests/fixtures/**`` — proven against the real detector, not a synthetic one."""
    structure = ev.import_and_call("fr_p0_structure")
    scanned = common.production_files()
    leaked = [p for p in scanned if "tests" in Path(p).relative_to(common.REPO_ROOT).parts[:1]]
    fixture_hits = [
        hit for hit in structure.scan_for_stale(scanned) if "/tests/" in hit or hit.startswith("tests/")
    ]
    return {
        "id": "f",
        "name": "scan isolation",
        "ok": not leaked and not fixture_hits,
        "why": f"the production scan root set reached {[str(p) for p in leaked[:5]]} {fixture_hits[:5]}",
    }


def _selftest_dependency_order(ev: Evidence, scratch: Path) -> dict:
    problems = []

    # (1) a gate never runs before a gate it depends on, even when ID order disagrees.
    case, results = _case(scratch, "order")
    order_log = case / "order.log"
    gates = [
        _gate("SYN-ZZZ-FIRST", 0, [], "passing"),
        _gate("SYN-AAA-SECOND", 0, ["SYN-ZZZ-FIRST"], "dependant"),
    ]
    registry = _write_case(case, "order", gates, order_log)
    proc, payloads = _run(registry, 0, results, case)
    executed = payloads[0]["order"] if payloads else []
    if executed != ["SYN-ZZZ-FIRST", "SYN-AAA-SECOND"]:
        problems.append(f"ID order overrode dependency order: {executed}")

    # (2)+(3) A fails, B is BLOCKED, and C depending on B is BLOCKED too.
    case, results = _case(scratch, "blocked")
    gates = [
        _gate("SYN-A", 0, [], "failing"),
        _gate("SYN-B", 0, ["SYN-A"], "dependant"),
        _gate("SYN-C", 0, ["SYN-B"], "grandchild"),
    ]
    registry = _write_case(case, "blocked", gates, case / "order.log")
    proc, payloads = _run(registry, 0, results, case)
    record = {r["id"]: r for r in payloads[0]["gates"]} if payloads else {}
    ev.resolve("each BLOCKED outcome", "the result record", "the dependency it names")
    if record.get("SYN-B", {}).get("status") != "BLOCKED":
        problems.append(f"SYN-B is {record.get('SYN-B', {}).get('status')}, expected BLOCKED")
    if "dependency SYN-A failed" not in record.get("SYN-B", {}).get("detail", ""):
        problems.append("SYN-B's BLOCKED record does not name the dependency that failed")
    if record.get("SYN-C", {}).get("status") != "BLOCKED":
        problems.append(f"SYN-C is {record.get('SYN-C', {}).get('status')}, expected BLOCKED")
    if (case / "order.log").exists() and "dependant" in (case / "order.log").read_text():
        problems.append("a BLOCKED gate was executed")

    # (4) a synthetic cycle aborts the run before any gate executes.
    case, results = _case(scratch, "cycle")
    order_log = case / "order.log"
    gates = [
        _gate("SYN-A", 0, ["SYN-B"], "passing"),
        _gate("SYN-B", 0, ["SYN-A"], "passing"),
    ]
    registry = _write_case(case, "cycle", gates, order_log)
    proc, payloads = _run(registry, 0, results, case)
    if proc.returncode == 0 or "cycle" not in proc.stdout.lower():
        problems.append(f"a dependency cycle did not abort the run: rc={proc.returncode}")
    if order_log.exists():
        problems.append("a gate executed despite the dependency cycle")
    if payloads:
        problems.append("a result file was written despite the dependency cycle")

    return {
        "id": "g",
        "name": "dependency order",
        "ok": not problems,
        "why": "; ".join(problems),
    }


def main() -> int:
    ev = Evidence(gate_id="FR-P0-HARNESS")
    outcome = gate_harness(ev)
    print(outcome.detail)
    print(f"  mechanisms: {ev.claim()}")
    return 0 if outcome.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
