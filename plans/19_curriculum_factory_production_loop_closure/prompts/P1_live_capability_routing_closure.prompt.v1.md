# GOAL

Implement phase **P1 — Live capability and routing closure** of
`plans/19_curriculum_factory_production_loop_closure/curriculum_factory_production_loop_closure.plan.v1.yaml`.
Read that file first: `overall_goal`, `scope_lock`, `operating_rules`, the `P0` block, the
`P1` block, and `red_team_protocol.severity` all bind this work. Read the P0 result file
under `plans/19_curriculum_factory_production_loop_closure/results/` before touching code.

**The defect.** `runtime/run_curriculum.py:47-49` answers `--test-live-capabilities` with
an unconditional `RuntimeFailure("LIVE-CAPABILITY-CYCLE-REQUIRED", …)`, and line 65 then
refuses all generation because that gate never passes. Nothing in the repository probes a
route. `policy/routes.v1.yaml` carries proof text transcribed from executions dated
2026-07-29 and 2026-07-31, which is a record of a past environment, not proof of this one.
`runtime/capability_cycle.py` is a real Gemini proof harness but is a standalone
`__main__` script bound to a `--task-root` outside the run, and it hardcodes the forbidden
route set as the literal `forbidden_routes={"imagegen"}` at
`runtime/capability_cycle.py:82`. `runtime/routing.py` refuses bypass and mismatch inside
`Selector.select`, but nothing calls the selector before a worker, so
`SEL-EXECUTED-MATCHES-DECIDED` remains deferred under `RT-3` and `ROUTE-PROVEN` under
`RT-2`. `policy/routing/routing_policy.v1.yaml` lists only `gpt-5.6-*` models in every
`hard_rules.*.allowed_models`, so `REV-JUDGE-SINGLE-CROSS-FAMILY` is unsatisfiable by
construction: the selector cannot address a judge from another family. `meta_prompt/curriculum.prompt.v1.md`
lines 79-86 record primary-source retrieval as a declared capability divergence that no
route covers.

**Build this.**

1. A **capability preflight** that computes the selected unit set (from `--lab-id`, else
   the whole validated manifest), classifies every route in `policy/routes.v1.yaml` as
   `required`, `optional`, `unavailable`, or `forbidden`, freezes that effective route
   manifest and the containment command for each route as a durable record, then
   recomputes the run's execution-contract digest with the **P0-frozen digest algorithm
   over the P0-frozen inventory** in its post-freeze state and binds it to the run.
2. **Real bounded probes** of every route the selected run needs, each recording the exact
   command, decided model, executed model, reasoning effort, sandbox policy, result,
   elapsed time, and a proof hash over the captured bytes. A probe response is the
   smallest valid structured response for that route and nothing else.
3. **Runtime enforcement**, not declaration: a worker invocation with a missing,
   schema-malformed, selector-bypassing, or decided-versus-executed-mismatched routing
   decision is refused before any worker output can enter the run.
4. **Registration and live proof** of two capabilities that do not exist as routes today —
   bounded primary-source retrieval, and a cross-family judge that `runtime/routing.py`
   can actually decide on — alongside `worker`, `pdf`, `rasterizer`, and conditional
   `imagegen`.
5. **Catalogue truth**: every route retained in `policy/routes.v1.yaml` after this phase
   carries proof produced by this phase's own execution. An unprovable route that the
   selected run does not need is removed via `runtime.capabilities.remove_unavailable_route`,
   not assumed. An unprovable route the run does need is a stop.

**Hard constraints.**

- Preserve the precedence and ownership rules in `meta_prompt/curriculum.prompt.v1.md`
  and `policy/controller.v1.yaml`. Code owns every classification and terminal decision.
- Simulated evidence, live-capability evidence, generated-unit evidence, and
  workbook-release evidence are four distinct categories. **Never treat a probe response
  as generated-unit evidence**, and never let a capability record be admitted as, counted
  toward, or cited as unit evidence.
- **Generate no curriculum content.** No unit, lab, dossier, or `curricula/*/units/`
  artifact may be created by this phase. Probe payloads are fixed capability strings such
  as `Reply with exactly: ROUTE_OK`, never curriculum text.
- Never infer success from file presence, installed binaries, `--help` output, version
  strings, or configuration files. Validate declared outputs, hashes, and returned bytes.
- A blocked curriculum fact, a retryable tool failure, and a factory defect are three
  separate terminal classifications. Use the **P0-frozen canonical terminal vocabulary**;
  do not reopen the `SYSTEM_FAILURE` / `META_SYSTEM_FAILURE` reconciliation P0 settled.
- Update policy, schema, checks, and deferred claims atomically with the enforcement that
  makes them true — and only those whose truth this phase changes.
- Writes go beneath `ENGINE/outputs` through `runtime.io.atomic_json` and
  `runtime.io.require_internal_output`. The worktree is dirty with user-owned work: never
  stage, stash, reset, restore, clean, or overwrite anything you did not create.
- Probe bounds belong in `policy/routes.v1.yaml`'s `preflight` block. Do **not** add a
  duration governor to `policy/limits.v1.yaml`; `tests/fixtures/time_limit_present.reject.yaml`
  exists to reject exactly that and must keep rejecting.
- Do not widen a sandbox, add credentials, disable a check, or relax a schema to obtain a
  pass.

# TEST

Run `P1-T01` through `P1-T21` strictly in order. Each is a command with a recorded exit
code and hashed evidence; none may be waived, reordered, or replaced by inspection.

1. **P1-T01 — P0 inheritance and baseline.** The P0 result file exists and its frozen
   deliverables resolve: the implementation matrix, the canonical digest algorithm and its
   inventory, the canonical terminal vocabulary, and the protected dirty-work inventory.
   Capture the pre-change baseline: `./tests/run_gates.sh 5`,
   `python3 -m unittest discover -s tests/runtime -t .`, `git status --porcelain`, and the
   current `python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit
   --test-live-capabilities` refusal. Record exit codes and hashes. **Stop** if P0 has not
   executed or its digest algorithm is unavailable.
2. **P1-T02 — Deterministic effective-manifest freeze.** Over the selected unit set, every
   route in `policy/routes.v1.yaml` resolves to exactly one of `required`, `optional`,
   `unavailable`, `forbidden`. The forbidden set is read from a declared contract source
   (curriculum manifest or `policy/`), and a repository scan proves no engine module
   contains a hardcoded route-name literal for it — specifically that
   `forbidden_routes={"imagegen"}` no longer appears in `runtime/`. Two runs over identical
   inputs produce byte-identical frozen manifests and identical frozen-manifest hashes.
3. **P1-T03 — Digest recompute and bind.** After the freeze, the run's execution-contract
   digest is recomputed with the P0-frozen algorithm over the P0-frozen inventory and
   written into the preflight record. An independent recomputation from the same inputs
   reproduces it; mutating any single inventory member changes it; and a record presented
   with a stale digest is refused with the P0-frozen classification.
4. **P1-T04 — `worker` route positive proof.** One real call on the exact command in
   `policy/routes.v1.yaml` (`codex exec -s workspace-write --skip-git-repo-check -m
   <decided_model> -c model_reasoning_effort=<decided_effort>`) with the model and effort
   supplied by a `Selector.select` decision, returning the smallest valid structured
   response. The record carries command, decided model, **observed executed model**,
   effort, sandbox policy, elapsed time, and proof hash, and the observed identity equals
   the decision's `decided_model`. **Stop** if the installed CLI exposes no way to observe
   actual model identity — do not infer it from the flag you passed.
5. **P1-T05 — `pdf` route positive proof.** One real `pandoc … --pdf-engine=typst -V
   mainfont="Helvetica"` call producing a valid `%PDF` byte header, with size and proof
   hash recorded.
6. **P1-T06 — `rasterizer` route positive proof.** One real `pdftoppm -r 200 -png` call
   over the artifact `P1-T05` produced, with page-image dimensions and per-page sha256
   recorded.
7. **P1-T07 — Research route registered and proven.** Bounded primary-source retrieval is
   a route in `policy/routes.v1.yaml` with a declared command, an explicit scope bound, and
   proof from one real bounded fetch of a source addressed by exact identifier. It writes
   only inside the run's capability namespace, and `component_research` reaches it through
   selection. The divergence paragraph at `meta_prompt/curriculum.prompt.v1.md:79-86` and
   its "declares four routes" claim are reconciled to what is now true.
8. **P1-T08 — Cross-family judge registered, addressable, and proven.** A judge model from
   a provider other than the generator family is present in
   `policy/routing/model_registry.v1.yaml` (with its `prose_patterns` entry) and in the
   `allowed_models` of the judge-bearing risk classes in
   `policy/routing/routing_policy.v1.yaml`, so `Selector.select` returns it for a review
   task class and refuses a same-family judge for that class. Its live proof runs through
   the isolated path in `runtime/capability_cycle.py` and validates under
   `runtime.capabilities.validate_cross_family_proof`: real call, one `init` event, init
   model equal to decided model, zero tool-use events, tools and MCP disabled, settings
   hash resolving. `python3 -m unittest tests.runtime.test_capabilities
   tests.runtime.test_routing tests.runtime.test_gemini -v` passes.
9. **P1-T09 — Conditional `imagegen` and catalogue truth.** Two cases, both deterministic.
   Against a fixture unit set declaring a generative visual role, `imagegen` classifies
   `required` and an unproven `imagegen` stops the preflight. Against the real
   `curricula/arduino_kit` selection, where the contract forbids generated images, it does
   not classify `required`, and if it remains unprovable `remove_unavailable_route` removes
   it so `policy/routes.v1.yaml` no longer retains it — `remove_unavailable_route` must
   refuse the removal when the route is required. After the phase, **every** route still
   listed in `policy/routes.v1.yaml`
   carries a proof record produced by this phase's execution — no route retains only the
   2026-07-29 or 2026-07-31 transcript.
10. **P1-T10 — PASS semantics.** `python3 runtime/run_curriculum.py --curriculum
    curricula/arduino_kit --test-live-capabilities` performs real probes, exits `0`, and
    reports `PASS` only when every `required` route is proven in the current environment.
11. **P1-T11 — Missing required route stops before unit creation.** With a required route
    made unavailable, the command exits non-zero with the P0-frozen terminal
    classification, names the route, and the output root contains **zero** unit artifacts
    and zero worker output.
12. **P1-T12 — Unused optional route does not stop the run.** With at least one route
    classified `optional` for the selected unit set, the command reports `PASS` and exits
    `0` whether or not that route proves. The two outcomes are distinguished, not blurred:
    an optional route that probes successfully is retained with its proof; an optional
    route that does not prove is removed from the catalogue under `P1-T09`'s rule and
    recorded as removed. Neither outcome stops the run, and neither is reported as proof.
13. **P1-T13 — Negative control: unavailable executable.** With the route's executable
    removed from `PATH`, the probe classifies the route `unavailable` with a named failure
    id, emits no traceback, and never reports `PASS` for a required route.
14. **P1-T14 — Negative control: timeout.** A probe that exceeds the bound declared in
    `policy/routes.v1.yaml`'s `preflight` block is recorded as a failed probe with its
    elapsed time, never as proof. `python3 tests/gates/fr_p4_policy_schemas.py --check
    agreement` still rejects `tests/fixtures/time_limit_present.reject.yaml`.
15. **P1-T15 — Negative control: malformed response.** A probe reply that is not the
    smallest valid structured response for that route — an unparsable stream line, a
    missing or extra token, a non-`%PDF` byte header — is `FAILED`, and the route is not
    marked proven.
16. **P1-T16 — Negative control: model mismatch.** A probe whose observed executed model
    differs from the decision's `decided_model` is refused at runtime with the P0-frozen
    classification; the route is not marked proven and no worker output is admitted.
17. **P1-T17 — Negative control: forbidden sandbox widening.** A probe command carrying
    `--dangerously-bypass-approvals-and-sandbox`, a sandbox wider than the one the route
    declares, or a `forbidden`-classified route is refused **before execution**, with no
    subprocess spawned.
18. **P1-T18 — Routing decisions rejected before worker output enters the run.** Four
    separate cases — decision absent, decision schema-invalid against
    `schemas/routing_decision.schema.v2.json`, selector bypassed (worker reached without a
    prior decision, including via `--model`), and `executed_model != decided_model` — each
    refused before admission. For each: no artifact written, a named failure id, and the
    P0-frozen terminal classification for an unrecorded model call.
19. **P1-T19 — Capability records are replay-verifiable.** Every proof hash recomputes from
    the stored bytes and `validate_cross_family_proof` re-validates the stored receipt,
    with no route re-invoked during replay.
20. **P1-T20 — Capability evidence is never unit evidence.** Admitting a capability record
    as generated-unit evidence is rejected with a named failure id; no file exists under
    any `curricula/*/units/`; the unit-scanning `FR-P5-*` gates still report zero generated
    units; and `RT-7` in `policy/deferred.v1.yaml` is unchanged.
21. **P1-T21 — Atomic contract reconciliation and regression.** `ROUTE-PROVEN` in
    `policy/checks.v1.yaml` states its quantifier over the **frozen effective manifest**
    and moves to `verified_by` an executing gate; `RT-2` and `RT-3` in
    `policy/deferred.v1.yaml` state what is now true without being declared discharged —
    P6 owns their disposition. `schemas/routes.schema.v1.json` and any other contract
    changed by new route fields, statuses, or bounds is updated in the same change.
    `./tests/run_gates.sh 5` and `python3 -m unittest discover -s tests/runtime -t .` show
    no new or worsened result against the `P1-T01` baseline, gate id by gate id.

A recorded probe, a passing schema, and an installed binary are each necessary and none is
sufficient: `PASS` requires a real call made in this environment during this phase.

# LOOP

Execute the tests in order. On a failure, record the test id, exact command, exit code,
evidence hashes, and a one-line root cause narrowed to a single artifact. Revise only that
artifact. Then rerun in this order: any policy, schema, or route file change forces
`P1-T02` and `P1-T03` again before anything else, because the frozen manifest and the
execution-contract digest are now different; then the failed test; then every later test
whose evidence could have changed. Continue until `P1-T01` through `P1-T21` all pass,
including every real probe and every negative control.

Never respond to a failure by widening a sandbox, adding a credential, substituting a route
the policy does not declare, marking a route proven from help text or a prior transcript,
removing a `required` route, weakening a schema, gate, or check, moving a probe bound into
`policy/limits.v1.yaml`, or fabricating a receipt. Never repair a failure by touching
user-owned dirty work.

**Stop conditions.** Stop, report blocked, and claim nothing if a required route cannot be
invoked within its declared sandbox and no policy-compliant route exists, or if actual
model identity or family cannot be observed and compared with the routing decision. A stop
is a truthful terminal state with its evidence recorded, never a partial pass.

**Before the phase may be claimed done**, all of the following must exist: the frozen
effective route manifest with its hash and per-route classification; the recomputed
execution-contract digest and its independent recomputation; a probe record per required
and retained route carrying command, model, effort, sandbox, result, elapsed time, and
proof hash; the cross-family judge selection decision and its validated receipt; the
research route proof; the rejected-decision evidence for all four `P1-T18` cases and all
five negative controls in `P1-T13` through `P1-T17`; the `P1-T01` and `P1-T21` gate
comparisons; and confirmation that no unit artifact was created.

Write these into `plans/19_curriculum_factory_production_loop_closure/results/P1.result.v1.md`
— baseline, changed paths, test ids with commands and exit codes, route proofs, digests,
rejected-decision evidence, contract reconciliations made and deliberately not made,
remaining failures, and the final verdict. Leave no draft or scratch file behind. Claim
completion only when every test above has passed with real evidence.
