import unittest

from runtime.retry import RetryLimit, RetryTracker


class RetryTests(unittest.TestCase):
    def test_malformed_and_transient_retry_once(self):
        tracker = RetryTracker()
        for kind in ("malformed", "transient"):
            tracker.retry(kind)
            with self.assertRaises(RetryLimit):
                tracker.retry(kind)

    def test_revision_limit(self):
        tracker = RetryTracker(revision_limit=2)
        tracker.revision({"A"})
        tracker.revision(set(), {"A"})
        with self.assertRaises(RetryLimit):
            tracker.revision(set())

    def test_repeat_failure_limit(self):
        tracker = RetryTracker(repeat_threshold=2)
        tracker.revision({"A"}, {"A", "B"})
        tracker.revision({"A"}, {"A"})
        with self.assertRaises(RetryLimit):
            tracker.revision({"A"}, {"A"})


if __name__ == "__main__":
    unittest.main()
