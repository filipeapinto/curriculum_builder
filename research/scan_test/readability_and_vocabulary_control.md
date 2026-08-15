# Readability and vocabulary control — a reviewer that measures the delivered text

## Why this thread

The run targets, per the QA report's scope line, "Target level 2 (age 9+,
Flesch-Kincaid grade 2-6, ≤2 new terms/lab)", against a "Reported symptom:
output reads at 'level 100' against a level-2 objective."

Nothing measured it. The QA report's second Critical finding:
"`results/unit_checks.json` for every lesson (L01-L04) contains only
`DOMAIN-SCHEMA-VALID`, `DOMAIN-VERIFIER`, `LAB-SCHEMA-VALID`,
`RECEIPT-HASH-RESOLVES`. No `TEXT-READABILITY-BAND`, no `TEXT-BLOOM-VERBS`,
despite `prompt.md` naming both as mandatory gate-2 checks run 'on every unit in
every subject.' No gate-2 deterministic results file exists at the run root at
all." The run root confirms it: `outputs/arduino_kit_run_v2/results/` holds
`gate_0_logger.json` and `gate_1_static_preflight.json` and nothing else.

The vocabulary cap was breached in the one place prose survived. QA, High:
"L04 (`document/L04.md:26-27,59,89`): `mAVΩ`, `10A socket`, `mode dial`, `fuse`
— 4+ undefined terms against a cap of 2." The gap is structural, not
accidental: `workers/lab.json` declares exactly two vocabulary terms per
lesson and the declaration is what the schema validates, while the rendered
text introduces more. As QA puts it for L01, "the `child_definition` for 'rail'
exists only in `workers/lab.json`, never surfaces in document text."

So: the cap is enforced against a *declaration*, not against the *text*.

## Findings

**Instruction-tuned models cannot be trusted to hit a stated readability
standard, which is why the band has to be measured rather than declared.**
"Flesch or Fumble? Evaluating Readability Standard Alignment of
Instruction-Tuned Language Models" (arXiv 2309.05454) evaluates models on story
completion and narrative simplification "using standard-guided prompts
controlling text readability" against FKGL and CEFR, and reports that
"globally recognized models like ChatGPT may be considered less effective and
may require more refined prompts for these generative tasks compared to other
open-sourced models such as BLOOMZ and FlanT5." Implication for this pipeline: a
prompt that states "Flesch-Kincaid grade 2-6" buys nothing on its own. The band
is an assertion to be tested against the emitted string, and the test is
arithmetic, not judgement.

**Levelling accuracy degrades precisely at the low grade bands this curriculum
targets.**
"Evaluating GenAI for Simplifying Texts for Education" (arXiv 2501.09158)
simplifies twelfth-grade material down to eighth, sixth and fourth grade and
finds that "Both LLMs and prompting techniques demonstrated variable utility in
grade level accuracy and consistency of keywords and key phrases when
attempting to level content down to the fourth grade reading level."
Implication for this pipeline: our target floor (grade 2) sits below the band
where that study already observed instability. The correct posture is that the
generator will miss low, so the gate must be strict and must run every unit,
not sampled.

**Term-cap compliance measured on the declaration is not compliance.**
This claim is grounded in the fixture rather than in a paper, and is marked as
such: `lab.json` vocabulary lists "correctly declare only 2 terms per lesson"
(QA) while L04's rendered text carries `mAVΩ`, `10A socket`, `mode dial` and
`fuse`. Implication for this pipeline: the readability agent must tokenise the
*rendered* document, diff its content words against the union of declared
vocabulary plus terms defined in prior units, and count what is left. No
published source is needed for this and none is claimed.

## Sources (all fetched and verified to resolve to real, on-topic content)

- "Flesch or Fumble? Evaluating Readability Standard Alignment of Instruction-Tuned Language Models," arXiv 2309.05454 — https://arxiv.org/abs/2309.05454
- "Evaluating GenAI for Simplifying Texts for Education: Improving Accuracy and Consistency for Enhanced Readability," arXiv 2501.09158 — https://arxiv.org/abs/2501.09158

## Discarded

- Nothing was fetched and rejected in this thread; both candidates verified
  cleanly against the specific claims they are cited for. Recorded here so a
  later scan can tell this thread was searched rather than skipped: the search
  also surfaced arXiv 2407.01384, 2410.14028, 2606.21981 and 2601.06225 on
  readability control. They were not fetched because the two kept sources
  already carry both claims this thread needs, and the methodology prefers a
  thin honest thread to a padded one. They are reasonable first candidates if
  this thread is deepened later.
