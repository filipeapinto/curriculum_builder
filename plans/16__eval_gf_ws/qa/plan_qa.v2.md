# Gate Rerun Flakiness (Phases 4-5) Plan v1 — Focused QA (Round 2)

## Verdict

**CHANGES REQUIRED — 1 Critical, 2 High.** The revision is substantive rather than
cosmetic: six of the seven prior findings are genuinely fixed, and the re-derived Phase D
is now correct in every particular I could check — the `class_drift` tally reproduces
exactly (`FR-P0-NOSTALE` 50, `FR-P1-GITKEEP` 19, `FR-P1-DOC` 7, `FR-P1-SCHEMA-RETENTION` 2,
six singletons), `FR-P1-DOC` is indeed absent from `registry.py`, `FR-P1-SCHEMA-RETENTION`
is declared `tree+text` at `registry.py:125`, and 81 of the 83 drift events belong to gates
that terminated by raising, so the proposed `aborted` skip targets precisely the right
population and conceals nothing (every such gate is already `FAIL`). The Phase E lockfile
name is safe: the only two globs over the results directory are `*.json`
(`selftest.py:116`, `:228`). What blocks the plan is Phase C step 1. Intersecting
`production_files()` with `git ls-files` has no implementation that is simultaneously
retried and mechanism-neutral: routed through `Evidence.run` it stamps `execution` onto four
gates whose `claim_class` does not contain it, failing `FR-P0-REGISTRY` deterministically on
every run; routed around `Evidence.run` it is not covered by the Phase B retry the plan
cites as its mitigation, and it plants an unretried `git` subprocess inside the root gate's
self-test. Two High defects follow from the same blind spot — that `scan_for_stale` and
`production_files()` have a caller inside `FR-P0-HARNESS` — plus an incomplete census of the
silent-swallow sites Phase B step 5 exists to close.

## Prior-round remediation

1. **REMEDIATED.** The 020605 record is reclassified as a tracked-policy-file-mid-edit case
   and explicitly withdrawn as justification; I re-read the record and its detail is exactly
   `deferred-id-unresolved:RT-9 at policy/deferred.v1.yaml`, with `FR-P4-CHECK-MAPPING` and
   `FR-P4-AGREEMENT` `BLOCKED` as described. Phase A step 4 adds the worktree-change
   detection that makes the case observable.
2. **REMEDIATED.** `PRODUCTION_EXCLUDED_TOP_LEVEL` is now explicitly left unchanged and is
   an acceptance criterion. `FR-P0-NOSTALE` reads `_tracked_production_files()`
   (`fr_p0_structure.py:278-293`), which the plan does not touch at all, so its 8 hits are
   structurally preserved — I re-ran it: 110 files, 8 hits, including the three
   `.claude/skills/curriculum-concept-visualization/**` ones. `git ls-files .claude` returns
   12 files, all retained under the tracked intersection. (The *mechanism* chosen to achieve
   this is what finding 1 rejects, not the goal.)
3. **REMEDIATED.** Every re-derived claim verifies: drift tally identical to the plan's
   table; `grep -c FR-P1-DOC tests/gates/registry.py` = 0; `registry.py:123-126` declares
   `FR-P1-SCHEMA-RETENTION` as `tree+text` (the recorded drift was `declared tree, reported
   text+tree`, so it can no longer occur); the last drift-bearing run is
   `gate_results.p5.20260802T132721.102859Z.json`. The withdrawal of the three original
   sites is correct.
4. **REMEDIATED.** All three read sites are now named and each is the right one:
   `common.py:291` is `_deserialize`'s `path.read_text(encoding="utf-8")`, `selftest.py:117`
   is `json.loads(path.read_text(...))`, `common.py:121` is `read_named`.
5. **REMEDIATED.** `plans/folder_refactoring/folder_refactoring.plan.v6.md:502-506` is
   verified as the numbered item `7.` carrying the enumeration ("excludes `tests/**` entire
   … plus `plans/**` and `.git/**`"); the grep instruction is gone.
6. **PARTIALLY REMEDIATED.** The three named detectors are fixed, but three further
   production-scan sites with the identical `except (OSError, UnicodeDecodeError): continue`
   are not (finding 3), and the re-raise is routed through the root gate (finding 2).
7. **REMEDIATED.** `tests/results/.run.lock` is safe: the only globs over that directory are
   `results.glob("*.json")` at `selftest.py:116` and `:228`; `RESULTS_DIR` appears only at
   `common.py:40`, `runner.py:34,79,81,85`, `selftest.py:106`; `.gitignore` carries only
   `tests/results/*.json` and `!tests/results/.gitkeep`, and the plan adds a dedicated line.
   No schema validates gate result records, so the new `aborted` / `transient_external` keys
   are safe too.

## Findings

### 1. Critical — Phase C step 1's `git ls-files` intersection cannot be both retried and mechanism-neutral

**Evidence.** Phase C step 1 requires `production_files()` to intersect its walk with
`git ls-files`, and asserts the mitigation: "`git ls-files` is on the Phase B retry
allowlist, which is why Phase B is ordered before Phase C." But Phase B step 3 places the
retry *inside one method*: "In `Evidence.run` (`tests/gates/common.py:274-282`), when the
command's argv is on the allowlist … retry". `production_files()` cannot reach it. Its
signature is `production_files(suffixes: Optional[Iterable[str]] = None)`
(`common.py:75`), and none of its five call sites passes an `Evidence`:
`fr_p1_retention.py:165`, `fr_p2_selector.py:234,333,550`, `selftest.py:241`.

The two available implementations both break something:

- *Through `Evidence.run`* (requiring an `ev` parameter threaded to all five call sites):
  `Evidence.run` unconditionally does `self._record("execution")` at `common.py:275`. The
  consumers' declared claim classes contain no `execution` —
  `FR-P1-SCHEMA-RETENTION` `tree+text` (`registry.py:125`), `FR-P2-CONTRACT-VERSIONED`
  `tree+text+schema+parse` (`:135`), `FR-P2-DEFERRED` `parse+text+mapping` (`:143`),
  `FR-P2-SEL-MAPPED` `tree+text+mapping` (`:167`). `_class_drift_sweep`
  (`runner.py:196-231`) would then report four drift entries on *every* run and rewrite
  `FR-P0-REGISTRY` `PASS` → `FAIL` at `runner.py:224-228`. Phase D step 3 forbids the only
  escape ("do **not** edit any `claim_class` in `registry.py` to match observed behaviour"),
  so the plan would convert an intermittent failure into a permanent one.
- *Around `Evidence.run`* (a bare `subprocess.run`, which is what `production_files()`'s
  "records no mechanism" contract implies): the Phase B retry does not apply, the Phase B
  `transient_external` marker is never set, and the plan's stated reason for ordering B
  before C is simply untrue. Worse, this puts an unretried, unmarked `git` invocation inside
  `selftest.py:241` — i.e. inside self-test (f) of `FR-P0-HARNESS`, the root gate, which
  currently has zero `git` dependency. The plan's own Phase B evidence records
  `git ls-files` failing with `fatal: .git/index: unable to map index file: Operation timed
  out` 50 times (`FR-P0-NOSTALE`) and 19 times (`FR-P1-GITKEEP`); routing that same call
  into the root gate makes each such failure block the entire run.

The plan never mentions the mechanism-recording consequence at all, even though Phase B
step 3 explicitly worries about exactly this class of problem for retries ("Retrying must
not record an additional `execution` mechanism … Phase D depends on mechanism sets being
stable").

**Impact.** The central normative change of Phase C is unimplementable as written. One
branch produces a deterministic `FR-P0-REGISTRY` `FAIL` on every run of phases 0-5 — a
self-inflicted regression larger than the flakiness being fixed, and one Phase D's own rules
forbid unwinding. The other branch silently voids the plan's declared mitigation and
introduces a new transient dependency at the single worst point in the dependency graph.
Because Phase F only measures verdict stability, the second branch would look "stable" right
up until the next `.git/index` stall, at which point every gate goes `BLOCKED`.

**Minimal required remediation.** State the implementation explicitly. Factor the bounded
retry out of `Evidence.run` into a module-level helper in `common.py` (e.g.
`_run_retryable(argv)`) that both `Evidence.run` and `production_files()` call, and have
`production_files()` call the helper **directly, recording no mechanism**, preserving its
documented "enumeration to select files is not `tree`" contract (`common.py:76-80`). Add an
explicit verification step: after the change, `_class_drift_sweep` reports an empty
`class_drift` on an otherwise-passing run, and the `mechanisms_used` recorded for
`FR-P1-SCHEMA-RETENTION`, `FR-P2-CONTRACT-VERSIONED`, `FR-P2-DEFERRED` and
`FR-P2-SEL-MAPPED` are byte-identical before and after Phase C. Separately, state what
`production_files()` does when `git ls-files` fails after retries — it must not fall back to
an untracked walk (that would silently restore the volatile scan root), and it must not be
allowed to fail the root gate silently.

### 2. High — Phase B step 5's re-raise fires inside the root gate, converting a per-file transient into a whole-run `BLOCKED`

**Evidence.** Phase B step 5 requires `scan_for_stale` (`fr_p0_structure.py:266-269`) to
re-raise after retries are exhausted. The plan discusses that detector only as
`FR-P0-NOSTALE`'s. It is also called by `FR-P0-HARNESS` self-test (f):

```python
# selftest.py:240-245
structure = ev.import_and_call("fr_p0_structure")
scanned = common.production_files()
leaked = [p for p in scanned if "tests" in Path(p).relative_to(common.REPO_ROOT).parts[:1]]
fixture_hits = [
    hit for hit in structure.scan_for_stale(scanned) if "/tests/" in hit or hit.startswith("tests/")
]
```

This call passes no `Evidence`, so it goes through `read_named`, and it scans the *whole*
`production_files()` set — 661 files today (448 under `outputs/`), and still ~110 after
Phase C. An exception propagates out of `_selftest_scan_isolation`, out of `gate_harness`
(the `try/finally` at `selftest.py:126-135` only removes the scratch dir), and is caught by
`runner.py:130-131`, making `FR-P0-HARNESS` `FAIL` — which takes every dependent gate to
`BLOCKED`. Phase B is ordered before Phase C, so the widest exposure (all 661 files) exists
for the whole interval between them.

Note also that the re-raise buys nothing at this call site: self-test (f) only asserts that
no scanned path and no hit lies under `tests/`. A silently dropped file there cannot produce
a false `PASS` of any substance, which is the entire justification for step 5. The risk is
imported without the benefit. The same applies to `FR-P0-NOSTALE`'s own fixture detector
(`fr_p0_structure.py:307`), where a re-raise is converted by `Fixture.evaluate`
(`common.py:353-357`) into a non-matching `matched_error` and reported as
"rejected for a different reason than declared" — a misleading fixture verdict for an I/O
fault.

For the record, the re-raise is safe against today's tree in the ordinary case: I read all
661 files returned by `production_files()` through `read_named` and got zero exceptions
(`errors="replace"` makes `UnicodeDecodeError` unreachable, and there are no broken symlinks
or unreadable files in the scan root), so nothing that legitimately raises today is being
correctly skipped. The defect is the blast radius, not a false positive.

**Impact.** The plan's stated goal is that a transient read stops flipping verdicts. As
written, Phase B step 5 makes one transient read flip *every* verdict in the run to
`BLOCKED`, via the root gate — the identical symptom the plan's own evidence attributes to
`FR-P0-HARNESS`'s 21 timeouts. It also risks tripping prerequisite 0b's stop condition and
invariant 1 during Phase F measurement.

**Minimal required remediation.** Make the re-raise conditional on the caller being a
production verdict scan rather than unconditional: give `scan_for_stale`,
`dangling_rt_references` and `live_v1_references` an explicit `strict: bool` (or
`on_read_error`) parameter, pass `strict=True` from `check_stale`, `check_deferred` and the
`FR-P2` production paths, and `strict=False` from `selftest.py:244` and from every
`Fixture` detector, where the swallow is harmless. State in Phase B that `scan_for_stale`
has a root-gate caller and that self-test (f) must be exempt.

### 3. High — the silent-swallow census is incomplete: three more production-scan sites over the same roots are left unfixed

**Evidence.** Phase B step 5 says "Three detectors discard read failures without a trace"
and names `fr_p0_structure.py:266-269`, `fr_p2_selector.py:293-296` and
`fr_p2_selector.py:239-242`. There are six such sites on production scan roots, not three.
The three the plan omits are all reached from real gate bodies, not fixtures:

- `fr_p1_retention.py:109` — `retention_gate_violations`, called at `:166` with
  `scan_files` derived from `common.production_files()` at `:165`. This detector is
  **armed**, not vacuous: `schemas/deprecated/` holds 4 retired schemas (the recorded
  `FR-P1-SCHEMA-RETENTION` detail is `PASS (4 files, 4 retired)`). A swallowed read here is
  a missed `retired-schema-still-referenced` hit — a false `PASS`, in exactly the direction
  step 5 exists to close.
- `fr_p2_selector.py:555` — the reverse `owner-without-id` scan inside `check_sel_mapped`,
  iterating `common.production_files()` at `:550`. This is a *different* site from the two
  the plan does fix, and `FR-P2-SEL-MAPPED` is on the plan's own transient-`FAIL` list.
- `fr_p5_engine.py:183` — `engine_domain_violations`, called at `:256` with
  `engine_files()` (`:67-79`), a live phase-5 production scan.

(`fr_p3_calibration.py:145,376` carry the same pattern but are only reached with
single-element fixture lists, so they are genuinely low-risk.)

**Impact.** Phase F step 3(b) requires confirming that "no file was silently dropped from
any scan", and the acceptance criteria rest on it. With three of six sites unfixed that
confirmation cannot be given for `FR-P1-SCHEMA-RETENTION`, `FR-P2-SEL-MAPPED` or
`FR-P5-ENGINE-GENERIC`, and the plan will be signed off asserting a property it did not
establish. Since `FR-P1-SCHEMA-RETENTION` is the one gate whose drift was content-caused
rather than abort-caused, leaving its scan able to under-read silently is a poor place to
stop.

**Minimal required remediation.** Extend Phase B step 5 to the full set: add
`fr_p1_retention.py:109`, `fr_p2_selector.py:555` and `fr_p5_engine.py:183` to the list of
sites that retry and then re-raise (subject to finding 2's `strict` distinction), or state
explicitly and with evidence why each omitted site cannot produce a false `PASS`. Add the
enumeration to the verification sequence so the census is checkable rather than asserted.

## Observations (non-blocking)

- **`dangling_rt_references` returns 4 hits, not 3.** Phase C's "three live hits, all under
  `.claude/skills/plan-create-workspace/iteration-1/**`" is stale; running it today over
  `common.production_files()` gives four, the fourth being
  `deferred-id-unresolved:RT-11 at .claude/skills/llm_learning_agents/references/repo_conventions.md`.
  That file is also untracked (`git ls-files .claude/skills/llm_learning_agents` is empty),
  so the conclusion — drops to 0 under a tracked intersection — still holds. The concrete
  expectation in Phase C step 2 ("drops from 3 to 0") should be written as "drops to 0",
  since the source is an untracked workspace that changes between runs.
- **`.claude/` file count.** The plan says 57; `production_files()` returns 69 under
  `.claude/` today (total 661, `outputs` 448, `.pytest_cache` 5). Same direction, same
  argument.
- **"the six most recent runs all record `class_drift: []`"** understates it — there are far
  more than six runs after `gate_results.p5.20260802T132721.102859Z.json`, all clean.
- **`git ls-files` reads the index, not `HEAD`.** The objective says a verdict should be "a
  function of committed repository state alone", but a tracked-content intersection makes it
  a function of the *staged* set, which the plan simultaneously requires to be a large,
  human-owned changeset (prerequisite 0a) and to survive untouched. `_tracked_production_files()`
  already has this property, so it is not a regression, but the wording overclaims.
- **`git ls-files` quotes non-ASCII paths** by default (`core.quotePath`), which a
  name-based intersection would drop. There are zero such paths today
  (`git ls-files | grep -c '^"'` = 0), so this is latent; `-z` or `-c core.quotePath=false`
  would close it.
- **`tests/flakiness/` and `plans/_eval_gf_ws/` are safe additions.** `FR-P0-TREE`
  (`fr_p0_structure.py:192`) checks the folder-refactoring plan's declared target tree, and
  `FR-P0-PLANREF` globs only `PLAN_DIR` (`common.py:42`, `fr_p0_structure.py:394`), so
  neither new directory perturbs a gate. No gate reads `.gitignore`, so Phase C step 4's
  additions are inert to the suite.
- **No schema validates gate result records** (`grep` over `schemas/` finds no
  `gate_results`/`stdout_digest` consumer), so Phase D's `aborted` and Phase B's
  `transient_external` keys cannot break record validation.
