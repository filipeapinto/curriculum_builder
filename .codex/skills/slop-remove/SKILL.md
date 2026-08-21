---
name: slop-remove
description: Tighten human-facing prose in Curriculum Factory artifacts by removing generic AI patterns while preserving contracts, evidence, safety, pedagogy, provenance, and version history. Use when asked to unslop, de-AI, humanize, simplify, or improve repository prose; do not use for code cleanup or as an automatic rewrite of machine-consumed or immutable artifacts.
---

# Slop remove

Make repository prose concrete, economical, and appropriate to its reader. Preserve the artifact's job. A less generic sentence is not an improvement if it weakens a contract, changes a fact, or hides uncertainty.

## Establish the editing boundary

Identify the artifact class before editing:

- **Learner-facing curriculum:** favor concrete objects and actions, short paragraphs, defined vocabulary, calm troubleshooting, and age-appropriate explanations. Follow `meta_prompt/assets/unit_prose.v1.md` and the active readability, pedagogy, and safety contracts.
- **Operational documentation:** make every sentence name a condition, component, input, output, state transition, gate, dependency, boundary, failure owner, or useful consequence. Preserve required information architecture.
- **Issue reports, plans, and verification records:** remove filler without changing findings, dispositions, acceptance criteria, status vocabulary, evidence distinctions, or uncertainty.
- **Research prose:** tighten rhetoric while preserving citations, attribution, causal strength, limitations, and warranted hedging.
- **Conversational or explanatory prose:** a restrained human voice is appropriate when it does not invent opinions or imply authority.

Do not rewrite code, JSON, YAML, schemas, commands, identifiers, hashes, URLs, citations, quoted evidence, source receipts, or generated data merely to improve style. Do not modify an immutable or superseded artifact in place. If repository rules require a new version, create the next version only when the user authorized an edit; otherwise report proposed changes.

## Preserve before improving

Record the facts and constraints that must survive. At minimum, protect:

- names, numbers, units, dates, negations, modal force, scope, and ordering;
- citations, evidence references, provenance, digests, and source boundaries;
- schema fields, controlled vocabulary, status values, and acceptance criteria;
- safety instructions, adult/learner responsibility, stop conditions, and expected observations;
- pedagogical sequence, reading band, defined terminology, and required repetition;
- required headings, tables, examples, and accessibility content;
- statements of uncertainty, absence of evidence, and untested paths.

Repository contracts outrank this skill. Read the relevant current contract before editing when the artifact identifies one or its location makes one discoverable. Do not infer that prose is redundant merely because a schema or another artifact contains related information; duplication may be an intentional interface or safety control.

## Edit in three passes

### 1. Remove empty rhetoric

Cut or replace:

- throat-clearing, generic introductions, generic conclusions, and process narration;
- puffery, promotional adjectives, and claims of importance without evidence;
- chatbot phrases, congratulations, sycophancy, and invitations that add no next action;
- vague attribution such as "experts believe" when no source is named;
- formulaic contrast, forced groups of three, false ranges, and repeated summary sections;
- superficial `-ing` clauses that imply a consequence without explaining or sourcing it;
- ornamental synonyms that rename the same actor or concept.

If removing a sentence changes no instruction, fact, relationship, qualification, or reader decision, remove it.

### 2. Make the content concrete

- Name the actor when responsibility matters.
- Replace feelings about a mechanism with what the mechanism does.
- Replace qualitative claims with the observed result or measurement when available.
- Prefer a plain word when it preserves the domain meaning.
- Split a sentence when a reader must backtrack to find its subject, condition, or result.
- Repeat a precise term instead of cycling through synonyms.
- Keep domain terms such as `scaffolding` when they name repository-defined concepts. Do not apply a generic jargon blacklist to controlled or technically exact vocabulary.
- Prefer active voice for instructions and ownership. Keep passive voice when the actor is unknown, irrelevant, or the artifact deliberately centers the state or result.

Ask of each sentence: could it appear unchanged in an unrelated repository? If yes, replace it with repository-specific information or remove it.

### 3. Restore an appropriate human voice

Avoid sterile uniformity, but do not manufacture personality. Vary sentence length where it improves reading rhythm. Use first person or an opinion only when the artifact class and authorial role permit it. Do not add emotional reactions, jokes, deliberate messiness, or false certainty to technical, evidentiary, safety, or governance artifacts.

Treat punctuation as syntax, not as an AI detector. Remove repeated em dashes, colons, parentheses, bold lead-ins, title case, or decorative symbols when they become mannerisms. Retain them when they express a real hierarchy, qualification, definition, range, or interface convention.

## Validate the result

Compare the revision with the protected facts and constraints. Then run the repository's relevant validators when editing is authorized and the commands are discoverable. Check, as applicable:

- schema and parser validity;
- citation and evidence-reference preservation;
- readability, pedagogy, and safety gates;
- HTML structure, accessibility, and rendering;
- version lineage and immutable-predecessor preservation;
- tests or acceptance checks named by the artifact.

Do not report style improvement as functional verification. If a requested rewrite cannot preserve a binding constraint, leave that passage unchanged and explain the conflict.

## Deliver the result

For an edit request, return the revised artifact or applied patch, summarize the material prose changes, and state which validations ran. For a review-only request, identify concrete passages, explain what each obscures, and propose bounded replacements without modifying files.

Do not claim that text is "human" or detector-proof. State only the observable improvements: reduced filler, clearer actors, more concrete mechanisms, preserved evidence, or better reader fit.
