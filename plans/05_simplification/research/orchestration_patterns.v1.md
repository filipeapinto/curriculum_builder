# Orchestrator + Subagent Fan-Out: What Works, What Fails, What the Evidence Says

Research compiled 2026-07-31. Focus: the engineering pattern of a master/orchestrator prompt that fans out to subagents, each producing part of a large artifact.

## Evidence strength key

| Label | Meaning |
|---|---|
| **A** | Controlled empirical study, peer-reviewed or with released dataset/protocol |
| **B** | Vendor engineering report with internal evals — real detail, unaudited numbers, commercial interest |
| **C** | Product/framework documentation — authoritative about the system it describes, not about the world |
| **D** | Practitioner writing / marketing — directional, weak |

Wherever a claim rests on **B** or **D**, treat the direction as informative and the magnitude as unverified.

---

## 1. When orchestrator + fan-out beats a single agent, and when it loses

### 1.1 The strongest positive result (B)

Anthropic's Research system is the canonical published win.

> "multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval"
> — [Anthropic, *How we built our multi-agent research system*](https://www.anthropic.com/engineering/multi-agent-research-system)

Caveats that matter more than the headline:
- The eval is internal and unreleased. **B, not A.**
- The task class is **breadth-first search over an open corpus** — the single case where independent parallel exploration is genuinely separable.
- Anthropic itself scopes the claim: *"some domains that require all agents to share the same context or involve many dependencies between agents are not a good fit for multi-agent systems today. For instance, most coding tasks involve fewer truly parallelizable tasks than research."*

In the same post they give the ablation that actually explains the gain: *"token usage by itself explains 80% of the variance"* in their eval performance. That reframes the 90.2% — a large part of the multi-agent advantage is **buying more inference compute and more context window**, not coordination per se.

### 1.2 The strongest negative result (A)

[BenchAgent — *Do More Agents Help? Controlled and Protocol-Aligned Evaluation of LLM Agent Workflows*, arXiv:2606.05670](https://arxiv.org/abs/2606.05670) (Fu et al., June 2026) is the most rigorous head-to-head available, because it equalises the substrate:

> "Does adding more agents help an LLM workflow once compared systems share the same benchmark loader, tool access, answer contract, usage accounting, and trajectory logging? ... Under SI conditions, at most one of six tested MAS exceeds the matched single-agent anchor on benchmark-balanced average accuracy: EvoAgent lies within the Wilson one-run guidance, while the remaining five trail by 2.56-11.29 points and occupy more expensive accuracy-cost trade-offs."

**Five of six multi-agent systems lost to a matched single agent, by 2.56–11.29 points, while costing more.** This is the single most important number in this report: most published multi-agent gains disappear when the harness is held constant, meaning much of the reported advantage was harness quality, not multi-agency.

The same paper's counterpoint is equally important: a **Claude-Code-style runtime workflow** reached 66.72% on GAIA overall and 69.23% on Level 3, *"more than 20 points above the strongest non-Claude baseline, Jarvis, a fixed MAS."* So the winning configuration is not "more agents" — it is **a strong harness that happens to use agents**.

### 1.3 Multi-agent debate: consistently negative (A)

- [*Stop Overvaluing Multi-Agent Debate*, arXiv:2502.08788](https://arxiv.org/abs/2502.08788) — five MAD methods, nine benchmarks, four foundation models: MAD methods *"fail to reliably outperform simple single-agent baselines such as Chain-of-Thought and Self-Consistency."* Their fix is not more agents but **model heterogeneity** (Heter-MAD).
- [ICLR 2025 blogpost, *Multi-LLM-Agents Debate*](https://d2jud02ci9yv69.cloudfront.net/2025-04-28-mad-159/blog/mad/) — with GPT-4o-mini: Self-Consistency 82.13% vs MAD 74.73% on MMLU; CoT 78.05% vs MAD 68.09% on HumanEval. And: *"increasing test-time computation does not always improve accuracy."* MAD *"incorrectly reverses correct answers too frequently."*
- [*The Cost of Consensus*, arXiv:2605.00914](https://arxiv.org/html/2605.00914v1) — unguided homogeneous debate *"fails to significantly outperform self-correction while considering the token cost"*; isolated self-correction wins on cost-accuracy for 7–8B models.

**Implication for a curriculum-builder-style artifact:** homogeneous agents arguing about the same content is the worst-value pattern in the literature. If you use multiple agents, make them *differ* — different roles, different inputs, different models — or don't use them.

### 1.4 Cost and token multipliers (B, C)

| Source | Multiplier | Baseline |
|---|---|---|
| [Anthropic engineering blog](https://www.anthropic.com/engineering/multi-agent-research-system) | agents ≈ **4×** tokens; multi-agent ≈ **15×** tokens | vs. chat interactions |
| [Anthropic, *When to use multi-agent systems*](https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them) | **3–10×** tokens | vs. single-agent, equivalent task |
| [Claude Code agent teams docs](https://code.claude.com/docs/en/agent-teams) | *"Token costs scale linearly"* per teammate | vs. single session |
| [PatchBoard, arXiv:2605.29313](https://arxiv.org/abs/2605.29313) | LangGraph MAS burned **368.3k tokens** per *successful* ALFWorld task | vs. 45.5k for a schema-constrained design |

The 8× spread between the 368.3k and 45.5k figures is the real lesson: **token cost of a multi-agent system is dominated by design, not by agent count.** Free-form message passing is what's expensive.

### 1.5 The decision rule the guidance converges on (B/C)

Anthropic's [when-to-use guidance](https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them) gives three qualifying conditions — context protection, parallelization, specialization — and three disqualifiers:

> "Dividing by type of work...creates constant coordination overhead. Each handoff loses context."

Problematic decompositions they name explicitly:
- sequential phases of the same work (planning → implementation → testing)
- tightly coupled components needing constant synchronisation
- **work requiring shared state between agents**

And the warning that most directly applies to anyone building an orchestrator prompt:

> "Teams invest months building elaborate multi-agent architectures only to discover that improved prompting on a single agent achieved equivalent results."

Their quantitative heuristic for context protection: subtasks that generate **>1,000 tokens of information irrelevant to the main task**. Their specialization signal: **20+ tools**, spanning unrelated domains, where adding tools degrades existing performance.

[OpenAI's practical guide](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) agrees: start with one agent and a few tools; split only when the agent fails to follow complicated instructions or consistently picks wrong tools.

### 1.6 Verdict on Q1

Fan-out wins when **(a)** the subtasks are genuinely independent, **(b)** each subtask generates a lot of intermediate context the final artifact doesn't need, and **(c)** the merge is a *synthesis* rather than a *reconciliation*. It loses when the parts must agree with each other, because agreement is exactly what isolated context cannot produce. The honest framing: **fan-out is a context-management technique that buys parallelism, not a reasoning technique that buys correctness.**

---

## 2. Shared state: named patterns for stopping workers contradicting each other

This is the crux for "each subagent produces part of one large artifact," and the literature is unusually clear that **natural-language message passing is the failure mode, not the solution.**

### 2.1 The problem statement (D, but the canonical articulation)

[Cognition, *Don't Build Multi-Agents*](https://cognition.com/blog/dont-build-multi-agents) gives the two principles everyone else cites:

> **Principle 1:** "Share context, and share full agent traces, not just individual messages"
> **Principle 2:** "Actions carry implicit decisions, and conflicting decisions carry bad results"

The Flappy Bird example is the canonical illustration: subagent 1 builds a Super Mario background, subagent 2 builds a stylistically inconsistent bird, and a third agent inherits *"the undesirable task of combining these two miscommunications."* The diagnosis:

> "the actions subagent 1 took and the actions subagent 2 took were based on conflicting assumptions not prescribed upfront."

**This is precisely the failure mode of splitting a document across parallel writers.** Style, terminology, depth level, and audience assumptions are all implicit decisions.

### 2.2 Pattern: Artifact system / externalised outputs (B)

Anthropic's answer to the same problem:

> "Rather than requiring subagents to communicate everything through the lead agent, implement artifact systems where specialized agents can create outputs that persist independently. Subagents call tools to store their work in external systems, then pass lightweight references back to the coordinator"

Two benefits: the orchestrator's context stays small, and the artifact — not a summary of the artifact — is the unit of merge. **Strongly recommended.** This is the pattern where subagents write files and return paths.

### 2.3 Pattern: Blackboard (A/D)

A centralised shared repository all agents read and write, with agents deciding independently what they can contribute. See [*LLM-based Multi-Agent Blackboard System for Information Discovery in Data Science*, arXiv:2510.01285](https://arxiv.org/html/2510.01285v1). L2MAC's variant is stricter: the file store is *never overwritten, only extended and revised*, with a Control Unit mediating all reads and writes.

The blackboard's weakness is that it is untyped — it becomes a dumping ground, and reading it costs context.

### 2.4 Pattern: Schema-grounded state mutation — the best empirical result (A)

[PatchBoard, arXiv:2605.29313](https://arxiv.org/abs/2605.29313) is the most directly useful empirical finding for shared-artifact fan-out:

> "LLM multi-agent systems often coordinate through natural-language dialogue or loosely structured shared memory, making intermediate state difficult to validate, attribute, and audit. We introduce PatchBoard, a schema-grounded collaboration architecture that replaces inter-agent dialogue with validated JSON Patch mutations over a shared structured state. An Architect agent constructs a task-specific schema and workflow rules, while a deterministic kernel validates each proposed state mutation against schema constraints, role-specific write contracts, and runtime invariants before committing it transactionally."

Results on 630 matched ALFWorld episodes:

| System | Success rate | Tokens per successful task |
|---|---|---|
| **PatchBoard** | **84.6%** | **45.5k** |
| Flock | 61.6% | 64.2k |
| LangGraph | 30.8% | 368.3k |

Three mechanisms are doing the work, and each is independently transferable:
1. **A schema authored up front** by an architect agent — the contract exists before any worker runs.
2. **Role-specific write contracts** — each agent may only mutate the parts of state it owns. This is what structurally prevents contradiction.
3. **A deterministic kernel** validating every mutation before commit — not an LLM checking, code checking.

### 2.5 Pattern: Reducers over concurrent writes (C)

[LangGraph](https://docs.langchain.com/oss/python/langgraph/use-graph-api)'s orchestrator-worker uses the `Send` API to fan out and **state reducers** (e.g. `operator.add`) to merge. The documented failure if you skip the reducer: *"the last worker overwrites previous results."* Nodes execute in **supersteps**, and *"the entire superstep is transactional."*

This is the minimum viable version of PatchBoard's idea: declare, in code, how concurrent writes combine.

### 2.6 Pattern: Ownership partitioning (C)

Claude Code's [agent teams docs](https://code.claude.com/docs/en/agent-teams) state the rule bluntly:

> "**Avoid file conflicts.** Two teammates editing the same file leads to overwrites. Break the work so each teammate owns a different set of files."

The git-worktree literature generalises it: isolation moves conflicts to merge time where tooling detects them, rather than letting them happen silently. But isolation is not sufficient — *"If two agents are both tasked with 'improve the checkout flow,' they'll still conflict because the task wasn't scoped to be independent."* **Spec-driven decomposition is the prerequisite; isolation only makes the failure visible.**

### 2.7 Pattern: Shared task list with locking (C)

Agent teams use a shared task list with dependencies and *"file locking to prevent race conditions when multiple teammates try to claim the same task simultaneously."* Note the documented failure mode: *"Task status can lag: teammates sometimes fail to mark tasks as completed, which blocks dependent tasks."* Coordination state held by LLMs decays.

### 2.8 Pattern: Prescribe the implicit decisions up front

Not named in the literature but it is the direct corollary of Cognition's Principle 2 and Anthropic's delegation guidance:

> "Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries. Without detailed task descriptions, agents duplicate work, leave gaps, or fail to find necessary information."

Anthropic's concrete failure: short instructions like *"research the semiconductor shortage"* produced *"one subagent explored the 2021 automotive chip crisis while 2 others duplicated work investigating current 2025 supply chains."*

**For a large written artifact this means the orchestrator must fix, before fan-out: the outline, the terminology/glossary, the audience and reading level, the section-level output schema, the length budget, and the cross-reference conventions.** Anything left implicit is a contradiction waiting to be merged.

---

## 3. Who holds the loop — the model or code outside it?

There is real, growing consensus here, and it runs **against** model-held orchestration for anything large.

### 3.1 The framing (B)

[Anthropic, *Building Effective AI Agents*](https://www.anthropic.com/engineering/building-effective-agents) draws the line:

> **Workflows:** "systems where LLMs and tools are orchestrated through predefined code paths."
> **Agents:** "systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks."

Orchestrator-workers is defined as the case where *"a central LLM dynamically breaks down tasks, delegates them to worker LLMs, and synthesizes their results"* — and is recommended specifically *for complex tasks where you cannot predict required subtasks in advance*. Where you **can** predict the subtasks, their `parallelization / sectioning` workflow (code-orchestrated) is the recommended pattern instead.

**This matters for artifact generation: if you know the outline, you do not need a model-held orchestrator. You need code that fans out per-section.**

### 3.2 OpenAI's version (C)

[OpenAI Agents SDK — Orchestration](https://openai.github.io/openai-agents-python/multi_agent/):

> "While orchestrating via LLM is powerful, orchestrating via code makes tasks more deterministic and predictable, in terms of speed, cost and performance."

Their code-orchestration catalogue: structured-output classification then routing; agent chaining; evaluation loops (`while` loop with an evaluator agent); parallel execution via `asyncio.gather`.

Their LLM-orchestration split: **agents-as-tools** when the main agent keeps ownership of the final answer, **handoffs** when a specialist should own the next response. For an artifact where one agent must remain accountable for the whole, agents-as-tools is the correct shape — handoffs surrender ownership.

### 3.3 The clearest statement: Claude Code dynamic workflows (C)

The [workflows documentation](https://code.claude.com/docs/en/workflows) makes "who holds the plan" an explicit product axis:

|  | Subagents | Skills | Agent teams | Workflows |
|---|---|---|---|---|
| Who decides what runs next | Claude, turn by turn | Claude, following the prompt | The lead agent, turn by turn | **The script** |
| Where intermediate results live | Claude's context window | Claude's context window | A shared task list | **Script variables** |
| What's repeatable | The worker definition | The instructions | The team definition | **The orchestration itself** |
| Scale | A few per turn | Same | A handful of peers | **Dozens to hundreds per run** |

> "A workflow moves the plan into code. With subagents, skills, and agent teams, Claude is the orchestrator: it decides turn by turn what to spawn or assign next, and every result lands in a context window. A workflow script holds the loop, the branching, and the intermediate results itself, so Claude's context holds only the final answer."

And on quality, not just scale:

> "Moving the plan into code also lets a workflow apply a repeatable quality pattern, not just run more agents: it can have independent agents adversarially review each other's findings before they're reported, or draft a plan from several angles and weigh them against each other"

This is the design that won the BenchAgent GAIA comparison by 20+ points.

### 3.4 Durability and checkpointing (B/C)

Anthropic on production reliability:

> "we can't just restart from the beginning: restarts are expensive and frustrating for users. Instead, we built systems that can resume from where the agent was when the errors occurred"
> "We combine the adaptability of AI agents built on Claude with deterministic safeguards like retry logic and regular checkpoints"
> "we use rainbow deployments to avoid disrupting running agents, by gradually shifting traffic from old to new versions"

LangGraph's [checkpointer](https://docs.langchain.com/oss/python/langgraph/persistence) persists thread state for fault tolerance and human-in-the-loop interrupts; a checkpoint is a recovery point, not a log entry.

The Claude Code workflow runtime documents a subtle and expensive replay rule:

> "An agent that was still running when you stopped isn't saved, so it starts over on resume. Replay follows the order agents started. Cached results stop at the first agent that didn't finish, and every agent that started after that one runs again, even if it completed."
> "A workflow that fans work out across many small agents therefore preserves more progress than one long agent."

**Practical consequence: prefer many small workers to few large ones, for resumability as well as for context.**

### 3.5 Verdict on Q3

The published consensus: **the model should decide *what* the parts are; code should decide *when each part runs, where its output goes, and whether it passed*.** A model-held orchestrator is appropriate for genuinely unpredictable decomposition and for a handful of delegations per turn. Beyond that, orchestration in the context window is the thing that breaks.

---

## 4. Documented failure modes and the taxonomies

### 4.1 MAST — the primary taxonomy (A)

[*Why Do Multi-Agent LLM Systems Fail?*, arXiv:2503.13657](https://arxiv.org/abs/2503.13657) (Cemri, Pan, Yang et al.; NeurIPS 2025). 1,600+ annotated traces across **7 frameworks** (ChatDev, MetaGPT, HyperAgent, AppWorld, AG2, Magentic-One, OpenManus); taxonomy built from 150 traces; human inter-annotator agreement **κ = 0.88**.

> "Despite enthusiasm for Multi-Agent LLM Systems (MAS), their performance gains on popular benchmarks are often minimal."

**The full 14 modes with measured frequencies:**

**FC1. System / specification design issues — 43.8%**
| ID | Failure mode | % |
|---|---|---|
| FM-1.1 | Disobey task specification | 11.8 |
| FM-1.2 | Disobey role specification | 1.5 |
| FM-1.3 | **Step repetition** | 15.7 |
| FM-1.4 | Loss of conversation history | 2.8 |
| FM-1.5 | **Unaware of termination conditions** | 12.4 |

**FC2. Inter-agent misalignment — 32.15%**
| ID | Failure mode | % |
|---|---|---|
| FM-2.1 | Conversation reset | 2.2 |
| FM-2.2 | Fail to ask for clarification | 6.8 |
| FM-2.3 | Task derailment | 7.4 |
| FM-2.4 | Information withholding | 0.85 |
| FM-2.5 | Ignored other agent's input | 1.9 |
| FM-2.6 | **Reasoning-action mismatch** | 13.2 |

**FC3. Task verification — 23.5%**
| ID | Failure mode | % |
|---|---|---|
| FM-3.1 | Premature termination | 6.2 |
| FM-3.2 | No or incomplete verification | 8.2 |
| FM-3.3 | Incorrect verification | 9.1 |

**Reading this for an artifact-generation orchestrator:**
- **Step repetition (15.7%)** is the largest single mode and is exactly "two workers wrote the same section."
- **Reasoning-action mismatch (13.2%)** — the agent's stated plan and its output diverge; a section that says it covers X but doesn't.
- **Unaware of termination conditions (12.4%)** + **premature termination (6.2%)** — agents stopping with the artifact incomplete, which the orchestrator then reports as done.
- **Verification failures total 23.5%**, and *incorrect* verification (9.1%) is worse than *absent* verification (8.2%): a wrong check is more damaging than no check, because it launders a defect as approved.

### 4.2 MAST's intervention results — the most important negative finding (A)

The authors tried both tactical (prompt) and structural (topology/verification) fixes:

- ChatDev/ProgramDev: workflow adjustment (CEO final approval) **+9.4%**; adding high-level task-objective verification **+15.6%**.
- But: *"Although first step interventions lead to performance gains, not all failure modes are resolved, and task completion rates still remain low, indicating that more substantial improvements are needed."*
- *"Achieving high reliability may require combinatorial changes ranging from agent system organization to model level improvements."*

And their verification conclusion, which is directly load-bearing for any orchestrator design:

> "**Multi-Level Verification is Needed.** Current verifier implementations are often insufficient; sole reliance on final-stage, low-level checks is inadequate."
> "More rigorous verification is needed, such as using external knowledge, collecting testing output throughout generation, and multi-level checks for both low-level correctness and high-level objectives."

**Takeaway: a better master prompt is worth roughly +10–15% on these benchmarks and does not fix the class of problem.** Anyone whose plan is "write a really good orchestrator prompt" should size their expectations to that number.

### 4.3 Context drift and context rot (A/B)

- [Chroma, *Context Rot*](https://research.trychroma.com/context-rot) (Hong, Troynikov, Huber) — 18 frontier models: *reliability decreases significantly with longer inputs, even on simple retrieval and text-replication tasks*, and degradation is **non-uniform** (needle-question similarity, distractors, haystack structure all matter). For 1M-token models the observable effect kicks in around 300–400k tokens.
- [Anthropic, *Effective context engineering*](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — context rot defined as *"as the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases"*; explained via the n² attention budget and the fact that models have *"less experience with, and fewer specialized parameters for, context-wide dependencies."*

### 4.4 Error compounding over long horizons (A)

[*The Illusion of Diminishing Returns: Measuring Long Horizon Execution in LLMs*, arXiv:2509.09677](https://arxiv.org/abs/2509.09677):
- Failures on longer tasks arise from **execution**, not inability to reason.
- Per-step accuracy **degrades as step count increases**.
- **Self-conditioning:** *models become more likely to make mistakes when the context contains their previous errors.* Errors are contagious within a context.
- Thinking mitigates self-conditioning and extends single-turn execution length.

**Direct consequence for fan-out:** self-conditioning is an argument *for* fresh subagent contexts (a worker doesn't inherit the orchestrator's mistakes) and *against* long single-threaded generation of a big artifact. It is one of the few genuinely pro-fan-out empirical results.

### 4.5 Lossy handoff — the cost of context isolation (B)

Anthropic states the tradeoff plainly:

> "each subagent might explore extensively, using tens of thousands of tokens or more, but returns only a condensed, distilled summary of its work."

And on compaction: *"overly aggressive compaction can result in the loss of subtle but critical context whose importance only becomes apparent later."*

The Claude Code SDK is more specific about what is actually lost:

> "A subagent's context window starts fresh, with no parent conversation, but isn't empty. **The only content you pass from parent to subagent is the Agent tool's prompt string**, so include any file paths, error messages, or decisions the subagent needs directly in that prompt."

The subagent receives its own system prompt + the Agent tool prompt + project CLAUDE.md; it does **not** receive the parent's conversation history, tool results, or system prompt. **The prompt string is the entire contract.** This is the single most actionable fact for anyone writing a master prompt that fans out.

### 4.6 Hierarchical merge failure modes (A)

For map-reduce over a long artifact specifically: [*Context-Aware Hierarchical Merging for Long Document Summarization*, arXiv:2502.00977](https://arxiv.org/pdf/2502.00977) — hierarchical merging *"often introduces hallucinations and information loss, particularly in domain-specific settings"* and *"cannot produce faithful summaries even when using the most performant LLMs."* Boundary-overlap chunking creates duplicate content that the reduce step must detect and merge.

STORM ([arXiv:2402.14207](https://arxiv.org/abs/2402.14207)) — the best-known multi-perspective long-form generation system — reports **+25% absolute** on "well-organized" and **+10%** on breadth of coverage vs. an outline-driven RAG baseline, but expert Wikipedia editors flagged two failure modes that are exactly the fan-out pathologies: **source bias transfer** and **over-association of unrelated facts across sections.**

### 4.7 Debugging and attribution is near-impossible (A)

This is the most underappreciated failure mode: **you cannot easily find out which subagent broke the artifact.**

- [TRAIL, arXiv:2505.08638](https://www.patronus.ai/blog/introducing-trail-a-benchmark-for-agentic-evaluation) — 148 human-annotated traces, 841 error annotations. *Best model (Gemini-2.5-pro) scores 11%* at localising errors in agentic traces.
- [Who&When Pro, arXiv:2607.09996](https://arxiv.org/html/2607.09996v1) — 12,326 failure traces, 26 source benchmarks. Step-level attribution: **94% on traces <3K tokens, 50% on traces >12K tokens.** Agent-level attribution: **~57.5%** best case. Error-mode classification: **17% macro-F1** on text. Joint accuracy (which step, which agent, what kind): **~25%**.
- Diagnosis of why: *"Models classify by surface-level similarity rather than tracing causal chains. Planning, verification, and coordination errors are frequently mislabeled as reasoning errors since they leave similar observable symptoms."*

Anthropic's version of the same problem: *"Agents make dynamic decisions and are non-deterministic between runs, even with identical prompts. This makes debugging harder."* Their mitigation is **full production tracing** of decision patterns and interaction structures.

**Design implication: attribution must be built in structurally (per-section provenance, per-agent write contracts, per-worker logs) because it cannot be recovered post-hoc by asking a model to read the trace.**

---

## 5. Verification: LLM-as-judge vs deterministic checks

### 5.1 The consensus shape (B/C/D)

There is broad agreement on a **layered** answer, not a winner:

- **Deterministic checks** for anything mechanically checkable: schema, format, required fields, length, link validity, presence of every planned section, test pass/fail. Cheap, predictable, unhackable.
- **LLM judges** only for the semantic residue: coverage, faithfulness to sources, tone, pedagogical fit.

Framed in the RL literature as **verifiable rewards** ("did it solve the problem") + **rubric graders** ("is it readable, correct in style, well-targeted"). See [Braintrust](https://www.braintrust.dev/articles/what-is-llm-as-a-judge), [Evidently](https://www.evidentlyai.com/llm-guide/llm-as-a-judge).

Anthropic's own eval used an LLM-as-judge with an explicit rubric — *"factual accuracy (do claims match sources?), citation accuracy (do the cited sources match the claims?), completeness (are all requested aspects covered?), source quality..., and tool efficiency"* — but they pair it with human testing, because *"People testing agents find edge cases that evals miss. These include hallucinated answers on unusual queries, system failures, or subtle source quality biases."* Their concrete example of a bias only humans caught: agents *"consistently chose SEO-optimized content farms over authoritative but less highly-ranked sources like academic PDFs or personal blogs."*

Also notable: they started with **~20 queries** and found that sufficient to see the impact of changes. Small, real eval sets beat large synthetic ones early.

### 5.2 Judge independence is much weaker than assumed (A)

The most important finding in this section: [*Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels*, arXiv:2605.29800](https://arxiv.org/html/2605.29800v1).

> "Testing a panel of 9 frontier LLMs from 7 model families on three natural language inference datasets (each with 100 human annotations per item), we find that the 9 judges effectively provide only about 2 independent votes' worth of information."

- n_eff = **2.18** (95% CI 2.07–2.31) on MNLI; 2.18–2.48 across datasets → **24.2% independence**.
- Mean pairwise φ correlation between judges: **0.391** (range 0.161–0.603).
- Condorcet gap **22.0 pp**: panel accuracy **72.0%** vs. Condorcet-predicted **94.0%**.
- **The best single judge (Qwen3-32B, 71.8%) matched the full nine-model panel.**
- Even with oracle labels, established aggregation methods close **at most 11%** of the gap.
- Their recommendation: report n_eff as standard diagnostic; *"if n_eff/k < 0.5, results should be treated with caution"*; and *"models that genuinely differ in how they process information—not merely different brand names on similar architectures."*

**Adding more judges from the same family buys almost nothing.** This directly undercuts the "have three subagents review it" pattern when all three are the same model with different prompts.

### 5.3 Self-evaluation bias (A)

- [*Self-Preference Bias in LLM-as-a-Judge*, arXiv:2410.21819](https://arxiv.org/pdf/2410.21819) — self-preference is widespread across popular LLMs and tasks. On ArenaHard, self-preferential bias ranges **-38% to +90%**; on other datasets **-21% to +56%**.
- Mechanism: **self-recognition capability** contributes significantly to the bias; and LLMs *"assign significantly higher evaluations to outputs with lower perplexity than human evaluators"* — i.e. models prefer text that is *familiar to them*, whether or not they wrote it. That means the bias survives even when you hide authorship.
- Mitigation with the most support: **do not use the same model to both generate and judge.** Peer-rank/panel approaches help, subject to the correlated-error ceiling in 5.2.
- Position bias and verbosity bias are separately documented and severe: all LLM judges show *"a strong and significant length bias... substantially greater than that observed in human evaluations."* Mitigations: randomise order, evaluate permutations, explicitly penalise redundancy in the rubric.
- Ceiling: strong judges reach **>80% agreement with human preferences** on MT-Bench/Chatbot Arena — about the same as human-human agreement. That is the realistic best case, not a floor.

### 5.4 The verification horizon (A)

[*Verification Horizon: Coding Agent Reward Limits*, arXiv:2606.26300](https://arxiv.org/abs/2606.26300) (June 2026) is the deepest treatment:

> "A classical intuition holds that verifying a solution is easier than producing one. For today's coding agents, this intuition is being inverted: as foundation models develop stronger reasoning capabilities and engineering harnesses grow more sophisticated, generating complex candidate solutions is no longer difficult -- reliably verifying them has become the harder problem. Every verifier we can build is only a proxy for human intent, never the intent itself."

Their framework: verification signals have three properties — **scalability, faithfulness, robustness** — and *"achieving all three simultaneously is the central challenge."* They study four reward constructions (test verifier, rubric verifier, user-as-verifier, automated agent verifier) and conclude:

> "no fixed reward function can remain effective as policy capability continues to grow; and verification must co-evolve with the generator."

Related: reward-hacking research finds *"'master-key' tokens trigger false-positive rewards up to 80% even on advanced judges."* A judge is an attack surface, and the generator is the attacker even without intending to be.

### 5.5 A shipped pattern worth copying (C)

Claude Code's bundled `/deep-research` workflow implements a verification design that maps onto artifact generation well:

> "Fans out web searches on a question across several angles, fetches and cross-checks the sources it finds, **votes on each claim**, and returns a cited report with claims that didn't survive cross-checking filtered out."

Plus a subtlety worth stealing:

> "when the verifier agents can't check a claim, such as after a rate limit or API error, the report lists that claim as **unverified** instead of counting it as refuted."

**Three-state verification (verified / refuted / unverified) instead of binary is a meaningful robustness improvement** — it stops infrastructure failures from silently becoming quality signals. Most hand-rolled orchestrators get this wrong.

### 5.6 Verdict on Q5

Consensus exists on the layering (deterministic first, judge for the residue) and on the mitigation (don't let the generator judge itself). Consensus does **not** exist that judge panels work — the effective-votes result says they mostly don't. Practical stance:

1. Every property you can check with code, check with code. This is where the reliable signal is.
2. One judge, a different model from the generator, with an explicit rubric, randomised order.
3. Do not expect a second and third judge of the same family to add much; spend that budget on a deterministic check or a human sample instead.
4. Verify at multiple levels (MAST: low-level correctness *and* high-level objective), not only at the end.
5. Treat "couldn't verify" as its own state.

---

## 6. Practical limits: how many, how long, what breaks first

### 6.1 Published numbers on subagent counts

| Source | Guidance | Type |
|---|---|---|
| [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system) | Lead spawns **3–5 subagents** typically; *"Simple fact-finding requires just 1 agent with 3-10 tool calls, direct comparisons might need 2-4 subagents with 10-15 calls each, and complex research might use more than 10 subagents"* | B |
| [Claude Code agent teams](https://code.claude.com/docs/en/agent-teams) | *"Start with 3-5 teammates for most workflows"*; *"Having 5-6 tasks per teammate keeps everyone productive"*; *"Three focused teammates often outperform five scattered ones"* | C |
| [Claude Code workflows](https://code.claude.com/docs/en/workflows) | Size guidelines: `small` <5, `medium` <15 (default), `large` <50 agents | C |
| [LLM judge panels](https://arxiv.org/html/2605.29800v1) | 9 judges ≈ 2 effective votes; best single judge matched the panel | A |
| LLM-as-judge ensembles (practitioner consensus) | Benefit strongest at 3–5 annotators, plateaus after | D |

**The convergence on 3–5 across independent sources is the most reliable practical number in this report.**

### 6.2 Hard runtime caps (C)

From the Claude Code workflow runtime — real engineering constraints from a shipped system:

| Constraint | Stated reason |
|---|---|
| **Up to 16 concurrent agents**, fewer on limited-CPU machines | "Bounds local resource use" |
| **1,000 agents total per run** | "Prevents runaway loops" |
| **No mid-run user input** | "For sign-off between stages, run each stage as its own workflow" |
| **No direct filesystem or shell access from the workflow itself** | "Agents read, write, and run commands. The script coordinates the agents" |
| Warning at **>25 agents scheduled** or **>1.5M projected tokens** | Cost blowout detection |
| Subagent nesting default **3 layers** below main conversation (configurable, `1` disables) | — |

Note the separation-of-powers design: the orchestration script **cannot touch the filesystem** — only agents can act, the script only coordinates. That is a deliberate blast-radius boundary worth copying.

### 6.3 Context limits (B)

> the lead agent "sav[es] its plan to Memory to persist the context, since if the context window exceeds 200,000 tokens it will be truncated and it is important to retain the plan"

Practical degradation begins well before any hard limit — see Chroma's 300–400k observable-effect threshold on 1M-token models (§4.3), and note that degradation is task-dependent and non-uniform, so there is no single safe number.

### 6.4 What breaks first — ranked by the evidence

1. **Task specification.** MAST FC1 = 43.8%, the largest category, and Anthropic's delegation failure (duplicate semiconductor research) is the same thing. The orchestrator prompt's boundaries are the first thing to fail, before any coordination machinery is exercised.
2. **Duplication and gaps.** FM-1.3 step repetition is the single largest mode at 15.7%. Two workers cover the same ground; nobody covers the gap between them.
3. **Verification.** 23.5% of failures, and *incorrect* verification (9.1%) exceeds *absent* verification (8.2%).
4. **Termination.** FM-1.5 (12.4%) + FM-3.1 (6.2%) = 18.6% — agents declaring done while incomplete. Agent teams docs report the same at product level: *"The lead may decide the team is finished before all tasks are actually complete."*
5. **Context**, on long runs — rot, then truncation, then lossy compaction.
6. **The synchronous merge.** Anthropic: *"our lead agents execute subagents synchronously, waiting for each set of subagents to complete before proceeding. This simplifies coordination, but creates bottlenecks."*
7. **Debuggability**, at which point iteration stops (§4.7 — 11% error localisation, ~25% joint attribution).

### 6.5 Latency and its counterweight (B)

Parallel tool use inside subagents *"cut research time by up to 90% for complex queries."* So fan-out is a strong latency win even where it's an accuracy wash — which is a legitimate reason to use it, and worth stating honestly rather than dressing up as a quality argument.

---

## Synthesis: what this means for a master prompt that fans out to build one large artifact

**Structural moves with real evidence behind them:**

1. **Fix the contract before fan-out.** Outline, glossary, audience, per-part output schema, length budget, cross-reference rules. Everything Cognition calls an "implicit decision" must be made explicit by the orchestrator. This addresses the 43.8% category.
2. **Give each worker exclusive ownership of its part.** Role-specific write contracts (PatchBoard: 84.6% vs 30.8%), or file-level ownership (agent teams docs). Never let two workers write the same artifact region.
3. **Workers write to files and return references, not content.** Anthropic's artifact pattern. Keeps the orchestrator's context small and makes the artifact — not a summary — the merge unit.
4. **Put the fan-out loop in code, not in the context window** once you exceed a handful of parts. This is the difference between the winning and losing configurations in BenchAgent.
5. **Validate every part deterministically before it counts as done.** Schema, required sections, terminology conformance, cross-reference resolution. Code checks, not judge checks.
6. **Judge with a different model than the one that generated, once, with a rubric.** Don't buy a panel of the same family; the ninth judge is worth almost nothing.
7. **Three-state verification.** verified / refuted / unverified.
8. **Verify at two levels** — per-part correctness and whole-artifact objective (MAST's explicit recommendation).
9. **Many small workers over few large ones** — better resumability, less self-conditioning, more preserved progress on interruption.
10. **Build attribution in.** Per-part provenance and per-worker logs, because post-hoc attribution runs at ~25% joint accuracy.

**Expectations to set honestly:**

- Budget **3–10× tokens** (Anthropic's own range) and start at **3–5 workers**.
- A better orchestrator prompt is worth roughly **+10–15%** on the benchmarks where it's been measured, and does not eliminate any failure category.
- Under matched harnesses, **most multi-agent systems lose to a good single agent**. The burden of proof is on the fan-out.
- The strongest honest arguments for fan-out on a large written artifact are **context isolation** (avoiding rot and self-conditioning) and **latency** — not correctness.
- The thing fan-out is structurally worst at is **making the parts agree with each other**, which is the defining requirement of a coherent large artifact. That has to be engineered in as a contract up front, or repaired at the merge — it does not emerge.

---

## Source list

**Primary engineering reports (B)**
- https://www.anthropic.com/engineering/multi-agent-research-system
- https://www.anthropic.com/engineering/building-effective-agents
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them
- https://cognition.com/blog/dont-build-multi-agents
- https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/

**Empirical papers (A)**
- https://arxiv.org/abs/2503.13657 — MAST, Why Do Multi-Agent LLM Systems Fail?
- https://arxiv.org/abs/2606.05670 — BenchAgent, Do More Agents Help?
- https://arxiv.org/abs/2605.29313 — PatchBoard, schema-grounded state mutation
- https://arxiv.org/abs/2502.08788 — Stop Overvaluing Multi-Agent Debate
- https://arxiv.org/html/2605.00914v1 — The Cost of Consensus
- https://d2jud02ci9yv69.cloudfront.net/2025-04-28-mad-159/blog/mad/ — ICLR blogpost on MAD
- https://arxiv.org/abs/2509.09677 — Illusion of Diminishing Returns / long-horizon execution
- https://arxiv.org/html/2605.29800v1 — Nine Judges, Two Effective Votes
- https://arxiv.org/pdf/2410.21819 — Self-Preference Bias in LLM-as-a-Judge
- https://arxiv.org/abs/2606.26300 — Verification Horizon
- https://arxiv.org/html/2607.09996v1 — Who&When Pro (failure attribution)
- https://www.patronus.ai/blog/introducing-trail-a-benchmark-for-agentic-evaluation — TRAIL
- https://research.trychroma.com/context-rot — Context Rot
- https://arxiv.org/abs/2402.14207 — STORM
- https://arxiv.org/pdf/2502.00977 — Context-Aware Hierarchical Merging
- https://arxiv.org/html/2510.01285v1 — Blackboard system for information discovery
- https://arxiv.org/abs/2605.18747 — Code as Agent Harness (survey)
- https://arxiv.org/abs/2308.00352 — MetaGPT

**Documentation (C)**
- https://code.claude.com/docs/en/agent-sdk/subagents
- https://code.claude.com/docs/en/workflows
- https://code.claude.com/docs/en/agent-teams
- https://openai.github.io/openai-agents-python/multi_agent/
- https://docs.langchain.com/oss/python/langgraph/use-graph-api
- https://docs.langchain.com/oss/python/langgraph/persistence

**Practitioner (D)**
- https://www.braintrust.dev/articles/what-is-llm-as-a-judge
- https://www.evidentlyai.com/llm-guide/llm-as-a-judge
- https://www.augmentcode.com/guides/git-worktrees-parallel-ai-agent-execution
