# SOTA Agents Pipeline — Plan v2

Changes from v1: (1) Phase 3 completion is now trackable when split across
multiple eval agents, via `eval_manifest.json`; (2) Phase 3's success
criterion no longer implies exact reproduction of Phase 1's recommendations.
Everything else is unchanged from v1.

## Goal

Review the labs in `outputs/arduino_kit_run_v2/` against the state of the art
(as of Aug 2026) in LLM-driven curriculum design, and turn the findings into
two reusable skills:

- `llm_driven_learning` — repeatable skill that runs the SOTA scan itself
  (the methodology used in Phase 1, packaged so it can be re-run later).
- `llm_learning_agents` — repeatable skill that creates the agent types the
  scan recommends, giving every agent in this repo a common creation pattern.

## Constraint: one fresh agent per phase

Each phase below runs as its own agent with a clean context window. Phases
hand off through files on disk (paths listed under each phase), never through
conversation memory — the orchestrator does not re-read full file contents
between phases, only passes paths forward. Phase 3 (evals) is deliberately a
separate agent from Phase 2 (skill creation) for the same reason: cap tokens
per agent, split further into multiple eval agents if one eval task would
otherwise blow the context budget.

Hard gate: the orchestrator waits for Phase 3 to fully end before starting
Phase 4 (explicit user requirement — do not overlap these). If Phase 3 is
split into multiple eval agents, the orchestrator waits until every agent
listed in `eval_manifest.json` (see Phase 3) has a `"status": "done"` entry
in its own `action_log.jsonl` before starting Phase 4.

## Folder tree / execution order

```
curriculum_builder/
├── outputs/arduino_kit_run_v2/          # input, read-only — labs under review
│   └── {L01..L04}/document/*.md, QA/*.md
│
├── docs/research/sota_agents_research/  # Phase 1 — SOTA Research Agent [bg]
│   ├── <source-cluster>.md              # one file per research thread, e.g.
│   │                                    #   academic_lessons_learned.md,
│   │                                    #   commercial_lessons_learned.md
│   ├── sota_agents.v1.json              # recommended reviewer agents,
│   │                                    #   verified sources only
│   └── action_log.jsonl                 # → this log is the input to Phase 2
│                                          ⬇ wait for Phase 1 to finish
├── .claude/skills/llm_driven_learning/  # Phase 2 — Skill-Creator Agent [bg]
│   ├── SKILL.md                         # packages Phase 1's research
│   │                                    #   methodology as a repeatable skill
│   ├── (skill-creator standard files)
│   └── skill_creation_action_log.jsonl
│                                          ⬇ wait for Phase 2 to finish
│   └── evals/                            # Phase 3 — Eval Agent(s) [bg, separate
│       ├── eval_manifest.json            #   context from Phase 2] — lists every
│       ├── workspaces/...                #   eval agent spawned, so the
│       ├── results/variance_report.*     #   orchestrator can confirm all are
│       └── action_log.jsonl              #   done before the hard wait clears
│                                          ⏸ HARD WAIT — Phase 4 does not start
│                                             until every agent in
│                                             eval_manifest.json is done
├── .claude/skills/llm_learning_agents/   # Phase 4 — Skill-Creator Agent [bg]
│   ├── SKILL.md                         # factory for creating the agent TYPES
│   │                                    #   from sota_agents.v1.json, as the
│   │                                    #   repo's common agent-creation pattern
│   ├── (skill-creator standard files)
│   └── action_log.jsonl
```

## Phase 1 — SOTA Research Agent

**Input:** `outputs/arduino_kit_run_v2/{L01..L04}/document/*.md`,
`outputs/arduino_kit_run_v2/QA/*.md`

**Do:** Research commercial and academic sources (as of Aug 2026) on
LLM-driven curriculum design for lessons learned. Ground the research against
the actual labs to identify gaps a reviewer agent should catch. Only cite
sources you have verified are real (see prompt for verification method).

**Output:**
- `docs/research/sota_agents_research/*.md` — one file per research thread
- `docs/research/sota_agents_research/sota_agents.v1.json` — array of:
  `{agent, function, what_makes_it_sota, role_in_curriculum_builder, issues_resolved, sources[]}`
- `docs/research/sota_agents_research/action_log.jsonl` — every action taken

## Phase 2 — Skill-Creator Agent (build `llm_driven_learning`)

**Input:** `sota_agents.v1.json`, `action_log.jsonl` from Phase 1

**Do:** Use `/skill-creator` to build the `llm_driven_learning` skill. The
skill encodes Phase 1's research methodology so the SOTA scan can be re-run
on demand later — it is not the reviewer agents themselves.

**Output:** `.claude/skills/llm_driven_learning/*`,
`skill_creation_action_log.jsonl`

## Phase 3 — Eval Agent(s) (assess `llm_driven_learning`)

**Input:** `.claude/skills/llm_driven_learning/`,
`outputs/arduino_kit_run_v2/` as test fixture

**Do:** Build evals and workspaces (via skill-creator's eval tooling) to
score whether the skill reliably produces sound, sourced SOTA
recommendations — sound methodology and real, verifiable citations, not
recommendations identical to Phase 1's (live web research is not
reproducible run-to-run). Split across multiple agents if needed to keep
each agent's context small; if split, write `eval_manifest.json` listing
every spawned agent's name/id so the orchestrator can confirm all finished.

**Output:** `.claude/skills/llm_driven_learning/evals/*`,
`eval_manifest.json` (if split across agents), variance report,
`action_log.jsonl`

**Orchestrator waits here until every agent in `eval_manifest.json` (or the
single Phase 3 agent, if not split) fully ends.**

## Phase 4 — Skill-Creator Agent (build `llm_learning_agents`)

**Input:** `sota_agents.v1.json`, Phase 2 + Phase 3 `action_log.jsonl` files

**Do:** Use `/skill-creator` to build the `llm_learning_agents` skill — a
factory for creating the agent types recommended in `sota_agents.v1.json`,
so every agent in the repo is created the same way.

**Output:** `.claude/skills/llm_learning_agents/*`, `action_log.jsonl`
</content>
</invoke>
