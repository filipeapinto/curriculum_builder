# Readability gates — the cheapest check that would have fired

## Why this thread

The run's target is age 9+, Flesch-Kincaid grade 2-6, at most 2 new terms per
lab (QA report, scope line). `prompt.md:193-195` names two mandatory
deterministic gate-2 checks against that target: *"readability —
`TEXT-READABILITY-BAND`"* and *"taxonomy verbs — `TEXT-BLOOM-VERBS`."*

Neither ran. `results/unit_checks.json` for L01-L04 contains only
`DOMAIN-SCHEMA-VALID`, `DOMAIN-VERIFIER`, `LAB-SCHEMA-VALID` and
`RECEIPT-HASH-RESOLVES`, and no gate-2 results file exists at the run root at
all — only `gate_0_logger.json` and `gate_1_static_preflight.json`. The QA
report's verdict: *"Nothing in the pipeline could have caught the level
mismatch even if the text had rendered as prose."*

This thread exists because of an ordering observation. A readability metric is
not a rendering check, but it consumes the rendered document — so it is the
one mandated check that a JSON dump would have tripped incidentally.

## Findings

**Readability of generated educational text is routinely measured with a
standard battery of formulas, so the gate is off-the-shelf, not research.**
Zhang, Wang, Zhang & Lan, "Decoupled quality and readability in skin cancer
education from large language models," *Frontiers in Public Health*
(20 February 2026), evaluates LLM-generated patient education using ARI, FRES,
GFOG, FKGL, CL, SMOG and LW. Scope caveat: the domain is Mandarin-Chinese
skin-cancer patient education, not children's STEM labs, so the study's
numbers do not transfer — the transferable part is that this battery is
standard practice and computable without a model. Implication for this
pipeline: `TEXT-READABILITY-BAND` is a few lines of arithmetic over the
document text, and its absence is an operational failure rather than a
missing capability.

**Readability and content quality are largely independent, so a pipeline must
measure both — and this run measured neither.** Same study: *"quality and
readability were largely independent dimensions,"* *"high-quality outputs do
not necessarily have high readability,"* with quality scores showing *"only
weak, predominantly negative correlations with most readability indices."*
Implication for this pipeline: a reviewer that judges pedagogical quality does
not subsume a readability band check, and vice versa. They are separate
verdicts on separate axes.

**Hitting a target reading level is a studied task that still fails in ways
requiring review.** "Generating Educational Materials with Different Levels of
Readability using LLMs" (arXiv:2406.12787) frames the leveled-text task as
rewriting educational material *"to specific readability levels while
preserving meaning,"* and its manual review of 100 processed materials found
*"misinformation introduction and inconsistent edit distribution."* Cited
conservatively: the abstract does not name a specific readability formula, so
no formula is attributed to it here. Implication for this pipeline: a
readability gate constrains surface form only; hitting grade 2-6 is not
evidence the content is correct, which is why this thread does not justify an
agent of its own beyond the band check.

**A readability check run on the shipped documents would have failed
loudly.** *This is my inference from the artifacts, not a published finding.*
No readability formula has defined behaviour on `{ "hook": "...",` — the
sentence and syllable counts are meaningless on brace-and-quote text, so the
check either returns a wild grade level or errors on the input. Either
outcome is a signal, and either would have stopped the run. I have not
executed the check against these files to confirm which; the claim is that a
gate existed on paper that would have had *something* to say, and it said
nothing because it never ran.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Zhang, Wang, Zhang & Lan, "Decoupled quality and readability in skin cancer education from large language models," Frontiers in Public Health, 20 February 2026 — https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2026.1777577/full
- "Generating Educational Materials with Different Levels of Readability using LLMs," arXiv:2406.12787 — https://arxiv.org/abs/2406.12787

## Discarded

- Nothing was fetched and then rejected in this thread. Two further candidates from the search set (a 2024 *Sagepub* readability comparison of LLM vs human educational content, and the WhyLabs LangKit feature documentation) were not fetched: the two sources above already carry the thread's claims, and the skill's guidance is to say a thread is adequately covered rather than pad it. Flagging for a later scan rather than silently dropping.
