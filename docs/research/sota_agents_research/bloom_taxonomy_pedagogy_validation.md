# Bloom's-taxonomy alignment and pedagogy validation

## Why this thread

The QA report's Critical #2 states that `results/unit_checks.json` for every
lesson (L01-L04) contains only `DOMAIN-SCHEMA-VALID`, `DOMAIN-VERIFIER`,
`LAB-SCHEMA-VALID`, `RECEIPT-HASH-RESOLVES` — no `TEXT-READABILITY-BAND` and
no `TEXT-BLOOM-VERBS`, despite `prompt.md` naming both as mandatory gate-2
checks run "on every unit in every subject." The report concludes "nothing
in the pipeline could have caught the level mismatch even if the text had
rendered as prose." Each lab's `## Evaluate` block (e.g. L01/L02/L03/L04) has
a `hinge_question` and `success_criteria_checklist` clearly written to a
5E/formative-assessment model with intended cognitive verbs ("point to,"
"explain," "trace"), but nothing in the run verified those verbs actually
match the target Bloom's level for age 9+.

## Findings

**Automated Bloom's-level classification of generated content is feasible
but not sufficient on its own.** "Automated Educational Question Generation
at Different Bloom's Skill Levels using Large Language Models: Strategies
and Evaluation" (arXiv:2408.04394) evaluates five state-of-the-art LLMs
generating questions targeted at specific Bloom's levels, using both expert
human evaluation and automated LLM-based assessment. It finds LLMs "can
generate relevant and high-quality educational questions of different
cognitive levels when prompted with adequate information," but explicitly
notes "automated evaluation is not on par with human evaluation" — meaning a
Bloom's-verb checker cannot fully replace human review, but is still
valuable as a fast, cheap first-pass gate that catches gross mismatches
before anything reaches a human reviewer.

**Educational LLM-agent surveys treat "content generation" and "error
detection" as distinct agent roles, not one generic agent.** "LLM Agents for
Education: Advances and Applications" (arXiv:2503.11733, Chu et al.) surveys
the landscape of LLM agents applied to education and documents
tutoring/content-generation agents and safety/ethics agents as
architecturally separate roles with different responsibilities. This
supports treating "does this content hit the target cognitive level and
grade band" as its own dedicated reviewer rather than folding it into a
general subjective judge.

**Layered/adversarial oversight architectures are an active 2026 research
direction for pedagogical reliability.** "Hierarchical Pedagogical
Oversight: A Multi-Agent Adversarial Framework for Reliable AI Tutoring"
(arXiv:2512.22496, Sadhu & Dhor) proposes a multi-agent adversarial
structure in which different agents perform complementary, layered review
functions rather than a single evaluation pass. (Note: the full body text of
this preprint could not be extracted during verification — only metadata,
title, authors, and subject tags (cs.MA, cs.AI) were confirmed as real and
on-topic. It is cited here only for the general architectural pattern of
layered/adversarial pedagogical oversight, not for specific numeric claims.)

## Sources (fetched and verified)

- "Automated Educational Question Generation at Different Bloom's Skill
  Levels using Large Language Models: Strategies and Evaluation,"
  arXiv:2408.04394 — https://arxiv.org/abs/2408.04394
- Chu et al., "LLM Agents for Education: Advances and Applications,"
  arXiv:2503.11733 — https://arxiv.org/pdf/2503.11733
- Sadhu & Dhor, "Hierarchical Pedagogical Oversight: A Multi-Agent
  Adversarial Framework for Reliable AI Tutoring," arXiv:2512.22496 —
  https://www.arxiv.org/pdf/2512.22496 (metadata/topic verified only; cite
  conservatively)

## Discarded

- MDPI "eXplainable AI Framework for Automated Lesson Plan Generation and
  Alignment with Bloom's Taxonomy" (doi:10.3390/computers14110494 →
  https://www.mdpi.com/2073-431X/14/11/494) — returned HTTP 403 Forbidden on
  two separate fetch attempts; could not be verified; not cited despite
  being topically on point.
