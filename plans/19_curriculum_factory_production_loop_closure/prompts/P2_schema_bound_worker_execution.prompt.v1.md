# GOAL

Implement phase **P2 — Schema-bound worker execution** of
`plans/19_curriculum_factory_production_loop_closure/curriculum_factory_production_loop_closure.plan.v1.yaml`
(status `approved`; schema at the sibling `.schema.v1.json`). Read that file first. The
plan's `scope_lock`, `operating_rules` and `red_team_protocol.severity` govern this work in
full; the phase block with `id: P2` is the contract you are discharging.

Build the reusable worker adapter that turns **one controller task into one bounded,
observable, schema-valid artifact**. Nothing else. P2 does not wire the controller, does not
implement state handlers, does not touch `--lab-id` or `--all`, and does not migrate
`runtime/session_bridge.py` — P3 owns those. Deterministic Python alone constructs requests,
enforces boundaries, admits artifacts, classifies failures and writes records.

P2 depends on P1 and consumes P1's output **by contract**, because P1 has not executed when
you read this. Read, never re-derive:

- **the P1-frozen effective route manifest** — the concrete `worker` route id, its exact
  executable invocation, and its declared sandbox policy. Today `policy/routes.v1.yaml`
  declares `worker` as
  `codex exec -s workspace-write --skip-git-repo-check -m <decided_model> -c model_reasoning_effort=<decided_effort>`;
  P1 freezes what is actually proven. Take the frozen record as authoritative and never
  re-parse policy, hardcode a command, or substitute a route.
- **the P1-frozen per-call containment command** — the mechanism that denies undeclared
  reads and writes. Containment is structural. A sentence in a prompt telling a worker not
  to read something is not containment and never satisfies this phase.
- **the P1-frozen execution-contract digest** — computed by P1 from the P0-frozen canonical
  digest algorithm. P2 binds it; P2 never defines a second digest, and never recomputes it
  under a different algorithm.
- **the P0-frozen state→artifact matrix** — the authority for which worker artifact types the
  controller exercises. Registry completeness is measured against that matrix, never against
  a list you write by hand.

Operating rules, applied literally (copied from the plan; they bind every step):

- Preserve the precedence and ownership rules already declared in
  `meta_prompt/curriculum.prompt.v1.md` and `policy/controller.v1.yaml`.
- Treat simulated evidence, live-capability evidence, generated-unit evidence, and
  workbook-release evidence as distinct categories.
- Never infer success from file presence; validate declared outputs, hashes, checks,
  transitions, and terminal decisions.
- **A worker may write only its declared schema-bound artifact and may never decide
  transitions or acceptance.**
- A blocked curriculum fact, a retryable tool failure, and a factory defect remain separate
  terminal classifications.
- Preserve accepted units on resume and refuse overwrite unless a new output version is
  explicitly requested.
- Execute phases in dependency order; atomically update policy, schema, checks, and deferred
  claims when their enforcement becomes true.
- Stop when a phase definition of success cannot be proven.

Hard constraints on the adapter itself:

1. **One invocation interface** serves the authoring, research, review and revision roles.
   Role identity is a parameter of the request, never a separate code path with its own
   boundary rules.
2. **Sealed request.** A request is built only from: authorized input paths, role
   instructions, stable check ids (from `policy/checks.v1.yaml` and the curriculum's own
   check inventory), exactly one output schema id, exactly one authorized output path, the
   validated routing decision, and the execution-contract digest. Anything not in the
   authorized input list is not reachable by the worker and its bytes never enter the
   request.
3. **Staged filesystem.** Each call gets its own staging root beneath the run's output root
   (`runtime/io.require_internal_output` already pins output roots beneath `<engine>/outputs`).
   The staging root holds copies of exactly the authorized inputs and is the worker's working
   directory and only writable region. Admission then moves the single declared artifact into
   the run root atomically (`runtime/io.atomic_json`, `require_within`, `sha256_file`).
4. **Atomic admission.** Absent, extra, malformed, out-of-scope, or schema-invalid output is
   rejected and admits nothing. Accepted state stays byte-identical across a rejected call.
5. **Four failure classes, normalized:** transient tool error, invalid output, policy
   violation, genuine domain block. Each maps to exactly one `failure_type` in
   `schemas/execution_log.schema.v2.json` (`missing-input`, `bad-input`, `tool-error`,
   `wrong-output`, `partial-run`, `other`) and one terminal classification via
   `runtime/controller.RuntimeFailure`. `BLOCKED` is legal only for a named unavailable
   safety-critical fact per `policy/controller.v1.yaml → blocked_eligibility`; a tool,
   schema, render or factory defect is never a block.
6. **Bounded retry** via `runtime/retry.RetryTracker` under `policy/limits.v1.yaml`. Exhausting
   a bound produces an honest failure, never a silent pass and never an extra call.
7. **Full observation.** Every call records stdout, stderr, exit status, the routing decision
   (validated by `runtime/routing.Selector.validate_decision`, decided model equal to executed
   model), staged input hashes, start/end/elapsed, output hash, and failure class — logged
   through `runtime/logger.ExecutionLogger` as one paired `ACT` operation with
   `action_kind: model_call` and a `decision_id`.
8. **No authority.** The adapter exposes no parameter, field or return value by which a worker
   can choose a next state, broaden its own inputs, or write a terminal decision. Worker
   output containing transition, acceptance or run-status fields is rejected, not filtered.
   `checkpoints/`, `acceptance.json`, `run_state.json` and `execution_log.jsonl` are never
   writable by a worker.
9. **Registry.** One policy manifest assigns exactly one output schema to every worker artifact
   type in the P0-frozen matrix. It carries its own `schema:` pointer, because
   `tests/gates/fr_p4_policy_schemas.py` resolves manifest/contract pairing from the manifest's
   own pointer — a manifest without one fails the existing gate.
10. **Idempotency.** Replaying a completed request appends no duplicate log record, writes no
    duplicate route record, and never overwrites a valid accepted artifact.

The adapter — not the worker — writes the per-call checkpoint. `runtime/checkpoint.Checkpoints.write`
has no digest field today, so P2 extends it **additively** with the execution-contract digest,
leaving every existing caller and `valid_prefix()` behaviour intact.

Allowlist. Create or modify only: `runtime/worker.py`; the additive digest field in
`runtime/checkpoint.py`; the new worker schemas under `schemas/` (request, result/route
record, and the registry contract); the registry manifest under `policy/`;
`tests/runtime/test_worker.py`; `tests/runtime/test_worker_adversarial.py`; new fixtures under
`tests/fixtures/`; run artifacts beneath `<engine>/outputs/`; and
`plans/19_curriculum_factory_production_loop_closure/results/P2.result.v1.md`. Do not edit
`runtime/session_bridge.py`, `runtime/controller.py`, `runtime/run_curriculum.py`,
`runtime/run_state.py`, or any existing check/limit/route policy. The worktree is dirty with
pre-existing user work: never stage, stash, reset, restore, clean, overwrite or delete it.

# TEST

Run P2-T01 through P2-T19 strictly in order. Every test is a committed, executable assertion
under `tests/runtime/`, except P2-T01 and P2-T19, which are captured commands.

1. **P2-T01 — Baseline.** Before any edit, capture and hash: `git status --porcelain`,
   `python3 -m pytest tests/runtime -q`, and `./tests/run_gates.sh 5`. Record per-gate ids and
   results. This is the only comparison basis for P2-T19.
2. **P2-T02 — P1 precondition binding.** The adapter refuses to build or invoke anything unless
   the P1 capability-preflight record is present, every required route is proven, and the
   execution-contract digest recomputes. A tampered or absent digest refuses **before** any
   staging directory is created and before any process is spawned; assert zero staged files
   and zero `model_call` log records.
3. **P2-T03 — Sealed request, per role.** For `authoring`, `research`, `review` and `revision`,
   the built request validates against the worker-request schema and carries exactly: role,
   authorized inputs, stable check ids, one output schema id, one authorized output path,
   routing decision id, execution-contract digest. Absent, extra, mistyped, traversal and
   absolute-path fields are each rejected by a separate assertion. Assert the serialized
   request contains no bytes from any file outside its authorized input list and no repository
   path outside the staging root.
4. **P2-T04 — Staged filesystem is exactly the authorized set.** Enumerate the staging tree and
   assert it equals the declared input list by path count and per-file `sha256_file`; assert no
   symlink in the tree resolves outside the staging root; assert the worker's working directory
   is the staging root.
5. **P2-T05 — Undeclared read denied.** A fake executor that reads an undeclared repository file
   (for example `policy/checks.v1.yaml` or another unit's `acceptance.json`) fails the call and
   is classified `policy violation`. Separately assert the invocation's sandbox arguments equal
   the P1-frozen containment command exactly — no widening, and never
   `--dangerously-bypass-approvals-and-sandbox`.
6. **P2-T06 — Path escape denied.** Writes to `../`, to an absolute path outside the staging
   root, and through a symlink whose target is outside it are each rejected with
   `runtime/io.BoundaryError` or the adapter's own refusal. Hash the whole run root before and
   after each attempt and assert byte-identical.
7. **P2-T07 — Valid admission.** A valid artifact of a registered type is admitted atomically to
   the authorized output path, its `sha256` recorded in the result record, and exactly one file
   is added to the run root. Assert the artifact validates against the schema the registry
   assigns to its type.
8. **P2-T08 — Admission negatives.** Six separate assertions: output absent; an extra file
   alongside the declared artifact; malformed JSON in the artifact; schema-invalid JSON;
   malformed structured output from the route itself (non-JSON or truncated stdout stream);
   artifact written to an out-of-scope path. Each rejects, admits nothing, leaves accepted
   state byte-identical, and yields a distinct normalized failure class.
9. **P2-T09 — Failure normalization table.** A table test asserts exactly four classes, each
   mapping to one `execution_log.schema.v2.json` `failure_type` and one terminal classification.
   Assert no tool error, invalid output, or policy violation can map to `BLOCKED`, and that a
   domain block requires a named unavailable safety-critical fact.
10. **P2-T10 — Bounded retry.** Transient and invalid-output retries are bounded by
    `RetryTracker` limits sourced from `policy/limits.v1.yaml`. Count executor invocations:
    exceeding a bound raises the honest failure, performs no further call, and admits nothing.
11. **P2-T11 — Role × failure-class matrix.** Fake executors exercise every one of the four
    roles against every one of the four failure classes plus success. A meta-assertion fails if
    any role/class pair in the matrix is unexercised, so adding a role without tests breaks the
    build. Assert all four roles reach the route through one public entry point in
    `runtime/worker.py` — no per-role invocation path exists.
12. **P2-T12 — Registry completeness.** Every artifact type in the P0-frozen state→artifact
    matrix has exactly one registry entry; a missing entry, a duplicate entry, and an entry
    naming a nonexistent or non-Draft-2020-12 schema each fail. Assert the registry manifest
    carries its own `schema:` pointer and that `./tests/run_gates.sh 5` still passes the
    `FR-P4` manifest-pairing gate.
13. **P2-T13 — No worker authority.** Worker output containing `terminal_state`, `next_state`,
    `acceptance`, `run_status`, or a broadened input list is rejected, not sanitized. Attempts to
    write `checkpoints/`, `acceptance.json`, `run_state.json` or `execution_log.jsonl` are
    rejected. Assert by source inspection that `runtime/worker.py` neither imports
    `runtime.run_state` nor writes an acceptance or checkpoint record.
14. **P2-T14 — Prompt injection through curriculum data.** Stage a curriculum input whose text
    instructs the worker to ignore its authorized outputs, write elsewhere, or declare the unit
    accepted. With a fake executor that fully obeys the injected text, the call still rejects,
    admits nothing, and leaves accepted state byte-identical. Assert the authorized input list,
    authorized output path and sandbox arguments are unchanged by the injected content —
    containment is structural, not instructional.
15. **P2-T15 — Identity and evidence capture.** One call records stdout, stderr, exit status,
    routing decision with `decided_model == executed_model` via `Selector.validate_decision`,
    staged input hashes, start/end/elapsed, output hash and failure class. Assert exactly one
    paired `ACT` operation with `action_kind: model_call` and a non-empty `decision_id`, and that
    `ExecutionLogger.audit()` reports zero `unclosed_starts`, `duplicate_closes` and
    `unknown_closes`.
16. **P2-T16 — Digest binding.** The request, the route record, the admitted artifact record and
    the adapter-written checkpoint all carry the same execution-contract digest. Mutating the
    digest in any one of the four makes verification fail, with a separate assertion per record.
    Assert existing `Checkpoints.write` callers and `valid_prefix()` still pass unchanged.
17. **P2-T17 — Replay idempotency.** Re-running a completed request adds no log record, no
    duplicate route record, and does not overwrite the valid admitted artifact (assert its
    `sha256` and mtime-independent bytes unchanged). Re-running the same request under a changed
    input set or changed digest refuses rather than overwriting.
18. **P2-T18 — Live canary.** Exactly one real call over the P1-frozen `worker` route producing
    the smallest valid artifact of a registered type. It must jointly prove: the adapter,
    schema admission, atomic write, log pairing with `decision_id`, executed-model identity
    equal to the decided model, the frozen containment arguments, and digest binding. Record the
    command, model, effort, sandbox policy, elapsed time, exit status, stdout/stderr hashes and
    artifact hash. A simulated, mocked or hand-written canary is not acceptance and never
    satisfies this test.
19. **P2-T19 — Regression and delta.** Re-run `python3 -m pytest tests/runtime -q` and
    `./tests/run_gates.sh 5`; compare by gate id against P2-T01 and accept no new or worsened
    result. Assert `git status --porcelain` shows changes only within the GOAL allowlist and that
    every pre-existing dirty path from P2-T01 is byte-identical.

P2-T18 is required for acceptance. Contract tests with fake executors (P2-T11) cannot
substitute for it, and it cannot substitute for them.

# LOOP

Execute the tests in order. On any failure, record the test id, the exact command, the exit
code, the relevant hashes, and a narrow root cause. Revise only the in-scope artifact that
caused the failure. Then immediately re-run the containment and authority set — P2-T04, P2-T05,
P2-T06, P2-T13, P2-T14 — because any adapter change can move a boundary. Then re-run the failed
test and every later test whose evidence could have changed. Continue until P2-T01 through
P2-T19 all pass, including the live canary and both gate comparisons.

Do not waive, reorder, weaken or replace a test. Never respond to a failure by widening the
sandbox, substituting a route, replacing structural containment with prompt instructions,
granting the worker a broader input or output set, mocking the canary, editing a check or limit
policy, or touching user work.

Stop without claiming success — per the phase's stop conditions and the plan's Critical/High
severity definitions — if:

- the chosen worker route cannot enforce authorized read and write boundaries (P2-T05 or
  P2-T06 cannot pass with a policy-compliant route);
- a worker result cannot be tied unambiguously to one request, one route decision and one
  output hash (P2-T15, P2-T16 or P2-T17 cannot pass);
- the P1-frozen route manifest, containment command or execution-contract digest is absent,
  ambiguous, or contradicts the P0-frozen matrix;
- passing would require work outside the GOAL allowlist, or a new or worsened gate result that
  cannot be repaired in scope.

In every stop case, report the blocker with its evidence and leave the repository consistent:
no partially wired adapter presented as complete, no failing test deleted, no result file
claiming more than the records support.

Before claiming done, write
`plans/19_curriculum_factory_production_loop_closure/results/P2.result.v1.md` containing: the
P2-T01 baseline and the P2-T19 comparison per gate id; the changed-path delta with hashes; the
registry table (artifact type → output schema); the failure-class table (class → log
`failure_type` → terminal classification); **per-role contract test results** for all four
roles across every failure class with the P2-T11 matrix coverage proof; **the live canary
record** from P2-T18 with command, route id, decided and executed model, effort, sandbox
policy, elapsed time, exit status and artifact hash; **the adversarial test outcomes** for
P2-T05, P2-T06, P2-T08, P2-T13 and P2-T14, each with its before/after run-root hash; any
remaining failure; and the final verdict. Claim completion only when every test from P2-T01
to P2-T19 has passed and the delta matches the allowlist.
