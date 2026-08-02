# Prompt — retire the superseded schemas, one version per contract

**Repo:** `/Users/filipepinto/Projects/curriculum_builder`
**Written:** 2026-08-02
**Read `readme.md` first, then this file, then `policy/deferred.v1.yaml`.**

---

## Goal

`schemas/` holds two live versions of the same contract in four cases. Nothing validates
against the older four. Retire them: **one version of each contract in `schemas/`, the
superseded ones in `schemas/deprecated/`, every live reference removed, and every gate
green.**

The four:

| Superseded | Live replacement | Validates anything today? |
|---|---|---|
| `schemas/lab.schema.v3.json` | `schemas/lab.schema.v4.json` | no |
| `schemas/curriculum.schema.v4.json` | `schemas/curriculum.schema.v5.json` | no |
| `schemas/execution_log.schema.v1.json` | `schemas/execution_log.schema.v2.json` | no |
| `schemas/routing_decision.schema.v1.json` | `schemas/routing_decision.schema.v2.json` | no |

---

## The finding this rests on, which you must confirm before acting

The two `v1` contracts are retained on the stated ground that records **already accepted
under v1** must keep validating. Check whether any such record exists. It does not:

- no unit has ever been generated — `RT-7` in `policy/deferred.v1.yaml`;
- there is no logger and no execution log — `RT-5`;
- there is no `curricula/*/units/` directory and no output root anywhere in the repo;
- `meta_prompt/curriculum.prompt.v1.md:95` already states, of the other two, *"zero units
  were ever accepted under either."*

So the retention justification is empty: four schemas are kept alive to validate a set
that has never had a member. `RT-6` compounds it — it makes retirement wait on a logger
emitting `v2` records, a condition unrelated to whether `v1` is needed by anything.

**Confirm all four bullets yourself.** If any accepted record turns out to exist, stop
and report it: the goal is wrong and the two `v1` contracts stay.

---

## Starting state

`HEAD` is `9e6d005`. The worktree is **dirty**, from two different sources:

1. **Committed-worthy work, done and verified:** `FR-P1-DOC` was retired (it checked that
   a root document listed every top-level folder — ceremony, and its document had been
   deleted), the contract-shape declaration moved to `tests/contract_assets.v1.md`, and
   `AGENTS.md` was deleted with every live reference to it repointed or removed.
2. **Four untracked copies** at `schemas/deprecated/*.json` — an attempt to move the four
   superseded schemas that was reverted in `schemas/` but left the copies behind.

**Step 0.** Commit (1) and delete (2), then confirm a clean base before touching anything:

```sh
rm schemas/deprecated/curriculum.schema.v4.json schemas/deprecated/execution_log.schema.v1.json \
   schemas/deprecated/lab.schema.v3.json schemas/deprecated/routing_decision.schema.v1.json
git add -A && git commit -m "tests: retire FR-P1-DOC and move the contract-shape declaration into tests/"
./tests/run_gates.sh 4    # expect 30 PASS, 0 FAIL
./tests/run_gates.sh 5    # expect 38 PASS, 0 FAIL
python3 tests/check_meta_prompt.py   # expect EXECUTABLE (6/6)
```

If that base is not green, fix it before starting. Gates run against a **commit**;
`FR-P0-CLEAN` fails on a dirty tree, so commit between steps.

---

## What blocks the move, exactly

`FR-P1-SCHEMA-RETENTION` is the rule: a schema may enter `schemas/deprecated/` only when
a repository-wide search for its basename returns zero hits outside that folder. Run it
with the four files moved and it enumerates every blocker itself — use that output as
your worklist rather than a grep. As of writing it is:

**Live references that must go:**

- `meta_prompt/curriculum.prompt.v1.md:88-97` — the retained-contracts table and the
  sentence after it, naming all four.
- `curricula/arduino_kit/checks.v1.yaml:124-139` — `LAB-CURRENT-MARGIN` and
  `LAB-VALUE-SOURCED` name `schemas/lab.schema.v3.json` as `owner` and `artifact`. **This
  is the only structural one.** Those fields moved into the curriculum's own domain
  contract; repoint both ids at `curricula/arduino_kit/domain.schema.v1.json` and delete
  the note at `:17-21` that explains why they were left behind.
- `tests/gates/fr_p1_retention.py:34-38` — `RETAINED_CONTRACTS`, the exemption that keeps
  the two `v1` files out of `deprecated/`. Delete the list and its uses.
- `tests/gates/fr_p3_calibration.py:54-58` — `FROZEN_CONTRACTS_EXEMPT`. Same.
- `tests/gates/fr_p2_selector.py:48-53, ~209` — `DECISION_V1`, `LOG_V1`, `V1_CONTRACTS`
  and the `FR-P2-CONTRACT-VERSIONED` legs built on them. Read that gate before editing:
  it asserts the prompt authorizes `v2` **only** while `v1` is retained unchanged. With
  `v1` retired, the leg that must survive is "the prompt authorizes `v2` only"; the leg
  that must go is "`v1` is retained byte-unchanged in `schemas/`". Its fixtures
  (`prompt_authorizes_v1_contract.reject.md`, `prompt_extra_authorized_input.accept.md`,
  `prompt_missing_routing_input.reject.md`, `contract_v1_edited_in_place.reject.json`,
  `act_v1_shaped.accept.json`) must be re-read one by one — some still carry a real
  criterion, some only carry the retention rule.
- `policy/calibration.v1.yaml:142`, `curricula/arduino_kit/kit_calibration.v1.yaml:52`,
  `curricula/arduino_kit/domain.schema.v1.json:5`,
  `curricula/arduino_kit/manifest.domain.schema.v1.json:5`,
  `curricula/arduino_kit/arduino_kit_curriculum.v5.yaml:6`,
  `docs/how_it_works.{md,typ}`, `docs/infographic.prompt.v1.md`,
  `meta_prompt/assets/pedagogy.v1.md` — prose and comments citing an old basename to
  explain where something came from. Rewrite each to name the live contract, or drop the
  citation. Do not leave a sentence that is now false.
- `policy/deferred.v1.yaml` `RT-6` — rewrite. The obligation was "the v1 contracts are
  retirable once a logger emits v2 records". They are retirable because nothing ever
  emitted v1 records. Record it as discharged by obsolescence, with the evidence, and
  keep `RT-5` and `RT-7` untouched.

**One design decision, and it is yours to make and record.** The scan also flags
`meta_prompt/deprecated/*.md` — retired assets that mention the old basenames. Those are
files *nothing may read*, so they cannot be live references, and editing retired prose to
satisfy a gate corrupts the record. Recommended: exclude `**/deprecated/**` from the scan
in `tests/gates/fr_p1_retention.py`, with a comment stating why, and prove the narrowing
does not blind the gate by adding a `.reject.` fixture where a **live** file references a
retired schema and is still caught. Do not simply widen an exclusion until the gate is
quiet — that is the failure the whole harness exists to prevent.

---

## Constraints

- **`./tests/run_gates.sh 4` must report 30 PASS, 0 FAIL at every commit.** If a change
  costs one of them, the change is wrong, not the gate. (It was 31 until `FR-P1-DOC` was
  retired; that retirement is recorded in `plans/folder_refactoring/folder_refactoring.plan.v6.md`.)
- **An acceptance criterion is never relaxed to make the repository pass.** Correcting a
  scan root, a regex or a stale pointer is a fix; deleting an assertion because it now
  fails is not. If a gate leg exists only to enforce the retention you are removing,
  delete the leg *and say so in the commit*; if it asserts anything else, keep it.
- **Never delete a fixture to make a gate pass.** Re-read it; if its defect is no longer
  expressible, replace it with one that still bites.
- Every gate you touch keeps its `claim_class` truthful — the mechanisms it records must
  match what it actually does, or `FR-P0-REGISTRY` reports drift.
- `plans/**/deprecated/` and `plans/legacy_v3/` are history. Do not edit them.
- Commit in steps, one concern each, in the repo's imperative style. Do not push.

---

## Order of work

1. Confirm the finding (§"The finding"). Stop if it does not hold.
2. Step 0 above: clean base, green gates.
3. Repoint `LAB-CURRENT-MARGIN` and `LAB-VALUE-SOURCED`. Commit. Gates green.
4. Strip the prompt's retained-contracts table and the prose citations. Commit.
5. Take the `deprecated/` scan decision, implement it with its fixture. Commit.
6. Remove the `v1` exemptions from the three gates, re-reading each affected fixture.
   Commit.
7. Rewrite `RT-6`. Commit.
8. `git mv` all four schemas into `schemas/deprecated/`. Commit.
9. Final verification (below), then write
   `plans/schema_retirement/schema_retirement.result.v1.md`: what moved, what was deleted
   from which gate and why, the decision taken at step 5, and anything you left undone.

---

## Definition of done

```sh
./tests/run_gates.sh 4                 # 30 PASS, 0 FAIL, 0 BLOCKED
./tests/run_gates.sh 5                 # 38 PASS, 0 FAIL, 0 BLOCKED
python3 tests/check_meta_prompt.py     # EXECUTABLE (6/6)
ls schemas/*.json                      # exactly one version of each contract
ls schemas/deprecated/                 # the four superseded files plus .gitkeep
git status --porcelain                 # empty
```

and `FR-P1-SCHEMA-RETENTION` reports the four as retired with **zero** live references.

A partial result is reported as partial. If a reference cannot be removed without
weakening something, stop at that point, leave the schema in `schemas/`, and say which
one and why — four schemas retired for the wrong reason is worse than three retired for
the right one.
