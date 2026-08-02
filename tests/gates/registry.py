"""The single gate registry — every gate its owning plan's catalogue declares, once.

The registry composes from **several** plans. ``tests/gates/gate_families.v1.yaml``
maps each gate-id prefix to the plan that owns that family and to the section of that
plan holding its catalogue, and ``FR-P0-REGISTRY`` compares each family against its
own plan's section rather than comparing everything against one. A gate whose prefix
no family claims is ``gate-family-unowned`` and fails.

Harness rule 2: this file lists **every** gate with its ``activation_phase``, its
claim class and its ``depends_on`` list from the first commit onward, so a later
gate can be reported ``SKIPPED (activates at phase M)`` rather than being invisible.
A gate is declared here before it is implemented.

``FR-P0-HARNESS`` is the root of the dependency graph: every other gate depends on
it directly or transitively.

``FR-ALL`` is deliberately absent. It is the regression *run*, not a gate.

Fields
------
id                 stable gate id, ``FR-P<phase>-<NAME>``
activation_phase   the phase from which the gate runs; earlier phases skip it
claim_class        an ordered set of mechanisms, joined by ``+`` (harness rule 6)
depends_on         gate ids that must pass before this gate may run
command            the exact command section 8 states for the gate
impl               ``module:function`` inside ``tests/gates/``; ``None`` while the
                   gate is declared but not yet implemented
"""

GATES = [
    # --- Phase 0 — harness, registry, structure, existing validation -------------
    {
        "id": "FR-P0-HARNESS",
        "activation_phase": 0,
        "claim_class": "execution+mapping",
        "depends_on": [],
        "command": "python3 tests/gates/selftest.py",
        "impl": "selftest:gate_harness",
    },
    {
        "id": "FR-P0-REGISTRY",
        "activation_phase": 0,
        "claim_class": "text+mapping",
        "depends_on": ["FR-P0-PLANREF"],
        "command": "python3 tests/gates/fr_p0_structure.py --check registry",
        "impl": "fr_p0_structure:check_registry",
    },
    {
        "id": "FR-P0-DEPS",
        "activation_phase": 0,
        "claim_class": "execution",
        "depends_on": ["FR-P0-HARNESS"],
        "command": "python3 -c \"import jsonschema, yaml; print('DEPS OK')\"",
        "impl": "fr_p0_structure:check_deps",
    },
    {
        "id": "FR-P0-TREE",
        "activation_phase": 0,
        "claim_class": "tree+text+mapping",
        "depends_on": ["FR-P0-PLANREF"],
        "command": "python3 tests/gates/fr_p0_structure.py --check tree",
        "impl": "fr_p0_structure:check_tree",
    },
    {
        "id": "FR-P0-NOSTALE",
        "activation_phase": 0,
        "claim_class": "text+execution",
        "depends_on": ["FR-P0-TREE"],
        "command": "python3 tests/gates/fr_p0_structure.py --check stale",
        "impl": "fr_p0_structure:check_stale",
    },
    {
        "id": "FR-P0-PLANREF",
        "activation_phase": 0,
        "claim_class": "tree+text+mapping",
        "depends_on": ["FR-P0-HARNESS"],
        "command": "python3 tests/gates/fr_p0_structure.py --check planref",
        "impl": "fr_p0_structure:check_planref",
    },
    {
        "id": "FR-P0-PARSE",
        "activation_phase": 0,
        "claim_class": "parse",
        "depends_on": ["FR-P0-TREE"],
        "command": "python3 tests/gates/fr_p0_structure.py --check parse",
        "impl": "fr_p0_structure:check_parse",
    },
    {
        "id": "FR-P0-SCHEMA",
        "activation_phase": 0,
        "claim_class": "schema",
        "depends_on": ["FR-P0-PARSE", "FR-P0-DEPS"],
        "command": "python3 tests/gates/fr_p0_structure.py --check schema",
        "impl": "fr_p0_structure:check_schema",
    },
    {
        "id": "FR-P0-HISTORY",
        "activation_phase": 0,
        "claim_class": "text+mapping+execution",
        "depends_on": ["FR-P0-TREE"],
        "command": "python3 tests/gates/fr_p0_structure.py --check history",
        "impl": "fr_p0_structure:check_history",
    },
    {
        "id": "FR-P0-CLEAN",
        "activation_phase": 0,
        "claim_class": "execution",
        "depends_on": ["FR-P0-HARNESS"],
        "command": "git status --porcelain",
        "impl": "fr_p0_structure:check_clean",
    },

    # --- Phase 1 — retention -----------------------------------------------------
    {
        "id": "FR-P1-GITKEEP",
        "activation_phase": 1,
        "claim_class": "tree+execution",
        "depends_on": ["FR-P0-TREE"],
        "command": "python3 tests/gates/fr_p1_retention.py --check gitkeep",
        "impl": "fr_p1_retention:check_gitkeep",
    },
    {
        "id": "FR-P1-SCHEMA-RETENTION",
        "activation_phase": 1,
        "claim_class": "tree+text",
        "depends_on": ["FR-P1-GITKEEP"],
        "command": "python3 tests/gates/fr_p1_retention.py --check schema-gate",
        "impl": "fr_p1_retention:check_schema_gate",
    },

    # --- Phase 2 — routing, selector, and the three contracts it needs -----------
    {
        "id": "FR-P2-CONTRACT-VERSIONED",
        "activation_phase": 2,
        "claim_class": "tree+text+schema+parse",
        "depends_on": ["FR-P0-SCHEMA"],
        "command": "python3 tests/gates/fr_p2_selector.py --check contract-versioned",
        "impl": "fr_p2_selector:check_contract_versioned",
    },
    {
        "id": "FR-P2-DEFERRED",
        "activation_phase": 2,
        "claim_class": "parse+text+mapping",
        "depends_on": ["FR-P0-PARSE"],
        "command": "python3 tests/gates/fr_p2_selector.py --check deferred",
        "impl": "fr_p2_selector:check_deferred",
    },
    {
        "id": "FR-P2-BOUND",
        "activation_phase": 2,
        "claim_class": "text+mapping",
        "depends_on": ["FR-P2-CONTRACT-VERSIONED", "FR-P2-DEFERRED"],
        "command": "python3 tests/gates/fr_p2_selector.py --check bound",
        "impl": "fr_p2_selector:check_bound",
    },
    {
        "id": "FR-P2-NOVALUES",
        "activation_phase": 2,
        "claim_class": "text+mapping",
        "depends_on": ["FR-P0-HARNESS"],
        "command": "python3 tests/gates/fr_p2_selector.py --check no-values",
        "impl": "fr_p2_selector:check_no_values",
    },
    {
        "id": "FR-P2-SEL-MAPPED",
        "activation_phase": 2,
        "claim_class": "tree+text+mapping",
        "depends_on": ["FR-P2-DEFERRED"],
        "command": "python3 tests/gates/fr_p2_selector.py --check sel-mapped",
        "impl": "fr_p2_selector:check_sel_mapped",
    },
    {
        "id": "FR-P2-DECISION-VALID",
        "activation_phase": 2,
        "claim_class": "schema+mapping",
        "depends_on": ["FR-P2-CONTRACT-VERSIONED"],
        "command": "python3 tests/gates/fr_p2_selector.py --check decision",
        "impl": "fr_p2_selector:check_decision",
    },
    {
        "id": "FR-P2-BYPASS-DECLARED",
        "activation_phase": 2,
        "claim_class": "declaration",
        "depends_on": ["FR-P2-CONTRACT-VERSIONED"],
        "command": "python3 tests/gates/fr_p2_selector.py --check bypass-declared",
        "impl": "fr_p2_selector:check_bypass_declared",
    },
    {
        "id": "FR-P2-UNRECORDED-DECLARED",
        "activation_phase": 2,
        "claim_class": "mapping+declaration",
        "depends_on": ["FR-P2-CONTRACT-VERSIONED"],
        "command": "python3 tests/gates/fr_p2_selector.py --check unrecorded-declared",
        "impl": "fr_p2_selector:check_unrecorded_declared",
    },
    {
        "id": "FR-P2-GATEITEMS",
        "activation_phase": 2,
        "claim_class": "text+mapping",
        "depends_on": ["FR-P0-HARNESS"],
        "command": "python3 tests/gates/fr_p2_selector.py --check gate-items",
        "impl": "fr_p2_selector:check_gate_items",
    },

    # --- Phase 3 — calibration boundaries ---------------------------------------
    {
        "id": "FR-P3-SPLIT",
        "activation_phase": 3,
        "claim_class": "parse+text+mapping+schema",
        "depends_on": ["FR-P0-SCHEMA"],
        "command": "python3 tests/gates/fr_p3_calibration.py --check split",
        "impl": "fr_p3_calibration:check_split",
    },
    {
        "id": "FR-P3-NO-LITERALS",
        "activation_phase": 3,
        "claim_class": "text+mapping",
        "depends_on": ["FR-P3-SPLIT"],
        "command": "python3 tests/gates/fr_p3_calibration.py --check literals",
        "impl": "fr_p3_calibration:check_literals",
    },
    {
        "id": "FR-P3-CAPS-OWNED",
        "activation_phase": 3,
        "claim_class": "parse+text+mapping",
        "depends_on": ["FR-P3-SPLIT"],
        "command": "python3 tests/gates/fr_p3_calibration.py --check caps",
        "impl": "fr_p3_calibration:check_caps",
    },
    {
        "id": "FR-P3-CAL-AGREE",
        "activation_phase": 3,
        "claim_class": "parse+mapping",
        "depends_on": ["FR-P3-SPLIT"],
        "command": "python3 tests/gates/fr_p3_calibration.py --check cal-agree",
        "impl": "fr_p3_calibration:check_cal_agree",
    },
    {
        "id": "FR-P3-KIT-SOURCE",
        "activation_phase": 3,
        "claim_class": "parse+text+mapping",
        "depends_on": ["FR-P3-SPLIT"],
        "command": "python3 tests/gates/fr_p3_calibration.py --check kit-source",
        "impl": "fr_p3_calibration:check_kit_source",
    },

    # --- Phase 4 — policy schemas and mapping ------------------------------------
    {
        "id": "FR-P4-ALL-VALIDATE",
        "activation_phase": 4,
        "claim_class": "schema+mapping",
        "depends_on": ["FR-P0-SCHEMA"],
        "command": "python3 tests/gates/fr_p4_policy_schemas.py --check validate",
        "impl": "fr_p4_policy_schemas:check_validate",
    },
    {
        "id": "FR-P4-AGREEMENT",
        "activation_phase": 4,
        "claim_class": "parse+mapping",
        "depends_on": ["FR-P4-CHECK-MAPPING"],
        "command": "python3 tests/gates/fr_p4_policy_schemas.py --check agreement",
        "impl": "fr_p4_policy_schemas:check_agreement",
    },
    {
        "id": "FR-P4-FIXTURE-BITES",
        "activation_phase": 4,
        "claim_class": "schema",
        "depends_on": ["FR-P0-SCHEMA"],
        "command": "python3 tests/gates/fr_p4_policy_schemas.py --check fixture-bites",
        "impl": "fr_p4_policy_schemas:check_fixture_bites",
    },
    {
        "id": "FR-P4-CHECK-MAPPING",
        "activation_phase": 4,
        "claim_class": "tree+text+mapping",
        "depends_on": ["FR-P2-DEFERRED"],
        "command": "python3 tests/gates/fr_p4_policy_schemas.py --check mapping",
        "impl": "fr_p4_policy_schemas:check_mapping",
    },

    # --- Phase 5 — the engine/domain boundary -----------------------------------
    # A different family, owned by a different plan. See
    # tests/gates/gate_families.v1.yaml: the FR-P5- prefix belongs to
    # plans/simplification/plan/, whose section 9 is this gate's catalogue.
    {
        "id": "FR-P5-ENGINE-GENERIC",
        "activation_phase": 5,
        "claim_class": "tree+parse+text+mapping",
        "depends_on": ["FR-P0-HARNESS"],
        "command": "python3 tests/gates/fr_p5_engine.py --check engine-generic",
        "impl": "fr_p5_engine:check_engine_generic",
    },

    # --- Phase 5 — the four generic checks a unit owes (plan phase 4) ------------
    {
        "id": "FR-P5-READABILITY",
        "activation_phase": 5,
        "claim_class": "tree+mapping",
        "depends_on": ["FR-P0-SCHEMA"],
        "command": "python3 tests/gates/fr_p5_unit.py --check readability",
        "impl": "fr_p5_unit:check_readability",
    },
    {
        "id": "FR-P5-BLOOM-VERBS",
        "activation_phase": 5,
        "claim_class": "tree+mapping",
        "depends_on": ["FR-P0-SCHEMA"],
        "command": "python3 tests/gates/fr_p5_unit.py --check bloom-verbs",
        "impl": "fr_p5_unit:check_bloom_verbs",
    },
    {
        "id": "FR-P5-DERIVATION",
        "activation_phase": 5,
        "claim_class": "tree+mapping",
        "depends_on": ["FR-P0-HARNESS"],
        "command": "python3 tests/gates/fr_p5_unit.py --check derivation",
        "impl": "fr_p5_unit:check_derivation",
    },
    {
        "id": "FR-P5-RECEIPT-HASH",
        "activation_phase": 5,
        "claim_class": "tree+mapping",
        "depends_on": ["FR-P0-HARNESS"],
        "command": "python3 tests/gates/fr_p5_unit.py --check receipt-hash",
        "impl": "fr_p5_unit:check_receipt_hash",
    },

    # --- Phase 5 — the unit contract (plan phase 1) ------------------------------
    {
        "id": "FR-P5-UNIT-CONTRACT",
        "activation_phase": 5,
        "claim_class": "parse+mapping",
        "depends_on": ["FR-P0-PARSE"],
        "command": "python3 tests/gates/fr_p5_unit.py --check unit-contract",
        "impl": "fr_p5_unit:check_unit_contract",
    },

    # --- Phase 5 — the verifier precondition (plan phase 2) ----------------------
    {
        "id": "FR-P5-VERIFIER-REQUIRED",
        "activation_phase": 5,
        "claim_class": "tree+parse+mapping+execution",
        "depends_on": ["FR-P0-SCHEMA"],
        "command": "python3 tests/gates/fr_p5_verifier.py --check verifier-required",
        "impl": "fr_p5_verifier:check_verifier_required",
    },

    # --- Phase 5 — the constraints G5 moved out of the engine --------------------
    {
        "id": "FR-P5-DOMAIN-CONSTRAINED",
        "activation_phase": 5,
        "claim_class": "tree+parse+mapping+schema",
        "depends_on": ["FR-P0-SCHEMA"],
        "command": "python3 tests/gates/fr_p5_manifest.py --check domain-constrained",
        "impl": "fr_p5_manifest:check_domain_constrained",
    },
]

GATES_BY_ID = {gate["id"]: gate for gate in GATES}
