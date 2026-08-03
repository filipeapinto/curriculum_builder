# Sequence coherence — a reviewer that reads the run, not the unit

## Why this thread

Each lesson ends with a `next_lab_link`. Read in order across the run:

- L01 → "L02 reuses the habit of checking the power state before the child handles a new component."
- L02 → "L03 uses this same connectivity picture to place jumper wires and an expansion board correctly."
- L03 → "L05 asks you to plan a resistor's two connection points the same way this lab planned a wire's."
- L04 → "L05 uses the same evidence-first habit to read a resistor's value before any circuit is built."

L03 hands off to L05, skipping L04 entirely. L04 is orphaned — nothing in the
run points into it — and L05 is claimed twice by units that promise it
different things. `results/gate_1_static_preflight.json` confirms L04 and L05
are both real units in a 35-unit manifest, so this is a broken forward chain,
not a naming artefact.

Nothing could have caught it. Every check in `results/unit_checks.json` is
scoped to one unit: schema validity of that unit, the domain verifier on that
unit, receipts for that unit's assets. `runtime/session_bridge.py:finalize()`
takes a single output directory. There is no gate whose input is the *set* of
units, so no gate can see a link that points outside the unit it lives in.

This defect is not in the QA report either. QA scoped itself to L01-L04
individually.

## Findings

**Coherence is a property that has to be defined and designed for
deliberately; it does not emerge from well-formed parts.**
Kristen Huff, Head of Measurement at Curriculum Associates, writing on the
Center for Assessment (NCIEA) blog, 13 August 2025: "Coherence is crucial to
student learning. We must not leave it to chance", and "We rarely define
coherence clearly, or design for it intentionally. Without that intentional
approach, we can't support effective teaching and learning." She adds that
"partial coherence is not coherence." Implication for this pipeline: four
individually schema-valid units are exactly the "well-formed parts" case. The
pipeline currently leaves coherence entirely to chance because no artifact
holds the between-unit claims, and the one place those claims *are* written
down — `next_lab_link` free text — is never parsed.

**Learning progressions are expected to be evaluated against explicit criteria,
structure among them, rather than accepted as authored.**
Kobrin, Larson, Cromwell and Garza, "A Framework for Evaluating Learning
Progressions on Features Related to Their Intended Uses" (Journal of
Educational Research and Practice, 2015), propose evaluating a progression on
structure, content, usability and validity evidence, arguing that "educators
and other stakeholders should understand these key features so they can
evaluate whether an LP is appropriate for an intended use." Implication for
this pipeline: "structure" is the criterion our run fails, and it is the one
criterion that is mechanically checkable — the forward-link graph over 35 units
should be a connected chain, and ours has a break and a double-claim in the
first four.

**Prerequisite structure is modelled as explicit, queryable relations in
current curriculum-graph work rather than as prose inside a lesson.**
"K12-KGraph: A Curriculum-Aligned Knowledge Graph for Benchmarking and Training
Educational LLMs" (arXiv 2605.09635) builds a graph with "nine node types and
fourteen relation types covering curriculum structure and visual grounding",
models prerequisite chains, and defines five benchmark task families —
"Ground, Prereq, Neighbor, Evidence, and Locate" — over 23,640 multi-select
questions. Note the abstract does not claim DAG-acyclicity validation, contrary
to the search snippet. Implication for this pipeline: the fixture already has
the raw material for this, in `pedagogy.prior_knowledge.prerequisite_labs`
inside each `lab.json` — a field that is populated, schema-validated, and read
by no check. Promoting it plus `next_lab_link` into an actual graph is a small
change; the reviewer is what makes the graph load-bearing.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Kristen Huff, "Designing for Coherence," Center for Assessment (NCIEA), 13 August 2025 — https://www.nciea.org/blog/designing-for-coherence/
- Kobrin, Larson, Cromwell, Garza, "A Framework for Evaluating Learning Progressions on Features Related to Their Intended Uses," Journal of Educational Research and Practice, 2015, ERIC EJ1118467 — https://eric.ed.gov/?id=EJ1118467
- "K12-KGraph: A Curriculum-Aligned Knowledge Graph for Benchmarking and Training Educational LLMs," arXiv 2605.09635 — https://arxiv.org/abs/2605.09635

## Discarded

- https://files.eric.ed.gov/fulltext/EJ1118467.pdf — fetched, returned undecodable PDF binary. Per the retry ladder, retried once via the ERIC record page, which returned clean bibliographic data and the framework criteria. Cite the record URL; do not re-fetch this PDF.
- Two researchgate.net entries ("Toward coherence in curriculum, instruction, and assessment"; "Learning progressions and teaching sequences: a review and analysis") — rejected without fetching, login-walled. The first is also available as Jin et al. 2019 in Science Education via Wiley; a later scan wanting the full review should try the DOI there rather than ResearchGate.
- The search snippet for arXiv 2605.09635 claimed the paper performs "DAG validation on taxonomic and prerequisite relations". The fetched abstract does not say this. The source is kept but cited only for what it does state; the DAG-validation claim is dropped rather than attributed.
