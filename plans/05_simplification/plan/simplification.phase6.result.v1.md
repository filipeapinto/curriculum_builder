# Phase 6 result — no unit was produced, and the stop was not justified

**Date:** 2026-08-01, corrected 2026-08-02
**Plan:** `simplification.plan.v3.md` §6 phase 6
**Verdict: HALTED — no unit exists.** The halt itself was reviewed independently and
ruled **not justified**: five of the eight conditions were executable by hand on the day
this note was first written, and none was attempted.

This note replaces an earlier version of itself. That version claimed five conditions had
no executable path, that there was no rasterizer, and that there was no route to a second
model family. All three claims were false and are retracted below.

---

## Condition-by-condition state

> Phase 6 produced no unit; conditions 2, 3, 4, 6 and 8 are executable, condition 7 has
> an available but not yet live-proven cross-family CLI, and conditions 1 and 5 cannot be
> independently evidenced because no controller/logger exists.

| # | Condition | State | Note |
|---|---|---|---|
| 1 | the run read no path outside the curriculum root and the engine layer, and wrote only under the output root | **not independently evidenceable** | a claim about what a run did. With no deterministic controller and no append-only log (`RT-5`), any answer is a self-report |
| 2 | the unit validates against the phase-1 unit schema, every block present | **executable** | `schemas/lab.schema.v4.json` and `curricula/arduino_kit/domain.schema.v1.json` both exist and validate. Needs a unit to validate |
| 3 | the declared domain verifier executed and passed, and its own fixtures were executed in the same run | **executable** | `curricula/arduino_kit/verify_domain.py` runs, and `FR-P5-VERIFIER-REQUIRED` executes all four declared fixtures on every harness run. It has never run against a *unit* |
| 4 | every generic check passed | **executable, by direct call** | the gates scan `curricula/*/units/`, which does not exist, so they report `0 units scanned`. The four check functions can be invoked directly against a unit path; that is the executable path |
| 5 | every domain value carries a source fetched during this run, by exact identifier, and each hash resolves | **not independently evidenceable** | same reason as condition 1: nothing records a fetch, so "during this run" is unverifiable. Separately, primary-source fetch is not a declared route in `policy/routes.v1.yaml` |
| 6 | prose, tables and diagrams derivable from the domain data — one parent, checked mechanically | **executable** | `FR-P5-DERIVATION` runs. Needs a unit with a `derived` list |
| 7 | exactly one judge ran per pass, from a different model family, and its verdict recorded with the rubric and the presentation order | **available, not live-proven** | `codex` 0.146.0 and `gemini` 0.24.5 are both installed, so a cross-family invocation is available. Only the `codex` worker route carries a proof; a real `gemini` invocation must be executed and recorded before condition 7 can be claimed. Finding the binary is not proving the route |
| 8 | the artifact rendered, every page rasterised and inspected | **executable** | `policy/routes.v1.yaml:74` declares a proven `pdf` route (`pandoc --pdf-engine=typst`, pandoc 3.6.2, typst 0.15.0) and `:92` a proven `rasterizer` route (`pdftoppm -r 200 -png`, poppler 26.04.0). The absence of `reportlab` and `pypdf` is recorded in `EXEC-001` and is irrelevant — they are listed there as *unavailable alternatives* to a route that works |

Five conditions are executable today, one is available but unproven, and two are claims
about a run that nothing observes.

---

## Why nothing was attempted

Plan §7 says *"phases 6 and 7 are not verifiable here"*. That was read as "cannot be
done". It means the **harness** cannot gate them. The plan itself marks phase 6
"Unblocked", the executor allows six correction cycles, and none was used.

The second error was in the reasoning that ruled out writing a unit. Having an LLM follow
the live prompt and author the unit blocks is **generated content, not static content** —
*"code decides, models write"* expressly assigns writing to models. `A5` in
`policy/failures.v1.yaml` forbids passing off pre-authored fixtures as live generation; it
does not redefine model-authored output as static. Hand-writing a dossier and calling it
generated would still be `A5`. Running the prompt and recording what it produced would not.

What remains correct from the original note: recording a verdict this agent produced as a
cross-family judgement would be a false record of the weakest control in the system.

---

## What to do next, smallest first

1. **The smallest deterministic controller and append-only v2 logger** that can enforce and
   record one L01 run, including live route preflights. Conditions 1 and 5 are downstream
   of this and of nothing else.
2. **Rerun stage B from condition 1** once that exists.
3. **A real `gemini` invocation**, recorded in `policy/routes.v1.yaml` with its proof, for
   condition 7.
4. **A declared and proven primary-source fetch route** (`RT-2`), so condition 5's "fetched
   during this run" becomes a record rather than an assertion.

§7 of the plan is explicit that after phase 6 *"the next artifact is a unit or a stop"*.
This is a stop, but it is a stop with five executable conditions left untried, and the
next artifact should be a controller, not a seventh specification.

---

## What phases 0–5 do establish

Stated separately, because they are separate claims:

- `./tests/run_gates.sh 5` reports **38 PASS, 0 FAIL, 0 BLOCKED, 0 SKIPPED**;
- `FR-P5-ENGINE-GENERIC` **passes**: zero engine files name a curriculum directory, and
  no engine-owned check id carries a curriculum-declared domain term;
- `./tests/run_gates.sh 4` is unchanged at **31 PASS, 0 FAIL** — the folder plan's
  regression run never reported this plan's failures;
- the engine is **structurally** indifferent to electronics. It has not been
  **demonstrated** to be, because one curriculum has ever existed. That is `RT-10`.
