# Retired P03 QA session 2 — 2026-08-16 — retired after round 2, not exhausted

Complete record of the second P03 QA session, preserved unaltered.

- Session id: `01a00c05-c34c-7c72-b3c8-ce82757de10c`
- Rounds run: 2 of a possible 5. Both returned `FAIL`.
- Terminal state: **retired by decision**, not `QA_FAILED` and not exhausted.

## Why it was retired

Round 2 **retired both of round 1's findings** after inspecting the re-executed move's
evidence, so the artifact work this session demanded was done and is reflected in the
current checkpoint. It was retired for two configuration defects that made a clean,
verified `QA_PASSED` unreachable from inside it regardless of artifact quality:

1. `qa_gate.py round` has no `--focus`; the focus is fixed at `start` and replayed
   verbatim. It contained the v1 digests, so every later round bound the gate to a
   superseded checkpoint — which is precisely what round 2's
   `P03-QA-DIGEST-BINDING-MISMATCH` found, and it cannot be fixed within a session.
2. Two grounding sources passed at `start` — `exceptions/source_move.v1.yaml` and
   `evidence/digest_manifest.json` — necessarily change between rounds. The gate hashes
   grounding each round and `verify` reports `GROUNDING_CHANGED` on a change, so this
   session could never produce a clean verification.

Round 2's other finding, `P03-QA-LEDGER-NOT-CURRENT`, was fixed in the artifact: the
gate's post-freeze relocation of the superseded version into `deprecated/` is now staged
and appears in the ledger, and `QA/` and `deprecated/` are explicitly accounted for.

Journal records `ACT-045` and `ACT-046` record the retirement and its reason.

## A disclosed handling error

The replacement session was first opened with `qa_gate.py start --force` against the
live `QA/` directory. `--force` overwrites in place rather than archiving, so it
truncated this session's `session.json`, `rounds/round-01.request.md` and
`rounds/round-01.events.jsonl` before failing with `QA_ERROR / CODEX_TURN_FAILED`. All
three were restored byte-for-byte from the git index, which already held them staged,
and this session was then archived here **before** the replacement session was opened.
No round response, verdict or meta file was affected.
