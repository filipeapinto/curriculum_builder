---
name: sota-incident-analyze
description: Reconstruct an LLM or agent execution incident from an approved evidence boundary. Use when serving as the incident analyst and producing an evidence-linked timeline or matrix that separates facts, attributed claims, inferences, competing explanations, and unknowns.
---

# SOTA Incident Analyze

1. Inspect only evidence authorized by the approved plan; preserve source artifacts unchanged.
2. Assign stable IDs and provenance to events, actors, inputs, operations, outputs, resources, artifacts, and evaluations.
3. Classify each statement as verified fact, attributed claim, inference, competing explanation, or unknown.
4. State confidence and the evidence that could resolve each material unknown.
5. Do not import external-review conclusions into the factual incident record.
6. Do not infer token use, causality, intent, failure, or acceptance from artifact volume alone.

Return the incident matrix, timeline, evidence gaps, competing explanations, confidence, and unresolved claims.

