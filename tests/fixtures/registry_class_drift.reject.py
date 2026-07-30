"""Negative fixture for FR-P0-REGISTRY (d).

A gate declaring `schema` whose implementation reported `schema+text`. The declared
class and the reported mechanisms are compared **as sets**, so this must be reported
`claim-class-drift` — understating what a gate did is as much a defect as
overstating it, because the result record is the only account of what was proven.

Never loaded by the runner. Only FR-P0-REGISTRY's fixture invocation reads it.
"""

GATES = [
    {
        "id": "FR-P0-SCHEMA",
        "activation_phase": 0,
        "claim_class": "schema",
        "depends_on": ["FR-P0-PARSE", "FR-P0-DEPS"],
        "command": "python3 tests/gates/fr_p0_structure.py --check schema",
        "impl": "fr_p0_structure:check_schema",
    }
]

# What the implementation reported it actually used: it also grepped.
REPORTED_MECHANISMS = {"FR-P0-SCHEMA": ["schema", "text"]}
