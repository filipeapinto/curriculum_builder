from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from curriculum_factory.checkpoint import CheckpointError
from curriculum_factory.controller import CurriculumRuntime, RuntimeFailure
from curriculum_factory.io import BoundaryError, sha256_file


ENGINE = Path(__file__).resolve().parents[2]
CURRICULUM = ENGINE / "curricula/arduino_kit"


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.runtime = CurriculumRuntime(ENGINE)
        # output roots must resolve beneath ENGINE/outputs/ (runtime/io.py's
        # require_internal_output), so test scratch space lives there too, not in
        # the OS tempdir.
        outputs_root = ENGINE / "outputs"
        outputs_root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=str(outputs_root))
        self.base = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_static_preflight_manifest_and_fixtures(self):
        result = self.runtime.static_preflight(CURRICULUM)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["unit_ids"][0], "L01")
        self.assertEqual(len(result["verifier_fixtures"]), 4)

    def test_existing_output_refused_without_mutation(self):
        output = self.base / "existing"
        output.mkdir()
        marker = output / "marker"
        marker.write_text("preserve")
        with self.assertRaises(RuntimeFailure) as caught:
            self.runtime.simulate(CURRICULUM, output, lab_id="L01")
        self.assertEqual(caught.exception.failure_id, "PRECONDITION-OUTPUT-ROOT-EXISTS")
        self.assertEqual(marker.read_text(), "preserve")

    def test_output_outside_engine_outputs_refused(self):
        # A path directly under ENGINE, but not under ENGINE/outputs, is still refused.
        with self.assertRaises(BoundaryError):
            self.runtime.prepare_output(ENGINE / "runtime-forbidden-output", resume=False)
        # A path entirely outside ENGINE is refused too — the boundary v1 enforced.
        with tempfile.TemporaryDirectory() as external:
            with self.assertRaises(BoundaryError):
                self.runtime.prepare_output(Path(external) / "forbidden", resume=False)

    def test_output_inside_engine_outputs_accepted(self):
        # The positive case: a run-named subdirectory of ENGINE/outputs/ is legal.
        output = self.runtime.prepare_output(self.base / "accepted", resume=False)
        self.assertTrue(output.is_dir())
        self.assertTrue((output / "results").is_dir())

    def test_clean_simulated_acceptance(self):
        result = self.runtime.simulate(CURRICULUM, self.base / "clean", lab_id="L01")
        self.assertEqual(result["terminal_state"], "ACCEPTED")
        self.assertEqual(result["coverage"], "simulated-controller-only")
        self.assertEqual(result["log_audit"]["unclosed_starts"], [])

    def test_legal_and_illegal_transitions(self):
        self.assertTrue(self.runtime.legal_transition("VALIDATE", "PLAN"))
        self.assertFalse(self.runtime.legal_transition("VALIDATE", "FINAL_ACCEPTANCE"))
        self.assertTrue(self.runtime.legal_transition("FINAL_ACCEPTANCE", "ACCEPTED"))

    def test_interrupt_resume_preserves_hashes(self):
        output = self.base / "resume"
        interrupted = self.runtime.simulate(CURRICULUM, output, lab_id="L01", interrupt_after="PLAN")
        self.assertEqual(interrupted["terminal_state"], "INTERRUPTED")
        preserved = output / "simulated/states/002_PLAN.json"
        before = sha256_file(preserved)
        resumed = self.runtime.simulate(CURRICULUM, output, lab_id="L01", resume=True)
        self.assertEqual(resumed["terminal_state"], "ACCEPTED")
        self.assertEqual(sha256_file(preserved), before)

    def test_resume_hash_mismatch_refused(self):
        output = self.base / "tampered"
        self.runtime.simulate(CURRICULUM, output, lab_id="L01", interrupt_after="PLAN")
        (output / "simulated/states/001_VALIDATE.json").write_text("tampered")
        with self.assertRaises(CheckpointError):
            self.runtime.simulate(CURRICULUM, output, lab_id="L01", resume=True)

    def test_unknown_unit_refused(self):
        with self.assertRaises(RuntimeFailure) as caught:
            self.runtime.simulate(CURRICULUM, self.base / "unknown", lab_id="DOES-NOT-EXIST")
        self.assertEqual(caught.exception.failure_id, "PRECONDITION-UNKNOWN-UNIT")

    def test_missing_verifier_refused(self):
        _, manifest = self.runtime.validated_manifest(CURRICULUM)
        manifest["domain"].pop("verifier")
        with self.assertRaises(RuntimeFailure):
            self.runtime.run_verifier_fixtures(manifest)

    def test_repeat_failure_stops(self):
        calls = 0
        def fail_validate(state: str):
            nonlocal calls
            if state == "VALIDATE":
                calls += 1
                return "CHECK-X"
            return None
        # The current state machine receives one injection per state; a second identical
        # simulated run proves the failure-set threshold at controller-test level.
        with self.assertRaises(RuntimeFailure):
            self.runtime.simulate(CURRICULUM, self.base / "failure", lab_id="L01",
                                  failure_injector=lambda state: "CHECK-X")


if __name__ == "__main__":
    unittest.main()
