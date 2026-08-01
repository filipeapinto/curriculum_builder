"""Negative fixture for FR-P0-REGISTRY — a gate registered under a family no plan owns.

Once the registry composes from several plans, "this gate is not in the plan" stops
being one question and becomes two: the gate may belong to a family and be missing
from that family's catalogue, or it may belong to **no declared family at all**. The
second is the one that quietly reintroduces the defect the family manifest exists to
remove — an id nobody's plan declares, checked against nobody's section, passing
because no catalogue was ever asked about it.

Derived from the real registry so the fixture cannot go stale as gates are added,
then one gate is appended under a prefix `tests/gates/gate_families.v1.yaml` gives to
no family: the comparison must report `gate-family-unowned`. Reporting anything else —
including `gate-registered-not-in-plan`, which would mean the id had been filed under
some family regardless — is a wrong-reason failure, not a pass.

Never loaded by the runner. Only FR-P0-REGISTRY's fixture invocation reads it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests" / "gates"))

from registry import GATES as _REAL_GATES  # noqa: E402

UNOWNED = {
    "id": "FR-P9-ORPHAN",
    "activation_phase": 9,
    "claim_class": "text",
    "depends_on": ["FR-P0-HARNESS"],
    "command": "python3 tests/gates/fr_p9_orphan.py --check orphan",
    "impl": "fr_p9_orphan:check_orphan",
}

GATES = list(_REAL_GATES) + [UNOWNED]
