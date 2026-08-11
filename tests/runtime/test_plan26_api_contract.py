"""Plan 26 official API-contract gate (spec section 3.3).

Proves the exact pinned LangGraph 1.2.9 / langgraph-checkpoint-sqlite 3.1.0
surface the implementation is authorized to use. This does not build the Plan 26
graph (N20 owns that); it proves the API shapes exist and behave as documented.

Skips only where the hash-locked environment is absent; CI installs
requirements/plan26.lock with --require-hashes and therefore always runs it for
real (asserted by tests/runtime/test_plan26_lock_drift.py).
"""

import importlib.metadata
import importlib.util
import inspect
import operator
import sqlite3
import sys
import tempfile
import unittest
from dataclasses import dataclass
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

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Send

REPO_ROOT = Path(__file__).resolve().parents[2]
IN_PATH = REPO_ROOT / "requirements" / "plan26.in"

PINNED_VERSIONS = {
    "langgraph": "1.2.9",
    "langgraph-checkpoint-sqlite": "3.1.0",
    "jsonschema": "4.26.0",
    "PyYAML": "6.0.3",
    "Pillow": "12.2.0",
    "pytest": "9.0.3",
}

FORBIDDEN_MODULES = (
    "langchain",
    "langchain_openai",
    "langchain_google_genai",
    "openai",
    "google.generativeai",
)


def _last(_old: Any, new: Any) -> Any:
    return new


@dataclass(frozen=True)
class RuntimeContextProbe:
    """Stand-in context schema; N11 owns the production RuntimeContext."""

    engine_root: str
    output_root: str


class LinearState(TypedDict, total=False):
    seen: Annotated[list, operator.add]
    head: Annotated[str, _last]
    secret: Annotated[str, _last]


class LinearInput(TypedDict, total=False):
    head: str


class LinearOutput(TypedDict, total=False):
    seen: list
    head: str


class BranchState(TypedDict, total=False):
    n: Annotated[int, _last]
    path: Annotated[list, operator.add]


class LoopState(TypedDict, total=False):
    attempts: Annotated[int, operator.add]


class FanoutState(TypedDict, total=False):
    items: Annotated[list, _last]
    done: Annotated[list, operator.add]
    barrier: Annotated[list, operator.add]


class PendingState(TypedDict, total=False):
    ok: Annotated[list, operator.add]


def _direct_pin_lines() -> list:
    return [
        line.strip()
        for line in IN_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _build_linear_builder() -> StateGraph:
    builder = StateGraph(
        LinearState,
        context_schema=RuntimeContextProbe,
        input_schema=LinearInput,
        output_schema=LinearOutput,
    )
    builder.add_node("first", lambda state: {"seen": ["first"], "head": "first", "secret": "x"})
    builder.add_node("second", lambda state: {"seen": ["second"], "head": "second"})
    builder.add_edge(START, "first")
    builder.add_edge("first", "second")
    builder.add_edge("second", END)
    return builder


class TestPinnedVersions(unittest.TestCase):
    def test_installed_versions_match_direct_pins(self) -> None:
        for dist, want in PINNED_VERSIONS.items():
            with self.subTest(dist=dist):
                self.assertEqual(importlib.metadata.version(dist), want)

    def test_direct_pins_file_declares_exact_versions(self) -> None:
        declared = set(_direct_pin_lines())
        for dist, want in PINNED_VERSIONS.items():
            with self.subTest(dist=dist):
                self.assertIn(f"{dist}=={want}", declared)

    def test_direct_pins_file_declares_nothing_else(self) -> None:
        expected = {f"{d}=={v}" for d, v in PINNED_VERSIONS.items()}
        self.assertEqual(set(_direct_pin_lines()), expected)

    def test_python_is_3_13(self) -> None:
        self.assertEqual(sys.version_info[:2], (3, 13))


class TestForbiddenImports(unittest.TestCase):
    def test_forbidden_model_wrappers_absent_from_locked_environment(self) -> None:
        for name in FORBIDDEN_MODULES:
            with self.subTest(module=name):
                top = name.split(".")[0]
                spec = importlib.util.find_spec(top)
                if top == "google" and spec is not None:
                    # google is a namespace package; only the SDK submodule is forbidden
                    spec = importlib.util.find_spec(name)
                self.assertIsNone(
                    spec, f"forbidden dependency {name} is importable in the locked environment"
                )

    def test_langchain_core_is_transitive_only(self) -> None:
        # langgraph resolves langchain_core internally; that does not authorize wrappers.
        self.assertIsNotNone(importlib.util.find_spec("langchain_core"))
        self.assertNotIn(
            "langchain-core", " ".join(_direct_pin_lines()), "langchain-core must stay transitive"
        )


class TestApiSignatures(unittest.TestCase):
    def test_stategraph_accepts_context_input_output_schemas(self) -> None:
        params = inspect.signature(StateGraph.__init__).parameters
        for name in ("state_schema", "context_schema", "input_schema", "output_schema"):
            with self.subTest(param=name):
                self.assertIn(name, params)

    def test_compile_accepts_checkpointer_and_name(self) -> None:
        params = inspect.signature(StateGraph.compile).parameters
        self.assertIn("checkpointer", params)
        self.assertIn("name", params)

    def test_start_and_end_sentinels(self) -> None:
        self.assertEqual(START, "__start__")
        self.assertEqual(END, "__end__")

    def test_send_signature(self) -> None:
        params = inspect.signature(Send.__init__).parameters
        self.assertIn("node", params)
        self.assertIn("arg", params)

    def test_builder_exposes_edge_api(self) -> None:
        for name in ("add_node", "add_edge", "add_conditional_edges", "compile"):
            with self.subTest(method=name):
                self.assertTrue(callable(getattr(StateGraph, name)))

    def test_compiled_graph_exposes_execution_and_inspection_api(self) -> None:
        for name in ("invoke", "get_state", "get_state_history"):
            with self.subTest(method=name):
                self.assertTrue(callable(getattr(CompiledStateGraph, name)))

    def test_sqlite_saver_takes_a_connection_and_exposes_read_api(self) -> None:
        self.assertIn("conn", inspect.signature(SqliteSaver.__init__).parameters)
        for name in ("get_tuple", "list"):
            with self.subTest(method=name):
                self.assertTrue(callable(getattr(SqliteSaver, name)))


class TestGraphBehavior(unittest.TestCase):
    def test_reducers_input_and_output_schemas(self) -> None:
        graph = _build_linear_builder().compile(name="plan26_api_contract")
        result = graph.invoke({"head": "start"})
        self.assertEqual(result["seen"], ["first", "second"])
        self.assertEqual(result["head"], "second")
        self.assertNotIn("secret", result, "output_schema did not filter undeclared channels")

    def test_conditional_edges_branch_on_state(self) -> None:
        builder = StateGraph(BranchState)
        builder.add_node("route_source", lambda state: {"path": ["source"]})
        builder.add_node("even", lambda state: {"path": ["even"]})
        builder.add_node("odd", lambda state: {"path": ["odd"]})
        builder.add_edge(START, "route_source")
        builder.add_conditional_edges(
            "route_source",
            lambda state: "even" if state["n"] % 2 == 0 else "odd",
            {"even": "even", "odd": "odd"},
        )
        builder.add_edge("even", END)
        builder.add_edge("odd", END)
        graph = builder.compile()
        self.assertEqual(graph.invoke({"n": 2})["path"], ["source", "even"])
        self.assertEqual(graph.invoke({"n": 3})["path"], ["source", "odd"])

    def test_conditional_edge_loop_terminates_on_counter(self) -> None:
        builder = StateGraph(LoopState)
        builder.add_node("work", lambda state: {"attempts": 1})
        builder.add_edge(START, "work")
        builder.add_conditional_edges(
            "work",
            lambda state: "work" if state["attempts"] < 3 else END,
            {"work": "work", END: END},
        )
        self.assertEqual(builder.compile().invoke({"attempts": 0})["attempts"], 3)

    def test_send_map_reduce_fanout_to_barrier(self) -> None:
        builder = StateGraph(FanoutState)
        builder.add_node("plan", lambda state: {"items": state["items"]})
        builder.add_node("worker", lambda payload: {"done": [payload["item"]]})
        builder.add_node("barrier", lambda state: {"barrier": [len(state["done"])]})
        builder.add_edge(START, "plan")
        builder.add_conditional_edges(
            "plan",
            lambda state: [Send("worker", {"item": item}) for item in state["items"]],
            ["worker"],
        )
        builder.add_edge("worker", "barrier")
        builder.add_edge("barrier", END)

        out = builder.compile().invoke({"items": ["a", "b", "c"]})
        self.assertEqual(sorted(out["done"]), ["a", "b", "c"])
        self.assertEqual(out["barrier"], [3], "barrier did not join once after all Send workers")


class TestSqliteSaverBehavior(unittest.TestCase):
    def _saver(self) -> SqliteSaver:
        path = Path(tempfile.mkdtemp(prefix="plan26_api_")) / "checkpoints.sqlite3"
        conn = sqlite3.connect(str(path), check_same_thread=False)
        self.addCleanup(conn.close)
        return SqliteSaver(conn)

    def test_invoke_get_state_and_history_over_saver(self) -> None:
        saver = self._saver()
        graph = _build_linear_builder().compile(
            checkpointer=saver, name="plan26_curriculum_factory"
        )
        config = {"configurable": {"thread_id": "run:episode:000001", "checkpoint_ns": ""}}
        self.assertEqual(graph.invoke({"head": "start"}, config=config)["head"], "second")

        snapshot = graph.get_state(config)
        self.assertEqual(snapshot.next, ())
        self.assertEqual(snapshot.values["seen"], ["first", "second"])

        history = list(graph.get_state_history(config))
        self.assertGreater(len(history), 1)
        ids = [entry.config["configurable"]["checkpoint_id"] for entry in history]
        self.assertEqual(len(ids), len(set(ids)), "state history repeated a checkpoint id")

        tup = saver.get_tuple(config)
        self.assertIsNotNone(tup)
        self.assertEqual(tup.config["configurable"]["thread_id"], "run:episode:000001")
        self.assertEqual(tup.config["configurable"]["checkpoint_ns"], "")
        self.assertGreater(len(list(saver.list(config))), 1)

    def test_pending_writes_survive_a_failed_superstep(self) -> None:
        class Boom(RuntimeError):
            pass

        failures = []

        def bad(_state):
            if not failures:
                failures.append(1)
                raise Boom("deliberate superstep failure")
            return {"ok": ["bad"]}

        builder = StateGraph(PendingState)
        builder.add_node("good", lambda state: {"ok": ["good"]})
        builder.add_node("bad", bad)
        builder.add_edge(START, "good")
        builder.add_edge(START, "bad")
        builder.add_edge("good", END)
        builder.add_edge("bad", END)

        saver = self._saver()
        graph = builder.compile(checkpointer=saver)
        config = {"configurable": {"thread_id": "run:episode:000002", "checkpoint_ns": ""}}
        with self.assertRaises(Boom):
            graph.invoke({"ok": []}, config=config)

        tup = saver.get_tuple(config)
        self.assertIsNotNone(tup)
        channels = {channel for _task_id, channel, _value in (tup.pending_writes or [])}
        self.assertIn(
            "ok", channels, "successful task's write was not persisted as a pending write"
        )

        resumed = graph.invoke(None, config=config)
        self.assertEqual(
            resumed["ok"].count("good"), 1, "completed task re-ran instead of replaying its write"
        )
        self.assertIn("bad", resumed["ok"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
