from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from curriculum_factory.gemini import (GeminiSettingsError, audit_stream_events, max_effort_settings,
                            resolve_alias, write_run_local_settings)


class GeminiSettingsTests(unittest.TestCase):
    MODEL = "gemini-explicit-test-model"

    def test_max_mapping_and_alias_resolution(self):
        resolved = resolve_alias(max_effort_settings(self.MODEL), self.MODEL)
        self.assertEqual(resolved["policy_effort"], "max")
        self.assertEqual(resolved["provider_control"], {"thinkingLevel": "HIGH"})
        self.assertTrue(resolved["tools_disabled"])

    def test_missing_thinking_control_refused(self):
        settings = max_effort_settings(self.MODEL)
        del settings["modelConfigs"]["aliases"][self.MODEL]["modelConfig"]["generateContentConfig"]["thinkingConfig"]
        with self.assertRaises(GeminiSettingsError):
            resolve_alias(settings, self.MODEL)

    def test_overridden_thinking_control_refused(self):
        settings = max_effort_settings(self.MODEL)
        settings["modelConfigs"]["aliases"][self.MODEL]["modelConfig"]["generateContentConfig"]["thinkingConfig"] = {"thinkingLevel": "LOW"}
        with self.assertRaises(GeminiSettingsError):
            resolve_alias(settings, self.MODEL)

    def test_underlying_model_mismatch_refused(self):
        settings = max_effort_settings(self.MODEL)
        settings["modelConfigs"]["aliases"][self.MODEL]["modelConfig"]["model"] = "different-model"
        with self.assertRaises(GeminiSettingsError):
            resolve_alias(settings, self.MODEL)

    def test_run_local_write_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path, digest = write_run_local_settings(root, self.MODEL)
            self.assertTrue(path.is_relative_to(root.resolve()))
            self.assertEqual(resolve_alias(json.loads(path.read_text()), self.MODEL)["settings_sha256"], digest)

    def test_stream_model_and_tool_audit(self):
        result = audit_stream_events([{"type": "init", "model": self.MODEL}, {"type": "result"}], self.MODEL)
        self.assertEqual(result, {"init_model": self.MODEL, "tool_use_events": 0})
        with self.assertRaises(GeminiSettingsError):
            audit_stream_events([{"type": "init", "model": "other"}], self.MODEL)
        with self.assertRaises(GeminiSettingsError):
            audit_stream_events([{"type": "init", "model": self.MODEL}, {"type": "tool_call"}], self.MODEL)

    @unittest.skipUnless(shutil.which("gemini") and shutil.which("node"), "installed Gemini resolver unavailable")
    def test_installed_loader_resolves_hashed_system_override(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings_path, digest = write_run_local_settings(root, self.MODEL)
            executable = Path(shutil.which("gemini")).resolve()
            cli_root = executable.parents[1]
            user_settings = Path.home() / ".gemini/settings.json"
            before = user_settings.read_bytes() if user_settings.exists() else None
            environment = dict(os.environ)
            environment["GEMINI_CLI_SYSTEM_SETTINGS_PATH"] = str(settings_path)
            result = subprocess.run(["node", str(Path(__file__).resolve().parents[2] / "src/curriculum_factory/resolve_gemini_settings.mjs"),
                                     str(cli_root), self.MODEL], cwd=root, env=environment,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            audit = json.loads(result.stdout)
            self.assertEqual(audit["resolved_model_config"]["model"], self.MODEL)
            self.assertEqual(audit["resolved_model_config"]["generateContentConfig"]["thinkingConfig"]["thinkingLevel"], "HIGH")
            self.assertEqual(audit["layers"]["system"]["sha256"], digest)
            self.assertEqual(audit["effective_tools"]["core"], [])
            self.assertEqual(audit["effective_mcp_server_count"], 0)
            self.assertEqual(user_settings.read_bytes() if user_settings.exists() else None, before)


if __name__ == "__main__":
    unittest.main()
