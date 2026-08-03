# Domain-expert factual verification for generated STEM content

## Why this thread

The ground-truth labs make specific, safety-relevant electronics claims that
a domain expert (not a pedagogy or safety reviewer) would need to check for
correctness — e.g. L04's Explain block: "The mAVΩ socket shares one small
fuse across voltage, resistance, and currents under 200 mA; a separate 10A
socket exists so a larger expected current does not risk that same fuse,"
and its Troubleshooting entry: "leaving the red probe in a current socket
and then measuring voltage could be a problem." L02 makes claims about
breadboard internal-clip topology ("five holes in the same segment share
one clip... The centre trench is built to separate the two sides"). None of
`curriculum_builder`'s current checks (`DOMAIN-SCHEMA-VALID`,
`DOMAIN-VERIFIER`, `LAB-SCHEMA-VALID`, `RECEIPT-HASH-RESOLVES`) verify
that domain claims like these are factually correct and safe as stated —
`DOMAIN-VERIFIER` per the QA report's own framing only establishes schema
validity, not semantic/factual correctness ("A valid unit is a shaped unit,
not a correct one").

## Findings

**Content-generation and error/fact-detection are treated as distinct
specialized agent roles in current educational-agent surveys, not one
generic reviewer.** "LLM Agents for Education: Advances and Applications"
(arXiv:2503.11733) surveys LLM agents across teaching, personalization,
content generation, and error detection as separate capability categories,
and covers safety/ethics and trustworthiness as further distinct concerns —
reinforcing that a single "does this look okay" pass is not equivalent to a
domain-fact-grounding pass.

**A concrete, verified 2026 architecture pattern: a "Safeguard Agent" that
scores factual accuracy as one explicit review dimension, with a
generation-revision loop rather than accept/reject.** "A Multi-Agent
Framework for Democratizing XR Content Creation in K-12 Classrooms"
(arXiv:2604.04728) defines a four-agent pipeline (Pedagogical Agent →
Execution Agent → Safeguard Agent → Tutor Agent) where the Safeguard Agent
explicitly evaluates generated content across five K-12 dimensions —
"age-appropriateness, factual accuracy, absence of violent or disturbing
imagery, absence of racial, gender, or cultural bias, and educational
alignment" — and, critically, "if the output fails the review, the pipeline
re-enters the generation stage, using safeguard feedback to guide the next
attempt," rather than simply failing the build. This generation-revision
loop pattern (score → targeted feedback → regenerate) is a stronger design
than a pass/fail gate for catching and fixing domain-fact errors before
they reach a human reviewer.

## Sources (fetched and verified)

- Chu et al., "LLM Agents for Education: Advances and Applications,"
  arXiv:2503.11733 — https://arxiv.org/pdf/2503.11733
- "A Multi-Agent Framework for Democratizing XR Content Creation in K-12
  Classrooms," arXiv:2604.04728 — https://arxiv.org/html/2604.04728

## Discarded

- Springer/AI Review, "Hallucination to truth: a review of fact-checking
  and factuality evaluation in large language models"
  (doi:10.1007/s10462-025-11454-w) — resolved only to a Springer
  authentication/paywall redirect with no accessible article content; not
  cited.
- A cluster of "2026 hallucination-rate benchmark" search results
  (sqmagazine.co.uk, modelslab.com, axis-intelligence.com,
  digitalapplied.com, suprmind.ai) were found but not fetched or cited —
  these are SEO/aggregator blog content of unverifiable rigor for a
  specific statistic, and were judged unsuitable as evidence regardless of
  whether they technically resolve.
