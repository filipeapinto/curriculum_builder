from __future__ import annotations

from pathlib import Path
import unittest

import yaml

from runtime.capabilities import (CapabilityError, remove_unavailable_route,
                                  route_required_by_unit, validate_cross_family_proof)
from runtime.gemini import max_effort_settings, resolve_alias


ENGINE = Path(__file__).resolve().parents[2]


class CapabilityTests(unittest.TestCase):
    def setUp(self):
        self.routes = yaml.safe_load((ENGINE / "policy/routes.v1.yaml").read_text())
        self.unit = yaml.safe_load((ENGINE / "curricula/arduino_kit/arduino_kit_curriculum.v5.yaml").read_text())["labs"][0]

    def test_unavailable_unused_route_removal_rule(self):
        self.assertFalse(route_required_by_unit("imagegen", self.unit, forbidden_routes={"imagegen"}))
        changed = remove_unavailable_route(self.routes, "imagegen", required=False)
        self.assertNotIn("imagegen", [route["id"] for route in changed["routes"]])
        self.assertIn("imagegen", [route["id"] for route in self.routes["routes"]])

    def test_required_route_cannot_be_removed(self):
        with self.assertRaises(CapabilityError):
            remove_unavailable_route(self.routes, "imagegen", required=True)

    def test_cross_family_declaration_requires_real_proof(self):
        model = "gemini-explicit-test-model"
        settings = max_effort_settings(model)
        receipt = {"real_call": False, "decided_model": model, "executed_model": model,
                   "policy_effort": "max", "settings_sha256": resolve_alias(settings, model)["settings_sha256"],
                   "events": [{"type": "init", "model": model}]}
        with self.assertRaises(CapabilityError):
            validate_cross_family_proof(receipt, settings)

    def test_valid_proof_binds_model_effort_hash_and_no_tools(self):
        model = "gemini-explicit-test-model"
        settings = max_effort_settings(model)
        receipt = {"real_call": True, "decided_model": model, "executed_model": model,
                   "policy_effort": "max", "settings_sha256": resolve_alias(settings, model)["settings_sha256"],
                   "events": [{"type": "init", "model": model}, {"type": "result"}]}
        self.assertTrue(validate_cross_family_proof(receipt, settings)["proof_valid"])


if __name__ == "__main__":
    unittest.main()
