"""Plan 26 lock-drift and dependency-audit gate (spec section 3.2).

Three layers, so no single deletion silently disarms the gate:

1. Static audit of requirements/plan26.in and requirements/plan26.lock that runs
   in any environment (no network, no pip-tools).
2. A real regeneration byte-comparison, skipped only when the pinned generator
   or network is unavailable; CI always has both.
3. A static ownership check that .github/workflows/plan26-lock-drift.yml still
   invokes the exact regeneration command and still runs these tests, so
   removing the CI step is itself a caught regression.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IN_PATH = REPO_ROOT / "requirements" / "plan26.in"
LOCK_PATH = REPO_ROOT / "requirements" / "plan26.lock"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "plan26-lock-drift.yml"

PIP_TOOLS_VERSION = "7.6.0"
PIP_VERSION_FOR_GENERATION = "25.3"

# The one canonical regeneration command. CI runs it verbatim; the workflow is
# asserted to contain this exact string.
REGENERATE_COMMAND = (
    "python -m piptools compile --generate-hashes --no-header --strip-extras "
    "--output-file requirements/plan26.lock requirements/plan26.in"
)
DRIFT_COMPARE_COMMAND = "git diff --exit-code -- requirements/plan26.lock"

DIRECT_PINS = {
    "langgraph": "1.2.9",
    "langgraph-checkpoint-sqlite": "3.1.0",
    "jsonschema": "4.26.0",
    "PyYAML": "6.0.3",
    "Pillow": "12.2.0",
    "pytest": "9.0.3",
}

# spec section 3.1 / graph rules.forbidden_production_imports
FORBIDDEN_DISTRIBUTIONS = (
    "langchain",
    "langchain-openai",
    "langchain-google-genai",
    "openai",
    "google-generativeai",
)

PINNED_LINE = re.compile(r"^(?P<name>[A-Za-z0-9._-]+)==(?P<version>[^\s\\]+)")


def _direct_pin_lines():
    return [
        line.strip()
        for line in IN_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _locked_distributions():
    found = {}
    for line in LOCK_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith((" ", "\t", "#")) or not line.strip():
            continue
        match = PINNED_LINE.match(line.strip())
        if match:
            found[match.group("name").lower()] = match.group("version")
    return found


def _generator_available():
    if shutil.which("git") is None:
        return False
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "import importlib.metadata as m; print(m.version('pip-tools'), m.version('pip'))",
        ],
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0:
        return False
    piptools_version, pip_version = probe.stdout.split()
    return piptools_version == PIP_TOOLS_VERSION and pip_version == PIP_VERSION_FOR_GENERATION


class TestDirectPins(unittest.TestCase):
    def test_in_file_declares_exactly_the_specified_pins(self) -> None:
        expected = {f"{name}=={version}" for name, version in DIRECT_PINS.items()}
        self.assertEqual(set(_direct_pin_lines()), expected)

    def test_pytest_is_marked_development_only(self) -> None:
        text = IN_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("development only", text)


class TestLockCompleteness(unittest.TestCase):
    def test_every_direct_pin_is_locked_at_the_pinned_version(self) -> None:
        locked = _locked_distributions()
        for name, version in DIRECT_PINS.items():
            with self.subTest(dist=name):
                self.assertEqual(locked.get(name.lower()), version)

    def test_lock_resolves_the_transitive_closure(self) -> None:
        locked = _locked_distributions()
        # langgraph's own runtime dependencies must be resolved, not floating
        for name in (
            "langgraph-checkpoint",
            "langgraph-prebuilt",
            "langgraph-sdk",
            "langchain-core",
            "aiosqlite",
            "sqlite-vec",
        ):
            with self.subTest(dist=name):
                self.assertIn(name, locked)
        self.assertGreater(len(locked), len(DIRECT_PINS))

    def test_every_locked_distribution_carries_at_least_one_sha256_hash(self) -> None:
        text = LOCK_PATH.read_text(encoding="utf-8")
        blocks = re.split(r"\n(?=[A-Za-z0-9._-]+==)", text)
        checked = 0
        for block in blocks:
            match = PINNED_LINE.match(block.strip())
            if not match:
                continue
            checked += 1
            with self.subTest(dist=match.group("name")):
                self.assertIn("--hash=sha256:", block)
        self.assertEqual(checked, len(_locked_distributions()))

    def test_lock_is_installable_with_require_hashes_semantics(self) -> None:
        # --require-hashes rejects any unpinned requirement; assert none exist.
        for line in LOCK_PATH.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "--hash", "\\")):
                continue
            if stripped.startswith("--"):
                continue
            if PINNED_LINE.match(stripped):
                continue
            self.fail(f"unpinned or unrecognized lock line: {line!r}")


class TestForbiddenDependencyAudit(unittest.TestCase):
    def test_forbidden_distributions_absent_from_lock(self) -> None:
        locked = _locked_distributions()
        for name in FORBIDDEN_DISTRIBUTIONS:
            with self.subTest(dist=name):
                self.assertNotIn(name, locked)

    def test_forbidden_distributions_absent_from_direct_pins(self) -> None:
        declared = {line.split("==")[0].lower() for line in _direct_pin_lines()}
        for name in FORBIDDEN_DISTRIBUTIONS:
            with self.subTest(dist=name):
                self.assertNotIn(name, declared)

    def test_langchain_core_is_transitive_and_langchain_umbrella_is_not(self) -> None:
        locked = _locked_distributions()
        self.assertIn("langchain-core", locked)
        self.assertNotIn("langchain", locked)


class TestDriftDetection(unittest.TestCase):
    """The comparison half of the CI command, exercised in both directions."""

    def _staged_copy(self):
        work = Path(tempfile.mkdtemp(prefix="plan26_drift_"))
        self.addCleanup(shutil.rmtree, work, True)
        (work / "requirements").mkdir()
        shutil.copy2(IN_PATH, work / "requirements" / "plan26.in")
        shutil.copy2(LOCK_PATH, work / "requirements" / "plan26.lock")
        return work

    def test_identical_lock_produces_an_empty_drift_report(self) -> None:
        work = self._staged_copy()
        result = subprocess.run(
            ["diff", "-u", str(LOCK_PATH), str(work / "requirements" / "plan26.lock")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_a_controlled_hash_change_produces_a_nonempty_drift_report(self) -> None:
        work = self._staged_copy()
        target = work / "requirements" / "plan26.lock"
        original = target.read_text(encoding="utf-8")
        mutated = original.replace("--hash=sha256:", "--hash=sha256:0", 1)
        self.assertNotEqual(original, mutated, "lock contained no sha256 hash to mutate")
        target.write_text(mutated, encoding="utf-8")

        result = subprocess.run(
            ["diff", "-u", str(LOCK_PATH), str(target)], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 1)
        self.assertNotEqual(result.stdout, "")

    def test_a_controlled_pin_change_produces_a_nonempty_drift_report(self) -> None:
        work = self._staged_copy()
        target = work / "requirements" / "plan26.lock"
        mutated = target.read_text(encoding="utf-8").replace("langgraph==1.2.9", "langgraph==1.2.8")
        target.write_text(mutated, encoding="utf-8")

        result = subprocess.run(
            ["diff", "-u", str(LOCK_PATH), str(target)], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("langgraph==1.2.8", result.stdout)

    @unittest.skipUnless(
        _generator_available(),
        f"pinned generator absent (needs pip=={PIP_VERSION_FOR_GENERATION}, "
        f"pip-tools=={PIP_TOOLS_VERSION}); CI installs both",
    )
    def test_regeneration_is_byte_identical_to_the_committed_lock(self) -> None:
        work = self._staged_copy()
        result = subprocess.run(
            REGENERATE_COMMAND.replace("python ", f"{sys.executable} ", 1).split(),
            cwd=work,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (work / "requirements" / "plan26.lock").read_bytes(),
            LOCK_PATH.read_bytes(),
            "regenerated lock drifted from the committed lock",
        )


class TestCiOwnership(unittest.TestCase):
    """Deleting the CI step, or these tests from it, must fail here."""

    def setUp(self) -> None:
        self.assertTrue(WORKFLOW_PATH.is_file(), f"missing CI workflow at {WORKFLOW_PATH}")
        self.text = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_workflow_is_valid_yaml_and_triggers_on_push_and_pull_request(self) -> None:
        import yaml

        doc = yaml.safe_load(self.text)
        triggers = doc.get(True, doc.get("on"))  # PyYAML parses bare `on:` as True
        self.assertIsInstance(triggers, dict)
        self.assertIn("push", triggers)
        self.assertIn("pull_request", triggers)

    def test_workflow_invokes_the_exact_regeneration_command(self) -> None:
        self.assertIn(REGENERATE_COMMAND, self.text)

    def test_workflow_fails_the_build_on_drift(self) -> None:
        self.assertIn(DRIFT_COMPARE_COMMAND, self.text)

    def test_workflow_pins_the_lock_generator(self) -> None:
        self.assertIn(f'"pip-tools=={PIP_TOOLS_VERSION}"', self.text)
        self.assertIn(f'"pip=={PIP_VERSION_FOR_GENERATION}"', self.text)

    def test_workflow_installs_with_require_hashes(self) -> None:
        self.assertIn(
            "python -m pip install --require-hashes -r requirements/plan26.lock", self.text
        )

    def test_workflow_runs_both_plan26_dependency_tests(self) -> None:
        self.assertIn("tests/runtime/test_plan26_api_contract.py", self.text)
        self.assertIn("tests/runtime/test_plan26_lock_drift.py", self.text)

    def test_workflow_uses_python_3_13(self) -> None:
        self.assertIn('python-version: "3.13"', self.text)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
