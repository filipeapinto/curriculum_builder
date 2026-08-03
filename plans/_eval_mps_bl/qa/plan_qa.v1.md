# Meta-Prompt Activation Plan v1 — Focused QA

## Verdict

**CHANGES REQUIRED — 0 Critical, 4 High.** The defect is correctly identified and the
scope is appropriately narrow: `runtime/controller.py:29` is genuinely the only one of the
four statements of the active contract path that nothing checks. But as written, the new
check cannot be imported reliably, cannot fail for the retention case the repository has
already planned for, leaves the most frequently run execution path unprotected, and
specifies its own weakest assertion by prose rather than by mechanism.

Findings are against `plans/meta_prompt_activation/meta_prompt_activation.plan.v1.md` as
first authored. Baseline confirmed before review: `python3 tests/check_meta_prompt.py`
reports `EXECUTABLE (6/6)`, and `CurriculumRuntime().prompt` currently equals
`meta_prompt_source.PROMPT`, so this change is a fence, not a repair.

## Findings

### 1. High — the activation check's import works only by cwd accident

**Evidence.** `tests/check_meta_prompt.py:77` does
`sys.path.insert(0, str(Path(__file__).resolve().parent))` — the `tests/` directory, not
the repository root. `runtime/controller.py` uses package-relative imports (`from .checkpoint
import ...`), so `import runtime.controller` resolves only if `REPO` is on `sys.path`. Today
that happens because the two invocations in the repository —
`runtime/finalize_evidence.py:37` (`cwd=engine`) and a manual run from the repository root
— put `''` on the path. Plan §4 states the import requirement and says nothing about the
path.

**Impact.** The seventh check would pass or explode depending on the caller's working
directory. Run from anywhere else, the plan's own catch-and-report rule converts that into
`FAIL activation: cannot import the controller` — a checker that reports the *contract* as
not executable because of where it was invoked from. That is a false negative in the class
`policy/failures.v1.yaml` calls B3, introduced by the check meant to close one.

**Minimal required remediation.** Add `sys.path.insert(0, str(REPO))` beside the existing
insert, and state in the docstring that this part reads the runtime and therefore imports
it. Keep the catch-and-report rule for genuine import failures.

### 2. High — the owner-row assertion cannot pass in the retention case the repository has already planned

**Evidence.** §4 item 5 requires every `owner:` value in `policy/checks.v1.yaml` matching
`meta_prompt/*.prompt.v*.md` to equal `source.PROMPT_REL`. `plans/contract_v2/prompt/contract_v2.prompt.v1.md:104`
plans to `git mv` the superseded prompt to `meta_prompt/deprecated/` and retain it. Under
`fnmatch`, `*` crosses `/`, so `meta_prompt/deprecated/curriculum.prompt.v1.md` matches the
stated pattern.

**Impact.** On the day v2 is activated, any retained owner row pointing at the deprecated
v1 fails the activation check, and the only way to make the checker green is to delete the
retained history the contract-v2 plan requires. A check that forbids the migration it exists
to protect will be weakened or deleted at the moment it first fires, which is worse than not
adding it.

**Minimal required remediation.** Anchor the pattern to the top level of `meta_prompt/` —
match `owner` values of the form `meta_prompt/<name>.prompt.v<n>.md` with no further path
separator — and state that a prompt under `meta_prompt/deprecated/` is deliberately out of
scope because it is retained history, not an active contract.

### 3. High — `simulate()` is left unprotected, and it is the path this plan itself runs

**Evidence.** §1 adds `resolve_prompt()` to `static_preflight()` only.
`CurriculumRuntime.simulate` (controller.py:161-234) never touches `self.prompt`. Both
`--test-static` and `--test-simulated-all` are verification steps in this plan's own §5 and
are two of the six commands in `runtime/finalize_evidence.py:34-40`.

**Impact.** With the active contract deleted or renamed, `--test-simulated-all` still walks
every state, writes checkpoints, passes the final log audit and returns `ACCEPTED`. The run
summary would say `terminal_state: ACCEPTED` for an engine that has no contract at all. The
plan would then have added a precondition that the most frequently executed path skips.

**Minimal required remediation.** Call `resolve_prompt()` at the top of `simulate()`, before
`prepare_output`, so the failure precedes any evidence-root mutation exactly as it does in
`session_bridge.prepare`. Add one runtime test asserting the failure id from `simulate` as
well as from `static_preflight`.

### 4. High — "asserted by source inspection" is not a mechanism

**Evidence.** §4 item 4 requires proof that `resolve_prompt` is reachable from
`static_preflight` and `session_bridge.prepare`, and specifies only "source inspection of
those two functions". Every other check in this file states its mechanism precisely —
`creator_derivable` explains why an anchor is subtraction and not a guess; `banner_problems`
explains which three claims must agree.

**Impact.** An unspecified mechanism will be implemented as a regex over the file text,
which matches a mention inside a comment, a docstring, or an unreachable branch, and misses
a call reached through a rename. The check would then certify a call site that does not
exist, which is the same self-certification `banner_problems` was written to stop.

**Minimal required remediation.** Specify `inspect.getsource` of the two function objects
(not a scan of the file), require the literal call token in each, and state the limit
plainly in the docstring: this proves the call is *written*, not that it *executes*. Pair it
with the behavioural half in `tests/runtime/` — a temporary engine with no prompt, asserting
`PRECONDITION-PROMPT-RESOLVE` out of `static_preflight`, `simulate`, and
`session_bridge.prepare` — so the two together cover what neither covers alone.

## Confirmed sound

- Not declaring `PRECONDITION-PROMPT-RESOLVE` in `policy/checks.v1.yaml` (§3). Verified:
  `FR-P4-CHECK-MAPPING` would require `verified_by` naming a registered gate, and
  `FR-P0-REGISTRY` would then require that gate in a finished plan's §8 catalogue. Eleven
  runtime precondition ids are already undeclared; a twelfth stated openly is correct.
- Keeping `__init__` total (§1). Verified: `tests/runtime/test_controller.py` constructs
  `CurriculumRuntime` for cases that never read the prompt, and a raising constructor would
  also break the new check's own import.
- Extending `tests/check_meta_prompt.py` rather than adding a gate. Verified: it is already
  invoked by `runtime/finalize_evidence.py:37`, and its docstring lines 58-67 give the
  reason a gate would force `FR-P0-REGISTRY` to disagree with a finished plan.
