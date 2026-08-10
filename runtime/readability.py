"""Readability and Bloom-verb scoring, shared by the fixture gate and by production.

These functions were defined inside `tests/gates/fr_p5_unit.py` and ran only against
hand-written fixtures, so `TEXT-READABILITY-BAND` and `TEXT-BLOOM-VERBS` never scored a
generated unit. They live here so `runtime/checks.py` runs the same metric over real
rendered text that the gate runs over its fixtures — one implementation, not two.

The gate bodies keep their harness dependencies injected through `bind_gate` rather than
imported, so this module stays free of any dependency on `tests/`.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Callable

_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
_SENTENCE = re.compile(r"[.!?]+(?:\s|$)")
_VOWEL_RUN = re.compile(r"[aeiouy]+")


def syllables(word: str) -> int:
    """Vowel runs, with a silent trailing ``e`` removed and a floor of one.

    A published syllabifier would be a dependency this repository does not have, and
    the band is what carries the judgement — the metric only has to be the same
    metric every time it is applied.
    """
    lowered = word.lower().strip("'’-")
    if not lowered:
        return 0
    if len(lowered) > 2 and lowered.endswith("e") and not lowered.endswith(("le", "ee", "ye")):
        lowered = lowered[:-1]
    return max(1, len(_VOWEL_RUN.findall(lowered)))


def grade_level(text: str) -> float | None:
    """Flesch-Kincaid grade level, or ``None`` when there is nothing to score."""
    words = _WORD.findall(text)
    sentences = max(1, len(_SENTENCE.findall(text)))
    if not words:
        return None
    total = sum(syllables(w) for w in words)
    return round(0.39 * (len(words) / sentences) + 11.8 * (total / len(words)) - 15.59, 2)


def text_violations(text: str, band, metric: str) -> list[str]:
    """Score one block of already-rendered child-facing text against the declared band."""
    if metric != "flesch_kincaid_grade":
        return [f"readability-metric-unknown:{metric!r} is not a metric this gate computes"]
    score = grade_level(text)
    if score is None:
        return ["readability-no-subject: the rendered text carries no words"]
    low, high = band
    if not low <= score <= high:
        problems = [f"readability-out-of-band: the unit scores {score} and the band is [{low}, {high}]"]
        return problems
    return []


def readability_violations(unit, band, metric: str) -> list[str]:
    problems: list[str] = []
    text = unit.get("child_facing_text") if isinstance(unit, dict) else None
    if not isinstance(text, list) or not [t for t in text if str(t).strip()]:
        return ["readability-no-subject: the unit declares no child_facing_text to score"]
    if metric != "flesch_kincaid_grade":
        return [f"readability-metric-unknown:{metric!r} is not a metric this gate computes"]
    score = grade_level("\n".join(str(t) for t in text))
    if score is None:
        return ["readability-no-subject: child_facing_text carries no words"]
    low, high = band
    if not low <= score <= high:
        problems.append(
            f"readability-out-of-band: the unit scores {score} and the band is [{low}, {high}]"
        )
    return problems


def bloom_flags(unit, table: dict) -> list[str]:
    """Every disagreement between a declared level and the verb that opens the
    objective. A **flag**, never a verdict: the level a verb implies is a reading, and
    human raters agree with each other on it only 46.58% of the time."""
    order = list(table)
    flags: list[str] = []
    objectives = ((unit or {}).get("pedagogy") or {}).get("learning_objectives") or []
    for index, objective in enumerate(objectives):
        declared = (objective or {}).get("bloom_level")
        statement = str((objective or {}).get("statement", "")).strip()
        opening = re.split(r"[^A-Za-z]+", statement, maxsplit=1)[0].lower()
        found = [level for level in order if opening in [v.lower() for v in table[level]]]
        if not found:
            flags.append(
                f"bloom-verb-unclassified: objective {index} opens with {opening!r}, "
                f"which no level's verb list claims"
            )
            continue
        if declared not in order:
            flags.append(
                f"bloom-verb-level-undeclared: objective {index} declares {declared!r}, "
                "which is not a level the table names"
            )
            continue
        implied = min(order.index(level) for level in found)
        if implied < order.index(declared):
            flags.append(
                f"bloom-verb-below-declared-level: objective {index} declares "
                f"{declared!r} and opens with {opening!r}, a {order[implied]!r} verb"
            )
        elif implied > order.index(declared):
            flags.append(
                f"bloom-verb-above-declared-level: objective {index} declares "
                f"{declared!r} and opens with {opening!r}, a {order[implied]!r} verb"
            )
    return flags


# --- gate bodies ---------------------------------------------------------------------

@dataclass
class GateBindings:
    """Everything the two gate bodies need from the `tests/gates` harness."""
    calibration: Path
    fixtures_dir: Path
    unit_files: Callable[[Any], list[Path]]
    load: Callable[[Path], Any]
    fixture: Callable[..., Any]
    gate_result: Callable[..., Any]
    rel: Callable[[Path], str]


BINDINGS: GateBindings | None = None


def bind_gate(bindings: GateBindings) -> None:
    global BINDINGS
    BINDINGS = bindings


def _bound() -> GateBindings:
    if BINDINGS is None:
        raise RuntimeError("runtime.readability gate bodies were called before bind_gate")
    return BINDINGS


def check_readability(ev):
    bound = _bound()
    calibration = ev.read_for_resolution(bound.calibration)
    ev.resolve("readability.band", bound.rel(bound.calibration), "the units under curricula/*/units/")
    declared = (calibration or {}).get("readability") or {}
    band, metric = declared.get("band"), str(declared.get("metric", ""))
    problems: list[str] = []
    if not (isinstance(band, list) and len(band) == 2):
        problems.append(
            f"readability-band-missing: {bound.rel(bound.calibration)} declares no two-element "
            "readability band, so the check has no premise to apply"
        )
        band = [0, 0]

    units = bound.unit_files(ev)
    for path in units:
        unit = ev.read_for_resolution(path)
        for problem in readability_violations(unit, band, metric):
            problems.append(f"{problem} ({bound.rel(path)})")

    line = (
        f"FR-P5-READABILITY {'PASS' if not problems else 'FAIL'} "
        f"({len(units)} units scanned, band {band}, metric {metric or 'none'}; "
        f"no generator exists, so the executed assertion is the fixture pair — RT-7)"
    )
    reject = bound.fixtures_dir / "unit_readability_above_band.reject.json"
    accept = bound.fixtures_dir / "unit_readability_in_band.accept.json"
    fixtures = [
        bound.fixture(
            name=bound.rel(reject),
            kind="reject",
            expected_error="readability-out-of-band",
            detector=lambda: (readability_violations(bound.load(reject), band, metric) or [None])[0],
        ),
        bound.fixture(
            name=bound.rel(accept),
            kind="accept",
            detector=lambda: (readability_violations(bound.load(accept), band, metric) or [None])[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return bound.gate_result(not problems, detail, fixtures, stdout=line)


def check_bloom_verbs(ev):
    bound = _bound()
    calibration = ev.read_for_resolution(bound.calibration)
    ev.resolve("bloom_verbs", bound.rel(bound.calibration), "each unit's declared bloom_level")
    table = (calibration or {}).get("bloom_verbs") or {}

    # What fails this gate is the flagging machinery being absent or unusable — never
    # a flag. A blocking Bloom check would be a 46.58%-reliable rule with the force of
    # a schema.
    problems: list[str] = []
    if not isinstance(table, dict) or len(table) < 2:
        problems.append(
            f"bloom-table-missing: {bound.rel(bound.calibration)} declares no ordered bloom_verbs "
            "table, so no verb can be classified at all"
        )
    for level, verbs in (table or {}).items():
        if not isinstance(verbs, list) or not verbs:
            problems.append(f"bloom-table-incomplete:{level} lists no verbs")

    units = bound.unit_files(ev)
    flags: list[str] = []
    for path in units:
        flags += [
            f"{flag} ({bound.rel(path)})"
            for flag in bloom_flags(ev.read_for_resolution(path), table)
        ]

    line = (
        f"FR-P5-BLOOM-VERBS {'PASS' if not problems else 'FAIL'} "
        f"({len(units)} units scanned, {len(table)} levels, {len(flags)} flags raised — "
        f"flags are recorded and never block; no generator exists, so the executed "
        f"assertion is the fixture pair — RT-7)"
    )
    for flag in flags:
        ev.note(f"bloom-flag: {flag}")
    reject = bound.fixtures_dir / "unit_bloom_verb_below_level.reject.json"
    accept = bound.fixtures_dir / "unit_bloom_verb_matches_level.accept.json"
    fixtures = [
        bound.fixture(
            name=bound.rel(reject),
            kind="reject",
            expected_error="bloom-verb-below-declared-level",
            detector=lambda: (bloom_flags(bound.load(reject), table) or [None])[0],
        ),
        bound.fixture(
            name=bound.rel(accept),
            kind="accept",
            detector=lambda: (bloom_flags(bound.load(accept), table) or [None])[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    if flags:
        detail += " | flags: " + "; ".join(flags)
    return bound.gate_result(not problems, detail, fixtures, stdout=line)
