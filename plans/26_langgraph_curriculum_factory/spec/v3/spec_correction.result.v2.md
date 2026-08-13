# Plan 26 spec correction (v2 -> v3) — result

status: `SPECIFICATION_CORRECTED_AND_INDEPENDENTLY_VERIFIED`

This is the v2->v3 counterpart of
`plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec_correction.result.v1.md`
(v1->v2). That correction, and its QA evidence, are historical, immutable,
and untouched by this task. This document reports a second, independent
correction pass: recovering `plans/27_langgraph_curriculum_factory_remediation`'s
Run 27 attempt from its `N20_PROVIDER_TRANSPORT` `BLOCKED` result
(`plans/27_langgraph_curriculum_factory_remediation/results/N20_PROVIDER_TRANSPORT.result.v1.json`),
per `plans/27_langgraph_curriculum_factory_remediation/n20_recovery.plan.v1.md`.

Status is reported here because the underlying gate `verify` operation
returned a witnessed, hash-chain-valid `QA_PASSED` (below), across two rounds.
Claude did not originate this verdict; Codex did, through the
`qa-gate-codex-run` skill.

## Artifacts

| Artifact | Path | SHA-256 |
|---|---|---|
| Corrected spec (v3, passing version) | `plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md` | `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c` |
| Corrected spec, round-1 attempt (superseded, one major finding) | `plans/26_langgraph_curriculum_factory/spec/v3/deprecated/langgraph_curriculum_factory.spec.v3.md` | `419d1e91d197e967302dab62e356c3fefa861d45585a089bf29b616264f66d87` |
| Predecessor spec (v2, historical, immutable) | `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md` | `99052a181052bbbaf8077a152af22db6f248d552f38dd73302a3c34abc11b758` (reconfirmed unchanged before and after this task) |
| Predecessor spec (v1, historical, immutable) | `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md` | `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6` (reconfirmed unchanged) |
| QA criteria | `plans/26_langgraph_curriculum_factory/spec/v3/spec_v3_correction_criteria.v1.md` | new, criteria SPEC3-T00–T08 plus falsification targets |

**Naming note.** The passing filename ends `.v4.md`, not `.v3.md`. The
document is specification v3 — its own header/status line says
"version 3" and it corrects v2 — but `.v4` is the `qa-gate-codex-run` skill's
own internal round-lineage numbering (`spec/v3/QA/`), which bumps the trailing
version number on every QA fix round regardless of the document's own
version identity. Round 1 was reviewed under the filename `...spec.v3.md`;
it drew one major finding; the fix was submitted as the tool-assigned next
version, `...spec.v4.md`, and passed. Round 1's file is preserved unedited
at `spec/v3/deprecated/`. Neither v1 nor v2 was touched by any of this.

v1 and v2 were never edited, moved, deprecated, or deleted. No Run 27 v1
result, evidence, patch, log, policy, schema, model-job configuration,
runtime code, test, or implementation graph file was changed by this task.

## Corrections made (recovery plan, "Correction design, 1. Correct the specification")

| # | Bounded change required | Where in v3 |
|---|---|---|
| 1 | Zero literal retired-provider/retired-family identifiers in active text (stricter than v2, which tolerated historical-narrative occurrences) | Systematic neutralization across §0, §1.2, §2.0–§2.4, §3.1, §6.3, §7.1, §7.2, §7.4, §9, §17.2, §18, §19, §20.1–§20.2, §21 |
| 2 | Canonical authorized-input projection delivered over stdin, not by file access | §7.1 (workspace bullet list), §7.2 (rewritten invocation shape and narrative) |
| 3 | Deterministic CLI-schema projection, inline JSON, `$schema` stripped, external `$ref` rejected; canonical schema remains post-execution admission authority | §7.1 (proof class 4, receipt list), §7.2 |
| 4 | Receipts bind canonical input digest, canonical schema digest, CLI-schema-projection digest, exact argv policy, requested identity, observed identity | §7.1 (extended receipt-field list) |
| 5 | Machine-readable stream events; executed identity from top-level assistant turn, not aggregate usage map | §7.1 (proof class 4), §7.2 |
| 6 | Empty tools + strict empty MCP configuration checked from the initialization event; any exposed tool beyond structured output fails closed | §7.1 (new proof-class-5 half), §7.2 |

No graph topology, reducer, retry, denominator, persistence, repair, or
terminal rule changed (verified structurally against v2 outside the sections
named above — SPEC3-T07).

## Independent Codex QA gate (SPEC3-T00–T08)

- **Transport:** `app-server` (default), via the `openai-codex` plugin.
- **Session:** `019ffbeb-3f45-7440-a83e-aa560938dc98`. Rollout witness file:
  `~/.codex/sessions/2026/08/13/rollout-2026-08-13T12-18-46-019ffbeb-3f45-7440-a83e-aa560938dc98.jsonl`.
- **Rounds:** 2 of 5 max, both witnessed by Codex.
- **Threshold:** `major`. **Criteria:** SPEC3-T00 through SPEC3-T08, plus
  falsification targets, as written in `spec_v3_correction_criteria.v1.md`.
- **Round 1 verdict:** `FAIL`. One major finding, `SPEC3-QA-001`: §7.2's
  closing paragraph and a §19 traceability row both said stdin projection
  delivery was "proven live," but only the CLI-schema-shape rejection
  (N20-F03) was actually proven live during the correction; stdin delivery
  itself was this correction's *design resolution* to N20-F04, not yet
  independently proven live in combination with the inline schema and
  `stream-json` output. Codex traced this precisely to the cited N20 evidence
  log and the recovery plan's own "Validate before implementation" item 4,
  which explicitly defers that proof to this validation step, not the
  specification pass.
- **Round 2 fix:** rewrote §7.2's closing paragraph and the §17.2/§19 rows to
  separate what is proven live (CLI-schema shape; stream-json identity
  mechanism; observed MCP listing) from what is this correction's reasoned
  design resolution pending its own live D03 proof (stdin delivery in
  combination with the schema/output-format flags), and added an explicit
  §20.2 prerequisite naming exactly that combined live proof. Also reverted
  an unrelated, out-of-scope embellishment (a resolved/open status
  inconsistency for `USER_DECISION_REQUIRED-01` that Codex flagged as an
  observation, not a finding) to restore v2's original, already-correct
  "named precisely, resolved via the approval record rather than in spec
  prose" pattern.
- **Round 2 verdict:** `PASS`. Zero findings. Observations: historical
  hashes match; zero case-insensitive `gemini`/`google` substring matches
  confirmed; the four transport-mechanics requirements are all present and
  internally consistent.
- **Honesty audit:** prior-rounds-consistent across both rounds.
- **`verify` output:**
  `{"state": "QA_PASSED", "reason": "CONVERGED", "chain_valid": true, "rounds_claimed": 2, "rounds_witnessed_by_codex": 2, "problems": []}`.
  Verified artifact hash `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`
  matches this table and the bytes Codex's round-02 review bound to.

## Incident during this task (fully remediated)

The first attempt to open this QA session used the artifact's *original*
directory (`plans/26_langgraph_curriculum_factory/spec/`), which already held
the v2 correction's completed `QA/` session. `qa_gate.py`'s QA directory is
always `<artifact_dir>/QA` (no override exists); starting a new session there
auto-archived the v2 session to `deprecated/QA-<timestamp>/` and began
overwriting it before this task's own 2-minute command timeout killed the
process mid-run, leaving `spec/QA/` partially rewritten mid-session. This was
caught immediately: `git status` showed `spec/QA/` as modified against the
last commit; `git checkout -- plans/26_langgraph_curriculum_factory/spec/QA/`
restored it byte-for-byte (confirmed identical to the tool's own archived
copy via `diff -rq`); the redundant archived copy was then deleted as stray
debris. The v3 specification was moved into its own `spec/v3/` subdirectory
so its `QA/` can never again collide with v2's. `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md`
sha256 was reconfirmed unchanged (`99052a181052bbbaf8077a152af22db6f248d552f38dd73302a3c34abc11b758`)
before this correction proceeded further.

## Exact changed files (this task)

New files only; nothing existing outside the incident above (fully reverted)
was edited, moved, or deleted:

- `plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md` (the corrected specification, passing version)
- `plans/26_langgraph_curriculum_factory/spec/v3/deprecated/langgraph_curriculum_factory.spec.v3.md` (round-1 attempt, tool-archived)
- `plans/26_langgraph_curriculum_factory/spec/v3/spec_v3_correction_criteria.v1.md` (QA criteria fed to the gate)
- `plans/26_langgraph_curriculum_factory/spec/v3/QA/` (gate-owned)
- `plans/26_langgraph_curriculum_factory/spec/v3/spec_correction.result.v2.md` (this file)

## Remaining observations

- The combined live proof of stdin projection delivery + inline CLI-schema
  projection + `stream-json` output for a Claude job is reported separately
  under this recovery task's "Validate before implementation" step 4
  evidence, not folded into this specification-correction result.
- `USER_DECISION_REQUIRED-01` remains resolved exactly as it was for v2, via
  the user's approval record (`contracts/spec_approval.v1.yaml`), not by
  editing spec prose — v3 makes no change to that pattern.

**No Run 27 v2-package implementation work was started by this task.**
