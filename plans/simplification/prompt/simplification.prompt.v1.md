# Execute the simplification plan v2

## Goal

Implement `../plan/simplification.plan.v2.md` phases 0–6, so that two things hold at
once:

1. **The engine is generic.** No engine file names a curriculum directory, no engine
   check id encodes a domain term, and the unit contract carries a `domain` block whose
   shape the curriculum supplies. G1–G6 resolved.
2. **The prompt works.** One prompt — `meta_prompt/curriculum.prompt.v1.md`, written by
   phase 5 — generates **L01 of `curricula/arduino_kit/`**, and that unit passes every
   check the engine and the curriculum declare.

Finish only when every harness gate active at the current phase passes, no gate is
`BLOCKED`, every `.reject.` fixture fails for its declared reason, every `.accept.`
fixture validates, the L01 test passes, every review approves, results are recorded, and
the worktree is clean. Preserve unrelated changes. Never weaken a requirement and never
report an unexecuted check as passing.

**Required arguments, no defaults.** The plan's §4 raises two decisions this run may not
make for itself:

```text
--circuit-mode      composed | created-gated      required
--signoff           <named person, or "none">     required
```

Refuse to start if either is absent, exactly as the meta prompt refuses to guess
`--output-root`. A default here would silently choose the product, and one of the two
available values is the option no evidence supports.

**Three verdicts, never interchanged.** **`BLOCKED`** is a gate-level outcome — a gate
whose dependency failed or was itself blocked, propagating transitively. **`HALTED`** is
the run-level verdict when a phase cannot be approved, whatever the cause.
**`APPROVED`** requires §Finish below.

## Agents

- **Coordinator:** assigns work, enforces phase order, owns commits, and owns the
  iteration budget.
- **Implementer:** makes the current phase's changes.
- **Validator:** independently runs the harness and the L01 test, and verifies the result
  record.
- **Reviewer:** independently checks the diff against the plan.
- **Judge** (phase 6 only): reviews the generated unit. **Must be a different model
  family than the one that generated it** — self-preference bias is measured at −38% to
  +90% and survives hiding authorship. One judge per pass, not a panel: nine cross-family
  judges measure at 2.18 effective votes.

Only the coordinator changes Git history. Keep implementation, validation, and review
separate.

## Loop — stage A, phases 0–5

Read `AGENTS.md`, the complete v2 plan, and `../research/conclusions.v1.md`. For each
phase `N` in 0, 4, 1, 2, 3, 5 — **that order**, because phase 4's checks are the only
part provable before anything runs, and the plan sequences them first for that reason:

1. The implementer completes phase `N`.
2. The reviewer returns `APPROVE` or actionable findings.
3. Fix findings and repeat review until approved.
4. The coordinator creates the phase's **candidate commit**. Gates run against a commit,
   never a dirty tree.
5. The validator runs `./tests/run_gates.sh <phase>` and inspects the new JSON result.
6. Validation passes only when the harness root ran first and passed, all gates with
   `activation_phase <= N` pass, **no gate is `BLOCKED`**, every later gate is recorded
   `SKIPPED`, every `.reject.` fixture fails for its declared reason, every `.accept.`
   fixture validates, results are written, and the worktree is clean.
7. On failure, the implementer fixes the cause, the reviewer rechecks, the coordinator
   **amends** the unshared candidate commit, and validation repeats from 5.
8. Advance only after review returns `APPROVE` and validation returns `PASS`.

## Loop — stage B, phase 6, the L01 test

This is the test that decides whether the prompt works. Run
`meta_prompt/curriculum.prompt.v1.md` against `curricula/arduino_kit/`, unit `L01`.

Iterate until every condition holds:

| # | Condition |
|---|---|
| 1 | the run **read no path outside** the curriculum root and the engine layer, and wrote only under the output root |
| 2 | the unit validates against the phase-1 unit schema, every block present |
| 3 | the curriculum's declared **domain verifier executed** and passed, and its own fixtures were executed in the same run |
| 4 | every generic check passed: schema, readability band, Bloom verbs against declared level, cross-document derivation, receipt hash resolves in the shipped artifact |
| 5 | every domain value carries a source **fetched during this run**, by exact identifier, and each hash resolves |
| 6 | prose, tables and diagrams are derivable from the domain data — one parent, checked mechanically, not asserted |
| 7 | exactly one judge ran per pass, from a different model family, and its verdict is recorded with the rubric and the presentation order |
| 8 | the artifact rendered, every page rasterised and inspected |
| 9 | a person read the unit and recorded that they did |
| 10 | under `--signoff <name>`, that person's sign-off is recorded before the unit is marked usable; under `--signoff none`, the unit is marked **not for use with a child** |

On any failure: the implementer fixes **the named cause only** — the prompt, a check, a
schema, or the curriculum's verifier — never the acceptance criteria. Re-run from
condition 1. The whole test re-runs; a repaired condition is not spot-checked in
isolation.

## Iteration budget and the stall rule

The coordinator owns both.

- **Six correction cycles per phase.** Exceeding it is `HALTED`, not a seventh cycle.
- **Every cycle must narrow the failing set.** If the identical failing set recurs twice,
  stop as `HALTED` and report the set. Repeating a fix that did not work is the loop this
  project has already run six times at the meta level.
- **Two cycles that add artifacts without reducing failures** is `HALTED`. Complexity
  that does not buy a pass is drift.
- Record every cycle: what failed, what changed, what the next run measured.

## Standing constraints

- **Do not confuse the prompt you are writing with the prompt you are executing.** This
  file is the executor. `meta_prompt/curriculum.prompt.v1.md` is the deliverable. Editing
  this file to make the deliverable pass is the failure this project is named after.
- **L01 cannot prove the domain verifier, and the report must say so.** L01 is
  `safe-power`: unpowered, polarity-neutral, and forbidden from labelling a connector
  terminal. Current limiting, polarity and supply match — the ERC rules that matter — are
  **not exercised by it**. Passing the L01 test proves the pipeline end to end. It does
  not prove electronics is safe to generate. Report those as two separate claims, and
  never let the first be read as the second. That is failure A5.
- **Extraction precedes retirement.** Phase 5 writes the prompt before anything under
  `meta_prompt/` moves to `deprecated/`. Six rules exist nowhere else — precedence
  (`inputs.v1.md:63-89`), the recorded divergences (`:96-100`), no hardcoded count
  (`:102-104`), one parent (`architecture.v1.md:44-50`), grounding (`:52-57`), and no
  model for deterministic work (`routing.v1.md:23-25`). Retiring first destroys them.
- **A missing verifier is a refusal, not a warning.** A curriculum with no declared,
  executable, fixture-proven domain verifier does not run. This is the plan's §3 and it
  is the whole reason the engine can be generic without being unsafe.
- **The engine never learns the domain.** If a fix requires the word "circuit",
  "datasheet", "kit" or "voltage" in `policy/`, `schemas/` or the prompt, the fix is in
  the wrong layer. Put it in `curricula/arduino_kit/`.
- **Fixing a check versus weakening it.** A check's implementation may be corrected when
  it misreads its subject — wrong scan root, bad regex, misparsed path. Record it as
  `gate_impl_fix` with a one-line reason and have the reviewer re-check it. A check's
  **acceptance criteria** may never be relaxed to make a failing repository pass. If the
  repository is what is wrong, fix the repository or return `HALTED`.
- **Never report a static or simulated pass as generated coverage.** "The engine handles
  any curriculum" and "a curriculum exists" are different claims.
- **`TEXT-BLOOM-VERBS` flags and never blocks.** Human raters agree with each other on
  Bloom level only 46.58% of the time.
- **Scope is phases 0–6.** Phase 7 — a second curriculum in an unrelated domain — is the
  plan's actual proof of genericity and is **not** in this run. Until it runs, report
  genericity as *structurally enforced, not demonstrated*.
- **Anything in the plan's §8 is out of scope.** Surface it under its `RT-` id; do not act
  on it.

## Finish

Return `APPROVED` only when: stage A passes at every phase; the L01 test passes all ten
conditions; both required arguments were supplied and are recorded with the run; the six
extracted rules resolve from outside `meta_prompt/`; and the report states, separately
and in these terms, (a) that the pipeline produced one unit, (b) that L01 did not
exercise the powered-circuit path, and (c) that genericity is structurally enforced and
not yet demonstrated.

Otherwise return `HALTED`, naming the failing gate id or test condition and its stated
failure meaning — and, where the cause is external or needs a decision, the exact blocker
or decision required.
