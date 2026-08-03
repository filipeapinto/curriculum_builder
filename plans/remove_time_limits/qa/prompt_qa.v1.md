# Prompt QA — Remove Governing Curriculum-Generation Time Limits v1

## Verdict and finding counts

**PASS** — 0 Critical, 0 High, 0 Medium, 0 Low.

The execution prompt is complete, internally consistent, repository-backed, and faithful to the approved plan and all six plan-QA reports. It is safe to delegate: no Critical or High defect blocks execution.

## Audit basis

Reviewed:

- `plans/remove_time_limits/prompts/remove_time_limits.prompt.v1.md` in full;
- the approved `plans/remove_time_limits/remove_time_limits.plan.v1.md` in full;
- all contract and tests QA reports, v1 through v3, under `plans/remove_time_limits/qa/`;
- current policy, schema, runtime parser/controller/checkpoint code, active simplification prompt, phase-4 agreement gate, `FR-P0-CLEAN`, gate runner, registry, status output, and runtime-test inventory.

Current repository evidence confirms the prompt's stated dirty-gate convention: `FR-P0-CLEAN` executes plain `git status --porcelain`, returns the full stdout to the runner while truncating human-readable detail after 20 entries, and the runner stores `sha256(stdout.encode("utf-8")).hexdigest()[:16]` as `stdout_digest`.

## Required-contract audit

| Requirement | Result | Prompt evidence |
|---|---|---|
| GOAL / TESTS / LOOP execution structure | **Satisfied** | The three top-level sections are explicit and the loop ties orientation, baseline stopping, inventory, edits, tests, scoped repair, reporting, and logging to the stated acceptance rules. |
| Exact implementation scope | **Satisfied** | GOAL names exactly five existing edit targets and exactly two new test files; TESTS G requires the task delta to be exactly those seven paths. Result and append-only log artifacts are explicitly classified as evidence rather than implementation-scope expansion. |
| Mandatory result and log artifacts | **Satisfied** | The prompt requires `remove_time_limits.result.v1.md` after final phase/status binding and one append-only `plans.log.md` execution entry, including verdict, evidence, scope, tests, dirty-gate disposition, and preservation state. |
| Preserve staged, unstaged, and untracked work | **Satisfied** | It captures human and NUL-delimited status, cached and working-tree diffs, copies/hashes, and new-file absence before edits; compares final files to working-tree baselines; and stops on collisions. |
| Prohibited worktree/index operations | **Satisfied** | It expressly forbids staging, stashing, committing, reverting, resetting, restoring, checking out, cleaning, deleting, or hiding user work and enumerates `git add`, `stash`, `commit`, `revert`, `reset`, `restore`, `checkout`, and `clean`. Repository edits must use `apply_patch`. |
| Native baseline and post-edit tests | **Satisfied** | It runs both direct phase-4 checks, phases 4 and 5, runtime unittest discovery, and meta-prompt validation before edits; reruns all required checks afterward; archives stdout, stderr, return codes, and exact emitted phase JSON. |
| Exact phase JSON failure/count checks | **Satisfied** | Exit 0 requires zero FAIL/BLOCKED. Exit 1 is limited to counts FAIL=1 and BLOCKED=0, sole `FR-P0-CLEAN` failure, every other activated gate PASS, no baseline regression, unambiguous emitted JSON, and `EXPECTED_DIRTY_BASELINE` labeling. All other outcomes block acceptance. |
| Digest binding to separately captured full plain status | **Satisfied** | It requires immediate byte-for-byte capture of plain porcelain, discovery of the current gate stdout source and runner algorithm, recomputation using the repository-confirmed 16-character SHA-256 convention, and equality to the exact JSON's `FR-P0-CLEAN.stdout_digest`. It correctly rejects use of truncated detail. |
| Fresh NUL-delimited exact path-set union | **Satisfied** | It independently captures fresh porcelain v1 with `-z --untracked-files=all`, parses complete NUL records including rename/copy records, normalizes the full path set, and requires exact set equality with the pre-edit dirty set union the seven authorized implementation paths. |
| Digest-discovery fallback | **Satisfied** | If the algorithm or stdout source cannot be discovered, the prompt prohibits claiming digest equivalence and limits JSON evidence to identity/counts while retaining full plain-status and exact NUL path-set proof. |
| Preservation boundaries | **Satisfied** | The prompt explicitly retains generic controller/check/meta-prompt contracts, elapsed telemetry, the 45-second request timeout, 300-second subprocess timeout, learner guidance, prompt v1-v5 history, and legacy runtime history; exact searches and byte/hash comparisons enforce the sensitive boundaries. |
| Stop conditions | **Satisfied** | It stops before editing on a non-clean baseline failure, stops on collisions or pre-existing new-test user work, and stops rather than adding an eighth implementation path, changing the index, weakening gates, hiding dirt, accepting stale/ambiguous results, or overstating evidence. |
| Result artifact completeness | **Satisfied** | The required result contents cover verdict, evidence directory, exact delta, command/result archives, phase counts and gate comparisons, digest/path-set evidence, parser and threshold behavior, simulation, telemetry, retention hashes, residual-hit classification, baseline/index audit, prohibited-operation confirmation, and unresolved issues. |

## Plan-QA remediation trace

The prompt carries forward every material finding from the earlier QA rounds:

- both active v6 instructions and both distinct 36,000-second contracts are handled;
- repository-native gate commands replace non-executing pytest probes;
- semantic renamed-duration rejection, legacy CLI rejection, retained defaults, deterministic former-threshold crossing, and numeric telemetry have biting tests;
- the dirty-suite exit-1 exception is narrow, parsed, and never relabeled PASS;
- every retained timeout/guidance/telemetry assertion is file-appropriate;
- pre-edit execution baselines support gate-by-gate regression comparison;
- the deliberate reject fixture has its own residual-search classification; and
- both final-QA Medium recommendations are fully resolved by full-stdout digest binding plus independent complete NUL-delimited set equality.

## Findings

No findings.

## Delegation decision

Because the verdict is **PASS** with exactly 0 Critical and 0 High findings, prompt QA authorizes and requires spawning the `execution` child to execute the prompt completely under its seven-file implementation allowlist and evidence-artifact rules.
