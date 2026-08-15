# State of the art (Aug 2026): restart strategies for long-running GOAL/TEST/LOOP prompts

## Why this thread

GOAL/TEST/LOOP prompts in this repo (e.g.
`prompts/rebrand_system/rebrand_curriculum_factory.prompt.v1.md`) can run
long enough to be interrupted mid-LOOP — a crash, a context limit, a
human-in-the-loop pause. `schemas/execution_log.schema.v2.json`'s
started/completed ACT pairing and its computed `unclosed_starts` field
exist specifically to make that recoverable, and
`prompts/rebrand_system/assets/run_rebrand_with_log.py` already writes a
conformant log through `runtime.logger.ExecutionLogger`. What's unclear is
whether that mechanism is actually *articulated* anywhere as a restart
procedure — nothing currently tells an agent "before you start, read the
log; here is how you tell a finished step from an interrupted one; here is
what you do about each." This checks what the state of the art (Aug 2026)
says a restart contract needs, so that gap can be closed deliberately
rather than left as an accident of the schema happening to have the right
shape.

## Findings

**A checkpoint is specifically defined as a persisted snapshot at a
known-good boundary, and its entire purpose is to make a loop restartable
without redoing finished work.** "A checkpoint is a persisted snapshot of
agent state at a known-good moment that makes loops restartable. Without
them, a crash at step 18 of a 20-step research task means starting from
zero." The same source frames the recovery unit correctly: "Splitting a run
into steps that write results to durable storage before the next one
starts lets it survive crashes: when something fails, only the step that
was in flight is lost, and the next worker resumes from the last completed
step instead of starting over" (explainx.ai / Indium.tech, 2026). This is
the exact shape `execution_log.schema.v2.json` already has — an ACT
`started` record is the "in-flight" state, an ACT `completed`/`skipped` or
an `EXEC` failure closes it — but the schema records the shape without
anywhere stating that a *new* run of a prompt must consult it first.

**The mechanism every mature runtime uses for restart detection is a
durable journal that is replayed on resume: entries already in the journal
are done and must not be re-run; entries absent are still pending.**
Temporal: "The Temporal service stores workflow event history and replays
workflow code against that history to reconstruct state after a worker
crash." Restate: "Application code records completed operations in a
journal; on recovery, Restate replays the journal and skips work already
completed." Inngest: "Each `step.run` result is persisted; if the function
re-executes, completed steps are skipped and stored results are injected."
The practical requirement each of these converges on: "Every meaningful
operation gets a `step_id`. The journal records planned action, inputs …
result receipt, retry count, and error state," and on restart "the runtime
consults this journal to determine which operations completed successfully
versus which remain pending" (Zylos Research, "Durable Execution for AI
Agent Runtimes," 2026-04-24). This is structurally identical to this repo's
`ACT`/`EXEC` pairing plus `unclosed_starts` — a started-but-unclosed ACT
*is* an in-flight step; a closed ACT *is* a completed step whose `result`
can be read instead of recomputed; an `EXEC` closing a started ACT *is* a
failed step whose `what_failed` tells the resuming run what went wrong
without re-attempting it blindly.

**Resume detection is explicit and operator-supplied, never automatic —
the runtime does not guess whether it's resuming; something has to tell
it.** LangGraph: "Resuming is a matter of passing the same `thread_id` back
to the graph … If the process died partway through, the next invocation
with the same thread finds the last checkpoint." "No automatic detection
occurs — the system operator must provide the matching thread ID. If a
fresh ID is supplied, execution starts from the beginning" (Zylos Research,
"AI Agent Workflow Checkpointing and Resumability," 2026-03-04, summarizing
LangGraph's model). Translated to this repo: the equivalent of a
`thread_id` is the log's file path (`execution/execution_log.jsonl` for a
given prompt instance). A GOAL/TEST/LOOP prompt's LOOP section needs its
own explicit first step — "check whether this log already exists and has
records" — because nothing does that check for it.

**Safe replay depends on the underlying steps being deterministic and
idempotent, not on the journal alone; only clearly-infrastructure failures
should be retried blindly.** "Design workflows to be deterministic and
idempotent, wrapping any side effects or non-deterministic operations
inside tasks that can be safely replayed" (Indium.tech, item 5). "Any tool
that writes external state … must carry an idempotency key tied to the
workflow state to prevent duplicate side effects on replay. The safest rule
is to only retry operations that raised a clear infrastructure exception
(timeout, rate limit, network error) and that you can prove are idempotent"
(search synthesis of 2026 loop-engineering sources). Concretely for this
repo: `apply_rebrand.sh`'s case-preserving phrase substitution is already
naturally idempotent — re-running it against already-rebranded text is a
no-op diff — which is exactly the property that makes it safe to re-run
unconditionally on resume rather than needing a "did I already do this"
check of its own. Not every step in a prompt will have that property by
default; it has to be designed in, or the step has to be guarded by reading
its own prior ACT record instead of re-running.

**Checkpoint placement matters: write the start record before an
irreversible or expensive action, and the completion record immediately
after, so recovery never has to guess how far a step got.** "Before
irreversible actions like sending emails or calling payment APIs,
checkpoint first so if the action fails, you can retry from the pre-action
snapshot with the same state. After expensive operations that burned
significant tokens or API calls, checkpoint immediately after to avoid
losing that work to downstream failure" (search synthesis, explainx.ai /
Indium.tech). This matches `runtime.logger.ExecutionLogger.start()`/
`.complete()`'s existing start-before/complete-after contract; the gap
again is that no GOAL/TEST/LOOP prompt currently instructs the agent to use
that pairing around its own LOOP steps rather than only around the specific
sub-steps `run_rebrand_with_log.py` happens to wrap.

## Conclusion

The state of the art doesn't require new infrastructure here —
`execution_log.schema.v2.json`'s ACT/EXEC pairing and computed
`unclosed_starts` is already the same durable-journal shape Temporal,
Restate, Inngest and LangGraph converged on for restart detection. What's
missing, matching the user's own diagnosis, is articulation: nothing in a
GOAL/TEST/LOOP prompt currently says (1) check for an existing log for this
task before starting — resume detection is never automatic, it has to be
an explicit first LOOP step; (2) read `unclosed_starts` and any records to
distinguish already-done work (skip), in-flight/interrupted work (retry
that one step, don't restart from zero), and never-attempted work (do it);
(3) only blindly retry a failed step if its `EXEC.failure_type` is
infrastructure-shaped (`tool-error`) and the step is provably idempotent —
a `wrong-output` or `bad-input` failure needs a different fix, not a
re-run; (4) place `start`/`complete` around each LOOP step itself, not only
around the sub-commands a helper script happens to wrap. This is a
specific, scoped addition to `schemas/prompt.schema.v1.json`'s `loop`
`$def` (a `resume_check` requirement) and to the prompt convention's LOOP
section — not a new mechanism, since the mechanism already exists in
`runtime/logger.py` and in the runtime's own separate `--resume`/checkpoint
contract in `meta_prompt/curriculum.prompt.v1.md`.

## Sources (fetched and verified)

- explainx.ai / Indium.tech search synthesis and Indium.tech, "7 State
  Persistence Strategies for Long-Running AI Agents in 2026" (fetched
  directly) —
  https://www.indium.tech/blog/7-state-persistence-strategies-ai-agents-2026/
- Zylos Research, "AI Agent Workflow Checkpointing and Resumability"
  (2026-03-04, fetched directly) —
  https://zylos.ai/research/2026-03-04-ai-agent-workflow-checkpointing-resumability/
- Zylos Research, "Durable Execution for AI Agent Runtimes: Checkpointing,
  Replay, and Recovery" (2026-04-24, fetched directly) —
  https://zylos.ai/research/2026-04-24-durable-execution-agent-runtimes/
- slavadubrov.github.io, "Long-Running AI Agent Runtime in 2026: Sessions,
  Sandboxes, Checkpoints, and Harnesses" —
  https://slavadubrov.github.io/blog/2026/05/26/ai-agent-runtime/
- explainx.ai, "AI Agent Loop Architecture: Triggers, Retries, Checkpoints
  2026" — https://www.explainx.ai/blog/ai-agent-loop-architecture-triggers-retries-checkpoints-2026
- Reactify Solutions, "Durable AI agents in 2026: long-running workflows
  with Temporal, Inngest, DBOS, and Restate" —
  https://www.reactify-solutions.com/articles/durable-ai-agents-2026
- Zylos Research, "Durable Execution Patterns for AI Agents: Building
  Fault-Tolerant Autonomous Systems" (2026-02-17) —
  https://zylos.ai/research/2026-02-17-durable-execution-ai-agents/

## Discarded

- "Memory in the Loop: In-Process Retrieval as Extended Working Memory for
  Language Agents" (arXiv:2607.05690) and "Remember When It Matters:
  Proactive Memory Agent for Long-Horizon Agents" (arXiv:2607.08716) were
  surfaced by search but not fetched or cited: both are about semantic/
  working-memory retrieval for conversational context, a different problem
  from crash-safe step-level restart, and citing them would conflate two
  separate "memory" concepts.
- "Externalization in LLM Agents: A Unified Review of Memory, Skills,
  Protocols and Harness Engineering" (arXiv:2604.08224) was surfaced but
  not fetched; the Zylos and Indium.tech sources already fetched covered
  the same checkpointing/idempotency ground with citable, concrete
  language, so a third overlapping source wasn't pulled in.
- Google's ADK "pause, resume, and never lose context" blog post and AWS
  Lambda Durable Functions were noted in search snippets as further
  platform examples but not fetched — they're additional instances of the
  same journal/checkpoint pattern already established by the Temporal/
  Restate/Inngest/LangGraph citations above, not a different pattern.
