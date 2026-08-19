# Execution log — `RUN-CAL-20260819-01`

| Activity | Start (EDT) | Terminal | Status | Evidence |
|---|---:|---:|---|---|
| `ACT-START-GATE-01` validate plan, approval, assignments, controls | 2026-08-19 05:20 | 05:22 | PASS | plan v1, approval record, execution contract, installed role skills |
| `ACT-LOCAL-01` read-only capability inventory | 2026-08-19 05:22 | 05:25 | COMPLETE | `capability-inventory.md`, local help/version output observed in controller transcript |
| `ACT-TERMS-01` terminology and threat map | 2026-08-19 05:25 | 05:28 | COMPLETE | `threat-vocabulary.md` |
| `ACT-SEARCH-01` six-family pilot candidate search | 2026-08-19 05:23 | 05:27 | COMPLETE | `query-log.md`, `source-register.csv` |
| `ACT-DRYRUN-01` safe dry-run protocol design | 2026-08-19 05:27 | 05:31 | COMPLETE / AWAITING HUMAN GATE | `protocol/calibration-benchmark-protocol.v1.md` |
| `ACT-CAL-REPORT-01` calibration report and budget reconciliation | 2026-08-19 05:31 | 05:34 | COMPLETE | `calibration-report.md`, `budget-ledger.md` |
| `ACT-APPROVAL-02` full protocol/live synthetic approval | 2026-08-19 | 2026-08-19 | APPROVED | `full-protocol-approval.md` |
| `ACT-ROUTE-01` model/auth/price/permission resolution | 2026-08-19 | 2026-08-19 | COMPLETE | official docs, `feasibility-security-matrix.md` |
| `ACT-PREFLIGHT-01` corpus/controller build and deterministic tests | 2026-08-19 | 2026-08-19 | COMPLETE | protocol scripts, schema, corpus digest |
| `ACT-BENCH-01` 30 × 3 × 2 benchmark | 2026-08-19 | 2026-08-19 | COMPLETE | 180 JSONL receipts, `benchmark-summary.md` |
| `ACT-SYNTH-01` comparative synthesis | 2026-08-19 | 2026-08-19 | COMPLETE | `sota-report.html` |
| `ACT-CHALLENGE-01` independent GPT-5.5 xhigh challenge | 2026-08-19 | 2026-08-19 | COMPLETE | `challenge-register.md`; 12 dispositions |
| `ACT-VERIFY-01` deterministic package verification | 2026-08-19 | 2026-08-19 | COMPLETE | `final-verification-report.md` |

Calibration invoked no model. After explicit full-protocol approval, synthetic model calls were made under the recorded route. Authentication status was inspected without reading credential material. No production/customer data was used. The final synthesis was materially narrowed from pilot to defer after independent challenge.
