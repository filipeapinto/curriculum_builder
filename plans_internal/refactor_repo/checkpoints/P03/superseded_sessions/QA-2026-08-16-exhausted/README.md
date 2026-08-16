# Superseded P03 QA session — 2026-08-16 — QA_FAILED / MAX_ITERATIONS_EXHAUSTED

This directory preserves, unaltered, the complete record of the first P03 QA session.
It is **evidence, not an active session**. Nothing here was produced by, or may be
counted toward, the current checkpoint's independent QA gate.

- Review session id: `01a00b6a-8a98-7e30-a456-d574b9f40355`
- Terminal state: `QA_FAILED`, reason `MAX_ITERATIONS_EXHAUSTED`, 5 of 5 rounds,
  5 findings still at threshold (`verdict.json`).
- Independent postmortem session id: `01a00be9-9be1-7480-afc5-5ddc6cec54d1`
- Postmortem classification: `SPECIFICATION_DEFICIENT`, confidence high
  (`postmortem.md`).

## Why the session is exhausted and must not be reused

The postmortem found that criterion 7 of the shared checkpoint criteria required the
exact artifact under review to already contain the successful result of that same
review. Every revision therefore became a new, not-yet-verified artifact, so at least
one blocker was unavoidable no matter what was repaired. It explicitly recorded that
this was not an integrity breach — every round's honesty audit reported
`prior_rounds_consistent: true` — and not primarily reviewer scope escalation.

The postmortem also returned four genuinely open, non-circular findings for artifact
remediation. Those are addressed in the current checkpoint, not here:

| Finding | Subject | Where it is addressed now |
|---|---|---|
| P03-QA-007 | Ownership overlap contradicted Test 1 | `prompts/resolved/prompt_manifest.resolved.v1.yaml` → `path_ownership_model`; scan at `../../evidence/test1_ownership_overlap_scan.v2.txt` |
| P03-QA-004 | Pre-move reconciliation never recorded | `exceptions/source_move.v1.yaml` → `premove-dryrun-reconciliation-not-recorded-contemporaneously`; evidence at `../../evidence/test2_*` |
| P03-QA-005 | Path ledger descriptive, not complete | `../../evidence/ledger/` |
| P03-QA-006 | Deliverables lacked digest coverage | `../../evidence/digest_manifest.json` |

## Contents

- `session.json`, `verdict.json` — the gate script's own session and terminal records.
- `rounds/round-01..05.*` — every request, response, event stream and stderr, exactly
  as the gate script wrote them.
- `postmortem.{md,json,request.md,response.json,events.jsonl,stderr.txt}` — the fresh
  independent session's diagnosis.
- `reports/P03_checkpoint_report.v1..v5.md` — all five superseded artifact versions
  that were submitted across the five rounds.
- `evidence_from_ee8922a/` — diagnostic evidence files produced while writing those
  superseded reports. They describe the provisional worktree's state at the time, not
  the current checkpoint, and are retained only for traceability.

## Provenance of these files

`rounds/round-01..03.*` and `session.json` as committed in `ee8922a` came from that
commit. Rounds 04 and 05, `verdict.json`, the postmortem files, and reports v4/v5 were
never committed; they were copied read-only from the preserved provisional worktree
`/Users/filipepinto/Projects/curriculum_builder_wt/refactor-p03-p10-direct`, which was
not modified in any way.
