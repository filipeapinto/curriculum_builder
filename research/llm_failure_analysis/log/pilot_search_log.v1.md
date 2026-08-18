# Pilot search log

Date: 2026-08-18  
Candidates screened: 28  
Sources fully assessed: 12  
Duplicates/consolidations: 9 pages consolidated into their parent specification or product documentation set  
Excluded after screening: 7 (marketing summaries, duplicate navigation pages, secondary explainers, or pages without mechanism detail)

## Queries

1. `site:opentelemetry.io docs generative AI semantic conventions traces metrics events`
2. `site:w3.org TR prov-o provenance recommendation`
3. `site:openlineage.io docs specification run event facets`
4. `site:temporal.io durable execution event history retries idempotency official`
5. `site:docs.temporal.io workflow execution event history retry policy idempotency official`
6. `site:nist.gov AI RMF generative AI profile incident monitoring evaluation official`
7. `site:sre.google postmortem culture incident response monitoring distributed systems official`
8. `site:mlflow.org docs tracing LLM agents token usage official`
9. `Temporal documentation durable execution workflow event history site:docs.temporal.io`
10. `LangSmith observability traces runs metadata feedback official docs site:docs.langchain.com/langsmith`
11. `OpenAI Agents SDK tracing official documentation evaluations graders site:openai.com OR site:platform.openai.com`
12. `Arize Phoenix tracing evaluations datasets experiments official docs site:arize.com OR site:arize-ai.github.io`
13. `site:platform.openai.com/docs/guides/agents-sdk tracing OpenAI Agents SDK`
14. `site:openai.github.io/openai-agents-python tracing official`
15. `site:docs.temporal.io encyclopedia event history durable execution retries`
16. `site:prisma-statement.org prisma 2020 checklist flow diagram`

## Fully assessed sources

| ID | Source | Class | Authority/quality | Extracted mechanism | Pilot disposition |
|---|---|---|---|---|---|
| S01 | [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/) | Observability standard | Official specification; mixed stability | Common attributes for traces, metrics, logs, events, resources; GenAI conventions are a separate evolving area | Include; record stability per field |
| S02 | [OpenTelemetry event conventions](https://opentelemetry.io/docs/specs/semconv/general/events/) | Observability standard | Official specification; development status | Named, timestamped, queryable events; `error.type`; separate events, spans, and attributes | Include with maturity caveat |
| S03 | [W3C PROV-O](https://www.w3.org/TR/prov-o/) | Provenance standard | W3C Recommendation with implementation report | Entities, activities, agents, derivation, attribution, association | Include as lineage vocabulary |
| S04 | [OpenLineage object model](https://openlineage.io/docs/spec/object-model/) and [facets](https://openlineage.io/docs/spec/facets/) | Lineage implementation | Official open specification | Run/job/input/output event model plus extensible facets | Include; compare with repository artifact model |
| S05 | [Temporal workflow execution](https://docs.temporal.io/workflow-execution) and [event history](https://docs.temporal.io/workflow-execution/event) | Durable execution | Official implementation documentation | Append-only history, replay, explicit terminal states, retry limits, resume from recorded state | Include as implementation evidence, not a mandatory platform choice |
| S06 | [NIST AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) | Governance standard/guidance | Government consensus framework | Documented TEVV, independent assessment, production monitoring, incident response, recovery, change management | Include for governance outcomes |
| S07 | [NIST Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) | GenAI governance | Government profile | Govern/map/measure/manage actions specialized to GAI risks | Include; extract only execution-relevant actions |
| S08 | [Google SRE postmortem culture](https://sre.google/sre-book/postmortem-culture/) | Incident practice | Mature documented industry practice | Incident impact, timeline/actions, causes, follow-ups; blameless learning and trend analysis | Include as incident-record practice |
| S09 | [MLflow token and cost tracking](https://mlflow.org/docs/latest/genai/tracing/token-usage-cost/) | LLM telemetry implementation | Official mature project documentation; version-dependent | Per-span and aggregate input/output/total tokens and estimated cost | Include; verify provider coverage and estimation limits later |
| S10 | [LangSmith observability concepts](https://docs.langchain.com/langsmith/observability-concepts) | LLM tracing implementation | Official product documentation | Projects, traces, runs, threads, stable IDs, metadata, feedback, retention | Include as comparative implementation, not normative evidence |
| S11 | [Phoenix observability and evaluation](https://arize.com/docs/phoenix/) | Open-source LLM observability/eval | Official open-source product documentation | OTel traces, datasets from failures, deterministic/LLM/human evals, version comparison and replay | Include; inspect tests/source in full review |
| S12 | [OpenAI Agents SDK tracing](https://openai.github.io/openai-agents-python/tracing/) | Agent tracing implementation | Official SDK documentation | End-to-end traces; typed spans for generations, functions, handoffs and guardrails; sensitive-data control | Include; trace schema and retention need full-review appraisal |

## Method sources retained separately

- [PRISMA 2020](https://www.prisma-statement.org/prisma-2020): reporting and selection-flow requirements.
- Kitchenham and Charters, *Guidelines for performing Systematic Literature Reviews in Software Engineering*: protocol, search, appraisal, extraction, and synthesis design.

## Yield and design implication

The sources are heterogeneous: some are normative standards, some governance guidance, some implementation documentation, and some mature practice. A single undifferentiated SLR would make quality comparison misleading. The pilot supports an evidence mapping study followed by focused reviews for (a) trace/telemetry schemas, (b) provenance and durable execution, and (c) evaluation/incident governance.
