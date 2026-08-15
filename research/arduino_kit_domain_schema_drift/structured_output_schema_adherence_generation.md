# Structured-output schema adherence in generation

## Why this thread

The four domain files aren't randomly malformed — they are byte-for-byte
consistent with each other's *superseded* shape
(`component_identity`/`primary_sources`/`terminals`/`legal_coordinates`/
`rail_topology`/`ratings`/`source_bundle_sha256`), right down to carrying
placeholder `"rail_topology": null` and `"source_bundle_sha256": null` fields
that only make sense in that old shape. `l02`-`l04` were authored on
2026-08-02, after the schema-owning commit that requires `electrical` +
`build_map`, which strongly suggests they were produced by pattern-matching
`l01` (the closest available example) rather than against
`domain.schema.v1.json` itself. This thread asks what current research says
about why a generator (model or process) would reproduce an existing file's
stale surface form instead of a stated-but-less-salient current rule, and how
reliably schema-following generation can be trusted at all.

## Findings

**Even purpose-built constrained-decoding frameworks fail a large fraction of
real-world schemas, and plain unconstrained generation fails far more often.**
JSONSchemaBench found that the best-performing framework (Guidance) still
drops to 30-41% empirical coverage on harder real-world schema datasets
(GitHub Hard, JSON Schema Store), while unconstrained "LM-only" generation
scores only 13-21% on the same hard datasets; closed-source API JSON modes
ranked lowest on coverage among all approaches tested
(*JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language
Models*, arXiv:2501.10868). Implication for this pipeline: nothing about
using an LLM to author or extend a domain file, with or without JSON mode,
gives schema conformance by default — a deterministic post-generation
validator is not a redundant safety net here, it is the only thing that
actually establishes conformance.

**Forcing rigid structured output has its own cost, so the fix is
validate-then-regenerate, not just "always constrain."** *Let Me Speak
Freely?* found a "significant decline in LLMs' reasoning abilities under
format restrictions," with stricter format constraints causing greater
degradation (arXiv:2408.02442). Implication for this pipeline: the
recommended agent should not be "force stricter grammar-constrained decoding
at generation time" as the whole fix — it should be free-form generation
followed by an explicit, deterministic schema check with a regenerate loop on
failure, which is closer to what this repo's own `verify_domain.py` already
does for other rule classes.

**LLMs lean on shortcuts from prompt context more, not less, under few-shot
prompting.** *Do LLMs Overcome Shortcut Learning?* found larger LLMs are more
likely to rely on shortcuts/spurious correlations under both zero-shot and
few-shot in-context prompting, that few-shot prompting generally underperforms
zero-shot on the shortcut-sensitive tasks tested, and that chain-of-thought
prompting reduces shortcut reliance more than either (arXiv:2410.13343).
Implication for this pipeline: treating `l01` as an implicit few-shot example
when drafting `l02`-`l04` is exactly the condition this paper associates with
higher shortcut reliance — copying the surface shape of a nearby existing
file rather than the stated schema. The mitigation isn't "give the model
better examples," since the example itself was stale; it's removing the
model's ability to ship an unvalidated shape at all.

## Sources (all fetched and verified to resolve to real, on-topic content)

- *JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language Models* — https://arxiv.org/html/2501.10868v1 (abstract page: https://arxiv.org/abs/2501.10868)
- *Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models* — https://arxiv.org/abs/2408.02442
- *Do LLMs Overcome Shortcut Learning? An Evaluation of Shortcut Challenges in Large Language Models* — https://arxiv.org/abs/2410.13343

## Discarded

- Nothing discarded from the direct candidate set for this thread — every
  fetched source resolved to real, on-topic content. One retry occurred:
  `arxiv.org/abs/2501.10868` returned only abstract/metadata with no
  extractable numbers (logged as PARTIALLY VERIFIED), so
  `arxiv.org/html/2501.10868v1` was fetched as the next rung and returned the
  full results with numbers (VERIFIED); both rungs are in the action log.
- A broader search on "few-shot example imitation / in-context surface form
  bias" returned only generic IBM/Medium/Springer explainer content on
  in-context learning in general, none of it specific enough to cite for the
  "copies a stale example instead of the stated rule" claim; abandoned in
  favor of the more specific shortcut-learning search that produced
  arXiv:2410.13343.
