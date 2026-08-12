from __future__ import annotations

import ast
import json
import unittest
import tempfile
from pathlib import Path
from unittest import mock

from runtime.controller import CurriculumRuntime
import runtime.run_curriculum as run_curriculum_module


ENGINE = Path(__file__).resolve().parents[2]
CURRICULUM = ENGINE / "curricula/arduino_kit"
RUN_CURRICULUM_SOURCE_PATH = ENGINE / "runtime" / "run_curriculum.py"
RUN_CURRICULUM_SOURCE = RUN_CURRICULUM_SOURCE_PATH.read_text(encoding="utf-8")
RUN_CURRICULUM_AST = ast.parse(RUN_CURRICULUM_SOURCE, filename=str(RUN_CURRICULUM_SOURCE_PATH))

LEGACY_CLI_FLAGS = (
    "--lab-id",
    "--max-model-calls-per-lab",
    "--max-concurrency",
    "--max-meta-revision-cycles",
    "--retry-malformed-output",
)

LEGACY_PLAN25_SYMBOLS = (
    "CurriculumFactoryGraph",
    "CodexWorker",
    "GeminiReviewer",
    "CurriculumRuntime",
    "parser_for",
)


class RunCurriculumMigrationContractTests(unittest.TestCase):
    """N40 cutover: `parser_for`/the Plan 25 dispatch surface stay retired."""

    def test_parser_for_is_absent_from_the_module(self):
        self.assertFalse(hasattr(run_curriculum_module, "parser_for"))
        with self.assertRaises(ImportError):
            from runtime.run_curriculum import parser_for  # noqa: F401

    def test_legacy_flags_are_rejected_by_the_current_parser(self):
        for flag in LEGACY_CLI_FLAGS:
            with self.subTest(flag=flag):
                parser = run_curriculum_module.build_parser()
                with self.assertRaises(SystemExit) as raised:
                    parser.parse_args(
                        ["--engine-root", str(ENGINE), "--curriculum", str(CURRICULUM),
                         "--output-root", "/tmp/plan26-legacy-flag-check", "--preflight", flag, "1"]
                    )
                self.assertEqual(raised.exception.code, 2)

    def test_no_plan25_dispatch_symbol_is_imported_or_referenced(self):
        names_in_source = {
            node.id for node in ast.walk(RUN_CURRICULUM_AST) if isinstance(node, ast.Name)
        }
        attributes_in_source = {
            node.attr for node in ast.walk(RUN_CURRICULUM_AST) if isinstance(node, ast.Attribute)
        }
        referenced = names_in_source | attributes_in_source
        for symbol in LEGACY_PLAN25_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, referenced)

        imported_modules = {
            (node.module or "")
            for node in ast.walk(RUN_CURRICULUM_AST)
            if isinstance(node, ast.ImportFrom)
        } | {
            alias.name
            for node in ast.walk(RUN_CURRICULUM_AST)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        forbidden_modules = {
            "runtime.controller",
            "runtime.session_bridge",
            "runtime.curriculum_factory_graph",
            "runtime.model_worker",
        }
        for module in forbidden_modules:
            with self.subTest(module=module):
                self.assertNotIn(module, imported_modules)


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
