# Rendered-page QA — the check that ran, passed, and proved nothing

## Why this thread

This run *did* have a check on the shipped PDF. It passed. It is worth being
precise about what it asserted, because it is the clearest example in the
fixture of a green check that carries no information.

`runtime/checks.py:82` — `rasterize_and_check_nonblank` — rasterizes every page
at 200 dpi, confirms the raster page count matches the PDF page count, and then
fails only if a page is near-uniform:

```python
extrema = image.convert("L").getextrema()
if extrema is None or extrema[1] - extrema[0] <= 2:
    raise CheckFailure(f"blank PDF page: {page}")
```

A page of pretty-printed JSON is dense black text on white. Its extrema span
almost the full range. It passes by the widest possible margin.
`L01/acceptance.json` duly records five page renders with their SHA-256 hashes
and `"terminal_state": "ACCEPTED"`.

`policy/controller.v1.yaml` lists both `PDF_RENDER` and `PDF_VISUAL_QA` as
states, and an ordering rule justifies them: *"PDF_RENDER and PDF_VISUAL_QA
precede FINAL_ACCEPTANCE. A lab correct as markdown and wrong at print size is
caught while revision is still cheap."* No `PDF_VISUAL_QA` verdict artifact
exists anywhere in the run. The intent was in the policy; the implementation
was a blank-page detector.

## Findings

**Snapshot-based visual regression on rendered PDF pages is established,
tooled practice, not a research proposal.** `moshensky/pdf-visual-diff` is
*"a library for testing visual regressions in PDFs. It uses pdf.js to convert
PDFs into PNGs and jimp for image comparisons."* Its `comparePdfToSnapshot`
rasterizes each page, pixel-compares it against a stored expected snapshot, and
on mismatch writes `.new` and `.diff` images so a human can see what moved.
Implication for this pipeline: the rasterization half already exists in
`rasterize_and_check_nonblank` and the hashes are already recorded in
`acceptance.json`. What is missing is a comparison target — the run compares
each page against nothing.

**Perceptual properties of a rendered artifact are the one place a model
reviewer is warranted, and it should be asked narrow probes.** *Agents' Last
Exam* (arXiv:2606.05405) reserves LLM judging for workflows whose deliverable
is perceptual — *"video clip, game screenshot, rendered scene, etc"* — and
scores them with *"narrow, evidence-anchored yes/no probes whose answers code
aggregates into the score."* Implication for this pipeline: page-level
questions that no pixel comparison answers ("is the diagram legible at print
size?", "does any section run off the page?") belong to a vision reviewer at
`PDF_VISUAL_QA`, asked as specific probes. Note this would *also* have caught
the JSON dump, but as a fourth line of defence — expensive, late, and after the
document was already built.

**A pixel-snapshot check would not reliably have caught this defect either.**
*My inference, stated because the thread would otherwise oversell the fix:*
these are first-run documents with no prior snapshot to diff against, and
generated lessons legitimately differ page-to-page across units, so
snapshot-diffing suits regression detection on a stable template rather than
first-emission validation. That is precisely why this thread does not produce
a standalone rendering-conformance agent — the text-level check in
`structured_output_rendering_conformance.md` does that job earlier and more
cheaply. This thread's contribution is narrower: it explains why an existing
green check was worthless, and it supplies the page-level checks worth adding
once the text-level gap is closed.

## Sources (all fetched and verified to resolve to real, on-topic content)

- `moshensky/pdf-visual-diff` — visual regression testing for PDFs (project repository, primary) — https://github.com/moshensky/pdf-visual-diff
- "Agents' Last Exam," arXiv:2606.05405 (full text via the HTML rendering) — https://arxiv.org/html/2606.05405v1

## Discarded

- https://applitools.com/blog/3-steps-visual-testing-pdf/ — "3 Steps to Visual Testing for PDF Files." Returned HTTP 403 Forbidden on first fetch and 403 again on the single permitted retry. No content retrieved, so nothing was cited from it; the claim it would have carried is supported by the `pdf-visual-diff` repository instead. A later scan should not expect this URL to fetch.
- The Medium "PuppetMaster" writeup and the `softwaretestinghelp.com` and `getautonoma.com` listicles from the same search set were rejected on the source-quality bar without fetching — practitioner blog and SEO comparison content restating the same technique the primary repository documents directly.
