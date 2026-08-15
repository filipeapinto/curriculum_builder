# Structured-output rendering conformance — a reviewer that reads the shipped artifact

## Why this thread

Every one of the four lessons shipped its body as a raw JSON dump. The QA
report calls it the top Critical finding: "Document renderer dumps raw JSON as
lesson body. All 4 lessons (L01-L04). Sections under 'Engage/Explore/Explain/...'
contain literal structured objects instead of prose", quoting
`L01/document/L01.md:15-19`.

The root cause is in this repository, at `runtime/session_bridge.py:211`:

```python
for title, value in labels:
    lines.extend(["", f"## {title}", "", json.dumps(value, ensure_ascii=False, indent=2)])
```

Lines 212-214 do the same for `identification`, `troubleshooting` and
`safety`. Eight of roughly eleven sections per unit are serialized objects. The
renderer never had a prose path for them.

What makes this a reviewer gap rather than only a bug is *which checks passed
anyway*. `L01/results/unit_checks.json` records `LAB-SCHEMA-VALID: PASS`,
`DOMAIN-SCHEMA-VALID: PASS`, `DOMAIN-VERIFIER: PASS`,
`RECEIPT-HASH-RESOLVES: PASS`. All four are green. They are green because they
validate `workers/lab.json` — the *upstream* structured object, which really is
well formed — and never look at `document/L01.md` or the PDF that a child
actually receives. The only post-render check in the codebase is
`rasterize_and_check_nonblank` (`runtime/checks.py:82`), and a page of pretty-
printed JSON is not blank.

No check in this pipeline reads the consumed artifact.

## Findings

**Structural validity of an intermediate representation says nothing about the
usability of the artifact downstream of it.**
"When Correct Isn't Usable: Improving Structured Output Reliability in Small
Language Models" (arXiv 2605.02363) names this the "structured-output
reliability gap" and insists that "Deployed language models must produce
outputs that are both correct and format-compliant." Its headline measurement
is the shape of our failure: naive prompting reached "up to 85% task accuracy
on GSM8K but 0% output accuracy across all models" — the content was right and
the delivered artifact was worthless. Implication for this pipeline: the run's
own framing, 100% schema validity against ~2% semantic success, is the same
split, and it is not detectable from the schema side. The measurement has to be
taken on the file that ships.

**Where label fidelity actually matters, current practice anchors the artifact
to deterministic generation rather than trusting a generative step to preserve
it.**
"CAGE: Bridging the Accuracy-Aesthetics Gap in Educational Diagrams via
Code-Anchored Generative Enhancement" (arXiv 2604.09691) reports that diffusion
models "catastrophically garble text labels" while code-based generation
ensures label correctness, and therefore emits executable code first and only
then lets a ControlNet stage refine it while "preserving label fidelity",
evaluated over 400 K-12 diagram prompts. Implication for this pipeline: the
architectural lesson transfers even though the medium differs — the trustworthy
step is the deterministic one, and the check belongs immediately after it, on
its output.

**This thread is thin, and that is itself the finding.**
Two sources support it. The literature on structured output is almost entirely
about constraining what a *model* emits; our defect is a hand-written renderer
downstream of a model that behaved correctly. That asymmetry is why the check
is missing: the pipeline inherited the industry's attention to model-output
validation and inherited its blind spot about the rendering step. Implication
for this pipeline: do not wait for a paper about this. The check is
deterministic, cheap, and needs no research — assert that no section body of a
shipped document parses as a JSON object or array.

## Sources (all fetched and verified to resolve to real, on-topic content)

- "When Correct Isn't Usable: Improving Structured Output Reliability in Small Language Models," arXiv 2605.02363 — https://arxiv.org/abs/2605.02363
- "CAGE: Bridging the Accuracy-Aesthetics Gap in Educational Diagrams via Code-Anchored Generative Enhancement," arXiv 2604.09691 — https://arxiv.org/abs/2604.09691

## Discarded

- https://arxiv.org/abs/2508.15866 — "Correctness-Guaranteed Code Generation via Constrained Decoding". Fetched. The search snippet attributed to it the sentence "conforming to context-free grammatical rules is far from semantic and runtime correctness"; the retrieved abstract does not contain it. The paper is about context-sensitive parsers for runtime-critical robotics code. Off topic for document rendering, and citing it would have carried a claim the source does not make.
- Entire first result set for "structured output validation LLM JSON leaking into rendered document conformance check" — Medium posts, dev.to, glukhov.org, projectsupply.in, collinwilkins.com, deepinspect.ai. Rejected without fetching under the source-quality bar: they cite only each other, and they are topically inverted anyway (validating JSON a model emits, not detecting JSON a renderer failed to consume).
