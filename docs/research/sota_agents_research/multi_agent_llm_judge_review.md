# Multi-agent LLM-as-judge review and cross-family bias mitigation

## Why this thread

The QA report for `arduino_kit_run_v2` (Critical #3) shows that
`REV-JUDGE-SINGLE-CROSS-FAMILY` — described in the report as "the only check
that reads output like a human would" — never ran. `acceptance.json` records
`"routing_divergence": "USER_AUTHORIZED_IN_SESSION_MODEL; cross-family judge
bypassed"`, and `routing/authoring.json` shows the same in-session model was
used as both author and (absent) evaluator. This means the pipeline's sole
subjective/semantic gate was inert for the entire run, and nothing caught the
fact that all four lessons rendered as raw JSON instead of prose.

## Findings

**Self-preference bias is real, common, and not eliminated by capability.**
"Quantifying and Mitigating Self-Preference Bias of LLM Judges"
(arXiv:2604.22891) finds 17 of 20 tested models show statistically
significant self-preference (they favor their own outputs when judging), and
that "strong capability doesn't guarantee fairness — advanced models often
exhibit pronounced self-preference." The paper's own mitigation is *not*
simply "use a different model family": it verifies each candidate judge's
bias empirically (via a Probabilistic Inclination Ratio against a
self-comparison-excluded baseline) and only trusts judges shown to be
low-bias, while also showing that forcing structured, per-dimension
evaluation (rather than one holistic score) cuts bias by ~31.5% on average.
Implication for `curriculum_builder`: swapping in *any* cross-family model as
judge is not sufficient by itself — the judge should be selected/validated
for low self-preference and should score on structured dimensions
(readability, domain accuracy, safety-block completeness, etc.), not a
single pass/fail.

**More judges/perspectives does not automatically mean less bias.**
"Judging with Many Minds: Do More Perspectives Mean Less Prejudice? On Bias
Amplifications and Resistance in Multi-Agent Based LLM-as-Judge"
(arXiv:2505.19477) studies multi-agent debate/critic setups (building on the
ChatEval pattern) and explicitly frames the question as open: multi-agent
judging can amplify shared blind spots as easily as it resists them,
depending on how the panel is composed and how disagreement is resolved.
This argues for deliberately diverse panel composition and an explicit
disagreement-handling policy, not just "add more judges."

**Unsupervised group-based polling can mitigate judge bias without human
labels.** "Mitigating Judgment Preference Bias in Large Language Models
through Group-Based Polling" (arXiv:2510.08145) introduces Genii, "an
unsupervised multi-agent collaborative optimization framework that mitigates
the inherent judgment preference bias of judgment models" via simulated
client-server polling among judge agents, with no human-annotated training
data required, and effectiveness preserved "even when weaker models act as
server agents." This is directly relevant to a resource-constrained pipeline
like `curriculum_builder`, where a full human-labeled bias-calibration set is
unlikely to exist.

**Production practice in 2026 treats judge LLMs as pipeline infrastructure,
not an optional eval step.** Zylos Research's "LLM-as-Judge in Production"
(April 2026) reports that "more than half of surveyed production agent teams
now rely on judge LLMs at runtime for quality gating, hallucination defense,
and tool-call verification," and identifies six architectural patterns
(offline harnesses, online runtime verifiers, self-consistency loops,
reflection patterns, constitutional-AI judges, inference-time reward
models). Two findings are especially relevant here:
- **Small, specialized judges beat large generalist judges on cost and
  accuracy**: "Galileo Luna-2 (3B–8B) achieves 0.88–0.95 accuracy on agentic
  evaluation tasks with a 97% cost reduction versus GPT-4-based evaluation."
- **Intrinsic self-correction (a model reviewing its own output with no
  external signal) does not reliably work** and "often degrades" quality —
  the judge needs an external signal (retrieval, test results, a second
  model) to be worth running at all. This directly undercuts any design
  where the same in-session authoring model is asked to also self-check its
  output, which is effectively what happened when the cross-family judge was
  bypassed in favor of the authoring model.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Chen et al., "Quantifying and Mitigating Self-Preference Bias of LLM
  Judges," arXiv:2604.22891 — https://arxiv.org/html/2604.22891v4
- "Judging with Many Minds: Do More Perspectives Mean Less Prejudice? On
  Bias Amplifications and Resistance in Multi-Agent Based LLM-as-Judge,"
  arXiv:2505.19477 — https://arxiv.org/pdf/2505.19477
- Liu et al., "Mitigating Judgment Preference Bias in Large Language Models
  through Group-Based Polling" (Genii), arXiv:2510.08145 —
  https://arxiv.org/abs/2510.08145
- Zylos Research, "LLM-as-Judge in Production: Agent Reasoning
  Verification, Self-Correction, and Hallucination Defense (2026)" —
  https://zylos.ai/research/2026-04-10-llm-as-judge-production-agent-verification-2026/

## Discarded

- OpenReview "Multi-Agent Debate for LLM Judges with Adaptive Stability
  Detection" (https://openreview.net/forum?id=Vusd1Hw2D9) — resolved to a
  login/verification wall with no accessible paper content; not cited.
