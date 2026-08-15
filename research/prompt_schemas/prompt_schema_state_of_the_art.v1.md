# State of the art (Aug 2026): is there a standard schema for GOAL/TEST/LOOP prompts?

## Why this thread

`curriculum_builder` already writes execution prompts in a house
GOAL/TESTS/LOOP shape (e.g.
`prompts/rebrand_system/rebrand_curriculum_factory.prompt.v1.md`), and a
PreToolUse hook (`.claude/hooks/check_prompt_governance.sh`) already gates
writes to every `*.prompt(.v<N>)?.md` file — today only for one rule
(subagent cost governance). Before authoring a JSON Schema to make that hook
also enforce "must have a GOAL, at least one TEST, and a LOOP," this checks
whether an external, more authoritative schema for this artifact class
already exists as of August 2026, so the house schema is informed by
convention rather than invented from nothing.

## Findings

**The field independently converged on the same three-part shape in June
2026, under the name "loop engineering," which validates GOAL/TEST/LOOP as
a real pattern rather than a house idiosyncrasy.** Addy Osmani's essay
(followed the same week by Peter Steinberger compressing it to "stop
prompting your agents and start designing the loops that prompt them")
defines a loop specification as "a trigger, a goal, a verification step, a
stopping rule and a memory, that a human hands to an agent harness … so the
agent pursues a goal on its own, in place of step-by-step prompting." The
companion arXiv paper "Stop Hand-Holding Your Coding Agent" (arXiv
2607.00038) frames the same requirement as "a clear goal with a testable
termination condition," "explicit success and failure exits," and a tool
set that touches the real environment (files, terminal, test runners). Read
against this repo's convention: GOAL = goal, TESTS = verification step
(made testable/terminating), LOOP = the trigger/stopping-rule/memory
machinery. Neither source publishes a machine-checkable schema for this —
both describe it in prose — so this is convergent validation of the
*shape*, not a schema to adopt wholesale.

**AGENTS.md, the closest thing to a widely-adopted standard for
agent-facing repo documents, deliberately has no required schema, which is
evidence against over-formalizing this artifact class rather than for it.**
AGENTS.md is described as "an open, vendor-neutral Markdown format" that is
"plain Markdown with no required fields," with only recommended sections
(overview, build/test commands, code style, testing, security, commit/PR
rules) and 60k+ repos using it without a shared enforced structure. This is
a different genre from a per-task execution prompt (AGENTS.md is
project-level standing context, GOAL/TEST/LOOP is a one-shot task
contract), so it doesn't directly transfer, but it does establish that the
2026 default for markdown agent artifacts is "structure by convention," not
"structure by schema."

**Spec-driven development (GitHub Spec Kit and equivalents — Kiro,
OpenSpec, BMAD) is the closest workflow analog to a GOAL/TEST/LOOP prompt,
and it separates "testable requirement" from "plan" as two different
documents, using EARS notation specifically to make individual requirement
statements checkable.** Spec Kit's four-phase loop produces `spec.md`
(requirements/user stories), `plan.md` (technical strategy), `tasks.md`
(work items), and a project `constitution.md`; "every major SDD framework …
converges on the same four-phase loop." EARS ("Easy Approach to
Requirements Syntax," Mavin, Rolls-Royce) supplies the sentence pattern
used to keep acceptance criteria unambiguous: "WHEN [condition/event], THE
SYSTEM SHALL [expected behavior]." This is directly relevant to how this
repo's TESTS section should be phrased (an executable condition and an
expected, checkable result — which is already the convention `TESTS`
sections in this repo follow, e.g. exit-code and grep-count assertions).
Fetching the Spec Kit repository directly found no published JSON/YAML
schema validating `spec.md`/`plan.md`/`tasks.md` — the templates that
generate them live under `.specify/templates/` as markdown, not as a
schema-checked contract, which is the same "structure by convention, not by
schema" pattern AGENTS.md shows.

**A real, formally schema-validated prompt file format does exist —
Prompty (Microsoft, contributed toward a Linux Foundation project) — but it
schemas a different artifact: an LLM inference template, not an agentic
task-execution contract.** A `.prompty` file is YAML frontmatter (name,
description, model configuration, declared `inputs`/`outputs`) plus a
markdown template body with role markers; the frontmatter is what gets
validated. This is the strongest evidence that *a schema for a class of
prompt file is a normal, adopted thing to build* — but Prompty's schema
covers "what variables does this template take and what model do I call it
with," not "does this task prompt have a goal, a way to verify success, and
a stopping condition." It's a precedent for the mechanism (frontmatter/
structure validated by a JSON Schema, gated by tooling), not a template to
copy for this repo's genre.

## Conclusion

No external body publishes a schema for GOAL/TEST/LOOP-shaped agentic task
prompts specifically — this repo's convention already matches where the
field converged in 2026 (a loop specification's goal + verification +
stopping condition), and the two workflows that come closest (AGENTS.md,
Spec Kit) both deliberately leave their markdown artifacts schema-free. The
house schema built from this research should therefore: (1) require the
three sections this repo already uses (GOAL, TESTS, LOOP), matching the
loop-engineering convergence; (2) require each TEST to state an executable
check and an expected/checkable result, in the spirit of EARS'
condition → expected-behavior shape; (3) require LOOP to state an explicit
stopping condition, per the "testable termination condition" requirement
loop engineering treats as load-bearing; and (4) take Prompty as precedent
that frontmatter-style, hook-validated schema enforcement on a markdown
prompt file is a normal, already-adopted pattern — not that its specific
fields (model/inputs/outputs) apply here.

## Sources (fetched and verified)

- Addy Osmani / Peter Steinberger, "Loop Engineering" (June 2026), as
  summarized in Tosea.ai, "What Is Loop Engineering? A Complete Guide from
  Prompt to Harness Engineering (2026)" —
  https://tosea.ai/blog/loop-engineering-ai-agents-complete-guide-2026
- "Stop Hand-Holding Your Coding Agent: Engineering the Loops that Replace
  Step-by-Step Prompting," arXiv:2607.00038 —
  https://arxiv.org/abs/2607.00038
- morphllm.com, "AGENTS.md Spec (2026): Recommended Sections + AGENTS.md vs
  CLAUDE.md vs .cursorrules" (search-result summary; direct fetch returned
  HTTP 429) — https://www.morphllm.com/agents-md-guide
- codersera.com, "AGENTS.md Complete Guide 2026: Spec, Tools, Examples" —
  https://codersera.com/blog/agents-md-complete-guide-2026/
- GitHub, `github/spec-kit` repository (fetched directly) —
  https://github.com/github/spec-kit
- thebcms.com, "Spec-Driven Development (SDD): The Definitive 2026 Guide" —
  https://www.thebcms.com/blog/spec-driven-development/
- Joshua McDonald, "EARS, Fifteen Years On: The Requirements Format Built
  for the Agent Era" —
  https://joshmcdonald.medium.com/ears-fifteen-years-on-the-requirements-format-built-for-the-agent-era-0f78f8ff35a0
- Wikipedia, "Easy Approach to Requirements Syntax" —
  https://en.wikipedia.org/wiki/Easy_Approach_to_Requirements_Syntax
- Prompty.ai, "The .prompty File Format" —
  https://prompty.ai/core-concepts/file-format/
- Prompty.ai, "Prompty Specification" —
  https://prompty.ai/docs/prompty-specification
- GitHub, `microsoft/prompty` —
  https://github.com/microsoft/prompty

## Discarded

- DSPy "Signature" objects (typed input/output field declarations for
  programmatic prompt optimization) were considered as another example of a
  schema'd prompt artifact, but were not cited above: DSPy signatures
  schema the *data contract* of a prompt used inside a Python program, not
  a human-authored, agent-executed task document, which is a different
  enough genre from GOAL/TEST/LOOP that citing it would overstate the
  analogy.
- The GitHub `spec-kit` fetch was checked specifically for a formal
  JSON/YAML schema validating `spec.md`/`plan.md`/`tasks.md`; none was
  found in the fetched content (the repo points to markdown templates under
  `.specify/templates/`, not a schema file), so the finding above states
  the absence rather than citing a schema that doesn't exist.
