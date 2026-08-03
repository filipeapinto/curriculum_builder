# Verdict design

Four decisions, made before any code is written, because each one is visible
in the `asserts` string and expensive to change afterwards. Recommendations
arrive with none of them settled — a research scan describes what an agent
should look for, not what authority its verdict carries here.

1. [Deterministic or judged](#1-deterministic-or-judged)
2. [Flags or blocks](#2-flags-or-blocks)
3. [Stage](#3-stage)
4. [Executed or deferred](#4-executed-or-deferred)
5. [Budget, for anything that calls a model](#5-budget-for-anything-that-calls-a-model)

---

## 1. Deterministic or judged

**Default to the cheapest detector that catches the defect the recommendation
names.** Ask what the check would have to be wrong about to miss it.

A judge is warranted when the defect is only visible to a reader — prose that
is fluent but incoherent, a hinge question that does not probe the objective
it claims to. A judge is *not* warranted for anything a parser settles.

The reference scan's own strongest finding makes the point: the root cause of
the failed run was a renderer emitting raw JSON as lesson bodies. That is one
`json.loads()`. Routing it to an LLM judge would spend a model call, add
latency, and introduce a verdict that can be argued with — to learn something
a parser knows for certain. Worse, a judge reading for meaning is
unreliable at spotting shape failures, which is exactly why deterministic
pre-emission checks run first.

This repo has measured the tradeoff and written it down: deterministic checks
beat judges by 1.2x to 7x where both were measured, and the budget recovered
from retiring a twelve-judge panel was explicitly reallocated to deterministic
checks. A judged agent added here is spending that budget back, so it needs
an argument.

**The productive middle:** many judged-looking recommendations decompose into
a deterministic core plus a genuinely subjective remainder. A readability
band is arithmetic. A vocabulary cap is set difference against a declared
list. What is left over — *is this explanation actually clear to a nine-year
old* — is the judge's, and it is a much smaller, cheaper question once the
mechanical part has been answered separately. Split them into two ids that
fail separately, so a failed report names which half broke.

---

## 2. Flags or blocks

**A check blocks only when a wrong verdict cannot manufacture the failure.**

The precedent is stated in the inventory. `TEXT-BLOOM-VERBS` flags and never
blocks, because human raters agree with each other on Bloom level only 46.58%
of the time. A blocking check built on that premise is a coin flip carrying
the force of a schema: it would stop good units at roughly the rate it stops
bad ones, and the run's operator would learn to override it, which costs the
check its authority over the cases where it was right.

Judged agents inherit this problem in a sharper form. The reference scan's
own sources report judge self-preference bias between -38% and +90%, surviving
attempts to hide authorship, and that 17 of 20 tested models show it. A
blocking judge is that bias with veto power.

So the rule of thumb:

| Detector | Verdict |
|---|---|
| Parse, schema, hash, arithmetic against a declared band | **blocks** — a false positive means the artifact really is malformed |
| Set membership against a declared list (vocabulary caps, permitted inputs) | **blocks** — the list is the premise, and the check only reads it |
| Cross-document consistency (does this step reference a step that exists?) | **blocks** — the inconsistency is a fact about the document |
| Model judgement on a named dimension | **flags** — record the score and the disagreement, never the veto |
| Model judgement where the failure is safety-relevant | **flags, and escalates to a named human** — the escalation is the teeth, not the block |

That last row matters for physical-safety recommendations. The instinct is
that safety checks must block. But a safety agent that blocks on an unreliable
verdict trains its operator to bypass it, and a bypassed safety check is worse
than a flag that reaches a human, because it has stopped generating a signal
anybody reads. What blocks is the *absence of the human signoff*, which is a
fact and not a judgement.

**When a check flags, say so in `asserts`.** Otherwise a report quoting it
reads as a pass. The existing wording to imitate: *"This check FLAGS and NEVER
BLOCKS … what is asserted is that the disagreement was reported, never that
the verdict is right."*

---

## 3. Stage

| Stage | Subject |
|---|---|
| `static` | manifests, policy, schemas, prompts — anything true before a run starts |
| `deterministic` | a unit or document, checked mechanically |
| `golden` | rendered artifacts (PDFs, rasterized pages) |
| `logger` | the execution log's own integrity |
| `live-capability` | requires a real model or network call |

The ordering principle is cost: a cheap check that invalidates the subject
should run before anything expensive reviews it. Reviewing prose that is
still a serialized object is compute spent to rediscover a shape failure.

The stage also fixes the release row your id must be advertised under, and
the gate checks stage agreement in both directions.

---

## 4. Executed or deferred

Answer honestly, and the honest answer is often `deferred`.

Today this repo has no renderer, no controller-driven live run, and zero
generated units — which is why most of `policy/checks.v1.yaml` reads
`deferred: RT-5`. A recommendation whose subject is *the rendered lesson
document* has no subject here yet.

But `deferred` and *unbuilt* are different, and the gap between them is where
most of the value sits:

- **Write the detector anyway**, against a hand-written fixture pair. This is
  what the phase-5 gates do, and it is why they were sequenced first: they
  operate on a unit file, so a fixture exercises them with no generator in
  existence. A detector that has never run on anything is a guess about its
  own behaviour.
- **Report the real subject count**, and let it be zero. Every phase-5 gate
  prints `(N units scanned …)` and today N is 0. This is the discipline that
  keeps a fixture-passing gate from being read as coverage of generated work
  — failure `A5`, by name.
- **Name the obligation.** `RT-7` is the id that records *why* the count is
  zero. A gate reporting zero with no `RT-` reference looks like a gate with
  nothing to do.

So a typical new agent lands as: an executing gate (`verified_by: FR-…`)
whose executed assertion is the fixture pair, plus an `RT-` obligation for
the missing production subject. Use `deferred:` in the inventory instead only
when you cannot write a detector at all — when the check needs a renderer's
output, a live model call, or an artifact type nothing in the repo produces.

---

## 5. Budget, for anything that calls a model

`policy/limits.v1.yaml` binds, and the limit that stops a run is named in its
final report.

- `per_lab.max_model_calls: 60` — the whole per-unit budget, authoring
  included. A judged agent's calls come out of this.
- `per_lab.max_revisions: 3` — a generation-revision loop (which several
  recommendations propose, and which is a genuinely stronger design than
  accept/reject) must terminate inside this. A fourth attempt on the same
  failed-check set is the repeat-failure signal.
- `retry.malformed_structured_output: 1` — one retry distinguishes a blip
  from a defect; a second hides the defect.

A model-calling agent also inherits the routing rules: every call carries a
routing decision, `executed_model` must equal `decided_model`, no model is
used for anything deterministic (`SEL-NO-MODEL-FOR-DETERMINISTIC`), and the
judge's family must differ from the generator's — self-preference bias
survives merely hiding authorship, so a different *instance* is not enough.

If a proposed agent does not fit the budget, that is a finding to record in
the dossier, not a number to raise. The limits carry their own rationale
strings, and changing one is a decision about the pipeline rather than a
detail of the agent being added.
