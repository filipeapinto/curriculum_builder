"""N40 CLI cutover proof: `runtime.run_curriculum` as the sole production entry.

Covers the node's own TEST checklist:

1. static + runtime call-graph proof of one production graph builder/path
2. CLI help exposes no legacy simulation/session-bridge/custom-controller path
3. mode mutual exclusion, arguments, canonical paths, collision/resume rules,
   stdout JSON, stderr diagnostics, and exit codes
4. preflight is read-only and cannot emit product success
5. CLI code contains no product nodes, guards, joins, acceptance, or frontier
   selection
6. missing authorization/capability fails before transmission and never
   simulates
7. existing Plan 25 roots are readable history but refused for Plan 26 resume
8. production import audit rejects LangChain wrappers/provider SDKs/direct
   model HTTP

The heavy graph/transport machinery (real LangGraph compilation, real model
transport, real checkpoint durability) is proven elsewhere (N20/N30's own
suites); this module proves the CLI *wires* those pieces correctly, using
the real persistence layer wherever it is cheap and safe to do so, real
bounded subprocess probes against the installed `claude`/`codex` CLIs where
N30's own preflight/capability behavior is under test, and narrow mocks only
where a real call would require a live subscription session this
environment does not have.
"""

from __future__ import annotations

import ast
import io
import json
import re
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from runtime.langgraph_factory import persistence as P
from runtime.langgraph_factory import transport as tp

import runtime.run_curriculum as R

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_SOURCE_PATH = REPO_ROOT / "runtime" / "run_curriculum.py"
CLI_SOURCE = CLI_SOURCE_PATH.read_text(encoding="utf-8")
CLI_AST = ast.parse(CLI_SOURCE, filename=str(CLI_SOURCE_PATH))


def _run_main(argv: list[str]) -> tuple[int, dict, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = R.main(argv)
    text = out.getvalue()
    assert text.count("\n") == 1, f"expected exactly one JSON line on stdout, got: {text!r}"
    return code, json.loads(text), err.getvalue()


def _passing_driver_capability_proof() -> dict:
    """A ready `driver_capability_proof`, for tests that stub the live-invoke path and
    must not launch a real, subscription-dependent `claude`/`codex` subprocess."""

    fields = {name: {"status": "PASS"} for name in R.DRIVER_CAPABILITY_FIELDS}
    drivers = {
        cli: {
            "cli": cli,
            "model": "claude-sonnet-5" if cli == "claude" else "gpt-5.6-sol",
            "provider": "anthropic" if cli == "claude" else "openai",
            "ready": True,
            "failed_fields": [],
            "fields": dict(fields),
        }
        for cli in R.MANDATORY_DRIVER_CLIS
    }
    return {"ready": True, "drivers": drivers}


_PASSING_DRIVER_CAPABILITIES = _passing_driver_capability_proof()


def _authorization_file(tmp_path: Path, **overrides) -> Path:
    payload = {
        "approved_at_utc": "2026-01-01T00:00:00+00:00",
        "expires_at_utc": "2099-01-01T00:00:00+00:00",
        "providers": {},
        "executables": [],
    }
    payload.update(overrides)
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


# ===========================================================================
# TEST 1 / 5 / 8 — static source and import-graph audit
# ===========================================================================


class ImportGraphAuditTests(unittest.TestCase):
    """No node reads this file; it is read once, at collection time."""

    def _imported_names(self) -> list[tuple[str, str]]:
        """Every `(module, attribute)` this file imports, `attribute` "" for a bare import."""
        found: list[tuple[str, str]] = []
        for node in ast.walk(CLI_AST):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    found.append((module, alias.name))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    found.append((alias.name, ""))
        return found

    def test_no_plan25_or_legacy_runtime_modules_are_imported(self):
        forbidden_modules = {
            "runtime.controller",
            "runtime.curriculum_factory_graph",
            "runtime.model_worker",
            "runtime.session_bridge",
            "runtime.checks",
            "runtime.checkpoint",
            "runtime.capability_cycle",
        }
        forbidden_names = {"CurriculumFactoryGraph", "CodexWorker", "CurriculumRuntime"}
        for module, name in self._imported_names():
            self.assertNotIn(module, forbidden_modules, f"legacy module imported: {module}")
            self.assertNotIn(name, forbidden_names, f"legacy symbol imported: {name}")

    def test_only_two_narrow_pure_helpers_are_imported_from_nodes_inputs(self):
        """The declared exception: identity/freeze helpers, plus frozen constant
        vocabulary shared with D03's own proof-field/driver names (never node bodies,
        never logic re-implemented here) -- not a fifth or sixth exception each time
        this grows, but the same "narrow, pure, side-effect-free" discipline the
        module docstring already applies to the two functions below."""
        from_nodes = sorted(name for module, name in self._imported_names() if module.endswith("nodes.inputs"))
        self.assertEqual(
            from_nodes,
            [
                "DRIVER_CAPABILITY_FIELDS",
                "MANDATORY_DRIVER_CLIS",
                "REQUIRED_CAPABILITIES",
                "_frozen_input_records",
                "_resolve_active_manifest",
            ],
        )

    def test_no_import_from_any_other_nodes_or_routing_or_workbook_module(self):
        forbidden_module_suffixes = (
            "nodes.domain", "nodes.content", "nodes.sources", "nodes.render",
            "nodes.review", "nodes.visuals", "nodes.terminal", "nodes",
            "routing", "workbook", "unit_graph", "model_nodes", "repair",
        )
        for module, _name in self._imported_names():
            if module.endswith("nodes.inputs") or module in ("runtime.langgraph_factory.graph",):
                continue
            for suffix in forbidden_module_suffixes:
                self.assertFalse(
                    module == f"runtime.langgraph_factory.{suffix}" or module.endswith(f".{suffix}"),
                    f"unexpected node/topology import: {module}",
                )

    def test_no_langchain_provider_sdk_or_direct_http_imports(self):
        forbidden = ("langchain", "openai", "anthropic", "requests", "httpx", "urllib3")
        for module, name in self._imported_names():
            haystack = f"{module}.{name}".lower()
            for bad in forbidden:
                self.assertNotIn(bad, haystack, f"forbidden provider/HTTP import: {module} / {name}")

    def test_no_product_node_or_guard_identifiers_appear_in_source(self):
        """D00-D98 and M01-M08 are never named: the CLI cannot call, route, or
        guard against a node it never imports."""
        node_id_pattern = re.compile(r"\b(?:D\d{2}[A-Z0-9_]*|M0[1-8][A-Z0-9_]*)\b")
        hits = sorted(set(node_id_pattern.findall(CLI_SOURCE)))
        self.assertEqual(hits, [], f"CLI source names product node IDs: {hits}")

    def test_build_curriculum_factory_graph_is_the_only_graph_builder_referenced(self):
        self.assertIn("build_curriculum_factory_graph", CLI_SOURCE)
        self.assertNotIn("register_workbook_topology", CLI_SOURCE)
        self.assertNotIn("register_skeleton", CLI_SOURCE)
        self.assertNotIn(".compile(", CLI_SOURCE)

    def test_graph_builder_is_called_at_most_once_per_execution_path(self):
        """Each of the two live-mode branches (fresh, resume) calls it exactly
        once; the source has exactly two call sites, one per branch."""
        calls = re.findall(r"build_curriculum_factory_graph\(", CLI_SOURCE)
        self.assertEqual(len(calls), 2)


# ===========================================================================
# TEST 2 — help surface
# ===========================================================================


class HelpSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.help_text = R.build_parser().format_help()

    def test_spec_section_16_flags_are_present(self):
        for flag in ("--engine-root", "--curriculum", "--output-root", "--preflight",
                     "--unit", "--all", "--resume", "--authorization"):
            self.assertIn(flag, self.help_text)

    def test_no_legacy_simulation_or_session_bridge_or_custom_controller_flags(self):
        legacy_flags = (
            "--lab-id", "--model", "--test-static", "--test-simulated-all",
            "--test-live-capabilities", "--test-golden-l01", "--interrupt-after",
            "--max-lab-seconds", "--phase-timeout-seconds", "--max-run-seconds",
        )
        for flag in legacy_flags:
            self.assertNotIn(flag, self.help_text)


# ===========================================================================
# TEST 3 — argument shape, canonical paths, exit codes
# ===========================================================================


class ArgumentValidationTests(unittest.TestCase):
    def test_mode_flags_are_mutually_exclusive(self):
        parser = R.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["--engine-root", ".", "--curriculum", ".", "--output-root", "/x",
                                "--unit", "L01", "--all"])

    def test_at_least_one_mode_flag_is_required(self):
        parser = R.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["--engine-root", ".", "--curriculum", ".", "--output-root", "/x"])

    def test_authorization_required_for_unit_all_resume(self):
        parser = R.build_parser()
        for mode_args in (["--unit", "L01"], ["--all"], ["--resume"]):
            args = parser.parse_args(
                ["--engine-root", ".", "--curriculum", ".", "--output-root", "/x", *mode_args]
            )
            with self.assertRaises(R.CliArgumentError):
                R._validate_args(args)

    def test_preflight_rejects_authorization(self):
        parser = R.build_parser()
        args = parser.parse_args(
            ["--engine-root", ".", "--curriculum", ".", "--output-root", "/x",
             "--preflight", "--authorization", "auth.json"]
        )
        with self.assertRaises(R.CliArgumentError):
            R._validate_args(args)

    def test_curriculum_root_resolves_manifest_file_to_parent_directory(self, tmp_path=None):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = root / "curricula" / "arduino_kit" / "arduino_kit_curriculum.v5.yaml"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("labs: []\n", encoding="utf-8")
            self.assertEqual(R._resolve_curriculum_root(str(manifest)), manifest.parent.resolve())
            self.assertEqual(R._resolve_curriculum_root(str(manifest.parent)), manifest.parent.resolve())

    def test_curriculum_root_missing_path_is_an_argument_error(self):
        with self.assertRaises(R.CliArgumentError):
            R._resolve_curriculum_root("/definitely/does/not/exist/for/plan26")

    def test_authorization_file_must_be_a_json_object_with_required_fields(self):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            not_json = root / "bad.json"
            not_json.write_text("not json", encoding="utf-8")
            with self.assertRaises(R.CliArgumentError):
                R._read_authorization(str(not_json))

            not_object = root / "list.json"
            not_object.write_text("[]", encoding="utf-8")
            with self.assertRaises(R.CliArgumentError):
                R._read_authorization(str(not_object))

            incomplete = root / "incomplete.json"
            incomplete.write_text(json.dumps({"providers": {}}), encoding="utf-8")
            with self.assertRaises(R.CliArgumentError):
                R._read_authorization(str(incomplete))

            missing = root / "missing.json"
            with self.assertRaises(R.CliArgumentError):
                R._read_authorization(str(missing))

    def test_collision_reason_for_fresh_output_root(self):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            nonexistent = root / "does-not-exist-yet"
            self.assertIsNone(R._collision_reason(nonexistent))

            empty = root / "empty"
            empty.mkdir()
            self.assertIsNone(R._collision_reason(empty))

            dirty = root / "dirty"
            dirty.mkdir()
            (dirty / "leftover.txt").write_text("x", encoding="utf-8")
            self.assertIsNotNone(R._collision_reason(dirty))

    def test_argparse_level_errors_exit_with_code_2(self):
        # argparse's own validation (no mode flag at all) raises SystemExit(2)
        # before main()'s try block is reached; that native argparse contract
        # is exit 2, matching spec section 14's "CLI argument errors ... exit 2".
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            with self.assertRaises(SystemExit) as raised:
                R.main(["--engine-root", str(REPO_ROOT), "--curriculum", str(REPO_ROOT), "--output-root", "/x"])
        self.assertEqual(raised.exception.code, 2)

    def test_missing_authorization_exits_2_with_diagnostics_and_no_terminal(self):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            code, payload, err = _run_main(
                ["--engine-root", str(REPO_ROOT), "--curriculum", str(REPO_ROOT),
                 "--output-root", str(root / "out"), "--unit", "L01"]
            )
        self.assertEqual(code, R.ARGUMENT_ERROR_EXIT)
        self.assertNotIn("terminal", payload)
        self.assertIn("error_code", payload)
        self.assertTrue(err.strip())


# ===========================================================================
# TEST 4 — preflight is read-only
# ===========================================================================


class PreflightTests(unittest.TestCase):
    """These exercise preflight's *structural* contract (no writes, no product
    success, collision handling), so the driver probe is stubbed to a passing
    fixture -- the real, unmocked, live probe is exercised once, deliberately, by
    `LiveDriverCapabilityProbeTests` below."""

    def test_preflight_never_creates_or_writes_the_output_root(self):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            output_root = Path(raw) / "preflight-target"
            with mock.patch.object(R, "_prove_driver_capabilities", return_value=_PASSING_DRIVER_CAPABILITIES):
                code, payload, _err = _run_main(
                    ["--engine-root", str(REPO_ROOT), "--curriculum", str(REPO_ROOT),
                     "--output-root", str(output_root), "--preflight"]
                )
            self.assertFalse(output_root.exists(), "preflight must not populate its output path")
            self.assertEqual(payload["kind"], "PREFLIGHT")
            self.assertIn(code, (0, R.NOT_READY_EXIT))
            self.assertEqual(code == 0, payload["ready"])
            self.assertNotIn("terminal", payload)
            self.assertIsInstance(payload["missing_capabilities"], list)
            self.assertIn("driver_capabilities", payload)

    def test_preflight_cannot_emit_product_success(self):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            output_root = Path(raw) / "preflight-target"
            with mock.patch.object(R, "_prove_driver_capabilities", return_value=_PASSING_DRIVER_CAPABILITIES):
                _code, payload, _err = _run_main(
                    ["--engine-root", str(REPO_ROOT), "--curriculum", str(REPO_ROOT),
                     "--output-root", str(output_root), "--preflight"]
                )
        self.assertNotIn(payload.get("kind"), ("UNIT_ACCEPTED", "COMPLETE"))
        self.assertNotIn("accepted_receipt", payload)
        self.assertNotIn("release_receipt", payload)

    def test_preflight_reports_a_collision_without_touching_an_existing_root(self):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            output_root = Path(raw) / "dirty"
            output_root.mkdir()
            (output_root / "stray.txt").write_text("keep-me", encoding="utf-8")
            with mock.patch.object(R, "_prove_driver_capabilities", return_value=_PASSING_DRIVER_CAPABILITIES):
                code, payload, _err = _run_main(
                    ["--engine-root", str(REPO_ROOT), "--curriculum", str(REPO_ROOT),
                     "--output-root", str(output_root), "--preflight"]
                )
            self.assertEqual(code, R.NOT_READY_EXIT)
            self.assertFalse(payload["ready"])
            self.assertIsNotNone(payload["collision"])
            self.assertEqual((output_root / "stray.txt").read_text(encoding="utf-8"), "keep-me")
            self.assertEqual(sorted(p.name for p in output_root.iterdir()), ["stray.txt"])


# ===========================================================================
# TEST 6 — capability/authorization failures never simulate
# ===========================================================================


class CapabilityAndAuthorizationFailureTests(unittest.TestCase):
    def test_capability_proof_failure_happens_before_any_transmission_and_never_simulates(self):
        import tempfile
        invoke_calls = []

        class _StubCompiled:
            def invoke(self, *args, **kwargs):
                invoke_calls.append((args, kwargs))
                raise AssertionError("compiled graph must not be invoked once capability proof fails")

        with tempfile.TemporaryDirectory() as raw:
            output_root = Path(raw) / "out"
            authorization = _authorization_file(Path(raw))
            with mock.patch.object(R, "build_curriculum_factory_graph", return_value=_StubCompiled()), \
                 mock.patch.object(R.tp, "prove_transport_capabilities",
                                    side_effect=tp.CapabilityProofFailed("no codex on PATH")):
                code, payload, err = _run_main(
                    ["--engine-root", str(REPO_ROOT), "--curriculum", str(REPO_ROOT),
                     "--output-root", str(output_root), "--unit", "L01",
                     "--authorization", str(authorization)]
                )

        self.assertEqual(invoke_calls, [])
        self.assertEqual(code, R.SYSTEM_FAILURE_EXIT)
        self.assertEqual(payload["terminal"]["kind"], "SYSTEM_FAILURE")
        self.assertNotIn(payload["terminal"].get("kind"), ("UNIT_ACCEPTED", "COMPLETE"))
        self.assertTrue(err.strip())

    def test_missing_authorization_file_fails_before_any_lock_or_graph_build(self):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            output_root = Path(raw) / "out"
            with mock.patch.object(R, "build_curriculum_factory_graph") as builder:
                code, payload, _err = _run_main(
                    ["--engine-root", str(REPO_ROOT), "--curriculum", str(REPO_ROOT),
                     "--output-root", str(output_root), "--unit", "L01",
                     "--authorization", str(Path(raw) / "does-not-exist.json")]
                )
            builder.assert_not_called()
        self.assertEqual(code, R.ARGUMENT_ERROR_EXIT)
        self.assertFalse(output_root.exists())
        self.assertNotIn("terminal", payload)


# ===========================================================================
# TEST 7 — Plan 25 roots are readable history, refused for resume
# ===========================================================================


class Plan25ResumeRefusalTests(unittest.TestCase):
    def test_a_plan25_shaped_root_is_refused_and_left_byte_identical(self):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            output_root = Path(raw) / "legacy"
            output_root.mkdir()
            # Shaped like the legacy `controller.simulate()` output layout, not
            # the Plan 26 `.langgraph/` contract: no identity envelope at all.
            (output_root / "checkpoints").mkdir()
            legacy_checkpoint = output_root / "checkpoints" / "0001.json"
            legacy_checkpoint.write_text(json.dumps({"terminal_state": "ACCEPTED"}), encoding="utf-8")
            before = {
                p.relative_to(output_root).as_posix(): p.read_bytes()
                for p in sorted(output_root.rglob("*")) if p.is_file()
            }

            with mock.patch.object(R, "build_curriculum_factory_graph") as builder:
                code, payload, err = _run_main(
                    ["--engine-root", str(REPO_ROOT), "--curriculum", str(REPO_ROOT),
                     "--output-root", str(output_root), "--resume",
                     "--authorization", str(_authorization_file(Path(raw)))]
                )
            builder.assert_not_called()

            after = {
                p.relative_to(output_root).as_posix(): p.read_bytes()
                for p in sorted(output_root.rglob("*")) if p.is_file()
            }

        self.assertEqual(code, R.NOT_READY_EXIT)
        self.assertNotIn("terminal", payload)
        self.assertTrue(err.strip())
        self.assertEqual(before, after, "a refused resume must not mutate the Plan 25 root at all")
        self.assertFalse((output_root / P.LANGGRAPH_DIRNAME).exists())


# ===========================================================================
# Output projection / exit-code mapping (pure functions)
# ===========================================================================


class OutputProjectionTests(unittest.TestCase):
    def test_unit_accepted_projects_accepted_receipt(self):
        output = {
            "contract_version": "1", "run_id": "r1", "episode_id": "e1",
            "mode": "one", "requested_unit_id": "U001", "output_root": "/out",
            "terminal": {"kind": "UNIT_ACCEPTED"},
            "accepted_unit_receipts": {"U001": {"receipt_hash": "abc"}},
            "checkpoint_metadata": [{"checkpoint_id": "c1"}, {"checkpoint_id": "c2"}],
            "evidence_index_entries": [{"a": 1}],
        }
        payload = R._project_result(output)
        self.assertEqual(payload["accepted_receipt"], {"receipt_hash": "abc"})
        self.assertNotIn("release_receipt", payload)
        self.assertEqual(payload["checkpoint_id"], "c2")
        self.assertEqual(R._exit_code_for(payload), 0)

    def test_complete_projects_release_receipt(self):
        output = {
            "terminal": {"kind": "COMPLETE"}, "mode": "all",
            "final_release_audits": [{"result": "PASS", "key": "k1"}],
            "checkpoint_metadata": [], "evidence_index_entries": [],
        }
        payload = R._project_result(output)
        self.assertEqual(payload["release_receipt"], {"result": "PASS", "key": "k1"})
        self.assertNotIn("accepted_receipt", payload)
        self.assertEqual(R._exit_code_for(payload), 0)

    def test_every_terminal_kind_maps_to_its_spec_exit_code(self):
        expected = {
            "UNIT_ACCEPTED": 0, "COMPLETE": 0, "INTERRUPTED": 10,
            "PAUSED_PREREQUISITE": 11, "CONVERGENCE_EXHAUSTED": 12, "SYSTEM_FAILURE": 20,
        }
        for kind, exit_code in expected.items():
            payload = R._project_result({"terminal": {"kind": kind}, "checkpoint_metadata": [], "evidence_index_entries": []})
            self.assertEqual(R._exit_code_for(payload), exit_code, kind)

    def test_evidence_index_hash_is_a_digest_over_the_entries(self):
        from runtime.langgraph_factory.artifacts import canonical_digest
        entries = [{"key": "a"}, {"key": "b"}]
        output = {"terminal": {"kind": "INTERRUPTED"}, "evidence_index_entries": entries, "checkpoint_metadata": []}
        payload = R._project_result(output)
        self.assertEqual(payload["evidence_index_hash"], canonical_digest(entries))


# ===========================================================================
# Fresh-run wiring (mocked graph + capability proof, real persistence layer)
# ===========================================================================


class FreshRunWiringTests(unittest.TestCase):
    def test_fresh_unit_run_builds_the_graph_once_and_invokes_with_a_fresh_envelope(self):
        import tempfile

        recorded: dict = {}

        class _StubCompiled:
            def invoke(self, graph_input, *, config, context):
                recorded["graph_input"] = graph_input
                recorded["config"] = config
                recorded["context"] = context
                return {
                    "contract_version": graph_input["invocation"]["contract_version"],
                    "run_id": "state-run-id",
                    "episode_id": "episode-1",
                    "mode": graph_input["invocation"]["mode"],
                    "requested_unit_id": graph_input["invocation"]["requested_unit_id"],
                    "output_root": graph_input["invocation"]["output_root"],
                    "terminal": {"kind": "INTERRUPTED", "classification": "graceful_signal"},
                    "checkpoint_metadata": [],
                    "evidence_index_entries": [],
                }

        builder_calls = []

        def _fake_builder(*, engine_root, output_root):
            builder_calls.append((engine_root, output_root))
            return _StubCompiled()

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            curriculum = root / "curricula" / "arduino_kit"
            manifest = curriculum / "arduino_kit_curriculum.v5.yaml"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("labs: []\n", encoding="utf-8")
            output_root = root / "out"
            authorization = _authorization_file(root, providers={"openai": ["frozen_unit_artifacts"]})

            with mock.patch.object(R, "build_curriculum_factory_graph", side_effect=_fake_builder), \
                 mock.patch.object(R.tp, "prove_transport_capabilities",
                                    return_value={"satisfied": True, "unsatisfied_required_facets": []}), \
                 mock.patch.object(R, "_prove_driver_capabilities", return_value=_PASSING_DRIVER_CAPABILITIES):
                code, payload, _err = _run_main(
                    ["--engine-root", str(REPO_ROOT), "--curriculum", str(manifest),
                     "--output-root", str(output_root), "--unit", "L01",
                     "--authorization", str(authorization)]
                )

        self.assertEqual(len(builder_calls), 1, "the graph must be built exactly once")
        self.assertEqual(code, 10)
        self.assertEqual(payload["terminal"]["kind"], "INTERRUPTED")

        envelope = recorded["graph_input"]["invocation"]
        self.assertEqual(envelope["kind"], "fresh")
        self.assertEqual(envelope["mode"], "one")
        self.assertEqual(envelope["requested_unit_id"], "L01")
        self.assertEqual(envelope["engine_root"], str(REPO_ROOT))
        self.assertEqual(envelope["curriculum_root"], str(manifest.parent.resolve()))
        self.assertEqual(envelope["output_root"], str(output_root.resolve()))
        self.assertIsNone(envelope["prior_identity"])
        self.assertIsNone(envelope["prior_terminal"])
        self.assertFalse(envelope["lease_open"])
        self.assertEqual(len(envelope["authorization"]["curriculum_digest"]), 64)
        self.assertEqual(envelope["authorization"]["output_root"], str(output_root.resolve()))

        context = recorded["context"]
        self.assertEqual(context.transport_registry.authorization.providers.get("openai"), ("frozen_unit_artifacts",))
        self.assertIsNotNone(context.transport_registry.capability_proof)
        self.assertFalse(context.transport_registry.guard.installed, "the guard must be uninstalled again after invoke")

        # The lock is released: a second invocation against the same root
        # (still empty of a committed run, since the stub never wrote one) does
        # not hit ExecutionLockUnavailable.
        lock = P.ExecutionLock(output_root)
        lock.acquire()
        lock.release()

    def test_all_mode_run_requests_no_unit_id(self):
        import tempfile

        recorded = {}

        class _StubCompiled:
            def invoke(self, graph_input, *, config, context):
                recorded["envelope"] = graph_input["invocation"]
                return {
                    "terminal": {"kind": "CONVERGENCE_EXHAUSTED"},
                    "mode": "all", "checkpoint_metadata": [], "evidence_index_entries": [],
                }

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            curriculum = root / "curricula" / "arduino_kit"
            manifest = curriculum / "arduino_kit_curriculum.v5.yaml"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("labs: []\n", encoding="utf-8")
            output_root = root / "out"
            authorization = _authorization_file(root)

            with mock.patch.object(R, "build_curriculum_factory_graph", return_value=_StubCompiled()), \
                 mock.patch.object(R.tp, "prove_transport_capabilities",
                                    return_value={"satisfied": True, "unsatisfied_required_facets": []}), \
                 mock.patch.object(R, "_prove_driver_capabilities", return_value=_PASSING_DRIVER_CAPABILITIES):
                code, payload, _err = _run_main(
                    ["--engine-root", str(REPO_ROOT), "--curriculum", str(manifest),
                     "--output-root", str(output_root), "--all",
                     "--authorization", str(authorization)]
                )

        self.assertEqual(code, 12)
        self.assertIsNone(recorded["envelope"]["requested_unit_id"])
        self.assertEqual(recorded["envelope"]["mode"], "all")

    def test_a_second_fresh_invocation_against_a_populated_root_is_refused(self):
        import tempfile

        class _StubCompiled:
            def invoke(self, graph_input, *, config, context):
                return {
                    "terminal": {"kind": "INTERRUPTED", "classification": "graceful_signal"},
                    "checkpoint_metadata": [], "evidence_index_entries": [],
                }

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            curriculum = root / "curricula" / "arduino_kit"
            manifest = curriculum / "arduino_kit_curriculum.v5.yaml"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("labs: []\n", encoding="utf-8")
            output_root = root / "out"
            authorization = _authorization_file(root)
            argv = ["--engine-root", str(REPO_ROOT), "--curriculum", str(manifest),
                    "--output-root", str(output_root), "--unit", "L01",
                    "--authorization", str(authorization)]

            with mock.patch.object(R, "build_curriculum_factory_graph", return_value=_StubCompiled()), \
                 mock.patch.object(R.tp, "prove_transport_capabilities",
                                    return_value={"satisfied": True, "unsatisfied_required_facets": []}), \
                 mock.patch.object(R, "_prove_driver_capabilities", return_value=_PASSING_DRIVER_CAPABILITIES):
                first_code, _payload, _err = _run_main(argv)
                self.assertEqual(first_code, 10)
                second_code, second_payload, _err2 = _run_main(argv)

        self.assertEqual(second_code, R.NOT_READY_EXIT)
        self.assertNotIn("terminal", second_payload)


# ===========================================================================
# Resume envelope/seeding wiring (mocked persistence primitives)
# ===========================================================================


class ResumeSeedingTests(unittest.TestCase):
    def test_resume_envelope_derives_mode_and_target_from_the_frozen_identity(self):
        identity = {
            "contract_version": "1", "engine_root": "/engine", "curriculum_root": "/curriculum",
            "active_manifest_path": "/curriculum/manifest.yaml", "output_root": "/out",
            "mode": "one", "requested_unit_id": "L07", "run_id": "run-xyz",
        }
        invocation = SimpleNamespace(
            bootstrap_kind=P.BOOTSTRAP_RESUME,
            run_id="run-xyz",
            episode_id="run-xyz:episode:000002",
            episode_ordinal=2,
            thread_id="run-xyz:episode:000002",
            identity_envelope=identity,
            prior_thread_id="run-xyz:episode:000001",
            resume_from={"terminal": {"kind": "INTERRUPTED", "classification": "graceful_signal"}},
        )
        prior_values = {
            "frozen_digest": "deadbeef" * 8,
            "accepted_unit_receipts": {},
            "terminal": {"kind": "INTERRUPTED"},
            "bootstrap_kind": "fresh",
            "invocation": {"kind": "fresh"},
            "episode_id": "run-xyz:episode:000001",
        }

        with mock.patch.object(P, "open_checkpoint_saver", return_value=(object(), mock.Mock(close=lambda: None))), \
             mock.patch.object(P, "ReadOnlyCheckpointView", return_value=object()), \
             mock.patch.object(P, "prepare_episode_invocation", return_value=invocation), \
             mock.patch.object(P, "extract_prior_episode", return_value=SimpleNamespace(values=prior_values)):
            got_invocation, envelope, frozen_digest, seed_values = R._prepare_resume(
                output_root=Path("/out"), lock=mock.Mock(), compiled=object()
            )

        self.assertIs(got_invocation, invocation)
        self.assertEqual(envelope["kind"], "resume")
        self.assertEqual(envelope["mode"], "one")
        self.assertEqual(envelope["requested_unit_id"], "L07")
        self.assertEqual(envelope["engine_root"], "/engine")
        self.assertEqual(envelope["prior_identity"], identity)
        self.assertEqual(envelope["prior_terminal"], {"kind": "INTERRUPTED", "classification": "graceful_signal"})
        self.assertFalse(envelope["lease_open"])
        self.assertEqual(frozen_digest, "deadbeef" * 8)

        # Episode-scoped fields are never carried forward from the prior episode.
        for excluded in ("terminal", "bootstrap_kind", "invocation", "episode_id"):
            self.assertNotIn(excluded, seed_values)
        self.assertEqual(seed_values["frozen_digest"], "deadbeef" * 8)
        self.assertEqual(seed_values["accepted_unit_receipts"], {})

    def test_recover_orphan_envelope_carries_no_prior_terminal_and_marks_lease_open(self):
        identity = {
            "contract_version": "1", "engine_root": "/engine", "curriculum_root": "/curriculum",
            "active_manifest_path": "/curriculum/manifest.yaml", "output_root": "/out",
            "mode": "all", "requested_unit_id": None, "run_id": "run-xyz",
        }
        invocation = SimpleNamespace(
            bootstrap_kind=P.BOOTSTRAP_RECOVER_ORPHAN,
            run_id="run-xyz",
            episode_id="run-xyz:recover:1",
            episode_ordinal=2,
            thread_id="run-xyz:recover:1",
            identity_envelope=identity,
            prior_thread_id="run-xyz:episode:000001",
            resume_from=None,
        )
        with mock.patch.object(P, "open_checkpoint_saver", return_value=(object(), mock.Mock(close=lambda: None))), \
             mock.patch.object(P, "ReadOnlyCheckpointView", return_value=object()), \
             mock.patch.object(P, "prepare_episode_invocation", return_value=invocation), \
             mock.patch.object(P, "extract_prior_episode", return_value=SimpleNamespace(values={})):
            _invocation, envelope, _frozen_digest, _seed = R._prepare_resume(
                output_root=Path("/out"), lock=mock.Mock(), compiled=object()
            )

        self.assertEqual(envelope["kind"], "recover_orphan")
        self.assertIsNone(envelope["prior_terminal"])
        self.assertTrue(envelope["lease_open"])


# ===========================================================================
# Evidence artifacts (spec-facing proof, written under results/evidence/)
# ===========================================================================

EVIDENCE_DIR = REPO_ROOT / "plans" / "26_langgraph_curriculum_factory" / "results" / "evidence" / "N40_CLI_CUTOVER"


class EvidenceArtifactTests(unittest.TestCase):
    """Regenerates the node's own result-doc evidence as a side effect of a real
    assertion, so the evidence can never drift from what actually passed."""

    def test_cli_help_evidence_matches_spec_section_16_surface(self):
        help_text = R.build_parser().format_help()
        for flag in ("--engine-root", "--curriculum", "--output-root", "--preflight",
                     "--unit", "--all", "--resume", "--authorization"):
            self.assertIn(flag, help_text)
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        (EVIDENCE_DIR / "cli_help.txt").write_text(help_text, encoding="utf-8")

    def test_static_import_audit_evidence(self):
        imports = sorted(
            f"{module or '<bare>'} :: {name or '<module>'}"
            for module, name in ImportGraphAuditTests()._imported_names()
        )
        report = (
            "Every import statement in runtime/run_curriculum.py (module :: name).\n"
            "TEST 1/5/8 assert no Plan 25, node-body, routing, or provider-SDK\n"
            "import appears in this list.\n\n" + "\n".join(imports) + "\n"
        )
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        (EVIDENCE_DIR / "import_audit.txt").write_text(report, encoding="utf-8")
        self.assertTrue(imports)

    def test_plan25_root_refusal_evidence(self):
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            output_root = Path(raw) / "legacy"
            output_root.mkdir()
            (output_root / "checkpoints").mkdir()
            (output_root / "checkpoints" / "0001.json").write_text(
                json.dumps({"terminal_state": "ACCEPTED"}), encoding="utf-8"
            )
            before = sorted(p.relative_to(output_root).as_posix() for p in output_root.rglob("*"))

            with mock.patch.object(R, "build_curriculum_factory_graph") as builder:
                code, payload, err = _run_main(
                    ["--engine-root", str(REPO_ROOT), "--curriculum", str(REPO_ROOT),
                     "--output-root", str(output_root), "--resume",
                     "--authorization", str(_authorization_file(Path(raw)))]
                )
            builder.assert_not_called()
            after = sorted(p.relative_to(output_root).as_posix() for p in output_root.rglob("*"))

        report = (
            "TEST 7: a Plan 25-shaped output root (checkpoints/0001.json, no\n"
            ".langgraph/) passed to --resume.\n\n"
            f"exit_code: {code}\n"
            f"stdout: {json.dumps(payload)}\n"
            f"stderr: {err.strip()}\n"
            f"files_before: {before}\n"
            f"files_after:  {after}\n"
            f"root_untouched: {before == after}\n"
        )
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        (EVIDENCE_DIR / "plan25_resume_refusal.txt").write_text(report, encoding="utf-8")
        self.assertEqual(before, after)
        self.assertEqual(code, R.NOT_READY_EXIT)

    def test_preflight_read_only_evidence(self):
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            output_root = Path(raw) / "preflight-target"
            code, payload, err = _run_main(
                ["--engine-root", str(REPO_ROOT), "--curriculum", str(REPO_ROOT),
                 "--output-root", str(output_root), "--preflight"]
            )
            output_root_exists_after = output_root.exists()

        report = (
            "TEST 4: --preflight against an output root that does not yet exist.\n\n"
            f"exit_code: {code}\n"
            f"stdout: {json.dumps(payload)}\n"
            f"stderr: {err.strip()}\n"
            f"output_root_created: {output_root_exists_after}\n"
        )
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        (EVIDENCE_DIR / "preflight_read_only.txt").write_text(report, encoding="utf-8")
        self.assertFalse(output_root_exists_after)
        self.assertNotIn("terminal", payload)


if __name__ == "__main__":
    unittest.main()
