# Curriculum Sequence and Prerequisite Coherence Reviewer

## Why this thread

This thread is new in this refresh. It comes from a defect the QA report does
not mention and the previous scan therefore never chased.

The run contains four lessons, L01 through L04. Two of them point forward to a
lesson that does not exist:

- `L03.md:112` — `"next_lab_link": "L05 asks you to plan a resistor's two
  connection points the same way this lab planned a wire's."`
- `L04.md:117` — `"next_lab_link": "L05 uses the same evidence-first habit to
  read a resistor's value before any circuit is built."`

There is no L05 in `outputs/arduino_kit_run_v2/`. Both are dangling forward
references, and they are not identical boilerplate — each invents a distinct
and plausible description of a lesson that was never generated, which is
harder to notice by eye than a repeated placeholder would be.

L04 also depends on a prerequisite the sequence never establishes: it teaches
socket selection by expected current ("under 200 mA," "above 200 mA") when no
prior lesson has introduced current as a quantity. L01 through L03 cover a
power path, breadboard connectivity, and jumper endpoints — none of them
defines current.

No check covers any of this. The unit-level checks operate on one unit at a
time: `results/unit_checks.json` is per-lesson, and the run-level results
(`gate_0_logger.json`, `gate_1_static_preflight.json`) concern logging and
static preflight. `CUR-COUNT-DERIVED` checks how many units there should be,
not whether the units reference each other coherently. The pipeline has no
reviewer whose input is *the sequence*.

## Findings

**Curriculum prerequisite structure is representable as a graph, and cycle/
dangling-edge detection over it is a mechanical check.** Liang, Lin et al.
(Peking University), "K12-KGraph: A Curriculum-Aligned Knowledge Graph for
Benchmarking and Training Educational LLMs" (arXiv:2605.09635), constructs a
heterogeneous property graph over seven node types (Concept, Skill,
Experiment, Exercise, Section, Chapter, Book) with nine edge types including
`prerequisites_for`, and validates it structurally: "we run depth-first cycle
detection on the `is_a` and `prerequisites_for` subgraphs and manually resolve
any violations, yielding valid DAGs for the taxonomic and prerequisite
relations." Implication for this pipeline: `next_lab_link` and the vocabulary
declarations already form exactly this kind of edge set. Resolving every
`next_lab_link` target against the set of units the run actually produced is
the same class of check — cheap, deterministic, and it would have caught both
dangling L05 references on the first unit that emitted one.

**Prerequisite reasoning is the task current LLMs are worst at, which is the
argument for checking it deterministically rather than asking a judge.** The
same paper's K12-Bench includes a `Prereq` task family — "given a
concept/skill, select its prerequisite closure" and "given a concept/skill,
select all of its *most direct* successors" — and reports that "Prereq and
Neighbor tasks are hardest... with EM below 35% even for Gemini-3-Flash,"
with most models below 30% exact match. Implication: an LLM judge asked "does
this lesson sequence hang together?" is being asked its weakest question. The
link-resolution and prerequisite-coverage checks should be deterministic graph
operations over the run's own artifacts, with the judge used only for the
residue.

**Coherence across a sequence is an established evaluation dimension for
instructional materials, not an invented one.** SciEval (arXiv:2604.25472)
scores K-12 science instructional materials "across 13 criteria (N=3549) using
the EQuIP rubric" — a rubric whose design centre is coherence between
standards, lessons and assessment across a unit rather than the quality of any
single lesson in isolation. Implication: reviewing units one at a time is a
structural blind spot in the current gate design, and adopting a
sequence-level dimension is aligned with how instructional materials are
professionally evaluated.

**Layered oversight supports making this its own review layer.** Sadhu & Dhor,
"Hierarchical Pedagogical Oversight" (arXiv:2512.22496), argues for
hierarchical multi-agent oversight with evaluation at different organisational
levels rather than a single flat reviewer. Implication: the sequence reviewer
runs at a different level from every existing check — after all units in a
curriculum are generated, over the set — which is why no per-unit gate could
have caught this defect no matter how strict it was.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Liang, Lin et al., "K12-KGraph: A Curriculum-Aligned Knowledge Graph for
  Benchmarking and Training Educational LLMs," arXiv:2605.09635 —
  https://arxiv.org/html/2605.09635v1
- "SciEval: A Benchmark for Automatic Evaluation of K-12 Science Instructional
  Materials," arXiv:2604.25472 — https://arxiv.org/abs/2604.25472
- Sadhu & Dhor, "Hierarchical Pedagogical Oversight: A Multi-Agent Adversarial
  Framework for Reliable AI Tutoring," arXiv:2512.22496 —
  https://www.arxiv.org/pdf/2512.22496

## Discarded

- `arxiv.org/abs/2601.21698` ("Curriculum Learning for LLM Pretraining"),
  `arxiv.org/abs/2603.13761` ("Level Up: Defining and Exploiting Transitional
  Problems for Curriculum Learning"), `arxiv.org/abs/2101.10382` ("Curriculum
  Learning: A Survey") — not fetched. All three surfaced on the sequencing
  queries and all three are about *curriculum learning* as a model-training
  technique (ordering training data easy-to-hard), which is an unrelated sense
  of the word "curriculum" from the one this thread is chasing. Recorded here
  so a later scan does not re-chase them: this query family reliably returns
  the training-technique sense, and needs "learning progression," "prerequisite
  graph" or "instructional materials" to reach the pedagogical sense.
- `futureagi.com/glossary/coherence/` — not fetched; a vendor glossary entry
  defining coherence as an eval metric, with no primary source behind it.
  Below the source-quality bar.
