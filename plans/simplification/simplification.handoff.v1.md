# Handoff — simplification plan v3, after execution and independent audit

**Written:** 2026-08-02
**Repo:** `/Users/filipepinto/Projects/curriculum_builder` (moved off OneDrive on this date)
**HEAD:** `0c47dc4`, worktree clean, branch `master`, nothing pushed
**Read this first, then `plans/simplification/prompt/simplification.prompt.v3.md`.**

---

## 1. What happened

`plans/simplification/prompt/simplification.prompt.v3.md` was executed against
`plans/simplification/plan/simplification.plan.v3.md`. Plan phases 0–5 were completed
and validated; plan phase 6 was not. Then five independent **Codex** reviews were fanned
out over the result, because the executing agent's judgement was not trusted. They found
**five defects the agent had missed**. None is fixed yet.

**The state to hold in mind: the engine genuinely did become generic, and five things
were damaged on the way there.** Both halves are true and neither cancels the other.

---

## 2. Environment — most of the old pain is gone

The repo used to live under OneDrive. `mmap()` fails on OneDrive placeholder files, so
`git log --follow` took 20+ minutes and every git-invoking gate failed for the
environment rather than for the repository. **That is over.** After the move:

| | before | after |
|---|---|---|
| `git status` | 2 min | 0.012 s |
| `git log --follow` one path | 20+ min | 0.016 s |
| `./tests/run_gates.sh 4` | minutes, often failing | **2.4 s**, 31 PASS |
| `./tests/run_gates.sh 5` | minutes, often failing | **2.8 s**, 38 PASS |

`.git` is a real directory inside the repo again. **Delete these two leftovers when
convenient — they are byte-identical copies of the same git dir and nothing reads them:**

    /Users/filipepinto/.cache/curriculum_builder.git
    /Users/filipepinto/Library/CloudStorage/OneDrive-ISCTE-IUL/Documentos/curriculum_builder.git.onedrive-backup

If a gate ever fails with `TimeoutError: [Errno 60]` or `mmap failed`, that was the old
environment and should no longer occur. If it does, it is not a repository defect.

---

## 3. Verified current state

    ./tests/run_gates.sh 4   ->  31 PASS, 0 FAIL, 0 BLOCKED, 7 SKIPPED
    ./tests/run_gates.sh 5   ->  38 PASS, 0 FAIL, 0 BLOCKED, 0 SKIPPED
    python3 tests/check_meta_prompt.py  ->  EXECUTABLE (6/6)
    63/63 fixtures pass.  Worktree clean.

`run_gates.sh 4` is the **folder-refactoring** family's regression run — a finished,
accepted plan. Its 31 must never move. `run_gates.sh 5` adds this plan's 7 gates.

Six commits, in the plan's own execution order (0, 4, 1, 2, 3, 5, 6):

    309b3ba  the four generic checks, each with an executed assertion   (plan phase 4)
    474b737  a unit contract that does not name its subject            (plan phase 1)
    0920757  the verifier a curriculum must declare, executed          (plan phase 2)
    1e14a1f  the check inventory splits, engine stops naming a kit     (plan phase 3)
    c87dd8e  one prompt, bound to nothing, and the meta level retired  (plan phase 5)
    0c47dc4  record that the L01 test has no executable path           (plan phase 6)

Baseline before any of it: `875c6b9`. Use `git diff 875c6b9..HEAD` for the whole change.

---

## 4. What was built

- **`meta_prompt/curriculum.prompt.v1.md`** — the deliverable. One prompt, one file, no
  section assets. Given a curriculum root it produces that curriculum and does not know
  what subject it teaches. v6 and its six section assets are under
  `meta_prompt/deprecated/`; three companions remain in `meta_prompt/assets/`.
- **`schemas/lab.schema.v4.json`** — six engine blocks plus `domain`, whose shape the
  engine deliberately does not fix. Closes `G1`.
- **`schemas/curriculum.schema.v5.json`** — no `kit_power_profile`, no `visual_system`.
  Closes `G5`. **See defect 1 below: this went too far.**
- **`curricula/arduino_kit/verify_domain.py`** — a real domain verifier. Seven electrical
  rules, no model call. Codex confirmed it is not a stub.
- **The check inventory is now two files** — `policy/checks.v1.yaml` (engine) and
  `curricula/<name>/checks.v1.yaml` (that curriculum's). Closes `G3`. Twelve ids moved.
- **`policy/calibration.v1.yaml`** — precedence comments generalised. Closes `G7`. Also
  gained the readability band and the Bloom verb table.
- **Seven gates in the `FR-P5-` family**, up from one. `FR-P5-ENGINE-GENERIC` now
  **passes**: zero engine files name a curriculum directory.

Result notes worth reading, in this order:
`plans/simplification/plan/simplification.phase0.result.v1.md` (the original measurement),
`…phase5.result.v1.md` (the six extracted rules, resolved one by one),
`…phase6.result.v1.md` (**currently wrong — see defect 2**).

---

## 5. THE FIVE DEFECTS — this is the work queue

All five were found by Codex, not by the executing agent. Listed worst first. Nothing
has been fixed.

### Defect 1 — `curriculum.schema.v5.json` is materially looser than v4

**The worst one.** `G5` was closed by *deleting* constraints rather than relocating them.

- v4 closed and validated `kit_power_profile` and `visual_system`
  (`schemas/curriculum.schema.v4.json:45-123`) and constrained mode/status/power presence
  (`:243-301`).
- v5 reduces `domain.config` to **any nonempty object**
  (`schemas/curriculum.schema.v5.json:60-63`) and `mode`/`domain_state` to **arbitrary
  strings** (`:240-267`).
- `FR-P0-SCHEMA` now validates that looser contract (`tests/gates/fr_p0_structure.py:460-475`).

**Fix:** the shape must live somewhere, and the right somewhere is the curriculum's own
contract — `curricula/arduino_kit/domain.schema.v1.json` or a sibling that validates
`domain.config`, plus a curriculum-declared enum for `mode` and `domain_state`. The
engine must require *that the curriculum constrains them*, not shrug. Moving a
constraint out of the engine is the plan's intent; dropping it is not.

### Defect 2 — `simplification.phase6.result.v1.md` is a false record

It says five of eight conditions have no executable path, no rasterizer, no second model
family. All three are wrong: `typst` 0.15.0 renders and rasterises to PNG, Poppler
26.04.0 is installed, `codex` 0.146.0 and `gemini` 0.24.5 are both present — and
**`policy/routes.v1.yaml:74` already records a proven PDF and Poppler rasterizer route**,
which the agent never read.

**Fix:** rewrite it to Codex's own wording —

> "Phase 6 produced no unit; conditions 2, 3, 4, 6 and 8 are executable, condition 7 has
> an available but not yet live-proven cross-family CLI, and conditions 1 and 5 cannot be
> independently evidenced because no controller/logger exists."

Keeping `HALTED` as the run-level outcome is defensible. Keeping the retracted blocker
analysis is not.

### Defect 3 — `L01-*` de-advertised, and the gate cannot see it

Plan phase 3 moved four `L01-*` ids to the curriculum inventory and removed `L01-*` from
the release table. `FR-P2-GATEITEMS` reads only `policy/checks.v1.yaml`
(`tests/gates/fr_p2_selector.py:41, 879-885`), so it went green instead of reporting
four unadvertised ids: `L01-DISCONNECTED`, `L01-POLARITY-NEUTRAL`,
`L01-NO-INVENTED-SUPPLY`, `L01-NO-UNPERFORMED-OBSERVATION`.

**Fix:** point `FR-P2-GATEITEMS` at `common.merged_check_inventory()` like the other five
gates, and give each curriculum's staged ids a release surface that advertises them.

### Defect 4 — `FR-P5-UNIT-CONTRACT` under-asserts

It compares only `required` and `additionalProperties`
(`tests/gates/fr_p5_unit.py:475-481`) and blacklists only five domain constraints
(`:492-495`). **An optional `electronics` property, or an `allOf` constraint on the
domain block, would pass** — which is `G1` walking back in through a side door.

**Fix:** assert over the full property set, not just `required`; reject any keyword that
constrains `domain`'s contents, not a blacklist of five.

### Defect 5 — a silenced cross-check

`tests/meta_prompt_source.py` sets `CROSS_CHECK_PLAN_TREE = False`, making
`shape_problems()` return immediately (`:187-230`) — even though its own docstring says
that without the comparison the contract's shape is self-certifying (`:221-227`). The
claimed replacement does not hold: `FR-P1-GITKEEP` only checks that four `.gitkeep` files
exist (`tests/gates/fr_p1_retention.py:45-73`), and the folder plan still declares the
obsolete v6 asset shape (`folder_refactoring.plan.v6.md:204-218`).

**Fix:** restore a real independent shape authority. Either update the folder plan's §4
tree to the current asset set, or move the shape declaration to a document maintained by
a different gate. A flag set to `False` is not a replacement.

---

## 6. Plan phase 6 — not done, and the stop was not justified

Stage B's L01 test was never attempted. Codex ruled: **`HALT NOT JUSTIFIED`**. The agent
read plan §7's *"phases 6 and 7 are not verifiable here"* as *"cannot be done"*; it means
the **harness** cannot gate them. The plan itself calls phase 6 "Unblocked", the executor
allows six correction cycles, and **none was attempted**.

Codex's condition-by-condition ruling:

- **2, 3, 4, 6, 8 — mechanically achievable by hand today.** Condition 4 needs the check
  functions called directly, because the gates scan only `curricula/*/units/`.
- **7 — achievable, but only after a real cross-family invocation.** Finding the binary
  is not proving the route.
- **1 and 5 — cannot be evidenced.** Without the deterministic logger, "read no path
  outside" and "fetched during this run" are self-reports.

Codex also overruled the agent's reasoning that an LLM writing unit blocks would be
"static coverage": *"an LLM following the live prompt and writing the unit blocks is
generated content, not static content… 'Code decides, models write' expressly assigns
writing to models."* A5 forbids passing off pre-authored fixtures as live generation; it
does not redefine model-authored output as static.

**Codex's single most important next action:**

> Implement the smallest deterministic controller and append-only v2 logger that can
> enforce and record one L01 run, including live route preflights, then rerun stage B
> from condition 1.

---

## 7. Constraints that must not be broken

From the executor prompt, and every one of them still binds:

- **R1** — `run_gates.sh 4` reports 31 PASS, 0 FAIL. *"If a change costs one of them, the
  change is wrong, not the gate."*
- **Fixing versus weakening** — an implementation may be corrected when it misreads its
  subject (wrong scan root, bad regex, misparsed path). **Acceptance criteria may never
  be relaxed to make a failing repository pass.** Defects 1, 3 and 5 above are all
  breaches of this line.
- **Schedule a leak; never silence one.** An exclusion in a gate, an exemption in a
  manifest, or a scan root that stops covering a live file is the defect, not the repair.
- **Never report a static or simulated pass as generated coverage** (A5).
- **The output is a draft.** No human reads or signs anything inside a run; the claim is
  "every declared automated check passed", never "child-ready".
- **Genericity is structurally enforced, not demonstrated.** One curriculum has ever
  existed. `RT-10` records this. Plan phase 7 — a second curriculum in an unrelated
  subject — is the plan's actual proof and is out of scope.
- **L01 cannot prove the domain verifier.** It is unpowered and polarity-neutral, so
  current limiting, polarity and supply match are unexercised by it.

Deferred register, for what is knowingly not done: `RT-7` (no generated unit exists),
`RT-8` (no curriculum declares its domain vocabulary, so leg (b) of the boundary gate is
armed and near-blind), `RT-10` (genericity undemonstrated). `RT-9` is deliberately unused
— a harness fixture cites it as its canonical dangling reference.

---

## 8. How to pick this up

    cd /Users/filipepinto/Projects/curriculum_builder
    ./tests/run_gates.sh 4      # expect 31 PASS, 0 FAIL   (~2.4s)
    ./tests/run_gates.sh 5      # expect 38 PASS, 0 FAIL   (~2.8s)
    python3 tests/check_meta_prompt.py

Gates run against a **commit**, never a dirty tree — `FR-P0-CLEAN` will fail otherwise.
Adding a gate is four things: a catalogue entry in the plan's §9, a registry entry at
`activation_phase: 5`, the id prefix in `tests/gates/gate_families.v1.yaml`, and an
`.accept.` plus a `.reject.` fixture.

The five Codex audits can be resumed for detail:

    codex resume 019fc237-3b09-7232-9680-750aea770820   # plan phases 0 and 4
    codex resume 019fc237-768d-7380-b6f3-3c68dda035a9   # plan phases 1 and 2
    codex resume 019fc237-a614-7551-a8da-121f9efe8f26   # phase 3 and the gate edits
    codex resume 019fc237-e745-7732-b1bf-ab0b39bc33db   # phase 5 and Finish
    codex resume 019fc237-fd59-7f30-8011-1fa66b0c1b98   # phase 6 verdict

**Suggested order:** defect 2 first (it is a false statement sitting in the repo and
costs ten minutes), then 1 (the real loss of rigour), then 3, 4, 5. Only then phase 6,
and per Codex that means writing the controller and logger first rather than another
prose stop.
