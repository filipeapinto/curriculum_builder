# Content standard: what each area owes the reader

Read this when an area is unfamiliar, when the system is large, or when a
section is coming out generic. Generic prose is the reliable symptom of writing
from expectation instead of from evidence, and it is invisible to every
mechanical check.

Each entry below gives the **reader questions** the section exists to answer,
the **evidence** that usually settles them, and the **recurring shortfall** —
the specific way this section goes wrong when it goes wrong.

## Contents

1. [Purpose and boundary](#1-purpose-and-boundary)
2. [Architecture](#2-architecture)
3. [Graph behavior](#3-graph-behavior)
4. [Node and tool contracts](#4-node-and-tool-contracts)
5. [State and data](#5-state-and-data)
6. [Route contracts](#6-route-contracts)
7. [Models and prompts](#7-models-and-prompts)
8. [Deployment](#8-deployment)
9. [Configuration and release](#9-configuration-and-release)
10. [Security and privacy](#10-security-and-privacy)
11. [Observability](#11-observability)
12. [Operations and recovery](#12-operations-and-recovery)
13. [Limitations and verification](#13-limitations-and-verification)

---

## 1. Purpose and boundary

**Reader questions.** Who uses this and on whose behalf? What outcome is it
responsible for producing? Where does the system start and stop — which
interfaces are its entry and exit points, which external systems does it depend
on or serve, and what is explicitly *not* its job? What assumptions does it
make about its callers and its environment?

**Evidence.** Requests and design records, API definitions and route tables,
policies, the top-level entry code, README and ADRs (treated as *declared*, not
observed).

**Recurring shortfall.** Restating the marketing sentence from the README and
calling it a boundary. A boundary is only useful when it names exclusions:
things a reader would reasonably assume the system handles and it does not.
Those are what cause incidents.

## 2. Architecture

**Reader questions.** What are the major components and what is each
responsible for? What depends on what, and in which direction? How does data
move between them? Where are the trust boundaries — the points where data
crosses from one authority or tenancy to another? How do the parts compose into
something that works?

**Evidence.** Module and package structure, imports and dependency
declarations, interface definitions, wiring or DI configuration, deployment
manifests, architecture records.

**Recurring shortfall.** A component list without a composition story. The
reader can already see the folders; what they cannot see is which components
they may reason about independently and which are coupled in a way that means a
change in one breaks the other.

## 3. Graph behavior

**Reader questions.** Where does execution enter? What are the nodes or stages,
in what order can they run, and what makes the difference? Where does it
branch, loop, join, or terminate? Are loops bounded, and by what? Where does a
human or an external system take over? What happens on failure at each point —
retry, repair, route elsewhere, or stop?

**Evidence.** Graph or workflow definitions, routing prompts, the orchestration
code, tests that exercise paths, execution traces.

**Recurring shortfall.** Inferring formal nodes and edges from the order of
paragraphs in a design document or the order of function definitions in a file.
A node is a node because something dispatches to it. State plainly whether the
graph is **framework-defined** (a declared structure a runtime executes) or
**prompt-orchestrated** (a model choosing the next step at runtime) — these
have completely different failure and debugging characteristics, and readers
who assume the wrong one will look for control in the wrong place.

## 4. Node and tool contracts

**Reader questions.** For each node: what is it for, what does it consume, what
does it produce, what model or prompt behavior does it depend on, which tools
does it call and what side effects do those have? What are its timeouts and
retries? What does it do when it fails, and what does terminal failure mean
here — abort the run, degrade, or hand off?

**Evidence.** Node implementations, prompt files, tool and function-call
definitions, decorator or middleware configuration, tests.

**Recurring shortfall.** Documenting the happy path only, and omitting side
effects. A node that writes a file, sends a message or mutates shared state on
its way to returning a value has a contract that includes those effects; an
operator retrying it needs to know which ones repeat.

## 5. State and data

**Reader questions.** What is carried between stages? Which fields matter,
what types and validation apply, who writes each and who reads it? How does
state persist — checkpoints, database, memory only — and what survives a
crash? When two writers touch the same field, what are the merge or mutation
rules? How is it versioned, redacted, and retained?

**Evidence.** Schemas, typed models, reducers and merge functions, storage and
migration code, checkpointer configuration, retention policy.

**Recurring shortfall.** Listing fields without naming readers and writers.
The debugging question is never "what is in state" — it is "who put that
there", and a field table without provenance cannot answer it.

## 6. Route contracts

**Reader questions.** For each route: where from, where to, what triggers or
guards it, what makes the decision (a condition in code, a model's judgement, a
schema validation result), what state travels along it, what the fallback is
when the guard cannot be evaluated, and what the reader should expect to happen
as a result.

**Evidence.** Graph definitions and conditional-edge functions, routing
prompts, traces showing which routes fire in practice.

**Recurring shortfall.** Documenting forward routes and leaving repair or
error back-edges implicit. The back-edges are the ones an operator meets during
an incident and the ones that turn into infinite loops when their bound is
missing. Give each one its trigger and its bound.

## 7. Models and prompts

**Reader questions.** Which models are used where, and why those? How are they
selected, and what is the fallback when one is unavailable or refuses? What is
each prompt responsible for? Where is structured output required, and what
happens when it fails to parse? Which limits — context, token, rate,
concurrency — actually bind in practice? Which configuration changes model
behavior?

**Evidence.** Prompt files, model configuration and adapters, retry and
fallback code, structured-output schemas, tests.

**Recurring shortfall.** Naming a model version and stopping. The behavioral
facts a maintainer needs are the fallback chain, the parse-failure path, and
which limit is the one that bites — a model name is the least load-bearing
detail in the section and the one most likely to be stale.

## 8. Deployment

**Reader questions.** Which environments exist and how do they differ? How is
this hosted — serverless, containers, a long-running worker, a laptop? What
runs where: services, workers, stores, queues? What is the network shape,
including ingress and egress? How does it scale, and what happens when a node
dies? What external dependencies must be up for it to work at all?

**Evidence.** Infrastructure as code, container and orchestration manifests,
platform configuration, service inventories, CI deployment definitions.

**Recurring shortfall.** Describing the intended topology from an
infrastructure repo without stating whether it is what is actually deployed.
If you did not inspect the running environment, that section is **declared**,
and the label is what stops an operator from acting on it as fact.

## 9. Configuration and release

**Reader questions.** Which parameters matter, what are their defaults and
allowed values, where do they come from and what scope do they apply to? Which
are sensitive? What does each actually change about behavior? Does it reload,
or does it need a restart? How does code get built and promoted to each
environment? What migrations run, which feature flags exist, how do you roll
back, and what is compatible with what?

**Evidence.** Configuration schemas and defaults, environment files (structure,
never values), CI/CD pipelines, deployment files, migration scripts, runbooks.

**Recurring shortfall.** A parameter table with names and defaults but no
behavioral effect. "`MAX_RETRIES: 3`" tells a reader nothing they could not
guess; what they need is what happens on the fourth failure and whether the
retries share a budget with anything else.

## 10. Security and privacy

**Reader questions.** Who can call this and how are they authenticated? What
authorization applies, and which paths are privileged? What classes of data
does it touch, and how is each protected in transit and at rest? Where do
secrets live and how are they delivered to the runtime? What isolates tenants
or environments? What network controls apply? What is audited? What is
retained, for how long? Who owns an incident here?

**Evidence.** Identity and access configuration, network policy, secret
management configuration, the code paths that enforce checks, audit
configuration, written policy, incident runbooks.

**Recurring shortfall.** Inventing controls that sound standard. "All data is
encrypted at rest and in transit, access is role-based, secrets are managed in
a vault" is what a security section looks like when nobody checked. Every
control named here must trace to something you inspected — and a **verified
gap** ("no authorization check exists on the admin route; confirmed at
`api/admin.py:40`") is far more valuable to a reader than an unverified
assurance.

## 11. Observability

**Reader questions.** How do I tell it is healthy? How do I tell a run
succeeded? What is logged, at what level, and with what identifiers — can I
follow one run end to end? What metrics and traces exist, and where are they
displayed? What alerts fire, on what thresholds, to whom? And critically: what
is **not** instrumented, so I know where I will be flying blind?

**Evidence.** Logging and instrumentation code, dashboard definitions, alert
rules, SLO definitions, trace configuration.

**Recurring shortfall.** Omitting the blind spots. A list of what is monitored
implies everything else is fine. The section becomes useful at the moment it
tells an on-call engineer which failure they will have to detect by hand.

## 12. Operations and recovery

**Reader questions.** What must be true before I act, and am I permitted to?
How do I start, stop, or trigger a run safely? What should I see when it works?
What must I never do? When it breaks: how do I triage, what can I retry, what
can I resume, what must be rolled back or restored from backup, and where are
the backups? Who do I escalate to? And under what conditions should I stop
touching it entirely?

**Evidence.** Runbooks, operational scripts and their guards, tests, past
incident records, continuity plans.

**Recurring shortfall.** Procedures with no prohibitions and no stop
conditions. The most valuable lines in an operations section are the ones that
say *do not do this* and *if you see this, stop and escalate* — those are the
ones written from real incidents, and they are the reason the section exists
rather than a link to the scripts.

## 13. Limitations and verification

**Reader questions.** What did you actually look at, and when or at which
version? What did you deliberately not look at? Where did evidence conflict,
and how did you resolve it? What is unknown? Which paths are untested? What
assumptions is this guide standing on? What known risks remain — and what would
make this document wrong?

**Evidence.** The source register from `scripts/source_register.py` and the
verification report from `scripts/verify_doc.py`.

**Recurring shortfall.** Treating this as an appendix nobody reads. It is the
section that makes every other section safe to act on, because it is where a
reader calibrates how much to trust them. Write the invalidation conditions
concretely: "if the graph definition in `graph.py` changes, sections 3 and 6
are stale" beats "this document may become outdated".
