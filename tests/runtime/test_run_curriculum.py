from __future__ import annotations

import json
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stdout

from runtime.controller import CurriculumRuntime
from runtime.run_curriculum import main, parser_for


ENGINE = Path(__file__).resolve().parents[2]
CURRICULUM = ENGINE / "curricula/arduino_kit"
REMOVED_FLAGS = (
    "--max-lab-seconds",
    "--phase-timeout-seconds",
    "--max-run-seconds",
)


class RunCurriculumParserTests(unittest.TestCase):
    def setUp(self):
        self.runtime = CurriculumRuntime(ENGINE)

    def test_parser_constructs_without_per_phase(self):
        self.runtime.limit_policy.pop("per_phase", None)
        parser = parser_for(self.runtime)
        self.assertIsNotNone(parser.parse_args(["--curriculum", str(CURRICULUM)]))

    def test_removed_time_flags_are_absent_and_rejected(self):
        parser = parser_for(self.runtime)
        help_text = parser.format_help()
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }
        for flag in REMOVED_FLAGS:
            with self.subTest(flag=flag):
                self.assertNotIn(flag, help_text)
                self.assertNotIn(flag, option_strings)
                with self.assertRaisesRegex(SystemExit, "2"):
                    parser.parse_args(["--curriculum", str(CURRICULUM), flag, "1"])

    def test_representative_retained_policy_defaults(self):
        args = parser_for(self.runtime).parse_args(["--curriculum", str(CURRICULUM)])
        expected = {
            "max_model_calls_per_lab": self.runtime.limit_policy["per_lab"]["max_model_calls"]["value"],
            "max_concurrency": self.runtime.limit_policy["per_run"]["max_concurrency"]["value"],
            "max_meta_revision_cycles": self.runtime.limit_policy["convergence"]["max_meta_revision_cycles"]["value"],
            "retry_malformed_output": self.runtime.limit_policy["retry"]["malformed_structured_output"]["value"],
        }
        for destination, value in expected.items():
            with self.subTest(destination=destination):
                self.assertEqual(getattr(args, destination), value)

    @mock.patch("runtime.run_curriculum.CurriculumFactoryGraph")
    @mock.patch("runtime.run_curriculum.CodexWorker")
    def test_live_cli_dispatches_exact_manifest_to_factory(self, worker, factory):
        factory.return_value.run.return_value = {"terminal": "UNIT_ACCEPTED", "run_id": "r1"}
        output = ENGINE / "outputs/cli-dispatch-not-created"
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = main(["--curriculum", str(CURRICULUM / "arduino_kit_curriculum.v5.yaml"),
                         "--lab-id", "L01", "--output-root", str(output)])
        self.assertEqual(0, code)
        factory.return_value.run.assert_called_once()
        call = factory.return_value.run.call_args.kwargs
        self.assertEqual(str(CURRICULUM / "arduino_kit_curriculum.v5.yaml"), call["curriculum"])
        self.assertEqual("L01", call["lab_id"])
        self.assertFalse(call["all_units"])


class RunCurriculumElapsedTimeTests(unittest.TestCase):
    def setUp(self):
        self.runtime = CurriculumRuntime(ENGINE)
        outputs_root = ENGINE / "outputs"
        outputs_root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=str(outputs_root))
        self.base = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_simulation_accepts_after_all_removed_time_thresholds(self):
        monotonic_times = [0.0, 901.0, 5401.0, 36001.0]
        monotonic_times.extend(36002.0 + index for index in range(len(self.runtime.states) - 3))
        output = self.base / "thresholds"
        with mock.patch("runtime.controller.time.monotonic", side_effect=monotonic_times):
            result = self.runtime.simulate(CURRICULUM, output, lab_id="L01")

        self.assertEqual(result["terminal_state"], "ACCEPTED")
        self.assertEqual(result["coverage"], "simulated-controller-only")
        checkpoints = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((output / "checkpoints").glob("*.json"))
        ]
        elapsed = [record["elapsed_seconds"] for record in checkpoints]
        self.assertTrue(all(isinstance(value, (int, float)) for value in elapsed))
        self.assertGreater(elapsed[0], 900)
        self.assertGreater(elapsed[1], 5400)
        self.assertGreater(elapsed[2], 36000)


if __name__ == "__main__":
    unittest.main()
