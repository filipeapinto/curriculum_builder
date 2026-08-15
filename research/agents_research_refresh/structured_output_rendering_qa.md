# Structured-Output Rendering Conformance Review

## Why this thread

The single most damaging defect in `outputs/arduino_kit_run_v2` is that the
lesson body is not prose at all. Every `Engage`, `Explore`, `Explain`,
`Elaborate`, `Evaluate`, `Identification`, `Troubleshooting` and
`Adult safety verification` section in all four lessons is a literal JSON
object. `L01/document/L01.md:15-19` renders:

```
{
  "hook": "Three objects can belong to one possible power path even while every connection is safely open on the table.",
  "eliciting_question": "What do you think the coloured line beside a breadboard rail tells you?"
}
```

The QA report confirms the same shape in L02, L03 and L04 and identifies it
as "a single templating bug, not four independent failures — identical
section shapes and identical failure across all units."

What makes this a reviewer-agent gap rather than only a bug: every check that
ran on these units passed. `results/unit_checks.json` contains only
`DOMAIN-SCHEMA-VALID`, `DOMAIN-VERIFIER`, `LAB-SCHEMA-VALID` and
`RECEIPT-HASH-RESOLVES`. `lab.json` was schema-valid, so nothing objected.
The pipeline has a check for this in policy — `DOC-DERIVED-FROM-SOURCE`
asserts "the rendered string equals what is there" — but no gate-2
deterministic results file exists at the run root at all, only
`gate_0_logger.json` and `gate_1_static_preflight.json`. The check exists on
paper and was inert in practice.

## Findings

**Perfect schema validity is compatible with near-total semantic failure, and
the gap is measured, not theoretical.** Yin Li's "When JSON Is Not Enough:
Semantic Reliability of Schema-Constrained LLM Ordering Agents"
(arXiv:2607.18261) runs OrderBench over 2,400 API calls across four models in
two modes and reports that Gemma-2-2B produced **100% schema-valid output
with 2% semantic success** and a 41.7% unsafe-acceptance rate; Qwen3-30B-A3B
reached 100% schema validity at ~31% semantic success. The paper concludes
that "schema validity can be perfect while semantic reliability remains
insufficient for direct execution" and argues for a layered architecture with
domain verification and fail-closed execution downstream of the schema check.
Implication for this pipeline: the 100%-schema / 2.0%-semantic pair this
project quotes about itself is not an anomaly of its own making — it is the
documented failure mode of treating schema validation as the acceptance
criterion, and it is fixed by adding a layer, not by tightening the schema.

**The same result reproduces across a broader benchmark, so it is not an
artifact of one task.** LLMStructBench (Singh, Khurdula, Khemlani & Agarwal,
"The Structured Output Benchmark," arXiv:2604.25359) evaluates structured
output quality across multiple models and prompting strategies and finds
semantic errors persisting despite structural validity, with prompting
strategy mattering more than model size. Implication: a semantic/rendering
layer is a standing architectural requirement, not something to be prompted
away by upgrading the authoring model.

**Production practice puts a deterministic structural check *before* any
LLM-judge layer, precisely because a same-family judge cannot see its own
blind spot.** Waxell's engineering writeup on AI agent output validation
(cross-posted to DEV Community, May 2026) describes three distinct layers:
Layer 1 is "Before any LLM judgment, run structural validation on the output:
does the response match the expected schema? Is it within length bounds?";
Layer 2 is where "LLM-as-judge and embedding-based approaches belong"; Layer 3
decides "what to do based on the risk context of this particular action." The
piece notes deterministic checks "catch a large category of failures —
structured output failures, format errors, and obvious hallucinations," and
that when judge and generator "come from the same family... the judge
inherits the same blind spots." Implication: a one-line deterministic check
("does this section parse as JSON when it is supposed to be prose?") is both
the cheapest and the earliest place to catch this defect — and it must run
before, not instead of, a judge. Note on provenance: the prior scan cited this
article's canonical `waxell.ai` URL and quoted a phrase, "deterministic
pre-emission checks," that the article does not contain; the wording above is
what the source actually says.

**An empirically validated release-gate architecture confirms structural and
content checks must produce separate signals.** "Automated Self-Testing as a
Quality Gate: Evidence-Driven Release Management for LLM Applications"
(arXiv:2603.15676, March 2026) reports 38 evaluation runs across 20+ releases
of a multi-agent system, emitting deterministic PROMOTE/HOLD/ROLLBACK
decisions across five dimensions; evidence coverage was the primary
severe-regression discriminator, and both ROLLBACKs were triggered by
evidence-coverage failures rather than by aggregate quality scores.
Implication: the gate that would have caught this run is a specific,
separately-reported dimension — not a better overall score.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Yin Li, "When JSON Is Not Enough: Semantic Reliability of Schema-Constrained
  LLM Ordering Agents," arXiv:2607.18261 —
  https://arxiv.org/html/2607.18261v1
- Singh, Khurdula, Khemlani & Agarwal, "The Structured Output Benchmark: A
  Multi-Source Benchmark for Evaluating Structured Output Quality in Large
  Language Models" (LLMStructBench), arXiv:2604.25359 —
  https://arxiv.org/pdf/2604.25359
- Waxell, "AI Agent Output Validation in Production: Why Static Quality Gates
  Fail and How to Fix Them," May 2026 (DEV Community cross-post) —
  https://dev.to/waxell/ai-agent-output-validation-in-production-why-static-quality-gates-fail-and-how-to-fix-them-51ba
- "Automated Self-Testing as a Quality Gate: Evidence-Driven Release
  Management for LLM Applications," arXiv:2603.15676 —
  https://arxiv.org/html/2603.15676v1

## Discarded

- `https://waxell.ai/blog/ai-agent-output-validation-production` — **cited by
  the previous scan; discarded in this refresh.** The URL is live but now
  returns only the site shell (title "AI Agent Governance & Observability |
  Waxell"); two fetches returned no article body, so a reader clicking the
  previous scan's citation cannot reach the evidence. Retry ladder: searched
  for an alternate form, found the publisher's own DEV Community cross-post
  with the same May 2026 date, which serves the full text and is cited above
  in its place. The underlying claim survives; the URL does not. Separately,
  the previous scan placed "deterministic pre-emission checks" in quotation
  marks — that phrase is not in the article, whose wording is "structural
  validation on the output."
- `futureagi.com/blog/evaluating-llm-structured-output-modes-2026/`,
  `eastondev.com`, `collinwilkins.com/articles/structured-output` — not
  fetched. Search snippets showed recycled latency/failure-rate tables
  (+0ms/5-10%, +50ms/2-5%, +100ms/<0.1%) with no primary benchmark behind
  them. Below the source-quality bar; the numbers were dropped rather than
  cited weakly.
