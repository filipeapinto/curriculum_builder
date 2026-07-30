# Plan: make the curriculum creator executable unattended, and reusable for a second curriculum — v3

Supersedes `remediation.plan.v2.md` (PLAN INSUFFICIENT) and `v1` (PLAN INSUFFICIENT).
Both failed on the same blocker: reviewer isolation was a convention, not a capability.
v3 replaces it with an OS-enforced boundary established by execution. Every other change
below is traceable to a specific v2 defect Codex identified.

## 1. Goal — WHY

Take `curriculum_creator` to a state where `prompts/meta_curriculum_prompt.prompt.v5.md`
can be started by a human and left alone until it reaches a terminal state, and where a
second curriculum in a different domain reuses the machinery without editing it.

## 2. The isolation mechanism — capability, not convention

This is the section both prior plans got wrong, so it comes first.

**Established by execution, 2026-07-29:**

| Test | Result |
|---|---|
| Worker with `-C <own dir>` **and** `-s read-only`, asked to read a sibling's verdict by absolute path | **Read it. 0 ms.** Working directory is not a boundary. |
| Worker with `-s read-only`, asked to write inside its root and to `/tmp` | **`BLOCKED`. Neither file appeared.** Write capability is genuinely removed. |

So reads cannot be restricted, but **writes can be removed entirely**. Isolation therefore
comes from ensuring there is nothing to read:

1. Every reviewer runs under `-s read-only`. It cannot create a verdict file, a signal
   file, a temp artifact, or anything else, anywhere — proven above, not asserted.
2. Verdicts return on **stdout only**, captured by the controller process.
3. The controller holds all four verdicts of a pass in memory and persists **nothing**
   until every reviewer in that pass has returned.
4. **During a pass the action log records only `sha256(verdict)`, never verdict content.**
   This closes the hole Codex found in v2: the log's `result`/`notes` fields would
   otherwise disclose reviewer A's finding to reviewer B, defeating the barrier through
   the audit trail itself. Content is written after the barrier; the hash proves the
   post-barrier content is the same verdict that was returned.
5. A **retry is a fresh sealed pass.** No prior-attempt verdict, checkpoint, or stdout
   capture is on disk while a retry runs.
6. **Resume** may not restart mid-pass. If a run is interrupted during a review pass, the
   whole pass re-runs; partial verdicts are discarded, never persisted for reuse.
7. Passes are **sequential, not parallel**. Plan verdicts are persisted only after
   `PLAN_DECISION`; a QA reviewer therefore sees them as authorized prior artifacts, which
   is intended, and never sees a sibling's QA verdict, which is not.

**Proven by an adversarial worker**, not by a watcher: `tools/check_isolation.py` runs a
real pass in which one reviewer is deliberately instructed to write its verdict to disk,
to `/tmp`, and to any reachable path, and to read any sibling verdict it can find. The
test fails if any write succeeds, if any verdict content appears in the log before the
barrier, or if the malicious reviewer obtains a sibling's verdict.

**If `-s read-only` proves insufficient** — for example if a worker route needs write
access for an unrelated reason — the fallback is a container or a second OS user, decided
**before** implementation, not after. That is a new dependency and is escalated (§8).

## 3. Success criteria — WHY

v2's criteria failed twice over: criterion 1 exited 0 on the defective tree (so its pass/
fail contract was inverted), and criteria 2–9 failed only because `tools/` did not exist —
the right answer for the wrong reason. v3 states an **expected exit code** for each, and
Step 1 requires each validator to fail *by detecting its defect*, evidenced by its
diagnostic output, not by being absent.

All commands run from `curriculum_creator/`.

| # | Command | Now | Done | Detects |
|---|---|---|---|---|
| 1 | `rg -F -q '3[0-5]' schema/` | exit 0 | **exit 1** | hardcoded lab-count regexes |
| 2 | `python3 tools/check_inputs_have_schemas.py` | exit 1 + names each unvalidated input | exit 0 | an input the prompt requires but no validator covers |
| 3 | `python3 tools/check_external_paths.py` | exit 1 + names `curriculum.v4.yaml:19` and both L01 files | exit 0 | outside references not on the `declared_external_reads` allowlist |
| 4 | `python3 -m pytest tests/test_log_pairing.py -q` | exit ≠0 | exit 0 | 6 pairing failures, against the **production** pairing function, imported not reimplemented |
| 5 | `python3 tools/check_isolation.py` | exit 1 | exit 0 | adversarial reviewer writes, reads a sibling, or leaks through the log |
| 6 | `python3 tools/check_checks_executed.py` | exit 1 | exit 0 | a check id with no executing test, or a test that passes vacuously |
| 7 | `python3 tools/check_domain_dispatch.py` | exit 1 | exit 0 | a full lab failing either layer, or an unregistered `domain_id` being accepted |
| 8 | `python3 tools/check_runtime_authority.py` | exit 1 — the prompt still names `controller.v1.yaml` and `lab.schema.v3.json` | exit 0 | **any** reference to a retired runtime artifact, repository-wide |
| 9 | `python3 tools/check_one_authority.py` | exit 1 — supplies defined in calibration **and** the manifest | exit 0 | two files claiming the same fact, against a declared fact catalog |

Criterion 8 is new. Codex showed a defect that survived all nine of v2's criteria: the
prompt could keep pointing at the retired controller and lab schema while every
documentation check passed. This closes it.

Codex's GREEN LIGHT is not a criterion. It is the exit condition of Step 8.

## 4. Context & assumptions — WHY

**Established by execution**

| Fact | Evidence |
|---|---|
| `-C` does not contain a worker | sibling verdict read by absolute path, 0 ms |
| `-s read-only` removes write capability | `BLOCKED`; no file created inside root or in `/tmp` |
| `codex exec` needs `--skip-git-repo-check` | `ROOT` is not a git repo |
| `codex exec` needs `< /dev/null` | otherwise blocks on stdin forever at 0.02s CPU, appearing alive |
| Only typst renders PDF; only `pdftoppm` rasterizes | no TeX engine, no importable Python PDF library |
| ImageGen has no proven invocation | never established |
| `uniqueItems` cannot enforce unique object ids | two objects differing elsewhere but sharing an `id` both validate |
| JSON Schema cannot compare `[min, max]` | no cross-element comparison in draft 2020-12 |

The last two were v2's proposed fixes for the duplicate-id and inverted-range concerns.
Both were wrong; in v3 they are code checks inside `tools/check_one_authority.py` and
`tools/check_calibration_semantics.py`.

**Assumptions**
- Architecture is sound. Four reviews, forty-plus findings, none saying the design is wrong.
- Learner age band 9+; pedagogy caps derive from it.

## 5. Steps — HOW

### Step 1: Build the validators, prove each detects its defect
- **Does:** Writes the nine `tools/` scripts and `tests/test_log_pairing.py`. Each must fail
  against the current tree **and print the specific defect it found**. A validator failing
  because a file is missing is not evidence — that was v2's error.
- **Produces:** `tools/`, `tests/`, and `plans/baseline.v3.md` recording each validator's
  exit code and diagnostic output against the current tree.
- **Owner:** this session. **Parallel?** yes.

### Step 2: Two decisions — **BLOCKS EVERYTHING DOWNSTREAM**
- **2a — Supply authority.** Three files define supplies: `calibration.power`,
  `curriculum.kit_power_profile`, and the proposed domain profile. Choose one; delete the
  others' claim; update calibration's schema to match. *Recommendation: the domain profile.*
- **2b — Controller boundary.** v2 left this dangling: Step 7 referenced an engine option
  Step 2 no longer contained. Decide now — (i) author a full transition/guard/retry contract
  in YAML, or (ii) write the engine in Python with an independently specified public
  behavioural contract, `engine/` declared in the prompt's input inventory with a hash and
  compatibility rule. *Recommendation: (ii).*
- **Owner:** user, then this session.

### Step 3: Mechanical corrections
Two lab-id regexes; repoint all three external kit-photo references; 8→12 reviewers in
`how_it_works.md` and `infographic.prompt.v1.md`; refresh `readme.md`; canonical naming
convention verified repository-wide. Duplicate ids and range ordering move to code checks,
not schema constraints.
- **Verified by:** 1, 3, 8.

### Step 4: Implement isolation per §2
Reviewers under `-s read-only`; stdout-only capture; in-memory barrier; hash-only logging
during a pass; retry as fresh sealed pass; resume forbidden mid-pass; sequential passes.
- **Verified by:** 5. **Depends on:** Step 2b.

### Step 5: Domain split with real dispatch
`lab.core.schema.v1.json` + `schema/domain/electronics.schema.v1.json` +
`schema/domain/registry.v1.json` mapping `domain_id` → schema + version. Seven visual roles
required, with a waiver schema and negative tests.
- **Verified by:** 7. **Depends on:** Step 2a.

### Step 6: Schemas, and the rules schemas cannot express
Schemas for `limits`, `routes`, `checks`, `failures`, `pipeline`. In code: fixture
existence, `UNPROVEN` route not cited by a gate, declared supply id present and
`verified_official` in the selected domain profile, `unclosed_starts` computed, duplicate
ids, range ordering. The log-pairing function is written **once** and imported by both the
controller and the test — v2's version let the test verify a different implementation.
- **Verified by:** 2, 4, 6, 9.

### Step 7: Migrate the runtime contract completely, then retire
Prompt, `checks.v1.yaml`, precedence list, release gates and documentation updated in one
pass; `controller.v1.yaml` and `lab.schema.v3.json` deleted, not merely superseded. Also:
bootstrap log root, ordering, persistence and resume semantics; a named deterministic
model-selection algorithm covering availability, substitution and ties, with a test;
imagegen proven by a real preflight or removed with the visual contract revised; PDF
acceptance given a defined pixel metric with fixtures and a test command; the pipeline
encoding four PDF-review invocations.
- **Verified by:** 6, 8.

### Step 8: Re-review
Submit to Codex; verify each finding independently before accepting it.

## 6. Artifacts — HOW

```text
curriculum_creator/
  tools/check_{inputs_have_schemas,external_paths,isolation,checks_executed,
               domain_dispatch,runtime_authority,one_authority,calibration_semantics}.py
  tests/test_log_pairing.py
  plans/baseline.v3.md                     validator baseline with diagnostics
  schema/lab.core.schema.v1.json
  schema/domain/{registry,electronics}.v1.json
  schema/{limits,routes,checks,failures,pipeline}.schema.v1.json
  assets/domain/electronics.v1.yaml        sole supply authority
  engine/                                  if Step 2b = (ii); declared with hash
  RETIRED: assets/controller.v1.yaml, schema/lab.schema.v3.json
```

## 7. Verification — HOW

The nine commands in §3, run from `curriculum_creator/`, with the stated exit codes.

Three disciplines, each from a specific past failure:

- **A validator must fail by detecting, not by being absent.** v2's criteria 2–9 exited on
  missing files.
- **Exit codes are stated explicitly.** v2's criterion 1 exited 0 on the broken tree.
- **Tests import the production implementation.** A test that reimplements the rule proves
  only that the test agrees with itself.

## 8. Risks and escalation — HOW

| Risk | Mitigation |
|---|---|
| A validator passes on a defect | Step 1 baseline requires the diagnostic, not just the exit code |
| Validators become a second unverified layer | each gets adversarial fixtures and a mutation test; production imports the same function |
| Isolation leaks through a channel not tested | the adversarial reviewer actively attempts write, read and log-leak |
| `-s read-only` insufficient for some worker | escalate before implementing; container or second OS user is a dependency decision |
| Partial fix reported complete | demonstrated repeatedly; every criterion is a command with a stated exit code, run and shown |

**Escalate when:** Step 2a or 2b is undecided; `-s read-only` cannot serve a required
worker; imagegen cannot be proven and the visual matrix must change; a finding contradicts
a decision recorded here on purpose, such as the calibration/prose divergence.

## 9. Traceability

v2 claimed to address "five findings" when Codex's v1 review contained six. All six are
carried here: calibration/power contradiction (2a), incomplete runtime migration (7),
cross-artifact rules wrongly assigned to JSON Schema (6), false lab-regex criterion (3, §3),
core/domain theatre and undeclared engine (5, 2b), insufficient success criteria (§3).
