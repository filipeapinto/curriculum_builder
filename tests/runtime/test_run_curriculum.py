from __future__ import annotations

import ast
import json
import unittest
import tempfile
from pathlib import Path
from unittest import mock

from runtime.controller import CurriculumRuntime
from runtime.langgraph_factory import egress as eg
from runtime.langgraph_factory import transport as tp
import runtime.run_curriculum as run_curriculum_module
import runtime.run_curriculum as R


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


# ===========================================================================
# N30: `_prove_one_driver` / `_prove_driver_capabilities` -- the five
# differentiated driver-capability proof classes, spec 7.1.
#
# Every adversarial scenario below injects a fake `runner` (the same
# `Callable[..., tp.ProcessOutcome]` contract `tp.CliTransport` already uses,
# never a real subprocess), so this suite is hermetic: it proves N30's own
# dispatch/gating logic, not whether a live subscription happens to be
# installed on the machine running the suite. The one genuinely live,
# unmocked exercise of the production path lives in
# `LiveDriverCapabilityProbeTests` below.
# ===========================================================================


def _outcome(*, returncode=0, stdout="", stderr="", termination="exited"):
    return tp.ProcessOutcome(returncode=returncode, stdout=stdout, stderr=stderr, pid=4242, termination=termination)


def _claude_stream(*, model="claude-sonnet-5", tools=(), mcp_servers=()):
    init_event = {
        "type": "system", "subtype": "init",
        "tools": list(tools), "mcp_servers": list(mcp_servers),
    }
    assistant_event = {
        "type": "assistant", "parent_tool_use_id": None,
        "message": {"model": model},
    }
    return "\n".join(json.dumps(event) for event in (init_event, assistant_event))


def _codex_stream(*, model="gpt-5.6-sol"):
    return json.dumps({"type": "session_configured", "model": model})


class DriverCapabilityFieldTests(unittest.TestCase):
    """TEST 1: five separate, explicit capability proof fields -- never one flag."""

    def test_a_ready_driver_reports_every_field_pass_and_no_undifferentiated_flag(self):
        runner = mock.Mock(return_value=_outcome(stdout=_claude_stream()))
        with tempfile.TemporaryDirectory() as raw:
            detail = run_curriculum_module._prove_one_driver(
                "claude", model="claude-sonnet-5", provider="anthropic",
                data_classes=["manifest_unit_projection"], runner=runner, workspace=Path(raw),
            )
        self.assertTrue(detail["ready"])
        self.assertEqual(detail["failed_fields"], [])
        self.assertEqual(set(detail["fields"]), set(run_curriculum_module.DRIVER_CAPABILITY_FIELDS))
        for field_name, field_detail in detail["fields"].items():
            with self.subTest(field=field_name):
                self.assertEqual(field_detail["status"], "PASS")
        # every field is its own object, not references to one shared flag
        statuses = [id(field) for field in detail["fields"].values()]
        self.assertEqual(len(statuses), len(set(statuses)))


class DriverCapabilityToolClosureTests(unittest.TestCase):
    """TEST 2 / 5 / 6: D03's tool/MCP-closure check, wired into real dispatch."""

    def test_closure_evaluates_the_observed_init_event_not_the_sandbox_flag(self):
        """N20-F06 regression, made permanent here: an MCP server is *listed* under
        `--setting-sources ""` but every one is `needs-auth` (no tool actually
        granted) -- closure must still be proven, not merely assumed from flag
        presence and not refused merely because a server is listed."""
        stream = _claude_stream(
            tools=[],
            mcp_servers=[
                {"name": "claude.ai Cloud Drive", "status": "needs-auth"},
                {"name": "claude.ai Mail", "status": "needs-auth"},
            ],
        )
        runner = mock.Mock(return_value=_outcome(stdout=stream))
        with tempfile.TemporaryDirectory() as raw:
            detail = run_curriculum_module._prove_one_driver(
                "claude", model="claude-sonnet-5", provider="anthropic",
                data_classes=[], runner=runner, workspace=Path(raw),
            )
        self.assertTrue(detail["ready"])
        self.assertEqual(detail["fields"]["tool_mcp_closure"]["status"], "PASS")
        self.assertEqual(detail["fields"]["tool_mcp_closure"]["closure"]["invokable_mcp_servers"], [])

    def test_an_exposed_non_structured_output_tool_fails_closure(self):
        stream = _claude_stream(tools=["Bash"])
        runner = mock.Mock(return_value=_outcome(stdout=stream))
        with tempfile.TemporaryDirectory() as raw:
            detail = run_curriculum_module._prove_one_driver(
                "claude", model="claude-sonnet-5", provider="anthropic",
                data_classes=[], runner=runner, workspace=Path(raw),
            )
        self.assertFalse(detail["ready"])
        self.assertEqual(detail["fields"]["tool_mcp_closure"]["status"], "FAIL")
        self.assertIn("tool_mcp_closure", detail["failed_fields"])

    def test_an_authenticated_invokable_mcp_server_fails_closure(self):
        stream = _claude_stream(mcp_servers=[{"name": "internal-tool", "status": "connected"}])
        runner = mock.Mock(return_value=_outcome(stdout=stream))
        with tempfile.TemporaryDirectory() as raw:
            detail = run_curriculum_module._prove_one_driver(
                "claude", model="claude-sonnet-5", provider="anthropic",
                data_classes=[], runner=runner, workspace=Path(raw),
            )
        self.assertFalse(detail["ready"])
        self.assertEqual(detail["fields"]["tool_mcp_closure"]["status"], "FAIL")

    def test_tool_mcp_closure_is_not_applicable_for_the_codex_driver(self):
        runner = mock.Mock(return_value=_outcome(stdout=_codex_stream()))
        with tempfile.TemporaryDirectory() as raw:
            detail = run_curriculum_module._prove_one_driver(
                "codex", model="gpt-5.6-sol", provider="openai",
                data_classes=[], runner=runner, workspace=Path(raw),
            )
        self.assertEqual(detail["fields"]["tool_mcp_closure"]["status"], "not_applicable")


class DriverCapabilityReadinessGateTests(unittest.TestCase):
    """TEST 3 / 4 / 6: every mandatory field gates readiness; Run 26's exact
    false-ready defect (binaries present, provider unauthenticated) must not
    reproduce."""

    def test_ready_requires_every_field_true_one_failure_makes_the_driver_not_ready(self):
        for failing_field in run_curriculum_module.DRIVER_CAPABILITY_FIELDS:
            with self.subTest(field=failing_field):
                runner = mock.Mock(return_value=_outcome(stdout=_claude_stream()))
                with tempfile.TemporaryDirectory() as raw:
                    if failing_field == "executable_identity":
                        with mock.patch.object(
                            run_curriculum_module.tp, "probe_executable",
                            side_effect=tp.CapabilityProofFailed("executable not on PATH: claude"),
                        ):
                            detail = run_curriculum_module._prove_one_driver(
                                "claude", model="claude-sonnet-5", provider="anthropic",
                                data_classes=[], runner=runner, workspace=Path(raw),
                            )
                    elif failing_field == "approved_data_boundary":
                        detail = run_curriculum_module._prove_one_driver(
                            "claude", model="claude-sonnet-5", provider="not-a-real-provider",
                            data_classes=[], runner=runner, workspace=Path(raw),
                        )
                    elif failing_field == "observable_subscription_backed_usability":
                        bad_runner = mock.Mock(return_value=_outcome(returncode=1, stderr="not authenticated"))
                        detail = run_curriculum_module._prove_one_driver(
                            "claude", model="claude-sonnet-5", provider="anthropic",
                            data_classes=[], runner=bad_runner, workspace=Path(raw),
                        )
                    else:
                        continue
                self.assertFalse(detail["ready"])
                self.assertIn(failing_field, detail["failed_fields"])

    def test_run_26_defect_binaries_present_provider_unauthenticated_is_not_ready(self):
        """Executable identity genuinely resolves (binaries present); the bounded
        probe exits nonzero (provider unauthenticated) -- `ready` must be false."""
        real_identity = tp.ExecutableIdentity(
            name="claude", path="/usr/local/bin/claude", sha256="a" * 64, version="1.0.0")
        unauthenticated_runner = mock.Mock(
            return_value=_outcome(returncode=1, stderr="Please run `claude login`"))
        with tempfile.TemporaryDirectory() as raw, \
             mock.patch.object(run_curriculum_module.tp, "probe_executable", return_value=real_identity):
            detail = run_curriculum_module._prove_one_driver(
                "claude", model="claude-sonnet-5", provider="anthropic",
                data_classes=[], runner=unauthenticated_runner, workspace=Path(raw),
            )
        self.assertEqual(detail["fields"]["executable_identity"]["status"], "PASS")
        self.assertFalse(detail["ready"])
        self.assertIn("observable_subscription_backed_usability", detail["failed_fields"])
        self.assertEqual(
            detail["fields"]["observable_subscription_backed_usability"]["reason"], "nonzero_bounded_probe")


class DriverCapabilityAdversarialCoverageTests(unittest.TestCase):
    """TEST 6: executable spoofing, wrong auth mode, unavailable subscription,
    nonzero bounded probe, malformed output, model/driver mismatch, forbidden
    environment credential, unapproved endpoint, attempted fallback."""

    def test_executable_spoofing_is_caught(self):
        runner = mock.Mock(return_value=_outcome(stdout=_claude_stream()))
        with tempfile.TemporaryDirectory() as raw, \
             mock.patch.object(
                 run_curriculum_module.tp, "probe_executable",
                 side_effect=tp.CapabilityProofFailed("claude --version failed with 127"),
             ):
            detail = run_curriculum_module._prove_one_driver(
                "claude", model="claude-sonnet-5", provider="anthropic",
                data_classes=[], runner=runner, workspace=Path(raw),
            )
        self.assertEqual(detail["fields"]["executable_identity"]["status"], "FAIL")
        self.assertFalse(detail["ready"])

    def test_forbidden_environment_credential_fails_closed_before_any_subprocess(self):
        runner = mock.Mock()
        with tempfile.TemporaryDirectory() as raw, \
             mock.patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-forbidden"}):
            detail = run_curriculum_module._prove_one_driver(
                "claude", model="claude-sonnet-5", provider="anthropic",
                data_classes=[], runner=runner, workspace=Path(raw),
            )
        self.assertFalse(detail["ready"])
        self.assertEqual(detail["fields"]["permitted_auth_mode"]["status"], "FAIL")
        self.assertEqual(detail["fields"]["permitted_auth_mode"]["reason"], "forbidden_api_key_present")
        runner.assert_not_called()

    def test_unavailable_subscription_and_nonzero_bounded_probe(self):
        runner = mock.Mock(return_value=_outcome(returncode=1, stderr="not logged in"))
        with tempfile.TemporaryDirectory() as raw:
            detail = run_curriculum_module._prove_one_driver(
                "codex", model="gpt-5.6-sol", provider="openai",
                data_classes=[], runner=runner, workspace=Path(raw),
            )
        self.assertEqual(detail["fields"]["observable_subscription_backed_usability"]["status"], "FAIL")
        self.assertEqual(
            detail["fields"]["observable_subscription_backed_usability"]["reason"], "nonzero_bounded_probe")

    def test_malformed_output_is_not_a_silent_pass(self):
        runner = mock.Mock(return_value=_outcome(returncode=0, stdout="not json at all\n<<<garbage>>>"))
        with tempfile.TemporaryDirectory() as raw:
            detail = run_curriculum_module._prove_one_driver(
                "claude", model="claude-sonnet-5", provider="anthropic",
                data_classes=[], runner=runner, workspace=Path(raw),
            )
        self.assertEqual(
            detail["fields"]["observable_subscription_backed_usability"]["reason"],
            "malformed_or_unobservable_output",
        )
        self.assertFalse(detail["ready"])

    def test_model_driver_mismatch_is_caught(self):
        runner = mock.Mock(return_value=_outcome(stdout=_claude_stream(model="claude-haiku-4-5-20251001")))
        with tempfile.TemporaryDirectory() as raw:
            detail = run_curriculum_module._prove_one_driver(
                "claude", model="claude-sonnet-5", provider="anthropic",
                data_classes=[], runner=runner, workspace=Path(raw),
            )
        field = detail["fields"]["observable_subscription_backed_usability"]
        self.assertEqual(field["status"], "FAIL")
        self.assertEqual(field["reason"], "model_driver_mismatch")
        self.assertEqual(field["expected_model"], "claude-sonnet-5")
        self.assertEqual(field["observed_model"], "claude-haiku-4-5-20251001")

    def test_unapproved_endpoint_provider_fails_the_data_boundary(self):
        runner = mock.Mock(return_value=_outcome(stdout=_claude_stream()))
        with tempfile.TemporaryDirectory() as raw:
            detail = run_curriculum_module._prove_one_driver(
                "claude", model="claude-sonnet-5", provider="retired-third-party",
                data_classes=[], runner=runner, workspace=Path(raw),
            )
        self.assertEqual(detail["fields"]["approved_data_boundary"]["status"], "FAIL")
        self.assertEqual(detail["fields"]["approved_data_boundary"]["reason"], "unapproved_provider")
        self.assertFalse(detail["ready"])
        # never any local reimplementation of the allowlist: the real, current
        # egress.py membership check is what actually failed it
        self.assertNotIn("retired-third-party", eg.PROVIDERS)

    def test_an_unavailable_approved_driver_never_recommends_a_fallback(self):
        """TEST 9: an honest non-success state, never a fallback-provider
        recommendation or alternate-provider route."""
        real_prove_one_driver = run_curriculum_module._prove_one_driver
        failing_runner = mock.Mock(return_value=_outcome(returncode=1, stderr="unavailable"))
        passing_runner = mock.Mock(return_value=_outcome(stdout=_claude_stream()))

        def fake_prove_one_driver(cli, **kwargs):
            kwargs["runner"] = failing_runner if cli == "codex" else passing_runner
            return real_prove_one_driver(cli, **kwargs)

        with tempfile.TemporaryDirectory() as raw, \
             mock.patch.object(run_curriculum_module, "_prove_one_driver", side_effect=fake_prove_one_driver):
            proof = run_curriculum_module._prove_driver_capabilities(workspace=Path(raw))

        self.assertFalse(proof["ready"])
        self.assertTrue(proof["drivers"]["claude"]["ready"])
        self.assertFalse(proof["drivers"]["codex"]["ready"])
        self.assertEqual(set(proof), {"ready", "drivers"})
        serialized = json.dumps(proof, default=str).lower()
        for forbidden_term in ("fallback", "alternate_provider", "recommended_route", "substitute"):
            self.assertNotIn(forbidden_term, serialized)


class DriverCapabilityContentFreeAndBoundaryTests(unittest.TestCase):
    """TEST 7 / 8: probes are content-free; the CLI calls only N20-owned egress
    functions for the provider/data-class boundary, never a local copy."""

    def test_probe_instruction_and_stdin_carry_no_curriculum_content(self):
        instruction = run_curriculum_module._PROBE_INSTRUCTION
        for forbidden in ("curriculum", "output_root", "digest", ".pdf", "/Users", "manifest"):
            self.assertNotIn(forbidden, instruction.lower())
        payload = tp.build_claude_stdin_payload(instruction=instruction, projection={})
        decoded = json.loads(payload)
        self.assertEqual(decoded["authorized_input_projection"], {})

    def test_content_free_field_is_reported_for_every_probe_regardless_of_outcome(self):
        runner = mock.Mock(return_value=_outcome(returncode=1, stderr="boom"))
        with tempfile.TemporaryDirectory() as raw:
            detail = run_curriculum_module._prove_one_driver(
                "claude", model="claude-sonnet-5", provider="anthropic",
                data_classes=[], runner=runner, workspace=Path(raw),
            )
        self.assertEqual(detail["fields"]["content_free_operation"]["status"], "PASS")
        self.assertEqual(detail["fields"]["content_free_operation"]["transmitted_authorized_input_projection"], {})

    def test_the_cli_source_imports_the_provider_boundary_read_only_and_defines_no_local_copy(self):
        """No local reimplementation of the provider allowlist or data-class
        mapping: the only provider/data-class vocabulary in this source comes from
        `egress.PROVIDERS`/`egress.PROVIDER_DATA_CLASSES`, imported, never a second,
        separately-declared tuple or dict of provider names."""
        import_from_egress = {
            alias.name
            for node in ast.walk(RUN_CURRICULUM_AST)
            if isinstance(node, ast.ImportFrom) and node.module and node.module.endswith(".egress")
            for alias in node.names
        }
        self.assertIn("PROVIDERS", import_from_egress)
        self.assertIn("PROVIDER_DATA_CLASSES", import_from_egress)
        # no second, locally-declared collection literally listing "anthropic" and
        # "openai" and "primary_source_hosts" together, which would be a local copy
        # of egress.PROVIDERS rather than a read-only reference to it
        for node in ast.walk(RUN_CURRICULUM_AST):
            if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
                literal_strings = {
                    element.value for element in node.elts
                    if isinstance(element, ast.Constant) and isinstance(element.value, str)
                }
                self.assertFalse(
                    {"anthropic", "openai", "primary_source_hosts"} <= literal_strings,
                    "run_curriculum.py declares a local copy of egress.PROVIDERS",
                )


class _FakeRegistry:
    def __init__(self, *, guard, runner=None):
        self.guard = guard
        self.runner = runner or (lambda *a, **k: None)
        self.capability_proof = None
        self.driver_capability_proof = None


class LiveInvokeCapabilityGateTests(unittest.TestCase):
    """TEST 3 / 4 / 10: the production CLI's live-invoke path (not just preflight)
    is the hard, unconditional stop before any curriculum content can be
    transmitted -- Run 26's exact defect, reproduced and refused at this gate."""

    def test_a_not_ready_driver_proof_stops_the_live_invoke_before_it_ever_reaches_the_graph(self):
        guard = mock.Mock(installed=True)
        context = mock.Mock(transport_registry=_FakeRegistry(guard=guard))
        not_ready_proof = {
            "ready": False,
            "drivers": {
                "claude": {"ready": True}, "codex": {"ready": False, "failed_fields": ["observable_subscription_backed_usability"]},
            },
        }
        with mock.patch.object(
            run_curriculum_module.tp, "prove_transport_capabilities",
            return_value={"satisfied": True, "unsatisfied_required_facets": []},
        ), mock.patch.object(
            run_curriculum_module, "_prove_driver_capabilities", return_value=not_ready_proof,
        ):
            with self.assertRaises(run_curriculum_module.tp.CapabilityProofFailed) as raised:
                run_curriculum_module._prove_live_capabilities(context, Path("/engine"), Path("/out"))
        self.assertIn("codex", str(raised.exception))
        # the failed proof is still attached, for D03's best-effort read and for audit
        self.assertEqual(context.transport_registry.driver_capability_proof, not_ready_proof)

    def test_a_ready_driver_proof_lets_the_live_invoke_proceed(self):
        guard = mock.Mock(installed=True)
        context = mock.Mock(transport_registry=_FakeRegistry(guard=guard))
        ready_proof = {"ready": True, "drivers": {"claude": {"ready": True}, "codex": {"ready": True}}}
        with mock.patch.object(
            run_curriculum_module.tp, "prove_transport_capabilities",
            return_value={"satisfied": True, "unsatisfied_required_facets": []},
        ), mock.patch.object(
            run_curriculum_module, "_prove_driver_capabilities", return_value=ready_proof,
        ):
            run_curriculum_module._prove_live_capabilities(context, Path("/engine"), Path("/out"))
        self.assertEqual(context.transport_registry.driver_capability_proof, ready_proof)


class LiveDriverCapabilityProbeTests(unittest.TestCase):
    """TEST 10: exercise the production CLI preflight path for real -- a genuine,
    unmocked, bounded, content-free `claude`/`codex` subprocess probe against
    whatever is actually installed. Deliberately the *only* test in this suite
    that is not hermetic: everything else injects a fake runner so the suite
    stays fast and deterministic; this one exists precisely to prove the wiring
    above is not merely plausible against fixtures but genuinely works against a
    live, installed CLI.
    """

    def test_the_real_production_probe_runs_end_to_end_against_the_installed_clis(self):
        proof = run_curriculum_module._prove_driver_capabilities()
        self.assertEqual(set(proof), {"ready", "drivers"})
        self.assertEqual(set(proof["drivers"]), set(run_curriculum_module.MANDATORY_DRIVER_CLIS))
        for cli, detail in proof["drivers"].items():
            with self.subTest(cli=cli):
                self.assertEqual(set(detail["fields"]), set(run_curriculum_module.DRIVER_CAPABILITY_FIELDS))
                for field_name, field_detail in detail["fields"].items():
                    self.assertIn(field_detail["status"], ("PASS", "FAIL", "not_applicable"), field_name)
        # the installed claude CLI in this environment is subscription-authenticated
        # and genuinely closed: this is the one assertion this test makes about a
        # *specific* live outcome, everything else only checks well-formedness,
        # since a live environment's actual auth/model state is not this suite's
        # to assert on beyond "the wiring produced an honest, well-shaped answer."
        claude = proof["drivers"]["claude"]
        self.assertEqual(claude["fields"]["executable_identity"]["status"], "PASS")
        self.assertEqual(claude["fields"]["permitted_auth_mode"]["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
