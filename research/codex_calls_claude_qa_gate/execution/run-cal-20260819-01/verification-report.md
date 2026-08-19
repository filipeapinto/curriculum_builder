# Deterministic verification report

Run: `RUN-CAL-20260819-01`  
Verification status: **PASS for calibration package completeness**  
Research acceptance status: **NOT REQUESTED / SECOND HUMAN GATE OPEN**

## Checks

| Check | Result |
|---|---|
| Approved plan resolved and unchanged | PASS — SHA-256 `28878edec101a917a2b98a5e14d05e019387c9ff20bd2ff27bccc87e8eacee82` |
| Explicit human approval captured separately | PASS — `APR-CAL-20260819-01` |
| Required calibration outputs present | PASS |
| Stable source IDs | PASS — 24 rows, 24 unique IDs, 0 duplicates |
| Candidate ceiling | PASS — exactly 24, no overrun |
| Exclusions visible | PASS — `SRC-018` false positive; `SRC-022` HTTP 404 |
| Required route/authority limitations stated | PASS |
| Claude/model calls | PASS — 0 |
| Paid spend/credential inspection | PASS — $0 / none |
| Plan immutability | PASS — plan digest matches pre-execution observation |
| Second approval enforced | PASS — protocol and report explicitly prohibit live invocation |

## Artifact digests

| Artifact | SHA-256 |
|---|---|
| `approval.md` | `3defc18e7a54ab7ef2ff219151850a30a27830def467075d2cf953debd23b1db` |
| `calibration-report.md` | `fd1c1fe6244635bf49840fc33b93dcd3f30f1df58a340fe5d82168df044044c7` |
| `records/budget-ledger.md` | `09e2706feaf9eb73bca8f33248b19109b2ea3a476d70da7e386726bb9fc3fb53` |
| `records/capability-inventory.md` | `f749805f47a72cd2915b4c0ba5b2d93f7e9d63d1d1eb3a8d23a9f6bcaa35c172` |
| `records/execution-log.md` | `c49dcb57dfb4cb71213d968362be709275eea3d027c1d1b3eccfde68dc8617c6` |
| `records/query-log.md` | `2815ab8e573e9343c8a221427997a888dffe6be9cde3b981de2e53e00c49d0e4` |
| `records/source-register.csv` | `e7de244a3f7e0e0ba0ed734d91391e94c7b62e9b6446a7dc451652ff7d14c1f3` |
| `records/threat-vocabulary.md` | `1505c4e69c147abf915190d090c5d6089dc220637d3b8bff61f4f41c3663afca` |
| `protocol/calibration-benchmark-protocol.v1.md` | `95ca33c94dd752c3a9c7dd91e776fe76670e386b3b513612642dfec651854d57` |

This verification establishes package integrity and calibration completeness only. It does not validate a Claude route, benchmark result, recommendation, or final research acceptance.
