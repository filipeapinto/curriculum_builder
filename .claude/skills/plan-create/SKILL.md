---
name: plan-create
description: Runs a full plan-to-prompt pipeline for a described issue, defect, or improvement — writes an implementation plan, subjects it to independent Critical/High-severity QA, revises it, writes an ordered execution test plan, writes a Claude Code GOAL/TEST/LOOP implementation prompt, and closes with an independent final audit, all logged append-only in plans/<slug>/plans.log.md. This mirrors the structure proven in this repo's plans/provider_correction/ workflow, where the independent QA step caught 4 High-severity defects the plan's own author missed. Use this skill whenever someone describes a bug, defect, regression, or improvement and wants a plan, an implementation plan, a QA'd plan, an execution test plan, or an implementation prompt written for it — for example "write a plan to fix the retry loop dropping errors", "I need an implementation plan for migrating the settings schema", "plan out removing the old routing table with tests", "draft a prompt I can hand to Claude Code for this refactor", "we found a defect where X, can you plan the fix", or "create a plan + QA package for this like we did for provider_correction". Also use it proactively whenever someone is about to hand-write a one-shot implementation prompt for a nontrivial change without an independent QA pass first — an unreviewed, self-approved plan is exactly the failure mode this pipeline exists to catch.
---

# plan-create: plan, QA, test, prompt, audit

This skill packages a workflow, not a template to fill in mechanically. It
produces six artifacts under `plans/<slug>/` for one described issue, defect,
or improvement, in a fixed order, with two points of genuine independent
review built in.

## Why the shape matters

The reference run this skill is modeled on (`plans/provider_correction/`) did
not pass focused QA on the first draft. The same session that wrote the plan
missed four High-severity problems — a required dependency that was actually
disabled, an effort value the target interface couldn't accept, an
underspecified evidence contract, and a deletion rule that would have
destroyed unrelated staged work. A fresh reviewer looking only at the plan and
the repository found all four. That is the whole reason this skill spawns
**separate subagents** for QA and final audit rather than having the
plan's author grade its own work: an author is anchored to the choices it just
made, and a plan that reads as reasonable to the person who wrote it is not
the same thing as a plan that survives someone else checking it against the
actual repository state.

The second thing worth preserving is scope discipline. QA and the final audit
report **Critical and High findings only** — never style preferences or
nice-to-haves — because a reviewer who can flag anything ends up training the
author to defend against noise instead of fixing what would actually break
the implementation.

## Output

Everything lives under `plans/<slug>/`, where `<slug>` is a short kebab-case
name for the issue (e.g. `provider_correction`, `retry-loop-fix`):

```
plans/<slug>/
  <slug>.plan.vN.md              # the implementation plan
  qa/
    plan_qa.vN.md                 # focused Critical/High QA of the plan
    execution_test.plan.vN.md     # ordered test plan for the plan
    final_audit.vN.md             # final standing audit of the whole package
  prompts/
    <slug>.prompt.vN.md           # GOAL/TEST/LOOP implementation prompt
  plans.log.md                    # append-only shared log, every stage
```

Exact section skeletons for all five documents, plus the fixed log entry
template, are in `references/templates.md`. Read it before writing the first
artifact — do not improvise section names, since the final validator and any
future automation over this repo's `plans/` tree depend on them being
consistent across every plan package.

This skill produces **planning artifacts only**. State explicitly in the plan
that its creation does not authorize implementation. Never edit application
code, run migrations, or otherwise implement the change while running this
skill.

## Step 0 — Intake

Get the issue, defect, or improvement description from the user. If it is
already concrete (a specific bug, a named regression, a scoped improvement),
don't stall on process — move to Step 1. Only ask a clarifying question when
the objective or boundary is genuinely ambiguous (e.g. "fix the flaky tests"
with no indication which tests or what flaky means).

Derive:
- `<slug>`: short kebab-case identifier for `plans/<slug>/`.
- `<TITLE>`: human-readable title for document headers.
- `<PREFIX>`: a 2-4 letter uppercase test-id prefix derived from the slug
  (e.g. `provider_correction` → `PC`, `retry-loop-fix` → `RLF`). This prefixes
  every test id in the execution test plan (`<PREFIX>-T00`, `<PREFIX>-T01`, ...).

Check whether `plans/<slug>/` already exists. If it does, this is a
**continuation** of an existing package, not a fresh one: read
`plans.log.md` end-to-end to learn what stage it last reached, and resume from
there — append new log entries and, where a document needs revision, bump to
the next `vN` only if you are materially re-scoping; an in-place revision (see
Step 3) keeps the same version.

## Step 1 — Initialize the workspace and log

```bash
python3 <skill-dir>/scripts/init_plan_workspace.py plans/<slug> \
  --title "<TITLE>" --objective "<one-paragraph objective>"
```

This creates `plans/<slug>/qa/` and `plans/<slug>/prompts/`, and writes
`plans.log.md` with the header, objective, and entry template — but only if
`plans.log.md` doesn't already exist. It never overwrites an existing log.

## Step 2 — Author the plan

Write `plans/<slug>/<slug>.plan.v1.md` following the `plan` skeleton in
`references/templates.md`. The parts that matter most:

- **Exact work** as an ordered, numbered list of concrete steps — not prose
  paragraphs. Someone implementing this later should be able to work through
  it top to bottom without re-deriving the approach.
- **Verification sequence** and **Acceptance criteria** that are checkable
  against the repository, not aspirational ("tests pass" is checkable; "the
  code is cleaner" is not).
- **Stop conditions and result**, naming the exact result file the
  implementation must write and the log it must append to.

If the issue depends on something outside your control (a disabled
dependency, a missing credential, an unreleased API), say so as an explicit
prerequisite with a fail-fast check as step 0 of "Exact work" — don't write a
plan that quietly assumes the blocker is already resolved.

Append a log entry (`scripts/append_log.py`, see Logging below) recording
that the plan was authored.

## Step 3 — Independent focused QA

Spawn a fresh `Agent` (subagent_type `general-purpose`) that has **not** seen
this conversation. Give it only:

- the path to `plans/<slug>/<slug>.plan.v1.md`,
- repository access to verify claims against real files, configs, and policy,
- instructions to act as a focused reviewer reporting **Critical and High
  findings only**, each with Evidence / Impact / Minimal required remediation,
  and a verdict line `**APPROVED — 0 Critical, 0 High.**` or
  `**CHANGES REQUIRED — <C> Critical, <H> High.**`.

Tell it explicitly not to comment on style, phrasing, or anything it cannot
back with evidence from the plan or the repository — and push it past
reading. The reviewer that catches real defects is the one that applies the
plan's proposed change to a scratch copy (e.g. `/tmp/<slug>qa/`) and actually
runs the affected tests, greps, or gates against it, rather than reasoning
about the diff in the abstract. A plan step that "should work" and a plan
step that was verified to work are different claims; tell the reviewer to
make the second one wherever it plausibly can. See the `plan_qa` skeleton in
`references/templates.md` for the exact document shape it should produce at
`plans/<slug>/qa/plan_qa.v1.md`.

Append a log entry recording the QA pass and its verdict.

## Step 4 — Revise until clean, bounded by convergence

If the verdict is `CHANGES REQUIRED`, revise `<slug>.plan.v1.md` **in place**
addressing every Critical and High finding without expanding scope beyond
what the finding requires — do not use QA as an excuse to redesign parts of
the plan that passed review. Append a log entry describing exactly what
changed and why (cite the finding numbers).

Then repeat Step 3 with another fresh subagent, and keep going as long as
it's genuinely converging: track the Critical+High count round over round.
A rigorous reviewer against a nontrivial plan in a large, often-dirty
repository can easily find real, *different* defects in round 2 that a
narrower round-1 pass had no way to see — that is convergence working, not
a sign of a broken plan, and stopping after a fixed two rounds regardless of
trend cuts the loop off exactly when it's paying off. So: continue while
each round's count is strictly lower than the previous round's, up to a
hard ceiling of **five** rounds. Stop immediately, short of the ceiling, if
a round's count does not decrease — that plateau (or regression) means
revisions aren't converging and another round of the same treatment won't
help. Whichever way it stops, if the plan still isn't clean, halt the whole
pipeline here, report the outstanding findings and the round-by-round count
to the user, and do not proceed to Steps 5-7 — a test plan and prompt built
on a plan with open Critical/High findings inherit those defects. This
mirrors the reference run's rule that no artifact claims success it hasn't
earned; it does not mean giving up the moment progress is still visible.

## Step 5 — Author the execution test plan

Write `plans/<slug>/qa/execution_test.plan.v1.md` using the
`execution_test_plan` skeleton in `references/templates.md`. Ordered tests,
each with a `<PREFIX>-T<NN>` id starting at `T00`, covering in sequence:
a read-only baseline capture, any fail-fast/prerequisite check from the
plan's step 0, one test per implementation phase in the plan, negative/
regression cases, and a final audit-and-pass-rule section. If the plan has an
external blocker, add an "Availability stages" section stating exactly which
test ids can run now versus only after the blocker clears — don't write tests
that silently assume the blocker is gone.

Append a log entry.

## Step 6 — Author the implementation prompt

Write `plans/<slug>/prompts/<slug>.prompt.v1.md` using the `prompt` skeleton
(`GOAL` / `TEST` / `LOOP`) in `references/templates.md`:

- **GOAL** restates the plan's scope and boundary and cites
  `plans/<slug>/<slug>.plan.v1.md` by path — it does not re-derive the plan
  from scratch in different words.
- **TEST** enumerates every test id from the execution test plan, in the same
  order, citing `plans/<slug>/qa/execution_test.plan.v1.md` by path.
- **LOOP** describes the repair-and-rerun discipline: on a test failure, fix
  only the in-scope artifact, rerun that test and anything downstream of it,
  and continue until every applicable test passes. State the stop conditions
  from the plan and the exact result-file and log-append requirements.

Append a log entry.

## Step 7 — Independent final audit

Spawn another fresh `Agent` (subagent_type `general-purpose`) with access to
the whole `plans/<slug>/` directory and the repository. Ask it to check the
package as a whole, not any single document in isolation:

- every stage has a log entry (complete participation record),
- every Critical/High finding from Step 3 was actually remediated,
- the prompt's TEST section and the execution test plan reference the exact
  same test ids in the exact same order,
- the plan's stated scope, the test plan's coverage, and the prompt's GOAL
  agree with each other,
- any remaining blocker is stated consistently everywhere it appears.

It writes `plans/<slug>/qa/final_audit.v1.md` using the `final_audit`
skeleton, with a verdict line `**PASS — 0 Critical, 0 High remaining.**` or
`**CHANGES REQUIRED — <C> Critical, <H> High remaining.**`, plus a
`## Remaining blocker` section when one exists.

Append a log entry. If `CHANGES REQUIRED`, repair the specific stage the
audit points at (not a full restart) and rerun the audit once more with
another fresh subagent. If it still doesn't pass after that second attempt,
stop and report the open findings to the user rather than shipping a package
that hasn't earned a clean audit.

## Step 8 — Validate mechanically

```bash
python3 <skill-dir>/scripts/validate_plan_package.py plans/<slug>
```

This checks, without needing to re-read every document by eye: all six
artifacts exist for the latest version, required sections are present in
each, both verdict lines are well-formed, a `PASS`/`APPROVED` verdict
actually carries `0 Critical, 0 High`, and every test id in the prompt's
`TEST` section has a matching entry in the execution test plan (and vice
versa — no orphans on either side). Fix anything it reports; it is checking
exactly the kind of drift that a distracted revision pass introduces.

## Step 9 — Report

Tell the user, concisely: where the package lives, the final QA and audit
verdicts, and — if the plan has an external prerequisite — that the package
is complete but implementation is blocked until the prerequisite clears. This
skill hands off a ready-to-run prompt; it does not execute it. Running
`plans/<slug>/prompts/<slug>.prompt.v1.md` is a separate, later action.

## Logging

Append to `plans/<slug>/plans.log.md` after every stage, not reconstructed
at the end — the log is what Step 7's auditor checks for a complete
participation record, and a log written from memory afterward tends to omit
exactly the revision that mattered.

```bash
python3 <skill-dir>/scripts/append_log.py plans/<slug>/plans.log.md \
  agent="plan_author" \
  action="Authored implementation plan v1 covering <short summary>." \
  paths="plans/<slug>/<slug>.plan.v1.md" \
  evidence="<what grounds this — repo inspection, prior QA finding, etc.>" \
  issues="None pending critical/high QA."
```

Entries are append-only: never edit or remove a prior entry, including your
own. A correction is always a new entry, exactly as the reference log did
when it corrected its own initial naming mistake in a later entry rather than
rewriting the first one.
