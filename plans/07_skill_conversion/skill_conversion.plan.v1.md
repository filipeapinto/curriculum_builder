# Skill conversion — plan v1

**Subject:** `meta_prompt/curriculum.prompt.v1.md`
**Goal:** make the curriculum contract invocable as a project skill without the skill
becoming a second copy of the contract.
**Written:** 2026-08-02

---

## The decision

Convert by **reference, not by transcription.** A new skill at
`.claude/skills/curriculum-build/SKILL.md` becomes the entry point; the contract stays
where it is and remains the only normative document.

Three properties of the contract force this and are not negotiable:

- **`ENGINE` is derived from the contract's own file location** (contract line 15,
  "derived, never written down"). A copy under `.claude/skills/` resolves `ENGINE` to the
  skill directory, and every path in the Inputs table then points at nothing. A copy is
  not a copy; it is a broken run.
- **The run records the hash of the contract file** (§Execution step 8). Two files
  carrying the contract means the recorded hash no longer identifies what executed.
- **Superseded versions live in `meta_prompt/deprecated/` and are never read**
  (§Precedence). Skills live at one fixed path and are overwritten in place, which has no
  room for that discipline. Keeping the contract versioned where it already is preserves
  it.

## The ranking problem, and the rule that follows from it

§Precedence ranks all eleven document classes and states why: "Every source that is read
is ranked. An unranked document is one whose contradictions get settled by whoever reads
it last, which is how four prose files came to promise something fourteen units
contradict."

A `SKILL.md` is read at the start of every run and is ranked nowhere. Confirmed: nothing
under `tests/` or `policy/` references `.claude`, so the skill also sits outside every
gate.

Two ways out. This plan takes the second.

1. Add the skill to §Precedence. Rejected — it edits the contract to accommodate a
   convenience wrapper, and it puts a twelfth rank in a list whose point is that it is
   closed.
2. **Make the skill strictly non-normative.** It states no rule the contract does not
   already state, resolves no conflict, and adds no check, threshold, ordering or
   vocabulary. Its whole content is: which file to read, which two arguments are
   required, and which preconditions to evaluate before reading anything else. A document
   that asserts nothing cannot contradict anything, so it needs no rank.

This is the single constraint the rest of the plan serves, and it is the thing to check
first in review.

## What the skill contains

**Path:** `.claude/skills/curriculum-build/SKILL.md`. No `scripts/`, no `references/`, no
`assets/` — each of those would be new content, and new content is normative content.

**Frontmatter.** `name: curriculum-build`. A `description` in the style the two existing
project skills already use: what it does, the trigger phrasings ("build the curriculum",
"run the pipeline on <curriculum>", "generate the units for <name>"), and a scope
boundary distinguishing it from `curriculum-concept-visualization` (draws a diagram) and
`electronics-circuit-visualization` (renders circuit data). The description must contain
no curriculum's subject words — `FR-P5-ENGINE-GENERIC` is the gate that would report it,
and although it does not currently scan `.claude/`, writing a subject word into an engine
document is the defect that gate exists to detect regardless of whether it is caught.

**Body, in this order:**

1. One line: read `meta_prompt/curriculum.prompt.v1.md` in full and follow it. It is the
   contract; this file is not.
2. The two required arguments, `--curriculum` and `--output-root`, with the refusal:
   neither has a default, and a run that was not given both does not start (§Execution
   step 1). This is the enforcement the door is for.
3. The three startup preconditions, named by their existing check ids and evaluated
   before any artifact and before any model call:
   - `PRECONDITION-ASSETS-RESOLVE` — the three rows of the contract's companion table
     resolve (§Companions);
   - `PRECONDITION-OUTPUT-ROOT-EXISTS` — `OUTPUT_ROOT` holds no prior run; report the
     occupied path and the next free version name; never auto-increment or merge
     (§Mission);
   - the domain verifier exists for the supplied curriculum, and its declared fixtures
     have been executed (§Execution step 7).
4. A closing line stating that everything else — ordering, gates, acceptance, reporting —
   is the contract's, and that this file adds nothing to it.

Target length: under 60 lines including frontmatter. If it grows past that, content has
leaked in from the contract and should be deleted rather than reworded.

## Current-state disclosure

The contract describes a full run; the repository executes no part of one. `RT-5` records
that no controller, logger, renderer or live route exists; `RT-7` records that no unit has
ever been generated and that reporting fixture coverage as generated-unit coverage would
be failure A5.

The skill therefore states, in one sentence, that no runtime exists yet and a run will
reach the point where it must execute a model, render an artifact or fetch a source and
stop there. Omitting this produces a skill that invites a run it cannot finish and then
reports partial coverage as success — the exact misreporting §Proving it calls a drift
stop.

This sentence is disclosure, not a rule, so it stays inside the non-normative constraint.

## Steps

1. Create `.claude/skills/curriculum-build/SKILL.md` as specified above.
2. Read it against the contract line by line and delete every sentence that states a rule
   the contract states. Deletion, not paraphrase.
3. Confirm no subject vocabulary from any curriculum under `curricula/` appears in it.
4. Run `./tests/run_gates.sh` and `python3 tests/check_meta_prompt.py`. Both must report
   exactly what they reported before the change — the skill touches no gated file, so any
   movement means something else was edited.
5. Confirm `git status --porcelain` shows one new file and nothing else. No edit to
   `meta_prompt/`, `policy/`, `schemas/` or `tests/` is in scope.

## Out of scope

Named because each is a plausible next thought and each would change what this plan is:

- editing the contract, including adding the skill to §Precedence;
- writing the controller, the logger or any runtime (`RT-5`);
- extending any gate to scan `.claude/`;
- adding scripts, references or assets to the skill;
- converting `docs/prompts/curriculum_pipeline_infographic.v2.prompt.md` or the
  `meta_prompt/assets/` companions to skills;
- changing how the two existing project skills are written.

## How to tell it worked

A reader who invokes the skill reaches the contract, having been stopped first if an
argument is missing, if a companion does not resolve, or if the output root is occupied.
A reader who reads the skill alone learns no rule — and if they can quote a rule from it
that the contract does not state, the conversion failed and the fix is to cut that line.
