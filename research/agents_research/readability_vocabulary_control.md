# Readability control and vocabulary-cap enforcement

## Why this thread

The QA report's reported symptom is "output reads at 'level 100' against a
level-2 objective" (target: age 9+, Flesch-Kincaid grade 2-6, ≤2 new
terms/lab). Its High-severity finding shows the vocabulary cap being
violated wherever prose exists at all: L04 introduces `mAVΩ`, `10A socket`,
`mode dial`, `fuse` — 4+ undefined terms against a cap of 2 — and L01 uses
"rail," "module," "low-voltage" before any definition, even though
`lab.json` correctly declares only 2 terms per lesson. The report notes the
`child_definition` for "rail" "exists only in `workers/lab.json`, never
surfaces in document text." `TEXT-READABILITY-BAND`, the gate-2 check meant
to catch exactly this, never ran.

## Findings

**Readability control needs a dedicated instruction-learning or
verification layer — plain prompting under-constrains grade level.**
"ReadCtrl: Personalizing Text Generation with Readability-Controlled
Instruction Learning" (arXiv:2406.09205) trains models for
"near-continuous" (not just categorical high/medium/low) readability
control, and reports its ReadCtrl-Mistral-7B model beating GPT-4 in human
evaluation (52.1% vs 35.7% win rate) on producing text that actually lands
at the requested readability level, with gains on both readability metrics
(FOG, FKGL) and quality metrics (BLEU, SARI, factuality, coherence). The
lesson for `curriculum_builder`: a general-purpose authoring prompt asking
for "level 2, age 9+" is not, by itself, a reliable way to hit a grade band
— dedicated readability-control tooling or a verification pass is needed on
top of generation.

**Even with dedicated multi-dimensional evaluation frameworks, LLMs
struggle to reliably hit a target readability level without explicit
lexical/syntactic constraint validation.** A 2026 study on LLM-generated
Arabic text at specific CEFR levels (arXiv:2606.21981) develops a
multi-dimensional evaluation framework (not just a single readability
score) to check whether generated text is calibrated to a target
proficiency band, and to determine whether models can hold to a target
difficulty level without losing semantic accuracy. (This paper's domain is
Arabic-language CEFR bands, not English grade-level bands — cited here for
its general methodological point that readability compliance needs
multi-dimensional, structural checking, not just a single Flesch-Kincaid
number, not for language- or curriculum-specific claims.)

**Commercial practice treats reading-level adaptation as its own
specialized product, still paired with mandatory human spot-checking.**
Diffit — reviewed by Kuraplan (2026) as "genuinely the best in the
category" for text leveling, with "non-fiction hold[ing] up cleanly across
4-5 reading levels" — is a dedicated tool solely for reading-level
differentiation, separate from lesson-plan generation tools like MagicSchool
or Curipod. Even so, the same review's only explicit verification
instruction to teachers is "Always read the answer key once before
printing," i.e., even the best-in-class dedicated readability tool is not
trusted to run unchecked.

## Sources (fetched and verified)

- Tran et al., "ReadCtrl: Personalizing Text Generation with
  Readability-Controlled Instruction Learning," arXiv:2406.09205 —
  https://arxiv.org/abs/2406.09205
- Rabih, Qwaider & Briscoe, "Can LLMs Control Readability? A
  Multi-Dimensional Analysis" (Arabic/CEFR), arXiv:2606.21981 —
  https://arxiv.org/pdf/2606.21981
- Kuraplan, "Diffit Review (2026) — The Gold Standard For Text Leveling" —
  https://www.kuraplan.com/reviews/diffit-review
