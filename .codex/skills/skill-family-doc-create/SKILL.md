---
name: skill-family-doc-create
description: >-
  Read a coordinated family of skills and produce exactly one standalone HTML
  family guide explaining what the family is, how to start it, how components
  connect and hand off, what comes out, how failures route, and whether the
  guide can be trusted. Use when documenting a skill family, explaining how a
  prefixed or orchestrated multi-skill pipeline fits together, creating a
  caller-facing family guide, updating a guide after component changes, or
  auditing an existing guide for drift. This is a documentation skill; it does
  not rename, move, or repackage the skills it documents.
---

# skill-family-doc-create: one trustworthy guide, not seven summaries

## What this produces

Two persistent deliverables are maintained: the family's standalone, slug-prefixed,
versioned HTML guide at the canonical path (section 1 below), and the agent-facing version index at
`<docs-root>/skill-families/index.md`. No companion README or YAML file
ships alongside a family guide — the guide's machine-readable half lives *inside* the HTML, in a
`<script type="application/json" id="family-model">` block, so a future `update` or
`audit` run has something to compare against without you having to manage a second
file. The full normative contract for what that HTML must contain is in
`references/document-contract.md`; read it before composing, not just before
validating.

Why one file and not the family's existing scattered docs: every additional
documentation artifact is another thing that can go stale relative to the code. A
caller who finds this file should never have to also go find its sidecar to trust it.

## Before you touch a template: read the family's own evidence

Do not start by imagining what the family probably does. Skills drift from their
specs, specs drift from history, and the file-name pattern that made you think "family"
might be coincidence. Ground everything in `references/document-contract.md` §3
(evidence order) and §7 (membership admission) before you write a sentence of prose.

## Invocation

```
Family source: <family directory, specification, or explicit skill paths>
Mode: create | update | audit
Optional evidence: <additional paths>
Optional focus: <audience or operational concern>
Optional output override: <explicit .html path>
```

`Family source` is mandatory — you do not go looking for a family to document
unimplied. `Mode` may be supplied, but normally infer it from the resolved canonical
path: no guide means `create`; a valid guide means `update`; an explicit request to
inspect without changing files means `audit`. Output location is resolved per §1 below
and must be reported to the caller before you write anything. You document the family
that exists; you have no packaging concept and never move or repackage its components.

- `create` — first family document; set `assurance.version` to `1` and write
  `<family-slug>-guide.v1.html`.
- `update` — revise an existing guide against current evidence, detect drift
  (references/document-contract.md §5), and write `<family-slug>-guide.vN+1.html`,
  where `N` comes from the highest valid versioned guide's embedded
  `assurance.version`. Never overwrite the predecessor.
- `audit` — inspect an existing guide, report currency, mutate nothing unless the
  caller explicitly asks for a fix.

## Workflow

Six stages. Do not skip validation because the earlier stages felt thorough — the
scripts catch classes of error a careful read does not.

### Stage 1 — Discover

Run `scripts/inspect_family.py` against every candidate component path (skill
directories, an orchestrator file, the governing specification, shared-state
directories). It gives you file digests, `SKILL.md` frontmatter, and a list of
kebab-case identifiers each `SKILL.md` textually mentions — a *signal* to chase, never
proof of membership on its own. Also read: orchestrators, specs, validators, scripts,
tests, `evals/`, CI config, any existing prose, and repository documentation
conventions (check whether `work-lib/docs/skill-families/` already has siblings whose
pattern you should match). Keep discovery scratch data in your run workspace; nothing
from it ships in the deliverable location except what you deliberately embed in the
model.

Resolve version state before composing. Folder existence alone is not a version
signal. Discover files matching `<family-slug>-guide.v*.html`, parse their embedded
models, validate schema and filename/version integrity, and select the highest embedded
`assurance.version` as `N`. Use update mode with version `N+1`. Source digest
changes are expected update evidence: classify them as `SOURCE_DRIFT`; they do not
invalidate lineage. If none exists, create version 1. If the highest numbered candidate
has an invalid/missing model, a filename/version mismatch, or a duplicate version, stop
with `LOCATION_CONFLICT`; never guess from filenames alone.

### Stage 2 — Reconstruct membership and topology

Admit a component only under `document-contract.md` §7's rule. For each admitted
component, record job / entry conditions / inputs / outputs / dependencies /
required-or-optional / downstream consumer / failure owner / evidence path — this is
exactly the `components[]` shape in `references/embedded-family-model.schema.json`.
Model every relationship as one `edges[].kind`: `sequence`, `dependency`,
`optional_gate`, `utility`, `repair_route`, or `alternate_entry`. Decide the default
entry point and its proof status (`proven` / `declared` / `unknown`) — never mark it
`proven` without an executable or observed basis.

### Stage 3 — Resolve conflicts

Ask only about ambiguities that would change membership, the default entry point,
topology, authority, or safe invocation. Do not interrupt for wording. If a
conflict can't be asked away and blocks progress, use the matching failure code
(section below) instead of guessing a diagram into existence.

### Stage 4 — Compose

Write for someone deciding whether and how to use this family, not for someone who
already knows it. Copy `assets/family-guide.template.html` to the resolved
slug-prefixed versioned path and fill it in — see the template's own header comment for the fill order (prose
sections first, embedded model last, so the model reflects what the prose actually
ended up saying rather than a plan you deviated from while writing). Link out to
component `SKILL.md` files for procedural depth instead of duplicating their content.
Compose the guide as four clearly separated documentation modes:

1. Discovery: Overview and System context.
2. Goal-oriented operation: Quick start, Runtime scenarios, Failure recovery.
3. Technical reference: Component reference, Artifact and state model, Requirements.
4. Trust and maintenance: Quality and evidence, Decisions/drift/risks, Version/provenance.

Follow `document-contract.md` §2 exactly. Use a context view for scope and structural
relationships, dynamic views for execution/branch/repair behavior, and an artifact-flow
view for persisted handoffs. Each view must answer a different engineering question.
Do not substitute a table for a required visualization or repeat one generic diagram
under multiple headings.

Treat the primary System context diagram as an interface map, not a directory map.
Every admitted skill must appear under its full skill identifier and show, inside or
immediately attached to its node: one-line responsibility, explicit input artifact(s),
explicit output artifact(s), and a complete realistic example that populates every
declared required and optional input category plus every output category. Mark omitted
optional values explicitly; never disguise them as unavailable categories. Never shorten identifiers (for example, do not render `graph-doc-grill` as
`goal-define`) and never use vague interface labels such as "report + verdict" or
"prompts + manifest" when exact filenames or patterns are known. If the resulting
diagram would be unreadable in one row, use a vertical pipeline, lanes, or stacked
interface cards; readability takes priority over compactness. The Component reference
must expand the same contracts without contradicting or introducing interfaces absent
from the diagram.

Copy interfaces from explicit component contracts before interpreting prose. Separate
caller inputs, gate preconditions, fixed dependencies, and produced artifacts; do not
collapse them into one list. A verdict that the orchestrator checks before dispatch is
not automatically an input read by the dispatched skill. A companion artifact written
by a dependency must be labeled with its actual writer. When a component exposes two
entry points, show two interfaces rather than synthesizing one fictional call.

For every orchestrator, document four output layers separately: **caller-facing
result** (what invoking the orchestrator ultimately produces), **direct writes**,
**delegated outputs with their owning writers**, and **control outputs**. Never infer
that “not the direct writer” means “not an orchestrator output.” Populate the embedded
component fields `caller_facing_outputs`, `direct_writes`, `delegated_outputs`, and
`control_outputs`; keep legacy `outputs[]` as a concise union for compatibility.

Write the operational sections as an engineering system description. State the
family's purpose, lifecycle, component responsibilities, interfaces, artifacts, gates,
dependencies, and failure ownership directly. Do not narrate how the family was named,
how the guide was produced, what the generator noticed, or what "this guide" believes.
If naming provenance materially matters, record it only in Version and provenance. A shared prefix
is membership evidence only after §7 admission.

Delete any sentence that does not help the reader decide one of: when to use the
family, which component runs, what crosses a boundary, what gate must pass, what output
appears, or who repairs a failure. Prefer concrete nouns, paths, commands, and state
transitions over commentary about the documentation process.

Compose the **tests and evaluations** section from real evidence, using the controlled
status vocabulary in `document-contract.md` §4 — this is required even when the answer
for every layer is `NOT_RUN` or `NO_EVIDENCE_FOUND`. Never let a missing test read as a
passed one.

Record generator provenance separately from family provenance. In every new or updated
guide set `assurance.generator.agent` to the executing agent (`codex` for this Codex
implementation), `assurance.generator.skill` to `skill-family-doc-create`, and
`assurance.generator.implementation` to the skill path used. A Codex-generated guide
may document `.claude/skills/`, and a Claude-generated guide may document
`.codex/skills/`; do not confuse generator with source.

### Stage 5 — Render

The output must open with no network access: embedded CSS (already in the template),
no external `<script src>`/`<link rel=stylesheet>`/remote images. Keep the nav,
heading hierarchy, and table structure the template establishes — they are what the
validators in stage 6 check.

### Stage 6 — Validate and inspect

Run, in order, against the finished file:

```
python3 scripts/inspect_family.py <component paths...>        # re-confirm nothing drifted mid-write
python3 scripts/validate_embedded_model.py <output.html> --repo-root <repo-root>
python3 scripts/validate_family_html.py <output.html>
python3 scripts/update_family_index.py <docs-root>/skill-families
```

Both validators exit non-zero and print a JSON error report on failure — treat every
line in that report as something to fix, not a false alarm; they check objective facts
(schema conformance, digest drift, missing sections, broken in-page links, component
coverage, controlled-vocabulary compliance), never prose quality. Then actually render
the HTML (open it, or use a headless renderer) and look at it — a file that validates
structurally can still be visually broken. Finally, get independent content QA against
`references/document-contract.md` before calling the document done; a self-review does
not count. Only a passing file gets delivered — on failure, use `VALIDATION_FAILED` or
`QA_FAILED` below rather than shipping with known defects. In `audit` mode, do not run
the index updater because audit is read-only. In create/update mode, run it only after
the family guide passes both validators, then report both the guide and index paths.

## Canonical location

| Repository context | Canonical current document |
|---|---|
| Repo has `work-lib/` | `<repo-root>/work-lib/docs/skill-families/<family-slug>/<family-slug>-guide.vN.html` |
| Repo has no `work-lib/` | `<repo-root>/docs/skill-families/<family-slug>/<family-slug>-guide.vN.html` |
| User-approved override | The exact supplied `.html` path |

The shared index is always `<docs-root>/skill-families/index.md`. It contains only each
family slug, current version, and generator type (`claude` or `codex`).

Full slug rules and the "never inside a component's own folder, never inside the
engineering-spec directory" rule are in
`references/document-contract.md` §1. Report the resolved path to the caller before
you write.

## Failure codes

| Code | When | Do |
|---|---|---|
| `NOT_A_FAMILY` | No substantive relationship supports the proposed set. | Name the evidence you reviewed; do not fabricate a family. |
| `MEMBERSHIP_AMBIGUOUS` | A consequential component boundary is unresolved. | Ask the smallest membership question needed. |
| `ENTRY_POINT_UNKNOWN` | No safe default invocation can be proven. | Request a decision, or disclose that no default exists. |
| `CONTRACT_CONFLICT` | Sources disagree on safe operation. | Present the conflict and the authority evidence (§3 evidence order). |
| `LOCATION_CONFLICT` | Canonical rule conflicts with an established repo convention or an occupied incompatible file. | Show the discovered paths; ask the smallest placement question. |
| `VALIDATION_FAILED` | The document or embedded model fails a validator check. | Repair before delivery — never deliver a failing file. |
| `QA_FAILED` | Independent content QA found a blocker. | Revise, or return the precise unresolved blocker. |

## Reference map

- `references/document-contract.md` — the full normative content contract: required
  sections, evidence order, the tests/evaluations vocabulary and layers, the seven
  drift classes, membership admission rule. Read before composing.
- `references/embedded-family-model.schema.json` — the schema the embedded model and
  `validate_embedded_model.py` both enforce.
- `assets/family-guide.template.html` — copy this, don't rebuild the CSS/layout from
  scratch.
- `scripts/inspect_family.py`, `scripts/validate_embedded_model.py`,
  `scripts/validate_family_html.py`, `scripts/update_family_index.py` — deterministic;
  run them, don't reimplement their checks by eye.
