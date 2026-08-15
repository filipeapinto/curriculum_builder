# Schema validity as a false signal — why "all checks passed" and "unreadable" coexisted

## Why this thread

The previous thread establishes *what* broke. This one answers the harder half
of the user's question: why the pipeline reported success while shipping it.

Every unit reached `"terminal_state": "ACCEPTED"` with
`"claim": "every executed automated check passed"`
(`outputs/arduino_kit_run_v2/L01/acceptance.json`). That claim is true. The
four checks that ran — `LAB-SCHEMA-VALID`, `DOMAIN-SCHEMA-VALID`,
`DOMAIN-VERIFIER`, `RECEIPT-HASH-RESOLVES` — all measure the structured data
and its provenance, and the structured data was fine. Acceptance was therefore
computed from a measurement that is real but does not cover the artifact the
learner reads.

The pipeline's own contract already says this in as many words. `prompt.md`
(frozen into every unit at `inputs/prompt.md`) states: *"100% schema validity
has been measured alongside 2.0% semantic success. A valid unit is a shaped
unit, not a correct one."* The failure mode was documented and the run still
accepted on shape.

## Findings

**Schema validity and semantic correctness are empirically separable, and the
gap is large enough to be dangerous.** Yin Li, "When JSON Is Not Enough:
Semantic Reliability of Schema-Constrained LLM Ordering Agents"
(arXiv:2607.18261): *"schema-valid output can still have large semantic error
rates"*; in the strongest model tested *"both modes achieve 100% schema
validity, yet semantic success remains near 80%,"* and in weaker models
*"schema-valid unsafe acceptances occur in double digits."* Its conclusion is
the one this run needed: *"structured output is a necessary interface layer,
not a substitute for domain verification and fail-closed execution."*
Scope caveat, stated because it matters: this paper is about ordering agents
executing transactions, not about documents. It supports the principle that a
schema-valid artifact can be wrong; it says nothing about rendering.
Implication for this pipeline: an acceptance decision computed only from
schema checks is structurally the same bet this paper measures losing, and
`acceptance.json` shows the bet was placed four times.

**Benchmarks that score only schema compliance systematically overstate
quality.** The Structured Output Benchmark (arXiv:2604.25359) was built
because existing benchmarks *"focus on schema compliance alone"*; it finds
*"models achieve near-perfect schema compliance, yet the best Value Accuracy,
measured by exact leaf-value match, reaches only 83.0% on text, 67.2% on
images, and 23.7% on audio."* Scope caveat: this measures value extraction
accuracy, not rendering. Implication for this pipeline: near-perfect schema
compliance is the expected result of a schema check, not evidence of quality —
it carries almost no information about the output, so a gate built only from
schema checks is close to a gate that always passes.

**The measurable consequence here is that "every executed automated check
passed" is a sentence about coverage, not about quality.** *This reading is my
own inference from the two sources above plus the run's artifacts, not a claim
either paper makes:* the honest form of that acceptance claim would name what
was *not* executed. In this run that list includes `TEXT-READABILITY-BAND` and
`TEXT-BLOOM-VERBS` (both mandated by `prompt.md:193-195`, neither present in
any `unit_checks.json`), any check on the rendered document, and
`REV-JUDGE-SINGLE-CROSS-FAMILY` (recorded as bypassed). An acceptance record
that cannot distinguish "passed" from "did not run" will always read as green.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Yin Li, "When JSON Is Not Enough: Semantic Reliability of Schema-Constrained LLM Ordering Agents," arXiv:2607.18261 — https://arxiv.org/abs/2607.18261
- "The Structured Output Benchmark: A Multi-Source Benchmark for Evaluating Structured Output Quality in Large Language Models," arXiv:2604.25359 — https://arxiv.org/abs/2604.25359

## Discarded

- Several results in this thread's search set (`tetrate.io`, `futureagi.com`, `jsonic.io`, `markaicode.com`, `validatethis.org`, `deepinspect.ai`) are vendor or SEO explainer pages on getting valid JSON out of an LLM. They restate the schema-vs-semantics point without primary evidence and address the inverse problem to ours. Rejected on the source-quality bar without fetching; the claim is carried by the two papers above instead.
