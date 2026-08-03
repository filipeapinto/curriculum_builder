# Skill conversion — plan v3

**Subject:** `meta_prompt/curriculum.prompt.v1.md`
**Goal:** make the curriculum contract invocable as a project skill without the skill
becoming a second copy of the contract.
**Written:** 2026-08-02
**Supersedes:** `skill_conversion.plan.v2.md`, corrected against a second review.
Two corrections, one of them critical, recorded at the end.

---

## The decision

Convert by **reference, not by transcription.** A new skill at
`.claude/skills/curriculum-build/SKILL.md` becomes the entry point; the contract stays
where it is and remains the only normative document.

Two properties of the contract force this:

- **`ENGINE` is derived from the contract's own file location** (contract line 15,
  "derived, never written down"), and the derivation is anchored:
  `tests/check_meta_prompt.py:107` asserts the mission block's
  `PROMPT = ENGINE/meta_prompt/curriculum.prompt.v1.md` line. A second copy of the
  contract under `.claude/skills/` does not satisfy that anchor — it is a file claiming to
  be at a path it is not at, and every path in the Inputs table resolves from that claim.
- **The run records the hash of the contract file** (§Execution step 8), and superseded
  versions live in `meta_prompt/deprecated/` where they are never read (§Precedence). Two
  files carrying the contract means the recorded hash no longer identifies what executed.
  Skills live at one fixed path and are overwritten in place, which has no room for that
  version discipline.

## The ranking problem, and the rule that follows from it

§Precedence ranks all eleven document classes and states why: "Every source that is read
is ranked. An unranked document is one whose contradictions get settled by whoever reads
it last, which is how four prose files came to promise something fourteen units
contradict."

A `SKILL.md` is read at the start of every run and is ranked nowhere. It will, however, be
*gated*: `PRODUCTION_EXCLUDED_TOP_LEVEL` in `tests/gates/common.py:55` excludes exactly
`tests`, `plans` and `.git`, so `.claude/` is inside the production scan set. (v1 claimed
the opposite.)

Two ways out. This plan takes the second.

1. Add the skill to §Precedence. Rejected — it edits the contract to accommodate a
   convenience wrapper, and it puts a twelfth rank in a list whose point is that it is
   closed.
2. **The skill states nothing that could conflict.** Two rules, and the second is the one
   this version adds:
   - **Attribution.** Every line either points at the contract or restates a contract rule
     *with the section or check id it comes from*.
   - **No sequencing.** The skill states no order, no grouping, and no combination of
     rules. Ordering is §Execution's, entirely.

**Why attribution alone was not enough, demonstrated by this plan's own defect.** v2
claimed attribution resolved the ranking problem. It does not: a citation gives
traceability, not rank. And v2 proved it — while citing sections correctly throughout, it
bundled the domain-verifier requirement into a group of "startup preconditions" evaluated
"before any artifact and before any model call." The contract does not say that. §Execution
puts the verifier at **step 7**, after `OUTPUT_ROOT` is created (step 4), after the logger
passes gate 0 (step 5), and after every manifest validates (step 6). Only steps 2 and 3 are
genuinely pre-artifact. v2 invented an ordering, cited its sources faithfully, and was
wrong anyway.

That is the failure mode attribution does not cover: **a set of correctly-cited rules,
combined in an order nobody authorised.** Hence the second rule. A document that sequences
nothing cannot resequence anything.

Residual risk, stated rather than resolved: an unranked document is still unranked, and
these two rules narrow the ways it can go wrong without closing them. Minimality is the
only remaining defence, which is why the length cap below is a constraint and not a
preference.

## What the skill contains

**Path:** `.claude/skills/curriculum-build/SKILL.md`. No `scripts/`, no `references/`, no
`assets/` — each would be new content, and new content is content with no citation.

There is a second, mechanical reason for that shape. `FR-P0-NOSTALE` scans `.claude/` and
reads a skill-relative path as a stale repository path: it currently reports three hits on
the literal string `assets/` in
`.claude/skills/curriculum-concept-visualization/SKILL.md:62` and
`references/layouts.md:4,46`. The term is anchored — `(?<![A-Za-z0-9_./])assets/` at
`tests/gates/fr_p0_structure.py:46` — so `meta_prompt/assets/` passes and a bare `assets/`
trips. **Every path the new file names must be repo-root-relative.**

**Frontmatter.** `name: curriculum-build`. A `description` in the style the two existing
project skills use: what it does, the trigger phrasings ("build the curriculum", "run the
pipeline on <curriculum>", "generate the units for <name>"), and a scope boundary
distinguishing it from `curriculum-concept-visualization` (draws a diagram) and
`electronics-circuit-visualization` (renders circuit data).

The description must contain no curriculum's subject words. **This is unenforced.**
`FR-P5-ENGINE-GENERIC` scans `policy/`, `schemas/`, the meta-prompt and the companion
markdown, and does not call `production_files()` (`tests/gates/fr_p5_engine.py:49-51`,
`67-81`, `254-256`) — so it does not reach `.claude/`. v2 asserted that it did. It is a
discipline here, not a gate, and writing a subject word into an engine-level document is
the defect that gate exists to detect whether or not it is caught.

**Body, in this order:**

1. One line: read `meta_prompt/curriculum.prompt.v1.md` in full and follow it. It is the
   contract; this file is not.
2. The two required arguments, `--curriculum` and `--output-root`: neither has a default,
   and a run that was not given both does not start (§Execution step 1).
3. The two genuine startup preconditions — the only two things the contract evaluates
   before any artifact exists:
   - `PRECONDITION-ASSETS-RESOLVE` — the three rows of the contract's companion table
     resolve (§Companions, §Execution step 2);
   - `PRECONDITION-OUTPUT-ROOT-EXISTS` — `OUTPUT_ROOT` holds no prior run; report the
     occupied path and the next free version name; never auto-increment or merge
     (§Mission, §Execution step 3).
4. A closing line: everything else — the logger, manifest validation, the domain verifier,
   unit order, gates, acceptance and reporting — is §Execution's, in §Execution's order,
   and this file neither restates nor reorders it.

**The domain verifier is deliberately not a door check.** It is §Execution step 7, owned by
`FR-P5-VERIFIER-REQUIRED` (`tests/gates/registry.py:340`), and it runs after the logger
exists so that its refusals are logged. v2 hoisted it to the door; that was the critical
defect of this plan's second version and it is corrected here by removal, not by rewording.

Target length: under 50 lines including frontmatter. If it grows past that, content has
leaked in from the contract and should be deleted rather than reworded.

The two existing project skills are 126–136 lines and carry full normative workflows with
skill-relative paths, so this reference-only shape has no precedent in the repo. That is
intended: neither of them is a versioned contract that hashes itself at run time.

## Current-state disclosure

The contract describes a full run; the repository executes no part of one. `RT-5` records
that no controller, logger, renderer or live route exists; `RT-7` records that no unit has
ever been generated and that reporting fixture coverage as generated-unit coverage would
be failure A5.

The skill therefore states, in one sentence, that no runtime exists yet and a run will
reach the point where it must execute a model, render an artifact or fetch a source and
stop there. Omitting this produces a skill that invites a run it cannot finish and then
reports partial coverage as success — the exact misreporting §Proving it calls a drift
stop. This is disclosure, not a rule, and it sequences nothing.

## Baseline, measured before any change

- `./tests/run_gates.sh` **requires a phase argument** (`tests/run_gates.sh:9`); with none
  it exits 2 on usage. The real commands are `./tests/run_gates.sh 4` and
  `./tests/run_gates.sh 5`. (v1 gave the bare command.)
- `./tests/run_gates.sh 4` → **28 PASS, 2 FAIL, 0 BLOCKED, 8 SKIPPED of 38**.
- `./tests/run_gates.sh 5` → **36 PASS, 2 FAIL, 0 BLOCKED, 0 SKIPPED of 38**.
- `python3 tests/check_meta_prompt.py` → exit 0, **6/6 PASS**.

Both failures are pre-existing and neither is caused by this work:

- `FR-P0-CLEAN` — the worktree is dirty (uncommitted `docs/` work, plus this plan). It
  cannot pass while this plan is being written, and chasing it is not part of the
  conversion.
- `FR-P0-NOSTALE` — the three `assets/` hits in the existing
  `curriculum-concept-visualization` skill. **A real defect, introduced by commit
  `4e3a779`, and out of scope here.** Flagged so it is not mistaken for damage this change
  caused, and so it gets its own fix rather than being folded into this one.

`plans/` is excluded from the production scan set, and `plan-ref-stale`
(`tests/gates/fr_p0_structure.py:325`) matches only `folder_refactoring.(plan|prompt).vN.md`
filenames, so this plan folder's own versioning trips nothing.

## Steps

1. Create `.claude/skills/curriculum-build/SKILL.md` as specified above.
2. Read it against the contract line by line. Delete every sentence that states a rule
   without naming the section or check id it comes from — deletion, not paraphrase.
3. **Check it sequences nothing.** For every rule it restates, confirm the contract states
   that rule at that point in that order. Any "before X" or "after Y" the contract does not
   state is the v2 defect recurring; cut it.
4. Confirm every path it names is repo-root-relative, and that no subject vocabulary from
   any curriculum under `curricula/` appears in it.
5. Run `./tests/run_gates.sh 4`, `./tests/run_gates.sh 5` and
   `python3 tests/check_meta_prompt.py`. Required outcome: **the same two failures and no
   third**, and `FR-P0-NOSTALE` still reporting exactly three hits, all in
   `curriculum-concept-visualization`. A fourth hit means a skill-relative path was
   written into the new file. This test is achievable: no repo-root-relative path in the
   planned content matches any entry in `STALE_TERMS`.
6. Confirm `git status --porcelain` shows the new skill and this plan added to the
   already-dirty set, and no modification to `meta_prompt/`, `policy/`, `schemas/` or
   `tests/`.

## Out of scope

- editing the contract, including adding the skill to §Precedence;
- writing the controller, the logger or any runtime (`RT-5`);
- fixing the pre-existing `FR-P0-NOSTALE` hits in `curriculum-concept-visualization`;
- extending `FR-P5-ENGINE-GENERIC` to scan `.claude/`, however tempting given the finding
  above;
- changing `PRODUCTION_EXCLUDED_TOP_LEVEL` or any gate's scan set;
- adding scripts, references or assets to the new skill;
- converting `docs/prompts/curriculum_pipeline_infographic.v2.prompt.md` or the
  `meta_prompt/assets/` companions to skills;
- committing, or cleaning the worktree to make `FR-P0-CLEAN` pass.

## How to tell it worked

A reader who invokes the skill reaches the contract, having been stopped first if an
argument is missing, if a companion does not resolve, or if the output root is occupied.
A reader who reads the skill alone finds no rule without a pointer to where it is decided,
and no ordering at all. If they can quote a rule with no pointer, or infer a sequence the
contract does not state, the conversion failed.

## Corrections from the v2 review

1. **CRITICAL — v2 reordered the contract.** It hoisted the domain-verifier requirement
   (§Execution step 7) into a bundle of checks run "before any artifact," alongside the two
   genuine startup preconditions. The contract runs it after `OUTPUT_ROOT` exists, after
   the logger passes gate 0, and after manifests validate. Removed from the skill's door
   checks, and a no-sequencing rule added to prevent the class.
2. **v2 claimed `FR-P5-ENGINE-GENERIC` scans `.claude/`.** It does not — it does not call
   `production_files()`. The subject-word rule there is unenforced discipline, now stated
   as such. (v1 said the gate wouldn't catch it; v2 overcorrected; this is the measured
   answer.)

Confirmed sound by the same review and unchanged: the `FR-P0-NOSTALE` reasoning and the
achievability of step 5's acceptance test.

Carried forward from the v1 review, still standing: the anchor-based ENGINE argument, the
phase-argument baseline, `.claude/` being inside the production scan set, and
`FR-P5-VERIFIER-REQUIRED` as the verifier's owning gate.

One review point remains declined: that the reference-only shape has no precedent among
the existing skills. True, and intended — neither of them hashes itself at run time or
keeps superseded versions.
