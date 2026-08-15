# Run 27 N90 requirements final audit

Audit time: 2026-08-15T10:53:26Z  
Run: `run27-execution-package-v2-graph-v9`  
Graph: `implementation.graph.v9.yaml` at `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`

## Exactly one terminal recommendation

`REMEDIATION_VERIFIED_NOT_ACTIVATED`

`ACTIVATED` is falsified because N70 and N80 are `NOT_AVAILABLE`, not `PASSED`. `BLOCKED` is not warranted because every implementation, integrity, evidence, convergence, and audit gate is current and valid; the only open condition is the graph-authorized unavailability of the approved Claude subscription driver for live product execution.

## Three separate conclusions

1. **Specification authority — PASSED.** The current user-approved corrected specification is `plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md` at SHA-256 `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`. N00 revalidated approval schema v6 and contract v6 before any implementation admission. Requirements lineage then covered current approval, approved specification, retained Plans 20–22/product requirements, code, tests, and product evidence with 8/8 claims and no uncovered layer.
2. **Implementation conformance — PASSED.** N10–N60 are current `PASSED` admissions. All schema/result, predecessor, write-set, provider/credential, topology, ownership, deterministic-evidence, and regression gates pass. Independent implementation QA is witnessed and its hash chain reverified below.
3. **Product activation — NOT AVAILABLE.** N70 and N80 are current `NOT_AVAILABLE`. Three N70/N80 content-free production preflights observed Codex ready and the approved Claude `claude-sonnet-5` subscription probe exiting 1. Every probe had an empty authorized input projection and closed observed Claude tools/MCP surface. Neither `outputs/run27/live_unit` nor `outputs/run27/live_workbook` exists; the two roots contain zero product files. No `UNIT_ACCEPTED`, `COMPLETE`, PDF, page, review, or release claim is made.

## Authority and historical-evidence disposition

- Normative authority proceeds from the current user request/approval to corrected specification v4, retained Plans 20–22 and product requirements, then current V9 implementation/results.
- Superseded Plan 26 v1 provider assertions and preflight semantics remain labeled superseded. They are regression context only.
- Graphs v1–v8, their results, QA, failed N70 attempts, and archived live roots remain historical evidence in collision-free namespaces. Graph v9 did not overwrite them.
- Plan 26 v1 specification/history was not edited for V9 admission. The active Plan 26 v3 N13 transport receipt was intentionally refreshed during the authorized repair cascade, with prior receipt versions preserved under receipt history; it is not used here as provider correctness or activation proof.
- Historical Markdown status, old receipts, old product attempts, and test claims confer no authority. Current schema-bound V9 results and controller receipts are the only scheduler authority.

## Current result and receipt chain

| Node | Outcome | Result SHA-256 | Scheduler receipt SHA-256 | Current |
|---|---|---|---|---|
| N00 | PASSED | `d64fa8aad0ba2ab485a140826f0efb69e506cdd7171fc84a7ab0885f979bb6c3` | `9bdfb2847fa25f327d9451a7ec4a4cae04ea1f9f2ef7d585fe2a3bdb5351e5b0` | yes |
| N10 | PASSED | `b093502759fe6c79665158343410e0283c05ab19dd4e83879c628f140355d25e` | `0c86bcafae0bea3f5c7a8cde16564dcf514cc334255ad0eb461162db15ec25f5` | yes |
| N20 | PASSED | `fd0928c444ae4667cfafb6e960c1623df11b5725d30b1ae79c25ec5a9320f300` | `b91f490a78c55a2989e1caf9aa9819f9f7c3cd49a1d8f6ed25a3df6096eaed98` | yes |
| N30 | PASSED | `5c39030a97c4e8e2f0986a6eb7514f7d1aab739742f6560672d1d8bc3532e310` | `c32ea3efffe9f390e541b75deb720fc6b0b59b2897880a7dc49d172c96861e10` | yes |
| N40 | PASSED | `4babb3aaf8b2ebe65b05868826374f8a689936f27498cee2f7678eb717dd5981` | `155ee64e184c1c8862c136044e6ea8596eb9cdc01e77bd680e9cfcc1a764b2da` | yes |
| N50 | PASSED | `f1905dbd453862d876ab22d20dad036c823de723470caece992b92cb5fbb4ce1` | `4eb7d7efff9d6950de75cb176fabb277d447f038e0ebfa80840972042cfd0600` | yes |
| N60 | PASSED | `76f1aad362e4465d678d8a7109384827e2176a3a5a7a64d213afbbdef51ecfba` | `8172513e7ce80fef6ac5c01a2e9e258efe9aaa13415f638d5decf12c2ce3ab6d` | yes |
| N70 | NOT_AVAILABLE | `cebc693ee9a1f5f911132cc787b39adbdb36255e0e6f60d5fefa4c24f7fcb055` | `63f547d377fec1281eb7edfba446070165fc9587578fbe6af067c2a5d0f0eaea` | yes |
| N80 | NOT_AVAILABLE | `d27bfca2c6144203b50ca6f66d219b3689b98dc953e7ce5b7d3c6ccddf02627f` | `7ddc3bf2004cc56df9d9660d1652033f3a13b6a407f4a2aa274c6ef19885f31f` | yes |

Every result passed the frozen JSON-schema validator. Controller `validate` recomputed each result hash, prompt/spec binding, predecessor result digest, changed-file digest, write-set delta, and receipt currency with zero problems. The audit log preserves the three failed early attempts (N00 command disposition, N10 predecessor-digest mistake, N20 outer-sandbox environment) and their reasons; re-admission did not erase them. No current receipt reports a stale reason.

## Implementation conformance

- **Eight jobs:** M01–M04, M06, and M08 use installed Claude/Anthropic subscription CLI routes; M05 and M07 use installed Codex/OpenAI subscription CLI routes. Generation/repair and independent judgment stay cross-family. Missing or identity-mismatched drivers fail closed without reassignment.
- **No billed/provider escape:** API-key variables are denial guards only. No provider SDK, direct model HTTP endpoint, custom endpoint, hidden fallback, or retired-provider production route exists. The complete-tree scanner inspected 67 files with zero violations.
- **Least privilege:** exact-host source policy validates every redirect, DNS/IP result, TLS/status/content type, resolved host, and byte digest. Model inputs are staged and hash/schema verified. Claude receives the bounded canonical projection on stdin with observed tool/MCP closure. Codex review receives frozen actual artifacts in its tool-closed workspace.
- **Verifier trust closure:** D02 freezes schema/config/calibration/verifier/dependencies/fixtures. D08 uses an isolated `-I -S` child, no parent site packages or network, authenticates runtime module hashes, executes every reject/accept fixture and exact candidate, then binds its receipt to all inputs. M02 cannot self-declare acceptance.
- **Topology/ownership:** production compile reachability covers the unit, repair, workbook, and legal terminal paths. Initial/repaired candidates are immutable physical ArtifactStore versions and heads advance only after owning-validator admission. All 75 ownership claims pass.
- **Evidence:** equivalent inputs yield one canonical output; stable paths show no drift. Evidence determinism is 2/2 claims, requirements lineage 8/8, and append-only failure/invalidation history remains visible.
- **Regression denominator:** focused adversarial 5 passed; full runtime repeatedly passed `1370`, with `419` subtests and exactly two frozen unrelated skips (unavailable installed Gemini resolver in the unrelated legacy pipeline; absent pinned pip-tools lock generator); Run 27 package passed `83` twice; whole-tree scan passed twice over 67 files. The frozen source/test aggregate remained `336314adfe2ddb7921950da52d1fd93c3b5c2d374e190b9e008ac0afb3711c2d` before/after direct N60 runs. Controller independently replayed N60 before admission.

## PM-01–PM-24 and CA-01–CA-12 closure

| Item(s) | Disposition | Evidence/owner |
|---|---|---|
| PM-01 | resolved | corrected Claude-author/Codex-judge subscription architecture; N20 eight-job conformance |
| PM-02 | resolved | N00 approval gate plus N50 authority-first lineage |
| PM-03 | resolved | false Plan 25 provider attribution superseded in spec; no current route derives authority from it |
| PM-04 | resolved | cross-family constraint uses the user-approved named Claude/Codex mapping |
| PM-05 | historical/consolidated | postmortem v2 folds exact retired-model hardcoding into PM-01; retained in history |
| PM-06 | resolved | D03 separates executable identity from subscription usability |
| PM-07 | resolved | content-free feasibility runs before any curriculum transmission |
| PM-08 | resolved | one failed mandatory field makes ready false/nonzero, demonstrated live at N70/N80 |
| PM-09 | historical/consolidated | retired-provider authorization folded into PM-01; whole-tree production scan is zero |
| PM-10 | historical/consolidated | role inversion folded into PM-01; final six/two job split is correct |
| PM-11 | resolved | full unit/repair/acceptance production topology reachable at N40 |
| PM-12 | resolved | workbook topology reachable in integration; audit does not claim live workbook registration as product proof |
| PM-13 | resolved | topology expectations derive from approved spec and reject stale edges |
| PM-14 | resolved | CLI/test ownership and migration retirement are atomic in exact node write sets |
| PM-15 | resolved | transitive descendant invalidation and predecessor result-digest binding are controller-enforced |
| PM-16 | resolved | N50 deterministic/run-scoped evidence plus repeat comparison |
| PM-17 | resolved | frozen schema-bound JSON outcomes replace Markdown parsing |
| PM-18 | resolved | 75/75 machine-readable integration ownership claims |
| PM-19 | resolved | deterministic atomic controller, merge journal/recovery, preserved failure history, 81 harness tests twice at N10 |
| PM-20 | resolved | current approval and requirements lineage precede spec-to-code conformance |
| PM-21 | historical/consolidated | postmortem v2 merges passing-tests-as-readiness overclaim into PM-22; live proof remains distinct |
| PM-22 | resolved for implementation; live blocker open | no credential/provider recommendation; truthful Claude unavailability produces NOT_AVAILABLE |
| PM-23 | resolved | family diversity is a bounded independent-judgment control, never sufficient product proof; no review claim exists without product |
| PM-24 | resolved | normative, superseded, historical, and implementation-observation evidence are explicitly separated |
| CA-01–CA-05 | resolved | corrected spec, independent review, user approval, SPECIFICATION_DEFECT disposition, then scoped remediation |
| CA-06–CA-07 | resolved | truthful preflight and provider/transport/authorization configuration at N20/N30 |
| CA-08 | resolved | descendant invalidation/receipt regeneration at N10 |
| CA-09 | resolved | deterministic run-scoped evidence at N50 |
| CA-10 | resolved | schema-bound controller results at N10 |
| CA-11 | resolved | production compile reachability and ownership gates at N40 |
| CA-12 | executed; activation unavailable | authorized live proof was attempted only after N60; approved Claude driver was unavailable, no bytes transmitted, no activation claimed |

## Activation falsification

- **Unauthorized-provider/API-key hypothesis:** falsified by 67-file scan, subscription-only routes, credential absence guards, authorization data classes, and no live transmission.
- **Same-family judge hypothesis:** falsified by six Anthropic author/repair routes versus two OpenAI review routes. No unexecuted judge is claimed as product evidence.
- **False-ready hypothesis:** falsified by three preflights returning `ready:false`, exit 3 on one failed mandatory Claude usability field while Codex remained ready.
- **Incomplete-denominator hypothesis:** falsified by complete runtime/package/scan counts, stable aggregate, and independent controller replay.
- **Stale-receipt hypothesis:** falsified by current status, per-node validation, predecessor result hashes, and zero currency reasons.
- **Topology-bypass hypothesis:** falsified by 213 production-compile integration tests and 75 ownership claims.
- **Evidence-drift hypothesis:** falsified by N50 repeat contracts and N60 unchanged source/test aggregate.
- **False-product hypothesis:** falsified directly: both live roots are absent and product file count is zero.

## Independent gate

The repository qa-gate skill reverified RC29, which binds the final implementation recovery bytes and committed regression/source-inspection criteria. Its only authoritative verification output is:

- state `QA_PASSED`, reason `CONVERGED`
- `chain_valid: true`, `problems: []`
- one round claimed and one round witnessed by Codex
- session `01a004d7-57fd-7080-853e-9e3a3f1afabc`
- chain `cfd2295d138e59724fa460a6e3c1d5a5d67c5bd747bd77f9f7615300e813843c`

RC28's apparent pass remains rejected as an integrity breach; it is not counted. RC29 review closure and the deterministic V9 execution/terminal audit are distinct: the former prevents implementation self-approval, while the latter proves the fresh scheduler/live outcomes.

## Final decision

Specification authority: **PASSED**.  
Implementation conformance: **PASSED**.  
Product activation: **NOT AVAILABLE**.  
Sole terminal recommendation: **REMEDIATION_VERIFIED_NOT_ACTIVATED**.
