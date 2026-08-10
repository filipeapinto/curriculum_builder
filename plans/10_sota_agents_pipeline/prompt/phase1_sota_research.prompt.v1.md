# Phase 1 Prompt — SOTA Research Agent

You are reviewing lab output from an LLM-driven curriculum generation
pipeline (`curriculum_builder`) against the state of the art in LLM-driven
curriculum design as of August 2026.

## Ground truth to review

Read the generated lab documents and QA report at:
- `outputs/arduino_kit_run_v2/L01/document/*.md` through `L04/document/*.md`
- `outputs/arduino_kit_run_v2/QA/arduino_kit_run_v2.qa_report.v1.md`

These are real pipeline outputs (Arduino kit curriculum, 4 lessons). Use them
to ground your research: what would a domain-expert reviewer, a pedagogy
reviewer, a safety reviewer, etc. actually need to catch in output like this?

## Research task

Research commercial and academic sources for lessons learned on LLM-driven
curriculum/lesson design and multi-agent review pipelines for generated
educational content. Cover both:
- **Academic**: papers on LLM-generated educational content, automated
  curriculum QA, multi-agent review/critique architectures, pedagogy
  validation.
- **Commercial**: production systems/companies doing AI-driven curriculum or
  content generation at scale, and what review/QA agent roles they use.

For each distinct research thread, write a markdown file to
`docs/research/sota_agents_research/<topic-name>.md` documenting what you
found and which source(s) it came from.

## Required JSON output

Write `docs/research/sota_agents_research/sota_agents.v1.json` — a JSON
array where each element is an agent you recommend adding to review labs
like the ones above:

```json
[
  {
    "agent": "string — name of the recommended agent",
    "function": "string — what it does",
    "what_makes_it_sota": "string — why this reflects current best practice",
    "role_in_curriculum_builder": "string — where/how it plugs into this repo's pipeline",
    "issues_resolved": "string — what gap in the L01-L04 labs / QA report this addresses",
    "sources": ["array of URLs or citations backing this recommendation"]
  }
]
```

## Logging

Log every action you take (searches run, files read, files written) to
`docs/research/sota_agents_research/action_log.jsonl`, one JSON object per
line, in the order taken. This log is the input to the next phase, which
will build a skill out of your methodology — so make it a faithful record of
the steps you actually followed, not a summary.

## Output

When done, confirm the three artifact paths exist:
- `docs/research/sota_agents_research/*.md`
- `docs/research/sota_agents_research/sota_agents.v1.json`
- `docs/research/sota_agents_research/action_log.jsonl`
