# Document skeletons

Exact section shapes for the six artifacts under `plans/<slug>/`. Use these
headers verbatim (same casing, same `##`/`#` level) — `scripts/validate_plan_package.py`
and Step 8 of SKILL.md look for them by name.

## plans.log.md

`scripts/init_plan_workspace.py` writes this for you; shown here so you know
what an entry must look like when you append one.

```markdown
# <TITLE> Planning Log

Append-only record for the planning, QA, test-planning, and implementation-prompt
workflow. Existing entries must not be edited or removed; later corrections are
new entries.

## Objective

<one paragraph: what this plan package exists to fix or build>

## Entry template

​```text
### <UTC timestamp> — <agent/task>
- Action: <work performed>
- Paths touched: <paths, or none>
- Evidence/decision: <verification or decision rationale>
- Issues: <critical/high findings, blockers, or none>
​```

## Entries

<entries appended here, oldest first, never edited>
```

## `<slug>.plan.vN.md`

```markdown
# <TITLE> — Implementation Plan vN

## Status and objective

Planning only; no implementation is authorized by this document's creation.

<what this plan does, in a short paragraph — the change, its boundary, and
what it explicitly does not do>

## Exact work

### 0. <fail-fast prerequisite check, if the plan depends on something outside
your control — omit this subsection entirely if there is no such dependency>

### 1. <first ordered step>

- <concrete, checkable sub-actions>

### 2. <next step>

...

## Verification sequence

1. <first check to run, and what "pass" means>
2. ...

## Acceptance criteria

- <checkable condition>
- <checkable condition>

## Stop conditions and result

Stop on <name the specific collision/ambiguity/blocker conditions that should
halt implementation rather than being worked around>.

Write `plans/<slug>/<slug>.result.vN.md` with <what it must record: baseline,
changed/deleted paths, test results, remaining failures>. Append the execution
outcome to `plans/<slug>/plans.log.md`.
```

Add an `## Architectural end state` section between "Status and objective"
and "Exact work" only when the plan changes how a system is structured, not
for a narrow bug fix — it should state the numbered invariants the change
must leave true, the way the reference plan stated who owns orchestration,
who owns acceptance, and where independent review comes from.

## `qa/plan_qa.vN.md`

```markdown
# <TITLE> Plan vN — Focused QA

## Verdict

**<APPROVED | CHANGES REQUIRED> — <C> Critical, <H> High.** <one-paragraph
summary of what's sound and, if applicable, what's blocking>

## Findings

### 1. <Critical | High> — <short finding title>

**Evidence.** <what in the plan or repository shows this>

**Impact.** <what breaks if this ships unfixed>

**Minimal required remediation.** <the smallest change that resolves it —
not a redesign>

### 2. ...
```

If the verdict is `APPROVED`, the `## Findings` section states plainly
`No Critical or High findings.` — do not pad it with low-severity notes
dressed up as findings; if you have a genuine low-severity observation worth
recording, put it under a separate `## Observations (non-blocking)` section
so it can never be confused with something that gates the verdict.

## `qa/execution_test.plan.vN.md`

```markdown
# <TITLE> — Execution Test Plan vN

## Purpose and boundary

Test `plans/<slug>/<slug>.plan.vN.md` without implementing it. <where
evidence goes, and what the tests must never do to the repository or user's
existing work>

## Availability stages

<only if the plan has an external prerequisite: which test ids can run now,
which are blocked until the prerequisite clears, and which are the one live
test that proves the prerequisite actually works — omit this section entirely
when there is no such blocker>

## Ordered tests

### <PREFIX>-T00 — <name>

<what it captures or checks, and what "pass" requires>

### <PREFIX>-T01 — <name>

...

## Final audit and pass rule

<what must be true across all tests for the package to be considered passing,
and what a partial or blocked state must honestly report instead of a false
success>
```

Test ids are sequential starting at `T00`, sharing one `<PREFIX>` derived from
the slug. Every id used here must also appear, in the same order, in the
`TEST` section of `prompts/<slug>.prompt.vN.md` — that agreement is what
`scripts/validate_plan_package.py` checks mechanically.

## `prompts/<slug>.prompt.vN.md`

```markdown
# GOAL

<restate the plan's scope and boundary, citing `plans/<slug>/<slug>.plan.vN.md`
by path. State any prerequisite that must hold before any repository mutation,
and what to do if it doesn't (stop, don't fall back to a workaround).>

# TEST

Use the ordered tests in `plans/<slug>/qa/execution_test.plan.vN.md`. Run
<PREFIX>-T00 through <PREFIX>-T<last>, strictly in order:

1. <PREFIX>-T00: <one line on what it proves>
2. <PREFIX>-T01: <one line on what it proves>
...

# LOOP

<the repair-and-rerun discipline: on a test failure, fix only the in-scope
artifact, rerun that test and everything downstream of it, and continue until
every applicable test passes. Restate the plan's stop conditions. Name the
exact result file to write and the log to append to. State plainly that
completion may only be claimed when every applicable test has passed.>
```

## `qa/final_audit.vN.md`

```markdown
# <TITLE> Planning Workflow — Final QA Audit vN

## Verdict

**<PASS | CHANGES REQUIRED> — <C> Critical, <H> High remaining.** <one
paragraph: is the package internally aligned, are prior findings actually
remediated, is anything left honestly reported as blocked>

## Evidence

- **Complete participation log:** <does every stage have a log entry>
- **Findings remediated:** <does every Critical/High from plan QA trace to an
  actual change>
- **Prompt alignment:** <do GOAL/TEST/LOOP agree with the plan and the
  execution test plan>
- **Change scope:** <does the package touch only what it claims to touch>

## Remaining blocker

<only if one exists: the exact external prerequisite that must clear before
implementation can proceed, and why that's an execution prerequisite rather
than a defect in the planning package>
```
