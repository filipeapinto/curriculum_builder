# Commercial and Production QA Practice

## Why this thread

Required by the methodology: papers describe what is possible, shipping
systems reveal which of it survived contact with users. It is also the thread
that changed most in this refresh — two of the three sources the previous scan
used here did not survive re-verification, and the replacement is stronger
than what it replaces.

The grounding defect it speaks to is the bypass. This run's `acceptance.json`
records `"cross-family judge bypassed"` on all four units with the rationale
"user authorized the current in-session LLM as the model worker; no separate
API" — i.e. the pipeline shipped with its only human-like review step turned
off, and shipped four unreadable lessons behind that decision. The question
for this thread is what production systems treat as non-negotiable.

## Findings

**A platform serving 100M+ users treats the judge itself as an artifact with a
measured error rate, not as the measurement.** Gupta, Rossell, Alcobaça et al.
(Nubank), "Building Customer Support AI Agents at 100M-User Scale: An
Evaluation-Driven Framework" (arXiv:2606.08867), presents a framework
integrating "(1) structured context engineering..., (2) systematic
human-in-the-loop prompt iteration, (3) rigorous LLM judge evaluation with
**measured inter-rater agreement** and GEPA optimization for consistency, and
(4) ideation-to-production validation," across five production deployments.
Its stated central insight: "evaluation-pipeline quality directly determines
iteration velocity," with the card-delivery A/B test yielding a 37 percentage-
point improvement in AI transactional NPS. Implication for this pipeline: the
lesson is not merely "restore the judge" but "measure the judge's agreement
with a human on a sample before trusting its verdicts" — and that the quality
of the eval pipeline, not the authoring model, is what governs how fast the
project can improve.

**A shipping K-12 vendor documents a continuous audit cycle and refuses to
position AI output as final.** MagicSchool's own quality documentation
describes a Framing → Auditing → Refining cycle, daily LLM evaluations and
quality-control testing, and internal benchmarks covering hallucination
detection, factual accuracy, bias and school-appropriateness, pairing each
tool with "the model best suited for its task." Its stated principle: "AI
outputs are designed to be a starting point for educator judgment, never a
final decision." Implication: the `*Draft pending downstream human review.*`
banner on every lesson in this run is the right posture and matches vendor
practice — but a banner is not a review step, and in this run there was no
mechanism between generation and that banner.

**The market-validated adoption pattern is teacher-as-editor with
machine-validated standards claims.** An analysis of AI lesson-planning tools
(Fora Soft, "Best AI Tools for Lesson Planning: 7 Compared," July 2026) argues
that compliance and workflow fit rather than model quality determine adoption,
and states that a validator should confirm a standards tag actually appears,
warning that models "will confidently cite the wrong standard, which is worse
than none." It grounds its claims in the RAND/Gallup "Teaching for Tomorrow"
(2025) study, FERPA (20 U.S.C. § 1232g), and the FTC's amended COPPA rule.
Cited with a caveat: this is a vendor-perspective piece that discloses its own
EdTech work, so it is used for the adoption-pattern observation and its named
regulatory anchors, not as independent measurement. Implication: a confidently
wrong claim is treated in the market as worse than an absent one — which
generalises directly to L04's unverified fuse sentence.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Gupta, Rossell, Alcobaça et al., "Building Customer Support AI Agents at
  100M-User Scale: An Evaluation-Driven Framework," arXiv:2606.08867 —
  https://arxiv.org/abs/2606.08867
- MagicSchool, "Quality & Responsible AI in Education" —
  https://www.magicschool.ai/privacy/quality
- Fora Soft, "Best AI Tools for Lesson Planning: 7 Compared (2026)" —
  https://www.forasoft.com/blog/article/automated-lesson-plan-generation-software

## Discarded

- `https://zylos.ai/research/2026-04-10-llm-as-judge-production-agent-verification-2026/`
  — **cited by the previous scan; discarded in this refresh.** Resolves, but is
  an unsigned vendor-domain synthesis with no original data whose headline
  statistic misattributes a LangChain survey finding (57% of respondents had
  agents *in production*) to runtime judge adoption. Full reasoning in
  `multi_agent_llm_judge_review.md`.
- `https://www.kuraplan.com/reviews/diffit-review` — **cited by the previous
  scan; discarded in this refresh.** Resolves and quotes accurately, but is a
  competitor-authored review that names its own product the #1 alternative.
  Full reasoning in `readability_vocabulary_control.md`.
- Khan Academy / Khanmigo quality documentation — searched for as a second
  vendor-primary source and not found. Every result on that query was an
  affiliate or SEO review site (kidsaitools.com, aitoolsbakery.com,
  myengineeringbuddy.com, aiflowreview.com) rather than Khan Academy's own
  material. The whole result set was rejected without fetching, and the query
  was not refined further because MagicSchool's own quality page already
  fills the vendor-primary slot. Recorded so a later scan does not repeat it.
- The previous scan's title for the Fora Soft piece ("7 Best AI Tools for
  Lesson Plan Generation in 2026") no longer matches the page, which is now
  "Best AI Tools for Lesson Planning: 7 Compared (2026)," updated 2026-07-24.
  Same URL, same substance, retitled — not a discard, but the citation text
  was corrected rather than carried forward.
