# <System name> — architecture and operations guide

> **Audience:** <design reviewers / maintainers / authorized operators — be specific>
> **Evidence basis:** <repo @ git rev, environment inspected or not, traces available or not>
> **Generated:** <date> · **Invalidated by:** <the concrete changes that make this stale>

<!--
This is a skeleton, not a form. Delete any section that does not apply and say
why in Limitations. Expand the sections where this system's real complexity
lives — a guide with thirteen equal-sized sections has usually been filled in
rather than written.

Evidence labels: mark sections, rows, diagram elements and load-bearing claims
as [declared], [observed], [inferred] or [unknown]. Do not label every
sentence; label wherever a reader might otherwise assume something was verified
that was not.
-->

## 1. Purpose and boundary

What the system is for, who uses it, what it owns, where it starts and stops,
what it explicitly does not do, and what it assumes about its environment.

**In scope:** …
**Out of scope:** …
**Assumptions:** …

## 2. Architecture

<!-- Architecture overview diagram here if the system is complex enough that a
reader needs orientation before detail. Every visual needs: title, takeaway,
scope, evidence status, and a text or tabular equivalent below it. -->

| Component | Responsibility | Depends on | Trust boundary | Evidence |
|---|---|---|---|---|
| | | | | |

## 3. Graph behavior

State plainly whether the graph is **framework-defined** or
**prompt-orchestrated**, then: entry points, nodes/stages, branches, loops and
their bounds, joins, termination conditions, human or external handoffs, and
failure paths.

## 4. Node and tool contracts

| Node | Purpose | Inputs | Outputs | Tools / side effects | Timeout · retries · repair | Failure semantics | Evidence |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## 5. State and data

| Field | Type | Validation | Written by | Read by | Persistence | Merge rule | Retention | Evidence |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

What survives a crash, what does not, and how state is versioned and redacted.

## 6. Route contracts

| From | To | Trigger / guard | Decision mechanism | State transferred | Fallback | Bound (for back-edges) | Evidence |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## 7. Models and prompts

Model roles and selection, fallback chain, prompt responsibilities, structured
outputs and their parse-failure path, the limits that actually bind, and the
configuration that changes behavior.

## 8. Deployment

Environments and how they differ, hosting model, runtime topology, services and
workers and stores and queues, network shape including ingress and egress,
scaling and HA behavior, external dependencies required for operation.

## 9. Configuration and release

| Parameter | Default | Allowed | Source · scope | Sensitive | Behavioral effect | Reload | Evidence |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

Build and promotion path, migrations, feature flags, rollback procedure,
compatibility constraints.

## 10. Security and privacy

Identity, authentication, authorization, privileged paths, data classes and
their protection, secrets handling (where they live and how they reach the
runtime — never their values), isolation, network controls, audit, retention,
incident ownership.

**Verified gaps:** <controls a reader might assume exist and that do not, each
with the location you confirmed it at. These are more valuable than the
controls that do exist.>

## 11. Observability

Health and success signals, logs and their run identifiers, metrics, traces,
dashboards, alerts and thresholds and their owners.

**Blind spots:** <what is not instrumented, and therefore what an operator will
have to detect by hand.>

## 12. Operations and recovery

**Prerequisites and permitted roles:** …
**Start / stop / trigger:** …
**Expected output when healthy:** …
**Prohibited actions:** …
**Triage:** …
**Retry · resume · rollback · restore:** …
**Escalation:** …
**Stop conditions —** if you see any of these, stop and escalate rather than
continuing: …

## 13. Limitations and verification

**Sources inspected**

<!-- Paste the table from scripts/source_register.py --md, or link the register. -->

**Excluded from inspection:** … (and why)
**Conflicts found and how resolved:** …
**Unknowns:** …
**Untested / unexercised paths:** …
**Checks performed:** <deterministic gates run, and what a reader still had to judge>
**Unresolved gaps:** …
**What would invalidate this guide:** …
