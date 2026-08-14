"""N60 adversarial regression, Run-27-harness level (as opposed to
`tests/runtime/test_plan27_adversarial.py`'s production-code level).

Most Run-27-harness adversarial properties -- descendant receipt reuse,
interrupted merge, resume drift at the attempt level, false result claims via
write-set/verification-failure admission gating, false completion via the
single-sink-final-audit rule, and nondeterministic evidence detection -- are
already proven, unmodified, by
`plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_controller.py`
(N10's own owned suite), re-run as part of this node's required full-tree
denominator. This file adds only the case that suite does not already name: a
spoofed Markdown status document's total lack of authority
(`rules.markdown_status_is_authority: false`), plus a static "incomplete
denominator" guard over both full test trees this campaign runs.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from unittest import mock

import pytest

_HERE = Path(__file__).resolve().parent
_CONTROLLER_DIR = _HERE.parent / "controller"
if str(_CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(_CONTROLLER_DIR))

import core as core_module  # noqa: E402
import scheduler as scheduler_module  # noqa: E402

REPO_ROOT = _HERE.parents[2]
GRAPH_V7_PATH = (
    _HERE.parent / "execution_package_v2" / "implementation.graph.v7.yaml"
)


# --------------------------------------------------------- Markdown status spoofing


def test_scheduler_status_has_no_authority_granted_to_any_markdown_file(tmp_path: Path):
    """Real Run 27 graph v7 (`rules.markdown_status_is_authority: false`), a
    fresh, empty state directory, and a spoofed status document dropped right
    next to it -- shaped exactly like a `plans.log.md` entry, claiming every
    node PASSED. `Scheduler.status()` must report every node's status as
    unadmitted (`None`, no receipt), and must never even open a `.md` file
    while computing that -- proving the property mechanically (by tracking
    every file actually read), not merely by the document's claim going
    unechoed.
    """
    graph = core_module.Graph.load(GRAPH_V7_PATH, REPO_ROOT)
    state_dir = tmp_path / "state"
    scheduler = scheduler_module.Scheduler(graph, state_dir, run_id="n60-markdown-spoof-test")

    spoof = tmp_path / "plans.log.md"
    spoof.write_text(
        "# Run 27 status\n\n"
        "All nodes N00 through N90: PASSED. ACTIVATED.\n",
        encoding="utf-8",
    )

    accessed: list[Path] = []
    original_read_text = Path.read_text

    def tracking_read_text(self: Path, *args: object, **kwargs: object) -> str:
        accessed.append(self)
        return original_read_text(self, *args, **kwargs)  # type: ignore[arg-type]

    with mock.patch.object(Path, "read_text", tracking_read_text):
        status = scheduler.status()

    assert all(node["status"] is None for node in status["nodes"]), (
        "a fresh state directory must report no admitted nodes, spoofed markdown "
        "notwithstanding"
    )
    markdown_reads = [path for path in accessed if path.suffix == ".md"]
    assert markdown_reads == [], f"status() read markdown file(s): {markdown_reads}"
    assert graph.rules.get("markdown_status_is_authority") is False


# ------------------------------------------------------------- incomplete denominators


_KNOWN_LEGITIMATE_SKIP_MARKERS = (
    # The hash-locked LangGraph environment probe: a real, environment-driven
    # skip (missing optional dependency group), not a hidden test weakening.
    "plan26 hash-locked environment not installed",
    # Host has no process sandbox available: transport fails closed instead of
    # running, a real environment gate, not a hidden weakening.
    "host provides no process sandbox",
    # A specific pinned CLI binary is not installed on this host: an
    # environment gate on the one thing being live-tested, not a weakening of
    # what the test proves when the binary is present.
    "is not installed on this host",
    # Host lacks the optional render/rasterize toolchain a specific capability
    # probe requires: an environment gate, not a hidden test weakening.
    "host lacks the pandoc/typst/poppler toolchain",
)


def _scan_for_unaccounted_skip_markers(root: Path) -> list[str]:
    """Every `pytest.mark.skip(if)`/`unittest.skip`/`xfail` decorator whose
    literal reason string is not one of the known, environment-driven,
    legitimate cases above. A new skip/xfail added anywhere in either tree
    without updating this list is exactly item 2's forbidden "skipped, xfailed,
    filtered, or weakened test used to obtain success" -- this makes that
    silent addition fail loudly instead.
    """
    offenders: list[str] = []
    for path in sorted(root.rglob("test_*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name not in {"skip", "skipif", "xfail"}:
                continue
            reason_text = ""
            for argument in list(node.args) + [keyword.value for keyword in node.keywords]:
                if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                    reason_text = argument.value
                    break
                if isinstance(argument, ast.JoinedStr):
                    # An f-string reason: concatenate its literal (non-interpolated)
                    # fragments so a known environment-driven message with a
                    # variable substring (e.g. an f"{cli} is not installed...")
                    # still matches on its fixed text.
                    reason_text = "".join(
                        part.value for part in argument.values
                        if isinstance(part, ast.Constant) and isinstance(part.value, str)
                    )
                    break
            if not any(marker in reason_text for marker in _KNOWN_LEGITIMATE_SKIP_MARKERS):
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}: {reason_text!r}")
    return offenders


def test_no_unaccounted_skip_or_xfail_marker_in_either_full_test_tree():
    offenders = _scan_for_unaccounted_skip_markers(
        REPO_ROOT / "tests" / "runtime"
    ) + _scan_for_unaccounted_skip_markers(_HERE)
    assert offenders == [], (
        "unaccounted skip/xfail marker(s) in this campaign's own test denominator "
        f"(update _KNOWN_LEGITIMATE_SKIP_MARKERS if genuinely environment-driven): "
        f"{offenders}"
    )
