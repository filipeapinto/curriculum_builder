# Document contract

Full normative source: `work-lib/specs/skill_family_doc_create_skill/skill_family_doc_create_skill.spec.v3.html`.
This file restates the parts of that spec you need while composing and validating the
guide, organized for lookup rather than narrative reading.

## 1. Canonical location

| Repository context | Canonical current document |
|---|---|
| Repo has `work-lib/` | `<repo-root>/work-lib/docs/skill-families/<family-slug>/<family-slug>-guide.vN.html` |
| Repo has no `work-lib/` | `<repo-root>/docs/skill-families/<family-slug>/<family-slug>-guide.vN.html` |
| User-approved override | The exact supplied `.html` path |

`<family-slug>`: lowercase kebab-case. Normalize spaces/underscores to hyphens, collapse
repeated hyphens, strip anything outside `a-z0-9-`. Derive it from an explicit family
declaration or a common specification ID — never from filename pattern-matching alone.
Once published, the slug is stable unless the user explicitly authorizes a rename.

The guide never lives inside one component's own skill folder (falsely implies that
component owns the family) and never lives in the family's engineering-spec directory
(caller documentation and builder authority are different artifact classes).

Every guide filename begins with the family slug and carries its embedded version:
`<family-slug>-guide.vN.html`. On `update`, retain the predecessor unchanged and
write a new sibling at version `N+1`; never overwrite or silently move a published
version. `audit` never moves or writes anything unless the caller explicitly asks for a fix.

Infer normal mode from versioned siblings whose embedded model parses, conforms to the
schema, and matches the filename: no matching guide = `create` version 1; otherwise
select the highest embedded version `N` and create version `N+1`. Source-digest
mismatches are update evidence and become `SOURCE_DRIFT`; they do not break lineage.
Folder existence alone does not cause an increment. A duplicate version,
filename/model mismatch, or structurally invalid highest candidate is
`LOCATION_CONFLICT`; never guess from filenames alone.

Maintain one cross-family index at `<docs-root>/skill-families/index.md`. After a
new or updated guide passes validation, regenerate the index from all canonical
`*/<family-slug>-guide.vN.html` files. The indexer selects the highest valid
version per family. The Markdown index contains only family slug, current
version, and generator type (`claude` or `codex`). `audit` is read-only and does not
regenerate it.

Record the executing system separately from the family sources in
`assurance.generator`: `agent`, `skill`, and `implementation`. Generator provenance
does not constrain whether the documented components live under `.claude/skills/`,
`.codex/skills/`, or elsewhere.

## 2. Required information architecture

Structure the guide as a progressive-disclosure engineering portal: discovery first,
goal-oriented operation next, technical reference after that, and trust evidence last.
Do not mix architecture explanation, invocation steps, reference tables, and provenance
inside the same section.

The following sections and order are required:

1. **Overview** — outcome, use when, do not use when, default entry point, operational
   status. Keep this scannable; no architecture history or source narration.
2. **System context** — one C4-style context/interface view showing the caller,
   family boundary, orchestrator, member skills, external validators/runtime, and final
   outputs. Every member-skill node must show the full skill identifier, responsibility,
   explicit inputs, explicit outputs, and a complete realistic example covering every
   declared required and optional input category and every output category (filename,
   path pattern, value, or compact shape). Distinguish caller inputs, gate preconditions,
   fixed dependencies, and produced artifacts. For orchestrators, separately show the
   caller-facing result, direct writes, delegated outputs with actual writers, and
   control outputs; lack of direct writes never erases the caller-facing result. State what is inside and outside the family
   boundary. Never abbreviate skill names or reduce an interface to vague labels such as
   "report + verdict" when exact artifacts are known.
3. **Quick start** — exact invocation, required inputs, run-root requirement, first
   expected artifact, and completion signal.
4. **Runtime scenarios** — dynamic views for the happy path, review rejection, resume,
   and test-failure/repair replay. Show ordered interactions and state transitions.
5. **Component reference** — one entry per admitted skill: responsibility,
   preconditions, reads, writes, postconditions, dependencies, required/optional status,
   downstream consumer, failure owner, and link to `SKILL.md`.
6. **Artifact and state model** — one artifact-flow view plus a reference table for
   shared files, schemas, writers, readers, mutability, and terminal states.
7. **Failure recovery** — symptom → failed gate → owner → restart point → mandatory
   downstream replay. Write this as operational recovery guidance.
8. **Requirements and constraints** — runtime, tools, installation, permissions,
   network behavior, dependencies, and explicit exclusions.
9. **Quality and evidence** — component tests, family integration, documentation
   validation, evidence dates/environments, and untested paths using §4 vocabulary.
10. **Decisions, drift, and risks** — authority ladder, consequential architecture
    decisions, source/spec divergence, known risks, and technical debt.
11. **Version and provenance** — document version, previous version, source digests,
    generator, validation receipts, and disclosures.

Use different views for different questions:

- System context: scope, actors, external systems, structural relationships, and each
  member's inspectable input/output contract with complete examples.
- Runtime scenarios: temporal interactions, gates, branches, and repair loops.
- Artifact/state model: persisted handoffs, ownership, schemas, and terminal states.

Do not reuse one generic diagram for all three questions and do not replace a required
view with prose or a component table. Every diagram must be self-describing, accessible,
and include a legend when line or color semantics are not obvious. Render with embedded
HTML/CSS or inline SVG; no external images or network dependencies.

Operational prose describes the engineered system, not the documentation session.
Use the established family name without discussing who named it. Keep naming
provenance, generator behavior, discovery history, and guide-author commentary out of
Overview, System context, Quick start, Runtime scenarios, Component reference,
Artifact and state model, Failure recovery, and Requirements and constraints. Put
material provenance only in Decisions/drift/risks or Version/provenance.

Apply a zero-slop test to every operational sentence: it must identify a use condition,
component responsibility, input, output, state transition, gate, dependency, boundary,
or failure owner. Remove throat-clearing, self-reference, rhetorical framing, and
process narration.

## 3. Evidence order when sources disagree

1. Explicit user decision for the current run.
2. Executable validators and observed current behavior.
3. Current component `SKILL.md` contracts.
4. Engineering specification.
5. Existing family prose.

A stale engineering spec is drift to disclose, not authority to obey — it must never
force the guide to misdescribe what's actually shipped. Every material claim (a
component exists, an edge exists, an invocation is safe, a dependency is required) needs
a traceable source path in the embedded model's `sources` array, or an explicit
disclosure in `assurance.disclosures` that the claim is user-supplied rather than
evidenced. Never convert absence of evidence into a fact.

## 4. Tests and evaluations

Always present, even when nothing was tested — never omit the section, and never let
absence of evidence read as "tests passed" or even "tests ran."

### Controlled status vocabulary

| Status | Meaning |
|---|---|
| `NOT_RUN` | A responsible source explicitly confirms it was not executed. |
| `NO_EVIDENCE_FOUND` | No trustworthy execution record found; whether it ran is unknown. |
| `PARTIAL` | Only some components/paths/criteria/environments were evaluated. |
| `PASS` | Evidence shows the stated scope met the stated criteria. |
| `FAIL` | Evidence shows one or more stated criteria were not met. |
| `BLOCKED` | Attempted but could not reach a valid result — name the prerequisite that failed. |
| `NOT_APPLICABLE` | A named category genuinely does not apply — record why. |

### Three layers, each with its own status

- **Component tests** — unit/schema/contract/behavior tests for individual members.
- **Family integration** — end-to-end flow, handoffs, gates, resumability, failure
  routing, shared-state behavior.
- **Documentation evaluation** — can a new caller understand, invoke, navigate, and
  recover using this guide?

A component-test pass is never presented as an integration pass. HTML validation passing
is never presented as proof the documented family works.

### Required fields per result

name + layer · scope (components/versions/paths/criteria) · method or exact command ·
execution date and environment · status (controlled vocabulary) · measured result or
findings (not just pass/fail) · evidence path or durable source reference · limitations,
exclusions, untested paths.

### Three evidence types — keep them visually distinct

1. **Observed historical evidence** already in the repository (e.g. an existing
   `evals/` result file).
2. **Tests executed during this documentation run** (you ran something while composing
   the guide).
3. **Declared but unexecuted tests** — a test *definition* exists (an `evals.json`, a
   planned fixture) but nothing has run it. This is never reported as a result.

## 5. Update and audit — the seven drift classes

The embedded model makes the file self-describing across runs. Compare current evidence
against the previous embedded model and classify:

| Group | Classes |
|---|---|
| Family shape | `MEMBERSHIP_DRIFT`, `TOPOLOGY_DRIFT` |
| Operating contract | `INTERFACE_DRIFT`, `DEPENDENCY_DRIFT` |
| Document truth | `AUTHORITY_DRIFT`, `PROSE_DRIFT`, `SOURCE_DRIFT` |

`update` writes the next slug-prefixed versioned sibling, preserves every predecessor, and
reruns all validation. `audit` reports findings to the caller without writing anything
unless explicitly asked to fix.

## 6. Failure codes

| Code | Meaning | Required response |
|---|---|---|
| `NOT_A_FAMILY` | No substantive relationship supports the proposed set. | Name the evidence reviewed; do not fabricate a family. |
| `MEMBERSHIP_AMBIGUOUS` | A consequential component boundary is unresolved. | Ask the smallest membership question needed. |
| `ENTRY_POINT_UNKNOWN` | No safe default invocation can be proven. | Request a decision, or disclose that no default exists. |
| `CONTRACT_CONFLICT` | Sources disagree on safe operation. | Present the conflict and the authority evidence. |
| `LOCATION_CONFLICT` | Canonical rule conflicts with an established convention or an occupied incompatible file. | Show the discovered paths; request the smallest placement decision. |
| `VALIDATION_FAILED` | The document or embedded model fails checks. | Repair before delivery. |
| `QA_FAILED` | Independent content QA found a blocker. | Revise, or return the precise unresolved blocker. |

## 7. Membership admission rule

Admit a component only when supported by: an orchestrator relationship, a
dependency/handoff, a common specification, a shared-state contract, or an explicit user
declaration. File-name similarity alone (e.g. a shared prefix) is never sufficient proof
by itself — it's a signal to go verify, not a conclusion.

For each admitted component, determine: job, entry conditions, inputs, outputs,
dependencies, required/optional status, downstream consumer, failure owner, evidence
path. Model edges as one of: sequence, dependency, optional gate, utility, repair route,
alternate entry — these map directly to `edges[].kind` in the embedded model schema.
For every orchestrator also populate `caller_facing_outputs`, `direct_writes`,
`delegated_outputs`, and `control_outputs`; `outputs[]` remains their concise union.
