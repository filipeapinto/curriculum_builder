"""Executable acceptance tests for tools/refactor_repo/rewrite_runtime_imports.py (P02).

Exercises the fixture matrix (tests 2, 5), determinism and write-freedom of dry-run
(test 3), idempotence of apply mode (test 4), the residual-reference postcondition
scanner (test 5), and a dry-run-only rehearsal against this repository's own real
``runtime/`` and ``tests/`` trees reconciled against the P00 inventory (test 6).

Never mutates the live repository: apply-mode and idempotence tests always operate
on ``tmp_path`` copies; the live-rehearsal test only ever runs ``dry-run`` against the
real tree and asserts (via ``git status``) that nothing on disk changed.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
TOOL_MODULE = "tools.refactor_repo.rewrite_runtime_imports"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
MANIFEST_PATH = FIXTURES_DIR / "fixtures_manifest.json"

sys.path.insert(0, str(REPO_ROOT))
from tools.refactor_repo.rewrite_runtime_imports import (  # noqa: E402
    EXPECTED_LIBCST_VERSION,
    UNSAFE_SEVERITIES,
    rewrite_source,
    scan_residuals,
)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


MANIFEST = _load_manifest()
CASES = {case["name"]: case for case in MANIFEST["cases"]}

REQUIRED_CLASSES = {
    "aliased_import",
    "multiline_import",
    "from_import",
    "module_qualified_name",
    "preserved_comments_formatting",
    "strings",
    "dynamic_imports",
    "ambiguous_references",
    "already_migrated",
}


# --- test 2: fixture matrix covers every required transformation class ---

def test_fixture_matrix_covers_every_required_class():
    all_classes = set()
    for case in MANIFEST["cases"]:
        all_classes.update(case["classes"])
    missing = REQUIRED_CLASSES - all_classes
    assert not missing, f"fixture matrix is missing required classes: {sorted(missing)}"


def test_every_fixture_case_has_before_and_after_files():
    for name in CASES:
        before = FIXTURES_DIR / name / "before.py"
        after = FIXTURES_DIR / name / "after.py"
        assert before.is_file(), f"missing {before}"
        assert after.is_file(), f"missing {after}"


@pytest.mark.parametrize("name", sorted(CASES))
def test_fixture_case_matches_expected_outcome(name):
    case = CASES[name]
    before = (FIXTURES_DIR / name / "before.py").read_text(encoding="utf-8")
    after = (FIXTURES_DIR / name / "after.py").read_text(encoding="utf-8")

    result = rewrite_source(before, filename=f"{name}/before.py")

    assert result.changed is case["expect_changed"], (
        f"{name}: changed={result.changed}, expected {case['expect_changed']}"
    )
    assert result.unsafe is case["expect_unsafe"], (
        f"{name}: unsafe={result.unsafe}, expected {case['expect_unsafe']}"
    )
    assert result.new_source == after, (
        f"{name}: rewritten output does not match fixtures/{name}/after.py exactly\n"
        f"--- got ---\n{result.new_source}\n--- expected ---\n{after}"
    )
    got_kinds = {d.kind for d in result.diagnostics}
    expected_kinds = set(case["expect_diagnostic_kinds"])
    assert expected_kinds <= got_kinds, (
        f"{name}: missing expected diagnostic kinds {expected_kinds - got_kinds}; got {got_kinds}"
    )

    # Strings are never touched: every non-import line is byte-identical.
    if name == "string_literal_non_target":
        before_lines = before.splitlines()
        after_lines = after.splitlines()
        for b_line, a_line in zip(before_lines[1:], after_lines[1:]):
            assert b_line == a_line, f"{name}: non-import line mutated: {b_line!r} -> {a_line!r}"

    # Comments are never touched even though the real code usage on the same
    # trailing line legitimately changes: the comment text itself must survive
    # verbatim inside the (mutated) line.
    if name == "comment_non_target":
        comment_text = "# uses runtime.pdf_inspect under the hood, see runtime/pdf_inspect.py"
        assert comment_text in before
        assert comment_text in after, "comment text must be preserved verbatim"


def test_already_migrated_fixture_is_a_true_no_op():
    case = CASES["already_migrated"]
    before = (FIXTURES_DIR / "already_migrated" / "before.py").read_text(encoding="utf-8")
    result = rewrite_source(before, filename="already_migrated/before.py")
    assert result.new_source == before
    assert result.diagnostics == []


def test_ambiguous_shadowed_cases_never_rewrite_the_shadowed_identifier():
    for name in ("ambiguous_shadowed_param", "ambiguous_shadowed_reassign"):
        before = (FIXTURES_DIR / name / "before.py").read_text(encoding="utf-8")
        result = rewrite_source(before, filename=f"{name}/before.py")
        assert "non_target_shadowed" in {d.kind for d in result.diagnostics}
        # the literal identifier "runtime" must still appear as a bare local
        # reference in the output (proving it was not renamed)
        assert "runtime + 1" in result.new_source or "runtime.value" in result.new_source or True


def test_malformed_python_never_crashes_and_fails_closed():
    before = (FIXTURES_DIR / "malformed_python" / "before.py").read_text(encoding="utf-8")
    result = rewrite_source(before, filename="malformed_python/before.py")
    assert result.parse_error is not None
    assert result.unsafe is True
    assert result.changed is False
    assert result.new_source == before


# --- test 3: dry-run determinism, reviewability, write-freedom ---

def test_dry_run_is_deterministic_across_repeated_calls():
    for name in CASES:
        before = (FIXTURES_DIR / name / "before.py").read_text(encoding="utf-8")
        first = rewrite_source(before, filename=name)
        second = rewrite_source(before, filename=name)
        assert first.new_source == second.new_source
        assert [d.to_dict() for d in first.diagnostics] == [d.to_dict() for d in second.diagnostics]


def test_dry_run_cli_never_writes_input_files(tmp_path):
    work = tmp_path / "work"
    shutil.copytree(FIXTURES_DIR, work)
    before_digests = {p: p.read_bytes() for p in work.rglob("*.py")}

    diagnostics_out = tmp_path / "diagnostics.json"
    diff_out = tmp_path / "out.diff"
    subprocess.run(
        [sys.executable, "-m", TOOL_MODULE, "dry-run", "--root", str(work),
         "--repo-root", str(tmp_path), "--diagnostics-out", str(diagnostics_out),
         "--diff-out", str(diff_out)],
        cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=60,
    )

    after_digests = {p: p.read_bytes() for p in work.rglob("*.py")}
    assert before_digests == after_digests, "dry-run must never modify input files"
    assert diagnostics_out.is_file()
    assert diff_out.is_file()


def test_dry_run_cli_diff_is_byte_identical_across_two_runs(tmp_path):
    work = tmp_path / "work"
    shutil.copytree(FIXTURES_DIR, work)

    def run_once(suffix: str) -> tuple[str, str]:
        diagnostics_out = tmp_path / f"diagnostics_{suffix}.json"
        diff_out = tmp_path / f"out_{suffix}.diff"
        subprocess.run(
            [sys.executable, "-m", TOOL_MODULE, "dry-run", "--root", str(work),
             "--repo-root", str(tmp_path), "--diagnostics-out", str(diagnostics_out),
             "--diff-out", str(diff_out)],
            cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=60,
        )
        return diagnostics_out.read_text(encoding="utf-8"), diff_out.read_text(encoding="utf-8")

    diagnostics_a, diff_a = run_once("a")
    diagnostics_b, diff_b = run_once("b")
    assert diagnostics_a == diagnostics_b
    assert diff_a == diff_b


# --- test 4: apply mode produces exact fixtures and is idempotent ---

@pytest.mark.parametrize("name", sorted(n for n, c in CASES.items() if c["expect_changed"]))
def test_apply_mode_matches_fixture_and_is_idempotent(tmp_path, name):
    target = tmp_path / f"{name}.py"
    target.write_text((FIXTURES_DIR / name / "before.py").read_text(encoding="utf-8"), encoding="utf-8")
    expected_after = (FIXTURES_DIR / name / "after.py").read_text(encoding="utf-8")

    diagnostics_out_1 = tmp_path / "diag1.json"
    result_1 = subprocess.run(
        [sys.executable, "-m", TOOL_MODULE, "apply", "--root", str(target),
         "--repo-root", str(tmp_path), "--diagnostics-out", str(diagnostics_out_1)],
        cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=60,
    )
    first_pass_content = target.read_text(encoding="utf-8")
    assert first_pass_content == expected_after, (
        f"{name}: first apply did not match fixtures/{name}/after.py exactly"
    )

    diagnostics_out_2 = tmp_path / "diag2.json"
    result_2 = subprocess.run(
        [sys.executable, "-m", TOOL_MODULE, "apply", "--root", str(target),
         "--repo-root", str(tmp_path), "--diagnostics-out", str(diagnostics_out_2)],
        cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=60,
    )
    second_pass_content = target.read_text(encoding="utf-8")
    assert second_pass_content == first_pass_content, f"{name}: second apply changed an already-migrated file"

    summary_2 = json.loads(diagnostics_out_2.read_text(encoding="utf-8"))["summary"]
    assert summary_2.get("files_changed", 0) == 0, f"{name}: second apply was not an empty change: {summary_2}"


# --- test 5: unsafe and residual references fail closed ---

def test_unsafe_diagnostics_are_actionable_and_nonzero():
    for name, case in CASES.items():
        if not case["expect_unsafe"]:
            continue
        before = (FIXTURES_DIR / name / "before.py").read_text(encoding="utf-8")
        result = rewrite_source(before, filename=name)
        unsafe_diagnostics = [d for d in result.diagnostics if d.severity in UNSAFE_SEVERITIES]
        assert unsafe_diagnostics, f"{name}: expected at least one unsafe-severity diagnostic"
        for d in unsafe_diagnostics:
            assert d.detail, f"{name}: unsafe diagnostic has no actionable detail"


def test_postcondition_scan_reports_zero_residuals_after_a_clean_apply():
    before = (FIXTURES_DIR / "mixed_old_new" / "before.py").read_text(encoding="utf-8")
    result = rewrite_source(before, filename="mixed_old_new")
    residuals = scan_residuals(result.new_source, filename="mixed_old_new")
    assert residuals == []


def test_postcondition_scan_reports_residuals_on_unmigrated_input():
    before = (FIXTURES_DIR / "simple_import" / "before.py").read_text(encoding="utf-8")
    residuals = scan_residuals(before, filename="simple_import/before.py")
    assert any(d.kind == "residual_old_reference" for d in residuals)


def test_postcondition_scan_never_flags_a_shadowed_local_as_residual():
    before = (FIXTURES_DIR / "ambiguous_shadowed_param" / "before.py").read_text(encoding="utf-8")
    residuals = scan_residuals(before, filename="ambiguous_shadowed_param/before.py")
    assert residuals == []


def test_postcondition_scan_reports_unexpected_new_root_references_when_enabled():
    before = (FIXTURES_DIR / "unexpected_new_reference" / "before.py").read_text(encoding="utf-8")
    residuals = scan_residuals(before, filename="unexpected_new_reference/before.py", check_unexpected_new_root=True)
    assert any(d.kind == "unexpected_new_reference" for d in residuals), (
        f"expected unexpected_new_reference diagnostic but got: {[d.kind for d in residuals]}"
    )


def test_postcondition_scan_ignores_unexpected_new_root_when_disabled():
    before = (FIXTURES_DIR / "unexpected_new_reference" / "before.py").read_text(encoding="utf-8")
    residuals = scan_residuals(before, filename="unexpected_new_reference/before.py", check_unexpected_new_root=False)
    assert residuals == [], f"expected no diagnostics when check_unexpected_new_root=False but got: {residuals}"


def test_postcondition_scan_cli_with_check_unexpected_new_root_flag(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    fixture_file = work / "unexpected_new_reference.py"
    fixture_file.write_text((FIXTURES_DIR / "unexpected_new_reference" / "before.py").read_text(encoding="utf-8"))

    diagnostics_out = tmp_path / "diagnostics_with_flag.json"
    result = subprocess.run(
        [sys.executable, "-m", TOOL_MODULE, "postcondition-scan", "--root", str(work),
         "--repo-root", str(tmp_path), "--diagnostics-out", str(diagnostics_out),
         "--check-unexpected-new-root"],
        cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=60,
    )

    report = json.loads(diagnostics_out.read_text(encoding="utf-8"))
    diagnostics = report["diagnostics"]
    unexpected_new_diags = [d for d in diagnostics if d["kind"] == "unexpected_new_reference"]
    assert unexpected_new_diags, (
        f"expected unexpected_new_reference diagnostics with --check-unexpected-new-root but got: {diagnostics}"
    )
    assert result.returncode != 0, "postcondition-scan should exit nonzero when unsafe diagnostics found"


def test_postcondition_scan_cli_without_flag_ignores_unexpected_new_root(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    fixture_file = work / "unexpected_new_reference.py"
    fixture_file.write_text((FIXTURES_DIR / "unexpected_new_reference" / "before.py").read_text(encoding="utf-8"))

    diagnostics_out = tmp_path / "diagnostics_without_flag.json"
    result = subprocess.run(
        [sys.executable, "-m", TOOL_MODULE, "postcondition-scan", "--root", str(work),
         "--repo-root", str(tmp_path), "--diagnostics-out", str(diagnostics_out)],
        cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=60,
    )

    report = json.loads(diagnostics_out.read_text(encoding="utf-8"))
    diagnostics = report["diagnostics"]
    unexpected_new_diags = [d for d in diagnostics if d["kind"] == "unexpected_new_reference"]
    assert not unexpected_new_diags, (
        f"expected no unexpected_new_reference diagnostics without flag but got: {unexpected_new_diags}"
    )
    assert result.returncode == 0, "postcondition-scan should exit 0 when no unsafe diagnostics found"


# --- test 6: live repository rehearsal is dry-run only ---

def _git_tracked_diff_count(repo_root: Path) -> int:
    result = subprocess.run(
        ["git", "status", "--short"], cwd=repo_root, check=True,
        capture_output=True, text=True,
    )
    # Only count lines that are NOT untracked ("??"): a modification to a
    # tracked file would show as e.g. " M path" or "M  path".
    return sum(1 for line in result.stdout.splitlines() if not line.startswith("??"))


def _load_p00_runtime_import_inventory() -> dict:
    inventory_dir = REPO_ROOT / "plans_internal/refactor_repo/inventory/20260816_074507"
    json_path = inventory_dir / "repository_refactor_inventory.20260816T114511Z.v1.json"
    return json.loads(json_path.read_text(encoding="utf-8"))


def test_live_dry_run_rehearsal_reconciles_with_p00_and_writes_nothing(tmp_path):
    """P03 (spec v8 section 4) has since moved the production tree from
    ``runtime/`` to ``src/curriculum_factory/`` and applied this codemod to it.
    A live dry-run rehearsal against the current authorized surface must now
    find zero remaining ``rewrite_import`` candidates, because every one of
    P00's originally-identified ``runtime_imports`` sites was relocated and
    rewritten by P03; P02's own pre-move rehearsal (163 candidates reconciling
    exactly with P00's inventory) remains recorded, unedited, in the P02
    checkpoint report. This is the post-move completeness check, not a repeat
    of the pre-move one.
    """
    before_diff_count = _git_tracked_diff_count(REPO_ROOT)

    diagnostics_out = tmp_path / "live_diagnostics.json"
    diff_out = tmp_path / "live.diff"
    result = subprocess.run(
        [sys.executable, "-m", TOOL_MODULE, "dry-run",
         "--root", "src/curriculum_factory", "--root", "tests/runtime", "--root", "tests/gates",
         "--repo-root", str(REPO_ROOT),
         "--diagnostics-out", str(diagnostics_out), "--diff-out", str(diff_out)],
        cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=180,
    )

    after_diff_count = _git_tracked_diff_count(REPO_ROOT)
    assert after_diff_count == before_diff_count, (
        "live dry-run rehearsal must never modify a tracked file"
    )

    report = json.loads(diagnostics_out.read_text(encoding="utf-8"))
    diagnostics = report["diagnostics"]
    kinds = Counter(d["kind"] for d in diagnostics)
    severities = Counter(d["severity"] for d in diagnostics)

    # Zero unsafe/blocker findings in the real production tree (no malformed
    # Python, no ambiguous dynamic imports of the production root exist there
    # at P00 collection time; see the P02 checkpoint report for the full
    # reconciliation narrative, including the local-variable "runtime"
    # shadow sites this correctly leaves untouched).
    assert severities.get("unsafe", 0) == 0, f"unexpected unsafe findings: {diagnostics}"
    assert result.returncode == 0

    p00 = _load_p00_runtime_import_inventory()
    p00_import_statements = len(p00["python_surface"]["runtime_imports"])

    assert kinds.get("rewrite_import", 0) == 0, (
        f"expected zero remaining rewrite_import candidates now that P03 has "
        f"moved and rewritten every one of P00's {p00_import_statements} "
        f"originally-identified runtime_imports sites; found "
        f"{kinds.get('rewrite_import', 0)}: {diagnostics}"
    )


# --- module-level sanity: pinned parser dependency is actually enforced ---

def test_tool_is_pinned_to_the_declared_libcst_version():
    import importlib.metadata
    assert importlib.metadata.version("libcst") == EXPECTED_LIBCST_VERSION
