# Structured-output-to-prose rendering validation

## Why this thread

This is the QA report's single biggest and most avoidable finding
(Critical #1): "Document renderer dumps raw JSON as lesson body. All 4
lessons (L01-L04)." The report shows the `## Engage` section of `L01.md`
containing a literal JSON object (`{"hook": ..., "eliciting_question":
...}`) instead of rendered prose, "mirroring `workers/lab.json`'s
`sequence`/`content` blocks byte-for-byte," and confirms it is "a single
templating bug, not four independent failures — identical section shapes
and identical failure across all units." The report's own root-cause
assessment is blunt: this "[m]akes every lesson unreadable at any grade
level, not just level 2," and none of the existing checks
(`DOMAIN-SCHEMA-VALID`, `DOMAIN-VERIFIER`, `LAB-SCHEMA-VALID`,
`RECEIPT-HASH-RESOLVES`) caught it, because none of them inspect the
*shape* of the rendered output — only whether upstream JSON was
schema-valid.

## Findings

**2026 production practice treats a cheap deterministic "does this look
like the right kind of thing" check as a mandatory pre-emission gate,
separate from and prior to any semantic LLM-judge.** An article on why
static output-validation gates fail in production (waxell.ai, 2026)
argues for three distinct validation layers, the first of which is
"deterministic pre-emission checks" that are explicitly "fast, cheap, and
catch a large category of failures — structured output failures, format
errors, and obvious hallucinations" — before any probabilistic/LLM-judge
semantic layer runs. It further notes LLM-as-judge alone has "production
limitations" (circularity — a model can't reliably judge its own class of
mistake — and latency), so "a robust approach pairs LLM-as-judge with
faster deterministic checks and an enforcement layer that acts on the
results." A one-line check ("does this section parse as valid JSON when it
is supposed to be prose?") is exactly this kind of cheap deterministic
check, and would have caught the L01-L04 bug on the very first lesson
rather than letting it repeat identically across all four.

**An empirically-validated release-gate architecture shows why structural
checks and content checks must run separately, because some failures are
invisible to a judge reading only for meaning.** "Automated Self-Testing as
a Quality Gate: Evidence-Driven Release Management for LLM Applications"
(arXiv:2603.15676) proposes a formalized PROMOTE/HOLD/ROLLBACK gate across
five dimensions (task success, context preservation, latency, safety pass
rate, evidence coverage), explicitly pairing "structural checks... with
content evaluation to catch failures invisible in response text alone."
Across 38 evaluation runs over 20+ releases, the framework caught 2
ROLLBACK-grade builds, and the authors found "automated gates surfaced
structural failures (latency, routing) that content-only assessment
missed" — direct empirical support for the general principle that a
content/semantic judge (like the bypassed `REV-JUDGE-SINGLE-CROSS-FAMILY`
check) is not a substitute for a structural/shape check, and vice versa;
`curriculum_builder` needs both, not one instead of the other.

## Sources (fetched and verified)

- Waxell.ai, "AI Agent Output Validation: Why Static Gates Fail [2026]" —
  https://waxell.ai/blog/ai-agent-output-validation-production
- "Automated Self-Testing as a Quality Gate: Evidence-Driven Release
  Management for LLM Applications," arXiv:2603.15676 —
  https://arxiv.org/html/2603.15676v1
