from __future__ import annotations

import dataclasses
import functools
import hashlib
import itertools
import json
import re
import unittest
from pathlib import Path

from curriculum_factory.langgraph_factory import reducers as R
from curriculum_factory.langgraph_factory.state import (
    FACTORY_INPUT_FIELDS,
    FACTORY_OUTPUT_FIELDS,
    FACTORY_STATE_FIELDS,
    FIELD_REDUCER_CLASSES,
    FIELD_REDUCERS,
    FORBIDDEN_RUNTIME_CONTEXT_FIELDS,
    RUNTIME_CONTEXT_FIELDS,
    FactoryInput,
    FactoryOutput,
    FactoryState,
    RuntimeContext,
    RuntimeContextViolation,
    StateInventoryError,
    reducer_for,
    validate_state_inventory,
)

try:  # pragma: no cover - environment probe, not behavior
    from langgraph.errors import EmptyChannelError
    from langgraph.graph import END, START, StateGraph
except ModuleNotFoundError:  # pragma: no cover
    LANGGRAPH_IMPORT_ERROR: str | None = (
        "plan26 hash-locked environment not installed "
        "(python3 -m pip install --require-hashes -r requirements/plan26.lock)"
    )
else:
    LANGGRAPH_IMPORT_ERROR = None

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = REPO_ROOT / "plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md"
# Frozen by N00 in contracts/baseline.v1.md; pins the table this test parses.
SPEC_DIGEST = "44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6"

# The spec stays frozen at the digest above; contracts/erratum_checkpoint_ns_rename.v1.md
# renames this one channel because LangGraph reserves `checkpoint_ns`.
SPEC_FIELD_ERRATA = {"checkpoint_ns": "checkpoint_namespace"}

# Reducer class per field, transcribed from spec section 5.2's "Class/reducer"
# column. Where the spec says "write-once per <key>" over a keyed map, the
# implementing class is `union_disjoint`, whose semantics are exactly
# write-once-per-key with conflict failure.
EXPECTED_REDUCER_CLASSES = {
    "invocation": "replace_current",
    "validated_recovery_envelope": "replace_current",
    "bootstrap_kind": "write_once",
    "contract_version": "write_once",
    "run_id": "write_once",
    "created_at": "write_once",
    "engine_root": "write_once",
    "curriculum_root": "write_once",
    "active_manifest_path": "write_once",
    "output_root": "write_once",
    "mode": "write_once",
    "requested_unit_id": "write_once",
    "frozen_inputs": "write_once",
    "frozen_digest": "write_once",
    "frozen_executable_identities": "write_once",
    "external_authorizations": "write_once",
    "effective_run": "write_once",
    "episode_id": "write_once",
    "checkpoint_thread_id": "write_once",
    "checkpoint_namespace": "write_once",
    "resume_from": "write_once",
    "resume_frontier": "replace_current",
    "cursor": "monotonic_max",
    "selected_unit_id": "replace_current",
    "unit_status": "monotonic_status",
    "source_requests": "append_unique",
    "source_denominators": "union_disjoint",
    "source_discoveries": "union_disjoint",
    "retrievals": "union_disjoint",
    "source_interpretations": "union_disjoint",
    "source_admissions": "append_unique",
    "source_join_evidence": "append_unique",
    "artifact_versions": "append_unique",
    "artifact_heads": "advance_head",
    "deterministic_checks": "append_unique",
    "visual_briefs": "append_unique",
    "visual_denominators": "union_disjoint",
    "visual_results": "union_disjoint",
    "visual_join_evidence": "append_unique",
    "unit_page_inventories": "append_unique",
    "unit_page_inspections": "append_unique",
    "review_packets": "append_unique",
    "unit_reviews": "append_unique",
    "finding_partitions": "append_unique",
    "repair_requests": "append_unique",
    "invalidations": "append_unique",
    "retest_plans": "append_unique",
    "retest_results": "append_unique",
    "attempt_counters": "monotonic_max",
    "failure_fingerprints": "append_unique",
    "accepted_unit_receipts": "accept_once",
    "accepted_unit_checkpoint_receipts": "append_unique",
    "workbook_versions": "append_unique",
    "workbook_head": "advance_head",
    "workbook_coverage": "append_unique",
    "workbook_page_inventories": "append_unique",
    "workbook_page_inspections": "append_unique",
    "workbook_review_packets": "append_unique",
    "workbook_reviews": "append_unique",
    "workbook_finding_partitions": "append_unique",
    "workbook_repair_requests": "append_unique",
    "workbook_invalidations": "append_unique",
    "workbook_retests": "append_unique",
    "final_release_audits": "append_unique",
    "route_decisions": "append_unique",
    "model_execution_receipts": "append_unique",
    "activation_receipts": "append_unique",
    "capability_receipts": "append_unique",
    "evidence_index_entries": "append_unique",
    "log_audit_receipts": "append_unique",
    "checkpoint_metadata": "append_unique",
    "pending_failure": "replace_current",
    "pending_packet": "replace_current",
    "pending_guard": "replace_current",
    "terminal_candidate": "replace_current",
    "terminal": "write_episode_terminal_once",
    "terminal_history": "append_unique",
}


def spec_section_5_2_fields() -> tuple[str, ...]:
    text = SPEC_PATH.read_text(encoding="utf-8")
    start = text.index("### 5.2 Complete persisted state")
    end = text.index("Derived, not persisted", start)
    fields: list[str] = []
    for line in text[start:end].splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| Field"):
            continue
        first_cell = line.split("|")[1]
        fields.extend(
            SPEC_FIELD_ERRATA.get(name, name)
            for name in re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", first_cell)
        )
    return tuple(fields)


def head(version: int, parent: str | None, digest: str) -> dict[str, object]:
    return {"version": version, "parent_hash": parent, "hash": digest}


class StateInventoryTests(unittest.TestCase):
    def test_spec_file_matches_frozen_baseline_digest(self):
        digest = hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest()
        self.assertEqual(digest, SPEC_DIGEST)

    def test_state_inventory_equals_spec_table_exactly(self):
        self.assertEqual(FACTORY_STATE_FIELDS, spec_section_5_2_fields())
        self.assertEqual(len(FACTORY_STATE_FIELDS), 77)

    def test_inventory_rejects_missing_and_unknown_fields(self):
        complete = {field: None for field in FACTORY_STATE_FIELDS}
        validate_state_inventory(complete)

        missing = dict(complete)
        missing.pop("terminal")
        with self.assertRaises(StateInventoryError) as ctx:
            validate_state_inventory(missing)
        self.assertIn("terminal", str(ctx.exception))

        unknown = dict(complete)
        unknown["execution_evidence"] = None
        with self.assertRaises(StateInventoryError) as ctx:
            validate_state_inventory(unknown)
        self.assertIn("execution_evidence", str(ctx.exception))

    def test_every_field_declares_exactly_one_reducer(self):
        self.assertEqual(tuple(FIELD_REDUCERS), FACTORY_STATE_FIELDS)
        for field, reducer in FIELD_REDUCERS.items():
            with self.subTest(field=field):
                self.assertTrue(callable(reducer))
                self.assertIn(reducer.reducer_class, R.REDUCER_CLASSES)

    def test_field_reducer_classes_match_spec_authority(self):
        self.assertEqual(FIELD_REDUCER_CLASSES, EXPECTED_REDUCER_CLASSES)

    def test_declared_correlation_key_for_deterministic_checks(self):
        reducer = reducer_for("deterministic_checks")
        self.assertEqual(
            reducer.correlation_key_fields,
            ("scope", "owner", "head_hash", "check_id", "attempt"),
        )

    def test_reducer_for_rejects_unknown_field(self):
        with self.assertRaises(StateInventoryError):
            reducer_for("execution_evidence")

    def test_output_schema_is_a_projection_of_persisted_state(self):
        self.assertTrue(set(FACTORY_OUTPUT_FIELDS) <= set(FACTORY_STATE_FIELDS))
        for required in ("contract_version", "run_id", "episode_id", "terminal", "mode",
                         "requested_unit_id", "output_root"):
            self.assertIn(required, FACTORY_OUTPUT_FIELDS)

    def test_input_schema_is_the_invocation_envelope(self):
        self.assertEqual(FACTORY_INPUT_FIELDS, ("invocation",))
        self.assertTrue(set(FACTORY_INPUT_FIELDS) <= set(FACTORY_STATE_FIELDS))

    def test_schemas_are_typed_dicts(self):
        for schema in (FactoryInput, FactoryState, FactoryOutput):
            self.assertTrue(hasattr(schema, "__annotations__"))
            self.assertTrue(hasattr(schema, "__total__"))


class WriteOnceTests(unittest.TestCase):
    def test_absent_to_value(self):
        self.assertEqual(R.write_once(None, "v1"), "v1")

    def test_equal_replay_is_idempotent(self):
        self.assertEqual(R.write_once("v1", "v1"), "v1")
        record = {"b": 1, "a": [1, 2]}
        self.assertEqual(R.write_once(record, {"a": [1, 2], "b": 1}), record)

    def test_differing_replay_fails(self):
        with self.assertRaises(R.WriteOnceConflict):
            R.write_once("v1", "v2")

    def test_null_update_is_a_noop_not_a_conflict(self):
        self.assertEqual(R.write_once("v1", None), "v1")
        self.assertIsNone(R.write_once(None, None))

    def test_non_json_value_fails_closed(self):
        with self.assertRaises(R.NonSerializableValue):
            R.write_once(None, Path("/tmp"))
        with self.assertRaises(R.NonSerializableValue):
            R.write_once(None, {"x": float("nan")})


WRITE_ONCE_FIELDS: tuple[str, ...] = tuple(
    field for field, cls in FIELD_REDUCER_CLASSES.items() if cls == "write_once"
)

FIRST_WRITE = {
    "bootstrap_kind": "fresh",
    "contract_version": "v1",
    "run_id": "run-1",
    "created_at": "2026-08-11T00:00:00Z",
    "engine_root": "/engine",
    "curriculum_root": "/curriculum",
    "active_manifest_path": "/curriculum/manifest.yaml",
    "output_root": "/out/run-1",
    "mode": "one",
    "requested_unit_id": "u1",
    "frozen_inputs": [{"key": "manifest", "sha256": "a" * 64}],
    "frozen_digest": "b" * 64,
    "frozen_executable_identities": [{"key": "typst", "sha256": "c" * 64}],
    "external_authorizations": [{"key": "egress", "granted": True}],
    "effective_run": {"ordered_unit_ids": ["u1"]},
    "episode_id": "ep-1",
    "checkpoint_thread_id": "run-1",
    "checkpoint_namespace": "",
    "resume_from": {"node": "D02"},
}


@unittest.skipIf(LANGGRAPH_IMPORT_ERROR is not None, LANGGRAPH_IMPORT_ERROR or "")
class WriteOnceThroughARealGraphTests(unittest.TestCase):
    """B-1: `write_once` must survive a real `StateGraph`, not just a direct call.

    LangGraph seeds a reduced channel by calling its annotated type when that type
    is zero-arg constructible, so a channel declared `Annotated[str, write_once]`
    starts at `''` and `write_once` rejects the channel's own first write. Only a
    real compiled invoke observes this.
    """

    def test_the_write_once_inventory_is_the_nineteen_declared_channels(self):
        self.assertEqual(len(WRITE_ONCE_FIELDS), 19)
        self.assertEqual(set(FIRST_WRITE), set(WRITE_ONCE_FIELDS))

    def test_no_write_once_channel_is_seeded_with_a_constructed_default(self):
        builder: StateGraph = StateGraph(FactoryState)
        for field in WRITE_ONCE_FIELDS:
            with self.subTest(field=field):
                with self.assertRaises(EmptyChannelError):
                    builder.channels[field].get()

    def _graph(self, *nodes):
        builder: StateGraph = StateGraph(FactoryState)
        previous = START
        for index, body in enumerate(nodes):
            name = f"n{index}"
            builder.add_node(name, body)
            builder.add_edge(previous, name)
            previous = name
        builder.add_edge(previous, END)
        return builder.compile()

    def test_every_write_once_channel_accepts_its_own_first_write(self):
        graph = self._graph(lambda state: dict(FIRST_WRITE))
        result = graph.invoke({"invocation": {"mode": "one"}})
        for field, expected in FIRST_WRITE.items():
            with self.subTest(field=field):
                self.assertEqual(result[field], expected)

    def test_an_equal_second_write_replays_and_a_differing_one_still_conflicts(self):
        replay = self._graph(lambda state: dict(FIRST_WRITE), lambda state: dict(FIRST_WRITE))
        self.assertEqual(replay.invoke({})["run_id"], "run-1")

        conflict = self._graph(
            lambda state: dict(FIRST_WRITE),
            lambda state: {"run_id": "run-2"},
        )
        with self.assertRaises(R.WriteOnceConflict):
            conflict.invoke({})

    def test_an_intentional_empty_write_is_a_recorded_value_not_an_unset_channel(self):
        empty = {"frozen_inputs": [], "external_authorizations": [], "effective_run": {},
                 "checkpoint_namespace": ""}
        result = self._graph(lambda state: dict(empty)).invoke({})
        for field, expected in empty.items():
            with self.subTest(field=field):
                self.assertEqual(result[field], expected)

        conflict = self._graph(lambda state: dict(empty), lambda state: {"frozen_inputs": [{"key": "m"}]})
        with self.assertRaises(R.WriteOnceConflict):
            conflict.invoke({})


class AppendUniqueTests(unittest.TestCase):
    def test_appends_and_replays_idempotently(self):
        first = R.append_unique(None, {"key": "a", "v": 1})
        again = R.append_unique(first, {"key": "a", "v": 1})
        self.assertEqual(again, [{"key": "a", "v": 1}])
        grown = R.append_unique(again, [{"key": "b", "v": 2}, {"key": "c", "v": 3}])
        self.assertEqual([r["key"] for r in grown], ["a", "b", "c"])

    def test_duplicate_key_with_differing_content_fails(self):
        existing = R.append_unique(None, {"key": "a", "v": 1})
        with self.assertRaises(R.DuplicateConflict):
            R.append_unique(existing, {"key": "a", "v": 2})

    def test_missing_correlation_field_fails(self):
        with self.assertRaises(R.CorrelationKeyError):
            R.append_unique(None, {"v": 1})

    def test_declared_tuple_correlation_key(self):
        reducer = R.append_unique_by("scope", "owner", "head_hash", "check_id", "attempt")
        base = {"scope": "unit", "owner": "D08", "head_hash": "h1", "check_id": "c1", "attempt": 1}
        state = reducer(None, dict(base, result="PASS"))
        self.assertEqual(reducer(state, dict(base, result="PASS")), state)
        with self.assertRaises(R.DuplicateConflict):
            reducer(state, dict(base, result="FAIL"))
        # A new attempt is a different correlation key, so it appends.
        self.assertEqual(len(reducer(state, dict(base, attempt=2, result="FAIL"))), 2)

    def test_reducer_does_not_mutate_its_input(self):
        existing = [{"key": "a"}]
        R.append_unique(existing, {"key": "b"})
        self.assertEqual(existing, [{"key": "a"}])

    def test_append_unique_by_requires_a_key(self):
        with self.assertRaises(R.CorrelationKeyError):
            R.append_unique_by()


class UnionDisjointTests(unittest.TestCase):
    UPDATES = (
        {"w1": {"status": "OK", "hash": "h1"}},
        {"w2": {"status": "OK", "hash": "h2"}},
        {"w3": {"status": "FAILED", "hash": "h3"}},
        {"w4": {"status": "OK", "hash": "h4"}},
    )

    def _fold(self, updates):
        return functools.reduce(R.union_disjoint, updates, None)

    def test_commutative_and_associative_under_completion_permutations(self):
        expected = self._fold(self.UPDATES)
        self.assertEqual(len(expected), 4)
        for order in itertools.permutations(self.UPDATES):
            with self.subTest(order=[next(iter(u)) for u in order]):
                self.assertEqual(self._fold(order), expected)
        for split in range(len(self.UPDATES) + 1):
            left = self._fold(self.UPDATES[:split])
            right = self._fold(self.UPDATES[split:])
            self.assertEqual(R.union_disjoint(left, right), expected)

    def test_equal_replay_is_idempotent_in_any_order(self):
        merged = self._fold(self.UPDATES)
        for order in itertools.permutations(self.UPDATES):
            self.assertEqual(functools.reduce(R.union_disjoint, order, merged), merged)

    def test_key_conflict_fails_in_every_order(self):
        conflicting = self.UPDATES + ({"w2": {"status": "FAILED", "hash": "hX"}},)
        for order in itertools.permutations(conflicting):
            with self.assertRaises(R.UnionConflict):
                self._fold(order)

    def test_non_mapping_update_fails(self):
        with self.assertRaises(R.UnionConflict):
            R.union_disjoint(None, [{"w1": 1}])


class AdvanceHeadTests(unittest.TestCase):
    def test_genesis_must_be_version_one_with_null_parent(self):
        heads = R.advance_head(None, {"domain": head(1, None, "h1")})
        self.assertEqual(heads["domain"]["version"], 1)
        with self.assertRaises(R.HeadAdvanceError):
            R.advance_head(None, {"domain": head(2, None, "h2")})
        with self.assertRaises(R.HeadAdvanceError):
            R.advance_head(None, {"domain": head(1, "h0", "h1")})

    def test_child_requires_parent_match_and_version_plus_one(self):
        heads = R.advance_head(None, {"domain": head(1, None, "h1")})
        advanced = R.advance_head(heads, {"domain": head(2, "h1", "h2")})
        self.assertEqual(advanced["domain"], head(2, "h1", "h2"))
        with self.assertRaises(R.HeadAdvanceError):
            R.advance_head(advanced, {"domain": head(4, "h2", "h4")})  # version skip
        with self.assertRaises(R.HeadAdvanceError):
            R.advance_head(advanced, {"domain": head(3, "h1", "h3")})  # wrong parent

    def test_equal_replay_is_idempotent_and_regression_fails(self):
        heads = R.advance_head(None, {"domain": head(1, None, "h1")})
        self.assertEqual(R.advance_head(heads, {"domain": head(1, None, "h1")}), heads)
        advanced = R.advance_head(heads, {"domain": head(2, "h1", "h2")})
        with self.assertRaises(R.HeadAdvanceError):
            R.advance_head(advanced, {"domain": head(1, None, "h1")})

    def test_independent_heads_advance_independently(self):
        heads = R.advance_head(None, {"domain": head(1, None, "d1"), "content": head(1, None, "c1")})
        heads = R.advance_head(heads, {"content": head(2, "c1", "c2")})
        self.assertEqual(heads["domain"]["version"], 1)
        self.assertEqual(heads["content"]["version"], 2)

    def test_malformed_head_record_fails(self):
        with self.assertRaises(R.HeadAdvanceError):
            R.advance_head(None, {"domain": {"version": 1, "hash": "h1"}})
        with self.assertRaises(R.HeadAdvanceError):
            R.advance_head(None, {"domain": head(0, None, "h1")})
        with self.assertRaises(R.HeadAdvanceError):
            R.advance_head(None, {"domain": head(1, None, "")})


class ReplaceCurrentTests(unittest.TestCase):
    def test_sets_replaces_and_clears(self):
        self.assertEqual(R.replace_current(None, {"a": 1}), {"a": 1})
        self.assertEqual(R.replace_current({"a": 1}, {"a": 1}), {"a": 1})
        self.assertEqual(R.replace_current({"a": 1}, {"b": 2}), {"b": 2})
        self.assertIsNone(R.replace_current({"a": 1}, None))

    def test_non_json_value_fails_closed(self):
        with self.assertRaises(R.ReplaceCurrentError):
            R.replace_current(None, {"clock": object()})


class MonotonicStatusTests(unittest.TestCase):
    def test_declared_forward_transitions(self):
        status = R.monotonic_status(None, {"u1": "PENDING"})
        for nxt in ("SELECTED", "SOURCING", "BUILDING", "REVIEWING", "ACCEPTED"):
            status = R.monotonic_status(status, {"u1": nxt})
        self.assertEqual(status["u1"], "ACCEPTED")

    def test_equal_replay_is_idempotent(self):
        status = R.monotonic_status(None, {"u1": "PENDING"})
        self.assertEqual(R.monotonic_status(status, {"u1": "PENDING"}), status)

    def test_regression_and_undeclared_transitions_fail(self):
        status = R.monotonic_status(None, {"u1": "PENDING"})
        status = R.monotonic_status(status, {"u1": "SELECTED"})
        with self.assertRaises(R.StatusTransitionError):
            R.monotonic_status(status, {"u1": "PENDING"})
        with self.assertRaises(R.StatusTransitionError):
            R.monotonic_status(status, {"u1": "ACCEPTED"})

    def test_acceptance_is_terminal(self):
        status = {"u1": "ACCEPTED"}
        self.assertEqual(R.monotonic_status(status, {"u1": "ACCEPTED"}), status)
        for regress in ("REVIEWING", "REPAIRING", "PENDING", "BLOCKED"):
            with self.subTest(regress=regress):
                with self.assertRaises(R.StatusTransitionError):
                    R.monotonic_status(status, {"u1": regress})

    def test_repair_cycle_is_declared_and_bounded(self):
        status = {"u1": "REVIEWING"}
        status = R.monotonic_status(status, {"u1": "REPAIRING"})
        status = R.monotonic_status(status, {"u1": "REVIEWING"})
        self.assertEqual(status["u1"], "REVIEWING")
        with self.assertRaises(R.StatusTransitionError):
            R.monotonic_status(status, {"u1": "SOURCING"})

    def test_unknown_status_and_illegal_first_status_fail(self):
        with self.assertRaises(R.StatusTransitionError):
            R.monotonic_status(None, {"u1": "DONE"})
        with self.assertRaises(R.StatusTransitionError):
            R.monotonic_status(None, {"u1": "ACCEPTED"})

    def test_units_are_independent(self):
        status = R.monotonic_status(None, {"u1": "PENDING", "u2": "PENDING"})
        status = R.monotonic_status(status, {"u1": "SELECTED"})
        self.assertEqual(status, {"u1": "SELECTED", "u2": "PENDING"})


class MonotonicMaxTests(unittest.TestCase):
    def test_counters_increase_and_replay_equal(self):
        counters = R.monotonic_max(None, {"u1:M03": 1})
        self.assertEqual(R.monotonic_max(counters, {"u1:M03": 1}), counters)
        self.assertEqual(R.monotonic_max(counters, {"u1:M03": 2})["u1:M03"], 2)

    def test_counters_cannot_regress(self):
        counters = R.monotonic_max(None, {"u1:M03": 3})
        with self.assertRaises(R.CounterRegression):
            R.monotonic_max(counters, {"u1:M03": 2})

    def test_non_counter_values_fail(self):
        for bad in (-1, "2", 1.0, True):
            with self.subTest(bad=bad):
                with self.assertRaises(R.CounterRegression):
                    R.monotonic_max(None, {"u1:M03": bad})

    def test_cursor_shape(self):
        cursor = R.monotonic_max(None, {"manifest_ordinal": 0, "accepted_ordinal": 0})
        cursor = R.monotonic_max(cursor, {"manifest_ordinal": 1})
        self.assertEqual(cursor, {"manifest_ordinal": 1, "accepted_ordinal": 0})
        with self.assertRaises(R.CounterRegression):
            R.monotonic_max(cursor, {"manifest_ordinal": 0})


class AcceptOnceTests(unittest.TestCase):
    def test_accepts_once_and_replays_equal(self):
        receipt = {"unit_id": "u1", "pdf_hash": "p1"}
        state = R.accept_once(None, {"u1": receipt})
        self.assertEqual(R.accept_once(state, {"u1": dict(receipt)}), state)

    def test_differing_rewrite_fails(self):
        state = R.accept_once(None, {"u1": {"unit_id": "u1", "pdf_hash": "p1"}})
        with self.assertRaises(R.AcceptOnceConflict):
            R.accept_once(state, {"u1": {"unit_id": "u1", "pdf_hash": "p2"}})

    def test_other_units_accept_independently(self):
        state = R.accept_once(None, {"u1": {"pdf_hash": "p1"}})
        state = R.accept_once(state, {"u2": {"pdf_hash": "p2"}})
        self.assertEqual(sorted(state), ["u1", "u2"])


class EpisodeTerminalTests(unittest.TestCase):
    def test_exactly_one_terminal_per_episode(self):
        terminal = {"kind": "COMPLETE", "exit_code": 0}
        state = R.write_episode_terminal_once(None, terminal)
        self.assertEqual(R.write_episode_terminal_once(state, dict(terminal)), state)
        with self.assertRaises(R.TerminalConflict):
            R.write_episode_terminal_once(state, {"kind": "SYSTEM_FAILURE", "exit_code": 20})

    def test_unknown_terminal_kind_fails(self):
        with self.assertRaises(R.TerminalConflict):
            R.write_episode_terminal_once(None, {"kind": "ACCEPTED_PENDING_REVIEW"})
        with self.assertRaises(R.TerminalConflict):
            R.write_episode_terminal_once(None, {"exit_code": 0})

    def test_six_declared_terminal_kinds(self):
        self.assertEqual(
            set(R.TERMINAL_KINDS),
            {"UNIT_ACCEPTED", "COMPLETE", "INTERRUPTED", "PAUSED_PREREQUISITE",
             "CONVERGENCE_EXHAUSTED", "SYSTEM_FAILURE"},
        )


class FailClosedContractTests(unittest.TestCase):
    def test_every_reducer_is_registered_and_typed(self):
        self.assertEqual(len(R.REDUCERS), 9)
        for name, reducer in R.REDUCERS.items():
            with self.subTest(reducer=name):
                self.assertEqual(reducer.reducer_class, name)

    def test_conflicting_replay_raises_a_typed_reducer_error(self):
        cases = [
            (R.write_once, "a", "b"),
            (R.append_unique, [{"key": "a", "v": 1}], {"key": "a", "v": 2}),
            (R.union_disjoint, {"a": 1}, {"a": 2}),
            (R.advance_head, {"d": head(1, None, "h1")}, {"d": head(3, "h1", "h3")}),
            (R.monotonic_status, {"u": "ACCEPTED"}, {"u": "PENDING"}),
            (R.monotonic_max, {"c": 2}, {"c": 1}),
            (R.accept_once, {"u": {"h": 1}}, {"u": {"h": 2}}),
            (R.write_episode_terminal_once, {"kind": "COMPLETE"}, {"kind": "INTERRUPTED"}),
        ]
        for reducer, existing, new in cases:
            with self.subTest(reducer=reducer.reducer_class):
                with self.assertRaises(R.ReducerError):
                    reducer(existing, new)

    def test_equal_replay_is_idempotent_for_every_reducer(self):
        cases = [
            (R.write_once, "a", "a", "a"),
            (R.append_unique, [{"key": "a"}], {"key": "a"}, [{"key": "a"}]),
            (R.union_disjoint, {"a": 1}, {"a": 1}, {"a": 1}),
            (R.advance_head, {"d": head(1, None, "h1")}, {"d": head(1, None, "h1")},
             {"d": head(1, None, "h1")}),
            (R.replace_current, {"p": 1}, {"p": 1}, {"p": 1}),
            (R.monotonic_status, {"u": "SELECTED"}, {"u": "SELECTED"}, {"u": "SELECTED"}),
            (R.monotonic_max, {"c": 2}, {"c": 2}, {"c": 2}),
            (R.accept_once, {"u": {"h": 1}}, {"u": {"h": 1}}, {"u": {"h": 1}}),
            (R.write_episode_terminal_once, {"kind": "COMPLETE"}, {"kind": "COMPLETE"},
             {"kind": "COMPLETE"}),
        ]
        for reducer, existing, new, expected in cases:
            with self.subTest(reducer=reducer.reducer_class):
                self.assertEqual(reducer(existing, new), expected)

    def test_canonical_json_is_the_one_serialization(self):
        self.assertEqual(R.canonical_json({"b": 1, "a": 2}), '{"a":2,"b":1}')
        self.assertEqual(
            R.canonical_digest({"a": 1}),
            hashlib.sha256(b'{"a":1}').hexdigest(),
        )
        with self.assertRaises(R.NonSerializableValue):
            R.canonical_json(float("inf"))

    def test_no_langgraph_import_in_state_or_reducers(self):
        for module in ("state.py", "reducers.py"):
            source = (REPO_ROOT / "src/curriculum_factory/langgraph_factory" / module).read_text(encoding="utf-8")
            self.assertNotIn("langgraph", source.replace("langgraph_factory", ""))


class RuntimeContextTests(unittest.TestCase):
    def build(self, **overrides) -> RuntimeContext:
        kwargs = {
            "engine_root": REPO_ROOT,
            "output_root": REPO_ROOT / "out",
            "path_guard": object(),
            "evidence_service": object(),
            "transport_registry": object(),
            "source_retriever": object(),
            "signal_token": object(),
            "clock": lambda: "2026-08-11T00:00:00Z",
        }
        kwargs.update(overrides)
        return RuntimeContext(**kwargs)

    def test_holds_only_the_declared_services(self):
        self.assertEqual(
            RUNTIME_CONTEXT_FIELDS,
            ("engine_root", "output_root", "path_guard", "evidence_service",
             "transport_registry", "source_retriever", "signal_token", "clock"),
        )

    def test_holds_no_model_client_or_routing_authority(self):
        context = self.build()
        for forbidden in FORBIDDEN_RUNTIME_CONTEXT_FIELDS:
            with self.subTest(attribute=forbidden):
                self.assertFalse(hasattr(context, forbidden))
        self.assertTrue(FORBIDDEN_RUNTIME_CONTEXT_FIELDS.isdisjoint(RUNTIME_CONTEXT_FIELDS))

    def test_subclass_injecting_a_model_client_is_rejected(self):
        @dataclasses.dataclass(frozen=True, slots=True)
        class LeakyContext(RuntimeContext):
            model_client: object = None

        with self.assertRaises(RuntimeContextViolation):
            LeakyContext(
                engine_root=REPO_ROOT,
                output_root=REPO_ROOT / "out",
                path_guard=object(),
                evidence_service=object(),
                transport_registry=object(),
                source_retriever=object(),
                signal_token=object(),
                clock=lambda: None,
                model_client=object(),
            )

    def test_is_not_json_or_checkpoint_serializable(self):
        context = self.build()
        with self.assertRaises(TypeError):
            json.dumps(context)
        with self.assertRaises(TypeError):
            json.dumps(dataclasses.asdict(context))
        with self.assertRaises(R.ReplaceCurrentError):
            R.replace_current(None, {"context": context})
        with self.assertRaises(R.NonSerializableValue):
            R.canonical_json({"context": context})

    def test_is_structurally_excluded_from_persisted_state(self):
        for field in RUNTIME_CONTEXT_FIELDS:
            if field in ("engine_root", "output_root"):
                continue  # persisted as canonical path strings, not as services
            self.assertNotIn(field, FACTORY_STATE_FIELDS)
        for name in ("runtime_context", "context", "services"):
            self.assertNotIn(name, FACTORY_STATE_FIELDS)

    def test_is_frozen(self):
        context = self.build()
        with self.assertRaises(dataclasses.FrozenInstanceError):
            context.output_root = REPO_ROOT  # type: ignore[misc]

    def test_rejects_string_roots_and_missing_services(self):
        with self.assertRaises(RuntimeContextViolation):
            self.build(engine_root=str(REPO_ROOT))
        with self.assertRaises(RuntimeContextViolation):
            self.build(transport_registry=None)
        with self.assertRaises(RuntimeContextViolation):
            self.build(clock="2026-08-11")


if __name__ == "__main__":
    unittest.main()
