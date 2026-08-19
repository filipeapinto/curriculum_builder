# Final deterministic verification report

Plan: `codex_calls_claude_qa_gate.plan.v1.html`  
Run: `RUN-CAL-20260819-01`  
Verification status: **PASS WITH DISCLOSED LIMITATIONS**  
Human acceptance: **PENDING**

| Check | Result | Evidence |
|---|---|---|
| Approved immutable plan | PASS | plan SHA-256 `28878edec101a917a2b98a5e14d05e019387c9ff20bd2ff27bccc87e8eacee82` |
| Calibration and full-protocol authority | PASS | `approval.md`, `full-protocol-approval.md` |
| Required artifact presence/nonempty | PASS | calibration, evidence, matrix, protocol, corpus, benchmark, synthesis, challenge, verification artifacts |
| Source register | PASS | 24 candidates, 24 unique IDs; 22 retained, 2 excluded with reasons |
| Frozen corpus | PASS | 30 unique cases; SHA-256 `b1ed0ef3db843d6f01f4f5f7d61feeb8d1c0ebd2f17bcbd2bd00594943c70138` |
| Benchmark receipts | PASS | 180 receipts and 180 unique condition/case/repetition keys |
| Condition counts | PASS | 60 Claude, 60 Sol, 60 Terra |
| Budget reconciliation | PASS | ≈2.28M input-like / 73.8k output benchmark tokens; $1.08083 client-estimated Claude; ceilings not exceeded |
| Fail-closed behavior | PASS | schema preflight failures, structured-output exhaustion, timeout, unavailable reviewer, and digest mismatch did not pass |
| Finding identifiers | PASS | `FND-001`–`FND-006` present |
| Independent challenge | PASS | separate GPT-5.5 xhigh review returned 12 challenges |
| Challenge dispositions | PASS | 12/12 explicitly accepted/corrected or rejected with evidence |
| Corrected decision | PASS | operational adoption deferred; research-only advisory experiments permitted |
| HTML structure/accessibility baseline | PASS | HTML parser accepted; language, title, headings, table headers, textual prose present |
| Visual rendering | PASS after correction | Quick Look rendering inspected at 1600 px; dark-mode inline-code contrast corrected |
| External links | PASS at collection / mutable | 22 retained candidates were reachable at collection; one recorded 404 exclusion; external content not archived |
| Human acceptance | PENDING | verifier does not self-approve |

## Integrity digests

- Final SOTA report: `sota-report.html` SHA-256 `9688d6ef1e10642324957e55d6184bcffeb5776298a27342c60eff6d804e3a53`.
- Claude receipts: `8718ca37422909e8b389ec6fba5f8343d0a1c5edc9f354f83a749ca27ccf10ce`.
- Sol receipts: `d2d7909d02ae66cb542d2bc2cd2520966531a73aea19315ea9927591ae1242d9`.
- Terra receipts: `b22673261cfd4b6384b98e592cd7a0ce87ab810c5aa77c945b620b23deb53903`.
- Verdict schema: `9873e88b7b9aeefa09d9f28b60910fa1035b2ad67eb04be08339d9883d5dd137`.

## Disclosed limitations

The source set is small and external pages were not archived. The synthetic corpus uses templated triplicates and lacks dual-human adjudication, production artifacts, confidence intervals, and equivalent provider workloads. Schema validity did not guarantee semantic consistency. Claude exposed internal structured-output `tool_use` and auxiliary-model activity on one failed run. Shared-host integrity is weak, and cost evidence is not billing-grade. These limitations are carried into the corrected **defer** decision and therefore do not silently waive an adoption gate.
