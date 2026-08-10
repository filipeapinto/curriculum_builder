# Phase 4 Prompt — Skill-Creator Agent (build `llm_learning_agents`)

You are building a reusable Claude Code skill inside the `curriculum_builder`
repo, as Phase 4 (the final phase) of the `sota_agents_pipeline` plan
(`plans/sota_agents_pipeline/sota_agents_pipeline.plan.v2.md`). You have a
clean context window — do not assume any prior conversation. Everything you
need is on disk at the paths below.

## What earlier phases already produced (read these, do not redo their work)

- `docs/research/sota_agents_research/sota_agents.v1.json` — Phase 1's array
  of recommended reviewer agents for this repo's curriculum pipeline. Each
  entry has `agent, function, what_makes_it_sota,
  role_in_curriculum_builder, issues_resolved, sources[]`.
- `.claude/skills/llm_driven_learning/skill_creation_action_log.jsonl` —
  Phase 2's record of how it built the sibling skill `llm_driven_learning`
  (the research-methodology skill). Read this for precedent on how a
  skill-creator-built skill in this repo is structured and logged — you are
  building `llm_learning_agents`, a different skill with a different job.
- `.claude/skills/llm_driven_learning/evals/results/variance_report.md` —
  Phase 3's assessment of `llm_driven_learning`. Relevant to you only insofar
  as it shows what "fit to use" looks like for a skill built this way in
  this repo; it is not about the skill you are building.

## Task

Use the `skill-creator` skill (invoke it via the Skill tool, name
`skill-creator:skill-creator`) to build a new skill at
`.claude/skills/llm_learning_agents/`.

This skill is **not** another research scan and does not run web searches.
It is a **factory**: given one entry from a `sota_agents.v<N>.json`-shaped
array (the schema Phase 1 produces and `llm_driven_learning` reproduces on
re-run), it creates the actual reviewer agent that entry describes, so that
every agent added to this repo's curriculum-review pipeline is created the
same way instead of each being hand-rolled differently.

Concretely, the skill should turn one recommendation object into a working
agent definition, deriving from the object's own fields:
- `agent` / `function` → the agent's name and core responsibility
- `role_in_curriculum_builder` → where in this repo's pipeline it plugs in
  (read enough of `runtime/` — e.g. `runtime/controller.py`,
  `runtime/checks.py`, `runtime/gemini.py` — and `policy/limits.v1.yaml` to
  understand this repo's actual agent/check conventions, so the factory
  produces something that fits the existing pipeline rather than a generic
  template)
- `issues_resolved` → what the new agent's pass/fail verdict should be
  checking for, concretely
- `what_makes_it_sota` / `sources` → carried into the agent's own
  documentation as provenance for why it exists, not re-verified (Phase 1
  and the `llm_driven_learning` skill already own source verification; this
  skill consumes already-verified recommendations, it does not re-research
  them)

Decide and document, as part of the skill's instructions, what concrete
artifact "creating an agent" means in this repo (e.g. a runtime check
function, a prompt template, a review-agent config, wherever this repo's
existing conventions point) — ground this in what you find in `runtime/` and
`policy/`, not in a generic notion of "agent."

Follow whatever skill-creator's standard workflow requires (SKILL.md,
supporting files, evals, etc.) — do not skip steps to save time. If the
workflow calls for eval execution or description optimization that needs an
interactive session you don't have (as Phase 2 found for
`llm_driven_learning`), defer those explicitly in your log rather than
skipping them silently — this is the last phase of the plan, so also record
that deferral clearly in your final summary since no later phase will pick
it up automatically.

## Output

- `.claude/skills/llm_learning_agents/SKILL.md` and any other files
  skill-creator's standard workflow produces.
- `.claude/skills/llm_learning_agents/action_log.jsonl` — log every action
  you take (files read, skill-creator steps followed, files written), one
  JSON object per line, in the order taken. This is a faithful record, not a
  summary.

## Done when

Confirm both of these exist and are non-empty:
- `.claude/skills/llm_learning_agents/SKILL.md`
- `.claude/skills/llm_learning_agents/action_log.jsonl`
</content>
