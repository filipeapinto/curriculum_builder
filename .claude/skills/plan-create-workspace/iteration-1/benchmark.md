# Skill Benchmark: plan-create

**Model**: <model-name>
**Date**: 2026-08-03T16:21:50Z
**Evals**: 0, 1, 2 (3 runs each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 75% ± 22% | 62% ± 0% | +0.12 |
| Time | 0.0s ± 0.0s | 0.0s ± 0.0s | +0.0s |
| Tokens | 0 ± 0 | 0 ± 0 | +0 |

## Notes

- Pass-rate parity (75% vs 62%) undersells the qualitative gap: every with-skill 'failure' on the two harder evals (meta-prompt-staleness, gate-flakiness) is honest by-design incompleteness -- the QA convergence rule correctly detected a plateau (findings stopped decreasing round-over-round) and withheld the test-plan/prompt/final-audit artifacts rather than build on an unclean plan. Every baseline 'failure' is a structural risk instead: no genuinely independent QA pass was evidenced (single narrative, no second plan version, no shown command execution), which is the exact failure mode the skill's fresh-subagent design exists to prevent.
- retry-tracker-defect is the cleanest comparison: the with-skill run reached a fully validated, independently-audited package (8/8, converging 3 High -> 2 -> 1 -> 0 across four independently-verified QA rounds, each of which actually patched a scratch copy and ran the real test suite/gates) while the baseline reached a superficially similar-looking package (5/8) whose QA and final audit were a single self-consistent narrative with no independent verification shown.
- gate-flakiness (the hardest, most investigative eval) is a useful warning about the pass-rate number itself: the with-skill run's three independently-verified QA rounds could not fully converge on this genuinely hard plan (7 -> 3 -> 3 Critical+High, correctly stopped at the plateau), while the baseline reached a self-declared clean PASS in a single unverified pass. The baseline's apparent 'success' here is less trustworthy, not more -- a single-pass, non-independent review that never got contradicted is not the same as a plan that was actually pressure-tested.
- Time and token metrics are 0/null throughout: this environment's background-agent notifications (idle_notification) do not surface total_tokens or duration_ms, so those columns could not be populated. plans.log.md timestamps (real UTC, written by scripts/append_log.py) offer a rough wall-clock proxy for with-skill runs only; baseline log timestamps are model-narrated, not measured, and were not used for timing.
- This iteration's most important finding was mid-run, not in the final numbers: all three initial with-skill runs hit SKILL.md's original hard 2-round QA cap and stopped despite findings strictly decreasing round over round (real convergence). Step 4 was rewritten to continue while the Critical+High count keeps strictly decreasing (5-round ceiling), and the three runs were resumed under the corrected rule before this benchmark was produced -- the numbers above already reflect the corrected skill, not the original draft.