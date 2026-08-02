# Phase 6 result — the L01 test could not be run, and why

**Date:** 2026-08-01
**Plan:** `simplification.plan.v3.md` §6 phase 6
**Verdict: HALTED.** Five of the eight conditions have no executable path in this
repository. No unit was produced.

Plan phases 0–5 are complete and validated. This note is about the one that is not, and
it is written in the form the plan asks for rather than as an apology: what is blocked,
by what exactly, and what would unblock it.

---

## The blocker under all of it

**Nothing in this repository executes the prompt.** There is no controller, no runner
and no entry point that reads `meta_prompt/curriculum.prompt.v1.md`, resolves a
curriculum, and produces a unit. `plans/legacy_v3/run_curriculum.v3.py` is the *failed*
v3 generator, retained as cited evidence and targeting a directory layout that no longer
exists; AGENTS.md states it is not the local build entry point.

This is not a discovery. `simplification.plan.v3.md` §7 states it — *"Phases 6 and 7 are
not verifiable here — nothing in this repository executes a model, renders a PDF or
fetches a source"* — and `RT-7` in `policy/deferred.v1.yaml` records it as an obligation
with a stated acceptance criterion. What this note adds is that it was checked rather
than assumed, condition by condition.

---

## The eight conditions

| # | Condition | State | Blocker |
|---|---|---|---|
| 1 | the run read no path outside the curriculum root and the engine layer, and wrote only under the output root | **blocked** | presupposes a run. There is no execution log to record reads against, because the logger is `RT-5` |
| 2 | the unit validates against the phase-1 unit schema, every block present | **executable, unexercised** | `schemas/lab.schema.v4.json` and the curriculum's `domain.schema.v1.json` both exist and validate. There is no unit to validate |
| 3 | the declared domain verifier executed and passed, and its own fixtures were executed in the same run | **executable, half-exercised** | `curricula/arduino_kit/verify_domain.py` runs, and `FR-P5-VERIFIER-REQUIRED` executes all four declared fixtures on every harness run. It has never run against a *unit*, because there is none |
| 4 | every generic check passed | **executable, unexercised** | all four run and all four report `0 units scanned`. That is `RT-7` |
| 5 | every domain value carries a source fetched during this run, by exact identifier, and each hash resolves | **blocked** | the network is reachable, and the primary-source capability is not a declared route. `policy/routes.v1.yaml` declares four and none is this one — the prompt records that divergence in its own §Inputs. Nothing records a fetch, so "fetched during this run" is not a checkable claim |
| 6 | prose, tables and diagrams derivable from the domain data — one parent, checked mechanically | **executable, unexercised** | `FR-P5-DERIVATION` runs. There is no unit with a `derived` list |
| 7 | exactly one judge ran per pass, from a different model family, and its verdict recorded with the rubric and the presentation order | **blocked** | there is no route to a second model family. `EXEC-002` in `policy/failures.v1.yaml` records the worker route exiting 1 under sandbox denial, and `ROUTE-PROVEN` is deferred under `RT-2`. A single agent cannot satisfy a cross-family requirement by asserting it did |
| 8 | the artifact rendered, every page rasterised and inspected | **blocked** | `typst` is present and renders `docs/how_it_works.typ`; there is no unit renderer and no rasterizer. `reportlab`, `pypdf` and a raster backend are all absent, which `EXEC-001` already records |

Three conditions are blocked on capability, two on there being no run at all, and three
would run the moment a unit existed.

---

## What was deliberately not done

**No unit was hand-written.** Writing an L01 dossier by hand, running the verifier and
the four generic checks over it, and reporting "six of eight conditions hold" was
available and was refused. It would be static coverage described as generated coverage,
which is failure **A5** in `policy/failures.v1.yaml` and is the failure this whole plan
is named after. The distinction the executing prompt draws is the one that matters here:
*"the engine handles any curriculum" and "a curriculum exists" are different claims*.

The same reasoning rules out a simulated judge. Recording a verdict this agent produced
as a cross-family judgement would be a false record of the one control the research
identifies as the weakest link.

---

## What would unblock it, smallest first

1. **A controller.** The single largest gap, and the only one that is pure code. Every
   other blocker is downstream of there being no run.
2. **A logger** (`RT-5`), because conditions 1 and 5 are claims about what a run did, and
   an unlogged run cannot make them.
3. **A proven primary-source route** (`RT-2`), so condition 5's "fetched during this run"
   becomes a record rather than an assertion.
4. **A proven second-family worker route** (`RT-2`, `EXEC-002`), for condition 7.
5. **A renderer and a rasterizer** (`EXEC-001`), for condition 8.

None of these is a specification. §7 of the plan is explicit that after phase 6 *"the
next artifact is a unit or a stop"*, and this is the stop, recorded so the next person
does not begin by writing a seventh specification.

---

## What phases 0–5 do establish

Stated separately from the above, because they are separate claims:

- `./tests/run_gates.sh 5` reports **38 PASS, 0 FAIL, 0 BLOCKED, 0 SKIPPED**;
- `FR-P5-ENGINE-GENERIC` **passes**: zero engine files name a curriculum directory, and
  no engine-owned check id carries a curriculum-declared domain term;
- `./tests/run_gates.sh 4` is unchanged at **31 PASS, 0 FAIL** — the folder plan's
  regression run never reported this plan's failures;
- the engine is **structurally** indifferent to electronics. It has not been
  **demonstrated** to be, because one curriculum has ever existed. That is `RT-10`.
