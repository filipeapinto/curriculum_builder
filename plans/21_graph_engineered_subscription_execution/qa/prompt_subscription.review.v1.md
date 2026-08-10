# Plan 21 prompt/subscription/security QA — round 1

## Verdict

**CHANGES REQUIRED — 1 Critical, 4 High, 2 Medium.** Plan 21 is a material
architectural improvement over Plan 20: all seven phase prompts have explicit
GOAL/TEST/LOOP sections, the repair loops are bounded and targeted, Claude's
current logout is treated honestly, model outputs do not own control flow, and
the evaluator context rules are substantially independent and fail-closed.
Those strengths do not overcome the blocking defects below. In particular, the
plan graph cannot satisfy its own terminal/failure vocabulary, the orchestrator
requires a compiler before the phase that creates it, and the currently
specified Codex receipt cannot prove the executed model identity that P2 makes
mandatory.

This is therefore not a PASS under the plan's own zero-Critical/High exit rule.

## Evidence gathered

- Read every Plan 21 artifact and all three Plan 20 QA reports in full.
- `graph_engineered_subscription_execution.plan.v1.yaml` validates against its
  sibling JSON Schema. This proves only the schema's shallow shape; it does not
  resolve the semantic contradictions below.
- Local capability facts on 2026-08-09:
  - `claude --version` → `2.1.226 (Claude Code)`.
  - `claude auth status` → `loggedIn: false`, `authMethod: none`,
    `apiProvider: firstParty`.
  - `codex --version` → `codex-cli 0.147.0`.
  - `codex login status` → `Logged in using ChatGPT`.
  - The checked model-key/provider environment variables were unset; values
    were never printed.
- A real ephemeral, read-only Codex canary succeeded under the active ChatGPT
  login. Its complete JSONL event vocabulary was `thread.started`,
  `turn.started`, `item.completed` (an `agent_message`), and `turn.completed`
  (usage). No event disclosed an observed/executed model. The canary used
  `--ephemeral --ignore-user-config --ignore-rules --sandbox read-only
  --skip-git-repo-check --json -C /private/tmp` and returned `OK`.
- A proposed canary that would have asked Codex to read a private repository
  file from outside its staged working directory was not run because doing so
  would export private workspace content to an external service. No conclusion
  below relies on that unexecuted test.

## Findings

### 1. Critical — The plan graph cannot represent its own terminal and failure semantics, so P1-T12 must reject Plan 21

**Evidence.** The plan declares `ACCEPTED`, `BLOCKED`, `SYSTEM_FAILURE`, and
`INTERRUPTED` as terminal states and seven distinct failure classes
(`graph_engineered_subscription_execution.plan.v1.yaml:39-51`). It also says
that `BLOCKED` is reserved for a named unavailable external safety-critical fact
and factory defects become `SYSTEM_FAILURE` (lines 188-189). But every phase
failure edge goes only to `BLOCKED` (lines 173-179), while the success terminal
is named `APPROVED`, not declared `ACCEPTED` (line 172). The sibling edge schema
makes the mismatch structural: `to` permits only `P<n>`, `APPROVED`, or
`BLOCKED`, so neither `SYSTEM_FAILURE` nor `INTERRUPTED` can be encoded
(`graph_engineered_subscription_execution.schema.v1.json:90-99`). The
orchestrator repeats the defect by directing every stopped node to the
`BLOCKED` edge (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:27-31`).

This is not terminology alone. P1's compiler must require exactly one legal edge
for every nonterminal failure class (P1-T04, `prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:23-24`),
reject missing failure edges, and self-compile Plan 21 (P1-T12, line 31). A P1
compiler faithful to those tests must reject the graph because factory defects,
interrupts, and convergence exhaustion have no representable terminal edge.
Conversely, a compiler that accepts it has weakened its own edge-totality and
terminal-authority requirements.

**Required remediation.** Define one canonical terminal namespace and extend
both plan edges and the schema to include every required terminal. Route each
stop/failure class to its lawful terminal (including `SYSTEM_FAILURE` and
`INTERRUPTED`) rather than sending all failures to `BLOCKED`. Add a biting
self-compile fixture that demonstrates each failure class has a legal witness
path and that a factory defect cannot reach `BLOCKED`.

### 2. High — The required Codex executed-model identity is not observable from the specified CLI receipt, making P2 a known blocker now

**Evidence.** P2 requires a Codex canary with "observed identity" (P2-T06),
requires requested/observed/registry identity equality (P2-T13), says never to
infer model identity solely from the requested id, and requires a hard stop when
observed identity cannot be checked
(`prompts/P2_subscription_worker_adapter.prompt.v1.md:20-21,29-30,37,51-54`).
The installed `codex exec --help` provides `--json`, `--output-schema`, and
`--output-last-message`, but no flag that emits the executed model. The real
Codex 0.147.0 canary described above likewise returned a valid event stream and
usage without any model/provider/family field. `--output-last-message` can
constrain the assistant's final answer but cannot turn a model's self-assertion
about its identity into observed execution evidence.

The stop condition is honest once discovered, but Plan 21's log names only the
Claude logout as the current implementation blocker
(`plans.log.md:13-15`). The same plan presents P2 as live-provable after OAuth is
restored. Current evidence shows a second, independent blocker: the specified
Codex CLI surface cannot meet P2-T06/P2-T13 without either trusting the requested
`-m` value (explicitly forbidden) or introducing a separately verified
execution-observation mechanism not scoped by the prompt.

**Required remediation.** Either name a concrete, testable Codex-side source of
executed model identity that is independent of the requested id and bind it into
the receipt, or revise the identity contract to the strongest evidence the CLI
actually exposes and explicitly accept/reject that weaker guarantee. Record the
current inability as a P0/P2 blocker alongside Claude logout; do not defer its
discovery to P2 implementation.

### 3. High — The orchestrator requires the graph compiler before P1 creates it

**Evidence.** The orchestrator says to execute a *compiled* Plan 21 graph and,
"Before activating a node, compile the plan graph"
(`prompts/P_ALL_graph_orchestrator.prompt.v1.md:3-5,13-19`). This applies to P0
and P1. Yet `runtime/prompt_graph.py` does not currently exist, and P1 is the
phase authorized to create it and its schema/tests
(`graph_engineered_subscription_execution.plan.v1.yaml:67-79`). P0 only performs
sibling JSON-Schema validation (P0-T01), not static graph compilation
(`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:31-32`). P1 cannot be
activated without a compiler, while the compiler cannot be created without
activating P1.

**Impact.** A literal P_ALL run stops before P0. Treating schema validation as
compilation would silently bypass the reachability, cycle, acceptance-dominance,
context, ownership, and failure-edge checks that distinguish P1 compilation
from P0-T01.

**Required remediation.** Specify a deterministic bootstrap path: for example,
P0 runs schema/digest/scope checks, P1 is the only bootstrap implementation
phase, and the newly built compiler must compile Plan 21 before P2/P3 activation.
Alternatively provide a pre-existing, separately hashed bootstrap compiler. Do
not call JSON-Schema validation "compile."

### 4. High — Write authorization is contradictory and nondeterministic, including an undeclared shared log written by parallel phases

**Evidence.** The plan says each phase prompt authorizes only its declared
outputs (`graph_engineered_subscription_execution.plan.v1.yaml:12-14`). No
node's `authorized_outputs` includes `plans.log.md` (lines 58-60, 72-76, 88-93,
105-110, 122-126, 138-141, 153-156), but every phase prompt instructs the
executor to append that file (P0 lines 53-55; P1 lines 43-46; P2 lines 51-55; P3
lines 40-43; P4 lines 52-56; P5 lines 47-51; P6 lines 40-44). P0 even says it may
write only two outputs "and append one log entry"
(`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:14-17`), which is three
write targets under the graph contract.

P1 and P2 may run in parallel (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:21-23`),
so both append the same unowned file with no deterministic reducer, locking, or
idempotency key. That directly conflicts with the plan's deterministic reducer
invariant (`graph_engineered_subscription_execution.plan.v1.yaml:185-187`). In
addition, P4/P5/P6 authorize prose placeholders such as "runtime and policy
files explicitly frozen by P0" and "fresh ... roots selected by P0" rather
than concrete paths (lines 122-126, 138-141, 153-156). The baseline contract
that is expected to resolve those selectors has no schema among P0's authorized
outputs, so downstream scope enforcement cannot validate a canonical shape.

**Impact.** A strict orchestrator must refuse each log append; a permissive one
violates its own allowlist. Parallel appends can produce order-dependent or lost
records. The prose scope selectors also recreate the prior-runs problem of
discovering the real write surface during execution rather than compiling it.

**Required remediation.** Add the log as an explicitly owned artifact and make
parallel nodes emit per-node immutable log events that a deterministic join
reduces, or serialize a single log writer. Define and schema the P0 baseline
contract, including exact path-set syntax, and require the compiler to resolve
all symbolic scopes to canonical concrete paths before a node activates.

### 5. High — "Subscription OAuth" has no specified evidence predicate and can be confused with paid Anthropic Console OAuth

**Evidence.** P2-T03 says Claude must "prove subscription OAuth" and that
ambiguous auth fails (`prompts/P2_subscription_worker_adapter.prompt.v1.md:27-28`),
but neither P0 nor P2 defines which `claude auth status` fields and values prove
that billing class. P0 freezes the current output, which is logged out and thus
contains no subscription evidence (P0-T06, `prompts/P0_contract_and_evidence_freeze.prompt.v1.md:36-37`).
Anthropic's official setup documentation distinguishes a Claude App Pro/Max
subscription from an Anthropic Console OAuth login that requires active Console
billing; both are first-party login paths
([Set up Claude Code](https://docs.anthropic.com/en/docs/claude-code/getting-started)).
Thus `loggedIn: true`, an OAuth-shaped `authMethod`, and
`apiProvider: firstParty` are not by themselves proof that usage draws from a
subscription rather than pay-as-you-go Console billing.

The prompt correctly rejects API-key environment variables, but that is not
equivalent to proving the positive billing entitlement. P2-T04 also names only
"a model API-key variable" and does not freeze the full provider/base-URL/key-
helper precedence surface (`prompts/P2_subscription_worker_adapter.prompt.v1.md:28-29`).

**Required remediation.** Freeze an exact, versioned positive predicate for
Claude subscription entitlement (including required `auth status` fields), the
negative provider/key/helper/base-URL precedence checks, and a real canary whose
receipt binds that predicate. If the installed CLI cannot expose an
unambiguous entitlement field, keep P2 blocked rather than accepting generic
first-party OAuth.

### 6. Medium — The Codex `read-only`/working-directory description does not itself establish authorized-input isolation

**Evidence.** P2 describes Codex isolation as an ephemeral invocation with
user config isolated where feasible, a `read-only` sandbox, and an isolated
working directory (`prompts/P2_subscription_worker_adapter.prompt.v1.md:10-12`),
then requires an unstaged-file access attempt to be denied (P2-T07, line 31).
Local `codex exec --help` describes `-C/--cd` as the working root and `--sandbox
read-only` as the policy for model-generated shell commands; it does not expose
an `exec` option that declares an authorized readable-root allowlist. The local
CLI's separate `codex sandbox --help` does expose
`--sandbox-state-readable-root`, but only when applying an explicit sandbox
state/profile. Plan 21 names neither that mechanism nor an equivalent outer OS
boundary.

P2-T07 and the stop condition are good and prevent a false pass, so this is not
raised as a High. But "isolated working directory" must not be implemented as
`-C` plus `--sandbox read-only` and then reported as structural read isolation.

**Required remediation.** Require a concrete readable-root containment profile
or equivalent outer sandbox, hash it into the command/policy receipt, and make
P2-T07 test both relative and absolute unstaged paths. If no such boundary is
available, take the declared stop.

### 7. Medium — The research/assessment states an Anthropic monthly-credit policy that official current guidance says was paused

**Evidence.** The assessment says subscription `claude -p` "uses a separate
monthly Agent SDK credit" (`assessment/plan20_gap_assessment.v1.md:33-41`).
Anthropic's current official June 2026 notice says that change was paused: the
monthly credit is not available and, for now, `claude -p` continues to draw from
subscription usage limits
([Use the Claude Agent SDK with your Claude plan](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)).

This does not invalidate the subscription-only architecture—`claude -p` remains
subscription-backed when the correct entitlement is active—but it is a dated
billing claim inside the Plan 21 decision record and should not survive an
August 2026 state-of-the-art review.

**Required remediation.** Correct the assessment to the paused/current policy,
add the official dated source, and avoid making the execution contract depend on
a credit mechanism that can change independently of CLI authentication.

## Non-blocking confirmations

- Every P0-P6 prompt and P_ALL contains a distinct GOAL, TEST, and LOOP. Test ids
  are complete and loops identify targeted repair ownership, mandatory retests,
  and stop/convergence conditions.
- Claude's present logout is handled honestly: P0 records it without fabricating
  capability, P2 requires a stop, and P_ALL allows P1 to finish while preventing
  P3 from crossing the join
  (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:35-37`,
  `prompts/P2_subscription_worker_adapter.prompt.v1.md:51-54`,
  `prompts/P_ALL_graph_orchestrator.prompt.v1.md:21-23`).
- The installed CLIs support the core structured-output flags claimed by P2:
  Claude exposes `-p`, `--safe-mode`, `--no-session-persistence`, `--tools`,
  `--output-format`, and `--json-schema`; Codex exposes `exec --ephemeral
  --ignore-user-config --ignore-rules --sandbox read-only --json
  --output-schema --output-last-message`.
- One normalized request/receipt *interface* with provider-specific drivers is
  plausible. It should normalize results and failure classes, not pretend that
  Claude and Codex have identical native security or identity evidence.
- P5's evaluator independence is well specified at the context/control layer:
  immutable candidate digests, no author transcript or sibling verdicts,
  schema-bound verdicts, deterministic aggregation, cross-family final judging,
  and fail-closed missing verdicts (`prompts/P5_evaluator_optimizer_acceptance.prompt.v1.md:6-12,16-37`).

## Exit decision

**NOT APPROVED.** Resolve all Critical and High findings, rerun schema and
self-compile checks, re-check both CLI capability surfaces, and repeat the full
independent review round. Do not use the declining number of findings as a
substitute for satisfying the plan's zero-Critical/High rule.
