#!/usr/bin/env python3
"""
Regression test for the `verify` integrity gap found 2026-08-10.

`verify` used to print `terminal["state"]` from session.json without checking it
against the last round's own chain-verified response, and matched the final artifact
hash against session.json's cached copy instead of the round's meta.json. Both fields
live in session.json, which nothing here is supposed to write by hand — but nothing
enforced that either, so a single edit to session.json could turn a real Codex FAIL
into a reported QA_PASSED, or make a review of one artifact carry over to a swapped-in
different one, without breaking the hash chain or the Codex-rollout witness check.

This builds synthetic sessions (no live Codex call — a fake rollout file stands in
for Codex's own session record) with an internally valid chain, tampers session.json
exactly as those two exploits did, and asserts `verify` now catches it. It also checks
an honest PASS and an honest FAIL still verify cleanly, so the fix doesn't regress the
common case.

Run directly: python3 scripts/test_verify_integrity.py
"""

import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("qa_gate.py")
spec = importlib.util.spec_from_file_location("qa_gate", MODULE_PATH)
qa_gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa_gate)


def build_session(tmp: Path, *, verdict: str, findings, session_id: str,
                   artifact_name: str = "adder.v1.py",
                   artifact_body: str = "def add(a, b):\n    return a - b\n"):
    """
    Write a complete, internally-consistent QA session: artifact, QA/rounds/round-01.*,
    session.json, and a fake Codex rollout file that witnesses round 1 exactly as
    `verify` expects one to look.

    Returns (qa_dir, artifact_path, rollout_path).
    """
    artifact = tmp / artifact_name
    artifact.write_text(artifact_body, encoding="utf-8")

    qa_dir = tmp / "QA"
    sess = qa_gate.Session(qa_dir)
    sess.rounds_dir.mkdir(parents=True, exist_ok=True)

    request_text = f"You are the independent QA authority.\nArtifact: {artifact}\n"
    response_obj = {
        "verdict": verdict,
        "honesty_audit": {"prior_rounds_consistent": True, "rounds_you_recall": 0,
                          "discrepancies": []},
        "rebuttal_response": "",
        "findings": findings,
        "observations": [],
        "reasoning": "test fixture",
    }
    response_text = json.dumps(response_obj)

    paths = sess.round_paths(1)
    paths["request"].write_text(request_text, encoding="utf-8")
    paths["response"].write_text(response_text, encoding="utf-8")

    turn_id = f"turn-{session_id}"
    artifact_sha = qa_gate.sha256_file(artifact)
    meta = {
        "attempt": 1,
        "turn_id": turn_id,
        "cwd": str(tmp),
        "artifact_path": str(artifact),
        "artifact_sha256": artifact_sha,
        "grounding": [],
        "request_sha256": qa_gate.sha256_text(request_text),
        "response_sha256": qa_gate.sha256_text(response_text),
    }
    meta["chain"] = qa_gate.chain_next(
        qa_gate.GENESIS, meta["request_sha256"], meta["response_sha256"],
        artifact_sha, qa_gate.grounding_digest([]))
    qa_gate.write_json(paths["meta"], meta)

    blocking = qa_gate.at_threshold(findings, "blocker")
    is_pass = verdict == "PASS" and not blocking
    terminal = {
        "state": "QA_PASSED" if is_pass else "QA_FAILED",
        "reason": "CONVERGED" if is_pass else "MAX_ITERATIONS_EXHAUSTED",
        "detail": "test fixture",
        "artifact": str(artifact),
        "rounds_completed": 1,
        "max_iterations": 3,
        "session_id": session_id,
        "thread_id": session_id,
        "transport": "app-server",
        "rollout_file": "",
        "chain": meta["chain"],
        "qa_dir": str(qa_dir),
        "finalized_at": qa_gate.now_iso(),
    }
    state = {
        "opened_at": qa_gate.now_iso(),
        "artifact_original": str(artifact),
        "artifact_current": str(artifact),
        "session_id": session_id,
        "thread_id": session_id,
        "chain": meta["chain"],
        "rounds_completed": 1,
        "rounds": [{
            "round": 1,
            "timestamp": qa_gate.now_iso(),
            "verdict": verdict,
            "artifact_path": str(artifact),
            "artifact_sha256": artifact_sha,
            "findings_at_threshold": [
                {"id": f.get("id"), "title": f.get("title"),
                 "severity": f.get("severity"), "criterion_ref": f.get("criterion_ref")}
                for f in blocking
            ],
            "observations_count": 0,
            "chain": meta["chain"],
        }],
        "stall_count": 0,
        "last_fingerprint": None,
        "exec_copied": [],
        "terminal": terminal,
        "config": {
            "criteria": "add(a, b) returns a + b",
            "focus": "",
            "threshold": "blocker",
            "max_iterations": 3,
            "timeout_seconds": 900,
            "retries": 2,
            "model": None,
            "effort": None,
            "transport": "app-server",
            "allow_execution": False,
            "grounding": [],
        },
    }
    sess.save(state)

    rollout = tmp / f"rollout-{session_id}.jsonl"
    rows = [
        {"type": "turn_context",
         "payload": {"turn_id": turn_id, "sandbox_policy": {"type": "read-only"},
                     "cwd": str(tmp), "workspace_roots": []}},
        {"type": "event_msg",
         "payload": {"type": "user_message", "message": request_text}},
        {"type": "event_msg",
         "payload": {"type": "task_complete", "turn_id": turn_id,
                     "last_agent_message": response_text}},
    ]
    rollout.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    return qa_dir, artifact, rollout


class VerifyIntegrityTest(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)
        self._orig_find_rollout = qa_gate.find_rollout

    def tearDown(self):
        qa_gate.find_rollout = self._orig_find_rollout
        self._tmpdir.cleanup()

    def _patch_rollout(self, rollout_path: Path):
        qa_gate.find_rollout = lambda session_id: rollout_path

    def _verify(self, qa_dir: Path):
        args = types.SimpleNamespace(qa_dir=str(qa_dir))
        code = qa_gate.cmd_verify(args)
        result = json.loads((qa_dir / "verification.json").read_text(encoding="utf-8"))
        return code, result

    def test_honest_fail_verifies_clean(self):
        qa_dir, _, rollout = build_session(
            self.tmp, verdict="FAIL", session_id="s-fail",
            findings=[{"id": "F1", "title": "subtracts instead of adding",
                      "severity": "blocker", "criterion_ref": "criterion 1"}])
        self._patch_rollout(rollout)
        code, result = self._verify(qa_dir)
        self.assertEqual(result["state"], "QA_FAILED")
        self.assertTrue(result["chain_valid"])
        self.assertEqual(result["problems"], [])
        self.assertEqual(code, qa_gate.FAILED)

    def test_honest_pass_verifies_clean(self):
        qa_dir, artifact, rollout = build_session(
            self.tmp, verdict="PASS", session_id="s-pass",
            findings=[], artifact_body="def add(a, b):\n    return a + b\n")
        self._patch_rollout(rollout)
        code, result = self._verify(qa_dir)
        self.assertEqual(result["state"], "QA_PASSED")
        self.assertTrue(result["chain_valid"])
        self.assertEqual(result["problems"], [])
        self.assertEqual(code, qa_gate.PASSED)

    def test_terminal_flip_is_caught(self):
        """
        Reproduces the exploit found live: a real Codex FAIL (blocker, untouched
        response.json/meta.json — the chain-hashed evidence) with session.json's
        cached `terminal` and `rounds[0]` fields hand-edited to claim PASS.
        """
        qa_dir, _, rollout = build_session(
            self.tmp, verdict="FAIL", session_id="s-flip",
            findings=[{"id": "F1", "title": "subtracts instead of adding",
                      "severity": "blocker", "criterion_ref": "criterion 1"}])
        self._patch_rollout(rollout)

        state = qa_gate.read_json(qa_dir / "session.json")
        state["terminal"]["state"] = "QA_PASSED"
        state["terminal"]["reason"] = "CONVERGED"
        state["rounds"][0]["verdict"] = "PASS"
        state["rounds"][0]["findings_at_threshold"] = []
        qa_gate.write_json(qa_dir / "session.json", state)

        code, result = self._verify(qa_dir)
        self.assertFalse(result["chain_valid"],
                         "verify must not report chain_valid on a flipped terminal")
        self.assertNotEqual(result["state"], "QA_PASSED",
                            "verify must not report QA_PASSED when the real Codex "
                            "verdict for the last round was FAIL")
        self.assertTrue(any("TERMINAL_STATE_MISMATCH" in p for p in result["problems"]),
                        result["problems"])
        self.assertEqual(code, qa_gate.FAILED)

    def test_artifact_substitution_is_caught(self):
        """
        Reproduces the second exploit: a genuine PASS transcript for one artifact,
        with session.json's cached artifact pointer and hash swapped to a different
        file after the fact — round-01.meta.json (chain-hashed) still names the
        original artifact's real hash.
        """
        qa_dir, artifact, rollout = build_session(
            self.tmp, verdict="PASS", session_id="s-swap",
            findings=[], artifact_body="def add(a, b):\n    return a + b\n")
        self._patch_rollout(rollout)

        swapped = self.tmp / "normalizer.v1.py"
        swapped.write_text("def normalize(s):\n    return s.strip().lower()\n",
                           encoding="utf-8")
        swapped_sha = qa_gate.sha256_file(swapped)

        state = qa_gate.read_json(qa_dir / "session.json")
        state["artifact_current"] = str(swapped)
        state["rounds"][0]["artifact_sha256"] = swapped_sha
        state["terminal"]["artifact"] = str(swapped)
        qa_gate.write_json(qa_dir / "session.json", state)

        code, result = self._verify(qa_dir)
        self.assertFalse(result["chain_valid"],
                         "verify must not report chain_valid when the artifact a "
                         "PASS is claimed for differs from what round 1 actually "
                         "hashed and reviewed")
        self.assertTrue(
            any("has been modified since round" in p or "artifact_sha256" in p
                for p in result["problems"]),
            result["problems"])
        self.assertEqual(code, qa_gate.FAILED)


if __name__ == "__main__":
    unittest.main()
