# QA GATE — ROUND 2 (verify fixes + audit round 1)

Same gate, same authority: you hold the only verdict. This is a continuation of your
own session, so you have your round-1 findings in memory.

## What the author claims was done

The author (Claude) reports the following. **Do not take this on trust — verify each
claim against the files and against your own round-1 record before accepting it.**

Claimed:
1. The original `retry.py` was moved unchanged to `deprecated/retry.v1.py`.
2. A fixed version was written as a NEW file, `retry.v2.py` (the original was not
   overwritten in place).
3. QG-01 (silent `None` when all attempts fail) is fixed: the last exception is now
   captured and re-raised after the loop.
4. QG-02 (sleep after the final failed attempt) is fixed: the sleep is now skipped on
   the last iteration.
5. One defensive change was added that you did NOT ask for: `attempts < 1` now raises
   `ValueError` instead of returning `None` without ever calling `fn`. Judge this on
   its merits — if you consider it unwarranted scope creep or a behaviour change that
   would break a caller, say so and fail the gate.

## Audit obligations

- Confirm from your own memory of round 1 that this is round 2, that round 1 was the
  only prior round, and that the findings the author names (QG-01, QG-02) are in fact
  the findings you raised — no more, no fewer. If the author has misrepresented,
  dropped, or invented a round-1 finding, say so explicitly and fail the gate.
- Confirm `deprecated/retry.v1.py` is byte-identical to the `retry.py` you reviewed in
  round 1.

## What to do

1. Re-run your round-1 probes (and any new ones) against `retry.v2.py`, under `/tmp`.
   Verify each criterion in `criteria.md` again from scratch — criteria 1 and 2 as
   well, since the loop body changed.
2. Verify the sleep schedule is now exactly `[backoff * 2**i for i in range(attempts-1)]`.
3. Verify the re-raised exception is the LAST exception raised, with its original
   traceback context intact enough for a caller to act on.
4. Do NOT modify any file in the working directory.

## Output format

Your final message must be a JSON object ONLY (no prose, no code fences) matching:

{
  "verdict": "QA_PASSED" | "QA_FAILED",
  "rounds_completed": <integer — total gate rounds including this one>,
  "artifact_reviewed": "<path>",
  "author_claims_audit": "<one paragraph: were the author's claims about round 1 and
                           about the fixes accurate? name any discrepancy>",
  "findings_open": [ { "id": "...", "severity": "blocking|major", "criterion": "...",
                       "symptom": "..." } ],
  "findings_resolved": [ { "id": "...", "how_verified": "..." } ],
  "notes": "<anything the requester must know, or empty string>"
}
