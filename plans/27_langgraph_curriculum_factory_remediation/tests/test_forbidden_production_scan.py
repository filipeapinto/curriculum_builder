"""Scope and policy of the forbidden production-reference scanner.

The scanner is driven entirely by the graph's declared scopes. These tests build
synthetic repositories so that both a clean tree and a dirty tree are proven,
and they assert the negative scope explicitly: Plan 26 history, plan
scaffolding, generated outputs, and test sources are never read by the
production scope.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

TESTS_DIR = Path(__file__).resolve().parent
PLAN_DIR = TESTS_DIR.parent
REPO_ROOT = PLAN_DIR.parents[1]
CONTROLLER_DIR = PLAN_DIR / "controller"
REAL_GRAPH = PLAN_DIR / "implementation.graph.v1.yaml"
SCANNER = CONTROLLER_DIR / "check_forbidden_production_refs.py"

if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

import check_forbidden_production_refs as scanner  # noqa: E402
from core import ControllerError, Graph  # noqa: E402


CLEAN_TRANSPORT = '''"""Subscription CLI transport."""

FORBIDDEN_CREDENTIAL_NAMES = (
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
)


def assert_no_api_key_is_present(environment):
    """Refuse to run when any API credential is present at all."""

    present = [name for name in FORBIDDEN_CREDENTIAL_NAMES if name in environment]
    if present:
        raise RuntimeError(f"credential authentication is not authorized: {present}")


def build_argv(model, instruction):
    return ["codex", "exec", "-m", model, instruction]
'''

CLEAN_CLI = '''"""Production entry point."""

from transport import assert_no_api_key_is_present


def main(environment):
    assert_no_api_key_is_present(environment)
    return 0
'''


class FakeRepo:
    def __init__(self, root: Path) -> None:
        self.repo = root / "repo"
        self.graph_path = self.repo / "graph.yaml"
        (self.repo / "runtime/langgraph_factory").mkdir(parents=True, exist_ok=True)
        (self.repo / "policy").mkdir(parents=True, exist_ok=True)
        (self.repo / "tests/runtime").mkdir(parents=True, exist_ok=True)
        (self.repo / "plans/26_history").mkdir(parents=True, exist_ok=True)
        (self.repo / "outputs/run26").mkdir(parents=True, exist_ok=True)
        self.write("runtime/langgraph_factory/transport.py", CLEAN_TRANSPORT)
        self.write("runtime/run_curriculum.py", CLEAN_CLI)
        self.write("policy/routes.v1.yaml", "routes:\n  - job: M01\n    cli: codex\n")
        self.write("tests/runtime/test_transport.py", "def test_transport():\n    assert True\n")
        # Deliberate out-of-scope contamination: the scanner must never see these.
        self.write("plans/26_history/postmortem.md", "the old run dispatched to gemini\n")
        self.write("outputs/run26/log.txt", "GEMINI_API_KEY=abc123\n")
        self.write("runtime/langgraph_factory/__pycache__/transport.cpython-313.pyc", "gemini\n")
        self.write_graph()

    def write(self, relative: str, text: str) -> Path:
        target = self.repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target

    def graph_document(self) -> dict[str, Any]:
        return {
            "graph_id": "fake",
            "version": 1,
            "source_spec": "spec.md",
            "node_result_schema": "schema.json",
            "entry": "N00_SPEC_APPROVAL_GATE",
            "result_pattern": "results/{node_id}.json",
            "nodes": {},
            "edges": [],
            "terminals": {},
            "rules": {
                "forbidden_production_scan": {
                    "scan_roots": [
                        "runtime/langgraph_factory",
                        "runtime/run_curriculum.py",
                        "policy/routes.v1.yaml",
                    ],
                    "excluded_globs": ["**/__pycache__/**", "**/*.pyc"],
                    "excluded_roots": ["plans", "tests", "outputs"],
                    "prohibited_dispatch_or_import_terms": ["gemini", "google.generativeai"],
                    "prohibited_credential_names": [
                        "GEMINI_API_KEY",
                        "GOOGLE_API_KEY",
                        "OPENAI_API_KEY",
                        "ANTHROPIC_API_KEY",
                    ],
                    "credential_absence_guard_paths": [
                        "runtime/run_curriculum.py",
                        "runtime/langgraph_factory/transport.py",
                    ],
                    "credential_occurrence_policy": "guards only",
                },
                "retired_provider_test_scan": {
                    "scan_roots": ["tests/runtime"],
                    "excluded_globs": ["**/__pycache__/**", "**/*.pyc"],
                    "prohibited_terms": ["gemini", "google", "GEMINI_API_KEY", "GOOGLE_API_KEY"],
                    "occurrence_policy": "zero_occurrences_in_active_test_source",
                },
            },
        }

    def write_graph(self, document: dict[str, Any] | None = None) -> None:
        self.graph_path.write_text(
            yaml.safe_dump(document or self.graph_document(), sort_keys=True), encoding="utf-8"
        )

    def graph(self) -> Graph:
        return Graph.load(self.graph_path, self.repo)

    def scan(self, scope: str = "all") -> dict[str, Any]:
        return scanner.run(self.graph(), scope)

    def cli(self, *argv: str) -> tuple[int, dict[str, Any]]:
        process = subprocess.run(
            [
                sys.executable,
                str(SCANNER),
                "--graph",
                str(self.graph_path),
                "--repo-root",
                str(self.repo),
                *argv,
            ],
            capture_output=True,
            text=True,
        )
        return process.returncode, json.loads(process.stdout.strip().splitlines()[-1])


@pytest.fixture()
def repo(tmp_path: Path) -> FakeRepo:
    return FakeRepo(tmp_path)


# --------------------------------------------------------------- clean tree


def test_a_clean_tree_passes_both_scopes(repo: FakeRepo) -> None:
    report = repo.scan()
    assert report["valid"], report["violations"]
    code, payload = repo.cli()
    assert code == 0 and payload["ok"]


def test_the_production_scope_never_reads_plans_tests_outputs_or_bytecode(repo: FakeRepo) -> None:
    production = repo.scan("production")["scopes"][0]
    scanned = set(production["scanned_files"])
    assert scanned == {
        "policy/routes.v1.yaml",
        "runtime/langgraph_factory/transport.py",
        "runtime/run_curriculum.py",
    }
    assert not any(item.startswith(("plans/", "tests/", "outputs/")) for item in scanned)
    assert not any("__pycache__" in item for item in scanned)
    assert production["excluded_roots"] == ["plans", "tests", "outputs"]


def test_contamination_outside_the_scan_roots_is_invisible(repo: FakeRepo) -> None:
    repo.write("plans/26_history/controller.py", "CLI = 'gemini'\nKEY = 'GEMINI_API_KEY'\n")
    repo.write("outputs/run26/manifest.json", '{"provider": "gemini"}\n')
    assert repo.scan("production")["valid"]


# ------------------------------------------------- prohibited dispatch terms


@pytest.mark.parametrize(
    "line",
    [
        'CLI = "gemini"',
        "import google.generativeai as genai",
        "from google.generativeai import configure",
        '    argv = ["Gemini", "-m", model]',
        "# fall back to gemini when codex is unavailable",
    ],
)
def test_any_occurrence_of_a_prohibited_provider_term_is_a_violation(
    repo: FakeRepo, line: str
) -> None:
    repo.write("runtime/langgraph_factory/transport.py", CLEAN_TRANSPORT + line + "\n")
    report = repo.scan("production")
    assert not report["valid"]
    assert {item["code"] for item in report["violations"]} == {"PROHIBITED_PROVIDER_TERM"}
    assert report["violations"][0]["path"] == "runtime/langgraph_factory/transport.py"


def test_a_prohibited_term_in_a_scanned_policy_file_is_a_violation(repo: FakeRepo) -> None:
    repo.write("policy/routes.v1.yaml", "routes:\n  - job: M05\n    cli: gemini\n")
    code, payload = repo.cli()
    assert code == 1
    assert payload["violations"][0]["path"] == "policy/routes.v1.yaml"
    assert payload["violations"][0]["line"] == 3


# ------------------------------------------------------ credential policy


def test_a_credential_name_is_legal_only_inside_an_absence_guard(repo: FakeRepo) -> None:
    assert repo.scan("production")["valid"]

    repo.write(
        "runtime/langgraph_factory/transport.py",
        CLEAN_TRANSPORT
        + '\n\ndef build_headers(environment):\n'
        '    return {"Authorization": environment["OPENAI_API_KEY"]}\n',
    )
    report = repo.scan("production")
    assert not report["valid"]
    violation = report["violations"][0]
    assert violation["code"] == "CREDENTIAL_OUTSIDE_GUARD_REGION"
    assert violation["term"] == "OPENAI_API_KEY"


def test_a_credential_name_outside_a_declared_guard_file_is_a_violation(repo: FakeRepo) -> None:
    repo.write(
        "runtime/langgraph_factory/model_nodes.py",
        'def configure():\n    return {"key": "ANTHROPIC_API_KEY"}\n',
    )
    report = repo.scan("production")
    assert not report["valid"]
    assert {item["code"] for item in report["violations"]} == {"CREDENTIAL_OUTSIDE_GUARD_FILE"}


def test_a_credential_named_outside_a_guard_region_is_a_violation_even_in_a_comment(
    repo: FakeRepo,
) -> None:
    repo.write(
        "runtime/run_curriculum.py",
        CLEAN_CLI + "\n\n# GEMINI_API_KEY is never read by this process\n",
    )
    report = repo.scan("production")
    assert not report["valid"]
    assert {item["code"] for item in report["violations"]} == {
        "CREDENTIAL_OUTSIDE_GUARD_REGION",
        "PROHIBITED_PROVIDER_TERM",
    }

    repo.write(
        "runtime/run_curriculum.py",
        CLEAN_CLI + '\n\ndef fallback(environment):\n    return environment.get("GEMINI_API_KEY")\n',
    )
    report = repo.scan("production")
    assert not report["valid"]
    assert "CREDENTIAL_OUTSIDE_GUARD_REGION" in {item["code"] for item in report["violations"]}


def test_a_denial_named_helper_may_reference_every_credential(repo: FakeRepo) -> None:
    repo.write(
        "runtime/run_curriculum.py",
        CLEAN_CLI
        + '\n\ndef reject_configured_credentials(environment):\n'
        '    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY"):\n'
        "        if name in environment:\n"
        '            raise SystemExit(f"{name} must not be configured")\n',
    )
    assert repo.scan("production")["valid"]


# ------------------------------------------------ retired provider test scope


def test_the_test_scope_enforces_zero_occurrences_in_active_test_source(repo: FakeRepo) -> None:
    assert repo.scan("tests")["valid"]
    repo.write(
        "tests/runtime/test_transport.py",
        "from runtime.gemini import resolve_alias\n\n\ndef test_alias():\n    assert resolve_alias\n",
    )
    report = repo.scan("tests")
    assert not report["valid"]
    assert {item["code"] for item in report["violations"]} == {
        "RETIRED_PROVIDER_TERM_IN_ACTIVE_TEST"
    }


def test_the_production_scope_alone_ignores_retired_test_references(repo: FakeRepo) -> None:
    repo.write("tests/runtime/test_transport.py", "GEMINI_API_KEY = 'x'\nimport gemini\n")
    assert repo.scan("production")["valid"]
    assert not repo.scan("tests")["valid"]
    assert not repo.scan("all")["valid"]


def test_bytecode_and_pycache_are_excluded_from_the_test_scope(repo: FakeRepo) -> None:
    repo.write("tests/runtime/__pycache__/test_transport.cpython-313.pyc", "gemini\n")
    repo.write("tests/runtime/legacy.pyc", "gemini\n")
    assert repo.scan("tests")["valid"]


# ------------------------------------------------------------ scope guards


def test_a_scan_root_under_an_excluded_root_is_rejected(repo: FakeRepo) -> None:
    document = repo.graph_document()
    document["rules"]["forbidden_production_scan"]["scan_roots"] = ["tests/runtime"]
    repo.write_graph(document)
    with pytest.raises(ControllerError) as error:
        repo.scan("production")
    assert error.value.code == "BAD_SCAN_SCOPE"


def test_a_missing_scan_scope_is_reported_not_silently_skipped(repo: FakeRepo) -> None:
    document = repo.graph_document()
    document["rules"].pop("forbidden_production_scan")
    repo.write_graph(document)
    code, payload = repo.cli("--scope", "production")
    assert code == 1 and payload["code"] == "MISSING_SCAN_SCOPE"


def test_an_unsupported_occurrence_policy_is_rejected(repo: FakeRepo) -> None:
    document = repo.graph_document()
    document["rules"]["retired_provider_test_scan"]["occurrence_policy"] = "best_effort"
    repo.write_graph(document)
    with pytest.raises(ControllerError) as error:
        repo.scan("tests")
    assert error.value.code == "BAD_SCAN_SCOPE"


@pytest.mark.parametrize(
    "pattern,candidate,expected",
    [
        ("**/__pycache__/**", "runtime/a/__pycache__/b.pyc", True),
        ("**/__pycache__/**", "runtime/a/b.py", False),
        ("**/*.pyc", "runtime/a/b.pyc", True),
        ("**/*.pyc", "runtime/a/b.py", False),
    ],
)
def test_exclusion_globs_match_as_declared(pattern: str, candidate: str, expected: bool) -> None:
    assert bool(scanner.glob_to_regex(pattern).match(candidate)) is expected


# ------------------------------------------------------- the real Plan 27 graph


def test_the_real_graph_scopes_load_and_name_the_expected_policy() -> None:
    graph = Graph.load(REAL_GRAPH, REPO_ROOT)
    production = graph.rules["forbidden_production_scan"]
    assert production["excluded_roots"] == ["plans", "tests", "outputs"]
    assert production["prohibited_dispatch_or_import_terms"] == ["gemini", "google.generativeai"]
    assert set(production["credential_absence_guard_paths"]) <= set(production["scan_roots"]) | {
        "runtime/run_curriculum.py",
        "runtime/langgraph_factory/transport.py",
    }
    assert (
        graph.rules["retired_provider_test_scan"]["occurrence_policy"]
        == "zero_occurrences_in_active_test_source"
    )


def test_the_scanner_reports_the_current_repository_debt_precisely() -> None:
    """N20 and N30 have not run yet, so the live tree must still be dirty and the
    scanner must say exactly where, rather than passing vacuously."""

    graph = Graph.load(REAL_GRAPH, REPO_ROOT)
    report = scanner.run(graph, "production")
    assert not report["valid"], "a vacuous pass here would mean the scanner reads nothing"
    paths = {item["path"] for item in report["violations"]}
    assert "runtime/langgraph_factory/transport.py" in paths
    assert all(not item.startswith(("plans/", "tests/", "outputs/")) for item in paths)
    assert {item["code"] for item in report["violations"]} == {"PROHIBITED_PROVIDER_TERM"}
