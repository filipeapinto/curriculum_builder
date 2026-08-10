# `arduino_kit_run_v2` audit

Status: the run is not releasable. Four unit-level `acceptance.json` files say `ACCEPTED`, but the shipped lessons are unusable as learner documents and several required safety, evidence, visual, and review controls did not execute.

The issues below were reproduced from `outputs/arduino_kit_run_v2/`, the frozen run inputs, the cached source pages, the rasterized shipped PDFs, and the runtime that produced them.

| Priority | Issue | Why it matters |
|---|---|---|
| P0 | [001 - Renderer emits raw JSON instead of lessons](001-renderer-emits-raw-json.md) | Every learner-facing unit is unreadable and required teaching material is omitted. |
| P0 | [002 - Acceptance bypasses mandatory quality gates](002-acceptance-bypasses-quality-gates.md) | Grossly defective PDFs are marked `ACCEPTED`. |
| P0 | [003 - Visual pipeline produces irrelevant and false diagrams](003-visual-pipeline-breaks-the-curriculum-contract.md) | Visuals do not teach or verify the claimed facts; L04 has no multimeter image. |
| P0 | [004 - L04 contains unsupported meter guidance and omits the core safety rule](004-l04-multimeter-evidence-and-safety.md) | Device-specific electrical guidance is not adequately supported and the required current-mode prohibition is not taught directly. |
| P1 | [005 - Predict-observe-explain activities produce no observation](005-activities-produce-no-evidence.md) | Learners trace labels rather than test the concepts the lessons claim to teach. |
| P1 | [006 - Source receipts prove byte identity, not claim support](006-source-receipts-do-not-prove-claims.md) | Invented or over-specific claims can pass because only file hashes are checked. |
| P1 | [007 - The run has no honest run-level completion state](007-run-level-state-is-incomplete.md) | A 35-unit run contains four units and no explicit partial/interrupted terminal record. |

Recommended order: fix 001 and 003, make 002 fail closed, correct 004, then address 005 and 006 before re-running. Issue 007 should be fixed before treating any future output root as a resumable or complete execution.

The earlier narrative audit remains at `outputs/arduino_kit_run_v2/QA/arduino_kit_run_v2.qa_report.v1.md`; these files turn that assessment and the additional visual/technical findings into implementation-ready work items.
