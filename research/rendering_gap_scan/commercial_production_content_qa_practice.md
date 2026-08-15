# What shipping platforms actually do before generated lessons reach learners

## Why this thread

Papers describe what is possible; platforms that ship generated lessons to
real learners reveal which controls survived contact with users. This run
shipped four labs to a "shipped PDF" state with `"terminal_state": "ACCEPTED"`
and a `"draft_status": "pending downstream human review"` — a status that names
a human step without defining, gating on, or recording one. The documents
themselves carry the same line: *"Draft pending downstream human review."*
(`L01.md:3`). That is the boundary worth comparing against production practice.

## Findings

**A shipping platform that generates lesson content at scale still places a
human editorial gate immediately before release, and says so explicitly.**
Duolingo's own engineering/product blog, "How Duolingo uses AI to create
lessons faster," describes Learning Designers who *"can still make edits
before they go into the app,"* making *"tweaks for naturalness, learning value,
and appropriate vocabulary,"* and states plainly that *"our Spanish teaching
experts always have the final say."* Implication for this pipeline: the
`"pending downstream human review"` status is the same idea with none of the
mechanism. Nothing in the run blocks on that review, records who performed it,
or prevents `ACCEPTED` without it — so it functions as a disclaimer rather than
a gate.

**Generation is templated and parameterised rather than free-form, which is
what makes a human gate affordable.** Same source: *"Think of the prompt as
kind of like a Mad Lib for generating Duolingo lessons,"* with fixed
per-exercise-type instructions plus variable per-exercise parameters. The
ZenML LLMOps Database entry summarising the same Duolingo material corroborates
this, describing a *"'Mad Lib' style prompt template system"* whose parameters
include vocabulary targets, CEFR level, grammar focus and exercise format, and
a Learning Designer queue that *"catches grammatical issues, unnatural
phrasing, and pedagogically suboptimal constructions."* Cited as corroboration
only — it is a secondary summary, and the claim above rests on the Duolingo
primary. Implication for this pipeline: this pipeline is *more* constrained
than Duolingo's, not less — `lab.json` is schema-bound and CEFR-equivalent
banding is declared in `calibration.yaml` — which makes the absence of the
review step at the end more conspicuous, not less.

**Human review at the end does not substitute for machine checks before
it, and reviewer attention is the scarcest resource in the pipeline.** *This
is my inference from the fixture, not a claim either source makes.* Duolingo's
designers review content that renders correctly; a designer handed L01 would
spend the entire review on the JSON dump and never reach naturalness,
vocabulary or learning value. That is the practical argument for ordering the
deterministic rendering check before any human or model reviewer: reviewers
are the expensive stage, and a defect a regex can find should never consume
one.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Duolingo, "How Duolingo uses AI to create lessons faster" (company blog, primary) — https://blog.duolingo.com/large-language-model-duolingo-lessons/
- ZenML LLMOps Database, "Duolingo: AI-Powered Lesson Generation System for Language Learning" (secondary summary, corroboration only) — https://www.zenml.io/llmops-database/ai-powered-lesson-generation-system-for-language-learning

## Discarded

- https://blog.duolingo.com/how-duolingo-experts-work-with-ai/ — fetched, and it is a genuine Duolingo primary source, but it does **not** describe humans reviewing AI output before release. It describes a four-stage course-creation process in which humans lead curriculum design and raw content creation while algorithms generate exercises; the humans it discusses are authoring, not reviewing. Its title and the search snippet both implied a review gate the page does not contain. Discarded for that claim — a later scan should not re-fetch it expecting one.
- `sridhar-ai.ch`, `x-pilot.ai`, `timtis.com` — rejected on the source-quality bar without fetching. All three recycle the same Duolingo "40% faster / 7 courses in 6 months" figures with no primary attribution, which is exactly the content-farm pattern the methodology says to drop rather than cite weakly. The productivity figures are therefore absent from this scan rather than sourced weakly.
- No Khan Academy / Khanmigo primary quality-methodology page was located in this scan's searches; the Khanmigo material returned was third-party summary. Named as a gap rather than filled with a weak source.
