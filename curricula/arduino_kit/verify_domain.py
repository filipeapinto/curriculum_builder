"""arduino_kit's domain verifier — electrical rule checking over a unit's domain block.

`plans/simplification/plan/simplification.plan.v3.md` §3 is why this file exists. The
closest published proxy to "design a working circuit from datasheets", verified by
simulation, has a top-model pass rate of **8.15%**. The useful reading is not that
electronics is too hard; it is that

    a domain is generatable exactly to the extent that it has a verifier which is
    not a model.

So the engine refuses to run a curriculum that declares no verifier, and this is
arduino_kit's. It is ordinary code over structured data — the thing CircuitLM reports
as *"what eliminated fatal errors"*. **No model is called from here, ever.** A model
checking a model's circuit is the one role the evidence specifically rules out.

Six curriculum-specific rules, each with its own code, each reported by name.
The engine validates the exact candidate and every fixture against the separately
frozen JSON Schema before this script is entered, so schema admission is not
delegated to an importable verifier library:

    polarity-unevidenced      a terminal or coordinate asserts a connector polarity
    supply-not-permitted      a supply that is not a verified_official permitted input
    current-limit-absent      current flows through a rated part with nothing limiting it
    rail-short                two supply nets share a node
    input-floating            a component pin sits on no named net
    composed-circuit-invented a designed circuit cites no vetted library entry

What it cannot do is stated as plainly: **it does not simulate.** Structural validity
and functional correctness are different properties, and CircuitLM's measured gap
between them — ERC-valid 77–85%, functional Pass@1 21–51% — is the whole reason
`circuit_reference.simulated` is a required declaration rather than something this file
computes. Simulation happens once, when a circuit enters the vetted library; this file
checks that the unit is using one.

    python3 curricula/arduino_kit/verify_domain.py --domain <path>

Exit 0 accepts. Exit 1 rejects and prints one line per rule that fired.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

DOMAIN_SCHEMA = HERE / "domain.schema.v1.json"
KIT_CALIBRATION = HERE / "kit_calibration.v1.yaml"
CIRCUIT_LIBRARY = HERE / "circuit_library.v1.yaml"

# The polarity vocabulary, anchored so an ordinary word never trips it. A terminal
# legitimately called `source_lead_end` or `dc_input` says nothing about which lead is
# which; `positive_terminal` is a claim, and a claim needs primary evidence that
# structured data cannot hold. This is `L01-POLARITY-NEUTRAL`, and it is unconditional:
# a polarity claimed on a path that is later powered is no better evidenced than one
# claimed while it is disconnected.
POLARITY = re.compile(
    r"(?i)(^|[^a-z])(positive|negative|anode|cathode|polarity|plus_lead|minus_lead)([^a-z]|$)"
)

# A part is rated when it declares an absolute maximum current. Current through one of
# those with nothing limiting it is the canonical way a child's circuit destroys a
# component and becomes hot, and it is one of the two LLM failure modes CircuitLM
# catalogues by name.
CURRENT_UNITS = {"A", "mA", "uA"}


def _load(path: Path):
    # The curriculum-owned sidecars use JSON bytes even where their historical
    # extension remains .yaml. JSON is a YAML subset, so engine-side readers stay
    # compatible while the isolated verifier needs only the standard library.
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# The rules


def _strings(node, found=None) -> list[str]:
    """Every string **value**, at any depth. Keys are deliberately not collected.

    `supply.positive_net` is the contract's own word for a rail's role, not a claim
    about which physical lead is which. A scan that read keys would reject the schema
    for using its own vocabulary, which is the shape of a check that gets switched off.
    """
    found = [] if found is None else found
    if isinstance(node, dict):
        for value in node.values():
            _strings(value, found)
    elif isinstance(node, list):
        for value in node:
            _strings(value, found)
    elif isinstance(node, str):
        found.append(node)
    return found


def rule_polarity(domain) -> list[str]:
    """A polarity claim in the assembly map or the circuit, unless a primary source
    establishes *that* — not merely some other parameter.

    The exemption is deliberately narrow and deliberately present: a datasheet pinout
    **is** evidence of polarity, and forbidding the word outright would forbid teaching
    the thing. What is forbidden is asserting it with nothing behind it. "Some parameter
    carries a source" is not that exemption: every parameter carries a source, because
    the contract requires one, so reading it that way would retire the rule.
    """
    electrical = (domain or {}).get("electrical") or {}
    sourced = any(
        re.search(r"(?i)polarity|pinout|orientation", str(param.get("name", "")))
        and str(param.get("source", "")).strip()
        for param in ((electrical.get("component_spec") or {}).get("parameters") or [])
        if isinstance(param, dict)
    )
    if sourced:
        return []
    # The subject is what a reader is told: the assembly map the child follows, and any
    # polarity a pin claims. Net names are the contract's vocabulary and are not claims.
    circuit = electrical.get("circuit") or {}
    pins = [
        str(pin.get("polarity"))
        for component in circuit.get("components") or []
        if isinstance(component, dict)
        for pin in component.get("pins") or []
        if isinstance(pin, dict) and pin.get("polarity")
    ]
    problems = []
    for text in _strings((domain or {}).get("build_map")) + pins:
        if POLARITY.search(text):
            problems.append(
                f"polarity-unevidenced: {text!r} asserts a connector polarity and no "
                "component parameter carries a primary source that establishes one"
            )
    return sorted(set(problems))[:5]


def rule_supply(domain) -> list[str]:
    profile = (domain or {}).get("power_profile")
    if not profile:
        return []
    permitted = {
        entry["id"]: entry
        for entry in ((_load(KIT_CALIBRATION) or {}).get("power") or {}).get("permitted_inputs", [])
        if isinstance(entry, dict) and "id" in entry
    }
    cited = str(profile.get("source", ""))
    entry = permitted.get(cited)
    if entry is None:
        return [
            f"supply-not-permitted: {cited!r} is not an id in this kit's "
            f"power.permitted_inputs ({', '.join(sorted(permitted)) or 'none declared'})"
        ]
    if entry.get("verification") != "verified_official":
        return [
            f"supply-not-permitted: {cited!r} has verification "
            f"{entry.get('verification')!r}; an unverified input must be sourced and "
            "photographed before a unit may use it"
        ]
    return []


def _rated_parts(electrical) -> set[str]:
    rated = set()
    for entry in electrical.get("ratings_and_limits") or []:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("unit")) in CURRENT_UNITS:
            rated.add(str(entry.get("parameter", "")).lower())
    return rated


def rule_current_limit(domain) -> list[str]:
    electrical = (domain or {}).get("electrical") or {}
    circuit = electrical.get("circuit") or {}
    if circuit.get("status") != "designed_verified":
        return []  # nothing is powered, so nothing carries current
    if not _rated_parts(electrical):
        return [
            "current-limit-absent: the circuit is designed_verified and declares no "
            "current rating, so nothing states what must not be exceeded"
        ]
    limiting = [
        entry for entry in electrical.get("calculations") or []
        if isinstance(entry, dict) and entry.get("purpose") == "current_limiting"
    ]
    if not limiting:
        return [
            "current-limit-absent: current flows through a rated part and no calculation "
            "states the limiting element"
        ]
    return [
        f"current-limit-absent: the current-limiting calculation states "
        f"margin_to_rating {entry.get('margin_to_rating')!r}"
        for entry in limiting
        if not str(entry.get("margin_to_rating", "")).strip()
        or str(entry.get("margin_to_rating", "")).strip().lower() == "none"
    ]


def rule_rail_short(domain) -> list[str]:
    circuit = ((domain or {}).get("electrical") or {}).get("circuit") or {}
    supply = circuit.get("supply") or {}
    rails = {supply.get("positive_net"), supply.get("negative_net")} - {None}
    if len(rails) < 2:
        return []
    nodes: dict[str, set[str]] = {}
    for net in circuit.get("nets") or []:
        if isinstance(net, dict) and net.get("name") in rails:
            nodes[net["name"]] = set(net.get("nodes") or [])
    names = sorted(nodes)
    problems = []
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            shared = nodes[first] & nodes[second]
            if shared:
                problems.append(
                    f"rail-short: {first} and {second} share {sorted(shared)}"
                )
    return problems


def rule_floating_input(domain) -> list[str]:
    circuit = ((domain or {}).get("electrical") or {}).get("circuit") or {}
    if circuit.get("status") != "designed_verified":
        return []
    named = {net["name"] for net in circuit.get("nets") or [] if isinstance(net, dict) and "name" in net}
    problems = []
    for component in circuit.get("components") or []:
        if not isinstance(component, dict):
            continue
        for pin in component.get("pins") or []:
            if not isinstance(pin, dict):
                continue
            if pin.get("net") not in named:
                problems.append(
                    f"input-floating: {component.get('designator')}.{pin.get('pin')} sits "
                    f"on {pin.get('net')!r}, which is not a named net"
                )
    return problems


def rule_composed_circuit(domain, policy: str) -> list[str]:
    circuit = ((domain or {}).get("electrical") or {}).get("circuit") or {}
    if policy != "composed" or circuit.get("status") != "designed_verified":
        return []
    reference = (domain or {}).get("circuit_reference") or {}
    library = {
        entry["id"]
        for entry in (_load(CIRCUIT_LIBRARY) or {}).get("circuits", [])
        if isinstance(entry, dict) and "id" in entry
    } if CIRCUIT_LIBRARY.exists() else set()
    if not reference.get("library_id"):
        return [
            "composed-circuit-invented: circuit_policy is composed and this designed "
            "circuit cites no vetted library entry"
        ]
    if reference["library_id"] not in library:
        return [
            f"composed-circuit-invented: {reference['library_id']!r} is not an entry in "
            f"{CIRCUIT_LIBRARY.name}"
        ]
    if reference.get("simulated") is not True:
        return [
            f"composed-circuit-invented: {reference['library_id']!r} is not recorded as "
            "simulated, and an unsimulated library entry is an invented circuit that has "
            "been filed"
        ]
    return []


def verify(domain, policy: str = "composed") -> list[str]:
    return (
        rule_polarity(domain)
        + rule_supply(domain)
        + rule_current_limit(domain)
        + rule_rail_short(domain)
        + rule_floating_input(domain)
        + rule_composed_circuit(domain, policy)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", required=True, type=Path,
                        help="the unit's domain block, as JSON")
    parser.add_argument("--circuit-policy", default="composed")
    args = parser.parse_args()
    try:
        domain = _load(args.domain)
    except Exception as exc:  # noqa: BLE001 - an unreadable block is a rejected block
        print(f"domain-schema-invalid: {type(exc).__name__}: {exc}")
        return 1
    problems = verify(domain, args.circuit_policy)
    for problem in problems:
        print(problem)
    if not problems:
        print("accepted: 6 curriculum rules ran after engine schema validation, none fired. "
              "This is structural checking and not "
              "simulation; a circuit is simulated once, when it enters the library.")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
