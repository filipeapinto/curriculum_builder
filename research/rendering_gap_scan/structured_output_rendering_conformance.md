# Rendered-output conformance review — checking the document, not the data behind it

## Why this thread

This is the defect that prompted the scan. All four shipped labs emit their
lesson body as pretty-printed JSON. `outputs/arduino_kit_run_v2/L01/document/L01.md:15-19`:

```
## Engage

{
  "hook": "Three objects can belong to one possible power path even while every connection is safely open on the table.",
  "eliciting_question": "What do you think the coloured line beside a breadboard rail tells you?"
}
```

L02, L03 and L04 fail identically at the same offsets. The QA report reaches
the same conclusion — *"Single templating bug, not four independent failures —
identical section shapes and identical failure across all units."*

The root cause is one function. `runtime/session_bridge.py:207-215` builds the
markdown body like this:

```python
labels = [("Engage", sequence["engage"]), ("Explore", sequence["explore"]), ...]
for title, value in labels:
    lines.extend(["", f"## {title}", "", json.dumps(value, ensure_ascii=False, indent=2)])
```

Eight sections are serialised rather than written. The title, the job sentence
and the objectives *do* render as prose, which is why the top of every file
looks fine.

**No check in the run could have seen this.** `results/unit_checks.json`
records `LAB-SCHEMA-VALID: PASS`, `DOMAIN-SCHEMA-VALID: PASS`,
`DOMAIN-VERIFIER: PASS`, `RECEIPT-HASH-RESOLVES: PASS` — and every one of those
verdicts is correct. The upstream `workers/lab.json` was well-formed; the
defect is entirely downstream of it. The prose contract that *was* violated,
`inputs/unit_prose.v1.md`, is explicitly a document with no schema: the
pipeline's own `prompt.md:44-45` says the prose inputs "have no schema and
cannot have one — read them as prose." So the one contract the document broke
was the one nothing was validating.

## Findings

**Turning a structured representation into readable text is a distinct,
separately evaluated stage — not a formatting detail of the generation step.**
NLG names it *surface realization*, and it has its own benchmark history:
Elder & Hokamp, "Generating High-Quality Surface Realizations Using Data
Augmentation and Factored Sequence Models" (arXiv:1805.07731), reports models
"ranked first on all evaluation metrics in the English portion of the 2018
Surface Realization shared task." Implication for this pipeline: the pipeline
has a content-planning stage (`CIRCUIT`, `EXPERIMENT`, `CHILD_TEXT` producing
`lab.json`) and a realization stage (`_markdown()`), but only the first has
any verdict attached to it. A stage the field considers worth its own shared
task is, here, twelve lines of unchecked string concatenation.

**Format and structure conformance is exactly the class of property current
practice assigns to a deterministic check, not to a model reviewer.**
Braintrust, "What is an LLM-as-a-judge? When to use it (and when to use
deterministic evals)" (26 February 2026): *"Deterministic checks should handle
everything that can be measured directly, including format, schema compliance,
and required fields,"* and *"LLM-as-a-judge should focus only on subjective
dimensions that require language understanding. Separating deterministic checks
from LLM-based scoring improves reliability."* Implication for this pipeline:
"is there a JSON object literal in the learner-facing body of this document" is
measured directly, in a regex, for a fraction of a cent. It should never have
been waiting on a judge — and in this run the judge was bypassed anyway
(`acceptance.json`: `"cross-family judge bypassed"`), so a design that leaned
on one would have shipped this regardless.

**A serious agent benchmark treats the deterministic check as the default and
the model judge as the fallback.** *Agents' Last Exam* (arXiv:2606.05405)
states it *"deliberately avoids LLM-as-judge wherever a deterministic
alternative exists,"* reserving judges for workflows that are genuinely
perceptual. Implication for this pipeline: the correct fix is a cheap
blocking check at emission time, and only then a reader-level reviewer for
what a regex cannot see. Ordering matters — a rendering check that runs after
the expensive reviewers wastes every review cycle spent on an unreadable
document.

**No source in this scan studies this exact defect.** I searched for published
work on structured data leaking verbatim into rendered learner-facing
documents and found none; the closest results were about the inverse problem
(parsing JSON out of model prose). *This is my inference, not a cited finding:*
the reason the literature is thin is that this failure is a software defect in
the emitter rather than a model behaviour, and it is invisible to every
evaluation harness that scores the model's structured output instead of the
artifact a learner receives. The published evidence supports the *principle*
(validate the artifact, deterministically, separately from the schema); the
specific check proposed here is engineering, grounded in this run.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Elder & Hokamp, "Generating High-Quality Surface Realizations Using Data Augmentation and Factored Sequence Models," arXiv:1805.07731 — https://arxiv.org/abs/1805.07731
- Braintrust Team, "What is an LLM-as-a-judge? When to use it (and when to use deterministic evals)," 26 February 2026 — https://www.braintrust.dev/articles/what-is-llm-as-a-judge
- "Agents' Last Exam," arXiv:2606.05405 (full text via the HTML rendering) — https://arxiv.org/html/2606.05405v1

## Discarded

- https://arxiv.org/abs/2001.03830 — "Revisiting Challenges in Data-to-Text Generation with Fact Grounding." Fetched; real and on the general topic, but the abstract does not contain the content-planning / surface-realization decomposition the search snippet implied, and its actual subject is factual hallucination in sports reports. Discarded rather than cited loosely.
- Search query `output guardrails deterministic validators content generation pipeline block before publishing format validator Guardrails AI` — the search tool returned `Web search error: unavailable` and no results. Not retried with the same wording; the deterministic-validator framing was obtained from the Braintrust and ALE sources instead.
- First query for this thread (`validating rendered document output LLM generated raw JSON leaking into prose rendering conformance check`) returned only output-*parsing* material — recovering JSON from model prose, the inverse of our defect. Nothing from that result set was fetched or kept.
