# Unit prose — v1

A companion of `meta_prompt/curriculum.prompt.v1.md`. It carries what a schema cannot:
how a unit reads. It is not contract text and it never decides a value — where the
schema has a field, the schema wins.

This file replaces `component_lab_template.v1.md`, which was titled *"Component-Oriented
Electronics Lab Template"* and wrote its rules about one subject. Everything below is
about a learner and a page, and nothing below is about what is being taught. That is
`G4` in `plans/simplification/plan/simplification.plan.v3.md` §2.

## Purpose

A unit teaches one thing. Applications and mini-projects show what that thing is good
for; they do not replace it as the organising principle.

```text
The subject
  → what it is
  → how to recognise and orient it
  → how it behaves
  → what it is used for
  → the core activity
  → the problems it can solve
```

## Required unit structure

The schema fixes which blocks exist. This fixes how they read.

**Title.** The subject is the title. State its job in one sentence the learner can
repeat back.

**What is it for.** Start with the need it meets, before describing how it works
inside. A learner who does not know why something exists has nothing to attach the
mechanism to.

**Meet it.** Give the learner-facing name and the technical name, what it looks like,
how to tell which way round it goes or that it has no orientation, and which of its
parts matter here. Exact identification comes from a verified photograph or a
deterministic render, never from a generated image.

**How it works.** Scientifically honest at the learner's level. Short paragraphs, no
slogans, no metaphor-only explanation. Introduce new technical words sparingly — the
cap is a premise in `policy/calibration.v1.yaml` and is never restated here — and define
each one where it is first useful.

**The core activity.** One physical action per numbered step. State the expected
observation before it happens, and give one safe "not yet" outcome with its first check.
Anything the learner must not do alone is stated as what the adult does, not as a
warning label.

**The assembly authority.** Whatever the domain's map is, it is rendered from the
domain's own data and never drawn by a generative model. Prose steps and the map are the
same data twice, so they cannot disagree.

**Record what happened.** Say exactly what to look for, hear, count or measure. Give the
learner somewhere to put it: a small evidence table, a drawing prompt, a tick box, or an
adult-read reading.

**Explain it.** Return to the mechanism, using only words already introduced.

**What it solves.** Two or three real applications of this subject — applications, never
replacement themes.

**Troubleshoot.** A calm table: what you notice, the likely reason, the safe first
check. Presented as normal practice rather than as failure.

**Adult verification.** Kept visibly separate from everything the learner reads. What
the adult confirms, what they measure, and what they sign off before the activity is
released.

## Visual standard

Visuals support the written teaching; they never replace it.

Exact fact — labels, positions, orientations, values, settings — comes only from a
verified photograph or a deterministic render. A generated image may carry context,
mechanism illustration, observation support and polish, and may carry no exact fact at
all. Every visual sits with the text it explains rather than floating free, and every
one ships with a receipt whose hash resolves to the artifact actually shipped.

## Child-language rules

- One idea per short paragraph, and a new word defined beside its first useful visual.
- A concrete object and a concrete action before any abstract term or symbol.
- Never rely on a warning alone: say what the learner does, what the adult does, and
  why.
- Keep adult technical checks visibly separate from the learner's text.
- Write to the reading band `policy/calibration.v1.yaml` declares. Text well under the
  band is as wrong as text over it: it teaches less than the learner can take.

## Safety baseline

What is hazardous depends entirely on the subject, so the specifics belong to the
curriculum and are stated in its own calibration and enforced by its own verifier. What
is engine-wide is the shape of the rule:

- The learner never handles the part of the activity the curriculum marks adult-only.
  An adult does, and signs off before the activity is released.
- Use only what the curriculum's calibration permits and its evidence verifies. Never
  infer a permitted input from a resemblance, a colour or a generic description.
- Make the activity safe before changing it, and say so as a step rather than as a
  caution.
- Stop if something behaves in a way the unit did not predict.
- A safe "not yet" result is a legitimate outcome and is written as one.
