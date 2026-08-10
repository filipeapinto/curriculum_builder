# Provider Correction Plan v1 — Focused QA

## Verdict

**CHANGES REQUIRED — 0 Critical, 4 High.** The removal strategy is appropriately narrow,
but v1 is not executable as written because the required plugin is disabled, its effort
interface conflicts with current routing policy, the plugin evidence contract is
underspecified, and deletion rules can destroy pre-existing staged work beyond the
requested reference removal.

`RETIRED` has the meaning defined by the reviewed plan: the lowercase ASCII sequence
`103, 101, 109, 105, 110, 105`. This report does not reproduce that sequence as text.

## Findings

### 1. High — the required plugin is installed but currently disabled

**Evidence.** `claude plugin list` reports `codex@openai-codex` version `1.0.4` at both
project and user scope with status `disabled`. V1 describes the plugin as installed and
does not test availability until verification step 5, after all implementation and
deletion work.

**Impact.** The plan can perform its destructive and architectural edits and only then
discover that its mandatory smoke call and acceptance criterion cannot run. Its stated
end state is therefore not currently attainable in the ordered workflow.

**Minimal required remediation.** Add one phase-0, read-only preflight before any edit:
record plugin version and enabled status and stop immediately if it is not enabled. Do not
add plugin enablement or external settings mutation to this plan; make enabled status an
explicit prerequisite for execution.

### 2. High — the plugin cannot carry the policy-required `max` effort value

**Evidence.** `policy/routing/routing_policy.v1.yaml:22` requires `max` for
`safety_critical`; `schemas/routing_decision.schema.v2.json:21` and
`policy/routing/model_registry.v1.yaml:20` permit that value. The installed plugin's
`skills/codex-cli-runtime/SKILL.md` accepts only `none`, `minimal`, `low`, `medium`,
`high`, and `xhigh` for `--effort`. The contract-v2 authoring prompt and v1 both forbid an
invented effort mapping while requiring decided and executed effort to agree.

**Impact.** A final or safety-critical OpenAI-family review selected at `max` cannot be
sent through the required plugin without rejection, silent defaulting, or a prohibited
mapping. Any of those outcomes breaks routing-record integrity and deterministic
acceptance.

**Minimal required remediation.** Make phase 0 fail closed on any routing decision whose
effort the installed plugin cannot express. Before implementation, choose one narrow,
explicit resolution in the authoritative routing policy/registry and schema or use a
plugin version that natively accepts `max`; do not claim equivalence between `xhigh` and
`max`. Add the resolved policy files to the allowlist only if that correction is actually
required.

### 3. High — no concrete plugin receipt/verdict contract makes the handoff testable

**Evidence.** Existing `runtime/session_bridge.py` authorizes two model-authored unit
files, while `runtime/finalize_evidence.py` reads a provider-specific live-proof JSON.
V1 says to make the bridge accept a structurally isolated plugin verdict and to validate a
receipt, but does not define the request, verdict, and receipt paths or required fields.
The installed plugin runs its own companion helper and stored-job workflow; its output is
not the existing runtime receipt shape. V1 postpones the first real plugin call until
verification, after the adapter would already have been implemented.

**Impact.** Different implementers can create incompatible evidence shapes or falsely
infer model, effort, authorization, and isolation from prose output. Python then cannot
deterministically prove that the accepted verdict came from the decided route or that
only authorized artifacts were supplied.

**Minimal required remediation.** Immediately after the enabled-status check, perform
one minimal read-only plugin preflight and record its actual result semantics. Add a short
artifact contract to step 3: fixed request, verdict, and receipt locations; required
execution id, route id, decided/executed model and effort, authorized input/output list,
and hashes; deterministic rejection of absent or mismatched fields. Claim only the
isolation the plugin can evidence; otherwise stop under the existing ambiguity condition.

### 4. High — the deletion instructions conflict with dirty-worktree preservation

**Evidence.** The current status contains all six simplification prompts as staged
additions, with v6 additionally modified in the working tree. Most runtime files targeted
for deletion or editing are also staged additions or staged-plus-modified files. V1 says
both to preserve user work and to delete the six prompts wholesale. Capturing status and
diffs is evidence, not protection, and the user's request authorizes removing references,
not discarding unrelated content in those files.

**Impact.** Execution can erase staged or unstaged user work unrelated to `RETIRED`, or
stop immediately because every target collides with the plan's broad collision stop
condition. Either behavior prevents a safe, efficient implementation.

**Minimal required remediation.** Classify each inventoried target against index and
working-tree state before editing. Preserve nonmatching content in staged or modified
source/planning files and remove only the affected statements; reserve whole-file/root
deletion for the provider-specific implementation files, caches, and generated run roots
already named in v1. Abort only on an overlapping hunk that cannot be separated safely.

