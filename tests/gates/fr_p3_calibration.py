"""Phase-3 gates — calibration boundaries.

The engine-wide premise and one kit's supplies were the same file. A second
curriculum would have inherited ELEGOO's battery in silence. These gates prove the
split held, that the caps have exactly one owner each, and that no contract
hard-codes a fact about the learner or the kit.

**No production scan here matches a bare value.** Every term — a cap, a learner age,
a kit name — is matched by the anchored ``prose_pattern`` declared in the manifest
that owns it. A cap whose value is ``1``, ``2``, ``required`` or ``understand``
scanned literally would flag every ordinal, list index and ordinary sentence in the
repository. A term with no pattern is a **failure**, never a skip.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
from common import Evidence, Fixture, REPO_ROOT, gate_result, read_named, rel  # noqa: E402

FIXTURES = common.FIXTURES_DIR

CALIBRATION = REPO_ROOT / "policy" / "calibration.v1.yaml"
KIT_CALIBRATION = REPO_ROOT / "curricula" / "arduino_kit" / "kit_calibration.v1.yaml"
CALIBRATION_SCHEMA = REPO_ROOT / "schemas" / "calibration.schema.v1.json"
KIT_SCHEMA = REPO_ROOT / "schemas" / "kit_calibration.schema.v1.json"
CURRICULUM = REPO_ROOT / "curricula" / "arduino_kit" / "arduino_kit_curriculum.v4.yaml"

SCHEMAS_DIR = REPO_ROOT / "schemas"

# The kit's own contract is the one schema allowed to name the kit — it is what the
# kit's facts are *for*. Every other schema naming it is defect F03.
NO_LITERALS_EXEMPT = {"kit_calibration.schema.v1.json"}

# Where a cap could be copied into prose. The cap entries themselves are excluded
# below: pedagogy_caps is where the cap is owned, so a gate that flagged it would
# forbid the manifest from stating the fact it exists to state.
CAP_SCAN_ROOTS = ("meta_prompt", "docs", "policy")


def _terms(doc, key) -> dict[str, dict]:
    return (doc or {}).get(key) or {}


def _missing_patterns(terms: dict[str, dict], label: str) -> list[str]:
    return [
        f"term-without-prose-pattern:{label}.{name}"
        for name, spec in terms.items()
        if not (spec or {}).get("prose_pattern")
    ]


# ---------------------------------------------------------------------------
# FR-P3-SPLIT


def split_violations(global_doc, global_text: str, kit_terms: dict[str, dict]) -> list[str]:
    """No `power` block and no kit term in the engine-wide calibration."""
    problems = []
    if "power" in (global_doc or {}):
        problems.append("kit-fact-in-global-calibration: a `power` block survived the split")
    problems += _missing_patterns(kit_terms, "kit_terms")
    for name, spec in kit_terms.items():
        pattern = (spec or {}).get("prose_pattern")
        if pattern and re.search(pattern, global_text):
            problems.append(f"kit-fact-in-global-calibration: the kit term {name!r} appears in it")
    return problems


def check_split(ev: Evidence):
    global_doc = ev.parse(CALIBRATION)
    kit_doc = ev.parse(KIT_CALIBRATION)
    kit_terms = _terms(kit_doc, "kit_terms")
    ev.resolve("every kit term", rel(KIT_CALIBRATION), rel(CALIBRATION) + "'s prose")
    problems = split_violations(global_doc, ev.text_of(CALIBRATION), kit_terms)

    # The kit side must actually hold what the engine side gave up.
    power = (kit_doc or {}).get("power") or {}
    if not power.get("permitted_inputs"):
        problems.append("kit-calibration-incomplete: no permitted_inputs")
    if not power.get("rails"):
        problems.append("kit-calibration-incomplete: no rails")
    if not re.search(r"\b3\s*[-–]\s*5\s*V\b", str(power.get("student_circuit_range", ""))):
        problems.append(
            f"kit-calibration-incomplete: student_circuit_range is "
            f"{power.get('student_circuit_range')!r}, not the 3-5 V range"
        )

    for instance, schema in ((CALIBRATION, CALIBRATION_SCHEMA), (KIT_CALIBRATION, KIT_SCHEMA)):
        error = ev.validate(instance, schema)
        if error:
            problems.append(f"{rel(instance)}: {error}")

    line = (
        f"FR-P3-SPLIT {'PASS' if not problems else 'FAIL'} "
        f"({len(kit_terms)} kit terms, 0 in the engine-wide calibration, "
        f"{len(power.get('permitted_inputs') or [])} permitted inputs)"
    )
    reject = FIXTURES / "global_calibration_with_kit_power.reject.yaml"
    accept = FIXTURES / "global_calibration_incidental_term.accept.yaml"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="kit-fact-in-global-calibration",
            detector=lambda: (
                split_violations(common._deserialize(reject), read_named(reject), kit_terms) or [None]
            )[0],
        ),
        Fixture(
            name=rel(accept),
            kind="accept",
            detector=lambda: (
                split_violations(common._deserialize(accept), read_named(accept), kit_terms) or [None]
            )[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P3-NO-LITERALS


def literal_violations(paths, terms: dict[str, dict], label: str) -> list[str]:
    problems = _missing_patterns(terms, label)
    for path in paths:
        try:
            text = read_named(path)
        except (OSError, UnicodeDecodeError):
            continue
        for name, spec in terms.items():
            pattern = (spec or {}).get("prose_pattern")
            if not pattern:
                continue
            match = re.search(pattern, text)
            if match:
                line = text[: match.start()].count("\n") + 1
                problems.append(f"data-fact-in-contract:{name} at {rel(path)}:{line}")
    return problems


def check_literals(ev: Evidence):
    terms = {
        **_terms(ev.read_for_resolution(CALIBRATION), "learner_terms"),
        **_terms(ev.read_for_resolution(KIT_CALIBRATION), "kit_terms"),
    }
    ev.resolve(
        "every learner and kit term",
        f"{rel(CALIBRATION)} and {rel(KIT_CALIBRATION)}",
        "the contracts under schemas/",
    )
    targets = ev.select(
        p for p in SCHEMAS_DIR.rglob("*.json") if p.name not in NO_LITERALS_EXEMPT
    )
    problems = []
    for path in targets:
        text = ev.text_of(path)
        for name, spec in terms.items():
            pattern = (spec or {}).get("prose_pattern")
            if not pattern:
                continue
            found = ev.search(pattern, text)
            if found:
                problems.append(f"data-fact-in-contract:{name} at {rel(path)}")
    problems += _missing_patterns(terms, "terms")

    line = (
        f"FR-P3-NO-LITERALS {'PASS' if not problems else 'FAIL'} "
        f"({len(targets)} contracts scanned, {len(terms)} terms, 0 hits; "
        f"{sorted(NO_LITERALS_EXEMPT)[0]} exempt as the kit's own contract)"
    )
    reject = FIXTURES / "schema_with_learner_literal.reject.json"
    accept = FIXTURES / "schema_incidental_digit.accept.json"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="data-fact-in-contract",
            detector=lambda: (literal_violations([reject], terms, "terms") or [None])[0],
        ),
        Fixture(
            name=rel(accept),
            kind="accept",
            detector=lambda: (literal_violations([accept], terms, "terms") or [None])[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P3-CAPS-OWNED and FR-P3-CAL-AGREE


def _follow(pointer: str):
    """Resolve an ``enforced_by`` of the form '<file> → <dotted path>' to the exact
    constraint it names.

    The walk is strict: each segment is looked up as a schema keyword, a
    ``properties`` member or a ``$defs`` member, in that order, and nothing else.
    A fuzzy search would let a wrong pointer resolve to a coincidentally-named
    constraint somewhere else in the file, which is precisely the drift this gate
    exists to catch.
    """
    if "→" not in pointer:
        return None, f"enforced_by is not of the form '<file> → <path>': {pointer!r}"
    file_part, path_part = (p.strip() for p in pointer.split("→", 1))
    path = REPO_ROOT / file_part
    if not path.exists():
        return None, f"enforced_by names {file_part}, which does not exist"
    node = common._deserialize(path)
    walked = []
    for key in path_part.split("."):
        nxt = _step(node, key)
        if nxt is None:
            return None, (
                f"enforced_by path {path_part!r} does not resolve at {key!r} "
                f"(reached {'.'.join(walked) or '<root>'})"
            )
        node, _ = nxt
        walked.append(key)
    return node, None


def _step(node, key):
    """One segment of a dotted pointer: a `properties` member, a `$defs` member, or
    a schema keyword such as `maxItems`, `items`, `contains`, `enum`, `required`."""
    if not isinstance(node, dict):
        return None
    for container in ("properties", "$defs"):
        child = node.get(container)
        if isinstance(child, dict) and key in child:
            return child[key], container
    if key in node:
        return node[key], "keyword"
    return None


def _constraint_agrees(name: str, value, constraint) -> bool:
    """Does the declared cap value equal the schema constraint that carries it?

    Five shapes, one per cap family, and no fallback: an unrecognised shape is a
    disagreement, never an assumed agreement.
    """
    if constraint is None:
        return False

    # A range cap, carried by an array subschema's bounds.
    if isinstance(value, list) and len(value) == 2 and isinstance(constraint, dict):
        return [
            constraint.get("minItems", constraint.get("minimum")),
            constraint.get("maxItems", constraint.get("maximum")),
        ] == list(value)

    # A floor, carried by an enum whose first member is the lowest level permitted.
    if isinstance(constraint, list) and constraint and isinstance(constraint[0], str):
        # `required: [...]` carries a presence cap; an enum carries a floor.
        if value == "required":
            return name in constraint
        return constraint[0] == value

    # A voice, carried by a pattern the criterion must match.
    if isinstance(constraint, str) and value == "first_person":
        return bool(re.match(r"\^\s*I can", constraint))

    # A scalar cap, carried directly by maxItems / minItems / const.
    if isinstance(constraint, dict):
        for key in ("maxItems", "minItems", "const", "maximum", "minimum"):
            if key in constraint and constraint[key] == value:
                return True
        return False

    return constraint == value


def cap_agreement_violations(caps: dict) -> list[str]:
    problems = []
    for name, cap in (caps or {}).items():
        if not isinstance(cap, dict):
            problems.append(f"cap-schema-disagreement:{name} is a bare value, not an owned cap")
            continue
        if "value" not in cap:
            problems.append(f"cap-schema-disagreement:{name} declares no value")
            continue
        pointer = cap.get("enforced_by")
        if not pointer:
            problems.append(f"cap-schema-disagreement:{name} names no enforced_by constraint")
            continue
        constraint, error = _follow(pointer)
        if error:
            problems.append(f"cap-schema-disagreement:{name} — {error}")
            continue
        if not _constraint_agrees(name, cap["value"], constraint):
            problems.append(
                f"cap-schema-disagreement:{name} — calibration says {cap['value']!r}, "
                f"{pointer} carries {constraint!r}"
            )
    return problems


def check_cal_agree(ev: Evidence):
    caps = (ev.parse(CALIBRATION) or {}).get("pedagogy_caps") or {}
    for name, cap in caps.items():
        if isinstance(cap, dict) and cap.get("enforced_by"):
            ev.resolve(f"pedagogy_caps.{name}.value", rel(CALIBRATION), cap["enforced_by"])
    problems = cap_agreement_violations(caps)
    line = (
        f"FR-P3-CAL-AGREE {'PASS' if not problems else 'FAIL'} "
        f"({len(caps)} caps, {len(caps) - len(problems)} agreeing with their schema constraint)"
    )
    reject = FIXTURES / "cap_schema_mismatch.reject.yaml"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="cap-schema-disagreement",
            detector=lambda: (
                cap_agreement_violations(
                    (common._deserialize(reject) or {}).get("pedagogy_caps") or {}
                ) or [None]
            )[0],
        )
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


def cap_copy_violations(paths, caps: dict) -> list[str]:
    """(c) A cap stated anywhere but where it is owned has two owners."""
    problems = []
    for path in paths:
        try:
            text = read_named(path)
        except (OSError, UnicodeDecodeError):
            continue
        for name, cap in (caps or {}).items():
            pattern = (cap or {}).get("prose_pattern") if isinstance(cap, dict) else None
            if not pattern:
                continue
            match = re.search(pattern, text)
            if match:
                line = text[: match.start()].count("\n") + 1
                problems.append(f"unowned-cap-copy:{name} at {rel(path)}:{line}")
    return problems


def check_caps(ev: Evidence):
    caps = (ev.parse(CALIBRATION) or {}).get("pedagogy_caps") or {}
    problems = []
    for name, cap in caps.items():
        if not isinstance(cap, dict):
            problems.append(f"cap-without-prose-pattern:{name} is a bare value")
            continue
        for field in ("value", "enforced_by", "prose_pattern"):
            if field not in cap:
                problems.append(
                    f"cap-without-prose-pattern:{name} declares no {field}"
                    if field == "prose_pattern"
                    else f"cap-incomplete:{name} declares no {field}"
                )
    problems += cap_agreement_violations(caps)
    for name, cap in caps.items():
        if isinstance(cap, dict) and cap.get("enforced_by"):
            ev.resolve(f"pedagogy_caps.{name}.value", rel(CALIBRATION), cap["enforced_by"])

    # The cap entries are where the cap is owned, so calibration itself is excluded.
    targets = ev.select(
        p
        for root in CAP_SCAN_ROOTS
        for p in (REPO_ROOT / root).rglob("*")
        if p.is_file()
        and p.suffix.lower() not in common.BINARY_SUFFIXES
        and p != CALIBRATION
    )
    for path in targets:
        text = ev.text_of(path)
        for name, cap in caps.items():
            pattern = (cap or {}).get("prose_pattern") if isinstance(cap, dict) else None
            if pattern and ev.search(pattern, text):
                problems.append(f"unowned-cap-copy:{name} at {rel(path)}")

    line = (
        f"FR-P3-CAPS-OWNED {'PASS' if not problems else 'FAIL'} "
        f"({len(caps)} caps, {len(caps)} patterns, {len(targets)} files scanned, 0 unowned copies)"
    )
    reject = FIXTURES / "prose_with_cap_value.reject.md"
    accept = FIXTURES / "prose_incidental_number.accept.md"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="unowned-cap-copy",
            detector=lambda: (cap_copy_violations([reject], caps) or [None])[0],
        ),
        Fixture(
            name=rel(accept),
            kind="accept",
            detector=lambda: (cap_copy_violations([accept], caps) or [None])[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P3-KIT-SOURCE


def kit_source_violations(curriculum, kit_doc) -> list[str]:
    """Every powered lab cites exactly one verified input, by id."""
    inputs = {
        entry["id"]: entry
        for entry in ((kit_doc or {}).get("power") or {}).get("permitted_inputs", [])
        if isinstance(entry, dict) and "id" in entry
    }
    problems = []
    for lab in (curriculum or {}).get("labs", []):
        activity = lab.get("core_activity") or {}
        if activity.get("mode") == "unpowered":
            if "power_input" in activity:
                problems.append(
                    f"unverified-source-cited:{lab.get('id')} is unpowered but cites a supply"
                )
            continue
        cited = activity.get("power_input")
        if not cited:
            problems.append(f"unverified-source-cited:{lab.get('id')} cites no input id")
            continue
        if isinstance(cited, list):
            problems.append(f"unverified-source-cited:{lab.get('id')} cites {len(cited)} inputs, not one")
            continue
        entry = inputs.get(cited)
        if entry is None:
            problems.append(f"unverified-source-cited:{lab.get('id')} cites {cited!r}, not a permitted input")
            continue
        if entry.get("verification") != "verified_official":
            problems.append(
                f"unverified-source-cited:{lab.get('id')} cites {cited!r}, whose verification is "
                f"{entry.get('verification')!r}"
            )
    return problems


def check_kit_source(ev: Evidence):
    curriculum = ev.parse(CURRICULUM)
    kit_doc = ev.parse(KIT_CALIBRATION)
    ev.text_of(KIT_CALIBRATION)
    problems = []

    checks = ev.read_for_resolution(REPO_ROOT / "policy" / "checks.v1.yaml")
    ids = {
        entry["id"]
        for value in (checks or {}).values()
        if isinstance(value, list)
        for entry in value
        if isinstance(entry, dict) and "id" in entry
    }
    if "CAL-SOURCE-VERIFIED" not in ids:
        problems.append("CAL-SOURCE-VERIFIED is not a check id in policy/checks.v1.yaml")

    powered = [
        lab for lab in (curriculum or {}).get("labs", [])
        if (lab.get("core_activity") or {}).get("mode") != "unpowered"
    ]
    for lab in powered:
        ev.resolve(
            f"{lab.get('id')}.core_activity.power_input",
            rel(CURRICULUM),
            rel(KIT_CALIBRATION) + " power.permitted_inputs",
        )
    problems += kit_source_violations(curriculum, kit_doc)

    line = (
        f"FR-P3-KIT-SOURCE {'PASS' if not problems else 'FAIL'} "
        f"({len(powered)} powered labs, each citing one verified_official input)"
    )
    reject = FIXTURES / "lab_cites_unverified_input.reject.yaml"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="unverified-source-cited",
            detector=lambda: (
                kit_source_violations(common._deserialize(reject), kit_doc) or [None]
            )[0],
        )
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------

CHECK_TABLE = {
    "split": check_split,
    "literals": check_literals,
    "caps": check_caps,
    "cal-agree": check_cal_agree,
    "kit-source": check_kit_source,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", required=True, choices=sorted(CHECK_TABLE))
    args = parser.parse_args()
    ev = Evidence(gate_id=args.check)
    outcome = CHECK_TABLE[args.check](ev)
    print(outcome.detail)
    for record in outcome.fixtures:
        print(f"  fixture {record['fixture']}: {record['outcome']} ({record['matched_error']})")
    print(f"  mechanisms: {ev.claim() or '-'}")
    return 0 if outcome.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
