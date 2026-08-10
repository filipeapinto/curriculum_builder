# Phase 5 result — extraction before retirement, rule by rule

**Date:** 2026-08-01
**Plan:** `simplification.plan.v3.md` §6 phase 5
**Verdict: the six rules resolve outside every file that was retired.**

§6 phase 5 fixes the order — write the prompt, *then* retire the meta level — because
six rules existed nowhere else and retiring first would have destroyed them. This is the
record that each one was carried, and where to. It is written as a resolution rather
than as an assurance: each row names the file and heading the rule now lives under, so a
reader can check the claim instead of accepting it.

Every source below is now under `meta_prompt/deprecated/` and nothing may read it.

| # | Rule | Was | Is |
|---|---|---|---|
| 1 | **Precedence** — the ranked order that settles a disagreement, without averaging | `inputs.v1.md:63-89` | `curriculum.prompt.v1.md` §Precedence, eleven ranks. Generalised: `curricula/arduino_kit/` became `CURRICULUM`, and the composed-contract rank became this file |
| 2 | **The recorded divergences** — a prose document that contradicts calibration loses, *and the divergence is reported* rather than resolved silently | `inputs.v1.md:96-100` | §Precedence, final paragraph. The two named divergences became the general statement, because naming one curriculum's files is what `G2` was |
| 3 | **No hardcoded count** — read it from the manifest, assert it against the ids present, derive every command from it | `inputs.v1.md:102-104` | §Precedence closing paragraph and §Never hardcode. Widened from the unit count to the curriculum's name and its subject |
| 4 | **One parent** — the domain's machine-readable data is the single authority; prose, tables, maps and diagrams are generated from it; fail closed on inconsistency | `architecture.v1.md:44-50` | §One parent, and it is now **checked** rather than stated: `DOC-DERIVED-FROM-SOURCE`, executed by `FR-P5-DERIVATION` |
| 5 | **Grounding** — every domain value carries a primary source, retrieved during the run by exact identifier, never recalled | `architecture.v1.md:52-57` | §Grounding. The `BLOCKED` case moved with it and changed kind: it is deterministic — did the fetch succeed, does the hash resolve — rather than a model's judgement, per the research §4.3 |
| 6 | **No model for deterministic work** — no model for merging, validating, hashing, rendering, aggregating, auditing or logging | `routing.v1.md:23-25` | §Routing, third invariant, with its check id `SEL-NO-MODEL-FOR-DETERMINISTIC` intact |

## What else moved, and what did not

**Twelve reviewers became one judge.** `architecture.v1.md:20-27` required twelve
isolated invocations. §5.2 of the plan directs the replacement and the evidence is §4.1:
nine cross-family judges provide 2.18 effective votes, and the best single judge matched
the full panel. `REV-COUNT-TWELVE` is retired and `REV-JUDGE-SINGLE-CROSS-FAMILY`
replaces it in `policy/checks.v1.yaml`. `REV-ISOLATED` is kept unchanged, and the prompt
now records what isolation does *not* address: correlated error.

**`G4` closed.** `component_lab_template.v1.md` was titled *"Component-Oriented
Electronics Lab Template"* and wrote its tone, child-language and safety rules about one
subject. `meta_prompt/assets/unit_prose.v1.md` replaces it. Its safety baseline is now
the *shape* of a safety rule — the curriculum states the specifics and its verifier
enforces them — because what is hazardous is a property of the subject.

**`pedagogy.v1.md` transfers whole**, as §2 says it would. 5E, Bloom,
Predict-Observe-Explain and cognitive load are teaching structure, not electronics.

**`model_selector_prompt.v1.md` stays**, and not because this plan wanted it: it is one
of the 26 destination files the folder plan's §4 tree names, and `FR-P0-TREE` asserts
every one of them exists. Removing it would fail a finished plan's gate to satisfy this
one. It is a companion the selector call reads, it names no curriculum, and it is
carried unchanged.

**What died, roughly 485 lines:** `proving.v1.md`'s six meta gates,
`deliverables.v1.md`, `logging.v1.md`'s meta state and drift stops, and the v6 prompt's
mission, write boundary, asset table and execution order. All of it existed to build a
generator. When nothing is being built, it has no subject. The parts with a runtime
meaning — the release table, the terminal states, the action-log pairing rule — were
carried into the prompt's §Proving it and §Final response rather than dropped.

## The order was kept

`meta_prompt/curriculum.prompt.v1.md` was written and committed before any file moved to
`meta_prompt/deprecated/`, and `tests/meta_prompt_source.py` was repointed in the same
commit that retired v6 — so no gate ever scanned a prompt that had left, and none
scanned a directory whose contract had gone. `FR-P5-ENGINE-GENERIC` reports `(a) 0
files` against the prompt that module names, which is this one.
