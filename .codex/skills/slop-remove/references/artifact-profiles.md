# Artifact profiles

Read only the section matching the artifact. Binding artifact contracts override these defaults.

## learner_prose

- Voice: warm, calm, and direct.
- Use concrete objects and actions before abstractions.
- Prefer short paragraphs and define technical words at first useful mention.
- Preserve pedagogical sequence, expected observations, safe "not yet" outcomes, and adult/learner responsibility.
- First person and author opinions remain off unless the curriculum contract explicitly calls for them.
- Follow `meta_prompt/assets/unit_prose.v1.md` and the active readability, pedagogy, and safety contracts.

## operational_documentation

- Voice: concise and neutral.
- Each operational sentence should identify a condition, component, input, output, transition, gate, dependency, boundary, failure owner, or useful consequence.
- Preserve required information architecture, exact interfaces, examples, recovery routes, and status vocabulary.
- Remove process narration unless it records provenance or an operationally relevant event.

## issue_plan_verification

- Voice: neutral and evidence-led.
- Preserve findings, dispositions, acceptance criteria, authority boundaries, test status, and uncertainty.
- Keep distinctions between observed evidence, inference, user decisions, and unexecuted tests.
- Do not make failure language gentler when severity is part of the record.

## research

- Voice: analytical and restrained.
- Preserve citations, attribution, causal strength, limitations, and warranted hedging.
- Replace vague attribution with a named source when the evidence provides one; otherwise retain the uncertainty or remove the unsupported claim.
- Do not convert mixed or weak evidence into confident prose.

## conversational

- Voice: natural and direct.
- First person and opinions are allowed when they reflect the actual speaker role and do not invent experience or authority.
- Rhythm may vary more than in technical artifacts.
- Remove canned enthusiasm, sycophancy, and generic closing invitations.

