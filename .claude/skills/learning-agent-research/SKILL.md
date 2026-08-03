---
name: learning-agent-research
description: Runs a grounded, source-verified scan of the state of the art in LLM-driven curriculum and lesson design, and turns it into a ranked set of recommended reviewer agents where every citation has been fetched and checked before it was written down. Use this skill whenever someone wants to know what current research and production practice say about generated educational content, review/QA pipelines for LLM-authored lessons, or which reviewer, judge, or gate agents a curriculum pipeline is missing — for example "refresh the SOTA research on LLM curriculum design", "re-run the SOTA scan against the newer run", "what agents should be reviewing these labs?", "research best practice for QA-ing AI-generated lesson content", "our pipeline shipped four broken lessons, what does current practice say should have caught that?", or "update our sources, some of these look stale". Also use it proactively whenever someone is about to recommend reviewer agents, QA gates, judges, or pedagogy checks for generated learning content based on memory or on search-result snippets alone — this skill exists precisely because ungrounded recommendations and unfetched citations are the two failure modes that make that kind of output worse than useless.
---

# LLM-driven learning: grounded SOTA scan

This skill packages a research methodology, not a set of answers. Running it
produces a fresh scan: research notes per topic, a machine-readable array of
recommended reviewer agents, and a faithful log of how the scan was actually
performed.

Two rules carry most of the value, and both exist because of specific ways
this kind of research fails:

1. **Ground before you search.** Research threads must be derived from defects
   you observed in real pipeline output, not from a generic topic taxonomy. A
   scan that starts from "what are the topics in AI education research?"
   produces recommendations nobody can act on, because no recommendation is
   attached to a real failure. You literally cannot fill in the
   `issues_resolved` field without ground truth, and that field is what makes
   the output worth reading.

2. **Fetch before you cite.** Every source gets retrieved and read before its
   URL appears in any artifact. Search snippets routinely misdescribe the
   thing they link to — in the reference run, one paper's snippet implied it
   endorsed cross-family LLM judging when the paper argues for empirically
   low-bias judges regardless of family, and another appeared to be about
   English grade-level readability when it is about Arabic CEFR levels. Both
   would have become confident, wrong claims. A research artifact with
   citations that do not support its claims is worse than no artifact, because
   it launders unfounded confidence into something that looks checkable.

## Output

Write everything to one output directory, default
`docs/research/<scan-name>/` (the reference run used
`docs/research/sota_agents_research/`):

- `<thread-name>.md` — one file per research thread
- `sota_agents.v<N>.json` — the recommendation array (pick the next unused
  `N` in the directory; do not overwrite a previous scan)
- `action_log.jsonl` — one JSON object per action, in the order taken

Exact shapes for all three are in `references/output_contracts.md`. Read it
before writing the first artifact.

## Step 1 — Ground in real output

Read the actual generated artifacts and any existing QA/review report before
running a single search. In the reference run this meant every lesson document
plus the QA report for the run under review.

Read the QA report *last*, after forming your own impression of the documents,
so you notice defects it missed rather than only inheriting its framing.

Write down the concrete defects: what shipped wrong, how systemic it was (one
bug reaching every unit, or four independent failures), which existing checks
were supposed to catch it, and which were skipped or inert. Log this as an
`analysis` entry.

If there is no real output to ground against, stop and say so rather than
researching in the abstract. A scan with no ground truth is a literature
summary, which is a different and much less useful deliverable — offer that
explicitly instead of silently substituting it.

## Step 2 — Derive threads from the defects

Turn the defect list into research threads by asking, per defect: *what kind
of reviewer would have caught this?* One thread per reviewer archetype. The
reference run derived seven threads (multi-agent judging, Bloom's/pedagogy
validation, readability and vocabulary control, domain-fact verification,
physical safety review, structured-output rendering conformance, commercial
platform QA practice) from six observed defects plus one thread on what
production platforms actually do.

Aim for 5-8 threads. Fewer and you are writing one essay; more and each thread
gets too little verification effort to be trustworthy.

Include at least one thread on **commercial/production practice**, not only
academic work. Papers describe what is possible; shipping platforms reveal
which of those things survived contact with real users, and their public
quality/trust pages are citable primary sources.

## Step 3 — Search each thread

Run one or more searches per thread, covering both academic sources (papers,
preprints, surveys) and commercial ones (vendor engineering/quality pages,
production writeups, credible practitioner analyses).

Log every search with its query, the thread it serves, and the result count.
When a query returns off-target results, log that judgement and refine rather
than silently retrying — the reference run's first child-safety query returned
online-safety/CSAM material instead of physical-hazard instructional review,
and recording the mismatch is what made the refinement legible afterwards.

Treat search results as **candidates only**. Nothing from a snippet enters an
artifact.

## Step 4 — Verify every source

For each candidate, fetch the URL, read what actually came back, and record a
verdict plus a keep-or-discard decision in the log before citing it anywhere.

`references/source_verification.md` has the verdict vocabulary
(VERIFIED / PARTIALLY VERIFIED / CORRECTED / FAILED), the retry ladder for
fetch failures, and the source-quality bar that rejects pages which resolve
but are not evidence. Read it before starting verification.

The short version: retry once via an alternate URL form before discarding;
when the fetched content contradicts what the snippet implied, correct the
claim rather than dropping the source; and a page resolving is not the same as
a page being evidence.

## Step 5 — Write one file per thread

Use `assets/thread_template.md`. Each thread file states why the thread exists
(anchored to the specific defect), what was found with claims attributed to
named sources, the verified source list, and — importantly — what was
discarded and why.

The discard section is not bookkeeping. It is what lets the next reader tell a
thin thread from a thoroughly searched one, and it stops a later scan from
re-fetching the same dead URL.

## Step 6 — Write the recommendation array

One entry per recommended reviewer agent, using the schema in
`references/output_contracts.md`. Each entry must name a real gap in the
pipeline you grounded against and cite only sources you logged as kept.

Recommend agents, not features. Each entry should be something that could be
instantiated as its own reviewer with its own inputs and its own verdict. If
two entries would run at the same point on the same input for the same reason,
they are one agent.

Keep the recommendation count honest — the reference run produced five agents
from seven threads, because two threads informed other agents rather than
justifying their own.

## Step 7 — Validate

Run the validator before declaring the scan complete:

```bash
python3 <skill-dir>/scripts/validate_outputs.py <output-dir>
```

It checks that the log is well-formed, that the JSON matches the schema, and —
the check that matters — that **every URL cited in the JSON or in a thread
file has a corresponding kept-verification entry in the action log**. That is
the mechanical enforcement of rule 2: a citation with no verification record
is a finding, not a formatting nit, and the validator exits non-zero on it.

Fix anything it reports rather than explaining it away. If a citation cannot
be traced to a verification, either verify it now or remove it.

## Logging

Append to `action_log.jsonl` as you go, not reconstructed at the end. The log
is a research provenance record: someone later needs to be able to tell
whether a claim rests on a paper that was read or a snippet that was skimmed,
and a summary written afterwards cannot support that.

```bash
python3 <skill-dir>/scripts/log_action.py <output-dir>/action_log.jsonl \
  action=web_fetch_verify url=https://... \
  claim="what this source is being cited for" \
  result="VERIFIED - abstract retrieved, matches claim" \
  decision="keep, cite in readability thread"
```

Log reads, searches, fetch verdicts, analysis judgements, and writes. Include
the failures and the corrections — a log showing only successes is evidence of
a log written from memory, and it hides exactly the discard reasoning that
makes the scan auditable.
