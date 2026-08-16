from __future__ import annotations

import json
from pathlib import Path
import tempfile
import threading
import unittest

import jsonschema

from curriculum_factory.logger import ExecutionLogger, LogError


ENGINE = Path(__file__).resolve().parents[2]
SCHEMA = ENGINE / "schemas/execution_log.schema.v2.json"


class LoggerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.logger = ExecutionLogger(self.root, SCHEMA)

    def tearDown(self):
        self.temp.cleanup()

    def test_append_monotonic_pair_and_schema(self):
        start = self.logger.start(action="Validate deterministic logger operation", action_kind="test",
                                  authorized_paths=[str(self.root)], trigger="unit test trigger",
                                  expected="paired schema-valid records")
        end = self.logger.complete(start, result="operation completed successfully")
        self.assertEqual((start, end), ("ACT-001", "ACT-002"))
        audit = self.logger.audit()
        self.assertTrue(audit["monotonic"])
        self.assertEqual(audit["unclosed_starts"], [])
        schema = json.loads(SCHEMA.read_text())
        jsonschema.Draft202012Validator(schema).validate(
            {"log_version": "2.0", "records": self.logger.records(), "unclosed_starts": []}
        )

    def test_append_only_bytes_preserved(self):
        first = self.logger.start(action="Record immutable first logger operation", action_kind="test",
                                  authorized_paths=[str(self.root)], trigger="append only test",
                                  expected="first bytes remain unchanged")
        before = self.logger.path.read_bytes()
        self.logger.complete(first, result="first record closed without rewrite")
        self.assertTrue(self.logger.path.read_bytes().startswith(before))

    def test_orphan_completion_refused(self):
        with self.assertRaises(LogError):
            self.logger.complete("ACT-999", result="must never be written")

    def test_duplicate_close_refused(self):
        start = self.logger.start(action="Open exactly one closeable operation", action_kind="test",
                                  authorized_paths=[str(self.root)], trigger="duplicate close test",
                                  expected="one close only")
        self.logger.complete(start, result="closed once as required")
        with self.assertRaises(LogError):
            self.logger.fail(start, failure_type="tool-error", what_failed="duplicate close was attempted",
                             expected="duplicate close refused")

    def test_model_call_without_decision_refused(self):
        with self.assertRaises(LogError):
            self.logger.start(action="Invoke bounded curriculum model worker", action_kind="model_call",
                              authorized_paths=[str(self.root)], trigger="model call test",
                              expected="valid structured worker output")

    def test_failure_explicitly_closes_start(self):
        start = self.logger.start(action="Execute operation that fails deterministically", action_kind="command",
                                  authorized_paths=[str(self.root)], trigger="failure pairing test",
                                  expected="explicit failure close")
        failure = self.logger.fail(start, failure_type="tool-error",
                                   what_failed="simulated command returned nonzero",
                                   expected="successful command result")
        self.assertEqual(failure, "EXEC-002")
        self.assertEqual(self.logger.audit()["failures"], 1)

    def test_concurrent_append_safe(self):
        def worker(index: int):
            start = self.logger.start(action=f"Concurrent append test operation {index}", action_kind="test",
                                      authorized_paths=[str(self.root)], trigger="thread safety test",
                                      expected="unique monotonic pair")
            self.logger.complete(start, result=f"thread operation {index} completed")
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(12)]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        audit = self.logger.audit()
        self.assertEqual(audit["records"], 24)
        self.assertTrue(audit["monotonic"])
        self.assertFalse(audit["unclosed_starts"])

    def test_negative_fixture_schema_rejects_untyped_action(self):
        schema = json.loads(SCHEMA.read_text())
        bad = {"log_version": "2.0", "records": [{"id": "ACT-001"}]}
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schema).validate(bad)


if __name__ == "__main__":
    unittest.main()
