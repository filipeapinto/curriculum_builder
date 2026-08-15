# State-of-the-art documentation for a complex runtime

**Research date:** 2026-08-15  
**Scope:** techniques for documenting a contract-first, graph-oriented runtime with
state transitions, model/tool calls, checkpoints, review gates, generated artifacts,
and operational controls. This is research and an adoption recommendation, not a
claim that every proposed capability already exists in this repository.

## Executive conclusion

The modern answer is not one comprehensive design document. It is a **versioned
documentation system** made of small, linked views, where each view has an owner,
source evidence, and a freshness rule. The important split is:

| Layer | Purpose | Source of truth |
| --- | --- | --- |
| Executable facts | State machine, schemas, policy, API/tool contracts, infrastructure, tests, telemetry | Code and versioned structured artifacts |
| Human explanation | Reader-oriented architecture, journeys, decision rationale, runbooks, diagrams | Documentation derived from and linked to executable facts |
| Operational evidence | What an actual version did, including errors and timing | Immutable run receipts, traces, logs, dashboards, and test reports |

For this runtime, use a **C4 + behavioral views + contracts + ADRs + observed
execution** approach. C4 gives readers progressive architectural zoom; behavioral
views explain state transitions and failure/retry paths; typed contracts make claims
testable; ADRs preserve why; and traces/run receipts distinguish declared behavior
from behavior that actually executed.

This fits the repository's existing direction: `policy/controller.v1.yaml` already
defines code-owned states, terminal states, checkpoint rules, and model boundaries;
`schemas/` and `policy/` can be treated as the canonical fact model; and the current
documentation specification correctly distinguishes declared, observed, inferred,
and unknown graph behavior. The root `readme.md` says live-runtime capabilities are
still deferred, so they should be documented as **specified** until verified run
evidence exists.

## What is state of the art in practice

### 1. Multiple focused views, not a mega-diagram

The [C4 model](https://c4model.com/) uses hierarchical system-context, container,
component, and code views, with dynamic and deployment diagrams as supporting views.
Its guidance explicitly says not every level is necessary; context and container
views are enough for many teams. Pair it with [arc42](https://docs.arc42.org/), a
well-established structure for the accompanying narrative: goals, constraints,
context, solution strategy, building blocks, runtime behavior, deployment, cross-cutting
concepts, decisions, quality requirements, risks, and glossary.

For a runtime, use these six views:

1. **System context (C4):** users, operator, curriculum/domain inputs, model
   providers, source/retrieval services, renderers, output storage, and all trust
   boundaries.
2. **Runtime topology (C4 container/deployment):** controller, workers, schema
   validators, checkpoint store, queues if any, telemetry pipeline, policy/config
   sources, and environment boundaries.
3. **State-machine view:** all states, valid transitions, terminal states, guards,
   retry limits, resumability, and which actor owns each transition. Generate this
   from `policy/controller.v1.yaml` whenever feasible.
4. **Critical-path sequence views:** one successful run and one representative
   failure/recovery run. Show calls, durable writes, checks, human gates, and
   side effects in time order.
5. **Data lineage and contract view:** state fields, readers/writers, validation,
   classification, retention/redaction, checkpoint boundaries, and artifact hashes.
6. **Trust and operations view:** identity, permitted egress, secret classes,
   configuration sources, alert paths, recovery, and escalation ownership.

Each visual should state its **scope, source revision, evidence class, and date**.
For example: “Declared controller graph, derived from
`policy/controller.v1.yaml` at commit `<sha>`” is different from “Observed path
from run `<id>`.” This prevents a polished diagram from becoming unearned evidence.

### 2. Architecture-as-code and documentation-as-code

Keep diagrams, contracts, and prose in Git beside the runtime. Render diagrams in
CI and make broken links, invalid diagrams, schema-reference errors, and stale
generated views fail the documentation build. Backstage's
[TechDocs guidance](https://backstage.io/docs/features/techdocs/creating-and-publishing/)
illustrates the prevailing docs-as-code pattern: Markdown near the source, a
deterministic site build, and CI/CD publication. Its recommended operational setup
builds documentation in CI/CD rather than on demand.

Prefer a simple source/render pattern:

```text
policy + schemas + code + test metadata + IaC + telemetry conventions
                         │
                         ├── checked generators ──> diagrams / contract tables
                         └── human authors ───────> explanations / runbooks / ADRs
                                                     │
                                                     └── CI validation + static site
```

Use Mermaid, PlantUML, D2, or a C4-oriented DSL only if their source stays in the
repository and is rendered by CI. The tool is secondary; reviewable source and
repeatable rendering are the key properties. Do not attempt to generate narrative
claims directly from code without human review: code reveals structure well but not
intent, operational trade-offs, or undocumented dependency assumptions.

### 3. Contracts are documentation and executable checks

For every boundary, publish a contract that a person can read and a machine can
validate. This is the highest-value technique for runtimes that mix deterministic
control with probabilistic model outputs.

| Boundary | Documentation artifact | Automated proof |
| --- | --- | --- |
| State and checkpoints | Versioned schema, ownership/lineage table, migration and redaction policy | Schema validation, migration tests, resume tests |
| State transition | Transition table with trigger, guard, effects, retry and terminal outcome | State-machine/transition tests; reachability checks |
| Model or worker invocation | Input/output schema, allowed tools, timeout, retry, idempotency, evaluation/repair policy | Contract tests and captured invocation receipts |
| HTTP APIs | OpenAPI description plus examples and error semantics | Spec linting and contract tests |
| Events or queues | Event schema and producer/consumer ownership | Schema compatibility and integration tests |
| Configuration | Typed config reference: name, type, default, scope, source, sensitivity, reload effect | Startup validation and configuration tests |
| Policy/gate | Rule, owner, severity, evidence required, bypass/exception process | Gate result recorded per run |

[OpenAPI](https://spec.openapis.org/oas/) is a mature machine-readable contract for
HTTP interfaces. Use its current 3.1.x specification for any exposed HTTP API; do
not replace it with a prose endpoint table. For internal schemas, retain JSON Schema
or the language's typed model as the authoritative artifact, and generate a concise
reader table from it.

### 4. Decision records preserve the reasoning that code cannot

Keep lightweight Markdown ADRs for decisions that are expensive to reverse:
controller ownership, checkpoint semantics, routing authority, model/tool boundaries,
data retention, evaluation gates, deployment patterns, and telemetry fields. The
[MADR project](https://adr.github.io/madr/) provides a maintained Markdown ADR
template with status, context/problem, considered options, and decision outcome.

An ADR should be short and immutable after acceptance; supersede it with a new ADR
rather than silently rewriting history. Link each ADR to the affected policy/code,
test, and operational consequence. Avoid ADRs for ordinary implementation detail.

### 5. Observability is live runtime documentation

Static documents describe intent; traces and receipts describe behavior. Instrument
the controller and worker boundaries so operators can reconstruct a run without
reading source. Use one correlation/run ID from intake through terminal decision;
record state entered/exited, attempt, selected worker/model, policy revision,
input/output hashes (not raw sensitive content), duration, error class, retry,
checkpoint reference, and terminal reason.

[OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
standardize names, types, and meanings for traces, metrics, logs, and resources,
which makes telemetry easier to correlate across components. Its trace model defines
spans as operations in and between systems, including client/server and
producer/consumer relationships. For model-enabled paths, the
[GenAI conventions](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/)
cover concepts such as agent, conversation, model, and input/output messages; they
also warn that message content may contain PII. Make content capture opt-in,
redacted, access-controlled, and retention-limited.

Build two documentation views from telemetry:

- **Declared vs. observed coverage:** which specified transitions have been observed
  for which version and test/run cohort; explicitly list unobserved transitions.
- **Run dossier:** a human-readable receipt for one run, linking input manifest
  digest, configuration/policy revisions, transition timeline, artifacts, gate
  results, and terminal outcome.

These are much more useful during incident response than an architecture diagram
alone.

### 6. Documentation needs operations and governance, not just design

Every document family should have an owner, review trigger, and service level for
freshness. A compact docs register is enough:

| Artifact | Owner | Update trigger | Validation |
| --- | --- | --- | --- |
| Architecture and topology | Runtime maintainer | Component, dependency, deployment, or trust-boundary change | Diagram build + architecture review |
| State and data contracts | Controller/schema owner | Schema, transition, checkpoint, or migration change | Contract/transition tests |
| ADRs | Decision maker | Reversible-cost or cross-team decision | PR review and linked implementation |
| Runbooks | On-call/operations owner | Alert, incident, recovery, or deployment change | Exercised drill or incident review |
| Observability dictionary | Platform/runtime owner | Span/metric/log attribute change | Telemetry schema/lint review |
| Security/data-flow view | Security and runtime owners | Egress, identity, data-classification, or retention change | Threat-model review |

Make changes to a contract, state, external interface, deployment, or runbook require
the related documentation update in the same pull request. This is more reliable
than a periodic request to “keep docs current.”

## Recommended information architecture for this repository

Create the following when the runtime is implemented; start the first four now using
the declared contracts and clearly label them **specified**.

```text
docs/runtime/
  index.md                         # reader entry point and evidence/freshness policy
  architecture/
    context.md                     # C4 level 1
    topology.md                    # C4 container + deployment/trust boundaries
    state-machine.md               # generated declared transitions + interpretation
    critical-journeys.md           # happy path, failure, retry, resume
  contracts/
    state-and-checkpoints.md
    workers-models-tools.md
    configuration.md
    interfaces.md
    data-lineage-and-retention.md
  decisions/                       # ADRs; one immutable Markdown file per decision
  operations/
    runbook.md
    incident-triage.md
    recovery-and-resume.md
    observability.md
  evidence/
    declared-vs-observed.md        # generated coverage summary; no raw secrets/PII
    run-dossier-template.md
```

Use `docs/research/` for sources and evaluations such as this report; use
`docs/runtime/` for the maintained reader-facing system documentation. Preserve the
repository's source-of-truth rule: policies, schemas, code, tests, and receipts are
authoritative; narrative explains and links to them.

## A pragmatic adoption sequence

1. **Now — establish the declared architecture.** Add a documentation index,
   context/topology diagram, state-machine table/diagram, contract index, and an
   evidence legend. Generate the state graph from the controller policy if possible.
2. **Before the first live model call — close contracts.** Define state/checkpoint
   compatibility, worker/tool interface schemas, typed configuration reference,
   egress/trust boundaries, redaction rules, and ADRs for irreversible decisions.
3. **With the runtime — make behavior observable.** Emit correlated transition and
   invocation telemetry; write append-only run receipts; generate declared-vs-observed
   transition coverage; keep sensitive payload content out by default.
4. **In CI and operations — prevent drift.** Validate schemas and diagrams, test
   documented transitions and recovery procedures, publish docs with the release,
   and update runbooks after every relevant incident.

## Quality bar

A document set is good enough when a new engineer can explain the system boundary,
state ownership, allowed transitions, data movement, failure/recovery behavior, and
current evidence status; and when an authorized operator can identify a failed run,
find its receipt/trace, decide whether retry is safe, and escalate appropriately.

It is not good enough if it contains a single dense architecture diagram, only
happy-path prose, screenshots without sources, generic security language, raw
telemetry with no interpretation, or claims that specified behavior has executed
without a test/run receipt.

## Sources consulted

- [C4 Model — overview](https://c4model.com/) and [diagram guidance](https://c4model.com/diagrams)
  — hierarchical static, dynamic, and deployment views; accessed 2026-08-15.
- [arc42 documentation](https://docs.arc42.org/) — architecture documentation
  structure and examples; accessed 2026-08-15.
- [Backstage TechDocs: creating and publishing](https://backstage.io/docs/features/techdocs/creating-and-publishing/)
  and [architecture](https://backstage.io/docs/features/techdocs/architecture/)
  — docs-as-code and CI/CD publishing practice; accessed 2026-08-15.
- [OpenAPI Specification](https://spec.openapis.org/oas/) — current 3.1.x
  machine-readable HTTP interface contract; accessed 2026-08-15.
- [MADR](https://adr.github.io/madr/) — Markdown ADR templates and decision-record
  conventions; accessed 2026-08-15.
- [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/),
  [trace conventions](https://opentelemetry.io/docs/specs/semconv/general/trace/),
  and [GenAI attributes](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/)
  — standardized telemetry semantics and GenAI content sensitivity warnings;
  accessed 2026-08-15.

