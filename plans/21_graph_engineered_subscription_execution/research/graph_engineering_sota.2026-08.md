# Graph engineering for prompted systems — state of the art, 2026-08-09

## Scope and terminology

This review uses **graph engineering** to mean the deliberate design, execution,
verification, and evolution of graphs whose nodes contain prompts, deterministic
tools, evaluators, or human gates. It is broader than Graph of Thoughts alone.
The evidence supports four related layers:

1. a **reasoning graph** inside or across model calls (Graph of Thoughts and its
   successors);
2. an **execution graph** of typed nodes, conditional edges, parallel fan-out,
   joins, and bounded cycles;
3. a **state/evidence graph** of checkpoints, artifacts, receipts, provenance,
   and resumable transitions; and
4. an **assurance graph** used to compile, test, trace, optimize, and statically
   verify the workflow before and during execution.

The cutoff is 2026-08-09. Peer-reviewed work is preferred. Recent 2026 arXiv
preprints are included where they describe capabilities not yet represented in
the archival literature and are identified as preprints.

## Evidence synthesis

### 1. Prompt structure has moved from linear chains to composable graphs

Graph of Thoughts models intermediate model outputs as vertices with dependency
edges, allowing branches to be combined and revised rather than forcing a single
linear chain. Later surveys generalize chains, trees, and graphs under one
blueprint. In production, the more important consequence is not exposing hidden
reasoning; it is decomposing work into inspectable, replaceable operations with
explicit dependencies.

Sources:

- [Graph of Thoughts (arXiv, 2023)](https://arxiv.org/abs/2308.09687)
- [Demystifying Chains, Trees, and Graphs of Thoughts (arXiv, 2024)](https://arxiv.org/abs/2401.14295)
- [AGORA (ACL 2025)](https://aclanthology.org/2025.acl-demo.11/)

### 2. The graph is now an execution contract, not merely a diagram

Current graph runtimes treat nodes as functions over typed state and edges as
deterministic or conditional routing. They support sequential work, parallel
fan-out, joins, cycles, interrupts, and explicit exit conditions. A graph is
compiled before execution to detect structural defects such as orphaned nodes.
Execution topology and message/context topology are distinct: an agent may be
scheduled after another agent without being entitled to receive its complete
history.

Sources:

- [LangGraph Graph API](https://langchain-ai.github.io/langgraph/how-tos/state-reducers/)
- [AutoGen GraphFlow](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/graph-flow.html)
- [Production workflow graphs (ACL Industry 2025)](https://aclanthology.org/2025.acl-industry.107/)

### 3. Reliable loops are evaluator-optimizer cycles with measurable exits

Anthropic's evaluator-optimizer pattern separates generation from evaluation
and loops only when criteria are clear and iterative feedback can measurably
improve the artifact. PiVe demonstrates the same shape for graph generation:
a verifier emits fine-grained corrective instructions and the generator revises
iteratively. The current lesson is **goal → test → targeted repair → retest**,
with a pass edge, a bounded repair edge, and an honest exhausted/blocked edge.
Unbounded self-reflection is not state of the art; 2026 work reports large
redundancy from late re-verification and graph-based pruning can cut reasoning
tokens while maintaining quality.

Sources:

- [Anthropic, Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [PiVe (Findings of ACL 2024)](https://aclanthology.org/2024.findings-acl.400/)
- [Graph-Based Chain-of-Thought Pruning (Findings of ACL 2026)](https://aclanthology.org/2026.findings-acl.281/)

### 4. Durable state, replay, and idempotency are first-class graph semantics

Stateful workflows checkpoint at graph or task boundaries, preserve completed
writes when siblings fail, and resume without rebuilding valid work. Because a
node can be replayed from its beginning, side effects must be idempotent or
wrapped as checkpointed tasks. Interrupts and human gates are graph transitions,
not ad-hoc pauses inside a monolithic function.

Sources:

- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph functional API](https://docs.langchain.com/oss/python/langgraph/functional-api)
- [LangGraph interrupts](https://langchain-ai.github.io/langgraph/concepts/breakpoints/)

### 5. Typed boundaries and context minimization matter as much as topology

Structured input/output schemas, guardrails, input filters, tool permissions,
and isolated workspaces constrain what each model node can observe or mutate.
AutoGen explicitly separates the execution graph from the message graph.
OpenAI handoffs provide typed handoff metadata and input filters; Anthropic
frames context engineering as the successor to prompt engineering because an
agent loop must cyclically select and refine what enters the next inference.

Sources:

- [OpenAI Agents SDK handoffs](https://openai.github.io/openai-agents-python/handoffs/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Anthropic, Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 6. Assurance has expanded from output checks to graph and trajectory checks

Outcome-only grading misses redundant or unsafe paths. GEMMAS evaluates the
interaction DAG itself. Agentproof (2026 preprint) extracts workflow graphs,
runs structural checks, produces witness traces, and evaluates temporal safety
policies. AgentEval (2026 preprint) mines stateful workflow boundaries and
perturbs each boundary, substantially increasing distinct boundary coverage
over prompt-only tests. Lean4Agent (2026 preprint) explores formal semantic
verification and reports better performance for verification-passing workflows.
These results support static graph validation plus dynamic path, boundary, and
fault-injection tests; neither replaces the other.

Sources:

- [GEMMAS (EMNLP Industry 2025)](https://aclanthology.org/2025.emnlp-industry.106/)
- [Agentproof (arXiv preprint, 2026)](https://arxiv.org/abs/2603.20356)
- [AgentEval (arXiv preprint, 2026)](https://arxiv.org/abs/2607.06873)
- [Lean4Agent (arXiv preprint, 2026)](https://arxiv.org/abs/2606.06523)

### 7. Graphs and prompts can evolve, but changes must be evaluated and versioned

EvoAgentX optimizes prompts, tool configurations, and workflow topology through
an evaluation layer. GraphFlow's wGraph (2026 preprint) dynamically instantiates
task workflows from atomic operations. This is useful only when the candidate
graph is versioned, compiled, evaluated against a fixed corpus, and promoted by
measured evidence. A model-generated topology must not mutate a live run in
place or silently change resume semantics.

Sources:

- [EvoAgentX (EMNLP Demos 2025)](https://aclanthology.org/2025.emnlp-demos.47/)
- [GraphFlow / wGraph (arXiv preprint, 2026)](https://arxiv.org/abs/2605.22566)

## August 2026 engineering rubric

A production prompt graph meets the state of the art when it has all of the
following properties, proportional to its risk:

| ID | Property | Required evidence |
|---|---|---|
| GE-01 | Explicit graph IR | Versioned nodes, edges, entry, terminals, and allowed cycles are machine-readable. |
| GE-02 | Atomic typed nodes | Each node has a role, goal, authorized inputs/outputs, schemas, owner, and side-effect class. |
| GE-03 | Explicit edge guards | Branch, fan-out, join, retry, revision, interrupt, and stop semantics are code-owned. |
| GE-04 | Goal–test–loop prompts | Every model-bearing node names its goal, deterministic tests, repair scope, retest order, and convergence limit. |
| GE-05 | Compiled topology | Static checks reject unreachable nodes, orphan terminals, illegal cycles, unsafe paths, and missing failure edges. |
| GE-06 | Typed state and reducers | State schemas and parallel merge/reducer semantics are explicit and deterministic. |
| GE-07 | Durable execution | Checkpoints, idempotency keys, replay rules, interrupt/resume, and immutable accepted artifacts are tested. |
| GE-08 | Boundary isolation | One normalized invocation contract enforces least-privilege context, tools, reads, writes, and structured output. |
| GE-09 | Independent evaluation | Generators do not accept their own outputs; evaluator evidence is schema-valid and fail-closed. |
| GE-10 | Targeted recovery | Failed checks map to one owned artifact/node; repair does not broadly regenerate accepted siblings. |
| GE-11 | Trace and provenance | Node/edge events bind graph version, prompt hash, inputs, route, model, outputs, checks, and costs/usage. |
| GE-12 | Path and fault testing | Positive paths, every guard boundary, retry exhaustion, malformed output, resume, and policy violations are exercised. |
| GE-13 | Process-level evals | Tests measure path efficiency, redundancy, unnecessary re-verification, and collaboration/context quality, not only final output. |
| GE-14 | Safe evolution | Prompt/topology candidates are evaluated off-line, versioned, compiled, and explicitly promoted; active runs remain pinned. |

This rubric is the assessment authority for Plan 20 and the design authority for
Plan 21.
