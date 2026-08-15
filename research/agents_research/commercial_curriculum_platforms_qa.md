# Commercial AI curriculum platforms and their review/QA agent roles

## Why this thread

`curriculum_builder` is one team's pipeline for generating hands-on STEM
curriculum with an LLM. It's useful to check what review/QA roles the
production K-12 AI-content industry has converged on by 2026, both as a
sanity check on the gaps the QA report found and as a source of
battle-tested patterns rather than first-principles design.

## Findings

**MagicSchool runs a named, continuous three-stage QA cycle plus daily
automated evals, and treats AI output as a draft, never a final
instructional decision.** MagicSchool's "Quality & Responsible AI" page
describes a "Framing → Auditing → Refining" cycle: "Framing: Structuring
prompts before they reach AI models," "Auditing: Checking outputs for
safety and accuracy," "Refining: Updating safeguards as usage patterns
evolve." It states the platform runs "LLM evaluations and quality control
daily," with named test dimensions including "Hallucination
detection/Factual accuracy," "Bias and diversity," and "School
appropriateness," on top of a "Multi-layered moderation system" ("Multiple
classifiers, word/phrase detection, and AI analysis"). Critically: "AI
outputs are drafts, not final instructional decisions" — i.e. even with
this much automated QA, human educator review remains mandatory before
classroom use, which matches `curriculum_builder`'s own "*Draft pending
downstream human review.*" banner on every L01-L04 document.

**Diffit is a dedicated, separate product for reading-level adaptation —
the market has split "does this read at the right level" into its own
specialized tool rather than folding it into general lesson generation.**
Diffit is reviewed (Kuraplan, 2026) as best-in-class specifically for text
leveling across "4-5 reading levels," distinct from MagicSchool (breadth of
80+ tools) and Curipod (live engagement/formative assessment). This
specialization mirrors the recommendation elsewhere in this research (see
`readability_vocabulary_control.md`) that readability/vocabulary-band
compliance needs its own dedicated checker rather than being one line item
inside a general judge.

**The market-validated adoption pattern is "teacher as editor," and
standards/citation claims are explicitly flagged as something that must be
validated, not trusted from the model.** An analysis of AI lesson-plan tools
(forasoft.com, 2026) states the precondition for safe adoption is "standards
alignment and a teacher-in-the-loop edit step" — missing either means "the
output won't survive a department chair's review" — and warns specifically:
"a validator should confirm the tag actually appears... Models will
confidently cite the wrong standard, which is worse than none." The same
piece documents that 2026's dominant district strategy is deploying multiple
*specialized* tools together — "MagicSchool for breadth, Diffit for
differentiation, Curipod for live engagement" — rather than one monolithic
generator-plus-reviewer. This directly supports recommending several
distinct, narrowly-scoped review agents for `curriculum_builder` (rendering
gate, Bloom's/readability gate, domain-fact gate, safety gate, cross-family
judge) instead of a single catch-all reviewer.

## Sources (fetched and verified)

- MagicSchool, "Quality & Responsible AI in Education" —
  https://www.magicschool.ai/privacy/quality
- Kuraplan, "Diffit Review (2026) — The Gold Standard For Text Leveling" —
  https://www.kuraplan.com/reviews/diffit-review
- Forasoft, "7 Best AI Tools for Lesson Plan Generation in 2026
  (MagicSchool, Diffit, Curipod, Eduaide, Brisk, Education Copilot,
  Khanmigo)" —
  https://www.forasoft.com/blog/article/automated-lesson-plan-generation-software

## Discarded

- Kuraplan "Curipod Review (2026)" was fetched to check a claimed
  "teacher-as-editor" / fact-checking quote surfaced in search results; the
  actual page content did not support that specific claim (it covered
  pricing verification and curriculum-mapping gaps instead), so it was not
  cited for that point. The equivalent, correctly-sourced claim is drawn
  from the Forasoft article above instead.
