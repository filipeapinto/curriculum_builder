# State of the art (Aug 2026): is there a standard schema for a "plan" artifact?

## Why this thread

`curriculum_builder` already has a house schema for the *prompt* artifact
(`schemas/prompt.schema.v1.json`/`v2.json`, grounded in
`research/prompt_schemas/prompt_schema_state_of_the_art.v1.md`), but nothing
schemas the *plan* artifact one level up — `plans/<slug>/` packages exist in
two demonstrably different shapes already (see below) with no contract
saying which fields are required in either, or how a plan declares which
shape it is. Before authoring `schemas/plan.schema.v1.json`, this checks (1)
what shape this repo's own plans have already converged on by evidence, not
assumption, and (2) whether an external, more authoritative schema for
"plan" as an artifact distinct from a prompt already exists.

## Findings

**This repo has already produced two structurally different, both-proven
plan shapes, and the difference is exactly "single prompt vs. graph of
prompts."** `plans/11_provider_correction/` (the reference run the
`plan-create` skill is modeled on) is one plan, one QA pass, one
`prompts/provider_correction.prompt.v1.md` — a linear plan implemented by a
single GOAL/TEST/LOOP prompt. `plans/26_langgraph_curriculum_factory/` and
`plans/27_langgraph_curriculum_factory_remediation/` are the opposite shape:
`implementation.graph.v<N>.yaml` declares named nodes
(`N00_SPEC_APPROVAL_GATE`, `N20_PROVIDER_TRANSPORT`, ...), each bound to its
*own* prompt file, with `depends_on`, `writes`, `verification` commands,
`test_lane`, and `allowed_results`; `edges` carry a `type` of `normal`,
`fan_out`, or `all_of`; `rework_edges` route a failing node back to an
earlier one; `terminals` (`ACTIVATED` / `IMPLEMENTED_NOT_ACTIVATED` /
`BLOCKED`) each require a `guard`. A `controller/` (`scheduler.py`,
`core.py`) executes that DAG mechanically — this is a real, already-running
"prompt graph," not a hypothetical.

**A third shape is also already real in this exact repo, and it is
different again from both of the above: the plan's own execution engine can
be an actual LangGraph `StateGraph`, not a bespoke controller.**
`runtime/langgraph_factory/graph.py` imports `from langgraph.graph import
END, START, StateGraph` and builds the production curriculum graph with
`builder.add_node(...)`, `builder.add_edge(source, target)`, and
`builder.add_conditional_edges(source, path, {target: target for target in
destinations})`, then compiles it. A `prompt_graph` (plan 26/27's shape)
dispatches Claude Code *prompts* as nodes via a custom scheduler; a
`langgraph_graph` compiles actual Python node functions into a LangGraph
`StateGraph` with real checkpointing and conditional routing. Conflating
these two would misdescribe what plans 26/27 actually built versus what
`runtime/langgraph_factory` actually runs — they are not the same
"graph," even though both are graphs.

**LangGraph's own "plan-and-execute" reference pattern independently
converges on "a plan is a graph with planner/executor/replanner nodes,"
which validates the shape found in plans 26/27 rather than the single-prompt
shape as the more general case.** LangChain's own write-up defines the
pattern as a **planner** node that "prompts an LLM to generate a multi-step
plan to complete a large task" and **executor** node(s) that "invoke 1 or
more tools to complete that task," with edges representing state
transitions "from planning to execution to evaluation and back again," and
notes plans can be "a DAG with variable assignments" (citing ReWOO's
`#E2`-style step-references-earlier-step syntax) rather than a flat list —
structurally the same shape as plan 26/27's `depends_on` edges between named
nodes. This is convergent validation that a plan-as-DAG is a recognized
architecture, not a house-specific complication.

**No external body publishes a schema for "plan" as a multi-shaped artifact
spanning single-prompt / prompt-graph / compiled-StateGraph — the same
"structure by convention, not by schema" pattern the prompt research already
found holds one level up too.** LangGraph publishes API shapes for
`StateGraph`/`add_node`/`add_edge` (a code contract, not a plan-document
schema) and a worked pattern, not a JSON Schema for a planning document.
Spec-driven-development tooling (Spec Kit et al., already checked in the
prompt research) treats `plan.md` as one of four markdown phase outputs with
no published schema. AGENTS.md-style "structure by convention" is the 2026
default for this genre generally, not an argument specific to prompts.

**Architecture Decision Records are a real, adopted precedent for the "why
does this exist" section this repo's own `agent_card.md` convention already
uses for reviewer agents (context → decision → consequences), but ADR itself
has no single canonical schema either.** The ADR clearinghouse states an ADR
"captures a single AD and its rationale... the reasons for a chosen
architectural decision, along with its trade-offs and consequences," and
explicitly catalogs multiple competing templates (Nygard's original,
Y-statements, MADR, and others) rather than one required shape. This
supports borrowing the *shape* (why this plan exists, what was chosen, what
it costs) for a plan's rationale section, not adopting ADR wholesale or
treating its field names as load-bearing.

## Conclusion

No external body schemas "plan" as an artifact that can be implemented three
different ways (single prompt, prompt graph, compiled LangGraph graph) —
this repo has already built and run all three, which is stronger grounding
than any external precedent. `schemas/plan.schema.v1.json` should therefore:
(1) require the fields every plan in this repo already has regardless of
shape — slug, title, objective, explicit non-authorization-to-implement
(per the `plan-create` skill's own rule that planning artifacts don't
authorize implementation), a rationale citing what would go wrong without
this plan, and the QA/audit pipeline (`plan_qa`, `execution_test_plan`,
`final_audit` verdict lines) `plans/11_provider_correction/` and the
`plan-create` skill already mandate; (2) require a closed
`implementation.execution_model` enum of exactly `single_prompt`,
`prompt_graph`, `langgraph_graph` — the three shapes found by evidence, not
an open string; (3) require only the minimum pointer fields each shape needs
(e.g. `prompt_graph` points at its own `implementation.graph.v<N>.yaml` and
`controller_path` rather than re-specifying node/edge shape inline) so this
schema does not duplicate or drift from `implementation.graph.schema.v3.json`
or `runtime/langgraph_factory/graph.py`'s real API surface; (4) borrow ADR's
context/decision/consequences *shape* for the rationale field without
adopting ADR's field names, consistent with this repo's `agent_card.md`
"defect it exists to catch" convention.

## Sources (fetched and verified)

- LangChain, "Plan-and-Execute Agents" —
  https://www.langchain.com/blog/planning-agents
- arXiv:2509.08646, "Architecting Resilient LLM Agents: A Guide to Secure
  Plan-then-Execute Implementations" (search-result summary; not fetched in
  full) — https://arxiv.org/pdf/2509.08646
- adr.github.io, "Architectural Decision Records (ADRs)" —
  https://adr.github.io/
- This repository, inspected directly: `plans/11_provider_correction/`,
  `plans/26_langgraph_curriculum_factory/implementation.graph.schema.v3.json`
  and `implementation.graph.v3.yaml`,
  `plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml`
  and `controller/`, `runtime/langgraph_factory/graph.py`,
  `.claude/skills/plan-create/SKILL.md`,
  `.claude/skills/learning-agent-create/assets/agent_card.md`.

## Discarded

- ReWOO's `#E2` step-output-reference syntax was noted as evidence that
  plans-as-DAGs are an established pattern, but its exact substitution
  syntax was not adopted here — this repo's own `depends_on`/`writes` shape
  (plans 26/27) already solves the same problem and changing it would break
  two already-running plan packages for no benefit.
- MADR and Y-statement ADR templates were found in the ADR survey but not
  cited individually: the finding needed was "ADR has no one canonical
  schema," which the clearinghouse itself states, not a specific template's
  field list.
