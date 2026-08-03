# Phase 3 Prompt — Variance Report Agent

You are finishing Phase 3 of the `sota_agents_pipeline` plan
(`plans/sota_agents_pipeline/sota_agents_pipeline.plan.v2.md`), after three
eval-runner agents have each independently run the `llm_driven_learning`
skill against one eval prompt from
`.claude/skills/llm_driven_learning/evals/evals.json` and graded it. You have
a clean context window — everything you need is on disk.

## Input

Read only these small files (do not re-read the full research output each
eval produced — that would blow your context for no benefit):
- `.claude/skills/llm_driven_learning/evals/results/eval_1_result.json`
- `.claude/skills/llm_driven_learning/evals/results/eval_2_result.json`
- `.claude/skills/llm_driven_learning/evals/results/eval_3_result.json`

If any of these is missing or has no `overall_pass` field, treat that eval as
unresolved and say so explicitly rather than guessing at its outcome.

## Task

Write
`.claude/skills/llm_driven_learning/evals/results/variance_report.md`
covering:

1. **Pass/fail summary** — per eval, overall pass/fail and which specific
   expectations failed, if any.
2. **Variance across runs** — since each eval invocation does live web
   research, results are not expected to be byte-identical. Call out where
   the *methodology* held steady across the three runs (grounding before
   searching, fetch-before-cite, output contract shape) versus where it
   didn't — methodology drift is the actual finding; differing papers/URLs
   chosen per run is not.
3. **Recurring failure modes** — if the same expectation failed in more than
   one eval, name it explicitly; that is a skill-instruction gap, not a
   one-off.
4. **Verdict** — is `llm_driven_learning` fit to use as-is, fit with a named
   fix, or not fit? Be concrete about what a fix would target if not "fit
   as-is".

## Output

- `.claude/skills/llm_driven_learning/evals/results/variance_report.md`
- `.claude/skills/llm_driven_learning/evals/action_log.jsonl` — log your
  reads and the report write, ending with:
  `{"status": "done", "report_path": ".claude/skills/llm_driven_learning/evals/results/variance_report.md"}`
</content>
