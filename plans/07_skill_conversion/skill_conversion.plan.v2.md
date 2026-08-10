# Skill conversion — plan v2

**Subject:** `meta_prompt/curriculum.prompt.v1.md`
**Goal:** make the curriculum contract invocable as a project skill without the skill
becoming a second copy of the contract.
**Written:** 2026-08-02
**Supersedes:** `skill_conversion.plan.v1.md`, corrected against a repository review.
Five corrections, recorded at the end.

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

A `SKILL.md` is read at the start of every run and is ranked nowhere.

**v1 claimed the skill would also sit outside every gate. That was wrong.**
`PRODUCTION_EXCLUDED_TOP_LEVEL` in `tests/gates/common.py:55` excludes exactly `tests`,
`plans` and `.git`. `.claude/` is inside the production scan set, and the existing skills
are already being scanned — see the pre-existing failure recorded below. The skill will be
gated. What it will not be is *ranked*, and ranking is the problem this section is about.

Two ways out. This plan takes the second.

1. Add the skill to §Precedence. Rejected — it edits the contract to accommodate a
   convenience wrapper, and it puts a twelfth rank in a list whose point is that it is
   closed.
2. **No rule originates in the skill.** Every line of it either points at the contract or
   restates a contract rule *with the section or check id it comes from*. Nothing appears
   there that cannot be traced to a numbered source.

**v1 called this "strictly non-normative" and claimed the skill "asserts nothing." That
overstated it.** Telling a reader to refuse a run with a missing argument, and to evaluate
three preconditions before touching an artifact, is a rule being stated — the fact that
the contract states it first does not make the restatement inert. The honest constraint is
attribution, not silence: a restatement that carries its citation cannot outrank its
source, because a reader who finds a conflict has the pointer to the thing that wins. An
uncited paraphrase is exactly the unranked document §Precedence warns about. So the test
is not "does this line assert something" but **"does this line say where it came from."**

This is the single constraint the rest of the plan serves, and it is the thing to check
first in review.

## What the skill contains

**Path:** `.claude/skills/curriculum-build/SKILL.md`. No `scripts/`, no `references/`, no
`assets/` — each would be new content, and new content is content with no citation.

There is now a second, mechanical reason for that shape. `FR-P0-NOSTALE` scans `.claude/`
and reads a skill-relative path as a stale repository path: it currently reports three
hits on the literal string `assets/` in
`.claude/skills/curriculum-concept-visualization/SKILL.md:62` and
`references/layouts.md:4,46`. **Any skill-relative path written into the new SKILL.md will
trip the same gate.** Every path it names must be repo-root-relative
(`meta_prompt/curriculum.prompt.v1.md`, `meta_prompt/assets/…`), which is what a
reference-only skill needs anyway.

**Frontmatter.** `name: curriculum-build`. A `description` in the style the two existing
project skills use: what it does, the trigger phrasings ("build the curriculum", "run the
pipeline on <curriculum>", "generate the units for <name>"), and a scope boundary
distinguishing it from `curriculum-concept-visualization` (draws a diagram) and
`electronics-circuit-visualization` (renders circuit data). The description must contain
no curriculum's subject words — `FR-P5-ENGINE-GENERIC` is the gate that reports it, and it
scans `.claude/`.

**Body, in this order:**

1. One line: read `meta_prompt/curriculum.prompt.v1.md` in full and follow it. It is the
   contract; this file is not.
2. The two required arguments, `--curriculum` and `--output-root`, with the refusal:
   neither has a default, and a run that was not given both does not start
   (§Execution step 1).
3. The three startup preconditions, each carrying its check id, evaluated before any
   artifact and before any model call:
   - `PRECONDITION-ASSETS-RESOLVE` — the three rows of the contract's companion table
     resolve (§Companions);
   - `PRECONDITION-OUTPUT-ROOT-EXISTS` — `OUTPUT_ROOT` holds no prior run; report the
     occupied path and the next free version name; never auto-increment or merge
     (§Mission);
   - `FR-P5-VERIFIER-REQUIRED` (`tests/gates/registry.py:340`) — the supplied curriculum
     declares a domain verifier and its declared fixtures have been executed against it,
     each refused for its own declared code (§Execution step 7). v1 described this
     precondition without naming the gate that owns it.
4. A closing line stating that everything else — ordering, gates, acceptance, reporting —
   is the contract's, and that this file adds nothing to it.

Target length: under 60 lines including frontmatter. If it grows past that, content has
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
stop.

## Baseline, measured before any change

Recorded here because v1's acceptance test assumed a clean tree and a bare
`./tests/run_gates.sh`, and both were wrong.

- `./tests/run_gates.sh` **requires a phase argument** (`tests/run_gates.sh:9`); with none
  it exits 2 on usage. The real commands are `./tests/run_gates.sh 4` and
  `./tests/run_gates.sh 5`.
- `./tests/run_gates.sh 4` → **28 PASS, 2 FAIL, 0 BLOCKED, 8 SKIPPED of 38**.
- `./tests/run_gates.sh 5` → **36 PASS, 2 FAIL, 0 BLOCKED, 0 SKIPPED of 38**.
- `python3 tests/check_meta_prompt.py` → exit 0, **6/6 PASS**.

Both failures are pre-existing and neither is caused by this work:

- `FR-P0-CLEAN` — the worktree is dirty (uncommitted `docs/` work, plus this plan). It
  cannot pass while this plan is being written, and chasing it is not part of the
  conversion.
- `FR-P0-NOSTALE` — the three `assets/` hits in the existing
  `curriculum-concept-visualization` skill, described above. **A real defect, introduced by
  commit `4e3a779`, and out of scope here.** Flagged so it is not mistaken for damage this
  change caused, and so it gets its own fix rather than being folded into this one.

## Steps

1. Create `.claude/skills/curriculum-build/SKILL.md` as specified above.
2. Read it against the contract line by line. Delete every sentence that states a rule
   without naming the section or check id it comes from — deletion, not paraphrase.
3. Confirm every path it names is repo-root-relative, and that no subject vocabulary from
   any curriculum under `curricula/` appears in it.
4. Run `./tests/run_gates.sh 4`, `./tests/run_gates.sh 5` and
   `python3 tests/check_meta_prompt.py`. Required outcome: **the same two failures and no
   third**, and `FR-P0-NOSTALE` still reporting exactly three hits, all in
   `curriculum-concept-visualization`. A fourth hit means a skill-relative path was
   written into the new file.
5. Confirm `git status --porcelain` shows the new skill and this plan added to the
   already-dirty set, and no modification to `meta_prompt/`, `policy/`, `schemas/` or
   `tests/`.

## Out of scope

Named because each is a plausible next thought and each would change what this plan is:

- editing the contract, including adding the skill to §Precedence;
- writing the controller, the logger or any runtime (`RT-5`);
- fixing the pre-existing `FR-P0-NOSTALE` hits in `curriculum-concept-visualization`;
- changing `PRODUCTION_EXCLUDED_TOP_LEVEL` or any gate's scan set;
- adding scripts, references or assets to the new skill;
- converting `docs/prompts/curriculum_pipeline_infographic.v2.prompt.md` or the
  `meta_prompt/assets/` companions to skills;
- committing, or cleaning the worktree to make `FR-P0-CLEAN` pass.

## How to tell it worked

A reader who invokes the skill reaches the contract, having been stopped first if an
argument is missing, if a companion does not resolve, if the output root is occupied, or
if the curriculum declares no verifier. A reader who reads the skill alone finds no rule
without a pointer to where it is actually decided — and if they can quote one, the
conversion failed and the fix is to cut that line or cite it.

## Corrections from the v1 review

1. **"Asserts nothing" was false.** The wrapper does state rules. Constraint reframed from
   non-normative to fully attributed.
2. **"`.claude/` is outside every gate" was false.** It is in the production scan set;
   `FR-P0-NOSTALE` already fails on it, and that failure constrains the new file's paths.
3. **`./tests/run_gates.sh` needs a phase argument.** Baseline measured and recorded.
4. **The ENGINE argument named the wrong mechanism.** Corrected to the anchor assertion at
   `tests/check_meta_prompt.py:107`; the conclusion is unchanged.
5. **The verifier precondition had no gate id.** Now `FR-P5-VERIFIER-REQUIRED`.

One review point was declined: that the reference-only shape has no precedent in the two
existing skills. True, and recorded above as intended rather than corrected — the contract
hashes itself and keeps superseded versions, and neither existing skill does either.
