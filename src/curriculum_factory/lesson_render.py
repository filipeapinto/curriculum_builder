"""Field-aware markdown rendering for one unit document.

Every block of `schemas/lab.schema.v4.json` has a template function here. Nothing is
serialized: a field with no template branch raises `RendererError` rather than reaching
the learner as JSON or being dropped in silence.
"""
from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Callable, Iterable


class RendererError(RuntimeError):
    """A required, non-empty schema field has no template branch."""


# Every field name each template function consumes, by its position in the document.
# A required, non-empty field absent from its entry is an unrendered field and raises.
HANDLED_FIELDS: dict[str, set[str]] = {
    "identity": {"unit_id", "slug", "kind", "title", "subject_job_sentence"},
    "pedagogy": {"learning_objectives", "prior_knowledge", "misconceptions", "vocabulary",
                 "scaffolding", "cognitive_load"},
    "pedagogy.learning_objectives[]": {"statement", "bloom_level", "success_criterion"},
    "pedagogy.prior_knowledge": {"prerequisite_labs", "assumed_ideas", "retrieval_prompt"},
    "pedagogy.misconceptions[]": {"misconception", "why_it_is_common", "confronted_by"},
    "pedagogy.vocabulary[]": {"term", "child_definition", "introduced_in"},
    "pedagogy.scaffolding": {"adult_does", "child_does", "fading_note"},
    "pedagogy.cognitive_load": {"segments", "concrete_before_abstract", "worked_example"},
    "sequence": {"engage", "explore", "explain", "elaborate", "evaluate"},
    "sequence.engage": {"hook", "eliciting_question"},
    "sequence.explore": {"predict", "observe", "steps", "expected_observation", "not_yet_outcome"},
    "sequence.explore.predict": {"question", "options", "recorded_before_observing"},
    "sequence.explore.observe": {"what_to_observe", "record_method", "evidence_fields"},
    "sequence.explore.steps[]": {"number", "action"},
    "sequence.explore.not_yet_outcome": {"symptom", "first_check"},
    "sequence.explain": {"what_you_saw", "why_it_happened", "self_explanation_prompt"},
    "sequence.elaborate": {"near_transfer", "far_transfer"},
    "sequence.evaluate": {"success_criteria_checklist", "hinge_question", "next_lab_link"},
    "sequence.evaluate.hinge_question": {"question", "reveals"},
    "content": {"identification", "troubleshooting", "sourced_claims", "derived",
                "unresolved_visual_roles"},
    "content.identification": {"child_name", "technical_name", "distinguishing_features",
                               "orientation_cue", "parts"},
    "content.identification.parts[]": {"label", "role"},
    "content.troubleshooting[]": {"what_you_notice", "likely_reason", "safe_first_check"},
    "content.sourced_claims[]": {"claim", "source_locator", "subject_scope", "evidence_scope",
                                 "derivation"},
    "safety": {"hazard_mode", "adult_verification"},
    "safety.adult_verification": {"variant", "marking", "verified_configuration", "limits",
                                  "endpoint_check", "signoff_required"},
}

# Pandoc rewrites a leading "[ ]" into a task-list glyph the shipped font has no character
# for, so it prints as a missing-glyph box. "[_]" is left alone and prints as a tick box.
TICK_BOX = "[_]"

_RECORD_METHOD_BRANCHES = {"evidence_table", "drawing_prompt", "tick_or_circle",
                           "adult_read_measurement"}

_SOURCE_KIND_CAPTION = {
    "verified_photograph": "Verified photograph.",
    "deterministic_render": "Drawn directly from this unit's own recorded data.",
    "imagegen": "Illustration only — it carries no exact detail.",
}

_ROLE_HEADING = {
    "subject_identification": "What it looks like",
    "purpose_or_application": "What it is used for",
    "orientation_and_parts": "Which way round it goes",
    "mechanism": "How it works",
    "assembly_or_path_map": "The map to follow",
    "expected_result": "Your evidence card",
    "safety_or_troubleshooting": "Safety picture",
}


def _guard(block: Any, key: str) -> None:
    """Raise if `block` carries a populated field this module has no branch for."""
    handled = HANDLED_FIELDS[key]
    if not isinstance(block, dict):
        return
    unhandled = sorted(name for name, value in block.items()
                       if name not in handled and value not in (None, "", [], {}))
    if unhandled:
        raise RendererError(f"unrendered required field(s) at {key}: {', '.join(unhandled)}")


def _guard_each(items: Iterable[Any], key: str) -> None:
    for item in items:
        _guard(item, key)


def _vocabulary_for(vocabulary: list[dict[str, Any]], section: str) -> list[str]:
    lines: list[str] = []
    for entry in vocabulary:
        _guard(entry, "pedagogy.vocabulary[]")
        if entry["introduced_in"] == section:
            lines.extend([f"**New word — {entry['term']}.** {entry['child_definition']}", ""])
    return lines


def render_identity(identity: dict[str, Any]) -> list[str]:
    _guard(identity, "identity")
    return [f"# {identity['unit_id']} — {identity['title']}", "",
            f"*{identity['kind'].capitalize()} unit · {identity['slug'].replace('-', ' ')} · "
            "draft pending downstream human review.*", "",
            identity["subject_job_sentence"], ""]


def render_before_we_start(prior_knowledge: dict[str, Any]) -> list[str]:
    """Retrieval practice: the child recalls, rather than re-reads, before new material."""
    _guard(prior_knowledge, "pedagogy.prior_knowledge")
    lines = ["## Before we start", "",
             "Answer this from memory, without looking back:", "",
             f"> {prior_knowledge['retrieval_prompt']}", ""]
    earlier = prior_knowledge.get("prerequisite_labs") or []
    if earlier:
        lines.extend([f"This unit follows {', '.join(earlier)}.", ""])
    assumed = prior_knowledge.get("assumed_ideas") or []
    if assumed:
        lines.append("You should already be able to say:")
        lines.append("")
        lines.extend(f"- {idea}" for idea in assumed)
        lines.append("")
    return lines


def render_objectives(objectives: list[dict[str, Any]]) -> list[str]:
    _guard_each(objectives, "pedagogy.learning_objectives[]")
    lines = ["## What I will learn", ""]
    lines.extend(f"- {objective['success_criterion']}" for objective in objectives)
    lines.append("")
    return lines


def render_engage(engage: dict[str, Any], vocabulary: list[dict[str, Any]]) -> list[str]:
    _guard(engage, "sequence.engage")
    lines = ["## Why this matters", "", engage["hook"], ""]
    lines.extend(_vocabulary_for(vocabulary, "engage"))
    lines.extend(["Before you read on, say what you already think:", "",
                  f"**{engage['eliciting_question']}**", ""])
    return lines


def render_identification(identification: dict[str, Any]) -> list[str]:
    _guard(identification, "content.identification")
    _guard_each(identification["parts"], "content.identification.parts[]")
    lines = ["## Meet it", "",
             f"Most people call it a **{identification['child_name']}**. Its proper name is "
             f"*{identification['technical_name']}*.", "",
             identification["distinguishing_features"], ""]
    cue = identification.get("orientation_cue")
    if cue:
        lines.extend([f"**Which way round:** {cue}", ""])
    lines.extend(["The parts that matter here:", ""])
    lines.extend(f"- **{part['label']}** — {part['role']}" for part in identification["parts"])
    lines.append("")
    return lines


def render_scaffolding(scaffolding: dict[str, Any]) -> list[str]:
    _guard(scaffolding, "pedagogy.scaffolding")
    lines = ["### Who does what", "", "An adult:", ""]
    lines.extend(f"- {item}" for item in scaffolding["adult_does"])
    lines.extend(["", "You:", ""])
    lines.extend(f"- {item}" for item in scaffolding["child_does"])
    lines.extend(["", f"*{scaffolding['fading_note']}*", ""])
    return lines


def render_cognitive_load(cognitive_load: dict[str, Any]) -> list[str]:
    _guard(cognitive_load, "pedagogy.cognitive_load")
    lines = ["### How this unit is broken up", ""]
    lines.extend(f"{index}. {segment}"
                 for index, segment in enumerate(cognitive_load["segments"], 1))
    lines.extend(["", f"Start with something you can hold: {cognitive_load['concrete_before_abstract']}",
                  ""])
    worked = cognitive_load.get("worked_example")
    if worked:
        lines.extend(["**Worked example.** " + worked, ""])
    return lines


def render_recording_block(observe: dict[str, Any]) -> list[str]:
    """The place the learner puts what they found, keyed on how they are asked to record it."""
    method = observe["record_method"]
    if method not in _RECORD_METHOD_BRANCHES:
        raise RendererError(f"no recording template for: {method}")
    fields = observe.get("evidence_fields") or []
    lines = ["### Record what you found", ""]
    if method == "evidence_table":
        lines.extend(["| What to record | What you found |", "| --- | --- |"])
        lines.extend(f"| {field} | |" for field in fields)
        if not fields:
            lines.append("| Your observation | |")
        lines.append("")
    elif method == "drawing_prompt":
        lines.extend(["Draw what you found in the space below.", ""])
        lines.extend(f"**{field}**\\\n\\\n\\" for field in fields)
        lines.append("")
    elif method == "tick_or_circle":
        lines.extend(f"- {TICK_BOX} {field}" for field in fields)
        if not fields:
            lines.append(f"- {TICK_BOX} What you found")
        lines.append("")
    else:
        lines.extend(["An adult reads each value and writes it here with you.", ""])
        lines.extend(f"- {field}: ______________  *(written down by an adult)*"
                     for field in fields)
        if not fields:
            lines.append("- Reading: ______________  *(written down by an adult)*")
        lines.append("")
    return lines


def render_explore(explore: dict[str, Any], vocabulary: list[dict[str, Any]]) -> list[str]:
    _guard(explore, "sequence.explore")
    predict, observe = explore["predict"], explore["observe"]
    _guard(predict, "sequence.explore.predict")
    _guard(observe, "sequence.explore.observe")
    _guard_each(explore["steps"], "sequence.explore.steps[]")
    _guard(explore["not_yet_outcome"], "sequence.explore.not_yet_outcome")

    lines = ["## Try it", ""]
    lines.extend(_vocabulary_for(vocabulary, "explore"))
    lines.extend(["### Predict first", "", f"**{predict['question']}**", ""])
    options = predict.get("options") or []
    for letter, option in zip("ABCDEFGH", options):
        lines.append(f"- **{letter}.** {option}")
    if options:
        lines.append("")
    if predict.get("recorded_before_observing") is True:
        lines.extend(["> **Write your answer down now**, before you look. "
                      "A prediction made after the fact teaches nothing.", ""])
    lines.extend(["### What to look for", "", observe["what_to_observe"], "",
                  "### Do this", ""])
    lines.extend(f"{step['number']}. {step['action']}" for step in explore["steps"])
    lines.append("")
    lines.extend(render_recording_block(observe))
    lines.extend(["**If it goes as planned:** " + explore["expected_observation"], ""])
    not_yet = explore["not_yet_outcome"]
    lines.extend(["### A safe \"not yet\"", "",
                  f"Sometimes this happens instead: {not_yet['symptom']} "
                  "That is a normal result, not a mistake.", "",
                  f"Your first check: {not_yet['first_check']}", ""])
    return lines


def render_misconceptions(misconceptions: list[dict[str, Any]]) -> list[str]:
    _guard_each(misconceptions, "pedagogy.misconceptions[]")
    lines = ["### A common wrong idea", ""]
    for entry in misconceptions:
        lines.extend([f"Many people think: *{entry['misconception']}*", "",
                      f"It is easy to think that because {entry['why_it_is_common'][0].lower()}"
                      f"{entry['why_it_is_common'][1:]}", "",
                      f"Here is what shows it is wrong: {entry['confronted_by']}", ""])
    return lines


def render_explain(explain: dict[str, Any], vocabulary: list[dict[str, Any]]) -> list[str]:
    _guard(explain, "sequence.explain")
    lines = ["## What happened", ""]
    lines.extend(_vocabulary_for(vocabulary, "explain"))
    lines.extend(["**What you saw.** " + explain["what_you_saw"], "",
                  "**Why it happened.** " + explain["why_it_happened"], ""])
    lines.extend(["Now say it back in your own words:", "",
                  f"> {explain['self_explanation_prompt']}", ""])
    return lines


def render_elaborate(elaborate: dict[str, Any], vocabulary: list[dict[str, Any]]) -> list[str]:
    _guard(elaborate, "sequence.elaborate")
    lines = ["## What it solves", ""]
    lines.extend(_vocabulary_for(vocabulary, "elaborate"))
    lines.extend(["Try this next, with what you already have:", ""])
    lines.extend(f"- {item}" for item in elaborate["near_transfer"])
    lines.extend(["", "And the same idea, out in the world:", ""])
    lines.extend(f"- {item}" for item in elaborate["far_transfer"])
    lines.append("")
    return lines


def render_evaluate(evaluate: dict[str, Any], vocabulary: list[dict[str, Any]]) -> list[str]:
    """`reveals` is teacher-facing and is rendered in the adult section, never here."""
    _guard(evaluate, "sequence.evaluate")
    _guard(evaluate["hinge_question"], "sequence.evaluate.hinge_question")
    lines = ["## Check yourself", ""]
    lines.extend(_vocabulary_for(vocabulary, "evaluate"))
    lines.extend(f"- {TICK_BOX} {item}" for item in evaluate["success_criteria_checklist"])
    lines.extend(["", "One last question:", "",
                  f"**{evaluate['hinge_question']['question']}**", ""])
    link = evaluate.get("next_lab_link")
    if link:
        lines.extend([f"*Next: {link}*", ""])
    return lines


def render_troubleshooting(troubleshooting: list[dict[str, Any]]) -> list[str]:
    _guard_each(troubleshooting, "content.troubleshooting[]")
    lines = ["## If something looks off", "",
             "None of these is a mistake — they are normal, and each has a calm first move.", "",
             "| What you notice | Why it happens | Your first check |", "| --- | --- | --- |"]
    lines.extend(f"| {row['what_you_notice']} | {row['likely_reason']} | {row['safe_first_check']} |"
                 for row in troubleshooting)
    lines.append("")
    return lines


def render_adult_verification(safety: dict[str, Any], *,
                              objectives: list[dict[str, Any]] | None = None,
                              hinge_question: dict[str, Any] | None = None) -> list[str]:
    """A visibly separate adult-only section. Nothing above this heading is teacher-facing."""
    _guard(safety, "safety")
    verification = safety["adult_verification"]
    _guard(verification, "safety.adult_verification")
    lines = ["## Adult verification (adult only)", "",
             f"**Hazard class:** {safety['hazard_mode']}", "",
             "Confirm each of these before releasing the activity:", "",
             f"- {TICK_BOX} Equipment identified: {verification['variant']}",
             f"- {TICK_BOX} Marking on the item: {verification['marking']}",
             f"- {TICK_BOX} Set up as verified: {verification['verified_configuration']}",
             f"- {TICK_BOX} Stays inside these bounds: {verification['limits']}",
             f"- {TICK_BOX} Final check: {verification['endpoint_check']}", ""]
    if objectives:
        lines.extend(["**What this unit is teaching:**", ""])
        lines.extend(f"- {objective['statement']} *({objective['bloom_level']})*"
                     for objective in objectives)
        lines.append("")
    if hinge_question:
        lines.extend([f"**The last question tells you:** {hinge_question['reveals']}", ""])
    if verification["signoff_required"]:
        lines.extend(["Adult signature: ______________________    Date: ______________", ""])
    else:
        lines.extend(["*No adult signature is required for this unit.*", ""])
    return lines


def render_visual(visual: dict[str, Any]) -> list[str]:
    embedded = Path(visual["provenance"]["embedded_as"]).name
    role = visual["role"]
    lines = [f"![{_ROLE_HEADING.get(role, role.replace('_', ' '))}](assets/{embedded})", "",
             f"*{_ROLE_HEADING.get(role, role.replace('_', ' '))}. "
             f"{_SOURCE_KIND_CAPTION.get(visual['source_kind'], '')}*", ""]
    omission = visual.get("omission_finding")
    if omission:
        lines.extend([f"*What it does not show: {omission}*", ""])
    return lines


def domain_fact_lines(domain: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    """The assembly authority, rendered verbatim from the domain's own data.

    Returns the lines and the `derived[]` records proving each rendered string came from
    a resolving pointer into this unit's domain block.
    """
    build_map = domain.get("build_map") or {}
    lines = ["## The map to follow", ""]
    derived: list[dict[str, Any]] = []

    def emit(pointer: str, value: str, template: Callable[[str], str]) -> None:
        lines.append(template(value))
        derived.append({"domain_pointer": pointer, "rendered_value": value})

    kind = build_map.get("map_kind")
    if kind == "breadboard":
        lines.extend(["Work through the map in this order:", ""])
        for index, step in enumerate(build_map.get("placement_steps", [])):
            emit(f"/build_map/placement_steps/{index}", step, lambda v: f"1. {v}")
        lines.extend(["", "Named on the map:", ""])
        for index, feature in enumerate(build_map.get("labelled_features", [])):
            emit(f"/build_map/labelled_features/{index}", feature,
                 lambda v: f"- {v.replace('_', ' ')}")
        lines.append("")
        inset = build_map.get("safety_inset") or {}
        if inset.get("shows"):
            emit("/build_map/safety_inset/shows", inset["shows"],
                 lambda v: f"**On the safety inset:** {v}")
            lines.append("")
    elif build_map.get("relationship") == "same_wire":
        # The prose says what the map draws, so the two cannot disagree: the first two
        # points are one wire's two ends, and anything further stands on its own.
        traced = build_map.get("traced_path", [])
        lines.extend(["These two are the two ends of one wire, joined to each other:", ""])
        for index, point in enumerate(traced[:2]):
            emit(f"/build_map/traced_path/{index}", point, lambda v: f"- {v}")
        if traced[2:]:
            lines.extend(["", "And find this on its own, joined to neither end:", ""])
            for offset, point in enumerate(traced[2:], start=2):
                emit(f"/build_map/traced_path/{offset}", point, lambda v: f"- {v}")
        lines.append("")
    else:
        lines.extend(["Find each of these on the map:", ""])
        for index, point in enumerate(build_map.get("traced_path", [])):
            emit(f"/build_map/traced_path/{index}", point, lambda v: f"- {v}")
        lines.append("")

    card = build_map.get("evidence_card") or {}
    if card.get("prompt"):
        lines.extend(["### Your evidence card", ""])
        emit("/build_map/evidence_card/prompt", card["prompt"], lambda v: v)
        lines.append("")
        for index, record in enumerate(card.get("child_records", [])):
            emit(f"/build_map/evidence_card/child_records/{index}", record,
                 lambda v: f"- {TICK_BOX} {v}")
        lines.append("")

    behaviour = (domain.get("electrical") or {}).get("behaviour") or {}
    if behaviour.get("child_level"):
        lines.extend(["### In one sentence", ""])
        emit("/electrical/behaviour/child_level", behaviour["child_level"], lambda v: v)
        lines.append("")
    return lines, derived


ADULT_HEADING = "## Adult verification (adult only)"


def child_facing_text(markdown: str) -> str:
    """The learner's own prose, with markdown syntax and the adult-only section removed.

    This is what `TEXT-READABILITY-BAND` scores: the adult section is written for an adult
    and scoring it against a child's band would measure the wrong reader.
    """
    body = markdown.split(ADULT_HEADING, 1)[0]
    lines = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("|", "![", "---")):
            continue
        stripped = re.sub(r"^#{1,6}\s*", "", stripped)
        stripped = re.sub(r"^[-*]\s*(\[[ x]\]\s*)?", "", stripped)
        stripped = re.sub(r"^\d+\.\s*", "", stripped)
        stripped = re.sub(r"^>\s*", "", stripped)
        stripped = re.sub(r"[*_`\\]", "", stripped)
        if stripped:
            # A heading or a bullet is a unit of reading. Without a terminator they run
            # together into one enormous sentence and the words-per-sentence term of any
            # readability metric becomes meaningless.
            lines.append(stripped if stripped[-1] in ".!?:" else stripped + ".")
    return "\n".join(lines)


def derived_records(lab: dict[str, Any]) -> list[dict[str, Any]]:
    """The `derived[]` array for this unit — one entry per fact the renderer emits verbatim."""
    return domain_fact_lines(lab["domain"])[1]


# Section anchors in `unit_prose.v1.md` arc order. A visual is placed immediately after
# the section its own `supports_section` names.
_ANCHOR_ORDER = ["engage", "identification", "explore", "assembly", "explain", "elaborate",
                 "evaluate", "troubleshooting", "adult_verification"]


def render_unit(lab: dict[str, Any]) -> str:
    """Assemble one unit document in `unit_prose.v1.md` arc order."""
    _guard(lab.get("content", {}), "content")
    _guard(lab.get("pedagogy", {}), "pedagogy")
    _guard(lab.get("sequence", {}), "sequence")

    pedagogy, sequence, content = lab["pedagogy"], lab["sequence"], lab["content"]
    vocabulary = pedagogy.get("vocabulary") or []

    sections: dict[str, list[str]] = {
        "engage": render_engage(sequence["engage"], vocabulary),
        "identification": render_identification(content["identification"]),
        "explore": (render_scaffolding(pedagogy["scaffolding"])
                    + render_cognitive_load(pedagogy["cognitive_load"])
                    + render_explore(sequence["explore"], vocabulary)),
        "assembly": domain_fact_lines(lab["domain"])[0],
        "explain": (render_explain(sequence["explain"], vocabulary)
                    + render_misconceptions(pedagogy["misconceptions"])),
        "elaborate": render_elaborate(sequence["elaborate"], vocabulary),
        "evaluate": render_evaluate(sequence["evaluate"], vocabulary),
        "troubleshooting": render_troubleshooting(content["troubleshooting"]),
        "adult_verification": render_adult_verification(
            lab["safety"], objectives=pedagogy["learning_objectives"],
            hinge_question=sequence["evaluate"]["hinge_question"]),
    }

    placed: dict[str, list[dict[str, Any]]] = {anchor: [] for anchor in _ANCHOR_ORDER}
    for visual in lab.get("visuals", []):
        placed.setdefault(visual["supports_section"], []).append(visual)

    lines = render_identity(lab["identity"])
    lines += render_before_we_start(pedagogy["prior_knowledge"])
    lines += render_objectives(pedagogy["learning_objectives"])
    for anchor in _ANCHOR_ORDER:
        lines += sections[anchor]
        for visual in placed.get(anchor, []):
            lines += render_visual(visual)

    unresolved = content.get("unresolved_visual_roles") or []
    if unresolved:
        lines += ["## Picture still needed (adult only)", "",
                  "This unit ships without a picture it is supposed to have. "
                  "It is not accepted until one is supplied:", ""]
        lines += [f"- **{entry['role']}** — {entry['reason']}" for entry in unresolved]
        lines.append("")

    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"
