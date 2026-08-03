# Phase 3 Prompt — Eval Runner Agent (assess `llm_driven_learning`)

You are one of several eval-runner agents assessing the `llm_driven_learning`
Claude Code skill, as part of Phase 3 of the `sota_agents_pipeline` plan
(`plans/sota_agents_pipeline/sota_agents_pipeline.plan.v2.md`). You have a
clean context window and no memory of any prior conversation — everything
you need is on disk or given to you directly in your task assignment.

You will be told, in your task assignment, a single **eval id** (1, 2, or 3).
Run only that eval. Other agents are running the other evals in parallel;
do not touch their workspaces or output directories.

## Setup

Read `.claude/skills/llm_driven_learning/evals/evals.json`. Find the eval
object matching your assigned id. It gives you:
- `prompt` — the exact user request to act on
- `expected_output` — a prose description of what a good response looks like
- `expectations` — a checklist you will grade against afterward

Read `.claude/skills/llm_driven_learning/SKILL.md` and everything it
references (`references/*.md`, `assets/*`, `scripts/*`) so you understand the
skill you're testing.

## Step 1 — Act as the user's assistant, invoking the skill

Treat the eval's `prompt` field as if a real user said it to you directly.
Respond to it for real: invoke the `llm_driven_learning` skill (Skill tool)
and follow it faithfully, exactly as the skill instructs — including
whatever output directory the prompt asks for. Do not shortcut, mock, or
pre-fill the scan; this is a live test of whether the skill produces good
results when actually run, including live web research and source
verification.

## Step 2 — Grade the result

After the skill run completes, grade it against every item in this eval's
`expectations` array, plus:

```bash
python3 .claude/skills/llm_driven_learning/scripts/validate_outputs.py <output-dir>
```

For each expectation, record pass/fail and a one-line reason citing specific
evidence (a log line, a file path, a quoted fragment) — not just "looks
fine". Be a skeptical grader: the point of this eval is to catch cases where
the skill's methodology or the agent following it cut a corner, not to
confirm the skill worked.

## Step 3 — Write your results

Write `.claude/skills/llm_driven_learning/evals/results/eval_<id>_result.json`:

```json
{
  "eval_id": <id>,
  "prompt_summary": "one line",
  "output_dir": "path the skill actually wrote to",
  "validator_exit_code": 0,
  "expectations": [
    {"expectation": "...", "pass": true, "evidence": "..."}
  ],
  "overall_pass": true,
  "notes": "anything a variance-report reader across all 3 evals needs to know"
}
```

## Step 4 — Log and signal done

Log every action (skill invocation, searches, fetches, grading judgements,
files written) to
`.claude/skills/llm_driven_learning/evals/workspaces/eval_<id>/action_log.jsonl`,
one JSON object per line, in the order taken — a faithful record, not a
summary written afterward.

As your final line in that log, write exactly:
```json
{"status": "done", "eval_id": <id>, "overall_pass": true_or_false, "result_path": ".claude/skills/llm_driven_learning/evals/results/eval_<id>_result.json"}
```
The orchestrator polls for this line to know you've finished — do not write
it until every other step above is actually complete.

## Output

- `.claude/skills/llm_driven_learning/evals/results/eval_<id>_result.json`
- `.claude/skills/llm_driven_learning/evals/workspaces/eval_<id>/action_log.jsonl`
  (ending in the `status: done` line)
- Whatever output directory the eval prompt itself specified (e.g.
  `docs/research/sota_scan_test/`) — this is the skill's real output, leave
  it in place for inspection.
</content>
