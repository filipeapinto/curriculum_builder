"""Required tests for execution package v2 (n20_recovery.plan.v2.md, Phase D).

These prove, in order: Phase A's restored v1 bytes and N10 result are intact;
this package's node-scoped scanner genuinely binds to this package's own
graph rather than silently falling back to the parent v1 package's graph
(the exact class of defect independent QA found in this package's failed
predecessor, ``implementation.graph.v2.yaml``'s ``PKG-QA-001`` finding); the
scanner's node-mode narrowing is a real intersection, not a reimplementation
that could quietly weaken a rule; the graph's structural corrections (N60
alone in complete-tree mode, no overlapping write ownership); and that
authoring this package touched no production or active-test file.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema
import pytest
import yaml

TESTS_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = TESTS_DIR.parent
PLAN_DIR = PACKAGE_DIR.parent
REPO_ROOT = PLAN_DIR.parents[1]

PACKAGE_CONTROLLER_DIR = PACKAGE_DIR / "controller"
PACKAGE_TOOLS_DIR = PACKAGE_DIR / "tools"
PARENT_CONTROLLER_DIR = PLAN_DIR / "controller"
PARENT_TOOLS_DIR = PLAN_DIR / "tools"
PARENT_GRAPH = PLAN_DIR / "implementation.graph.v1.yaml"

PACKAGE_GRAPH = PACKAGE_DIR / "implementation.graph.v8.yaml"
APPROVED_GRAPH_V7 = PACKAGE_DIR / "implementation.graph.v7.yaml"
RECOVERY_GRAPH_V7_MODIFIED = PACKAGE_DIR / "recovery/implementation.graph.v7.modified.b6c17e81.yaml"
DEPRECATED_GRAPH_V4 = PACKAGE_DIR / "deprecated/implementation.graph.v4.yaml"
DEPRECATED_GRAPH_V5 = PACKAGE_DIR / "deprecated/implementation.graph.v5.yaml"
DEPRECATED_GRAPH_V6 = PACKAGE_DIR / "deprecated/implementation.graph.v6.yaml"
CONTRACT_SCHEMA_V2 = PACKAGE_DIR / "schemas/spec_approval.schema.v2.json"
CONTRACT_V2 = PACKAGE_DIR / "contracts/spec_approval.v2.yaml"
CONTRACT_SCHEMA_V3 = PACKAGE_DIR / "schemas/spec_approval.schema.v3.json"
CONTRACT_V3 = PACKAGE_DIR / "contracts/spec_approval.v3.yaml"
CONTRACT_SCHEMA_V5 = PACKAGE_DIR / "schemas/spec_approval.schema.v5.json"
CONTRACT_V5 = PACKAGE_DIR / "contracts/spec_approval.v5.yaml"
PARENT_APPROVAL_SCHEMA_V1 = PLAN_DIR / "schemas/spec_approval.schema.v1.json"
RESULTS_V8_PREFIX = "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/"
LEGACY_RESULTS_PREFIX = "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/"
SCAN_NODE = PACKAGE_CONTROLLER_DIR / "scan_node.py"
VALIDATE_PLAN_V2 = PACKAGE_TOOLS_DIR / "validate_plan_v2.py"
VALIDATE_RESULT_V2 = PACKAGE_TOOLS_DIR / "validate_result_v2.py"
PACKAGE_PROMPTS_DIR = PACKAGE_DIR / "prompts"

for _dir in (str(PACKAGE_CONTROLLER_DIR), str(PARENT_CONTROLLER_DIR), str(PACKAGE_TOOLS_DIR)):
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

import scan_node as scanner  # noqa: E402
from core import Graph  # noqa: E402
import validate_plan_v2  # noqa: E402


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run(argv: list[str]) -> tuple[int, dict[str, Any]]:
    process = subprocess.run(
        [sys.executable, *argv], cwd=REPO_ROOT, capture_output=True, text=True
    )
    return process.returncode, json.loads(process.stdout.strip())


# ------------------------------------------------ Phase A restoration proof


PHASE_A_HASHES = [
    (
        PARENT_CONTROLLER_DIR / "check_forbidden_production_refs.py",
        "cb530b326bb68964976b5b074fefa43392af83bd5c3c6a76f744991d30b066ee",
    ),
    (
        PARENT_TOOLS_DIR / "validate_plan.py",
        "9f534ba3597d331c6ba6c64551004bf01044fb221298aaccd914d476cdf396d0",
    ),
    (
        PARENT_TOOLS_DIR / "validate_result.py",
        "0beef6ed7c5f7bbba3adf50818c53d86dd5cff1f5cefd2abbd8c629a8f229cec",
    ),
]


@pytest.mark.parametrize("path,expected", PHASE_A_HASHES, ids=[p.name for p, _ in PHASE_A_HASHES])
def test_phase_a_v1_files_retain_their_admitted_hash(path: Path, expected: str) -> None:
    assert sha256_file(path) == expected


def test_original_n10_result_failure_is_proven_pre_existing_at_head() -> None:
    code, payload = run([str(PARENT_TOOLS_DIR / "validate_result.py"), "--node", "N10_HARNESS_PROTOCOL"])
    assert code == 1
    assert payload["valid"] is False
    assert payload["error"] == (
        "N10_HARNESS_PROTOCOL: changed-file hash mismatch: "
        "plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py"
    )
    relative = "plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py"
    head_bytes = subprocess.run(
        ["git", "show", f"HEAD:{relative}"], cwd=REPO_ROOT, capture_output=True, check=True
    ).stdout
    assert hashlib.sha256(head_bytes).hexdigest() == sha256_file(REPO_ROOT / relative)
    assert sha256_file(REPO_ROOT / relative) == "9ce7fe5b187620968ce289f73bbfc48a38ed1262386c25dc15116d0d8b3b2436"


# --------------------------------------------- package-v2 graph binding proof


def test_node_scoped_scan_defaults_to_the_package_v2_graph_not_the_parent() -> None:
    code, payload = run([str(SCAN_NODE), "--node", "N20_PROVIDER_TRANSPORT", "--json"])
    assert payload["graph_sha256"] == sha256_file(PACKAGE_GRAPH)
    assert payload["graph_sha256"] != sha256_file(PARENT_GRAPH)


def test_using_the_wrong_parent_graph_explicitly_excludes_n20s_new_egress_ownership() -> None:
    """PKG-QA-001 was exactly this: a node-scoped scan bound to the wrong graph
    silently used stale write sets. Proving the *wrong* binding produces a
    visibly different (and wrong) result confirms the scanner is genuinely
    graph-sensitive, not accidentally graph-invariant."""

    code, payload = run(
        [str(SCAN_NODE), "--node", "N20_PROVIDER_TRANSPORT", "--graph", str(PARENT_GRAPH), "--json"]
    )
    scanned = {item for scope in payload["scopes"] for item in scope["scanned_files"]}
    assert "runtime/langgraph_factory/egress.py" not in scanned


# ---------------------------------------- node-mode intersection, real graph


def test_n20_node_mode_includes_its_newly_owned_egress_module_and_test() -> None:
    """This is the exact real command that reached BLOCKED under graph v5
    (finding N20V2-F01): scan_node.py --node N20_PROVIDER_TRANSPORT --graph
    implementation.graph.v8.yaml (v6 originally fixed this; v7 carries the
    fix forward unchanged, correcting only the unrelated result-namespace
    collision documented in its own header). PKGV2-T22(a) requires dedicated
    proof that it now passes with zero violations, not merely that it scans
    the right file scope."""

    code, payload = run(
        [str(SCAN_NODE), "--node", "N20_PROVIDER_TRANSPORT", "--graph", str(PACKAGE_GRAPH), "--json"]
    )
    assert code == 0
    assert payload["ok"] is True
    assert payload["valid"] is True
    assert payload["violations"] == []
    scanned = {item for scope in payload["scopes"] for item in scope["scanned_files"]}
    assert "runtime/langgraph_factory/egress.py" in scanned
    assert "tests/runtime/test_plan26_egress.py" in scanned


def test_n20_node_mode_ignores_a_later_nodes_owned_file() -> None:
    code, payload = run(
        [str(SCAN_NODE), "--node", "N20_PROVIDER_TRANSPORT", "--graph", str(PACKAGE_GRAPH), "--json"]
    )
    scanned = {item for scope in payload["scopes"] for item in scope["scanned_files"]}
    # runtime/run_curriculum.py is owned by N30_PREFLIGHT_EGRESS, a later node.
    assert "runtime/run_curriculum.py" not in scanned


def test_n30_node_mode_excludes_the_egress_module_it_only_reads() -> None:
    code, payload = run(
        [str(SCAN_NODE), "--node", "N30_PREFLIGHT_EGRESS", "--graph", str(PACKAGE_GRAPH), "--json"]
    )
    scanned = {item for scope in payload["scopes"] for item in scope["scanned_files"]}
    assert "runtime/langgraph_factory/egress.py" not in scanned


def test_complete_tree_mode_against_the_real_repo_is_clean_after_n60() -> None:
    graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
    report = scanner.run_complete_tree(graph)
    assert report["valid"]
    assert report["violations"] == []


# ------------------------------------------- seeded violations, synthetic tree


class FakePackageRepo:
    """A minimal synthetic tree with two nodes owning disjoint files, so a
    seeded violation's node-mode/complete-tree-mode visibility can be proven
    without touching the real repository."""

    def __init__(self, root: Path) -> None:
        self.repo = root / "repo"
        self.graph_path = self.repo / "graph.yaml"
        (self.repo / "runtime/langgraph_factory").mkdir(parents=True, exist_ok=True)
        (self.repo / "tests/runtime").mkdir(parents=True, exist_ok=True)
        self.write("runtime/langgraph_factory/transport.py", "CLI = 'codex'\n")
        self.write("runtime/run_curriculum.py", "def main():\n    return 0\n")
        self.write_graph()

    def write(self, relative: str, text: str) -> Path:
        target = self.repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target

    def graph_document(self) -> dict[str, Any]:
        return {
            "graph_id": "fake",
            "version": 2,
            "source_spec": "spec.md",
            "node_result_schema": "schema.json",
            "entry": "N_EARLY",
            "result_pattern": "results/{node_id}.json",
            "nodes": {
                "N_EARLY": {"writes": ["runtime/langgraph_factory/transport.py"]},
                "N_LATE": {"writes": ["runtime/run_curriculum.py"]},
            },
            "edges": [],
            "terminals": {},
            "rules": {
                "forbidden_production_scan": {
                    "scan_roots": ["runtime/langgraph_factory", "runtime/run_curriculum.py"],
                    "excluded_globs": ["**/__pycache__/**", "**/*.pyc"],
                    "excluded_roots": ["plans", "tests", "outputs"],
                    "prohibited_dispatch_or_import_terms": ["gemini", "google.generativeai"],
                    "prohibited_credential_names": [
                        "GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
                    ],
                    "credential_absence_guard_paths": [],
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

    def write_graph(self) -> None:
        self.graph_path.write_text(yaml.safe_dump(self.graph_document(), sort_keys=True), encoding="utf-8")

    def graph(self) -> Graph:
        return Graph.load(self.graph_path, self.repo)


@pytest.fixture()
def package_repo(tmp_path: Path) -> FakePackageRepo:
    return FakePackageRepo(tmp_path)


def test_a_seeded_violation_in_an_early_owned_file_fails_only_that_node(package_repo: FakePackageRepo) -> None:
    package_repo.write("runtime/langgraph_factory/transport.py", "CLI = 'gemini'\n")
    graph = package_repo.graph()

    early_report = scanner.run_node(graph, "N_EARLY")
    assert not early_report["valid"]
    assert {item["path"] for item in early_report["violations"]} == {"runtime/langgraph_factory/transport.py"}

    late_report = scanner.run_node(graph, "N_LATE")
    assert late_report["valid"]


def test_the_seeded_violation_and_a_later_violation_both_fail_complete_tree_mode(
    package_repo: FakePackageRepo,
) -> None:
    package_repo.write("runtime/langgraph_factory/transport.py", "CLI = 'gemini'\n")
    package_repo.write("runtime/run_curriculum.py", "def main():\n    return 'gemini'\n")
    graph = package_repo.graph()

    report = scanner.run_complete_tree(graph)
    assert not report["valid"]
    paths = {item["path"] for item in report["violations"]}
    assert "runtime/langgraph_factory/transport.py" in paths
    assert "runtime/run_curriculum.py" in paths


# ------------------------------------------------------ graph shape proofs


def test_n60_is_the_only_node_using_complete_tree_mode() -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    complete_tree_nodes = [
        node_id
        for node_id, node in document["nodes"].items()
        for command in node["verification"]
        if len(command) > 1 and command[1] == scan_node_relative and "--node" not in command
    ]
    assert complete_tree_nodes == ["N60_ADVERSARIAL_REGRESSION"]


# ------------------------------------------------- PKGV2-QA-001: exact args


NODE_SCOPED_SCAN_NODES = [
    "N20_PROVIDER_TRANSPORT",
    "N30_PREFLIGHT_EGRESS",
    "N40_INTEGRATION_OWNERSHIP",
    "N50_EVIDENCE_AUDIT_CONTROLS",
]


def _node_scoped_scan_commands(node: dict[str, Any], scan_node_relative: str) -> list[list[str]]:
    return [
        command
        for command in node["verification"]
        if len(command) > 1 and command[1] == scan_node_relative and "--node" in command
    ]


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_each_n20_to_n50_scan_command_carries_its_own_exact_node_id(node_id: str) -> None:
    """PKGV2-QA-001: presence of a --node flag is not proof it names the right
    node -- a command could carry another node's ID and still satisfy a
    presence-only check. Assert the value itself."""

    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    commands = _node_scoped_scan_commands(document["nodes"][node_id], scan_node_relative)
    assert commands, f"{node_id}: no node-scoped scan_node.py command found"
    for command in commands:
        assert command[command.index("--node") + 1] == node_id


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_each_n20_to_n50_scan_command_carries_the_exact_package_v2_graph(node_id: str) -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    expected_graph = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    commands = _node_scoped_scan_commands(document["nodes"][node_id], scan_node_relative)
    assert commands, f"{node_id}: no node-scoped scan_node.py command found"
    for command in commands:
        assert command[command.index("--graph") + 1] == expected_graph


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_each_n20_to_n50_node_owns_its_own_exact_result_path_and_evidence_root(node_id: str) -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    writes = document["nodes"][node_id]["writes"]
    prefix = RESULTS_V8_PREFIX
    assert f"{prefix}{node_id}.result.v1.json" in writes
    assert f"{prefix}evidence/{node_id}" in writes
    for write in writes:
        if "/results/" in write:
            assert write.startswith(prefix), f"{node_id}: {write!r} is not under the package-v2 graph-v7 results root"


def test_n60_whole_tree_exception_is_exactly_n60_and_no_other_node() -> None:
    """Complements test_n60_is_the_only_node_using_complete_tree_mode by also
    proving no N20-N50 node was mutated into the whole-tree exception -- i.e.
    every node-scoped node still carries --node."""

    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    for node_id in NODE_SCOPED_SCAN_NODES:
        commands = [
            command
            for command in document["nodes"][node_id]["verification"]
            if len(command) > 1 and command[1] == scan_node_relative
        ]
        assert commands
        for command in commands:
            assert "--node" in command, f"{node_id} must not use whole-tree mode"
    n60_commands = [
        command
        for command in document["nodes"]["N60_ADVERSARIAL_REGRESSION"]["verification"]
        if len(command) > 1 and command[1] == scan_node_relative
    ]
    assert n60_commands
    assert all("--node" not in command for command in n60_commands)


# --------------------------------------- PKGV2-QA-001: validator mutation proofs


def test_validator_rejects_a_node_scoped_scan_command_whose_node_argument_names_another_node() -> None:
    """PKGV2-QA-001's exact trigger: swap N20's --node value for another
    node's ID and confirm the validator now rejects the graph, not just
    documents that it should."""

    module = _load_module("validate_plan_v2_node_swap_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node = document["nodes"]["N20_PROVIDER_TRANSPORT"]
    rewritten = []
    for command in node["verification"]:
        if len(command) > 1 and command[1] == scan_node_relative and "--node" in command:
            command = list(command)
            command[command.index("--node") + 1] = "N30_PREFLIGHT_EGRESS"
        rewritten.append(command)
    node["verification"] = rewritten
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validator_rejects_a_node_scoped_scan_command_bound_to_the_parent_v1_graph_value() -> None:
    """PKGV2-QA-001's other half: swap --graph's *value* to the parent v1
    graph path (rather than removing the flag entirely, which the round-1
    validator already caught) and confirm the validator rejects it."""

    module = _load_module("validate_plan_v2_graph_swap_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    parent_graph_relative = PARENT_GRAPH.relative_to(REPO_ROOT).as_posix()
    node = document["nodes"]["N30_PREFLIGHT_EGRESS"]
    rewritten = []
    for command in node["verification"]:
        if len(command) > 1 and command[1] == scan_node_relative and "--node" in command:
            command = list(command)
            command[command.index("--graph") + 1] = parent_graph_relative
        rewritten.append(command)
    node["verification"] = rewritten
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validator_rejects_a_node_result_write_moved_to_the_parent_v1_results_root() -> None:
    """PKGV2-QA-001's result/evidence half: move a node's result write back
    to the parent package's results/ root and confirm rejection."""

    module = _load_module("validate_plan_v2_result_path_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    node = document["nodes"]["N40_INTEGRATION_OWNERSHIP"]
    package_result = f"{RESULTS_V8_PREFIX}N40_INTEGRATION_OWNERSHIP.result.v1.json"
    parent_result = (
        "plans/27_langgraph_curriculum_factory_remediation/"
        "results/N40_INTEGRATION_OWNERSHIP.result.v1.json"
    )
    assert package_result in node["writes"]
    node["writes"] = [parent_result if item == package_result else item for item in node["writes"]]
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validator_rejects_an_evidence_root_moved_to_the_parent_v1_results_root() -> None:
    module = _load_module("validate_plan_v2_evidence_path_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    node = document["nodes"]["N50_EVIDENCE_AUDIT_CONTROLS"]
    package_evidence = f"{RESULTS_V8_PREFIX}evidence/N50_EVIDENCE_AUDIT_CONTROLS"
    parent_evidence = (
        "plans/27_langgraph_curriculum_factory_remediation/"
        "results/evidence/N50_EVIDENCE_AUDIT_CONTROLS"
    )
    assert package_evidence in node["writes"]
    node["writes"] = [parent_evidence if item == package_evidence else item for item in node["writes"]]
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validator_rejects_a_second_node_using_whole_tree_scan_mode() -> None:
    """Proves the N60 whole-tree exception is exact: giving N50 an
    additional bare (no --node) scan_node.py invocation, alongside its
    correct node-scoped one, must be rejected even though N50 still also
    carries a valid --node command."""

    module = _load_module("validate_plan_v2_second_whole_tree_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    graph_flag = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    node = document["nodes"]["N50_EVIDENCE_AUDIT_CONTROLS"]
    node["verification"] = list(node["verification"]) + [
        ["python3", scan_node_relative, "--graph", graph_flag]
    ]
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validate_plan_v2_passes_and_thereby_proves_no_write_path_overlaps() -> None:
    code, payload = run([str(VALIDATE_PLAN_V2)])
    assert code == 0
    assert payload["valid"] is True


def test_validator_rejects_a_node_scoped_scan_missing_the_explicit_graph_binding() -> None:
    """Direct proof that the PKG-QA-001 defect class is now caught, not just
    absent by convention: strip --graph from N20's scan command and require
    the validator to refuse the graph."""

    module = _load_module("validate_plan_v2_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node = document["nodes"]["N20_PROVIDER_TRANSPORT"]
    rewritten = []
    for command in node["verification"]:
        if len(command) > 1 and command[1] == scan_node_relative and "--node" in command:
            index = command.index("--graph")
            command = command[:index] + command[index + 2 :]
        rewritten.append(command)
    node["verification"] = rewritten
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validator_rejects_egress_ownership_outside_n20() -> None:
    module = _load_module("validate_plan_v2_ownership_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    egress = "runtime/langgraph_factory/egress.py"
    document["nodes"]["N20_PROVIDER_TRANSPORT"]["writes"].remove(egress)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validate_result_v2_entry_point_is_wired_to_this_package_and_reports_honestly() -> None:
    """N30_PREFLIGHT_EGRESS has not executed under this package (N00, N10,
    and N20 are already admitted), so this proves the tool is correctly wired
    to this package's own graph/result root without fabricating a result
    artifact."""

    code, payload = run([str(VALIDATE_RESULT_V2), "--node", "N30_PREFLIGHT_EGRESS"])
    assert code == 1
    assert payload["valid"] is False
    assert "missing result" in payload["error"]


# --------------------------------------- PKGV2-QA-002: exact occurrence counts


def _scan_node_command(node: dict[str, Any], scan_node_relative: str) -> list[str]:
    """The single scan_node.py invocation on this node (every node in this
    graph has exactly one)."""

    commands = [
        command
        for command in node["verification"]
        if len(command) > 1 and command[1] == scan_node_relative
    ]
    assert len(commands) == 1
    return list(commands[0])


def _replace_scan_command(
    document: dict[str, Any], node_id: str, scan_node_relative: str, new_command: list[str]
) -> None:
    node = document["nodes"][node_id]
    rewritten = []
    replaced = False
    for command in node["verification"]:
        if len(command) > 1 and command[1] == scan_node_relative and not replaced:
            rewritten.append(new_command)
            replaced = True
        else:
            rewritten.append(command)
    assert replaced
    node["verification"] = rewritten


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_exactly_one_of_each_flag_is_accepted(node_id: str) -> None:
    """Positive control: the package's own unmodified graph carries exactly
    one --node and one --graph occurrence per node-scoped command, and must
    validate without error."""

    module = _load_module(f"validate_plan_v2_baseline_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    module.validate_graph(document)  # must not raise


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_missing_node_flag_is_rejected(node_id: str) -> None:
    module = _load_module(f"validate_plan_v2_zero_node_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative)
    index = command.index("--node")
    del command[index : index + 2]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_missing_graph_flag_is_rejected(node_id: str) -> None:
    module = _load_module(f"validate_plan_v2_zero_graph_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative)
    index = command.index("--graph")
    del command[index : index + 2]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_duplicate_node_flag_same_value_is_rejected(node_id: str) -> None:
    """PKGV2-QA-002: duplication itself is the exploitable condition, even
    when the appended occurrence repeats the already-correct value -- a
    first-occurrence check sees the same correct value twice and would still
    pass, but argparse still has two occurrences to resolve from."""

    module = _load_module(f"validate_plan_v2_dup_node_same_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + ["--node", node_id]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_duplicate_node_flag_wrong_value_is_rejected(node_id: str) -> None:
    """PKGV2-QA-002's exact trigger: a scan command retains the correct first
    --node pair and appends a second, wrong one. argparse would execute
    against the wrong (last) value; a first-occurrence check would still see
    the correct first value and pass."""

    module = _load_module(f"validate_plan_v2_dup_node_wrong_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    other_node = next(n for n in NODE_SCOPED_SCAN_NODES if n != node_id)
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + ["--node", other_node]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_duplicate_graph_flag_wrong_value_is_rejected(node_id: str) -> None:
    """PKGV2-QA-002's other trigger: a second --graph pointing at the parent
    v1 graph, appended after the correct package-v2 --graph."""

    module = _load_module(f"validate_plan_v2_dup_graph_wrong_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    parent_graph_relative = PARENT_GRAPH.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--graph",
        parent_graph_relative,
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_duplicate_graph_flag_same_value_is_rejected(node_id: str) -> None:
    module = _load_module(f"validate_plan_v2_dup_graph_same_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    expected_graph = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--graph",
        expected_graph,
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


# ---- N60: the whole-tree exception's own zero/one/duplicate proofs


def test_n60_whole_tree_command_with_exactly_one_graph_and_zero_node_is_accepted() -> None:
    module = _load_module("validate_plan_v2_n60_baseline", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    module.validate_graph(document)  # must not raise; the unmodified graph is the positive control


def test_n60_whole_tree_command_missing_graph_flag_is_rejected() -> None:
    module = _load_module("validate_plan_v2_n60_zero_graph", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative)
    index = command.index("--graph")
    del command[index : index + 2]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_n60_whole_tree_command_with_duplicate_graph_flag_wrong_value_is_rejected() -> None:
    """The exact scenario the task calls out: N60's complete-tree command
    with a second, wrong --graph appended after the correct one."""

    module = _load_module("validate_plan_v2_n60_dup_graph_wrong", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    parent_graph_relative = PARENT_GRAPH.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--graph",
        parent_graph_relative,
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_n60_whole_tree_command_with_duplicate_graph_flag_same_value_is_rejected() -> None:
    module = _load_module("validate_plan_v2_n60_dup_graph_same", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    expected_graph = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--graph",
        expected_graph,
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_n60_whole_tree_command_with_erroneous_node_flag_added_is_rejected() -> None:
    """N60 must stay in complete-tree mode: an erroneously appended --node
    (not a duplicate of an existing flag, since N60 has none to begin with)
    must also be rejected, since argparse would then execute this command in
    node-scoped mode instead of the required complete-tree mode."""

    module = _load_module("validate_plan_v2_n60_added_node", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--node",
        "N20_PROVIDER_TRANSPORT",
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


# ------------------------------- PKGV2-QA-002 round 3: argparse equals-form


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_equals_form_duplicate_node_flag_is_rejected(node_id: str) -> None:
    """PKGV2-QA-002's round-3 finding: argparse accepts --node=value as well
    as --node value, and resolves a mix of the two spellings to the last one
    seen just like two of the same spelling. A count of exact "--node" tokens
    alone would miss an equals-form duplicate; flag_values must not."""

    module = _load_module(f"validate_plan_v2_dup_node_equals_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    other_node = next(n for n in NODE_SCOPED_SCAN_NODES if n != node_id)
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [f"--node={other_node}"]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_equals_form_duplicate_graph_flag_is_rejected(node_id: str) -> None:
    module = _load_module(f"validate_plan_v2_dup_graph_equals_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    parent_graph_relative = PARENT_GRAPH.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        f"--graph={parent_graph_relative}"
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_single_equals_form_occurrence_is_accepted(node_id: str) -> None:
    """The fix must not overcorrect: a command carrying its one --node and
    one --graph occurrence entirely in equals-form (no duplication at all)
    is exactly one occurrence of each and must still validate."""

    module = _load_module(f"validate_plan_v2_single_equals_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    graph_flag = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative)
    node_index = command.index("--node")
    command[node_index : node_index + 2] = [f"--node={node_id}"]
    graph_index = command.index("--graph")
    command[graph_index : graph_index + 2] = [f"--graph={graph_flag}"]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    module.validate_graph(document)  # must not raise


def test_n60_whole_tree_command_with_equals_form_duplicate_graph_flag_is_rejected() -> None:
    module = _load_module("validate_plan_v2_n60_dup_graph_equals", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    parent_graph_relative = PARENT_GRAPH.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        f"--graph={parent_graph_relative}"
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_n60_whole_tree_command_with_equals_form_node_flag_added_is_rejected() -> None:
    module = _load_module("validate_plan_v2_n60_added_node_equals", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--node=N20_PROVIDER_TRANSPORT"
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_n60_whole_tree_command_with_single_equals_form_graph_occurrence_is_accepted() -> None:
    module = _load_module("validate_plan_v2_n60_single_equals", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    graph_flag = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative)
    graph_index = command.index("--graph")
    command[graph_index : graph_index + 2] = [f"--graph={graph_flag}"]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    module.validate_graph(document)  # must not raise


# --------------------------- PKGV2-QA-002: argparse abbreviation-form proofs
#
# The round-3 fix moved occurrence counting onto argparse itself rather than
# hand-rolled patterns, specifically to close the whole spelling space at
# once instead of one variant per QA round. These tests prove that actually
# holds for prefix abbreviation (e.g. --nod for --node), the next spelling
# argparse accepts beyond the separated and equals forms already covered
# above, without a corresponding round-4 finding being needed to add it.


def test_node_scoped_scan_command_with_abbreviation_form_duplicate_node_flag_is_rejected() -> None:
    module = _load_module("validate_plan_v2_dup_node_abbrev", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node_id = "N20_PROVIDER_TRANSPORT"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--nod",
        "N30_PREFLIGHT_EGRESS",
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_node_scoped_scan_command_with_abbreviation_form_duplicate_graph_flag_is_rejected() -> None:
    module = _load_module("validate_plan_v2_dup_graph_abbrev", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    parent_graph_relative = PARENT_GRAPH.relative_to(REPO_ROOT).as_posix()
    node_id = "N30_PREFLIGHT_EGRESS"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        f"--grap={parent_graph_relative}"
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_n60_whole_tree_command_with_abbreviation_form_node_flag_added_is_rejected() -> None:
    module = _load_module("validate_plan_v2_n60_added_node_abbrev", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--nod",
        "N20_PROVIDER_TRANSPORT",
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


# ------------------------------------------------- no production edit proof


def test_no_production_policy_schema_or_active_test_file_was_modified() -> None:
    """This graph-scaffolding/RC-authoring task itself must touch no
    production, policy, schema, or active-test file. N20_PROVIDER_TRANSPORT
    has, separately, already executed for real and legitimately modified a
    known, recorded set of these files (its own admitted result,
    plans/27_.../execution_package_v2/results/N20_PROVIDER_TRANSPORT.result.v1.json,
    lists exactly which ones and their exact sha256) -- that is real,
    independently-verified production work this task must not touch or
    undo, not a defect. So this test's real proof obligation is narrower
    than "zero git diff": every path git reports as changed under these
    roots must be explained by N20's own recorded changed_files at exactly
    N20's own recorded hash; nothing else, and nothing further, may differ."""

    process = subprocess.run(
        [
            "git", "status", "--porcelain", "--",
            "runtime", "policy",
            "schemas/routes.schema.v1.json", "schemas/model_registry.schema.v1.json",
            "tests/runtime",
        ],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert process.returncode == 0
    changed_paths = {line[3:] for line in process.stdout.splitlines() if line.strip()}

    n20_result = json.loads(
        (PACKAGE_DIR / "results/N20_PROVIDER_TRANSPORT.result.v1.json").read_text(encoding="utf-8")
    )
    n20_changed = {
        item["path"]: item["sha256"]
        for item in n20_result["changed_files"]
        if item["change"] != "deleted"
    }

    unexplained = changed_paths - n20_changed.keys()
    assert not unexplained, f"unexpected diff outside N20's own recorded changes: {unexplained}"
    for path in changed_paths:
        assert sha256_file(REPO_ROOT / path) == n20_changed[path], (
            f"{path}: live content no longer matches N20's own admitted-result hash"
        )


# ------------------------------------------------- RC1-QA-001: fresh-prompt
# graph-reference consistency
#
# RC1's one-round QA session (release_candidate/rc1/QA/) returned FAIL with
# finding RC1-QA-001: "Automated suite does not prove fresh-prompt
# consistency" -- no test read or validated N00/N20/N30's prompt text, so the
# suite stayed green while all three prompts instructed a scan against
# `implementation.graph.v1.yaml`, a filename this package does not contain,
# instead of the package's actually enforced and graph-bound
# `implementation.graph.v4.yaml`. The tests below close that blind spot by
# parsing the live prompt text itself (not merely the graph's own
# `verification` commands, already covered above by
# test_each_n20_to_n50_scan_command_carries_the_exact_package_v2_graph).

FRESH_PROMPT_NODE_IDS = ["N00_SPEC_APPROVAL_GATE", "N20_PROVIDER_TRANSPORT", "N30_PREFLIGHT_EGRESS"]

# Matches an explicit `--graph <path>` (whitespace-form) or `--graph=<path>`
# (equals-form) flag value inside a shell command shown in prompt text, e.g.
# "...scan_node.py --node N20_PROVIDER_TRANSPORT --graph
# execution_package_v2/implementation.graph.v4.yaml" or
# "...--graph=execution_package_v2/implementation.graph.v4.yaml".
#
# RC2-QA-001: the whitespace-only form of this pattern left every equals-form
# reference -- correct or stale -- entirely invisible to this check, so a
# stale equals-form reference could sit right beside a correct whitespace-form
# one and the suite stayed green. Both spellings are exactly the two argparse
# itself accepts, the same ambiguity validate_plan_v2.py's own
# flag_values()/_scan_node_argument_parser() already had to resolve for
# PKGV2-QA-002 -- mirrored here rather than reinvented.
_GRAPH_FLAG_PATTERN = re.compile(r"--graph(?:\s+|=)(\S+\.yaml)")

# Matches N00's existence-requirement phrasing, e.g. "Require
# `execution_package_v2/implementation.graph.v4.yaml` to exist". Deliberately
# narrow (requires the literal "Require `...` to exist" shape) so it does not
# also match unrelated backtick-quoted historical filenames elsewhere in the
# same prompt (e.g. a past predecessor package's own graph, cited by name as
# context for an unrelated finding, which is a legitimate reference and must
# not be flagged).
_REQUIRE_EXISTS_PATTERN = re.compile(r"Require `([^`]+\.yaml)` to exist")


def _graph_references(text: str) -> list[str]:
    return _GRAPH_FLAG_PATTERN.findall(text) + _REQUIRE_EXISTS_PATTERN.findall(text)


# RC2-QA-001: a suffix/endswith comparison against `execution_package_v2/<name>`
# let a wrong path *prefix* through unpunished as long as the reference merely
# ended with the enforced graph's filename (e.g.
# "other/execution_package_v2/implementation.graph.v4.yaml"). Resolve each
# extracted reference to its real, absolute filesystem path and require exact
# equality against the package graph's own real path -- never a
# substring/suffix relationship.
#
# Two base directories are legitimate here because this package's own live
# prompts use both conventions: N20/N30 spell the reference as a full
# repo-relative path (resolved against REPO_ROOT), and N00 spells it relative
# to the plan directory (resolved against PLAN_DIR). A reference only counts
# as resolving to the enforced graph if at least one of these bases makes it
# land, path-for-path, on the graph's real location -- a wrong prefix fails
# under both bases, since prepending an extra path segment cannot cancel out.
_GRAPH_REFERENCE_BASES = (REPO_ROOT, PLAN_DIR)


def _resolves_to_enforced_graph(reference: str) -> bool:
    target = PACKAGE_GRAPH.resolve()
    return any((base / reference).resolve() == target for base in _GRAPH_REFERENCE_BASES)


def _fresh_prompt_path(node_id: str) -> Path:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    return REPO_ROOT / document["nodes"][node_id]["prompt"]


@pytest.mark.parametrize("node_id", FRESH_PROMPT_NODE_IDS)
def test_each_fresh_prompt_references_the_exact_enforced_graph(node_id: str) -> None:
    """RC1-QA-001 / RC2-QA-001 regression: the graph-bound prompt for
    N00/N20/N30 must reference this package's actually enforced graph file --
    never a missing, stale, mismatched, or wrong-prefixed one -- whether the
    prompt spells --graph in the whitespace-form or the equals-form."""

    prompt_path = _fresh_prompt_path(node_id)
    text = prompt_path.read_text(encoding="utf-8")
    references = _graph_references(text)
    assert references, f"{node_id}: prompt {prompt_path} contains no graph-path reference at all"
    for reference in references:
        assert _resolves_to_enforced_graph(reference), (
            f"{node_id}: prompt {prompt_path} references {reference!r}, which does not "
            f"resolve to the enforced graph ({PACKAGE_GRAPH!r})"
        )


# Mutation-based negative proof (same discipline as the PKGV2-QA-001/002
# fixes above): prove this check is a real regression test, not a vacuously
# green assertion, by running it against the exact historical prompt text
# that produced RC1-QA-001 -- the superseded v3 prompts, preserved unchanged
# on disk -- and confirming it fails there, then against a reference stripped
# entirely.

_RC1_DEFECTIVE_PROMPTS = {
    "N00_SPEC_APPROVAL_GATE": PACKAGE_PROMPTS_DIR / "N00_spec_approval_gate.prompt.v3.md",
    "N20_PROVIDER_TRANSPORT": PACKAGE_PROMPTS_DIR / "N20_provider_transport.prompt.v3.md",
    "N30_PREFLIGHT_EGRESS": PACKAGE_PROMPTS_DIR / "N30_preflight_egress.prompt.v3.md",
}


@pytest.mark.parametrize("node_id", FRESH_PROMPT_NODE_IDS)
def test_graph_reference_check_rejects_the_real_rc1_qa_001_defect(node_id: str) -> None:
    text = _RC1_DEFECTIVE_PROMPTS[node_id].read_text(encoding="utf-8")
    references = _graph_references(text)
    assert references, (
        f"{node_id}: expected the superseded v3 prompt to still contain a graph "
        "reference to mutate-test against"
    )
    assert any(not _resolves_to_enforced_graph(reference) for reference in references), (
        f"{node_id}: expected the superseded v3 prompt's stale graph reference to be "
        "caught as mismatched by this check, but every reference it found already "
        "resolves to the enforced graph -- the check would not have caught RC1-QA-001"
    )


def test_graph_reference_check_rejects_a_prompt_with_no_graph_reference_at_all() -> None:
    stripped_text = "# GOAL\n\nDo something. No graph file is named anywhere in this text.\n"
    assert _graph_references(stripped_text) == []


@pytest.mark.parametrize("node_id", FRESH_PROMPT_NODE_IDS)
def test_fresh_prompt_graph_references_do_not_regress_to_a_different_wrong_version(node_id: str) -> None:
    """Guards against a fix that merely swaps one wrong version for another
    (e.g. a future graph bump to v5 landing while a prompt still says v4)."""

    prompt_path = _fresh_prompt_path(node_id)
    text = prompt_path.read_text(encoding="utf-8")
    for reference in _graph_references(text):
        mutated = reference.replace(PACKAGE_GRAPH.name, "implementation.graph.v999.yaml")
        assert not _resolves_to_enforced_graph(mutated)


# ------------------------------------------------- RC2-QA-001: equals-form and
# wrong-prefix graph references
#
# RC2's one-round QA session (release_candidate/rc2/QA/) returned FAIL with
# finding RC2-QA-001: the check above only ever matched the whitespace-form
# `--graph <path>` spelling (an equals-form `--graph=<path>` reference, stale
# or correct, was invisible to it entirely) and compared references with
# `str.endswith(...)`, so a wrong path *prefix* that merely ended with the
# enforced graph's own filename (e.g.
# "other/execution_package_v2/implementation.graph.v4.yaml") would incorrectly
# pass. These tests mutation-prove both gaps are closed, plus that a
# genuinely correct reference still passes in either spelling.


def test_graph_reference_check_finds_an_equals_form_reference_at_all() -> None:
    """RC2-QA-001: the original whitespace-only pattern would not even see an
    equals-form reference, correct or stale -- prove it is now extracted."""

    text = (
        "python3 controller/scan_node.py --node N20_PROVIDER_TRANSPORT "
        "--graph=plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v1.yaml"
    )
    assert _graph_references(text) == [
        "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v1.yaml"
    ]


def test_graph_reference_check_rejects_an_equals_form_stale_reference() -> None:
    """RC2-QA-001's trigger example: a stale equals-form reference sitting
    beside what might otherwise look like a correct whitespace-form one must
    still be caught."""

    text = (
        "Use the whitespace form: --graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml\n"
        "Retained stale equals form: --graph=execution_package_v2/implementation.graph.v1.yaml\n"
    )
    references = _graph_references(text)
    assert len(references) == 2
    assert not all(_resolves_to_enforced_graph(reference) for reference in references)


def test_graph_reference_check_rejects_a_wrong_prefix_reference_ending_in_the_right_filename() -> None:
    """RC2-QA-001's other trigger: a wrong path prefix that happens to end
    with the enforced graph's own filename must not slip through a
    suffix/endswith comparison."""

    text = (
        "python3 controller/scan_node.py --node N20_PROVIDER_TRANSPORT "
        "--graph other/execution_package_v2/implementation.graph.v8.yaml"
    )
    references = _graph_references(text)
    assert references == ["other/execution_package_v2/implementation.graph.v8.yaml"]
    assert not _resolves_to_enforced_graph(references[0])


@pytest.mark.parametrize(
    "flag_spelling",
    [
        "--graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml",
        "--graph=plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml",
    ],
    ids=["whitespace-form", "equals-form"],
)
def test_graph_reference_check_accepts_a_genuinely_correct_reference_in_either_spelling(flag_spelling: str) -> None:
    """Positive control: a genuinely correct reference must still pass, in
    both spellings, so the RC2-QA-001 fix did not simply reject everything."""

    text = f"python3 controller/scan_node.py --node N20_PROVIDER_TRANSPORT {flag_spelling}"
    references = _graph_references(text)
    assert len(references) == 1
    assert _resolves_to_enforced_graph(references[0])


# ------------------------------------------------- N00 schema-v2 blocker fix
#
# N00 could not actually be executed against implementation.graph.v4.yaml:
# plans/27_.../schemas/spec_approval.schema.v1.json -- the *parent* v1
# package's own frozen schema -- const-locks approved_spec to that package's
# own spec, a path this package's approved spec v4 can never equal, so
# validation failed structurally and unconditionally no matter how the
# approval record was filled in; N00_spec_approval_gate.prompt.v4.md S6 also
# claimed that schema was frozen per this package's own rules.frozen_before_entry,
# which it never was. These tests prove the fix: N00 (graph v5) binds a
# package-scoped schema v2 whose const-locked paths genuinely match this
# package's own live artifacts, contract v2 validates against it, every
# bound digest recomputes against live bytes, a mutated digest/path/model
# assignment is rejected by the real validator (not merely undocumented),
# and the old parent schema is untouched.

CONTRACT_V5_DIGEST_FIELDS = [
    "approved_spec_sha256",
    "spec_qa_verification_sha256",
    "approved_rc_manifest_sha256",
    "execution_package_qa_verification_sha256",
    "approved_graph_sha256",
]


def _schema_v5() -> dict[str, Any]:
    return json.loads(CONTRACT_SCHEMA_V5.read_text(encoding="utf-8"))


def _contract_v4() -> dict[str, Any]:
    return yaml.safe_load(CONTRACT_V5.read_text(encoding="utf-8"))


def _write_mutated_contract_v4(tmp_path: Path, mutate) -> Path:
    contract = _contract_v4()
    mutate(contract)
    mutated_path = tmp_path / "spec_approval.v4.mutated.yaml"
    mutated_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
    return mutated_path


def test_graph_v8_declares_schema_v5_frozen_not_schema_v3_v2_or_the_parent_v1_schema() -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    frozen = document["rules"]["frozen_before_entry"]
    schema_v5_relative = CONTRACT_SCHEMA_V5.relative_to(REPO_ROOT).as_posix()
    schema_v3_relative = CONTRACT_SCHEMA_V3.relative_to(REPO_ROOT).as_posix()
    schema_v2_relative = CONTRACT_SCHEMA_V2.relative_to(REPO_ROOT).as_posix()
    parent_v1_relative = PARENT_APPROVAL_SCHEMA_V1.relative_to(REPO_ROOT).as_posix()
    assert schema_v5_relative in frozen
    assert schema_v3_relative not in frozen
    assert schema_v2_relative not in frozen
    assert parent_v1_relative not in frozen
    # node_result.schema.v1.json must remain -- adding schema v5 must not drop it.
    assert document["node_result_schema"] in frozen


def test_n00_prompt_v8_validates_against_schema_v5_not_schema_v3_v2_or_the_parent_v1_schema() -> None:
    """The prompt's own explanatory prose legitimately names the historical
    parent v1 schema and schemas v2/v3 (to explain the defect being fixed,
    exactly as prompt v6 named v2's stale-schema-binding defect) -- so a
    blanket "v3.json not in text" assertion would be too strict. What must
    actually be true is that the load-bearing validation instruction (TEST
    step 6) targets schema v5."""

    prompt_path = _fresh_prompt_path("N00_SPEC_APPROVAL_GATE")
    assert prompt_path.name == "N00_spec_approval_gate.prompt.v8.md"
    text = prompt_path.read_text(encoding="utf-8")
    assert (
        "Validate `execution_package_v2/contracts/spec_approval.v5.yaml` against\n"
        "   `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/schemas/spec_approval.schema.v5.json`"
    ) in text
    assert "Validate a new `execution_package_v2/contracts/spec_approval.v1.yaml`" not in text


def test_n00_prompt_v8_does_not_repeat_the_false_frozen_claim_about_schema_v1() -> None:
    prompt_path = _fresh_prompt_path("N00_SPEC_APPROVAL_GATE")
    text = prompt_path.read_text(encoding="utf-8")
    assert "is frozen and unversioned per" not in text


def test_schema_v5_spec_path_const_matches_graph_v8_source_spec() -> None:
    schema = _schema_v5()
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    assert schema["properties"]["approved_spec"]["const"] == document["source_spec"]


def test_schema_v5_graph_path_const_matches_this_packages_own_active_graph() -> None:
    schema = _schema_v5()
    expected = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    assert schema["properties"]["approved_graph"]["const"] == expected


def test_schema_v5_spec_path_const_resolves_to_the_live_v4_specification_file() -> None:
    schema = _schema_v5()
    spec_path = REPO_ROOT / schema["properties"]["approved_spec"]["const"]
    assert spec_path.is_file()
    assert spec_path.name == "langgraph_curriculum_factory.spec.v4.md"


def test_contract_v4_validates_against_schema_v5() -> None:
    schema = _schema_v5()
    jsonschema.Draft202012Validator.check_schema(schema)
    contract = _contract_v4()
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(contract)


@pytest.mark.parametrize("field", CONTRACT_V5_DIGEST_FIELDS)
def test_contract_v4_bound_digest_recomputes_against_live_bytes(field: str) -> None:
    contract = _contract_v4()
    rc_manifest_path = REPO_ROOT / contract["approved_rc_manifest"]
    paths_by_field = {
        "approved_spec_sha256": REPO_ROOT / contract["approved_spec"],
        "spec_qa_verification_sha256": (REPO_ROOT / contract["approved_spec"]).parent / "QA" / "verification.json",
        "approved_rc_manifest_sha256": rc_manifest_path,
        "execution_package_qa_verification_sha256": rc_manifest_path.parent / "QA" / "verification.json",
        "approved_graph_sha256": REPO_ROOT / contract["approved_graph"],
    }
    path = paths_by_field[field]
    assert path.is_file(), f"{field}: bound path does not exist: {path}"
    assert contract[field] == sha256_file(path)


def test_contract_v4_recomputed_digests_match_the_v3_contracts_original_approval() -> None:
    """Four of contract v5's five digests must be the *same* already-approved
    values from spec_approval.v3.yaml (spec, spec QA, rc3 manifest, rc3 QA)
    -- carried forward, not reinvented, and rc3 remains the approved
    package-structure snapshot even though this correction's own rc8 lineage
    is what the result-namespace collision was fixed and QA'd against. Only
    approved_graph_sha256 legitimately advances, with the v6->v7
    result-namespace correction this record itself performs."""

    contract = _contract_v4()
    assert contract["approved_spec_sha256"] == "e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c"
    assert contract["spec_qa_verification_sha256"] == "899c9720be48f071d6caf26eceafa81be626cd3bda685afa05eb0cc1dfe9a631"
    assert contract["approved_rc_manifest_sha256"] == "0e4fbfe2c258ae6176931e5490f8a2b55bdf8708d3ef0f257b50a05c9e582a6d"
    assert contract["execution_package_qa_verification_sha256"] == "202e2f214dd732ce24eb758c7cee5965cfcc113d71d03350d8bc5fefa7773217"
    assert contract["approved_rc_manifest"] == (
        "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc3/manifest.v1.json"
    )


def test_contract_v4_model_assignments_match_user_decision_required_01() -> None:
    assignments = _contract_v4()["model_assignments"]
    expected = {
        "M01_RESEARCH_UNIT_SOURCES": {"model": "claude-sonnet-5", "effort": "xhigh"},
        "M02_CREATE_UNIT_DOMAIN_DATA": {"model": "claude-sonnet-5", "effort": "high"},
        "M03_WRITE_UNIT_CONTENT": {"model": "claude-sonnet-5", "effort": "high"},
        "M04_CREATE_UNIT_VISUALS": {"model": "claude-sonnet-5", "effort": "high"},
        "M05_REVIEW_ACTUAL_UNIT": {"model": "gpt-5.6-sol", "effort": "xhigh"},
        "M06_REPAIR_NAMED_UNIT_ARTIFACT": {"model": "claude-sonnet-5", "effort": "xhigh"},
        "M07_REVIEW_ACTUAL_WORKBOOK": {"model": "gpt-5.6-sol", "effort": "xhigh"},
        "M08_REPAIR_NAMED_WORKBOOK_DEFECT": {"model": "claude-sonnet-5", "effort": "xhigh"},
    }
    assert assignments == expected


def test_validate_plan_v2_module_is_wired_to_schema_v5_not_schema_v3_v2_or_v1() -> None:
    assert validate_plan_v2.CONTRACT_SCHEMA_PATH == CONTRACT_SCHEMA_V5
    assert not hasattr(validate_plan_v2, "APPROVAL_SCHEMA_PATH")
    assert validate_plan_v2.GRAPH_PATH == PACKAGE_GRAPH


def test_validate_plan_v2_passes_end_to_end_against_the_live_contract() -> None:
    code, payload = run([str(VALIDATE_PLAN_V2)])
    assert code == 0, payload
    assert payload["valid"] is True


@pytest.mark.parametrize("field", CONTRACT_V5_DIGEST_FIELDS)
def test_validator_rejects_a_wrong_but_well_formed_bound_digest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, field: str) -> None:
    """JSON Schema cannot hash a file, so a syntactically well-formed but
    wrong digest passes schema-shape validation alone. The validator-level
    recompute-and-compare in validate_spec_approval_contract() must still
    reject it -- proving this is a real integrity check, not documentation."""

    wrong_digest = "0" * 64
    mutated_path = _write_mutated_contract_v4(tmp_path, lambda c: c.__setitem__(field, wrong_digest))
    monkeypatch.setattr(validate_plan_v2, "CONTRACT_PATH", mutated_path)
    with pytest.raises(validate_plan_v2.ValidationError):
        validate_plan_v2.validate_spec_approval_contract()


def test_validator_rejects_a_nonexistent_rc_manifest_generation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """approved_rc_manifest is deliberately not const-locked to rc3 forever
    (a future re-approval must be expressible without a schema bump), so
    schema v5's pattern alone accepts any rc<N> path shape. The validator
    must still reject a generation that does not actually exist on disk."""

    def _mutate(contract: dict[str, Any]) -> None:
        contract["approved_rc_manifest"] = (
            "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/"
            "release_candidate/rc99/manifest.v1.json"
        )

    mutated_path = _write_mutated_contract_v4(tmp_path, _mutate)
    monkeypatch.setattr(validate_plan_v2, "CONTRACT_PATH", mutated_path)
    with pytest.raises(validate_plan_v2.ValidationError):
        validate_plan_v2.validate_spec_approval_contract()


def test_validator_rejects_a_wrong_approved_spec_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """approved_spec IS const-locked (unlike approved_rc_manifest): a wrong
    value must fail schema validation itself, exactly the class of defect
    (a const pointed at the wrong package's spec) this whole correction
    lineage exists to fix -- proving schema v5 does not repeat it in reverse."""

    def _mutate(contract: dict[str, Any]) -> None:
        contract["approved_spec"] = "plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md"

    mutated_path = _write_mutated_contract_v4(tmp_path, _mutate)
    monkeypatch.setattr(validate_plan_v2, "CONTRACT_PATH", mutated_path)
    with pytest.raises(jsonschema.ValidationError):
        validate_plan_v2.validate_spec_approval_contract()


def test_validator_rejects_a_wrong_approved_graph_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A value naming graph v6 -- correct for schema v3, wrong for schema v5
    -- must still be rejected: schema v5's const genuinely moved to v7, it
    did not just widen to accept both."""

    def _mutate(contract: dict[str, Any]) -> None:
        contract["approved_graph"] = (
            "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/"
            "deprecated/implementation.graph.v6.yaml"
        )

    mutated_path = _write_mutated_contract_v4(tmp_path, _mutate)
    monkeypatch.setattr(validate_plan_v2, "CONTRACT_PATH", mutated_path)
    with pytest.raises(jsonschema.ValidationError):
        validate_plan_v2.validate_spec_approval_contract()


@pytest.mark.parametrize(
    "job_id,wrong_assignment",
    [
        ("M01_RESEARCH_UNIT_SOURCES", {"model": "claude-sonnet-5", "effort": "high"}),
        ("M05_REVIEW_ACTUAL_UNIT", {"model": "claude-sonnet-5", "effort": "xhigh"}),
    ],
    ids=["m01-wrong-effort", "m05-wrong-family"],
)
def test_validator_rejects_a_wrong_model_assignment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, job_id: str, wrong_assignment: dict[str, str]
) -> None:
    def _mutate(contract: dict[str, Any]) -> None:
        contract["model_assignments"][job_id] = wrong_assignment

    mutated_path = _write_mutated_contract_v4(tmp_path, _mutate)
    monkeypatch.setattr(validate_plan_v2, "CONTRACT_PATH", mutated_path)
    with pytest.raises(jsonschema.ValidationError):
        validate_plan_v2.validate_spec_approval_contract()


def test_unmutated_contract_v4_copy_still_passes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Positive control for every mutation test above: an unmutated copy at a
    different path must still pass, so the rejections above are proving a
    real mutation was caught, not that the check always fails."""

    mutated_path = _write_mutated_contract_v4(tmp_path, lambda c: None)
    monkeypatch.setattr(validate_plan_v2, "CONTRACT_PATH", mutated_path)
    validate_plan_v2.validate_spec_approval_contract()


def test_parent_v1_approval_schema_is_byte_unchanged() -> None:
    """The parent v1 package's own frozen schema
    (plans/27_.../schemas/spec_approval.schema.v1.json) is untouched by this
    correction: it remains exclusively that package's own frozen contract,
    never edited to accommodate this package."""

    assert sha256_file(PARENT_APPROVAL_SCHEMA_V1) == (
        "829943e745cf6eb550e6319f42df4086f187a08d373f7e08f9fddf822d9fde36"
    )


def test_schema_v2_is_byte_unchanged() -> None:
    """Schema v2 is superseded, not edited: it remains, unchanged, the frozen
    contract for any record that still cites implementation.graph.v5.yaml."""

    assert sha256_file(CONTRACT_SCHEMA_V2) == (
        "d6a160aa79921c0ce0bab57504e5c36f921c7b6a5b66798786f118aec0ab6cd4"
    )


def test_contract_v2_is_byte_unchanged() -> None:
    assert sha256_file(CONTRACT_V2) == (
        "b6519442e532753fde795c892a5d386d1afa060cfa5df9dff8ad86351c0bc4c9"
    )


def test_schema_v3_is_byte_unchanged() -> None:
    """Schema v3 is superseded by RC8, not edited: it remains, unchanged, the
    frozen contract for any record that still cites
    implementation.graph.v6.yaml."""

    assert sha256_file(CONTRACT_SCHEMA_V3) == (
        "cdb71a99ea5714d59a9bf9a360217fda849548eddbd140527e1892c139f7f0c4"
    )


def test_contract_v3_is_byte_unchanged() -> None:
    assert CONTRACT_V3.is_file()
    contract = yaml.safe_load(CONTRACT_V3.read_text(encoding="utf-8"))
    assert contract["schema_version"] == 3
    assert contract["approved_graph"] == (
        "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml"
    )


def test_deprecated_graph_v4_is_byte_identical_to_the_originally_approved_graph() -> None:
    assert DEPRECATED_GRAPH_V4.is_file()
    assert sha256_file(DEPRECATED_GRAPH_V4) == (
        "0d5b5af8b0c60847e3b52ac93c4c10328f48a1404130a6b785485bcbbae3d571"
    )


def test_deprecated_graph_v5_is_byte_identical_to_the_rc3_rc5_approved_graph() -> None:
    """N20V2-F01: implementation.graph.v5.yaml is the graph the real N20
    execution ran against and reached a genuine BLOCKED on -- it must be
    preserved exactly, not edited to make the defect disappear."""

    assert DEPRECATED_GRAPH_V5.is_file()
    assert sha256_file(DEPRECATED_GRAPH_V5) == (
        "ce2362787a9760c9db3b2f667a0561ebd877ec89f24d690b2210ec9b6f3777b8"
    )


def test_deprecated_graph_v6_is_byte_identical_to_the_rc7_approved_graph() -> None:
    """RC8's own reason for existing: implementation.graph.v6.yaml correctly
    fixed N20V2-F01 but itself carried the result-namespace collision this
    correction fixes -- it must be preserved exactly, not edited to make the
    defect disappear."""

    assert DEPRECATED_GRAPH_V6.is_file()
    assert sha256_file(DEPRECATED_GRAPH_V6) == (
        "b186b58828fd1f490a57dd3cfe7d26bcdff70a37f78d6d996f2f8234ef2b5c26"
    )


def test_rc3_manifest_and_qa_are_untouched_by_this_correction() -> None:
    rc3_dir = PACKAGE_DIR / "release_candidate/rc3"
    assert sha256_file(rc3_dir / "manifest.v1.json") == (
        "0e4fbfe2c258ae6176931e5490f8a2b55bdf8708d3ef0f257b50a05c9e582a6d"
    )
    assert sha256_file(rc3_dir / "QA" / "verification.json") == (
        "202e2f214dd732ce24eb758c7cee5965cfcc113d71d03350d8bc5fefa7773217"
    )


def test_rc4_manifest_and_qa_are_untouched_by_this_correction() -> None:
    """rc4 FAILED (MAX_ITERATIONS_EXHAUSTED, RC4-QA-001) and never produced a
    verification.json -- session.json and verdict.json are its QA record."""

    rc4_dir = PACKAGE_DIR / "release_candidate/rc4"
    assert sha256_file(rc4_dir / "manifest.v1.json") == (
        "dbf3fbe87f622ec34d3238164358a325ad755c083af68d8349d8803a02a09961"
    )
    assert sha256_file(rc4_dir / "QA" / "session.json") == (
        "18283d57afce6d637edb51fe6c86a022de2d5101bf5d364d08e267dab15a0e3a"
    )
    assert sha256_file(rc4_dir / "QA" / "verdict.json") == (
        "a78c9e9d4657fe48ce44301bf78870c282494328519cd8e8b7436d92a758cbd2"
    )


def test_rc5_manifest_and_qa_are_untouched_by_this_correction() -> None:
    rc5_dir = PACKAGE_DIR / "release_candidate/rc5"
    assert sha256_file(rc5_dir / "manifest.v1.json") == (
        "75e52f5c04dc67c1450791cea80a838544bb954916348a409beb64f719012722"
    )
    assert sha256_file(rc5_dir / "QA" / "verification.json") == (
        "9118efe12ca553af6e7d7d01657f7705f251d8e8bbaa13ff0f4153af109b4d05"
    )


def test_rc6_manifest_and_qa_are_untouched_by_this_correction() -> None:
    """rc6 FAILED (RC6-QA-001, RC6-QA-002) and never produced a
    verification.json -- session.json and verdict.json are its QA record."""

    rc6_dir = PACKAGE_DIR / "release_candidate/rc6"
    assert sha256_file(rc6_dir / "manifest.v1.json") == (
        "aae9a059a35b3a387ea5e216eb52cbada551c2119a252e15851677eedb0234b8"
    )
    assert sha256_file(rc6_dir / "QA" / "session.json") == (
        "9db0705fdfad8dcabca483fd310b5dbabfb27159b032c3ecb3e568a7f7322232"
    )
    assert sha256_file(rc6_dir / "QA" / "verdict.json") == (
        "a861172224cbfdb84c265ef708f6d304c89b49c2f00e78a60487b36e52687440"
    )


def test_rc7_manifest_and_qa_are_untouched_by_this_correction() -> None:
    """rc7 reached QA_PASSED and is the immediate predecessor RC8 exists to
    correct (the result-namespace collision was found in independent
    verification of rc7's own approved graph, not by rc7's QA session
    itself, which correctly scoped its review to rc6's two findings)."""

    rc7_dir = PACKAGE_DIR / "release_candidate/rc7"
    assert sha256_file(rc7_dir / "manifest.v1.json") == (
        "a6512de76b7e36b3e5548620b22df222a231a4bf00edf35bacec61d999a50d2d"
    )
    assert sha256_file(rc7_dir / "QA" / "verification.json") == (
        "22a89ca64f3db385fd1d8f20f310eb880a6ec2265894924ff78a4a0cbb415901"
    )


def test_spec_approval_v1_contract_is_untouched() -> None:
    v1_contract_path = PACKAGE_DIR / "contracts/spec_approval.v1.yaml"
    contract = yaml.safe_load(v1_contract_path.read_text(encoding="utf-8"))
    assert contract["schema_version"] == 1


def test_spec_approval_v2_contract_is_untouched() -> None:
    contract = yaml.safe_load(CONTRACT_V2.read_text(encoding="utf-8"))
    assert contract["schema_version"] == 2
    assert contract["approved_graph"] == (
        "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v5.yaml"
    )


# --------------------------------------------------------- RC8: result-
# namespace collision / preservation proofs
#
# implementation.graph.v6.yaml correctly fixed N20V2-F01 (the scan-scope
# defect) but its own result_pattern was byte-identical to
# implementation.graph.v5.yaml's own. N00 and N10 are already ADMITTED
# (PASSED) and N20 is already BLOCKED, all three with real results at
# execution_package_v2/results/{node_id}.result.v1.json -- a fresh execution
# of any of them under graph v6 as originally built would have silently
# overwritten those exact files. implementation.graph.v8.yaml fixes this by
# moving result_pattern (and every node's own result/evidence write paths)
# to the versioned subdirectory execution_package_v2/results/v8/, whose
# per-node filenames never coincide with the flat per-node files directly
# under execution_package_v2/results/. These tests prove the collision
# cannot recur and that the historical records are untouched.

ADMITTED_OR_BLOCKED_RESULT_FILES = [
    "N00_SPEC_APPROVAL_GATE.result.v1.json",
    "N10_HARNESS_PROTOCOL.result.v1.json",
    "N20_PROVIDER_TRANSPORT.result.v1.json",
]

# Recorded once, by hand, from the live files at the start of RC8's own work
# (before any RC8 file was written) -- these are the exact bytes N00/N10 were
# ADMITTED under and N20 was BLOCKED under, and must never change.
ADMITTED_OR_BLOCKED_RESULT_HASHES = {
    "N00_SPEC_APPROVAL_GATE.result.v1.json": "1592643a4d48b011bf5338b77fa949887da960e086ff081907bddd510f65cda6",
    "N10_HARNESS_PROTOCOL.result.v1.json": "a3b678c49c62254517d847b60537e7ed5372b29d81db458f13aadae4ecce7c70",
    "N20_PROVIDER_TRANSPORT.result.v1.json": "894e430aa1c5739d0af638fec10e91f2eaf32f090a917213b1bf7fa2ce5e609a",
}


@pytest.mark.parametrize("filename", ADMITTED_OR_BLOCKED_RESULT_FILES)
def test_admitted_or_blocked_result_file_is_byte_unchanged(filename: str) -> None:
    path = PACKAGE_DIR / "results" / filename
    assert path.is_file()
    assert sha256_file(path) == ADMITTED_OR_BLOCKED_RESULT_HASHES[filename]


def test_graph_v8_result_pattern_never_collides_with_the_legacy_results_root() -> None:
    """The direct proof that the RC8 defect is fixed: graph v8's own
    result_pattern, formatted for every admitted/blocked node, never equals
    the exact legacy path those nodes' real results live at. results/v7/ is
    legitimately a subdirectory of results/ (that is not the defect -- the
    defect was reusing the exact same flat filename), so the proof is exact
    per-node path inequality, not path-prefix disjointness."""

    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    pattern = document["result_pattern"]
    assert pattern.startswith(RESULTS_V8_PREFIX)
    for filename in ADMITTED_OR_BLOCKED_RESULT_FILES:
        node_id = filename.rsplit(".result.v1.json", 1)[0]
        v7_path = pattern.format(node_id=node_id)
        legacy_path = f"{LEGACY_RESULTS_PREFIX}{filename}"
        assert v7_path != legacy_path
        assert (REPO_ROOT / v7_path).resolve() != (REPO_ROOT / legacy_path).resolve()


@pytest.mark.parametrize("node_id", ["N00_SPEC_APPROVAL_GATE", "N10_HARNESS_PROTOCOL", "N20_PROVIDER_TRANSPORT"])
def test_validate_result_v2_reports_missing_not_a_collision_for_admitted_nodes(node_id: str) -> None:
    """The live validator (bound to graph v8's own results/v7/ root) must
    honestly report the v7 result as missing for these three already-admitted
    nodes -- never fabricate a pass by reading the legacy v5-lineage file at
    the old path, and never raise from an accidental write. This is the
    behavioral proof that no code path in this validator can be tricked into
    treating the legacy file as this generation's own result."""

    code, payload = run([str(VALIDATE_RESULT_V2), "--node", node_id])
    assert code == 1
    assert payload["valid"] is False
    assert "missing result" in payload["error"]
    assert "results/v8" in payload["error"]


def test_graph_v8_carries_the_modified_recovery_input_in_versioned_form() -> None:
    """The live-mutated v7 bytes are recovery input, never an admission target.
    V8 preserves their approved topology and ownership corrections while moving
    operational bindings to v8."""

    recovered = yaml.safe_load(RECOVERY_GRAPH_V7_MODIFIED.read_text(encoding="utf-8"))
    v8 = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))

    assert sha256_file(APPROVED_GRAPH_V7) == "b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22"
    assert sha256_file(RECOVERY_GRAPH_V7_MODIFIED) == "b6c17e81c6e32f32b86183d4577fe9a18894c0657504eca832e36d7daa17865e"
    assert recovered["edges"] == v8["edges"]
    assert recovered["terminals"] == v8["terminals"]
    assert recovered["rules"]["forbidden_production_scan"] == v8["rules"]["forbidden_production_scan"]
    assert recovered["rules"]["retired_provider_test_scan"] == v8["rules"]["retired_provider_test_scan"]

    for node_id, recovered_node in recovered["nodes"].items():
        v8_node = v8["nodes"][node_id]
        assert recovered_node["depends_on"] == v8_node["depends_on"]
        assert recovered_node.get("read_only_inputs", []) == v8_node.get("read_only_inputs", [])
        assert recovered_node["allowed_results"] == v8_node["allowed_results"]

        def _non_result_writes(writes: list[str]) -> set[str]:
            return {w for w in writes if "/results/" not in w}

        assert _non_result_writes(recovered_node["writes"]) == _non_result_writes(v8_node["writes"])


def test_graph_v8_result_writes_are_the_recovery_writes_moved_under_results_v8() -> None:
    recovered = yaml.safe_load(RECOVERY_GRAPH_V7_MODIFIED.read_text(encoding="utf-8"))
    v8 = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    for node_id, recovered_node in recovered["nodes"].items():
        v8_node = v8["nodes"][node_id]
        recovered_results = {w for w in recovered_node["writes"] if "/results/" in w}
        v8_results = {w for w in v8_node["writes"] if "/results/" in w}
        expected_v8 = {w.replace("/results/v7/", "/results/v8/") for w in recovered_results}
        assert v8_results == expected_v8


# --------------------------------------------- N20V2-F01: scan-scope narrowing
#
# The real N20 execution against implementation.graph.v5.yaml reached a
# genuine BLOCKED (finding N20V2-F01):
# rules.retired_provider_test_scan.scan_roots was ['tests/runtime'], walked
# recursively, and caught 16 occurrences of "gemini" in exactly two files --
# tests/runtime/test_gemini.py and tests/runtime/test_capabilities.py -- that
# test a wholly separate, still-active Plan 11/19/20/21 Gemini pipeline this
# migration does not own. implementation.graph.v6.yaml fixes this by making
# scan_roots an explicit, exact list of every migration-owned active test
# file across N20-N60, instead of a directory to walk. These tests prove the
# fix against the real repository and real graph, not a synthetic fixture --
# scan_node.py's own scanning logic is unmodified (checked at the top of this
# file); only the graph's configured scan_roots value changed.

GEMINI_TEST = "tests/runtime/test_gemini.py"
CAPABILITIES_TEST = "tests/runtime/test_capabilities.py"

MIGRATION_OWNED_TEST_FILES_BY_NODE = {
    "N20_PROVIDER_TRANSPORT": [
        "tests/runtime/test_plan26_transport.py",
        "tests/runtime/test_plan26_model_nodes.py",
        "tests/runtime/test_plan26_egress.py",
        "tests/runtime/test_curriculum_factory_graph.py",
        "tests/runtime/test_plan26_adversarial.py",
        "tests/runtime/test_plan26_api_contract.py",
        "tests/runtime/test_plan26_lock_drift.py",
    ],
    "N30_PREFLIGHT_EGRESS": [
        "tests/runtime/test_plan26_cli.py",
        "tests/runtime/test_plan26_deterministic_nodes.py",
        "tests/runtime/test_run_curriculum.py",
    ],
    "N40_INTEGRATION_OWNERSHIP": [
        "tests/runtime/test_plan26_topology.py",
        "tests/runtime/test_plan26_unit_graph.py",
        "tests/runtime/test_plan26_repair_acceptance.py",
        "tests/runtime/test_plan26_workbook.py",
    ],
    "N50_EVIDENCE_AUDIT_CONTROLS": [
        "tests/runtime/test_plan26_evidence.py",
        "tests/runtime/test_plan26_persistence.py",
    ],
    "N60_ADVERSARIAL_REGRESSION": [
        "tests/runtime/test_plan27_adversarial.py",
    ],
}


def test_n20_write_set_no_longer_owns_the_unrelated_gemini_pipeline_tests() -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    writes = document["nodes"]["N20_PROVIDER_TRANSPORT"]["writes"]
    assert GEMINI_TEST not in writes
    assert CAPABILITIES_TEST not in writes


def test_no_node_in_the_graph_owns_the_unrelated_gemini_pipeline_tests() -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    for node_id, node in document["nodes"].items():
        writes = node.get("writes", [])
        assert GEMINI_TEST not in writes, f"{node_id} unexpectedly owns {GEMINI_TEST}"
        assert CAPABILITIES_TEST not in writes, f"{node_id} unexpectedly owns {CAPABILITIES_TEST}"


def test_retired_provider_test_scan_scan_roots_is_the_explicit_migration_owned_union() -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    scan_roots = document["rules"]["retired_provider_test_scan"]["scan_roots"]
    expected = sorted(
        path for paths in MIGRATION_OWNED_TEST_FILES_BY_NODE.values() for path in paths
    )
    assert sorted(scan_roots) == expected
    assert GEMINI_TEST not in scan_roots
    assert CAPABILITIES_TEST not in scan_roots


def test_scan_roots_are_directory_free_explicit_file_paths() -> None:
    """N20V2-F01's root cause was scan_roots naming a directory
    (tests/runtime) walked recursively. Prove every entry is a .py file path,
    never a directory."""

    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    scan_roots = document["rules"]["retired_provider_test_scan"]["scan_roots"]
    for root in scan_roots:
        assert root.endswith(".py"), root
        assert not (REPO_ROOT / root).is_dir(), root


@pytest.mark.parametrize("node_id", sorted(MIGRATION_OWNED_TEST_FILES_BY_NODE))
def test_node_scoped_scan_covers_exactly_its_own_migration_owned_test_files(node_id: str) -> None:
    """Real repo, real graph v6: node-scoped mode must scan exactly this
    node's own migration-owned test files (or, for N60's future file, none
    yet on disk) -- never the unrelated Gemini-pipeline tests, never another
    node's files."""

    graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
    report = scanner.run_node(graph, node_id)
    tests_scope = next(scope for scope in report["scopes"] if scope["scope"] == "tests")
    expected = {
        path for path in MIGRATION_OWNED_TEST_FILES_BY_NODE[node_id] if (REPO_ROOT / path).is_file()
    }
    assert set(tests_scope["scanned_files"]) == expected
    assert GEMINI_TEST not in tests_scope["scanned_files"]
    assert CAPABILITIES_TEST not in tests_scope["scanned_files"]


def test_n20_real_node_scoped_scan_is_the_regression_proof_that_n20v2_f01_is_fixed() -> None:
    """PKGV2-T22(a): the whole point of graph v6 is that N20's real
    node-scoped command -- which reached a genuine BLOCKED with 16 violations
    under graph v5 -- now passes cleanly. N30/N40/N50 legitimately still
    surface pre-existing, unrelated 'gemini'/'google' occurrences in their own
    test assertions (proven separately by
    test_complete_tree_mode_against_the_real_repo_reports_the_known_pre_remediation_debt),
    so only N20 -- the node this recovery cycle actually corrects -- is
    asserted zero-violations here; asserting it for every node would be
    false."""

    graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
    report = scanner.run_node(graph, "N20_PROVIDER_TRANSPORT")
    assert report["valid"] is True
    assert report["violations"] == []
    for scope in report["scopes"]:
        assert scope["violations"] == []


def test_complete_tree_mode_never_scans_the_unrelated_gemini_pipeline_tests() -> None:
    graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
    report = scanner.run_complete_tree(graph)
    tests_scope = next(scope for scope in report["scopes"] if scope["scope"] == "tests")
    assert GEMINI_TEST not in tests_scope["scanned_files"]
    assert CAPABILITIES_TEST not in tests_scope["scanned_files"]
    # N60's own future file does not exist yet -- scanning silently omits it
    # rather than erroring, and every other entry that does exist is covered.
    expected = {
        path
        for paths in MIGRATION_OWNED_TEST_FILES_BY_NODE.values()
        for path in paths
        if (REPO_ROOT / path).is_file()
    }
    assert set(tests_scope["scanned_files"]) == expected


def test_n60_adversarial_file_causes_no_scan_error_in_either_mode() -> None:
    """The prior v7 N60 produced this migration-owned file. Its presence must
    be scanned cleanly without changing v7's historical admission status."""

    graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
    future_file = REPO_ROOT / "tests/runtime/test_plan27_adversarial.py"
    assert future_file.is_file()
    for node_id in MIGRATION_OWNED_TEST_FILES_BY_NODE:
        scanner.run_node(graph, node_id)  # must not raise
    scanner.run_complete_tree(graph)  # must not raise


@pytest.mark.parametrize(
    "node_id,relative_path",
    [
        ("N20_PROVIDER_TRANSPORT", "tests/runtime/test_plan26_transport.py"),
        ("N30_PREFLIGHT_EGRESS", "tests/runtime/test_plan26_cli.py"),
        ("N40_INTEGRATION_OWNERSHIP", "tests/runtime/test_plan26_topology.py"),
        ("N50_EVIDENCE_AUDIT_CONTROLS", "tests/runtime/test_plan26_evidence.py"),
    ],
)
def test_seeded_violation_in_a_migration_owned_file_is_caught_by_its_node_scoped_scan(
    node_id: str, relative_path: str
) -> None:
    target = REPO_ROOT / relative_path
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text(original + "\n# gemini\n", encoding="utf-8")
        graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
        report = scanner.run_node(graph, node_id)
        assert not report["valid"]
        assert any(item["path"] == relative_path for item in report["violations"])
    finally:
        target.write_text(original, encoding="utf-8")


@pytest.mark.parametrize(
    "relative_path",
    [
        "tests/runtime/test_plan26_transport.py",
        "tests/runtime/test_plan26_cli.py",
        "tests/runtime/test_plan26_topology.py",
        "tests/runtime/test_plan26_evidence.py",
    ],
)
def test_seeded_violation_in_a_migration_owned_file_is_caught_by_complete_tree_scan(relative_path: str) -> None:
    target = REPO_ROOT / relative_path
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text(original + "\n# gemini\n", encoding="utf-8")
        graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
        report = scanner.run_complete_tree(graph)
        assert not report["valid"]
        assert any(item["path"] == relative_path for item in report["violations"])
    finally:
        target.write_text(original, encoding="utf-8")


@pytest.mark.parametrize("relative_path", [GEMINI_TEST, CAPABILITIES_TEST])
def test_seeded_violation_in_the_unrelated_gemini_pipeline_tests_is_never_caught(relative_path: str) -> None:
    """Positive proof of the exemption, not merely an absence: a seeded
    violation in test_gemini.py/test_capabilities.py must not fail either
    scan mode, because these files are genuinely outside scan_roots -- not
    merely clean by coincidence today."""

    target = REPO_ROOT / relative_path
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text(original + "\n# freshly seeded gemini violation\n", encoding="utf-8")
        graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
        complete_tree_report = scanner.run_complete_tree(graph)
        assert not any(item["path"] == relative_path for item in complete_tree_report["violations"])
        node_report = scanner.run_node(graph, "N20_PROVIDER_TRANSPORT")
        assert not any(item["path"] == relative_path for item in node_report["violations"])
    finally:
        target.write_text(original, encoding="utf-8")
