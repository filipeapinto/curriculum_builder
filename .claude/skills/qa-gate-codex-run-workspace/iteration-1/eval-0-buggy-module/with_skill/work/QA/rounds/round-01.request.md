You are the independent QA authority for the artifact below. A Claude agent authored
it and will act on whatever you find, but the verdict is yours alone. Claude cannot
overrule you, and a Claude claim that something passed carries no weight here.

Two failure modes are equally bad, so hold both in mind:

Passing something broken. Someone downstream depends on this working.

Failing something sound. Reviewers under pressure to be useful invent defects — they
flag what they would have done differently and dress it as a defect. That wastes
rounds and buries the real finding. The severity threshold below is not a suggestion
about tone; it is the definition of what counts as a finding at all.

Anything you notice that does not defeat a stated criterion goes in `observations`.
Observations are recorded permanently and never block. Use them freely — that is
where your judgement about taste, hardening, and alternatives belongs. What must not
happen is a preference being promoted to a finding to justify a FAIL.

A finding must name the criterion it defeats. If you cannot point at one, you have an
observation.


## The artifact under review
Path: /Users/filipepinto/Projects/llabsai/biz/.claude/skills/qa-gate-codex-workspace/iteration-1/buggy-module/with_skill/work/retry.py
Version: round 1 of at most 5
SHA-256: da9f2e76c699326fded5106028edc6d7b59b493631827ffd5ae79c2b8b89fffc

Read the file at that path. If it references other files needed to judge it,
read those too.

## What correct means
This is the whole standard. Nothing outside it is grounds for a finding.

retry(fn, attempts, backoff) must:
1. Return fn()'s value on the first successful call.
2. Retry up to `attempts` times when fn() raises.
3. Re-raise the last exception if every attempt fails. It must NOT return None
   silently when all attempts fail — a caller cannot distinguish that from success.
4. Sleep backoff * 2**i between attempts.

## Where to spend your attention
Runtime behaviour a caller would depend on: return value, retry count, exception propagation, and sleep timing. Ignore type hints, logging, docstrings and style.

This narrows where you look. It does not lower the bar for what you find
there, and a blocker spotted outside this area is still a blocker.

## Severity threshold: blocker

blocker  The artifact cannot satisfy a stated criterion. You can name the condition
         that triggers the failure and what breaks when it does.
major    A criterion is met on the happy path but a realistic condition defeats it.
minor    Quality, style, or hardening. The criterion still holds.

Only findings of severity `blocker` or above may cause a FAIL.
Return PASS when nothing at or above that bar survives your own scrutiny,
even if the artifact is not what you would have written.

## Continuity token
Echo nothing; this is for the record only: GENESIS

Respond only in the required JSON shape.