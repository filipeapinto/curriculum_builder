# Domain-Fact Safeguard Reviewer (electronics)

## Why this thread

The lessons make specific, checkable claims about real hardware, and nothing
in the executed check set verifies any of them. `L04.md:89` states:

> "The mAVΩ socket shares one small fuse across voltage, resistance, and
> currents under 200 mA; a separate 10A socket exists so a larger expected
> current does not risk that same fuse."

This is a claim about the internal protection topology of a specific class of
meter, written for a nine-year-old and their supervising adult, in a lab whose
whole purpose is teaching which socket to use. On common DMMs the mAVΩ jack's
fuse protects the *current* path; describing it as shared across voltage and
resistance measurement is at best imprecise and is the kind of statement a
domain expert would either correct or qualify. Similar unverified physical
assertions appear elsewhere: L02 claims "five holes in the same segment share
one clip" and that power rails "can be physically split partway."

The checks that ran on these units were `DOMAIN-SCHEMA-VALID`,
`DOMAIN-VERIFIER`, `LAB-SCHEMA-VALID` and `RECEIPT-HASH-RESOLVES`. The QA
report's own framing applies directly: "100% schema validity has been measured
alongside 2.0% semantic success. A valid unit is a shaped unit, not a correct
one." No check asks whether the sentence is *true*.

## Findings

**Schema-constrained generation gives no protection against domain-level
falsehood, and the size of that gap has been measured.** Yin Li, "When JSON Is
Not Enough" (arXiv:2607.18261), reports models producing 100% schema-valid
output at 2-31% semantic success across 2,400 calls, and concludes that
"schema validity can be perfect while semantic reliability remains
insufficient for direct execution," recommending domain verification as a
distinct downstream layer with fail-closed execution. Implication for this
pipeline: `DOMAIN-SCHEMA-VALID` passing tells you the domain block is
well-shaped; it tells you nothing about whether the fuse sentence is right,
and the paper's recommended remedy is exactly a separate domain-verification
layer.

**A verified 2026 K-12 content pipeline implements factual accuracy as a named
review dimension with a regenerate-on-failure loop, not accept/reject.** "A
Multi-Agent Framework for Democratizing XR Content Creation in K-12
Classrooms" (arXiv:2604.04728) defines a four-agent pipeline — Pedagogical
Agent, Execution Agent, Safeguard Agent, Tutor Agent — where the Safeguard
Agent scores content against five named criteria: age-appropriateness,
accuracy (factual content), safety, bias, and educational value. On failure,
"If the output fails the review, the pipeline re-enters the generation stage,
using safeguard feedback to guide the next attempt." Implication: the
domain-fact reviewer should feed a targeted regeneration pass rather than
emitting a bare rejection — a corrected fuse sentence is the desired outcome,
not a blocked unit. (Verification note: this paper's abstract does not list
the five criteria; the list and the quoted sentence come from the full HTML
text, which was fetched specifically to confirm them.)

**Fact/error detection is treated as its own agent role in the educational-
agent literature.** Chu et al., "LLM Agents for Education: Advances and
Applications" (arXiv:2503.11733), surveys educational LLM agents and separates
content generation from error detection and domain-specific reasoning as
distinct roles. Cited for that architectural claim only; it is a survey and
carries no measured result here. Implication: the domain checker is not a
clause inside the general judge's rubric — it needs its own input, namely the
frozen domain reference the run already carries under `inputs/` and
`sources/`, which the general judge does not read.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Yin Li, "When JSON Is Not Enough: Semantic Reliability of Schema-Constrained
  LLM Ordering Agents," arXiv:2607.18261 —
  https://arxiv.org/html/2607.18261v1
- "A Multi-Agent Framework for Democratizing XR Content Creation in K-12
  Classrooms," arXiv:2604.04728 — https://arxiv.org/html/2604.04728
- Chu et al., "LLM Agents for Education: Advances and Applications,"
  arXiv:2503.11733 — https://arxiv.org/pdf/2503.11733

## Discarded

- Nothing was discarded in this thread. Both sources the previous scan cited
  here (arXiv:2503.11733 and arXiv:2604.04728) were re-verified in this
  refresh and both still hold. One verification detail is worth recording so a
  later scan does not repeat the work: the arXiv **abstract** page for
  2604.04728 does not name the Safeguard Agent's five criteria and does not
  mention the regeneration loop, so the abstract alone is insufficient to
  support the claim made of it. The `/html/` full text does support it
  verbatim, and that is the form cited above.
