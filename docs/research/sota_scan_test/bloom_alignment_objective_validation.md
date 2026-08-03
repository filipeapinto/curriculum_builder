# Bloom alignment — a reviewer that checks cognitive demand actually moves

## Why this thread

`TEXT-BLOOM-VERBS` is named in `prompt.md` as a mandatory gate-2 check "on
every unit in every subject" and, per the QA report, does not appear in any
unit's `results/unit_checks.json`. It never ran.

The data it would have read is sitting there unused. Every unit's
`workers/lab.json` carries `pedagogy.learning_objectives[].bloom_level`. Read
across the run:

| unit | declared Bloom levels |
|---|---|
| L01 | remember, understand, apply |
| L02 | remember, understand, apply |
| L03 | remember, understand, apply |
| L04 | remember, understand, apply |

Four units, one identical triple. Nothing rises across the sequence. The QA
report does not mention this — it is a defect this scan found by reading
`lab.json` directly before reading QA.

It gets worse when the declared level is checked against the actual task. L01's
third objective is declared `apply`, and its success criterion is "I can trace
the teaching path and complete the evidence card in order." The Explore steps
backing it are "Point to the source lead end", "Point to the module DC input",
"Trace the three dashed teaching links on the path map with a finger". Pointing
and tracing a supplied map is recognition. The declared level and the authored
task disagree, and the field is self-reported by the same model that wrote the
task.

## Findings

**Well-formed generated objectives vary their Bloom level with the nature of
the unit; a constant level triple is the anomaly.**
"Harnessing LLMs in Curricular Design: Using GPT-4 to Support Authoring of
Learning Objectives" (arXiv 2306.17459) analysed 127 generated learning
objectives for an AI Practitioner course and found they "largely operate at the
appropriate level of Bloom's taxonomy, respecting the different nature of the
conceptual modules (lower levels) and projects (higher levels)." Implication for
this pipeline: differentiation by unit type is the published signature of
objectives that were actually reasoned about. Our four units are all
identification labs and all carry the same triple, so the flatness may be
partly genuine — but nothing in the pipeline can currently distinguish
"correctly flat because these are four foundation labs" from "flat because the
field was copied", and across a 35-unit manifest that distinction is the whole
point of the check.

**A prompted-LLM Bloom classifier generalises across datasets where supervised
classifiers collapse, so the gate can be built to work outside its training
distribution.**
"Cross-Dataset Bloom Question Classification: Supervised Models and Prompted
LLMs" (arXiv 2606.13684, accepted at AIED 2026) reports that "Supervised ML/DL
models degraded substantially on unseen datasets" whereas LLMs "were more
stable", with the best strategy combining in-context examples with
course-specific action verbs. Implication for this pipeline: this repository
spans arbitrary subjects from a curriculum manifest, so a classifier trained on
one subject's item bank is the wrong shape. A prompted classifier seeded with
the unit's own action verbs is the shape that survives, and it can be run as an
independent adjudication of `bloom_level` rather than a reading of it.

## Sources (all fetched and verified to resolve to real, on-topic content)

- "Harnessing LLMs in Curricular Design: Using GPT-4 to Support Authoring of Learning Objectives," arXiv 2306.17459 — https://arxiv.org/abs/2306.17459
- "Cross-Dataset Bloom Question Classification: Supervised Models and Prompted LLMs," AIED 2026, arXiv 2606.13684 — https://arxiv.org/abs/2606.13684

## Discarded

- https://www.jeffbullas.com/thread/can-ai-create-teaching-rubrics-aligned-with-blooms-taxonomy/ — rejected without fetching under the source-quality bar: marketing/content-farm material on an SEO blog, no primary evidence.
- Two researchgate.net entries ("Bloom's Learning Outcomes' Automatic Classification Using LSTM and Pretrained Word Embeddings"; "Automatic applying Bloom's taxonomy to classify and analysis the cognition level of English question items") — rejected without fetching. ResearchGate serves these behind a login wall; a later scan should look for the publisher DOI rather than re-attempting these URLs.
