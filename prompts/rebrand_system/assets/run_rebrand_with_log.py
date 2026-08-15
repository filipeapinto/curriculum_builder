#!/usr/bin/env python3
"""Runs the rebrand end to end and logs every step to a schema-conformant
execution_log.jsonl (schemas/execution_log.schema.v2.json), using the same
runtime.logger.ExecutionLogger the curriculum runtime itself uses. No
hand-authored log entries: every record is produced by calling .start(),
.complete() or .fail(), which validates each record against the schema
before it is written.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from runtime.logger import ExecutionLogger  # noqa: E402

ASSETS = REPO_ROOT / "prompts" / "rebrand_system" / "assets"
LOG_ROOT = REPO_ROOT / "prompts" / "rebrand_system" / "execution"
SCHEMA_PATH = REPO_ROOT / "schemas" / "execution_log.schema.v2.json"
AUTH_PATHS = [str(REPO_ROOT / "readme.md"), str(ASSETS), str(LOG_ROOT)]

logger = ExecutionLogger(root=LOG_ROOT, schema_path=SCHEMA_PATH)

BASELINE_STATUS = set(
    subprocess.run(["git", "status", "--porcelain=v1", "--", "."], cwd=REPO_ROOT,
                    capture_output=True, text=True).stdout.splitlines()
)


def run_step(*, action: str, action_kind: str, trigger: str, expected: str, cmd: list[str]) -> bool:
    start_id = logger.start(
        action=action, action_kind=action_kind, authorized_paths=AUTH_PATHS,
        trigger=trigger, expected=expected,
    )
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if proc.returncode == 0:
        logger.complete(start_id, result=f"exit 0: {proc.stdout.strip()[:500] or 'ok'}")
        return True
    logger.fail(
        start_id, failure_type="tool-error",
        what_failed=f"exit {proc.returncode}: {proc.stderr.strip()[:500] or proc.stdout.strip()[:500]}",
        expected=expected,
    )
    return False


def run_test(*, action: str, trigger: str, expected: str, check) -> bool:
    """check() returns (passed: bool, detail: str)."""
    start_id = logger.start(
        action=action, action_kind="test", authorized_paths=AUTH_PATHS,
        trigger=trigger, expected=expected,
    )
    passed, detail = check()
    if passed:
        logger.complete(start_id, result=detail[:500] or "pass")
        return True
    logger.fail(start_id, failure_type="wrong-output", what_failed=detail[:500] or "test failed", expected=expected)
    return False


def test_only_authorized_files_changed() -> tuple[bool, str]:
    allowed_files = {"readme.md"}
    targets_txt = ASSETS / "targets.v1.txt"
    if targets_txt.exists():
        allowed_files |= {ln.strip() for ln in targets_txt.read_text().splitlines()
                           if ln.strip() and not ln.startswith("#")}
    out = subprocess.run(["git", "status", "--porcelain=v1", "--", "."], cwd=REPO_ROOT,
                          capture_output=True, text=True).stdout
    current = set(out.splitlines())
    new_lines = current - BASELINE_STATUS

    def is_allowed(line: str) -> bool:
        if "prompts/rebrand_system/assets/" in line or "prompts/rebrand_system/execution/" in line:
            return True
        path = line[3:].strip()
        return path in allowed_files

    stray = [ln for ln in new_lines if not is_allowed(ln)]
    return (not stray, "no stray changes" if not stray else "stray: " + "; ".join(sorted(stray)))


def test_zero_remaining_targets() -> tuple[bool, str]:
    subprocess.run([str(ASSETS / "find_old_name_references.sh")], cwd=REPO_ROOT, check=True,
                    capture_output=True, text=True)
    lines = (ASSETS / "targets.v1.txt").read_text().splitlines()
    data_lines = [ln for ln in lines if ln.strip() and not ln.startswith("#")]
    return (not data_lines, "zero targets" if not data_lines else f"remaining: {data_lines}")


def test_readme_clean() -> tuple[bool, str]:
    text = (REPO_ROOT / "readme.md").read_text()
    if "Curriculum Factory" not in text:
        return False, "brand string missing"
    if "curriculum-neutral pipeline for producing" in text:
        return False, "old self-description still present"
    import re
    missing = []
    for p in re.findall(r"`([^`]*/[^`]*)`", text):
        if p.endswith("/"):
            continue  # generic directory mention, not a path reference
        if not (REPO_ROOT / p).exists():
            missing.append(p)
    if missing:
        return False, f"orphan paths: {missing}"
    return True, "brand present, no orphan paths"


def test_code_identifiers_untouched() -> tuple[bool, str]:
    out = subprocess.run(
        ["git", "diff", "--stat", "--", "runtime/langgraph_factory/egress.py",
         "tests/runtime/test_plan26_egress.py"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    ).stdout.strip()
    return (not out, "untouched" if not out else out)


def test_repo_identity_untouched() -> tuple[bool, str]:
    remote = subprocess.run(["git", "remote", "-v"], cwd=REPO_ROOT, capture_output=True, text=True).stdout
    first_line = (REPO_ROOT / "readme.md").read_text().splitlines()[0]
    ok = "curriculum_builder" in remote and first_line == "# curriculum_builder"
    return (ok, f"remote={'ok' if 'curriculum_builder' in remote else 'BAD'}, "
                f"title={first_line!r}")


def main() -> int:
    ok = True
    ok &= run_step(
        action="Run find_old_name_references.sh to regenerate rebrand target lists",
        action_kind="command", trigger="rebrand_curriculum_factory.prompt.v1.md LOOP step 1",
        expected="targets.v1.txt, readme_targets.v1.txt, repo_wide_context.v1.txt regenerated",
        cmd=[str(ASSETS / "find_old_name_references.sh")],
    )
    ok &= run_step(
        action="Run apply_rebrand.sh to apply the Curriculum Factory rebrand mechanically",
        action_kind="file_write", trigger="rebrand_curriculum_factory.prompt.v1.md LOOP step 2",
        expected="target files and readme.md rebranded in place",
        cmd=[str(ASSETS / "apply_rebrand.sh")],
    )
    ok &= run_test(action="TEST 1: only authorized files changed",
                    trigger="rebrand_curriculum_factory.prompt.v1.md TESTS #1",
                    expected="git status shows changes only under assets/ or execution/, plus rebranded targets",
                    check=test_only_authorized_files_changed)
    ok &= run_test(action="TEST 2: re-running the finder now finds zero remaining live targets",
                    trigger="rebrand_curriculum_factory.prompt.v1.md TESTS #2",
                    expected="targets.v1.txt has zero non-comment lines",
                    check=test_zero_remaining_targets)
    ok &= run_test(action="TEST 3: readme.md carries the brand and has no orphan paths",
                    trigger="rebrand_curriculum_factory.prompt.v1.md TESTS #3",
                    expected="Curriculum Factory present, old self-description gone, all backtick paths resolve",
                    check=test_readme_clean)
    ok &= run_test(action="TEST 4: code identifiers untouched",
                    trigger="rebrand_curriculum_factory.prompt.v1.md TESTS #4",
                    expected="egress.py and its test have no diff",
                    check=test_code_identifiers_untouched)
    ok &= run_test(action="TEST 5: repo/remote identity untouched",
                    trigger="rebrand_curriculum_factory.prompt.v1.md TESTS #5",
                    expected="git remote and readme.md title still say curriculum_builder",
                    check=test_repo_identity_untouched)

    audit = logger.audit()
    print("audit:", audit)
    print("PASS" if ok and not audit["unclosed_starts"] else "FAIL")
    return 0 if ok and not audit["unclosed_starts"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
