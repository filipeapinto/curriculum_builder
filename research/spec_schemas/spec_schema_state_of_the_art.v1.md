# State of the art (Aug 2026): is there a standard schema for a "spec" artifact?

## Why this thread

`curriculum_builder` now has house schemas for two artifacts one level below
this one — the *prompt* (`schemas/prompt.schema.v1.json`/`v2.json`) and the
*plan* (`schemas/plan.schema.v1.json`). Neither schemas the artifact a plan's
own graph can name as a hard precondition: `implementation.graph.v3.yaml`
(plan 26) declares a required `source_spec` field, and plan 27's graph makes
`N00_SPEC_APPROVAL_GATE` its entry node with `BLOCKED_SPEC_NOT_APPROVED` as
an allowed result — meaning this repo already treats "spec approved" as a
gate that can block every downstream node, without ever having schemad what
"spec" itself has to contain to be approvable. Before authoring
`schemas/spec.schema.v1.json`, this checks (1) what shape this repo's own
spec artifact has already converged on by evidence, and (2) whether an
external, more authoritative schema for "spec" as an artifact distinct from
a plan already exists.

## Findings

**This repo has exactly one real spec lineage, not several independently-built
shapes — a materially weaker evidence base than the plan schema had, and this
matters for how much the new schema should assume is general.**
`plans/26_langgraph_curriculum_factory/spec/` contains
`langgraph_curriculum_factory.spec.v1.md` →
`langgraph_curriculum_factory.spec.v2.md` →
`spec/v3/langgraph_curriculum_factory.spec.v3.md` (now moved to its own
`deprecated/`) → `spec/v3/langgraph_curriculum_factory.spec.v4.md` (current,
QA-passed). No other `plans/<slug>/` directory in this repo has a `spec/`
subdirectory at all. Unlike the plan schema, which could point at three
separately-proven execution shapes across three different plans, this schema
is grounded in one document's four-revision evolution. The mitigating
evidence: the section skeleton (`0. Governing decision` through
`22. Historical regression controls`) is byte-identical in structure across
all four revisions — only content within sections changed — which is real
convergence evidence, just narrower than the plan schema had.

**The spec's own quality-gate checklist states the same non-authorization
boundary the `plan-create` skill states for plans, almost verbatim, and ties
it to a sharper three-way distinction.** §21 of `spec.v4.md` includes, as a
checked item: "The implementation phase is not performed by this
specification," and §0 states as a governing rule: "Implementation
conformance, product activation, and specification correctness are three
distinct claims and must never be merged into one verdict" (§2.0.3 expands
this). This is the direct analog of `plan.schema.v1.json`'s
`authorizes_implementation: false` — strong enough, precedent-carrying
evidence to reuse the same field name and constraint in the spec schema
rather than inventing new language.

**Specs in this repo are QA'd by a different, more adversarial mechanism than
plans: the generic `qa-gate-codex-run` skill, not `plan-create`'s
self-authored `plan_qa`/`final_audit`.** `spec/v3/QA/verdict.json` shows
`"state": "QA_PASSED"`, `"reason": "CONVERGED"`, `rounds_completed: 2`,
`max_iterations: 5`, plus a Codex `session_id`/`thread_id`/`rollout_file` —
exactly the shape `.claude/skills/qa-gate-codex-run/scripts/qa_gate.py`
produces (`qa_gate.py` lines 21–23 define the closed state set: `QA_PASSED`,
`QA_FAILED`, `QA_ERROR (Codex unreachable/unusable — inconclusive, NOT a
failure)`). `qa-gate-codex-run`'s own description states its reason for
existing: "Claude cannot QA its own work... under pressure to be finished, an
agent reviewing its own artifact reliably concludes the artifact is fine."
The skill is generic (usable on any artifact), but the evidence shows it is
what actually gates specs specifically in this repo — the spec schema's `qa`
block should bind to *this* verdict shape, not reuse the plan schema's
`APPROVED — N Critical, N High.` verdict-line pattern, which belongs to a
different skill.

**Specs carry their own falsification-style criteria IDs, distinct from a
plan's Critical/High QA findings.** `spec/spec_correction_criteria.v1.md`
defines `SPEC3-T00`–`SPEC3-T08` (e.g. `SPEC3-T00 — Historical immutability`,
verified by literal sha256 comparison against the prior version; `SPEC3-T01
— Zero literal retired-provider identifiers`, verified by a case-insensitive
grep with an explicit zero-match bar). These are falsifiable, mechanically
checkable statements in the same spirit as EARS' condition→expected shape,
but keyed to an ID namespace (`<PREFIX><version>-T<NN>`) parallel to, not
identical to, the plan schema's PREFIX-T00 test-id convention from
`plan-create`.

**Specs are held to a stricter historical-immutability rule than plans.** A
plan may be revised in place at the same version (`plan-create` Step 3); a
spec may not — `SPEC3-T00` requires that neither prior version file was
"edited, moved, or deleted," verified against a specific sha256 per file, and
every revision opens with an explicit "Supersession statement" section
naming exactly what changed and why. This is a materially different
versioning discipline and the schema should require a `supersedes` pointer
plus a supersession statement once a spec is not v1, rather than silently
allowing in-place mutation the way a plan can.

**Specs explicitly name their own unresolved items rather than silently
resolving them.** §20 of `spec.v4.md` separates "Resolved decisions" (14
enumerated, closed) from "External prerequisites before implementation
activation" and tracks exactly one open item by a stable ID,
`USER_DECISION_REQUIRED-01`, which the quality-gate checklist calls out by
name as the one thing "left open... named precisely rather than silently
resolved by inventing a mapping." No other convention already schemad in
this repo (prompt or plan) has an equivalent "explicitly-named-open-item"
requirement; it is worth carrying into the spec schema as its own field
rather than folding it into free prose, precisely because the failure mode
it guards against (quietly inventing an answer instead of naming the gap) is
exactly what a schema-checked required field can catch and prose can't.

**Top-level `specs/` (e.g. `specs/graph_based_system_documentation/`) is a
different, unrelated genre and must not be conflated with this artifact.**
Every file under `specs/graph_based_system_documentation/` is an `.html`
page-design document, and all six versions currently in the tree sit under
`deprecated/`. This is a documentation-page design spec (what a rendered
system-documentation page should look like), not an engineering
requirements/architecture spec that gates implementation. The word "spec" is
overloaded across exactly two unrelated meanings in this repo; this schema
targets only the `plans/<slug>/spec/*.md` genre — the one with a QA gate, an
approval node, and a `source_spec` consumer in a graph.

**External precedent (already fetched and verified by
`research/prompt_schemas/prompt_schema_state_of_the_art.v1.md`, re-read here
for the spec-document phase specifically rather than re-fetched): Spec Kit's
`spec.md` phase is requirements/user-stories, checked with EARS, and has no
published schema, extending the same "structure by convention" finding from
plan.md to spec.md specifically.** The prompt research doc states Spec Kit's
four-phase loop produces "`spec.md` (requirements/user stories), `plan.md`
(technical strategy), `tasks.md` (work items), and a project
`constitution.md`," uses EARS ("WHEN [condition/event], THE SYSTEM SHALL
[expected behavior]") to keep individual requirement statements checkable,
and states directly that fetching the Spec Kit repository "found no
published JSON/YAML schema validating `spec.md`/`plan.md`/`tasks.md`." This
confirms the same gap one layer up: no external body schemas the spec
artifact either, and EARS is the applicable precedent for how this repo's
`traceability_matrix`/checklist rows should be phrased, exactly as it already
guided `prompt.schema.v1.json`'s `test` shape.

## Conclusion

No external body schemas "spec" as this repo uses it, and this repo itself
has only one lineage to draw from — weaker grounding than the plan schema
had, so `schemas/spec.schema.v1.json` should stay conservative: (1) require
only the sections stable across all four revisions of the one real example
(governing decision, scope/non-goals, evidence-based baseline, traceability
matrix, resolved/open decisions, quality-gate checklist), not the
LangGraph-specific technical sections (§3–§18), which are domain content for
*this* spec and would overfit the schema if hardcoded — those should be a
free-form ordered list of `{heading, body}` design sections instead; (2)
reuse `authorizes_implementation: false` verbatim from the plan schema, since
the spec's own checklist states the identical non-authorization boundary;
(3) bind the `qa` block to `qa-gate-codex-run`'s actual verdict shape
(`QA_PASSED`/`QA_FAILED`/`QA_ERROR`, `rounds_completed`, `max_iterations`),
not the plan schema's Critical/High verdict-line pattern; (4) require a
named `open_decisions` field (IDs like `USER_DECISION_REQUIRED-NN`) separate
from `resolved_decisions`, since this repo's own evidence shows that
distinction catching a real failure mode; (5) require `supersedes` and a
supersession statement once `version > 1`, per the stricter immutability
rule §SPEC3-T00 enforces that plans do not have.

## Sources (fetched and verified)

- This repository, inspected directly:
  `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md`,
  `.../spec/langgraph_curriculum_factory.spec.v2.md`,
  `.../spec/v3/deprecated/langgraph_curriculum_factory.spec.v3.md`,
  `.../spec/v3/langgraph_curriculum_factory.spec.v4.md`,
  `.../spec/spec_correction_criteria.v1.md`,
  `.../spec/v3/spec_v3_correction_criteria.v1.md`, `.../spec/QA/verdict.json`,
  `.../spec/v3/QA/verdict.json`,
  `plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml`
  and `v2.yaml`, `plans/26_langgraph_curriculum_factory/implementation.graph.schema.v3.json`,
  `.claude/skills/qa-gate-codex-run/SKILL.md` and
  `.claude/skills/qa-gate-codex-run/scripts/qa_gate.py`,
  `specs/graph_based_system_documentation/deprecated/*.html`.
- `research/prompt_schemas/prompt_schema_state_of_the_art.v1.md` (this
  repo's own prior research, re-read for its Spec Kit findings rather than
  re-fetched — its own Sources section lists the original fetches: GitHub
  `github/spec-kit`, thebcms.com's SDD guide, and the EARS sources).

## Discarded

- Re-fetching Spec Kit / EARS sources directly was considered and skipped:
  `research/prompt_schemas/prompt_schema_state_of_the_art.v1.md` already
  fetched and verified them in the same repo, days before this document, and
  the passage needed (the `spec.md` phase specifically) is present verbatim
  in that document. Re-fetching identical claims would not have changed the
  finding and this document says so rather than presenting it as a fresh
  fetch.
- IEEE 830 / ISO 29148 (classic software-requirements-specification
  standards) were considered but not cited: they schema natural-language
  requirements documents in general, not an artifact with a QA-gate,
  approval-node, and graph-consumer relationship the way this repo's spec is
  actually used; citing them would have implied a precedent for this
  specific shape that doesn't exist.
