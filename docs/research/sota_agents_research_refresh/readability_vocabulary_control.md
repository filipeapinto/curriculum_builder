# Readability-Band and Vocabulary-Cap Checker

## Why this thread

The run targets "level 2 (age 9+, Flesch-Kincaid grade 2-6, ≤2 new terms/lab)"
and the reported symptom was that output "reads at 'level 100' against a
level-2 objective." Two separate failures sit underneath that.

First, the check never ran. `policy/checks.v1.yaml` defines
`TEXT-READABILITY-BAND` as asserting that "every unit's child-facing text
scores inside the band policy/calibration.v1.yaml declares under readability
... A band and not a ceiling: text far below it is as wrong as text far
above it." Its own note concedes the state of play: "zero generated units
exist to score today; the executed assertion is the fixture pair, and RT-7 is
the coverage that is missing." `results/unit_checks.json` for L01-L04 confirms
it: only `DOMAIN-SCHEMA-VALID`, `DOMAIN-VERIFIER`, `LAB-SCHEMA-VALID` and
`RECEIPT-HASH-RESOLVES` were executed.

Second, the vocabulary cap was violated where prose exists at all. The QA
report records L04 introducing `mAVΩ`, `10A socket`, `mode dial` and `fuse` —
four-plus undefined terms against a declared cap of two — and notes that in
L01 the `child_definition` for "rail" "exists only in `workers/lab.json`,
never surfaces in document text." The declared vocabulary list was compliant;
the rendered text was not. Nothing compared the two.

## Findings

**Readability compliance improves substantially when it is a
verified/controlled objective rather than a prompt instruction.** Tran, Yao,
Li & Yu, "ReadCtrl: Personalizing Text Generation with Readability-Controlled
Instruction Learning" (arXiv:2406.09205), reports that "ReadCtrl-Mistral-7B
models significantly outperformed strong baseline models such as GPT-4 and
Claude-3, with a win rate of 52.1%:35.7% against GPT-4 in human evaluations"
on hitting requested readability levels. Implication for this pipeline:
telling the authoring model "write at level 2" is the weaker of the two
options that were measured; a checked band is the stronger one.

**A single aggregate readability score is not enough — compliance needs
multi-dimensional structural and lexical checking.** Rabih, Qwaider & Briscoe,
"Can LLMs Control Readability? A Multi-Dimensional Evaluation Framework for
CEFR-Controlled Arabic Generation" (arXiv:2606.21981), builds a
multi-dimensional framework rather than a single score to test whether models
hold a target proficiency band without losing semantic accuracy. **Scope
caveat, carried forward deliberately:** this paper's domain is Arabic CEFR
bands, not English grade-level bands. It is cited here only for the
methodological point that a band check needs structural and lexical
components, never for a language- or curriculum-specific claim. Implication:
the agent should report the Flesch-Kincaid number *and* the undefined-term
list separately, because a document can sit inside the grade band while
carrying four undefined technical terms — which is close to what L04 does.

**Automated scoring of instructional materials against an established rubric
is a live benchmark, and general-purpose models are not yet good at it.**
"SciEval: A Benchmark for Automatic Evaluation of K-12 Science Instructional
Materials" (arXiv:2604.25472) scores materials "across 13 criteria (N=3549)
using the EQuIP rubric," establishes a gold standard where "expert
annotations achieve high inter-rater reliability," and finds that among
mainstream LLMs tested "none achieve strong performance," with domain-aligned
fine-tuning worth "up to 11 percent performance gains." Implication: the
deterministic parts of this check — Flesch-Kincaid score, term counting
against the declared vocabulary list — should stay deterministic and stay
blocking. The judgemental parts should be reported to a human, not trusted to
a general model, because on this exact task general models measure weak.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Tran, Yao, Li & Yu, "ReadCtrl: Personalizing Text Generation with
  Readability-Controlled Instruction Learning," arXiv:2406.09205 —
  https://arxiv.org/abs/2406.09205
- Rabih, Qwaider & Briscoe, "Can LLMs Control Readability? A Multi-Dimensional
  Evaluation Framework for CEFR-Controlled Arabic Generation,"
  arXiv:2606.21981 — https://arxiv.org/pdf/2606.21981
- "SciEval: A Benchmark for Automatic Evaluation of K-12 Science Instructional
  Materials," arXiv:2604.25472 — https://arxiv.org/abs/2604.25472

## Discarded

- `https://www.kuraplan.com/reviews/diffit-review` — **cited by the previous
  scan; discarded in this refresh.** The page resolves and both strings the
  previous scan quoted are verbatim present, including "Always read the answer
  key once before printing." It fails on independence, not liveness: the
  review's own About section states "Kuraplan is our product and is named as
  the #1 alternative for the full teacher workflow (especially for non-US
  curricula); we have disclosed that bias openly." That makes it a competitor
  rating a rival while ranking itself first — competitive marketing, not
  evidence, and the previous scan cited it for a best-in-class claim without
  surfacing the conflict. No replacement was sought, because whether a
  third-party product leads the leveling category was never load-bearing for
  the recommendation.
