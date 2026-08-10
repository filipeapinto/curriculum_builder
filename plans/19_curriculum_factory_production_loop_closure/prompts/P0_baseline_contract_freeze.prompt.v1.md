# GOAL

Execute phase **P0 — Executable baseline and contract freeze** of
`plans/19_curriculum_factory_production_loop_closure/curriculum_factory_production_loop_closure.plan.v1.yaml`
(schema: the sibling `.schema.v1.json`). Read that file first. Its `scope_lock`,
`operating_rules` and `red_team_protocol.severity` bind this phase in full.

P0 establishes **one reproducible baseline and a precise production behavior table before
changing the runtime**. It inventories, freezes, reconciles self-contradicting active
contracts, and adds failing tests. It implements **no production behavior**. Any commit
that makes `--lab-id`, `--all`, or `--test-live-capabilities` do real work is out of scope
and is a phase failure, not progress.

These `operating_rules` bind P0 literally:

- Preserve the precedence and ownership rules already declared in
  `meta_prompt/curriculum.prompt.v1.md` and `policy/controller.v1.yaml`.
- Treat simulated evidence, live-capability evidence, generated-unit evidence, and
  workbook-release evidence as distinct categories. The existing simulated path is
  simulated-controller evidence only and may never be recorded as production evidence.
- **Never infer success from file presence**; validate declared outputs, hashes, checks,
  transitions, and terminal decisions.
- Preserve accepted units on resume and refuse overwrite unless a new output version is
  explicitly requested.
- Atomically update policy, schema, checks, and deferred claims when their enforcement
  becomes true. **No enforcement becomes true in P0**, so every
  `enforced_at_runtime: false` in `policy/controller.v1.yaml` stays `false` and every
  `MAPPED, NOT EXECUTED` check keeps its `RT-` id.
- Stop when a phase definition of success cannot be proven.

## Ground truth you must not re-derive incorrectly

Confirmed executable behavior at the time this prompt was written:

| Invocation (all prefixed `python3 -m runtime.run_curriculum --curriculum curricula/arduino_kit`) | exit | classification |
|---|---|---|
| `--preflight` | 0 | `{"status": "PASS", ...}` from `CurriculumRuntime.static_preflight`; writes nothing to disk |
| `--test-static` | 0 | same code path as `--preflight` |
| `--test-simulated-all --output-root outputs/<fresh>` | 0 | `terminal_state: ACCEPTED`, `coverage: simulated-controller-only` |
| `--test-live-capabilities` | 2 | `SYSTEM_FAILURE` / `LIVE-CAPABILITY-CYCLE-REQUIRED` (unconditional raise, `runtime/run_curriculum.py:47`) |
| `--lab-id L01` | 2 | `SYSTEM_FAILURE` / `LIVE-GENERATION-NOT-PREFLIGHTED` (`runtime/run_curriculum.py:65`) |
| `--all` | 2 | `SYSTEM_FAILURE` / `LIVE-GENERATION-NOT-PREFLIGHTED` (same raise) |

Those three refusals are the three central production gaps. `runtime/controller.py`
implements only `simulate()`. `runtime/session_bridge.py` is the manual `prepare`/`finalize`
bridge with a hardcoded `MODEL_ID` and a default `--curriculum curricula/arduino_kit`.
`runtime/capability_cycle.py` performs a real Gemini probe but is a separate CLI, unreachable
from `runtime/run_curriculum.py`. `runtime/run_state.manifest_unit_ids()` reads
`results/gate_1_static_preflight.json`, which **no production code writes** — only
`tests/runtime/unit_fixture.py`.

Known active-contract contradictions to reconcile (find any others; do not assume this list
is exhaustive):

1. **Terminal vocabulary is not canonical.** `policy/controller.v1.yaml:58`
   `terminal_states: [ACCEPTED, BLOCKED, SYSTEM_FAILURE]`; the same file's
   `terminal_conditions` emits `META_SYSTEM_FAILURE`; `policy/failures.v1.yaml` uses
   `META_SYSTEM_FAILURE` and `META_DRIFT_STOP`; `runtime/run_state.py:26` treats
   `ACCEPTED_PENDING_REVIEW` as completed; `schemas/run_lifecycle.schema.v1.json` enumerates
   `IN_PROGRESS, PARTIAL, INTERRUPTED, BLOCKED, COMPLETE`; `CurriculumRuntime.simulate`
   returns `terminal_state: "INTERRUPTED"`. Detailed failure ids (`LIVE-*`, `PRECONDITION-*`,
   `REPEAT-FAILURE`, `LOG-GATE-FAILED`, `FINAL-LOG-AUDIT`, condition `C1`, the `A`/`B`
   series) are a separate namespace and must never occupy a terminal-state field.
2. **Fixed L01-L35 constraint.** `schemas/curriculum.schema.v5.json:160` states the schema
   does not fix a lab count; lab `id` uses `^L[0-9]{2,3}$` (line 191); but
   `sequence.prerequisites` and `sequence.prepares_for` use `^L(0[1-9]|[12][0-9]|3[0-5])$`
   (lines 222, 229). `schemas/run_lifecycle.schema.v1.json` `manifest_unit_ids` uses
   `^L[0-9]{2,3}$`. Unit identifiers must be derived from the manifest, not fixed by the
   engine. Reconcile the patterns to agree; do not weaken a constraint that a gate relies on.
3. **Domain-specific engine states.** `policy/controller.v1.yaml` `states` includes
   `CIRCUIT`, `EXPERIMENT`, `PLAN_REVIEW_ELECTRONICS`, `QA_ELECTRONICS` — electronics
   vocabulary in an engine-layer contract that `FR-P5-ENGINE-GENERIC` exists to keep neutral.
   Roles must be neutral and domain-declared, with Arduino vocabulary bound under
   `curricula/arduino_kit/`.
4. **Workbook states are undeclared.** `policy/controller.v1.yaml` `full_run.completion_rule`
   describes assembly, page render, page inspection, four workbook reviews, workbook-only
   revision and acceptance in prose; no state list exists. `runtime/workbook.py` implements
   only `assemble()`, which writes `run_status: COMPLETE`.
   `schemas/controller.schema.v1.json` has root `additionalProperties: false`, so any new
   key in the policy requires the matching schema edit in the same change.

The Arduino manifest `curricula/arduino_kit/arduino_kit_curriculum.v5.yaml` declares 35 labs
`L01`–`L35`. `runtime/io.require_internal_output` forces every `--output-root` beneath
`outputs/`, which is gitignored.

## Worktree and generated-output protection

`outputs/` currently holds four run roots — `arduino_kit_run_v1`, `arduino_kit_run_v2`,
`remove-time-limits-v2-acceptance`, `runtime_task_v6`. They are user-owned generated
evidence. Never write into, rename, delete, or point `--output-root` at any of them. Every
run this phase makes uses a fresh root that does not yet exist.

Nine tracked files carry uncommitted user modifications (`.claude/settings.json`,
`curricula/arduino_kit/checks.v1.yaml`, `curricula/arduino_kit/domain.schema.v1.json`,
`curricula/arduino_kit/l04_multimeter_evidence.v1.json`, `policy/checks.v1.yaml`,
`runtime/checks.py`, `runtime/session_bridge.py`, `schemas/lab.schema.v4.json`,
`tests/gates/fr_p5_unit.py`), plus untracked user work. Never stage, stash, reset, restore,
clean, revert, or overwrite any of it.

## Change allowlist

Create only:

- `plans/19_curriculum_factory_production_loop_closure/baseline/worktree_baseline.v1.json`
- `plans/19_curriculum_factory_production_loop_closure/baseline/P0_matrix.v1.json`
- `plans/19_curriculum_factory_production_loop_closure/baseline/P0_matrix.schema.v1.json`
- `plans/19_curriculum_factory_production_loop_closure/baseline/execution_contract_digest.py`
- `plans/19_curriculum_factory_production_loop_closure/baseline/execution_contract_inventory.v1.json`
- `plans/19_curriculum_factory_production_loop_closure/baseline/cli_classification.v1.json`
- `plans/19_curriculum_factory_production_loop_closure/baseline/gate_baseline.v1.json`
- `plans/19_curriculum_factory_production_loop_closure/baseline/stale_authority.v1.md`
- `plans/19_curriculum_factory_production_loop_closure/results/P0.result.v1.md`
- `tests/runtime/test_production_loop_contract.py` (the three failing gap tests plus their
  reason probes)
- `tests/runtime/test_p0_contract_freeze.py` (the deterministic matrix, vocabulary, schema
  and digest assertions)

Modify only, and only to remove a proven active contradiction, with the smallest edit that
removes it: `policy/controller.v1.yaml`, `schemas/controller.schema.v1.json`,
`schemas/curriculum.schema.v5.json`, `schemas/run_lifecycle.schema.v1.json`,
`policy/deferred.v1.yaml`, `policy/checks.v1.yaml`.

`policy/checks.v1.yaml` already carries user hunks. Before touching it, run
`git diff -U0 -- policy/checks.v1.yaml` and confirm your edit is purely additive and does not
overlap any user hunk range. If it would overlap, or if a required reconciliation lands in any
other already-modified file, do not edit: record it in the result file as a blocked
reconciliation and stop under the second stop condition.

`execution_contract_digest.py` is a read-only inventory tool. It hashes and reports. It must
not import `runtime.controller`, `runtime.session_bridge` or `runtime.capability_cycle`, and
must not write anywhere except the path given on its command line.

# TEST

Run `P0-T01` through `P0-T17` in this order. Every check is a command with a deterministic
verdict; record the command, exit code and evidence hash for each.

1. **P0-T01 — Baseline capture, before any mutation.** Write
   `baseline/worktree_baseline.v1.json` containing: `git rev-parse HEAD`; the full
   `git status --porcelain=v1` output verbatim; for every tracked-and-modified and untracked
   path, its SHA-256; and a full recursive `{relative_path: sha256}` manifest of everything
   under `outputs/`, excluding `__pycache__/`, `*.pyc` and `.DS_Store`, never following
   symlinks. Passes when the file exists, parses, and its `outputs/` manifest is non-empty and
   covers all four run roots. This file is the only allowlisted artifact that may be written
   before P0-T02.
2. **P0-T02 — Environment health.** `python3 -m pytest tests/runtime -q --collect-only`
   collects with **zero collection errors**; record the collected count (166 at authoring
   time) and the versions of `python3`, `pytest`, `jsonschema` and `pyyaml`. If collection
   errors exist, no later "fails because production is absent" claim is admissible; fix the
   environment or stop.
3. **P0-T03 — Validate all current manifests and schemas before edits.** For every
   `policy/*.yaml` and `policy/routing/*.yaml` carrying a `schema:` pointer, validate the
   document against the pointed schema with `jsonschema.Draft202012Validator`. Validate
   `curricula/arduino_kit/arduino_kit_curriculum.v5.yaml` through
   `runtime.controller.CurriculumRuntime.validated_manifest` and run
   `run_verifier_fixtures`. All must pass **before** any allowlisted contract edit. Record
   every pointer pair and result.
4. **P0-T04 — Pre-change suite and gate baseline.** Run `python3 -m pytest tests/runtime -q`
   and `./tests/run_gates.sh 5`. Record exact pass/fail counts and, in
   `baseline/gate_baseline.v1.json`, the per-gate-id verdict
   (`PASS`/`FAIL`/`SKIPPED`/`BLOCKED`) for all 38 registered gates plus the
   `tests/results/gate_results.p5.*.json` filename produced. Recording, not passing, is the
   requirement here; a pre-existing failure is baseline, not a P0 defect.
5. **P0-T05 — CLI path classification.** Execute and record exit code, stdout, stderr,
   `terminal_state` and `failure_id` for each of `--preflight`, `--test-static`,
   `--test-live-capabilities`, `--lab-id L01`, `--all`, and
   `--test-simulated-all --output-root outputs/p0_baseline_sim/run` (this root must not exist
   beforehand; create nothing under the four pre-existing run roots). Write
   `baseline/cli_classification.v1.json`. Passes when every observed classification matches
   the ground-truth table in GOAL, or when a divergence is recorded with the file and line
   that produced it.
6. **P0-T06 — Unit-state ownership matrix.** `baseline/P0_matrix.v1.json` validates against
   `baseline/P0_matrix.schema.v1.json` (root `additionalProperties: false`), and a test in
   `tests/runtime/test_p0_contract_freeze.py` asserts: the matrix's unit-state keys equal
   `CurriculumRuntime().states` exactly, in order, with no extra and no missing state; every
   state has exactly one `owner` (a `module:symbol` string), exactly one
   `expected_artifact_or_action`, and exactly one `status` in `{IMPLEMENTED, ABSENT}`; every
   `IMPLEMENTED` owner resolves to a real importable symbol; every `ABSENT` owner names the
   plan phase (`P1`–`P5`) that will own it. No state may carry two owners or zero.
7. **P0-T07 — Workbook-state inventory.** The matrix declares a frozen `workbook_states`
   list, each with the same one-owner / one-artifact-or-action shape, derived from
   `policy/controller.v1.yaml` `full_run.completion_rule` and `runtime/workbook.py`. The test
   asserts `runtime.workbook.assemble` is the sole declared owner of any state whose expected
   action writes `run_status: COMPLETE`. If the state list is added to
   `policy/controller.v1.yaml`, `schemas/controller.schema.v1.json` is updated in the same
   change and the policy still validates (re-run P0-T03).
8. **P0-T08 — Canonical terminal vocabulary.** The matrix declares exactly one unit-terminal
   vocabulary and exactly one run-lifecycle vocabulary, plus the mapping between them. A test
   asserts: every terminal token appearing in `policy/controller.v1.yaml`,
   `policy/failures.v1.yaml`, `schemas/run_lifecycle.schema.v1.json`, `runtime/run_state.py`
   and `runtime/controller.py` belongs to one of the two declared vocabularies; and that no
   detailed failure id (`LIVE-*`, `PRECONDITION-*`, `REPEAT-FAILURE`, `LOG-GATE-FAILED`,
   `FINAL-LOG-AUDIT`, `C1`, `A`/`B` series) is used as a terminal-state value anywhere. The
   failure-id namespace is inventoried separately in the matrix.
9. **P0-T09 — Derived unit identifiers.** A test asserts that no active schema fixes the unit
   count or range: the `sequence.prerequisites` and `sequence.prepares_for` patterns in
   `schemas/curriculum.schema.v5.json` equal the lab `id` pattern in the same file, and
   `manifest_unit_ids` in `schemas/run_lifecycle.schema.v1.json` equals it too. Re-validate the
   Arduino manifest afterwards (P0-T03 command) — all 35 units must still validate.
10. **P0-T10 — Neutral engine roles.** A test asserts every engine-layer state name in
    `policy/controller.v1.yaml` is either in the matrix's frozen neutral vocabulary or is
    declared as a domain role in a `curricula/<name>/` file, and that
    `FR-P5-ENGINE-GENERIC` still reports its P0-T04 verdict or better. Electronics vocabulary
    may live only under `curricula/arduino_kit/`.
11. **P0-T11 — Enforcement claims unchanged and grounded.** A test asserts every
    `enforced_at_runtime` in `policy/controller.v1.yaml` is still `false` with the same
    `deferred:` id it had at P0-T01, every `deferred:` id in `policy/controller.v1.yaml` and
    `policy/checks.v1.yaml` resolves to an id in `policy/deferred.v1.yaml`, and no check
    changed from `MAPPED, NOT EXECUTED` to executed. `RT-9` stays undefined —
    `tests/fixtures/deferred_reference_dangling.reject.yaml` depends on it.
12. **P0-T12 — Digest algorithm and inventory.** `execution_contract_digest.py` covers, at
    minimum: the selected manifest and domain inputs
    (`curricula/arduino_kit/{arduino_kit_curriculum.v5.yaml, manifest.domain.schema.v1.json,
    domain.schema.v1.json, checks.v1.yaml, kit_calibration.v1.yaml, circuit_library.v1.yaml,
    verify_domain.py}`), `meta_prompt/curriculum.prompt.v1.md` and the three companions in
    `meta_prompt/assets/`, all `policy/*.yaml` and `policy/routing/*.yaml`, all active
    `schemas/*.json` (excluding `schemas/deprecated/`), all `runtime/*.py`, the resolved path
    + version + SHA-256 of each external tool (`codex`, `pandoc`, `pdftoppm`, `pdfunite`,
    `gemini`, `node`) or an explicit `null` when absent, and each entry of
    `policy/routes.v1.yaml` with its `status`. The digest is SHA-256 over
    `json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`
    where `payload` maps repo-relative POSIX paths to file SHA-256; `__pycache__/`, `*.pyc`
    and `.DS_Store` are excluded; symlinks are never followed. Tests assert: two consecutive
    runs produce byte-identical output; the digest recorded in
    `baseline/execution_contract_inventory.v1.json` recomputes exactly; flipping one byte of
    any covered input in a temporary copy changes the digest; and the script writes nothing
    outside its output argument.
13. **P0-T13 — The three gaps fail, reproducibly.** `tests/runtime/test_production_loop_contract.py`
    contains exactly three tests asserting production behavior that does not exist —
    (a) `--lab-id L01` dispatches a live single-unit production path and writes a
    schema-valid `run_state.json` plus that unit's acceptance record with a truthful terminal
    state, (b) `--all` dispatches units in manifest-derived order with no manual invocation
    between them and records each dispatch in the run lifecycle, (c)
    `--test-live-capabilities` executes real bounded route probes and returns a structured
    PASS record. Each must assert an observable dispatch/lifecycle fact that the owning phase
    (P3, P4, P1) can satisfy with a bounded fixture or injected executor — never a test that
    can only pass by generating all 35 Arduino units. Add one reason probe per gap asserting
    the exact current refusal
    (`LIVE-GENERATION-NOT-PREFLIGHTED`, `LIVE-GENERATION-NOT-PREFLIGHTED`,
    `LIVE-CAPABILITY-CYCLE-REQUIRED`) at exit code 2.
    `python3 -m pytest tests/runtime/test_production_loop_contract.py -q` must report
    **exactly 3 failed, 3 passed, 0 errors**. Zero errors is what distinguishes "production is
    absent" from "the fixture or import is broken". No `xfail`, `skip`, `pytest.raises`
    wrapper or try/except may convert a gap test into a pass.
14. **P0-T14 — Nothing else regressed.**
    `python3 -m pytest tests/runtime -q --ignore=tests/runtime/test_production_loop_contract.py`
    reports the same passed count and the same failures as P0-T04, with zero errors.
15. **P0-T15 — Gates no worse than baseline.** Re-run `./tests/run_gates.sh 5` and compare
    per gate id against `baseline/gate_baseline.v1.json`. Accept no new or worsened verdict.
16. **P0-T16 — Preservation audit.** Re-run the P0-T01 capture into a scratch file under the
    system temp directory, never inside the repository, and diff: every path in the P0-T01
    `outputs/` manifest still exists and is byte-identical, no path under the four
    pre-existing run roots was added or removed, and any new `outputs/` path lives under
    `outputs/p0_baseline_sim/`; every pre-existing modified and untracked path's SHA-256 is
    unchanged except for files on the modify allowlist; and
    `git status --porcelain=v1` differs from baseline only by the allowlisted create/modify
    paths. `git stash list` and `git rev-parse HEAD` are unchanged.
17. **P0-T17 — Stale-authority list is bounded and reproducible.** Every entry in
    `baseline/stale_authority.v1.md` names a document path, quotes the exact stale claim,
    names the executable behavior that contradicts it, and gives the command that reproduces
    the contradiction. A test asserts every cited document path exists and the file contains
    zero entries whose contradiction has no recorded command. Aspirational, stylistic or
    "should eventually" entries are not admissible.

# LOOP

Run P0-T01 first and never mutate anything before it is written. Then run each check in
order. On failure: record the check id, the exact command, exit code, evidence hashes and the
narrow root cause; revise **only** the one in-scope artifact responsible; immediately re-run
**P0-T16** to prove the revision touched nothing user-owned; then re-run the failed check and
every later check whose evidence could have changed. A contract edit always re-runs P0-T03,
P0-T14 and P0-T15.

Never respond to a failure by: implementing production behavior; flipping an
`enforced_at_runtime` flag; marking a deferred obligation discharged; relaxing a schema
constraint to make a gate pass; deleting, skipping or `xfail`-ing a test or fixture;
converting a gap test into a passing test; editing anything under `outputs/`; or staging,
stashing, resetting, restoring or cleaning the worktree.

Stop, without claiming success, when:

- Active contracts cannot be reconciled to neutral roles, derived unit identifiers, and one
  owner per transition or terminal decision — for example a controller state with no
  possible single owner, or two files that both claim authority over the same terminal
  decision with no non-arbitrary resolution.
- The baseline cannot be reproduced without modifying user-owned work — including a required
  reconciliation that overlaps a user hunk in an already-modified file, or a run that cannot
  be executed without writing into an existing `outputs/` run root.
- Any check cannot be made deterministic, or P0-T02 keeps reporting collection errors.

On a stop, still write the result file, state which check stopped the phase, what would be
required to proceed, and make no further mutation.

The phase is done only when P0-T01 through P0-T17 all hold **with the three gap tests still
failing**, and
`plans/19_curriculum_factory_production_loop_closure/results/P0.result.v1.md` exists containing:
the captured baseline (HEAD, `git status`, `outputs/` manifest hash); the full unit-state,
workbook-state, route, check, artifact and deferred-obligation matrix with its one-owner
column; the canonical digest algorithm statement and the computed execution-contract digest;
the recorded CLI classification table; the pre-change and post-change per-gate comparison; the
verbatim failing output of the three gap tests with their commands and exit codes; the
stale-authority list; every contract edit made with its before/after and the contradiction it
removed; every reconciliation deliberately not made and why; and the final verdict. Claim
completion only when the recorded delta matches the change allowlist exactly.
