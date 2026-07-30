"""Negative fixture for FR-P0-REGISTRY (a).

A registry that has lost a gate the plan's section 8 declares. Derived from the real
registry so the fixture cannot go stale as gates are added, then one id is dropped:
the comparison must report `gate-declared-in-plan-not-registered`, which is the
defect that made a later gate impossible to report as skipped.

Never loaded by the runner. Only FR-P0-REGISTRY's fixture invocation reads it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests" / "gates"))

from registry import GATES as _REAL_GATES  # noqa: E402

DROPPED = "FR-P0-CLEAN"

GATES = [gate for gate in _REAL_GATES if gate["id"] != DROPPED]
