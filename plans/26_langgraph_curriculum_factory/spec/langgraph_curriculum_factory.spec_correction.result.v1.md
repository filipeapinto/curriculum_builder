# Plan 26 spec correction — result

status: `SPECIFICATION_CORRECTED_AND_INDEPENDENTLY_VERIFIED`

This status is reported here because the underlying gate `verify` operation
returned a witnessed, hash-chain-valid `QA_PASSED` (below). Claude did not
originate this verdict; Codex did, through the `qa-gate-codex-run` skill.

## Artifacts

| Artifact | Path | SHA-256 |
|---|---|---|
| Corrected spec (v2, passing version) | `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md` | `99052a181052bbbaf8077a152af22db6f248d552f38dd73302a3c34abc11b758` |
| Predecessor spec (v1, historical, immutable) | `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md` | `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6` (unchanged from N60/N90's recorded value; reconfirmed before and after this task) |
| QA criteria | `plans/26_langgraph_curriculum_factory/spec/spec_correction_criteria.v1.md` | new, criteria for SPEC-T00–T10 plus the GOAL falsification targets |

v1 was never edited, moved, deprecated, or deleted. No Plan 26 receipt,
patch, result, log, policy, schema, model-job configuration, runtime code,
test, or implementation graph file was changed by this task.

## Deterministic test results (SPEC-T00–SPEC-T10)

All run directly against the live repository before the Codex gate was
opened, per LOOP step 3–4.

| Test | Result | Evidence |
|---|---|---|
| SPEC-T00 — historical immutability | PASS | v1 sha256 unchanged (`44e63e6...`); `git status --porcelain=v1` shows only new files added by this task plus one pre-existing, unrelated untracked directory (`plans/27_langgraph_curriculum_factory_remediation/results/`) that predates this task and was never modified |
| SPEC-T01 — authority and supersession | PASS | v2 §2.0 (authority hierarchy, 7 ranked levels with citations) and the Supersession statement table at the top of v2, citing PM-01–PM-24 and Plans 11/20/21/25 for every retained or superseded decision |
| SPEC-T02 — Gemini elimination | PASS | Exhaustive case-insensitive grep of v2 for `gemini`/`google`/`GEMINI_API_KEY`/`GOOGLE_API_KEY`; all 47 occurrences manually classified as historical/defect narrative or explicit prohibition; none defines a production job, provider, credential, authorization, endpoint, prerequisite, fallback, or activation remedy |
| SPEC-T03 — subscription-only invariant | PASS | v2 §1.2, §3.1, §7.1, §7.4, §17.2, §21 |
| SPEC-T04 — cross-family role mapping | PASS | v2 §6.3 table: M01–M04/M06/M08 = Claude/Anthropic; M05/M07 = Codex/OpenAI; family-mismatch = system failure rule stated |
| SPEC-T05 — complete consistency | PASS | Systematic table/prose walk across §6.3, §7, §9, §13, §16, §19, §20, §21; spot-grep confirmed no orphaned `gpt-5.6-sol`/unconverted "Codex authors" phrasing outside the historical/supersession narrative |
| SPEC-T06 — preflight truthfulness | PASS | v2 §6.2 (D03), §7.1 (five explicit proof classes, ready:true impossible on identity-proof alone), §14, §17.2 new adversarial row naming the exact N60 exit-41/false-ready condition |
| SPEC-T07 — data-boundary correction | PASS | v2 §7.4: `google` authorization class removed, replaced by `anthropic`/`openai` classes |
| SPEC-T08 — LangGraph preservation | PASS | Scripted structural diff of §8 graph diagram, §8.2 edge table, §14 terminal table, and the D00–D98 node catalogue against v1: byte-identical except the one disclosed, named D03 capability-proof strengthening; no other reducer, checkpoint/resume, repair-bound, artifact-immutability, or denominator text changed |
| SPEC-T09 — honest lifecycle | PASS | v2 §2.0.3 (three claims never merged), §22 closing statement ("None of the rows above authorizes starting Run 27...") |
| SPEC-T10 — historical regressions | PASS | v2 §22 maps each postmortem finding (PM-01–PM-24 group; PM-11/12/15/16/17/19) to its v2 control or explicit, named deferral to a later implementation run |

Markdown table-structure lint (column-count consistency across all pipe
tables in v2): 0 issues.

## Independent Codex QA gate (SPEC-T11, SPEC-T12)

- **Transport:** `app-server` (default), via the `openai-codex` plugin
  (`plugin_version 1.0.4`), through `scripts/codex_bridge.mjs` /
  `runAppServerTurn`. First attempt failed closed with `QA_ERROR` /
  `NODE_NOT_INSTALLED` (Node.js was not on `PATH`); per LOOP step 7 the run
  stopped immediately rather than substituting `--transport exec` or
  self-review, and the user was asked to choose. The user installed Node.js
  and explicitly directed `start --force` on the same default app-server
  transport, which then completed normally.
- **Session:** `019ffb5f-9dcc-74b3-82b8-1899f29d490e` (session ID = thread
  ID). Rollout witness file:
  `~/.codex/sessions/2026/08/13/rollout-2026-08-13T09-46-15-019ffb5f-9dcc-74b3-82b8-1899f29d490e.jsonl`.
- **Rounds:** 1 of 5 max. Turn ID `019ffb5f-a4d7-7113-aa6a-23faf9667ed3`.
- **Threshold:** `major`. **Criteria:** SPEC-T00 through SPEC-T10, plus the
  seven GOAL falsification targets, as written in
  `spec_correction_criteria.v1.md`.
- **Grounding sources (12, all hashed and chained):** postmortem v2, spec
  v1, the active meta-prompt, Plans 11/20/21/22/25 (both files), N60, N90,
  and the `qa-gate-codex-run` SKILL.md itself — exactly the GOAL source list
  plus the v2 postmortem.
- **Codex's verdict (round 1):** `PASS`. Zero findings. Three non-blocking
  observations:
  1. v2 §11's "retained... without modification" framing is not literally
     exact, since §11.2 adds one disclosed PM-15 normative sentence; Codex
     confirmed this does not defeat SPEC-T08 (checkpoint/resume mechanics
     are unchanged) and is not a finding. Left as-is rather than reopening
     a new gate round over a cosmetic wording point after PASS+verify.
  2. The custom-endpoint/base-URL-override prohibition is expressed
     indirectly (isolated configuration, fixed authorization classes,
     egress restriction) rather than as one literal sentence; Codex judged
     the combined contract still satisfies SPEC-T03.
  3. The installed Claude CLI currently reports `loggedIn: false` in this
     environment; the specification does not claim otherwise — it requires
     preflight to fail until subscription-backed authentication is proven,
     which is exactly the state this observation confirms.
- **Honesty audit:** `prior_rounds_consistent: true` (round 1 has no prior
  rounds to recall).
- **`verify` output:**
  `{"state": "QA_PASSED", "reason": "CONVERGED", "chain_valid": true, "rounds_claimed": 1, "rounds_witnessed_by_codex": 1, "problems": []}`.
  The artifact hash `verify` checked
  (`99052a181052bbbaf8077a152af22db6f248d552f38dd73302a3c34abc11b758`) matches
  the hash recorded in this table and the hash Codex's round-01 metadata
  bound its review to — the reviewed artifact and the passing artifact are
  byte-identical.

## Exact changed files (this task)

New files only; nothing existing was edited, moved, or deleted:

- `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md` (the corrected specification)
- `plans/26_langgraph_curriculum_factory/spec/spec_correction_criteria.v1.md` (QA criteria fed to the gate)
- `plans/26_langgraph_curriculum_factory/spec/QA/` (gate-owned: `session.json`, `verdict.json`, `rounds/round-01.*`) — Claude did not write into this directory; it is entirely `qa_gate.py`-owned output
- `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec_correction.result.v1.md` (this file)

Pre-existing, unrelated dirty state observed and left untouched:

- `plans/27_langgraph_curriculum_factory_remediation/results/` — untracked
  directory already present at the start of this task (a Plan 27
  remediation-run attempt whose own `N00_SPEC_APPROVAL_GATE` evidence checks
  for exactly this v2 spec's absence/presence — consistent with this task
  being its prerequisite gate, not something this task should modify).

## Remaining observations

- `USER_DECISION_REQUIRED-01` (v2 §7.1, §20.2): the exact Claude model
  alias/name and effort level for each of the six Claude-owned jobs
  (M01–M04, M06, M08), and confirmation of the Codex model/effort for
  M05/M07, remain unresolved. No repository source settles this, so v2
  states the mechanism (`claude -p --output-format json --json-schema`,
  evidenced live against the installed `claude` CLI, version
  `2.1.231 (Claude Code)`) and the family/job assignment, but does not
  invent per-job model/effort pins. This must be resolved before
  implementation freezes `config/model_jobs.v1.yaml`.
- Live proof that the `claude -p --output-format json` envelope exposes a
  machine-readable executed-model identity field (the same discipline v1
  already required of Codex/Gemini) was not established by this
  specification-only task and remains an implementation-time D03
  prerequisite (v2 §20.2).
- The installed Claude CLI's current `loggedIn: false` state (Codex's
  observation 3 above) is exactly the kind of honest non-ready condition
  v2's corrected preflight is designed to report — not a defect in this
  task's output.

**No Run 27 or implementation work was started.**
