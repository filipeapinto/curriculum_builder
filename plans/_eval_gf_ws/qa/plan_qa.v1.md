# Gate Rerun Flakiness (Phases 4-5) Plan v1 — Focused QA

## Verdict

**CHANGES REQUIRED — 3 Critical, 4 High.** The plan's instrumentation-first structure is
sound, its Phase B diagnosis is the correct dominant cause, and almost every raw count in
it is reproducible against `tests/results/` (88 runs containing `Operation timed out`; the
per-gate transient tallies 50/21/19/18/7/6/4/3; `FR-P0-REGISTRY` 51 flips; `FR-P0-NOSTALE`
46 flips; the 148 ms `FR-P0-CLEAN` PASS/FAIL pair; the untracked, load-bearing
`tests/fixtures/time_limit_present.reject.yaml`; the whole "confirmed non-causes" section).
What blocks it is causal attribution, not arithmetic. Phase C's one cited cascade record
names `policy/deferred.v1.yaml`, not `outputs/`, as the offending file, so the evidence
does not support the remediation it is offered for. Phase C's exclusion change also
silently narrows `FR-P0-NOSTALE` — the plan asserts the opposite — and would suppress three
live detector hits on *committed* `.claude/skills/**` content. Phase D targets three code
sites that the 276 recorded runs show produced 0, 0 and 1 drift events respectively, while
the real drift sources (85% of them a Phase B side effect, the rest `FR-P1-DOC` and
`FR-P1-SCHEMA-RETENTION`) go unmentioned. Four further High defects concern a
retry applied to the wrong read helper, a rule-7 pointer that points at the wrong lines, an
unaddressed silent-`OSError` swallow that flakes in the *pass* direction, and an
under-specified lockfile name that can break the root gate.

## Findings

### 1. Critical — Phase C's cascade evidence names `policy/`, not `outputs/`

**Evidence.** The plan (§3, "Evidence, part 1") writes: "The cascade is on record:
`gate_results.p4.20260802T020605.174698Z.json` shows `FR-P2-DEFERRED FAIL —
deferred-id-unresolved:RT-9`, taking `FR-P4-AGREEMENT` and `FR-P4-CHECK-MAPPING` to
`BLOCKED`". The record's actual `detail` is:

```
FR-P2-DEFERRED FAIL (8 ids, 8 mirrored, 1 dangling) — deferred-id-unresolved:RT-9 at policy/deferred.v1.yaml
```

The location clause the plan drops is the causal part. `policy/deferred.v1.yaml` is a
tracked policy file that was mid-edit at 02:06 on 2026-08-02; `git log -S"RT-9" --
policy/deferred.v1.yaml` returns nothing, confirming the RT-9 was in an uncommitted working
state. It was not an `outputs/` file. Running `dangling_rt_references` today over
`common.production_files()` returns three hits, all under
`.claude/skills/plan-create-workspace/iteration-1/...` — zero under `outputs/`. The plan
itself concedes this a sentence earlier ("They pass today only because those particular ids
happen to be declared"), i.e. `outputs/` has never actually produced a dangling id, yet the
cascade record is presented as proof that it did.

**Impact.** The plan's single item of direct evidence for its one normative change —
narrowing `PRODUCTION_EXCLUDED_TOP_LEVEL` — does not support that change. An implementer who
excludes `outputs/` and re-runs will find `FR-P2-DEFERRED` fixed by the `.claude` exclusion
and wrongly credit `outputs/`, and Phase F will read as confirmation of a cause that was
never demonstrated. Worse, the real 020605 cause (a tracked policy file read mid-edit) is a
"repository state changed between runs" case that the plan's four phases do not address at
all, so it will recur.

**Minimal required remediation.** Replace the cited cascade with the reproducible one: state
that the live dangling `RT-9` hits are the three `.claude/skills/plan-create-workspace/**`
files, and record the 020605 run separately as a mid-edit tracked-file change, not as an
`outputs/` leak. Keep the `outputs/` exclusion if wanted, but justify it as invariant 2
(gitignored state out of the verdict path) rather than as an observed flip.

### 2. Critical — the Phase C exclusion *does* narrow `FR-P0-NOSTALE`, and suppresses three live hits on committed content

**Evidence.** The plan's "Deliberate non-change" states: "`FR-P0-NOSTALE` uses `git ls-files`
at `fr_p0_structure.py:281`, a separate scan root from `production_files()`, and this plan
does not narrow it." `fr_p0_structure.py:287` reads:

```python
if top in common.PRODUCTION_EXCLUDED_TOP_LEVEL or top in common.PRODUCTION_EXCLUDED_ANYWHERE:
```

`_tracked_production_files()` uses the *same* constant the plan proposes to extend. It is not
a separate scan root; it is the same exclusion set applied to a different file listing.

`.claude/` is not purely generated: `git ls-files .claude` returns 12 tracked, committed
files (`settings.json` plus both skill trees, added in HEAD commit `4e3a779`). Simulating the
proposed exclusion set against `scan_for_stale(_tracked_production_files())` today:

- current: 8 hits, of which 3 are
  `stale-path:assets/ at .claude/skills/curriculum-concept-visualization/SKILL.md:62` and
  `.../references/layouts.md:4` and `:46`;
- after excluding `outputs`, `.claude`, `.pytest_cache`: 5 hits — those three vanish.

**Impact.** The change makes a currently-failing detector stop reporting real violations in
committed repository content. That is precisely the failure mode `common.py:50-54` warns
against ("adding a root here would narrow a normative scan set... which is how a detector
stops seeing the file it exists to check"), and it violates the plan's own boundary ("does
not relax any acceptance criterion... does not rewrite a gate to make it stop failing"). It
also violates the plan's own proposed governing principle — "the production scan root is
*committed, non-generated repository content*" — since `.claude/skills/**` is exactly that.
The acceptance criterion "`common.production_files()` returns no path under ... `.claude/`"
bakes the coverage loss in.

**Minimal required remediation.** Do not exclude by top-level name in the shared constant.
Either (a) give `_tracked_production_files()` its own exclusion set that omits the generated
roots but keeps `.claude`, or (b) exclude only the untracked agent-workspace subtree
(`.claude/skills/plan-create-workspace/**`) rather than `.claude` entire. Add an explicit
before/after check to the verification sequence: `scan_for_stale` must return the same
hits on committed files before and after the change.

### 3. Critical — Phase D's three cited sites account for essentially none of the observed drift

**Evidence.** Across all 276 files in `tests/results/`, the `class_drift` entries actually
recorded on `FR-P0-REGISTRY` are:

```
FR-P0-NOSTALE 50, FR-P1-GITKEEP 19, FR-P1-DOC 7, FR-P1-SCHEMA-RETENTION 2,
FR-P2-GATEITEMS 1, FR-P2-SEL-MAPPED 1, FR-P3-SPLIT 1, FR-P4-CHECK-MAPPING 1,
FR-P5-DERIVATION 1, FR-P5-RECEIPT-HASH 1
```

The plan's flagship site, `fr_p5_verifier.py:151-154`, has produced **zero** drift events:
`FR-P5-VERIFIER-REQUIRED` reported the full `('tree','parse','mapping','execution')` set in
all 65 runs in which it ran. `fr_p4_policy_schemas.py:87-96` (`FR-P4-ALL-VALIDATE`) has also
produced zero. `fr_p4_policy_schemas.py:189-191` (`FR-P4-CHECK-MAPPING`) has produced one.

61 of `FR-P0-REGISTRY`'s 64 recorded `FAIL`s are class-drift, and 53 of the 62 runs carrying
a non-empty `class_drift` also contain `Operation timed out`. The two largest drift
contributors, `FR-P0-NOSTALE` (50) and `FR-P1-GITKEEP` (19), match the plan's own Phase B
transient-I/O tallies *exactly* — drift is overwhelmingly a Phase B consequence (a gate that
raises mid-way reports partial mechanisms via `runner.py:130-135`), not an independent cause.

The reasoning is also internally inconsistent. Phase D's stated mechanism is the
phase-4/phase-5 asymmetry created by `runner.py:209` skipping `SKIPPED` gates. But two of the
three cited sites belong to `activation_phase: 4` gates that run identically at phase 4 and
phase 5, so they cannot produce that asymmetry at all. The only drift with no timeout in the
record comes from `FR-P1-DOC` (7) and `FR-P1-SCHEMA-RETENTION` (2) — neither is in Phase D's
remediation list.

**Impact.** Phase D as written changes three call sites that have caused at most 1 of 83
recorded drift events, will not move `FR-P0-REGISTRY`'s flip count, and will make Phase F's
"every gate stable" look like the fix worked when the actual improvement came from Phase B.
The two content-caused drift sources are left unfixed and unrecorded.

**Minimal required remediation.** Re-derive Phase D from the recorded `class_drift` field
rather than from code reading: state that drift is a Phase B derivative for
`FR-P0-NOSTALE`/`FR-P1-GITKEEP`, and replace the three cited sites with the two that drift
without a timeout (`FR-P1-DOC`: declared `mapping+text+tree`, reported `text+tree`;
`FR-P1-SCHEMA-RETENTION`: declared `tree`, reported `text+tree`). Drop or demote the
phase-asymmetry claim, which the record does not support. (The proposed
"record unconditionally" technique is itself drift-safe at all three cited sites — every
mechanism it would add is already in the gate's declared `claim_class` in `registry.py` —
so no *new* drift is introduced; the sites are simply the wrong ones.)

### 4. High — Phase B's file-read retry is applied to a helper the named failures do not use

**Evidence.** Phase B step 4 says the raised `TimeoutError`s from `FR-P0-HARNESS`,
`FR-P2-SEL-MAPPED` and `FR-P0-PARSE` should be fixed by retrying "the text-read helper at
`tests/gates/common.py:121` (the `errors="replace"` read used by every `production_files()`
consumer)". That helper is `read_named`. The named gates do not reach it:

- `FR-P0-PARSE`'s recorded detail is
  `FR-P0-PARSE FAIL (34 files parsed) — policy/deferred.v1.yaml: builtins.TimeoutError: [Errno 60] ...`.
  Its path is `check_parse` (`fr_p0_structure.py:437-446`) → `parse_error` → `ev.parse` →
  `common._deserialize`, whose read is `path.read_text(encoding="utf-8")` at
  **`common.py:291`** — a different call with different arguments.
- `FR-P0-HARNESS`'s 21 bare `TimeoutError`s originate inside `selftest.py`; the file reads
  there are `json.loads(path.read_text(...))` at `selftest.py:117`, not `read_named`.

Separately, every `read_named` consumer the plan names already wraps the call in
`except (OSError, UnicodeDecodeError): continue` (`fr_p0_structure.py:268`,
`fr_p2_selector.py:295`, `:241`), and `TimeoutError` is a subclass of `OSError` — so those
call sites cannot be the ones producing an uncaught `TimeoutError` in the first place.

**Impact.** Roughly 25 of the ~40 raised-exception transients in the record (21
`FR-P0-HARNESS` + 4 `FR-P0-PARSE`, plus the `FR-P3-CAPS-OWNED`/`FR-P2-GATEITEMS` cases that
go through `_deserialize`) would remain unretried and unmarked. Since `FR-P0-HARNESS` is the
root gate, every one of its 21 timeouts blocks the entire run — the exact reported symptom
Phase B claims to remove.

**Minimal required remediation.** Apply the bounded retry at `common.py:291`
(`_deserialize`'s `read_text`) as well as `common.py:121`, and to the result-file read in
`selftest.py:117`. Keep the `Evidence.run` allowlist as specified.

### 5. High — the rule-7 "statement of record" pointers are wrong, and the prescribed grep cannot find the real one

**Evidence.** Phase C step 1 instructs: "Grep for `rule 7` and pick the live
(non-`deprecated/`) source — at planning time the live hits are in
`plans/folder_refactoring/folder_refactoring.plan.v6.md` (e.g. `:820`, `:871`) and
`plans/folder_refactoring/folder_refactoring.prompt.v6.md:88`."

None of those three enumerate the exclusion set:

- `:819-820` says the opposite — "The scan root is that set as rule 7 defines it — **by
  exclusion, never re-enumerated here**".
- `:871` says only "Production scan excludes `tests/**` per rule 7."
- `prompt.v6.md:88` says only "Never let a production scan read `tests/**` or `plans/**`".

The actual normative enumeration is `folder_refactoring.plan.v6.md:502-506`: "Every detector
takes an explicit scan root set. The production set excludes `tests/**` entire —
`tests/gates/**`, `tests/fixtures/**`, `tests/selftest/**`, `tests/results/**` — plus
`plans/**` and `.git/**`." That paragraph is numbered `7.` in a rules list and contains no
literal string `rule 7`, so the prescribed grep will never surface it.

**Impact.** Two outcomes, both bad. Either the implementer hits Phase C step 1's own stop
condition ("If the live rule-7 statement cannot be identified unambiguously, stop and
report") and Phases C-F never execute; or the implementer edits `:820`/`:871` — non-normative
prose — while `:502-506` continues to state an exclusion set that the code no longer matches,
which is precisely the code/rule divergence the step exists to prevent, and the acceptance
criterion "The rule-7 statement of record and `common.py:50-55` agree" would be signed off
falsely.

**Minimal required remediation.** Name the statement of record explicitly as
`plans/folder_refactoring/folder_refactoring.plan.v6.md:502-506` and drop the grep
instruction (or change it to grep for `excludes \`tests/\*\*\` entire`).

### 6. High — a flakiness cause in the *pass* direction is neither identified nor fixed

**Evidence.** Three of the plan's own scan detectors swallow read failures silently:

```python
# fr_p0_structure.py:266-269 (scan_for_stale)
try:
    text = ev.text_of(path) if ev is not None else read_named(path)
except (OSError, UnicodeDecodeError):
    continue
```

The same pattern is at `fr_p2_selector.py:293-296` (`dangling_rt_references`) and
`fr_p2_selector.py:239-242` (`live_v1_references`). `TimeoutError` is a subclass of `OSError`,
so under exactly the `[Errno 60]` conditions Phase B documents, a file simply drops out of the
scan with no note, no mechanism change, and no marker. `FR-P0-NOSTALE` currently has 8 real
hits; a transient failure on `runtime/session_bridge.py` alone would silence 5 of them and
could turn a genuine `FAIL` into a `PASS`.

**Impact.** The plan's entire framing is that transient I/O produces spurious `FAIL`s and that
Phase F should show them gone. The same I/O also produces spurious `PASS`es, which Phase F
cannot detect and which the `transient_external` marker will never be attached to — a stable,
green, and wrong verdict. This is a Critical/High flakiness cause present in the repository
that Phases B-E do not cover.

**Minimal required remediation.** In Phase B, add: a swallowed read in these three detectors
must `ev.note(...)` the skipped path and set `transient_external`, or (preferred) re-raise
after the bounded retry is exhausted so the run reports `FAIL` rather than an under-scanned
`PASS`. Add "no file was silently dropped from any scan" to the Phase F comparison.

### 7. High — the Phase E lockfile is placed but not named, and a `.json` name breaks the root gate

**Evidence.** Phase E step 2 specifies "an `O_EXCL` lockfile under `tests/results/`" and step 3
that it "must be gitignored, following `.gitignore:1-5`". `.gitignore:4` is
`tests/results/*.json` — the only existing pattern for that directory — so "follow the
existing pattern" points an implementer at a `.json` name. But `selftest.py:116-117` does

```python
for path in sorted(results.glob("*.json")):
    payloads.append(json.loads(path.read_text(encoding="utf-8")))
```

and self-test (e) asserts `len(sorted(results.glob("*.json"))) == 2` (`selftest.py:228,232`).
A lockfile matching `*.json` in a results directory therefore makes self-test (c) raise on
`json.loads` and self-test (e) count 3 instead of 2. Both live inside `FR-P0-HARNESS`, the
root gate, so the whole run goes `BLOCKED`.

(The placement itself is otherwise safe: `_run` at `selftest.py:101-109` always sets
`FR_RESULTS_DIR` to a per-case scratch directory, so a child runner never contends with the
parent's lock, and `_selftest_no_overwrite`'s two `_run` calls are sequential.)

**Impact.** A one-character naming choice can take every gate to `BLOCKED`, which is the same
symptom the plan exists to remove, and it would surface only after Phase E is already
implemented.

**Minimal required remediation.** State the lockfile name explicitly as a non-`.json`
basename (e.g. `tests/results/.run.lock`) and add a matching `.gitignore` line rather than
relying on `tests/results/*.json`.

## Observations (non-blocking)

- Invariant 1 requires "a clean worktree", but the plan simultaneously forbids committing and
  requires the pre-existing staged changeset to survive (§0a, acceptance criteria). The
  precondition is unsatisfiable for the plan's own duration; in practice `FR-P0-CLEAN` will be
  a deterministic `FAIL` throughout, which still satisfies "stable", but the plan never says
  so. Nothing in the registry depends on `FR-P0-CLEAN`, so there is no cascade.
- Invariant 2 ("No gate verdict depends on a file that is untracked or gitignored") is
  contradicted by `FR-P0-CLEAN`, whose entire purpose is to depend on untracked state
  (`fr_p0_structure.py:589-597`). An exemption clause would remove the ambiguity.
- The transient-failure enumeration in Phase B omits `FR-P0-PLANREF` (2), `FR-P2-NOVALUES` (2)
  and `FR-P3-SPLIT` (1); every count it does give is exact.
- `production_files()` now returns 655 paths (`outputs` 448, `.claude` 57, `.pytest_cache` 5)
  against the plan's 633/448/41/5 — the tree has grown since planning; the 78% figure still
  holds.
- `tests/fixtures/time_limit_present.reject.yaml` is confirmed untracked, not gitignored, and
  genuinely load-bearing: `Fixture.evaluate` (`common.py:351-354`) converts the
  `FileNotFoundError` into a non-matching `matched_error`, so `gate_result` returns
  `ok=False` and `FR-P4-AGREEMENT` fails on a fresh clone. The plan's claim is correct.
- Every "confirmed non-cause" was verified: `RESULTS_DIR` appears only at the five cited
  sites, there is no `os.listdir` under `tests/`, every enumeration site cited is sorted,
  `common.py:534-538` does parse the integer version, and `runner.py:111` is a plain
  sequential loop.
