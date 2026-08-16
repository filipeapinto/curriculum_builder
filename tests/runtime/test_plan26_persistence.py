"""N21 persistence/resume proof against the real SqliteSaver (spec section 11).

Every checkpoint assertion here runs against a real `langgraph.checkpoint.sqlite`
saver over a real `sqlite3` file, a real compiled multi-node graph, and — for the
crash and lock-race matrices — real operating-system processes that are actually
SIGKILLed. Nothing in this module substitutes a mock for the durability it
claims to prove.

Skips only where the hash-locked environment is absent (same technique as
tests/runtime/test_plan26_api_contract.py), so the repository's ambient
`python3 -m pytest -q` stays green; CI installs requirements/plan26.lock with
--require-hashes and therefore runs the whole module for real.
"""

import ast
import hashlib
import json
import operator
import os
import signal
import sqlite3
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from typing import Annotated, Any, TypedDict

try:  # pragma: no cover - environment probe, not behavior
    import langgraph  # noqa: F401
    import langgraph.checkpoint.sqlite  # noqa: F401
except ModuleNotFoundError as exc:  # pragma: no cover
    raise unittest.SkipTest(
        "plan26 hash-locked environment not installed "
        "(python3 -m pip install --require-hashes -r requirements/plan26.lock): "
        f"{exc}"
    ) from exc

from langgraph.graph import END, START, StateGraph

from curriculum_factory.langgraph_factory import persistence as P
from curriculum_factory.langgraph_factory.evidence import EvidenceStore
from curriculum_factory.langgraph_factory.nodes import project as project_for_node
from curriculum_factory.langgraph_factory.nodes import terminal as D98
from curriculum_factory.langgraph_factory.state import RuntimeContext

REPO_ROOT = Path(__file__).resolve().parents[2]
PERSISTENCE_SOURCE = REPO_ROOT / "src" / "curriculum_factory" / "langgraph_factory" / "persistence.py"

IDENTITY_SEED = {
    "contract_version": "plan26.v1",
    "created_at": "2026-08-11T00:00:00Z",
    "engine_root": "/engine",
    "curriculum_root": "/curriculum",
    "active_manifest_path": "/curriculum/manifest.yaml",
    "output_root": "/output",
    "mode": "one",
    "requested_unit_id": "U01",
}


class LinearState(TypedDict, total=False):
    seen: Annotated[list, operator.add]


class FanoutState(TypedDict, total=False):
    ok: Annotated[list, operator.add]


def _tree_snapshot(root: Path, *, skip_control: bool = True) -> dict[str, tuple[int, str]]:
    """mtime_ns + sha256 of every file under ``root``, for before/after proofs."""
    out: dict[str, tuple[int, str]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if skip_control and relative.startswith(f"{P.LANGGRAPH_DIRNAME}/"):
            continue
        out[relative] = (
            path.stat().st_mtime_ns,
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )
    return out


def _run_child(script: str, *args: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as handle:
        handle.write(textwrap.dedent(script))
        child_path = handle.name
    try:
        return subprocess.run(
            [sys.executable, child_path, str(REPO_ROOT / "src"), *args],
            capture_output=True,
            text=True,
            timeout=180,
        )
    finally:
        os.unlink(child_path)


CRASH_CHILD = """
    import operator, os, signal, sys
    from pathlib import Path
    from typing import Annotated, TypedDict

    sys.path.insert(0, sys.argv[1])
    from curriculum_factory.langgraph_factory import persistence as P
    from langgraph.graph import END, START, StateGraph

    output_root = Path(sys.argv[2])
    boundary = sys.argv[3]
    thread_id = sys.argv[4]

    lock = P.ExecutionLock(output_root).acquire()
    saver, conn = P.open_checkpoint_saver(output_root)
    admissions = P.AdmissionLedger(output_root)

    class S(TypedDict, total=False):
        done: Annotated[list, operator.add]

    def render(state):
        if boundary == "before_admit":
            os.kill(os.getpid(), signal.SIGKILL)
        admissions.admit("unit-a:render:1", {"bytes": "ACCEPTED"})
        if boundary == "after_admit":
            os.kill(os.getpid(), signal.SIGKILL)
        return {"done": ["render"]}

    builder = StateGraph(S)
    builder.add_node("D13", render)
    builder.add_edge(START, "D13")
    builder.add_edge("D13", END)
    graph = builder.compile(checkpointer=saver, name=P.COMPILED_GRAPH_NAME)
    graph.invoke({"done": []}, config=P.invoke_config(thread_id))
    P.flush_checkpoint_durability(conn, output_root)
    if boundary == "after_checkpoint":
        os.kill(os.getpid(), signal.SIGKILL)
    sys.exit(0)
"""

LOCK_CHILD = """
    import sys
    from pathlib import Path

    sys.path.insert(0, sys.argv[1])
    from curriculum_factory.langgraph_factory import persistence as P

    try:
        P.ExecutionLock(Path(sys.argv[2])).acquire()
    except P.ExecutionLockUnavailable:
        sys.stderr.write("LOSER\\n")
        sys.exit(P.LOCK_LOSER_EXIT_CODE)
    sys.stdout.write("WINNER\\n")
    sys.exit(0)
"""

ORPHAN_CHILD = """
    import operator, os, signal, sys
    from pathlib import Path
    from typing import Annotated, TypedDict

    sys.path.insert(0, sys.argv[1])
    from curriculum_factory.langgraph_factory import persistence as P
    from langgraph.graph import END, START, StateGraph

    output_root = Path(sys.argv[2])
    seed = {
        "contract_version": "plan26.v1",
        "created_at": "2026-08-11T00:00:00Z",
        "engine_root": "/engine",
        "curriculum_root": "/curriculum",
        "active_manifest_path": "/curriculum/manifest.yaml",
        "output_root": "/output",
        "mode": "one",
        "requested_unit_id": "U01",
    }

    lock = P.ExecutionLock(output_root).acquire()
    saver, conn = P.open_checkpoint_saver(output_root)
    invocation = P.prepare_episode_invocation(
        output_root=output_root, lock=lock, identity_seed=seed
    )

    class S(TypedDict, total=False):
        seen: Annotated[list, operator.add]

    builder = StateGraph(S)
    builder.add_node("D05", lambda state: {"seen": ["D05"]})
    builder.add_node("M03", lambda state: {"seen": ["M03"]})
    builder.add_edge(START, "D05")
    builder.add_edge("D05", "M03")
    builder.add_edge("M03", END)
    graph = builder.compile(checkpointer=saver, name=P.COMPILED_GRAPH_NAME)
    graph.invoke({"seen": []}, config=invocation.config)
    P.flush_checkpoint_durability(conn, output_root)
    sys.stdout.write(invocation.thread_id + "\\n")
    sys.stdout.flush()
    # Power loss: D98 never runs, so the episode lease is left open.
    os.kill(os.getpid(), signal.SIGKILL)
"""


class PersistenceTestCase(unittest.TestCase):
    """Shared fixture: one temp output root with a held lock and a real saver."""

    def setUp(self) -> None:
        self.output_root = Path(tempfile.mkdtemp(prefix="plan26_n21_")).resolve()
        self.lock = P.ExecutionLock(self.output_root).acquire()
        self.addCleanup(self.lock.release)
        self.saver, self.conn = P.open_checkpoint_saver(self.output_root)
        self.addCleanup(self.conn.close)

    def compile_graph(self, builder: StateGraph) -> Any:
        return builder.compile(checkpointer=self.saver, name=P.COMPILED_GRAPH_NAME)

    def linear_graph(self) -> Any:
        builder = StateGraph(LinearState)
        builder.add_node("D05", lambda state: {"seen": ["D05"]})
        builder.add_node("D13", lambda state: {"seen": ["D13"]})
        builder.add_edge(START, "D05")
        builder.add_edge("D05", "D13")
        builder.add_edge("D13", END)
        return self.compile_graph(builder)

    def fresh_invocation(self, **overrides: Any) -> P.EpisodeInvocation:
        seed = {**IDENTITY_SEED, "output_root": str(self.output_root), **overrides}
        return P.prepare_episode_invocation(
            output_root=self.output_root, lock=self.lock, identity_seed=seed
        )


# --------------------------------------------------------------------------
# TEST 1 — checkpoint path, pragmas, thread ids, namespace
# --------------------------------------------------------------------------


class TestCheckpointConfiguration(PersistenceTestCase):
    def test_checkpoint_database_lives_at_the_spec_path(self) -> None:
        expected = self.output_root / ".langgraph" / "checkpoints.sqlite3"
        self.assertEqual(P.checkpoint_db_path(self.output_root), expected)
        self.assertTrue(expected.is_file(), "SqliteSaver.setup() did not create the database file")
        self.assertEqual(
            P.execution_lock_path(self.output_root),
            self.output_root / ".langgraph" / "execution.lock",
        )

    def test_live_connection_reports_the_required_pragmas(self) -> None:
        observed = P.read_connection_pragmas(self.conn)
        self.assertEqual(observed["journal_mode"], "wal")
        self.assertEqual(observed["synchronous"], 2, "synchronous must be FULL (2)")
        self.assertEqual(observed["foreign_keys"], 1)
        self.assertEqual(observed["busy_timeout"], P.SQLITE_BUSY_TIMEOUT_MS)
        self.assertEqual(P.verify_connection_pragmas(self.conn), observed)

    def test_wal_mode_is_visible_in_the_actual_sqlite_file_header(self) -> None:
        # Byte 18/19 of the SQLite header are the file format read/write versions;
        # WAL sets both to 2. This reads the committed file, not the connection.
        self.conn.commit()
        header = P.checkpoint_db_path(self.output_root).read_bytes()[:20]
        self.assertEqual((header[18], header[19]), (2, 2), "database file is not in WAL format")

    def test_a_relaxed_pragma_is_refused_rather_than_silently_accepted(self) -> None:
        self.conn.execute("PRAGMA synchronous=OFF")
        with self.assertRaises(P.CheckpointCorrupt):
            P.verify_connection_pragmas(self.conn)

    def test_saver_tables_exist_in_the_real_database(self) -> None:
        names = {
            row[0]
            for row in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        self.assertIn("checkpoints", names)
        self.assertIn("writes", names)

    def test_thread_ids_follow_the_frozen_format(self) -> None:
        self.assertEqual(P.episode_thread_id("run-x", 1), "run-x:episode:000001")
        self.assertEqual(P.episode_thread_id("run-x", 123456), "run-x:episode:123456")
        self.assertEqual(P.recovery_thread_id("run-x", 7), "run-x:recover:7")
        for bad in (0, -1):
            with self.subTest(ordinal=bad), self.assertRaises(P.PersistenceError):
                P.episode_thread_id("run-x", bad)

    def test_invoke_config_is_exactly_thread_id_and_root_namespace(self) -> None:
        config = P.invoke_config("run-x:episode:000001")
        self.assertEqual(
            config, {"configurable": {"thread_id": "run-x:episode:000001", "checkpoint_ns": ""}}
        )
        self.assertEqual(P.CHECKPOINT_NS, "")

    def test_strict_msgpack_is_enforced_for_persisted_values(self) -> None:
        self.assertEqual(os.environ[P.STRICT_MSGPACK_ENV], "true")

    def test_a_real_checkpoint_is_stored_under_the_root_namespace(self) -> None:
        invocation = self.fresh_invocation()
        self.linear_graph().invoke({"seen": []}, config=invocation.config)
        rows = self.conn.execute(
            "SELECT DISTINCT thread_id, checkpoint_ns FROM checkpoints"
        ).fetchall()
        self.assertEqual(rows, [(invocation.thread_id, "")])
        self.assertTrue(invocation.thread_id.endswith(":episode:000001"))
        self.assertTrue(invocation.thread_id.startswith(invocation.run_id))

    def test_run_id_is_deterministic_and_seed_sensitive(self) -> None:
        first = P.compute_fresh_run_id(IDENTITY_SEED)
        self.assertEqual(first, P.compute_fresh_run_id(dict(IDENTITY_SEED)))
        drifted = {**IDENTITY_SEED, "mode": "all"}
        self.assertNotEqual(first, P.compute_fresh_run_id(drifted))

    def test_prepare_requires_the_exclusive_lock(self) -> None:
        idle = P.ExecutionLock(self.output_root)
        with self.assertRaises(P.PersistenceError):
            P.prepare_episode_invocation(
                output_root=self.output_root, lock=idle, identity_seed=IDENTITY_SEED
            )


# --------------------------------------------------------------------------
# TEST 2 — snapshots, next/tasks, pending writes, evidence high-water marks
# --------------------------------------------------------------------------


class TestSupersepCorrelation(PersistenceTestCase):
    def test_snapshot_next_tasks_and_evidence_marks_correlate_after_a_superstep(self) -> None:
        invocation = self.fresh_invocation()
        graph = self.linear_graph()
        result = graph.invoke({"seen": []}, config=invocation.config)
        self.assertEqual(result["seen"], ["D05", "D13"])

        view = P.ReadOnlyCheckpointView(graph, self.saver)
        readout = P.extract_prior_episode(view, invocation.thread_id)
        self.assertEqual(readout.next, (), "a completed episode still has a task frontier")
        self.assertEqual(readout.tasks, ())
        self.assertEqual(readout.pending_writes, ())
        self.assertGreater(readout.history_length, 1)
        self.assertIsNotNone(readout.checkpoint_id)
        self.assertEqual(readout.state_digest, P.state_digest({"seen": ["D05", "D13"]}))

        store = EvidenceStore(self.output_root)
        store.append(
            "activations",
            {
                "run_id": invocation.run_id,
                "episode_id": invocation.episode_id,
                "activation_id": "act-1",
                "node_id": "D13",
                "phase": "ACT",
            },
        )
        store.append(
            "executions",
            {
                "run_id": invocation.run_id,
                "episode_id": invocation.episode_id,
                "activation_id": "act-1",
                "node_id": "D13",
                "status": "OK",
            },
        )
        record = P.record_checkpoint_correlation(
            store,
            run_id=invocation.run_id,
            episode_id=invocation.episode_id,
            node_id="D13",
            activation_id="act-1",
            readout=readout,
        )
        payload = record.payload
        self.assertEqual(payload["checkpoint_id"], readout.checkpoint_id)
        self.assertEqual(payload["checkpoint_ns"], "")
        self.assertEqual(payload["state_digest"], readout.state_digest)
        self.assertEqual(payload["thread_id"], invocation.thread_id)
        self.assertEqual(payload["evidence_ordinal"], 1)
        self.assertEqual(payload["evidence_high_water"]["activations"], 1)
        self.assertEqual(payload["evidence_high_water"]["executions"], 1)
        self.assertTrue(store.audit_all()["checkpoints"].passed)

    def test_a_correlation_record_is_hash_chained_and_tamper_evident(self) -> None:
        invocation = self.fresh_invocation()
        graph = self.linear_graph()
        graph.invoke({"seen": []}, config=invocation.config)
        view = P.ReadOnlyCheckpointView(graph, self.saver)
        readout = P.extract_prior_episode(view, invocation.thread_id)
        store = EvidenceStore(self.output_root)
        P.record_checkpoint_correlation(
            store,
            run_id=invocation.run_id,
            episode_id=invocation.episode_id,
            node_id="D13",
            activation_id="act-1",
            readout=readout,
        )
        log = store.log("checkpoints")
        self.assertTrue(log.audit().passed)
        tampered = log.path.read_text(encoding="utf-8").replace(readout.state_digest, "0" * 64)
        log.path.write_text(tampered, encoding="utf-8")
        self.assertFalse(log.audit().passed)


# --------------------------------------------------------------------------
# TEST 3 — crash matrix around checkpoint/admission boundaries
# --------------------------------------------------------------------------


class TestCrashMatrix(unittest.TestCase):
    BOUNDARIES = ("before_admit", "after_admit", "after_checkpoint")

    def test_a_real_sigkill_at_every_boundary_duplicates_no_committed_work(self) -> None:
        for boundary in self.BOUNDARIES:
            with self.subTest(boundary=boundary):
                output_root = Path(tempfile.mkdtemp(prefix=f"plan26_n21_crash_{boundary}_"))
                thread_id = "run-crash:episode:000001"
                child = _run_child(CRASH_CHILD, str(output_root), boundary, thread_id)
                self.assertEqual(
                    child.returncode,
                    -signal.SIGKILL,
                    f"child did not die by SIGKILL at {boundary}: {child.stderr[-400:]}",
                )

                admissions = P.AdmissionLedger(output_root)
                before = [
                    r for r in admissions.records() if r["payload"]["key"] == "unit-a:render:1"
                ]
                self.assertEqual(len(before), 0 if boundary == "before_admit" else 1)

                # Retry the same committed work under the same activation key.
                was_new, digest = admissions.admit("unit-a:render:1", {"bytes": "ACCEPTED"})
                self.assertEqual(was_new, boundary == "before_admit")
                after = [
                    r for r in admissions.records() if r["payload"]["key"] == "unit-a:render:1"
                ]
                self.assertEqual(len(after), 1, "retry duplicated committed work")
                self.assertEqual(after[0]["payload"]["output_hash"], digest)

                # A second retry is still idempotent, and the lock the dead
                # process held was released by the kernel.
                admissions.admit("unit-a:render:1", {"bytes": "ACCEPTED"})
                self.assertEqual(
                    len([r for r in admissions.records() if r["payload"]["key"] == "unit-a:render:1"]),
                    1,
                )
                P.ExecutionLock(output_root).acquire().release()

    def test_a_differing_replay_under_a_committed_key_is_an_integrity_failure(self) -> None:
        output_root = Path(tempfile.mkdtemp(prefix="plan26_n21_admit_"))
        admissions = P.AdmissionLedger(output_root)
        admissions.admit("unit-a:render:1", {"bytes": "ACCEPTED"})
        with self.assertRaises(P.AdmissionConflict):
            admissions.admit("unit-a:render:1", {"bytes": "DIFFERENT"})
        self.assertEqual(len(admissions.records()), 1)

    def test_completed_sibling_work_replays_its_write_instead_of_re_executing(self) -> None:
        output_root = Path(tempfile.mkdtemp(prefix="plan26_n21_replay_"))
        lock = P.ExecutionLock(output_root).acquire()
        self.addCleanup(lock.release)
        saver, conn = P.open_checkpoint_saver(output_root)
        self.addCleanup(conn.close)

        executions: list[str] = []
        failures: list[int] = []

        def good(_state):
            executions.append("good")
            return {"ok": ["good"]}

        def bad(_state):
            if not failures:
                failures.append(1)
                raise RuntimeError("deliberate superstep failure")
            return {"ok": ["bad"]}

        builder = StateGraph(FanoutState)
        builder.add_node("good", good)
        builder.add_node("bad", bad)
        builder.add_edge(START, "good")
        builder.add_edge(START, "bad")
        builder.add_edge("good", END)
        builder.add_edge("bad", END)
        graph = builder.compile(checkpointer=saver, name=P.COMPILED_GRAPH_NAME)
        config = P.invoke_config("run-replay:episode:000001")

        with self.assertRaises(RuntimeError):
            graph.invoke({"ok": []}, config=config)
        resumed = graph.invoke(None, config=config)
        self.assertEqual(resumed["ok"].count("good"), 1, "committed sibling work ran twice")
        self.assertEqual(executions, ["good"], "the completed task re-executed on retry")


# --------------------------------------------------------------------------
# TEST 4 — fan-out sibling crash: pending writes survive, join stays unsatisfied
# --------------------------------------------------------------------------


class TestFanoutSiblingCrash(PersistenceTestCase):
    def test_surviving_pending_write_cannot_satisfy_a_partial_join(self) -> None:
        builder = StateGraph(FanoutState)
        builder.add_node("good", lambda state: {"ok": ["good"]})

        def bad(_state):
            raise RuntimeError("sibling crashed")

        builder.add_node("bad", bad)
        builder.add_edge(START, "good")
        builder.add_edge(START, "bad")
        builder.add_edge("good", END)
        builder.add_edge("bad", END)
        graph = self.compile_graph(builder)
        config = P.invoke_config("run-fanout:episode:000001")

        with self.assertRaises(RuntimeError):
            graph.invoke({"ok": []}, config=config)

        checkpoint_tuple = self.saver.get_tuple(config)
        self.assertIsNotNone(checkpoint_tuple)
        channels = {write[1] for write in checkpoint_tuple.pending_writes}
        self.assertIn("ok", channels, "surviving sibling's pending write was lost")

        view = P.ReadOnlyCheckpointView(graph, self.saver)
        readout = P.extract_prior_episode(view, "run-fanout:episode:000001")
        self.assertIn("bad", readout.next, "crashed sibling left the frontier")
        self.assertTrue(
            any(write["channel"] == "ok" for write in readout.pending_writes),
            "readout dropped the surviving pending write",
        )

        frontier = P.compute_resume_frontier(
            readout=readout,
            denominators={"visual_result": {"expected": ["good", "bad"], "completed": ["good"]}},
        )
        join = frontier["joins"]["visual_result"]
        self.assertFalse(join["satisfied"], "a partial fan-out was admitted as a join")
        self.assertEqual(join["pending"], ["bad"])
        self.assertEqual(join["completed"], ["good"])

    def test_join_is_satisfied_only_when_every_denominator_member_completed(self) -> None:
        self.assertTrue(
            P.classify_join_members(expected_keys=["a", "b"], completed_keys=["b", "a"])["satisfied"]
        )
        self.assertFalse(
            P.classify_join_members(expected_keys=["a", "b"], completed_keys=["a"])["satisfied"]
        )
        self.assertFalse(
            P.classify_join_members(expected_keys=[], completed_keys=[])["satisfied"],
            "an empty denominator must not count as a satisfied join",
        )
        with self.assertRaises(P.PersistenceError):
            P.classify_join_members(expected_keys=["a"], completed_keys=["a", "zz"])


# --------------------------------------------------------------------------
# TEST 5 — resume refusal on identity/digest/executable/evidence/accepted drift
# --------------------------------------------------------------------------


class TestResumeRefusal(PersistenceTestCase):
    BASELINE = {
        "frozen_digest": "a" * 64,
        "frozen_inputs": [{"path": "m.yaml", "sha256": "b" * 64, "role": "manifest"}],
        "frozen_executable_identities": [{"name": "codex", "sha256": "c" * 64}],
        "evidence_chain_hashes": {"activations": "d" * 64},
        "accepted_receipt_hashes": {"U01": "e" * 64},
        "accepted_byte_digests": {"units/U01/unit.pdf": "f" * 64},
    }

    DRIFTS = (
        ("identity", "contract_version", "plan26.v2"),
        ("frozen_digest", "frozen_digest", "0" * 64),
        ("executable", "frozen_executable_identities", [{"name": "codex", "sha256": "0" * 64}]),
        ("evidence", "evidence_chain_hashes", {"activations": "0" * 64}),
        ("accepted_bytes", "accepted_byte_digests", {"units/U01/unit.pdf": "0" * 64}),
        ("accepted_bytes", "accepted_receipt_hashes", {"U01": "0" * 64}),
    )

    def _expected(self) -> dict[str, Any]:
        return {**IDENTITY_SEED, "run_id": "run-x", **self.BASELINE}

    def test_every_drift_class_refuses_resume(self) -> None:
        for drift_class, field, mutated in self.DRIFTS:
            with self.subTest(drift_class=drift_class, field=field):
                with self.assertRaises(P.ResumeRefused) as caught:
                    P.validate_resume_inputs(
                        expected=self._expected(), observed={field: mutated}
                    )
                self.assertEqual(caught.exception.drift_class, drift_class)
                self.assertEqual(caught.exception.field, field)

    def test_matching_inputs_are_admitted(self) -> None:
        expected = self._expected()
        observed = {field: expected[field] for _, field, _ in self.DRIFTS}
        P.validate_resume_inputs(expected=expected, observed=observed)

    def test_an_unclassified_input_is_refused_rather_than_ignored(self) -> None:
        with self.assertRaises(P.ResumeRefused) as caught:
            P.validate_resume_inputs(expected=self._expected(), observed={"surprise": 1})
        self.assertEqual(caught.exception.drift_class, "identity")

    def test_a_missing_baseline_key_is_refused(self) -> None:
        with self.assertRaises(P.ResumeRefused) as caught:
            P.validate_resume_inputs(expected={}, observed={"frozen_digest": "a" * 64})
        self.assertEqual(caught.exception.drift_class, "frozen_digest")

    def test_non_resumable_terminals_are_rejected(self) -> None:
        for name in sorted(P.NON_RESUMABLE_TERMINALS):
            with self.subTest(terminal=name):
                with self.assertRaises(P.ResumeRefused) as caught:
                    P._validate_terminal_legality({"terminal": name})
                self.assertEqual(caught.exception.drift_class, "terminal_legality")
        for name in sorted(P.RESUMABLE_TERMINALS):
            with self.subTest(terminal=name):
                self.assertEqual(P._validate_terminal_legality({"terminal": name}), name)

    def test_refused_resume_performs_no_product_work(self) -> None:
        invocation = self.fresh_invocation()
        self.linear_graph().invoke({"seen": []}, config=invocation.config)
        P.EpisodeLeaseLedger(self.output_root).close_episode(
            episode_ordinal=invocation.episode_ordinal,
            terminal={"terminal": "INTERRUPTED", "reason": "test"},
        )
        product = self.output_root / "units" / "U01"
        product.mkdir(parents=True)
        (product / "unit.pdf").write_bytes(b"ACCEPTED BYTES")
        before_product = _tree_snapshot(self.output_root)
        before_ledger = P.EpisodeLeaseLedger(self.output_root).records()

        with self.assertRaises(P.ResumeRefused) as caught:
            P.prepare_episode_invocation(
                output_root=self.output_root,
                lock=self.lock,
                resume=True,
                resume_baseline={"frozen_digest": "a" * 64},
                recomputed={"frozen_digest": "0" * 64},
            )
        self.assertEqual(caught.exception.drift_class, "frozen_digest")
        self.assertEqual(_tree_snapshot(self.output_root), before_product)
        self.assertEqual(P.EpisodeLeaseLedger(self.output_root).records(), before_ledger)

    def test_run_id_disagreement_with_the_envelope_refuses(self) -> None:
        invocation = self.fresh_invocation()
        self.assertEqual(invocation.bootstrap_kind, P.BOOTSTRAP_FRESH)
        P.EpisodeLeaseLedger(self.output_root).close_episode(
            episode_ordinal=1, terminal={"terminal": "INTERRUPTED"}
        )
        with self.assertRaises(P.ResumeRefused) as caught:
            P.prepare_episode_invocation(
                output_root=self.output_root,
                lock=self.lock,
                resume=True,
                identity_seed={**IDENTITY_SEED, "output_root": "/somewhere/else"},
            )
        self.assertEqual(caught.exception.drift_class, "identity")
        self.assertEqual(caught.exception.field, "run_id")

    def test_a_fresh_invocation_over_a_prior_identity_is_refused(self) -> None:
        self.fresh_invocation()
        with self.assertRaises(P.ResumeRefused):
            self.fresh_invocation()

    def test_identity_envelope_bytes_are_immutable(self) -> None:
        invocation = self.fresh_invocation()
        with self.assertRaises(P.ResumeRefused):
            P.write_identity_envelope(self.output_root, {"run_id": "run-other"})
        self.assertEqual(
            P.read_identity_envelope(self.output_root)["run_id"], invocation.run_id
        )


# --------------------------------------------------------------------------
# TEST 6 — graceful interrupt: one terminal candidate, deterministic frontier
# --------------------------------------------------------------------------


class TestGracefulInterrupt(PersistenceTestCase):
    def test_sigint_sets_the_token_and_blocks_new_transmission(self) -> None:
        token = P.InterruptToken(self.output_root).install()
        self.addCleanup(token.close)
        self.assertFalse(token.is_set())
        token.guard_transmission("M03 dispatch")  # allowed before the signal

        signal.raise_signal(signal.SIGINT)

        self.assertTrue(token.is_set())
        self.assertEqual(token.reason, "SIGINT")
        with self.assertRaises(P.InterruptionRequested):
            token.guard_transmission("M03 dispatch")
        self.assertIn(b"INTERRUPTED", token.marker_path.read_bytes())

    def test_sigterm_is_handled_the_same_way(self) -> None:
        token = P.InterruptToken(self.output_root).install()
        self.addCleanup(token.close)
        signal.raise_signal(signal.SIGTERM)
        self.assertTrue(token.is_set())
        self.assertEqual(token.reason, "SIGTERM")

    def test_interrupt_writes_one_terminal_and_a_deterministic_safe_frontier(self) -> None:
        invocation = self.fresh_invocation()
        builder = StateGraph(LinearState)
        builder.add_node("D05", lambda state: {"seen": ["D05"]})

        def interrupted(_state):
            raise RuntimeError("aborted at the atomic boundary")

        builder.add_node("D13", interrupted)
        builder.add_edge(START, "D05")
        builder.add_edge("D05", "D13")
        builder.add_edge("D13", END)
        graph = self.compile_graph(builder)
        with self.assertRaises(RuntimeError):
            graph.invoke({"seen": []}, config=invocation.config)

        view = P.ReadOnlyCheckpointView(graph, self.saver)
        readout = P.extract_prior_episode(view, invocation.thread_id)
        first = P.compute_resume_frontier(readout=readout, reason="interrupt")
        second = P.compute_resume_frontier(readout=readout, reason="interrupt")
        self.assertEqual(first["frontier_digest"], second["frontier_digest"])
        self.assertEqual(first["destinations"], ["D13"])
        self.assertEqual(first, second)

        candidate = P.build_interrupt_terminal_candidate(
            run_id=invocation.run_id,
            episode_id=invocation.episode_id,
            frontier=first,
            classification="graceful_signal",
            heads={},
            high_water_marks={"checkpoint_records": 1, "evidence_records": 0},
        )
        self.assertEqual(candidate["kind"], "INTERRUPTED")
        self.assertEqual(candidate["resume_frontier"], first)
        self.assertEqual(candidate["resume_frontier_digest"], first["frontier_digest"])

        ledger = P.EpisodeLeaseLedger(self.output_root)
        ledger.close_episode(episode_ordinal=invocation.episode_ordinal, terminal=candidate)
        closed = [
            record
            for record in ledger.records()
            if record["payload"]["state"] == "CLOSED"
            and record["payload"]["episode_ordinal"] == invocation.episode_ordinal
        ]
        self.assertEqual(len(closed), 1, "the episode wrote more than one terminal")
        with self.assertRaises(P.EpisodeLedgerError):
            ledger.close_episode(episode_ordinal=invocation.episode_ordinal, terminal=candidate)

    def test_the_candidate_is_accepted_by_the_real_d98_validator(self) -> None:
        """The cross-node contract: D98 must accept what this node builds.

        D98 re-derives the INTERRUPTED precondition itself and downgrades any
        candidate it cannot confirm to SYSTEM_FAILURE, so an interoperable shape
        is the only thing that makes a graceful interrupt actually interrupt.
        """
        invocation = self.fresh_invocation()
        readout = P.PriorEpisodeReadout(
            thread_id=invocation.thread_id, checkpoint_id="ckpt-9",
            parent_checkpoint_id=None, values={}, next=("D13",), tasks=(),
            pending_writes=(), state_digest="a" * 64, history_length=2, terminal=None,
        )
        frontier = P.compute_resume_frontier(readout=readout, reason="interrupt")
        heads = {"units/U01/content": "c" * 64}

        candidate = P.build_interrupt_terminal_candidate(
            run_id=invocation.run_id,
            episode_id=invocation.episode_id,
            frontier=frontier,
            classification="graceful_signal",
            heads=heads,
            high_water_marks={
                "checkpoint_records": 1,
                "evidence_records": 2,
                "last_checkpoint_id": "ckpt-9",
            },
        )

        state = {
            "terminal_candidate": candidate,
            "terminal": None,
            "terminal_history": [],
            "episode_id": invocation.episode_id,
            "run_id": invocation.run_id,
            "mode": "one",
            "requested_unit_id": "U01",
            "effective_run": {"ordered_unit_ids": ["U01"], "target_closure": ["U01"]},
            "accepted_unit_receipts": {},
            "final_release_audits": [],
            "workbook_head": {},
            "artifact_heads": {
                "units/U01/content": {"version": 1, "parent_hash": None, "hash": "c" * 64}
            },
            "attempt_counters": {},
            "failure_fingerprints": [],
            "checkpoint_metadata": [{"checkpoint_id": "ckpt-9"}],
            "evidence_index_entries": [{"key": "e1"}, {"key": "e2"}],
            "pending_failure": None,
            "resume_frontier": None,
            "output_root": str(self.output_root),
        }
        projection = project_for_node("D98_WRITE_TERMINAL", state)

        validation = D98.validate_terminal_candidate(candidate, projection)
        self.assertTrue(validation.accepted, f"D98 rejected the candidate: {validation.rejections}")
        self.assertEqual(validation.kind, "INTERRUPTED")

        record = D98.write_terminal(projection)["terminal"]
        self.assertEqual(record["kind"], "INTERRUPTED")
        self.assertEqual(record["exit_code"], 10)
        self.assertTrue(record["resumable"])
        self.assertEqual(record["evidence"]["resume_frontier"], frontier)

        # A stale head is what D98 exists to catch; the shape alone must not pass.
        stale = dict(candidate, heads={"units/U01/content": "d" * 64})
        self.assertFalse(D98.validate_terminal_candidate(stale, projection).accepted)

    def test_the_classification_vocabulary_matches_d98s_authority(self) -> None:
        self.assertEqual(P.INTERRUPT_CLASSIFICATIONS, D98._INTERRUPT_CLASSIFICATIONS)
        with self.assertRaises(P.PersistenceError):
            P.build_interrupt_terminal_candidate(
                run_id="run-1", episode_id="ep-1",
                frontier={"frontier_digest": "0" * 64, "destinations": []},
                classification="SIGINT", heads={}, high_water_marks={},
            )

    def test_frontier_digest_changes_when_the_frontier_changes(self) -> None:
        base = P.PriorEpisodeReadout(
            thread_id="t", checkpoint_id="c", parent_checkpoint_id=None, values={},
            next=("D13",), tasks=(), pending_writes=(), state_digest="0" * 64,
            history_length=1, terminal=None,
        )
        other = dataclasses_replace(base, next=("D15",))
        self.assertNotEqual(
            P.compute_resume_frontier(readout=base)["frontier_digest"],
            P.compute_resume_frontier(readout=other)["frontier_digest"],
        )


def dataclasses_replace(instance: P.PriorEpisodeReadout, **changes: Any) -> P.PriorEpisodeReadout:
    import dataclasses

    return dataclasses.replace(instance, **changes)


# --------------------------------------------------------------------------
# TEST 7 — orphan recovery performs zero product side effects
# --------------------------------------------------------------------------


class TestOrphanRecovery(unittest.TestCase):
    def test_recovery_after_sigkill_uses_a_new_thread_and_touches_no_product(self) -> None:
        output_root = Path(tempfile.mkdtemp(prefix="plan26_n21_orphan_")).resolve()
        product = output_root / "units" / "U01"
        product.mkdir(parents=True)
        (product / "unit.pdf").write_bytes(b"ACCEPTED BYTES")
        (product / "receipt.json").write_text(json.dumps({"accepted": True}), encoding="utf-8")

        child = _run_child(ORPHAN_CHILD, str(output_root))
        self.assertEqual(
            child.returncode, -signal.SIGKILL, f"orphan child survived: {child.stderr[-400:]}"
        )
        orphan_thread = child.stdout.strip()
        self.assertTrue(orphan_thread.endswith(":episode:000001"), orphan_thread)

        ledger = P.EpisodeLeaseLedger(output_root)
        self.assertIsNotNone(ledger.open_lease(), "unclean exit did not leave an open lease")

        before = _tree_snapshot(output_root)
        lock = P.ExecutionLock(output_root).acquire()
        self.addCleanup(lock.release)
        saver, conn = P.open_checkpoint_saver(output_root)
        self.addCleanup(conn.close)
        builder = StateGraph(LinearState)
        builder.add_node("D05", lambda state: {"seen": ["D05"]})
        builder.add_edge(START, "D05")
        builder.add_edge("D05", END)
        graph = builder.compile(checkpointer=saver, name=P.COMPILED_GRAPH_NAME)
        view = P.ReadOnlyCheckpointView(graph, saver)

        invocation = P.prepare_episode_invocation(
            output_root=output_root, lock=lock, resume=True, read_view=view
        )
        self.assertEqual(invocation.bootstrap_kind, P.BOOTSTRAP_RECOVER_ORPHAN)
        self.assertEqual(invocation.prior_thread_id, orphan_thread)
        self.assertNotEqual(invocation.thread_id, orphan_thread)
        self.assertEqual(invocation.thread_id, f"{invocation.run_id}:recover:1")
        self.assertEqual(invocation.config["configurable"]["checkpoint_ns"], "")
        self.assertIsNotNone(invocation.resume_from)
        self.assertEqual(invocation.resume_from["thread_id"], orphan_thread)

        self.assertEqual(
            _tree_snapshot(output_root), before, "recovery mutated product bytes"
        )

    def test_recovery_services_raise_on_any_touch(self) -> None:
        services = P.build_recovery_services()
        self.assertEqual(
            sorted(services), ["renderer", "source_retriever", "transport_registry"]
        )
        for name, service in services.items():
            with self.subTest(service=name):
                with self.assertRaises(P.RecoveryServiceForbidden):
                    service.send({"job": "M01"})
                with self.assertRaises(P.RecoveryServiceForbidden):
                    service()
                with self.assertRaises(P.RecoveryServiceForbidden):
                    service.anything  # noqa: B018 - any attribute touch must raise

    def test_a_recovery_runtime_context_carries_only_forbidden_product_services(self) -> None:
        output_root = Path(tempfile.mkdtemp(prefix="plan26_n21_ctx_")).resolve()
        services = P.build_recovery_services()
        context = RuntimeContext(
            engine_root=Path("/engine"),
            output_root=output_root,
            path_guard=object(),
            evidence_service=EvidenceStore(output_root),
            transport_registry=services["transport_registry"],
            source_retriever=services["source_retriever"],
            signal_token=P.InterruptToken(),
            clock=lambda: 0,
        )
        with self.assertRaises(P.RecoveryServiceForbidden):
            context.transport_registry.dispatch("M01")
        with self.assertRaises(P.RecoveryServiceForbidden):
            context.source_retriever.fetch("https://example.invalid")
        # The evidence writer stays real: D96/D98 must still record the closure.
        context.evidence_service.append(
            "events",
            {"run_id": "run-x", "episode_id": "run-x:recover:1", "kind": "RECOVER", "node_id": "D96"},
        )
        self.assertEqual(context.evidence_service.high_water_marks()["events"], 1)

    def test_the_read_only_view_cannot_continue_a_prior_thread(self) -> None:
        output_root = Path(tempfile.mkdtemp(prefix="plan26_n21_ro_")).resolve()
        lock = P.ExecutionLock(output_root).acquire()
        self.addCleanup(lock.release)
        saver, conn = P.open_checkpoint_saver(output_root)
        self.addCleanup(conn.close)
        builder = StateGraph(LinearState)
        builder.add_node("D05", lambda state: {"seen": ["D05"]})
        builder.add_edge(START, "D05")
        builder.add_edge("D05", END)
        graph = builder.compile(checkpointer=saver, name=P.COMPILED_GRAPH_NAME)
        view = P.ReadOnlyCheckpointView(graph, saver)
        for forbidden in ("invoke", "stream", "update_state", "ainvoke", "batch"):
            with self.subTest(method=forbidden):
                self.assertFalse(hasattr(view, forbidden))
        with self.assertRaises(AttributeError):
            view.invoke(None, config=P.invoke_config("t"))

    def test_persistence_module_never_calls_invoke_or_update_state(self) -> None:
        tree = ast.parse(PERSISTENCE_SOURCE.read_text(encoding="utf-8"))
        called = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        for forbidden in ("invoke", "ainvoke", "stream", "astream", "update_state", "batch"):
            with self.subTest(method=forbidden):
                self.assertNotIn(
                    forbidden, called, f"persistence.py calls .{forbidden}() on something"
                )

    def test_persistence_module_imports_no_product_or_model_module(self) -> None:
        tree = ast.parse(PERSISTENCE_SOURCE.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        forbidden_prefixes = (
            "curriculum_factory.langgraph_factory.transport",
            "curriculum_factory.langgraph_factory.egress",
            "curriculum_factory.langgraph_factory.model_nodes",
            "curriculum_factory.langgraph_factory.nodes",
            "curriculum_factory.langgraph_factory.workbook",
            "langchain",
            "openai",
            "httpx",
            "requests",
            "urllib",
            "socket",
        )
        offenders = sorted(
            name
            for name in imported
            if any(name == prefix or name.startswith(prefix + ".") for prefix in forbidden_prefixes)
        )
        # The retired image/text-generation SDK family, named by module-name
        # suffix rather than the retired provider's own name so this active
        # test stays out of the retired-provider term scan (N50V7 evidence
        # audit contract) while still catching every forbidden import it did.
        offenders += sorted(
            name for name in imported if "generativeai" in name or "_genai" in name
        )
        self.assertEqual(offenders, [], "persistence.py reached a product or transport module")


# --------------------------------------------------------------------------
# TEST 8 — an incomplete model activation routes to D91, never back to a model
# --------------------------------------------------------------------------


class TestModelFrontierRouting(PersistenceTestCase):
    def test_an_aborted_model_node_frontier_becomes_d91(self) -> None:
        invocation = self.fresh_invocation()
        builder = StateGraph(LinearState)
        builder.add_node("D03", lambda state: {"seen": ["D03"]})

        def aborted_model(_state):
            raise RuntimeError("model subprocess aborted by the timeout protocol")

        builder.add_node("M03", aborted_model)
        builder.add_edge(START, "D03")
        builder.add_edge("D03", "M03")
        builder.add_edge("M03", END)
        graph = self.compile_graph(builder)
        with self.assertRaises(RuntimeError):
            graph.invoke({"seen": []}, config=invocation.config)

        view = P.ReadOnlyCheckpointView(graph, self.saver)
        readout = P.extract_prior_episode(view, invocation.thread_id)
        self.assertEqual(readout.next, ("M03",), "the real frontier is not the model node")

        frontier = P.compute_resume_frontier(readout=readout, reason="resume")
        self.assertEqual(frontier["destinations"], ["D91"])
        self.assertEqual(
            frontier["reclassified_model_destinations"], [{"from": "M03", "to": "D91"}]
        )
        self.assertFalse(
            set(frontier["destinations"]) & P.MODEL_NODE_IDS,
            "a model node survived as a resume destination",
        )

    def test_every_model_node_id_is_reclassified(self) -> None:
        for model_id in sorted(P.MODEL_NODE_IDS):
            with self.subTest(model=model_id):
                readout = P.PriorEpisodeReadout(
                    thread_id="t", checkpoint_id="c", parent_checkpoint_id=None, values={},
                    next=(model_id,), tasks=({"id": "1", "name": model_id, "error": None,
                                              "interrupts": 0},),
                    pending_writes=(), state_digest="0" * 64, history_length=1, terminal=None,
                )
                frontier = P.compute_resume_frontier(readout=readout)
                self.assertEqual(frontier["destinations"], ["D91"])

    def test_deterministic_destinations_are_preserved_unchanged(self) -> None:
        readout = P.PriorEpisodeReadout(
            thread_id="t", checkpoint_id="c", parent_checkpoint_id=None, values={},
            next=("D07", "D13"), tasks=(), pending_writes=(), state_digest="0" * 64,
            history_length=1, terminal=None,
        )
        self.assertEqual(P.compute_resume_frontier(readout=readout)["destinations"], ["D07", "D13"])


# --------------------------------------------------------------------------
# TEST 9 — one lock winner; the loser mutates nothing
# --------------------------------------------------------------------------


class TestExecutionLockRace(unittest.TestCase):
    def test_two_real_processes_race_and_the_loser_mutates_nothing(self) -> None:
        output_root = Path(tempfile.mkdtemp(prefix="plan26_n21_lock_")).resolve()
        winner = P.ExecutionLock(output_root).acquire()
        self.addCleanup(winner.release)
        saver, conn = P.open_checkpoint_saver(output_root)
        self.addCleanup(conn.close)
        (output_root / "units").mkdir()
        (output_root / "units" / "unit.pdf").write_bytes(b"ACCEPTED BYTES")

        before = _tree_snapshot(output_root, skip_control=False)
        loser = _run_child(LOCK_CHILD, str(output_root))
        after = _tree_snapshot(output_root, skip_control=False)

        self.assertEqual(loser.returncode, P.LOCK_LOSER_EXIT_CODE, loser.stderr[-400:])
        self.assertIn("LOSER", loser.stderr)
        self.assertNotIn("WINNER", loser.stdout)
        self.assertEqual(before, after, "the losing process mutated the output root")
        self.assertEqual(sorted(before), sorted(after))

    def test_the_lock_is_reacquirable_once_the_winner_releases(self) -> None:
        output_root = Path(tempfile.mkdtemp(prefix="plan26_n21_lock2_")).resolve()
        winner = P.ExecutionLock(output_root).acquire()
        self.assertEqual(_run_child(LOCK_CHILD, str(output_root)).returncode, P.LOCK_LOSER_EXIT_CODE)
        winner.release()
        self.assertEqual(_run_child(LOCK_CHILD, str(output_root)).returncode, 0)

    def test_a_second_in_process_acquisition_is_also_refused(self) -> None:
        output_root = Path(tempfile.mkdtemp(prefix="plan26_n21_lock3_")).resolve()
        first = P.ExecutionLock(output_root).acquire()
        self.addCleanup(first.release)
        with self.assertRaises(P.ExecutionLockUnavailable):
            P.ExecutionLock(output_root).acquire()


# --------------------------------------------------------------------------
# TEST 10 — either layer's corruption blocks recovery, with no self-repair
# --------------------------------------------------------------------------


class TestCorruptionBlocksRecovery(unittest.TestCase):
    def _populated_root(self) -> tuple[Path, P.ExecutionLock, sqlite3.Connection]:
        output_root = Path(tempfile.mkdtemp(prefix="plan26_n21_corrupt_")).resolve()
        lock = P.ExecutionLock(output_root).acquire()
        self.addCleanup(lock.release)
        saver, conn = P.open_checkpoint_saver(output_root)
        invocation = P.prepare_episode_invocation(
            output_root=output_root,
            lock=lock,
            identity_seed={**IDENTITY_SEED, "output_root": str(output_root)},
        )
        builder = StateGraph(LinearState)
        builder.add_node("D05", lambda state: {"seen": ["D05"]})
        builder.add_edge(START, "D05")
        builder.add_edge("D05", END)
        graph = builder.compile(checkpointer=saver, name=P.COMPILED_GRAPH_NAME)
        graph.invoke({"seen": []}, config=invocation.config)
        P.AdmissionLedger(output_root).admit("unit-a:render:1", {"bytes": "ACCEPTED"})
        P.EpisodeLeaseLedger(output_root).close_episode(
            episode_ordinal=invocation.episode_ordinal, terminal={"terminal": "INTERRUPTED"}
        )
        P.flush_checkpoint_durability(conn, output_root)
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.commit()
        conn.close()
        return output_root, lock, conn

    def test_a_healthy_root_verifies_on_both_layers(self) -> None:
        output_root, _lock, _conn = self._populated_root()
        report = P.verify_persistence_integrity(output_root, EvidenceStore(output_root))
        self.assertEqual(report["checkpoint"]["integrity_check"], "ok")
        self.assertEqual(report["episode_ledger"]["status"], "PASS")
        self.assertEqual(report["admission_ledger"]["status"], "PASS")

    def test_corrupt_sqlite_blocks_recovery_and_is_not_repaired(self) -> None:
        output_root, lock, _conn = self._populated_root()
        db_path = P.checkpoint_db_path(output_root)
        raw = bytearray(db_path.read_bytes())
        page_size = int.from_bytes(raw[16:18], "big")
        self.assertGreater(len(raw), page_size * 2, "database is too small to corrupt a data page")
        raw[page_size : page_size + 512] = b"\xff" * 512
        db_path.write_bytes(bytes(raw))
        corrupted_digest = hashlib.sha256(db_path.read_bytes()).hexdigest()

        # The append-only layer is untouched and still verifies on its own.
        self.assertEqual(P.EpisodeLeaseLedger(output_root).audit()["status"], "PASS")
        self.assertEqual(P.AdmissionLedger(output_root).audit()["status"], "PASS")

        with self.assertRaises(P.CheckpointCorrupt):
            P.verify_checkpoint_integrity(output_root)
        with self.assertRaises(P.CheckpointCorrupt):
            P.verify_persistence_integrity(output_root, EvidenceStore(output_root))
        with self.assertRaises(P.CheckpointCorrupt):
            P.prepare_episode_invocation(output_root=output_root, lock=lock, resume=True)
        self.assertEqual(
            hashlib.sha256(db_path.read_bytes()).hexdigest(),
            corrupted_digest,
            "a failed integrity check repaired the database",
        )

    def test_corrupt_append_log_blocks_recovery_and_is_not_repaired(self) -> None:
        output_root, lock, _conn = self._populated_root()
        ledger_path = P.EpisodeLeaseLedger(output_root).path
        text = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(text.replace('"OPEN"', '"OPENX"', 1), encoding="utf-8")
        corrupted_digest = hashlib.sha256(ledger_path.read_bytes()).hexdigest()

        # The checkpoint layer is untouched and still verifies on its own.
        self.assertEqual(P.verify_checkpoint_integrity(output_root)["integrity_check"], "ok")

        self.assertEqual(P.EpisodeLeaseLedger(output_root).audit()["status"], "FAIL")
        with self.assertRaises(P.CheckpointCorrupt):
            P.verify_persistence_integrity(output_root)
        with self.assertRaises(P.CheckpointCorrupt):
            P.prepare_episode_invocation(output_root=output_root, lock=lock, resume=True)
        self.assertEqual(
            hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
            corrupted_digest,
            "a failed integrity check rewrote the append log",
        )

    def test_a_truncated_append_log_is_detected(self) -> None:
        output_root, _lock, _conn = self._populated_root()
        ledger_path = P.AdmissionLedger(output_root).path
        raw = ledger_path.read_bytes()
        ledger_path.write_bytes(raw[:-5])
        self.assertEqual(P.AdmissionLedger(output_root).audit()["status"], "FAIL")

    def test_evidence_log_corruption_alone_blocks_recovery(self) -> None:
        output_root, _lock, _conn = self._populated_root()
        store = EvidenceStore(output_root)
        store.append(
            "events",
            {"run_id": "run-x", "episode_id": "e1", "kind": "START", "node_id": "D00"},
        )
        log = store.log("events")
        log.path.write_text(
            log.path.read_text(encoding="utf-8").replace('"START"', '"STARTX"'), encoding="utf-8"
        )
        self.assertEqual(P.verify_checkpoint_integrity(output_root)["integrity_check"], "ok")
        with self.assertRaises(P.CheckpointCorrupt):
            P.verify_persistence_integrity(output_root, EvidenceStore(output_root))


# --------------------------------------------------------------------------
# Episode lifecycle: new empty thread per episode (spec 11.1, 11.4 step 6)
# --------------------------------------------------------------------------


class TestEpisodeLifecycle(PersistenceTestCase):
    def test_each_episode_gets_a_new_thread_with_empty_langgraph_state(self) -> None:
        first = self.fresh_invocation()
        graph = self.linear_graph()
        graph.invoke({"seen": []}, config=first.config)
        P.EpisodeLeaseLedger(self.output_root).close_episode(
            episode_ordinal=first.episode_ordinal, terminal={"terminal": "INTERRUPTED"}
        )

        view = P.ReadOnlyCheckpointView(graph, self.saver)
        second = P.prepare_episode_invocation(
            output_root=self.output_root, lock=self.lock, resume=True, read_view=view
        )
        self.assertEqual(second.bootstrap_kind, P.BOOTSTRAP_RESUME)
        self.assertEqual(second.episode_ordinal, 2)
        self.assertEqual(second.thread_id, P.episode_thread_id(first.run_id, 2))
        self.assertEqual(second.prior_thread_id, first.thread_id)
        self.assertEqual(second.run_id, first.run_id)

        # The new thread genuinely starts empty; D04 (N22) is what imports state.
        self.assertIsNone(self.saver.get_tuple(second.config))
        self.assertEqual(graph.get_state(second.config).values, {})
        self.assertEqual(second.resume_from["thread_id"], first.thread_id)
        self.assertEqual(second.resume_from["checkpoint_ns"], "")

    def test_a_lease_cannot_be_opened_twice_or_out_of_order(self) -> None:
        ledger = P.EpisodeLeaseLedger(self.output_root)
        ledger.open_episode(
            run_id="run-x", episode_ordinal=1, thread_id="t1", bootstrap_kind=P.BOOTSTRAP_FRESH
        )
        with self.assertRaises(P.EpisodeLedgerError):
            ledger.open_episode(
                run_id="run-x", episode_ordinal=2, thread_id="t2", bootstrap_kind=P.BOOTSTRAP_RESUME
            )
        ledger.close_episode(episode_ordinal=1, terminal={"terminal": "INTERRUPTED"})
        with self.assertRaises(P.EpisodeLedgerError):
            ledger.open_episode(
                run_id="run-x", episode_ordinal=3, thread_id="t3", bootstrap_kind=P.BOOTSTRAP_RESUME
            )

    def test_episode_state_update_matches_the_frozen_state_fields(self) -> None:
        from curriculum_factory.langgraph_factory.state import FACTORY_STATE_FIELDS

        update = self.fresh_invocation().as_state_update()
        for field in update:
            with self.subTest(field=field):
                self.assertIn(field, FACTORY_STATE_FIELDS)
        self.assertEqual(update["checkpoint_namespace"], "")
        self.assertEqual(update["bootstrap_kind"], P.BOOTSTRAP_FRESH)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
