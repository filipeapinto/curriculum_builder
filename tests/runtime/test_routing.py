from __future__ import annotations

from pathlib import Path
import unittest

from curriculum_factory.routing import RoutingError, Selector


ENGINE = Path(__file__).resolve().parents[2]


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.selector = Selector(ENGINE)

    def test_decision_is_valid_and_equal(self):
        decision = self.selector.select("write-child", "child_explanatory_writing")
        self.selector.validate_decision(decision)
        self.assertEqual(decision["decided_model"], decision["executed_model"])

    def test_bypass_refused(self):
        with self.assertRaises(RoutingError):
            self.selector.select("write-child", "child_explanatory_writing",
                                 fallback_model="gpt-5.6-terra")

    def test_executed_mismatch_refused(self):
        with self.assertRaises(RoutingError):
            self.selector.select("write-child", "child_explanatory_writing",
                                 executed_model="gpt-5.6-terra")

    def test_deterministic_model_work_refused(self):
        for task in ("merge", "validation", "hashing", "rendering", "aggregation", "audit", "logging"):
            with self.subTest(task=task), self.assertRaises(RoutingError):
                self.selector.select("deterministic", task)

    def test_unknown_task_refused(self):
        with self.assertRaises(RoutingError):
            self.selector.select("unknown", "not-declared")

    def test_max_effort_final_acceptance(self):
        decision = self.selector.select("accept", "final_acceptance")
        self.assertEqual(decision["reasoning_effort"], "max")


if __name__ == "__main__":
    unittest.main()
