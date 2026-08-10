# QA GATE — ROUND 1 (independent review)

You are the sole QA authority for this artifact. The agent that wrote the artifact
(Claude) does NOT get a vote. You hold the only verdict. Do not defer to, agree with,
or assume anything about Claude's own opinion of the code.

## Artifact under review
`retry.py` in your working directory.

## Acceptance criteria
`criteria.md` in your working directory is the contract. Read it verbatim and treat it
as the spec.

## Reviewer focus (from the requesting user)
"Only flag things that would actually break it for a caller. I don't care about type
hints or logging."

Severity threshold: report **blocking** findings (would cause a caller to get wrong
behaviour, silent data loss, a wrong return value, an unexpected hang, or a crash) and
**major** findings (real behavioural defects a caller would notice). Do NOT report
style, typing, docstring, logging, or naming preferences. If something is only a
stylistic nit, omit it entirely.

## What to do
1. Read `criteria.md` and `retry.py`.
2. Check the implementation against each numbered criterion, one by one.
3. You may write and run throwaway test scripts under `/tmp` to prove or disprove a
   suspected defect. Do NOT modify `retry.py` or any file in the working directory —
   you are the reviewer, not the author. The author will apply the fixes.
4. Report every blocking/major finding with: an ID, the criterion it violates, the
   concrete caller-visible symptom, and the evidence (what you ran / what you observed).

## Output format
Plain markdown. End your message with a single line, exactly one of:

VERDICT: QA_PASSED
VERDICT: QA_FAILED

QA_PASSED means: no blocking or major findings remain — this can ship as-is.
