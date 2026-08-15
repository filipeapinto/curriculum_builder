# The reader-level reviewer — and why it is the second fix, not the first

## Why this thread

The pipeline had exactly one reviewer that reads output the way a person
would, and it did not run. All four units record, in `acceptance.json`:

```
"routing_divergence": "USER_AUTHORIZED_IN_SESSION_MODEL; cross-family judge bypassed"
```

with `routing/authoring.json` giving the rationale: *"user authorized the
current in-session LLM as the model worker; no separate API."* The QA report
notes this is documented as `deferred: RT-5` in `policy/checks.v1.yaml` rather
than a silent bug — *"but it means the pipeline's sole subjective gate was
inert for the entire run."*

So there are two questions, and they are different. Would a judge have caught
a JSON dump? Almost certainly. Is a judge the right *fix* for a JSON dump?
The evidence says no.

## Findings

**Where a deterministic alternative exists, current benchmark practice does
not use a judge at all.** *Agents' Last Exam* (arXiv:2606.05405) states it
*"deliberately avoids LLM-as-judge wherever a deterministic alternative
exists."* Implication for this pipeline: a JSON object literal in a
learner-facing section is detectable by a parser, so the primary fix is a
deterministic check. Restoring the judge is still necessary — but if it is the
*only* fix, the pipeline is paying model latency and cost, and accepting model
non-determinism, for a property a regex decides.

**When a judge is genuinely needed, it should be aimed at narrow,
evidence-anchored questions rather than holistic scoring.** Same source: the
minority of workflows that need a judge — *"video clip, game screenshot,
rendered scene, etc"* — are *"scored not by general-purpose holistic prompts
but by narrow, evidence-anchored yes/no probes whose answers code aggregates
into the score."* Implication for this pipeline: the restored reviewer should
ask specific probes against `unit_prose.v1.md` ("does the Explain section
address the learner in the second person?", "is each new term defined at first
use in the body text?"), not "rate this lesson's quality out of ten."

**The division of labour between code checks and judges is explicit in
current production guidance.** Braintrust (26 February 2026):
*"Code-based checks validate structural requirements such as format
compliance, length limits, and schema rules, while LLM-as-a-judge evaluates
qualitative dimensions that code cannot measure reliably,"* and separating the
two *"improves reliability."* Implication for this pipeline: the reviewer
restored at `QA_COMMUNICATION` should be scoped to tone, learner-appropriate
explanation and pedagogical coherence — with rendering conformance already
guaranteed upstream, so no review cycle is ever spent discovering that a
document is unreadable.

**On the user's actual question — is this just intuition?** *Partly, and the
part that is inference should be labelled.* That a competent reviewer reading
L01 would have flagged it is not a research finding; it is obvious, and no
source is needed. What the sources do establish is the non-obvious half: the
judge is the wrong primary control for this defect class, its absence is a
second independent gap rather than the same gap, and a judge cannot be relied
on as the safety net because it is exactly the component that gets bypassed
under routing pressure — as it was here, four times out of four.

## Sources (all fetched and verified to resolve to real, on-topic content)

- "Agents' Last Exam," arXiv:2606.05405 (full text via the HTML rendering) — https://arxiv.org/html/2606.05405v1
- Braintrust Team, "What is an LLM-as-a-judge? When to use it (and when to use deterministic evals)," 26 February 2026 — https://www.braintrust.dev/articles/what-is-llm-as-a-judge

## Discarded

- https://arxiv.org/abs/2606.05405 — the arXiv *abstract* page was fetched first and returned only the high-level summary ("long horizon, economically valuable, real world tasks with verifiable outcomes"), none of the evaluation methodology. Not a dead source: the retry ladder's HTML form (`arxiv.org/html/2606.05405v1`) yielded the full text, and that is the form cited above. Recorded so a later scan goes straight to the HTML form.
- The LLM-as-a-judge-for-software-engineering surveys in this thread's search set (arXiv:2510.24367, arXiv:2505.20854) were not fetched: they concern judging code and SE artifacts, and this thread's claims are already carried by two verified sources. Named here so a later scan can decide differently.
