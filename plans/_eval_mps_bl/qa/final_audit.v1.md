# Meta-Prompt Activation — Final Audit v1

Standing audit of the corrected plan, the focused QA, the execution test plan, the
implementation prompt, and the shared log.

## Verdict

**PASS — 0 Critical, 0 High remaining.** All four High findings from
`qa/plan_qa.v1.md` are remediated in the plan text, carried into the execution test plan as
observable tests, and carried into the implementation prompt as instructions and named loop
cases. No participant is unlogged.

## Remediation trace

| Finding | Remediated in plan | Test that would catch a regression | In the prompt |
| ------- | ------------------ | ---------------------------------- | ------------- |
| 1 — import works only by cwd accident | §4 item 1: `sys.path.insert(0, str(REPO))` | MP-T04 (invoke by absolute path from outside the repo) | GOAL item 1, LOOP case 2 |
| 2 — owner pattern forbids the planned retention | §4 item 5: pattern anchored to top-level `meta_prompt/`, with the contract-v2 retention named | MP-T05 row 7 requires **PASS** on a `meta_prompt/deprecated/` owner row | GOAL item 5, LOOP case 3 |
| 3 — `simulate()` unprotected | §1: call added at the top of `simulate()`, above `prepare_output` | MP-T01 step 4 (defect is real), MP-T02 row 4 (no output root left behind), MP-T05 row 4 | GOAL, TEST 3, LOOP case 1 |
| 4 — "source inspection" is not a mechanism | §4 item 4: `inspect.getsource` of three function objects, limit stated in the docstring | MP-T05 rows 3-5 name the function; MP-T02 rows 3-5 cover the behavioural half | GOAL item 4, TEST 6 |

## Verified independently

- **The premise.** `python3 tests/check_meta_prompt.py` reports `EXECUTABLE (6/6)` today,
  and `CurriculumRuntime().prompt` equals `meta_prompt_source.PROMPT`. The change is a
  fence around a currently-correct state, not a repair, and the plan says so in §Status.
  MP-T01 makes the premise executable rather than asserted, which is the right shape for a
  plan whose subject is currently healthy.
- **The hole is where the plan says.** `runtime/controller.py:29` is the only one of the
  four path statements with no checker above it: (1)⇄(2) are bound by
  `check_meta_prompt.creator_derivable`'s anchor requirement, and (3) is required to resolve
  by `FR-P4-CHECK-MAPPING`.
- **The late-failure claim.** `runtime/session_bridge.py:91` copies `runtime.prompt` during
  input freeze, after the logger gate, manifest validation and verifier fixtures — so the
  current failure mode is mid-run inside a created evidence root, exactly as §"What is
  already checked" states.
- **Scope discipline.** No gate is added, `tests/gates/registry.py` and the plan catalogues
  are untouched, and the decision not to declare `PRECONDITION-PROMPT-RESOLVE` is stated
  with its reason rather than left silent. Eleven undeclared runtime precondition ids
  already exist; the plan does not pretend this is tidy.

## Residual risks, accepted and named

1. **Item 4 proves a call is written, not that it runs.** `inspect.getsource` cannot see
   reachability. The behavioural tests in MP-T02 cover the executing half for the three call
   sites that exist today; a fourth call site added later would be uncovered until someone
   adds it to both lists. The plan states the limit in the docstring rather than implying
   coverage it does not have.
2. **The activation check imports the runtime.** That is a new dependency direction —
   a contract checker now depends on runtime code. It is contained by the catch-and-report
   rule and by MP-T05's unimportable-controller row, but it is a real coupling and should be
   revisited if `check_meta_prompt.py` is ever folded into the gate registry.
3. **The undeclared check id remains undeclared.** Generalising the registry so a check like
   this can be declared without forcing a finished plan's catalogue to change is named as
   separate work in §3 and is not attempted here.

None of the three blocks implementation.

## Workflow hygiene

- Plan, QA, execution test plan, implementation prompt and this audit are each a distinct
  artifact; the QA was written against the plan as first authored and the plan was revised
  afterwards, with both states recorded in `plans.log.md`.
- The prompt's TEST section covers MP-T00 through MP-T07 with no test omitted or reordered,
  and its LOOP names the four failure modes the test plan can actually produce.
- The plan, the test plan and the prompt agree on the same four changed files and the same
  forbidden set.
