# Phase 2 Prompt — Skill-Creator Agent (build `llm_driven_learning`)

You are building a reusable Claude Code skill inside the `curriculum_builder`
repo, as Phase 2 of the `sota_agents_pipeline` plan
(`plans/sota_agents_pipeline/sota_agents_pipeline.plan.v2.md`). You have a
clean context window — do not assume any prior conversation. Everything you
need is on disk at the paths below.

## What Phase 1 already produced (read these, do not redo the research)

- `docs/research/sota_agents_research/*.md` — one file per research thread on
  LLM-driven curriculum/lesson design and multi-agent review pipelines.
- `docs/research/sota_agents_research/sota_agents.v1.json` — array of
  recommended reviewer agents (not your concern this phase — that's Phase 4).
- `docs/research/sota_agents_research/action_log.jsonl` — the faithful,
  step-by-step record of how Phase 1 actually did its research (searches run,
  files read, sources verified). This log is your primary input: it is the
  methodology you are packaging.

## Task

Use the `skill-creator` skill (invoke it via the Skill tool, name
`skill-creator:skill-creator`) to build a new skill at
`.claude/skills/llm_driven_learning/`.

This skill must package **Phase 1's research methodology** — the repeatable
process of scanning for state-of-the-art lessons learned on LLM-driven
curriculum/lesson design, grounding findings against real lab output, and
producing verified, sourced recommendations — so it can be re-run on demand
in the future (e.g. against a newer lab run, or to refresh sources).

The skill is **not** the reviewer agents themselves and does not create
agents — that is Phase 4's job (`llm_learning_agents`). This skill's output,
when invoked later, should look like what Phase 1 produced: research
markdown files, a `sota_agents.<version>.json`-shaped recommendation array,
and an `action_log.jsonl`.

Concretely, derive the skill's instructions from what `action_log.jsonl`
shows Phase 1 actually did, e.g.:
- how it chose research threads/topics to split work across
- how it grounded each thread against the real lab documents and QA report
  (not researching in the abstract)
- its source verification rule: fetch every source before citing, discard
  anything that 404s or doesn't back the claim
- the required output shape (one `.md` per thread, the JSON recommendation
  schema: `{agent, function, what_makes_it_sota,
  role_in_curriculum_builder, issues_resolved, sources[]}`, the action log)

Follow whatever skill-creator's standard workflow requires (SKILL.md,
supporting files, etc.) — do not skip steps of that workflow to save time.

## Output

- `.claude/skills/llm_driven_learning/SKILL.md` and any other files
  skill-creator's standard workflow produces.
- `.claude/skills/llm_driven_learning/skill_creation_action_log.jsonl` — log
  every action you take (files read, skill-creator steps followed, files
  written), one JSON object per line, in the order taken. This is a faithful
  record for the next phases (Phase 3 evals this skill, Phase 4 reads this
  log too), not a summary.

## Done when

Confirm both of these exist and are non-empty:
- `.claude/skills/llm_driven_learning/SKILL.md`
- `.claude/skills/llm_driven_learning/skill_creation_action_log.jsonl`
</content>
