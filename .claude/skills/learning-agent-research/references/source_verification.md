# Source verification

Read this before citing anything. Every URL that ends up in a thread file or
in the recommendation JSON must first have a verification entry in
`action_log.jsonl`, and `scripts/validate_outputs.py` enforces that
mechanically.

## The procedure

For each candidate source turned up by search:

1. Fetch the URL and read what came back.
2. Compare it against the specific claim you intend to cite it for — not
   against the topic in general. "This paper is about LLM judges" is not
   verification of "this paper recommends cross-family judges."
3. Log a verdict and a decision.
4. Only then may the URL appear in an artifact.

## Verdict vocabulary

Use these four verdicts so the log reads consistently across scans and across
different people running them.

**VERIFIED** — real content retrieved, and it supports the claim. Quote or
paraphrase the supporting line in the log entry so the verification is itself
checkable. Decision: `keep`.

**PARTIALLY VERIFIED** — the source demonstrably exists and is on topic
(title, authors, abstract, subject tags all match) but the body text could not
be extracted. This is common with arXiv PDFs whose text streams do not decode.
Decision: `keep but cite conservatively` — you may cite it for the general
architectural or topical claim, never for a specific number or quotation you
did not actually read.

**CORRECTED** — content retrieved, but it contradicts what the search snippet
implied. This is the most valuable verdict in the log, because it is the one
that caught a wrong claim before it shipped. Record both the original
assumption and the correction, then cite the source accurately for what it
actually says. Decision: `keep, cite accurately (do not claim X)`.

**FAILED** — 404, paywall, login wall, HTTP 403, or unextractable content with
no working alternate form. Decision: `DISCARD - do not cite`, and list it in
the thread file's Discarded section so nobody re-fetches it next scan.

## Retry ladder

A fetch failure is more often a transport problem than an existence problem.
Try one alternate form before discarding:

- arXiv: `arxiv.org/pdf/<id>` → `arxiv.org/abs/<id>` → `arxiv.org/html/<id>`.
  The abstract page usually yields clean text when the PDF does not, and an
  abstract is enough to verify most topical claims.
- DOI links: follow the redirect and fetch the resolved publisher URL.
- Publisher pages returning 403: retry once. If it persists, discard — do not
  substitute your memory of the paper for its content.

Log each rung of the ladder as its own entry. The retry history is what shows
a later reader that a discard was earned rather than lazy.

## Source-quality bar

**A page resolving is not the same as a page being evidence.** Reject, without
bothering to fetch, sources that are content-farm or SEO-aggregator material:
recycled statistics with no primary source, listicles, vendor blogs that cite
only other vendor blogs. In the reference run an entire result set for a
specific hallucination-rate statistic was discarded on these grounds even
though the pages would have loaded, and the statistic was simply dropped
rather than cited weakly.

Prefer, in rough order:

1. Papers and preprints with retrievable abstracts.
2. Primary vendor documentation on their own quality/trust/methodology
   (a platform describing its own review pipeline is a primary source about
   that pipeline).
3. Established standards and professional-body guidance (e.g. a science
   teachers' association safety checklist) — usually the best grounding for a
   safety or compliance recommendation, because it predates the LLM framing
   and is what practitioners are actually held to.
4. Named practitioner analyses with checkable specifics.

Dropping a claim you cannot source well is always available and is usually the
right move. An unsupported number is a liability; its absence costs nothing.

## Anti-patterns

- Citing from memory because the paper is famous. Fetch it.
- Citing a snippet because it says what you wanted. Fetch it.
- Keeping a source whose content turned out to be about something adjacent,
  on the grounds that it is "close enough."
- Padding a thin thread with weak sources so it looks as substantial as the
  others. Say the thread is thin instead; that is a finding.
