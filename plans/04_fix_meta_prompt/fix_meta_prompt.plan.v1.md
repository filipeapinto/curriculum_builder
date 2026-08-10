# Fix the meta prompt — plan v1

**Date:** 2026-07-31
**Subject:** `meta_prompt/meta_curriculum_builder.prompt.v5.md`
**Status:** proposed, not started. No file has been edited under this plan.
**Predecessor evidence:** `plans/fix_curriculum_meta_prompt/research/redundancy.analysis.v1.md`
§5 (nine changes reported but not made) and §6 (three product decisions escalated to a
human). Both predate the folder refactoring and are re-verified against the current
tree below, not assumed.

---

## 1. The objective, stated so it can be failed

**An agent handed this prompt and nothing else must be able to start.** Today it
cannot: the block that tells it where it is names a directory that does not exist.
Every other defect in this plan is secondary to that one.

Three sub-objectives, in priority order:

1. **Anchoring.** Every variable in the write boundary resolves to a real location,
   and every input path resolves from it.
2. **Truthfulness.** No sentence in the prompt asserts something the repository
   contradicts, and no release gate is unsatisfiable-by-construction or vacuous.
3. **Precision.** Every reference is unambiguous — no bare filename whose folder must
   be guessed, no precedence list that omits documents it must rank.

**Explicit non-objective.** This plan does **not** make the generator exist. Nothing
here executes a model, writes an execution log or renders a PDF. It repairs a
specification so that the specification could be followed; it does not follow it.

---

## 2. State at the time of writing

Verified 2026-07-31 against `HEAD` = `5b1a0c6`, worktree clean, all 31 gates passing.

**What is already right, and must not be disturbed.** All 32 repo-relative paths the
prompt names resolve correctly — the folder refactoring retargeted them and
`FR-P0-NOSTALE` holds them at zero stale hits. Schema coverage is materially better
than when the predecessor analysis was written: eleven `policy/` manifests now carry
a `schema:` pointer and validate, and `curriculum`, `lab`, `calibration`,
`kit_calibration` and `circuit_data` all have contracts.

**What is broken.** Twelve defects, in three classes.

### A — Anchoring. Blocks any run.

| # | Where | Defect |
|---|---|---|
| **A1** | `:23` | `ROOT = …/Documentos/elegoo` exists but holds only `outputs/`, `tmp/`, `work/`. None of the inputs is under it. |
| **A2** | `:24` | `CREATOR = curriculum_creator` does not exist — not under `ROOT`, not in this repository, nowhere. |
| **A3** | `:25` | `META_PROMPT` names `curriculum_creator/prompts/meta_curriculum_prompt.prompt.v5.md`. Neither the folder nor that filename exists; the file is `meta_prompt/meta_curriculum_builder.prompt.v5.md`. |
| **A4** | `:26` | `LEGACY = curriculum_creator/plans/legacy_v3` — correct subpath, wrong prefix. |
| **A5** | `:27` | `WORK` is an English sentence, not a path. `V7 = WORK/templates_v7` therefore resolves to nothing, so `PRECONDITION-OUTPUT-ROOT-EXISTS` — "stop if `V7` exists at startup" — cannot be evaluated at all. **Introduced by the folder refactoring** while purging the `work/elegoo_labs` ghost paths: removing the ghost was right, leaving prose where a path goes was not. |
| **A6** | `:50` | "Everything required is under `CREATOR`" is false. Everything required is under this repository. |

### B — Precision.

| # | Where | Defect |
|---|---|---|
| **B1** | `:67` | Three bare filenames — `roster.md`, `teacher_framework.md`, `teacher_audit.md` — read as repo-root paths. They live in `curricula/arduino_kit/`. |
| **B2** | `:78-82` | The precedence list ranks five sources and omits four documents it must rank: `meta_prompt/component_lab_template.v1.md`, `meta_prompt/pedagogy.v1.md`, `docs/how_it_works.md`, `readme.md`. Reported as unfixed by the predecessor analysis; still unfixed. |

### C — Truthfulness.

| # | Where | Defect |
|---|---|---|
| **C1** | `:50`, `:310` | "Validate each file against its schema before reading a value from it" is unfulfillable for prose inputs, which have no schema and cannot have one. |
| **C2** | `:339` | Release gate "every fixture marked `reject` actually rejected" is **vacuous for four of five ids**: `LAB-BLOOM-DEPTH`, `LAB-POE-ORDER`, `LAB-CURRENT-MARGIN` and `LAB-VALUE-SOURCED` declare `fixture_expectation: reject` and name no fixture. Only `L01-POLARITY-NEUTRAL` has one. |
| **C3** | `:358` | "`ACT` entries record completed actions" contradicts `schemas/execution_log.schema.v2.json`, whose `act.status` enum is `started \| completed \| skipped` and which appends an ACT at start *and* at completion. |
| **C4** | `:216` | The gate table's category `live-golden` has no counterpart in `policy/checks.v1.yaml`, whose stage vocabulary is `logger \| static \| deterministic \| golden \| live-capability`. Two names for one stage. |

---

## 3. The decision this plan cannot make

**Where do runs write?** `A1`, `A5` and the whole `V7` precondition depend on it, and
it is a product decision, not a consistency question.

Three options, with what each costs:

| Option | `ROOT` | Cost |
|---|---|---|
| **(a)** run root beside the repo | `…/Documentos/elegoo/work` | Nothing to create — `elegoo/work` already exists. Keeps generated output out of the input repository, which is what `CREATOR` immutability was for. |
| **(b)** run root inside the repo | `…/curriculum_builder/runs` | Self-contained and clonable, but generated artifacts land inside the input tree, and `.gitignore` must then carry them. Weakens "everything else is immutable, `CREATOR` included". |
| **(c)** run root supplied at invocation | `--output-root`, no default | Most honest — the controller already declares `--output-root` in `policy/controller.v1.yaml`. But the prompt cannot then state a concrete `V7`, and the startup precondition becomes conditional on an argument. |

**Recommendation: (a).** It preserves the immutability boundary the prompt is built
around, requires creating nothing, and leaves `--output-root` free to override.
**This plan does not proceed past step 1 until a human picks one.**

---

## 4. The fixes

Each is a single edit to `meta_prompt/meta_curriculum_builder.prompt.v5.md` unless
stated. Nothing else in the repository changes except where named.

**Step 1 — the write boundary (A1-A6).** Rewrite the block so every variable is a
path. Under recommendation (a):

```text
ROOT        = <the chosen run root, from §3>
CREATOR     = /Users/…/Documentos/curriculum_builder     the input repository, immutable
META_PROMPT = CREATOR/meta_prompt/meta_curriculum_builder.prompt.v5.md
LEGACY      = CREATOR/plans/legacy_v3
V7          = ROOT/templates_v7
```

`PRIOR_V4` and `PRIOR_V5` are **deleted**, not repointed: they exist to be named as
not-written-to, and neither exists at any location. Naming a directory that is not
there does not protect it. Their diagnoses are quoted in full in
`policy/failures.v1.yaml`, which the prompt already says.

`:50` becomes "Everything required is under `CREATOR`", which is then true.

**Step 2 — precision (B1, B2).** Expand the three bare filenames to their
`curricula/arduino_kit/` paths. Extend the precedence list to rank all nine sources,
or replace it with a pointer to a single owned list — the predecessor analysis
proposes the latter and this plan follows it, because a second copy of a precedence
order is a second thing to keep equal.

**Step 3 — truthfulness (C1-C4).**

- **C1** → "Validate every *manifest* against its schema before reading a value from
  it. Prose inputs have no schema; read them as prose." Narrowed to what is true.
- **C2** → the release gate is qualified to *"every fixture marked `reject` in
  `policy/checks.v1.yaml` actually rejected, and every id marked
  `fixture_expectation: reject` that names no fixture reported as such"*. The
  alternative — authoring four lab fixtures — is curriculum work and out of scope.
  **The defect is disclosed, not hidden, and not silently satisfied.**
- **C3** → correct the sentence to match the contract: an `ACT` is appended when an
  action starts and again when it ends; `EXEC` records a failure that closes a start.
- **C4** → use `golden`, the vocabulary `policy/checks.v1.yaml` owns.

**Step 4 — the three escalations.** `redundancy.analysis.v1.md` §6 raises three
product decisions that touch this prompt: `adult_led_controller_station` in fourteen
labs (P2), whether ImageGen is optional (P7), whether `recommended` is a supported
calibration value (P12). **This plan does not decide any of them.** It surfaces each
under its own id in `policy/deferred.v1.yaml` so they stop being prose in a document
nothing reads, and stop blocking a fix that is otherwise unrelated to them.

---

## 5. How this is verified — and the structural problem in doing so

The obvious answer is "add gates". It does not work as-is, and the reason matters.

`FR-P0-REGISTRY` compares `tests/gates/registry.py` against §8 of the **active
folder-refactoring plan**, resolved by `common.active_plan_path()`, which globs
`plans/folder_refactoring/` and takes the highest version. The registry must equal
that section exactly, in both directions. Adding a gate for the meta prompt would
make the registry disagree with a plan that is finished and accepted, and
`FR-P0-REGISTRY` would fail — correctly.

Three ways out, and this plan must pick one:

| | Approach | Consequence |
|---|---|---|
| **(i)** | Verify by a one-off resolution script plus review; add no gate. | Cheapest. The fix is then not regression-protected: the anchoring can rot again exactly as it did. |
| **(ii)** | Supersede with `folder_refactoring.plan.v7.md` carrying an extended §8. | Keeps one registry, but files meta-prompt gates under a plan about folders. Topically wrong, and grows a plan that is done. |
| **(iii)** | Generalise the harness: let the registry compose from **several** plans, each owning its own gate family, with `FR-P0-REGISTRY` checking each family against its own plan's §8. | Correct shape, and the only one where this plan can own gates named for it. Costs a change to `common.py`, `registry.py` and `FR-P0-REGISTRY` — the machinery the whole suite rests on. |

**Recommendation: (iii)**, but *sequenced after* the prompt fix, not before it. The
anchoring defect blocks a run today; the harness generalisation blocks nothing. Doing
(i) first and (iii) second gets the prompt runnable without a second refactor of the
gate suite standing between the user and a working prompt.

**Acceptance for this plan, whichever is chosen:**

1. Every variable in the write boundary resolves to an existing directory, or to one
   the prompt explicitly creates.
2. Every path the prompt names resolves, tested mechanically — the same sweep §2 used.
3. All 31 existing gates still pass, and the worktree is clean.
4. No sentence added by this plan asserts anything unproven; `C2`'s residual defect is
   reported by identifier, not resolved by wording.

---

## 6. Out of scope

Building the generator. Authoring the four missing lab fixtures. Deciding P2, P7 or
P12. Editing `plans/fix_curriculum_meta_prompt/`, which is history. Any change to
`policy/`, `schemas/` or `curricula/` except adding the three escalation ids to
`policy/deferred.v1.yaml` under step 4.
