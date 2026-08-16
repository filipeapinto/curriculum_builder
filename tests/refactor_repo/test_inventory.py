"""Executable acceptance tests for tools/refactor_repo/inventory.py and baseline.py.

These exercise the P00 inventory tool against this repository's own real state
(never a mock), plus one synthetic tmp_path git repository for the
unresolved-directory stop condition, which needs a directory the tool's fixed
classification table cannot have anticipated.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import uuid
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL_DIR = REPO_ROOT / "tools" / "refactor_repo"
SCHEMA_PATH = REPO_ROOT / "schemas" / "repository_refactor_inventory.schema.v1.json"
INVENTORY_SCRIPT = TOOL_DIR / "inventory.py"
BASELINE_SCRIPT = TOOL_DIR / "baseline.py"

sys.path.insert(0, str(TOOL_DIR))
import collectors  # noqa: E402
import inventory  # noqa: E402


def _run_inventory(output_dir: Path, extra_args: list[str] | None = None) -> tuple[int, dict]:
    args = [sys.executable, str(INVENTORY_SCRIPT), "--repo-root", str(REPO_ROOT),
            "--output-dir", str(output_dir)]
    if extra_args:
        args += extra_args
    result = subprocess.run(args, capture_output=True, text=True, timeout=180)
    try:
        summary = json.loads(result.stdout)
    except json.JSONDecodeError:
        summary = {}
    return result.returncode, summary


@pytest.fixture(scope="module")
def inventory_document(tmp_path_factory) -> dict:
    output_dir = tmp_path_factory.mktemp("inventory_doc")
    returncode, summary = _run_inventory(output_dir)
    assert returncode == 0, f"inventory run failed: {summary}"
    json_path = Path(summary["json_report"])
    return json.loads(json_path.read_text(encoding="utf-8"))


# --- test 2: machine output validates and carries reproducibility metadata ---

def test_machine_report_validates_against_schema(inventory_document):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(inventory_document)


def test_provenance_fields_present_and_truthful(inventory_document):
    prov = inventory_document["provenance"]
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", prov["generated_at_utc"])
    assert len(prov["repository_commit"]) >= 7
    assert isinstance(prov["dirty_state"]["is_dirty"], bool)
    assert isinstance(prov["dirty_state"]["changed_paths"], list)
    assert "python" in prov["tool_versions"] and "git" in prov["tool_versions"]
    assert prov["command"]
    assert isinstance(prov["configuration"], dict)
    assert prov["configuration"]["scan_file_count"] > 0
    assert prov["omissions"] == []
    assert prov["collection_failures"] == []
    assert prov["complete"] is True


# --- test 1 (fault-injection half): omission named, nonzero exit ---

def test_fault_injection_names_omission_and_exits_nonzero(tmp_path):
    returncode, summary = _run_inventory(tmp_path, ["--fail-collector", "schema_identifiers"])
    assert returncode == 1
    assert summary["complete"] is False
    collectors_named = {o["collector"] for o in summary["omissions"]}
    assert "schema_identifiers" in collectors_named
    assert summary["counts"]["schema_identifiers"] == 0


# --- test 1 (read-only half): a successful run does not mutate the repo ---

def test_inventory_run_does_not_mutate_repo_tracked_state(tmp_path):
    before = subprocess.run(
        ["git", "status", "--porcelain=v1", "--ignored=matching", "-uall"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    ).stdout
    returncode, _ = _run_inventory(tmp_path)
    assert returncode == 0
    after = subprocess.run(
        ["git", "status", "--porcelain=v1", "--ignored=matching", "-uall"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    ).stdout
    assert before == after, "inventory run changed the repository's git status"


# --- test 3: inventory covers the complete specification surface ---

def test_directories_cover_every_top_level_directory(inventory_document):
    actual_dirs = {
        p.name for p in REPO_ROOT.iterdir()
        if p.is_dir() and p.name != ".git" and p.name not in collectors.ALWAYS_SKIP_DIR_NAMES
    }
    reported_dirs = {
        d["path"].rstrip("/") for d in inventory_document["directories"]
        if d["path"].rstrip("/") not in collectors.ALWAYS_SKIP_DIR_NAMES
    }
    assert actual_dirs == reported_dirs
    for entry in inventory_document["directories"]:
        assert entry["owner_or_reader"]
        assert entry["tracked_state"] in {"tracked", "ignored", "mixed", "untracked"}
        assert entry["lifecycle_class"] != "unresolved"
        assert entry["proposed_disposition"]
        assert len(entry["evidence"]) >= 1


def test_python_surface_finds_real_runtime_imports(inventory_document):
    ps = inventory_document["python_surface"]
    assert len(ps["runtime_imports"]) > 0
    sample = ps["runtime_imports"][0]
    assert (REPO_ROOT / sample["source_file"]).exists()
    assert "runtime" in sample["statement"]
    # No hardcoded absolute checkout paths were found in production Python at
    # collection time; this is a positive finding, not an omission.
    assert isinstance(ps["absolute_checkout_paths"], list)


def test_old_identity_references_cover_declared_identities(inventory_document):
    identities_found = {r["identity"] for r in inventory_document["old_identity_references"]}
    assert identities_found <= {i["identity"] for i in inventory_document["identities"]}
    assert "Repository slug" in identities_found
    assert "Python package" in identities_found


def test_structured_configuration_covers_packaging_and_ci(inventory_document):
    paths = {c["path"] for c in inventory_document["structured_configuration"]}
    assert "pyproject.toml" in paths
    assert ".github/workflows/plan26-lock-drift.yml" in paths
    pyproject = next(c for c in inventory_document["structured_configuration"] if c["path"] == "pyproject.toml")
    assert pyproject["present"] is False  # packaging skeleton (P01) has not run yet


def test_test_subtrees_cover_every_tests_subdirectory(inventory_document):
    actual = {
        p.name for p in (REPO_ROOT / "tests").iterdir()
        if p.is_dir() and p.name not in collectors.ALWAYS_SKIP_DIR_NAMES
    }
    reported = {t["path"].split("/")[1] for t in inventory_document["test_subtrees"]}
    assert actual == reported
    for entry in inventory_document["test_subtrees"]:
        assert entry["scope"]
        assert isinstance(entry["environment_needs"], list)
        assert isinstance(entry["ci_lane"], list)
        assert isinstance(entry["direct_references"], list)


def test_schema_identifiers_cover_every_top_level_schema_file(inventory_document):
    actual = {p.name for p in (REPO_ROOT / "schemas").glob("*.json")}
    reported = {Path(s["path"]).name for s in inventory_document["schema_identifiers"]}
    assert actual == reported


def test_environment_records_pip_equivalent_inventory(inventory_document):
    env = inventory_document["environment"]
    assert env["python_version"]
    assert env["platform"]
    assert len(env["installed_packages"]) > 0


# --- test 4: human report and machine report describe the same inventory ---

def test_human_and_machine_reports_share_stable_id_sets(tmp_path):
    output_dir = tmp_path
    returncode, summary = _run_inventory(output_dir)
    assert returncode == 0
    document = json.loads(Path(summary["json_report"]).read_text(encoding="utf-8"))
    human_text = Path(summary["human_report"]).read_text(encoding="utf-8")

    # id -> disposition, straight from the machine report.
    recomputed = inventory.compute_stable_ids(document)

    appendix_match = re.search(r"## Stable item identifier appendix.*?```\n(.*?)```", human_text, re.S)
    assert appendix_match, "human report is missing the machine-comparable stable-id appendix"
    appendix: dict[str, str] = {}
    for line in appendix_match.group(1).splitlines():
        if not line.strip():
            continue
        stable_id, _, disposition = line.partition("\t")
        appendix[stable_id] = disposition

    # render_human_report() flattens embedded newlines/tabs in each appendix
    # row (see inventory.py) before writing it out, so the machine-side value
    # must be flattened the same way for an exact, non-lossy comparison.
    def _flatten(value: object) -> str:
        return str(value).replace("\n", " ").replace("\t", " ")

    recomputed_flat = {stable_id: _flatten(disposition) for stable_id, disposition in recomputed.items()}

    # The prompt's test 4 requires the human and machine reports to describe
    # the *same* inventory: not just the same set of stable item identifiers,
    # but the same disposition recorded against each one. Comparing only the
    # id keys (as an earlier version of this test did, via `set(recomputed)`,
    # which silently drops dict values) would pass even if the human report's
    # appendix carried a stale or wrong disposition for a shared id.
    assert set(appendix) == set(recomputed_flat), "stable-id sets differ between human and machine reports"
    assert appendix == recomputed_flat, "dispositions differ between human and machine reports for a shared id"


# --- unresolved-directory stop condition ---

def test_collect_directories_stops_on_unresolved_top_level_directory(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp_path, check=True)
    mystery = tmp_path / "mystery_directory"
    mystery.mkdir()
    (mystery / "a.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=tmp_path, check=True)

    with pytest.raises(collectors.CollectorUnavailable, match="mystery_directory"):
        collectors.collect_directories(tmp_path)


def test_collect_test_subtrees_stops_on_unresolved_subtree(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp_path, check=True)
    tests_dir = tmp_path / "tests"
    unknown = tests_dir / "unknown_subtree"
    unknown.mkdir(parents=True)
    (unknown / "a.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=tmp_path, check=True)

    with pytest.raises(collectors.CollectorUnavailable, match="unknown_subtree"):
        collectors.collect_test_subtrees(tmp_path, [])


# --- test 5: behavioral baseline is executable and comparable ---

def test_baseline_capture_and_compare_are_equivalent_on_unchanged_repo(tmp_path):
    args_first = [sys.executable, str(BASELINE_SCRIPT), "capture", "--repo-root", str(REPO_ROOT),
                  "--output-dir", str(tmp_path), "--label", "a"]
    result_first = subprocess.run(args_first, capture_output=True, text=True, timeout=180)
    assert result_first.returncode == 0, result_first.stderr

    args_second = [sys.executable, str(BASELINE_SCRIPT), "capture", "--repo-root", str(REPO_ROOT),
                    "--output-dir", str(tmp_path), "--label", "b"]
    result_second = subprocess.run(args_second, capture_output=True, text=True, timeout=180)
    assert result_second.returncode == 0, result_second.stderr

    first_path = json.loads(result_first.stdout)["output"]
    second_path = json.loads(result_second.stdout)["output"]

    compare_out = tmp_path / "compare.json"
    args_compare = [sys.executable, str(BASELINE_SCRIPT), "compare",
                     "--first", first_path, "--second", second_path, "--output", str(compare_out)]
    result_compare = subprocess.run(args_compare, capture_output=True, text=True, timeout=60)
    comparison = json.loads(result_compare.stdout)
    assert comparison["verdict"] == "EQUIVALENT", comparison["differences"]
    assert result_compare.returncode == 0


def test_baseline_compare_detects_changed_behavior(tmp_path):
    """Test 5's expected outcome is that the baseline "can distinguish equivalent
    from changed behavior" -- the two tests above only ever compare unchanged
    captures, so they can prove EQUIVALENT works but never prove CHANGED does.
    This test captures a pristine checkout, deliberately perturbs one of the
    representative artifacts baseline.py hashes, captures again, and asserts
    `compare` reports a real difference and a non-EQUIVALENT verdict.

    The scratch checkout is a disposable linked git worktree created as a
    sibling of this repository's own working directory (never inside it, and
    never committed to), removed in `finally` regardless of outcome.
    """
    worktree = REPO_ROOT.parent / f"p00-baseline-changed-behavior-{uuid.uuid4().hex[:8]}"
    try:
        subprocess.run(
            ["git", "worktree", "add", "--detach", str(worktree), "HEAD"],
            cwd=REPO_ROOT, check=True, capture_output=True, text=True, timeout=120,
        )

        out_dir = tmp_path / "changed_behavior"
        args_pristine = [sys.executable, str(BASELINE_SCRIPT), "capture", "--repo-root", str(worktree),
                          "--output-dir", str(out_dir), "--label", "pristine"]
        result_pristine = subprocess.run(args_pristine, capture_output=True, text=True, timeout=180)
        assert result_pristine.returncode == 0, result_pristine.stderr
        pristine_path = json.loads(result_pristine.stdout)["output"]

        # Deliberately perturb one of baseline.py's own representative
        # artifacts, inside the disposable worktree only. This is a real
        # behavioral change to what capture() hashes, not a synthetic edit of
        # a captured JSON document after the fact.
        import baseline as baseline_module  # local import: sys.path already has tools/refactor_repo
        target_relative = baseline_module.REPRESENTATIVE_ARTIFACTS[0]
        target = worktree / target_relative
        assert target.exists(), f"expected representative artifact missing in scratch worktree: {target}"
        original_bytes = target.read_bytes()
        target.write_bytes(original_bytes + b"\n# perturbed by test_baseline_compare_detects_changed_behavior\n")

        args_perturbed = [sys.executable, str(BASELINE_SCRIPT), "capture", "--repo-root", str(worktree),
                           "--output-dir", str(out_dir), "--label", "perturbed"]
        result_perturbed = subprocess.run(args_perturbed, capture_output=True, text=True, timeout=180)
        assert result_perturbed.returncode == 0, result_perturbed.stderr
        perturbed_path = json.loads(result_perturbed.stdout)["output"]

        compare_out = out_dir / "compare_changed.json"
        args_compare = [sys.executable, str(BASELINE_SCRIPT), "compare",
                         "--first", pristine_path, "--second", perturbed_path, "--output", str(compare_out)]
        result_compare = subprocess.run(args_compare, capture_output=True, text=True, timeout=60)
        comparison = json.loads(result_compare.stdout)

        assert comparison["verdict"] == "CHANGED", "compare() failed to detect a deliberately changed artifact"
        assert result_compare.returncode == 1
        diff_fields = {d["field"] for d in comparison["differences"]}
        assert "representative_artifacts (path->sha256 map)" in diff_fields
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(worktree)],
                        cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)
        subprocess.run(["git", "worktree", "prune"], cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)
